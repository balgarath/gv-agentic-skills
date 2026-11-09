# EEVEE technical reference (Blender 5.2 LTS, headless bpy)

The measurement of record for getting high-quality stills out of EEVEE by script on **Blender 5.2.0 LTS, Windows**, engine id `BLENDER_EEVEE`: settings, quality numbers and how they were made. It deliberately holds no API renames, CLI or introspection (api.md) and no symptom triage (diagnosis.md).

## Index (section, then the moment you need it)

| Section | Open it when |
|---|---|
| 0 Read this first | emitters light nothing, fog has no glow, a proxy lamp does nothing, dim lamps vanish, hot cores go white, 8K limits |
| 1 Quick presets | you want a preview or an 8K final starting point |
| 2 EEVEE vs Legacy vs Cycles | choosing the engine; what EEVEE still cannot do |
| 3 Sampling and noise | how many samples; noise from RT, shadows, Fast GI; the first frame is slow (shader compile) |
| 4 Raytracing | reflections missing, method choice, artefacts, glass recipes, reflecting what is out of frame |
| 5 Shadows | Shadow buffer full, missing shadows, draft and final disagree on shadow patterns, light leaking |
| 6 Volumetrics | fog density by scene size, god-rays, slices vs tiles, VRAM, a Sun with a world volume, haze boxes |
| 7 Light linking, groups, clamping | `light_threshold`, `clamp_surface_indirect`, light linking, light groups in EEVEE |
| 8 Emission and glow | emission strength by area, tuning by eye, night ratios, proxy lights, glow in fog, coloured window light |
| 9 Compositor glow recipes | glare chains that looked right, glare size vs resolution, re-compositing from EXR |
| 10 Color management | view transforms, AgX desaturating bright emitters, saturated purple going pink |
| 11 High-resolution strategy | 8K timing and VRAM, overscan and off-frame glow, output formats, passes, AA |
| 12 Performance knobs | which knob costs time, preview vs final values, where a large scene's time went, Cycles timings |
| 13, 14 | how the test numbers were made; sources |

## How to read the evidence tags

The tags are defined once, in the `maintaining-skills` skill (Provenance tags). In this file **[TESTED]** means run on one laptop: Blender 5.2.0 LTS (hash fbe6228777e7), Windows 11, RTX 4090 Laptop 16 GB, driver 546.92, OpenGL backend; numbers in the appendix. Notation local to this file: **(Blender X+)** is a version gate, and **(Legacy only, does not apply)** marks EEVEE <= 4.1 advice that is wrong now.

Caveats on **[TESTED]** numbers: the GPU was shared with another Blender render during some runs, so
wall-clock times are approximate; quality/RMSE/pixel numbers are not affected. Test scenes are small
(960x540 unless stated) and synthetic: a dark glossy floor, a dim back wall, five thin emissive
cylinders (cyan, magenta, orange, green, violet). Treat trends as reliable and exact values as
scene-specific.

## 0. Read this first (the findings that change how you build)

1. **Emissive geometry lights nothing unless Raytracing is ON, and then only through the screen.**
   With `use_raytracing=False` (the default) five bright neon tubes lit no floor or wall and made no
   reflections. With it on, only emitter pixels *visible in the frame* contribute; an emitter just
   outside the frame gives ~0 under every method [TESTED], except coarsely through a Sphere probe with
   the `PROBE` method (section 8, Other routes). Visible thin tubes bounce weakly (about 1/4 to 1/3 of
   Cycles on the floor, ~zero on a distant wall) [TESTED]; no light sampling of emissive meshes is the
   inferred reason. Plan on **proxy lights** for any emitter that must illuminate (section 8).
2. **Emissive meshes never scatter into volumetric fog.** Only Light objects feed froxel scattering:
   fog + neon tubes with no lights gave a wall patch of 0.0003, identical to no emitters [TESTED].
   Haze glow needs proxy lights or emission-shader volume shells.
3. **A proxy light inside its own emitter mesh is fully self-shadowed** (4 lights per tube at
   20-4000 W changed the image by <1%). Set `emitter.visible_shadow = False` [TESTED].
4. **`light_threshold` (default 0.01) culls dim lights at distance.** A 20 W proxy lit a wall 6 m
   away at 0.0005 with the default and 0.0175 with 0.001 (35x). Lower it, or use per-light
   `use_custom_distance` [TESTED].
5. **Glow comes from compositor Glare, real lights in haze, and emission-shader volume shells.**
   `scene.eevee` has no bloom property in 5.2 (api.md, There is NO bloom property; Glare node: api.md).
6. **AgX/ACES/Khronos all push a hot emissive core to near-white; the compositor cannot fix it.**
   Mean core saturation falls with strength under every filmic transform (table: section 10);
   saturation boosts or the *Punchy* look before the view transform barely moved the core [TESTED]. Workable strength depends on emissive
   AREA (Emission below); carry brightness with Glare, lights and haze.
7. **The default `clamp_surface_indirect` silently caps reflections of bright emitters.** Numbers and
   the fix: section 7.
8. **Headless EEVEE works on Windows with a GPU and a desktop session** in background mode, on OpenGL
   (default) and Vulkan, compositor included [TESTED]. The manual calls it unsupported on *headless
   Windows systems* (no desktop session) [DOC limitations page]. Invocation, backends and exit codes:
   api.md, Headless rendering from the command line.
9. **At 8K, VRAM and the shadow pool are the limits, not time.** 8K volumetrics at tile 4 + 128
   samples peaked at ~15.9 GB of a 16 GB card; 20 point lights at 8K overflowed the shadow pool
   (fix and its scope: section 5) [TESTED].
10. **`Bloom` at Glare defaults washes the frame.** With emitters >1 it raised mean image brightness
    6x (0.035 to 0.208) [TESTED]. A fresh node does not default to Bloom (api.md, Glare node table).
    Two stacked `Fog Glow` nodes worked on that scene; clipped neon on true black: section 9.

## 1. Quick presets

Both blocks run clean on 5.2.0 (rendered in a harness) [TESTED]. Enum-valued properties take
**strings** (`'4'`, `'512'`), numeric ones take numbers. Put your scene-building code before them.

### 1a. Preview preset (about 1-4 s per 960x540 frame on simple test scenes, one machine)

`scripts/scene_template.py` copies this block; change both together. `scripts/check_snippets.py` fails if they drift (its PRESET check diffs every assignment except the two resolution lines).

```python
import bpy
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'            # 5.x id. BLENDER_EEVEE_NEXT existed only in 4.2-4.5
ev = sc.eevee
ro = ev.ray_tracing_options

sc.render.resolution_x, sc.render.resolution_y = 1920, 1080
sc.render.resolution_percentage = 50          # 960x540 working size
sc.render.filter_size = 1.5                   # pixel filter, default

ev.taa_render_samples = 16                    # enough to judge composition and lighting; some noise left
ev.use_raytracing = True                      # the default is False: section 0, item 1
ev.ray_tracing_method = 'SCREEN'              # 'PROBE' only sees light-probe spheres/planes
ro.resolution_scale = '4'                     # trace at 1/4 res (valid '1','2','4','8','16')
ro.use_denoise = True; ro.denoise_spatial = True; ro.denoise_temporal = True; ro.denoise_bilateral = True
ro.screen_trace_quality = 0.25                # "precision" (default)
ro.screen_trace_thickness = 0.1               # raise to 0.3-1.0 if thin emitters/reflections are missed
ro.trace_max_roughness = 0.5                  # rougher BSDFs use Fast GI instead of traced rays
ev.use_fast_gi = True
ev.fast_gi_method = 'GLOBAL_ILLUMINATION'     # 'AMBIENT_OCCLUSION_ONLY' = cheaper, no bounce light
ev.fast_gi_resolution = '4'
ev.fast_gi_ray_count = 1
ev.fast_gi_step_count = 4

ev.use_shadows = True
ev.shadow_ray_count = 1
ev.shadow_step_count = 2
ev.shadow_resolution_scale = 0.5
ev.shadow_pool_size = '512'

ev.volumetric_tile_size = '16'                # coarse froxels (valid '1','2','4','8','16')
ev.volumetric_samples = 32                    # depth slices
ev.volumetric_sample_distribution = 0.8
ev.use_volumetric_shadows = False             # expensive

ev.clamp_surface_direct = 0.0                 # 0 = clamp off
ev.clamp_surface_indirect = 10.0              # the default; section 7
ev.use_overscan = False
sc.render.use_motion_blur = False
```

### 1b. Final-quality preset (8K, 16-bit EXR)

```python
import bpy
sc = bpy.context.scene
sc.render.engine = 'BLENDER_EEVEE'
ev = sc.eevee
ro = ev.ray_tracing_options

sc.render.resolution_x, sc.render.resolution_y = 7680, 4320
sc.render.resolution_percentage = 100
sc.render.filter_size = 1.5                    # default; 1.0 is crisper but aliases more

ev.taa_render_samples = 128                    # RMSE plateau 128-256 in the section 3 sweep; 64 is the floor for finals
ev.use_raytracing = True
ev.ray_tracing_method = 'SCREEN'
ro.resolution_scale = '2'                      # half-res tracing (4K rays at 8K); '1' = full res, costlier
ro.use_denoise = True; ro.denoise_spatial = True; ro.denoise_temporal = True; ro.denoise_bilateral = True
ro.screen_trace_quality = 0.25                 # raise to 0.5 only if you see missed hits/stepping
ro.screen_trace_thickness = 0.1                # tune per scene
ro.trace_max_roughness = 0.5
ev.use_fast_gi = True
ev.fast_gi_method = 'GLOBAL_ILLUMINATION'
ev.fast_gi_resolution = '2'
ev.fast_gi_ray_count = 2                       # the defaults (rays 2, steps 8)
ev.fast_gi_step_count = 8

ev.use_shadows = True
ev.shadow_ray_count = 1                        # TAA averages rays across samples; 2-4 made no measurable difference here
ev.shadow_step_count = 6                       # 1 measurably worse, 16 slightly better
ev.shadow_resolution_scale = 1.0
ev.shadow_pool_size = '512'                    # per-light shadow_maximum_resolution is the measured fix; see Shadows
ev.light_threshold = 0.01                      # lower to 0.001 if dim/proxy lights vanish at distance

ev.volumetric_tile_size = '8'                  # tile 4 at 8K hit ~16 GB VRAM
ev.volumetric_samples = 128
ev.volumetric_sample_distribution = 0.8
ev.use_volumetric_shadows = False              # only if solid objects must darken the fog
ev.volumetric_shadow_samples = 16
ev.volumetric_light_clamp = 0.0
ev.clamp_volume_direct = 0.0; ev.clamp_volume_indirect = 0.0

ev.clamp_surface_direct = 0.0
ev.clamp_surface_indirect = 0.0                # off; why: section 7
ev.use_overscan = True
ev.overscan_size = 10.0                        # percent; screen-space RT/GI sees a little outside the frame

sc.render.use_motion_blur = False
sc.render.image_settings.file_format = 'OPEN_EXR'
sc.render.image_settings.color_mode = 'RGBA'
sc.render.image_settings.color_depth = '16'    # half float = EEVEE's native precision
sc.render.image_settings.exr_codec = 'ZIP'
```

Then, per light with the pool problem, raise `light.shadow_maximum_resolution` (a coarser shadow map; values and their scope: section 5).

## 2. EEVEE Next vs Legacy vs Cycles

### What changed in the rewrite (Blender 4.2 LTS, July 2024) [DOC release_notes/4.2 eevee]
Sources: https://developer.blender.org/docs/release_notes/4.2/eevee/ and
https://developer.blender.org/docs/release_notes/4.2/eevee_migration/

| Area | EEVEE Legacy (<= 4.1) | EEVEE rewrite (4.2+, id `BLENDER_EEVEE` from 5.0) |
|---|---|---|
| GI | Baked irradiance volumes + cubemaps, SSR | Screen-space raytracing for every BSDF, Fast GI approximation (horizon-scan style), baked **Light Probe Volumes** (object-level data), dynamic sphere probes |
| Shadows | Cube/cascade maps, soft-shadow toggle, contact shadows | **Virtual shadow maps** + **shadow map raytracing**; biases automatic; contact shadows removed; per-light *Jitter* replaces global soft shadows |
| Bloom | Render-panel Bloom | **Removed.** Use compositor Glare (Legacy only, does not apply) |
| Volumes | Froxels, "Volumetric Lighting" toggle, world volume clipped to clip distance | Froxels, accurate mesh intersection, dithered lighting to reduce flicker (a world volume and Suns: section 6) |
| Lights | Limits on count | No count limit (4096 visible at once) |
| Materials | `Blend Mode`, SSR refraction | `Render Method` Dithered or Blended; Raytraced Transmission; Thickness output |
| Light/shadow linking | Not available | Added in 4.3 [DOC](https://developer.blender.org/docs/release_notes/4.3/eevee/) |
| Backend | OpenGL only | OpenGL default; Vulkan experimental 4.3, on par in 4.5, usable in 5.2 [TESTED] |

5.x timeline [DOC, release_notes/5.0, 5.1, 5.2 /eevee]: 5.0 renamed the engine id to `BLENDER_EEVEE`
and made the compositor tree its own datablock; 5.1 added *Direct/Indirect Light Intensity* and the
Raycast node; **5.2** overhauled screen-space raytracing (new `Backface` option, "Far Thickness"
removed from Fast GI, scenes can render darker than 5.1 because of energy-conservation fixes), added
larger shadow pool options (section 5), light camera-ray visibility, faster instancing.

### What it still cannot do well [DOC unless noted; manual "Limitations" page]
- Raytracing uses the **depth buffer**, not geometry: only front-most visible surfaces count; off-screen,
  occluded and blended surfaces are invisible to it. Effects vanish at the frame border
  (`use_overscan` partially mitigates).
- Volumes: **single scattering only**; volumes do not appear in reflections/refractions/probes;
  volumetric shadows only affect other volumes, not solids; only for volumes inside the view frustum.
- Light probe capture treats specular as diffuse; 128 sphere probes, 16 plane probes in frustum.
- Blended materials are incompatible with raytracing; one refraction event only.
- Output is **half-float**; Combined and Light passes clamp negatives to 0.
- Lights have one colour and no node trees; area-light `spread` unsupported; spot `size` does not soften the cone.
- No CPU render, no multi-GPU, not supported on headless Windows systems.

### When to choose which
| Need | Pick |
|---|---|
| Fast iteration, stylised/neon/sci-fi where you control the lights, fog with light shafts, 8K in minutes | **EEVEE** |
| Emissive meshes must light the scene accurately, including off-screen ones | **Cycles** (light-samples emissive meshes; in one test the Cycles floor energy was ~3x EEVEE RT's) |
| Multi-bounce volumetric glow, caustic-ish glass, true multi-scatter | **Cycles** |
| EEVEE look but calibrated lights | EEVEE, with a **low-res Cycles reference** to tune proxy-light power (the 4 W per strength per m2 number in section 8 came from this; a 480x270, 128 spp CPU reference took 6 s) |

Tradeoff: EEVEE is much faster (8K neon frame at 16 samples: 25 s measured, so 128 samples is minutes
by extrapolation; Cycles CPU at 960x540 256 spp took 34-60 s for a scene EEVEE does in under 5 s), paid
for with hand-placed proxy lights and screen-space artefacts. For mostly glowing geometry with haze,
EEVEE plus proxy lights plus Glare matched Cycles' look in one test [TESTED], judged by eye.

## 3. Sampling and noise

`scene.eevee.taa_render_samples` (default 64, min 1) is the final-render temporal AA sample count;
`taa_samples` (default 16) the viewport's (0 = infinite) [DOC sampling page, URL in section 14].
Everything stochastic **accumulates across these samples**: pixel jitter (AA), shadow rays, jittered
shadows, soft-light sampling, volume froxel jitter, raytrace rays, depth-of-field jitter, motion
blur steps. There are no separate "denoise samples" for the main render; noise goes by accumulation plus the raytrace denoiser.

### Measured convergence [TESTED] (neon scene, RT on, soft proxy lights, reference = 1024 spp, 4 shadow rays, 16 steps; RMSE on x/(1+x) tonemapped values, lower is better)

| `taa_render_samples` | 1 | 4 | 16 | 32 | 64 | 128 | 256 | 512 |
|---|---|---|---|---|---|---|---|---|
| RMSE | 0.0345 | 0.0047 | 0.00135 | 0.00091 | 0.00063 | 0.00051 | 0.00048 | 0.00048 |

On this scene: 16 for previews, 64 as the floor for finals, 128 standard, 256 for hard scenes; past
256 nothing was left to gain, and cost is linear (12.99 s at 256 vs 3.06 s at 64). One production
kit's finals ran below 128 and were judged clean by eye (OBSERVED(triangle-bashkit)), so
read this as one scene's curve.

Volumes converge faster than surfaces: in the god-ray scene RMSE vs reference was 0.073 at 1 spp,
0.052 at 4, 0.0496 at 16, 0.0491 at 64 [TESTED]. Slice count, not TAA, was the limiter there (section 6).

### Where noise comes from and what kills it, from the same sweep [TESTED]
| Source | Fix | Evidence |
|---|---|---|
| Raytraced reflections / GI | Keep **`ray_tracing_options.use_denoise` ON**. Spatial reuse is the big one | all denoise off: RMSE 0.0082 vs 0.00063 on (13x). Spatial off alone: 0.0082. Temporal off alone: 0.0033. Bilateral off: 0.00071 (negligible) |
| Soft-shadow sampling | More `taa_render_samples`; `shadow_step_count` up (1 to 6 to 16: 0.00114, 0.00063, 0.00054); per-light `use_shadow_jitter` (0.00056 vs 0.00063) | `shadow_ray_count` 1/2/4: 0.00063/0.00063/0.00062, no gain at 64 spp |
| Fireflies from very bright emitters in glossy reflections | `clamp_surface_indirect` (costs highlights, section 7), more samples | |
| Fast GI noise | `fast_gi_ray_count`, `fast_gi_step_count`, lower `fast_gi_quality` (precision) | per the manual [DOC, page not re-checked]; benefit not measured |

Caveats: (a) the reference used default RT settings, so `resolution_scale` and
`screen_trace_quality` comparisons are biased toward the default (they changed the *result*, not just
the noise); they do not show "higher precision = worse". (b) Changing `shadow_ray_count`/`shadow_step_count`
forces a shader recompile: the first render in a fresh process took 21-27 s instead of 1-3 s.
This is the skill's one home for shader-compile cost. 21-27 s is the cold case (variants not yet in
the local shader cache); the warm case, shaders compiled by an earlier run, was far shorter even in
a much heavier production scene [OBSERVED(festival-scene), 2026-11-01], so compile time tracks how new the variants are more
than scene size. That a disk cache carries shaders between processes is inferred from the two
numbers (UNVERIFIED(2026-11-08), carried from 2026-11-01: needs a cold and a warm render of one new
variant in two processes, on a machine allowed to render). Either way it is per process, so render
every shot of a batch in one process (pipeline.md, All shots in one process).

With raytracing: RT noise is resolved per sample, then accumulated by TAA; the denoiser's *temporal*
mode (re-projects the previous result) removes fireflies but adds colour bias [DOC raytracing page].
With volumetrics: froxel lighting is dithered per sample (4.2+), so low `taa_render_samples` shows
grain in fog; the fix is TAA samples, not tile size.

## 4. Raytracing settings

Panel: Render > Raytracing. Docs: Raytracing page (section 14).

| Python | Values / default (5.2) | Meaning |
|---|---|---|
| `scene.eevee.use_raytracing` | bool, **False** | Off = fast pre-filtered light-probe pipeline: **no screen-space reflections** (emissive consequences: section 0, item 1) [TESTED]. |
| `scene.eevee.ray_tracing_method` | `'SCREEN'` (default), `'PROBE'` | `SCREEN`: trace the depth buffer, fall back to probes when the ray leaves the view. `PROBE`: use only light-probe spheres/planes (cheapest, needs hand-placed probes). |
| `ray_tracing_options.resolution_scale` | `'1','2'(default),'4','8','16'` | Trace resolution divisor. 2 at 8K = 4K rays. |
| `ray_tracing_options.screen_trace_quality` | 0-1, 0.25 | "Precision". Higher = more accurate hits, **shorter max trace distance**, more cost. |
| `ray_tracing_options.screen_trace_thickness` | 0.1 | Assumed thickness of depth-buffer surfaces. Higher catches thin things but stretches reflections and flickers. |
| `ray_tracing_options.use_backface_hit` | True | (5.2) Treat back-face hits as hits; reduces GI light leaking. |
| `ray_tracing_options.backface_radiance_scale` | 0-1, 0.25 | (5.2) How much front-face lighting is reused on back-face hits. |
| `ray_tracing_options.use_denoise` | True | Master denoise switch. |
| `denoise_spatial` / `denoise_temporal` / `denoise_bilateral` | True | Spatial reuse (can leak light across surfaces), temporal accumulation (removes fireflies, adds colour bias), bilateral blur. |
| `ray_tracing_options.trace_max_roughness` | 0-1, 0.5 | BSDFs rougher than this use Fast GI. **1.0 = raytrace everything, Fast GI unused.** |
| `scene.eevee.use_fast_gi` | True | Toggle Fast GI approximation. |
| `fast_gi_method` | `'AMBIENT_OCCLUSION_ONLY'`, `'GLOBAL_ILLUMINATION'` (default) | AO only = fastest, no bounce. |
| `fast_gi_resolution` | `'1','2'(default),'4','8','16'` | |
| `fast_gi_ray_count` 2, `fast_gi_step_count` 8 | | More = less noise. |
| `fast_gi_quality` 0.25 (precision), `fast_gi_distance` 0 (unlimited), `fast_gi_bias` 0.05, `fast_gi_thickness_near` 0.1 | | `fast_gi_thickness_far` was **removed in 5.2** (caused dark halos) [DOC release_notes/5.2 eevee]. |
| `scene.eevee.gi_diffuse_bounces` 3, `gi_cubemap_resolution` '512', `gi_visibility_resolution` '32', `gi_irradiance_pool_size` '16', `gi_glossy_clamp` 0 | | Light-probe pipeline settings. `gi_irradiance_pool_size` is a **volume-probe memory pool** (MB); bump it only if baked volumes do not fit. |

Fast GI does nothing unless raytracing is on (RT off: identical images with Fast GI on or off) [TESTED].

### Artefacts by method
- **SCREEN**: light/reflection pops at the frame border and when an emitter leaves frame; thin objects
  missed unless `screen_trace_thickness` is raised; smearing and flicker at high thickness; leaking
  through thin walls (Backface hit, lower thickness); rays cannot see **behind** the front-most
  surface, so an emitter's *underside* is invisible (in the ortho top-down test an emitter cube lit
  the floor only via its visible top face's pixels; inferred from the geometry, not verified).
- **PROBE**: needs a Sphere probe near the emitter; with one, an off-screen emitter gave a coarse
  contribution (floor 0.05 vs Cycles 0.22) [TESTED]. Without probes: nothing.
- **Denoiser**: spatial reuse leaks light across surfaces; temporal adds colour bias.
- Blended-render-method materials do not take part in raytracing at all [DOC limitations page].
- Shader to RGB blocks raytracing for BSDFs behind it [DOC via Blender issue 119828; UNVERIFIED(2026-11-08) whether the issue is still open: projects.blender.org returned 403 to an automated read on 2026-11-08, so check it by hand].
- Planar probes combined with non-Screen raytracing methods break or skip raytracing [DOC, page not re-checked]. **A `PLANE` probe on a mirror floor removed the object reflection under SCREEN tracing, with no error, in one synthetic test** [TESTED 2026-11-08 on 5.2.0, headless, 480x270, 16 samples, Standard view: 40 m metallic roughness-0 floor at z 0, emissive red 2 m cube above; probe at z 0.001, rotation 0, scale 20 x 20 x 1, other settings default; the reflection's mean red fell from 1.00 without the probe to 0.12 with it, and the reflected cube is gone]. Not ruled out: a wrong orientation or offset for this floor, rather than plane probes breaking reflections in general. A second case lost all object reflections with a plane probe at the water (OBSERVED(triangle-bashkit)). *Check (broken render):* render once with the plane probe hidden; if the reflection returns, drop the probe or fix its placement.

### Reflections from out of frame [OBSERVED(triangle-bashkit)]

Screen tracing sees nothing out of frame, yet a tower wall mirrors what is behind the camera. A Sphere light probe at the tower fixes it: `ob.hide_probe_sphere = True` on the piece so it does not capture its own inside, and `gi_cubemap_resolution` plus `world.probe_resolution` raised until a test render reads sharp. Off-screen neighbours then appear in the glass. In a group shot leave pieces visible to the probe and stand it in open air; with no probe, keep the reflected object in frame.

### Glass: three recipes by job [OBSERVED(triangle-bashkit), tested side by side, property names TESTED 2026-11-05]

| Job | Recipe | Result |
|---|---|---|
| Smoked curtain wall that must mirror neighbours | Mix of Transparent and tinted Glossy, `surface_render_method` DITHERED | needed many more samples than the clear-pane recipe to lose grain |
| Clear panes (shop fronts, a glazed dome) | Principled Transmission 1, DITHERED, `use_raytrace_refraction` True, `thickness_mode` SLAB, a small Value into the material output Thickness socket, a low IOR, no roughness | clean at far fewer samples than the dithered mix; little reflection, so neighbours vanish from it |
| Vehicles, where dither read as cork over a lit interior | BLENDED | clean, but takes no raytraced reflections |

Start the clear-pane Thickness small, IOR low and roughness zero, then check the panes in a test render.

- A glass-like IOR shifts what is behind each pane and chops interiors at every strut; slight roughness lets the denoiser blur everything behind (hence none in this recipe, where weathered surfaces want some).
- Thickness SPHERE reads as frosted on sheets but bends properly on cast blocks.
- The Principled pane casts an opaque shadow: set `visible_shadow` False on panes or interior lamps stay trapped.
- With backface culling only the near pane shows; `recalc_face_normals` on an open skin left front panes facing in, so they culled away. Set normals by hand.

## 5. Shadows

Docs: Light settings and Sampling pages (section 14).

EEVEE uses **Virtual Shadow Maps** (resolution only where needed, cached) plus **Shadow Map
Raytracing** for soft shadows [DOC light_settings page]. Light radius is the softness control.

| Setting | Property | Default | Notes |
|---|---|---|---|
| Shadows on/off | `scene.eevee.use_shadows` | True | |
| Rays per light | `shadow_ray_count` | 1 (range 1-4) | Reduces random-sampling noise. No measurable gain at 64 spp [TESTED]. |
| Steps per ray | `shadow_step_count` | 6 (1-16) | More = softer shadows, costlier. Fewer steps reduces leaking from overlapping casters [DOC, page not re-checked]. 1 was clearly worse [TESTED]. |
| Resolution scale | `shadow_resolution_scale` | 1.0 | Global shadow-map resolution percentage. |
| Pool size | `shadow_pool_size` | `'512'` | Enum MB: 16 to 2048 (16, 32, 64, 128, 256, 512, 1024, 1536, 2048; TESTED 2026-11-03 on 5.2.0; 1536 and 2048 are new in 5.2 [DOC release_notes/5.2 eevee]). The "Shadow buffer full (A / B)" message counts tiles: 512 -> 2048, 2048 -> 8192 [TESTED]. |
| Jitter (global, viewport) | `use_shadow_jitter_viewport` | False | Jitter is always on in final renders **if the light has it enabled**. |
| Light threshold | `light_threshold` | 0.01 | Lights below this intensity are culled with distance; see section 7. |
| Light radius | `Light.shadow_soft_size` | 0.0 (point/area default differs by type) | Bigger = softer. Spot `size` softens the shadow, not the cone [DOC light_settings page]. |
| Per-light jitter | `Light.use_shadow_jitter`, `shadow_jitter_overblur` (10) | False | Fixes leaking from large lights; **cannot be cached**, updates every sample, high cost [DOC light_settings page]. |
| Per-light filter | `Light.shadow_filter_radius` | 1.0 | PCF blur; >1 px raises leak risk [DOC light_settings page]. |
| Per-light resolution limit | `Light.shadow_maximum_resolution` | 0.001 | Minimum shadow-map pixel size. **Larger = less memory, coarser shadow, more leaking.** `use_absolute_resolution` makes it a fixed size at 1 unit from the light (not for suns). |
| Cast shadow (object) | `Object.visible_shadow` | True | Replaces legacy material shadow mode. |
| Light casts shadows | `Light.use_shadow` | True | Off removes occlusion too, not just the dark patch: see Shadows are occlusion, below. |
| Shadow terminator (4.5+) | `Object.shadow_terminator_normal_offset` 0, `shadow_terminator_geometry_offset` 0.1, `shadow_terminator_shading_offset` 0 | | Fix self-shadow banding on low-poly [DOC release_notes/4.5 eevee]. |
| Material | `use_backface_culling_shadow`, `use_transparent_shadow` | False, True | Turn transparent shadows off where not needed for speed. |

Removed in 4.2 (Legacy only, does not apply): cube/cascade shadow sizes, `use_soft_shadows`,
contact shadows, shadow bias and clip-start sliders [DOC release_notes/4.2 eevee_migration].

### Artefacts and fixes [DOC light_settings page unless tagged]
| Artefact | Cause | Fix |
|---|---|---|
| Light leaking through thin walls | Thin geometry + shadow-map raytracing | Give the wall thickness; lower `shadow_maximum_resolution`; fewer steps |
| Leaking from big area lights / overlapping casters | Shadow Map Raytracing | Lower `shadow_step_count`, enable per-light Jitter, shrink light radius |
| Self-shadow acne / banding on low-poly | Shading normal vs geometry | `shadow_terminator_*` offsets (4.5+); 4.5 also quantised geometric normals |
| Contact shadows missing | Removed in 4.2 [DOC release_notes/4.2 eevee_migration] | Finer `shadow_maximum_resolution`, small light radius, or Fast GI AO |

**Shadow buffer full at 8K** [TESTED]: 20 point lights (radius 0.06) at 7680x4320 requested 28,396
tiles; pool 512 = 2048 tiles and pool 2048 = 8192 tiles both overflow. The message prints as an
`Error:` line every frame and the render still completes, shadows missing. Check: grep stdout for `Shadow buffer full`.
| Variant | Result |
|---|---|
| default | "Shadow buffer full" x15 |
| pool '2048' | still full; VRAM 7.2 -> 10.1 GB |
| pool '2048' + `shadow_resolution_scale` 0.5 | clean |
| default pool + every light `shadow_maximum_resolution = 0.01` | clean, lowest VRAM of the working fixes (0.01 is this test scene's value, see below) |
| `shadow_resolution_scale` 0.25 | clean |
The same scene at 960x540 also complained at 2,262 / 2,048 tiles with large-radius lights. Shadow demand scales with on-screen pixels, so check at the final resolution.

**Fix:** raise each lamp's `shadow_maximum_resolution` (coarser per-lamp maps). Raising the pool alone still overflowed and cost VRAM; only pool 2048 with `shadow_resolution_scale` 0.5 cleared it that way. The 0.01 and the 0.001-0.01 range are this synthetic 8K scene's; production builds capped lamps coarser (OBSERVED(festival-scene), OBSERVED(archway)). Larger is coarser and leakier, so start from the synthetic range, step up until the message stops, and judge the shadow by eye. Fill or rim lamps with nothing in range meant to block them can take `Light.use_shadow = False`, but then nothing occludes them (next section).

**Worked case: draft and final disagree** [OBSERVED(archway), 2026-11-06; cause UNVERIFIED(2026-11-08)]. Point lamps behind backlit cut panels: a small draft showed every lamp's projected pattern on the ground, the high-resolution final kept one. A CPU ray check (lamp to ground through the alpha mask, no renderer) reproduced the draft, so the final lost shadow detail. Inferred cause: pool overflow at the final size; no log confirmed it. Raising the lamps' `shadow_maximum_resolution` fixed it. A passing draft does not clear the final for shadow detail; check at the final resolution.

**Many lamps** [OBSERVED(triangle-bashkit)]. One kit cleared the pool scene by scene with per-lamp values spanning two orders of magnitude, and on the busiest scenes by turning shadows off on the small point lamps, leaving a minority casting (one scene's value each, tune by eye). So a crowd is limited by **shadow-casting** lamps on screen, not lamp count (no count limit: section 2), at the price of leaking, which that kit accepted for speed (next section). Overflow is view dependent at one lamp set: on one merged city the same lamps overflowed on most cameras and not the rest; across later video shots with similar casting counts, street-level views overflowed and others did not, and excess tile demand tracked frame time better than tris or lamp count, with causation not separated from view type. Check overflow on every camera. An earlier "overflow costs nothing" reading came from a confounded test (diagnosis.md, A render is slower than expected).

### Shadows are occlusion, and often not the cost [OBSERVED(festival-scene), 2026-11-01]
- **A light with its shadow off passes through everything.** An interior dome light with
  `use_shadow = False` leaked its colour through the dome cover onto a tree outside. Shadow-off suits
  lights with nothing in range meant to block them (true fill or rim). Symptom entry: diagnosis.md,
  Coloured light lands where it should not reach.
- **Shadow-off as a speed fix gave little** there: the remaining casters were the pattern-projecting
  lamps whose shadows are the image, and the decimated trees were already `visible_shadow = False`.
  Measure before assuming shadows are the budget (section 12, Where the time went in a large scene).

## 6. Volumetrics

Docs: Volumes page (section 14).

EEVEE evaluates every volume in the view frustum into **froxel** 3D textures (high VRAM): XY cells =
render resolution / tile size, Z slices = `volumetric_samples`, distributed along view depth.

| Python | Default / range | Meaning and advice |
|---|---|---|
| `volumetric_tile_size` | `'8'`; `'1','2','4','8','16'` | Pixels per froxel cell (UI "Resolution"). Smaller = sharper shafts, **memory scales with 1/tile^2**. |
| `volumetric_samples` | 64; 1-256 | Depth slices (UI "Steps"). |
| `volumetric_sample_distribution` | 0.8; 0-1 | 0 = linear, 1 = exponential: more slices near the camera. |
| `use_volume_custom_range`, `volumetric_start` 0.1, `volumetric_end` 100 | False | Normally range is automatic. Enable for **world volumes** or many volume objects to concentrate slices [DOC, page not re-checked]. |
| `volumetric_ray_depth` | 16; 1-16 | Max surface intersections for the *Accurate* volume-intersection material option; exceeding it artefacts. |
| `use_volumetric_shadows`, `volumetric_shadow_samples` | False; 16 (1-128) | Approximates absorption by *other volumes*; "very computationally expensive". Does **not** shadow solids [DOC, page not re-checked]. |
| `volumetric_light_clamp` | 0 = off | Clamp volume scattering to cut flicker/fireflies. |
| `clamp_volume_direct`, `clamp_volume_indirect` | 0, 0 | Per-path clamps (files from before 4.2 had indirect near 0, so volumes ignored indirect light) [DOC release_notes/4.2 eevee_migration]. |
| `Light.volume_factor` | 1.0 | Per-light scattering multiplier; use to dim a light's fog contribution without changing surface lighting. |
| `Material.volume_intersection_method` | `FAST` / `ACCURATE` | Fast fine for closed manifold meshes. |
| `World.use_eevee_finite_volume` | False | Setting it True did **not** let Sun light through a world volume [TESTED 5.2, 2026-11-01; the sun trap below]. |

**Trap: a world volume blocks Sun lights completely [TESTED 5.2.0, 2026-11-01].** With a Volume
Scatter on the World's Volume output a Sun contributes nothing: ground and fog read 0.00000 in a
320x180 test (ground plane, sun 3.0, world scatter density 0.02) against 0.54 on the ground with no
volume. Still zero with the sun's shadow off, with `use_eevee_finite_volume = True`, and at density
0.0005. A point light in the same world volume lit ground and fog normally (ground 0.86); a scatter
cube (40 x 40 x 10 m) at the same density kept the sun (ground 0.50). The sky still renders, so the
frame reads as unlit ground, not pure black. First seen when an archway fly-through's moon fill
vanished until the haze moved into a bounded box [OBSERVED(archway), 2026-10-31]; the festival scene
uses a bounded haze cube too. *Check (broken render):* with a Sun in the scene, disconnect the World's
Volume output and re-render; if the sun returns, move the haze into a bounded volume object. Why (infinite optical depth toward a light at infinity) is inference, not checked.

### Measured: what actually limits quality [TESTED]
God-ray scene (spot through slats into world fog, 960x540, `taa` 64): RMSE vs a tile-2 / 256-slice /
256-spp reference.
| Setting | Result |
|---|---|
| tile 1,2,4,8,16 at 64 slices | RMSE 0.0488, 0.0487, 0.0488, 0.0491, 0.0493: **tile size did not matter** here (wide beams) |
| slices 16 / 32 / 64 / 128 / 256 at tile 8 | 0.068 / 0.077 / 0.049 / **0.018** / **0.0025** (error is depth slicing) |
| distribution 0 / 0.4 / 0.8 / 1.0 at 64 slices | 0.047 / 0.049 / 0.049 / **0.015** (fog dense near camera) |
| volumetric shadows (16 steps) | 0.0706, slightly worse (it changes the look) |
| `volumetric_light_clamp` 3 | no change |
Takeaway: **raise slices before touching tile size**; raise distribution toward 1.0 when the fog
that matters is close to the camera. Tile size matters for thin, sharp shafts and for sub-tile
detail; in one test scene tile 1 cost 0.8 s vs 0.2-0.3 s for tile 4-8.

### Cost at 8K [TESTED] (godray scene, 128 slices, taa 32, no RT; other-app baseline 1.6 GB)
| tile | froxel columns | time | peak VRAM |
|---|---|---|---|
| none (no fog) | n/a | 6.2 s | 5.8 GB |
| 16 | 480x270 | 7.5 s | 6.5 GB |
| 8 | 960x540 | 6.7 s | 8.3 GB |
| 4 | 1920x1080 | 9.6 s | **15.9 GB** (near the 16 GB card limit; risk of driver reset) |
Rule: froxel columns = pixels / tile^2, so **tile 8 at 8K is equivalent in memory to tile 2 at 1080p**.
Stay at tile 8-16 at 8K.

### Getting clean god-rays and haze
1. Fog source: a cube volume object around the action, or a world `Principled Volume` only with no
   Sun light (the sun trap above); anisotropy 0.3-0.6 for forward-scatter shafts. **`Density` is extinction per metre, so density and scene
   extent are one decision.** Transmittance along a sightline is `exp(-density * metres)`; pick the
   density from the transmittance wanted at the subject's distance, not a remembered figure.

   | Scene extent | Density | Transmittance it buys |
   |---|---|---|
   | A room, tens of metres (the test scene here) | 0.005-0.03 | 0.61 down to 0.05 at 100 m. The top of that range, the god-ray scene in the appendix, blew out white light; 0.008 with coloured lights looked right [TESTED] |
   | A city, kilometres | orders of magnitude lower; solve `exp(-density * metres)` for the transmittance wanted at the far subjects | [OBSERVED(triangle-battle), scene 02] |

   **The trap is carrying a room-scale figure to a kilometre-scale scene.** 0.010 looks like thin
   haze and is what most references quote; over 1 km it is optical depth 10, transmittance 4.5e-5.
   Subjects kilometres out render essentially black with no error, and it reads as a lighting
   failure, so the hours go into lamp power (OBSERVED(triangle-battle), a first kilometre-scale
   render).
2. Light it with **Lights** (spot with a blocking slat/gobo, point/area proxies for neon). Emissive
   surfaces do not scatter [TESTED].
3. Slices 128+, distribution 0.8-1.0, tile 8; custom range only for world volumes over large extents.
4. Volumetric shadows only if solids must visibly darken fog; they are costly.
5. Colour the fog via Principled Volume `Color` or light colour; coloured lights tint the haze.

One kit tuned bounded haze boxes by eye per space (street canyon, alley, plaza, boulevard, city chunk, interior hall), sun `volume_factor` near 0 [OBSERVED(triangle-bashkit)]. Working points, not a formula; the transmittance rule decides. Too much read as washed out, milky at short range, or a filled or purple sky; an interior looking toward a sun at high anisotropy blew out until anisotropy and density both came down.

### Haze boxes scatter the world [OBSERVED(triangle-bashkit)]

With a bright reflection world a haze box turned the sky flat navy or mid purple. Fix: a near black volume Color so it only absorbs, glow from volume emission; or drop the reflection world and the sun's `volume_factor`. Glow falling off faster than density gives a low band lifting the far city under black sky (OBSERVED(triangle-bashkit)). A box seen from above its top reads as a flat wash, so cameras over it hide it. Steam in a unit box with density from object coordinates gives each instance its own noise.

Symptom table: diagnosis.md, Volume artefacts.

## 7. Light linking, light groups, clamping, intensity

### Clamping and thresholds [DOC light_paths page, section 14]
| Property | Default | What it does |
|---|---|---|
| `clamp_surface_direct` | 0 (off) | Max light a surface can reflect from direct lights. |
| `clamp_surface_indirect` | **10** | Max for raytraced/probe light **and the world** (world counts as indirect). |
| `clamp_volume_direct`, `clamp_volume_indirect` | 0, 0 | Same for volumes. |
| `direct_light_intensity`, `indirect_light_intensity` | 1, 1 | (5.1+) Scale contribution **after** clamping; does not change transport. Like a compositing multiplier, consistent across material types. |
| `light_threshold` | 0.01 | Minimum intensity for a light to contribute; sets the cull distance. Per-light override: `use_custom_distance` + `cutoff_distance` (40). |
| `LightProbeVolume.clamp_direct` 0, `clamp_indirect` 10 | | Bake clamps (emission counts as direct). |

**Clamping helps** with fireflies from glossy surfaces reflecting very bright emitters, dense volumes,
tiny bright lights. **It kills the look** here [TESTED]: mirror/metal floor reflecting a strength-30
tube, peak pixel value by `clamp_surface_indirect`:
| clamp | 0 (off) | 10 (default) | 3 | 1 |
|---|---|---|---|---|
| peak reflected value | 26.3 | 8.8 | 2.7 | 0.88 |
With emitters stronger than ~10 and reflective floors, set it to 0 (or 30-50) and rely on TAA +
denoise. Glare thresholds read the clamped value, so a low clamp also starves the glow.

### `light_threshold` [TESTED]
20/40/60 W proxy lights x 4 per tube; wall patch brightness at 6 m:
| W per light | thr 0.01 | thr 0.001 | thr 0.0001 |
|---|---|---|---|
| 20 | 0.0005 | 0.0175 | 0.0194 |
| 40 | 0.0009 | 0.0375 | 0.0385 |
| 60 | 0.0148 | 0.0569 | 0.0576 |
Per-light `use_custom_distance=True, cutoff_distance=40` reproduced the 0.0001 result. A global value
of exactly 0 loses all culling (5.2 fixed shadow artefacts there) [DOC release_notes/5.2 eevee].

### Light linking (Blender 4.3+) [DOC release_notes/4.3 eevee]
Python: `obj.light_linking.receiver_collection = coll` (which objects a light affects) and
`obj.light_linking.blocker_collection = coll` (shadow linking) set on the **light object**
[TESTED] that the API exists; behaviour per the manual [DOC light_linking page, https://docs.blender.org/manual/en/latest/render/lights/light_linking.html].
Use it so a neon proxy light affects only the floor, or a character rim light only the character.
5.2 can copy linking to the selection.

### Light groups
`view_layer.lightgroups.add(name="Neon")` and `obj.lightgroup = "Neon"` exist, but **no light-group
channel appeared in an EEVEE multilayer EXR** (passes listed in section 11) [TESTED]. Treat light
groups as Cycles-only until proven otherwise. Alternative: render lights in separate passes by
toggling visibility, or use the compositor on `Diffuse Direct`/`Glossy Direct`/`Emission`.

## 8. Emission and glow without bloom

### Emission strength scale
Emission shader Strength 1.0 on a mesh = pixel equals the colour (shadeless) [DOC emission shader
page, section 14]. Above 1 is real HDR energy the view transform must compress, spending hue (section
10). For coloured neon under AgX the scale depends on emissive area. This table is the one place
emission strengths are recommended; provenance per row:

| Emissive element | Workable strength | Provenance |
|---|---|---|
| Thin strokes, edges, filaments, other than a hero meant to clip or a stroke set by capped luminance compensation for thresholded glow | above the panel range; step up from it | OBSERVED(triangle-battle) |
| Hero strokes meant to clip, a few pixels to a few tens across | well above the thin-stroke range, under AgX Punchy, Glare Bloom then weak Fog Glow | OBSERVED(cylinder-mirror), Cycles |
| Small panels and windows | 2 to 4 | HEURISTIC, interpolated from the section 10 saturation measurements |
| Large faces, walls, broad surfaces | 0.5 to 2 | HEURISTIC, interpolated from the same measurements |

Emissive AREA sets the workable strength. A thin stroke (a tube a few centimetres across) has almost no core: the viewer reads its glare halo, which carries the hue and stays saturated, so it tolerates high strengths. A large face (panel, sign, glowing wall) has a big core that desaturates as the section 10 measurements say.

Check rather than trust the table: sample the rendered core of the brightest coloured element and come back down if it reads white unintentionally. For a hero meant to clip, or a strength set by capped luminance compensation for thresholded glow (formula and cap: the `art-direction` skill, light-and-color.md, Color balance in glow), check the halo instead.

Colour matters as much as strength. A teal such as `#4fd1c5`, high luminance and only moderately saturated, is AgX's worst case; saturated neons such as `#20e3ff` or `#ff2bd6` hold hue much better. That teal's emission ladder on one project read pale at the lowest rungs and white well below 40 (OBSERVED(triangle-battle)); at 40, flat crimson and magenta quads were still off white (TESTED 2026-11-04, 5.2.0, look None; other values: the `art-direction` skill, composition.md, section 6).

Raising emission is a normal tuning move: raise a step, look, and stop when the colour washes out or the emitter floods its surroundings. The table is a start; the eye decides. Under AgX strength spends hue, so each step needs a look. A raise cannot light the scene or the fog (emissive meshes are not sources, section 0); that takes lamp power, fog density or glare strength.

**Night scenes: the ratio matters more than either side.** Where the emitter to ambient ratio is the look, cut ambient first (world, fill, moon, haze emission), then scale emitters with a gain per material family, a cap on large faces, and proxy lamps raised to match [OBSERVED(triangle-bashkit); the values were under Standard and do not carry to AgX]. Standard clips as a hue shift rather than white, so check the worst channel: red turned yellow once green passed 1, so hold a red emitter below where its green channel passes 1. Why the ratio works and what it costs: the `art-direction` skill, light-and-color.md, Contrast and falloff.

### Do emissive materials light the scene? Measured answer
Oblique camera, 5 tubes, floor roughness 0.25, Cycles 256 spp as ground truth [TESTED] at 960x540:
| Setup | Floor | Wall (6 m) | Visual |
|---|---|---|---|
| Cycles | 0.0504 | 0.0122 | Wall tinted, floor glow, reflections |
| EEVEE default (RT off, Fast GI on) | ~0.012 | ~0 | **No reflections, no bounce, black wall** |
| EEVEE RT on (`SCREEN`) | 0.0122-0.0183 | 0.0004 | Reflections yes; weak floor bounce; wall black |
| RT on, `trace_max_roughness` 1.0 / precision / thickness 0.5 | 0.0183 / 0.0191 / 0.0208 | ~0 | essentially unchanged |
| RT on + helper proxy lights, `k_watts=4` / 5 (below) | 0.058 / 0.070 | 0.0097 / 0.0133 | Matches Cycles look (floor a bit hot from point-light specular) |

Off-screen emitters (ortho top-down, emitter cube just outside the frame; floor strip beside it):
RT screen 0, RT probe-method 0, Fast GI 0, RT with overscan 10-50%: <= 0.0006 [TESTED]. Cycles gave
0.22 for the same geometry.

Other routes tried [TESTED]:
| Route | Result |
|---|---|
| Sphere light probe + RT method `PROBE` | picks up emitter coarsely (0.05) |
| Baked Light Probe Volume, `capture_emission=True` (12x12x4, 256 samples) | weak (0.0033). One quick bake, probably badly tuned, so a weak result for the technique and not a verdict on it. Bake via `bpy.ops.object.lightprobe_cache_bake(subset='SELECTED')` works headless (4 s) |
| Hide emitter from camera (`visible_camera=False`) | contributes **0** to screen-space RT |
| Real area light under emitter | works (RT off) |

### Proxy lights (the reliable fix)
Place Light objects at the emitter, color-matched. For tubes, point lights along the axis. Tested helper:

```python
import bpy, mathutils

def add_proxy_lights(scene, obj, color, strength, count=4, radius=0.05, k_watts=4.0, volume_factor=1.0):
    """Approximate an emissive mesh with `count` point lights along its longest bounding-box axis.
    Total power = k_watts * strength * surface_area_m2 (empirical, ONE calibration vs Cycles: re-check).
    Turns OFF obj shadow casting; otherwise the lights sit inside the mesh and are fully self-shadowed."""
    obj.visible_shadow = False
    mw = obj.matrix_world
    corners = [mw @ mathutils.Vector(c) for c in obj.bound_box]
    lo = mathutils.Vector((min(c.x for c in corners), min(c.y for c in corners), min(c.z for c in corners)))
    hi = mathutils.Vector((max(c.x for c in corners), max(c.y for c in corners), max(c.z for c in corners)))
    ext = hi - lo
    axis = max(range(3), key=lambda i: ext[i])
    centre = (lo + hi) / 2
    s = mw.to_scale()
    area = sum(p.area for p in obj.data.polygons) * ((s.x * s.y * s.z) ** (2.0 / 3.0))
    watts_each = k_watts * strength * area / count
    lights = []
    for i in range(count):
        pos = centre.copy(); pos[axis] = lo[axis] + (i + 0.5) / count * ext[axis]
        ld = bpy.data.lights.new(f"proxy_{obj.name}_{i}", 'POINT')
        ld.color = color[:3]; ld.energy = watts_each; ld.shadow_soft_size = radius; ld.volume_factor = volume_factor
        lo_ = bpy.data.objects.new(ld.name, ld); scene.collection.objects.link(lo_); lo_.location = pos
        lights.append(lo_)
    scene.eevee.light_threshold = min(scene.eevee.light_threshold, 0.001)   # default 0.01 culls dim proxies
    return lights
```
Calibration [TESTED], one scene, with this exact helper: tube radius 0.06, 2.2 m long (0.85 m2; the helper
counts the end caps), strength 15, 4 lights per tube. `k_watts` 3 / 4 / 5 gave floor 0.046 / 0.058 / 0.070
and wall 0.0060 / 0.0097 / 0.0133 against Cycles 0.050 / 0.0122, so **k_watts about 4 (12.76 W per light,
~51 W per tube) lands within ~20%**; 60 W per light was 4x too bright on the floor. Point-light
specular hotspots on the glossy floor are why the floor runs hot and the wall cool. One scene:
calibrate against a 480x270 Cycles render of your own.
For area-shaped emitters (screens, panels) use an Area light of the same size, `volume_factor` tuned,
facing the right way: an Area light emits along **local -Z**, rotation (0,0,0) faces down, and flipped
180 degrees it lit nothing in one test.

A cylinder is centred on its origin: depth 2.2 at z = 0.5 spans z -0.6 to 1.6, so a tube sunk below z = 0 puts the lights at its centre under the floor (a mistake made during testing).

### Glow in fog
Proxy lights give scattering [TESTED: wall patch 0.0003 without lights, 0.144 with]. With no lights:
an **emission-shader volume shell**, a slightly larger mesh around the emitter whose material's
*Volume* output is an Emission node (Strength about 0.3-1.5 by size). It gave a soft real glow,
RT-independent [TESTED], judged by eye; 1.5 on a 0.45 m shell was too opaque. A radial falloff via
Texture Coordinate / gradient should halo better (not tried). Volumes are camera-only (not in reflections).

Coloured light through a window [OBSERVED(triangle-bashkit)]: lamps have one colour and shadows do not tint, so coloured glass throwing coloured light needs one spot per tone, all leaving one source point behind the wall, the stone tracery shaping the beam. `visible_shadow` False on glass and lead. `volume_factor` is the washout control: at full value a rose window vanished behind its own shaft, so start the window spots low and the point lamps at none (the separate glow lamp at the glass runs lower: scene-code.md, Backlit cut panels). Festival style beams: real narrow-cone spots at very high power plus soft cone meshes carrying each beam's core.

## 9. Compositor glow recipes

Compositor glow settings, recipes and cost. View-transform and compositor findings carry across engines, so Cycles-measured recipes sit here too. Node API (sockets, identifiers, build snippet): api.md.

### What looked good (judged by eye, neon on dark, AgX) [TESTED]
**Thin-tube chain:** two stacked **Fog Glow** nodes, then a small saturation lift (the snippet and its numbers: api.md, Minimal working snippet). On the synthetic thin-tube scene (emitter strength 3, 4 proxy lights per tube, section 6 fog density) it gave clean coloured cores, saturated halos, no wash. The 3 is that scene's setting; strengths to use come from the section 8 table. Variants: **single Fog Glow** (Size 0.5, Thr 1.0) clean; Bloom at defaults washed the frame (section 0, item 10); Streaks (Thr 2, Strength 0.5) mild.

That chain was tested on low-strength emitters on a dark scene. For clipped emitters on true black, the **clipped-hero chain** that held on one project was Bloom with a raised threshold and low strength, then a weak Fog Glow, under AgX Punchy (OBSERVED(cylinder-mirror), Cycles OptiX, 5.2.0). Two to three times that Fog Glow strength laid a coloured veil across the frame, so step up from low and stop before the veil. It differs from the Bloom-at-defaults wash in threshold, strength and size; which matters is untested.

Set `Type`, `Quality`, threshold, size and strength explicitly on every Glare node; the defaults are not the look (api.md, Glare node table).

Glare is resolution relative: a halo tuned at 1080p shrinks to nothing at 8K. Tune glare size on 8K region crops, not previews.

### Re-compositing without re-rendering [TESTED]
Render the raw beauty with the compositor **off** to EXR, then grade in a second headless run whose
tree starts from an Image node:

```python norun
# norun: two-stage sketch; needs a previously rendered raw.exr and ellipsis stands in for the glare nodes
# stage 1 (in the render script)
sc.render.use_compositing = False
sc.render.image_settings.file_format = 'OPEN_EXR'; sc.render.image_settings.color_depth = '16'
# stage 2 (separate run, empty scene, same resolution)
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene; sc.render.engine = 'BLENDER_EEVEE'
sc.render.resolution_x, sc.render.resolution_y = 7680, 4320
sc.view_settings.view_transform = 'AgX'
tree = bpy.data.node_groups.new("Comp", "CompositorNodeTree"); sc.compositing_node_group = tree
img = bpy.data.images.load("raw.exr")                 # colorspace comes up as Linear Rec.709, correct
n = tree.nodes.new("CompositorNodeImage"); n.image = img   # outputs: Image, Alpha (multilayer EXR adds pass outputs)
# ...glare nodes as above, then Group Output; set output PNG format and bpy.ops.render.render(write_still=True)
```
Cost of Glare Fog Glow High at 4K: about +1-2 s; at 8K about +9 s [TESTED]. Cheap enough to iterate.

## 10. Color management

### View transforms in 5.2 [TESTED]
Default for new scenes is `AgX`; names, looks and displays are strings readable from the enum-error
list (api.md, Introspection, snippet 2). Exact spellings that matter: `'AgX'`,
`'Khronos PBR Neutral'`, `'ACES 2.0'`, and the look `'AgX - Punchy'` (looks are per view transform).
`view_settings.exposure` is in stops, applied before the transform; `gamma` after.
`bpy.data.colorspace.working_space` (default `'Linear Rec.709'`) is read-only on 5.2.0 [TESTED
2026-11-08], so set it with the operator: `bpy.ops.wm.set_working_color_space(working_space='Linear Rec.2020')` returned FINISHED headless, and the value survived save and reload [TESTED 2026-11-08 on 5.2.0]. Its `working_space` enum is filled at run time (introspection lists no items), so pass a name as `working_space` reads back. Its `convert_colors` option (default True) was not compared.

| Transform | Character [DOC displays_views page] | Use for glowing neon |
|---|---|---|
| Standard | no tone mapping, clips | Graphic look; hue skews to cyan/magenta/yellow on overexposure [TESTED: magenta and green tubes at strength 15 became pure white] |
| Filmic | deprecated, superseded by AgX | Keeps saturation longer than AgX in one test, at the cost of hue skew |
| AgX | 16.5 stops, **desaturates highly exposed colours** | Default; best highlight roll-off, whitens hot cores |
| ACES 1.3 / 2.0 | film standard; 2.0 more neutral, better gamut mapping | similar to AgX; ACES 1.3 whitened cores most (S 0.09 at strength 15) |
| Khronos PBR Neutral | product-photo colour accuracy under neutral light | keeps mid-range saturation best (S 0.78 at strength 1) but whitens hot cores (0.15 at 15) |
| Raw / False Color / Filmic Log | inspection only | |

### Why AgX desaturates bright emissives, and the measured counter [TESTED]
All filmic transforms compress high-intensity values toward white on purpose (to mimic film). A neon
core at strength 15 is ~15x display white, so every channel saturates near 1.0 and hue is lost.
Mean HSV saturation of the tube-core pixel (5 colours; sRGB-encoded PNG):

| Emitter strength | Standard | AgX | AgX Punchy | Filmic | ACES 1.3 | ACES 2.0 | Khronos | Raw |
|---|---|---|---|---|---|---|---|---|
| 1 | 0.78 | 0.44 | 0.59 | 0.70 | 0.72 | 0.66 | 0.78 | 0.95 |
| 4 | 0.57 | 0.23 | 0.29 | 0.54 | 0.31 | 0.38 | 0.38 | 0.78 |
| 15 | 0.31 | 0.11 | 0.16 | 0.37 | 0.09 | 0.14 | 0.15 | 0.39 |
| 60 | 0.20 | 0.02 | 0.04 | 0.13 | 0.02 | 0.03 | 0.04 | 0.20 |

Counter-measures, ranked by what worked:
1. **Lower the emitter strength** to the section 8 table's value and let Glare/lights/haze carry
   brightness. At strength 3 with AgX the section 9 recipe gave clearly coloured cores on the
   thin-tube scene [TESTED], judged by eye.
2. **Colour comes from the halo.** Glare halos next to a hot core stayed saturated under AgX
   (HSV S 0.7-1.0 at 16-40 px) [TESTED]; a white-hot core with a coloured halo is how neon photographs.
3. **AgX - Punchy** helps modestly (+0.05-0.15 core S). Compositor `Master Saturation` 1.8-2.5 did
   **nothing** for the already-white core (S 0.04 vs 0.05), but is fine for the halo [TESTED].
4. Lower view `exposure` (e.g. -1.5) raised the cyan tube's core S from 0.05 to 0.12, halos still saturated (one tube measured).
5. Saturate the **emission colour** itself (pure primaries), strength low.
6. `Standard` skews hues when overexposed; it suits deliberately graphic output.

**Saturated purple clips toward magenta** [OBSERVED(client-commission), Cycles, view transform not recorded]. Violet panel emission went pink at high strength; lower emission and a hue shift toward blue kept it violet. A saturated violet light colour still leaned pink on gravel and rake-lit wood.

Recommended for a dark scene with saturated glows and low-strength emitters: `AgX`, look `'None'` (or `'AgX - Punchy'` if
colours feel muddy), exposure 0 to -1, emitter strength per the section 8 table, Glare Fog Glow chain, saturation lift <= 1.2.
For clipped hero strokes on true black: AgX Punchy with Bloom then weak Fog Glow (section 9).
Compositor Glare input is scene-linear; the view transform is applied after the compositor [TESTED].

## 11. High-resolution strategy (8K = 7680x4320)

### Measured at 8K [TESTED]
| Scene / settings | Time | Peak VRAM (incl. ~1.6 GB other apps) | File |
|---|---|---|---|
| Neon, no RT, taa 32 | 6.2 s | 5.8 GB | EXR 16-bit ~1 MB (mostly black) |
| Neon + RT + 20 point lights (limit 0.01), taa 16, no glare | 25.4 s | 7.1 GB | PNG16 RGB 97 MB |
| same + Glare Fog Glow High | 34.5 s | 7.1 GB | PNG16 96 MB |
| same + Glare Medium | 26.8 s | 8.7 GB | |
| 4K, same RT scene, taa 16 | 9-11 s | 4.2 GB | PNG16 25 MB |
So **8K cost about 2.5x 4K** per sample here, not 4x: fixed costs (shader compile, scene sync) are
shared. The RT neon scene at taa 128 is on the order of minutes (HEURISTIC, linear from taa 16).

### 8K direct vs 4K + upscale
Render 8K directly. EEVEE's quality limits are per-pixel stochastic (TAA) and screen-space; a 4K
upscale adds no detail and softens the hard glow edges and fine geometry that justify 8K. The cost
(about 2.5x 4K) is manageable within VRAM. For tight schedules, 4K at `taa_render_samples=256` plus a
clean AI/Lanczos upscale is faster, untested here (HEURISTIC). Test composition with
`resolution_percentage` at 12.5-25% of 8K (identical framing) rather than changing resolution.

### Memory and pool settings
- Everything stochastic scales with pixels; volumetrics with pixels / tile^2 x slices; shadows with
  on-screen pixel footprint per light.
- `shadow_pool_size` (MB): default 512 (options: section 5). Raising it to 2048 cost +3 GB VRAM and did
  not fix 20 lights at 8K by itself (section 5).
- `gi_irradiance_pool_size` (volume-probe memory, MB, default 16) matters only when baking
  `LightProbeVolume`s. Bake failing for memory: lower `surfel_density`, split volumes [DOC, page not re-checked].
- `LightProbeVolume` data needs a bake (`bpy.ops.object.lightprobe_cache_bake`), is stored in the object, and `bake_samples` defaults to 2048, which is slow.
- Keep total under ~14 GB on a 16 GB card, or other GPU apps (and a running GUI Blender) crash or stall.
- If the driver resets, the process dies with no useful Python error. Lower tile size or slices first.

### `use_overscan` and post effects
`use_overscan` (+`overscan_size` percent, default 3, max 50) renders a larger internal buffer so
screen-space raytracing/GI do not fade at the frame edge, at real performance cost [DOC film page].
**The extra band is cropped from the output**, so compositor Glare cannot see light sources in it:
glow from off-frame lights needs a wider render (larger `resolution` with a camera `lens` or `shift`
change, then crop in the compositor). GAP(2026-11-08), carried from 2026-11-03: crop-in-comp not yet
tried; it needs a render with an off-frame light and would land here. An emitter-overscan test
(emitter at the frame edge) was inconclusive (floor strip 0.00001 to 0.00005).

### Output formats
| Choice | Notes |
|---|---|
| OpenEXR 16-bit (`color_depth='16'`) | **Use for finals and passes.** Matches EEVEE's half-float output; 5.2 writes half EXR faster [DOC pipeline_io 5.2]; ZIP lossless default; 5.1 added `HTJ2K` codec; codecs available: NONE, ZIP, PIZ, DWAA, DWAB, HTJ2K, ZIPS, RLE, PXR24, B44, B44A. EEVEE output has only 16-bit float precision [DOC limitations], so 32 adds nothing. |
| PNG 16-bit | Final graded deliverable after compositor + view transform. 96 MB at 8K RGB. 8-bit PNG bands in dark gradients and smoky fog. |
| Multilayer EXR | `image_settings.media_type='MULTI_LAYER_IMAGE'` then `file_format='OPEN_EXR_MULTILAYER'` (setting `file_format='OPEN_EXR'` under `MULTI_LAYER_IMAGE` raises). Needs `use_compositing=False` to write raw passes [TESTED]. 5.0 writes multi-part EXR by default. |
| Dithering | `render.dither_intensity` (default 1.0) adds noise to 8-bit outputs to break banding; keep for PNG8/JPEG. |

### Passes to save for flexible post [TESTED: all appeared in a multilayer EXR]
`Combined`, `Depth` (`use_pass_z`), `Normal`, `Position`, `Mist`, `Emission` (`use_pass_emit`),
`Diffuse Color`, `Diffuse Direct`, `Glossy Direct`, `Shadow`, `Ambient Occlusion`, `Environment`,
`Transparent` (`view_layer.eevee.use_pass_transparent`), `Volume Direct`
(`view_layer.eevee.use_pass_volume_direct`). Pass props live on the view layer
(`view_layer.use_pass_*`); EEVEE-only ones are under `view_layer.eevee`. `view_layer.eevee.use_pass_bloom`
still exists but there is no bloom to feed it (its existence TESTED 2026-11-03). The **Emission** pass is the
natural Glare source if you want glow only from emitters. Cryptomatte: `use_pass_cryptomatte_*`.
5.0 renamed passes ("DiffCol" -> "Diffuse Color", "Z" -> "Depth") [DOC release_notes/5.0].

### Anti-aliasing at 8K
`render.filter_size` default 1.5 px. If the 8K frame will be downscaled, leave 1.5; for native 8K
sharpness try 1.0-1.2 with TAA 128+ (HEURISTIC).

## 12. Performance knobs, preview vs final

| Knob | Preview | Final (8K) | Cost / effect |
|---|---|---|---|
| `taa_render_samples` | 16 | 128 (64 min, 256 hard) | linear in time |
| resolution | `resolution_percentage` 25-50 | 100 | quadratic |
| `use_raytracing` | True (False for layout only) | True | reflections + emissive bounce |
| `ray_tracing_options.resolution_scale` | '4' | '2' ('1' for hero) | big |
| `ray_tracing_options.use_denoise` | True | True | keep on (off was 13x noise, section 3) |
| `use_fast_gi` / `fast_gi_resolution` / rays / steps | True / '4' / 1 / 4 | True / '2' / 2 / 8 | moderate |
| `shadow_ray_count` / `shadow_step_count` | 1 / 2 | 1 / 6 | small; changing forces shader recompile |
| `shadow_resolution_scale` | 0.5 | 1.0 | memory, VRAM |
| per-light `shadow_maximum_resolution` | 0.01 (test scene) | tune by eye; scene values span a wide range (section 5) | memory; raising it fixes "Shadow buffer full" |
| `shadow_pool_size` | '512' | '512' (raise only if needed) | VRAM |
| `volumetric_tile_size` | '16' | '8' ('4' at 8K peaked ~15.9 GB of 16, section 6) | VRAM / tile^2 |
| `volumetric_samples` | 32 | 128 | slicing quality |
| `use_volumetric_shadows` | False | False unless needed | expensive |
| `clamp_surface_indirect` | 10 | 0 (or 30-50 for fireflies) | look, not speed |
| `use_overscan` | False | True, 10 | perf cost, fixes edge artefacts |
| Glare `Quality` | Low/Medium | High | +9 s at 8K |
| `render.use_motion_blur` | False | per shot | steps cost far less than a multiple on one scene (animation.md, Motion blur; the older "steps multiply cost" [DOC, page not re-checked] is superseded there) |
| DOF | off or `bokeh_max_size` small | `bokeh_max_size` 100+, `use_bokeh_jittered` costs samples [DOC, page not re-checked] | |
| Material | `use_backface_culling` on where possible [DOC, page not re-checked] | | |
| `light_threshold` | 0.01 | 0.001 if proxies vanish | culling vs reach |

Finishing layer cost [OBSERVED(triangle-bashkit)]: a grime, dressing and weather pass raised one city camera's frame time by about half; its once-per-camera setup was nearly all `scene.ray_cast`, so per-camera setup cost is ray cost (pipeline.md, Cheap framing pass). Rain and dust as thin triangles sized to a fraction of a pixel at distance need a rebuild after a large output-resolution change.

Depth of field [DOC https://docs.blender.org/manual/en/latest/render/eevee/render_settings/depth_of_field.html]:
camera `dof.use_dof`, `focus_distance`, `aperture_fstop`; `bokeh_max_size` px (0 disables the post-process
blur but not jitter), `bokeh_threshold` (sprite brightness), `bokeh_neighbor_max`, `bokeh_overblur`,
`use_bokeh_jittered`. Blended materials do not blur correctly in the post-process path.

### Cycles counterpart [OBSERVED(cylinder-mirror)]

On closed mirror tubes in Cycles on OptiX, scaling animation frame time from still timings over-predicted it several times over (OBSERVED(cylinder-mirror)), so time 5 frames before quoting a queue.

### Where the time went in a large scene [OBSERVED(festival-scene), 2026-11-01]

The one measured production-size EEVEE scene, a night festival site; a case, not a constant.

- Fit time per still against samples to split per-sample from fixed cost, and vary resolution. Here
  resolution had no measurable effect, which points at per-primitive work (geometry, shadow-map
  updates) rather than per-pixel shading (HEURISTIC; the decimation result fits it).
- **Almost all of the gain was polygon count**: foliage decimation nearly halved each shot. Each
  Poly Haven tree is a geometry-nodes leaf-card scatter of millions of polygons; realizing and
  decimating them, harder away from the cameras, gave the gain (ratios, recipe, cache: scene-code.md,
  Decimating heavy imported assets). The trees already had `visible_shadow = False`, and shadows
  bought little (section 5, Shadows are occlusion).
- **Method:** A/B timing at fixed samples, hiding one category per run (all trees, then all shadows)
  and comparing seconds per still; the render script's `--hide` prefix flag (pipeline.md) makes each
  run one command.

Untested knobs that may matter at this scale (UNVERIFIED(2026-11-08), carried from 2026-11-01: needs
timed renders; A/B before adopting): `scene.render.use_simplify` with `simplify_subdivision_render`,
`simplify_child_particles_render` and `simplify_volumes` (names exist on 5.2, TESTED by
introspection; EEVEE time effect unmeasured); the EEVEE shadow-resolution simplify reported in a
developer commit; collection instances versus batched meshes for many repeated modules
(scene-code.md, Batching crowds, still no head to head A/B).

### Render time on one growing kit [OBSERVED(triangle-bashkit)]

Per-frame cost rose from seconds to minutes as the kit grew into a city, and in the last city varied by an order of magnitude by view. Time the heaviest view before quoting (pipeline.md, Quoting render time).

**Haze lamp count ranked full-city frame cost; it is not a cost model.** Across that city's cameras, lamps with a volume factor reaching visible haze correlated with frame time better than seen tris, but one outlier camera carried most of it and the derived fit missed a culled shot by a wide margin (pipeline.md, Quoting render time). That culling leaves haze cost alone because visible lamps stay was never timed, and this frame argues against it; test one frame with and one without the unseen lamps, same file.

## 13. Appendix: how the numbers above were made

All on Blender 5.2.0 LTS, `-b --factory-startup`, OpenGL, RTX 4090 Laptop 16 GB. Scripts lived in
`...\scratchpad\scripts\` (not kept). Scene definitions:

- **Neon scene**: 40 m plane floor (albedo 0.03/0.03/0.04, roughness 0.25), 40 m back wall at y=6
  (albedo 0.15), five cylinders r=0.06, depth 2.2, emission colours cyan (0,0.8,1), magenta (1,0.05,0.6),
  orange (1,0.3,0.02), green (0.1,1,0.1), violet (0.6,0.1,1), 40 mm camera at (0,-8,2.5), black world.
- **Emission GI table**: Cycles 128-256 spp CPU denoised; EEVEE `taa_render_samples=64`, `Standard` view,
  32-bit EXR; "floor" = bottom 35% of frame, "wall patch" = two tube-free vertical strips of the wall.
  (Initial geometry had tubes straddling the floor; the proxy-light rows use tubes raised to z=1.25.)
- **Top-down emitter test**: ortho camera scale 6, white floor 0.8 rough 1, emitter cube 1x4x0.2 at z=0.5,
  cyan strength 20, region x in [-2,-1].
- **Noise sweep**: neon + 20 soft (0.25 m) proxy lights + one blocker box, RT on, RMSE of x/(1+x)
  against taa 1024 / 4 rays / 16 steps.
- **God-ray scene**: 200 m floor, wall at 30 m, 11 slats at y=10, spot 20 kW through them toward the
  camera, world Principled Volume density 0.03 anisotropy 0.6, camera 28 mm.
- **Colour test**: PNG 8-bit, HSV of the tube-centre pixel found by `world_to_camera_view`.
- **8K runs**: separate processes, VRAM sampled with `nvidia-smi` every 0.4 s, baseline subtracted not
  applied (1.6 GB was held by other apps, so subtract that for the scene's own use).

## 14. Sources

Official manual (the live site blocks scripted fetches with Cloudflare 403; the same pages were read as raw
RST from `https://projects.blender.org/blender/blender-manual/raw/branch/main/manual/...`):
- EEVEE index https://docs.blender.org/manual/en/latest/render/eevee/index.html
- Raytracing https://docs.blender.org/manual/en/latest/render/eevee/render_settings/raytracing.html
- Volumes https://docs.blender.org/manual/en/latest/render/eevee/render_settings/volumes.html
- Sampling (incl. shadows, light threshold) https://docs.blender.org/manual/en/latest/render/eevee/render_settings/sampling.html
- Light paths (clamping, intensity) https://docs.blender.org/manual/en/latest/render/eevee/render_settings/light_paths.html
- Performance (shadow pool, probe pool, compositor device) https://docs.blender.org/manual/en/latest/render/eevee/render_settings/performance.html
- Film (overscan) https://docs.blender.org/manual/en/latest/render/eevee/render_settings/film.html
- Depth of field / motion blur .../render_settings/depth_of_field.html , .../motion_blur.html
- Light settings (virtual shadow maps, jitter, resolution limit) https://docs.blender.org/manual/en/latest/render/eevee/light_settings.html
- Materials https://docs.blender.org/manual/en/latest/render/eevee/material_settings.html
- World settings https://docs.blender.org/manual/en/latest/render/eevee/world_settings.html
- Light probes (volume, sphere) https://docs.blender.org/manual/en/latest/render/eevee/light_probes/index.html
- Limitations https://docs.blender.org/manual/en/latest/render/eevee/limitations/limitations.html
- Emission shader https://docs.blender.org/manual/en/latest/render/shader_nodes/shader/emission.html
- Glare node https://docs.blender.org/manual/en/latest/compositing/types/filter/glare.html
- Displays and views https://docs.blender.org/manual/en/latest/render/color_management/displays_views.html
- CLI arguments https://docs.blender.org/manual/en/latest/advanced/command_line/arguments.html and .../render.html

Release notes (raw markdown from `projects.blender.org/blender/blender-developer-docs`):
- 4.2 EEVEE https://developer.blender.org/docs/release_notes/4.2/eevee/ ; migration .../4.2/eevee_migration/
- 4.3 https://developer.blender.org/docs/release_notes/4.3/eevee/ (light/shadow linking, Vulkan experimental)
- 4.5 https://developer.blender.org/docs/release_notes/4.5/eevee/ (shadow terminator, Vulkan parity)
- 5.0 EEVEE, compositor, python_api, color_management; compositor migration https://developer.blender.org/docs/release_notes/5.0/migration/compositor_migration/
- 5.1 EEVEE (light path intensity), compositor
- 5.2 EEVEE (screen-space RT overhaul, shadow pool), compositor, python_api (`gpu.init()`), pipeline_io, rendering

Community (low trust, used only to cross-check): https://blenderartists.org/t/getting-emission-shader-to-cast-light-in-eevee-next/1548871 ; the EEVEE emission/Shader-to-RGB limitation https://projects.blender.org/blender/blender/issues/119828 ; CG Cookie "Vibrant colors with AgX" https://cgcookie.com .

Where sources disagreed: none materially. The community advice to "just use bloom/SSR" is Legacy-only and
contradicted by the 4.2 migration page and by the property check. Where docs were silent (proxy-light
wattage, AgX core saturation, emissive GI strength, 8K VRAM) the numbers come from this file's own tests and are tagged.
