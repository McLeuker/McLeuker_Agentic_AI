-- ============================================================================
-- McLeuker AI V6.0 - Agentic Execution Schema
-- ============================================================================
-- Run this in Supabase SQL Editor to add execution tracking tables.
-- These tables are ADDITIVE - they do NOT modify existing tables.
-- ============================================================================

-- Execution runs (top-level tracking)
CREATE TABLE IF NOT EXISTS executions (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    user_request TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','planning','researching','executing','verifying','retrying','delivering','completed','failed','cancelled','paused')),
    final_output TEXT,
    plan_id TEXT,
    plan_reasoning TEXT,
    total_steps INTEGER DEFAULT 0,
    completed_steps INTEGER DEFAULT 0,
    total_tokens INTEGER DEFAULT 0,
    execution_time_seconds REAL DEFAULT 0,
    context JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Individual execution steps
CREATE TABLE IF NOT EXISTS execution_steps (
    id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    step_type TEXT NOT NULL
        CHECK (step_type IN ('plan','research','code','browser','verify','deliver','think')),
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending','planning','researching','executing','verifying','retrying','delivering','completed','failed','cancelled','paused')),
    agent TEXT DEFAULT 'kimi',
    instruction TEXT NOT NULL,
    input_data JSONB DEFAULT '{}',
    output_data JSONB,
    reasoning TEXT,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    execution_time_ms REAL DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Execution artifacts (generated files, code outputs, etc.)
CREATE TABLE IF NOT EXISTS execution_artifacts (
    id TEXT PRIMARY KEY,
    execution_id TEXT NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    step_id TEXT REFERENCES execution_steps(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    artifact_type TEXT NOT NULL
        CHECK (artifact_type IN ('code','document','image','data','other')),
    content TEXT,
    file_path TEXT,
    public_url TEXT,
    size_bytes INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Execution events (for real-time streaming history)
CREATE TABLE IF NOT EXISTS execution_events (
    id BIGSERIAL PRIMARY KEY,
    execution_id TEXT NOT NULL REFERENCES executions(id) ON DELETE CASCADE,
    event_type TEXT NOT NULL,
    event_data JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_executions_user_id ON executions(user_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_created_at ON executions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_execution_steps_execution_id ON execution_steps(execution_id);
CREATE INDEX IF NOT EXISTS idx_execution_steps_status ON execution_steps(status);
CREATE INDEX IF NOT EXISTS idx_execution_artifacts_execution_id ON execution_artifacts(execution_id);
CREATE INDEX IF NOT EXISTS idx_execution_events_execution_id ON execution_events(execution_id);
CREATE INDEX IF NOT EXISTS idx_execution_events_created_at ON execution_events(created_at DESC);

-- Enable Row Level Security
ALTER TABLE executions ENABLE ROW LEVEL SECURITY;
ALTER TABLE execution_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE execution_artifacts ENABLE ROW LEVEL SECURITY;
ALTER TABLE execution_events ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only see their own executions
CREATE POLICY IF NOT EXISTS "Users can view own executions"
    ON executions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can insert own executions"
    ON executions FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can update own executions"
    ON executions FOR UPDATE
    USING (auth.uid() = user_id);

-- Steps, artifacts, events inherit access from parent execution
CREATE POLICY IF NOT EXISTS "Users can view own execution steps"
    ON execution_steps FOR SELECT
    USING (execution_id IN (SELECT id FROM executions WHERE user_id = auth.uid()));

CREATE POLICY IF NOT EXISTS "Users can view own execution artifacts"
    ON execution_artifacts FOR SELECT
    USING (execution_id IN (SELECT id FROM executions WHERE user_id = auth.uid()));

CREATE POLICY IF NOT EXISTS "Users can view own execution events"
    ON execution_events FOR SELECT
    USING (execution_id IN (SELECT id FROM executions WHERE user_id = auth.uid()));

-- Service role bypass for backend operations
CREATE POLICY IF NOT EXISTS "Service role full access executions"
    ON executions FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "Service role full access steps"
    ON execution_steps FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "Service role full access artifacts"
    ON execution_artifacts FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "Service role full access events"
    ON execution_events FOR ALL
    USING (auth.role() = 'service_role');

-- Updated_at trigger
CREATE OR REPLACE FUNCTION update_execution_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS trigger_update_execution_updated_at ON executions;
CREATE TRIGGER trigger_update_execution_updated_at
    BEFORE UPDATE ON executions
    FOR EACH ROW
    EXECUTE FUNCTION update_execution_updated_at();
