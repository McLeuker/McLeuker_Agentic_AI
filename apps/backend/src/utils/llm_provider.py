"""
McLeuker Agentic AI Platform - LLM Provider Abstraction
Supports OpenAI (GPT-4) and Grok with a unified interface.
"""

import os
import json
from typing import Optional, Dict, Any, List, Union
from abc import ABC, abstractmethod
import httpx
from openai import OpenAI, AsyncOpenAI

from src.config.settings import get_settings


class LLMProvider(ABC):
    """Abstract base class for LLM providers."""
    
    @abstractmethod
    async def complete(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[str, Dict[str, str]]] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Generate a completion from the LLM."""
        pass
    
    @abstractmethod
    async def complete_with_structured_output(
        self,
        messages: List[Dict[str, str]],
        response_format: Dict[str, Any],
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Generate a completion with structured JSON output."""
        pass


class OpenAIProvider(LLMProvider):
    """OpenAI GPT-4 provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.OPENAI_API_KEY or os.getenv("OPENAI_API_KEY")
        self.model = model or settings.OPENAI_MODEL
        
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        self.client = AsyncOpenAI(api_key=self.api_key)
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[str, Dict[str, str]]] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Generate a completion using OpenAI."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if functions:
            # Convert to tools format for newer API
            tools = [{"type": "function", "function": f} for f in functions]
            kwargs["tools"] = tools
            if function_call:
                if isinstance(function_call, str):
                    if function_call == "auto":
                        kwargs["tool_choice"] = "auto"
                    elif function_call == "none":
                        kwargs["tool_choice"] = "none"
                    else:
                        kwargs["tool_choice"] = {"type": "function", "function": {"name": function_call}}
                else:
                    kwargs["tool_choice"] = {"type": "function", "function": function_call}
        
        response = await self.client.chat.completions.create(**kwargs)
        
        result = {
            "content": response.choices[0].message.content,
            "role": response.choices[0].message.role,
            "finish_reason": response.choices[0].finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }
        
        # Handle function/tool calls
        if response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            result["function_call"] = {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments
            }
        
        return result
    
    async def complete_with_structured_output(
        self,
        messages: List[Dict[str, str]],
        response_format: Dict[str, Any],
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Generate a completion with structured JSON output."""
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            response_format={"type": "json_object"}
        )
        
        content = response.choices[0].message.content
        try:
            parsed_content = json.loads(content)
        except json.JSONDecodeError:
            parsed_content = {"raw": content}
        
        return {
            "content": parsed_content,
            "role": response.choices[0].message.role,
            "finish_reason": response.choices[0].finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens
            }
        }


class GrokProvider(LLMProvider):
    """Grok (xAI) provider."""
    
    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        settings = get_settings()
        self.api_key = api_key or settings.GROK_API_KEY or os.getenv("GROK_API_KEY")
        self.model = model or settings.GROK_MODEL
        self.base_url = "https://api.x.ai/v1"
        
        if not self.api_key:
            raise ValueError("Grok API key is required")
        
        # Use OpenAI client with custom base URL for Grok
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
    
    async def complete(
        self,
        messages: List[Dict[str, str]],
        functions: Optional[List[Dict[str, Any]]] = None,
        function_call: Optional[Union[str, Dict[str, str]]] = None,
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Generate a completion using Grok."""
        kwargs = {
            "model": self.model,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        if functions:
            tools = [{"type": "function", "function": f} for f in functions]
            kwargs["tools"] = tools
            if function_call:
                if isinstance(function_call, str):
                    if function_call == "auto":
                        kwargs["tool_choice"] = "auto"
                    elif function_call == "none":
                        kwargs["tool_choice"] = "none"
                    else:
                        kwargs["tool_choice"] = {"type": "function", "function": {"name": function_call}}
                else:
                    kwargs["tool_choice"] = {"type": "function", "function": function_call}
        
        response = await self.client.chat.completions.create(**kwargs)
        
        result = {
            "content": response.choices[0].message.content,
            "role": response.choices[0].message.role,
            "finish_reason": response.choices[0].finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
        }
        
        if hasattr(response.choices[0].message, 'tool_calls') and response.choices[0].message.tool_calls:
            tool_call = response.choices[0].message.tool_calls[0]
            result["function_call"] = {
                "name": tool_call.function.name,
                "arguments": tool_call.function.arguments
            }
        
        return result
    
    async def complete_with_structured_output(
        self,
        messages: List[Dict[str, str]],
        response_format: Dict[str, Any],
        temperature: float = 0.1,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Generate a completion with structured JSON output."""
        # Add instruction for JSON output
        system_msg = messages[0] if messages and messages[0]["role"] == "system" else None
        if system_msg:
            system_msg["content"] += "\n\nYou must respond with valid JSON only."
        else:
            messages.insert(0, {
                "role": "system",
                "content": "You must respond with valid JSON only."
            })
        
        response = await self.client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens
        )
        
        content = response.choices[0].message.content
        try:
            # Try to extract JSON from the response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            parsed_content = json.loads(content)
        except json.JSONDecodeError:
            parsed_content = {"raw": content}
        
        return {
            "content": parsed_content,
            "role": response.choices[0].message.role,
            "finish_reason": response.choices[0].finish_reason,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
        }


class LLMFactory:
    """Factory for creating LLM providers."""
    
    _providers = {
        "openai": OpenAIProvider,
        "grok": GrokProvider
    }
    
    @classmethod
    def create(
        cls,
        provider: str = "openai",
        api_key: Optional[str] = None,
        model: Optional[str] = None
    ) -> LLMProvider:
        """Create an LLM provider instance."""
        if provider not in cls._providers:
            raise ValueError(f"Unknown provider: {provider}. Available: {list(cls._providers.keys())}")
        
        return cls._providers[provider](api_key=api_key, model=model)
    
    @classmethod
    def get_default(cls) -> LLMProvider:
        """Get the default LLM provider based on settings."""
        settings = get_settings()
        return cls.create(provider=settings.DEFAULT_LLM_PROVIDER)
