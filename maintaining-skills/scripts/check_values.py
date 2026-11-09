"""
Value-duplicate guard: fail when the same tuned number appears in more than one file.
Also a control-character scan: fail on stray bytes a non-raw Python string writes into
a markdown file (see control_scan), across every .md in scope, INTAKE.md included.
Also a pointer scan: fail when a backticked path under references/, scripts/, evals/, projects/ or house/
exists nowhere (see pointer_scan), across the files the value guard reads.

Failure mode 2 of the eight (see the maintaining-skills skill): one parameter,
several files, several values. The cure is one canonical home per tuned value.
This script finds the cheap half of the problem mechanically: the SAME value
repeated, in the SAME context, in two different files. It does not find two
files that DISAGREE (different values for one parameter); that stays a manual
grep, and so do repeats inside one file unless --within-file is given.

It lives in the maintaining-skills skill because it serves every corpus, not one.
Run with plain Python (3.10+, standard library only, no Blender):

  python -I check_values.py                      # blender + art-direction skills
  python -I check_values.py PATH [PATH ...]      # files or directories of .md
  python -I check_values.py --allow FILE         # use exactly this allowlist (repeatable);
                                                 # turns allowlist discovery off
  python -I check_values.py --within-file        # also list repeats inside one file
                                                 # (advisory, never affects the exit code)
  python -I check_values.py --explain            # show the shared context words
  python -I check_values.py --list-allowed       # show findings the allowlist suppressed

With no PATH it scans SKILL.md, references/, projects/ and house/ of the `blender` and
`art-direction` skills, found as siblings of this script's skill directory
(<skills>/maintaining-skills/scripts/..). NOTES-FOR-REVIEW.md, INTAKE.md and
INTAKE-ARCHIVE.md are never scanned for values.

Allowlist: per corpus, discovered automatically. For every scanned file the script
walks up to the directory holding SKILL.md and loads `scripts/check_values.allow`
there if it exists, so each corpus keeps its own exceptions beside its own files.
With no allowlist found there are no exceptions. `--allow FILE` replaces discovery
with exactly the files given.

Paragraph joining: a hard-wrapped paragraph is read as one text, so a value and its
context words split across a line break are seen together. Paragraphs end at a blank
line, a heading, a fence, a table row or a new list item; each table row is its own
unit. A finding is reported at the line where the value starts.

What counts as a tuned value (everything else is ignored):
  * decimals            0.012   1.15   22.88
  * ranges              5 to 8   0.005-0.03   30 to 40 percent
  * numbers with units  400 m   30 MW   7.2 km   2,500 W   45 percent   2x
  * comma-grouped counts  2,500
Ignored on purpose: bare integers; version numbers (5.2, 5.2.0, 4.2+, v2);
resolutions and dimensions (960x540, 8K); ratios (4:1, 60/30/10); dates and
years; hex colours; URLs; line, section, step and item references ("section
14", "L117-121"); anything inside a fenced code block or a heading.

Two occurrences are the same finding only when the value is identical AND the
words around the number overlap enough to be about the same thing. Words are
weighted by how rare they are across the scanned files, so "fog density"
matches "fog density" but a stray 0.25 next to unrelated words does not. Values
with few significant digits (0.5, 1.0) must overlap more than distinctive ones
(0.012). That trade is deliberate: precision over recall.

Output, worst first (most files, then most occurrences):

  VALUE - file.md:LINE | other.md:LINE

Exit status: 0 clean, 1 an unallowed duplicate, a control character or a dead pointer
was found, 2 usage or allowlist error. Wire it into the swap checklist beside the corpus's snippet runner.

Allowlist file: one entry per line, `#` starts a comment.

  VALUE [@ file1.md,file2.md] | REASON

VALUE is written any way the corpus writes it ("5 to 8", "5-8", "0.50"); it is
normalised the same way. The optional `@` list restricts the exception to those
files, so a third file reusing the value is still reported. A REASON is
required: an exception without one is an error. Identity facts that must appear
twice (an enum range, a default the API fixes) belong here, declared once.

STATUS: TESTED 2026-11-03: moved here from blender/scripts, run with and without --allow
on the blender and art-direction corpora, paragraph joining added. TESTED 2026-11-04:
control scan added, replayed on synthetic files (stray byte, TAB after line start, lone CR,
INTAKE.md all fail; a leading TAB and CRLF pass). TESTED 2026-11-05: pointer scan added,
replayed on synthetic files (missing relative, tilde and cross-skill paths fail; real,
sibling, tilde and fenced paths pass), and run across every skill.
"""
import argparse
import math
import re
import sys
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent.parent                     # the skills directory: holds blender/, art-direction/, maintaining-skills/
DEFAULT_SKILLS = ("blender", "art-direction")
ALLOW_NAME = "check_values.allow"             # discovered at <skill>/scripts/check_values.allow
SKIP_NAMES = {"NOTES-FOR-REVIEW.md", "INTAKE.md", "INTAKE-ARCHIVE.md"}
CONTROL_RE = re.compile(rb"[\x00-\x08\x0b-\x1f]")   # run after CRLF is normalised, so a lone CR is caught
MID_TAB_RE = re.compile(rb"[^\t\n]\t")              # a TAB after line start; leading indent is allowed
POINTER_RE = re.compile(r"`((?:~/\.claude/skills/)?(?:[\w.-]+/)?(?:references|scripts|evals|projects|house)/[\w./-]+\.\w+)`")
POINTER_SKIP = {"anthropic-best-practices.md"}      # upstream guide; its paths are examples, not pointers

WINDOW_WORDS = 9          # words either side of the number that count as its context
MIN_SHARED_WEIGHT = 5.0   # summed rarity weight of shared words needed to call two uses the same claim
LOW_SPECIFICITY_EXTRA = 2.0   # added when the value has a single significant digit (0.5, 1.0, 5 to 8)
MIN_SHARED_WORDS = 2
ENTRY_MIN_WEIGHT = 3.5    # a SKILL.md line is a short summary, so one distinctive shared word is enough

UNITS = {
    "m": "m", "km": "km", "mm": "mm", "cm": "cm", "w": "W", "kw": "kW", "mw": "MW",
    "gb": "GB", "mb": "MB", "px": "px", "ms": "ms", "s": "s", "sec": "s", "seconds": "s",
    "second": "s", "k": "K", "hz": "Hz", "fps": "fps", "stop": "stops", "stops": "stops",
    "degree": "deg", "degrees": "deg", "deg": "deg", "°": "deg", "%": "%", "percent": "%",
    "x": "x", "×": "x",
}
UNIT_RE = r"(?:km|mm|cm|kW|MW|GB|MB|px|ms|Hz|fps|seconds?|sec|stops?|degrees?|deg|°|percent|%|[mWsKx×])"
NUM = r"\d+(?:\.\d+)?"
NUM_COMMA = r"\d{1,3}(?:,\d{3})+(?:\.\d+)?|\d+(?:\.\d+)?"

STOPWORDS = set("""
a about above across after again all also an and any are as at be been being but by can could did do does
each else even every few for from get got had has have how if in into is it its just like may more most much
must no nor not of off on once one only or other our out over own per same should so some such than that the
their them then there these they this those through to too under up us use used using very was we were what
when where which while who why will with within would you your yet
""".split())

# Patterns blanked out (replaced by spaces) before numbers are extracted.
BLANK_PATTERNS = [
    re.compile(r"https?://\S+"),
    re.compile(r"\]\([^)]*\)"),                                   # markdown link target
    re.compile(r"<!--.*?-->"),
    re.compile(r"#[0-9a-fA-F]{3,8}\b"),                           # hex colour
    re.compile(r"\b0x[0-9a-fA-F]+\b"),
    re.compile(r"\b(?:19|20)\d\d-\d\d-\d\d\b"),                    # ISO date
    re.compile(r"\b(?:19|20)\d\d\b"),                              # year
    re.compile(r"\b\d+\.\d+\.\d+(?:\.\d+)*\b"),                    # 5.2.0
    re.compile(r"\b\d+\.x\b"),                                     # 5.x
    re.compile(r"\b[vV]\d+(?:\.\d+)*\b"),                          # v2, v1.2
    re.compile(r"\b\d+(?:\.\d+)?\+(?=[\s)\],;.]|$)"),              # 4.2+  (version gate)
    re.compile(r"\b\d+(?:\s*[x×]\s*\d+)+\b"),                 # 960x540, 1920 x 1080
    re.compile(r"\b\d+[kK]\b"),                                    # 8K, 4K (no space = resolution)
    re.compile(r"\b\d+(?::\d+)+\b"),                               # 4:1, 16:9
    re.compile(r"\b\d+(?:/\d+)+\b"),                               # 60/30/10, 5.0/5.1
    re.compile(r"(?i)\b(?:sections?|steps?|items?|lines?|pages?|pp?|rows?|figures?|fig|facts?|tests?|WO|"
               r"scenes?|stages?|levels?|bands?|rungs?|cases?|slides?|L|F|C|S|n)\s*[-=]?\s*\d+"
               r"(?:\s*(?:to|and|or|,|-|–)\s*\d+)*"),          # "section 14", "L117-121", "F3", "n=3"
    re.compile(r"(?i)\b(?:Blender|EEVEE|Cycles|Python|LTS|ACES|version|release notes?)\s*\d+(?:\.\d+)*"),
]
RANGE_RE = re.compile(
    r"(?<![\w.\-])(?P<a>%s)\s*(?P<sep>to|-|–)\s*(?P<b>%s)(?:\s?(?P<unit>%s)(?![\w]))?" % (NUM, NUM, UNIT_RE))
UNIT_NUM_RE = re.compile(r"(?<![\w.\-])(?P<n>%s)\s?(?P<unit>%s)(?![\w%%])" % (NUM_COMMA, UNIT_RE))
DECIMAL_RE = re.compile(r"(?<![\w.\-/])\d+\.\d+(?![\w.]|\.\d)")
GROUPED_RE = re.compile(r"(?<![\w.\-])\d{1,3}(?:,\d{3})+(?![\w,]|\.\d)")
WORD_RE = re.compile(r"[A-Za-z][A-Za-z_]{2,}")


@dataclass
class Occ:
    key: str
    shown: str
    file: str
    line: int
    words: frozenset
    spec: int = 0                      # number of significant digits in the value
    kind: str = ""
    entry: bool = False                # lives in a SKILL.md (the always-loaded entry file)


@dataclass
class Finding:
    key: str
    occs: list
    shared: set = field(default_factory=set)
    score: float = 0.0


def fmt_num(text):
    """Canonical text for a number: strip commas and trailing zeros ('0.50' -> '0.5', '5.0' -> '5')."""
    text = text.replace(",", "")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def sig_digits(*nums):
    best = 99
    for n in nums:
        digits = re.sub(r"\D", "", n).lstrip("0")
        best = min(best, len(digits.rstrip("0")) or 1)
    return best


def canonical_unit(u):
    return UNITS.get(u.lower(), u)


def make_key(kind, a, b=None, unit=""):
    unit = canonical_unit(unit) if unit else ""
    if kind == "range":
        base = "%s-%s" % (fmt_num(a), fmt_num(b))
    else:
        base = fmt_num(a)
    return ("%s %s" % (base, unit) if unit else base)


def normalise_spec(text):
    """Normalise an allowlist VALUE the way the scanner keys its own finds."""
    t = text.strip()
    m = re.fullmatch(r"(?P<a>%s)\s*(?:to|-|–)\s*(?P<b>%s)\s*(?P<u>%s)?" % (NUM, NUM, UNIT_RE), t)
    if m:
        return make_key("range", m.group("a"), m.group("b"), m.group("u") or "")
    m = re.fullmatch(r"(?P<n>%s)\s*(?P<u>%s)" % (NUM_COMMA, UNIT_RE), t)
    if m:
        return make_key("unit", m.group("n"), unit=m.group("u"))
    m = re.fullmatch(NUM, t)
    if m:
        return fmt_num(t)
    return t


def blank(text, pattern):
    return pattern.sub(lambda m: " " * len(m.group(0)), text)


def clean_line(raw):
    text = raw
    for pat in BLANK_PATTERNS:
        text = blank(text, pat)
    return text


def stem(word):
    w = word.lower()
    return w[:-1] if len(w) > 4 and w.endswith("s") and not w.endswith("ss") else w


def context_words(text, start, end, first_cell=""):
    """Content words near [start, end) on the line, plus a table row's label cell."""
    left = [m for m in WORD_RE.finditer(text[:start])][-WINDOW_WORDS:]
    right = [m for m in WORD_RE.finditer(text[end:])][:WINDOW_WORDS]
    words = set()
    for m in left + right:
        words.add(m.group(0))
    for m in WORD_RE.finditer(first_cell):
        words.add(m.group(0))
    out = set()
    for w in words:
        for part in w.split("_") + ([w] if "_" in w else []):
            p = stem(part)
            if len(p) >= 3 and p not in STOPWORDS:
                out.add(p)
    return frozenset(out)


LIST_START = re.compile(r"^\s*(?:[-*+]|\d+[.)])\s+")


def segments(lines):
    """Split a markdown file into units: (text, line_of_each_char, first_table_cell).

    A hard-wrapped paragraph or list item becomes one unit with its lines joined by a space, so a
    value and its context are not cut by a line break. A table row is its own unit. Front matter,
    fences and headings are dropped."""
    segs, cur, cur_map = [], [], []
    in_fence = in_front = False

    def flush():
        if cur:
            segs.append(("".join(cur), list(cur_map), ""))
            cur.clear()
            cur_map.clear()

    for n, raw in enumerate(lines, 1):
        stripped = raw.lstrip()
        if n == 1 and stripped.rstrip() == "---":
            in_front = True
            continue
        if in_front:
            if stripped.rstrip() == "---":
                in_front = False
            continue
        if stripped.startswith("```") or stripped.startswith("~~~"):
            flush()
            in_fence = not in_fence
            continue
        if in_fence or stripped.startswith("#") or not stripped.strip():
            flush()
            continue
        if stripped.startswith("|"):
            flush()
            cells = stripped.strip("|").split("|")
            segs.append((raw, [n] * len(raw), cells[0] if cells else ""))
            continue
        if LIST_START.match(raw):
            flush()
        piece = raw.strip() + " "
        cur.append(piece)
        cur_map.extend([n] * len(piece))
    flush()
    return segs


def scan_file(path, display):
    """Return (occurrences, per-unit word sets) for every tuned value outside fences, headings and front matter."""
    occs, line_words = [], []
    lines = path.read_text(encoding="utf-8", errors="replace").split("\n")
    for raw, lmap, first_cell in segments(lines):
        text = clean_line(raw)
        words_here = {stem(w) for w in WORD_RE.findall(text) if stem(w) not in STOPWORDS}
        line_words.append(words_here)

        def emit(kind, key, shown, m, specdig):
            occs.append(Occ(key, shown, display, lmap[m.start()], context_words(text, m.start(), m.end(), first_cell),
                            specdig, kind, display.endswith("SKILL.md")))

        work = text
        for m in RANGE_RE.finditer(work):
            a, b = m.group("a"), m.group("b")
            if float(a) >= float(b):
                continue
            unit = m.group("unit") or ""
            if unit in ("%", "percent") and (a, b) == ("0", "100"):
                continue
            emit("range", make_key("range", a, b, unit), m.group(0).strip(), m, sig_digits(a, b))
        work = blank(work, RANGE_RE)
        for m in UNIT_NUM_RE.finditer(work):
            if m.group("unit") in ("%", "percent") and m.group("n") in ("0", "100"):
                continue                         # 0% and 100% are prose, not tuning
            emit("unit", make_key("unit", m.group("n"), unit=m.group("unit")), m.group(0).strip(), m,
                 sig_digits(m.group("n")))
        work = blank(work, UNIT_NUM_RE)
        for m in DECIMAL_RE.finditer(work):
            tok = m.group(0)
            whole, frac = tok.split(".")
            if len(frac) == 1 and 3 <= int(whole) <= 6:
                continue                         # 5.2, 4.5: read as a Blender version, whatever the line says
            if sig_digits(tok) < 2:
                continue                         # 0.5, 1.0, 2.0: too common to mean anything on their own
            emit("decimal", fmt_num(tok), tok, m, sig_digits(tok))
        for m in GROUPED_RE.finditer(work):      # 2,500: a comma-grouped count is never incidental
            emit("grouped", fmt_num(m.group(0)), m.group(0), m, sig_digits(m.group(0)))
    return occs, line_words


def rarity_weights(all_line_words):
    df = Counter()
    for words in all_line_words:
        df.update(words)
    total = max(1, len(all_line_words))
    return {w: math.log(total / c) for w, c in df.items()}


def pair_score(a, b, weight):
    shared = a.words & b.words
    return shared, sum(weight.get(w, 0.0) for w in shared)


def threshold(a, b):
    if a.entry or b.entry:
        return ENTRY_MIN_WEIGHT
    extra = LOW_SPECIFICITY_EXTRA if min(a.spec, b.spec) <= 1 else 0.0
    return MIN_SHARED_WEIGHT + extra


def min_words(a, b):
    return 1 if (a.entry or b.entry) else MIN_SHARED_WORDS


def find_groups(occs, weight, same_file):
    by_key = defaultdict(list)
    for o in occs:
        by_key[o.key].append(o)
    findings = []
    for key, group in by_key.items():
        if len(group) < 2:
            continue
        parent = list(range(len(group)))

        def find(i):
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        best = 0.0
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                a, b = group[i], group[j]
                if (a.file == b.file) != same_file:
                    continue
                if same_file and abs(a.line - b.line) < 3:
                    continue
                shared, score = pair_score(a, b, weight)
                if len(shared) >= min_words(a, b) and score >= threshold(a, b):
                    parent[find(i)] = find(j)
                    best = max(best, score)
        comps = defaultdict(list)
        for i in range(len(group)):
            comps[find(i)].append(group[i])
        for root, members in comps.items():
            if len(members) < 2:
                continue
            files = {m.file for m in members}
            if same_file and len(files) != 1:
                continue
            if not same_file and len(files) < 2:
                continue
            shared = set.intersection(*[set(m.words) for m in members]) or set()
            findings.append(Finding(key, sorted(members, key=lambda o: (o.file, o.line)), shared, best))
    findings.sort(key=lambda f: (-len({o.file for o in f.occs}), -len(f.occs), -f.score, f.key))
    return findings


def die(message):
    print("check_values: " + message, file=sys.stderr)
    sys.exit(2)


def load_allow(path):
    entries = []
    if not path.exists():
        return entries
    for n, raw in enumerate(path.read_text(encoding="utf-8").split("\n"), 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "|" not in line:
            die("%s:%d: allowlist entry has no reason (VALUE [@ files] | REASON)" % (path, n))
        spec, reason = line.split("|", 1)
        if not reason.strip():
            die("%s:%d: allowlist entry has an empty reason" % (path, n))
        files = None
        if "@" in spec:
            spec, flist = spec.split("@", 1)
            files = {f.strip() for f in flist.split(",") if f.strip()}
        entries.append({"key": normalise_spec(spec), "files": files, "reason": reason.strip(),
                        "line": n, "used": False, "src": path.name})
    return entries


def is_allowed(finding, entries):
    names = {Path(o.file).name for o in finding.occs}
    for e in entries:
        if e["key"] != finding.key:
            continue
        if e["files"] is None or names <= e["files"]:
            e["used"] = True
            return e
    return None


def collect(paths):
    files = []
    for p in paths:
        p = Path(p)
        if p.is_dir():
            files += sorted(x for x in p.rglob("*.md") if x.name not in SKIP_NAMES)
        elif p.suffix == ".md":
            files.append(p)
        else:
            die("not a markdown file or directory: %s" % p)
    seen, out = set(), []
    for f in files:
        r = f.resolve()
        if r not in seen:
            seen.add(r)
            out.append(f)
    return out


def default_paths():
    paths = []
    for skill in DEFAULT_SKILLS:
        d = ROOT / skill
        if (d / "SKILL.md").exists():
            paths.append(d / "SKILL.md")
        # projects/ and house/ hold values too (case notes, owner conventions), so a
        # value copied between them and references/ must be seen as a duplicate.
        for sub in ("references", "projects", "house"):
            if (d / sub).is_dir():
                paths.append(d / sub)
    return paths


def discover_allow(files):
    """Per-corpus allowlists: for each scanned file, the scripts/check_values.allow of its skill directory."""
    found, seen = [], set()
    for f in files:
        d = f.resolve().parent
        while d != d.parent:
            if (d / "SKILL.md").exists():
                a = d / "scripts" / ALLOW_NAME
                if a.exists() and a not in seen:
                    seen.add(a)
                    found.append(a)
                break
            d = d.parent
    return found


def control_targets(paths):
    """Every .md the control scan reads: SKIP_NAMES do not apply, and each default skill is read whole."""
    if not paths:
        return [p for skill in DEFAULT_SKILLS for p in sorted((ROOT / skill).rglob("*.md"))]
    out = []
    for p in map(Path, paths):
        out += sorted(p.rglob("*.md")) if p.is_dir() else [p]
    return out


def control_scan(files):
    """Return (file, line, what) for each control byte. Reads bytes, since text mode hides a lone CR."""
    found = []
    for f in files:
        data = f.read_bytes().replace(b"\r\n", b"\n")
        for m in CONTROL_RE.finditer(data):
            found.append((f, data.count(b"\n", 0, m.start()) + 1, "0x%02X" % data[m.start()]))
        for m in MID_TAB_RE.finditer(data):
            found.append((f, data.count(b"\n", 0, m.start()) + 1, "TAB after line start"))
    return found


def skill_dir(path):
    """The directory holding SKILL.md above this file, or None."""
    d = path.resolve().parent
    while d != d.parent:
        if (d / "SKILL.md").exists():
            return d
        d = d.parent
    return None


def pointer_scan(files):
    """Return (file, line, path) for each backticked skill path that exists nowhere. Fenced code is skipped.

    Bare names (`eevee.md`) are left out on purpose: elsewhere they name project or agent files.
    A relative path counts if it exists in the file's own skill, under the skills root, or in a sibling.
    """
    found = []
    siblings = [d for d in ROOT.iterdir() if d.is_dir()]
    for f in files:
        own = skill_dir(f)
        if own is None or f.name in POINTER_SKIP:
            continue
        fenced = False
        for n, line in enumerate(f.read_text(encoding="utf-8", errors="replace").splitlines(), 1):
            if line.lstrip().startswith(("```", "~~~")):
                fenced = not fenced
                continue
            if fenced:
                continue
            for m in POINTER_RE.finditer(line):
                p = m.group(1)
                if p.startswith("~/"):
                    hit = (Path.home() / p[2:]).exists()
                else:
                    hit = any((d / p).exists() for d in (own, ROOT, *siblings))
                if not hit:
                    found.append((f, n, p))
    return found


def label_for(path, roots):
    """A short, unambiguous label: path relative to the common parent of the scan, forward slashes."""
    try:
        return path.resolve().relative_to(roots).as_posix()
    except ValueError:
        return path.as_posix()


def render(findings, explain):
    for f in findings:
        spots = " | ".join(dict.fromkeys("%s:%d" % (o.file, o.line) for o in f.occs))
        print("%s - %s" % (f.key, spots))
        if explain:
            print("    context shared: %s" % (", ".join(sorted(f.shared)) or "(chain of pairwise overlaps)"))
            print("    written as: %s" % "; ".join(sorted({o.shown for o in f.occs})))


def main():
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass
    ap = argparse.ArgumentParser(description="Fail when the same tuned value appears in more than one file.")
    ap.add_argument("paths", nargs="*", help="markdown files or directories (default: blender and art-direction skills)")
    ap.add_argument("--allow", action="append", default=None,
                    help="allowlist file (repeatable); replaces per-corpus discovery of <skill>/scripts/check_values.allow")
    ap.add_argument("--within-file", action="store_true", help="also list repeats inside one file (advisory)")
    ap.add_argument("--explain", action="store_true", help="show shared context words and how each was written")
    ap.add_argument("--list-allowed", action="store_true", help="also list findings the allowlist suppressed")
    a = ap.parse_args()

    files = collect(a.paths or default_paths())
    if not files:
        die("no markdown files to scan")
    parts = [f.resolve().parent.parts for f in files]
    prefix = []
    for group in zip(*parts):
        if len(set(group)) == 1:
            prefix.append(group[0])
        else:
            break
    base = Path(*prefix) if prefix else Path(".")

    all_occs, all_words = [], []
    for f in files:
        occs, words = scan_file(f, label_for(f, base))
        all_occs += occs
        all_words += words
    weight = rarity_weights(all_words)
    allow_files = [Path(x) for x in a.allow] if a.allow else discover_allow(files)
    entries = []
    for af in allow_files:
        entries += load_allow(af)
    allow_names = ", ".join(x.name for x in allow_files) or "no allowlist"

    findings = find_groups(all_occs, weight, same_file=False)
    bad, allowed = [], []
    for f in findings:
        (allowed if is_allowed(f, entries) else bad).append(f)

    print("check_values: %d files, %d tuned values, %d cross-file duplicate(s), %d allowed"
          % (len(files), len(all_occs), len(bad), len(allowed)))
    if bad:
        print()
        render(bad, a.explain)
    if a.list_allowed and allowed:
        print("\nallowed by %s:" % allow_names)
        render(allowed, a.explain)
    for e in entries:
        if not e["used"]:
            print("note: %s line %d (%s) matched nothing; remove it if stale" % (e["src"], e["line"], e["key"]),
                  file=sys.stderr)
    if a.within_file:
        inside = [f for f in find_groups(all_occs, weight, same_file=True) if not is_allowed(f, entries)]
        print("\nadvisory, repeats inside one file (%d, not counted in the exit status):" % len(inside))
        render(inside, a.explain)
    targets = control_targets(a.paths)
    control = control_scan(targets)
    print("control scan: %d files, %d finding(s)" % (len(targets), len(control)))
    for f, line, what in control:
        print("%s:%d %s" % (f, line, what))
    pointers = pointer_scan(files)
    print("pointer scan: %d files, %d finding(s)" % (len(files), len(pointers)))
    for f, line, path in pointers:
        print("%s:%d %s" % (f, line, path))
    if bad:
        print("\nFAIL: fix by keeping one canonical home and deleting the other copy; "
              "if the repeat is legitimate, declare it once in the corpus's scripts/%s with a reason." % ALLOW_NAME)
    if control:
        print("\nFAIL: stray control bytes, usually a non-raw Python string that wrote a Windows path.")
    if pointers:
        print("\nFAIL: a backticked skill path points at nothing.")
    if bad or control or pointers:
        sys.exit(1)
    print("\nOK")


if __name__ == "__main__":
    main()
