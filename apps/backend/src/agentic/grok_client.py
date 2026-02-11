"""
Grok Client for Real-Time Data and Verification
================================================

Adapted for McLeuker AI backend. Provides:
- Real-time X/Twitter data access
- Fact verification and cross-checking
- Trending topic detection
- Fallback handling for primary LLM

Uses the sync OpenAI client with run_in_executor for async compatibility.
"""

import openai
import os
import json
import asyncio
import functools
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


@dataclass
class GrokResponse:
    """Structured response from Grok"""
    content: str
    realtime_data: bool = False
    sources: Optional[List[Dict]] = None
    usage: Optional[Dict] = None
    latency_ms: Optional[float] = None


@dataclass
class FactCheckResult:
    """Result of fact verification"""
    claim: str
    verdict: str  # "verified", "partially_verified", "unverified", "false"
    confidence: float  # 0.0 to 1.0
    explanation: str
    sources: List[Dict]
    checked_at: datetime


class GrokClient:
    """
    Grok client for real-time data and verification.

    Features:
    - Real-time X/Twitter search
    - Web search with current data
    - Fact verification against multiple sources
    - Trending topic analysis
    - Fallback completion when primary LLM fails
    """

    MODEL = "grok-3-mini"
    API_BASE = "https://api.x.ai/v1"

    def __init__(self, api_key: Optional[str] = None, client: Optional[openai.OpenAI] = None):
        """
        Initialize Grok client.

        Args:
            api_key: xAI API key. Falls back to GROK_API_KEY env var.
            client: Optional pre-existing sync OpenAI client (reuse from main.py).
        """
        if client:
            self.client = client
        else:
            self.api_key = api_key or os.getenv("GROK_API_KEY", "")
            if not self.api_key:
                logger.warning("Grok API key not set – GrokClient will be non-functional")
                self.client = None
                return
            self.client = openai.OpenAI(api_key=self.api_key, base_url=self.API_BASE)

        logger.info("Grok client initialized")

    # ------------------------------------------------------------------
    # Core chat
    # ------------------------------------------------------------------

    async def chat(
        self,
        messages: List[Dict[str, Any]],
        temperature: float = 0.5,
        max_tokens: Optional[int] = None,
        tools: Optional[List[Dict]] = None,
    ) -> GrokResponse:
        """Send chat request to Grok."""
        if not self.client:
            return GrokResponse(content="Grok client not available")

        start_time = datetime.now()

        params: Dict[str, Any] = {
            "model": self.MODEL,
            "messages": messages,
            "temperature": temperature,
        }
        if max_tokens:
            params["max_tokens"] = max_tokens
        else:
            params["max_tokens"] = 16384

        try:
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None, functools.partial(self.client.chat.completions.create, **params)
            )

            latency = (datetime.now() - start_time).total_seconds() * 1000
            message = response.choices[0].message
            realtime_data = any(kw in (message.content or "") for kw in ["x.com", "twitter.com", "trending"])

            return GrokResponse(
                content=message.content or "",
                realtime_data=realtime_data,
                usage={
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                } if response.usage else None,
                latency_ms=latency,
            )

        except Exception as e:
            logger.error(f"Grok API error: {e}")
            return GrokResponse(
                content=f"Grok API error: {str(e)}",
                latency_ms=(datetime.now() - start_time).total_seconds() * 1000,
            )

    # ------------------------------------------------------------------
    # Real-time context
    # ------------------------------------------------------------------

    async def get_realtime_context(
        self,
        query: str,
        include_x_posts: bool = True,
        include_web: bool = True,
        max_sources: int = 10,
    ) -> Dict[str, Any]:
        """Get real-time context from X/Twitter and web."""

        system_prompt = """You are a real-time information specialist with access to X (Twitter) and web search.

Your task is to provide the most current information available. Be explicit about:
1. What information is confirmed vs. speculative
2. The recency of the data (timestamps when available)
3. Source credibility

Format your response as JSON:
{
    "summary": "brief summary of findings",
    "key_points": ["list of key facts"],
    "sources": [
        {
            "title": "source title",
            "url": "source url",
            "type": "x_post|web|news",
            "timestamp": "ISO timestamp if available",
            "credibility": "high|medium|low"
        }
    ],
    "trending": ["related trending topics"],
    "confidence": "high|medium|low"
}"""

        sources_str = []
        if include_x_posts:
            sources_str.append("X/Twitter posts")
        if include_web:
            sources_str.append("web sources")

        user_prompt = f"""Query: {query}

Search for real-time information from {', '.join(sources_str)}.
Return up to {max_sources} most relevant and recent sources.

Focus on:
- Breaking news and recent developments
- Official announcements
- Verified accounts when relevant
- Cross-referenced facts"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = await self.chat(messages=messages, temperature=0.5)

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            result = json.loads(content.strip())
            result["latency_ms"] = response.latency_ms
            result["realtime_data"] = response.realtime_data
            return result

        except json.JSONDecodeError:
            return {
                "summary": response.content,
                "key_points": [],
                "sources": [],
                "trending": [],
                "confidence": "unknown",
                "latency_ms": response.latency_ms,
                "realtime_data": response.realtime_data,
            }

    # ------------------------------------------------------------------
    # Fact verification
    # ------------------------------------------------------------------

    async def verify_facts(
        self,
        claims: List[str],
        include_explanations: bool = True,
    ) -> List[FactCheckResult]:
        """Verify a list of claims against real-time data."""

        system_prompt = """You are a fact-checking specialist with access to real-time data.

For each claim, determine:
- verdict: "verified" | "partially_verified" | "unverified" | "false"
- confidence: 0.0 to 1.0
- explanation: Brief explanation of your findings
- sources: Supporting or contradicting sources

Respond in JSON format:
{
    "results": [
        {
            "claim": "original claim",
            "verdict": "verified|partially_verified|unverified|false",
            "confidence": 0.95,
            "explanation": "detailed explanation",
            "sources": [
                {"title": "...", "url": "...", "supports": true}
            ]
        }
    ]
}"""

        user_prompt = f"""Verify the following claims using current data:

{chr(10).join(f"{i+1}. {claim}" for i, claim in enumerate(claims))}

Search for authoritative sources and cross-reference information."""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = await self.chat(messages=messages, temperature=0.3)

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]

            data = json.loads(content.strip())

            results = []
            for rd in data.get("results", []):
                results.append(FactCheckResult(
                    claim=rd.get("claim", ""),
                    verdict=rd.get("verdict", "unverified"),
                    confidence=rd.get("confidence", 0.0),
                    explanation=rd.get("explanation", ""),
                    sources=rd.get("sources", []),
                    checked_at=datetime.now(),
                ))
            return results

        except json.JSONDecodeError:
            return [
                FactCheckResult(
                    claim=claim,
                    verdict="unverified",
                    confidence=0.0,
                    explanation="Failed to parse verification response",
                    sources=[],
                    checked_at=datetime.now(),
                )
                for claim in claims
            ]

    # ------------------------------------------------------------------
    # Trending topics
    # ------------------------------------------------------------------

    async def get_trending_topics(
        self,
        category: Optional[str] = None,
        location: Optional[str] = None,
        limit: int = 10,
    ) -> Dict[str, Any]:
        """Get trending topics from X/Twitter."""

        system_prompt = """You are a trending topics analyst with access to X (Twitter).

Identify current trending topics with:
- Topic name
- Volume/engagement level
- Key hashtags
- Brief description

Respond in JSON format:
{
    "trends": [
        {
            "topic": "topic name",
            "volume": "high|medium|low",
            "hashtags": ["#tag1", "#tag2"],
            "description": "brief description"
        }
    ],
    "timestamp": "ISO timestamp"
}"""

        filters = []
        if category:
            filters.append(f"category: {category}")
        if location:
            filters.append(f"location: {location}")
        filter_str = f" ({', '.join(filters)})" if filters else ""

        user_prompt = f"What are the top {limit} trending topics on X/Twitter right now{filter_str}?"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]

        response = await self.chat(messages=messages, temperature=0.5)

        try:
            content = response.content
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0]
            elif "```" in content:
                content = content.split("```")[1].split("```")[0]
            result = json.loads(content.strip())
            result["latency_ms"] = response.latency_ms
            return result
        except json.JSONDecodeError:
            return {
                "trends": [],
                "timestamp": datetime.now().isoformat(),
                "error": "Failed to parse trending topics",
                "raw_response": response.content,
            }

    # ------------------------------------------------------------------
    # Fallback completion
    # ------------------------------------------------------------------

    async def fallback_completion(
        self,
        messages: List[Dict[str, Any]],
        primary_error: str,
        temperature: float = 0.7,
    ) -> GrokResponse:
        """Fallback completion when primary LLM fails."""
        logger.warning(f"Falling back to Grok. Primary error: {primary_error}")
        fallback_messages = messages.copy()
        fallback_messages.append({
            "role": "system",
            "content": f"Note: The primary AI model encountered an error ({primary_error}). You are the fallback model. Please provide the best response possible.",
        })
        return await self.chat(messages=fallback_messages, temperature=temperature)
