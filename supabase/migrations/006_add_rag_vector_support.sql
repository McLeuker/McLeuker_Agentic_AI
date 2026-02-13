-- Migration: Add RAG and Vector Search Support
-- =============================================
-- This migration adds:
-- 1. pgvector extension for vector storage
-- 2. Documents table for RAG
-- 3. Indexes for efficient similarity search
-- 4. Functions for vector operations

-- Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Documents table for RAG
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    content TEXT NOT NULL,
    embedding VECTOR(1536),  -- Adjust dimension based on embedding model
    metadata JSONB DEFAULT '{}',
    source TEXT,
    document_type TEXT DEFAULT 'text',
    chunk_index INTEGER DEFAULT 0,
    total_chunks INTEGER DEFAULT 1,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE
);

-- Indexes for documents
CREATE INDEX IF NOT EXISTS idx_documents_user_id ON documents(user_id);
CREATE INDEX IF NOT EXISTS idx_documents_conversation_id ON documents(conversation_id);
CREATE INDEX IF NOT EXISTS idx_documents_source ON documents(source);
CREATE INDEX IF NOT EXISTS idx_documents_document_type ON documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_created_at ON documents(created_at);

-- HNSW index for fast similarity search (cosine distance)
CREATE INDEX IF NOT EXISTS idx_documents_embedding_cosine 
ON documents 
USING hnsw (embedding vector_cosine_ops)
WITH (m = 16, ef_construction = 64);

-- Alternative: IVFFlat index for larger datasets
-- CREATE INDEX IF NOT EXISTS idx_documents_embedding_ivf
-- ON documents
-- USING ivfflat (embedding vector_cosine_ops)
-- WITH (lists = 100);

-- Function to search documents by similarity
CREATE OR REPLACE FUNCTION search_documents(
    query_embedding VECTOR(1536),
    match_threshold FLOAT DEFAULT 0.7,
    match_count INT DEFAULT 5,
    filter_user_id UUID DEFAULT NULL,
    filter_conversation_id UUID DEFAULT NULL,
    filter_document_type TEXT DEFAULT NULL
)
RETURNS TABLE (
    id UUID,
    content TEXT,
    metadata JSONB,
    source TEXT,
    document_type TEXT,
    similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id,
        d.content,
        d.metadata,
        d.source,
        d.document_type,
        1 - (d.embedding <=> query_embedding) AS similarity
    FROM documents d
    WHERE 
        -- Filter by user if provided
        (filter_user_id IS NULL OR d.user_id = filter_user_id)
        -- Filter by conversation if provided
        AND (filter_conversation_id IS NULL OR d.conversation_id = filter_conversation_id)
        -- Filter by document type if provided
        AND (filter_document_type IS NULL OR d.document_type = filter_document_type)
        -- Similarity threshold
        AND 1 - (d.embedding <=> query_embedding) > match_threshold
    ORDER BY d.embedding <=> query_embedding
    LIMIT match_count;
END;
$$;

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger to auto-update updated_at
CREATE TRIGGER update_documents_updated_at
    BEFORE UPDATE ON documents
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to delete old documents (for cleanup)
CREATE OR REPLACE FUNCTION delete_old_documents(
    older_than_days INT DEFAULT 30,
    filter_user_id UUID DEFAULT NULL
)
RETURNS INT
LANGUAGE plpgsql
AS $$
DECLARE
    deleted_count INT;
BEGIN
    DELETE FROM documents
    WHERE created_at < NOW() - INTERVAL '1 day' * older_than_days
    AND (filter_user_id IS NULL OR user_id = filter_user_id);
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$;

-- Row Level Security (RLS) policies
ALTER TABLE documents ENABLE ROW LEVEL SECURITY;

-- Policy: Users can only see their own documents
CREATE POLICY "Users can view own documents"
    ON documents FOR SELECT
    USING (auth.uid() = user_id);

-- Policy: Users can insert their own documents
CREATE POLICY "Users can insert own documents"
    ON documents FOR INSERT
    WITH CHECK (auth.uid() = user_id);

-- Policy: Users can update their own documents
CREATE POLICY "Users can update own documents"
    ON documents FOR UPDATE
    USING (auth.uid() = user_id);

-- Policy: Users can delete their own documents
CREATE POLICY "Users can delete own documents"
    ON documents FOR DELETE
    USING (auth.uid() = user_id);

-- Admin policy (for service role)
CREATE POLICY "Service role can manage all documents"
    ON documents FOR ALL
    USING (auth.role() = 'service_role');

-- Add execution tracking table
CREATE TABLE IF NOT EXISTS execution_logs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    execution_id UUID NOT NULL,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    step_type TEXT NOT NULL,
    step_content TEXT,
    tool_name TEXT,
    tool_input JSONB,
    tool_output JSONB,
    status TEXT DEFAULT 'pending',
    error TEXT,
    duration_ms INTEGER,
    retry_count INTEGER DEFAULT 0,
    screenshot_url TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for execution logs
CREATE INDEX IF NOT EXISTS idx_execution_logs_execution_id ON execution_logs(execution_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_conversation_id ON execution_logs(conversation_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_user_id ON execution_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_execution_logs_created_at ON execution_logs(created_at);
CREATE INDEX IF NOT EXISTS idx_execution_logs_status ON execution_logs(status);

-- RLS for execution logs
ALTER TABLE execution_logs ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own execution logs"
    ON execution_logs FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage execution logs"
    ON execution_logs FOR ALL
    USING (auth.role() = 'service_role');

-- Add browser sessions table
CREATE TABLE IF NOT EXISTS browser_sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id TEXT UNIQUE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID REFERENCES conversations(id) ON DELETE CASCADE,
    current_url TEXT,
    current_title TEXT,
    viewport_width INTEGER DEFAULT 1280,
    viewport_height INTEGER DEFAULT 720,
    is_active BOOLEAN DEFAULT TRUE,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for browser sessions
CREATE INDEX IF NOT EXISTS idx_browser_sessions_session_id ON browser_sessions(session_id);
CREATE INDEX IF NOT EXISTS idx_browser_sessions_user_id ON browser_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_browser_sessions_conversation_id ON browser_sessions(conversation_id);
CREATE INDEX IF NOT EXISTS idx_browser_sessions_is_active ON browser_sessions(is_active);

-- RLS for browser sessions
ALTER TABLE browser_sessions ENABLE ROW LEVEL SECURITY;

CREATE POLICY "Users can view own browser sessions"
    ON browser_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service role can manage browser sessions"
    ON browser_sessions FOR ALL
    USING (auth.role() = 'service_role');

-- Comments for documentation
COMMENT ON TABLE documents IS 'Stores documents for RAG with vector embeddings';
COMMENT ON COLUMN documents.embedding IS 'Vector embedding for semantic search';
COMMENT ON COLUMN documents.chunk_index IS 'Index of this chunk within the original document';
COMMENT ON FUNCTION search_documents IS 'Performs similarity search on documents using cosine distance';

-- Grant permissions
GRANT ALL ON documents TO authenticated;
GRANT ALL ON execution_logs TO authenticated;
GRANT ALL ON browser_sessions TO authenticated;
GRANT USAGE ON SCHEMA public TO authenticated;
