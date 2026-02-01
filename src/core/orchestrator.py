"""
V3.1 Core Orchestrator
The unified brain that coordinates all layers using Grok as the sole reasoning model.
Implements the Think-Act-Observe-Correct loop with credit management.
"""

import asyncio
import json
import time
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from enum import Enum
import aiohttp

from src.config.settings import settings


class TaskType(Enum):
    """Types of tasks the orchestrator can handle."""
    SIMPLE_QUERY = "simple_query"
    RESEARCH = "research"
    DATA_ANALYSIS = "data_analysis"
    WEB_ACTION = "web_action"
    IMAGE_GENERATION = "image_generation"
    FILE_GENERATION = "file_generation"
    MULTI_STEP = "multi_step"


@dataclass
class TaskContext:
    """Context for a task execution."""
    user_id: str
    session_id: str
    query: str
    conversation_history: List[Dict] = field(default_factory=list)
    credits_available: int = 100
    credits_used: int = 0
    task_type: TaskType = TaskType.SIMPLE_QUERY
    requires_search: bool = False
    requires_action: bool = False
    requires_analyst: bool = False
    requires_image: bool = False
    pending_user_input: Optional[str] = None
    collected_data: Dict = field(default_factory=dict)
    reasoning_steps: List[str] = field(default_factory=list)
    sources: List[Dict] = field(default_factory=list)


@dataclass
class OrchestratorResponse:
    """Response from the orchestrator."""
    success: bool
    response: str
    reasoning: List[str] = field(default_factory=list)
    sources: List[Dict] = field(default_factory=list)
    files: List[Dict] = field(default_factory=list)
    images: List[str] = field(default_factory=list)
    follow_up_questions: List[str] = field(default_factory=list)
    credits_used: int = 0
    needs_user_input: bool = False
    user_input_prompt: Optional[str] = None
    error: Optional[str] = None


class GrokBrain:
    """The unified Grok-powered reasoning engine."""
    
    def __init__(self):
        self.api_key = settings.XAI_API_KEY
        self.model = settings.GROK_MODEL
        self.base_url = settings.GROK_API_BASE
        
    async def think(self, prompt: str, system_prompt: str = None, temperature: float = 0.1) -> str:
        """Execute a reasoning step using Grok."""
        if not self.api_key:
            raise ValueError("Grok API key not configured")
        
        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{self.base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": settings.LLM_MAX_TOKENS
                },
                timeout=aiohttp.ClientTimeout(total=60)
            ) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"Grok API error: {resp.status} - {error_text}")
                
                data = await resp.json()
                return data["choices"][0]["message"]["content"]
    
    async def analyze_task(self, query: str, conversation_history: List[Dict] = None) -> Dict:
        """Analyze the user's query to determine task type and requirements."""
        
        system_prompt = """You are a task analyzer for a fashion and lifestyle AI platform.
Analyze the user's query and determine:
1. task_type: One of [simple_query, research, data_analysis, web_action, image_generation, file_generation, multi_step]
2. requires_search: Does this need real-time web search? (true/false)
3. requires_action: Does this need web browsing/interaction? (true/false)
4. requires_analyst: Does this need data analysis or file generation? (true/false)
5. requires_image: Does this need image generation? (true/false)
6. missing_info: List any critical information missing from the query that we should ask the user for.

Focus on fashion, beauty, textile, skincare, lifestyle, tech, sustainability, culture, and catwalks.

Respond in JSON format only:
{
    "task_type": "...",
    "requires_search": true/false,
    "requires_action": true/false,
    "requires_analyst": true/false,
    "requires_image": true/false,
    "missing_info": ["list of missing info"] or [],
    "reasoning": "brief explanation of your analysis"
}"""

        context = ""
        if conversation_history:
            context = "\n\nPrevious conversation:\n"
            for msg in conversation_history[-5:]:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                context += f"{role}: {content}\n"
        
        prompt = f"{context}\n\nUser query: {query}\n\nAnalyze this task:"
        
        response = await self.think(prompt, system_prompt, temperature=0.0)
        
        # Parse JSON response
        try:
            # Clean up response if needed
            response = response.strip()
            if response.startswith("```json"):
                response = response[7:]
            if response.startswith("```"):
                response = response[3:]
            if response.endswith("```"):
                response = response[:-3]
            
            return json.loads(response)
        except json.JSONDecodeError:
            # Default analysis if parsing fails
            return {
                "task_type": "simple_query",
                "requires_search": True,
                "requires_action": False,
                "requires_analyst": False,
                "requires_image": False,
                "missing_info": [],
                "reasoning": "Default analysis due to parsing error"
            }
    
    async def generate_response(self, context: TaskContext, search_results: str = "", 
                                 analyst_results: str = "", action_results: str = "") -> str:
        """Generate the final response based on all collected data."""
        
        system_prompt = """You are McLeuker Fashion AI, a frontier agentic AI platform specializing in fashion, beauty, textile, skincare, lifestyle, tech, sustainability, culture, and catwalks.

Your responses should be:
1. Comprehensive and well-structured with clear sections
2. Include relevant emojis for visual appeal
3. Cite sources when using search results
4. Provide actionable insights
5. Be professional yet engaging

Format your response with:
- Clear headings using ##
- Bullet points for lists
- Bold for key terms
- Source citations as [1], [2], etc."""

        prompt = f"""User Query: {context.query}

{"Search Results:" + search_results if search_results else ""}
{"Analysis Results:" + analyst_results if analyst_results else ""}
{"Web Action Results:" + action_results if action_results else ""}

Previous conversation context:
{json.dumps(context.conversation_history[-3:], indent=2) if context.conversation_history else "None"}

Generate a comprehensive, helpful response:"""

        return await self.think(prompt, system_prompt, temperature=0.3)
    
    async def generate_follow_ups(self, query: str, response: str) -> List[str]:
        """Generate relevant follow-up questions."""
        
        prompt = f"""Based on this conversation:
User asked: {query}
AI responded: {response[:500]}...

Generate 3 relevant follow-up questions the user might want to ask next.
Focus on fashion, beauty, lifestyle, and related topics.
Return as a JSON array of strings only: ["question1", "question2", "question3"]"""

        result = await self.think(prompt, temperature=0.5)
        
        try:
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            return json.loads(result)
        except:
            return [
                "What are the latest trends in this area?",
                "Can you provide more details?",
                "How does this compare to alternatives?"
            ]


class V31Orchestrator:
    """
    The V3.1 Master Orchestrator
    Coordinates all layers: Reasoning, Search, Action, Analyst, Output
    """
    
    def __init__(self):
        self.brain = GrokBrain()
        self.search_layer = None
        self.action_layer = None
        self.analyst_layer = None
        self.output_layer = None
    
    def set_layers(self, search=None, action=None, analyst=None, output=None):
        """Set the layer implementations."""
        self.search_layer = search
        self.action_layer = action
        self.analyst_layer = analyst
        self.output_layer = output
    
    async def process(self, user_id: str, session_id: str, query: str,
                      conversation_history: List[Dict] = None,
                      credits_available: int = 100) -> OrchestratorResponse:
        """
        Main entry point for processing user queries.
        Implements the Think-Act-Observe-Correct loop.
        """
        
        # Initialize context
        context = TaskContext(
            user_id=user_id,
            session_id=session_id,
            query=query,
            conversation_history=conversation_history or [],
            credits_available=credits_available
        )
        
        try:
            # STEP 1: THINK - Analyze the task
            context.reasoning_steps.append("🧠 Analyzing your request...")
            analysis = await self.brain.analyze_task(query, conversation_history)
            
            context.task_type = TaskType(analysis.get("task_type", "simple_query"))
            context.requires_search = analysis.get("requires_search", False)
            context.requires_action = analysis.get("requires_action", False)
            context.requires_analyst = analysis.get("requires_analyst", False)
            context.requires_image = analysis.get("requires_image", False)
            
            # Check for missing information (Manus-style interaction)
            missing_info = analysis.get("missing_info", [])
            if missing_info:
                return OrchestratorResponse(
                    success=True,
                    response="",
                    needs_user_input=True,
                    user_input_prompt=f"To help you better, I need some additional information: {', '.join(missing_info)}. Could you please provide these details?",
                    reasoning=context.reasoning_steps
                )
            
            # Credit cost estimation
            estimated_cost = settings.CREDIT_COST_REASONING
            if context.requires_search:
                estimated_cost += settings.CREDIT_COST_SEARCH
            if context.requires_action:
                estimated_cost += settings.CREDIT_COST_ACTION
            if context.requires_analyst:
                estimated_cost += settings.CREDIT_COST_ANALYST
            if context.requires_image:
                estimated_cost += settings.CREDIT_COST_IMAGE
            
            # Check credits (only block if completely out)
            if credits_available <= 0:
                return OrchestratorResponse(
                    success=False,
                    response="You've run out of credits. Please top up to continue using the platform.",
                    needs_user_input=True,
                    user_input_prompt="Your credit balance is empty. Would you like to add more credits to continue?",
                    error="insufficient_credits"
                )
            
            # STEP 2: ACT - Execute required layers
            search_results = ""
            action_results = ""
            analyst_results = ""
            
            # Execute Search Layer (Parallel)
            if context.requires_search and self.search_layer:
                context.reasoning_steps.append("🔍 Searching across multiple sources...")
                search_data = await self.search_layer.parallel_search(query)
                search_results = search_data.get("synthesized", "")
                context.sources = search_data.get("sources", [])
                context.credits_used += settings.CREDIT_COST_SEARCH
            
            # Execute Action Layer
            if context.requires_action and self.action_layer:
                context.reasoning_steps.append("🌐 Browsing the web for live data...")
                action_results = await self.action_layer.execute(query, context.collected_data)
                context.credits_used += settings.CREDIT_COST_ACTION
            
            # Execute Analyst Layer
            if context.requires_analyst and self.analyst_layer:
                context.reasoning_steps.append("📊 Analyzing data and generating files...")
                analyst_data = await self.analyst_layer.execute(query, context.collected_data)
                analyst_results = analyst_data.get("analysis", "")
                context.collected_data["files"] = analyst_data.get("files", [])
                context.credits_used += settings.CREDIT_COST_ANALYST
            
            # Execute Image Generation
            images = []
            if context.requires_image and self.output_layer:
                context.reasoning_steps.append("🎨 Generating visual content...")
                images = await self.output_layer.generate_images(query)
                context.credits_used += settings.CREDIT_COST_IMAGE
            
            # STEP 3: OBSERVE & SYNTHESIZE - Generate final response
            context.reasoning_steps.append("✨ Synthesizing your response...")
            response = await self.brain.generate_response(
                context, search_results, analyst_results, action_results
            )
            
            # Generate follow-up questions
            follow_ups = await self.brain.generate_follow_ups(query, response)
            
            # Add reasoning credit
            context.credits_used += settings.CREDIT_COST_REASONING
            
            return OrchestratorResponse(
                success=True,
                response=response,
                reasoning=context.reasoning_steps,
                sources=context.sources,
                files=context.collected_data.get("files", []),
                images=images,
                follow_up_questions=follow_ups,
                credits_used=context.credits_used
            )
            
        except Exception as e:
            return OrchestratorResponse(
                success=False,
                response=f"I encountered an error while processing your request. Please try again.",
                error=str(e),
                reasoning=context.reasoning_steps
            )


# Global orchestrator instance
orchestrator = V31Orchestrator()
