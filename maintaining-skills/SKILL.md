---
name: maintaining-skills
description: Use when an EXISTING skill or reference corpus has decayed and needs maintenance - it has grown large, contradicts itself, gives different values for the same fact in different files, carries stale or UNVERIFIED markers, has drifted from what a live project actually measured, or needs re-checking after a model upgrade. Also use to fold what a project learned back into its skill ("audit the skill against this project", "the skill is behind the project", "merge the intake file", "should we prune this section"). Triggers on contradiction, rot, drift, bloat, duplication, stale docs. If the job is CREATING a new skill, or making agents comply with a rule they rationalise around, that is writing-skills, not this one.
---

# Maintaining skills

**Triage.** Creating a skill, or making agents comply with a rule they
rationalise around: `writing-skills`. This skill repairs an existing skill that
has rotted, contradicts itself, or fell behind its projects. An
audit-driven edit meets `writing-skills`' Iron Law when the audit (the project's
real mistakes, checked against the skill as it stands) runs first.

**Every run starts the same way.** Run `python -I <this
skill>/scripts/intake_list.py` and show its output in chat: one line per entry
across every skill plus GLOBAL (`~/.claude/INTAKE.md`), each with date and
open/held state. Then read the target skill's `MAINTENANCE.md` (next section).
Do both even when the target is named; they cost a few seconds.

## What this skill protects

A skill serves many sessions across many projects and should one day work for
other people (owner decision, 2026-11-08). So:

- **Firm statements only for tool facts, version traps and "the output is
  broken if X" checks.** Everything else is a technique: what it is, where it
  worked (OBSERVED(project)), what else to try; no "always" or "never".
- **One project's case notes** go in `projects/<project>.md`. **The owner's
  conventions and taste** go in `house/`, which ships empty. The general technique lives in `references/` and points back to
  the project file as evidence.
- **One canonical home per fact.** The entry file owns decisions and routing;
  reference files own values and evidence. Every load-bearing claim carries a
  provenance tag and date (`references/provenance-tags.md`, the one glossary).

The eight rots and the check for each: `references/rot-modes.md`.

## The brief (MAINTENANCE.md, one per skill)

Standing direction for one skill's passes; the intake cannot hold it, since
merges clear it. Four parts: what the skill is for and where its owner wants it
to go; where firm rule ends and technique begins for that subject; where things
go; pass notes. Normal use never
loads it. Corpus-wide direction stays here; per-skill direction goes in its
brief. Each line carries a date and source. A line about the machine or
environment names the command this pass ran itself; a worker's report is not a
source (a worker's wrong claim about which program was first on PATH once reached a brief).

- **Start:** read it and follow it in every step. With none, this is the skill's
  first pass; onboard before anything else: (1) draft a brief from what the
  skill holds now (description, entry file, folders, intake) and show it; (2)
  tell the person in a few lines how the loop works: sessions deposit findings
  to `INTAKE.md`, a pass the person approves folds them in, the brief carries
  direction between passes; (3) before asking, check whether the conversation
  already answers what the skill is for and where it should go (a session spent
  redesigning or using the skill usually does); draft the brief from that and
  ask only about the gaps; (4) write the brief from their answers, each line
  sourced to them, then run the pass under it. A dispatched agent stops after
  (1) and returns the draft and questions; only the person answers them.
- **End:** propose changes to the brief inside the one approval message (step 3
  below), or say "no change" in one line. Never skip it silently.

## The pass

One pass audits, merges and asks the person once: one approval message
with defaults, not a question per entry. Nothing is applied before the reply.

### 1. Gather

- **The intake.** Every open entry for the target skill. For a held entry, check
  only whether the condition in its "what would confirm it" line has happened.
  If it has, it joins the open entries; if not, leave it untouched: no
  re-dating, no re-judging, no question. A hold unconfirmed after 90 days is
  dropped with a log line (git keeps it).
- **The project**, when the pass is an audit (run inside the project the skill
  serves). Read its recent artifacts and collect its paid-for mistakes: rejected
  builds, redesigns, wrong tables. For each, ask whether the skill as it stands
  would have prevented it; the ones it would not are the top findings. Then list
  what the project learned that the skill lacks, where the skill contradicts the
  project's own measurements, and any helper written again across scripts or
  sessions (that belongs in the skill's `scripts/`). When a gap needs knowledge
  no project holds, propose a research pass in the approval message rather than
  starting one; once approved, run it with whatever web-research method your harness has and deposit the
  findings to the affected skill's INTAKE.md.
- **The rot sweep** over the target skill (`references/rot-modes.md`), plus
  `python -I scripts/check_values.py <skill dir>` (value duplicates, control
  characters, dead pointers; its docstring lists what it misses).
- **The quality review** (`references/quality-review.md`): the skill judged as
  its user would judge it; at most eight ranked recommendations and a grade. It
  reuses the gathers and merge logs and spawns nothing of its own. Full on a
  first pass, a large change, a grade of C or below, or on request; else a delta
  against `REVIEW.md`. The tier says who runs it: your strongest model (on Claude, Fable) for a
  first review or a skill graded C or below; Opus tier, by an agent that has not
  edited the skill this session, for a routine full review; Sonnet, inline, for
  a delta. (On a non-Claude stack read these tiers as flagship, strong and mid.)

### 2. Triage into four bins

Re-run every checkable claim first. An entry's account can be wrong (3 of
13 were on one pass, `references/evidence.md`); a claim that cannot be cheaply
re-run goes in under a weaker tag or is held.

| Bin | What goes in | Needs the person? |
|---|---|---|
| **Admit** | Re-run tool facts, version traps and broken-output checks; a correction to a fact that was wrong; a technique with its project tag, placed in `references/` or `projects/`; routing rows, pointer fixes, tags, dates, duplicates collapsed to one home | No. Listed one line each in the message; the person can pull any row |
| **Ask** | Any new or changed "always", "never" or "must" in an entry file, quoted in full; any step in a procedure skill (this one, `session-wrapup`, `writing-skills`); archiving or deleting a section; anything that reads as the owner's taste (home is `house/` or CLAUDE.md); moving an entry to another skill's intake; changes to the brief | Yes. One row each, with a recommended answer |
| **Hold** | A behavioural rule seen fewer than about three times, unless the person stated it as a preference (then it is Ask, and the log says the gate was skipped); a claim that could not be re-run | No. Gains a `**Held <date>:** <what would confirm it>` line |
| **Drop** | One-off facts, guesses, entries resolved elsewhere, holds past 90 days | No. Named in the log with the reason |

**A lesson about this skill's own process** goes into `references/evidence.md`
as one line (an Admit row, named as a process lesson). It enters SKILL.md, as
an Ask row, only when it would have prevented a defect the diff reviewer found,
on two passes; that stops the procedure growing every pass.

### 3. One approval message

Send one message, in this order: the Ask table with a recommended
answer per row; the Admit list, one line per entry; hold and drop counts with
the dropped entries named; whole-skill proposals; brief changes or "no change".
End with: "Reply go to take every recommendation, or name the rows to change."
A dispatching session's brief does not replace this; a dispatched agent returns
the message to its caller instead of applying anything.

**Whole-skill proposals** are the quality review's recommendations, each in its
bin (cuts, archives, scripts and research are Ask; pointer fixes and moves to
`house/` are Admit). Size bounds: `references/rot-modes.md`. A pruning probe is
one possible recommendation, never run in a review (`references/pruning.md`).

### 4. Apply and close

- Record the pre-apply point (a commit, or HEAD noted while the skill's files
  are clean) before the first edit; step 5 diffs against it. Place each admitted
  entry in its canonical home with qualifiers and tag intact; delete any copy
  elsewhere.
- Run `check_values.py` on every skill the pass touched. If a value was reworded
  or an allowlist line added only to make it pass, say so in the log; the
  reviewer checks that nothing was lost.
- Run `git status --untracked-files=all`; confirm every new file and folder is
  listed. An ignore rule drops them silently.
- Close INTAKE.md: cleared entries removed; held entries keep their heading and
  carry the `**Held <date>:**` line (the intake counter keys on it); open
  entries that landed below the Merge log move above it. Write a dated Merge log
  entry: counts per bin, where each admitted entry landed, the review result
  when known. Keep the latest log in INTAKE.md; move older ones to
  `INTAKE-ARCHIVE.md`.
- Write or update `REVIEW.md` from the quality review (each recommendation
  approved, declined or done); add its grade line to the brief's Pass notes.

### 5. Review, then commit

A reviewer who made no edits reads the diff against the pre-apply
point, new files included. Its brief names what the scripts cannot see: dropped
qualifiers and tags, contradictions between files, a prose pointer to a file or
section this pass emptied, an allowlist line without a reason. Fix what it
finds, then the reviewer reads the fix diff once, against a copy of the files as
it reviewed them. Two reads stop it; a third only if the fix read found
something above LOW. Add the result to the Merge log and commit. Every merge so
far found defects here with every script passing (`references/evidence.md`);
never skip it.

## Scope rules

- A pass targets one skill. A sibling is touched only where the pass changes a
  contract they share (the intake entry format, the held marker, a
  cross-skill pointer), and only that line. A pass on this skill does not
  include `session-wrapup` (owner decision, 2026-11-08).
- Deposits happen every session; passes run when the
  intake list flags a skill (about five open entries) or a project milestone
  ships. One session is n=1 and cannot tell a recurring rule from a one-off.
- GLOBAL (`~/.claude/INTAKE.md`) is passed like a skill. Each entry's
  destination is an existing skill, the global CLAUDE.md, a `house/` file, or
  a new-skill proposal when a cluster of `gap` entries points the same way.

## Done when

- The rot sweep is clean, or each remaining finding has an intake entry.
- Every paid-for mistake collected in step 1 is one the skill now catches, or
  has an open intake entry naming what would close it.
- `check_values.py` is clean on every touched skill, the diff was read, the
  Merge log is written, the brief was read at the start and its changes (or "no
  change") were in the approval message, and the pass's own lessons are
  deposited to this skill's intake.
- Every trigger has a destination and every destination a trigger: the skill's
  `INTAKE.md` exists and the owner's end-of-session step deposits to it
  (the repo's INSTALL.md names `session-wrapup` as that step). A project skill with a personal
  skill's exact name never runs, so check for one when the destination is a
  project skill.

## Files

`references/`: `rot-modes.md` (rots, checks, structural rules, size bounds),
`provenance-tags.md` (the glossary), `quality-review.md` (method, grades,
template), `pruning.md`, `tooling.md` (skill-creator scripts, this skill's
scripts, the triggering eval), `evidence.md` (rule evidence).
`scripts/`: `check_values.py` (limits in its docstring), `intake_list.py`
(`--counts` for the end-of-session step), `trigger_eval.py` (triggering eval).
`evals/`: cases (`evals/README.md`). `house/`: the owner's wiring; ships empty (see its README).
