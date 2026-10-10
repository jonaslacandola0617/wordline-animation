# Worldline style guide - Pack 03B

Stylised low-poly with **real modelled form**: every object is built from lofted / lathed / bevelled / displaced geometry, not primitives stacked in a block. Flat shading by default (hard facets), chamfered edges on man-made parts, smooth shading only for gas-giant globes. Damage is geometry: cuts, splintered ends, recessed fissures, dents and missing slats are real vertices, not texture.

## Shared palette (identical to Pack 03A)
| token | hex | use |
|---|---|---|
| `WL_concrete` | `#C9BDB0` | warm concrete |
| `WL_stone` | `#DED4C4` | light stone |
| `WL_asphalt` | `#454B50` | asphalt / road |
| `WL_blue_steel` | `#628797` | painted blue steel |
| `WL_steel` | `#68747C` | structural steel |
| `WL_timber` | `#A67B56` | warm timber |
| `WL_foliage_mid` | `#65936B` | mid foliage |
| `WL_foliage_deep` | `#416F56` | deep foliage |
| `WL_coral` | `#D87560` | muted coral |
| `WL_yellow` | `#E5B64D` | safety yellow |
| `WL_offwhite` | `#ECE8DF` | warm off-white |
| `WL_rubber` | `#292F34` | dark rubber |

## Extra colours (animals, geology, planets, props, accessories, rescue)
Pack-specific hues used by 03B only. Every material in an MTL is named `WL_<token>`; full list with roughness / metalness / emission / alpha:

```

# ---- shared Worldline base palette (identical to Pack 03A) ----
"concrete": ("#C9BDB0", 0.92), "stone": ("#DED4C4", 0.90), "asphalt": ("#454B50", 0.95),
"blue_steel": ("#628797", 0.50, 0.35), "steel": ("#68747C", 0.45, 0.55), "timber": ("#A67B56", 0.88),
"foliage_mid": ("#65936B", 0.90), "foliage_deep": ("#416F56", 0.90), "coral": ("#D87560", 0.75),
"yellow": ("#E5B64D", 0.70), "offwhite": ("#ECE8DF", 0.80), "rubber": ("#292F34", 0.92),
# ---- animals ----
"pigeon_grey": ("#9AA2A8", 0.9), "pigeon_dark": ("#656D74", 0.9), "pigeon_neck": ("#5F8F8A", 0.5),
"pigeon_pink": ("#C98588", 0.8), "beak_dark": ("#4A4440", 0.7), "beak_yellow": ("#E2B24A", 0.6),
"eye_orange": ("#E8872A", 0.4), "eye_dark": ("#1B1C20", 0.35), "white": ("#F4F3EE", 0.85),
"gull_grey": ("#A3AEB6", 0.9), "gull_red": ("#D8402F", 0.6), "crow_black": ("#2B2D33", 0.85),
"crow_sheen": ("#414657", 0.6), "eagle_brown": ("#6B4A33", 0.9), "eagle_light": ("#A5805C", 0.9),
"eagle_white": ("#EFEADD", 0.85), "talon": ("#3B342F", 0.6),
"dog_tan": ("#B98A56", 0.9), "dog_dark": ("#7A5738", 0.9), "dog_light": ("#E8D9BC", 0.9),
"cat_grey": ("#8C8F96", 0.9), "cat_stripe": ("#5C5F66", 0.9), "pink_nose": ("#D9928E", 0.7),
"deer_brown": ("#A7733F", 0.9), "deer_belly": ("#E9D9BC", 0.9), "antler": ("#CDB894", 0.8),
"cow_white": ("#F1EEE6", 0.9), "cow_black": ("#2A2C30", 0.9), "cow_pink": ("#E0A59B", 0.8), "hoof": ("#3B3430", 0.7),
# ---- disaster / geology ----
"rock_dark": ("#4F4843", 0.95), "rock_char": ("#2E2A29", 0.95), "rock_mid": ("#6D655E", 0.95),
"ember": ("#C2552B", 0.7, 0.0, 0.9), "lava_glow": ("#FF6A2B", 0.5, 0.0, 2.2), "basalt": ("#3C3B3F", 0.9),
"ash": ("#7B7570", 0.95), "meteor_core": ("#8A7C72", 0.9), "regolith": ("#A9A8A4", 0.95),
"lunar_dark": ("#7A7977", 0.95), "lunar_fresh": ("#C9C8C4", 0.9), "ice_pale": ("#CFE8F2", 0.25, 0.0, 0.0, 0.85),
"ice_deep": ("#7FB7D6", 0.2, 0.0, 0.0, 0.8), "ice_white": ("#F0F6FA", 0.5), "soil": ("#6B4F3A", 0.95),
"bark": ("#6E4F37", 0.95), "root": ("#5A4130", 0.95), "bark_fresh": ("#C9A27A", 0.9),
"crust_black": ("#232223", 0.9), "sand": ("#D9C8A0", 0.95), "dirt_dark": ("#4A382B", 0.95),
"glass": ("#8FC7DE", 0.1, 0.0, 0.0, 0.55), "car_red": ("#B84A3E", 0.45, 0.2), "car_dark": ("#2D3136", 0.6),
"hull_white": ("#E7E4DA", 0.7), "hull_blue": ("#3C6E8F", 0.6), "rust": ("#8A4B33", 0.9), "road_line": ("#E8E1CC", 0.8),
# ---- celestial ----
"moon_hi": ("#BDBAB3", 0.95), "moon_mare": ("#6F6D6A", 0.95), "moon_rim": ("#D6D3CB", 0.95), "moon_floor": ("#8C8A85", 0.95),
"ocean": ("#2F6FB5", 0.35), "ocean_deep": ("#245A9A", 0.35), "ocean_shallow": ("#4C93CF", 0.35),
"land_green": ("#5E9A4F", 0.9), "land_dark": ("#3F7A47", 0.9), "land_brown": ("#9A8A52", 0.9), "desert": ("#D0B070", 0.9),
"polar": ("#F2F6F8", 0.6), "cloud": ("#FFFFFF", 0.9, 0.0, 0.0, 0.6),
"mars_red": ("#B5532F", 0.95), "mars_dark": ("#7A3A27", 0.95), "mars_light": ("#D9936A", 0.95), "mars_ice": ("#EFE9E0", 0.7),
"jup_cream": ("#EBDDBF", 0.8), "jup_tan": ("#CC9E66", 0.8), "jup_brown": ("#9B6B45", 0.8), "jup_rust": ("#B8603A", 0.8),
"jup_white": ("#F5EEDD", 0.8), "jup_red": ("#C4492F", 0.7),
"sat_cream": ("#E8D8A8", 0.8), "sat_gold": ("#CBA96B", 0.8), "sat_pale": ("#F1E6C2", 0.8), "sat_dark": ("#A58E5E", 0.8),
"ring_a": ("#D6C59C", 0.85, 0.0, 0.0, 0.92), "ring_b": ("#9A8A6A", 0.85, 0.0, 0.0, 0.85),
"ring_c": ("#EADFBF", 0.85, 0.0, 0.0, 0.92), "ring_gap": ("#6F6350", 0.85, 0.0, 0.0, 0.55),
"venus_a": ("#E5CF92", 0.8), "venus_b": ("#F1E3B4", 0.8), "venus_c": ("#D4B574", 0.8), "venus_d": ("#C9A15A", 0.8),
"merc_a": ("#8D8680", 0.95), "merc_b": ("#6B6560", 0.95), "merc_c": ("#A9A39C", 0.95), "merc_d": ("#7C6F63", 0.95),
"nep_a": ("#2F55C9", 0.55), "nep_b": ("#3F6FE0", 0.55), "nep_c": ("#1F3A94", 0.55), "nep_d": ("#8DB3F5", 0.55),
"rogue_dark": ("#3D2E2A", 0.95), "rogue_mid": ("#6B4A3A", 0.95), "rogue_hi": ("#8E7461", 0.95),
"rogue_glow": ("#E0522A", 0.5, 0.0, 1.6), "ice_rog_a": ("#D6EEF7", 0.35), "ice_rog_b": ("#9CCBE0", 0.35),
"ice_rog_c": ("#F6FBFD", 0.45), "ice_rog_d": ("#5E94B8", 0.35), "ice_rog_e": ("#B9A7D8", 0.4),
"aster_a": ("#7F7A74", 0.95), "aster_b": ("#5A5651", 0.95), "aster_c": ("#A09A91", 0.95), "aster_d": ("#6E5F54", 0.95),
"comet_dark": ("#2B2927", 0.95), "comet_mid": ("#4B4540", 0.95), "comet_ice": ("#E9F2F7", 0.4), "comet_vent": ("#9FD0E6", 0.4, 0.0, 0.6),
# ---- props / interiors / accessories ----
"wood_light": ("#C79B6B", 0.85), "wood_dark": ("#7A5638", 0.85), "fabric_blue": ("#4F7FA0", 0.95), "fabric_coral": ("#D87560", 0.95),
"fabric_grey": ("#7D868C", 0.95), "chrome": ("#C9D0D6", 0.25, 0.9), "plastic_black": ("#25282D", 0.55), "plastic_white": ("#EEEBE4", 0.55),
"screen": ("#2B3B4D", 0.2, 0.0, 0.25), "screen_lit": ("#7FC4E8", 0.2, 0.0, 0.9), "led_green": ("#47D16C", 0.3, 0.0, 1.2),
"led_red": ("#E8453C", 0.3, 0.0, 1.2), "leather": ("#7B4F35", 0.7), "leather_dark": ("#3E2A20", 0.7), "canvas": ("#B7B08A", 0.95),
"canvas_red": ("#C9503C", 0.95), "canvas_green": ("#4F7A58", 0.95), "reflective": ("#D8E85A", 0.5, 0.0, 0.35),
"hiviz_orange": ("#F26A21", 0.7), "silver": ("#B9BFC5", 0.35, 0.8), "red_paint": ("#C93A30", 0.5, 0.2), "safety_white": ("#F2F2EE", 0.6),
"med_green": ("#3F8F6A", 0.7), "med_red": ("#D33A32", 0.6), "pot_clay": ("#B9694A", 0.9), "plant_green": ("#4F9A4F", 0.9),
"metal_gal": ("#A7B1B8", 0.4, 0.7), "metal_rust": ("#8A5A40", 0.85, 0.3), "sign_green": ("#2E7A52", 0.5), "sign_white": ("#EEF0EC", 0.5),
```

## Rules
- Silhouette first: major forms (head / body / limbs, rim / bowl / ejecta, hull / ribs / keel) must read at a distance.
- Max about 30k triangles per model (celestial hero bodies are ~20-30k; props 200-3.5k).
- No stick-figure animals, no plain-sphere planets (each has displaced craters / continents / bands), no block props, no duplicate geometry.
- Emissive only where something glows (lava, ember, screens, LEDs, lenses, beacons).
- Separate named objects for anything that moves or breaks; pivots go in the JSON.
