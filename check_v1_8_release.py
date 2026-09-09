from __future__ import annotations

import json
import py_compile
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "content" / "nmt_2026_pack_v1_7.json"
SQL = ROOT / "supabase_v1_7_content_pack4.sql"


def main() -> int:
    errors: list[str] = []
    pack = json.loads(PACK.read_text(encoding="utf-8"))

    if len(pack) != 120:
        errors.append(f"Pack size must be 120, got {len(pack)}")
    task_counts = Counter(q.get("nmt_task_type") for q in pack)
    expected = {f"Task {i}": 20 for i in range(1, 7)}
    if dict(task_counts) != expected:
        errors.append(f"Task distribution mismatch: {dict(task_counts)}")
    correct_counts = Counter(q.get("correct_option") for q in pack)
    if dict(correct_counts) != {0: 30, 1: 30, 2: 30, 3: 30}:
        errors.append(f"Correct-position balance mismatch: {dict(correct_counts)}")

    # Every question must remain Telegram-friendly A-D single choice.
    for q in pack:
        options = q.get("options") or {}
        if set(options) != {"A", "B", "C", "D"}:
            errors.append(f"Non A-D question: {q.get('question_code')}")
        if str(q.get("sub_category") or "").startswith("Matching:"):
            errors.append(f"Matching UI label remains: {q.get('question_code')}")

    # Unique codes/texts across all shipped packs.
    seen_codes: dict[str, str] = {}
    seen_texts: dict[str, str] = {}
    for path in sorted((ROOT / "content").glob("nmt_2026_pack_v1_*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for q in data:
            code = str(q.get("question_code") or "")
            text = " ".join(str(q.get("question_text") or "").lower().split())
            if code in seen_codes:
                errors.append(f"Duplicate question_code {code}: {seen_codes[code]} and {path.name}")
            else:
                seen_codes[code] = path.name
            if text and text in seen_texts:
                errors.append(f"Exact duplicate text: {seen_texts[text]} and {path.name} ({code})")
            elif text:
                seen_texts[text] = f"{path.name} ({code})"

    sql = SQL.read_text(encoding="utf-8")
    if "Matching: Notices" in sql or "Matching: Situations" in sql:
        errors.append("Old Matching subcategory names remain in SQL")
    codes_in_sql = {q["question_code"] for q in pack if q["question_code"] in sql}
    if len(codes_in_sql) != 120:
        errors.append(f"SQL does not contain all pack codes: {len(codes_in_sql)}/120")

    for path in [ROOT / "main.py", ROOT / "server.py", *(ROOT / "bot").glob("*.py")]:
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(str(exc))

    handlers = (ROOT / "bot" / "handlers.py").read_text(encoding="utf-8")
    db = (ROOT / "bot" / "db_client.py").read_text(encoding="utf-8")
    keyboards = (ROOT / "bot" / "keyboards.py").read_text(encoding="utf-8")
    admin = (ROOT / "bot" / "admin.py").read_text(encoding="utf-8")
    config = (ROOT / "bot" / "config.py").read_text(encoding="utf-8")

    required = {
        "handlers.py": ["start_daily", "daily_completed", "NMT Practice 32", "get_daily_reminder_keyboard"],
        "db_client.py": ["get_daily_tasks", "complete_daily_session", 'ZoneInfo("Europe/Kyiv")', 'len(daily_dates) < 2'],
        "keyboards.py": ["⚡ Сьогодні · 3 хв", "••• Ще", "get_daily_result_keyboard"],
        "admin.py": ["Daily retention", "D1:", "D3:", "D7:", "Виручка Stars"],
        "config.py": ["FREE_DAILY_QUIZ_LIMIT: int = 1", "REFERRAL_INVITEE_PREMIUM_DAYS: int = 1"],
    }
    sources = {
        "handlers.py": handlers,
        "db_client.py": db,
        "keyboards.py": keyboards,
        "admin.py": admin,
        "config.py": config,
    }
    for name, markers in required.items():
        for marker in markers:
            if marker not in sources[name]:
                errors.append(f"Missing marker in {name}: {marker}")

    # Product honesty / no stale v1.7 claims.
    stale = [
        "Повна симуляція",
        "Симуляцію НМТ завершено",
        "Твій streak чекає",
        "Streak продовжено",
        "усі 3 Free-тести",
    ]
    for marker in stale:
        if marker in handlers or marker in keyboards:
            errors.append(f"Stale v1.7 UX remains: {marker}")

    # Main keyboard must not expose referral/channel/Premium as first-class home actions.
    main_slice = keyboards[keyboards.index("def get_main_keyboard"):keyboards.index("def get_more_keyboard")]
    for forbidden in ("show_referral", "show_tariffs", "CHANNEL_URL"):
        if forbidden in main_slice:
            errors.append(f"Home menu is cluttered by: {forbidden}")

    if errors:
        print("V1.8 RELEASE CHECK FAILED")
        for error in errors:
            print(" -", error)
        return 1

    print("V1.8 RELEASE CHECK OK")
    print("Content Pack #4: 120 A-D questions")
    print("Task groups:", dict(task_counts))
    print("Correct positions:", dict(correct_counts))
    print("Daily Core / streak / referral / retention markers: OK")
    print("Python compilation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
