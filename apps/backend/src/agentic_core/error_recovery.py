"""
Error Recovery & Self-Healing System
=====================================

Provides automatic error detection, diagnosis, and recovery
for agent execution failures.

Features:
- Automatic retry with exponential backoff
- Error classification and diagnosis
- Recovery strategy selection
- Fallback agent activation
- State preservation and rollback
"""

import asyncio
import json
import logging
import traceback
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Dict, List, Optional, Type, AsyncGenerator
import openai

logger = logging.getLogger(__name__)


class ErrorType(Enum):
    """Types of errors that can occur during execution."""
    NETWORK = "network"  # Network/connectivity issues
    TIMEOUT = "timeout"  # Execution timeout
    RATE_LIMIT = "rate_limit"  # API rate limiting
    AUTHENTICATION = "authentication"  # Auth failures
    VALIDATION = "validation"  # Input validation errors
    RESOURCE_UNAVAILABLE = "resource_unavailable"  # Missing resources
    EXECUTION = "execution"  # Runtime execution errors
    LLM_ERROR = "llm_error"  # LLM API errors
    BROWSER_ERROR = "browser_error"  # Browser automation errors
    FILE_ERROR = "file_error"  # File operation errors
    UNKNOWN = "unknown"  # Unclassified errors


class RecoveryStrategy(Enum):
    """Strategies for error recovery."""
    RETRY = "retry"  # Simple retry
    RETRY_WITH_BACKOFF = "retry_with_backoff"  # Retry with exponential backoff
    FALLBACK_AGENT = "fallback_agent"  # Switch to fallback agent
    DECOMPOSE_TASK = "decompose_task"  # Break task into smaller parts
    SKIP_AND_CONTINUE = "skip_and_continue"  # Skip failed step
    MANUAL_INTERVENTION = "manual_intervention"  # Require user input
    ABORT = "abort"  # Stop execution


@dataclass
class ErrorRecord:
    """Record of an error that occurred."""
    error_type: ErrorType
    message: str
    stack_trace: Optional[str] = None
    context: Dict[str, Any] = field(default_factory=dict)
    timestamp: str = ""
    recovery_attempts: int = 0
    max_recovery_attempts: int = 3
    
    def __post_init__(self):
        if not self.timestamp:
            from datetime import datetime
            self.timestamp = datetime.now().isoformat()
    
    def to_dict(self) -> Dict:
        return {
            "error_type": self.error_type.value,
            "message": self.message,
            "stack_trace": self.stack_trace,
            "context": self.context,
            "timestamp": self.timestamp,
            "recovery_attempts": self.recovery_attempts,
            "max_recovery_attempts": self.max_recovery_attempts,
        }


@dataclass
class RecoveryResult:
    """Result of a recovery attempt."""
    success: bool
    strategy_used: RecoveryStrategy
    error_record: ErrorRecord
    new_context: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    continue_execution: bool = True


class ErrorClassifier:
    """Classifies errors into types for targeted recovery."""
    
    # Error patterns for classification
    PATTERNS = {
        ErrorType.NETWORK: [
            "connection", "timeout", "network", "unreachable",
            "refused", "reset", "dns", "certificate"
        ],
        ErrorType.RATE_LIMIT: [
            "rate limit", "too many requests", "429", "quota exceeded",
            "throttle", "limit exceeded"
        ],
        ErrorType.AUTHENTICATION: [
            "unauthorized", "forbidden", "401", "403", "auth",
            "credential", "token expired", "api key"
        ],
        ErrorType.TIMEOUT: [
            "timeout", "timed out", "deadline exceeded"
        ],
        ErrorType.VALIDATION: [
            "validation", "invalid", "required", "missing",
            "format", "schema", "parse"
        ],
        ErrorType.RESOURCE_UNAVAILABLE: [
            "not found", "404", "missing", "unavailable",
            "does not exist", "no such"
        ],
        ErrorType.LLM_ERROR: [
            "openai", "anthropic", "grok", "kimi", "llm",
            "model", "completion", "chat.completions"
        ],
        ErrorType.BROWSER_ERROR: [
            "playwright", "browser", "page", "element not found",
            "selector", "navigation", "frame"
        ],
        ErrorType.FILE_ERROR: [
            "file not found", "permission denied", "ioerror",
            "oserror", "read", "write", "directory"
        ],
    }
    
    @classmethod
    def classify(cls, error: Exception) -> ErrorType:
        """Classify an error based on its message and type."""
        error_str = str(error).lower()
        error_type_name = type(error).__name__.lower()
        
        for error_type, patterns in cls.PATTERNS.items():
            for pattern in patterns:
                if pattern in error_str or pattern in error_type_name:
                    return error_type
        
        return ErrorType.UNKNOWN


class RecoveryManager:
    """
    Manages error recovery for agent execution.
    
    Usage:
        recovery = RecoveryManager(llm_client)
        
        @recovery.with_recovery(max_retries=3)
        async def execute_task():
            # Task execution
            pass
    """
    
    def __init__(self, llm_client: openai.AsyncOpenAI, model: str = "kimi-k2.5"):
        self.llm_client = llm_client
        self.model = model
        self._error_history: List[ErrorRecord] = []
        self._recovery_strategies: Dict[ErrorType, List[RecoveryStrategy]] = {
            ErrorType.NETWORK: [RecoveryStrategy.RETRY_WITH_BACKOFF, RecoveryStrategy.FALLBACK_AGENT],
            ErrorType.TIMEOUT: [RecoveryStrategy.RETRY_WITH_BACKOFF, RecoveryStrategy.DECOMPOSE_TASK],
            ErrorType.RATE_LIMIT: [RecoveryStrategy.RETRY_WITH_BACKOFF],
            ErrorType.AUTHENTICATION: [RecoveryStrategy.MANUAL_INTERVENTION, RecoveryStrategy.ABORT],
            ErrorType.VALIDATION: [RecoveryStrategy.RETRY, RecoveryStrategy.DECOMPOSE_TASK],
            ErrorType.RESOURCE_UNAVAILABLE: [RecoveryStrategy.SKIP_AND_CONTINUE, RecoveryStrategy.FALLBACK_AGENT],
            ErrorType.EXECUTION: [RecoveryStrategy.RETRY, RecoveryStrategy.DECOMPOSE_TASK, RecoveryStrategy.FALLBACK_AGENT],
            ErrorType.LLM_ERROR: [RecoveryStrategy.RETRY_WITH_BACKOFF, RecoveryStrategy.FALLBACK_AGENT],
            ErrorType.BROWSER_ERROR: [RecoveryStrategy.RETRY, RecoveryStrategy.SKIP_AND_CONTINUE],
            ErrorType.FILE_ERROR: [RecoveryStrategy.RETRY, RecoveryStrategy.SKIP_AND_CONTINUE],
            ErrorType.UNKNOWN: [RecoveryStrategy.RETRY, RecoveryStrategy.FALLBACK_AGENT, RecoveryStrategy.ABORT],
        }
    
    def with_recovery(
        self,
        max_retries: int = 3,
        fallback_handler: Optional[Callable] = None,
        on_error: Optional[Callable] = None,
    ):
        """Decorator to add recovery to a function."""
        def decorator(func: Callable):
            async def wrapper(*args, **kwargs):
                last_error = None
                
                for attempt in range(max_retries):
                    try:
                        return await func(*args, **kwargs)
                    except Exception as e:
                        last_error = e
                        error_type = ErrorClassifier.classify(e)
                        
                        error_record = ErrorRecord(
                            error_type=error_type,
                            message=str(e),
                            stack_trace=traceback.format_exc(),
                            context={"attempt": attempt, "args": str(args), "kwargs": str(kwargs)},
                            recovery_attempts=attempt,
                            max_recovery_attempts=max_retries,
                        )
                        
                        self._error_history.append(error_record)
                        
                        if on_error:
                            on_error(error_record)
                        
                        # Try recovery
                        recovery_result = await self.attempt_recovery(error_record, fallback_handler)
                        
                        if recovery_result.success:
                            logger.info(f"Recovery successful with strategy: {recovery_result.strategy_used.value}")
                            # Update kwargs with new context if needed
                            kwargs.update(recovery_result.new_context)
                            continue
                        
                        if not recovery_result.continue_execution:
                            raise e
                
                # All retries exhausted
                if last_error:
                    raise last_error
            
            return wrapper
        return decorator
    
    async def attempt_recovery(
        self,
        error_record: ErrorRecord,
        fallback_handler: Optional[Callable] = None,
    ) -> RecoveryResult:
        """
        Attempt to recover from an error.
        """
        strategies = self._recovery_strategies.get(error_record.error_type, [RecoveryStrategy.RETRY])
        
        for strategy in strategies:
            try:
                if strategy == RecoveryStrategy.RETRY:
                    return await self._retry_recovery(error_record)
                
                elif strategy == RecoveryStrategy.RETRY_WITH_BACKOFF:
                    return await self._retry_with_backoff(error_record)
                
                elif strategy == RecoveryStrategy.FALLBACK_AGENT:
                    if fallback_handler:
                        return await self._fallback_recovery(error_record, fallback_handler)
                
                elif strategy == RecoveryStrategy.DECOMPOSE_TASK:
                    return await self._decompose_recovery(error_record)
                
                elif strategy == RecoveryStrategy.SKIP_AND_CONTINUE:
                    return RecoveryResult(
                        success=True,
                        strategy_used=strategy,
                        error_record=error_record,
                        message="Skipping failed step and continuing",
                        continue_execution=True,
                    )
                
                elif strategy == RecoveryStrategy.MANUAL_INTERVENTION:
                    return RecoveryResult(
                        success=False,
                        strategy_used=strategy,
                        error_record=error_record,
                        message="Manual intervention required",
                        continue_execution=False,
                    )
                
                elif strategy == RecoveryStrategy.ABORT:
                    return RecoveryResult(
                        success=False,
                        strategy_used=strategy,
                        error_record=error_record,
                        message="Execution aborted",
                        continue_execution=False,
                    )
            
            except Exception as e:
                logger.warning(f"Recovery strategy {strategy.value} failed: {e}")
                continue
        
        # All strategies failed
        return RecoveryResult(
            success=False,
            strategy_used=RecoveryStrategy.ABORT,
            error_record=error_record,
            message="All recovery strategies failed",
            continue_execution=False,
        )
    
    async def _retry_recovery(self, error_record: ErrorRecord) -> RecoveryResult:
        """Simple retry recovery."""
        return RecoveryResult(
            success=True,
            strategy_used=RecoveryStrategy.RETRY,
            error_record=error_record,
            message="Retrying operation",
            continue_execution=True,
        )
    
    async def _retry_with_backoff(self, error_record: ErrorRecord) -> RecoveryResult:
        """Retry with exponential backoff."""
        attempt = error_record.recovery_attempts
        delay = min(2 ** attempt, 60)  # Max 60 seconds
        
        logger.info(f"Retrying with backoff: {delay}s (attempt {attempt + 1})")
        await asyncio.sleep(delay)
        
        return RecoveryResult(
            success=True,
            strategy_used=RecoveryStrategy.RETRY_WITH_BACKOFF,
            error_record=error_record,
            message=f"Retrying after {delay}s backoff",
            continue_execution=True,
        )
    
    async def _fallback_recovery(
        self,
        error_record: ErrorRecord,
        fallback_handler: Callable,
    ) -> RecoveryResult:
        """Switch to fallback handler."""
        try:
            result = await fallback_handler(error_record)
            return RecoveryResult(
                success=True,
                strategy_used=RecoveryStrategy.FALLBACK_AGENT,
                error_record=error_record,
                message="Fallback handler executed successfully",
                continue_execution=True,
                new_context={"fallback_result": result},
            )
        except Exception as e:
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.FALLBACK_AGENT,
                error_record=error_record,
                message=f"Fallback handler failed: {e}",
                continue_execution=True,
            )
    
    async def _decompose_recovery(self, error_record: ErrorRecord) -> RecoveryResult:
        """Decompose task into smaller parts."""
        # Use LLM to suggest task decomposition
        messages = [
            {
                "role": "system",
                "content": """The following task failed. Suggest how to break it into smaller, simpler subtasks.

Respond with JSON:
{
    "decomposition": [
        {"step": 1, "description": "First simple step"},
        {"step": 2, "description": "Second simple step"}
    ],
    "reasoning": "Explanation of why this decomposition helps"
}"""
            },
            {
                "role": "user",
                "content": f"Error: {error_record.message}\n\nContext: {json.dumps(error_record.context)}"
            }
        ]
        
        try:
            response = await self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=1024,
                response_format={"type": "json_object"},
            )
            
            result = json.loads(response.choices[0].message.content)
            
            return RecoveryResult(
                success=True,
                strategy_used=RecoveryStrategy.DECOMPOSE_TASK,
                error_record=error_record,
                message="Task decomposed into smaller steps",
                continue_execution=True,
                new_context={"decomposition": result.get("decomposition", [])},
            )
            
        except Exception as e:
            return RecoveryResult(
                success=False,
                strategy_used=RecoveryStrategy.DECOMPOSE_TASK,
                error_record=error_record,
                message=f"Decomposition failed: {e}",
                continue_execution=True,
            )
    
    def get_error_summary(self) -> Dict[str, Any]:
        """Get a summary of errors and recoveries."""
        if not self._error_history:
            return {"total_errors": 0}
        
        error_counts = {}
        recovery_counts = {}
        
        for record in self._error_history:
            error_type = record.error_type.value
            error_counts[error_type] = error_counts.get(error_type, 0) + 1
        
        return {
            "total_errors": len(self._error_history),
            "error_breakdown": error_counts,
            "recent_errors": [e.to_dict() for e in self._error_history[-5:]],
        }
    
    def clear_history(self):
        """Clear error history."""
        self._error_history = []


# Singleton instance
_recovery_manager: Optional[RecoveryManager] = None


def get_recovery_manager(llm_client: openai.AsyncOpenAI = None) -> RecoveryManager:
    """Get or create the Recovery Manager singleton."""
    global _recovery_manager
    if _recovery_manager is None and llm_client:
        _recovery_manager = RecoveryManager(llm_client)
    return _recovery_manager
