"""
Intake lister: one line per intake entry across every skill, or counts only.

Lives at <skills root>/maintaining-skills/scripts/intake_list.py
Used by:  maintaining-skills (full list, every run)
          session-wrapup   (--counts, every session)

Run with plain Python 3.10+, standard library only:

  python -I intake_list.py                 # full list, grouped by skill, GLOBAL last (if present)
  python -I intake_list.py --counts        # one line per skill with entries, then one
                                           # line naming skills with no intake file
  python -I intake_list.py --open-only     # full list, held entries left out
  python -I intake_list.py --project DIR   # also scan DIR/.claude/skills/*/INTAKE.md
  python -I intake_list.py --root DIR      # skills root (default: the folder holding this
                                           # skill's own folder, wherever you installed it)

GLOBAL is an optional INTAKE.md one level above the skills root (for a root of
~/.claude/skills that is ~/.claude/INTAKE.md). If it does not exist it is
skipped silently.

What counts as an entry: a heading line matching `## <year>-...`. The intake
files print their own entry format as a literal `## <date> | ...` line, so a
bare `## ` pattern would overcount by one per file; keying on the year avoids it.

What counts as held: inside an entry, any line that starts with `**` and
contains the word "held" (any case). The merge pass writes that marker when it
holds an entry back (`maintaining-skills`, merge step "Apply and close"). Examples
that match today: `**Held 2026-11-08.**`, `**Still held 2026-11-05 ...**`,
`**Part promoted 2026-11-05.** ... Held by owner's decision`.

Anything under a heading that is not a dated entry (for example `## Merge log`)
is ignored until the next dated heading.

Exit code is always 0; this is a report, not a gate.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

ENTRY = re.compile(r"^## (2\d{3}-\d{2}-\d{2})\s*(.*)$")
HEADING = re.compile(r"^## ")
CLAIM_WIDTH = 96


def parse(path: Path) -> list[dict]:
    text = path.read_text(encoding="utf-8", errors="replace").replace("\r\n", "\n")
    entries: list[dict] = []
    cur: dict | None = None
    for line in text.split("\n"):
        m = ENTRY.match(line)
        if m:
            rest = m.group(2)
            parts = [p.strip() for p in rest.split("|") if p.strip()]
            kind = parts[0] if parts else ""
            # headings without pipes ("## 2026-10-31 gap: ...") still get a type word
            if not parts and rest.strip():
                kind = rest.strip().split()[0].rstrip(":")
            elif parts and " " in kind:
                kind = kind.split()[0].rstrip(":")
            cur = {"date": m.group(1), "kind": kind[:12], "claim": "", "held": False}
            entries.append(cur)
            continue
        if HEADING.match(line):
            cur = None
            continue
        if cur is None:
            continue
        s = line.strip()
        if s.startswith("**") and "held" in s.lower():
            cur["held"] = True
        # the claim is the first paragraph, joined across hard wraps, up to the display width
        if s.startswith("```"):
            cur["claim_done"] = True
        elif not s:
            if cur["claim"]:
                cur["claim_done"] = True
        elif not cur.get("claim_done") and len(cur["claim"]) < CLAIM_WIDTH:
            cur["claim"] = re.sub(r"\s+", " ", (cur["claim"] + " " + s).strip())
    return entries


def shorten(s: str, width: int = CLAIM_WIDTH) -> str:
    s = s.replace("**", "")
    return s if len(s) <= width else s[: width - 3].rstrip() + "..."


def collect(root: Path, projects: list[Path]) -> tuple[list[tuple[str, Path]], list[str]]:
    found: list[tuple[str, Path]] = []
    missing: list[str] = []
    if root.is_dir():
        for d in sorted(p for p in root.iterdir() if p.is_dir() and not p.name.startswith(".")):
            f = d / "INTAKE.md"
            (found if f.is_file() else missing).append((d.name, f) if f.is_file() else d.name)
    for proj in projects:
        pr = proj / ".claude" / "skills"
        if pr.is_dir():
            for d in sorted(p for p in pr.iterdir() if p.is_dir()):
                f = d / "INTAKE.md"
                if f.is_file():
                    found.append((f"{proj.name}/{d.name}", f))
    g = root.parent / "INTAKE.md"
    if g.is_file():
        found.append(("GLOBAL", g))
    return found, missing


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--counts", action="store_true", help="counts only, one line per skill")
    ap.add_argument("--open-only", action="store_true", help="leave held entries out of the list")
    ap.add_argument("--project", action="append", default=[], metavar="DIR",
                    help="also scan DIR/.claude/skills/*/INTAKE.md (repeatable)")
    ap.add_argument("--root", default=str(Path(__file__).resolve().parents[2]),
                    help="skills root (default: parent of this skill's folder)")
    ap.add_argument("--trigger", type=int, default=5, help="open entries that flag a skill for a merge")
    a = ap.parse_args()

    found, missing = collect(Path(a.root), [Path(p) for p in a.project])
    total_open = total_held = 0
    flagged: list[str] = []
    for name, path in found:
        entries = parse(path)
        if not entries:
            print(f"{name}: 0 open" if a.counts else f"## {name}: 0 open")
            if not a.counts:
                print()
            continue
        held = sum(e["held"] for e in entries)
        n_open = len(entries) - held
        total_open += n_open
        total_held += held
        if n_open >= a.trigger:
            flagged.append(name)
        head = f"{name}: {n_open} open" + (f", {held} held" if held else "")
        if a.counts:
            print(head)
            continue
        print(f"## {head}")
        for i, e in enumerate(entries, 1):
            if a.open_only and e["held"]:
                continue
            state = "held" if e["held"] else "open"
            print(f"{i:>3}. {e['date']}  {state:<4}  {e['kind']:<12} {shorten(e['claim'])}")
        print()
    if missing:
        print("no intake file: " + ", ".join(missing))
    line = f"total: {total_open} open, {total_held} held"
    if flagged:
        line += f". At or past {a.trigger} open: {', '.join(flagged)}"
    print(line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
