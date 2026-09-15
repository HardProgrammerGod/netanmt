# Neta NMT English v3 — test report

Дата підготовки: 2026-09-15.

## Перевірено локально

### PASS — Python source integrity

Команда:

```bash
python -m compileall -q .
```

Результат: усі Python-файли компілюються синтаксично.

### PASS — v3 release smoke test

Команда:

```bash
python tools/smoke_test_learning_v3.py
```

Перевіряє source/migration invariants, зокрема:

- value proposition + 3-question intro;
- optional 12-question diagnostic;
- channel CTA;
- відсутність активного Premium purchase CTA;
- persistent `learning_sessions`;
- idempotent `UNIQUE(session_id, question_index)`;
- server-side correctness validation;
- atomic topic progress update;
- scalable PostgreSQL question selector;
- old-user compatibility;
- pseudonymous leaderboard identity;
- reminder safety/scale RPC;
- atomic referral activation;
- DB-side admin analytics;
- D1/D3/D7 building blocks;
- admin router order/guard;
- balanced PostgreSQL function bodies.

Результат: `SMOKE_V3_OK`.

### PASS — content pack validation

Команда:

```bash
python tools/validate_content.py
```

Результат для bundled v1.7 pack:

- 120 questions;
- Task 1–6: по 20;
- Reading: 80;
- Use of English: 40;
- correct positions A/B/C/D: 30/30/30/30.

### PASS — static scenario design

За кодом/constraints перевірено:

- **новий user**: отримує value proposition, не 12-question gate;
- **старий user**: legacy progress markers пропускають intro;
- **restart**: question IDs/current index/answers зберігаються в PostgreSQL;
- **double callback**: row lock + unique answer index + order validation;
- **DB answer truth**: correct answer читається з `questions.correct_option` у SQL;
- **partial activity**: answer already counts for retention day;
- **leaderboard**: point only after completed session, max 1/day;
- **DB failure path**: answer keyboard прибирається лише після успішного write; exception повертає safe retry message;
- **reminder**: suppress only after completed Daily, not merely partial activity;
- **blocked reminder recipient**: `TelegramForbiddenError` → inactive/reminder off;
- **referral**: DB atomic, one activation per referred user;
- **admin**: admin router included before generic router and explicit admin guard exists.

## Що НЕ можна чесно вважати перевіреним до production/staging deploy

Це середовище не має production credentials, локального PostgreSQL/Supabase та доступу до Telegram Bot API. Також `aiogram`/`supabase` не були встановлені в середовищі, а спроба підтягнути packages була заблокована відсутністю мережевого доступу.

Тому після встановлення обов’язково потрібні живі перевірки:

- виконання SQL migration саме на вашому Supabase;
- реальний Telegram webhook/callback flow;
- actual concurrent double-click against PostgreSQL;
- restart на Render;
- TelegramForbiddenError на заблокованому test account;
- реальна доставка reminder за київським часом;
- реальний referral activation;
- admin panel з production ADMIN_IDS;
- latency/cold-start numbers на Render;
- поведінка під реальним навантаженням.

## Важлива примітка про канал

`channel_view` = користувач відкрив екран із CTA на `@neta_nmt`. Це корисна funnel metric, але не доказ підписки. Бот навмисно не блокує навчання вимогою підписатися.

## Важлива примітка про SQL

Міграція спроєктована як additive/rerunnable за основними DDL частинами і не видаляє legacy business data. Проте локального PostgreSQL parser/runtime у цьому середовищі немає, тому фінальна SQL execution check має бути зроблена у Supabase SQL Editor після backup.

## Release decision

Код готовий до staging/production installation **за умови виконання post-deploy checklist з `INSTALL_V3.md`**. Живі інтеграційні пункти вище не можна замінити статичною перевіркою.
