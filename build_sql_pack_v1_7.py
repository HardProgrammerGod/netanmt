from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT / "content" / "nmt_2026_pack_v1_7.json"
OUT = ROOT / "supabase_v1_7_content_pack4.sql"


def q(value):
    if value is None:
        return "NULL"
    if isinstance(value, bool):
        return "TRUE" if value else "FALSE"
    if isinstance(value, int):
        return str(value)
    return "'" + str(value).replace("'", "''") + "'"


data = json.loads(PACK.read_text(encoding="utf-8"))
rows = []
for item in data:
    options = json.dumps(item["options"], ensure_ascii=False, separators=(",", ":"))
    values = [
        item["question_code"],
        item["topic"],
        item["difficulty"],
        item["question_text"],
        options,
        item["correct_option"],
        item["explanation"],
        item["category"],
        item["sub_category"],
        item["section"],
        item["is_active"],
        item["is_diagnostic"],
        item["nmt_task_type"],
        item["content_pack"],
        item["quality_status"],
    ]
    rendered = [q(v) for v in values]
    # Options needs a jsonb cast.
    rendered[4] += "::jsonb"
    rows.append("    (" + ", ".join(rendered) + ")")

sql = f"""-- Neta NMT v1.7 Content Pack #4\n-- 120 original practice questions, 20 for each Task 1-6.\n-- Idempotent: rows with an existing question_code are skipped.\n\nWITH new_questions (\n    question_code, topic, difficulty, question_text, options, correct_option,\n    explanation, category, sub_category, section, is_active, is_diagnostic,\n    nmt_task_type, content_pack, quality_status\n) AS (\n{',\n'.join(rows)}\n)\nINSERT INTO public.questions (\n    question_code, topic, difficulty, question_text, options, correct_option,\n    explanation, category, sub_category, section, is_active, is_diagnostic,\n    nmt_task_type, content_pack, quality_status\n)\nSELECT\n    n.question_code, n.topic, n.difficulty, n.question_text, n.options, n.correct_option,\n    n.explanation, n.category, n.sub_category, n.section, n.is_active, n.is_diagnostic,\n    n.nmt_task_type, n.content_pack, n.quality_status\nFROM new_questions n\nWHERE NOT EXISTS (\n    SELECT 1\n    FROM public.questions q\n    WHERE q.question_code = n.question_code\n);\n\n-- Verification\nSELECT nmt_task_type, COUNT(*) AS questions\nFROM public.questions\nWHERE content_pack = 'v1.7-nmt2026-pack4'\nGROUP BY nmt_task_type\nORDER BY nmt_task_type;\n\nSELECT COUNT(*) AS total_pack4_questions\nFROM public.questions\nWHERE content_pack = 'v1.7-nmt2026-pack4';\n"""
OUT.write_text(sql, encoding="utf-8")
print(OUT, len(data))
