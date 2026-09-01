

## v1.3 — Adaptive Learning Engine

Before deploying v1.3, run `supabase_v1_3_learning_engine.sql` in Supabase SQL Editor.

What v1.3 adds:
- per-topic learner mastery (`user_topic_progress`);
- adaptive question selection based on weak topics, prior mistakes and difficulty;
- diagnostic answers seed the learner profile;
- visible mastery changes after regular trainings;
- product funnel events (`events`) for diagnostic, training and Stars payments;
- diagnostic questions are excluded from ordinary training.

If your v1.2 diagnostic pool is already working and contains 12 questions, you do **not** need to rerun `supabase_v1_2_diagnostic.sql`.
