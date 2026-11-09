"""Falsifier runner: execute the skill's python snippets and scripts headless and check identity facts.

Run with plain Python (not inside Blender):
  python check_snippets.py [--blender PATH] [--keep-going] [--no-render]

--no-render: for a quick check without the render demos. The script demos
that call bpy.ops.render.render (silhouette_proof.py, scene_template.py) are reported SKIPPED, never
PASS, and every reference block and MANIFEST fact runs with bpy.ops.render.render replaced by a
function that raises, so a block that starts rendering fails loudly instead of rendering.
SKIPPED rows do not fail the run; the summary line counts them.

What it does:
  0. Compiles every scripts/*.py on the host with warnings as errors, before anything
     else: a SyntaxWarning fails the run here, since one inside Blender does not.
  1. Walks ../references/*.md, extracts fenced ```python blocks (blocks fenced
     ```python norun are skipped and counted). An INDENTED python fence is reported
     as a failure, because the extractor only matches fences at column 0 and an
     indented one would otherwise be neither run nor counted.
  2. Wraps each block with warnings.simplefilter("error", DeprecationWarning), `import bpy`
     and a fresh bpy.ops.wm.read_factory_settings(use_empty=True), so a block
     that only works because an earlier block ran will fail by itself.
  3. Runs ONE Blender process per reference file, executing blocks in order and
     stopping that file at the first failure (--keep-going runs the rest too).
  4. Smoke calls: a block that only defines functions would pass trivially, so SMOKE
     appends a call and an assertion to the blocks it names (build_split_sky,
     make_ramped_fog, box_mesh, add_proxy_lights, build_glow_compositor, Batch,
     ridge_z, shear, max_pixel_diff). Smoked blocks are marked and counted.
  5. Runs MANIFEST, the identity facts SKILL.md and api.md state before any
     lookup; if Blender changes, the same test fails for every copy.
  6. Runs the demos of scripts/frame_check.py (printing, strict and occlusion modes; the
     strict one must exit 1 and name its rows), silhouette_proof.py and scene_template.py,
     each as its own Blender process, checking exit code and sentinel lines.
  7. Runs the host-side scripts in HOST under this Python with -I (project_nobpy.py).
  8. PRESET: parses the eevee.md section 1a python block and scene_template.py's EEVEE
     block, and fails if any assignment differs or exists in only one of them. The two
     resolution lines are exempt (the template takes --res). Host-side, no Blender.
  9. Prints a PASS/FAIL/SKIPPED table and exits nonzero on any failure.

Blocks with no smoke entry still pass trivially if they only define functions: they
prove the code parses and the imports resolve, not that the function works.

STATUS: TESTED 2026-11-08 on Blender 5.2.0 LTS, a full run with both render demos, the occlusion
demo and the PRESET check; the counts are in the latest Merge log in ../INTAKE.md. The PRESET
check was replayed with one template value changed and failed it. The compile step was replayed on a bad script
and failed it. Earlier runs: 2026-11-01 29 checks (12 MANIFEST
facts, 16 python blocks, 11 fenced norun); 2026-10-27 28 checks, 9 norun.
"""
import argparse
import glob
import os
import subprocess
import sys
import tempfile
import warnings

HERE = os.path.dirname(os.path.abspath(__file__))
REFS = os.path.join(HERE, "..", "references")
DEFAULT_BLENDER = os.environ.get("BLENDER", r"C:\Program Files\Blender Foundation\Blender 5.2\blender.exe")

# Identity facts: (name, code). Each runs in a fresh factory scene.
MANIFEST = [
    ("scene.node_tree is gone", "assert not hasattr(bpy.context.scene, 'node_tree')"),
    ("engine id BLENDER_EEVEE exists",
     "assert 'BLENDER_EEVEE' in {i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items}"),
    ("BLENDER_EEVEE_NEXT is gone",
     "assert 'BLENDER_EEVEE_NEXT' not in {i.identifier for i in bpy.types.RenderSettings.bl_rna.properties['engine'].enum_items}"),
    ("boolean solver is FLOAT, not FAST",
     "bpy.ops.mesh.primitive_cube_add()\n"
     "mod = bpy.context.active_object.modifiers.new('b', 'BOOLEAN')\n"
     "ids = [i.identifier for i in mod.bl_rna.properties['solver'].enum_items]\n"
     "assert 'FLOAT' in ids and 'FAST' not in ids, ids"),
    ("sequencer collection is strips, not sequences",
     "ids = [p.identifier for p in bpy.types.SequenceEditor.bl_rna.properties]\n"
     "assert 'strips' in ids and 'sequences' not in ids, ids"),
    ("scene.eevee.use_bloom is gone", "assert not hasattr(bpy.context.scene.eevee, 'use_bloom')"),
    ("glare options are sockets, not properties",
     "t = bpy.data.node_groups.new('C', 'CompositorNodeTree')\n"
     "g = t.nodes.new('CompositorNodeGlare')\n"
     "assert 'glare_type' not in g.bl_rna.properties and 'Type' in [s.identifier for s in g.inputs]"),
    ("CompositorNodeComposite is gone",
     "t = bpy.data.node_groups.new('C', 'CompositorNodeTree')\n"
     "try:\n    t.nodes.new('CompositorNodeComposite')\n    raise SystemExit('exists')\n"
     "except RuntimeError:\n    pass"),
    ("links.new accepts either argument order",
     "t = bpy.data.node_groups.new('C', 'CompositorNodeTree')\n"
     "a = t.nodes.new('CompositorNodeRLayers'); b = t.nodes.new('CompositorNodeGlare')\n"
     "t.links.new(a.outputs['Image'], b.inputs['Image']); t.links.clear()\n"
     "t.links.new(b.inputs['Image'], a.outputs['Image'])\n"
     "assert len(t.links) == 1 and t.links[0].from_node == a"),
    ("a new material or world already has a node_tree",
     "assert bpy.data.materials.new('m').node_tree is not None\n"
     "assert bpy.data.worlds.new('w').node_tree is not None"),
    ("default camera clip_end is 1000.0",
     "assert bpy.data.cameras.new('c').clip_end == 1000.0"),
    ("bevel modifier takes width, segments, limit_method ANGLE, harden_normals",
     "bpy.ops.mesh.primitive_cube_add()\n"
     "m = bpy.context.active_object.modifiers.new('b', 'BEVEL')\n"
     "m.width = 0.01; m.segments = 2; m.limit_method = 'ANGLE'; m.harden_normals = True"),
    ("Light has use_shadow, not shadow",
     "l = bpy.data.lights.new('l', 'POINT')\n"
     "assert hasattr(l, 'use_shadow') and not hasattr(l, 'shadow')"),
    ("shadow_pool_size enum runs 16 to 2048 incl. 1536 and 2048",
     "ids = [i.identifier for i in bpy.types.SceneEEVEE.bl_rna.properties['shadow_pool_size'].enum_items]\n"
     "assert ids == ['16', '32', '64', '128', '256', '512', '1024', '1536', '2048'], ids"),
]

# Smoke calls appended to a block whose code contains the marker. Each runs after the block's own
# code in the same process, so it can use the block's definitions.
SMOKE = [
    ("def build_split_sky(", """
sc = bpy.context.scene
build_split_sky(sc, (0.1, 0.3, 1.0, 1.0), (0.0, 0.0, 0.02, 1.0))
nt = sc.world.node_tree
types = {n.bl_idname for n in nt.nodes}
assert {'ShaderNodeLightPath', 'ShaderNodeMixRGB', 'ShaderNodeBackground', 'ShaderNodeOutputWorld'} <= types, types
assert len(nt.links) == 3, len(nt.links)
"""),
    ("def make_ramped_fog(", """
mat = make_ramped_fog("F", 0.012)
nt = mat.node_tree
vol = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeVolumePrincipled')
out = next(n for n in nt.nodes if n.bl_idname == 'ShaderNodeOutputMaterial')
assert vol.inputs['Density'].is_linked and out.inputs['Volume'].is_linked
"""),
    ("def box_mesh(", """
me = box_mesh("b", -1, 1, -2, 2, -3, 3)
assert len(me.polygons) == 6 and len(me.vertices) == 8
for poly in me.polygons:      # box centred on the origin, so an outward normal points away from it
    assert poly.normal.dot(poly.center) > 0, poly.index
"""),
    ("class Batch:", """
import mathutils
b = Batch("t")
b.add([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [(0, 1, 2)], mathutils.Matrix.Translation((5, 0, 0)))
b.add([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [(0, 1, 2)])
assert b.v[0] == (5.0, 0.0, 0.0) and b.f[-1] == (3, 4, 5), (b.v, b.f)
"""),
    ("def ridge_z(", """
assert ridge_z(0, 10, 20, 5) == 0.0 and ridge_z(30, 10, 20, 5) == 5.0 and abs(ridge_z(15, 10, 20, 5) - 2.5) < 1e-9
"""),
    ("def shear(", """
assert shear(1.0, 2.0, 0.5) == (2.0, 2.0)
"""),
    ("def add_proxy_lights(", """
bpy.ops.mesh.primitive_cylinder_add(radius=0.06, depth=2.2, location=(0, 0, 1.25))
tube = bpy.context.active_object
bpy.context.view_layer.update()
sc = bpy.context.scene
ls = add_proxy_lights(sc, tube, (0, 0.8, 1, 1), 15.0)
assert len(ls) == 4 and tube.visible_shadow is False
assert abs(ls[0].data.energy - 12.76) < 0.05, ls[0].data.energy      # the calibration quoted in eevee.md
assert abs(sum(l.location.z for l in ls) / 4 - 1.25) < 1e-6           # spread along the tube's long (z) axis
assert sc.eevee.light_threshold < 0.0011     # float32 storage of 0.001
"""),
    ("def build_glow_compositor(", """
t = bpy.context.scene.compositing_node_group
assert t is not None and sum(1 for n in t.nodes if n.bl_idname == 'CompositorNodeGlare') == 2
assert len(t.links) == 4 and all(l.is_valid for l in t.links), len(t.links)
"""),
    ("def max_pixel_diff(", """
import os, tempfile
_d = tempfile.mkdtemp()
def _mk(name, v):
    im = bpy.data.images.new(name, 8, 8)
    im.pixels = [v] * (8 * 8 * 4)
    im.filepath_raw = os.path.join(_d, name + ".png")
    im.file_format = 'PNG'
    im.save()
    return im.filepath_raw
_a, _b, _c = _mk("a", 0.2), _mk("b", 0.2), _mk("c", 0.6)
assert max_pixel_diff(_a, _b) == 0.0 and max_pixel_diff(_a, _c) > 0.1
"""),
]

# Script demos: (label, script, args after "--", expected exit code, sentinel lines that must appear,
# renders). renders=True marks a demo that calls bpy.ops.render.render; --no-render skips it.
SCRIPTS = [
    ("frame_check.py", "frame_check.py", [], 0,
     ["### FRAME_CHECK_DEMO: PASS", "### FRAME_CHECK_STRICT_DEMO: PASS",
      "### FRAME_CHECK_OCCLUSION_DEMO: PASS"], False),
    ("frame_check --strict", "frame_check.py", ["--strict"], 1,
     ["FrameCheckError", "drifted=CHECK, spire=OFF FRAME, behind=BEHIND CAMERA"], False),
    ("silhouette_proof.py", "silhouette_proof.py", ["{tmp}/sil.png"], 0, ["### SILHOUETTE_DEMO: PASS"], True),
    ("scene_template.py", "scene_template.py", ["--res", "320", "--out", "{tmp}/tpl.png"], 0,
     ["### CLIP_END", "### OUT:"], True),
]

# Host-side scripts, run under this Python with -I: (label, script, args, sentinel lines that must appear).
HOST = [
    ("project_nobpy.py", "project_nobpy.py",
     ["--loc", "0", "-10", "0", "--aim", "0", "0", "0", "--lens", "35",
      "--point", "centre=0,0,0@0.5,0.5", "--point", "behind=0,-20,0"],
     ["1 checked, 0 FAIL, worst dev 0.000", "BEHIND"]),
]

RUNNER = '''import sys, traceback
args = sys.argv[sys.argv.index("--") + 1:]
keep = args[0] == "keep"
if args[1] == "norender":
    import bpy
    def _no_render(*a, **k):
        raise RuntimeError("bpy.ops.render.render called under --no-render")
    _sub = bpy.ops.render              # a fresh module object on every access, so pin one
    _sub.render = _no_render
    bpy.ops.render = _sub              # TESTED 2026-11-08: a later bpy.ops.render.render() raises
for i, f in enumerate(args[2:]):
    print("### BLOCK %d START" % i, flush=True)
    try:
        exec(compile(open(f, encoding="utf-8").read(), f, "exec"), {"__name__": "__main__"})
        print("### BLOCK %d PASS" % i, flush=True)
    except BaseException as e:
        tb = traceback.extract_tb(e.__traceback__)[-1]
        print("### BLOCK %d FAIL %s: %s (line %s)" % (i, type(e).__name__, str(e).splitlines()[0][:150] if str(e) else "", tb.lineno), flush=True)
        if not keep:
            break
'''
WRAP = ('import warnings; warnings.simplefilter("error", DeprecationWarning)\n'
        'import bpy\nbpy.ops.wm.read_factory_settings(use_empty=True)\n')


def extract(path):
    """Return ([(md_line, code)], skipped_count, [indented_fence_lines]) for the python fences in one markdown file."""
    blocks, skipped, buf, info, start, problems = [], 0, None, "", 0, []
    for n, line in enumerate(open(path, encoding="utf-8").read().split("\n"), 1):
        if buf is None and not line.startswith("```") and line.lstrip().startswith("```python"):
            problems.append(n)
        if buf is None and line.startswith("```"):
            info, buf, start = line[3:].strip(), [], n
        elif buf is not None and line.startswith("```"):
            if info.split()[:1] == ["python"]:
                if "norun" in info.split():
                    skipped += 1
                else:
                    blocks.append((start, "\n".join(buf)))
            buf = None
        elif buf is not None:
            buf.append(line)
    return blocks, skipped, problems


def smoke_for(code):
    """The smoke snippets whose marker appears in this block's code."""
    return [snip for marker, snip in SMOKE if marker in code]


def compile_scripts():
    """Compile every scripts/*.py with warnings as errors; return rows for the table."""
    rows = []
    for path in sorted(glob.glob(os.path.join(HERE, "*.py"))):
        with open(path, encoding="utf-8") as f:
            source = f.read()
        with warnings.catch_warnings():
            warnings.simplefilter("error")
            try:
                compile(source, path, "exec")
                rows.append(("COMPILE", os.path.basename(path), "PASS", ""))
            except (SyntaxError, Warning) as e:
                rows.append(("COMPILE", os.path.basename(path), "FAIL", str(e).splitlines()[0][:150]))
    return rows


def run(label, blocks, blender, keep, no_render=False):
    """Run blocks in one Blender process; return a list of (label, where, status, detail)."""
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        files = []
        for i, (_, code) in enumerate(blocks):
            p = os.path.join(tmp, "block_%d.py" % i)
            open(p, "w", encoding="utf-8").write(WRAP + code + "\n" + "".join(smoke_for(code)))
            files.append(p)
        runner = os.path.join(tmp, "runner.py")
        open(runner, "w", encoding="utf-8").write(RUNNER)
        cmd = [blender, "-b", "--factory-startup", "--python-exit-code", "1", "--python", runner,
               "--", "keep" if keep else "stop", "norender" if no_render else "render"] + files
        try:
            out = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=300).stdout
        except subprocess.TimeoutExpired:
            out = ""
    status = {}
    for line in out.splitlines():
        if line.startswith("### BLOCK "):
            parts = line.split(" ", 4)
            status[int(parts[2])] = (parts[3], parts[4] if len(parts) > 4 else "")
    for i, (md_line, code) in enumerate(blocks):
        st, detail = status.get(i, ("NOT RUN", ""))
        st = {"PASS": "PASS", "FAIL": "FAIL", "START": "CRASH"}.get(st, st)
        rows.append((label, "line %d" % md_line, st, (detail + " [smoked]").strip() if smoke_for(code) else detail))
    return rows


def run_scripts(blender, no_render=False):
    """Run each script demo as its own Blender process; check exit code and sentinel lines."""
    rows = []
    with tempfile.TemporaryDirectory() as tmp:
        for label, script, args, want_code, wants, renders in SCRIPTS:
            if renders and no_render:
                rows.append(("SCRIPT", label, "SKIPPED", "renders; skipped under --no-render (compile-checked only)"))
                continue
            args = [a.replace("{tmp}", tmp) for a in args]
            cmd = [blender, "-b", "--factory-startup", "--python-exit-code", "1", "--python",
                   os.path.join(HERE, script)] + (["--"] + args if args else [])
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, errors="replace", timeout=300)
                out, code = r.stdout + r.stderr, r.returncode
            except subprocess.TimeoutExpired:
                out, code = "", -1
            missing = [w for w in wants if w not in out]
            if code != want_code:
                rows.append(("SCRIPT", label, "FAIL", "exit %s, wanted %s" % (code, want_code)))
            elif missing:
                rows.append(("SCRIPT", label, "FAIL", "missing output: %s" % missing[0]))
            else:
                rows.append(("SCRIPT", label, "PASS", "exit %s" % code))
    return rows


def run_host():
    """Run each HOST script under this Python with -I; check exit code 0 and sentinel lines."""
    rows = []
    for label, script, args, wants in HOST:
        r = subprocess.run([sys.executable, "-I", os.path.join(HERE, script)] + args,
                           capture_output=True, text=True, errors="replace", timeout=120)
        missing = [w for w in wants if w not in r.stdout]
        if r.returncode != 0:
            rows.append(("HOST", label, "FAIL", "exit %s" % r.returncode))
        elif missing:
            rows.append(("HOST", label, "FAIL", "missing output: %s" % missing[0]))
        else:
            rows.append(("HOST", label, "PASS", "exit 0"))
    return rows


# Lines the template is allowed to set differently from eevee.md 1a (it takes --res).
PRESET_EXEMPT = {"sc.render.resolution_x,sc.render.resolution_y", "sc.render.resolution_percentage"}


def _assignments(text):
    """{target: value} for the simple `a.b = value` lines of a python block (comments stripped)."""
    import re
    out = {}
    for line in text.splitlines():
        line = line.split("#")[0].strip()
        for part in line.split(";"):
            m = re.match(r"([\w.]+(?:\s*,\s*[\w.]+)*)\s*=\s*(.+)$", part.strip())
            if m and "." in m.group(1):
                out[m.group(1).replace(" ", "")] = m.group(2).strip()
    return out


def run_preset():
    """Diff the eevee.md 1a preset block against scene_template.py's copy of it."""
    md = open(os.path.join(REFS, "eevee.md"), encoding="utf-8").read()
    tpl = open(os.path.join(HERE, "scene_template.py"), encoding="utf-8").read()
    try:
        block = md.split("### 1a.", 1)[1].split("```python", 1)[1].split("```", 1)[0]
        tblock = tpl.split("# EEVEE preview preset", 1)[1].split("sc.render.filepath", 1)[0]
    except IndexError:
        return [("PRESET", "eevee.md 1a vs scene_template.py", "FAIL", "could not find one of the two blocks")]
    a, b = _assignments(block), _assignments(tblock)
    diffs = sorted(k for k in set(a) | set(b) if k not in PRESET_EXEMPT and a.get(k) != b.get(k))
    if diffs:
        k = diffs[0]
        return [("PRESET", "eevee.md 1a vs scene_template.py", "FAIL",
                 "%d differ, first %s: md %s, template %s" % (len(diffs), k, a.get(k), b.get(k)))]
    return [("PRESET", "eevee.md 1a vs scene_template.py", "PASS", "%d assignments match" % len(a))]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--blender", default=DEFAULT_BLENDER)
    ap.add_argument("--keep-going", action="store_true")
    ap.add_argument("--no-render", action="store_true",
                    help="report the demos that render as SKIPPED and block bpy.ops.render.render in blocks")
    a = ap.parse_args()
    compiled = compile_scripts()
    if not os.path.exists(a.blender):
        for label, where, st, detail in compiled:
            print("%-16s %-24s %-8s %s" % (label, where, st, detail))
        sys.exit("Blender not found: %s (use --blender)" % a.blender)
    rows = run("MANIFEST", [(i + 1, c) for i, (_, c) in enumerate(MANIFEST)], a.blender, True, a.no_render)
    rows = compiled + [(r[0], MANIFEST[int(r[1].split()[1]) - 1][0], r[2], r[3]) for r in rows]
    skipped = 0
    for path in sorted(glob.glob(os.path.join(REFS, "*.md"))):
        blocks, sk, problems = extract(path)
        skipped += sk
        for n in problems:
            rows.append((os.path.basename(path), "line %d" % n, "FAIL",
                         "indented python fence is never run; dedent it or fence norun"))
        if blocks:
            rows += run(os.path.basename(path), blocks, a.blender, a.keep_going, a.no_render)
    rows += run_scripts(a.blender, a.no_render)
    rows += run_host()
    rows += run_preset()
    # A SMOKE marker that matches no block means a rename silently dropped its smoke test.
    all_code = "\n".join(c for path in glob.glob(os.path.join(REFS, "*.md")) for _, c in extract(path)[0])
    for marker, _ in SMOKE:
        if marker not in all_code:
            rows.append(("SMOKE", marker, "FAIL", "marker matches no python block"))
    width = max(len(r[1]) for r in rows)
    for label, where, st, detail in rows:
        print("%-16s %-*s %-8s %s" % (label, width, where, st, detail))
    bad = [r for r in rows if r[2] not in ("PASS", "SKIPPED")]
    skips = sum(1 for r in rows if r[2] == "SKIPPED")
    smoked = sum(1 for r in rows if r[3].endswith("[smoked]"))
    print("\n%d checks, %d passed, %d not passing, %d skipped (--no-render), %d blocks fenced norun, %d blocks smoke-called"
          % (len(rows), len(rows) - len(bad) - skips, len(bad), skips, skipped, smoked))
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
