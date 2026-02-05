"""
Kimi K2.5 Client for McLeuker AI
Moonshot AI integration for execution tasks and agentic workflows.

Features:
- OpenAI-compatible API
- 256K context window
- Tool calling support
- Streaming responses
- Cost tracking (97% cheaper than Grok)
"""

import asyncio
import json
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
import aiohttp
from datetime import datetime

from src.config.settings import settings


@dataclass
class KimiResponse:
    """Response from Kimi K2.5 model."""
    success: bool
    content: str
    reasoning: List[str]
    tool_calls: List[Dict] = None
    tokens_used: int = 0
    cost: float = 0.0
    model: str = "kimi-k2.5"
    error: Optional[str] = None


class KimiClient:
    """
    Client for Kimi K2.5 (Moonshot AI) - Execution Model
    
    Optimized for:
    - Code generation and execution
    - Tool calling and agentic workflows
    - Long-context tasks (256K tokens)
    - Cost-effective operations (97% cheaper than Grok)
    """
    
    # Pricing per 1M tokens (in USD)
    PRICING = {
        "kimi-k2.5": {"input": 0.002, "output": 0.006},  # $0.002/$0.006 per 1M tokens
        "kimi-k2-thinking": {"input": 0.002, "output": 0.006}
    }
    
    def __init__(self):
        self.api_key = settings.MOONSHOT_API_KEY
        self.api_base = settings.KIMI_API_BASE
        self.model = settings.KIMI_MODEL
        self.max_tokens = settings.KIMI_MAX_TOKENS
        self.timeout = settings.LLM_TIMEOUT
        
        if not self.api_key:
            raise ValueError("MOONSHOT_API_KEY not configured")
    
    async def execute(
        self,
        query: str,
        context: Optional[str] = None,
        tools: Optional[List[Dict]] = None,
        system_prompt: Optional[str] = None,
        temperature: float = 0.7,
        stream: bool = False
    ) -> KimiResponse:
        """
        Execute a query using Kimi K2.5.
        
        Args:
            query: The user query or task to execute
            context: Additional context (search results, previous steps)
            tools: List of tools available for the model to call
            system_prompt: Custom system prompt
            temperature: Sampling temperature (0-1)
            stream: Whether to stream the response
        
        Returns:
            KimiResponse with execution results
        """
        try:
            # Build messages
            messages = self._build_messages(query, context, system_prompt)
            
            # Prepare request payload
            payload = {
                "model": self.model,
                "messages": messages,
                "temperature": temperature,
                "max_tokens": self.max_tokens,
            }
            
            # Add tools if provided
            if tools:
                payload["tools"] = tools
                payload["tool_choice"] = "auto"
            
            # Make API request
            if stream:
                return await self._execute_stream(payload)
            else:
                return await self._execute_sync(payload)
        
        except Exception as e:
            return KimiResponse(
                success=False,
                content="",
                reasoning=[f"Error executing with Kimi: {str(e)}"],
                error=str(e)
            )
    
    async def _execute_sync(self, payload: Dict) -> KimiResponse:
        """Execute synchronous request."""
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    return KimiResponse(
                        success=False,
                        content="",
                        reasoning=[f"API error: {resp.status}"],
                        error=error_text
                    )
                
                data = await resp.json()
                return self._parse_response(data)
    
    async def _execute_stream(self, payload: Dict) -> AsyncGenerator[str, None]:
        """Execute streaming request."""
        payload["stream"] = True
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.api_base}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json=payload,
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            ) as resp:
                async for line in resp.content:
                    line = line.decode('utf-8').strip()
                    if line.startswith('data: '):
                        data = line[6:]
                        if data == '[DONE]':
                            break
                        try:
                            chunk = json.loads(data)
                            content = chunk.get('choices', [{}])[0].get('delta', {}).get('content', '')
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
    
    def _build_messages(
        self,
        query: str,
        context: Optional[str] = None,
        system_prompt: Optional[str] = None
    ) -> List[Dict]:
        """Build message array for API request."""
        messages = []
        
        # System prompt
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        else:
            messages.append({
                "role": "system",
                "content": self._get_default_system_prompt()
            })
        
        # Add context if provided
        if context:
            messages.append({
                "role": "user",
                "content": f"Context:\n{context}\n\nTask:\n{query}"
            })
        else:
            messages.append({
                "role": "user",
                "content": query
            })
        
        return messages
    
    def _get_default_system_prompt(self) -> str:
        """Get default system prompt for execution tasks."""
        return """You are Kimi K2.5, an advanced AI assistant specialized in execution and agentic workflows.

Your strengths:
- Code generation and debugging
- Tool calling and API integration
- Data analysis and processing
- Long-context understanding (256K tokens)
- Multi-step task execution

Focus on:
1. Precise execution of tasks
2. Using available tools effectively
3. Providing structured, actionable outputs
4. Handling complex multi-step workflows
5. Generating clean, production-ready code

Current domain: Fashion, Beauty, Lifestyle, and Sustainability intelligence."""
    
    def _parse_response(self, data: Dict) -> KimiResponse:
        """Parse API response into KimiResponse."""
        try:
            choice = data.get('choices', [{}])[0]
            message = choice.get('message', {})
            content = message.get('content', '')
            tool_calls = message.get('tool_calls', [])
            
            # Extract usage stats
            usage = data.get('usage', {})
            input_tokens = usage.get('prompt_tokens', 0)
            output_tokens = usage.get('completion_tokens', 0)
            total_tokens = usage.get('total_tokens', 0)
            
            # Calculate cost
            cost = self._calculate_cost(input_tokens, output_tokens)
            
            return KimiResponse(
                success=True,
                content=content,
                reasoning=[f"Executed with {self.model}"],
                tool_calls=tool_calls if tool_calls else None,
                tokens_used=total_tokens,
                cost=cost,
                model=self.model
            )
        
        except Exception as e:
            return KimiResponse(
                success=False,
                content="",
                reasoning=[f"Error parsing response: {str(e)}"],
                error=str(e)
            )
    
    def _calculate_cost(self, input_tokens: int, output_tokens: int) -> float:
        """Calculate cost based on token usage."""
        pricing = self.PRICING.get(self.model, self.PRICING["kimi-k2.5"])
        
        input_cost = (input_tokens / 1_000_000) * pricing["input"]
        output_cost = (output_tokens / 1_000_000) * pricing["output"]
        
        return input_cost + output_cost
    
    async def execute_with_tools(
        self,
        query: str,
        tools: List[Dict],
        context: Optional[str] = None,
        max_iterations: int = 5
    ) -> KimiResponse:
        """
        Execute a query with tool calling support.
        Handles multi-step agentic workflows.
        
        Args:
            query: The task to execute
            tools: Available tools for the model
            context: Additional context
            max_iterations: Maximum tool calling iterations
        
        Returns:
            Final KimiResponse after all tool calls
        """
        messages = self._build_messages(query, context)
        iteration = 0
        total_cost = 0.0
        reasoning_steps = []
        
        while iteration < max_iterations:
            # Execute with tools
            response = await self.execute(
                query=query,
                context=context,
                tools=tools,
                stream=False
            )
            
            total_cost += response.cost
            reasoning_steps.extend(response.reasoning)
            
            # Check if model wants to call tools
            if not response.tool_calls:
                # No more tool calls, return final response
                response.cost = total_cost
                response.reasoning = reasoning_steps
                return response
            
            # Execute tool calls
            for tool_call in response.tool_calls:
                tool_name = tool_call.get('function', {}).get('name')
                tool_args = json.loads(tool_call.get('function', {}).get('arguments', '{}'))
                
                reasoning_steps.append(f"Calling tool: {tool_name} with args: {tool_args}")
                
                # Here you would execute the actual tool
                # For now, we'll just log it
                # tool_result = await execute_tool(tool_name, tool_args)
            
            iteration += 1
        
        # Max iterations reached
        return KimiResponse(
            success=True,
            content=response.content,
            reasoning=reasoning_steps + ["Max iterations reached"],
            cost=total_cost,
            model=self.model
        )


# Global Kimi client instance
kimi_client = KimiClient() if settings.is_kimi_configured() else None
