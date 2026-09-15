# Neta NMT English — Telegram v7

Current production candidate: **v7**.

Neta is a short NMT English learning loop with persistent Neta Memory, adaptive
repetition, benefit-first extra practice, progress and weekly XP.

## Learner loop
`3-question demo → Daily → useful next action → Neta Memory → Progress/Ranking → return`

Daily is the habit anchor, not a learning cap.

After Daily:
- mistakes → `Закріпити помилки · 5`;
- perfect Daily → `Підвищити складність · 5`;
- deeper session → `Повне тренування · 10`.

## Product surfaces
- ⚡ Daily;
- 🧠 focus practice;
- 🚀 challenge practice;
- 🔥 full practice;
- 📊 progress;
- 🏆 opt-in weekly XP ranking;
- 🎓 Neta School early-access funnel;
- 📣 channel;
- ⚙️ reminders/privacy/ranking settings;
- admin learning analytics.

## Upgrade
If production is on v4/v5/v6, run only:
`migrations/2026_09_15_learning_v7.sql`

Then deploy v7 code.

See:
- `INSTALL_V7.md`
- `PRODUCT_V7.md`
- `TEST_REPORT_V7.md`

Release gate:
`python tools/smoke_test_learning_v7.py`
