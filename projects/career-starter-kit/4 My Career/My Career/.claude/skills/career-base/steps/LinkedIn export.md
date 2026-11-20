# LinkedIn data export

## Purpose

Read a LinkedIn data export folder for facts about the person, and leave out everything about other people and everything private.

## Input

One folder in Inbox that holds `Positions.csv` or `Profile.csv`. Its label is `LinkedIn export` (or the folder name if there are two exports).

If you find a `.zip` instead, do not try to open it. Ask the person to unzip it into Inbox (Mac: double-click it, Windows: right-click > Extract All). In auto mode, list it in the reply and carry on without it.

## Do

1. Read each CSV file listed below that exists. Every file is optional. Real exports leave out empty files.
2. Match columns by their header name, never by their position. LinkedIn changes the column order from time to time.
3. Row 1 is the first data row under the header. The locator is `<File>.csv row N`, for example `Positions.csv row 1`.
4. A field may hold commas and line breaks inside double quotes. Treat the whole quoted field as one value. Two double quotes in a row inside a field are one quote mark.
5. Make facts exactly as `steps/2 Extract.md` describes, one per title, date, sentence of description, skill or qualification.

### Files to read and how

| File | Use it for |
|---|---|
| `Profile.csv` | Headline, Summary, Geo Location. Ignore Address, Birth Date, Zip Code, Twitter Handles, Instant Messengers |
| `Profile Summary.csv` | The summary, only if the Summary in `Profile.csv` is blank |
| `Positions.csv` | One role per row: Company Name, Title, Location, Started On, Finished On. Each sentence of Description is a fact. A blank Finished On means the role is current |
| `Education.csv` | One qualification per row: School Name, Degree Name, Start Date, End Date, Notes, Activities |
| `Skills.csv` | One skill per row. These are `Claimed only` unless an achievement shows the skill |
| `Certifications.csv` | One certification per row: Name, Authority, Started On, Finished On. Licence Number only if it is filled in |
| `Volunteering.csv` | One role per row, with `relationship: volunteer` on the employer |
| `Recommendations_Received.csv` | Only rows with Status `VISIBLE`. Use Company and Job Title for who wrote it. Never use First Name or Last Name |
| `Endorsement_Received_Info.csv` | A count per skill only. Never the endorsers' names |
| `Projects.csv`, `Honors.csv`, `Languages.csv`, `Courses.csv`, `Publications.csv` | One fact per row, if present |

### Files never to read

`Connections.csv`, `messages.csv`, any file starting `Inferences`, any file starting `Ad_Targeting`, `Registration.csv`, `Email Addresses.csv`, `PhoneNumbers.csv`, `Whatsapp Phone Numbers.csv`, the `Jobs` folder, `Company Follows.csv`, `Rich_Media.csv`, and any other file not in the table above.

List the files you skipped. The Source note says they were skipped "to keep other people's details and your private data out".

### Dates

- Positions and volunteering use `Mon YYYY`, for example `Mar 2021`. Write them as `2021-03` in frontmatter.
- Education uses the year only.
- If the LinkedIn PDF and the export disagree only on precision (a year in one, a month and year in the other), cite both and use the less precise form. It is not a gap.

### LinkedIn PDF and export together

If both a LinkedIn PDF and an export exist, they are one source family for "found in one source only" purposes. A fact that is in both LinkedIn files but not in the CV is still found in one source only when compared with the CV.

## Output

The same fact list as `steps/2 Extract.md`, plus:
- `files_read`: the CSV files read, with their row counts
- `files_skipped`: the files left out

## Done when

Every row of every file in the read list has been turned into facts, and every skipped file is listed.
