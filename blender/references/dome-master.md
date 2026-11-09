# Dome master / fisheye cameras

Dome layer. Dome deliverables are square fisheye dome masters rendered with a Cycles
panoramic camera (`cam.type = 'PANO'`); everything here was tested in Cycles. Which mapping
and master size to deliver is a studio choice, not a Blender fact.

## Default: Fisheye Equidistant for fulldome

The fulldome standard is the **equidistant (angular, f-theta) fisheye**, which IMERSA
and Paul Bourke both document as the dome master format. It's a square frame with the
circle inscribed, black corners, and dome front at the bottom of the frame. Blender's
manual also recommends Fisheye Equidistant for full-dome. Dome playback and warp systems
expect it. So unless a venue asks for something else:

```python
import bpy, math
cam = bpy.data.cameras.new("dome")
cam.type = 'PANO'
cam.panorama_type = 'FISHEYE_EQUIDISTANT'
cam.fisheye_fov = math.radians(180)   # or the project's FOV
```

There's no lens setting. The circle fills the square at any FOV, TESTED 2026-11-04 in
5.2.0 at 120, 160 and 180.

**What equisolid looks like if it's played as equidistant:** radial error is zero at
the zenith and at the rim. Content shifts outward by about 3.7° at 45° and by up to about
3.8° around 50-55°. The center is magnified about 11% and the rim compressed about 21%.
Use equisolid only when a venue explicitly asks for it.

**Fixed-dome FOV:** a master rendered at 160° and played as a 180° dome stretches every
angle by 180/160. Make sure that's intended, for example as a deliberate zoom or for a
truncated dome.

Sources ([DOC, page not re-checked]):
- https://paulbourke.net/dome/fisheye/
- https://paulbourke.net/dome/fisheyetypes/
- the IMERSA fulldome file specs
- Blender manual, Cycles cameras

## Equisolid: fisheye_lens has to match fisheye_fov

In `FISHEYE_EQUISOLID` the circle fills the square only when
`2 · lens · sin(fov/4) = sensor_width / 2` (sensor_width 36, sensor_fit AUTO). A lens below that
leaves a thin black margin; above it the circle edges are cropped, and a lower field of view
needs a higher lens. Working values with about 1% margin: 12.63 mm at 180°, 13.86 mm at 160°.
TESTED 2026-11-03 in 5.2.0 Cycles. Derive other values from the formula above.

**How to check it:** look at it on a NON-dark background. Against a black world the edge of
the circle is invisible, which is exactly why this setting is hard to judge. Render with a
white world at 1 sample, then measure or view the circle (TESTED 2026-11-04).

Check `scene.camera` is the panoramic camera first: a file can carry an active perspective
camera beside its fisheye, and a wrong fill report came from exactly that
(OBSERVED(cylinder-mirror)). That file's fisheye measured as the
formula predicts (TESTED 2026-11-04, 5.2.0).

## Equidistant

`FISHEYE_EQUIDISTANT` (r ∝ θ) has no lens setting. `fisheye_fov` alone maps onto the
frame, and the circle always fills it. That makes it hard to get wrong, but it is a
different radial mapping from equisolid. Do not swap between the two inside one project
without telling whoever owns the content, because content near the rim lands at different
radii.

## Code (equisolid, for a venue that asks for it; the default is equidistant, above)

```python
import bpy, math
scene = bpy.context.scene
cam = bpy.data.cameras.new("dome")
cam.type = 'PANO'
cam.panorama_type = 'FISHEYE_EQUISOLID'
cam.fisheye_fov = math.radians(160)
cam.fisheye_lens = 13.86          # the ~99% working value; exact fill is (cam.sensor_width/2)/(2*math.sin(cam.fisheye_fov/4))
scene.render.resolution_x = scene.render.resolution_y = 2048   # square dome master
```
