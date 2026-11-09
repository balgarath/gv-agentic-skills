"""Pure-Python camera projection: where does a world point land in frame, with no bpy.

Taken 2026-11-08 from the triangle-battle project (OBSERVED(triangle-battle)),
unchanged apart from this header and the import name in Typical use. The camera it models is the one
`(aim - loc).to_track_quat('-Z', 'Y')` builds, which is the aiming idiom in SKILL.md and api.md.
TESTED 2026-11-08 on Blender 5.2.0 LTS by a check run inside Blender, no
render (the check is not included here): over 15 camera cases, max deviation from world_to_camera_view 3.11e-05 on frame and 9.6e-07 beyond
100 m; the only large deviations are the to_track_quat roll band near vertical (api.md, Camera aiming).
`scripts/check_snippets.py` runs one host-side projection of it. Plain `python -I project_nobpy.py --help`.

Original docstring follows.

Pure-Python camera projection that matches the aiming idiom below exactly.

Answers "where does this world point land in frame?" in microseconds, before
any geometry exists. No bpy, no numpy: stdlib only, runs under plain `python`.
Verified against Blender's world_to_camera_view by a check run inside Blender
(not included; re-run an equivalent if Blender or your camera helper changes).

Conventions (all inherited from Blender, none of them negotiable):
  - World is Z-up, units are meters.
  - Frame coords (u, v) are 0..1 from the BOTTOM-LEFT of the frame, so v=0.776
    is high in the picture. Off-frame is anything outside 0..1.
  - depth is metres along the view axis (not slant range). depth <= 0 means the
    point is behind the camera; its (u, v) are mirrored garbage, so project()
    returns nan for them unless raw=True.
  - Aim is a world point. The camera helper orients with
        (aim - loc).to_track_quat('-Z', 'Y')
    i.e. the camera looks down its local -Z, local +Y is "up", and up is
    resolved toward world +Z. That makes camera-right = Z_world x back-axis,
    zero roll, horizon always level. Straight up/down has no unique answer;
    Blender falls back to local up = world +Y whenever |dx|+|dy| < 1e-4 of the
    (unnormalized) aim vector, and so do we. Note this is discontinuous:
    exactly-down gives top-of-frame = +Y, but a hair off vertical flips to
    whichever way the tilt points. Also: Blender's float32 solve loses the
    roll entirely for aims within ~3e-4 rad of vertical but past that cutoff
    (e.g. 0.04 m off over 400 m): its camera ends up rolled by an arbitrary
    angle. We return the mathematically right roll, which Blender will not
    reproduce there. Aim exactly vertical, or tilt by a degree or more.
  - Sensor fit is AUTO with sensor_width = 36 by default: the sensor value
    spans the LARGER image dimension, so landscape frames use it horizontally
    and portrait frames vertically. Pixels are square.

Typical use:
    from project_nobpy import Camera, check, report
    cam = Camera((-140, -420, 185), (20, 900, -30), lens=35)
    report(check(cam, [("pentagon", (-120, 420, 0), (0.408, 0.401))]))
"""
import argparse
import json
import math
import re
from dataclasses import dataclass, field

# Blender's own cutoff in vec_to_quat, compared against the raw (unnormalized) aim vector.
_DEGENERATE_EPS = 1e-4


def _sub(a, b): return (a[0] - b[0], a[1] - b[1], a[2] - b[2])
def _dot(a, b): return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]
def _len(a): return math.sqrt(_dot(a, a))


def _cross(a, b):
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _unit(a):
    n = _len(a)
    return (a[0] / n, a[1] / n, a[2] / n)


def track_basis(direction):
    """Camera (right, up, back) world axes for to_track_quat('-Z', 'Y').

    Derivation: -Z must point along `direction`, so back = -dir. Local Y should
    lean toward world Z as far as the -Z constraint allows, which pins local X
    to the horizontal: right = Z x back. Then up = back x right completes a
    right-handed frame. When dir is vertical Z x back vanishes; Blender then
    takes up = world +Y (checked empirically for both straight up and down).
    """
    if _len(direction) == 0.0:
        raise ValueError("camera location and aim coincide")
    back = _unit((-direction[0], -direction[1], -direction[2]))
    if abs(direction[0]) + abs(direction[1]) < _DEGENERATE_EPS:
        up = (0.0, 1.0, 0.0)
        right = _cross(up, back)
        return right, up, back
    right = _unit(_cross((0.0, 0.0, 1.0), back))
    up = _cross(back, right)
    return right, up, back


class Camera:
    """Matches the author's camera helper's conventions."""

    def __init__(self, location, aim, lens=35.0, sensor=36.0, res_x=1920, res_y=1080):
        self.location = tuple(float(c) for c in location)
        self.aim = tuple(float(c) for c in aim)
        self.lens = float(lens)
        self.sensor = float(sensor)
        self.res_x = int(res_x)
        self.res_y = int(res_y)
        self.forward = _unit(_sub(self.aim, self.location))
        self.right, self.up, self._back = track_basis(_sub(self.aim, self.location))
        # AUTO fit: sensor width covers the larger pixel dimension.
        if self.res_x >= self.res_y:
            self.sensor_x = self.sensor
            self.sensor_y = self.sensor * self.res_y / self.res_x
        else:
            self.sensor_y = self.sensor
            self.sensor_x = self.sensor * self.res_x / self.res_y

    def project(self, point, raw=False):
        """(u, v, depth). u, v are 0..1 from bottom-left, depth in metres along view axis.

        Behind the camera (depth <= 0) u and v come back nan so a wrapped
        coordinate can't pass for a real one; raw=True returns Blender's
        mirrored values, which only the verifier wants.
        """
        d = _sub(point, self.location)
        depth = _dot(d, self.forward)
        if depth <= 0.0 and not raw:
            return (math.nan, math.nan, depth)
        if depth == 0.0:
            return (0.5, 0.5, 0.0)      # Blender's own answer for the exact-zero case
        u = 0.5 + _dot(d, self.right) / depth * self.lens / self.sensor_x
        v = 0.5 + _dot(d, self.up) / depth * self.lens / self.sensor_y
        return (u, v, depth)

    def project_px(self, point):
        """(x_px, y_px, depth) with the origin at the bottom-left pixel corner."""
        u, v, depth = self.project(point)
        return (u * self.res_x, v * self.res_y, depth)

    def apparent_px(self, point, world_size, along="screen"):
        """Pixels a world_size-metre object at `point` spans vertically.

        The scale-chain question: is a 3 m figure 22 px or 53 px here?
        along="screen" (default) is pinhole scale for an object perpendicular
        to the view axis, which is what scale chains quote. along="world_z"
        measures a truly vertical segment standing on `point`; the two differ
        by perspective foreshortening when the camera is steeply pitched.
        """
        _, _, depth = self.project(point, raw=True)
        if depth <= 0.0:
            return math.nan
        if along == "screen":
            return world_size * self.lens / self.sensor_y / depth * self.res_y
        top = (point[0], point[1], point[2] + world_size)
        _, y0, d0 = self.project_px(point)
        _, y1, d1 = self.project_px(top)
        if d1 <= 0.0:
            return math.nan
        return abs(y1 - y0)

    def horizon_v(self):
        """v of the flat horizon (the vanishing line of the ground plane).

        Roll is always zero here, so it is a horizontal line at
        0.5 - (lens / sensor_y) * tan(pitch). A ground point at finite range
        sits slightly below this; at 99 km from 185 m up the gap is ~0.003 v.
        """
        horiz = math.hypot(self.forward[0], self.forward[1])
        if horiz < 1e-12:
            return math.nan     # looking straight along the vertical, no horizon in frame
        pitch = math.atan2(self.forward[2], horiz)
        return 0.5 - math.tan(pitch) * self.lens / self.sensor_y

    @property
    def fov_h(self):
        return math.degrees(2.0 * math.atan(self.sensor_x / (2.0 * self.lens)))

    @property
    def fov_v(self):
        return math.degrees(2.0 * math.atan(self.sensor_y / (2.0 * self.lens)))

    def __repr__(self):
        return ("Camera(loc=%s, aim=%s, lens=%g, %dx%d, fov %.1fx%.1f deg, horizon v=%s)"
                % (self.location, self.aim, self.lens, self.res_x, self.res_y,
                   self.fov_h, self.fov_v, _fmt_v(self.horizon_v())))


def _fmt_v(x):
    return "n/a" if x != x else "%.3f" % x


@dataclass
class Result:
    name: str
    point: tuple
    u: float
    v: float
    depth: float
    behind: bool
    on_frame: bool
    expected: tuple = None
    du: float = None
    dv: float = None
    dev: float = None           # max(|du|, |dv|)
    passed: bool = None         # None when nothing was expected
    extra: dict = field(default_factory=dict)


def check(camera, points, tol=0.02):
    """Project (name, (x, y, z), expected_uv_or_None) tuples; return Result list.

    A point behind the camera is never on frame and fails any expectation.
    """
    out = []
    for name, p, exp in points:
        u, v, depth = camera.project(p)
        behind = depth <= 0.0
        on = (not behind) and 0.0 <= u <= 1.0 and 0.0 <= v <= 1.0
        r = Result(name, tuple(p), u, v, depth, behind, on)
        if exp is not None:
            r.expected = (float(exp[0]), float(exp[1]))
            if behind:
                r.passed = False
            else:
                r.du, r.dv = u - r.expected[0], v - r.expected[1]
                r.dev = max(abs(r.du), abs(r.dv))
                r.passed = r.dev <= tol
        out.append(r)
    return out


def report(results, file=None):
    """Print an aligned table; FAIL and OFF-FRAME/BEHIND are flagged at line end."""
    w = max([len(r.name) for r in results] + [6])
    hdr = "%-*s  %7s %7s  %8s  %-15s  %7s %7s  %s" % (
        w, "anchor", "u", "v", "depth", "expected", "du", "dv", "status")
    print(hdr, file=file)
    print("-" * len(hdr), file=file)
    for r in results:
        exp = "(%.3f,%.3f)" % r.expected if r.expected else "-"
        du = "%+.3f" % r.du if r.du is not None else "-"
        dv = "%+.3f" % r.dv if r.dv is not None else "-"
        if r.behind:
            uv = "%7s %7s" % ("-", "-")
        else:
            uv = "%7.3f %7.3f" % (r.u, r.v)
        flags = []
        if r.passed is True: flags.append("PASS")
        elif r.passed is False: flags.append("FAIL")
        if r.behind: flags.append("BEHIND")
        elif not r.on_frame: flags.append("OFF-FRAME")
        print("%-*s  %s  %8.1f  %-15s  %7s %7s  %s"
              % (w, r.name, uv, r.depth, exp, du, dv, " ".join(flags)), file=file)
    scored = [r for r in results if r.passed is not None]
    if scored:
        bad = sum(1 for r in scored if not r.passed)
        print("%d checked, %d FAIL, worst dev %.3f" % (
            len(scored), bad, max((r.dev for r in scored if r.dev is not None), default=math.nan)),
            file=file)


def _parse_point(s):
    """'name=x,y,z' or 'name=x,y,z@u,v' (the @ part is the expected frame coord)."""
    m = re.match(r"^\s*([^=]+)=\s*([-\d.e+]+)\s*,\s*([-\d.e+]+)\s*,\s*([-\d.e+]+)"
                 r"(?:\s*@\s*([-\d.e+]+)\s*,\s*([-\d.e+]+))?\s*$", s)
    if not m:
        raise argparse.ArgumentTypeError("bad point %r, want name=x,y,z[@u,v]" % s)
    g = m.groups()
    exp = (float(g[4]), float(g[5])) if g[4] is not None else None
    return (g[0].strip(), (float(g[1]), float(g[2]), float(g[3])), exp)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Project world points through a camera aimed with to_track_quat.")
    ap.add_argument("--loc", nargs=3, type=float, required=True, metavar=("X", "Y", "Z"))
    ap.add_argument("--aim", nargs=3, type=float, required=True, metavar=("X", "Y", "Z"))
    ap.add_argument("--lens", type=float, default=35.0)
    ap.add_argument("--sensor", type=float, default=36.0)
    ap.add_argument("--res", nargs=2, type=int, default=(1920, 1080), metavar=("W", "H"))
    ap.add_argument("--tol", type=float, default=0.02)
    ap.add_argument("--point", action="append", type=_parse_point, default=[],
                    help="name=x,y,z or name=x,y,z@u,v (repeatable)")
    ap.add_argument("--json", metavar="FILE",
                    help='JSON list of {"name", "xyz", "uv"?} entries, added to --point')
    a = ap.parse_args(argv)
    cam = Camera(a.loc, a.aim, a.lens, a.sensor, a.res[0], a.res[1])
    pts = list(a.point)
    if a.json:
        with open(a.json) as f:
            pts += [(e["name"], tuple(e["xyz"]), e.get("uv")) for e in json.load(f)]
    print(cam)
    if pts:
        report(check(cam, pts, a.tol))


if __name__ == "__main__":
    main()
