"""
McLeuker Memory Layer — Context Management and Knowledge Persistence
=====================================================================

Provides memory capabilities for the agentic engine:
- MemoryManager: Session and long-term memory
- ContextCompressor: Token management for kimi-2.5's 256K window
- KnowledgeGraph: Entity and relationship tracking
"""

from .memory_manager import MemoryManager, MemoryEntry, MemoryType
from .context_compressor import ContextCompressor, CompressionResult
from .knowledge_graph import KnowledgeGraph, Entity, Relationship

__all__ = [
    "MemoryManager", "MemoryEntry", "MemoryType",
    "ContextCompressor", "CompressionResult",
    "KnowledgeGraph", "Entity", "Relationship",
]
