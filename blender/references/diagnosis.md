# Diagnosis: a render is wrong

Start here when a render is wrong. One symptom, one decisive test, one fix. Deep settings live in eevee.md; API facts in api.md.

## Render came out pure white

Two causes have been observed (items 1 and 2, OBSERVED(triangle-battle)); the rest are checks to rule out. Check in this order.

1. **Compositing node group is incomplete at render time.** A `scene.compositing_node_group` whose graph is not fully wired when the render starts renders pure white with no error and no warning. Assigning the group early in a script and wiring it before rendering is fine (api.md, The compositor moved off `scene.node_tree`).
2. **Group Input used as a passthrough.** Group Input -> Group Output renders pure white; the source must be `CompositorNodeRLayers` (api.md, Trap: an empty or unwired group renders PURE WHITE).
3. **Emission blowout.** Not a bug, a different white problem. Under AgX a high emission strength drives the core toward white, reaching it first on a high-luminance colour such as the teal ladder (measured core saturation and that ladder: eevee.md, Color management and Emission; saturated hues stay off white longer: the `art-direction` skill, composition.md, section 6). Workable strengths: eevee.md, Emission.
4. **`use_compositing` is off.** Set `scene.render.use_compositing = True`.
5. **Faces on an empty material slot.** After `new_from_object` on a Boolean result (api.md, Material slots and vectors that surprise).
6. **Wrong or missing glare option values.** Glare options are input sockets, and an invalid menu string raises `TypeError` rather than rendering white, so this one is loud. Mentioned only to rule it out (valid strings: api.md, Compositor migration, glare sockets and node menu items).

Fast bisect: set `scene.compositing_node_group = None` and re-render. If the image returns, the problem is in the compositor graph. If it stays white, look at emission and lighting.

## Render black or far darker than expected

A black frame has a short cause list; check in this order. Decisive first test: print `scene.camera`, `scene.world` and the light count before reading anything else.

1. **No light reaches the surfaces.** A scene lit only by emissive meshes is black with raytracing off, the default (Emission glows but lights nothing, below).
2. **`scene.camera` is unset.** The render has no viewpoint.
3. **View transform.** Re-render with `'Standard'` to see raw values before suspecting the lights.
4. **No world datablock.** The empty-scene reset leaves none, so the scene renders far darker (scene-code.md, Scene scaffold). Check `scene.world`.
5. **Fog so dense it buries the camera.** Density test: Fog is not showing up, below.
6. **A Sun light plus a world volume.** Decisive test: disconnect the World's Volume output and re-render. If the image returns, move the haze into a bounded volume box (eevee.md, Volumetrics, the sun trap).

An unwired compositor does not render black; it renders white (Render came out pure white).

## Fog is not showing up

Two different failures look identical, so separate them first.

**Decisive test:** render the same frame at an absurd density (0.25) and at 0.0, then compare the pixels. Do not compare the files: Blender stamps File, Date, Time and RenderTime metadata into every PNG, so two identical renders are pixel-equal but never byte-equal, and `cmp` always reports a difference [TESTED 2026-11-03, 5.2.0].

```python
import bpy
import numpy as np

def max_pixel_diff(path_a, path_b):
    """Largest absolute per-channel difference between two renders of the same size (0.0 = pixel-identical)."""
    flat = []
    for path in (path_a, path_b):
        img = bpy.data.images.load(path)
        a = np.empty(len(img.pixels), dtype=np.float32)
        img.pixels.foreach_get(a)
        flat.append(a)
        bpy.data.images.remove(img)
    assert flat[0].shape == flat[1].shape, "renders differ in size"
    return float(np.abs(flat[0] - flat[1]).max())

# print("### FOG_DIFF:", max_pixel_diff("frame_density_0.25.png", "frame_density_0.0.png"))
```

- Max diff 0.0 (or one 8-bit step, about 0.004): the volume is not rendering at all. Look at the volume object, its material, and the volumetrics settings.
- Larger diff: the volume renders fine and **nothing is lighting it**. In the verified case the lights were too weak and too far away. Add or move real lamps (eevee.md, Emission, Proxy lights).

If the volume renders and is lit but the look is wrong, density is the next suspect; the starting range is owned by eevee.md (Volumetrics, Getting clean god-rays and haze). A density far too high buries the camera in opaque fog and the frame goes black.

## Fog flattens the image instead of adding depth

Fog close to the camera lowers contrast without suggesting distance. Decisive test: if the nearest objects lose as much contrast as the far ones, the density is uniform along the view axis. Atmospheric perspective belongs on distant things.

Fix: multiply the density by a distance ramp so it starts near zero at the camera and climbs with depth. Also multiply by a height ramp and by a large-scale noise so the fog is layered rather than uniform. Ramped-fog material: scene-code.md.

## One region is washed out and you cannot tell which light

Decisive test: isolate by elimination. Set the big lamps near zero, confirm the region goes dark, then add light back one lamp at a time; the lamp that washes it out shows itself. This is faster than subtracting light from a washed-out frame. HEURISTIC

## Emission glows but lights nothing / no glow in fog

Symptom: the emitter looks right, but the floor and walls beside it stay dark and fog around it shows no glow. The mechanism (emissive meshes are not light sources; `use_raytracing` defaults to False; they never scatter into fog) and its measurements are in eevee.md, section 0, items 1 and 2.

**Decisive test:** add one real lamp beside the emitter and re-render. If the surroundings and the fog respond, this is the cause.

Fix: proxy lights with the emitter's shadow casting off (eevee.md, Proxy lights).

## Shadows missing, or "Shadow buffer full" in the log

The message prints as an `Error:` line every frame and the render still completes, with shadows missing.

**Decisive test:** grep render stdout for `Shadow buffer full`. That only works where stdout is captured: a build that prints no console logs zero lines even while overflowing, so judge from the image there (pipeline.md, Remote and helper renders). A draft can be clean while the final overflows (eevee.md, section 5, worked case).

Fix: raise each lamp's `shadow_maximum_resolution` first (a larger value is a coarser shadow map and fewer tiles). The variant table, the shadow-off caveat and the resolution scaling are owned by eevee.md, Shadows (Shadow buffer full at 8K). A shadow-off lamp shines through walls: see the next entry.

## Coloured light lands where it should not reach

Symptom: a lamp's colour shows on an object that a wall, cover or panel should hide it from, such as an interior light tinting a tree outside a dome. OBSERVED(festival-scene). Decisive test: check `light.use_shadow` on the lamps of that colour; a lamp with shadows off is not occluded by anything. Fix: turn its shadow back on, or move the lamp so nothing is meant to block it (eevee.md, Shadows, Shadows are occlusion).

## A render is slower than expected

Decisive test: at fixed samples, time the same still with one category hidden at a time (all trees, all shadow casting, all volumes) and compare seconds; the category whose removal moves the time is the cost. Toggle on one fixed frame and view, never by comparing different frames of a moving shot: the view changes along with the thing you meant to test. One kit concluded shadow overflow was harmless from frames that happened to sit in a camera whip, and the test decided nothing (OBSERVED(triangle-bashkit)). Note also that an overflowing frame drops shadows, which may make it cheaper, so removing the overflow can make it slower. Guessing failed in the festival case: shadows were suspected and polygon count was the cost (eevee.md, Where the time went in a large scene). If time does not change with resolution, suspect geometry before shading. Log each stage before blaming process overhead (pipeline.md, Animation). For many shots of one small file, batch them in one process (pipeline.md, All shots in one process). For a heavy file with per-shot views, cull first (pipeline.md, Per-shot culled files): the render, not the load, was the cost there.

## A detail is missing — or is it just too small?

Before deciding a detail is broken, compute whether it can exist at your preview resolution.

```
pixels_per_degree = image_width_px / horizontal_FOV_degrees
```

Worked case from the project: at 326 m with a 24 mm lens on a 900 px wide preview, a 0.3 m detail covers about **0.5 px** and is invisible. At 8K (7680 wide) the same detail is about 4.7 px and still reads. (full-frame sensor, as in scale.md: `size_px = size_m / distance_m * focal_mm / 36 * width_px`.)

Two consequences:
- Detail sizes written for one camera distance must be rescaled if the camera moves.
- "Missing" at preview size is not evidence of a bug.

**Decisive test:** inspect fine detail with border rendering. Render a small region at full 4K or 8K pixel scale in a few seconds, instead of a whole 8K frame.

```python
import bpy
scene = bpy.context.scene
r = scene.render
r.resolution_x, r.resolution_y = 7680, 4320      # the real target resolution
r.resolution_percentage = 100
r.use_border = True
r.use_crop_to_border = True
r.border_min_x, r.border_max_x = 0.45, 0.55      # 0..1 of full frame
r.border_min_y, r.border_max_y = 0.60, 0.70
```

## Reflections missing, or a reflective surface renders as a flat dark shape

Four causes, one line each. Decisive test: print `scene.eevee.use_raytracing` and `scene.eevee.ray_tracing_method` first.

- `use_raytracing` is False, the default: no reflections at all (eevee.md, section 4, and the emissive consequences in section 0, item 1) [TESTED].
- `ray_tracing_method = 'PROBE'` with no light probes placed: nothing to reflect [TESTED].
- Materials using the Blended render method do not take part in raytracing [DOC limitations page].
- A `PLANE` light probe on the mirror surface with SCREEN tracing: in one synthetic headless test the reflection's mean red fell from 1.00 to 0.12 and the reflected cube was gone, no error; probe placement not ruled out (eevee.md, section 4, Artefacts by method) [TESTED 2026-11-08].

**It will not present as a raytracing problem.** A correct dielectric water material, a correct reflection probe and the whole skyline on screen for screen-space tracing to find still render as a flat dark rectangle, with no error, no warning and a plausible file size. It reads as a material fault, which sends you tuning roughness and IOR, and no value of either can fix it. Check the switch before the material. OBSERVED(triangle-battle)

## Hot dots or flat discs on glass, wet floors or water

They are the lamps themselves. Light `specular_factor` and `transmission_factor` are separate lobes (properties TESTED 5.2.0, 2026-11-05). Set them per surface and per camera [OBSERVED(triangle-bashkit)]:

- Lamps behind glass need both at 0, or each point lamp shows as a bright disc through raytraced refraction.
- Lamp specular well below its default still drew blobs in polished floors; step it down until they go.
- Suns burn flat panes white: lower specular and transmission on suns, with soft DISK area lamps for sheen.
- A sun with a wide angle mirrors as a broad hot patch on wet ground, so zero it for low wet cameras. Cutting sun specular too far on stone removed its form, because that albedo reads mostly through specular.

## Volume artefacts

Symptom table for fog and light shafts. Levers and measured values: eevee.md, Volumetrics.

| Symptom | Cause | Fix |
|---|---|---|
| Banding / depth slicing in shafts | too few slices | raise slices, then distribution (eevee.md, Volumetrics) |
| Blocky shaft edges | tile too coarse | finer tile, watching VRAM (eevee.md, Volumetrics, Cost at 8K) |
| Flicker / grain in fog | low TAA, bright lights | more TAA samples; `volumetric_light_clamp`, `clamp_volume_*` (eevee.md, Sampling and noise) |
| Haze starts abruptly at camera | `volumetric_start` too high with custom range | lower start |
| Volume vanishes at distance | custom range `volumetric_end` too short, or none and sparse slices | extend end; the auto range gave identical horizon brightness for walls at 30, 300 and 1500 m, so it is generous [TESTED], one scene |
| Fog not in reflections | single-scatter, camera-ray only | known limitation [DOC limitations page] |
| Glow missing around emitters | emission does not scatter | Emission glows but lights nothing / no glow in fog, above |
| Sky turns flat navy or mid purple inside a haze box | the box scatters the world | near black volume Color (eevee.md, Volumetrics, Haze boxes scatter the world) |
| Dot grid or banding in dark sky, on a sheet | can be the viewer, not the render (one case) | check first, below |

**Check a crop before chasing banding or a grid.** An image viewer posterises dark gradients when a large sheet is shrunk while the PNG is clean. One review's banding on a sheet may be the same artefact (not checked). Separately, a dot grid seen in a dark sky on one kit drove the volumetric tile finer, which multiplies the froxel columns; autocorrelation at short lags on the sky of later frames then showed no periodic pattern, so the grid was never confirmed in a render. Run that test on the PNG first, and drop an expensive setting once the problem that justified it is gone: the finer tile stayed on after this result. OBSERVED(triangle-bashkit).

## A knob appears to do nothing

A sweep that moves the image not at all is far more often a mis-aimed measurement than a dead feature. A render measurement is only as good as the pixel it samples, and a confident number from the wrong pixel is worse than no number.

OBSERVED(triangle-battle), and it cost a wrong conclusion about the renderer plus a workaround built on top of it. A sky-brightness knob was measured on a patch "just above the horizon" and looked completely dead across a wide sweep, which produced the claim that EEVEE ignores the world's Light Path "Is Camera Ray" split, and an emissive sky dome to replace it. Both were wrong. The far terrain rose above the camera, so the ground was seen from below and its surface filled the frame above the nominal horizon line, the far edge projecting lower than the near crest. The patch was lying on unlit terrain. Sampled slightly higher, on actual sky, the knob responded cleanly and monotonically (the working split sky: scene-code.md, The split sky).

**Decisive test:** before trusting any measured patch, project the geometry that could occupy it, or render the patch as a crop and look at it. Suspect the measurement before the renderer.

**Dimming a see-through emissive panel can also appear to do nothing.** Under Standard a modest linear value shows far brighter on screen, and see-through panels stack front and back emission, so a dimmed panel barely changed. To make a large panel area dark, scale it down by an order of magnitude or more, not a small step. For an even mid value use opaque holes. Measured by display percentile on frames, OBSERVED(triangle-bashkit).

## The run was silent, crashed, or lied

Exit code 0 proves nothing. Check each row; the commands are in api.md, Headless rendering from the command line.

| Check | How |
|---|---|
| Python error | exit code under `--python-exit-code 1`, plus a `Traceback` grep |
| Blender-level problems | scan stdout for `Error:` lines, excluding "Shadow buffer full", which prints as `Error:` on every frame while the render completes and can number thousands (api.md, Logging) |
| Output exists and is sane | `os.path.exists`, then size, then **look** at a downscaled copy. A detailed 8K PNG16 is about 100 MB; a few KB means black or blank |
| GPU/driver reset or OOM | process dies, truncated log, no output file. Reduce VRAM (tile size, slices, resolution) and retry; watch `nvidia-smi --query-gpu=memory.used` |
| Wrong backend/GPU | print `gpu.platform.renderer_get()` after `gpu.init()` |
| Crash or silent stall in `BM_mesh_bevel` (EXCEPTION_ACCESS_VIOLATION, stack in `blender.crash.txt`) | a script-built loft collapsed to near zero radius, leaving a degenerate island after `dissolve_degenerate`. Bisect islands in child processes and guard lofts against zero radius; bevel on boolean output was not the cause. OBSERVED(triangle-bashkit), one mesh |
| Log gone after a death | stdout piped to grep dies with the run; redirect to a file |
| Output vanished with no error | a relative output path; pass absolute paths |

File size is a one-way signal (SKILL.md, The loop, step 4); open the image and look.

## Faces shade wrong / volume will not scatter

Box geometry from `from_pydata` with careless winding gives inward-facing normals. They shade wrong and can stop volume objects from scattering, with no error message. Check winding first. Decisive test: rebuild the mesh with the outward winding from scene-code.md, Hand-built meshes: face winding, and re-render; if shading or scattering returns, winding was the cause.

## A personality/detail system "does not work"

Scope: pipelines where full detail is gated behind a near-distance LOD check. If the camera sits beyond that threshold, none of the detail renders and the crowd silently reverts to bare outlines. Decisive test: verify that your nearest unit is actually inside the LOD 0 band before concluding the system failed.
