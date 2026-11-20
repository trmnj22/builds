# Adding a project

1. Copy, never move. Build the public version in `projects/<name>/` from a copy of the original.
2. Swap every real example for fictional data: a made-up person, made-up companies. No clients, no employer material, no course or exam content, no personal finance, health, family or immigration content.
3. No secrets in files. Keys come from environment variables, with a `.env.example` holding blank values.
4. No absolute paths (`/Users/...`) and no vault references.
5. Write a README: what it does, why, how it works, quick start, an example, design decisions.
6. Run `scripts/check.sh`. Any hit blocks the commit. Fix the file, never the check.
7. Add a row to the table in the top README.
