"""
McLeuker Agentic AI Platform - Unified Agent Orchestrator

The brain of the system that coordinates all layers and manages
the complete task execution pipeline.
"""

import asyncio
from typing import Optional, Dict, Any, List, Callable
from datetime import datetime
from enum import Enum

from src.models.schemas import (
    Task,
    TaskRequest,
    TaskResponse,
    TaskStatus,
    TaskInterpretation,
    ReasoningBlueprint,
    ResearchOutput,
    StructuredOutput,
    ExecutionResult,
    GeneratedFile,
    Message,
    Conversation
)
from src.layers.task_interpretation import TaskInterpretationLayer
from src.layers.llm_reasoning import LLMReasoningLayer
from src.layers.web_research import WebResearchLayer
from src.layers.logic_structuring import LogicStructuringLayer
from src.layers.execution import ExecutionLayer
from src.tools.ai_search import AISearchPlatform
from src.utils.llm_provider import LLMProvider, LLMFactory
from src.config.settings import get_settings


class AgentState(str, Enum):
    """Current state of the agent."""
    IDLE = "idle"
    INTERPRETING = "interpreting"
    REASONING = "reasoning"
    RESEARCHING = "researching"
    STRUCTURING = "structuring"
    EXECUTING = "executing"
    COMPLETED = "completed"
    ERROR = "error"


class UnifiedAgentOrchestrator:
    """
    Unified Agent Orchestrator
    
    Coordinates all layers of the agentic AI system:
    1. Task Interpretation
    2. LLM Reasoning
    3. Web Research
    4. Logic & Structuring
    5. Execution
    
    Implements the observe → think → act → verify loop.
    """
    
    def __init__(
        self,
        llm_provider: Optional[LLMProvider] = None,
        output_dir: Optional[str] = None
    ):
        """Initialize the Unified Agent Orchestrator."""
        self.llm = llm_provider or LLMFactory.get_default()
        self.settings = get_settings()
        
        # Initialize all layers
        self.interpretation_layer = TaskInterpretationLayer(self.llm)
        self.reasoning_layer = LLMReasoningLayer(self.llm)
        self.research_layer = WebResearchLayer(llm_provider=self.llm)
        self.structuring_layer = LogicStructuringLayer(self.llm)
        self.execution_layer = ExecutionLayer(output_dir)
        self.search_platform = AISearchPlatform(self.llm)
        
        # State management
        self.current_state = AgentState.IDLE
        self.current_task: Optional[Task] = None
        
        # Progress callbacks
        self._progress_callbacks: List[Callable] = []
    
    def add_progress_callback(self, callback: Callable):
        """Add a callback for progress updates."""
        self._progress_callbacks.append(callback)
    
    async def _notify_progress(self, status: str, details: Optional[Dict] = None):
        """Notify all callbacks of progress."""
        for callback in self._progress_callbacks:
            try:
                if asyncio.iscoroutinefunction(callback):
                    await callback(status, details)
                else:
                    callback(status, details)
            except Exception as e:
                print(f"Progress callback error: {e}")
    
    async def process_task(
        self,
        request: TaskRequest,
        stream_progress: bool = True
    ) -> Task:
        """
        Process a complete task from prompt to deliverables.
        
        Args:
            request: The task request containing the user prompt
            stream_progress: Whether to stream progress updates
            
        Returns:
            Task: The completed task with all outputs
        """
        # Create task object
        task = Task(
            user_prompt=request.prompt,
            status=TaskStatus.PENDING,
            user_id=request.user_id
        )
        self.current_task = task
        
        try:
            # Phase 1: Task Interpretation
            task.status = TaskStatus.INTERPRETING
            self.current_state = AgentState.INTERPRETING
            await self._notify_progress("Understanding your request...", {"phase": 1})
            
            interpretation = await self.interpretation_layer.interpret(request.prompt)
            task.interpretation = interpretation
            
            # Phase 2: Reasoning
            task.status = TaskStatus.REASONING
            self.current_state = AgentState.REASONING
            await self._notify_progress("Planning execution strategy...", {"phase": 2})
            
            reasoning = await self.reasoning_layer.reason(
                request.prompt,
                interpretation
            )
            task.reasoning = reasoning
            
            # Phase 3: Research (if needed)
            if interpretation.requires_real_time_research:
                task.status = TaskStatus.RESEARCHING
                self.current_state = AgentState.RESEARCHING
                await self._notify_progress("Researching live sources...", {"phase": 3})
                
                research = await self.research_layer.research(reasoning)
                task.research = research
            else:
                # Create minimal research output
                task.research = ResearchOutput(
                    search_results=[],
                    synthesized_findings="No real-time research required for this task."
                )
            
            # Phase 4: Structuring
            task.status = TaskStatus.STRUCTURING
            self.current_state = AgentState.STRUCTURING
            await self._notify_progress("Structuring information...", {"phase": 4})
            
            structured = await self.structuring_layer.structure(
                interpretation,
                reasoning,
                task.research
            )
            task.structured_output = structured
            
            # Phase 5: Execution
            task.status = TaskStatus.EXECUTING
            self.current_state = AgentState.EXECUTING
            await self._notify_progress("Generating files...", {"phase": 5})
            
            execution_result = await self.execution_layer.execute(
                interpretation,
                structured
            )
            task.execution_result = execution_result
            
            # Complete
            task.status = TaskStatus.COMPLETED
            self.current_state = AgentState.COMPLETED
            task.updated_at = datetime.utcnow()
            
            await self._notify_progress("Task completed!", {
                "phase": 6,
                "files": len(execution_result.files)
            })
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error_message = str(e)
            self.current_state = AgentState.ERROR
            await self._notify_progress(f"Error: {str(e)}", {"error": True})
        
        self.current_task = None
        return task
    
    async def quick_search(self, query: str) -> Dict[str, Any]:
        """
        Perform a quick AI-powered search.
        
        Args:
            query: The search query
            
        Returns:
            Search results with summary
        """
        return await self.search_platform.search(
            query,
            summarize=True,
            scrape_top=2
        )
    
    async def quick_answer(self, question: str) -> Dict[str, Any]:
        """
        Get a quick answer to a question.
        
        Args:
            question: The question to answer
            
        Returns:
            Answer with sources
        """
        return await self.search_platform.quick_answer(question)
    
    async def research_topic(
        self,
        topic: str,
        depth: str = "medium"
    ) -> Dict[str, Any]:
        """
        Perform in-depth research on a topic.
        
        Args:
            topic: The topic to research
            depth: Research depth (light, medium, deep)
            
        Returns:
            Comprehensive research results
        """
        return await self.search_platform.research_topic(topic, depth)
    
    async def chat(
        self,
        message: str,
        conversation: Optional[Conversation] = None
    ) -> Dict[str, Any]:
        """
        Have a conversation with the agent.
        
        Args:
            message: The user's message
            conversation: Optional existing conversation
            
        Returns:
            Agent response with any actions taken
        """
        # Analyze the message to determine intent
        analysis = await self._analyze_message(message)
        
        response = {
            "message": "",
            "action_taken": None,
            "task_id": None,
            "files": None
        }
        
        if analysis.get("is_task_request"):
            # This is a task request, process it
            task_request = TaskRequest(prompt=message)
            task = await self.process_task(task_request)
            
            response["message"] = self._format_task_response(task)
            response["action_taken"] = "task_execution"
            response["task_id"] = task.id
            if task.execution_result:
                response["files"] = [f.dict() for f in task.execution_result.files]
        
        elif analysis.get("is_search_query"):
            # This is a search query
            search_result = await self.quick_search(message)
            response["message"] = search_result.get("summary", "")
            response["action_taken"] = "search"
            response["sources"] = search_result.get("results", [])[:5]
        
        elif analysis.get("is_question"):
            # This is a simple question
            answer = await self.quick_answer(message)
            response["message"] = answer.get("answer", "")
            response["action_taken"] = "answer"
            response["sources"] = answer.get("sources", [])
        
        else:
            # General conversation
            response["message"] = await self._generate_response(message, conversation)
            response["action_taken"] = "conversation"
        
        return response
    
    async def _analyze_message(self, message: str) -> Dict[str, Any]:
        """Analyze a message to determine its type and intent."""
        messages = [
            {
                "role": "system",
                "content": """Analyze the user message and determine:
1. is_task_request: Does the user want to create a deliverable (report, spreadsheet, presentation, etc.)?
2. is_search_query: Does the user want to search for information?
3. is_question: Is this a simple question that can be answered directly?
4. is_conversation: Is this general conversation?

Respond with a JSON object with boolean values for each category."""
            },
            {
                "role": "user",
                "content": message
            }
        ]
        
        response = await self.llm.complete_with_structured_output(
            messages=messages,
            response_format={"type": "json_object"},
            temperature=0.1
        )
        
        return response.get("content", {})
    
    async def _generate_response(
        self,
        message: str,
        conversation: Optional[Conversation] = None
    ) -> str:
        """Generate a conversational response."""
        messages = [
            {
                "role": "system",
                "content": """You are McLeuker AI, an intelligent assistant specialized in fashion, business, and research.
You can help users with:
- Creating reports, spreadsheets, and presentations
- Researching topics and answering questions
- Providing insights on fashion, sustainability, and business

Be helpful, professional, and concise."""
            }
        ]
        
        # Add conversation history
        if conversation:
            for msg in conversation.messages[-10:]:
                messages.append({
                    "role": msg.role,
                    "content": msg.content
                })
        
        messages.append({
            "role": "user",
            "content": message
        })
        
        response = await self.llm.complete(
            messages=messages,
            temperature=0.7,
            max_tokens=500
        )
        
        return response.get("content", "")
    
    def _format_task_response(self, task: Task) -> str:
        """Format a task result into a user-friendly message."""
        if task.status == TaskStatus.FAILED:
            return f"I encountered an error while processing your request: {task.error_message}"
        
        if not task.execution_result or not task.execution_result.files:
            return "I've processed your request but couldn't generate any files."
        
        files = task.execution_result.files
        file_list = "\n".join([f"- {f.filename}" for f in files])
        
        return f"""I've completed your request! Here are the generated files:

{file_list}

{task.execution_result.message}"""
    
    def get_state(self) -> Dict[str, Any]:
        """Get the current state of the orchestrator."""
        return {
            "state": self.current_state.value,
            "has_active_task": self.current_task is not None,
            "task_id": self.current_task.id if self.current_task else None,
            "task_status": self.current_task.status.value if self.current_task else None
        }


# Create a global orchestrator instance
_orchestrator: Optional[UnifiedAgentOrchestrator] = None


def get_orchestrator() -> UnifiedAgentOrchestrator:
    """Get or create the global orchestrator instance."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = UnifiedAgentOrchestrator()
    return _orchestrator


async def process_prompt(prompt: str) -> Task:
    """
    Convenience function to process a prompt.
    
    Args:
        prompt: The user's prompt
        
    Returns:
        Completed task
    """
    orchestrator = get_orchestrator()
    request = TaskRequest(prompt=prompt)
    return await orchestrator.process_task(request)
