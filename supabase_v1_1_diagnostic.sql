-- Neta School / NMT Bot v1.1
-- Safe migration: adds onboarding and diagnostic fields without deleting existing data.

ALTER TABLE public.users
    ADD COLUMN IF NOT EXISTS onboarding_completed boolean NOT NULL DEFAULT false,
    ADD COLUMN IF NOT EXISTS diagnostic_correct integer NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS diagnostic_total integer NOT NULL DEFAULT 0,
    ADD COLUMN IF NOT EXISTS diagnostic_score_min integer,
    ADD COLUMN IF NOT EXISTS diagnostic_score_max integer,
    ADD COLUMN IF NOT EXISTS diagnostic_weak_topics jsonb NOT NULL DEFAULT '[]'::jsonb,
    ADD COLUMN IF NOT EXISTS diagnostic_completed_at timestamptz;

-- Users who already solved tasks can keep using the bot without being forced through onboarding.
-- Brand-new users (including imported pre-registrations with zero activity) keep the diagnostic.
UPDATE public.users
SET onboarding_completed = true
WHERE COALESCE(total_tasks_solved, 0) > 0
  AND onboarding_completed = false;

CREATE INDEX IF NOT EXISTS idx_users_onboarding_completed
    ON public.users (onboarding_completed);
