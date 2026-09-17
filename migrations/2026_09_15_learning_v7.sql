-- Neta NMT English v7
-- ONE-FILE UPGRADE: safe to run if production is currently on v4, v5 or v6.
-- Includes the full v6 data/history/XP upgrade, then adds v7 benefit-first practice modes.
-- No users, answers, orders, payment history or Premium rights are deleted.

-- Neta NMT English v6
-- Upgrade migration: safe to run on v4 OR v5; v5's history backfill is included.
-- Business/product change:
--   Daily = 4-question habit anchor, NOT a daily learning limit.
--   Unlimited additional 5/10-question adaptive practice.
--   Weekly XP rewards real study effort; duplicate/farming protections remain.
--   Existing users, answers, orders, payments and Premium rights are preserved.

begin;

-- Rebuild topic progress from the complete canonical answer history.
-- It is deterministic and safe to re-run: existing rows are SET to the aggregate,
-- not incremented again.
insert into public.user_topic_progress (
  user_id,
  category,
  sub_category,
  attempts,
  correct,
  mastery_score,
  current_difficulty,
  last_seen_at,
  updated_at
)
select
  ua.user_id,
  coalesce(nullif(q.category, ''), nullif(q.topic, ''), 'Other') as category,
  coalesce(nullif(q.sub_category, ''), nullif(q.category, ''), nullif(q.topic, ''), 'General') as sub_category,
  count(*)::integer as attempts,
  count(*) filter (where ua.is_correct)::integer as correct,
  round((100.0 * count(*) filter (where ua.is_correct) / nullif(count(*), 0))::numeric, 2) as mastery_score,
  case
    when (100.0 * count(*) filter (where ua.is_correct) / nullif(count(*), 0)) < 40 then 1
    when (100.0 * count(*) filter (where ua.is_correct) / nullif(count(*), 0)) < 70 then 2
    else 3
  end as current_difficulty,
  max(ua.answered_at) as last_seen_at,
  now() as updated_at
from public.user_answers ua
join public.questions q on q.id = ua.question_id
group by
  ua.user_id,
  coalesce(nullif(q.category, ''), nullif(q.topic, ''), 'Other'),
  coalesce(nullif(q.sub_category, ''), nullif(q.category, ''), nullif(q.topic, ''), 'General')
on conflict (user_id, category, sub_category)
do update set
  attempts = excluded.attempts,
  correct = excluded.correct,
  mastery_score = excluded.mastery_score,
  current_difficulty = excluded.current_difficulty,
  last_seen_at = excluded.last_seen_at,
  updated_at = now();

-- Preserve all answers, but if an old version left parallel active sessions,
-- keep the newest resumable one and mark only the older unfinished shells abandoned.
with ranked_active as (
  select
    s.id,
    row_number() over(
      partition by s.user_id
      order by s.updated_at desc, s.started_at desc, s.id desc
    ) as rn
  from public.learning_sessions s
  where s.status = 'active'
)
update public.learning_sessions s
set status = 'abandoned', updated_at = now()
from ranked_active r
where s.id = r.id and r.rn > 1;

create unique index if not exists learning_sessions_one_active_per_user_uidx
  on public.learning_sessions(user_id)
  where status = 'active';

create table if not exists public.learning_xp_events (
  id bigint generated always as identity primary key,
  user_id bigint not null references public.users(id) on delete cascade,
  learning_date date not null,
  event_type text not null check (event_type in ('answer','daily_bonus','streak_bonus')),
  points integer not null check (points between 1 and 10),
  question_id uuid references public.questions(id),
  session_id uuid references public.learning_sessions(id) on delete set null,
  event_key text not null unique,
  created_at timestamptz not null default now()
);

create index if not exists learning_xp_events_user_date_idx
  on public.learning_xp_events(user_id, learning_date desc);

create unique index if not exists learning_xp_answer_question_day_uidx
  on public.learning_xp_events(user_id, question_id, learning_date)
  where event_type = 'answer' and question_id is not null;

alter table public.learning_xp_events enable row level security;
revoke all on table public.learning_xp_events from anon, authenticated;
grant select, insert, update, delete on table public.learning_xp_events to service_role;
grant usage, select on sequence public.learning_xp_events_id_seq to service_role;

-- Backfill one answer-XP reward per question per Kyiv day from the complete
-- canonical answer history. Earliest attempt wins for that day.
with first_attempt as (
  select distinct on (
    ua.user_id,
    ua.question_id,
    (ua.answered_at at time zone 'Europe/Kyiv')::date
  )
    ua.id,
    ua.user_id,
    ua.question_id,
    ua.is_correct,
    (ua.answered_at at time zone 'Europe/Kyiv')::date as learning_date,
    ua.answered_at
  from public.user_answers ua
  where ua.user_id is not null
    and ua.question_id is not null
    and ua.answered_at is not null
  order by
    ua.user_id,
    ua.question_id,
    (ua.answered_at at time zone 'Europe/Kyiv')::date,
    ua.answered_at asc,
    ua.id asc
)
insert into public.learning_xp_events(
  user_id, learning_date, event_type, points, question_id, event_key, created_at
)
select
  f.user_id,
  f.learning_date,
  'answer',
  case when f.is_correct then 2 else 1 end,
  f.question_id,
  format('answer:%s:%s:%s', f.user_id, f.question_id, f.learning_date),
  f.answered_at
from first_attempt f
on conflict do nothing;

-- Historical completed Daily sessions receive the same +5 habit bonus.
insert into public.learning_xp_events(
  user_id, learning_date, event_type, points, session_id, event_key, created_at
)
select distinct on (s.user_id, s.learning_date)
  s.user_id,
  s.learning_date,
  'daily_bonus',
  5,
  s.id,
  format('daily:%s:%s', s.user_id, s.learning_date),
  coalesce(s.completed_at, s.updated_at, now())
from public.learning_sessions s
where s.session_type = 'daily'
  and s.status = 'completed'
order by s.user_id, s.learning_date, s.completed_at asc nulls last
on conflict do nothing;

-- v4 used a different hidden XP scale. XP was not part of the learner-facing
-- product, so normalize it once to the new transparent ledger.
update public.users u
set xp = coalesce((
  select sum(x.points)::integer
  from public.learning_xp_events x
  where x.user_id = u.id
), 0);

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
  v_len integer := greatest(3, least(coalesce(p_length, 4), case when p_session_type = 'diagnostic' then 12 when p_session_type = 'practice' then 10 else 5 end));
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

-- Race-safe practice creation/resume. A user never gets parallel active
-- sessions from double taps or old Telegram buttons.
create or replace function public.create_practice_session_v6(
  p_user_id bigint,
  p_length integer
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_len integer := case when coalesce(p_length, 5) >= 10 then 10 else 5 end;
  v_today date := (now() at time zone 'Europe/Kyiv')::date;
  v_existing public.learning_sessions%rowtype;
  v_question_ids uuid[];
  v_session public.learning_sessions%rowtype;
begin
  perform 1 from public.users u where u.id = p_user_id for update;
  if not found then
    raise exception 'user not found';
  end if;

  select * into v_existing
  from public.learning_sessions s
  where s.user_id = p_user_id
    and s.status = 'active'
  order by s.updated_at desc
  limit 1;

  if found then
    return to_jsonb(v_existing);
  end if;

  select array_agg(x.question_id order by x.ord)
  into v_question_ids
  from public.select_learning_questions(p_user_id, 'practice', v_len) x;

  if coalesce(cardinality(v_question_ids), 0) < v_len then
    raise exception 'question selector returned only %/% questions',
      coalesce(cardinality(v_question_ids), 0), v_len;
  end if;

  insert into public.learning_sessions(
    user_id, session_key, session_type, learning_date, question_ids,
    current_index, answered_count, correct_count, status
  ) values (
    p_user_id,
    format('practice:%s:%s', v_today, gen_random_uuid()),
    'practice',
    v_today,
    v_question_ids,
    0, 0, 0, 'active'
  )
  returning * into v_session;

  return to_jsonb(v_session);
end;
$$;

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
  v_xp_points integer := 0;
  v_xp_inserted integer := 0;
  v_xp_awarded integer := 0;
  v_streak integer := 0;
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
        last_active_at = now(),
        updated_at = now()
    where id = p_user_id;

    v_xp_points := case when v_actual_correct then 2 else 1 end;
    insert into public.learning_xp_events(
      user_id, learning_date, event_type, points, question_id, session_id, event_key
    ) values (
      p_user_id, v_session.learning_date, 'answer', v_xp_points, p_question_id, p_session_id,
      format('answer:%s:%s:%s', p_user_id, p_question_id, v_session.learning_date)
    )
    on conflict do nothing;
    get diagnostics v_xp_inserted = row_count;
    if v_xp_inserted > 0 then
      update public.users set xp = coalesce(xp, 0) + v_xp_points where id = p_user_id;
      v_xp_awarded := v_xp_awarded + v_xp_points;
    end if;

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
    values (
      p_user_id, v_today, 0, 1,
      case when v_session.session_type = 'daily' then 1 else 0 end
    )
    on conflict (user_id, learning_date) do update
      set completed_sessions = public.learning_days.completed_sessions + 1,
          leaderboard_points = greatest(
            public.learning_days.leaderboard_points,
            excluded.leaderboard_points
          ),
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

      select coalesce(u.streak, 0) into v_streak
      from public.users u where u.id = p_user_id;

      insert into public.learning_xp_events(
        user_id, learning_date, event_type, points, session_id, event_key
      ) values (
        p_user_id, v_today, 'daily_bonus', 5, p_session_id,
        format('daily:%s:%s', p_user_id, v_today)
      )
      on conflict do nothing;
      get diagnostics v_xp_inserted = row_count;
      if v_xp_inserted > 0 then
        update public.users set xp = coalesce(xp, 0) + 5 where id = p_user_id;
        v_xp_awarded := v_xp_awarded + 5;
      end if;

      v_xp_points := least(5, greatest(0, v_streak - 1));
      if v_xp_points > 0 then
        insert into public.learning_xp_events(
          user_id, learning_date, event_type, points, session_id, event_key
        ) values (
          p_user_id, v_today, 'streak_bonus', v_xp_points, p_session_id,
          format('streak:%s:%s', p_user_id, v_today)
        )
        on conflict do nothing;
        get diagnostics v_xp_inserted = row_count;
        if v_xp_inserted > 0 then
          update public.users set xp = coalesce(xp, 0) + v_xp_points where id = p_user_id;
          v_xp_awarded := v_xp_awarded + v_xp_points;
        end if;
      end if;
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
    'is_correct', v_actual_correct,
    'xp_awarded', v_xp_awarded
  );
end;
$$;


create or replace function public.get_session_xp_v6(
  p_session_id uuid,
  p_user_id bigint
) returns integer
language sql
stable
security definer
set search_path = public
as $$
  select coalesce(sum(x.points), 0)::integer
  from public.learning_xp_events x
  where x.session_id = p_session_id
    and x.user_id = p_user_id;
$$;

create or replace function public.get_user_learning_progress_v6(p_user_id bigint)
returns jsonb
language sql
stable
security definer
set search_path = public
as $$
  with answer_summary as (
    select
      count(*)::integer as attempts,
      count(*) filter (where ua.is_correct)::integer as correct
    from public.user_answers ua
    where ua.user_id = p_user_id
  ),
  all_learning_dates as (
    select (ua.answered_at at time zone 'Europe/Kyiv')::date as learning_date
    from public.user_answers ua
    where ua.user_id = p_user_id and ua.answered_at is not null
    union
    select ld.learning_date
    from public.learning_days ld
    where ld.user_id = p_user_id
  ),
  day_summary as (
    select count(distinct learning_date)::integer as learning_days
    from all_learning_dates where learning_date is not null
  ),
  skill_rows as (
    select
      coalesce(nullif(q.category, ''), nullif(q.topic, ''), 'Other') as category,
      coalesce(nullif(q.sub_category, ''), nullif(q.category, ''), nullif(q.topic, ''), 'General') as sub_category,
      count(*)::integer as attempts,
      count(*) filter (where ua.is_correct)::integer as correct,
      round((100.0 * count(*) filter (where ua.is_correct) / nullif(count(*), 0))::numeric, 2) as mastery_score
    from public.user_answers ua
    join public.questions q on q.id = ua.question_id
    where ua.user_id = p_user_id
    group by
      coalesce(nullif(q.category, ''), nullif(q.topic, ''), 'Other'),
      coalesce(nullif(q.sub_category, ''), nullif(q.category, ''), nullif(q.topic, ''), 'General')
  ),
  skills_json as (
    select coalesce(jsonb_agg(
      jsonb_build_object(
        'category', category,
        'sub_category', sub_category,
        'attempts', attempts,
        'correct', correct,
        'mastery_score', mastery_score
      )
      order by attempts desc, mastery_score asc, sub_category
    ), '[]'::jsonb) as skills
    from skill_rows
  ),
  xp_summary as (
    select
      coalesce(sum(x.points), 0)::integer as xp_total,
      coalesce(sum(x.points) filter (
        where x.learning_date >= date_trunc('week', now() at time zone 'Europe/Kyiv')::date
          and x.learning_date < (date_trunc('week', now() at time zone 'Europe/Kyiv')::date + 7)
      ), 0)::integer as xp_week
    from public.learning_xp_events x
    where x.user_id = p_user_id
  )
  select jsonb_build_object(
    'attempts', coalesce(a.attempts, 0),
    'correct', coalesce(a.correct, 0),
    'learning_days', coalesce(d.learning_days, 0),
    'streak', coalesce(u.streak, 0),
    'xp_total', coalesce(x.xp_total, 0),
    'xp_week', coalesce(x.xp_week, 0),
    'skills', s.skills
  )
  from answer_summary a
  cross join day_summary d
  cross join skills_json s
  cross join xp_summary x
  left join public.users u on u.id = p_user_id;
$$;

create or replace function public.get_weekly_xp_leaderboard_v6(
  p_user_id bigint,
  p_week_start date,
  p_week_end date,
  p_limit integer default 10
) returns jsonb
language sql
stable
security definer
set search_path = public
as $$
  with scores as (
    select
      u.id as user_id,
      coalesce(nullif(u.public_alias, ''), 'Учасник') as alias,
      coalesce(sum(x.points), 0)::integer as xp,
      count(distinct x.learning_date)::integer as days
    from public.users u
    join public.learning_xp_events x on x.user_id = u.id
    where x.learning_date between p_week_start and p_week_end
      and u.leaderboard_opt_in = true
      and coalesce(u.is_test_account, false) = false
    group by u.id, u.public_alias
  ),
  ranked as (
    select
      s.*,
      row_number() over(order by s.xp desc, s.days desc, s.alias asc, s.user_id asc)::integer as rank
    from scores s
  ),
  top_rows as (
    select coalesce(jsonb_agg(
      jsonb_build_object(
        'user_id', r.user_id,
        'alias', r.alias,
        'xp', r.xp,
        'days', r.days,
        'rank', r.rank
      ) order by r.rank
    ), '[]'::jsonb) as rows
    from ranked r
    where r.rank <= greatest(1, least(coalesce(p_limit, 10), 100))
  ),
  me as (
    select r.rank, r.xp, r.days from ranked r where r.user_id = p_user_id
  )
  select jsonb_build_object(
    'rows', t.rows,
    'my_rank', (select rank from me),
    'my_xp', coalesce((select xp from me), 0),
    'my_days', coalesce((select days from me), 0),
    'week_start', p_week_start,
    'week_end', p_week_end
  )
  from top_rows t;
$$;


-- If the learner already completed any real learning session today, do not send
-- a return reminder. Daily is a habit anchor, not a reason to nag someone who
-- already studied more.
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
        and s.learning_date = p_learning_date
        and s.status = 'completed'
        and s.session_type in ('intro','daily','practice','diagnostic')
    )
    and (
      u.last_reminder_at is null
      or (u.last_reminder_at at time zone 'Europe/Kyiv')::date <> p_learning_date
    )
  order by u.id
  limit greatest(1, least(coalesce(p_limit, 2000), 10000));
$$;

revoke all on function public.get_learning_reminder_candidates(date, time, integer) from public, anon, authenticated;
revoke all on function public.select_learning_questions(bigint, text, integer) from public, anon, authenticated;
revoke all on function public.record_learning_answer(uuid, bigint, uuid, integer, integer, boolean) from public, anon, authenticated;
revoke all on function public.create_practice_session_v6(bigint, integer) from public, anon, authenticated;
revoke all on function public.get_session_xp_v6(uuid, bigint) from public, anon, authenticated;
revoke all on function public.get_user_learning_progress_v6(bigint) from public, anon, authenticated;
revoke all on function public.get_weekly_xp_leaderboard_v6(bigint, date, date, integer) from public, anon, authenticated;

grant execute on function public.get_learning_reminder_candidates(date, time, integer) to service_role;
grant execute on function public.select_learning_questions(bigint, text, integer) to service_role;
grant execute on function public.record_learning_answer(uuid, bigint, uuid, integer, integer, boolean) to service_role;
grant execute on function public.create_practice_session_v6(bigint, integer) to service_role;
grant execute on function public.get_session_xp_v6(uuid, bigint) to service_role;
grant execute on function public.get_user_learning_progress_v6(bigint) to service_role;
grant execute on function public.get_weekly_xp_leaderboard_v6(bigint, date, date, integer) to service_role;

commit;


-- ============================================================
-- Neta v7 product CTA semantics
-- Safe incremental layer on top of the v6 upgrade above.
-- ============================================================
begin;

create or replace function public.select_practice_questions_v7(
  p_user_id bigint,
  p_mode text,
  p_length integer
) returns table(question_id uuid, ord integer)
language plpgsql
security definer
set search_path = public
as $$
declare
  v_len integer := case when coalesce(p_length, 5) >= 10 then 10 else 5 end;
  v_mode text := case when p_mode in ('focus','challenge','full') then p_mode else 'full' end;
begin
  if v_mode = 'focus' then
    return query
    with latest as (
      select distinct on (ua.question_id)
        ua.question_id, ua.is_correct, ua.answered_at
      from public.user_answers ua
      join public.questions q on q.id = ua.question_id
      where ua.user_id = p_user_id
        and ua.question_id is not null
        and q.is_active = true
        and q.quality_status = 'approved'
        and q.is_diagnostic = false
      order by ua.question_id, ua.answered_at desc
    ),
    weak as (
      select l.question_id as id, l.answered_at
      from latest l
      where l.is_correct = false
      order by l.answered_at desc
      limit v_len
    ),
    fallback as (
      select x.question_id as id, x.ord
      from public.select_learning_questions(p_user_id, 'practice', v_len) x
      where not exists (select 1 from weak w where w.id = x.question_id)
      limit greatest(0, v_len - (select count(*)::integer from weak))
    ),
    combined as (
      select w.id, row_number() over(order by w.answered_at desc)::integer as sort_key
      from weak w
      union all
      select f.id, ((select count(*)::integer from weak) + f.ord)::integer
      from fallback f
    )
    select c.id, row_number() over(order by c.sort_key)::integer
    from combined c
    order by c.sort_key
    limit v_len;
    return;
  end if;

  if v_mode = 'challenge' then
    return query
    with seen as (
      select distinct ua.question_id
      from public.user_answers ua
      where ua.user_id = p_user_id and ua.question_id is not null
    ),
    hard_unseen as (
      select q.id
      from public.questions q
      where q.is_active = true
        and q.quality_status = 'approved'
        and q.is_diagnostic = false
        and coalesce(q.difficulty, 1) >= 2
        and not exists (select 1 from seen s where s.question_id = q.id)
      order by coalesce(q.difficulty, 1) desc, q.usage_count asc, random()
      limit v_len
    ),
    hard_seen as (
      select q.id
      from public.questions q
      where q.is_active = true
        and q.quality_status = 'approved'
        and q.is_diagnostic = false
        and coalesce(q.difficulty, 1) >= 2
        and not exists (select 1 from hard_unseen h where h.id = q.id)
      order by coalesce(q.difficulty, 1) desc, q.usage_count asc, random()
      limit greatest(0, v_len - (select count(*)::integer from hard_unseen))
    ),
    combined as (
      select h.id, 0 as grp from hard_unseen h
      union all
      select h.id, 1 as grp from hard_seen h
    )
    select c.id, row_number() over(order by c.grp, random())::integer
    from combined c
    limit v_len;
    return;
  end if;

  return query
  select x.question_id, x.ord
  from public.select_learning_questions(p_user_id, 'practice', v_len) x
  order by x.ord;
end;
$$;

create or replace function public.create_practice_session_v7(
  p_user_id bigint,
  p_length integer,
  p_mode text default 'full'
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  v_len integer := case when coalesce(p_length, 5) >= 10 then 10 else 5 end;
  v_mode text := case when p_mode in ('focus','challenge','full') then p_mode else 'full' end;
  v_today date := (now() at time zone 'Europe/Kyiv')::date;
  v_existing public.learning_sessions%rowtype;
  v_question_ids uuid[];
  v_session public.learning_sessions%rowtype;
begin
  perform 1 from public.users u where u.id = p_user_id for update;
  if not found then
    raise exception 'user not found';
  end if;

  select * into v_existing
  from public.learning_sessions s
  where s.user_id = p_user_id
    and s.status = 'active'
  order by s.updated_at desc
  limit 1;

  if found then
    return to_jsonb(v_existing);
  end if;

  select array_agg(x.question_id order by x.ord)
  into v_question_ids
  from public.select_practice_questions_v7(p_user_id, v_mode, v_len) x;

  if coalesce(cardinality(v_question_ids), 0) < v_len then
    -- Defensive fallback: never block motivated learners because a specialized
    -- pool is temporarily too small.
    select array_agg(x.question_id order by x.ord)
    into v_question_ids
    from public.select_learning_questions(p_user_id, 'practice', v_len) x;
  end if;

  if coalesce(cardinality(v_question_ids), 0) < v_len then
    raise exception 'question selector returned only %/% questions',
      coalesce(cardinality(v_question_ids), 0), v_len;
  end if;

  insert into public.learning_sessions(
    user_id, session_key, session_type, learning_date, question_ids,
    current_index, answered_count, correct_count, status
  ) values (
    p_user_id,
    format('practice:%s:%s:%s', v_mode, v_today, gen_random_uuid()),
    'practice',
    v_today,
    v_question_ids,
    0, 0, 0, 'active'
  )
  returning * into v_session;

  return to_jsonb(v_session) || jsonb_build_object('practice_mode', v_mode);
end;
$$;

revoke all on function public.select_practice_questions_v7(bigint, text, integer) from public, anon, authenticated;
revoke all on function public.create_practice_session_v7(bigint, integer, text) from public, anon, authenticated;
grant execute on function public.select_practice_questions_v7(bigint, text, integer) to service_role;
grant execute on function public.create_practice_session_v7(bigint, integer, text) to service_role;

commit;
