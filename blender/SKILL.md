---
name: blender
description: Use when executing Blender work via Python/bpy - writing a bpy script, headless CLI rendering, rendering many cameras from a saved .blend, a render that is too slow, EEVEE setup, shader and compositor node graphs, volumetrics, crowds and procedural geometry at scale, or when a render is BROKEN (came out white, black, missing shadows, missing fog, missing glow, crashed silently). Covers the Blender 5.x API changes that every tutorial and every model still gets wrong. Triggers on "bpy script", "render in Blender", "headless Blender", "EEVEE", "my render came out white/black/empty", "shadow buffer full", "compositor nodes". If the render works but looks BAD (flat, amateur, small, cluttered), that is the art-direction skill, not this one.
---

# Blender: scripted scenes, headless EEVEE, 5.2

Build the scene in Python, render headless, look at the image, iterate. The
render is the test; your eyes are the assertion.

**Triage.** What the image should *look like* (composition, scale, lighting
design, colour, camera moves): the `art-direction` skill. Broken render: here.

**Companion skill.** When the task involves how the image should look, or
judging a render you just made, also load `art-direction` with the Skill tool.
It adds to this skill; it does not replace it. A broken render or a pure API
question does not need it. (owner decision, 2026-11-08)

**How this skill is written.** Firm statements are Blender facts, version traps
and "your render is broken if X" checks, tested on 5.2.0. Everything else is a
technique: it says what to measure, where it worked, tagged OBSERVED(project).
Your own project case notes go in `projects/` and your own studio conventions
in `house/`; both ship empty (each folder's README says what belongs there).

## Install and invocation

Written against Blender 5.2 LTS. Set your executable path here at install time
(Windows default: `C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`).

```bash
"/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup --python-exit-code 1 --python scene.py -- --res 960
```

- Pass `--factory-startup` and `--python-exit-code 1` on every run: without
  the second, a Python exception still exits 0 (`references/api.md`, Headless
  rendering).
- Arguments after `--` reach your script via
  `sys.argv[sys.argv.index("--") + 1:]`.
- Write scripts with a file-write tool, not Bash heredocs: on Windows Git Bash,
  quotes and backticks corrupt heredocs (seen more than once, across projects).

## Before writing any bpy: the 5.x delta

Blender 5.x renamed things that tutorials and model training data still write
the old way, and much of the old code runs without error while doing the
wrong thing. Check this table before writing, not after debugging:

| Area | Old (what you will reflexively write) | 5.2 reality |
|---|---|---|
| Engine id | `BLENDER_EEVEE_NEXT` (4.2-4.5 only) | `'BLENDER_EEVEE'`; the rewritten engine kept the old id |
| Compositor | `scene.node_tree`, `Composite` node | gone; `scene.compositing_node_group` holding a standalone `CompositorNodeTree`, output via `NodeGroupOutput` |
| Node options | `node.glare_type = 'FOG_GLOW'` | options are input *sockets*: `node.inputs['Type'].default_value = 'Fog Glow'` |
| Bloom | `scene.eevee.use_bloom` | gone (AttributeError); glow = compositor Glare + real lights + haze |
| Boolean solver | `solver='FAST'` | `'FLOAT'` |
| Sequencer | `scene.sequence_editor.sequences` | `strips` |
| Nodes modifier inputs | `mod["Socket_2"] = value` | raises `TypeError`; `mod.properties.inputs.Socket_2.value = value` |
| use_nodes | `mat/world/scene.use_nodes = True` | deprecated (removal in 6.0); a new material or world already has its `node_tree` |
| Animation | `action.fcurves` | raises; slotted actions and channelbags (`references/api.md`, Animation) |

All TESTED on 5.2.0; the first eight are re-asserted by `scripts/check_snippets.py`.
When any API surprises you, introspect instead of guessing:

```python norun
# norun: needs a node and an obj bound by the caller
print([(i.name, i.type) for i in node.inputs])
print(sorted(p.identifier for p in obj.bl_rna.properties if not p.is_readonly))
```

Then deposit what you found in `INTAKE.md` (format below).

## The loop

1. Build the whole scene in one idempotent script starting from
   `bpy.ops.wm.read_factory_settings(use_empty=True)`, regenerating from
   scratch every run. Once a build costs more than the renders you iterate on,
   save it and render from the saved `.blend` with a separate script that never
   saves (`references/pipeline.md`).
2. **Verify framing by arithmetic before rendering.** Keep an anchor table
   (world point -> intended frame coordinate) and check projections at build
   time: `scripts/frame_check.py` in Blender, `scripts/project_nobpy.py`
   before any geometry exists. A changed camera height or lens silently moves
   every anchor.
3. Render small first, with one `--res` variable so preview and final share a
   code path (preview preset: `references/eevee.md`, section 1).
4. **Look at the output image.** Exit code 0 routinely accompanies a black
   frame, a white frame, or a camera aimed at nothing. A few KB where detail
   was expected means blank or blown out, but a plausible size proves nothing,
   and comparing two files' sizes or bytes misleads; diff pixels.
5. Change one thing, re-render, compare. Resolution will not fix a wrong look
   or framing, so get those right small. Shadow-map detail, glare size and
   thin detail all change with final pixels, so before accepting a preview
   check them at final resolution, on a border crop if the frame is large
   (`references/diagnosis.md`, A detail is missing; `references/eevee.md`,
   sections 5 and 9).
6. Expose tuning values as `--` arguments and sweep them in a shell loop;
   gate expensive stages behind an integer `--stage` flag.

Diagnostic views: view transform `'Standard'` (raw values) and `'False Color'`
(exposure). Broken-output triage: `references/diagnosis.md`.

## Traps, in the order a build meets them

Each: the fact, then the check. Techniques live in the references; one project's values in `projects/`.

**Scaffold.** `read_factory_settings(use_empty=True)` leaves **no world
datablock**, so the scene renders far darker and reads as a lighting bug.
`clip_end` silently drops everything past it; with a finite ground plane the
binding distance is the ground's far CORNER, not the farthest object
(`references/scene-code.md`). *Check:* `scene.world` is not None;
`cam.data.clip_end` clears the far corner.

**Camera.** `to_track_quat('-Z','Y')` returns a garbage roll when the aim is
just off vertical (a float32 collapse). Aim exactly vertical or tilt clearly
off it; never "almost straight down" (the band: `references/api.md`, Camera
aiming). *Check:* frame_check anchors land within tolerance.

**Lighting.** Two EEVEE defaults silently cap a dark scene: `light_threshold`
culls dim lamps with distance, and `clamp_surface_indirect` caps reflected
emitters (`references/eevee.md`, section 7). *Check:* a dim or distant lamp
that contributes nothing: test the threshold before moving the lamp.

**Emission.** In EEVEE emissive meshes are not light sources: with
`use_raytracing` False (the default) they light nothing, with it on only while
visible in frame, and they never scatter into fog. Under AgX high strength
whitens the core, more on large emissive areas than thin strokes. Technique
for an emitter that must illuminate, and tuning strength
by eye: `references/eevee.md`, section 8; shadow-casting lamps, not lamp count,
limit a crowd (section 5). *Check:* the brightest coloured element's core; if
it went white and that was not the intent, come back down. Under Standard the
failure is a hue shift, so check the worst channel.

**Volumetrics.** **A world volume zeroes Sun light** (tested at densities 0.0005
and 0.02, no error): with a Sun, put haze in a bounded volume box. Froxel VRAM is
pixels / tile squared x slices, so fine tiles at 8K exhaust the card. Slices vs
tiles, and density by scene size: `references/eevee.md`, section 6.

**Compositor.** A `compositing_node_group` that is not completely wired when
the render starts renders **pure white with no error**; assigning it early and
wiring it before rendering is fine. The render source is
`CompositorNodeRLayers` with `rl.scene = scene`, never a `NodeGroupInput`.
*Check (bisect):* set `compositing_node_group = None` and re-render.

**Shadows.** "Shadow buffer full" prints as an `Error:` line every frame **and
the render still completes**, with shadows missing. Demand scales with
on-screen pixels, so a clean draft does not clear the final. Turning a lamp's
shadow off (`light.data.use_shadow = False`) also stops it being occluded, so
it leaks through walls. Fixes that worked: `references/eevee.md`, section 5.
*Check:* grep stdout for `Shadow buffer full`, only where stdout is captured;
a box that prints no console logs zero lines while overflowing
(`references/pipeline.md`, Remote and helper renders).

**Render and verify.** Blender floods stdout: prefix your diagnostics
`### KEY: value` and grep `^###|Error|Traceback`, excluding Shadow buffer full
lines, which can number thousands (`references/api.md`, Logging). Kill a stuck
render by PID, not by name; another render may be running.

## Where to look, by moment

| You are about to / you are seeing | Read |
|---|---|
| write any bpy; `AttributeError`/`TypeError` from a renamed property, engine id, probe type or node option; Vignette or Film Grain "missing"; build the compositor or glare graph; CLI flags, headless runs, GPU backend; Cycles ignored the GPU; a Nodes modifier input; faces white after appending a material; a packed image gone after reload; aim or roll a camera; `action.fcurves` raises or a driver will not update; introspect an API | `references/api.md` |
| samples or a preset; EEVEE or Cycles; raytracing; shadow pool and caps; volumetric slices, tiles, density, god-rays; `light_threshold` and clamps; light linking; emission strength, proxy lights, a crowd of lamps (section 5); glare recipes; AgX and view transforms; 8K, VRAM, formats, passes; what a large scene's time went on | `references/eevee.md` (index at top) |
| "my render came out white / black / no fog / fog flattens / no glow / washed out / hot dots on glass / shadows missing / light leaking / detail missing / reflections missing / banding or flicker in fog / a knob does nothing / silent or crashed / render is slow" | `references/diagnosis.md` |
| scaffold, sweeps, split sky, ramped fog, mesh winding, batching or instancing crowds, crowd motion, decimating assets, backlit cut panels, LOD and re-scatter, bevels, variation, dark or wet materials, carving, a geometry check | `references/scene-code.md` (index at top) |
| motion blur too heavy or light after a fps change; a keyframed or baked camera path; Follow Path or Track To; camera shake; noise crawling between frames; a day to night crossfade; a walking rigged person | `references/animation.md` |
| a dome master or fisheye camera; the circle does not fill or is cropped; equisolid vs equidistant (Cycles PANO) | `references/dome-master.md` |
| split build from render; render named cameras; batch shots; cache assets; linked libraries; a no-render framing or logic proof; a .blend you did not write; a render queue; render or resume an animation; a laptop or overnight queue that died; quote render time; render on a second machine; per-shot culled files; review motion; encode the final video, frame count off, the wrong frame rate came out, banding after encode | `references/pipeline.md` (index at top) |
| your own project case notes | `projects/` |
| your own delivery formats and machine rules | `house/` |
| prove silhouettes | run `scripts/silhouette_proof.py` (renders) |
| something may stand in front of an anchor (a tower blocking a camera, a landmark hidden behind a ridge) | `scripts/frame_check.py`, `check_occlusion` (no render; ray-casts camera to each anchor) |
| check this skill's snippets and scripts | `python -I scripts/check_snippets.py --keep-going` (add `--no-render` for a quick check that skips the render demos). Host-side driver; passed to Blender's `--python` its argparse eats Blender's argv |
| check for a value repeated across files | `python -I ../maintaining-skills/scripts/check_values.py` (needs the maintaining-skills skill installed beside this one) |

## Depositing findings (intake)

When a session verifies something non-obvious (an API fact, a measured
behaviour, a trap, a technique that worked), append it to `INTAKE.md` in this
directory before the session ends:

```
## 2026-10-27 | fact | proposed home: references/api.md
<one-paragraph claim, how it was verified, exact version, which project>
```

Do not edit reference files mid-task; the merge pass (`maintaining-skills`)
places entries, keeps one home per fact, and deletes duplicates.
