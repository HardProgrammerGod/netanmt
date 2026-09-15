# Neta NMT English v4 — test report

Дата: 2026-09-15.

## Перевірено локально

### Python source integrity

`python -m compileall -q .`

Перевіряє синтаксис усіх Python-файлів.

### Release smoke test

`python tools/smoke_test_learning_v4.py`

Перевіряє:

- onboarding + Neta Memory;
- optional diagnostic;
- full-text A–D options + compact answer buttons;
- відсутність technical Task labels у learner UI;
- persistent sessions і idempotent answers;
- DB-side correctness validation;
- Daily-only streak;
- scalable selector;
- old-user compatibility;
- reminders/referrals/leaderboard;
- channel/course analytics;
- pseudonymous public ranking;
- webhook secret verification;
- backend-only RPC permissions/RLS hardening;
- відсутність obvious committed secrets;
- admin router precedence/guard.

### Content validation

`python tools/validate_content.py`

Bundled v1.7 pack перевіряється на структуру, task distribution і correct answer positions.

### Secret scan

`python tools/security_check.py`

Шукає типові Telegram token/JWT/Supabase secret patterns у репозиторії. `.env` не входить у Git і `.gitignore` доданий.

## Що потребує live verification після deploy

Без production Telegram/Supabase/Render credentials локально неможливо чесно підтвердити:

- execution migration на конкретній production БД;
- справжній Telegram signed webhook;
- concurrent double-click проти PostgreSQL;
- Render restart/cold start;
- actual reminder delivery;
- TelegramForbiddenError після блокування;
- реальний referral flow між двома акаунтами;
- production admin ID;
- p50/p95 latency під реальним трафіком.

Ці пункти є одноразовим post-deploy smoke test, а не причиною продовжувати product development.
