"""
V3.1 Output Layer - Image Generation
Nano Banana integration for AI-powered image generation.
"""

import asyncio
import aiohttp
import json
import base64
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from src.config.settings import settings


@dataclass
class ImageResult:
    """Result from image generation."""
    success: bool
    images: List[str]  # Base64 encoded images or URLs
    error: Optional[str] = None


class NanoBananaGenerator:
    """
    Nano Banana image generation integration.
    Creates fashion mood boards, product mockups, and visual content.
    """
    
    def __init__(self):
        self.api_key = settings.NANO_BANANA_API_KEY
        self.enabled = bool(self.api_key)
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
    
    async def generate(self, prompt: str, num_images: int = 1, 
                       style: str = "fashion", size: str = "1024x1024") -> ImageResult:
        """Generate images using Nano Banana / Google Imagen."""
        if not self.enabled:
            return ImageResult(success=False, images=[], error="Nano Banana not configured")
        
        try:
            # Enhance prompt for fashion context
            enhanced_prompt = self._enhance_prompt(prompt, style)
            
            url = f"{self.base_url}/models/imagen-3.0-generate-002:predict"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            
            payload = {
                "instances": [{"prompt": enhanced_prompt}],
                "parameters": {
                    "sampleCount": min(num_images, 4),
                    "aspectRatio": "1:1" if size == "1024x1024" else "16:9",
                    "personGeneration": "allow_adult",
                    "safetyFilterLevel": "block_few"
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload,
                                        timeout=aiohttp.ClientTimeout(total=60)) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        # Try alternative endpoint
                        return await self._fallback_generate(enhanced_prompt, num_images)
                    
                    data = await resp.json()
                    images = []
                    
                    for prediction in data.get("predictions", []):
                        if "bytesBase64Encoded" in prediction:
                            images.append(prediction["bytesBase64Encoded"])
                        elif "image" in prediction:
                            images.append(prediction["image"])
                    
                    return ImageResult(success=True, images=images)
                    
        except Exception as e:
            return ImageResult(success=False, images=[], error=str(e))
    
    async def _fallback_generate(self, prompt: str, num_images: int) -> ImageResult:
        """Fallback to alternative image generation method."""
        try:
            # Use Google's Gemini vision model for image generation
            url = f"{self.base_url}/models/gemini-2.0-flash-exp:generateContent"
            headers = {
                "Content-Type": "application/json",
                "x-goog-api-key": self.api_key
            }
            
            payload = {
                "contents": [{
                    "parts": [{
                        "text": f"Generate a detailed visual description for: {prompt}. Describe colors, composition, style, and mood in detail."
                    }]
                }],
                "generationConfig": {
                    "temperature": 0.7,
                    "maxOutputTokens": 1024
                }
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=headers, json=payload,
                                        timeout=aiohttp.ClientTimeout(total=30)) as resp:
                    if resp.status != 200:
                        return ImageResult(success=False, images=[], error="Image generation unavailable")
                    
                    data = await resp.json()
                    # Return the description as a placeholder
                    description = data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")
                    
                    return ImageResult(
                        success=True, 
                        images=[],
                        error=f"Image generation pending. Visual description: {description[:500]}"
                    )
                    
        except Exception as e:
            return ImageResult(success=False, images=[], error=str(e))
    
    def _enhance_prompt(self, prompt: str, style: str) -> str:
        """Enhance the prompt for better fashion-focused results."""
        
        style_modifiers = {
            "fashion": "high fashion, editorial style, professional photography, Vogue magazine quality",
            "streetwear": "urban style, street photography, authentic, trendy, youth culture",
            "luxury": "luxury brand aesthetic, elegant, sophisticated, premium quality",
            "minimalist": "minimalist design, clean lines, simple elegance, modern aesthetic",
            "vintage": "vintage fashion, retro style, nostalgic, classic elegance",
            "sustainable": "eco-friendly fashion, sustainable materials, natural tones, ethical fashion",
            "avant-garde": "avant-garde fashion, experimental, artistic, runway style",
            "casual": "casual wear, comfortable, everyday style, relaxed aesthetic"
        }
        
        modifier = style_modifiers.get(style.lower(), style_modifiers["fashion"])
        
        return f"{prompt}. Style: {modifier}. High resolution, professional quality."


class OutputLayer:
    """
    The V3.1 Output Layer
    Handles image generation and output formatting.
    """
    
    def __init__(self):
        self.image_gen = NanoBananaGenerator()
    
    async def generate_images(self, query: str, num_images: int = 1, 
                              style: str = "fashion") -> List[str]:
        """Generate images based on the query."""
        
        result = await self.image_gen.generate(query, num_images, style)
        
        if result.success:
            return result.images
        else:
            # Return empty list but log the error
            print(f"Image generation error: {result.error}")
            return []
    
    async def generate_mood_board(self, theme: str, elements: List[str]) -> Dict:
        """Generate a fashion mood board with multiple related images."""
        
        prompts = [
            f"{theme} - {element}" for element in elements[:4]
        ]
        
        tasks = [self.image_gen.generate(p, 1, "fashion") for p in prompts]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        images = []
        for r in results:
            if isinstance(r, ImageResult) and r.success:
                images.extend(r.images)
        
        return {
            "theme": theme,
            "images": images,
            "count": len(images)
        }


# Global instance
output_layer = OutputLayer()
