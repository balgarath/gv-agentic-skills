# Tooling that already exists: use it, do not rebuild it

## skill-creator plugin

If you have the skill-creator plugin installed, its scripts are under the plugin's `skills/skill-creator/` folder (find it with your harness's plugin listing). Without it, skip this section.

| Script | Use here |
|---|---|
| `quick_validate.py` | Mechanical lint on any edited skill. Needs PyYAML; Python 3.12 has it (ran 2026-11-08) |
| `run_eval.py` | Triggering only: does the description fire. It cannot give a task pass rate (argument list re-read 2026-11-08, not run; it failed on Windows in an earlier run) |
| with/without-skill subagent runs (its SKILL.md, "Running and evaluating test cases") | No-skill baselines for a pruning probe (`pruning.md`) |
| `aggregate_benchmark.py` | Pass rate and variance across those runs |
| `run_loop.py` | After any description edit; wraps `run_eval.py` and `improve_description.py` |
| `eval-viewer/generate_review.py` | Shows results for human review |
| `agents/analyzer.md` | Its "non-discriminating assertions" check finds claims that never fail |

## This skill's own scripts

| Script | Use |
|---|---|
| `scripts/check_values.py` | Value-duplicate guard, control-character scan, dead-pointer scan, over any paths given (with none: blender and art-direction). Each corpus keeps its allowlist at `<skill>/scripts/check_values.allow`. It finds the same value repeated in two files and is blind to two files giving different values for one parameter; it checks that a pointed-to path exists and cannot check a section name or whether the target holds what the pointer promises. Details and limits in its docstring |
| `scripts/trigger_eval.py` | Triggering eval without an API key: `build` writes one routing prompt, `grade` scores a subagent's JSON answer, `selftest` checks the script. See `evals/README.md` |
| `scripts/intake_list.py` | One line per intake entry across every skill plus GLOBAL, with open/held; `--counts` for the end-of-session summary; `--project DIR` to include a project's own skills |

## This skill's triggering eval

`evals/` holds the disambiguation eval for both sibling pairs
(`writing-skills` / `maintaining-skills`, `blender` / `art-direction`). Run it
after any description edit: `scripts/trigger_eval.py build`, dispatch one Haiku
or Sonnet worker with the prompt, then `grade` its JSON answer. No API key, no
WSL. It catches clear misfires only and does not test the triage-line handoff;
read `evals/README.md` for how to run it and for its limits.

## Falsifier notes (moved here from the entry file, 2026-11-08)

- **Control-character scan** in `check_values.py`: after normalising CRLF it
  fails on bytes 0x00-0x08 and 0x0B-0x1F and on a TAB after line start, across
  every `.md` in the corpus, INTAKE.md included. A non-raw Python string turns
  the backslash-t, backslash-r and backslash-05 of a Windows path into a TAB, a CR and a control byte (TESTED 2026-11-04,
  by synthetic replay).
- **Pointer scan** in `check_values.py`: fails when a backticked path under the
  scanned folders (list: `check_values.py` docstring) exists nowhere in that
  skill or a sibling (TESTED 2026-11-05, by synthetic replay). A path that
  exists only in a sibling passes.
- **Hard-wrapped paragraphs** are read as one text, so a value split across a
  line break is still seen (TESTED 2026-11-03). Blindness to two files giving
  different values for one parameter was TESTED 2026-10-28, by replay.
- **Measured-value claims** ("this range renders best") need a measurement
  script with a tolerance, a different artifact from a snippet check; write one
  only for the few values that gate real decisions.
- **Honesty:** no empirical study shows executable docs stay current by
  themselves (ASSERTED 2026-10-27); the known failure is the tedium of making
  existing docs pass, so the runner must be cheap and wired into the pass.
- **A new agent file may not be dispatchable from the session that wrote it** (`Agent type '...' not found`); the first test of a new agent file belongs in a fresh session (OBSERVED(maintaining-skills), 2026-11-06, not re-run).
