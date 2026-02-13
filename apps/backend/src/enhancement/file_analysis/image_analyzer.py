"""
Image Analyzer - Specialized Image Analysis
============================================

Specialized image analysis for fashion and beauty domains.
"""

import json
import logging
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from pathlib import Path
import mimetypes

logger = logging.getLogger(__name__)


@dataclass
class ImageAnalysis:
    """Image analysis result"""
    description: str
    objects: List[str] = field(default_factory=list)
    colors: List[str] = field(default_factory=list)
    styles: List[str] = field(default_factory=list)
    text_found: List[str] = field(default_factory=list)
    mood: str = ""
    composition: str = ""
    quality_assessment: str = ""


class ImageAnalyzer:
    """
    Specialized image analyzer for fashion and beauty.
    
    Capabilities:
    - Fashion item recognition
    - Style analysis
    - Color palette extraction
    - Outfit analysis
    - Beauty product identification
    """
    
    def __init__(self, llm_client):
        self.llm_client = llm_client
    
    async def analyze_fashion_image(
        self,
        image_path: str,
        analysis_type: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze a fashion image.
        
        Args:
            image_path: Path to image
            analysis_type: Type of analysis (general, outfit, detail, trend)
            
        Returns:
            Analysis result
        """
        try:
            # Encode image
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            base64_image = base64.b64encode(image_data).decode("utf-8")
            mime_type, _ = mimetypes.guess_type(image_path)
            data_url = f"data:{mime_type};base64,{base64_image}"
            
            # Build prompt based on analysis type
            prompts = {
                "general": "Analyze this fashion image. Describe the outfit, style, colors, and key elements.",
                "outfit": "Analyze this outfit in detail. Identify each piece, brand if visible, styling, and overall look.",
                "detail": "Focus on the details in this fashion image. Analyze textures, materials, craftsmanship, and finishing.",
                "trend": "Analyze this image for fashion trends. What trends does it represent? Is it current or vintage?",
            }
            
            prompt = prompts.get(analysis_type, prompts["general"])
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a fashion image analysis expert. Provide detailed, structured analysis."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
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
            
            analysis_text = response.choices[0].message.content
            
            # Parse structured response
            return {
                "analysis": analysis_text,
                "analysis_type": analysis_type,
                "key_findings": self._extract_findings(analysis_text)
            }
            
        except Exception as e:
            logger.error(f"Fashion image analysis failed: {e}")
            return {"error": str(e)}
    
    async def analyze_beauty_image(
        self,
        image_path: str,
        focus: str = "general"
    ) -> Dict[str, Any]:
        """
        Analyze a beauty image.
        
        Args:
            image_path: Path to image
            focus: Analysis focus (general, makeup, skincare, product)
            
        Returns:
            Analysis result
        """
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            base64_image = base64.b64encode(image_data).decode("utf-8")
            mime_type, _ = mimetypes.guess_type(image_path)
            data_url = f"data:{mime_type};base64,{base64_image}"
            
            prompts = {
                "general": "Analyze this beauty image. Describe the look, products used, and techniques.",
                "makeup": "Analyze this makeup look in detail. Identify products, colors, application techniques.",
                "skincare": "Analyze this skincare-related image. Identify products, routine indicators.",
                "product": "Identify the beauty product(s) in this image. Brand, type, packaging details.",
            }
            
            prompt = prompts.get(focus, prompts["general"])
            
            messages = [
                {
                    "role": "system",
                    "content": "You are a beauty image analysis expert. Provide detailed product and technique analysis."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
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
            
            return {
                "analysis": response.choices[0].message.content,
                "focus": focus
            }
            
        except Exception as e:
            logger.error(f"Beauty image analysis failed: {e}")
            return {"error": str(e)}
    
    async def extract_color_palette(
        self,
        image_path: str
    ) -> Dict[str, Any]:
        """Extract dominant colors from image"""
        
        try:
            with open(image_path, "rb") as f:
                image_data = f.read()
            
            base64_image = base64.b64encode(image_data).decode("utf-8")
            mime_type, _ = mimetypes.guess_type(image_path)
            data_url = f"data:{mime_type};base64,{base64_image}"
            
            messages = [
                {
                    "role": "system",
                    "content": "Extract the dominant colors from this image. Provide color names and hex codes."
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": "Extract the color palette from this image. List dominant colors with approximate percentages."},
                        {"type": "image_url", "image_url": {"url": data_url}}
                    ]
                }
            ]
            
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=1000
            )
            
            return {
                "color_palette": response.choices[0].message.content
            }
            
        except Exception as e:
            logger.error(f"Color extraction failed: {e}")
            return {"error": str(e)}
    
    def _extract_findings(self, text: str) -> List[str]:
        """Extract key findings from analysis text"""
        findings = []
        lines = text.split("\n")
        
        for line in lines:
            line = line.strip()
            if line.startswith(("- ", "* ", "• ")):
                findings.append(line[2:].strip())
            elif line and line[0].isdigit() and "." in line[:3]:
                findings.append(line.split(".", 1)[1].strip())
        
        return findings[:10]
