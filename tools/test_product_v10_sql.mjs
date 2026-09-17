// npm install --prefix /tmp/neta-sql @electric-sql/pglite
// PGLITE_MODULE=/tmp/neta-sql/node_modules/@electric-sql/pglite/dist/index.js node tools/test_product_v10_sql.mjs
import fs from 'node:fs';
import assert from 'node:assert/strict';
const {PGlite}=await import(process.env.PGLITE_MODULE || '@electric-sql/pglite');
const db=new PGlite();
const now="timestamptz '2026-09-17 16:10:00+00'"; // 19:10 Kyiv
await db.exec(`
create role anon; create role authenticated; create role service_role;
create table users(id bigint primary key,created_at timestamptz default now(),last_active_at timestamptz,
 is_active boolean default true,is_premium boolean default false,premium_until timestamptz,
 total_tasks_solved int default 0,referrals_count int default 0,is_test_account boolean default false,
 reminder_enabled boolean default false,reminder_time time,reminder_timezone text default 'Europe/Kyiv',last_reminder_at timestamptz);
create table events(id bigint generated always as identity primary key,user_id bigint,event_name text,metadata jsonb default '{}',created_at timestamptz default now());
create table questions(id bigint primary key,is_active boolean,quality_status text);
create table orders(user_id bigint,status text,currency text,amount numeric);
create table learning_sessions(id uuid default gen_random_uuid(),user_id bigint,session_type text,status text,started_at timestamptz,completed_at timestamptz,learning_date date);
create table learning_session_answers(user_id bigint);
insert into users(id,created_at) values(1,'2026-09-15'),(2,'2026-09-15'),(3,'2026-09-15');
insert into events(user_id,event_name) values(2,'reminder_disabled');
update users set reminder_enabled=true,reminder_time='17:00' where id=3;
`);
let sql=fs.readFileSync(new URL('../migrations/2026_09_17_product_v10.sql',import.meta.url),'utf8').replaceAll('now()',now);
await db.exec(sql);
let query=async s=>(await db.query(s)).rows;
let row=async s=>(await query(s))[0];
assert.equal((await row('select reminder_enabled from users where id=1')).reminder_enabled,true);
assert.equal((await row('select reminder_enabled from users where id=2')).reminder_enabled,false);
assert.equal((await row('select reminder_time from users where id=3')).reminder_time,'17:00:00');
await db.exec('update users set reminder_enabled=false,reminder_preference_set=true where id=1');
await db.exec(sql);
assert.equal((await row('select reminder_enabled from users where id=1')).reminder_enabled,false);
console.log('PASS: migration applies twice, preserves optout and chosen time');
await db.exec(`insert into questions select g,true,'approved' from generate_series(1,1507) g;
insert into orders values(1,'paid','XTR',199),(2,'pending','XTR',49),(3,'paid','UAH',350);`);
const stats=(await row('select get_admin_stats_v10() as x')).x;
assert.equal(stats.total_questions,1507); assert.equal(stats.stars_revenue,199);
console.log('PASS: exact 1507 questions, paid XTR only');
await db.exec(`insert into users(id,created_at) select g,'2026-09-15' from generate_series(10,22) g;
update users set is_active=false where id=11;
update users set reminder_enabled=false where id=12;
update users set created_at='2026-09-17' where id=13;
update users set created_at='2026-08-01' where id=14;
update users set reminder_time='21:00' where id=15;
update users set is_test_account=true where id=16;
insert into learning_sessions(user_id,session_type,status,started_at,completed_at,learning_date)
values(17,'practice','completed','2026-09-17 10:00+00','2026-09-17 10:10+00','2026-09-17');
update users set created_at='2026-09-01' where id in (18,19,20,21,22);
-- User 18/19: 3 ignored sends. 18 yesterday => blocked, 19 three days ago => allowed.
insert into learning_reminder_deliveries(user_id,learning_date,tip_index,status,sent_at)
select 18, date '2026-09-16'-g,g,'sent',timestamptz '2026-09-16 16:10+00'-g*interval '1 day' from generate_series(0,2) g;
insert into learning_reminder_deliveries(user_id,learning_date,tip_index,status,sent_at)
select 19, date '2026-09-14'-g,g,'sent',timestamptz '2026-09-14 16:10+00'-g*interval '1 day' from generate_series(0,2) g;
-- Set recent completed anchor so 14-day dormant rule doesn't take priority.
insert into learning_sessions(user_id,session_type,status,started_at,completed_at,learning_date)
select g,'daily','completed','2026-09-10','2026-09-10','2026-09-10' from generate_series(18,22) g;
insert into learning_reminder_deliveries(user_id,learning_date,tip_index,status,sent_at)
select 20, date '2026-09-16'-g,g,'sent',timestamptz '2026-09-16 16:10+00'-g*interval '1 day' from generate_series(0,4) g;
insert into learning_reminder_deliveries(user_id,learning_date,tip_index,status,sent_at)
select 21, date '2026-09-10'-g,g,'sent',timestamptz '2026-09-10 16:10+00'-g*interval '1 day' from generate_series(0,4) g;
update learning_sessions set completed_at='2026-09-01' where user_id=21;
-- 22 seven ignored => pause even if otherwise interval satisfied.
insert into learning_reminder_deliveries(user_id,learning_date,tip_index,status,sent_at)
select 22, date '2026-09-16'-g,g,'sent',timestamptz '2026-09-16 16:10+00'-g*interval '1 day' from generate_series(0,6) g;
update learning_sessions set completed_at='2026-09-09' where user_id=22;
`);
const claimed=await query('select * from claim_learning_reminders_v10(100)');
assert.deepEqual(claimed.map(x=>Number(x.user_id)).sort((a,b)=>a-b),[10,19,21]);
assert.equal((await query('select * from claim_learning_reminders_v10(100)')).length,0);
const id=claimed.find(x=>Number(x.user_id)===10).id;
assert.equal((await row(`select can_send_learning_reminder_v10('${id}') as x`)).x,true);
await db.exec('update users set reminder_enabled=false where id=10');
assert.equal((await row(`select can_send_learning_reminder_v10('${id}') as x`)).x,false);
console.log('PASS: new/inactive/optout/test/completed/time/backoff/pause filtering, duplicate claim, late optout');
await db.exec(`insert into users(id,created_at) values(30,'2026-09-10'),(31,'2026-07-01');
insert into events(user_id,event_name,created_at,metadata) values
 (30,'bot_started','2026-09-10','{"start_param":"tt_01"}'),
 (30,'bot_started','2026-09-12','{"start_param":"direct"}'),
 (31,'bot_started','2026-07-01','{}'),(31,'bot_started','2026-09-16','{}');
insert into learning_sessions(user_id,session_type,status,started_at,completed_at,learning_date) values
 (30,'daily','completed','2026-09-10','2026-09-10','2026-09-10'),
 (30,'daily','completed','2026-09-11','2026-09-11','2026-09-11');`);
const funnel=(await row('select get_product_funnel_v10(30) as x')).x;
assert.equal(funnel.starts,1); assert.equal(funnel.daily_done,1); assert.equal(funnel.sources.tt_01,1);
assert.equal(funnel.retention.d1.retained,1);
// Today (D7 for the Sept 10 cohort) is not yet a complete observation day.
assert.equal(funnel.retention.d7.retained,0);
console.log('PASS: first-ever source, no reactivation-as-acquisition, observed retention');
// Explicit enable restarts a paused user's reminder cadence.
await db.exec("update users set reminder_resume_at='2026-09-17 15:00+00' where id=22");
assert.equal((await query('select * from claim_learning_reminders_v10(100)')).some(x=>Number(x.user_id)===22),true);
// Recheck completion after claim prevents sending to someone who just studied.
await db.exec("update users set reminder_enabled=true where id=10; insert into learning_sessions(user_id,status,completed_at) values(10,'completed','2026-09-17 16:09+00')");
assert.equal((await row(`select can_send_learning_reminder_v10('${id}') as x`)).x,false);
// Deterministic nighttime run on the same schema: a fresh otherwise eligible user receives nothing.
await db.exec("insert into users(id,created_at) values(40,'2026-09-15')");
await db.exec(sql.replaceAll("2026-09-17 16:10:00+00","2026-09-17 22:10:00+00"));
assert.equal((await query('select * from claim_learning_reminders_v10(100)')).length,0);
console.log('PASS: explicit resubscribe, late completion and nighttime suppression');
await db.close();
