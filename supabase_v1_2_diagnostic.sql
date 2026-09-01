-- Neta School / NMT Bot v1.2
-- Curated onboarding diagnostic: 12 questions.
-- Run this once in Supabase SQL Editor.

ALTER TABLE public.questions
    ADD COLUMN IF NOT EXISTS is_diagnostic boolean NOT NULL DEFAULT false;

CREATE INDEX IF NOT EXISTS idx_questions_is_diagnostic
    ON public.questions (is_diagnostic);

-- Make this migration safe to re-run.
UPDATE public.questions
SET is_diagnostic = false
WHERE is_diagnostic IS NULL;

-- Curated 12-question starter diagnostic.
-- We use deterministic IDs so the seed can be recognized/re-run safely.
INSERT INTO public.questions
    (id, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_diagnostic)
VALUES
('diag-v12-01', 'Grammar', 1,
 'If Sarah _____ to school every day, she usually takes the bus.',
 '{"A":"walk","B":"walks","C":"is walk","D":"walking"}', 1,
 'With a third-person singular subject in the Present Simple, the verb takes -s.', 'Use of English', 'Present Simple', 'NMT', true),

('diag-v12-02', 'Grammar', 2,
 'I _____ this book yet, so please do not tell me how it ends.',
 '{"A":"did not finish","B":"have not finished","C":"am not finishing","D":"was not finishing"}', 1,
 'The sentence describes an unfinished action up to the present, so Present Perfect is appropriate.', 'Use of English', 'Present Perfect', 'NMT', true),

('diag-v12-03', 'Grammar', 2,
 'If I _____ more time yesterday, I would have helped you.',
 '{"A":"have","B":"had","C":"had had","D":"would have"}', 2,
 'This is a Third Conditional sentence: if + Past Perfect, followed by would have + past participle.', 'Use of English', 'Conditionals', 'NMT', true),

('diag-v12-04', 'Grammar', 1,
 'You _____ wear a uniform at this school; it is optional.',
 '{"A":"must","B":"have to","C":"do not have to","D":"should"}', 2,
 'The sentence says the uniform is optional, so the correct meaning is lack of obligation.', 'Use of English', 'Modal verbs', 'NMT', true),

('diag-v12-05', 'Grammar', 1,
 'She arrived _____ the airport two hours before her flight.',
 '{"A":"at","B":"in","C":"on","D":"to"}', 0,
 'The standard preposition used with arrive and a specific place such as an airport is at.', 'Use of English', 'Prepositions', 'NMT', true),

('diag-v12-06', 'Articles', 1,
 'My brother wants to become _____ engineer when he grows up.',
 '{"A":"a","B":"an","C":"the","D":"no article"}', 1,
 'Engineer begins with a vowel sound, so the indefinite article an is required.', 'Use of English', 'Articles', 'NMT', true),

('diag-v12-07', 'Vocabulary', 2,
 'The instructions were very _____, so everyone understood what to do.',
 '{"A":"confusing","B":"clear","C":"rare","D":"narrow"}', 1,
 'If everyone understood the instructions, they were clear.', 'Use of English', 'Vocabulary in context', 'NMT', true),

('diag-v12-08', 'Word Formation', 2,
 'The manager thanked us for our _____ and patience during the project.',
 '{"A":"cooperate","B":"cooperative","C":"cooperation","D":"cooperating"}', 2,
 'After our, the sentence needs a noun; cooperation is the noun that fits the meaning.', 'Use of English', 'Word Formation', 'NMT', true),

('diag-v12-09', 'Reading', 1,
 'Read the text: "Mia usually studies in the library because her home is noisy. On Fridays, however, she stays at home because the library closes early." Why does Mia stay at home on Fridays?',
 '{"A":"She prefers studying alone.","B":"Her home is quieter on Fridays.","C":"The library closes early.","D":"She has no classes on Fridays."}', 2,
 'The text explicitly states that the library closes early on Fridays.', 'Reading', 'Reading for detail', 'NMT', true),

('diag-v12-10', 'Reading', 2,
 'Read the text: "Tom started cycling to work last month. At first the journey took him almost an hour, but after a few weeks he found a shorter route and now arrives in about thirty-five minutes." What changed for Tom?',
 '{"A":"He bought a faster bicycle.","B":"He changed his route.","C":"He stopped cycling to work.","D":"He moved closer to work."}', 1,
 'The text says Tom found a shorter route, reducing the journey time.', 'Reading', 'Reading for detail', 'NMT', true),

('diag-v12-11', 'Reading', 2,
 'Read the text: "The café introduced reusable cups and offered a small discount to customers who brought their own. After three months, the owner reported that the amount of disposable-cup waste had fallen significantly." What was one likely reason for the reduction in waste?',
 '{"A":"Customers were encouraged to reuse cups.","B":"The café stopped selling drinks.","C":"The café moved to another building.","D":"Customers received larger drinks."}', 0,
 'The text connects the reduction with reusable cups and an incentive for customers to bring their own.', 'Reading', 'Main idea and inference', 'NMT', true),

('diag-v12-12', 'Reading', 2,
 'Read the text: "Lena wanted to improve her English listening skills. Instead of studying for two hours once a week, she listened to a short podcast for fifteen minutes every evening. After several weeks, she noticed that understanding everyday conversations had become easier." Which approach did Lena choose?',
 '{"A":"Long weekly study sessions","B":"Daily short practice","C":"Only grammar exercises","D":"Speaking practice once a month"}', 1,
 'Lena replaced one long weekly session with fifteen minutes of listening every evening.', 'Reading', 'Main idea', 'NMT', true)
ON CONFLICT (id) DO UPDATE SET
    topic = EXCLUDED.topic,
    difficulty = EXCLUDED.difficulty,
    question_text = EXCLUDED.question_text,
    options = EXCLUDED.options,
    correct_option = EXCLUDED.correct_option,
    explanation = EXCLUDED.explanation,
    category = EXCLUDED.category,
    sub_category = EXCLUDED.sub_category,
    section = EXCLUDED.section,
    is_diagnostic = true;

-- Ensure exactly this curated pool is used for onboarding.
UPDATE public.questions
SET is_diagnostic = false
WHERE id NOT LIKE 'diag-v12-%'
  AND is_diagnostic = true;
