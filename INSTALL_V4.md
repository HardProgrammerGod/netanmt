# Neta NMT English v4 — встановлення

## 1. SQL

У Supabase SQL Editor виконайте **один** файл:

`migrations/2026_09_15_learning_v4.sql`

Це cumulative migration для поточного legacy schema. Вона не видаляє `users`, `user_answers`, `orders`, Premium-права чи історію платежів.

Backup перед production migration бажаний як страховка для відкату, але сам бот його не потребує.

V4 додає/оновлює:

- persistent learning sessions;
- idempotent answers;
- Neta Memory / topic progress;
- curated intro і добровільну діагностику;
- Daily streak тільки за завершений Daily;
- reminders, referrals, opt-in leaderboard;
- analytics, latency та error reporting;
- scalable DB-side question selection;
- захист internal RPC/table access для server-side Supabase key.

## 2. Supabase key — важливо

Telegram bot є backend-застосунком. На Render використовуйте **server-only Supabase service-role/secret key**, а не publishable/anon key.

Рекомендовано:

```env
SUPABASE_SERVICE_ROLE_KEY=...
```

Старе ім’я `SUPABASE_KEY` залишене як fallback для сумісності, але після v4 воно також повинно містити backend/service-role key.

Ніколи не додавайте цей ключ у GitHub, frontend або майбутній Web-клієнт.

## 3. Render environment

```env
BOT_TOKEN=...
SUPABASE_URL=...
SUPABASE_SERVICE_ROLE_KEY=...
WEBHOOK_BASE_URL=https://your-render-service.onrender.com
ADMIN_IDS=123456789
CHANNEL_URL=https://t.me/neta_nmt
```

`WEBHOOK_SECRET` можна не задавати: v4 безпечно й стабільно виводить його з `BOT_TOKEN` і використовує для перевірки заголовка Telegram webhook. Якщо задаєте вручну, дозволені лише `A-Z a-z 0-9 _ -`.

## 4. Render deploy

- Build Command: `pip install -r requirements.txt`
- Start Command: `python main.py`
- Health Check: `/health`
- `WEBHOOK_BASE_URL` вказуйте без `/webhook` наприкінці.

Після старту webhook встановлюється автоматично із secret token.

## 5. Канал

Для переходів **із каналу в бот** використовуйте атрибутоване посилання:

`https://t.me/netaNMT_bot?start=channel_neta`

Для реклами створюйте окремі start-параметри, наприклад `tiktok_01`, `telegram_ad_01`. Це дозволяє бачити перше джерело залучення.

## 6. Post-deploy smoke test

Після першого deploy перевірте один раз:

1. Новий user: `/start` → 3 intro → профіль → Daily.
2. Довгі варіанти A–D повністю видно в тексті; кнопки лише `A/B/C/D`.
3. Старий user не проходить intro повторно.
4. Почати Daily → restart Render → `/start` продовжує те саме питання.
5. Double tap не додає дві відповіді.
6. Завершений Daily піднімає streak лише один раз за день.
7. Diagnostic = 12 питань і карта навичок без прогнозу НМТ.
8. Reminder приходить тільки якщо Daily не завершено; `off` вимикає його.
9. Після блокування бота reminder worker ставить user inactive.
10. Referral активується один раз після intro.
11. Leaderboard добровільний, максимум 1 бал/день, публічно лише псевдонім.
12. `Про курс`: `course_view` і `course_interest` окремі.
13. `Канал`: CTA відкриває `@neta_nmt`.
14. Admin panel доступна лише `ADMIN_IDS`.
15. У Render logs немає BOT_TOKEN/Supabase key.

Після цього Telegram-ядро варто змінювати лише через blocker-баги або дані з воронки, а основну розробку переносити у Web.
