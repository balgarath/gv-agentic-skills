# Triggering eval for the skill disambiguation

Method: one routing prompt, one subagent, one JSON answer, graded by script. No
API key, no `claude -p` sessions, no WSL. Script: `scripts/trigger_eval.py`
(plain Python 3, standard library only).

## What it tests

Four skills have overlapping trigger surfaces, in two pairs.

| Pair | Split | File |
|---|---|---|
| `writing-skills` / `maintaining-skills` | creating goes to writing-skills, repairing goes to maintaining-skills | `triggering.json` (12 cases) |
| `blender` / `art-direction` | broken goes to blender, bad goes to art-direction | `triggering-craft-pair.json` (10 cases) |

Both descriptions in each pair mention skills or renders, so routing has to work
off the situation. The triggering eval assumes a `writing-skills` skill is installed (see Files and fields). The question the eval answers: shown the live descriptions of
every installed skill, does a model pick the intended one for each query.

## How to run it

Run after any description edit to a skill in these pairs, and after adding a
skill whose description could compete with them.

1. **Build the prompt.**
   ```
   python -I ~/.claude/skills/maintaining-skills/scripts/trigger_eval.py build --out <dir>/trigger_prompt.txt
   ```
   It reads the live `name` and `description` of every skill in `~/.claude/skills`
   (add `--plugins` to include plugin skills), loads both case files, shuffles
   the queries under opaque labels `q01` onward (`--seed N` to vary the order),
   and writes the prompt plus `trigger_prompt.txt.key.json` (label to case).
2. **Dispatch one worker** (Haiku or Sonnet; Haiku is the cheaper, harsher
   reader) with the full text of the prompt file and nothing else. It answers
   with one JSON object, label to skill name or `"none"`. Save the reply to a
   file. This is a subscription-covered subagent call; nothing else is needed.
3. **Grade.**
   ```
   python -I ~/.claude/skills/maintaining-skills/scripts/trigger_eval.py grade <reply file> --key <dir>/trigger_prompt.txt.key.json
   ```
   It prints correct fire per file, per category and per intended skill, every
   misroute, every `none`, each near-miss result, and any skill name not in the
   listing. Exit code 1 when a clear case misroutes or a label is missing.

`python -I .../trigger_eval.py selftest` builds a prompt and grades a fabricated
answer; run it after editing the script.

## Reading the result

| Result | Meaning |
|---|---|
| Correct fire | The model named the intended skill. Pass. `skill-creator` also passes where a case's `pass_if` names it (case 12) |
| Misroute | A different skill was named. Read the case's `why_this_points_there`, then the two descriptions: which sentence pulled it? Fix the description, rerun with a different `--seed` |
| None | No skill named. For a clear case, the description is not firing on the situation |
| Near-miss | Cases 11, 12, 109, 110, where either answer is defensible for a first fire. Informational; a miss here is not a fail on its own |

A pass is every clear case correct. A clear case answered `none` counts as a
failure, the same as a clear misroute (exit code 1). Two or more clear misroutes
that repeat under a second seed are a description defect, not noise.

## Honest limits

- **The model knows it is being tested and sees all 22 queries together.** It
  compares them, notices they split into creating versus repairing, and routes
  more carefully than a real session would. It over-routes. A pass here is not
  a hit rate; real triggering baselines run roughly 20 to 50 percent (ASSERTED
  2026-10-27, weak community numbers).
- **So it catches clear misfires only:** a description that sends a creation
  request to the repair skill, or two descriptions that claim the same
  situation. It cannot show that a skill fires unprompted in a long working
  session.
- **The handoff is not tested.** Each SKILL.md opens with a triage line that
  sends the agent to its sibling, and a case's `pass_if` credits "sibling loads
  first, then hands off". That needs a real session loading skills in order.
  Here a wrong first pick is a misroute, even where a real session would
  recover. Do not read a misroute as proof the handoff fails.
- **One answer per case per run.** Twenty-two cases cannot separate small
  differences; rerun with another seed before claiming one.
- The listing is the description text only. Skills with long descriptions may
  be shortened by the host in a live session; this prompt does not shorten them.

## Files and fields

Both case files are bare JSON arrays (the format skill-creator's `run_eval.py`
reads, kept so that runner could be used on a Linux box).

| Field | Meaning |
|---|---|
| `id` | Unique integer. 1 to 12 in the main file, 101 to 110 in the craft file |
| `query` | The prompt, as typed |
| `should_trigger` | Relative to `maintaining-skills` in `triggering.json`, to `blender` in `triggering-craft-pair.json`. Kept for skill-creator's runner; the grader uses `intended_skill` |
| `intended_skill` | The skill that should end up loaded. The real ground truth |
| `category` | `clear` or `near-miss` |
| `pass_if` | The pass criterion for a full session, in words. The grader credits only a direct hit or a named non-handoff terminal such as `skill-creator` |
| `why_this_points_there` | Why the case points where it does. Read this to audit the eval, not to run it |

The `triggering.json` cases assume a separate `writing-skills` skill, which this
pack does not ship. Without it, the cases that intend `writing-skills` will grade
as misroutes or `none` (the runner exits 1). Judge only the `maintaining-skills`
cases there, or install a `writing-skills` skill first.

Legitimate other terminals: `skill-creator` for case 12 (it owns
description-triggering work). In case 110 `blender` may load after
`art-direction` for the volume settings, which a one-shot answer cannot show.

## Status

Built and self-tested 2026-11-08 with a fabricated answer file. Ran once on
2026-11-08 against a real Haiku answer: 22 of 22 correct. Honest reading: a
perfect score here shows only that the descriptions are not clearly broken, given
a model that knows it is being tested and sees every query at once. Harder,
vaguer and multi-skill cases are the next step; add them to the case files
before trusting a pass.
