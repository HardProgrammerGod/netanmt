# Neta v7 — release test report

## Локально PASS
- Python compileall.
- `tools/smoke_test_learning_v7.py`.
- Content validation: 120 questions; 20 на кожен NMT task; correct positions 30/30/30/30.
- Benefit-first Daily CTA invariants.
- Semantic focus/challenge/full practice modes.
- Weekly XP ranking + settings opt-out.
- Compact progress + course waitlist copy.
- Existing history/XP/idempotency/security invariants inherited from v4/v6.
- No destructive users/user_answers/orders migration statements.
- No obvious committed Telegram/Supabase secrets.

## Не можна чесно підтвердити локально
- виконання migration у production PostgreSQL;
- реальний Telegram webhook;
- Render cold start/restart;
- production concurrent callbacks;
- реальні reminders/referrals/admin permissions.

Після deploy потрібен один live smoke з `INSTALL_V7.md`.
