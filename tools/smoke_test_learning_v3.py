"""Dependency-free release smoke test for Neta learning flow v3.

This does not contact Telegram, Supabase or Render. It validates source,
migration and content invariants that must hold before deployment.
"""
from pathlib import Path
import ast
import json

ROOT = Path(__file__).resolve().parents[1]

py_files = [
    ROOT / "main.py",
    ROOT / "bot" / "handlers.py",
    ROOT / "bot" / "learning_db.py",
    ROOT / "bot" / "keyboards.py",
    ROOT / "bot" / "admin.py",
    ROOT / "bot" / "db_client.py",
]
for path in py_files:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

handlers = (ROOT / "bot" / "handlers.py").read_text(encoding="utf-8")
keyboards = (ROOT / "bot" / "keyboards.py").read_text(encoding="utf-8")
learning_db = (ROOT / "bot" / "learning_db.py").read_text(encoding="utf-8")
main = (ROOT / "main.py").read_text(encoding="utf-8")
admin = (ROOT / "bot" / "admin.py").read_text(encoding="utf-8")
migration = (ROOT / "migrations" / "2026_09_15_learning_v3.sql").read_text(encoding="utf-8")

# Product flow.
for token in [
    "start_intro", "start_today", "start_diagnostic", "show_progress",
    "show_friends", "show_course", "show_channel", "show_settings",
    "course_interest", "reminder_off",
]:
    assert token in handlers or token in keyboards, token

assert "Побачити Neta в дії · 3 питання" in keyboards
assert "Neta — не просто збірник тестів" in handlers
assert "запам’ятала цю помилку" in handlers
assert "Карта навичок · 12 питань" in keyboards
assert "Канал Neta" in keyboards
assert "https://t.me/neta_nmt" in (ROOT / "bot" / "config.py").read_text(encoding="utf-8")
assert "buy_premium" not in keyboards.lower(), "Premium purchase CTA leaked into active UI"

# Honest positioning: short sessions are not presented as a reliable NMT score/level.
assert "не прогноз бала НМТ" in handlers
assert "не достовірний рівень англійської" in handlers

# Persistence and idempotency are DB-backed.
for token in [
    "learning_sessions", "learning_session_answers", "unique(session_id, question_index)",
    "record_learning_answer", "on conflict (session_id, question_index) do nothing",
    "question does not match session position", "unexpected question order",
]:
    assert token.lower() in migration.lower(), token

# The DB calculates correctness from questions.correct_option instead of trusting the client.
assert "v_actual_correct := p_selected_index = v_correct_option" in migration

# Scalable bank selection: selector lives in PostgreSQL and app no longer loads 1000 questions to choose 3–5.
assert "select_learning_questions" in migration
assert 'supabase.rpc("select_learning_questions"' in learning_db
session_block = learning_db.split("async def get_or_create_session", 1)[1].split("async def get_questions", 1)[0]
assert ".limit(1000)" not in session_block

# Curated intro codes are bundled; migration can still fall back if a DB missed the pack.
pack = json.loads((ROOT / "content" / "nmt_2026_pack_v1_7.json").read_text(encoding="utf-8"))
codes = {str(q.get("question_code")) for q in pack}
for code in ("N17-T2-004", "N17-T5-007", "N17-T6-002"):
    assert code in codes, code
    assert code in migration, code

# Old users retain access to the product without being forced through intro again.
for token in ["onboarding_completed", "diagnostic_completed_at", "total_tasks_solved", "total_questions_answered", "first_lesson_completed_at"]:
    assert token in migration, token
assert "ensure_learning_start_context" in migration
assert "Existing users who already used the old product" in migration

# Progress preserves legacy data. Topic mastery is updated atomically inside
# record_learning_answer so two fast answers cannot lose an increment.
for token in ["user_topic_progress", "total_questions_answered", "user_answers", "learning_days"]:
    assert token in learning_db, token
assert "insert into public.user_topic_progress" in migration.lower()
assert "on conflict (user_id, category, sub_category) do update" in migration.lower()
assert "DBClient.update_topic_progress" not in handlers

# Privacy: public alias is generated from a hash, not from Telegram profile data or ID fragments.
safe_alias_block = learning_db.split("def safe_alias", 1)[1].split("class LearningDB", 1)[0]
assert "first_name" not in safe_alias_block.split("return", 1)[1]
assert "username" not in safe_alias_block.split("return", 1)[1]
assert "str(uid)[-3:]" not in learning_db
assert "public_alias = null" in migration

# Reminder safety and scale.
assert "TelegramForbiddenError" in handlers
assert "set_user_inactive" in handlers
assert "reminder_enabled" in migration
assert "get_learning_reminder_candidates" in migration
assert 'supabase.rpc("get_learning_reminder_candidates"' in learning_db
assert "session_type = 'daily'" in migration and "status = 'completed'" in migration

# Analytics / observability.
for token in [
    "value_proposition_shown", "first_lesson_started", "first_lesson_completed",
    "diagnostic_started", "diagnostic_completed", "question_shown", "question_answered",
    "daily_lesson_completed", "course_view", "course_interest", "channel_view",
    "referral_visit", "referral_activated", "answer_handler_ms",
    "process_to_first_webhook_ms",
]:
    assert token in handlers or token in main or token in admin, token

# Business analytics and referral activation aggregate atomically in PostgreSQL.
for token in ["get_learning_admin_report", "get_question_bank_audit", "activate_learning_referral"]:
    assert token in migration, token
    assert token in learning_db, token
assert "make_interval" in migration

# Any answer counts as learning activity for retention; leaderboard stays completion-based.
assert "values (p_user_id, v_session.learning_date, 1, 0, 0)" in migration
assert "values (p_user_id, v_today, 0, 1, 1)" in migration

# Leaderboard bounded to 1 point/day, opt-in only, and DB-side aggregated.
assert "leaderboard_points integer not null default 0 check (leaderboard_points between 0 and 1)" in migration.lower()
assert "leaderboard_opt_in" in learning_db
assert "get_weekly_learning_leaderboard" in migration
assert 'supabase.rpc("get_weekly_learning_leaderboard"' in learning_db

# Router order protects admin handlers from generic main routing.
assert main.index("dp.include_router(\n    admin_router") < main.index("dp.include_router(\n    main_router")
assert "def _is_admin" in admin

# Migration function bodies should be paired.
assert migration.count("$$;") == migration.count("as $$"), "Unbalanced PostgreSQL function bodies"

print("SMOKE_V3_OK: source, product and migration invariants passed")
