"""
McLeuker AI V5.1 - Core Orchestrator
====================================
The brain of the system. Coordinates all layers and enforces the response contract.

Architecture:
User Input
 → Intent Router
 → Query Planner  
 → Tool Executor (Grok + Search)
 → Response Contract Builder
 → File Generator (if needed)
 → Structured Response

Key improvements over V5:
1. ENFORCES response contract - LLM fills slots, doesn't decide layout
2. Separates content from citations
3. Generates real files
4. Prevents domain overfitting
"""

import os
import json
import asyncio
import aiohttp
import re
from datetime import datetime
from typing import Dict, Any, List, Optional, AsyncGenerator
import uuid

from ..schemas.response_contract import (
    ResponseContract, Source, GeneratedFile, TableData, KeyInsight,
    ActionItem, LayoutSection, IntentType, DomainType, StreamingChunk,
    create_empty_response
)
from ..layers.intent.intent_router import intent_router
from ..services.file_generator import file_generator


class V51Orchestrator:
    """
    V5.1 Orchestrator with Response Contract Enforcement
    """
    
    def __init__(self):
        # API Keys
        self.grok_api_key = os.getenv("XAI_API_KEY") or os.getenv("GROK_API_KEY")
        self.serper_api_key = os.getenv("SERPER_API_KEY")
        
        # Grok API endpoint
        self.grok_url = "https://api.x.ai/v1/chat/completions"
        
        # Current date for context
        self.current_date = datetime.now().strftime("%B %d, %Y")
        
        # Session storage
        self.sessions: Dict[str, List[Dict]] = {}
    
    async def process(
        self,
        message: str,
        session_id: str = None,
        mode: str = "quick"
    ) -> ResponseContract:
        """
        Main processing pipeline with response contract enforcement.
        """
        session_id = session_id or str(uuid.uuid4())
        start_time = datetime.now()
        
        try:
            # === STEP 1: Intent Classification ===
            classification = intent_router.classify(message)
            intent = classification['intent']
            domain = classification['domain']
            
            # === STEP 2: Search (if needed) ===
            sources = []
            search_context = ""
            
            if classification['requires_search']:
                search_results = await self._search(message, mode)
                sources = self._parse_sources(search_results)
                search_context = self._format_search_context(search_results)
            
            # === STEP 3: Generate Response with Grok ===
            # Use structured prompt that enforces clean output
            structured_response = await self._generate_structured_response(
                message=message,
                intent=intent,
                domain=domain,
                search_context=search_context,
                sources=sources
            )
            
            # === STEP 4: Generate Files (if requested) ===
            files = []
            if classification['requires_file_generation']:
                files = await self._generate_files(
                    structured_response,
                    classification['file_type'],
                    message
                )
            
            # === STEP 5: Build Response Contract ===
            processing_time = int((datetime.now() - start_time).total_seconds() * 1000)
            
            response = ResponseContract(
                session_id=session_id,
                intent=intent,
                domain=domain,
                confidence=classification['confidence'],
                summary=structured_response.get('summary', ''),
                main_content=structured_response.get('main_content', ''),
                key_insights=self._parse_insights(structured_response.get('key_insights', [])),
                tables=self._parse_tables(structured_response.get('tables', [])),
                sections=self._parse_sections(structured_response.get('sections', [])),
                sources=sources,
                source_count=len(sources),
                files=files,
                action_items=self._parse_actions(structured_response.get('action_items', [])),
                follow_up_questions=structured_response.get('follow_up_questions', []),
                credits_used=2 if mode == 'quick' else 5,
                processing_time_ms=processing_time,
                success=True
            )
            
            return response
            
        except Exception as e:
            return create_empty_response(session_id, str(e))
    
    async def _search(self, query: str, mode: str) -> List[Dict]:
        """Perform web search using Serper API"""
        if not self.serper_api_key:
            return []
        
        num_results = 5 if mode == 'quick' else 10
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    "https://google.serper.dev/search",
                    headers={
                        "X-API-KEY": self.serper_api_key,
                        "Content-Type": "application/json"
                    },
                    json={
                        "q": query,
                        "num": num_results
                    },
                    timeout=aiohttp.ClientTimeout(total=15)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        return data.get("organic", [])
        except Exception as e:
            print(f"Search error: {e}")
        
        return []
    
    def _parse_sources(self, search_results: List[Dict]) -> List[Source]:
        """Convert search results to Source objects"""
        sources = []
        for result in search_results[:5]:
            sources.append(Source(
                title=result.get("title", ""),
                url=result.get("link", ""),
                snippet=result.get("snippet", ""),
                publisher=self._extract_publisher(result.get("link", ""))
            ))
        return sources
    
    def _extract_publisher(self, url: str) -> str:
        """Extract publisher name from URL"""
        try:
            from urllib.parse import urlparse
            domain = urlparse(url).netloc
            # Remove www. and .com/.org etc
            parts = domain.replace("www.", "").split(".")
            return parts[0].title() if parts else ""
        except:
            return ""
    
    def _format_search_context(self, search_results: List[Dict]) -> str:
        """Format search results as context for Grok"""
        if not search_results:
            return ""
        
        context_parts = ["SEARCH RESULTS:"]
        for i, result in enumerate(search_results, 1):
            context_parts.append(f"""
Source {i}: {result.get('title', '')}
URL: {result.get('link', '')}
Content: {result.get('snippet', '')}
""")
        return "\n".join(context_parts)
    
    async def _generate_structured_response(
        self,
        message: str,
        intent: IntentType,
        domain: DomainType,
        search_context: str,
        sources: List[Source]
    ) -> Dict[str, Any]:
        """
        Generate response using Grok with STRUCTURED output enforcement.
        
        Key: LLM fills slots, doesn't decide layout freely.
        """
        
        # Build the structured prompt
        system_prompt = f"""You are McLeuker AI, a professional fashion and lifestyle intelligence assistant.
Today's date: {self.current_date}

CRITICAL OUTPUT RULES:
1. Write CLEAN PROSE without inline citations like [1][2][3]
2. DO NOT put citation numbers in the main content
3. Sources are provided separately - just write naturally
4. Structure your response in clear sections
5. Be concise but comprehensive
6. Focus on actionable insights

User Intent: {intent.value}
Domain: {domain.value}

You MUST respond with a JSON object in this EXACT format:
{{
    "summary": "1-2 sentence TL;DR",
    "main_content": "Clean prose WITHOUT any [1][2][3] citations. Write naturally.",
    "key_insights": [
        {{"title": "Insight title", "description": "Brief explanation"}}
    ],
    "tables": [
        {{"title": "Table title", "headers": ["Col1", "Col2"], "rows": [["val1", "val2"]]}}
    ],
    "action_items": [
        {{"action": "What to do", "details": "How to do it"}}
    ],
    "follow_up_questions": ["Question 1?", "Question 2?"]
}}

IMPORTANT: The main_content must be CLEAN TEXT without any citation markers."""

        user_prompt = f"""User Query: {message}

{search_context}

Generate a structured response following the JSON format specified. Remember:
- NO inline citations in main_content
- Write clean, professional prose
- Include actionable insights
- Generate tables if comparing data"""

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(
                    self.grok_url,
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
                        "max_tokens": 4000
                    },
                    timeout=aiohttp.ClientTimeout(total=60)
                ) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        content = data["choices"][0]["message"]["content"]
                        
                        # Parse JSON response
                        return self._parse_structured_response(content)
                    else:
                        error_text = await resp.text()
                        print(f"Grok API error: {resp.status} - {error_text}")
                        return self._fallback_response(message)
                        
        except Exception as e:
            print(f"Grok generation error: {e}")
            return self._fallback_response(message)
    
    def _parse_structured_response(self, content: str) -> Dict[str, Any]:
        """Parse the structured JSON response from Grok"""
        try:
            # Try to extract JSON from the response
            # Handle cases where Grok wraps JSON in markdown code blocks
            json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
            if json_match:
                content = json_match.group(1)
            else:
                # Try to find JSON object directly
                json_match = re.search(r'\{.*\}', content, re.DOTALL)
                if json_match:
                    content = json_match.group(0)
            
            parsed = json.loads(content)
            
            # Clean any remaining citations from main_content
            if 'main_content' in parsed:
                parsed['main_content'] = self._remove_citations(parsed['main_content'])
            
            return parsed
            
        except json.JSONDecodeError:
            # If JSON parsing fails, extract content manually
            return {
                'summary': '',
                'main_content': self._remove_citations(content),
                'key_insights': [],
                'tables': [],
                'action_items': [],
                'follow_up_questions': []
            }
    
    def _remove_citations(self, text: str) -> str:
        """Remove inline citations like [1], [2][3], etc."""
        # Remove citation patterns
        text = re.sub(r'\[\d+\]', '', text)
        text = re.sub(r'\[\d+,\s*\d+\]', '', text)
        text = re.sub(r'\[\d+-\d+\]', '', text)
        # Clean up extra spaces
        text = re.sub(r'\s+', ' ', text)
        text = re.sub(r'\s+([.,;:])', r'\1', text)
        return text.strip()
    
    def _fallback_response(self, message: str) -> Dict[str, Any]:
        """Fallback response when Grok fails"""
        return {
            'summary': 'I encountered an issue processing your request.',
            'main_content': f'I apologize, but I was unable to fully process your query: "{message}". Please try again or rephrase your question.',
            'key_insights': [],
            'tables': [],
            'action_items': [],
            'follow_up_questions': ['Would you like to try a different query?']
        }
    
    async def _generate_files(
        self,
        structured_response: Dict[str, Any],
        file_type: str,
        original_query: str
    ) -> List[GeneratedFile]:
        """Generate actual downloadable files"""
        files = []
        
        try:
            # Extract table data for file generation
            tables = structured_response.get('tables', [])
            
            if file_type == 'excel' and tables:
                for table in tables:
                    if isinstance(table, dict) and 'headers' in table and 'rows' in table:
                        table_data = TableData(
                            title=table.get('title', 'Data'),
                            headers=table['headers'],
                            rows=table['rows']
                        )
                        file = file_generator.generate_excel_from_table(
                            table_data,
                            title=table.get('title', 'McLeuker AI Report')
                        )
                        files.append(file)
            
            elif file_type == 'csv' and tables:
                for table in tables:
                    if isinstance(table, dict) and 'headers' in table and 'rows' in table:
                        # Convert to list of dicts
                        data = []
                        for row in table['rows']:
                            row_dict = {table['headers'][i]: row[i] for i in range(min(len(table['headers']), len(row)))}
                            data.append(row_dict)
                        file = file_generator.generate_csv(data, title=table.get('title', 'data'))
                        files.append(file)
            
            elif file_type == 'pdf':
                content = structured_response.get('main_content', '')
                file = file_generator.generate_pdf(
                    content=content,
                    title=f"McLeuker AI Report",
                    tables=[TableData(**t) for t in tables if isinstance(t, dict)]
                )
                files.append(file)
                
        except Exception as e:
            print(f"File generation error: {e}")
        
        return files
    
    def _parse_insights(self, insights: List) -> List[KeyInsight]:
        """Parse key insights from response"""
        parsed = []
        for insight in insights:
            if isinstance(insight, dict):
                parsed.append(KeyInsight(
                    title=insight.get('title', ''),
                    description=insight.get('description', '')
                ))
        return parsed
    
    def _parse_tables(self, tables: List) -> List[TableData]:
        """Parse tables from response"""
        parsed = []
        for table in tables:
            if isinstance(table, dict) and 'headers' in table and 'rows' in table:
                parsed.append(TableData(
                    title=table.get('title'),
                    headers=table['headers'],
                    rows=table['rows']
                ))
        return parsed
    
    def _parse_sections(self, sections: List) -> List[LayoutSection]:
        """Parse layout sections from response"""
        parsed = []
        for section in sections:
            if isinstance(section, dict):
                parsed.append(LayoutSection(
                    title=section.get('title', ''),
                    content=section.get('content', '')
                ))
        return parsed
    
    def _parse_actions(self, actions: List) -> List[ActionItem]:
        """Parse action items from response"""
        parsed = []
        for action in actions:
            if isinstance(action, dict):
                parsed.append(ActionItem(
                    action=action.get('action', ''),
                    details=action.get('details'),
                    link=action.get('link')
                ))
        return parsed


# Singleton instance
orchestrator = V51Orchestrator()
