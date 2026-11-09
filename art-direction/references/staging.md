# Staging: character, readability, story, explorable space

Making abstract geometry read as characters, keeping two armies readable, putting a story in a single frame, and designing space a viewer moves through. Tags: defined once, in the `maintaining-skills` skill; research-sourced items carry their strength tag.

## Shape language, briefly

The standard theory, repeated across character-design teaching (CONVENTION; [Prolific Studio](https://blog.prolificstudio.co/blog/shape-language-in-character-design/), [CG Wire](https://blog.cg-wire.com/character-shape-language/)): circles read friendly and safe, squares read stable and strong but also stubborn or oppressive, triangles read dangerous, dynamic and cunning, which is why they are heavily used for antagonists. Diagonals read as dynamism, verticals as power, horizontals as calm.

What the convention offers:
- The dominant shape sets the first read; a secondary shape adds depth.
- Test every character as a solid black silhouette, because the shape has to work before details exist.
- Break the conventions only on purpose, so the subversion looks intentional. Round antagonists and triangular protagonists can surprise viewers but are risky and need careful handling.

## Subverting the prior

Shape conventions describe a feeling (energy versus mass), not a moral, so a subverted casting can work: a triangle is dynamic, directional and agile, which are legitimate hero traits, and an upward-pointing triangle reads as aspiration; a regular solid is static, enclosed and heavy, and stable becomes immovable and oppressive when scaled up and made indifferent. Read both sides at the level of feeling.

The risk is that audiences are trained to read a shape one way, so a subverted casting can make both sides read the same. It works when the other channels carry the difference on purpose: behaviour and arrangement, colour and light, order against individuality, orientation, and repetition (CONVENTION). Indifference reads as menace: no gaze, no lean, no reaction. A form with no front, no face and no eye is the more inhuman for it.

## Personality without a face

Personality has to come from features a viewer can point at and name, and the parametric approach to it is weak. OBSERVED(triangle-battle). Varying proportion, lean and line quality (a nearly clean outline reads as veteran, a scrappy one as rookie; a small outline jitter reads as hand-drawn, a larger one as broken geometry) is real but WEAK. It was tried first on a mass battle and the client still saw no personality At the size a crowd unit occupies in frame, a few percent of proportion difference is invisible, and invisible variation is indistinguishable from noise.

Two cheap things moved the needle (OBSERVED(triangle-battle)):
- **Limbs.** Two short two-segment arms with an elbow, projecting from the lower part of the shape. A shape with arms is a body: it has reach, posture and intent, and it can hold something. Keep them short: long thin arms read as spider legs, and shorter, slightly thicker tubes read as limbs. Step the length down on a proof until they stop reading as legs (OBSERVED(triangle-battle)).
- **An aperture.** A single short lit bar set into the body. Not a face and not an eye, but doing an eye's job: it tells the viewer what the thing is attending to, and rotating it makes the unit look somewhere. This was the single biggest change. A triangle with a glowing slot reads as a creature; the same triangle without one reads as a shape.

Then gear rides the limbs, and the weapon carries the gesture (OBSERVED(triangle-battle)). A spear held low and forward is a charge, held high is a signal, planted is a brace. Weapons and personality are the same problem, so build gestures as presets that choose limb angles and implement together rather than randomising them separately. Give each faction a distinct death as well.

The wider toolkit for characters with no face (CONVENTION):
- **Silhouette.** If the outline is distinct, the character is. Vary heroes by proportion (tall narrow, wide low, with notches or a bent tip). A leader gets a bigger or more distinctive outline.
- **Posture and implied motion.** A forward lean of 10 to 25 degrees reads as a charge. A triangle balanced on a vertex or tilting mid-leap carries unstable energy; one planted on a face is stable. Make each figure's line of action flow in its direction of travel, and make every pose communicate a clear intention ([Disney's principles of staging](https://abc7news.com/post/the-12-principles-of-animation-as-illustrated-through-disney-and-disney-pixar-films/1437293/)).
- **Anticipation.** A small preparatory move before the main one; in a still, a hero crouched low with a trailing spark, or a seam half-charged.
- **Asymmetry as personality.** A bent tip, one missing corner, one dimmer face, an off-centre glow. Perfect symmetry reads as machine, asymmetry as life.
- **Damage as biography.** Scorch marks, cracked glow, chipped edges, dents. A burned veteran has a story; an unmarked antagonist suggests it has never been hurt, which sharpens the stakes.
- **Eye substitutes.** An emissive slit or point at the leading vertex works as a gaze, and which face leads shows attention.
- **Scale relationships.** Tiny courage against enormous indifference. The size difference is the story.
- **Light direction implies emotion.** Light from below or from inside seams is the classic menace light; light from above with rim light reads heroic; strong backlight turns anyone into a mysterious silhouette.
- **Anthropomorphic cues without faces.** Formation (a leader and followers), distance kept, huddling, one figure stepping forward, a small figure sheltered behind a larger one.

A pipeline that gates full detail behind a near level of detail can silently revert the whole personality system to bare outlines when the camera sits beyond the gate. Check this before concluding the system failed: the blender skill, diagnosis.md.

Crowds at night read as silhouettes against light, not as lit figures. OBSERVED(triangle-bashkit). Back spots placed low and behind the crowd cut dark figures out against wet paving, and crowd lamps stay low so people read against the stage. Each figure carries one prop that reads at the distance the crowd is seen from. Low poly stand-ins showed in close shots, so use real figures inside a set distance of any hero camera, found by checking the closest shots Keep robed figures out of close walking roles: long robes hide the legs and glide in motion, with no fix found yet.

## Crowd variance: a stated trade

Variance is characterisation: make the two sides differ in how much they differ (a project design idea, not tested against alternatives). One faction varies in proportion, lean, damage, accessories and how crooked its outline is drawn. The other is perfectly identical, and the only thing that changes is how broken a member is. The crowd then carries meaning before any individual is read: one side is people, the other is a machine. Accessories help too; a crest, a carried standard or a trailing ribbon punctuates a crowd and tells the eye where units divide.

CONTESTED. Against that, a shipped many-unit battle game deliberately held silhouettes constant across idle, attack and running poses because constancy mattered for reading big battles, and made faction colour the most saturated colour in the scene, placed at a different location on each unit type (ASSERTED, single devlog). Both can be true. Variance is a crowd-grain and characterisation tool, and an anti-pattern for faction identification. Decide per project which job the crowd is doing: telling the viewer who a unit is, or telling them what kind of army this is.

## Faction readability channels

Assign identity to separate channels (CORROBORATED, read through an index because the two primary PDFs would not parse). A shipped AAA readability system puts colour on team (friend or foe) and silhouette plus motion and stance on class. It carries silhouettes with rim highlights rather than dark outlines, and puts the highest value contrast where the weapon is held, with a gradient from dark feet to light chest. The goal is silhouettes identifiable even with no lighting cues. Consequence for abstract armies: put faction on one channel and identity on another; one channel carrying both cannot separate them.

Readability usually fails on the background, not the units (CORROBORATED). Two factions with clear silhouettes still become unreadable when their colours are close to each other or to the environment, and colourblindness is a named failure mode. Quieter, lower-contrast backgrounds, dropping small details at small sizes and shading large forms in solid colours all protect the shape. So enforce the loud budget on the environment specifically, to protect the armies.

A staged test (ASSERTED, weak source; the pixel numbers come from a non-authoritative listing): check the silhouette at a 32 px thumbnail, the colour blocking at 64 px with a squint, and add detail only after both pass. One devlog independently reports 16x16 px as its workable floor for unit visibility without overlap.

## Formations are silhouettes

At four pixels an individual is nothing but a formation is still readable. Give each faction a formation language and the far field stays legible: ordered ranks and blocks against loose arcs and wedges. A wedge-shaped bite taken out of a rectangular block tells the whole story at any distance.

**Build the bite subtractively.** Overlapping a wedge of units onto an intact block reads as two formations stacked on each other, not as a notch: at a few tens of pixels per figure the eye gets outline only, and both outlines are still complete Delete the block's units that fall inside the wedge's hull and what is left is a rectangle with a triangular notch cut out of it, which is the one shape that survives being small. OBSERVED(triangle-battle). The general form: a silhouette-level read needs a silhouette-level edit, and anything that depends on overlap or occlusion to be understood will not survive the distance the brief is judged at.

Useful placement helpers are a ranked-block placer with a jitter parameter (near zero for a disciplined faction), an arc scatter for a loose line, and a clump with a falloff exponent for melee pockets. Placement geometry in general is in composition.md, section 7.

Read formations as islands and moats (OBSERVED(triangle-battle)). Uniform coverage reads as wallpaper or confetti, not as a battle; busy-ness should come from separated bright islands with dark gaps between them, chained into an eye path.
- **Two different gaps.** The halo is the local dark rim around one incident, a small fraction of its width. The moat is the clear dark gap between separate islands, much wider, on the order of an island (HEURISTIC, from one scene).
- **Measure the moat in screen space.** Two islands separated by open ground in the plan can still overlap on screen once the camera is raised or tilted, and then the gap is gone.
- **One colour per cluster, chosen once.** Giving every unit an individually random accent colour destroys all formation reading, because nothing groups. Pick the accent for the cluster and keep it for every member; variety belongs between clusters and not inside them.

## Storytelling in a single frame

A pretty frame is wallpaper; a frame with a clear before and after is an image people read.

- **The decisive moment.** Pick the instant of maximum tension, one beat before impact: the giant's seam is charging, a hero is mid-leap, the formation has just broken forward. The instant that makes peak action inevitable is more interesting than the peak itself.
- **What just happened.** Evidence in the frame: shattered minions smoking up front, craters, scorched ground, a toppled hero with a dimming glow. This is aftermath, and it gives the stakes weight.
- **What is about to happen.** Foreshadowing: a beam building at the giant's face, a crack already spreading where a hero struck, the sky changing colour behind it. Charged glow gradients imply timing.
- **Asymmetric stakes.** Tiny against enormous. The audience instinctively roots for the small side, so make the asymmetry plain and give the small side one thing the giant lacks: motion, unity, individuality, warm light.
- **The detail that rewards a second look.** One hero planting a small beacon, one fallen figure with a still-glowing core, a hairline crack shaped like a strike. Keep it in the lower third or at an edge so the focal point stays clean.
- **One clear read.** Caption the frame in one sentence ("the last triangles hold the line before the giant fires"). Every element should serve that sentence; cut anything that does not.
- **Colour follows emotion, even in dark work.** Eggleston's Toy Story color script stays soft and bright until something sinister happens, then goes bleak and muddy ([Hyperallergic](https://hyperallergic.com/610771/the-art-of-pixar-chronicle-books/)). Put the hope in the heroes' glow and let the giant own the oppression.

## When a viewer misreads the event, suspect geometry

A brace reads as holding only when it leans against the load. OBSERVED(triangle-battle); it cost a rebuild and it generalises. A support leaning in the same direction as the thing it supports reads as pushing it over, not holding it up.
- Put the support under the overhang, not beside it, and check this with real coordinates: compare the leaning mass's position at its crease with the support's position; if nothing is above the support, no lighting trick will fix the read (OBSERVED(triangle-battle)).
- Lean the support about the axis that produces an opposing diagonal in frame. Rotating about the wrong axis tips the object toward the camera, which just reads as foreshortening. Work out which world axis maps to "sideways in frame" before choosing the rotation axis.

When a viewer misreads what is happening in a frame, suspect the geometry of the relationship before reaching for lighting or effects.

**Run an unintended read pass on every sheet, with a second reviewer.** OBSERVED(triangle-bashkit), over a dozen cases on one project. The question: what else does this shape look like, and could that embarrass the client? The classes that came up: hate-group and religious symbols, faces from groups of round openings, stars and other loaded figures formed by crossed or paired shapes, famous landmarks and film props, everyday objects, and, for words and marks, famous logos and signs. A second reviewer working from sheets caught several that the builders had missed.

## Grey massing: what a blockout reveals

OBSERVED(triangle-battle). The practice is in SKILL.md, Review practices: the whole composition in neutral grey, flat light, final camera, judged at thumbnail with the squint test. What the grey pass shows that a plan does not:
- Masses merging into one.
- A key object reading as wallpaper.
- Terrain not reading.
- Islands that are separate in world space but overlap in screen space. Plans are drawn in world space, so this is the one they miss. Pair the pass with the projection table (composition.md, Composing in screen space and placing in 3D).

The pass costs seconds at 480x270, so there is no reason to skip it.

**A footprint rule is a read from the camera, not a plan property.** OBSERVED(triangle-bashkit). A kit rule against boxy footprints (a house convention there) was treated as a corner problem, but rounding a box leaves a box. An audit from the main view flagged many times more pieces than the plan audit did: near vertical walls seen flat on, and truncated triangles with near equal faces, read as boxes whatever the plan said A plan audit alone would have passed the kit, so audit from the main view.

- What worked: turn each tier half a corner step (60 degrees on a triangle, 36 on a pentagon, 30 on a hexagon) so staggered corners show the polygon; truncated triangles need clearly unequal faces; lean walls; give prow corners; pose a pier nearly square to the feature wall so both flanking faces show, since at a moderate yaw a pentagon shows only two faces and reads as a box.
- Limits: a slim tower with too much batter reads as a cone, and on a slim triangle it takes only a few degrees; a turned triangle tier needs to fit the inscribed circle of the tier below or it reads as a sliding slab, and long street walls read as slabs on polygon plans, so a long side needs setbacks too (OBSERVED(triangle-bashkit)).

## Explorable space

Designing for a viewer in motion changes the composition unit, and most of the findings below come from level-design practice (a research pass over about 34 sources, 9 fetched directly; confidence tagged per item). Neither side of the contested item has published playtest data.

- **The composition unit is mass and silhouette, because the viewpoint is unknown.** It is hard to use small composition elements when you do not know where the viewer will come from, and checking every angle is laborious. A viewer in motion picks up dominant colour, silhouette and motion before individual objects (F4, CORROBORATED, three sources of mixed quality).
- **Eye paths are CONTESTED in player-controlled space**. One sourced position, a level-design reference book, holds that leading lines and eye paths "aren't actually effective" there: the convergence artists read as leading lines is an artifact of linear perspective, hallways converge in any screenshot, and the book reports them failing in playtesting ("The player never plays your screenshot"). The named opposition teaches them: Miriam Bellard (GDC 2019) on rule-of-thirds walkthroughs and leading lines, Jim Brown (GDC 2014) on negative space, and mainstream level-design guides still teach leading lines through pipes, wires and floor patterns. The same source concedes that sightlines, approaches, lighting, colour and perspective "can matter, sometimes". Operational split, neither side proven: eye paths for designed cameras (composition.md, section 13); sightline, vista and landmark reasoning for free movement. Confidence high that the disagreement is real, medium on who is right.
- **Sightlines reveal; they cannot compel.** A sightline is a trajectory of empty space offering a view into another space, and it cannot guarantee behaviour; viewers use sightlines only when they seem relevant. Sequence approach, then vista, then the complicated space, and introduce a vista before a complicated arena (VERIFIED-PRIMARY).
- **A landmark counts only if it is navigationally useful.** Size and decorative distinctiveness do not qualify an object as a landmark (F9, CORROBORATED).
- **Operational Lynch for game worlds** (F6, VERIFIED-PRIMARY, qualitative, no numbers): most paths begin or end at a node, with few dead ends, and zig-zag is fine; edges are terrain features separating districts; a district needs exactly one shared characteristic, of any kind; landmarks sit adjacent to nodes, because landmarks lend importance to nodes and nodes give meaning to landmarks.
- **Empirical caution on Lynch.** In one small test (n=3) only landmarks and edges recurred in participants' route descriptions, with paths weak because game worlds have no street names (F5, ASSERTED, weak: PDF not read; do not upgrade). Read it as a reason to over-invest in landmarks and edges, not to drop the rest.
- **Spatial hierarchy is purely relative.** It comes from contrast in height, density, orientation or shape: a tall element stands out only among short ones, and a focal point creates a new centre. A colossus reads as dominant only against what surrounds it, which is the scale chain (scale.md) restated as a local property (F8, VERIFIED-PRIMARY).
- **Legibility and believability trade at vantage points.** Showing several sharply distinct districts from one overlook is what makes a world readable and what makes it read as artificial. An abstract geometric style buys room to sit toward legibility (F7, VERIFIED-PRIMARY for the trade; the style inference is ASSERTED).
- **Multi-camera coherence.** Dress each view to contain a landmark another view owns: world coherence across separately composed spaces was achieved on a shipped title by dressing each level's vista to contain the other level (VERIFIED-PRIMARY). The cheap test: every designed camera sees at least one landmark another camera owns. Shot dressing may cheat, layout owns continuity: "cheating is encouraged in previs", and layout avoids physically impossible camera moves (CORROBORATED, one studio-authored source). Consecutive-shot conventions are about a 20% size change and about 30 degrees between cuts (ASSERTED numbers, long-standing film convention).

## Pre-flight

Characters and readability
- [ ] Does each unit pass the black-silhouette test before any detail is added?
- [ ] Does it carry something a viewer can point at (limbs, an aperture, a gesture), not only proportion and lean differences?
- [ ] If the shape-language prior is subverted, do the other channels carry the difference on purpose (behaviour, colour and light, order versus individuality, orientation, repetition)?
- [ ] Is faction on one channel and class or identity on another?
- [ ] Do the factions stay readable against the background, not only against each other?
- [ ] Is the crowd-variance trade decided for this project (characterisation or faction identification)?
- [ ] Do formations read when units are a few pixels, with islands and moats measured in screen space and one accent colour per cluster?
- [ ] Is the nearest unit inside the full-detail band, so the personality system actually renders?

Story
- [ ] Can the frame be captioned in one sentence, and does every element serve it?
- [ ] Is it the beat before impact, with evidence of what just happened and what is about to?
- [ ] Does every support lean against its load, checked with real coordinates?

Explorable space
- [ ] Is the composition unit mass and silhouette, with approach, then vista, then the complicated space?
- [ ] Is every landmark navigationally useful, and does every designed camera see a landmark another camera owns?
- [ ] Was the grey massing pass done, with island overlap checked in screen space? (Scope: SKILL.md, review gate 1, which excludes emissive work on black.)
