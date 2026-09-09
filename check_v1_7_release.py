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

    # Detect exact duplicate question texts/codes across all shipped packs.
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
                errors.append(f"Exact duplicate question text: {seen_texts[text]} and {path.name} ({code})")
            elif text:
                seen_texts[text] = f"{path.name} ({code})"

    sql = SQL.read_text(encoding="utf-8")
    codes_in_sql = {q["question_code"] for q in pack if q["question_code"] in sql}
    if len(codes_in_sql) != 120:
        errors.append(f"SQL does not contain all pack codes: {len(codes_in_sql)}/120")

    for path in [ROOT / "main.py", ROOT / "server.py", *(ROOT / "bot").glob("*.py")]:
        try:
            py_compile.compile(str(path), doraise=True)
        except py_compile.PyCompileError as exc:
            errors.append(str(exc))

    handlers = (ROOT / "bot" / "handlers.py").read_text(encoding="utf-8")
    admin = (ROOT / "bot" / "admin.py").read_text(encoding="utf-8")
    keyboards = (ROOT / "bot" / "keyboards.py").read_text(encoding="utf-8")
    required_markers = {
        "handlers.py": ["referral_joined", "referral_reward_granted", "+3 дні Premium"],
        "admin.py": ["Активованих рефералів", "Реферальна петля", "Розв'язали ≥1 завдання"],
        "keyboards.py": ["+3 дні Premium за друга", "Кинути виклик другу · +3 дні Premium"],
    }
    sources = {"handlers.py": handlers, "admin.py": admin, "keyboards.py": keyboards}
    for name, markers in required_markers.items():
        for marker in markers:
            if marker not in sources[name]:
                errors.append(f"Missing marker in {name}: {marker}")

    if errors:
        print("V1.7 RELEASE CHECK FAILED")
        for error in errors:
            print(" -", error)
        return 1

    print("V1.7 RELEASE CHECK OK")
    print("Content Pack #4: 120 unique questions")
    print("Task distribution:", dict(task_counts))
    print("Correct positions:", dict(correct_counts))
    print("Referral growth loop: markers present")
    print("Python compilation: OK")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
