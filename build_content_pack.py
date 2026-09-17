from __future__ import annotations
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / "content"
OUT.mkdir(exist_ok=True)
items = []

def add(code, task, category, sub, difficulty, question, options, correct, explanation):
    assert len(options) == 4
    assert 0 <= correct <= 3
    # Avoid answer-position patterns: distribute correct answers evenly A-D.
    target = (int(code.rsplit("-", 1)[-1]) - 1) % 4
    options = list(options)
    options[correct], options[target] = options[target], options[correct]
    correct = target
    items.append({
        "question_code": code,
        "topic": "reading" if category == "Reading" else "use_of_english",
        "difficulty": difficulty,
        "question_text": question,
        "options": {"A": options[0], "B": options[1], "C": options[2], "D": options[3]},
        "correct_option": correct,
        "explanation": explanation,
        "category": category,
        "sub_category": sub,
        "section": "NMT",
        "is_active": True,
        "is_diagnostic": False,
        "nmt_task_type": task,
        "content_pack": "v1.4-nmt2026-pack1",
        "quality_status": "approved",
    })

# ---------------- TASK 1: short-text matching ----------------
task1 = [
("T1-001",1,"NOTICE: Saturday English Speaking Club. Small groups, games and short discussions. No preparation needed. B1+ recommended.",
 ["A student who wants relaxed speaking practice", "A student looking for a grammar exam", "A teacher needing a classroom", "A beginner who cannot understand basic English"],0,"The notice is specifically for informal speaking practice in small groups."),
("T1-002",1,"CITY LIBRARY: Exam Week. Quiet study room open until 10 p.m. Bring your student card. Individual study only.",
 ["Someone who wants a late, quiet place to study", "Someone planning a group birthday party", "Someone looking for sports training", "Someone who needs to borrow a laptop for a month"],0,"The key details are late opening and individual quiet study."),
("T1-003",1,"BEGINNER CODING LAB: Build your first simple website in two hours. Laptops provided. No previous programming experience required.",
 ["An experienced developer seeking a job", "A complete beginner interested in web coding", "A designer selling artwork", "A student preparing for a biology test"],1,"The lab is designed for people with no prior programming experience."),
("T1-004",2,"VOLUNTEERS NEEDED: Sunday river clean-up, 9:00–12:00. Gloves and bags supplied. Wear comfortable shoes and bring water.",
 ["Someone who wants to help the environment outdoors", "Someone looking for paid office work", "Someone wanting an indoor concert", "Someone who needs professional sports equipment"],0,"The activity is an outdoor environmental volunteering event."),
("T1-005",1,"MUSEUM LATE NIGHT: Free entry for students after 6 p.m. on Friday. Modern art galleries remain open until 9 p.m.",
 ["A student who wants an inexpensive evening museum visit", "A family looking for a morning zoo trip", "A tourist wanting a guided mountain hike", "A student needing a language course"],0,"Students can visit the museum free in the evening."),
("T1-006",2,"BIKE CHECK DAY: Mechanics will inspect brakes, tyres and gears free of charge. Repairs requiring new parts are paid separately.",
 ["A cyclist who wants a free safety inspection", "Someone who wants to buy a new car", "A person looking for a driving lesson", "A cyclist needing guaranteed free replacement parts"],0,"The inspection is free, while parts are not."),
("T1-007",1,"BOOK SWAP: Bring up to five books you have finished and exchange them for others. Please bring books in good condition.",
 ["A reader who wants to exchange used books", "An author seeking a publisher", "A student wanting to print a textbook", "A collector looking for rare coins"],0,"The event is for exchanging books people already own."),
("T1-008",2,"PHOTOGRAPHY WALK: Learn to improve composition using any phone or camera. Sunday, 15:00. Suitable for beginners.",
 ["A beginner wanting practical photography tips", "A professional needing studio rental", "Someone who wants to repair a camera", "A person searching for a painting class"],0,"The walk teaches beginner composition with phones or cameras."),
("T1-009",1,"SCHOOL NEWSPAPER: We need students who enjoy interviewing people, writing short articles or taking photos. Weekly meeting: Wednesday.",
 ["A student interested in journalism or photography", "A student who only wants maths tutoring", "A person seeking full-time employment", "A teacher looking for exam papers"],0,"The newspaper needs writers, interviewers and photographers."),
("T1-010",2,"SCHOLARSHIP Q&A: Online session about application documents, deadlines and common mistakes. Questions can be sent in advance.",
 ["A student preparing a scholarship application", "A student learning to swim", "A tourist booking a hotel", "A musician looking for rehearsal space"],0,"The session explains scholarship applications and deadlines."),
("T1-011",1,"THEATRE AUDITIONS: Looking for students aged 15–18 for a school comedy. Prepare a one-minute monologue. Rehearsals begin next month.",
 ["A teenager who wants to act in a play", "A student wanting to watch a film", "A parent looking for childcare", "A musician wanting to sell an instrument"],0,"The notice invites teenagers to audition for acting roles."),
("T1-012",2,"SWIMMING BASICS: Four Saturday lessons for people who can enter the water confidently but cannot yet swim 25 metres.",
 ["A beginner swimmer wanting basic lessons", "A competitive swimmer training for a race", "Someone afraid to enter a swimming pool", "A person wanting diving certification"],0,"The lessons are for basic swimmers who are comfortable in water."),
("T1-013",2,"ROBOTICS OPEN LAB: Teams can test small robots and get advice from mentors. Participants should already know basic programming.",
 ["A team with some programming knowledge developing a robot", "A complete beginner who has never used a computer", "A student wanting an English speaking club", "A family wanting a museum tour"],0,"The lab expects basic programming knowledge and supports robot testing."),
("T1-014",1,"LOCAL FOOD MARKET: Saturday 8:00–13:00. Fresh bread, cheese, vegetables and honey from nearby farms. Bring your own bag if possible.",
 ["Someone wanting to buy locally produced food", "Someone looking for electronics", "Someone needing a restaurant reservation", "Someone wanting to rent a bicycle"],0,"The market sells food from nearby farms."),
("T1-015",2,"STUDY SKILLS WEBINAR: Learn how to plan revision, avoid distractions and use short review sessions effectively. Free registration.",
 ["A student who wants to organize exam preparation better", "A teacher applying for a new job", "A tourist learning city history", "A student seeking advanced coding practice"],0,"The webinar focuses on planning and effective revision."),
("T1-016",1,"ART SUPPLIES SALE: Student discount this weekend on sketchbooks, brushes and acrylic paints. Student ID required.",
 ["An art student buying materials", "A runner buying sports shoes", "A reader buying novels", "A programmer buying a keyboard"],0,"The discount applies to art materials and requires student ID."),
("T1-017",2,"HIKING CLUB: Easy 8 km route this Sunday. Participants need comfortable footwear, rain protection and a packed lunch.",
 ["Someone looking for a beginner-friendly day hike", "Someone seeking an indoor fitness class", "Someone wanting a luxury bus tour", "Someone needing climbing equipment training"],0,"The route is described as easy and requires basic outdoor preparation."),
("T1-018",1,"FILM CLUB: Watch an English-language film with English subtitles, then discuss it together. Thursday at 17:30.",
 ["A learner who wants to combine film and English practice", "A person looking for silent meditation", "A student wanting a chemistry laboratory", "A musician searching for a concert"],0,"The activity combines an English film and discussion."),
("T1-019",2,"CAFÉ WEEKEND ASSISTANT: 8 hours on Saturday. Tasks include taking orders, clearing tables and helping customers. Training provided.",
 ["Someone seeking short weekend customer-service work", "Someone looking for a full-time engineering role", "A student wanting unpaid volunteering", "A chef seeking advanced professional training"],0,"This is short weekend work involving customer service."),
("T1-020",2,"LANGUAGE EXCHANGE: Practise Ukrainian and English with international students. You should be comfortable holding a simple conversation in English.",
 ["Someone who can already have a basic English conversation", "Someone who wants a silent reading room", "A person needing translation certification", "A complete beginner learning the alphabet"],0,"The exchange requires enough English for a simple conversation."),
]
for code,d,text,opts,c,exp in task1:
    add("N14-"+code,"Task 1","Reading","Matching: Notices",d,"Read the notice and choose the person it is most suitable for.\n\n"+text,opts,c,exp)

# ---------------- TASK 2: reading multiple choice ----------------
task2 = [
("T2-001",1,"Maya used to revise only the night before a test. This term, she began studying for twenty minutes each evening. She says she now feels calmer before exams and remembers more afterwards.","What changed in Maya's study routine?",["She studies in shorter regular sessions","She stopped taking tests","She studies only in the morning","She studies with a private teacher"],0,"The passage says she now studies for twenty minutes each evening."),
("T2-002",2,"A small café near the station removed half of its indoor tables and added a covered outdoor area. The owner says customers stay longer there during warm months, while the indoor space feels less crowded.","Why did the café change its seating?",["To create a more comfortable use of space","To stop serving customers indoors","To reduce the number of customers","To turn the café into a shop"],0,"The change made indoor seating less crowded and added useful outdoor space."),
("T2-003",2,"Leo bought a second-hand laptop because a new model was outside his budget. Before paying, he checked the battery, keyboard and screen and asked for a short warranty from the shop.","What does the passage suggest about Leo?",["He made a careful purchase","He wanted the most expensive model","He never checked the laptop","He borrowed the laptop from a friend"],0,"He checked key parts and asked for a warranty before buying."),
("T2-004",1,"The town's new bus app shows live arrival times. It does not sell tickets yet, but passengers can save favourite stops and receive service alerts.","Which feature is NOT available in the app?",["Live arrival times","Saved favourite stops","Ticket purchases","Service alerts"],2,"The text explicitly says the app does not sell tickets yet."),
("T2-005",2,"Nina joined a school debate club mainly to become more confident speaking in front of others. After two months, she noticed another benefit: she had become better at listening carefully before replying.","What unexpected benefit did Nina notice?",["She learned to listen more carefully","She stopped feeling nervous immediately","She won every debate","She began writing longer essays"],0,"Listening carefully is described as an additional benefit."),
("T2-006",2,"A community garden gives local residents small plots to grow vegetables. Members share tools and water, but each person is responsible for looking after their own plot.","What are members expected to do individually?",["Look after their own growing area","Buy all shared tools","Pay for everyone's water","Manage the entire garden"],0,"Each member is responsible for their own plot."),
("T2-007",3,"When a software company introduced one meeting-free afternoon each week, managers worried communication would suffer. Instead, employees reported finishing more focused work, while teams moved routine updates to short written messages.","What was the result of the change?",["Focused work increased without stopping communication","Employees refused to communicate","Managers added more long meetings","The company ended written updates"],0,"The company preserved communication while increasing focused work."),
("T2-008",1,"The science centre's new exhibition is designed for visitors to touch, test and move many of the displays. Staff say the goal is to make difficult ideas easier to understand through direct experience.","What is special about the exhibition?",["It is highly interactive","It is only for scientists","Visitors cannot touch anything","It focuses entirely on paintings"],0,"Visitors are encouraged to interact directly with the displays."),
("T2-009",2,"Oleh cycles to college when the weather is dry, but on rainy days he takes the metro. He says cycling is usually faster during morning traffic and also gives him some exercise.","Why does Oleh often choose to cycle?",["It can save time and provides exercise","The metro is permanently closed","He dislikes all public transport","His college is outside the city"],0,"He mentions both speed in traffic and exercise."),
("T2-010",2,"A bookshop began placing short staff recommendations beside selected novels. Sales of those books increased, especially when the notes explained who might enjoy the story rather than simply saying it was good.","Which recommendations were most effective?",["Those describing the type of reader who might enjoy the book","Those using only one-word praise","Those hiding the book's subject","Those written by customers who had not read the book"],0,"The passage says recommendations worked best when they explained who would enjoy the story."),
("T2-011",3,"Researchers asked two groups of students to learn the same list of words. One group reread the list several times; the other repeatedly tried to recall the words without looking. A week later, the recall group remembered more.","What conclusion best matches the study?",["Trying to retrieve information can strengthen memory","Reading once always guarantees long-term memory","Students should avoid testing themselves","Learning vocabulary is impossible without a teacher"],0,"The group practising recall remembered more after a week."),
("T2-012",1,"The local pool now opens at 6:30 on weekdays. The earlier time was introduced after many residents said they wanted to swim before work or school.","Why was the opening time changed?",["To meet demand for early swimming","To reduce the number of swimmers","To prepare for evening competitions","To close the pool during weekends"],0,"Residents requested an earlier time before work or school."),
("T2-013",2,"Sara planned to buy a printed travel guide but finally downloaded an offline city map instead. She knew mobile internet might be expensive abroad and wanted directions that would work without a connection.","Why did Sara choose an offline map?",["It works without mobile internet","It contains no street names","It is always more detailed than every guide","It requires constant online access"],0,"Her main concern was using directions without internet access."),
("T2-014",2,"A school replaced some traditional homework with short projects in which students choose examples from everyday life. Teachers found that students asked more questions in class because they wanted to check whether their examples really fit the topic.","How did the projects affect students?",["They encouraged more classroom questions","They eliminated the need for lessons","They made students avoid real-life examples","They reduced all homework to zero"],0,"Students asked more questions to verify their examples."),
("T2-015",3,"A small clothing brand started publishing repair guides for its jackets. At first this seemed likely to reduce sales, but the company says customers became more loyal because they trusted a brand that helped products last longer.","Why did the repair guides help the company?",["They increased customer trust and loyalty","They forced customers to buy new jackets immediately","They made repairs impossible","They removed the need for customer service"],0,"Helping products last longer strengthened trust and loyalty."),
("T2-016",1,"The university café offers a discount to customers who bring a reusable cup. The programme aims to reduce the number of disposable cups used each day.","What is the purpose of the discount?",["To reduce waste","To increase the price of coffee","To sell more disposable cups","To stop customers bringing drinks"],0,"The discount encourages reusable cups and therefore less waste."),
("T2-017",2,"After moving into a noisy street, Daniel first tried studying with music. He soon found that quiet background noise through headphones worked better because songs distracted him from reading.","Why did Daniel stop using music while studying?",["Songs distracted his attention","His headphones stopped working","He no longer needed to study","The street became completely silent"],0,"The passage says songs distracted him from reading."),
("T2-018",3,"A local history project asked older residents to record memories of the neighbourhood. Students then compared these stories with old photographs and maps. The aim was not to prove every memory exact, but to understand how people experienced changes in the area.","What was the main goal of the project?",["To explore personal experiences of local change","To prove every memory was perfectly accurate","To replace maps with interviews","To create a tourist advertisement"],0,"The project focused on how residents experienced changes."),
("T2-019",2,"An online course allows students to watch recorded lessons at any time, but live workshops are held twice a month. The workshops are used mainly for questions, discussion and practical tasks.","What are the live workshops mainly for?",["Interaction and practice","Watching the same recorded lesson silently","Taking attendance only","Downloading course files"],0,"Questions, discussion and practical tasks are interactive activities."),
("T2-020",2,"The city planted young trees along several busy roads. Officials do not expect an immediate change in summer temperatures, but they hope the trees will provide more shade as they grow.","Why will the full benefit take time?",["The trees need time to grow","The roads will close permanently","Shade only works in winter","The city plans to remove the trees soon"],0,"Young trees need to mature before they provide substantial shade."),
]
for code,d,passage,q,opts,c,exp in task2:
    sub = "Reading: Detail" if code[-1] in "124678" else ("Reading: Inference" if d==3 else "Reading: Main Idea")
    add("N14-"+code,"Task 2","Reading",sub,d,passage+"\n\n"+q,opts,c,exp)

# ---------------- TASK 3: matching situations ----------------
task3 = [
("T3-001",1,"I want to improve my English speaking, but I am busy on weekdays and prefer learning with other people.",["Saturday Conversation Group","Self-paced Grammar PDF","Monday Morning Writing Class","Private Pronunciation Test"],0,"A Saturday group directly matches the need for weekend speaking practice with others."),
("T3-002",2,"I already know basic Python and want a short course where I can build a real project rather than only watch lectures.",["Python Project Weekend","Introduction to Computers","History of Programming Talk","Typing Skills for Beginners"],0,"The project weekend fits someone with basics who wants hands-on work."),
("T3-003",1,"I need a place to study after 8 p.m. and I do not want group activities.",["Late Quiet Study Hall","Afternoon Debate Club","Morning Sports Centre","Weekend Music Workshop"],0,"The late quiet hall matches both time and individual study."),
("T3-004",2,"I enjoy drawing and want feedback on my work, but I cannot attend every week.",["Monthly Portfolio Clinic","Daily Painting Course","Weekly Exam Club","Online Maths Marathon"],0,"A monthly portfolio clinic offers feedback without weekly attendance."),
("T3-005",2,"I want to start running, but I have never trained regularly and I am worried about doing too much too soon.",["Beginner 5K Plan","Advanced Marathon Team","Competitive Sprint Trials","Mountain Race Club"],0,"A beginner plan is appropriate for gradually starting regular running."),
("T3-006",1,"I would like to volunteer with animals, but I can only help for a few hours on Sunday.",["Sunday Animal Shelter Helpers","Weekday Office Internship","Full-time Farm Manager","Evening Language Exchange"],0,"The Sunday shelter role matches the time and interest in animals."),
("T3-007",2,"I need help preparing a CV and practising common interview questions for my first part-time job.",["Student Job Workshop","Advanced Business Law","Photography Walk","Creative Writing Circle"],0,"A student job workshop directly covers CVs and interviews."),
("T3-008",2,"I want to practise photography outdoors and I only have a smartphone, not a professional camera.",["Phone Photography Walk","Studio Lighting for Professionals","Camera Repair Lab","Film Editing Theory"],0,"The phone photography walk suits outdoor practice with a smartphone."),
("T3-009",1,"I like reading fiction and want to discuss books with people my age once a month.",["Monthly Teen Book Club","Daily News Writing Course","Silent Library Membership","Academic Research Seminar"],0,"The monthly teen book club fits fiction discussion and frequency."),
("T3-010",2,"I understand grammar rules quite well, but I often choose the wrong word in context during tests.",["Vocabulary in Context Clinic","Basic Alphabet Course","Speaking Only Club","Handwriting Workshop"],0,"The vocabulary clinic targets word choice in context."),
("T3-011",3,"I want a course that gives me deadlines and teacher feedback because I usually stop self-study courses after a week.",["Guided Course with Weekly Feedback","Open Video Library","Independent Reading List","One-day Exhibition"],0,"Regular deadlines and feedback address the learner's difficulty with self-study."),
("T3-012",2,"I want to learn basic cooking, especially inexpensive meals I can make after school.",["Budget Cooking for Students","Advanced Pastry Masterclass","Restaurant Management Theory","Professional Chef Competition"],0,"The student budget course matches beginner, inexpensive after-school cooking."),
("T3-013",1,"I am interested in local history but prefer walking around the city to sitting in a lecture room.",["Historical Walking Tour","Archive Research Lecture","Online Grammar Class","Indoor Chess Tournament"],0,"A walking tour combines local history with being outdoors in the city."),
("T3-014",2,"I need to improve how I organize notes from different subjects before final exams.",["Revision and Note-Making Workshop","Beginner Guitar Lesson","Weekend Cycling Club","Job Interview Practice"],0,"The workshop directly targets revision and note organization."),
("T3-015",2,"I can swim comfortably but want to improve technique rather than learn from the beginning.",["Intermediate Stroke Clinic","Water Confidence for Beginners","Lifeguard Recruitment","Children's First Swim"],0,"An intermediate technique clinic fits an already comfortable swimmer."),
("T3-016",3,"I want to learn about starting a small online project and test whether people actually want it before spending much money.",["Lean Project Validation Workshop","Corporate Accounting Degree","Advanced Graphic Design Diploma","Public Speaking Competition"],0,"Validation focuses on testing demand before significant spending."),
("T3-017",1,"I want a free activity where I can practise English by watching something entertaining.",["English Film Evening","Private Exam Tutoring","Paid Translation Course","Silent Reading Test"],0,"A film evening is entertaining and can provide language practice."),
("T3-018",2,"I am confident speaking English but need more practice with reading long texts quickly for exams.",["Timed Reading Practice","Beginner Conversation Club","Pronunciation Basics","Creative Drawing Class"],0,"Timed reading practice addresses exam reading speed."),
("T3-019",2,"I want to repair simple problems on my bicycle myself instead of visiting a shop every time.",["Basic Bike Maintenance","Road Racing Team","Car Mechanics Diploma","City Transport History"],0,"Basic maintenance teaches simple bicycle repairs."),
("T3-020",1,"I want to meet international students and exchange languages in a relaxed setting.",["Language Exchange Café","Formal Written Exam","Private Coding Lesson","Individual Silent Study"],0,"A language exchange café is a relaxed social language setting."),
]
for code,d,sit,opts,c,exp in task3:
    add("N14-"+code,"Task 3","Reading","Matching: Situations",d,"Choose the option that best matches this person.\n\n"+sit,opts,c,exp)

# ---------------- TASK 4: gapped text ----------------
task4 = [
("T4-001",1,"I used to keep all my school deadlines in my head. _____ Now I check it every evening and rarely forget an assignment.",["Then I started using a simple calendar app.","However, I stopped studying completely.","For example, calendars are always expensive.","As a result, I never write anything down."],0,"The next sentence refers to checking 'it', so a calendar app fits logically."),
("T4-002",2,"The park was once almost empty in the evenings. The city added better lighting and repaired the paths. _____ Families and runners now use it much more often after work.",["As a result, people began to feel safer there.","In contrast, the park was moved to another city.","Nevertheless, the paths were removed again immediately.","For this reason, nobody can enter the park."],0,"Improved lighting and paths logically lead to greater safety and more use."),
("T4-003",2,"Online lessons can be convenient because students can learn from home. _____ Without a routine, it is easy to postpone work until later.",["However, they still require self-discipline.","Therefore, every online lesson is easier than school.","For example, internet access is never necessary.","Similarly, students cannot choose when to study."],0,"The contrast is convenience versus the need for self-discipline."),
("T4-004",1,"Lena wanted to read more books this year. She decided not to set an enormous target. _____ After a few months, reading had become part of her normal routine.",["Instead, she began with ten pages a day.","As a result, she gave away every book she owned.","However, she stopped reading on the first day.","For example, she bought a television."],0,"A small daily target explains how reading became a routine."),
("T4-005",2,"The school café introduced a reusable cup discount. At first, only a few students brought their own cups. _____ By the end of the term, the number had increased significantly.",["Teachers then reminded students about the programme.","The café then banned all drinks.","No one was allowed to enter the building.","The discount was removed before it began."],0,"Reminders can logically explain the later increase in participation."),
("T4-006",2,"Mark was nervous before giving presentations. He began practising them aloud at home and recording himself. _____ This helped him notice where he spoke too quickly.",["He listened to the recordings afterwards.","He deleted every presentation before speaking.","He decided never to practise again.","He turned off the microphone during class."],0,"Listening to recordings explains how he noticed his speaking speed."),
("T4-007",3,"Many people assume creativity appears only when inspiration arrives. In reality, creative professionals often rely on routines. _____ Regular work creates more opportunities for useful ideas to appear.",["They set aside time to produce ideas even on ordinary days.","They avoid working until the perfect idea arrives.","They refuse to repeat any process.","They believe schedules always destroy creativity."],0,"A regular creative routine supports the final sentence."),
("T4-008",2,"The town wanted more people to cycle to the centre. It created protected bike lanes on several busy roads. _____ Surveys later showed that new cyclists felt more confident using those routes.",["The lanes separated cyclists from faster traffic.","The roads were closed to bicycles.","All traffic signs were removed.","Cyclists were asked to use only pavements."],0,"Protected separation from traffic explains increased confidence."),
("T4-009",1,"I often forgot new vocabulary after learning it once. _____ Reviewing words at increasing intervals helped me remember them much longer.",["Then I tried spaced repetition.","So I stopped learning languages.","Nevertheless, I threw away my notes.","For example, I avoided old words completely."],0,"Spaced repetition is directly explained in the next sentence."),
("T4-010",2,"A local shop began offering online ordering for customers who were short on time. _____ Customers could then collect their purchases on the way home.",["Orders were prepared before the customer arrived.","The shop stopped selling products.","Customers had to wait longer than before by design.","The collection desk opened only once a year."],0,"Prepared orders make convenient collection possible."),
("T4-011",3,"Students sometimes highlight almost every line of a textbook because everything seems important. _____ A better strategy is to identify the central idea first and mark only information that supports it.",["This can make the highlighting less useful.","This always guarantees perfect memory.","This removes the need to understand the text.","This makes every textbook shorter."],0,"If everything is highlighted, the method loses its ability to show what matters."),
("T4-012",2,"The weather forecast predicted heavy rain during our trip. We did not cancel the walk. _____ In the end, we stayed dry enough to enjoy the day.",["Instead, we packed waterproof jackets and changed the route.","Therefore, we left all rain protection at home.","However, we chose the longest exposed route possible.","As a result, we forgot to check the weather."],0,"Preparing for rain explains why the walk still worked."),
("T4-013",1,"The library created a shelf called 'Staff Picks'. Each recommendation included two short sentences about the book. _____ Many visitors said the notes helped them choose faster.",["The notes focused on what kind of reader might enjoy it.","The books were hidden from visitors.","The shelf contained no titles.","The staff refused to describe any book."],0,"Useful reader-focused notes logically help visitors choose."),
("T4-014",2,"Emma wanted to spend less time checking her phone while studying. She placed it in another room for thirty minutes at a time. _____ She found it easier to concentrate because notifications no longer interrupted her.",["She checked messages during each break instead.","She kept every notification at maximum volume.","She opened social media on another device continuously.","She stopped taking any study breaks."],0,"Checking messages during planned breaks supports fewer interruptions while studying."),
("T4-015",3,"A team kept making the same small mistakes during a project. Instead of blaming individuals, they held a short review after each stage. _____ Over time, repeated errors became less common.",["They recorded what went wrong and changed the process.","They agreed never to discuss mistakes.","They made the process more confusing on purpose.","They removed all deadlines and responsibilities."],0,"Identifying causes and changing the process explains fewer repeated errors."),
("T4-016",2,"The community centre offered a free trial week for its fitness classes. _____ Many participants later joined because they had discovered which class suited them best.",["People could try several different sessions before choosing.","Everyone had to buy a yearly membership first.","Only professional athletes were admitted.","The centre closed during the trial week."],0,"Trying several classes explains better-informed membership choices."),
("T4-017",1,"We arrived at the station earlier than necessary. _____ We had enough time to find the correct platform and buy water before boarding.",["That turned out to be useful.","As a result, we missed the train immediately.","However, the station did not exist.","Therefore, we went home without checking anything."],0,"The next sentence lists benefits of arriving early."),
("T4-018",2,"The teacher stopped giving one long vocabulary test at the end of each month. Instead, she used short weekly quizzes. _____ Students also received feedback sooner and could review weak words before the next quiz.",["This encouraged more regular revision.","This made vocabulary disappear from the course.","This prevented students from seeing their mistakes.","This meant students studied only once a month."],0,"Frequent quizzes naturally encourage regular revision and faster feedback."),
("T4-019",3,"A company asked customers why they abandoned an online order. Many said the checkout required too many steps. _____ Completion rates improved soon after.",["The company simplified the form and removed unnecessary fields.","The company added several extra pages to checkout.","The company hid the final price until after payment.","The company stopped listening to customer feedback."],0,"Simplifying the checkout directly addresses the reported problem."),
("T4-020",2,"My first attempt at baking bread was disappointing because I cut it immediately after it came out of the oven. _____ The next loaf had a much better texture.",["The second time, I let it cool before slicing it.","The second time, I used no flour at all.","After that, I stopped using an oven.","Then I placed the dough in the freezer before baking."],0,"Letting bread cool before slicing explains the improved texture."),
]
for code,d,passage,opts,c,exp in task4:
    add("N14-"+code,"Task 4","Reading","Reading: Gapped Text",d,passage,opts,c,exp)

# ---------------- TASK 5: lexical cloze ----------------
task5 = [
("T5-001",1,"The new study room is usually quiet, so it is a good place to _____ on difficult homework.",["concentrate","celebrate","depend","invite"],0,"The natural collocation is 'concentrate on' homework."),
("T5-002",2,"Please _____ attention to the instructions before you begin the task.",["pay","make","do","take"],0,"The fixed collocation is 'pay attention'."),
("T5-003",2,"The organisers had to _____ the outdoor event because of the storm.",["cancel","solve","borrow","earn"],0,"An event can be cancelled because of bad weather."),
("T5-004",1,"I was tired, but a short walk helped me _____ my energy.",["regain","refuse","reduce","replace"],0,"'Regain energy' means get your energy back."),
("T5-005",2,"This app allows users to _____ their progress over several weeks.",["track","catch","hold","reach"],0,"'Track progress' means monitor how it changes over time."),
("T5-006",2,"The teacher asked us to _____ an example from everyday life.",["provide","avoid","remove","divide"],0,"'Provide an example' is the correct collocation."),
("T5-007",3,"The company decided to _____ feedback before changing the product.",["gather","rise","achieve","deliver"],0,"Companies commonly 'gather feedback' from users."),
("T5-008",2,"It took me a few days to _____ used to the new timetable.",["get","make","turn","bring"],0,"The expression is 'get used to'."),
("T5-009",2,"We were running _____ of time, so we skipped the final activity.",["out","off","away","over"],0,"'Run out of time' means have almost no time left."),
("T5-010",1,"The museum is within walking _____ of the station.",["distance","length","space","route"],0,"The fixed phrase is 'within walking distance'."),
("T5-011",3,"The article _____ an important point about how habits are formed.",["raises","lifts","grows","builds"],0,"We 'raise a point' or 'raise an issue' in discussion."),
("T5-012",2,"I did not recognise him at first because he had _____ his hairstyle completely.",["changed","turned","exchanged","moved"],0,"'Change your hairstyle' is the natural verb choice."),
("T5-013",2,"The course is designed to _____ students with practical interview skills.",["equip","fill","cover","dress"],0,"'Equip someone with skills' means give them the abilities they need."),
("T5-014",3,"The manager asked the team to _____ up with three possible solutions.",["come","get","take","put"],0,"The phrasal verb is 'come up with' an idea or solution."),
("T5-015",1,"Make sure you _____ a copy of the file before editing it.",["save","spend","lend","accept"],0,"You save a copy of a digital file."),
("T5-016",2,"The train was delayed, but we still arrived in _____ for the meeting.",["time","hour","period","season"],0,"'In time for' means early enough not to miss something."),
("T5-017",3,"Her explanation was clear and _____, so everyone understood the main idea quickly.",["concise","crowded","ordinary","patient"],0,"'Concise' means brief but clear, fitting the context."),
("T5-018",2,"The website lets you _____ the results by price, date or rating.",["filter","pour","spread","press"],0,"Digital results can be filtered using criteria."),
("T5-019",2,"The project was more difficult than expected, but the team managed to _____ it through.",["see","look","watch","notice"],0,"'See something through' means continue until it is completed."),
("T5-020",3,"Regular practice can make a noticeable _____ to your confidence when speaking.",["difference","changeover","distance","division"],0,"The fixed phrase is 'make a difference'."),
]
for code,d,q,opts,c,exp in task5:
    sub = "Vocabulary: Phrasal Verbs" if code in {"T5-008","T5-009","T5-014","T5-019"} else "Vocabulary: Collocations"
    add("N14-"+code,"Task 5","Use of English",sub,d,q,opts,c,exp)

# ---------------- TASK 6: grammar cloze ----------------
task6 = [
("T6-001",1,"I _____ this book last week and finished it yesterday.",["bought","have bought","buy","had buy"],0,"A finished past time ('last week') requires Past Simple."),
("T6-002",2,"By the time we arrived, the film _____.",["had started","has started","starts","was start"],0,"Past Perfect describes an action completed before another past action."),
("T6-003",1,"If it _____ tomorrow, we will move the event indoors.",["rains","will rain","rained","would rain"],0,"First Conditional uses Present Simple in the if-clause."),
("T6-004",2,"If I _____ more free time, I would join the course.",["had","have","will have","would have"],0,"Second Conditional uses Past Simple after 'if'."),
("T6-005",3,"If they had checked the address, they _____ the wrong building.",["would not have visited","will not visit","did not visit","would not visit"],0,"Third Conditional uses would have + past participle for the result."),
("T6-006",1,"You _____ wear a helmet on this construction site. It is compulsory.",["must","might","could","would"],0,"'Must' expresses a strong rule or obligation."),
("T6-007",2,"You _____ have called a taxi; the station is only five minutes away.",["needn't","mustn't","couldn't","wouldn't"],0,"'Needn't have' means the action was unnecessary, though it happened."),
("T6-008",1,"She is _____ engineer who works for a renewable-energy company.",["an","a","the","—"],0,"'Engineer' begins with a vowel sound, so the indefinite article is 'an'."),
("T6-009",2,"This is the café _____ we first met.",["where","which","who","whose"],0,"'Where' refers to the place in which something happened."),
("T6-010",2,"The new bridge _____ next year if the project stays on schedule.",["will be completed","will complete","completed","has completing"],0,"Future passive is 'will be + past participle'."),
("T6-011",2,"He said that he _____ the report the following day.",["would finish","will finish","finishes","has finished"],0,"In reported speech, future 'will' commonly shifts to 'would'."),
("T6-012",1,"I enjoy _____ new places on foot when I travel.",["exploring","to explore always","explore","explored"],0,"'Enjoy' is followed by a gerund (-ing form)."),
("T6-013",2,"We decided _____ the earlier train to avoid traffic.",["to take","taking","take","taken"],0,"'Decide' is followed by the infinitive with 'to'."),
("T6-014",3,"Hardly _____ the presentation when the internet connection failed.",["had we started","we had started","did we start","we started"],0,"After 'Hardly' at the beginning, inversion is used: 'Hardly had we started...'"),
("T6-015",2,"There are _____ students in the room today than yesterday.",["fewer","less","few","little"],0,"'Students' is countable, so the comparative is 'fewer'."),
("T6-016",2,"She has lived here _____ 2022.",["since","for","during","from"],0,"'Since' introduces the starting point of an action continuing to the present."),
("T6-017",1,"Neither Tom nor his friends _____ available this evening.",["are","is","be","was"],0,"With 'neither...nor', agreement normally follows the nearer subject, 'friends'."),
("T6-018",3,"I wish I _____ so much time on my phone yesterday.",["hadn't spent","didn't spend","wouldn't spend","haven't spent"],0,"A regret about the past after 'wish' uses Past Perfect."),
("T6-019",2,"The task was _____ difficult that several students asked for extra time.",["so","such","too","enough"],0,"The structure is 'so + adjective + that'."),
("T6-020",2,"Not only _____ the answer, but she also explained why it was correct.",["did she know","she knew","knew she","she did know"],0,"After initial 'Not only', subject–auxiliary inversion is required."),
]
for code,d,q,opts,c,exp in task6:
    if code in {"T6-001","T6-002","T6-016","T6-018"}: sub="Grammar: Tenses"
    elif code in {"T6-003","T6-004","T6-005"}: sub="Grammar: Conditionals"
    elif code in {"T6-006","T6-007"}: sub="Grammar: Modal Verbs"
    elif code in {"T6-010","T6-011"}: sub="Grammar: Passive & Reported Speech"
    elif code in {"T6-012","T6-013"}: sub="Grammar: Gerund & Infinitive"
    else: sub="Grammar: Mixed"
    add("N14-"+code,"Task 6","Use of English",sub,d,q,opts,c,exp)

# Validation
codes = [x["question_code"] for x in items]
assert len(items) == 120, len(items)
assert len(codes) == len(set(codes))
assert all(x["question_text"].strip() for x in items)
assert all(len(x["options"]) == 4 for x in items)
assert all(1 <= x["difficulty"] <= 3 for x in items)
for task in [f"Task {i}" for i in range(1,7)]:
    assert sum(1 for x in items if x["nmt_task_type"] == task) == 20

json_path = OUT / "nmt_2026_pack_v1_4.json"
json_path.write_text(json.dumps(items, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# Build idempotent SQL with safe literals.
def sql_text(s):
    if s is None:
        return "NULL"
    return "'" + str(s).replace("'", "''") + "'"

def sql_json(obj):
    raw=json.dumps(obj, ensure_ascii=False, separators=(",",":"))
    return sql_text(raw) + "::jsonb"

lines=[]
lines.append("-- Neta NMT v1.4: NMT-2026 Content Pack #1 (120 original questions)")
lines.append("-- Safe to run more than once. Content is original and structured around the official 2026 task counts/types.")
lines.append("")
lines.append("ALTER TABLE public.questions ADD COLUMN IF NOT EXISTS question_code text;")
lines.append("ALTER TABLE public.questions ADD COLUMN IF NOT EXISTS nmt_task_type text;")
lines.append("ALTER TABLE public.questions ADD COLUMN IF NOT EXISTS content_pack text;")
lines.append("ALTER TABLE public.questions ADD COLUMN IF NOT EXISTS quality_status text NOT NULL DEFAULT 'approved';")
lines.append("CREATE UNIQUE INDEX IF NOT EXISTS idx_questions_question_code ON public.questions(question_code);")
lines.append("CREATE INDEX IF NOT EXISTS idx_questions_nmt_simulation ON public.questions(nmt_task_type, quality_status) WHERE is_active = true AND is_diagnostic = false;")
lines.append("")
cols=["question_code","topic","difficulty","question_text","options","correct_option","explanation","category","sub_category","section","is_active","is_diagnostic","nmt_task_type","content_pack","quality_status"]
for x in items:
    vals=[
        sql_text(x["question_code"]), sql_text(x["topic"]), str(x["difficulty"]), sql_text(x["question_text"]), sql_json(x["options"]), str(x["correct_option"]), sql_text(x["explanation"]), sql_text(x["category"]), sql_text(x["sub_category"]), sql_text(x["section"]), "true", "false", sql_text(x["nmt_task_type"]), sql_text(x["content_pack"]), sql_text(x["quality_status"])
    ]
    lines.append(f"INSERT INTO public.questions ({', '.join(cols)}) VALUES ({', '.join(vals)})")
    lines.append("ON CONFLICT (question_code) DO UPDATE SET")
    lines.append("  topic=EXCLUDED.topic, difficulty=EXCLUDED.difficulty, question_text=EXCLUDED.question_text, options=EXCLUDED.options,")
    lines.append("  correct_option=EXCLUDED.correct_option, explanation=EXCLUDED.explanation, category=EXCLUDED.category, sub_category=EXCLUDED.sub_category,")
    lines.append("  section=EXCLUDED.section, is_active=EXCLUDED.is_active, is_diagnostic=EXCLUDED.is_diagnostic, nmt_task_type=EXCLUDED.nmt_task_type,")
    lines.append("  content_pack=EXCLUDED.content_pack, quality_status=EXCLUDED.quality_status;")
    lines.append("")
lines.append("-- Verification")
lines.append("SELECT nmt_task_type, count(*) AS questions FROM public.questions WHERE content_pack='v1.4-nmt2026-pack1' GROUP BY nmt_task_type ORDER BY nmt_task_type;")
lines.append("SELECT count(*) AS total_pack_questions FROM public.questions WHERE content_pack='v1.4-nmt2026-pack1';")
(ROOT / "supabase_v1_4_content_pack.sql").write_text("\n".join(lines)+"\n", encoding="utf-8")

print(f"Built {len(items)} questions -> {json_path}")
