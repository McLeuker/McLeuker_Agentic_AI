"""
WebSocket Handler for Real-Time Execution Streaming
=====================================================

Provides WebSocket connections for:
- Real-time execution progress updates
- Step-by-step status streaming
- Bidirectional control (pause/resume/cancel)
"""

import asyncio
import json
from typing import Dict, Set, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

try:
    from fastapi import WebSocket, WebSocketDisconnect
    FASTAPI_AVAILABLE = True
except ImportError:
    FASTAPI_AVAILABLE = False


class ExecutionWebSocketManager:
    """
    Manages WebSocket connections for execution streaming.

    Features:
    - Multiple clients per execution
    - Automatic cleanup on disconnect
    - Heartbeat to keep connections alive
    - Bidirectional messaging for control
    """

    def __init__(self):
        # execution_id -> set of WebSocket connections
        self._connections: Dict[str, Set] = {}
        # All active connections
        self._all_connections: Set = set()
        logger.info("WebSocket manager initialized")

    async def connect(self, websocket, execution_id: str):
        """Accept a new WebSocket connection for an execution."""
        try:
            await websocket.accept()
        except Exception:
            pass  # Already accepted

        if execution_id not in self._connections:
            self._connections[execution_id] = set()

        self._connections[execution_id].add(websocket)
        self._all_connections.add(websocket)

        logger.info(f"WebSocket connected for execution {execution_id}")

        # Send connection confirmation
        await self._safe_send(websocket, {
            "type": "connected",
            "data": {
                "execution_id": execution_id,
                "timestamp": datetime.now().isoformat(),
            },
        })

    async def disconnect(self, websocket, execution_id: str):
        """Remove a WebSocket connection."""
        if execution_id in self._connections:
            self._connections[execution_id].discard(websocket)
            if not self._connections[execution_id]:
                del self._connections[execution_id]

        self._all_connections.discard(websocket)
        logger.info(f"WebSocket disconnected for execution {execution_id}")

    async def broadcast(self, execution_id: str, event_type: str, data: Dict):
        """Broadcast event to all connections for an execution."""
        if execution_id not in self._connections:
            return

        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }

        disconnected = set()
        for ws in self._connections[execution_id]:
            success = await self._safe_send(ws, message)
            if not success:
                disconnected.add(ws)

        # Clean up disconnected
        for ws in disconnected:
            self._connections[execution_id].discard(ws)
            self._all_connections.discard(ws)

    async def broadcast_all(self, event_type: str, data: Dict):
        """Broadcast to all connected clients."""
        message = {
            "type": event_type,
            "data": data,
            "timestamp": datetime.now().isoformat(),
        }

        disconnected = set()
        for ws in self._all_connections:
            success = await self._safe_send(ws, message)
            if not success:
                disconnected.add(ws)

        for ws in disconnected:
            self._all_connections.discard(ws)

    async def _safe_send(self, websocket, data: Dict) -> bool:
        """Safely send data to a WebSocket."""
        try:
            await websocket.send_json(data)
            return True
        except Exception as e:
            logger.debug(f"WebSocket send failed: {e}")
            return False

    def get_connection_count(self, execution_id: Optional[str] = None) -> int:
        """Get number of active connections."""
        if execution_id:
            return len(self._connections.get(execution_id, set()))
        return len(self._all_connections)

    def create_stream_callback(self, execution_id: str):
        """Create a callback function for ExecutionOrchestrator streaming."""
        async def callback(event_type: str, data: Dict):
            await self.broadcast(execution_id, event_type, data)
        return callback


# Global instance
_ws_manager: Optional[ExecutionWebSocketManager] = None


def get_websocket_manager() -> ExecutionWebSocketManager:
    """Get or create global WebSocket manager."""
    global _ws_manager
    if _ws_manager is None:
        _ws_manager = ExecutionWebSocketManager()
    return _ws_manager
