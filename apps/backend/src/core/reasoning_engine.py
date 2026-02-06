"""
McLeuker AI V6 - Reasoning Engine
=================================
Manus AI-style reasoning and task decomposition.

This module provides:
1. Chain-of-thought reasoning for complex queries
2. Task decomposition into executable steps
3. Real-time reasoning stream for transparency
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional, AsyncGenerator
from dataclasses import dataclass, field
from datetime import datetime
import httpx


@dataclass
class ReasoningStep:
    """A single step in the reasoning process"""
    step_id: int
    step_type: str  # "thinking", "planning", "searching", "analyzing", "generating"
    title: str
    description: str
    status: str = "pending"  # pending, in_progress, completed, failed
    details: Dict[str, Any] = field(default_factory=dict)
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            "step_id": self.step_id,
            "step_type": self.step_type,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "details": self.details,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }


@dataclass
class TaskPlan:
    """A complete task plan with all reasoning steps"""
    query: str
    goal: str
    steps: List[ReasoningStep] = field(default_factory=list)
    total_steps: int = 0
    current_step: int = 0
    created_at: datetime = field(default_factory=datetime.utcnow)
    
    def to_dict(self) -> Dict:
        return {
            "query": self.query,
            "goal": self.goal,
            "steps": [s.to_dict() for s in self.steps],
            "total_steps": self.total_steps,
            "current_step": self.current_step,
            "created_at": self.created_at.isoformat()
        }


class ReasoningEngine:
    """
    Manus AI-style Reasoning Engine
    
    Provides transparent, step-by-step reasoning for user queries.
    Shows the AI's thinking process in real-time.
    """
    
    def __init__(self):
        self.grok_api_key = os.getenv("XAI_API_KEY", "")
        self.grok_base_url = "https://api.x.ai/v1"
        
        # Standard task templates for different query types
        self.task_templates = {
            "research": [
                {"type": "thinking", "title": "Understanding Query", "desc": "Analyzing the research question and identifying key concepts"},
                {"type": "planning", "title": "Creating Research Plan", "desc": "Breaking down the research into specific areas to investigate"},
                {"type": "searching", "title": "Gathering Information", "desc": "Searching multiple sources for relevant data"},
                {"type": "analyzing", "title": "Analyzing Findings", "desc": "Cross-referencing sources and extracting key insights"},
                {"type": "generating", "title": "Synthesizing Response", "desc": "Creating a comprehensive, structured response"}
            ],
            "comparison": [
                {"type": "thinking", "title": "Understanding Comparison", "desc": "Identifying the items to compare and comparison criteria"},
                {"type": "planning", "title": "Defining Criteria", "desc": "Establishing the framework for comparison"},
                {"type": "searching", "title": "Gathering Data", "desc": "Collecting information on each item"},
                {"type": "analyzing", "title": "Comparative Analysis", "desc": "Analyzing differences and similarities"},
                {"type": "generating", "title": "Creating Comparison", "desc": "Generating structured comparison output"}
            ],
            "advice": [
                {"type": "thinking", "title": "Understanding Context", "desc": "Analyzing the situation and requirements"},
                {"type": "planning", "title": "Identifying Options", "desc": "Exploring possible recommendations"},
                {"type": "searching", "title": "Validating Options", "desc": "Researching best practices and expert opinions"},
                {"type": "analyzing", "title": "Evaluating Options", "desc": "Weighing pros and cons of each approach"},
                {"type": "generating", "title": "Formulating Advice", "desc": "Creating actionable recommendations"}
            ],
            "general": [
                {"type": "thinking", "title": "Processing Query", "desc": "Understanding what information is needed"},
                {"type": "searching", "title": "Finding Information", "desc": "Searching for relevant data"},
                {"type": "analyzing", "title": "Processing Results", "desc": "Analyzing and organizing findings"},
                {"type": "generating", "title": "Creating Response", "desc": "Generating a helpful response"}
            ]
        }
    
    async def create_task_plan(
        self, 
        query: str, 
        intent_type: str = "general",
        domain: str = "general",
        mode: str = "quick"
    ) -> TaskPlan:
        """
        Create a task plan for the given query.
        
        This analyzes the query and creates a structured plan
        that shows the AI's reasoning process.
        """
        # Determine the appropriate template
        template_key = intent_type if intent_type in self.task_templates else "general"
        template = self.task_templates[template_key]
        
        # Adjust for mode
        if mode == "deep":
            # Add extra analysis steps for deep mode
            extra_steps = [
                {"type": "analyzing", "title": "Deep Analysis", "desc": "Performing comprehensive cross-source analysis"},
                {"type": "analyzing", "title": "Insight Extraction", "desc": "Identifying non-obvious patterns and trends"}
            ]
            template = template[:3] + extra_steps + template[3:]
        
        # Create reasoning steps
        steps = []
        for i, step_template in enumerate(template, 1):
            step = ReasoningStep(
                step_id=i,
                step_type=step_template["type"],
                title=step_template["title"],
                description=step_template["desc"],
                status="pending"
            )
            steps.append(step)
        
        # Generate goal using AI
        goal = await self._generate_goal(query, domain)
        
        return TaskPlan(
            query=query,
            goal=goal,
            steps=steps,
            total_steps=len(steps),
            current_step=0
        )
    
    async def _generate_goal(self, query: str, domain: str) -> str:
        """Generate a clear goal statement for the task"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.grok_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.grok_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-3-mini-fast",
                        "messages": [
                            {
                                "role": "system",
                                "content": "You are a task planner. Given a user query, generate a single clear goal statement that describes what the AI will accomplish. Keep it under 20 words. Do not include any explanation, just the goal."
                            },
                            {
                                "role": "user",
                                "content": f"Query: {query}\nDomain: {domain}"
                            }
                        ],
                        "max_tokens": 50,
                        "temperature": 0.3
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            pass
        
        # Fallback goal
        return f"Research and provide comprehensive insights on: {query[:50]}..."
    
    async def generate_reasoning_stream(
        self,
        query: str,
        context: Optional[Dict] = None
    ) -> AsyncGenerator[Dict, None]:
        """
        Generate a stream of reasoning thoughts.
        
        This provides the "thinking" display that shows
        the AI's internal reasoning process.
        """
        # Initial understanding
        yield {
            "type": "thought",
            "content": f"Let me understand what you're asking about: \"{query[:100]}...\"" if len(query) > 100 else f"Let me understand what you're asking about: \"{query}\"",
            "phase": "understanding"
        }
        await asyncio.sleep(0.2)
        
        # Analyze key concepts
        key_concepts = await self._extract_key_concepts(query)
        yield {
            "type": "thought",
            "content": f"I've identified the key concepts: {', '.join(key_concepts[:5])}",
            "phase": "analysis"
        }
        await asyncio.sleep(0.2)
        
        # Determine approach
        approach = await self._determine_approach(query)
        yield {
            "type": "thought",
            "content": f"My approach will be to {approach}",
            "phase": "planning"
        }
        await asyncio.sleep(0.2)
        
        # Consider context if available
        if context and context.get("previous_messages"):
            yield {
                "type": "thought",
                "content": "I'm considering our previous conversation to provide relevant context...",
                "phase": "context"
            }
            await asyncio.sleep(0.2)
    
    async def _extract_key_concepts(self, query: str) -> List[str]:
        """Extract key concepts from the query"""
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.post(
                    f"{self.grok_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.grok_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-3-mini-fast",
                        "messages": [
                            {
                                "role": "system",
                                "content": "Extract 3-5 key concepts from the query. Return only a JSON array of strings. Example: [\"concept1\", \"concept2\", \"concept3\"]"
                            },
                            {
                                "role": "user",
                                "content": query
                            }
                        ],
                        "max_tokens": 100,
                        "temperature": 0.1
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    # Try to parse as JSON
                    try:
                        return json.loads(content)
                    except:
                        # Extract words from response
                        return [w.strip() for w in content.replace("[", "").replace("]", "").replace('"', '').split(",")][:5]
        except:
            pass
        
        # Fallback: simple word extraction
        words = query.split()
        return [w for w in words if len(w) > 4][:5]
    
    async def _determine_approach(self, query: str) -> str:
        """Determine the best approach for the query"""
        query_lower = query.lower()
        
        if any(word in query_lower for word in ["compare", "vs", "versus", "difference"]):
            return "compare the options systematically and highlight key differences"
        elif any(word in query_lower for word in ["trend", "forecast", "future", "predict"]):
            return "analyze current trends and provide forward-looking insights"
        elif any(word in query_lower for word in ["how to", "guide", "steps", "process"]):
            return "provide a step-by-step guide with practical recommendations"
        elif any(word in query_lower for word in ["best", "top", "recommend"]):
            return "evaluate options and provide ranked recommendations"
        elif any(word in query_lower for word in ["analyze", "analysis", "research"]):
            return "conduct comprehensive research and synthesize findings"
        else:
            return "gather relevant information and provide a comprehensive overview"


# Global instance
reasoning_engine = ReasoningEngine()
