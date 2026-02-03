"""
McLeuker AI V5.1 - Intent Router
================================
Prevents domain overfitting by properly classifying user intent.

Design Principles:
1. FLEXIBLE classification - not everything is fashion
2. SMART defaults - assume general query unless clear indicators
3. NO excessive questions - answer first, clarify later
4. DOMAIN hints - use keywords, not rigid rules
"""

from dataclasses import dataclass
from enum import Enum
from typing import Optional, List
import re

# Use absolute imports instead of relative
from src.schemas.response_contract import IntentType, DomainType


@dataclass
class IntentResult:
    """Result of intent classification"""
    intent_type: IntentType
    domain: DomainType
    confidence: float
    search_mode: str  # quick, deep, auto
    needs_clarification: bool
    clarification_question: Optional[str] = None
    detected_keywords: List[str] = None
    
    def __post_init__(self):
        if self.detected_keywords is None:
            self.detected_keywords = []


class IntentRouter:
    """
    V5.1 Intent Router - Smart classification without excessive questions
    """
    
    # Domain keyword patterns - expanded beyond fashion
    DOMAIN_PATTERNS = {
        DomainType.FASHION: [
            r'\b(fashion|style|outfit|clothing|wear|dress|trend|runway|catwalk|designer|couture)\b',
            r'\b(ss\d{2}|fw\d{2}|spring|summer|fall|winter)\s*(collection|season|show)\b',
            r'\b(vogue|elle|harper|bazaar|gq|esquire)\b'
        ],
        DomainType.BEAUTY: [
            r'\b(beauty|makeup|cosmetic|skincare|skin\s*care|foundation|lipstick|mascara)\b',
            r'\b(serum|moisturizer|cleanser|toner|sunscreen|spf)\b',
            r'\b(glow|radiant|hydrat|anti-aging|wrinkle)\b'
        ],
        DomainType.LIFESTYLE: [
            r'\b(lifestyle|wellness|fitness|health|diet|nutrition|mindfulness)\b',
            r'\b(travel|vacation|destination|hotel|resort)\b',
            r'\b(home|decor|interior|design|furniture)\b'
        ],
        DomainType.CULTURE: [
            r'\b(culture|art|music|film|movie|book|literature|exhibition)\b',
            r'\b(celebrity|influencer|social\s*media|viral|trending)\b',
            r'\b(event|festival|concert|premiere|award)\b'
        ],
        DomainType.SUSTAINABILITY: [
            r'\b(sustainab|eco|green|organic|ethical|fair\s*trade)\b',
            r'\b(recycl|upcycl|circular|zero\s*waste|carbon)\b',
            r'\b(environment|climate|biodegradable|renewable)\b'
        ],
        DomainType.TECHNOLOGY: [
            r'\b(tech|digital|ai|artificial\s*intelligence|machine\s*learning)\b',
            r'\b(app|software|platform|startup|innovation)\b',
            r'\b(wearable|smart|iot|blockchain|nft)\b'
        ],
        DomainType.GENERAL: []  # Fallback
    }
    
    # Intent patterns
    INTENT_PATTERNS = {
        IntentType.RESEARCH: [
            r'\b(research|analyze|study|investigate|explore|deep\s*dive)\b',
            r'\b(comprehensive|detailed|thorough|in-depth|complete)\b',
            r'\b(report|analysis|overview|summary)\b'
        ],
        IntentType.SHOPPING: [
            r'\b(buy|purchase|shop|order|get|find|where\s*to\s*buy)\b',
            r'\b(price|cost|affordable|budget|expensive|cheap)\b',
            r'\b(recommend|suggestion|best|top|review)\b'
        ],
        IntentType.ADVICE: [
            r'\b(advice|tip|help|guide|how\s*to|should\s*i)\b',
            r'\b(recommend|suggest|what\s*do\s*you\s*think)\b',
            r'\b(opinion|perspective|insight)\b'
        ],
        IntentType.CREATIVE: [
            r'\b(create|generate|make|design|write|compose)\b',
            r'\b(mood\s*board|inspiration|idea|concept)\b',
            r'\b(image|visual|graphic|presentation)\b'
        ],
        IntentType.DATA: [
            r'\b(data|statistic|number|figure|metric|kpi)\b',
            r'\b(excel|spreadsheet|csv|chart|graph|table)\b',
            r'\b(compare|comparison|versus|vs)\b'
        ],
        IntentType.GENERAL: []  # Fallback
    }
    
    def __init__(self):
        self.last_intent = None
        self.context_history = []
    
    def classify(self, query: str, context: Optional[List[str]] = None) -> IntentResult:
        """
        Classify user intent without excessive questions.
        
        Strategy:
        1. Check for explicit domain/intent indicators
        2. Use context from conversation history
        3. Default to GENERAL if unclear (don't ask!)
        4. Only ask clarification for truly ambiguous cases
        """
        query_lower = query.lower()
        
        # Detect domain
        domain, domain_confidence, domain_keywords = self._detect_domain(query_lower)
        
        # Detect intent type
        intent_type, intent_confidence, intent_keywords = self._detect_intent(query_lower)
        
        # Determine search mode
        search_mode = self._determine_search_mode(query_lower, intent_type)
        
        # Check if clarification is truly needed (very rare!)
        needs_clarification, clarification_question = self._check_clarification_need(
            query_lower, domain, intent_type, domain_confidence, intent_confidence
        )
        
        # Combine keywords
        all_keywords = domain_keywords + intent_keywords
        
        # Calculate overall confidence
        overall_confidence = (domain_confidence + intent_confidence) / 2
        
        result = IntentResult(
            intent_type=intent_type,
            domain=domain,
            confidence=overall_confidence,
            search_mode=search_mode,
            needs_clarification=needs_clarification,
            clarification_question=clarification_question,
            detected_keywords=all_keywords
        )
        
        # Store for context
        self.last_intent = result
        
        return result
    
    def _detect_domain(self, query: str) -> tuple:
        """Detect the domain with confidence score"""
        best_domain = DomainType.GENERAL
        best_score = 0.0
        best_keywords = []
        
        for domain, patterns in self.DOMAIN_PATTERNS.items():
            if not patterns:
                continue
                
            keywords = []
            score = 0.0
            
            for pattern in patterns:
                matches = re.findall(pattern, query, re.IGNORECASE)
                if matches:
                    keywords.extend(matches)
                    score += len(matches) * 0.3
            
            if score > best_score:
                best_score = score
                best_domain = domain
                best_keywords = keywords
        
        # Cap confidence at 1.0
        confidence = min(best_score, 1.0) if best_score > 0 else 0.3
        
        return best_domain, confidence, best_keywords
    
    def _detect_intent(self, query: str) -> tuple:
        """Detect the intent type with confidence score"""
        best_intent = IntentType.GENERAL
        best_score = 0.0
        best_keywords = []
        
        for intent, patterns in self.INTENT_PATTERNS.items():
            if not patterns:
                continue
                
            keywords = []
            score = 0.0
            
            for pattern in patterns:
                matches = re.findall(pattern, query, re.IGNORECASE)
                if matches:
                    keywords.extend(matches)
                    score += len(matches) * 0.3
            
            if score > best_score:
                best_score = score
                best_intent = intent
                best_keywords = keywords
        
        # Cap confidence at 1.0
        confidence = min(best_score, 1.0) if best_score > 0 else 0.3
        
        return best_intent, confidence, best_keywords
    
    def _determine_search_mode(self, query: str, intent_type: IntentType) -> str:
        """Determine search mode based on query and intent"""
        # Deep search indicators
        deep_patterns = [
            r'\b(comprehensive|detailed|thorough|in-depth|complete|full)\b',
            r'\b(research|analyze|study|investigate|deep\s*dive)\b',
            r'\b(all|everything|entire|whole)\b'
        ]
        
        # Quick search indicators
        quick_patterns = [
            r'\b(quick|fast|brief|simple|short|summary)\b',
            r'\b(just|only|main|key|top)\b'
        ]
        
        for pattern in deep_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return "deep"
        
        for pattern in quick_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                return "quick"
        
        # Default based on intent
        if intent_type == IntentType.RESEARCH:
            return "deep"
        elif intent_type == IntentType.SHOPPING:
            return "quick"
        
        return "auto"
    
    def _check_clarification_need(
        self, 
        query: str, 
        domain: DomainType, 
        intent_type: IntentType,
        domain_confidence: float,
        intent_confidence: float
    ) -> tuple:
        """
        Check if clarification is truly needed.
        
        V5.1 Philosophy: Almost NEVER ask for clarification!
        - Answer first, refine later
        - Use smart defaults
        - Only ask if query is truly incomprehensible
        """
        # Very short queries might need clarification
        words = query.split()
        if len(words) < 2:
            return True, "Could you tell me more about what you're looking for?"
        
        # If both confidence scores are very low, might need help
        if domain_confidence < 0.2 and intent_confidence < 0.2:
            # But still try to answer! Only ask if truly stuck
            return False, None
        
        # Default: NO clarification needed
        return False, None


# Global instance
intent_router = IntentRouter()
