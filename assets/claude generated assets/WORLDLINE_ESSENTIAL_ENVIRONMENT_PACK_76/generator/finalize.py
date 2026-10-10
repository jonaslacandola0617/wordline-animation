import json, os, shutil, collections
from pack import ROOT, BUDGET
cat = json.load(open(f'{ROOT}/metadata/ASSET_CATALOG.json'))['assets']
val = json.load(open('/tmp/validation_raw.json')); sc = json.load(open('/tmp/scene_conn.json'))
by = collections.OrderedDict()
for n, a in cat.items(): by.setdefault(a['category'], []).append(a)
tot_tris = sum(a['triangles'] for a in cat.values())
rows = []; outside = []
for c, lst in by.items():
    lo, hi = BUDGET[c]
    tr = [a['triangles'] for a in lst]
    ob = [(a['name'], a['triangles']) for a in lst if a['triangles'] < lo or a['triangles'] > hi]
    outside += ob
    rows.append(f"| {c} | {len(lst)} | {min(tr)} | {int(sum(tr)/len(tr))} | {max(tr)} | {lo}-{hi} | {len(ob)} |")
below = [f"{n} ({t})" for n, t in outside if t < min(BUDGET[cat[n]['category']])]
above = [f"{n} ({t})" for n, t in outside if t > max(BUDGET[cat[n]['category']])]
wt = sorted(((v['watertight_edge_pct'], n) for n, v in val.items()))[:6]
nobj = sum(1 for c in by for f in os.listdir(f'{ROOT}/{c}') if f.endswith('.obj'))
nmtl = sum(1 for c in by for f in os.listdir(f'{ROOT}/{c}') if f.endswith('.mtl'))
scene_size = os.path.getsize(f'{ROOT}/showcase/SHOWCASE_SCENE.obj')/1e6

readme = f"""# WORLDLINE LAB - ASSET PACK 02: ESSENTIAL ENVIRONMENT PACK (76 OBJ models)

Real, generated geometry: **{nobj} OBJ + {nmtl} MTL files** (14 roads, 18 street props, 12 utilities, 14 harbor, 18 destruction), {tot_tris:,} triangles in total,
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
`previews/showcase/*.png` (5 scene renders), `showcase/SHOWCASE_SCENE.obj/.mtl` ({scene_size:.1f} MB, {sc['connection_points']} road connection points checked),
`metadata/ASSET_CATALOG.json` (dimensions, bbox, groups, materials, tri counts, connection points per model), `metadata/CONNECTION_POINTS.json`
(road/harbor grid spec + every connection point), `metadata/DAMAGE_PARTS.json` (detachable groups + pivot hints), `generator/` (source).

## Road module grid (summary - full spec in CONNECTION_POINTS.json)
12 m modules along local Z, lane 3.4 m, curb 0.15 m high x 0.25 m, slab 0.4 m. Junction arms N/E/S/W at 6 m. Right-hand traffic.
ROAD_01/07/08/09 share the same 2-lane cross-section (6.8 m carriageway); ROAD_02/14 share the 4-lane + 1.6 m median section. ROAD_13 origin = junction centre.
Sidewalks (ROAD_12) are 3 m wide; strips beside a junction start 0.65 m out (the 3x3 m corner module ROAD_13 occupies 3.65-6.65 m).

## Using destruction assets
OBJ stores no physics or pivots. Detachable parts are separate named groups; `DAMAGE_PARTS.json` lists them with bounding boxes and a pivot hint
(authored hinge points where meaningful, otherwise bbox base-centre). Several fragments in one group are separate closed solids, so they can be split by connected component.
"""
open(f'{ROOT}/README.md', 'w').write(readme)

style = """# STYLE GUIDE - Asset Pack 02

**Pack 01 (46 humans/vehicles/trees/buildings) was NOT provided, so no direct harmonisation against it was possible.** The standards below were
chosen to match the brief ("premium colourful low-poly, faceted, bevelled, strong silhouettes"). When Pack 01 is available, compare these items first:
polygon density (this pack: small props 200-1,800 tris, utilities 500-6,000, harbor 700-5,500), bevel width (0.01-0.06 m), shading (flat, per-face normals), and the palette below.

## Modelling language
* Multi-part construction: every asset is an assembly of lofted/extruded solids (beams, tubes, lathes, bevelled boxes, profile sweeps) - no single-primitive assets.
* Bevels/chamfers on curbs, barriers, boxes, caps; tapered poles; thickness on every slab, wall and plate; hollow-looking walls (planters) are built from real wall pieces.
* Facets: 8-16 sided cylinders; flat shading. No smoothing groups, no textures.
* Destruction: Voronoi fracture plates with open crack gaps, layered skin/core cross-sections, exposed rebar, jagged profile extrusions, tilted/offset pieces, per-part groups.

## Material palette (all defined in each MTL that uses it)
Asphalt: asphalt_warm (.30,.285,.275), asphalt_cool (.225,.255,.30) | Concrete: concrete_pale, concrete_weathered, broken_concrete, concrete_core |
Metals: metal_painted_grey, galvanized_steel, brushed_metal, rust_metal, paint_navy/green/blue | Safety: safety_yellow, safety_orange, traffic_red |
Wood: timber_warm, wood_weathered | Rubber: rubber_dark | Glass: glass_tinted (d .45) | Emissive: signal_red/amber/green, lamp_emissive |
Markings: marking_white, marking_yellow, tactile_yellow | Masonry: brick_red, mortar, plaster_cream, roof_tile, dusty_stone | Others: soil, ad_panel, sign_*, container_* , insulator_*, rebar, cable_black.
(grass_muted, ground_tan, sea_deep are used only by the showcase scene.)
"""
open(f'{ROOT}/STYLE_GUIDE.md', 'w').write(style)

vr = f"""# VALIDATION REPORT

All numbers below were produced by `generator/pack.py` (independent OBJ re-parse of the files on disk) and `generator/scene.py`. Items not run are listed under *Not done*.

## Counts
Roads 14 | Street props 18 | Utilities 12 | Harbor 14 | Destruction 18 | **Total OBJ files {nobj}** | MTL files {nmtl} | total triangles {tot_tris:,}.
No empty files; no placeholder or duplicate-with-recolour assets (each model has its own construction function).

## Automated checks (all 76 files) - PASSED
* Every `f` has 3 vertices; all vertex and normal indices in range; 0 degenerate triangles; all vertices finite.
* Every `vn` is unit length and agrees (>0.99 dot) with the winding-derived face normal on every face (outward winding guaranteed by a signed-volume check at construction).
* `mtllib` file exists next to each OBJ and every `usemtl` is defined in it (relative references, work after extraction).
* Catalog (ASSET_CATALOG.json) is generated from the files on disk, so it matches them.

## Geometry quality metrics (informational)
Edge-sharing metric = % of edges used by exactly two triangles inside a group. Lowest: {', '.join(f'{n} {p}%' for p, n in wt)}; all others are higher.
Models are unions of closed solids that often overlap/touch (e.g. a post inserted into a base), so "exactly two" is not 100% everywhere - they are not single manifold meshes.

## Triangle budgets vs the brief's suggested ranges
| Category | Models | Min | Mean | Max | Suggested range | Outside range |
|---|---:|---:|---:|---:|---|---:|
{chr(10).join(rows)}

Below range (simple but fully modelled objects, e.g. a bench or cone): {', '.join(below) or 'none'}.
Above range: {', '.join(above) or 'none'}. The brief calls these guidelines, not maximums.

## Modular connection check
Showcase road network: {sc['connection_points']} road connection points (ROAD_01/04/05/09) tested for coincident position (<1 cm), opposed direction and equal carriageway width:
**{sc['matched']} matched, {len(sc['open_ends'])} unmatched** - the unmatched ones are the intentional outer ends of the network ({', '.join(f"{o[0]}.{o[1]}@{o[2]}" for o in sc['open_ends'])}).
Visual curb/height continuity is shown in `previews/showcase/05_modular_road_network_test.png`. ROAD_06 (24 m), ROAD_07 (curve), ROAD_08 (slope), ROAD_10/11 (highway) and ROAD_12/13/14 are
documented with connection points but were only checked by the visual assembly, not by the numeric test above (ROAD_14 shares ROAD_02's end profile by construction).

## Visual review
Rendered previews of every model (960x720, three-quarter or angled top-down) and a 76-model contact sheet. I looked at test sheets of every category and the final contact sheet while building and fixed
problems found (e.g. renderer depth/clipping bugs, overlapping icon geometry in PROP_02, flat-black roof membrane in DESTROY_07). This was a developer's check of software renders, **not** an art-director sign-off.
Previews come from a custom z-buffer rasteriser (flat shading + approximate shadow), so they approximate - not equal - a Three.js/Blender render.

## Showcase scene
`showcase/SHOWCASE_SCENE.obj` ({scene_size:.1f} MB): ROAD_01/04/05/09 network, sidewalks, corner modules, signals, lights, furniture, poles and electrical equipment, harbor structures, containers, quay, piers, port gantry crane and the
separate damaged-area (all 18 destruction assets). Terrain, water, lawns and the quay slab are scene-only helpers (not part of the 76). No placeholder buildings/humans/cars were added because Pack 01 was not available.
Renders: street level, elevated, harbor panorama, destruction close-up, and a modular-network test view.

## Not done / limitations (honest list)
* No import test in Blender, Three.js or any DCC tool (none available offline) - only the independent parser above.
* Pack 01 not supplied: style harmonisation could not be verified (see STYLE_GUIDE.md).
* No textures (flat colours + emissive/transparent materials only). OBJ cannot store pivots/physics; pivots are metadata hints.
* Rooftop units (UTILITY_07/08/09) are free-standing assets; in the scene they sit on a plinth, not on buildings.
* HARBOR_14 container and the held container in the scene are HARBOR_10 instances; the crane model itself carries the spreader only.
* The scene is a 226k-triangle composition intended for rendering/inspection; it is not optimised/instanced for the browser.
"""
open(f'{ROOT}/VALIDATION_REPORT.md', 'w').write(vr)

os.makedirs(f'{ROOT}/generator', exist_ok=True)
for f in ('lib.py', 'roads.py', 'props.py', 'utilities.py', 'harbor.py', 'destroy.py', 'render.py', 'pack.py', 'scene.py', 'finalize.py'): shutil.copy(f, f'{ROOT}/generator/{f}')
open(f'{ROOT}/generator/README.txt', 'w').write("python3 pack.py   # builds all 76 models, validates, writes metadata + previews (needs numpy, Pillow)\npython3 scene.py  # showcase scene + 5 renders\npython3 finalize.py # docs\nEdit ROOT in pack.py to change the output folder.\n")
print('docs ok', nobj, nmtl, tot_tris, below, above)
