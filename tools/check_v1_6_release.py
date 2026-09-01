from __future__ import annotations
import json
from collections import Counter
from pathlib import Path
import py_compile

ROOT = Path(__file__).resolve().parents[1]
for path in ROOT.rglob('*.py'):
    if '__pycache__' not in path.parts:
        py_compile.compile(str(path), doraise=True)

pack = json.loads((ROOT/'content/nmt_2026_pack_v1_6.json').read_text(encoding='utf-8'))
assert len(pack) == 204
assert len({q['question_code'] for q in pack}) == 204
counts = Counter(q['nmt_task_type'] for q in pack)
assert counts == {f'Task {i}': 34 for i in range(1, 7)}
assert all(q['quality_status'] == 'approved' for q in pack)
assert all(set(q['options']) == {'A','B','C','D'} for q in pack)
print('v1.6 release OK')
print('questions:', len(pack))
print('tasks:', dict(sorted(counts.items())))
