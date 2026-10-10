# Moon Fall Rescue — Art-Direction Gate Status

Date: 2026-10-09  
Status: mandatory asset-quality gate ready for visual review; full timeline rebuild paused

## Confirmed failure evidence

The existing `worldline-lab_moon-fall.webm` was inspected at 00:02, 00:08, 00:15, 00:25, 00:35, 00:46, 00:57, and 01:04.

- 00:02: primitive street canyon, largely blank building faces, tiny unreadable people/vehicles, Moon mostly hidden by a tower.
- 00:08: blank rooftop/façade dominates; Moon is absent from its own reveal.
- 00:15: harbor is readable only as simple boxes and strips; boats, docks, and waterfront buildings lack modeled character.
- 00:25: giant simple prisms surround tiny stick figures and block vehicles.
- 00:35: tsunami is a stack of horizontal blue bands and round foam dots; no visible impact choreography.
- 00:46: Moon breakup is drawn crack lines; flooding is a flat overlay; destruction lacks structural source.
- 00:57: finale uses black building silhouettes, random debris, stick figures, and a cropped Moon; it does not create a coherent hero composition.
- 01:04: Worldline end card is visually intact and should be preserved.

The master is 1080 × 1920 VP9 with stereo Opus and approximately 65 seconds long, but only 809 distinct decoded video frames were present. Effective cadence is approximately 12.45 FPS, confirming the reported performance failure.

Audit screenshots are stored in `episodes/moon-fall/qa/rescue-audit`.

## New mandatory asset gate

`episodes/moon-fall/moon-fall-asset-quality-gate.html` contains five selectable tests:

1. Modeled human family: faceted head/hair, neck, tapered torso, shoulders, articulated upper/lower arms, hands, pelvis, articulated upper/lower legs, and modeled shoes in neutral, pointing, and running poses.
2. Vehicle family: structurally distinct sedan, bus, and emergency vehicle with shaped bodies, cabins, glazing, separate polygonal wheels, lights, and an emergency light bar.
3. Building family: office, residential, and commercial designs with different silhouettes, setbacks/roof structures, dimensional façade bands, balconies/railings, storefront glazing, awning/trim, and rooftop equipment.
4. Populated environment: waterfront street with architecture, sidewalks, lanes, crosswalk markings, streetlights, polygonal trees, varied pedestrians, sedans, bus, and emergency vehicle.
5. Cinematic frame: the populated world, articulated foreground activity, layered architecture, atmospheric depth, and a clearly framed detailed Moon without disaster effects masking the assets.

The test page uses a world-space perspective renderer with face sorting and directional faceted lighting. It exposes `renderGate(0..4)` and `gateDiagnostics` for deterministic review.

## In-progress episode source

The main episode remains browser-openable and syntax-valid. Early architecture scaffolding has begun: greater silhouette variety, modeled floor/roof structures, balcony slabs, storefront bases, rooftop equipment, and larger population/vehicle pools. These changes are not declared visually accepted and are not the final rescue.

The complete timeline, tsunami, structural destruction, lunar breakup, finale, audio redesign, and fresh export are intentionally not marked complete because the latest directive requires the asset foundation to pass first.

## Gate required before continuation

Review all five views in the asset-quality page at normal and mobile size. Continue the episode rebuild only if:

- paused humans read as designed low-poly people rather than sticks/capsules;
- all three vehicle classes are recognizable without relying on color;
- the three building families have genuinely different silhouettes and dimensional façades;
- the street reads as a coherent inhabited world rather than a blockout;
- the cinematic frame approaches the supplied reference family without depending on particles, darkness, text, or camera shake.

