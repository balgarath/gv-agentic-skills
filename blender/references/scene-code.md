# Scene code: working build patterns

Patterns for building scenes from Python. Scope: headless EEVEE stills with designed cameras, except Crowd motion, which is animation; patterns that break under a free camera say so. What `scripts/check_snippets.py` checks here: each unfenced block executes on 5.2 without an exception or a DeprecationWarning. Blocks that only define functions are also called by a per-block smoke test in the runner (`build_split_sky`, `make_ramped_fog`, `box_mesh`, `Batch`, `ridge_z`, `shear`), which proves each builds something plausible and not that it looks right; blocks fenced norun are not run. Patterns tagged OBSERVED(project) are techniques that worked there; the values that project used and the case behind them are in `projects/`.

Index: Scene scaffold (world, clip_end, seeds) | Arguments, stages, sweeps | The split sky | Ramped fog | Face winding | Shearing a lattice | Batching crowds (and instancing) | Crowd motion | Decimating heavy imported assets | Backlit cut panels | LOD by distance (and re-scatter for a planned path) | ridge_z | Bevels and edge masks | Per-object variation | Bulk edits to materials | Dark materials | Wet ground and water | Carving with no booleans | A geometry check needs a control. Camera aiming lives in api.md.

## Scene scaffold

Start every generator script from a genuinely empty scene so runs are idempotent, then create the world explicitly [TESTED]:

```python
import bpy
bpy.ops.wm.read_factory_settings(use_empty=True)
w = bpy.data.worlds.new("World")
bpy.context.scene.world = w
```

`read_factory_settings(use_empty=True)` leaves **no world datablock**. Forgetting this gives a scene with no environment at all, which renders much darker than expected and is easy to misdiagnose as a lighting problem.

Clip planes: the camera's `clip_start` and `clip_end` silently cull everything outside them. Set `cam.data.clip_end` at scaffold time and print it with the anchor table. The default `clip_end` of a new camera is 1000.0 on 5.2 [TESTED, asserted by `scripts/check_snippets.py`], so anything farther is lost until you raise it.

**Size it from the ground extent, not from the object list.** With a finite ground plane the binding distance is the ground mesh's far CORNER, not the farthest object, and the gap can be large, so a `clip_end` sized to the objects slices the ground. The symptom is not anything that looks like a clipping bug; it is a sky wedge at a frame corner, and it appears only in wide or high frames that actually reach the corner. Compute the corner's distance from each camera, set `clip_end` past it, and gate the build on it [OBSERVED(triangle-battle)]. Scope: the corner arithmetic is certain, the symptom was not observed there, since raising `clip_end` on this reasoning changed no pixel in the rendered frames.

Seeded randomness: use one `random.Random(seed)` per subsystem rather than the global module, so adding a crowd in one place does not reshuffle another.

## Arguments, stages, sweeps

Expose every tuning value as a command-line argument. Parse `sys.argv` after the double-hyphen separator that Blender passes through, then sweep variants in a shell loop; three variants in one loop beat three edit-render cycles.

```python
import sys
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
```

Gate expensive parts with integer `STAGE` flags so early iterations can skip them. (The from-scratch rule and its scope, build script only: SKILL.md, The loop; the saved-file render script: pipeline.md.)

## The split sky (Light Path trick)

Problem: a sky gradient rich enough to look good fills a night scene with ambient light and washes the ground to flat grey. Dimming the sky fixes the ground and kills the sky. The two needs conflict.

Fix: use the **Is Camera Ray** output of a `ShaderNodeLightPath` to choose between two versions of the sky. Camera rays see a bright, vivid sky. Every other ray, which is what lights the scene, sees a much darker one. The backdrop stays vivid and contributes almost no illumination.

This one change fixed a washed-out foreground that several rounds of lamp tuning had not. OBSERVED(triangle-battle)

The split does work in EEVEE on 5.2: swept, the dark side's strength moves scene lighting cleanly and monotonically [TESTED 5.2]. A session once concluded the opposite and built an emissive sky dome to work around it. The knob was fine; the measurement patch was lying on unlit terrain (diagnosis.md, A knob appears to do nothing). Measure a sky knob on a pixel that is actually sky.

```python
import bpy

def build_split_sky(scene, bright_color, dark_color, bright_strength=1.0, dark_strength=0.03):
    # create_world: read_factory_settings(use_empty=True) leaves NO world (see Scene scaffold)
    world = bpy.data.worlds.new("World")
    scene.world = world
    if world.node_tree is None:   # 5.2 already creates the tree; the setter is deprecated
        world.use_nodes = True
    nt = world.node_tree
    nt.nodes.clear()
    N, L = nt.nodes, nt.links

    lp = N.new('ShaderNodeLightPath')

    mix = N.new('ShaderNodeMixRGB')              # class name per findings
    mix.inputs['Color1'].default_value = dark_color     # factor 0: what the scene is lit by
    mix.inputs['Color2'].default_value = bright_color   # factor 1: what the camera sees
    L.new(lp.outputs['Is Camera Ray'], mix.inputs['Fac'])

    # In a real build, replace the two flat colours with your gradient, one copy
    # scaled to bright_strength and one to dark_strength.

    bg = N.new('ShaderNodeBackground')
    L.new(mix.outputs['Color'], bg.inputs['Color'])
    bg.inputs['Strength'].default_value = 1.0
    out = N.new('ShaderNodeOutputWorld')
    L.new(bg.outputs['Background'], out.inputs['Surface'])
```

`bright_strength` and `dark_strength` are shown as parameters for clarity but are not wired in the sketch. Apply them by scaling the two colours, or by feeding two Background nodes into a Mix Shader driven by Is Camera Ray. The dark value in the example is a placeholder, not a verified number.

**The split also runs the other way, and metal needs it.** Camera sees a near black sky, all other rays see a soft gradient with a bright tinted horizon band; black metal has nothing to reflect otherwise. Used across several rounds of one kit [OBSERVED(triangle-bashkit)]. Set the band's strength per setting and judge it on wet paving and water first, since too much washes them out; an isolated sheet cell took more than a street. A hard step at the horizon flips tilted panes black and white, so ramp it either side. Rays that leave glass through the back of a dome, and reflections that miss, hit this world, so a bright band turned panes milky and put a false glow in water: start the band above the horizon and darken below. Roof metal under a dark sky showed nothing from above and needed some diffuse.

## Ramped fog material

Fog needs density that climbs with distance, so atmospheric perspective lands on distant things (symptom: diagnosis.md, Fog flattens the image instead of adding depth). The sketch assumes a volume object (a large cube) whose Generated Y runs along the view direction and Generated Z is up, which matched the verified scene. If your volume box is oriented differently, swap the axes.

```python
import bpy

# base_density is a room-scale code default, not a recommendation. Density is extinction per metre,
# so a kilometre-scale scene needs roughly two orders of magnitude less; the decision and its
# arithmetic are owned by eevee.md (Volumetrics, Getting clean god-rays and haze).
def make_ramped_fog(name="Fog", base_density=0.012):
    mat = bpy.data.materials.new(name)
    if mat.node_tree is None:   # 5.2 already creates the tree; the setter is deprecated
        mat.use_nodes = True
    nt = mat.node_tree
    nt.nodes.clear()
    N, L = nt.nodes, nt.links

    tc   = N.new('ShaderNodeTexCoord')
    sep  = N.new('ShaderNodeSeparateXYZ')
    L.new(tc.outputs['Generated'], sep.inputs['Vector'])

    # Distance ramp: ~0 at the camera end (Y=0), 1 at the far end.
    dist = N.new('ShaderNodeMapRange')
    dist.inputs['From Min'].default_value = 0.0
    dist.inputs['From Max'].default_value = 1.0
    dist.inputs['To Min'].default_value   = 0.0
    dist.inputs['To Max'].default_value   = 1.0
    L.new(sep.outputs['Y'], dist.inputs['Value'])

    # Height ramp: denser low, thinner high (flip From/To to reverse).
    hgt = N.new('ShaderNodeMapRange')
    hgt.inputs['From Min'].default_value = 0.0
    hgt.inputs['From Max'].default_value = 1.0
    hgt.inputs['To Min'].default_value   = 1.0
    hgt.inputs['To Max'].default_value   = 0.1
    L.new(sep.outputs['Z'], hgt.inputs['Value'])

    # Large-scale noise so the fog is patchy.
    noise = N.new('ShaderNodeTexNoise')
    noise.inputs['Scale'].default_value = 1.5
    L.new(tc.outputs['Generated'], noise.inputs['Vector'])

    def mul(a, b):
        m = N.new('ShaderNodeMath'); m.operation = 'MULTIPLY'
        L.new(a, m.inputs[0]); L.new(b, m.inputs[1])
        return m.outputs[0]

    d = mul(dist.outputs['Result'], hgt.outputs['Result'])
    d = mul(d, noise.outputs['Fac'])

    scale = N.new('ShaderNodeMath'); scale.operation = 'MULTIPLY'
    L.new(d, scale.inputs[0]); scale.inputs[1].default_value = base_density

    vol = N.new('ShaderNodeVolumePrincipled')
    L.new(scale.outputs[0], vol.inputs['Density'])
    out = N.new('ShaderNodeOutputMaterial')
    L.new(vol.outputs['Volume'], out.inputs['Volume'])
    return mat
```

Note the noise multiplies the density by a value that averages around 0.5, so raise `base_density` to compensate. Use the density test (diagnosis.md, Fog is not showing up) to confirm the volume still renders after you add ramps.

## Hand-built meshes: face winding

Outward winding for a box built with `from_pydata` (symptoms of the wrong winding: diagnosis.md, Faces shade wrong / volume will not scatter). Vertex layout: indices 0 to 3 are the bottom as (-,-), (+,-), (+,+), (-,+); indices 4 to 7 are the top in the same order. Correct outward winding:

```python
import bpy

BOX_FACES = [
    (0, 3, 2, 1),   # bottom
    (4, 5, 6, 7),   # top
    (0, 1, 5, 4),   # side
    (1, 2, 6, 5),   # side
    (2, 3, 7, 6),   # side
    (3, 0, 4, 7),   # side
]

def box_mesh(name, x0, x1, y0, y1, z0, z1):
    verts = [
        (x0, y0, z0), (x1, y0, z0), (x1, y1, z0), (x0, y1, z0),   # bottom
        (x0, y0, z1), (x1, y0, z1), (x1, y1, z1), (x0, y1, z1),   # top
    ]
    me = bpy.data.meshes.new(name)
    me.from_pydata(verts, [], BOX_FACES)
    me.update()
    return me
```

## Shearing a lattice

To shear a lattice so every square cell becomes a parallelogram, apply the shear to the **base vertices as a function of height, before thickening or beveling**. Shearing finished beam geometry self-intersects and z-fights.

Write one helper that maps `(local_x, local_z)` to a displaced position, and run every corner of every beam through it.

```python
def shear(local_x, local_z, k=0.2):
    """Displace x as a function of height. Returns (x, z)."""
    return (local_x + k * local_z, local_z)
```

The linear form above is an illustration of the structure (one function, applied to every corner). The actual displacement function used in the project is not recorded in the findings.

## Batching crowds

Batch a crowd of unique, posed units instead of giving each one an object. Thousands of unique objects were slow to create, slow to render and awkward to material. This scope is the point: repeated shared meshes are a different case (Batching versus collection instances, below). The approach that works [OBSERVED(triangle-battle), 5.2, a mass battle]:

1. Generate each unit in LOCAL space as plain `verts` and `faces` lists.
2. Transform by a matrix and append into a running array.
3. Build one mesh object per material.

A crowd in 8 materials becomes **8 objects**, however many figures it holds.

```python
from mathutils import Vector

class Batch:
    def __init__(self, name):
        self.name, self.v, self.f = name, [], []

    def add(self, verts, faces, M=None):
        b = len(self.v)
        if M is None:
            self.v.extend(tuple(p) for p in verts)
        else:
            self.v.extend(tuple(M @ Vector(p)) for p in verts)
        for face in faces:
            self.f.append(tuple(i + b for i in face))
```

**Batching leaves every object's origin at the world origin.** Vertices built in world space and appended into one mesh make the object's transform identity, so `ob.matrix_world.translation` reads (0, 0, 0) for all of them and any gate written against it silently sees the same point for every object. A bevel gate written as a distance from the camera (the gate itself: the art-direction skill, references/light-and-color.md, Material believability) matched nothing across 400-odd objects, because the single shared origin fell outside it. The same code with the camera nearer that origin would have beveled the entire scene, giants included: the gate matches all or nothing depending on where one point happens to land. Neither failure announces itself. Gate on the mesh's own bounds instead [TESTED 5.2]:

```python norun
# norun: fragment; needs an object ob, a camera location cam_loc and mathutils.Vector
d = min(((ob.matrix_world @ Vector(c)) - cam_loc).length for c in ob.bound_box)
```

On one batched crowd in headless EEVEE stills the build took under a second and the render a few seconds with volumetrics and glare [OBSERVED(triangle-battle)]. **At that scale geometry is not the bottleneck; lamps and volumetrics are.** The scope is the vertex count: with imported assets far heavier per asset, polygon count became the dominant cost and cutting it nearly halved render time (festival scene, imported foliage: eevee.md, Where the time went in a large scene; Decimating heavy imported assets, below). This also inverts in a real-time engine, where draw calls dominate and merging destroys culling and instancing; do not carry this rule to Unity.

Batching versus collection instances: scope by what repeats. Shared meshes instance; a baked static crowd with geometry that differs per unit batches (HEURISTIC). Variation that is only colour or scale can stay instanced (Per-object variation, below), and an animated crowd keeps one object per actor (Crowd motion, below). No head to head A/B exists, so whether instancing beats batching for thousands of identical modules in EEVEE 5.2 is unmeasured either way (UNVERIFIED(2026-11-08), carried from 2026-11-01: the A/B needs two timed renders, held in INTAKE.md). The batching rule above was measured on varied, posed figures, where instancing does not apply. What instancing has shown, with nothing batched to compare against:

- The festival scene places its trees as collection instances (`instance_type = 'COLLECTION'`), each decimated mesh shared by every instance, and that rendered fine.
- Geometry Nodes proxies [OBSERVED(triangle-bashkit), on a laptop, proxy shadows off]: tens of thousands of instances took a fraction of a second to instance and rendered in seconds, with built buildings and roof pieces added.
- Full city: thousands of unique mesh objects drew several times their stored triangles through instancing, and the file loaded in seconds.
- One object per actor is cheap when the mesh is shared and swapped: re-rendering hundreds of people cost little over no change.

Have each unit builder return a **dict of `{part_name: (verts, faces)}`** so one figure can feed several batches (dark body to one, glowing edge to another). Per-instance colour variation then costs nothing: route the glow part into one of N colour batches. Key the choice to the unit's cluster, not to a per-unit random draw (one colour per cluster: the art-direction skill, references/staging.md). Apply a unit's lean in local space before its yaw: the lean then turns with the unit and reads the same whichever way it faces, whereas a lean applied after the yaw points the same world direction for every unit.

## Crowd motion: a pose flipbook

Cheap crowd motion with no rig [OBSERVED(triangle-bashkit), a test clip on a shared GPU and the kit's video crowd]. Each pose runs the real figure function on a posed skeleton, is built on first use and shared by everyone in that pose, and `apply(frame)` swaps `ob.data` and sets location and yaw. Skinning was rejected because it would collapse faceted figures.

- The whole plan is pure, computed per actor from a seed before any frame, so any process can start on any frame and a resume matches; check it by diffing a cold single-process frame against the same frame of the sequence.
- Memory, per-frame cost and plan time per process stayed small at hundreds of people; measure all three on your crowd.
- Feet stay planted because the numbers are locked, not tuned: whole frames per gait cycle and body travel of exactly one cycle length; measure drift to confirm.
- Fix each actor's LOD tier per shot from nearest approach so nothing pops. Bind with the whole shot range even for one frame, so a resumed process picks the same actors.

Limits: pipeline.md, Reviewing motion.

## Decimating heavy imported assets (LOD cache)

Imported assets can carry far more geometry than a still needs. Poly Haven trees are geometry-nodes leaf-card scatters of millions of polygons each, and in the festival scene they were the render cost (eevee.md, Where the time went in a large scene). The pattern that worked [OBSERVED(festival-scene), 2026-11-01]:

1. **Realize the instances.** Evaluate the object and copy the result to a plain mesh, `bpy.data.meshes.new_from_object(obj.evaluated_get(depsgraph))`, then `mesh.transform(obj.matrix_world)`. A Decimate modifier on the unevaluated object would not see the geometry-nodes cards.
2. **Decimate per LOD**: a temporary object with a `DECIMATE` modifier at the LOD ratio, evaluated again with `new_from_object`. Skip meshes under a few thousand polygons. Pick a **near ratio and a lower far ratio**, with "near" measured as distance to the nearest shot camera, all exposed as build flags. Copy the source's material slots onto the new mesh.
3. **One collection per (model, LOD)**, used as the `instance_collection` of every placement, so each decimated mesh exists once.
4. **Cache the result** with `bpy.data.libraries.write(path, set_of_collections, path_remap='ABSOLUTE', compress=True)`, with the ratios in the file name so changing a ratio misses the cache. Later builds append it with `bpy.data.libraries.load(path, link=False)` and assign `data_to.collections`; a `--rebuild-lod` flag forces regeneration. Decimating is slow enough per build to be worth caching. Relink image paths after appending if textures moved.
5. Freed source: once both LODs exist, unlink and remove the full-detail objects so the saved `.blend` does not carry them.

Choose LOD by distance to the nearest designed camera (LOD by distance, below). Night silhouettes survived the festival's far ratio on far trees; check close shots by eye before going lower.

## Backlit cut panels (pattern-projecting lamps)

Laser-cut sheet modules (black = material, white = void) lit from inside, casting patterned light through haze and onto the ground. Wiring used in two projects [CORROBORATED: OBSERVED(archway) 2026-10-31; OBSERVED(festival-scene) 2026-11-01]:

- Load the mask image with `colorspace_settings.name = 'Non-Color'`; drive Principled `Alpha` with `1 - mask` (a Math SUBTRACT from 1) so voids are transparent. Panels are thin sheets (solidified, or flat faces).
- `material.surface_render_method = 'DITHERED'` (the 5.x name for hashed alpha) and `use_transparent_shadow = True`. Shadow maps then follow the alpha, so the voids pass light and the sheet blocks it.
- **One real point light inside each module**, shadows ON (the pattern is the shadow; turning it off leaks the light through everything: eevee.md, Shadows are occlusion), small radius so the pattern stays sharp, and a capped `shadow_maximum_resolution` so several such lamps fit the shadow pool (production caps: eevee.md, section 5). Without a cap, a handful of these lamps overflowed the pool at 1080p on one build (OBSERVED(festival-scene)).
- Power and haze: start low and raise power per module by eye; pick density from the scene's extent (eevee.md, section 6). Too much of both floods the frame. Haze in a bounded volume box, not the world, if a Sun is present (eevee.md, Volumetrics, the sun trap).
- **Cycles: the lamp's `shadow_soft_size` sets the projected pattern's penumbra**, and a size that leaves the panel itself looking correct can smear the pattern on a floor a couple of metres away, which then reads as a missing shadow rather than blur. A point lamp inside an alpha-cut panel lost its ripple pattern on the floor at one size and gave crisp stripes at a much smaller one [OBSERVED(client-commission), Cycles, one interior debug render]. EEVEE radii do not carry to Cycles; step the size down until the floor pattern is crisp.

Additions from the kit [OBSERVED(triangle-bashkit)]:

- **Beams with no cut geometry.** A flat tri mesh panel with DITHERED, `use_transparent_shadow` True and a Transparent BSDF in the holes passes a point lamp through the mask into a bounded volume box. Set `volume_factor` 0 on moon and flood or they grey the haze (OBSERVED(triangle-bashkit)).
- **Glow and throw together.** A Light Path Is Shadow Ray mix makes a hole fully Transparent to shadow rays while the eye sees a mix of glow and see-through, so light leaves at full strength and the panel still glows. Settings there: one point lamp per cage, shadow on, a small radius, a reduced `shadow_filter_radius`, jitter off, specular 0, colour pushed a little toward pale so hue survives on the ground (OBSERVED(triangle-bashkit)). Floors must stop below the lamp or rays never reach the lower panels. Unshadowed glow lamps inside a tower leaked a pool on the ground and killed the pattern near the base.
- **Swap treatment without rebuilding.** Hand back panels as triangles, and one call swaps material and lamp power across fret lit, glass unlit, glass lit and both (an `apply_treatment` function), which let every window be judged in both states from one build. Lit glass emits a multiple of pane colour with a per pane hot factor falling toward the rim; unlit glass is a darkened, glossy Principled with a trace of emission; the window glow lamp scales with R squared and is not the beam-throwing window spots (eevee.md, Glow in fog); unlit cells keep part of the glass tint (OBSERVED(triangle-bashkit)).

## LOD by distance

Builder-time LOD from camera distance works for a designed camera set; it cannot follow a free camera. For multi-camera scenes, gate by distance to the NEAREST designed camera (the policy that worked on one project, OBSERVED(triangle-battle)). Three levels is enough; strip the expensive parts, not the silhouette:

| LOD | Distance | What to drop |
|---|---|---|
| 0 | near | nothing |
| 1 | mid | fewer stroke sub-segments, no accessories |
| 2 | far | silhouette only, no interior detail, no membrane |

Pass the level into the unit builder rather than filtering afterwards, so the cost is never paid.

**Re-scatter for a planned moving camera** [OBSERVED(archway-d), EEVEE]. Builder-time LOD can follow a camera whose path is known: swap the point mesh under the existing geometry nodes modifier (keep the node group and tuft collections, build a new mesh with the same attributes, `ob.data = new`). Fix each tuft's LOD from the nearest distance at which it is inside the view wedge at any sampled moment of the path (sample often enough that a fast pan cannot skip a tuft), and drop tufts never seen. LOD never changes in time, so nothing pops; the cost is that anything off the planned views is bare, so a changed ending needs a re-scatter. Audit coverage with the sun raised high at low resolution on a subsample of frames, where bare ground cannot hide in the dark.

Attributes and shaders replace lamps and geometry at scale [OBSERVED(triangle-bashkit), each from that round's demo render]:

- Windows as a shader in object space (floor height, runs from a large patch noise, a dark service level at intervals): a dozen landmarks drew under a million tris, where modelled windows on a structure that size would be millions.
- A per-vertex `wash` attribute drives emission on stone to fake uplight from each setback with no lamp, and it instances. Bevelling that mesh breaks the attribute order.
- One hot metal material on a point attribute `temp`, 0 soot to 1 molten.
- Fog as an exponential of Camera Data View Distance in each material, with no volume, out to the city's full extent.

Far-rank grow cheat: a 3 m figure at 600 m with a 24 mm lens on a full-frame sensor is about 4.7 pixels at 1400px wide, so cull it or scale far ranks up with distance so a mass reads as a mass.

```python norun
# norun: fragment; y is the unit's depth and near_y, base_size come from the builder
grow = 1.0 + (y - near_y) / 300.0
size = base_size * grow
```

Two scopes bind this. It is invisible only from the designed camera; parallax exposes it when the camera moves. And never grow the figures serving as the scale ruler (the art-direction skill, references/scale.md).

## ridge_z and placement on terrain

Put the far army on rising ground: a smooth ridge behind the line lifts distant ranks above the horizon so they stack instead of overlapping into a line.

```python
def ridge_z(y, Y0, Y1, H):
    """Smoothstep ridge height at depth y: 0 before Y0, H after Y1."""
    if y <= Y0: return 0.0
    t = min(1.0, (y - Y0) / (Y1 - Y0))
    return H * (t * t * (3.0 - 2.0 * t))     # smoothstep
```

Apply it to the ground mesh vertices **and** to every unit placement, or the crowd sinks through the hill.

## Bevels and edge masks

Bevel what the camera can resolve (the rule and its distance gate: the art-direction skill, references/light-and-color.md, Material believability). The modifier recipe is a `BEVEL` modifier with `segments` 2 to 3, a tiny `width` relative to the object, `limit_method = 'ANGLE'`, and `harden_normals = True` if shading looks faceted (CONVENTION; the property names are asserted by `scripts/check_snippets.py` on 5.2).

Use real-geometry bevels, not the shader Bevel node: the node does nothing in EEVEE on 5.2. Its Normal output was identical to the geometry normal, with a maximum pixel difference of 0.0000 [TESTED 2026-11-03, 5.2.0]. The Geometry node's Pointiness does work in EEVEE: on Suzanne it gave 0.004 to 0.737 across 134 distinct values [TESTED 2026-11-03, 5.2.0], so an edge-wear mask can be built on Pointiness. For script-generated geometry, an edge-angle mask computed in Python and used to blend a worn material is the other route.

## Per-object variation

Per-object variation (colour, roughness, wear) has two routes: an attribute written from Python, or the Object Info Random output in the shader. Starting values carried from the pre-consolidation skill, unrun (HEURISTIC): random scale 5 to 15 percent, rotation jitter 1 to 5 degrees.

Recipe that ran [OBSERVED(triangle-bashkit), verified by render; `attribute_type` values TESTED 2026-11-05]: named point attributes on the instancing mesh reach instances through a shader Attribute node with `attribute_type` INSTANCER. One float3 held seed, hue and a flag, a second held scale and lit share, with Object Info Random as fallback so a plain collection instance still varies. Feed instance scale back into window UVs or stretched blocks stretch their floors. `interpolation = 'Closest'` on a window atlas switches off mip averaging so a far window stays a spark instead of dissolving into a dim facade. Stills only: twinkle under camera motion is untested.

## Bulk edits to materials

A bulk multiply over materials compounds on shared datablocks. A `scale_emission` run across a kit's pieces hit shared materials repeatedly and turned every rose window black: copy the material before scaling. Same class: a relight loop multiplies unlinked strengths, so it must run last and once, materials made later are tagged to skip it, and an animation layer multiplies in front of the strength and never replaces it. Linked strengths are not touched by such a loop, which silently hides some emitters from it. OBSERVED(triangle-bashkit).

## Dark materials: metal, crystal, rock

Evidence from self-critique passes on one kit's sheets [OBSERVED(triangle-bashkit)]. Glass is in eevee.md, section 4.

**Damp bark that will not darken** [OBSERVED(client-commission), Cycles]: lowering base colour substantially barely moved mean weave luma, because specular and sky reflection now set the value. Past that point cut specular, and expect form loss. A value mask drawn from the silhouette also counts grass and vine in front, so use it for comparison only.

**Dark metal that reads.**
- Triangular plates on a staggered lattice, each with a real seam, chamfer and a small tilt scaled by its short side; scaled by the long side, slivers crumpled like foil.
- A small pane tilt worked on curtain walls; larger tilts made a black and white harlequin, so step it up from near zero. Moving shared nodes a few centimetres does the same job on real glass.
- Rivet heads kept flat; taller cones sparkled like a starfield.
- Heat tint at full strength was an oil slick, so it was cut and its mix capped.
- Metal base colour is the mirror strength, so keep it far above black: a mid-dark base still reads near black. Metal also needs something to reflect (The split sky, above).
- Metal takes no diffuse lamp light, so interior shells and awnings use a partial metallic so lamps show on them. That is a working exception to binary metallic (the `art-direction` skill, light-and-color.md, Material believability), for this one reason.
- Mill scale textures read as marble patches from mid distance on.

**Faceted crystal.** Each shard runs its own smooth ramp and value, each facet takes a value from its True Normal, plus Layer Weight on True Normal so camera-facing facets lift to the pale hue, and `scene.render.dither_intensity` 1.

**Rock.** Split a coarse triangle lattice by midpoint displacement with offset proportional to edge length, so large planes survive. Store tone per facet and inherit mostly from the parent, since an even mix read as confetti.

**Masonry ruins.** Lay loose trapezoid blocks and let a `keep(x, y)` test drop blocks, so a wall stops and shows its thickness with no booleans.

## Wet ground and water

Screen traced reflections [OBSERVED(triangle-bashkit)]:

- Fresnel alone is weak near the camera, so harbor water used a raised IOR with Specular IOR Level at full, on purpose.
- A street near full wetness is a flat mirror; back the wetness off and keep dry roughness low.
- Puddles stay dielectric: a dark metal multiplies reflections by its base colour and goes flat.
- BLENDED decals do not appear in screen traced reflections and reflect only the light probe, which showed as a flat purple sheen until Specular IOR Level was 0.
- A grazing ground plane mirrors the horizon glow, so far ground specular is 0.
- Olive cast on dark wet stone came from green neon plus magenta sky summed in dry specular, measured in the frame. Fixed by keeping green lowest in base colours and a violet Specular Tint on dry stone only, so water still mirrors true neon.

## Sharp carving with no booleans

Carved type and lead lines with no booleans and no swept tubes [OBSERVED(triangle-bashkit)]: draw into a signed distance field on a numpy grid, take level sets by marching squares, feed outlines to `mathutils.geometry.delaunay_2d_cdt` as constraints, and read each vertex height back from the field. One field gives a V cut, raised relief, lead came or pane edge. A fine grid per glyph height still builds a frieze quickly. A carved band must stand proud of its wall by more than the cut is deep or the glowing floor ends up inside the wall. Too heavy a stroke weight closed a double ring into a disk; check rings at the weight you use.

## A geometry check needs a control

A check that cannot fail proves nothing, so test the test [OBSERVED(triangle-bashkit)]. Sliding each train car along its beam testing mesh overlap gave 0 pairs; dropped into the beam as a control it gave many, so the test detects contact. The same test against a station proved no train could pass, because the hall's hip ends closed across the track. For scatter, test rows by measurement against a control: compare the structure factor peak and the global sixfold (hexagonal) order of the scatter with a jittered lattice's; a row-free scatter scores far lower on both.
