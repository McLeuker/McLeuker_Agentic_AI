-- McLeuker AI Platform - Complete Database Schema
-- This migration creates all necessary tables for the platform with proper memory and persistence

-- ============================================================================
-- 1. USERS TABLE - Core user data with profile information
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
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

-- Create index for faster lookups
CREATE INDEX IF NOT EXISTS idx_users_user_id ON public.users(user_id);
CREATE INDEX IF NOT EXISTS idx_users_email ON public.users(email);

-- ============================================================================
-- 2. PROFILES TABLE - Extended profile information (for backward compatibility)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
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

CREATE INDEX IF NOT EXISTS idx_profiles_user_id ON public.profiles(user_id);

-- ============================================================================
-- 3. CONVERSATIONS TABLE - Chat conversation sessions
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id TEXT NOT NULL,
    title TEXT DEFAULT 'New Chat',
    sector TEXT DEFAULT 'all',
    is_archived BOOLEAN DEFAULT FALSE,
    is_pinned BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON public.conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_session_id ON public.conversations(session_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON public.conversations(updated_at DESC);

-- ============================================================================
-- 4. CHAT_MESSAGES TABLE - Individual messages within conversations
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.chat_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES public.conversations(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system')),
    content TEXT NOT NULL,
    model_used TEXT,
    credits_used INTEGER DEFAULT 0,
    is_favorite BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    attachments JSONB DEFAULT '[]'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation_id ON public.chat_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_user_id ON public.chat_messages(user_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_created_at ON public.chat_messages(created_at);

-- ============================================================================
-- 5. SUBSCRIPTIONS TABLE - User subscription plans
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL UNIQUE REFERENCES auth.users(id) ON DELETE CASCADE,
    plan TEXT DEFAULT 'free' CHECK (plan IN ('free', 'pro', 'studio', 'enterprise')),
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'cancelled', 'past_due', 'trialing')),
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

CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id);
CREATE INDEX IF NOT EXISTS idx_subscriptions_stripe_customer_id ON public.subscriptions(stripe_customer_id);

-- ============================================================================
-- 6. CREDIT_TRANSACTIONS TABLE - Credit usage history
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.credit_transactions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    type TEXT NOT NULL CHECK (type IN ('usage', 'purchase', 'refund', 'bonus', 'monthly_reset')),
    description TEXT,
    balance_after INTEGER NOT NULL,
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE SET NULL,
    message_id UUID REFERENCES public.chat_messages(id) ON DELETE SET NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON public.credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created_at ON public.credit_transactions(created_at DESC);

-- ============================================================================
-- 7. WORKSPACES TABLE - Team workspaces (for future team features)
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.workspaces (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    slug TEXT NOT NULL UNIQUE,
    description TEXT,
    owner_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    logo_url TEXT,
    settings JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_workspaces_owner_id ON public.workspaces(owner_id);
CREATE INDEX IF NOT EXISTS idx_workspaces_slug ON public.workspaces(slug);

-- ============================================================================
-- 8. WORKSPACE_MEMBERS TABLE - Workspace membership
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL REFERENCES public.workspaces(id) ON DELETE CASCADE,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    role TEXT DEFAULT 'member' CHECK (role IN ('owner', 'admin', 'member', 'viewer')),
    invited_by UUID REFERENCES auth.users(id),
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

CREATE INDEX IF NOT EXISTS idx_workspace_members_workspace_id ON public.workspace_members(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_members_user_id ON public.workspace_members(user_id);

-- ============================================================================
-- 9. SUPPORT_REQUESTS TABLE - Customer support tickets
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.support_requests (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    type TEXT NOT NULL CHECK (type IN ('bug', 'feature', 'billing', 'general', 'technical')),
    subject TEXT NOT NULL,
    message TEXT NOT NULL,
    status TEXT DEFAULT 'open' CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')),
    priority TEXT DEFAULT 'normal' CHECK (priority IN ('low', 'normal', 'high', 'urgent')),
    assigned_to TEXT,
    resolution TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_support_requests_user_id ON public.support_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_support_requests_status ON public.support_requests(status);

-- ============================================================================
-- 10. USER_MEMORY TABLE - Long-term memory for AI personalization
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.user_memory (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    memory_type TEXT NOT NULL CHECK (memory_type IN ('preference', 'fact', 'context', 'style', 'project')),
    key TEXT NOT NULL,
    value TEXT NOT NULL,
    confidence FLOAT DEFAULT 1.0,
    source TEXT, -- conversation_id or 'manual'
    expires_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, memory_type, key)
);

CREATE INDEX IF NOT EXISTS idx_user_memory_user_id ON public.user_memory(user_id);
CREATE INDEX IF NOT EXISTS idx_user_memory_type ON public.user_memory(memory_type);

-- ============================================================================
-- 11. SAVED_OUTPUTS TABLE - Saved AI-generated content
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.saved_outputs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE SET NULL,
    message_id UUID REFERENCES public.chat_messages(id) ON DELETE SET NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    content_type TEXT DEFAULT 'text' CHECK (content_type IN ('text', 'report', 'analysis', 'code', 'image', 'document')),
    tags TEXT[] DEFAULT '{}',
    is_public BOOLEAN DEFAULT FALSE,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_saved_outputs_user_id ON public.saved_outputs(user_id);
CREATE INDEX IF NOT EXISTS idx_saved_outputs_content_type ON public.saved_outputs(content_type);

-- ============================================================================
-- 12. FILE_UPLOADS TABLE - Track uploaded files
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.file_uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE SET NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER NOT NULL,
    storage_path TEXT NOT NULL,
    public_url TEXT,
    mime_type TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_file_uploads_user_id ON public.file_uploads(user_id);
CREATE INDEX IF NOT EXISTS idx_file_uploads_conversation_id ON public.file_uploads(conversation_id);

-- ============================================================================
-- 13. API_USAGE TABLE - Track API usage for billing
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.api_usage (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    api_name TEXT NOT NULL,
    endpoint TEXT,
    tokens_used INTEGER DEFAULT 0,
    cost_cents INTEGER DEFAULT 0,
    request_metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_api_usage_user_id ON public.api_usage(user_id);
CREATE INDEX IF NOT EXISTS idx_api_usage_created_at ON public.api_usage(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_api_usage_api_name ON public.api_usage(api_name);

-- ============================================================================
-- 14. USER_SESSIONS TABLE - Track active sessions for auth persistence
-- ============================================================================
CREATE TABLE IF NOT EXISTS public.user_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    session_token TEXT NOT NULL UNIQUE,
    device_info JSONB DEFAULT '{}'::jsonb,
    ip_address TEXT,
    user_agent TEXT,
    is_active BOOLEAN DEFAULT TRUE,
    last_activity_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON public.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_session_token ON public.user_sessions(session_token);
CREATE INDEX IF NOT EXISTS idx_user_sessions_expires_at ON public.user_sessions(expires_at);

-- ============================================================================
-- ROW LEVEL SECURITY (RLS) POLICIES
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.support_requests ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_outputs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.file_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

-- Users policies
DROP POLICY IF EXISTS "Users can view own data" ON public.users;
CREATE POLICY "Users can view own data" ON public.users FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can update own data" ON public.users;
CREATE POLICY "Users can update own data" ON public.users FOR UPDATE USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own data" ON public.users;
CREATE POLICY "Users can insert own data" ON public.users FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Profiles policies
DROP POLICY IF EXISTS "Profiles are viewable by owner" ON public.profiles;
CREATE POLICY "Profiles are viewable by owner" ON public.profiles FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Profiles are editable by owner" ON public.profiles;
CREATE POLICY "Profiles are editable by owner" ON public.profiles FOR UPDATE USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Profiles can be created by owner" ON public.profiles;
CREATE POLICY "Profiles can be created by owner" ON public.profiles FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Conversations policies
DROP POLICY IF EXISTS "Conversations are viewable by owner" ON public.conversations;
CREATE POLICY "Conversations are viewable by owner" ON public.conversations FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Conversations are editable by owner" ON public.conversations;
CREATE POLICY "Conversations are editable by owner" ON public.conversations FOR ALL USING (auth.uid() = user_id);

-- Chat messages policies
DROP POLICY IF EXISTS "Messages are viewable by conversation owner" ON public.chat_messages;
CREATE POLICY "Messages are viewable by conversation owner" ON public.chat_messages FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Messages can be created by owner" ON public.chat_messages;
CREATE POLICY "Messages can be created by owner" ON public.chat_messages FOR INSERT WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "Messages can be updated by owner" ON public.chat_messages;
CREATE POLICY "Messages can be updated by owner" ON public.chat_messages FOR UPDATE USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Messages can be deleted by owner" ON public.chat_messages;
CREATE POLICY "Messages can be deleted by owner" ON public.chat_messages FOR DELETE USING (auth.uid() = user_id);

-- Subscriptions policies
DROP POLICY IF EXISTS "Subscriptions are viewable by owner" ON public.subscriptions;
CREATE POLICY "Subscriptions are viewable by owner" ON public.subscriptions FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Subscriptions can be updated by owner" ON public.subscriptions;
CREATE POLICY "Subscriptions can be updated by owner" ON public.subscriptions FOR UPDATE USING (auth.uid() = user_id);

-- Credit transactions policies
DROP POLICY IF EXISTS "Credit transactions are viewable by owner" ON public.credit_transactions;
CREATE POLICY "Credit transactions are viewable by owner" ON public.credit_transactions FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Credit transactions can be created" ON public.credit_transactions;
CREATE POLICY "Credit transactions can be created" ON public.credit_transactions FOR INSERT WITH CHECK (auth.uid() = user_id);

-- Support requests policies
DROP POLICY IF EXISTS "Support requests are viewable by owner" ON public.support_requests;
CREATE POLICY "Support requests are viewable by owner" ON public.support_requests FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Support requests can be created by owner" ON public.support_requests;
CREATE POLICY "Support requests can be created by owner" ON public.support_requests FOR INSERT WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "Support requests can be updated by owner" ON public.support_requests;
CREATE POLICY "Support requests can be updated by owner" ON public.support_requests FOR UPDATE USING (auth.uid() = user_id);

-- User memory policies
DROP POLICY IF EXISTS "Memory is viewable by owner" ON public.user_memory;
CREATE POLICY "Memory is viewable by owner" ON public.user_memory FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Memory can be managed by owner" ON public.user_memory;
CREATE POLICY "Memory can be managed by owner" ON public.user_memory FOR ALL USING (auth.uid() = user_id);

-- Saved outputs policies
DROP POLICY IF EXISTS "Saved outputs are viewable by owner" ON public.saved_outputs;
CREATE POLICY "Saved outputs are viewable by owner" ON public.saved_outputs FOR SELECT USING (auth.uid() = user_id OR is_public = true);
DROP POLICY IF EXISTS "Saved outputs can be managed by owner" ON public.saved_outputs;
CREATE POLICY "Saved outputs can be managed by owner" ON public.saved_outputs FOR ALL USING (auth.uid() = user_id);

-- File uploads policies
DROP POLICY IF EXISTS "File uploads are viewable by owner" ON public.file_uploads;
CREATE POLICY "File uploads are viewable by owner" ON public.file_uploads FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "File uploads can be managed by owner" ON public.file_uploads;
CREATE POLICY "File uploads can be managed by owner" ON public.file_uploads FOR ALL USING (auth.uid() = user_id);

-- API usage policies
DROP POLICY IF EXISTS "API usage is viewable by owner" ON public.api_usage;
CREATE POLICY "API usage is viewable by owner" ON public.api_usage FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "API usage can be created" ON public.api_usage;
CREATE POLICY "API usage can be created" ON public.api_usage FOR INSERT WITH CHECK (auth.uid() = user_id);

-- User sessions policies
DROP POLICY IF EXISTS "Sessions are viewable by owner" ON public.user_sessions;
CREATE POLICY "Sessions are viewable by owner" ON public.user_sessions FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Sessions can be managed by owner" ON public.user_sessions;
CREATE POLICY "Sessions can be managed by owner" ON public.user_sessions FOR ALL USING (auth.uid() = user_id);

-- ============================================================================
-- TRIGGERS FOR AUTOMATIC TIMESTAMPS
-- ============================================================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply trigger to tables with updated_at
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

DROP TRIGGER IF EXISTS update_user_memory_updated_at ON public.user_memory;
CREATE TRIGGER update_user_memory_updated_at BEFORE UPDATE ON public.user_memory FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_saved_outputs_updated_at ON public.saved_outputs;
CREATE TRIGGER update_saved_outputs_updated_at BEFORE UPDATE ON public.saved_outputs FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

DROP TRIGGER IF EXISTS update_workspaces_updated_at ON public.workspaces;
CREATE TRIGGER update_workspaces_updated_at BEFORE UPDATE ON public.workspaces FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- ============================================================================
-- FUNCTION: Auto-create user profile on signup
-- ============================================================================
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    -- Insert into users table
    INSERT INTO public.users (user_id, email, name, auth_provider, last_login_at)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
        COALESCE(NEW.raw_app_meta_data->>'provider', 'email'),
        NOW()
    )
    ON CONFLICT (user_id) DO UPDATE SET
        last_login_at = NOW(),
        email = EXCLUDED.email;
    
    -- Insert into profiles table
    INSERT INTO public.profiles (user_id, email, full_name)
    VALUES (
        NEW.id,
        NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1))
    )
    ON CONFLICT (user_id) DO UPDATE SET
        email = EXCLUDED.email;
    
    -- Insert into subscriptions table with default free plan
    INSERT INTO public.subscriptions (user_id, plan, status, credits_remaining, credits_monthly)
    VALUES (NEW.id, 'free', 'active', 50, 50)
    ON CONFLICT (user_id) DO NOTHING;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create trigger for new user signup
DROP TRIGGER IF EXISTS on_auth_user_created ON auth.users;
CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- FUNCTION: Update last login timestamp
-- ============================================================================
CREATE OR REPLACE FUNCTION public.handle_user_login()
RETURNS TRIGGER AS $$
BEGIN
    UPDATE public.users
    SET last_login_at = NOW()
    WHERE user_id = NEW.id;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Note: This trigger would need to be set up differently as Supabase doesn't
-- have a direct trigger for login events. Instead, call this from the app.

-- ============================================================================
-- GRANT PERMISSIONS
-- ============================================================================
GRANT USAGE ON SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL TABLES IN SCHEMA public TO anon, authenticated;
GRANT ALL ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated;
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated;
