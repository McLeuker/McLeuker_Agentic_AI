"""
McLeuker Agentic AI Platform - Media Services

This module provides integrations for media services including:
- ElevenLabs (Text-to-Speech)
- Hugging Face (Various AI models)
"""

import asyncio
import os
from typing import Optional, Dict, Any, List
from datetime import datetime
import httpx

from src.config.settings import get_settings


class ElevenLabsService:
    """ElevenLabs Text-to-Speech service."""
    
    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.ELEVENLABS_API_KEY
        self.base_url = "https://api.elevenlabs.io/v1"
        
        # Default voice IDs
        self.voices = {
            "rachel": "21m00Tcm4TlvDq8ikWAM",  # Female, American
            "drew": "29vD33N1CtxCmqQRPOHJ",     # Male, American
            "clyde": "2EiwWnXFnvU5JabPnv8n",   # Male, American
            "paul": "5Q0t7uMcjvnagumLfvZi",    # Male, American
            "domi": "AZnzlk1XvdvUeBnXmlld",    # Female, American
            "bella": "EXAVITQu4vr4xnSDxMaL",   # Female, American
            "antoni": "ErXwobaYiN019PkySvjV",  # Male, American
            "elli": "MF3mGyEYCl7XYWbV9V6O",    # Female, American
            "josh": "TxGEqnHWrfWFTfGW9XjX",    # Male, American
            "arnold": "VR6AewLTigWG4xSOukaG",  # Male, American
            "adam": "pNInz6obpgDQGcFmaJgB",    # Male, American
            "sam": "yoZ06aMxZJJ28mfd3POQ",     # Male, American
        }
    
    async def get_voices(self) -> List[Dict[str, Any]]:
        """Get available voices."""
        if not self.api_key:
            return []
        
        headers = {
            "xi-api-key": self.api_key
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/voices",
                    headers=headers,
                    timeout=30.0
                )
                response.raise_for_status()
                data = response.json()
                return data.get("voices", [])
            except Exception as e:
                print(f"ElevenLabs get voices error: {e}")
                return []
    
    async def text_to_speech(
        self,
        text: str,
        voice_id: Optional[str] = None,
        voice_name: Optional[str] = None,
        model_id: str = "eleven_monolingual_v1",
        output_path: Optional[str] = None
    ) -> Optional[bytes]:
        """
        Convert text to speech.
        
        Args:
            text: The text to convert
            voice_id: The voice ID to use
            voice_name: The voice name (will be converted to ID)
            model_id: The model to use
            output_path: Optional path to save the audio file
            
        Returns:
            Audio bytes or None if failed
        """
        if not self.api_key:
            print("ElevenLabs API key not configured")
            return None
        
        # Resolve voice ID
        if voice_name and voice_name.lower() in self.voices:
            voice_id = self.voices[voice_name.lower()]
        elif not voice_id:
            voice_id = self.voices["rachel"]  # Default voice
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/text-to-speech/{voice_id}",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                )
                response.raise_for_status()
                
                audio_bytes = response.content
                
                # Save to file if path provided
                if output_path:
                    os.makedirs(os.path.dirname(output_path), exist_ok=True)
                    with open(output_path, "wb") as f:
                        f.write(audio_bytes)
                
                return audio_bytes
            except Exception as e:
                print(f"ElevenLabs TTS error: {e}")
                return None
    
    async def text_to_speech_stream(
        self,
        text: str,
        voice_id: Optional[str] = None,
        voice_name: Optional[str] = None,
        model_id: str = "eleven_monolingual_v1"
    ):
        """
        Stream text to speech audio.
        
        Yields audio chunks as they are generated.
        """
        if not self.api_key:
            return
        
        # Resolve voice ID
        if voice_name and voice_name.lower() in self.voices:
            voice_id = self.voices[voice_name.lower()]
        elif not voice_id:
            voice_id = self.voices["rachel"]
        
        headers = {
            "xi-api-key": self.api_key,
            "Content-Type": "application/json"
        }
        
        payload = {
            "text": text,
            "model_id": model_id,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75
            }
        }
        
        async with httpx.AsyncClient() as client:
            try:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/text-to-speech/{voice_id}/stream",
                    headers=headers,
                    json=payload,
                    timeout=60.0
                ) as response:
                    response.raise_for_status()
                    async for chunk in response.aiter_bytes():
                        yield chunk
            except Exception as e:
                print(f"ElevenLabs TTS stream error: {e}")


class HuggingFaceService:
    """Hugging Face Inference API service."""
    
    def __init__(self, api_key: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.HUGGINGFACE_API_KEY
        self.base_url = "https://api-inference.huggingface.co/models"
    
    async def inference(
        self,
        model_id: str,
        inputs: Any,
        parameters: Optional[Dict[str, Any]] = None
    ) -> Optional[Any]:
        """
        Run inference on a Hugging Face model.
        
        Args:
            model_id: The model ID (e.g., "facebook/bart-large-cnn")
            inputs: The input data
            parameters: Optional model parameters
            
        Returns:
            Model output or None if failed
        """
        if not self.api_key:
            print("Hugging Face API key not configured")
            return None
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        payload = {"inputs": inputs}
        if parameters:
            payload["parameters"] = parameters
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.post(
                    f"{self.base_url}/{model_id}",
                    headers=headers,
                    json=payload,
                    timeout=120.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                print(f"Hugging Face inference error: {e}")
                return None
    
    async def summarize(
        self,
        text: str,
        model_id: str = "facebook/bart-large-cnn",
        max_length: int = 150,
        min_length: int = 30
    ) -> Optional[str]:
        """Summarize text using a summarization model."""
        result = await self.inference(
            model_id=model_id,
            inputs=text,
            parameters={
                "max_length": max_length,
                "min_length": min_length,
                "do_sample": False
            }
        )
        
        if result and isinstance(result, list) and len(result) > 0:
            return result[0].get("summary_text", "")
        return None
    
    async def generate_text(
        self,
        prompt: str,
        model_id: str = "gpt2",
        max_new_tokens: int = 100,
        temperature: float = 0.7
    ) -> Optional[str]:
        """Generate text using a text generation model."""
        result = await self.inference(
            model_id=model_id,
            inputs=prompt,
            parameters={
                "max_new_tokens": max_new_tokens,
                "temperature": temperature,
                "do_sample": True
            }
        )
        
        if result and isinstance(result, list) and len(result) > 0:
            return result[0].get("generated_text", "")
        return None
    
    async def classify_text(
        self,
        text: str,
        model_id: str = "facebook/bart-large-mnli",
        candidate_labels: List[str] = None
    ) -> Optional[Dict[str, Any]]:
        """Classify text using a zero-shot classification model."""
        if candidate_labels is None:
            candidate_labels = ["positive", "negative", "neutral"]
        
        result = await self.inference(
            model_id=model_id,
            inputs=text,
            parameters={
                "candidate_labels": candidate_labels
            }
        )
        
        return result
    
    async def embed_text(
        self,
        text: str,
        model_id: str = "sentence-transformers/all-MiniLM-L6-v2"
    ) -> Optional[List[float]]:
        """Generate text embeddings."""
        result = await self.inference(
            model_id=model_id,
            inputs=text
        )
        
        if result and isinstance(result, list):
            return result
        return None


# Convenience functions
async def text_to_speech(
    text: str,
    voice_name: str = "rachel",
    output_path: Optional[str] = None
) -> Optional[bytes]:
    """Convert text to speech using ElevenLabs."""
    service = ElevenLabsService()
    return await service.text_to_speech(text, voice_name=voice_name, output_path=output_path)


async def summarize_text(text: str) -> Optional[str]:
    """Summarize text using Hugging Face."""
    service = HuggingFaceService()
    return await service.summarize(text)
