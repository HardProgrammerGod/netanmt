# Neta Telegram v3 — product freeze note

## Що вважаємо ядром продукту

**Обіцянка:** 5 хвилин на день; Neta пам’ятає помилки, повертає їх і показує конкретні навички.

**Механіка:** Neta Memory.

**Основна дія:** «Заняття на сьогодні».

**Retention:** добровільне нагадування + накопичуваний прогрес + канал із безкоштовним контентом.

**Growth:** referrals + opt-in weekly leaderboard + source attribution.

**Monetization discovery:** «Про курс» → `course_view` → «Мені цікаво» → `course_interest`.

## Що свідомо НЕ додаємо зараз

- примусову підписку на канал;
- fake scarcity;
- aggressive Premium paywall;
- десятки режимів;
- складні ліги;
- нескінченне фармлення балів;
- прогноз НМТ на основі кількох відповідей.

## Коли Telegram можна не чіпати і рухатись у Web

Після post-deploy smoke test і виправлення лише blocker-багів. Нові product ideas варто перевіряти даними, а не додавати автоматично.

Web має використовувати те саме ядро даних: `users`, `learning_sessions`, `learning_session_answers`, `user_topic_progress`, `learning_days`, `events`, course-interest events.

## Метрики, за якими вирішувати наступні кроки

1. `/start` → intro start.
2. intro start → intro complete.
3. intro complete → first Daily start/complete.
4. D1 / D3 / D7 серед matured cohorts.
5. channel_view / completed learners.
6. referral activation rate.
7. course_interest / course_view.
8. answer/start p50/p95 latency + error rate.

Фічу варто змінювати лише якщо вона вирішує конкретне просідання в цій воронці або потрібна Web-продукту.
