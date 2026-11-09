# Composition: organising crowded and complex frames

Index: 0. Organising a crowded frame: the checklist | 1. Why busy images fail, and the named fixes | 2. The perceptual basis in four facts | 3. Value massing and notan | 4. Depth banding: value banding by distance | 5. Gestalt grouping: how a viewer parses a crowd | 6. Dominance, hierarchy and the loud budget | 7. Rhythm, interval and spacing | 8. Frame structure: armature, thirds, rabatment and the golden ratio | 9. Balance and visual weight | 10. Depth structure: overlap, framing masses and viewpoint | 11. Edges, detail frequency and variable busyness | 12. Rest areas and colour organisation | 13. Eye-path design | 14. Composing in screen space and placing in 3D | 15. Testing a composition | 16. Precedents: what the old solutions did and what transfers | 17. Where sources disagree, and where the theory does not transfer | 18. Pre-flight composition checklist

How shapes, values, colours and attention are arranged across the picture plane so a dense image reads as one picture. Scale, camera height and lens live in scale.md; lighting and palette craft in light-and-color.md; character and story in staging.md. Renderer-agnostic; Blender implementations live in the blender skill.

Provenance tags are defined once, in the `maintaining-skills` skill (Provenance tags). Conventions local to this file: a URL in parentheses means the claim was checked against that page; where a table below carries HEURISTIC numbers, they are predictions from arithmetic, not measurements of a finished image; OBSERVED(triangle-battle) here means scene 02, through two rejected reviews and a rethink.

The scale chain governs any frame with a big thing in it: scale.md.

## 0. Organising a crowded frame: the checklist

One working order, from a dense two-sided battle frame (OBSERVED(triangle-battle)); each step feeds the next. Placing figures (step 7) before steps 1 to 6 is how that crowd turned to noise. A frame with no crowd skips the crowd steps.

1. **Write the one-sentence read and rank the cast.** One sentence, for example "a small wedge of triangles holds a breach while the giant square looms over the field." Name a dominant element (what owns the frame, here the colossal square), a subdominant (the hero cluster, where the eye should land) and subordinates (everything else). Dominance and subordination exist to control the order in which the viewer meets things ([BYU Art 110](https://courses.byui.edu/art110_new/art110/week09/dominate-subordinate.html)).
2. **Fix the camera, camera height, lens and aspect ratio first.** Every principle below concerns the 2D image. If the camera moves afterwards, the composition is invalidated. Camera height sets how much content a frame can hold (scale.md), so settle it before adding objects. Compose in screen space and verify with an anchor table (section 14), and let the 3D scene follow.
3. **Block in three or four value masses before any figure exists.** Use flat, big shapes: ground plane, smoke banks, the dominant mass, light shafts, far ridgelines. Decide which one value covers more than half the frame (section 3). Link the darks into one connected shape. Do it first as a neutral grey blockout and review it before any look-dev (grey massing: SKILL.md, Review practices).
4. **Divide depth into 4 or 5 bands, and write the scale chain.** Give each band a value window, a haze level and a colour temperature. Enforce them with fog density and albedo caps, not hope (section 4). Write the scale chain, with distance and frame coverage for each rung, as scale.md describes, and keep the largest object a modest fraction of the frame.
5. **Draw the fronts.** A front is a line where the two sides meet. Draw two or three as S-curves or diagonals in screen space, with one side's territory on each side. Fights happen along fronts. They are the skeleton of the image.
6. **Set a density map and a loudness map.** Density is figures per screen area. Loudness is contrast, saturation and edge sharpness. They are different maps, and a dense area can be quiet. Budget one primary loud incident, a handful of secondary ones and a quiet majority (section 6).
7. **Place figures by clustered sampling in screen space, then lift to 3D.** Clusters of uneven size, gaps between clusters at least about twice the spacing inside them, orientation following a flow field (sections 5 and 7). A uniform grid reads as wallpaper and pure random scatter as confetti (section 1).
8. **Spend the loud budget on purpose.** Put the primary incident near a structural point and give it the frame's highest local contrast, its crispest edges and the only use of its accent hue. Dim, soften or desaturate anything that competes.
9. **Let edges be lost and found.** Merge same-side figures into masses (lost edges). Keep crisp edges where the two sides touch and at the focal point (section 11).
10. **Check overlap.** Each fight should be partly occluded by something nearer. Overlap is the main depth cue in a crowd (section 10). Break accidental tangents between silhouettes and with the frame edge.
11. **Build the eye path.** A hub at the hero, four to six stops, a loop back, and no exit through the frame edge (section 13). Designed cameras only; see section 13 for player-controlled space.
12. **Run the tests on a proof render** (section 15): greyscale, squint, thumbnail, flip, black-shape silhouette, busyness map and crop test. Fix, re-proof, repeat before spending an 8K render.

## 1. Why busy images fail, and the named fixes

| Failure | What the viewer sees | Cause | Fix |
|-|-|-|-|
| Confetti | Thousands of equal small bits, no mass | Every element has the same size, value and contrast, so nothing groups | Group into value masses (section 3). Add a size hierarchy. Lower the contrast of most elements so a few can carry weight |
| Wallpaper | A regular texture; the eye slides off | Uniform spacing, size, orientation and contrast. Evenly spaced elements give no rhythm to follow | Variable density, uneven cluster sizes, jittered orientation and scale, real gaps (section 7) |
| Mush | Everything merges into mid-grey brown | Compressed value range, many similar mid-values, hues blended | Restore true darks and a few lights, separate depth bands by value, keep side boundaries crisp, keep each side's hue distinct |
| Noise | Active everywhere, nothing important | No hierarchy; many equal "loud" incidents compete | One primary incident, a few secondary, a quiet majority (section 6) |
| Hot spots | Several equally bright areas pull the eye apart | The saliency budget was spent many times | Dim all but one. Rank by area and contrast |
| Flat stage | All fights seem to sit on one plane | No overlap between planes, no value drop with distance | Bands, occluders, haze (sections 4 and 10) |
| Tangents | Silhouettes kiss each other or the frame edge | Edges touch without overlapping, which reads as an accident | Overlap by a clear margin or separate by a clear gap |
| Bullseye | Everything radiates from dead centre | Symmetry with the focal point in the middle | Offset the focal point, tilt the axis, use asymmetric balance (section 9) |
| Leakage | The eye exits the frame | Lines, gazes or bright accents point out of frame | Turn flow back inward; put quiet or dark masses at the edges |
| Uniform busyness | Constant detail density, no rest | Detail frequency is the same everywhere | Map busyness and vary it deliberately (sections 11 and 12) |
| Colour riot | Too many hues of equal strength | No colour hierarchy | One hue family per side, one reserved accent (section 12) |

Bruegel's crowd scenes survive crowding because each small action sits inside one perspective structure and a muted triadic palette keeps colour from fighting ([Edwards on Census at Bethlehem](https://elizabethedwards.substack.com/p/art-analysis-the-census-at-bethlehem), a blog). The "Where's Waldo" effect that comes with it suits a painting studied at length and is a liability in a single hero shot.

## 2. The perceptual basis in four facts

The operative consequences, one citation each.

1. **Attention is pulled by local feature contrast.** Saliency models build maps for colour, intensity and orientation at several scales and pick a winner, so the eye goes to contrast before it goes to position ([Itti, Koch and Niebur, lecture summary](https://www.inf.ed.ac.uk/teaching/courses/ccs/lectures/ccs_l15_saliency.pdf); primary paper not read).
2. **Pop-out needs a difference in a single feature, and it needs rarity.** A target differing from distractors in one feature is found regardless of how many distractors there are ([Treisman, summary slides](https://web.cs.hacettepe.edu.tr/~erkut/cmp717.f20/materials/w12-visual-saliency.pdf)). If every fighter glows, glow is the background feature and nothing stands out by glowing. The hero must differ in a channel the crowd does not use.
3. **Viewers start near the centre, regardless of content.** The first glance lands near the middle however the image is designed, so a dead middle wastes the first glance ([Hayes and Henderson](https://viscoglab.ucdavis.edu/sites/g/files/dgvnsk12381/files/inline-files/hayeshendersoncenterbias.pdf)).
4. **Clutter tracks local contrast variability and edge density, not figure count.** Edge Density is a cheap proof-render measure ([Rosenholtz et al.](https://dspace.mit.edu/handle/1721.1/37593)). Treat it as a proxy for clutter, not a full model of it. (A note on how far the model holds on real scenes stayed unconfirmed for two passes and was deleted 2026-11-08: no action depended on it.)

## 3. Value massing and notan

**Principle.** Before it is anything else, a picture is an arrangement of a few value shapes. Notan is the Japanese term for the dark and light arrangement under a painting. It is a design plan, not a copy of the scene's actual values ([Virtual Art Academy](https://www.virtualartacademy.com/notan/)).

**Why it works.** The first read of an image is low-frequency: large dark and light shapes. Detail is read later. If the large shapes are organised, small detail inherits that organisation. If they are not, good detail cannot rescue it. This is why the squint test works. Squinting lowers spatial resolution and leaves the masses.

**Numbers from the literature.**
- Plan with two, three or four values. Fewer values give a stronger structure ([Virtual Art Academy](https://www.virtualartacademy.com/notan/)).
- One value should cover more than half the picture, and the remaining values should not split the rest evenly (same source).
- Link the darks into one large connected shape, as in Whistler's Mother (same source).
- Small light accents can enliven an otherwise dull pattern (same source).

**How to apply when placing objects by coordinate.**
- Build the masses from large geometry first: ground plane, the dominant mass, smoke and haze banks, far ridge silhouettes, shafts of light. They carry most of the area. Figures live inside the masses.
- Give every object a value class (dark, mid, light, accent) and an area budget. HEURISTIC starting point for a dark battle: dominant dark about 55 to 65 percent of frame area, mid about 25 to 35 percent, light about 8 to 12 percent, accent a small fraction of the light. Tune by eye, but keep one value above 50 percent.
- Make most figures take the value of the mass they belong to. A crowd that reads as one dark wedge with a few lit incidents is organised. A crowd where every figure is a distinct mid-value is confetti.
- Link the darks. Arrange shadow, smoke and silhouette so dark areas connect across the frame: a ground shadow that flows into the dominant mass's base and on into a far ridge. One connected dark shape reads as structure. Scattered dark islands read as holes.
- Keep an area of near-black with no internal detail. It anchors the masses and gives the lights something to be bright against.

## 4. Depth banding: value banding by distance

**Principle.** Distant planes lose contrast, shift cooler and lose detail. A painting guide gives a step count: near foreground 4 to 5 value steps between lightest and darkest, next layer 3, middle ground 2, far background 1 to 1.5, with far hills often merging into one value ([Will Kemp Art School](https://willkempartschool.com/how-to-create-depth-in-landscape-painting-understanding-value-compression/)). The page does not state the length of its value scale, so read the counts as relative: the far band holds roughly a quarter of the near band's range (HEURISTIC reading, re-dated 2026-11-08 from an unverified scale-length guess, which was dropped). Value order is preserved. The range compresses and the ranking does not flip (same source).

**Why it matters in a crowd.** Banding separates the fights from each other. If a far fight has the same contrast as a near one, they compete and the picture flattens. Each band gets a smaller value range than the one in front, so the eye ranks fights by nearness without effort. It also lowers measured clutter, since clutter tracks local contrast variability (section 2, fact 4). The haze itself, as lighting, is covered in light-and-color.md (Atmosphere and depth).

**Dark-scene correction.** In a dark battle the depth cue is mostly the lifting of blacks toward the haze value and the dimming of lights toward it. Far darks get lighter and far lights get dimmer. The nearest band keeps the true darks.

### The never-paler-than-the-sky check

**Scope: this holds for objects darker than the airlight**, the haze or sky colour along their sightline. By the Beer-Lambert formula below, apparent value minus haze value equals transmittance times (true value minus haze value), so the sign of the difference follows the object, not the distance. A dark object is lifted toward the haze but never past it. An emissive or sunlit distant surface brighter than the haze stays brighter than it, dimmed toward it, and can read paler than the sky behind it; the rule does not cover those, which is also why far lights can punch through haze (see the apply notes below) and why the upper windows in the band table sit above h.

Within its scope the line of sight past an object always crosses more air than the line of sight to it, so a dark distant object paler than the sky immediately behind it never occurs. Check any render of a dark distant silhouette by sampling the object and the sky directly behind it: the object must be darker. Provenance: a geometric argument within that scope, high confidence, and checkable against any photograph. The source is a single field observer in Japan, who ruled out tone mapping as the cause and conceded the effect may sit too far out to matter in many scenes.

CONTESTED, single-observer: the full tint-curve claim, that tint runs deep blue in the mid-distance and then becomes paler and less saturated again at extreme distance. It is one observer with no measurements and no distances or exponents, so do not rely on the curve; use only the constraint. Atmospheric perspective as plain monotonic loss of contrast and saturation with distance is the older, taught view, and the curve claim is the correction to it. Both are recorded here.

Corollary (F3, ASSERTED): one fixed fog colour cannot serve a sky that runs from blue zenith to pale horizon. Fog near the zenith blue makes distant mountains wrong against a pale horizon, and fog matching the horizon pushes dark peaks paler than the sky, which cannot occur. The stated fixes are a compromise fog colour, per-channel fog falloff to shift tint from blue toward white with distance, or a sky model.

**The math (Beer-Lambert, standard physics).** A surface seen through a uniform scattering medium has apparent value v = h + T * (v_true - h), where h is the haze value, T = exp(-sigma * d) is transmittance, sigma is extinction density and d is distance. Retained contrast equals T. Pick sigma so the farthest band retains 10 to 15 percent: sigma = -ln(0.12) / d_far, about 2.1 / d_far.

HEURISTIC starting table, display-referred values on a 0 to 1 scale, haze value h = 0.15, true values 0.01 to 1.0, derived from the formula above. These are predictions from arithmetic, not measurements of a rendered image:

| Band | Distance as fraction of d_far | Retained contrast T | Value window | Colour temperature |
|-|-|-|-|-|
| 1 near | 0.1 | 0.81 | 0.04 to 0.84 | Warmest, highest saturation |
| 2 near-mid | 0.25 | 0.59 | 0.07 to 0.65 | Warm to neutral |
| 3 mid | 0.5 | 0.35 | 0.10 to 0.45 | Neutral to cool |
| 4 far | 0.75 | 0.20 | 0.12 to 0.32 | Cool |
| 5 extreme far | 1.0 | 0.12 | 0.13 to 0.25 | Coolest, nearly one value |

Read the window against h. Values below h belong to objects darker than the haze, where the never-paler rule applies. Values above h are bright true values (lights, sunlit surfaces) dimmed toward h, which the rule does not cover.

**How to apply by coordinate.**
- Decide d_far from the scene (distance to the farthest fights), set sigma from it, and set the haze density to match. Use height falloff so low ground carries more haze than structure tops.
- Cap albedo and emission per band at the window's upper value and give far materials a floor near the haze value. Do not trust fog alone, because emissive figures can punch through haze and break the band (they are outside the never-paler rule, which is scoped to objects darker than the haze).
- Reserve full saturation for band 1 and the focal incident. Far bands trend toward the haze hue.
- Verify on a proof render (section 15): measure the 2nd and 98th percentile luminance of each band's figures and compare with the table.

## 5. Gestalt grouping: how a viewer parses a crowd

The classical grouping laws (proximity, similarity, continuity, closure, common fate, figure-ground, Prägnanz) are standard ([Wikipedia, Gestalt psychology](https://en.wikipedia.org/wiki/Gestalt_psychology)); a crowd is parsed in groups, not figure by figure, so your job is to hand the viewer the groups you want.

| Law | In a crowd | How to apply in 3D placement |
|-|-|-|
| Proximity | Close figures read as one unit | Tight inside, separated outside. HEURISTIC: gap between clusters at least 2x the median nearest-neighbour distance inside them, or groups blur together |
| Similarity | Same shape, colour, size or value groups together | Code each side in two channels at once, shape and hue, and keep the code consistent. Kurosawa colour-coded the armies in Ran, yellow, red and blue by side, so loyalty reads instantly, and the colours bleed into a muddy violet-brown where armies clash ([Color Culture](https://colorculture.org/ran-cinematography-analysis/), a blog analysis). Borrow the blend: let hues mix only at the contact line |
| Continuity | Elements on a smooth path read as one stream | Arrange figures along arcs and S-curves. Abrupt direction changes make grouping less likely |
| Closure | Gaps are filled in | Partly occlude figures. The brain completes them, so the frame feels like thousands without each one being fully legible |
| Common fate | Things moving the same way group | A still can imply motion. Orient figures by a flow field (lean, apex direction, glow trails) so a group shares a direction. Where two flows collide you get the front |
| Common region | Things inside one boundary group | Enclose a fight in a light pool, crater, shockwave ring, smoke bank or rubble ring. The enclosure makes a dozen figures one unit |
| Connectedness | Joined things group | Link figures with beams, tethers or shared shadow. Use sparingly |
| Figure-ground | Compact, enclosed, symmetric regions read as figure | Keep figure shapes compact against a calmer ground. Use counterchange: light figures on dark ground in one area, dark figures on light ground in another (dark silhouettes against a glowing breach) |
| Prägnanz | The simplest interpretation wins | Aim for a few large simple compound shapes (a wedge, an arc, a ring) built from many small ones. A viewer who sees a wedge has parsed the crowd |

Flow field recipe (HEURISTIC). Define a vector field as the sum of two or three attractors, each side's advance toward the front, plus low-amplitude curl noise. Orient each figure along the local vector, then add random jitter of plus or minus 15 to 25 degrees so groups read as streams without becoming a combed pattern. A triangle has an apex, which makes it a built-in arrow. Aim apexes along the flow and the field becomes visible.

## 6. Dominance, hierarchy and the loud budget

**Principle.** Make one thing dominant in each channel, a few things subdominant and everything else subordinate. A design-course page says dominance controls the sequence and attention each element gets, usually through size and colour, and that the dominant element often works better slightly off centre ([BYU Art 110](https://courses.byui.edu/art110_new/art110/week09/dominate-subordinate.html)). Value works the same way: one value range leads and the others support (same source).

**Why it works.** Given section 2, facts 1 and 2, attention is a competition decided by local contrast and rarity. If ten things share the top contrast, the competition is a tie and the eye wanders. A hierarchy decides the winner in advance.

**Apply by channel.** One way to set the hierarchy: in each channel, one thing takes first rank.
- Value contrast: the highest local contrast belongs to the hero incident.
- Saturation: the most saturated hue in the frame is the hero accent, used nowhere else at that strength.
- Edge sharpness: crispest edges and best focus at the hero incident.
- Scale within its depth band: the hero is the largest figure in its band or has a distinct silhouette.
- Rarity of feature: one channel the crowd does not use (section 2, fact 2). If the crowd glows, give the hero a dark core with a bright rim, or the one unique hue.

**The loud budget (HEURISTIC).** Call a cluster "loud" when it has high contrast, saturation and edge sharpness at once. Budget one primary, three to five secondary, and the rest quiet. Loud clusters together cover roughly 10 to 20 percent of the frame. If a saliency or edge-density map shows more than about six separate hot blobs, the frame is noise.

**Brightness stops ranking near the clip.** Under AgX, flat emitters stop separating by brightness well before they reach one white. Measured on flat EEVEE quads with no compositor, one crimson RGB (0.9, 0.02, 0.05), TESTED 2026-11-04 on 5.2.0: with look None, white reaches 255 by strength 16 and crimson is 255/220/219 at 22, 255/249/248 at 100; with AgX - Punchy, white reaches 255 at 24 and crimson is 255/205/204 at 22, 255/242/241 at 100. So above about 16-24, size is the dominance channel left: a hero's own echoes and accents, clipped to the same white, beat it unless the hero is visibly larger. OBSERVED(cylinder-mirror), rounds in which heroes lost to equally bright echoes under AgX, fixed by size, not brightness; scope is a clipping view transform (AgX here). Starting value: at least 1.5x in stroke width and figure size (HEURISTIC).

Link the ranks. The eye path (section 13) runs between the subdominant and the dominant, because a dominant mass the eye cannot connect to the story competes with it.

## 7. Rhythm, interval and spacing

**Principle.** Evenly spaced, evenly sized elements become wallpaper: the eye finds no beat to follow, so it slides over the surface. Uneven spacing with an underlying order stays alive. This is CONVENTION in painting teaching with no single checkable source, so the numbers here are HEURISTIC.

**A two-scale placement scheme.**
- Poisson-disk sampling gives points no closer than a minimum distance r and looks natural, and Bridson's algorithm generates it in O(N) time in any dimension ([Bridson, SIGGRAPH 2007](https://www.cs.ubc.ca/~rbridson/docs/bridson-siggraph07-poissondisk.pdf)). Use it at the micro scale to stop figures interpenetrating while still looking organic. Used with one global r across the whole frame, it makes a regular macro texture, which is wallpaper again. The macro scale needs structure from you.
- Macro: put cluster centres along the fronts and in territory behind them. Draw cluster sizes from a heavy-tailed spread (a few large clusters, many small ones, for example a log-normal with sigma around 0.6). Make the sizes uneven, odd and not repeated in sequence.
- Micro: inside each cluster, use Poisson-disk with r set to about 0.6 to 0.9 of figure width where you want contact and overlap, and larger where you want air. Jitter scale by about plus or minus 15 percent (log-normal, sigma 0.15 to 0.25) and orientation as in section 5.
- Gaps: between clusters at least twice the inner spacing. Successive gaps along a line of clusters should differ, with ratios of roughly 1.3 to 2.
- Rhythm along the eye path: alternate dense and sparse, loud and quiet, so the path has a beat. Dense, sparse, dense with a different count each time.

**Sampling in screen space.** Because figures stand on a ground plane, screen y maps to depth, and the depth band of a figure follows from where it sits on screen. Sampling in world space piles distant figures into a thin dense strip near the horizon. Sampling in screen space with your target density and casting each sample to the ground (section 14) gives you the picture you designed.

## 8. Frame structure: armature, thirds, rabatment and the golden ratio

Definitions, one line each:
- Thirds: lines at 1/3 and 2/3 of each axis. In 1845 George Field called the rule "neither accurate nor universal" ([Wikipedia](https://en.wikipedia.org/wiki/Rule_of_thirds)).
- Golden section: 0.618 and 0.382. Replications of the preference studies conflict, and claims of deliberate use by Renaissance painters are frequently overstated (ASSERTED from secondary sources only; the conflict is not resolved here).
- Rabatment: the squares implied by rotating a rectangle's short side onto its long side; in a 3:2 frame the rabatment lines coincide with the thirds lines, and on wide frames they sit close to the middle, so they say "keep the main mass off the exact centre line" and not much more ([Wikipedia](https://en.wikipedia.org/wiki/Rabatment_of_the_rectangle)).

**Honest verdict.** The evidence that these grids cause preference is weak. They are useful as cheap checks: is the focal point on dead centre, does the horizon split the frame in half, are the masses distributed or crowded into one corner. They do not tell you what makes a frame work. Contrast and mass structure do (sections 3 and 6). Place the primary incident near a thirds intersection or rabatment line and give it the frame's highest local contrast. The grid supplies a rough location and the contrast does the work, since the eye goes to contrast before it goes to position.

**For a crowded frame, use the armature for masses and directions, not points.**
- Run the main front along a frame diagonal or a line parallel to it. Diagonals read as dynamic ([CG Wire](https://blog.cg-wire.com/character-shape-language/)).
- Build the macro shape as a large triangle: base along the lower frame, apex at or near the hero cluster. A stable pyramid is a standard Renaissance and Baroque device (CONVENTION, source not located).
- Put the threat's mass on one side of the diagonal and the hero cluster on the other (section 9).

## 9. Balance and visual weight

**Principle.** Visual weight is how hard a region pulls the eye. CONVENTION from Arnheim's work (not read), which treats the picture as a field of forces. Factors that add weight: larger area, higher local contrast, higher saturation, warmth, isolation, sharper edges, complexity and distance from the frame centre (a lever effect: the same weight counts more far from the middle).

**Why it matters.** A crowd of thousands has enormous total area, but weight comes from contrast, so a small hot cluster can balance a huge quiet mass. Asymmetric balance is the working solution: the colossal threat, large and low contrast and cold, balances against the hero cluster, small and high contrast and warm or saturated, placed further from centre. This also avoids the bullseye failure.

**Apply.**
- Estimate weight per region as area x local contrast x distance factor. Place the heavy quiet mass near the centre line and the small intense cluster farther out on the opposite side.
- Check with the proof-render centroid in section 15. HEURISTIC: a weighted centroid within about 8 percent of the frame centre reads as stable. An offset of 10 to 20 percent reads as tension. Beyond that the frame feels like it is sliding.
- Sizes of weight are relative to the frame, so re-check after any camera change.

## 10. Depth structure: overlap, framing masses and viewpoint

**Overlap.** Occlusion is a monocular depth cue (textbook-level). Cutting and Vishton (1995) are widely cited as ranking it the most effective cue at every distance (ASSERTED: widely repeated, the primary was not re-read; nothing below depends on the ranking). The reasoning holds for crowds on its own: with thousands of similar objects, size and texture gradients are ambiguous and overlap is what tells the viewer which is in front. Apply:
- Every fight should be partly covered by something nearer: a foreground figure, a rubble pile, a smoke bank, a strut of the threat.
- Do not let two silhouettes just touch. Overlap by a clear margin (HEURISTIC: at least 15 to 25 percent of the smaller one's width) or leave a clear gap.
- Order the overlaps so near objects are darker or higher contrast than far objects (section 4), then the occlusion order matches the value order.

**Repoussoir and coulisse.** A repoussoir ("pushing back") is a figure or object in the right or left foreground that brackets the edge of the composition and adds depth. It is common in Mannerist, Baroque and Dutch work ([Wikipedia, Repoussoir](https://en.wikipedia.org/wiki/Repoussoir)). A coulisse is a dark wing of trees or architecture on one side that frames a luminous distance, associated with Claude Lorrain and Poussin ([Eclectic Light](https://eclecticlight.co/2015/04/05/making-space-2-size-distance-position/), a blog; one source treats it as a kind of repoussoir; ASSERTED, a single blog, weak). Apply: put large dark low-detail masses (a fallen block, a broken wall, a drifting plate) at one or both lower corners or side edges, soft from depth of field, leaning inward. HEURISTIC: 5 to 15 percent of frame area, with lower contrast and detail than the focal zone so they frame and do not compete.

**Orthogonals.** The National Gallery notes that the broken lances in Uccello's Battle of San Romano make a grid-like pattern across the foreground leading toward a vanishing point, and that the painting is hard to follow partly because it has darkened ([National Gallery entry](https://www.nationalgallery.org.uk/paintings/paolo-uccello-the-battle-of-san-romano)). Apply: yaw debris, fallen figures, spears and beams so they run along ground lines that converge on the vanishing point, and put that vanishing point near the focal cluster. A cheap rule: rotate each piece of debris to point toward the hero's ground position, with jitter of 10 to 20 degrees (HEURISTIC).

**Viewpoint.** Painters of crowded battles often raised the viewpoint. Altdorfer's Battle of Alexander at Issus starts feet from the fighting and rises to seas, continents and the curve of the earth; the sky takes more than a third of the panel ([Wikipedia](https://en.wikipedia.org/wiki/The_Battle_of_Alexander_at_Issus)). Bruegel's Census at Bethlehem looks down as from an upper window, with a view corridor from the foreground crowd to the ruins (Edwards, blog). Mughal and Persian battle pages stack figures in shallow tiers high on the picture plane (ASSERTED, weak sources). The mechanism is the same: a raised or tilted ground plane spreads fights into vertical bands so they overlap less and more of them are legible. Camera height is a content ceiling: scale.md.

**Open frameworks give every bay a stage.** OBSERVED(triangle-battle). A closed solid (a cube, a slab, a tower) presents one outer surface and no interior, so the only things it can contribute are silhouette and occupied area. An open framework gives much more: a building under construction, a lattice, an exposed structural frame. Every bay is a stage where fights and incidents can happen in and through the structure. You can see past it to the sky and to what lies behind, which also lets it sit inside the haze bands. It can be backlit, so it silhouettes with light coming through its structure. Countable bays also act as a scale ruler, which makes it a good rung in the scale chain. If a large object in a frame has "nothing happening on it", consider opening it up before decorating its surface.

Crowds become grain at aerial scale: scale.md.

**Lens.** Long lenses stack layers. Color Culture's Ran analysis says telephoto compression piles soldiers into a dense, seemingly endless mass ([Color Culture](https://colorculture.org/ran-cinematography-analysis/), blog). This agrees with the long-lens guidance in scale.md (Lens): more overlap per unit of screen area, which suits a packed frame.

## 11. Edges, detail frequency and variable busyness

**Edges.** Painters mix sharp and blurred edges to direct attention. Sharp edges tend to mark the focal point and blurred edges recede, and some blurs are chosen for attention and do not match any optical effect ([Eclectic Light, edge hierarchies](https://eclecticlight.co/2023/11/03/painting-on-the-edge-edge-hierarchies/)). The eye is drawn to hard edges and skips over soft or lost ones ([BYU Art 110](https://courses.byui.edu/art110_new/art110/week09/dominate-subordinate.html)). Edges are lost where neighbouring shapes are similar in value and hue, and found where value or colour changes (painting blogs, not individually verified). One warning: Renoir's uniformly sharp figures looked "cut out", which critics disliked (Eclectic Light).

**Why it matters in a crowd.** Edges are where the clutter is. Edge count, not figure count, makes an image busy (section 2, fact 4). Losing edges inside masses removes most of the clutter without removing any figures.

**Apply by coordinate.**
- Same-side neighbours in the middle and far bands: give them the same albedo and emission, and no rim light, so they merge into one mass. That is a lost edge produced by value similarity.
- The front, where the two sides touch: raise value difference and put a rim or backlight on the contact edge. Edges encode conflict. They are crisp where sides meet and soft where allies stand together.
- Focal incident: crispest edges and sharpest focus. Do not rely on depth of field alone, because an 8K image will be examined at 100 percent. Control edge clarity with lighting and value contrast too.
- Detail frequency budget: fine detail (small seams, glints, particles) only in band 1 and at the focal incident. Far bands carry silhouette only.
- Vary edge quality within one figure so the figures do not look cut out: a crisp lit side and a soft shadow side.
- Backlight helps readability in dark crowds. For the Helm's Deep night battle, cinematographer Andrew Lesnie used overexposed backlight motivated by moonlight, partly so the action stayed legible with hundreds of dark-clad extras ([American Cinematographer](https://theasc.com/magazine/dec02/two/page3.html)).

**Busyness map.** Use Edge Density (section 15) to see where detail is. Aim for a gradient: highest at the focal incident, falling away, with at least a few large smooth areas. If the map is flat, the frame has uniform busyness.

## 12. Rest areas and colour organisation

### 12.1 Rest in a frame with almost no empty canvas

Negative space is the usual advice for rest (scale.md, levers), and a dense frame cannot afford blank canvas. Altdorfer shows the way out: thousands of figures fill the lower part, while the sky takes more than a third of the panel and carries the sun and the crescent moon ([Wikipedia](https://en.wikipedia.org/wiki/The_Battle_of_Alexander_at_Issus)). Even the densest classic battle gives the eye somewhere to rest. For a dense frame, the rest areas are quiet masses and not blank canvas.

Quiet zone types, all filled:
- A dark mass with no internal contrast (a notan shape): a shadowed crowd wedge, the base of the threat, a far ridge.
- A smoke or haze bank: soft, low contrast, hides detail.
- A lull in the ground fight: sparse stragglers, debris, a few small embers.
- A large simple surface: the threat's flat face is itself a rest area.

HEURISTIC: quiet zones total about 30 to 40 percent of the frame area. Put at least one directly beside the hero cluster. Contrast is local, so a quiet moat around the hero raises its apparent contrast without raising its absolute values (section 2, fact 1).

Altdorfer also split light and dark between the armies: light falls on the west where Alexander's side prevails, and the Persians retreat under the crescent moon into darkness ([Wikipedia](https://en.wikipedia.org/wiki/The_Battle_of_Alexander_at_Issus)). In a two-sided scene, a lit side and a shadowed side is a strong value structure. Keep one side's territory in the dominant value and the other in the secondary value.

### 12.2 Colour as a grouping channel

Ways to pick a palette are in light-and-color.md (Color design). This section covers only the composition use of colour.
- One hue family per side. Hue is the cheapest grouping channel in a crowd (section 5, similarity). Kurosawa's coding is the precedent.
- Reserve the hero's accent hue, and use it nowhere else at that strength. A small echo of it at the other eye-path stops, at roughly 10 to 20 percent of the main strength (HEURISTIC), links the stops without pulling attention from the hero.
- Pick the hero's hue from what the field lacks. A cool accent in a warm field, or the reverse, pops because it is rare (section 2, fact 2).
- Separate planes by temperature: warmer near, cooler far. Field (1845) put the ratio of advancing to retiring colour at about 3:1 and Reynolds put warm to cold at 2:1, though Field also thought the natural balance closer to equal ([Wikipedia](https://en.wikipedia.org/wiki/Rule_of_thirds)). Treat these as rough weights for area, not rules.

## 13. Eye-path design

Scope: designed cameras, where the viewpoint is fixed. In player-controlled space this whole section is CONTESTED; see staging.md, Explorable space.

The brief for a dense frame is not a tidy left-to-right reading route. Saliency competition (section 2) means the first deliberate look goes to the highest-salience blob after the centre glance. So design a hub and a loop, not a single line.

**Steps.**
1. **Choose the destination, which is also the hub.** This is the hero incident. Place it near a thirds intersection or rabatment line (section 8) and give it first rank in every channel (section 6). The viewer's gaze will reach it first and return to it.
2. **Handle the centre glance.** Fixation begins near the centre (section 2, fact 3). Put a medium-loud stop, not a void, in the central region, and arrange a leading line from it to the hub.
3. **Choose four to six stops in total** (HEURISTIC). Wikipedia's account of Altdorfer describes about four routes: the Macedonian front pressing the fleeing Persians, the king's chariot pursued by Alexander, the slope of soldiers down to the camp and city and up the mountain, and then the sky ([Wikipedia](https://en.wikipedia.org/wiki/The_Battle_of_Alexander_at_Issus)). For a two-sided battle read: the hero cluster, the threat's base, a secondary fight on the main front, a deep-distance anchor such as a glowing far breach, and a return through a quiet area back to the hero.
4. **Chain the stops with several links at once.** Redundant links make a path robust.
   - Leading lines: the front, rubble lines, beams, debris pointed by section 10's orthogonals.
   - Orientation: triangle apexes aimed at the next stop.
   - Value steps: each stop slightly less loud than the one before it, apart from the hub.
   - Scale steps: size decreases along the path, which also reads as depth.
   - Edge quality: sharp to soft along the path.
   - Colour echo: the hero hue repeated in small amounts (section 12.2).
5. **Prefer S-curves.** A sinuous front moves the eye gradually and covers more of the frame than a straight diagonal (CONVENTION).
6. **Seal the exits.** Elements near the frame edge point inward. Keep bright accents away from the edge. Put dark or quiet masses at the edges and corners. A gentle vignette of roughly 5 to 15 percent falloff (HEURISTIC) helps, and it should be subtle.
7. **Verify** (section 15). Compute a saliency or local-contrast map from the proof render and check:
   - The strongest blob is the hero. HEURISTIC: at least 1.3x the next strongest.
   - The next blobs, in order, are the intended stops.
   - The hot blobs number no more than about six.
   - Convert the intended stops to screen coordinates from your spec and confirm the blobs are where you said.
   - Fresh-eyes test: look at a 256 px thumbnail, write down what you looked at first, second and third, and compare with the intended path.

## 14. Composing in screen space and placing in 3D

Work from the picture to the world. Write a composition spec as data, generate the scene from it, and check the render against it. The spec holds the frame size and horizon, the depth bands (each with a distance range and a value window), the front polylines, the hero position and radius, the eye-path stops and the quiet zones, all in normalised frame coordinates.

Anchor-table implementation: the blender skill, scripts/frame_check.py. It consumes only an anchor table, `{name: (world_pos, (nx, ny))}`; the spec above is yours to structure as data, and no script here defines it.

**Verify framing with projection maths, not by eye.** Write an anchor table of world points with their intended normalised frame coordinates, then print the actual projected coordinates at build time. OBSERVED(triangle-battle): this caught a whole-scene framing error in scene 02, and later confirmed a plan's geometry closely. Treat it as normal practice for any composed 3D frame, and run it on every build, since a changed camera height or lens silently moves every anchor.

Do this for the rungs of the scale chain too (their tops and bases), since a rung that lands off-frame or on top of the next rung is the quickest way to lose the chain. Print the table before rendering anything.

**What the anchor table does not prove.** Projection answers where a point lands in frame and nothing else. It does not know what is between the camera and the point, or what is around the camera, and both gaps have passed a full table at tolerance while the frame was wrong. OBSERVED(triangle-battle, scene 02).

- **In front of the anchor: base anchors are grazing by construction.** An object standing on a terrace has its feet at the terrace plane, and that same terrace's nearer lip projects to within a few thousandths of the same frame height. On one camera every anchor passed the stated gate while a separate occlusion sweep showed several bases hidden, each within a few thousandths of its nearer ground, an order of magnitude inside the tolerance, so no tightening of the tolerance separates them (OBSERVED(triangle-battle)). Either mark base anchors as reference points rather than visible ones, or run a visibility check beside the projection check. The sweep is cheap, a scan of nearer ground points along the anchor's bearing, and it also found a clearly occluded base against a camera note promising that it rises out of the haze. That is a composition decision, and it is far cheaper at the massing gate than after the giants are built.
- **At the camera: treat every designed camera as a keep-out volume.** A generated block landed on top of a designed camera whose position sat inside a building region. The frame rendered as the dark inside of a box, and all of that camera's anchors still passed, as did the occlusion sweep (OBSERVED(triangle-battle)), because the sweep walks the ground toward each anchor and this obstruction was behind it. Generated content has to avoid the cameras the way it already avoids the giants' footprints.

So anchor verification is necessary and is not sufficient. Exit code 0, a full table of passing anchors and a black frame are all compatible, and the only thing that catches that class is looking at the render.

**A camera plan written before the world exists is a wish list.** OBSERVED(triangle-bashkit). A shot plan was written against kit docs while the city was being built, with locations given as district plus piece numbers. When real coordinates arrived, most shots changed: landmarks stood far from where the plan assumed, the hero piece was out of frame on the shot meant to show it, some districts were never placed, and some plan numbers could not be met at all Camera first (section 0) was right and was not followed. If shots depend on sight lines, write them as inputs to the generator: a reserved site, two landmarks collinear with a camera point, a clear axis height. Run the anchor table when coordinates first exist, before any cost is spent on the shots.

**Cameras are a build product.** OBSERVED(triangle-bashkit). Any layout change re-invalidates them. Across three successive cities on one kit, most cameras needed re-aiming after a layout, a reused position was blocked by new towers and found only on the contact sheet because the log's check lines were printed and nobody read them, and proof frames that had passed several reviews turned out to show a dark wall or miss their subject What held up: a ray search for clear spots, then a cheap preview, then one render. Pick a camera by naming the hero it must show and testing that hero's visibility, since a clear view is not the same as the right view.

Pipeline:
1. Build the value masses (section 3) and set the haze from d_far (section 4).
2. For each front polyline, sample cluster centres in screen space with uneven spacing. For each cluster draw a size, then sample members by Poisson-disk in screen space around it (section 7).
3. Cast each sample to the ground. Add terrain or rubble height afterwards, since the height shifts the screen position. Resample or apply the inverse offset.
4. Compute depth from the hit, assign the band, and set value cap, emission cap and haze from the band table.
5. Orient from the flow field (section 5). Choose the side and hue from the front's side.
6. Place the hero cluster last. Then run a clearing pass: find any non-hero figure within the quiet moat whose loudness exceeds the hero's, and lower it.
7. Place foreground occluders (section 10) along the lower corners and edges.
8. Project the eye-path stops and verify the blobs (section 15).

## 15. Testing a composition

Run on a proof render, not the final. Render at 1280 or 1920 wide with low samples, view transform and look as the final will have, and save as an 8-bit PNG so the numbers are display-referred. A linear EXR measured raw will mislead you, because values after the view transform differ from scene-linear values.

| Test | What it checks | How to run | Pass |
|-|-|-|-|
| Greyscale | Value structure with hue removed | Convert to luminance (Pillow `convert("L")` uses ITU-R 601 weights, close enough for this) | Masses and the hero still separate. Colour is not carrying the whole hierarchy |
| Posterise (notan) | Value massing | Quantise to 3 or 4 levels and count area per level | One level above 50 percent. Darks form one connected shape. Hero is on a clear light-dark boundary |
| Squint | What survives low resolution | Gaussian blur, radius about 1.5 percent of image width on a 1280-wide copy (HEURISTIC) | You can still name the main masses, the front and the hero |
| Thumbnail | The poster read | Shrink to 64 to 128 px wide | 3 to 5 clear masses. The hero is the highest-contrast blob |
| Flip | Hidden imbalance, drift, tangents | Mirror horizontally and look again with fresh eyes | The frame still balances. Nothing slides or points out of frame. A flipped image removes your familiarity with the layout, which is the point. Claims about left-to-right reading bias are widely taught and mixed in the research (ASSERTED, one side recorded) |
| Black shape | Silhouette readability | Override all materials to black on a white background, no fog, standard view transform | Sides separate by silhouette alone. Shapes are distinguishable. Clusters form recognisable shapes. Overlaps read |
| Busyness map | Detail frequency | Edge Density (`scripts/composition_sheet.py`; its `edge_busy_fraction` is edge density alone, so it is an upper bound on the loud share of section 6, not the loud share) | Gradient from loud to quiet. A few large smooth zones. No flat map |
| Crop test | Nested composition at 100 percent | Cut the 8K final into 1920 x 1080 crops (a 4 by 4 grid at 7680 x 4320) and view four to six | Each crop has its own local focus and does not dissolve into noise |
| Saliency or fresh-eyes | Intended eye path | Spectral-residual saliency (OpenCV's `saliency` module, which ships only in the contrib build: TESTED 2026-11-08, absent from opencv-python 4.13.0 here) or the thumbnail-caption method in section 13 | Hero first, stops in order |

**Derive each threshold from the brief, not by eye.** A cutoff picked by eye can be exactly wrong while the tool around it looks like a working instrument. OBSERVED(triangle-battle): a "loud fraction" metric, the share of frame brighter than a cutoff, had its cutoff set by eye just above the brightest large element in the frame. More than doubling the lit windows changed the picture visibly and moved the measurement not at all. Deriving the cutoff from the brief's own tonal bands, so "loud" came to mean brighter than anything that is only lit, made the number track the picture Where a brief gives value ranges anywhere, every threshold downstream of it should be derived from them. The general falsifier: **a measurement that does not move when the picture visibly does is a broken instrument, not a passing test.**

**Numeric value checks are necessary and not sufficient.** OBSERVED(cylinder-mirror): every frame passed lit, dark, hot and saturation while several failed by eye, as texture, unused periphery or lopsided. On a circular frame a coverage check (a high-percentile lit radius, and the lit centroid's distance from centre) caught the shrunken and lopsided ones. A low "lit" threshold on max channel counts bloom halo, so lit % includes glow.

**Contact sheet review: what it buys and what it hides.** OBSERVED(triangle-bashkit), one project's review loop. Every piece keeps one number for good, the client answers by number, and the client's picks override the builder's critique; when rounds go by with no picks, stop for the client's read. A sheet is cheap and shows a kit at once, but it judges pieces on the sheet's own light: cells too dark to judge, flat lighting that made a piece look weak that read fine in a ring, and small cells that hid detail. Pieces that only work in runs need a run on the sheet. A demo with real neighbours teaches more per render than a sheet. A frame counts as checked only once someone has viewed it. The numbered, labelled sheet: `scripts/contact_sheet.py` (folder or file list, `--help`).

Proof contact sheet and numbers: `scripts/composition_sheet.py` (this skill) writes one sheet (original, greyscale, notan, squint, thumbnail, flipped, busyness) and prints the numbers to check.

Black-shape proof: the blender skill, scripts/silhouette_proof.py.

How to read the results. Use the Read tool on the contact sheet and the silhouette PNG, since the agent can see images. Look for: whether the notan tile has one dominant value and a connected dark shape, whether the squint tile still shows a front and a hero, whether the thumbnail tile has a single brightest blob in the intended place, and whether the busyness tile has a gradient. Then compare the numbers to the pass values in the table.

## 16. Precedents: what the old solutions did and what transfers

| Work | What it solved | Transferable move | Confidence |
|-|-|-|-|
| Altdorfer, Battle of Alexander at Issus (1529) | Thousands of figures plus a continental view | Sky over a third of the panel as rest. Light and dark split between the armies. Several gaze routes | Moderate |
| Bruegel, Census at Bethlehem (1566) | A crowd of many separate actions | One perspective structure holding many small scenes. High viewpoint. Muted triadic palette | Low (blog analysis) |
| Uccello, Battle of San Romano (c. 1438 to 1440) | Chaos given a spatial structure | Foreground debris as orthogonals to a vanishing point | High |
| Rubens, Battle of the Amazons | A tightly packed, surging clash | Tightly packed composition; not enough sourced analysis for a technique claim | Low |
| Kurosawa, Ran | Readable armies in a battle | Colour code per side, telephoto stacking, crowds blocked as masses that sweep across the frame | Moderate |
| Jackson, Helm's Deep | A night battle that stays legible | Moonlight-motivated backlight, strong previsualisation, crowd agents with simplified behaviour | High |
| John Martin, Pandemonium and Fall of Babylon | Overwhelming scale with tiny figures | Tiny figures in fore and middle ground as scale referent, towering architecture | Low |
| Mughal and Persian battle pages, Japanese folding screens | Many simultaneous actions without perspective depth | Tiered stacking of actions, overlapping figures guiding the eye | Low |

The table is not exhaustive. Bruegel's Triumph of Death and Frazetta's covers were dropped 2026-11-08 after two passes unverified. Not researched: Moebius, Warhammer and Magic: The Gathering battle art, the Pelennor Fields staging, Hogarth, and the primary texts for Arnheim, Bouleau and Hambidge.

## 17. Where sources disagree, and where the theory does not transfer

- **Camera height.** Painters of crowds raised the viewpoint to spread fights vertically. Film and CG craft for colossal scale favours a low camera. Scene 02 supplied the missing data: a low camera caps how much a frame can hold, and tall architecture near a raised lens keeps the looming foreground. Low is good for one close giant, high is good for breadth; choose per shot. Resolved in scale.md.
- **Cropping the giant versus measuring it.** Cropping suits a close giant when the subject is menace or mystery; chaining suits a far giant when the subject is how big it is. One large object filling the frame cannot do both jobs. Resolved in scale.md.
- **Negative space.** The usual advice recommends it; a dense brief allows almost none. Altdorfer shows even the densest battle keeps a large quiet area. Resolved here with filled quiet masses (section 12.1); whether that satisfies a brief's "almost no empty canvas" intent is the client's call. The general negative-space lever is in scale.md.
- **Eye paths in player-controlled space are CONTESTED** (see staging.md, Explorable space). Eye paths here are a designed-camera technique.
- **Thirds and golden ratio.** Teaching sources present them as laws. The literature does not support them as causes of preference. They are sanity checks here, and contrast and mass structure carry the work.
- **Saliency models versus painters.** Saliency models predict bottom-up attention in photographs, and the centre bias alone beats many of them. Painters guide attention by meaning too (faces, gestures, story). Abstract figures have no faces, so bottom-up salience matters more here than it would in a figurative painting, but this has not been validated.
- **Painters control every pixel. A procedural scene does not.** Lighting, haze and overlap come out of the physics, so a placement that follows the spec can still produce unplanned values. That is why section 15 measures the render and does not trust the spec.
- **Numbers.** Where percentages are given for quiet area, loud area, cluster gaps and overlap margins, they are starting values and no source supports them. They exist to make the checks testable.
- **Perspective compression.** Painters flatten and tilt space as a convention. A 3D scene has true perspective and depth of field, so equivalents (tiered ground, long lens) are approximations.

## 18. Pre-flight composition checklist

Answer each from the proof render, with a number where one exists.

Structure
- [ ] Can I state the frame's read in one sentence, and does every large element serve it?
- [ ] Is there one dominant value covering more than half the frame, and do the darks connect into one shape?
- [ ] Do the posterised levels (3 or 4) show a clear light-dark pattern with the hero on a boundary?
- [ ] Is the dominant, subdominant and subordinate ranking visible in the squint test?
- [ ] Is the primary mass or focal point off dead centre, and is the weighted centroid within about 8 percent of centre (or deliberately offset 10 to 20 percent)?

Scale and framing
- [ ] Scale, camera height and lens items: scale.md, Scale pre-flight.
- [ ] Does the printed anchor table match the intended frame coordinates, rungs included?
- [ ] Does any large object have nothing happening on it, and would opening it into a framework help?

Depth
- [ ] Do the depth bands each have a narrower value range than the one in front, matching the table in section 4?
- [ ] Do far bands lift their blacks and dim their lights toward the haze value?
- [ ] Does every distant dark silhouette (an object darker than the haze) read darker than the sky directly behind it?
- [ ] Is every fight partly overlapped by something nearer, and are there no accidental tangents?
- [ ] Are there foreground masses at the edges, covering roughly 5 to 15 percent, softer and calmer than the hero zone?
- [ ] Do debris and beams run toward a vanishing point near the hero?

Crowd organisation
- [ ] Do clusters read as groups, with gaps at least about twice the inner spacing?
- [ ] Are cluster sizes uneven and spacing irregular, with no grid or wallpaper pattern?
- [ ] Is each side coded by shape and by hue, and do hues mix only at the front?
- [ ] Do figures follow a flow field, with jitter, so groups share a direction?

Hierarchy and attention
- [ ] Is there exactly one primary incident with the highest local contrast, saturation and edge sharpness?
- [ ] Does it use a feature channel the crowd does not use (so it pops)?
- [ ] Are there no more than about six separate hot blobs in the busyness or saliency map?
- [ ] Is the hero's saliency at least about 1.3x the next hot spot?
- [ ] Is there a quiet moat around the hero?

Edges and busyness
- [ ] Do same-side figures merge into masses, with crisp edges at the front and the hero?
- [ ] Does the busyness map show a gradient and a few large smooth zones (quiet area roughly 30 to 40 percent)?
- [ ] Is fine detail limited to band 1 and the hero?

Eye path (designed cameras)
- [ ] Does the eye path have a hub at the hero and four to six stops, linked by more than one device each?
- [ ] Do the stops land at the screen coordinates in the spec?
- [ ] Do edge elements point inward, with no bright accents at the frame edge?

Tests
- [ ] Greyscale, squint, thumbnail (64 to 128 px), flip and black-shape tests all passed?
- [ ] Do four to six 1920 x 1080 crops of the proof or final each hold their own local focus?
- [ ] Did I re-run the tests after the last scene change?
