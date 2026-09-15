# Neta NMT English v5 — release test report

## Перевірено локально
- Python compileall: PASS.
- Release smoke v5: PASS.
- Content validator: PASS — 120 release questions, 20 per NMT task type, balanced A/B/C/D correct positions.
- Secret scan: PASS — hardcoded Telegram token, Supabase JWT/secret key не знайдені.
- v5 migration static safety check: немає DROP TABLE, TRUNCATE або DELETE для users/user_answers/orders.
- Старий + новий прогрес: код читає один DB-side RPC на основі повної `user_answers` history.
- Neta Memory backfill: v5 migration детерміновано перебудовує `user_topic_progress` з усіх наявних `user_answers`.
- UI invariants: compact A/B/C/D buttons, full options in message, Daily/Memory/Progress/Friends/Course hierarchy.
- Existing v4 persistence/idempotency/security invariants залишилися release-gate у v5 smoke test.

## Що не можна чесно підтвердити локально
Потрібен live deployment:
- виконання PostgreSQL migration у твоєму реальному Supabase;
- реальний Telegram webhook + secret token;
- Render cold start;
- restart під час активної сесії;
- Telegram duplicate callback delivery;
- blocked-user reminder behavior;
- реферальний deep link;
- admin access з твоїм реальним ADMIN_IDS.

## Обов'язковий post-deploy check
1. Відкрий `Мій прогрес` старим акаунтом і звір кількість відповідей.
2. Заверши один Daily; кількість має зрости рівно на 4.
3. Перезапусти Render посеред Daily і продовж.
4. Швидко натисни одну відповідь двічі — має зарахуватися один раз.
5. Перевір Friends, Channel, Course interest, Reminder та Admin.
