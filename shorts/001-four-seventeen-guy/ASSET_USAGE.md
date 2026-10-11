# Asset Usage Manifest — Short 001

## Humans — WORLDLINE_LAB_ASSET_PACK_46
- `models/humans/HUMAN_03.obj/.mtl` — The 4:17 Guy. Formal jacket/tie asset. Group pivots are driven from Pack 46 manifest metadata.
- `models/humans/HUMAN_01.obj/.mtl` — left office worker.
- `models/humans/HUMAN_04.obj/.mtl` — right office worker.
- `models/humans/HUMAN_02.obj/.mtl` — background office worker.

Pack 46 explicitly provides named human body groups and joint-pivot metadata, although no skeleton is included. Short 001 creates runtime pivot groups from that supplied metadata rather than replacing the people with primitives.

## Interiors — WORLDLINE_ASSET_PACK_03B_81
- `interiors/INTERIOR_04_OfficeDesk.obj/.mtl` — three office workstations.
- `interiors/INTERIOR_05_OfficeChair.obj/.mtl` — three office chairs, including the impact chair.
- `interiors/INTERIOR_06_Shelf.obj/.mtl` — background bookcase.

## Procedural supporting geometry
Only assets not present as dedicated supplied props are generated:
- office room shell / ceiling tile
- digital wall clock
- monitors and keyboards
- paper sheets
- drinking cup and visible water
- ceiling fragments

These are supporting geometry, not replacements for available supplied hero assets.
