-- ══════════════════════════════════════════════════════════════════════════════
-- SkillPath AI — Production Database Schema for Supabase PostgreSQL
-- ══════════════════════════════════════════════════════════════════════════════
-- Description: Creates the 4 required application tables (users, user_states,
--              quiz_history, learning_activities), primary keys, foreign keys,
--              indexes, unique constraints, and Row Level Security (RLS) policies.
-- Safe to execute on a fresh Supabase database (fully idempotent with IF NOT EXISTS).
-- ══════════════════════════════════════════════════════════════════════════════

-- 1. USERS TABLE
CREATE TABLE IF NOT EXISTS public.users (
    id SERIAL PRIMARY KEY,
    github_id VARCHAR UNIQUE,
    supabase_id VARCHAR UNIQUE,
    username VARCHAR UNIQUE NOT NULL,
    email VARCHAR,
    password_hash VARCHAR
);

CREATE INDEX IF NOT EXISTS ix_users_id ON public.users (id);
CREATE INDEX IF NOT EXISTS ix_users_username ON public.users (username);
CREATE INDEX IF NOT EXISTS ix_users_github_id ON public.users (github_id);
CREATE INDEX IF NOT EXISTS ix_users_supabase_id ON public.users (supabase_id);

-- 2. USER STATES TABLE
CREATE TABLE IF NOT EXISTS public.user_states (
    id SERIAL PRIMARY KEY,
    user_id INTEGER UNIQUE NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    target_role VARCHAR,
    extracted_skills JSONB,
    current_topic VARCHAR,
    current_difficulty VARCHAR,
    current_module VARCHAR,
    module_progress JSONB,
    fatigue DOUBLE PRECISION DEFAULT 0.0,

    -- Resume & Skill persistence
    resume_filename VARCHAR,
    resume_uploaded_at VARCHAR,
    resume_file_path VARCHAR,
    resume_text TEXT,
    extracted_skills_categorized JSONB,

    -- Video completion & Adaptive tracking
    video_progress JSONB DEFAULT '{}'::jsonb,
    topic_ability JSONB DEFAULT '{}'::jsonb,
    recommended_topics JSONB,
    last_video_id VARCHAR,
    last_video_title VARCHAR,
    last_video_position_seconds DOUBLE PRECISION DEFAULT 0.0,
    last_accessed_at VARCHAR,

    -- DSA Personalization & Research Tracking
    dsa_language VARCHAR DEFAULT 'Python',
    initial_performance_category VARCHAR,
    current_ability DOUBLE PRECISION DEFAULT 0.5,
    created_at VARCHAR,
    updated_at VARCHAR,

    -- Dashboard tracking metrics
    total_learning_hours DOUBLE PRECISION DEFAULT 0.0,
    current_streak INTEGER DEFAULT 0,
    last_activity_date VARCHAR,
    completed_projects INTEGER DEFAULT 0,
    badges JSONB
);

CREATE INDEX IF NOT EXISTS ix_user_states_id ON public.user_states (id);
CREATE INDEX IF NOT EXISTS ix_user_states_user_id ON public.user_states (user_id);

-- 3. QUIZ HISTORY TABLE
CREATE TABLE IF NOT EXISTS public.quiz_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    topic VARCHAR,
    module_key VARCHAR,
    difficulty VARCHAR,
    quiz_score DOUBLE PRECISION,
    code_score DOUBLE PRECISION DEFAULT 0.0,
    reward DOUBLE PRECISION DEFAULT 0.0,

    -- Detailed Quiz Result Fields
    quiz_id VARCHAR,
    questions JSONB,
    user_answers JSONB,
    correct_answers JSONB,
    score INTEGER DEFAULT 0,
    total_questions INTEGER DEFAULT 0,
    percentage DOUBLE PRECISION DEFAULT 0.0,
    unanswered INTEGER DEFAULT 0,
    completed_at VARCHAR
);

CREATE INDEX IF NOT EXISTS ix_quiz_history_id ON public.quiz_history (id);
CREATE INDEX IF NOT EXISTS ix_quiz_history_user_id ON public.quiz_history (user_id);
CREATE INDEX IF NOT EXISTS ix_quiz_history_topic ON public.quiz_history (topic);
CREATE INDEX IF NOT EXISTS ix_quiz_history_quiz_id ON public.quiz_history (quiz_id);

-- 4. LEARNING ACTIVITIES TABLE
CREATE TABLE IF NOT EXISTS public.learning_activities (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES public.users(id) ON DELETE CASCADE,
    activity_type VARCHAR NOT NULL,
    title VARCHAR NOT NULL,
    description TEXT,
    topic VARCHAR,
    created_at VARCHAR NOT NULL
);

CREATE INDEX IF NOT EXISTS ix_learning_activities_id ON public.learning_activities (id);
CREATE INDEX IF NOT EXISTS ix_learning_activities_user_id ON public.learning_activities (user_id);
CREATE INDEX IF NOT EXISTS ix_learning_activities_created_at ON public.learning_activities (created_at);

-- 5. ROW LEVEL SECURITY (RLS) POLICIES
-- Protects Supabase public schema from unauthorized PostgREST API access via public anon keys.
-- The FastAPI backend (connecting directly as postgres via DATABASE_URL) automatically bypasses RLS.
ALTER TABLE public.users ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.user_states ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quiz_history ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.learning_activities ENABLE ROW LEVEL SECURITY;

-- Allow authenticated users to view/update their own profile
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'users' AND policyname = 'users_self_access'
    ) THEN
        CREATE POLICY users_self_access ON public.users
            FOR ALL
            TO authenticated
            USING (supabase_id = auth.uid()::text)
            WITH CHECK (supabase_id = auth.uid()::text);
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'user_states' AND policyname = 'user_states_self_access'
    ) THEN
        CREATE POLICY user_states_self_access ON public.user_states
            FOR ALL
            TO authenticated
            USING (user_id IN (SELECT id FROM public.users WHERE supabase_id = auth.uid()::text))
            WITH CHECK (user_id IN (SELECT id FROM public.users WHERE supabase_id = auth.uid()::text));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'quiz_history' AND policyname = 'quiz_history_self_access'
    ) THEN
        CREATE POLICY quiz_history_self_access ON public.quiz_history
            FOR ALL
            TO authenticated
            USING (user_id IN (SELECT id FROM public.users WHERE supabase_id = auth.uid()::text))
            WITH CHECK (user_id IN (SELECT id FROM public.users WHERE supabase_id = auth.uid()::text));
    END IF;

    IF NOT EXISTS (
        SELECT 1 FROM pg_policies WHERE tablename = 'learning_activities' AND policyname = 'learning_activities_self_access'
    ) THEN
        CREATE POLICY learning_activities_self_access ON public.learning_activities
            FOR ALL
            TO authenticated
            USING (user_id IN (SELECT id FROM public.users WHERE supabase_id = auth.uid()::text))
            WITH CHECK (user_id IN (SELECT id FROM public.users WHERE supabase_id = auth.uid()::text));
    END IF;
END $$;

-- 6. SUPABASE STORAGE BUCKET FOR RESUMES
INSERT INTO storage.buckets (id, name, public)
VALUES ('resumes', 'resumes', false)
ON CONFLICT (id) DO NOTHING;
