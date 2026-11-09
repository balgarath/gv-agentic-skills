# Animation: motion blur, camera paths, noise, rigged people

Craft and facts for animated renders. Scope: Blender 5.2.0 LTS; the engine is named per claim
(EEVEE and Cycles differ here). API facts are TESTED 2026-11-08 by introspection and evaluation,
no render. Craft claims are techniques from one project each, tagged OBSERVED(project); the
values and cases behind each belong in `projects/`. The fcurve and driver API
(slotted actions, channelbags, loopable drivers, drivers in excluded collections) is in
api.md, Animation; queues, resume, timing and encoding are in pipeline.md. Provenance tags: the
`maintaining-skills` skill.

Index: Motion blur (shutter units, EEVEE steps, Cycles steps) | Camera paths (baked keys, Follow
Path, Track To, high pitch, shake) | Noise and seeds | Blending two looks | Rigged people.

## Motion blur

**`render.motion_blur_shutter` is measured in frames**, not seconds or degrees: the RNA text is
"Time taken in frames between shutter open and close", default 0.5, and values above 1.0 are
accepted (2.0 reads back 2.0) [TESTED]. So the same number gives different blur at different
frame rates: blur time is shutter / fps, and 0.5 is 33 ms at 15 fps but 8.3 ms at 60 fps, a
quarter (arithmetic). Reading 0.5 as a half-open shutter angle at any fps is derived from that text, not
stated by it (HEURISTIC).

Technique: when a look was approved on a low-rate draft, match blur in seconds at the final
rate, `shutter_final = shutter_draft * fps_final / fps_draft` (HEURISTIC, from the unit). It held
on two projects: Cycles matched a draft frame closely on one frame (OBSERVED(client-commission)); EEVEE
accepted a shutter above 1.0 and matched by eye (OBSERVED(archway-d)).
Without the change, the flight's last frames went from soft glow to sharper, darker
bands at the final rate.

**EEVEE:** `scene.eevee.motion_blur_steps` (default 1, min 1) and `motion_blur_max` (default 32,
range 0 to 2048) [TESTED]. Sweep the steps on a frame with close, fast motion: on
one scene the lowest count ghosted blockily, a few steps mostly fixed it, more was smooth and
beyond that showed no gain, and frame time grew far less than in proportion to steps; raising
`motion_blur_max` and samples changed nothing [OBSERVED(archway-d)]. EEVEE has no seed property (Noise and seeds, below).

Diagnostic before chasing stepped edges: render the same frame unblurred and compare. On that
scene the remaining steps were the far panel of a double-skinned cut sheet seen through the near
cuts, blurred, not a renderer artefact.

**Cycles:** per-object `object.cycles.use_motion_blur`, `use_deform_motion` and `motion_steps`
(on the Object, not the scene; default 1, range 1 to 7; the actual step count is 2^(steps-1) and
memory grows with it) [TESTED]. Cost on one project was a few percent at 1080p
(OBSERVED(client-commission)).

## Camera paths

**Bake an analytic path, one key per frame** (OBSERVED(client-commission), corroborated by
archway-d). Compute position and heading as functions of time in seconds and write a key per
frame. Roll is then exactly 0, speed is measurable, and the same time-based path rebuilds at
any frame rate: unblurred frames at the same time were identical across 15 and 60 fps. Rebuild
the keys at the final rate instead of sampling low-rate keys through subframes (a planted foot
drifted through subframes and held with keys rebuilt at the final rate, OBSERVED(archway-d)).
Two checks that ran: clearance against each object class sampled densely along the path, reporting the minimum and where it happens; and the largest frame-to-frame change in
acceleration, looking for spikes (OBSERVED(client-commission)).

**Heading and pitch straight into `rotation_euler`** has no vertical trap (unlike
`to_track_quat`, api.md, Camera aiming) and keeps Euler roll at exactly 0. At high pitch any yaw
still reads as image roll on screen, so lock the heading before the tilt gets high
(OBSERVED(archway-d), one shot). Where to aim and how to pace a move: the `art-direction`
skill.

The API facts for Follow Path (arc-length position, heading and banking), for Track To overwriting the
object's own rotation (where a shake can go), and for the F-curve Noise modifier properties are
not kept here. Introspect to confirm them on your version (api.md, Introspection).

## Noise and seeds

- **EEVEE 5.2 has no seed property** on `scene.eevee` or `scene.render` [TESTED]. Cycles has
  `scene.cycles.seed` and `use_animated_seed`.
- Cycles, fixed seed: noise held steady on a near-still camera, with about a tenth of the mean
  frame-to-frame difference of a new seed per frame (OBSERVED(client-commission)). Shimmer
  during camera motion could not be measured from frame differences.
- `bpy.ops.cycles.denoise_animation(input_filepath=..., output_filepath=...)` exists; its text
  says it needs denoising data passes and multilayer OpenEXR output [TESTED existence only;
  which denoiser it runs is unknown, and nothing here has run it].

## Blending two looks (day to night)

A crossfade between two finished sequences rendered with different view transforms (AgX day,
Standard night) cannot be blended in scene-linear, which needs one view transform. What ran:
decode both finished sRGB frames to linear light, blend, re-encode. On one frame it
looked better than a display-space blend, which came out darker (HEURISTIC: judged by eye on
one frame; the method then ran for the whole final). Either way it reads as a
dissolve, not dusk. How it reads: the `art-direction` skill, camera-motion.md, Time change.

## Rigged people

**Pose bones by matrix, no IK constraints, no depsgraph in the loop.** Per frame compute each
bone's desired armature-space matrix, convert it with
`basis = (parent_pose @ rest_parent.inverted() @ rest).inverted() @ desired`, working parent
first, and write the fcurves with `foreach_set` [formula TESTED 2026-11-08: a 4-bone chain with
roll matched the true `matrix_basis` to 2.4e-07]. Speed: several rigs over a full shot built in seconds (OBSERVED(archway-d)).

Walk cycle technique [OBSERVED(archway-d), RenderPeople rigs]:

- Foot plants are world points, the pelvis follows the lane, and two-bone IK solved in Python
  joins them, so a stance foot cannot slide.
- Enforce stride x cadence = ground speed by defining cycle time as stride / speed.
- Reach above 1.0 is what breaks plants: at a normal walking speed, long strides needed the pelvis
  lowered a few centimetres below rest; solve for the drop rather than guess it.
- Measure drift by gait phase, not by a height window, since swing toes pass under any low
  threshold. A whole-stance drift reading can come from the ball bone sitting above the sole
  pivot rather than from sliding.
- Lock an idle person's feet the same way: IK back to the base ankle when the hip sways.
- Limit: the mesh dips slightly into the ground at heel and toe rock.

RenderPeople FBX rigs: bone tails do not point at the child joint, so aim a limb by
`child.head - bone.head`, not by the bone's Y axis (OBSERVED(archway-d), asset-specific).

Not here yet: a colour chase rolled through hand-balanced lamps (periodic monotone cubic, not
yet judged in playback).
