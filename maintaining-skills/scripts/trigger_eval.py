"""Triggering eval, no API key: build one routing prompt, grade one JSON answer.

Why it exists: skill-creator's run_eval.py needs `claude -p` sessions and a Linux
select() on pipes. This does the same job for clear misfires with one dispatched
subagent (Haiku or Sonnet) and plain Python 3 (standard library only).

  python -I trigger_eval.py build [--out FILE] [--seed N] [--plugins] [--evals DIR]
      Reads the live name and description of every skill in ~/.claude/skills (and,
      with --plugins, the skills under ~/.claude/plugins), builds an "available
      skills" listing, loads the case files in evals/, shuffles the queries under
      opaque labels (q01, q02, ...) and writes:
        FILE            the prompt; hand its full text to ONE subagent
        FILE.key.json   label -> case id, the skill names listed, the seed
      Default FILE: trigger_prompt.txt in the current directory.

  python -I trigger_eval.py grade ANSWER [--key FILE.key.json] [--evals DIR]
      ANSWER is the subagent's reply (a file; text around the JSON is tolerated).
      Reports correct fire per pair, misroutes, nones, near-miss results, and any
      answer that names a skill not in the listing.

  python -I trigger_eval.py selftest
      Builds a prompt in a temp dir and grades a fabricated answer. Exits 1 on a
      broken script.

Limit (see evals/README.md): the model sees every query at once and knows it is
being tested, so it over-routes. Good for clear misfires, not for real hit rates.
The handoff through a skill's triage line is not tested.
"""
import argparse
import json
import random
import re
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).resolve().parent
SKILL_DIR = HERE.parent                      # .../maintaining-skills
EVALS = SKILL_DIR / "evals"
SKILLS = SKILL_DIR.parent                    # ~/.claude/skills
PLUGINS = SKILLS.parent / "plugins"
CASE_FILES = ["triggering.json", "triggering-craft-pair.json"]
# A "pair" is the set of intended skills inside one case file.


def parse_frontmatter(text):
    """Return (name, description) from a SKILL.md; either may be None."""
    m = re.match(r"﻿?---\s*\r?\n(.*?)\r?\n---", text, re.S)
    if not m:
        return None, None
    fields, key = {}, None
    for line in m.group(1).splitlines():
        km = re.match(r"^([A-Za-z_-]+):\s*(.*)$", line)
        if km and not line.startswith((" ", "\t")):
            key = km.group(1)
            fields[key] = km.group(2).strip()
        elif key and line.strip():
            fields[key] += " " + line.strip()
    out = {}
    for k in ("name", "description"):
        v = fields.get(k)
        if v is not None:
            v = v.strip()
            if v in (">", "|", ">-", "|-"):
                v = ""
            if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
                v = v[1:-1]
        out[k] = v
    return out["name"], out["description"]


def collect_skills(with_plugins):
    found = {}
    paths = sorted(SKILLS.glob("*/SKILL.md"))
    if with_plugins and PLUGINS.is_dir():
        paths += sorted(PLUGINS.glob("marketplaces/*/plugins/*/skills/*/SKILL.md"))
        paths += sorted(PLUGINS.glob("cache/**/skills/*/SKILL.md"))
    for p in paths:
        name, desc = parse_frontmatter(p.read_text(encoding="utf-8", errors="replace"))
        if not name or not desc:
            print("skipped (no name or description): %s" % p, file=sys.stderr)
            continue
        found.setdefault(name, desc)   # personal skills come first and win
    return found


def load_cases(evals_dir):
    cases = []
    for fname in CASE_FILES:
        f = Path(evals_dir) / fname
        if not f.exists():
            print("missing case file: %s" % f, file=sys.stderr)
            continue
        for c in json.loads(f.read_text(encoding="utf-8")):
            c["_file"] = fname
            cases.append(c)
    return cases


PROMPT_HEAD = """You are doing a skill-routing exercise. Below is the list of skills an assistant has
available, exactly as its session shows them (name, then description). After the list are
numbered user messages. For EACH message, name the ONE skill the assistant should load
first to handle it, judging only from the descriptions. If no skill fits, answer "none".
Use a skill name exactly as listed. Do not run any tools and do not read any files.

=== AVAILABLE SKILLS ===
"""

PROMPT_TAIL = """
=== MESSAGES ===
{messages}

=== ANSWER FORMAT ===
Reply with ONLY one JSON object, no prose and no code fence, mapping every label to a
skill name or "none". Example shape: {{"q01": "some-skill", "q02": "none"}}
Every label from q01 to q{last} must appear exactly once.
"""


def build(args):
    skills = collect_skills(args.plugins)
    cases = load_cases(args.evals)
    if not cases:
        sys.exit("no cases loaded")
    rng = random.Random(args.seed)
    order = list(range(len(cases)))
    rng.shuffle(order)
    labels = {}
    msgs = []
    for n, idx in enumerate(order, 1):
        lab = "q%02d" % n
        labels[lab] = {"id": cases[idx]["id"], "file": cases[idx]["_file"]}
        msgs.append("[%s] %s" % (lab, cases[idx]["query"]))
    listing = "\n".join("- %s: %s" % (n, d) for n, d in sorted(skills.items()))
    text = PROMPT_HEAD + listing + "\n" + PROMPT_TAIL.format(
        messages="\n\n".join(msgs), last="%02d" % len(cases))
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(text, encoding="utf-8")
    key = Path(str(out) + ".key.json")
    key.write_text(json.dumps({"seed": args.seed, "labels": labels,
                               "skills": sorted(skills)}, indent=1), encoding="utf-8")
    print("wrote %s (%d skills, %d cases, %d chars)" % (out, len(skills), len(cases), len(text)))
    print("wrote %s" % key)
    print("next: give the full text of the prompt file to ONE Haiku or Sonnet subagent, "
          "save its JSON reply, then run: grade <reply file> --key %s" % key)


def extract_json(text):
    start, end = text.find("{"), text.rfind("}")
    if start < 0 or end < start:
        sys.exit("no JSON object found in the answer")
    try:
        obj = json.loads(text[start:end + 1])
    except json.JSONDecodeError as e:
        sys.exit("answer JSON does not parse: %s" % e)
    if not isinstance(obj, dict):
        sys.exit("answer JSON is not an object")
    return obj


def acceptable_alternates(case, skill_names):
    """Skills pass_if names as legitimate terminals other than the intended one.

    pass_if also names a sibling that 'hands off' to the intended skill. That path
    needs a real session and is NOT credited here: it is reported as a misroute.
    """
    if "skill-creator" in case.get("pass_if", ""):
        return {"skill-creator", "anthropic-skills:skill-creator"}
    return set()


def short(q, n=70):
    q = " ".join(q.split())
    return q if len(q) <= n else q[:n - 3] + "..."


def grade(args):
    key = json.loads(Path(args.key).read_text(encoding="utf-8"))
    listed = set(key["skills"])
    ans = extract_json(Path(args.answer).read_text(encoding="utf-8", errors="replace"))
    by_id = {}
    for c in load_cases(args.evals):
        by_id[(c["_file"], c["id"])] = c
    rows, missing, unknown = [], [], []
    for lab, ref in key["labels"].items():
        case = by_id.get((ref["file"], ref["id"]))
        if case is None:
            sys.exit("case %s/%s in the key is not in the case files; rebuild" % (ref["file"], ref["id"]))
        if lab not in ans:
            missing.append(lab)
            continue
        chosen = str(ans[lab]).strip()
        if chosen.lower() == "none":
            res = "none"
        elif chosen == case["intended_skill"]:
            res = "correct"
        elif chosen in acceptable_alternates(case, listed):
            res = "alt-ok"
        else:
            res = "misroute"
        if chosen.lower() != "none" and chosen not in listed:
            unknown.append((lab, chosen))
        rows.append((ref["file"], case, chosen, res))
    for lab in ans:
        if lab not in key["labels"]:
            unknown.append((lab, "<label not in key>"))

    print("Triggering eval: %d answered of %d" % (len(rows), len(key["labels"])))
    if missing:
        print("MISSING labels (counted as neither pass nor fail): %s" % ", ".join(sorted(missing)))
    print()
    for fname in CASE_FILES:
        fr = [r for r in rows if r[0] == fname]
        if not fr:
            continue
        ok = sum(r[3] in ("correct", "alt-ok") for r in fr)
        print("%s: correct fire %d of %d" % (fname, ok, len(fr)))
        for cat in ("clear", "near-miss"):
            cr = [r for r in fr if r[1].get("category") == cat]
            if cr:
                print("  %-9s %d of %d" % (cat, sum(r[3] in ("correct", "alt-ok") for r in cr), len(cr)))
        for skill in sorted({r[1]["intended_skill"] for r in fr}):
            sr = [r for r in fr if r[1]["intended_skill"] == skill]
            print("  intended %-20s %d of %d" % (skill, sum(r[3] in ("correct", "alt-ok") for r in sr), len(sr)))
    print()
    bad = [r for r in rows if r[3] == "misroute"]
    print("Misroutes (%d):" % len(bad))
    for f, c, chosen, _ in bad:
        print("  case %s [%s] wanted %s, got %s : %s" % (c["id"], c.get("category"), c["intended_skill"], chosen, short(c["query"])))
    nones = [r for r in rows if r[3] == "none"]
    print("None (%d):" % len(nones))
    for f, c, chosen, _ in nones:
        print("  case %s [%s] wanted %s : %s" % (c["id"], c.get("category"), c["intended_skill"], short(c["query"])))
    print("Near-miss results:")
    for f, c, chosen, res in rows:
        if c.get("category") == "near-miss":
            print("  case %s wanted %s, got %s -> %s" % (c["id"], c["intended_skill"], chosen, res))
    if unknown:
        print("Names not in the listing (check for typos or invention):")
        for lab, n in unknown:
            print("  %s -> %s" % (lab, n))
    print()
    print("Not tested: handoff through a triage line. A misroute above may still recover "
          "in a real session; a correct fire here may not fire unprompted.")
    clear_bad = [r for r in bad if r[1].get("category") == "clear"]
    clear_none = [r for r in nones if r[1].get("category") == "clear"]
    return 1 if (clear_bad or clear_none or missing) else 0


def selftest(_args):
    with tempfile.TemporaryDirectory() as d:
        out = Path(d) / "p.txt"
        ns = argparse.Namespace(out=str(out), seed=7, plugins=False, evals=str(EVALS))
        build(ns)
        key = json.loads(Path(str(out) + ".key.json").read_text(encoding="utf-8"))
        by_id = {(c["_file"], c["id"]): c for c in load_cases(EVALS)}
        ans = {}
        for i, (lab, ref) in enumerate(sorted(key["labels"].items())):
            c = by_id[(ref["file"], ref["id"])]
            ans[lab] = c["intended_skill"] if i % 4 else ("none" if i % 8 == 0 else "bogus-skill")
        ap = Path(d) / "a.json"
        ap.write_text("Here you go:\n" + json.dumps(ans), encoding="utf-8")
        rc = grade(argparse.Namespace(answer=str(ap), key=str(out) + ".key.json", evals=str(EVALS)))
        print("selftest grade exit code %d (1 expected: fabricated misroutes)" % rc)
        return 0 if rc == 1 else 1


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    b = sub.add_parser("build")
    b.add_argument("--out", default="trigger_prompt.txt")
    b.add_argument("--seed", type=int, default=1)
    b.add_argument("--plugins", action="store_true")
    b.add_argument("--evals", default=str(EVALS))
    g = sub.add_parser("grade")
    g.add_argument("answer")
    g.add_argument("--key", default="trigger_prompt.txt.key.json")
    g.add_argument("--evals", default=str(EVALS))
    sub.add_parser("selftest")
    a = ap.parse_args()
    if a.cmd == "build":
        build(a)
    elif a.cmd == "grade":
        sys.exit(grade(a))
    else:
        sys.exit(selftest(a))


if __name__ == "__main__":
    main()
