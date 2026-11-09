"""Verify framing by arithmetic: project world anchors to the frame and flag drift.

STATUS: TESTED 2026-11-03 on Blender 5.2.0 LTS (check_occlusion: TESTED 2026-11-08, see below)
(`-b --factory-startup --python-exit-code 1 --python frame_check.py`): the
round trip hit the ground at 3 of 3 points within 1e-3, the four demo anchors
flagged ok, CHECK, OFF FRAME and BEHIND CAMERA as asserted, strict mode passed a
clean table silently, raised FrameCheckError naming the three bad rows on the demo
table, and `-- --strict` exited 1 under `--python-exit-code 1`. The runner
`check_snippets.py` re-runs both demos. Not cross-checked against the original author's projection
code numerically; only the self-consistency check above ran.

Purpose: an anchor table maps world points to their intended frame coordinates
(nx, ny in 0..1, y up). check_anchors() prints the actual projection and flags
BEHIND CAMERA, OFF FRAME, CHECK (error above tol) or ok. Run it on every build:
a changed camera height or lens silently moves every anchor. Include the tops
and bases of the scale-chain rungs; a rung off frame or on top of the next is
the quickest way to lose the chain.

Two modes. Printing (default) is the design-time mode: you read the table. Strict
(`strict=True`) is for a numeric acceptance criterion: any row that is not ok
raises FrameCheckError naming the rows, so the build fails under
`--python-exit-code 1` instead of exiting 0 with every row wrong.

Occlusion (check_occlusion, added 2026-11-08): check_anchors proves an anchor
lands where the table says; it says nothing about whether anything stands in
front of it. check_occlusion ray-casts from the camera to each anchor through the
evaluated scene and reports one of four flags, naming the first object hit and
how far in front of the anchor it is:
  ok      nothing hit, or the hit is within `tol` metres of the anchor (an anchor ON
          a surface hits that surface at its own distance; the margin is printed so
          grazing anchors are visible).
  INSIDE  the anchor lies inside the first-hit object (behind its nearest surface,
          by Object.closest_point_on_mesh and that face's normal). It probably marks
          that object (a barge centre, a crowd centre), so the hit is its own
          surface; not a failure, but look at it once by eye. The test uses the
          world matrix ray_cast returns, so it holds for instances too. (A bounding-box
          test was rejected: a terrain's box swallows a real terrain occlusion.)
  UNRESOLVED  the blocker is an instance (collection instance, Geometry Nodes scatter:
          ray_cast's matrix differs from the object's own, or the object is not in the
          scene) and the anchor is not inside it. Something instanced stands in front;
          whether it is the anchor's own object cannot be told from here. Look by eye.
  HIDDEN  the anchor is outside a non-instanced blocker: something stands in front of it.
          An instance placed exactly at its source's transform, with the source in the
          scene, cannot be told from its source and reads HIDDEN (a false fail, not a pass).
Limits: an anchor at a corner or apex of its own object, or a spec point a little off
the built mesh, can read HIDDEN by that same object; a gap under about 0.1 percent of
the distance is the tell (OBSERVED(triangle-battle)). Check those
by eye. Objects in a collection whose render is disabled, and view-layer holdout or
indirect-only collections, are still hit by ray_cast, so they over-flag; pass them in
`ignore`. A collection excluded from the view layer is not in the depsgraph and is
never hit.
`ignore` names objects to see through (haze boxes). Objects with hide_render set or
visible_camera off are skipped, since the camera cannot see them. scene.ray_cast sees
what the depsgraph holds, so an object hidden in the viewport is not hit at all. One
ray per anchor plus one per skipped hit, so a few dozen anchors cost well under a
second (OBSERVED(triangle-battle)). TESTED 2026-11-08, 5.2.0, on the demo
below and one project scene.

Assumptions: zero lens shift and horizontal sensor fit (ray_from_ndc).
round_trip_check() must pass before you trust the inverse helpers.

The pure-Python projection in project_nobpy.py was verified to 1e-6 against
Blender; this script is the generic skill copy.

Run the demo, which also runs the occlusion demo (add `-- --strict` to see the failing strict run exit 1):
  blender.exe -b --factory-startup --python-exit-code 1 --python frame_check.py
"""
import math
import sys

import bpy
from mathutils import Vector
from bpy_extras.object_utils import world_to_camera_view


class FrameCheckError(RuntimeError):
    """Raised by check_anchors(strict=True) when any anchor is not ok."""


def to_ndc(scene, cam, world_pos):
    v = world_to_camera_view(scene, cam, Vector(world_pos))
    return v.x, v.y, v.z


def ray_from_ndc(scene, cam, nx, ny):
    """Return (origin, direction) in world space for a screen point."""
    cd, r = cam.data, scene.render
    half_w = math.tan(cd.angle_x * 0.5)
    half_h = half_w * r.resolution_y / r.resolution_x
    local = Vector(((nx * 2 - 1) * half_w, (ny * 2 - 1) * half_h, -1.0))
    origin = cam.matrix_world.translation.copy()
    direction = (cam.matrix_world.to_3x3() @ local).normalized()
    return origin, direction


def ground_hit(scene, cam, nx, ny, ground_z=0.0):
    o, d = ray_from_ndc(scene, cam, nx, ny)
    if d.z >= -1e-6:
        return None                      # at or above the horizon
    return o + d * ((ground_z - o.z) / d.z)


def round_trip_check(scene, cam, points=((0.62, 0.40), (0.20, 0.10), (0.90, 0.30)), tol=1e-3):
    """Project ground hits back to the frame; assert they land where they were cast from."""
    bpy.context.view_layer.update()
    hits = 0
    for nx, ny in points:
        p = ground_hit(scene, cam, nx, ny)
        if p is None:
            continue                     # above the horizon for this camera
        gx, gy, _ = to_ndc(scene, cam, p)
        assert abs(gx - nx) < tol and abs(gy - ny) < tol, \
            "round trip failed at (%.2f, %.2f): got (%.5f, %.5f)" % (nx, ny, gx, gy)
        hits += 1
    assert hits, "no test point hit the ground; aim the camera lower"
    return hits


def check_anchors(scene, cam, anchors, tol=0.01, strict=False):
    """anchors: {name: (world_pos, (nx, ny))}. Prints the table, returns the rows.

    strict=True raises FrameCheckError naming every row that is CHECK, OFF FRAME or BEHIND CAMERA."""
    bpy.context.view_layer.update()
    rows = []
    for name, (pos, want) in anchors.items():
        nx, ny, depth = to_ndc(scene, cam, pos)
        err = max(abs(nx - want[0]), abs(ny - want[1]))
        if depth <= 0:
            flag = "BEHIND CAMERA"
        elif not (0 <= nx <= 1 and 0 <= ny <= 1):
            flag = "OFF FRAME"
        else:
            flag = "ok" if err < tol else "CHECK"
        rows.append((name, (nx, ny), depth, err, flag))
        print(f"{name:10s} want ({want[0]:.3f}, {want[1]:.3f})  got ({nx:.3f}, {ny:.3f})  "
              f"depth {depth:7.1f} m  err {err:.4f}  {flag}")
    bad = [r for r in rows if r[4] != "ok"]
    if strict and bad:
        msg = "### FRAME_CHECK FAIL: " + ", ".join("%s=%s" % (r[0], r[4]) for r in bad)
        print(msg)
        raise FrameCheckError(msg)
    return rows


def _inside(ob, mat, pos, dg):
    """True if world point pos is behind the nearest surface of mesh object ob placed at mat."""
    if ob is None or ob.type != 'MESH':
        return False
    local = mat.inverted() @ pos
    ok, loc, nrm, _i = ob.evaluated_get(dg).closest_point_on_mesh(local)
    return bool(ok) and (local - loc).dot(nrm) < 0.0


def _is_instance(scene, ob, mat):
    """True when ray_cast hit an instance rather than the object itself."""
    if ob is None or scene.objects.get(ob.name) != ob:
        return True
    a, b = mat, ob.matrix_world
    return any(abs(a[i][j] - b[i][j]) > 1e-5 for i in range(4) for j in range(4))


def check_occlusion(scene, cam, anchors, tol=0.05, ignore=(), strict=False):
    """anchors: {name: world_pos} or the check_anchors table {name: (world_pos, (nx, ny))}.

    Prints one row per anchor and returns [(name, flag, blocker, gap_m)]. flag is ok,
    INSIDE, UNRESOLVED or HIDDEN (module docstring); gap_m is how far in front of the
    anchor the first hit is (None when nothing is hit). strict=True raises
    FrameCheckError naming every HIDDEN row; INSIDE and UNRESOLVED rows do not fail it."""
    bpy.context.view_layer.update()
    dg = bpy.context.evaluated_depsgraph_get()
    origin = cam.matrix_world.translation.copy()
    skip = set(ignore)
    rows = []
    for name, val in anchors.items():
        pos = Vector(val[0] if isinstance(val[0], (tuple, list, Vector)) else val)
        seg = pos - origin
        dist = seg.length
        d = seg.normalized()
        start, travelled, blocker, gap, hit_ob, hit_mat = origin.copy(), 0.0, None, None, None, None
        while travelled < dist:
            hit, loc, _n, _i, ob, mat = scene.ray_cast(dg, start, d, distance=dist - travelled)
            if not hit:
                break
            t_hit = travelled + (loc - start).length
            if ob is not None and (ob.name in skip or ob.hide_render or not ob.visible_camera):
                travelled = t_hit + 1e-4
                start = origin + d * travelled
                continue
            blocker, gap, hit_ob, hit_mat = (ob.name if ob else "?"), dist - t_hit, ob, mat.copy()
            break
        if blocker is None or gap <= tol:
            flag = "ok"
        elif _inside(hit_ob, hit_mat, pos, dg):
            flag = "INSIDE"
        elif _is_instance(scene, hit_ob, hit_mat):
            flag = "UNRESOLVED"
        else:
            flag = "HIDDEN"
        rows.append((name, flag, blocker, gap))
        extra = "" if blocker is None else f"  first hit {blocker} {gap:.3f} m before it"
        print(f"{name:10s} dist {dist:8.2f} m  {flag}{extra}")
    bad = [r for r in rows if r[1] == "HIDDEN"]
    if strict and bad:
        msg = "### OCCLUSION FAIL: " + ", ".join("%s=HIDDEN by %s" % (r[0], r[2]) for r in bad)
        print(msg)
        raise FrameCheckError(msg)
    return rows


def _occlusion_demo(sc, cam):
    """A ground plane, a wall between the camera and one anchor, a haze box to see through."""
    import bmesh

    def box(name, centre, size):
        me = bpy.data.meshes.new(name)
        bm = bmesh.new()
        bmesh.ops.create_cube(bm, size=1.0)
        bmesh.ops.scale(bm, vec=size, verts=bm.verts)
        bmesh.ops.translate(bm, vec=centre, verts=bm.verts)
        bm.to_mesh(me)
        bm.free()
        ob = bpy.data.objects.new(name, me)
        sc.collection.objects.link(ob)
        return ob

    box("ground", (0, 30, -0.5), (200, 200, 1))          # top face at z 0
    box("wall", (0, 0, 2), (20, 1, 4))                   # 4 m wall at y 0, in front of "blocked"
    box("haze", (20, 30, 5), (10, 10, 10))               # a volume box around "in_haze"
    box("barge", (-20, 30, 8), (6, 6, 2))                 # "barge_centre" marks this object
    ghost = box("ghost", (-12, 0, 6), (8, 1, 12))         # on the ray to "past_ghost", render-hidden
    ghost.hide_render = True
    # a collection instance on the ray to "past_inst": its object is not in the scene
    src = bpy.data.collections.new("inst_src")
    me = bpy.data.meshes.new("inst_box")
    bm = bmesh.new()
    bmesh.ops.create_cube(bm, size=1.0)
    bmesh.ops.scale(bm, vec=(8, 1, 12), verts=bm.verts)
    bmesh.ops.translate(bm, vec=(0, 0, 6), verts=bm.verts)
    bm.to_mesh(me)
    bm.free()
    src.objects.link(bpy.data.objects.new("inst_box", me))
    inst = bpy.data.objects.new("inst", None)
    inst.instance_type = 'COLLECTION'
    inst.instance_collection = src
    inst.location = (21, 0, 0)
    sc.collection.objects.link(inst)
    bpy.context.view_layer.update()
    anchors = {
        "open":    (0.0, 30.0, 0.0),      # on the ground, nothing in front: ok (hits ground at itself)
        "blocked": (0.0, 15.0, 0.5),      # low, behind the wall: HIDDEN by wall
        "in_haze": (20.0, 30.0, 5.0),     # inside the haze box: ok only with ignore=("haze",)
        "barge_centre": (-20.0, 30.0, 8.0),  # inside its own object: INSIDE, not a failure
        "past_ghost": (-20.0, 20.0, 0.0),    # behind a hide_render wall: ok
        "past_inst": (35.0, 20.0, 0.0),      # behind an instanced wall: UNRESOLVED, not HIDDEN
    }
    rows = check_occlusion(sc, cam, anchors, ignore=("haze",))
    flags = {r[0]: (r[1], r[2]) for r in rows}
    assert flags["open"][0] == "ok", flags
    assert flags["blocked"] == ("HIDDEN", "wall"), flags
    assert flags["in_haze"][0] == "ok", flags
    assert flags["barge_centre"] == ("INSIDE", "barge"), flags
    assert flags["past_ghost"][0] == "ok", flags
    assert flags["past_inst"] == ("UNRESOLVED", "inst_box"), flags
    ghost.hide_render = False
    assert check_occlusion(sc, cam, {"past_ghost": anchors["past_ghost"]})[0][1:3] == ("HIDDEN", "ghost")
    ghost.hide_render = True
    assert check_occlusion(sc, cam, {"in_haze": anchors["in_haze"]})[0][1:3] == ("INSIDE", "haze")
    try:
        check_occlusion(sc, cam, anchors, ignore=("haze",), strict=True)
        raise AssertionError("strict occlusion did not raise")
    except FrameCheckError as e:
        assert "blocked=HIDDEN by wall" in str(e) and not any(
            n in str(e) for n in ("open", "barge", "past_ghost", "past_inst")), str(e)
    print("### FRAME_CHECK_OCCLUSION_DEMO: PASS")


if __name__ == "__main__":
    # Demo on a trivial scene: a camera 30 m back and 10 m up, aimed down the +Y axis.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    cd = bpy.data.cameras.new("cam")
    cd.sensor_fit = 'HORIZONTAL'
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
    cam.location = (0.0, -30.0, 10.0)
    cam.rotation_euler = (Vector((0.0, 60.0, -10.0)) - cam.location).to_track_quat('-Z', 'Y').to_euler()
    bpy.context.view_layer.update()

    print("### round trip points hit:", round_trip_check(sc, cam))
    hero = (0.0, 30.0, 0.0)
    hx, hy, _ = to_ndc(sc, cam, hero)
    demo = {
        "hero":   (hero, (hx, hy)),                         # intended = actual
        "drifted": ((6.0, 30.0, 0.0), (hx, hy)),            # lands 6 m off its intended spot
        "spire":  ((0.0, 60.0, 400.0), (0.55, 0.70)),       # far above the frame
        "behind": ((0.0, -60.0, 5.0), (0.50, 0.50)),        # behind the camera
    }
    rows = check_anchors(sc, cam, demo)
    flags = [r[4] for r in rows]
    assert flags == ["ok", "CHECK", "OFF FRAME", "BEHIND CAMERA"], flags
    print("### FRAME_CHECK_DEMO: PASS", flags)

    # Strict mode: a clean table passes silently, the demo table raises and names its bad rows.
    check_anchors(sc, cam, {"hero": demo["hero"]}, strict=True)
    try:
        check_anchors(sc, cam, demo, strict=True)
        raise AssertionError("strict mode did not raise on a table with bad rows")
    except FrameCheckError as e:
        assert all(n in str(e) for n in ("drifted", "spire", "behind")) and "hero" not in str(e), str(e)
    print("### FRAME_CHECK_STRICT_DEMO: PASS")
    _occlusion_demo(sc, cam)
    if "--strict" in sys.argv:       # prove the process exit code: this run is expected to fail
        check_anchors(sc, cam, demo, strict=True)
