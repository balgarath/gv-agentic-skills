# INSTALL - all four skills (recommended)

You are an agent installing four skills for your user. Follow the steps in
order. Do not interview the user: discover what you need yourself and report
what you did at the end. If a step cannot complete, finish the others and
name the gap in your report.

## 1. Find your skills directory

- Claude Code: `~/.claude/skills` (Windows: `%USERPROFILE%\.claude\skills`).
  Create it if absent.
- Cursor, Codex, or another harness: choose the folder your harness loads
  instructions from (for example a rules directory, or a docs folder your
  AGENTS.md points at). You will copy the four skill folders there and add one
  pointer line per skill to your rules or memory file: the skill name, one
  line on when to use it, and the path to its SKILL.md.

## 2. Copy the skills

Copy `art-direction/`, `blender/`, `session-wrapup/` and `maintaining-skills/`
from this repo into the skills directory as sibling folders, names unchanged.
The skills reference each other by sibling paths, so keep all four together.
If a folder of the same name already exists there, stop and ask the user
before touching it.

## 3. Set the Blender path

Find the Blender executable: check PATH (`where blender` or `which blender`),
then the OS defaults (Windows `C:\Program Files\Blender Foundation\`, macOS
`/Applications/Blender.app/Contents/MacOS/Blender`, Linux `/usr/bin/blender`,
then snap, flatpak and Steam locations). Edit the "Install and invocation"
section of `blender/SKILL.md` to state the path you found. If you find none,
leave the section as shipped and tell the user the blender skill needs
Blender 5.x installed.

Python note: two art-direction scripts (`composition_sheet.py`, `contact_sheet.py`)
need `pip install pillow numpy`. Everything else is standard-library Python.

## 4. Map the model tiers (non-Claude harnesses only)

`maintaining-skills/SKILL.md` and
`maintaining-skills/references/quality-review.md` name Claude tiers (the
strongest tier, which on Claude is Fable, then Opus, Sonnet, Haiku). On any other stack, edit those
mentions to your own flagship / strong / mid / cheap models.

## 5. Wire the heartbeat

The four skills form a loop: the craft skills deposit findings into their
INTAKE.md, session-wrapup sweeps every session's findings in, and
maintaining-skills merges them with the user's approval. The loop only runs
if session-wrapup actually runs. Add one standing rule wherever your harness
keeps standing rules (user memory, CLAUDE.md, a rules file):
"Run the session-wrapup skill before ending any session."
Where the skill says "the user", use whatever you normally call your user.

Note: maintaining-skills mentions a separate `writing-skills` skill for
creating new skills. It is not part of this pack; those mentions degrade to
advice.

## 6. Verify, then report

- The four SKILL.md files exist at their installed paths.
- From the skills directory,
  `python -I maintaining-skills/scripts/intake_list.py --counts` runs and
  lists the four skills (the script takes the folder holding its own skill as the skills root, so it works at any install path; `--root DIR` overrides).
- `python -I maintaining-skills/scripts/check_values.py blender art-direction`
  (run from the skills directory) exits 0.
- The Blender path written in `blender/SKILL.md` exists, or you reported it
  missing.

Report to the user: what you installed and where, the Blender path you set,
the standing rule you added, and any gaps.
