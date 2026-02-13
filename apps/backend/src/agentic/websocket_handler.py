"""
WebSocket Handler for Real-time Browser Screenshots
====================================================

Handles WebSocket connections for live browser screenshot streaming
to the frontend LiveScreen component.
"""

import asyncio
import json
import logging
from typing import Dict, Optional, Set
from fastapi import WebSocket, WebSocketDisconnect
from dataclasses import dataclass, asdict
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ScreenshotMessage:
    """Screenshot message structure for WebSocket."""
    type: str = "browser_screenshot"
    image: str = ""  # base64 encoded JPEG
    url: str = ""
    title: str = ""
    action: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "data": {
                "image": self.image,
                "url": self.url,
                "title": self.title,
                "action": self.action,
                "timestamp": self.timestamp,
            }
        }


@dataclass
class ExecutionMessage:
    """Execution status message."""
    type: str
    step_id: int
    tool: str
    status: str  # pending, running, completed, failed
    title: str = ""
    instruction: str = ""
    result_summary: str = ""
    execution_time_ms: int = 0
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "data": {
                "step_id": self.step_id,
                "tool": self.tool,
                "status": self.status,
                "title": self.title,
                "instruction": self.instruction,
                "result_summary": self.result_summary,
                "execution_time_ms": self.execution_time_ms,
                "timestamp": self.timestamp,
            }
        }


@dataclass
class ReasoningMessage:
    """Reasoning/thinking message."""
    type: str = "reasoning"
    content: str = ""
    timestamp: str = ""
    
    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> dict:
        return {
            "type": self.type,
            "data": {
                "content": self.content,
                "timestamp": self.timestamp,
            }
        }


class ExecutionWebSocketManager:
    """
    Manages WebSocket connections for execution streaming.
    
    Features:
    - Multi-client support per execution
    - Automatic reconnection handling
    - Heartbeat/ping-pong
    - Message queuing for offline clients
    """
    
    def __init__(self):
        # execution_id -> set of WebSocket connections
        self.connections: Dict[str, Set[WebSocket]] = {}
        # execution_id -> message queue for offline clients
        self.message_queues: Dict[str, list] = {}
        # Track connection health
        self.connection_heartbeats: Dict[WebSocket, datetime] = {}
        self._cleanup_task: Optional[asyncio.Task] = None
    
    async def start(self):
        """Start the WebSocket manager."""
        self._cleanup_task = asyncio.create_task(self._cleanup_loop())
        logger.info("WebSocket manager started")
    
    async def stop(self):
        """Stop the WebSocket manager and close all connections."""
        if self._cleanup_task:
            self._cleanup_task.cancel()
        
        # Close all connections
        for execution_id, websockets in self.connections.items():
            for ws in websockets:
                try:
                    await ws.close()
                except Exception:
                    pass
        
        self.connections.clear()
        self.message_queues.clear()
        logger.info("WebSocket manager stopped")
    
    async def connect(self, websocket: WebSocket, execution_id: str):
        """Accept a new WebSocket connection."""
        await websocket.accept()
        
        if execution_id not in self.connections:
            self.connections[execution_id] = set()
        
        self.connections[execution_id].add(websocket)
        self.connection_heartbeats[websocket] = datetime.now()
        
        # Send any queued messages
        if execution_id in self.message_queues:
            for message in self.message_queues[execution_id]:
                try:
                    await websocket.send_json(message)
                except Exception:
                    break
            # Clear queue after sending
            del self.message_queues[execution_id]
        
        logger.info(f"WebSocket connected for execution {execution_id}. Total connections: {len(self.connections[execution_id])}")
    
    async def disconnect(self, websocket: WebSocket, execution_id: str):
        """Remove a WebSocket connection."""
        if execution_id in self.connections:
            self.connections[execution_id].discard(websocket)
            if not self.connections[execution_id]:
                del self.connections[execution_id]
        
        self.connection_heartbeats.pop(websocket, None)
        
        try:
            await websocket.close()
        except Exception:
            pass
        
        logger.info(f"WebSocket disconnected for execution {execution_id}")
    
    async def broadcast_screenshot(
        self,
        execution_id: str,
        image_base64: str,
        url: str = "",
        title: str = "",
        action: str = ""
    ):
        """Broadcast a screenshot to all connected clients."""
        message = ScreenshotMessage(
            image=image_base64,
            url=url,
            title=title,
            action=action,
        ).to_dict()
        
        await self._broadcast(execution_id, message)
    
    async def broadcast_step_update(
        self,
        execution_id: str,
        step_id: int,
        tool: str,
        status: str,
        title: str = "",
        instruction: str = "",
        result_summary: str = "",
        execution_time_ms: int = 0
    ):
        """Broadcast a step update to all connected clients."""
        message = ExecutionMessage(
            type="step_update",
            step_id=step_id,
            tool=tool,
            status=status,
            title=title,
            instruction=instruction,
            result_summary=result_summary,
            execution_time_ms=execution_time_ms,
        ).to_dict()
        
        await self._broadcast(execution_id, message)
    
    async def broadcast_reasoning(self, execution_id: str, content: str):
        """Broadcast reasoning content to all connected clients."""
        message = ReasoningMessage(content=content).to_dict()
        await self._broadcast(execution_id, message)
    
    async def broadcast_completion(self, execution_id: str, success: bool, result: dict = None):
        """Broadcast execution completion."""
        message = {
            "type": "execution_complete",
            "data": {
                "success": success,
                "result": result or {},
                "timestamp": datetime.now().isoformat(),
            }
        }
        await self._broadcast(execution_id, message)
    
    async def broadcast_error(self, execution_id: str, error: str):
        """Broadcast an error message."""
        message = {
            "type": "error",
            "data": {
                "error": error,
                "timestamp": datetime.now().isoformat(),
            }
        }
        await self._broadcast(execution_id, message)
    
    async def _broadcast(self, execution_id: str, message: dict):
        """Internal broadcast method with queue fallback."""
        if execution_id not in self.connections or not self.connections[execution_id]:
            # Queue message for later
            if execution_id not in self.message_queues:
                self.message_queues[execution_id] = []
            self.message_queues[execution_id].append(message)
            # Limit queue size
            if len(self.message_queues[execution_id]) > 100:
                self.message_queues[execution_id] = self.message_queues[execution_id][-100:]
            return
        
        disconnected = set()
        for ws in self.connections[execution_id]:
            try:
                await ws.send_json(message)
                self.connection_heartbeats[ws] = datetime.now()
            except Exception as e:
                logger.warning(f"Failed to send to WebSocket: {e}")
                disconnected.add(ws)
        
        # Clean up disconnected clients
        for ws in disconnected:
            await self.disconnect(ws, execution_id)
    
    async def _cleanup_loop(self):
        """Periodic cleanup of stale connections."""
        while True:
            try:
                await asyncio.sleep(30)  # Check every 30 seconds
                
                now = datetime.now()
                stale_threshold = 60  # 60 seconds without heartbeat
                
                for execution_id, websockets in list(self.connections.items()):
                    stale = set()
                    for ws in websockets:
                        last_heartbeat = self.connection_heartbeats.get(ws)
                        if last_heartbeat and (now - last_heartbeat).seconds > stale_threshold:
                            stale.add(ws)
                    
                    for ws in stale:
                        logger.info(f"Removing stale WebSocket connection for {execution_id}")
                        await self.disconnect(ws, execution_id)
                        
            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Cleanup loop error: {e}")


# Global WebSocket manager instance
_websocket_manager: Optional[ExecutionWebSocketManager] = None


def get_websocket_manager() -> ExecutionWebSocketManager:
    """Get or create the global WebSocket manager."""
    global _websocket_manager
    if _websocket_manager is None:
        _websocket_manager = ExecutionWebSocketManager()
    return _websocket_manager


async def initialize_websocket_manager():
    """Initialize the WebSocket manager on startup."""
    manager = get_websocket_manager()
    await manager.start()
    return manager


async def shutdown_websocket_manager():
    """Shutdown the WebSocket manager."""
    global _websocket_manager
    if _websocket_manager:
        await _websocket_manager.stop()
        _websocket_manager = None
