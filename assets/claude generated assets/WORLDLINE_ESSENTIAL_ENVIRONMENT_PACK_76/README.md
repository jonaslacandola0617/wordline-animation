# WORLDLINE LAB - ASSET PACK 02: ESSENTIAL ENVIRONMENT PACK (76 OBJ models)

Real, generated geometry: **76 OBJ + 76 MTL files** (14 roads, 18 street props, 12 utilities, 14 harbor, 18 destruction), 103,614 triangles in total,
plus metadata, previews, a validation report and an assembled showcase scene. Everything was produced by the Python generator in `generator/`
(deterministic - re-running `python3 pack.py` rebuilds identical files; no external assets, no network).

## Conventions
* Units: **metres**. Up axis **+Y**, right-handed, forward **+Z**. Three.js: load with `OBJLoader` + `MTLLoader`, no axis conversion needed.
* Flat (faceted) shading: one `vn` per face. Triangles only. Each OBJ has `g <MODEL>__<part>` groups and `usemtl` per group; MTL files sit next to the OBJ.
* Origins: roads = module centre at road surface (connection points at z=+/-6); props/utilities = ground-contact point; harbor = logical placement point
  (pier/dock: deck-level centre; floating objects/buoy: waterline y=0); destruction = ground-contact centre of the assembly.
* Materials: shared palette (see STYLE_GUIDE.md). Emissive lens/lamp/signal materials carry `Ke`; glass uses `d 0.45`.
* Road markings, wear tracks, seams, tactile domes and curb chamfers are **real thin geometry** (0.01-0.02 m), not textures. No texture files are used.

## Folder layout
`roads/ street_props/ utilities/ harbor/ destruction/` (OBJ+MTL pairs), `previews/<category>/*.png` (960x720), `previews/contact_sheet.png`,
`previews/showcase/*.png` (5 scene renders), `showcase/SHOWCASE_SCENE.obj/.mtl` (11.6 MB, 29 road connection points checked),
`metadata/ASSET_CATALOG.json` (dimensions, bbox, groups, materials, tri counts, connection points per model), `metadata/CONNECTION_POINTS.json`
(road/harbor grid spec + every connection point), `metadata/DAMAGE_PARTS.json` (detachable groups + pivot hints), `generator/` (source).

## Road module grid (summary - full spec in CONNECTION_POINTS.json)
12 m modules along local Z, lane 3.4 m, curb 0.15 m high x 0.25 m, slab 0.4 m. Junction arms N/E/S/W at 6 m. Right-hand traffic.
ROAD_01/07/08/09 share the same 2-lane cross-section (6.8 m carriageway); ROAD_02/14 share the 4-lane + 1.6 m median section. ROAD_13 origin = junction centre.
Sidewalks (ROAD_12) are 3 m wide; strips beside a junction start 0.65 m out (the 3x3 m corner module ROAD_13 occupies 3.65-6.65 m).

## Using destruction assets
OBJ stores no physics or pivots. Detachable parts are separate named groups; `DAMAGE_PARTS.json` lists them with bounding boxes and a pivot hint
(authored hinge points where meaningful, otherwise bbox base-centre). Several fragments in one group are separate closed solids, so they can be split by connected component.
