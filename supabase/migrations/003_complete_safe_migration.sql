-- McLeuker AI Platform - Complete Safe Migration Script
-- Run this in Supabase SQL Editor

-- ============================================================================
-- PART 1: CREATE ALL TABLES (IF NOT EXISTS)
-- ============================================================================

-- 1. USERS TABLE (likely exists)
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    name TEXT,
    email TEXT NOT NULL,
    profile_image TEXT,
    company TEXT,
    role TEXT,
    subscription_plan TEXT DEFAULT 'free',
    credit_balance INTEGER DEFAULT 50,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_login_at TIMESTAMPTZ,
    auth_provider TEXT DEFAULT 'email',
    preferences JSONB DEFAULT '{}'::jsonb,
    onboarding_completed BOOLEAN DEFAULT FALSE
);

-- 2. PROFILES TABLE (likely exists)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    full_name TEXT,
    email TEXT,
    avatar_url TEXT,
    bio TEXT,
    website TEXT,
    company TEXT,
    job_title TEXT,
    location TEXT,
    timezone TEXT DEFAULT 'UTC',
    language TEXT DEFAULT 'en',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 3. CONVERSATIONS TABLE (likely exists)
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    session_id TEXT NOT NULL,
    title TEXT DEFAULT 'New Chat',
    sector TEXT DEFAULT 'all',
    is_archived BOOLEAN DEFAULT FALSE,
    is_pinned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 4. CHAT_MESSAGES TABLE (likely exists)
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    model_used TEXT,
    credits_used INTEGER DEFAULT 0,
    is_favorite BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    attachments JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 5. SUBSCRIPTIONS TABLE
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE,
    plan TEXT DEFAULT 'free',
    status TEXT DEFAULT 'active',
    credits_remaining INTEGER DEFAULT 50,
    credits_monthly INTEGER DEFAULT 50,
    stripe_customer_id TEXT,
    stripe_subscription_id TEXT,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 6. CREDIT_TRANSACTIONS TABLE
CREATE TABLE IF NOT EXISTS public.credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    amount INTEGER NOT NULL,
    type TEXT NOT NULL,
    description TEXT,
    balance_after INTEGER NOT NULL,
    conversation_id UUID,
    message_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. SUPPORT_REQUESTS TABLE
CREATE TABLE IF NOT EXISTS public.support_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    type TEXT NOT NULL,
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT DEFAULT 'open',
    priority TEXT DEFAULT 'normal',
    assigned_to TEXT,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 8. WORKSPACES TABLE
CREATE TABLE IF NOT EXISTS public.workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    owner_id UUID NOT NULL,
    logo_url TEXT,
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 9. WORKSPACE_MEMBERS TABLE
CREATE TABLE IF NOT EXISTS public.workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role TEXT DEFAULT 'member',
    invited_by UUID,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

-- 10. USER_MEMORY TABLE - Long-term memory for AI personalization
CREATE TABLE IF NOT EXISTS public.user_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    memory_type TEXT NOT NULL,
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    source TEXT,
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, memory_type, key)
);

-- 11. SAVED_OUTPUTS TABLE - Saved AI-generated content
CREATE TABLE IF NOT EXISTS public.saved_outputs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    conversation_id UUID,
    message_id UUID,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_type TEXT DEFAULT 'text',
    tags TEXT[] DEFAULT '{}',
    is_public BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- 12. FILE_UPLOADS TABLE - Track uploaded files
CREATE TABLE IF NOT EXISTS public.file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    conversation_id UUID,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    storage_path TEXT NOT NULL,
    public_url TEXT,
    mime_type TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 13. API_USAGE TABLE - Track API usage for billing
CREATE TABLE IF NOT EXISTS public.api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    api_name TEXT NOT NULL,
    endpoint TEXT,
    tokens_used INTEGER DEFAULT 0,
    cost_cents INTEGER DEFAULT 0,
    request_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 14. USER_SESSIONS TABLE - Track active sessions
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
    session_token TEXT NOT NULL UNIQUE,
    device_info JSONB DEFAULT '{}'::jsonb,
    ip_address TEXT,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- PART 2: ADD MISSING COLUMNS TO EXISTING TABLES
-- ============================================================================

-- Add missing columns to users table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'company') THEN
        ALTER TABLE public.users ADD COLUMN company TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'role') THEN
        ALTER TABLE public.users ADD COLUMN role TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'preferences') THEN
        ALTER TABLE public.users ADD COLUMN preferences JSONB DEFAULT '{}'::jsonb;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'onboarding_completed') THEN
        ALTER TABLE public.users ADD COLUMN onboarding_completed BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

-- Add missing columns to profiles table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'avatar_url') THEN
        ALTER TABLE public.profiles ADD COLUMN avatar_url TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'bio') THEN
        ALTER TABLE public.profiles ADD COLUMN bio TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'website') THEN
        ALTER TABLE public.profiles ADD COLUMN website TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'company') THEN
        ALTER TABLE public.profiles ADD COLUMN company TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'job_title') THEN
        ALTER TABLE public.profiles ADD COLUMN job_title TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'location') THEN
        ALTER TABLE public.profiles ADD COLUMN location TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'timezone') THEN
        ALTER TABLE public.profiles ADD COLUMN timezone TEXT DEFAULT 'UTC';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'language') THEN
        ALTER TABLE public.profiles ADD COLUMN language TEXT DEFAULT 'en';
    END IF;
END $$;

-- Add missing columns to conversations table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'conversations' AND column_name = 'sector') THEN
        ALTER TABLE public.conversations ADD COLUMN sector TEXT DEFAULT 'all';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'conversations' AND column_name = 'is_archived') THEN
        ALTER TABLE public.conversations ADD COLUMN is_archived BOOLEAN DEFAULT FALSE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'conversations' AND column_name = 'is_pinned') THEN
        ALTER TABLE public.conversations ADD COLUMN is_pinned BOOLEAN DEFAULT FALSE;
    END IF;
END $$;

-- Add missing columns to chat_messages table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'chat_messages' AND column_name = 'attachments') THEN
        ALTER TABLE public.chat_messages ADD COLUMN attachments JSONB DEFAULT '[]'::jsonb;
    END IF;
END $$;

-- ============================================================================
-- PART 3: CREATE INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_users_user_id ON public.users(user_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);
CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON public.profiles(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON public.conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON public.conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON public.conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id ON public.chat_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON public.chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON public.chat_messages(created_at);
CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON public.credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created_at ON public.credit_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_support_requests_user_id ON public.support_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_support_requests_status ON public.support_requests(status);
CREATE INDEX IF NOT EXISTS idx_workspaces_owner_id ON public.workspaces(owner_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON public.workspaces(slug);
CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace_id ON public.workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_user_id ON public.workspace_members(user_id);
CREATE INDEX IF NOT EXISTS idx_user_memory_user_id ON public.user_memory(user_id);
CREATE INDEX IF NOT EXISTS idx_user_memory_type ON public.user_memory(memory_type);
CREATE INDEX IF NOT EXISTS idx_saved_outputs_user_id ON public.saved_outputs(user_id);
CREATE INDEX IF NOT EXISTS idx_file_uploads_user_id ON public.file_uploads(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON public.api_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON public.api_usage(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_token ON public.user_sessions(session_token);

-- ============================================================================
-- PART 4: ENABLE ROW LEVEL SECURITY
-- ============================================================================

ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_outputs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.file_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- PART 5: CREATE RLS POLICIES
-- ============================================================================

-- Users policies
DROP POLICY IF EXISTS "Users can view own data" ON public.users;
CREATE POLICY "Users can view own data" ON public.users FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can update own data" ON public.users;
CREATE POLICY "Users can update own data" ON public.users FOR UPDATE USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own data" ON public.users;
CREATE POLICY "Users can insert own data" ON public.users FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Profiles policies
DROP POLICY IF EXISTS "Profiles viewable by owner" ON public.profiles;
CREATE POLICY "Profiles viewable by owner" ON public.profiles FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Profiles editable by owner" ON public.profiles;
CREATE POLICY "Profiles editable by owner" ON public.profiles FOR UPDATE USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Profiles insertable by owner" ON public.profiles;
CREATE POLICY "Profiles insertable by owner" ON public.profiles FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Conversations policies
DROP POLICY IF EXISTS "Conversations viewable by owner" ON public.conversations;
CREATE POLICY "Conversations viewable by owner" ON public.conversations FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Conversations manageable by owner" ON public.conversations;
CREATE POLICY "Conversations manageable by owner" ON public.conversations FOR ALL USING (auth.uid() = user_id);

-- Chat messages policies
DROP POLICY IF EXISTS "Messages viewable by owner" ON public.chat_messages;
CREATE POLICY "Messages viewable by owner" ON public.chat_messages FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Messages insertable by owner" ON public.chat_messages;
CREATE POLICY "Messages insertable by owner" ON public.chat_messages FOR INSERT WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "Messages updatable by owner" ON public.chat_messages;
CREATE POLICY "Messages updatable by owner" ON public.chat_messages FOR UPDATE USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Messages deletable by owner" ON public.chat_messages;
CREATE POLICY "Messages deletable by owner" ON public.chat_messages FOR DELETE USING (auth.uid() = user_id);

-- Subscriptions policies
DROP POLICY IF EXISTS "Subscriptions viewable by owner" ON public.subscriptions;
CREATE POLICY "Subscriptions viewable by owner" ON public.subscriptions FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Subscriptions updatable by owner" ON public.subscriptions;
CREATE POLICY "Subscriptions updatable by owner" ON public.subscriptions FOR UPDATE USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Subscriptions insertable by owner" ON public.subscriptions;
CREATE POLICY "Subscriptions insertable by owner" ON public.subscriptions FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Credit transactions policies
DROP POLICY IF EXISTS "Credit transactions viewable by owner" ON public.credit_transactions;
CREATE POLICY "Credit transactions viewable by owner" ON public.credit_transactions FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Credit transactions insertable by owner" ON public.credit_transactions;
CREATE POLICY "Credit transactions insertable by owner" ON public.credit_transactions FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Support requests policies
DROP POLICY IF EXISTS "Support requests viewable by owner" ON public.support_requests;
CREATE POLICY "Support requests viewable by owner" ON public.support_requests FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Support requests manageable by owner" ON public.support_requests;
CREATE POLICY "Support requests manageable by owner" ON public.support_requests FOR ALL USING (auth.uid() = user_id);

-- Workspaces policies
DROP POLICY IF EXISTS "Workspaces viewable by owner" ON public.workspaces;
CREATE POLICY "Workspaces viewable by owner" ON public.workspaces FOR SELECT USING (owner_id = auth.uid());
DROP POLICY IF EXISTS "Workspaces manageable by owner" ON public.workspaces;
CREATE POLICY "Workspaces manageable by owner" ON public.workspaces FOR ALL USING (owner_id = auth.uid());

-- Workspace members policies
DROP POLICY IF EXISTS "Workspace members viewable" ON public.workspace_members;
CREATE POLICY "Workspace members viewable" ON public.workspace_members FOR SELECT USING (user_id = auth.uid());

-- User memory policies
DROP POLICY IF EXISTS "Memory viewable by owner" ON public.user_memory;
CREATE POLICY "Memory viewable by owner" ON public.user_memory FOR SELECT USING (user_id = auth.uid());
DROP POLICY IF EXISTS "Memory manageable by owner" ON public.user_memory;
CREATE POLICY "Memory manageable by owner" ON public.user_memory FOR ALL USING (user_id = auth.uid());

-- Saved outputs policies
DROP POLICY IF EXISTS "Saved outputs viewable" ON public.saved_outputs;
CREATE POLICY "Saved outputs viewable" ON public.saved_outputs FOR SELECT USING (user_id = auth.uid() OR is_public = true);
DROP POLICY IF EXISTS "Saved outputs manageable by owner" ON public.saved_outputs;
CREATE POLICY "Saved outputs manageable by owner" ON public.saved_outputs FOR ALL USING (user_id = auth.uid());

-- File uploads policies
DROP POLICY IF EXISTS "File uploads viewable by owner" ON public.file_uploads;
CREATE POLICY "File uploads viewable by owner" ON public.file_uploads FOR SELECT USING (user_id = auth.uid());
DROP POLICY IF EXISTS "File uploads manageable by owner" ON public.file_uploads;
CREATE POLICY "File uploads manageable by owner" ON public.file_uploads FOR ALL USING (user_id = auth.uid());

-- API usage policies
DROP POLICY IF EXISTS "API usage viewable by owner" ON public.api_usage;
CREATE POLICY "API usage viewable by owner" ON public.api_usage FOR SELECT USING (user_id = auth.uid());
DROP POLICY IF EXISTS "API usage insertable by owner" ON public.api_usage;
CREATE POLICY "API usage insertable by owner" ON public.api_usage FOR INSERT WITH CHECK (user_id = auth.uid());

-- User sessions policies
DROP POLICY IF EXISTS "Sessions viewable by owner" ON public.user_sessions;
CREATE POLICY "Sessions viewable by owner" ON public.user_sessions FOR SELECT USING (user_id = auth.uid());
DROP POLICY IF EXISTS "Sessions manageable by owner" ON public.user_sessions;
CREATE POLICY "Sessions manageable by owner" ON public.user_sessions FOR ALL USING (user_id = auth.uid());

-- ============================================================================
-- PART 6: CREATE HELPER FUNCTIONS AND TRIGGERS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers
DROP TRIGGER IF EXISTS update_users_updated_at ON public.users;
CREATE TRIGGER update_users_updated_at BEFORE UPDATE ON public.users FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_profiles_updated_at ON public.profiles;
CREATE TRIGGER update_profiles_updated_at BEFORE UPDATE ON public.profiles FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_conversations_updated_at ON public.conversations;
CREATE TRIGGER update_conversations_updated_at BEFORE UPDATE ON public.conversations FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON public.subscriptions;
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON public.subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_support_requests_updated_at ON public.support_requests;
CREATE TRIGGER update_support_requests_updated_at BEFORE UPDATE ON public.support_requests FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_workspaces_updated_at ON public.workspaces;
CREATE TRIGGER update_workspaces_updated_at BEFORE UPDATE ON public.workspaces FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_user_memory_updated_at ON public.user_memory;
CREATE TRIGGER update_user_memory_updated_at BEFORE UPDATE ON public.user_memory FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_saved_outputs_updated_at ON public.saved_outputs;
CREATE TRIGGER update_saved_outputs_updated_at BEFORE UPDATE ON public.saved_outputs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- PART 7: GRANT PERMISSIONS
-- ============================================================================

GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO authenticated;
GRANT SELECT ON ALL TABLES IN SCHEMA public TO anon;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO authenticated;

-- Success message
SELECT 'Migration completed successfully! All 14 tables created with RLS policies.' as status;
