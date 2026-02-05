"""
McLeuker AI - Supabase Memory Persistence
==========================================
Integrates the memory system with Supabase for persistent storage.
Syncs user_memory, saved_outputs, and file_uploads tables.
"""

import os
import json
import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from dataclasses import dataclass
import httpx

logger = logging.getLogger(__name__)

# Supabase configuration
SUPABASE_URL = os.getenv("SUPABASE_URL", os.getenv("VITE_SUPABASE_URL", ""))
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_KEY", os.getenv("SUPABASE_KEY", os.getenv("VITE_SUPABASE_PUBLISHABLE_KEY", "")))


@dataclass
class MemoryRecord:
    """A memory record for persistence"""
    user_id: str
    memory_type: str  # preference, fact, context, style, project
    key: str
    value: str
    confidence: float = 1.0
    source: Optional[str] = None
    expires_at: Optional[str] = None
    
    def to_dict(self) -> Dict:
        return {
            "user_id": self.user_id,
            "memory_type": self.memory_type,
            "key": self.key,
            "value": self.value,
            "confidence": self.confidence,
            "source": self.source,
            "expires_at": self.expires_at,
        }


class SupabaseMemoryService:
    """
    Service for persisting memory to Supabase.
    Handles user_memory, saved_outputs, and file_uploads tables.
    """
    
    def __init__(self):
        self.base_url = SUPABASE_URL
        self.api_key = SUPABASE_KEY
        self.headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        if not self.base_url or not self.api_key:
            logger.warning("Supabase credentials not configured. Memory persistence disabled.")
    
    def _get_rest_url(self, table: str) -> str:
        """Get the REST API URL for a table"""
        return f"{self.base_url}/rest/v1/{table}"
    
    async def _request(self, method: str, url: str, data: Dict = None, params: Dict = None) -> Optional[Dict]:
        """Make an async HTTP request to Supabase"""
        if not self.base_url or not self.api_key:
            return None
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.request(
                    method=method,
                    url=url,
                    headers=self.headers,
                    json=data,
                    params=params,
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    return response.json()
                elif response.status_code == 204:
                    return {"success": True}
                else:
                    logger.error(f"Supabase request failed: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Supabase request error: {e}")
            return None
    
    # =========================================================================
    # User Memory Operations
    # =========================================================================
    
    async def save_memory(self, memory: MemoryRecord) -> Optional[Dict]:
        """Save or update a memory record (upsert)"""
        url = self._get_rest_url("user_memory")
        data = memory.to_dict()
        data["updated_at"] = datetime.utcnow().isoformat()
        
        # Use upsert with conflict resolution
        headers = {**self.headers, "Prefer": "resolution=merge-duplicates,return=representation"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    return result[0] if isinstance(result, list) else result
                else:
                    logger.error(f"Failed to save memory: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error saving memory: {e}")
            return None
    
    async def save_memories_batch(self, memories: List[MemoryRecord]) -> bool:
        """Save multiple memories at once"""
        if not memories:
            return True
        
        url = self._get_rest_url("user_memory")
        data = [m.to_dict() for m in memories]
        for d in data:
            d["updated_at"] = datetime.utcnow().isoformat()
        
        headers = {**self.headers, "Prefer": "resolution=merge-duplicates"}
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    url,
                    headers=headers,
                    json=data,
                    timeout=30.0
                )
                return response.status_code in [200, 201]
        except Exception as e:
            logger.error(f"Error saving memories batch: {e}")
            return False
    
    async def get_user_memories(self, user_id: str, memory_type: str = None) -> List[Dict]:
        """Get all memories for a user"""
        url = self._get_rest_url("user_memory")
        params = {"user_id": f"eq.{user_id}", "order": "updated_at.desc"}
        
        if memory_type:
            params["memory_type"] = f"eq.{memory_type}"
        
        result = await self._request("GET", url, params=params)
        return result if isinstance(result, list) else []
    
    async def get_memory(self, user_id: str, key: str, memory_type: str = None) -> Optional[Dict]:
        """Get a specific memory by key"""
        url = self._get_rest_url("user_memory")
        params = {
            "user_id": f"eq.{user_id}",
            "key": f"eq.{key}",
            "limit": "1"
        }
        
        if memory_type:
            params["memory_type"] = f"eq.{memory_type}"
        
        result = await self._request("GET", url, params=params)
        return result[0] if result and len(result) > 0 else None
    
    async def delete_memory(self, user_id: str, memory_id: str) -> bool:
        """Delete a memory record"""
        url = self._get_rest_url("user_memory")
        params = {"id": f"eq.{memory_id}", "user_id": f"eq.{user_id}"}
        
        result = await self._request("DELETE", url, params=params)
        return result is not None
    
    async def get_memories_for_ai_context(self, user_id: str) -> str:
        """Get formatted memories for AI context injection"""
        memories = await self.get_user_memories(user_id)
        
        if not memories:
            return ""
        
        # Group by type
        grouped = {}
        for m in memories:
            mtype = m.get("memory_type", "other")
            if mtype not in grouped:
                grouped[mtype] = []
            grouped[mtype].append(m)
        
        # Format for AI
        context_parts = ["User Context:"]
        
        type_labels = {
            "preference": "Preferences",
            "fact": "Known Facts",
            "context": "Context",
            "style": "Communication Style",
            "project": "Current Projects"
        }
        
        for mtype, label in type_labels.items():
            if mtype in grouped and grouped[mtype]:
                context_parts.append(f"\n{label}:")
                for m in grouped[mtype][:10]:  # Limit to 10 per type
                    context_parts.append(f"- {m['key']}: {m['value']}")
        
        return "\n".join(context_parts)
    
    # =========================================================================
    # Saved Outputs Operations
    # =========================================================================
    
    async def save_output(
        self,
        user_id: str,
        title: str,
        content: str,
        content_type: str = "text",
        conversation_id: str = None,
        message_id: str = None,
        tags: List[str] = None,
        metadata: Dict = None
    ) -> Optional[Dict]:
        """Save an AI-generated output"""
        url = self._get_rest_url("saved_outputs")
        data = {
            "user_id": user_id,
            "title": title,
            "content": content,
            "content_type": content_type,
            "conversation_id": conversation_id,
            "message_id": message_id,
            "tags": tags or [],
            "metadata": metadata or {},
            "is_public": False
        }
        
        return await self._request("POST", url, data=data)
    
    async def get_saved_outputs(self, user_id: str, content_type: str = None) -> List[Dict]:
        """Get saved outputs for a user"""
        url = self._get_rest_url("saved_outputs")
        params = {"user_id": f"eq.{user_id}", "order": "created_at.desc"}
        
        if content_type:
            params["content_type"] = f"eq.{content_type}"
        
        result = await self._request("GET", url, params=params)
        return result if isinstance(result, list) else []
    
    async def delete_saved_output(self, user_id: str, output_id: str) -> bool:
        """Delete a saved output"""
        url = self._get_rest_url("saved_outputs")
        params = {"id": f"eq.{output_id}", "user_id": f"eq.{user_id}"}
        
        result = await self._request("DELETE", url, params=params)
        return result is not None
    
    # =========================================================================
    # File Uploads Operations
    # =========================================================================
    
    async def track_file_upload(
        self,
        user_id: str,
        file_name: str,
        file_type: str,
        file_size: int,
        storage_path: str,
        public_url: str = None,
        mime_type: str = None,
        conversation_id: str = None,
        metadata: Dict = None
    ) -> Optional[Dict]:
        """Track a file upload in the database"""
        url = self._get_rest_url("file_uploads")
        data = {
            "user_id": user_id,
            "file_name": file_name,
            "file_type": file_type,
            "file_size": file_size,
            "storage_path": storage_path,
            "public_url": public_url,
            "mime_type": mime_type,
            "conversation_id": conversation_id,
            "metadata": metadata or {}
        }
        
        return await self._request("POST", url, data=data)
    
    async def get_file_uploads(self, user_id: str, conversation_id: str = None) -> List[Dict]:
        """Get file uploads for a user"""
        url = self._get_rest_url("file_uploads")
        params = {"user_id": f"eq.{user_id}", "order": "created_at.desc"}
        
        if conversation_id:
            params["conversation_id"] = f"eq.{conversation_id}"
        
        result = await self._request("GET", url, params=params)
        return result if isinstance(result, list) else []
    
    async def delete_file_upload(self, user_id: str, upload_id: str) -> bool:
        """Delete a file upload record"""
        url = self._get_rest_url("file_uploads")
        params = {"id": f"eq.{upload_id}", "user_id": f"eq.{user_id}"}
        
        result = await self._request("DELETE", url, params=params)
        return result is not None
    
    # =========================================================================
    # API Usage Tracking
    # =========================================================================
    
    async def track_api_usage(
        self,
        user_id: str,
        api_name: str,
        endpoint: str = None,
        tokens_used: int = 0,
        cost_cents: int = 0,
        metadata: Dict = None
    ) -> Optional[Dict]:
        """Track API usage for billing"""
        url = self._get_rest_url("api_usage")
        data = {
            "user_id": user_id,
            "api_name": api_name,
            "endpoint": endpoint,
            "tokens_used": tokens_used,
            "cost_cents": cost_cents,
            "request_metadata": metadata or {}
        }
        
        return await self._request("POST", url, data=data)
    
    async def get_api_usage(self, user_id: str, days: int = 30) -> List[Dict]:
        """Get API usage for a user"""
        url = self._get_rest_url("api_usage")
        since = (datetime.utcnow() - timedelta(days=days)).isoformat()
        params = {
            "user_id": f"eq.{user_id}",
            "created_at": f"gte.{since}",
            "order": "created_at.desc"
        }
        
        result = await self._request("GET", url, params=params)
        return result if isinstance(result, list) else []
    
    # =========================================================================
    # User Profile Operations
    # =========================================================================
    
    async def get_user(self, user_id: str) -> Optional[Dict]:
        """Get user profile from users table"""
        url = self._get_rest_url("users")
        params = {"id": f"eq.{user_id}", "limit": "1"}
        
        result = await self._request("GET", url, params=params)
        return result[0] if result and len(result) > 0 else None
    
    async def update_user(self, user_id: str, updates: Dict) -> Optional[Dict]:
        """Update user profile"""
        url = self._get_rest_url("users")
        updates["updated_at"] = datetime.utcnow().isoformat()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    url,
                    headers=self.headers,
                    json=updates,
                    params={"id": f"eq.{user_id}"},
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    return result[0] if isinstance(result, list) else result
                else:
                    logger.error(f"Failed to update user: {response.status_code} - {response.text}")
                    return None
        except Exception as e:
            logger.error(f"Error updating user: {e}")
            return None
    
    # =========================================================================
    # Conversation Operations
    # =========================================================================
    
    async def get_conversation(self, conversation_id: str) -> Optional[Dict]:
        """Get a conversation by ID"""
        url = self._get_rest_url("conversations")
        params = {"id": f"eq.{conversation_id}", "limit": "1"}
        
        result = await self._request("GET", url, params=params)
        return result[0] if result and len(result) > 0 else None
    
    async def update_conversation(self, conversation_id: str, updates: Dict) -> Optional[Dict]:
        """Update a conversation"""
        url = self._get_rest_url("conversations")
        updates["updated_at"] = datetime.utcnow().isoformat()
        
        try:
            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    url,
                    headers=self.headers,
                    json=updates,
                    params={"id": f"eq.{conversation_id}"},
                    timeout=30.0
                )
                
                if response.status_code in [200, 201]:
                    result = response.json()
                    return result[0] if isinstance(result, list) else result
                else:
                    logger.error(f"Failed to update conversation: {response.status_code}")
                    return None
        except Exception as e:
            logger.error(f"Error updating conversation: {e}")
            return None


# Singleton instance
_memory_service: Optional[SupabaseMemoryService] = None


def get_supabase_memory_service() -> SupabaseMemoryService:
    """Get the singleton memory service instance"""
    global _memory_service
    if _memory_service is None:
        _memory_service = SupabaseMemoryService()
    return _memory_service
