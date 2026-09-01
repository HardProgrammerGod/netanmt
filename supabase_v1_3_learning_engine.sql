-- ============================================================
-- NETA NMT v1.3 — Adaptive Learning Engine + Analytics
-- Safe to run more than once.
-- ============================================================

-- v1.2 compatibility / safety
ALTER TABLE public.questions
ADD COLUMN IF NOT EXISTS is_diagnostic boolean NOT NULL DEFAULT false;

ALTER TABLE public.user_answers
ADD COLUMN IF NOT EXISTS answer integer;

-- ------------------------------------------------------------
-- Per-user mastery by NMT topic
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.user_topic_progress (
    user_id bigint NOT NULL,
    category text NOT NULL,
    sub_category text NOT NULL,
    attempts integer NOT NULL DEFAULT 0,
    correct integer NOT NULL DEFAULT 0,
    mastery_score numeric(5,2) NOT NULL DEFAULT 0,
    current_difficulty integer NOT NULL DEFAULT 1,
    last_answer_correct boolean,
    last_seen_at timestamptz NOT NULL DEFAULT now(),
    updated_at timestamptz NOT NULL DEFAULT now(),
    PRIMARY KEY (user_id, category, sub_category)
);

CREATE INDEX IF NOT EXISTS idx_user_topic_progress_user
ON public.user_topic_progress(user_id);

CREATE INDEX IF NOT EXISTS idx_user_topic_progress_weak
ON public.user_topic_progress(user_id, mastery_score);

-- ------------------------------------------------------------
-- Product/business funnel analytics
-- ------------------------------------------------------------
CREATE TABLE IF NOT EXISTS public.events (
    id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id bigint,
    event_name text NOT NULL,
    metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
    created_at timestamptz NOT NULL DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_events_user_created
ON public.events(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_events_name_created
ON public.events(event_name, created_at DESC);

-- Useful question-selection indexes
CREATE INDEX IF NOT EXISTS idx_questions_training_pool
ON public.questions(category, sub_category, difficulty)
WHERE is_active = true AND is_diagnostic = false;

CREATE INDEX IF NOT EXISTS idx_questions_diagnostic
ON public.questions(is_diagnostic)
WHERE is_diagnostic = true;
