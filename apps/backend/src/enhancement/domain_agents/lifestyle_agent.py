"""
Lifestyle Agent - Lifestyle & Wellness Intelligence
====================================================

Analyzes lifestyle aspects:
- Lifestyle trends
- Wellness integration
- Consumer behavior
- Living aesthetics
- Daily rituals
"""

import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class LifestyleTrend:
    """Lifestyle trend profile"""
    trend_name: str
    category: str
    description: str
    key_elements: List[str] = field(default_factory=list)
    target_audience: str = ""
    adoption_stage: str = ""
    related_products: List[str] = field(default_factory=list)


@dataclass
class WellnessIntegration:
    """Wellness integration profile"""
    practice: str
    benefits: List[str] = field(default_factory=list)
    how_to_integrate: str = ""
    time_commitment: str = ""
    cost_considerations: str = ""


class LifestyleAgent:
    """Specialized agent for lifestyle analysis"""
    
    LIFESTYLE_CATEGORIES = [
        "wellness", "minimalism", "slow_living", "conscious_consumption",
        "digital_wellness", "work_life_balance", "self_care", "mindfulness"
    ]
    
    def __init__(self, llm_client, search_tools=None):
        self.llm_client = llm_client
        self.search_tools = search_tools
    
    async def analyze(
        self,
        query: str,
        context: Optional[Dict] = None,
        images: Optional[List[str]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Main analysis entry point"""
        
        yield {"type": "status", "message": "Lifestyle Agent initializing..."}
        
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["trend", "trending", "popular", "movement"]):
            async for event in self._analyze_lifestyle_trend(query, context):
                yield event
        elif any(kw in query_lower for kw in ["wellness", "health", "self-care", "mindfulness"]):
            async for event in self._analyze_wellness(query, context):
                yield event
        elif any(kw in query_lower for kw in ["consumer", "behavior", "buying", "shopping"]):
            async for event in self._analyze_consumer_behavior(query, context):
                yield event
        elif any(kw in query_lower for kw in ["aesthetic", "style", "look", "vibe", "home"]):
            async for event in self._analyze_aesthetic(query, context):
                yield event
        else:
            async for event in self._general_lifestyle_analysis(query, context):
                yield event
    
    async def _analyze_lifestyle_trend(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze a lifestyle trend"""
        
        yield {"type": "status", "message": "Analyzing lifestyle trend..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} lifestyle trend 2025",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a lifestyle trends expert. Analyze current trends.

Respond in JSON format with:
{
    "trend_name": "...",
    "category": "...",
    "description": "...",
    "origins": "...",
    "key_elements": ["..."],
    "target_demographic": "...",
    "adoption_stage": "...",
    "driving_factors": ["..."],
    "related_products_services": ["..."],
    "fashion_connection": "...",
    "predicted_longevity": "...",
    "regional_variations": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze lifestyle trend: {query}\n\nResearch: {json.dumps(search_results[:5], indent=2)}"}
        ]
        
        try:
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            yield {"type": "lifestyle_trend", "data": analysis}
            
        except Exception as e:
            logger.error(f"Trend analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _analyze_wellness(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze wellness practices"""
        
        yield {"type": "status", "message": "Analyzing wellness practices..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} wellness lifestyle integration",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a wellness lifestyle expert. Analyze wellness integration.

Respond in JSON format with:
{
    "wellness_practice": "...",
    "description": "...",
    "proven_benefits": ["..."],
    "how_to_integrate": "...",
    "daily_routine_suggestions": ["..."],
    "products_that_support": ["..."],
    "fashion_wellness_connection": "...",
    "time_commitment": "...",
    "cost_considerations": "...",
    "beginner_tips": ["..."],
    "resources": ["..."]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze wellness: {query}\n\nResearch: {json.dumps(search_results[:5], indent=2)}"}
        ]
        
        try:
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            yield {"type": "wellness_analysis", "data": analysis}
            
        except Exception as e:
            logger.error(f"Wellness analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _analyze_consumer_behavior(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze consumer behavior"""
        
        yield {"type": "status", "message": "Analyzing consumer behavior..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} consumer behavior fashion lifestyle",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a consumer behavior expert. Analyze lifestyle consumers.

Respond in JSON format with:
{
    "consumer_segment": "...",
    "motivations": ["..."],
    "purchasing_patterns": "...",
    "brand_preferences": ["..."],
    "media_consumption": "...",
    "values_priorities": ["..."],
    "pain_points": ["..."],
    "marketing_approaches": ["..."]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze consumer behavior: {query}\n\nResearch: {json.dumps(search_results[:5], indent=2)}"}
        ]
        
        try:
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            yield {"type": "consumer_behavior", "data": analysis}
            
        except Exception as e:
            logger.error(f"Consumer behavior analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _analyze_aesthetic(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze lifestyle aesthetic"""
        
        yield {"type": "status", "message": "Analyzing lifestyle aesthetic..."}
        
        system_prompt = """You are a lifestyle aesthetic expert. Analyze living aesthetics.

Respond in JSON format with:
{
    "aesthetic_name": "...",
    "description": "...",
    "key_visual_elements": ["..."],
    "color_palette": ["..."],
    "essential_items": ["..."],
    "fashion_connection": "...",
    "home_decor_elements": ["..."],
    "daily_rituals": ["..."],
    "philosophy": "...",
    "how_to_achieve": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze aesthetic: {query}"}
        ]
        
        try:
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            yield {"type": "aesthetic_analysis", "data": analysis}
            
        except Exception as e:
            logger.error(f"Aesthetic analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _general_lifestyle_analysis(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """General lifestyle analysis"""
        
        yield {"type": "status", "message": "Analyzing lifestyle topic..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"lifestyle {query}",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a lifestyle expert. Provide comprehensive analysis.
Respond in JSON format with:
{
    "topic": "...",
    "summary": "...",
    "key_insights": ["..."],
    "practical_applications": ["..."],
    "trend_forecast": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze: {query}\n\nResearch: {json.dumps(search_results[:5], indent=2)}"}
        ]
        
        try:
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=3000,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            yield {"type": "general_analysis", "data": analysis}
            
        except Exception as e:
            logger.error(f"General analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
