# Provenance tags (the one glossary)

This is the only place the tags are defined; every other file points here.
Files in other skills that cite "maintaining-skills skill (Provenance tags)"
land on this file. Bracketed (`[TESTED]`) and bare (TESTED) are the same tag.
Do not coin a variant (`-low`, `-via-summary`); put the nuance in the sentence.

| Tag | Meaning |
|---|---|
| TESTED | Ran it on a stated version of the tool. A file that states its version once at the top need not repeat it per line. "Read its source" is not TESTED; say so in the sentence. |
| DOC | Stated by official documentation or release notes. Name a page only after opening it; otherwise write `[DOC, page not re-checked]`. Never upgrade a bare DOC to a named page by topic. |
| OBSERVED(project) | Seen on a real build of a project, not in a controlled test. One project, so numbers are anchors and not constants. |
| CONVENTION | Widely taught craft that could not be tied to one checkable source. |
| HEURISTIC | A derived starting value, interpolation or prediction; tune by eye. A plan's requirement is HEURISTIC, never TESTED. |
| CORROBORATED | Two or more independent sources agree. |
| VERIFIED-PRIMARY | One primary source, traced by a research pass; the primary may not have been re-read here. |
| ASSERTED | One source, taken at its word. Say in the sentence if it is weak. |
| CONTESTED | Credible sources disagree; both sides are recorded. |
| UNVERIFIED(date) | Could not confirm; the date is when it was added or last carried forward. Also marks code that has not run (name what would verify it). Lifecycle: rot 8 in `rot-modes.md`. |
| CONFLICT(date) | Two statements disagree and no test settles it; an intake entry is open. |
| GAP(date) | Known missing content; says where it will land. |

**Authority rule.** When two statements disagree, the one with a passing test
wins; with no tests, newer provenance wins; with neither, open a CONFLICT
intake entry rather than picking silently.
