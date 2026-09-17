"""Dependency-free release smoke test for Neta Telegram v5.

This does not contact Telegram, Supabase or Render. It validates source,
migration, UI and security invariants that must hold before deployment.
"""
from pathlib import Path
import ast
import json
import re

ROOT = Path(__file__).resolve().parents[1]

py_files = [
    ROOT / "main.py",
    ROOT / "bot" / "handlers.py",
    ROOT / "bot" / "learning_db.py",
    ROOT / "bot" / "keyboards.py",
    ROOT / "bot" / "admin.py",
    ROOT / "bot" / "db_client.py",
    ROOT / "bot" / "config.py",
]
for path in py_files:
    ast.parse(path.read_text(encoding="utf-8"), filename=str(path))

handlers = (ROOT / "bot" / "handlers.py").read_text(encoding="utf-8")
keyboards = (ROOT / "bot" / "keyboards.py").read_text(encoding="utf-8")
learning_db = (ROOT / "bot" / "learning_db.py").read_text(encoding="utf-8")
config = (ROOT / "bot" / "config.py").read_text(encoding="utf-8")
main = (ROOT / "main.py").read_text(encoding="utf-8")
admin = (ROOT / "bot" / "admin.py").read_text(encoding="utf-8")
migration_v4 = (ROOT / "migrations" / "2026_09_15_learning_v4.sql").read_text(encoding="utf-8")
migration_v5 = (ROOT / "migrations" / "2026_09_15_learning_v5.sql").read_text(encoding="utf-8")
migration = migration_v4

# Product flow / polished UI.
for token in [
    "start_intro", "start_today", "start_diagnostic", "show_progress",
    "show_friends", "show_course", "show_channel", "show_settings",
    "show_privacy", "course_interest", "reminder_off",
]:
    assert token in handlers or token in keyboards, token

assert "Спробувати Neta Memory · 3 питання" in keyboards
assert "Neta — 5 хвилин англійської, які підлаштовуються під тебе." in handlers
assert "Neta Memory додала цю навичку в повторення" in handlers
assert "Карта навичок · 12 питань" in keyboards
assert "Канал · розбори НМТ" in keyboards
assert "https://t.me/neta_nmt" in config
assert "buy_premium" not in keyboards.lower(), "Premium purchase CTA leaked into active UI"

# Long Telegram options must be readable in message body; answer buttons are compact.
question_text_block = handlers.split("def _question_text", 1)[1].split("async def _main_screen", 1)[0]
assert "option_lines" in question_text_block
assert 'f"<b>{letter}.</b>' in question_text_block
question_keyboard_block = keyboards.split("def get_question_keyboard", 1)[1].split("def get_intro_result_keyboard", 1)[0]
assert 'text=row[0]' in question_keyboard_block and 'text=row[2]' in question_keyboard_block
assert "options.get" not in question_keyboard_block
assert "nmt_task_type" not in question_text_block, "Technical Task labels should not leak into learner UI"

# Honest positioning.
assert "не оцінка рівня" in handlers
assert "не офіційний рівень англійської чи прогноз бала НМТ" in handlers

# Persistence and idempotency are DB-backed.
for token in [
    "learning_sessions", "learning_session_answers", "unique(session_id, question_index)",
    "record_learning_answer", "on conflict (session_id, question_index) do nothing",
    "question does not match session position", "unexpected question order",
]:
    assert token.lower() in migration.lower(), token
assert "v_actual_correct := p_selected_index = v_correct_option" in migration

# Daily streak is earned only after completed Daily and once per Kyiv date.
assert "elsif v_session.session_type = 'daily'" in migration.lower()
assert "last_streak_date = v_today" in migration.lower()
assert "get_streak" in learning_db
assert "Серія:" in handlers

# Scalable question selection.
assert "select_learning_questions" in migration
assert 'supabase.rpc("select_learning_questions"' in learning_db
session_block = learning_db.split("async def get_or_create_session", 1)[1].split("async def get_questions", 1)[0]
assert ".limit(1000)" not in session_block

# Curated intro content.
pack = json.loads((ROOT / "content" / "nmt_2026_pack_v1_7.json").read_text(encoding="utf-8"))
codes = {str(q.get("question_code")) for q in pack}
for code in ("N17-T2-004", "N17-T5-007", "N17-T6-002"):
    assert code in codes, code
    assert code in migration, code

# Old-user compatibility / data preservation.
for token in ["onboarding_completed", "diagnostic_completed_at", "total_tasks_solved", "total_questions_answered", "first_lesson_completed_at"]:
    assert token in migration, token
assert "ensure_learning_start_context" in migration
assert "Existing users who already used the old product" in migration

# Privacy / leaderboard.
safe_alias_block = learning_db.split("def safe_alias", 1)[1].split("class LearningDB", 1)[0]
assert "first_name" not in safe_alias_block.split("return", 1)[1]
assert "username" not in safe_alias_block.split("return", 1)[1]
assert "str(uid)[-3:]" not in learning_db
assert "public_alias = null" in migration
assert "Telegram ID" in handlers and "школу, місто" in handlers

# Reminder safety.
assert "TelegramForbiddenError" in handlers
assert "set_user_inactive" in handlers
assert "get_learning_reminder_candidates" in migration
assert 'supabase.rpc("get_learning_reminder_candidates"' in learning_db

# Security: Telegram signed webhook + no hardcoded manager account + backend-only RPCs.
assert "WEBHOOK_SECRET" in config and "sha256" in config
assert "secret_token=WEBHOOK_SECRET" in main
assert 'os.getenv("MANAGER_USERNAME", "")' in config
for rpc in [
    "ensure_learning_start_context", "select_learning_questions", "record_learning_answer",
    "activate_learning_referral", "get_learning_reminder_candidates",
    "get_weekly_learning_leaderboard", "get_learning_admin_report", "get_question_bank_audit",
]:
    assert rpc in migration
assert "grant execute on function %s to service_role" in migration.lower()
assert "revoke all on table public.users from anon, authenticated" in migration.lower()
assert "alter table public.questions enable row level security" in migration.lower()
assert "SUPABASE_SERVICE_ROLE_KEY" in config

# Analytics / observability.
for token in [
    "value_proposition_shown", "first_lesson_started", "first_lesson_completed",
    "diagnostic_started", "diagnostic_completed", "question_shown", "question_answered",
    "daily_lesson_completed", "course_view", "course_interest", "channel_view",
    "referral_visit", "referral_activated", "answer_handler_ms", "process_to_first_webhook_ms",
]:
    assert token in handlers or token in main or token in admin, token

# Leaderboard bounded to one point/day and opt-in only.
assert "leaderboard_points integer not null default 0 check (leaderboard_points between 0 and 1)" in migration.lower()
assert "leaderboard_opt_in" in learning_db
assert "get_weekly_learning_leaderboard" in migration

# Admin router precedence + guard.
assert main.index("dp.include_router(\n    admin_router") < main.index("dp.include_router(\n    main_router")
assert "def _is_admin" in admin

# No obvious secret values committed. Placeholders are allowed.
secret_patterns = [
    re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b"),  # Telegram bot token
    re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b"),  # JWT
    re.compile(r"\bsb_secret_[A-Za-z0-9_-]{20,}\b"),
]
for path in ROOT.rglob("*"):
    if not path.is_file() or ".git" in path.parts or path.suffix in {".zip", ".jpg", ".jpeg", ".png", ".pyc"}:
        continue
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        continue
    for pattern in secret_patterns:
        assert not pattern.search(text), f"Possible secret in {path}"

# PostgreSQL function body delimiters should remain paired. DO blocks add one $$;
# without an `as $$`, so account for those explicitly.
do_blocks = len(re.findall(r"\bdo\s+\$\$", migration, flags=re.I))
assert migration.count("$$;") == migration.count("as $$") + do_blocks, "Unbalanced PostgreSQL dollar-quoted bodies"

# v5: complete legacy + current history is canonical and old mistakes are backfilled.
assert 'supabase.rpc("get_user_learning_progress_v5"' in learning_db
assert "from public.user_answers ua" in migration_v5.lower()
assert "insert into public.user_topic_progress" in migration_v5.lower()
assert "on conflict (user_id, category, sub_category)" in migration_v5.lower()
assert "get_user_learning_progress_v5" in migration_v5
assert "grant execute on function public.get_user_learning_progress_v5(bigint) to service_role" in migration_v5.lower()
assert "delete from public.user_answers" not in migration_v5.lower()
assert "truncate" not in migration_v5.lower()
assert "drop table" not in migration_v5.lower()

# v5 visual/product polish.
for token in ["⚡ Daily завершено", "🧠 Neta Memory", "👥 Друзі · цей тиждень", "🎓 Neta School"]:
    assert token in handlers, token
assert "Твоє посилання:\n<code>" not in handlers
assert "🧠 Мій прогрес" in keyboards
assert "📣 Канал · розбори НМТ" in keyboards

# Validate the incremental migration dollar quotes too.
do_blocks_v5 = len(re.findall(r"\bdo\s+\$\$", migration_v5, flags=re.I))
assert migration_v5.count("$$;") == migration_v5.count("as $$") + do_blocks_v5

print("SMOKE_V5_OK: history continuity, product UI, security and v4 invariants passed")
