-- McLeuker AI - Kimi 2.5 Complete Schema Migration (003)
-- Adds new tables for file generation, tool execution, usage stats, and API keys
-- Safe to run multiple times (uses IF NOT EXISTS throughout)

-- 1. Enable necessary extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- 2. Add mode column and CHECK constraint to conversations table
ALTER TABLE public.conversations ADD COLUMN IF NOT EXISTS mode TEXT;

DO $$
BEGIN
  ALTER TABLE public.conversations DROP CONSTRAINT IF EXISTS conversations_mode_check;
  ALTER TABLE public.conversations ADD CONSTRAINT conversations_mode_check
    CHECK (mode IS NULL OR mode IN ('instant', 'thinking', 'agent', 'swarm', 'research', 'code', 'deep', 'quick'));
EXCEPTION WHEN OTHERS THEN
  NULL;
END $$;

-- 3. Add missing columns to conversations
ALTER TABLE public.conversations ADD COLUMN IF NOT EXISTS context JSONB DEFAULT '{}';
ALTER TABLE public.conversations ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';
ALTER TABLE public.conversations ADD COLUMN IF NOT EXISTS is_archived BOOLEAN DEFAULT FALSE;

-- 4. Add missing columns to chat_messages (reasoning, tool_calls, etc.)
ALTER TABLE public.chat_messages ADD COLUMN IF NOT EXISTS reasoning_content TEXT;
ALTER TABLE public.chat_messages ADD COLUMN IF NOT EXISTS tool_calls JSONB;
ALTER TABLE public.chat_messages ADD COLUMN IF NOT EXISTS tool_results JSONB;
ALTER TABLE public.chat_messages ADD COLUMN IF NOT EXISTS tokens_used INTEGER;
ALTER TABLE public.chat_messages ADD COLUMN IF NOT EXISTS latency_ms INTEGER;

-- 5. Create generated_files table
CREATE TABLE IF NOT EXISTS public.generated_files (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE SET NULL,
    message_id UUID REFERENCES public.chat_messages(id) ON DELETE SET NULL,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,
    storage_path TEXT,
    download_url TEXT,
    expires_at TIMESTAMPTZ DEFAULT NOW() + INTERVAL '24 hours',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Add CHECK constraint for file_type
DO $$
BEGIN
  ALTER TABLE public.generated_files ADD CONSTRAINT generated_files_file_type_check
    CHECK (file_type IN ('excel', 'word', 'pdf', 'pptx', 'csv', 'json'));
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- 6. Create tool_executions table
CREATE TABLE IF NOT EXISTS public.tool_executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES public.conversations(id) ON DELETE SET NULL,
    tool_name TEXT NOT NULL,
    tool_input JSONB,
    tool_output JSONB,
    execution_time_ms INTEGER,
    success BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- 7. Create usage_stats table
CREATE TABLE IF NOT EXISTS public.usage_stats (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    date DATE DEFAULT CURRENT_DATE,
    requests_count INTEGER DEFAULT 0,
    tokens_input INTEGER DEFAULT 0,
    tokens_output INTEGER DEFAULT 0,
    files_generated INTEGER DEFAULT 0,
    searches_performed INTEGER DEFAULT 0,
    UNIQUE(user_id, date)
);

-- 8. Create user_api_keys table (encrypted)
CREATE TABLE IF NOT EXISTS public.user_api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    key_name TEXT NOT NULL,
    encrypted_key TEXT NOT NULL,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, key_name)
);

-- 9. Performance indexes
CREATE INDEX IF NOT EXISTS idx_generated_files_user_id ON public.generated_files(user_id);
CREATE INDEX IF NOT EXISTS idx_generated_files_expires_at ON public.generated_files(expires_at);
CREATE INDEX IF NOT EXISTS idx_generated_files_conversation_id ON public.generated_files(conversation_id);
CREATE INDEX IF NOT EXISTS idx_tool_executions_user_id ON public.tool_executions(user_id);
CREATE INDEX IF NOT EXISTS idx_tool_executions_conversation_id ON public.tool_executions(conversation_id);
CREATE INDEX IF NOT EXISTS idx_tool_executions_created_at ON public.tool_executions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_usage_stats_user_date ON public.usage_stats(user_id, date);
CREATE INDEX IF NOT EXISTS idx_user_api_keys_user_id ON public.user_api_keys(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_is_archived ON public.conversations(is_archived);

-- 10. Row Level Security (RLS) policies

-- generated_files
ALTER TABLE public.generated_files ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
  CREATE POLICY "Users can view own files" ON public.generated_files FOR SELECT USING (auth.uid() = user_id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
  CREATE POLICY "Users can create own files" ON public.generated_files FOR INSERT WITH CHECK (auth.uid() = user_id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
  CREATE POLICY "Users can delete own files" ON public.generated_files FOR DELETE USING (auth.uid() = user_id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- tool_executions
ALTER TABLE public.tool_executions ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
  CREATE POLICY "Users can view own tool executions" ON public.tool_executions FOR SELECT USING (auth.uid() = user_id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

DO $$
BEGIN
  CREATE POLICY "Users can create own tool executions" ON public.tool_executions FOR INSERT WITH CHECK (auth.uid() = user_id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- usage_stats
ALTER TABLE public.usage_stats ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
  CREATE POLICY "Users can view own usage stats" ON public.usage_stats FOR SELECT USING (auth.uid() = user_id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- user_api_keys
ALTER TABLE public.user_api_keys ENABLE ROW LEVEL SECURITY;

DO $$
BEGIN
  CREATE POLICY "Users can manage own API keys" ON public.user_api_keys FOR ALL USING (auth.uid() = user_id);
EXCEPTION WHEN duplicate_object THEN NULL;
END $$;

-- 11. Functions

-- Update updated_at timestamp trigger function
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at trigger to user_api_keys
DROP TRIGGER IF EXISTS update_user_api_keys_updated_at ON public.user_api_keys;
CREATE TRIGGER update_user_api_keys_updated_at
    BEFORE UPDATE ON public.user_api_keys
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Increment usage stats function
CREATE OR REPLACE FUNCTION increment_usage_stats(
    p_user_id UUID,
    p_tokens_input INTEGER DEFAULT 0,
    p_tokens_output INTEGER DEFAULT 0,
    p_files_generated INTEGER DEFAULT 0,
    p_searches_performed INTEGER DEFAULT 0
)
RETURNS VOID AS $$
BEGIN
    INSERT INTO public.usage_stats (user_id, date, requests_count, tokens_input, tokens_output, files_generated, searches_performed)
    VALUES (p_user_id, CURRENT_DATE, 1, p_tokens_input, p_tokens_output, p_files_generated, p_searches_performed)
    ON CONFLICT (user_id, date)
    DO UPDATE SET
        requests_count = usage_stats.requests_count + 1,
        tokens_input = usage_stats.tokens_input + p_tokens_input,
        tokens_output = usage_stats.tokens_output + p_tokens_output,
        files_generated = usage_stats.files_generated + p_files_generated,
        searches_performed = usage_stats.searches_performed + p_searches_performed;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Clean up expired files function
CREATE OR REPLACE FUNCTION cleanup_expired_files()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM public.generated_files
    WHERE expires_at < NOW();
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Get conversation with messages function
CREATE OR REPLACE FUNCTION get_conversation_with_messages(p_conversation_id UUID)
RETURNS JSONB AS $$
DECLARE
    result JSONB;
BEGIN
    SELECT jsonb_build_object(
        'conversation', row_to_json(c),
        'messages', (
            SELECT jsonb_agg(row_to_json(m) ORDER BY m.created_at)
            FROM public.chat_messages m
            WHERE m.conversation_id = c.id
        )
    )
    INTO result
    FROM public.conversations c
    WHERE c.id = p_conversation_id AND c.user_id = auth.uid();
    
    RETURN result;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Search conversations function (uses pg_trgm from migration 002)
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
    LEFT JOIN public.chat_messages m ON m.conversation_id = c.id
    WHERE c.user_id = auth.uid()
    AND (
        c.title ILIKE '%' || p_query || '%'
        OR m.content ILIKE '%' || p_query || '%'
    )
    ORDER BY c.updated_at DESC
    LIMIT 20;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 12. Grant service role access for backend operations
GRANT ALL ON public.generated_files TO service_role;
GRANT ALL ON public.tool_executions TO service_role;
GRANT ALL ON public.usage_stats TO service_role;
GRANT ALL ON public.user_api_keys TO service_role;
GRANT EXECUTE ON FUNCTION increment_usage_stats TO service_role;
GRANT EXECUTE ON FUNCTION cleanup_expired_files TO service_role;
GRANT EXECUTE ON FUNCTION get_conversation_with_messages TO service_role;
GRANT EXECUTE ON FUNCTION search_conversations TO service_role;
