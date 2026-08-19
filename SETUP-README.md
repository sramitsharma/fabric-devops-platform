# Setup Guide (5 minutes)

## 1. Arrange the workspace

Your folder layout should be:

```
fabric-platform/            ← workspace root (any name)
├── CLAUDE.md               ← copy the CLAUDE.md file here
├── claude-docs/            ← your existing folder (can be empty)
├── repo-a/                 ← cloned repos as siblings
├── repo-b/
└── ...
```

Key point: **always run `claude` from the workspace root**, not from
inside claude-docs or a repo. CLAUDE.md at the root is auto-loaded every
session and applies to everything beneath it.

## 2. Bootstrap (first session only)

Start Claude Code from the root and paste the entire contents of
`BOOTSTRAP-PROMPT.md`. It will scaffold claude-docs, create the
subagents and skills, interview you (Phase 0), then analyze your repos
(Phase 1). Expect the interview + first repo analyses to take one or
two sessions — that's fine; `/wrap-up` and `project-state.md` make
resumption seamless.

## 3. Daily rhythm afterwards

- Start a session → Claude orients from INDEX.md + project-state.md.
- Drop meeting notes into `claude-docs/meetings/inbox/` anytime, then
  run `/ingest-meeting` — this is what keeps docs from going stale.
- Corrections: say it in chat or run `/update-docs <correction>`; the
  doc-curator propagates it everywhere.
- Learning: run `/teach <topic>` whenever something is unfamiliar.
- End every session with `/wrap-up`.
- Run `/status` weekly to catch stale or orphaned docs.

## 4. Recommended extras

- Put the workspace root under git (even locally) so claude-docs has
  history — you can diff how understanding evolved and recover from bad
  edits. Add repos to .gitignore since they have their own remotes.
- Use `#` prefix in chat for quick memory adds (e.g.
  `# our prod Fabric capacity is F64`), and `/memory` to review what
  Claude has persisted.
- When a conversation gets long, `/compact` after `/wrap-up` rather
  than pushing through a degraded context.
- As the target architecture solidifies, ask Claude to graduate stable
  knowledge from claude-docs into the repos themselves (README/ADRs) so
  your team benefits, keeping claude-docs as the working brain.
