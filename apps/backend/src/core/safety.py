"""
McLeuker AI - Safety Guardrails and Validators
==============================================
Comprehensive safety system for AI outputs including:
- Input validation and sanitization
- Output validation and filtering
- Confidence scoring
- Hallucination detection
- Rate limiting
- Content moderation

Inspired by Manus AI safety architecture.
"""

import re
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict
import logging

logger = logging.getLogger(__name__)


class SafetyLevel(Enum):
    """Safety levels for content"""
    SAFE = "safe"
    CAUTION = "caution"
    WARNING = "warning"
    BLOCKED = "blocked"


class ContentCategory(Enum):
    """Categories for content moderation"""
    GENERAL = "general"
    FASHION = "fashion"
    BUSINESS = "business"
    TECHNICAL = "technical"
    SENSITIVE = "sensitive"


@dataclass
class ValidationResult:
    """Result of validation check"""
    is_valid: bool
    level: SafetyLevel
    issues: List[str] = field(default_factory=list)
    suggestions: List[str] = field(default_factory=list)
    confidence: float = 1.0
    
    def to_dict(self) -> Dict:
        return {
            "is_valid": self.is_valid,
            "level": self.level.value,
            "issues": self.issues,
            "suggestions": self.suggestions,
            "confidence": self.confidence
        }


@dataclass
class ConfidenceScore:
    """Confidence scoring for AI outputs"""
    overall: float  # 0.0 to 1.0
    factual: float  # Confidence in factual accuracy
    relevance: float  # Relevance to query
    coherence: float  # Internal consistency
    source_quality: float  # Quality of sources used
    
    def to_dict(self) -> Dict:
        return {
            "overall": round(self.overall, 3),
            "factual": round(self.factual, 3),
            "relevance": round(self.relevance, 3),
            "coherence": round(self.coherence, 3),
            "source_quality": round(self.source_quality, 3)
        }


class InputValidator:
    """Validates and sanitizes user input"""
    
    # Patterns for potentially harmful input
    INJECTION_PATTERNS = [
        r"ignore\s+(previous|all)\s+(instructions|prompts)",
        r"system\s*:\s*",
        r"<\|.*?\|>",
        r"\[INST\]",
        r"```system",
    ]
    
    # Maximum input lengths
    MAX_QUERY_LENGTH = 10000
    MAX_CONTEXT_LENGTH = 50000
    
    def __init__(self):
        self.injection_regex = re.compile(
            "|".join(self.INJECTION_PATTERNS),
            re.IGNORECASE
        )
    
    def validate(self, query: str, context: Optional[Dict] = None) -> ValidationResult:
        """Validate user input"""
        issues = []
        suggestions = []
        
        # Length check
        if len(query) > self.MAX_QUERY_LENGTH:
            issues.append(f"Query exceeds maximum length ({self.MAX_QUERY_LENGTH} chars)")
            suggestions.append("Please shorten your query")
        
        if len(query.strip()) == 0:
            issues.append("Query is empty")
            return ValidationResult(
                is_valid=False,
                level=SafetyLevel.BLOCKED,
                issues=issues
            )
        
        # Injection detection
        if self.injection_regex.search(query):
            issues.append("Potential prompt injection detected")
            return ValidationResult(
                is_valid=False,
                level=SafetyLevel.BLOCKED,
                issues=issues,
                suggestions=["Please rephrase your query"]
            )
        
        # Context validation
        if context:
            context_str = json.dumps(context)
            if len(context_str) > self.MAX_CONTEXT_LENGTH:
                issues.append("Context exceeds maximum length")
                suggestions.append("Consider reducing context size")
        
        # Determine safety level
        if issues:
            level = SafetyLevel.WARNING
        else:
            level = SafetyLevel.SAFE
        
        return ValidationResult(
            is_valid=len(issues) == 0 or level != SafetyLevel.BLOCKED,
            level=level,
            issues=issues,
            suggestions=suggestions
        )
    
    def sanitize(self, query: str) -> str:
        """Sanitize user input"""
        # Remove potential injection patterns
        sanitized = self.injection_regex.sub("", query)
        
        # Normalize whitespace
        sanitized = " ".join(sanitized.split())
        
        # Truncate if too long
        if len(sanitized) > self.MAX_QUERY_LENGTH:
            sanitized = sanitized[:self.MAX_QUERY_LENGTH]
        
        return sanitized.strip()


class OutputValidator:
    """Validates AI outputs for safety and quality"""
    
    # Patterns for potentially problematic output
    HARMFUL_PATTERNS = [
        r"(how\s+to\s+)?(make|create|build)\s+(a\s+)?bomb",
        r"(how\s+to\s+)?hack\s+(into|someone)",
        r"(illegal|illicit)\s+drugs",
    ]
    
    # Patterns for hallucination indicators
    HALLUCINATION_INDICATORS = [
        r"I\s+(don't|do\s+not)\s+have\s+access\s+to",
        r"I\s+cannot\s+(verify|confirm)",
        r"I'm\s+not\s+sure\s+(if|whether)",
        r"this\s+may\s+(not\s+be|be\s+in)?accurate",
    ]
    
    def __init__(self):
        self.harmful_regex = re.compile(
            "|".join(self.HARMFUL_PATTERNS),
            re.IGNORECASE
        )
        self.hallucination_regex = re.compile(
            "|".join(self.HALLUCINATION_INDICATORS),
            re.IGNORECASE
        )
    
    def validate(self, output: str, query: str = "") -> ValidationResult:
        """Validate AI output"""
        issues = []
        suggestions = []
        confidence = 1.0
        
        # Check for harmful content
        if self.harmful_regex.search(output):
            issues.append("Output contains potentially harmful content")
            return ValidationResult(
                is_valid=False,
                level=SafetyLevel.BLOCKED,
                issues=issues
            )
        
        # Check for hallucination indicators
        hallucination_matches = self.hallucination_regex.findall(output)
        if hallucination_matches:
            confidence -= 0.1 * len(hallucination_matches)
            if len(hallucination_matches) > 2:
                issues.append("Output may contain uncertain or unverified information")
                suggestions.append("Consider verifying key facts from primary sources")
        
        # Check output quality
        if len(output.strip()) < 50:
            issues.append("Output is very short")
            suggestions.append("Response may be incomplete")
            confidence -= 0.2
        
        # Check relevance (basic keyword matching)
        if query:
            query_words = set(query.lower().split())
            output_words = set(output.lower().split())
            overlap = len(query_words & output_words) / max(len(query_words), 1)
            if overlap < 0.1:
                issues.append("Output may not be relevant to query")
                confidence -= 0.3
        
        # Determine safety level
        if issues:
            level = SafetyLevel.CAUTION if confidence > 0.5 else SafetyLevel.WARNING
        else:
            level = SafetyLevel.SAFE
        
        return ValidationResult(
            is_valid=True,
            level=level,
            issues=issues,
            suggestions=suggestions,
            confidence=max(0.0, confidence)
        )
    
    def filter_output(self, output: str) -> str:
        """Filter potentially problematic content from output"""
        # Remove harmful patterns
        filtered = self.harmful_regex.sub("[content filtered]", output)
        return filtered


class ConfidenceScorer:
    """Calculates confidence scores for AI outputs"""
    
    def __init__(self):
        self.source_quality_weights = {
            "academic": 1.0,
            "news": 0.8,
            "official": 0.9,
            "blog": 0.5,
            "social": 0.3,
            "unknown": 0.4
        }
    
    def score(
        self,
        output: str,
        query: str,
        sources: List[Dict] = None,
        reasoning_trace: List[str] = None
    ) -> ConfidenceScore:
        """Calculate confidence score for an output"""
        
        # Factual confidence
        factual = self._score_factual(output, sources or [])
        
        # Relevance
        relevance = self._score_relevance(output, query)
        
        # Coherence
        coherence = self._score_coherence(output, reasoning_trace or [])
        
        # Source quality
        source_quality = self._score_sources(sources or [])
        
        # Overall score (weighted average)
        overall = (
            factual * 0.3 +
            relevance * 0.3 +
            coherence * 0.2 +
            source_quality * 0.2
        )
        
        return ConfidenceScore(
            overall=overall,
            factual=factual,
            relevance=relevance,
            coherence=coherence,
            source_quality=source_quality
        )
    
    def _score_factual(self, output: str, sources: List[Dict]) -> float:
        """Score factual accuracy based on source support"""
        if not sources:
            return 0.5  # Neutral without sources
        
        # Check if output contains information from sources
        source_content = " ".join([s.get("content", "") for s in sources])
        
        # Simple overlap check
        output_words = set(output.lower().split())
        source_words = set(source_content.lower().split())
        
        if not source_words:
            return 0.5
        
        overlap = len(output_words & source_words) / len(output_words)
        return min(1.0, 0.5 + overlap)
    
    def _score_relevance(self, output: str, query: str) -> float:
        """Score relevance to the original query"""
        if not query:
            return 0.7
        
        query_words = set(query.lower().split())
        output_words = set(output.lower().split())
        
        # Key term overlap
        overlap = len(query_words & output_words) / max(len(query_words), 1)
        
        return min(1.0, 0.3 + overlap * 0.7)
    
    def _score_coherence(self, output: str, reasoning_trace: List[str]) -> float:
        """Score internal coherence"""
        # Basic coherence checks
        score = 0.7
        
        # Check for structured output
        if any(marker in output for marker in ["1.", "•", "-", "##"]):
            score += 0.1
        
        # Check for reasoning trace
        if reasoning_trace and len(reasoning_trace) > 0:
            score += 0.1
        
        # Penalize very short outputs
        if len(output) < 100:
            score -= 0.2
        
        return min(1.0, max(0.0, score))
    
    def _score_sources(self, sources: List[Dict]) -> float:
        """Score quality of sources used"""
        if not sources:
            return 0.5
        
        total_weight = 0
        for source in sources:
            source_type = source.get("type", "unknown")
            weight = self.source_quality_weights.get(source_type, 0.4)
            total_weight += weight
        
        avg_weight = total_weight / len(sources)
        return avg_weight


class RateLimiter:
    """Rate limiting for API requests"""
    
    def __init__(
        self,
        requests_per_minute: int = 60,
        requests_per_hour: int = 500,
        requests_per_day: int = 5000
    ):
        self.limits = {
            "minute": requests_per_minute,
            "hour": requests_per_hour,
            "day": requests_per_day
        }
        self.requests: Dict[str, List[datetime]] = defaultdict(list)
    
    def check(self, user_id: str) -> Tuple[bool, Optional[str]]:
        """Check if user is within rate limits"""
        now = datetime.utcnow()
        user_requests = self.requests[user_id]
        
        # Clean old requests
        user_requests[:] = [
            req for req in user_requests
            if now - req < timedelta(days=1)
        ]
        
        # Check limits
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        minute_count = sum(1 for req in user_requests if req > minute_ago)
        hour_count = sum(1 for req in user_requests if req > hour_ago)
        day_count = len(user_requests)
        
        if minute_count >= self.limits["minute"]:
            return False, f"Rate limit exceeded: {self.limits['minute']} requests per minute"
        if hour_count >= self.limits["hour"]:
            return False, f"Rate limit exceeded: {self.limits['hour']} requests per hour"
        if day_count >= self.limits["day"]:
            return False, f"Rate limit exceeded: {self.limits['day']} requests per day"
        
        return True, None
    
    def record(self, user_id: str):
        """Record a request"""
        self.requests[user_id].append(datetime.utcnow())
    
    def get_usage(self, user_id: str) -> Dict:
        """Get usage statistics for a user"""
        now = datetime.utcnow()
        user_requests = self.requests.get(user_id, [])
        
        minute_ago = now - timedelta(minutes=1)
        hour_ago = now - timedelta(hours=1)
        
        return {
            "minute": {
                "used": sum(1 for req in user_requests if req > minute_ago),
                "limit": self.limits["minute"]
            },
            "hour": {
                "used": sum(1 for req in user_requests if req > hour_ago),
                "limit": self.limits["hour"]
            },
            "day": {
                "used": len([req for req in user_requests if now - req < timedelta(days=1)]),
                "limit": self.limits["day"]
            }
        }


class SafetyGuard:
    """
    Unified safety guard combining all safety components.
    """
    
    def __init__(self):
        self.input_validator = InputValidator()
        self.output_validator = OutputValidator()
        self.confidence_scorer = ConfidenceScorer()
        self.rate_limiter = RateLimiter()
    
    def validate_request(
        self,
        query: str,
        user_id: str,
        context: Optional[Dict] = None
    ) -> ValidationResult:
        """Validate an incoming request"""
        
        # Rate limit check
        allowed, error = self.rate_limiter.check(user_id)
        if not allowed:
            return ValidationResult(
                is_valid=False,
                level=SafetyLevel.BLOCKED,
                issues=[error]
            )
        
        # Input validation
        result = self.input_validator.validate(query, context)
        
        if result.is_valid:
            self.rate_limiter.record(user_id)
        
        return result
    
    def validate_response(
        self,
        output: str,
        query: str,
        sources: List[Dict] = None,
        reasoning_trace: List[str] = None
    ) -> Tuple[ValidationResult, ConfidenceScore]:
        """Validate and score an AI response"""
        
        # Output validation
        validation = self.output_validator.validate(output, query)
        
        # Confidence scoring
        confidence = self.confidence_scorer.score(
            output, query, sources, reasoning_trace
        )
        
        return validation, confidence
    
    def sanitize_input(self, query: str) -> str:
        """Sanitize user input"""
        return self.input_validator.sanitize(query)
    
    def filter_output(self, output: str) -> str:
        """Filter AI output"""
        return self.output_validator.filter_output(output)


# Global safety guard instance
safety_guard = SafetyGuard()


def get_safety_guard() -> SafetyGuard:
    """Get the global safety guard"""
    return safety_guard
