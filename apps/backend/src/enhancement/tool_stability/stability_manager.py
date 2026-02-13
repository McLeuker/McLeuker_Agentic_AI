"""
Stability Manager - Retry and Error Recovery
=============================================

Manages stability for tool calls:
- Retry strategies
- Circuit breaker pattern
- Error recovery
- Fallback mechanisms
"""

import asyncio
import logging
from typing import Dict, List, Optional, Any, Callable, TypeVar, Generic
from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import Enum
import functools

logger = logging.getLogger(__name__)

T = TypeVar('T')


class RetryStrategy(Enum):
    """Retry strategies"""
    FIXED = "fixed"           # Fixed delay between retries
    EXPONENTIAL = "exponential"  # Exponential backoff
    LINEAR = "linear"         # Linear increase


@dataclass
class RetryConfig:
    """Configuration for retry behavior"""
    max_retries: int = 3
    retry_delay: float = 1.0
    max_delay: float = 60.0
    strategy: RetryStrategy = RetryStrategy.EXPONENTIAL
    retry_on_exceptions: tuple = (Exception,)
    retry_on_result: Optional[Callable[[Any], bool]] = None
    
    def calculate_delay(self, attempt: int) -> float:
        """Calculate delay for given attempt"""
        if self.strategy == RetryStrategy.FIXED:
            return self.retry_delay
        
        elif self.strategy == RetryStrategy.EXPONENTIAL:
            delay = self.retry_delay * (2 ** attempt)
            return min(delay, self.max_delay)
        
        elif self.strategy == RetryStrategy.LINEAR:
            delay = self.retry_delay * (attempt + 1)
            return min(delay, self.max_delay)
        
        return self.retry_delay


class CircuitState(Enum):
    """Circuit breaker states"""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject calls
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.
    
    Prevents cascading failures by stopping calls to failing services.
    """
    
    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        half_open_max_calls: int = 3
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.half_open_max_calls = half_open_max_calls
        
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.half_open_calls = 0
    
    def can_execute(self) -> bool:
        """Check if execution is allowed"""
        if self.state == CircuitState.CLOSED:
            return True
        
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time:
                elapsed = (datetime.now() - self.last_failure_time).total_seconds()
                if elapsed >= self.recovery_timeout:
                    self.state = CircuitState.HALF_OPEN
                    self.half_open_calls = 0
                    logger.info("Circuit breaker entering half-open state")
                    return True
            return False
        
        if self.state == CircuitState.HALF_OPEN:
            return self.half_open_calls < self.half_open_max_calls
        
        return True
    
    def record_success(self):
        """Record a successful call"""
        if self.state == CircuitState.HALF_OPEN:
            self.half_open_calls += 1
            self.success_count += 1
            
            if self.success_count >= self.half_open_max_calls:
                self._reset()
                logger.info("Circuit breaker closed - service recovered")
        
        else:
            self.failure_count = 0
    
    def record_failure(self):
        """Record a failed call"""
        self.failure_count += 1
        self.last_failure_time = datetime.now()
        
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.OPEN
            logger.warning("Circuit breaker opened - service still failing")
        
        elif self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
            logger.warning(f"Circuit breaker opened after {self.failure_count} failures")
    
    def _reset(self):
        """Reset circuit breaker"""
        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.success_count = 0
        self.half_open_calls = 0
        self.last_failure_time = None


class StabilityManager:
    """
    Manages stability for tool calls.
    
    Features:
    - Configurable retry strategies
    - Circuit breaker pattern
    - Error recovery
    - Fallback mechanisms
    """
    
    def __init__(self):
        self.circuit_breakers: Dict[str, CircuitBreaker] = {}
        self.default_retry_config = RetryConfig()
    
    def get_circuit_breaker(self, service_name: str) -> CircuitBreaker:
        """Get or create circuit breaker for service"""
        if service_name not in self.circuit_breakers:
            self.circuit_breakers[service_name] = CircuitBreaker()
        return self.circuit_breakers[service_name]
    
    async def execute_with_retry(
        self,
        func: Callable[..., Any],
        *args,
        retry_config: Optional[RetryConfig] = None,
        **kwargs
    ) -> Any:
        """
        Execute function with retry logic.
        
        Args:
            func: Function to execute
            *args: Function arguments
            retry_config: Retry configuration
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
            
        Raises:
            Exception: If all retries fail
        """
        config = retry_config or self.default_retry_config
        
        last_exception = None
        
        for attempt in range(config.max_retries + 1):
            try:
                result = await func(*args, **kwargs)
                
                # Check if result indicates retry needed
                if config.retry_on_result and config.retry_on_result(result):
                    if attempt < config.max_retries:
                        delay = config.calculate_delay(attempt)
                        logger.warning(f"Retry condition met, waiting {delay}s before retry {attempt + 1}")
                        await asyncio.sleep(delay)
                        continue
                
                return result
                
            except config.retry_on_exceptions as e:
                last_exception = e
                
                if attempt < config.max_retries:
                    delay = config.calculate_delay(attempt)
                    logger.warning(f"Attempt {attempt + 1} failed: {e}, retrying in {delay}s")
                    await asyncio.sleep(delay)
                else:
                    logger.error(f"All {config.max_retries + 1} attempts failed")
        
        raise last_exception or Exception("All retries failed")
    
    async def execute_with_circuit_breaker(
        self,
        service_name: str,
        func: Callable[..., Any],
        *args,
        fallback: Optional[Callable[..., Any]] = None,
        **kwargs
    ) -> Any:
        """
        Execute function with circuit breaker.
        
        Args:
            service_name: Service identifier
            func: Function to execute
            *args: Function arguments
            fallback: Optional fallback function
            **kwargs: Function keyword arguments
            
        Returns:
            Function result or fallback result
        """
        breaker = self.get_circuit_breaker(service_name)
        
        if not breaker.can_execute():
            logger.warning(f"Circuit breaker open for {service_name}, using fallback")
            if fallback:
                return await fallback(*args, **kwargs)
            raise Exception(f"Service {service_name} unavailable and no fallback provided")
        
        try:
            result = await func(*args, **kwargs)
            breaker.record_success()
            return result
            
        except Exception as e:
            breaker.record_failure()
            
            if fallback:
                logger.warning(f"Executing fallback for {service_name}")
                return await fallback(*args, **kwargs)
            
            raise
    
    async def execute_stable(
        self,
        service_name: str,
        func: Callable[..., Any],
        *args,
        retry_config: Optional[RetryConfig] = None,
        fallback: Optional[Callable[..., Any]] = None,
        **kwargs
    ) -> Any:
        """
        Execute function with full stability measures.
        
        Combines retry logic with circuit breaker.
        
        Args:
            service_name: Service identifier
            func: Function to execute
            *args: Function arguments
            retry_config: Retry configuration
            fallback: Optional fallback function
            **kwargs: Function keyword arguments
            
        Returns:
            Function result
        """
        async def _execute_with_retry():
            return await self.execute_with_retry(
                func, *args, retry_config=retry_config, **kwargs
            )
        
        return await self.execute_with_circuit_breaker(
            service_name, _execute_with_retry, fallback=fallback
        )
    
    def create_stable_wrapper(
        self,
        service_name: str,
        retry_config: Optional[RetryConfig] = None,
        fallback: Optional[Callable[..., Any]] = None
    ):
        """
        Create a wrapper that adds stability to any function.
        
        Args:
            service_name: Service identifier
            retry_config: Retry configuration
            fallback: Optional fallback function
            
        Returns:
            Decorator function
        """
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @functools.wraps(func)
            async def wrapper(*args, **kwargs) -> T:
                return await self.execute_stable(
                    service_name, func, *args,
                    retry_config=retry_config,
                    fallback=fallback,
                    **kwargs
                )
            return wrapper
        return decorator
    
    def get_circuit_status(self) -> Dict[str, Any]:
        """Get status of all circuit breakers"""
        return {
            name: {
                "state": breaker.state.value,
                "failure_count": breaker.failure_count,
                "success_count": breaker.success_count,
            }
            for name, breaker in self.circuit_breakers.items()
        }
    
    def reset_circuit(self, service_name: str) -> bool:
        """Reset a circuit breaker"""
        if service_name in self.circuit_breakers:
            self.circuit_breakers[service_name]._reset()
            return True
        return False
