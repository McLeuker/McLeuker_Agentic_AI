"""
Sustainability Agent - Fashion Sustainability Intelligence
===========================================================

Analyzes sustainability in fashion including:
- Material sustainability ratings
- Eco-certifications
- Supply chain transparency
- Circular fashion
- Carbon footprint analysis
"""

import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class MaterialSustainability:
    """Material sustainability profile"""
    material: str
    sustainability_score: float  # 0-100
    biodegradability: str
    water_usage: str
    carbon_footprint: str
    certifications: List[str] = field(default_factory=list)
    pros: List[str] = field(default_factory=list)
    cons: List[str] = field(default_factory=list)
    alternatives: List[str] = field(default_factory=list)


@dataclass
class BrandSustainability:
    """Brand sustainability profile"""
    brand: str
    overall_score: float
    transparency_score: float
    environmental_score: float
    social_score: float
    governance_score: float
    certifications: List[str] = field(default_factory=list)
    initiatives: List[str] = field(default_factory=list)
    areas_for_improvement: List[str] = field(default_factory=list)


class SustainabilityAgent:
    """Specialized agent for fashion sustainability analysis"""
    
    # Eco-certifications
    CERTIFICATIONS = {
        "GOTS": "Global Organic Textile Standard",
        "OEKO-TEX": "Standard 100 - Safe textiles",
        "BLUESIGN": "Sustainable textile production",
        "FAIR_TRADE": "Fair labor practices",
        "B_CORP": "B Corporation certified",
        "GRS": "Global Recycled Standard",
        "FSC": "Forest Stewardship Council",
        "CRADLE_TO_CRADLE": "Circular design certification",
    }
    
    # Material sustainability database (simplified)
    MATERIAL_RATINGS = {
        "organic_cotton": {"score": 85, "water": "low", "biodegradable": "yes"},
        "recycled_polyester": {"score": 70, "water": "medium", "biodegradable": "no"},
        "tencel": {"score": 90, "water": "low", "biodegradable": "yes"},
        "hemp": {"score": 95, "water": "very_low", "biodegradable": "yes"},
        "linen": {"score": 88, "water": "low", "biodegradable": "yes"},
        "conventional_cotton": {"score": 45, "water": "high", "biodegradable": "yes"},
        "virgin_polyester": {"score": 30, "water": "medium", "biodegradable": "no"},
        "conventional_wool": {"score": 60, "water": "medium", "biodegradable": "yes"},
        "vegan_leather_pu": {"score": 40, "water": "medium", "biodegradable": "no"},
        "apple_leather": {"score": 75, "water": "low", "biodegradable": "partial"},
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
        
        yield {"type": "status", "message": "Sustainability Agent initializing..."}
        
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["material", "fabric", "fiber", "textile"]):
            async for event in self._analyze_material(query, context):
                yield event
        elif any(kw in query_lower for kw in ["brand", "company", "label", "house"]):
            async for event in self._analyze_brand_sustainability(query, context):
                yield event
        elif any(kw in query_lower for kw in ["certification", "certified", "standard"]):
            async for event in self._explain_certifications(query, context):
                yield event
        elif any(kw in query_lower for kw in ["circular", "recycle", "upcycle", "secondhand"]):
            async for event in self._analyze_circular_fashion(query, context):
                yield event
        else:
            async for event in self._general_sustainability_analysis(query, context):
                yield event
    
    async def _analyze_material(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze material sustainability"""
        
        yield {"type": "status", "message": "Analyzing material sustainability..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} sustainable fashion material environmental impact",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a sustainable materials expert in fashion.
Provide comprehensive sustainability analysis of materials.

Respond in JSON format with:
{
    "material": "...",
    "sustainability_score": 0-100,
    "environmental_impact": {
        "water_usage": "...",
        "carbon_footprint": "...",
        "land_use": "...",
        "chemical_use": "..."
    },
    "biodegradability": "...",
    "recyclability": "...",
    "certifications_available": ["..."],
    "pros": ["..."],
    "cons": ["..."],
    "more_sustainable_alternatives": ["..."],
    "best_practices": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze sustainability of: {query}\n\nResearch: {json.dumps(search_results[:5], indent=2)}"}
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
            
            yield {"type": "material_analysis", "data": analysis}
            
        except Exception as e:
            logger.error(f"Material analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _analyze_brand_sustainability(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze brand sustainability practices"""
        
        yield {"type": "status", "message": "Analyzing brand sustainability..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} sustainability practices ESG report",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a fashion sustainability analyst. Evaluate brand sustainability.

Respond in JSON format with:
{
    "brand": "...",
    "overall_sustainability_score": 0-100,
    "transparency_score": 0-100,
    "environmental_score": 0-100,
    "social_score": 0-100,
    "governance_score": 0-100,
    "key_initiatives": ["..."],
    "certifications": ["..."],
    "supply_chain_transparency": "...",
    "carbon_neutral_commitments": "...",
    "circular_programs": ["..."],
    "areas_of_concern": ["..."],
    "recommendations": ["..."]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze sustainability of brand: {query}\n\nResearch: {json.dumps(search_results[:5], indent=2)}"}
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
            
            yield {"type": "brand_sustainability", "data": analysis}
            
        except Exception as e:
            logger.error(f"Brand analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _explain_certifications(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Explain eco-certifications"""
        
        yield {"type": "status", "message": "Explaining certifications..."}
        
        system_prompt = """You are a sustainability certification expert.
Explain fashion eco-certifications clearly.

Respond in JSON format with:
{
    "certifications": [
        {
            "name": "...",
            "full_name": "...",
            "what_it_means": "...",
            "requirements": ["..."],
            "credibility": "high/medium/low",
            "limitations": ["..."]
        }
    ],
    "how_to_verify": "...",
    "greenwashing_warnings": ["..."]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Explain certifications for: {query}"}
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
            
            yield {"type": "certifications", "data": analysis}
            
        except Exception as e:
            logger.error(f"Certification explanation failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _analyze_circular_fashion(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze circular fashion options"""
        
        yield {"type": "status", "message": "Analyzing circular fashion..."}
        
        system_prompt = """You are a circular fashion expert. Analyze circular options.

Respond in JSON format with:
{
    "circular_options": [
        {
            "option": "...",
            "description": "...",
            "environmental_benefit": "...",
            "how_to_participate": "..."
        }
    ],
    "resale_platforms": ["..."],
    "rental_services": ["..."],
    "repair_resources": ["..."],
    "upcycling_ideas": ["..."],
    "recycling_programs": ["..."]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze circular fashion for: {query}"}
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
            
            yield {"type": "circular_fashion", "data": analysis}
            
        except Exception as e:
            logger.error(f"Circular fashion analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _general_sustainability_analysis(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """General sustainability analysis"""
        
        yield {"type": "status", "message": "Analyzing sustainability topic..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"fashion sustainability {query}",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a fashion sustainability expert. Provide comprehensive analysis.
Respond in JSON format with:
{
    "topic": "...",
    "summary": "...",
    "key_issues": ["..."],
    "solutions": ["..."],
    "industry_progress": "...",
    "consumer_actions": ["..."]
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
