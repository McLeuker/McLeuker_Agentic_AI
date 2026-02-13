"""
Integration Module — Main Integration Point
=============================================
Connects all enhancement components with the existing McLeuker architecture.
Provides a unified interface for domain routing, file analysis, workflow
orchestration, and end-to-end execution.
"""

import logging
from typing import Dict, List, Optional, Any, AsyncGenerator
from dataclasses import dataclass

from .domain_agents import (
    FashionAgent, BeautyAgent, SkincareAgent,
    SustainabilityAgent, TechAgent, CatwalkAgent,
    CultureAgent, TextileAgent, LifestyleAgent, DomainRouter
)
from .tool_stability import (
    WorkflowOrchestrator, Workflow, WorkflowStep,
    ExtractionPipeline, ExtractionStep,
    StabilityManager, RetryConfig, StatePersistence
)
from .file_analysis import (
    MultimodalAnalyzer, ImageAnalyzer,
    DocumentAnalyzer, CodeAnalyzer, DataExtractor
)

logger = logging.getLogger(__name__)


@dataclass
class EnhancementConfig:
    """Configuration for the enhancement system."""
    enable_domain_agents: bool = True
    enable_tool_stability: bool = True
    enable_file_analysis: bool = True
    enable_execution_engine: bool = True
    max_parallel_workflows: int = 5
    workflow_timeout: float = 300.0
    retry_max_attempts: int = 3
    state_persistence_path: Optional[str] = "/tmp/mcleuker_workflows"


class McLeukerEnhancement:
    """
    Main enhancement class for McLeuker Agentic AI.

    Provides:
    - Domain-specific agent routing (9 agents)
    - Tool call stability (retry, circuit breaker, state persistence)
    - File upload analysis (multimodal via Kimi 2.5)
    - Workflow orchestration (multi-step, parallel, dependency-aware)
    - End-to-end execution engine (web automation, credential management)
    """

    def __init__(
        self,
        llm_client,
        search_tools=None,
        browser_tools=None,
        file_tools=None,
        config: Optional[EnhancementConfig] = None
    ):
        self.llm_client = llm_client
        self.search_tools = search_tools
        self.browser_tools = browser_tools
        self.file_tools = file_tools
        self.config = config or EnhancementConfig()

        self._init_domain_agents()
        self._init_tool_stability()
        self._init_file_analysis()

        logger.info("McLeukerEnhancement initialized successfully")

    def _init_domain_agents(self):
        """Initialize all 9 domain-specific agents and the router."""
        if not self.config.enable_domain_agents:
            self.domain_router = None
            return

        agents = {
            "fashion": FashionAgent(self.llm_client, self.search_tools, self.browser_tools),
            "beauty": BeautyAgent(self.llm_client, self.search_tools),
            "skincare": SkincareAgent(self.llm_client, self.search_tools),
            "sustainability": SustainabilityAgent(self.llm_client, self.search_tools),
            "tech": TechAgent(self.llm_client, self.search_tools),
            "catwalk": CatwalkAgent(self.llm_client, self.search_tools),
            "culture": CultureAgent(self.llm_client, self.search_tools),
            "textile": TextileAgent(self.llm_client, self.search_tools),
            "lifestyle": LifestyleAgent(self.llm_client, self.search_tools),
        }

        self.domain_router = DomainRouter(
            fashion_agent=agents["fashion"],
            beauty_agent=agents["beauty"],
            skincare_agent=agents["skincare"],
            sustainability_agent=agents["sustainability"],
            tech_agent=agents["tech"],
            catwalk_agent=agents["catwalk"],
            culture_agent=agents["culture"],
            textile_agent=agents["textile"],
            lifestyle_agent=agents["lifestyle"],
        )

        logger.info("Domain agents initialized: %s", list(agents.keys()))

    def _init_tool_stability(self):
        """Initialize tool stability components."""
        if not self.config.enable_tool_stability:
            return

        self.stability_manager = StabilityManager()
        self.state_persistence = StatePersistence(
            storage_path=self.config.state_persistence_path
        )
        self.workflow_orchestrator = None
        logger.info("Tool stability components initialized")

    def _init_file_analysis(self):
        """Initialize file analysis components."""
        if not self.config.enable_file_analysis:
            return

        self.multimodal_analyzer = MultimodalAnalyzer(self.llm_client)
        self.image_analyzer = ImageAnalyzer(self.llm_client)
        self.document_analyzer = DocumentAnalyzer(self.llm_client)
        self.code_analyzer = CodeAnalyzer(self.llm_client)
        self.data_extractor = DataExtractor(self.llm_client)
        logger.info("File analysis components initialized")

    def setup_workflow_orchestrator(self, tool_registry):
        """Setup workflow orchestrator with the tool registry from main app."""
        self.workflow_orchestrator = WorkflowOrchestrator(
            tool_registry=tool_registry,
            state_persistence=self.state_persistence,
            max_parallel_steps=self.config.max_parallel_workflows
        )
        logger.info("Workflow orchestrator setup complete")

    async def process_query(
        self,
        query: str,
        preferred_domain: Optional[str] = None,
        context: Optional[Dict] = None,
        images: Optional[List[str]] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Process a user query with domain routing."""
        if not self.config.enable_domain_agents or not self.domain_router:
            yield {"type": "error", "error": "Domain agents not enabled"}
            return

        async for event in self.domain_router.route(
            query, preferred_domain, context, images
        ):
            yield event

    async def analyze_file(
        self,
        file_path: str,
        query: Optional[str] = None,
        extract_text: bool = True
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Analyze an uploaded file using multimodal capabilities."""
        if not self.config.enable_file_analysis:
            yield {"type": "error", "error": "File analysis not enabled"}
            return

        async for event in self.multimodal_analyzer.analyze_file(
            file_path, query, extract_text
        ):
            yield event

    async def execute_workflow(
        self,
        workflow: Workflow,
        context: Optional[Dict] = None
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """Execute a workflow with stability and recovery."""
        if not self.workflow_orchestrator:
            yield {"type": "error", "error": "Workflow orchestrator not setup"}
            return

        async for event in self.workflow_orchestrator.execute(workflow, context):
            yield event

    def create_workflow(
        self,
        name: str,
        description: str,
        steps: List[WorkflowStep],
        metadata: Optional[Dict] = None
    ) -> Workflow:
        """Create a new workflow definition."""
        if not self.workflow_orchestrator:
            raise ValueError("Workflow orchestrator not setup. Call setup_workflow_orchestrator first.")

        return self.workflow_orchestrator.create_workflow(
            name, description, steps, metadata
        )

    def get_domain_info(self) -> Dict[str, Any]:
        """Get information about available domain agents."""
        if not self.config.enable_domain_agents or not self.domain_router:
            return {"enabled": False}
        return self.domain_router.get_agent_info()

    def get_status(self) -> Dict[str, Any]:
        """Get full enhancement system status."""
        return {
            "domain_agents": self.config.enable_domain_agents,
            "tool_stability": self.config.enable_tool_stability,
            "file_analysis": self.config.enable_file_analysis,
            "execution_engine": self.config.enable_execution_engine,
            "available_domains": (
                self.domain_router.get_agent_info()["available_agents"]
                if self.config.enable_domain_agents and self.domain_router
                else []
            ),
            "workflow_orchestrator": self.workflow_orchestrator is not None,
        }


def create_enhancement(
    llm_client,
    search_tools=None,
    browser_tools=None,
    file_tools=None,
    config: Optional[EnhancementConfig] = None
) -> McLeukerEnhancement:
    """Factory function to create a configured enhancement instance."""
    return McLeukerEnhancement(
        llm_client=llm_client,
        search_tools=search_tools,
        browser_tools=browser_tools,
        file_tools=file_tools,
        config=config
    )
