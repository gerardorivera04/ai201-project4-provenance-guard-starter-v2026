"""
What your test runs. ← UNIT 8, MILESTONE 3

Each of your five criteria needs something run against it. A criterion about
false positives needs your own writing. One about label coverage needs inputs
across the score range. One about the appeal path needs a real content_id.

Working that out is Milestone 3's first step, and this file is where you write
it down. `run_eval.py` runs everything here three times.

Two are filled in as examples. Replace them with what your criteria actually
need — these are a shape, not a set.

A scenario carries **either** of these:

    "texts"   a list of strings. Each is sent as {"text": ..., "creator_id": ...}
              with a creator_id made up for you. Use this for most criteria.

    "bodies"  a list of whole request bodies, sent exactly as written. Use this
              when the malformed request IS the point — empty text, no `text`
              field at all, something enormous. A bad-input criterion needs it,
              because you cannot express "the field is missing" as a string.
"""

SCENARIOS = [
    {
        "name": "false positives - my own writing",
        "criterion": 1,
        "texts": [
            "Love can be both a blessing and a curse as viewed in William Shakespeare’s Othello. Our protagonist, Othello, is a Moorish, skilled general in the Venetian army who marries the Venetian senator’s daughter, Desdemona, behind the Venetian senator’s back because they share and develop a special bond of romantic love as they reach a point in their relationship to fully trust one another for any predicaments they face in their lives.",
            "Secondly, love can be interpreted as a destructive force as time progresses in Othello when holes start to appear in Othello and Desdemona’s special bond and the love becomes overwhelming as Othello’s close connections with people like Iago, Cassio, and even Desdemona are the causes for such destructive effects, such as pain and betrayal, to occur at the heart of Venice’s community, which is Othello and Desdemona’s loving relationship.",
            "I'm interested in working for CrowdStrike with the company's sharp eye in looking at an individual's skillset and how they can make a difference in global security. Thus, I fit in that category ever since I told my family to build this everyday habit of avoiding spam calls and messages to ensure their data doesn't get compromised.",
            "Therefore, I'm interested in working for CrowdStrike because CrowdStrike is the definitive cybersecurity company where people, myself included, can take our passion and skillset in cybersecurity onto a global level, which includes working on incident response investigations, performing network-based forensics, and supporting the production of high-quality written and verbal reports.",
            "The purpose of this software design document is to introduce a new employee management system for company ‘Z’. The new employment management system will contain features and functionalities to ensure that all employees' data can be managed and maintained under the admin role. The new employee management system will have a GUI (Graphical User Interface) to allow manipulation of employee data by the admin and allow employees to view their own information. All employees can view their data and see the changes made by the admin when necessary. Next, an admin is given control in the form of CRUD functionality over what each employee has done to remain important to the company.",
            "CRUD - Create, read, update, and delete are the four basic functions of persistent storage, which is a major part of nearly all computer software. ",
            "I don’t want to share much information, but I have a question. For context, I pre-ordered a Zelda 40th Anniversary Nintendo Switch 2 controller at Best Buy, which states on my Best Buy account that the controller will be shipped at my house next week. The pre-order was successful as the order clearly states that the item will shipped on October 29th, but here’s where I’m confused. Would my card need to be charged again whenever it comes time for the item to get shipped? as For instance, I placed the order on Sept. 8th, 2026 where I did get charged for the controller as my payment of $106.99 had gone through so that I had a successful pre-order, but I can’t find the same payment on my Truist account as I do remember getting some money back into my checking account, which was about $100.",
            "I want to create my own version of an AI Resume Tailor with scoring functionality where I can insert my resume, receive recommendations for any changes/improvements to achieve a perfect score of 100, and the goal is to achieve a perfect score for any job role you're interested in the computer science field, which ranges from 'Software Engineer' to 'Data Scientist'.",
            "What questions should I ask at a NVIDIA event here at Georgia State as a recent graduate student (graduated May 2026) who specializes in Python, SQL, and React and uses AI-assisted development tools? In addition, what are some new grad roles that are available at this time, including Software and AI Engineer roles?",
            "Which of the following services should he select on Home Depot's Pro Referral website based on my father's company's job description? For context, there are some services he can't offer for two reasons: (1) Some jobs can't be carried out due to needing more than one person as he's looking for jobs intended for 1-2 employees, and (2) he specializes in using certain materials rather than all of them, so he's looking for jobs where he can use brick, stone, and/or stucco. In addition, here's a screenshot of all the services as a Concrete/Masonry Pro on the Home Depot Pro Referral website, and the following job description: Building Improvements and Repairs using Brick, Stone, and Stucco.",
        ],
    },
    {
        "name": "score spread - human versus AI comparison",
        "criterion": 2,
        "texts": [
            "Can you make a draft of a business card for the company? For context, the picture of the business card's front side and the back side will contain three pictures of the work he's done in the past.",
            "There's a section called Additional Details and is asking for the legal name of the Single-member Limited Liability Company, but there is a problem where I can't use the comma as the legal name is North Georgia Repair Specialty, LLC.",
            "What are the steps in applying and registering as an LLC in Georgia? For context, my father wants to start an LLC where he holds both of the following positions, Single-Owner and Single-Member, so that he's the only one working for his business and he's not hiring others to do cement/concrete house repairs for stairs, floors, etc.",
            "Out of curiosity, does my father qualify for Social Security Disability Insurance (SSDI)? For instance, my father has lost hearing in his left ear and he has affected his standard of living significantly because he can't work in very loud environments, such as cement work in neighborhoods, as being surrounded by these environments every day would cause him to suffer from headaches and lack of sleep at night. In addition, he has enough work history as well to meet the Work Qualification, which is working at least 5 out of the 10 years before the disability had begun.",
            "Video game development is an excellent profession for bringing passion and creativity to your creation. Being a video game developer has its benefits to balancing workload and fun, such as gaining profits, creating software, and running software tests. However, a video game developer is going to require time and dedication to reach a master level of their craft as one must practice to gain experience on what makes video games great. Thus, digital literacy is a necessity on the path to being a great video game developer because digital literacy helps to understand quality over quantity, avoid any experience-changing issues, and create the best version of your video game.",
            "The importance of effective time management cannot be overstated in today's fast-paced work environment. Professionals who develop strong organizational habits are better positioned to meet deadlines and reduce stress. There are several key strategies that can help individuals improve their productivity. First, prioritization is essential. By identifying the most important tasks and addressing them first, workers can ensure that critical objectives are met. Second, minimizing distractions plays a significant role. Setting aside dedicated blocks of time for concentrated work is widely considered beneficial. Finally, regular breaks are important for maintaining performance.",
            "Absolutely. Given your current background—CS coursework, Python/C/Java/SQL/JavaScript, algorithms, networking, Linux, and your Vue/Node/MySQL Employee Management System—I would not fill your resume with more basic CRUD applications. For Microsoft, I’d build 2–3 technically deep projects that demonstrate software engineering, cloud, AI, distributed systems, and security. Microsoft’s current student ecosystem heavily emphasizes AI, Azure, GitHub, cloud development, and hands-on MVPs.",
            "Ethernet can give you lower/more consistent latency, fewer connection drops, and less wireless interference. It won't necessarily increase your Internet plan's maximum download speed, but it can make the connection more consistent. And importantly, you don't need an Ethernet adapter for Switch 2 because its dock already includes the LAN port.If you tell me the exact ASUS gaming router model you have (e.g., RT-AX82U, RT-AX86U, ROG Rapture GT-AX6000, etc.), I can show you exactly which port to plug the Switch 2 into and the ASUS settings I'd recommend for the best Switch 2 gaming/NAT performance.",
            "I contributed to software quality assurance in a fast-paced, agile environment by executing comprehensive exploratory testing across multiple platforms. I identified and documented around 50 high-quality bugs with detailed reproduction steps and system logs, which increased application stability by 15% before production releases. I accelerated the debugging cycle by 25% through precise, developer-ready bug reports that streamlined root cause analysis. I collaborated with globally distributed development teams to validate bug fixes before deployment, reducing production hotfixes by 15%. Finally, I maintained 99 perecent core system uptime by performing in-depth regression testing to ensure new deployments did not impact existing functionality.",
            "StreetSense is an AI-assisted civic reporting app that lets residents photograph potholes, capture GPS location, and submit reports to city officials for review and repair. We built a cross-platform mobile app with React Native and Expo, a REST API with Python, FastAPI, SQLModel, and PostgreSQL, and integrated the Google Gemini API to automatically score pothole severity, estimate dimensions, and estimate vehicle damage costs from uploaded images.",
        ],
    },
    {
        "name": "label coverage - 15 varied submissions",
        "criterion": 3,
        "texts": [
            # Clearly-human examples.
            "I missed the bus this morning, so I walked the last few blocks to campus. It was annoying at first, but the extra time outside actually helped me clear my head before class.",
            "My first attempt at the database query failed because I used the wrong column name. I stared at it for ten minutes before noticing the typo, then the rest of the task worked normally.",
            "I usually plan my week on Sunday night, but I do not follow the plan perfectly. The list still helps because I can see what must be finished and what can wait.",
            "The meeting started late because two people were still commuting. We used the time to compare notes, and by the time everyone arrived we already had a shorter list of decisions to make.",
            "I prefer testing small changes as I go instead of waiting until the end. It makes mistakes less stressful because I can usually remember what I changed right before something stopped working.",
            # Borderline or mixed-style examples.
            "A reliable application should be easy to understand, simple to maintain, and prepared for unexpected input. These qualities support users and also reduce the amount of time developers spend diagnosing avoidable problems.",
            "When I worked on the project, I learned that communication was almost as important as writing code. A quick message about an unclear requirement prevented several hours of work in the wrong direction.",
            "Good time management is not only about creating a schedule. It also requires reviewing priorities, adjusting when circumstances change, and leaving enough flexibility for tasks that take longer than expected.",
            "The dashboard gives users a clear view of reported issues and their current status. Although the main workflow is straightforward, the design still needs careful error handling so that an incomplete request does not create confusing results.",
            "Learning a new framework can feel slow during the first few days because every small feature requires looking something up. After the basic patterns become familiar, the same documentation becomes a useful reference instead of a constant interruption.",
            # Clearly-AI examples.
            "In today's rapidly evolving technological landscape, effective project management is essential for achieving sustainable organizational success. By establishing clear objectives, fostering collaboration, and continuously evaluating performance, teams can maximize productivity and deliver high-quality outcomes.",
            "Artificial intelligence is transforming modern industries by improving efficiency, enhancing decision-making, and creating innovative opportunities. As organizations adopt these technologies, responsible implementation and continuous learning will remain essential for long-term growth.",
            "A successful cybersecurity strategy requires a comprehensive and proactive approach. Organizations should implement strong access controls, conduct regular security assessments, educate employees about potential threats, and maintain an effective incident response plan to protect valuable information.",
            "Cloud computing provides businesses with scalable, flexible, and cost-effective resources. By leveraging cloud-based infrastructure, organizations can streamline operations, support remote collaboration, improve data availability, and respond more efficiently to changing market demands.",
            "The development of a high-quality software application involves several important stages, including planning, design, implementation, testing, deployment, and maintenance. Each stage contributes to the overall reliability, usability, and performance of the final product.",
        ],
    },
    {
        "name": "appeal path submissions",
        "criterion": 4,
        "texts": [
            "I wrote this short project reflection after completing my software testing assignment.",
            "The application stores each report and allows users to review the current status.",
            "I tested the login flow, documented the failures, and shared the reproduction steps with my team.",
            "This paragraph describes how I improved the interface after receiving feedback from another developer.",
            "I reviewed the final submission carefully and corrected the configuration errors before deployment.",
        ],
    },
    {
        "name": "bad input handling",
        "criterion": 5,
        "bodies": [
            {"creator_id": "eval_missing_text"},
            {"text": "", "creator_id": "eval_empty_text"},
            {"text": "   ", "creator_id": "eval_whitespace_text"},
            {"text": "x" * 10001, "creator_id": "eval_oversized_text"},
        ],
    },
]


def validate() -> list[str]:
    """
    Complain about anything malformed, before a long run rather than during.

    A "bodies" scenario is deliberately exempt from the empty check — an empty
    string is the whole point of a bad-input case, and refusing to run one
    would make that criterion untestable.
    """
    problems = []
    for i, scenario in enumerate(SCENARIOS, 1):
        if not scenario.get("name"):
            problems.append(f"scenario {i} has no name")

        texts = scenario.get("texts")
        bodies = scenario.get("bodies")

        if texts and bodies:
            problems.append(
                f"scenario {i} ('{scenario.get('name')}') has both texts and "
                f"bodies — pick one"
            )
            continue

        if bodies:
            for j, body in enumerate(bodies, 1):
                if not isinstance(body, dict):
                    problems.append(
                        f"scenario {i}, body {j} is not a dict — bodies are whole "
                        f"request bodies, like {{'text': '', 'creator_id': 'x'}}"
                    )
            continue

        if not texts:
            problems.append(f"scenario {i} has no texts and no bodies")
            continue

        for j, text in enumerate(texts, 1):
            if not str(text).strip():
                problems.append(
                    f"scenario {i}, text {j} is empty — if an empty submission is what "
                    f"you're testing, use 'bodies' instead of 'texts'"
                )
            elif str(text).startswith("REPLACE ME"):
                problems.append(
                    f"scenario {i} ('{scenario.get('name')}'), text {j} is still "
                    f"the placeholder"
                )
    return problems
