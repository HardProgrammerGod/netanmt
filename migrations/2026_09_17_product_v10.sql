-- Neta product v10. Requires learning v4 + v7 schema. Additive, rerunnable.
begin;
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
commit;
