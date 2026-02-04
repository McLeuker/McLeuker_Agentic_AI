"""
McLeuker AI V7.0 - Reasoning-First Orchestrator
================================================
True reasoning-first approach inspired by Manus AI.

Key Principles:
1. NO PRESET TEMPLATES - Every response is dynamically reasoned
2. REASONING FIRST - AI thinks through each query step by step
3. REAL-TIME STREAMING - Show actual reasoning in the chat
4. CONTEXT-AWARE - Responses adapt to the specific query

The AI reasons through:
1. Understanding what the user is asking
2. Planning how to approach the problem
3. Executing research/analysis steps
4. Synthesizing findings into a coherent response
"""

import asyncio
import json
import os
import re
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any, AsyncGenerator
from dataclasses import dataclass, field
import httpx


@dataclass
class ReasoningStep:
    """A single step in the reasoning process"""
    id: str
    type: str  # thinking, searching, analyzing, writing
    title: str
    content: str
    status: str = "pending"  # pending, active, complete
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "type": self.type,
            "title": self.title,
            "content": self.content,
            "status": self.status,
            "timestamp": self.timestamp
        }


@dataclass 
class ReasoningResponse:
    """Final response after reasoning"""
    success: bool
    content: str = ""
    reasoning_steps: List[ReasoningStep] = field(default_factory=list)
    sources: List[Dict] = field(default_factory=list)
    credits_used: int = 2
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "content": self.content,
            "reasoning_steps": [s.to_dict() for s in self.reasoning_steps],
            "sources": self.sources,
            "credits_used": self.credits_used,
            "error": self.error
        }


class ReasoningOrchestrator:
    """
    Reasoning-First Orchestrator
    
    This orchestrator doesn't use preset templates. Instead, it:
    1. Analyzes the query to understand intent
    2. Plans a reasoning approach
    3. Executes reasoning steps with real-time streaming
    4. Generates a response based on actual reasoning
    """
    
    def __init__(self):
        self.grok_api_key = os.getenv("XAI_API_KEY", "")
        self.grok_base_url = "https://api.x.ai/v1"
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
        
        # Session memory for context continuity
        self.session_memory: Dict[str, List[Dict]] = {}
    
    async def process_with_reasoning(
        self,
        query: str,
        session_id: Optional[str] = None,
        mode: str = "quick"
    ) -> AsyncGenerator[Dict, None]:
        """
        Process a query with real-time reasoning streaming.
        
        Yields events:
        - reasoning_start: Beginning of reasoning
        - thinking: AI thinking/reasoning step
        - searching: Searching for information
        - source: Found a source
        - writing: Writing response
        - content: Response content chunk
        - complete: Final response
        - error: Error occurred
        """
        session_id = session_id or str(uuid.uuid4())
        reasoning_steps: List[ReasoningStep] = []
        
        try:
            # ================================================================
            # STEP 1: Start reasoning process
            # ================================================================
            yield {
                "type": "reasoning_start",
                "data": {
                    "session_id": session_id,
                    "query": query,
                    "mode": mode,
                    "timestamp": datetime.now().isoformat()
                }
            }
            
            # ================================================================
            # STEP 2: Understand the query (AI reasoning)
            # ================================================================
            understanding_step = ReasoningStep(
                id=str(uuid.uuid4())[:8],
                type="thinking",
                title="Understanding your question",
                content="",
                status="active"
            )
            reasoning_steps.append(understanding_step)
            
            yield {
                "type": "thinking",
                "data": {
                    "step_id": understanding_step.id,
                    "title": understanding_step.title,
                    "content": f"Let me understand what you're asking about: \"{query}\"",
                    "status": "active"
                }
            }
            
            # Get AI's understanding of the query
            understanding = await self._reason_about_query(query)
            understanding_step.content = understanding
            understanding_step.status = "complete"
            
            yield {
                "type": "thinking",
                "data": {
                    "step_id": understanding_step.id,
                    "title": understanding_step.title,
                    "content": understanding,
                    "status": "complete"
                }
            }
            
            await asyncio.sleep(0.2)
            
            # ================================================================
            # STEP 3: Plan the approach
            # ================================================================
            planning_step = ReasoningStep(
                id=str(uuid.uuid4())[:8],
                type="thinking",
                title="Planning my approach",
                content="",
                status="active"
            )
            reasoning_steps.append(planning_step)
            
            yield {
                "type": "thinking",
                "data": {
                    "step_id": planning_step.id,
                    "title": planning_step.title,
                    "content": "Determining the best way to answer this...",
                    "status": "active"
                }
            }
            
            plan = await self._plan_approach(query, understanding, mode)
            planning_step.content = plan
            planning_step.status = "complete"
            
            yield {
                "type": "thinking",
                "data": {
                    "step_id": planning_step.id,
                    "title": planning_step.title,
                    "content": plan,
                    "status": "complete"
                }
            }
            
            await asyncio.sleep(0.2)
            
            # ================================================================
            # STEP 4: Research/Search (if needed)
            # ================================================================
            sources = []
            needs_research = await self._needs_research(query, understanding)
            
            if needs_research:
                search_step = ReasoningStep(
                    id=str(uuid.uuid4())[:8],
                    type="searching",
                    title="Researching information",
                    content="",
                    status="active"
                )
                reasoning_steps.append(search_step)
                
                yield {
                    "type": "searching",
                    "data": {
                        "step_id": search_step.id,
                        "title": search_step.title,
                        "content": "Searching for relevant information...",
                        "status": "active"
                    }
                }
                
                # Perform search and stream sources
                async for search_event in self._search_with_streaming(query, mode):
                    if search_event["type"] == "source":
                        sources.append(search_event["data"])
                        yield search_event
                    elif search_event["type"] == "search_progress":
                        yield {
                            "type": "searching",
                            "data": {
                                "step_id": search_step.id,
                                "title": search_step.title,
                                "content": search_event["data"]["message"],
                                "status": "active"
                            }
                        }
                
                search_step.content = f"Found {len(sources)} relevant sources"
                search_step.status = "complete"
                
                yield {
                    "type": "searching",
                    "data": {
                        "step_id": search_step.id,
                        "title": search_step.title,
                        "content": search_step.content,
                        "status": "complete"
                    }
                }
            
            # ================================================================
            # STEP 5: Analyze and synthesize
            # ================================================================
            analysis_step = ReasoningStep(
                id=str(uuid.uuid4())[:8],
                type="thinking",
                title="Analyzing and synthesizing",
                content="",
                status="active"
            )
            reasoning_steps.append(analysis_step)
            
            yield {
                "type": "thinking",
                "data": {
                    "step_id": analysis_step.id,
                    "title": analysis_step.title,
                    "content": "Analyzing the information and forming my response...",
                    "status": "active"
                }
            }
            
            analysis = await self._analyze_and_synthesize(query, understanding, sources)
            analysis_step.content = analysis
            analysis_step.status = "complete"
            
            yield {
                "type": "thinking",
                "data": {
                    "step_id": analysis_step.id,
                    "title": analysis_step.title,
                    "content": analysis,
                    "status": "complete"
                }
            }
            
            await asyncio.sleep(0.2)
            
            # ================================================================
            # STEP 6: Generate response with streaming
            # ================================================================
            writing_step = ReasoningStep(
                id=str(uuid.uuid4())[:8],
                type="writing",
                title="Writing response",
                content="",
                status="active"
            )
            reasoning_steps.append(writing_step)
            
            yield {
                "type": "writing",
                "data": {
                    "step_id": writing_step.id,
                    "title": writing_step.title,
                    "content": "Composing my response...",
                    "status": "active"
                }
            }
            
            # Stream the response content
            full_content = ""
            async for content_chunk in self._generate_response_stream(
                query=query,
                understanding=understanding,
                plan=plan,
                analysis=analysis,
                sources=sources,
                mode=mode
            ):
                full_content += content_chunk
                yield {
                    "type": "content",
                    "data": {
                        "chunk": content_chunk,
                        "full_content": full_content
                    }
                }
            
            writing_step.content = "Response complete"
            writing_step.status = "complete"
            
            yield {
                "type": "writing",
                "data": {
                    "step_id": writing_step.id,
                    "title": writing_step.title,
                    "content": writing_step.content,
                    "status": "complete"
                }
            }
            
            # ================================================================
            # STEP 7: Complete
            # ================================================================
            credits_used = 2 if mode == "quick" else 5
            
            yield {
                "type": "complete",
                "data": {
                    "content": full_content,
                    "reasoning_steps": [s.to_dict() for s in reasoning_steps],
                    "sources": sources,
                    "credits_used": credits_used,
                    "session_id": session_id
                }
            }
            
            # Store in session memory
            if session_id not in self.session_memory:
                self.session_memory[session_id] = []
            self.session_memory[session_id].append({
                "query": query,
                "response": full_content,
                "timestamp": datetime.now().isoformat()
            })
            
        except Exception as e:
            yield {
                "type": "error",
                "data": {
                    "message": str(e),
                    "reasoning_steps": [s.to_dict() for s in reasoning_steps]
                }
            }
    
    # =========================================================================
    # Reasoning Methods - These use LLM to actually reason
    # =========================================================================
    
    async def _reason_about_query(self, query: str) -> str:
        """Use LLM to understand what the user is asking"""
        prompt = f"""Briefly analyze this query in 1-2 sentences. What is the user asking about? What do they want to know?

Query: "{query}"

Your analysis (be concise):"""
        
        return await self._call_llm(prompt, max_tokens=150)
    
    async def _plan_approach(self, query: str, understanding: str, mode: str) -> str:
        """Use LLM to plan how to answer the query"""
        depth = "comprehensive" if mode == "deep" else "focused"
        
        prompt = f"""Based on this query and understanding, briefly describe your approach to answering it in 1-2 sentences.

Query: "{query}"
Understanding: {understanding}
Mode: {depth}

Your approach (be concise):"""
        
        return await self._call_llm(prompt, max_tokens=150)
    
    async def _needs_research(self, query: str, understanding: str) -> bool:
        """Determine if the query needs external research"""
        # Most queries benefit from research for up-to-date information
        research_keywords = [
            "latest", "recent", "current", "trend", "news", "update",
            "2024", "2025", "2026", "today", "now", "market", "industry"
        ]
        query_lower = query.lower()
        return any(kw in query_lower for kw in research_keywords) or len(query.split()) > 5
    
    async def _analyze_and_synthesize(
        self, 
        query: str, 
        understanding: str, 
        sources: List[Dict]
    ) -> str:
        """Analyze sources and synthesize key findings"""
        if not sources:
            return "Using my knowledge to formulate a comprehensive response."
        
        source_summaries = "\n".join([
            f"- {s.get('title', 'Source')}: {s.get('snippet', '')[:100]}..."
            for s in sources[:5]
        ])
        
        prompt = f"""Based on these sources, what are the key points relevant to the query? Summarize in 2-3 sentences.

Query: "{query}"
Sources:
{source_summaries}

Key findings (be concise):"""
        
        return await self._call_llm(prompt, max_tokens=200)
    
    async def _generate_response_stream(
        self,
        query: str,
        understanding: str,
        plan: str,
        analysis: str,
        sources: List[Dict],
        mode: str
    ) -> AsyncGenerator[str, None]:
        """Generate the final response with streaming"""
        
        # Build context from sources
        source_context = ""
        if sources:
            source_context = "\n\nRelevant information from sources:\n" + "\n".join([
                f"- {s.get('title', 'Source')}: {s.get('snippet', '')}"
                for s in sources[:5]
            ])
        
        depth_instruction = "comprehensive and detailed" if mode == "deep" else "focused and concise"
        
        system_prompt = f"""You are McLeuker AI, an expert assistant. Provide a {depth_instruction} response.

Guidelines:
- Write naturally and conversationally
- Be specific and actionable
- Include relevant data and examples when available
- Structure your response clearly with paragraphs
- Do NOT use citation markers like [1] or [2]
- Today's date: {datetime.now().strftime('%B %d, %Y')}"""

        user_prompt = f"""Query: {query}

My understanding: {understanding}
My approach: {plan}
Key findings: {analysis}
{source_context}

Please provide a helpful, well-structured response:"""

        # Stream response from Grok
        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.grok_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.grok_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-3-latest",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 2000 if mode == "deep" else 1000,
                    "stream": True
                }
            )
            
            if response.status_code != 200:
                error_text = response.text
                raise Exception(f"LLM API error: {response.status_code} - {error_text}")
            
            # Parse SSE stream
            async for line in response.aiter_lines():
                if line.startswith("data: "):
                    data = line[6:]
                    if data == "[DONE]":
                        break
                    try:
                        chunk = json.loads(data)
                        if chunk.get("choices") and chunk["choices"][0].get("delta", {}).get("content"):
                            yield chunk["choices"][0]["delta"]["content"]
                    except json.JSONDecodeError:
                        continue
    
    async def _search_with_streaming(
        self, 
        query: str, 
        mode: str
    ) -> AsyncGenerator[Dict, None]:
        """Search for information with streaming updates"""
        max_sources = 10 if mode == "deep" else 5
        sources = []
        
        yield {
            "type": "search_progress",
            "data": {"message": "Initializing search..."}
        }
        
        # Try Perplexity first
        if self.perplexity_api_key:
            yield {
                "type": "search_progress",
                "data": {"message": "Searching knowledge bases..."}
            }
            
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://api.perplexity.ai/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.perplexity_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.1-sonar-small-128k-online",
                            "messages": [
                                {
                                    "role": "system",
                                    "content": "Return relevant sources as JSON array with title, url, snippet fields."
                                },
                                {"role": "user", "content": f"Find sources about: {query}"}
                            ],
                            "max_tokens": 1000
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]
                        
                        # Try to parse sources from response
                        try:
                            json_match = re.search(r'\[[\s\S]*\]', content)
                            if json_match:
                                parsed_sources = json.loads(json_match.group())
                                for s in parsed_sources[:max_sources]:
                                    source = {
                                        "title": s.get("title", "Source"),
                                        "url": s.get("url", ""),
                                        "snippet": s.get("snippet", "")
                                    }
                                    sources.append(source)
                                    yield {
                                        "type": "source",
                                        "data": source
                                    }
                        except:
                            pass
            except Exception as e:
                yield {
                    "type": "search_progress",
                    "data": {"message": f"Search service unavailable, using knowledge base..."}
                }
        
        # Use Grok as fallback for additional context
        if len(sources) < max_sources:
            yield {
                "type": "search_progress",
                "data": {"message": "Gathering additional information..."}
            }
            
            try:
                grok_sources = await self._get_grok_sources(query, max_sources - len(sources))
                for s in grok_sources:
                    sources.append(s)
                    yield {
                        "type": "source",
                        "data": s
                    }
            except:
                pass
        
        yield {
            "type": "search_progress",
            "data": {"message": f"Found {len(sources)} sources"}
        }
    
    async def _get_grok_sources(self, query: str, max_sources: int) -> List[Dict]:
        """Get sources from Grok's knowledge"""
        prompt = f"""For the query "{query}", provide {max_sources} relevant sources as a JSON array.
Each source should have: title, url, snippet (brief description).
Return ONLY the JSON array, no other text.

Example format:
[{{"title": "Source Title", "url": "https://example.com", "snippet": "Brief description"}}]"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.grok_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.grok_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-3-latest",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.3,
                    "max_tokens": 800
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                try:
                    json_match = re.search(r'\[[\s\S]*\]', content)
                    if json_match:
                        return json.loads(json_match.group())
                except:
                    pass
        
        return []
    
    async def _call_llm(self, prompt: str, max_tokens: int = 500) -> str:
        """Make a simple LLM call"""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.grok_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.grok_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-3-latest",
                    "messages": [{"role": "user", "content": prompt}],
                    "temperature": 0.5,
                    "max_tokens": max_tokens
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return data["choices"][0]["message"]["content"]
            else:
                return "Processing..."


# Global instance
reasoning_orchestrator = ReasoningOrchestrator()
