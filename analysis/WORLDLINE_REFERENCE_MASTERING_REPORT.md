# Worldline Lab — Deep Reference Mastering Report

Status: complete reference reverse-engineering; no new episode created  
Date: 2026-10-09  
Primary source set: `references/samples`  
Corpus: 14 supplied files, 13 unique videos, 935.7 seconds of unique footage

## 1. Scope, evidence, and confidence

This report treats the supplied videos as animation references, not as branding templates. Every file was decoded across its complete duration. Each unique video was inspected at 0%, 5%, 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 90%, and the ending. Eight additional high-change frames per file were found by comparing half-second samples in CIELAB color space, then checked against the surrounding story state. Audio streams were decoded and measured in one-second windows.

The two files named `7066782ad2f41d149065d8c936812b9e.mp4` and `7066782ad2f41d149065d8c936812b9e(1).mp4` have the same SHA-256 hash (`1DB92C…AC758F`). They are one zombie reference, not two independent creative examples.

Evidence strength:

- High confidence: geometry, composition, object density, color progression, lighting, visible motion, scene states, cuts, transitions, event staging, final frames, resolution, frame rate, codec, and measured audio envelope.
- Medium confidence: exact camera paths and physical simulation methods, which are inferred from rendered frames rather than source project files.
- Deliberately not invented: the precise identity of music cues, narration voices, or off-screen sound effects. The files prove an audio track and its dynamics; semantic audio labels require monitored auditioning. Recommendations below are production requirements, not claims that an inaudible cue definitely exists in a reference.

All references are 576 × 1024 vertical proxies at approximately 30 FPS. This is evidence of composition and timing, not a recommended mastering resolution.

## 2. Reference inventory and measured structure

| ID | File | Topic | Duration | Strong visual-change candidates (s) | Audio RMS / spread |
|---|---|---|---:|---|---:|
| R01 | `f47772957016a648e86da12965f4a600.mp4` | Rain for 1,000 years | 95.97 | 18, 21.5, 23.5, 25.5, 55, 61.5, 70, 88 | -13.80 dBFS / 18.89 dB |
| R02 | `4a7422e4ac644fce42faf420c6ee892b.mp4` | 60-meter giant | 69.00 | 12, 18, 32, 37.5, 41, 43.5, 53.5, 65 | -12.78 / 14.14 dB |
| R03 | `150e1171fbadcbdcd91bdb17464dcf13.mp4` | 1,000-year sandstorm | 93.97 | 5.5, 7.5, 24, 40, 61.5, 81, 84.5, 88.5 | -13.36 / 15.51 dB |
| R04 | `5918a3830da3c011942276f0aeb900af.mp4` | Everyone becomes cheese | 65.00 | 5, 9, 13.5, 18, 36, 40.5, 57.5, 61 | -16.51 / 1.37 dB |
| R05 | `7066782ad2f41d149065d8c936812b9e.mp4` | Zombie outbreak | 63.97 | 7, 9, 11.5, 15.5, 17.5, 21, 30, 50.5 | -11.51 / 6.81 dB |
| R05-D | `7066782ad2f41d149065d8c936812b9e(1).mp4` | Exact duplicate of R05 | 63.97 | identical | identical |
| R06 | `cb3b02602de8ba4faab845f698ba9c72.mp4` | Flat Earth | 65.00 | 20.5, 24, 30, 40.5, 43, 51, 58, 61 | -17.16 / 12.10 dB |
| R07 | `d7202baa78a3b6ad72f8e36168113f09.mp4` | Oxygen rises 1%/second | 80.07 | 20, 23, 25.5, 31, 34, 38.5, 42.5, 64.5 | -6.83 / 30.63 dB |
| R08 | `Download.mp4` | Gravity off for 10 seconds | 58.73 | 6.5, 10, 18, 20.5, 26, 32, 45, 57.5 | -24.65 / 12.29 dB |
| R09 | `Download (1).mp4` | Fart on every planet | 60.00 | 0.5, 5, 11, 17, 30, 37, 51, 58.5 | -17.26 / 11.88 dB |
| R10 | `Download (2).mp4` | Sky disappears | 65.00 | 2, 11, 16, 25, 46.5, 50.5, 57.5, 61 | -16.79 / 15.40 dB |
| R11 | `Download (3).mp4` | Sun disappears | 62.00 | 3.5, 8.5, 26, 29, 45, 47, 51.5, 58 | -16.54; long silent tail |
| R12 | `Download (4).mp4` | Rogue planet hits Earth | 77.00 | 7, 12.5, 28.5, 36, 47, 52.5, 66.5, 70 | -14.76 / 14.82 dB |
| R13 | `Download (5).mp4` | Earth has Saturn-like rings | 80.00 | 27.5, 31, 47.5, 51, 55, 62.5, 65.5, 68.5 | -11.36; long silent tail |

“Visual-change candidate” means a strong frame-to-frame appearance change, not automatically a hard edit. Weather, flashes, occlusion, and large object motion can also trigger it.

## 3. Video-by-video reverse engineering

### R01 — Rain for 1,000 years

Timeline:

- 0–9.6 s: high oblique view over a complete city intersection. Crosswalks, lane markings, traffic lights, storefront awnings, taxis, delivery vehicles, pedestrians, and regularly spaced trees establish a normal city before rain becomes the premise.
- 9.6–28.8 s: Hour 1 → Hour 25 → Day 7. Rain thickens, visibility drops, umbrellas appear, drains fail, standing water becomes a navigable layer, and night window lights preserve depth.
- 28.8–48 s: Day 7 → Day 33 → Month 9. The same intersection remains recognizable while water rises from curb height to a street canal. Cars give way to small boats; daily behavior adapts instead of vanishing immediately.
- 48–67.2 s: Month 9 → Year 3 → Year 1,045. Water occupies the full street volume; only upper architecture and floating debris remain. The palette loses warm city color and becomes deep blue-gray.
- 67.2–86.3 s: rain stops around Year 1,062; water recedes over centuries. Mud, abandoned structure, and exposed street furniture make the reversal physical.
- 86.3–95.97 s: Year 2,822. Vegetation has overtaken the same block, producing a readable before/after hero shot rather than an unrelated ending.

Production anatomy: simplified but coherent Manhattan-like architecture; strong window rhythm; repeated trees used as a scale grid; high camera makes water level measurable against façades. The event is not “rain particles.” It is a persistent state machine affecting drainage, transport, light, population, building access, debris, water level, and ecological succession. Best lesson: preserve one anchor composition long enough for accumulated change to become the spectacle.

Audio evidence: broad dynamic spread (18.89 dB); largest measured one-second rises near 70, 89, and 92 s align with the rain-stop/recovery/final-reveal region. Use continuous rain as a bed whose spectral density, surface impacts, and low-frequency water movement change by era; do not loop one unchanged rain file for 90 seconds.

### R02 — 60-meter giant walks into the city

Timeline:

- 0–13.8 s: centered avenue canyon; giant framed between tall buildings, with cars, fire hydrant, street furniture, crowd, helicopters, and birds giving immediate scale. Distance readout falls roughly 474 → 344 m.
- 13.8–27.6 s: medium and low angles emphasize mass. The giant crosses façade lines while street-level people remain small, readable witnesses.
- 27.6–41.4 s: 266 → 32 m. Foreground heads, vehicles, emergency activity, dust, and increasingly low camera positions intensify proximity. A giant foot displaces air/dust and dominates the street.
- 41.4–55.2 s: 6 m. Extreme low-angle hand/torso shots alternate with a toppled/collapsing body. Debris and dust enter the near field.
- 55.2–69 s: the giant lies across the avenue and against buildings. Final frames hold the consequence long enough to read the scale relationship.

Production anatomy: buildings are not background wallpaper; their height, windows, and street width measure the impossible body. The giant has rounded, jointed human geometry with cloth-color blocking, while the city is rectilinear. Movement remains slow enough to sell mass. The camera changes height and distance as the threat approaches. Best lesson: scale must be triangulated by at least three familiar references—people, vehicles, and architecture.

Audio evidence: largest rise at 65 s (+12.9 dB), with other large rises at 50 and 55 s, matching collapse and aftermath. The correct stack is footfall transient + sub weight + façade/debris layer + crowd response + short reverb tail, with the camera shake driven by the same impact envelope.

### R03 — Sandstorm for 1,000 years

Timeline:

- 0–9.4 s: aerial city setup, warning banner, orange wall of dust, and a wind/visibility gauge. The storm is spatially legible before it engulfs the street.
- 9.4–28.2 s: wind climbs above 200 km/h; palm trees bend, loose objects streak, particles cross camera, and visibility collapses. By Hour 36, the street still reads beneath the storm.
- 28.2–47 s: Hour 36 → Month 6 → Year 34. Sand depth becomes the main continuity metric. Doors, roads, and lower façades disappear; only tower tops survive.
- 47–65.8 s: Year 34 → Year 499 → Year 1,000. The city silhouette sinks into an orange atmospheric field. Persistence is communicated through the same towers at successively lower visible height.
- 65.8–84.5 s: all-clear; clean pale desert replaces the storm. Survey/excavation figures and equipment introduce a new scale and story goal.
- 84.5–93.97 s: distant expedition crosses layered dunes; the ending implies a buried city beneath the “empty” landscape.

Production anatomy: strongest atmospheric-depth reference. Near particles are large/fast, mid particles numerous, far layers become haze; silhouettes disappear by depth, not uniformly. Palms, signs, and debris visibly respond to wind. The persistent warning/status design is useful as causal telemetry but is not Worldline branding.

Audio evidence: rises near 62, 82, and 90 s correspond to late storm/clear/reveal transitions. Sound should evolve from wind gusts and grit impacts to dense low-pass roar, then drop decisively at the all-clear so the absence of storm becomes an event.

### R04 — Everyone turns into cheese

Timeline:

- 0–13 s: beach overlook and population establish the joke; one articulated figure becomes the readable hero. Human-to-cheese transformation keeps limbs and pose but changes head/material identity.
- 13–26 s: total-mass beat and dog interaction. Props—umbrellas, towels, shoreline items—keep the beach inhabited.
- 26–39 s: heat/sweat consequence and closed-sauna gag. Different character clusters and body types prevent a single repeated mannequin from carrying every beat.
- 39–52 s: hugging/squeaking and cheese-type variation; actions are staged as small readable vignettes.
- 52–65 s: aged “extra sharp” grandfather gag, then wide beach call-to-action.

Production anatomy: intentionally simpler than the catastrophe films, but strong at character continuity, comedic specificity, readable poses, and object-based punchlines. Characters use capsule/cylinder limbs, simple joint rotations, and high-contrast clothing. Beach water carries specular texture; umbrellas, clouds, rocks, birds, and shadows keep the flat sand from feeling empty.

Audio evidence: unusually compressed/steady body (1.37 dB P10–P90 spread), with the largest rise at 61 s. This supports a constant narration/music-driven comedy cadence rather than a disaster crescendo. Production lesson: not every premise needs maximum dynamic violence; match the mix arc to genre.

### R05 — Zombie outbreak on your street

Timeline:

- 0–6.4 s: aerial of a functioning block with traffic, people, trees, storefronts, crosswalks, and varied façades.
- 6.4–19.2 s: camera descends to sidewalk. A foreground tree occludes the move, giving parallax and physical camera placement. Pharmacy/storefront windows, pedestrians, and the infected/survivor counter establish the first bite.
- 19.2–32 s: counter moves 2 → 4 → 13; the camera alternates between sidewalk and intersection. Steam/smoke and traffic signals maintain environmental activity.
- 32–51.1 s: 13 → 39 → 65. High angles show propagation through the block while fog, fire points, stopped vehicles, and thinning survivors alter the same world.
- 51.1–63.97 s: street-level chase into a dark crowd, then a stark factual end card.

Production anatomy: the outbreak is sold by population-state change rather than gore. The same citizens switch from walking/standing to attack, flight, clustering, and disappearance. The camera uses occlusion and elevation changes to make a modest block feel larger. The infected counter is editorial evidence of exponential growth, but Worldline should use temporary metrics rather than a persistent borrowed HUD.

Audio evidence: relatively dense/steady body (6.81 dB spread), followed by a large rise near 60 s. Use a staged crowd system: ordinary city bed → isolated alarm/reaction → layered running/shouts → dense pursuit → abrupt or controlled end-card reduction.

### R06 — Earth is flat

Timeline:

- 0–13 s: fixed balcony foreground overlooks village, lake, forest, and mountain ridge. The horizon metric rises while birds animate depth.
- 13–26 s: horizon flattens; gravity tilt reaches 8.5°. Rocks, water, and air visibly move toward the middle while the camera preserves the geography.
- 26–39 s: hard scale jump to the literal edge of the disc, with ocean surface, exposed crust/mantle wall, star field, and railing.
- 39–52 s: gravity points sideways at 71°; the edge view makes the abstract rule spatial.
- 52–65 s: return to the village. The edge rises from tens to thousands of miles; ocean pours toward the center and the landscape folds/crushes into a spherical tendency.

Production anatomy: the film alternates a stable human viewpoint with one explanatory macro viewpoint. The balcony railing is a powerful foreground anchor. Water and terrain are the protagonists; village objects act as scale. Best lesson: an impossible physical rule becomes believable when one familiar geography is retained and one macro cut explains what the familiar camera cannot.

Audio evidence: 12.10 dB spread, with rises around 13, 52, and 63 s. Those points map to first transformation, return from edge, and final crush. Use tonal/tactile cues for gravity direction and water migration, not only generic impacts.

### R07 — Oxygen increases 1% every second

Timeline:

- 0–8 s: dusk suburban gathering with pool, tables, chairs, fences, houses, apartment blocks, roads, people, fire sources, and water tower. Oxygen starts at 21%.
- 8–24 s: 26 → 42%. Existing flames grow first; plants, vinyl, and structures ignite in causal sequence. People remain visible around the pool and yard.
- 24–40 s: gas station and grills turn the neighborhood into a connected fire field. The citywide view grows brighter while the sky remains a stable dusk gradient.
- 40–56 s: 58 → 74%. Pool becomes the safe pocket; steel begins to soften/burn. Camera alternates overview and close explanatory vignette.
- 56–72 s: 74 → 90%. Black environment, white-hot flames, glowing windows, embers, and distant burning towers create a final inferno tableau.
- 72–80.07 s: end transition.

Production anatomy: perhaps the best causal escalation reference. It begins with a populated, prop-rich party and converts existing objects one material class at a time. Fire changes illumination, not just particle count: nearby surfaces brighten, distant city windows contribute, smoke/embers vary with oxygen state, and the pool reads as a cool-color refuge.

Audio evidence: the loudest measured corpus item (-6.83 dBFS RMS) with extreme 30.63 dB spread and decoded overs. This is dramatic but not a safe mastering target. Preserve the arc—small ignition → neighborhood roar → city inferno—while leaving headroom and limiting true peak below -1 dBTP.

### R08 — Gravity turns off for 10 seconds

Timeline:

- 0–11.7 s: street-level normal afternoon; dense façades, pedestrians, cars, trees, fountain, and telemetry establish 9.81 m/s².
- 11.7–23.5 s: gravity reaches zero. Cars cannot brake; people, fountain water, and loose objects rise. Tilted camera and foreground tree exaggerate disorientation.
- 23.5–35.2 s: gravity returns. Water falls from 127 m and objects crash onto the avenue; camera pulls higher to show many simultaneous consequences.
- 35.2–47 s: counterfactual scale jump—if it lasted ten minutes, Earth begins to fail. Planetary geometry replaces the street.
- 47–58.73 s: humorous room-scale coda compares gravity with a refrigerator magnet, then end card.

Production anatomy: strongest scale ladder: human street → neighborhood consequence → planet → domestic punchline. The event affects every object class with the same force rule. Fountain water is especially useful because it shows both absence and return of gravity.

Audio evidence: quietest reference (-24.65 dBFS RMS) yet still has rises around 6, 16, and 33 s. Do not copy its low absolute level; copy the synchronization between onset/return and audio accents.

### R09 — Fart on every planet

Timeline:

- 0–6 s: black title/metric to Earth hero figure.
- 6–24 s: Moon, Mars, Venus, and Titan. The same astronaut/mannequin remains centered while ground, sky, color, and labels change.
- 24–42 s: Jupiter then Uranus. Body orientation changes on the gas giant, adding one physical gag to an otherwise locked format.
- 42–60 s: confirmation beat, return to Earth, and end card.

Production anatomy: lowest-density world reference. Its value is modular continuity: one clear subject, one fact per environment, instant color-coded location change, and a stable comparison frame. It is not the density target for a disaster episode. Use this structure for list/comparison premises only.

Audio evidence: 11.88 dB spread with several early rises. The episodic structure calls for short transition signatures per planet and a consistent voice/music bed. Avoid identical visual and sonic timing for every stop; one exception beat prevents monotony.

### R10 — The sky disappears

Timeline:

- 0–13 s: balcony/village/lake/forest/mountain composition under normal daylight; pressure drops to 0 and sky becomes space-black.
- 13–26 s: aircraft fall, vapor/atmospheric residue streaks upward, and lake begins violent thermal change.
- 26–39 s: water reaches freezing; frost spreads across terrain, buildings, and trees while the camera stays fixed.
- 39–52 s: ozone protection gone; vegetation bleaches and dies over days.
- 52–65 s: month-scale barren world and a full-frame ice-blast/frost aperture transition to the end card.

Production anatomy: one composition carries most of the transformation, proving that camera motion is optional when world-state motion is rich. The foreground railing, middle village, horizontal lake, forest strip, and mountains form measurable depth bands. Each consequence owns a distinct material change.

Audio evidence: 15.40 dB spread, with rises near 29 and 39 s. Build sound by removing the normal atmosphere bed, then replacing it with designed pressure/thermal cues; silence or filtered sound can express “no air” more effectively than a constant roar.

### R11 — The Sun disappears

Timeline:

- 0–12.4 s: same balcony geography in daylight; last-sunlight countdown.
- 12.4–24.8 s: space-black sky and dark moon; village/lake lights become the depth system.
- 24.8–37.2 s: day 1 → week 2 → month 5. Frost, snow, lake ice, and vegetation death progress in layers.
- 37.2–49.6 s: year 1 at -103°F; the landscape holds long enough to read total transformation.
- 49.6–62 s: frost/ice texture closes over frame, then factual end card. The final several seconds are effectively silent.

Production anatomy: demonstrates color and emissive progression—daylight blue/green → black/amber lights → cold blue-white. The stable view makes the lighting change itself the camera event. The ice aperture is a motivated transition because it grows from the premise.

Audio evidence: normal body around -16.54 dBFS but a long silent tail creates misleading extreme spread. Treat the silence as a deliberate ending device only if it supports the final card; otherwise retain a low atmospheric tail.

### R12 — Rogue planet hits Earth

Timeline:

- 0–15.4 s: coastal city, ocean, cruise ship, park, varied towers, roads, vehicles, and a small planet. Aerial park cut reorients scale.
- 15.4–30.8 s: planet grows; city activity stops; sea begins pulling away. Viewpoints alternate harbor and building-height aerial.
- 30.8–46.2 s: gravity deformation escalates. Roads, park, towers, and water respond; dusty atmosphere begins occluding the city.
- 46.2–61.6 s: tower failure, orange shockfront, fire wall, and crustal destruction move from horizon toward camera.
- 61.6–77 s: the crust appears peeled into debris; ash/rock passes the lens, then a polished end card.

Production anatomy: strongest all-around spectacle reference. It combines a genuinely varied city, multiple camera platforms, a growing celestial object, water displacement, structural failure, flash, fire, dust, shockfront, foreground debris, and aftermath. Crucially, escalation changes systems and viewpoints; it does not merely scale the planet sprite.

Audio evidence: measured body grows toward late acts without unsafe overall loudness (-14.76 dBFS RMS). This is the best mix-shape reference: ambience and tension early, dense causal layers late, then a controlled ending.

### R13 — Earth has Saturn-like rings

Timeline:

- 0–24 s: Chicago rooftop/balcony composition. Planters in the foreground, skyline/window grid in the middle, and giant rings in the sky establish four depth layers. Sunset shifts toward night.
- 24–40 s: city lights rise; rings brighten the night. A few meteors appear.
- 40–56 s: meteor rate jumps from 4 to hundreds/thousands per minute. Trails cross multiple depths; first major tower strike introduces flash and smoke.
- 56–68 s: impacts spread across Chicago; fire, smoke, embers, and falling streaks fill near and far planes while the foreground railing/planters retain human scale.
- 68–80 s: clean end card follows the sustained inferno.

Production anatomy: strongest fixed-composition escalation reference. It proves that one hero angle can carry a whole episode when the sky, lighting, windows, meteor density, impact locations, fire, smoke, and debris all evolve. The ring is always readable; effects frame it rather than erase it.

Audio evidence: energetic body (-11.36 dBFS RMS) followed by a long silent tail. Measured rises near 31, 38, 41, and 48 s fit the night/meteor transition. Preserve headroom for the first large strike and avoid turning every meteor into the same full-volume impact.

## 4. Cross-reference animation DNA

### 4.1 Visual classification

The family is stylized real-time 3D, not one generic “low-poly” look. Architecture is simplified and rectilinear; people use rounded jointed primitives; vegetation and rock are faceted; water ranges from planar/specular to layered volume; hero phenomena use exaggerated scale and denser particles. Materials are mostly matte with controlled specular highlights. Texture detail is secondary to silhouette, color blocking, repetition, and lighting.

Three subfamilies recur:

1. Persistent-world transformation: R01, R03, R05, R06, R07, R10, R11, R13.
2. Moving threat / multi-camera spectacle: R02, R08, R12.
3. Modular comparison or comedy: R04, R09.

Worldline should choose the subfamily from the premise; forcing every idea into a city-catastrophe template will make the work repetitive.

### 4.2 Geometry and object language

- Buildings: box-derived masses with meaningful width/height/setback differences, façade color families, window grids, roof caps/equipment, ground-floor signs, and occasional glass towers. Strong scenes mix 4–7 building families in one view.
- Vehicles: distinct silhouettes—sedan/taxi, van, truck, bus, emergency vehicle, boat, aircraft—plus glazing, wheels, front/back, and motion path. They are scale references and reaction agents.
- Characters: head, torso, upper/lower limbs or readable simplified equivalents; varied clothing colors, poses, group sizes, and roles. A crowd is a state system, not copied statues.
- Vegetation: trunk + faceted canopy or palm segments; varied height, hue, lean, and spacing. It communicates wind, season, fire, inundation, and abandonment.
- Props: signals, hydrants, railings, planters, umbrellas, tables, chairs, signs, awnings, fences, boats, streetlights, and debris. Props are what turn geometry into a place.
- Hero natural forms: layered surfaces and irregular silhouettes; avoid a single flat circle, cone, or translucent overlay.

### 4.3 Environment and composition

The strongest frame has four layers:

1. Foreground occluder/anchor—railing, tree, planter, vehicle edge, sign, spray, particles.
2. Midground activity—people, traffic, pool, street, buildings, boats.
3. Background scale—skyline, lake, mountains, harbor, distant district.
4. Hero/sky phenomenon—planet, rings, storm wall, giant, fire field, black sky.

Density is organized, not random. Ordinary objects repeat with rhythm; one hero object breaks it. Readability comes from clear value separation, controlled fog, and scale contrast.

### 4.4 Camera language

- Establish physical placement. Successful cameras sit on balconies, sidewalks, medians, rooftops, harbor edges, street corners, or aerial platforms.
- Slow drift/push reveals depth. Pans and tilts follow a cause. Low angles create mass; high angles reveal propagation.
- Use foreground occlusion during travel to sell parallax, as in R05.
- Change viewpoint when the story’s scale changes, not on an arbitrary timer.
- Fixed-camera episodes require richer state evolution; multi-camera episodes require continuity anchors.
- Impact shake envelope: 1–3 frame displacement/rotation attack, 4–10 frame high-frequency vibration, 10–24 frame decay. Scale amplitude by camera distance and support it with object/particle reaction.

### 4.5 Color and lighting progression

Normal worlds start with a balanced local palette. The event then takes ownership of color without collapsing everything into one tint:

- Water/rain: neutral city → blue-gray → near-black flood → warm recovery green.
- Sandstorm: daylight neutrals → saturated orange/brown → pale post-storm desert.
- Fire/oxygen: dusk blue/orange → bright orange → white-hot against black.
- Sky/Sun loss: day blue/green → black sky → cold blue-white.
- Rings/impacts: lavender sunset → night navy/gold → orange inferno.

Lighting must respond to the event. Fire adds local light and window contrast; celestial bodies affect sky and silhouettes; vanished light reveals practicals; storm density reduces distance contrast. A full-screen grade alone is insufficient.

### 4.6 Motion and reaction

Motion is layered by frequency and scale:

- Continuous: rain, wind, water shimmer, smoke, distant traffic, birds.
- Behavioral: walk, stop, point, film, flee, cluster, attack, shelter.
- Mechanical: vehicles brake, drift, collide, float, stop, reroute.
- Structural: bend, crack, tilt, collapse, settle.
- Spectacle: impact front, flash, fire spread, debris wave, terrain rise.

The key causal rule is propagation. The phenomenon acts on material classes and agents in an intelligible order. R07 ignites existing hot sources before harder materials; R01 floods drains before drowning façades; R05 changes one person before a crowd; R13 begins with isolated meteors before citywide impacts.

### 4.7 VFX, destruction, and particles

Effective VFX stacks have distinct jobs:

- Primary volume/surface: flood, storm, fire field, ring, planet, ice.
- Interaction layer: splashes, dust puffs, sparks, ripples, bending vegetation, broken glass.
- Atmospheric depth: fog, smoke, ash, sand, rain, embers.
- Energy/readability: short flash, bloom, rim light, silhouette contrast.
- Camera-space punctuation: near debris, droplets, heat warp, frost edge—used sparingly.

Destruction needs origin, force direction, mass hierarchy, and aftermath. Large chunks define structure, medium pieces carry motion, fine dust/embers sell energy. Debris that spawns everywhere with no source reads as decoration.

### 4.8 Editing, pacing, and transitions

The median pattern is one causal stage every roughly 8–12 seconds, with a smaller visual development every 2–4 seconds. Most clips use 5–8 major visual states over 60–96 seconds. Cuts are motivated by one of four needs: reveal a new scale, explain a consequence, show a reaction, or land a payoff.

Transitions are usually hard cuts, atmospheric occlusion, flash, darkness, or material wipes (ice/dust). The strongest are caused by the premise. Avoid generic zoom spins and constant camera cuts that destroy spatial memory.

Opening rule: in the first three seconds, show the complete question, a legible normal world, and either the anomaly or a clear promise of it. Final hero rule: hold the largest consequence for at least 1.5–3 seconds before the end card, with a familiar scale reference still visible.

## 5. Sound, music, SFX, and mix findings

Every supplied file contains stereo AAC at 44.1 kHz. The newer hashed references generally use AAC-LC around 128 kb/s; several `Download` references use HE-AACv2 around 32 kb/s. Codec bitrate is not a creative target. Worldline should master at a higher delivery quality.

Objective envelope findings:

- Best controlled catastrophe arc: R12, around -14.76 dBFS RMS with 14.82 dB P10–P90 spread.
- Strong dynamic storytelling: R01, R03, R10, and R12.
- Comedy/list format: R04 is intentionally steady, only 1.37 dB spread.
- Excessive decoded level/overs: R07. Copy its escalation, not its gain.
- Intentional/encoded silent tails: R11 and R13. These inflate spread statistics and must not be mistaken for superior dynamics.
- Audio-visual alignment is strongest when measured rises coincide with collapse/reveal regions: R02 around 50–65 s, R01 around 70/89/92 s, R03 around 62/82/90 s, and R05 around 60 s.

Required Worldline audio architecture:

1. Location bed: traffic, room, coast, wind, rain, insects, crowd, or distant city.
2. Premise engine: one evolving sound tied to the impossible process.
3. Object reactions: materials, vehicles, water, vegetation, structures.
4. Human layer: speech/noise/reactions appropriate to visible behavior.
5. Cinematic support: restrained music/drone, risers, sub accents, and transition sweeteners.
6. Hero stack: transient + low-frequency weight + midrange detail + environment tail.
7. Closure: deliberate reduction or tail under the end card.

Mix target: approximately -14 to -12 LUFS integrated, true peak no higher than -1 dBTP, narration consistently intelligible, early acts leaving 6–10 dB of perceived headroom for the payoff. Duck music and dense ambience under narration; never solve intelligibility by crushing the entire mix.

## 6. Reusable Worldline production system

### 6.1 Master object library standard

Each asset needs silhouette variants, material slots, LOD/detail modes, state hooks, and anchor points for VFX/reactions.

| Library | Minimum production families | Required states |
|---|---|---|
| Buildings | 6 urban, 4 suburban, 3 industrial, 3 civic/landmark | normal, dark, lit, damaged, burning, flooded/buried/frozen as relevant |
| Vehicles | sedan, taxi, SUV, van, box truck, bus, emergency, boat, aircraft | moving, stopped, braking, abandoned, damaged, floating/falling |
| People | 12 body/clothing combinations, 6 age/height silhouettes | idle, walk, look, point, film, flee, shelter, fall, crowd/attack as relevant |
| Vegetation | 5 deciduous, 3 conifer, 3 palm/shrub families | calm, wind, bent, burning, dead, submerged/buried/frozen |
| Street/scene props | signals, lights, signs, hydrants, rails, planters, awnings, tables, chairs, fences, umbrellas | intact, active, reactive, damaged, debris |
| Terrain/water | road, sidewalk, park, beach, lake, ocean, dunes, rock/ice | dry/wet, cracked, flooded, frozen, displaced, reclaimed |
| VFX | rain, snow, sand, fog, smoke, dust, ash, embers, sparks, debris, splash, shockfront | staged density, depth bands, wind/force direction |

Do not create “variation” by recoloring one mesh. At least silhouette, proportion, façade rhythm, or articulation must change.

### 6.2 New-world generation standard

Before animation, define:

- Premise-specific location and why it reveals the physics.
- Time of day, weather, and baseline palette.
- Camera map with at least three physically plausible positions unless a fixed-view transformation is deliberately chosen.
- Foreground, midground, background, and hero layers for every major shot.
- Ordinary activity loop that establishes life.
- Agent/material state table showing how each class reacts at every escalation stage.
- Continuity anchors that survive cuts or time jumps.
- One explanatory macro view only when the local view cannot show the rule.
- Final hero composition before intermediate shots are built.

A proposed world fails if it is an old street with a swapped celestial object, or if the premise can be removed without changing object behavior.

### 6.3 Event stack library

**Impact stack:** approach cue → contact flash → local deformation → debris impulse → dust/smoke expansion → camera shake → delayed secondary failures → settling particles/aftermath.

**Flood stack:** rain/source increase → drains/low points fill → curb overflow → vehicle/pedestrian adaptation → current/debris → access loss → full-volume inundation → recession residue → ecological recovery.

**Wind/sand stack:** distant wall → vegetation/loose-prop response → near particle streaks → visibility compression → sand accumulation → architectural burial → calm/clear contrast → excavation/reveal.

**Fire spread stack:** existing ignition sources intensify → nearby soft materials catch → vegetation/vehicles/structures propagate → local light and smoke rise → ember transport → citywide field → white-hot/black contrast → ash/ruin.

**Outbreak/crowd stack:** normal loops → isolated anomaly → witness pause/point → first flight/attack → traffic interruption → clustering and route change → population inversion → pursuit/empty aftermath.

**Gravity/force stack:** baseline motion → force parameter changes → loose/light objects react first → fluids reveal vector → people/vehicles lose control → structures/terrain respond → force return/reversal → collision field and settling.

**Thermal/freeze stack:** light/air change → practical lights/temperature cue → frost on small exposed edges → water phase change → vegetation loss → snow/ice accumulation → enclosing material transition.

**Transformation/comedy stack:** hero introduction → rule demonstration → second-order practical consequence → character interaction → exception/escalation gag → final callback.

## 7. HTML/Canvas implementation guide

### 7.1 Rendering architecture

- Use a deterministic fixed-step simulation at 30 FPS; rendering may interpolate for preview, but exported state must derive from frame number.
- Keep simulation world state separate from camera, editorial text, and post effects.
- Organize render passes: opaque world → transparent volumes/water → particles → screen-space effects → typography/UI.
- Use typed object pools for particles/debris; avoid allocation during active frames.
- Depth-sort transparent objects by camera-space distance and split large volumes into depth bands where necessary.
- Build mesh/primitive helpers that support per-face shade, normals or pseudo-lighting, fog, material state, and damage state. Plain front-facing rectangles are insufficient for hero objects.
- Use seeded variation for stable populations, but art-direct placement and silhouettes.

### 7.2 Camera implementation

Represent shots as authored rigs, not a global zoom:

```text
CameraRig {
  position, target, focalLength,
  startFrame, endFrame,
  easing,
  lookAtSubject,
  shakeBus,
  focusDistance
}
```

Camera evaluation order: authored path → target tracking → event impulse → restrained handheld/noise → projection. Event shake must be additive and decay to zero. Use focal length/FOV consistently so scale does not jump accidentally between shots.

### 7.3 VFX implementation

Each event emits a synchronized packet:

```text
EventPacket {
  frame, worldPosition, radius, direction, severity,
  lightPulse, cameraImpulse, particleBursts[],
  objectStateChanges[], audioCues[]
}
```

This prevents the common failure where sound, particles, flash, and camera shake occur on different frames. Particle systems require world-space origin, force field, wind, lifetime, size curve, opacity curve, color curve, and depth band. Screen-space particles are reserved for near-lens punctuation.

### 7.4 Audio and export implementation

- Route every source through Web Audio buses: narration, ambience, SFX, crowd, music, master.
- Connect master both to `AudioContext.destination` and `MediaStreamAudioDestinationNode`.
- Combine the canvas capture video track and destination audio track into one `MediaStream` before `MediaRecorder`.
- Automate gain/filter/pan from deterministic timeline events; do not use unsynchronized `setTimeout` calls.
- Verify one video and one audio track before export.
- Export from frame zero through the complete end card at 1080 × 1920, 30 FPS, with a high video bitrate and at least 192 kb/s requested audio where supported.
- Remux/transcode only after inspecting the output duration, frame cadence, and both tracks.

## 8. Entertainment rules

1. Establish a world worth losing before threatening it.
2. Make the premise affect more than one object class.
3. Show an understandable cause before the largest consequence.
4. Add one meaningful micro-event every 2–4 seconds.
5. Advance causal state every 8–12 seconds.
6. Alternate information, reaction, and spectacle; do not deliver sixty seconds of one mode.
7. Use people as witnesses and scale, not static decoration.
8. Preserve at least one continuity anchor through transformations.
9. Change camera scale when story scale changes.
10. Reserve the clearest composition, largest state change, and strongest synchronized event for the final hero beat.
11. Hold the payoff; do not cut away at the exact frame it becomes readable.
12. End cleanly before fatigue erases the climax.

## 9. Common failure modes and why they fail

- “Low-poly” treated as crude boxes: loses silhouette specificity and material readability.
- Empty environment plus one hero object: provides no scale or life.
- Recolored old world: makes episodes interchangeable.
- Persistent HUD copied from references: imports another creator’s identity and competes with Worldline editorial text.
- Event represented by a tint: changes appearance but not physics.
- Random particles: no source, direction, material, or consequence.
- Continuous shake: feels like a broken camera rather than impact response.
- Same camera for every premise: erases differences in scale and causality.
- Cut-heavy editing without anchors: prevents spatial memory.
- Static crowds: immediately expose the simulation as a diorama.
- Fire without light/smoke/propagation: reads as decals.
- Water without level, flow, occlusion, or interaction: reads as a transparent overlay.
- Destruction without large/medium/fine hierarchy: reads as confetti.
- Loudness used as escalation: produces fatigue and clipping instead of impact.
- Silent or missing audio export: destroys timing even if the preview sounded correct.
- Final end card replacing the hero shot: withholds the visual reward.

## 10. Production quality gates

### Reference and design gate

- [ ] Correct subfamily selected: persistent transformation, moving spectacle, or modular comparison.
- [ ] Topic-specific world and final hero frame approved.
- [ ] Full object/reaction matrix exists.
- [ ] No borrowed watermark, persistent UI, typography, or creator branding.

### World gate

- [ ] Four depth layers present in every hero shot.
- [ ] At least 4 meaningful building/terrain silhouettes and 3 prop classes where the location calls for them.
- [ ] Vehicles, people, and vegetation show structural and behavioral variation.
- [ ] Normal-world activity is visible before escalation.

### Animation gate

- [ ] Every phenomenon has a causal propagation order.
- [ ] Crowd and environment states change with the event.
- [ ] Camera placement and lens feel physical.
- [ ] Shake occurs only on motivated impulses and fully decays.
- [ ] No object teleports between continuity shots unless the time jump is explicit.

### VFX and lighting gate

- [ ] Effects occupy world space and reveal depth.
- [ ] Fire/flash/sky events affect illumination.
- [ ] Particle density, size, speed, and direction vary by depth/state.
- [ ] Hero form remains readable through the effect stack.
- [ ] Destruction has origin, force, chunk hierarchy, and aftermath.

### Editorial and pacing gate

- [ ] Hook communicates premise and place by 3 s.
- [ ] Micro-events occur every 2–4 s; causal stages every 8–12 s.
- [ ] Cuts serve reveal, explanation, reaction, or payoff.
- [ ] Final hero shot is held 1.5–3 s before closure.

### Audio gate

- [ ] Location, premise, object, human, cinematic, hero, and closure layers are considered.
- [ ] Major cues share the same event frame as light, shake, and particles.
- [ ] Narration remains intelligible.
- [ ] Integrated loudness and true peak are measured; no decoded overs/clipping.
- [ ] Export contains exactly one audible audio track.

### Technical gate

- [ ] 1080 × 1920, constant 30 FPS, full duration.
- [ ] Deterministic frame render and seeking work.
- [ ] Preview and export match.
- [ ] No missing assets, console errors, dropped end frames, or jitter.
- [ ] Final MP4/WebM is probed for duration, cadence, video track, and audio track.

## 11. Final mastery assessment

The corpus does not have one universal recipe. Its shared strength is a production logic:

**Build a recognizable, inhabited world; introduce one impossible rule; propagate it through materials, objects, people, light, atmosphere, and sound; then widen the scale while preserving an anchor.**

The highest-value references by discipline are:

- World persistence and environmental state: R01 rain.
- Atmosphere and burial: R03 sandstorm.
- Scale and camera proximity: R02 giant.
- Crowd-state propagation: R05 zombie.
- Material-by-material escalation and emissive lighting: R07 oxygen.
- Stable geography and physical-rule explanation: R06 flat Earth, R10 sky, R11 Sun.
- Multi-scale spectacle: R12 rogue planet.
- Fixed hero composition and late VFX density: R13 rings.
- Character comedy and modular subject continuity: R04 cheese, R09 planets.
- Force-system demonstration: R08 gravity.

Production readiness: ready to design a new Worldline Lab episode from this system. The next episode should begin with premise-specific world design and a shot/event/audio plan, not by modifying an old animation. This report intentionally stops before creating that episode.

## 12. Directive deliverable coverage

| Required deliverable | Where completed |
|---|---|
| 1. Full breakdown of every video | §3, R01–R13; duplicate R05-D documented in §1–2 |
| 2. Timestamped shot/scene analysis | §3 timeline blocks; measured change timestamps in §2 |
| 3. Geometry analysis | §4.2 |
| 4. Object analysis | §4.2 and §6.1 |
| 5. Environment analysis | §4.3 |
| 6. Building analysis | §4.2 and per-video production anatomy |
| 7. Vehicle analysis | §4.2, R01/R02/R05/R08/R12 |
| 8. Character analysis | §4.2, R02/R04/R05 |
| 9. Vegetation analysis | §4.2, R01/R03/R07/R10/R11 |
| 10. Color analysis | §4.5 and every timeline |
| 11. Lighting analysis | §4.5, R07/R11/R13 |
| 12. Camera analysis | §4.4 and every production-anatomy note |
| 13. Camera shake analysis | §4.4 and §7.2 |
| 14. Motion analysis | §4.6 |
| 15. VFX analysis | §4.7 |
| 16. Explosion/destruction analysis | §4.7, R02/R07/R12/R13 |
| 17. Particle analysis | §4.7 and §7.3 |
| 18. Environmental reaction analysis | §4.6 and R01/R03/R06/R07/R10/R11 |
| 19. Human reaction analysis | §4.6 and R02/R04/R05/R07/R08 |
| 20. Editing/pacing analysis | §4.8 |
| 21. Sound/SFX analysis | §5 |
| 22. Music analysis | §5; recommendations only where the soundtrack’s semantic identity was not objectively verifiable |
| 23. Audio mix analysis | §2 metrics and §5 |
| 24. Final hero-shot analysis | each R01–R13 ending plus §4.8 |
| 25. Cross-reference Animation DNA | §4 |
| 26. Worldline Animation Bible | `WORLDLINE_PRODUCTION_BIBLE.md` |
| 27. Object Library Standard | §6.1 |
| 28. VFX Event Stack Library | §6.3 |
| 29. HTML/Canvas Implementation Guide | §7 |
| 30. Production Quality Checklist | §10 |
| 31. Common Failure Modes | §9 |
| 32. Final Mastery Report | §11 |

