"""
Agent Factory - Creates Agent Instances Dynamically
===================================================

The Agent Factory creates agent instances from definitions.
Supports:
- Dynamic agent instantiation
- Configuration injection
- Tool binding
- LLM client setup
- Memory attachment
"""

import logging
from typing import Any, Dict, List, Optional, Type

from agent_swarm.agents.definitions import AgentDefinition, get_agent_definition, AGENT_REGISTRY
from agent_swarm.core.base_agent import BaseSwarmAgent, AgentResult

logger = logging.getLogger(__name__)


class AgentFactory:
    """
    Factory for creating agent instances from definitions.
    
    Usage:
        factory = AgentFactory(llm_client, tool_registry)
        agent = factory.create_agent("blog_writer")
        result = await agent.execute("Write a blog post", {...})
    """

    def __init__(
        self,
        llm_client: Any,
        tool_registry: Any,
        memory_manager: Optional[Any] = None,
        coordinator: Optional[Any] = None,
        default_config: Optional[Dict[str, Any]] = None,
    ):
        self.llm_client = llm_client
        self.tool_registry = tool_registry
        self.memory_manager = memory_manager
        self.coordinator = coordinator
        self.default_config = default_config or {}
        
        # Cache for agent classes
        self._agent_classes: Dict[str, Type[BaseSwarmAgent]] = {}
        
        logger.info("AgentFactory initialized")

    def create_agent(
        self,
        agent_name: str,
        custom_config: Optional[Dict[str, Any]] = None,
    ) -> Optional[BaseSwarmAgent]:
        """
        Create an agent instance by name.
        
        Args:
            agent_name: Name of the agent to create
            custom_config: Optional custom configuration
        
        Returns:
            Agent instance or None if creation failed
        """
        definition = get_agent_definition(agent_name)
        if not definition:
            logger.error(f"Agent definition not found: {agent_name}")
            return None
        
        try:
            # Get or create agent class
            agent_class = self._get_agent_class(definition)
            
            # Merge configurations
            config = {**self.default_config, **(custom_config or {})}
            
            # Create agent instance
            agent = agent_class(
                llm_client=self.llm_client,
                tool_registry=self.tool_registry,
                memory_manager=self.memory_manager,
                coordinator=self.coordinator,
            )
            
            # Apply definition settings
            agent.name = definition.name
            agent.description = definition.description
            agent.supported_task_types = definition.capabilities
            agent.required_tools = definition.required_tools
            agent.max_execution_time = config.get("max_execution_time", 300)
            
            logger.info(f"Created agent instance: {agent_name}")
            return agent
            
        except Exception as e:
            logger.error(f"Failed to create agent {agent_name}: {e}")
            return None

    def create_agents_batch(
        self,
        agent_names: List[str],
    ) -> Dict[str, Optional[BaseSwarmAgent]]:
        """Create multiple agents at once."""
        results = {}
        for name in agent_names:
            results[name] = self.create_agent(name)
        return results

    def _get_agent_class(
        self,
        definition: AgentDefinition,
    ) -> Type[BaseSwarmAgent]:
        """
        Get or create an agent class for the definition.
        
        Dynamically creates a class that inherits from BaseSwarmAgent
        and implements the execute method with the agent's system prompt.
        """
        cache_key = definition.name
        
        if cache_key in self._agent_classes:
            return self._agent_classes[cache_key]
        
        # Capture definition in closure
        _def = definition
        
        class DynamicAgent(BaseSwarmAgent):
            """Dynamically generated agent class."""
            
            def __init__(self, **kwargs):
                super().__init__(**kwargs)
                self._system_prompt = _def.system_prompt
                self._temperature = _def.temperature
                self._max_tokens = _def.max_tokens
                self._llm_model = _def.llm_model
            
            async def execute(
                self,
                task_description: str,
                input_data: Dict[str, Any],
                context: Optional[Dict[str, Any]] = None,
            ) -> AgentResult:
                """Execute the agent task using LLM."""
                if not self.llm_client:
                    return AgentResult(
                        success=False,
                        error="LLM client not available",
                    )
                
                try:
                    import functools, asyncio
                    
                    # Build messages
                    messages = [
                        {"role": "system", "content": self._system_prompt},
                        {"role": "user", "content": f"""Task: {task_description}

Input Data: {str(input_data)[:2000]}

Context: {str(context or {})[:1000]}

Please complete this task thoroughly and provide a comprehensive result."""},
                    ]
                    
                    # Call LLM (use sync client wrapped in executor for compatibility)
                    loop = asyncio.get_event_loop()
                    
                    # Use temperature=1 for kimi models (required)
                    temp = 1 if "kimi" in self._llm_model else self._temperature
                    
                    response = await loop.run_in_executor(
                        None,
                        functools.partial(
                            self.llm_client.chat.completions.create,
                            model=self._llm_model,
                            messages=messages,
                            temperature=temp,
                            max_tokens=self._max_tokens,
                        )
                    )
                    
                    result = response.choices[0].message.content
                    
                    return AgentResult(
                        success=True,
                        data=result,
                        metadata={
                            "model": self._llm_model,
                            "temperature": temp,
                            "agent_name": self.name,
                        },
                    )
                    
                except Exception as e:
                    logger.error(f"Agent execution failed: {e}")
                    return AgentResult(
                        success=False,
                        error=str(e),
                    )
        
        # Set class name
        DynamicAgent.__name__ = f"{_def.name.title().replace('_', '')}Agent"
        
        # Cache and return
        self._agent_classes[cache_key] = DynamicAgent
        return DynamicAgent

    def get_available_agents(self) -> List[str]:
        """Get list of available agent names."""
        return list(AGENT_REGISTRY.keys())

    def get_agent_info(self, agent_name: str) -> Optional[Dict[str, Any]]:
        """Get information about an agent."""
        definition = get_agent_definition(agent_name)
        if not definition:
            return None
        
        return {
            "name": definition.name,
            "description": definition.description,
            "category": definition.category,
            "subcategory": definition.subcategory,
            "capabilities": definition.capabilities,
            "required_tools": definition.required_tools,
            "temperature": definition.temperature,
            "tags": definition.tags,
            "examples": definition.examples,
        }


class AgentBuilder:
    """
    Builder pattern for creating custom agents.
    
    Usage:
        agent = (AgentBuilder()
            .with_name("custom_agent")
            .with_description("Does custom things")
            .with_system_prompt("You are a custom agent...")
            .with_capabilities(["custom_task"])
            .with_tools(["custom_tool"])
            .build(llm_client, tool_registry))
    """

    def __init__(self):
        self._name = ""
        self._description = ""
        self._system_prompt = ""
        self._capabilities: List[str] = []
        self._required_tools: List[str] = []
        self._temperature = 0.7
        self._max_tokens = 4000
        self._category = "custom"

    def with_name(self, name: str) -> "AgentBuilder":
        self._name = name
        return self

    def with_description(self, description: str) -> "AgentBuilder":
        self._description = description
        return self

    def with_system_prompt(self, prompt: str) -> "AgentBuilder":
        self._system_prompt = prompt
        return self

    def with_capabilities(self, capabilities: List[str]) -> "AgentBuilder":
        self._capabilities = capabilities
        return self

    def with_tools(self, tools: List[str]) -> "AgentBuilder":
        self._required_tools = tools
        return self

    def with_temperature(self, temp: float) -> "AgentBuilder":
        self._temperature = temp
        return self

    def with_category(self, category: str) -> "AgentBuilder":
        self._category = category
        return self

    def build(
        self,
        llm_client: Any,
        tool_registry: Any,
    ) -> BaseSwarmAgent:
        """Build the custom agent."""
        # Register the custom definition temporarily
        definition = AgentDefinition(
            name=self._name,
            description=self._description,
            category=self._category,
            subcategory="custom",
            capabilities=self._capabilities,
            required_tools=self._required_tools,
            system_prompt=self._system_prompt,
            temperature=self._temperature,
            max_tokens=self._max_tokens,
        )
        
        # Add to registry so factory can find it
        AGENT_REGISTRY[self._name] = definition

        factory = AgentFactory(llm_client, tool_registry)
        agent = factory.create_agent(self._name)
        
        if not agent:
            raise RuntimeError(f"Failed to build agent: {self._name}")
        
        return agent
