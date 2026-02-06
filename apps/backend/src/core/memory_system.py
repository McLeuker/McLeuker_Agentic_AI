"""
McLeuker AI V8 - Persistent Memory System
==========================================
Advanced memory system for maintaining conversation context across sessions.
Inspired by Manus AI's memory architecture.

Features:
- Short-term memory (current conversation)
- Long-term memory (persistent across sessions)
- Semantic memory (knowledge and facts)
- Episodic memory (past interactions)
- Working memory (current task context)
"""

import json
import hashlib
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List, Tuple
from dataclasses import dataclass, field, asdict
from enum import Enum
from collections import deque
import logging
import asyncio

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    """Types of memory storage"""
    SHORT_TERM = "short_term"      # Current conversation
    LONG_TERM = "long_term"        # Persistent across sessions
    SEMANTIC = "semantic"          # Facts and knowledge
    EPISODIC = "episodic"          # Past interactions
    WORKING = "working"            # Current task context


@dataclass
class MemoryEntry:
    """A single memory entry"""
    id: str
    content: str
    memory_type: MemoryType
    timestamp: datetime
    relevance_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    embedding: Optional[List[float]] = None
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def to_dict(self) -> Dict:
        return {
            "id": self.id,
            "content": self.content,
            "memory_type": self.memory_type.value,
            "timestamp": self.timestamp.isoformat(),
            "relevance_score": self.relevance_score,
            "metadata": self.metadata,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> "MemoryEntry":
        return cls(
            id=data["id"],
            content=data["content"],
            memory_type=MemoryType(data["memory_type"]),
            timestamp=datetime.fromisoformat(data["timestamp"]),
            relevance_score=data.get("relevance_score", 1.0),
            metadata=data.get("metadata", {}),
            access_count=data.get("access_count", 0),
            last_accessed=datetime.fromisoformat(data["last_accessed"]) if data.get("last_accessed") else None
        )


@dataclass
class ConversationContext:
    """Context for the current conversation"""
    user_id: str
    session_id: str
    topic: Optional[str] = None
    intent: Optional[str] = None
    entities: List[str] = field(default_factory=list)
    sentiment: str = "neutral"
    turn_count: int = 0
    started_at: datetime = field(default_factory=datetime.utcnow)
    last_message_at: Optional[datetime] = None
    preferences: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "session_id": self.session_id,
            "topic": self.topic,
            "intent": self.intent,
            "entities": self.entities,
            "sentiment": self.sentiment,
            "turn_count": self.turn_count,
            "started_at": self.started_at.isoformat(),
            "last_message_at": self.last_message_at.isoformat() if self.last_message_at else None,
            "preferences": self.preferences
        }


class ShortTermMemory:
    """
    Short-term memory for current conversation.
    Uses a sliding window approach with recency weighting.
    """
    
    def __init__(self, max_entries: int = 20, decay_rate: float = 0.1):
        self.max_entries = max_entries
        self.decay_rate = decay_rate
        self.entries: deque = deque(maxlen=max_entries)
        self.context: Optional[ConversationContext] = None
    
    def add(self, content: str, role: str = "user", metadata: Dict = None) -> MemoryEntry:
        """Add a new entry to short-term memory"""
        entry = MemoryEntry(
            id=self._generate_id(content),
            content=content,
            memory_type=MemoryType.SHORT_TERM,
            timestamp=datetime.utcnow(),
            metadata={"role": role, **(metadata or {})}
        )
        self.entries.append(entry)
        return entry
    
    def get_recent(self, n: int = 10) -> List[MemoryEntry]:
        """Get the n most recent entries"""
        return list(self.entries)[-n:]
    
    def get_context_summary(self) -> str:
        """Generate a summary of the current conversation context"""
        if not self.entries:
            return "No conversation history."
        
        recent = self.get_recent(5)
        summary_parts = []
        
        for entry in recent:
            role = entry.metadata.get("role", "unknown")
            content = entry.content[:200] + "..." if len(entry.content) > 200 else entry.content
            summary_parts.append(f"[{role}]: {content}")
        
        return "\n".join(summary_parts)
    
    def set_context(self, context: ConversationContext):
        """Set the conversation context"""
        self.context = context
    
    def clear(self):
        """Clear short-term memory"""
        self.entries.clear()
        self.context = None
    
    def _generate_id(self, content: str) -> str:
        """Generate a unique ID for a memory entry"""
        timestamp = datetime.utcnow().isoformat()
        return hashlib.md5(f"{content}{timestamp}".encode()).hexdigest()[:16]


class LongTermMemory:
    """
    Long-term memory for persistent storage across sessions.
    Stores important facts, user preferences, and key interactions.
    """
    
    def __init__(self, max_entries: int = 1000):
        self.max_entries = max_entries
        self.entries: Dict[str, MemoryEntry] = {}
        self.user_profiles: Dict[str, Dict] = {}
    
    def store(self, content: str, user_id: str, importance: float = 0.5, metadata: Dict = None) -> MemoryEntry:
        """Store a memory in long-term storage"""
        entry = MemoryEntry(
            id=self._generate_id(content, user_id),
            content=content,
            memory_type=MemoryType.LONG_TERM,
            timestamp=datetime.utcnow(),
            relevance_score=importance,
            metadata={"user_id": user_id, **(metadata or {})}
        )
        
        # Manage capacity
        if len(self.entries) >= self.max_entries:
            self._evict_least_relevant()
        
        self.entries[entry.id] = entry
        return entry
    
    def retrieve(self, query: str, user_id: str, top_k: int = 5) -> List[MemoryEntry]:
        """Retrieve relevant memories for a query"""
        user_entries = [
            e for e in self.entries.values()
            if e.metadata.get("user_id") == user_id
        ]
        
        # Simple keyword matching (would use embeddings in production)
        query_words = set(query.lower().split())
        scored_entries = []
        
        for entry in user_entries:
            entry_words = set(entry.content.lower().split())
            overlap = len(query_words & entry_words)
            score = overlap / max(len(query_words), 1) * entry.relevance_score
            scored_entries.append((entry, score))
        
        # Sort by score and return top_k
        scored_entries.sort(key=lambda x: x[1], reverse=True)
        
        results = []
        for entry, score in scored_entries[:top_k]:
            entry.access_count += 1
            entry.last_accessed = datetime.utcnow()
            results.append(entry)
        
        return results
    
    def update_user_profile(self, user_id: str, updates: Dict):
        """Update user profile with new information"""
        if user_id not in self.user_profiles:
            self.user_profiles[user_id] = {
                "created_at": datetime.utcnow().isoformat(),
                "preferences": {},
                "interests": [],
                "interaction_count": 0
            }
        
        profile = self.user_profiles[user_id]
        profile["interaction_count"] += 1
        profile["last_interaction"] = datetime.utcnow().isoformat()
        
        for key, value in updates.items():
            if key == "interests" and isinstance(value, list):
                existing = set(profile.get("interests", []))
                existing.update(value)
                profile["interests"] = list(existing)
            elif key == "preferences" and isinstance(value, dict):
                profile.setdefault("preferences", {}).update(value)
            else:
                profile[key] = value
    
    def get_user_profile(self, user_id: str) -> Optional[Dict]:
        """Get user profile"""
        return self.user_profiles.get(user_id)
    
    def _evict_least_relevant(self):
        """Remove the least relevant entry"""
        if not self.entries:
            return
        
        # Find entry with lowest combined score (relevance * recency)
        now = datetime.utcnow()
        min_score = float('inf')
        min_id = None
        
        for entry_id, entry in self.entries.items():
            age_days = (now - entry.timestamp).days + 1
            recency_factor = 1 / age_days
            combined_score = entry.relevance_score * recency_factor * (entry.access_count + 1)
            
            if combined_score < min_score:
                min_score = combined_score
                min_id = entry_id
        
        if min_id:
            del self.entries[min_id]
    
    def _generate_id(self, content: str, user_id: str) -> str:
        """Generate a unique ID"""
        timestamp = datetime.utcnow().isoformat()
        return hashlib.md5(f"{content}{user_id}{timestamp}".encode()).hexdigest()[:16]


class SemanticMemory:
    """
    Semantic memory for storing facts and knowledge.
    Organized by topics and categories.
    """
    
    def __init__(self):
        self.knowledge_base: Dict[str, List[Dict]] = {}
        self.facts: Dict[str, MemoryEntry] = {}
    
    def add_fact(self, fact: str, category: str, confidence: float = 1.0, source: str = None) -> MemoryEntry:
        """Add a fact to semantic memory"""
        entry = MemoryEntry(
            id=hashlib.md5(fact.encode()).hexdigest()[:16],
            content=fact,
            memory_type=MemoryType.SEMANTIC,
            timestamp=datetime.utcnow(),
            relevance_score=confidence,
            metadata={"category": category, "source": source}
        )
        
        self.facts[entry.id] = entry
        
        if category not in self.knowledge_base:
            self.knowledge_base[category] = []
        self.knowledge_base[category].append({
            "fact": fact,
            "confidence": confidence,
            "source": source,
            "added_at": datetime.utcnow().isoformat()
        })
        
        return entry
    
    def query_facts(self, query: str, category: str = None, top_k: int = 5) -> List[MemoryEntry]:
        """Query facts from semantic memory"""
        candidates = list(self.facts.values())
        
        if category:
            candidates = [f for f in candidates if f.metadata.get("category") == category]
        
        # Simple keyword matching
        query_words = set(query.lower().split())
        scored = []
        
        for fact in candidates:
            fact_words = set(fact.content.lower().split())
            overlap = len(query_words & fact_words)
            score = overlap / max(len(query_words), 1) * fact.relevance_score
            scored.append((fact, score))
        
        scored.sort(key=lambda x: x[1], reverse=True)
        return [f for f, s in scored[:top_k] if s > 0]
    
    def get_category_knowledge(self, category: str) -> List[Dict]:
        """Get all knowledge in a category"""
        return self.knowledge_base.get(category, [])


class WorkingMemory:
    """
    Working memory for current task execution.
    Tracks active goals, sub-tasks, and intermediate results.
    """
    
    def __init__(self):
        self.current_goal: Optional[str] = None
        self.sub_tasks: List[Dict] = []
        self.intermediate_results: Dict[str, Any] = {}
        self.active_tools: List[str] = []
        self.context_variables: Dict[str, Any] = {}
    
    def set_goal(self, goal: str):
        """Set the current goal"""
        self.current_goal = goal
        self.sub_tasks = []
        self.intermediate_results = {}
    
    def add_subtask(self, task: str, status: str = "pending", result: Any = None):
        """Add a subtask"""
        self.sub_tasks.append({
            "task": task,
            "status": status,
            "result": result,
            "created_at": datetime.utcnow().isoformat()
        })
    
    def update_subtask(self, index: int, status: str, result: Any = None):
        """Update a subtask status"""
        if 0 <= index < len(self.sub_tasks):
            self.sub_tasks[index]["status"] = status
            if result is not None:
                self.sub_tasks[index]["result"] = result
            self.sub_tasks[index]["updated_at"] = datetime.utcnow().isoformat()
    
    def store_result(self, key: str, value: Any):
        """Store an intermediate result"""
        self.intermediate_results[key] = {
            "value": value,
            "stored_at": datetime.utcnow().isoformat()
        }
    
    def get_result(self, key: str) -> Optional[Any]:
        """Get an intermediate result"""
        result = self.intermediate_results.get(key)
        return result["value"] if result else None
    
    def set_variable(self, key: str, value: Any):
        """Set a context variable"""
        self.context_variables[key] = value
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get a context variable"""
        return self.context_variables.get(key, default)
    
    def get_state(self) -> Dict:
        """Get the current working memory state"""
        return {
            "current_goal": self.current_goal,
            "sub_tasks": self.sub_tasks,
            "intermediate_results": list(self.intermediate_results.keys()),
            "active_tools": self.active_tools,
            "context_variables": list(self.context_variables.keys())
        }
    
    def clear(self):
        """Clear working memory"""
        self.current_goal = None
        self.sub_tasks = []
        self.intermediate_results = {}
        self.active_tools = []
        self.context_variables = {}


class MemorySystem:
    """
    Unified memory system combining all memory types.
    Provides a single interface for memory operations.
    """
    
    def __init__(self):
        self.short_term = ShortTermMemory()
        self.long_term = LongTermMemory()
        self.semantic = SemanticMemory()
        self.working = WorkingMemory()
        
        # Session tracking
        self.active_sessions: Dict[str, ConversationContext] = {}
    
    def start_session(self, user_id: str, session_id: str) -> ConversationContext:
        """Start a new conversation session"""
        context = ConversationContext(
            user_id=user_id,
            session_id=session_id
        )
        self.active_sessions[session_id] = context
        self.short_term.set_context(context)
        return context
    
    def end_session(self, session_id: str):
        """End a conversation session and consolidate memories"""
        if session_id in self.active_sessions:
            context = self.active_sessions[session_id]
            
            # Extract important information from short-term memory
            self._consolidate_to_long_term(context)
            
            del self.active_sessions[session_id]
            self.short_term.clear()
            self.working.clear()
    
    def add_message(self, content: str, role: str, session_id: str, metadata: Dict = None) -> MemoryEntry:
        """Add a message to memory"""
        entry = self.short_term.add(content, role, metadata)
        
        # Update context
        if session_id in self.active_sessions:
            context = self.active_sessions[session_id]
            context.turn_count += 1
            context.last_message_at = datetime.utcnow()
            
            # Extract entities and update topic
            self._update_context_from_message(context, content, role)
        
        return entry
    
    def get_context_for_response(self, query: str, user_id: str, session_id: str) -> Dict:
        """Get comprehensive context for generating a response"""
        context = {
            "conversation_history": self.short_term.get_context_summary(),
            "relevant_memories": [],
            "user_profile": None,
            "working_state": self.working.get_state(),
            "relevant_facts": []
        }
        
        # Get relevant long-term memories
        long_term_memories = self.long_term.retrieve(query, user_id, top_k=3)
        context["relevant_memories"] = [m.content for m in long_term_memories]
        
        # Get user profile
        context["user_profile"] = self.long_term.get_user_profile(user_id)
        
        # Get relevant facts
        relevant_facts = self.semantic.query_facts(query, top_k=3)
        context["relevant_facts"] = [f.content for f in relevant_facts]
        
        # Get session context
        if session_id in self.active_sessions:
            session_context = self.active_sessions[session_id]
            context["session"] = session_context.to_dict()
        
        return context
    
    def remember_important(self, content: str, user_id: str, importance: float = 0.7, metadata: Dict = None):
        """Store something important in long-term memory"""
        self.long_term.store(content, user_id, importance, metadata)
    
    def learn_fact(self, fact: str, category: str, confidence: float = 1.0, source: str = None):
        """Add a fact to semantic memory"""
        self.semantic.add_fact(fact, category, confidence, source)
    
    def set_task_goal(self, goal: str):
        """Set the current task goal in working memory"""
        self.working.set_goal(goal)
    
    def add_task_step(self, step: str, status: str = "pending"):
        """Add a task step to working memory"""
        self.working.add_subtask(step, status)
    
    def store_task_result(self, key: str, value: Any):
        """Store a task result in working memory"""
        self.working.store_result(key, value)
    
    def _consolidate_to_long_term(self, context: ConversationContext):
        """Consolidate important short-term memories to long-term"""
        # Extract key information from conversation
        recent_messages = self.short_term.get_recent(10)
        
        if len(recent_messages) >= 3:
            # Store conversation summary
            summary = self._generate_conversation_summary(recent_messages)
            self.long_term.store(
                summary,
                context.user_id,
                importance=0.6,
                metadata={"type": "conversation_summary", "session_id": context.session_id}
            )
        
        # Update user profile with learned preferences
        if context.topic:
            self.long_term.update_user_profile(context.user_id, {
                "interests": [context.topic],
                "last_topic": context.topic
            })
    
    def _update_context_from_message(self, context: ConversationContext, content: str, role: str):
        """Update context based on message content"""
        # Simple entity extraction (would use NER in production)
        words = content.split()
        
        # Look for capitalized words as potential entities
        potential_entities = [w for w in words if w[0].isupper() and len(w) > 2]
        context.entities.extend(potential_entities[:5])
        context.entities = list(set(context.entities))[-20:]  # Keep last 20 unique
        
        # Update topic based on keywords
        topic_keywords = {
            "fashion": ["fashion", "style", "clothing", "outfit", "wear", "designer"],
            "sustainability": ["sustainable", "eco", "green", "environmental", "ethical"],
            "technology": ["tech", "ai", "digital", "innovation", "software"],
            "beauty": ["beauty", "skincare", "makeup", "cosmetics"],
            "business": ["business", "market", "industry", "brand", "company"]
        }
        
        content_lower = content.lower()
        for topic, keywords in topic_keywords.items():
            if any(kw in content_lower for kw in keywords):
                context.topic = topic
                break
    
    def _generate_conversation_summary(self, messages: List[MemoryEntry]) -> str:
        """Generate a summary of the conversation"""
        user_messages = [m.content for m in messages if m.metadata.get("role") == "user"]
        
        if not user_messages:
            return "No user messages in conversation."
        
        # Simple summary: first and last user messages
        summary = f"User discussed: {user_messages[0][:100]}"
        if len(user_messages) > 1:
            summary += f" ... and concluded with: {user_messages[-1][:100]}"
        
        return summary


# Global memory system instance
memory_system = MemorySystem()


def get_memory_system() -> MemorySystem:
    """Get the global memory system"""
    return memory_system
