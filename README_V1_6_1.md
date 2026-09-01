# Neta NMT v1.6.1 — Launch Ready

This package is the v1.6 release prepared for the first launch mailing.

## What changed from v1.6
- Imported all 42 legacy rows where `is_active=true`.
- 40 real learners are marked `waiting` and ready for the launch ping.
- `@nnopkam` (manager) and `@netaNMT_bot` (the bot account) are marked `excluded`.
- `/waitlist_stats` now shows excluded rows separately.
- `/launch_preview` shows the exact launch message and current recipient count without sending anything.
- `/launch_ping CONFIRM` only sends to rows with `status='waiting'` and `ping_sent_at IS NULL`.
- Launch copy no longer inserts raw first names, preventing odd/placeholder legacy names from appearing in the mailing.

## Install
If you have NOT run the previous v1.6 SQL yet, run only:

`supabase_v1_6_1_launch_ready.sql`

It contains the full v1.6 migration/content pack plus the 42-row legacy waitlist import.

If you already ran v1.6 SQL, run only:

`launch_waitlist_active_42_seed.sql`

Then deploy the code in this package.

## Before launch
1. `/waitlist_stats` — expected: 42 total, 40 ready, 2 excluded.
2. `/launch_preview` — inspect the message.
3. When ready: `/launch_ping CONFIRM`.

The command is manual; nothing is scheduled automatically.
