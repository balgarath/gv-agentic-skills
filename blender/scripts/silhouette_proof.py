"""Black-shape proof: every surface black on a white world, no fog, standard transform.

STATUS: TESTED 2026-11-03 (first 2026-10-27). The demo ran headless on Blender 5.2.0 LTS
(`-b --factory-startup --python-exit-code 1 --python silhouette_proof.py -- out.png`):
a 2 m cube inside a fog box rendered black (0,0,0) at frame centre on a white
(1,1,1) corner, and world, view transform and hide_render were restored. A control
run with volume hiding disabled rendered the corner black, so the hiding is what
makes the proof work. Tested with one demo scene only.

Purpose: check silhouette readability. If sides, clusters and overlaps do not
separate as pure black shapes, no amount of lighting will rescue them.

silhouette_proof(scene, out_path) overrides every material with black emission,
sets the world to white strength 1, hides volume objects from the render, uses
the Standard view transform, renders a still, and restores all saved state in a
finally block (including the temporary datablocks it created).

Run the demo (a cube inside a fog box):
  blender.exe -b --factory-startup --python-exit-code 1 --python silhouette_proof.py -- out.png
"""
import os
import sys

import bpy


def _is_volume_object(obj):
    if obj.type == 'VOLUME':
        return True
    for slot in getattr(obj, "material_slots", []):
        nt = slot.material.node_tree if slot.material else None
        if nt and any(n.bl_idname.startswith("ShaderNodeVolume") for n in nt.nodes):
            return True
    return False


def silhouette_proof(scene, out_path):
    vl = scene.view_layers[0]
    saved = (vl.material_override, scene.view_settings.view_transform,
             scene.render.filepath, scene.world)
    hidden = [o for o in scene.objects if _is_volume_object(o) and not o.hide_render]
    mat = world = None
    try:
        mat = bpy.data.materials.new("SIL_BLACK")
        if mat.node_tree is None:
            mat.use_nodes = True
        nt = mat.node_tree
        nt.nodes.clear()
        em = nt.nodes.new("ShaderNodeEmission")
        em.inputs["Color"].default_value = (0, 0, 0, 1)
        out = nt.nodes.new("ShaderNodeOutputMaterial")
        nt.links.new(em.outputs[0], out.inputs[0])

        world = bpy.data.worlds.new("SIL_WHITE")
        if world.node_tree is None:
            world.use_nodes = True
        bg = world.node_tree.nodes["Background"]
        bg.inputs["Color"].default_value = (1, 1, 1, 1)
        bg.inputs["Strength"].default_value = 1.0

        vl.material_override = mat
        scene.world = world
        scene.view_settings.view_transform = "Standard"
        for o in hidden:
            o.hide_render = True
        scene.render.filepath = out_path
        bpy.ops.render.render(write_still=True)
    finally:
        vl.material_override, scene.view_settings.view_transform, \
            scene.render.filepath, scene.world = saved
        for o in hidden:
            o.hide_render = False
        if mat:
            bpy.data.materials.remove(mat)
        if world:
            bpy.data.worlds.remove(world)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    out = os.path.abspath(argv[0] if argv else "silhouette.png")
    bpy.ops.wm.read_factory_settings(use_empty=True)
    sc = bpy.context.scene
    sc.render.engine = 'BLENDER_EEVEE'
    sc.render.resolution_x, sc.render.resolution_y = 320, 180
    sc.world = bpy.data.worlds.new("World")
    bpy.ops.mesh.primitive_cube_add(size=2, location=(0, 0, 0))
    bpy.ops.mesh.primitive_cube_add(size=12, location=(0, 0, 0))      # the fog box
    fog = bpy.context.active_object
    fog.name = "fog_box"
    fm = bpy.data.materials.new("fog")
    if fm.node_tree is None:
        fm.use_nodes = True
    fm.node_tree.nodes.clear()
    vp = fm.node_tree.nodes.new("ShaderNodeVolumePrincipled")
    vp.inputs["Density"].default_value = 0.5
    fo = fm.node_tree.nodes.new("ShaderNodeOutputMaterial")
    fm.node_tree.links.new(vp.outputs["Volume"], fo.inputs["Volume"])
    fog.data.materials.append(fm)
    cd = bpy.data.cameras.new("cam")
    cam = bpy.data.objects.new("cam", cd)
    sc.collection.objects.link(cam)
    sc.camera = cam
    cam.location = (0, -14, 0)
    cam.rotation_euler = (1.5708, 0, 0)
    before = (sc.world.name, sc.view_settings.view_transform, fog.hide_render)
    silhouette_proof(sc, out)
    after = (sc.world.name, sc.view_settings.view_transform, fog.hide_render)
    assert before == after, (before, after)
    img = bpy.data.images.load(out)
    w, h = img.size
    px = lambda x, y: tuple(round(c, 2) for c in img.pixels[(y * w + x) * 4:(y * w + x) * 4 + 3])
    print("### SILHOUETTE: centre", px(w // 2, h // 2), "corner", px(5, 5), "size", os.path.getsize(out))
    assert max(px(w // 2, h // 2)) < 0.05 and min(px(5, 5)) > 0.95
    print("### SILHOUETTE_DEMO: PASS state restored")
