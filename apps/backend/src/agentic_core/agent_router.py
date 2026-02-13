"""
Agent Orchestration Router — Intelligent Agent Selection & Routing
===================================================================

Routes user requests to the most appropriate agent(s) based on:
- Task type classification
- Agent capabilities
- Current system load
- Historical performance

Enables seamless multi-agent coordination for complex tasks.
"""

import json
import logging
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Type, Callable, AsyncGenerator
import openai

logger = logging.getLogger(__name__)


class AgentCapability(Enum):
    """Capabilities that agents can have."""
    WEB_SEARCH = "web_search"
    WEB_BROWSING = "web_browsing"
    CODE_GENERATION = "code_generation"
    CODE_EXECUTION = "code_execution"
    FILE_GENERATION = "file_generation"
    FILE_ANALYSIS = "file_analysis"
    WEBSITE_BUILDING = "website_building"
    DOCUMENT_CREATION = "document_creation"
    PRESENTATION_CREATION = "presentation_creation"
    SPREADSHEET_CREATION = "spreadsheet_creation"
    DEEP_RESEARCH = "deep_research"
    COMPUTER_USE = "computer_use"
    VISION_ANALYSIS = "vision_analysis"
    DATA_ANALYSIS = "data_analysis"
    MULTI_AGENT_COORDINATION = "multi_agent_coordination"


@dataclass
class AgentInfo:
    """Information about a registered agent."""
    name: str
    description: str
    capabilities: List[AgentCapability]
    handler: Callable
    priority: int = 5  # 1-10, lower = higher priority
    avg_execution_time_seconds: float = 30.0
    success_rate: float = 0.95
    concurrent_limit: int = 5
    current_load: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def can_handle(self, required_capabilities: List[AgentCapability]) -> bool:
        """Check if agent has all required capabilities."""
        return all(cap in self.capabilities for cap in required_capabilities)
    
    def is_available(self) -> bool:
        """Check if agent has capacity for new tasks."""
        return self.current_load < self.concurrent_limit
    
    def score_for_task(self, task_type: str, complexity: str) -> float:
        """Calculate a suitability score for a task."""
        score = 0.0
        
        # Priority bonus
        score += (10 - self.priority) * 10
        
        # Success rate bonus
        score += self.success_rate * 100
        
        # Speed bonus (faster = higher score)
        score += max(0, 100 - self.avg_execution_time_seconds)
        
        # Load penalty (higher load = lower score)
        load_ratio = self.current_load / max(1, self.concurrent_limit)
        score -= load_ratio * 50
        
        return score


@dataclass
class RoutingDecision:
    """Result of a routing decision."""
    request_id: str
    selected_agents: List[str]
    routing_reason: str
    execution_mode: str  # "single", "sequential", "parallel", "swarm"
    estimated_duration_seconds: float
    fallback_agents: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)


class AgentRouter:
    """
    Intelligent agent routing and orchestration.
    
    Features:
    - Automatic agent selection based on task requirements
    - Load balancing across agents
    - Multi-agent coordination for complex tasks
    - Fallback agent selection
    - Performance tracking
    
    Usage:
        router = AgentRouter(llm_client)
        router.register_agent("website_builder", website_builder_agent_info)
        
        decision = await router.route_request("Build a website for my bakery")
        async for event in router.execute_with_routing(decision, request):
            print(event)
    """
    
    def __init__(self, llm_client: openai.AsyncOpenAI, model: str = "kimi-k2.5"):
        self.llm_client = llm_client
        self.model = model
        self._agents: Dict[str, AgentInfo] = {}
        self._routing_history: List[Dict] = []
    
    def register_agent(self, name: str, agent_info: AgentInfo):
        """Register an agent with the router."""
        self._agents[name] = agent_info
        logger.info(f"Registered agent: {name} with capabilities: {[c.value for c in agent_info.capabilities]}")
    
    def unregister_agent(self, name: str):
        """Unregister an agent."""
        if name in self._agents:
            del self._agents[name]
            logger.info(f"Unregistered agent: {name}")
    
    def get_agent(self, name: str) -> Optional[AgentInfo]:
        """Get agent info by name."""
        return self._agents.get(name)
    
    def list_agents(self) -> List[AgentInfo]:
        """List all registered agents."""
        return list(self._agents.values())
    
    def find_agents_by_capability(self, capability: AgentCapability) -> List[AgentInfo]:
        """Find all agents with a specific capability."""
        return [a for a in self._agents.values() if capability in a.capabilities]
    
    async def route_request(
        self,
        request: str,
        request_id: Optional[str] = None,
        context: Optional[Dict] = None,
        preferred_agents: Optional[List[str]] = None,
    ) -> RoutingDecision:
        """
        Route a request to the most appropriate agent(s).
        """
        import uuid
        request_id = request_id or str(uuid.uuid4())
        
        # Analyze request to determine required capabilities
        required_caps = await self._analyze_required_capabilities(request)
        
        # Find capable agents
        capable_agents = [
            (name, agent) for name, agent in self._agents.items()
            if agent.can_handle(required_caps) and agent.is_available()
        ]
        
        # Score and rank agents
        scored_agents = [
            (name, agent, agent.score_for_task("", ""))
            for name, agent in capable_agents
        ]
        scored_agents.sort(key=lambda x: x[2], reverse=True)
        
        # Apply preferred agents if specified
        if preferred_agents:
            scored_agents = [
                (n, a, s) for n, a, s in scored_agents
                if n in preferred_agents
            ]
        
        # Determine execution mode based on task complexity
        execution_mode = await self._determine_execution_mode(request, required_caps)
        
        # Select agents based on execution mode
        selected_agents = []
        fallback_agents = []
        
        if execution_mode == "single":
            if scored_agents:
                selected_agents = [scored_agents[0][0]]
                fallback_agents = [a[0] for a in scored_agents[1:3]]
        
        elif execution_mode == "sequential":
            # Select top 2-3 agents for sequential execution
            selected_agents = [a[0] for a in scored_agents[:3]]
            fallback_agents = [a[0] for a in scored_agents[3:5]]
        
        elif execution_mode == "parallel":
            # Select multiple agents for parallel execution
            selected_agents = [a[0] for a in scored_agents[:3]]
            fallback_agents = [a[0] for a in scored_agents[3:5]]
        
        elif execution_mode == "swarm":
            # Use all capable agents in swarm mode
            selected_agents = [a[0] for a in scored_agents[:5]]
            fallback_agents = [a[0] for a in scored_agents[5:7]]
        
        # Estimate duration
        estimated_duration = sum(
            self._agents[name].avg_execution_time_seconds
            for name in selected_agents
        )
        
        # Generate routing reason
        routing_reason = await self._generate_routing_reason(
            request, selected_agents, execution_mode, required_caps
        )
        
        decision = RoutingDecision(
            request_id=request_id,
            selected_agents=selected_agents,
            routing_reason=routing_reason,
            execution_mode=execution_mode,
            estimated_duration_seconds=estimated_duration,
            fallback_agents=fallback_agents,
            metadata={
                "required_capabilities": [c.value for c in required_caps],
                "all_capable_agents": [a[0] for a in scored_agents],
                "context": context or {},
            }
        )
        
        # Record routing decision
        self._routing_history.append({
            "request_id": request_id,
            "request": request[:100],
            "decision": decision,
            "timestamp": import_time(),
        })
        
        logger.info(f"Routed request {request_id} to agents: {selected_agents} (mode: {execution_mode})")
        return decision
    
    async def _analyze_required_capabilities(self, request: str) -> List[AgentCapability]:
        """Analyze request to determine required agent capabilities."""
        messages = [
            {
                "role": "system",
                "content": """Analyze the user request and determine what capabilities are needed.

Available capabilities:
- web_search: Searching the web for information
- web_browsing: Navigating and interacting with websites
- code_generation: Writing code
- code_execution: Running code
- file_generation: Creating files (documents, spreadsheets, etc.)
- file_analysis: Analyzing uploaded files
- website_building: Creating and deploying websites
- document_creation: Creating documents (DOCX, PDF)
- presentation_creation: Creating presentations (PPTX)
- spreadsheet_creation: Creating spreadsheets (XLSX)
- deep_research: Comprehensive multi-source research
- computer_use: GUI automation
- vision_analysis: Analyzing images
- data_analysis: Statistical analysis and visualization
- multi_agent_coordination: Coordinating multiple agents

Respond with JSON:
{
    "required_capabilities": ["capability1", "capability2"],
    "reasoning": "explanation"
}"""
            },
            {
                "role": "user",
                "content": f"Analyze this request: {request}"
            }
        ]
        
        try:
            response = await self.llm_client.chat.completions.create(
                model=self.model,
                messages=messages,
                temperature=0.3,
                max_tokens=1024,
                response_format={"type": "json_object"},
            )
            
            result = json.loads(response.choices[0].message.content)
            caps = result.get("required_capabilities", [])
            return [AgentCapability(c) for c in caps if c in [ac.value for ac in AgentCapability]]
            
        except Exception as e:
            logger.error(f"Error analyzing capabilities: {e}")
            # Fallback to basic capabilities
            return [AgentCapability.WEB_SEARCH, AgentCapability.CODE_GENERATION]
    
    async def _determine_execution_mode(
        self,
        request: str,
        required_caps: List[AgentCapability],
    ) -> str:
        """Determine the best execution mode for the request."""
        # Simple heuristics
        cap_values = [c.value for c in required_caps]
        
        # Complex tasks that need multiple capabilities
        if len(required_caps) > 2:
            return "swarm"
        
        # Research tasks benefit from parallel execution
        if AgentCapability.DEEP_RESEARCH in required_caps:
            return "parallel"
        
        # Website building typically needs sequential steps
        if AgentCapability.WEBSITE_BUILDING in required_caps:
            return "sequential"
        
        # Simple tasks
        if len(required_caps) <= 1:
            return "single"
        
        return "sequential"
    
    async def _generate_routing_reason(
        self,
        request: str,
        selected_agents: List[str],
        execution_mode: str,
        required_caps: List[AgentCapability],
    ) -> str:
        """Generate a human-readable explanation of the routing decision."""
        cap_names = [c.value.replace("_", " ").title() for c in required_caps]
        agent_names = ", ".join(selected_agents)
        
        mode_descriptions = {
            "single": f"This task will be handled by {agent_names} as it requires {', '.join(cap_names)}.",
            "sequential": f"This multi-step task requires {', '.join(cap_names)}. {agent_names} will work sequentially.",
            "parallel": f"This task benefits from parallel execution. {agent_names} will work simultaneously on different aspects.",
            "swarm": f"This complex task requires a coordinated swarm approach with {agent_names}.",
        }
        
        return mode_descriptions.get(execution_mode, f"Task routed to {agent_names}")
    
    async def execute_with_routing(
        self,
        decision: RoutingDecision,
        request: str,
        context: Optional[Dict] = None,
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        Execute a request using the routing decision.
        """
        yield {
            "type": "routing_decision",
            "data": {
                "request_id": decision.request_id,
                "agents": decision.selected_agents,
                "mode": decision.execution_mode,
                "reason": decision.routing_reason,
            }
        }
        
        if decision.execution_mode == "single":
            async for event in self._execute_single(decision, request, context):
                yield event
        
        elif decision.execution_mode == "sequential":
            async for event in self._execute_sequential(decision, request, context):
                yield event
        
        elif decision.execution_mode == "parallel":
            async for event in self._execute_parallel(decision, request, context):
                yield event
        
        elif decision.execution_mode == "swarm":
            async for event in self._execute_swarm(decision, request, context):
                yield event
    
    async def _execute_single(
        self,
        decision: RoutingDecision,
        request: str,
        context: Optional[Dict],
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute with a single agent."""
        agent_name = decision.selected_agents[0]
        agent = self._agents.get(agent_name)
        
        if not agent:
            yield {"type": "error", "data": {"error": f"Agent {agent_name} not found"}}
            return
        
        # Increment load
        agent.current_load += 1
        
        try:
            yield {"type": "agent_start", "data": {"agent": agent_name}}
            
            # Call agent handler
            async for event in agent.handler(request, context):
                yield event
            
            yield {"type": "agent_complete", "data": {"agent": agent_name}}
            
        except Exception as e:
            logger.error(f"Error executing with {agent_name}: {e}")
            yield {"type": "agent_error", "data": {"agent": agent_name, "error": str(e)}}
            
            # Try fallback
            for fallback in decision.fallback_agents:
                yield {"type": "fallback_attempt", "data": {"from": agent_name, "to": fallback}}
                fallback_agent = self._agents.get(fallback)
                if fallback_agent:
                    try:
                        async for event in fallback_agent.handler(request, context):
                            yield event
                        return
                    except Exception as e2:
                        yield {"type": "fallback_error", "data": {"agent": fallback, "error": str(e2)}}
        
        finally:
            agent.current_load -= 1
    
    async def _execute_sequential(
        self,
        decision: RoutingDecision,
        request: str,
        context: Optional[Dict],
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute with multiple agents sequentially."""
        for i, agent_name in enumerate(decision.selected_agents):
            agent = self._agents.get(agent_name)
            if not agent:
                continue
            
            agent.current_load += 1
            
            try:
                yield {"type": "agent_start", "data": {"agent": agent_name, "step": i + 1, "total": len(decision.selected_agents)}}
                
                async for event in agent.handler(request, context):
                    yield event
                
                yield {"type": "agent_complete", "data": {"agent": agent_name, "step": i + 1}}
                
            except Exception as e:
                yield {"type": "agent_error", "data": {"agent": agent_name, "error": str(e)}}
            
            finally:
                agent.current_load -= 1
    
    async def _execute_parallel(
        self,
        decision: RoutingDecision,
        request: str,
        context: Optional[Dict],
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute with multiple agents in parallel."""
        import asyncio
        
        async def run_agent(agent_name: str):
            agent = self._agents.get(agent_name)
            if not agent:
                return []
            
            agent.current_load += 1
            events = []
            
            try:
                async for event in agent.handler(request, context):
                    events.append({"agent": agent_name, **event})
            except Exception as e:
                events.append({"agent": agent_name, "type": "error", "data": {"error": str(e)}})
            finally:
                agent.current_load -= 1
            
            return events
        
        # Start all agents
        tasks = [run_agent(name) for name in decision.selected_agents]
        
        # Yield results as they complete
        for completed_task in asyncio.as_completed(tasks):
            events = await completed_task
            for event in events:
                yield event
    
    async def _execute_swarm(
        self,
        decision: RoutingDecision,
        request: str,
        context: Optional[Dict],
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute with a coordinated swarm of agents."""
        # For now, delegate to parallel execution with coordination
        # This can be enhanced with a dedicated swarm coordinator
        yield {"type": "swarm_start", "data": {"agents": decision.selected_agents}}
        
        async for event in self._execute_parallel(decision, request, context):
            yield event
        
        yield {"type": "swarm_complete", "data": {"agents": decision.selected_agents}}


def import_time():
    """Helper to get current time."""
    from datetime import datetime
    return datetime.now().isoformat()


# Singleton instance
_agent_router: Optional[AgentRouter] = None


def get_agent_router(llm_client: openai.AsyncOpenAI = None) -> AgentRouter:
    """Get or create the Agent Router singleton."""
    global _agent_router
    if _agent_router is None and llm_client:
        _agent_router = AgentRouter(llm_client)
    return _agent_router
