"""
McLeuker AI V8 - RAG (Retrieval-Augmented Generation) System
=============================================================
Knowledge base retrieval system specialized for fashion domain.
Provides context-aware information retrieval to enhance AI responses.
"""

import os
import json
import hashlib
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


class KnowledgeCategory(Enum):
    """Categories of fashion knowledge"""
    TRENDS = "trends"
    DESIGNERS = "designers"
    BRANDS = "brands"
    MATERIALS = "materials"
    SUSTAINABILITY = "sustainability"
    TECHNOLOGY = "technology"
    HISTORY = "history"
    BUSINESS = "business"
    CULTURE = "culture"
    BEAUTY = "beauty"


@dataclass
class KnowledgeChunk:
    """A chunk of knowledge in the RAG system"""
    id: str
    content: str
    category: KnowledgeCategory
    source: str
    metadata: Dict = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    relevance_score: float = 1.0
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "category": self.category.value,
            "source": self.source,
            "metadata": self.metadata,
            "created_at": self.created_at.isoformat(),
            "relevance_score": self.relevance_score
        }


@dataclass
class RetrievalResult:
    """Result from knowledge retrieval"""
    query: str
    chunks: List[KnowledgeChunk]
    total_found: int
    categories_searched: List[str]
    retrieval_time_ms: float
    
    def to_dict(self) -> Dict:
        return {
            "query": self.query,
            "chunks": [c.to_dict() for c in self.chunks],
            "total_found": self.total_found,
            "categories_searched": self.categories_searched,
            "retrieval_time_ms": self.retrieval_time_ms
        }


class FashionKnowledgeBase:
    """
    Fashion domain knowledge base with curated information.
    Includes trends, designers, brands, materials, and more.
    """
    
    def __init__(self):
        self.chunks: Dict[str, KnowledgeChunk] = {}
        self.category_index: Dict[KnowledgeCategory, List[str]] = {cat: [] for cat in KnowledgeCategory}
        self.keyword_index: Dict[str, List[str]] = {}
        
        # Initialize with fashion domain knowledge
        self._initialize_knowledge_base()
    
    def _initialize_knowledge_base(self):
        """Initialize with curated fashion knowledge"""
        
        # Sustainability knowledge
        sustainability_knowledge = [
            {
                "content": "Sustainable fashion focuses on reducing environmental impact through eco-friendly materials, ethical production, and circular economy principles. Key practices include using organic cotton, recycled polyester, and biodegradable fabrics.",
                "source": "Fashion Sustainability Guide 2026",
                "metadata": {"topic": "overview", "year": 2026}
            },
            {
                "content": "Circular fashion promotes extending garment life through repair, resale, and recycling. Brands like Patagonia, Eileen Fisher, and Stella McCartney lead in circular initiatives. The resale market is projected to reach $77 billion by 2026.",
                "source": "Circular Economy Fashion Report",
                "metadata": {"topic": "circular_fashion", "market_size": "$77B"}
            },
            {
                "content": "Regenerative agriculture in fashion focuses on farming practices that restore soil health. Brands are investing in regenerative cotton and wool to reduce carbon footprint and improve biodiversity.",
                "source": "Regenerative Fashion Initiative",
                "metadata": {"topic": "regenerative", "focus": "agriculture"}
            },
            {
                "content": "Fashion industry accounts for 10% of global carbon emissions. Key reduction strategies include renewable energy in manufacturing, sustainable shipping, and reduced water usage in textile production.",
                "source": "Fashion Carbon Report 2026",
                "metadata": {"topic": "emissions", "percentage": "10%"}
            }
        ]
        
        for item in sustainability_knowledge:
            self.add_chunk(item["content"], KnowledgeCategory.SUSTAINABILITY, item["source"], item["metadata"])
        
        # Technology knowledge
        tech_knowledge = [
            {
                "content": "AI in fashion enables personalized styling, trend forecasting, and supply chain optimization. Machine learning models analyze social media, runway shows, and sales data to predict upcoming trends with 85% accuracy.",
                "source": "Fashion Tech Report 2026",
                "metadata": {"topic": "AI", "accuracy": "85%"}
            },
            {
                "content": "Virtual try-on technology uses AR and AI to allow customers to visualize clothing without physical fitting. Adoption increased 300% since 2024, reducing return rates by up to 40%.",
                "source": "Retail Technology Review",
                "metadata": {"topic": "virtual_try_on", "return_reduction": "40%"}
            },
            {
                "content": "Blockchain in fashion provides supply chain transparency and authentication. Luxury brands use NFTs for digital ownership certificates and to combat counterfeiting.",
                "source": "Fashion Blockchain Guide",
                "metadata": {"topic": "blockchain", "use_case": "authentication"}
            },
            {
                "content": "3D printing revolutionizes fashion production with on-demand manufacturing, reducing waste and enabling mass customization. Adidas and Nike lead in 3D-printed footwear.",
                "source": "3D Fashion Manufacturing Report",
                "metadata": {"topic": "3D_printing", "leaders": ["Adidas", "Nike"]}
            },
            {
                "content": "Digital fashion and virtual clothing for metaverse platforms represent a $50 billion market opportunity. Brands create digital-only collections for gaming and social platforms.",
                "source": "Metaverse Fashion Report",
                "metadata": {"topic": "digital_fashion", "market": "$50B"}
            }
        ]
        
        for item in tech_knowledge:
            self.add_chunk(item["content"], KnowledgeCategory.TECHNOLOGY, item["source"], item["metadata"])
        
        # Trends knowledge
        trends_knowledge = [
            {
                "content": "2026 fashion trends emphasize quiet luxury, understated elegance, and investment dressing. Minimalist aesthetics with premium materials dominate high-end fashion.",
                "source": "Fashion Trend Forecast 2026",
                "metadata": {"topic": "quiet_luxury", "year": 2026}
            },
            {
                "content": "Color trends for 2026 include earthy tones, sage green, warm terracotta, and classic navy. Pantone's Color of the Year influences seasonal collections across all market segments.",
                "source": "Color Trend Report 2026",
                "metadata": {"topic": "colors", "year": 2026}
            },
            {
                "content": "Athleisure continues to evolve with technical fabrics meeting luxury design. The market reaches $450 billion globally, driven by work-from-home culture and wellness focus.",
                "source": "Athleisure Market Report",
                "metadata": {"topic": "athleisure", "market_size": "$450B"}
            },
            {
                "content": "Gender-fluid fashion gains mainstream acceptance with major brands launching unisex collections. 56% of Gen Z consumers prefer gender-neutral clothing options.",
                "source": "Gender-Fluid Fashion Study",
                "metadata": {"topic": "gender_fluid", "gen_z_preference": "56%"}
            },
            {
                "content": "Vintage and secondhand fashion represents the fastest-growing segment, with 40% of consumers buying pre-owned items. Platforms like Depop, Vestiaire Collective, and ThredUp lead the market.",
                "source": "Resale Fashion Report",
                "metadata": {"topic": "vintage", "consumer_adoption": "40%"}
            }
        ]
        
        for item in trends_knowledge:
            self.add_chunk(item["content"], KnowledgeCategory.TRENDS, item["source"], item["metadata"])
        
        # Designers knowledge
        designers_knowledge = [
            {
                "content": "Emerging designers to watch in 2026 include Nensi Dojaka (Albanian-British), Peter Do (Vietnamese-American), and Maximilian Davis (British-Trinidadian). They represent a new wave of diverse, sustainability-conscious talent.",
                "source": "Emerging Designers Guide 2026",
                "metadata": {"topic": "emerging", "year": 2026}
            },
            {
                "content": "Luxury house creative director changes reshape fashion landscape. New appointments bring fresh perspectives while honoring heritage. Key moves include Pharrell at Louis Vuitton Men's and Chemena Kamali at Chloé.",
                "source": "Fashion Leadership Report",
                "metadata": {"topic": "creative_directors", "year": 2026}
            },
            {
                "content": "Independent designers leverage direct-to-consumer models and social media to build global brands without traditional retail. Instagram and TikTok become primary discovery platforms.",
                "source": "Independent Fashion Report",
                "metadata": {"topic": "independent", "channels": ["Instagram", "TikTok"]}
            }
        ]
        
        for item in designers_knowledge:
            self.add_chunk(item["content"], KnowledgeCategory.DESIGNERS, item["source"], item["metadata"])
        
        # Materials knowledge
        materials_knowledge = [
            {
                "content": "Innovative sustainable materials include Piñatex (pineapple leather), Mylo (mushroom leather), and Econyl (regenerated nylon from ocean waste). These alternatives reduce reliance on animal and petroleum-based materials.",
                "source": "Sustainable Materials Guide",
                "metadata": {"topic": "alternatives", "materials": ["Piñatex", "Mylo", "Econyl"]}
            },
            {
                "content": "Lab-grown materials revolutionize fashion with bio-fabricated silk, leather, and cotton. Companies like Bolt Threads and Modern Meadow lead development of animal-free luxury materials.",
                "source": "Bio-Fabrication Report",
                "metadata": {"topic": "lab_grown", "companies": ["Bolt Threads", "Modern Meadow"]}
            },
            {
                "content": "Smart textiles integrate technology into fabrics for temperature regulation, health monitoring, and color-changing properties. Applications range from athletic wear to medical garments.",
                "source": "Smart Textiles Innovation Report",
                "metadata": {"topic": "smart_textiles", "applications": ["athletic", "medical"]}
            }
        ]
        
        for item in materials_knowledge:
            self.add_chunk(item["content"], KnowledgeCategory.MATERIALS, item["source"], item["metadata"])
        
        # Business knowledge
        business_knowledge = [
            {
                "content": "Global fashion market valued at $1.7 trillion in 2026. Asia-Pacific leads growth with China and India as key markets. E-commerce represents 30% of total fashion sales globally.",
                "source": "Global Fashion Market Report 2026",
                "metadata": {"topic": "market_size", "value": "$1.7T", "ecommerce_share": "30%"}
            },
            {
                "content": "Fashion retail transformation accelerates with omnichannel strategies. Successful brands integrate online and offline experiences through click-and-collect, virtual appointments, and experiential stores.",
                "source": "Retail Transformation Report",
                "metadata": {"topic": "omnichannel", "strategies": ["click-and-collect", "virtual_appointments"]}
            },
            {
                "content": "Supply chain resilience becomes priority after global disruptions. Nearshoring, diversified sourcing, and inventory optimization help brands manage risk and reduce lead times.",
                "source": "Fashion Supply Chain Report",
                "metadata": {"topic": "supply_chain", "strategies": ["nearshoring", "diversification"]}
            }
        ]
        
        for item in business_knowledge:
            self.add_chunk(item["content"], KnowledgeCategory.BUSINESS, item["source"], item["metadata"])
        
        # Beauty knowledge
        beauty_knowledge = [
            {
                "content": "Clean beauty movement drives demand for non-toxic, sustainable cosmetics. Ingredient transparency and eco-friendly packaging become standard expectations among consumers.",
                "source": "Clean Beauty Report 2026",
                "metadata": {"topic": "clean_beauty", "focus": ["transparency", "packaging"]}
            },
            {
                "content": "Skincare-makeup hybrid products blur category lines. Products offering skincare benefits with cosmetic coverage gain popularity, led by brands like Ilia, Kosas, and Merit.",
                "source": "Beauty Hybrid Trends",
                "metadata": {"topic": "hybrid", "brands": ["Ilia", "Kosas", "Merit"]}
            },
            {
                "content": "Personalized beauty powered by AI analyzes skin type, concerns, and preferences to recommend customized routines. Brands offer bespoke formulations based on individual data.",
                "source": "Personalized Beauty Report",
                "metadata": {"topic": "personalization", "technology": "AI"}
            }
        ]
        
        for item in beauty_knowledge:
            self.add_chunk(item["content"], KnowledgeCategory.BEAUTY, item["source"], item["metadata"])
    
    def add_chunk(self, content: str, category: KnowledgeCategory, source: str, metadata: Dict = None) -> KnowledgeChunk:
        """Add a knowledge chunk to the base"""
        chunk_id = hashlib.md5(f"{content}{source}".encode()).hexdigest()[:16]
        
        chunk = KnowledgeChunk(
            id=chunk_id,
            content=content,
            category=category,
            source=source,
            metadata=metadata or {}
        )
        
        self.chunks[chunk_id] = chunk
        self.category_index[category].append(chunk_id)
        
        # Build keyword index
        words = re.findall(r'\b\w+\b', content.lower())
        for word in set(words):
            if len(word) > 3:
                if word not in self.keyword_index:
                    self.keyword_index[word] = []
                self.keyword_index[word].append(chunk_id)
        
        return chunk
    
    def get_chunks_by_category(self, category: KnowledgeCategory) -> List[KnowledgeChunk]:
        """Get all chunks in a category"""
        chunk_ids = self.category_index.get(category, [])
        return [self.chunks[cid] for cid in chunk_ids if cid in self.chunks]


class RAGRetriever:
    """
    Retrieval component for the RAG system.
    Finds relevant knowledge chunks for a given query.
    """
    
    def __init__(self, knowledge_base: FashionKnowledgeBase):
        self.kb = knowledge_base
    
    def retrieve(self, query: str, top_k: int = 5, categories: List[KnowledgeCategory] = None) -> RetrievalResult:
        """Retrieve relevant knowledge chunks for a query"""
        import time
        start_time = time.time()
        
        query_lower = query.lower()
        query_words = set(re.findall(r'\b\w+\b', query_lower))
        
        # Determine categories to search
        if categories is None:
            categories = self._infer_categories(query_lower)
        
        # Score all relevant chunks
        scored_chunks: List[Tuple[KnowledgeChunk, float]] = []
        
        for category in categories:
            for chunk in self.kb.get_chunks_by_category(category):
                score = self._calculate_relevance(query_words, chunk)
                if score > 0:
                    scored_chunks.append((chunk, score))
        
        # Also search by keywords
        for word in query_words:
            if word in self.kb.keyword_index:
                for chunk_id in self.kb.keyword_index[word]:
                    if chunk_id in self.kb.chunks:
                        chunk = self.kb.chunks[chunk_id]
                        score = self._calculate_relevance(query_words, chunk)
                        if score > 0 and not any(c.id == chunk.id for c, _ in scored_chunks):
                            scored_chunks.append((chunk, score))
        
        # Sort by score and get top_k
        scored_chunks.sort(key=lambda x: x[1], reverse=True)
        top_chunks = [chunk for chunk, score in scored_chunks[:top_k]]
        
        # Update relevance scores
        for i, chunk in enumerate(top_chunks):
            chunk.relevance_score = scored_chunks[i][1] if i < len(scored_chunks) else 0
        
        retrieval_time = (time.time() - start_time) * 1000
        
        return RetrievalResult(
            query=query,
            chunks=top_chunks,
            total_found=len(scored_chunks),
            categories_searched=[c.value for c in categories],
            retrieval_time_ms=retrieval_time
        )
    
    def _infer_categories(self, query: str) -> List[KnowledgeCategory]:
        """Infer relevant categories from query"""
        categories = []
        
        category_keywords = {
            KnowledgeCategory.SUSTAINABILITY: ["sustainable", "eco", "green", "ethical", "circular", "recycl"],
            KnowledgeCategory.TECHNOLOGY: ["tech", "ai", "digital", "virtual", "blockchain", "3d", "innovation"],
            KnowledgeCategory.TRENDS: ["trend", "style", "fashion", "season", "color", "look"],
            KnowledgeCategory.DESIGNERS: ["designer", "brand", "creative", "collection", "runway"],
            KnowledgeCategory.MATERIALS: ["material", "fabric", "textile", "leather", "cotton", "silk"],
            KnowledgeCategory.BUSINESS: ["market", "retail", "sales", "business", "industry", "commerce"],
            KnowledgeCategory.BEAUTY: ["beauty", "skincare", "makeup", "cosmetic", "skin"],
            KnowledgeCategory.CULTURE: ["culture", "art", "heritage", "tradition"],
            KnowledgeCategory.HISTORY: ["history", "vintage", "classic", "heritage"]
        }
        
        for category, keywords in category_keywords.items():
            if any(kw in query for kw in keywords):
                categories.append(category)
        
        # Default to trends if no specific category found
        if not categories:
            categories = [KnowledgeCategory.TRENDS, KnowledgeCategory.SUSTAINABILITY, KnowledgeCategory.TECHNOLOGY]
        
        return categories
    
    def _calculate_relevance(self, query_words: set, chunk: KnowledgeChunk) -> float:
        """Calculate relevance score between query and chunk"""
        chunk_words = set(re.findall(r'\b\w+\b', chunk.content.lower()))
        
        # Word overlap
        overlap = len(query_words & chunk_words)
        if overlap == 0:
            return 0.0
        
        # Jaccard similarity
        union = len(query_words | chunk_words)
        jaccard = overlap / union if union > 0 else 0
        
        # Boost for exact phrase matches
        query_str = " ".join(sorted(query_words))
        if query_str in chunk.content.lower():
            jaccard *= 1.5
        
        # Boost for category relevance
        category_boost = 1.0
        if chunk.category in [KnowledgeCategory.TRENDS, KnowledgeCategory.SUSTAINABILITY]:
            category_boost = 1.2
        
        return min(jaccard * category_boost, 1.0)


class RAGGenerator:
    """
    Generation component that augments LLM responses with retrieved knowledge.
    """
    
    def __init__(self, retriever: RAGRetriever):
        self.retriever = retriever
    
    def build_context(self, query: str, top_k: int = 5) -> Tuple[str, RetrievalResult]:
        """Build context from retrieved knowledge"""
        result = self.retriever.retrieve(query, top_k=top_k)
        
        if not result.chunks:
            return "", result
        
        context_parts = ["### Relevant Knowledge:\n"]
        
        for i, chunk in enumerate(result.chunks, 1):
            context_parts.append(f"**[{i}] {chunk.category.value.title()}** (Source: {chunk.source})")
            context_parts.append(f"{chunk.content}\n")
        
        context = "\n".join(context_parts)
        return context, result
    
    def augment_prompt(self, query: str, system_prompt: str = None) -> Tuple[str, str, RetrievalResult]:
        """Augment a prompt with retrieved knowledge"""
        context, result = self.build_context(query)
        
        augmented_system = system_prompt or ""
        if context:
            augmented_system += f"\n\n{context}"
        
        return augmented_system, query, result


class RAGSystem:
    """
    Complete RAG system combining retrieval and generation.
    """
    
    def __init__(self):
        self.knowledge_base = FashionKnowledgeBase()
        self.retriever = RAGRetriever(self.knowledge_base)
        self.generator = RAGGenerator(self.retriever)
    
    def retrieve(self, query: str, top_k: int = 5, categories: List[KnowledgeCategory] = None) -> RetrievalResult:
        """Retrieve relevant knowledge"""
        return self.retriever.retrieve(query, top_k, categories)
    
    def augment_query(self, query: str, system_prompt: str = None) -> Dict:
        """Augment a query with relevant knowledge"""
        augmented_system, augmented_query, result = self.generator.augment_prompt(query, system_prompt)
        
        return {
            "original_query": query,
            "augmented_system_prompt": augmented_system,
            "augmented_query": augmented_query,
            "retrieval_result": result.to_dict(),
            "knowledge_used": len(result.chunks)
        }
    
    def add_knowledge(self, content: str, category: str, source: str, metadata: Dict = None) -> Dict:
        """Add new knowledge to the system"""
        try:
            cat = KnowledgeCategory(category.lower())
        except ValueError:
            cat = KnowledgeCategory.TRENDS
        
        chunk = self.knowledge_base.add_chunk(content, cat, source, metadata)
        return chunk.to_dict()
    
    def get_knowledge_stats(self) -> Dict:
        """Get statistics about the knowledge base"""
        stats = {
            "total_chunks": len(self.knowledge_base.chunks),
            "categories": {},
            "keywords_indexed": len(self.knowledge_base.keyword_index)
        }
        
        for category in KnowledgeCategory:
            count = len(self.knowledge_base.category_index[category])
            stats["categories"][category.value] = count
        
        return stats


# Global instance
rag_system = RAGSystem()


def get_rag_system() -> RAGSystem:
    """Get the global RAG system"""
    return rag_system
