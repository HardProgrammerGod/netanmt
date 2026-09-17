-- Test-only schema from supplied table export. ARRAY resolved to uuid[] from existing migrations.
-- WARNING: This schema is for context only and is not meant to be run.
-- Table order and constraints may not be valid for execution.

CREATE TABLE public.users (
  id bigint NOT NULL,
  username text,
  first_name text,
  level integer DEFAULT 1,
  xp integer DEFAULT 0,
  energy integer DEFAULT 5,
  max_energy integer DEFAULT 5,
  is_premium boolean DEFAULT false,
  mascot_skin text DEFAULT 'default'::text,
  referrer_id bigint,
  created_at timestamp with time zone DEFAULT now(),
  is_active boolean DEFAULT true,
  streak integer NOT NULL DEFAULT 0,
  total_tasks_solved integer NOT NULL DEFAULT 0,
  referrals_count integer NOT NULL DEFAULT 0,
  referral_rewarded boolean NOT NULL DEFAULT false,
  premium_until timestamp with time zone,
  last_active_at timestamp with time zone DEFAULT now(),
  last_streak_date date,
  last_reminder_at timestamp with time zone,
  daily_quiz_count integer NOT NULL DEFAULT 0,
  daily_quiz_date date DEFAULT CURRENT_DATE,
  daily_tests_left integer DEFAULT 3,
  last_test_date date,
  total_questions_answered integer DEFAULT 0,
  total_correct_answers integer DEFAULT 0,
  express_test_completed boolean DEFAULT false,
  express_test_score integer,
  updated_at timestamp with time zone DEFAULT now(),
  onboarding_completed boolean NOT NULL DEFAULT false,
  diagnostic_correct integer NOT NULL DEFAULT 0,
  diagnostic_total integer NOT NULL DEFAULT 0,
  diagnostic_score_min integer,
  diagnostic_score_max integer,
  diagnostic_weak_topics jsonb NOT NULL DEFAULT '[]'::jsonb,
  diagnostic_completed_at timestamp with time zone,
  acquisition_source text,
  is_test_account boolean NOT NULL DEFAULT false,
  reminder_enabled boolean NOT NULL DEFAULT false,
  reminder_time time without time zone,
  reminder_timezone text NOT NULL DEFAULT 'Europe/Kyiv'::text,
  public_alias text,
  leaderboard_opt_in boolean NOT NULL DEFAULT false,
  first_lesson_completed_at timestamp with time zone,
  CONSTRAINT users_pkey PRIMARY KEY (id),
  CONSTRAINT users_referrer_id_fkey FOREIGN KEY (referrer_id) REFERENCES public.users(id)
);
CREATE TABLE public.questions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  topic text NOT NULL,
  difficulty integer NOT NULL,
  question_text text NOT NULL,
  options jsonb NOT NULL,
  correct_option integer NOT NULL,
  explanation text,
  created_at timestamp with time zone DEFAULT now(),
  category text,
  sub_category text,
  section text DEFAULT 'NMT'::text,
  is_active boolean DEFAULT true,
  usage_count integer DEFAULT 0,
  is_diagnostic boolean NOT NULL DEFAULT false,
  question_code text,
  nmt_task_type text,
  content_pack text,
  quality_status text NOT NULL DEFAULT 'approved'::text,
  is_intro boolean NOT NULL DEFAULT false,
  intro_priority integer,
  CONSTRAINT questions_pkey PRIMARY KEY (id)
);
CREATE TABLE public.user_answers (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  user_id bigint,
  question_id uuid,
  is_correct boolean NOT NULL,
  answered_at timestamp with time zone DEFAULT now(),
  selected_answer text,
  answer_index integer,
  answer integer,
  CONSTRAINT user_answers_pkey PRIMARY KEY (id),
  CONSTRAINT user_answers_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT user_answers_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id)
);
CREATE TABLE public.topics (
  id text NOT NULL,
  title text NOT NULL,
  order_index integer NOT NULL,
  min_level integer DEFAULT 1,
  icon text DEFAULT '📚'::text,
  CONSTRAINT topics_pkey PRIMARY KEY (id)
);
CREATE TABLE public.user_topics (
  user_id bigint NOT NULL,
  topic_id text NOT NULL,
  is_completed boolean DEFAULT false,
  score integer DEFAULT 0,
  CONSTRAINT user_topics_pkey PRIMARY KEY (user_id, topic_id),
  CONSTRAINT user_topics_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT user_topics_topic_id_fkey FOREIGN KEY (topic_id) REFERENCES public.topics(id)
);
CREATE TABLE public.orders (
  order_id text NOT NULL,
  user_id bigint NOT NULL,
  amount numeric NOT NULL,
  status text DEFAULT 'pending'::text,
  created_at timestamp with time zone DEFAULT now(),
  currency text DEFAULT 'XTR'::text,
  premium_days integer,
  payment_provider text DEFAULT 'telegram_stars'::text,
  telegram_payment_charge_id text,
  telegram_provider_payment_charge_id text,
  payload text,
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT orders_pkey PRIMARY KEY (order_id),
  CONSTRAINT orders_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.referral_rewards (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  referrer_id bigint NOT NULL,
  referred_user_id bigint NOT NULL UNIQUE,
  reward_days integer NOT NULL DEFAULT 3,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT referral_rewards_pkey PRIMARY KEY (id),
  CONSTRAINT referral_rewards_referrer_fkey FOREIGN KEY (referrer_id) REFERENCES public.users(id),
  CONSTRAINT referral_rewards_referred_user_fkey FOREIGN KEY (referred_user_id) REFERENCES public.users(id)
);
CREATE TABLE public.user_topic_progress (
  user_id bigint NOT NULL,
  category text NOT NULL,
  sub_category text NOT NULL,
  attempts integer NOT NULL DEFAULT 0,
  correct integer NOT NULL DEFAULT 0,
  mastery_score numeric NOT NULL DEFAULT 0,
  current_difficulty integer NOT NULL DEFAULT 1,
  last_answer_correct boolean,
  last_seen_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  CONSTRAINT user_topic_progress_pkey PRIMARY KEY (user_id, category, sub_category)
);
CREATE TABLE public.events (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id bigint,
  event_name text NOT NULL,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  event_key text,
  CONSTRAINT events_pkey PRIMARY KEY (id)
);
CREATE TABLE public.simulation_results (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id bigint NOT NULL,
  correct integer NOT NULL CHECK (correct >= 0),
  total integer NOT NULL DEFAULT 32 CHECK (total > 0),
  nmt_score integer CHECK (nmt_score IS NULL OR nmt_score >= 100 AND nmt_score <= 200),
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT simulation_results_pkey PRIMARY KEY (id)
);
CREATE TABLE public.manual_payment_requests (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id bigint NOT NULL,
  tariff text NOT NULL,
  days integer NOT NULL,
  discount_percent integer NOT NULL DEFAULT 27,
  status text NOT NULL DEFAULT 'pending'::text,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  completed_at timestamp with time zone,
  CONSTRAINT manual_payment_requests_pkey PRIMARY KEY (id)
);
CREATE TABLE public.launch_waitlist (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  telegram_id bigint,
  username text,
  first_name text,
  source text DEFAULT 'preregistration'::text,
  status text NOT NULL DEFAULT 'waiting'::text,
  ping_sent_at timestamp with time zone,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  notes text,
  CONSTRAINT launch_waitlist_pkey PRIMARY KEY (id)
);
CREATE TABLE public.learning_sessions (
  id uuid NOT NULL DEFAULT gen_random_uuid(),
  user_id bigint NOT NULL,
  session_key text NOT NULL,
  session_type text NOT NULL CHECK (session_type = ANY (ARRAY['intro'::text, 'daily'::text, 'practice'::text, 'diagnostic'::text])),
  learning_date date NOT NULL,
  question_ids uuid[] NOT NULL,
  current_index integer NOT NULL DEFAULT 0 CHECK (current_index >= 0),
  answered_count integer NOT NULL DEFAULT 0 CHECK (answered_count >= 0),
  correct_count integer NOT NULL DEFAULT 0 CHECK (correct_count >= 0),
  status text NOT NULL DEFAULT 'active'::text CHECK (status = ANY (ARRAY['active'::text, 'completed'::text, 'abandoned'::text])),
  started_at timestamp with time zone NOT NULL DEFAULT now(),
  completed_at timestamp with time zone,
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT learning_sessions_pkey PRIMARY KEY (id),
  CONSTRAINT learning_sessions_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.learning_session_answers (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  session_id uuid NOT NULL,
  user_id bigint NOT NULL,
  question_id uuid NOT NULL,
  question_index integer NOT NULL CHECK (question_index >= 0),
  selected_index integer NOT NULL CHECK (selected_index >= 0 AND selected_index <= 3),
  is_correct boolean NOT NULL,
  answered_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT learning_session_answers_pkey PRIMARY KEY (id),
  CONSTRAINT learning_session_answers_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.learning_sessions(id),
  CONSTRAINT learning_session_answers_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT learning_session_answers_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id)
);
CREATE TABLE public.learning_days (
  user_id bigint NOT NULL,
  learning_date date NOT NULL,
  answered_count integer NOT NULL DEFAULT 0,
  completed_sessions integer NOT NULL DEFAULT 0,
  leaderboard_points integer NOT NULL DEFAULT 0 CHECK (leaderboard_points >= 0 AND leaderboard_points <= 1),
  updated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT learning_days_pkey PRIMARY KEY (user_id, learning_date),
  CONSTRAINT learning_days_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id)
);
CREATE TABLE public.referral_activations (
  referred_user_id bigint NOT NULL,
  referrer_id bigint NOT NULL,
  activated_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT referral_activations_pkey PRIMARY KEY (referred_user_id),
  CONSTRAINT referral_activations_referred_user_id_fkey FOREIGN KEY (referred_user_id) REFERENCES public.users(id),
  CONSTRAINT referral_activations_referrer_id_fkey FOREIGN KEY (referrer_id) REFERENCES public.users(id)
);
CREATE TABLE public.operational_metrics (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  metric_name text NOT NULL,
  user_id bigint,
  duration_ms integer,
  metadata jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT operational_metrics_pkey PRIMARY KEY (id)
);
CREATE TABLE public.error_reports (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  user_id bigint,
  error_type text NOT NULL,
  context text,
  details jsonb NOT NULL DEFAULT '{}'::jsonb,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT error_reports_pkey PRIMARY KEY (id)
);
CREATE TABLE public.learning_xp_events (
  id bigint GENERATED ALWAYS AS IDENTITY NOT NULL,
  user_id bigint NOT NULL,
  learning_date date NOT NULL,
  event_type text NOT NULL CHECK (event_type = ANY (ARRAY['answer'::text, 'daily_bonus'::text, 'streak_bonus'::text])),
  points integer NOT NULL CHECK (points >= 1 AND points <= 10),
  question_id uuid,
  session_id uuid,
  event_key text NOT NULL UNIQUE,
  created_at timestamp with time zone NOT NULL DEFAULT now(),
  CONSTRAINT learning_xp_events_pkey PRIMARY KEY (id),
  CONSTRAINT learning_xp_events_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(id),
  CONSTRAINT learning_xp_events_question_id_fkey FOREIGN KEY (question_id) REFERENCES public.questions(id),
  CONSTRAINT learning_xp_events_session_id_fkey FOREIGN KEY (session_id) REFERENCES public.learning_sessions(id)
);