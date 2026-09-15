# Neta NMT English — install v5

## Якщо v4 вже встановлена
1. У Supabase SQL Editor виконай **тільки** `migrations/2026_09_15_learning_v5.sql`.
2. Задеплой код v5 на Render.
3. Перезапусти сервіс.
4. Перевір `/start` → `Мій прогрес`: старі + нові відповіді мають відображатися разом.
5. Заверши один Daily і перевір, що лічильник збільшився рівно на кількість нових відповідей.

## Якщо ставиш з нуля
Виконай спочатку `migrations/2026_09_15_learning_v4.sql`, потім `migrations/2026_09_15_learning_v5.sql`, після цього деплой v5.

## Render environment
Обов'язкові:
- `BOT_TOKEN`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ADMIN_IDS`
- `WEBHOOK_BASE_URL`

Опційні:
- `CHANNEL_URL` (за замовчуванням Neta channel, якщо це вже задано в config)
- `MANAGER_USERNAME`

Не публікуй `.env` і service-role key у GitHub.

## Що робить v5
- `user_answers` стає канонічною історією прогресу.
- Старі відповіді перебудовують `user_topic_progress`, тому старі помилки знову можуть потрапляти в Neta Memory.
- UI Daily/Progress/Friends/Course став компактнішим і більш візуальним.
- Дані користувачів, orders, платежі та Premium-права не видаляються.

## Live smoke після деплою
- старий користувач: старі відповіді видно;
- новий користувач: 3 intro питання;
- Daily: 4 питання, результат, streak;
- подвійний tap: одна відповідь;
- restart: сесія продовжується;
- Progress: старі + нові дані;
- Friends: opt-in рейтинг;
- Course: view + interest;
- Channel;
- reminders;
- admin panel.

Локальні тести не замінюють реальний Telegram/Supabase/Render smoke-test.
