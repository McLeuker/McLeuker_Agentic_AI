-- McLeuker AI V2 - Complete Supabase Schema
-- This schema supports: memory, conversations, files, agent executions, and usage tracking

-- Enable extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "vector"; -- For semantic search if needed

-- =====================================================
-- PROFILES (extends auth.users)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    username TEXT UNIQUE,
    full_name TEXT,
    avatar_url TEXT,
    
    -- Subscription and usage
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    monthly_tokens_used INTEGER DEFAULT 0,
    monthly_tokens_limit INTEGER DEFAULT 100000,
    monthly_files_generated INTEGER DEFAULT 0,
    monthly_files_limit INTEGER DEFAULT 10,
    
    -- Preferences
    preferences JSONB DEFAULT '{
        "default_mode": "thinking",
        "theme": "dark",
        "language": "en",
        "auto_save": true,
        "show_reasoning": true
    }'::jsonb,
    
    -- API keys (encrypted)
    encrypted_api_keys JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- CONVERSATIONS
-- =====================================================
CREATE TABLE IF NOT EXISTS public.conversations (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Basic info
    title TEXT,
    description TEXT,
    
    -- Mode and configuration
    mode TEXT DEFAULT 'thinking' CHECK (mode IN ('instant', 'thinking', 'agent', 'swarm', 'research', 'code', 'hybrid')),
    model_config JSONB DEFAULT '{}',
    
    -- Context and memory
    context JSONB DEFAULT '{}',
    memory_summary TEXT,
    memory_context JSONB DEFAULT '[]',
    
    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'archived', 'deleted')),
    is_pinned BOOLEAN DEFAULT FALSE,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    tags TEXT[] DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_message_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- MESSAGES
-- =====================================================
CREATE TABLE IF NOT EXISTS public.messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES public.conversations(id) ON DELETE CASCADE,
    
    -- Message content
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'system', 'tool')),
    content TEXT NOT NULL,
    
    -- Kimi-2.5 reasoning content
    reasoning_content TEXT,
    
    -- Tool interactions
    tool_calls JSONB DEFAULT '[]',
    tool_results JSONB DEFAULT '[]',
    
    -- Model info
    model_used TEXT,
    
    -- Usage stats
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    tokens_reasoning INTEGER DEFAULT 0,
    latency_ms INTEGER,
    
    -- Files and attachments
    attachments JSONB DEFAULT '[]',
    generated_files UUID[] DEFAULT '{}',
    
    -- Search and sources
    search_query TEXT,
    search_sources JSONB DEFAULT '[]',
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- GENERATED FILES
-- =====================================================
CREATE TABLE IF NOT EXISTS public.generated_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE SET NULL,
    message_id UUID REFERENCES public.messages(id) ON DELETE SET NULL,
    
    -- File info
    filename TEXT NOT NULL,
    original_name TEXT,
    file_type TEXT NOT NULL CHECK (file_type IN ('excel', 'word', 'pdf', 'pptx', 'csv', 'json', 'code', 'image')),
    mime_type TEXT,
    file_size INTEGER,
    
    -- Storage
    storage_path TEXT NOT NULL,
    storage_bucket TEXT DEFAULT 'files',
    download_url TEXT,
    public_url TEXT,
    
    -- Content info
    content_summary TEXT,
    row_count INTEGER,
    sheet_count INTEGER,
    
    -- Expiration
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '7 days',
    is_permanent BOOLEAN DEFAULT FALSE,
    
    -- Status
    status TEXT DEFAULT 'active' CHECK (status IN ('active', 'expired', 'deleted')),
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- AGENT EXECUTIONS
-- =====================================================
CREATE TABLE IF NOT EXISTS public.agent_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE SET NULL,
    message_id UUID REFERENCES public.messages(id) ON DELETE SET NULL,
    
    -- Execution info
    execution_type TEXT NOT NULL CHECK (execution_type IN ('single', 'swarm', 'hybrid')),
    agent_name TEXT NOT NULL,
    
    -- Input/Output
    input_data JSONB NOT NULL,
    output_data JSONB,
    
    -- Status
    status TEXT DEFAULT 'running' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    
    -- Performance
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    execution_time_ms INTEGER,
    
    -- Error info
    error_message TEXT,
    error_stack TEXT,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- TOOL EXECUTIONS
-- =====================================================
CREATE TABLE IF NOT EXISTS public.tool_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE SET NULL,
    message_id UUID REFERENCES public.messages(id) ON DELETE SET NULL,
    agent_execution_id UUID REFERENCES public.agent_executions(id) ON DELETE SET NULL,
    
    -- Tool info
    tool_name TEXT NOT NULL,
    tool_version TEXT DEFAULT '1.0',
    
    -- Input/Output
    tool_input JSONB NOT NULL,
    tool_output JSONB,
    
    -- Status
    status TEXT DEFAULT 'running' CHECK (status IN ('pending', 'running', 'completed', 'failed')),
    success BOOLEAN,
    
    -- Performance
    execution_time_ms INTEGER,
    
    -- Error info
    error_message TEXT,
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- MEMORY SNAPSHOTS (for long conversations)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.memory_snapshots (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    conversation_id UUID NOT NULL REFERENCES public.conversations(id) ON DELETE CASCADE,
    
    -- Snapshot content
    summary TEXT NOT NULL,
    key_points JSONB DEFAULT '[]',
    entities JSONB DEFAULT '[]',
    topics TEXT[] DEFAULT '{}',
    
    -- Message range
    from_message_id UUID REFERENCES public.messages(id),
    to_message_id UUID REFERENCES public.messages(id),
    message_count INTEGER,
    
    -- Embedding for semantic search (optional)
    embedding VECTOR(1536),
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- USAGE STATS
-- =====================================================
CREATE TABLE IF NOT EXISTS public.usage_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Time period
    date DATE DEFAULT CURRENT_DATE,
    hour INTEGER, -- For hourly stats (optional)
    
    -- Request stats
    requests_count INTEGER DEFAULT 0,
    streaming_requests INTEGER DEFAULT 0,
    
    -- Token usage
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    tokens_reasoning INTEGER DEFAULT 0,
    tokens_total INTEGER DEFAULT 0,
    
    -- Model usage
    kimi_requests INTEGER DEFAULT 0,
    grok_requests INTEGER DEFAULT 0,
    hybrid_requests INTEGER DEFAULT 0,
    
    -- Feature usage
    files_generated INTEGER DEFAULT 0,
    searches_performed INTEGER DEFAULT 0,
    agents_executed INTEGER DEFAULT 0,
    tools_executed INTEGER DEFAULT 0,
    
    -- Performance
    avg_latency_ms INTEGER,
    
    UNIQUE(user_id, date, hour)
);

-- =====================================================
-- SEARCH CACHE (for performance)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.search_cache (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    query_hash TEXT UNIQUE NOT NULL,
    query_text TEXT NOT NULL,
    
    -- Results
    results JSONB NOT NULL,
    sources JSONB DEFAULT '[]',
    
    -- Metadata
    search_type TEXT DEFAULT 'web',
    result_count INTEGER,
    
    -- Expiration
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '1 hour',
    
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =====================================================
-- USER API KEYS (encrypted)
-- =====================================================
CREATE TABLE IF NOT EXISTS public.user_api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    key_name TEXT NOT NULL,
    encrypted_key TEXT NOT NULL,
    key_last_four TEXT,
    
    is_active BOOLEAN DEFAULT TRUE,
    
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    
    UNIQUE(user_id, key_name)
);

-- =====================================================
-- INDEXES
-- =====================================================

-- Conversations
CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON public.conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_updated_at ON public.conversations(updated_at DESC);
CREATE INDEX IF NOT EXISTS idx_conversations_status ON public.conversations(status);
CREATE INDEX IF NOT EXISTS idx_conversations_mode ON public.conversations(mode);

-- Messages
CREATE INDEX IF NOT EXISTS idx_messages_conversation_id ON public.messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON public.messages(created_at);
CREATE INDEX IF NOT EXISTS idx_messages_role ON public.messages(role);

-- Files
CREATE INDEX IF NOT EXISTS idx_files_user_id ON public.generated_files(user_id);
CREATE INDEX IF NOT EXISTS idx_files_conversation_id ON public.generated_files(conversation_id);
CREATE INDEX IF NOT EXISTS idx_files_expires_at ON public.generated_files(expires_at);
CREATE INDEX IF NOT EXISTS idx_files_status ON public.generated_files(status);

-- Agent executions
CREATE INDEX IF NOT EXISTS idx_agent_executions_user_id ON public.agent_executions(user_id);
CREATE INDEX IF NOT EXISTS idx_agent_executions_status ON public.agent_executions(status);
CREATE INDEX IF NOT EXISTS idx_agent_executions_created_at ON public.agent_executions(created_at);

-- Tool executions
CREATE INDEX IF NOT EXISTS idx_tool_executions_user_id ON public.tool_executions(user_id);
CREATE INDEX IF NOT EXISTS idx_tool_executions_tool_name ON public.tool_executions(tool_name);

-- Usage stats
CREATE INDEX IF NOT EXISTS idx_usage_stats_user_date ON public.usage_stats(user_id, date);

-- Search cache
CREATE INDEX IF NOT EXISTS idx_search_cache_query_hash ON public.search_cache(query_hash);
CREATE INDEX IF NOT EXISTS idx_search_cache_expires ON public.search_cache(expires_at);

-- Memory snapshots
CREATE INDEX IF NOT EXISTS idx_memory_snapshots_conversation ON public.memory_snapshots(conversation_id);

-- =====================================================
-- ROW LEVEL SECURITY (RLS)
-- =====================================================

-- Profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own profile"
    ON public.profiles FOR SELECT USING (auth.uid() = id);
CREATE POLICY "Users can update own profile"
    ON public.profiles FOR UPDATE USING (auth.uid() = id);

-- Conversations
ALTER TABLE public.conversations ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own conversations"
    ON public.conversations FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can create conversations"
    ON public.conversations FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own conversations"
    ON public.conversations FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own conversations"
    ON public.conversations FOR DELETE USING (auth.uid() = user_id);

-- Messages
ALTER TABLE public.messages ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view messages in own conversations"
    ON public.messages FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.conversations 
                WHERE conversations.id = messages.conversation_id 
                AND conversations.user_id = auth.uid())
    );
CREATE POLICY "Users can create messages in own conversations"
    ON public.messages FOR INSERT WITH CHECK (
        EXISTS (SELECT 1 FROM public.conversations 
                WHERE conversations.id = messages.conversation_id 
                AND conversations.user_id = auth.uid())
    );

-- Files
ALTER TABLE public.generated_files ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own files"
    ON public.generated_files FOR SELECT USING (auth.uid() = user_id);

-- Agent executions
ALTER TABLE public.agent_executions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own agent executions"
    ON public.agent_executions FOR SELECT USING (auth.uid() = user_id);

-- Tool executions
ALTER TABLE public.tool_executions ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own tool executions"
    ON public.tool_executions FOR SELECT USING (auth.uid() = user_id);

-- Usage stats
ALTER TABLE public.usage_stats ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can view own usage stats"
    ON public.usage_stats FOR SELECT USING (auth.uid() = user_id);

-- API keys
ALTER TABLE public.user_api_keys ENABLE ROW LEVEL SECURITY;
CREATE POLICY "Users can manage own API keys"
    ON public.user_api_keys FOR ALL USING (auth.uid() = user_id);

-- =====================================================
-- FUNCTIONS
-- =====================================================

-- Update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_conversations_updated_at
    BEFORE UPDATE ON public.conversations
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_messages_updated_at
    BEFORE UPDATE ON public.messages
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_files_updated_at
    BEFORE UPDATE ON public.generated_files
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Increment usage stats
CREATE OR REPLACE FUNCTION increment_usage_stats(
    p_user_id UUID,
    p_tokens_input INTEGER DEFAULT 0,
    p_tokens_output INTEGER DEFAULT 0,
    p_tokens_reasoning INTEGER DEFAULT 0,
    p_files_generated INTEGER DEFAULT 0,
    p_searches_performed INTEGER DEFAULT 0,
    p_agents_executed INTEGER DEFAULT 0,
    p_tools_executed INTEGER DEFAULT 0,
    p_model TEXT DEFAULT 'kimi'
)
RETURNS VOID AS $$
DECLARE
    v_kimi INTEGER := 0;
    v_grok INTEGER := 0;
    v_hybrid INTEGER := 0;
BEGIN
    IF p_model = 'kimi' THEN v_kimi := 1;
    ELSIF p_model = 'grok' THEN v_grok := 1;
    ELSIF p_model = 'hybrid' THEN v_hybrid := 1;
    END IF;

    INSERT INTO public.usage_stats (
        user_id, date, requests_count,
        tokens_input, tokens_output, tokens_reasoning, tokens_total,
        kimi_requests, grok_requests, hybrid_requests,
        files_generated, searches_performed, agents_executed, tools_executed
    ) VALUES (
        p_user_id, CURRENT_DATE, 1,
        p_tokens_input, p_tokens_output, p_tokens_reasoning,
        p_tokens_input + p_tokens_output + p_tokens_reasoning,
        v_kimi, v_grok, v_hybrid,
        p_files_generated, p_searches_performed, p_agents_executed, p_tools_executed
    )
    ON CONFLICT (user_id, date, hour)
    DO UPDATE SET
        requests_count = usage_stats.requests_count + 1,
        tokens_input = usage_stats.tokens_input + p_tokens_input,
        tokens_output = usage_stats.tokens_output + p_tokens_output,
        tokens_reasoning = usage_stats.tokens_reasoning + p_tokens_reasoning,
        tokens_total = usage_stats.tokens_total + p_tokens_input + p_tokens_output + p_tokens_reasoning,
        kimi_requests = usage_stats.kimi_requests + v_kimi,
        grok_requests = usage_stats.grok_requests + v_grok,
        hybrid_requests = usage_stats.hybrid_requests + v_hybrid,
        files_generated = usage_stats.files_generated + p_files_generated,
        searches_performed = usage_stats.searches_performed + p_searches_performed,
        agents_executed = usage_stats.agents_executed + p_agents_executed,
        tools_executed = usage_stats.tools_executed + p_tools_executed;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get conversation with messages
CREATE OR REPLACE FUNCTION get_conversation_with_messages(
    p_conversation_id UUID,
    p_limit INTEGER DEFAULT 100,
    p_offset INTEGER DEFAULT 0
)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'conversation', row_to_json(c),
        'messages', (
            SELECT jsonb_agg(row_to_json(m) ORDER BY m.created_at)
            FROM (
                SELECT * FROM public.messages
                WHERE messages.conversation_id = c.id
                ORDER BY created_at DESC
                LIMIT p_limit OFFSET p_offset
            ) m
        ),
        'total_messages', (
            SELECT COUNT(*) FROM public.messages
            WHERE messages.conversation_id = c.id
        )
    )
    INTO result
    FROM public.conversations c
    WHERE c.id = p_conversation_id AND c.user_id = auth.uid();
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Search conversations
CREATE OR REPLACE FUNCTION search_conversations(p_query TEXT)
RETURNS TABLE (
    id UUID,
    title TEXT,
    preview TEXT,
    updated_at TIMESTAMPTZ
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.title,
        LEFT(m.content, 200) as preview,
        c.updated_at
    FROM public.conversations c
    LEFT JOIN public.messages m ON m.conversation_id = c.id
    WHERE c.user_id = auth.uid()
    AND c.status = 'active'
    AND (
        c.title ILIKE '%' || p_query || '%'
        OR m.content ILIKE '%' || p_query || '%'
    )
    ORDER BY c.updated_at DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Cleanup expired files
CREATE OR REPLACE FUNCTION cleanup_expired_files()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    UPDATE public.generated_files
    SET status = 'expired'
    WHERE expires_at < NOW()
    AND status = 'active'
    AND is_permanent = FALSE;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Create memory snapshot
CREATE OR REPLACE FUNCTION create_memory_snapshot(p_conversation_id UUID)
RETURNS UUID AS $$
DECLARE
    v_snapshot_id UUID;
    v_summary TEXT;
    v_key_points JSONB;
    v_first_message_id UUID;
    v_last_message_id UUID;
    v_message_count INTEGER;
BEGIN
    -- Get message range
    SELECT 
        MIN(id), MAX(id), COUNT(*)
    INTO v_first_message_id, v_last_message_id, v_message_count
    FROM public.messages
    WHERE conversation_id = p_conversation_id;
    
    -- Create snapshot (in real implementation, this would call an LLM)
    v_summary := 'Conversation summary for ' || p_conversation_id::text;
    v_key_points := '["Key point 1", "Key point 2"]'::jsonb;
    
    INSERT INTO public.memory_snapshots (
        conversation_id,
        summary,
        key_points,
        from_message_id,
        to_message_id,
        message_count
    ) VALUES (
        p_conversation_id,
        v_summary,
        v_key_points,
        v_first_message_id,
        v_last_message_id,
        v_message_count
    )
    RETURNING id INTO v_snapshot_id;
    
    RETURN v_snapshot_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================================
-- SCHEDULED JOBS (using pg_cron if available)
-- =====================================================

-- Cleanup expired files daily
-- SELECT cron.schedule('cleanup-expired-files', '0 0 * * *', 'SELECT cleanup_expired_files()');

-- Cleanup old search cache hourly
-- SELECT cron.schedule('cleanup-search-cache', '0 * * * *', 'DELETE FROM public.search_cache WHERE expires_at < NOW()');
