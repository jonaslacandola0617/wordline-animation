# VALIDATION REPORT

All numbers below were produced by `generator/pack.py` (independent OBJ re-parse of the files on disk) and `generator/scene.py`. Items not run are listed under *Not done*.

## Counts
Roads 14 | Street props 18 | Utilities 12 | Harbor 14 | Destruction 18 | **Total OBJ files 76** | MTL files 76 | total triangles 103,614.
No empty files; no placeholder or duplicate-with-recolour assets (each model has its own construction function).

## Automated checks (all 76 files) - PASSED
* Every `f` has 3 vertices; all vertex and normal indices in range; 0 degenerate triangles; all vertices finite.
* Every `vn` is unit length and agrees (>0.99 dot) with the winding-derived face normal on every face (outward winding guaranteed by a signed-volume check at construction).
* `mtllib` file exists next to each OBJ and every `usemtl` is defined in it (relative references, work after extraction).
* Catalog (ASSET_CATALOG.json) is generated from the files on disk, so it matches them.

## Geometry quality metrics (informational)
Edge-sharing metric = % of edges used by exactly two triangles inside a group. Lowest: ROAD_08 92.0%, ROAD_01 92.3%, PROP_07 94.7%, PROP_12 95.7%, PROP_16 95.7%, UTILITY_07 96.1%; all others are higher.
Models are unions of closed solids that often overlap/touch (e.g. a post inserted into a base), so "exactly two" is not 100% everywhere - they are not single manifold meshes.

## Triangle budgets vs the brief's suggested ranges
| Category | Models | Min | Mean | Max | Suggested range | Outside range |
|---|---:|---:|---:|---:|---|---:|
| roads | 14 | 308 | 1048 | 2908 | 200-4000 | 0 |
| street_props | 18 | 208 | 691 | 2696 | 150-2500 | 1 |
| utilities | 12 | 620 | 2261 | 6124 | 500-4000 | 2 |
| harbor | 14 | 732 | 2090 | 5484 | 1000-10000 | 4 |
| destruction | 18 | 380 | 1116 | 3568 | 400-5000 | 1 |

Below range (simple but fully modelled objects, e.g. a bench or cone): HARBOR_04 (992), HARBOR_08 (768), HARBOR_09 (732), HARBOR_12 (860), DESTROY_01 (380).
Above range: PROP_17 (2696), UTILITY_04 (6124), UTILITY_06 (5448). The brief calls these guidelines, not maximums.

## Modular connection check
Showcase road network: 29 road connection points (ROAD_01/04/05/09) tested for coincident position (<1 cm), opposed direction and equal carriageway width:
**24 matched, 5 unmatched** - the unmatched ones are the intentional outer ends of the network (ROAD_01.end_B@[0.0, 0.0, 30.0], ROAD_01.end_A@[0.0, 0.0, -30.0], ROAD_01.end_A@[-30.0, 0.0, -0.0], ROAD_09.end_B@[36.0, 0.0, 18.0], ROAD_09.end_A@[36.0, 0.0, -30.0]).
Visual curb/height continuity is shown in `previews/showcase/05_modular_road_network_test.png`. ROAD_06 (24 m), ROAD_07 (curve), ROAD_08 (slope), ROAD_10/11 (highway) and ROAD_12/13/14 are
documented with connection points but were only checked by the visual assembly, not by the numeric test above (ROAD_14 shares ROAD_02's end profile by construction).

## Visual review
Rendered previews of every model (960x720, three-quarter or angled top-down) and a 76-model contact sheet. I looked at test sheets of every category and the final contact sheet while building and fixed
problems found (e.g. renderer depth/clipping bugs, overlapping icon geometry in PROP_02, flat-black roof membrane in DESTROY_07). This was a developer's check of software renders, **not** an art-director sign-off.
Previews come from a custom z-buffer rasteriser (flat shading + approximate shadow), so they approximate - not equal - a Three.js/Blender render.

## Showcase scene
`showcase/SHOWCASE_SCENE.obj` (11.6 MB): ROAD_01/04/05/09 network, sidewalks, corner modules, signals, lights, furniture, poles and electrical equipment, harbor structures, containers, quay, piers, port gantry crane and the
separate damaged-area (all 18 destruction assets). Terrain, water, lawns and the quay slab are scene-only helpers (not part of the 76). No placeholder buildings/humans/cars were added because Pack 01 was not available.
Renders: street level, elevated, harbor panorama, destruction close-up, and a modular-network test view.

## Not done / limitations (honest list)
* No import test in Blender, Three.js or any DCC tool (none available offline) - only the independent parser above.
* Pack 01 not supplied: style harmonisation could not be verified (see STYLE_GUIDE.md).
* No textures (flat colours + emissive/transparent materials only). OBJ cannot store pivots/physics; pivots are metadata hints.
* Rooftop units (UTILITY_07/08/09) are free-standing assets; in the scene they sit on a plinth, not on buildings.
* HARBOR_14 container and the held container in the scene are HARBOR_10 instances; the crane model itself carries the spreader only.
* The scene is a 226k-triangle composition intended for rendering/inspection; it is not optimised/instanced for the browser.
