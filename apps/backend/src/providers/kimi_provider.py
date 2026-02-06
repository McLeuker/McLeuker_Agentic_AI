"""
McLeuker AI - Kimi K2.5 Provider
================================
Integration with Moonshot AI's Kimi K2.5 model for:
- Tool calling and execution
- Multimodal understanding (images, videos)
- Long context processing (256K tokens)
- Thinking/reasoning mode support

API Reference: https://platform.moonshot.ai/docs
"""

import os
import json
import base64
from typing import Optional, Dict, Any, List, Union, AsyncGenerator
from dataclasses import dataclass
import httpx
from openai import AsyncOpenAI


@dataclass
class KimiToolCall:
    """Represents a tool call from Kimi"""
    id: str
    name: str
    arguments: Dict[str, Any]
    
    @classmethod
    def from_response(cls, tool_call) -> "KimiToolCall":
        return cls(
            id=tool_call.id,
            name=tool_call.function.name,
            arguments=json.loads(tool_call.function.arguments)
        )


@dataclass
class KimiResponse:
    """Response from Kimi K2.5"""
    content: Optional[str]
    reasoning_content: Optional[str]  # Thinking mode output
    tool_calls: List[KimiToolCall]
    finish_reason: str
    usage: Dict[str, int]
    
    def has_tool_calls(self) -> bool:
        return len(self.tool_calls) > 0


class KimiProvider:
    """
    Kimi K2.5 Provider for McLeuker AI.
    
    Features:
    - OpenAI-compatible API
    - Tool calling with up to 128 tools
    - Thinking mode for complex reasoning
    - Multimodal support (images, videos)
    - 256K context window
    """
    
    # Available Kimi models
    MODELS = {
        "kimi-k2.5": {
            "context_window": 262144,
            "supports_thinking": True,
            "supports_multimodal": True,
            "supports_tools": True
        },
        "kimi-k2-turbo-preview": {
            "context_window": 262144,
            "supports_thinking": True,
            "supports_multimodal": False,
            "supports_tools": True
        },
        "kimi-k2-thinking": {
            "context_window": 262144,
            "supports_thinking": True,
            "supports_multimodal": False,
            "supports_tools": True
        }
    }
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        model: str = "kimi-k2.5",
        base_url: str = "https://api.moonshot.ai/v1",
        thinking_enabled: bool = True
    ):
        self.api_key = api_key or os.getenv("KIMI_API_KEY")
        if not self.api_key:
            raise ValueError("Kimi API key is required. Set KIMI_API_KEY environment variable.")
        
        self.model = model
        self.base_url = base_url
        self.thinking_enabled = thinking_enabled
        
        # Initialize OpenAI-compatible client
        self.client = AsyncOpenAI(
            api_key=self.api_key,
            base_url=self.base_url
        )
        
        # Model capabilities
        self.capabilities = self.MODELS.get(model, self.MODELS["kimi-k2.5"])
    
    async def complete(
        self,
        messages: List[Dict[str, Any]],
        tools: Optional[List[Dict[str, Any]]] = None,
        tool_choice: str = "auto",
        max_tokens: int = 32768,
        stream: bool = False
    ) -> Union[KimiResponse, AsyncGenerator[Dict, None]]:
        """
        Generate a completion using Kimi K2.5.
        
        Args:
            messages: List of message dicts with role and content
            tools: Optional list of tool definitions
            tool_choice: "auto" or "none" (required when thinking enabled)
            max_tokens: Maximum tokens to generate (default 32K)
            stream: Whether to stream the response
            
        Returns:
            KimiResponse or async generator if streaming
        """
        kwargs = {
            "model": self.model,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        # Add thinking parameter
        if self.capabilities["supports_thinking"]:
            kwargs["extra_body"] = {
                "thinking": {"type": "enabled" if self.thinking_enabled else "disabled"}
            }
        
        # Add tools if provided
        if tools and self.capabilities["supports_tools"]:
            kwargs["tools"] = tools
            kwargs["tool_choice"] = tool_choice
        
        if stream:
            return self._stream_completion(**kwargs)
        else:
            return await self._complete(**kwargs)
    
    async def _complete(self, **kwargs) -> KimiResponse:
        """Non-streaming completion"""
        response = await self.client.chat.completions.create(**kwargs)
        
        message = response.choices[0].message
        
        # Extract tool calls
        tool_calls = []
        if hasattr(message, 'tool_calls') and message.tool_calls:
            tool_calls = [KimiToolCall.from_response(tc) for tc in message.tool_calls]
        
        # Extract reasoning content (from thinking mode)
        reasoning_content = None
        if hasattr(message, 'reasoning_content'):
            reasoning_content = message.reasoning_content
        
        return KimiResponse(
            content=message.content,
            reasoning_content=reasoning_content,
            tool_calls=tool_calls,
            finish_reason=response.choices[0].finish_reason,
            usage={
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0
            }
        )
    
    async def _stream_completion(self, **kwargs) -> AsyncGenerator[Dict, None]:
        """Streaming completion"""
        async with self.client.chat.completions.stream(**kwargs) as stream:
            async for chunk in stream:
                if chunk.choices and chunk.choices[0].delta:
                    delta = chunk.choices[0].delta
                    yield {
                        "type": "content",
                        "content": delta.content or "",
                        "tool_calls": delta.tool_calls if hasattr(delta, 'tool_calls') else None
                    }
    
    async def complete_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        tool_executor: callable,
        max_iterations: int = 10
    ) -> KimiResponse:
        """
        Complete with automatic tool execution loop.
        
        This implements the agentic pattern where Kimi can:
        1. Analyze the request
        2. Call tools as needed
        3. Process tool results
        4. Continue until task is complete
        
        Args:
            messages: Initial messages
            tools: Tool definitions
            tool_executor: Async function to execute tools
            max_iterations: Maximum tool call iterations
            
        Returns:
            Final KimiResponse after all tool calls
        """
        current_messages = messages.copy()
        iteration = 0
        
        while iteration < max_iterations:
            response = await self.complete(
                messages=current_messages,
                tools=tools,
                tool_choice="auto"
            )
            
            if not response.has_tool_calls():
                return response
            
            # Add assistant message with tool calls
            assistant_msg = {
                "role": "assistant",
                "content": response.content or "",
            }
            
            # Include reasoning_content if present (required for thinking mode)
            if response.reasoning_content:
                assistant_msg["reasoning_content"] = response.reasoning_content
            
            # Add tool calls to message
            assistant_msg["tool_calls"] = [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.name,
                        "arguments": json.dumps(tc.arguments)
                    }
                }
                for tc in response.tool_calls
            ]
            current_messages.append(assistant_msg)
            
            # Execute each tool call
            for tool_call in response.tool_calls:
                try:
                    result = await tool_executor(tool_call.name, tool_call.arguments)
                    tool_result = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps(result) if isinstance(result, dict) else str(result)
                    }
                except Exception as e:
                    tool_result = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "content": json.dumps({"error": str(e)})
                    }
                
                current_messages.append(tool_result)
            
            iteration += 1
        
        # Max iterations reached
        return await self.complete(
            messages=current_messages,
            tools=tools,
            tool_choice="none"  # Force final response
        )
    
    async def analyze_image(
        self,
        image_path: str,
        prompt: str,
        detail: str = "auto"
    ) -> KimiResponse:
        """
        Analyze an image using Kimi K2.5's vision capabilities.
        
        Args:
            image_path: Path to the image file
            prompt: Question or instruction about the image
            detail: Level of detail ("auto", "low", "high")
            
        Returns:
            KimiResponse with analysis
        """
        if not self.capabilities["supports_multimodal"]:
            raise ValueError(f"Model {self.model} does not support multimodal input")
        
        # Read and encode image
        with open(image_path, "rb") as f:
            image_data = f.read()
        
        # Determine image type from extension
        ext = os.path.splitext(image_path)[1].lower()
        mime_type = {
            ".png": "image/png",
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".webp": "image/webp",
            ".gif": "image/gif"
        }.get(ext, "image/png")
        
        image_url = f"data:{mime_type};base64,{base64.b64encode(image_data).decode('utf-8')}"
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
        
        return await self.complete(messages=messages)
    
    async def analyze_video(
        self,
        video_path: str,
        prompt: str
    ) -> KimiResponse:
        """
        Analyze a video using Kimi K2.5's vision capabilities.
        
        Args:
            video_path: Path to the video file
            prompt: Question or instruction about the video
            
        Returns:
            KimiResponse with analysis
        """
        if not self.capabilities["supports_multimodal"]:
            raise ValueError(f"Model {self.model} does not support multimodal input")
        
        # Read and encode video
        with open(video_path, "rb") as f:
            video_data = f.read()
        
        # Determine video type from extension
        ext = os.path.splitext(video_path)[1].lower()
        mime_type = {
            ".mp4": "video/mp4",
            ".mpeg": "video/mpeg",
            ".mov": "video/quicktime",
            ".avi": "video/x-msvideo",
            ".webm": "video/webm",
            ".wmv": "video/x-ms-wmv"
        }.get(ext, "video/mp4")
        
        video_url = f"data:{mime_type};base64,{base64.b64encode(video_data).decode('utf-8')}"
        
        messages = [
            {
                "role": "user",
                "content": [
                    {
                        "type": "video_url",
                        "video_url": {"url": video_url}
                    },
                    {
                        "type": "text",
                        "text": prompt
                    }
                ]
            }
        ]
        
        return await self.complete(messages=messages)
    
    def create_tool_definition(
        self,
        name: str,
        description: str,
        parameters: Dict[str, Any],
        required: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Helper to create a tool definition in the correct format.
        
        Args:
            name: Tool name (must match regex ^[a-zA-Z_][a-zA-Z0-9-_]{0,63}$)
            description: What the tool does
            parameters: Parameter definitions
            required: List of required parameter names
            
        Returns:
            Tool definition dict
        """
        tool_def = {
            "type": "function",
            "function": {
                "name": name,
                "description": description,
                "parameters": {
                    "type": "object",
                    "properties": parameters
                }
            }
        }
        
        if required:
            tool_def["function"]["parameters"]["required"] = required
        
        return tool_def


# Singleton instance
kimi_provider: Optional[KimiProvider] = None


def get_kimi_provider(
    api_key: Optional[str] = None,
    model: str = "kimi-k2.5",
    thinking_enabled: bool = True
) -> KimiProvider:
    """Get or create the Kimi provider singleton"""
    global kimi_provider
    
    if kimi_provider is None:
        kimi_provider = KimiProvider(
            api_key=api_key,
            model=model,
            thinking_enabled=thinking_enabled
        )
    
    return kimi_provider
