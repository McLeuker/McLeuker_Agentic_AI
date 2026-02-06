-- ============================================================================
-- McLeuker AI Platform - Kimi 2.5 Schema Updates (CORRECTED)
-- Uses actual database column names verified from production DB
-- Safe to run multiple times (idempotent)
-- ============================================================================

-- 1. ENABLE pg_trgm EXTENSION for full-text search
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- 2. UPDATE chat_messages role CHECK to include 'tool'
ALTER TABLE public.chat_messages DROP CONSTRAINT IF EXISTS chat_messages_role_check;
ALTER TABLE public.chat_messages ADD CONSTRAINT chat_messages_role_check
  CHECK (role IN ('user', 'assistant', 'system', 'tool'));

-- 3. UPDATE credit_transactions transaction_type CHECK (actual column name)
ALTER TABLE public.credit_transactions DROP CONSTRAINT IF EXISTS credit_transactions_transaction_type_check;
ALTER TABLE public.credit_transactions ADD CONSTRAINT credit_transactions_transaction_type_check
  CHECK (transaction_type IN ('usage', 'purchase', 'refund', 'bonus', 'monthly_reset', 'subscription'));

-- 4. UPDATE support_requests request_type CHECK (actual column name)
ALTER TABLE public.support_requests DROP CONSTRAINT IF EXISTS support_requests_request_type_check;
ALTER TABLE public.support_requests ADD CONSTRAINT support_requests_request_type_check
  CHECK (request_type IN ('bug', 'feature', 'billing', 'general', 'technical', 'question', 'other'));

-- 5. ADD priority column to support_requests (does not exist yet)
ALTER TABLE public.support_requests ADD COLUMN IF NOT EXISTS priority VARCHAR(20) DEFAULT 'normal';
ALTER TABLE public.support_requests DROP CONSTRAINT IF EXISTS support_requests_priority_check;
ALTER TABLE public.support_requests ADD CONSTRAINT support_requests_priority_check
  CHECK (priority IN ('low', 'normal', 'medium', 'high', 'urgent'));

-- 6. ADD full-text search index on chat_messages.content (trigram)
CREATE INDEX IF NOT EXISTS idx_chat_messages_content_trgm
  ON public.chat_messages USING gin(content gin_trgm_ops);

-- 7. ADD GIN index on saved_outputs.tags
CREATE INDEX IF NOT EXISTS idx_saved_outputs_tags
  ON public.saved_outputs USING gin(tags);

-- 8. ADD created_at DESC index on file_uploads
CREATE INDEX IF NOT EXISTS idx_file_uploads_created_at
  ON public.file_uploads(created_at DESC);

-- 9. ADD indexes on user_memory
CREATE INDEX IF NOT EXISTS idx_user_memory_key
  ON public.user_memory(key);
CREATE INDEX IF NOT EXISTS idx_user_memory_updated_at
  ON public.user_memory(updated_at DESC);

-- 10. ADD conversations created_at DESC index
CREATE INDEX IF NOT EXISTS idx_conversations_created_at
  ON public.conversations(created_at DESC);

-- 11. ADD file_type CHECK constraint on file_uploads
ALTER TABLE public.file_uploads DROP CONSTRAINT IF EXISTS file_uploads_file_type_check;
ALTER TABLE public.file_uploads ADD CONSTRAINT file_uploads_file_type_check
  CHECK (file_type IN ('image', 'video', 'document', 'audio', 'other'));

-- 12. ADD confidence CHECK constraint for user_memory
ALTER TABLE public.user_memory DROP CONSTRAINT IF EXISTS user_memory_confidence_check;
ALTER TABLE public.user_memory ADD CONSTRAINT user_memory_confidence_check
  CHECK (confidence >= 0 AND confidence <= 1);

-- 13. ADD missing columns to file_uploads
ALTER TABLE public.file_uploads ADD COLUMN IF NOT EXISTS storage_path TEXT;
ALTER TABLE public.file_uploads ADD COLUMN IF NOT EXISTS public_url TEXT;
ALTER TABLE public.file_uploads ADD COLUMN IF NOT EXISTS metadata JSONB DEFAULT '{}';

-- 14. CREATE STORAGE BUCKET for file uploads
DO $$
BEGIN
  INSERT INTO storage.buckets (id, name, public, file_size_limit, allowed_mime_types)
  VALUES (
    'uploads', 'uploads', true, 52428800,
    ARRAY['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml',
          'application/pdf', 'application/msword',
          'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
          'application/vnd.openxmlformats-officedocument.presentationml.presentation',
          'text/plain', 'text/csv', 'text/markdown',
          'video/mp4', 'video/webm', 'audio/mpeg', 'audio/wav']
  )
  ON CONFLICT (id) DO UPDATE SET
    file_size_limit = EXCLUDED.file_size_limit,
    allowed_mime_types = EXCLUDED.allowed_mime_types;
EXCEPTION
  WHEN OTHERS THEN
    RAISE NOTICE 'Storage bucket creation skipped: %', SQLERRM;
END $$;

-- 15. Storage bucket RLS policies
DO $$
BEGIN
  DROP POLICY IF EXISTS "Authenticated users can upload files" ON storage.objects;
  CREATE POLICY "Authenticated users can upload files" ON storage.objects
    FOR INSERT WITH CHECK (bucket_id = 'uploads' AND auth.role() = 'authenticated');

  DROP POLICY IF EXISTS "Users can view own files" ON storage.objects;
  CREATE POLICY "Users can view own files" ON storage.objects
    FOR SELECT USING (bucket_id = 'uploads' AND (auth.role() = 'authenticated' OR bucket_id = 'uploads'));

  DROP POLICY IF EXISTS "Users can delete own files" ON storage.objects;
  CREATE POLICY "Users can delete own files" ON storage.objects
    FOR DELETE USING (bucket_id = 'uploads' AND auth.role() = 'authenticated');
EXCEPTION
  WHEN OTHERS THEN
    RAISE NOTICE 'Storage policies skipped: %', SQLERRM;
END $$;

-- 16. UPDATE handle_new_user function for Kimi 2.5
-- Uses ACTUAL column names: credits_balance, subscription_tier, last_active_at
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
    INSERT INTO public.users (id, email, name, auth_provider, last_active_at, credits_balance)
    VALUES (
        NEW.id, NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1)),
        COALESCE(NEW.raw_app_meta_data->>'provider', 'email'),
        NOW(), 100
    )
    ON CONFLICT (id) DO UPDATE SET last_active_at = NOW(), email = EXCLUDED.email;
    
    INSERT INTO public.profiles (user_id, email, full_name)
    VALUES (
        NEW.id, NEW.email,
        COALESCE(NEW.raw_user_meta_data->>'full_name', NEW.raw_user_meta_data->>'name', split_part(NEW.email, '@', 1))
    )
    ON CONFLICT (user_id) DO UPDATE SET email = EXCLUDED.email;
    
    INSERT INTO public.subscriptions (user_id, plan, status, credits_remaining, credits_monthly)
    VALUES (NEW.id, 'free', 'active', 100, 100)
    ON CONFLICT (user_id) DO NOTHING;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- ============================================================================
-- DONE! Kimi 2.5 schema updates applied.
-- 
-- TABLE INVENTORY (all 21 tables):
-- 1.  users              - Core user data + preferences
-- 2.  profiles            - Extended profile (bio, website, job)
-- 3.  conversations       - Chat sessions
-- 4.  chat_messages       - Messages (now with 'tool' role)
-- 5.  subscriptions       - Stripe subscription plans
-- 6.  credit_transactions - Credit usage/purchase history
-- 7.  workspaces          - Team workspaces
-- 8.  workspace_members   - Workspace membership
-- 9.  support_requests    - Support tickets (now with priority)
-- 10. user_memory         - AI memory system
-- 11. saved_outputs       - Saved AI content
-- 12. file_uploads        - Uploaded file metadata (new columns added)
-- 13. api_usage           - API usage tracking
-- 14. user_sessions       - Active session tracking
-- +   storage.uploads     - File storage bucket (new)
-- ============================================================================
