"""
Reflection Engine — Self-Correction and Quality Assurance
==========================================================

After each step, reflects on the result to:
- Validate output quality
- Detect errors or hallucinations
- Decide whether to retry, revise plan, or continue
- Learn from failures for future steps
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ReflectionAction(Enum):
    CONTINUE = "continue"
    RETRY = "retry"
    REVISE_PLAN = "revise_plan"
    SKIP = "skip"
    ABORT = "abort"


@dataclass
class ReflectionResult:
    step_id: str
    action: ReflectionAction
    reflection: str
    confidence: float = 0.0
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    suggested_action: str = ""
    restart_from_step: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "step_id": self.step_id,
            "action": self.action.value,
            "reflection": self.reflection,
            "confidence": self.confidence,
            "issues": self.issues,
            "suggestions": self.suggestions,
        }


class ReflectionEngine:
    """
    Reflects on execution results to ensure quality and correctness.

    Uses grok-4-1-fast-reasoning for fast, accurate reflection.
    """

    REFLECTION_PROMPT = """You are a quality assurance expert for an AI agent system.

Evaluate the execution result of a step and decide the next action.

Respond in JSON format:
{
    "action": "continue|retry|revise_plan|skip|abort",
    "reflection": "your analysis of the result",
    "confidence": 0.0-1.0,
    "issues": ["issue1", "issue2"],
    "suggestions": ["suggestion1"],
    "restart_from_step": null or "step_id"
}

Actions:
- continue: Result is good, proceed to next step
- retry: Result has minor issues, retry the same step
- revise_plan: Major issue detected, need to revise the plan
- skip: Step is not needed, skip it
- abort: Critical failure, abort execution"""

    def __init__(self, grok_client, config):
        """
        Initialize reflection engine.

        Args:
            grok_client: Async OpenAI client for grok
            config: AgenticConfig
        """
        self.grok_client = grok_client
        self.config = config
        self._reflection_history: List[ReflectionResult] = []

    async def reflect(
        self,
        step_id: str,
        step_description: str,
        result: Any,
        objective: str,
        context: Optional[Dict[str, Any]] = None,
    ) -> ReflectionResult:
        """
        Reflect on a step's execution result.

        Args:
            step_id: The step that was executed
            step_description: What the step was supposed to do
            result: The execution result
            objective: The overall objective
            context: Additional context

        Returns:
            ReflectionResult with action recommendation
        """
        result_str = str(result)[:4000] if result else "No output"

        messages = [
            {"role": "system", "content": self.REFLECTION_PROMPT},
            {"role": "user", "content": f"""Evaluate this execution result:

OVERALL OBJECTIVE: {objective}

STEP: {step_id} — {step_description}

RESULT:
{result_str}

Was this step successful? What should we do next?"""}
        ]

        try:
            response = await self.grok_client.chat.completions.create(
                model=self.config.reasoning_model,
                messages=messages,
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

            content = response.choices[0].message.content
            data = json.loads(content)

            action_str = data.get("action", "continue")
            try:
                action = ReflectionAction(action_str)
            except ValueError:
                action = ReflectionAction.CONTINUE

            reflection = ReflectionResult(
                step_id=step_id,
                action=action,
                reflection=data.get("reflection", ""),
                confidence=data.get("confidence", 0.8),
                issues=data.get("issues", []),
                suggestions=data.get("suggestions", []),
                suggested_action=action_str,
                restart_from_step=data.get("restart_from_step"),
            )

            self._reflection_history.append(reflection)
            return reflection

        except Exception as e:
            logger.exception(f"Reflection failed for step {step_id}: {e}")
            # Default: continue
            return ReflectionResult(
                step_id=step_id,
                action=ReflectionAction.CONTINUE,
                reflection=f"Reflection failed: {e}. Continuing by default.",
                confidence=0.5,
            )

    async def reflect_on_plan(
        self,
        objective: str,
        all_results: Dict[str, Any],
    ) -> ReflectionResult:
        """
        Reflect on the entire execution — final quality check.

        Args:
            objective: The original objective
            all_results: All step results

        Returns:
            ReflectionResult for the overall execution
        """
        results_summary = []
        for step_id, result in all_results.items():
            results_summary.append(f"[{step_id}]: {str(result)[:500]}")

        messages = [
            {"role": "system", "content": """You are a final quality reviewer. Evaluate whether the overall execution
achieved the objective. Check for completeness, accuracy, and quality.

Respond in JSON:
{
    "action": "continue|revise_plan",
    "reflection": "overall assessment",
    "confidence": 0.0-1.0,
    "issues": [],
    "suggestions": []
}"""},
            {"role": "user", "content": f"""Final review:

OBJECTIVE: {objective}

ALL RESULTS:
{chr(10).join(results_summary)}

Did we achieve the objective? Is the quality sufficient?"""}
        ]

        try:
            response = await self.grok_client.chat.completions.create(
                model=self.config.reasoning_model,
                messages=messages,
                temperature=0.3,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

            data = json.loads(response.choices[0].message.content)

            action_str = data.get("action", "continue")
            try:
                action = ReflectionAction(action_str)
            except ValueError:
                action = ReflectionAction.CONTINUE

            return ReflectionResult(
                step_id="final_review",
                action=action,
                reflection=data.get("reflection", ""),
                confidence=data.get("confidence", 0.8),
                issues=data.get("issues", []),
                suggestions=data.get("suggestions", []),
            )

        except Exception as e:
            logger.exception(f"Final reflection failed: {e}")
            return ReflectionResult(
                step_id="final_review",
                action=ReflectionAction.CONTINUE,
                reflection=f"Final reflection failed: {e}",
                confidence=0.5,
            )

    def get_history(self) -> List[Dict[str, Any]]:
        """Get reflection history."""
        return [r.to_dict() for r in self._reflection_history]

    def clear_history(self):
        """Clear reflection history."""
        self._reflection_history.clear()
