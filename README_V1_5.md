# Neta NMT v1.5 — Progress & Content Pack #2

## What this release adds

- 180 new original NMT-style questions (30 per Task 1–6).
- Total regular content reaches 300 questions if v1.4 Pack #1 is already installed.
- Progress Dashboard with overall mastery, weakest/strongest topics, accuracy and recommended next step.
- Full simulation history in `simulation_results`.
- NMT-2026 official 32-point -> 100–200 conversion inside the bot for full 32-question simulations.
- Diagnostic topic normalization so new onboarding results feed the adaptive selector more directly.

## Install

1. In Supabase SQL Editor run `supabase_v1_5_progress_and_content.sql` once.
2. Confirm the verification query shows 180 questions in Pack #2 and ~300 approved regular questions in total if Pack #1 was already loaded.
3. Deploy this repository to Render with `python main.py`.
4. Open the bot, go to `📊 Мій прогрес`, then complete a 32-question simulation and return to progress.

## Important

Do not rerun old v1.2/v1.3/v1.4 migrations unless you intentionally need to repair those parts. The v1.5 migration is idempotent and does not delete Pack #1.
