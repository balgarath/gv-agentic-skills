# INSTALL - craft pair only (blender + art-direction)

Prefer the full INSTALL.md: the craft skills deposit what they learn into
INTAKE.md files, and the meta pair (session-wrapup + maintaining-skills) is
what collects and merges those deposits. Alone, the deposits still accumulate
harmlessly; nothing reads them.

Follow INSTALL.md steps 1, 2, 3 and 6, scoped to `blender/` and
`art-direction/` only, with these changes:

- Step 2: copy only the two folders, still as siblings, names unchanged.
- Step 6: skip the two `maintaining-skills/scripts/...` commands; they need
  the meta pair.
- Degrade notes: both skills cite the provenance-tag glossary
  (`maintaining-skills/references/provenance-tags.md`) and a value-duplicate
  checker in `../maintaining-skills/scripts/`. Without the meta pair, read
  tags like TESTED and OBSERVED(project) at face value and ignore the checker
  row. The "Depositing findings" sections still work: they only append to
  each skill's INTAKE.md.

- Python: two art-direction scripts (`composition_sheet.py`, `contact_sheet.py`)
  need `pip install pillow numpy`.

Report to the user what you installed, the Blender path you set, and that the
intake deposits will sit unread until the meta pair is installed.
