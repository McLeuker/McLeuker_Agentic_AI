"""
McLeuker AI V8.0 - Multi-Layer Agentic Reasoning Orchestrator
==============================================================
True agentic AI approach with multi-layer reasoning like Manus AI.

Key Principles:
1. MULTI-LAYER REASONING - Break tasks into reasoning layers
2. REAL-TIME DATA - Always search for current/future information
3. DYNAMIC SOURCES - Source count based on query needs, not fixed
4. AGENTIC APPROACH - Each layer builds on previous findings
5. EXPANDABLE REASONING - Show detailed reasoning process
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
class ReasoningLayer:
    """A layer in the multi-layer reasoning process"""
    id: str
    layer_num: int
    type: str  # understanding, planning, research, analysis, synthesis, writing
    title: str
    content: str
    sub_steps: List[Dict] = field(default_factory=list)
    status: str = "pending"  # pending, active, complete
    expanded: bool = True
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "layer_num": self.layer_num,
            "type": self.type,
            "title": self.title,
            "content": self.content,
            "sub_steps": self.sub_steps,
            "status": self.status,
            "expanded": self.expanded,
            "timestamp": self.timestamp
        }


@dataclass 
class ReasoningResponse:
    """Final response after multi-layer reasoning"""
    success: bool
    content: str = ""
    reasoning_layers: List[ReasoningLayer] = field(default_factory=list)
    sources: List[Dict] = field(default_factory=list)
    credits_used: int = 2
    error: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "success": self.success,
            "content": self.content,
            "reasoning_layers": [l.to_dict() for l in self.reasoning_layers],
            "sources": self.sources,
            "credits_used": self.credits_used,
            "error": self.error
        }


class ReasoningOrchestrator:
    """
    Multi-Layer Agentic Reasoning Orchestrator
    
    This orchestrator uses multiple reasoning layers:
    Layer 1: Understanding - Deeply understand the query intent
    Layer 2: Planning - Break down into sub-tasks
    Layer 3: Research - Search for CURRENT/FUTURE information
    Layer 4: Analysis - Analyze findings from each sub-task
    Layer 5: Synthesis - Combine insights across layers
    Layer 6: Response - Generate final response
    """
    
    def __init__(self):
        self.grok_api_key = os.getenv("XAI_API_KEY", "")
        self.grok_base_url = "https://api.x.ai/v1"
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
        
        # Session memory for context continuity
        self.session_memory: Dict[str, List[Dict]] = {}
        
        # Current date for real-time context
        self.current_date = datetime.now().strftime("%B %d, %Y")
        self.current_year = datetime.now().year
    
    async def process_with_reasoning(
        self,
        query: str,
        session_id: Optional[str] = None,
        mode: str = "quick"
    ) -> AsyncGenerator[Dict, None]:
        """
        Process a query with multi-layer agentic reasoning.
        
        Yields events for each reasoning layer and sub-step.
        """
        session_id = session_id or str(uuid.uuid4())
        reasoning_layers: List[ReasoningLayer] = []
        all_sources: List[Dict] = []
        
        try:
            # ================================================================
            # LAYER 1: Deep Understanding
            # ================================================================
            layer1 = ReasoningLayer(
                id=str(uuid.uuid4())[:8],
                layer_num=1,
                type="understanding",
                title="Understanding your request",
                content="",
                status="active"
            )
            reasoning_layers.append(layer1)
            
            yield {
                "type": "layer_start",
                "data": {
                    "layer_id": layer1.id,
                    "layer_num": 1,
                    "title": layer1.title,
                    "type": layer1.type
                }
            }
            
            # Sub-step 1.1: Parse intent
            yield {
                "type": "sub_step",
                "data": {
                    "layer_id": layer1.id,
                    "step": "Analyzing query intent...",
                    "status": "active"
                }
            }
            
            intent_analysis = await self._analyze_intent(query)
            layer1.sub_steps.append({"step": "Intent analysis", "result": intent_analysis})
            
            yield {
                "type": "sub_step",
                "data": {
                    "layer_id": layer1.id,
                    "step": intent_analysis,
                    "status": "complete"
                }
            }
            
            # Sub-step 1.2: Identify temporal context
            yield {
                "type": "sub_step",
                "data": {
                    "layer_id": layer1.id,
                    "step": "Determining temporal context...",
                    "status": "active"
                }
            }
            
            temporal_context = await self._analyze_temporal_context(query)
            layer1.sub_steps.append({"step": "Temporal context", "result": temporal_context})
            
            yield {
                "type": "sub_step",
                "data": {
                    "layer_id": layer1.id,
                    "step": temporal_context,
                    "status": "complete"
                }
            }
            
            layer1.content = f"{intent_analysis}\n\nTemporal focus: {temporal_context}"
            layer1.status = "complete"
            
            yield {
                "type": "layer_complete",
                "data": {
                    "layer_id": layer1.id,
                    "content": layer1.content
                }
            }
            
            await asyncio.sleep(0.1)
            
            # ================================================================
            # LAYER 2: Task Planning & Breakdown
            # ================================================================
            layer2 = ReasoningLayer(
                id=str(uuid.uuid4())[:8],
                layer_num=2,
                type="planning",
                title="Breaking down the task",
                content="",
                status="active"
            )
            reasoning_layers.append(layer2)
            
            yield {
                "type": "layer_start",
                "data": {
                    "layer_id": layer2.id,
                    "layer_num": 2,
                    "title": layer2.title,
                    "type": layer2.type
                }
            }
            
            # Get sub-tasks from LLM
            sub_tasks = await self._break_into_subtasks(query, intent_analysis, mode)
            
            for i, task in enumerate(sub_tasks):
                yield {
                    "type": "sub_step",
                    "data": {
                        "layer_id": layer2.id,
                        "step": f"Sub-task {i+1}: {task}",
                        "status": "complete"
                    }
                }
                layer2.sub_steps.append({"step": f"Sub-task {i+1}", "result": task})
            
            layer2.content = f"Identified {len(sub_tasks)} sub-tasks to address"
            layer2.status = "complete"
            
            yield {
                "type": "layer_complete",
                "data": {
                    "layer_id": layer2.id,
                    "content": layer2.content
                }
            }
            
            await asyncio.sleep(0.1)
            
            # ================================================================
            # LAYER 3: Real-Time Research
            # ================================================================
            layer3 = ReasoningLayer(
                id=str(uuid.uuid4())[:8],
                layer_num=3,
                type="research",
                title="Researching current information",
                content="",
                status="active"
            )
            reasoning_layers.append(layer3)
            
            yield {
                "type": "layer_start",
                "data": {
                    "layer_id": layer3.id,
                    "layer_num": 3,
                    "title": layer3.title,
                    "type": layer3.type
                }
            }
            
            # Research each sub-task with REAL-TIME focus
            for i, task in enumerate(sub_tasks[:3]):  # Limit to 3 for speed
                yield {
                    "type": "sub_step",
                    "data": {
                        "layer_id": layer3.id,
                        "step": f"Searching for: {task}...",
                        "status": "active"
                    }
                }
                
                # Search with real-time focus
                task_sources = await self._search_realtime(task, temporal_context)
                all_sources.extend(task_sources)
                
                yield {
                    "type": "sub_step",
                    "data": {
                        "layer_id": layer3.id,
                        "step": f"Found {len(task_sources)} sources for: {task}",
                        "status": "complete"
                    }
                }
                layer3.sub_steps.append({
                    "step": f"Research: {task}",
                    "result": f"Found {len(task_sources)} sources"
                })
            
            # Emit sources
            for source in all_sources:
                yield {
                    "type": "source",
                    "data": source
                }
            
            layer3.content = f"Gathered {len(all_sources)} relevant sources with current data"
            layer3.status = "complete"
            
            yield {
                "type": "layer_complete",
                "data": {
                    "layer_id": layer3.id,
                    "content": layer3.content,
                    "source_count": len(all_sources)
                }
            }
            
            await asyncio.sleep(0.1)
            
            # ================================================================
            # LAYER 4: Deep Analysis
            # ================================================================
            layer4 = ReasoningLayer(
                id=str(uuid.uuid4())[:8],
                layer_num=4,
                type="analysis",
                title="Analyzing findings",
                content="",
                status="active"
            )
            reasoning_layers.append(layer4)
            
            yield {
                "type": "layer_start",
                "data": {
                    "layer_id": layer4.id,
                    "layer_num": 4,
                    "title": layer4.title,
                    "type": layer4.type
                }
            }
            
            # Analyze each sub-task's findings
            analyses = []
            for i, task in enumerate(sub_tasks[:3]):
                yield {
                    "type": "sub_step",
                    "data": {
                        "layer_id": layer4.id,
                        "step": f"Analyzing: {task}...",
                        "status": "active"
                    }
                }
                
                task_analysis = await self._analyze_subtask(task, all_sources, temporal_context)
                analyses.append(task_analysis)
                
                yield {
                    "type": "sub_step",
                    "data": {
                        "layer_id": layer4.id,
                        "step": task_analysis[:200] + "..." if len(task_analysis) > 200 else task_analysis,
                        "status": "complete"
                    }
                }
                layer4.sub_steps.append({"step": f"Analysis: {task}", "result": task_analysis})
            
            layer4.content = "Completed analysis of all sub-tasks"
            layer4.status = "complete"
            
            yield {
                "type": "layer_complete",
                "data": {
                    "layer_id": layer4.id,
                    "content": layer4.content
                }
            }
            
            await asyncio.sleep(0.1)
            
            # ================================================================
            # LAYER 5: Synthesis
            # ================================================================
            layer5 = ReasoningLayer(
                id=str(uuid.uuid4())[:8],
                layer_num=5,
                type="synthesis",
                title="Synthesizing insights",
                content="",
                status="active"
            )
            reasoning_layers.append(layer5)
            
            yield {
                "type": "layer_start",
                "data": {
                    "layer_id": layer5.id,
                    "layer_num": 5,
                    "title": layer5.title,
                    "type": layer5.type
                }
            }
            
            yield {
                "type": "sub_step",
                "data": {
                    "layer_id": layer5.id,
                    "step": "Combining insights from all analyses...",
                    "status": "active"
                }
            }
            
            synthesis = await self._synthesize_findings(query, analyses, all_sources, temporal_context)
            
            yield {
                "type": "sub_step",
                "data": {
                    "layer_id": layer5.id,
                    "step": synthesis[:300] + "..." if len(synthesis) > 300 else synthesis,
                    "status": "complete"
                }
            }
            
            layer5.content = synthesis
            layer5.status = "complete"
            
            yield {
                "type": "layer_complete",
                "data": {
                    "layer_id": layer5.id,
                    "content": layer5.content
                }
            }
            
            await asyncio.sleep(0.1)
            
            # ================================================================
            # LAYER 6: Response Generation
            # ================================================================
            layer6 = ReasoningLayer(
                id=str(uuid.uuid4())[:8],
                layer_num=6,
                type="writing",
                title="Generating response",
                content="",
                status="active"
            )
            reasoning_layers.append(layer6)
            
            yield {
                "type": "layer_start",
                "data": {
                    "layer_id": layer6.id,
                    "layer_num": 6,
                    "title": layer6.title,
                    "type": layer6.type
                }
            }
            
            yield {
                "type": "sub_step",
                "data": {
                    "layer_id": layer6.id,
                    "step": "Composing final response...",
                    "status": "active"
                }
            }
            
            # Stream the final response
            full_content = ""
            async for chunk in self._generate_response_stream(
                query, intent_analysis, sub_tasks, analyses, synthesis, all_sources, mode, temporal_context
            ):
                full_content += chunk
                yield {
                    "type": "content",
                    "data": {"chunk": chunk}
                }
            
            layer6.content = "Response complete"
            layer6.status = "complete"
            
            yield {
                "type": "sub_step",
                "data": {
                    "layer_id": layer6.id,
                    "step": "Response complete",
                    "status": "complete"
                }
            }
            
            yield {
                "type": "layer_complete",
                "data": {
                    "layer_id": layer6.id,
                    "content": layer6.content
                }
            }
            
            # ================================================================
            # GENERATE FOLLOW-UP QUESTIONS
            # ================================================================
            follow_up_questions = await self._generate_follow_up_questions(query, full_content, sub_tasks)
            
            yield {
                "type": "follow_up",
                "data": {
                    "questions": follow_up_questions
                }
            }
            
            # ================================================================
            # COMPLETE
            # ================================================================
            credits_used = 2 if mode == "quick" else 5
            
            yield {
                "type": "complete",
                "data": {
                    "content": full_content,
                    "reasoning_layers": [l.to_dict() for l in reasoning_layers],
                    "sources": all_sources,
                    "follow_up_questions": follow_up_questions,
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
                    "reasoning_layers": [l.to_dict() for l in reasoning_layers]
                }
            }
    
    # =========================================================================
    # Layer 1: Understanding Methods
    # =========================================================================
    
    async def _analyze_intent(self, query: str) -> str:
        """Deeply analyze the query intent"""
        prompt = f"""Analyze this query in 2-3 sentences. What exactly is the user asking? What do they want to learn or achieve?

Query: "{query}"

Your analysis:"""
        
        return await self._call_llm(prompt, max_tokens=200)
    
    async def _analyze_temporal_context(self, query: str) -> str:
        """Determine the temporal focus of the query"""
        prompt = f"""For this query, determine the temporal focus. Is the user asking about:
- Current/present state (what's happening NOW in {self.current_year})
- Future trends/predictions (what's COMING)
- Historical context (what happened before)
- Timeless information

Query: "{query}"
Today's date: {self.current_date}

Answer in one sentence specifying the temporal focus:"""
        
        result = await self._call_llm(prompt, max_tokens=100)
        
        # Default to current if unclear
        if "current" in result.lower() or "now" in result.lower() or "present" in result.lower():
            return f"Focus on current state ({self.current_year}) and emerging developments"
        elif "future" in result.lower() or "coming" in result.lower() or "predict" in result.lower():
            return f"Focus on future trends and predictions for {self.current_year} and beyond"
        else:
            return f"Focus on current state ({self.current_year}) with relevant context"
    
    # =========================================================================
    # Layer 2: Planning Methods
    # =========================================================================
    
    async def _break_into_subtasks(self, query: str, intent: str, mode: str) -> List[str]:
        """Break the query into actionable sub-tasks"""
        num_tasks = 4 if mode == "deep" else 3
        
        prompt = f"""Break this query into {num_tasks} specific research sub-tasks. Each sub-task should be a focused question or area to investigate.

Query: "{query}"
Intent: {intent}
Today: {self.current_date}

Return ONLY a JSON array of {num_tasks} sub-task strings, focusing on CURRENT and FUTURE information:
Example: ["What are the current X in {self.current_year}?", "What emerging trends are shaping X?", "What predictions exist for X?"]"""
        
        result = await self._call_llm(prompt, max_tokens=400)
        
        try:
            json_match = re.search(r'\[[\s\S]*\]', result)
            if json_match:
                tasks = json.loads(json_match.group())
                return tasks[:num_tasks]
        except:
            pass
        
        # Fallback sub-tasks
        return [
            f"What is the current state of this topic in {self.current_year}?",
            "What emerging trends are developing?",
            "What are experts predicting for the near future?"
        ]
    
    # =========================================================================
    # Layer 3: Research Methods - REAL-TIME FOCUS
    # =========================================================================
    
    async def _search_realtime(self, task: str, temporal_context: str) -> List[Dict]:
        """Search for REAL-TIME information using Perplexity"""
        sources = []
        
        # Enhance query with strong temporal context - focus on 2025/2026
        current_month = datetime.now().strftime("%B")
        enhanced_query = f"{task} {current_month} {self.current_year} latest news updates"
        
        if self.perplexity_api_key:
            try:
                async with httpx.AsyncClient(timeout=30.0) as client:
                    response = await client.post(
                        "https://api.perplexity.ai/chat/completions",
                        headers={
                            "Authorization": f"Bearer {self.perplexity_api_key}",
                            "Content-Type": "application/json"
                        },
                        json={
                            "model": "llama-3.1-sonar-large-128k-online",  # Use larger model for better results
                            "messages": [
                                {
                                    "role": "system",
                                    "content": f"""You are a research assistant. Find the most CURRENT and RECENT information about the topic.
Today's date is {self.current_date}. Focus on information from {self.current_year} or very recent sources.
Return sources as a JSON array with: title, url, snippet (include dates/years when available)."""
                                },
                                {"role": "user", "content": enhanced_query}
                            ],
                            "max_tokens": 1500,
                            "temperature": 0.2,
                            "search_recency_filter": "week"  # Focus on very recent results
                        }
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        content = data["choices"][0]["message"]["content"]
                        
                        # Parse sources
                        try:
                            json_match = re.search(r'\[[\s\S]*\]', content)
                            if json_match:
                                parsed = json.loads(json_match.group())
                                for s in parsed:
                                    sources.append({
                                        "title": s.get("title", "Source"),
                                        "url": s.get("url", ""),
                                        "snippet": s.get("snippet", "")
                                    })
                        except:
                            # Extract info from text response
                            sources.append({
                                "title": f"Research on: {task}",
                                "url": "",
                                "snippet": content[:200] if content else ""
                            })
            except Exception as e:
                pass
        
        # Fallback to Grok for additional context
        if len(sources) < 2:
            grok_sources = await self._get_grok_realtime_sources(task)
            sources.extend(grok_sources)
        
        return sources[:4]  # Dynamic limit based on what we find
    
    async def _get_grok_realtime_sources(self, query: str) -> List[Dict]:
        """Get current sources from Grok"""
        prompt = f"""For the topic "{query}", provide 2-3 relevant and CURRENT sources (from {self.current_year} or very recent).
Return as JSON array with: title, url, snippet. Include year/date in snippets when possible.
Focus on what's happening NOW, not historical information.

Return ONLY the JSON array:"""

        async with httpx.AsyncClient(timeout=30.0) as client:
            try:
                response = await client.post(
                    f"{self.grok_base_url}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {self.grok_api_key}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "model": "grok-4-fast-non-reasoning",
                        "messages": [{"role": "user", "content": prompt}],
                        "temperature": 0.3,
                        "max_tokens": 600
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"]
                    
                    json_match = re.search(r'\[[\s\S]*\]', content)
                    if json_match:
                        return json.loads(json_match.group())
            except:
                pass
        
        return []
    
    # =========================================================================
    # Layer 4: Analysis Methods
    # =========================================================================
    
    async def _analyze_subtask(self, task: str, sources: List[Dict], temporal_context: str) -> str:
        """Analyze findings for a specific sub-task"""
        source_info = "\n".join([
            f"- {s.get('title', 'Source')}: {s.get('snippet', '')[:150]}"
            for s in sources[:3]
        ])
        
        prompt = f"""Based on these sources, analyze the current state of: "{task}"

Sources:
{source_info}

Temporal focus: {temporal_context}
Today: {self.current_date}

Provide a 2-3 sentence analysis focusing on CURRENT developments and what's happening NOW:"""
        
        return await self._call_llm(prompt, max_tokens=250)
    
    # =========================================================================
    # Layer 5: Synthesis Methods
    # =========================================================================
    
    async def _synthesize_findings(
        self, 
        query: str, 
        analyses: List[str], 
        sources: List[Dict],
        temporal_context: str
    ) -> str:
        """Synthesize all analyses into coherent insights"""
        analyses_text = "\n".join([f"- {a}" for a in analyses])
        
        prompt = f"""Synthesize these analyses into 3-4 key insights about: "{query}"

Analyses:
{analyses_text}

Temporal focus: {temporal_context}
Today: {self.current_date}

Provide a synthesis focusing on what's CURRENT and what's EMERGING (not historical):"""
        
        return await self._call_llm(prompt, max_tokens=400)
    
    # =========================================================================
    # Layer 6: Response Generation
    # =========================================================================
    
    async def _generate_response_stream(
        self,
        query: str,
        intent: str,
        sub_tasks: List[str],
        analyses: List[str],
        synthesis: str,
        sources: List[Dict],
        mode: str,
        temporal_context: str
    ) -> AsyncGenerator[str, None]:
        """Generate the final response with streaming"""
        
        source_context = "\n".join([
            f"- {s.get('title', 'Source')}: {s.get('snippet', '')}"
            for s in sources[:5]
        ])
        
        analyses_context = "\n".join([f"- {a}" for a in analyses])
        
        depth = "comprehensive and detailed" if mode == "deep" else "focused and insightful"
        
        system_prompt = f"""You are McLeuker AI, an expert fashion and industry analyst. 
Provide a {depth} response based on CURRENT information.

CRITICAL FORMATTING RULES:
1. Use STRUCTURED formatting with clear sections and headers (use ## for main sections)
2. Use bullet points (•) for lists of items, trends, or key points
3. Use relevant emojis sparingly to highlight key concepts (🔥 for hot trends, 📈 for growth, 🌱 for sustainability, 💡 for insights, ⚡ for innovation, 🎯 for key points)
4. Keep paragraphs SHORT (2-3 sentences max)
5. Use **bold** for important terms and concepts
6. Include numbered lists when showing steps or rankings

CONTENT RULES:
1. Focus on what's happening NOW in {self.current_year} and what's EMERGING
2. Do NOT reference old data (2023 or earlier) unless providing historical context
3. Use phrases like "currently", "as of {self.current_year}", "emerging now", "looking ahead"
4. Be specific with current examples and recent developments
5. Do NOT use citation markers like [1] or [2]

STRUCTURE YOUR RESPONSE AS:
## 🎯 Current State (What's Happening Now)
[Brief overview with bullet points]

## 🔥 Key Trends & Developments
[Bullet points with specific examples]

## 📈 Future Outlook
[What's emerging and predictions]

## 💡 Key Takeaways
[3-5 bullet point summary]

Today's date: {self.current_date}"""

        user_prompt = f"""Query: {query}

My understanding: {intent}
Temporal focus: {temporal_context}

Key analyses:
{analyses_context}

Synthesis:
{synthesis}

Source information:
{source_context}

Please provide a helpful, CURRENT-focused response. Start with what's happening NOW, then discuss emerging trends and future outlook:"""

        async with httpx.AsyncClient(timeout=60.0) as client:
            response = await client.post(
                f"{self.grok_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.grok_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-4-fast-non-reasoning",
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": user_prompt}
                    ],
                    "temperature": 0.7,
                    "max_tokens": 1500 if mode == "deep" else 800,
                    "stream": True
                }
            )
            
            if response.status_code == 200:
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            if "choices" in data and len(data["choices"]) > 0:
                                delta = data["choices"][0].get("delta", {})
                                if "content" in delta:
                                    yield delta["content"]
                        except:
                            continue
            else:
                yield "I apologize, but I encountered an issue generating the response. Please try again."
    
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
                    "model": "grok-4-fast-non-reasoning",
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
    
    async def _generate_follow_up_questions(self, query: str, response: str, sub_tasks: List[str]) -> List[str]:
        """Generate 3-5 follow-up questions based on the query and response"""
        prompt = f"""Based on this conversation, generate 3-5 follow-up questions the user might want to ask next.

Original query: "{query}"

Response summary: {response[:500]}...

Sub-tasks explored: {', '.join(sub_tasks[:3])}

Generate follow-up questions that:
1. Dive deeper into specific aspects mentioned
2. Explore related topics
3. Ask for practical applications or examples
4. Request comparisons or analysis
5. Explore future implications

Return ONLY a JSON array of 3-5 question strings, no other text:
Example: ["How can I apply this to my business?", "What are the risks involved?", "Can you compare X with Y?"]"""
        
        result = await self._call_llm(prompt, max_tokens=300)
        
        try:
            json_match = re.search(r'\[[\s\S]*\]', result)
            if json_match:
                questions = json.loads(json_match.group())
                return questions[:5]  # Limit to 5 questions
        except:
            pass
        
        # Fallback questions
        return [
            f"Can you dive deeper into any specific aspect of {query.split()[-2] if len(query.split()) > 2 else 'this topic'}?",
            "What are the practical applications of this information?",
            "How does this compare to other approaches?",
            "What are the potential risks or challenges?",
            "What should I focus on next?"
        ]


# Global instance
reasoning_orchestrator = ReasoningOrchestrator()
