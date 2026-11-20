# Board of advisers for Claude Code

This version runs the four advisers as separate agents, working at the same time without seeing each other's views.

1. Copy the `.claude` folder into the folder where you keep your decision documents. (It's a hidden folder. On a Mac press Cmd+Shift+. in Finder to see it.)
2. Open Claude Code in that folder.
3. Type `/board-of-advisers` followed by your decision and the folder with your documents.

Each adviser uses the standard version of its method (pre-mortem, devil's advocate, outside view, consider the opposite). Nothing else needs to be installed.

To change how an adviser behaves, edit its file in `.claude/agents/`. It's plain English.
