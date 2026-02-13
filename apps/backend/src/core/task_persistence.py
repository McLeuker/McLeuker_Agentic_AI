"""
McLeuker AI - Task Persistence Manager
Runs agent tasks as background asyncio.Tasks with state stored in Supabase.
Tasks survive page navigation — frontend can reconnect and replay events.

Architecture:
  1. User starts a task → creates background asyncio.Task
  2. Events are buffered in-memory AND stored in Supabase execution_history
  3. SSE endpoint streams events from buffer (live) or replays from DB (reconnect)
  4. WebSocket also receives events for the live execution panel
"""

import asyncio
import json
import logging
import time
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, AsyncGenerator, Callable, Coroutine, Dict, List, Optional

logger = logging.getLogger(__name__)


class ExecutionStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    PAUSED = "paused"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class BufferedEvent:
    """A single event in the execution stream."""
    event_type: str
    data: Dict[str, Any]
    timestamp: float = field(default_factory=time.time)
    sequence: int = 0


@dataclass
class PersistentExecution:
    """Tracks a running execution with its state and event buffer."""
    execution_id: str
    user_id: str
    task_description: str
    mode: str = "agent"
    conversation_id: Optional[str] = None
    status: ExecutionStatus = ExecutionStatus.PENDING
    events: List[BufferedEvent] = field(default_factory=list)
    steps: List[Dict] = field(default_factory=list)
    result: Dict = field(default_factory=dict)
    files_generated: List[Dict] = field(default_factory=list)
    screenshots: List[str] = field(default_factory=list)
    credits_used: int = 0
    error: Optional[str] = None
    asyncio_task: Optional[asyncio.Task] = None
    created_at: float = field(default_factory=time.time)
    started_at: Optional[float] = None
    completed_at: Optional[float] = None
    # Subscribers waiting for events
    _subscribers: List[asyncio.Queue] = field(default_factory=list)
    _event_sequence: int = 0
    _cancel_event: asyncio.Event = field(default_factory=asyncio.Event)


class TaskPersistenceManager:
    """
    Manages background task execution with persistence.
    Tasks run independently of SSE/WebSocket connections.
    """

    def __init__(self, supabase=None, ws_manager=None):
        self.supabase = supabase
        self.ws_manager = ws_manager
        self._executions: Dict[str, PersistentExecution] = {}
        self._max_buffer_size = 500  # Max events to keep in memory per execution
        self._cleanup_interval = 300  # Clean up completed executions after 5 min
        self._cleanup_task: Optional[asyncio.Task] = None

    async def start(self):
        """Start the cleanup background task."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("TaskPersistenceManager started")

    async def stop(self):
        """Stop the cleanup task."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            try:
                await self._cleanup_task
            except asyncio.CancelledError:
                pass

    # ========================================================================
    # EXECUTION LIFECYCLE
    # ========================================================================

    async def create_execution(
        self,
        user_id: str,
        task_description: str,
        mode: str = "agent",
        conversation_id: Optional[str] = None,
        execution_id: Optional[str] = None,
    ) -> str:
        """Create a new execution record. Returns execution_id."""
        eid = execution_id or str(uuid.uuid4())[:12]

        execution = PersistentExecution(
            execution_id=eid,
            user_id=user_id,
            task_description=task_description,
            mode=mode,
            conversation_id=conversation_id,
        )
        self._executions[eid] = execution

        # Persist to Supabase
        await self._db_create(execution)

        return eid

    async def run_execution(
        self,
        execution_id: str,
        coroutine_factory: Callable[..., Coroutine],
        *args,
        **kwargs,
    ):
        """
        Run an execution as a background asyncio.Task.
        The coroutine_factory should be an async generator that yields events.
        """
        execution = self._executions.get(execution_id)
        if not execution:
            raise ValueError(f"Execution {execution_id} not found")

        async def _run():
            execution.status = ExecutionStatus.RUNNING
            execution.started_at = time.time()
            await self._db_update_status(execution_id, "running")

            try:
                # Emit start event
                await self.emit_event(execution_id, "execution_start", {
                    "execution_id": execution_id,
                    "task": execution.task_description,
                    "mode": execution.mode,
                })

                # Run the actual execution generator
                async for evt in coroutine_factory(*args, **kwargs):
                    if execution._cancel_event.is_set():
                        execution.status = ExecutionStatus.CANCELLED
                        await self.emit_event(execution_id, "execution_cancelled", {})
                        break

                    evt_name = evt.get("event", "")
                    evt_data = evt.get("data", {})

                    # Track steps
                    if evt_name == "step_update":
                        self._update_step(execution, evt_data)

                    # Track files
                    if evt_name == "execution_artifact":
                        execution.files_generated.append(evt_data)

                    # Track screenshots (keep last 10)
                    if evt_name == "browser_screenshot":
                        screenshot = evt_data.get("screenshot", evt_data.get("image", ""))
                        if screenshot:
                            execution.screenshots = execution.screenshots[-9:] + [screenshot[:100] + "..."]

                    # Emit to subscribers and WebSocket
                    await self.emit_event(execution_id, evt_name, evt_data)

                # Mark complete if not cancelled
                if execution.status == ExecutionStatus.RUNNING:
                    execution.status = ExecutionStatus.COMPLETED
                    execution.completed_at = time.time()
                    await self.emit_event(execution_id, "execution_complete", {
                        "status": "completed",
                        "execution_time_ms": int((execution.completed_at - execution.started_at) * 1000),
                    })
                    await self._db_update_status(execution_id, "completed")

            except asyncio.CancelledError:
                execution.status = ExecutionStatus.CANCELLED
                await self._db_update_status(execution_id, "cancelled")
            except Exception as e:
                execution.status = ExecutionStatus.FAILED
                execution.error = str(e)
                execution.completed_at = time.time()
                await self.emit_event(execution_id, "execution_error", {
                    "message": str(e),
                })
                await self._db_update_status(execution_id, "failed", error=str(e))
                logger.error(f"Execution {execution_id} failed: {e}")

        execution.asyncio_task = asyncio.create_task(_run())

    async def emit_event(self, execution_id: str, event_type: str, data: Dict[str, Any]):
        """Emit an event to all subscribers and buffer it."""
        execution = self._executions.get(execution_id)
        if not execution:
            return

        execution._event_sequence += 1
        buffered = BufferedEvent(
            event_type=event_type,
            data=data,
            sequence=execution._event_sequence,
        )

        # Buffer the event (trim if too large)
        execution.events.append(buffered)
        if len(execution.events) > self._max_buffer_size:
            execution.events = execution.events[-self._max_buffer_size:]

        # Notify all SSE subscribers
        for queue in execution._subscribers:
            try:
                queue.put_nowait(buffered)
            except asyncio.QueueFull:
                pass  # Subscriber is slow, skip

        # Forward to WebSocket
        if self.ws_manager:
            try:
                if event_type == "browser_screenshot":
                    await self.ws_manager.broadcast_screenshot(
                        execution_id=execution_id,
                        image_base64=data.get("screenshot", data.get("image", "")),
                        url=data.get("url", ""),
                        title=data.get("title", ""),
                        action=data.get("action", ""),
                        step=data.get("step", 0),
                    )
                elif event_type in ("step_update", "execution_progress", "execution_reasoning",
                                     "execution_artifact", "execution_complete", "execution_error",
                                     "execution_start", "execution_cancelled"):
                    await self.ws_manager.broadcast(execution_id, event_type, data)
            except Exception as ws_err:
                logger.debug(f"WS forward error (non-fatal): {ws_err}")

    # ========================================================================
    # SSE STREAMING (with reconnection support)
    # ========================================================================

    async def subscribe(
        self,
        execution_id: str,
        from_sequence: int = 0,
    ) -> AsyncGenerator[BufferedEvent, None]:
        """
        Subscribe to execution events. Supports reconnection:
        - If from_sequence=0, streams all buffered events then live
        - If from_sequence>0, replays events after that sequence then live
        """
        execution = self._executions.get(execution_id)
        if not execution:
            # Try to load from DB
            execution = await self._db_load(execution_id)
            if not execution:
                return

        queue: asyncio.Queue = asyncio.Queue(maxsize=200)
        execution._subscribers.append(queue)

        try:
            # Replay buffered events
            for evt in execution.events:
                if evt.sequence > from_sequence:
                    yield evt

            # If already completed, we're done
            if execution.status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED):
                return

            # Stream live events
            while True:
                try:
                    evt = await asyncio.wait_for(queue.get(), timeout=30.0)
                    yield evt
                    if evt.event_type in ("execution_complete", "execution_error", "execution_cancelled"):
                        break
                except asyncio.TimeoutError:
                    # Send keepalive
                    yield BufferedEvent(event_type="keepalive", data={"status": execution.status.value})
        finally:
            if queue in execution._subscribers:
                execution._subscribers.remove(queue)

    # ========================================================================
    # EXECUTION MANAGEMENT
    # ========================================================================

    async def cancel_execution(self, execution_id: str):
        """Cancel a running execution."""
        execution = self._executions.get(execution_id)
        if execution and execution.asyncio_task and not execution.asyncio_task.done():
            execution._cancel_event.set()
            execution.asyncio_task.cancel()

    async def get_status(self, execution_id: str) -> Optional[Dict]:
        """Get execution status."""
        execution = self._executions.get(execution_id)
        if not execution:
            return await self._db_get_status(execution_id)

        return {
            "execution_id": execution.execution_id,
            "status": execution.status.value,
            "task": execution.task_description,
            "mode": execution.mode,
            "steps": execution.steps,
            "files_generated": len(execution.files_generated),
            "credits_used": execution.credits_used,
            "error": execution.error,
            "event_count": len(execution.events),
            "last_sequence": execution._event_sequence,
            "created_at": execution.created_at,
            "started_at": execution.started_at,
            "completed_at": execution.completed_at,
        }

    async def list_user_executions(self, user_id: str, limit: int = 20) -> List[Dict]:
        """List executions for a user."""
        # In-memory active executions
        active = [
            {
                "execution_id": e.execution_id,
                "status": e.status.value,
                "task": e.task_description[:100],
                "mode": e.mode,
                "created_at": e.created_at,
            }
            for e in self._executions.values()
            if e.user_id == user_id
        ]

        # DB historical executions
        historical = await self._db_list_user(user_id, limit)

        # Merge, deduplicate by execution_id
        seen = {e["execution_id"] for e in active}
        for h in historical:
            if h["execution_id"] not in seen:
                active.append(h)

        return sorted(active, key=lambda x: x.get("created_at", 0), reverse=True)[:limit]

    # ========================================================================
    # INTERNAL HELPERS
    # ========================================================================

    def _update_step(self, execution: PersistentExecution, step_data: Dict):
        """Update or add a step to the execution."""
        step_id = step_data.get("id", "")
        for i, s in enumerate(execution.steps):
            if s.get("id") == step_id:
                execution.steps[i] = {**s, **step_data}
                return
        execution.steps.append(step_data)

    # ========================================================================
    # DATABASE OPERATIONS
    # ========================================================================

    async def _db_create(self, execution: PersistentExecution):
        """Create execution record in Supabase."""
        if not self.supabase:
            return
        try:
            self.supabase.table("execution_history").insert({
                "execution_id": execution.execution_id,
                "user_id": execution.user_id,
                "conversation_id": execution.conversation_id,
                "task_description": execution.task_description,
                "mode": execution.mode,
                "status": execution.status.value,
                "steps": json.dumps([]),
                "result": json.dumps({}),
                "files_generated": json.dumps([]),
                "screenshots": json.dumps([]),
                "credits_used": 0,
            }).execute()
        except Exception as e:
            logger.warning(f"DB create execution error (non-fatal): {e}")

    async def _db_update_status(self, execution_id: str, status: str, error: str = None):
        """Update execution status in Supabase."""
        if not self.supabase:
            return
        try:
            execution = self._executions.get(execution_id)
            update_data = {
                "status": status,
                "updated_at": datetime.utcnow().isoformat(),
            }
            if execution:
                update_data["steps"] = json.dumps(execution.steps[:50])  # Limit stored steps
                update_data["files_generated"] = json.dumps(execution.files_generated[:20])
                update_data["credits_used"] = execution.credits_used
            if error:
                update_data["error"] = error[:1000]
            if status in ("completed", "failed", "cancelled"):
                update_data["completed_at"] = datetime.utcnow().isoformat()
                if execution and execution.started_at:
                    update_data["execution_time_ms"] = int((time.time() - execution.started_at) * 1000)

            self.supabase.table("execution_history").update(update_data).eq(
                "execution_id", execution_id
            ).execute()
        except Exception as e:
            logger.warning(f"DB update status error (non-fatal): {e}")

    async def _db_get_status(self, execution_id: str) -> Optional[Dict]:
        """Get execution status from Supabase."""
        if not self.supabase:
            return None
        try:
            result = self.supabase.table("execution_history").select("*").eq(
                "execution_id", execution_id
            ).execute()
            if result.data and len(result.data) > 0:
                row = result.data[0]
                return {
                    "execution_id": row["execution_id"],
                    "status": row["status"],
                    "task": row.get("task_description", ""),
                    "mode": row.get("mode", ""),
                    "steps": json.loads(row.get("steps", "[]")) if isinstance(row.get("steps"), str) else row.get("steps", []),
                    "files_generated": len(json.loads(row.get("files_generated", "[]")) if isinstance(row.get("files_generated"), str) else row.get("files_generated", [])),
                    "credits_used": row.get("credits_used", 0),
                    "error": row.get("error"),
                    "created_at": row.get("created_at"),
                    "completed_at": row.get("completed_at"),
                }
        except Exception as e:
            logger.warning(f"DB get status error: {e}")
        return None

    async def _db_load(self, execution_id: str) -> Optional[PersistentExecution]:
        """Load a completed execution from DB for replay."""
        if not self.supabase:
            return None
        try:
            result = self.supabase.table("execution_history").select("*").eq(
                "execution_id", execution_id
            ).execute()
            if result.data and len(result.data) > 0:
                row = result.data[0]
                execution = PersistentExecution(
                    execution_id=row["execution_id"],
                    user_id=row.get("user_id", ""),
                    task_description=row.get("task_description", ""),
                    mode=row.get("mode", "agent"),
                    status=ExecutionStatus(row.get("status", "completed")),
                )
                # Reconstruct minimal events from stored steps
                steps = json.loads(row.get("steps", "[]")) if isinstance(row.get("steps"), str) else row.get("steps", [])
                for i, step in enumerate(steps):
                    execution.events.append(BufferedEvent(
                        event_type="step_update",
                        data=step,
                        sequence=i + 1,
                    ))
                # Add completion event
                execution.events.append(BufferedEvent(
                    event_type=f"execution_{row.get('status', 'completed')}",
                    data={"status": row.get("status", "completed")},
                    sequence=len(steps) + 1,
                ))
                self._executions[execution_id] = execution
                return execution
        except Exception as e:
            logger.warning(f"DB load execution error: {e}")
        return None

    async def _db_list_user(self, user_id: str, limit: int = 20) -> List[Dict]:
        """List user's executions from DB."""
        if not self.supabase:
            return []
        try:
            result = self.supabase.table("execution_history").select(
                "execution_id, status, task_description, mode, created_at"
            ).eq("user_id", user_id).order("created_at", desc=True).limit(limit).execute()
            return [
                {
                    "execution_id": r["execution_id"],
                    "status": r["status"],
                    "task": r.get("task_description", "")[:100],
                    "mode": r.get("mode", ""),
                    "created_at": r.get("created_at"),
                }
                for r in (result.data or [])
            ]
        except Exception as e:
            logger.warning(f"DB list user executions error: {e}")
        return []

    async def _cleanup_loop(self):
        """Periodically clean up completed executions from memory."""
        while True:
            try:
                await asyncio.sleep(self._cleanup_interval)
                now = time.time()
                to_remove = []
                for eid, execution in self._executions.items():
                    if execution.status in (ExecutionStatus.COMPLETED, ExecutionStatus.FAILED, ExecutionStatus.CANCELLED):
                        if execution.completed_at and (now - execution.completed_at) > self._cleanup_interval:
                            if not execution._subscribers:  # No active subscribers
                                to_remove.append(eid)
                for eid in to_remove:
                    del self._executions[eid]
                if to_remove:
                    logger.info(f"Cleaned up {len(to_remove)} completed executions from memory")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.warning(f"Cleanup loop error: {e}")
