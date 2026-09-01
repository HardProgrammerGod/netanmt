# Neta NMT Content Pack v1.4

`nmt_2026_pack_v1_4.json` contains 120 original practice questions:

- Task 1 — 20
- Task 2 — 20
- Task 3 — 20
- Task 4 — 20
- Task 5 — 20
- Task 6 — 20

The pack is aligned to the 2026 NMT English structure (32 questions in a full block with task counts 5/5/6/6/5/5). Telegram presents matching-style items as individual four-option questions, so the simulator is a practice approximation of the official interface rather than a copy of it.

Run `supabase_v1_4_content_pack.sql` in Supabase to install/update the pack. The migration is idempotent through `question_code`.

Validate the editable JSON source with:

```bash
python tools/validate_content.py content/nmt_2026_pack_v1_4.json
```
