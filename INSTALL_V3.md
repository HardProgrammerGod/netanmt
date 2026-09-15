# Neta NMT English v3 — встановлення

## 1. Зробіть backup Supabase

Перед міграцією збережіть резервну копію/експорт важливих таблиць. Міграція additive і не видаляє старі `users`, `user_answers`, `orders`, Premium-права чи платежі, але production migration все одно треба запускати після backup.

## 2. Запустіть одну актуальну міграцію

У Supabase SQL Editor виконайте весь файл:

`migrations/2026_09_15_learning_v3.sql`

Не запускайте старі v2 migration-файли — їх немає у фінальному ZIP.

Міграція:

- додає persistent learning sessions;
- додає idempotent answers;
- додає Neta Memory / topic progress update у DB transaction;
- додає learning days, reminders, leaderboard opt-in, referral activations;
- додає metrics/errors/events support;
- додає curated intro flags;
- додає selector RPC без application-side LIMIT 1000;
- додає atomic referral RPC;
- додає scale-safe reminder RPC;
- додає DB-side admin analytics;
- зберігає legacy users/answers/orders/Premium;
- позначає старих активних користувачів так, щоб їх не змушувати проходити intro заново.

## 3. Environment variables

Обов’язкові:

```env
BOT_TOKEN=...
SUPABASE_URL=...
SUPABASE_KEY=...
WEBHOOK_BASE_URL=https://your-render-service.onrender.com
ADMIN_IDS=123456789
```

Рекомендовані:

```env
CHANNEL_URL=https://t.me/neta_nmt
```

`SUPABASE_KEY` має мати права на виклик RPC і запис у таблиці, які використовує backend. Не кладіть production secret у Git.

## 4. Deploy

Render:

1. завантажте код/підключіть repo;
2. Build Command: `pip install -r requirements.txt`;
3. Start Command: `python main.py`;
4. Health Check: `/health`;
5. перевірте `WEBHOOK_BASE_URL` без `/webhook` наприкінці — код додає шлях сам.

Після запуску `main.py` встановлює Telegram webhook автоматично.

## 5. Канал як частина воронки

У Telegram-каналі `@neta_nmt` краще замінити звичайне посилання на бота на атрибутоване:

`https://t.me/netaNMT_bot?start=channel_neta`

Для реклами використовуйте окремі start-параметри, наприклад:

- `?start=tiktok_sep`
- `?start=telegram_ad_01`
- `?start=school_chat_01`

Referral-посилання бот формує сам (`ref_<telegram_id>`), але в acquisition analytics вони агрегуються як `referral`, а конкретний referrer зберігається окремо.

## 6. Обов’язкова post-deploy перевірка

Перевірте на окремих тестових акаунтах:

1. **Новий користувач**: `/start` → value prop → 3 intro questions → Neta Memory → Daily.
2. **Старий користувач**: `/start` не змушує проходити intro повторно; старі counters/Premium на місці.
3. **Restart**: почніть Daily, перезапустіть Render, `/start` продовжує з того самого питання.
4. **Double tap**: двічі надішліть той самий callback/натисніть швидко — answer/counter зараховується один раз.
5. **DB failure**: тимчасово використайте invalid test DB/config у staging або симулюйте error; користувач отримує retry text, progress не дублюється.
6. **Diagnostic**: 12 питань, результат = карта навичок, без NMT score prediction.
7. **Reminder**: set time → до завершення Daily приходить → після completed Daily не приходить → off вимикає.
8. **Blocked bot**: після Telegram forbidden reminder worker ставить `is_active=false`, reminder off.
9. **Referral**: новий user через ref link завершує intro → одна activation, без Premium reward.
10. **Leaderboard**: лише opt-in users, максимум 1 point/day, лише псевдонім.
11. **Course**: `course_view` і `course_interest` окремі.
12. **Channel**: CTA відкриває `@neta_nmt`, `channel_view` з’являється в report.
13. **Admin**: звичайний user не має доступу; ADMIN_IDS бачить panel і Learning report.
14. **Cold start**: після sleep/redeploy відкрийте bot; у report перевірте `process_to_first_webhook_ms`, `start_handler_ms`, `webhook_response_ms`.

## 7. Що не треба робити перед Web

Не додавайте ще 10 режимів, ліги, магазин або складну валюту тільки заради кількості функцій. Після цього release варто збирати реальні дані й паралельно будувати Web на тих самих сутностях: users, learning sessions, topic progress, events і course interest.
