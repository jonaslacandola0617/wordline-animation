# STYLE GUIDE - Asset Pack 02

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
