"""
Multimodal Analyzer - kimi-2.5 Vision Capabilities
===================================================

Analyzes files using kimi-2.5's multimodal capabilities:
- Image understanding
- Document OCR
- Visual reasoning
- Cross-modal analysis
"""

import json
import logging
import base64
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)


@dataclass
class AnalysisResult:
    """Result of multimodal analysis"""
    success: bool
    content_type: str
    description: str
    key_elements: List[str] = field(default_factory=list)
    extracted_text: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    confidence: float = 0.0
    errors: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "success": self.success,
            "content_type": self.content_type,
            "description": self.description,
            "key_elements": self.key_elements,
            "extracted_text": self.extracted_text,
            "metadata": self.metadata,
            "confidence": self.confidence,
            "errors": self.errors,
        }


class MultimodalAnalyzer:
    """
    Multimodal analyzer using kimi-2.5's vision capabilities.
    
    Supports:
    - Image analysis
    - Document OCR
    - Visual reasoning
    - Cross-modal understanding
    """
    
    SUPPORTED_IMAGE_TYPES = [
        "image/jpeg", "image/jpg", "image/png", "image/gif",
        "image/webp", "image/bmp", "image/tiff"
    ]
    
    SUPPORTED_DOCUMENT_TYPES = [
        "application/pdf", "text/plain", "text/markdown",
        "application/msword", "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/vnd.ms-excel", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        "application/vnd.ms-powerpoint", "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    ]
    
    def __init__(self, llm_client, max_image_size: int = 20 * 1024 * 1024):
        """
        Initialize multimodal analyzer.
        
        Args:
            llm_client: AsyncOpenAI client for kimi-2.5
            max_image_size: Maximum image size in bytes
        """
        self.llm_client = llm_client
        self.max_image_size = max_image_size
    
    async def analyze_file(
        self,
        file_path: str,
        query: Optional[str] = None,
        extract_text: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Analyze a file using multimodal capabilities.
        
        Args:
            file_path: Path to file
            query: Optional specific query about the file
            extract_text: Whether to extract text
            
        Yields:
            Analysis events and results
        """
        yield {"type": "analysis_started", "file_path": file_path}
        
        path = Path(file_path)
        
        if not path.exists():
            yield {"type": "error", "error": f"File not found: {file_path}"}
            return
        
        # Detect content type
        mime_type, _ = mimetypes.guess_type(str(path))
        
        if mime_type in self.SUPPORTED_IMAGE_TYPES:
            async for event in self._analyze_image(file_path, query, extract_text):
                yield event
        
        elif mime_type in self.SUPPORTED_DOCUMENT_TYPES:
            async for event in self._analyze_document(file_path, query, extract_text):
                yield event
        
        else:
            # Try generic analysis
            async for event in self._generic_analysis(file_path, query):
                yield event
    
    async def _analyze_image(
        self,
        file_path: str,
        query: Optional[str],
        extract_text: bool
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze an image using kimi-2.5 vision"""
        
        yield {"type": "status", "message": "Analyzing image with vision..."}
        
        try:
            # Read and encode image
            with open(file_path, "rb") as f:
                image_data = f.read()
            
            if len(image_data) > self.max_image_size:
                yield {"type": "error", "error": "Image too large"}
                return
            
            base64_image = base64.b64encode(image_data).decode("utf-8")
            
            # Determine image format
            mime_type, _ = mimetypes.guess_type(file_path)
            data_url = f"data:{mime_type};base64,{base64_image}"
            
            # Build prompt
            if query:
                user_prompt = query
            else:
                user_prompt = """Analyze this image in detail. Provide:
1. A comprehensive description
2. Key visual elements
3. Colors and composition
4. Any text visible in the image
5. Context and meaning"""
            
            # Call kimi-2.5 with vision
            messages = [
                {
                    "role": "system",
                    "content": "You are a visual analysis expert. Analyze images comprehensively."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": user_prompt},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }
            ]
            
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=4000
            )
            
            analysis_text = response.choices[0].message.content
            
            # Parse structured response
            result = AnalysisResult(
                success=True,
                content_type="image",
                description=analysis_text,
                key_elements=self._extract_key_elements(analysis_text),
                confidence=0.9
            )
            
            yield {
                "type": "image_analysis",
                "data": result.to_dict()
            }
            
            # Extract text if requested
            if extract_text:
                async for event in self._extract_text_from_image(data_url):
                    yield event
            
        except Exception as e:
            logger.exception(f"Image analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _extract_text_from_image(
        self,
        data_url: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Extract text from image using OCR"""
        
        yield {"type": "status", "message": "Extracting text from image..."}
        
        try:
            messages = [
                {
                    "role": "system",
                    "content": "Extract all visible text from this image. Preserve formatting."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract all text visible in this image:"},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }
            ]
            
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=2000
            )
            
            extracted_text = response.choices[0].message.content
            
            yield {
                "type": "text_extraction",
                "extracted_text": extracted_text
            }
            
        except Exception as e:
            logger.error(f"Text extraction failed: {e}")
            yield {"type": "error", "error": f"Text extraction failed: {e}"}
    
    async def _analyze_document(
        self,
        file_path: str,
        query: Optional[str],
        extract_text: bool
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze a document"""
        
        yield {"type": "status", "message": "Analyzing document..."}
        
        try:
            # For PDFs, we might need to convert to images first
            # For now, read as text if possible
            mime_type, _ = mimetypes.guess_type(file_path)
            
            if mime_type == "application/pdf":
                async for event in self._analyze_pdf(file_path, query):
                    yield event
            elif mime_type in ["text/plain", "text/markdown"]:
                async for event in self._analyze_text_file(file_path, query):
                    yield event
            else:
                yield {"type": "error", "error": f"Document type not fully supported: {mime_type}"}
            
        except Exception as e:
            logger.exception(f"Document analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _analyze_pdf(
        self,
        file_path: str,
        query: Optional[str]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze PDF document"""
        
        yield {"type": "status", "message": "Processing PDF..."}
        
        try:
            # Try to extract text from PDF
            import PyPDF2
            
            with open(file_path, "rb") as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() + "\n"
            
            if text.strip():
                # Analyze extracted text
                user_prompt = query or "Analyze this document. Provide a summary and key points."
                
                messages = [
                    {
                        "role": "system",
                        "content": "You are a document analysis expert. Summarize and extract key information."
                    },
                    {
                        "role": "user",
                        "content": f"{user_prompt}\n\nDocument content:\n{text[:8000]}"
                    }
                ]
                
                response = await self.llm_client.chat.completions.create(
                    model="kimi-k2.5",
                    messages=messages,
                    temperature=1.0,
                    max_tokens=4000
                )
                
                analysis = response.choices[0].message.content
                
                result = AnalysisResult(
                    success=True,
                    content_type="pdf",
                    description=analysis,
                    extracted_text=text[:5000],
                    metadata={"pages": len(reader.pages)},
                    confidence=0.85
                )
                
                yield {
                    "type": "document_analysis",
                    "data": result.to_dict()
                }
            else:
                yield {"type": "error", "error": "Could not extract text from PDF"}
            
        except ImportError:
            yield {"type": "error", "error": "PDF analysis requires PyPDF2. Install with: pip install PyPDF2"}
        except Exception as e:
            logger.error(f"PDF analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _analyze_text_file(
        self,
        file_path: str,
        query: Optional[str]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze text file"""
        
        yield {"type": "status", "message": "Analyzing text file..."}
        
        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                text = f.read()
            
            user_prompt = query or "Analyze this document. Provide a summary and key points."
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a document analysis expert. Summarize and extract key information."
                },
                {
                    "role": "user",
                    "content": f"{user_prompt}\n\nDocument content:\n{text[:10000]}"
                }
            ]
            
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=4000
            )
            
            analysis = response.choices[0].message.content
            
            result = AnalysisResult(
                success=True,
                content_type="text",
                description=analysis,
                extracted_text=text[:5000],
                confidence=0.9
            )
            
            yield {
                "type": "document_analysis",
                "data": result.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Text file analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _generic_analysis(
        self,
        file_path: str,
        query: Optional[str]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Generic file analysis"""
        
        yield {"type": "status", "message": "Performing generic analysis..."}
        
        try:
            # Get file info
            path = Path(file_path)
            stat = path.stat()
            
            mime_type, _ = mimetypes.guess_type(str(path))
            
            result = AnalysisResult(
                success=True,
                content_type=mime_type or "unknown",
                description=f"File: {path.name}, Size: {stat.st_size} bytes, Type: {mime_type}",
                metadata={
                    "filename": path.name,
                    "size": stat.st_size,
                    "mime_type": mime_type,
                    "extension": path.suffix
                },
                confidence=0.5
            )
            
            yield {
                "type": "generic_analysis",
                "data": result.to_dict()
            }
            
        except Exception as e:
            logger.error(f"Generic analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    def _extract_key_elements(self, text: str) -> List[str]:
        """Extract key elements from analysis text"""
        elements = []
        
        # Simple extraction based on common patterns
        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            # Look for bullet points or numbered items
            if line.startswith(("- ", "* ", "• ", "1. ", "2. ", "3. ")):
                elements.append(line[2:].strip())
        
        return elements[:10]  # Limit to 10 elements
    
    async def compare_images(
        self,
        image_paths: List[str],
        comparison_query: str
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Compare multiple images.
        
        Args:
            image_paths: List of image paths
            comparison_query: What to compare
            
        Yields:
            Comparison results
        """
        yield {"type": "comparison_started", "image_count": len(image_paths)}
        
        try:
            # Encode all images
            image_contents = []
            for path in image_paths:
                with open(path, "rb") as f:
                    image_data = f.read()
                base64_image = base64.b64encode(image_data).decode("utf-8")
                mime_type, _ = mimetypes.guess_type(path)
                data_url = f"data:{mime_type};base64,{base64_image}"
                image_contents.append({
                    "type": "image_url",
                    "image_url": {"url": data_url}
                })
            
            # Build comparison prompt
            messages = [
                {
                    "role": "system",
                    "content": "You are an image comparison expert. Compare images in detail."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": comparison_query},
                        *image_contents
                    ]
                }
            ]
            
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=4000
            )
            
            comparison = response.choices[0].message.content
            
            yield {
                "type": "image_comparison",
                "comparison": comparison
            }
            
        except Exception as e:
            logger.error(f"Image comparison failed: {e}")
            yield {"type": "error", "error": str(e)}
