"""Release gate for Neta Telegram v7."""
from pathlib import Path
import ast, json, re

ROOT=Path(__file__).resolve().parents[1]
handlers=(ROOT/"bot/handlers.py").read_text(encoding="utf-8")
keyboards=(ROOT/"bot/keyboards.py").read_text(encoding="utf-8")
learning=(ROOT/"bot/learning_db.py").read_text(encoding="utf-8")
sql=(ROOT/"migrations/2026_09_15_learning_v7.sql").read_text(encoding="utf-8")
base_sql=(ROOT/"migrations/2026_09_15_learning_v4.sql").read_text(encoding="utf-8")
schema_sql=base_sql + "\n" + sql

for path in [ROOT/"main.py",ROOT/"bot/handlers.py",ROOT/"bot/keyboards.py",ROOT/"bot/learning_db.py",ROOT/"bot/admin.py",ROOT/"bot/config.py"]:
    ast.parse(path.read_text(encoding="utf-8"),filename=str(path))

# Benefit-first post-Daily CTAs.
for token in [
    "🧠 Закріпити помилки · 5",
    "🚀 Підвищити складність · 5",
    "🔥 Повне тренування · 10",
    "🏠 Завершити",
]:
    assert token in keyboards, token
assert "🧠 Ще 5" not in keyboards
assert "🔥 Ще 10" not in keyboards
assert "✓ Daily виконано" not in keyboards

# Main screen continues learning after Daily.
assert "Daily завершено" in handlers
assert "Можеш закріпити їх зараз" in handlers
assert "Можеш підняти складність зараз" in handlers
assert "had_daily_errors" in keyboards

# Semantic practice modes are real, not cosmetic labels.
for mode in ["focus","challenge","full"]:
    assert mode in learning and mode in sql
assert "create_practice_session_v7" in learning
assert "select_practice_questions_v7" in sql
assert "where l.is_correct = false" in sql.lower()
assert "coalesce(q.difficulty, 1) >= 2" in sql.lower()

# Ranking naming/copy.
assert "🏆 Рейтинг" in keyboards
assert "👥 Друзі" not in keyboards
assert "🏆 Рейтинг тижня" in handlers
assert "Заробляй XP за правильні відповіді, Daily та повторення помилок" in handlers
assert "максимум 1 бал" not in handlers.lower()
assert "Вийти з рейтингу" not in keyboards.split("def get_friends_keyboard",1)[1].split("def build_referral_share_url",1)[0]
assert "Вийти з рейтингу" in keyboards.split("def get_settings_keyboard",1)[1].split("def get_privacy_keyboard",1)[0]

# Compact progress.
for token in ["🧠 Мій прогрес","📚 Навчальних днів","🔥 Серія","🎯 Точність","✍️ Виконано завдань","Сильні теми","Варто повторити","🎯 Пройти карту навичок","🧠 Тренувати слабкі теми"]:
    assert token in handlers or token in keyboards, token
progress=handlers.split('@router.callback_query(F.data == "show_progress")',1)[1].split('@router.callback_query(F.data == "show_friends")',1)[0]
assert "без прогнозу бала" not in progress.lower()

# Learner-facing course waitlist.
for token in ["🎓 Neta School","🔔 Повідомити про запуск","списку раннього доступу","програму, ціну та старт"]:
    assert token in handlers or token in keyboards, token
for banned in ["Курс ще готується","зараз не продається","лише сигнал","Мені цікаво"]:
    assert banned not in handlers and banned not in keyboards, banned

# Persistence and anti-duplication inherited in the one-file migration.
for token in [
    "unique(session_id, question_index)",
    "on conflict (session_id, question_index) do nothing",
    "learning_xp_answer_question_day_uidx",
    "learning_sessions_one_active_per_user_uidx",
    "get_user_learning_progress_v6",
]:
    assert token.lower() in schema_sql.lower(), token
for destructive in [
    "delete from public.users","delete from public.user_answers","delete from public.orders",
    "truncate table public.users","truncate table public.user_answers","truncate table public.orders",
    "drop table public.users","drop table public.user_answers","drop table public.orders",
]:
    assert destructive not in sql.lower(), destructive

# Security.
config=(ROOT/"bot/config.py").read_text(encoding="utf-8")
main=(ROOT/"main.py").read_text(encoding="utf-8")
assert "SUPABASE_SERVICE_ROLE_KEY" in config
assert "WEBHOOK_SECRET" in config
assert "secret_token=WEBHOOK_SECRET" in main
for rpc in ["select_practice_questions_v7","create_practice_session_v7"]:
    assert f"revoke all on function public.{rpc}" in sql.lower()
    assert f"grant execute on function public.{rpc}" in sql.lower()

# Content bank unchanged.
pack=json.loads((ROOT/"content/nmt_2026_pack_v1_7.json").read_text(encoding="utf-8"))
assert len(pack) >= 120

# No obvious secrets.
patterns=[
    re.compile(r"\b\d{8,10}:[A-Za-z0-9_-]{30,}\b"),
    re.compile(r"\beyJ[A-Za-z0-9_-]{20,}\.eyJ[A-Za-z0-9_-]{20,}\.[A-Za-z0-9_-]{20,}\b"),
    re.compile(r"\bsb_secret_[A-Za-z0-9_-]{20,}\b"),
]
for path in ROOT.rglob("*"):
    if not path.is_file() or "__pycache__" in path.parts or path.suffix in {".pyc",".zip",".png",".jpg",".jpeg"}:
        continue
    try: text=path.read_text(encoding="utf-8")
    except UnicodeDecodeError: continue
    for pattern in patterns:
        assert not pattern.search(text), f"Possible secret in {path}"

print("SMOKE_V7_OK: benefit-first CTA, semantic practice, ranking, progress, course, history and security invariants passed")
