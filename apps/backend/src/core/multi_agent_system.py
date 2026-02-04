"""
McLeuker AI V8 - Multi-Agent Collaboration System
==================================================
Advanced multi-agent system where agents can delegate tasks to each other,
collaborate on complex problems, and synthesize results.
Inspired by Manus AI's agent architecture.
"""

import asyncio
import json
import uuid
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable, Tuple
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging

logger = logging.getLogger(__name__)


class AgentRole(Enum):
    """Specialized agent roles"""
    ORCHESTRATOR = "orchestrator"      # Coordinates other agents
    RESEARCHER = "researcher"          # Gathers information
    ANALYST = "analyst"                # Analyzes data
    WRITER = "writer"                  # Creates content
    CODER = "coder"                    # Writes and executes code
    CRITIC = "critic"                  # Reviews and improves
    SPECIALIST = "specialist"          # Domain expert
    EXECUTOR = "executor"              # Executes tool calls


class TaskStatus(Enum):
    """Task execution status"""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    DELEGATED = "delegated"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    """Task priority levels"""
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    CRITICAL = 4


@dataclass
class AgentTask:
    """A task for an agent to execute"""
    id: str
    description: str
    role: AgentRole
    priority: TaskPriority = TaskPriority.MEDIUM
    status: TaskStatus = TaskStatus.PENDING
    parent_task_id: Optional[str] = None
    delegated_to: Optional[str] = None
    delegated_from: Optional[str] = None
    input_data: Dict = field(default_factory=dict)
    output_data: Optional[Dict] = None
    error: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    metadata: Dict = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "description": self.description,
            "role": self.role.value,
            "priority": self.priority.value,
            "status": self.status.value,
            "parent_task_id": self.parent_task_id,
            "delegated_to": self.delegated_to,
            "delegated_from": self.delegated_from,
            "input_data": self.input_data,
            "output_data": self.output_data,
            "error": self.error,
            "created_at": self.created_at.isoformat(),
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "metadata": self.metadata
        }


@dataclass
class AgentMessage:
    """Message between agents"""
    id: str
    from_agent: str
    to_agent: str
    message_type: str  # request, response, delegation, notification
    content: Dict
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "from_agent": self.from_agent,
            "to_agent": self.to_agent,
            "message_type": self.message_type,
            "content": self.content,
            "timestamp": self.timestamp.isoformat()
        }


class BaseAgent(ABC):
    """Base class for all agents"""
    
    def __init__(self, agent_id: str, role: AgentRole, name: str):
        self.agent_id = agent_id
        self.role = role
        self.name = name
        self.capabilities: List[str] = []
        self.current_task: Optional[AgentTask] = None
        self.task_history: List[AgentTask] = []
        self.message_queue: asyncio.Queue = asyncio.Queue()
        self.collaborators: Dict[str, "BaseAgent"] = {}
        self.is_active = True
    
    @abstractmethod
    async def execute_task(self, task: AgentTask) -> Dict:
        """Execute a task and return results"""
        pass
    
    @abstractmethod
    async def can_handle(self, task: AgentTask) -> Tuple[bool, float]:
        """Check if agent can handle a task and return confidence score"""
        pass
    
    async def delegate_task(self, task: AgentTask, target_agent: "BaseAgent") -> AgentTask:
        """Delegate a task to another agent"""
        task.status = TaskStatus.DELEGATED
        task.delegated_to = target_agent.agent_id
        task.delegated_from = self.agent_id
        
        # Send delegation message
        message = AgentMessage(
            id=str(uuid.uuid4()),
            from_agent=self.agent_id,
            to_agent=target_agent.agent_id,
            message_type="delegation",
            content={"task": task.to_dict()}
        )
        
        await target_agent.receive_message(message)
        logger.info(f"Agent {self.name} delegated task {task.id} to {target_agent.name}")
        
        return task
    
    async def receive_message(self, message: AgentMessage):
        """Receive a message from another agent"""
        await self.message_queue.put(message)
    
    async def send_message(self, to_agent: "BaseAgent", message_type: str, content: Dict):
        """Send a message to another agent"""
        message = AgentMessage(
            id=str(uuid.uuid4()),
            from_agent=self.agent_id,
            to_agent=to_agent.agent_id,
            message_type=message_type,
            content=content
        )
        await to_agent.receive_message(message)
    
    def register_collaborator(self, agent: "BaseAgent"):
        """Register another agent as a collaborator"""
        self.collaborators[agent.agent_id] = agent
    
    def get_status(self) -> Dict:
        """Get current agent status"""
        return {
            "agent_id": self.agent_id,
            "name": self.name,
            "role": self.role.value,
            "is_active": self.is_active,
            "current_task": self.current_task.to_dict() if self.current_task else None,
            "tasks_completed": len([t for t in self.task_history if t.status == TaskStatus.COMPLETED]),
            "capabilities": self.capabilities
        }


class OrchestratorAgent(BaseAgent):
    """
    Master orchestrator that coordinates all other agents.
    Decomposes complex tasks and delegates to specialists.
    """
    
    def __init__(self):
        super().__init__(
            agent_id="orchestrator_001",
            role=AgentRole.ORCHESTRATOR,
            name="Master Orchestrator"
        )
        self.capabilities = [
            "task_decomposition",
            "agent_coordination",
            "result_synthesis",
            "workflow_management"
        ]
        self.task_queue: asyncio.Queue = asyncio.Queue()
        self.active_workflows: Dict[str, Dict] = {}
    
    async def execute_task(self, task: AgentTask) -> Dict:
        """Orchestrate task execution across multiple agents"""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        self.current_task = task
        
        try:
            # Decompose the task
            subtasks = await self._decompose_task(task)
            
            # Create workflow
            workflow_id = str(uuid.uuid4())
            self.active_workflows[workflow_id] = {
                "main_task": task,
                "subtasks": subtasks,
                "results": {},
                "status": "running"
            }
            
            # Assign subtasks to appropriate agents
            assignments = await self._assign_subtasks(subtasks)
            
            # Execute subtasks (some in parallel, some sequential)
            results = await self._execute_workflow(assignments)
            
            # Synthesize results
            final_result = await self._synthesize_results(task, results)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.output_data = final_result
            
            self.active_workflows[workflow_id]["status"] = "completed"
            self.active_workflows[workflow_id]["results"] = final_result
            
            return final_result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            logger.error(f"Orchestrator failed task {task.id}: {e}")
            return {"error": str(e)}
        finally:
            self.current_task = None
            self.task_history.append(task)
    
    async def can_handle(self, task: AgentTask) -> Tuple[bool, float]:
        """Orchestrator can handle any task by delegating"""
        return True, 1.0
    
    async def _decompose_task(self, task: AgentTask) -> List[AgentTask]:
        """Decompose a complex task into subtasks"""
        subtasks = []
        description = task.description.lower()
        
        # Research subtask
        if any(kw in description for kw in ["research", "find", "search", "discover", "learn"]):
            subtasks.append(AgentTask(
                id=f"{task.id}_research",
                description=f"Research: {task.description}",
                role=AgentRole.RESEARCHER,
                parent_task_id=task.id,
                input_data=task.input_data
            ))
        
        # Analysis subtask
        if any(kw in description for kw in ["analyze", "compare", "evaluate", "assess", "understand"]):
            subtasks.append(AgentTask(
                id=f"{task.id}_analysis",
                description=f"Analyze: {task.description}",
                role=AgentRole.ANALYST,
                parent_task_id=task.id,
                input_data=task.input_data
            ))
        
        # Writing subtask
        if any(kw in description for kw in ["write", "create", "generate", "compose", "draft"]):
            subtasks.append(AgentTask(
                id=f"{task.id}_writing",
                description=f"Write: {task.description}",
                role=AgentRole.WRITER,
                parent_task_id=task.id,
                input_data=task.input_data
            ))
        
        # Code subtask
        if any(kw in description for kw in ["code", "program", "script", "implement", "build"]):
            subtasks.append(AgentTask(
                id=f"{task.id}_coding",
                description=f"Code: {task.description}",
                role=AgentRole.CODER,
                parent_task_id=task.id,
                input_data=task.input_data
            ))
        
        # If no specific subtasks identified, create a general research + analysis + writing flow
        if not subtasks:
            subtasks = [
                AgentTask(
                    id=f"{task.id}_research",
                    description=f"Research information about: {task.description}",
                    role=AgentRole.RESEARCHER,
                    parent_task_id=task.id,
                    input_data=task.input_data
                ),
                AgentTask(
                    id=f"{task.id}_analysis",
                    description=f"Analyze findings about: {task.description}",
                    role=AgentRole.ANALYST,
                    parent_task_id=task.id,
                    input_data=task.input_data
                ),
                AgentTask(
                    id=f"{task.id}_synthesis",
                    description=f"Synthesize response for: {task.description}",
                    role=AgentRole.WRITER,
                    parent_task_id=task.id,
                    input_data=task.input_data
                )
            ]
        
        # Always add a critic review at the end
        subtasks.append(AgentTask(
            id=f"{task.id}_review",
            description=f"Review and improve response for: {task.description}",
            role=AgentRole.CRITIC,
            parent_task_id=task.id,
            input_data=task.input_data
        ))
        
        return subtasks
    
    async def _assign_subtasks(self, subtasks: List[AgentTask]) -> List[Tuple[AgentTask, BaseAgent]]:
        """Assign subtasks to appropriate agents"""
        assignments = []
        
        for subtask in subtasks:
            best_agent = None
            best_confidence = 0.0
            
            for agent in self.collaborators.values():
                can_handle, confidence = await agent.can_handle(subtask)
                if can_handle and confidence > best_confidence:
                    best_agent = agent
                    best_confidence = confidence
            
            if best_agent:
                assignments.append((subtask, best_agent))
            else:
                logger.warning(f"No agent found for subtask: {subtask.description}")
        
        return assignments
    
    async def _execute_workflow(self, assignments: List[Tuple[AgentTask, BaseAgent]]) -> Dict[str, Dict]:
        """Execute workflow with proper dependencies"""
        results = {}
        
        # Group by dependency (research first, then analysis, then writing, then review)
        role_order = [AgentRole.RESEARCHER, AgentRole.ANALYST, AgentRole.WRITER, AgentRole.CODER, AgentRole.CRITIC]
        
        for role in role_order:
            role_tasks = [(t, a) for t, a in assignments if t.role == role]
            
            if role_tasks:
                # Execute tasks of same role in parallel
                task_coroutines = []
                for subtask, agent in role_tasks:
                    # Pass previous results as context
                    subtask.input_data["previous_results"] = results
                    task_coroutines.append(agent.execute_task(subtask))
                
                task_results = await asyncio.gather(*task_coroutines, return_exceptions=True)
                
                for (subtask, _), result in zip(role_tasks, task_results):
                    if isinstance(result, Exception):
                        results[subtask.id] = {"error": str(result)}
                    else:
                        results[subtask.id] = result
        
        return results
    
    async def _synthesize_results(self, main_task: AgentTask, results: Dict[str, Dict]) -> Dict:
        """Synthesize all subtask results into final output"""
        synthesis = {
            "task_id": main_task.id,
            "description": main_task.description,
            "subtask_results": results,
            "synthesis": {
                "research_findings": [],
                "analysis_insights": [],
                "generated_content": [],
                "review_improvements": []
            }
        }
        
        for task_id, result in results.items():
            if "error" in result:
                continue
            
            if "_research" in task_id:
                synthesis["synthesis"]["research_findings"].append(result)
            elif "_analysis" in task_id:
                synthesis["synthesis"]["analysis_insights"].append(result)
            elif "_writing" in task_id or "_synthesis" in task_id:
                synthesis["synthesis"]["generated_content"].append(result)
            elif "_review" in task_id:
                synthesis["synthesis"]["review_improvements"].append(result)
        
        return synthesis


class ResearcherAgent(BaseAgent):
    """Agent specialized in gathering information from multiple sources"""
    
    def __init__(self):
        super().__init__(
            agent_id="researcher_001",
            role=AgentRole.RESEARCHER,
            name="Research Specialist"
        )
        self.capabilities = [
            "web_search",
            "data_gathering",
            "source_verification",
            "trend_analysis"
        ]
    
    async def execute_task(self, task: AgentTask) -> Dict:
        """Execute research task"""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        self.current_task = task
        
        try:
            # Import research tools
            from ..tools.data_tools import get_research_engine
            
            research_engine = get_research_engine()
            query = task.input_data.get("query", task.description)
            
            # Conduct parallel research
            results = await research_engine.research(query)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.output_data = {
                "query": query,
                "sources_searched": list(results.keys()),
                "findings": {k: v.to_dict() for k, v in results.items()},
                "summary": self._summarize_findings(results)
            }
            
            return task.output_data
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            return {"error": str(e)}
        finally:
            self.current_task = None
            self.task_history.append(task)
    
    async def can_handle(self, task: AgentTask) -> Tuple[bool, float]:
        """Check if this agent can handle the task"""
        if task.role == AgentRole.RESEARCHER:
            return True, 0.95
        
        description = task.description.lower()
        research_keywords = ["research", "find", "search", "discover", "gather", "collect"]
        
        if any(kw in description for kw in research_keywords):
            return True, 0.8
        
        return False, 0.0
    
    def _summarize_findings(self, results: Dict) -> str:
        """Summarize research findings"""
        summaries = []
        for source, result in results.items():
            if result.success:
                count = len(result.results)
                summaries.append(f"{source}: Found {count} results")
        return "; ".join(summaries) if summaries else "No results found"


class AnalystAgent(BaseAgent):
    """Agent specialized in analyzing data and extracting insights"""
    
    def __init__(self):
        super().__init__(
            agent_id="analyst_001",
            role=AgentRole.ANALYST,
            name="Data Analyst"
        )
        self.capabilities = [
            "data_analysis",
            "pattern_recognition",
            "trend_identification",
            "comparative_analysis"
        ]
    
    async def execute_task(self, task: AgentTask) -> Dict:
        """Execute analysis task"""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        self.current_task = task
        
        try:
            # Get previous results if available
            previous_results = task.input_data.get("previous_results", {})
            
            analysis = {
                "task": task.description,
                "data_analyzed": [],
                "patterns_found": [],
                "insights": [],
                "recommendations": []
            }
            
            # Analyze research findings
            for task_id, result in previous_results.items():
                if "_research" in task_id and "findings" in result:
                    findings = result["findings"]
                    analysis["data_analyzed"].append(task_id)
                    
                    # Extract patterns
                    for source, data in findings.items():
                        if data.get("success") and data.get("results"):
                            results_count = len(data["results"])
                            analysis["patterns_found"].append({
                                "source": source,
                                "data_points": results_count,
                                "pattern": f"Found {results_count} relevant items from {source}"
                            })
            
            # Generate insights
            if analysis["patterns_found"]:
                analysis["insights"].append({
                    "type": "coverage",
                    "insight": f"Analyzed data from {len(analysis['data_analyzed'])} research tasks"
                })
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.output_data = analysis
            
            return analysis
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            return {"error": str(e)}
        finally:
            self.current_task = None
            self.task_history.append(task)
    
    async def can_handle(self, task: AgentTask) -> Tuple[bool, float]:
        """Check if this agent can handle the task"""
        if task.role == AgentRole.ANALYST:
            return True, 0.95
        
        description = task.description.lower()
        analysis_keywords = ["analyze", "compare", "evaluate", "assess", "examine", "study"]
        
        if any(kw in description for kw in analysis_keywords):
            return True, 0.8
        
        return False, 0.0


class WriterAgent(BaseAgent):
    """Agent specialized in creating content and responses"""
    
    def __init__(self):
        super().__init__(
            agent_id="writer_001",
            role=AgentRole.WRITER,
            name="Content Writer"
        )
        self.capabilities = [
            "content_generation",
            "response_synthesis",
            "formatting",
            "storytelling"
        ]
    
    async def execute_task(self, task: AgentTask) -> Dict:
        """Execute writing task"""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        self.current_task = task
        
        try:
            previous_results = task.input_data.get("previous_results", {})
            
            # Gather all insights and findings
            research_data = []
            analysis_data = []
            
            for task_id, result in previous_results.items():
                if "_research" in task_id:
                    research_data.append(result)
                elif "_analysis" in task_id:
                    analysis_data.append(result)
            
            # Create content structure
            content = {
                "task": task.description,
                "sections": [],
                "key_points": [],
                "supporting_data": []
            }
            
            # Add research-based content
            if research_data:
                content["sections"].append({
                    "title": "Research Findings",
                    "content": self._format_research(research_data)
                })
            
            # Add analysis-based content
            if analysis_data:
                content["sections"].append({
                    "title": "Analysis & Insights",
                    "content": self._format_analysis(analysis_data)
                })
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.output_data = content
            
            return content
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            return {"error": str(e)}
        finally:
            self.current_task = None
            self.task_history.append(task)
    
    async def can_handle(self, task: AgentTask) -> Tuple[bool, float]:
        """Check if this agent can handle the task"""
        if task.role == AgentRole.WRITER:
            return True, 0.95
        
        description = task.description.lower()
        writing_keywords = ["write", "create", "generate", "compose", "draft", "synthesize"]
        
        if any(kw in description for kw in writing_keywords):
            return True, 0.8
        
        return False, 0.0
    
    def _format_research(self, research_data: List[Dict]) -> str:
        """Format research data into readable content"""
        content = []
        for data in research_data:
            if "summary" in data:
                content.append(data["summary"])
        return " ".join(content) if content else "Research data collected."
    
    def _format_analysis(self, analysis_data: List[Dict]) -> str:
        """Format analysis data into readable content"""
        insights = []
        for data in analysis_data:
            if "insights" in data:
                for insight in data["insights"]:
                    insights.append(insight.get("insight", ""))
        return " ".join(insights) if insights else "Analysis completed."


class CriticAgent(BaseAgent):
    """Agent specialized in reviewing and improving content"""
    
    def __init__(self):
        super().__init__(
            agent_id="critic_001",
            role=AgentRole.CRITIC,
            name="Quality Critic"
        )
        self.capabilities = [
            "quality_review",
            "fact_checking",
            "improvement_suggestions",
            "consistency_check"
        ]
    
    async def execute_task(self, task: AgentTask) -> Dict:
        """Execute review task"""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        self.current_task = task
        
        try:
            previous_results = task.input_data.get("previous_results", {})
            
            review = {
                "task": task.description,
                "items_reviewed": len(previous_results),
                "quality_scores": {},
                "improvements": [],
                "overall_assessment": ""
            }
            
            # Review each previous result
            for task_id, result in previous_results.items():
                if "error" not in result:
                    score = self._assess_quality(result)
                    review["quality_scores"][task_id] = score
                    
                    if score < 0.8:
                        review["improvements"].append({
                            "task": task_id,
                            "suggestion": "Consider adding more detail and verification"
                        })
            
            # Calculate overall assessment
            if review["quality_scores"]:
                avg_score = sum(review["quality_scores"].values()) / len(review["quality_scores"])
                review["overall_assessment"] = f"Overall quality: {avg_score:.2f}/1.0"
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.output_data = review
            
            return review
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            return {"error": str(e)}
        finally:
            self.current_task = None
            self.task_history.append(task)
    
    async def can_handle(self, task: AgentTask) -> Tuple[bool, float]:
        """Check if this agent can handle the task"""
        if task.role == AgentRole.CRITIC:
            return True, 0.95
        
        description = task.description.lower()
        review_keywords = ["review", "check", "verify", "improve", "critique", "assess"]
        
        if any(kw in description for kw in review_keywords):
            return True, 0.8
        
        return False, 0.0
    
    def _assess_quality(self, result: Dict) -> float:
        """Assess the quality of a result"""
        score = 0.5  # Base score
        
        # Check for completeness
        if result:
            score += 0.2
        
        # Check for error-free
        if "error" not in result:
            score += 0.2
        
        # Check for content
        if any(key in result for key in ["content", "findings", "insights", "sections"]):
            score += 0.1
        
        return min(score, 1.0)


class ExecutorAgent(BaseAgent):
    """Agent specialized in executing tool calls and actions"""
    
    def __init__(self):
        super().__init__(
            agent_id="executor_001",
            role=AgentRole.EXECUTOR,
            name="Tool Executor"
        )
        self.capabilities = [
            "tool_execution",
            "api_calls",
            "file_operations",
            "code_execution"
        ]
    
    async def execute_task(self, task: AgentTask) -> Dict:
        """Execute tool-based task"""
        task.status = TaskStatus.IN_PROGRESS
        task.started_at = datetime.utcnow()
        self.current_task = task
        
        try:
            tool_name = task.input_data.get("tool")
            tool_params = task.input_data.get("params", {})
            
            # Import tool registry
            from ..tools.tool_registry import tool_registry
            
            result = await tool_registry.execute(tool_name, tool_params)
            
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.output_data = result
            
            return result
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            return {"error": str(e)}
        finally:
            self.current_task = None
            self.task_history.append(task)
    
    async def can_handle(self, task: AgentTask) -> Tuple[bool, float]:
        """Check if this agent can handle the task"""
        if task.role == AgentRole.EXECUTOR:
            return True, 0.95
        
        if "tool" in task.input_data:
            return True, 0.9
        
        return False, 0.0


class MultiAgentSystem:
    """
    Main multi-agent system that manages all agents and their collaboration.
    """
    
    def __init__(self):
        # Initialize agents
        self.orchestrator = OrchestratorAgent()
        self.researcher = ResearcherAgent()
        self.analyst = AnalystAgent()
        self.writer = WriterAgent()
        self.critic = CriticAgent()
        self.executor = ExecutorAgent()
        
        # Register collaborators
        self.agents = {
            self.orchestrator.agent_id: self.orchestrator,
            self.researcher.agent_id: self.researcher,
            self.analyst.agent_id: self.analyst,
            self.writer.agent_id: self.writer,
            self.critic.agent_id: self.critic,
            self.executor.agent_id: self.executor
        }
        
        # Set up collaboration network
        for agent in self.agents.values():
            for other_agent in self.agents.values():
                if agent.agent_id != other_agent.agent_id:
                    agent.register_collaborator(other_agent)
    
    async def execute(self, task_description: str, input_data: Dict = None) -> Dict:
        """Execute a task using the multi-agent system"""
        task = AgentTask(
            id=str(uuid.uuid4()),
            description=task_description,
            role=AgentRole.ORCHESTRATOR,
            input_data=input_data or {}
        )
        
        # Let orchestrator handle the task
        result = await self.orchestrator.execute_task(task)
        
        return result
    
    def get_system_status(self) -> Dict:
        """Get status of all agents"""
        return {
            "agents": {agent_id: agent.get_status() for agent_id, agent in self.agents.items()},
            "active_workflows": len(self.orchestrator.active_workflows)
        }


# Global instance
multi_agent_system = MultiAgentSystem()


def get_multi_agent_system() -> MultiAgentSystem:
    """Get the global multi-agent system"""
    return multi_agent_system
