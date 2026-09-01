-- ============================================================
-- NETA NMT v1.2 — Curated 12-question onboarding diagnostic
-- FIXED for questions.id UUID. Safe to rerun.
-- ============================================================

ALTER TABLE public.questions
ADD COLUMN IF NOT EXISTS is_diagnostic boolean NOT NULL DEFAULT false;

-- Remove only our current diagnostic pool; ordinary questions stay untouched.
DELETE FROM public.questions
WHERE is_diagnostic = true;

INSERT INTO public.questions (
    topic, difficulty, question_text, options, correct_option, explanation,
    category, sub_category, section, is_active, usage_count, is_diagnostic
)
VALUES
('grammar',1,'She _____ to London three times this year.','["has been","was","had been","is"]'::jsonb,0,'We use the Present Perfect for experiences or actions connected with an unfinished time period such as "this year".','Grammar','Tenses','NMT',true,0,true),
('grammar',1,'I saw _____ interesting documentary about space yesterday.','["an","a","the","—"]'::jsonb,0,'We use "an" before a singular countable noun beginning with a vowel sound.','Grammar','Articles','NMT',true,0,true),
('grammar',2,'If I _____ more time, I would learn another language.','["have","had","will have","would have"]'::jsonb,1,'This is the Second Conditional: If + Past Simple, would + infinitive.','Grammar','Conditionals','NMT',true,0,true),
('grammar',1,'You _____ wear a seat belt when you are in a car.','["must","might","could","would"]'::jsonb,0,'"Must" expresses a strong obligation or rule.','Grammar','Modal Verbs','NMT',true,0,true),
('grammar',1,'She has been interested _____ photography since she was a child.','["in","on","at","for"]'::jsonb,0,'The correct collocation is "be interested in something".','Grammar','Prepositions','NMT',true,0,true),
('vocabulary',2,'The new technology has significantly improved the _____ of the process.','["efficient","efficiency","efficiently","efficiencies"]'::jsonb,1,'After "the" we need a noun. "Efficiency" is the noun form of "efficient".','Vocabulary','Word Formation','NMT',true,0,true),
('vocabulary',2,'The hotel was so crowded that we could hardly find a _____ table.','["vacant","ancient","polite","narrow"]'::jsonb,0,'"Vacant" means empty or available.','Vocabulary','Context','NMT',true,0,true),
('grammar',2,'By the time we arrived at the station, the train _____.','["left","has left","had left","was leaving"]'::jsonb,2,'The Past Perfect is used for an action that happened before another past action.','Grammar','Mixed Grammar','NMT',true,0,true),
('reading',1,E'Many students believe that studying for several hours without a break is the best way to prepare for an exam. However, research and experience suggest that short, regular breaks can help maintain concentration and make studying more effective. The key is not simply how long students study, but how effectively they use their time.\n\nWhat is the main idea of the text?','["Students should never study for several hours.","Taking regular breaks can make studying more effective.","Exams are becoming more difficult every year.","Students should study only in the morning."]'::jsonb,1,'The text focuses on how regular breaks can improve the effectiveness of studying.','Reading','Main Idea','NMT',true,0,true),
('reading',1,E'Public libraries have changed significantly in recent years. In addition to books, many libraries now provide computers, internet access and spaces where people can study or work. Some also organize language clubs, lectures and other educational events.\n\nAccording to the text, what can people find in many modern libraries?','["Only printed books","Computers and educational activities","Free accommodation","Restaurants and cinemas"]'::jsonb,1,'The text specifically mentions computers, internet access, study spaces and educational events.','Reading','Detail','NMT',true,0,true),
('reading',2,E'When Anna first moved to the city, she found public transport rather confusing. After a few weeks, however, she became familiar with the different routes and could travel around without checking a map.\n\nWhat does "became familiar with" mean in this context?','["Forgot about","Became comfortable with and understood","Was afraid of","Stopped using"]'::jsonb,1,'In this context, "became familiar with" means she learned how the routes worked and became comfortable using them.','Reading','Vocabulary in Context','NMT',true,0,true),
('reading',2,E'Tom usually studied English only before tests. Although he often received good marks, he noticed that he quickly forgot new vocabulary after each test. He decided to spend fifteen minutes every day reviewing words instead.\n\nWhat can we infer about Tom''s new approach?','["He wants to study less seriously.","He wants to remember vocabulary for longer.","He no longer needs to learn vocabulary.","He plans to stop taking tests."]'::jsonb,1,'Because Tom forgot vocabulary quickly, he decided to review it regularly in order to remember it for longer.','Reading','Inference','NMT',true,0,true);
