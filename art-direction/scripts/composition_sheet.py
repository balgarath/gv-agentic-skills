"""composition_sheet.py - proof contact sheet and composition numbers for any image.

STATUS: TESTED 2026-10-27 - executed on real renders, see "Run record"
at the bottom of this docstring. Verified means it runs and its numbers are
arithmetically sensible; it does not verify the pass thresholds themselves,
which are HEURISTIC.

Purpose
    Takes a rendered or photographed image (any PNG/JPG, renderer-free) and
    writes one contact sheet of seven tiles: original, greyscale, notan
    (4 fixed value levels), squint (blurred), thumbnail (96 px wide),
    flipped, busyness heat map. It also returns and prints the numbers
    that references/composition.md section 15 (Testing a composition)
    scores against.

Inputs
    in.png   path to the proof image. Use an 8-bit, view-transformed render
             (display-referred). A raw linear EXR measured here will mislead.
    out.png  path for the contact sheet.
    width    optional analysis width in pixels, default 1280.

Usage
    python composition_sheet.py in.png out.png [width]
    python composition_sheet.py --help

Requires Pillow and numpy.

Pass values (from composition.md section 15 and the section 18 checklist)
    # notan_area_fractions   one level above 0.5 (dominant_value_ok True);
    #                        darks should also form one connected shape
    #                        (judge that on the notan tile, not from the number)
    # quiet_fraction         roughly 0.3 to 0.4 (HEURISTIC)
    # edge_busy_fraction     share of frame with high edge density (ed > 0.6).
    #                        Edge density is ONE of the three channels that
    #                        make a cluster loud (contrast, saturation, edge
    #                        sharpness; composition.md section 6), so this is
    #                        an upper bound on the loud share, not the loud
    #                        share itself. Above about 0.2 the frame is too
    #                        busy whatever the other channels do; inside the
    #                        0.1 to 0.2 loud target it proves nothing alone.
    #                        Renamed from loud_fraction 2026-11-08 (it never
    #                        measured contrast or saturation).
    # weight_centroid_xy     within about 0.08 of (0.5, 0.5) reads as stable;
    #                        an offset of 0.10 to 0.20 reads as tension
    #                        (HEURISTIC). y is measured from the top here.
    # Tiles:
    #   greyscale   masses and the hero still separate without colour
    #   notan       one level > 50 percent, darks connected, hero on a
    #               light-dark boundary
    #   squint      you can still name the main masses, the front, the hero
    #   thumbnail   3 to 5 clear masses; the hero is the highest-contrast blob
    #   flipped     the frame still balances; nothing slides or points out
    #   busyness    a gradient from loud to quiet with a few large smooth
    #               zones; a flat map means uniform busyness
    # These thresholds are HEURISTIC starting values, not measured standards.

Run record (2026-10-27, Windows, Python 3.12.10, Pillow 12.2.0, numpy 2.4.3)
    python -I composition_sheet.py scenes/01-the-brace/renders/triangle_battle_preview.png sheet.png
      (input 2200x1237 RGBA; exit 0; sheet written, 3x3 grid of 640 px tiles)
      notan_area_fractions: [0.624, 0.348, 0.018, 0.01]
      dominant_value_ok: True
      quiet_fraction: 0.404
      loud_fraction: 0.181   (now printed as edge_busy_fraction)
      weight_centroid_xy: (0.552, 0.561)
    python -I composition_sheet.py triangle_battle_8k.png sheet.png 960
      (input 7680x4320 RGBA; exit 0)
      notan [0.622, 0.349, 0.02, 0.01], quiet 0.411, loud 0.253, centroid (0.56, 0.551)
    2026-11-08: argparse added; --help exits 0, missing arguments exit 2.
    Re-run on a bash kit render, numbers printed, exit 0.
"""
import argparse

import numpy as np
from PIL import Image, ImageFilter, ImageOps


def composition_sheet(path, out_path, W=1280):
    im = Image.open(path).convert("RGB")
    H = round(im.height * W / im.width)
    im = im.resize((W, H), Image.LANCZOS)
    grey = im.convert("L")
    L = np.asarray(grey, np.float32) / 255.0
    Ln = np.clip(L / max(np.percentile(L, 99.5), 1e-4), 0, 1)

    bins = np.digitize(Ln, [0.12, 0.35, 0.65])             # 4 fixed levels
    frac = np.bincount(bins.ravel(), minlength=4) / bins.size
    notan = Image.fromarray(np.array([10, 90, 170, 250], np.uint8)[bins])

    squint = grey.filter(ImageFilter.GaussianBlur(W * 0.015))
    thumb = im.resize((96, max(1, round(96 * H / W))), Image.LANCZOS)
    flipped = ImageOps.mirror(im)

    edges = grey.filter(ImageFilter.FIND_EDGES).filter(ImageFilter.BoxBlur(int(W * 0.03)))
    ed = np.asarray(edges, np.float32)
    ed = np.clip(ed / max(np.percentile(ed, 99), 1e-4), 0, 1)
    heat = Image.fromarray((ed * 255).astype(np.uint8))

    wgt = Ln * (0.25 + ed)                                   # proxy for visual weight
    ys, xs = np.mgrid[0:H, 0:W]
    cx = float((wgt * xs).sum() / wgt.sum() / W)
    cy = float((wgt * ys).sum() / wgt.sum() / H)

    tiles = [im, grey, notan, squint, thumb, flipped, heat]
    tw = 640
    th = round(H * tw / W)
    sheet = Image.new("RGB", (tw * 3, th * 3), (20, 20, 20))
    for i, t in enumerate(tiles):
        resample = Image.NEAREST if t is thumb else Image.LANCZOS
        sheet.paste(t.convert("RGB").resize((tw, th), resample), ((i % 3) * tw, (i // 3) * th))
    sheet.save(out_path)
    return {
        "notan_area_fractions": [round(float(f), 3) for f in frac],   # want one level > 0.5
        "dominant_value_ok": bool(frac.max() > 0.5),
        "quiet_fraction": round(float((ed < 0.25).mean()), 3),        # want roughly 0.3 to 0.4
        "edge_busy_fraction": round(float((ed > 0.6).mean()), 3),     # upper bound on the loud share
        "weight_centroid_xy": (round(cx, 3), round(cy, 3)),            # y is from the top here
    }


if __name__ == "__main__":
    ap = argparse.ArgumentParser(
        description="Proof contact sheet (original, greyscale, notan, squint, thumbnail, "
                    "flipped, busyness) and composition numbers for one image.")
    ap.add_argument("image", help="8-bit, view-transformed proof render (PNG/JPG)")
    ap.add_argument("out", help="output contact sheet PNG")
    ap.add_argument("width", nargs="?", type=int, default=1280,
                    help="analysis width in px (default 1280)")
    a = ap.parse_args()
    for key, value in composition_sheet(a.image, a.out, a.width).items():
        print(f"{key}: {value}")
