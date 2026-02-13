"""
Beauty Agent - Beauty & Cosmetics Intelligence
===============================================

Specialized agent for beauty domain analysis including:
- Product analysis and reviews
- Ingredient research
- Trend forecasting
- Brand positioning
- Market analysis
"""

import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum

logger = logging.getLogger(__name__)


class BeautyAnalysisType(Enum):
    PRODUCT_ANALYSIS = "product_analysis"
    INGREDIENT_RESEARCH = "ingredient_research"
    TREND_FORECAST = "trend_forecast"
    BRAND_POSITIONING = "brand_positioning"
    MARKET_ANALYSIS = "market_analysis"
    ROUTINE_RECOMMENDATION = "routine_recommendation"


@dataclass
class ProductAnalysis:
    """Beauty product analysis"""
    product_name: str
    brand: str
    category: str
    key_ingredients: List[str] = field(default_factory=list)
    benefits: List[str] = field(default_factory=list)
    target_concerns: List[str] = field(default_factory=list)
    skin_types: List[str] = field(default_factory=list)
    price_point: str = ""
    market_positioning: str = ""
    similar_products: List[str] = field(default_factory=list)


@dataclass
class IngredientProfile:
    """Beauty ingredient profile"""
    name: str
    category: str  # active, emollient, preservative, etc.
    benefits: List[str] = field(default_factory=list)
    concerns: List[str] = field(default_factory=list)
    compatibility: List[str] = field(default_factory=list)
    contraindications: List[str] = field(default_factory=list)
    concentration_range: str = ""
    scientific_evidence: str = ""


class BeautyAgent:
    """
    Specialized agent for beauty and cosmetics domain.
    
    Capabilities:
    - Analyze beauty products
    - Research ingredients
    - Forecast beauty trends
    - Analyze brand positioning
    - Recommend routines
    """
    
    PRODUCT_CATEGORIES = [
        "skincare", "makeup", "haircare", "fragrance",
        "bodycare", "suncare", "tools", "supplements"
    ]
    
    SKIN_TYPES = ["normal", "dry", "oily", "combination", "sensitive", "acne-prone"]
    
    KEY_INGREDIENTS = [
        "retinol", "vitamin_c", "hyaluronic_acid", "niacinamide",
        "salicylic_acid", "glycolic_acid", "peptides", "ceramides",
        "azelaic_acid", "bakuchiol", "collagen", "squalane"
    ]
    
    def __init__(
        self,
        llm_client,
        search_tools=None,
        image_analysis=None,
    ):
        self.llm_client = llm_client
        self.search_tools = search_tools
        self.image_analysis = image_analysis
    
    async def analyze(
        self,
        query: str,
        analysis_type: Optional[BeautyAnalysisType] = None,
        context: Optional[Dict] = None,
        images: Optional[List[str]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Main analysis entry point"""
        
        yield {"type": "status", "message": "Beauty Agent initializing..."}
        
        if not analysis_type:
            analysis_type = await self._detect_analysis_type(query)
        
        yield {"type": "analysis_type_detected", "type": analysis_type.value}
        
        if analysis_type == BeautyAnalysisType.PRODUCT_ANALYSIS:
            async for event in self._analyze_product(query, context, images):
                yield event
        elif analysis_type == BeautyAnalysisType.INGREDIENT_RESEARCH:
            async for event in self._research_ingredient(query, context):
                yield event
        elif analysis_type == BeautyAnalysisType.TREND_FORECAST:
            async for event in self._forecast_trends(query, context):
                yield event
        elif analysis_type == BeautyAnalysisType.ROUTINE_RECOMMENDATION:
            async for event in self._recommend_routine(query, context):
                yield event
        else:
            async for event in self._general_analysis(query, context):
                yield event
    
    async def _detect_analysis_type(self, query: str) -> BeautyAnalysisType:
        """Detect analysis type from query"""
        query_lower = query.lower()
        
        if any(kw in query_lower for kw in ["ingredient", "retinol", "vitamin c", "acid", "peptide"]):
            return BeautyAnalysisType.INGREDIENT_RESEARCH
        
        if any(kw in query_lower for kw in ["product", "review", "serum", "cream", "moisturizer"]):
            return BeautyAnalysisType.PRODUCT_ANALYSIS
        
        if any(kw in query_lower for kw in ["trend", "forecast", "upcoming", "next"]):
            return BeautyAnalysisType.TREND_FORECAST
        
        if any(kw in query_lower for kw in ["routine", "regimen", "skincare routine", "steps"]):
            return BeautyAnalysisType.ROUTINE_RECOMMENDATION
        
        return BeautyAnalysisType.MARKET_ANALYSIS
    
    async def _analyze_product(
        self,
        query: str,
        context: Optional[Dict],
        images: Optional[List[str]]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze a beauty product"""
        
        yield {"type": "status", "message": "Researching product..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} review ingredients benefits",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a beauty product analyst. Analyze:
- Key ingredients and their benefits
- Product claims vs. reality
- Suitable skin types
- How it fits in a routine
- Value proposition
- Similar alternatives

Respond in JSON format with:
{
    "product_name": "...",
    "brand": "...",
    "category": "...",
    "key_ingredients": [{"name": "...", "benefit": "..."}],
    "claimed_benefits": ["..."],
    "suitable_skin_types": ["..."],
    "texture_feel": "...",
    "how_to_use": "...",
    "price_point": "...",
    "value_assessment": "...",
    "similar_products": ["..."],
    "overall_rating": "..."
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze this beauty product: {query}\n\nSearch results: {json.dumps(search_results[:5], indent=2)}"}
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
            
            yield {
                "type": "product_analysis",
                "data": analysis,
                "product": ProductAnalysis(
                    product_name=analysis.get("product_name", ""),
                    brand=analysis.get("brand", ""),
                    category=analysis.get("category", ""),
                    key_ingredients=[i.get("name") for i in analysis.get("key_ingredients", [])],
                    benefits=analysis.get("claimed_benefits", []),
                    target_concerns=[],
                    skin_types=analysis.get("suitable_skin_types", []),
                    price_point=analysis.get("price_point", ""),
                    similar_products=analysis.get("similar_products", [])
                )
            }
            
        except Exception as e:
            logger.error(f"Product analysis failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _research_ingredient(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Research a beauty ingredient"""
        
        yield {"type": "status", "message": "Researching ingredient..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"{query} skincare ingredient benefits research",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a cosmetic chemist and ingredient expert. Analyze:
- What the ingredient does
- Scientific backing
- How to use it effectively
- What it pairs well with
- Potential side effects
- Concentration considerations

Respond in JSON format with:
{
    "ingredient_name": "...",
    "category": "...",
    "what_it_does": "...",
    "key_benefits": ["..."],
    "scientific_evidence": "...",
    "how_to_use": "...",
    "pairs_well_with": ["..."],
    "avoid_combining_with": ["..."],
    "concentration_range": "...",
    "potential_side_effects": ["..."],
    "best_for": ["..."]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Research this ingredient: {query}\n\nSearch results: {json.dumps(search_results[:5], indent=2)}"}
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
            
            yield {
                "type": "ingredient_research",
                "data": analysis,
                "ingredient": IngredientProfile(
                    name=analysis.get("ingredient_name", ""),
                    category=analysis.get("category", ""),
                    benefits=analysis.get("key_benefits", []),
                    concerns=analysis.get("potential_side_effects", []),
                    compatibility=analysis.get("pairs_well_with", []),
                    contraindications=analysis.get("avoid_combining_with", []),
                    concentration_range=analysis.get("concentration_range", ""),
                    scientific_evidence=analysis.get("scientific_evidence", "")
                )
            }
            
        except Exception as e:
            logger.error(f"Ingredient research failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _forecast_trends(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Forecast beauty trends"""
        
        yield {"type": "status", "message": "Forecasting beauty trends..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query="beauty trends 2025 2026 skincare makeup",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a beauty trend forecaster. Predict upcoming trends in:
- Skincare innovations
- Makeup directions
- Haircare developments
- Ingredient popularity
- Consumer preferences

Respond in JSON format with:
{
    "trends": [
        {
            "trend_name": "...",
            "category": "...",
            "description": "...",
            "driving_factors": ["..."],
            "key_products": ["..."],
            "timeline": "..."
        }
    ]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Forecast beauty trends: {query}\n\nSearch results: {json.dumps(search_results[:5], indent=2)}"}
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
            
            yield {"type": "trend_forecast", "data": analysis}
            
        except Exception as e:
            logger.error(f"Trend forecast failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _recommend_routine(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Recommend a skincare routine"""
        
        yield {"type": "status", "message": "Creating routine recommendation..."}
        
        system_prompt = """You are a skincare expert. Create a personalized routine.

Respond in JSON format with:
{
    "skin_type": "...",
    "primary_concerns": ["..."],
    "morning_routine": [
        {"step": 1, "product_type": "...", "purpose": "...", "tips": "..."}
    ],
    "evening_routine": [
        {"step": 1, "product_type": "...", "purpose": "...", "tips": "..."}
    ],
    "weekly_treatments": ["..."],
    "key_ingredients_to_look_for": ["..."],
    "lifestyle_tips": ["..."]
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
                max_tokens=4000,
                response_format={"type": "json_object"}
            )
            
            analysis = json.loads(response.choices[0].message.content)
            
            yield {"type": "routine_recommendation", "data": analysis}
            
        except Exception as e:
            logger.error(f"Routine recommendation failed: {e}")
            yield {"type": "error", "error": str(e)}
    
    async def _general_analysis(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """General beauty analysis"""
        
        yield {"type": "status", "message": "Analyzing beauty topic..."}
        
        search_results = []
        if self.search_tools:
            try:
                search_results = await self.search_tools.web_search(
                    query=f"beauty {query}",
                    num_results=10
                )
            except Exception as e:
                logger.warning(f"Search failed: {e}")
        
        system_prompt = """You are a beauty industry expert. Provide comprehensive analysis.
Respond in JSON format with:
{
    "topic": "...",
    "summary": "...",
    "key_points": ["..."],
    "market_insights": "...",
    "recommendations": ["..."]
}"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Analyze: {query}\n\nSearch results: {json.dumps(search_results[:5], indent=2)}"}
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
