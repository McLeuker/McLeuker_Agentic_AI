"""
V3.1 Core Orchestrator - FIXED VERSION
The unified brain that coordinates all layers using Grok as the sole reasoning model.
Implements the Think-Act-Observe-Correct loop with credit management.

FIXES APPLIED:
1. Sources are now properly formatted as strings before being passed to Grok
2. Response text no longer contains [object Object]
3. Better error handling for edge cases
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


def format_sources_for_prompt(sources: List[Dict]) -> str:
    """
    FIX: Format sources as a readable string for the Grok prompt.
    This prevents [object Object] from appearing in responses.
    """
    if not sources:
        return ""
    
    formatted = "\n\nAvailable Sources:\n"
    for i, source in enumerate(sources, 1):
        title = source.get('title', 'Unknown Source')
        url = source.get('url', '')
        snippet = source.get('snippet', '')[:200] if source.get('snippet') else ''
        
        formatted += f"[{i}] {title}\n"
        if url:
            formatted += f"    URL: {url}\n"
        if snippet:
            formatted += f"    Summary: {snippet}...\n"
        formatted += "\n"
    
    return formatted


def format_sources_for_response(sources: List[Dict]) -> str:
    """
    FIX: Format sources as citation text for the final response.
    """
    if not sources:
        return ""
    
    formatted = "\n\n**Sources:**\n"
    for i, source in enumerate(sources, 1):
        title = source.get('title', 'Unknown Source')
        url = source.get('url', '#')
        formatted += f"[{i}] [{title}]({url})\n"
    
    return formatted


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

IMPORTANT: For simple conversational queries like "why?", "what?", "how?", etc., set missing_info to empty array and task_type to "simple_query".
Only ask for more info if the query is genuinely ambiguous about a complex task.

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
        
        # FIX: Format sources as readable text, not objects
        formatted_sources = format_sources_for_prompt(context.sources)
        
        system_prompt = """You are McLeuker Fashion AI, a frontier agentic AI platform specializing in fashion, beauty, textile, skincare, lifestyle, tech, sustainability, culture, and catwalks.

Your responses should be:
1. Comprehensive and well-structured with clear sections
2. Include relevant emojis for visual appeal
3. Cite sources using [1], [2], etc. format when referencing information from the provided sources
4. Provide actionable insights
5. Be professional yet engaging

Format your response with:
- Clear headings using ## for main sections
- Bullet points for lists
- Bold for emphasis on key terms
- Citations like [1], [2] when referencing sources

IMPORTANT: When citing sources, use the number format [1], [2], etc. DO NOT include the full source object or URL inline.
The sources will be listed separately at the end of your response."""

        # Build the prompt with all available data
        prompt_parts = [f"User Query: {context.query}"]
        
        if search_results:
            prompt_parts.append(f"\n\nSearch Results:\n{search_results}")
        
        if analyst_results:
            prompt_parts.append(f"\n\nAnalysis Results:\n{analyst_results}")
            
        if action_results:
            prompt_parts.append(f"\n\nWeb Action Results:\n{action_results}")
        
        # FIX: Add formatted sources (as strings, not objects)
        if formatted_sources:
            prompt_parts.append(formatted_sources)
        
        prompt_parts.append("\n\nGenerate a comprehensive, well-structured response:")
        
        prompt = "\n".join(prompt_parts)
        
        response = await self.think(prompt, system_prompt, temperature=0.7)
        
        # FIX: Clean up any accidental [object Object] that might have slipped through
        response = response.replace("[object Object]", "")
        response = response.replace(",[object Object],", "")
        response = response.replace(", [object Object],", "")
        response = response.replace("[object Object],", "")
        response = response.replace(",[object Object]", "")
        
        return response


class FashionOrchestrator:
    """The main orchestrator that coordinates all layers."""
    
    def __init__(self):
        self.brain = GrokBrain()
        self.search_layer = None
        self.action_layer = None
        self.analyst_layer = None
        self.output_layer = None
        
    async def initialize_layers(self):
        """Initialize all available layers."""
        try:
            from src.layers.search import SearchLayer
            self.search_layer = SearchLayer()
        except Exception as e:
            print(f"Search layer not available: {e}")
            
        try:
            from src.layers.action import ActionLayer
            self.action_layer = ActionLayer()
        except Exception as e:
            print(f"Action layer not available: {e}")
            
        try:
            from src.layers.analyst import AnalystLayer
            self.analyst_layer = AnalystLayer()
        except Exception as e:
            print(f"Analyst layer not available: {e}")
            
        try:
            from src.layers.output import OutputLayer
            self.output_layer = OutputLayer()
        except Exception as e:
            print(f"Output layer not available: {e}")
    
    async def process_query(self, user_id: str, session_id: str, query: str, 
                           conversation_history: List[Dict] = None,
                           mode: str = "auto") -> OrchestratorResponse:
        """Process a user query through the orchestration pipeline."""
        
        # Initialize context
        context = TaskContext(
            user_id=user_id,
            session_id=session_id,
            query=query,
            conversation_history=conversation_history or []
        )
        
        try:
            # Step 1: Analyze the task
            context.reasoning_steps.append("🧠 Analyzing your request...")
            analysis = await self.brain.analyze_task(query, conversation_history)
            
            # FIX: Don't ask for user input on simple queries
            # Only ask if there's genuinely missing critical information
            if analysis.get("missing_info") and len(analysis.get("missing_info", [])) > 0:
                # Check if the query is too short/vague for a complex task
                if len(query.strip()) < 10 and analysis.get("task_type") != "simple_query":
                    # For very short queries, just try to answer instead of asking for more info
                    analysis["missing_info"] = []
            
            # Update context based on analysis
            context.task_type = TaskType(analysis.get("task_type", "simple_query"))
            context.requires_search = analysis.get("requires_search", False)
            context.requires_action = analysis.get("requires_action", False)
            context.requires_analyst = analysis.get("requires_analyst", False)
            context.requires_image = analysis.get("requires_image", False)
            
            # Step 2: Execute search if needed
            search_results = ""
            if context.requires_search and self.search_layer:
                context.reasoning_steps.append("🔍 Searching across multiple sources...")
                try:
                    search_data = await self.search_layer.search(query)
                    search_results = search_data.get("formatted_results", "")
                    
                    # FIX: Store sources as proper objects for later formatting
                    raw_sources = search_data.get("sources", [])
                    for source in raw_sources:
                        if isinstance(source, dict):
                            context.sources.append({
                                "title": str(source.get("title", "Unknown")),
                                "url": str(source.get("url", "")),
                                "snippet": str(source.get("snippet", ""))[:300],
                                "source": str(source.get("source", "Web"))
                            })
                    
                    context.credits_used += 1
                except Exception as e:
                    print(f"Search error: {e}")
            
            # Step 3: Execute action if needed
            action_results = ""
            if context.requires_action and self.action_layer:
                context.reasoning_steps.append("🌐 Performing web actions...")
                try:
                    action_data = await self.action_layer.execute(query)
                    action_results = action_data.get("results", "")
                    context.credits_used += 2
                except Exception as e:
                    print(f"Action error: {e}")
            
            # Step 4: Execute analyst if needed
            analyst_results = ""
            if context.requires_analyst and self.analyst_layer:
                context.reasoning_steps.append("📊 Analyzing data...")
                try:
                    analyst_data = await self.analyst_layer.analyze(query, context.collected_data)
                    analyst_results = analyst_data.get("analysis", "")
                    context.credits_used += 2
                except Exception as e:
                    print(f"Analyst error: {e}")
            
            # Step 5: Generate response
            context.reasoning_steps.append("✨ Synthesizing your response...")
            response_text = await self.brain.generate_response(
                context, 
                search_results=search_results,
                analyst_results=analyst_results,
                action_results=action_results
            )
            
            # FIX: Final cleanup of any [object Object] in response
            response_text = self._clean_response(response_text)
            
            # Step 6: Generate follow-up questions
            follow_ups = await self._generate_follow_ups(query, response_text)
            
            return OrchestratorResponse(
                success=True,
                response=response_text,
                reasoning=context.reasoning_steps,
                sources=context.sources,  # Return as proper objects for frontend
                follow_up_questions=follow_ups,
                credits_used=max(context.credits_used, 1)
            )
            
        except Exception as e:
            return OrchestratorResponse(
                success=False,
                response=f"I encountered an error while processing your request. Please try again.",
                reasoning=context.reasoning_steps,
                error=str(e),
                credits_used=1
            )
    
    def _clean_response(self, response: str) -> str:
        """
        FIX: Clean any [object Object] artifacts from the response.
        This is a safety net in case any slip through.
        """
        if not response:
            return response
            
        # Remove various forms of [object Object]
        patterns_to_remove = [
            "[object Object]",
            ",[object Object],",
            ", [object Object],",
            "[object Object],",
            ",[object Object]",
            " [object Object] ",
        ]
        
        for pattern in patterns_to_remove:
            response = response.replace(pattern, "")
        
        # Clean up any double spaces or commas left behind
        while "  " in response:
            response = response.replace("  ", " ")
        while ",," in response:
            response = response.replace(",,", ",")
        while ", ," in response:
            response = response.replace(", ,", ",")
            
        return response.strip()
    
    async def _generate_follow_ups(self, query: str, response: str) -> List[str]:
        """Generate follow-up questions based on the conversation."""
        try:
            system_prompt = """Generate 3 relevant follow-up questions based on the user's query and the response provided.
The questions should:
1. Dig deeper into the topic
2. Explore related aspects
3. Be concise (under 50 characters each)

Return as a JSON array of strings only, no other text:
["Question 1?", "Question 2?", "Question 3?"]"""
            
            prompt = f"User asked: {query}\n\nResponse summary: {response[:500]}...\n\nGenerate follow-up questions:"
            
            result = await self.brain.think(prompt, system_prompt, temperature=0.7)
            
            # Parse the JSON array
            result = result.strip()
            if result.startswith("```"):
                result = result.split("```")[1]
                if result.startswith("json"):
                    result = result[4:]
            
            return json.loads(result)
        except:
            return [
                "Tell me more about this topic",
                "What are the latest trends?",
                "How can I apply this?"
            ]


# Singleton instance
_orchestrator = None

async def get_orchestrator() -> FashionOrchestrator:
    """Get or create the orchestrator singleton."""
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = FashionOrchestrator()
        await _orchestrator.initialize_layers()
    return _orchestrator
