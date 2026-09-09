from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "content"
OUT.mkdir(exist_ok=True)

PACK = "v1.7-nmt2026-pack4"
items = []


def arranged(correct: str, distractors: list[str], index: int):
    pos = (index - 1) % 4
    opts = list(distractors[:3])
    opts.insert(pos, correct)
    return {letter: value for letter, value in zip("ABCD", opts)}, pos


def add(code, task, category, sub_category, difficulty, question, correct, distractors, index, explanation):
    options, correct_option = arranged(correct, distractors, index)
    items.append(
        {
            "question_code": code,
            "topic": "reading" if category == "Reading" else "use_of_english",
            "difficulty": difficulty,
            "question_text": question,
            "options": options,
            "correct_option": correct_option,
            "explanation": explanation,
            "category": category,
            "sub_category": sub_category,
            "section": "NMT",
            "is_active": True,
            "is_diagnostic": False,
            "nmt_task_type": task,
            "content_pack": PACK,
            "quality_status": "approved",
        }
    )


# Task 1 — matching short notices with the most suitable person.
task1 = [
    ("WEEKEND STUDY ROOM: Quiet desks, reliable Wi-Fi and charging points. No group conversations in the room.", "A student who needs a silent place to work for several hours", ["A group wanting to rehearse a presentation aloud", "Someone looking for a sports activity", "A learner who needs one-to-one grammar lessons"], 1),
    ("BIKE CHECK MORNING: Volunteers will inspect brakes, tyres and lights. Minor adjustments are free; no major repairs.", "Someone who wants a basic safety check before cycling regularly", ["Someone needing a broken bicycle frame replaced", "A person wanting to rent a bicycle for a month", "A beginner looking for cycling lessons"], 1),
    ("CV EXPRESS CLINIC: Bring a one-page CV and a vacancy you like. A mentor will suggest focused improvements in 20 minutes.", "A student preparing an application for a specific job", ["Someone who wants a complete career-change course", "A learner seeking help with a school essay", "A person who has not decided what kind of work interests them"], 2),
    ("CITY SKETCH WALK: Bring a pencil and small notebook. We stop at four locations and draw quick five-minute scenes. Beginners welcome.", "Someone who wants informal outdoor drawing practice", ["An experienced painter looking for studio space", "A tourist wanting a guided bus tour", "Someone who needs professional design software training"], 1),
    ("SPEAK & SWAP: Practise English in pairs for ten minutes, then change partners. Conversation cards are provided.", "A learner who wants several short speaking conversations", ["Someone looking for a long private lesson", "A student who only wants writing correction", "A person searching for a silent reading club"], 1),
    ("PHONE PHOTOGRAPHY AT NIGHT: Learn exposure, focus and composition after sunset. A smartphone with manual controls is recommended.", "Someone interested in improving evening photos on a phone", ["A person who wants to buy a professional camera", "Someone needing daytime passport photos", "A beginner who does not own any phone or camera"], 2),
    ("ONE-HOUR MEAL PREP: Prepare three simple lunches using inexpensive ingredients. Containers are provided.", "Someone who wants to organise cheap lunches for several days", ["A guest looking for a formal restaurant meal", "Someone wanting an advanced baking course", "A person who needs food delivered immediately"], 1),
    ("FIRST AID THEORY SESSION: Learn how to recognise common emergencies and when to call professional help. Demonstration only; no certification.", "Someone who wants introductory safety knowledge without a qualification", ["A worker who needs an official first-aid certificate", "Someone seeking hospital treatment", "A student wanting a sports fitness test"], 2),
    ("PORTFOLIO REVIEW DESK: Show up to five design projects. A tutor will comment on presentation, sequence and clarity.", "A design student who already has work and wants feedback on how to present it", ["A beginner wanting to learn drawing from zero", "Someone who needs a website coded for them", "A person looking for printing services only"], 2),
    ("BEGINNER BADMINTON: Rackets available. The first 20 minutes cover rules and basic shots, followed by friendly games.", "Someone new to badminton who wants a relaxed introduction", ["An advanced player preparing for a tournament", "Someone looking for solo gym training", "A spectator who only wants to watch professional matches"], 1),
    ("DIGITAL DECLUTTER HOUR: Learn a simple folder system and remove duplicate files from your laptop. Bring your own device.", "Someone whose computer files have become difficult to organise", ["A person needing a laptop hardware repair", "Someone wanting to learn advanced programming", "A student who only uses paper notes"], 1),
    ("MINI DEBATE LAB: Teams receive a topic, ten minutes to prepare and two minutes each to speak. Feedback focuses on clear arguments.", "A learner who wants practice forming arguments quickly", ["Someone who wants to memorise a long speech", "A person looking for quiet independent reading", "A beginner wanting pronunciation drills only"], 2),
    ("BUDGET BASICS FOR STUDENTS: Track one week of spending and build three simple categories for the next week. No banking products are sold.", "A student who wants a simple way to control everyday spending", ["An investor seeking complex market analysis", "Someone who wants a bank loan", "A person needing accounting certification"], 1),
    ("LOCAL HISTORY AUDIO WALK: Download the free route before arrival. The walk takes about 70 minutes and can be completed at your own pace.", "Someone who wants a flexible self-guided walk with historical information", ["A visitor who wants a guide beside them at all times", "Someone looking for an indoor lecture only", "A runner wanting a competitive race"], 2),
    ("GRAMMAR ERROR CLINIC: Bring five sentences you are unsure about. A tutor will explain the patterns behind the mistakes.", "A learner who wants targeted explanations of recurring grammar errors", ["Someone wanting a full beginner course", "A student who needs a text translated", "A person seeking only vocabulary flashcards"], 1),
    ("PRESENTATION REHEARSAL BOOTH: Practise a five-minute talk, receive two audience questions and review your timing.", "Someone who wants to practise handling questions after a short presentation", ["A student who needs someone else to write the presentation", "A person wanting to learn video editing", "Someone looking for a long academic lecture"], 2),
    ("REPAIR CAFÉ: Bring a small household item that has stopped working. Volunteers will help you diagnose simple faults; spare parts are not guaranteed.", "Someone who wants help understanding a simple problem with a small device", ["A customer demanding a guaranteed professional repair", "Someone wanting to buy new appliances", "A person needing a car engine repaired"], 2),
    ("READING SPRINT: Choose any book, silence your phone and read for 40 minutes. The final ten minutes are for optional discussion.", "Someone who struggles to create uninterrupted reading time", ["A learner wanting a teacher-led literature class", "A person needing a book delivered", "Someone looking for a noisy social event"], 1),
    ("INTERVIEW ROLE-PLAY: Practise common job-interview questions with another participant. Bring the vacancy description if possible.", "Someone who wants realistic practice before a job interview", ["A manager looking to recruit employees", "A student needing a CV printed", "A person who wants general conversation with no work focus"], 2),
    ("BEGINNER SPREADSHEET LAB: Enter data, use SUM and AVERAGE, and create one simple chart. Laptops are available.", "A student who needs basic spreadsheet skills for a simple project", ["An analyst needing advanced database training", "Someone wanting to repair a laptop", "A person looking for a graphic-design workshop"], 1),
]
for i, (notice, correct, distractors, diff) in enumerate(task1, 1):
    add(f"N17-T1-{i:03d}", "Task 1", "Reading", "Reading: Notices", diff,
        "Read the notice and choose the person it is most suitable for.\n\n" + notice,
        correct, distractors, i,
        "The correct option matches the purpose and practical details of the notice.")


# Task 2 — short reading comprehension with one correct option.
task2 = [
    ("When our school introduced a shared online calendar, teachers expected students to check it every morning. At first, many still relied on screenshots sent by friends. After reminders were added automatically, missed deadlines fell noticeably.", "What helped reduce missed deadlines?", "Automatic reminders connected to the calendar", ["Replacing the calendar with paper notices", "Allowing students to submit work without deadlines", "Asking friends to send more screenshots"], 1),
    ("I started taking the bus to college because it was cheaper than travelling by car. The journey is longer, but I use the extra time to review vocabulary. As a result, the commute no longer feels wasted.", "Why is the writer now more positive about the bus journey?", "The travel time has become useful for studying", ["The bus has become faster than driving", "The ticket price increased", "The writer no longer studies vocabulary"], 1),
    ("The community garden originally planned to open every evening. Volunteers soon realised that most visitors came on Saturday mornings, while weekday attendance was low. They changed the schedule and used the saved time for maintenance.", "Why was the opening schedule changed?", "Visitor numbers were much higher at a different time", ["The garden needed to close permanently", "Volunteers wanted to stop doing maintenance", "Saturday visits were causing complaints"], 2),
    ("Marta used to rewrite every page of her notes before an exam. It felt productive, but she rarely tested whether she could recall the ideas. This term she replaced much of the rewriting with short self-quizzes and found gaps in her knowledge earlier.", "What change did Marta make?", "She began checking what she could remember instead of mostly copying notes", ["She stopped revising before exams", "She started writing longer notes", "She only studied material she already knew"], 2),
    ("A small café tested a discount for customers who brought reusable cups. The number of reusable cups increased, but staff also noticed that the discount slowed payment at busy times. They kept the idea but changed it to a simple loyalty stamp.", "Why did the café modify the original scheme?", "It created delays during busy periods", ["Customers refused to use reusable cups", "The café wanted to end all environmental measures", "The cups became more expensive to wash"], 2),
    ("The museum's new app does not try to describe every object. Instead, visitors choose one of three short routes: design, everyday life or technology. Each route highlights only a small number of exhibits.", "What is the main idea behind the app?", "It offers focused routes based on visitors' interests", ["It replaces all information in the museum", "It requires visitors to see every exhibit", "It is designed only for museum staff"], 1),
    ("Our group planned to record a twenty-minute podcast in one take. During the first attempt, small mistakes forced us to restart several times. We later recorded the episode in shorter sections, which made editing much easier.", "What did the group learn?", "Recording in smaller parts was more practical", ["Editing should be avoided completely", "Long recordings never contain mistakes", "The podcast needed to be twice as long"], 1),
    ("Leo chose an online course because it promised flexible study. He was surprised to discover that flexibility still required planning: without fixed lesson times, he often postponed tasks. Setting his own weekly deadline solved most of the problem.", "What difficulty did Leo experience?", "He delayed work when there was no fixed schedule", ["The course had too many compulsory meetings", "He could not access the lessons online", "His weekly deadline made him study less"], 2),
    ("The first version of our survey asked students whether the library was 'good'. The answers were not very useful because people interpreted 'good' differently. We replaced the question with separate items about opening hours, noise and available desks.", "Why were the survey questions changed?", "The original wording was too vague", ["Students refused to answer any questions", "The library had changed its opening hours", "The survey contained too many specific details"], 2),
    ("A local running club noticed that new members often stopped attending after one session. Experienced runners were friendly, but the pace was too fast for beginners. The club added a separate first-month group, and more newcomers stayed.", "What most likely improved newcomer retention?", "A group with a more suitable pace for beginners", ["Longer races for experienced runners", "Fewer opportunities to meet other runners", "Removing all organised sessions"], 1),
    ("Nadia wanted to improve her English listening, so she chose very difficult podcasts. She understood almost nothing and quickly lost motivation. Her teacher suggested material where she could follow the main idea while still meeting some new language.", "What was the teacher's advice?", "Use material that is challenging but still mostly understandable", ["Avoid listening practice until vocabulary is perfect", "Choose only the most difficult podcasts available", "Translate every sentence before listening"], 2),
    ("The school newspaper published articles only at the end of each month. Students said they often forgot to submit ideas because the deadline felt distant. The editors introduced a short weekly planning meeting, which produced a steadier flow of stories.", "What problem did the weekly meetings address?", "Students were not contributing ideas consistently", ["Articles were too short to publish", "The newspaper had too many editors", "Students wanted fewer opportunities to write"], 2),
    ("A study app introduced a badge for completing seven days in a row. Usage rose at first, but some learners stopped completely after missing one day. The developers later allowed a missed day without resetting the whole streak.", "Why was the streak system changed?", "A single missed day discouraged some users from continuing", ["Badges made every learner study less", "Users wanted the app to remove all progress tracking", "Seven days was too short to earn any badge"], 2),
    ("The volunteer team had always collected donations in cash. At a crowded event, counting and storing the money became difficult. They added a digital payment option, not to eliminate cash, but to reduce pressure at busy times.", "What was the purpose of adding digital payments?", "To make handling donations easier when many people arrived", ["To prevent anyone from donating cash", "To increase ticket prices", "To replace the volunteer team"], 1),
    ("I used to practise presentations by reading my slides aloud. My teacher pointed out that the audience could read the slides themselves. I began using the slides only as visual support and spent more time explaining examples.", "How did the writer change the presentation style?", "The writer stopped treating the slide text as the full speech", ["The writer added more text to every slide", "The writer stopped using examples", "The writer asked the audience to read silently throughout"], 2),
    ("A second-hand bookshop began posting photos of new arrivals online. Customers started reserving books before visiting, which helped sales. However, staff now update the post immediately when a book is sold so people do not travel for something unavailable.", "Why do staff update posts quickly?", "To prevent customers from expecting books that have already been sold", ["To stop customers from making reservations", "To make the shop harder to find", "To reduce the number of new arrivals"], 1),
    ("Our class created a shared document for a group report. At first everyone edited the same paragraph at once, creating confusion. We then assigned each person a section and used comments for suggestions across sections.", "What solved the editing problem?", "Giving people clear responsibility for different sections", ["Deleting the shared document", "Allowing only one person to contribute ideas", "Removing all comments from the document"], 1),
    ("The language club tried holding meetings at 8 a.m., assuming students preferred to meet before lessons. Attendance was poor. A quick poll showed that most members travelled a long distance, so the club moved meetings to late afternoon.", "What information caused the schedule change?", "Many members could not easily arrive early", ["Students wanted meetings to be shorter", "The club had no afternoon rooms", "Morning meetings were too popular"], 1),
    ("A charity's website had a long page explaining its work, but few visitors reached the donation button at the bottom. The team shortened the introduction and moved one clear action button near the top. Donations increased without changing the campaign itself.", "What does the example suggest?", "Making the main action easier to find can affect results", ["Visitors always prefer longer explanations", "The campaign needed a completely different purpose", "Donation buttons work only at the bottom of a page"], 2),
    ("When I first learned to cook, I followed recipes without preparing ingredients in advance. I often discovered halfway through that something was missing. Now I read the full recipe first and put everything on the counter before starting.", "What habit helped the writer avoid interruptions?", "Checking the whole recipe and preparing ingredients first", ["Cooking without any recipe", "Buying ingredients after cooking begins", "Choosing recipes with more steps"], 1),
]
for i, (text, q, correct, distractors, diff) in enumerate(task2, 1):
    add(f"N17-T2-{i:03d}", "Task 2", "Reading", "Reading: Multiple Choice", diff,
        f"Read the text and answer the question.\n\n{text}\n\n{q}", correct, distractors, i,
        "The correct answer is supported directly by the main idea or cause-and-effect relationship in the text.")


# Task 3 — matching situations to services/activities.
task3 = [
    ("You understand grammar rules but freeze when you have to answer quickly in conversation.", "Timed speaking practice with rotating partners", ["Silent reading room", "Essay formatting service", "Beginner coding workshop"], 1),
    ("You have several university deadlines in the same week and need to decide what to do first.", "Priority-planning session", ["Photography walk", "Pronunciation club", "Book exchange"], 1),
    ("You want feedback on whether your CV matches one particular vacancy.", "Vacancy-focused CV review", ["General career lecture", "Creative writing circle", "Computer repair desk"], 2),
    ("Your phone photos look blurry indoors and you want to understand why.", "Low-light smartphone photography workshop", ["Outdoor running club", "Spreadsheet basics class", "Library membership desk"], 1),
    ("You keep forgetting new English words even though you copy long vocabulary lists.", "Vocabulary-in-context practice session", ["Public speaking competition", "Laptop cleaning service", "Tourist information desk"], 2),
    ("You want to practise answering unexpected questions after presenting a project.", "Presentation Q&A rehearsal", ["Poster printing service", "Quiet study hour", "Beginner chess tournament"], 2),
    ("You need a calm place with Wi-Fi to study but do not want group discussion around you.", "Silent study workspace", ["Conversation café", "Team brainstorming room", "Music rehearsal studio"], 1),
    ("You want to find out where your money goes each week without learning complex finance.", "Student budget basics session", ["Advanced investment seminar", "Job interview role-play", "Language exchange"], 1),
    ("You have an old lamp that stopped working and want help identifying a simple fault before replacing it.", "Community repair café", ["Interior design consultation", "Book club", "Running assessment"], 2),
    ("You want to become more confident using SUM, AVERAGE and simple charts for school data.", "Beginner spreadsheet lab", ["Advanced programming bootcamp", "Debate club", "CV review desk"], 1),
    ("You want to walk around the city and learn history without having to stay with a group.", "Self-guided audio history route", ["Coach-led running session", "Live theatre workshop", "Grammar clinic"], 1),
    ("You know what you want to say in an essay, but your paragraphs do not connect clearly.", "Writing cohesion clinic", ["Pronunciation drill", "Photo editing workshop", "Bike safety check"], 2),
    ("You are new to badminton and want to learn the basic rules before playing relaxed games.", "Beginner badminton evening", ["Competitive tennis league", "Solo weight-training plan", "Sports photography class"], 1),
    ("You want to improve a five-minute talk by checking its timing and clarity.", "Short-presentation rehearsal booth", ["Long-form writing workshop", "Museum audio tour", "Digital declutter clinic"], 1),
    ("Your laptop is full of duplicate files and inconsistent folders, but the hardware works fine.", "Digital file organisation session", ["Laptop repair service", "Photography basics", "Job-search workshop"], 1),
    ("You want to test whether you truly remember a topic instead of just rereading it.", "Active-recall study workshop", ["Silent reading club", "Film discussion group", "Basic budgeting desk"], 2),
    ("You want to prepare three simple lunches for the week without spending much.", "Low-cost meal-prep class", ["Fine-dining tasting event", "Advanced pastry course", "City walking tour"], 1),
    ("You need short feedback on repeated grammar mistakes in sentences you wrote yourself.", "Targeted grammar error clinic", ["Full translation service", "Beginner sports class", "Web-design course"], 1),
    ("You are applying for your first job and want realistic practice answering common interview questions.", "Job interview role-play", ["Academic lecture", "Book swap", "Photo editing lab"], 1),
    ("You want to focus on reading for forty minutes without phone distractions.", "Reading sprint session", ["Group debate", "Conversation exchange", "Spreadsheet tutorial"], 1),
]
for i, (situation, correct, distractors, diff) in enumerate(task3, 1):
    add(f"N17-T3-{i:03d}", "Task 3", "Reading", "Reading: Situations", diff,
        "Choose the best service or activity for the situation.\n\n" + situation,
        correct, distractors, i,
        "The correct service matches both the learner's goal and the format they need.")


# Task 4 — gapped text / cohesion.
task4 = [
    ("I had planned to study for three hours without stopping. _____. After that, I switched to shorter blocks with small breaks and found it easier to stay focused.", "By the end of the first hour, my attention had already dropped", ["The library was closed for the whole month", "My teacher cancelled the exam completely", "The subject suddenly became much easier"], 1),
    ("Our first poster contained five different fonts and several long paragraphs. _____. We simplified the design and people could understand the message much faster.", "A quick test showed that readers did not know where to look first", ["The printer produced more copies than expected", "We decided to make every paragraph longer", "The event was moved to another city"], 2),
    ("Danylo always checked the total score after a practice test but ignored individual mistakes. _____. Once he began reviewing the reason for each error, the same mistakes appeared less often.", "That made it difficult to see what he actually needed to improve", ["His scores were automatically deleted", "He stopped taking practice tests forever", "The questions became shorter every week"], 2),
    ("The club wanted more students to attend its meetings. _____. Attendance improved after the time was moved to just after classes.", "A short poll revealed that the original evening slot was inconvenient", ["The club removed all announcements", "Students asked for meetings to start at midnight", "The room became smaller"], 1),
    ("I used to open my messages every time the phone vibrated while I was studying. _____. Putting the device in another room removed most of those interruptions.", "Even a quick check often turned into several minutes of distraction", ["My phone battery became larger", "The study material was printed in colour", "I bought a new desk lamp"], 1),
    ("The team assumed users understood the icon on the new website. _____. They added a short text label and the problem almost disappeared.", "Testing showed that many people clicked the wrong control", ["The website received no visitors at all", "The icon became physically larger on the server", "The team removed the navigation menu"], 2),
    ("Nina practised her speech alone until she could say every line from memory. _____. During a real rehearsal, one unexpected question made her lose her place.", "However, she had not practised responding flexibly", ["She had never written the speech", "The audience refused to ask questions", "Her presentation contained no words"], 2),
    ("The first version of our timetable looked perfect in a spreadsheet. _____. We added travel time between locations and had to move two activities.", "When we tested it in real life, one transition was impossible", ["Everyone asked for more spreadsheet columns", "The weather was sunny that week", "The timetable used only one font"], 2),
    ("I wanted to learn every unfamiliar word in an article before continuing. _____. Reading first for the main idea helped me finish texts without getting stuck.", "As a result, I spent too much time on words that were not essential", ["The articles contained no vocabulary", "My dictionary stopped working", "I stopped reading English completely"], 2),
    ("The organisers expected most participants to arrive gradually. _____. They opened a second registration desk to prevent a long queue.", "Instead, two buses arrived at almost the same time", ["No one attended the event", "The venue was cancelled the previous year", "Registration had been completed online for everyone"], 1),
    ("The class created a shared document for the report. _____. Assigning one section to each person made the final editing much clearer.", "At first, several people changed the same sentences at once", ["Nobody had access to the internet", "The report required no writing", "The teacher asked for an individual project"], 1),
    ("Our podcast sounded balanced through headphones. _____. We lowered the background music before publishing the final version.", "On a phone speaker, some words were difficult to hear", ["The episode had no recorded speech", "We decided to remove every microphone", "The headphones were too expensive"], 2),
    ("Sofiia kept postponing a large assignment because it felt too difficult to begin. _____. Completing the first small step made the rest of the work less intimidating.", "She finally divided the task into actions that could be finished in twenty minutes", ["The deadline was removed permanently", "She chose an even larger assignment", "The teacher completed the work for her"], 1),
    ("The article quoted several impressive numbers. _____. Before using them, we found the original report and checked how the data had been collected.", "However, it did not provide a clear source", ["The report contained no numbers", "We decided that evidence was unnecessary", "The article was written in large font"], 2),
    ("A new member joined our running group but struggled with the usual pace. _____. After we introduced a slower first-month session, more beginners kept attending.", "The problem was not motivation but the difficulty of the first experience", ["The club stopped accepting beginners", "Experienced runners began training even faster", "All sessions were moved online"], 2),
    ("The teacher marked every grammar error in my essay but did not always write the correction. _____. Finding the correct form myself helped me notice repeated patterns.", "Instead, the symbols in the margin showed what type of mistake I had made", ["The essay contained no grammar", "The teacher rewrote the entire essay", "I was told never to revise the text"], 3),
    ("We originally planned a thirty-question survey. _____. The shorter version produced more complete responses.", "After a pilot test, we removed questions that did not support the main research goal", ["We added fifty unrelated questions", "Participants asked for more complicated wording", "The research goal was cancelled"], 2),
    ("I thought I needed to feel motivated before beginning revision. _____. Now I start with a five-minute task, and motivation often appears after I have begun.", "Waiting for the right mood usually meant I delayed the work", ["Revision became impossible after five minutes", "My exam date changed every day", "I stopped using a calendar"], 1),
    ("The event page clearly listed the date and location, but few people registered. _____. Sign-ups increased once we explained what participants would actually do there.", "Visitors still could not tell why the event might be useful to them", ["The venue had become impossible to reach", "The date was hidden from visitors", "Registration was closed before the page was published"], 2),
    ("Maks copied every new expression into a notebook with a translation. _____. Adding one personal example sentence made the expressions easier to use later.", "He noticed that he could recognise many items but could not produce them in conversation", ["The notebook contained too few pages", "Translations became illegal at school", "He decided to learn no new expressions"], 2),
]
for i, (text, correct, distractors, diff) in enumerate(task4, 1):
    add(f"N17-T4-{i:03d}", "Task 4", "Reading", "Reading: Gapped Text", diff,
        "Choose the sentence that best completes the text.\n\n" + text,
        correct, distractors, i,
        "The correct sentence creates the strongest logical connection between the ideas before and after the gap.")


# Task 5 — grammar cloze.
task5 = [
    ("By the time we reached the station, the train _____.", "had left", ["has left", "leaves", "was leave"], 2, "Grammar: Tenses", "Past Perfect shows that the train left before another past event."),
    ("If I _____ more time yesterday, I would have checked the final paragraph again.", "had had", ["have", "would have", "had"], 3, "Grammar: Conditionals", "Third Conditional uses if + Past Perfect for an unreal past condition."),
    ("The results _____ on the school website tomorrow morning.", "will be published", ["will publish", "are publishing by", "have published"], 2, "Grammar: Passive Voice", "The results receive the action, so a future passive form is required."),
    ("She avoided _____ her phone while she was revising.", "checking", ["to check", "check", "to checking"], 1, "Grammar: Gerund / Infinitive", "Avoid is followed by a gerund."),
    ("The student _____ presentation won the competition thanked the whole team.", "whose", ["who", "which", "whom"], 2, "Grammar: Relative Clauses", "Whose expresses possession before the noun presentation."),
    ("You _____ submit the form today; the deadline has been extended until Friday.", "don't have to", ["mustn't", "can't to", "shouldn't have"], 1, "Grammar: Modal Verbs", "Don't have to expresses lack of necessity."),
    ("I have been interested in design _____ I was at primary school.", "since", ["for", "during", "from"], 1, "Grammar: Prepositions", "Since introduces the starting point of an action or state continuing to the present."),
    ("There are _____ students in the library today than there were yesterday.", "fewer", ["less", "fewest", "little"], 1, "Grammar: Quantifiers", "Fewer is used with plural countable nouns."),
    ("He said that he _____ the document the previous evening.", "had finished", ["has finished", "finishes", "will finish"], 2, "Grammar: Reported Speech", "An action completed before the reported past moment is commonly backshifted to Past Perfect."),
    ("This is _____ route to the city centre during rush hour.", "the quickest", ["quicker", "quickest than", "more quickest"], 1, "Grammar: Comparatives", "The superlative is required when selecting one route as the highest degree in a group."),
    ("I'd rather you _____ me before changing the shared file.", "asked", ["ask", "will ask", "have asking"], 3, "Grammar: Verb Patterns", "Would rather + subject commonly uses a past form for a present or future preference."),
    ("Rarely _____ such a clear explanation of this rule.", "have I heard", ["I have heard", "did I heard", "I heard have"], 3, "Grammar: Inversion", "A negative-frequency adverb at the beginning triggers subject-auxiliary inversion."),
    ("I _____ for this exam all week, so I am taking a short break tonight.", "have been studying", ["study yesterday", "am studied", "had study"], 2, "Grammar: Tenses", "Present Perfect Continuous describes an activity continuing over a period up to now."),
    ("Unless you _____ your email address correctly, you will not receive the confirmation.", "enter", ["will enter", "entered", "would enter"], 2, "Grammar: Conditionals", "Unless takes a present form when referring to a real future condition."),
    ("The classroom needs _____ before the next group arrives.", "cleaning", ["to cleaning", "clean", "cleaned it"], 3, "Grammar: Gerund / Infinitive", "Need + gerund can have a passive meaning: the classroom needs to be cleaned."),
    ("The teacher to _____ I spoke recommended a different book.", "whom", ["whose", "which", "where"], 3, "Grammar: Relative Clauses", "Whom can follow a preposition when referring to a person as the object."),
    ("You _____ have checked the attachment before sending the email.", "should", ["can", "must to", "need"], 2, "Grammar: Modal Verbs", "Should have + past participle expresses criticism or regret about a past action."),
    ("We arrived _____ the airport earlier than expected.", "at", ["in", "on", "to"], 1, "Grammar: Prepositions", "Arrive at is used for specific places such as an airport or station."),
    ("_____ of the two proposals fully solves the problem.", "Neither", ["None", "Any", "Much"], 2, "Grammar: Quantifiers", "Neither refers to not one and not the other of two items."),
    ("She asked me whether I _____ free the following day.", "would be", ["will be", "am", "have been"], 2, "Grammar: Reported Speech", "Would expresses future in the past in reported speech."),
]
for i, (q, correct, distractors, diff, sub, exp) in enumerate(task5, 1):
    add(f"N17-T5-{i:03d}", "Task 5", "Use of English", sub, diff, q, correct, distractors, i, exp)


# Task 6 — vocabulary, collocations, phrasal verbs and word formation.
task6 = [
    ("The new rule will come into _____ at the beginning of October.", "effect", ["result", "action", "work"], 2, "Vocabulary: Collocations", "Come into effect means begin to apply officially."),
    ("I need to _____ up on the vocabulary from last term before the test.", "brush", ["wipe", "turn", "make"], 2, "Vocabulary: Phrasal Verbs", "Brush up on means refresh or improve knowledge you already had."),
    ("The instructions were clear and _____, so we finished the setup quickly.", "practical", ["practice", "practically", "practise"], 1, "Vocabulary: Word Formation", "An adjective is needed to describe the instructions."),
    ("After a long discussion, the group finally reached an _____.", "agreement", ["agree", "agreeable", "agreed"], 1, "Vocabulary: Word Formation", "A noun is required after an."),
    ("You should take travel time into _____ when planning the day.", "account", ["notice", "mindly", "thought"], 2, "Vocabulary: Collocations", "Take something into account means consider it."),
    ("We ran _____ of time and had to leave the final question unanswered.", "out", ["off", "away", "down"], 1, "Vocabulary: Phrasal Verbs", "Run out of means have no more of something left."),
    ("The article raises an important _____ about the use of personal data.", "issue", ["occasion", "scene", "event"], 2, "Vocabulary: Collocations", "Raise an issue is a common collocation meaning introduce an important topic or problem."),
    ("The new menu is much more _____; customers can find what they need in seconds.", "user-friendly", ["user-friend", "friendly using", "usefully friend"], 2, "Vocabulary: Context", "User-friendly means easy for people to use."),
    ("The school plans to _____ a mentoring programme for new students.", "launch", ["lift", "rise", "throw"], 1, "Vocabulary: Collocations", "Launch a programme means start it officially."),
    ("I came _____ an old practice test while organising my files.", "across", ["under", "through", "down"], 1, "Vocabulary: Phrasal Verbs", "Come across means find or meet something by chance."),
    ("Regular speaking practice made a _____ improvement to her confidence.", "noticeable", ["notice", "noticeably", "noticing"], 2, "Vocabulary: Word Formation", "An adjective is needed before improvement."),
    ("The organiser apologised for the _____ caused by the delayed start.", "inconvenience", ["inconvenient", "inconveniently", "convenientness"], 2, "Vocabulary: Word Formation", "A noun is required after the."),
    ("Please _____ attention to the final sentence of the question.", "pay", ["give", "do", "make"], 1, "Vocabulary: Collocations", "Pay attention is the fixed collocation."),
    ("The teacher pointed _____ that the example did not support our conclusion.", "out", ["off", "away", "up"], 1, "Vocabulary: Phrasal Verbs", "Point out means draw attention to a fact or problem."),
    ("We completed the project ahead of _____.", "schedule", ["calendar", "programme", "timing plan"], 1, "Vocabulary: Collocations", "Ahead of schedule means earlier than planned."),
    ("Her answer showed a good _____ of the main argument.", "understanding", ["understand", "understood", "understandable"], 2, "Vocabulary: Word Formation", "A noun is required after a good."),
    ("We need to _____ down the list to the three strongest ideas.", "narrow", ["thin", "close", "short"], 2, "Vocabulary: Phrasal Verbs", "Narrow down means reduce the number of choices."),
    ("The final presentation was both informative and visually _____.", "appealing", ["appeal", "appealingly", "appealed"], 2, "Vocabulary: Word Formation", "An adjective is required after visually to describe the presentation."),
    ("The course did not live up _____ the description on the website.", "to", ["with", "for", "at"], 2, "Vocabulary: Phrasal Verbs", "Live up to means be as good as expected or promised."),
    ("Students are encouraged to make _____ of the free mock tests before the exam.", "use", ["using", "usage to", "useful"], 1, "Vocabulary: Collocations", "Make use of means use something that is available."),
]
for i, (q, correct, distractors, diff, sub, exp) in enumerate(task6, 1):
    add(f"N17-T6-{i:03d}", "Task 6", "Use of English", sub, diff, q, correct, distractors, i, exp)


assert len(items) == 120, len(items)
path = OUT / "nmt_2026_pack_v1_7.json"
path.write_text(json.dumps(items, ensure_ascii=False, indent=2), encoding="utf-8")
# Convenience copy at repository root, matching previous releases.
(ROOT / "nmt_2026_pack_v1_7.json").write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
print(path, len(items))
