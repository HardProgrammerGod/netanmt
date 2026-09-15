from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "content"
OUT.mkdir(exist_ok=True)
items=[]

def add(code, task, category, sub, difficulty, question, options, correct, explanation):
    assert len(options)==4 and 0<=correct<=3
    target=(int(code.rsplit('-',1)[-1])-1)%4
    opts=list(options)
    opts[correct],opts[target]=opts[target],opts[correct]
    correct=target
    items.append({
        "question_code":code,
        "topic":"reading" if category=="Reading" else "use_of_english",
        "difficulty":difficulty,
        "question_text":question,
        "options":{"A":opts[0],"B":opts[1],"C":opts[2],"D":opts[3]},
        "correct_option":correct,
        "explanation":explanation,
        "category":category,
        "sub_category":sub,
        "section":"NMT",
        "is_active":True,
        "is_diagnostic":False,
        "nmt_task_type":task,
        "content_pack":"v1.6-nmt2026-pack3",
        "quality_status":"approved",
    })

# TASK 1 — notices / short texts
notices=[
("SPEAKING PARTNER HOUR: Pair up with another learner for three 15-minute conversations. Topic cards are provided.","A learner who wants several short speaking practices",1),
("MOBILE PHOTO EDITING: Learn simple cropping, light and colour corrections using a free phone app. Bring your own phone.","Someone wanting basic photo-editing skills on a phone",1),
("EXAM PLANNING CLINIC: Bring your exam dates and current timetable. A mentor will help you build a realistic two-week study plan.","A student who needs help organising revision time",2),
("EVENING TABLE TENNIS: Casual games from 18:00. Bats are available, and beginners are welcome.","A beginner wanting a relaxed evening sport",1),
("LOCAL MAP PROJECT: Volunteers photograph damaged street signs and upload locations through a simple form.","Someone comfortable using a phone for community volunteering",2),
("BOOK REPAIR WORKSHOP: Learn to fix loose pages and damaged covers. Bring one paperback you would like to repair.","A reader who wants to repair a damaged book",2),
("STUDENT PODCAST TASTER: Record a two-minute interview and learn basic editing. No previous audio experience required.","A beginner curious about making a podcast",1),
("MORNING REVISION ROOM: Silent room open 07:00–08:30 with desks, Wi-Fi and charging points. No group work.","A student needing an early quiet study space",1),
("JOB INTERVIEW PRACTICE: Twenty-minute mock interview followed by feedback. Bring the job advert you are interested in.","Someone preparing for a specific job interview",2),
("URBAN SKETCH WALK: Draw buildings outdoors with pencil or pen. Any skill level welcome; bring a small notebook.","Someone who wants informal drawing practice outside",1),
("FIRST AID THEORY TALK: Learn how emergency services are contacted and what information callers should provide. No practical training included.","Someone interested in understanding emergency-call basics",2),
("ECO SWAP SHELF: Leave clean reusable folders, notebooks or stationery and take items you need. No money changes hands.","A student who wants to exchange school supplies",1),
("INTRO TO 3D DESIGN: Create a simple keyring model on a computer. Laptops and software are provided.","A beginner wanting to try basic 3D modelling",1),
("WRITING FEEDBACK DESK: Bring up to 250 words of English writing. A tutor will comment on clarity, grammar and organisation.","A learner who wants feedback on a short English text",2),
("SUNSET NATURE WALK: Slow 5 km route with stops to identify birds and plants. Bring a light jacket and water.","Someone wanting a gentle nature-focused walk",1),
("STUDENT BUDGET SESSION: Learn how to track weekly spending, separate needs from wants and set a savings goal.","A student wanting to manage everyday spending better",1),
("DIGITAL DECLUTTER HOUR: Organise folders, rename files and set up a simple backup routine. Bring your laptop.","Someone whose computer files are poorly organised",2),
("SHORT FILM CLUB: Watch a 15-minute film and discuss its ending in English. B1 level recommended.","An intermediate learner interested in film discussion",2),
("MUSEUM AUDIO GUIDE TESTERS: Try a new student audio guide and complete a five-minute feedback form afterwards.","A student willing to test and review a museum service",2),
("BEGINNER CHESS TABLES: Learn legal moves and play short guided games. Pieces are supplied.","Someone who has never learned chess properly",1),
("CAMPUS LOST-AND-FOUND SORT: Volunteers label and organise unclaimed items for two hours on Friday.","Someone willing to help with a simple organising task",1),
("CANVA POSTER BASICS: Make a clean event poster using templates, spacing and readable fonts. No design experience needed.","A beginner wanting to create a simple digital poster",1),
("READING SPRINT: Bring any English book. Read silently for 25 minutes, then share one idea with a small group.","A learner wanting a short structured reading session",1),
("CAREER EMAIL WORKSHOP: Practise writing a polite enquiry email and a follow-up message to an employer.","Someone wanting to improve professional email writing",2),
("RAINY-DAY RUN CLUB: If weather is poor, training moves indoors. Sessions focus on easy endurance, not speed.","A runner who wants consistent non-competitive training",2),
("STUDENT TECH HELP: Volunteers explain basic phone settings to older visitors. Patience matters more than advanced technical knowledge.","A patient student comfortable with everyday phone settings",2),
("FRENCH PRONUNCIATION TASTER: One beginner lesson focusing on sounds and greetings. No previous French required.","Someone who wants to try French for the first time",1),
("SCIENCE ARTICLE CLUB: Read one short popular-science article before the meeting and discuss whether its evidence is convincing.","Someone who enjoys discussing evidence in science writing",3),
("WEEKLY MEAL PREP DEMO: Watch a tutor prepare three simple lunches and receive a shopping list. This is a demonstration, not a cooking class.","Someone wanting ideas for simple prepared lunches",1),
("SCHOOL EVENT PHOTOGRAPHERS: Volunteers needed for candid photos during Saturday's event. You should already know basic camera controls.","A student with basic photography experience",2),
("OPEN MIC REHEARSAL: Perform one song or poem to a small friendly audience before the main event next week.","Someone wanting a low-pressure performance practice",2),
("RESEARCH QUESTION LAB: Turn a broad school-project topic into a focused research question and identify useful keywords.","A student starting a research-based school project",2),
("PUBLIC TRANSPORT Q&A: Staff explain student passes, route planning and what to do if a card is lost.","A student needing practical information about local transport",1),
("BEGINNER VIDEO CAPTIONS: Add readable subtitles to a short video and export it for social media. Laptops supplied.","Someone wanting to learn simple video subtitling",2),
]
answers=[x[1] for x in notices]
for i,(text,ans,diff) in enumerate(notices,1):
    ds=[answers[(i+5)%34],answers[(i+13)%34],answers[(i+23)%34]]
    add(f"N16-T1-{i:03d}","Task 1","Reading","Matching: Notices",diff,
        "Read the notice and choose the person it is most suitable for.\n\n"+text,[ans,*ds],0,
        "The correct person matches the purpose, level and practical details in the notice.")

# TASK 2 — reading comprehension
reads=[
("Marta began reviewing vocabulary on the bus for ten minutes each morning instead of studying a long list once a week. After a month, she noticed she could recall more words during speaking practice.","What changed for Marta?","Regular short reviews improved her recall",1),
("A school café moved its most popular healthy snacks closer to the checkout. Sales of those items rose even though prices and the menu stayed the same.","What most likely caused the change in sales?","The snacks became easier for customers to notice",2),
("Denys joined an online course expecting recorded lectures. Instead, most lessons required him to solve short problems before seeing the explanation. He found this frustrating at first but later said he remembered more.","Why did Denys eventually value the course format?","Active problem-solving helped him remember the material",2),
("A local library added colour labels to shelves after visitors said category numbers were hard to follow. Staff report that fewer people now ask where common sections are located.","What problem did the labels help solve?","Visitors had difficulty finding sections",1),
("Iryna wanted to run faster, so she trained hard every day. Her coach suggested adding easier days between difficult sessions. Within weeks, Iryna felt less tired and her times improved.","What did the coach change?","The balance between hard and easy training",2),
("A museum tested two versions of a sign. One used a long paragraph; the other used three short bullet points. Visitors answered questions more accurately after reading the shorter version.","What does the result suggest?","Concise information was easier to understand",2),
("Taras often forgot small homework deadlines. He started entering tasks into one calendar immediately after each lesson. The number of missed deadlines quickly fell.","What made the biggest difference?","Recording deadlines in one place right away",1),
("A student newspaper stopped publishing only at the end of each month and began posting shorter articles throughout the week. Website visits became more regular rather than rising sharply once a month.","What changed in audience behaviour?","Readers visited the site more consistently",2),
("Olena practised presentations alone until a teacher suggested recording one on her phone. Watching the video showed her that she spoke too quickly, something she had not noticed while presenting.","What did the recording provide?","A way to observe a speaking habit she was unaware of",2),
("The town introduced a free bike-repair stand beside the railway station. Commuters can use basic tools themselves. Staff do not perform repairs, but instructions are displayed nearby.","What is the service mainly designed for?","People who can carry out simple repairs themselves",2),
("A class compared two articles reporting the same event. Both included accurate facts, but each selected different details for its headline and opening paragraph.","What lesson could students learn from the comparison?","Sources can frame the same event differently",3),
("Nazar turned off app notifications while studying but kept his phone on the desk. He still checked it frequently. When he later placed it in a drawer, the checking habit decreased.","What additional change helped Nazar concentrate?","Putting the phone out of sight",1),
("A volunteer group asked new members to choose one small responsibility for their first event instead of helping with everything. More newcomers returned for a second event than before.","Why might the new approach have worked?","The first experience felt more manageable",2),
("A language teacher noticed students knew grammar rules but hesitated in conversation. She introduced two-minute speaking rounds where students had to use one target structure without stopping to correct every mistake.","What skill was the teacher mainly trying to develop?","Fluent use of known grammar while speaking",3),
("A café offered a small discount to customers bringing reusable cups. At first only a few participated, but signs showing how many disposable cups had been saved led to a further increase.","What did the signs add?","Visible evidence that the behaviour had an impact",2),
("Sofiia usually read difficult texts from beginning to end without stopping. Her tutor suggested first scanning headings and questions. She then found relevant information more quickly.","How did the tutor change Sofiia's reading strategy?","She began previewing the text before detailed reading",2),
("A school coding club used to begin each meeting with a long explanation. It switched to showing a small project first and explaining the code while students modified it. Attendance stayed similar, but more students finished projects.","What improved after the change?","Students were more successful at completing projects",2),
("Mykhailo was sure he needed complete silence to study. During a crowded week he tried quiet instrumental music and discovered it helped cover distracting conversations without disturbing him.","What did Mykhailo discover?","A controlled background sound could reduce other distractions",2),
("A teacher returned essays with only a final mark. Later she added two specific comments: one strength and one next step. Students made more targeted changes in the following assignment.","Why were the comments useful?","They showed students what to keep and what to improve",2),
("A sports centre noticed many new members stopped attending after the first month. It introduced short orientation sessions explaining how to use equipment and plan simple workouts. Retention improved.","What problem was the orientation intended to address?","New members were unsure how to use the centre effectively",2),
("Kateryna prepared for a listening test by replaying the same easy podcast. Her teacher suggested mixing familiar material with slightly harder clips. At first her scores dipped, then improved beyond her previous level.","Why did her scores initially fall?","The new material was more challenging",1),
("A city park replaced some signs saying 'Do not walk on the grass' with signs explaining that young plants were being restored. Staff observed fewer people crossing the protected area.","What was different about the new signs?","They explained the reason for the rule",2),
("A student team had ten ideas for a project but only one week to build something. They chose the smallest idea that could demonstrate the core concept and finished on time.","What strategy did the team use?","They reduced the scope to a workable version",2),
("Yulia always highlighted many sentences while reading. When she later tried writing a one-sentence summary after each section, she realised some highlighted details were not important.","What did summarising help Yulia do?","Separate main ideas from less important details",2),
("A school sent event reminders one week before each activity. Many students forgot. Adding a second reminder on the morning of the event increased attendance.","What did the school change?","The timing and frequency of reminders",1),
("An online shop displayed delivery dates only at the final checkout page. After moving estimated dates onto product pages, fewer customers abandoned their orders.","Why might abandonment have fallen?","Customers learned important delivery information earlier",2),
("Roman studied grammar by rereading explanations. Before an exam he switched to answering questions without notes, then checking mistakes. He discovered several rules he had only thought he understood.","What did practice questions reveal?","Gaps that passive rereading had hidden",2),
("A community centre offered a free lecture on digital security, but attendance was low. The next session was advertised using three specific topics people would learn, and registrations doubled.","What likely improved the advertisement?","It made the practical benefits clearer",2),
("A team leader asked everyone to give status updates in a one-hour meeting. Later, routine updates moved to a shared document and meetings were used only for decisions. Meetings became shorter.","What information moved out of meetings?","Routine progress reports",1),
("Daria wanted to read more English fiction but found full novels intimidating. She started with short stories and gradually chose longer texts.","Why did short stories help Daria?","They made the reading goal feel more manageable",1),
("A bus app began showing not only arrival times but also how crowded each bus was. Users said they sometimes waited for the next bus even when the first one arrived sooner.","What new factor influenced users' choices?","Expected crowding",1),
("A teacher gave students a checklist before they submitted reports. The checklist did not contain answers; it reminded them to check sources, headings and conclusions. Missing sections became less common.","How did the checklist help?","It prompted students to review key requirements",2),
("A youth club planned every activity itself. Later it allowed members to propose and vote on one activity each month. Participation in those member-chosen events was especially high.","What may explain the higher participation?","Members had a role in choosing the activity",2),
("A small study group agreed that anyone could ask for a five-minute explanation when confused, but no one had to pretend to understand. Members said they became more willing to discuss mistakes.","What did the rule mainly create?","A safer atmosphere for admitting confusion",3),
]
for i,(text,q,ans,diff) in enumerate(reads,1):
    distract=["It increased the cost of the activity","It removed the need to practise","It made the task completely automatic"]
    # Tailor generic distractors with nearby correct answers for harder items.
    if diff>=2:
        distract=[reads[(i+7)%34][2],reads[(i+16)%34][2],reads[(i+25)%34][2]]
    add(f"N16-T2-{i:03d}","Task 2","Reading","Reading: Comprehension",diff,
        text+"\n\n"+q,[ans,*distract],0,"The correct option is directly supported by the change, result or detail described in the text.")

# TASK 3 — matching situations
situations=[
("You need a place to practise a five-minute presentation and receive comments on delivery.","Presentation rehearsal with feedback"),
("You have several scanned pages and need help turning them into a clearly organised PDF.","Document-scanning and file-organisation help"),
("You want to practise English conversation but cannot attend a fixed weekly class.","Drop-in speaking exchange"),
("You are starting a research project and are unsure which search terms to use.","Research keyword planning session"),
("You want to try volunteering but can only commit to one Saturday morning.","One-off community volunteer event"),
("You have a bicycle that works but want somebody to check whether it is safe.","Basic bicycle safety inspection"),
("You want to learn how to make your study notes easier to review before an exam.","Note-organisation workshop"),
("You need a quiet desk after normal library closing time.","Late-evening study room"),
("You want to practise answering common interview questions before applying for a summer job.","Mock job interview"),
("You enjoy photography and want a short project with a clear weekly theme.","Weekly photo challenge"),
("You have basic English but want help understanding how the NMT reading tasks work.","NMT reading strategy session"),
("You want to improve typing speed but do not need a full computer course.","Short typing-practice clinic"),
("You need feedback on whether a scholarship motivation letter is clear and convincing.","Motivation-letter review"),
("You want a low-cost social activity where it is fine to arrive alone.","Open board-game evening"),
("You are comfortable with basic coding and want to build something small with other students.","Weekend coding mini-project"),
("You want to understand your monthly spending before deciding how much you can save.","Personal budget review"),
("You need help choosing which tasks to do first during a very busy week.","Priority-planning session"),
("You want to practise pronunciation by hearing and repeating short phrases.","Guided pronunciation lab"),
("You would like to learn whether a news article uses reliable evidence.","Media-literacy workshop"),
("You want to repair a loose backpack strap instead of buying a new bag.","Basic sewing repair table"),
("You want to test whether a university subject interests you before choosing a course.","Subject taster lecture"),
("You have an idea for a student event but need help estimating time, people and materials.","Event-planning clinic"),
("You want to practise reading faster without trying to understand every single word.","Skimming and scanning workshop"),
("You need a simple way to back up important school files automatically.","Digital backup setup help"),
("You want to learn basic spreadsheet formulas for a school project.","Beginner spreadsheet lab"),
("You are nervous about joining a sports group because you have little experience.","Beginner-friendly social sports session"),
("You want to exchange books you have finished without spending money.","Community book swap"),
("You need a short explanation of how student public-transport passes work.","Student transport information desk"),
("You want to make a simple poster for a school event but have no design experience.","Template-based poster workshop"),
("You have recorded a short video and want to add readable captions.","Video subtitling clinic"),
("You want a teacher to explain two grammar mistakes that keep appearing in your writing.","Targeted grammar feedback desk"),
("You are looking for a calm activity that combines walking with learning about local history.","Guided historical walking tour"),
("You need to practise presenting a project to people who may ask unexpected questions.","Project Q&A rehearsal"),
("You want to learn how to break a large goal into weekly actions.","Goal-planning workshop"),
]
matches=[x[1] for x in situations]
for i,(sit,match) in enumerate(situations,1):
    ds=[matches[(i+6)%34],matches[(i+15)%34],matches[(i+24)%34]]
    diff=1 if i%5==1 else (3 if i%8==0 else 2)
    add(f"N16-T3-{i:03d}","Task 3","Reading","Matching: Situations",diff,
        "Choose the service or activity that best matches the situation.\n\n"+sit,[match,*ds],0,
        "The correct option matches both the person's goal and the practical format they need.")

# TASK 4 — gapped text / cohesion
gaps=[
("I had written a long list of everything I wanted to revise. _____. Once I chose the three most important topics, starting felt much easier.","The size of the list was making the task feel impossible",1),
("Our first online meeting was full of interruptions. _____. The next meeting was noticeably calmer and shorter.","Before the second one, we agreed on simple speaking rules",2),
("Mila thought the route would take twenty minutes. _____. She started leaving home earlier after that.","Roadworks made the journey much slower than usual",1),
("The article contained several impressive statistics. _____. We checked the original report before using them in our project.","However, it did not explain where the numbers came from",3),
("I used to wait until I felt motivated before studying. _____. Now I begin with one five-minute task even when I do not feel ready.","That often meant I postponed work for too long",2),
("The club wanted more beginners to join. _____. New members said the first meeting felt less intimidating.","It introduced a short welcome session before regular activities",1),
("The first draft of our survey had twenty-five questions. _____. More students completed the shorter version.","We removed items that did not connect to our main research question",2),
("Oleh kept making the same pronunciation error. _____. Hearing the contrast helped him notice the difference.","His teacher recorded the correct and incorrect versions side by side",2),
("The room looked bright enough during the day. _____. We added a desk lamp before the evening study session.","After sunset, the work area became much darker",1),
("I assumed a difficult word was essential to understanding the paragraph. _____. The main idea was still clear without it.","So I tried reading the sentence again while temporarily ignoring the word",2),
("The team had collected plenty of ideas but had not chosen a direction. _____. By the end of the meeting, everyone knew what would be built first.","They voted on one clear priority",1),
("The school wanted students to use the new recycling bins correctly. _____. Sorting mistakes decreased during the following week.","Simple picture labels were added above each opening",1),
("Nina had practised her talk many times alone. _____. A friend asked questions she had never considered.","Then she tried presenting it to another person",2),
("The website worked well on a laptop. _____. Several buttons were too small on a phone screen.","Testing it on a mobile device revealed a different problem",2),
("The teacher did not correct every sentence in the draft. _____. Students had to find and fix some patterns themselves.","Instead, she marked the types of errors in the margin",3),
("We planned to interview ten people. _____. We therefore changed the project to focus on six detailed interviews.","Only a few participants were available before the deadline",2),
("The library's study area had become noisy in the afternoon. _____. Students could still work together elsewhere in the building.","One room was redesignated as silent space",1),
("I used to choose the easiest practice questions because they felt encouraging. _____. My progress became faster when I added more challenging items.","Eventually I realised that comfort was not the same as learning",2),
("The event page gave the date and location but registrations remained low. _____. More people signed up after the update.","Organisers added a short explanation of what participants would actually do",1),
("Sasha copied every new word into a notebook. _____. He began adding one example sentence beside each word.","Later he noticed that isolated translations were hard to use in conversation",2),
("The class had only thirty minutes to complete the task. _____. They divided the research, writing and checking between different people.","Working sequentially would have taken too long",2),
("The weather was colder than the forecast suggested. _____. Fortunately, the visitor centre sold inexpensive gloves.","I had not packed anything warm enough for my hands",1),
("Our presentation slides contained full paragraphs. _____. The audience paid more attention to the speaker after we simplified them.","We replaced most of the text with short phrases and visuals",2),
("I wanted to understand why my practice score had fallen. _____. Most mistakes came from rushing, not from unknown grammar.","I reviewed each wrong answer instead of only looking at the total score",2),
("The organisers expected fifty visitors. _____. They quickly opened a second registration desk.","More than twice that number arrived in the first hour",1),
("The first version of the timetable looked efficient on paper. _____. Travel time between two locations had been forgotten.","A practical test showed that one transition was unrealistic",3),
("Emma was hesitant to ask for feedback because she expected only criticism. _____. The comments also identified what already worked well.","Her first review changed that expectation",2),
("The school introduced a weekly reading challenge. _____. Participation rose when students could choose from several types of text.","At first the same article was assigned to everyone",2),
("We were tempted to add another feature before launch. _____. Fixing the confusing registration step had a much bigger effect.","User tests showed that a simpler problem needed attention first",2),
("The podcast episode sounded clear through headphones. _____. We reduced the music volume before publishing it.","On phone speakers, the background music covered parts of the speech",2),
("Maks wanted to memorise the speech word for word. _____. Using a short outline made his delivery sound more natural.","He found that forgetting one sentence could make him lose his place",2),
("The teacher asked us to predict the article's topic from its title. _____. Our predictions gave us a purpose for reading.","Only after that did we read the full text",1),
("The group had different opinions about which design was best. _____. The decision became easier once they compared all versions against the same criteria.","They agreed to define the criteria before voting",3),
("I often opened several study tabs at the same time. _____. Keeping only the resources needed for the current task reduced that distraction.","Switching between them had become a habit",2),
]
answers=[x[1] for x in gaps]
for i,(text,ans,diff) in enumerate(gaps,1):
    ds=[answers[(i+4)%34],answers[(i+12)%34],answers[(i+20)%34]]
    add(f"N16-T4-{i:03d}","Task 4","Reading","Reading: Gapped Text",diff,
        "Choose the sentence that best completes the text.\n\n"+text,[ans,*ds],0,
        "The correct sentence creates the strongest logical and grammatical connection across the gap.")

# TASK 5 — grammar cloze
grammar=[
("By the time the lesson started, I _____ the homework.","had finished",["finished","have finished","was finishing"],2,"Past Perfect shows the homework was completed before another past event.","Grammar: Tenses"),
("If I _____ about the schedule change, I would have arrived earlier.","had known",["knew","would know","have known"],3,"Third Conditional uses if + Past Perfect for an unreal past condition.","Grammar: Conditionals"),
("The new library _____ next month after the renovation is completed.","will be opened",["will open by","is opening by","has opened"],2,"A passive form is needed because the library receives the action.","Grammar: Passive Voice"),
("She suggested _____ the difficult questions first.","doing",["to do","do","to doing"],2,"Suggest is followed by a gerund in this structure.","Grammar: Gerund / Infinitive"),
("This is the teacher _____ helped me prepare for the competition.","who",["which","where","whose of"],1,"Who refers to a person as the subject of the relative clause.","Grammar: Relative Clauses"),
("You _____ have brought your laptop; computers are available here.","needn't",["mustn't","couldn't","shouldn't to"],2,"Needn't have/needn't indicates lack of necessity; here the simple context is no need to bring it.","Grammar: Modal Verbs"),
("I have lived here _____ 2023.","since",["for","during","from since"],1,"Since introduces the starting point of a period continuing to the present.","Grammar: Prepositions"),
("There were _____ students in the room than we expected.","fewer",["less","fewest","little"],1,"Fewer is used with plural countable nouns.","Grammar: Quantifiers"),
("He asked me where I _____ the information.","had found",["did find","have found","find"],3,"Backshift in reported speech commonly changes Past Simple to Past Perfect.","Grammar: Reported Speech"),
("The test was _____ difficult than the practice version.","more",["most","much as","very more"],1,"Long adjectives form the comparative with more.","Grammar: Comparatives"),
("I wish I _____ more time to revise this week.","had",["have","would have had","will have"],2,"Wish about a present situation uses a past form: I wish I had.","Grammar: Wish"),
("Neither the teacher nor the students _____ ready to leave.","were",["was","is","has been"],3,"With neither...nor, agreement usually follows the nearer subject: students.","Grammar: Agreement"),
("We _____ for twenty minutes when the bus finally arrived.","had been waiting",["waited","have waited","were waited"],3,"Past Perfect Continuous emphasises duration before another past event.","Grammar: Tenses"),
("If the weather _____ better tomorrow, we will study outside.","is",["will be","would be","was"],1,"First Conditional uses Present Simple in the if-clause.","Grammar: Conditionals"),
("The documents must _____ before Friday.","be submitted",["submit","be submitting","have submit"],2,"Modal + passive uses modal + be + past participle.","Grammar: Passive Voice"),
("I stopped _____ my phone while studying because it distracted me.","checking",["to check","check","checked"],2,"Stop doing means cease an activity.","Grammar: Gerund / Infinitive"),
("The book, _____ was published last year, has already won an award.","which",["who","where","what"],2,"Which introduces a non-defining relative clause referring to a thing.","Grammar: Relative Clauses"),
("You _____ be tired after travelling all night.","must",["can to","should to","need"],1,"Must can express a strong logical deduction.","Grammar: Modal Verbs"),
("She is responsible _____ organising the final presentation.","for",["of","to","with"],1,"The fixed adjective-preposition combination is responsible for.","Grammar: Prepositions"),
("Only _____ information was available on the website.","a little",["a few","many","few"],2,"Information is uncountable, so a little is appropriate.","Grammar: Quantifiers"),
("He said that he _____ the email the day before.","had sent",["sent tomorrow","has sent","sends"],2,"Reported speech with an earlier past action uses Past Perfect.","Grammar: Reported Speech"),
("This route is by far _____ of the three.","the shortest",["shorter","the shorter","most short"],1,"Comparing three items requires the superlative.","Grammar: Comparatives"),
("I'd rather you _____ me before changing the plan.","asked",["ask","will ask","have ask"],3,"Would rather + subject commonly takes a past form for a present/future preference.","Grammar: Verb Patterns"),
("Not only _____ late, but he also forgot the documents.","was he",["he was","did he was","he did"],3,"Negative inversion follows not only at the beginning of the clause.","Grammar: Inversion"),
("I _____ this book for two weeks, but I still have fifty pages left.","have been reading",["read","am read","had read yesterday"],2,"Present Perfect Continuous describes an activity continuing over a period until now.","Grammar: Tenses"),
("Unless you _____ the form today, your application will not be processed.","submit",["will submit","submitted","would submit"],2,"Unless takes a present form when referring to a real future condition.","Grammar: Conditionals"),
("The room needs _____ before the guests arrive.","cleaning",["to cleaning","clean","cleaned by"],3,"Need + gerund can have a passive meaning: needs cleaning.","Grammar: Gerund / Infinitive"),
("The student _____ laptop was stolen reported it immediately.","whose",["who","which","whom laptop"],2,"Whose expresses possession in a relative clause.","Grammar: Relative Clauses"),
("You _____ have told me earlier; I could have helped.","should",["must","can","need to have"],2,"Should have + past participle expresses criticism or regret about the past.","Grammar: Modal Verbs"),
("We arrived _____ the station just before eight.","at",["in","on","to at"],1,"Arrive at is used for a specific place such as a station.","Grammar: Prepositions"),
("_____ of the two answers is completely correct.","Neither",["None","Any","Much"],2,"Neither refers to not one and not the other of two items.","Grammar: Quantifiers"),
("She asked whether I _____ available the following afternoon.","would be",["will be","am","have been yesterday"],2,"Future in the past is commonly expressed with would in reported speech.","Grammar: Reported Speech"),
("The more carefully you read, the _____ mistakes you make.","fewer",["less","few","fewest"],2,"The comparative structure uses fewer with plural countable mistakes.","Grammar: Comparatives"),
("Hardly _____ the exam when the fire alarm rang.","had we started",["we had started","did we started","we started had"],3,"Hardly at the beginning triggers inversion with Past Perfect.","Grammar: Inversion"),
]
for i,(q,ans,ds,diff,exp,sub) in enumerate(grammar,1):
    add(f"N16-T5-{i:03d}","Task 5","Use of English",sub,diff,q,[ans,*ds],0,exp)

# TASK 6 — vocabulary / word formation
vocab=[
("The new timetable will come into _____ next Monday.","effect",["result","action","work"],2,"The fixed expression is come into effect.","Vocabulary: Collocations"),
("I need to _____ up on the grammar we studied last month.","brush",["clean","turn","make"],2,"Brush up on means improve or refresh existing knowledge.","Vocabulary: Phrasal Verbs"),
("Her explanation was short but very _____ .", "effective",["effect","effectively","effectiveness"],1,"An adjective is needed after very to describe the explanation.","Vocabulary: Word Formation"),
("The team finally reached an _____ after a long discussion.","agreement",["agree","agreeable","agreedly"],1,"A noun is required after an.","Vocabulary: Word Formation"),
("Please take the weather into _____ before choosing the route.","account",["mindly","thought","notice of"],2,"Take something into account means consider it.","Vocabulary: Collocations"),
("We ran _____ of printer paper just before the deadline.","out",["off","away","down"],1,"Run out of means have none left.","Vocabulary: Phrasal Verbs"),
("The article raises an important _____ about online privacy.","issue",["event","occasion","scene"],2,"Raise an issue is a common academic collocation.","Vocabulary: Collocations"),
("The instructions were surprisingly _____, so everyone completed the setup quickly.","straightforward",["straightly","forwarded","straightness"],2,"Straightforward means clear and uncomplicated.","Vocabulary: Context"),
("The school decided to _____ a new mentoring programme.","launch",["throw","lift","rise"],1,"Launch a programme means start it officially.","Vocabulary: Collocations"),
("I came _____ an interesting article while searching for statistics.","across",["over","through","under"],2,"Come across means find by chance.","Vocabulary: Phrasal Verbs"),
("Regular practice can make a _____ difference to confidence.","significant",["significance","significantly","signify"],2,"An adjective modifies difference.","Vocabulary: Word Formation"),
("The organiser apologised for the _____ caused by the last-minute change.","inconvenience",["inconvenient","inconveniently","convenienceful"],2,"A noun is required after the.","Vocabulary: Word Formation"),
("We should _____ attention to the wording of the question.","pay",["give","make","do"],1,"The fixed collocation is pay attention.","Vocabulary: Collocations"),
("The teacher pointed _____ that two answers were possible only in informal English.","out",["off","up","away"],2,"Point out means draw attention to a fact.","Vocabulary: Phrasal Verbs"),
("The project was completed ahead of _____ .", "schedule",["calendar","programme time","planing"],1,"Ahead of schedule means earlier than planned.","Vocabulary: Collocations"),
("Her response showed a high level of _____ of the topic.","understanding",["understand","understood","understandable"],2,"A noun is required after level of.","Vocabulary: Word Formation"),
("We need to _____ down the list to the five strongest ideas.","narrow",["short","close","thin"],2,"Narrow down means reduce the number of choices.","Vocabulary: Phrasal Verbs"),
("The speaker gave a very _____ example that everyone could relate to.","practical",["practice","practically","practise"],1,"An adjective is required before example.","Vocabulary: Word Formation"),
("The final result did not live up _____ our expectations.","to",["with","for","at"],2,"The phrase is live up to expectations.","Vocabulary: Phrasal Verbs"),
("Students are encouraged to make _____ of the free practice materials.","use",["usage to","using","useful"],2,"Make use of means use something that is available.","Vocabulary: Collocations"),
("The instructions should be _____ enough for a beginner to follow.","clear",["clearly","clarity","clearnessly"],1,"An adjective follows be and enough modifies that adjective.","Vocabulary: Word Formation"),
("The team came _____ with three possible solutions.","up",["over","out","down"],1,"Come up with means produce or think of an idea.","Vocabulary: Phrasal Verbs"),
("The course places strong _____ on practical communication.","emphasis",["emphasise","emphatic","emphasising"],2,"Place emphasis on is the correct noun collocation.","Vocabulary: Collocations"),
("The website was temporarily _____ due to maintenance.","unavailable",["availability","availably","unavailability of"],2,"An adjective is needed after was.","Vocabulary: Word Formation"),
("I need to catch _____ on the lessons I missed last week.","up",["out","over","down"],1,"Catch up on means do work needed to reach the current level.","Vocabulary: Phrasal Verbs"),
("The change had an immediate _____ on attendance.","impact",["affect","influence to","impaction"],2,"Have an impact on is a standard collocation.","Vocabulary: Collocations"),
("The teacher asked for a more _____ explanation of how we reached the answer.","detailed",["detail","details","detailingly"],1,"An adjective is required before explanation.","Vocabulary: Word Formation"),
("Don't put _____ the application until the final day.","off",["out","over","away"],1,"Put off means postpone.","Vocabulary: Phrasal Verbs"),
("The new policy is intended to _____ access to study resources.","improve",["improvement","improvedly","improving of"],2,"After to, the base verb improve is required.","Vocabulary: Word Formation"),
("The organisers took _____ for the mistake and corrected it quickly.","responsibility",["responsible","response","responsibly"],2,"Take responsibility for is the fixed collocation.","Vocabulary: Collocations"),
("The plan fell _____ because two key volunteers became unavailable.","through",["under","across","behind"],2,"Fall through means fail to happen as planned.","Vocabulary: Phrasal Verbs"),
("The data provides useful _____ into how students revise.","insight",["sight","viewing","inside"],3,"Provide insight into is a common academic collocation.","Vocabulary: Collocations"),
("The task requires both accuracy and _____ .", "flexibility",["flexible","flexibly","flex"],2,"A noun is needed to parallel accuracy.","Vocabulary: Word Formation"),
("We should look _____ the issue before making a final decision.","into",["through at","over to","up on"],2,"Look into means investigate.","Vocabulary: Phrasal Verbs"),
]
for i,(q,ans,ds,diff,exp,sub) in enumerate(vocab,1):
    add(f"N16-T6-{i:03d}","Task 6","Use of English",sub,diff,q,[ans,*ds],0,exp)

assert len(items)==204, len(items)
path=OUT/'nmt_2026_pack_v1_6.json'
path.write_text(json.dumps(items,ensure_ascii=False,indent=2),encoding='utf-8')
print(path, len(items))
