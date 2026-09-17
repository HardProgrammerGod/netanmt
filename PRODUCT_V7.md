# Neta Telegram v7 — product freeze candidate

## Головний принцип
Кнопка продає **результат**, а число лише пояснює обсяг.

Після Daily:
- якщо були помилки → `🧠 Закріпити помилки · 5`;
- якщо 4/4 → `🚀 Підвищити складність · 5`;
- завжди → `🔥 Повне тренування · 10`.

5-question CTA стоїть першим: нижчий психологічний поріг і чистіший сигнал extra-practice rate.

## Реальна семантика CTA
- `focus`: пріоритет останніх невиправлених помилок;
- `challenge`: пріоритет unseen approved questions difficulty 2–3, потім складніші seen;
- `full`: звичайний adaptive mix Neta Memory.

Тобто назви кнопок не є лише маркетинговим текстом.

## Головний екран після Daily
Показує результат Daily, тему помилки/стан 4/4 та одразу дає продовження.
Окремої кнопки `Сьогодні виконано` немає.

Навігація:
`📊 Мій прогрес`
`🏆 Рейтинг · 🎓 Курс`
`📣 Канал · ⚙️ Налаштування`

## Рейтинг
`Друзі` перейменовано на `Рейтинг`.
Weekly ranking = XP. Public identity = pseudonym. Participation = opt-in.
`Вийти з рейтингу` перенесено в Settings.

## Progress
Компактний learner-facing екран:
learning days, streak, accuracy, completed tasks, strong topics, topics to repeat.
CTA: skill map + weak-topic practice.

## Neta School
Course screen більше не пояснює внутрішню перевірку попиту.
`course_interest` тепер означає конкретну дію: `Повідомити про запуск` / early-access waitlist.

## Business metrics
Після v7 головні метрики:
activation, D1/D3/D7, Daily completion, extra-practice start/completion,
5-vs-10 choice, weekly XP participation, referrals, channel view, course waitlist.

Після live smoke Telegram feature scope заморожується до появи даних.
