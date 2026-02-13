"""
Base Agent — Foundation for all agents in the McLeuker Agentic AI system.
=========================================================================

Provides:
- Unified LLM interface (Kimi 2.5 / Grok with automatic fallback)
- Event emission for real-time streaming
- Message history management
- Tool call parsing
"""

import asyncio
import json
import os
import time
from typing import Dict, List, Any, Optional, Callable, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)


# ============================================================================
# DATA MODELS
# ============================================================================

class AgentStatus(Enum):
    IDLE = "idle"
    PLANNING = "planning"
    EXECUTING = "executing"
    OBSERVING = "observing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class AgentEvent:
    """Event emitted by an agent during execution."""
    type: str
    data: Dict[str, Any]
    timestamp: str = ""

    def __post_init__(self):
        if not self.timestamp:
            self.timestamp = datetime.now().isoformat()

    def to_dict(self) -> Dict:
        return {"type": self.type, "data": self.data, "timestamp": self.timestamp}


@dataclass
class ToolCall:
    """A tool call from the LLM."""
    id: str
    name: str
    arguments: Dict[str, Any]


@dataclass
class ToolResult:
    """Result from executing a tool."""
    tool_call_id: str
    name: str
    output: Any
    error: Optional[str] = None
    screenshot: Optional[str] = None  # base64 JPEG
    execution_time_ms: float = 0


# ============================================================================
# BASE AGENT
# ============================================================================

class BaseAgent:
    """
    Base class for all agents. Provides LLM calling, event emission,
    and message history management.
    """

    def __init__(
        self,
        name: str,
        system_prompt: str,
        llm_client=None,
        model: str = "kimi-k2.5",
        fallback_model: str = "grok-4-1-fast-reasoning",
    ):
        self.name = name
        self.system_prompt = system_prompt
        self.llm_client = llm_client
        self.model = model
        self.fallback_model = fallback_model
        self.status = AgentStatus.IDLE
        self.messages: List[Dict[str, Any]] = []
        self.event_callbacks: List[Callable] = []

        # Fallback LLM client (Grok)
        self._fallback_client = None
        grok_key = os.getenv("GROK_API_KEY")
        if grok_key:
            import openai
            self._fallback_client = openai.AsyncOpenAI(
                api_key=grok_key,
                base_url="https://api.x.ai/v1"
            )

    def add_message(self, role: str, content: str, **kwargs):
        """Add a message to conversation history."""
        msg = {"role": role, "content": content}
        msg.update(kwargs)
        self.messages.append(msg)

    def get_messages_for_llm(self) -> List[Dict]:
        """Get messages formatted for LLM API call."""
        msgs = [{"role": "system", "content": self.system_prompt}]
        msgs.extend(self.messages)
        return msgs

    def clear_messages(self):
        """Clear conversation history."""
        self.messages = []

    async def emit_event(self, event_type: str, data: Dict):
        """Emit an event to all registered callbacks."""
        for cb in self.event_callbacks:
            try:
                if asyncio.iscoroutinefunction(cb):
                    await cb(event_type, data)
                else:
                    cb(event_type, data)
            except Exception as e:
                logger.error(f"Event callback error: {e}")

    def on_event(self, callback: Callable):
        """Register an event callback."""
        self.event_callbacks.append(callback)

    async def call_llm(
        self,
        messages: List[Dict],
        tools: Optional[List[Dict]] = None,
        stream: bool = False,
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> Dict:
        """
        Call the LLM with automatic fallback.
        Returns the full API response dict.
        """
        # Try primary model first
        for attempt, (client, model) in enumerate([
            (self.llm_client, self.model),
            (self._fallback_client, self.fallback_model),
        ]):
            if client is None:
                continue
            try:
                kwargs = {
                    "model": model,
                    "messages": messages,
                    "temperature": 1.0 if "kimi" in model else temperature,
                    "max_tokens": max_tokens,
                }
                if tools:
                    kwargs["tools"] = tools
                    kwargs["tool_choice"] = "auto"

                response = await client.chat.completions.create(**kwargs)
                return response.model_dump()

            except Exception as e:
                logger.warning(f"LLM call failed ({model}): {e}")
                if attempt == 0:
                    logger.info(f"Falling back to {self.fallback_model}")
                    continue
                raise

        raise RuntimeError("All LLM clients failed")

    async def call_llm_stream(
        self,
        messages: List[Dict],
        temperature: float = 0.7,
        max_tokens: int = 4096,
    ) -> AsyncGenerator[str, None]:
        """Stream LLM response token by token."""
        for client, model in [
            (self.llm_client, self.model),
            (self._fallback_client, self.fallback_model),
        ]:
            if client is None:
                continue
            try:
                response = await client.chat.completions.create(
                    model=model,
                    messages=messages,
                    temperature=1.0 if "kimi" in model else temperature,
                    max_tokens=max_tokens,
                    stream=True,
                )
                async for chunk in response:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield delta.content
                return
            except Exception as e:
                logger.warning(f"Stream failed ({model}): {e}")
                continue

    async def run(self, user_input: str, context: Optional[Dict] = None) -> AsyncGenerator[AgentEvent, None]:
        """Override in subclasses to implement agent logic."""
        raise NotImplementedError
