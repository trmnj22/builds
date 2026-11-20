# Start here

This folder turns your CV into a knowledge graph of your career, linked notes with every fact traced to its file, then uses it to tailor CVs, find jobs and draft LinkedIn posts. Everything stays on your computer.

You need the Claude desktop app (Mac or Windows) on a paid plan, Pro or above. No paid plan? Pair with someone who has one and watch theirs run.

## Your first run, in 6 steps

**First, the usual way.** In the Claude app's Chat tab, start a new chat, attach your CV and the job ad, and type `Tailor my CV to this job`. Leave it writing while you set up.

**1. Get the folder.** Download this repo (Code > Download ZIP) or the My-Career.zip you were given, and unzip it. Mac: double-click the zip. Windows: right-click it, Extract All, then Extract. Move the My Career folder somewhere easy, such as Documents. Use the inner My Career folder, the one with this file in it. Never work from inside the zip.

**2. Swap in your files.** Go into the My Career folder you just unzipped and open the Inbox folder inside it. This is a folder, not your email inbox. Delete everything whose name starts with "Sam Whitlock" (three files and one folder). Put in your CV (PDF is best) and a job ad you want (save it as a PDF). Your LinkedIn profile PDF is optional. Keep the LinkedIn data export for later, because it makes the first build longer. Want to see Sam's example first? Leave Sam's files there.

**3. Open the folder in Claude.** Claude app > Code tab > choose the My Career folder. Check it says Local, not Cloud. If it asks whether you trust the folder, choose Yes. Set the permission mode to Auto (or Accept edits).

**4. Type `Build my career base`.** A quick build takes about 5 to 7 minutes. While it runs, go back to the Chat tab and finish the plain-chat CV. When the build is done, `/grill-me` starts asking what your files leave out, one question at a time. Click an answer to each, or type your own. There is no limit: answer as many as you like, and click "That's enough for now" when you want to move on. Your answers go into your notes and your Job Scout settings. Type `Grill me` later for more questions. To see what it built, open Index.md.

**5. Type `Tailor my CV to the ad in Inbox`.** Open Targets, then the folder named after the job. Read Fit.md first. Then compare CV.md with the CV the plain chat wrote you. Find one line in the chat version you couldn't defend. No job ad? Type `Tailor my CV to this role:` and two lines about it. Not job hunting? Type `Write a LinkedIn post` instead. Claude asks a few quick questions, then drafts a post from your notes in LinkedIn/Drafts. You copy it into LinkedIn yourself.

**6. Type `Set up my Job Scout to run every day at 7am`.** Then open Scheduled in the left sidebar > Job Scout and check three things: the folder is My Career, the permission mode allows edits, and it runs only on this computer. Click Run now once and approve anything it asks. You don't need to wait for it, it takes about 3 minutes and writes a shortlist in Job Scout/Shortlists. It runs while your laptop is awake and Claude is open.

## After your first run

- **Full build.** Type `/effort ultracode` once (Pro: first turn on Dynamic workflows in `/config`), then `Build my full career base`. It takes about 20 minutes and checks every fact with separate checkers. Approve the workflow card with Always. Without ultracode it still runs, just slower.
- **Add more.** Put your LinkedIn data export, reviews or award write-ups in Inbox, then type `Add this to my career base`. Type `Grill me` any time to fill more gaps.
- **LinkedIn.** Type `Write a LinkedIn post`. Claude scans the last week's news on your topics, offers three scored ideas (one from the news, one from your own career, one counter-view), asks up to three questions and drafts one in LinkedIn/Drafts. Every claim is checked against your notes. You copy it into LinkedIn yourself, or say `Fill it` if Claude in Chrome is connected and you are signed in to LinkedIn in Chrome. Claude fills the composer and stops. The Post button is yours.
  - After you post, type `I posted it` and paste the link. A week later, type `Log my LinkedIn numbers`.
  - Type `Set up my LinkedIn scan every Monday at 8am` for three fresh ideas each week. Check the task the same way as the Job Scout in step 6. It never drafts or posts.
  - How the scoring and the post shape work is in LinkedIn/About LinkedIn.md.
- **Big decisions.** Type `Ask my board of advisers`, for example "Should I take this job?". Four advisers test it and write a one-page memo.
- **Cowork instead of the Code tab.** Claude app > Cowork > Projects > New project > Use an existing folder > My Career. Paste this into the project's Instructions box, then type the same sentences:

> Before anything else, read CLAUDE.md in this folder and follow it. When I type a command or one of the sentences in its table, open the file it names and follow it step by step.

- **Your LinkedIn data.** On a computer, open your profile > More (or Resources) > Save to PDF. Or Me > Settings and Privacy > Data privacy > Get a copy of your data. Unzip the export into Inbox (Windows: right-click > Extract All).

All commands are in README.md. The rules Claude follows are in CLAUDE.md.

## If something goes wrong
- **It says Roles is empty:** do step 4 first.
- **It can't read a file:** save it as a PDF and put it in Inbox again.
- **It asks permission at every step:** set the permission mode to Accept edits.
- **On a Mac you can't see .claude:** press Cmd+Shift+full stop in Finder. You don't need to open it.
