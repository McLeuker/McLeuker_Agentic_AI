-- ============================================================================
-- McLeuker AI V9.0 - Agentic Execution Schema Migration
-- ============================================================================
-- Run this in Supabase SQL Editor AFTER schema_execution.sql.
-- These tables are ADDITIVE - they do NOT modify existing tables.
-- Adds: credentials, workflows, domain_agent_sessions, file_analyses
-- ============================================================================

-- ============================================================================
-- 1. User Credentials (encrypted, for web automation)
-- ============================================================================

CREATE TABLE IF NOT EXISTS user_credentials (
    id TEXT PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    service TEXT NOT NULL,
    credential_type TEXT NOT NULL DEFAULT 'oauth'
        CHECK (credential_type IN ('oauth', 'api_key', 'username_password', 'cookie', 'token')),
    encrypted_data TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'expired', 'revoked', 'pending')),
    scopes JSONB DEFAULT '[]',
    granted_at TIMESTAMPTZ DEFAULT NOW(),
    expires_at TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, service)
);

-- ============================================================================
-- 2. Workflow Definitions and Runs
-- ============================================================================

CREATE TABLE IF NOT EXISTS workflows (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    name TEXT NOT NULL,
    description TEXT,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'running', 'completed', 'failed', 'paused', 'cancelled')),
    steps JSONB NOT NULL DEFAULT '[]',
    total_steps INTEGER DEFAULT 0,
    completed_steps INTEGER DEFAULT 0,
    execution_time_ms REAL DEFAULT 0,
    context JSONB DEFAULT '{}',
    metadata JSONB DEFAULT '{}',
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS workflow_steps (
    id TEXT PRIMARY KEY,
    workflow_id TEXT NOT NULL REFERENCES workflows(id) ON DELETE CASCADE,
    step_number INTEGER NOT NULL,
    name TEXT NOT NULL,
    tool_name TEXT NOT NULL,
    tool_params JSONB DEFAULT '{}',
    dependencies JSONB DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    result JSONB,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    execution_time_ms REAL DEFAULT 0,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 3. Domain Agent Sessions
-- ============================================================================

CREATE TABLE IF NOT EXISTS domain_agent_sessions (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    execution_id TEXT REFERENCES executions(id) ON DELETE SET NULL,
    domain TEXT NOT NULL,
    agent_name TEXT NOT NULL,
    query TEXT NOT NULL,
    response TEXT,
    confidence REAL DEFAULT 0.0,
    sources JSONB DEFAULT '[]',
    reasoning_layers JSONB DEFAULT '[]',
    execution_time_ms REAL DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 4. File Analysis Records
-- ============================================================================

CREATE TABLE IF NOT EXISTS file_analyses (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    execution_id TEXT REFERENCES executions(id) ON DELETE SET NULL,
    file_name TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER DEFAULT 0,
    analysis_type TEXT NOT NULL DEFAULT 'general'
        CHECK (analysis_type IN ('general', 'image', 'document', 'code', 'data')),
    description TEXT,
    key_elements JSONB DEFAULT '[]',
    extracted_text TEXT,
    confidence REAL DEFAULT 0.0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- 5. Web Automation Sessions (browser screenshots and actions)
-- ============================================================================

CREATE TABLE IF NOT EXISTS web_automation_sessions (
    id TEXT PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    execution_id TEXT REFERENCES executions(id) ON DELETE SET NULL,
    url TEXT,
    page_title TEXT,
    actions JSONB DEFAULT '[]',
    screenshots JSONB DEFAULT '[]',
    status TEXT NOT NULL DEFAULT 'active'
        CHECK (status IN ('active', 'completed', 'failed', 'timeout')),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- ============================================================================
-- Indexes
-- ============================================================================

CREATE INDEX IF NOT EXISTS idx_user_credentials_user_id ON user_credentials(user_id);
CREATE INDEX IF NOT EXISTS idx_user_credentials_service ON user_credentials(service);
CREATE INDEX IF NOT EXISTS idx_workflows_user_id ON workflows(user_id);
CREATE INDEX IF NOT EXISTS idx_workflows_status ON workflows(status);
CREATE INDEX IF NOT EXISTS idx_workflow_steps_workflow_id ON workflow_steps(workflow_id);
CREATE INDEX IF NOT EXISTS idx_domain_agent_sessions_user_id ON domain_agent_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_domain_agent_sessions_domain ON domain_agent_sessions(domain);
CREATE INDEX IF NOT EXISTS idx_file_analyses_user_id ON file_analyses(user_id);
CREATE INDEX IF NOT EXISTS idx_web_automation_sessions_user_id ON web_automation_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_web_automation_sessions_execution_id ON web_automation_sessions(execution_id);

-- ============================================================================
-- Row Level Security
-- ============================================================================

ALTER TABLE user_credentials ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflows ENABLE ROW LEVEL SECURITY;
ALTER TABLE workflow_steps ENABLE ROW LEVEL SECURITY;
ALTER TABLE domain_agent_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_analyses ENABLE ROW LEVEL SECURITY;
ALTER TABLE web_automation_sessions ENABLE ROW LEVEL SECURITY;

-- User policies
CREATE POLICY IF NOT EXISTS "Users can manage own credentials"
    ON user_credentials FOR ALL
    USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can view own workflows"
    ON workflows FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can insert own workflows"
    ON workflows FOR INSERT
    WITH CHECK (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can view own workflow steps"
    ON workflow_steps FOR SELECT
    USING (workflow_id IN (SELECT id FROM workflows WHERE user_id = auth.uid()));

CREATE POLICY IF NOT EXISTS "Users can view own domain sessions"
    ON domain_agent_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can view own file analyses"
    ON file_analyses FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "Users can view own web sessions"
    ON web_automation_sessions FOR SELECT
    USING (auth.uid() = user_id);

-- Service role bypass
CREATE POLICY IF NOT EXISTS "Service role full access credentials"
    ON user_credentials FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "Service role full access workflows"
    ON workflows FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "Service role full access workflow steps"
    ON workflow_steps FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "Service role full access domain sessions"
    ON domain_agent_sessions FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "Service role full access file analyses"
    ON file_analyses FOR ALL
    USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "Service role full access web sessions"
    ON web_automation_sessions FOR ALL
    USING (auth.role() = 'service_role');

-- ============================================================================
-- Updated_at triggers
-- ============================================================================

DROP TRIGGER IF EXISTS trigger_update_credentials_updated_at ON user_credentials;
CREATE TRIGGER trigger_update_credentials_updated_at
    BEFORE UPDATE ON user_credentials
    FOR EACH ROW
    EXECUTE FUNCTION update_execution_updated_at();

DROP TRIGGER IF EXISTS trigger_update_workflows_updated_at ON workflows;
CREATE TRIGGER trigger_update_workflows_updated_at
    BEFORE UPDATE ON workflows
    FOR EACH ROW
    EXECUTE FUNCTION update_execution_updated_at();
