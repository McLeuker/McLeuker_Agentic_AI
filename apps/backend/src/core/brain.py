"""
McLeuker AI V5 - Brain Module (Grok Integration)
The unified reasoning engine powered by Grok with proper error handling and fallbacks.

Design Principles:
1. NEVER ask for clarification unless absolutely critical
2. ALWAYS provide a response, even if partial
3. Use Grok as the reasoning brain, not a classifier
4. Implement proper streaming for real-time feedback
5. Graceful fallbacks on errors
"""

import asyncio
import json
import aiohttp
from typing import Dict, List, Optional, Any, AsyncGenerator
from datetime import datetime
from dataclasses import dataclass

from src.config.settings import settings


@dataclass
class BrainResponse:
    """Response from the Brain module."""
    success: bool
    content: str
    reasoning: List[str]
    error: Optional[str] = None
    tokens_used: int = 0


class GrokBrain:
    """
    The unified Grok-powered reasoning engine.
    Implements the Think-Act-Observe pattern without excessive clarification.
    """
    
    # System prompt that defines the AI's behavior
    SYSTEM_PROMPT = """You are McLeuker AI, a frontier AI assistant specializing in Fashion, Beauty, Lifestyle, and Culture.

CURRENT DATE: {current_date}

CORE PRINCIPLES:
1. NEVER ask for clarification unless the query is completely unintelligible
2. ALWAYS provide a helpful response, even if you need to make reasonable assumptions
3. If a query is vague, interpret it in the most useful way and proceed
4. For fashion/beauty queries, assume the user wants current trends unless specified
5. Be confident and direct in your responses

RESPONSE FORMAT:
- Start with a direct answer to the question
- Use clear sections with headers when appropriate
- Include specific examples, brands, or trends when relevant
- Add citations in [1], [2] format when using search results
- End with actionable insights or follow-up suggestions

DOMAIN EXPERTISE:
- Fashion & Catwalks (runway trends, designer collections)
- Beauty & Skincare (products, routines, ingredients)
- Textile & Sustainability (materials, eco-fashion)
- Lifestyle & Culture (trends, movements, influences)
- Tech & Innovation (fashion tech, AI in beauty)

IMPORTANT: You have access to real-time search results. Use them to provide accurate, up-to-date information.
When search results are provided, synthesize them into a coherent response with proper citations."""

    def __init__(self):
        self.api_key = settings.XAI_API_KEY
        self.model = settings.GROK_MODEL
        self.base_url = settings.GROK_API_BASE
        self.timeout = settings.LLM_TIMEOUT
        self.max_tokens = settings.LLM_MAX_TOKENS
    
    def _get_system_prompt(self) -> str:
        """Get the system prompt with current date."""
        current_date = datetime.now().strftime("%B %d, %Y")
        return self.SYSTEM_PROMPT.format(current_date=current_date)
    
    async def think(
        self,
        query: str,
        context: Optional[str] = None,
        search_results: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict]] = None,
        temperature: float = 0.7
    ) -> BrainResponse:
        """
        Execute a reasoning step using Grok.
        
        Args:
            query: The user's question or request
            context: Additional context for the query
            search_results: Results from search layer
            conversation_history: Previous messages in the conversation
            temperature: Creativity level (0.0-1.0)
        
        Returns:
            BrainResponse with the generated content
        """
        if not self.api_key:
            return BrainResponse(
                success=False,
                content="I apologize, but I'm currently unable to process requests. Please try again later.",
                reasoning=["Grok API key not configured"],
                error="API_KEY_MISSING"
            )
        
        # Build the messages array
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        
        # Add conversation history (limited to last N messages)
        if conversation_history:
            for msg in conversation_history[-settings.MAX_CONVERSATION_HISTORY:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        # Build the user prompt with context and search results
        user_prompt = self._build_user_prompt(query, context, search_results)
        messages.append({"role": "user", "content": user_prompt})
        
        reasoning_steps = ["Analyzing query", "Preparing response"]
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": self.max_tokens
                    },
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        return BrainResponse(
                            success=False,
                            content=self._get_fallback_response(query),
                            reasoning=reasoning_steps + [f"API error: {resp.status}"],
                            error=f"API_ERROR_{resp.status}"
                        )
                    
                    data = await resp.json()
                    content = data["choices"][0]["message"]["content"]
                    tokens_used = data.get("usage", {}).get("total_tokens", 0)
                    
                    reasoning_steps.append("Response generated successfully")
                    
                    return BrainResponse(
                        success=True,
                        content=content,
                        reasoning=reasoning_steps,
                        tokens_used=tokens_used
                    )
        
        except asyncio.TimeoutError:
            return BrainResponse(
                success=False,
                content=self._get_fallback_response(query),
                reasoning=reasoning_steps + ["Request timed out"],
                error="TIMEOUT"
            )
        except Exception as e:
            return BrainResponse(
                success=False,
                content=self._get_fallback_response(query),
                reasoning=reasoning_steps + [f"Error: {str(e)}"],
                error=str(e)
            )
    
    async def think_stream(
        self,
        query: str,
        context: Optional[str] = None,
        search_results: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict]] = None,
        temperature: float = 0.7
    ) -> AsyncGenerator[str, None]:
        """
        Execute a reasoning step with streaming response.
        Yields chunks of the response as they're generated.
        """
        if not self.api_key:
            yield "I apologize, but I'm currently unable to process requests."
            return
        
        messages = [{"role": "system", "content": self._get_system_prompt()}]
        
        if conversation_history:
            for msg in conversation_history[-settings.MAX_CONVERSATION_HISTORY:]:
                messages.append({
                    "role": msg.get("role", "user"),
                    "content": msg.get("content", "")
                })
        
        user_prompt = self._build_user_prompt(query, context, search_results)
        messages.append({"role": "user", "content": user_prompt})
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    f"{self.base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": temperature,
                        "max_tokens": self.max_tokens,
                        "stream": True
                    },
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as resp:
                    if resp.status != 200:
                        yield self._get_fallback_response(query)
                        return
                    
                    async for line in resp.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data = line[6:]
                            if data == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data)
                                delta = chunk.get("choices", [{}])[0].get("delta", {})
                                content = delta.get("content", "")
                                if content:
                                    yield content
                            except json.JSONDecodeError:
                                continue
        
        except Exception as e:
            yield self._get_fallback_response(query)
    
    def _build_user_prompt(
        self,
        query: str,
        context: Optional[str],
        search_results: Optional[List[Dict]]
    ) -> str:
        """Build the user prompt with context and search results."""
        prompt_parts = []
        
        # Add context if provided
        if context:
            prompt_parts.append(f"Context: {context}")
        
        # Add search results if provided
        if search_results:
            prompt_parts.append("\n--- SEARCH RESULTS ---")
            for i, result in enumerate(search_results[:10], 1):
                title = result.get("title", "Unknown")
                url = result.get("url", "")
                snippet = result.get("snippet", "")[:300]
                prompt_parts.append(f"[{i}] {title}")
                if url:
                    prompt_parts.append(f"    URL: {url}")
                if snippet:
                    prompt_parts.append(f"    {snippet}")
            prompt_parts.append("--- END SEARCH RESULTS ---\n")
            prompt_parts.append("Use the above search results to provide an accurate, well-cited response.")
        
        # Add the main query
        prompt_parts.append(f"\nUser Query: {query}")
        
        return "\n".join(prompt_parts)
    
    def _get_fallback_response(self, query: str) -> str:
        """Generate a fallback response when the main request fails."""
        return f"""I apologize, but I encountered an issue while processing your request about "{query[:100]}...".

Here's what I can tell you based on my knowledge:

For fashion and beauty queries, I recommend:
1. Checking trusted sources like Vogue, WWD, or Business of Fashion
2. Following industry experts on social media for real-time trends
3. Exploring brand websites for the latest collections

Please try your query again in a moment, or rephrase it for better results."""


# Global brain instance
brain = GrokBrain()
