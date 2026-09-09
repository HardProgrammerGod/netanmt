from __future__ import annotations

import json
import sys
from collections import Counter
from pathlib import Path


def main(path: str) -> int:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    errors = []
    seen = set()
    for i, q in enumerate(data, start=1):
        code = q.get("question_code")
        if not code or code in seen:
            errors.append(f"#{i}: missing/duplicate question_code: {code!r}")
        seen.add(code)
        options = q.get("options") or {}
        if set(options.keys()) != {"A", "B", "C", "D"}:
            errors.append(f"{code}: options must contain A-D")
        if q.get("correct_option") not in {0, 1, 2, 3}:
            errors.append(f"{code}: invalid correct_option")
        if q.get("difficulty") not in {1, 2, 3}:
            errors.append(f"{code}: difficulty must be 1..3")
        if q.get("category") not in {"Reading", "Use of English"}:
            errors.append(f"{code}: invalid category")
        if q.get("nmt_task_type") not in {f"Task {n}" for n in range(1, 7)}:
            errors.append(f"{code}: invalid nmt_task_type")
        if not str(q.get("question_text") or "").strip():
            errors.append(f"{code}: empty question_text")
        if not str(q.get("explanation") or "").strip():
            errors.append(f"{code}: empty explanation")

    if errors:
        print("CONTENT VALIDATION FAILED")
        for error in errors:
            print(" -", error)
        return 1

    print(f"OK: {len(data)} questions")
    print("Tasks:", dict(sorted(Counter(q["nmt_task_type"] for q in data).items())))
    print("Categories:", dict(Counter(q["category"] for q in data)))
    print("Difficulty:", dict(sorted(Counter(q["difficulty"] for q in data).items())))
    print("Correct positions:", dict(sorted(Counter(q["correct_option"] for q in data).items())))
    return 0


if __name__ == "__main__":
    target = sys.argv[1] if len(sys.argv) > 1 else "content/nmt_2026_pack_v1_4.json"
    raise SystemExit(main(target))
