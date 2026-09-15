# Neta NMT English — Telegram Product v4

Production-oriented Telegram core перед Web-версією.

## Чим Neta відрізняється

Основна механіка — **Neta Memory**. Користувач проходить коротке Daily, а система зберігає помилки/навички та підмішує потрібні повторення в наступні заняття. Продукт накопичує персональну цінність, а не просто видає випадкові тести.

## UX

- `/start` → 3 curated intro questions;
- Daily = 4 питання (~4 хв);
- довгі A–D варіанти видно повністю в повідомленні;
- компактні кнопки A/B/C/D не обрізають відповіді на мобільному;
- feedback короткий і конкретний;
- результат Daily показує точність, сильнішу навичку, повторення та streak;
- добровільна карта навичок на 12 питань;
- progress, friends, course, settings, channel;
- privacy screen;
- мінімум emoji, без залежності від декоративних стікерів.

## Business funnel

Traffic source → intro → Daily → repeat learning days → channel/referral → course interest.

Канал: `https://t.me/neta_nmt`

Для атрибуції з каналу в бот: `https://t.me/netaNMT_bot?start=channel_neta`.

## Safety / security

- секрети тільки в Render env;
- `.gitignore` блокує `.env`;
- Telegram webhook перевіряє secret token;
- Supabase internal RPCs/table data закриті від anon/authenticated після v4 migration;
- backend використовує server-only service-role/secret key;
- public leaderboard використовує згенерований псевдонім без Telegram ID/username;
- school/city/phone не потрібні для learning flow;
- повторні callbacks не зараховуються двічі.

## Legacy compatibility

Premium purchase CTA прибраний із активного UX, але старі `is_premium`, `premium_until`, `orders` і завершення вже розпочатих Stars payments збережені.

## Deploy

Див. `INSTALL_V4.md`.

Головна migration:

`migrations/2026_09_15_learning_v4.sql`

Release checks:

```bash
python -m compileall -q .
python tools/smoke_test_learning_v4.py
python tools/validate_content.py
python tools/security_check.py
```
