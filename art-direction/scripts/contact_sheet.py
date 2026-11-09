"""contact_sheet.py - numbered, labelled review grid from a folder or a list of images.

STATUS: TESTED 2026-11-08, Windows, Python 3.12, Pillow 12 (run record at the bottom).

Purpose
    A review sheet the client can answer by number: every cell carries a
    number and a label, the numbering is stable (sorted by name, or the order
    given), and missing or unreadable files show as an empty labelled cell
    instead of shifting the numbers. Replaces seven hand-written copies in one
    project (make_sheet*.py and a round's contact_sheet.py). This is the
    review sheet; composition_sheet.py is the composition test battery for one
    image. Plain Python + Pillow, no renderer.

Usage
    python contact_sheet.py FOLDER -o sheet.png
    python contact_sheet.py a.png b.png c.png -o sheet.png
    python contact_sheet.py FOLDER -o sheet.png --pattern "cam_*.png" --cols 5 \
        --cell 480 --title "Round 18 cameras" --labels labels.json

Options (see --help)
    --pattern GLOB   which files to take from a folder (default *.png)
    --cols N         columns (default: about square)
    --cell PX        cell width; height follows the first image's aspect
    --labels FILE    JSON {filename_or_stem: label}; a value may also be
                     {"name": ..., "sub": ...} for a second line
    --number-from N  first number (default 1)
    --numbers-from-names  use the last number in the file name as
                     its number (r18_cam_07.png -> 07), so numbers survive gaps
    --title TEXT     header line
    --bg R,G,B  --fg R,G,B  --accent R,G,B   colours

Exit 0 on success, 2 on bad arguments or no images found.

Run record
    2026-11-08: --help exit 0. Folder run on
    a local folder of renders with --pattern "cam_*.png"
    --numbers-from-names --cols 5 --cell 320, and a file-list run with a
    missing path and a labels JSON; outputs written to the session scratchpad,
    viewed, numbers and labels correct, missing cell shown as "missing".
"""
import argparse
import glob
import json
import math
import os
import re
import sys

from PIL import Image, ImageDraw, ImageFont

FONT_CANDIDATES = [
    "C:/Windows/Fonts/bahnschrift.ttf",
    "C:/Windows/Fonts/segoeui.ttf",
    "C:/Windows/Fonts/arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
]


def font(size):
    for f in FONT_CANDIDATES:
        if os.path.exists(f):
            try:
                return ImageFont.truetype(f, size)
            except OSError:
                pass
    try:
        return ImageFont.load_default(size=size)
    except TypeError:  # Pillow < 10.1
        return ImageFont.load_default()


def rgb(s):
    parts = [int(p) for p in s.split(",")]
    if len(parts) != 3 or not all(0 <= p <= 255 for p in parts):
        raise argparse.ArgumentTypeError("colour must be R,G,B with 0-255 each")
    return tuple(parts)


def collect(inputs, pattern):
    files = []
    for p in inputs:
        if os.path.isdir(p):
            files += sorted(glob.glob(os.path.join(p, pattern)))
        else:
            files.append(p)  # kept even if missing, so numbering does not shift
    return files


def load_labels(path):
    if not path:
        return {}
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def label_for(path, labels):
    base = os.path.basename(path)
    stem = os.path.splitext(base)[0]
    v = labels.get(base, labels.get(stem, stem))
    if isinstance(v, dict):
        return str(v.get("name", stem)), str(v.get("sub", ""))
    return str(v), ""


def number_from_name(path, fallback):
    runs = re.findall(r"\d+", os.path.splitext(os.path.basename(path))[0])
    return runs[-1] if runs else str(fallback)


def build(files, out, cols=None, cell=480, labels=None, number_from=1,
          numbers_from_names=False, title=None, bg=(12, 12, 16),
          fg=(236, 236, 240), accent=(250, 200, 80)):
    labels = labels or {}
    n = len(files)
    cols = cols or max(1, math.ceil(math.sqrt(n)))
    rows = math.ceil(n / cols)
    aspect = None
    for f in files:
        try:
            with Image.open(f) as im:
                aspect = im.height / im.width
            break
        except (OSError, ValueError):
            continue
    if aspect is None:
        print("contact_sheet: none of the inputs could be opened", file=sys.stderr)
        sys.exit(2)
    cw, ch = cell, max(1, round(cell * aspect))
    pad, gut = max(8, cell // 30), max(6, cell // 40)
    f_num, f_name, f_sub = font(max(14, cell // 10)), font(max(11, cell // 22)), font(max(10, cell // 28))
    cap = f_name.size + f_sub.size + 10
    head = (f_name.size * 2 + pad) if title else 0
    W = pad * 2 + cols * cw + (cols - 1) * gut
    H = pad * 2 + head + rows * (ch + cap) + (rows - 1) * gut
    sheet = Image.new("RGB", (W, H), bg)
    d = ImageDraw.Draw(sheet)
    if title:
        d.text((pad, pad), title, font=font(f_name.size * 2 - 4), fill=fg)
    dim = tuple((a + b) // 2 for a, b in zip(fg, bg))
    for i, f in enumerate(files):
        x = pad + (i % cols) * (cw + gut)
        y = pad + head + (i // cols) * (ch + cap + gut)
        num = number_from_name(f, i + number_from) if numbers_from_names else str(i + number_from)
        name, sub = label_for(f, labels)
        try:
            with Image.open(f) as im:
                im = im.convert("RGB")
                im.thumbnail((cw, ch), Image.LANCZOS)
                sheet.paste(im, (x + (cw - im.width) // 2, y + (ch - im.height) // 2))
        except (OSError, ValueError):
            d.rectangle((x, y, x + cw - 1, y + ch - 1), outline=dim)
            sub = (sub + "  " if sub else "") + "missing"
        d.text((x + 6, y + 4), num, font=f_num, fill=accent, stroke_width=3, stroke_fill=bg)
        d.text((x, y + ch + 4), name, font=f_name, fill=fg)
        if sub:
            d.text((x, y + ch + 6 + f_name.size), sub, font=f_sub, fill=dim)
    sheet.save(out)
    return sheet.size, n


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="Numbered, labelled contact sheet from a folder or a list of images.")
    ap.add_argument("inputs", nargs="+", help="image files and/or folders")
    ap.add_argument("-o", "--out", required=True, help="output PNG path")
    ap.add_argument("--pattern", default="*.png", help="glob inside folders (default *.png)")
    ap.add_argument("--cols", type=int, default=None, help="columns (default about square)")
    ap.add_argument("--cell", type=int, default=480, help="cell width in px (default 480)")
    ap.add_argument("--labels", help="JSON {filename_or_stem: label or {name, sub}}")
    ap.add_argument("--number-from", type=int, default=1, help="first number (default 1)")
    ap.add_argument("--numbers-from-names", action="store_true",
                    help="number each cell by the last run of digits in its file name (fallback: position)")
    ap.add_argument("--title", help="header line")
    ap.add_argument("--bg", type=rgb, default=(12, 12, 16))
    ap.add_argument("--fg", type=rgb, default=(236, 236, 240))
    ap.add_argument("--accent", type=rgb, default=(250, 200, 80), help="number colour")
    a = ap.parse_args(argv)
    files = collect(a.inputs, a.pattern)
    if not files:
        ap.error("no images found")
    size, n = build(files, a.out, a.cols, a.cell, load_labels(a.labels), a.number_from,
                    a.numbers_from_names, a.title, a.bg, a.fg, a.accent)
    print(f"{a.out} {size[0]}x{size[1]} {n} cells")
    return 0


if __name__ == "__main__":
    sys.exit(main())
