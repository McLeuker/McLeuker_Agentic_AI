"""
Hybrid Orchestrator for McLeuker AI V7
Wraps the existing V5 orchestrator with hybrid brain capabilities.

This orchestrator intelligently routes between:
- Grok: Reasoning, planning, synthesis
- Kimi: Execution, coding, tool calls
"""

import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass

from src.core.orchestrator import orchestrator as v5_orchestrator, OrchestratorResponse
from src.core.hybrid_brain import hybrid_brain, TaskType, HybridResponse
from src.config.settings import settings


class HybridOrchestrator:
    """
    Enhanced orchestrator using dual-model architecture.
    
    Wraps V5 orchestrator and adds intelligent model routing:
    - Reasoning tasks → Grok
    - Execution tasks → Kimi
    - Complex tasks → Both (hybrid)
    """
    
    def __init__(self):
        self.v5_orchestrator = v5_orchestrator
        self.hybrid_brain = hybrid_brain
        self.use_hybrid = settings.ENABLE_MULTI_MODEL and settings.is_kimi_configured()
    
    async def process(
        self,
        query: str,
        session_id: Optional[str] = None,
        mode: str = "auto",
        domain_filter: Optional[str] = None
    ) -> OrchestratorResponse:
        """
        Process query with hybrid brain routing.
        
        Flow:
        1. Determine if query needs execution
        2. Route to appropriate model(s)
        3. Return enhanced response with cost tracking
        """
        
        if not self.use_hybrid:
            # Fallback to V5 orchestrator if Kimi not configured
            return await self.v5_orchestrator.process(
                query=query,
                session_id=session_id,
                mode=mode,
                domain_filter=domain_filter
            )
        
        # Determine task type
        task_type = self._determine_task_type(query, mode)
        
        # Use V5 orchestrator for search and context
        v5_response = await self.v5_orchestrator.process(
            query=query,
            session_id=session_id,
            mode=mode,
            domain_filter=domain_filter
        )
        
        # If execution is needed, enhance with Kimi
        if task_type in [TaskType.EXECUTION, TaskType.HYBRID]:
            # Extract search results from V5 response
            search_results = []
            if v5_response.response and v5_response.response.sources:
                search_results = [
                    {
                        "title": source.title,
                        "url": source.url,
                        "snippet": source.snippet
                    }
                    for source in v5_response.response.sources
                ]
            
            # Use hybrid brain for enhanced processing
            hybrid_response = await self.hybrid_brain.think(
                query=query,
                search_results=search_results,
                task_type=task_type
            )
            
            # Enhance V5 response with hybrid brain results
            if hybrid_response.success and v5_response.response:
                # Update main content with hybrid brain output
                v5_response.response.main_content = hybrid_response.content
                
                # Add cost tracking
                v5_response.reasoning_steps.append({
                    "type": "hybrid_brain",
                    "models_used": hybrid_response.models_used,
                    "cost": hybrid_response.cost,
                    "tokens": hybrid_response.tokens_used
                })
                
                # Update credits based on actual cost
                if hybrid_response.cost > 0:
                    # Convert cost to credits (rough estimate)
                    v5_response.credits_used = max(1, int(hybrid_response.cost * 100))
        
        return v5_response
    
    async def process_stream(
        self,
        query: str,
        session_id: Optional[str] = None,
        mode: str = "auto",
        domain_filter: Optional[str] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Stream processing with hybrid brain.
        
        Currently delegates to V5 orchestrator streaming.
        Future: Add Kimi streaming for execution tasks.
        """
        async for event in self.v5_orchestrator.process_stream(
            query=query,
            session_id=session_id,
            mode=mode,
            domain_filter=domain_filter
        ):
            yield event
    
    def _determine_task_type(self, query: str, mode: str) -> TaskType:
        """
        Determine task type for model routing.
        
        Args:
            query: User query
            mode: Processing mode (auto, quick, deep)
        
        Returns:
            TaskType for routing decision
        """
        query_lower = query.lower()
        
        # Execution keywords
        execution_keywords = [
            "generate", "create", "build", "code", "script", "program",
            "write code", "implement", "develop", "compile", "debug",
            "excel", "csv", "file", "report", "table", "chart",
            "calculate", "compute", "process data", "analyze data",
            "execute", "run", "tool", "api call"
        ]
        
        # Reasoning keywords
        reasoning_keywords = [
            "what is", "explain", "why", "how does", "tell me about",
            "describe", "what are", "who is", "when did", "where",
            "understand", "learn", "know", "information about"
        ]
        
        # Check for execution needs
        needs_execution = any(kw in query_lower for kw in execution_keywords)
        
        # Check for pure reasoning
        is_reasoning = any(kw in query_lower for kw in reasoning_keywords)
        
        if needs_execution and not is_reasoning:
            return TaskType.EXECUTION
        elif is_reasoning and not needs_execution:
            return TaskType.REASONING
        else:
            # Complex query or unclear - use hybrid
            return TaskType.HYBRID
    
    def get_status(self) -> Dict[str, Any]:
        """Get orchestrator status including model availability."""
        return {
            "hybrid_enabled": self.use_hybrid,
            "models_available": {
                "grok": settings.is_grok_configured(),
                "kimi": settings.is_kimi_configured()
            },
            "default_provider": settings.DEFAULT_LLM_PROVIDER,
            "multi_model_ready": settings.is_multi_model_ready()
        }


# Global hybrid orchestrator instance
hybrid_orchestrator = HybridOrchestrator()
