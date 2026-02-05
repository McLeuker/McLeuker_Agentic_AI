"""
Hybrid Brain for McLeuker AI V7
Combines Grok (reasoning) and Kimi K2.5 (execution) for optimal performance.

Architecture:
- Grok: Intent understanding, planning, response synthesis
- Kimi: Tool execution, code generation, agentic workflows
"""

import asyncio
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass
from enum import Enum

from src.config.settings import settings
from src.core.kimi_client import kimi_client, KimiResponse

# Import existing Grok brain
try:
    from src.core.brain import brain as grok_brain, BrainResponse
except ImportError:
    grok_brain = None
    BrainResponse = None


class TaskType(Enum):
    """Types of tasks for model routing."""
    REASONING = "reasoning"  # Use Grok
    EXECUTION = "execution"  # Use Kimi
    HYBRID = "hybrid"        # Use both


@dataclass
class HybridResponse:
    """Response from hybrid brain."""
    success: bool
    content: str
    reasoning: List[str]
    sources: List[Dict] = None
    tool_calls: List[Dict] = None
    tokens_used: int = 0
    cost: float = 0.0
    models_used: List[str] = None
    error: Optional[str] = None


class HybridBrain:
    """
    Hybrid brain using dual-model architecture:
    - Grok for reasoning, planning, and synthesis
    - Kimi K2.5 for execution, coding, and tool calls
    
    This provides best-of-breed capabilities while optimizing costs.
    """
    
    def __init__(self):
        self.grok = grok_brain
        self.kimi = kimi_client
        
        # Verify models are configured
        if not settings.is_grok_configured():
            raise ValueError("Grok not configured - XAI_API_KEY required")
        
        if not settings.is_kimi_configured():
            print("⚠️  Kimi not configured - execution will use Grok fallback")
    
    async def think(
        self,
        query: str,
        context: Optional[str] = None,
        search_results: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict]] = None,
        task_type: TaskType = TaskType.HYBRID
    ) -> HybridResponse:
        """
        Process a query using the hybrid brain.
        
        Args:
            query: User query
            context: Additional context
            search_results: Search results to incorporate
            conversation_history: Previous conversation
            task_type: Type of task (reasoning, execution, or hybrid)
        
        Returns:
            HybridResponse with results
        """
        try:
            if task_type == TaskType.REASONING:
                # Pure reasoning - use Grok only
                return await self._reasoning_only(query, context, search_results, conversation_history)
            
            elif task_type == TaskType.EXECUTION:
                # Pure execution - use Kimi only
                return await self._execution_only(query, context, search_results)
            
            else:
                # Hybrid - use both models
                return await self._hybrid_workflow(query, context, search_results, conversation_history)
        
        except Exception as e:
            return HybridResponse(
                success=False,
                content="",
                reasoning=[f"Error in hybrid brain: {str(e)}"],
                error=str(e)
            )
    
    async def _reasoning_only(
        self,
        query: str,
        context: Optional[str],
        search_results: Optional[List[Dict]],
        conversation_history: Optional[List[Dict]]
    ) -> HybridResponse:
        """Use Grok for pure reasoning tasks."""
        if not self.grok:
            return HybridResponse(
                success=False,
                content="",
                reasoning=["Grok brain not available"],
                error="Grok not configured"
            )
        
        # Use existing Grok brain
        response = await self.grok.think(
            query=query,
            context=context,
            search_results=search_results,
            conversation_history=conversation_history
        )
        
        return HybridResponse(
            success=response.success,
            content=response.content,
            reasoning=response.reasoning,
            sources=search_results if search_results else [],
            models_used=["grok"],
            error=response.error
        )
    
    async def _execution_only(
        self,
        query: str,
        context: Optional[str],
        search_results: Optional[List[Dict]]
    ) -> HybridResponse:
        """Use Kimi for pure execution tasks."""
        if not self.kimi:
            # Fallback to Grok
            return await self._reasoning_only(query, context, search_results, None)
        
        # Build context with search results
        full_context = context or ""
        if search_results:
            full_context += "\n\nSearch Results:\n"
            for i, result in enumerate(search_results[:5], 1):
                full_context += f"{i}. {result.get('title', 'Unknown')}\n"
                full_context += f"   {result.get('snippet', '')}\n\n"
        
        # Execute with Kimi
        response = await self.kimi.execute(
            query=query,
            context=full_context if full_context else None
        )
        
        return HybridResponse(
            success=response.success,
            content=response.content,
            reasoning=response.reasoning,
            tool_calls=response.tool_calls,
            tokens_used=response.tokens_used,
            cost=response.cost,
            models_used=["kimi"],
            error=response.error
        )
    
    async def _hybrid_workflow(
        self,
        query: str,
        context: Optional[str],
        search_results: Optional[List[Dict]],
        conversation_history: Optional[List[Dict]]
    ) -> HybridResponse:
        """
        Hybrid workflow: Grok for reasoning, Kimi for execution.
        
        Flow:
        1. Grok: Understand query and plan approach
        2. Kimi: Execute any required actions/code
        3. Grok: Synthesize final response
        """
        total_cost = 0.0
        reasoning_steps = []
        models_used = []
        
        # Step 1: Grok plans the approach
        if self.grok:
            planning_prompt = f"""Analyze this query and determine what needs to be done:

Query: {query}

Provide:
1. What type of task is this?
2. What actions/executions are needed?
3. What information should be included in the response?

Be concise and actionable."""
            
            plan_response = await self.grok.think(
                query=planning_prompt,
                context=context,
                search_results=search_results,
                conversation_history=conversation_history
            )
            
            reasoning_steps.append(f"Planning (Grok): {plan_response.content[:200]}")
            models_used.append("grok")
        
        # Step 2: Check if execution is needed
        needs_execution = self._needs_execution(query)
        
        execution_result = None
        if needs_execution and self.kimi:
            # Kimi executes the task
            execution_result = await self.kimi.execute(
                query=query,
                context=context
            )
            
            total_cost += execution_result.cost
            reasoning_steps.extend(execution_result.reasoning)
            models_used.append("kimi")
        
        # Step 3: Grok synthesizes final response
        if self.grok:
            synthesis_context = context or ""
            if execution_result:
                synthesis_context += f"\n\nExecution Result:\n{execution_result.content}"
            
            final_response = await self.grok.think(
                query=query,
                context=synthesis_context,
                search_results=search_results,
                conversation_history=conversation_history
            )
            
            reasoning_steps.append(f"Synthesis (Grok): Final response generated")
            
            return HybridResponse(
                success=final_response.success,
                content=final_response.content,
                reasoning=reasoning_steps,
                sources=search_results if search_results else [],
                tool_calls=execution_result.tool_calls if execution_result else None,
                tokens_used=execution_result.tokens_used if execution_result else 0,
                cost=total_cost,
                models_used=list(set(models_used)),
                error=final_response.error
            )
        
        # Fallback: return execution result if no Grok
        if execution_result:
            return HybridResponse(
                success=execution_result.success,
                content=execution_result.content,
                reasoning=reasoning_steps,
                tool_calls=execution_result.tool_calls,
                tokens_used=execution_result.tokens_used,
                cost=total_cost,
                models_used=models_used,
                error=execution_result.error
            )
        
        # No execution, no Grok - error
        return HybridResponse(
            success=False,
            content="",
            reasoning=["No models available for processing"],
            error="No models configured"
        )
    
    def _needs_execution(self, query: str) -> bool:
        """Determine if query needs execution (vs pure reasoning)."""
        execution_keywords = [
            "generate", "create", "build", "code", "script", "analyze data",
            "calculate", "process", "execute", "run", "compile", "debug",
            "excel", "csv", "file", "report", "table", "chart"
        ]
        
        query_lower = query.lower()
        return any(keyword in query_lower for keyword in execution_keywords)
    
    async def think_stream(
        self,
        query: str,
        search_results: Optional[List[Dict]] = None,
        conversation_history: Optional[List[Dict]] = None
    ) -> AsyncGenerator[str, None]:
        """
        Stream response from hybrid brain.
        Currently uses Grok for streaming (Kimi streaming in future).
        """
        if self.grok:
            async for chunk in self.grok.think_stream(
                query=query,
                search_results=search_results,
                conversation_history=conversation_history
            ):
                yield chunk
        else:
            yield "Error: No streaming model available"


# Global hybrid brain instance
hybrid_brain = HybridBrain() if settings.is_multi_model_ready() or settings.is_grok_configured() else None
