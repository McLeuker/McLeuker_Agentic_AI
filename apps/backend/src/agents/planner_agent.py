"""
Planner Agent — Task Decomposition and Planning
=================================================

Decomposes user requests into executable steps.
Each step has a tool, instruction, and expected output.
Uses Kimi 2.5 / Grok for intelligent planning.
"""

import json
import re
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from .base_agent import BaseAgent, AgentEvent
import logging

logger = logging.getLogger(__name__)


@dataclass
class ExecutionStep:
    """A single step in the execution plan."""
    id: int
    tool: str  # browser, code, search, github, think, file
    instruction: str
    expected_output: str = ""
    depends_on: List[int] = field(default_factory=list)
    status: str = "pending"
    result: Optional[Dict] = None


@dataclass
class ExecutionPlan:
    """Complete execution plan."""
    goal: str
    steps: List[ExecutionStep]
    reasoning: str = ""


PLANNER_SYSTEM_PROMPT = """You are a task planning agent. Your job is to decompose user requests into clear, executable steps.

Available tools:
- **browser**: Navigate websites, click elements, type text, read content, take screenshots. Use for any web interaction.
- **code**: Execute Python code in a sandbox. Use for calculations, data processing, file generation.
- **search**: Search the web for information. Use for research and fact-finding.
- **github**: Read/write files, create branches, make PRs on GitHub repositories.
- **think**: Analyze information and reason about findings. Use between action steps.
- **file**: Generate files (PDF, Excel, Word, etc.)

Rules:
1. Break complex tasks into 3-8 atomic steps
2. Each step should use exactly ONE tool
3. Steps should be ordered logically
4. Include browser steps for ANY web interaction (login, form filling, reading pages)
5. Always end with a think step to summarize results
6. Be specific in instructions — include URLs, selectors, exact actions

Respond with a JSON object:
{
  "goal": "One-sentence summary of the task",
  "reasoning": "Brief explanation of your approach",
  "steps": [
    {
      "id": 1,
      "tool": "browser",
      "instruction": "Navigate to https://example.com and read the main content",
      "expected_output": "Page content extracted",
      "depends_on": []
    }
  ]
}
"""


class PlannerAgent(BaseAgent):
    """Plans task execution by decomposing requests into steps."""

    def __init__(self, llm_client=None, **kwargs):
        super().__init__(
            name="planner",
            system_prompt=PLANNER_SYSTEM_PROMPT,
            llm_client=llm_client,
            **kwargs
        )

    async def create_plan(self, user_request: str, context: Optional[Dict] = None) -> ExecutionPlan:
        """Create an execution plan from a user request."""
        messages = self.get_messages_for_llm()

        # Add context if available
        context_str = ""
        if context:
            if context.get("conversation_history"):
                context_str += f"\nConversation context: {context['conversation_history'][-3:]}"
            if context.get("available_tools"):
                context_str += f"\nAvailable tools: {', '.join(context['available_tools'])}"

        messages.append({
            "role": "user",
            "content": f"Create an execution plan for this request:\n\n{user_request}{context_str}\n\nRespond with JSON only."
        })

        try:
            response = await self.call_llm(messages, temperature=0.3, max_tokens=2048)
            content = response["choices"][0]["message"]["content"]

            # Parse JSON from response
            plan_data = self._parse_plan_json(content)

            steps = []
            for s in plan_data.get("steps", []):
                steps.append(ExecutionStep(
                    id=s.get("id", len(steps) + 1),
                    tool=s.get("tool", "think"),
                    instruction=s.get("instruction", ""),
                    expected_output=s.get("expected_output", ""),
                    depends_on=s.get("depends_on", []),
                ))

            plan = ExecutionPlan(
                goal=plan_data.get("goal", user_request[:100]),
                steps=steps,
                reasoning=plan_data.get("reasoning", ""),
            )

            logger.info(f"Plan created: {len(plan.steps)} steps for: {plan.goal}")
            return plan

        except Exception as e:
            logger.error(f"Planning failed: {e}")
            # Fallback: single think step
            return ExecutionPlan(
                goal=user_request[:100],
                steps=[
                    ExecutionStep(id=1, tool="think", instruction=user_request),
                ],
                reasoning=f"Planning failed ({e}), falling back to direct reasoning",
            )

    def _parse_plan_json(self, content: str) -> Dict:
        """Parse JSON from LLM response, handling markdown fences."""
        # Remove markdown code fences
        content = content.strip()
        if content.startswith("```"):
            content = re.sub(r"^```(?:json)?\s*\n?", "", content)
            content = re.sub(r"\n?```\s*$", "", content)

        try:
            return json.loads(content)
        except json.JSONDecodeError:
            # Try to find JSON object in the text
            match = re.search(r'\{[\s\S]*\}', content)
            if match:
                try:
                    return json.loads(match.group())
                except:
                    pass
            raise ValueError(f"Could not parse plan JSON from: {content[:200]}")
