# WORLDLINE LAB - Asset Pack 03A (80 models)

Transportation, terrain, vegetation and rural infrastructure. 80 OBJ + MTL pairs, 252,016 triangles in total, no external textures (flat-colour MTL materials only).

| Folder | Models |
|---|---|
| land_vehicles/ | 12 |
| small_vehicles/ | 6 |
| boats/ | 10 |
| aircraft/ | 7 |
| rail/ | 8 |
| terrain/ | 16 |
| plants/ | 12 |
| rural_landmarks/ | 9 |

## Conventions
- Meters, **Y-up**, right-handed. Grounded assets sit on Y = 0 (boats: keel at Y = 0, waterline height in the JSON metadata).
- **Nominal forward = -Z** for land/small vehicles, boats, aircraft and rail. Terrain, plants and rural landmarks are static scenery with no heading.
- One normal per triangle (`vn`), flat/faceted shading. Winding is outward-facing (verified per solid part by signed volume at build time).
- Named `g` groups for movable parts (wheels, rotors, ladder, dump bed, boom/stick/bucket, gates...). **OBJ holds no skeleton/animation**; pivots live in `metadata/<ID>.json` (`pivots`).
- Boats: `extra.waterline_height_above_keel_m` (also pivot `waterline_reference`) for buoyancy.
- Load: `MTLLoader` then `OBJLoader` (set `transparent = true` where `opacity < 1` for glass).

## Files
`ASSET_CATALOG.json` (index), `metadata/` (per-asset JSON), `previews/` (per-asset PNG + contact sheets), `STYLE_GUIDE.md`, `VALIDATION_REPORT.md`.

## Models
| ID | Title | Triangles | Size W x H x D (m) |
|---|---|---|---|
| LAND_01 | City Bus | 2,996 | 3.4 x 3.7 x 11.8 |
| LAND_02 | School Bus | 4,104 | 3.1 x 3.1 x 9.7 |
| LAND_03 | Ambulance | 3,004 | 3.2 x 3.3 x 6.5 |
| LAND_04 | Fire Truck | 5,068 | 3.8 x 3.6 x 9.2 |
| LAND_05 | Police Van | 3,152 | 3.1 x 2.8 x 6.2 |
| LAND_06 | Delivery Van | 2,800 | 3.0 x 3.2 x 6.3 |
| LAND_07 | Semi-Truck (tractor + trailer) | 10,368 | 3.4 x 4.3 x 19.3 |
| LAND_08 | Dump Truck | 5,820 | 3.5 x 3.8 x 10.3 |
| LAND_09 | Cement Mixer | 6,212 | 3.4 x 4.5 x 11.8 |
| LAND_10 | Bulldozer | 2,160 | 3.9 x 3.5 x 5.9 |
| LAND_11 | Excavator | 2,392 | 3.9 x 5.1 x 10.5 |
| LAND_12 | Tow Truck | 3,972 | 4.0 x 4.1 x 10.9 |
| SMALL_01 | Motorcycle | 2,444 | 0.8 x 1.3 x 2.2 |
| SMALL_02 | Scooter | 1,892 | 0.8 x 1.5 x 2.0 |
| SMALL_03 | Bicycle | 2,192 | 0.7 x 1.1 x 1.6 |
| SMALL_04 | Electric Bicycle | 2,508 | 0.7 x 1.2 x 1.6 |
| SMALL_05 | Delivery Motorcycle | 2,708 | 0.8 x 1.6 x 2.4 |
| SMALL_06 | Quad Bike | 2,356 | 1.5 x 1.1 x 2.0 |
| BOAT_01 | Fishing Boat | 2,660 | 4.0 x 6.9 x 14.2 |
| BOAT_02 | Speedboat | 640 | 2.2 x 2.5 x 7.8 |
| BOAT_03 | Yacht | 2,496 | 6.4 x 11.8 x 23.5 |
| BOAT_04 | Passenger Ferry | 3,536 | 9.0 x 10.9 x 29.9 |
| BOAT_05 | Cargo Ship | 3,904 | 17.0 x 25.4 x 89.5 |
| BOAT_06 | Container Ship | 5,680 | 26.0 x 36.5 x 109.5 |
| BOAT_07 | Tugboat | 3,820 | 5.9 x 8.3 x 12.6 |
| BOAT_08 | Sailboat | 1,052 | 3.1 x 15.0 x 13.1 |
| BOAT_09 | Coast Guard Boat | 2,440 | 5.3 x 8.7 x 16.5 |
| BOAT_10 | Oil Tanker | 4,656 | 19.0 x 26.5 x 124.4 |
| AIR_01 | Passenger Airliner | 4,884 | 36.5 x 11.9 x 39.4 |
| AIR_02 | Cargo Aircraft | 11,616 | 60.0 x 19.4 x 48.6 |
| AIR_03 | Civilian Helicopter | 1,056 | 10.6 x 3.5 x 12.0 |
| AIR_04 | Rescue Helicopter | 1,280 | 11.3 x 4.5 x 14.4 |
| AIR_05 | Fighter Jet | 2,584 | 12.2 x 4.9 x 19.4 |
| AIR_06 | Private Jet | 3,560 | 18.2 x 6.0 x 20.8 |
| AIR_07 | Drone | 1,280 | 1.9 x 0.8 x 1.9 |
| RAIL_01 | Subway Train | 1,884 | 3.0 x 4.0 x 18.1 |
| RAIL_02 | Elevated Monorail | 1,096 | 3.2 x 9.2 x 26.0 |
| RAIL_03 | Street Tram | 2,312 | 2.7 x 5.0 x 18.1 |
| RAIL_04 | Passenger Train | 3,788 | 3.0 x 5.7 x 46.5 |
| RAIL_05 | Freight Train | 6,644 | 3.1 x 4.8 x 53.2 |
| RAIL_06 | Rail Track Module | 2,504 | 4.5 x 0.8 x 10.1 |
| RAIL_07 | Railway Crossing Barrier | 1,220 | 10.0 x 4.3 x 7.0 |
| RAIL_08 | Elevated Rail Support | 796 | 7.8 x 15.5 x 14.0 |
| TERRAIN_01 | Small Rock | 320 | 2.0 x 0.9 x 1.5 |
| TERRAIN_02 | Large Boulder | 1,280 | 6.4 x 2.9 x 5.8 |
| TERRAIN_03 | Rock Cluster | 1,520 | 6.6 x 2.0 x 6.0 |
| TERRAIN_04 | Cliff Face | 3,392 | 62.0 x 27.8 x 34.0 |
| TERRAIN_05 | Mountain Peak | 4,784 | 110.0 x 41.6 x 110.0 |
| TERRAIN_06 | Volcanic Cone | 4,400 | 108.0 x 25.5 x 108.0 |
| TERRAIN_07 | Crater | 4,400 | 76.0 x 10.7 x 76.0 |
| TERRAIN_08 | Canyon Segment | 4,328 | 62.0 x 26.3 x 84.0 |
| TERRAIN_09 | Hillside | 3,680 | 80.0 x 11.5 x 80.0 |
| TERRAIN_10 | Sand Dune | 3,336 | 72.0 x 11.9 x 56.0 |
| TERRAIN_11 | Sandy Beach | 2,712 | 70.0 x 6.4 x 62.0 |
| TERRAIN_12 | Rocky Coastline | 2,820 | 72.0 x 19.2 x 54.0 |
| TERRAIN_13 | Riverbank | 2,400 | 56.0 x 5.7 x 44.0 |
| TERRAIN_14 | Cave Entrance | 1,928 | 22.8 x 11.5 x 23.2 |
| TERRAIN_15 | Cracked Ground | 876 | 45.0 x 2.0 x 40.0 |
| TERRAIN_16 | Raised Terrain Plateau | 4,776 | 96.0 x 16.6 x 88.0 |
| PLANT_01 | Grass Tuft | 756 | 0.6 x 0.5 x 0.6 |
| PLANT_02 | Tall Grass | 1,296 | 1.6 x 1.9 x 1.6 |
| PLANT_03 | Flowering Bush | 3,472 | 1.9 x 1.7 x 2.0 |
| PLANT_04 | Hedge | 1,488 | 1.3 x 1.5 x 4.3 |
| PLANT_05 | Fern | 3,988 | 3.0 x 0.8 x 2.7 |
| PLANT_06 | Cactus | 1,096 | 2.2 x 3.2 x 1.1 |
| PLANT_07 | Bamboo Cluster | 5,620 | 5.2 x 7.9 x 5.2 |
| PLANT_08 | Tropical Broadleaf Plant | 1,728 | 4.1 x 2.2 x 4.5 |
| PLANT_09 | Planter Flowers | 2,064 | 1.1 x 1.4 x 1.2 |
| PLANT_10 | Mangrove Roots | 2,024 | 6.6 x 5.9 x 6.4 |
| PLANT_11 | Vine Cluster | 1,756 | 3.4 x 1.8 x 3.7 |
| PLANT_12 | Dry Scrub | 2,886 | 1.6 x 1.4 x 1.6 |
| RURAL_01 | Windmill (windpump) | 2,304 | 5.3 x 15.2 x 6.1 |
| RURAL_02 | Water Tower | 3,728 | 10.7 x 24.9 x 10.7 |
| RURAL_03 | Radio Tower | 3,786 | 11.8 x 59.1 x 5.7 |
| RURAL_04 | Grain Silo | 3,204 | 9.7 x 17.9 x 9.4 |
| RURAL_05 | Barn | 798 | 15.1 x 12.9 x 18.6 |
| RURAL_06 | Greenhouse | 2,300 | 8.3 x 4.7 x 14.3 |
| RURAL_07 | Oil Storage Tank | 6,160 | 36.3 x 14.0 x 36.0 |
| RURAL_08 | Industrial Chimney | 8,128 | 9.6 x 59.5 x 7.8 |
| RURAL_09 | Solar Panel Array | 2,946 | 13.5 x 1.6 x 11.6 |
