# Scale: making size read

How size is made to read. Scale advice previously lived in four files; this is now its only home. Tags: defined once, in the `maintaining-skills` skill.

## Scale is inference, not frame area

The viewer infers size from the chain of known-size things between the camera and an object, so the rung chain has to be designed before anything else is placed. OBSERVED(triangle-battle), scene 02, the most important lesson of that build. A mass that fills the frame reads as NEAR. A mass that is smaller in frame but sits behind several layers of recognisable, known-size objects reads as COLOSSAL, because the viewer computes its size from the chain in front of it.

The failure that taught it: a giant structure occupying a large share of frame width read as a nearby wall and felt unimpressive (OBSERVED(triangle-battle)). More surface detail did not help. The fix was geometric: move it further away, let it shrink in the frame, and put a chain of known-size things in front of it. The client's own reference is a skyline of ordinary buildings, then an obelisk behind them, then a spire behind that, then something larger still. Each rung lets you read the next.

**The working method: design the depth chain explicitly, as a list of rungs, before placing anything else.** For each rung write what it is, its real height, its distance from the camera, its share of the frame and what it occludes. Expect the largest object to be a modest fraction of the frame.

Worked example (HEURISTIC, illustrative values, not the scene 02 numbers). Frame fraction is the share of frame height: `(height / distance) / vertical_FOV_in_radians`. Here the vertical FOV is 30 degrees, which is 0.52 rad.

| Rung | What it is | Real height | Distance | Frame height | Reads as |
|-|-|-|-|-|-|
| 0 | Crowd grain: figures, carts, banners | 2 m | 100 m | about 4% | the ruler everything else is measured against |
| 1 | Ordinary buildings: floors and windows countable | 30 m | 400 m | about 14% | a skyline the viewer already understands |
| 2 | Obelisk behind the skyline | 100 m | 1,500 m | about 13% | taller than the skyline it peeks over |
| 3 | Spire behind the obelisk | 230 m | 4,000 m | about 11% | taller than the obelisk, measured against it |
| 4 | The largest thing | 600 m | 12,000 m | about 10% | enormous, because four rungs sit in front of it |

The frame fractions barely change down the list while the real heights climb from 30 m to 600 m. That is the point: the viewer sees a similar on-screen size getting hazier and further back, and concludes that the far object is huge.

What makes a chain work:
- **Each rung is recognisable at its own size.** Floors, windows, cranes, doors, figures. A rung with no countable feature is not a ruler and adds nothing.
- **Each rung partly occludes the next and sits one haze band further back** (banding: composition.md, Depth banding). Overlap proves order, haze proves distance.
- **Several dwarfing objects at different distances beat one.** They can be measured against each other. A single colossus on an empty horizon has nothing to be compared with and reads flat.
- **Do not scale a rung up to fill the frame.** The moment the largest object is large in frame it stops reading as far, and the chain collapses back into a wall. If a brief asks for impact, add a rung or a distance, not frame area.
- **The crowd is the lowest rung** (crowd grain, below).
- **Test it in grey before look-dev** (grey massing: SKILL.md, Review practices). Ask someone how big the largest thing is. If the answer is "big, and close", the chain is wrong.

Dominance follows from the same logic: a giant is dominant by value mass and by the rungs that frame it, not by silhouette area. The older habit of always cropping the giant, and the habit of always keeping it large, are both reconciled in the next section.

## Crop it, or chain it

Cropping and chaining are opposite ways to handle a giant, and each is right for one case. Cropping hides the measure: the viewer cannot size what runs off the frame edge, so it suits a giant that is close to the lens when the subject is menace or mystery. Show the base and one corner, with a face extending past the top of frame (Blade Runner 2049 shows K as a small silhouette low in frame against massive amber-lit walls with open space above). Chaining supplies the measure: it suits a giant that is far away when the subject is how big it is, and the viewer has to be able to measure it against rungs of known size. One object filling the frame cannot do both jobs. A close giant cut by the frame edge also gives the foreground its hierarchy: plant it near the lens and let the scale run down from it to specks.

## The levers that create colossal

Scale is a relationship, not a number: a 300 m cube with no references looks like a toy at any resolution. These levers work together.

- **Human-scale referent.** Put something of known size in frame, ideally small, in front of the giant. A small figure in front of a much larger middle-ground element makes the giant look huge; without the comparison the same giant looks far less impressive (Ctrl+Paint, "Are you remembering FMB"). Keep referents small relative to frame height and consistent in size.
- **Detail frequency.** A giant reads large when it carries detail at several module sizes. If a 300 m mass has panels the size of house walls and nothing finer, it reads small. Add seams at door scale, trenches, vents, masts, rivet lines and window-like apertures at many sizes: big plates, then sub-plates, then fine grooves, with light and wear at each level.
- **Overlap and layering, reconciled with the chain.** Use at least three clearly separate planes, each visibly in front of the next; a chain may carry four or five rungs and still read, because each rung is a recognisable known-size object that partly occludes the next. Three planes is the floor, and extra rungs are fine when each is a countable ruler.
- **Atmospheric perspective.** Distant forms lose contrast, saturation and detail and take on the ambient colour. Put the base of a monolith partly in haze and let its upper portion emerge, so it reads as tall and distant (value windows per band: composition.md, Depth banding).
- **Negative space.** Empty sky or ground around a small figure makes the system feel overwhelming, so do not fill every corner. For a deliberately dense frame use filled quiet masses instead of blank canvas (composition.md, Rest areas).
- **Leading lines and diagonals.** Run the main line on a diagonal from the foreground to the giant's base; rubble lines, light beams and formations can point at the focal point.
- **Value and saturation direction.** The eye goes to the highest contrast, highest saturation and sharpest area. Make the focal point the brightest, most saturated, sharpest thing against the darkest nearby mass, and desaturate and darken competitors.

City scale levers, each from a rejected first pass. OBSERVED(triangle-bashkit), by eye on one kit.

- **Level camera, vertical lens shift.** For a colossus seen from a distance, verticals stay straight and the subject read far larger than tilting up. The slight tilt in Camera height is for one close giant.
- **Very fine shader windows on a megastructure are a rung.** Work out the metres per pixel at the structure's distance and lens; floors only a pixel or two tall still read as countable, and the structure then reads as huge at a large share of frame height, once the windows gave it a rung.
- **A dense low city.** A sparse one made landmarks look like table models.
- **Lit share falls with distance while brightness rises.** Gain alone burned a white band across the far city; the falling share is what turns a far city into dust.
- **Low filler plus a haze lift on the axis.** Black filler cut the hero into a bad shape.
- **Long lens for portraits of towers.** On a normal lens they read as cones from perspective alone; a longer lens fixed it.
- **Tilt a torus.** From a low camera it needs a fair tilt before its hole opens; too little and it reads as a mushroom. Step the tilt up and check from the shot camera.

## Camera height and how much a frame holds

Camera height set how much content a frame could hold, so settle it before adding objects. OBSERVED(triangle-battle), two scenes of one project on flat or gently rising ground; the mechanism is geometric, the numbers are that project's. At a low camera on flat or gently rising ground the ground plane compresses into a band near the horizon, everything occludes everything behind it, and there is physically nowhere to put more content. Raising the camera and tilting down opens the ground into usable area, and depth becomes vertical distance in the image. On that project, raising the camera turned one crowded stripe into several readable bands, and on a later scene identical content that filled the frame from a low camera occupied a small fraction of it from high ones, so a high camera has room for several times the content If a brief asks for "much more going on", move the camera before adding objects.

Where the horizon lands for a camera pitched down by `pitch_down`:

```text
horizon_frame_y = 0.5 + 0.5 * tan(pitch_down) / tan(half_vFOV)
```

A second effect: terracing and ground relief that is invisible from a low camera reads clearly from above. Terrain that seems not to be working may be a camera problem and not a terrain problem.

The usual objection to a high camera is that it reads as a strategy-game screenshot and loses the looming foreground. That holds only if everything near the lens is short. Tall architecture close to the camera rises into an elevated view and preserves foreground scale, so breadth and looming are not mutually exclusive.

A low camera (hero height, tilted up slightly, horizon in the bottom quarter) puts the viewer at the heroes' point of view and suits one close giant, at the cost above. A workable compromise for a broad shot (HEURISTIC): horizon near the upper third line, so about two thirds of the frame is ground plane carrying tiered fights, with the giant rising above the horizon and cropped by the top edge and tall structures near the lens keeping the foreground tall. Colossal scale no longer depends on a low camera at all once the chain is in place.

Choose per shot. Low = one close giant. High = breadth. Do not split the difference by accident.

## Lens

Focal length is an emotional decision: choose a number, justify it, and do not leave the default by accident.

- Wide (14 to 28 mm): immersion, stretched space, dynamic movement, exaggerated foreground. Good for being among the fight.
- Normal (35 to 50 mm): neutral, close to the human eye. Safe default for a grounded look.
- Long (85 to 200 mm): compresses space, makes the background larger relative to the foreground, isolates subjects and makes the viewer an observer. Good for monumental looming and for packing layers into a dense frame (In Depth Cine, focal length).

For giants the effect is counterintuitive. Wide lenses exaggerate near objects and shrink distant ones, so a very wide lens makes a distant colossus smaller and works against it. A longer lens (50 to 85 mm full-frame equivalent) from further back makes the distant giant loom behind the small foreground. If you want wide-angle drama, put the giant close to camera and cut it off. This is convention-level optics.

Field of view, for a 36 mm full-frame reference: `FOV = 2 * atan(sensor_width / (2 * focal_length))`.

| Focal length (36 mm sensor) | Horizontal FOV |
|-|-|
| 18 mm | 90.0 degrees |
| 24 mm | 73.7 degrees |
| 28 mm | 65.5 degrees |
| 35 mm | 54.4 degrees |
| 50 mm | 39.6 degrees |
| 85 mm | 23.9 degrees |
| 135 mm | 15.2 degrees |

A larger sensor at the same focal length gives a wider FOV, so use one sensor width consistently. In a 16:9 frame the vertical FOV is smaller than the horizontal, and tools that auto-fit the sensor value to the larger dimension change what fits, so check the sensor-fit behaviour before reasoning about the frame.

The vertical arithmetic, corrected. For a 36 mm wide sensor at 16:9 the sensor height is 20.25 mm, so `half_vFOV = atan(10.125 / focal_mm)`. At 24 mm that is **22.88 degrees**. Horizontal: `half_hFOV = atan(18.0 / focal_mm)`, which is 36.87 degrees at 24 mm. To place a feature at a known height in frame:

```text
frac_above_centre = tan(angle_from_centre) / tan(half_vFOV)    # 0..1
frame_y = 0.5 + 0.5 * frac_above_centre
```

Solve it the other way to find how far back the camera must sit. This is how a real spec error was caught: a camera placed too close to a tall tower put the key feature far above what the lens covered above centre, so it was entirely off frame. The table caught it; looking did not (OBSERVED(triangle-battle)). Compute it rather than memorise it.

### Camera imperfections

Subtle imperfections sell realism: a degree or two of roll, slightly imperfect framing, a very mild vignette, faint chromatic aberration toward the edges, light grain, glare around bright cores. Heavy fringing, strong barrel distortion, dirty-lens overlays and grain visible at poster size are gimmicks. The test: if a viewer can name the effect in a half-second glance, it is too strong.

## Depth of field and the miniature tells

Depth of field is a decision about what is sharp: let one or two depth planes fall off, and use foreground bokeh from out-of-focus embers or debris as a framing device. Think in f-stops (convention): f/2 to f/4 is shallow, f/5.6 to f/8 gives gentle falloff with a readable background, f/11 and up is mostly sharp. A vast field wants f/5.6 to f/11 focused on the hero group; a close hero insert wants f/2 to f/2.8. Do not blur the focal subject to look cinematic, and do not blur everything evenly. Intent beats amount.

**The miniature trap.** Depth of field depends on real scene scale. If heroes are 0.1 units tall and the camera is 0.5 units away, strong blur looks like a macro shot of toys. Build at real-world size (heroes 1.5 to 2 m, giants 200 m or more) or you get a tilt-shift miniature look that kills the scale you are fighting for. Over-blurred renders read as small for this reason.

Research additions, each with its own confidence:
- Shallow depth of field is the primary tell that gives away miniature scale, ahead of geometry or texture. Match the f-stop to the depth of field the subject would have had at full scale (CORROBORATED, high on the principle).
- If anything animates, motion speed carries scale: camera speed scales with the square root of the scale factor, the one hard number in the research. It applies to real-time motion only, never to static passes (CORROBORATED, high on the formula).
- Detail is allocated by screen time as well as by distance: a shot held a second or two can carry shortcuts the audience cannot pick up, while a long-held shot needs real detail (ASSERTED, one interview).
- Scale errors are detected pre-verbally. Review by asking "does it feel wrong", not "what looks wrong" (ASSERTED).

## Distant vistas: cards and the crossover

Distant vistas are conventionally cards or shells that receive whatever budget is left over, and a senior environment artist's stated approach is to treat them as a painting and focus on composition (VERIFIED-PRIMARY). A card cannot survive an approaching camera, so an explorable scene needs a documented crossover distance where the card becomes geometry.

## Crowds as grain

At city or aerial scale individual figures become specks, and that is useful rather than a problem. OBSERVED(triangle-battle). They become the texture that states how large the architecture is, exactly as workers do in a construction photograph. Specks beside a floor, a bay or a doorway are the cheapest ruler in the frame. What follows:

- **Keep their size true.** They are measuring the architecture, so skip any grow-with-distance cheat for them.
- **Spend nothing on individuals.** The lowest level of detail is enough, arranged in islands and moats, not a uniform sprinkle.
- **Put the detail in a few incidents near the lens.** The design needs a small number of genuinely large, readable incidents, close enough for full detail. Everything else is density.
- **The grain is the lowest rung** of the scale chain; each rung above it is measured against the one below.

Batching and level-of-detail implementation: the blender skill, references/scene-code.md.

## Scaling the subject to the story

On one project a hero that was legible did not carry a narrative read until it was scaled up, and that was the single change that made the scene stop reading as "objects near a building" and start reading as an event (OBSERVED(triangle-battle)). If the viewer is meant to care about an interaction, the elements involved need enough frame area to show their relationship: step the hero size up on a proof and ask what the frame is about. Detail sizes do not survive a camera move: element dimensions written for one camera distance must be rescaled by the distance ratio, or thin details drop below a pixel.

## Display scale

Judge size and count at the real display and viewing distance, not the monitor: convert each element to physical size at that display. Dome layer: 1° of arc = pi x diameter / 360, about 3.1 in on a 30-ft dome (HEURISTIC, derived from the formula, 2026-11-04).

## Scale pre-flight

Answer each from the proof render.
- [ ] Is the depth chain written as rungs, each with a real height, a distance, a frame share and what it occludes?
- [ ] Is the largest object a modest fraction of the frame, and behind at least two known-size rungs? (If it is close and the subject is menace, is it cropped on purpose instead?)
- [ ] Is a human-scale referent in front of the giant, and does the giant carry detail at several module sizes?
- [ ] Is the camera high enough that the content fits? If the frame looks full but sparse, check camera height before adding objects.
- [ ] Was the focal length chosen on purpose, and does it support colossal (longer and farther back, or the giant cropped close) instead of fighting it?
- [ ] Is the scene built at real-world size, with depth of field moderate and one clear sharp plane?
- [ ] Are camera imperfections too subtle to name at a glance?
