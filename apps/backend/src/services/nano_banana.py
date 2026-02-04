"""
Nano Banana Image Generation Service
=====================================
Integration with Google's Gemini API for image generation (Nano Banana Pro).
"""

import os
import base64
import httpx
import uuid
from typing import Optional, Dict, Any
from datetime import datetime


class NanoBananaService:
    """
    Nano Banana (Gemini) Image Generation Service
    
    Uses Google's Gemini API for:
    - Text-to-image generation
    - Image editing
    - Image analysis
    """
    
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY", os.getenv("NANO_BANANA_API_KEY", ""))
        self.base_url = "https://generativelanguage.googleapis.com/v1beta"
        # Use Gemini 2.0 Flash for image generation (Nano Banana)
        self.model = "gemini-2.0-flash-exp"
        self.image_model = "gemini-2.0-flash-exp-image-generation"
        
    async def generate_image(
        self,
        prompt: str,
        style: Optional[str] = None,
        aspect_ratio: str = "1:1"
    ) -> Dict[str, Any]:
        """
        Generate an image from a text prompt using Nano Banana.
        
        Args:
            prompt: Text description of the image to generate
            style: Optional style modifier (e.g., "photorealistic", "artistic", "minimalist")
            aspect_ratio: Image aspect ratio ("1:1", "16:9", "9:16", "4:3")
            
        Returns:
            Dict with image data (base64) and metadata
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Nano Banana API key not configured"
            }
        
        # Enhance prompt with style
        enhanced_prompt = prompt
        if style:
            enhanced_prompt = f"{prompt}. Style: {style}"
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                # Use Gemini's image generation endpoint
                response = await client.post(
                    f"{self.base_url}/models/{self.model}:generateContent",
                    params={"key": self.api_key},
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [{
                                "text": f"Generate a high-quality image: {enhanced_prompt}"
                            }]
                        }],
                        "generationConfig": {
                            "responseModalities": ["image", "text"],
                            "responseMimeType": "image/png"
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    # Extract image from response
                    if "candidates" in data and len(data["candidates"]) > 0:
                        candidate = data["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            for part in candidate["content"]["parts"]:
                                if "inlineData" in part:
                                    return {
                                        "success": True,
                                        "image_data": part["inlineData"]["data"],
                                        "mime_type": part["inlineData"].get("mimeType", "image/png"),
                                        "prompt": prompt,
                                        "timestamp": datetime.now().isoformat()
                                    }
                                elif "text" in part:
                                    # Model returned text instead of image
                                    return {
                                        "success": False,
                                        "error": "Model returned text instead of image",
                                        "text_response": part["text"]
                                    }
                    
                    return {
                        "success": False,
                        "error": "No image generated in response"
                    }
                else:
                    error_data = response.json() if response.content else {}
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}",
                        "details": error_data
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def edit_image(
        self,
        image_data: str,
        edit_prompt: str,
        mime_type: str = "image/png"
    ) -> Dict[str, Any]:
        """
        Edit an existing image using Nano Banana.
        
        Args:
            image_data: Base64 encoded image data
            edit_prompt: Description of the edit to make
            mime_type: MIME type of the image
            
        Returns:
            Dict with edited image data
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Nano Banana API key not configured"
            }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/models/{self.model}:generateContent",
                    params={"key": self.api_key},
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [
                                {
                                    "inlineData": {
                                        "mimeType": mime_type,
                                        "data": image_data
                                    }
                                },
                                {
                                    "text": f"Edit this image: {edit_prompt}"
                                }
                            ]
                        }],
                        "generationConfig": {
                            "responseModalities": ["image", "text"],
                            "responseMimeType": "image/png"
                        }
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "candidates" in data and len(data["candidates"]) > 0:
                        candidate = data["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            for part in candidate["content"]["parts"]:
                                if "inlineData" in part:
                                    return {
                                        "success": True,
                                        "image_data": part["inlineData"]["data"],
                                        "mime_type": part["inlineData"].get("mimeType", "image/png"),
                                        "edit_prompt": edit_prompt,
                                        "timestamp": datetime.now().isoformat()
                                    }
                    
                    return {
                        "success": False,
                        "error": "No edited image in response"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_image(
        self,
        image_data: str,
        question: str,
        mime_type: str = "image/png"
    ) -> Dict[str, Any]:
        """
        Analyze an image and answer questions about it.
        
        Args:
            image_data: Base64 encoded image data
            question: Question about the image
            mime_type: MIME type of the image
            
        Returns:
            Dict with analysis result
        """
        if not self.api_key:
            return {
                "success": False,
                "error": "Nano Banana API key not configured"
            }
        
        try:
            async with httpx.AsyncClient(timeout=60.0) as client:
                response = await client.post(
                    f"{self.base_url}/models/{self.model}:generateContent",
                    params={"key": self.api_key},
                    headers={"Content-Type": "application/json"},
                    json={
                        "contents": [{
                            "parts": [
                                {
                                    "inlineData": {
                                        "mimeType": mime_type,
                                        "data": image_data
                                    }
                                },
                                {
                                    "text": question
                                }
                            ]
                        }]
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if "candidates" in data and len(data["candidates"]) > 0:
                        candidate = data["candidates"][0]
                        if "content" in candidate and "parts" in candidate["content"]:
                            for part in candidate["content"]["parts"]:
                                if "text" in part:
                                    return {
                                        "success": True,
                                        "analysis": part["text"],
                                        "question": question,
                                        "timestamp": datetime.now().isoformat()
                                    }
                    
                    return {
                        "success": False,
                        "error": "No analysis in response"
                    }
                else:
                    return {
                        "success": False,
                        "error": f"API error: {response.status_code}"
                    }
                    
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# Singleton instance
nano_banana_service = NanoBananaService()
