"""
McLeuker AI V5.1 - Intent Router
================================
This layer classifies user intent BEFORE calling the LLM.

Key improvements over V5:
1. Distinguishes: research | advice | shopping | doc_generation | strategy
2. Prevents domain lock-in (fashion-only bias)
3. Detects file generation requests
4. Infers tone and complexity

This fixes the "domain overfitting" issue from ChatGPT diagnosis.
"""

import re
from typing import Tuple, Dict, Any
from ..schemas.response_contract import IntentType, DomainType


class IntentRouter:
    """
    Smart intent classification without excessive clarification.
    Routes queries to appropriate processing pipelines.
    """
    
    # File generation keywords
    FILE_KEYWORDS = {
        'excel': ['excel', 'spreadsheet', 'xlsx', 'xls', 'sheet'],
        'pdf': ['pdf', 'document', 'report file'],
        'ppt': ['ppt', 'pptx', 'powerpoint', 'presentation', 'slides', 'deck'],
        'csv': ['csv', 'data file', 'export data']
    }
    
    # Intent patterns
    INTENT_PATTERNS = {
        IntentType.DOC_GENERATION: [
            r'generat[e|ing]\s+(me\s+)?(an?\s+)?excel',
            r'generat[e|ing]\s+(me\s+)?(an?\s+)?spreadsheet',
            r'generat[e|ing]\s+(me\s+)?(an?\s+)?pdf',
            r'generat[e|ing]\s+(me\s+)?(an?\s+)?ppt',
            r'generat[e|ing]\s+(me\s+)?(an?\s+)?presentation',
            r'create\s+(me\s+)?(an?\s+)?excel',
            r'create\s+(me\s+)?(an?\s+)?spreadsheet',
            r'make\s+(me\s+)?(an?\s+)?excel',
            r'give\s+me\s+(an?\s+)?excel',
            r'export\s+(to|as)\s+excel',
            r'download\s+as',
        ],
        IntentType.SHOPPING: [
            r'where\s+(can\s+i|to|should\s+i)\s+buy',
            r'recommend\s+(me\s+)?shops?',
            r'physical\s+stores?',
            r'visit\s+(these\s+)?shops?',
            r'what\s+to\s+wear',
            r'dress\s+between\s+\d+\s+and\s+\d+',
            r'budget\s+\d+',
            r'under\s+\d+\s*(euros?|\$|dollars?)',
            r'shops?\s+in\s+paris',
            r'stores?\s+in\s+',
        ],
        IntentType.COMPARISON: [
            r'compare\s+',
            r'vs\.?\s+',
            r'versus\s+',
            r'difference\s+between',
            r'which\s+is\s+better',
            r'pricing\s+across',
            r'market\s+share',
        ],
        IntentType.NEWS: [
            r"what'?s\s+(happening|going\s+on|new)",
            r'news\s+(today|this\s+week|now)',
            r'right\s+now\s+\d{4}',
            r'today\s+\d{4}',
            r'this\s+week',
            r'latest\s+',
            r'current\s+',
            r'now\s+in\s+\d{4}',
        ],
        IntentType.RESEARCH: [
            r'insights?\s+(of|about|on|for)',
            r'analysis\s+(of|about|on)',
            r'research\s+',
            r'deep\s+dive',
            r'comprehensive',
            r'master\s+(excel|sheet|list)',
            r'overview\s+of',
        ],
        IntentType.ADVICE: [
            r'what\s+should\s+i',
            r'recommend\s+(me)?',
            r'suggest',
            r'advice',
            r'tips?\s+for',
            r'how\s+to',
            r'best\s+way\s+to',
        ],
        IntentType.STRATEGY: [
            r'strategy',
            r'business\s+plan',
            r'market\s+entry',
            r'competitive\s+analysis',
            r'swot',
        ],
    }
    
    # Domain keywords
    DOMAIN_KEYWORDS = {
        DomainType.FASHION: [
            'fashion', 'clothing', 'apparel', 'runway', 'collection', 'designer',
            'dress', 'outfit', 'wear', 'style', 'trend', 'silhouette', 'couture',
            'rtw', 'ready-to-wear', 'fashion week', 'pfw', 'nyfw', 'milan',
            'dior', 'chanel', 'gucci', 'louis vuitton', 'prada', 'balenciaga'
        ],
        DomainType.BEAUTY: [
            'beauty', 'makeup', 'cosmetics', 'lipstick', 'foundation', 'mascara',
            'eyeshadow', 'blush', 'highlighter', 'beauty trends'
        ],
        DomainType.SKINCARE: [
            'skincare', 'skin care', 'serum', 'moisturizer', 'cleanser', 'retinol',
            'vitamin c', 'spf', 'sunscreen', 'acne', 'anti-aging', 'ingredients'
        ],
        DomainType.SUSTAINABILITY: [
            'sustainability', 'sustainable', 'eco', 'green', 'ethical', 'circular',
            'recycled', 'organic', 'carbon', 'emissions', 'esg', 'environment'
        ],
        DomainType.LUXURY: [
            'luxury', 'premium', 'high-end', 'exclusive', 'lvmh', 'kering',
            'hermes', 'birkin', 'handbag', 'pricing', 'market share'
        ],
        DomainType.LIFESTYLE: [
            'lifestyle', 'wellness', 'health', 'fitness', 'travel', 'experience',
            'consumer', 'behavior', 'culture', 'values'
        ],
        DomainType.RETAIL: [
            'retail', 'store', 'shop', 'ecommerce', 'omnichannel', 'brick and mortar',
            'physical store', 'boutique', 'flagship'
        ],
    }
    
    def __init__(self):
        self.last_intent = None
        self.last_domain = None
    
    def classify(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Classify user intent and domain from query.
        Returns structured classification result.
        """
        query_lower = query.lower().strip()
        
        # Detect intent
        intent = self._detect_intent(query_lower)
        
        # Detect domain (flexible, not forced)
        domain = self._detect_domain(query_lower)
        
        # Detect file type if doc generation
        file_type = self._detect_file_type(query_lower) if intent == IntentType.DOC_GENERATION else None
        
        # Calculate confidence
        confidence = self._calculate_confidence(query_lower, intent, domain)
        
        # Detect complexity
        complexity = self._detect_complexity(query_lower)
        
        # Store for context
        self.last_intent = intent
        self.last_domain = domain
        
        return {
            'intent': intent,
            'domain': domain,
            'file_type': file_type,
            'confidence': confidence,
            'complexity': complexity,
            'requires_search': self._requires_search(intent),
            'requires_file_generation': intent == IntentType.DOC_GENERATION,
            'suggested_mode': 'deep' if complexity == 'high' else 'quick'
        }
    
    def _detect_intent(self, query: str) -> IntentType:
        """Detect primary intent from query patterns"""
        for intent, patterns in self.INTENT_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return intent
        
        # Default to research for complex queries, general for simple
        if len(query.split()) > 15:
            return IntentType.RESEARCH
        return IntentType.GENERAL
    
    def _detect_domain(self, query: str) -> DomainType:
        """Detect domain - flexible, not forced"""
        scores = {domain: 0 for domain in DomainType}
        
        for domain, keywords in self.DOMAIN_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query:
                    scores[domain] += 1
        
        # Get highest scoring domain
        max_score = max(scores.values())
        if max_score > 0:
            for domain, score in scores.items():
                if score == max_score:
                    return domain
        
        return DomainType.GENERAL
    
    def _detect_file_type(self, query: str) -> str:
        """Detect requested file type"""
        for file_type, keywords in self.FILE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in query:
                    return file_type
        return 'excel'  # Default to Excel
    
    def _calculate_confidence(self, query: str, intent: IntentType, domain: DomainType) -> float:
        """Calculate classification confidence"""
        confidence = 0.7  # Base confidence
        
        # Boost for clear intent patterns
        if intent != IntentType.GENERAL:
            confidence += 0.15
        
        # Boost for clear domain keywords
        if domain != DomainType.GENERAL:
            confidence += 0.1
        
        # Reduce for very short queries
        if len(query.split()) < 5:
            confidence -= 0.1
        
        return min(0.99, max(0.5, confidence))
    
    def _detect_complexity(self, query: str) -> str:
        """Detect query complexity"""
        word_count = len(query.split())
        
        if word_count > 30 or 'comprehensive' in query or 'detailed' in query:
            return 'high'
        elif word_count > 15:
            return 'medium'
        return 'low'
    
    def _requires_search(self, intent: IntentType) -> bool:
        """Determine if intent requires web search"""
        search_intents = {
            IntentType.RESEARCH,
            IntentType.NEWS,
            IntentType.COMPARISON,
            IntentType.SHOPPING
        }
        return intent in search_intents


# Singleton instance
intent_router = IntentRouter()
