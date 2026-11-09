# gv-agentic-skills

Four working skills for coding agents, taken from a production Blender and
projection-art pipeline and scrubbed for general use.

- **blender**: scripted scenes and headless EEVEE on Blender 5.x. The API
  changes every tutorial still gets wrong, and the traps in the order a build
  meets them.
- **art-direction**: what an image should aim at and how to check it with a
  test instead of a feeling. Renderer-agnostic.
- **session-wrapup**: the end-of-session checklist. Git state, docs, and the
  intake sweep that writes down what each skill should learn.
- **maintaining-skills**: the merge pass that folds those findings back into
  the skills, with the user approving every rule change.

The four form a loop. The craft skills deposit findings in their INTAKE.md
files, session-wrapup sweeps them in every session, maintaining-skills merges
them. Install all four unless you have a reason not to.

## Install

Point your agent at this repo and tell it: read INSTALL.md and follow it.
INSTALL-craft.md installs only blender and art-direction. INSTALL-meta.md
installs only session-wrapup and maintaining-skills. Built for Claude Code;
each INSTALL file carries a short adaptation note for other harnesses.

## Run session-wrapup yourself

session-wrapup does not fire on its own. Run it at the end of each session:
type `/session-wrapup`, or just tell the agent "run the session wrap-up".
If you skip it, findings pile up in the INTAKE.md files and never get merged.
The standing rule INSTALL.md adds will remind the agent, but don't count on
that alone.

## What the skills assume

Markdown plus Python 3.10+. Most scripts use only the standard library; the two
art-direction image scripts (`composition_sheet.py` needs Pillow and numpy,
`contact_sheet.py` needs Pillow) need `pip install pillow numpy`. The blender skill targets
Blender 5.2 LTS. Factual claims carry provenance tags (TESTED, OBSERVED, DOC);
the glossary is maintaining-skills/references/provenance-tags.md. Project
names in OBSERVED tags refer to the original author's projects; treat them as
evidence trails, not references you can open.

## License

MIT-0 (MIT No Attribution). Use it, change it, sell it, ship it; no
attribution required. See LICENSE.
