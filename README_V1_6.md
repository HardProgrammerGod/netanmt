# Neta NMT v1.6 — Monetization & Launch

This release is intended as the pre-launch business build on top of v1.5.

## What changed

- Manager payment flow defaults to `@nnopkam` and logs manual payment requests.
- Manager checkout uses a pre-filled Telegram draft containing tariff, username, Telegram ID and request ID.
- Admin command `/premium TELEGRAM_ID DAYS` grants verified manual payments and closes pending requests.
- Premium Focus: 10-question adaptive weak-topic session for Premium users.
- Retention worker no longer messages an inactive user every hour. It only sends in the configured Kyiv hour (default 18:00) and respects a cooldown.
- Launch waitlist table + protected `/launch_ping CONFIRM` admin broadcast.
- Content Pack #3: 204 new original practice items, 34 per Task 1–6.
- With v1.4 (120) + v1.5 (180), the regular approved pool becomes about 504 questions, plus the 12 diagnostic questions.

## Upgrade

1. Run only `supabase_v1_6_launch_monetization_content.sql` in Supabase SQL Editor.
2. Deploy this code to Render.
3. In BotFather/Render no new required environment variable is needed. The default manager is `nnopkam`.
4. Optional environment overrides:
   - `MANAGER_USERNAME=nnopkam`
   - `MANAGER_DISCOUNT_PERCENT=27`
   - `RETENTION_SEND_HOUR_KYIV=18`
   - `RETENTION_INACTIVE_HOURS=20`
   - `RETENTION_COOLDOWN_HOURS=20`

## Manager payment

A learner chooses a manager-payment tariff. The bot records a pending request and opens `@nnopkam` with a pre-filled draft.

After you verify payment, use:

`/premium 123456789 30`

The bot grants Premium, marks pending manual requests completed and notifies the learner.

## 42-person preregistration list

The v1.6 migration creates `launch_waitlist`.

Import your old list into that table. The important column is `telegram_id` (Telegram chat/user ID). A template is included as `waitlist_import_template.csv`.

Admin tools:

- Admin panel → `Launch / waitlist`
- `/waitlist_stats`
- `/launch_ping CONFIRM`

The confirmation word is required so the launch broadcast cannot be started accidentally.

Telegram bots can only send a proactive launch message to a chat they are allowed to message. If the old preregistration database does not contain usable Telegram IDs or those people never started this bot, import their data for tracking but do not expect the bot broadcast to reach them automatically.

## Content Pack #3

`content/nmt_2026_pack_v1_6.json`

- Task 1: 34
- Task 2: 34
- Task 3: 34
- Task 4: 34
- Task 5: 34
- Task 6: 34
- Total: 204

Run `python tools/validate_content.py content/nmt_2026_pack_v1_6.json` to validate structure.
