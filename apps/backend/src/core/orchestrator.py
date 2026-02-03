"""
McLeuker AI V5.1 - Core Orchestrator with Response Contract
============================================================
Enforces structured output format for consistent frontend rendering.

Design Principles:
1. STRUCTURED output - always return ResponseContract format
2. CLEAN separation - content vs sources vs files
3. NO inline citations in prose - sources are separate objects
4. GUARANTEED format - frontend can rely on response structure
"""

import asyncio
import json
import os
import re
import uuid
from datetime import datetime
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field, asdict
import httpx

# Use absolute imports instead of relative
from src.schemas.response_contract import (
    ResponseContract, Source, GeneratedFile, TableData, KeyInsight,
    LayoutSection, IntentType, DomainType
)
from src.layers.intent.intent_router import intent_router, IntentResult
from src.services.file_generator import file_generator


@dataclass
class OrchestratorResponse:
    """Response from the orchestrator - follows ResponseContract"""
    success: bool
    response: Optional[ResponseContract] = None
    error: Optional[str] = None
    reasoning_steps: List[str] = field(default_factory=list)
    credits_used: int = 0
    session_id: str = ""
    
    def to_dict(self) -> dict:
        result = {
            "success": self.success,
            "error": self.error,
            "reasoning_steps": self.reasoning_steps,
            "credits_used": self.credits_used,
            "session_id": self.session_id
        }
        if self.response:
            result["response"] = self.response.to_dict()
        return result


class V5Orchestrator:
    """
    V5.1 Orchestrator with Response Contract enforcement.
    
    Key improvements over V5.0:
    - Structured output format (ResponseContract)
    - Clean source management (no inline citations)
    - File generation pipeline
    - Intent-aware processing
    """
    
    def __init__(self):
        self.grok_api_key = os.getenv("XAI_API_KEY", "")
        self.grok_base_url = "https://api.x.ai/v1"
        self.perplexity_api_key = os.getenv("PERPLEXITY_API_KEY", "")
        self.session_contexts: Dict[str, List[Dict]] = {}
        
    async def process(
        self,
        query: str,
        session_id: Optional[str] = None,
        mode: str = "auto",
        domain_filter: Optional[str] = None
    ) -> OrchestratorResponse:
        """
        Process a user query and return structured response.
        """
        reasoning_steps = []
        
        try:
            # Generate session ID if not provided
            if not session_id:
                session_id = str(uuid.uuid4())
            
            # Step 1: Intent Classification
            reasoning_steps.append("Analyzing query intent...")
            intent_result = intent_router.classify(query)
            reasoning_steps.append(f"Intent: {intent_result.intent_type.value}, Domain: {intent_result.domain.value}")
            
            # Override search mode if specified
            search_mode = mode if mode != "auto" else intent_result.search_mode
            
            # Step 2: Search for information
            reasoning_steps.append(f"Searching ({search_mode} mode)...")
            search_results = await self._search(query, search_mode, intent_result.domain)
            reasoning_steps.append(f"Found {len(search_results)} sources")
            
            # Step 3: Generate response with Grok
            reasoning_steps.append("Generating response...")
            response_contract = await self._generate_response(
                query=query,
                search_results=search_results,
                intent_result=intent_result,
                session_id=session_id
            )
            reasoning_steps.append("Response generated successfully")
            
            # Step 4: Generate files if needed
            if intent_result.intent_type == IntentType.DATA:
                reasoning_steps.append("Generating data files...")
                files = await self._generate_files(query, response_contract)
                response_contract.files = files
            
            # Calculate credits
            credits_used = 2 if search_mode == "quick" else 5
            
            return OrchestratorResponse(
                success=True,
                response=response_contract,
                reasoning_steps=reasoning_steps,
                credits_used=credits_used,
                session_id=session_id
            )
            
        except Exception as e:
            reasoning_steps.append(f"Error: {str(e)}")
            return OrchestratorResponse(
                success=False,
                error=str(e),
                reasoning_steps=reasoning_steps,
                session_id=session_id or ""
            )
    
    async def _search(
        self, 
        query: str, 
        mode: str, 
        domain: DomainType
    ) -> List[Dict[str, Any]]:
        """Search for information using available APIs"""
        results = []
        
        # Try Perplexity first
        if self.perplexity_api_key:
            try:
                perplexity_results = await self._search_perplexity(query, mode)
                results.extend(perplexity_results)
            except Exception as e:
                print(f"Perplexity search failed: {e}")
        
        # Fallback to Grok's knowledge
        if not results:
            results = await self._search_grok(query, domain)
        
        return results[:10]  # Limit to 10 sources
    
    async def _search_perplexity(self, query: str, mode: str) -> List[Dict]:
        """Search using Perplexity API"""
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
                        {"role": "user", "content": f"Search for: {query}. Return factual information with sources."}
                    ],
                    "return_citations": True
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                citations = data.get("citations", [])
                return [
                    {
                        "title": f"Source {i+1}",
                        "url": url,
                        "snippet": ""
                    }
                    for i, url in enumerate(citations)
                ]
        
        return []
    
    async def _search_grok(self, query: str, domain: DomainType) -> List[Dict]:
        """Use Grok to generate search-like results with real-time data"""
        if not self.grok_api_key:
            return []
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.grok_base_url}/chat/completions",
                headers={
                    "Authorization": f"Bearer {self.grok_api_key}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "grok-3-latest",
                    "messages": [
                        {
                            "role": "system",
                            "content": f"You are a research assistant. For the query, provide 5 relevant sources with titles and URLs from reputable {domain.value} publications. Format as JSON array with 'title', 'url', 'snippet' fields."
                        },
                        {"role": "user", "content": query}
                    ],
                    "temperature": 0.3
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                content = data["choices"][0]["message"]["content"]
                
                # Try to parse JSON from response
                try:
                    # Find JSON array in response
                    json_match = re.search(r'\[[\s\S]*\]', content)
                    if json_match:
                        sources = json.loads(json_match.group())
                        return sources
                except:
                    pass
        
        return []
    
    async def _generate_response(
        self,
        query: str,
        search_results: List[Dict],
        intent_result: IntentResult,
        session_id: str
    ) -> ResponseContract:
        """Generate structured response using Grok"""
        
        # Build context from search results
        sources_context = "\n".join([
            f"[{i+1}] {r.get('title', 'Source')}: {r.get('snippet', '')}"
            for i, r in enumerate(search_results)
        ])
        
        # System prompt for structured output
        system_prompt = f"""You are McLeuker AI, a professional {intent_result.domain.value} expert.
        
IMPORTANT RULES:
1. Write clean prose WITHOUT inline citations like [1] or [2]
2. Do NOT reference sources in the text
3. Provide actionable, specific information
4. Use markdown formatting (headers, bold, bullets)
5. Be comprehensive but concise
6. Today's date is {datetime.now().strftime('%B %d, %Y')}

The sources will be displayed separately in the UI, so focus on the content itself."""

        user_prompt = f"""Query: {query}

Available information:
{sources_context}

Provide a comprehensive response with:
1. A brief summary (2-3 sentences)
2. Key insights (3-5 bullet points)
3. Detailed sections as needed
4. Actionable recommendations

Remember: NO inline citations in your response."""

        # Call Grok
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
                    "max_tokens": 2000
                }
            )
            
            if response.status_code != 200:
                raise Exception(f"Grok API error: {response.status_code}")
            
            data = response.json()
            content = data["choices"][0]["message"]["content"]
        
        # Parse response into structured format
        return self._parse_to_contract(
            content=content,
            query=query,
            search_results=search_results,
            intent_result=intent_result
        )
    
    def _parse_to_contract(
        self,
        content: str,
        query: str,
        search_results: List[Dict],
        intent_result: IntentResult
    ) -> ResponseContract:
        """Parse Grok response into ResponseContract format"""
        
        # Extract summary (first paragraph or first 2 sentences)
        paragraphs = content.split('\n\n')
        summary = paragraphs[0] if paragraphs else content[:200]
        
        # Clean any remaining citations from content
        clean_content = re.sub(r'\[\d+\]', '', content)
        clean_content = re.sub(r'\s+', ' ', clean_content).strip()
        
        # Create sources from search results
        sources = [
            Source(
                id=f"src_{i+1}",
                title=r.get("title", f"Source {i+1}"),
                url=r.get("url", ""),
                snippet=r.get("snippet", ""),
                domain=intent_result.domain.value,
                reliability_score=0.8
            )
            for i, r in enumerate(search_results)
        ]
        
        # Extract key insights (look for bullet points)
        insights = []
        bullet_pattern = r'[-•*]\s*(.+?)(?=\n|$)'
        bullet_matches = re.findall(bullet_pattern, content)
        for i, match in enumerate(bullet_matches[:5]):
            insights.append(KeyInsight(
                id=f"insight_{i+1}",
                text=match.strip(),
                importance="high" if i < 2 else "medium",
                source_ids=[f"src_{(i % len(sources)) + 1}"] if sources else []
            ))
        
        # Create layout sections
        sections = []
        header_pattern = r'^#+\s*(.+?)$'
        headers = re.findall(header_pattern, content, re.MULTILINE)
        for i, header in enumerate(headers[:5]):
            sections.append(LayoutSection(
                id=f"section_{i+1}",
                title=header.strip(),
                content_type="text",
                order=i+1
            ))
        
        # Generate follow-up questions
        follow_ups = [
            f"What specific aspects of {intent_result.domain.value} would you like to explore further?",
            "Would you like me to generate a detailed report on this topic?",
            "Are there any particular brands or products you'd like me to focus on?"
        ]
        
        return ResponseContract(
            query=query,
            summary=summary[:500],
            main_content=clean_content,
            sources=sources,
            files=[],
            tables=[],
            key_insights=insights,
            layout_sections=sections,
            intent_type=intent_result.intent_type.value,
            domain=intent_result.domain.value,
            confidence_score=intent_result.confidence,
            follow_up_questions=follow_ups,
            generated_at=datetime.now().isoformat()
        )
    
    async def _generate_files(
        self,
        query: str,
        response: ResponseContract
    ) -> List[GeneratedFile]:
        """Generate downloadable files based on response data"""
        files = []
        
        # Generate Excel if data-related query
        if response.tables or "data" in query.lower() or "excel" in query.lower():
            try:
                excel_file = await file_generator.generate_excel(
                    title=f"McLeuker Report - {query[:50]}",
                    data={
                        "Summary": response.summary,
                        "Key Insights": [i.text for i in response.key_insights],
                        "Sources": [{"Title": s.title, "URL": s.url} for s in response.sources]
                    }
                )
                if excel_file:
                    files.append(excel_file)
            except Exception as e:
                print(f"Excel generation failed: {e}")
        
        return files


# Global instance
orchestrator = V5Orchestrator()
