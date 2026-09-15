from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "content"
OUT.mkdir(exist_ok=True)
items=[]

def add(code, task, category, sub, difficulty, question, options, correct, explanation):
    assert len(options)==4 and 0<=correct<=3
    # Even answer distribution A-D across the pack.
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
        "content_pack":"v1.5-nmt2026-pack2",
        "quality_status":"approved",
    })

# ---------------- TASK 1: notices / short texts ----------------
notices=[
("STUDY ROOM BOOKING: Reserve a desk for up to three hours. Food is not allowed, but closed water bottles are fine.","A student who needs a quiet place for focused work",1),
("BEGINNER GUITAR GROUP: Six evening lessons. You only need your own instrument; no music-reading experience is necessary.","Someone starting to learn guitar from the beginning",1),
("COMMUNITY GARDEN: Saturday volunteers will plant herbs and repair raised beds. Tools are provided; wear clothes that can get dirty.","Someone happy to do practical outdoor volunteering",2),
("MATHS HELP DESK: Drop in after classes with one or two questions you could not solve. This is not a full private lesson.","A student needing quick help with specific maths problems",1),
("CITY WALK: Discover hidden courtyards and local stories. Two hours, mostly on foot. Comfortable shoes recommended.","A visitor interested in exploring the city on foot",1),
("LAPTOP CLINIC: Free software checks for students. Hardware replacement is not included in the service.","A student whose laptop may have a software problem",2),
("DEBATE CLUB: Weekly discussion of current social topics. Participants should be ready to explain and defend their opinions in English.","An English learner who wants structured speaking practice",2),
("SECOND-HAND UNIFORM SALE: Clean school jackets, shirts and sportswear at low prices. Cash and card accepted.","A family wanting cheaper school clothing",1),
("SCIENCE FAIR TEAM: We need two students to help present our renewable-energy project next Friday. Training provided.","A student comfortable speaking to visitors about a project",2),
("QUIET CINEMA SCREENING: Lower sound, softer lighting and no trailers. Guests may leave and return during the film.","Someone who prefers a calmer cinema environment",2),
("MORNING YOGA: Gentle 45-minute class before school. Mats available. Suitable for complete beginners.","A beginner wanting a light early exercise class",1),
("CAREER CV CHECK: Bring a one-page CV and receive ten minutes of feedback from a recruiter. Booking required.","Someone who wants quick professional feedback on a CV",2),
("WEEKEND POTTERY: Make a simple cup by hand. Materials and firing included in the fee. No wheel experience needed.","A beginner interested in making a ceramic object",1),
("LOCAL HISTORY ARCHIVE: Volunteers needed to scan old photographs and type short descriptions. Basic computer skills required.","Someone who likes history and can use a computer",2),
("EXAM BREAKFAST: Free porridge and fruit for students from 7:30 to 9:00 during exam week. Student card required.","A student wanting a free meal before a morning exam",1),
("DOG SHELTER ORIENTATION: New volunteers must attend this 45-minute safety session before walking dogs.","Someone who wants to volunteer with dogs in the future",2),
("CREATIVE WRITING HOUR: Bring a notebook. We will use short prompts and share work only if you choose to.","Someone who wants low-pressure writing practice",1),
("REPAIR CAFÉ: Bring a broken small household item. Volunteers will try to help you fix it; spare parts may cost extra.","Someone hoping to repair an item rather than replace it",2),
("STUDENT RADIO: Looking for presenters, editors and people interested in choosing music. No broadcasting experience required.","A student curious about making radio content",1),
("PUBLIC SPEAKING WORKSHOP: Practise short presentations, eye contact and handling nerves. Participants will speak several times.","Someone wanting confidence in front of an audience",2),
("BIKE-TO-SCHOOL DAY: Free secure parking and a basic breakfast for students arriving by bicycle before 9:00.","A student planning to cycle to school in the morning",1),
("ONLINE RESEARCH SESSION: Learn to evaluate websites, check sources and avoid unreliable information in school projects.","A student wanting to improve source-checking skills",2),
("BOARD GAME EVENING: Strategy and party games for ages 14–18. Come alone or with friends; staff will form groups.","A teenager who wants a social activity without needing a team",1),
("SCHOOL ORCHESTRA: New members welcome, but you should have played your instrument for at least one year.","A student with some experience playing an instrument",2),
("WATERCOLOUR TASTER: One 90-minute lesson with all materials supplied. Learn three basic techniques and take your painting home.","Someone wanting to try watercolour without buying supplies",1),
("VOLUNTEER TRANSLATORS: Help translate short event notices from English into Ukrainian. B2 English or above is recommended.","A stronger English learner interested in translation practice",2),
("TECH TALK: How small satellites collect Earth data. Short lecture followed by questions. No advanced physics knowledge needed.","Someone curious about space technology at an accessible level",1),
("STUDENT MARKET: Sell handmade items, art prints or baked goods. Apply for a table by Wednesday.","A student who wants to sell something they have made",2),
("RUNNING GROUP: Easy 4 km route every Tuesday. The group stays together; this is not race training.","Someone wanting a relaxed group run",1),
("LANGUAGE PLACEMENT TEST: Twenty-minute online test for students joining our autumn English courses. It is not an official certificate.","A learner who needs to find the right course level",2),
]
notice_answers=[row[1] for row in notices]
for i,(text,ans,diff) in enumerate(notices,1):
    # Use other realistic personas as distractors to avoid giveaway options.
    distractors=[
        notice_answers[(i+4)%len(notice_answers)],
        notice_answers[(i+11)%len(notice_answers)],
        notice_answers[(i+19)%len(notice_answers)],
    ]
    add(f"N15-T1-{i:03d}","Task 1","Reading","Matching: Notices",diff,
        "Read the notice and choose the person it is most suitable for.\n\n"+text,
        [ans,*distractors],0,"The key details in the notice match this person's goal and requirements.")

# ---------------- TASK 2: reading comprehension ----------------
reading2=[
("Lena started keeping her phone in another room while doing homework. At first she worried she would miss messages, but after a week she noticed she finished assignments faster and checked her phone less often even during breaks.","What was the main benefit Lena noticed?","She completed her homework more efficiently",1,"The text says she finished assignments faster."),
("A neighbourhood bakery began selling yesterday's bread at a discount during the final hour before closing. The owner says less food is now thrown away, and many students come specifically at that time.","Why did the bakery introduce the discount?","To reduce food waste while still selling the bread",2,"The change is linked directly to throwing away less food."),
("When Amir joined the school basketball team, he expected the hardest part to be fitness. Instead, he found remembering the team's plays more difficult. He began drawing them in a notebook and reviewing them before practice.","What problem did Amir have?","He struggled to remember the team's planned moves",2,"He found the plays difficult to remember."),
("The town installed digital signs at three busy bus stops. They show expected arrival times based on live vehicle locations rather than only the printed timetable. Passengers say waiting feels less uncertain.","What do the new signs provide?","Updated information about when buses are likely to arrive",1,"The signs use live locations to estimate arrival times."),
("Nora used to buy bottled water every day at college. After receiving a reusable bottle, she began filling it at the campus fountains. She says the change was easy because the fountains are located near most classrooms.","Why was Nora able to change her habit easily?","Water refill points were convenient for her",1,"The fountains were near most classrooms."),
("A teacher asked students to submit the first version of an essay a week before the final deadline. The class then exchanged drafts and gave one another comments. Many students made major changes before submitting the final version.","What was the purpose of submitting an early draft?","To give students time to improve their work using feedback",2,"The early draft allowed peer feedback and later revision."),
("Kai had always assumed museums were quiet places where visitors simply looked at objects. During a science museum visit, however, he tested machines, built a paper bridge and joined a short experiment. He left surprised by how active the visit had been.","What surprised Kai?","The museum involved visitors in practical activities",1,"He expected passive viewing but took part in hands-on activities."),
("A small company introduced one meeting-free afternoon each week. Staff can still contact one another for urgent issues, but routine meetings must be scheduled at other times. Employees say longer tasks are now easier to finish.","Why do employees value the meeting-free afternoon?","It gives them uninterrupted time for focused work",2,"They can complete longer tasks more easily without routine meetings."),
("Marta began learning new vocabulary by writing each word in a sentence about her own life. She found that unusual or funny personal examples were especially easy to remember later.","What helped Marta remember vocabulary?","Connecting new words with memorable personal examples",1,"She used sentences about her own life and remembered unusual examples."),
("The school cafeteria tested a pre-order system for lunch. Students choose meals in an app before 10 a.m. Kitchen staff can then prepare more accurate quantities, and queues at lunchtime are shorter.","What is one effect of the pre-order system?","The cafeteria can better predict how much food to prepare",2,"Pre-orders give kitchen staff more accurate quantity information."),
("Daniel wanted to improve his running pace, so he initially tried to run fast every day. After feeling constantly tired, he changed his plan: most runs are now easy, with only one faster session each week.","Why did Daniel change his training?","His original approach left him too tired",2,"The text says daily fast running made him constantly tired."),
("A local theatre now offers a short discussion after selected performances. Audience members can ask actors and directors about choices made during rehearsals. Attendance at the discussion is optional and included in the ticket price.","What can audience members do after selected performances?","Ask the theatre team about how the production was created",1,"The discussion allows questions about rehearsal and production choices."),
("Sofia used a translation app whenever she did not know an English word. Her teacher suggested first trying to describe the idea using words she already knew. Sofia says this has made conversations smoother because she pauses less often.","What skill did Sofia develop?","Explaining an idea even when she does not know the exact word",2,"She learned to paraphrase instead of immediately using translation."),
("A city park replaced some frequently cut grass with wildflower areas. The new areas need less mowing and attract more insects, although signs explain that they may look less tidy at certain times of year.","What is a benefit of the wildflower areas?","They require less maintenance and support insects",2,"Both reduced mowing and more insects are stated."),
("Before giving a presentation, Oleksii recorded himself practising it on his phone. He noticed that he spoke too quickly in the introduction and rarely looked up from his notes. In the final presentation, he deliberately slowed down and used shorter notes.","How did the recording help Oleksii?","It showed him specific aspects of his delivery to improve",2,"He identified speed and eye-contact issues from the recording."),
("An online shop began showing an estimated repairability score for electronic products. The score considers whether common parts can be replaced and whether repair information is available.","What does the score help customers compare?","How practical products may be to repair",2,"The score is based on replaceable parts and repair information."),
("Yana joined a reading challenge that asked participants to read ten books in ten different genres. She normally chose only fantasy, so the challenge introduced her to biographies and science writing, which she had rarely considered before.","What changed because of the challenge?","Yana tried types of books she did not usually choose",1,"The challenge pushed her beyond her usual fantasy choices."),
("A school replaced long weekly announcements with a short daily message shown on classroom screens. Teachers report that students now remember deadlines better because information is more current and repeated closer to the relevant date.","Why are students remembering deadlines better?","They receive shorter, more timely reminders",2,"The messages are current and repeated near the deadline."),
("When Oleh first worked in a café, he tried to memorize every order without writing anything down. After several mistakes, he began using the small order pad provided. His accuracy improved immediately.","What lesson did Oleh learn?","Using a simple tool was more reliable than depending only on memory",1,"Writing orders down reduced his mistakes."),
("The university library added standing desks near its windows. They are not intended to replace normal desks but to give students another option when they want to change position during long study sessions.","Why were standing desks added?","To provide more choice in how students study",1,"They are an additional option, not a replacement."),
("A volunteer group originally planned monthly clean-up events. However, many people said they could not commit to a whole morning. The group now runs shorter one-hour sessions twice a month, and attendance has increased.","Why did attendance increase?","The new sessions require a smaller time commitment",2,"Shorter sessions made participation easier."),
("Eva noticed that she often forgot online passwords and repeatedly reset them. She started using a password manager, which creates and stores strong passwords. She now needs to remember only one main password.","What problem did the password manager solve for Eva?","It reduced the number of passwords she had to remember herself",1,"The manager stores the other passwords for her."),
("A café tested reusable takeaway cups with a small deposit. Customers receive the deposit back when they return the cup to any participating café. The system is designed to make reuse convenient even for people who do not visit the same café again.","Why can customers return cups to different cafés?","To make the reuse system easier to use",2,"Multiple return points increase convenience."),
("Mykhailo began studying in the same place and at the same time each evening. After several weeks, he found it easier to start working without spending time deciding when and where to study.","What advantage did the routine give Mykhailo?","It reduced the effort needed to begin studying",2,"A fixed routine removed repeated decisions about time and place."),
("A language teacher sometimes asks students to explain a grammar rule to a partner instead of only completing exercises. She says explaining forces students to organise what they know and reveals gaps in understanding.","Why does the teacher use peer explanation?","It helps students notice whether they truly understand the rule",2,"Explaining makes knowledge gaps visible."),
("After the local cinema introduced cheaper tickets on Tuesday afternoons, attendance at those screenings rose sharply. Evening attendance stayed almost unchanged, suggesting the offer attracted people who were flexible about time.","What can be inferred from the result?","The discount mainly changed when some people chose to visit",3,"Afternoon attendance rose while evenings stayed similar."),
("A school club wanted more students to attend its events. Instead of posting only dates, it began publishing short videos showing what happens at meetings. Sign-ups increased, especially among first-year students who had not known what to expect.","Why were the videos effective?","They made the club's activities easier to understand before joining",2,"The videos showed what meetings were actually like."),
("Ihor bought noise-cancelling headphones for travel, expecting to use them mainly on planes. He now uses them more often in the library because they reduce background conversations without requiring loud music.","Where does Ihor now use the headphones most usefully?","In the library while studying",1,"The text says he uses them more often in the library."),
("A teacher noticed students often skipped optional revision sheets because they looked too long. She divided each sheet into five-minute sections with clear labels. More students began completing at least part of the revision.","What made the revision sheets more approachable?","Breaking them into small clearly defined sections",2,"The shorter labelled sections reduced the apparent size of the task."),
("A local bus route was extended by two stops to reach a new residential area. Although the full journey is now a few minutes longer, passenger numbers increased because more residents can reach the route on foot.","Why did passenger numbers increase?","The route became accessible to more people",2,"The extension brought the route within walking distance of more residents."),
]
reading2_distractors=[
["She spent more time checking messages during breaks","She began doing all assignments at school","She stopped using her phone completely"],
["To attract only tourists at closing time","To make fresh bread more expensive","To shorten the bakery's opening hours"],
["He was not fit enough to join practices","He disliked drawing in his notebook","He could not understand the coach's instructions at all"],
["The price of each bus journey","Only the times printed on old timetables","How crowded each bus will be"],
["She stopped drinking water outside college","A friend filled the bottle for her every day","Bottled water became unavailable in shops"],
["To give the teacher less marking to do","To prevent students from changing their essays","To make the final deadline earlier"],
["The museum was much quieter than expected","Visitors were not allowed near the exhibits","The museum focused only on modern art"],
["It lets them leave work earlier every week","It removes the need to communicate with colleagues","It guarantees that no urgent issue can interrupt them"],
["Writing every word several times without context","Learning only words that looked unusual","Avoiding examples connected with her own life"],
["Students must now pay before entering the cafeteria","Lunch has become available only through the app","The cafeteria prepares the same amount of every meal"],
["He wanted to train for a different sport","He decided that pace never matters","His weekly schedule had too few running days"],
["Buy a cheaper ticket for the next show","Join actors during the performance","Watch a recording of the rehearsal"],
["Translating every sentence before speaking","Avoiding conversations with unfamiliar people","Learning every possible word before using English"],
["They are cut more frequently than ordinary grass","They require more water and fewer insects visit them","They make every part of the park look tidier all year"],
["It automatically rewrote his presentation","It allowed him to avoid practising again","It showed that his notes were too short to use"],
["How fashionable the products are","How quickly the products are delivered","How many apps are installed on the products"],
["She stopped reading fantasy completely","She read fewer books than before","She chose only books recommended by friends"],
["Every message now contains more information","Deadlines were removed from the school schedule","Students receive announcements only once a month"],
["Customers preferred orders that were not written down","The café stopped allowing staff to use order pads","Memorising became easier as the café got busier"],
["To force all students to stand while studying","To reduce the number of study places","To keep students away from the windows"],
["The events became longer and less frequent","The group stopped advertising the events","Participants were required to attend every session"],
["It created several new passwords he must memorise","It removed the need for any main password","It made all of his accounts use the same weak password"],
["To make customers keep every cup permanently","To ensure only one café can use the system","To prevent deposits from being returned"],
["He had to choose a new study place every day","He began studying for much shorter periods","He stopped planning any study time in advance"],
["It lets students avoid learning the grammar rule","It replaces all written practice with conversation","It ensures partners always give the correct explanation"],
["Evening tickets became much more expensive","The cinema lost nearly all evening customers","People stopped going to Tuesday screenings"],
["They guaranteed that every student would enjoy the club","They replaced the need to attend club meetings","They showed only the dates of future events"],
["On planes, because the text says he never studies","At home, where background conversations are strongest","Only outdoors, because they require open space"],
["Making each section longer and more detailed","Removing the labels from the sheets","Giving students all sections at the same time without breaks"],
["The buses started moving faster on the entire route","Every resident received a free bus pass","The railway station was moved closer to the route"],
]
for i,(passage,q,ans,diff,exp) in enumerate(reading2,1):
    add(f"N15-T2-{i:03d}","Task 2","Reading","Reading: Detail" if i%3 else "Reading: Main Idea",diff,
        passage+"\n\n"+q,[ans,*reading2_distractors[i-1]],0,exp)

# ---------------- TASK 3: situations / matching ----------------
situations=[
("You need a place to practise a presentation with a projector before tomorrow.","Bookable presentation room with screen and projector"),
("You want to improve English conversation but can only attend online in the evening.","Evening online speaking group"),
("You have an old phone that still works and want it reused instead of thrown away.","Electronics donation and refurbishment point"),
("You want to exercise outdoors but prefer a beginner-friendly group that stays together.","Social beginner running group"),
("You need feedback on a university motivation letter, not a full English course.","Short application-writing review session"),
("You want to learn basic photo editing using free software on your own laptop.","Introductory digital photo-editing workshop"),
("You are looking for a quiet weekend activity where you can work independently on art.","Open studio session with individual workspaces"),
("You want to volunteer but are available for only one hour after school.","Short local volunteering shift"),
("You need to borrow a novel electronically because you cannot get to the library.","Library e-book service"),
("You want help choosing between several study programmes and understanding their differences.","Education guidance consultation"),
("You can already swim confidently and want to improve technique rather than learn the basics.","Intermediate swimming technique class"),
("You want to join a group that discusses books in English once a month.","Monthly English-language book club"),
("You need a low-cost place to print a large school poster.","Student print centre with large-format printing"),
("You want to learn how to make a simple budget for your personal spending.","Practical money-planning workshop"),
("You are interested in coding but first want to see whether it suits you before joining a long course.","One-day coding taster session"),
("You want to practise interview answers for a part-time job.","Mock interview clinic"),
("You have a bicycle with working brakes but need help adjusting the gears.","Community bicycle repair workshop"),
("You want to study with other students but still work on your own tasks.","Silent co-study session"),
("You would like to hear local musicians perform without buying an expensive concert ticket.","Free student music showcase"),
("You want to improve pronunciation and receive feedback on a few specific sounds.","Pronunciation mini-clinic"),
("You are new to the city and want a social event where it is normal to come alone.","Welcome mixer for new students"),
("You want to learn basic first aid in a classroom setting.","Introductory first-aid course"),
("You have several books you no longer need and want other students to use them.","Campus book exchange"),
("You need access to a computer for two hours to complete an online assignment.","Public computer desk reservation"),
("You want to learn how to check whether online images have been edited or taken out of context.","Digital media verification workshop"),
("You enjoy history and want a guided activity rather than exploring alone.","Guided local-history walk"),
("You want to practise English through games instead of formal exercises.","English board-game club"),
("You need a calm place for a video interview where background noise will be minimal.","Private study booth with reliable internet"),
("You want to try volunteering with children but need introductory training first.","Youth-volunteer orientation session"),
("You are preparing for exams and want a workshop specifically about planning revision time.","Exam revision planning workshop"),
]
situation_matches=[row[1] for row in situations]
for i,(situation,match) in enumerate(situations,1):
    distractors=[
        situation_matches[(i+5)%len(situation_matches)],
        situation_matches[(i+13)%len(situation_matches)],
        situation_matches[(i+21)%len(situation_matches)],
    ]
    add(f"N15-T3-{i:03d}","Task 3","Reading","Matching: Situations",1 if i%4==1 else (3 if i%7==0 else 2),
        "Choose the service or activity that best matches the situation.\n\n"+situation,
        [match,*distractors],0,
        "This option matches the person's goal, format and practical constraints.")

# ---------------- TASK 4: gapped text / cohesion ----------------
gaps=[
("I had planned to study at the library, but every desk was taken. _____. I found a quiet corner there and finished my work.","So I went to the smaller study centre across the street",1),
("Maks was nervous before his first debate. _____. By the second round, he was speaking much more confidently.","However, his teammates encouraged him and helped him prepare",2),
("The weather forecast predicted heavy rain for the afternoon. _____. We moved the picnic to a covered area in the park.","As a result, we changed our original plan",1),
("Our class collected old batteries for recycling for three weeks. _____. In total, we filled six large containers.","The response was much bigger than we had expected",1),
("I usually read news on my phone during breakfast. _____. Now I leave the phone in another room until I finish eating.","Recently, I realised this habit made my mornings feel rushed",2),
("The first version of our poster contained too much text. _____. The final version used shorter headings and more space.","We decided to simplify the design",1),
("Sara had never travelled alone by train before. _____. She checked the platform number twice and arrived early.","Because of this, she planned the journey carefully",1),
("The café introduced a reusable-cup discount last month. _____. More customers are now bringing their own cups.","The small incentive seems to be working",2),
("I tried to learn twenty new words in one evening. _____. The next day I could remember only a few of them.","That method turned out to be ineffective for me",1),
("The museum's new exhibition is popular with families. _____. Children can touch several models and try short experiments.","One reason is that many displays are interactive",1),
("Our group project was moving slowly because nobody knew who was responsible for each task. _____. Progress became much faster after that.","We created a simple list of roles and deadlines",2),
("The bus was delayed by roadworks. _____. I sent my teacher a message explaining that I might be late.","When I realised the delay would be significant",2),
("Nadia wanted to improve her listening skills. _____. After a few weeks, she noticed everyday speech was easier to follow.","She began listening to short English podcasts each day",1),
("The sports hall is being repaired this week. _____. All basketball practice will take place outside if the weather is suitable.","Therefore, the team needs a temporary alternative",1),
("We tested the new website with five students before launching it. _____. Their comments helped us simplify the registration form.","They immediately found several confusing parts",2),
("Petro usually avoided asking questions in class. _____. He started writing questions down and speaking to the teacher after lessons.","He still wanted to understand difficult topics better",2),
("The library used to close at six during exam season. _____. This year it will remain open until ten on weekdays.","Students had repeatedly asked for longer opening hours",1),
("I was disappointed when my application was rejected. _____. The feedback showed me how to improve the next one.","Still, I asked the organiser for comments",2),
("The volunteer event attracted more people than expected. _____. Organisers had to bring extra gloves and rubbish bags.","Nearly twice as many participants arrived",1),
("Our teacher asked us to compare two sources on the same topic. _____. We noticed that they presented some facts very differently.","The exercise made us look more carefully at how information was selected",3),
("I used to keep all my school files on the desktop. _____. Finding the right document became difficult.","As the number of files grew",1),
("The first rehearsal ended much later than planned. _____. For the next rehearsal, the director prepared a clearer schedule.","Too much time had been spent deciding what to practise next",2),
("The new cycle path connects the school with the railway station. _____. Several students now use bicycles for part of their journey.","This has created another practical travel option",1),
("Olha was unsure whether to join the science club. _____. She attended one open meeting before making a decision.","Rather than deciding immediately",2),
("The online course includes short quizzes after each unit. _____. Learners can quickly see which topics they should review.","These checks provide immediate feedback",1),
("We arrived at the exhibition just before closing time. _____. We decided to return the following morning.","There was not enough time to see everything properly",1),
("The school newspaper wanted more student contributions. _____. It introduced a simple online form for sending ideas.","One barrier was that students did not know how to submit them",2),
("I had assumed the workshop would be mostly theory. _____. We spent most of the session solving practical examples in small groups.","In fact, it was far more interactive",1),
("The path looked short on the map. _____. The steep hills made the walk much more tiring than expected.","Distance was not the only thing that mattered",2),
("The team reviewed comments from users every Friday. _____. Small problems were fixed before they became larger ones.","This regular habit made improvements easier to manage",2),
]
gap_answers=[row[1] for row in gaps]
for i,(text,ans,diff) in enumerate(gaps,1):
    distractors=[
        gap_answers[(i+3)%len(gap_answers)],
        gap_answers[(i+10)%len(gap_answers)],
        gap_answers[(i+18)%len(gap_answers)],
    ]
    add(f"N15-T4-{i:03d}","Task 4","Reading","Reading: Gapped Text",diff,
        "Choose the sentence that best completes the text.\n\n"+text,
        [ans,*distractors],0,
        "The correct sentence creates a logical and grammatical connection between the ideas before and after the gap.")

# ---------------- TASK 5: lexical cloze ----------------
lexical=[
("The teacher asked us to _____ attention to the final paragraph.","pay",["make","do","give"],1,"The fixed collocation is 'pay attention'.","Vocabulary: Collocations"),
("I accidentally _____ across an old photo while cleaning my desk.","came",["went","made","brought"],2,"'Come across' means find something by chance.","Vocabulary: Phrasal Verbs"),
("The new timetable will _____ effect next Monday.","take",["make","have","bring"],2,"The collocation is 'take effect'.","Vocabulary: Collocations"),
("She has a good _____ of humour and often makes the group laugh.","sense",["feeling","idea","mind"],1,"The standard phrase is 'a sense of humour'.","Vocabulary: Collocations"),
("We need to _____ a decision before the registration deadline.","make",["do","take","put"],1,"English uses 'make a decision'.","Vocabulary: Collocations"),
("The meeting was _____ off because the speaker was ill.","called",["put","set","made"],2,"'Call off' means cancel.","Vocabulary: Phrasal Verbs"),
("The course is designed to _____ students with practical experience.","provide",["offer","supply to","give with"],2,"'Provide someone with something' is the correct structure.","Vocabulary: Collocations"),
("Please _____ in mind that the library closes early on Friday.","bear",["hold","keep up","take"],3,"The fixed expression is 'bear in mind'.","Vocabulary: Collocations"),
("It took me a few days to _____ used to the new schedule.","get",["become to","make","turn"],1,"The expression is 'get used to'.","Vocabulary: Collocations"),
("The organisers had to _____ up with a new plan after the venue closed.","come",["get","bring","take"],2,"'Come up with' means think of or produce an idea.","Vocabulary: Phrasal Verbs"),
("The article _____ attention to the problem of food waste.","draws",["pays","makes","takes"],2,"'Draw attention to' is a common collocation.","Vocabulary: Collocations"),
("I could not _____ out why the printer was not working.","figure",["look","take","find to"],2,"'Figure out' means understand or solve.","Vocabulary: Phrasal Verbs"),
("The school plans to _____ a survey among students next month.","conduct",["make","perform up","set"],2,"We commonly 'conduct a survey'.","Vocabulary: Collocations"),
("Her explanation was clear and easy to _____ .","follow",["go","attend","lead"],1,"An explanation can be easy to 'follow'.","Vocabulary: Collocations"),
("The team worked hard to _____ the deadline.","meet",["reach to","arrive","touch"],1,"The collocation is 'meet a deadline'.","Vocabulary: Collocations"),
("I need to _____ down on the amount of time I spend scrolling.","cut",["bring","make","turn"],2,"'Cut down on' means reduce.","Vocabulary: Phrasal Verbs"),
("The workshop gave me the _____ to practise speaking in front of others.","opportunity",["occasionally","possibility to can","chance of to"],2,"'Give someone the opportunity to do something' is natural English.","Vocabulary: Collocations"),
("We should _____ advantage of the free revision session.","take",["make","have","get"],2,"The fixed phrase is 'take advantage of'.","Vocabulary: Collocations"),
("The new rule will _____ to all students from September.","apply",["use","belong","work on"],2,"A rule 'applies to' a group or situation.","Vocabulary: Collocations"),
("I was tired, but I decided to _____ on and finish the last exercise.","carry",["move","take","keep up it"],2,"'Carry on' means continue.","Vocabulary: Phrasal Verbs"),
("The teacher _____ an example to explain the difference.","gave",["did","made up of","put"],1,"We 'give an example'.","Vocabulary: Collocations"),
("The project aims to _____ awareness of online safety.","raise",["rise","lift up","grow"],2,"The collocation is 'raise awareness'.","Vocabulary: Collocations"),
("Please _____ the form in before Friday.","hand",["give","put to","take"],1,"'Hand in' means submit.","Vocabulary: Phrasal Verbs"),
("The museum offers a wide _____ of activities for schools.","range",["amount","numbering","size"],1,"A 'wide range of' is the natural expression.","Vocabulary: Collocations"),
("We need to _____ the problem before it becomes more serious.","address",["speak","tell","answer to"],3,"'Address a problem' means deal with it.","Vocabulary: Collocations"),
("The teacher told us not to _____ up after one difficult exercise.","give",["make","take","put"],1,"'Give up' means stop trying.","Vocabulary: Phrasal Verbs"),
("The event was a great _____ and attracted more than 500 visitors.","success",["successful","succeed","successfully"],1,"A noun is needed after 'a great'.","Vocabulary: Word Formation"),
("Her instructions were surprisingly _____, so everyone knew what to do.","clear",["clearly","clarity","clearnessly"],1,"An adjective is needed after 'were'.","Vocabulary: Word Formation"),
("The app allows users to _____ track of their study time.","keep",["hold","make","stay"],2,"The collocation is 'keep track of'.","Vocabulary: Collocations"),
("We finally _____ up the issue during the class meeting.","brought",["came","made","took"],3,"'Bring up an issue' means introduce it for discussion.","Vocabulary: Phrasal Verbs"),
]
for i,(stem,ans,wrong,diff,exp,sub) in enumerate(lexical,1):
    add(f"N15-T5-{i:03d}","Task 5","Use of English",sub,diff,
        "Choose the word that best completes the sentence.\n\n"+stem,
        [ans,*wrong],0,exp)

# ---------------- TASK 6: grammar cloze ----------------
grammar=[
("By the time we reached the station, the train _____ .","had left",["left","has left","leaves"],2,"Past Perfect marks the earlier past action.","Grammar: Tenses"),
("If I _____ more time this weekend, I will finish the project.","have",["had","will have","would have"],1,"First Conditional: if + Present Simple, will + infinitive.","Grammar: Conditionals"),
("This book _____ by thousands of students every year.","is used",["uses","is using","has use"],1,"Present Simple passive: is/are + past participle.","Grammar: Passive & Reported Speech"),
("She suggested _____ the meeting until Monday.","postponing",["to postpone","postpone","postponed"],2,"'Suggest' is followed by a gerund in this structure.","Grammar: Gerund & Infinitive"),
("I _____ this laptop for three years and it still works well.","have had",["had","am having","have"],2,"Present Perfect is used for a state continuing until now.","Grammar: Tenses"),
("You _____ bring your own calculator; one will be provided.","do not have to",["must not","cannot","should not to"],2,"'Do not have to' expresses lack of necessity.","Grammar: Modal Verbs"),
("The teacher asked me where I _____ the information.","had found",["find","have found","will find"],3,"Reported speech shifts the earlier action to Past Perfect.","Grammar: Passive & Reported Speech"),
("I am not used to _____ so early in the morning.","getting up",["get up","to get up","got up"],2,"'Be used to' is followed by a noun or gerund.","Grammar: Gerund & Infinitive"),
("When I called, Marta _____ for her exam, so I did not keep her long.","was studying",["studied","has studied","had study"],2,"Past Continuous describes an action in progress at a past moment.","Grammar: Tenses"),
("If he _____ the instructions more carefully, he would not have made that mistake.","had read",["read","would read","has read"],3,"Third Conditional uses Past Perfect in the if-clause.","Grammar: Conditionals"),
("The new sports centre _____ next month.","will be opened",["will open by","is opening by them","opens been"],2,"Future passive: will be + past participle.","Grammar: Passive & Reported Speech"),
("You _____ have seen Anna at school yesterday; she was at home all day.","cannot",["must","should","need"],3,"'Cannot have + past participle' expresses impossibility about the past.","Grammar: Modal Verbs"),
("I stopped _____ my messages while studying because it distracted me.","checking",["to checking","check","checked"],2,"'Stop doing' means cease an activity.","Grammar: Gerund & Infinitive"),
("We _____ dinner when the lights suddenly went out.","were having",["had","have had","are having"],2,"Past Continuous sets the background for a shorter past event.","Grammar: Tenses"),
("If I were you, I _____ that email once more before sending it.","would read",["will read","read","had read"],2,"Second Conditional advice: If I were you, I would...").replace if False else None,
]
# append manually to avoid tuple typo above
grammar=grammar[:14]+[
("If I were you, I _____ that email once more before sending it.","would read",["will read","read","had read"],2,"Second Conditional advice uses 'would + infinitive'.","Grammar: Conditionals"),
("The results _____ on the website as soon as they are available.","will be published",["will publish","are publishing","published"],2,"The subject receives the action, so future passive is required.","Grammar: Passive & Reported Speech"),
("He admitted _____ the wrong file by mistake.","sending",["to send","send","sent"],2,"'Admit' is normally followed by a gerund.","Grammar: Gerund & Infinitive"),
("I _____ my keys, so I cannot open the door.","have lost",["lost yesterday","had lost","am losing"],2,"Present Perfect links a recent past event with a present result.","Grammar: Tenses"),
("Unless you _____ now, you will miss the beginning of the lesson.","leave",["will leave","left","would leave"],2,"After 'unless' in a future condition, use Present Simple.","Grammar: Conditionals"),
("Students _____ use their phones during the test.","must not",["do not have to","could","might"],1,"'Must not' expresses prohibition.","Grammar: Modal Verbs"),
("She told me that she _____ the report the following day.","would finish",["will finish","finishes","has finished"],2,"In reported speech, 'will' usually shifts to 'would'.","Grammar: Passive & Reported Speech"),
("We decided _____ a short break before continuing.","to take",["taking","take","took"],1,"'Decide' is followed by the infinitive with 'to'.","Grammar: Gerund & Infinitive"),
("This time next week, we _____ our final exams.","will be taking",["take","have taken","were taking"],3,"Future Continuous describes an action in progress at a future time.","Grammar: Tenses"),
("If the weather _____ better yesterday, we would have gone hiking.","had been",["was","would be","has been"],3,"Third Conditional requires Past Perfect in the condition.","Grammar: Conditionals"),
("The classroom _____ before the students arrived.","had been cleaned",["had cleaned","was cleaning","has been clean"],3,"Past Perfect passive shows the cleaning happened before another past action.","Grammar: Passive & Reported Speech"),
("You _____ check the deadline again; I am not completely sure of the date.","should",["must not","cannot","would have"],1,"'Should' is suitable for advice.","Grammar: Modal Verbs"),
("I remember _____ that museum when I was younger.","visiting",["to visit","visit","visited to"],2,"'Remember doing' refers to a memory of a past action.","Grammar: Gerund & Infinitive"),
("She _____ English since she was eight years old.","has studied",["studied","is studying since","had studied now"],2,"Present Perfect with 'since' describes an activity continuing to the present.","Grammar: Tenses"),
("Had I known about the change, I _____ earlier.","would have arrived",["will arrive","would arrive","had arrived"],3,"This is an inverted Third Conditional.","Grammar: Conditionals"),
("The manager said that all applications _____ by Friday.","had to be submitted",["have submit","must submitting","were submit"],3,"The passive infinitive 'be submitted' is required after 'had to'.","Grammar: Passive & Reported Speech"),
]
assert len(grammar)==30, len(grammar)
for i,(stem,ans,wrong,diff,exp,sub) in enumerate(grammar,1):
    add(f"N15-T6-{i:03d}","Task 6","Use of English",sub,diff,
        "Choose the option that best completes the sentence.\n\n"+stem,
        [ans,*wrong],0,exp)

assert len(items)==180, len(items)
json_path=OUT/"nmt_2026_pack_v1_5.json"
json_path.write_text(json.dumps(items,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")

def sql_text(s):
    return "NULL" if s is None else "'"+str(s).replace("'","''")+"'"

def sql_json(obj):
    return sql_text(json.dumps(obj,ensure_ascii=False,separators=(",",":")))+"::jsonb"

lines=[
"-- Neta NMT v1.5: NMT-2026 Content Pack #2 (180 original questions)",
"-- Safe to run more than once. Adds Pack #2 without deleting Pack #1.",
"",
"ALTER TABLE public.questions ADD COLUMN IF NOT EXISTS question_code text;",
"ALTER TABLE public.questions ADD COLUMN IF NOT EXISTS nmt_task_type text;",
"ALTER TABLE public.questions ADD COLUMN IF NOT EXISTS content_pack text;",
"ALTER TABLE public.questions ADD COLUMN IF NOT EXISTS quality_status text NOT NULL DEFAULT 'approved';",
"CREATE UNIQUE INDEX IF NOT EXISTS idx_questions_question_code ON public.questions(question_code);",
"CREATE INDEX IF NOT EXISTS idx_questions_nmt_simulation ON public.questions(nmt_task_type, quality_status) WHERE is_active = true AND is_diagnostic = false;",
"",
]
cols=["question_code","topic","difficulty","question_text","options","correct_option","explanation","category","sub_category","section","is_active","is_diagnostic","nmt_task_type","content_pack","quality_status"]
for x in items:
    vals=[sql_text(x["question_code"]),sql_text(x["topic"]),str(x["difficulty"]),sql_text(x["question_text"]),sql_json(x["options"]),str(x["correct_option"]),sql_text(x["explanation"]),sql_text(x["category"]),sql_text(x["sub_category"]),sql_text(x["section"]),"true","false",sql_text(x["nmt_task_type"]),sql_text(x["content_pack"]),sql_text(x["quality_status"])]
    lines.append(f"INSERT INTO public.questions ({', '.join(cols)}) VALUES ({', '.join(vals)})")
    lines.append("ON CONFLICT (question_code) DO UPDATE SET")
    lines.append(" topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,")
    lines.append(" correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,")
    lines.append(" section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,")
    lines.append(" content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;")
    lines.append("")
lines += [
"-- Verification",
"SELECT nmt_task_type, count(*) AS questions FROM public.questions WHERE content_pack='v1.5-nmt2026-pack2' GROUP BY nmt_task_type ORDER BY nmt_task_type;",
"SELECT count(*) AS total_pack2_questions FROM public.questions WHERE content_pack='v1.5-nmt2026-pack2';",
"SELECT count(*) AS total_approved_regular_questions FROM public.questions WHERE is_active=true AND is_diagnostic=false AND quality_status='approved';",
]
(ROOT/"supabase_v1_5_content_pack.sql").write_text("\n".join(lines)+"\n",encoding="utf-8")
print(f"Built {len(items)} questions -> {json_path}")
