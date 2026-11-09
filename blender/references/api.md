# Blender 5.x API — verified facts

Everything tagged [TESTED] was confirmed by running it on Blender 5.2.0
LTS, Windows. 5.x renamed things that every tutorial and every model's
training data still write the old way, so prefer this file over recalled
knowledge; re-verify with the introspection section on any other version.
Settings values and quality measurements live in eevee.md; the few timings
here (Cycles GPU, backends) are evidence for an API behaviour, not tuning
values. Everything in this file is firm for 5.2.0 unless a line says it was
observed on one project.

Index, by what you are seeing or about to do:

| Section | Open it when |
|---|---|
| Render engine id | `enum "BLENDER_EEVEE_NEXT" not found` |
| Boolean solver and sequencer renames | `'FAST'` rejected; `sequences` missing; `new_effect` rejects `frame_end` |
| Light probe types | `TypeError` on `'CUBEMAP'`/`'PLANAR'`/`'GRID'`; `type` is read-only |
| Nodes modifier inputs | `mod["Socket_2"]` raises `TypeError` |
| `use_nodes` | a `DeprecationWarning` on materials, worlds or the scene |
| The compositor moved | `scene.node_tree` missing; the render came out pure white |
| Compositor migration, glare sockets | `glare_type` missing; Composite node gone; valid menu strings; Vignette or Film Grain "missing" (they are assets) |
| links.new argument order | unsure which socket goes first |
| Legacy scene.eevee properties | `use_bloom`, `use_ssr`, `use_gtao`, `shadow_cube_size` raise |
| Headless rendering | CLI flags and order, exit codes, Cycles ignoring the GPU, the stdout grep, backend and GPU checks |
| Camera aiming | the frame comes back rolled; `world_to_camera_view` trust; roll vs yaw |
| Animation | `action.fcurves` raises; creating fcurves; loopable drivers; a driver that does not update |
| Material slots and vectors | faces render white after appending; a sky upside down |
| Images | a packed generated image is gone after reload; 16-bit textures eating memory |
| Introspection | any API you do not trust |

---

## Render engine id: there is no BLENDER_EEVEE_NEXT in 5.x

The engine enum on 5.2 offers exactly these values [TESTED]:

```python norun
# norun: illustrative; scene is the active scene
scene.render.engine  # enum: 'BLENDER_EEVEE' | 'BLENDER_WORKBENCH' | 'CYCLES'
```

The rewritten EEVEE (raytracing, real shadows, froxel volumetrics) ships
under the plain `BLENDER_EEVEE` identifier. Blender 4.2 briefly exposed
`BLENDER_EEVEE_NEXT`; scripts carrying that string raise:

```
TypeError: bpy_struct: item.attr = val: enum "BLENDER_EEVEE_NEXT" not found in
('BLENDER_EEVEE', 'BLENDER_WORKBENCH', 'CYCLES')
```

Defensive pattern when a script must span versions:

```python
import bpy
scene = bpy.context.scene
ids = {i.identifier for i in
       type(scene).bl_rna.properties['render'].fixed_type
       .bl_rna.properties['engine'].enum_items}
scene.render.engine = 'BLENDER_EEVEE_NEXT' if 'BLENDER_EEVEE_NEXT' in ids else 'BLENDER_EEVEE'
```

---

## Boolean solver and sequencer renames [TESTED 5.2]

Two more 5.x renames. Both are asserted on 5.2 by `scripts/check_snippets.py`.

- The boolean modifier and operation `solver` value `'FAST'` became
  `'FLOAT'`. The 5.2 enum is `'FLOAT'`, `'EXACT'`, `'MANIFOLD'`.
- The sequencer collection `scene.sequence_editor.sequences` became
  `strips`.

One signature trap in the same area: `scene.sequence_editor.strips.new_effect(name, type, channel, frame_start, length, input1, input2)` takes `length`, not `frame_end`. `frame_end=` raises `TypeError: StripsTopLevel.new_effect(): was called with invalid keyword argument(s) (frame_end)`. From frame 1, `length=24` gives `frame_final_end` 25 (TESTED 2026-11-08, 5.2.0).

To re-check on another build:

```python norun
# norun: needs an existing mesh object named obj
mod = obj.modifiers.new("b", 'BOOLEAN')
print([i.identifier for i in mod.bl_rna.properties['solver'].enum_items])
print([p.identifier for p in bpy.types.SequenceEditor.bl_rna.properties])
```

---

## Light probe types were renamed, and `type` is read-only [TESTED 5.2]

The EEVEE Next rewrite replaced the probe types and 5.2 keeps the new ones. The
`'CUBEMAP'`, `'PLANAR'` and `'GRID'` that every pre-4.2 tutorial writes raise
`TypeError` from `bpy.data.lightprobes.new(name, type=...)`:

```python
import bpy
assert [i.identifier for i in bpy.types.LightProbe.bl_rna.properties["type"].enum_items]     == ['SPHERE', 'PLANE', 'VOLUME']
```

**`LightProbe.type` is read-only.** Assigning it raises
`AttributeError: bpy_struct: attribute "type" from "LightProbeSphere" is read-only`,
so the type is fixed at creation and the datablock comes back as a per-type
subclass (`LightProbeSphere`, `LightProbePlane`, `LightProbeVolume`). Code that
creates a probe and then sets `type` cannot be ported by swapping the string.

The three types no longer share a property set, so ported code fails on
properties as well as on names:

| Property | SPHERE | PLANE | VOLUME |
|---|---|---|---|
| `influence_distance`, `clip_start`, `data_display_size` | yes | yes | yes |
| `parallax_distance`, `visibility_blur`, `visibility_collection`, `visibility_*_bias` | yes | yes | yes |
| `clip_end` | yes | **no** | no |
| `falloff`, `influence_type`, `parallax_type`, `use_custom_parallax` | yes | no | no |
| `resolution_x/y/z`, `intensity`, `bake_samples`, `capture_*`, `clamp_direct`, `clamp_indirect` | no | no | yes |

A `PLANE` probe in particular exposes far less than the old planar one: no
resolution and no falloff. Read the live set with the `dump()` helper in
Introspection instead of porting from an older file.

---

## Nodes modifier inputs: `mod["Socket_2"]` is gone [TESTED 5.2.0, 2026-11-05]

On 5.2 a Nodes modifier takes no ID properties. `mod["Socket_2"] = value` raises `TypeError: bpy_struct[key] = val: id properties not supported for this type` for an object and for a plain float alike (the two types tested), and `mod.keys()` raises too. Older scripts write the old form. Set the socket through `mod.properties.inputs`, with the identifier from the group interface:

```python
import bpy
ng = bpy.data.node_groups.new("G", "GeometryNodeTree")
ng.interface.new_socket("Geometry", in_out="INPUT", socket_type="NodeSocketGeometry")
val = ng.interface.new_socket("Val", in_out="INPUT", socket_type="NodeSocketFloat")
ng.interface.new_socket("Geometry", in_out="OUTPUT", socket_type="NodeSocketGeometry")
ob = bpy.data.objects.new("a", bpy.data.meshes.new("a"))
mod = ob.modifiers.new("N", "NODES")
mod.node_group = ng
try:
    mod[val.identifier] = 2.5
except TypeError:
    pass
else:
    raise AssertionError("mod[identifier] works again: update api.md and SKILL.md")
getattr(mod.properties.inputs, val.identifier).value = 2.5
assert getattr(mod.properties.inputs, val.identifier).value == 2.5
```

Assigning the attribute itself (`inputs.Socket_2 = 2.5`) is read-only; write `.value`. An object socket takes an object the same way (TESTED). The Triangle City kit met the error and used one small node group per part with the object set on the Object Info socket, which also works (OBSERVED(triangle-bashkit)).

---

## `use_nodes` is deprecated everywhere

`World.use_nodes`, `Material.use_nodes` and `Scene.use_nodes` all emit:

```
DeprecationWarning: 'X.use_nodes' is expected to be removed in Blender 6.0
```

They still function in 5.2 [TESTED]. Materials and worlds continue to expose
`.node_tree` normally, and a **new material or world already has its
`node_tree` before `use_nodes` is set** [TESTED 5.2, asserted by
`scripts/check_snippets.py`]. So do not set `use_nodes` on a new datablock.
The practice every script and snippet in this skill follows, which also covers
older builds: `if x.node_tree is None: x.use_nodes = True`. Only the **scene**
compositor moved (below).

---

## The compositor moved off `scene.node_tree`

`scene.node_tree` **no longer exists** on 5.2 [TESTED]:

```
AttributeError: 'Scene' object has no attribute 'node_tree'
```

The scene exposes exactly two compositor-related attributes:

```python norun
# norun: needs the active scene bound to the name scene
scene.compositing_node_group   # None by default; assign a CompositorNodeTree
scene.use_nodes                # deprecated
```

You create the tree as a standalone node group and assign it:

```python norun
# norun: needs the active scene bound to the name scene
ng = bpy.data.node_groups.new("Comp", 'CompositorNodeTree')
scene.compositing_node_group = ng
```

### Trap: an empty or unwired group renders PURE WHITE [TESTED]

Assigning a node group whose Group Output is not properly wired produces a
flat white frame **with no error and no warning**. Diagnosed by byte size: the
same scene rendered 130 KB with no compositor, and 28 KB of pure white with an
unwired one.

So: wire the compositor completely, or leave `scene.compositing_node_group`
as `None`. There is no safe half-configured state. A `NodeGroupInput` does not
carry the render either: Group Input -> Group Output is the same white frame,
and the source must be a `CompositorNodeRLayers` with `rl.scene = scene`
[TESTED].

The group needs real interface sockets, created through `ng.interface`:

```python norun
# norun: needs the node group ng from the previous block
ng.interface.new_socket("Image", in_out='INPUT',  socket_type='NodeSocketColor')
ng.interface.new_socket("Image", in_out='OUTPUT', socket_type='NodeSocketColor')
```

`ng.interface` methods available: `new_socket`, `new_panel`, `remove`, `clear`,
`copy`, `move`, `move_to_parent`, `items_tree`, `active`, `active_index`.

---

## Compositor migration, glare sockets and node menu items

The full compositor migration, with identifiers (identifiers beat display names — duplicates exist):

| Old (<= 4.5) | 5.x |
|---|---|
| `Composite` node | **Removed.** Use a **Group Output** node whose **first input is a Color socket**. Add the socket with `tree.interface.new_socket(...)` |
| Node options as properties (`node.glare_type`) | Options are **input sockets** (`node.inputs['Type'].default_value = 'Fog Glow'`). Menu sockets take the display **string**. |
| Many compositor nodes (Math, Gamma, Mix RGB, Z Combine...) | Replaced by Shader node counterparts: `ShaderNodeMix`, `ShaderNodeMath`, `ShaderNodeGamma`. `CompositorNodeMixRGB` raises "undefined" [TESTED]. |
| File Output `base_path`, `file_slots` | `directory`, `file_name`, `file_output_items` [DOC release_notes/5.0 compositor_migration]; not tested here |
| `scene.copy()` copies the tree | now only references it |
| Turn compositor off with `use_nodes=False` | `scene.render.use_compositing = False` [TESTED: bypasses the tree] |

Compositor runs in `-b` mode and on either device [TESTED]: `scene.render.compositor_device` `'CPU'` or
`'GPU'` (default GPU) gave identical results; `compositor_precision` `'AUTO'`/`'FULL'`;
`compositor_denoise_device`, `compositor_denoise_preview_quality`, `compositor_denoise_final_quality`.

### Glare node: 5.2 sockets [TESTED] by introspection; identifiers differ from display names
Use the **identifier** (`node.inputs["Highlights Threshold"]`). In 5.2, `inputs["Threshold"]` also
resolved by display name [TESTED], but names can repeat on other nodes (Color Balance has several "Lift"),
so use identifiers.

| Identifier | Display name | Type | Default | Notes |
|---|---|---|---|---|
| `Image` | Image | Color | | input |
| `Type` | Type | Menu | **`Streaks`** (not Bloom) | `'Bloom','Ghosts','Streaks','Fog Glow','Simple Star','Sun Beams','Kernel'` |
| `Quality` | Quality | Menu | `Medium` | `'High','Medium','Low'` |
| `Highlights Threshold` | Threshold | Float | 1.0 | luminance needed to glow (scene-linear) |
| `Highlights Smoothness` | Smoothness | Factor | 0.1 | softness of threshold |
| `Clamp Highlights` | Clamp | Bool | False | clamp extracted highlights |
| `Maximum Highlights` | Maximum | Float | 10.0 | clamp ceiling |
| `Strength` | Strength | Factor | 1.0 | >1 boosts glare, <1 blends |
| `Saturation` | Saturation | Factor | 1.0 | glare saturation |
| `Tint` | Tint | Color | white | glare tint |
| `Size` | Size | Factor | 0.5 | Bloom/Fog Glow/Sun Beams; relative to image (1 = whole image) |
| `Streaks` | Streaks | Int | 4 | count |
| `Streaks Angle` | Streaks Angle | Angle | 0 | |
| `Iterations` | Iterations | Int | 3 | Ghosts count / Streaks and Simple Star quality |
| `Fade` | Fade | Factor | 0.9 | |
| `Color Modulation` | Color Modulation | Factor | 0.25 | Ghosts/Streaks chromatic shift |
| `Diagonal Star` | Diagonal | Bool | True | Simple Star rotation |
| `Sun Position` | Sun Position | 2D vector | (0.5, 0.5) | Sun Beams source |
| `Jitter` | Jitter | Factor | 0 | Sun Beams speed/grain |
| `Kernel Data Type` | Kernel Data Type | Menu | `Float` | `'Float','Color'` |
| `Float Kernel`, `Color Kernel` | Kernel (both) | Float, Color | | Kernel mode; two sockets share the display name `Kernel` |

Outputs: `Image` (beauty + glare), `Glare` (glare only), `Highlights` (extracted). Manual:
https://docs.blender.org/manual/en/latest/compositing/types/filter/glare.html . 5.0 made Fog Glow more
physical, made Low/Medium quality stable, added Sun Beams and Kernel; 5.1 made Glare 1.2-2x faster [DOC release_notes/5.0, 5.1 compositor].

`enum_items` introspection returns empty for these MENU sockets (they are populated dynamically), which
is why the valid strings are listed here. The menu strings are title-case, and an invalid value raises
`TypeError` (provoking that error is how the list is read back; see Introspection).
Menu items for the other nodes you will use [TESTED]: Color Balance `Type` = `'Lift/Gamma/Gain',
'Offset/Power/Slope (ASC-CDL)', 'White Point'`; Blur `Type` = `'Flat','Tent','Quadratic','Cubic','Gaussian',
'Fast Gaussian','Catrom','Mitch'`; Denoise `Quality` = `'Follow Scene','High','Balanced','Fast'`;
Tonemap `Type` = `'R/D Photoreceptor','Rh Simple'`.

### Minimal working snippet (tested): Render Layers -> Glare -> Glare -> Color Correction -> Group Output

```python
import bpy

def build_glow_compositor(scene, glares, saturation=1.0):
    """glares: list of dicts keyed by Glare input identifier, e.g. {"Type":"Fog Glow","Size":0.25}"""
    tree = bpy.data.node_groups.new("Comp", "CompositorNodeTree")
    scene.compositing_node_group = tree
    rl = tree.nodes.new("CompositorNodeRLayers")
    rl.scene = scene; rl.layer = scene.view_layers[0].name
    out = tree.nodes.new("NodeGroupOutput")
    tree.interface.new_socket(name="Image", in_out="OUTPUT", socket_type="NodeSocketColor")
    last = rl.outputs["Image"]
    for cfg in glares:
        g = tree.nodes.new("CompositorNodeGlare")
        for k, v in cfg.items():
            g.inputs[k].default_value = v
        tree.links.new(last, g.inputs["Image"])
        last = g.outputs["Image"]
    if saturation != 1.0:
        cc = tree.nodes.new("CompositorNodeColorCorrection")
        cc.inputs["Master Saturation"].default_value = saturation
        tree.links.new(last, cc.inputs["Image"]); last = cc.outputs["Image"]
    tree.links.new(last, out.inputs["Image"])      # Group Output first input MUST be the color socket
    return tree

FOG = {"Type": "Fog Glow", "Quality": "High", "Highlights Threshold": 0.8, "Highlights Smoothness": 0.5}
build_glow_compositor(bpy.context.scene,
                      [dict(FOG, **{"Size": 0.25, "Strength": 0.6}), dict(FOG, **{"Size": 0.7, "Strength": 0.35})],
                      saturation=1.15)
# scene.render.use_compositing must be True (default). The view transform is applied to the Group Output result.
```

### Other compositor nodes that exist in 5.2 [TESTED]
`CompositorNodeColorCorrection` (per-range Saturation/Contrast/Gamma/Gain/Offset), `ColorBalance`,
`HueSat`, `CurveRGB`, `BrightContrast`, `Blur`, `BokehBlur`, `Denoise`, `Lensdist` (Dispersion = chromatic
aberration), `Tonemap`, `AlphaOver`, `ConvertColorSpace`, `ConvertToDisplay`, `OutputFile`, `Image`,
`Cryptomatte`. Vignette, Film Grain, Chromatic Aberration, Split Toning are **assets** (node groups from
the asset shelf), not node types; `CompositorNodeVignette` does not exist [TESTED]; the assets are listed in the 5.0 and 5.2 compositor release notes [DOC release_notes/5.0, 5.2].
Grain/vignette must be built from nodes or appended assets.

---

## links.new argument order

`links.new(a.outputs[...], b.inputs[...])` and
`links.new(b.inputs[...], a.outputs[...])` build the same link on 5.2
[TESTED]; asserted by `scripts/check_snippets.py`. The order is a convention,
not a correctness question. The snippets and scripts in this skill write the
output socket first.

---

## Confirmed class and property names (5.2)

These node classes were once flagged as unconfirmed. All are correct on 5.2 and
were used in a working production script, which is OBSERVED(triangle-battle)
evidence and not a controlled test:

`CompositorNodeTree`, `CompositorNodeHueSat`, `CompositorNodeRLayers`,
`ShaderNodeVolumePrincipled`, `ShaderNodeLightPath`, `ShaderNodeMapRange`,
`ShaderNodeValToRGB`, `ShaderNodeLayerWeight`, `ShaderNodeAddShader`,
`ShaderNodeTexEnvironment`, `NodeGroupOutput`.

---

## Legacy scene.eevee properties that are gone on 5.2

Read the live list of what does exist with the Introspection section below.

### There is NO bloom property

Legacy EEVEE's `scene.eevee.use_bloom` is **gone**. Glow must come from
emissive materials, real volumetric scattering, and a compositor Glare pass.
Any tutorial that says to tick Bloom predates the EEVEE rewrite.

Other legacy EEVEE properties that raise `AttributeError` on 5.2 [TESTED]: `use_ssr`,
`use_soft_shadows`, `use_gtao`, `use_volumetric_lights`, `shadow_cube_size`, `gi_auto_bake`, `use_sss`.

Emission strength vs hue under AgX: eevee.md, Emission.

---

## Headless rendering from the command line

Two verified ways to drive a render from the command line, plus the flags that matter.

### Verified invocation patterns [TESTED, 5.2.0]
```bash
BL="C:/Program Files/Blender Foundation/Blender 5.2/blender.exe"

# A) script builds scene and renders itself (most robust)
"$BL" -b --factory-startup --python-exit-code 1 --python scene.py -- --stage 6 --res 960
#    in scene.py:  bpy.ops.render.render(write_still=True)
#    parse extra args after "--":  sys.argv[sys.argv.index("--") + 1:]

# B) script only builds the scene, CLI renders it
"$BL" -b --factory-startup --python-exit-code 1 --python setup.py -o "C:/out/shot_####" -F PNG -f 1
#    -> C:\out\shot_0001.png.  Without #### Blender appends the frame number: -o ".../p1_" -> p1_0001.png
#    Arguments run in order: put -o/-F/-x BEFORE -f or -a. -f/-a go last.

# C) build script saved a .blend; a render script opens it and renders named cameras
"$BL" -b --factory-startup --python-exit-code 1 scene.blend --python render.py -- --shots a,b
#    the .blend must come BEFORE --python: with the order swapped the script ran against the
#    factory startup scene (Camera, Cube, Light) and bpy.data.filepath was empty [TESTED 5.2.0, 2026-11-01].
#    Pattern, conventions and costs: pipeline.md.
```
- `--factory-startup` always (reproducible; ignores user prefs and addons).
- `--python-exit-code 1`: without it a Python exception still exits **0** [TESTED: exit 0 vs 7].
- From script: `scene.render.filepath` (extension is appended when `use_file_extension` True),
  `scene.render.image_settings.file_format/color_depth/color_mode/exr_codec`. With
  `bpy.ops.render.render(write_still=True)` the path has no frame number unless it contains `####`.
- Compositor File Output (5.x): the frame number is only appended on animation renders; CLI renders
  count as animation renders [DOC release_notes/5.0 compositor].
- Engine override `-E BLENDER_EEVEE`; list with `-E help`. Check **all scenes** use the right engine.
- Logging: `--log-level info`; `--debug-gpu` (GL 4.3+ debug), `--profile-gpu` (writes profile.json).
- `-t 0` threads (CPU side only matters for scene prep).
- Do not name a script after a standard-library module (`inspect.py`, `random.py`): the script's folder comes first on the import path, so the stdlib import inside Blender or a host tool loads your file instead (one debugging detour on the bash kit, OBSERVED(triangle-bashkit)).

### Cycles on the GPU headless (NVIDIA RTX, OptiX)

`-b --factory-startup` ignores user preferences: `compute_device_type` is `NONE`, `prefs.devices` is empty, and `scene.cycles.device = 'GPU'` alone renders on the CPU with no error. TESTED 2026-11-04 on 5.2.0, RTX 4090 Laptop: same scene 16.5 s untouched, 2.0 s after this block. The block selects OptiX devices only; on a machine without one every `d.use` stays False and Cycles silently stays on the CPU, so read the printed device list (another vendor: set `compute_device_type` from its enum and check `prefs.devices`).

```python
prefs = bpy.context.preferences.addons['cycles'].preferences
prefs.compute_device_type = 'OPTIX'
prefs.get_devices()
for d in prefs.devices:
    d.use = (d.type == 'OPTIX')
bpy.context.scene.cycles.device = 'GPU'
print("### devices", [(d.name, d.type, d.use) for d in prefs.devices])
```

### Logging: sentinel prefix and grep

Blender writes a lot of noise to stdout. Prefix your own diagnostics with a sentinel and grep for it:

```python
import os
elapsed, p = 0.0, "out.png"   # your measured render time and output path
print("### RENDER_SECONDS: %.2f" % elapsed)
print("### EXISTS:", os.path.exists(p), os.path.getsize(p) if os.path.exists(p) else 0)
```

```bash
blender.exe -b --factory-startup --python-exit-code 1 --python scene.py > run.log 2>&1
grep -E "^###|Error|Traceback" run.log | grep -v "Shadow buffer full"
grep -c "Shadow buffer full" run.log
```

Grep carefully: a pattern that misses the traceback makes a crashed run look silent. Always include
`Traceback` and `Error`, and when a run produces no output at all, read the end of the log to see what
really happened. **"Shadow buffer full" prints as an `Error:` line every frame**, so on an
overflowing render a plain `Error` grep returns thousands of lines on one bash-kit shot (OBSERVED(triangle-bashkit)), all
of them shadow warnings or copies spliced mid-line into other output (OBSERVED(triangle-bashkit)).
Exclude them from the error count and count them separately, as above. A real error spliced into
a shadow line would be dropped by the exclusion; the `Traceback` and exit code still catch Python
failures. Write the log to a file: a pipe dies with the run. Triage for silent, crashed or wrong-backend runs: diagnosis.md, The run was silent, crashed, or lied.

Scene scaffold patterns: scene-code.md.

### Does EEVEE work headless?
- **Yes, with `-b`, as long as there is a GPU and a normal interactive Windows desktop session.**
  `blender -b` creates an offscreen GL context; EEVEE rendered this way with raytracing, volumetrics,
  compositor Glare and 8K output, while a GUI Blender was open [TESTED].
- The manual: "Headless rendering is not supported on headless Windows systems" [DOC limitations
  page]. In practice that means a user session with a GPU driver.
  Linux without X needs a virtual display (xvfb-run) or EGL; not relevant here.
- **GPU selection**: OpenGL backend uses the system's default GPU. On hybrid laptops set
  `blender.exe` to *High performance* in Windows Graphics settings. Confirm in-script (below).
  `--gpu-device` selection works **only with Vulkan** [DOC arguments page]. No multi-GPU for EEVEE [DOC limitations page].

```python
import gpu
gpu.init()               # gpu.init() is new in 5.2: required in -b before gpu.platform.*
print(gpu.platform.backend_type_get(), gpu.platform.renderer_get())   # OPENGL NVIDIA GeForce RTX 4090 Laptop GPU/...
```

- **Backends**: default OPENGL here. `--gpu-backend vulkan` rendered successfully headless.
  TESTED 2026-11-03, one scene, 640x360 at 64 spp: frames 2 and 3 took 0.18-0.20 s on Vulkan against
  0.17-0.19 s on OpenGL, so steady-state speed matched; the first frame took 2.25 s against 0.51 s (cold shader compile).
  Preference: `bpy.context.preferences.system.gpu_backend` (`'OPENGL'`/`'VULKAN'`).
  `shader_compilation_method` `'THREAD'`, `gpu_shader_workers`.
- Shader compile time is paid per process; cold and warm values: eevee.md, Sampling and noise, caveat (b).

---

## Camera aiming without constraints (to_track_quat roll trap, projection noise)

Aim a camera at a point by setting its rotation directly. This is cheaper and more predictable than a Track To constraint when scripting:


```python norun
# norun: needs a camera object cam_obj and an aim point target
import mathutils
direction = mathutils.Vector(target) - cam_obj.location
cam_obj.rotation_euler = direction.to_track_quat('-Z', 'Y').to_euler()
```

**Trap: `to_track_quat` produces a garbage roll just off vertical.** [TESTED]
on 5.2 by sweeping a camera 400 m above the origin and comparing against an
analytic projection. Aimed exactly straight down or straight up, it is correct
and takes a clean fallback (local up becomes world +Y). Tilted a long way off
vertical, it is correct. But in the band between, roughly a tilt under 3.5e-4
radians and above the fallback cutoff, the frame comes back rotated by an
arbitrary angle near 90 degrees. Measured deviations in that band reach 1.0 in
normalized frame coordinates, which is a completely different picture, not a
rounding error.

The cause is that Blender derives the roll with an `acos` of a float32 cosine,
and that argument collapses to exactly -1 once the tilt is small enough. The
fallback branch below `|dx| + |dy| < 1e-4` on the unnormalized aim vector is
fine; the trouble is the sliver above it.

So for a bird's-eye camera, either aim it *exactly* vertical or tilt it by a
degree or more. Never nudge an aim "almost" straight down, which is the natural
thing to write, and note the discontinuity: exactly vertical puts world +Y at
the top of frame, while a hair off vertical follows the tilt direction instead.

**`world_to_camera_view` is not a plausible source of framing disagreement.**
Against a pure-Python float64 projector it deviated by at most 3.1e-05 in frame
coordinates anywhere on frame, and 9.6e-07 beyond 100 m, over 270 sampled
points across 10 camera cases [TESTED 5.2, the triangle-battle
project's verification script]. Its float32 camera-space noise is real but it
lives a few ulps down.

So when a projected anchor misses its spec by anything a composition would
notice, from about 1e-3 up, the spec is wrong or rounded and the backend is
not. Two near-field rows that looked like a float32 disagreement were the
spec's own 3-decimal rounding, identical in both projectors; checking the spec
first saves a cycle. OBSERVED(triangle-battle)

**Roll is not the Z channel on a level camera.** Camera looking down +Y with
`rotation_euler` X = pi/2, in the default XYZ mode: `(pi/2, 0, radians(45))`
yaws (view moves to (-0.71, 0.71, 0)); `(pi/2, radians(45), 0)` rolls about the
view axis. TESTED 2026-11-04.

---

## Animation: slotted actions and loopable drivers

On 5.2 `action.fcurves` raises AttributeError (slotted actions). Read through `action.layers[0].strips[0].channelbag(action.slots[0]).fcurves` (TESTED 2026-11-04, 5.2.0). To create, `bpy_extras.anim_utils.action_ensure_channelbag_for_slot(action, slot)` returns the channelbag, whose `fcurves` has `find`, `new` and `ensure` (existence TESTED 2026-11-08, 5.2.0). Animation craft (motion blur units, camera paths, rigs): animation.md.

**Drivers inside an excluded collection do not evaluate.** With `layer_collection.exclude = True` the object is absent from the depsgraph and its evaluated data keeps the last stored value (a light stayed at energy 50 while its driver said 70). After clearing `exclude`, call `view_layer.update()` and read through a fresh depsgraph after `frame_set` (TESTED 2026-11-08, 5.2.0).

`driver.is_simple_expression` is True for `clamp`, `abs`, `fmod`, `floor` and `sin` of `frame` and False for `sum([frame])` (TESTED 2026-11-08). Simple is sufficient to run with autoexec off, not necessary: `sum([...])` also ran, and what blocked a driver was reading `bpy.context` (pipeline.md, Opening .blend files you did not write).

For loopable motion, skip keyframes: scripted drivers in the simple-expression subset (check `driver.is_simple_expression`), each a pure function of `(frame-1)/(fps*loop_seconds)`, with `fps` a driver variable bound to `scene.render.fps`, and every channel completing integer sine cycles or integer full turns. TESTED 2026-11-04: frame 451 at 30 fps and frame 901 at 60 fps equal frame 1 for a 15 s loop, also after reload, with an emission colour driver valid and simple. They evaluate with autoexec off: pipeline.md, Opening .blend files you did not write.

Integer full turns on every axis always close. A symmetry angle such as 120° is safe on a single-axis spin; beside other axes it closes only from a zero Euler start, or on the first-applied axis, so do not rely on it (TESTED 2026-11-04 by matrix).

Animating many materials from one clock [OBSERVED(triangle-bashkit)]: one Value node per material carrying a driver with expression `frame / fps`, `fps` a SINGLE_PROP variable on the Scene's `render.fps`, and everything else node math downstream. Factors go on a Multiply in front of the existing strength, so build this layer after any relight. Every driver reported simple and valid. Per element phase comes from attributes (letter id, trail position) or Object Info Random for instances. One frame from two separate processes matched closely over a strip of rows, weaker than a pixel match.

---

## Material slots and vectors that surprise

`bpy.data.meshes.new_from_object` on a Boolean result carries one empty material slot. Appending a material then lands it on slot 2 while every face stays on index 0, the empty slot, so the faces render white with no error (slot count and face index TESTED 2026-11-05, 5.2.0, two cubes with no material; white render OBSERVED(triangle-bashkit)). Clear the slots before appending.

Shader `Geometry.Incoming` points back toward the camera, so its z is negative above the horizon. A one-sided sky built on it comes out upside down, and a sky graph using `abs` never reveals it (OBSERVED(triangle-bashkit), seen in render).

---

## Images: packing and bit depth

- **Assign `im.pixels` first, then `.pack()`; the order matters.** `bpy.data.images.new(...)` then `.pack()` before any pixels leaves `packed_file` None and `source` GENERATED, and it stays that way when pixels are assigned afterwards: the image reloads black. With `im.pixels` assigned first, `.pack()` works: `packed_file` is set, `source` becomes FILE, and after save and reload it is still packed with the pixels intact (a byte image comes back quantised to 8 bits: 0.5 reads 0.502) (TESTED 2026-11-08, 5.2.0, each case saved and reopened). An earlier note here said a generated image never survived `.pack()` and prescribed saving to PNG first; that was too broad. Saving to a PNG, loading it as a FILE image and packing that also works (the earlier note's route, TESTED 2026-11-08).
- **16-bit PNG textures load as float.** A 16-bit PNG loads with `is_float` True and 128 bits per pixel (RGBA float32); an 8-bit one does not (TESTED). At 2048 x 2048 with mipmaps that is about 89 MB per texture in memory. Some downloaded asset textures are 16-bit (Poly Haven leaves and bark on one build, OBSERVED(archway)); reduce them to 8-bit before packing when the depth is not needed.

---

## Introspection (more durable than this file)

These snippets read the live API instead of trusting recall; run them on any Blender version other than 5.2.0.

```python
import bpy
sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'

# 1. every EEVEE property with value, type, range, enum choices
def dump(obj, filt=None):
    import re
    for p in obj.bl_rna.properties:
        if p.identifier == 'rna_type' or (filt and not re.search(filt, p.identifier)): continue
        extra = ''
        if p.type == 'ENUM': extra = ' ENUM=' + ','.join(i.identifier for i in p.enum_items)
        elif p.type in ('INT', 'FLOAT') and not p.is_array: extra = f' range=[{p.hard_min},{p.hard_max}]'
        print(f'{p.identifier} ({p.type}) = {getattr(obj, p.identifier, "?")}{extra}')
dump(sc.eevee); dump(sc.eevee.ray_tracing_options); dump(sc.view_settings)

# 2. enums whose items are dynamic (view transforms, looks, node menu sockets): provoke the error list
for target, attr in ((sc.view_settings, 'view_transform'), (sc.view_settings, 'look'), (sc.display_settings, 'display_device')):
    try: setattr(target, attr, '__x__')
    except TypeError as e: print(attr, str(e).split('not found in')[1])

# 3. compositor: every input socket with identifier, type, default, menu choices
tree = bpy.data.node_groups.new('C', 'CompositorNodeTree'); sc.compositing_node_group = tree
def sockets(idname):
    n = tree.nodes.new(idname)
    for s in n.inputs:
        dv = getattr(s, 'default_value', None)
        print(f'{n.bl_label}: id={s.identifier!r} name={s.name!r} type={s.bl_idname} default={dv}')
        if s.type == 'MENU':
            try: s.default_value = '__x__'
            except TypeError as e: print('   MENU', str(e).split('not found in')[1])
    print('outputs:', [o.identifier for o in n.outputs])
sockets('CompositorNodeGlare')
print(sorted(c.__name__ for c in bpy.types.CompositorNode.__subclasses__()))   # not exhaustive

# 4. does a legacy property exist? (hasattr beats a crash)
print(hasattr(sc.eevee, 'use_bloom'), hasattr(sc, 'node_tree'), hasattr(sc, 'compositing_node_group'))

# 5. GPU/backend in background mode (5.2+)
import gpu; gpu.init(); print(gpu.platform.backend_type_get(), gpu.platform.renderer_get())

# 6. find any RNA property by name across common structs
def find(substr):
    for owner in (sc.eevee, sc.eevee.ray_tracing_options, sc.render, sc.view_settings, sc.view_layers[0], sc.view_layers[0].eevee):
        for p in owner.bl_rna.properties:
            if substr in p.identifier: print(type(owner).__name__, p.identifier)
find('shadow')
```

A read-only property may have a setter operator. Search the operator names for it: `[f'{m}.{o}' for m in dir(bpy.ops) for o in dir(getattr(bpy.ops, m)) if 'working' in o]` returned `['wm.set_working_color_space']` on 5.2.0 (TESTED 2026-11-08).

When the CLI is the only tool: `blender --python-expr "import bpy; print(bpy.app.version_string)" -b`.
