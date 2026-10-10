# Worldline Lab — Internal Production Bible

Status: reference analysis complete; permanent production standard  
Scope: `references/current` defines identity and workflow; the 14 supplied files in `references/samples` (13 unique videos) define animation, camera, density, escalation, and spectacle.  
Last updated: 2026-10-09

Evidence base: [WORLDLINE_REFERENCE_MASTERING_REPORT.md](WORLDLINE_REFERENCE_MASTERING_REPORT.md). The mastering report contains the full timeline, video-by-video, audio-envelope, event-stack, object-library, implementation, and production-readiness analysis. This Bible is the compact standard used during production.

## 1. Non-negotiable reference split

### Preserve from `references/current`

- Worldline Lab typography, palette, editorial restraint, captions, chapter language, end card, player controls, and browser export workflow.
- The clean hierarchy: the simulated world first; temporary editorial information second.
- The short in-world opening. No detached logo intro.

### Match or exceed from `references/samples`

- Actual low-poly 3D depth, mesh variety, environment density, physical camera placement, atmospheric scale, staged escalation, populated worlds, reactive objects, particles, destruction, and final spectacle.
- The samples are technique references, not branding references. Do not import their watermarks, logos, typography, persistent metric UI, or end cards.

### Explicitly do not preserve

- The sparse, repeatedly reused generic street found in several current exports.
- Flat placeholder geometry, empty roads, static crowds, static camera zooms, or a disaster represented only by a color grade.
- Video-only export. The next exporter must include mixed audio.

## 2. Reference inventory and timeline review

All 17 MP4 files in the reference workspace were decoded across their full timelines: three current identity references and 14 supplied animation samples. The two zombie files are byte-identical, yielding 16 unique videos overall and 13 unique animation samples. Each file was sampled at 0%, 5%, 10%, 20%, 30%, 40%, 50%, 60%, 70%, 80%, 90%, and the ending, plus eight high-change moments detected at half-second intervals. All are vertical 576 × 1024 proxy exports at approximately 30 FPS.

### Current identity references

| File | Duration | Content | Identity lesson | Animation limitation |
|---|---:|---|---|---|
| `current/Download.mp4` | 65.0 s | Every volcano erupts | Best current use of chapter cards, restrained captions, palette shift, volcanic silhouette, ash, and the established end card | Reuses one street for most of the runtime; cars and people mostly function as dressing; plume and lighting change more than the world does |
| `current/Download (1).mp4` | 61.9 s | Earth has no shadows | Demonstrates clean information overlays, comparison language, lower captions, and the end-card system | Sparse generic street, crude figures/vehicles/trees, long washed-out passages, limited environmental reaction, weak spatial depth |
| `current/Download (2).mp4` | 59.9 s | An ocean above Earth | Shows cool palette adaptation, temporary chapter text, translucent water/light treatment, and a distinct underwater beat | Again starts from the same generic street; much of the event is conveyed as large translucent surfaces and tint rather than convincing water volume or world interaction |

### Current source projects

| File | Topic | Reusable implementation |
|---|---|---|
| `worldline-lab-moon-doubling-final.html` | Moon doubles | Strongest canonical brand implementation: title, six chapter cards, captions, callouts, end card, player, deterministic time hooks, 12 Mbps export |
| `worldline-lab-no-shadows.html` | No shadows | Canonical lower captions, transient comparison labels, player/export shell, scene-time API |
| `worldline-lab-random-doors.html` | Random doors | Canonical chapter/end-card shell applied to a more scene-specific concept; reusable projection and label helpers |

### Animation benchmark references

| File | Duration | Content | Techniques to carry forward |
|---|---:|---|---|
| `samples/Download.mp4` | 58.7 s | Gravity turns off for ten seconds | Human-scale street hook; dense façades, traffic, people, fountain, and trees; water/debris rising; low/high viewpoints; objects crashing back; macro Earth escalation; small visual coda |
| `samples/Download (1).mp4` | 60.0 s | Sound on every planet | Strong subject continuity across distinct environments; fast, readable world changes; simple silhouette stays legible against different planets. Use the transition logic, not the sparse staging or branding |
| `samples/Download (2).mp4` | 65.0 s | The sky disappears | Fixed-location transformation done well: foreground railing, village, lake, distant forest and mountains; sky loss, falling aircraft, frost, snow, color drain, time jumps, and a final ice-blast vignette |
| `samples/Download (3).mp4` | 62.0 s | The Sun disappears | Clear day-to-night transition; streetlights create scale; falling temperature is visible through frost, snow, frozen water, and an enclosing ice texture; the same landscape becomes a different world |
| `samples/Download (4).mp4` | 77.0 s | Rogue planet hits Earth | Highest-value camera/world benchmark: coastal city, park, cruise ship, varied towers, aerial camera moves, approaching celestial object, city pull-apart, global view, impact flash, shockfront, debris, and ash-filled aftermath |
| `samples/Download (5).mp4` | 80.0 s | Earth has Saturn-like rings | Highest-value escalation benchmark: foreground balcony/planters, dense lit skyline, enormous ring scale, sunset-to-night lighting, growing meteor density, building strikes, citywide fire, smoke, and a readable final inferno |
| `samples/f47772957016a648e86da12965f4a600.mp4` | 96.0 s | Rain for 1,000 years | Highest-value persistent-state benchmark: one intersection survives rain, drainage failure, flooding, boats, abandonment, recession, and forest succession while remaining spatially recognizable |
| `samples/4a7422e4ac644fce42faf420c6ee892b.mp4` | 69.0 s | 60-meter giant | Highest-value mass/proximity benchmark: avenue canyon, people/cars/helicopters as scale references, distance progression, low angles, foot/air displacement, collapse, debris, and dust |
| `samples/150e1171fbadcbdcd91bdb17464dcf13.mp4` | 94.0 s | Sandstorm for 1,000 years | Highest-value atmospheric-depth benchmark: storm wall, wind-reactive palms/props, depth-banded particles, visibility loss, sand accumulation, burial, all-clear contrast, and excavation coda |
| `samples/5918a3830da3c011942276f0aeb900af.mp4` | 65.0 s | Everyone turns into cheese | Character-comedy benchmark: articulated simplified figures, pose-readable interaction, beach props, transformation continuity, consequence gags, and a steady rather than catastrophic pacing arc |
| `samples/7066782ad2f41d149065d8c936812b9e.mp4` | 64.0 s | Zombie outbreak | Crowd-state benchmark: normal city activity, first bite, exponential population inversion, traffic disruption, smoke/fire, aerial propagation views, street chase, and a dark final crowd |
| `samples/cb3b02602de8ba4faab845f698ba9c72.mp4` | 65.0 s | Flat Earth | Physical-rule benchmark: persistent balcony geography, moving water/air/objects, macro disc-edge explanation, gravity-direction change, rising edge, and terrain-scale final transformation |
| `samples/d7202baa78a3b6ad72f8e36168113f09.mp4` | 80.1 s | Oxygen rises 1% per second | Best material-by-material escalation benchmark: populated pool party, ignition-source logic, vegetation/structure/fire spread, pool refuge, emissive lighting, embers, and citywide white-hot inferno |
| `samples/7066782ad2f41d149065d8c936812b9e(1).mp4` | 64.0 s | Exact duplicate of zombie reference | Do not count as independent style evidence; SHA-256 matches the file above |

## 3. Canonical Worldline identity

### Typography

- Playfair Display, weight 600, including italic, for scenario questions, chapter phrases, editorial statements, and the final question.
- Manrope 600/700/800 for captions, metadata, dates, technical labels, callouts, controls, and brand lockups.
- Typical source sizes on a 1080 × 1920 canvas:
  - Opening question: 72–76 px Playfair.
  - Chapter phrase: 92 px Playfair.
  - Chapter number: 30 px Manrope 800.
  - Chapter date: 26 px Manrope 700.
  - Chapter descriptor: 23 px Manrope 700.
  - Captions: 52–54 px Manrope 800.
  - End-card question: 100 px Playfair.

### Palette

| Token | Value | Use |
|---|---|---|
| Ink | `#0B0D0C` | Backgrounds, caption glass, gradients, end card |
| Ivory | `#F2EFE8` | Primary editorial text |
| Soft white | `#FAF9F6` | High-priority question/caption text |
| Antique gold | `#C4A46B` | Rules, selected words, chapter numbers, compact accents |
| Muted sage | `#7C897B` | Secondary metadata and quiet labels |
| Graphite | `#383C3A` | Controls, borders, neutral UI surfaces |

Gold remains an accent. The simulated world may use topic-specific colors; the editorial layer keeps this palette.

### Opening question

- Begins over the world at about 0.25–0.30 s.
- Fades away around 2.6–3.2 s.
- Uses a restrained dark vertical gradient for legibility, not a full title card.
- The first anomaly should already be visually underway by the time the text clears.

### Chapter cards

- Temporary, normally about 3.3–3.4 seconds.
- Structure: number → thin gold rule → date label → large Playfair phrase → small uppercase descriptor.
- Typical placement starts near x = 84, with content centered in the upper 200–380 px region.
- Source projects introduce chapters around 5 s and then near ten-second boundaries.
- Use chapter cards to mark genuine causal stages. Do not use them as a permanent HUD.

### Captions

- Lower-middle placement, visually around y = 1436 on the 1920 px canvas.
- Maximum working line width is about 860 px with a 72 px line height.
- Manrope ExtraBold, ivory/soft white, with selected phrases in antique gold.
- Backing: ink at roughly 34% opacity, about 30 px horizontal padding, 18 px corner radius, subtle dark shadow.
- Fade/slide in over about 0.25–0.30 s; fade out at the end of each phrase.
- Never use karaoke animation, per-word bouncing, rainbow emphasis, or giant full-width subtitle slabs.

### End card

- Keep the established ink field and thin vertical antique-gold rule.
- Brand and status use compact uppercase Manrope: `WORLDLINE LAB` / `SIMULATION COMPLETE`.
- Final question remains the three-line Playfair lockup: `What should / we simulate / next?`, with italic `next?`.
- Small thought-experiment metadata sits below.
- Current source starts the transition at about 57.7 s in a 60 s project. For longer episodes, reserve approximately the last 2–3 seconds.
- The final hero image must land before this card; the card is closure, not the payoff itself.

## 4. Player and export contract

- Physical canvas: 1080 × 1920. CSS may scale only the preview.
- Nominal frame rate: 30 FPS.
- Controls: Replay, Pause/Play, timeline slider, elapsed time, Export WebM.
- Controls sit in a compact bottom overlay and auto-hide after about 2.5 seconds of inactivity.
- Keyboard conventions in current source: Space toggles playback; `r` replays.
- Keep deterministic inspection hooks such as `setTime(seconds)` and `renderFrame(frameNumber)`.
- Export restarts at frame zero, records the entire runtime, and downloads only after completion.
- Preferred codec order: VP9, then VP8, then generic WebM.
- Preserve the current video target of approximately 12 Mbps or higher.

### Required exporter correction

The three inspected HTML projects call `canvas.captureStream(30)` directly and construct a video-only `MediaRecorder`. They do not create a `MediaStreamAudioDestinationNode`, do not add an audio track, and do not set an audio bitrate. The next production must:

1. Route all generated and loaded audio through one Web Audio master bus.
2. Connect that bus both to the speakers and a `MediaStreamAudioDestinationNode`.
3. Combine the canvas video track with the destination audio track before constructing `MediaRecorder`.
4. Request at least 192 kbps audio when supported.
5. Assert one video track and one audio track before recording.
6. Verify the downloaded WebM contains both tracks.

## 5. Animation target extracted from the samples

### Geometry

- Low-poly means simplified faceted meshes with deliberate silhouettes, not a voxel world.
- Buildings need multiple widths, depths, heights, façades, window rhythms, roof equipment, ledges, setbacks, and color families.
- Vehicles need identifiable classes and readable components: body, hood, cabin, glazing, wheels, and front/back distinction.
- People need heads, torsos, arms, and legs with pose-readable actions. Vary clothing, height, grouping, and movement speed.
- Trees require trunk/canopy construction and at least several silhouettes. Avoid one cone-on-stick model repeated uniformly.
- Hero natural effects—water, rock, ice, ash, clouds, debris, fire, shockfronts—may use stronger faceting and exaggeration.

### Density and depth

Every important shot should contain:

- Foreground: railing, planter, sign, tree, signal, vehicle edge, furniture, spray, or debris.
- Midground: people, moving vehicles, the active street/plaza/shoreline, nearby structures.
- Background: varied skyline, terrain, harbor, mountains, ocean, or distant districts.
- Sky/hero layer: the impossible object or atmospheric consequence.

The successful samples establish scale with repeated ordinary objects before revealing the impossible one. A world should look inhabited before it is threatened.

### Camera language

- Default to a physically believable camera: eye level, street corner, sidewalk, balcony, rooftop, harbor edge, plaza, or aerial overlook.
- Use slow push/pull, controlled pan/tilt, restrained drift, or tracking. Camera motion should reveal spatial relationships.
- Change viewpoint when the scale of the story changes. The gravity and rogue-planet samples move from human scale to city scale to planetary scale.
- During impacts, use an envelope: rapid displacement/rotation attack, short high-frequency vibration, and visible decay. Do not apply endless random jitter.

### Environmental transformation

The strongest references keep a recognizable location while progressively changing many systems together:

- Light and sky color.
- Weather and atmosphere.
- Water, vegetation, loose objects, vehicles, and people.
- Window lights, streetlights, signage, and traffic behavior.
- Particle density and visibility range.
- Camera response and audio intensity.

The event must propagate through the world. A tint or a single hero object is not enough.

## 6. Pacing and escalation model

### Recommended structure for a 60–96 second episode

| Time | Story function | Required visual behavior |
|---:|---|---|
| 0–5% | Hook in-world | Scenario question over a strong normal-world composition; first subtle anomaly |
| 5–17% | Normal → wrong | Ordinary motion establishes scale; one or two micro-events signal change |
| 17–32% | Physical change | Hero phenomenon becomes undeniable; temporary metric or chapter card may appear |
| 32–48% | Public reaction | People stop, point, film, group, flee; traffic and loose objects respond |
| 48–67% | Environmental consequence | Lighting, weather, infrastructure, water, or structures change together |
| 67–84% | Large-scale transformation | New viewpoint or scale jump; denser VFX and stronger sound |
| 84–96% | Final hero payoff | Largest, clearest, thumbnail-worthy consequence with strong scale references |
| Final 2–4 s | Worldline closure | Established end card; mix falls back enough for clean closure |

### Micro-event cadence

Add a meaningful change every 2–4 seconds. Examples: bird departure, a stopped pedestrian, pointing, phone filming, brake lights, a fallen sign, flickering windows, water displacement, first ash, glass vibration, siren lights, a cracking surface, or a passing foreground object.

### Major-stage cadence

Advance the causal state every 8–12 seconds. Avoid merely increasing particle count while the world and camera remain unchanged.

## 7. VFX integration rules

- Synchronize large events across camera, particles, lighting, foreground reaction, and sound.
- Use flashes briefly and preserve detail; do not white-out the payoff for long stretches.
- Use dust/ash/smoke volumes to reveal depth through parallax and occlusion.
- Build particle fields in world space with size, speed, turbulence, and density changing by stage.
- Heat, water, gravity, and lensing distortions need a localized physical cause.
- Fire requires a light contribution on nearby geometry, smoke above it, and ember/debris movement consistent with wind.
- Destruction pieces need origin, momentum, gravity, collision intent, and scale variation—not arbitrary triangles.
- Keep chromatic fringe, bloom, vignette shifts, and motion blur subtle enough that the low-poly forms remain readable.

## 8. Audio findings and production target

All 17 MP4 files contain stereo AAC audio at 44.1 kHz. Current exports use approximately 127–128 kbps; sample exports vary between roughly 31–32 kbps and 128 kbps. The most effective benchmark envelopes build over the middle and late sections, then drop for the ending. Rogue planet has the cleanest controlled catastrophe arc; rain and sandstorm use strong late reveal transitions; giant concentrates large rises around collapse; cheese intentionally stays dynamically steady. The oxygen reference is dramatically loud and shows decoded overs, while Sun/rings contain long silent tails. Copy their dramatic shape, not unsafe gain or accidental silence.

Decoded reference audio also shows possible overs/clipping in multiple files, including all three current MP4s. Do not copy that defect.

### Required mix architecture

- Base ambience: location-specific traffic, wind, water, birds, room tone, or distant crowd.
- Causal layers: engines, footsteps, horns, alarms, sirens, structural stress, water, impacts, ash, rock, or fire.
- Human scale: varied crowd reactions and movement, used when people are visible.
- Cinematic layer: restrained drone/bed, risers, reverse sweeps, sub impacts, and transition sweeteners.
- Hero impact: tightly synchronized transient, low-frequency weight, environment tail, and a short reduction in competing layers.
- End card: intentional downshift or atmospheric tail, not an abrupt accidental silence.

Target approximately -14 to -12 LUFS integrated, true peaks below -1 dBTP, no clipping, and enough early headroom for the final event to feel larger. Use measured LUFS/true-peak tools on final exports; RMS figures in the mastering report describe reference envelopes and are not interchangeable with LUFS.

## 9. New-episode world design gate

Before implementation, write and approve internally:

- Location type and why it makes the premise legible.
- Time of day and weather.
- Three or more camera locations with physical placement.
- Building language and skyline silhouette.
- Foreground dressing.
- Vehicle classes and movement paths.
- Crowd composition and reaction-state transitions.
- Vegetation and street/terrain props.
- Hero phenomenon and its scale references.
- Stage-by-stage environmental reactions.
- VFX stack.
- Ambience, SFX, human audio, music, and final mix arc.
- Deliberate final hero shot.

Reject the plan if it can be described as a previous scene with a different hero object.

## 10. Engineering boundary: reuse systems, not productions

### Reuse

- Projection, camera transforms, mesh primitives, depth sorting, face shading, fog, lighting, particles, caption/chapter/end-card renderers, audio mixer, deterministic timeline, player controls, and export pipeline.

### Build new per episode

- Scene layout, structures, skyline, road/terrain network, façade families, vehicles, characters, vegetation variants, props, camera positions, environmental animation, destruction sequence, VFX staging, and sound palette.

A deterministic episode seed may stabilize a production, but randomness is not art direction. Structural families and composition must be intentionally designed for the topic.

## 11. Quality gate

An episode is not complete until all are true:

### Identity

- Playfair/Manrope hierarchy and six-color editorial palette are preserved.
- Chapter cards and captions are temporary and restrained.
- No unnecessary persistent HUD.
- Established end card is intact.

### World

- The environment is topic-specific and visibly new.
- Foreground, midground, background, and hero/sky layers are present.
- Buildings, vehicles, people, vegetation, and props have structural—not merely color—variation.
- Ordinary activity establishes scale before the event.

### Story and motion

- A micro-event occurs every 2–4 seconds.
- A major causal stage changes every 8–12 seconds.
- Human and environmental reactions match the event.
- Camera positions feel physically located.
- Final hero shot is instantly readable and thumbnail-worthy.

### VFX and audio

- Major events synchronize camera, light, particles, world reaction, and sound.
- Effects have physical causes and do not obscure the scene.
- Ambience, scenario SFX, human reaction, and cinematic layers are present where appropriate.
- No clipping; final mix has dynamic range.

### Export

- 1080 × 1920, approximately 30 FPS, full runtime, high bitrate.
- Replay, Pause/Play, scrub, time, and Export WebM work.
- Export starts from zero and stops only after the episode finishes.
- Output contains exactly one video track and one audio track.
- No console errors.

## 12. Production conclusion

Worldline Lab should not look like its current animations with more particles. The correct synthesis is:

**Worldline editorial identity + sample-level 3D worlds and camera language + stronger synchronized VFX, human reaction, escalation, and sound.**

The brand remains consistent. Every world, composition, and catastrophe must be newly produced for its topic.
