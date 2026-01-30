"""
McLeuker Agentic AI Platform - Layer 1: Task Interpretation Layer

This layer converts a raw user prompt into a structured, machine-readable task plan.
It is the first step in the agent pipeline and produces a deterministic JSON contract
for all downstream layers.
"""

import json
from typing import Optional, Dict, Any
from src.models.schemas import (
    TaskInterpretation,
    DomainType,
    OutputFormat,
    ResearchDepth,
    ConfidenceLevel,
    ExecutionStep
)
from src.utils.llm_provider import LLMProvider, LLMFactory


# OpenAI Function Schema for Task Interpretation
INTERPRET_TASK_FUNCTION = {
    "name": "interpret_task",
    "description": "Interpret a user request and convert it into a structured task plan for an agentic AI system.",
    "parameters": {
        "type": "object",
        "properties": {
            "intent": {
                "type": "string",
                "description": "Clear description of what the user wants to achieve."
            },
            "domains": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [d.value for d in DomainType]
                },
                "description": "Primary and secondary domains involved in the request."
            },
            "requires_real_time_research": {
                "type": "boolean",
                "description": "Whether up-to-date external information is required."
            },
            "research_depth": {
                "type": "string",
                "enum": [r.value for r in ResearchDepth],
                "description": "Expected depth of research if required."
            },
            "geography": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Relevant regions or markets if mentioned or implied."
            },
            "time_horizon": {
                "type": "string",
                "description": "Timeframe referenced (e.g., SS26, 2025, next 6 months), if any."
            },
            "outputs": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [o.value for o in OutputFormat]
                },
                "description": "Requested output formats."
            },
            "execution_plan": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [e.value for e in ExecutionStep]
                },
                "description": "Ordered list of execution steps."
            },
            "confidence_level": {
                "type": "string",
                "enum": [c.value for c in ConfidenceLevel],
                "description": "How confident the system is about interpreting the request correctly."
            },
            "assumptions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Explicit assumptions made if the user request was ambiguous."
            }
        },
        "required": [
            "intent",
            "domains",
            "requires_real_time_research",
            "research_depth",
            "outputs",
            "execution_plan",
            "confidence_level"
        ]
    }
}

# System prompt for the Task Interpretation Agent
TASK_INTERPRETATION_SYSTEM_PROMPT = """You are a Task Interpretation Agent inside an agentic AI platform.

Your sole responsibility is to transform a raw user request into a structured task plan.

Rules:
- Do NOT perform research.
- Do NOT generate final content.
- Do NOT explain your reasoning.
- Do NOT ask questions.
- Make reasonable assumptions if needed and list them explicitly.
- Always respond by calling the function interpret_task.
- Output must be deterministic, concise, and machine-readable.

Focus on:
- User intent: What does the user want to achieve?
- Domain detection: Which industry/domain(s) is this related to? (multi-domain allowed)
- Research necessity: Does this require real-time web research?
- Output formats: What deliverables does the user need? (Excel, PDF, PPT, etc.)
- Ordered execution steps: What sequence of steps should be taken?

Domain options: fashion, beauty, skincare, sustainability, fashion_tech, catwalks, culture, textile, lifestyle, business, technology, marketing, finance, healthcare, other

Output format options: excel, csv, pdf, word, ppt, web, dashboard, code, text, json

Research depth options: none, light, medium, deep

Execution step options: reasoning, web_research, data_structuring, analysis, excel_generation, pdf_generation, ppt_generation, web_generation, code_generation, quality_check

If the user doesn't specify output formats, infer the most appropriate ones based on the request.
If the user mentions "report", default to PDF.
If the user mentions "data", "list", or "table", default to Excel.
If the user mentions "presentation" or "deck", default to PPT.
If multiple outputs are implied, include all of them.

Always include 'reasoning' as the first step and 'quality_check' as the last step in the execution plan."""


class TaskInterpretationLayer:
    """
    Layer 1: Task Interpretation
    
    Converts a raw user prompt into a structured task plan that serves as
    the contract for all downstream layers.
    """
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """Initialize the Task Interpretation Layer."""
        self.llm = llm_provider or LLMFactory.get_default()
    
    async def interpret(self, user_prompt: str) -> TaskInterpretation:
        """
        Interpret a user prompt and return a structured task plan.
        
        Args:
            user_prompt: The raw user request/prompt
            
        Returns:
            TaskInterpretation: A structured task plan
        """
        messages = [
            {"role": "system", "content": TASK_INTERPRETATION_SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ]
        
        response = await self.llm.complete(
            messages=messages,
            functions=[INTERPRET_TASK_FUNCTION],
            function_call={"name": "interpret_task"},
            temperature=0.1
        )
        
        # Extract the function call arguments
        if "function_call" in response and response["function_call"]:
            arguments = response["function_call"]["arguments"]
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            
            # Validate and create TaskInterpretation
            return TaskInterpretation(**arguments)
        else:
            # Fallback: try to parse content as JSON
            content = response.get("content", "")
            if content:
                try:
                    data = json.loads(content)
                    return TaskInterpretation(**data)
                except json.JSONDecodeError:
                    pass
            
            # Return a default interpretation with low confidence
            return TaskInterpretation(
                intent=user_prompt,
                domains=[DomainType.OTHER],
                requires_real_time_research=True,
                research_depth=ResearchDepth.MEDIUM,
                outputs=[OutputFormat.TEXT],
                execution_plan=[ExecutionStep.REASONING, ExecutionStep.QUALITY_CHECK],
                confidence_level=ConfidenceLevel.LOW,
                assumptions=["Could not fully interpret the request"]
            )
    
    async def interpret_with_context(
        self,
        user_prompt: str,
        conversation_history: Optional[list] = None,
        domain_hint: Optional[DomainType] = None
    ) -> TaskInterpretation:
        """
        Interpret a user prompt with additional context.
        
        Args:
            user_prompt: The raw user request/prompt
            conversation_history: Previous messages in the conversation
            domain_hint: A hint about the domain from the UI
            
        Returns:
            TaskInterpretation: A structured task plan
        """
        # Build context-aware prompt
        context_parts = []
        
        if domain_hint:
            context_parts.append(f"Domain context: {domain_hint.value}")
        
        if conversation_history:
            context_parts.append("Previous conversation context:")
            for msg in conversation_history[-5:]:  # Last 5 messages
                context_parts.append(f"- {msg.get('role', 'user')}: {msg.get('content', '')[:200]}")
        
        context_parts.append(f"\nCurrent request: {user_prompt}")
        
        full_prompt = "\n".join(context_parts)
        
        return await self.interpret(full_prompt)


# Convenience function for direct usage
async def interpret_task(
    user_prompt: str,
    llm_provider: Optional[LLMProvider] = None
) -> TaskInterpretation:
    """
    Convenience function to interpret a task.
    
    Args:
        user_prompt: The raw user request/prompt
        llm_provider: Optional LLM provider to use
        
    Returns:
        TaskInterpretation: A structured task plan
    """
    layer = TaskInterpretationLayer(llm_provider)
    return await layer.interpret(user_prompt)
