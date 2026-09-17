-- One transaction: original RPC definitions + v10 + levels. Run this file only.
begin;

create unique index if not exists events_event_key_uidx on public.events(event_key) where event_key is not null;
create unique index if not exists learning_sessions_user_key_v11_uidx on public.learning_sessions(user_id,session_key);
create unique index if not exists learning_session_answers_question_v11_uidx on public.learning_session_answers(session_id,question_index);
create unique index if not exists learning_sessions_one_active_per_user_uidx on public.learning_sessions(user_id) where status='active';
create unique index if not exists learning_xp_answer_question_day_uidx on public.learning_xp_events(user_id,question_id,learning_date) where event_type='answer' and question_id is not null;
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

do $$ declare r record; begin
 for r in select p.oid::regprocedure as fn from pg_proc p join pg_namespace n on n.oid=p.pronamespace
 where n.nspname='public' and p.proname=any(array['ensure_learning_start_context','select_learning_questions','record_learning_answer','activate_learning_referral','get_learning_reminder_candidates','get_weekly_learning_leaderboard','get_learning_admin_report','get_question_bank_audit','create_practice_session_v6','get_session_xp_v6','get_user_learning_progress_v6','get_weekly_xp_leaderboard_v6','select_practice_questions_v7','create_practice_session_v7']) loop
 execute format('revoke all on function %s from public, anon, authenticated',r.fn);
 execute format('grant execute on function %s to service_role',r.fn);
 end loop;
end; $$;
-- Neta product v10. Requires learning v4 + v7 schema. Additive, rerunnable.
alter table public.users
  add column if not exists reminder_preference_set boolean not null default false,
  add column if not exists reminder_resume_at timestamptz,
  add column if not exists reminder_v10_initialized boolean not null default false;
-- Recover explicit preferences before enabling previously unconfigured users.
update public.users u set reminder_preference_set = true
where not u.reminder_v10_initialized and (
  u.reminder_enabled = true or exists (
    select 1 from public.events e where e.user_id=u.id
    and e.event_name in ('reminder_disabled','reminder_enabled','reminder_skipped')
  )
);
update public.users set reminder_enabled=true, reminder_time='19:00', reminder_timezone='Europe/Kyiv'
where not reminder_v10_initialized and not reminder_preference_set and is_active=true;
update public.users set reminder_time='19:00' where reminder_enabled=true and reminder_time is null;
update public.users set reminder_v10_initialized=true where not reminder_v10_initialized;
alter table public.users alter column reminder_enabled set default true;
alter table public.users alter column reminder_time set default '19:00';
alter table public.users alter column reminder_v10_initialized set default true;

create table if not exists public.learning_reminder_deliveries (
  id uuid primary key default gen_random_uuid(),
  user_id bigint not null references public.users(id) on delete cascade,
  learning_date date not null,
  status text not null default 'claimed' check(status in ('claimed','sent','failed','blocked','skipped')),
  tip_index integer not null,
  quiet boolean not null default false,
  claimed_at timestamptz not null default now(),
  sent_at timestamptz,
  clicked_at timestamptz,
  unique(user_id,learning_date)
);
alter table public.learning_reminder_deliveries enable row level security;
revoke all on public.learning_reminder_deliveries from anon, authenticated;
grant all on public.learning_reminder_deliveries to service_role;
create index if not exists learning_reminders_user_sent_idx
  on public.learning_reminder_deliveries(user_id,sent_at desc);
create index if not exists learning_sessions_user_completed_idx
  on public.learning_sessions(user_id,completed_at desc) where status='completed';

-- Claim BEFORE Telegram delivery. A restart or second worker cannot send twice.
-- Claimed/failed/ambiguous sends are deliberately not retried the same day.
create or replace function public.claim_learning_reminders_v10(p_limit integer default 20)
returns setof public.learning_reminder_deliveries
language sql security definer set search_path=public as $$
with clock as (
  select now() as ts, (now() at time zone 'Europe/Kyiv')::date as today,
         (now() at time zone 'Europe/Kyiv')::time as local_time
), eligible as (
 select u.id, c.today, n.sent_total,
        (n.ignored >= 3 or c.today-(coalesce(greatest(s.last_done,u.reminder_resume_at),u.created_at) at time zone 'Europe/Kyiv')::date >= 7) as quiet
 from public.users u cross join clock c
 left join lateral (
   select max(completed_at) as last_done from public.learning_sessions
   where user_id=u.id and status='completed'
 ) s on true
 cross join lateral (
   select count(*) filter(where status='sent')::int as sent_total,
          count(*) filter(where status='sent' and sent_at>coalesce(greatest(s.last_done,u.reminder_resume_at),u.created_at))::int as ignored,
          max(sent_at) filter(where status='sent') as last_sent
   from public.learning_reminder_deliveries where user_id=u.id
 ) n
 where u.is_active=true and u.reminder_enabled=true and not u.is_test_account
   and u.reminder_time is not null
   and c.local_time >= '09:00'::time and c.local_time < '22:00'::time
   and c.local_time >= u.reminder_time
   and c.local_time < u.reminder_time + interval '90 minutes'
   and c.ts >= coalesce(u.created_at,c.ts) + interval '20 hours'
   and n.ignored < 7
   and c.ts-coalesce(greatest(s.last_done,u.reminder_resume_at),u.created_at,c.ts) < interval '30 days'
   and (u.last_reminder_at is null or (u.last_reminder_at at time zone 'Europe/Kyiv')::date < c.today)
   and not exists(select 1 from public.learning_sessions ls where ls.user_id=u.id
     and ls.status='completed' and (ls.completed_at at time zone 'Europe/Kyiv')::date=c.today)
   and not exists(select 1 from public.learning_reminder_deliveries d where d.user_id=u.id and d.learning_date=c.today)
   and (n.last_sent is null or c.today-(n.last_sent at time zone 'Europe/Kyiv')::date >=
       case when n.ignored>=5 or c.ts-coalesce(greatest(s.last_done,u.reminder_resume_at),u.created_at,c.ts)>=interval '14 days' then 7
            when n.ignored>=3 then 3 else 1 end)
 order by n.last_sent nulls first, u.id
 limit greatest(1,least(coalesce(p_limit,20),100))
), claimed as (
 insert into public.learning_reminder_deliveries(user_id,learning_date,tip_index,quiet)
 select id,today,sent_total,quiet from eligible
 on conflict(user_id,learning_date) do nothing returning *
) select * from claimed;
$$;

create or replace function public.can_send_learning_reminder_v10(p_id uuid)
returns boolean language sql security definer set search_path=public as $$
 select exists(select 1 from public.learning_reminder_deliveries d join public.users u on u.id=d.user_id
 where d.id=p_id and d.status='claimed' and u.is_active=true and u.reminder_enabled=true
 and d.learning_date=(now() at time zone 'Europe/Kyiv')::date
 and (now() at time zone 'Europe/Kyiv')::time < '22:00'::time
 and not exists(select 1 from public.learning_sessions s where s.user_id=u.id and s.status='completed'
   and (s.completed_at at time zone 'Europe/Kyiv')::date=d.learning_date));
$$;

create or replace function public.get_admin_stats_v10()
returns jsonb language sql stable security definer set search_path=public as $$
select jsonb_build_object(
 'total_users',count(*), 'active_users',count(*) filter(where is_active=true),
 'blocked_users',count(*) filter(where is_active is not true),
 'learners_started',count(*) filter(where total_tasks_solved>0 or exists(select 1 from public.learning_session_answers a where a.user_id=u.id)),
 'active_7d',count(*) filter(where last_active_at>=now()-interval '7 days'),
 'premium_users',count(*) filter(where is_premium=true and (premium_until is null or premium_until>now())),
 'total_referrals',coalesce(sum(referrals_count),0),
 'total_questions',(select count(*) from public.questions),
 'active_questions',(select count(*) from public.questions where is_active=true and quality_status='approved'),
 'daily_users',(select count(*) from (select user_id from public.learning_sessions where session_type='daily' and status='completed'
   union select user_id from public.events where event_name='daily_completed') d),
 'referral_starts',(select count(distinct user_id) from public.events where event_name in ('referral_joined','referral_visit')),
 'paying_users',(select count(distinct user_id) from public.orders where status='paid' and currency='XTR'),
 'stars_revenue',(select coalesce(sum(amount),0) from public.orders where status='paid' and currency='XTR')
) from public.users u;
$$;

create or replace function public.get_product_funnel_v10(p_days integer default 30)
returns jsonb language sql stable security definer set search_path=public as $$
with bounds as (
 select now()-make_interval(days=>greatest(1,least(p_days,90))) as since,
 (now() at time zone 'Europe/Kyiv')::date as today
), starts as (
 -- FIRST recorded start, not first start inside a moving window.
 select distinct on(e.user_id) e.user_id,e.created_at,coalesce(e.metadata->>'start_param','direct') as source
 from public.events e join public.users u on u.id=e.user_id
 where e.event_name='bot_started' and not u.is_test_account
 order by e.user_id,e.created_at,e.id
), cohort as (
 select s.* from starts s,bounds b where s.created_at>=b.since
), stages as (
 select c.user_id,
 exists(select 1 from public.learning_sessions s where s.user_id=c.user_id and s.session_type='intro' and s.started_at>=c.created_at) as intro_start,
 exists(select 1 from public.learning_sessions s where s.user_id=c.user_id and s.session_type='intro' and s.status='completed' and s.completed_at>=c.created_at) as intro_done,
 exists(select 1 from public.learning_sessions s where s.user_id=c.user_id and s.session_type='daily' and s.started_at>=c.created_at) as daily_start,
 exists(select 1 from public.learning_sessions s where s.user_id=c.user_id and s.session_type='daily' and s.status='completed' and s.completed_at>=c.created_at) as daily_done,
 exists(select 1 from public.learning_sessions s where s.user_id=c.user_id and s.session_type='practice' and s.status='completed' and s.completed_at>=c.created_at) as practice_done,
 exists(select 1 from public.events e where e.user_id=c.user_id and e.event_name='course_view' and e.created_at>=c.created_at) as course_view,
 exists(select 1 from public.events e where e.user_id=c.user_id and e.event_name='course_interest' and e.created_at>=c.created_at) as course_interest
 from cohort c
), daily_days as (
 select distinct s.user_id,(s.completed_at at time zone 'Europe/Kyiv')::date as day
 from public.learning_sessions s join public.users u on u.id=s.user_id
 where s.session_type='daily' and s.status='completed' and not u.is_test_account
), first_daily as (
 select user_id,min(day) as day from daily_days group by user_id
), retention as (
 select n, count(*) filter(where f.day+n < b.today) as eligible,
 count(*) filter(where f.day+n < b.today and exists(select 1 from daily_days d where d.user_id=f.user_id and d.day=f.day+n)) as retained
 from (values(1),(3),(7)) ns(n) cross join bounds b
 left join first_daily f on f.day >= (b.since at time zone 'Europe/Kyiv')::date
 group by n
), delivery as (
 select d.* from public.learning_reminder_deliveries d,bounds b where d.claimed_at>=b.since
)
select jsonb_build_object(
 'starts',(select count(*) from cohort),
 'intro_start',(select count(*) from stages where intro_start),
 'intro_done',(select count(*) from stages where intro_done),
 'daily_start',(select count(*) from stages where daily_start),
 'daily_done',(select count(*) from stages where daily_done),
 'practice_done',(select count(*) from stages where practice_done),
 'course_view',(select count(*) from stages where course_view),
 'course_interest',(select count(*) from stages where course_interest),
 'sources',(select coalesce(jsonb_object_agg(source,n),'{}'::jsonb) from (select source,count(*) n from cohort group by source) x),
 'retention',(select jsonb_object_agg('d'||n,jsonb_build_object('eligible',eligible,'retained',retained)) from retention),
 'reminders_sent',(select count(*) from delivery where status='sent'),
 'reminders_clicked',(select count(*) from delivery where status='sent' and clicked_at is not null),
 'reminders_failed',(select count(*) from delivery where status in ('failed','blocked')),
 'reminders_unknown',(select count(*) from delivery where status='claimed' and claimed_at < now()-interval '10 minutes'),
 'reminders_returned',(select count(*) from delivery d where status='sent' and exists(
   select 1 from public.learning_sessions s where s.user_id=d.user_id and s.status='completed'
   and s.completed_at>=d.sent_at and s.completed_at<d.sent_at+interval '24 hours')),
 'disabled',(select count(distinct e.user_id) from public.events e,bounds b where e.event_name='reminder_disabled' and e.created_at>=b.since)
);
$$;

revoke all on function public.claim_learning_reminders_v10(integer) from public,anon,authenticated;
revoke all on function public.can_send_learning_reminder_v10(uuid) from public,anon,authenticated;
revoke all on function public.get_admin_stats_v10() from public,anon,authenticated;
revoke all on function public.get_product_funnel_v10(integer) from public,anon,authenticated;
grant execute on function public.claim_learning_reminders_v10(integer) to service_role;
grant execute on function public.can_send_learning_reminder_v10(uuid) to service_role;
grant execute on function public.get_admin_stats_v10() to service_role;
grant execute on function public.get_product_funnel_v10(integer) to service_role;

create or replace function public.sync_learning_level_v11()
returns trigger language plpgsql set search_path=public as $$
begin
 new.level := 1 + greatest(coalesce(new.xp,0),0) / 100;
 return new;
end;
$$;
drop trigger if exists users_learning_level_v11 on public.users;
create trigger users_learning_level_v11 before insert or update of xp,level on public.users
for each row execute function public.sync_learning_level_v11();
-- Preserve all earned XP. Correct the derived level only.
update public.users set level=1+greatest(coalesce(xp,0),0)/100
where level is distinct from 1+greatest(coalesce(xp,0),0)/100;
revoke all on function public.sync_learning_level_v11() from public,anon,authenticated;

commit;
