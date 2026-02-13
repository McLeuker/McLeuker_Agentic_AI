"""
WebSocket V2 - Real-time Execution Streaming
=============================================
Enhanced WebSocket manager for agentic AI execution streaming.
Works alongside the existing ExecutionWebSocketManager in websocket_handler.py.

Features:
- Session management with heartbeat
- Execution stream lifecycle (start / step / screenshot / error / end)
- Channel-based subscriptions
- Automatic cleanup of stale sessions
"""

import asyncio
import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Set
from uuid import uuid4

from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Session
# ---------------------------------------------------------------------------

@dataclass
class WebSocketSessionV2:
    """Represents a connected WebSocket client."""
    session_id: str = field(default_factory=lambda: str(uuid4()))
    websocket: Optional[WebSocket] = None
    user_id: Optional[str] = None
    conversation_id: Optional[str] = None
    subscriptions: Set[str] = field(default_factory=set)
    connected_at: datetime = field(default_factory=datetime.utcnow)
    last_ping: datetime = field(default_factory=datetime.utcnow)
    is_alive: bool = True


# ---------------------------------------------------------------------------
# Manager
# ---------------------------------------------------------------------------

class WebSocketManagerV2:
    """
    Manages WebSocket connections for real-time execution streaming.
    Designed to coexist with the existing ExecutionWebSocketManager.
    """

    def __init__(
        self,
        heartbeat_interval: float = 30.0,
        heartbeat_timeout: float = 60.0,
    ):
        self._sessions: Dict[str, WebSocketSessionV2] = {}
        self._execution_sessions: Dict[str, Set[str]] = {}  # execution_id -> session_ids
        self._conversation_sessions: Dict[str, Set[str]] = {}  # conversation_id -> session_ids
        self._heartbeat_interval = heartbeat_interval
        self._heartbeat_timeout = heartbeat_timeout
        self._cleanup_task: Optional[asyncio.Task] = None
        logger.info("WebSocketManagerV2 initialized")

    async def start(self):
        """Start background tasks."""
        if not self._cleanup_task:
            self._cleanup_task = asyncio.create_task(self._cleanup_loop())

    async def stop(self):
        """Stop background tasks."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
            self._cleanup_task = None

    # -- Connection lifecycle --------------------------------------------------

    async def connect(
        self,
        websocket: WebSocket,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> WebSocketSessionV2:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        session = WebSocketSessionV2(
            websocket=websocket,
            user_id=user_id,
            conversation_id=conversation_id,
        )
        self._sessions[session.session_id] = session

        # Subscribe to conversation channel
        if conversation_id:
            if conversation_id not in self._conversation_sessions:
                self._conversation_sessions[conversation_id] = set()
            self._conversation_sessions[conversation_id].add(session.session_id)
            session.subscriptions.add(f"conversation:{conversation_id}")

        # Send connection established
        await self._send(session, {
            "type": "connection.established",
            "session_id": session.session_id,
            "timestamp": datetime.utcnow().isoformat(),
        })

        logger.info(f"WS V2 connected: {session.session_id} (user={user_id}, conv={conversation_id})")
        return session

    async def disconnect(self, session_id: str):
        """Disconnect a session."""
        session = self._sessions.pop(session_id, None)
        if not session:
            return

        # Remove from execution subscriptions
        for exec_id, sids in list(self._execution_sessions.items()):
            sids.discard(session_id)
            if not sids:
                del self._execution_sessions[exec_id]

        # Remove from conversation subscriptions
        for conv_id, sids in list(self._conversation_sessions.items()):
            sids.discard(session_id)
            if not sids:
                del self._conversation_sessions[conv_id]

        session.is_alive = False
        logger.info(f"WS V2 disconnected: {session_id}")

    # -- Message handling ------------------------------------------------------

    async def handle_message(self, session_id: str, data: Dict[str, Any]):
        """Handle an incoming message from a client."""
        session = self._sessions.get(session_id)
        if not session:
            return

        msg_type = data.get("type", "")

        if msg_type == "ping":
            session.last_ping = datetime.utcnow()
            await self._send(session, {"type": "pong", "timestamp": datetime.utcnow().isoformat()})

        elif msg_type == "subscribe":
            channel = data.get("channel", "")
            if channel:
                session.subscriptions.add(channel)
                # Handle conversation subscription
                conv_id = data.get("conversation_id")
                if conv_id:
                    if conv_id not in self._conversation_sessions:
                        self._conversation_sessions[conv_id] = set()
                    self._conversation_sessions[conv_id].add(session_id)
                # Handle execution subscription
                exec_id = data.get("execution_id")
                if exec_id:
                    if exec_id not in self._execution_sessions:
                        self._execution_sessions[exec_id] = set()
                    self._execution_sessions[exec_id].add(session_id)

        elif msg_type == "unsubscribe":
            channel = data.get("channel", "")
            session.subscriptions.discard(channel)

    # -- Execution streaming ---------------------------------------------------

    async def start_execution_stream(
        self, execution_id: str, conversation_id: Optional[str] = None,
        user_id: Optional[str] = None,
    ):
        """Notify clients that an execution has started."""
        payload = {
            "type": "execution.started",
            "execution_id": execution_id,
            "conversation_id": conversation_id,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_conversation(conversation_id, payload)

    async def stream_step(self, execution_id: str, step_data: Dict[str, Any]):
        """Stream a step update."""
        payload = {"type": "execution.step", "execution_id": execution_id, "step": step_data}
        await self._broadcast_to_execution(execution_id, payload)

    async def stream_thought(self, execution_id: str, thought: str):
        payload = {"type": "execution.thought", "execution_id": execution_id, "thought": thought}
        await self._broadcast_to_execution(execution_id, payload)

    async def stream_tool_call(self, execution_id: str, tool_name: str, tool_input: Dict):
        payload = {
            "type": "execution.tool_call",
            "execution_id": execution_id,
            "tool_name": tool_name,
            "tool_input": tool_input,
        }
        await self._broadcast_to_execution(execution_id, payload)

    async def stream_tool_result(self, execution_id: str, tool_name: str, result: Any, success: bool = True):
        payload = {
            "type": "execution.tool_result",
            "execution_id": execution_id,
            "tool_name": tool_name,
            "result": result,
            "success": success,
        }
        await self._broadcast_to_execution(execution_id, payload)

    async def stream_screenshot(self, execution_id: str, screenshot_b64: str, metadata: Optional[Dict] = None):
        payload = {
            "type": "execution.screenshot",
            "execution_id": execution_id,
            "screenshot": screenshot_b64,
            "metadata": metadata or {},
        }
        await self._broadcast_to_execution(execution_id, payload)

    async def stream_error(self, execution_id: str, error: str):
        payload = {"type": "execution.error", "execution_id": execution_id, "error": error}
        await self._broadcast_to_execution(execution_id, payload)

    async def end_execution_stream(self, execution_id: str, success: bool = True):
        payload = {
            "type": "execution.completed" if success else "execution.failed",
            "execution_id": execution_id,
            "success": success,
            "timestamp": datetime.utcnow().isoformat(),
        }
        await self._broadcast_to_execution(execution_id, payload)
        # Clean up
        self._execution_sessions.pop(execution_id, None)

    # -- Broadcasting ----------------------------------------------------------

    async def _send(self, session: WebSocketSessionV2, data: Dict[str, Any]):
        """Send data to a single session."""
        if not session.websocket or not session.is_alive:
            return
        try:
            await session.websocket.send_json(data)
        except Exception as e:
            logger.warning(f"Failed to send to {session.session_id}: {e}")
            session.is_alive = False

    async def _broadcast_to_execution(self, execution_id: str, data: Dict[str, Any]):
        """Broadcast to all sessions subscribed to an execution."""
        session_ids = self._execution_sessions.get(execution_id, set())
        # Also broadcast to conversation sessions
        conv_id = data.get("conversation_id")
        if conv_id:
            session_ids = session_ids | self._conversation_sessions.get(conv_id, set())
        # Fallback: broadcast to all sessions if no specific subscriptions
        if not session_ids:
            session_ids = set(self._sessions.keys())
        for sid in list(session_ids):
            session = self._sessions.get(sid)
            if session:
                await self._send(session, data)

    async def _broadcast_to_conversation(self, conversation_id: Optional[str], data: Dict[str, Any]):
        """Broadcast to all sessions subscribed to a conversation."""
        if not conversation_id:
            # Broadcast to all
            for session in self._sessions.values():
                await self._send(session, data)
            return
        session_ids = self._conversation_sessions.get(conversation_id, set())
        for sid in list(session_ids):
            session = self._sessions.get(sid)
            if session:
                await self._send(session, data)

    async def broadcast_all(self, data: Dict[str, Any]):
        """Broadcast to all connected sessions."""
        for session in self._sessions.values():
            await self._send(session, data)

    # -- Cleanup ---------------------------------------------------------------

    async def _cleanup_loop(self):
        """Periodically clean up stale sessions."""
        while True:
            try:
                await asyncio.sleep(self._heartbeat_interval)
                now = datetime.utcnow()
                stale = []
                for sid, session in self._sessions.items():
                    if not session.is_alive:
                        stale.append(sid)
                    elif (now - session.last_ping).total_seconds() > self._heartbeat_timeout:
                        stale.append(sid)
                for sid in stale:
                    await self.disconnect(sid)
                    logger.info(f"Cleaned up stale session: {sid}")
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup error: {e}")

    # -- Stats -----------------------------------------------------------------

    def get_stats(self) -> Dict[str, Any]:
        return {
            "total_sessions": len(self._sessions),
            "active_executions": len(self._execution_sessions),
            "conversation_subscriptions": len(self._conversation_sessions),
        }


# ---------------------------------------------------------------------------
# Execution Stream Manager (high-level wrapper)
# ---------------------------------------------------------------------------

class ExecutionStreamManagerV2:
    """
    High-level wrapper for execution streaming.
    Used by the AgentOrchestrator to push updates.
    """

    def __init__(self, ws_manager: WebSocketManagerV2):
        self.ws_manager = ws_manager

    async def start_execution_stream(self, execution_id: str, conversation_id: Optional[str] = None, user_id: Optional[str] = None):
        await self.ws_manager.start_execution_stream(execution_id, conversation_id, user_id)

    async def stream_step(self, execution_id: str, step_data: Dict[str, Any]):
        await self.ws_manager.stream_step(execution_id, step_data)

    async def stream_thought(self, execution_id: str, thought: str):
        await self.ws_manager.stream_thought(execution_id, thought)

    async def stream_tool_call(self, execution_id: str, tool_name: str, tool_input: Dict):
        await self.ws_manager.stream_tool_call(execution_id, tool_name, tool_input)

    async def stream_tool_result(self, execution_id: str, tool_name: str, result: Any, success: bool = True):
        await self.ws_manager.stream_tool_result(execution_id, tool_name, result, success)

    async def stream_screenshot(self, execution_id: str, screenshot_b64: str, metadata: Optional[Dict] = None):
        await self.ws_manager.stream_screenshot(execution_id, screenshot_b64, metadata)

    async def stream_error(self, execution_id: str, error: str):
        await self.ws_manager.stream_error(execution_id, error)

    async def end_execution_stream(self, execution_id: str, success: bool = True):
        await self.ws_manager.end_execution_stream(execution_id, success)
