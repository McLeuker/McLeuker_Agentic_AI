"""
Agent Swarm - 100+ Agent Ecosystem for True Agentic AI
======================================================

A production-ready agent swarm system built on top of kimi-2.5 + grok-4-1-fast-reasoning.
"""

__version__ = "2.0.0"
__author__ = "McLeuker AI Team"

import logging
logger = logging.getLogger(__name__)

# Safe lazy imports to avoid circular import issues
def get_version():
    return __version__

def get_agent_count():
    from agent_swarm.agents.definitions import AGENT_REGISTRY
    return len(AGENT_REGISTRY)

def get_category_counts():
    from collections import Counter
    from agent_swarm.agents.definitions import AGENT_REGISTRY
    return dict(Counter(agent.category for agent in AGENT_REGISTRY.values()))

def initialize_swarm(llm_client, reasoning_client=None, tool_registry=None, memory_manager=None):
    """Initialize the agent swarm with all registered agents."""
    from agent_swarm.core.coordinator import AgentSwarmCoordinator, AgentMetadata, AgentCapability
    from agent_swarm.core.base_agent import BaseSwarmAgent
    from agent_swarm.agents.definitions import AGENT_REGISTRY
    
    # Also load part2 definitions
    try:
        from agent_swarm.agents import definitions_part2
    except Exception:
        pass
    
    coordinator = AgentSwarmCoordinator(
        llm_client=llm_client,
        reasoning_client=reasoning_client or llm_client,
        tool_registry=tool_registry,
        memory_manager=memory_manager,
    )
    
    for definition in AGENT_REGISTRY.values():
        capabilities = [
            AgentCapability(name=cap, description=f"Capability: {cap}")
            for cap in definition.capabilities
        ]
        
        metadata = AgentMetadata(
            name=definition.name,
            description=definition.description,
            category=definition.category,
            subcategory=definition.subcategory,
            capabilities=capabilities,
            required_tools=definition.required_tools,
            tags=definition.tags,
            temperature=definition.temperature,
        )
        
        coordinator.register_agent(BaseSwarmAgent, metadata)
    
    logger.info(f"Initialized swarm with {len(AGENT_REGISTRY)} agents")
    return coordinator
