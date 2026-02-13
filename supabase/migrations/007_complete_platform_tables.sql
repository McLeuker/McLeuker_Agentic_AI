-- ============================================================================
-- McLeuker AI Platform - Complete Table Sync Migration
-- Version: 007
-- Date: 2026-02-13
-- Purpose: Create ALL missing tables that the backend and frontend reference
--          but don't exist in Supabase yet. Uses IF NOT EXISTS to be safe.
-- ============================================================================

-- ============================================================================
-- 1. USER CREDITS - Core billing table (referenced by credit_service.py)
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_credits (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    balance INTEGER NOT NULL DEFAULT 50,
    lifetime_purchased INTEGER NOT NULL DEFAULT 0,
    lifetime_used INTEGER NOT NULL DEFAULT 0,
    last_daily_claim TIMESTAMPTZ,
    last_monthly_claim TIMESTAMPTZ,
    plan TEXT NOT NULL DEFAULT 'free',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

-- Index for fast lookups
CREATE INDEX IF NOT EXISTS idx_user_credits_user_id ON user_credits(user_id);

-- ============================================================================
-- 2. USER CREDIT SUMMARY - View for billing dashboard (causes 404 currently)
-- ============================================================================
-- This is a VIEW, not a table. It aggregates data from user_credits and
-- credit_transactions for the frontend billing dashboard.
CREATE OR REPLACE VIEW user_credit_summary AS
SELECT
    uc.user_id,
    uc.balance,
    uc.lifetime_purchased,
    uc.lifetime_used,
    uc.plan,
    uc.last_daily_claim,
    uc.last_monthly_claim,
    COALESCE(
        (SELECT SUM(ABS(ct.amount))
         FROM credit_transactions ct
         WHERE ct.user_id = uc.user_id
           AND ct.type = 'deduction'
           AND ct.created_at >= DATE_TRUNC('day', NOW())),
        0
    ) AS credits_used_today,
    COALESCE(
        (SELECT SUM(ABS(ct.amount))
         FROM credit_transactions ct
         WHERE ct.user_id = uc.user_id
           AND ct.type = 'deduction'
           AND ct.created_at >= DATE_TRUNC('month', NOW())),
        0
    ) AS credits_used_this_month,
    COALESCE(
        (SELECT COUNT(*)
         FROM credit_transactions ct
         WHERE ct.user_id = uc.user_id
           AND ct.created_at >= DATE_TRUNC('day', NOW())),
        0
    ) AS transactions_today,
    CASE
        WHEN uc.last_daily_claim IS NULL THEN TRUE
        WHEN uc.last_daily_claim < DATE_TRUNC('day', NOW()) THEN TRUE
        ELSE FALSE
    END AS daily_credits_available,
    uc.updated_at AS last_activity
FROM user_credits uc;

-- ============================================================================
-- 3. CREDIT TRANSACTIONS - Transaction log (referenced by credit_service.py)
-- ============================================================================
CREATE TABLE IF NOT EXISTS credit_transactions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    amount INTEGER NOT NULL,
    balance_after INTEGER NOT NULL DEFAULT 0,
    type TEXT NOT NULL DEFAULT 'deduction',
    description TEXT,
    session_id TEXT,
    operation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created_at ON credit_transactions(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_date ON credit_transactions(user_id, created_at DESC);

-- ============================================================================
-- 4. ACTIVE TASKS - Task persistence (tasks survive page navigation)
-- ============================================================================
CREATE TABLE IF NOT EXISTS active_tasks (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    task_id TEXT NOT NULL UNIQUE,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    conversation_id UUID,
    type TEXT NOT NULL DEFAULT 'search',
    status TEXT NOT NULL DEFAULT 'pending',
    description TEXT,
    input_data JSONB DEFAULT '{}',
    result JSONB DEFAULT '{}',
    steps JSONB DEFAULT '[]',
    current_step INTEGER DEFAULT 0,
    total_steps INTEGER DEFAULT 0,
    progress INTEGER DEFAULT 0,
    error TEXT,
    execution_time_ms INTEGER,
    credits_used INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_active_tasks_task_id ON active_tasks(task_id);
CREATE INDEX IF NOT EXISTS idx_active_tasks_user_id ON active_tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_active_tasks_status ON active_tasks(status);
CREATE INDEX IF NOT EXISTS idx_active_tasks_user_status ON active_tasks(user_id, status);

-- ============================================================================
-- 5. CONVERSATIONS - Chat conversation metadata
-- ============================================================================
CREATE TABLE IF NOT EXISTS conversations (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    title TEXT NOT NULL DEFAULT 'New Conversation',
    mode TEXT NOT NULL DEFAULT 'thinking',
    status TEXT NOT NULL DEFAULT 'active',
    metadata JSONB DEFAULT '{}',
    message_count INTEGER DEFAULT 0,
    last_message_preview TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_conversations_user_id ON conversations(user_id);
CREATE INDEX IF NOT EXISTS idx_conversations_user_status ON conversations(user_id, status);
CREATE INDEX IF NOT EXISTS idx_conversations_updated ON conversations(updated_at DESC);

-- ============================================================================
-- 6. CHAT MESSAGES - Individual messages within conversations
-- ============================================================================
CREATE TABLE IF NOT EXISTS chat_messages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    conversation_id UUID NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
    role TEXT NOT NULL,
    content TEXT NOT NULL,
    metadata JSONB DEFAULT '{}',
    attachments JSONB DEFAULT '[]',
    tokens_used INTEGER DEFAULT 0,
    model TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_chat_messages_conversation ON chat_messages(conversation_id);
CREATE INDEX IF NOT EXISTS idx_chat_messages_conv_created ON chat_messages(conversation_id, created_at);

-- ============================================================================
-- 7. CREDIT PACKAGES - Purchasable credit bundles
-- ============================================================================
CREATE TABLE IF NOT EXISTS credit_packages (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL,
    credits INTEGER NOT NULL,
    price_usd DECIMAL(10,2) NOT NULL,
    stripe_price_id TEXT,
    description TEXT,
    popular BOOLEAN DEFAULT FALSE,
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed default credit packages
INSERT INTO credit_packages (name, credits, price_usd, description, popular, sort_order)
VALUES
    ('Starter', 500, 4.99, '500 credits for casual use', FALSE, 1),
    ('Pro', 2000, 14.99, '2,000 credits — best value', TRUE, 2),
    ('Power', 5000, 29.99, '5,000 credits for heavy users', FALSE, 3),
    ('Enterprise', 20000, 99.99, '20,000 credits for teams', FALSE, 4)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- 8. PRICING PLANS - Subscription tiers
-- ============================================================================
CREATE TABLE IF NOT EXISTS pricing_plans (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    name TEXT NOT NULL UNIQUE,
    display_name TEXT NOT NULL,
    price_monthly_usd DECIMAL(10,2) NOT NULL DEFAULT 0,
    price_yearly_usd DECIMAL(10,2) NOT NULL DEFAULT 0,
    monthly_credits INTEGER NOT NULL DEFAULT 0,
    features JSONB DEFAULT '[]',
    limits JSONB DEFAULT '{}',
    stripe_monthly_price_id TEXT,
    stripe_yearly_price_id TEXT,
    active BOOLEAN DEFAULT TRUE,
    sort_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Seed default pricing plans
INSERT INTO pricing_plans (name, display_name, price_monthly_usd, price_yearly_usd, monthly_credits, features, limits, sort_order)
VALUES
    ('free', 'Free', 0, 0, 50, '["Basic chat", "Web search", "5 daily credits"]', '{"max_file_size_mb": 10, "max_conversations": 10, "modes": ["instant"]}', 1),
    ('pro', 'Pro', 19.99, 199.99, 2000, '["All modes", "File generation", "Priority support", "Agent execution"]', '{"max_file_size_mb": 50, "max_conversations": 100, "modes": ["instant", "thinking", "agent"]}', 2),
    ('enterprise', 'Enterprise', 49.99, 499.99, 10000, '["Everything in Pro", "Agent Swarm", "Custom agents", "API access", "Dedicated support"]', '{"max_file_size_mb": 200, "max_conversations": -1, "modes": ["instant", "thinking", "agent", "swarm"]}', 3)
ON CONFLICT (name) DO NOTHING;

-- ============================================================================
-- 9. USER SUBSCRIPTIONS - Active user subscriptions
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_subscriptions (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    plan_id UUID REFERENCES pricing_plans(id),
    plan_name TEXT NOT NULL DEFAULT 'free',
    status TEXT NOT NULL DEFAULT 'active',
    stripe_subscription_id TEXT,
    stripe_customer_id TEXT,
    current_period_start TIMESTAMPTZ,
    current_period_end TIMESTAMPTZ,
    cancel_at_period_end BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id)
);

CREATE INDEX IF NOT EXISTS idx_user_subscriptions_user_id ON user_subscriptions(user_id);

-- ============================================================================
-- 10. CREDIT CONSUMPTION - Detailed usage tracking per operation
-- ============================================================================
CREATE TABLE IF NOT EXISTS credit_consumption (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    session_id TEXT,
    operation TEXT NOT NULL,
    credits_used INTEGER NOT NULL DEFAULT 0,
    context TEXT,
    mode TEXT,
    conversation_id UUID,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_credit_consumption_user_id ON credit_consumption(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_consumption_created ON credit_consumption(created_at DESC);

-- ============================================================================
-- 11. USAGE LOGS - General usage tracking
-- ============================================================================
CREATE TABLE IF NOT EXISTS usage_logs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    action TEXT NOT NULL,
    details JSONB DEFAULT '{}',
    ip_address TEXT,
    user_agent TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_usage_logs_user_id ON usage_logs(user_id);
CREATE INDEX IF NOT EXISTS idx_usage_logs_created ON usage_logs(created_at DESC);

-- ============================================================================
-- 12. FILE UPLOADS - Track uploaded files
-- ============================================================================
CREATE TABLE IF NOT EXISTS file_uploads (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    conversation_id UUID,
    filename TEXT NOT NULL,
    original_name TEXT,
    file_type TEXT,
    file_size INTEGER,
    mime_type TEXT,
    storage_path TEXT,
    storage_bucket TEXT DEFAULT 'uploads',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_file_uploads_user_id ON file_uploads(user_id);

-- ============================================================================
-- 13. GENERATED FILES - Track generated output files
-- ============================================================================
CREATE TABLE IF NOT EXISTS generated_files (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    file_id TEXT NOT NULL UNIQUE,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    conversation_id UUID,
    filename TEXT NOT NULL,
    file_type TEXT NOT NULL,
    file_size INTEGER,
    storage_path TEXT,
    storage_bucket TEXT DEFAULT 'generated-files',
    download_count INTEGER DEFAULT 0,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_generated_files_file_id ON generated_files(file_id);
CREATE INDEX IF NOT EXISTS idx_generated_files_user_id ON generated_files(user_id);

-- ============================================================================
-- 14. EXECUTION HISTORY - Persistent record of all agent executions
-- ============================================================================
CREATE TABLE IF NOT EXISTS execution_history (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    execution_id TEXT NOT NULL UNIQUE,
    user_id UUID REFERENCES auth.users(id) ON DELETE SET NULL,
    conversation_id UUID,
    task_description TEXT,
    mode TEXT,
    status TEXT NOT NULL DEFAULT 'running',
    steps JSONB DEFAULT '[]',
    result JSONB DEFAULT '{}',
    screenshots JSONB DEFAULT '[]',
    files_generated JSONB DEFAULT '[]',
    credits_used INTEGER DEFAULT 0,
    execution_time_ms INTEGER,
    error TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    started_at TIMESTAMPTZ DEFAULT NOW(),
    completed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_execution_history_execution_id ON execution_history(execution_id);
CREATE INDEX IF NOT EXISTS idx_execution_history_user_id ON execution_history(user_id);
CREATE INDEX IF NOT EXISTS idx_execution_history_status ON execution_history(status);
CREATE INDEX IF NOT EXISTS idx_execution_history_user_status ON execution_history(user_id, status);

-- ============================================================================
-- 15. USERS TABLE - Ensure it has all needed columns
-- ============================================================================
-- Add credit_balance column if it doesn't exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM information_schema.columns
        WHERE table_name = 'users' AND column_name = 'credit_balance'
    ) THEN
        ALTER TABLE users ADD COLUMN credit_balance INTEGER DEFAULT 0;
    END IF;
END $$;

-- ============================================================================
-- 16. RPC FUNCTIONS
-- ============================================================================

-- Function to claim daily credits
CREATE OR REPLACE FUNCTION claim_daily_credits(p_user_id UUID)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_last_claim TIMESTAMPTZ;
    v_balance INTEGER;
    v_daily_amount INTEGER := 5;
BEGIN
    SELECT last_daily_claim, balance INTO v_last_claim, v_balance
    FROM user_credits WHERE user_id = p_user_id;

    IF NOT FOUND THEN
        INSERT INTO user_credits (user_id, balance, last_daily_claim)
        VALUES (p_user_id, 50 + v_daily_amount, NOW());
        RETURN jsonb_build_object('success', true, 'credits_granted', v_daily_amount, 'new_balance', 50 + v_daily_amount);
    END IF;

    IF v_last_claim IS NOT NULL AND v_last_claim >= DATE_TRUNC('day', NOW()) THEN
        RETURN jsonb_build_object('success', false, 'credits_granted', 0, 'message', 'Daily credits already claimed today');
    END IF;

    UPDATE user_credits
    SET balance = balance + v_daily_amount,
        last_daily_claim = NOW(),
        updated_at = NOW()
    WHERE user_id = p_user_id;

    RETURN jsonb_build_object('success', true, 'credits_granted', v_daily_amount, 'new_balance', v_balance + v_daily_amount);
END;
$$;

-- Function to claim monthly bonus credits
CREATE OR REPLACE FUNCTION claim_monthly_bonus(p_user_id UUID)
RETURNS JSONB
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
DECLARE
    v_last_claim TIMESTAMPTZ;
    v_balance INTEGER;
    v_plan TEXT;
    v_monthly_amount INTEGER;
BEGIN
    SELECT last_monthly_claim, balance, plan INTO v_last_claim, v_balance, v_plan
    FROM user_credits WHERE user_id = p_user_id;

    IF NOT FOUND THEN
        RETURN jsonb_build_object('success', false, 'message', 'No credit record found');
    END IF;

    IF v_last_claim IS NOT NULL AND v_last_claim >= DATE_TRUNC('month', NOW()) THEN
        RETURN jsonb_build_object('success', false, 'credits_granted', 0, 'message', 'Monthly bonus already claimed');
    END IF;

    -- Monthly bonus based on plan
    v_monthly_amount := CASE v_plan
        WHEN 'pro' THEN 2000
        WHEN 'enterprise' THEN 10000
        ELSE 0
    END;

    IF v_monthly_amount = 0 THEN
        RETURN jsonb_build_object('success', false, 'message', 'Monthly bonus not available on free plan');
    END IF;

    UPDATE user_credits
    SET balance = balance + v_monthly_amount,
        last_monthly_claim = NOW(),
        updated_at = NOW()
    WHERE user_id = p_user_id;

    RETURN jsonb_build_object('success', true, 'credits_granted', v_monthly_amount, 'new_balance', v_balance + v_monthly_amount);
END;
$$;

-- Function to auto-create user credits on signup
CREATE OR REPLACE FUNCTION handle_new_user_credits()
RETURNS TRIGGER
LANGUAGE plpgsql
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO user_credits (user_id, balance, plan)
    VALUES (NEW.id, 50, 'free')
    ON CONFLICT (user_id) DO NOTHING;
    RETURN NEW;
END;
$$;

-- Trigger to auto-create credits for new users
DROP TRIGGER IF EXISTS on_auth_user_created_credits ON auth.users;
CREATE TRIGGER on_auth_user_created_credits
    AFTER INSERT ON auth.users
    FOR EACH ROW
    EXECUTE FUNCTION handle_new_user_credits();

-- ============================================================================
-- 17. ROW LEVEL SECURITY (RLS)
-- ============================================================================

-- Enable RLS on all tables
ALTER TABLE user_credits ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_transactions ENABLE ROW LEVEL SECURITY;
ALTER TABLE active_tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE conversations ENABLE ROW LEVEL SECURITY;
ALTER TABLE chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_packages ENABLE ROW LEVEL SECURITY;
ALTER TABLE pricing_plans ENABLE ROW LEVEL SECURITY;
ALTER TABLE user_subscriptions ENABLE ROW LEVEL SECURITY;
ALTER TABLE credit_consumption ENABLE ROW LEVEL SECURITY;
ALTER TABLE usage_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE file_uploads ENABLE ROW LEVEL SECURITY;
ALTER TABLE generated_files ENABLE ROW LEVEL SECURITY;
ALTER TABLE execution_history ENABLE ROW LEVEL SECURITY;

-- Users can read their own credits
CREATE POLICY IF NOT EXISTS "users_read_own_credits" ON user_credits
    FOR SELECT USING (auth.uid() = user_id);

-- Service role can do everything (backend uses service key)
CREATE POLICY IF NOT EXISTS "service_full_access_credits" ON user_credits
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "service_full_access_transactions" ON credit_transactions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "service_full_access_tasks" ON active_tasks
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "service_full_access_conversations" ON conversations
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "service_full_access_messages" ON chat_messages
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "service_full_access_subscriptions" ON user_subscriptions
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "service_full_access_consumption" ON credit_consumption
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "service_full_access_usage" ON usage_logs
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "service_full_access_uploads" ON file_uploads
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "service_full_access_generated" ON generated_files
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "service_full_access_execution" ON execution_history
    FOR ALL USING (auth.role() = 'service_role');

-- Public can read credit packages and pricing plans
CREATE POLICY IF NOT EXISTS "public_read_packages" ON credit_packages
    FOR SELECT USING (true);

CREATE POLICY IF NOT EXISTS "public_read_plans" ON pricing_plans
    FOR SELECT USING (true);

-- Users can read their own data
CREATE POLICY IF NOT EXISTS "users_read_own_transactions" ON credit_transactions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "users_read_own_tasks" ON active_tasks
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "users_read_own_conversations" ON conversations
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "users_read_own_messages" ON chat_messages
    FOR SELECT USING (
        conversation_id IN (
            SELECT id FROM conversations WHERE user_id = auth.uid()
        )
    );

CREATE POLICY IF NOT EXISTS "users_read_own_subscriptions" ON user_subscriptions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "users_read_own_uploads" ON file_uploads
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "users_read_own_generated" ON generated_files
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY IF NOT EXISTS "users_read_own_execution" ON execution_history
    FOR SELECT USING (auth.uid() = user_id);

-- ============================================================================
-- 18. SAVED OUTPUTS - Ensure it exists for frontend
-- ============================================================================
CREATE TABLE IF NOT EXISTS saved_outputs (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    conversation_id UUID,
    title TEXT,
    content TEXT,
    output_type TEXT DEFAULT 'text',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS idx_saved_outputs_user_id ON saved_outputs(user_id);

ALTER TABLE saved_outputs ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "service_full_access_saved" ON saved_outputs
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "users_read_own_saved" ON saved_outputs
    FOR SELECT USING (auth.uid() = user_id);

-- ============================================================================
-- 19. USER MEMORY - For RAG and context persistence
-- ============================================================================
CREATE TABLE IF NOT EXISTS user_memory (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    key TEXT NOT NULL,
    value TEXT,
    category TEXT DEFAULT 'general',
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(user_id, key)
);

CREATE INDEX IF NOT EXISTS idx_user_memory_user_id ON user_memory(user_id);

ALTER TABLE user_memory ENABLE ROW LEVEL SECURITY;

CREATE POLICY IF NOT EXISTS "service_full_access_memory" ON user_memory
    FOR ALL USING (auth.role() = 'service_role');

CREATE POLICY IF NOT EXISTS "users_read_own_memory" ON user_memory
    FOR SELECT USING (auth.uid() = user_id);
