"""
Catwalk Agent - Runway & Fashion Show Intelligence
===================================================

Analyzes runway shows and fashion presentations:
- Collection analysis
- Designer spotlights
- Trend extraction
- Show coverage
- Comparative analysis
"""

import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class RunwayShow:
    """Runway show details"""
    designer: str
    season: str
    year: int
    location: str
    theme: str
    key_looks: List[Dict] = field(default_factory=list)
    standout_elements: List[str] = field(default_factory=list)
    overall_impression: str = ""
    critics_notes: List[str] = field(default_factory=list)


@dataclass
class LookAnalysis:
    """Individual look analysis"""
    look_number: int
    description: str
    key_pieces: List[str] = field(default_factory=list)
    color_palette: List[str] = field(default_factory=list)
    materials: List[str] = field(default_factory=list)
    styling_details: List[str] = field(default_factory=list)
    inspiration: str = ""


class CatwalkAgent:
    """Specialized agent for runway and fashion show analysis"""
    
    FASHION_WEEKS = {
        "nyfw": "New York Fashion Week",
        "lfw": "London Fashion Week",
        "mfw": "Milan Fashion Week",
        "pfw": "Paris Fashion Week",
    }
    
    def __init__(self, llm_client, search_tools=None, image_analysis=None):
        self.llm_client = llm_client
        self.search_tools = search_tools
        self.image_analysis = image_analysis
    
    async def analyze(
        self,
        query: str,
        context: Optional[Dict] = None,
        images: Optional[List[str]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Main analysis entry point"""
        
        yield {"type": "status", "message": "Catwalk Agent initializing..."}
        
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["collection", "show", "runway", "presentation"]):
            async for event in self._analyze_collection(query, context, images):
                yield event
        elif any(kw in query_lower for kw in ["fashion week", "nyfw", "lfw", "mfw", "pfw"]):
            async for event in self._analyze_fashion_week(query, context):
                yield event
        elif any(kw in query_lower for kw in ["designer", "creative director"]):
            async for event in self._spotlight_designer(query, context):
                yield event
        elif any(kw in query_lower for kw in ["compare", "versus", "vs"]):
            async for event in self._compare_shows(query, context):
                yield event
        else:
            async for event in self._general_runway_analysis(query, context):
                yield event
    
    async def _analyze_collection(
        self,
        query: str,
        context: Optional[Dict],
        images: Optional[List[str]]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze a runway collection"""
        
        yield {"type": "status", "message": "Analyzing runway collection..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} runway collection review",
                    num_results=15
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        yield {"type": "search_complete", "results_count": len(search_results)}
        
        system_prompt = """You are a fashion critic specializing in runway analysis.
Provide detailed collection analysis.

Respond in JSON format with:
{
    "designer": "...",
    "season": "...",
    "year": 2025,
    "location": "...",
    "theme_concept": "...",
    "inspiration": "...",
    "key_looks": [
        {
            "look_number": 1,
            "description": "...",
            "standout_elements": ["..."],
            "styling_notes": "..."
        }
    ],
    "color_palette": ["..."],
    "materials": ["..."],
    "silhouettes": ["..."],
    "signature_details": ["..."],
    "casting_notes": "...",
    "music_atmosphere": "...",
    "set_design": "...",
    "overall_impression": "...",
    "critics_consensus": "...",
    "commercial_viability": "...",
    "awards_potential": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze this runway collection: {query}\n\nReviews: {json.dumps(search_results[:8], indent=2)}"}
        ]
        
        try:
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=5000,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            yield {"type": "collection_analysis", "data": analysis}
            
        except Exception as e:
            logger.error(f"Collection analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _analyze_fashion_week(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze a fashion week"""
        
        yield {"type": "status", "message": "Analyzing fashion week..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} fashion week highlights best shows",
                    num_results=15
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a fashion week correspondent. Provide comprehensive coverage.

Respond in JSON format with:
{
    "fashion_week": "...",
    "season": "...",
    "year": 2025,
    "top_shows": [
        {
            "designer": "...",
            "highlights": ["..."],
            "standout_looks": ["..."],
            "rating": "..."
        }
    ],
    "emerging_trends": ["..."],
    "surprise_moments": ["..."],
    "celebrity_attendance": ["..."],
    "industry_buzz": "...",
    "overall_direction": "...",
    "best_in_show": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze fashion week: {query}\n\nCoverage: {json.dumps(search_results[:8], indent=2)}"}
        ]
        
        try:
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=5000,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            yield {"type": "fashion_week_analysis", "data": analysis}
            
        except Exception as e:
            logger.error(f"Fashion week analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _spotlight_designer(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Spotlight a designer's runway work"""
        
        yield {"type": "status", "message": "Analyzing designer's runway work..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} designer runway collections evolution",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a fashion historian specializing in designer analysis.
Analyze the designer's runway evolution and signature style.

Respond in JSON format with:
{
    "designer": "...",
    "signature_aesthetic": "...",
    "design_philosophy": "...",
    "notable_collections": [
        {"season": "...", "year": 2025, "theme": "...", "impact": "..."}
    ],
    "recurring_themes": ["..."],
    "signature_techniques": ["..."],
    "evolution_over_time": "...",
    "industry_impact": "...",
    "future_direction": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Spotlight designer: {query}\n\nResearch: {json.dumps(search_results[:5], indent=2)}"}
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
            
            yield {"type": "designer_spotlight", "data": analysis}
            
        except Exception as e:
            logger.error(f"Designer spotlight failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _compare_shows(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Compare multiple runway shows"""
        
        yield {"type": "status", "message": "Comparing runway shows..."}
        
        system_prompt = """You are a fashion critic comparing runway shows.
Provide comparative analysis.

Respond in JSON format with:
{
    "shows_compared": ["..."],
    "similarities": ["..."],
    "differences": ["..."],
    "standout_elements": {
        "show1": ["..."],
        "show2": ["..."]
    },
    "trend_alignment": "...",
    "commercial_potential": "...",
    "winner": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Compare these shows: {query}"}
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
            
            yield {"type": "show_comparison", "data": analysis}
            
        except Exception as e:
            logger.error(f"Show comparison failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _general_runway_analysis(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """General runway analysis"""
        
        yield {"type": "status", "message": "Analyzing runway topic..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"runway fashion {query}",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a runway fashion expert. Provide comprehensive analysis.
Respond in JSON format with:
{
    "topic": "...",
    "summary": "...",
    "key_insights": ["..."],
    "related_shows": ["..."],
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
