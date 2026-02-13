-- Agent Swarm Database Schema
-- ===========================
-- Complete schema for 100+ agent ecosystem

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==================== AGENT REGISTRY ====================

CREATE TABLE IF NOT EXISTS agent_definitions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(255) UNIQUE NOT NULL,
    description TEXT,
    category VARCHAR(100) NOT NULL,
    subcategory VARCHAR(100),
    version VARCHAR(50) DEFAULT '1.0.0',
    capabilities JSONB DEFAULT '[]',
    required_tools JSONB DEFAULT '[]',
    system_prompt TEXT,
    temperature DECIMAL(3,2) DEFAULT 0.7,
    max_tokens INTEGER DEFAULT 4000,
    llm_model VARCHAR(100) DEFAULT 'kimi-k2.5',
    tags JSONB DEFAULT '[]',
    examples JSONB DEFAULT '[]',
    constraints JSONB DEFAULT '[]',
    metadata JSONB DEFAULT '{}',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_definitions_category ON agent_definitions(category);
CREATE INDEX idx_agent_definitions_name ON agent_definitions(name);
CREATE INDEX idx_agent_definitions_active ON agent_definitions(is_active);

-- ==================== AGENT INSTANCES ====================

CREATE TABLE IF NOT EXISTS agent_instances (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    instance_id VARCHAR(255) UNIQUE NOT NULL,
    agent_name VARCHAR(255) REFERENCES agent_definitions(name),
    status VARCHAR(50) DEFAULT 'idle',
    current_tasks JSONB DEFAULT '[]',
    total_tasks_completed INTEGER DEFAULT 0,
    total_tasks_failed INTEGER DEFAULT 0,
    average_execution_time_ms INTEGER DEFAULT 0,
    health_score DECIMAL(3,2) DEFAULT 1.0,
    error_count INTEGER DEFAULT 0,
    last_active_at TIMESTAMPTZ DEFAULT NOW(),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    metadata JSONB DEFAULT '{}',
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID
);

CREATE INDEX idx_agent_instances_agent_name ON agent_instances(agent_name);
CREATE INDEX idx_agent_instances_status ON agent_instances(status);
CREATE INDEX idx_agent_instances_user ON agent_instances(user_id);
CREATE INDEX idx_agent_instances_conversation ON agent_instances(conversation_id);

-- ==================== AGENT TASKS ====================

CREATE TABLE IF NOT EXISTS agent_tasks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id VARCHAR(255) UNIQUE NOT NULL,
    description TEXT NOT NULL,
    input_data JSONB DEFAULT '{}',
    priority INTEGER DEFAULT 3,
    status VARCHAR(50) DEFAULT 'pending',
    assigned_agent VARCHAR(255),
    parent_task VARCHAR(255),
    subtasks JSONB DEFAULT '[]',
    result JSONB,
    error TEXT,
    execution_time_ms INTEGER,
    context JSONB DEFAULT '{}',
    callback_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID
);

CREATE INDEX idx_agent_tasks_status ON agent_tasks(status);
CREATE INDEX idx_agent_tasks_agent ON agent_tasks(assigned_agent);
CREATE INDEX idx_agent_tasks_user ON agent_tasks(user_id);
CREATE INDEX idx_agent_tasks_conversation ON agent_tasks(conversation_id);
CREATE INDEX idx_agent_tasks_created ON agent_tasks(created_at);

-- ==================== AGENT EXECUTION LOGS ====================

CREATE TABLE IF NOT EXISTS agent_execution_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    task_id VARCHAR(255) REFERENCES agent_tasks(task_id),
    agent_name VARCHAR(255),
    instance_id VARCHAR(255),
    step_type VARCHAR(100),
    step_content TEXT,
    tool_name VARCHAR(255),
    tool_input JSONB,
    tool_output JSONB,
    status VARCHAR(50),
    error TEXT,
    duration_ms INTEGER,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_execution_logs_task ON agent_execution_logs(task_id);
CREATE INDEX idx_execution_logs_agent ON agent_execution_logs(agent_name);
CREATE INDEX idx_execution_logs_created ON agent_execution_logs(created_at);

-- ==================== AGENT COMMUNICATION ====================

CREATE TABLE IF NOT EXISTS agent_messages (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    message_id VARCHAR(255) UNIQUE NOT NULL,
    from_agent VARCHAR(255),
    to_agent VARCHAR(255),
    message_type VARCHAR(100),
    content JSONB,
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX idx_agent_messages_from ON agent_messages(from_agent);
CREATE INDEX idx_agent_messages_to ON agent_messages(to_agent);
CREATE INDEX idx_agent_messages_type ON agent_messages(message_type);

-- ==================== AGENT PERFORMANCE METRICS ====================

CREATE TABLE IF NOT EXISTS agent_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    agent_name VARCHAR(255) REFERENCES agent_definitions(name),
    date DATE DEFAULT CURRENT_DATE,
    tasks_completed INTEGER DEFAULT 0,
    tasks_failed INTEGER DEFAULT 0,
    avg_execution_time_ms INTEGER DEFAULT 0,
    success_rate DECIMAL(5,4) DEFAULT 0,
    user_satisfaction DECIMAL(3,2),
    metadata JSONB DEFAULT '{}',
    UNIQUE(agent_name, date)
);

CREATE INDEX idx_agent_metrics_agent ON agent_metrics(agent_name);
CREATE INDEX idx_agent_metrics_date ON agent_metrics(date);

-- ==================== USER AGENT PREFERENCES ====================

CREATE TABLE IF NOT EXISTS user_agent_preferences (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    agent_name VARCHAR(255) REFERENCES agent_definitions(name),
    preference_score DECIMAL(3,2) DEFAULT 0.5,
    usage_count INTEGER DEFAULT 0,
    last_used_at TIMESTAMPTZ,
    custom_settings JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, agent_name)
);

CREATE INDEX idx_user_preferences_user ON user_agent_preferences(user_id);
CREATE INDEX idx_user_preferences_agent ON user_agent_preferences(agent_name);

-- ==================== AGENT SWARM SESSIONS ====================

CREATE TABLE IF NOT EXISTS agent_swarm_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    session_id VARCHAR(255) UNIQUE NOT NULL,
    user_id UUID REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID,
    active_agents JSONB DEFAULT '[]',
    task_queue JSONB DEFAULT '[]',
    status VARCHAR(50) DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    ended_at TIMESTAMPTZ
);

CREATE INDEX idx_swarm_sessions_user ON agent_swarm_sessions(user_id);
CREATE INDEX idx_swarm_sessions_status ON agent_swarm_sessions(status);

-- ==================== FUNCTIONS ====================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for updated_at
CREATE TRIGGER update_agent_definitions_updated_at
    BEFORE UPDATE ON agent_definitions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER update_agent_swarm_sessions_updated_at
    BEFORE UPDATE ON agent_swarm_sessions
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Function to get agent statistics
CREATE OR REPLACE FUNCTION get_agent_stats(agent_name_param VARCHAR)
RETURNS TABLE (
    total_tasks BIGINT,
    completed_tasks BIGINT,
    failed_tasks BIGINT,
    avg_execution_time BIGINT,
    success_rate DECIMAL
) AS $$
BEGIN
    RETURN QUERY
    SELECT
        COUNT(*)::BIGINT as total_tasks,
        COUNT(*) FILTER (WHERE status = 'completed')::BIGINT as completed_tasks,
        COUNT(*) FILTER (WHERE status = 'failed')::BIGINT as failed_tasks,
        AVG(execution_time_ms)::BIGINT as avg_execution_time,
        CASE 
            WHEN COUNT(*) > 0 THEN 
                COUNT(*) FILTER (WHERE status = 'completed')::DECIMAL / COUNT(*)
            ELSE 0
        END as success_rate
    FROM agent_tasks
    WHERE assigned_agent = agent_name_param;
END;
$$ LANGUAGE plpgsql;

-- Function to clean up old tasks
CREATE OR REPLACE FUNCTION cleanup_old_tasks(days_old INTEGER DEFAULT 30)
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    DELETE FROM agent_tasks
    WHERE created_at < NOW() - INTERVAL '1 day' * days_old
    AND status IN ('completed', 'failed', 'cancelled');
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Function to get popular agents
CREATE OR REPLACE FUNCTION get_popular_agents(limit_count INTEGER DEFAULT 10)
RETURNS TABLE (
    agent_name VARCHAR,
    usage_count BIGINT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        t.assigned_agent::VARCHAR,
        COUNT(*)::BIGINT as usage_count
    FROM agent_tasks t
    WHERE t.created_at > NOW() - INTERVAL '30 days'
    GROUP BY t.assigned_agent
    ORDER BY usage_count DESC
    LIMIT limit_count;
END;
$$ LANGUAGE plpgsql;

-- ==================== ROW LEVEL SECURITY ====================

ALTER TABLE agent_definitions ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_instances ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_execution_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_agent_preferences ENABLE ROW LEVEL SECURITY;
ALTER TABLE agent_swarm_sessions ENABLE ROW LEVEL SECURITY;

-- Policies for agent_definitions (readable by all, writable by service)
CREATE POLICY "Agent definitions readable by all"
    ON agent_definitions FOR SELECT
    USING (is_active = TRUE);

CREATE POLICY "Agent definitions writable by service"
    ON agent_definitions FOR ALL
    USING (auth.role() = 'service_role');

-- Policies for agent_instances
CREATE POLICY "Users can view own agent instances"
    ON agent_instances FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service can manage agent instances"
    ON agent_instances FOR ALL
    USING (auth.role() = 'service_role');

-- Policies for agent_tasks
CREATE POLICY "Users can view own tasks"
    ON agent_tasks FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service can manage tasks"
    ON agent_tasks FOR ALL
    USING (auth.role() = 'service_role');

-- Policies for execution logs
CREATE POLICY "Users can view own execution logs"
    ON agent_execution_logs FOR SELECT
    USING (
        task_id IN (
            SELECT task_id FROM agent_tasks WHERE user_id = auth.uid()
        )
    );

CREATE POLICY "Service can manage execution logs"
    ON agent_execution_logs FOR ALL
    USING (auth.role() = 'service_role');

-- Policies for user preferences
CREATE POLICY "Users can manage own preferences"
    ON user_agent_preferences FOR ALL
    USING (auth.uid() = user_id);

-- Policies for swarm sessions
CREATE POLICY "Users can view own sessions"
    ON agent_swarm_sessions FOR SELECT
    USING (auth.uid() = user_id);

CREATE POLICY "Service can manage sessions"
    ON agent_swarm_sessions FOR ALL
    USING (auth.role() = 'service_role');

-- ==================== SEED DATA ====================

-- Insert sample agent definitions (will be populated by application)
-- Categories: content, data, development, business, research, media, operations, legal, healthcare

INSERT INTO agent_definitions (name, description, category, subcategory, capabilities, tags, is_active)
VALUES
    ('blog_writer', 'Writes engaging blog posts', 'content', 'writing', '["blog_writing", "seo"]', '["writing", "content"]', TRUE),
    ('data_analyst', 'Analyzes datasets and generates insights', 'data', 'analysis', '["data_analysis", "visualization"]', '["data", "analytics"]', TRUE),
    ('frontend_developer', 'Builds web interfaces', 'development', 'frontend', '["react", "vue", "css"]', '["frontend", "web"]', TRUE),
    ('project_manager', 'Plans and manages projects', 'business', 'project_management', '["planning", "coordination"]', '["project", "management"]', TRUE),
    ('market_researcher', 'Conducts market research', 'research', 'market', '["research", "analysis"]', '["research", "market"]', TRUE),
    ('graphic_designer', 'Creates visual designs', 'media', 'design', '["design", "branding"]', '["design", "visual"]', TRUE),
    ('customer_support_agent', 'Handles customer inquiries', 'operations', 'support', '["support", "communication"]', '["support", "customer"]', TRUE),
    ('contract_reviewer', 'Reviews contracts', 'legal', 'contracts', '["review", "analysis"]', '["legal", "contract"]', TRUE)
ON CONFLICT (name) DO NOTHING;

-- ==================== COMMENTS ====================

COMMENT ON TABLE agent_definitions IS 'Registry of all available agents in the swarm';
COMMENT ON TABLE agent_instances IS 'Runtime instances of agents';
COMMENT ON TABLE agent_tasks IS 'Tasks submitted to the agent swarm';
COMMENT ON TABLE agent_execution_logs IS 'Detailed execution logs for agent tasks';
COMMENT ON TABLE agent_messages IS 'Inter-agent communication messages';
COMMENT ON TABLE agent_metrics IS 'Performance metrics for agents';
COMMENT ON TABLE user_agent_preferences IS 'User preferences for specific agents';
COMMENT ON TABLE agent_swarm_sessions IS 'Active agent swarm sessions';
