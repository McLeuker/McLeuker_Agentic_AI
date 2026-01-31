"""
McLeuker Agentic AI Platform - Conversation Memory System

Robust memory management for maintaining context across conversations.
Similar to how Manus AI and ChatGPT maintain conversation context.
"""

import json
import hashlib
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field, asdict
from collections import OrderedDict
import threading


@dataclass
class Message:
    """A single message in a conversation."""
    role: str  # "user", "assistant", "system"
    content: str
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp.isoformat(),
            "metadata": self.metadata
        }
    
    def to_llm_format(self) -> Dict[str, str]:
        """Convert to format suitable for LLM API calls."""
        return {"role": self.role, "content": self.content}


@dataclass
class ConversationContext:
    """Extracted context from a conversation."""
    topics: List[str] = field(default_factory=list)
    entities: Dict[str, str] = field(default_factory=dict)  # name -> type
    key_facts: List[str] = field(default_factory=list)
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    last_intent: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass
class Conversation:
    """A complete conversation with memory and context."""
    id: str
    user_id: Optional[str] = None
    messages: List[Message] = field(default_factory=list)
    context: ConversationContext = field(default_factory=ConversationContext)
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)
    title: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def add_message(self, role: str, content: str, metadata: Dict[str, Any] = None):
        """Add a message to the conversation."""
        msg = Message(
            role=role,
            content=content,
            metadata=metadata or {}
        )
        self.messages.append(msg)
        self.updated_at = datetime.utcnow()
        return msg
    
    def get_recent_messages(self, count: int = 10) -> List[Message]:
        """Get the most recent messages."""
        return self.messages[-count:] if self.messages else []
    
    def get_messages_for_llm(self, max_messages: int = 20, max_tokens: int = 8000) -> List[Dict[str, str]]:
        """Get messages formatted for LLM API, respecting token limits."""
        messages = []
        total_chars = 0
        char_limit = max_tokens * 4  # Rough estimate: 4 chars per token
        
        # Always include system message if present
        for msg in self.messages:
            if msg.role == "system":
                messages.append(msg.to_llm_format())
                total_chars += len(msg.content)
                break
        
        # Add recent messages in reverse order, respecting limits
        recent = self.messages[-max_messages:]
        for msg in recent:
            if msg.role != "system":
                msg_chars = len(msg.content)
                if total_chars + msg_chars > char_limit:
                    break
                messages.append(msg.to_llm_format())
                total_chars += msg_chars
        
        return messages
    
    def get_context_summary(self) -> str:
        """Generate a summary of the conversation context."""
        parts = []
        
        if self.context.topics:
            parts.append(f"Topics discussed: {', '.join(self.context.topics)}")
        
        if self.context.entities:
            entities_str = ", ".join([f"{name} ({type_})" for name, type_ in self.context.entities.items()])
            parts.append(f"Key entities: {entities_str}")
        
        if self.context.key_facts:
            parts.append(f"Key facts: {'; '.join(self.context.key_facts[-5:])}")
        
        if self.context.last_intent:
            parts.append(f"Last intent: {self.context.last_intent}")
        
        return "\n".join(parts) if parts else "No context available."
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "user_id": self.user_id,
            "messages": [m.to_dict() for m in self.messages],
            "context": self.context.to_dict(),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "title": self.title,
            "metadata": self.metadata
        }


class ConversationMemoryStore:
    """
    In-memory conversation store with LRU eviction.
    
    Maintains conversation history and context for all active conversations.
    """
    
    def __init__(self, max_conversations: int = 1000, ttl_hours: int = 24):
        self.max_conversations = max_conversations
        self.ttl = timedelta(hours=ttl_hours)
        self._conversations: OrderedDict[str, Conversation] = OrderedDict()
        self._user_conversations: Dict[str, List[str]] = {}  # user_id -> conversation_ids
        self._lock = threading.RLock()
    
    def create_conversation(
        self,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Conversation:
        """Create a new conversation."""
        with self._lock:
            if not conversation_id:
                conversation_id = self._generate_id()
            
            conversation = Conversation(
                id=conversation_id,
                user_id=user_id
            )
            
            self._conversations[conversation_id] = conversation
            
            # Track user conversations
            if user_id:
                if user_id not in self._user_conversations:
                    self._user_conversations[user_id] = []
                self._user_conversations[user_id].append(conversation_id)
            
            # Evict old conversations if needed
            self._evict_if_needed()
            
            return conversation
    
    def get_conversation(self, conversation_id: str) -> Optional[Conversation]:
        """Get a conversation by ID."""
        with self._lock:
            conv = self._conversations.get(conversation_id)
            if conv:
                # Move to end (most recently used)
                self._conversations.move_to_end(conversation_id)
            return conv
    
    def get_or_create_conversation(
        self,
        conversation_id: Optional[str] = None,
        user_id: Optional[str] = None
    ) -> Conversation:
        """Get an existing conversation or create a new one."""
        if conversation_id:
            conv = self.get_conversation(conversation_id)
            if conv:
                return conv
        return self.create_conversation(conversation_id, user_id)
    
    def get_user_conversations(self, user_id: str, limit: int = 50) -> List[Conversation]:
        """Get all conversations for a user."""
        with self._lock:
            conv_ids = self._user_conversations.get(user_id, [])
            conversations = []
            for cid in reversed(conv_ids[-limit:]):
                conv = self._conversations.get(cid)
                if conv:
                    conversations.append(conv)
            return conversations
    
    def delete_conversation(self, conversation_id: str) -> bool:
        """Delete a conversation."""
        with self._lock:
            conv = self._conversations.pop(conversation_id, None)
            if conv and conv.user_id:
                user_convs = self._user_conversations.get(conv.user_id, [])
                if conversation_id in user_convs:
                    user_convs.remove(conversation_id)
            return conv is not None
    
    def add_message(
        self,
        conversation_id: str,
        role: str,
        content: str,
        metadata: Dict[str, Any] = None
    ) -> Optional[Message]:
        """Add a message to a conversation."""
        conv = self.get_conversation(conversation_id)
        if conv:
            return conv.add_message(role, content, metadata)
        return None
    
    def _generate_id(self) -> str:
        """Generate a unique conversation ID."""
        timestamp = datetime.utcnow().isoformat()
        hash_input = f"{timestamp}-{len(self._conversations)}"
        return hashlib.sha256(hash_input.encode()).hexdigest()[:16]
    
    def _evict_if_needed(self):
        """Evict old conversations if over capacity."""
        while len(self._conversations) > self.max_conversations:
            # Remove oldest (first) item
            oldest_id, oldest_conv = next(iter(self._conversations.items()))
            self._conversations.pop(oldest_id)
            
            # Clean up user tracking
            if oldest_conv.user_id:
                user_convs = self._user_conversations.get(oldest_conv.user_id, [])
                if oldest_id in user_convs:
                    user_convs.remove(oldest_id)
    
    def cleanup_expired(self):
        """Remove expired conversations."""
        with self._lock:
            now = datetime.utcnow()
            expired = [
                cid for cid, conv in self._conversations.items()
                if now - conv.updated_at > self.ttl
            ]
            for cid in expired:
                self.delete_conversation(cid)
            return len(expired)


# Global memory store instance
_memory_store: Optional[ConversationMemoryStore] = None


def get_memory_store() -> ConversationMemoryStore:
    """Get or create the global memory store."""
    global _memory_store
    if _memory_store is None:
        _memory_store = ConversationMemoryStore()
    return _memory_store
