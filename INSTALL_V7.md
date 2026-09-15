# Neta NMT English — install v7

## Важливо
v6 ти ще не публікував, тому **не деплой v6**. Використовуй одразу v7.

Якщо production зараз на v4, v5 або v6:
1. Supabase → SQL Editor.
2. Виконай **тільки** `migrations/2026_09_15_learning_v7.sql`.
3. Запуш код v7 у GitHub.
4. Render → Deploy latest commit.
5. Пройди live smoke нижче.

v7 SQL уже містить v6 upgrade/backfill, тому окремо запускати v5/v6 перед ним не треба.

## Render environment
- `BOT_TOKEN`
- `SUPABASE_URL`
- `SUPABASE_SERVICE_ROLE_KEY`
- `ADMIN_IDS`
- `WEBHOOK_BASE_URL`
- optional `CHANNEL_URL`
- optional `MANAGER_USERNAME`

## Live smoke
1. Старий користувач → `📊 Мій прогрес`: стара історія на місці.
2. Daily з помилкою → `🧠 Закріпити помилки · 5`.
3. Daily 4/4 → `🚀 Підвищити складність · 5`.
4. `🔥 Повне тренування · 10`.
5. Після `🏠 Завершити` головний екран усе одно дозволяє продовжити навчання.
6. Focus mode реально повертає матеріал із помилок; challenge mode пріоритезує difficulty 2–3.
7. Подвійний tap на відповідь не зараховується двічі.
8. Restart Render посеред сесії → `/start` → продовження.
9. `🏆 Рейтинг`: XP, opt-in, псевдонім; кнопки invite/back.
10. `Вийти з рейтингу` є в `⚙️ Налаштування`, а не в рейтингу.
11. `🎓 Курс` → `🔔 Повідомити про запуск` → підтвердження раннього доступу.
12. Admin learning report, referral, channel, reminder, cold start.

Локальні тести не замінюють production Supabase/Telegram/Render smoke.
