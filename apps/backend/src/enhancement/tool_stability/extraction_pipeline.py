"""
Extraction Pipeline - Complex Data Extraction Workflows
========================================================

Specialized pipeline for complex multi-step data extraction:
- Web scraping workflows
- Document processing
- Data transformation
- Validation and cleaning
"""

import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator, Callable
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class ExtractionType(Enum):
    """Types of extraction"""
    WEB_SCRAPE = "web_scrape"
    DOCUMENT_PARSE = "document_parse"
    API_FETCH = "api_fetch"
    IMAGE_EXTRACT = "image_extract"
    DATA_TRANSFORM = "data_transform"
    VALIDATE = "validate"


@dataclass
class ExtractionStep:
    """A single extraction step"""
    id: str
    name: str
    extraction_type: ExtractionType
    source: str  # URL, file path, etc.
    selectors: Dict[str, str] = field(default_factory=dict)  # CSS selectors, XPath, etc.
    transformations: List[str] = field(default_factory=list)  # Transform to apply
    validators: List[str] = field(default_factory=list)  # Validation rules
    fallback_sources: List[str] = field(default_factory=list)
    output_schema: Dict[str, Any] = field(default_factory=dict)
    result: Optional[Any] = None
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "extraction_type": self.extraction_type.value,
            "source": self.source,
            "selectors": self.selectors,
            "transformations": self.transformations,
            "validators": self.validators,
            "fallback_sources": self.fallback_sources,
            "output_schema": self.output_schema,
            "result": self.result,
            "errors": self.errors,
        }


@dataclass
class ExtractionResult:
    """Result of extraction"""
    success: bool
    data: Any = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    errors: List[str] = field(default_factory=list)
    extraction_time_ms: float = 0.0
    sources_used: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "data": self.data,
            "metadata": self.metadata,
            "errors": self.errors,
            "extraction_time_ms": self.extraction_time_ms,
            "sources_used": self.sources_used,
        }


class ExtractionPipeline:
    """
    Pipeline for complex data extraction workflows.
    
    Features:
    - Multi-source extraction
    - Data transformation
    - Validation
    - Fallback mechanisms
    - Incremental extraction
    """
    
    def __init__(
        self,
        browser_tools=None,
        file_tools=None,
        api_client=None,
        image_analyzer=None,
    ):
        """
        Initialize extraction pipeline.
        
        Args:
            browser_tools: Browser automation tools
            file_tools: File operation tools
            api_client: API client for data fetching
            image_analyzer: Image analysis capability
        """
        self.browser_tools = browser_tools
        self.file_tools = file_tools
        self.api_client = api_client
        self.image_analyzer = image_analyzer
        
        # Transformation functions
        self._transformers: Dict[str, Callable] = {
            "clean_html": self._clean_html,
            "extract_text": self._extract_text,
            "parse_json": self._parse_json,
            "normalize": self._normalize_data,
            "deduplicate": self._deduplicate,
        }
        
        # Validation functions
        self._validators: Dict[str, Callable] = {
            "not_empty": self._validate_not_empty,
            "has_required_fields": self._validate_required_fields,
            "is_valid_url": self._validate_url,
            "is_number": self._validate_number,
        }
    
    async def extract(
        self,
        steps: List[ExtractionStep],
        combine_results: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute extraction pipeline.
        
        Args:
            steps: List of extraction steps
            combine_results: Whether to combine results
            
        Yields:
            Extraction events and results
        """
        yield {"type": "pipeline_started", "total_steps": len(steps)}
        
        results = []
        
        for i, step in enumerate(steps):
            yield {
                "type": "step_started",
                "step_id": step.id,
                "step_name": step.name,
                "step_number": i + 1,
                "total_steps": len(steps)
            }
            
            try:
                result = await self._execute_step(step)
                results.append(result)
                
                yield {
                    "type": "step_completed",
                    "step_id": step.id,
                    "step_name": step.name,
                    "success": result.success,
                    "data_preview": self._preview_data(result.data)
                }
                
            except Exception as e:
                logger.exception(f"Extraction step {step.id} failed: {e}")
                step.errors.append(str(e))
                
                yield {
                    "type": "step_failed",
                    "step_id": step.id,
                    "step_name": step.name,
                    "error": str(e)
                }
        
        # Combine results if requested
        if combine_results:
            combined = self._combine_results(results)
            yield {"type": "pipeline_completed", "combined_result": combined}
        else:
            yield {"type": "pipeline_completed", "results": [r.to_dict() for r in results]}
    
    async def _execute_step(self, step: ExtractionStep) -> ExtractionResult:
        """Execute a single extraction step"""
        
        start_time = datetime.now()
        sources_tried = [step.source]
        
        try:
            # Try primary source
            data = await self._extract_from_source(step)
            
            if data is None and step.fallback_sources:
                # Try fallback sources
                for fallback in step.fallback_sources:
                    sources_tried.append(fallback)
                    step.source = fallback
                    data = await self._extract_from_source(step)
                    if data is not None:
                        break
            
            if data is None:
                return ExtractionResult(
                    success=False,
                    errors=["Failed to extract data from all sources"],
                    sources_used=sources_tried,
                    extraction_time_ms=(datetime.now() - start_time).total_seconds() * 1000
                )
            
            # Apply transformations
            for transform_name in step.transformations:
                transformer = self._transformers.get(transform_name)
                if transformer:
                    data = transformer(data)
            
            # Validate
            for validator_name in step.validators:
                validator = self._validators.get(validator_name)
                if validator:
                    is_valid, error = validator(data, step.output_schema)
                    if not is_valid:
                        step.errors.append(error)
            
            step.result = data
            
            return ExtractionResult(
                success=len(step.errors) == 0,
                data=data,
                errors=step.errors,
                sources_used=sources_tried,
                extraction_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
            
        except Exception as e:
            return ExtractionResult(
                success=False,
                errors=[str(e)],
                sources_used=sources_tried,
                extraction_time_ms=(datetime.now() - start_time).total_seconds() * 1000
            )
    
    async def _extract_from_source(self, step: ExtractionStep) -> Any:
        """Extract data based on extraction type"""
        
        if step.extraction_type == ExtractionType.WEB_SCRAPE:
            return await self._web_scrape(step)
        
        elif step.extraction_type == ExtractionType.DOCUMENT_PARSE:
            return await self._parse_document(step)
        
        elif step.extraction_type == ExtractionType.API_FETCH:
            return await self._api_fetch(step)
        
        elif step.extraction_type == ExtractionType.IMAGE_EXTRACT:
            return await self._extract_from_image(step)
        
        elif step.extraction_type == ExtractionType.DATA_TRANSFORM:
            return await self._transform_data(step)
        
        else:
            raise ValueError(f"Unknown extraction type: {step.extraction_type}")
    
    async def _web_scrape(self, step: ExtractionStep) -> Any:
        """Scrape data from web"""
        if not self.browser_tools:
            raise ValueError("Browser tools not available")
        
        # Navigate to page
        await self.browser_tools.navigate(step.source)
        
        results = {}
        
        for key, selector in step.selectors.items():
            try:
                # Extract text
                text_result = await self.browser_tools.extract_text(selector=selector)
                if text_result.success:
                    results[key] = text_result.output.get("text", "")
            except Exception as e:
                logger.warning(f"Failed to extract {key}: {e}")
        
        return results
    
    async def _parse_document(self, step: ExtractionStep) -> Any:
        """Parse document file"""
        if not self.file_tools:
            raise ValueError("File tools not available")
        
        # Read file
        result = await self.file_tools.read_file(step.source)
        
        if result.success:
            return result.output.get("content", "")
        
        return None
    
    async def _api_fetch(self, step: ExtractionStep) -> Any:
        """Fetch data from API"""
        if not self.api_client:
            raise ValueError("API client not available")
        
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get(step.source)
            response.raise_for_status()
            
            if "json" in response.headers.get("content-type", ""):
                return response.json()
            
            return response.text
    
    async def _extract_from_image(self, step: ExtractionStep) -> Any:
        """Extract data from image"""
        if not self.image_analyzer:
            raise ValueError("Image analyzer not available")
        
        # Use image analysis
        return await self.image_analyzer.analyze(step.source, step.selectors)
    
    async def _transform_data(self, step: ExtractionStep) -> Any:
        """Transform existing data"""
        # This would transform data from previous steps
        return step.result
    
    # Transformation functions
    def _clean_html(self, data: Any) -> Any:
        """Clean HTML content"""
        if isinstance(data, str):
            import re
            # Remove HTML tags
            clean = re.sub(r'<[^>]+>', '', data)
            # Normalize whitespace
            clean = re.sub(r'\s+', ' ', clean)
            return clean.strip()
        return data
    
    def _extract_text(self, data: Any) -> Any:
        """Extract plain text"""
        if isinstance(data, dict):
            return {k: self._clean_html(v) if isinstance(v, str) else v 
                    for k, v in data.items()}
        return self._clean_html(data)
    
    def _parse_json(self, data: Any) -> Any:
        """Parse JSON string"""
        if isinstance(data, str):
            try:
                return json.loads(data)
            except json.JSONDecodeError:
                return data
        return data
    
    def _normalize_data(self, data: Any) -> Any:
        """Normalize data format"""
        if isinstance(data, list):
            return [self._normalize_data(item) for item in data]
        if isinstance(data, dict):
            return {k.lower().strip(): self._normalize_data(v) 
                    for k, v in data.items()}
        if isinstance(data, str):
            return data.strip()
        return data
    
    def _deduplicate(self, data: Any) -> Any:
        """Remove duplicates from list"""
        if isinstance(data, list):
            seen = set()
            result = []
            for item in data:
                item_str = json.dumps(item, sort_keys=True) if isinstance(item, (dict, list)) else str(item)
                if item_str not in seen:
                    seen.add(item_str)
                    result.append(item)
            return result
        return data
    
    # Validation functions
    def _validate_not_empty(self, data: Any, schema: Dict) -> tuple:
        """Validate data is not empty"""
        if data is None or (isinstance(data, (list, dict, str)) and len(data) == 0):
            return False, "Data is empty"
        return True, ""
    
    def _validate_required_fields(self, data: Any, schema: Dict) -> tuple:
        """Validate required fields exist"""
        required = schema.get("required_fields", [])
        if isinstance(data, dict):
            missing = [f for f in required if f not in data]
            if missing:
                return False, f"Missing required fields: {missing}"
        return True, ""
    
    def _validate_url(self, data: Any, schema: Dict) -> tuple:
        """Validate URL format"""
        if isinstance(data, str):
            import re
            url_pattern = r'^https?://[^\s/$.?#].[^\s]*$'
            if not re.match(url_pattern, data):
                return False, "Invalid URL format"
        return True, ""
    
    def _validate_number(self, data: Any, schema: Dict) -> tuple:
        """Validate data is a number"""
        try:
            float(data)
            return True, ""
        except (ValueError, TypeError):
            return False, "Not a valid number"
    
    def _preview_data(self, data: Any, max_length: int = 200) -> Any:
        """Create preview of data"""
        if isinstance(data, str):
            return data[:max_length] + "..." if len(data) > max_length else data
        if isinstance(data, (list, dict)):
            preview = json.dumps(data)[:max_length]
            return preview + "..." if len(json.dumps(data)) > max_length else data
        return data
    
    def _combine_results(self, results: List[ExtractionResult]) -> Dict:
        """Combine multiple extraction results"""
        combined_data = {}
        all_errors = []
        total_time = 0
        all_sources = []
        
        for result in results:
            if result.success and result.data:
                if isinstance(result.data, dict):
                    combined_data.update(result.data)
                else:
                    combined_data[f"result_{len(combined_data)}"] = result.data
            
            all_errors.extend(result.errors)
            total_time += result.extraction_time_ms
            all_sources.extend(result.sources_used)
        
        return {
            "success": len(combined_data) > 0,
            "data": combined_data,
            "errors": all_errors,
            "total_extraction_time_ms": total_time,
            "sources_used": list(set(all_sources))
        }
