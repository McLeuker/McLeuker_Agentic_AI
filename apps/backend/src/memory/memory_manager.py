"""
Memory Manager — Session and Long-Term Memory
===============================================

Manages memory across execution sessions:
- Short-term (session) memory
- Long-term memory persistence
- Memory search and retrieval
- Automatic importance scoring
"""

import json
import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path

logger = logging.getLogger(__name__)


class MemoryType(Enum):
    CONVERSATION = "conversation"
    FACT = "fact"
    PREFERENCE = "preference"
    TASK_RESULT = "task_result"
    ERROR = "error"
    LEARNING = "learning"


@dataclass
class MemoryEntry:
    """A single memory entry."""
    id: str
    content: str
    memory_type: MemoryType
    session_id: str
    importance: float = 0.5
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    access_count: int = 0
    last_accessed: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content[:500],
            "memory_type": self.memory_type.value,
            "session_id": self.session_id,
            "importance": self.importance,
            "tags": self.tags,
            "created_at": self.created_at,
            "access_count": self.access_count,
        }


class MemoryManager:
    """
    Manages memory for the agentic engine.

    Features:
    - Session-scoped short-term memory
    - Persistent long-term memory
    - Importance-based retrieval
    - Tag-based search
    """

    def __init__(self, persist_path: str = "/tmp/agentic_memory"):
        """
        Initialize memory manager.

        Args:
            persist_path: Path for memory persistence
        """
        self.persist_path = Path(persist_path)
        self.persist_path.mkdir(parents=True, exist_ok=True)

        self._short_term: Dict[str, List[MemoryEntry]] = {}  # session_id -> entries
        self._long_term: List[MemoryEntry] = []
        self._counter = 0

        self._load_long_term()

    def _generate_id(self) -> str:
        self._counter += 1
        return f"mem_{self._counter}_{datetime.now().strftime('%H%M%S')}"

    def store(
        self,
        content: str,
        memory_type: MemoryType,
        session_id: str,
        importance: float = 0.5,
        tags: Optional[List[str]] = None,
        metadata: Optional[Dict[str, Any]] = None,
    ) -> MemoryEntry:
        """Store a memory entry."""
        entry = MemoryEntry(
            id=self._generate_id(),
            content=content,
            memory_type=memory_type,
            session_id=session_id,
            importance=importance,
            tags=tags or [],
            metadata=metadata or {},
        )

        # Short-term
        if session_id not in self._short_term:
            self._short_term[session_id] = []
        self._short_term[session_id].append(entry)

        # Long-term if important enough
        if importance >= 0.7:
            self._long_term.append(entry)

        return entry

    def recall(
        self,
        session_id: str,
        memory_type: Optional[MemoryType] = None,
        tags: Optional[List[str]] = None,
        limit: int = 20,
    ) -> List[MemoryEntry]:
        """Recall memories for a session."""
        entries = self._short_term.get(session_id, [])

        if memory_type:
            entries = [e for e in entries if e.memory_type == memory_type]

        if tags:
            entries = [e for e in entries if any(t in e.tags for t in tags)]

        # Sort by importance and recency
        entries.sort(key=lambda e: (e.importance, e.created_at), reverse=True)

        # Update access counts
        for entry in entries[:limit]:
            entry.access_count += 1
            entry.last_accessed = datetime.now().isoformat()

        return entries[:limit]

    def recall_long_term(
        self,
        query: Optional[str] = None,
        memory_type: Optional[MemoryType] = None,
        limit: int = 10,
    ) -> List[MemoryEntry]:
        """Recall from long-term memory."""
        entries = list(self._long_term)

        if memory_type:
            entries = [e for e in entries if e.memory_type == memory_type]

        if query:
            query_lower = query.lower()
            entries = [e for e in entries if query_lower in e.content.lower() or
                       any(query_lower in t.lower() for t in e.tags)]

        entries.sort(key=lambda e: e.importance, reverse=True)
        return entries[:limit]

    def get_context_for_session(self, session_id: str, max_entries: int = 10) -> str:
        """Get formatted context string for a session."""
        entries = self.recall(session_id, limit=max_entries)

        if not entries:
            return ""

        context_parts = []
        for entry in entries:
            context_parts.append(f"[{entry.memory_type.value}] {entry.content}")

        return "\n".join(context_parts)

    def clear_session(self, session_id: str):
        """Clear short-term memory for a session."""
        if session_id in self._short_term:
            del self._short_term[session_id]

    def _save_long_term(self):
        """Save long-term memory to disk."""
        try:
            data = [e.to_dict() for e in self._long_term[-1000:]]  # Keep last 1000
            file_path = self.persist_path / "long_term.json"
            with open(file_path, "w") as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save long-term memory: {e}")

    def _load_long_term(self):
        """Load long-term memory from disk."""
        file_path = self.persist_path / "long_term.json"
        if not file_path.exists():
            return

        try:
            with open(file_path, "r") as f:
                data = json.load(f)

            for entry_data in data:
                try:
                    entry = MemoryEntry(
                        id=entry_data["id"],
                        content=entry_data["content"],
                        memory_type=MemoryType(entry_data["memory_type"]),
                        session_id=entry_data["session_id"],
                        importance=entry_data.get("importance", 0.5),
                        tags=entry_data.get("tags", []),
                        created_at=entry_data.get("created_at", ""),
                        access_count=entry_data.get("access_count", 0),
                    )
                    self._long_term.append(entry)
                except Exception:
                    pass

            logger.info(f"Loaded {len(self._long_term)} long-term memories")
        except Exception as e:
            logger.error(f"Failed to load long-term memory: {e}")

    def get_stats(self) -> Dict[str, Any]:
        """Get memory statistics."""
        return {
            "short_term_sessions": len(self._short_term),
            "short_term_entries": sum(len(v) for v in self._short_term.values()),
            "long_term_entries": len(self._long_term),
        }
