"""
McLeuker AI V8 - Human-Like Conversational Engine
==================================================
Advanced response generation that produces natural, reasoning-first,
conversational outputs like Manus AI. Uses Grok-4 for deep reasoning
and Kimi K2.5 for execution.

Key Features:
- Natural conversational tone
- Reasoning-first approach (show thinking process)
- Context-aware responses
- Dynamic structure based on query complexity
- No rigid templates - each response is unique
"""

import os
import json
import asyncio
import aiohttp
from datetime import datetime
from typing import Optional, Dict, Any, List, AsyncGenerator, Tuple
from dataclasses import dataclass, field
from enum import Enum
import logging
import re

logger = logging.getLogger(__name__)


# API Configuration
GROK_API_KEY = os.getenv("GROK_API_KEY", "") or os.getenv("XAI_API_KEY", "")
MOONSHOT_API_KEY = os.getenv("MOONSHOT_API_KEY", "")
GROK_BASE_URL = "https://api.x.ai/v1"
KIMI_BASE_URL = "https://api.moonshot.cn/v1"


class ResponseStyle(Enum):
    """Different response styles based on query type"""
    CONVERSATIONAL = "conversational"      # Natural, flowing dialogue
    ANALYTICAL = "analytical"              # Deep analysis with reasoning
    CREATIVE = "creative"                  # Imaginative, exploratory
    INFORMATIVE = "informative"            # Fact-focused, educational
    ADVISORY = "advisory"                  # Recommendation-based


class QueryComplexity(Enum):
    """Query complexity levels"""
    SIMPLE = "simple"           # Quick, direct answer
    MODERATE = "moderate"       # Some reasoning needed
    COMPLEX = "complex"         # Deep analysis required
    RESEARCH = "research"       # Multi-source research


@dataclass
class ConversationTurn:
    """A single turn in the conversation"""
    role: str
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict = field(default_factory=dict)


@dataclass
class ResponsePlan:
    """Plan for generating a response"""
    query: str
    style: ResponseStyle
    complexity: QueryComplexity
    reasoning_steps: List[str]
    sections_needed: List[str]
    tone: str
    estimated_length: str


class QueryAnalyzer:
    """Analyzes queries to determine response approach"""
    
    def analyze(self, query: str, context: Dict = None) -> ResponsePlan:
        """Analyze query and create response plan"""
        query_lower = query.lower()
        
        # Determine complexity
        complexity = self._assess_complexity(query_lower)
        
        # Determine style
        style = self._determine_style(query_lower)
        
        # Plan reasoning steps
        reasoning_steps = self._plan_reasoning(query_lower, complexity)
        
        # Determine sections needed
        sections = self._determine_sections(query_lower, complexity)
        
        # Determine tone
        tone = self._determine_tone(query_lower, context)
        
        # Estimate length
        length = self._estimate_length(complexity)
        
        return ResponsePlan(
            query=query,
            style=style,
            complexity=complexity,
            reasoning_steps=reasoning_steps,
            sections_needed=sections,
            tone=tone,
            estimated_length=length
        )
    
    def _assess_complexity(self, query: str) -> QueryComplexity:
        """Assess query complexity"""
        # Research indicators
        research_keywords = ["research", "comprehensive", "in-depth", "analyze", "compare", "all", "everything"]
        if any(kw in query for kw in research_keywords):
            return QueryComplexity.RESEARCH
        
        # Complex indicators
        complex_keywords = ["why", "how does", "explain", "impact", "relationship", "future"]
        if any(kw in query for kw in complex_keywords):
            return QueryComplexity.COMPLEX
        
        # Moderate indicators
        moderate_keywords = ["what are", "tell me about", "describe", "list"]
        if any(kw in query for kw in moderate_keywords):
            return QueryComplexity.MODERATE
        
        return QueryComplexity.SIMPLE
    
    def _determine_style(self, query: str) -> ResponseStyle:
        """Determine appropriate response style"""
        if any(kw in query for kw in ["analyze", "compare", "evaluate", "assess"]):
            return ResponseStyle.ANALYTICAL
        if any(kw in query for kw in ["create", "imagine", "design", "innovative"]):
            return ResponseStyle.CREATIVE
        if any(kw in query for kw in ["recommend", "suggest", "should", "best"]):
            return ResponseStyle.ADVISORY
        if any(kw in query for kw in ["what is", "define", "explain", "how"]):
            return ResponseStyle.INFORMATIVE
        return ResponseStyle.CONVERSATIONAL
    
    def _plan_reasoning(self, query: str, complexity: QueryComplexity) -> List[str]:
        """Plan reasoning steps"""
        steps = ["Understanding the question"]
        
        if complexity in [QueryComplexity.COMPLEX, QueryComplexity.RESEARCH]:
            steps.extend([
                "Identifying key aspects to explore",
                "Gathering relevant information",
                "Analyzing patterns and connections",
                "Synthesizing insights"
            ])
        elif complexity == QueryComplexity.MODERATE:
            steps.extend([
                "Identifying relevant information",
                "Organizing key points"
            ])
        
        steps.append("Formulating response")
        return steps
    
    def _determine_sections(self, query: str, complexity: QueryComplexity) -> List[str]:
        """Determine what sections the response needs"""
        sections = []
        
        if complexity == QueryComplexity.RESEARCH:
            sections = ["context", "analysis", "findings", "implications", "recommendations"]
        elif complexity == QueryComplexity.COMPLEX:
            sections = ["overview", "analysis", "insights"]
        elif complexity == QueryComplexity.MODERATE:
            sections = ["main_points", "details"]
        else:
            sections = ["direct_answer"]
        
        return sections
    
    def _determine_tone(self, query: str, context: Dict = None) -> str:
        """Determine appropriate tone"""
        if any(kw in query for kw in ["urgent", "quickly", "asap"]):
            return "direct and efficient"
        if any(kw in query for kw in ["help", "confused", "understand"]):
            return "supportive and clear"
        if any(kw in query for kw in ["professional", "business", "formal"]):
            return "professional and precise"
        return "warm and conversational"
    
    def _estimate_length(self, complexity: QueryComplexity) -> str:
        """Estimate response length"""
        if complexity == QueryComplexity.RESEARCH:
            return "comprehensive (800-1500 words)"
        elif complexity == QueryComplexity.COMPLEX:
            return "detailed (400-800 words)"
        elif complexity == QueryComplexity.MODERATE:
            return "moderate (200-400 words)"
        return "concise (50-200 words)"


class HumanLikeResponseGenerator:
    """
    Generates human-like, conversational responses.
    Avoids rigid templates and produces natural, reasoning-first output.
    """
    
    def __init__(self):
        self.analyzer = QueryAnalyzer()
        self.grok_model = "grok-4"
        self.kimi_model = "kimi-k2.5-preview"
    
    async def generate_response(
        self,
        query: str,
        context: Dict = None,
        conversation_history: List[ConversationTurn] = None,
        rag_context: str = None
    ) -> AsyncGenerator[Dict, None]:
        """Generate a human-like response with streaming"""
        
        # Analyze query
        plan = self.analyzer.analyze(query, context)
        
        # Build the prompt
        system_prompt = self._build_system_prompt(plan, rag_context)
        user_prompt = self._build_user_prompt(query, conversation_history, context)
        
        # Stream reasoning and response
        async for chunk in self._stream_grok_response(system_prompt, user_prompt, plan):
            yield chunk
    
    def _build_system_prompt(self, plan: ResponsePlan, rag_context: str = None) -> str:
        """Build system prompt for natural conversation"""
        
        prompt = f"""You are McLeuker AI, an expert fashion intelligence assistant. Your responses should feel like a natural conversation with a knowledgeable friend who happens to be a fashion industry expert.

## Your Communication Style

**Be Natural and Human:**
- Write as if you're having a real conversation, not generating a report
- Use natural transitions and flow between ideas
- Vary your sentence structure and length
- Show genuine curiosity and engagement with the topic
- It's okay to express nuanced opinions when appropriate

**Show Your Thinking:**
- Share your reasoning process naturally, like thinking out loud
- Connect ideas with phrases like "What's interesting here is...", "This connects to...", "I'm noticing that..."
- Acknowledge complexity when it exists: "This is nuanced because..."
- Be honest about uncertainty: "From what I understand...", "The evidence suggests..."

**Avoid These Patterns:**
- Don't use rigid bullet point lists for everything
- Don't start every section with the same structure
- Don't use corporate-speak or overly formal language
- Don't repeat the same phrases or transitions
- Never use phrases like "Certainly!", "Of course!", "Great question!"
- Don't artificially pad responses with unnecessary words

**Response Approach for This Query:**
- Style: {plan.style.value}
- Complexity: {plan.complexity.value}
- Tone: {plan.tone}
- Length: {plan.estimated_length}

**Reasoning Steps to Follow:**
{chr(10).join(f"- {step}" for step in plan.reasoning_steps)}
"""
        
        if rag_context:
            prompt += f"""

## Relevant Knowledge to Draw From:
{rag_context}

Use this knowledge naturally in your response - weave it into your conversation rather than citing it formally.
"""
        
        prompt += """

## Final Notes:
- Each response should feel unique and tailored to this specific question
- Structure your response based on what makes sense for the content, not a template
- If the question is simple, give a simple answer - don't over-explain
- If it's complex, take the reader on a journey through your thinking
- End naturally, not with forced calls-to-action or summary statements
"""
        
        return prompt
    
    def _build_user_prompt(
        self,
        query: str,
        conversation_history: List[ConversationTurn] = None,
        context: Dict = None
    ) -> str:
        """Build user prompt with context"""
        
        prompt_parts = []
        
        # Add conversation history if available
        if conversation_history:
            prompt_parts.append("Previous conversation:")
            for turn in conversation_history[-5:]:  # Last 5 turns
                role = "User" if turn.role == "user" else "Assistant"
                prompt_parts.append(f"{role}: {turn.content[:500]}")
            prompt_parts.append("")
        
        # Add context if available
        if context:
            if context.get("user_profile"):
                profile = context["user_profile"]
                if profile.get("interests"):
                    prompt_parts.append(f"User interests: {', '.join(profile['interests'][:5])}")
            if context.get("relevant_memories"):
                prompt_parts.append(f"Relevant context: {'; '.join(context['relevant_memories'][:3])}")
            prompt_parts.append("")
        
        # Add the query
        prompt_parts.append(f"User: {query}")
        
        return "\n".join(prompt_parts)
    
    async def _stream_grok_response(
        self,
        system_prompt: str,
        user_prompt: str,
        plan: ResponsePlan
    ) -> AsyncGenerator[Dict, None]:
        """Stream response from Grok-4"""
        
        if not GROK_API_KEY:
            yield {"type": "error", "data": {"message": "Grok API key not configured"}}
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {GROK_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                # Determine temperature based on style
                temperature = 0.7  # Default conversational
                if plan.style == ResponseStyle.ANALYTICAL:
                    temperature = 0.4
                elif plan.style == ResponseStyle.CREATIVE:
                    temperature = 0.9
                
                payload = {
                    "model": self.grok_model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": temperature,
                    "max_tokens": 4000,
                    "stream": True
                }
                
                # Yield reasoning start
                yield {
                    "type": "reasoning_start",
                    "data": {
                        "style": plan.style.value,
                        "complexity": plan.complexity.value,
                        "steps": plan.reasoning_steps
                    }
                }
                
                # Yield reasoning steps
                for i, step in enumerate(plan.reasoning_steps):
                    yield {
                        "type": "reasoning_step",
                        "data": {
                            "step_num": i + 1,
                            "total_steps": len(plan.reasoning_steps),
                            "description": step
                        }
                    }
                    await asyncio.sleep(0.3)  # Brief pause for UX
                
                yield {"type": "reasoning_complete", "data": {}}
                yield {"type": "response_start", "data": {}}
                
                async with session.post(
                    f"{GROK_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        yield {"type": "error", "data": {"message": f"API error: {error_text}"}}
                        return
                    
                    full_content = ""
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data = line[6:]
                            if data == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data)
                                delta = chunk.get('choices', [{}])[0].get('delta', {})
                                content = delta.get('content', '')
                                if content:
                                    full_content += content
                                    yield {
                                        "type": "content",
                                        "data": {"chunk": content}
                                    }
                            except json.JSONDecodeError:
                                continue
                    
                    yield {
                        "type": "response_complete",
                        "data": {
                            "full_content": full_content,
                            "style": plan.style.value,
                            "complexity": plan.complexity.value
                        }
                    }
                    
        except Exception as e:
            logger.error(f"Grok streaming error: {e}")
            yield {"type": "error", "data": {"message": str(e)}}
    
    async def generate_with_kimi_execution(
        self,
        query: str,
        tools: List[Dict] = None,
        context: Dict = None
    ) -> AsyncGenerator[Dict, None]:
        """Generate response with Kimi K2.5 for tool execution"""
        
        if not MOONSHOT_API_KEY:
            yield {"type": "error", "data": {"message": "Moonshot API key not configured"}}
            return
        
        try:
            async with aiohttp.ClientSession() as session:
                headers = {
                    "Authorization": f"Bearer {MOONSHOT_API_KEY}",
                    "Content-Type": "application/json"
                }
                
                messages = [
                    {
                        "role": "system",
                        "content": "You are McLeuker AI's execution engine. Execute tool calls efficiently and return structured results."
                    },
                    {"role": "user", "content": query}
                ]
                
                payload = {
                    "model": self.kimi_model,
                    "messages": messages,
                    "temperature": 0.3,
                    "max_tokens": 4000,
                    "stream": True
                }
                
                if tools:
                    payload["tools"] = tools
                    payload["tool_choice"] = "auto"
                
                yield {"type": "execution_start", "data": {"model": self.kimi_model}}
                
                async with session.post(
                    f"{KIMI_BASE_URL}/chat/completions",
                    headers=headers,
                    json=payload
                ) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        yield {"type": "error", "data": {"message": f"Kimi API error: {error_text}"}}
                        return
                    
                    full_content = ""
                    tool_calls = []
                    
                    async for line in response.content:
                        line = line.decode('utf-8').strip()
                        if line.startswith('data: '):
                            data = line[6:]
                            if data == '[DONE]':
                                break
                            try:
                                chunk = json.loads(data)
                                delta = chunk.get('choices', [{}])[0].get('delta', {})
                                
                                # Handle content
                                content = delta.get('content', '')
                                if content:
                                    full_content += content
                                    yield {"type": "content", "data": {"chunk": content}}
                                
                                # Handle tool calls
                                if 'tool_calls' in delta:
                                    for tc in delta['tool_calls']:
                                        yield {
                                            "type": "tool_call",
                                            "data": {
                                                "name": tc.get('function', {}).get('name'),
                                                "arguments": tc.get('function', {}).get('arguments')
                                            }
                                        }
                                        tool_calls.append(tc)
                                        
                            except json.JSONDecodeError:
                                continue
                    
                    yield {
                        "type": "execution_complete",
                        "data": {
                            "content": full_content,
                            "tool_calls": tool_calls
                        }
                    }
                    
        except Exception as e:
            logger.error(f"Kimi execution error: {e}")
            yield {"type": "error", "data": {"message": str(e)}}


class ConversationalEngine:
    """
    Main conversational engine that orchestrates human-like responses.
    """
    
    def __init__(self):
        self.generator = HumanLikeResponseGenerator()
        self.conversation_history: Dict[str, List[ConversationTurn]] = {}
    
    async def chat(
        self,
        session_id: str,
        query: str,
        context: Dict = None,
        rag_context: str = None,
        use_tools: bool = False,
        tools: List[Dict] = None
    ) -> AsyncGenerator[Dict, None]:
        """Main chat interface"""
        
        # Get conversation history
        history = self.conversation_history.get(session_id, [])
        
        # Add user message to history
        user_turn = ConversationTurn(role="user", content=query)
        history.append(user_turn)
        
        # Generate response
        if use_tools and tools:
            async for chunk in self.generator.generate_with_kimi_execution(query, tools, context):
                yield chunk
        else:
            async for chunk in self.generator.generate_response(
                query,
                context,
                history,
                rag_context
            ):
                yield chunk
                
                # Capture complete response for history
                if chunk.get("type") == "response_complete":
                    assistant_turn = ConversationTurn(
                        role="assistant",
                        content=chunk["data"].get("full_content", "")
                    )
                    history.append(assistant_turn)
        
        # Update history
        self.conversation_history[session_id] = history[-20:]  # Keep last 20 turns
    
    def clear_history(self, session_id: str):
        """Clear conversation history for a session"""
        if session_id in self.conversation_history:
            del self.conversation_history[session_id]


# Global instance
conversational_engine = ConversationalEngine()


def get_conversational_engine() -> ConversationalEngine:
    """Get the global conversational engine"""
    return conversational_engine
