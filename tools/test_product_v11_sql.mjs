import fs from 'node:fs';
import assert from 'node:assert/strict';
const {PGlite}=await import(process.env.PGLITE_MODULE||'@electric-sql/pglite');
const db=new PGlite();
const q=async(s,p=[])=>(await db.query(s,p)).rows;
const one=async(s,p=[])=>(await q(s,p))[0];
await db.exec('create role anon; create role authenticated; create role service_role;');
await db.exec(fs.readFileSync(new URL('./fixtures/schema_v11.sql',import.meta.url),'utf8'));
await db.exec('insert into users(id,xp,level) values(1,245,1),(2,99,1),(3,0,1);');
const migration=fs.readFileSync(new URL('../migrations/2026_09_17_product_v11_ALL.sql',import.meta.url),'utf8');
await db.exec(migration);
assert.equal((await one('select level from users where id=1')).level,3);
await db.exec('update users set xp=100 where id=2');
assert.equal((await one('select level from users where id=2')).level,2);
await db.exec('update users set reminder_enabled=false,reminder_preference_set=true where id=1');
await db.exec(migration);
assert.deepEqual(await one('select xp,level,reminder_enabled from users where id=1'),{xp:245,level:3,reminder_enabled:false});
console.log('PASS supplied schema: migration twice, XP preserved, levels backfilled and updated, optout preserved');
await db.exec(`insert into questions(topic,difficulty,question_text,options,correct_option,category,sub_category,is_intro,is_diagnostic)
select 'Grammar',1+(g%3),'Test question '||g,'{"A":"yes","B":"no","C":"other","D":"none"}',0,'Use of English','Grammar: Tenses',g<=3,g>1030 from generate_series(1,1057) g;`);
assert.equal((await one('select get_admin_stats_v10() x')).x.total_questions,1057);
const context=(await one("select ensure_learning_start_context(4,'test','Test',null,'test','Alias') x")).x;
assert.equal(context.user.id,4);
async function start(type,length,key){
 const ids=(await q('select * from select_learning_questions(4,$1,$2)',[type,length])).map(r=>r.question_id);
 assert.equal(ids.length,length);
 return (await one("insert into learning_sessions(user_id,session_key,session_type,learning_date,question_ids) values(4,$1,$2,(now() at time zone 'Europe/Kyiv')::date,$3::uuid[]) returning *",[key,type,ids]));
}
async function finish(s){
 for(let i=0;i<s.question_ids.length;i++){
  const args=[s.id,4,s.question_ids[i],i,0,true];
  const r=(await one('select record_learning_answer($1,$2,$3,$4,$5,$6) x',args)).x;
  assert.equal(r.inserted,true);
  const before=await one('select xp,level,total_tasks_solved from users where id=4');
  const dup=(await one('select record_learning_answer($1,$2,$3,$4,$5,$6) x',args)).x;
  assert.equal(dup.inserted,false);
  assert.deepEqual(await one('select xp,level,total_tasks_solved from users where id=4'),before);
 }
 assert.equal((await one('select status from learning_sessions where id=$1',[s.id])).status,'completed');
}
await finish(await start('intro',3,'intro:v3'));
await finish(await start('daily',4,'daily:test'));
for(const mode of ['focus','challenge','full']){
 const s=(await one('select create_practice_session_v7(4,$1,$2) x',[mode==='full'?10:5,mode])).x;
 await finish(s);
}
await finish(await start('diagnostic',12,'diagnostic:v3'));
console.log('PASS RPC workflows: intro, Daily, 5/10 practice, diagnostic, duplicate answers');
await db.exec('update users set leaderboard_opt_in=true where id=4');
assert.equal((await one("select get_weekly_xp_leaderboard_v6(4,current_date-7,current_date+1,10) x")).x.my_rank,1);
await db.exec('update users set leaderboard_opt_in=false where id=4');
assert.equal((await one("select get_weekly_xp_leaderboard_v6(4,current_date-7,current_date+1,10) x")).x.my_rank,null);
for(const call of ["get_user_learning_progress_v6(4)","get_learning_admin_report('{}',7)","get_question_bank_audit()","get_product_funnel_v10(30)","get_admin_stats_v10()","activate_learning_referral(4)"]){
 await q(`select ${call}`);
}
const sample=(await one('select id from learning_sessions limit 1')).id;
await q('select get_session_xp_v6($1,4)',[sample]);
await q('select * from claim_learning_reminders_v10(20)');
const state=await one('select xp,level from users where id=4');
assert.equal(state.level,1+Math.floor(state.xp/100));
console.log('PASS leaderboard optin/out, progress/admin/funnel/referral/reminder RPCs, derived level after actual answers');
await db.close();
