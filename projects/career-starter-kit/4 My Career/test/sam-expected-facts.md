# Sam Whitlock: expected facts and traps

For testers. Not in the zip. Sam Whitlock is a made-up person. Every fact below comes from the three files that ship in `My Career/Inbox`:

- CV: `Sam Whitlock CV.pdf` (1 page). Label `CV`.
- LinkedIn PDF: `Sam Whitlock LinkedIn profile.pdf` (1 page). Label `LinkedIn PDF`.
- LinkedIn export: `Sam Whitlock LinkedIn data export/` (7 CSV files). Label `LinkedIn export`. Built only from the LinkedIn PDF, so it should agree with it everywhere.
- The job ad `Sam Whitlock job ad - GM Customer and Operations.pdf` (Kestrel Bay Energy, also made up) is never a source of facts about Sam.

The LinkedIn PDF and the export count as one source family. A fact in LinkedIn but not in the CV is still "found in one source only".

## 1. Identity and contact

| Fact | CV p1 | LinkedIn PDF p1 and export |
|---|---|---|
| Name | Sam Whitlock | Sam Whitlock (Profile.csv row 1) |
| Location | Melbourne VIC | Greater Melbourne Area (Profile.csv row 1) |
| Email | sam.whitlock@example.com | not shown |
| Phone | 0400 000 000 | not shown |
| Headline | not shown | Head of Customer Operations at Fernmoor Water |
| Years of experience | "fourteen years" | "Fourteen years" |
| Summary | Operations leader, water utility, freight, insurance. Runs large frontline teams and fixes the processes underneath | "I like the unglamorous end of operations: the queue, the roster, the root cause." |
| Current study | Executive MBA at Ridgeway Business School | Executive MBA student at Ridgeway Business School |

Role dates start Feb 2011, which is about 15 years by Nov 2026. That clashes with "fourteen years" in both sources (trap 1).

## 2. Roles (5 in total, 4 jobs and 1 volunteer)

### Fernmoor Water - Head of Customer Operations
- Dates: Mar 2021 to present (CV p1). March 2021 to Present (LinkedIn PDF p1). Mar 2021, blank finish (Positions.csv row 1).
- Location: Melbourne (both).
- Scope: customer operations for 410,000 households (both). Contact centre, billing, collections and field scheduling (CV only).
- Team 140 staff, budget $18M operating, reports to the Chief Customer Officer (CV only).
- Achievements:
  - Cut written complaints by 31% in two years by fixing the top five causes at the source (CV). "fix it upstream" program with the billing and network teams that took written complaints down by almost a third (LinkedIn). Same achievement, two wordings (trap 3).
  - Led the customer side of the billing system replacement. Went live on time in October 2023 with no missed billing cycle (CV only).
  - Moved the contact centre to a hybrid model in 2022. Staff turnover fell from 34% to 19% (CV only). The recommendation supports it.
  - Represent the business in hardship and vulnerability reporting to the state water regulator (CV only). May be a scope line or an achievement.
  - Set up the company's first customer vulnerability team in 2022: six specialists who handle family violence, hardship and medical cases end to end (LinkedIn only). No result stated (trap 7).

### Calder Freight - Operations Manager
- Title: "Operations Manager, Victoria" (CV p1) vs "Operations Manager" (LinkedIn PDF p1, Positions.csv row 2). Trap 2.
- Dates: Jul 2016 to Feb 2021 (all three agree).
- Location: Melbourne. Three depots (both). Depot names Laverton, Dandenong, Somerton and 210 staff and contractors (CV only).
- Achievements:
  - Lifted on-time delivery from 88% to 95% by redesigning dock scheduling and route cut-off times (CV). Rebuilt dock scheduling with the planning team (LinkedIn). The "with the planning team" wording must survive (trap 5).
  - Halved the lost-time injury frequency rate over three years (CV only). What Sam did is not stated (trap 6).
  - Kept all three depots running through the 2020 lockdowns (CV). With split shifts and no site closures (LinkedIn).

### Bellmere Insurance - Claims Team Leader
- Dates: Feb 2013 to Jun 2016 (all three agree).
- Location: Melbourne (CV only). LinkedIn gives no location.
- Led a team of 12 handling motor and home claims (CV only).

### Bellmere Insurance - Graduate Analyst
- Feb 2011 to Jan 2013 (LinkedIn PDF p1, Positions.csv row 4). The CV only says "Joined as a graduate analyst in 2011". The whole role is one-source as a role.

### Bellbird Junior Football Club - Board member (treasurer)
- Volunteer (`relationship: volunteer`). LinkedIn only.
- Dates: "2019 to Present" (LinkedIn PDF p1). "Jan 2019", blank finish (Volunteering.csv row 1).
- Look after a $240,000 annual budget and the club's grant applications.
- The month "Jan" is an artefact of the export format. LinkedIn exports always carry a month. This is NOT a gap. The build should cite both and use the year-only form ("2019").

## 3. Employers (4)
Fernmoor Water, Calder Freight, Bellmere Insurance (employee) and Bellbird Junior Football Club (volunteer). No source states an industry in a form that needs a note line beyond "water utility", "freight" and "insurance" from the CV and LinkedIn summaries.

## 4. Education (2)
- Executive MBA, Ridgeway Business School, 2025 to 2027, in progress (CV, LinkedIn, Education.csv row 1).
- Bachelor of Commerce, Eastgate University. CV says "2010". LinkedIn says "2007 to 2010" (Education.csv row 2). Precision only, not a gap.

## 5. Certifications
None. A build may write "gap: none stated" on Profile. It must not invent one.

## 6. Skills
- CV skills list: Contact centre and frontline operations, Process improvement, Large-scale change, Budget ownership, Regulatory reporting, Safety leadership.
- LinkedIn top skills (and Skills.csv): Operations management, Customer experience, Change management.
- Expect at least 9 skill notes. "Large-scale change" and "Change management" may stay as two notes or be linked, never silently merged into a new name.

## 7. Recommendation (1)
- From: Former Chief Customer Officer, Fernmoor Water (LinkedIn PDF p1, Recommendations_Received.csv row 1).
- Text: took over a contact centre losing a third of its people every year, the hybrid roster is still the model the business copies.
- The export carries the recommender's made-up name in First Name and Last Name. That name must never appear in any note (trap 8). The phrase "a third of its people" is a quote about staff turnover, not about complaints, so it is allowed.

## 8. Traps (each is a check)

1. **Years.** A note shows "Fourteen years" or "fourteen years" (CV p1, LinkedIn PDF p1) AND the role dates from Feb 2011, and a Gap note of kind `disagree` covers it. No note states "15 years" or "15+ years" as a fact. "from Feb 2011, about 15 years by Nov 2026" is the allowed computed form.
2. **Calder title.** Both "Operations Manager, Victoria" (CV) and "Operations Manager" (LinkedIn) appear. The role note has `title_disagrees: yes`. One Gap note covers it.
3. **Complaints.** "31%" cited to the CV and "almost a third" cited to LinkedIn both appear. Nothing about complaints says "a third" alone, "about a third", "nearly a third" or "over 30%".
4. **One-source facts.** Each of these exists as a note or a line, and each is in a `one-source` Gap note or in the Index "Found in one source only" list: Graduate Analyst role, vulnerability team, treasurer role (LinkedIn only), billing system replacement, LTIFR, team sizes (140, 210, 12), $18M budget (CV only).
5. **"with the planning team".** The dock scheduling achievement has `my_part: team` and keeps the phrase "with the planning team".
6. **LTIFR.** The lost-time injury achievement has "gap:" for what Sam did.
7. **Vulnerability team.** The vulnerability team achievement has "gap:" for the result.
8. **Other people's names.** The recommender's name from Recommendations_Received.csv appears in no note.
9. **The job ad.** Kestrel Bay Energy and the job ad file are never cited as a source in any note outside Targets. The ad may be named in Index.md and Build log.md only as "not used for facts".

Not a trap, and not a gap: the "Jan 2019" month in Volunteering.csv (see section 2), and "2010" vs "2007 to 2010" for the Bachelor of Commerce.

## 9. Minimum counts after a build on Sam
Roles 5, employers 4, achievements 10, skills 9, education 2, recommendations 1, gaps 6, sources 3 (plus Told me only if a question was answered), themes 1 to 5, stories 3.

## 10. Tailoring checks (Kestrel Bay Energy ad)
- Fit.md shows Gap for working knowledge of the energy regulatory framework (AER and ESC obligations).
- Budget: Sam's $18M is under the ad's $20M. Should be Partial or Gap, never Strong.
- Team: 140 at Fernmoor (210 at Calder) vs 150 or more asked. Must not be inflated.
- The CV uses the modest Calder title "Operations Manager" and lists the title in "Check before you send", unless Sam answered the question.
- CV.html prints on two A4 pages or fewer.
