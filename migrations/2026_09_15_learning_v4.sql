-- Neta NMT English learning flow v4
-- Standalone additive migration from the legacy schema shared by the owner.
-- Existing users, answers, orders, Premium rights and payment history are preserved.

create extension if not exists pgcrypto;

alter table public.users
  add column if not exists acquisition_source text,
  add column if not exists is_test_account boolean not null default false,
  add column if not exists reminder_enabled boolean not null default false,
  add column if not exists reminder_time time,
  add column if not exists reminder_timezone text not null default 'Europe/Kyiv',
  add column if not exists public_alias text,
  add column if not exists leaderboard_opt_in boolean not null default false,
  add column if not exists first_lesson_completed_at timestamptz;

alter table public.questions
  add column if not exists is_intro boolean not null default false,
  add column if not exists intro_priority integer;

alter table public.events
  add column if not exists event_key text;

create unique index if not exists events_event_key_uidx
  on public.events(event_key)
  where event_key is not null;

create index if not exists events_user_name_created_idx
  on public.events(user_id, event_name, created_at desc);

create index if not exists questions_learning_selector_idx
  on public.questions(is_active, quality_status, is_diagnostic, is_intro, usage_count);

create table if not exists public.learning_sessions (
  id uuid primary key default gen_random_uuid(),
  user_id bigint not null references public.users(id) on delete cascade,
  session_key text not null,
  session_type text not null,
  learning_date date not null,
  question_ids uuid[] not null,
  current_index integer not null default 0 check (current_index >= 0),
  answered_count integer not null default 0 check (answered_count >= 0),
  correct_count integer not null default 0 check (correct_count >= 0),
  status text not null default 'active' check (status in ('active','completed','abandoned')),
  started_at timestamptz not null default now(),
  completed_at timestamptz,
  updated_at timestamptz not null default now(),
  unique(user_id, session_key)
);

-- v2 had a check without diagnostic. Keep the allowed set explicit for the current learning flow.
alter table public.learning_sessions
  drop constraint if exists learning_sessions_session_type_check;

alter table public.learning_sessions
  add constraint learning_sessions_session_type_check
  check (session_type in ('intro','daily','practice','diagnostic'));

create index if not exists learning_sessions_user_status_idx
  on public.learning_sessions(user_id, status, updated_at desc);

create table if not exists public.learning_session_answers (
  id bigint generated always as identity primary key,
  session_id uuid not null references public.learning_sessions(id) on delete cascade,
  user_id bigint not null references public.users(id) on delete cascade,
  question_id uuid not null references public.questions(id),
  question_index integer not null check (question_index >= 0),
  selected_index integer not null check (selected_index between 0 and 3),
  is_correct boolean not null,
  answered_at timestamptz not null default now(),
  unique(session_id, question_index)
);

create index if not exists learning_session_answers_user_idx
  on public.learning_session_answers(user_id, answered_at desc);

create table if not exists public.learning_days (
  user_id bigint not null references public.users(id) on delete cascade,
  learning_date date not null,
  answered_count integer not null default 0,
  completed_sessions integer not null default 0,
  leaderboard_points integer not null default 0 check (leaderboard_points between 0 and 1),
  updated_at timestamptz not null default now(),
  primary key(user_id, learning_date)
);

create table if not exists public.referral_activations (
  referred_user_id bigint primary key references public.users(id) on delete cascade,
  referrer_id bigint not null references public.users(id) on delete cascade,
  activated_at timestamptz not null default now(),
  check (referred_user_id <> referrer_id)
);

create index if not exists referral_activations_referrer_idx
  on public.referral_activations(referrer_id, activated_at desc);

create table if not exists public.operational_metrics (
  id bigint generated always as identity primary key,
  metric_name text not null,
  user_id bigint,
  duration_ms integer,
  metadata jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists operational_metrics_name_created_idx
  on public.operational_metrics(metric_name, created_at desc);

create table if not exists public.error_reports (
  id bigint generated always as identity primary key,
  user_id bigint,
  error_type text not null,
  context text,
  details jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now()
);

create index if not exists error_reports_created_idx
  on public.error_reports(created_at desc);

-- Public leaderboard aliases are regenerated by the application as pseudonyms.
-- Clear any v2 aliases that may have been based on Telegram profile names.
update public.users set public_alias = null where public_alias is not null;

-- Normalize referral acquisition labels from older builds so acquisition
-- reporting is grouped by channel instead of one source per referrer ID.
update public.users
set acquisition_source = 'referral'
where acquisition_source like 'ref\_%' escape '\';

-- Existing users who already used the old product must not be forced through
-- the new 3-question intro again.
update public.users
set first_lesson_completed_at = coalesce(first_lesson_completed_at, diagnostic_completed_at, created_at, now())
where first_lesson_completed_at is null
  and (
    coalesce(onboarding_completed, false) = true
    or diagnostic_completed_at is not null
    or coalesce(total_tasks_solved, 0) > 0
    or coalesce(total_questions_answered, 0) > 0
  );

-- Curated first experience. If some codes are absent, the selector below
-- automatically falls back to other approved active questions.
update public.questions set is_intro = false where is_intro = true;

update public.questions
set is_intro = true,
    intro_priority = case question_code
      when 'N17-T2-004' then 10  -- reading / self-testing context
      when 'N17-T5-007' then 20  -- prepositions
      when 'N17-T6-002' then 30  -- phrasal verbs
      when 'N17-T2-010' then 40
      when 'N17-T5-006' then 50
      when 'N17-T6-001' then 60
      else 999
    end
where question_code in (
  'N17-T2-004','N17-T5-007','N17-T6-002',
  'N17-T2-010','N17-T5-006','N17-T6-001'
);


-- One round-trip startup context. This replaces several sequential PostgREST
-- calls on /start and keeps the first-value screen fast.
create or replace function public.ensure_learning_start_context(
  p_user_id bigint,
  p_username text,
  p_first_name text,
  p_referrer_id bigint,
  p_source text,
  p_public_alias text
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_referrer_id bigint;
  v_user public.users%rowtype;
  v_session jsonb;
  v_intro_done boolean := false;
  v_today date := (now() at time zone 'Europe/Kyiv')::date;
begin
  if p_referrer_id is not null
     and p_referrer_id <> p_user_id
     and exists(select 1 from public.users r where r.id = p_referrer_id) then
    v_referrer_id := p_referrer_id;
  end if;

  insert into public.users as u(
    id, username, first_name, referrer_id, is_active, last_active_at,
    acquisition_source, public_alias, updated_at
  ) values (
    p_user_id,
    coalesce(p_username, ''),
    coalesce(nullif(p_first_name, ''), 'Учень'),
    v_referrer_id,
    true,
    now(),
    left(coalesce(nullif(p_source, ''), 'direct'), 120),
    nullif(left(coalesce(p_public_alias, ''), 120), ''),
    now()
  )
  on conflict (id) do update
    set username = excluded.username,
        first_name = excluded.first_name,
        is_active = true,
        last_active_at = now(),
        updated_at = now(),
        acquisition_source = coalesce(nullif(u.acquisition_source, ''), excluded.acquisition_source),
        public_alias = coalesce(nullif(u.public_alias, ''), excluded.public_alias),
        referrer_id = u.referrer_id
  returning * into v_user;

  select to_jsonb(s) into v_session
  from public.learning_sessions s
  where s.user_id = p_user_id
    and s.status = 'active'
  order by s.updated_at desc
  limit 1;

  if v_session is null then
    select to_jsonb(s) into v_session
    from public.learning_sessions s
    where s.user_id = p_user_id
      and s.learning_date = v_today
      and s.status = 'completed'
    order by s.completed_at desc nulls last
    limit 1;
  end if;

  v_intro_done :=
    coalesce(v_user.onboarding_completed, false)
    or v_user.diagnostic_completed_at is not null
    or v_user.first_lesson_completed_at is not null
    or coalesce(v_user.total_tasks_solved, 0) > 0
    or coalesce(v_user.total_questions_answered, 0) > 0
    or exists(
      select 1 from public.events e
      where e.user_id = p_user_id and e.event_name = 'first_lesson_completed'
    );

  return jsonb_build_object(
    'user', to_jsonb(v_user),
    'session', v_session,
    'intro_done', v_intro_done
  );
end;
$$;

-- Select only the handful of question IDs needed for a session inside
-- PostgreSQL. This removes the old application-side LIMIT 1000 ceiling.
create or replace function public.select_learning_questions(
  p_user_id bigint,
  p_session_type text,
  p_length integer
) returns table(question_id uuid, ord integer)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_len integer := greatest(3, least(coalesce(p_length, 4), case when p_session_type = 'diagnostic' then 12 else 5 end));
begin
  if p_session_type = 'intro' then
    return query
    with curated as (
      select q.id,
             row_number() over (order by coalesce(q.intro_priority, 999), q.usage_count asc, q.id) as rn
      from public.questions q
      where q.is_active = true
        and q.quality_status = 'approved'
        and q.is_diagnostic = false
        and q.is_intro = true
      order by coalesce(q.intro_priority, 999), q.usage_count asc, q.id
      limit v_len
    ),
    fallback as (
      select q.id,
             row_number() over (order by q.usage_count asc, random()) as rn
      from public.questions q
      where q.is_active = true
        and q.quality_status = 'approved'
        and q.is_diagnostic = false
        and not exists (select 1 from curated c where c.id = q.id)
      order by q.usage_count asc, random()
      limit greatest(0, v_len - (select count(*)::integer from curated))
    ),
    combined as (
      select c.id, c.rn::integer as sort_key from curated c
      union all
      select f.id, ((select count(*)::integer from curated) + f.rn::integer) as sort_key from fallback f
    )
    select c.id, (row_number() over (order by c.sort_key))::integer
    from combined c
    order by c.sort_key;
    return;
  end if;

  if p_session_type = 'diagnostic' then
    return query
    with pool as (
      select q.id, 0 as source_rank, q.usage_count
      from public.questions q
      where q.is_active = true
        and q.quality_status = 'approved'
        and q.is_diagnostic = true
      union all
      select q.id, 1 as source_rank, q.usage_count
      from public.questions q
      where q.is_active = true
        and q.quality_status = 'approved'
        and q.is_diagnostic = false
        and not exists (
          select 1 from public.questions d
          where d.id = q.id and d.is_diagnostic = true
        )
    ), picked as (
      select p.id
      from pool p
      order by p.source_rank asc, p.usage_count asc, random()
      limit v_len
    )
    select p.id, (row_number() over ())::integer
    from picked p;
    return;
  end if;

  return query
  with history as (
    select a.question_id, a.is_correct, a.answered_at
    from public.learning_session_answers a
    where a.user_id = p_user_id
    union all
    select ua.question_id, ua.is_correct, ua.answered_at
    from public.user_answers ua
    where ua.user_id = p_user_id and ua.question_id is not null
  ),
  latest_per_question as (
    select distinct on (h.question_id)
      h.question_id, h.is_correct, h.answered_at
    from history h
    order by h.question_id, h.answered_at desc
  ),
  latest_wrong as (
    select h.question_id, h.answered_at as last_wrong_at
    from latest_per_question h
    join public.questions q on q.id = h.question_id
    where h.is_correct = false
      and q.is_active = true
      and q.quality_status = 'approved'
      and q.is_diagnostic = false
    order by h.answered_at desc
    limit greatest(1, v_len / 2)
  ),
  unseen as (
    select q.id
    from public.questions q
    where q.is_active = true
      and q.quality_status = 'approved'
      and q.is_diagnostic = false
      and not exists (select 1 from history h where h.question_id = q.id)
      and not exists (select 1 from latest_wrong w where w.question_id = q.id)
    order by q.usage_count asc, random()
    limit greatest(0, v_len - (select count(*)::integer from latest_wrong))
  ),
  base as (
    select w.question_id as id, 0 as grp, w.last_wrong_at as ts
    from latest_wrong w
    union all
    select u.id, 1 as grp, null::timestamptz as ts
    from unseen u
  ),
  fallback as (
    select q.id
    from public.questions q
    where q.is_active = true
      and q.quality_status = 'approved'
      and q.is_diagnostic = false
      and not exists (select 1 from base b where b.id = q.id)
    order by q.usage_count asc, random()
    limit greatest(0, v_len - (select count(*)::integer from base))
  ),
  combined as (
    select b.id, b.grp, b.ts from base b
    union all
    select f.id, 2 as grp, null::timestamptz as ts from fallback f
  ),
  picked as (
    select c.id
    from combined c
    order by c.grp asc, c.ts desc nulls last, random()
    limit v_len
  )
  select p.id, (row_number() over ())::integer
  from picked p;
end;
$$;

-- Idempotent, validated answer persistence. The database is the source of truth
-- for order, correct answer and completion state.
create or replace function public.record_learning_answer(
  p_session_id uuid,
  p_user_id bigint,
  p_question_id uuid,
  p_question_index integer,
  p_selected_index integer,
  p_is_correct boolean
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_inserted boolean := false;
  v_row_count integer := 0;
  v_session public.learning_sessions%rowtype;
  v_completed_now boolean := false;
  v_today date;
  v_correct_option integer;
  v_actual_correct boolean;
  v_category text;
  v_sub_category text;
  v_seed_mastery numeric;
  v_delta numeric;
begin
  select * into v_session
  from public.learning_sessions
  where id = p_session_id and user_id = p_user_id
  for update;

  if not found then
    raise exception 'learning session not found';
  end if;

  if p_question_index < 0 or p_question_index >= cardinality(v_session.question_ids) then
    raise exception 'question index out of range';
  end if;

  if v_session.question_ids[p_question_index + 1] <> p_question_id then
    raise exception 'question does not match session position';
  end if;

  if p_selected_index < 0 or p_selected_index > 3 then
    raise exception 'selected index out of range';
  end if;

  if v_session.status <> 'active' then
    return jsonb_build_object(
      'inserted', false,
      'completed_now', false,
      'session_id', v_session.id,
      'current_index', v_session.current_index,
      'answered_count', v_session.answered_count,
      'correct_count', v_session.correct_count,
      'status', v_session.status,
      'total', cardinality(v_session.question_ids)
    );
  end if;

  if p_question_index <> v_session.current_index then
    if exists (
      select 1 from public.learning_session_answers a
      where a.session_id = p_session_id and a.question_index = p_question_index
    ) then
      return jsonb_build_object(
        'inserted', false,
        'completed_now', false,
        'session_id', v_session.id,
        'current_index', v_session.current_index,
        'answered_count', v_session.answered_count,
        'correct_count', v_session.correct_count,
        'status', v_session.status,
        'total', cardinality(v_session.question_ids)
      );
    end if;
    raise exception 'unexpected question order';
  end if;

  select q.correct_option,
         coalesce(nullif(trim(q.category), ''), nullif(trim(q.topic), ''), 'Use of English'),
         coalesce(nullif(trim(q.sub_category), ''), 'General')
  into v_correct_option, v_category, v_sub_category
  from public.questions q
  where q.id = p_question_id;

  if v_correct_option is null then
    raise exception 'question not found';
  end if;

  v_actual_correct := p_selected_index = v_correct_option;

  insert into public.learning_session_answers(
    session_id, user_id, question_id, question_index, selected_index, is_correct
  ) values (
    p_session_id, p_user_id, p_question_id, p_question_index, p_selected_index, v_actual_correct
  )
  on conflict (session_id, question_index) do nothing;

  get diagnostics v_row_count = row_count;
  v_inserted := v_row_count > 0;

  if v_inserted then
    update public.learning_sessions
    set answered_count = answered_count + 1,
        correct_count = correct_count + case when v_actual_correct then 1 else 0 end,
        current_index = p_question_index + 1,
        updated_at = now()
    where id = p_session_id;

    insert into public.user_answers(user_id, question_id, is_correct, answer_index, answer)
    values (p_user_id, p_question_id, v_actual_correct, p_selected_index, p_selected_index);

    update public.users
    set total_tasks_solved = coalesce(total_tasks_solved, 0) + 1,
        total_questions_answered = coalesce(total_questions_answered, 0) + 1,
        total_correct_answers = coalesce(total_correct_answers, 0) + case when v_actual_correct then 1 else 0 end,
        xp = coalesce(xp, 0) + case when v_actual_correct then 10 else 3 end,
        last_active_at = now(),
        updated_at = now()
    where id = p_user_id;

    -- Normalize legacy diagnostic taxonomy to the same skill names used by the
    -- regular bank so progress remains continuous across old and new flows.
    if v_category = 'Grammar' then
      v_category := 'Use of English';
      v_sub_category := case v_sub_category
        when 'Tenses' then 'Grammar: Tenses'
        when 'Articles' then 'Grammar: Articles'
        when 'Conditionals' then 'Grammar: Conditionals'
        when 'Modal Verbs' then 'Grammar: Modal Verbs'
        when 'Prepositions' then 'Grammar: Prepositions'
        when 'Mixed Grammar' then 'Grammar: Mixed'
        else v_sub_category
      end;
    elsif v_category = 'Vocabulary' then
      v_category := 'Use of English';
      v_sub_category := case v_sub_category
        when 'Word Formation' then 'Vocabulary: Word Formation'
        when 'Context' then 'Vocabulary: Context'
        else v_sub_category
      end;
    elsif v_category = 'Reading' then
      v_sub_category := case v_sub_category
        when 'Main Idea' then 'Reading: Main Idea'
        when 'Detail' then 'Reading: Detail'
        when 'Vocabulary in Context' then 'Reading: Vocabulary in Context'
        when 'Inference' then 'Reading: Inference'
        else v_sub_category
      end;
    end if;

    v_seed_mastery := case
      when v_session.session_type = 'diagnostic' and v_actual_correct then 55
      when v_session.session_type = 'diagnostic' and not v_actual_correct then 20
      when v_actual_correct then 12
      else 0
    end;
    v_delta := case when v_actual_correct then 12 else -10 end;

    insert into public.user_topic_progress(
      user_id, category, sub_category, attempts, correct, mastery_score,
      current_difficulty, last_answer_correct, last_seen_at, updated_at
    ) values (
      p_user_id, v_category, v_sub_category, 1, case when v_actual_correct then 1 else 0 end,
      v_seed_mastery,
      case when v_seed_mastery < 40 then 1 when v_seed_mastery < 70 then 2 else 3 end,
      v_actual_correct, now(), now()
    )
    on conflict (user_id, category, sub_category) do update
      set attempts = public.user_topic_progress.attempts + 1,
          correct = public.user_topic_progress.correct + case when v_actual_correct then 1 else 0 end,
          mastery_score = greatest(0, least(100, public.user_topic_progress.mastery_score + v_delta)),
          current_difficulty = case
            when greatest(0, least(100, public.user_topic_progress.mastery_score + v_delta)) < 40 then 1
            when greatest(0, least(100, public.user_topic_progress.mastery_score + v_delta)) < 70 then 2
            else 3
          end,
          last_answer_correct = v_actual_correct,
          last_seen_at = now(),
          updated_at = now();

    -- Any answered question is learning activity for retention. Leaderboard
    -- points are still awarded only after a completed session below.
    insert into public.learning_days(user_id, learning_date, answered_count, completed_sessions, leaderboard_points)
    values (p_user_id, v_session.learning_date, 1, 0, 0)
    on conflict (user_id, learning_date) do update
      set answered_count = public.learning_days.answered_count + 1,
          updated_at = now();
  end if;

  select * into v_session
  from public.learning_sessions
  where id = p_session_id;

  if v_session.status = 'active' and v_session.answered_count >= cardinality(v_session.question_ids) then
    update public.learning_sessions
    set status = 'completed', completed_at = coalesce(completed_at, now()), updated_at = now()
    where id = p_session_id;
    v_completed_now := true;

    v_today := v_session.learning_date;
    insert into public.learning_days(user_id, learning_date, answered_count, completed_sessions, leaderboard_points)
    values (p_user_id, v_today, 0, 1, 1)
    on conflict (user_id, learning_date) do update
      set completed_sessions = public.learning_days.completed_sessions + 1,
          leaderboard_points = 1,
          updated_at = now();

    if v_session.session_type = 'intro' then
      update public.users
      set first_lesson_completed_at = coalesce(first_lesson_completed_at, now())
      where id = p_user_id;
    elsif v_session.session_type = 'daily' then
      -- Daily streak changes only once per Kyiv learning date. Intro and
      -- diagnostics never inflate it.
      update public.users
      set streak = case
            when last_streak_date = v_today then coalesce(streak, 0)
            when last_streak_date = v_today - 1 then coalesce(streak, 0) + 1
            else 1
          end,
          last_streak_date = v_today,
          updated_at = now()
      where id = p_user_id;
    end if;
  end if;

  select * into v_session from public.learning_sessions where id = p_session_id;

  return jsonb_build_object(
    'inserted', v_inserted,
    'completed_now', v_completed_now,
    'session_id', v_session.id,
    'current_index', v_session.current_index,
    'answered_count', v_session.answered_count,
    'correct_count', v_session.correct_count,
    'status', v_session.status,
    'total', cardinality(v_session.question_ids),
    'is_correct', v_actual_correct
  );
end;
$$;


-- Referral activation is fully atomic. The legacy referrals_count remains useful,
-- but no Premium reward is granted by the new product flow.
create or replace function public.activate_learning_referral(
  p_referred_user_id bigint
) returns bigint
language plpgsql
security definer
set search_path = public
as $$
declare
  v_referrer_id bigint;
  v_inserted integer := 0;
begin
  select u.referrer_id into v_referrer_id
  from public.users u
  where u.id = p_referred_user_id;

  if v_referrer_id is null or v_referrer_id = p_referred_user_id then
    return null;
  end if;

  insert into public.referral_activations(referred_user_id, referrer_id)
  values (p_referred_user_id, v_referrer_id)
  on conflict (referred_user_id) do nothing;

  get diagnostics v_inserted = row_count;
  if v_inserted = 0 then
    return null;
  end if;

  update public.users
  set referrals_count = coalesce(referrals_count, 0) + 1,
      updated_at = now()
  where id = v_referrer_id;

  return v_referrer_id;
end;
$$;

-- Return reminder recipients database-side so reminder delivery is not capped
-- by PostgREST page size. A partial session still counts for retention, but only
-- a completed daily session suppresses the reminder as required by the product.
create or replace function public.get_learning_reminder_candidates(
  p_learning_date date,
  p_reminder_time time,
  p_limit integer default 2000
) returns table(user_id bigint)
language sql
security definer
set search_path = public
as $$
  select u.id
  from public.users u
  where u.is_active = true
    and u.reminder_enabled = true
    and u.reminder_time is not null
    and extract(hour from u.reminder_time) = extract(hour from p_reminder_time)
    and extract(minute from u.reminder_time) = extract(minute from p_reminder_time)
    and not exists (
      select 1
      from public.learning_sessions s
      where s.user_id = u.id
        and s.session_type = 'daily'
        and s.learning_date = p_learning_date
        and s.status = 'completed'
    )
    and (
      u.last_reminder_at is null
      or (u.last_reminder_at at time zone 'Europe/Kyiv')::date <> p_learning_date
    )
  order by u.id
  limit greatest(1, least(coalesce(p_limit, 2000), 10000));
$$;


-- Weekly leaderboard is aggregated database-side so it remains correct after
-- the user base exceeds PostgREST row limits.
create or replace function public.get_weekly_learning_leaderboard(
  p_user_id bigint,
  p_week_start date,
  p_week_end date,
  p_limit integer default 10
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_rows jsonb := '[]'::jsonb;
  v_my_rank integer;
begin
  with scores as (
    select u.id as user_id,
           coalesce(nullif(u.public_alias, ''), 'Учасник') as alias,
           sum(least(1, greatest(0, d.leaderboard_points)))::int as days
    from public.users u
    join public.learning_days d on d.user_id = u.id
    where d.learning_date between p_week_start and p_week_end
      and u.leaderboard_opt_in = true
      and coalesce(u.is_test_account, false) = false
    group by u.id, u.public_alias
  ), ranked as (
    select s.*,
           (row_number() over (order by s.days desc, s.alias asc, s.user_id asc))::int as rank
    from scores s
  )
  select coalesce(
           jsonb_agg(
             jsonb_build_object('user_id', user_id, 'alias', alias, 'days', days, 'rank', rank)
             order by rank
           ),
           '[]'::jsonb
         )
  into v_rows
  from ranked
  where rank <= greatest(1, least(coalesce(p_limit, 10), 100));

  with scores as (
    select u.id as user_id,
           coalesce(nullif(u.public_alias, ''), 'Учасник') as alias,
           sum(least(1, greatest(0, d.leaderboard_points)))::int as days
    from public.users u
    join public.learning_days d on d.user_id = u.id
    where d.learning_date between p_week_start and p_week_end
      and u.leaderboard_opt_in = true
      and coalesce(u.is_test_account, false) = false
    group by u.id, u.public_alias
  ), ranked as (
    select s.user_id,
           (row_number() over (order by s.days desc, s.alias asc, s.user_id asc))::int as rank
    from scores s
  )
  select r.rank into v_my_rank
  from ranked r
  where r.user_id = p_user_id;

  return jsonb_build_object(
    'rows', v_rows,
    'my_rank', v_my_rank,
    'week_start', p_week_start,
    'week_end', p_week_end
  );
end;
$$;

-- Reliable aggregated admin report. Aggregation is performed inside PostgreSQL,
-- avoiding client row limits as the user base grows.
create or replace function public.get_learning_admin_report(
  p_admin_ids bigint[] default '{}'::bigint[],
  p_days integer default 7
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_cutoff timestamptz := now() - make_interval(days => greatest(1, least(coalesce(p_days, 7), 90)));
  v_today date := (now() at time zone 'Europe/Kyiv')::date;
  v_sources jsonb := '{}'::jsonb;
  v_events jsonb := '{}'::jsonb;
  v_dropouts integer := 0;
  v_latency jsonb := '{}'::jsonb;
  v_errors jsonb := '{}'::jsonb;
  v_retention jsonb := '{}'::jsonb;
begin
  select coalesce(jsonb_object_agg(src, cnt), '{}'::jsonb)
  into v_sources
  from (
    select coalesce(nullif(u.acquisition_source, ''), 'unknown') as src, count(*)::int as cnt
    from public.users u
    where coalesce(u.is_test_account, false) = false
      and not (u.id = any(coalesce(p_admin_ids, '{}'::bigint[])))
    group by 1
  ) s;

  select coalesce(jsonb_object_agg(event_name, cnt), '{}'::jsonb)
  into v_events
  from (
    select e.event_name, count(*)::int as cnt
    from public.events e
    join public.users u on u.id = e.user_id
    where e.created_at >= v_cutoff
      and coalesce(u.is_test_account, false) = false
      and not (u.id = any(coalesce(p_admin_ids, '{}'::bigint[])))
    group by e.event_name
  ) e;

  with valid_events as (
    select e.event_name,
           e.metadata->>'session_id' as session_id,
           coalesce(e.metadata->>'question_index', '0') as question_index
    from public.events e
    join public.users u on u.id = e.user_id
    where e.created_at >= v_cutoff
      and coalesce(u.is_test_account, false) = false
      and not (u.id = any(coalesce(p_admin_ids, '{}'::bigint[])))
      and e.metadata ? 'session_id'
  ), shown as (
    select distinct session_id, question_index
    from valid_events where event_name = 'question_shown'
  ), answered as (
    select distinct session_id, question_index
    from valid_events where event_name = 'question_answered'
  )
  select count(*)::int into v_dropouts
  from shown s
  left join answered a using(session_id, question_index)
  where a.session_id is null;

  select coalesce(jsonb_object_agg(metric_name, payload), '{}'::jsonb)
  into v_latency
  from (
    select m.metric_name,
           jsonb_build_object(
             'p50', round(percentile_cont(0.50) within group(order by m.duration_ms))::int,
             'p95', round(percentile_cont(0.95) within group(order by m.duration_ms))::int,
             'n', count(*)::int
           ) as payload
    from public.operational_metrics m
    left join public.users u on u.id = m.user_id
    where m.created_at >= v_cutoff
      and m.duration_ms is not null
      and m.metric_name in ('start_handler_ms','lesson_start_ms','answer_handler_ms','webhook_response_ms','process_to_first_webhook_ms')
      and (
        m.user_id is null
        or (coalesce(u.is_test_account, false) = false and not (m.user_id = any(coalesce(p_admin_ids, '{}'::bigint[]))))
      )
    group by m.metric_name
  ) x;

  select coalesce(jsonb_object_agg(error_type, cnt), '{}'::jsonb)
  into v_errors
  from (
    select er.error_type, count(*)::int as cnt
    from public.error_reports er
    left join public.users u on u.id = er.user_id
    where er.created_at >= v_cutoff
      and (
        er.user_id is null
        or (coalesce(u.is_test_account, false) = false and not (er.user_id = any(coalesce(p_admin_ids, '{}'::bigint[]))))
      )
    group by er.error_type
  ) x;

  with valid_users as (
    select u.id
    from public.users u
    where coalesce(u.is_test_account, false) = false
      and not (u.id = any(coalesce(p_admin_ids, '{}'::bigint[])))
  ), first_days as (
    select d.user_id, min(d.learning_date) as first_day
    from public.learning_days d
    join valid_users v on v.id = d.user_id
    group by d.user_id
  ), r as (
    select
      count(*) filter (where v_today > f.first_day + 1)::int as d1_eligible,
      count(*) filter (
        where v_today > f.first_day + 1
          and exists(select 1 from public.learning_days d where d.user_id=f.user_id and d.learning_date=f.first_day+1)
      )::int as d1_returned,
      count(*) filter (where v_today > f.first_day + 3)::int as d3_eligible,
      count(*) filter (
        where v_today > f.first_day + 3
          and exists(select 1 from public.learning_days d where d.user_id=f.user_id and d.learning_date=f.first_day+3)
      )::int as d3_returned,
      count(*) filter (where v_today > f.first_day + 7)::int as d7_eligible,
      count(*) filter (
        where v_today > f.first_day + 7
          and exists(select 1 from public.learning_days d where d.user_id=f.user_id and d.learning_date=f.first_day+7)
      )::int as d7_returned
    from first_days f
  )
  select jsonb_build_object(
    'd1', jsonb_build_object('eligible', d1_eligible, 'returned', d1_returned),
    'd3', jsonb_build_object('eligible', d3_eligible, 'returned', d3_returned),
    'd7', jsonb_build_object('eligible', d7_eligible, 'returned', d7_returned)
  ) into v_retention
  from r;

  return jsonb_build_object(
    'sources', v_sources,
    'events', v_events,
    'dropout_shown_without_answer', coalesce(v_dropouts, 0),
    'latency', v_latency,
    'errors', v_errors,
    'retention', coalesce(v_retention, '{}'::jsonb)
  );
end;
$$;

create or replace function public.get_question_bank_audit()
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_categories jsonb := '{}'::jsonb;
  v_total integer := 0;
  v_active integer := 0;
  v_diag integer := 0;
  v_intro integer := 0;
begin
  select count(*)::int,
         count(*) filter (where q.is_active=true and q.quality_status='approved' and q.is_diagnostic=false)::int,
         count(*) filter (where q.is_active=true and q.quality_status='approved' and q.is_diagnostic=true)::int,
         count(*) filter (where q.is_active=true and q.quality_status='approved' and q.is_intro=true)::int
  into v_total, v_active, v_diag, v_intro
  from public.questions q;

  select coalesce(jsonb_object_agg(category_name, cnt), '{}'::jsonb)
  into v_categories
  from (
    select case
      when lower(coalesce(q.category, q.topic, '')) like '%read%' then 'Reading'
      when lower(coalesce(q.category, q.topic, '')) like '%use of english%' then 'Use of English'
      when lower(coalesce(q.category, q.topic, '')) like '%grammar%' then 'Use of English'
      when lower(coalesce(q.category, q.topic, '')) like '%vocab%' then 'Use of English'
      else coalesce(nullif(q.category,''), nullif(q.topic,''), 'Інше')
    end as category_name,
    count(*)::int as cnt
    from public.questions q
    where q.is_active=true and q.quality_status='approved' and q.is_diagnostic=false
    group by 1
  ) c;

  return jsonb_build_object(
    'total', v_total,
    'active_approved', v_active,
    'diagnostic_active', v_diag,
    'intro_active', v_intro,
    'categories', v_categories
  );
end;
$$;

create or replace view public.learning_retention_daily as
with first_day as (
  select user_id, min(learning_date) as cohort_date
  from public.learning_days
  group by user_id
), eligible as (
  select f.user_id, f.cohort_date, u.is_test_account
  from first_day f
  join public.users u on u.id = f.user_id
)
select
  e.cohort_date,
  count(*) filter (where not e.is_test_account) as cohort_users,
  count(*) filter (
    where not e.is_test_account
      and current_date > e.cohort_date + 1
      and exists(select 1 from public.learning_days d where d.user_id=e.user_id and d.learning_date=e.cohort_date+1)
  ) as d1_returned,
  count(*) filter (
    where not e.is_test_account
      and current_date > e.cohort_date + 3
      and exists(select 1 from public.learning_days d where d.user_id=e.user_id and d.learning_date=e.cohort_date+3)
  ) as d3_returned,
  count(*) filter (
    where not e.is_test_account
      and current_date > e.cohort_date + 7
      and exists(select 1 from public.learning_days d where d.user_id=e.user_id and d.learning_date=e.cohort_date+7)
  ) as d7_returned,
  count(*) filter (where not e.is_test_account and current_date > e.cohort_date + 1) as d1_eligible,
  count(*) filter (where not e.is_test_account and current_date > e.cohort_date + 3) as d3_eligible,
  count(*) filter (where not e.is_test_account and current_date > e.cohort_date + 7) as d7_eligible
from eligible e
group by e.cohort_date;


-- ============================================================
-- V4 production hardening
-- The Telegram bot is the only client allowed to call internal RPCs directly.
-- Use the Supabase server-side service-role/secret key on Render.
-- ============================================================

do $$
declare
  r record;
begin
  for r in
    select p.oid::regprocedure as fn
    from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public'
      and p.proname = any(array[
        'ensure_learning_start_context',
        'select_learning_questions',
        'record_learning_answer',
        'activate_learning_referral',
        'get_learning_reminder_candidates',
        'get_weekly_learning_leaderboard',
        'get_learning_admin_report',
        'get_question_bank_audit'
      ])
  loop
    execute format('revoke all on function %s from public', r.fn);
    execute format('revoke all on function %s from anon', r.fn);
    execute format('revoke all on function %s from authenticated', r.fn);
    execute format('grant execute on function %s to service_role', r.fn);
  end loop;
end $$;

-- Personal/operational tables are backend-only in the Telegram version.
-- service_role bypasses RLS; future web clients should get explicit policies,
-- never broad table access.
alter table public.users enable row level security;
alter table public.user_answers enable row level security;
alter table public.user_topics enable row level security;
alter table public.user_topic_progress enable row level security;
alter table public.orders enable row level security;
alter table public.referral_rewards enable row level security;
alter table public.events enable row level security;
alter table public.learning_sessions enable row level security;
alter table public.learning_session_answers enable row level security;
alter table public.learning_days enable row level security;
alter table public.operational_metrics enable row level security;
alter table public.error_reports enable row level security;

revoke all on table public.users from anon, authenticated;
revoke all on table public.user_answers from anon, authenticated;
revoke all on table public.user_topics from anon, authenticated;
revoke all on table public.user_topic_progress from anon, authenticated;
revoke all on table public.orders from anon, authenticated;
revoke all on table public.referral_rewards from anon, authenticated;
revoke all on table public.events from anon, authenticated;
revoke all on table public.learning_sessions from anon, authenticated;
revoke all on table public.learning_session_answers from anon, authenticated;
revoke all on table public.learning_days from anon, authenticated;
revoke all on table public.operational_metrics from anon, authenticated;
revoke all on table public.error_reports from anon, authenticated;

-- Keep the question bank private from direct anonymous API scraping too.
alter table public.questions enable row level security;
revoke all on table public.questions from anon, authenticated;
