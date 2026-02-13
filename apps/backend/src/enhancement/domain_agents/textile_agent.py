"""
Textile Agent - Textile & Material Intelligence
================================================

Analyzes textiles and materials:
- Fabric properties
- Material innovation
- Technical specifications
- Care instructions
- Performance characteristics
"""

import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class FabricProfile:
    """Fabric profile"""
    name: str
    fiber_content: str
    weave_knit_type: str
    weight: str
    drape: str
    breathability: str
    durability: str
    care_instructions: List[str] = field(default_factory=list)
    best_uses: List[str] = field(default_factory=list)
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)


@dataclass
class MaterialInnovation:
    """Material innovation profile"""
    name: str
    innovation_type: str
    description: str
    benefits: List[str] = field(default_factory=list)
    applications: List[str] = field(default_factory=list)
    sustainability_impact: str = ""
    commercial_availability: str = ""


class TextileAgent:
    """Specialized agent for textile and material analysis"""
    
    FABRIC_TYPES = {
        "cotton": {"natural": True, "breathable": True, "care": "easy"},
        "silk": {"natural": True, "breathable": True, "care": "delicate"},
        "wool": {"natural": True, "breathable": True, "care": "special"},
        "linen": {"natural": True, "breathable": True, "care": "easy"},
        "polyester": {"natural": False, "breathable": False, "care": "easy"},
        "nylon": {"natural": False, "breathable": False, "care": "easy"},
        "viscose": {"natural": False, "breathable": True, "care": "delicate"},
        "tencel": {"natural": False, "breathable": True, "care": "easy"},
    }
    
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
        
        yield {"type": "status", "message": "Textile Agent initializing..."}
        
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["fabric", "material", "textile", "fiber"]):
            async for event in self._analyze_fabric(query, context):
                yield event
        elif any(kw in query_lower for kw in ["innovation", "new material", "tech fabric", "smart fabric"]):
            async for event in self._analyze_innovation(query, context):
                yield event
        elif any(kw in query_lower for kw in ["care", "wash", "maintain", "clean"]):
            async for event in self._provide_care_instructions(query, context):
                yield event
        elif any(kw in query_lower for kw in ["compare", "versus", "vs"]):
            async for event in self._compare_materials(query, context):
                yield event
        else:
            async for event in self._general_textile_analysis(query, context):
                yield event
    
    async def _analyze_fabric(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze a fabric"""
        
        yield {"type": "status", "message": "Analyzing fabric..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} fabric properties characteristics",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a textile expert. Provide comprehensive fabric analysis.

Respond in JSON format with:
{
    "fabric_name": "...",
    "fiber_content": "...",
    "weave_or_knit_type": "...",
    "weight_category": "...",
    "physical_properties": {
        "drape": "...",
        "hand_feel": "...",
        "luster": "...",
        "texture": "..."
    },
    "performance_characteristics": {
        "breathability": "...",
        "moisture_wicking": "...",
        "durability": "...",
        "stretch_recovery": "...",
        "wrinkle_resistance": "..."
    },
    "care_instructions": {
        "washing": "...",
        "drying": "...",
        "ironing": "...",
        "dry_cleaning": "...",
        "special_notes": "..."
    },
    "best_uses": ["..."],
    "garment_types": ["..."],
    "pros": ["..."],
    "cons": ["..."],
    "similar_fabrics": ["..."],
    "price_range": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze fabric: {query}\n\nResearch: {json.dumps(search_results[:5], indent=2)}"}
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
            
            yield {"type": "fabric_analysis", "data": analysis}
            
        except Exception as e:
            logger.error(f"Fabric analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _analyze_innovation(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze material innovation"""
        
        yield {"type": "status", "message": "Analyzing material innovation..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} textile innovation material science",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a textile innovation expert. Analyze material innovations.

Respond in JSON format with:
{
    "innovation_name": "...",
    "category": "...",
    "description": "...",
    "how_it_works": "...",
    "key_benefits": ["..."],
    "performance_improvements": ["..."],
    "sustainability_impact": "...",
    "applications": ["..."],
    "key_companies": ["..."],
    "commercial_availability": "...",
    "cost_implications": "...",
    "future_potential": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze innovation: {query}\n\nResearch: {json.dumps(search_results[:5], indent=2)}"}
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
            
            yield {"type": "innovation_analysis", "data": analysis}
            
        except Exception as e:
            logger.error(f"Innovation analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _provide_care_instructions(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Provide care instructions"""
        
        yield {"type": "status", "message": "Providing care instructions..."}
        
        system_prompt = """You are a fabric care expert. Provide detailed care instructions.

Respond in JSON format with:
{
    "fabric_garment": "...",
    "washing": {
        "method": "...",
        "temperature": "...",
        "detergent": "...",
        "frequency": "..."
    },
    "drying": {
        "method": "...",
        "temperature": "...",
        "special_notes": "..."
    },
    "ironing": {
        "temperature": "...",
        "technique": "..."
    },
    "storage": "...",
    "stain_removal": ["..."],
    "professional_care": "...",
    "common_mistakes": ["..."],
    "longevity_tips": ["..."]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Care instructions for: {query}"}
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
            
            yield {"type": "care_instructions", "data": analysis}
            
        except Exception as e:
            logger.error(f"Care instructions failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _compare_materials(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Compare materials"""
        
        yield {"type": "status", "message": "Comparing materials..."}
        
        system_prompt = """You are a textile comparison expert. Compare materials side by side.

Respond in JSON format with:
{
    "materials_compared": ["..."],
    "comparison_table": {
        "property": ["material1", "material2"]
    },
    "best_for": {
        "material1": ["..."],
        "material2": ["..."]
    },
    "recommendation": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Compare materials: {query}"}
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
            
            yield {"type": "material_comparison", "data": analysis}
            
        except Exception as e:
            logger.error(f"Material comparison failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _general_textile_analysis(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """General textile analysis"""
        
        yield {"type": "status", "message": "Analyzing textile topic..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"textile {query}",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a textile expert. Provide comprehensive analysis.
Respond in JSON format with:
{
    "topic": "...",
    "summary": "...",
    "key_information": ["..."],
    "technical_details": "...",
    "practical_applications": ["..."]
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
