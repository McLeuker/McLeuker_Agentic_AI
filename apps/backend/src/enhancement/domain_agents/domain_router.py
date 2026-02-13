"""
Domain Router - Route queries to appropriate domain agents
===========================================================

Routes user queries to the most appropriate domain agent based on:
- Query content analysis
- Domain detection
- Agent availability
"""

import json
import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from enum import Enum

logger = logging.getLogger(__name__)


class DomainType(Enum):
    """Available domain types"""
    FASHION = "fashion"
    BEAUTY = "beauty"
    SKINCARE = "skincare"
    SUSTAINABILITY = "sustainability"
    TECH = "tech"
    CATWALK = "catwalk"
    CULTURE = "culture"
    TEXTILE = "textile"
    LIFESTYLE = "lifestyle"
    GENERAL = "general"


class DomainRouter:
    """
    Router for domain-specific queries.
    
    Analyzes queries and routes them to the appropriate domain agent.
    """
    
    # Domain keywords for detection
    DOMAIN_KEYWORDS = {
        DomainType.FASHION: [
            "fashion", "trend", "style", "outfit", "collection", "designer",
            "runway", "catwalk", "brand", "luxury", "couture", "ready-to-wear",
            "lookbook", "fashion week", "season", "spring", "summer", "fall", "winter",
            "silhouette", "color trend", "pattern", "texture", "garment", "apparel"
        ],
        DomainType.BEAUTY: [
            "beauty", "makeup", "cosmetic", "lipstick", "foundation", "mascara",
            "eyeshadow", "blush", "concealer", "highlighter", "contour",
            "hair", "hairstyle", "hair color", "hair care", "shampoo", "conditioner",
            "fragrance", "perfume", "scent", "nail", "manicure", "pedicure"
        ],
        DomainType.SKINCARE: [
            "skincare", "skin", "serum", "moisturizer", "cleanser", "toner",
            "retinol", "vitamin c", "niacinamide", "acid", "exfoliant",
            "spf", "sunscreen", "anti-aging", "acne", "pores", "hydration",
            "routine", "regimen", "face", "facial", "dermatology"
        ],
        DomainType.SUSTAINABILITY: [
            "sustainable", "eco-friendly", "green", "ethical", "organic",
            "recycled", "upcycled", "circular", "carbon footprint", "vegan",
            "cruelty-free", "fair trade", "biodegradable", "zero waste",
            "certification", "gots", "oeko-tex", "bluesign", "b corp"
        ],
        DomainType.TECH: [
            "technology", "tech", "wearable", "smart", "3d print", "ai",
            "artificial intelligence", "virtual", "ar", "vr", "digital",
            "blockchain", "nft", "metaverse", "innovation", "automation",
            "e-textile", "sensor", "app", "platform", "software"
        ],
        DomainType.CATWALK: [
            "runway", "catwalk", "show", "presentation", "fashion week",
            "nyfw", "lfw", "mfw", "pfw", "look", "exit", "finale",
            "front row", "backstage", "model", "casting", "set design"
        ],
        DomainType.CULTURE: [
            "culture", "history", "heritage", "subculture", "movement",
            "punk", "goth", "hip hop", "grunge", "streetwear", "era",
            "decade", "1920s", "1960s", "1970s", "1980s", "1990s",
            "social", "identity", "expression", "art", "music"
        ],
        DomainType.TEXTILE: [
            "textile", "fabric", "material", "fiber", "weave", "knit",
            "cotton", "silk", "wool", "linen", "polyester", "nylon",
            "denim", "leather", "suede", "velvet", "lace", "chiffon",
            "care", "wash", "maintain", "durability", "breathability"
        ],
        DomainType.LIFESTYLE: [
            "lifestyle", "wellness", "self-care", "mindfulness", "minimalism",
            "slow living", "hygge", "lagom", "conscious", "mindful",
            "ritual", "routine", "habit", "balance", "home", "living",
            "aesthetic", "vibe", "mood", "atmosphere"
        ],
    }
    
    def __init__(
        self,
        fashion_agent=None,
        beauty_agent=None,
        skincare_agent=None,
        sustainability_agent=None,
        tech_agent=None,
        catwalk_agent=None,
        culture_agent=None,
        textile_agent=None,
        lifestyle_agent=None,
    ):
        """
        Initialize domain router with agents.
        
        Args:
            fashion_agent: FashionAgent instance
            beauty_agent: BeautyAgent instance
            skincare_agent: SkincareAgent instance
            sustainability_agent: SustainabilityAgent instance
            tech_agent: TechAgent instance
            catwalk_agent: CatwalkAgent instance
            culture_agent: CultureAgent instance
            textile_agent: TextileAgent instance
            lifestyle_agent: LifestyleAgent instance
        """
        self.agents = {
            DomainType.FASHION: fashion_agent,
            DomainType.BEAUTY: beauty_agent,
            DomainType.SKINCARE: skincare_agent,
            DomainType.SUSTAINABILITY: sustainability_agent,
            DomainType.TECH: tech_agent,
            DomainType.CATWALK: catwalk_agent,
            DomainType.CULTURE: culture_agent,
            DomainType.TEXTILE: textile_agent,
            DomainType.LIFESTYLE: lifestyle_agent,
        }
        
        logger.info(f"DomainRouter initialized with {sum(1 for a in self.agents.values() if a is not None)} agents")
    
    def detect_domain(self, query: str) -> DomainType:
        """
        Detect the domain of a query.
        
        Args:
            query: User query
            
        Returns:
            Detected domain type
        """
        query_lower = query.lower()
        
        # Score each domain
        domain_scores = {}
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            score = 0
            for keyword in keywords:
                if keyword in query_lower:
                    # Longer keyword matches get higher weight
                    score += len(keyword.split())
            domain_scores[domain] = score
        
        # Get highest scoring domain
        if domain_scores:
            best_domain = max(domain_scores, key=domain_scores.get)
            if domain_scores[best_domain] > 0:
                return best_domain
        
        return DomainType.GENERAL
    
    def get_available_domains(self) -> List[str]:
        """Get list of available domain agents"""
        return [domain.value for domain, agent in self.agents.items() if agent is not None]
    
    async def route(
        self,
        query: str,
        preferred_domain: Optional[str] = None,
        context: Optional[Dict] = None,
        images: Optional[List[str]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Route query to appropriate agent.
        
        Args:
            query: User query
            preferred_domain: Optional preferred domain override
            context: Additional context
            images: Optional images
            
        Yields:
            Events from the selected agent
        """
        # Determine domain
        if preferred_domain:
            try:
                domain = DomainType(preferred_domain.lower())
            except ValueError:
                domain = self.detect_domain(query)
        else:
            domain = self.detect_domain(query)
        
        yield {
            "type": "domain_detected",
            "domain": domain.value,
            "confidence": "high" if preferred_domain else "auto"
        }
        
        # Get agent
        agent = self.agents.get(domain)
        
        if agent is None:
            # Try to find any available agent
            available = self.get_available_domains()
            if available:
                yield {
                    "type": "agent_unavailable",
                    "requested_domain": domain.value,
                    "available_domains": available,
                    "fallback": "general"
                }
                # Fallback to general
                async for event in self._general_response(query, context):
                    yield event
            else:
                yield {
                    "type": "error",
                    "error": f"No agents available for domain: {domain.value}"
                }
            return
        
        # Route to agent
        yield {"type": "routing", "to_agent": domain.value}
        
        try:
            async for event in agent.analyze(query, context, images):
                # Add domain tag to events
                event["domain"] = domain.value
                yield event
        except Exception as e:
            logger.error(f"Agent error: {e}")
            yield {"type": "error", "error": str(e), "domain": domain.value}
    
    async def route_multi_domain(
        self,
        query: str,
        domains: List[str],
        context: Optional[Dict] = None,
        images: Optional[List[str]] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Route query to multiple domain agents.
        
        Args:
            query: User query
            domains: List of domain names to consult
            context: Additional context
            images: Optional images
            
        Yields:
            Events from multiple agents
        """
        yield {"type": "multi_domain_start", "domains": domains}
        
        for domain_name in domains:
            try:
                domain = DomainType(domain_name.lower())
                agent = self.agents.get(domain)
                
                if agent:
                    yield {"type": "consulting_agent", "domain": domain_name}
                    
                    async for event in agent.analyze(query, context, images):
                        event["domain"] = domain_name
                        event["multi_domain"] = True
                        yield event
                        
            except ValueError:
                yield {"type": "error", "error": f"Unknown domain: {domain_name}"}
        
        yield {"type": "multi_domain_complete", "domains": domains}
    
    async def _general_response(
        self,
        query: str,
        context: Optional[Dict]
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """General response when no specific agent is available"""
        
        yield {"type": "status", "message": "Providing general analysis..."}
        
        # Use fashion agent as fallback if available
        fashion_agent = self.agents.get(DomainType.FASHION)
        if fashion_agent:
            async for event in fashion_agent.analyze(query, context):
                yield event
            return
        
        # Otherwise provide simple response
        yield {
            "type": "general_response",
            "message": "I'm analyzing your query across multiple domains...",
            "query": query
        }
    
    def get_agent_info(self) -> Dict[str, Any]:
        """Get information about registered agents"""
        return {
            "available_agents": self.get_available_domains(),
            "all_domains": [d.value for d in DomainType],
            "detection_keywords": {
                domain.value: len(keywords)
                for domain, keywords in self.DOMAIN_KEYWORDS.items()
            }
        }
