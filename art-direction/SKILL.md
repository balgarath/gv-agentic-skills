---
name: art-direction
description: Use when deciding what an image or scene should look like - composing a frame, making something read as colossal or tiny, lighting design, color palettes, value structure, readability of crowds or abstract characters, single-image storytelling, planning a camera move, or designing an explorable 3D space with multiple cameras. Renderer-agnostic - applies to Blender renders, Unity scenes, photographs, and 2D canvas work alike. Triggers on "looks flat/amateur/boring/small/cluttered", "why doesn't this look cinematic", "compose this shot", "art direction", "the scale doesn't read", "palette", "where should the camera go", "how fast should the camera move". If the render is BROKEN (white, black, errors, missing elements), that is the blender skill, not this one.
---

# Art direction: what to aim at

How to decide what makes an image or a space good, and how to check the
decision with a test instead of a feeling. Nothing here depends on a
renderer; the Blender implementation lives in the `blender` skill.
**Triage:** broken is there, bad is here.

**Provenance tags** are defined once, in the `maintaining-skills` skill,
Provenance tags.

## How this skill is built

- **Firm checks** (below) say when an image is broken for any project.
- **Everything else is a technique:** what it is, where it worked
  (OBSERVED(project) or a source), and when not to use it. Pick techniques
  per brief; none is a rule.
- `projects/` holds one project's cases and decisions; `house/` holds your own
  conventions. Neither is general truth. Both ship empty; each folder's README
  says what belongs there.

## Firm checks: the image is broken if

1. **The subject is lost.** At thumbnail size, with a squint, a fresh viewer
   cannot find the subject or name what the frame is about.
2. **Silhouettes merge.** Key shapes fuse into one mass, or an important
   shape sits on a background of its own value, at the size it is judged.
3. **The read is wrong.** A viewer misreads the event (a brace that reads as
   pushing), the size (a colossus that reads "big, and close"), or the shape
   (it resembles something that would embarrass the client).
4. **A dark distant object reads paler than the sky behind it.** Within its
   scope (objects darker than the haze) it cannot occur, so it reads false
   (`references/composition.md`, section 4).
5. **The subject is out of frame or hidden**, whatever the anchor numbers say.
6. **It was not looked at.** A frame counts as checked only once someone has
   viewed it, and a measurement that does not move when the picture visibly
   does is a broken instrument, not a pass.

## Scale is inference (the technique that does the most work)

OBSERVED(triangle-battle), at full price. The viewer infers size from the
chain of known-size things between the camera and the object, not from frame
area; a mass that fills the frame reads as near. Write the depth chain as
rungs (what, real height, distance, frame share, what it occludes), each
countable and partly occluding the next. For more impact, add a rung or a
distance before adding frame area. Check: grey massing, then ask someone how
big the largest thing is. Method and worked tables: `references/scale.md`.

## Before look-dev

If a reference exists, measure it into a target profile and score candidates
against that rather than thresholds picked by eye; then build, review by eye
against it, fix (OBSERVED(cylinder-mirror)). Restate any brief word with two
readings before building on it. `references/lookdev.md`.

## A working order

Each step feeds the next; content placed before steps 1-4 turned dense frames
to noise (OBSERVED(triangle-battle)). Detail and alternatives live in the
references.

1. **The read and the cast.** One sentence; one dominant element, one
   subdominant, subordinates. Cut what does not serve the sentence.
2. **The camera,** before content: position, height, lens, aspect. Camera
   height set how much one project's frames could hold (OBSERVED(triangle-battle), two scenes;
   `references/scale.md`). A wide lens shrinks a distant colossus. Verify
   framing with an anchor table and projection math (`blender` skill
   `scripts/frame_check.py`).
3. **Value masses.** A few flat value shapes first; in a dark frame, one value
   dominating and connected darks gave the structure (`composition.md`).
4. **Depth bands and atmosphere.** Each band narrower in value than the one in
   front; in haze, distant darks lift and lights dim.
5. **The scale chain,** projected, rungs in order.
6. **Placement and grouping,** for crowds: clusters with real gaps, a flow
   field, one accent per cluster for formation reads.
7. **Hierarchy.** One primary incident, a few secondary, a quiet majority, for
   representational scenes; an abstract or reference-led brief may want many
   artifacts (measure the reference). Under a clipping view transform, size is
   the dominance channel left.
8. **The eye path,** for designed cameras only (CONTESTED for explorable
   space: `references/staging.md`).
9. **The tests** before any expensive render: greyscale, posterize, squint,
   thumbnail, flip, silhouette, busyness, crop. Ask a reviewer whether it
   *feels* wrong; scale errors are felt before they are named.

## Why images read as amateur (the short diagnosis)

| Tell | Fix lives in |
|---|---|
| Flat even light, nothing shaped | a dominant key, dim cool fill, rim; shaped darkness: `light-and-color.md` |
| Everything sharp, clean, unweathered | roughness variation, wear, resolvable bevels, DOF with intent: `light-and-color.md`, `scale.md` |
| Scale does not read | the chain: `scale.md` |
| No atmosphere, hard cutoffs to black | height-falloff haze: `light-and-color.md` |
| Uniform busyness, confetti, wallpaper | masses, moats, loud budget: `composition.md` |
| Hues fight or wash out | pick a palette approach for the brief; near-white cores, hue in the halo: `light-and-color.md`, Color design |
| Pretty but empty | a before and an after: `staging.md` |
| Abstract shapes with no character | silhouette, lean, limbs, aperture, gesture: `staging.md` |

## Review practices

Techniques, OBSERVED on the projects named in the references; grey massing and the anchor table saved rebuilds, the unintended-read pass caught near misses.

1. **Grey massing before look-dev,** final camera, judged at thumbnail. Not
   for emissive work on black, where the first proof is the emitters on black.
2. **Proof tests before any final,** re-run after the last scene change.
3. **Anchor table on every build.** It proves framing only, not visibility or
   a clear camera (`references/composition.md`, section 14).
4. **Unintended read pass on every sheet,** with a second reviewer
   (`references/staging.md`).
5. **Numbered contact sheets** the client answers by number
   (`scripts/contact_sheet.py`).

## Where to look, by moment

| You are deciding / seeing | Read |
|---|---|
| a dense or crowded frame; value masses; depth bands; grouping; rhythm and spacing; thirds, balance, visual weight; edges and busyness; hierarchy; eye path; running the tests; shots planned before the world exists; cameras broken by a layout change; how old paintings solved it; where sources disagree | `references/composition.md` |
| making something read big or small; the crop-or-chain choice; camera height; lens and FOV math; camera imperfections; DOF and miniature tells; distant vistas as cards; crowds as grain; heroes too small to carry the story; judging size at the real display | `references/scale.md` |
| lighting design, atmosphere, glow; picking a palette; neon looks cheap; coloured light eats the material colour; materials look fake; one hue glows and the others look weak | `references/light-and-color.md` |
| measuring a reference; modelling a real object or installation; a brief word with two readings; how wide a round should go; a candidate failing the same way again; mirror enclosures; judging motion | `references/lookdev.md` |
| planning a camera move, orbit, fly-in or walk-through; how fast to pan; where a move should end; a reveal that feels rushed; a day-to-night dissolve | `references/camera-motion.md` |
| shape language; subverting it; character without a face; faction readability; formations; story in one frame; what else a shape reads as; a footprint that reads as a box; crowds at night; what grey massing reveals; explorable worlds and multi-camera coherence | `references/staging.md` |
| what one project found or decided | `projects/` |
| your own house conventions | `house/` |
| proof sheet and composition numbers for one image | `python scripts/composition_sheet.py in.png out.png` |
| a numbered review sheet from a folder | `python scripts/contact_sheet.py FOLDER -o sheet.png` |

## Depositing findings

A lesson learned at full price goes to `INTAKE.md` in this directory before
the session ends, with OBSERVED(project), and a note on whether it holds for
every project or is one way that worked once. The merge pass
(`maintaining-skills` skill) integrates it; do not edit references mid-task.
