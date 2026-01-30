"""
McLeuker Agentic AI Platform - Layer 2: LLM Reasoning Layer

This layer thinks, plans, and structures the task, but does not execute it.
It produces a Reasoning Blueprint that guides all downstream layers.
"""

import json
from typing import Optional, Dict, Any, List
from src.models.schemas import (
    TaskInterpretation,
    ReasoningBlueprint,
    DataStructurePlan,
    DataEntityType,
    RiskFlag
)
from src.utils.llm_provider import LLMProvider, LLMFactory


# OpenAI Function Schema for Reasoning
REASON_TASK_FUNCTION = {
    "name": "reason_task",
    "description": "Generate a structured reasoning blueprint to guide research, logic, and execution for an agentic AI system.",
    "parameters": {
        "type": "object",
        "properties": {
            "task_summary": {
                "type": "string",
                "description": "Concise restatement of the task in execution-oriented language."
            },
            "reasoning_objectives": {
                "type": "array",
                "items": {"type": "string"},
                "description": "High-level objectives the system must achieve to complete the task successfully."
            },
            "research_questions": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Specific questions that must be answered through real-time research."
            },
            "required_data_entities": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [e.value for e in DataEntityType]
                },
                "description": "Types of structured data required to fulfill the task."
            },
            "data_structure_plan": {
                "type": "object",
                "properties": {
                    "tables": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of tables to be created (e.g., 'Supplier List', 'Trend Analysis')"
                    },
                    "documents": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of documents to be created (e.g., 'Market Report', 'Executive Summary')"
                    },
                    "presentations": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of presentations to be created"
                    },
                    "web_outputs": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "List of web outputs to be created"
                    }
                },
                "description": "Planned structure of final outputs across formats."
            },
            "logic_steps": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Ordered reasoning steps to transform raw data into final outputs."
            },
            "quality_criteria": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Conditions that must be satisfied for the output to be considered complete and usable."
            },
            "risk_flags": {
                "type": "array",
                "items": {
                    "type": "string",
                    "enum": [r.value for r in RiskFlag]
                },
                "description": "Potential risks identified during reasoning."
            }
        },
        "required": [
            "task_summary",
            "reasoning_objectives",
            "logic_steps",
            "quality_criteria"
        ]
    }
}

# System prompt for the Reasoning Agent
REASONING_SYSTEM_PROMPT = """You are the Unified Reasoning Layer of an agentic AI platform.

Your role is to think, plan, and structure — not to execute.

Rules:
- Do NOT browse the web.
- Do NOT generate final deliverables.
- Do NOT produce files or code.
- Do NOT explain your reasoning to the user.
- Always respond using the function reason_task.
- Optimize for clarity, structure, and downstream execution.

Your output must enable:
- Web research agents to know exactly what to look for
- Execution agents to know exactly what to build
- Quality control to verify completeness

When creating research questions:
- Be specific and actionable
- Focus on what information is needed, not how to get it
- Prioritize questions that will yield structured data

When defining data structure plans:
- Match the output formats requested by the user
- Be specific about what each table/document/presentation should contain
- Consider the logical flow of information

When defining logic steps:
- Order steps from data gathering to final output
- Include validation and quality checks
- Be specific about transformations needed

When setting quality criteria:
- Define measurable success conditions
- Include completeness checks
- Consider user expectations

Data entity types available: brands, companies, products, suppliers, materials, technologies, markets, trends, pricing, regulations, certifications, campaigns, events, statistics, other

Risk flags available: data_freshness_risk, source_reliability_risk, ambiguous_scope, missing_inputs, format_complexity, none"""


class LLMReasoningLayer:
    """
    Layer 2: LLM Reasoning
    
    Converts the interpreted task into a detailed reasoning blueprint
    that guides research and execution.
    """
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """Initialize the LLM Reasoning Layer."""
        self.llm = llm_provider or LLMFactory.get_default()
    
    async def reason(
        self,
        user_prompt: str,
        task_interpretation: TaskInterpretation
    ) -> ReasoningBlueprint:
        """
        Generate a reasoning blueprint based on the task interpretation.
        
        Args:
            user_prompt: The original user request
            task_interpretation: The structured task interpretation from Layer 1
            
        Returns:
            ReasoningBlueprint: A detailed reasoning plan
        """
        # Build the context message
        context = f"""Original user request: {user_prompt}

Task Interpretation:
- Intent: {task_interpretation.intent}
- Domains: {', '.join([d.value for d in task_interpretation.domains])}
- Requires Research: {task_interpretation.requires_real_time_research}
- Research Depth: {task_interpretation.research_depth.value}
- Geography: {', '.join(task_interpretation.geography) if task_interpretation.geography else 'Not specified'}
- Time Horizon: {task_interpretation.time_horizon or 'Not specified'}
- Required Outputs: {', '.join([o.value for o in task_interpretation.outputs])}
- Execution Plan: {' → '.join([e.value for e in task_interpretation.execution_plan])}
- Confidence: {task_interpretation.confidence_level.value}
- Assumptions: {', '.join(task_interpretation.assumptions) if task_interpretation.assumptions else 'None'}

Based on this interpretation, create a detailed reasoning blueprint that will guide the research and execution phases."""

        messages = [
            {"role": "system", "content": REASONING_SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ]
        
        response = await self.llm.complete(
            messages=messages,
            functions=[REASON_TASK_FUNCTION],
            function_call={"name": "reason_task"},
            temperature=0.1
        )
        
        # Extract the function call arguments
        if "function_call" in response and response["function_call"]:
            arguments = response["function_call"]["arguments"]
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            
            # Handle nested data_structure_plan
            if "data_structure_plan" in arguments and arguments["data_structure_plan"]:
                arguments["data_structure_plan"] = DataStructurePlan(**arguments["data_structure_plan"])
            
            # Convert string enums to proper types
            if "required_data_entities" in arguments:
                arguments["required_data_entities"] = [
                    DataEntityType(e) if isinstance(e, str) else e 
                    for e in arguments["required_data_entities"]
                ]
            
            if "risk_flags" in arguments:
                arguments["risk_flags"] = [
                    RiskFlag(r) if isinstance(r, str) else r 
                    for r in arguments["risk_flags"]
                ]
            
            return ReasoningBlueprint(**arguments)
        else:
            # Fallback: create a basic reasoning blueprint
            return self._create_fallback_blueprint(task_interpretation)
    
    def _create_fallback_blueprint(
        self,
        task_interpretation: TaskInterpretation
    ) -> ReasoningBlueprint:
        """Create a fallback reasoning blueprint when LLM fails."""
        # Generate basic research questions based on intent
        research_questions = []
        if task_interpretation.requires_real_time_research:
            research_questions = [
                f"What are the key aspects of {task_interpretation.intent}?",
                f"What are the latest developments in {', '.join([d.value for d in task_interpretation.domains])}?",
            ]
        
        # Generate basic data structure plan
        data_structure_plan = DataStructurePlan(
            tables=["Main Data Table"] if any(o in [OutputFormat.EXCEL, OutputFormat.CSV] for o in task_interpretation.outputs) else None,
            documents=["Main Report"] if any(o in [OutputFormat.PDF, OutputFormat.WORD] for o in task_interpretation.outputs) else None,
            presentations=["Main Presentation"] if OutputFormat.PPT in task_interpretation.outputs else None,
            web_outputs=["Web Content"] if OutputFormat.WEB in task_interpretation.outputs else None
        )
        
        return ReasoningBlueprint(
            task_summary=task_interpretation.intent,
            reasoning_objectives=[
                "Gather relevant information",
                "Structure data for output",
                "Generate requested deliverables"
            ],
            research_questions=research_questions if research_questions else None,
            required_data_entities=[DataEntityType.OTHER],
            data_structure_plan=data_structure_plan,
            logic_steps=[
                "Collect and validate input data",
                "Structure information according to output requirements",
                "Generate final deliverables",
                "Perform quality check"
            ],
            quality_criteria=[
                "All requested outputs are generated",
                "Information is accurate and relevant",
                "Outputs are properly formatted"
            ],
            risk_flags=[RiskFlag.AMBIGUOUS_SCOPE]
        )
    
    async def refine_reasoning(
        self,
        blueprint: ReasoningBlueprint,
        feedback: str
    ) -> ReasoningBlueprint:
        """
        Refine an existing reasoning blueprint based on feedback.
        
        Args:
            blueprint: The existing reasoning blueprint
            feedback: Feedback or additional context
            
        Returns:
            ReasoningBlueprint: A refined reasoning plan
        """
        context = f"""Current Reasoning Blueprint:
- Task Summary: {blueprint.task_summary}
- Objectives: {', '.join(blueprint.reasoning_objectives)}
- Research Questions: {', '.join(blueprint.research_questions) if blueprint.research_questions else 'None'}
- Logic Steps: {' → '.join(blueprint.logic_steps)}
- Quality Criteria: {', '.join(blueprint.quality_criteria)}

Feedback/Additional Context: {feedback}

Please refine the reasoning blueprint based on this feedback."""

        messages = [
            {"role": "system", "content": REASONING_SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ]
        
        response = await self.llm.complete(
            messages=messages,
            functions=[REASON_TASK_FUNCTION],
            function_call={"name": "reason_task"},
            temperature=0.1
        )
        
        if "function_call" in response and response["function_call"]:
            arguments = response["function_call"]["arguments"]
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            
            if "data_structure_plan" in arguments and arguments["data_structure_plan"]:
                arguments["data_structure_plan"] = DataStructurePlan(**arguments["data_structure_plan"])
            
            return ReasoningBlueprint(**arguments)
        
        return blueprint


# Convenience function for direct usage
async def reason_task(
    user_prompt: str,
    task_interpretation: TaskInterpretation,
    llm_provider: Optional[LLMProvider] = None
) -> ReasoningBlueprint:
    """
    Convenience function to generate a reasoning blueprint.
    
    Args:
        user_prompt: The original user request
        task_interpretation: The structured task interpretation
        llm_provider: Optional LLM provider to use
        
    Returns:
        ReasoningBlueprint: A detailed reasoning plan
    """
    layer = LLMReasoningLayer(llm_provider)
    return await layer.reason(user_prompt, task_interpretation)
