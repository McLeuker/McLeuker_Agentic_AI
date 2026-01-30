"""
McLeuker Agentic AI Platform - Layer 5: Execution Layer

This layer orchestrates all execution agents to generate the final
deliverables based on the structured output from the Structuring Layer.
"""

import os
from typing import Optional, List, Dict, Any
from datetime import datetime

from src.models.schemas import (
    TaskInterpretation,
    StructuredOutput,
    GeneratedFile,
    ExecutionResult,
    OutputFormat
)
from src.agents.excel_agent import ExcelAgent
from src.agents.pdf_agent import PDFAgent
from src.agents.ppt_agent import PPTAgent
from src.agents.web_code_agent import WebCodeAgent
from src.config.settings import get_settings


class ExecutionLayer:
    """
    Layer 5: Execution
    
    Orchestrates all execution agents to generate final deliverables
    based on the requested output formats.
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the Execution Layer with all agents."""
        settings = get_settings()
        self.output_dir = output_dir or settings.OUTPUT_DIR
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
        
        # Initialize agents
        self.excel_agent = ExcelAgent(self.output_dir)
        self.pdf_agent = PDFAgent(self.output_dir)
        self.ppt_agent = PPTAgent(self.output_dir)
        self.web_code_agent = WebCodeAgent(self.output_dir)
        
        # Map output formats to agents
        self.format_to_agent = {
            OutputFormat.EXCEL: self.excel_agent,
            OutputFormat.CSV: self.excel_agent,
            OutputFormat.PDF: self.pdf_agent,
            OutputFormat.WORD: self.pdf_agent,
            OutputFormat.PPT: self.ppt_agent,
            OutputFormat.WEB: self.web_code_agent,
            OutputFormat.DASHBOARD: self.web_code_agent,
            OutputFormat.CODE: self.web_code_agent,
        }
    
    async def execute(
        self,
        task_interpretation: TaskInterpretation,
        structured_output: StructuredOutput,
        filename_prefix: Optional[str] = None
    ) -> ExecutionResult:
        """
        Execute all required output generation.
        
        Args:
            task_interpretation: The task interpretation with required outputs
            structured_output: The structured data to convert
            filename_prefix: Optional prefix for all generated files
            
        Returns:
            ExecutionResult: Result containing all generated files
        """
        all_files = []
        errors = []
        
        # Get required output formats
        required_formats = task_interpretation.outputs
        
        # Generate prefix from intent if not provided
        if not filename_prefix:
            # Create a short prefix from the intent
            intent_words = task_interpretation.intent.split()[:3]
            filename_prefix = "_".join(intent_words).lower()
            filename_prefix = "".join(c if c.isalnum() or c == "_" else "" for c in filename_prefix)
        
        # Track which agents have been used to avoid duplicates
        used_agents = set()
        
        for output_format in required_formats:
            agent = self.format_to_agent.get(output_format)
            
            if not agent:
                errors.append(f"No agent available for format: {output_format.value}")
                continue
            
            # Skip if this agent has already been used
            agent_id = id(agent)
            if agent_id in used_agents:
                continue
            used_agents.add(agent_id)
            
            try:
                files = await agent.execute(structured_output, filename_prefix)
                all_files.extend(files)
            except Exception as e:
                errors.append(f"Error executing {output_format.value} agent: {str(e)}")
        
        # Determine success
        success = len(all_files) > 0 and len(errors) == 0
        
        # Create result message
        if success:
            message = f"Successfully generated {len(all_files)} file(s)"
        elif all_files:
            message = f"Generated {len(all_files)} file(s) with {len(errors)} error(s)"
        else:
            message = "Failed to generate any files"
        
        return ExecutionResult(
            files=all_files,
            success=success,
            message=message,
            errors=errors if errors else None
        )
    
    async def execute_single_format(
        self,
        output_format: OutputFormat,
        structured_output: StructuredOutput,
        filename_prefix: Optional[str] = None
    ) -> List[GeneratedFile]:
        """
        Execute a single output format.
        
        Args:
            output_format: The format to generate
            structured_output: The structured data
            filename_prefix: Optional prefix for filenames
            
        Returns:
            List of generated files
        """
        agent = self.format_to_agent.get(output_format)
        
        if not agent:
            return []
        
        return await agent.execute(structured_output, filename_prefix)
    
    async def generate_excel(
        self,
        structured_output: StructuredOutput,
        filename_prefix: Optional[str] = None
    ) -> List[GeneratedFile]:
        """Generate Excel files."""
        return await self.excel_agent.execute(structured_output, filename_prefix)
    
    async def generate_pdf(
        self,
        structured_output: StructuredOutput,
        filename_prefix: Optional[str] = None
    ) -> List[GeneratedFile]:
        """Generate PDF files."""
        return await self.pdf_agent.execute(structured_output, filename_prefix)
    
    async def generate_ppt(
        self,
        structured_output: StructuredOutput,
        filename_prefix: Optional[str] = None
    ) -> List[GeneratedFile]:
        """Generate PowerPoint files."""
        return await self.ppt_agent.execute(structured_output, filename_prefix)
    
    async def generate_web(
        self,
        structured_output: StructuredOutput,
        filename_prefix: Optional[str] = None
    ) -> List[GeneratedFile]:
        """Generate web/HTML files."""
        return await self.web_code_agent.execute(structured_output, filename_prefix)
    
    def get_supported_formats(self) -> List[OutputFormat]:
        """Get all supported output formats."""
        return list(self.format_to_agent.keys())
    
    def get_output_directory(self) -> str:
        """Get the output directory path."""
        return self.output_dir
    
    def list_generated_files(self) -> List[str]:
        """List all files in the output directory."""
        if not os.path.exists(self.output_dir):
            return []
        
        return [
            os.path.join(self.output_dir, f)
            for f in os.listdir(self.output_dir)
            if os.path.isfile(os.path.join(self.output_dir, f))
        ]
    
    def cleanup_old_files(self, max_age_hours: int = 24):
        """
        Clean up files older than the specified age.
        
        Args:
            max_age_hours: Maximum age of files to keep (in hours)
        """
        if not os.path.exists(self.output_dir):
            return
        
        current_time = datetime.now().timestamp()
        max_age_seconds = max_age_hours * 3600
        
        for filename in os.listdir(self.output_dir):
            filepath = os.path.join(self.output_dir, filename)
            if os.path.isfile(filepath):
                file_age = current_time - os.path.getmtime(filepath)
                if file_age > max_age_seconds:
                    try:
                        os.remove(filepath)
                    except OSError:
                        pass


# Convenience function for direct usage
async def execute_task(
    task_interpretation: TaskInterpretation,
    structured_output: StructuredOutput,
    output_dir: Optional[str] = None,
    filename_prefix: Optional[str] = None
) -> ExecutionResult:
    """
    Convenience function to execute a task.
    
    Args:
        task_interpretation: The task interpretation
        structured_output: The structured data
        output_dir: Optional output directory
        filename_prefix: Optional prefix for filenames
        
    Returns:
        ExecutionResult: Result containing all generated files
    """
    layer = ExecutionLayer(output_dir)
    return await layer.execute(
        task_interpretation,
        structured_output,
        filename_prefix
    )
