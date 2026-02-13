"""
Computer Use Agent — GUI Automation with Real-time Screenshots
===============================================================

Enables the AI to control a browser environment through:
- Screenshot capture and analysis
- Mouse control (move, click, scroll)
- Keyboard input (typing, shortcuts)
- Real-time streaming via WebSocket

Integrates with LiveScreen.tsx for frontend visualization.
"""

import asyncio
import base64
import json
import logging
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncGenerator, Dict, List, Optional, Tuple

import openai

# Try to import Playwright
try:
    from playwright.async_api import async_playwright, Page, Browser, BrowserContext
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False
    logging.warning("Playwright not available - Computer Use Agent will have limited functionality")

from agentic.websocket_handler import get_websocket_manager

logger = logging.getLogger(__name__)


class MouseAction(Enum):
    MOVE = "move"
    CLICK = "click"
    DOUBLE_CLICK = "double_click"
    RIGHT_CLICK = "right_click"
    SCROLL = "scroll"


class KeyAction(Enum):
    TYPE = "type"
    PRESS = "press"
    HOTKEY = "hotkey"


@dataclass
class ComputerAction:
    """A single computer action to execute."""
    action_type: str  # "mouse", "keyboard", "screenshot", "wait", "navigate"
    params: Dict[str, Any] = field(default_factory=dict)
    reasoning: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "action_type": self.action_type,
            "params": self.params,
            "reasoning": self.reasoning,
        }


@dataclass
class ActionResult:
    """Result of executing a computer action."""
    success: bool
    action: ComputerAction
    screenshot: Optional[str] = None  # base64 encoded
    error: Optional[str] = None
    execution_time_ms: float = 0
    url: str = ""
    title: str = ""
    
    def to_dict(self) -> Dict:
        return {
            "success": self.success,
            "action": self.action.to_dict(),
            "error": self.error,
            "execution_time_ms": self.execution_time_ms,
            "url": self.url,
            "title": self.title,
        }


class ComputerUseAgent:
    """
    Computer Use Agent for GUI automation and task execution.
    
    Features:
    - Screenshot-based reasoning with kimi-2.5 vision
    - Mouse and keyboard control
    - Real-time WebSocket streaming to frontend
    - Multi-step task execution
    
    Usage:
        agent = ComputerUseAgent(kimi_client)
        await agent.initialize()
        async for event in agent.execute_task("task", execution_id="exec_123"):
            print(event)
    """
    
    def __init__(
        self,
        llm_client: openai.AsyncOpenAI,
        model: str = "kimi-k2.5",
        viewport_width: int = 1280,
        viewport_height: int = 720,
        headless: bool = True,
    ):
        self.llm_client = llm_client
        self.model = model
        self.viewport_width = viewport_width
        self.viewport_height = viewport_height
        self.headless = headless
        
        # Playwright instances
        self._playwright = None
        self._browser: Optional[Browser] = None
        self._context: Optional[BrowserContext] = None
        self._page: Optional[Page] = None
        
        # State
        self._initialized = False
        self._action_history: List[ActionResult] = []
        self._max_history = 10
        
        # WebSocket manager for streaming
        self._ws_manager = get_websocket_manager()
    
    @property
    def is_available(self) -> bool:
        """Check if Computer Use Agent is available."""
        return PLAYWRIGHT_AVAILABLE and self.llm_client is not None
    
    async def initialize(self):
        """Initialize the browser environment."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not available. Install with: pip install playwright && playwright install chromium")
        
        if self._initialized:
            return
        
        try:
            self._playwright = await async_playwright().start()
            
            # Launch browser
            self._browser = await self._playwright.chromium.launch(
                headless=self.headless,
                args=[
                    "--no-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-gpu",
                    f"--window-size={self.viewport_width},{self.viewport_height}",
                ]
            )
            
            # Create context with viewport
            self._context = await self._browser.new_context(
                viewport={"width": self.viewport_width, "height": self.viewport_height},
                user_agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            )
            
            # Create page
            self._page = await self._context.new_page()
            
            self._initialized = True
            logger.info("Computer Use Agent initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize Computer Use Agent: {e}")
            raise
    
    async def shutdown(self):
        """Shutdown the browser environment."""
        if self._page:
            await self._page.close()
        if self._context:
            await self._context.close()
        if self._browser:
            await self._browser.close()
        if self._playwright:
            await self._playwright.stop()
        
        self._initialized = False
        logger.info("Computer Use Agent shutdown")
    
    async def execute_task(
        self,
        task: str,
        execution_id: str,
        max_steps: int = 30,
        starting_url: Optional[str] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a computer automation task with real-time streaming.
        
        Args:
            task: Natural language description of the task
            execution_id: Unique execution ID for WebSocket streaming
            max_steps: Maximum number of actions to take
            starting_url: Optional URL to start at
            
        Yields:
            Events with type: "start", "thinking", "action", "screenshot", "complete", "error"
        """
        if not self._initialized:
            await self.initialize()
        
        # Start event
        yield {"type": "start", "data": {"task": task, "max_steps": max_steps}}
        
        # Navigate to starting URL if provided
        if starting_url and self._page:
            await self._page.goto(starting_url, wait_until="networkidle")
            yield {"type": "navigation", "data": {"url": starting_url}}
        
        # Execute task loop
        for step in range(max_steps):
            try:
                # Capture screenshot
                screenshot_b64 = await self._capture_screenshot()
                url = self._page.url if self._page else ""
                title = await self._page.title() if self._page else ""
                
                # Stream screenshot via WebSocket
                await self._ws_manager.broadcast_screenshot(
                    execution_id=execution_id,
                    image_base64=screenshot_b64,
                    url=url,
                    title=title,
                    action=f"Step {step + 1}: Analyzing..."
                )
                
                yield {
                    "type": "screenshot",
                    "data": {
                        "step": step,
                        "screenshot": screenshot_b64,
                        "url": url,
                        "title": title,
                    }
                }
                
                # Get next action from LLM
                action = await self._get_next_action(task, screenshot_b64, step)
                
                if action is None:
                    yield {"type": "thinking", "data": {"step": step, "message": "Task appears complete"}}
                    break
                
                yield {"type": "thinking", "data": {"step": step, "reasoning": action.reasoning}}
                yield {"type": "action", "data": {"step": step, "action": action.to_dict()}}
                
                # Stream step update
                await self._ws_manager.broadcast_step_update(
                    execution_id=execution_id,
                    step_id=step,
                    tool=action.action_type,
                    status="running",
                    title=action.action_type,
                    instruction=action.reasoning,
                )
                
                # Execute action
                result = await self._execute_action(action)
                self._action_history.append(result)
                
                # Stream result screenshot
                if result.screenshot:
                    await self._ws_manager.broadcast_screenshot(
                        execution_id=execution_id,
                        image_base64=result.screenshot,
                        url=result.url,
                        title=result.title,
                        action=f"Step {step + 1}: {action.action_type}"
                    )
                    
                    yield {
                        "type": "screenshot",
                        "data": {
                            "step": step,
                            "after_action": True,
                            "screenshot": result.screenshot,
                            "url": result.url,
                            "title": result.title,
                        }
                    }
                
                # Stream step completion
                await self._ws_manager.broadcast_step_update(
                    execution_id=execution_id,
                    step_id=step,
                    tool=action.action_type,
                    status="completed" if result.success else "failed",
                    title=action.action_type,
                    result_summary=result.error if result.error else "Success",
                    execution_time_ms=int(result.execution_time_ms),
                )
                
                if not result.success:
                    yield {"type": "error", "data": {"step": step, "error": result.error}}
                    # Try to recover
                    continue
                
                # Check if task is complete
                if await self._is_task_complete(task):
                    yield {"type": "thinking", "data": {"step": step, "message": "Task completed successfully"}}
                    break
                
                # Small delay between actions
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error in step {step}: {e}")
                yield {"type": "error", "data": {"step": step, "error": str(e)}}
                
                # Stream error
                await self._ws_manager.broadcast_error(execution_id, str(e))
                break
        
        # Complete event
        final_screenshot = await self._capture_screenshot()
        url = self._page.url if self._page else ""
        title = await self._page.title() if self._page else ""
        
        # Stream final screenshot
        await self._ws_manager.broadcast_screenshot(
            execution_id=execution_id,
            image_base64=final_screenshot,
            url=url,
            title=title,
            action="Task Complete"
        )
        
        # Stream completion
        await self._ws_manager.broadcast_completion(
            execution_id=execution_id,
            success=True,
            result={
                "steps_taken": len(self._action_history),
                "final_url": url,
                "final_title": title,
            }
        )
        
        yield {
            "type": "complete",
            "data": {
                "task": task,
                "steps_taken": len(self._action_history),
                "final_screenshot": final_screenshot,
                "final_url": url,
                "final_title": title,
            }
        }
    
    async def _capture_screenshot(self) -> str:
        """Capture screenshot and return base64 encoded string."""
        if not self._page:
            raise RuntimeError("Page not initialized")
        
        screenshot_bytes = await self._page.screenshot(
            type="jpeg",
            quality=80,
            full_page=False,
        )
        
        return base64.b64encode(screenshot_bytes).decode("utf-8")
    
    async def _get_next_action(
        self,
        task: str,
        screenshot_b64: str,
        step: int,
    ) -> Optional[ComputerAction]:
        """Use LLM to determine the next action based on screenshot and task."""
        messages = [
            {
                "role": "system",
                "content": """You are a computer automation assistant. Analyze the screenshot and determine the next action to complete the task.

Available actions:
1. navigate {"url": "https://..."} - Navigate to a URL
2. mouse_move {"x": int, "y": int} - Move mouse to coordinates
3. mouse_click {"x": int, "y": int, "button": "left"|"right"} - Click at coordinates
4. mouse_double_click {"x": int, "y": int} - Double click at coordinates
5. mouse_scroll {"x": int, "y": int, "scroll_amount": int} - Scroll at position
6. keyboard_type {"text": str} - Type text
7. keyboard_press {"key": str} - Press a key (Enter, Tab, Escape, etc.)
8. keyboard_hotkey {"keys": [str]} - Press key combination (e.g., ["ctrl", "a"])
9. wait {"duration": float} - Wait for specified seconds
10. complete {} - Task is complete

Respond with JSON:
{
    "reasoning": "Explain what you see and what action to take",
    "action": "action_name",
    "params": {...}
}

Viewport size: 1280x720
Coordinates are in pixels from top-left (0,0)."""
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Task: {task}\n\nCurrent step: {step}\n\nWhat is the next action?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{screenshot_b64}"}}
                ]
            }
        ]
        
        # Add action history context
        if self._action_history:
            recent_actions = self._action_history[-3:]
            history_text = "\n".join([
                f"Step {i}: {r.action.action_type} - {'success' if r.success else 'failed'}"
                for i, r in enumerate(recent_actions)
            ])
            messages.append({
                "role": "user",
                "content": f"Recent actions:\n{history_text}"
            })
        
        try:
            response = await self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.7,
                max_tokens=1024,
                response_format={"type": "json_object"},
            )
            
            result = json.loads(response.choices[0].message.content)
            
            if result.get("action") == "complete":
                return None
            
            return ComputerAction(
                action_type=result.get("action", "wait"),
                params=result.get("params", {}),
                reasoning=result.get("reasoning", ""),
            )
            
        except Exception as e:
            logger.error(f"Error getting next action from LLM: {e}")
            # Fallback to wait
            return ComputerAction(
                action_type="wait",
                params={"duration": 1.0},
                reasoning="Error occurred, waiting...",
            )
    
    async def _execute_action(self, action: ComputerAction) -> ActionResult:
        """Execute a computer action."""
        start_time = time.time()
        
        if not self._page:
            return ActionResult(
                success=False,
                action=action,
                error="Page not initialized",
                execution_time_ms=0,
            )
        
        try:
            action_type = action.action_type
            params = action.params
            
            if action_type == "navigate":
                url = params.get("url", "")
                await self._page.goto(url, wait_until="networkidle")
                
            elif action_type == "mouse_move":
                await self._page.mouse.move(params["x"], params["y"])
                
            elif action_type == "mouse_click":
                x, y = params.get("x", 0), params.get("y", 0)
                button = params.get("button", "left")
                await self._page.mouse.click(x, y, button=button)
                
            elif action_type == "mouse_double_click":
                x, y = params.get("x", 0), params.get("y", 0)
                await self._page.mouse.dblclick(x, y)
                
            elif action_type == "mouse_scroll":
                x, y = params.get("x", 0), params.get("y", 0)
                scroll_amount = params.get("scroll_amount", 0)
                await self._page.mouse.move(x, y)
                await self._page.mouse.wheel(0, scroll_amount)
                
            elif action_type == "keyboard_type":
                text = params.get("text", "")
                await self._page.keyboard.type(text)
                
            elif action_type == "keyboard_press":
                key = params.get("key", "")
                await self._page.keyboard.press(key)
                
            elif action_type == "keyboard_hotkey":
                keys = params.get("keys", [])
                for key in keys[:-1]:
                    await self._page.keyboard.down(key)
                if keys:
                    await self._page.keyboard.press(keys[-1])
                for key in reversed(keys[:-1]):
                    await self._page.keyboard.up(key)
                
            elif action_type == "wait":
                duration = params.get("duration", 1.0)
                await asyncio.sleep(duration)
                
            else:
                return ActionResult(
                    success=False,
                    action=action,
                    error=f"Unknown action type: {action_type}",
                    execution_time_ms=(time.time() - start_time) * 1000,
                )
            
            # Wait for any navigation or loading
            await self._page.wait_for_load_state("networkidle", timeout=5000)
            
            # Capture screenshot after action
            screenshot = await self._capture_screenshot()
            url = self._page.url
            title = await self._page.title()
            
            return ActionResult(
                success=True,
                action=action,
                screenshot=screenshot,
                execution_time_ms=(time.time() - start_time) * 1000,
                url=url,
                title=title,
            )
            
        except Exception as e:
            logger.error(f"Error executing action {action.action_type}: {e}")
            return ActionResult(
                success=False,
                action=action,
                error=str(e),
                execution_time_ms=(time.time() - start_time) * 1000,
            )
    
    async def _is_task_complete(self, task: str) -> bool:
        """Check if the task appears to be complete."""
        # Simple heuristic: check if we've had several successful actions without changes
        if len(self._action_history) < 3:
            return False
        
        # Check recent actions for completion indicators
        recent = self._action_history[-3:]
        if all(r.success for r in recent):
            # Could add more sophisticated completion detection here
            pass
        
        return False
    
    async def click_element(self, selector: str) -> bool:
        """Click an element by CSS selector."""
        if not self._page:
            return False
        try:
            await self._page.click(selector)
            return True
        except Exception as e:
            logger.error(f"Error clicking element {selector}: {e}")
            return False
    
    async def type_text(self, selector: str, text: str) -> bool:
        """Type text into an element."""
        if not self._page:
            return False
        try:
            await self._page.fill(selector, text)
            return True
        except Exception as e:
            logger.error(f"Error typing into {selector}: {e}")
            return False
    
    async def get_element_text(self, selector: str) -> Optional[str]:
        """Get text content of an element."""
        if not self._page:
            return None
        try:
            element = await self._page.query_selector(selector)
            if element:
                return await element.text_content()
            return None
        except Exception as e:
            logger.error(f"Error getting text from {selector}: {e}")
            return None


# Singleton instance
_computer_use_agent: Optional[ComputerUseAgent] = None


def get_computer_use_agent(llm_client: openai.AsyncOpenAI = None) -> Optional[ComputerUseAgent]:
    """Get or create the Computer Use Agent singleton."""
    global _computer_use_agent
    if _computer_use_agent is None and llm_client:
        _computer_use_agent = ComputerUseAgent(llm_client)
    return _computer_use_agent


async def shutdown_computer_use_agent():
    """Shutdown the Computer Use Agent."""
    global _computer_use_agent
    if _computer_use_agent:
        await _computer_use_agent.shutdown()
        _computer_use_agent = None
