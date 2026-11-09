# The quality review: a skill judged as its user would judge it

Read during step 1 of the pass (SKILL.md, The pass, Gather). It produces the
one-page `REVIEW.md` whose recommendations become rows in the approval
message. Added 2026-11-08 after the owner approved all eight recommendations of
the first such report (blender B+, art-direction B-) and asked for it in every
round.

## What it answers

A person using the skill to make a successful project with successful output
would ask five things. The review answers them in that order, one page, and
ends with a grade.

1. **Usefulness.** Does an agent with the skill reach good output faster and
   more reliably than one without? Evidence, not opinion: probe results if
   any exist, the paid-for project mistakes the skill now catches, and the
   ones it still misses (open and held intake entries, gaps found in step 1).
2. **Usability.** Can the fact be reached? Walk two or three real task
   phrases from the entry file to the fact and count hops. What does a
   typical task cost to read (entry file plus the reference it routes to)?
   Would a stranger understand it (owner names, undefined jargon, missing
   version)? Are the splits clean: between sibling skills, and between
   `house/`, `projects/` and general content?
3. **Efficiency.** Which text costs tokens without changing outcomes:
   textbook material a model already holds, narrative that repeats what a
   project file holds, lists that introspection replaces, duplicated facts.
   What to cut, compress or archive, and by how many tokens.
4. **Maintenance.** How has the skill been maintained (passes, intake
   volume, holds, reviewer findings, questions asked), and did that effort
   change correctness or size? Source: the merge logs and `git log`.
5. **Recommendations and grade.** At most eight, ranked by value per effort,
   each with the risk it takes on and the bin it lands in (Ask for cuts,
   archives, new scripts and research; Admit for pointer fixes and moves to
   `house/`). Then a grade and one plain sentence.

## Full or delta

- **Full review** when the skill has no `REVIEW.md`, when more than about a
  quarter of its bytes changed since the last review (`git diff --stat
  <last review commit> -- <skill dir>`), when the last grade is C or below,
  or when the person asks.
- **Delta review** otherwise: open the last `REVIEW.md`, re-check only the
  files this pass or the sessions since touched plus anything the intake
  names, mark each old recommendation done, open or declined, and re-grade
  only if something moved. A delta is a few lines of change in the same file,
  not a new report.

## Cost rules

- No agent runs for the review. Probe results are cited from existing
  reports; a new probe is a recommendation row (`pruning.md`), never part of
  the review.
- No second rot sweep and no second project read. The review consumes what
  step 1 already gathered (the mistakes list, the rot findings,
  `check_values.py` output) and adds only the routing walk, the load table
  and the maintenance read.
- Load table by command, not by reading: `wc -c` on the entry file and each
  reference, tokens as bytes/4, one row per typical task (entry file plus the
  file it routes to). A skill with one reference needs one row.
- One page. Fixed headings, about 60 to 80 lines. If it is longer, it is
  doing step 1's or step 2's work.

## Who runs it (model tiers, 2026-11-08)

- **A first review of a skill, and any review of a skill graded C or below:**
  your strongest model (on Claude, Fable). Novel ground or a skill in trouble is where the
  judgement is hardest.
- **A routine full review:** Opus tier, by an agent that has not edited the
  skill this session. In a dispatched pass that is the gathering worker, before
  any apply.
- **A delta review:** Sonnet, inline in the pass worker. It is mostly
  comparison.
- The independent diff reviewer of step 5 stays separate; the review is not a
  substitute for it.
- The person is the audience. Write it so the recommendations can be approved
  in one reply, as the first one was.
- On a non-Claude stack, map these tiers to your own flagship / strong / mid / cheap models.

## Grade anchors

Letter plus one sentence, so grades compare across passes.

| Grade | Meaning |
|---|---|
| A | A stranger with it reaches good output faster, the evidence shows it, and nothing in it costs more than it saves |
| B | Clear value with evidence; one or two cost centres or gaps named in the recommendations |
| C | Value in places; elsewhere it is costly, unverified or wrong, and the fix is more than a trim |
| D | Would not recommend loading it as it stands |

Plus and minus mark direction within a band. A grade never moves on taste;
it moves when a recommendation lands, a probe reports, or a mistake the skill
should have caught gets through.

## Where it lives

- `<skill>/REVIEW.md`, one file, overwritten each pass; git holds the
  history. Normal use never loads it (the skill's own SKILL.md does not point
  at it). It ships with the skill when shared; it names no owner.
- One line per pass in the skill's `MAINTENANCE.md`, Pass notes:
  `Review <date>: <grade>, <one phrase on where the cost is>; <n> recs,
  <n> approved, <n> done.` That line is the trend; `REVIEW.md` is the detail.
- The merge log records which recommendations were applied, like any other
  row.

## Template

```
# Review - <skill>  (<date>, <full|delta>, by <tier>)

Grade: <letter>. <One sentence.>
Previous: <grade, date> or none.

## Usefulness
<evidence: probe gains if any; mistakes now caught, with the price paid;
mistakes still missed, each pointing at an intake entry or gap>

## Usability
<routing walk: phrase -> hops; load table; stranger test; splits>

## Efficiency
<ranked list of tokens recoverable, with the files and sections>

## Maintenance
<passes, intake volume, holds, reviewer findings, questions asked; what the
effort changed>

## Recommendations (value per effort)
1. <action> (effort; value). Risk: <...>. Bin: <Ask|Admit>.
...
Not recommended: <...>

## Status of previous recommendations
<done / open / declined, one line each>
```

## What it does not do

It does not edit, archive or deposit anything; its output is rows in the
approval message. It does not grade the owner's taste in `house/`. It does
not re-run probes or snippets. It does not replace the rot sweep (defects)
or the project read (mistakes); it frames them for a user and prices them.
