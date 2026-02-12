"""
Agent Execution API Routes
============================

Provides the /api/v3/agent/* endpoints that use the new agent framework.
These are ADDITIVE — they don't replace any existing v1/v2 endpoints.

Endpoints:
- POST /api/v3/agent/execute — Start an agent execution (SSE stream)
- GET  /api/v3/agent/status/{id} — Get execution status
- WS   /api/v3/agent/ws/{id} — WebSocket for live screenshots
"""

import json
import asyncio
from typing import Optional
from fastapi import APIRouter, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

import logging
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v3/agent", tags=["agent"])


class AgentExecuteRequest(BaseModel):
    prompt: str
    conversation_id: Optional[str] = None
    context: Optional[dict] = None


def create_agent_routes(execution_engine, ws_manager):
    """
    Create agent routes with the given execution engine and websocket manager.
    Called from main.py during startup.
    """

    @router.post("/execute")
    async def execute_agent(request: AgentExecuteRequest):
        """Start an agent execution and stream events via SSE."""

        async def event_stream():
            try:
                async for event in execution_engine.execute_stream(
                    user_request=request.prompt,
                    context=request.context,
                ):
                    event_type = event.get("event", "unknown")
                    event_data = event.get("data", {})

                    # Format as SSE
                    payload = json.dumps({
                        "type": event_type,
                        "data": event_data,
                    })
                    yield f"data: {payload}\n\n"

                    # Also broadcast via WebSocket for live screen
                    if event_type == "browser_screenshot":
                        await ws_manager.broadcast(
                            "browser_screenshot",
                            event_data,
                        )

            except Exception as e:
                logger.error(f"Agent execution error: {e}")
                error_payload = json.dumps({
                    "type": "error",
                    "data": {"message": str(e)},
                })
                yield f"data: {error_payload}\n\n"

        return StreamingResponse(
            event_stream(),
            media_type="text/event-stream",
            headers={
                "Cache-Control": "no-cache",
                "Connection": "keep-alive",
                "X-Accel-Buffering": "no",
            },
        )

    @router.websocket("/ws/{execution_id}")
    async def agent_websocket(websocket: WebSocket, execution_id: str):
        """WebSocket endpoint for live browser screenshots."""
        await ws_manager.connect(websocket, execution_id)
        try:
            while True:
                # Keep connection alive, receive any client messages
                data = await websocket.receive_text()
                # Client can send commands like "screenshot" to request current state
                if data == "screenshot" and execution_engine.browser:
                    state = execution_engine.browser.state
                    if state.screenshot_b64:
                        await websocket.send_json({
                            "type": "browser_screenshot",
                            "data": {
                                "image": state.screenshot_b64,
                                "url": state.url,
                                "title": state.title,
                            }
                        })
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket, execution_id)
        except Exception as e:
            logger.error(f"WebSocket error: {e}")
            ws_manager.disconnect(websocket, execution_id)

    @router.websocket("/ws")
    async def agent_websocket_global(websocket: WebSocket):
        """Global WebSocket for all execution events."""
        await ws_manager.connect(websocket)
        try:
            while True:
                await websocket.receive_text()
        except WebSocketDisconnect:
            ws_manager.disconnect(websocket)
        except Exception as e:
            ws_manager.disconnect(websocket)

    return router
