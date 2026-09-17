-- Neta NMT English v5
-- Incremental migration: run AFTER the v4 migration.
-- Purpose:
--   1) restore one continuous progress history from legacy + current user_answers;
--   2) rebuild Neta Memory topic stats so old mistakes can influence future Daily sessions;
--   3) expose one backend-only progress RPC to avoid API row-limit/fallback bugs.
--
-- This migration does NOT delete users, answers, orders, payments or Premium rights.

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

create or replace function public.get_user_learning_progress_v5(p_user_id bigint)
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
    where ua.user_id = p_user_id
      and ua.answered_at is not null
    union
    select ld.learning_date
    from public.learning_days ld
    where ld.user_id = p_user_id
  ),
  day_summary as (
    select count(distinct learning_date)::integer as learning_days
    from all_learning_dates
    where learning_date is not null
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
    select coalesce(
      jsonb_agg(
        jsonb_build_object(
          'category', category,
          'sub_category', sub_category,
          'attempts', attempts,
          'correct', correct,
          'mastery_score', mastery_score
        )
        order by attempts desc, mastery_score asc, sub_category
      ),
      '[]'::jsonb
    ) as skills
    from skill_rows
  )
  select jsonb_build_object(
    'attempts', coalesce(a.attempts, 0),
    'correct', coalesce(a.correct, 0),
    'learning_days', coalesce(d.learning_days, 0),
    'streak', coalesce(u.streak, 0),
    'skills', s.skills
  )
  from answer_summary a
  cross join day_summary d
  cross join skills_json s
  left join public.users u on u.id = p_user_id;
$$;

revoke all on function public.get_user_learning_progress_v5(bigint) from public;
revoke all on function public.get_user_learning_progress_v5(bigint) from anon;
revoke all on function public.get_user_learning_progress_v5(bigint) from authenticated;
grant execute on function public.get_user_learning_progress_v5(bigint) to service_role;

commit;
