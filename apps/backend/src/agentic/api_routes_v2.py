"""
API Routes V2 — Agentic AI Execution Endpoints
================================================

Integrates with existing main.py structure.
Provides endpoints for the 3-mode execution system with:
- SSE streaming for real-time events
- WebSocket for live browser screenshots (LiveScreen.tsx)
- Clarification flow
- Event bus for forwarding SSE events to WebSocket clients
"""

import asyncio
import json
import logging
from typing import Optional, Dict, Any, List, Set
from datetime import datetime

from fastapi import APIRouter, HTTPException, WebSocket, WebSocketDisconnect, Request
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel, Field

from .execution_orchestrator_v2 import ExecutionOrchestratorV2

logger = logging.getLogger(__name__)


# ─── Event Bus for WebSocket forwarding ──────────────────────────

class EventBus:
    """
    Forwards SSE events to WebSocket clients.
    Each execution_id can have multiple WebSocket subscribers.
    """

    def __init__(self):
        self._subscribers: Dict[str, List[asyncio.Queue]] = {}

    def subscribe(self, execution_id: str) -> asyncio.Queue:
        """Subscribe to events for an execution."""
        queue: asyncio.Queue = asyncio.Queue(maxsize=100)
        if execution_id not in self._subscribers:
            self._subscribers[execution_id] = []
        self._subscribers[execution_id].append(queue)
        return queue

    def unsubscribe(self, execution_id: str, queue: asyncio.Queue):
        """Unsubscribe from events."""
        if execution_id in self._subscribers:
            try:
                self._subscribers[execution_id].remove(queue)
            except ValueError:
                pass
            if not self._subscribers[execution_id]:
                del self._subscribers[execution_id]

    async def publish(self, execution_id: str, event_type: str, data: Dict):
        """Publish an event to all subscribers of an execution."""
        if execution_id not in self._subscribers:
            return
        message = {"type": event_type, "data": data, "timestamp": datetime.now().isoformat()}
        for queue in self._subscribers[execution_id]:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                # Drop oldest event if queue is full
                try:
                    queue.get_nowait()
                    queue.put_nowait(message)
                except Exception:
                    pass


# ─── Pydantic Models ─────────────────────────────────────────────

class V2ExecuteRequest(BaseModel):
    """Request to start execution"""
    query: str = Field(..., description="User's task/request")
    mode: str = Field("agent", description="Execution mode: instant, auto, agent")
    context: Optional[Dict[str, Any]] = Field(None, description="Additional context")
    conversation_id: Optional[str] = Field(None, description="Conversation ID")


class V2ClarifyRequest(BaseModel):
    """Request to provide clarification"""
    execution_id: str
    answers: Dict[str, str] = Field(..., description="Answers to clarification questions")


# ─── Router Factory ──────────────────────────────────────────────

def create_v2_routes(orchestrator: ExecutionOrchestratorV2) -> APIRouter:
    """
    Create V2 API router with the given orchestrator.

    Args:
        orchestrator: Initialized ExecutionOrchestratorV2

    Returns:
        FastAPI APIRouter
    """
    router = APIRouter(prefix="/api/v2", tags=["agentic-ai-v2"])
    event_bus = EventBus()

    @router.post("/execute")
    async def start_execution(request: V2ExecuteRequest):
        """
        Start a new agentic execution with SSE streaming.

        Modes:
        - **instant**: Quick response, no reasoning or execution
        - **auto**: Light reasoning, auto-execute if confident
        - **agent**: Full reasoning, asks for clarification if needed

        Returns SSE stream of events.
        """
        mode = request.mode.lower()
        if mode not in ("instant", "auto", "agent"):
            mode = "agent"

        conversation_history = None
        if request.context and "messages" in request.context:
            conversation_history = request.context["messages"]

        # Generate execution_id early so WebSocket clients can connect
        import uuid
        execution_id = str(uuid.uuid4())

        async def event_stream():
            try:
                # Send execution_id first so frontend can connect WebSocket
                yield f"event: execution.started\ndata: {json.dumps({'execution_id': execution_id})}\n\n"

                async for event_data in orchestrator.execute_stream(
                    user_request=request.query,
                    mode=mode,
                    conversation_history=conversation_history,
                ):
                    event_type = event_data.get("event", "update")
                    data = event_data.get("data", event_data)

                    # Clean data for JSON serialization
                    clean_data = _clean_for_json(data)

                    # Publish to WebSocket subscribers (for LiveScreen)
                    await event_bus.publish(execution_id, event_type, clean_data)

                    yield f"event: {event_type}\ndata: {json.dumps(clean_data)}\n\n"

                # Final done event
                done_data = {"status": "completed", "execution_id": execution_id}
                await event_bus.publish(execution_id, "done", done_data)
                yield f"event: done\ndata: {json.dumps(done_data)}\n\n"

            except Exception as e:
                logger.error(f"SSE stream error: {e}")
                error_data = {"error": str(e)}
                await event_bus.publish(execution_id, "error", error_data)
                yield f"event: error\ndata: {json.dumps(error_data)}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.post("/clarify")
    async def provide_clarification(request: V2ClarifyRequest):
        """Provide clarification answers to continue execution."""
        try:
            execution = orchestrator.get_execution(request.execution_id)
            if not execution:
                raise HTTPException(status_code=404, detail="Execution not found")

            result = await orchestrator.reasoning_agent.clarify(
                original_request=execution["user_request"],
                clarification_answers=request.answers,
            )

            return {
                "execution_id": request.execution_id,
                "status": "clarification_received",
                "can_proceed": result.can_proceed,
                "message": "Clarification received",
            }

        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Clarification failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    @router.get("/execute/{execution_id}")
    async def get_execution_status(execution_id: str):
        """Get execution status and results."""
        execution = orchestrator.get_execution(execution_id)
        if not execution:
            raise HTTPException(status_code=404, detail="Execution not found")
        return _clean_for_json(execution)

    @router.post("/execute/{execution_id}/cancel")
    async def cancel_execution(execution_id: str):
        """Cancel an active execution."""
        try:
            await orchestrator.cancel_execution(execution_id)
            await event_bus.publish(execution_id, "execution.cancelled", {"execution_id": execution_id})
            return {
                "execution_id": execution_id,
                "status": "cancelled",
                "message": "Execution cancelled",
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @router.websocket("/ws/execute/{execution_id}")
    async def execution_websocket(websocket: WebSocket, execution_id: str):
        """
        WebSocket for real-time execution streaming.

        Streams browser screenshots and execution events to LiveScreen.tsx.
        Events are forwarded from the SSE stream via EventBus.
        """
        await websocket.accept()
        queue = event_bus.subscribe(execution_id)

        try:
            # Send connection confirmation
            await websocket.send_json({
                "type": "connection.established",
                "timestamp": datetime.now().isoformat(),
                "data": {"execution_id": execution_id},
            })

            # Two concurrent tasks:
            # 1. Forward events from EventBus to WebSocket
            # 2. Listen for client messages (ping/cancel)

            async def forward_events():
                """Forward events from EventBus queue to WebSocket."""
                while True:
                    try:
                        message = await asyncio.wait_for(queue.get(), timeout=30)
                        await websocket.send_json(message)
                        if message.get("type") in ("done", "error", "execution.cancelled"):
                            break
                    except asyncio.TimeoutError:
                        # Send keepalive
                        try:
                            await websocket.send_json({"type": "keepalive"})
                        except Exception:
                            break

            async def listen_client():
                """Listen for client messages."""
                while True:
                    try:
                        message = await websocket.receive_json()
                        msg_type = message.get("type")
                        if msg_type == "ping":
                            await websocket.send_json({"type": "pong"})
                        elif msg_type == "cancel":
                            await orchestrator.cancel_execution(execution_id)
                            await websocket.send_json({
                                "type": "execution.cancelled",
                                "data": {"execution_id": execution_id},
                            })
                            break
                    except (WebSocketDisconnect, Exception):
                        break

            # Run both tasks concurrently
            done, pending = await asyncio.wait(
                [
                    asyncio.create_task(forward_events()),
                    asyncio.create_task(listen_client()),
                ],
                return_when=asyncio.FIRST_COMPLETED,
            )
            for task in pending:
                task.cancel()

        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected: {execution_id}")
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
        finally:
            event_bus.unsubscribe(execution_id, queue)
            try:
                await websocket.close()
            except Exception:
                pass

    @router.get("/health")
    async def health_check():
        """V2 health check."""
        return {
            "status": "healthy",
            "service": "agentic-ai-v2",
            "version": "5.0.0",
            "timestamp": datetime.now().isoformat(),
            "components": {
                "reasoning_agent": orchestrator.reasoning_agent is not None,
                "browser_engine": orchestrator.browser_engine is not None,
                "search_layer": orchestrator.search_layer is not None,
                "kimi_client": orchestrator.kimi_client is not None,
                "grok_client": orchestrator.grok_client is not None,
            },
        }

    return router


# ─── Helpers ─────────────────────────────────────────────────────

def _clean_for_json(data: Any) -> Any:
    """Clean data for JSON serialization — remove non-serializable fields."""
    if isinstance(data, dict):
        clean = {}
        for k, v in data.items():
            if k == "stream_callback":
                continue
            try:
                json.dumps(v)
                clean[k] = v
            except (TypeError, ValueError):
                clean[k] = str(v)
        return clean
    return data
