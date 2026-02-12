"""
WebSocket Manager — Real-time event streaming
================================================

Manages WebSocket connections for:
- Browser screenshot streaming
- Execution progress updates
- Live screen sharing
"""

import asyncio
import json
from typing import Dict, Set, Any, Optional
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


class ExecutionWebSocketManager:
    """Manages WebSocket connections for execution streaming."""

    def __init__(self):
        self._connections: Dict[str, Set[WebSocket]] = {}  # execution_id -> websockets
        self._global_connections: Set[WebSocket] = set()

    async def connect(self, websocket: WebSocket, execution_id: Optional[str] = None):
        """Accept a WebSocket connection."""
        await websocket.accept()
        if execution_id:
            if execution_id not in self._connections:
                self._connections[execution_id] = set()
            self._connections[execution_id].add(websocket)
        else:
            self._global_connections.add(websocket)
        logger.info(f"WebSocket connected (execution: {execution_id or 'global'})")

    def disconnect(self, websocket: WebSocket, execution_id: Optional[str] = None):
        """Remove a WebSocket connection."""
        if execution_id and execution_id in self._connections:
            self._connections[execution_id].discard(websocket)
            if not self._connections[execution_id]:
                del self._connections[execution_id]
        self._global_connections.discard(websocket)

    async def broadcast(self, event_type: str, data: Dict, execution_id: Optional[str] = None):
        """Broadcast an event to all relevant connections."""
        message = json.dumps({"type": event_type, "data": data})
        targets = set()

        if execution_id and execution_id in self._connections:
            targets.update(self._connections[execution_id])
        targets.update(self._global_connections)

        disconnected = set()
        for ws in targets:
            try:
                await ws.send_text(message)
            except Exception:
                disconnected.add(ws)

        # Clean up disconnected
        for ws in disconnected:
            self._global_connections.discard(ws)
            for eid in list(self._connections.keys()):
                self._connections[eid].discard(ws)

    async def send_screenshot(self, screenshot_b64: str, url: str, title: str, execution_id: Optional[str] = None):
        """Send a browser screenshot to connected clients."""
        await self.broadcast("browser_screenshot", {
            "image": screenshot_b64,
            "url": url,
            "title": title,
        }, execution_id)
