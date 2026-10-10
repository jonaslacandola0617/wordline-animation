# WORLDLINE LAB - 46-model low-poly asset pack

46 OBJ models (10 humans, 6 cars, 10 trees, 20 buildings), each with its own `.mtl`. Total 157,436 triangles.

## Conventions
- Y-up, right-handed. **Forward = +Z** (humans face +Z, cars drive toward +Z, building fronts/entrances face +Z).
- Units = metres. Origin sits on the ground (min Y = 0), roughly centred on the footprint.
- Faceted shading: one normal per triangle (`vn`), outward-facing winding verified per part.
- `.mtl` files sit next to their `.obj` (relative `mtllib`). Glass uses `d < 1` (set `transparent = true` in Three.js, as the viewer does).
- Named `g` groups for animation / destruction (OBJ has no skeletons - **no rigs are included**):
  - Humans: head, hair, torso, neck, arm_L/R, sleeve_L/R, hand_L/R, leg_L/R, legwear_L/R, shoe_L/R, accessories.
  - Cars: body, cabin, glass, wheel_FL/FR/RL/RR (+ `_arch`), lights, mirrors, fascia.
  - Trees: trunk, branches, foliage / canopy / fronds / coconuts / blossoms.
  - Buildings: `walls_floorNN`, `windows_floorNN`, `facade_floorNN`, `balconies`, `roof`, `doors`, `canopies`, `roof_equipment`, ...
- `manifest.json` lists per-model triangles, bounding box, groups, materials and **pivot metadata** (human joints, car wheel centres).

## Load in Three.js
```js
const mtl = await new MTLLoader().setPath('models/humans/').loadAsync('HUMAN_01.mtl'); mtl.preload();
const obj = await new OBJLoader().setMaterials(mtl).setPath('models/humans/').loadAsync('HUMAN_01.obj');
```
Run `python3 -m http.server` in this folder and open `viewer.html` to browse all 46 models.

## Models
| Name | Category | Triangles | Size W x H x D (m) |
|---|---|---|---|
| HUMAN_01 | humans | 1836 | 0.7 x 1.8 x 0.4 |
| HUMAN_02 | humans | 1938 | 0.6 x 1.7 x 0.5 |
| HUMAN_03 | humans | 2272 | 0.8 x 1.9 x 0.4 |
| HUMAN_04 | humans | 2276 | 0.7 x 1.8 x 0.4 |
| HUMAN_05 | humans | 2368 | 0.7 x 1.8 x 0.6 |
| HUMAN_06 | humans | 2428 | 0.8 x 1.9 x 0.4 |
| HUMAN_07 | humans | 2444 | 0.7 x 1.8 x 0.4 |
| HUMAN_08 | humans | 2400 | 0.8 x 1.8 x 0.4 |
| HUMAN_09 | humans | 2780 | 0.8 x 1.8 x 0.5 |
| HUMAN_10 | humans | 2464 | 0.7 x 1.7 x 0.4 |
| CAR_01 | cars | 3404 | 1.8 x 1.6 x 4.0 |
| CAR_02 | cars | 3404 | 2.0 x 1.6 x 4.8 |
| CAR_03 | cars | 3664 | 2.1 x 2.1 x 4.6 |
| CAR_04 | cars | 3480 | 2.0 x 1.4 x 4.5 |
| CAR_05 | cars | 3968 | 2.0 x 1.9 x 4.7 |
| CAR_06 | cars | 3680 | 2.0 x 1.6 x 4.9 |
| TREE_01 | trees | 1322 | 13.0 x 12.8 x 11.1 |
| TREE_02 | trees | 1184 | 6.5 x 8.8 x 7.1 |
| TREE_03 | trees | 1192 | 8.5 x 16.5 x 8.9 |
| TREE_04 | trees | 588 | 6.3 x 16.6 x 8.1 |
| TREE_05 | trees | 608 | 7.0 x 14.4 x 6.9 |
| TREE_06 | trees | 2140 | 9.3 x 11.9 x 9.3 |
| TREE_07 | trees | 2768 | 11.8 x 13.3 x 11.8 |
| TREE_08 | trees | 1504 | 9.4 x 7.2 x 8.6 |
| TREE_09 | trees | 470 | 2.4 x 10.0 x 2.3 |
| TREE_10 | trees | 832 | 13.7 x 8.7 x 12.1 |
| BUILDING_01 | buildings | 1704 | 17.5 x 9.3 x 14.2 |
| BUILDING_02 | buildings | 2312 | 6.2 x 14.8 x 12.7 |
| BUILDING_03 | buildings | 3292 | 14.6 x 15.8 x 13.0 |
| BUILDING_04 | buildings | 7140 | 16.9 x 28.0 x 13.0 |
| BUILDING_05 | buildings | 10176 | 24.6 x 88.2 x 23.1 |
| BUILDING_06 | buildings | 1564 | 13.8 x 8.0 x 12.6 |
| BUILDING_07 | buildings | 2032 | 14.9 x 8.5 x 14.8 |
| BUILDING_08 | buildings | 2784 | 18.6 x 12.5 x 17.0 |
| BUILDING_09 | buildings | 10036 | 23.0 x 46.0 x 20.6 |
| BUILDING_10 | buildings | 7708 | 26.8 x 195.0 x 29.4 |
| BUILDING_11 | buildings | 14680 | 29.0 x 45.4 x 18.0 |
| BUILDING_12 | buildings | 6904 | 48.6 x 23.2 x 30.1 |
| BUILDING_13 | buildings | 2314 | 22.6 x 23.0 x 15.1 |
| BUILDING_14 | buildings | 3484 | 20.6 x 22.0 x 19.1 |
| BUILDING_15 | buildings | 3248 | 48.8 x 12.0 x 24.7 |
| BUILDING_16 | buildings | 3108 | 52.0 x 35.2 x 27.3 |
| BUILDING_17 | buildings | 6424 | 20.1 x 23.0 x 14.3 |
| BUILDING_18 | buildings | 3052 | 39.9 x 15.4 x 59.0 |
| BUILDING_19 | buildings | 1908 | 28.0 x 14.9 x 20.5 |
| BUILDING_20 | buildings | 6152 | 30.6 x 252.7 x 30.1 |

