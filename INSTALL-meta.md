# INSTALL - meta pair only (session-wrapup + maintaining-skills)

This pair maintains whatever skills you keep; nothing in it is specific to
Blender or art. session-wrapup is the end-of-session checklist and intake
sweep; maintaining-skills is the merge pass that folds findings back in.

Follow INSTALL.md steps 1, 2, 4, 5 and 6, scoped to `session-wrapup/` and
`maintaining-skills/` only, with these changes:

- Step 2: copy only the two folders, still as siblings, names unchanged. They
  depend on each other (session-wrapup's counting step runs
  `maintaining-skills/scripts/intake_list.py`), so never install one of the
  two alone.
- Step 6: skip the `check_values.py blender art-direction` command unless the
  craft pair is installed; `intake_list.py --counts` should list whatever
  skills exist.

Report to the user what you installed and the standing rule you added.
