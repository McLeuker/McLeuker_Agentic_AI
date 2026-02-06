"""
V3.1 Supabase Database Integration
Handles users, credits, conversations, and usage tracking.
"""

import os
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

# Supabase client will be initialized if available
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None

from src.config.settings import settings


@dataclass
class User:
    """User model."""
    id: str
    email: str
    name: Optional[str]
    credits_balance: int
    plan: str  # 'free', 'pro', 'enterprise'
    created_at: str
    updated_at: str


@dataclass
class CreditTransaction:
    """Credit transaction model."""
    id: str
    user_id: str
    amount: int  # positive for add, negative for use
    type: str  # 'purchase', 'usage', 'bonus', 'refund'
    description: str
    session_id: Optional[str]
    created_at: str


@dataclass
class Conversation:
    """Conversation model."""
    id: str
    user_id: str
    title: Optional[str]
    messages: List[Dict]
    credits_used: int
    created_at: str
    updated_at: str


class SupabaseClient:
    """
    Supabase database client for McLeuker Fashion AI.
    Manages users, credits, and conversations.
    """
    
    def __init__(self):
        self.client: Optional[Client] = None
        self.enabled = False
        
        if SUPABASE_AVAILABLE and settings.SUPABASE_URL and settings.SUPABASE_KEY:
            try:
                self.client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
                self.enabled = True
                print("✅ Supabase client initialized")
            except Exception as e:
                print(f"⚠️ Supabase initialization failed: {e}")
    
    # =========================================================================
    # User Management
    # =========================================================================
    
    async def get_user(self, user_id: str) -> Optional[User]:
        """Get user by ID."""
        if not self.enabled:
            return self._mock_user(user_id)
        
        try:
            result = self.client.table("users").select("*").eq("id", user_id).single().execute()
            if result.data:
                return User(**result.data)
        except Exception as e:
            print(f"Error getting user: {e}")
        
        return None
    
    async def create_user(self, user_id: str, email: str, name: Optional[str] = None) -> Optional[User]:
        """Create a new user with default credits."""
        if not self.enabled:
            return self._mock_user(user_id)
        
        try:
            user_data = {
                "id": user_id,
                "email": email,
                "name": name,
                "credits_balance": 100,  # Default free credits
                "plan": "free",
                "created_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            result = self.client.table("users").insert(user_data).execute()
            if result.data:
                return User(**result.data[0])
        except Exception as e:
            print(f"Error creating user: {e}")
        
        return None
    
    async def get_or_create_user(self, user_id: str, email: str = None) -> User:
        """Get existing user or create new one."""
        user = await self.get_user(user_id)
        if not user and email:
            user = await self.create_user(user_id, email)
        if not user:
            user = self._mock_user(user_id)
        return user
    
    def _mock_user(self, user_id: str) -> User:
        """Return a mock user when Supabase is not available."""
        return User(
            id=user_id,
            email=f"{user_id}@mock.com",
            name=None,
            credits_balance=100,
            plan="free",
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat()
        )
    
    # =========================================================================
    # Credit Management
    # =========================================================================
    
    async def get_credits(self, user_id: str) -> int:
        """Get user's credit balance."""
        if not self.enabled:
            return 100  # Mock credits
        
        try:
            result = self.client.table("users").select("credits_balance").eq("id", user_id).single().execute()
            if result.data:
                return result.data.get("credits_balance", 0)
        except Exception as e:
            print(f"Error getting credits: {e}")
        
        return 0
    
    async def use_credits(self, user_id: str, amount: int, description: str, 
                          session_id: Optional[str] = None) -> bool:
        """Deduct credits from user's balance."""
        if not self.enabled:
            return True  # Mock success
        
        try:
            # Get current balance
            current = await self.get_credits(user_id)
            if current < amount:
                return False  # Insufficient credits
            
            # Update balance
            new_balance = current - amount
            self.client.table("users").update({
                "credits_balance": new_balance,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            # Log transaction
            await self._log_credit_transaction(user_id, -amount, "usage", description, session_id)
            
            return True
        except Exception as e:
            print(f"Error using credits: {e}")
            return False
    
    async def add_credits(self, user_id: str, amount: int, type: str = "purchase",
                          description: str = "Credit purchase") -> bool:
        """Add credits to user's balance."""
        if not self.enabled:
            return True  # Mock success
        
        try:
            current = await self.get_credits(user_id)
            new_balance = current + amount
            
            self.client.table("users").update({
                "credits_balance": new_balance,
                "updated_at": datetime.utcnow().isoformat()
            }).eq("id", user_id).execute()
            
            await self._log_credit_transaction(user_id, amount, type, description)
            
            return True
        except Exception as e:
            print(f"Error adding credits: {e}")
            return False
    
    async def _log_credit_transaction(self, user_id: str, amount: int, type: str,
                                       description: str, session_id: Optional[str] = None):
        """Log a credit transaction."""
        if not self.enabled:
            return
        
        try:
            transaction_data = {
                "user_id": user_id,
                "amount": amount,
                "type": type,
                "description": description,
                "session_id": session_id,
                "created_at": datetime.utcnow().isoformat()
            }
            self.client.table("credit_transactions").insert(transaction_data).execute()
        except Exception as e:
            print(f"Error logging transaction: {e}")
    
    # =========================================================================
    # Conversation Management
    # =========================================================================
    
    async def save_conversation(self, session_id: str, user_id: str, 
                                 messages: List[Dict], credits_used: int) -> bool:
        """Save or update a conversation."""
        if not self.enabled:
            return True  # Mock success
        
        try:
            # Check if conversation exists
            existing = self.client.table("conversations").select("id").eq("id", session_id).execute()
            
            conversation_data = {
                "id": session_id,
                "user_id": user_id,
                "messages": messages,
                "credits_used": credits_used,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if existing.data:
                # Update existing
                self.client.table("conversations").update(conversation_data).eq("id", session_id).execute()
            else:
                # Create new
                conversation_data["created_at"] = datetime.utcnow().isoformat()
                self.client.table("conversations").insert(conversation_data).execute()
            
            return True
        except Exception as e:
            print(f"Error saving conversation: {e}")
            return False
    
    async def get_conversation(self, session_id: str) -> Optional[Conversation]:
        """Get a conversation by session ID."""
        if not self.enabled:
            return None
        
        try:
            result = self.client.table("conversations").select("*").eq("id", session_id).single().execute()
            if result.data:
                return Conversation(**result.data)
        except Exception as e:
            print(f"Error getting conversation: {e}")
        
        return None
    
    async def get_user_conversations(self, user_id: str, limit: int = 20) -> List[Conversation]:
        """Get user's recent conversations."""
        if not self.enabled:
            return []
        
        try:
            result = self.client.table("conversations").select("*").eq("user_id", user_id).order("updated_at", desc=True).limit(limit).execute()
            if result.data:
                return [Conversation(**c) for c in result.data]
        except Exception as e:
            print(f"Error getting conversations: {e}")
        
        return []
    
    # =========================================================================
    # Usage Tracking
    # =========================================================================
    
    async def log_usage(self, user_id: str, session_id: str, action: str,
                        provider: str, tokens_used: int = 0, cost: float = 0.0):
        """Log API usage for analytics."""
        if not self.enabled:
            return
        
        try:
            usage_data = {
                "user_id": user_id,
                "session_id": session_id,
                "action": action,
                "provider": provider,
                "tokens_used": tokens_used,
                "cost": cost,
                "created_at": datetime.utcnow().isoformat()
            }
            self.client.table("usage_logs").insert(usage_data).execute()
        except Exception as e:
            print(f"Error logging usage: {e}")


# Global instance
db = SupabaseClient()


# ============================================================================
# SQL Schema for Supabase (Run this in Supabase SQL Editor)
# ============================================================================

SUPABASE_SCHEMA = """
-- McLeuker Fashion AI V3.1 Database Schema

-- Users table
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    email TEXT UNIQUE NOT NULL,
    name TEXT,
    credits_balance INTEGER DEFAULT 100,
    plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'enterprise')),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Credit transactions table
CREATE TABLE IF NOT EXISTS credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('purchase', 'usage', 'bonus', 'refund')),
    description TEXT,
    session_id TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Conversations table
CREATE TABLE IF NOT EXISTS conversations (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    title TEXT,
    messages JSONB DEFAULT '[]'::jsonb,
    credits_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Usage logs table
CREATE TABLE IF NOT EXISTS usage_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    session_id TEXT,
    action TEXT NOT NULL,
    provider TEXT NOT NULL,
    tokens_used INTEGER DEFAULT 0,
    cost DECIMAL(10, 6) DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_session_id ON usage_logs(session_id);

-- Row Level Security (RLS)
ALTER TABLE users ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;

-- Policies (adjust based on your auth setup)
CREATE POLICY "Users can view own data" ON users FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own data" ON users FOR UPDATE USING (auth.uid() = id);

CREATE POLICY "Users can view own transactions" ON credit_transactions FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can view own conversations" ON conversations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own conversations" ON conversations FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own conversations" ON conversations FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own usage" ON usage_logs FOR SELECT USING (auth.uid() = user_id);
"""
