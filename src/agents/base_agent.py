"""
McLeuker Agentic AI Platform - Base Execution Agent

Base class for all execution agents in the Execution Layer.
"""

import os
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List
from datetime import datetime

from src.models.schemas import (
    StructuredOutput,
    GeneratedFile,
    OutputFormat
)
from src.config.settings import get_settings


class BaseExecutionAgent(ABC):
    """
    Abstract base class for execution agents.
    
    Each execution agent is responsible for generating a specific
    type of output (Excel, PDF, PPT, etc.).
    """
    
    def __init__(self, output_dir: Optional[str] = None):
        """Initialize the execution agent."""
        settings = get_settings()
        self.output_dir = output_dir or settings.OUTPUT_DIR
        
        # Ensure output directory exists
        os.makedirs(self.output_dir, exist_ok=True)
    
    @property
    @abstractmethod
    def supported_formats(self) -> List[OutputFormat]:
        """Return the list of output formats this agent supports."""
        pass
    
    @abstractmethod
    async def execute(
        self,
        structured_output: StructuredOutput,
        filename_prefix: Optional[str] = None
    ) -> List[GeneratedFile]:
        """
        Execute the agent to generate output files.
        
        Args:
            structured_output: The structured data to convert to files
            filename_prefix: Optional prefix for generated filenames
            
        Returns:
            List[GeneratedFile]: List of generated files
        """
        pass
    
    def _generate_filename(
        self,
        prefix: Optional[str],
        extension: str,
        suffix: Optional[str] = None
    ) -> str:
        """Generate a unique filename."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        parts = []
        
        if prefix:
            # Sanitize prefix
            prefix = "".join(c if c.isalnum() or c in "._-" else "_" for c in prefix)
            parts.append(prefix[:50])
        
        parts.append(timestamp)
        
        if suffix:
            parts.append(suffix)
        
        filename = "_".join(parts)
        return f"{filename}.{extension}"
    
    def _get_file_path(self, filename: str) -> str:
        """Get the full path for a file."""
        return os.path.join(self.output_dir, filename)
    
    def _get_file_size(self, filepath: str) -> int:
        """Get the size of a file in bytes."""
        try:
            return os.path.getsize(filepath)
        except OSError:
            return 0
    
    def _create_generated_file(
        self,
        filename: str,
        format: OutputFormat
    ) -> GeneratedFile:
        """Create a GeneratedFile object."""
        filepath = self._get_file_path(filename)
        return GeneratedFile(
            filename=filename,
            format=format,
            path=filepath,
            size_bytes=self._get_file_size(filepath)
        )
