# VALIDATION REPORT - Worldline Asset Pack 03B

Everything below was produced by running scripts against the files in this folder; nothing is asserted that was not checked. Checks are listed with what they do and do not prove.

## 1. Count
| category | expected | found |
|---|---|---|
| A. Animals | 8 | 8 |
| B. Disaster objects | 14 | 14 |
| C. Celestial bodies | 12 | 12 |
| D. Interior / commercial props | 14 | 14 |
| E. Accessories | 12 | 12 |
| F. Emergency / rescue | 9 | 9 |
| G. Floating debris | 12 | 12 |
| **total** | 81 | **81** |

Exact count match: **YES**. Every catalog entry has an OBJ, an MTL, a metadata JSON and a preview PNG on disk (checked by `validate03.py`).

## 2. OBJ / MTL structural checks (`source/validate03.py`, parses the written files)
- Total vertices 168,055, faces 328,898 (all triangles).
- Checked per file: non-empty geometry; all face vertex/normal indices in range; no NaN/inf; `mtllib` resolves; every `usemtl` is defined in the MTL and has `Kd`; OBJ bounding box equals the catalog dimensions; object names carry the asset id; metadata part count equals OBJ object count; per-object signed volume (outward normals); zero-area triangles; identical-geometry duplicates across assets.

- Assets with hard problems: **0** 

- Warnings (not failures; explained):

  - ANIMAL_03 Crow: 1 object(s) with identical vertex layout to another object in the same file (mirrored/instanced parts count)
  - ANIMAL_05 Dog: 3 object(s) with identical vertex layout to another object in the same file (mirrored/instanced parts count)
  - ANIMAL_06 Cat: 3 object(s) with identical vertex layout to another object in the same file (mirrored/instanced parts count)
  - ANIMAL_07 Deer: 1 object(s) with identical vertex layout to another object in the same file (mirrored/instanced parts count)
  - ANIMAL_08 Cow: 3 object(s) with identical vertex layout to another object in the same file (mirrored/instanced parts count)
  - DISASTER_11 Overturned Vehicle Shell: 3 object(s) with identical vertex layout to another object in the same file (mirrored/instanced parts count)
  - INTERIOR_04 Office Desk: 2 object(s) with identical vertex layout to another object in the same file (mirrored/instanced parts count)
  - INTERIOR_10 Market Cart: 1 object(s) with identical vertex layout to another object in the same file (mirrored/instanced parts count)
  - ACCESSORY_09 Binoculars: 1 object(s) with identical vertex layout to another object in the same file (mirrored/instanced parts count)
  - RESCUE_02 Rescue Ladder: 1 object(s) with identical vertex layout to another object in the same file (mirrored/instanced parts count)
  - RESCUE_03 Portable Barricade: 3 object(s) with identical vertex layout to another object in the same file (mirrored/instanced parts count)

## 3. Three.js loader test
All 81 files were parsed with Three.js r160 `MTLLoader` + `OBJLoader` under Node (no GPU, no rendering - this proves the files parse, materials bind by name and geometry is produced, not how they look in a viewer).

- Loaded OK: **81 / 81**. Failures: none.

## 4. Visual inspection
Each model was rendered (Cycles, 768 px) and the previews were looked at by me during development, one contact sheet per category (`previews/_CONTACT_SHEET_*.jpg`). Defects found and fixed during that process included: bird skin materials, rock cuts that removed too much (meteor / lunar fragments), a floating chair back rail and a floating counter shelf, an unreadable hard-hat ridge layout and a flat-panel safety vest. The final previews in this folder were rendered after those fixes; I did not re-inspect every final 768 px image individually, only the category contact sheets built from them.

## 5. Known limitations (honest list)
- Static meshes only; no rigs, no animation, no textures, no UVs.
- **Earth** continents come from hand-written coarse lat/lon polygons - recognisable but not cartographically exact; clouds are a separate translucent part.
- **Celestial bodies** are authored at ~1 unit radius, not at real scale (real radius is in each JSON `notes.scale`). Planet colour regions are per-face materials, so they have faceted edges at this resolution (20k triangles).
- **RESCUE_09 Emergency Supply Crate**: the body is a closed block; the contents rest on top of it rather than inside a hollow interior.
- **DISASTER_03 Lunar Fragment**: interior break faces are filled with a triangle fan, so the banding shows as thin slivers.
- **INTERIOR_14 Display Cabinet**: items inside are seen through two glass layers (door + panel) and read faintly.
- Translucency (glass, ice, clouds, rings) is material alpha (`d` in MTL); some viewers sort it imperfectly.
- **CELESTIAL_12 Comet Nucleus**: the bilobate shape is computed per ray from the centre, which leaves a faint radial pleating on the lobes; no tail/coma by design. **CELESTIAL_10** surface cracks are noise-driven and read as a mottled crust rather than discrete plates.
- Animals are static poses (birds in a flight/landing pose, mammals standing); Dog/Cat/Cow/Deer are blocky-faceted low-poly rather than anatomically detailed.
- Previews are single-angle renders for inspection, not product shots.
- Pack 03A categories (transport, terrain, vegetation, rural) were intentionally not generated.

## 6. Per-asset table
| id | name | verts | faces | objects | materials | Three.js | status |
|---|---|---|---|---|---|---|---|
| ANIMAL_01 | Pigeon | 730 | 1,248 | 21 | 7 | ok | ok |
| ANIMAL_02 | Seagull | 770 | 1,316 | 22 | 6 | ok | ok |
| ANIMAL_03 | Crow | 742 | 1,268 | 19 | 4 | ok | warn |
| ANIMAL_04 | Eagle | 924 | 1,588 | 24 | 6 | ok | ok |
| ANIMAL_05 | Dog | 524 | 956 | 23 | 6 | ok | warn |
| ANIMAL_06 | Cat | 500 | 880 | 23 | 6 | ok | warn |
| ANIMAL_07 | Deer | 564 | 1,012 | 21 | 7 | ok | warn |
| ANIMAL_08 | Cow | 556 | 1,004 | 23 | 7 | ok | warn |
| DISASTER_01 | Atmospheric Impact Asteroid | 288 | 560 | 1 | 3 | ok | ok |
| DISASTER_02 | Meteor Fragment | 191 | 378 | 1 | 2 | ok | ok |
| DISASTER_03 | Lunar Fragment | 173 | 342 | 1 | 3 | ok | ok |
| DISASTER_04 | Fractured Rock | 328 | 644 | 3 | 2 | ok | ok |
| DISASTER_05 | Volcanic Bomb | 100 | 196 | 1 | 2 | ok | ok |
| DISASTER_06 | Lava Rock | 162 | 320 | 1 | 3 | ok | ok |
| DISASTER_07 | Lava Crust Piece | 418 | 800 | 4 | 4 | ok | ok |
| DISASTER_08 | Ground Fissure Module | 292 | 532 | 5 | 4 | ok | ok |
| DISASTER_09 | Impact Crater | 2,393 | 4,718 | 2 | 5 | ok | ok |
| DISASTER_10 | Uprooted Tree | 793 | 1,410 | 6 | 7 | ok | ok |
| DISASTER_11 | Overturned Vehicle Shell | 1,571 | 3,006 | 14 | 5 | ok | warn |
| DISASTER_12 | Collapsed Boat Hull | 1,902 | 3,508 | 11 | 5 | ok | ok |
| DISASTER_13 | Broken Road Slab | 668 | 1,196 | 5 | 4 | ok | ok |
| DISASTER_14 | Ice Fragment | 293 | 558 | 3 | 3 | ok | ok |
| CELESTIAL_01 | Detailed Moon | 10,242 | 20,480 | 1 | 4 | ok | ok |
| CELESTIAL_02 | Earth | 11,322 | 22,280 | 2 | 9 | ok | ok |
| CELESTIAL_03 | Mars | 10,242 | 20,480 | 1 | 4 | ok | ok |
| CELESTIAL_04 | Jupiter | 10,242 | 20,480 | 1 | 6 | ok | ok |
| CELESTIAL_05 | Saturn | 14,562 | 29,120 | 2 | 8 | ok | ok |
| CELESTIAL_06 | Venus | 10,242 | 20,480 | 1 | 4 | ok | ok |
| CELESTIAL_07 | Mercury | 10,242 | 20,480 | 1 | 4 | ok | ok |
| CELESTIAL_08 | Neptune | 10,242 | 20,480 | 1 | 4 | ok | ok |
| CELESTIAL_09 | Rocky Rogue Planet | 10,242 | 20,480 | 1 | 4 | ok | ok |
| CELESTIAL_10 | Icy Rogue Planet | 10,242 | 20,480 | 1 | 5 | ok | ok |
| CELESTIAL_11 | Detailed Astronomical Asteroid | 11,082 | 21,880 | 2 | 4 | ok | ok |
| CELESTIAL_12 | Comet Nucleus | 10,902 | 21,580 | 2 | 4 | ok | ok |
| INTERIOR_01 | Chair | 216 | 380 | 5 | 3 | ok | ok |
| INTERIOR_02 | Table | 120 | 204 | 3 | 2 | ok | ok |
| INTERIOR_03 | Sofa | 312 | 564 | 7 | 3 | ok | ok |
| INTERIOR_04 | Office Desk | 256 | 464 | 8 | 4 | ok | warn |
| INTERIOR_05 | Office Chair | 532 | 964 | 6 | 4 | ok | ok |
| INTERIOR_06 | Shelf | 1,352 | 2,476 | 4 | 8 | ok | ok |
| INTERIOR_07 | Commercial Counter | 264 | 476 | 5 | 5 | ok | ok |
| INTERIOR_08 | Refrigerator | 184 | 332 | 5 | 3 | ok | ok |
| INTERIOR_09 | Vending Machine | 832 | 1,464 | 7 | 9 | ok | ok |
| INTERIOR_10 | Market Cart | 960 | 1,672 | 7 | 6 | ok | warn |
| INTERIOR_11 | Restaurant Table | 652 | 1,252 | 8 | 7 | ok | ok |
| INTERIOR_12 | Outdoor Umbrella | 468 | 788 | 6 | 5 | ok | ok |
| INTERIOR_13 | Cash Register | 576 | 1,052 | 7 | 5 | ok | ok |
| INTERIOR_14 | Display Cabinet | 872 | 1,628 | 7 | 7 | ok | ok |
| ACCESSORY_01 | Smartphone | 196 | 336 | 6 | 4 | ok | ok |
| ACCESSORY_02 | Backpack | 272 | 504 | 7 | 4 | ok | ok |
| ACCESSORY_03 | Handbag | 240 | 444 | 5 | 3 | ok | ok |
| ACCESSORY_04 | Suitcase | 448 | 816 | 7 | 4 | ok | ok |
| ACCESSORY_05 | Umbrella | 468 | 792 | 5 | 5 | ok | ok |
| ACCESSORY_06 | Hard Hat | 574 | 1,112 | 6 | 3 | ok | ok |
| ACCESSORY_07 | Safety Vest | 418 | 720 | 6 | 3 | ok | ok |
| ACCESSORY_08 | Flashlight | 508 | 990 | 7 | 7 | ok | ok |
| ACCESSORY_09 | Binoculars | 492 | 948 | 7 | 4 | ok | warn |
| ACCESSORY_10 | Telescope | 564 | 1,016 | 9 | 5 | ok | ok |
| ACCESSORY_11 | First-Aid Kit | 248 | 444 | 7 | 4 | ok | ok |
| ACCESSORY_12 | Handheld Radio | 242 | 400 | 8 | 6 | ok | ok |
| RESCUE_01 | Stretcher | 624 | 1,128 | 7 | 5 | ok | ok |
| RESCUE_02 | Rescue Ladder | 480 | 864 | 6 | 4 | ok | warn |
| RESCUE_03 | Portable Barricade | 1,010 | 1,848 | 8 | 5 | ok | warn |
| RESCUE_04 | Warning Siren | 476 | 904 | 6 | 6 | ok | ok |
| RESCUE_05 | Megaphone | 350 | 666 | 7 | 6 | ok | ok |
| RESCUE_06 | Fire Extinguisher | 310 | 576 | 9 | 6 | ok | ok |
| RESCUE_07 | Flotation Ring | 564 | 1,080 | 4 | 5 | ok | ok |
| RESCUE_08 | Portable Floodlight | 400 | 724 | 7 | 6 | ok | ok |
| RESCUE_09 | Emergency Supply Crate | 568 | 1,056 | 9 | 8 | ok | ok |
| DEBRIS_01 | Driftwood | 359 | 642 | 4 | 3 | ok | ok |
| DEBRIS_02 | Wooden Plank | 218 | 388 | 5 | 3 | ok | ok |
| DEBRIS_03 | Broken Crate | 856 | 1,506 | 5 | 4 | ok | ok |
| DEBRIS_04 | Floating Barrel | 368 | 728 | 3 | 3 | ok | ok |
| DEBRIS_05 | Pallet | 444 | 796 | 5 | 4 | ok | ok |
| DEBRIS_06 | Road Sign Fragment | 136 | 236 | 5 | 5 | ok | ok |
| DEBRIS_07 | Roof Tile Cluster | 1,738 | 3,408 | 2 | 2 | ok | ok |
| DEBRIS_08 | Shattered Window Panel | 352 | 570 | 4 | 3 | ok | ok |
| DEBRIS_09 | Broken Dock Timber | 262 | 452 | 6 | 6 | ok | ok |
| DEBRIS_10 | Metal Sheet | 686 | 1,332 | 3 | 3 | ok | ok |
| DEBRIS_11 | Broken Furniture | 312 | 540 | 6 | 3 | ok | ok |
| DEBRIS_12 | Uprooted Planter | 590 | 1,076 | 7 | 5 | ok | ok |
## 7. Note on preview files
Preview PNGs were palette-quantised (128 colours) after rendering to keep the archive under the 30 MiB delivery limit; they are inspection images only. OBJ/MTL/JSON files are unaffected.
