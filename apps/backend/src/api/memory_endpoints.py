"""
McLeuker AI - Memory API Endpoints
===================================
API endpoints for managing user memory, saved outputs, and file uploads.
Integrates with Supabase for persistent storage.
"""

import os
import json
import logging
from datetime import datetime
from typing import Optional, Dict, Any, List

from fastapi import APIRouter, HTTPException, Request, UploadFile, File, Form
from pydantic import BaseModel, Field

from ..core.supabase_memory import (
    get_supabase_memory_service,
    MemoryRecord,
    SupabaseMemoryService
)

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/memory", tags=["memory"])


# =============================================================================
# Request/Response Models
# =============================================================================

class SaveMemoryRequest(BaseModel):
    user_id: str
    memory_type: str = "preference"  # preference, fact, context, style, project
    key: str
    value: str
    confidence: float = 1.0
    source: Optional[str] = None
    expires_at: Optional[str] = None


class SaveMemoriesBatchRequest(BaseModel):
    user_id: str
    memories: List[Dict]


class SaveOutputRequest(BaseModel):
    user_id: str
    title: str
    content: str
    content_type: str = "text"  # text, report, analysis, code, image, document
    conversation_id: Optional[str] = None
    message_id: Optional[str] = None
    tags: List[str] = Field(default_factory=list)
    metadata: Dict = Field(default_factory=dict)


class ExtractMemoryRequest(BaseModel):
    user_id: str
    conversation_content: str
    extract_preferences: bool = True
    extract_facts: bool = True


# =============================================================================
# Memory Endpoints
# =============================================================================

@router.post("/save")
async def save_memory(request: SaveMemoryRequest):
    """Save a single memory record"""
    try:
        service = get_supabase_memory_service()
        
        memory = MemoryRecord(
            user_id=request.user_id,
            memory_type=request.memory_type,
            key=request.key,
            value=request.value,
            confidence=request.confidence,
            source=request.source,
            expires_at=request.expires_at
        )
        
        result = await service.save_memory(memory)
        
        if result:
            return {"success": True, "memory": result}
        else:
            raise HTTPException(status_code=500, detail="Failed to save memory")
    
    except Exception as e:
        logger.error(f"Error saving memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/save-batch")
async def save_memories_batch(request: SaveMemoriesBatchRequest):
    """Save multiple memories at once"""
    try:
        service = get_supabase_memory_service()
        
        memories = [
            MemoryRecord(
                user_id=request.user_id,
                memory_type=m.get("memory_type", "preference"),
                key=m["key"],
                value=m["value"],
                confidence=m.get("confidence", 1.0),
                source=m.get("source"),
                expires_at=m.get("expires_at")
            )
            for m in request.memories
        ]
        
        success = await service.save_memories_batch(memories)
        
        return {"success": success, "count": len(memories)}
    
    except Exception as e:
        logger.error(f"Error saving memories batch: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/list/{user_id}")
async def get_memories(user_id: str, memory_type: Optional[str] = None):
    """Get all memories for a user"""
    try:
        service = get_supabase_memory_service()
        memories = await service.get_user_memories(user_id, memory_type)
        
        return {"success": True, "memories": memories, "count": len(memories)}
    
    except Exception as e:
        logger.error(f"Error getting memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/get/{user_id}/{key}")
async def get_memory(user_id: str, key: str, memory_type: Optional[str] = None):
    """Get a specific memory by key"""
    try:
        service = get_supabase_memory_service()
        memory = await service.get_memory(user_id, key, memory_type)
        
        if memory:
            return {"success": True, "memory": memory}
        else:
            return {"success": False, "memory": None}
    
    except Exception as e:
        logger.error(f"Error getting memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/delete/{user_id}/{memory_id}")
async def delete_memory(user_id: str, memory_id: str):
    """Delete a memory record"""
    try:
        service = get_supabase_memory_service()
        success = await service.delete_memory(user_id, memory_id)
        
        return {"success": success}
    
    except Exception as e:
        logger.error(f"Error deleting memory: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/context/{user_id}")
async def get_ai_context(user_id: str):
    """Get formatted memory context for AI"""
    try:
        service = get_supabase_memory_service()
        context = await service.get_memories_for_ai_context(user_id)
        
        return {"success": True, "context": context}
    
    except Exception as e:
        logger.error(f"Error getting AI context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Saved Outputs Endpoints
# =============================================================================

@router.post("/outputs/save")
async def save_output(request: SaveOutputRequest):
    """Save an AI-generated output"""
    try:
        service = get_supabase_memory_service()
        
        result = await service.save_output(
            user_id=request.user_id,
            title=request.title,
            content=request.content,
            content_type=request.content_type,
            conversation_id=request.conversation_id,
            message_id=request.message_id,
            tags=request.tags,
            metadata=request.metadata
        )
        
        if result:
            return {"success": True, "output": result}
        else:
            raise HTTPException(status_code=500, detail="Failed to save output")
    
    except Exception as e:
        logger.error(f"Error saving output: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/outputs/list/{user_id}")
async def get_saved_outputs(user_id: str, content_type: Optional[str] = None):
    """Get saved outputs for a user"""
    try:
        service = get_supabase_memory_service()
        outputs = await service.get_saved_outputs(user_id, content_type)
        
        return {"success": True, "outputs": outputs, "count": len(outputs)}
    
    except Exception as e:
        logger.error(f"Error getting saved outputs: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/outputs/delete/{user_id}/{output_id}")
async def delete_saved_output(user_id: str, output_id: str):
    """Delete a saved output"""
    try:
        service = get_supabase_memory_service()
        success = await service.delete_saved_output(user_id, output_id)
        
        return {"success": success}
    
    except Exception as e:
        logger.error(f"Error deleting saved output: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# File Uploads Endpoints
# =============================================================================

@router.post("/files/track")
async def track_file_upload(
    user_id: str = Form(...),
    file_name: str = Form(...),
    file_type: str = Form(...),
    file_size: int = Form(...),
    storage_path: str = Form(...),
    public_url: Optional[str] = Form(None),
    mime_type: Optional[str] = Form(None),
    conversation_id: Optional[str] = Form(None)
):
    """Track a file upload in the database"""
    try:
        service = get_supabase_memory_service()
        
        result = await service.track_file_upload(
            user_id=user_id,
            file_name=file_name,
            file_type=file_type,
            file_size=file_size,
            storage_path=storage_path,
            public_url=public_url,
            mime_type=mime_type,
            conversation_id=conversation_id
        )
        
        if result:
            return {"success": True, "upload": result}
        else:
            raise HTTPException(status_code=500, detail="Failed to track file upload")
    
    except Exception as e:
        logger.error(f"Error tracking file upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/files/list/{user_id}")
async def get_file_uploads(user_id: str, conversation_id: Optional[str] = None):
    """Get file uploads for a user"""
    try:
        service = get_supabase_memory_service()
        uploads = await service.get_file_uploads(user_id, conversation_id)
        
        return {"success": True, "uploads": uploads, "count": len(uploads)}
    
    except Exception as e:
        logger.error(f"Error getting file uploads: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/files/delete/{user_id}/{upload_id}")
async def delete_file_upload(user_id: str, upload_id: str):
    """Delete a file upload record"""
    try:
        service = get_supabase_memory_service()
        success = await service.delete_file_upload(user_id, upload_id)
        
        return {"success": success}
    
    except Exception as e:
        logger.error(f"Error deleting file upload: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# API Usage Tracking Endpoints
# =============================================================================

@router.post("/usage/track")
async def track_api_usage(
    user_id: str,
    api_name: str,
    endpoint: Optional[str] = None,
    tokens_used: int = 0,
    cost_cents: int = 0,
    metadata: Dict = None
):
    """Track API usage for billing"""
    try:
        service = get_supabase_memory_service()
        
        result = await service.track_api_usage(
            user_id=user_id,
            api_name=api_name,
            endpoint=endpoint,
            tokens_used=tokens_used,
            cost_cents=cost_cents,
            metadata=metadata or {}
        )
        
        if result:
            return {"success": True, "usage": result}
        else:
            raise HTTPException(status_code=500, detail="Failed to track API usage")
    
    except Exception as e:
        logger.error(f"Error tracking API usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/usage/list/{user_id}")
async def get_api_usage(user_id: str, days: int = 30):
    """Get API usage for a user"""
    try:
        service = get_supabase_memory_service()
        usage = await service.get_api_usage(user_id, days)
        
        # Calculate totals
        total_tokens = sum(u.get("tokens_used", 0) for u in usage)
        total_cost = sum(u.get("cost_cents", 0) for u in usage)
        
        return {
            "success": True,
            "usage": usage,
            "count": len(usage),
            "total_tokens": total_tokens,
            "total_cost_cents": total_cost
        }
    
    except Exception as e:
        logger.error(f"Error getting API usage: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# =============================================================================
# Memory Extraction (AI-powered)
# =============================================================================

@router.post("/extract")
async def extract_memories_from_conversation(request: ExtractMemoryRequest):
    """
    Extract memories from conversation content using AI.
    This analyzes the conversation and identifies:
    - User preferences
    - Facts about the user
    - Context for future conversations
    """
    try:
        # This would use an LLM to extract structured information
        # For now, return a placeholder
        
        extracted = {
            "preferences": [],
            "facts": [],
            "context": []
        }
        
        # Simple keyword-based extraction (would be replaced with LLM)
        content_lower = request.conversation_content.lower()
        
        # Extract preferences
        if request.extract_preferences:
            if "prefer" in content_lower or "like" in content_lower:
                extracted["preferences"].append({
                    "key": "detected_preference",
                    "value": "User expressed preferences in conversation",
                    "confidence": 0.7
                })
        
        # Extract facts
        if request.extract_facts:
            if "i am" in content_lower or "i work" in content_lower or "my name" in content_lower:
                extracted["facts"].append({
                    "key": "detected_fact",
                    "value": "User shared personal information",
                    "confidence": 0.8
                })
        
        return {
            "success": True,
            "extracted": extracted,
            "message": "Memory extraction completed. Use /memory/save-batch to persist."
        }
    
    except Exception as e:
        logger.error(f"Error extracting memories: {e}")
        raise HTTPException(status_code=500, detail=str(e))
