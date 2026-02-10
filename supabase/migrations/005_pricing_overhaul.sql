-- =====================================================
-- McLeuker AI V5.5 - Pricing Overhaul Migration
-- New tiers: Free / Standard ($19) / Pro ($99) / Enterprise (contact)
-- 18% annual discount, domain access gating, daily fresh credits
-- =====================================================

-- 1. Add new columns to profiles table for domain access and daily credits
ALTER TABLE public.profiles 
  ADD COLUMN IF NOT EXISTS daily_credits_balance INTEGER DEFAULT 0,
  ADD COLUMN IF NOT EXISTS daily_credits_last_refresh DATE,
  ADD COLUMN IF NOT EXISTS domain_access TEXT[] DEFAULT ARRAY['all', 'fashion']::TEXT[],
  ADD COLUMN IF NOT EXISTS max_concurrent_tasks INTEGER DEFAULT 1,
  ADD COLUMN IF NOT EXISTS can_use_deep_search BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS can_use_agent_mode BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS can_use_creative BOOLEAN DEFAULT FALSE,
  ADD COLUMN IF NOT EXISTS can_export_files BOOLEAN DEFAULT FALSE;

-- 2. Update subscription_tier check constraint to include 'standard'
ALTER TABLE public.profiles DROP CONSTRAINT IF EXISTS profiles_subscription_tier_check;
ALTER TABLE public.profiles ADD CONSTRAINT profiles_subscription_tier_check 
  CHECK (subscription_tier IN ('free', 'standard', 'pro', 'enterprise'));

-- 3. Add columns to users table (if it exists separately)
DO $$ 
BEGIN
  IF EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'users' AND table_schema = 'public') THEN
    EXECUTE 'ALTER TABLE public.users ADD COLUMN IF NOT EXISTS daily_credits_balance INTEGER DEFAULT 0';
    EXECUTE 'ALTER TABLE public.users ADD COLUMN IF NOT EXISTS daily_credits_last_refresh DATE';
    EXECUTE 'ALTER TABLE public.users ADD COLUMN IF NOT EXISTS domain_access TEXT[] DEFAULT ARRAY[''all'', ''fashion'']::TEXT[]';
    EXECUTE 'ALTER TABLE public.users ADD COLUMN IF NOT EXISTS max_concurrent_tasks INTEGER DEFAULT 1';
    EXECUTE 'ALTER TABLE public.users ADD COLUMN IF NOT EXISTS can_use_deep_search BOOLEAN DEFAULT FALSE';
    EXECUTE 'ALTER TABLE public.users ADD COLUMN IF NOT EXISTS can_use_agent_mode BOOLEAN DEFAULT FALSE';
    EXECUTE 'ALTER TABLE public.users ADD COLUMN IF NOT EXISTS can_use_creative BOOLEAN DEFAULT FALSE';
    EXECUTE 'ALTER TABLE public.users ADD COLUMN IF NOT EXISTS can_export_files BOOLEAN DEFAULT FALSE';
  END IF;
END $$;

-- 4. Create plan_features table for detailed feature comparison
CREATE TABLE IF NOT EXISTS public.plan_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    plan_slug TEXT NOT NULL,
    feature_key TEXT NOT NULL,
    feature_label TEXT NOT NULL,
    feature_value TEXT, -- 'true', 'false', '5', 'Unlimited', etc.
    feature_category TEXT DEFAULT 'general', -- 'general', 'credits', 'domains', 'capabilities', 'support'
    display_order INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(plan_slug, feature_key)
);

-- 5. Insert plan features for comparison table
-- Free Plan Features
INSERT INTO public.plan_features (plan_slug, feature_key, feature_label, feature_value, feature_category, display_order) VALUES
('free', 'daily_credits', 'Daily Fresh Credits', '15', 'credits', 1),
('free', 'monthly_credits', 'Monthly Credits', '~450', 'credits', 2),
('free', 'daily_credit_usage', 'Daily Credits Usable For', 'Instant Search only', 'credits', 3),
('free', 'credit_packs', 'Credit Pack Purchases', 'Starting at $10', 'credits', 4),
('free', 'domain_access', 'Domain Access', '2 domains (Global + 1)', 'domains', 5),
('free', 'instant_search', 'Instant Search', 'true', 'capabilities', 6),
('free', 'deep_search', 'Deep Search', 'false', 'capabilities', 7),
('free', 'agent_mode', 'Agent Mode', 'false', 'capabilities', 8),
('free', 'creative_mode', 'Creative Mode', 'false', 'capabilities', 9),
('free', 'file_exports', 'File Exports (PDF, Excel, PPT)', 'false', 'capabilities', 10),
('free', 'concurrent_tasks', 'Concurrent Tasks', '1', 'capabilities', 11),
('free', 'real_time_data', 'Real-Time Data', 'true', 'capabilities', 12),
('free', 'source_citations', 'Source Citations', 'true', 'capabilities', 13),
('free', 'reasoning_display', 'Reasoning Display', 'Basic', 'capabilities', 14),
('free', 'support', 'Support', 'Community', 'support', 15),

-- Standard Plan Features
('standard', 'daily_credits', 'Daily Fresh Credits', '50', 'credits', 1),
('standard', 'monthly_credits', 'Monthly Credits', '~1,500', 'credits', 2),
('standard', 'daily_credit_usage', 'Daily Credits Usable For', 'Instant Search only', 'credits', 3),
('standard', 'credit_packs', 'Credit Pack Purchases', 'Starting at $10', 'credits', 4),
('standard', 'domain_access', 'Domain Access', '5 domains', 'domains', 5),
('standard', 'instant_search', 'Instant Search', 'true', 'capabilities', 6),
('standard', 'deep_search', 'Deep Search', 'true', 'capabilities', 7),
('standard', 'agent_mode', 'Agent Mode', 'false', 'capabilities', 8),
('standard', 'creative_mode', 'Creative Mode', 'false', 'capabilities', 9),
('standard', 'file_exports', 'File Exports (PDF, Excel, PPT)', 'true', 'capabilities', 10),
('standard', 'concurrent_tasks', 'Concurrent Tasks', '3', 'capabilities', 11),
('standard', 'real_time_data', 'Real-Time Data', 'true', 'capabilities', 12),
('standard', 'source_citations', 'Source Citations', 'true', 'capabilities', 13),
('standard', 'reasoning_display', 'Reasoning Display', 'Full', 'capabilities', 14),
('standard', 'support', 'Support', 'Email', 'support', 15),

-- Pro Plan Features
('pro', 'daily_credits', 'Daily Fresh Credits', '300', 'credits', 1),
('pro', 'monthly_credits', 'Monthly Credits', '~9,000', 'credits', 2),
('pro', 'daily_credit_usage', 'Daily Credits Usable For', 'Instant Search only', 'credits', 3),
('pro', 'credit_packs', 'Credit Pack Purchases', 'Starting at $10', 'credits', 4),
('pro', 'domain_access', 'Domain Access', 'All 10 domains', 'domains', 5),
('pro', 'instant_search', 'Instant Search', 'true', 'capabilities', 6),
('pro', 'deep_search', 'Deep Search', 'true', 'capabilities', 7),
('pro', 'agent_mode', 'Agent Mode', 'true', 'capabilities', 8),
('pro', 'creative_mode', 'Creative Mode', 'true', 'capabilities', 9),
('pro', 'file_exports', 'File Exports (PDF, Excel, PPT)', 'true', 'capabilities', 10),
('pro', 'concurrent_tasks', 'Concurrent Tasks', 'Unlimited', 'capabilities', 11),
('pro', 'real_time_data', 'Real-Time Data', 'true', 'capabilities', 12),
('pro', 'source_citations', 'Source Citations', 'true', 'capabilities', 13),
('pro', 'reasoning_display', 'Reasoning Display', 'Full + Advanced', 'capabilities', 14),
('pro', 'support', 'Support', 'Priority', 'support', 15),

-- Enterprise Plan Features
('enterprise', 'daily_credits', 'Daily Fresh Credits', 'Custom', 'credits', 1),
('enterprise', 'monthly_credits', 'Monthly Credits', 'Custom', 'credits', 2),
('enterprise', 'daily_credit_usage', 'Daily Credits Usable For', 'All modes', 'credits', 3),
('enterprise', 'credit_packs', 'Credit Pack Purchases', 'Custom pricing', 'credits', 4),
('enterprise', 'domain_access', 'Domain Access', 'All + Custom domains', 'domains', 5),
('enterprise', 'instant_search', 'Instant Search', 'true', 'capabilities', 6),
('enterprise', 'deep_search', 'Deep Search', 'true', 'capabilities', 7),
('enterprise', 'agent_mode', 'Agent Mode', 'true', 'capabilities', 8),
('enterprise', 'creative_mode', 'Creative Mode', 'true', 'capabilities', 9),
('enterprise', 'file_exports', 'File Exports (PDF, Excel, PPT)', 'true', 'capabilities', 10),
('enterprise', 'concurrent_tasks', 'Concurrent Tasks', 'Unlimited', 'capabilities', 11),
('enterprise', 'real_time_data', 'Real-Time Data', 'true', 'capabilities', 12),
('enterprise', 'source_citations', 'Source Citations', 'true', 'capabilities', 13),
('enterprise', 'reasoning_display', 'Reasoning Display', 'Full + Advanced + Custom', 'capabilities', 14),
('enterprise', 'support', 'Support', 'Dedicated Account Manager + SLA', 'support', 15)

ON CONFLICT (plan_slug, feature_key) DO UPDATE SET
  feature_label = EXCLUDED.feature_label,
  feature_value = EXCLUDED.feature_value,
  feature_category = EXCLUDED.feature_category,
  display_order = EXCLUDED.display_order;

-- 6. Create function to refresh daily credits
CREATE OR REPLACE FUNCTION public.refresh_daily_credits(p_user_id UUID)
RETURNS JSONB AS $$
DECLARE
    v_plan TEXT;
    v_last_refresh DATE;
    v_daily_amount INTEGER;
    v_new_balance INTEGER;
BEGIN
    -- Get user's plan and last refresh date
    SELECT subscription_plan, daily_credits_last_refresh
    INTO v_plan, v_last_refresh
    FROM public.users
    WHERE user_id = p_user_id;

    -- If already refreshed today, return current balance
    IF v_last_refresh = CURRENT_DATE THEN
        SELECT daily_credits_balance INTO v_new_balance
        FROM public.users WHERE user_id = p_user_id;
        RETURN jsonb_build_object('refreshed', false, 'balance', COALESCE(v_new_balance, 0), 'reason', 'already_refreshed_today');
    END IF;

    -- Determine daily credit amount based on plan
    v_daily_amount := CASE COALESCE(v_plan, 'free')
        WHEN 'free' THEN 15
        WHEN 'standard' THEN 50
        WHEN 'pro' THEN 300
        WHEN 'enterprise' THEN 500
        ELSE 15
    END;

    -- Refresh: set balance to daily amount (not accumulate)
    UPDATE public.users
    SET daily_credits_balance = v_daily_amount,
        daily_credits_last_refresh = CURRENT_DATE
    WHERE user_id = p_user_id;

    RETURN jsonb_build_object('refreshed', true, 'balance', v_daily_amount, 'daily_amount', v_daily_amount);
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 7. Create function to check domain access
CREATE OR REPLACE FUNCTION public.check_domain_access(p_user_id UUID, p_domain TEXT)
RETURNS JSONB AS $$
DECLARE
    v_plan TEXT;
    v_allowed_domains TEXT[];
    v_has_access BOOLEAN;
BEGIN
    SELECT COALESCE(subscription_plan, 'free') INTO v_plan
    FROM public.users WHERE user_id = p_user_id;

    -- Define allowed domains per plan
    v_allowed_domains := CASE v_plan
        WHEN 'free' THEN ARRAY['all', 'fashion']
        WHEN 'standard' THEN ARRAY['all', 'fashion', 'beauty', 'skincare', 'sustainability', 'fashion-tech']
        WHEN 'pro' THEN ARRAY['all', 'fashion', 'beauty', 'skincare', 'sustainability', 'fashion-tech', 'catwalks', 'culture', 'textile', 'lifestyle']
        WHEN 'enterprise' THEN ARRAY['all', 'fashion', 'beauty', 'skincare', 'sustainability', 'fashion-tech', 'catwalks', 'culture', 'textile', 'lifestyle']
        ELSE ARRAY['all', 'fashion']
    END;

    v_has_access := p_domain = ANY(v_allowed_domains);

    RETURN jsonb_build_object(
        'has_access', v_has_access,
        'plan', v_plan,
        'allowed_domains', to_jsonb(v_allowed_domains),
        'requested_domain', p_domain,
        'upgrade_required', NOT v_has_access
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 8. Create function to deduct credits with pause-on-empty
CREATE OR REPLACE FUNCTION public.deduct_credits_with_pause(
    p_user_id UUID,
    p_amount INTEGER,
    p_task_type TEXT,
    p_description TEXT DEFAULT NULL
)
RETURNS JSONB AS $$
DECLARE
    v_plan TEXT;
    v_credit_balance INTEGER;
    v_daily_balance INTEGER;
    v_can_use_daily BOOLEAN;
    v_deducted_from TEXT;
    v_remaining INTEGER;
BEGIN
    -- Get user state
    SELECT COALESCE(subscription_plan, 'free'), COALESCE(credit_balance, 0), COALESCE(daily_credits_balance, 0)
    INTO v_plan, v_credit_balance, v_daily_balance
    FROM public.users WHERE user_id = p_user_id;

    -- Daily credits can only be used for instant search
    v_can_use_daily := (p_task_type = 'instant_search' OR p_task_type = 'simple_query');

    -- Try to deduct from purchased/subscription credits first
    IF v_credit_balance >= p_amount THEN
        UPDATE public.users SET credit_balance = credit_balance - p_amount WHERE user_id = p_user_id;
        v_deducted_from := 'purchased_credits';
        v_remaining := v_credit_balance - p_amount;
    -- Then try daily credits (only for instant search)
    ELSIF v_can_use_daily AND v_daily_balance >= p_amount THEN
        UPDATE public.users SET daily_credits_balance = daily_credits_balance - p_amount WHERE user_id = p_user_id;
        v_deducted_from := 'daily_credits';
        v_remaining := v_daily_balance - p_amount;
    -- Insufficient credits - pause
    ELSE
        RETURN jsonb_build_object(
            'success', false,
            'paused', true,
            'reason', 'insufficient_credits',
            'credit_balance', v_credit_balance,
            'daily_balance', v_daily_balance,
            'required', p_amount,
            'task_type', p_task_type,
            'message', 'Insufficient credits. Purchase more credits to continue this task.'
        );
    END IF;

    -- Log the transaction
    INSERT INTO public.credit_transactions (user_id, amount, type, description, balance_after)
    VALUES (p_user_id, -p_amount, 'usage', COALESCE(p_description, p_task_type), v_remaining);

    RETURN jsonb_build_object(
        'success', true,
        'paused', false,
        'deducted', p_amount,
        'deducted_from', v_deducted_from,
        'remaining', v_remaining
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- 9. Function to set plan permissions when subscription changes
CREATE OR REPLACE FUNCTION public.apply_plan_permissions(p_user_id UUID, p_plan TEXT)
RETURNS VOID AS $$
BEGIN
    UPDATE public.users SET
        subscription_plan = p_plan,
        can_use_deep_search = (p_plan IN ('standard', 'pro', 'enterprise')),
        can_use_agent_mode = (p_plan IN ('pro', 'enterprise')),
        can_use_creative = (p_plan IN ('pro', 'enterprise')),
        can_export_files = (p_plan IN ('standard', 'pro', 'enterprise')),
        max_concurrent_tasks = CASE p_plan
            WHEN 'free' THEN 1
            WHEN 'standard' THEN 3
            WHEN 'pro' THEN 100
            WHEN 'enterprise' THEN 100
            ELSE 1
        END,
        domain_access = CASE p_plan
            WHEN 'free' THEN ARRAY['all', 'fashion']
            WHEN 'standard' THEN ARRAY['all', 'fashion', 'beauty', 'skincare', 'sustainability', 'fashion-tech']
            WHEN 'pro' THEN ARRAY['all', 'fashion', 'beauty', 'skincare', 'sustainability', 'fashion-tech', 'catwalks', 'culture', 'textile', 'lifestyle']
            WHEN 'enterprise' THEN ARRAY['all', 'fashion', 'beauty', 'skincare', 'sustainability', 'fashion-tech', 'catwalks', 'culture', 'textile', 'lifestyle']
            ELSE ARRAY['all', 'fashion']
        END,
        monthly_credits = CASE p_plan
            WHEN 'free' THEN 15
            WHEN 'standard' THEN 1500
            WHEN 'pro' THEN 9000
            WHEN 'enterprise' THEN 25000
            ELSE 15
        END
    WHERE user_id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;
