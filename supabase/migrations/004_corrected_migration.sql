-- McLeuker AI Platform - Corrected Migration Script
-- Based on actual existing schema analysis
-- Your users table uses 'id' as primary key (auth.users UUID)

-- ============================================================================
-- PART 1: ADD MISSING COLUMNS TO EXISTING TABLES
-- ============================================================================

-- Add missing columns to users table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'company') THEN
        ALTER TABLE public.users ADD COLUMN company TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'role') THEN
        ALTER TABLE public.users ADD COLUMN role TEXT DEFAULT 'user';
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'profile_image') THEN
        ALTER TABLE public.users ADD COLUMN profile_image TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'preferences') THEN
        ALTER TABLE public.users ADD COLUMN preferences JSONB DEFAULT '{}'::jsonb;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'onboarding_completed') THEN
        ALTER TABLE public.users ADD COLUMN onboarding_completed BOOLEAN DEFAULT FALSE;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'users' AND column_name = 'auth_provider') THEN
        ALTER TABLE public.users ADD COLUMN auth_provider TEXT DEFAULT 'email';
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
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'profiles' AND column_name = 'name') THEN
        ALTER TABLE public.profiles ADD COLUMN name TEXT;
    END IF;
END $$;

-- Add missing columns to conversations table
DO $$ 
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'conversations' AND column_name = 'sector') THEN
        ALTER TABLE public.conversations ADD COLUMN sector TEXT DEFAULT 'all';
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
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_schema = 'public' AND table_name = 'chat_messages' AND column_name = 'thinking_content') THEN
        ALTER TABLE public.chat_messages ADD COLUMN thinking_content TEXT;
    END IF;
END $$;

-- ============================================================================
-- PART 2: CREATE NEW TABLES FOR MEMORY AND ADDITIONAL FEATURES
-- Note: Using 'id' from users table as foreign key reference
-- ============================================================================

-- SUBSCRIPTIONS TABLE (if not exists)
CREATE TABLE IF NOT EXISTS public.subscriptions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL,
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

-- WORKSPACES TABLE
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

-- WORKSPACE_MEMBERS TABLE
CREATE TABLE IF NOT EXISTS public.workspace_members (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    user_id UUID NOT NULL,
    role TEXT DEFAULT 'member',
    invited_by UUID,
    joined_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(workspace_id, user_id)
);

-- USER_MEMORY TABLE - Long-term memory for AI personalization
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

-- SAVED_OUTPUTS TABLE - Saved AI-generated content
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

-- FILE_UPLOADS TABLE - Track uploaded files
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

-- API_USAGE TABLE - Track API usage for billing
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

-- USER_SESSIONS TABLE - Track active sessions
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
-- PART 3: CREATE INDEXES
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_subscriptions_user_id ON public.subscriptions(user_id);
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
-- PART 4: ENABLE ROW LEVEL SECURITY ON NEW TABLES
-- ============================================================================

ALTER TABLE public.subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspaces ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.workspace_members ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_memory ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.saved_outputs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.file_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.api_usage ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_sessions ENABLE ROW LEVEL SECURITY;

-- ============================================================================
-- PART 5: CREATE RLS POLICIES FOR NEW TABLES
-- ============================================================================

-- Subscriptions policies
DROP POLICY IF EXISTS "Subscriptions viewable by owner" ON public.subscriptions;
CREATE POLICY "Subscriptions viewable by owner" ON public.subscriptions FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Subscriptions manageable by owner" ON public.subscriptions;
CREATE POLICY "Subscriptions manageable by owner" ON public.subscriptions FOR ALL USING (auth.uid() = user_id);

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

-- Apply triggers to new tables
DROP TRIGGER IF EXISTS update_subscriptions_updated_at ON public.subscriptions;
CREATE TRIGGER update_subscriptions_updated_at BEFORE UPDATE ON public.subscriptions FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

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
SELECT 'Migration completed successfully! New tables created and existing tables updated.' as status;
