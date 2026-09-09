from pathlib import Path
import json
import py_compile

root=Path(__file__).resolve().parents[1]
required=[
    root/'main.py', root/'bot'/'handlers.py', root/'bot'/'db_client.py',
    root/'supabase_v1_5_progress_and_content.sql', root/'content'/'nmt_2026_pack_v1_5.json'
]
for path in required:
    assert path.exists(), f'missing: {path}'
for path in (root/'bot').glob('*.py'):
    py_compile.compile(str(path), doraise=True)
py_compile.compile(str(root/'main.py'), doraise=True)
pack=json.loads((root/'content'/'nmt_2026_pack_v1_5.json').read_text(encoding='utf-8'))
assert len(pack)==180
assert len({q['question_code'] for q in pack})==180
counts={f'Task {i}':0 for i in range(1,7)}
for q in pack:
    counts[q['nmt_task_type']]+=1
assert all(v==30 for v in counts.values()), counts
print('V1.5 release OK')
print('Pack #2:', len(pack))
print('Task counts:', counts)
