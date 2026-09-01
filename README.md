# Neta NMT v1.5

Current release: **Progress Dashboard + Content Pack #2**. See `README_V1_5.md` for deployment steps.

# Neta NMT v1.4 — Content & Simulation Release

Before deploying v1.4, run `supabase_v1_4_content_pack.sql` in Supabase SQL Editor. It adds the content metadata columns/indexes and installs Content Pack #1.

## What v1.4 adds

- 120 original NMT-2026-style practice questions (20 for each Task 1–6);
- a 32-question full practice simulation with official 2026 task counts: 5/5/6/6/5/5;
- adaptive training now selects only approved, active, non-diagnostic content;
- simulation prefers questions the learner has not answered before;
- question counters now show `current/total` and the NMT task label;
- analytics events `simulation_started` and `simulation_completed`;
- JSON source pack plus a local content validator.

## Deploy order

1. Run `supabase_v1_4_content_pack.sql`.
2. Confirm the final SQL output shows 20 questions for each Task 1–6 and 120 total.
3. Deploy this code to Render.
4. Open `Тренування НМТ` -> `Повна симуляція НМТ — 32`.
5. Keep the existing 12-question diagnostic; do not rerun the old v1.2 seed unless you intentionally want to recreate it.

## Important

This simulator mirrors the official NMT-2026 question count and task proportions, but Telegram renders matching-style tasks as individual four-option items. It is practice content, not an official UCEQA test or score predictor.
