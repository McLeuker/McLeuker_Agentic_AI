"""
Culture Agent - Fashion Culture & Context Intelligence
=======================================================

Analyzes cultural aspects of fashion:
- Historical context
- Cultural influences
- Social impact
- Subcultures
- Fashion movements
"""

import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class CulturalContext:
    """Cultural context analysis"""
    era_period: str
    cultural_movement: str
    social_factors: List[str] = field(default_factory=list)
    key_figures: List[str] = field(default_factory=list)
    influence_on_fashion: str = ""
    lasting_impact: str = ""


@dataclass
class SubcultureStyle:
    """Subculture style analysis"""
    name: str
    origin: str
    era: str
    key_elements: List[str] = field(default_factory=list)
    iconic_pieces: List[str] = field(default_factory=list)
    cultural_significance: str = ""
    evolution: str = ""


class CultureAgent:
    """Specialized agent for fashion culture and context analysis"""
    
    FASHION_ERAS = [
        "1920s_flapper", "1950s_new_look", "1960s_mod", "1970s_punk",
        "1980s_power_dressing", "1990s_minimalism", "2000s_streetwear"
    ]
    
    SUBCULTURES = [
        "punk", "goth", "hip_hop", "grunge", "rave", "normcore",
        "streetwear", "hypebeast", "cottagecore", "dark_academia"
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
        
        yield {"type": "status", "message": "Culture Agent initializing..."}
        
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["history", "era", "period", "decade", "1920s", "1960s"]):
            async for event in self._analyze_historical_context(query, context):
                yield event
        elif any(kw in query_lower for kw in ["subculture", "punk", "goth", "hip hop", "grunge"]):
            async for event in self._analyze_subculture(query, context):
                yield event
        elif any(kw in query_lower for kw in ["cultural", "influence", "movement", "revolution"]):
            async for event in self._analyze_cultural_movement(query, context):
                yield event
        elif any(kw in query_lower for kw in ["social", "impact", "society", "identity"]):
            async for event in self._analyze_social_impact(query, context):
                yield event
        else:
            async for event in self._general_cultural_analysis(query, context):
                yield event
    
    async def _analyze_historical_context(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze historical fashion context"""
        
        yield {"type": "status", "message": "Analyzing historical context..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} fashion history era",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a fashion historian. Analyze the historical context.

Respond in JSON format with:
{
    "era_period": "...",
    "historical_context": "...",
    "social_climate": "...",
    "key_fashion_elements": ["..."],
    "iconic_designers": ["..."],
    "influential_figures": ["..."],
    "cultural_significance": "...",
    "lasting_influence": "...",
    "modern_references": ["..."]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze historical context: {query}\n\nResearch: {json.dumps(search_results[:5], indent=2)}"}
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
            
            yield {"type": "historical_context", "data": analysis}
            
        except Exception as e:
            logger.error(f"Historical analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _analyze_subculture(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze a fashion subculture"""
        
        yield {"type": "status", "message": "Analyzing subculture..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} fashion subculture style history",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a subculture fashion expert. Analyze the style movement.

Respond in JSON format with:
{
    "subculture_name": "...",
    "origin": "...",
    "era": "...",
    "founding_context": "...",
    "key_visual_elements": ["..."],
    "iconic_pieces": ["..."],
    "color_palette": ["..."],
    "key_figures": ["..."],
    "cultural_significance": "...",
    "music_connection": "...",
    "political_social_context": "...",
    "evolution_over_time": "...",
    "mainstream_adoption": "...",
    "modern_influence": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze subculture: {query}\n\nResearch: {json.dumps(search_results[:5], indent=2)}"}
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
            
            yield {"type": "subculture_analysis", "data": analysis}
            
        except Exception as e:
            logger.error(f"Subculture analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _analyze_cultural_movement(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze a cultural fashion movement"""
        
        yield {"type": "status", "message": "Analyzing cultural movement..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} fashion movement cultural impact",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a fashion cultural studies expert. Analyze the movement.

Respond in JSON format with:
{
    "movement_name": "...",
    "origins": "...",
    "key_principles": ["..."],
    "fashion_manifestations": ["..."],
    "cultural_impact": "...",
    "key_proponents": ["..."],
    "opposition_to": "...",
    "legacy": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze movement: {query}\n\nResearch: {json.dumps(search_results[:5], indent=2)}"}
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
            
            yield {"type": "movement_analysis", "data": analysis}
            
        except Exception as e:
            logger.error(f"Movement analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _analyze_social_impact(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze social impact of fashion"""
        
        yield {"type": "status", "message": "Analyzing social impact..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} fashion social impact identity",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a fashion sociology expert. Analyze social impact.

Respond in JSON format with:
{
    "topic": "...",
    "social_dimensions": ["..."],
    "identity_expression": "...",
    "class_gender_dynamics": "...",
    "cultural_appropriation_concerns": "...",
    "empowerment_aspects": "...",
    "industry_impact": "...",
    "consumer_behavior": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze social impact: {query}\n\nResearch: {json.dumps(search_results[:5], indent=2)}"}
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
            
            yield {"type": "social_impact", "data": analysis}
            
        except Exception as e:
            logger.error(f"Social impact analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _general_cultural_analysis(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """General cultural analysis"""
        
        yield {"type": "status", "message": "Analyzing cultural topic..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"fashion culture {query}",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a fashion cultural expert. Provide comprehensive analysis.
Respond in JSON format with:
{
    "topic": "...",
    "summary": "...",
    "cultural_significance": "...",
    "key_insights": ["..."],
    "context": "..."
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
