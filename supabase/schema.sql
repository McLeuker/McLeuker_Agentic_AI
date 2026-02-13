-- ============================================================================
-- McLeuker AI - Supabase Schema
-- Production-ready database schema for Agentic AI system
-- Last Updated: 2026-02-13
-- ============================================================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ============================================================================
-- USER MANAGEMENT & AUTHENTICATION
-- ============================================================================

-- Profiles table (extends Supabase auth.users)
CREATE TABLE IF NOT EXISTS public.profiles (
    id UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
    email TEXT NOT NULL,
    full_name TEXT,
    avatar_url TEXT,
    subscription_tier TEXT DEFAULT 'free' CHECK (subscription_tier IN ('free', 'pro', 'enterprise')),
    credits INTEGER DEFAULT 100,
    monthly_credits_used INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on profiles
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;

-- Profile policies
CREATE POLICY "Users can view own profile" ON public.profiles
    FOR SELECT USING (auth.uid() = id);

CREATE POLICY "Users can update own profile" ON public.profiles
    FOR UPDATE USING (auth.uid() = id);

-- Trigger to create profile on user signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.profiles (id, email, full_name)
    VALUES (NEW.id, NEW.email, NEW.raw_user_meta_data->>'full_name');
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
    AFTER INSERT ON auth.users
    FOR EACH ROW EXECUTE FUNCTION public.handle_new_user();

-- ============================================================================
-- EXECUTIONS - Track AI task executions
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.executions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Execution details
    request TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending' 
        CHECK (status IN ('pending', 'running', 'completed', 'failed', 'cancelled')),
    
    -- Agent information
    agent_type TEXT NOT NULL 
        CHECK (agent_type IN (
            'computer_use', 'website_builder', 'document_agent', 
            'slides_agent', 'excel_agent', 'deep_research', 'agent_swarm'
        )),
    
    -- Execution context
    context JSONB DEFAULT '{}',
    
    -- Results
    result JSONB,
    error_message TEXT,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    execution_time_ms INTEGER,
    
    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on executions
ALTER TABLE public.executions ENABLE ROW LEVEL SECURITY;

-- Execution policies
CREATE POLICY "Users can view own executions" ON public.executions
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own executions" ON public.executions
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own executions" ON public.executions
    FOR UPDATE USING (auth.uid() = user_id);

-- Indexes for executions
CREATE INDEX IF NOT EXISTS idx_executions_user_id ON public.executions(user_id);
CREATE INDEX IF NOT EXISTS idx_executions_status ON public.executions(status);
CREATE INDEX IF NOT EXISTS idx_executions_agent_type ON public.executions(agent_type);
CREATE INDEX IF NOT EXISTS idx_executions_created_at ON public.executions(created_at DESC);

-- ============================================================================
-- EXECUTION STEPS - Track individual steps within an execution
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.execution_steps (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    execution_id UUID NOT NULL REFERENCES public.executions(id) ON DELETE CASCADE,
    
    -- Step details
    step_number INTEGER NOT NULL,
    tool TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending'
        CHECK (status IN ('pending', 'running', 'completed', 'failed', 'skipped')),
    
    -- Content
    title TEXT,
    instruction TEXT,
    result_summary TEXT,
    
    -- Screenshot (base64 encoded, optional)
    screenshot TEXT,
    
    -- Timing
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    execution_time_ms INTEGER,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on execution_steps
ALTER TABLE public.execution_steps ENABLE ROW LEVEL SECURITY;

-- Execution steps policies
CREATE POLICY "Users can view own execution steps" ON public.execution_steps
    FOR SELECT USING (
        EXISTS (
            SELECT 1 FROM public.executions e 
            WHERE e.id = execution_steps.execution_id 
            AND e.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can create own execution steps" ON public.execution_steps
    FOR INSERT WITH CHECK (
        EXISTS (
            SELECT 1 FROM public.executions e 
            WHERE e.id = execution_steps.execution_id 
            AND e.user_id = auth.uid()
        )
    );

CREATE POLICY "Users can update own execution steps" ON public.execution_steps
    FOR UPDATE USING (
        EXISTS (
            SELECT 1 FROM public.executions e 
            WHERE e.id = execution_steps.execution_id 
            AND e.user_id = auth.uid()
        )
    );

-- Indexes for execution_steps
CREATE INDEX IF NOT EXISTS idx_execution_steps_execution_id ON public.execution_steps(execution_id);
CREATE INDEX IF NOT EXISTS idx_execution_steps_status ON public.execution_steps(status);

-- ============================================================================
-- ARTIFACTS - Store generated files (documents, presentations, spreadsheets)
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.artifacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    execution_id UUID REFERENCES public.executions(id) ON DELETE SET NULL,
    
    -- Artifact details
    name TEXT NOT NULL,
    file_type TEXT NOT NULL 
        CHECK (file_type IN ('docx', 'pdf', 'pptx', 'xlsx', 'csv', 'html', 'zip')),
    
    -- Storage
    storage_path TEXT NOT NULL,  -- Path in S3/Supabase Storage
    file_size_bytes INTEGER,
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on artifacts
ALTER TABLE public.artifacts ENABLE ROW LEVEL SECURITY;

-- Artifact policies
CREATE POLICY "Users can view own artifacts" ON public.artifacts
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own artifacts" ON public.artifacts
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own artifacts" ON public.artifacts
    FOR DELETE USING (auth.uid() = user_id);

-- Indexes for artifacts
CREATE INDEX IF NOT EXISTS idx_artifacts_user_id ON public.artifacts(user_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_execution_id ON public.artifacts(execution_id);
CREATE INDEX IF NOT EXISTS idx_artifacts_file_type ON public.artifacts(file_type);

-- ============================================================================
-- WEBSITES - Track generated website projects
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.websites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    execution_id UUID REFERENCES public.executions(id) ON DELETE SET NULL,
    
    -- Website details
    name TEXT NOT NULL,
    description TEXT,
    
    -- Build status
    build_status TEXT DEFAULT 'pending' 
        CHECK (build_status IN ('pending', 'building', 'success', 'failed')),
    
    -- Deployment
    deploy_platform TEXT CHECK (deploy_platform IN ('vercel', 'netlify', 'none')),
    deploy_url TEXT,
    preview_url TEXT,
    
    -- Storage
    storage_path TEXT,  -- Path to built files
    
    -- Metadata
    requirements JSONB DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    deployed_at TIMESTAMP WITH TIME ZONE
);

-- Enable RLS on websites
ALTER TABLE public.websites ENABLE ROW LEVEL SECURITY;

-- Website policies
CREATE POLICY "Users can view own websites" ON public.websites
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own websites" ON public.websites
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own websites" ON public.websites
    FOR UPDATE USING (auth.uid() = user_id);

CREATE POLICY "Users can delete own websites" ON public.websites
    FOR DELETE USING (auth.uid() = user_id);

-- Indexes for websites
CREATE INDEX IF NOT EXISTS idx_websites_user_id ON public.websites(user_id);
CREATE INDEX IF NOT EXISTS idx_websites_build_status ON public.websites(build_status);

-- ============================================================================
-- RESEARCH REPORTS - Store deep research results
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.research_reports (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    execution_id UUID REFERENCES public.executions(id) ON DELETE SET NULL,
    
    -- Report details
    query TEXT NOT NULL,
    executive_summary TEXT,
    
    -- Content
    findings JSONB DEFAULT '[]',
    sources JSONB DEFAULT '[]',
    recommendations JSONB DEFAULT '[]',
    gaps JSONB DEFAULT '[]',
    
    -- Metadata
    depth TEXT CHECK (depth IN ('quick', 'standard', 'comprehensive')),
    focus_areas JSONB DEFAULT '[]',
    num_sources INTEGER DEFAULT 0,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on research_reports
ALTER TABLE public.research_reports ENABLE ROW LEVEL SECURITY;

-- Research report policies
CREATE POLICY "Users can view own research reports" ON public.research_reports
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own research reports" ON public.research_reports
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can delete own research reports" ON public.research_reports
    FOR DELETE USING (auth.uid() = user_id);

-- Indexes for research_reports
CREATE INDEX IF NOT EXISTS idx_research_reports_user_id ON public.research_reports(user_id);
CREATE INDEX IF NOT EXISTS idx_research_reports_query ON public.research_reports USING gin(to_tsvector('english', query));

-- ============================================================================
-- CREDIT TRANSACTIONS - Track credit usage
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.credit_transactions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Transaction details
    amount INTEGER NOT NULL,  -- Positive for credits added, negative for used
    transaction_type TEXT NOT NULL 
        CHECK (transaction_type IN ('purchase', 'usage', 'bonus', 'refund')),
    
    -- Reference
    execution_id UUID REFERENCES public.executions(id) ON DELETE SET NULL,
    stripe_payment_intent_id TEXT,
    
    -- Description
    description TEXT,
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Enable RLS on credit_transactions
ALTER TABLE public.credit_transactions ENABLE ROW LEVEL SECURITY;

-- Credit transaction policies
CREATE POLICY "Users can view own credit transactions" ON public.credit_transactions
    FOR SELECT USING (auth.uid() = user_id);

-- Indexes for credit_transactions
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user_id ON public.credit_transactions(user_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_created_at ON public.credit_transactions(created_at DESC);

-- ============================================================================
-- AGENT CONFIGURATION - Store agent settings
-- ============================================================================

CREATE TABLE IF NOT EXISTS public.agent_configs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    
    -- Agent type
    agent_type TEXT NOT NULL 
        CHECK (agent_type IN (
            'computer_use', 'website_builder', 'document_agent', 
            'slides_agent', 'excel_agent', 'deep_research', 'agent_swarm'
        )),
    
    -- Configuration
    config JSONB NOT NULL DEFAULT '{}',
    
    -- Timestamps
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    
    -- Unique constraint
    UNIQUE(user_id, agent_type)
);

-- Enable RLS on agent_configs
ALTER TABLE public.agent_configs ENABLE ROW LEVEL SECURITY;

-- Agent config policies
CREATE POLICY "Users can view own agent configs" ON public.agent_configs
    FOR SELECT USING (auth.uid() = user_id);

CREATE POLICY "Users can create own agent configs" ON public.agent_configs
    FOR INSERT WITH CHECK (auth.uid() = user_id);

CREATE POLICY "Users can update own agent configs" ON public.agent_configs
    FOR UPDATE USING (auth.uid() = user_id);

-- ============================================================================
-- FUNCTIONS & TRIGGERS
-- ============================================================================

-- Update timestamps trigger
CREATE OR REPLACE FUNCTION public.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update trigger to all tables with updated_at
CREATE TRIGGER update_profiles_updated_at
    BEFORE UPDATE ON public.profiles
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_executions_updated_at
    BEFORE UPDATE ON public.executions
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_artifacts_updated_at
    BEFORE UPDATE ON public.artifacts
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_websites_updated_at
    BEFORE UPDATE ON public.websites
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_research_reports_updated_at
    BEFORE UPDATE ON public.research_reports
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

CREATE TRIGGER update_agent_configs_updated_at
    BEFORE UPDATE ON public.agent_configs
    FOR EACH ROW EXECUTE FUNCTION public.update_updated_at_column();

-- Function to update user credits
CREATE OR REPLACE FUNCTION public.update_user_credits(
    p_user_id UUID,
    p_amount INTEGER,
    p_transaction_type TEXT,
    p_description TEXT DEFAULT NULL,
    p_execution_id UUID DEFAULT NULL
)
RETURNS VOID AS $$
BEGIN
    -- Insert transaction record
    INSERT INTO public.credit_transactions (
        user_id, amount, transaction_type, description, execution_id
    ) VALUES (
        p_user_id, p_amount, p_transaction_type, p_description, p_execution_id
    );
    
    -- Update user credits
    UPDATE public.profiles
    SET 
        credits = credits + p_amount,
        monthly_credits_used = CASE 
            WHEN p_amount < 0 THEN monthly_credits_used + ABS(p_amount)
            ELSE monthly_credits_used
        END,
        updated_at = NOW()
    WHERE id = p_user_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- STORAGE BUCKETS
-- ============================================================================

-- Create storage bucket for artifacts
INSERT INTO storage.buckets (id, name, public)
VALUES ('artifacts', 'artifacts', false)
ON CONFLICT (id) DO NOTHING;

-- Create storage bucket for website builds
INSERT INTO storage.buckets (id, name, public)
VALUES ('websites', 'websites', true)
ON CONFLICT (id) DO NOTHING;

-- Storage policies for artifacts
CREATE POLICY "Users can upload own artifacts" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'artifacts' 
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can view own artifacts" ON storage.objects
    FOR SELECT USING (
        bucket_id = 'artifacts' 
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

CREATE POLICY "Users can delete own artifacts" ON storage.objects
    FOR DELETE USING (
        bucket_id = 'artifacts' 
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

-- Storage policies for websites (public read)
CREATE POLICY "Anyone can view websites" ON storage.objects
    FOR SELECT USING (bucket_id = 'websites');

CREATE POLICY "Users can upload own websites" ON storage.objects
    FOR INSERT WITH CHECK (
        bucket_id = 'websites' 
        AND auth.uid()::text = (storage.foldername(name))[1]
    );

-- ============================================================================
-- SEED DATA (Optional)
-- ============================================================================

-- Add default agent configurations
INSERT INTO public.agent_configs (agent_type, config) VALUES
    ('computer_use', '{"viewport_width": 1280, "viewport_height": 720, "headless": true}'::jsonb),
    ('website_builder', '{"framework": "react", "styling": "tailwind"}'::jsonb),
    ('document_agent', '{"default_template": "business_proposal"}'::jsonb),
    ('slides_agent', '{"default_template": "business_presentation"}'::jsonb),
    ('excel_agent', '{"default_type": "budget"}'::jsonb),
    ('deep_research', '{"max_sources": 20, "default_depth": "comprehensive"}'::jsonb)
ON CONFLICT DO NOTHING;

-- ============================================================================
-- END OF SCHEMA
-- ============================================================================
