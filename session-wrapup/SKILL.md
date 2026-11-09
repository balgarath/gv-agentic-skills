---
name: session-wrapup
description: Use before ending any session, when the user says wrap up, done for today, close out, or ready to close. The mandatory cleanup checklist - git state in every repo the session touched, the project's own wrapup steps, docs and TODOs, the intake sweep that deposits what each skill should learn, intake counts, and the reflection questions.
---

# Session wrapup

Run every step. A session is not "ready to close" until each row of the output
block is PASS, or N/A with its reason. Keep it cheap: one pass, no
deliberation. The merge pass (`maintaining-skills`) judges what this skill
deposits; this skill only has to deposit it.

## 1. Git, in every repo this session changed

The working folder may not be a repo while the work landed in one that is
(often `~/.claude`). Name each repo touched and run this in each:

```bash
git status --porcelain
B=$(git symbolic-ref --quiet --short refs/remotes/origin/HEAD 2>/dev/null | sed 's#^origin/##')
[ -n "$B" ] || for b in main master; do git show-ref --verify --quiet "refs/heads/$b" && B=$b && break; done
[ -n "$B" ] || echo "no main/master: name the default branch by hand"
echo "default=$B remote=[$(git remote)]"
[ -n "$B" ] && git branch --no-merged "$B"
```

- **Commit only what this session changed**, staged by path. List any other
  change and leave it alone: harness files (`.claude.json`, `file-history/`,
  `state/`, a `settings.json` edit you did not make), another session's work,
  the user's own edits. Ask before discarding anything.
- **Unmerged branches.** Each branch `--no-merged` prints is a FAIL until it
  is merged or the user says to keep it. This works with no remote
  (TESTED 2026-11-08, local repo with no remote).
- **With a remote:** `git log origin/$B..HEAD --oneline` shows what is not
  pushed. If you are in a cloud or ephemeral session: push the feature branch and give a clickable PR link;
  never push the default branch. In a local session (the usual case): merge or push as the project's
  CLAUDE.md says. Run step 2 before any push or merge to the default branch; a
  project step may gate it (for example a deploy risk check). Before any PR: `git fetch origin && git merge origin/$B
  --no-edit`, resolve, commit, push. With no remote, report N/A "no remote";
  `git log origin/...` is a fatal error there, not an empty result (TESTED
  2026-11-04).
- **Merged branches**, local only:
  `git branch --merged "$B" | grep -E 'claude/|feat/|fix/' | xargs -r git branch -d`.

## 2. The project's own wrapup steps

A personal skill shadows a project skill of the same name (DOC,
code.claude.com/docs/en/skills, opened 2026-11-08), so a project's
`.claude/skills/session-wrapup/SKILL.md` never runs by itself. If the working
project has one, or a wrapup section in its CLAUDE.md, open it now and run its
project-only steps (a deploy risk check, a staging sync, a different TODO
path). Report each as its own row. Skip the steps that repeat this file. Then do any
push or merge that step 1 held back for this step.

## 3. Docs, TODOs and rules

Per the project's CLAUDE.md and any global documentation habits:
- project docs named in the project's CLAUDE.md updated for what changed;
- items finished this session moved from `docs/todos.md` to
  `docs/completed-todos.md` (N/A if the project keeps none);
- any "when X, also do Y" rule that came up this session added to the
  Checklists section of the right CLAUDE.md (project or global).

## 4. Intake sweep

Findings go to `INTAKE.md` files, never into a skill's reference files
mid-session; one session is n=1. A skill being wrong outranks a new finding,
since a wrong fact costs time every session until it is fixed.

Walk the session once per skill, not once overall:

1. **List the skills.** Those this session loaded (Skill tool calls, reads of
   a SKILL.md), plus those it should have loaded: a task matched a skill's
   description and ran without it. One scan of the skill list is enough.
2. **For each skill, three questions.** One line each, or "nothing":
   - What cost time that this skill should have prevented?
   - What did the skill say that was wrong, or leave out that the session
     needed?
   - What did the session learn that the skill lacks: a tool fact, a trap, a
     technique and the project it worked on, a gap?
3. **Deposit each non-empty answer** as one entry in that skill's intake:
   ```
   ## <date> | <fact|trap|measurement|conflict|gap|technique> | proposed home: <file section>
   <the claim; how it was verified; version or project; cost if known>
   ```
   Say which project it came from. The merge pass decides whether it is a
   rule or a technique; do not pre-judge it here, and do not skip it because
   it is small.
4. **Nothing fits.** `~/.claude/INTAKE.md`, tagged `gap`. Plugin and
   `anthropic-skills:*` skills: also GLOBAL (their directories are
   overwritten on update, ASSERTED 2026-10-27). Project skills under
   `<project>/.claude/skills/<name>/`: GLOBAL, tagged
   `project:<project>/<name>`, since the counter in step 5 reads only
   `~/.claude/skills` unless given `--project`.
5. **Last, the same three questions about this wrapup run**, deposited to
   `~/.claude/skills/session-wrapup/INTAKE.md`. This skill's lessons only
   appear while it runs, so this is their one chance.

Destination for a personal skill: `~/.claude/skills/<name>/INTAKE.md`.
Create it from the stub when absent, then append:

```bash
N=<name>; S=~/.claude/skills/$N/INTAKE.md
test -f "$S" || sed "s/SKILLNAME/$N skill/" ~/.claude/skills/session-wrapup/INTAKE-stub.md > "$S"
```

## 5. Intake counts

```bash
python -I <skills dir>/maintaining-skills/scripts/intake_list.py --counts
```

Paste the output as printed: open and held per skill, the skills with no
intake file, and the skills at or past five open entries. For each flagged
skill say plainly that it is due for a `maintaining-skills` pass from a fresh
session. Do not merge during wrapup.

## 6. Reflection

Answer each in a few plain lines. The user reads these to catch blind spots, so
name things.

1. What in this session's output would you not bet on, and what would check it?
2. What did the instructions leave open that you filled with a guess, and what
   did you guess?
3. What did you do more than once that a script, hook or skill line would have
   done once? (If a skill fits, that answer is a step 4 deposit.)
4. What should the user do differently next time, and what should the next session
   start with?

## Output

```
Session Cleanup
[PASS/FAIL/N/A] 1a Committed this session's changes (repos: ...)
[PASS/FAIL/N/A] 1b No unmerged branches; pushed or PR link (or: no remote)
[PASS/FAIL/N/A] 2  Project wrapup steps (which: ...)
[PASS/FAIL/N/A] 3  Docs, TODOs, CLAUDE.md rules
[PASS/FAIL/N/A] 4  Intake sweep: <n> entries to <skills>; wrapup's own: <n>
[INFO         ] 5  Intake counts: <pasted>; due for a pass: <skills or none>
[PASS         ] 6  Reflection answered below
```

Every N/A carries its reason after a colon. Fix a FAIL before declaring the
session ready to close.
