"""
Reasoning Agent V2 — Clarification Before Execution
=====================================================

This agent handles the reasoning phase BEFORE any execution.
It analyzes user requests and determines if clarification is needed.

Key principle: ALWAYS reason first, ask for missing info, then execute.

Uses:
- grok-4-1-fast-reasoning for reasoning (per architecture preference)
- Kimi K2.5 as fallback
- Fully async (openai.AsyncOpenAI)
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class ReasoningResult:
    """Result of reasoning phase"""
    can_proceed: bool
    needs_clarification: bool
    clarification_questions: List[str]
    task_analysis: str
    execution_plan: Optional[Dict]
    confidence: float  # 0.0 to 1.0
    reasoning_text: str = ""  # Raw reasoning for transparency


class ReasoningAgent:
    """
    Agent that reasons about user requests before execution.

    Flow:
    1. Analyze user request
    2. Identify missing information
    3. Ask clarification questions if needed
    4. Create execution plan if ready

    Supports dual-model with fallback:
    - Primary: grok-4-1-fast-reasoning (fast reasoning)
    - Fallback: kimi-k2.5 (vision + general)
    """

    def __init__(self, grok_client=None, kimi_client=None):
        """
        Args:
            grok_client: openai.AsyncOpenAI for Grok (primary reasoning)
            kimi_client: openai.AsyncOpenAI for Kimi (fallback + vision)
        """
        self.grok_client = grok_client
        self.kimi_client = kimi_client

    async def _call_llm(self, messages: List[Dict], max_tokens: int = 2000) -> str:
        """Call LLM with fallback: Grok → Kimi"""
        # Try Grok first (preferred for reasoning)
        if self.grok_client:
            try:
                response = await self.grok_client.chat.completions.create(
                    model="grok-4-1-fast-reasoning",
                    messages=messages,
                    temperature=0.7,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.warning(f"Grok reasoning failed, falling back to Kimi: {e}")

        # Fallback to Kimi
        if self.kimi_client:
            try:
                response = await self.kimi_client.chat.completions.create(
                    model="kimi-k2.5",
                    messages=messages,
                    temperature=1,  # kimi-k2.5 requires temperature=1
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content or ""
            except Exception as e:
                logger.error(f"Kimi reasoning also failed: {e}")
                raise

        raise RuntimeError("No LLM client available for reasoning")

    async def reason(
        self,
        user_request: str,
        conversation_history: Optional[List[Dict]] = None,
        mode: str = "agent",
    ) -> ReasoningResult:
        """
        Reason about the user request.

        Args:
            user_request: What the user wants
            conversation_history: Previous messages for context
            mode: Execution mode (instant, auto, agent)

        Returns:
            ReasoningResult with analysis and next steps
        """

        system_prompt = """You are a reasoning assistant that analyzes user requests before execution.

Your job is to:
1. Understand what the user wants to accomplish
2. Identify any missing information needed to complete the task
3. Determine if the request is clear enough to proceed
4. Create an execution plan if ready

IMPORTANT RULES:
- If the request is vague or missing critical details, ask for clarification
- If credentials, accounts, or personal info is needed but not provided, ask for it
- If the task scope is unclear, ask clarifying questions
- Only proceed to execution when you have ALL necessary information
- For web browsing tasks: you CAN navigate to websites, click, type, scroll, and take screenshots
- For login tasks: ask the user for credentials if not provided, then proceed
- Be practical — if the task is straightforward (e.g. "go to google.com"), just proceed

Available tools for execution:
- browser: Navigate websites, click, type, scroll, take screenshots, login to accounts
- search: Search the web for information across multiple engines
- code: Execute Python/JS code in a sandbox
- github: Read/write GitHub repositories
- think: Analyze and reason about information

Respond in JSON format:
{
    "can_proceed": true/false,
    "needs_clarification": true/false,
    "clarification_questions": ["question 1", "question 2"],
    "task_analysis": "Detailed analysis of what needs to be done",
    "reasoning": "Your step-by-step reasoning about this request",
    "execution_plan": {
        "steps": [
            {"step": 1, "action": "description", "tool": "browser/search/code/github/think", "url": "optional", "query": "optional"}
        ]
    },
    "confidence": 0.8
}"""

        messages = [{"role": "system", "content": system_prompt}]

        # Add conversation history for context
        if conversation_history:
            for msg in conversation_history[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                if content:
                    messages.append({"role": role, "content": content})

        user_content = f"""Analyze this request and determine if we can proceed:

USER REQUEST: "{user_request}"

MODE: {mode}

Think carefully:
1. What exactly does the user want?
2. What information is missing?
3. Can we execute this without more details?
4. What tools do we need?
5. What is the step-by-step plan?

Provide your analysis in JSON format."""

        messages.append({"role": "user", "content": user_content})

        try:
            content = await self._call_llm(messages, max_tokens=2000)
            result = self._parse_reasoning_response(content)
            logger.info(
                f"Reasoning complete — can_proceed: {result.can_proceed}, "
                f"needs_clarification: {result.needs_clarification}, "
                f"confidence: {result.confidence}"
            )
            return result

        except Exception as e:
            logger.error(f"Reasoning failed: {e}")
            return ReasoningResult(
                can_proceed=False,
                needs_clarification=True,
                clarification_questions=[
                    "I need to understand your request better. Could you provide more details?"
                ],
                task_analysis=f"Failed to analyze request: {str(e)}",
                execution_plan=None,
                confidence=0.0,
                reasoning_text=f"Error: {str(e)}",
            )

    def _parse_reasoning_response(self, content: str) -> ReasoningResult:
        """Parse LLM reasoning response"""
        try:
            # Extract JSON from response
            json_str = content.strip()
            if "```json" in content:
                json_str = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                json_str = content.split("```")[1].split("```")[0].strip()
            else:
                # Try to find JSON object in text
                start = content.find("{")
                end = content.rfind("}")
                if start != -1 and end != -1:
                    json_str = content[start : end + 1]

            data = json.loads(json_str)

            return ReasoningResult(
                can_proceed=data.get("can_proceed", False),
                needs_clarification=data.get("needs_clarification", True),
                clarification_questions=data.get("clarification_questions", []),
                task_analysis=data.get("task_analysis", ""),
                execution_plan=data.get("execution_plan"),
                confidence=data.get("confidence", 0.0),
                reasoning_text=data.get("reasoning", ""),
            )

        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse reasoning JSON: {e}")
            return ReasoningResult(
                can_proceed=False,
                needs_clarification=True,
                clarification_questions=[
                    "I had trouble understanding your request. Could you rephrase or provide more details?"
                ],
                task_analysis="Parsing error — need clarification",
                execution_plan=None,
                confidence=0.0,
                reasoning_text=content,  # Keep raw text for debugging
            )

    async def clarify(
        self,
        original_request: str,
        clarification_answers: Dict[str, str],
        conversation_history: Optional[List[Dict]] = None,
    ) -> ReasoningResult:
        """
        Process clarification answers and re-evaluate.

        Args:
            original_request: Original user request
            clarification_answers: User's answers to clarification questions
            conversation_history: Previous messages

        Returns:
            Updated ReasoningResult
        """
        context = f"""Original request: {original_request}

Clarifications provided:
"""
        for question, answer in clarification_answers.items():
            context += f"\nQ: {question}\nA: {answer}"

        return await self.reason(context, conversation_history)


class ModeRouter:
    """
    Routes requests to appropriate mode based on complexity.

    Modes:
    - instant: Quick responses, no reasoning
    - auto: Light reasoning, automatic execution
    - agent: Full reasoning, clarification if needed
    """

    def __init__(self, grok_client=None, kimi_client=None):
        self.reasoning_agent = ReasoningAgent(grok_client, kimi_client)

    async def route(
        self,
        user_request: str,
        mode: str = "auto",
        conversation_history: Optional[List[Dict]] = None,
    ) -> Dict[str, Any]:
        """Route request to appropriate handler."""

        # INSTANT MODE: Skip reasoning, direct response
        if mode == "instant":
            return {
                "mode": "instant",
                "should_reason": False,
                "should_execute": False,
                "direct_response": True,
                "message": "Provide direct answer without execution",
            }

        # AUTO MODE: Light reasoning, auto-execute if confident
        if mode == "auto":
            reasoning = await self.reasoning_agent.reason(
                user_request, conversation_history, mode="auto"
            )

            if reasoning.can_proceed and reasoning.confidence > 0.8:
                return {
                    "mode": "auto",
                    "should_reason": True,
                    "should_execute": True,
                    "needs_clarification": False,
                    "execution_plan": reasoning.execution_plan,
                    "confidence": reasoning.confidence,
                    "reasoning": reasoning.reasoning_text,
                }
            else:
                return {
                    "mode": "agent",
                    "should_reason": True,
                    "should_execute": False,
                    "needs_clarification": True,
                    "clarification_questions": reasoning.clarification_questions,
                    "confidence": reasoning.confidence,
                    "reasoning": reasoning.reasoning_text,
                }

        # AGENT MODE: Full reasoning with clarification
        reasoning = await self.reasoning_agent.reason(
            user_request, conversation_history, mode="agent"
        )

        return {
            "mode": "agent",
            "should_reason": True,
            "should_execute": reasoning.can_proceed,
            "needs_clarification": reasoning.needs_clarification,
            "clarification_questions": reasoning.clarification_questions,
            "execution_plan": reasoning.execution_plan,
            "task_analysis": reasoning.task_analysis,
            "confidence": reasoning.confidence,
            "reasoning": reasoning.reasoning_text,
        }
