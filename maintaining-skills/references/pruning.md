# Pruning sections: policy, and how to run a probe

Runs only on request, or after a model upgrade when the owner asks. Published
pruning machinery operates on whole skills (ASSERTED 2026-10-27,
`evidence.md`); pruning sections is this skill's own invention, so treat it as
policy under test. One probe has run so far (blender, 2026-11-08).

## Policy

- **Only capability-uplift content is ever a candidate**: API deltas, version
  traps, measured settings, things models absorb as they improve. Encoded
  preference (craft, judgement, taste) is exempt; its value does not shrink
  with model quality. List the candidate sections first; with none, the check
  ends and no probe runs.
- **The person picks** which listed sections, if any, to probe.
- **Gain alone cannot decide.** Zero gain looks identical for an absorbed
  section and an unusable one. Retire only on near-zero gain AND high unaided
  pass (absorption shown). Near-zero gain with low unaided pass means the
  section is broken: repair it, do not retire it.
- **Archive and hide, never delete.** Move the section to
  `references/archive/` and drop it from the routing index; git keeps
  everything.
- **Cap: one section archived per file per pass.** Over-pruning is a measured
  harm (`evidence.md`).

## How to brief and grade a probe (technique, OBSERVED(blender) 2026-11-08, one probe)

Learned on the blender probe: 11 sections, 4 rounds, 108 scripts from 28
Sonnet agents, report and harness not shipped (a blend checker, a run grader, an evals.json and brief generators). Move the harness into this skill's `scripts/` if a second
probe makes it routine.

1. **The prompt states the goal and never names the feature.** Prompts that
   said "Follow Path", "through OptiX" or "pack" cued the answer and produced
   gain 0 with 100% unaided pass, which a goal-only re-probe then had to redo.
2. **Grade the saved result, not the script text.** Agents write the script
   without running the tool; a headless run loads the saved file and a checker
   asserts values. Validate the checker first against a hand-written good
   solution and a naive one. On the blender probe that validation alone found
   three skill-side defects (a read-only property documented as settable, a
   pack-order claim, a `new_effect` keyword) before any agent ran, so a probe
   is also a falsifier run.
3. **State the convention the trap depends on**, or the trap is unscorable:
   the camera-roll trap gave +Y-up by two routes until the prompt fixed the
   convention. A leading phrase then pushed every agent to hand math, so state
   it plainly and stop there.
4. **Size.** One agent per section, arm and run, writing several scripts, is
   enough; two runs per arm per prompt separates "never" from "sometimes".
5. **Outcomes to record per section:** gain (with-skill minus unaided pass),
   unaided pass, the verdict (keep, archive, repair, hold with reason), and
   any skill defect the probe exposed, deposited to that skill's intake.

## Tooling for a probe

With/without-skill subagent runs and `aggregate_benchmark.py` from the
skill-creator plugin (`tooling.md`) give pass rate and variance across runs.
`run_eval.py` there tests triggering only and cannot give a task pass rate.
