"""
McLeuker Agentic AI Platform - Layer 4: General Logic & Structuring Layer

This layer transforms researched information into actionable, structured data
ready for the final output generation in the Execution Layer.
"""

import json
from typing import Optional, Dict, Any, List
from src.models.schemas import (
    ReasoningBlueprint,
    ResearchOutput,
    StructuredOutput,
    StructuredTable,
    StructuredDocument,
    StructuredPresentation,
    OutputFormat,
    TaskInterpretation
)
from src.utils.llm_provider import LLMProvider, LLMFactory


# Function schema for structuring data
STRUCTURE_DATA_FUNCTION = {
    "name": "structure_data",
    "description": "Transform research findings into structured data for output generation.",
    "parameters": {
        "type": "object",
        "properties": {
            "tables": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "description": {"type": "string"},
                        "columns": {
                            "type": "array",
                            "items": {"type": "string"}
                        },
                        "rows": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "additionalProperties": True
                            }
                        }
                    },
                    "required": ["name", "columns", "rows"]
                },
                "description": "Structured tables for Excel/CSV output"
            },
            "documents": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "sections": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "heading": {"type": "string"},
                                    "content": {"type": "string"},
                                    "subsections": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "heading": {"type": "string"},
                                                "content": {"type": "string"}
                                            }
                                        }
                                    }
                                },
                                "required": ["heading", "content"]
                            }
                        },
                        "metadata": {
                            "type": "object",
                            "properties": {
                                "author": {"type": "string"},
                                "date": {"type": "string"},
                                "summary": {"type": "string"}
                            }
                        }
                    },
                    "required": ["title", "sections"]
                },
                "description": "Structured documents for PDF/Word output"
            },
            "presentations": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "slides": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "title": {"type": "string"},
                                    "content": {"type": "string"},
                                    "bullet_points": {
                                        "type": "array",
                                        "items": {"type": "string"}
                                    },
                                    "notes": {"type": "string"},
                                    "layout": {
                                        "type": "string",
                                        "enum": ["title", "content", "two_column", "image", "chart", "blank"]
                                    }
                                },
                                "required": ["title"]
                            }
                        },
                        "theme": {"type": "string"}
                    },
                    "required": ["title", "slides"]
                },
                "description": "Structured presentations for PPT output"
            },
            "raw_data": {
                "type": "object",
                "additionalProperties": True,
                "description": "Additional raw data for custom processing"
            }
        }
    }
}

# System prompt for the Structuring Agent
STRUCTURING_SYSTEM_PROMPT = """You are a Data Structuring Agent in an agentic AI platform.

Your role is to transform research findings into structured, actionable data formats.

Rules:
- Do NOT perform additional research.
- Do NOT generate final files.
- Focus on organizing and structuring information.
- Always respond using the function structure_data.
- Ensure data is properly formatted for downstream execution agents.

When creating tables:
- Use clear, descriptive column names
- Ensure data types are consistent within columns
- Include all relevant data points from research
- Order rows logically (alphabetically, by importance, or chronologically)

When creating documents:
- Use a logical section hierarchy
- Include executive summaries where appropriate
- Ensure content flows naturally between sections
- Include citations and sources where available

When creating presentations:
- Keep slides focused on single topics
- Use bullet points for key information
- Include speaker notes for context
- Balance text with visual elements (suggest charts/images)
- Limit bullet points to 5-7 per slide

Consider the domain context when structuring:
- Fashion: Include brand names, collections, seasons, materials
- Business: Include metrics, KPIs, market data
- Technology: Include technical specifications, comparisons
- Sustainability: Include certifications, environmental metrics"""


class LogicStructuringLayer:
    """
    Layer 4: General Logic & Structuring
    
    Transforms research findings into structured data formats
    ready for the Execution Layer.
    """
    
    def __init__(self, llm_provider: Optional[LLMProvider] = None):
        """Initialize the Logic & Structuring Layer."""
        self.llm = llm_provider or LLMFactory.get_default()
    
    async def structure(
        self,
        task_interpretation: TaskInterpretation,
        reasoning_blueprint: ReasoningBlueprint,
        research_output: ResearchOutput
    ) -> StructuredOutput:
        """
        Structure research findings for output generation.
        
        Args:
            task_interpretation: The task interpretation from Layer 1
            reasoning_blueprint: The reasoning blueprint from Layer 2
            research_output: The research output from Layer 3
            
        Returns:
            StructuredOutput: Structured data ready for execution
        """
        # Build context for structuring
        context = self._build_context(
            task_interpretation,
            reasoning_blueprint,
            research_output
        )
        
        messages = [
            {"role": "system", "content": STRUCTURING_SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ]
        
        response = await self.llm.complete(
            messages=messages,
            functions=[STRUCTURE_DATA_FUNCTION],
            function_call={"name": "structure_data"},
            temperature=0.2,
            max_tokens=4096
        )
        
        # Extract and parse the function call
        if "function_call" in response and response["function_call"]:
            arguments = response["function_call"]["arguments"]
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            
            return self._parse_structured_output(arguments)
        else:
            # Fallback: create basic structure
            return self._create_fallback_structure(
                task_interpretation,
                reasoning_blueprint,
                research_output
            )
    
    def _build_context(
        self,
        task_interpretation: TaskInterpretation,
        reasoning_blueprint: ReasoningBlueprint,
        research_output: ResearchOutput
    ) -> str:
        """Build context string for the LLM."""
        parts = [
            "=== TASK CONTEXT ===",
            f"Intent: {task_interpretation.intent}",
            f"Domains: {', '.join([d.value for d in task_interpretation.domains])}",
            f"Required Outputs: {', '.join([o.value for o in task_interpretation.outputs])}",
            "",
            "=== REASONING BLUEPRINT ===",
            f"Task Summary: {reasoning_blueprint.task_summary}",
            f"Objectives: {', '.join(reasoning_blueprint.reasoning_objectives)}",
        ]
        
        if reasoning_blueprint.data_structure_plan:
            parts.append("\nPlanned Data Structures:")
            if reasoning_blueprint.data_structure_plan.tables:
                parts.append(f"- Tables: {', '.join(reasoning_blueprint.data_structure_plan.tables)}")
            if reasoning_blueprint.data_structure_plan.documents:
                parts.append(f"- Documents: {', '.join(reasoning_blueprint.data_structure_plan.documents)}")
            if reasoning_blueprint.data_structure_plan.presentations:
                parts.append(f"- Presentations: {', '.join(reasoning_blueprint.data_structure_plan.presentations)}")
        
        parts.append("\n=== RESEARCH FINDINGS ===")
        
        # Add synthesized findings
        if research_output.synthesized_findings:
            parts.append(research_output.synthesized_findings[:3000])
        
        # Add search result summaries
        for sr in research_output.search_results[:3]:
            parts.append(f"\nQuery: {sr.query}")
            for result in sr.results[:3]:
                parts.append(f"- {result.title}: {result.snippet[:200]}")
        
        parts.append("\n=== INSTRUCTIONS ===")
        parts.append("Based on the above context, structure the research findings into the appropriate formats.")
        parts.append("Create tables, documents, and/or presentations as specified in the required outputs.")
        parts.append("Ensure all data is properly organized and ready for file generation.")
        
        return "\n".join(parts)
    
    def _parse_structured_output(self, data: Dict[str, Any]) -> StructuredOutput:
        """Parse the LLM response into StructuredOutput."""
        tables = None
        documents = None
        presentations = None
        
        if "tables" in data and data["tables"]:
            tables = []
            for t in data["tables"]:
                tables.append(StructuredTable(
                    name=t.get("name", "Untitled Table"),
                    description=t.get("description", ""),
                    columns=t.get("columns", []),
                    rows=t.get("rows", [])
                ))
        
        if "documents" in data and data["documents"]:
            documents = []
            for d in data["documents"]:
                documents.append(StructuredDocument(
                    title=d.get("title", "Untitled Document"),
                    sections=d.get("sections", []),
                    metadata=d.get("metadata")
                ))
        
        if "presentations" in data and data["presentations"]:
            presentations = []
            for p in data["presentations"]:
                presentations.append(StructuredPresentation(
                    title=p.get("title", "Untitled Presentation"),
                    slides=p.get("slides", []),
                    theme=p.get("theme")
                ))
        
        return StructuredOutput(
            tables=tables,
            documents=documents,
            presentations=presentations,
            raw_data=data.get("raw_data")
        )
    
    def _create_fallback_structure(
        self,
        task_interpretation: TaskInterpretation,
        reasoning_blueprint: ReasoningBlueprint,
        research_output: ResearchOutput
    ) -> StructuredOutput:
        """Create a fallback structure when LLM fails."""
        tables = None
        documents = None
        presentations = None
        
        # Create basic table if Excel/CSV is requested
        if any(o in [OutputFormat.EXCEL, OutputFormat.CSV] for o in task_interpretation.outputs):
            tables = [StructuredTable(
                name="Research Data",
                description="Data extracted from research",
                columns=["Topic", "Finding", "Source"],
                rows=[
                    {
                        "Topic": reasoning_blueprint.task_summary,
                        "Finding": research_output.synthesized_findings[:500] if research_output.synthesized_findings else "No findings",
                        "Source": "Web Research"
                    }
                ]
            )]
        
        # Create basic document if PDF/Word is requested
        if any(o in [OutputFormat.PDF, OutputFormat.WORD] for o in task_interpretation.outputs):
            documents = [StructuredDocument(
                title=reasoning_blueprint.task_summary,
                sections=[
                    {
                        "heading": "Executive Summary",
                        "content": research_output.synthesized_findings[:1000] if research_output.synthesized_findings else "Research summary pending."
                    },
                    {
                        "heading": "Findings",
                        "content": research_output.synthesized_findings[1000:3000] if research_output.synthesized_findings else "Detailed findings pending."
                    }
                ],
                metadata={
                    "author": "McLeuker AI",
                    "summary": task_interpretation.intent
                }
            )]
        
        # Create basic presentation if PPT is requested
        if OutputFormat.PPT in task_interpretation.outputs:
            presentations = [StructuredPresentation(
                title=reasoning_blueprint.task_summary,
                slides=[
                    {
                        "title": "Overview",
                        "content": task_interpretation.intent,
                        "layout": "title"
                    },
                    {
                        "title": "Key Findings",
                        "bullet_points": reasoning_blueprint.reasoning_objectives[:5],
                        "layout": "content"
                    }
                ],
                theme="professional"
            )]
        
        return StructuredOutput(
            tables=tables,
            documents=documents,
            presentations=presentations
        )
    
    async def restructure_for_format(
        self,
        structured_output: StructuredOutput,
        target_format: OutputFormat
    ) -> StructuredOutput:
        """
        Restructure existing output for a specific format.
        
        Args:
            structured_output: Existing structured output
            target_format: Target output format
            
        Returns:
            StructuredOutput: Restructured output
        """
        context = f"""Current structured data:
{json.dumps(structured_output.dict(), indent=2, default=str)[:3000]}

Target format: {target_format.value}

Restructure the data to be optimal for the target format."""

        messages = [
            {"role": "system", "content": STRUCTURING_SYSTEM_PROMPT},
            {"role": "user", "content": context}
        ]
        
        response = await self.llm.complete(
            messages=messages,
            functions=[STRUCTURE_DATA_FUNCTION],
            function_call={"name": "structure_data"},
            temperature=0.2
        )
        
        if "function_call" in response and response["function_call"]:
            arguments = response["function_call"]["arguments"]
            if isinstance(arguments, str):
                arguments = json.loads(arguments)
            return self._parse_structured_output(arguments)
        
        return structured_output


# Convenience function for direct usage
async def structure_data(
    task_interpretation: TaskInterpretation,
    reasoning_blueprint: ReasoningBlueprint,
    research_output: ResearchOutput,
    llm_provider: Optional[LLMProvider] = None
) -> StructuredOutput:
    """
    Convenience function to structure research data.
    
    Args:
        task_interpretation: The task interpretation
        reasoning_blueprint: The reasoning blueprint
        research_output: The research output
        llm_provider: Optional LLM provider
        
    Returns:
        StructuredOutput: Structured data ready for execution
    """
    layer = LogicStructuringLayer(llm_provider)
    return await layer.structure(
        task_interpretation,
        reasoning_blueprint,
        research_output
    )
