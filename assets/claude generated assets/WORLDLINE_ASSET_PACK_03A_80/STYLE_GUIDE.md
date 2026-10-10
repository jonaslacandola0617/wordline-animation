# Worldline 3D style guide (as applied in Pack 03A)

**Geometry:** purposeful faceted low-poly. Vehicles are lofted from cross-sections (chamfered rings) rather than boxes; hulls are lofted from keel/chine/sheer sections; aircraft fuselages are lofted ellipses with swept hexahedral wings; terrain is jittered heightfield solids or displaced icospheres; plants/trees use tapered tubes, ribbons and faceted blobs.

**Palette (base):** warm concrete `#C9BDB0`, architectural stone `#DED4C4`, asphalt `#454B50`, painted blue steel `#628797`, structural steel `#68747C`, warm timber `#A67B56`, mid foliage `#65936B`, deep foliage `#416F56`, muted coral `#D87560`, safety yellow `#E5B64D`, warm off-white `#ECE8DF`, dark rubber/trim `#292F34`. Complementary additions: emergency red/orange, school yellow, hull colours, rock/sand/soil tones, glass tints.

**Materials:** matte to low-specular flat colours, glass with partial opacity, small emissive values for lights. Distinct material groups per function (paint, glass, tyre, rim, trim, lights).

**Scale/orientation:** real-world metres, Y-up, vehicles face -Z, ground at Y = 0.

**Edges/shading:** per-face normals (faceted look); chamfered body rings and rounded tubes instead of hard primitive boxes where silhouette matters.
