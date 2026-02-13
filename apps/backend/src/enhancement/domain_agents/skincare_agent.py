"""
Skincare Agent - Advanced Skincare Intelligence
================================================

Deep skincare analysis including:
- Ingredient deep-dives
- Routine optimization
- Skin concern analysis
- Product compatibility
- Scientific research synthesis
"""

import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)


@dataclass
class SkinConcern:
    """Skin concern profile"""
    concern: str
    severity: str  # mild, moderate, severe
    recommended_ingredients: List[str] = field(default_factory=list)
    avoid_ingredients: List[str] = field(default_factory=list)
    lifestyle_factors: List[str] = field(default_factory=list)


@dataclass
class RoutineStep:
    """Skincare routine step"""
    step_number: int
    product_type: str
    purpose: str
    recommended_ingredients: List[str] = field(default_factory=list)
    application_tips: str = ""
    wait_time: str = ""  # e.g., "2-3 minutes"


class SkincareAgent:
    """Specialized agent for advanced skincare analysis"""
    
    ACTIVE_INGREDIENTS = {
        "retinol": {"category": "retinoid", "concerns": ["aging", "acne", "texture"]},
        "vitamin_c": {"category": "antioxidant", "concerns": ["brightening", "aging", "protection"]},
        "niacinamide": {"category": "multifunctional", "concerns": ["pores", "barrier", "tone"]},
        "salicylic_acid": {"category": "bha", "concerns": ["acne", "pores", "oil"]},
        "glycolic_acid": {"category": "aha", "concerns": ["texture", "tone", "aging"]},
        "hyaluronic_acid": {"category": "humectant", "concerns": ["hydration", "plumping"]},
        "azelaic_acid": {"category": "multifunctional", "concerns": ["rosacea", "acne", "tone"]},
        "peptides": {"category": "anti-aging", "concerns": ["aging", "firmness"]},
        "ceramides": {"category": "barrier", "concerns": ["barrier", "dryness", "sensitivity"]},
    }
    
    INCOMPATIBLE_PAIRS = [
        ("retinol", "vitamin_c"),  # Can cause irritation
        ("aha", "retinol"),  # Too exfoliating together
        ("bha", "retinol"),  # Too exfoliating together
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
        
        yield {"type": "status", "message": "Skincare Agent initializing..."}
        
        # Detect analysis type
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["routine", "regimen", "am routine", "pm routine"]):
            async for event in self._create_routine(query, context):
                yield event
        elif any(kw in query_lower for kw in ["ingredient", "retinol", "acid", "serum"]):
            async for event in self._deep_ingredient_analysis(query, context):
                yield event
        elif any(kw in query_lower for kw in ["concern", "acne", "aging", "dark spots"]):
            async for event in self._analyze_concern(query, context):
                yield event
        else:
            async for event in self._general_skincare_analysis(query, context):
                yield event
    
    async def _create_routine(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Create a personalized skincare routine"""
        
        yield {"type": "status", "message": "Creating personalized routine..."}
        
        system_prompt = """You are an expert dermatologist and skincare specialist.
Create a comprehensive, science-backed skincare routine.

Respond in JSON format with:
{
    "skin_profile": {
        "type": "...",
        "concerns": ["..."],
        "sensitivity_level": "..."
    },
    "morning_routine": [
        {"step": 1, "product": "...", "key_ingredients": ["..."], "purpose": "...", "tips": "..."}
    ],
    "evening_routine": [
        {"step": 1, "product": "...", "key_ingredients": ["..."], "purpose": "...", "tips": "..."}
    ],
    "weekly_treatments": [
        {"treatment": "...", "frequency": "...", "purpose": "..."}
    ],
    "ingredient_compatibility": {
        "can_mix": [["...", "..."]],
        "avoid_mixing": [["...", "..."]],
        "timing_separation": [{"ingredients": ["..."], "separation": "..."}]
    },
    "expected_timeline": {
        "immediate": ["..."],
        "2_4_weeks": ["..."],
        "3_months": ["..."]
    },
    "lifestyle_recommendations": ["..."]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Create a skincare routine for: {query}"}
        ]
        
        try:
            response = await self.llm_client.chat.completions.create(
                model="kimi-k2.5",
                messages=messages,
                temperature=1.0,
                max_tokens=5000,
                response_format={"type": "json_object"}
            )
            
            routine = json.loads(response.choices[0].message.content)
            
            yield {"type": "routine_created", "data": routine}
            
        except Exception as e:
            logger.error(f"Routine creation failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _deep_ingredient_analysis(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Deep analysis of a skincare ingredient"""
        
        yield {"type": "status", "message": "Analyzing ingredient..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} skincare ingredient mechanism research",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a cosmetic chemist with deep knowledge of skincare actives.
Provide a comprehensive, scientifically accurate ingredient analysis.

Respond in JSON format with:
{
    "ingredient": {
        "name": "...",
        "inci_name": "...",
        "category": "...",
        "molecular_weight": "..."
    },
    "mechanism_of_action": "...",
    "proven_benefits": [
        {"benefit": "...", "evidence_level": "high/medium/low", "timeframe": "..."}
    ],
    "concentration_guidelines": {
        "minimum_effective": "...",
        "typical_range": "...",
        "maximum_recommended": "..."
    },
    "formulation_considerations": {
        "ph_requirements": "...",
        "stability_issues": ["..."],
        "packaging_requirements": "..."
    },
    "compatibility": {
        "synergistic_with": ["..."],
        "antagonistic_with": ["..."],
        "can_be_alternated_with": ["..."]
    },
    "usage_guidelines": {
        "best_time": "...",
        "frequency": "...",
        "application_order": "..."
    },
    "side_effects": {
        "common": ["..."],
        "rare": ["..."],
        "contraindications": ["..."]
    },
    "supporting_research": [
        {"study": "...", "findings": "...", "year": "..."}
    ]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Deep analysis of: {query}\n\nResearch: {json.dumps(search_results[:5], indent=2)}"}
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
            
            yield {"type": "ingredient_analysis", "data": analysis}
            
        except Exception as e:
            logger.error(f"Ingredient analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _analyze_concern(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze a skin concern"""
        
        yield {"type": "status", "message": "Analyzing skin concern..."}
        
        system_prompt = """You are a dermatologist specializing in cosmetic concerns.
Provide evidence-based analysis and treatment recommendations.

Respond in JSON format with:
{
    "concern": "...",
    "causes": ["..."],
    "contributing_factors": ["..."],
    "effective_ingredients": [
        {"ingredient": "...", "mechanism": "...", "evidence": "..."}
    ],
    "recommended_products": {
        "cleanser": "...",
        "treatment": "...",
        "moisturizer": "...",
        "sunscreen": "..."
    },
    "professional_treatments": ["..."],
    "lifestyle_modifications": ["..."],
    "expected_results": {
        "timeline": "...",
        "realistic_outcomes": ["..."]
    }
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze skin concern: {query}"}
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
            
            yield {"type": "concern_analysis", "data": analysis}
            
        except Exception as e:
            logger.error(f"Concern analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _general_skincare_analysis(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """General skincare analysis"""
        
        yield {"type": "status", "message": "Analyzing skincare topic..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"skincare {query}",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a skincare expert. Provide comprehensive, evidence-based analysis.
Respond in JSON format with:
{
    "topic": "...",
    "summary": "...",
    "key_insights": ["..."],
    "evidence_based_facts": ["..."],
    "common_misconceptions": ["..."],
    "recommendations": ["..."]
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
    
    def check_compatibility(self, ingredients: List[str]) -> Dict:
        """Check ingredient compatibility"""
        warnings = []
        recommendations = []
        
        for i, ing1 in enumerate(ingredients):
            for ing2 in ingredients[i+1:]:
                # Check incompatible pairs
                for pair in self.INCOMPATIBLE_PAIRS:
                    if (ing1.lower() in pair[0] and ing2.lower() in pair[1]) or \
                       (ing1.lower() in pair[1] and ing2.lower() in pair[0]):
                        warnings.append(f"{ing1} + {ing2}: May cause irritation. Consider using at different times.")
        
        return {
            "compatible": len(warnings) == 0,
            "warnings": warnings,
            "recommendations": recommendations
        }
