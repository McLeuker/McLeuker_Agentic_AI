"""
McLeuker AI V6 - Memory Manager
===============================
Manus AI-style memory and context management.

This module provides:
1. Conversation history management
2. Context extraction and summarization
3. Entity tracking across conversations
4. Session persistence
"""

import os
import json
import asyncio
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import defaultdict
import httpx


@dataclass
class Message:
    """A single message in the conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }


@dataclass
class ConversationContext:
    """Context extracted from a conversation"""
    entities: List[str] = field(default_factory=list)  # Key entities mentioned
    topics: List[str] = field(default_factory=list)    # Topics discussed
    preferences: Dict[str, Any] = field(default_factory=dict)  # User preferences
    summary: str = ""  # Summary of the conversation
    last_intent: str = ""  # Last detected intent
    
    def to_dict(self) -> Dict:
        return {
            "entities": self.entities,
            "topics": self.topics,
            "preferences": self.preferences,
            "summary": self.summary,
            "last_intent": self.last_intent
        }


@dataclass
class Session:
    """A conversation session with full history and context"""
    session_id: str
    messages: List[Message] = field(default_factory=list)
    context: ConversationContext = field(default_factory=ConversationContext)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    user_id: Optional[str] = None
    domain: str = "general"
    
    def to_dict(self) -> Dict:
        return {
            "session_id": self.session_id,
            "messages": [m.to_dict() for m in self.messages],
            "context": self.context.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "user_id": self.user_id,
            "domain": self.domain
        }


class MemoryManager:
    """
    Manus AI-style Memory Manager
    
    Provides persistent context across conversations,
    entity tracking, and intelligent summarization.
    """
    
    def __init__(self):
        self.grok_api_key = os.getenv("XAI_API_KEY", "")
        self.grok_base_url = "https://api.x.ai/v1"
        
        # In-memory session storage (can be replaced with database)
        self.sessions: Dict[str, Session] = {}
        
        # Configuration
        self.max_messages_in_context = 10  # Max messages to include in context
        self.max_context_tokens = 2000     # Approximate max tokens for context
        self.summarize_threshold = 6       # Summarize after this many messages
    
    def get_or_create_session(
        self, 
        session_id: str, 
        user_id: Optional[str] = None,
        domain: str = "general"
    ) -> Session:
        """Get existing session or create a new one"""
        if session_id not in self.sessions:
            self.sessions[session_id] = Session(
                session_id=session_id,
                user_id=user_id,
                domain=domain
            )
        return self.sessions[session_id]
    
    def add_message(
        self, 
        session_id: str, 
        role: str, 
        content: str,
        metadata: Optional[Dict] = None
    ) -> Message:
        """Add a message to the session"""
        session = self.get_or_create_session(session_id)
        
        message = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        
        session.messages.append(message)
        session.updated_at = datetime.utcnow()
        
        return message
    
    async def get_context_for_query(
        self, 
        session_id: str, 
        current_query: str
    ) -> Dict[str, Any]:
        """
        Get relevant context for a new query.
        
        This returns:
        - Recent messages (formatted for LLM)
        - Extracted entities and topics
        - Summary of earlier conversation
        - Relevant preferences
        """
        session = self.get_or_create_session(session_id)
        
        # If we have many messages, summarize older ones
        if len(session.messages) >= self.summarize_threshold:
            await self._update_context_summary(session)
        
        # Build context
        context = {
            "session_id": session_id,
            "has_history": len(session.messages) > 0,
            "message_count": len(session.messages),
            "recent_messages": self._get_recent_messages(session),
            "context_summary": session.context.summary,
            "entities": session.context.entities,
            "topics": session.context.topics,
            "preferences": session.context.preferences,
            "last_intent": session.context.last_intent,
            "domain": session.domain
        }
        
        # Extract entities from current query
        new_entities = await self._extract_entities(current_query)
        context["current_entities"] = new_entities
        
        return context
    
    def _get_recent_messages(self, session: Session) -> List[Dict]:
        """Get recent messages formatted for LLM context"""
        recent = session.messages[-self.max_messages_in_context:]
        return [
            {
                "role": m.role,
                "content": m.content[:500]  # Truncate long messages
            }
            for m in recent
        ]
    
    async def _update_context_summary(self, session: Session):
        """Update the context summary with older messages"""
        if len(session.messages) < self.summarize_threshold:
            return
        
        # Get messages to summarize (older ones)
        messages_to_summarize = session.messages[:-3]  # Keep last 3 unsummarized
        
        if not messages_to_summarize:
            return
        
        # Format messages for summarization
        conversation_text = "\n".join([
            f"{m.role}: {m.content[:200]}"
            for m in messages_to_summarize
        ])
        
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
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
                                "content": """Summarize this conversation in 2-3 sentences, focusing on:
1. What the user was asking about
2. Key information provided
3. Any preferences or requirements mentioned
Keep it concise and factual."""
                            },
                            {
                                "role": "user",
                                "content": conversation_text
                            }
                        ],
                        "max_tokens": 150,
                        "temperature": 0.3
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    session.context.summary = data["choices"][0]["message"]["content"].strip()
                    
                    # Also extract topics
                    await self._extract_topics_from_summary(session)
        except Exception as e:
            # Keep existing summary if update fails
            pass
    
    async def _extract_entities(self, text: str) -> List[str]:
        """Extract key entities from text"""
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
                                "content": "Extract key entities (brands, people, places, products, concepts) from the text. Return only a JSON array of strings. Example: [\"Gucci\", \"sustainability\", \"Paris Fashion Week\"]"
                            },
                            {
                                "role": "user",
                                "content": text
                            }
                        ],
                        "max_tokens": 100,
                        "temperature": 0.1
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    try:
                        return json.loads(content)
                    except:
                        return []
        except:
            pass
        
        return []
    
    async def _extract_topics_from_summary(self, session: Session):
        """Extract topics from the conversation summary"""
        if not session.context.summary:
            return
        
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
                                "content": "Extract 2-4 main topics from this summary. Return only a JSON array of strings."
                            },
                            {
                                "role": "user",
                                "content": session.context.summary
                            }
                        ],
                        "max_tokens": 50,
                        "temperature": 0.1
                    }
                )
                
                if response.status_code == 200:
                    data = response.json()
                    content = data["choices"][0]["message"]["content"].strip()
                    try:
                        session.context.topics = json.loads(content)
                    except:
                        pass
        except:
            pass
    
    def update_context(
        self, 
        session_id: str, 
        intent: str = "",
        entities: Optional[List[str]] = None,
        preferences: Optional[Dict] = None
    ):
        """Update session context with new information"""
        session = self.get_or_create_session(session_id)
        
        if intent:
            session.context.last_intent = intent
        
        if entities:
            # Add new entities, avoiding duplicates
            existing = set(session.context.entities)
            for entity in entities:
                if entity not in existing:
                    session.context.entities.append(entity)
            # Keep only the most recent 20 entities
            session.context.entities = session.context.entities[-20:]
        
        if preferences:
            session.context.preferences.update(preferences)
    
    def get_conversation_history(
        self, 
        session_id: str, 
        limit: int = 10
    ) -> List[Dict]:
        """Get conversation history for display"""
        session = self.get_or_create_session(session_id)
        return [m.to_dict() for m in session.messages[-limit:]]
    
    def clear_session(self, session_id: str):
        """Clear a session's history"""
        if session_id in self.sessions:
            del self.sessions[session_id]
    
    def get_context_prompt(self, context: Dict) -> str:
        """
        Generate a context prompt to prepend to the LLM request.
        
        This provides the AI with relevant context from the conversation.
        """
        parts = []
        
        if context.get("context_summary"):
            parts.append(f"Previous conversation summary: {context['context_summary']}")
        
        if context.get("entities"):
            parts.append(f"Key entities discussed: {', '.join(context['entities'][:10])}")
        
        if context.get("topics"):
            parts.append(f"Topics covered: {', '.join(context['topics'])}")
        
        if context.get("preferences"):
            prefs = context["preferences"]
            if prefs:
                pref_str = ", ".join([f"{k}: {v}" for k, v in list(prefs.items())[:5]])
                parts.append(f"User preferences: {pref_str}")
        
        if parts:
            return "CONTEXT:\n" + "\n".join(parts) + "\n\n"
        
        return ""


# Global instance
memory_manager = MemoryManager()
