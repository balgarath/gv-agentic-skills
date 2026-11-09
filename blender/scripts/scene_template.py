"""Minimal end-to-end scripted scene: reset, world, ground, light, camera, render.

STATUS: TESTED 2026-11-03. Ran headless on Blender 5.2.0 LTS (hash
fbe6228777e7), Windows, `-b --factory-startup --python-exit-code 1 ... -- --res 480`:
printed `### CLIP_END: 1000.0 (farthest mesh corner 38.3 m)`, rendered in 1.4 s and
wrote a 120 KB PNG. clip_end is sized from the world-space bounding-box corners of
every mesh (the 40 m ground plane's far corner), not from object origins. The image
was last looked at on 2026-10-27 (a lit cube on a ground plane); the runner
check_snippets.py re-runs this script at 320 px and checks the sentinel lines.

Purpose: the smallest script that exercises every stage the blender skill
traps on: an idempotent reset, an explicit world, a camera aimed without a
constraint with clip_end set and printed, argv after `--`, EEVEE preview
settings, a `### ` sentinel report, and a still render.

Run:
  "/c/Program Files/Blender Foundation/Blender 5.2/blender.exe" -b --factory-startup \
      --python-exit-code 1 --python scene_template.py -- --res 960 --out template.png

The EEVEE block is the preview preset from eevee.md (section 1a), copied here
because this script is its executable form. If the two differ, eevee.md wins.
"""
import math
import os
import sys
import time

import bpy
from mathutils import Vector

argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []


def arg(name, default):
    return argv[argv.index(name) + 1] if name in argv else default


RES = int(arg("--res", 960))
OUT = os.path.abspath(arg("--out", "scene_template.png"))

# Reset: leaves no world datablock, so the world is created explicitly below.
bpy.ops.wm.read_factory_settings(use_empty=True)
sc = bpy.context.scene
world = bpy.data.worlds.new("World")
sc.world = world
if world.node_tree is None:
    world.use_nodes = True
world.node_tree.nodes["Background"].inputs["Color"].default_value = (0.02, 0.02, 0.03, 1.0)

# Ground, one subject, one area light (an Area light emits along local -Z).
bpy.ops.mesh.primitive_plane_add(size=40, location=(0, 0, 0))
bpy.ops.mesh.primitive_cube_add(size=1.0, location=(0, 0, 0.5))
light_data = bpy.data.lights.new("key", 'AREA')
light_data.energy = 800.0
light_data.size = 4.0
light = bpy.data.objects.new("key", light_data)
sc.collection.objects.link(light)
light.location = (0, -2, 5)

# Camera aimed without a constraint; clip_end is set explicitly and printed.
cam_data = bpy.data.cameras.new("cam")
cam = bpy.data.objects.new("cam", cam_data)
sc.collection.objects.link(cam)
sc.camera = cam
cam.location = (6, -8, 3)
target = Vector((0, 0, 0.5))
cam.rotation_euler = (target - cam.location).to_track_quat('-Z', 'Y').to_euler()
# Size clip_end from the world-space bounding-box CORNERS of every mesh, not from object origins:
# a finite ground plane's far corner is much farther than its origin (scene-code.md, Scene scaffold).
bpy.context.view_layer.update()
corners = [o.matrix_world @ Vector(c) for o in bpy.data.objects if o.type == 'MESH' for c in o.bound_box]
farthest = max((c - cam.location).length for c in corners)
cam_data.clip_end = max(cam_data.clip_end, farthest * 2.0)
print("### CLIP_END: %.1f (farthest mesh corner %.1f m)" % (cam_data.clip_end, farthest))

# EEVEE preview preset (eevee.md section 1a) with --res overriding the size.
sc.render.engine = 'BLENDER_EEVEE'            # 5.x id. BLENDER_EEVEE_NEXT existed only in 4.2-4.5
ev = sc.eevee
ro = ev.ray_tracing_options

sc.render.resolution_x, sc.render.resolution_y = RES, round(RES * 9 / 16)
sc.render.resolution_percentage = 100
sc.render.filter_size = 1.5                   # pixel filter, default

ev.taa_render_samples = 16                    # enough to judge composition and lighting; some noise left
ev.use_raytracing = True                      # the default is False: eevee.md, section 0, item 1
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
ev.clamp_surface_indirect = 10.0              # the default; eevee.md, section 7
ev.use_overscan = False
sc.render.use_motion_blur = False

sc.render.filepath = OUT
sc.render.image_settings.file_format = 'PNG'
t0 = time.time()
bpy.ops.render.render(write_still=True)
print("### RENDER_SECONDS: %.2f" % (time.time() - t0))
print("### OUT:", OUT, os.path.getsize(OUT) if os.path.exists(OUT) else "MISSING")
