# Pipeline: build once, render many

How to structure a scripted Blender project once one build takes longer than the renders it feeds. Scope: headless EEVEE stills from designed cameras on one PC (Blender 5.2.0 LTS, Windows, one laptop with an RTX 4090 Laptop GPU); Animation, Serial render queues and Reviewing motion cover EEVEE animation, and the last two also cover Cycles previews. Process-level costs live here; per-render cost and what drives it live in eevee.md (Performance knobs, Where the time went in a large scene). Provenance tags: the `maintaining-skills` skill (Provenance tags). Everything here is technique unless tagged TESTED: it worked on the project named, and your own project values belong in your `projects/` notes.

Index: When to split | The two scripts | All shots in one process | Animation: one process per shot | Organising the file | Cheap framing pass (fast rays, no-render proofs) | Persistent sessions | Opening .blend files you did not write | Serial render queues | Long renders on laptops | Quoting render time | Remote and helper renders | Per-shot culled files | Parallel rounds on one kit | Reviewing motion | Finishing a video.

Worked examples: the festival scene [OBSERVED(festival-scene), 2026-11-01] and the Triangle City bash kit, a 37 round kit and a 1080p video [OBSERVED(triangle-bashkit), 2026-11-05, Blender 5.2.0, one city file].

## When to split

A single script that builds and renders is the right shape while the build is cheap (SKILL.md, The loop). Split when a build costs more than the renders you iterate on, or when you re-render the same layout many times while tuning only lighting, exposure or framing. The festival build appends dozens of assets, decimates foliage and writes a large `.blend`; rebuilding it to change one camera's exposure would waste most of each iteration.

The regenerate-from-scratch rule still holds, scoped to the build script: the build starts from `read_factory_settings(use_empty=True)` and never mutates a previous run's file. The render script opens a saved `.blend` and never saves it. The one further stage is a derive step that reads the build's file and writes separate per-shot files (Per-shot culled files, below). It never overwrites the build output.

## The two scripts

**Build script.** Creates everything, then ends with `bpy.ops.wm.save_as_mainfile(filepath=BLEND)`. Anything the render script needs that is not already scene data (a look profile, per-shot exposure, haze density) is written into the file before saving, so the render script needs no build-script import:

- scene-wide profile as a JSON string in a custom property, `scene["fs_profile"] = json.dumps({...})`, read back with `json.loads(sc.get("fs_profile", "{}"))`;
- per-shot values as custom properties on each camera's data, `cam.data["exposure"]`, read back with `cam.data.get("exposure", 0.0)`.

A render script that finds no profile should say so loudly and fall back, not fail silently (the script this came from prints a `### WARNING` and uses defaults).

**Render script.** Opens the file (or is handed it on the command line), selects shots by name, applies per-shot settings, renders, exits:

```bash
blender -b --factory-startup --python-exit-code 1 scene.blend --python render_shots.py -- --shots plaza,lamp_close --samples 16 --suffix _s16
blender -b --factory-startup --python-exit-code 1 scene.blend --python render_shots.py -- --shots all
```

The `.blend` must come before `--python` on the command line, or the script runs against the startup scene instead (TESTED: api.md, Headless rendering from the command line, pattern C).

Conventions that made that render script simple (OBSERVED(festival-scene)):

- **Cameras are named `cam_<shot>`**; a shot name maps to one camera and one output file. `--shots all` renders every `cam_*` except ones reserved for animation. A `--list` flag that prints the available shots costs one line.
- **Assert the camera exists before spending render time.** That script printed `### no camera <shot>` and skipped; that is the floor. For batch runs prefer validating the whole shot list up front and exiting non-zero on any miss, so a typo fails in a second rather than after the other renders (HEURISTIC).
- **One manifest line per render**: camera, resolution, samples, seconds, output path, behind the `###` sentinel so it survives the stdout grep. That script printed shot, seconds and path; resolution and samples belong on the same line so a timing table can be rebuilt from logs alone (HEURISTIC).
- Overrides are flags (`--samples`, `--pct`, `--suffix`, `--hide Name1,Name2`); a `--hide` by object-name prefix is what made the A/B cost measurement in eevee.md cheap.

Skeleton of the loop (a version of this has run on a real project):

```python norun
# norun: needs a saved .blend with cam_* cameras; the full project version is not shipped
import bpy, sys, time, json
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
sc = bpy.context.scene
prof = json.loads(sc.get("fs_profile", "{}"))
shots = argv[argv.index("--shots") + 1].split(",")
missing = [s for s in shots if bpy.data.objects.get("cam_" + s) is None]
if missing: sys.exit(f"### missing cameras: {missing}")
for s in shots:
    sc.camera = bpy.data.objects["cam_" + s]
    sc.view_settings.exposure = sc.camera.data.get("exposure", 0.0) + prof.get("exposure", 0.0)
    sc.render.filepath = f"//renders/{s}.png"
    t = time.time(); bpy.ops.render.render(write_still=True)
    r = sc.render
    print(f"### render cam={s} res={r.resolution_x}x{r.resolution_y}@{r.resolution_percentage}% "
          f"spp={sc.eevee.taa_render_samples} s={time.time()-t:.1f} -> {r.filepath}")
```

## All shots in one process

Render every shot of a batch in one Blender process. The per-process costs are paid once:

- Loading the `.blend`: seconds per process for a large file; time it once on yours [OBSERVED(festival-scene)].
- Shader compilation: depends on whether the shader variants are new; values and the cold vs warm split: eevee.md, Sampling and noise (caveat b).

The batching gain is the load cost not paid twice. The festival's before and after timing of three stills dropped mostly because of the foliage decimation (eevee.md, Where the time went), not batching, so do not read it as a batching measurement.

## Animation: one process per shot, not per frame

Scope: this is for frames of one shot. Stills of many shots from one file still share a process (All shots in one process, above). Render to a folder of numbered PNGs from one process per shot or frame range. Crash safety comes from the folder: rerun the same command and finished frames are skipped, with `render.use_overwrite = False` under `-a`, and with your own skip test in a script frame loop, which should also guard against a half-written PNG (Serial render queues, below). A process per frame adds no safety. A queue that started `blender -b` once per frame on a large city file landed frames minutes apart [OBSERVED(triangle-bashkit)].

Log each stage before blaming process overhead. On that file process start plus load was small next to the per-camera dress, and `bpy.ops.render.render` was the main cost and varied by more than an order of magnitude by view, so opening once saves the load and the repeated dress and is not the order-of-magnitude gain it looks like. Save per-camera setup into a per-shot `.blend` once (Per-shot culled files, below); never run it in the frame loop.

From a source read, not measured here [VERIFIED-PRIMARY, Blender main about 5.3 RC, 2026-11-05, security reviewed]: EEVEE ignores `render.use_persistent_data` and builds a fresh instance each frame, the depsgraph is still reused across `-a` frames, and temporal reprojection is viewport only. `render.use_placeholder` writes an empty file when a frame starts, so a crash leaves a file that a resume skips (that interaction is an inference from the code, not tested): keep placeholders off.

## Organising the file for selective work

- **One top-level collection per installation** (dome, obelisk, lamps, site), with its lights in a child collection, so a shot or a test can hide one installation via `hide_render` or `layer_collection.exclude` without a rebuild. The festival build already nests `Site/Ground, Paths, Grass, Trees, Lighting` this way [OBSERVED(festival-scene)].
- **Expensive derived assets are cached as `.blend` files and appended on later builds**, keyed by the parameters that produced them, with a flag to force a rebuild. The festival foliage LOD cache is the worked case (scene-code.md, Decimating heavy imported assets).
- **Linked libraries and library overrides only for assets shared across scenes** (a lamp module used in three projects). For a scene one script generates end to end, whole-scene linking adds resync overhead and breakage risk for little gain. Overrides are created for every dependent datablock and edits can be lost on resync when the library changes; the scripted route is `bpy.data.libraries.load(path, link=True)` then `override_hierarchy_create(scene, view_layer, reference=None, do_fully_editable=False)` on the linked collection (TESTED 2026-11-08 on 5.2.0, minimal case, no render: a linked one-object collection, overridden this way, took an edit to the object's location that survived save and reload. Resync after the library changes was not tested).
- **Incremental rebuild** (open the saved file, delete one installation's collection, regenerate it, save) is possible with this layout but breaks the build script's from-scratch rule. Not adopted; decide per project and say so in the project's docs if you do.
- Uncompressed `.blend` files loaded about twice as fast as compressed ones in one test: 0.02 s against 0.045 s for a 3 M vertex file of random positions (39.5 MB against 32.2 MB), three loads each (TESTED 2026-11-08, 5.2.0, `save_as_mainfile(compress=...)`). Random data compresses poorly, so a real scene's size saving and its load cost may differ; the festival build saves with defaults.
- **Keep tuned values in a pure-data module that never imports bpy**, with a test that fails if it starts to, so values can be checked, diffed and fed to host-side tools without Blender [OBSERVED(triangle-battle)].

## Cheap framing pass

Before any EEVEE render, check framing with something far cheaper (the Embree pass below is the one that has been run): a Workbench render (`scene.render.engine = 'BLENDER_WORKBENCH'`) per camera, or a low-sample contact sheet of every shot camera in one image. Both are seen in public tooling as the agent's layout check; neither has been measured in this pipeline, including whether Workbench is actually faster than a 16 spp EEVEE frame on a heavy scene (UNVERIFIED(2026-11-08), carried from 2026-11-01: the comparison needs two timed renders, not yet run on a machine allowed to render). The arithmetic framing check in SKILL.md (The loop, step 2) still comes first and costs nothing.

### Fast rays and a no-render framing pass [OBSERVED(triangle-bashkit)]

`scene.ray_cast` walks every instance per ray, so on a large instanced city even a coarse ray grid takes many minutes a frame. The route that needs nothing installed: export the evaluated depsgraph (unique meshes via `foreach_get`, one matrix per `dg.object_instances` entry, hit parent `inst.parent.original.name`) and load Blender's own `blender.shared/embree4.dll` from host Python with ctypes, one sub scene per mesh. Constants and struct offsets: `RTC_GEOMETRY_TYPE_INSTANCE` 121, `RTC_FORMAT_FLOAT3X4_ROW_MAJOR` 0x9134, `RTCRayHit` primID 68, geomID 72, instID 76. `rtcIntersect1` in a Python loop ran orders of magnitude faster than `scene.ray_cast`, the build took seconds, and every test ray matched `scene.ray_cast` in hit and distance; check a sample of rays the same way. CPU only.

Shaded by normal and depth at low resolution, plus a top down map, those rays fitted every video camera to the real city with no render and showed which shots could not be met as planned, on a laptop that was shutting down under render load. They prove clearance and framing, not look.

### No-render proofs

Checks that answer a question a render would answer, at a fraction of the cost, on a machine that must not render:

- **Projection with no Blender at all:** `scripts/project_nobpy.py` (stdlib Python) projects world points through the camera `to_track_quat('-Z','Y')` builds and checks them against an anchor table, so framing is fixed before any geometry exists. Agreement with `world_to_camera_view` is in its header (TESTED 2026-11-08).
- **Visibility is a separate question from framing.** An anchor can land exactly on its spec and still be hidden by terrain in front of it; base anchors of objects standing on a terrace graze its near lip by construction. Walking the ground along each camera-to-anchor line found such a case [OBSERVED(triangle-battle), scene-coupled]. The generic check is `scripts/frame_check.py`, `check_occlusion`: one ray from the camera to each anchor through the whole scene, so it also sees buildings and crowds; its flags and limits are in the script's docstring (TESTED 2026-11-08, 5.2.0).
- **An emission graph's logic by evaluating its Math chain in Python:** recurse from the Emission Strength socket, return `default_value` when a socket is unlinked, substitute the time for the driven Value node and a dict lookup for Attribute nodes. A short script that runs in seconds, no GPU, safe beside a running queue. It proves the per-element strengths at chosen frames, not the look [OBSERVED(triangle-bashkit)].
- **A projected shadow pattern by a CPU ray check:** cast from the lamp through the alpha mask to the ground; it reproduced the patterns a draft showed and a final lost (eevee.md, section 5, worked case).

## Persistent Blender sessions

Default: cold start from the saved `.blend` per batch. Revisit only if measured time to first frame dominates the iteration (the suggestion was above about 30 s; the festival's load plus compile stayed under that, OBSERVED(festival-scene)).

If a persistent session is ever built:

- loopback only, with a per-session token; never an open socket;
- arbitrary code execution off by default and gated;
- a hung-request timeout that kills the child by PID;
- remember it reintroduces state drift across runs, which the from-scratch build exists to prevent.

**Do not use `blender-mcp` (ahujasid) with untrusted prompts or on a networked machine.** It runs arbitrary Python through `execute_blender_code` (public record CVE-2026-10688, code injection), listens on an unauthenticated localhost:9876 socket, and installs via `curl | sh` / `irm | iex` [ASSERTED: its README plus third-party CVE databases, 2026-11-01]. Its safe mode is a validation layer, not a sandbox.

Third-party Blender tooling (MCP servers, CLIs, skills, gists) generally targets 2.7x to 4.x and predates the 5.x API changes. Check anything borrowed against SKILL.md, Before writing any bpy: the 5.x delta.

## Opening .blend files you did not write

`--factory-startup` still matters when opening a file: it keeps user addons and prefs out. Automatic Python execution in opened files (Python drivers, registered text-block scripts) is off by default on 5.2, and `-Y` / `--disable-autoexec` forces it off [TESTED 5.2, `blender --help`: "Disable automatic Python script execution (Python-drivers & startup scripts), (default)"]. Pass `-Y` explicitly for any `.blend` not authored by this pipeline so a changed preference cannot turn it back on. Consequence for your own files, TESTED 2026-11-04 on 5.2.0 with drivers saved, reopened with `-b` and evaluated at frame 100: a simple expression (`frame*0.001`) and a non-simple one using only safe names (`sum([frame*0.001])`) both evaluated with autoexec off, default and `-Y`; a driver reading `bpy.context.scene` was blocked (`is_valid` False, `bpy.app.autoexec_fail` True) and evaluated only with `-y`. On these three expressions, what divided them was what the expression touches, not whether it is simple.

## Serial render queues

A guard that waits while any `blender.exe` runs deadlocks when a GUI is open. Filter by path: `Get-Process blender -ErrorAction SilentlyContinue | ? Path -like '*Blender 5.2*'` (TESTED 2026-11-04; without the ErrorAction it errors when none run). Inside a bash double-quoted string the shell expands PowerShell's `$_`, so use single quotes or the form above (TESTED 2026-11-04).

After stopping a queue on Git Bash, check `Get-CimInstance Win32_Process` for command lines naming the queue script: a child loop outlived its parent task, woke later and overwrote outputs (OBSERVED(cylinder-mirror), not re-run).

Keep logs readable: PowerShell `Add-Content` from a pipeline held a lock on the log and blocked every reader for the whole queue (OBSERVED(triangle-bashkit)).

On a machine that may die, render out of order so a partial run is still a clip: every 4th frame plus the last, then every 2nd, then the rest, each written as `.tmp.png` and moved into place, one process, placeholders off, resume by skipping frames above a size floor no half-written PNG reaches. A power cut early in one shot still left a watchable rough clip (OBSERVED(triangle-bashkit), one shot).

## Long renders on laptops

Hardware scope: one machine, a laptop with an RTX 4090 Laptop GPU. OBSERVED(triangle-bashkit), 2026-11-05. Use the checks anywhere.

- **Check the OS event log before calling a dead queue a sleep.** An unexplained queue death can be an unexpected power-off under sustained load, which the event log records and the render log does not.
- **Start a flushed health log before a long render** (GPU temperature, watts, throttle flags) and read temperature limits against power draw. A log sampled every few seconds can miss spikes, and a package can sit near its limit while core temperature and power draw look moderate.
- **A low average CPU figure does not mean a GPU render leaves the CPU cool.** At a low total CPU figure the package sat flat near its limit during each frame and fell within seconds of the frame ending; scene prep after load peaked higher (HWiNFO, DTS CPU Package). The note's explanation, the draw sync thread boosting one or two cores, was not tested.
- **A between-frames thermal guard cannot stop a frame in progress**, but removing it shortened time to failure to minutes.
- **Check the VRAM poller.** An `nvidia-smi` poller in the render script reported peak 0 throughout while the system log saw several GB.
- **Watch for a stale sensor log on overnight runs.** HWiNFO's shared memory stopped after a fixed stretch of logging and the CPU sensors went silent with no alarm; have the watcher flag a log that stops changing. A logging time limit as the cause is inferred from timing (UNVERIFIED(2026-11-08)).

## Quoting render time

Quote seconds per frame as wall clock per finished PNG, measured on the current scene, and time one real frame before quoting hours. A per-frame figure from an early, smaller city budgeted a video, and the merged city ran more than ten times that end to end. A pre-render cost fit overestimated a culled street shot several times over (Per-shot culled files, below; the fit's weakness: eevee.md, Where the time went in a large scene). Same direction as Cycles: eevee.md, Cycles counterpart. OBSERVED(triangle-bashkit).

Sample across the shot and time one frame of the heaviest shot, not the first. On the kit, per-frame time varied several times over between shots at the same settings while staying steady inside each shot, so a first-shot ETA was worthless. On a small EEVEE scene a short frame sample quoted low, because the close frames cost more (OBSERVED(archway-d)). The first frame of a fresh process costs more than the steady state (shader compile: eevee.md, section 3, caveat b); leave it out of the mean.

## Remote and helper renders

A second machine is a different instrument; check what it can report before trusting it (OBSERVED(archway), one incident).

- **A launcher build of Blender that returns no console output** (some store or packaged builds only run through a wrapper executable) cannot report "Shadow buffer full", so a zero count there is not evidence, even for a deliberately undersized shadow pool that must overflow. Judge overflow from the image instead: compare a reduced-size draft against the full-size final for projected shadow patterns.
- Hand-off that worked: shared files, the exact command line, and a request for VRAM peak, seconds per frame and the PNG copied back. Expect volumetric froxels to dominate VRAM at 4K.
- Whether to split a pass onto a slower helper, and how, is untested.

## Per-shot culled files

A derive stage between build and render. Order of work: remove what the camera cannot see first, keep in-frame lamps, shadows and samples, and reduce those only on what is still heavy. Per-shot files never overwrite the build output, and they and their cameras go stale on any layout change, so rerun this stage after one. EEVEE has no occlusion or camera culling setting: no property named for culling or occlusion exists on `SceneEEVEE`, `RenderSettings`, `Camera` or `Light` (TESTED 2026-11-08, 5.2.0, introspection: a name search for cull, occlu or visib on `SceneEEVEE`, `RenderSettings`, `Camera`, `Light` and `Object`; per-object `visible_*` ray flags exist but cull nothing by view).

Result [OBSERVED(triangle-bashkit)]: a few times faster as measured with no setting changed, and less once a dress layer on the full-city camera is discounted (eevee.md, Performance knobs). Not like for like: two cameras on the same boulevard, and the culled shot adds motion. Shadow overflow was not the difference. It pays by view: most tris and lamps left street shots and almost none left a skyline shot, so wide shots still need lamp work.

Method, CPU only:

- Sample frames at an interval, plus first, last and every frame of a whip.
- Bounding box against the view with a small margin, then a depth grid, then a reduced-resolution ray grid with transmission through glass and one reflection bounce.
- Keep everything hit, everything in view not provably behind the depth grid, anything within a keep distance of a seen surface, shadow casters found by rays from seen surfaces to each kept shadow lamp, and any actor cluster that comes into view.
- Lamp reach is the square root of power over `light_threshold` plus a margin (formula from memory of the source, UNVERIFIED(2026-11-08, carried: needs the light-culling source or a render test); no lamps went missing). Treat it as a generous keep radius, not the real cutoff: the measured falloff in eevee.md, `light_threshold`, reaches much less far. Haze counts as a visible surface for lamps with a volume factor.
- The unit of removal is a top level object or collection instance. A kept lamp inside an instance becomes a real lamp with the same data and world matrix, and the kept instance swaps to a lamp free copy.

Proof without a render: run the same rays on frames and offsets the analyzer did not use, against the full file and against true `scene.ray_cast`, and check that no lamp data changed.

## Parallel rounds on one kit

Conventions that held across one kit's rounds [OBSERVED(triangle-bashkit), one project; evidence, not a rule]:

- One module per round, a reserved number range, and a number that names one piece for good. Other files import read-only; each round ends with a merge list.
- A registry maps number to module and adapter. Rounds that skipped it needed adapters at merge. One round replaced a piece mid round and broke another's demo.
- Each piece loads as one named collection at the origin and places as an instance. Wall greebles carry their origin on the mount plate; scatter is plan only and seeded, so reseeding is cheap.
- A load check of every piece proves load, not look.
- With no git, back up the source before a merge. Keep a resume note per stage: they carried work over usage limits and power cuts.

## Reviewing motion

An image-only agent cannot judge motion from stills. Run a motion-review script of your own over the sequence (a frame-difference and flicker summary plus a few contact images; the original author's ran synthetic tests 14/14, TESTED 2026-11-04, and is not shipped here). Such a script needs OpenCV on the host Python, not Blender's. Its thresholds come from one rater and one family of dome previews (OBSERVED(cylinder-mirror)): good for "did this get faster", not for absolute targets. A designed fade reads to it as flicker and a hard cut as a huge flicker maximum; both are expected, so review the shot's own frames alone first [OBSERVED(archway-d)]. What to ask of the review: the `art-direction` skill, `references/lookdev.md`, Motion.

To find a dead region, composite per-pixel max over a subsample of frames at reduced size and tabulate ever-lit fraction by angle and radius. On cylinder-mirror this located black walls by azimuth and ruled out bounce limits (OBSERVED(cylinder-mirror)). For carried-over geometry, inventory per-face materials first.

Limits of a motion kit to check before a shot depends on them [OBSERVED(triangle-bashkit)]: robed walkers glide (the `art-direction` skill, staging.md, Personality without a face). Fast wheels on a three sided hub turn far enough per frame to alias, so rotors were slowed per frame on purpose. Crowd planning grows with the square of walkers, so plan per shot. One planner left conflicts and sent a fast taxi with no bank across a pavement corner because the real junction had no road through it. A planned sign blade turned out hidden behind a building, found by rays and not by a render.

## Finishing a video

Encode facts TESTED 2026-11-08 on ffmpeg 8.0.1 (gyan.dev full build, Windows) with tiny PNG sequences; general flags are [DOC, page not re-checked].

- **Encode from one numbered PNG sequence and join clips at the frame level.** Two clips joined with ffmpeg concat came out a few frames short from timestamp rounding, while one numbered sequence encoded to the exact count [OBSERVED(client-commission)]. Count the result: `ffprobe -v error -select_streams v:0 -show_entries stream=nb_frames -of csv=p=0 out.mp4` returned the exact count [TESTED].
- **image2 input defaults to 25 fps.** Pass `-framerate N` before `-i`; with none, `r_frame_rate` came out 25/1 [TESTED].
- **Colour tags.** PNG input is tagged sRGB transfer (`iec61966-2-1`) with colour space unknown. The output options `-color_trc bt709 -colorspace bt709` did not change the transfer tag; the filter `-vf setparams=color_trc=bt709:colorspace=bt709:color_primaries=bt709` did [TESTED]. It retags metadata; whether the RGB to YUV matrix follows the tag was not checked.
- **Banding in dark glow.** Dark glow gradients ringed on one project's draft and final encodes until static grain (including coarse colour grain) was added [OBSERVED(client-commission)], while another project's master at the same crf was clean [OBSERVED(archway-d)]. There is no universal crf: check the darkest gradient at native size. A downscaled contact sheet (PIL LANCZOS) made clean dark ground look posterized once, so do not judge banding from a sheet (one case, held).
- A command with those parts, run on the test frames: `ffmpeg -framerate 60 -i f%04d.png -c:v libx264 -crf 16 -preset slow -pix_fmt yuv420p -vf setparams=color_trc=bt709:colorspace=bt709:color_primaries=bt709 -movflags +faststart out.mp4` [TESTED, 8x8 frames]. libx264 `-crf`, `-preset`, `-tune`, the prores_ks profiles and `+faststart` are standard ffmpeg [DOC, page not re-checked].
