"""
V3.1 Database Layer
Supabase integration for users, credits, and conversations.
"""

from src.database.supabase_client import (
    SupabaseClient,
    User,
    CreditTransaction,
    Conversation,
    db,
    SUPABASE_SCHEMA
)

__all__ = [
    "SupabaseClient",
    "User",
    "CreditTransaction", 
    "Conversation",
    "db",
    "SUPABASE_SCHEMA"
]
