# Bootstrap Prompt — paste this into your FIRST Claude Code session

> Prerequisites: `CLAUDE.md` is at the workspace root; you launched
> `claude` from that root; `claude-docs/` exists (empty is fine).

---

Read CLAUDE.md fully — it is the constitution for this workspace. Then
execute this bootstrap in order. Do not skip steps and do not start
repo analysis until scaffolding and the Phase 0 interview are done.

## Step 1 — Scaffold

Create the full `claude-docs/` structure exactly as specified in
CLAUDE.md §2, with stub files containing valid frontmatter and a
one-line purpose statement each. Create `claude-docs/INDEX.md` listing
every doc with status. Initialize `memory/project-state.md` with
phase = "Phase 0 — Discovery".

## Step 2 — Create the subagents (`.claude/agents/`)

1. **repo-analyst** — read-only explorer. Given a repo path, produce a
   structured analysis: purpose; tech stack; entry points; pipeline/CI
   definitions; infra-as-code; Fabric/Azure resources referenced; data
   flow (sources → transforms → sinks); tenancy handling; secrets and
   identity handling; test coverage; TODO/FIXME debt; quality
   assessment; open questions. Every claim cites file paths. Returns a
   summary ≤ 400 lines for persistence to `claude-docs/repos/<repo>.md`.
2. **doc-curator** — enforces CLAUDE.md §5. Given a change or
   correction, finds every affected doc via INDEX.md, updates in place,
   fixes frontmatter, reports what changed. Never creates duplicate docs.
3. **fabric-architect** — advises against CLAUDE.md §7: always presents 2–4 options with trade-offs, never a single finished design; uses web search
   to verify current Fabric/Azure/GitLab capabilities before proposing;
   outputs ADR-ready recommendations with option comparison.
4. **meeting-scribe** — implements the ingestion protocol in
   CLAUDE.md §9.

## Step 3 — Create the skills (`.claude/skills/`)

- **/status** — read INDEX.md + project-state.md + open-questions.md;
  report phase, recent changes, stale docs (last_updated > 30 days or
  contradicted), orphan docs, and recommended next actions.
- **/analyze-repo <name>** — run repo-analyst on one repo, persist the
  doc, update INDEX.md, current-state.md and project-state.md.
- **/ingest-meeting** — run meeting-scribe on everything in
  meetings/inbox/ (or on pasted text).
- **/update-docs <correction>** — run doc-curator to propagate a
  correction or new fact across all affected docs.
- **/teach <topic>** — explain a concept per CLAUDE.md §8 and append it
  to the right file in learning/.
- **/recall <question>** — answer any "what did we decide / discuss /
  why" question strictly from claude-docs, citing the doc and date, and
  clearly labeling each point as DECIDED, OPEN, or SUGGESTION-ONLY.
- **/wrap-up** — end-of-session: persist state, update frontmatter,
  summarize next steps into project-state.md.

## Step 4 — Phase 0 interview

Interview me ONE question at a time (wait for each answer). Cover at
minimum: (1) what a "tenant" is in this platform and the intended
isolation model; (2) list of repos and what I believe each does;
(3) environments and Azure subscription / Fabric capacity layout;
(4) GitLab group/project structure and CI runner situation;
(5) compliance/security constraints; (6) meeting-notes format and
source; (7) current pain points I already know about; (8) my top three
outcomes for the next 30 days. Persist every answer into glossary.md,
project-state.md, and open-questions.md as appropriate. For each
Azure/Fabric term that comes up, add a Concept callout and log it to
learning/.

## Step 5 — Phase 1 kickoff

List all sibling repos you can see. Confirm the list with me, then
analyze them one repo per /analyze-repo run (not all at once — protect
context). After the final repo, synthesize
`architecture/current-state.md` and a first-pass
`architecture/gaps-and-issues.md`, and present the top 10 gaps ranked
by risk — then STOP and discuss them with me. Do not begin any
target-state or solution design until we have talked through the
findings and I have set priorities (per CLAUDE.md §3).

## Step 6 — Confirm

Finish the bootstrap by running /status and showing me the output.
