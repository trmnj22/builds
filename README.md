# Builds

Things I have designed and built myself, mostly AI agents and the tooling around them.

I have spent fifteen years delivering Microsoft Dynamics 365 and retail programmes, the last few leading AI work into production. Most of that code belongs to clients and stays private. This repo is the part I can show: tools I built for my own work and study, rebuilt with fictional sample data so anyone can run them.

Each project is designed and directed by me and built with Claude Code as my pair programmer. That is how I work now, and the design choices, the guardrails and the tests are mine.

## Projects

| Project | What it does | Stack |
|---|---|---|
| [cv-builder](projects/cv-builder) | Turns a Markdown CV into a designed, ATS-safe two-page PDF and a Word copy, and refuses to shrink the type to make it fit | Python, headless Chrome, python-docx |
| [tech-picker](projects/tech-picker) | Ranks an evidence bank of past technical work against a job ad, with a coverage table that marks every gap "do not claim" | Python |
| [whiteboard-visuals](projects/whiteboard-visuals) | Renders hand-drawn style post images from a small JSON spec, with a checker that enforces the design system | Python, SVG |
| [assignment-grader](projects/assignment-grader) | A Claude Code skill: two blind grader agents, one strict and one lenient, then a combined dashboard | Claude Code skill, multi-agent |
| [career-starter-kit](projects/career-starter-kit) | A Claude Code project that turns your career history into a linked evidence graph, then tailors CVs from it | Claude Code skills and agents |

More are on the way: a multi-agent operations floor on the Claude API, and a script-to-video pipeline.

## How this repo stays safe

No passwords, keys, tokens, client names or client data, ever. Every commit and push runs `scripts/check.sh` (gitleaks across the full history, plus a private deny list kept outside the repo), and GitHub runs its own secret scan on every push.

## Licence

MIT. See [LICENSE](LICENSE).
