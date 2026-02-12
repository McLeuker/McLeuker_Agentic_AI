"""
Agentic Core API Routes — HTTP/SSE/WebSocket Endpoints
========================================================

Provides API endpoints for the agentic engine:
- POST /api/agentic/execute — Start execution with SSE streaming
- GET  /api/agentic/sessions — List active sessions
- POST /api/agentic/cancel/{session_id} — Cancel execution
- WS   /api/agentic/ws/{session_id} — WebSocket for live screen
- GET  /api/agentic/health — Agentic engine health check
"""

import asyncio
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/agentic", tags=["agentic"])

# Global reference — set during startup
_engine = None
_ws_connections: Dict[str, list] = {}


def set_engine(engine):
    """Set the agentic engine reference."""
    global _engine
    _engine = engine
    logger.info("Agentic API routes: engine connected")


@router.post("/execute")
async def execute_task(request: Request):
    """
    Execute a task with full agentic workflow.

    Returns SSE stream of execution events.
    """
    if not _engine:
        return {"error": "Agentic engine not initialized"}

    body = await request.json()
    user_request = body.get("message", body.get("query", ""))
    mode = body.get("mode", "auto")
    session_id = body.get("session_id")
    user_id = body.get("user_id")
    conversation_history = body.get("conversation_history", [])

    if not user_request:
        return {"error": "No message provided"}

    async def event_stream():
        try:
            async for event in _engine.execute(
                user_request=user_request,
                session_id=session_id,
                user_id=user_id,
                mode=mode,
                conversation_history=conversation_history,
            ):
                event_type = event.get("type", "status")
                event_data = event.get("data", {})

                # SSE format
                yield f"event: {event_type}\ndata: {json.dumps(event_data)}\n\n"

                # Forward to WebSocket clients
                sid = session_id or event.get("session_id", "")
                if sid and sid in _ws_connections:
                    for ws in _ws_connections[sid]:
                        try:
                            await ws.send_json(event)
                        except Exception:
                            pass

            yield "event: done\ndata: {}\n\n"

        except asyncio.CancelledError:
            yield 'event: cancelled\ndata: {"message": "Execution cancelled"}\n\n'
        except Exception as e:
            logger.exception(f"Execution stream error: {e}")
            yield f'event: error\ndata: {{"error": "{str(e)}"}}\n\n'

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        }
    )


@router.get("/sessions")
async def list_sessions(user_id: Optional[str] = None):
    """List active execution sessions."""
    if not _engine:
        return {"sessions": [], "error": "Engine not initialized"}

    return {
        "sessions": _engine.get_active_executions(),
        "state_sessions": _engine.state_manager.list_sessions(user_id=user_id),
    }


@router.post("/cancel/{session_id}")
async def cancel_execution(session_id: str):
    """Cancel an active execution."""
    if not _engine:
        return {"error": "Engine not initialized"}

    _engine.cancel_execution(session_id)
    return {"status": "cancelled", "session_id": session_id}


@router.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    """
    WebSocket endpoint for live execution updates.

    The frontend LiveScreen.tsx connects here to receive:
    - browser.navigated events with screenshots
    - browser.screenshot events
    - step progress events
    - execution status updates
    """
    await websocket.accept()

    if session_id not in _ws_connections:
        _ws_connections[session_id] = []
    _ws_connections[session_id].append(websocket)

    logger.info(f"WebSocket connected for session {session_id}")

    try:
        while True:
            data = await websocket.receive_text()
            msg = json.loads(data)

            if msg.get("type") == "ping":
                await websocket.send_json({"type": "pong", "timestamp": datetime.now().isoformat()})
            elif msg.get("type") == "cancel":
                if _engine:
                    _engine.cancel_execution(session_id)
                await websocket.send_json({"type": "cancelled"})

    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for session {session_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        if session_id in _ws_connections:
            _ws_connections[session_id] = [
                ws for ws in _ws_connections[session_id] if ws != websocket
            ]
            if not _ws_connections[session_id]:
                del _ws_connections[session_id]


@router.get("/health")
async def agentic_health():
    """Agentic engine health check."""
    if not _engine:
        return {
            "status": "not_initialized",
            "engine": False,
        }

    return {
        "status": "healthy",
        "engine": True,
        "planner": _engine.planner is not None,
        "executor": _engine.executor is not None,
        "reflector": _engine.reflector is not None,
        "state_manager": _engine.state_manager is not None,
        "search_layer": _engine.search_layer is not None,
        "browser_engine": _engine.browser_engine is not None,
        "active_executions": len(_engine._active_executions),
        "memory_stats": _engine.state_manager.list_sessions() if _engine.state_manager else [],
    }
