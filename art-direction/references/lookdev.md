# Look-dev: reference profile, real objects, iterating, mirror enclosures, motion

What to settle before and during look-dev on a generated image or animation. Everything here is a technique, tagged with where it worked. Provenance tags: the `maintaining-skills` skill (Provenance tags). The execution side (scripts, renders, the motion tool) is in the `blender` skill, `references/pipeline.md`.

## Measure the reference into a target profile

If a reference exists, measure it before building. The fields below are for emissive-on-black work; replace them with what matters for a lit scene. A profile holds:

- lit, dark and hot fractions
- artifact count and size distribution
- per-hue halo strength
- coverage of the frame
- motion speed and alive fraction, if a clip exists

Score candidates against that profile rather than thresholds picked by eye. OBSERVED(cylinder-mirror): the reference image sat in the project folder from the first message and went unmeasured until a late revision, most of the feedback rounds walked back toward it, and a threshold invented by eye proved unpassable. This is the threshold rule in composition.md, section 15, applied before the first render instead of after.

## Real objects come from photographs

A real installation or object is modelled from photographs of it, not from working files, and a confident gap fill is the expensive failure. OBSERVED(triangle-bashkit): a real obelisk's panels were filled from superseded art in a working file and presented as real, other sources were partly right, and photos settled it. State which file is true and how you know, cite the photo, and say "not found" instead of inventing or rotating art. True geometry, true size and true timing stay the default for a real object.

Check how it is put together, not only its surfaces: the joints and member sizes. OBSERVED(client-commission): a render gave a real frame joint hardware and members it does not have; reference photos showed the difference and it cost a redo. With the obelisk case above, two projects.

## Mirror enclosures

Spinning the whole enclosure rotates every echo rigidly: clips the client read as rigid measured a high tangential share and a low residual (OBSERVED(cylinder-mirror)). Move the objects instead. Measure tangential share on your own clips.

Black wall panels do not thin echoes evenly. They delete every echo in that azimuth, showing as a permanent wedge. Thin by lowering all walls' reflectivity together, so 2nd and 3rd copies fade, and check lit share per sector on a test render as you step it down; a dense scene may want to keep its original reflectivity, and a converging shape can lose its star pattern (OBSERVED(cylinder-mirror)).

Partial black is fine where a ray-cast shows those faces are never first-hit (OBSERVED(cylinder-mirror)). Echo density scales roughly with emitters x sides x bounces (HEURISTIC).

## Iterating with a client

Techniques, each from rounds that cost something. None is a rule; each says when it does not apply.

- **Restate a brief word that has two readings before building on it.** OBSERVED twice: a request for "light animations" was read as animating lights when it meant not heavy (triangle-bashkit). Emphasis marks on the word were the clue. Skip it when the word has one reading in context.
- **Change one dial per take, or bracket less, target and more.** OBSERVED(cylinder-mirror): correcting toward "too busy, more black" overshot into a set too sparse, and a bracket of less, target and more landed. OBSERVED(client-commission): a round of many different species and weaves drew "too much variation"; one design with one dial changed per take landed and the client picked one. Ask how wide a round should go. A first round of broad exploration is the case where wide is right.
- **When a candidate fails the same way twice, change the geometry, not the parameters.** OBSERVED(cylinder-mirror): several candidates failed the same way version after version while their parameters were retuned each time; new skeletons fixed them (OBSERVED(cylinder-mirror)). A second identical failure is the signal to rebuild the structure. A failure that changes shape between versions is still a tuning problem.

## Motion

Do not judge motion from 4 or 5 stills. Give the reviewer speed in % of frame width per second, adding deg/s for a dome master, plus rigid share, alive fraction, and trail and slit-scan images, and state clip length, fps and frame spacing (OBSERVED(cylinder-mirror), after rejected motion passes). How a designed camera move should look: camera-motion.md.

Some benchmark questions stay answerable with frames shuffled, so a good score does not prove temporal understanding (arXiv 2505.14321, abstract read 2026-11-04, VERIFIED-PRIMARY).
