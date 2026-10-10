# WORLDLINE ASSET PACK 03B - 81 low-poly OBJ models

Procedurally modelled in Blender (bpy) with real geometry: animals, disaster objects, celestial bodies, interior/commercial props, accessories, rescue gear and floating debris. Pack 03A (transport / terrain / vegetation / rural) is a separate pack and is **not** included.

## Contents

| folder | models |
|---|---|
| `animals/` | 8 |
| `disaster_objects/` | 14 |
| `celestial/` | 12 |
| `interiors/` | 14 |
| `accessories/` | 12 |
| `emergency/` | 9 |
| `floating_debris/` | 12 |
| `previews/` | one PNG per model + a contact sheet per category |
| `metadata/` | one JSON per model (pivots, parts, grip/attachment points, bounds) |

Total: **81 models**, 328,898 triangles.

## Conventions
- Units: **metres** for animals, disaster, interiors, accessories, rescue and debris. Celestial bodies are authored at ~1 model unit = body radius (real-size factor in each JSON `notes.scale`).
- Axes: **Y-up, forward = -Z** (right-handed). Grounded objects rest on Y = 0 with the origin at the footprint centre; airborne / celestial objects are centred.
- OBJ is triangulated with outward-facing normals, one `o` object per named component. Component names are `<ASSET_ID>_<Name>` (e.g. `INTERIOR_08_Door_Fridge`).
- Movable parts (doors, drawers, wheels, swivel seats, lids, jaws...) are separate objects; because OBJ stores no pivots, their pivots are written to `metadata/<asset>.json` (`parts[].pivot_file_xyz`, same axes as the OBJ).
- Grip / attachment points for accessories and rescue items are in the JSON key `attachment_points_file_xyz`.
- Materials: `<asset>.mtl` next to each OBJ (flat colours, `d` for translucency, `Ke` for emissive). **No textures, no UVs** - nothing to resolve or relocate.
- These are **static meshes**. Nothing here is animated; poses are described in each JSON `pose`.

## Loading (Three.js)
```js
const mtl = await new MTLLoader().loadAsync('interiors/INTERIOR_08_Refrigerator.mtl'); mtl.preload();
const obj = await new OBJLoader().setMaterials(mtl).loadAsync('interiors/INTERIOR_08_Refrigerator.obj');
```

## Model list

### A. Animals
| id | name | file | triangles | size W x H x D (m) | parts |
|---|---|---|---|---|---|
| ANIMAL_01 | Pigeon | `animals/ANIMAL_01_Pigeon.obj` | 1,248 | 0.70 x 0.24 x 0.47 | 21 |
| ANIMAL_02 | Seagull | `animals/ANIMAL_02_Seagull.obj` | 1,316 | 1.35 x 0.17 x 0.71 | 22 |
| ANIMAL_03 | Crow | `animals/ANIMAL_03_Crow.obj` | 1,268 | 1.04 x 0.36 x 0.74 | 19 |
| ANIMAL_04 | Eagle | `animals/ANIMAL_04_Eagle.obj` | 1,588 | 2.18 x 0.61 x 1.40 | 24 |
| ANIMAL_05 | Dog | `animals/ANIMAL_05_Dog.obj` | 956 | 0.33 x 0.79 x 1.21 | 23 |
| ANIMAL_06 | Cat | `animals/ANIMAL_06_Cat.obj` | 880 | 0.23 x 0.59 x 0.83 | 23 |
| ANIMAL_07 | Deer | `animals/ANIMAL_07_Deer.obj` | 1,012 | 0.42 x 1.93 x 1.32 | 21 |
| ANIMAL_08 | Cow | `animals/ANIMAL_08_Cow.obj` | 1,004 | 0.70 x 1.41 x 2.33 | 23 |

### B. Disaster objects
| id | name | file | triangles | size W x H x D (m) | parts |
|---|---|---|---|---|---|
| DISASTER_01 | Atmospheric Impact Asteroid | `disaster_objects/DISASTER_01_AtmosphericImpactAsteroid.obj` | 560 | 4.30 x 3.14 x 3.98 | 1 |
| DISASTER_02 | Meteor Fragment | `disaster_objects/DISASTER_02_MeteorFragment.obj` | 378 | 0.95 x 0.84 x 0.95 | 1 |
| DISASTER_03 | Lunar Fragment | `disaster_objects/DISASTER_03_LunarFragment.obj` | 342 | 1.78 x 1.36 x 1.32 | 1 |
| DISASTER_04 | Fractured Rock | `disaster_objects/DISASTER_04_FracturedRock.obj` | 644 | 3.67 x 2.29 x 2.92 | 3 |
| DISASTER_05 | Volcanic Bomb | `disaster_objects/DISASTER_05_VolcanicBomb.obj` | 196 | 0.81 x 0.50 x 0.53 | 1 |
| DISASTER_06 | Lava Rock | `disaster_objects/DISASTER_06_LavaRock.obj` | 320 | 1.07 x 0.78 x 1.00 | 1 |
| DISASTER_07 | Lava Crust Piece | `disaster_objects/DISASTER_07_LavaCrustPiece.obj` | 800 | 2.58 x 0.26 x 1.84 | 4 |
| DISASTER_08 | Ground Fissure Module | `disaster_objects/DISASTER_08_GroundFissureModule.obj` | 532 | 4.00 x 1.75 x 4.00 | 5 |
| DISASTER_09 | Impact Crater | `disaster_objects/DISASTER_09_ImpactCrater.obj` | 4,718 | 10.00 x 3.67 x 10.00 | 2 |
| DISASTER_10 | Uprooted Tree | `disaster_objects/DISASTER_10_UprootedTree.obj` | 1,410 | 4.11 x 2.70 x 7.62 | 6 |
| DISASTER_11 | Overturned Vehicle Shell | `disaster_objects/DISASTER_11_OverturnedVehicleShell.obj` | 3,006 | 3.50 x 1.50 x 4.74 | 14 |
| DISASTER_12 | Collapsed Boat Hull | `disaster_objects/DISASTER_12_CollapsedBoatHull.obj` | 3,508 | 4.41 x 3.28 x 7.53 | 11 |
| DISASTER_13 | Broken Road Slab | `disaster_objects/DISASTER_13_BrokenRoadSlab.obj` | 1,196 | 4.54 x 2.29 x 8.92 | 5 |
| DISASTER_14 | Ice Fragment | `disaster_objects/DISASTER_14_IceFragment.obj` | 558 | 1.19 x 1.13 x 1.01 | 3 |

### C. Celestial bodies
| id | name | file | triangles | size W x H x D (m) | parts |
|---|---|---|---|---|---|
| CELESTIAL_01 | Detailed Moon | `celestial/CELESTIAL_01_DetailedMoon.obj` | 20,480 | 2.00 x 2.01 x 2.00 | 1 |
| CELESTIAL_02 | Earth | `celestial/CELESTIAL_02_Earth.obj` | 22,280 | 2.07 x 2.03 x 2.08 | 2 |
| CELESTIAL_03 | Mars | `celestial/CELESTIAL_03_Mars.obj` | 20,480 | 2.02 x 2.01 x 2.01 | 1 |
| CELESTIAL_04 | Jupiter | `celestial/CELESTIAL_04_Jupiter.obj` | 20,480 | 2.00 x 1.87 x 2.00 | 1 |
| CELESTIAL_05 | Saturn | `celestial/CELESTIAL_05_Saturn.obj` | 29,120 | 4.69 x 1.80 x 4.69 | 2 |
| CELESTIAL_06 | Venus | `celestial/CELESTIAL_06_Venus.obj` | 20,480 | 2.00 x 2.00 x 2.01 | 1 |
| CELESTIAL_07 | Mercury | `celestial/CELESTIAL_07_Mercury.obj` | 20,480 | 2.01 x 2.01 x 2.01 | 1 |
| CELESTIAL_08 | Neptune | `celestial/CELESTIAL_08_Neptune.obj` | 20,480 | 2.00 x 1.97 x 2.00 | 1 |
| CELESTIAL_09 | Rocky Rogue Planet | `celestial/CELESTIAL_09_RockyRoguePlanet.obj` | 20,480 | 2.04 x 2.04 x 2.03 | 1 |
| CELESTIAL_10 | Icy Rogue Planet | `celestial/CELESTIAL_10_IcyRoguePlanet.obj` | 20,480 | 2.01 x 2.01 x 2.01 | 1 |
| CELESTIAL_11 | Detailed Astronomical Asteroid | `celestial/CELESTIAL_11_DetailedAstronomicalAsteroid.obj` | 21,880 | 2.69 x 1.40 x 1.56 | 2 |
| CELESTIAL_12 | Comet Nucleus | `celestial/CELESTIAL_12_CometNucleus.obj` | 21,580 | 3.41 x 1.76 x 1.72 | 2 |

### D. Interior / commercial props
| id | name | file | triangles | size W x H x D (m) | parts |
|---|---|---|---|---|---|
| INTERIOR_01 | Chair | `interiors/INTERIOR_01_Chair.obj` | 380 | 0.46 x 0.96 x 0.44 | 5 |
| INTERIOR_02 | Table | `interiors/INTERIOR_02_Table.obj` | 204 | 1.99 x 0.76 x 1.09 | 3 |
| INTERIOR_03 | Sofa | `interiors/INTERIOR_03_Sofa.obj` | 564 | 2.00 x 0.88 x 0.91 | 7 |
| INTERIOR_04 | Office Desk | `interiors/INTERIOR_04_OfficeDesk.obj` | 464 | 1.50 x 0.77 x 0.76 | 8 |
| INTERIOR_05 | Office Chair | `interiors/INTERIOR_05_OfficeChair.obj` | 964 | 0.64 x 0.97 x 0.65 | 6 |
| INTERIOR_06 | Shelf | `interiors/INTERIOR_06_Shelf.obj` | 2,476 | 0.83 x 1.83 x 0.30 | 4 |
| INTERIOR_07 | Commercial Counter | `interiors/INTERIOR_07_CommercialCounter.obj` | 476 | 2.34 x 1.84 x 0.79 | 5 |
| INTERIOR_08 | Refrigerator | `interiors/INTERIOR_08_Refrigerator.obj` | 332 | 0.70 x 1.78 x 0.78 | 5 |
| INTERIOR_09 | Vending Machine | `interiors/INTERIOR_09_VendingMachine.obj` | 1,464 | 0.97 x 1.88 x 0.89 | 7 |
| INTERIOR_10 | Market Cart | `interiors/INTERIOR_10_MarketCart.obj` | 1,672 | 1.52 x 1.91 x 2.38 | 7 |
| INTERIOR_11 | Restaurant Table | `interiors/INTERIOR_11_RestaurantTable.obj` | 1,252 | 0.83 x 0.86 x 0.83 | 8 |
| INTERIOR_12 | Outdoor Umbrella | `interiors/INTERIOR_12_OutdoorUmbrella.obj` | 788 | 3.00 x 2.72 x 3.00 | 6 |
| INTERIOR_13 | Cash Register | `interiors/INTERIOR_13_CashRegister.obj` | 1,052 | 0.42 x 0.45 x 0.44 | 7 |
| INTERIOR_14 | Display Cabinet | `interiors/INTERIOR_14_DisplayCabinet.obj` | 1,628 | 0.95 x 1.88 x 0.47 | 7 |

### E. Accessories
| id | name | file | triangles | size W x H x D (m) | parts |
|---|---|---|---|---|---|
| ACCESSORY_01 | Smartphone | `accessories/ACCESSORY_01_Smartphone.obj` | 336 | 0.08 x 0.01 x 0.15 | 6 |
| ACCESSORY_02 | Backpack | `accessories/ACCESSORY_02_Backpack.obj` | 504 | 0.49 x 0.61 x 0.36 | 7 |
| ACCESSORY_03 | Handbag | `accessories/ACCESSORY_03_Handbag.obj` | 444 | 0.34 x 0.34 x 0.18 | 5 |
| ACCESSORY_04 | Suitcase | `accessories/ACCESSORY_04_Suitcase.obj` | 816 | 0.47 x 1.00 x 0.29 | 7 |
| ACCESSORY_05 | Umbrella | `accessories/ACCESSORY_05_Umbrella.obj` | 792 | 1.52 x 0.99 x 1.52 | 5 |
| ACCESSORY_06 | Hard Hat | `accessories/ACCESSORY_06_HardHat.obj` | 1,112 | 0.38 x 0.18 x 0.46 | 6 |
| ACCESSORY_07 | Safety Vest | `accessories/ACCESSORY_07_SafetyVest.obj` | 720 | 0.42 x 0.62 x 0.26 | 6 |
| ACCESSORY_08 | Flashlight | `accessories/ACCESSORY_08_Flashlight.obj` | 990 | 0.10 x 0.23 x 0.10 | 7 |
| ACCESSORY_09 | Binoculars | `accessories/ACCESSORY_09_Binoculars.obj` | 948 | 0.18 x 0.08 x 0.23 | 7 |
| ACCESSORY_10 | Telescope | `accessories/ACCESSORY_10_Telescope.obj` | 1,016 | 1.08 x 1.69 x 1.38 | 9 |
| ACCESSORY_11 | First-Aid Kit | `accessories/ACCESSORY_11_FirstAidKit.obj` | 444 | 0.32 x 0.25 x 0.14 | 7 |
| ACCESSORY_12 | Handheld Radio | `accessories/ACCESSORY_12_HandheldRadio.obj` | 400 | 0.06 x 0.30 x 0.04 | 8 |

### F. Emergency / rescue
| id | name | file | triangles | size W x H x D (m) | parts |
|---|---|---|---|---|---|
| RESCUE_01 | Stretcher | `emergency/RESCUE_01_Stretcher.obj` | 1,128 | 0.65 x 0.18 x 2.40 | 7 |
| RESCUE_02 | Rescue Ladder | `emergency/RESCUE_02_RescueLadder.obj` | 864 | 0.51 x 0.17 x 3.33 | 6 |
| RESCUE_03 | Portable Barricade | `emergency/RESCUE_03_PortableBarricade.obj` | 1,848 | 1.95 x 1.17 x 1.14 | 8 |
| RESCUE_04 | Warning Siren | `emergency/RESCUE_04_WarningSiren.obj` | 904 | 0.97 x 2.18 x 0.92 | 6 |
| RESCUE_05 | Megaphone | `emergency/RESCUE_05_Megaphone.obj` | 666 | 0.36 x 0.35 x 0.52 | 7 |
| RESCUE_06 | Fire Extinguisher | `emergency/RESCUE_06_FireExtinguisher.obj` | 576 | 0.23 x 0.60 x 0.16 | 9 |
| RESCUE_07 | Flotation Ring | `emergency/RESCUE_07_FlotationRing.obj` | 1,080 | 0.82 x 0.14 x 0.82 | 4 |
| RESCUE_08 | Portable Floodlight | `emergency/RESCUE_08_PortableFloodlight.obj` | 724 | 1.25 x 2.09 x 0.96 | 7 |
| RESCUE_09 | Emergency Supply Crate | `emergency/RESCUE_09_EmergencySupplyCrate.obj` | 1,056 | 0.79 x 0.75 x 0.66 | 9 |

### G. Floating debris
| id | name | file | triangles | size W x H x D (m) | parts |
|---|---|---|---|---|---|
| DEBRIS_01 | Driftwood | `floating_debris/DEBRIS_01_Driftwood.obj` | 642 | 3.49 x 0.60 x 0.96 | 4 |
| DEBRIS_02 | Wooden Plank | `floating_debris/DEBRIS_02_WoodenPlank.obj` | 388 | 0.27 x 0.11 x 2.32 | 5 |
| DEBRIS_03 | Broken Crate | `floating_debris/DEBRIS_03_BrokenCrate.obj` | 1,506 | 0.81 x 0.60 x 1.22 | 5 |
| DEBRIS_04 | Floating Barrel | `floating_debris/DEBRIS_04_FloatingBarrel.obj` | 728 | 0.90 x 0.71 x 0.69 | 3 |
| DEBRIS_05 | Pallet | `floating_debris/DEBRIS_05_Pallet.obj` | 796 | 1.21 x 0.16 x 1.25 | 5 |
| DEBRIS_06 | Road Sign Fragment | `floating_debris/DEBRIS_06_RoadSignFragment.obj` | 236 | 1.66 x 0.19 x 0.62 | 5 |
| DEBRIS_07 | Roof Tile Cluster | `floating_debris/DEBRIS_07_RoofTileCluster.obj` | 3,408 | 1.51 x 0.08 x 1.35 | 2 |
| DEBRIS_08 | Shattered Window Panel | `floating_debris/DEBRIS_08_ShatteredWindowPanel.obj` | 570 | 1.57 x 0.05 x 1.41 | 4 |
| DEBRIS_09 | Broken Dock Timber | `floating_debris/DEBRIS_09_BrokenDockTimber.obj` | 452 | 1.17 x 0.41 x 2.89 | 6 |
| DEBRIS_10 | Metal Sheet | `floating_debris/DEBRIS_10_MetalSheet.obj` | 1,332 | 1.00 x 0.31 x 1.60 | 3 |
| DEBRIS_11 | Broken Furniture | `floating_debris/DEBRIS_11_BrokenFurniture.obj` | 540 | 1.18 x 0.38 x 0.99 | 6 |
| DEBRIS_12 | Uprooted Planter | `floating_debris/DEBRIS_12_UprootedPlanter.obj` | 1,076 | 1.00 x 0.56 x 1.12 | 7 |

## Regenerating
`blender -b -P source/worldline_pack03b_generate.py -- --out ./WORLDLINE_ASSET_PACK_03B_81` (Blender 3.2+, or `pip install bpy`). `--only INTERIOR_08,CELESTIAL` builds a subset; `--no-render` skips previews. `source/validate03.py <pack folder>` re-runs the independent OBJ/MTL validation.
