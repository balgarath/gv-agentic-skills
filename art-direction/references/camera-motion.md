# Camera motion: how a designed move should look

Pace, eye height, the shape of a move, arrivals and endings, and time changes, for a designed camera moving through a fixed or authored scene (not a player-controlled one). Renderer-agnostic. Provenance tags: the `maintaining-skills` skill (Provenance tags).

**Status, 2026-11-08.** Every item here is a technique at a weak tag: a sourced starting value or one project's observation. None has been tested on a finished film judged in playback. Lens choice lives in scale.md (Lens); judging motion from numbers and clips lives in lookdev.md (Motion); building the move in bpy (keys, roll, clearance, motion blur, encode) is the `blender` skill's job, in its `references/animation.md`.

## Pace

Speed is easiest to judge in the unit lookdev.md uses for motion: percent of frame width per second, with deg/s added for a dome master.

- **Pans.** RED's guidance: no faster than one frame width per 7 s at 24 fps with a 180 degree shutter, which is about 14 percent of frame width per second (DOC, page not re-checked). A guideline, not a cliff. A longer lens or smaller sensor means slower rotation for the same judder; 48 or 60 fps smooths it.
- **Orbits: walking pace is the portable starting value.** A ground-level orbit read as calm at roughly walking pace along the path (HEURISTIC). Convert to deg/s for a given radius: deg/s = 57.3 x speed / radius. For comparison, the pan rule at 35 mm (about 54 degrees of horizontal view) gives about 7.7 deg/s. Whether an orbit lands near that depends on its radius, so convert per shot rather than carrying a deg/s figure across.
- **Slow arcs.** One vendor glossary gives 90 degrees in 8 to 15 s, about 6 to 11 deg/s, with partial arcs of 45 to 90 degrees (ASSERTED, weak). A drone SDK's default orbit of 20 deg/s is a machine default and fast at short radius (DOC, page not re-checked).
- **When unsure, halve the speed** (ASSERTED, one education site).
- Motion speed also carries scale: scale.md, Depth of field and the miniature tells.

## Eye height, roll, lens

- A walking view sits at about 1.5 to 1.6 m eye height (ASSERTED, one education site).
- Roll stays at zero unless a tilted horizon is the point of the shot.
- One lens per shot. No source endorsed changing focal length mid-shot, and a stray focal channel reads as zoom wobble (ASSERTED). Which lens: scale.md, Lens.

## Shape of a move

- Ease in and out. Few keys, so the move reads as one gesture; the same source suggests 3 or 4 per 10 s (ASSERTED, one education site).
- Hold about 2 s on the hero view and on the final composition, and hold right after a reveal (ASSERTED, same source).
- Rise and settle: slow start, build, peak at the reveal, release (ASSERTED, same source).

## Arrival and ending

- **Plan the ending before tuning the move.** Look at the end frame before committing a path. OBSERVED(archway-d): a forward exit away from a light source landed on the dark side of the scene.
- **Exterior to interior.** Move to the entrance first, so the viewer expects to enter (ASSERTED, SIGGRAPH education material, page not opened).
- **A push toward a centerpiece through a tight door can read as arriving, not entering.** OBSERVED(client-commission), one case: pushing toward a hanging centerpiece made it grow and crop the room, so a stop near it read as arriving. The client's choice there was to commit, fly into the object, then cut. That is one option; a wider door, a higher path or a stop short of the threshold are others nobody has tested.
- **Looking up under an overhead structure.** OBSERVED(archway-d), one shot: aim at the structure's mass centre, not its nearest underside, with the tilt soft-capped; aiming at a fixed pitch toward the underside left half the frame sky. Passing under it leaves a stretch of plain sky between losing the structure and finding the horizon, and that gap is geometric, so no tuning removes it: plan what fills it or end the shot another way.
- **Rising into an overhead panel** (the other way to end that shot, OBSERVED(archway-d)). Fix the heading before the tilt gets high, because at high pitch any yaw reads as the image rolling even with roll at zero. Track the structure's mass centre, capped at the final view pitch, so it never leaves frame; this removes the sky gap. Let ground motion ease to rest under the target while the climb holds steady and never slows, and let the cut or end card take over in flight, so no slow-down is seen. Scout the end-of-shot colours from a temporary camera before choosing the target: they differed a lot from panel to panel.

## Time change

- A cross dissolve of about 1 to 2 s at 24 fps (Adobe help gives 24 to 48 frames; ASSERTED). Longer feels dreamlike. It suits a time change on the same subject, and overuse feels like a slideshow.
- A dissolve between a day and a night render reads as a dissolve, not as dusk: rake light showed on the sunlit scene mid-fade and trees greyed out (OBSERVED(client-commission), one frame judged by eye). If the brief wants dusk, a dissolve will not deliver it.
- The same camera for day and night made the two comparable across every set (OBSERVED(client-commission)).

## Gaps

GAP(2026-11-06): no authoritative source gave a doorway speed or height, an ease percentage, or several day-night fades in one short shot. These are judgment calls until a project proves them; findings land here.
