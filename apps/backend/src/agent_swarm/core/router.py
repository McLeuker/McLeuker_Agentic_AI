"""
Agent Router - Intelligent Task Routing for Agent Swarm
=======================================================

Routes tasks to the most appropriate agent(s) using:
- LLM-based agent selection (grok-4-1-fast-reasoning for reasoning)
- Capability matching
- Keyword-based routing
- Historical performance
"""

import asyncio
import functools
import json
import logging
from collections import Counter
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

logger = logging.getLogger(__name__)


@dataclass
class RoutingDecision:
    """Result of a routing decision."""
    agent_name: str
    confidence: float
    reasoning: str
    alternatives: List[Tuple[str, float]]
    estimated_time: int  # seconds


class AgentRouter:
    """
    Intelligent router for agent task assignment.
    
    Uses multiple strategies:
    1. LLM-based semantic routing (grok-4-1-fast-reasoning)
    2. Capability-based matching
    3. Keyword-based routing
    4. Historical performance
    """

    def __init__(
        self,
        llm_client: Any,
        reasoning_client: Any = None,
        coordinator: Any = None,
        enable_llm_routing: bool = True,
        enable_fallback: bool = True,
    ):
        self.llm_client = llm_client
        self.reasoning_client = reasoning_client or llm_client
        self.coordinator = coordinator
        self.enable_llm_routing = enable_llm_routing
        self.enable_fallback = enable_fallback
        
        # Routing history for learning
        self._routing_history: List[Dict] = []
        
        logger.info("AgentRouter initialized")

    async def route_task(
        self,
        task_description: str,
        input_data: Optional[Dict[str, Any]] = None,
        preferred_agents: Optional[List[str]] = None,
        excluded_agents: Optional[List[str]] = None,
        required_capabilities: Optional[List[str]] = None,
    ) -> Optional[RoutingDecision]:
        """Route a task to the best agent."""
        # Import here to avoid circular imports
        from agent_swarm.agents.definitions import get_agent_definition, search_agents, get_agents_by_capability
        
        # Try LLM-based routing first
        if self.enable_llm_routing and self.reasoning_client:
            decision = await self._llm_route(
                task_description, input_data,
                preferred_agents, excluded_agents, required_capabilities,
            )
            if decision:
                return decision
        
        # Fallback to capability-based routing
        if required_capabilities:
            decision = self._capability_route(
                task_description, required_capabilities, excluded_agents,
            )
            if decision:
                return decision
        
        # Fallback to keyword-based routing
        decision = self._keyword_route(task_description, excluded_agents)
        if decision:
            return decision
        
        # Final fallback
        if self.enable_fallback:
            return self._fallback_route(excluded_agents)
        
        return None

    async def route_multi_agent(
        self,
        task_description: str,
        input_data: Optional[Dict[str, Any]] = None,
        max_agents: int = 3,
    ) -> List[RoutingDecision]:
        """Route a task to multiple agents for parallel execution."""
        decisions = []
        excluded = set()
        
        for _ in range(max_agents):
            decision = await self.route_task(
                task_description, input_data,
                excluded_agents=list(excluded),
            )
            if not decision:
                break
            decisions.append(decision)
            excluded.add(decision.agent_name)
        
        return decisions

    async def _llm_route(
        self,
        task_description: str,
        input_data: Optional[Dict[str, Any]],
        preferred_agents: Optional[List[str]],
        excluded_agents: Optional[List[str]],
        required_capabilities: Optional[List[str]],
    ) -> Optional[RoutingDecision]:
        """Use LLM (grok-4-1-fast-reasoning) to select the best agent."""
        from agent_swarm.agents.definitions import get_agent_definition, search_agents
        
        try:
            # Get candidate agents
            if preferred_agents:
                candidates = [
                    get_agent_definition(name)
                    for name in preferred_agents
                    if get_agent_definition(name)
                ]
            else:
                candidates = list(search_agents(task_description)[:10])
            
            if excluded_agents:
                candidates = [c for c in candidates if c.name not in excluded_agents]
            
            if not candidates:
                return None
            
            # Build agent descriptions
            agent_descriptions = []
            for agent in candidates:
                caps = ", ".join(agent.capabilities[:5])
                agent_descriptions.append(
                    f"{agent.name}: {agent.description}\n"
                    f"  Capabilities: {caps}\n"
                    f"  Category: {agent.category}"
                )
            
            prompt = f"""Select the best agent for this task. Reason carefully about which agent's capabilities best match the task requirements.

Task: {task_description}

Input Data: {str(input_data)[:500] if input_data else "None"}

Available Agents:
{chr(10).join(agent_descriptions)}

Respond in JSON format:
{{
    "selected_agent": "agent_name",
    "confidence": 0.95,
    "reasoning": "Why this agent is best",
    "estimated_seconds": 120
}}"""

            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                functools.partial(
                    self.reasoning_client.chat.completions.create,
                    model="grok-4-1-fast-reasoning",
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=500,
                )
            )
            
            content = response.choices[0].message.content
            # Extract JSON from response
            if "```json" in content:
                content = content.split("```json")[1].split("```")[0].strip()
            elif "```" in content:
                content = content.split("```")[1].split("```")[0].strip()
            
            result = json.loads(content)
            
            selected_name = result.get("selected_agent")
            if not selected_name or selected_name not in [a.name for a in candidates]:
                return None
            
            alternatives = [
                (a.name, 0.5) for a in candidates
                if a.name != selected_name
            ][:3]
            
            return RoutingDecision(
                agent_name=selected_name,
                confidence=result.get("confidence", 0.8),
                reasoning=result.get("reasoning", "LLM selection"),
                alternatives=alternatives,
                estimated_time=result.get("estimated_seconds", 60),
            )
            
        except Exception as e:
            logger.error(f"LLM routing failed: {e}")
            return None

    def _capability_route(
        self,
        task_description: str,
        required_capabilities: List[str],
        excluded_agents: Optional[List[str]],
    ) -> Optional[RoutingDecision]:
        """Route based on required capabilities."""
        from agent_swarm.agents.definitions import get_agent_definition, get_agents_by_capability
        
        candidates = []
        for capability in required_capabilities:
            agents = get_agents_by_capability(capability)
            for agent in agents:
                if excluded_agents and agent.name in excluded_agents:
                    continue
                candidates.append(agent)
        
        if not candidates:
            return None
        
        agent_scores = Counter(a.name for a in candidates)
        best_name, score = agent_scores.most_common(1)[0]
        
        best_agent = get_agent_definition(best_name)
        if not best_agent:
            return None
        
        return RoutingDecision(
            agent_name=best_name,
            confidence=min(0.7 + score * 0.1, 0.95),
            reasoning=f"Matches {score} required capabilities",
            alternatives=[(name, 0.5) for name, _ in agent_scores.most_common(4)[1:]],
            estimated_time=60,
        )

    def _keyword_route(
        self,
        task_description: str,
        excluded_agents: Optional[List[str]],
    ) -> Optional[RoutingDecision]:
        """Route based on keyword matching."""
        from agent_swarm.agents.definitions import search_agents
        
        candidates = search_agents(task_description)
        
        if excluded_agents:
            candidates = [c for c in candidates if c.name not in excluded_agents]
        
        if not candidates:
            return None
        
        best = candidates[0]
        
        return RoutingDecision(
            agent_name=best.name,
            confidence=0.6,
            reasoning="Keyword match",
            alternatives=[(c.name, 0.4) for c in candidates[1:3]],
            estimated_time=60,
        )

    def _fallback_route(
        self,
        excluded_agents: Optional[List[str]],
    ) -> Optional[RoutingDecision]:
        """Fallback to a general-purpose agent."""
        from agent_swarm.agents.definitions import AGENT_REGISTRY
        
        fallback_names = [
            "research_assistant",
            "general_assistant",
            "task_executor",
        ]
        
        for name in fallback_names:
            if name in AGENT_REGISTRY:
                if excluded_agents and name in excluded_agents:
                    continue
                return RoutingDecision(
                    agent_name=name,
                    confidence=0.5,
                    reasoning="Fallback selection",
                    alternatives=[],
                    estimated_time=120,
                )
        
        available = [
            name for name in AGENT_REGISTRY.keys()
            if not excluded_agents or name not in excluded_agents
        ]
        
        if available:
            return RoutingDecision(
                agent_name=available[0],
                confidence=0.4,
                reasoning="Last resort fallback",
                alternatives=[],
                estimated_time=120,
            )
        
        return None

    def record_routing_result(
        self,
        task_description: str,
        decision: RoutingDecision,
        success: bool,
        execution_time: int,
    ):
        """Record routing result for learning."""
        self._routing_history.append({
            "task": task_description,
            "agent": decision.agent_name,
            "confidence": decision.confidence,
            "success": success,
            "execution_time": execution_time,
        })
        if len(self._routing_history) > 1000:
            self._routing_history = self._routing_history[-1000:]

    def get_routing_stats(self) -> Dict[str, Any]:
        """Get routing statistics."""
        if not self._routing_history:
            return {"total_routings": 0}
        
        total = len(self._routing_history)
        successful = sum(1 for r in self._routing_history if r["success"])
        
        agent_stats = {}
        for record in self._routing_history:
            agent = record["agent"]
            if agent not in agent_stats:
                agent_stats[agent] = {"total": 0, "success": 0}
            agent_stats[agent]["total"] += 1
            if record["success"]:
                agent_stats[agent]["success"] += 1
        
        return {
            "total_routings": total,
            "successful_routings": successful,
            "success_rate": successful / total if total > 0 else 0,
            "agent_stats": agent_stats,
        }
