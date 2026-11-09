# The eight ways a skill corpus rots, and the structural rules that prevent them

Read during the rot sweep (SKILL.md, The pass, step 1) and when editing any
skill. Each rot was found at real cost in the blender and art-direction corpus
(`evidence.md`). Symptom, then the check that finds it.

The core move: audit a skill against the project that uses it, in both
directions, with the project's own history as the test set. Retrieval testing
cannot do this job. Point queries find an answer and pass while four files hold
four different values; contradiction is a property of the whole corpus, so it
needs cross-file sweeps, not per-question tests.

| # | Rot | Check |
|---|---|---|
| 1 | The always-loaded entry file contradicts the corpus's own measurements | For every operational claim in SKILL.md, locate its evidence in a reference file and compare. A claim with no evidence file is also a finding |
| 2 | N different values for one parameter across N files | Grep each named parameter or number across every file. One fact in two places with two values is a defect; in two places with one value it is a pending defect. `scripts/check_values.py` finds only the second kind. A value changed to pass the guard becomes a pointer to its home or a `check_values.allow` line with a reason, never a reworded number |
| 3 | A scoped truth stated as a universal law | For each claim ask "under what engine, camera, medium or version was this measured?" If the answer is narrower than the sentence, rescope the sentence. A copied claim: diff its qualifiers and tag against the source; each hop tends to drop one, so it arrives broader and surer than measured |
| 4 | Mutually contradictory items inside one checklist | Read each checklist as a single instruction set; flag pairs that cannot both be followed |
| 5 | Code pasted in prose that has never run | Run every code block (a snippet runner where the corpus has one; the blender skill's `scripts/check_snippets.py` is the worked example). Undefined names, missing imports and deprecation warnings are failures. Blocks that cannot run standalone are fenced `norun` with a stated reason |
| 6 | The same trap documented in several places | Duplicates drift into contradictions, and repetition biases which value an agent follows regardless of correctness (ASSERTED 2026-10-27, `evidence.md`). Delete all but one canonical home; never "see also" a duplicate |
| 7 | The entry file's descriptions of its reference files have drifted | Regenerate each description from the file's actual section headings and diff |
| 8 | UNVERIFIED markers that never resolve | List every UNVERIFIED, TODO, GAP and CONFLICT marker with its age. Any older than two passes is verified, deleted, or re-dated with a stated reason |

## Structural rules a healthy corpus obeys

Enforce these during any edit; they make the rots structurally hard to
reintroduce.

- **Built for many projects, and to be shared.** Of every claim, at deposit
  and at merge, ask: true for every project, or one way that worked on one
  project? Only tool facts, version traps and "the output is broken if X"
  checks are stated as rules. Craft, tuned settings and workflow are
  techniques: what it is, where it worked, what else to try. One project's
  case notes go in `projects/<project>.md`; the owner's standing conventions
  go in `house/`, which says it can be deleted when sharing. New reference
  files are welcome when a topic has no good home.
- **One canonical home per fact.** Every value, trap or rule lives in exactly
  one section; everything else points there.
- **The entry file owns decisions and checks; reference files own values and
  evidence.** The always-loaded file never carries a tuned number that a
  measurement file also carries, so the two cannot disagree. Exception: binary
  identity facts (names, paths, renames) may be duplicated when a script
  checks them.
- **Scope on every claim**, in the same sentence.
- **No prose-only snippets.** Code beyond about 15 lines is a script that has
  run, or carries UNVERIFIED(date) naming what would verify it.
- **Provenance tag and date on every load-bearing claim**
  (`provenance-tags.md`), with the UNVERIFIED lifecycle from rot 8.
- **Index in the agent's words at the moment of need** (symptoms and tasks),
  not subject-matter vocabulary. Each section is reached from a row in the
  entry file; walk a few real task phrases from the entry file to the fact.
- **Entry-file size.** Decision-critical content fits the first ~5,000 tokens,
  which is what survives compaction. Being under the official limits is not
  the lever: the audited skill was inside every stated limit and failed in all
  eight ways (OBSERVED 2026-10-27, `evidence.md`). A reference past about 300
  lines gets a local index or a split; split into references inside one
  skill, not into sibling skills, since each sibling must trigger on its own
  description.
- **Description check.** A body far larger than its description is not itself
  a defect (`evidence.md`). Judge the description by reading it against real
  trigger phrases; run the triggering eval (`tooling.md`) after editing it.
