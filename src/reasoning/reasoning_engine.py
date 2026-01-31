"""
McLeuker Agentic AI Platform - Reasoning Engine

Advanced reasoning system with chain-of-thought, similar to Manus AI.
Provides visible reasoning steps and structured thinking.
"""

import json
import re
from typing import Optional, List, Dict, Any, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ReasoningType(str, Enum):
    """Types of reasoning approaches."""
    DIRECT = "direct"  # Simple, direct answer
    ANALYTICAL = "analytical"  # Break down and analyze
    COMPARATIVE = "comparative"  # Compare options
    CREATIVE = "creative"  # Generate ideas
    RESEARCH = "research"  # Requires external information
    STEP_BY_STEP = "step_by_step"  # Multi-step process
    SYNTHESIS = "synthesis"  # Combine multiple sources


@dataclass
class ReasoningStep:
    """A single step in the reasoning process."""
    step_number: int
    title: str
    content: str
    reasoning_type: ReasoningType
    confidence: float = 1.0
    sources: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "step": self.step_number,
            "title": self.title,
            "content": self.content,
            "type": self.reasoning_type.value,
            "confidence": self.confidence,
            "sources": self.sources
        }
    
    def to_display(self) -> str:
        """Format for display to user."""
        emoji_map = {
            ReasoningType.DIRECT: "💡",
            ReasoningType.ANALYTICAL: "🔍",
            ReasoningType.COMPARATIVE: "⚖️",
            ReasoningType.CREATIVE: "✨",
            ReasoningType.RESEARCH: "📚",
            ReasoningType.STEP_BY_STEP: "📋",
            ReasoningType.SYNTHESIS: "🔗"
        }
        emoji = emoji_map.get(self.reasoning_type, "•")
        return f"{emoji} **{self.title}**\n{self.content}"


@dataclass
class ReasoningChain:
    """Complete chain of reasoning for a query."""
    query: str
    steps: List[ReasoningStep] = field(default_factory=list)
    conclusion: Optional[str] = None
    requires_search: bool = False
    requires_file_generation: bool = False
    output_format: Optional[str] = None
    confidence: float = 1.0
    timestamp: datetime = field(default_factory=datetime.utcnow)
    
    def add_step(
        self,
        title: str,
        content: str,
        reasoning_type: ReasoningType = ReasoningType.ANALYTICAL,
        confidence: float = 1.0,
        sources: List[str] = None
    ) -> ReasoningStep:
        """Add a reasoning step."""
        step = ReasoningStep(
            step_number=len(self.steps) + 1,
            title=title,
            content=content,
            reasoning_type=reasoning_type,
            confidence=confidence,
            sources=sources or []
        )
        self.steps.append(step)
        return step
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "query": self.query,
            "steps": [s.to_dict() for s in self.steps],
            "conclusion": self.conclusion,
            "requires_search": self.requires_search,
            "requires_file_generation": self.requires_file_generation,
            "output_format": self.output_format,
            "confidence": self.confidence,
            "timestamp": self.timestamp.isoformat()
        }
    
    def to_display(self) -> str:
        """Format the reasoning chain for display."""
        parts = ["🧠 **Reasoning Process**\n"]
        
        for step in self.steps:
            parts.append(step.to_display())
            parts.append("")
        
        if self.conclusion:
            parts.append(f"✅ **Conclusion**: {self.conclusion}")
        
        return "\n".join(parts)


class ReasoningEngine:
    """
    Advanced reasoning engine with chain-of-thought capabilities.
    
    Analyzes queries, determines the best approach, and generates
    structured reasoning that can be displayed to users.
    """
    
    def __init__(self, llm_provider=None):
        self.llm = llm_provider
    
    async def analyze_query(
        self,
        query: str,
        context: Optional[Dict[str, Any]] = None
    ) -> ReasoningChain:
        """
        Analyze a query and create a reasoning chain.
        
        Args:
            query: The user's query
            context: Optional conversation context
            
        Returns:
            ReasoningChain with analysis and approach
        """
        chain = ReasoningChain(query=query)
        
        # Step 1: Understand the query
        query_analysis = self._analyze_query_type(query)
        chain.add_step(
            title="Understanding the Request",
            content=query_analysis["understanding"],
            reasoning_type=ReasoningType.ANALYTICAL
        )
        
        # Step 2: Determine if search is needed
        needs_search = self._needs_real_time_info(query)
        chain.requires_search = needs_search
        
        if needs_search:
            chain.add_step(
                title="Information Requirements",
                content="This query requires real-time information from the web. I'll search for current data to provide accurate answers.",
                reasoning_type=ReasoningType.RESEARCH
            )
        
        # Step 3: Determine if file generation is needed
        file_analysis = self._analyze_file_requirements(query)
        chain.requires_file_generation = file_analysis["needs_file"]
        chain.output_format = file_analysis.get("format")
        
        if file_analysis["needs_file"]:
            chain.add_step(
                title="Output Planning",
                content=f"This request requires generating a {file_analysis['format']} file. I'll structure the data appropriately.",
                reasoning_type=ReasoningType.STEP_BY_STEP
            )
        
        # Step 4: Plan the approach
        approach = self._plan_approach(query_analysis, needs_search, file_analysis)
        chain.add_step(
            title="Approach",
            content=approach,
            reasoning_type=ReasoningType.STEP_BY_STEP
        )
        
        return chain
    
    async def reason_with_llm(
        self,
        query: str,
        context: Optional[str] = None,
        search_results: Optional[str] = None
    ) -> ReasoningChain:
        """
        Use LLM for deep reasoning about a query.
        
        Args:
            query: The user's query
            context: Conversation context
            search_results: Results from web search
            
        Returns:
            ReasoningChain with LLM-powered analysis
        """
        if not self.llm:
            return await self.analyze_query(query)
        
        chain = ReasoningChain(query=query)
        
        # Build the reasoning prompt
        system_prompt = """You are an advanced reasoning AI assistant. Analyze the user's query and provide structured reasoning.

Your response should include:
1. Understanding what the user wants
2. Breaking down the problem
3. Identifying what information is needed
4. Planning how to answer
5. Any assumptions you're making

Format your response as a structured analysis with clear sections."""

        user_prompt = f"Query: {query}"
        
        if context:
            user_prompt = f"Context:\n{context}\n\n{user_prompt}"
        
        if search_results:
            user_prompt += f"\n\nSearch Results:\n{search_results}"
        
        try:
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ]
            
            response = await self.llm.complete(
                messages=messages,
                temperature=0.3,
                max_tokens=1000
            )
            
            content = response.get("content", "")
            
            # Parse the LLM response into reasoning steps
            steps = self._parse_reasoning_response(content)
            for step_title, step_content in steps:
                chain.add_step(
                    title=step_title,
                    content=step_content,
                    reasoning_type=self._classify_step_type(step_content)
                )
            
        except Exception as e:
            chain.add_step(
                title="Analysis",
                content=f"Analyzing the query: {query}",
                reasoning_type=ReasoningType.ANALYTICAL
            )
        
        return chain
    
    def _analyze_query_type(self, query: str) -> Dict[str, Any]:
        """Analyze the type and intent of a query."""
        query_lower = query.lower()
        
        # Determine query type
        query_type = "general"
        understanding = ""
        
        if any(w in query_lower for w in ["what is", "what are", "explain", "define"]):
            query_type = "definition"
            understanding = "The user is asking for an explanation or definition."
        
        elif any(w in query_lower for w in ["how to", "how do", "how can"]):
            query_type = "how_to"
            understanding = "The user wants to learn how to do something."
        
        elif any(w in query_lower for w in ["best", "top", "recommend", "suggest"]):
            query_type = "recommendation"
            understanding = "The user is looking for recommendations or suggestions."
        
        elif any(w in query_lower for w in ["compare", "difference", "vs", "versus"]):
            query_type = "comparison"
            understanding = "The user wants to compare different options."
        
        elif any(w in query_lower for w in ["list", "give me", "show me", "find"]):
            query_type = "list"
            understanding = "The user wants a list of items or information."
        
        elif any(w in query_lower for w in ["create", "make", "generate", "build", "write"]):
            query_type = "creation"
            understanding = "The user wants to create or generate something."
        
        elif any(w in query_lower for w in ["why", "reason", "cause"]):
            query_type = "explanation"
            understanding = "The user wants to understand the reasons behind something."
        
        elif "?" in query:
            query_type = "question"
            understanding = "The user is asking a question that needs answering."
        
        else:
            understanding = "The user has made a general request or statement."
        
        return {
            "type": query_type,
            "understanding": understanding
        }
    
    def _needs_real_time_info(self, query: str) -> bool:
        """Determine if the query needs real-time information."""
        query_lower = query.lower()
        
        # Time-sensitive keywords
        time_keywords = [
            "today", "now", "current", "latest", "recent", "this week",
            "this month", "2024", "2025", "2026", "happening", "right now",
            "trending", "news", "update", "live", "real-time"
        ]
        
        # Search-indicating keywords
        search_keywords = [
            "find", "search", "look up", "what's happening",
            "where can i", "where is", "show me", "give me"
        ]
        
        # Event keywords
        event_keywords = [
            "fashion week", "event", "conference", "show", "exhibition",
            "sale", "opening", "launch"
        ]
        
        if any(kw in query_lower for kw in time_keywords):
            return True
        
        if any(kw in query_lower for kw in search_keywords):
            return True
        
        if any(kw in query_lower for kw in event_keywords):
            return True
        
        return False
    
    def _analyze_file_requirements(self, query: str) -> Dict[str, Any]:
        """Analyze if the query requires file generation."""
        query_lower = query.lower()
        
        # File type keywords
        file_keywords = {
            "excel": ["excel", "spreadsheet", "xlsx", "xls", "table", "data sheet"],
            "pdf": ["pdf", "document", "report"],
            "word": ["word", "doc", "docx", "document"],
            "ppt": ["powerpoint", "ppt", "pptx", "presentation", "slides"],
            "csv": ["csv", "comma separated"]
        }
        
        for format_type, keywords in file_keywords.items():
            if any(kw in query_lower for kw in keywords):
                return {"needs_file": True, "format": format_type}
        
        # Check for implicit file requests
        if any(w in query_lower for w in ["create", "generate", "make", "build", "export"]):
            if any(w in query_lower for w in ["list", "table", "data", "report"]):
                return {"needs_file": True, "format": "excel"}
        
        return {"needs_file": False, "format": None}
    
    def _plan_approach(
        self,
        query_analysis: Dict[str, Any],
        needs_search: bool,
        file_analysis: Dict[str, Any]
    ) -> str:
        """Plan the approach to answer the query."""
        steps = []
        
        query_type = query_analysis["type"]
        
        if needs_search:
            steps.append("1. Search for current information from reliable sources")
            steps.append("2. Analyze and verify the search results")
        
        if query_type == "recommendation":
            steps.append("3. Evaluate options based on quality and relevance")
            steps.append("4. Rank and present the best recommendations")
        
        elif query_type == "comparison":
            steps.append("3. Identify key comparison criteria")
            steps.append("4. Analyze each option against the criteria")
            steps.append("5. Present a balanced comparison")
        
        elif query_type == "list":
            steps.append("3. Compile comprehensive list of items")
            steps.append("4. Organize and categorize the information")
        
        elif query_type == "creation":
            steps.append("3. Structure the content appropriately")
            steps.append("4. Generate the requested output")
        
        else:
            steps.append("3. Synthesize information into a clear answer")
        
        if file_analysis["needs_file"]:
            steps.append(f"5. Format and generate {file_analysis['format']} file")
        
        return "\n".join(steps) if steps else "Provide a direct, helpful response."
    
    def _parse_reasoning_response(self, content: str) -> List[Tuple[str, str]]:
        """Parse LLM response into reasoning steps."""
        steps = []
        
        # Try to find numbered sections
        section_pattern = r'(?:^|\n)(\d+[\.\)]\s*)?([A-Z][^:\n]+):\s*([^\n]+(?:\n(?!\d+[\.\)])[^\n]+)*)'
        matches = re.findall(section_pattern, content, re.MULTILINE)
        
        if matches:
            for _, title, content in matches:
                if title.strip() and content.strip():
                    steps.append((title.strip(), content.strip()))
        
        # If no structured sections found, create a single step
        if not steps:
            steps.append(("Analysis", content.strip()))
        
        return steps
    
    def _classify_step_type(self, content: str) -> ReasoningType:
        """Classify the type of a reasoning step."""
        content_lower = content.lower()
        
        if any(w in content_lower for w in ["search", "find", "look up", "research"]):
            return ReasoningType.RESEARCH
        
        if any(w in content_lower for w in ["compare", "versus", "difference"]):
            return ReasoningType.COMPARATIVE
        
        if any(w in content_lower for w in ["create", "generate", "build"]):
            return ReasoningType.CREATIVE
        
        if any(w in content_lower for w in ["step", "first", "then", "next", "finally"]):
            return ReasoningType.STEP_BY_STEP
        
        if any(w in content_lower for w in ["combine", "synthesize", "together"]):
            return ReasoningType.SYNTHESIS
        
        return ReasoningType.ANALYTICAL
