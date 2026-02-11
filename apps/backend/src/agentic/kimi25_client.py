"""
Kimi 2.5 Complete Client with All Native Capabilities
======================================================

Adapted for McLeuker AI's 3-toggle architecture (instant/thinking/agent).
Provides a unified interface to Kimi 2.5's operational modes:
- Instant Mode: Fast responses without reasoning traces
- Thinking Mode: Step-by-step analysis with visible reasoning
- Agent Mode: Autonomous workflows with tool calls + swarm coordination

Additional capabilities:
- Vision-to-Code: Generate working code from UI mockups/screenshots
- 256K Context: Process entire documents in a single pass
- Multimodal: Native understanding of text, images, and video
"""

import openai
import os
import json
import base64
import asyncio
import functools
from typing import List, Dict, Any, Optional, Literal, AsyncGenerator, Union
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class KimiModeType(Enum):
    """Kimi 2.5 operational modes - mapped to McLeuker's 3 toggles"""
    INSTANT = "instant"      # Auto/Instant toggle
    THINKING = "thinking"    # Thinking toggle
    AGENT = "agent"          # Agent toggle (includes swarm capabilities)


@dataclass
class KimiMode:
    """Configuration for Kimi 2.5 operational mode"""
    type: KimiModeType = KimiModeType.THINKING
    thinking_budget: Optional[int] = None  # 8K, 32K, or 96K for thinking mode
    temperature: float = 1.0  # Kimi requires temperature=1
    top_p: float = 0.95
    max_tokens: Optional[int] = None
    tools: Optional[List[Dict]] = None
    stream: bool = False


@dataclass
class KimiResponse:
    """Structured response from Kimi 2.5"""
    content: str
    reasoning_content: Optional[str] = None
    tool_calls: Optional[List[Dict]] = None
    usage: Optional[Dict] = None
    mode: KimiModeType = KimiModeType.THINKING
    latency_ms: Optional[float] = None
    finish_reason: Optional[str] = None


@dataclass
class SwarmTask:
    """Individual task in an Agent Swarm"""
    task_id: str
    specialty: str
    instruction: str
    tools: List[str] = field(default_factory=list)
    expected_output: str = ""
    dependencies: List[str] = field(default_factory=list)
    status: str = "pending"
    result: Optional[str] = None
    agent_id: Optional[str] = None


@dataclass
class SwarmPlan:
    """Execution plan for Agent Swarm"""
    main_objective: str
    sub_tasks: List[SwarmTask]
    parallel_groups: List[List[str]]
    estimated_steps: int
    reasoning: str


class Kimi25Client:
    """
    Complete Kimi 2.5 client adapted for McLeuker AI.

    Uses the sync OpenAI client (matching main.py pattern) with run_in_executor
    for async compatibility. Supports all Kimi 2.5 capabilities.

    Modes mapped to McLeuker toggles:
    - instant → Fast responses, no reasoning trace
    - thinking → Reasoning traces with configurable budget
    - agent → Tool calls + swarm coordination
    """

    MODEL = "kimi-k2.5"
    API_BASE = "https://api.moonshot.ai/v1"

    THINKING_BUDGETS = {
        "standard": 8000,
        "complex": 32000,
        "frontier": 96000,
    }

    def __init__(self, api_key: Optional[str] = None, client: Optional[openai.OpenAI] = None):
        """
        Initialize Kimi 2.5 client.

        Args:
            api_key: Moonshot API key. Falls back to KIMI_API_KEY env var.
            client: Optional pre-existing sync OpenAI client (reuse from main.py).
        """
        if client:
            self.client = client
        else:
            self.api_key = api_key or os.getenv("KIMI_API_KEY", "")
            if not self.api_key:
                logger.warning("Kimi API key not set – Kimi25Client will be non-functional")
                self.client = None
                return
            self.client = openai.OpenAI(api_key=self.api_key, base_url=self.API_BASE)

        logger.info("Kimi 2.5 client initialized")

    # ------------------------------------------------------------------
    # Core chat
    # ------------------------------------------------------------------

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        mode: Optional[KimiMode] = None,
        stream: bool = False,
    ) -> Union[KimiResponse, AsyncGenerator[str, None]]:
        """Unified chat interface with all Kimi 2.5 capabilities."""
        if not self.client:
            return KimiResponse(content="Kimi client not available", mode=KimiModeType.INSTANT)

        mode = mode or KimiMode(type=KimiModeType.THINKING)
        start_time = datetime.now()

        params = self._build_request_params(messages, mode)
        params["stream"] = stream

        try:
            if stream:
                return self._stream_response(params, mode, start_time)
            else:
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None, functools.partial(self.client.chat.completions.create, **params)
                )
                return self._parse_response(response, mode, start_time)
        except Exception as e:
            logger.error(f"Kimi API error: {e}")
            return KimiResponse(
                content=f"Kimi API error: {str(e)}",
                mode=mode.type,
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )

    def _build_request_params(self, messages: List[Dict[str, Any]], mode: KimiMode) -> Dict[str, Any]:
        """Build API request parameters based on mode."""
        params: Dict[str, Any] = {
            "model": self.MODEL,
            "messages": messages,
            "temperature": 1,  # Kimi requires temperature=1
            "top_p": mode.top_p,
        }

        if mode.max_tokens:
            params["max_tokens"] = mode.max_tokens
        else:
            params["max_tokens"] = 16384

        if mode.type == KimiModeType.INSTANT:
            # No reasoning trace, faster
            pass
        elif mode.type == KimiModeType.THINKING:
            # Reasoning traces enabled
            pass
        elif mode.type == KimiModeType.AGENT:
            # Enable tools
            if mode.tools:
                params["tools"] = mode.tools
                params["tool_choice"] = "auto"
            else:
                # Default Kimi built-in tools
                params["tools"] = [
                    {"type": "builtin_function", "function": {"name": "$web_search"}},
                    {"type": "builtin_function", "function": {"name": "moonshot/fetch:latest"}},
                ]

        return params

    def _parse_response(self, response: Any, mode: KimiMode, start_time: datetime) -> KimiResponse:
        """Parse API response into structured format."""
        latency = (datetime.now() - start_time).total_seconds() * 1000
        message = response.choices[0].message

        return KimiResponse(
            content=message.content or "",
            reasoning_content=getattr(message, "reasoning_content", None),
            tool_calls=[tc.model_dump() if hasattr(tc, "model_dump") else vars(tc) for tc in (message.tool_calls or [])] if message.tool_calls else None,
            usage={
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            } if response.usage else None,
            mode=mode.type,
            latency_ms=latency,
            finish_reason=response.choices[0].finish_reason,
        )

    async def _stream_response(self, params: Dict[str, Any], mode: KimiMode, start_time: datetime) -> AsyncGenerator[str, None]:
        """Stream response from Kimi API."""
        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, functools.partial(self.client.chat.completions.create, **params)
            )

            for chunk in response:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta
                    if delta.content:
                        yield json.dumps({"type": "content", "data": delta.content})
                    if getattr(delta, "reasoning_content", None):
                        yield json.dumps({"type": "reasoning", "data": delta.reasoning_content})
                    if getattr(delta, "tool_calls", None):
                        yield json.dumps({"type": "tool_calls", "data": str(delta.tool_calls)})

            latency = (datetime.now() - start_time).total_seconds() * 1000
            yield json.dumps({"type": "done", "latency_ms": latency})

        except Exception as e:
            logger.error(f"Kimi streaming error: {e}")
            yield json.dumps({"type": "error", "error": str(e)})

    # ------------------------------------------------------------------
    # Agent Swarm
    # ------------------------------------------------------------------

    async def agent_swarm(
        self,
        task: str,
        max_agents: int = 20,
        context: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
    ) -> SwarmPlan:
        """Execute Agent Swarm to decompose and plan parallel task execution."""

        system_prompt = f"""You are an Agent Swarm orchestrator for Kimi K2.5.

Your task is to decompose complex requests into parallel sub-tasks that can be executed by up to {max_agents} specialized sub-agents simultaneously.

For each sub-task, specify:
1. task_id: Unique identifier (e.g., "task_1", "task_2")
2. specialty: Agent specialty (researcher, coder, analyst, writer, verifier, etc.)
3. instruction: Specific, actionable instruction
4. tools: List of required tools from available options
5. expected_output: Expected format and content of output
6. dependencies: List of task_ids that must complete before this task (empty if parallelizable)

Also identify parallel_groups: groups of task_ids that can execute simultaneously.

Respond in JSON format:
{{
    "main_objective": "brief description",
    "reasoning": "explanation of decomposition strategy",
    "estimated_steps": number,
    "sub_tasks": [
        {{
            "task_id": "task_1",
            "specialty": "researcher",
            "instruction": "specific instruction",
            "tools": ["web_search", "browser"],
            "expected_output": "format description",
            "dependencies": []
        }}
    ],
    "parallel_groups": [["task_1", "task_2"], ["task_3"]]
}}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Task: {task}\n\nContext: {context or 'None'}"},
        ]

        response = await self.chat(
            messages=messages,
            mode=KimiMode(type=KimiModeType.THINKING, thinking_budget=self.THINKING_BUDGETS["complex"]),
        )

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            plan_data = json.loads(content.strip())

            sub_tasks = []
            for td in plan_data.get("sub_tasks", []):
                sub_tasks.append(SwarmTask(
                    task_id=td.get("task_id", "task_0"),
                    specialty=td.get("specialty", "general"),
                    instruction=td.get("instruction", ""),
                    tools=td.get("tools", []),
                    expected_output=td.get("expected_output", ""),
                    dependencies=td.get("dependencies", []),
                ))

            return SwarmPlan(
                main_objective=plan_data.get("main_objective", task),
                sub_tasks=sub_tasks,
                parallel_groups=plan_data.get("parallel_groups", []),
                estimated_steps=plan_data.get("estimated_steps", len(sub_tasks)),
                reasoning=plan_data.get("reasoning", response.reasoning_content or ""),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse swarm plan: {e}")
            return SwarmPlan(
                main_objective=task,
                sub_tasks=[SwarmTask(task_id="task_1", specialty="general", instruction=task, tools=["web_search"], expected_output="Complete response")],
                parallel_groups=[["task_1"]],
                estimated_steps=1,
                reasoning=response.reasoning_content or "Fallback plan due to parsing error",
            )

    # ------------------------------------------------------------------
    # Vision-to-Code
    # ------------------------------------------------------------------

    async def vision_to_code(
        self,
        image_data: Union[str, bytes],
        requirements: str = "",
        framework: str = "react",
    ) -> Dict[str, Any]:
        """Generate complete code from UI mockups or screenshots."""
        if isinstance(image_data, bytes):
            image_url = f"data:image/png;base64,{base64.b64encode(image_data).decode()}"
        elif image_data.startswith("http") or image_data.startswith("data:"):
            image_url = image_data
        else:
            image_url = f"data:image/png;base64,{image_data}"

        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": image_url}},
                    {
                        "type": "text",
                        "text": f"""Generate complete, production-ready {framework} code based on this design.
Requirements: {requirements}
Provide your response in JSON format:
{{
    "code": "complete component code here",
    "file_structure": ["list of files to create"],
    "dependencies": ["list of npm packages to install"],
    "explanation": "brief explanation of the implementation"
}}""",
                    },
                ],
            }
        ]

        response = await self.chat(
            messages=messages,
            mode=KimiMode(type=KimiModeType.THINKING, thinking_budget=self.THINKING_BUDGETS["complex"]),
        )

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            result = json.loads(content.strip())
            result["reasoning"] = response.reasoning_content
            return result
        except json.JSONDecodeError:
            return {
                "code": response.content,
                "file_structure": [],
                "dependencies": [],
                "explanation": "Raw code output (JSON parsing failed)",
                "reasoning": response.reasoning_content,
            }

    # ------------------------------------------------------------------
    # Long-context analysis
    # ------------------------------------------------------------------

    async def long_context_analysis(
        self,
        documents: List[str],
        analysis_type: str = "synthesis",
        instructions: str = "",
    ) -> Dict[str, Any]:
        """Utilize Kimi 2.5's 256K context window for full document analysis."""
        combined = "\n\n" + "=" * 80 + "\n\n".join(documents)
        max_input = 250000
        if len(combined) > max_input:
            combined = combined[:max_input] + "\n\n[Documents truncated due to length]"

        prompt = f"""Analyze the following {len(documents)} document(s).
Analysis Type: {analysis_type}
{instructions}

Documents:
{combined}

Provide a comprehensive analysis."""

        response = await self.chat(
            messages=[{"role": "user", "content": prompt}],
            mode=KimiMode(type=KimiModeType.THINKING, thinking_budget=self.THINKING_BUDGETS["complex"]),
        )

        return {
            "analysis": response.content,
            "reasoning": response.reasoning_content,
            "document_count": len(documents),
            "total_input_chars": len(combined),
            "usage": response.usage,
        }

    # ------------------------------------------------------------------
    # Multimodal
    # ------------------------------------------------------------------

    async def multimodal_chat(
        self,
        text: str,
        images: Optional[List[Union[str, bytes]]] = None,
        videos: Optional[List[Union[str, bytes]]] = None,
        mode: Optional[KimiMode] = None,
    ) -> KimiResponse:
        """Chat with multimodal inputs (text + images + videos)."""
        content: List[Dict[str, Any]] = []

        if images:
            for img in images:
                if isinstance(img, bytes):
                    img_url = f"data:image/png;base64,{base64.b64encode(img).decode()}"
                elif img.startswith("http") or img.startswith("data:"):
                    img_url = img
                else:
                    img_url = f"data:image/png;base64,{img}"
                content.append({"type": "image_url", "image_url": {"url": img_url}})

        if videos:
            for vid in videos:
                if isinstance(vid, bytes):
                    vid_url = f"data:video/mp4;base64,{base64.b64encode(vid).decode()}"
                elif vid.startswith("http") or vid.startswith("data:"):
                    vid_url = vid
                else:
                    vid_url = f"data:video/mp4;base64,{vid}"
                content.append({"type": "video_url", "video_url": {"url": vid_url}})

        content.append({"type": "text", "text": text})

        messages = [{"role": "user", "content": content}]
        return await self.chat(messages=messages, mode=mode or KimiMode(type=KimiModeType.THINKING))

    # ------------------------------------------------------------------
    # Default tools
    # ------------------------------------------------------------------

    def get_default_tools(self) -> List[Dict]:
        """Get default tools for Agent mode."""
        return [
            {"type": "function", "function": {"name": "web_search", "description": "Search the web for current information", "parameters": {"type": "object", "properties": {"query": {"type": "string", "description": "Search query"}}, "required": ["query"]}}},
            {"type": "function", "function": {"name": "browser_navigate", "description": "Navigate to a URL and extract content", "parameters": {"type": "object", "properties": {"url": {"type": "string", "description": "URL to navigate to"}}, "required": ["url"]}}},
            {"type": "function", "function": {"name": "code_interpreter", "description": "Execute Python code", "parameters": {"type": "object", "properties": {"code": {"type": "string", "description": "Python code to execute"}}, "required": ["code"]}}},
            {"type": "function", "function": {"name": "file_read", "description": "Read content from a file", "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "File path"}}, "required": ["path"]}}},
            {"type": "function", "function": {"name": "file_write", "description": "Write content to a file", "parameters": {"type": "object", "properties": {"path": {"type": "string", "description": "File path"}, "content": {"type": "string", "description": "Content to write"}}, "required": ["path", "content"]}}},
        ]
