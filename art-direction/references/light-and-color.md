# Light and color: lighting, atmosphere, palette, materials, glow

Lighting design, atmosphere, palette, material believability, glow: what to aim at, in any renderer. Engine measurements live in the blender skill (eevee.md). Composition and value structure live in composition.md.

Ratios and temperatures below are established cinematography and CG convention (CONVENTION), appearing across many sources and not in one citable place. Treat them as strong starting values and judge by eye with the pre-flight list at the end.

## Why the gap exists

Renderers are physically plausible by default, which makes artists lazy about the three things a renderer does not decide for you: where the light is, what the camera chooses to see, and how imperfect the world is. Pro images are designed, not captured. Roger Deakins' lighting is motivated by sources the audience can find in the frame, and he treats the photography as service to the story ([No Film School](https://nofilmschool.com/cinematography-should-never-stand-out-roger-deakins)). The material half of the same philosophy: CG is too clean, so you bring in the dirt of the real world ([Blender Guru, rust](https://www.blenderguru.com/posts/how-to-make-rust)).

## Lighting design

### Key, fill, rim, and what each is for

- **Key**: the dominant source. It decides mood, shadow direction and where the brightest value lives. Place it 30 to 45 degrees off the camera axis and higher than the subject for a classic read. At night the key does not have to be a conventional light. It can be the giant glowing object.
- **Fill**: lifts the shadow side. Keep it dim and cool. Key-to-fill around 4:1 (two stops) is drama, 8:1 and up is noir. Ratios are measured in stops, where each stop doubles or halves light ([UAL lighting notes](https://3danimationcrystal.myblog.arts.ac.uk/?p=1293)). The 4:1 figure is convention.
- **Rim (kick, back, edge light)**: a light behind and to the side of the subject that traces its edges. It separates the subject from the background, and it is what makes frames look expensive, because it adds a bright edge exactly where flat renders lose the silhouette. Place it 120 to 150 degrees from the camera axis, aimed to graze edges. One glossary-level guideline: a rim near key intensity gives a hard graphic outline, 50 to 75 percent of key gives subtle separation ([Morphic glossary](https://morphic.com/ai-glossary/rim-light), low authority, treat as convention).

Reverse key (upstage) lighting is the cousin worth knowing. The key sits on the far side of the subject so the camera sees mostly shadow side and bright edges. It reads moody and dimensional ([BlenderNation](https://www.blendernation.com/2022/12/24/one-simple-technique-to-improve-your-lighting-in-blender/)). In a battle scene it is nearly the default: backlight everything from the enemy side so the heroes get glowing outlines.

### Motivated lighting

Every light should have a plausible in-world source: a window, a lamp, fire, a screen, an energy seam, the moon. Deakins' Blade Runner 2049 work leans on practicals such as signage, screens and light off water ([StudioBinder](https://www.studiobinder.com/blog/blade-runner-2049-cinematography-analysis/)).

Name the motivations before placing lights: moon or sky (cool ambient), the giant's seams and apertures (hostile key), practicals carried by the subjects (small glows), and explosions and embers (flickering warm accents). If you add a cheat light with no source, hide it behind something and keep it weaker than the motivated ones.

Practical lights inside the scene double as visual interest. They create specular glints, spill onto neighbours, light the haze into visible volumes and give the eye points to travel between. Put a real light object near each important emitter. An emissive material alone makes a glowing surface. A point or area light beside it makes the neighbours react, and that reaction is what makes the glow believable (in EEVEE this is mandatory, not optional; measurements in the blender skill, eevee.md, Emission).

### Contrast and falloff

Light that falls off over distance gives a gradient across an object, which reads as 3D ([Gleb Alexandrov on light falloff](https://bazaar.blendernation.com/listing/blender-secrets-light-falloff-with-special-guest-gleb-alexandrov/)). The practical takeaway: use smaller, closer lights and avoid giant distant soft sources that wash everything equally. Spot lights with a soft edge and modest area lights give controllable falloff. Directional (sun) lights have none, so use them only for a low-strength moon term.

**A night city's hierarchy is a ratio.** OBSERVED(triangle-bashkit), one city under a Standard view, judged in the builder's review. The fix for a first city that read all purple was ambient terms down and emitters up (the numbers: the blender skill, scene-code.md); several frames improved at once. It has costs to plan for:

- Dark ambient removes the only light in districts with no practicals, so plan the practical layer when you cut ambient, for example hue pools at street level and uplights at the feet of big pieces.
- Ground lamps added for a bright hero overlit the paving.
- The dark sky is fragile. A sky only slightly too bright overhead reads tinted rather than black, and dense near-camera rain or a wide fog card can erase it; step these down in test frames until the sky holds (OBSERVED(triangle-bashkit)).

### Color temperature contrast

Warm key against cool fill is the backbone of most great images. Three reasons: it mimics the world, where sun and lamps are warm and sky fill is blue; warm and cool sit on opposite ends of the opponent-colour axis, so the contrast itself separates planes and subjects; and warm advances while cool recedes, which gives depth for free.

In a night scene you can flip the usual roles: cool moon ambient with a warm hostile key, or a cold light on the dominant mass against warm practicals on the small side. Pick one arrangement and keep it consistent. Blade Runner 2049 shows both directions: dominant orange with silhouette and heavy haze to preserve depth in the Vegas sequence, and cyans and desaturated greens in LA ([Color Culture](https://colorculture.org/blade-runner-2049-cinematography-analysis/)).

Pick temperatures as explicit Kelvin values so they stay coherent. Convention values: 1800 to 2700 K for fire and embers, 3000 K incandescent, 6500 K neutral, 8000 to 10000 K for moonlit shadow.

### Negative fill: shaped darkness

Black is not the absence of design. Negative fill is deliberately removing bounce so one side of a subject goes deep, which raises contrast and gives the lit side more punch. In a dark scene the difference between moody and underexposed is shaped darkness: dark masses with readable edges, and a few controlled highlights that show where the form turns.

Practical moves: keep ambient light very low and let haze and rim do the filling. Allow big dark masses, but guarantee at least one lit edge on each. Avoid a uniform ambient glow that turns every shadow into the same mid-grey.

### Lighting for silhouette readability

Silhouette lighting is the key skill for a cast of abstract geometric characters, because their identity is their outline.

- Light against dark, dark against light. A bright character needs a darker patch behind it. A dark character needs lit haze behind it. Check every key silhouette for this.
- Every major shape gets at least one edge with strong value contrast against its background (rim, glow, or backlit haze).
- Use haze as a light backdrop. A glowing fog bank behind the giant turns its mass into a pure, readable shape.
- Avoid overlapping silhouettes at the same value. Stagger value by depth.
- Keep silhouettes simple at thumbnail size. If a shape needs interior detail to be understood, the silhouette failed.

Deakins reduces characters and locations to forms in smog and mist for this reason. Silhouette plus haze separates layers in a scene dominated by one hue ([Color Culture](https://colorculture.org/blade-runner-2049-cinematography-analysis/); [ASC write-up](https://theasc.com/article/roger-deakins-asc-bsc-blade-runner-2049-discussion/)).

## Atmosphere and depth

Haze is the highest-leverage single addition to a dark scene.

1. It makes light visible (shafts, glows around sources), so light becomes an object in the image.
2. It creates atmospheric perspective for free, so distant things lose contrast and take on ambient colour, which sells depth and scale.
3. It softens harsh geometry and hides CG cleanliness.
4. It provides a backlit, glowing backdrop that gives dark shapes silhouettes.
5. It spreads coloured light through the frame, so the palette fills the image instead of sitting only on subjects ([StudioBinder on 2049's fog](https://www.studiobinder.com/blog/blade-runner-2049-cinematography-analysis/)).

Deakins uses fog to direct attention: important elements stay clear, less important ones sit behind the fog, and it diffuses harsh light so key elements stand out (StudioBinder).

The moves, in any renderer:
- **Height-falloff density.** Thick at the ground, thinning with altitude. The base of a monolith disappears into it and the top clears.
- **Break-up.** Modulate density with noise so the haze is patchy and layered.
- **Fog cards.** Large translucent planes with noisy alpha at different depths add layering where a global volume is uniform.
- **Light shafts.** Spot lights through the haze, or emissive seams casting beams. Aim shafts diagonally to support the composition.
- **Airborne particulate.** Thousands of tiny emissive or lit specks (embers, ash, dust, floating debris) in three depth layers: near ones large and soft (bokeh), mid ones sharp, far ones tiny. They give parallax-like depth, a scale cue and implied motion through streak direction.
- **Smoke.** Hide the contact line between objects and ground, break the straight edges of a mass, and give silhouettes a ragged edge. Smoke columns from wrecks add vertical leading lines.

EEVEE implementation: the blender skill, scene-code.md and eevee.md, Volumetrics.

Colour: give the atmosphere one hue related to the dominant light (blue for cool night, a warm tint near the giant's glow). Distant objects drift toward the ambient colour and lose saturation. The value windows per depth band, and the scoped check that a distant object darker than the haze never reads paler than the sky behind it, are in composition.md (Depth banding).

## Color design

Picking a palette is a choice among approaches, not one rule. Each approach below says where it came from and when it fits; choose per brief, and vary the approach across a set of candidates when the client has not said. In every approach value comes before hue (Value first, below).

### Ways to pick a palette

- **One dominant family plus one accent.** A limited palette reads as intentional, and 60/30/10 proportions are one guide ([freeCodeCamp](https://www.freecodecamp.org/news/the-60-30-10-rule-in-design/); CONVENTION). In a dark scene give the 60 percent to the dark base (blue-black and haze), 30 percent to a secondary (the dominant mass's hue or mid-tone atmosphere), and 10 percent or less to the saturated accent. Fits a restrained frame, a night scene, or one subject that has to win. Not for a brief that wants many hues: one project set a floor on hues per scene and rejected a set that had drifted into a few related hues (OBSERVED(cylinder-mirror)).
- **Many saturated hues on true black.** OBSERVED(cylinder-mirror), emissive work on black: many hues in one scene, each glowing element surrounded by dark space so it pops, with glow tuned per hue so every hue reads, not just the brightest (Color balance in glow, below). Across a candidate set, limited palettes were welcome as some of the candidates, not all of them.
- **Complementary and split-complementary.** A cyan hero against an orange-red mass is complementary and high contrast. Split-complementary (cyan against red-orange and yellow-orange) adds variety without chaos (CONVENTION). Fits two opposed forces.
- **Temperature contrast.** Warm against cool, chosen as Kelvin values (Color temperature contrast, above). Fits any scene with a key and a fill; it can sit under any of the other approaches.
- **Emotion first, from a color script.** Ralph Eggleston's Pixar color scripts mapped color, value and drama across a whole film on long strips of paper ([Hyperallergic](https://hyperallergic.com/610771/the-art-of-pixar-chronicle-books/)), and often started as value scripts, the light-dark journey before hue. For a single frame: decide the emotion, then the value structure, then the hues. "Pixar but dark" means clean, readable shapes and saturated accents under low-key light, not murky desaturated grime. Fits a sequence, or a frame whose mood the brief names.
- **A wedge of the wheel.** Restrict all hues to a chosen wedge of the colour wheel, a common painters' method (CONVENTION, source not located). It keeps a multi-hue crowd coherent without limiting it to one family.
- **One family per side, per piece or per district.** Hue as a grouping channel: one family per side of a conflict (composition.md, section 12.2), or one per piece of a kit with a hue lean per district as a layout input. OBSERVED(triangle-bashkit): one family per piece kept a mixed kit coherent, but a city with no district lean read as one hue at street level.
- **Take it from the reference.** If a reference exists, measure its hue count and each hue's share into the target profile (lookdev.md) and match that, rather than choosing by any approach above.
- GAP(2026-11-08): more palette-picking approaches wanted, for example a palette sampled from a photograph, harmony schemes beyond complementary, or palettes for daylight and high-key work. None is sourced in this corpus yet.

### Handling color once the palette is chosen

- **Keeping neon from looking cheap**, for a restrained neon look. Neon looks cheap when it is pure RGB, uniformly bright and everywhere. One weak source (a vendor tips page, [Piktochart](https://piktochart.com/tips/cyberpunk-color-palette); ASSERTED) suggests saturation around 70 to 90 percent, not 100, and saturated area limited to a small fraction of the frame. Give emitters a near-white core with coloured falloff, match bloom and spill hue to the source, let distant neons dim and desaturate through haze, and keep each light source to one hue so the dark base does most of the work. A brief that wants saturated colour on black uses dark space around each element in place of the area limit (many hues, above).
- **Warm against a cool neon frame.** OBSERVED(triangle-bashkit), the builder's review: warm gold interiors at street level did the most for a cool neon frame, as a complement. A single warm process gives a warm beat if lit openings stay low enough that it remains the brightest thing. Neon stayed thin and subordinate to a dim fill and rim so the whole mass read. The view-transform numbers stay with the project.
- **Saturated coloured light replaces material colour.** HEURISTIC, from one observation, OBSERVED(client-commission): brown wood stopped reading as brown at night under a saturated rake light. A rake analogous to the palette held it; a nearby but off-hue rake washed the material out. The view transform and renderer for that observation were not recorded, so check it in your own pipeline before relying on it.
- **Value first, hue second.** The squint test and a greyscale conversion expose value structure ([Draw Paint Academy](https://drawpaintacademy.com/painting-tests/)). Reduce the image to three or four values (dark, mid, light, plus a tiny peak) and put the darkest darks next to the lightest lights at the focal point. To check a render, make a 25 percent-size copy, desaturate it, blur it, and confirm that silhouettes and the focal point still separate.
- **Avoid the muddy mid-tone trap.** Dark scenes go muddy when everything sits at similar low-contrast greys, usually from a global ambient lift and emitters of similar strength. Drop the ambient level. Keep true deep darks. Let mid-tones live only in haze and glow falloff. Separate planes by value steps and add a few strong highlights. If the histogram is a hump in the lower middle with no tail at either end, it will look like mud.
- **The Blade Runner 2049 benchmark.** Color carries the emotion, lighting shapes form, blacks stay deep without losing detail, highlights roll off gradually ([Color Culture](https://colorculture.org/blade-runner-2049-cinematography-analysis/)). Gradual rolloff comes from the display transform, which is renderer-side (the blender skill, eevee.md, Color management).

## Material believability

- **Material identity.** Give every object a material reason (painted steel, cast ceramic, anodised alloy) and vary base colour slightly per object, so a field of identical shapes does not look stamped. No exactly-default grey.
- **Roughness variation is the most important single property.** Beginners most often skip it, and the material then looks flat even with good colour and bump. Real surfaces have uneven roughness from handling, weathering, polish and dirt. Drive roughness from layered noise confined to a believable band (painted metal roughly 0.25 to 0.6), add fine noise for micro-variation and stretched, directional noise for brushed or dragged wear. Avoid exactly 0 or 1 on weathered surfaces; clear technical glass is the exception (the blender skill, eevee.md, section 4).
- **Imperfections.** Smudges and fingerprints are low-frequency roughness noise. Scratches are thin stretched patterns through a sharp ramp, driving roughness and a slightly lighter base colour. Dust is a mask from the surface normal against up, giving a light rough blend on top faces. Edge wear shows bare metal where edges catch scratches; the robust route for script-generated geometry is an edge-angle mask computed in the build script and used to blend a worn material (per-object variation: the blender skill, scene-code.md, Per-object variation). The principle behind "warble" tutorials is cheap noise-driven displacement, rotation and scale jitter ([BlenderNation](https://www.blendernation.com/2020/04/10/lazy-tutorials-cg-realism-with-warbles-in-blender/); the method is video-only).
- **Bevels.** Nothing real has a perfect 90-degree edge, and sharp edges catch no highlight. Bevel every hard edge the camera can resolve: a bevel below a pixel is wasted geometry, so gate bevels by camera distance, working out where a bevel drops below a pixel for the lens and resolution (OBSERVED(triangle-battle)). The modifier recipe and the EEVEE specifics: the blender skill, scene-code.md, Bevels and edge masks.
- **Metallic versus dielectric.** Metallic is nearly binary, 0 or 1, with in-between values only at transitions such as rust over metal. Do not use 0.5 metallic as a compromise. One working exception: a low metallic on interior shells so lamps show on them (the blender skill, scene-code.md, Dark materials). Worn paint exposes metal at edges.
- **Pure values kill realism.** Pure white and pure black albedo do not exist in real materials: keep albedo roughly 0.03 to 0.9 in linear, and add large-scale value drift by multiplying in low-frequency noise at 5 to 15 percent.
- **Stained glass has two jobs.** OBSERVED(triangle-bashkit). It has to work backlit and unlit, so judge both states from one build (the swap, and the unlit tint: the blender skill, scene-code.md, Backlit cut panels). Unlit panes need enough tint to read as dark jewels. A combined fret and glass treatment suited simple solids and got busy on an already patterned piece (OBSERVED(triangle-bashkit)). Neon on hot glass disappears, so signs on lit glass use dark stencils and neon goes on dark plates. Designed windows beat random patches: lead lines drawn first, panes found from them, one hue family per window.
- **Grounding.** Objects float without contact cues: contact shadows and occlusion, scorch rings, dust and small debris at bases, wet ground with noisy, low roughness reflecting the neon, emissive spill onto the floor.

## Glow that reads as light

Glow reads as light and not bright paint when it behaves like a real source.

- Give it a hot, near-white core with the saturated hue at the edges and in the halo, because bright real sources clip toward white. Mix a little white into the emitted colour at high strength, or use a gradient across the glowing shape.
- Add variation inside the glow: flicker, filaments, panels, noise-modulated strength. Uniform emission looks like a flat colour fill.
- Make the glow affect the world. Nearby surfaces pick up its hue, haze lights up around it, specular highlights show on neighbours. Add a real light, a glare or bloom pass, and scattering in the haze.
- Emission strength ranks hierarchy only below the view transform's clip range: there, make the hero focal point brightest and background accents much dimmer. Above it, use size (composition.md, section 6).
- For a frame with one hero source, keep glow areas small: a few percent of the frame, because when everything glows, nothing does. Emissive-on-black work is mostly glow; there the black around each element does this job (Color design, many hues).
- Follow in-world logic: seams, vents, apertures, cores. Glow that follows the geometry's structure feels engineered.
- Emissive pop needs three value tiers at once: a clipped core, a saturated halo, connected black around them. Haze with no black lifted the frame to grey; thin strokes with no compositor read as pen lines (OBSERVED(cylinder-mirror), the client's verdicts). Strength ranges: the `blender` skill, eevee.md section 8.

## Color balance in glow

Where glow thresholds on luminance, halo energy goes roughly as G = (L - T) x stroke_px, with L = strength x Rec.709 luminance, T = the candidate's Bloom threshold and stroke_px = stroke width in pixels at a fixed output width. Equal strengths give unequal glow, because Rec.709 luminance differs a lot by hue: reds, magentas and violets sit low, yellows and yellow-greens several times higher. Compute it for your own hues. To find a G target, measure G on strokes the client liked and on ones they flagged (OBSERVED(cylinder-mirror), one rater, one family).

A compensating strength, `strength = (T + G_target / stroke_px) / lum`, with a cap where thin-stroke cores start eating hue, is HEURISTIC: on its one trial it did not equalise halo across hues (OBSERVED(cylinder-mirror)). Treat it as a starting value and check per-hue halo.

## Pre-flight

Lighting
- [ ] Is there a clear dominant key, and can I point to its in-world source?
- [ ] Does every major silhouette have at least one rim or backlit edge?
- [ ] Is key-to-fill at least roughly 4:1, or deliberately lower?
- [ ] Is there warm/cool contrast, arranged consistently across the frame?
- [ ] Is ambient light low enough that shadows are shaped, not washed to grey?
- [ ] Does each important emitter have a real light beside it, spilling onto its neighbours? (In EEVEE this is mandatory; the blender skill, eevee.md, Emission.)

Atmosphere
- [ ] Is there haze with height falloff and visible light shafts?
- [ ] Do distant objects lose contrast and shift toward the ambient colour?
- [ ] Are there particulates in several depth layers, and does smoke break up contact lines and straight edges?

Materials
- [ ] Does every surface have roughness variation, with no values at exactly 0 or 1 unless intended?
- [ ] Is there wear, dust, scorch or smudge in proportion to the object's history?
- [ ] Do emitters have a hot core, internal variation and falloff, and (for a one-hero frame) cover only a small fraction of it?
- [ ] Are objects grounded, with contact shadow, debris or dust at their bases?

Color and value
- [ ] Was a palette approach chosen for this brief (Color design), and does the frame's hue count match it?
- [ ] Greyscale check: do three or four values still separate shapes and the focal point?
- [ ] Is the histogram free of a flat mid-tone hump and of large pure-black or pure-white clipped areas?

If three or more boxes in one section are unchecked, fix that section before spending time on a final render.
