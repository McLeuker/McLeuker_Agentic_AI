"""
RAG V3 - Retrieval Augmented Generation System
================================================
Enhanced RAG system with:
- Document chunking with overlap
- Multiple embedding providers (Kimi, OpenAI-compatible)
- Vector similarity search via Supabase pgvector
- Contextual retrieval with conversation awareness
- Fallback to in-memory vector store

Integrates with existing Supabase client from main.py.
"""

import asyncio
import hashlib
import json
import logging
import math
import re
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from uuid import uuid4

import httpx

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Document model
# ---------------------------------------------------------------------------

@dataclass
class DocumentChunk:
    """A chunk of a document with its embedding."""
    id: str = field(default_factory=lambda: str(uuid4()))
    content: str = ""
    embedding: Optional[List[float]] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    source: Optional[str] = None
    document_type: str = "text"
    chunk_index: int = 0
    total_chunks: int = 1
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "source": self.source,
            "document_type": self.document_type,
            "chunk_index": self.chunk_index,
            "total_chunks": self.total_chunks,
        }


@dataclass
class SearchResult:
    """A search result with similarity score."""
    chunk: DocumentChunk
    similarity: float = 0.0


# ---------------------------------------------------------------------------
# Embedding providers
# ---------------------------------------------------------------------------

class EmbeddingProvider:
    """Base class for embedding providers."""
    async def embed(self, text: str) -> List[float]:
        raise NotImplementedError

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        return [await self.embed(t) for t in texts]


class KimiEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using Kimi / Moonshot API."""

    def __init__(
        self,
        api_key: str,
        base_url: str = "https://api.moonshot.ai/v1",
        model: str = "moonshot-v1-embedding",
    ):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.model = model

    async def embed(self, text: str) -> List[float]:
        async with httpx.AsyncClient(timeout=30) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/embeddings",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={"model": self.model, "input": text},
                )
                resp.raise_for_status()
                data = resp.json()
                return data["data"][0]["embedding"]
            except Exception as e:
                logger.error(f"Embedding failed: {e}")
                # Return zero vector as fallback
                return [0.0] * 1536

    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        async with httpx.AsyncClient(timeout=60) as client:
            try:
                resp = await client.post(
                    f"{self.base_url}/embeddings",
                    headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"},
                    json={"model": self.model, "input": texts},
                )
                resp.raise_for_status()
                data = resp.json()
                return [d["embedding"] for d in sorted(data["data"], key=lambda x: x["index"])]
            except Exception:
                return [await self.embed(t) for t in texts]


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """Embedding provider using any OpenAI-compatible API."""

    def __init__(self, client: Any, model: str = "text-embedding-3-small"):
        self.client = client
        self.model = model

    async def embed(self, text: str) -> List[float]:
        try:
            resp = await self.client.embeddings.create(model=self.model, input=text)
            return resp.data[0].embedding
        except Exception as e:
            logger.error(f"OpenAI embedding failed: {e}")
            return [0.0] * 1536


# ---------------------------------------------------------------------------
# Text chunking
# ---------------------------------------------------------------------------

def chunk_text(
    text: str,
    chunk_size: int = 1000,
    chunk_overlap: int = 200,
    separators: Optional[List[str]] = None,
) -> List[str]:
    """Split text into overlapping chunks."""
    if not text:
        return []

    if separators is None:
        separators = ["\n\n", "\n", ". ", " "]

    chunks = []
    current_pos = 0

    while current_pos < len(text):
        end_pos = min(current_pos + chunk_size, len(text))

        if end_pos < len(text):
            # Try to find a good split point
            best_split = end_pos
            for sep in separators:
                idx = text.rfind(sep, current_pos, end_pos)
                if idx > current_pos:
                    best_split = idx + len(sep)
                    break
            end_pos = best_split

        chunk = text[current_pos:end_pos].strip()
        if chunk:
            chunks.append(chunk)

        # Move forward with overlap
        current_pos = max(current_pos + 1, end_pos - chunk_overlap)

    return chunks


# ---------------------------------------------------------------------------
# In-memory vector store (fallback when Supabase pgvector not available)
# ---------------------------------------------------------------------------

class InMemoryVectorStore:
    """Simple in-memory vector store using cosine similarity."""

    def __init__(self):
        self._documents: List[DocumentChunk] = []

    def add(self, chunk: DocumentChunk):
        self._documents.append(chunk)

    def search(self, query_embedding: List[float], top_k: int = 5, threshold: float = 0.5) -> List[SearchResult]:
        results = []
        for doc in self._documents:
            if doc.embedding:
                sim = self._cosine_similarity(query_embedding, doc.embedding)
                if sim >= threshold:
                    results.append(SearchResult(chunk=doc, similarity=sim))
        results.sort(key=lambda r: r.similarity, reverse=True)
        return results[:top_k]

    @staticmethod
    def _cosine_similarity(a: List[float], b: List[float]) -> float:
        if len(a) != len(b):
            return 0.0
        dot = sum(x * y for x, y in zip(a, b))
        norm_a = math.sqrt(sum(x * x for x in a))
        norm_b = math.sqrt(sum(x * x for x in b))
        if norm_a == 0 or norm_b == 0:
            return 0.0
        return dot / (norm_a * norm_b)


# ---------------------------------------------------------------------------
# RAG System
# ---------------------------------------------------------------------------

class RAGSystemV3:
    """
    Retrieval Augmented Generation system.

    Supports:
    - Supabase pgvector for production
    - In-memory fallback for development
    """

    def __init__(
        self,
        embedding_provider: EmbeddingProvider,
        supabase_client: Optional[Any] = None,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
        top_k: int = 5,
        similarity_threshold: float = 0.5,
    ):
        self.embedding_provider = embedding_provider
        self.supabase = supabase_client
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.top_k = top_k
        self.similarity_threshold = similarity_threshold

        # Fallback in-memory store
        self._memory_store = InMemoryVectorStore()
        self._use_supabase = supabase_client is not None

        logger.info(f"RAGSystemV3 initialized (supabase={self._use_supabase})")

    async def add_document(
        self,
        content: str,
        source: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        document_type: str = "text",
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> List[str]:
        """Add a document to the knowledge base. Returns chunk IDs."""
        chunks = chunk_text(content, self.chunk_size, self.chunk_overlap)
        if not chunks:
            return []

        # Generate embeddings
        embeddings = await self.embedding_provider.embed_batch(chunks)

        doc_chunks = []
        for i, (text, emb) in enumerate(zip(chunks, embeddings)):
            chunk = DocumentChunk(
                content=text,
                embedding=emb,
                metadata=metadata or {},
                source=source,
                document_type=document_type,
                chunk_index=i,
                total_chunks=len(chunks),
            )
            doc_chunks.append(chunk)

        # Store
        if self._use_supabase:
            await self._store_supabase(doc_chunks, user_id, conversation_id)
        else:
            for c in doc_chunks:
                self._memory_store.add(c)

        logger.info(f"Added {len(doc_chunks)} chunks from document (source={source})")
        return [c.id for c in doc_chunks]

    async def search(
        self,
        query: str,
        top_k: Optional[int] = None,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        document_type: Optional[str] = None,
    ) -> List[SearchResult]:
        """Search for relevant documents."""
        k = top_k or self.top_k
        query_embedding = await self.embedding_provider.embed(query)

        if self._use_supabase:
            return await self._search_supabase(query_embedding, k, user_id, conversation_id, document_type)
        else:
            return self._memory_store.search(query_embedding, k, self.similarity_threshold)

    async def get_context_for_query(
        self,
        query: str,
        max_tokens: int = 2000,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Get formatted context for an LLM query."""
        results = await self.search(query, user_id=user_id, conversation_id=conversation_id)

        context_parts = []
        sources = []
        total_chars = 0

        for r in results:
            if total_chars + len(r.chunk.content) > max_tokens * 4:
                break
            context_parts.append(r.chunk.content)
            if r.chunk.source and r.chunk.source not in sources:
                sources.append(r.chunk.source)
            total_chars += len(r.chunk.content)

        return {
            "context": "\n\n---\n\n".join(context_parts),
            "sources": sources,
            "num_results": len(results),
            "total_chars": total_chars,
        }

    # -- Supabase storage ------------------------------------------------------

    async def _store_supabase(
        self, chunks: List[DocumentChunk],
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
    ):
        """Store chunks in Supabase with pgvector."""
        try:
            for chunk in chunks:
                data = {
                    "id": chunk.id,
                    "content": chunk.content,
                    "embedding": chunk.embedding,
                    "metadata": chunk.metadata,
                    "source": chunk.source,
                    "document_type": chunk.document_type,
                    "chunk_index": chunk.chunk_index,
                    "total_chunks": chunk.total_chunks,
                }
                if user_id:
                    data["user_id"] = user_id
                if conversation_id:
                    data["conversation_id"] = conversation_id

                self.supabase.table("documents").insert(data).execute()
        except Exception as e:
            logger.error(f"Supabase store failed: {e}")
            # Fallback to memory
            for c in chunks:
                self._memory_store.add(c)

    async def _search_supabase(
        self,
        query_embedding: List[float],
        top_k: int,
        user_id: Optional[str] = None,
        conversation_id: Optional[str] = None,
        document_type: Optional[str] = None,
    ) -> List[SearchResult]:
        """Search Supabase using pgvector similarity."""
        try:
            result = self.supabase.rpc("search_documents", {
                "query_embedding": query_embedding,
                "match_threshold": self.similarity_threshold,
                "match_count": top_k,
                "filter_user_id": user_id,
                "filter_conversation_id": conversation_id,
                "filter_document_type": document_type,
            }).execute()

            results = []
            for row in (result.data or []):
                chunk = DocumentChunk(
                    id=row["id"],
                    content=row["content"],
                    metadata=row.get("metadata", {}),
                    source=row.get("source"),
                    document_type=row.get("document_type", "text"),
                )
                results.append(SearchResult(chunk=chunk, similarity=row.get("similarity", 0)))
            return results

        except Exception as e:
            logger.error(f"Supabase search failed: {e}")
            return self._memory_store.search(query_embedding, top_k, self.similarity_threshold)


# ---------------------------------------------------------------------------
# Contextual RAG (conversation-aware)
# ---------------------------------------------------------------------------

class ContextualRAGV3:
    """RAG system that maintains conversation context."""

    def __init__(self, rag_system: RAGSystemV3):
        self.rag = rag_system
        self._conversation_context: Dict[str, List[str]] = {}

    async def get_enhanced_context(
        self,
        query: str,
        conversation_id: str,
        conversation_history: Optional[List[Dict]] = None,
        max_tokens: int = 3000,
    ) -> Dict[str, Any]:
        """Get context enhanced with conversation history."""
        # Get RAG context
        rag_context = await self.rag.get_context_for_query(
            query, max_tokens=max_tokens // 2, conversation_id=conversation_id,
        )

        # Build conversation context
        conv_context = ""
        if conversation_history:
            recent = conversation_history[-5:]
            conv_parts = []
            for msg in recent:
                role = msg.get("role", "user")
                content = msg.get("content", "")[:200]
                conv_parts.append(f"{role}: {content}")
            conv_context = "\n".join(conv_parts)

        return {
            "rag_context": rag_context["context"],
            "conversation_context": conv_context,
            "sources": rag_context["sources"],
            "combined_context": f"{rag_context['context']}\n\n--- Recent conversation ---\n{conv_context}" if conv_context else rag_context["context"],
        }
