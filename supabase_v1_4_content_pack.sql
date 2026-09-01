-- Neta NMT v1.4: NMT-2026 Content Pack #1 (120 original questions)
-- Safe to run more than once. Content is original and structured around the official 2026 task counts/types.

ALTER TABLE public.questions ADD COLUMN IF NOT EXISTS question_code text;
ALTER TABLE public.questions ADD COLUMN IF NOT EXISTS nmt_task_type text;
ALTER TABLE public.questions ADD COLUMN IF NOT EXISTS content_pack text;
ALTER TABLE public.questions ADD COLUMN IF NOT EXISTS quality_status text NOT NULL DEFAULT 'approved';
CREATE UNIQUE INDEX IF NOT EXISTS idx_questions_question_code ON public.questions(question_code);
CREATE INDEX IF NOT EXISTS idx_questions_nmt_simulation ON public.questions(nmt_task_type, quality_status) WHERE is_active = true AND is_diagnostic = false;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-001', 'reading', 1, 'Read the notice and choose the person it is most suitable for.

NOTICE: Saturday English Speaking Club. Small groups, games and short discussions. No preparation needed. B1+ recommended.', '{"A":"A student who wants relaxed speaking practice","B":"A student looking for a grammar exam","C":"A teacher needing a classroom","D":"A beginner who cannot understand basic English"}'::jsonb, 0, 'The notice is specifically for informal speaking practice in small groups.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-002', 'reading', 1, 'Read the notice and choose the person it is most suitable for.

CITY LIBRARY: Exam Week. Quiet study room open until 10 p.m. Bring your student card. Individual study only.', '{"A":"Someone planning a group birthday party","B":"Someone who wants a late, quiet place to study","C":"Someone looking for sports training","D":"Someone who needs to borrow a laptop for a month"}'::jsonb, 1, 'The key details are late opening and individual quiet study.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-003', 'reading', 1, 'Read the notice and choose the person it is most suitable for.

BEGINNER CODING LAB: Build your first simple website in two hours. Laptops provided. No previous programming experience required.', '{"A":"An experienced developer seeking a job","B":"A designer selling artwork","C":"A complete beginner interested in web coding","D":"A student preparing for a biology test"}'::jsonb, 2, 'The lab is designed for people with no prior programming experience.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-004', 'reading', 2, 'Read the notice and choose the person it is most suitable for.

VOLUNTEERS NEEDED: Sunday river clean-up, 9:00–12:00. Gloves and bags supplied. Wear comfortable shoes and bring water.', '{"A":"Someone who needs professional sports equipment","B":"Someone looking for paid office work","C":"Someone wanting an indoor concert","D":"Someone who wants to help the environment outdoors"}'::jsonb, 3, 'The activity is an outdoor environmental volunteering event.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-005', 'reading', 1, 'Read the notice and choose the person it is most suitable for.

MUSEUM LATE NIGHT: Free entry for students after 6 p.m. on Friday. Modern art galleries remain open until 9 p.m.', '{"A":"A student who wants an inexpensive evening museum visit","B":"A family looking for a morning zoo trip","C":"A tourist wanting a guided mountain hike","D":"A student needing a language course"}'::jsonb, 0, 'Students can visit the museum free in the evening.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-006', 'reading', 2, 'Read the notice and choose the person it is most suitable for.

BIKE CHECK DAY: Mechanics will inspect brakes, tyres and gears free of charge. Repairs requiring new parts are paid separately.', '{"A":"Someone who wants to buy a new car","B":"A cyclist who wants a free safety inspection","C":"A person looking for a driving lesson","D":"A cyclist needing guaranteed free replacement parts"}'::jsonb, 1, 'The inspection is free, while parts are not.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-007', 'reading', 1, 'Read the notice and choose the person it is most suitable for.

BOOK SWAP: Bring up to five books you have finished and exchange them for others. Please bring books in good condition.', '{"A":"A student wanting to print a textbook","B":"An author seeking a publisher","C":"A reader who wants to exchange used books","D":"A collector looking for rare coins"}'::jsonb, 2, 'The event is for exchanging books people already own.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-008', 'reading', 2, 'Read the notice and choose the person it is most suitable for.

PHOTOGRAPHY WALK: Learn to improve composition using any phone or camera. Sunday, 15:00. Suitable for beginners.', '{"A":"A person searching for a painting class","B":"A professional needing studio rental","C":"Someone who wants to repair a camera","D":"A beginner wanting practical photography tips"}'::jsonb, 3, 'The walk teaches beginner composition with phones or cameras.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-009', 'reading', 1, 'Read the notice and choose the person it is most suitable for.

SCHOOL NEWSPAPER: We need students who enjoy interviewing people, writing short articles or taking photos. Weekly meeting: Wednesday.', '{"A":"A student interested in journalism or photography","B":"A student who only wants maths tutoring","C":"A person seeking full-time employment","D":"A teacher looking for exam papers"}'::jsonb, 0, 'The newspaper needs writers, interviewers and photographers.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-010', 'reading', 2, 'Read the notice and choose the person it is most suitable for.

SCHOLARSHIP Q&A: Online session about application documents, deadlines and common mistakes. Questions can be sent in advance.', '{"A":"A student learning to swim","B":"A student preparing a scholarship application","C":"A tourist booking a hotel","D":"A musician looking for rehearsal space"}'::jsonb, 1, 'The session explains scholarship applications and deadlines.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-011', 'reading', 1, 'Read the notice and choose the person it is most suitable for.

THEATRE AUDITIONS: Looking for students aged 15–18 for a school comedy. Prepare a one-minute monologue. Rehearsals begin next month.', '{"A":"A parent looking for childcare","B":"A student wanting to watch a film","C":"A teenager who wants to act in a play","D":"A musician wanting to sell an instrument"}'::jsonb, 2, 'The notice invites teenagers to audition for acting roles.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-012', 'reading', 2, 'Read the notice and choose the person it is most suitable for.

SWIMMING BASICS: Four Saturday lessons for people who can enter the water confidently but cannot yet swim 25 metres.', '{"A":"A person wanting diving certification","B":"A competitive swimmer training for a race","C":"Someone afraid to enter a swimming pool","D":"A beginner swimmer wanting basic lessons"}'::jsonb, 3, 'The lessons are for basic swimmers who are comfortable in water.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-013', 'reading', 2, 'Read the notice and choose the person it is most suitable for.

ROBOTICS OPEN LAB: Teams can test small robots and get advice from mentors. Participants should already know basic programming.', '{"A":"A team with some programming knowledge developing a robot","B":"A complete beginner who has never used a computer","C":"A student wanting an English speaking club","D":"A family wanting a museum tour"}'::jsonb, 0, 'The lab expects basic programming knowledge and supports robot testing.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-014', 'reading', 1, 'Read the notice and choose the person it is most suitable for.

LOCAL FOOD MARKET: Saturday 8:00–13:00. Fresh bread, cheese, vegetables and honey from nearby farms. Bring your own bag if possible.', '{"A":"Someone looking for electronics","B":"Someone wanting to buy locally produced food","C":"Someone needing a restaurant reservation","D":"Someone wanting to rent a bicycle"}'::jsonb, 1, 'The market sells food from nearby farms.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-015', 'reading', 2, 'Read the notice and choose the person it is most suitable for.

STUDY SKILLS WEBINAR: Learn how to plan revision, avoid distractions and use short review sessions effectively. Free registration.', '{"A":"A tourist learning city history","B":"A teacher applying for a new job","C":"A student who wants to organize exam preparation better","D":"A student seeking advanced coding practice"}'::jsonb, 2, 'The webinar focuses on planning and effective revision.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-016', 'reading', 1, 'Read the notice and choose the person it is most suitable for.

ART SUPPLIES SALE: Student discount this weekend on sketchbooks, brushes and acrylic paints. Student ID required.', '{"A":"A programmer buying a keyboard","B":"A runner buying sports shoes","C":"A reader buying novels","D":"An art student buying materials"}'::jsonb, 3, 'The discount applies to art materials and requires student ID.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-017', 'reading', 2, 'Read the notice and choose the person it is most suitable for.

HIKING CLUB: Easy 8 km route this Sunday. Participants need comfortable footwear, rain protection and a packed lunch.', '{"A":"Someone looking for a beginner-friendly day hike","B":"Someone seeking an indoor fitness class","C":"Someone wanting a luxury bus tour","D":"Someone needing climbing equipment training"}'::jsonb, 0, 'The route is described as easy and requires basic outdoor preparation.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-018', 'reading', 1, 'Read the notice and choose the person it is most suitable for.

FILM CLUB: Watch an English-language film with English subtitles, then discuss it together. Thursday at 17:30.', '{"A":"A person looking for silent meditation","B":"A learner who wants to combine film and English practice","C":"A student wanting a chemistry laboratory","D":"A musician searching for a concert"}'::jsonb, 1, 'The activity combines an English film and discussion.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-019', 'reading', 2, 'Read the notice and choose the person it is most suitable for.

CAFÉ WEEKEND ASSISTANT: 8 hours on Saturday. Tasks include taking orders, clearing tables and helping customers. Training provided.', '{"A":"A student wanting unpaid volunteering","B":"Someone looking for a full-time engineering role","C":"Someone seeking short weekend customer-service work","D":"A chef seeking advanced professional training"}'::jsonb, 2, 'This is short weekend work involving customer service.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T1-020', 'reading', 2, 'Read the notice and choose the person it is most suitable for.

LANGUAGE EXCHANGE: Practise Ukrainian and English with international students. You should be comfortable holding a simple conversation in English.', '{"A":"A complete beginner learning the alphabet","B":"Someone who wants a silent reading room","C":"A person needing translation certification","D":"Someone who can already have a basic English conversation"}'::jsonb, 3, 'The exchange requires enough English for a simple conversation.', 'Reading', 'Matching: Notices', 'NMT', true, false, 'Task 1', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-001', 'reading', 1, 'Maya used to revise only the night before a test. This term, she began studying for twenty minutes each evening. She says she now feels calmer before exams and remembers more afterwards.

What changed in Maya''s study routine?', '{"A":"She studies in shorter regular sessions","B":"She stopped taking tests","C":"She studies only in the morning","D":"She studies with a private teacher"}'::jsonb, 0, 'The passage says she now studies for twenty minutes each evening.', 'Reading', 'Reading: Detail', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-002', 'reading', 2, 'A small café near the station removed half of its indoor tables and added a covered outdoor area. The owner says customers stay longer there during warm months, while the indoor space feels less crowded.

Why did the café change its seating?', '{"A":"To stop serving customers indoors","B":"To create a more comfortable use of space","C":"To reduce the number of customers","D":"To turn the café into a shop"}'::jsonb, 1, 'The change made indoor seating less crowded and added useful outdoor space.', 'Reading', 'Reading: Detail', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-003', 'reading', 2, 'Leo bought a second-hand laptop because a new model was outside his budget. Before paying, he checked the battery, keyboard and screen and asked for a short warranty from the shop.

What does the passage suggest about Leo?', '{"A":"He never checked the laptop","B":"He wanted the most expensive model","C":"He made a careful purchase","D":"He borrowed the laptop from a friend"}'::jsonb, 2, 'He checked key parts and asked for a warranty before buying.', 'Reading', 'Reading: Main Idea', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-004', 'reading', 1, 'The town''s new bus app shows live arrival times. It does not sell tickets yet, but passengers can save favourite stops and receive service alerts.

Which feature is NOT available in the app?', '{"A":"Live arrival times","B":"Saved favourite stops","C":"Service alerts","D":"Ticket purchases"}'::jsonb, 3, 'The text explicitly says the app does not sell tickets yet.', 'Reading', 'Reading: Detail', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-005', 'reading', 2, 'Nina joined a school debate club mainly to become more confident speaking in front of others. After two months, she noticed another benefit: she had become better at listening carefully before replying.

What unexpected benefit did Nina notice?', '{"A":"She learned to listen more carefully","B":"She stopped feeling nervous immediately","C":"She won every debate","D":"She began writing longer essays"}'::jsonb, 0, 'Listening carefully is described as an additional benefit.', 'Reading', 'Reading: Main Idea', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-006', 'reading', 2, 'A community garden gives local residents small plots to grow vegetables. Members share tools and water, but each person is responsible for looking after their own plot.

What are members expected to do individually?', '{"A":"Buy all shared tools","B":"Look after their own growing area","C":"Pay for everyone''s water","D":"Manage the entire garden"}'::jsonb, 1, 'Each member is responsible for their own plot.', 'Reading', 'Reading: Detail', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-007', 'reading', 3, 'When a software company introduced one meeting-free afternoon each week, managers worried communication would suffer. Instead, employees reported finishing more focused work, while teams moved routine updates to short written messages.

What was the result of the change?', '{"A":"Managers added more long meetings","B":"Employees refused to communicate","C":"Focused work increased without stopping communication","D":"The company ended written updates"}'::jsonb, 2, 'The company preserved communication while increasing focused work.', 'Reading', 'Reading: Detail', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-008', 'reading', 1, 'The science centre''s new exhibition is designed for visitors to touch, test and move many of the displays. Staff say the goal is to make difficult ideas easier to understand through direct experience.

What is special about the exhibition?', '{"A":"It focuses entirely on paintings","B":"It is only for scientists","C":"Visitors cannot touch anything","D":"It is highly interactive"}'::jsonb, 3, 'Visitors are encouraged to interact directly with the displays.', 'Reading', 'Reading: Detail', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-009', 'reading', 2, 'Oleh cycles to college when the weather is dry, but on rainy days he takes the metro. He says cycling is usually faster during morning traffic and also gives him some exercise.

Why does Oleh often choose to cycle?', '{"A":"It can save time and provides exercise","B":"The metro is permanently closed","C":"He dislikes all public transport","D":"His college is outside the city"}'::jsonb, 0, 'He mentions both speed in traffic and exercise.', 'Reading', 'Reading: Main Idea', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-010', 'reading', 2, 'A bookshop began placing short staff recommendations beside selected novels. Sales of those books increased, especially when the notes explained who might enjoy the story rather than simply saying it was good.

Which recommendations were most effective?', '{"A":"Those using only one-word praise","B":"Those describing the type of reader who might enjoy the book","C":"Those hiding the book''s subject","D":"Those written by customers who had not read the book"}'::jsonb, 1, 'The passage says recommendations worked best when they explained who would enjoy the story.', 'Reading', 'Reading: Main Idea', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-011', 'reading', 3, 'Researchers asked two groups of students to learn the same list of words. One group reread the list several times; the other repeatedly tried to recall the words without looking. A week later, the recall group remembered more.

What conclusion best matches the study?', '{"A":"Students should avoid testing themselves","B":"Reading once always guarantees long-term memory","C":"Trying to retrieve information can strengthen memory","D":"Learning vocabulary is impossible without a teacher"}'::jsonb, 2, 'The group practising recall remembered more after a week.', 'Reading', 'Reading: Detail', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-012', 'reading', 1, 'The local pool now opens at 6:30 on weekdays. The earlier time was introduced after many residents said they wanted to swim before work or school.

Why was the opening time changed?', '{"A":"To close the pool during weekends","B":"To reduce the number of swimmers","C":"To prepare for evening competitions","D":"To meet demand for early swimming"}'::jsonb, 3, 'Residents requested an earlier time before work or school.', 'Reading', 'Reading: Detail', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-013', 'reading', 2, 'Sara planned to buy a printed travel guide but finally downloaded an offline city map instead. She knew mobile internet might be expensive abroad and wanted directions that would work without a connection.

Why did Sara choose an offline map?', '{"A":"It works without mobile internet","B":"It contains no street names","C":"It is always more detailed than every guide","D":"It requires constant online access"}'::jsonb, 0, 'Her main concern was using directions without internet access.', 'Reading', 'Reading: Main Idea', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-014', 'reading', 2, 'A school replaced some traditional homework with short projects in which students choose examples from everyday life. Teachers found that students asked more questions in class because they wanted to check whether their examples really fit the topic.

How did the projects affect students?', '{"A":"They eliminated the need for lessons","B":"They encouraged more classroom questions","C":"They made students avoid real-life examples","D":"They reduced all homework to zero"}'::jsonb, 1, 'Students asked more questions to verify their examples.', 'Reading', 'Reading: Detail', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-015', 'reading', 3, 'A small clothing brand started publishing repair guides for its jackets. At first this seemed likely to reduce sales, but the company says customers became more loyal because they trusted a brand that helped products last longer.

Why did the repair guides help the company?', '{"A":"They made repairs impossible","B":"They forced customers to buy new jackets immediately","C":"They increased customer trust and loyalty","D":"They removed the need for customer service"}'::jsonb, 2, 'Helping products last longer strengthened trust and loyalty.', 'Reading', 'Reading: Inference', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-016', 'reading', 1, 'The university café offers a discount to customers who bring a reusable cup. The programme aims to reduce the number of disposable cups used each day.

What is the purpose of the discount?', '{"A":"To stop customers bringing drinks","B":"To increase the price of coffee","C":"To sell more disposable cups","D":"To reduce waste"}'::jsonb, 3, 'The discount encourages reusable cups and therefore less waste.', 'Reading', 'Reading: Detail', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-017', 'reading', 2, 'After moving into a noisy street, Daniel first tried studying with music. He soon found that quiet background noise through headphones worked better because songs distracted him from reading.

Why did Daniel stop using music while studying?', '{"A":"Songs distracted his attention","B":"His headphones stopped working","C":"He no longer needed to study","D":"The street became completely silent"}'::jsonb, 0, 'The passage says songs distracted him from reading.', 'Reading', 'Reading: Detail', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-018', 'reading', 3, 'A local history project asked older residents to record memories of the neighbourhood. Students then compared these stories with old photographs and maps. The aim was not to prove every memory exact, but to understand how people experienced changes in the area.

What was the main goal of the project?', '{"A":"To prove every memory was perfectly accurate","B":"To explore personal experiences of local change","C":"To replace maps with interviews","D":"To create a tourist advertisement"}'::jsonb, 1, 'The project focused on how residents experienced changes.', 'Reading', 'Reading: Detail', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-019', 'reading', 2, 'An online course allows students to watch recorded lessons at any time, but live workshops are held twice a month. The workshops are used mainly for questions, discussion and practical tasks.

What are the live workshops mainly for?', '{"A":"Taking attendance only","B":"Watching the same recorded lesson silently","C":"Interaction and practice","D":"Downloading course files"}'::jsonb, 2, 'Questions, discussion and practical tasks are interactive activities.', 'Reading', 'Reading: Main Idea', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T2-020', 'reading', 2, 'The city planted young trees along several busy roads. Officials do not expect an immediate change in summer temperatures, but they hope the trees will provide more shade as they grow.

Why will the full benefit take time?', '{"A":"The city plans to remove the trees soon","B":"The roads will close permanently","C":"Shade only works in winter","D":"The trees need time to grow"}'::jsonb, 3, 'Young trees need to mature before they provide substantial shade.', 'Reading', 'Reading: Main Idea', 'NMT', true, false, 'Task 2', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-001', 'reading', 1, 'Choose the option that best matches this person.

I want to improve my English speaking, but I am busy on weekdays and prefer learning with other people.', '{"A":"Saturday Conversation Group","B":"Self-paced Grammar PDF","C":"Monday Morning Writing Class","D":"Private Pronunciation Test"}'::jsonb, 0, 'A Saturday group directly matches the need for weekend speaking practice with others.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-002', 'reading', 2, 'Choose the option that best matches this person.

I already know basic Python and want a short course where I can build a real project rather than only watch lectures.', '{"A":"Introduction to Computers","B":"Python Project Weekend","C":"History of Programming Talk","D":"Typing Skills for Beginners"}'::jsonb, 1, 'The project weekend fits someone with basics who wants hands-on work.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-003', 'reading', 1, 'Choose the option that best matches this person.

I need a place to study after 8 p.m. and I do not want group activities.', '{"A":"Morning Sports Centre","B":"Afternoon Debate Club","C":"Late Quiet Study Hall","D":"Weekend Music Workshop"}'::jsonb, 2, 'The late quiet hall matches both time and individual study.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-004', 'reading', 2, 'Choose the option that best matches this person.

I enjoy drawing and want feedback on my work, but I cannot attend every week.', '{"A":"Online Maths Marathon","B":"Daily Painting Course","C":"Weekly Exam Club","D":"Monthly Portfolio Clinic"}'::jsonb, 3, 'A monthly portfolio clinic offers feedback without weekly attendance.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-005', 'reading', 2, 'Choose the option that best matches this person.

I want to start running, but I have never trained regularly and I am worried about doing too much too soon.', '{"A":"Beginner 5K Plan","B":"Advanced Marathon Team","C":"Competitive Sprint Trials","D":"Mountain Race Club"}'::jsonb, 0, 'A beginner plan is appropriate for gradually starting regular running.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-006', 'reading', 1, 'Choose the option that best matches this person.

I would like to volunteer with animals, but I can only help for a few hours on Sunday.', '{"A":"Weekday Office Internship","B":"Sunday Animal Shelter Helpers","C":"Full-time Farm Manager","D":"Evening Language Exchange"}'::jsonb, 1, 'The Sunday shelter role matches the time and interest in animals.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-007', 'reading', 2, 'Choose the option that best matches this person.

I need help preparing a CV and practising common interview questions for my first part-time job.', '{"A":"Photography Walk","B":"Advanced Business Law","C":"Student Job Workshop","D":"Creative Writing Circle"}'::jsonb, 2, 'A student job workshop directly covers CVs and interviews.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-008', 'reading', 2, 'Choose the option that best matches this person.

I want to practise photography outdoors and I only have a smartphone, not a professional camera.', '{"A":"Film Editing Theory","B":"Studio Lighting for Professionals","C":"Camera Repair Lab","D":"Phone Photography Walk"}'::jsonb, 3, 'The phone photography walk suits outdoor practice with a smartphone.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-009', 'reading', 1, 'Choose the option that best matches this person.

I like reading fiction and want to discuss books with people my age once a month.', '{"A":"Monthly Teen Book Club","B":"Daily News Writing Course","C":"Silent Library Membership","D":"Academic Research Seminar"}'::jsonb, 0, 'The monthly teen book club fits fiction discussion and frequency.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-010', 'reading', 2, 'Choose the option that best matches this person.

I understand grammar rules quite well, but I often choose the wrong word in context during tests.', '{"A":"Basic Alphabet Course","B":"Vocabulary in Context Clinic","C":"Speaking Only Club","D":"Handwriting Workshop"}'::jsonb, 1, 'The vocabulary clinic targets word choice in context.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-011', 'reading', 3, 'Choose the option that best matches this person.

I want a course that gives me deadlines and teacher feedback because I usually stop self-study courses after a week.', '{"A":"Independent Reading List","B":"Open Video Library","C":"Guided Course with Weekly Feedback","D":"One-day Exhibition"}'::jsonb, 2, 'Regular deadlines and feedback address the learner''s difficulty with self-study.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-012', 'reading', 2, 'Choose the option that best matches this person.

I want to learn basic cooking, especially inexpensive meals I can make after school.', '{"A":"Professional Chef Competition","B":"Advanced Pastry Masterclass","C":"Restaurant Management Theory","D":"Budget Cooking for Students"}'::jsonb, 3, 'The student budget course matches beginner, inexpensive after-school cooking.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-013', 'reading', 1, 'Choose the option that best matches this person.

I am interested in local history but prefer walking around the city to sitting in a lecture room.', '{"A":"Historical Walking Tour","B":"Archive Research Lecture","C":"Online Grammar Class","D":"Indoor Chess Tournament"}'::jsonb, 0, 'A walking tour combines local history with being outdoors in the city.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-014', 'reading', 2, 'Choose the option that best matches this person.

I need to improve how I organize notes from different subjects before final exams.', '{"A":"Beginner Guitar Lesson","B":"Revision and Note-Making Workshop","C":"Weekend Cycling Club","D":"Job Interview Practice"}'::jsonb, 1, 'The workshop directly targets revision and note organization.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-015', 'reading', 2, 'Choose the option that best matches this person.

I can swim comfortably but want to improve technique rather than learn from the beginning.', '{"A":"Lifeguard Recruitment","B":"Water Confidence for Beginners","C":"Intermediate Stroke Clinic","D":"Children''s First Swim"}'::jsonb, 2, 'An intermediate technique clinic fits an already comfortable swimmer.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-016', 'reading', 3, 'Choose the option that best matches this person.

I want to learn about starting a small online project and test whether people actually want it before spending much money.', '{"A":"Public Speaking Competition","B":"Corporate Accounting Degree","C":"Advanced Graphic Design Diploma","D":"Lean Project Validation Workshop"}'::jsonb, 3, 'Validation focuses on testing demand before significant spending.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-017', 'reading', 1, 'Choose the option that best matches this person.

I want a free activity where I can practise English by watching something entertaining.', '{"A":"English Film Evening","B":"Private Exam Tutoring","C":"Paid Translation Course","D":"Silent Reading Test"}'::jsonb, 0, 'A film evening is entertaining and can provide language practice.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-018', 'reading', 2, 'Choose the option that best matches this person.

I am confident speaking English but need more practice with reading long texts quickly for exams.', '{"A":"Beginner Conversation Club","B":"Timed Reading Practice","C":"Pronunciation Basics","D":"Creative Drawing Class"}'::jsonb, 1, 'Timed reading practice addresses exam reading speed.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-019', 'reading', 2, 'Choose the option that best matches this person.

I want to repair simple problems on my bicycle myself instead of visiting a shop every time.', '{"A":"Car Mechanics Diploma","B":"Road Racing Team","C":"Basic Bike Maintenance","D":"City Transport History"}'::jsonb, 2, 'Basic maintenance teaches simple bicycle repairs.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T3-020', 'reading', 1, 'Choose the option that best matches this person.

I want to meet international students and exchange languages in a relaxed setting.', '{"A":"Individual Silent Study","B":"Formal Written Exam","C":"Private Coding Lesson","D":"Language Exchange Café"}'::jsonb, 3, 'A language exchange café is a relaxed social language setting.', 'Reading', 'Matching: Situations', 'NMT', true, false, 'Task 3', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-001', 'reading', 1, 'I used to keep all my school deadlines in my head. _____ Now I check it every evening and rarely forget an assignment.', '{"A":"Then I started using a simple calendar app.","B":"However, I stopped studying completely.","C":"For example, calendars are always expensive.","D":"As a result, I never write anything down."}'::jsonb, 0, 'The next sentence refers to checking ''it'', so a calendar app fits logically.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-002', 'reading', 2, 'The park was once almost empty in the evenings. The city added better lighting and repaired the paths. _____ Families and runners now use it much more often after work.', '{"A":"In contrast, the park was moved to another city.","B":"As a result, people began to feel safer there.","C":"Nevertheless, the paths were removed again immediately.","D":"For this reason, nobody can enter the park."}'::jsonb, 1, 'Improved lighting and paths logically lead to greater safety and more use.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-003', 'reading', 2, 'Online lessons can be convenient because students can learn from home. _____ Without a routine, it is easy to postpone work until later.', '{"A":"For example, internet access is never necessary.","B":"Therefore, every online lesson is easier than school.","C":"However, they still require self-discipline.","D":"Similarly, students cannot choose when to study."}'::jsonb, 2, 'The contrast is convenience versus the need for self-discipline.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-004', 'reading', 1, 'Lena wanted to read more books this year. She decided not to set an enormous target. _____ After a few months, reading had become part of her normal routine.', '{"A":"For example, she bought a television.","B":"As a result, she gave away every book she owned.","C":"However, she stopped reading on the first day.","D":"Instead, she began with ten pages a day."}'::jsonb, 3, 'A small daily target explains how reading became a routine.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-005', 'reading', 2, 'The school café introduced a reusable cup discount. At first, only a few students brought their own cups. _____ By the end of the term, the number had increased significantly.', '{"A":"Teachers then reminded students about the programme.","B":"The café then banned all drinks.","C":"No one was allowed to enter the building.","D":"The discount was removed before it began."}'::jsonb, 0, 'Reminders can logically explain the later increase in participation.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-006', 'reading', 2, 'Mark was nervous before giving presentations. He began practising them aloud at home and recording himself. _____ This helped him notice where he spoke too quickly.', '{"A":"He deleted every presentation before speaking.","B":"He listened to the recordings afterwards.","C":"He decided never to practise again.","D":"He turned off the microphone during class."}'::jsonb, 1, 'Listening to recordings explains how he noticed his speaking speed.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-007', 'reading', 3, 'Many people assume creativity appears only when inspiration arrives. In reality, creative professionals often rely on routines. _____ Regular work creates more opportunities for useful ideas to appear.', '{"A":"They refuse to repeat any process.","B":"They avoid working until the perfect idea arrives.","C":"They set aside time to produce ideas even on ordinary days.","D":"They believe schedules always destroy creativity."}'::jsonb, 2, 'A regular creative routine supports the final sentence.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-008', 'reading', 2, 'The town wanted more people to cycle to the centre. It created protected bike lanes on several busy roads. _____ Surveys later showed that new cyclists felt more confident using those routes.', '{"A":"Cyclists were asked to use only pavements.","B":"The roads were closed to bicycles.","C":"All traffic signs were removed.","D":"The lanes separated cyclists from faster traffic."}'::jsonb, 3, 'Protected separation from traffic explains increased confidence.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-009', 'reading', 1, 'I often forgot new vocabulary after learning it once. _____ Reviewing words at increasing intervals helped me remember them much longer.', '{"A":"Then I tried spaced repetition.","B":"So I stopped learning languages.","C":"Nevertheless, I threw away my notes.","D":"For example, I avoided old words completely."}'::jsonb, 0, 'Spaced repetition is directly explained in the next sentence.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-010', 'reading', 2, 'A local shop began offering online ordering for customers who were short on time. _____ Customers could then collect their purchases on the way home.', '{"A":"The shop stopped selling products.","B":"Orders were prepared before the customer arrived.","C":"Customers had to wait longer than before by design.","D":"The collection desk opened only once a year."}'::jsonb, 1, 'Prepared orders make convenient collection possible.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-011', 'reading', 3, 'Students sometimes highlight almost every line of a textbook because everything seems important. _____ A better strategy is to identify the central idea first and mark only information that supports it.', '{"A":"This removes the need to understand the text.","B":"This always guarantees perfect memory.","C":"This can make the highlighting less useful.","D":"This makes every textbook shorter."}'::jsonb, 2, 'If everything is highlighted, the method loses its ability to show what matters.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-012', 'reading', 2, 'The weather forecast predicted heavy rain during our trip. We did not cancel the walk. _____ In the end, we stayed dry enough to enjoy the day.', '{"A":"As a result, we forgot to check the weather.","B":"Therefore, we left all rain protection at home.","C":"However, we chose the longest exposed route possible.","D":"Instead, we packed waterproof jackets and changed the route."}'::jsonb, 3, 'Preparing for rain explains why the walk still worked.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-013', 'reading', 1, 'The library created a shelf called ''Staff Picks''. Each recommendation included two short sentences about the book. _____ Many visitors said the notes helped them choose faster.', '{"A":"The notes focused on what kind of reader might enjoy it.","B":"The books were hidden from visitors.","C":"The shelf contained no titles.","D":"The staff refused to describe any book."}'::jsonb, 0, 'Useful reader-focused notes logically help visitors choose.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-014', 'reading', 2, 'Emma wanted to spend less time checking her phone while studying. She placed it in another room for thirty minutes at a time. _____ She found it easier to concentrate because notifications no longer interrupted her.', '{"A":"She kept every notification at maximum volume.","B":"She checked messages during each break instead.","C":"She opened social media on another device continuously.","D":"She stopped taking any study breaks."}'::jsonb, 1, 'Checking messages during planned breaks supports fewer interruptions while studying.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-015', 'reading', 3, 'A team kept making the same small mistakes during a project. Instead of blaming individuals, they held a short review after each stage. _____ Over time, repeated errors became less common.', '{"A":"They made the process more confusing on purpose.","B":"They agreed never to discuss mistakes.","C":"They recorded what went wrong and changed the process.","D":"They removed all deadlines and responsibilities."}'::jsonb, 2, 'Identifying causes and changing the process explains fewer repeated errors.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-016', 'reading', 2, 'The community centre offered a free trial week for its fitness classes. _____ Many participants later joined because they had discovered which class suited them best.', '{"A":"The centre closed during the trial week.","B":"Everyone had to buy a yearly membership first.","C":"Only professional athletes were admitted.","D":"People could try several different sessions before choosing."}'::jsonb, 3, 'Trying several classes explains better-informed membership choices.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-017', 'reading', 1, 'We arrived at the station earlier than necessary. _____ We had enough time to find the correct platform and buy water before boarding.', '{"A":"That turned out to be useful.","B":"As a result, we missed the train immediately.","C":"However, the station did not exist.","D":"Therefore, we went home without checking anything."}'::jsonb, 0, 'The next sentence lists benefits of arriving early.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-018', 'reading', 2, 'The teacher stopped giving one long vocabulary test at the end of each month. Instead, she used short weekly quizzes. _____ Students also received feedback sooner and could review weak words before the next quiz.', '{"A":"This made vocabulary disappear from the course.","B":"This encouraged more regular revision.","C":"This prevented students from seeing their mistakes.","D":"This meant students studied only once a month."}'::jsonb, 1, 'Frequent quizzes naturally encourage regular revision and faster feedback.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-019', 'reading', 3, 'A company asked customers why they abandoned an online order. Many said the checkout required too many steps. _____ Completion rates improved soon after.', '{"A":"The company hid the final price until after payment.","B":"The company added several extra pages to checkout.","C":"The company simplified the form and removed unnecessary fields.","D":"The company stopped listening to customer feedback."}'::jsonb, 2, 'Simplifying the checkout directly addresses the reported problem.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T4-020', 'reading', 2, 'My first attempt at baking bread was disappointing because I cut it immediately after it came out of the oven. _____ The next loaf had a much better texture.', '{"A":"Then I placed the dough in the freezer before baking.","B":"The second time, I used no flour at all.","C":"After that, I stopped using an oven.","D":"The second time, I let it cool before slicing it."}'::jsonb, 3, 'Letting bread cool before slicing explains the improved texture.', 'Reading', 'Reading: Gapped Text', 'NMT', true, false, 'Task 4', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-001', 'use_of_english', 1, 'The new study room is usually quiet, so it is a good place to _____ on difficult homework.', '{"A":"concentrate","B":"celebrate","C":"depend","D":"invite"}'::jsonb, 0, 'The natural collocation is ''concentrate on'' homework.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-002', 'use_of_english', 2, 'Please _____ attention to the instructions before you begin the task.', '{"A":"make","B":"pay","C":"do","D":"take"}'::jsonb, 1, 'The fixed collocation is ''pay attention''.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-003', 'use_of_english', 2, 'The organisers had to _____ the outdoor event because of the storm.', '{"A":"borrow","B":"solve","C":"cancel","D":"earn"}'::jsonb, 2, 'An event can be cancelled because of bad weather.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-004', 'use_of_english', 1, 'I was tired, but a short walk helped me _____ my energy.', '{"A":"replace","B":"refuse","C":"reduce","D":"regain"}'::jsonb, 3, '''Regain energy'' means get your energy back.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-005', 'use_of_english', 2, 'This app allows users to _____ their progress over several weeks.', '{"A":"track","B":"catch","C":"hold","D":"reach"}'::jsonb, 0, '''Track progress'' means monitor how it changes over time.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-006', 'use_of_english', 2, 'The teacher asked us to _____ an example from everyday life.', '{"A":"avoid","B":"provide","C":"remove","D":"divide"}'::jsonb, 1, '''Provide an example'' is the correct collocation.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-007', 'use_of_english', 3, 'The company decided to _____ feedback before changing the product.', '{"A":"achieve","B":"rise","C":"gather","D":"deliver"}'::jsonb, 2, 'Companies commonly ''gather feedback'' from users.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-008', 'use_of_english', 2, 'It took me a few days to _____ used to the new timetable.', '{"A":"bring","B":"make","C":"turn","D":"get"}'::jsonb, 3, 'The expression is ''get used to''.', 'Use of English', 'Vocabulary: Phrasal Verbs', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-009', 'use_of_english', 2, 'We were running _____ of time, so we skipped the final activity.', '{"A":"out","B":"off","C":"away","D":"over"}'::jsonb, 0, '''Run out of time'' means have almost no time left.', 'Use of English', 'Vocabulary: Phrasal Verbs', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-010', 'use_of_english', 1, 'The museum is within walking _____ of the station.', '{"A":"length","B":"distance","C":"space","D":"route"}'::jsonb, 1, 'The fixed phrase is ''within walking distance''.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-011', 'use_of_english', 3, 'The article _____ an important point about how habits are formed.', '{"A":"grows","B":"lifts","C":"raises","D":"builds"}'::jsonb, 2, 'We ''raise a point'' or ''raise an issue'' in discussion.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-012', 'use_of_english', 2, 'I did not recognise him at first because he had _____ his hairstyle completely.', '{"A":"moved","B":"turned","C":"exchanged","D":"changed"}'::jsonb, 3, '''Change your hairstyle'' is the natural verb choice.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-013', 'use_of_english', 2, 'The course is designed to _____ students with practical interview skills.', '{"A":"equip","B":"fill","C":"cover","D":"dress"}'::jsonb, 0, '''Equip someone with skills'' means give them the abilities they need.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-014', 'use_of_english', 3, 'The manager asked the team to _____ up with three possible solutions.', '{"A":"get","B":"come","C":"take","D":"put"}'::jsonb, 1, 'The phrasal verb is ''come up with'' an idea or solution.', 'Use of English', 'Vocabulary: Phrasal Verbs', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-015', 'use_of_english', 1, 'Make sure you _____ a copy of the file before editing it.', '{"A":"lend","B":"spend","C":"save","D":"accept"}'::jsonb, 2, 'You save a copy of a digital file.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-016', 'use_of_english', 2, 'The train was delayed, but we still arrived in _____ for the meeting.', '{"A":"season","B":"hour","C":"period","D":"time"}'::jsonb, 3, '''In time for'' means early enough not to miss something.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-017', 'use_of_english', 3, 'Her explanation was clear and _____, so everyone understood the main idea quickly.', '{"A":"concise","B":"crowded","C":"ordinary","D":"patient"}'::jsonb, 0, '''Concise'' means brief but clear, fitting the context.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-018', 'use_of_english', 2, 'The website lets you _____ the results by price, date or rating.', '{"A":"pour","B":"filter","C":"spread","D":"press"}'::jsonb, 1, 'Digital results can be filtered using criteria.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-019', 'use_of_english', 2, 'The project was more difficult than expected, but the team managed to _____ it through.', '{"A":"watch","B":"look","C":"see","D":"notice"}'::jsonb, 2, '''See something through'' means continue until it is completed.', 'Use of English', 'Vocabulary: Phrasal Verbs', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T5-020', 'use_of_english', 3, 'Regular practice can make a noticeable _____ to your confidence when speaking.', '{"A":"division","B":"changeover","C":"distance","D":"difference"}'::jsonb, 3, 'The fixed phrase is ''make a difference''.', 'Use of English', 'Vocabulary: Collocations', 'NMT', true, false, 'Task 5', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-001', 'use_of_english', 1, 'I _____ this book last week and finished it yesterday.', '{"A":"bought","B":"have bought","C":"buy","D":"had buy"}'::jsonb, 0, 'A finished past time (''last week'') requires Past Simple.', 'Use of English', 'Grammar: Tenses', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-002', 'use_of_english', 2, 'By the time we arrived, the film _____.', '{"A":"has started","B":"had started","C":"starts","D":"was start"}'::jsonb, 1, 'Past Perfect describes an action completed before another past action.', 'Use of English', 'Grammar: Tenses', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-003', 'use_of_english', 1, 'If it _____ tomorrow, we will move the event indoors.', '{"A":"rained","B":"will rain","C":"rains","D":"would rain"}'::jsonb, 2, 'First Conditional uses Present Simple in the if-clause.', 'Use of English', 'Grammar: Conditionals', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-004', 'use_of_english', 2, 'If I _____ more free time, I would join the course.', '{"A":"would have","B":"have","C":"will have","D":"had"}'::jsonb, 3, 'Second Conditional uses Past Simple after ''if''.', 'Use of English', 'Grammar: Conditionals', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-005', 'use_of_english', 3, 'If they had checked the address, they _____ the wrong building.', '{"A":"would not have visited","B":"will not visit","C":"did not visit","D":"would not visit"}'::jsonb, 0, 'Third Conditional uses would have + past participle for the result.', 'Use of English', 'Grammar: Conditionals', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-006', 'use_of_english', 1, 'You _____ wear a helmet on this construction site. It is compulsory.', '{"A":"might","B":"must","C":"could","D":"would"}'::jsonb, 1, '''Must'' expresses a strong rule or obligation.', 'Use of English', 'Grammar: Modal Verbs', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-007', 'use_of_english', 2, 'You _____ have called a taxi; the station is only five minutes away.', '{"A":"couldn''t","B":"mustn''t","C":"needn''t","D":"wouldn''t"}'::jsonb, 2, '''Needn''t have'' means the action was unnecessary, though it happened.', 'Use of English', 'Grammar: Modal Verbs', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-008', 'use_of_english', 1, 'She is _____ engineer who works for a renewable-energy company.', '{"A":"—","B":"a","C":"the","D":"an"}'::jsonb, 3, '''Engineer'' begins with a vowel sound, so the indefinite article is ''an''.', 'Use of English', 'Grammar: Mixed', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-009', 'use_of_english', 2, 'This is the café _____ we first met.', '{"A":"where","B":"which","C":"who","D":"whose"}'::jsonb, 0, '''Where'' refers to the place in which something happened.', 'Use of English', 'Grammar: Mixed', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-010', 'use_of_english', 2, 'The new bridge _____ next year if the project stays on schedule.', '{"A":"will complete","B":"will be completed","C":"completed","D":"has completing"}'::jsonb, 1, 'Future passive is ''will be + past participle''.', 'Use of English', 'Grammar: Passive & Reported Speech', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-011', 'use_of_english', 2, 'He said that he _____ the report the following day.', '{"A":"finishes","B":"will finish","C":"would finish","D":"has finished"}'::jsonb, 2, 'In reported speech, future ''will'' commonly shifts to ''would''.', 'Use of English', 'Grammar: Passive & Reported Speech', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-012', 'use_of_english', 1, 'I enjoy _____ new places on foot when I travel.', '{"A":"explored","B":"to explore always","C":"explore","D":"exploring"}'::jsonb, 3, '''Enjoy'' is followed by a gerund (-ing form).', 'Use of English', 'Grammar: Gerund & Infinitive', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-013', 'use_of_english', 2, 'We decided _____ the earlier train to avoid traffic.', '{"A":"to take","B":"taking","C":"take","D":"taken"}'::jsonb, 0, '''Decide'' is followed by the infinitive with ''to''.', 'Use of English', 'Grammar: Gerund & Infinitive', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-014', 'use_of_english', 3, 'Hardly _____ the presentation when the internet connection failed.', '{"A":"we had started","B":"had we started","C":"did we start","D":"we started"}'::jsonb, 1, 'After ''Hardly'' at the beginning, inversion is used: ''Hardly had we started...''', 'Use of English', 'Grammar: Mixed', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-015', 'use_of_english', 2, 'There are _____ students in the room today than yesterday.', '{"A":"few","B":"less","C":"fewer","D":"little"}'::jsonb, 2, '''Students'' is countable, so the comparative is ''fewer''.', 'Use of English', 'Grammar: Mixed', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-016', 'use_of_english', 2, 'She has lived here _____ 2022.', '{"A":"from","B":"for","C":"during","D":"since"}'::jsonb, 3, '''Since'' introduces the starting point of an action continuing to the present.', 'Use of English', 'Grammar: Tenses', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-017', 'use_of_english', 1, 'Neither Tom nor his friends _____ available this evening.', '{"A":"are","B":"is","C":"be","D":"was"}'::jsonb, 0, 'With ''neither...nor'', agreement normally follows the nearer subject, ''friends''.', 'Use of English', 'Grammar: Mixed', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-018', 'use_of_english', 3, 'I wish I _____ so much time on my phone yesterday.', '{"A":"didn''t spend","B":"hadn''t spent","C":"wouldn''t spend","D":"haven''t spent"}'::jsonb, 1, 'A regret about the past after ''wish'' uses Past Perfect.', 'Use of English', 'Grammar: Tenses', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-019', 'use_of_english', 2, 'The task was _____ difficult that several students asked for extra time.', '{"A":"too","B":"such","C":"so","D":"enough"}'::jsonb, 2, 'The structure is ''so + adjective + that''.', 'Use of English', 'Grammar: Mixed', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

INSERT INTO public.questions (question_code, topic, difficulty, question_text, options, correct_option, explanation, category, sub_category, section, is_active, is_diagnostic, nmt_task_type, content_pack, quality_status) VALUES ('N14-T6-020', 'use_of_english', 2, 'Not only _____ the answer, but she also explained why it was correct.', '{"A":"she did know","B":"she knew","C":"knew she","D":"did she know"}'::jsonb, 3, 'After initial ''Not only'', subject–auxiliary inversion is required.', 'Use of English', 'Grammar: Mixed', 'NMT', true, false, 'Task 6', 'v1.4-nmt2026-pack1', 'approved')
ON CONFLICT (question_code) DO UPDATE SET
  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,
  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,
  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,
  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;

-- Verification
SELECT nmt_task_type, count(*) AS questions FROM public.questions WHERE content_pack='v1.4-nmt2026-pack1' GROUP BY nmt_task_type ORDER BY nmt_task_type;
SELECT count(*) AS total_pack_questions FROM public.questions WHERE content_pack='v1.4-nmt2026-pack1';
