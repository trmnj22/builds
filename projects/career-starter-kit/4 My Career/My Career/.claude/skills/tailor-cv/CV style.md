# CV style

How `CV.md` and `CV.html` are laid out. A4, one column, system fonts, 10pt body, 16mm margins, two pages at most (900 words of visible text or fewer).

## Order
1. Name
2. Contact line: email | phone | location
3. Profile (three short lines, written the same way as the bullets: no I, my, he or she, and never a mix of first and third person)
4. Experience, newest first. For each role: title, employer, then a line with dates and location, then 3 to 5 bullets (fewer for older roles)
5. Volunteering (only if a Roles note has `relationship: volunteer` on its employer, and it helps this ad)
6. Education
7. Skills (one line, only skills with notes, Strong and Some first)

## Wording
- When sources word the same thing differently (for example a percentage in one and words in another), use one source's wording for the line, the more modest one. Never blend the two into one claim.
- Keep "with the planning team" and similar words exactly.

## CV.md shape
```
# {{Name}} (from [[Profile]])
{{email}} | {{phone}} | {{location}} (from [[Profile]])

## Profile
{{line}} (from [[note]])

## Experience
### {{Title}}, {{Employer}} (from [[{{Employer - Title}}]])
{{Mon YYYY}} to {{Mon YYYY or present}}, {{location}} (from [[{{Employer - Title}}]])
- {{bullet}} (from [[{{achievement}}]])

## Volunteering
## Education
- {{Qualification}}, {{Institution}}, {{year or "in progress"}} (from [[{{Qualification - Institution}}]])

## Skills
{{skill}}, {{skill}}, {{skill}} (from [[{{skill}}]], [[{{skill}}]])

## Check before you send
- {{choice made and why}} [[Gap - {{...}}]]
```

## CV.html
Copy this skeleton. Fill the body from the checked CV.md, without the `(from [[...]])` notes and without Check before you send. Write dates in full words ("March 2021 to present"). Write "and" rather than an ampersand.

The CSS below puts one property in each rule so this file stays free of semicolons. Copy it as it is, or merge rules for the same selector into one block with semicolons between properties. Both work the same.

```html
<!DOCTYPE html>
<html lang="en-AU">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{{Name}} CV</title>
<style>
@page { size: A4 }
@page { margin: 16mm }
* { box-sizing: border-box }
body { font-family: -apple-system, "Segoe UI", Helvetica, Arial, sans-serif }
body { font-size: 10pt }
body { line-height: 1.4 }
body { color: #1a1a1a }
body { background: #fff }
body { max-width: 178mm }
body { margin: 0 auto }
body { padding: 12mm 16px }
h1 { font-size: 20pt }
h1 { margin: 0 0 2pt }
.contact { color: #444 }
.contact { margin: 0 0 10pt }
h2 { font-size: 10pt }
h2 { text-transform: uppercase }
h2 { letter-spacing: 1pt }
h2 { color: #1f4e5f }
h2 { border-bottom: 1px solid #b9c7cc }
h2 { padding-bottom: 2pt }
h2 { margin: 12pt 0 5pt }
h2 { break-after: avoid }
h3 { font-size: 10.5pt }
h3 { margin: 8pt 0 0 }
.meta { color: #555 }
.meta { margin: 0 0 2pt }
p { margin: 0 0 4pt }
ul { margin: 2pt 0 0 }
ul { padding-left: 14pt }
li { margin-bottom: 2pt }
.role { break-inside: avoid }
@media print { body { padding: 0 } }
@media print { body { max-width: none } }
</style>
</head>
<body>
<h1>{{Name}}</h1>
<p class="contact">{{email}} | {{phone}} | {{location}}</p>

<h2>Profile</h2>
<p>{{profile line}}</p>

<h2>Experience</h2>
<div class="role">
<h3>{{Title}}, {{Employer}}</h3>
<p class="meta">{{Month YYYY}} to {{Month YYYY or present}} | {{location}}</p>
<ul>
<li>{{bullet}}</li>
</ul>
</div>

<h2>Education</h2>
<p>{{Qualification}}, {{Institution}}, {{year}}</p>

<h2>Skills</h2>
<p>{{skill}}, {{skill}}, {{skill}}</p>
</body>
</html>
```

## Checks before saving CV.html
- Visible text is 900 words or fewer.
- No line says more than the CV.md line it came from.
- No photo, date of birth, age or marital status.
