-- ============================================================
-- McLeuker Agentic AI — Final Complete Schema Migration
-- Migration 008: Create all missing tables, views, storage, RLS
-- Date: 2026-02-13
-- ============================================================
-- This migration creates the 8 missing tables/views that the
-- backend and frontend reference but do not yet exist in Supabase.
-- It also ensures storage buckets and RLS policies are in place.
-- ============================================================

-- ============================================================
-- PART 1: MISSING TABLES
-- ============================================================

-- 1. execution_history — Backend task persistence (TaskPersistenceManager)
CREATE TABLE IF NOT EXISTS public.execution_history (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    task_type TEXT NOT NULL DEFAULT 'agent',
    prompt TEXT,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    result JSONB,
    error TEXT,
    steps JSONB DEFAULT '[]'::jsonb,
    events JSONB DEFAULT '[]'::jsonb,
    metadata JSONB DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_execution_history_user_id ON public.execution_history(user_id);
CREATE INDEX IF NOT EXISTS idx_execution_history_status ON public.execution_history(status);
CREATE INDEX IF NOT EXISTS idx_execution_history_created ON public.execution_history(created_at DESC);

COMMENT ON TABLE public.execution_history IS 'Stores all agent execution history for task persistence and recovery';

-- 2. credit_consumption — Detailed credit usage tracking
CREATE TABLE IF NOT EXISTS public.credit_consumption (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    credits_used NUMERIC(10,2) NOT NULL DEFAULT 0,
    action_type TEXT NOT NULL DEFAULT 'chat',
    mode TEXT DEFAULT 'instant',
    model TEXT DEFAULT 'kimi',
    conversation_id UUID,
    execution_id UUID,
    description TEXT,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_credit_consumption_user ON public.credit_consumption(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_consumption_created ON public.credit_consumption(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_credit_consumption_action ON public.credit_consumption(action_type);

COMMENT ON TABLE public.credit_consumption IS 'Detailed log of every credit consumption event';

-- 3. user_credit_summary — VIEW for billing dashboard
CREATE OR REPLACE VIEW public.user_credit_summary AS
SELECT
    uc.user_id,
    uc.balance AS current_balance,
    uc.lifetime_earned,
    uc.lifetime_spent,
    us.plan_type,
    us.status AS subscription_status,
    us.monthly_credits,
    us.credits_remaining AS monthly_remaining,
    (SELECT COALESCE(SUM(cc.credits_used), 0)
     FROM public.credit_consumption cc
     WHERE cc.user_id = uc.user_id
       AND cc.created_at >= date_trunc('month', now())) AS month_usage,
    (SELECT COALESCE(SUM(cc.credits_used), 0)
     FROM public.credit_consumption cc
     WHERE cc.user_id = uc.user_id
       AND cc.created_at >= date_trunc('day', now())) AS today_usage,
    (SELECT COUNT(*)
     FROM public.credit_consumption cc
     WHERE cc.user_id = uc.user_id
       AND cc.created_at >= date_trunc('month', now())) AS month_requests,
    uc.updated_at AS last_activity
FROM public.user_credits uc
LEFT JOIN public.user_subscriptions us ON us.user_id = uc.user_id;

COMMENT ON VIEW public.user_credit_summary IS 'Aggregated credit summary view for billing dashboard';

-- 4. uploads — Frontend file upload records (separate from file_uploads which is backend)
CREATE TABLE IF NOT EXISTS public.uploads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    file_name TEXT NOT NULL,
    file_type TEXT,
    file_size BIGINT DEFAULT 0,
    storage_path TEXT NOT NULL,
    public_url TEXT,
    category TEXT DEFAULT 'general',
    conversation_id UUID,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_uploads_user ON public.uploads(user_id);
CREATE INDEX IF NOT EXISTS idx_uploads_conversation ON public.uploads(conversation_id);
CREATE INDEX IF NOT EXISTS idx_uploads_created ON public.uploads(created_at DESC);

COMMENT ON TABLE public.uploads IS 'Frontend file upload records linked to Supabase Storage';

-- 5. rag_documents — RAG system document store
CREATE TABLE IF NOT EXISTS public.rag_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL,
    source_type TEXT NOT NULL DEFAULT 'text' CHECK (source_type IN ('text', 'url', 'file', 'conversation')),
    source_url TEXT,
    content TEXT,
    content_hash TEXT,
    token_count INTEGER DEFAULT 0,
    chunk_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_rag_documents_user ON public.rag_documents(user_id);
CREATE INDEX IF NOT EXISTS idx_rag_documents_active ON public.rag_documents(is_active);
CREATE INDEX IF NOT EXISTS idx_rag_documents_source ON public.rag_documents(source_type);

COMMENT ON TABLE public.rag_documents IS 'RAG system document store for knowledge retrieval';

-- 6. rag_chunks — RAG system chunk store with vector embeddings
CREATE TABLE IF NOT EXISTS public.rag_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES public.rag_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL DEFAULT 0,
    content TEXT NOT NULL,
    token_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_rag_chunks_document ON public.rag_chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_rag_chunks_index ON public.rag_chunks(document_id, chunk_index);

COMMENT ON TABLE public.rag_chunks IS 'RAG system text chunks for vector search';

-- Try to add vector column if pgvector extension is available
DO $$
BEGIN
    -- Enable pgvector extension if not already enabled
    CREATE EXTENSION IF NOT EXISTS vector;
    
    -- Add embedding column to rag_chunks
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_schema = 'public' AND table_name = 'rag_chunks' AND column_name = 'embedding'
    ) THEN
        ALTER TABLE public.rag_chunks ADD COLUMN embedding vector(1536);
        CREATE INDEX IF NOT EXISTS idx_rag_chunks_embedding ON public.rag_chunks
            USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'pgvector extension not available - skipping embedding column. RAG will use text search.';
END $$;

-- 7. agent_swarm_sessions — Agent Swarm coordination sessions
CREATE TABLE IF NOT EXISTS public.agent_swarm_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    coordinator_id TEXT,
    task TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'completed', 'failed', 'cancelled')),
    agents_used JSONB DEFAULT '[]'::jsonb,
    result JSONB,
    total_steps INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_swarm_sessions_user ON public.agent_swarm_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_swarm_sessions_status ON public.agent_swarm_sessions(status);
CREATE INDEX IF NOT EXISTS idx_swarm_sessions_created ON public.agent_swarm_sessions(created_at DESC);

COMMENT ON TABLE public.agent_swarm_sessions IS 'Agent Swarm multi-agent coordination sessions';

-- 8. agent_tasks — Individual agent task records within a swarm session
CREATE TABLE IF NOT EXISTS public.agent_tasks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID NOT NULL REFERENCES public.agent_swarm_sessions(id) ON DELETE CASCADE,
    agent_id TEXT NOT NULL,
    agent_name TEXT,
    agent_category TEXT,
    task TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'active', 'completed', 'failed', 'skipped')),
    result JSONB,
    error TEXT,
    tokens_used INTEGER DEFAULT 0,
    execution_time_ms INTEGER DEFAULT 0,
    parent_task_id UUID REFERENCES public.agent_tasks(id),
    metadata JSONB DEFAULT '{}'::jsonb,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_agent_tasks_session ON public.agent_tasks(session_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_agent ON public.agent_tasks(agent_id);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_status ON public.agent_tasks(status);
CREATE INDEX IF NOT EXISTS idx_agent_tasks_parent ON public.agent_tasks(parent_task_id);

COMMENT ON TABLE public.agent_tasks IS 'Individual agent task records within Agent Swarm sessions';


-- ============================================================
-- PART 2: ENSURE EXISTING TABLES HAVE REQUIRED COLUMNS
-- ============================================================

-- Ensure user_credits has all required columns
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_credits' AND column_name = 'lifetime_earned') THEN
        ALTER TABLE public.user_credits ADD COLUMN lifetime_earned NUMERIC(12,2) DEFAULT 0;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_credits' AND column_name = 'lifetime_spent') THEN
        ALTER TABLE public.user_credits ADD COLUMN lifetime_spent NUMERIC(12,2) DEFAULT 0;
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Could not add columns to user_credits: %', SQLERRM;
END $$;

-- Ensure user_subscriptions has all required columns
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_subscriptions' AND column_name = 'monthly_credits') THEN
        ALTER TABLE public.user_subscriptions ADD COLUMN monthly_credits INTEGER DEFAULT 100;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'user_subscriptions' AND column_name = 'credits_remaining') THEN
        ALTER TABLE public.user_subscriptions ADD COLUMN credits_remaining INTEGER DEFAULT 100;
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Could not add columns to user_subscriptions: %', SQLERRM;
END $$;

-- Ensure conversations has mode column
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'conversations' AND column_name = 'mode') THEN
        ALTER TABLE public.conversations ADD COLUMN mode TEXT DEFAULT 'instant';
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Could not add mode column to conversations: %', SQLERRM;
END $$;

-- Ensure chat_messages has all required columns
DO $$
BEGIN
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'chat_messages' AND column_name = 'reasoning') THEN
        ALTER TABLE public.chat_messages ADD COLUMN reasoning TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'chat_messages' AND column_name = 'sources') THEN
        ALTER TABLE public.chat_messages ADD COLUMN sources JSONB DEFAULT '[]'::jsonb;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'chat_messages' AND column_name = 'downloads') THEN
        ALTER TABLE public.chat_messages ADD COLUMN downloads JSONB DEFAULT '[]'::jsonb;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'chat_messages' AND column_name = 'mode') THEN
        ALTER TABLE public.chat_messages ADD COLUMN mode TEXT;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name = 'chat_messages' AND column_name = 'tokens_used') THEN
        ALTER TABLE public.chat_messages ADD COLUMN tokens_used INTEGER DEFAULT 0;
    END IF;
EXCEPTION WHEN OTHERS THEN
    RAISE NOTICE 'Could not add columns to chat_messages: %', SQLERRM;
END $$;


-- ============================================================
-- PART 3: UPDATED_AT TRIGGERS
-- ============================================================

-- Create the trigger function if it doesn't exist
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Add updated_at triggers to all new tables that have updated_at
DO $$
DECLARE
    tbl TEXT;
BEGIN
    FOR tbl IN SELECT unnest(ARRAY[
        'execution_history', 'uploads', 'rag_documents',
        'agent_swarm_sessions'
    ]) LOOP
        EXECUTE format(
            'DROP TRIGGER IF EXISTS update_%s_updated_at ON public.%I; ' ||
            'CREATE TRIGGER update_%s_updated_at BEFORE UPDATE ON public.%I ' ||
            'FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();',
            tbl, tbl, tbl, tbl
        );
    END LOOP;
END $$;


-- ============================================================
-- PART 4: ROW LEVEL SECURITY (RLS)
-- ============================================================

-- Enable RLS on all new tables
ALTER TABLE public.execution_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.credit_consumption ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rag_documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.rag_chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_swarm_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.agent_tasks ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only access their own data

-- execution_history
DROP POLICY IF EXISTS "Users can view own executions" ON public.execution_history;
CREATE POLICY "Users can view own executions" ON public.execution_history
    FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own executions" ON public.execution_history;
CREATE POLICY "Users can insert own executions" ON public.execution_history
    FOR INSERT WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can update own executions" ON public.execution_history;
CREATE POLICY "Users can update own executions" ON public.execution_history
    FOR UPDATE USING (auth.uid() = user_id);

-- credit_consumption
DROP POLICY IF EXISTS "Users can view own consumption" ON public.credit_consumption;
CREATE POLICY "Users can view own consumption" ON public.credit_consumption
    FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Service can insert consumption" ON public.credit_consumption;
CREATE POLICY "Service can insert consumption" ON public.credit_consumption
    FOR INSERT WITH CHECK (true);

-- uploads
DROP POLICY IF EXISTS "Users can view own uploads" ON public.uploads;
CREATE POLICY "Users can view own uploads" ON public.uploads
    FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own uploads" ON public.uploads;
CREATE POLICY "Users can insert own uploads" ON public.uploads
    FOR INSERT WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can delete own uploads" ON public.uploads;
CREATE POLICY "Users can delete own uploads" ON public.uploads
    FOR DELETE USING (auth.uid() = user_id);

-- rag_documents
DROP POLICY IF EXISTS "Users can view own rag docs" ON public.rag_documents;
CREATE POLICY "Users can view own rag docs" ON public.rag_documents
    FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own rag docs" ON public.rag_documents;
CREATE POLICY "Users can insert own rag docs" ON public.rag_documents
    FOR INSERT WITH CHECK (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can update own rag docs" ON public.rag_documents;
CREATE POLICY "Users can update own rag docs" ON public.rag_documents
    FOR UPDATE USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can delete own rag docs" ON public.rag_documents;
CREATE POLICY "Users can delete own rag docs" ON public.rag_documents
    FOR DELETE USING (auth.uid() = user_id);

-- rag_chunks (access via document ownership)
DROP POLICY IF EXISTS "Users can view own rag chunks" ON public.rag_chunks;
CREATE POLICY "Users can view own rag chunks" ON public.rag_chunks
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.rag_documents rd WHERE rd.id = document_id AND rd.user_id = auth.uid())
    );
DROP POLICY IF EXISTS "Service can insert rag chunks" ON public.rag_chunks;
CREATE POLICY "Service can insert rag chunks" ON public.rag_chunks
    FOR INSERT WITH CHECK (true);

-- agent_swarm_sessions
DROP POLICY IF EXISTS "Users can view own swarm sessions" ON public.agent_swarm_sessions;
CREATE POLICY "Users can view own swarm sessions" ON public.agent_swarm_sessions
    FOR SELECT USING (auth.uid() = user_id);
DROP POLICY IF EXISTS "Users can insert own swarm sessions" ON public.agent_swarm_sessions;
CREATE POLICY "Users can insert own swarm sessions" ON public.agent_swarm_sessions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

-- agent_tasks (access via session ownership)
DROP POLICY IF EXISTS "Users can view own agent tasks" ON public.agent_tasks;
CREATE POLICY "Users can view own agent tasks" ON public.agent_tasks
    FOR SELECT USING (
        EXISTS (SELECT 1 FROM public.agent_swarm_sessions s WHERE s.id = session_id AND s.user_id = auth.uid())
    );
DROP POLICY IF EXISTS "Service can insert agent tasks" ON public.agent_tasks;
CREATE POLICY "Service can insert agent tasks" ON public.agent_tasks
    FOR INSERT WITH CHECK (true);
DROP POLICY IF EXISTS "Service can update agent tasks" ON public.agent_tasks;
CREATE POLICY "Service can update agent tasks" ON public.agent_tasks
    FOR UPDATE USING (true);

-- Service role bypass: Allow the backend (service_role key) full access
-- The service_role key bypasses RLS by default in Supabase, so no additional policies needed.


-- ============================================================
-- PART 5: STORAGE BUCKETS
-- ============================================================

-- Create storage buckets if they don't exist
INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES ('uploads', 'uploads', false, 52428800, -- 50MB limit
    ARRAY['image/jpeg','image/png','image/gif','image/webp','image/svg+xml',
          'application/pdf','application/msword',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'application/vnd.ms-excel',
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'application/vnd.ms-powerpoint',
          'application/vnd.openxmlformats-officedocument.presentationml.presentation',
          'text/plain','text/csv','text/markdown',
          'application/json','application/zip',
          'video/mp4','video/webm','audio/mpeg','audio/wav'])
ON CONFLICT (id) DO NOTHING;

INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
VALUES ('generated-files', 'generated-files', true, 104857600, NULL) -- 100MB, all types
ON CONFLICT (id) DO NOTHING;

-- Storage RLS policies for 'uploads' bucket
DROP POLICY IF EXISTS "Users can upload own files" ON storage.objects;
CREATE POLICY "Users can upload own files" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'uploads' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

DROP POLICY IF EXISTS "Users can view own uploads" ON storage.objects;
CREATE POLICY "Users can view own uploads" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'uploads' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

DROP POLICY IF EXISTS "Users can delete own uploads" ON storage.objects;
CREATE POLICY "Users can delete own uploads" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'uploads' AND
        auth.uid()::text = (storage.foldername(name))[1]
    );

-- Storage RLS for 'generated-files' bucket (public read, service write)
DROP POLICY IF EXISTS "Public can read generated files" ON storage.objects;
CREATE POLICY "Public can read generated files" ON storage.objects
    FOR SELECT USING (bucket_id = 'generated-files');

DROP POLICY IF EXISTS "Service can write generated files" ON storage.objects;
CREATE POLICY "Service can write generated files" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'generated-files');


-- ============================================================
-- PART 6: HELPER FUNCTIONS
-- ============================================================

-- Function to get user credit summary (used by credit_service.py)
CREATE OR REPLACE FUNCTION public.get_user_credit_summary(p_user_id UUID)
RETURNS TABLE (
    current_balance NUMERIC,
    lifetime_earned NUMERIC,
    lifetime_spent NUMERIC,
    plan_type TEXT,
    subscription_status TEXT,
    monthly_credits INTEGER,
    monthly_remaining INTEGER,
    month_usage NUMERIC,
    today_usage NUMERIC,
    month_requests BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        uc.balance,
        uc.lifetime_earned,
        uc.lifetime_spent,
        us.plan_type,
        us.status,
        us.monthly_credits,
        us.credits_remaining,
        COALESCE((SELECT SUM(cc.credits_used) FROM public.credit_consumption cc
                  WHERE cc.user_id = p_user_id AND cc.created_at >= date_trunc('month', now())), 0),
        COALESCE((SELECT SUM(cc.credits_used) FROM public.credit_consumption cc
                  WHERE cc.user_id = p_user_id AND cc.created_at >= date_trunc('day', now())), 0),
        COALESCE((SELECT COUNT(*) FROM public.credit_consumption cc
                  WHERE cc.user_id = p_user_id AND cc.created_at >= date_trunc('month', now())), 0)
    FROM public.user_credits uc
    LEFT JOIN public.user_subscriptions us ON us.user_id = uc.user_id
    WHERE uc.user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to log credit consumption (called by backend)
CREATE OR REPLACE FUNCTION public.log_credit_consumption(
    p_user_id UUID,
    p_credits NUMERIC,
    p_action TEXT DEFAULT 'chat',
    p_mode TEXT DEFAULT 'instant',
    p_model TEXT DEFAULT 'kimi',
    p_description TEXT DEFAULT NULL
)
RETURNS UUID AS $$
DECLARE
    v_id UUID;
BEGIN
    INSERT INTO public.credit_consumption (user_id, credits_used, action_type, mode, model, description)
    VALUES (p_user_id, p_credits, p_action, p_mode, p_model, p_description)
    RETURNING id INTO v_id;
    
    -- Update lifetime_spent in user_credits
    UPDATE public.user_credits
    SET lifetime_spent = COALESCE(lifetime_spent, 0) + p_credits,
        balance = GREATEST(0, balance - p_credits),
        updated_at = now()
    WHERE user_id = p_user_id;
    
    RETURN v_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to search RAG chunks by text similarity
CREATE OR REPLACE FUNCTION public.search_rag_chunks(
    p_query TEXT,
    p_user_id UUID DEFAULT NULL,
    p_limit INTEGER DEFAULT 10
)
RETURNS TABLE (
    chunk_id UUID,
    document_id UUID,
    content TEXT,
    document_title TEXT,
    similarity FLOAT
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        rc.id,
        rc.document_id,
        rc.content,
        rd.title,
        ts_rank(to_tsvector('english', rc.content), plainto_tsquery('english', p_query))::FLOAT AS sim
    FROM public.rag_chunks rc
    JOIN public.rag_documents rd ON rd.id = rc.document_id
    WHERE rd.is_active = true
      AND (p_user_id IS NULL OR rd.user_id = p_user_id)
      AND to_tsvector('english', rc.content) @@ plainto_tsquery('english', p_query)
    ORDER BY sim DESC
    LIMIT p_limit;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;


-- ============================================================
-- PART 7: GRANT PERMISSIONS
-- ============================================================

-- Grant access to the anon and authenticated roles for new tables
GRANT SELECT ON public.execution_history TO anon, authenticated;
GRANT INSERT, UPDATE ON public.execution_history TO authenticated;

GRANT SELECT ON public.credit_consumption TO anon, authenticated;
GRANT INSERT ON public.credit_consumption TO authenticated;

GRANT SELECT ON public.user_credit_summary TO anon, authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE ON public.uploads TO authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE ON public.rag_documents TO authenticated;
GRANT SELECT, INSERT ON public.rag_chunks TO authenticated;

GRANT SELECT, INSERT ON public.agent_swarm_sessions TO authenticated;
GRANT SELECT, INSERT, UPDATE ON public.agent_tasks TO authenticated;

-- Grant RPC function execution
GRANT EXECUTE ON FUNCTION public.get_user_credit_summary(UUID) TO anon, authenticated;
GRANT EXECUTE ON FUNCTION public.log_credit_consumption(UUID, NUMERIC, TEXT, TEXT, TEXT, TEXT) TO authenticated;
GRANT EXECUTE ON FUNCTION public.search_rag_chunks(TEXT, UUID, INTEGER) TO authenticated;


-- ============================================================
-- DONE
-- ============================================================
-- Summary of changes:
-- - Created 8 missing tables: execution_history, credit_consumption,
--   uploads, rag_documents, rag_chunks, agent_swarm_sessions, agent_tasks
-- - Created 1 view: user_credit_summary
-- - Added missing columns to existing tables (user_credits, user_subscriptions,
--   conversations, chat_messages)
-- - Created updated_at triggers for new tables
-- - Enabled RLS on all new tables with user-scoped policies
-- - Created 2 storage buckets: uploads, generated-files
-- - Created 3 helper functions: get_user_credit_summary,
--   log_credit_consumption, search_rag_chunks
-- - Granted proper permissions to anon and authenticated roles
