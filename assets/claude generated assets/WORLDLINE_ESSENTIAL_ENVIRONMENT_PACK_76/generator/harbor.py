from lib import *
from props import put, bolts, insulator

def cleat(M, g, x, y, z, ry=0, mat='galvanized_steel', s=1.0):
    T = Model('t', 'x')
    T.box('c', mat, -0.12*s, 0, -0.04*s, 0.12*s, 0.04*s, 0.04*s, 0.01)
    T.add('c', mat, tbox(-0.2*s, 0.04*s, -0.045*s, 0.2*s, 0.11*s, 0.045*s, 0.6))
    for sx in (-1, 1): T.add('c', mat, tbox(sx*0.17*s-0.03*s, 0.0, -0.045*s, sx*0.17*s+0.03*s, 0.11*s, 0.045*s, 0.8))
    for (gg, m), p in T.groups.items(): M.add(g, m, p.rot('y', ry).move(x, y, z))

def truss_plane(M, g, mat, a, b, h, n, t=0.1, z_axis=False):
    """Warren truss in a vertical plane between bottom points a,b (3D), height h."""
    for i in range(n+1):
        p = tuple(a[k]+(b[k]-a[k])*i/n for k in range(3))
        M.beam(g, mat, p, (p[0], p[1]+h, p[2]), t*0.8, t*0.8)
    M.beam(g, mat, a, b, t, t); M.beam(g, mat, (a[0], a[1]+h, a[2]), (b[0], b[1]+h, b[2]), t, t)
    for i in range(n):
        p = tuple(a[k]+(b[k]-a[k])*i/n for k in range(3)); q = tuple(a[k]+(b[k]-a[k])*(i+1)/n for k in range(3))
        if i % 2 == 0: M.beam(g, mat, p, (q[0], q[1]+h, q[2]), t*0.7, t*0.7)
        else: M.beam(g, mat, (p[0], p[1]+h, p[2]), q, t*0.7, t*0.7)

def HARBOR_01():
    M = Model('HARBOR_01', 'harbor', 'Wooden pier module 3 x 12 m: 60 deck planks, 3 stringers, 5 cross-beams, 10 round piles with caps, edge fascia, cleats; deck top y=+1.2 above waterline y=0')
    for i in range(48):
        z = -6+i*0.25
        M.box('deck_planks', 'timber_warm' if i % 3 else 'wood_weathered', -1.5, 1.12, z+0.01, 1.5, 1.2, z+0.24, 0.006)
    for x in (-1.2, 0.0, 1.2): M.box('stringers', 'wood_weathered', x-0.06, 0.92, -6, x+0.06, 1.12, 6, 0.01)
    for k in range(5):
        z = -5.4+k*2.7
        M.box('cross_beams', 'wood_weathered', -1.6, 0.74, z-0.08, 1.6, 0.92, z+0.08, 0.012)
        for x in (-1.4, 1.4):
            M.add('piles', 'wood_weathered', cyl(0.17, 4.2, 8, -3.0, x, z, 0.15, 0.2))
            M.add('pile_caps', 'rubber_dark', cylb(0.18, 0.05, 8, 0.7, x, z, 0.01) if False else cyl(0.18, 0.04, 8, 0.7, x, z))
            M.beam('piles_brace', 'wood_weathered', (x, -0.4, z), (x*0.3, 0.8, z+0.0), 0.07, 0.07) if False else None
    for s in (-1, 1):
        M.box('fascia', 'wood_weathered', s*1.5-0.04 if s > 0 else -1.54, 0.95, -6, s*1.5+0.04 if s > 0 else -1.46, 1.3, 6, 0.01)
        M.box('curb_rail', 'timber_warm', s*1.38-0.05 if s > 0 else -1.43, 1.2, -6, s*1.38+0.05 if s > 0 else -1.33, 1.3, 6, 0.01) if False else None
        for z in (-4.5, -1.5, 1.5, 4.5): cleat(M, 'cleats', s*1.3, 1.2, z, 0 if s > 0 else 180)
    for z in (-4.5, -1.5, 1.5, 4.5): M.cn(f'mooring_z{z}', (1.3, 1.25, z), (1, 0, 0))
    M.cn('end_A', (0, 1.2, -6), (0, 0, -1), width=3.0); M.cn('end_B', (0, 1.2, 6), (0, 0, 1), width=3.0)
    for k in range(3): M.det(f'deck_planks', 'deck planks (peel individually)', (0, 1.16, 0))
    M.det('piles', 'piles', (0, 0, 0)); M.det('stringers', 'stringers', (0, 1.0, 0))
    return M

def HARBOR_02():
    M = Model('HARBOR_02', 'harbor', 'Concrete pier module 6 x 12 m: 0.6 m deck slab with chamfered curb, 8 square piers, cross-beams, rubber fenders, bollard pads, expansion joints; deck top y=+1.6')
    M.box('deck', 'concrete_weathered', -3.0, 1.0, -6, 3.0, 1.5, 6, 0.03)
    M.box('deck_topping', 'concrete_pale', -2.95, 1.5, -6, 2.95, 1.56, 6, 0.02)
    for s in (-1, 1): M.add('curb', 'concrete_pale', profile_ext([(s*2.55, 1.56), (s*3.0, 1.56), (s*3.0, 1.84), (s*2.95, 1.9), (s*2.6, 1.9), (s*2.55, 1.84)][::(1 if s > 0 else -1)], -6, 6))
    for k in (-2, 0, 2): M.box('joints', 'rubber_dark', -2.9, 1.56, k*2.0-0.03 + 2.0 if False else k*2.0+2.0-0.03, 2.9, 1.565, k*2.0+2.0+0.03) if False else None
    for z in (-4.0, 0.0, 4.0): M.box('joints', 'rubber_dark', -2.9, 1.56, z-0.025, 2.9, 1.565, z+0.025)
    for k, z in enumerate((-5.0, -1.7, 1.7, 5.0)):
        for x in (-2.0, 2.0):
            M.add('piers', 'concrete_pale', box(x-0.32, -3.0, z-0.32, x+0.32, 1.0, z+0.32, 0.05))
        M.box('cross_beams', 'concrete_weathered', -2.8, 0.4, z-0.25, 2.8, 1.0, z+0.25, 0.03)
    for s in (-1, 1):
        M.box('long_beams', 'concrete_weathered', s*2.2-0.25, 0.5, -6, s*2.2+0.25, 1.0, 6, 0.03)
        for z in (-4.0, 0.0, 4.0):
            M.add('fenders', 'rubber_dark', cylb(0.2, 1.1, 8, 0.2, s*3.0+s*0.2, z, 0.03))
            M.beam('fender_chain', 'galvanized_steel', (s*3.0, 1.7, z), (s*3.2, 1.0, z), 0.02, 0.02)
            M.box('bollard_pad', 'concrete_pale', s*2.3-0.35, 1.56, z-0.35+2.0 if False else z+1.8-0.35, s*2.3+0.35, 1.6, z+1.8+0.35, 0.01) if False else None
    for z in (-3.0, 3.0):
        for s in (-1, 1):
            M.box('bollard_pad', 'concrete_weathered', s*2.2-0.3, 1.56, z-0.3, s*2.2+0.3, 1.62, z+0.3, 0.01)
            M.add('bollard_socket', 'galvanized_steel', cylb(0.17, 0.12, 8, 1.62, s*2.2, z, 0.02))
            M.cn(f'bollard_mount_{s}_{z}', (s*2.2, 1.74, z), (0, 1, 0), mates='HARBOR_08')
    for z in (-4.0, 4.0): M.box('ladder_recess', 'rubber_dark', 2.4, 1.0, z-0.3, 3.0, 1.9, z+0.3) if False else None
    M.cn('end_A', (0, 1.56, -6), (0, 0, -1), width=6); M.cn('end_B', (0, 1.56, 6), (0, 0, 1), width=6); M.cn('seawall_edge', (3.0, 1.56, 0), (1, 0, 0), mates='HARBOR_04')
    M.det('deck', 'deck slab (sheared from piers)', (0, 1.25, 0)); M.det('piers', 'support piers', (0, -1, 0))
    return M

def HARBOR_03():
    M = Model('HARBOR_03', 'harbor', 'Floating steel/timber dock 2.4 x 6 m: 2 cylindrical pontoons, steel frame, timber deck, side rails, cleats, end hinge plates; deck top y=+0.55')
    for x in (-0.75, 0.75):
        M.add('pontoons', 'safety_orange' if False else 'paint_blue', cylb(0.45, 5.6, 12, 0, 0, 0, 0.06).rot('x', 90).move(x, -0.0, -2.8) if False else tube((x, 0.0, -2.8), (x, 0.0, 2.8), 0.45, 12))
        for z in (-2.8, 2.8): M.add('pontoon_caps', 'paint_blue', lathe([(0.45, 0), (0.35, 0.12), (0.15, 0.2)], 12).rot('x', 90 if z > 0 else -90).move(x, 0, z) if False else cyl(0.45, 0.01, 12).rot('x', 90).move(x, 0.0, z+0.0))
    for z in (-2.4, -0.8, 0.8, 2.4):
        M.box('frame', 'metal_painted_grey', -1.2, 0.3, z-0.08, 1.2, 0.45, z+0.08, 0.015)
        for x in (-0.75, 0.75): M.box('straps', 'galvanized_steel', x-0.5, -0.45+0.0 if False else -0.4, z-0.08, x+0.5, 0.45, z+0.08, 0.015) if False else M.box('straps', 'galvanized_steel', x-0.13, 0.28, z-0.1, x+0.13, 0.46, z+0.1)
    for s in (-1, 1): M.box('frame', 'metal_painted_grey', s*1.2-0.05 if s > 0 else -1.25, 0.3, -3.0, s*1.2+0.05 if s > 0 else -1.15, 0.45, 3.0, 0.015)
    for i in range(24): M.box('deck', 'timber_warm' if i % 2 else 'wood_weathered', -1.2, 0.45, -3.0+i*0.25+0.01, 1.2, 0.55, -3.0+i*0.25+0.24, 0.006)
    for s in (-1, 1):
        for z in (-2.9, -1.0, 1.0, 2.9):
            M.beam('rail_posts', 'safety_yellow', (s*1.15, 0.55, z), (s*1.15, 1.2, z), 0.06, 0.06)
        M.beam('rail', 'safety_yellow', (s*1.15, 1.2, -2.9), (s*1.15, 1.2, 2.9), 0.05, 0.05); M.beam('rail', 'safety_yellow', (s*1.15, 0.88, -2.9), (s*1.15, 0.88, 2.9), 0.04, 0.04)
        for z in (-1.8, 0.0, 1.8): cleat(M, 'cleats', s*1.05, 0.55, z, 90 if s > 0 else 270)
    for z in (-3.0, 3.0):
        for x in (-0.7, 0.7):
            M.box('hinge_plate', 'galvanized_steel', x-0.2, 0.45, z-0.1 if z < 0 else z, x+0.2, 0.52, z if z < 0 else z+0.1, 0.01) if False else M.box('hinge_plate', 'galvanized_steel', x-0.2, 0.4, z-0.12, x+0.2, 0.5, z+0.12, 0.01)
            M.add('hinge_pin', 'brushed_metal', tube((x-0.18, 0.5, z), (x+0.18, 0.5, z), 0.04, 8))
    M.cn('end_A', (0, 0.55, -3.0), (0, 0, -1), width=2.4); M.cn('end_B', (0, 0.55, 3.0), (0, 0, 1), width=2.4)
    M.det('deck', 'deck planks', (0, 0.5, 0)); M.det('pontoons', 'pontoons', (0, 0, 0))
    return M

def HARBOR_04():
    M = Model('HARBOR_04', 'harbor', 'Concrete seawall 12 m: recurved water-facing profile (+X side), 3 structural sections with joints, toe apron, top walkway edge, parapet, rings & ladder recess; walkway y=+2.2')
    prof = [(-1.6, -2.0), (1.9, -2.0), (1.9, -1.5), (1.4, -1.45), (0.9, -0.9), (0.55, -0.1), (0.35, 0.8), (0.4, 1.6), (0.65, 2.1), (1.0, 2.35), (1.0, 2.5), (0.6, 2.5), (0.5, 2.9), (0.2, 2.9), (0.15, 2.2), (-1.6, 2.2)]
    for k in range(3):
        z0 = -6+4*k+0.02; z1 = z0+3.96
        M.add(f'section_{k+1}', 'concrete_weathered' if k % 2 else 'concrete_pale', profile_ext(prof, z0, z1))
        for y in (0.2, 0.7, 1.2, 1.7):
            xs = {0.2: 0.45, 0.7: 0.36, 1.2: 0.35, 1.7: 0.46}[y]
            M.box(f'section_{k+1}_courses', 'concrete_weathered', xs, y, z0+0.02, xs+0.03, y+0.03, z1-0.02)
        M.box(f'section_{k+1}_cap', 'concrete_pale', -1.2, 2.2, z0, 0.2, 2.25, z1)
        M.add(f'section_{k+1}_ring', 'brushed_metal', tube((0.62, 1.2, z0+2), (0.7, 1.2, z0+2), 0.03, 6) if False else cyl(0.06, 0.05, 8, 0, 0, 0).rot('z', -90).move(0.36, 1.0, z0+2.0))
    M.box('joints', 'rubber_dark', 0.2, -1.5, -2.03, 1.0, 2.5, -1.97) if False else None
    for z in (-2.0, 2.0): M.box('joints', 'rubber_dark', 0.34, -0.2, z-0.02, 0.66, 2.2, z+0.02) if False else M.box('joints', 'rubber_dark', 0.2, -1.4, z-0.02, 0.9, 2.18, z+0.02)
    M.box('toe_apron', 'dusty_stone', 1.4, -2.2, -6, 2.4, -1.5, 6, 0.04)
    for z in (-5, -1, 3): M.box('ladder_recess', 'rubber_dark', 0.3, 0.0, z, 0.52, 2.2, z+0.5) if False else None
    for z in (-3.5, 3.5):
        for i in range(8): M.add('ladder_rung', 'galvanized_steel', tube((0.55-0.0, -1.0+i*0.4, z-0.2), (0.55, -1.0+i*0.4, z+0.2), 0.02, 5) if False else tube((0.44-0.0+0.0, -1.0+i*0.4, z-0.2), (0.44, -1.0+i*0.4, z+0.2), 0.02, 5))
    for z in (-5.5, -1.5, 2.5, 5.5): M.box('railing_sockets', 'galvanized_steel', 0.3, 2.9, z-0.07, 0.4, 2.93, z+0.07, 0.01) if False else M.add('railing_sockets', 'galvanized_steel', cylb(0.07, 0.05, 8, 2.9, 0.35, z, 0.01))
    for z in (-5.5, -1.5, 2.5, 5.5): M.cn(f'railing_mount_z{z}', (0.35, 2.95, z), (0, 1, 0), mates='HARBOR_12')
    M.cn('end_A', (0, 0, -6), (0, 0, -1)); M.cn('end_B', (0, 0, 6), (0, 0, 1)); M.cn('road_edge', (-1.6, 2.2, 0), (-1, 0, 0), mates='ROAD_09')
    M.det('section_1', 'wall section 1', (0, 0, -4)); M.det('section_2', 'wall section 2', (0, 0, 0)); M.det('section_3', 'wall section 3', (0, 0, 4))
    return M

def tetrapod(r=0.28, L=0.85, seg=5):
    P = Part()
    dirs = [(0.943, -0.333, 0), (-0.471, -0.333, 0.816), (-0.471, -0.333, -0.816), (0, 1.0, 0)]
    for d in dirs:
        P = P + tube((0, 0, 0), mul(d, L), r, seg, r*0.62)
    P = P + cyl(r*1.1, 0.02, seg)   # tiny hub plate avoids z-fighting
    return P

def HARBOR_05():
    M = Model('HARBOR_05', 'harbor', 'Rubble-mound breakwater 12 m: quarry-rock core with trapezoid profile + 3 courses of interlocking 4-legged concrete armour units (tetrapods)')
    prof = [(-4.5, 0), (4.5, 0), (2.0, 3.0), (-2.0, 3.0)]
    M.add('core', 'dusty_stone', profile_ext(prof, -6, 6))
    rnd = random.Random(7)
    for i in range(14):                                # surface boulders on core
        z = -5.5+i*0.8+rnd.uniform(-0.2, 0.2)
        for sx in (-1, 1):
            x = sx*rnd.uniform(3.3, 4.2); y = 0.15
            M.add('rocks', 'dusty_stone', rock(x, y, z, 0.5, 0.35, 0.5, i*3+sx, 6))
    rows = [(-3.6, 0.55), (-2.7, 1.25), (-1.8, 1.95), (-0.9, 2.6), (0.0, 3.05), (0.9, 2.6), (1.8, 1.95), (2.7, 1.25), (3.6, 0.55)]
    k = 0
    for x, y in rows:
        n = 6 if abs(x) > 0.5 else 5
        for i in range(n):
            z = -5.0+i*(10.0/(n-1))+(0.5 if (rows.index((x, y)) % 2) else 0)*0.8 - (0.4 if rows.index((x, y)) % 2 else 0)
            if abs(z) > 5.6: continue
            T = tetrapod(0.4, 1.25).rot('y', rnd.uniform(0, 360)).rot('x', rnd.uniform(-35, 35)).rot('z', rnd.uniform(-35, 35)).move(x, y+0.25, z)
            M.add(f'armour_row{rows.index((x, y))+1}', 'broken_concrete' if k % 2 else 'concrete_pale', T); k += 1
    M.cn('end_A', (0, 0, -6), (0, 0, -1)); M.cn('end_B', (0, 0, 6), (0, 0, 1))
    M.det('armour_row5', 'crest armour units (can be dislodged individually)', (0, 3.1, 0))
    return M

def rock(cx, cy, cz, rx, ry, rz, seed, seg=6):
    rnd = random.Random(seed); rings = []
    levels = [(0.0, 0.0), (0.45, 0.8), (0.85, 1.0), (1.0, 0.55)] if False else [(-0.9, 0.55), (-0.3, 1.0), (0.4, 0.95), (0.95, 0.5)]
    for t, k in levels:
        rings.append([(cx+rx*k*(0.75+0.3*rnd.random())*math.cos(2*math.pi*i/seg+0.4*t), cy+ry*t+rnd.uniform(-0.04, 0.04)*ry, cz+rz*k*(0.75+0.3*rnd.random())*math.sin(2*math.pi*i/seg+0.4*t)) for i in range(seg)])
    return loft(rings)

def HARBOR_06():
    M = Model('HARBOR_06', 'harbor', 'Lighthouse 20 m: stone plinth + steps, tapered banded tower (red/white), arched door, 3 window levels, gallery with railing, glazed lantern room with mullions, dome, lightning rod')
    M.add('plinth', 'dusty_stone', cylb(4.2, 1.0, 12, 0, b=0.15))
    for i in range(3): M.add('steps', 'dusty_stone', cylb(3.4-i*0.0, 0.2, 12, 0, 0, 0, 0.0) if False else cyl(4.2+0.55*(3-i)/3, 0.0, 12) if False else cyl(4.2+0.6-i*0.2, 0.18, 12, i*0.0) if False else merge([]))
    for i in range(3): M.add('steps', 'concrete_weathered', box(-0.9+0.0, 0.0+i*0.0, 3.2-i*0.0, 0.9, 0.0, 3.2, 0.0)) if False else None
    for i in range(4): M.add('steps', 'concrete_weathered', box(-1.0, i*0.25, 3.6+(3-i)*0.3-0.0 if False else 3.0+(3-i)*0.3, 1.0, i*0.25+0.25, 4.5, 0.01) if False else box(-1.0, 0.0, 3.9+0.3*(3-i)-0.3*3+0.9 if False else 3.0+0.3*(3-i)+0.0, 1.0, 0.25*(i+1) if False else 0.25*(i+1), 4.2, 0.01))
    bands = [('white_paint', 0, 3.0), ('traffic_red', 3.0, 6.5), ('white_paint', 6.5, 10.0), ('traffic_red', 10.0, 13.5), ('white_paint', 13.5, 17.0)]
    r = lambda y: 3.0-0.9*(y/17.0)
    for m, a, b in bands:
        M.add('tower_'+m, m, lathe([(r(a), 1.0+a), (r(b), 1.0+b)], 12, 0, 0, math.pi/12))
        M.add('tower_band_trim', 'concrete_pale', lathe([(r(b)+0.0, 1.0+b-0.05), (r(b)+0.08, 1.0+b-0.0), (r(b)+0.08, 1.0+b+0.1), (r(b), 1.0+b+0.1)], 12, 0, 0, math.pi/12)) if m == 'white_paint' and b < 17 else None
    # door
    M.box('door_frame', 'concrete_pale', -0.65, 1.0, 2.5, 0.65, 2.9, 3.2, 0.05) if False else None
    M.box('door', 'wood_weathered', -0.5, 1.0, 2.88, 0.5, 2.55, 2.99, 0.02) if False else M.box('door_frame', 'concrete_pale', -0.7, 1.0, 2.7, 0.7, 3.3, 3.05, 0.04)
    M.box('door', 'wood_weathered', -0.5, 1.0, 3.0, 0.5, 3.1, 3.1, 0.02)
    M.add('door_arch', 'wood_weathered', cyl(0.5, 0.1, 10, 3.1, 0, 3.0).rot('x', 90, (0, 3.1, 3.0)) if False else cyl(0.5, 0.1, 10, 0, 0, 0).rot('x', 90).move(0, 3.1, 3.0))
    for y, rr in ((6.5, 2.4), (10.5, 2.15), (14.5, 1.85)):
        for a in (0, 90, 180, 270):
            T = Model('t', 'x'); rad = r(y-1.0)
            T.box('window_frame', 'concrete_pale', -0.3, y-0.45, rad-0.04, 0.3, y+0.45, rad+0.1, 0.03)
            T.box('window', 'glass_tinted', -0.2, y-0.35, rad+0.1, 0.2, y+0.35, rad+0.13)
            T.box('window_sill', 'concrete_weathered', -0.38, y-0.5, rad+0.02, 0.38, y-0.43, rad+0.18, 0.01)
            for (g, m), p in T.groups.items(): M.add(g, m, p.rot('y', a+(0 if a else 0)))
    top = 1.0+17.0
    M.add('gallery_floor', 'concrete_pale', cylb(2.6, 0.25, 12, top, b=0.05)); M.add('gallery_brackets', 'concrete_weathered', lathe([(2.1, top), (2.6, top), (2.6, top-0.4)], 12) if False else cyl(2.0, 0.0, 12) if False else lathe([(2.0, top-0.5), (2.55, top)], 12))
    for i in range(16):
        a = 2*math.pi*i/16
        M.add('railing_posts', 'brushed_metal', tube((2.45*math.cos(a), top+0.25, 2.45*math.sin(a)), (2.45*math.cos(a), top+1.2, 2.45*math.sin(a)), 0.035, 5))
    for y in (top+1.15, top+0.75): M.add('railing_rails', 'brushed_metal', merge([tube((2.45*math.cos(2*math.pi*i/16), y, 2.45*math.sin(2*math.pi*i/16)), (2.45*math.cos(2*math.pi*(i+1)/16), y, 2.45*math.sin(2*math.pi*(i+1)/16)), 0.03, 5) for i in range(16)]))
    M.add('lantern_base', 'traffic_red', cylb(1.6, 0.5, 12, top+0.25, b=0.05))
    ly = top+0.75
    M.add('lantern_glass', 'glass_tinted', cyl(1.5, 1.7, 12, ly))
    for i in range(12): 
        a = 2*math.pi*i/12+math.pi/12
        M.add('lantern_mullions', 'brushed_metal', tube((1.52*math.cos(a), ly, 1.52*math.sin(a)), (1.52*math.cos(a), ly+1.7, 1.52*math.sin(a)), 0.045, 5))
    M.add('lantern_ring', 'brushed_metal', cylb(1.58, 0.12, 12, ly+1.7, b=0.02)); M.add('lantern_ring', 'brushed_metal', cylb(1.58, 0.12, 12, ly-0.1, b=0.02))
    M.add('lamp', 'lamp_emissive', cyl(0.4, 0.8, 8, ly+0.45)); M.add('lamp_lens', 'glass_tinted', cyl(0.5, 0.0, 8) if False else cyl(0.55, 0.3, 8, ly+0.3, 0, 0, 0.3) if False else merge([]))
    M.add('dome', 'traffic_red', lathe([(1.7, ly+1.82), (1.5, ly+2.1), (1.0, ly+2.45), (0.4, ly+2.75), (0.01, ly+2.85)], 12))
    M.add('vane', 'brushed_metal', tube((0, ly+2.8, 0), (0, ly+4.2, 0), 0.05, 6, 0.015)); M.add('vane', 'brushed_metal', sphere_like(0, ly+4.3, 0, 0.1))
    M.cn('base', (0, 0, 0), (0, -1, 0)); M.cn('light_origin', (0, ly+0.85, 0), (0, 0, 1), emissive='lamp_emissive')
    M.det('dome', 'lantern dome + vane', (0, ly+1.8, 0)); M.det('lantern_glass', 'lantern glazing', (0, ly+0.8, 0))
    return M

def sphere_like(cx, cy, cz, r, seg=6):
    return lathe([(0.01, -r), (r*0.8, -r*0.6), (r, 0), (r*0.8, r*0.6), (0.01, r)], seg, cx, cz).move(0, cy, 0)

def HARBOR_07():
    M = Model('HARBOR_07', 'harbor', 'Harbour jib crane 22 m: rail-mounted portal base with 4 legs, slewing house + cab + counterweight, A-frame, articulated lattice boom + jib, hoist/luffing ropes, winch house, hook block; groups: base/house/boom/jib/ropes/hook')
    for x in (-1.0, 1.0):
        M.box('rails', 'rust_metal', x*3.5-0.1, 0, -4.2, x*3.5+0.1, 0.18, 4.2, 0.02) if False else None
    for s in (-1, 1):
        M.box('rail', 'rust_metal', s*3.2-0.12, 0, -4.2, s*3.2+0.12, 0.16, 4.2, 0.02)
        for z in (-3.0, 3.0): M.box('bogie', 'metal_painted_grey', s*3.2-0.35, 0.16, z-0.5, s*3.2+0.35, 0.65, z+0.5, 0.05)
        for z in (-3.0, 3.0):
            for dz in (-0.3, 0.3): M.add('wheels', 'rubber_dark', cylb(0.2, 0.24, 10, 0, 0, 0, 0.02).rot('x', 90).rot('z', 0).move(s*3.2, 0.36, z+dz) if False else tube((s*3.2-0.12, 0.36, z+dz), (s*3.2+0.12, 0.36, z+dz), 0.2, 10))
    P = [(-3.2, 0.65, -3.0), (3.2, 0.65, -3.0), (3.2, 0.65, 3.0), (-3.2, 0.65, 3.0)]
    for (x, y, z) in P: M.beam('legs', 'safety_yellow', (x, y, z), (x*0.8, 6.5, z*0.8), 0.45, 0.45)
    for i in range(4):
        a = P[i]; b = P[(i+1) % 4]
        M.beam('sill', 'safety_yellow', a, b, 0.4, 0.4)
        a2 = (a[0]*0.8, 6.5, a[2]*0.8); b2 = (b[0]*0.8, 6.5, b[2]*0.8)
        M.beam('portal_top', 'safety_yellow', a2, b2, 0.4, 0.4)
        M.beam('leg_brace', 'safety_yellow', (a[0]*0.95, 1.2, a[2]*0.95), (b[0]*0.82, 5.9, b[2]*0.82), 0.16, 0.16)
        M.beam('leg_brace', 'safety_yellow', (b[0]*0.95, 1.2, b[2]*0.95), (a[0]*0.82, 5.9, a[2]*0.82), 0.16, 0.16)
    M.add('slew_ring', 'metal_painted_grey', cylb(2.2, 0.5, 14, 6.5, b=0.08))
    # house (slewing, group 'house'), rotates about (0,7,0)
    M.box('house', 'safety_yellow', -1.7, 7.0, -2.8, 1.7, 9.2, 1.4, 0.12)
    M.box('house', 'metal_painted_grey', -1.75, 9.2, -2.8, 1.75, 9.35, 1.4, 0.05)
    M.box('cab', 'paint_navy', -1.0, 7.8, 1.4, 0.4, 9.2, 2.4, 0.08); M.box('cab_window', 'glass_tinted', -0.9, 8.2, 2.4, 0.3, 9.0, 2.43, 0.0)
    M.box('counterweight', 'concrete_weathered', -1.5, 7.0, -4.2, 1.5, 8.8, -2.8, 0.08)
    for i in range(5): M.box('counterweight', 'rust_metal', -1.5+i*0.6+0.02, 7.0, -4.22, -0.92+i*0.6, 8.8, -4.2) if False else None
    for y in (7.6, 8.4): M.box('house_vents', 'rubber_dark', 1.7, y, -2.4, 1.73, y+0.15, 0.8)
    M.box('winch_house', 'safety_yellow', -1.0, 9.35, -2.5, 1.0, 10.4, -0.4, 0.08)
    M.add('winch_drum', 'brushed_metal', tube((-0.9, 10.9, -1.5), (0.9, 10.9, -1.5), 0.35, 12)) if False else M.add('winch_drum', 'brushed_metal', tube((-0.7, 9.9, -1.45), (0.7, 9.9, -1.45), 0.42, 12))
    # A-frame
    for s in (-1, 1): M.beam('a_frame', 'safety_yellow', (s*1.2, 9.2, -0.6), (s*0.3, 13.2, -1.6), 0.25, 0.25)
    M.beam('a_frame', 'safety_yellow', (-0.5, 13.0, -1.6), (0.5, 13.0, -1.6), 0.25, 0.25)
    M.add('a_frame_sheave', 'brushed_metal', tube((-0.35, 13.5, -1.6), (0.35, 13.5, -1.6), 0.25, 10))
    # boom (lattice) from (0,9.0,1.0) rising to tip
    b0 = (0.0, 9.0, 1.0); b1 = (0.0, 16.0, 10.5)
    d = norm(sub(b1, b0)); L = math.dist(b0, b1); n = 8
    up = (0, math.cos(0.0), 0)
    perp = norm(cross((1, 0, 0), d))                   # in-plane normal
    for s in (-1, 1):
        for sg in (-1, 1):
            a = add(b0, (s*0.55, 0, 0)); a = add(a, mul(perp, sg*0.45*0.5*0+sg*0.0)) if False else a
    for s in (-1, 1):
        for sg in (-1, 1):
            w0 = 0.7; w1 = 0.3
            M.beam('boom_chord', 'safety_yellow', add(b0, (s*w0, 0, 0)) if sg > 0 else add(add(b0, (s*w0, 0, 0)), mul(perp, -0.9)), add(b1, (s*w1, 0, 0)) if sg > 0 else add(add(b1, (s*w1, 0, 0)), mul(perp, -0.5)), 0.14, 0.14)
    for i in range(n):
        t0 = i/n; t1 = (i+1)/n
        for s in (-1, 1):
            a = add(add(b0, mul(sub(b1, b0), t0)), (s*(0.7-0.4*t0), 0, 0)); b = add(add(b0, mul(sub(b1, b0), t1)), (s*(0.7-0.4*t1), 0, 0))
            a2 = add(a, mul(perp, -(0.9-0.4*t0))); b2 = add(b, mul(perp, -(0.9-0.4*t1)))
            M.beam('boom_web', 'safety_yellow', a, b2 if i % 2 == 0 else a2, 0.07, 0.07) if False else (M.beam('boom_web', 'safety_yellow', a, b2, 0.07, 0.07) if i % 2 == 0 else M.beam('boom_web', 'safety_yellow', a2, b, 0.07, 0.07))
        a = add(b0, mul(sub(b1, b0), t0)); 
        M.beam('boom_web', 'safety_yellow', add(a, (-(0.7-0.4*t0), 0, 0)), add(a, ((0.7-0.4*t0), 0, 0)), 0.07, 0.07)
    # jib
    j1 = add(b1, (0, 3.0, 4.2)) if False else (0.0, 15.2, 14.6)
    M.beam('jib', 'safety_yellow', (0.0, 16.0, 10.5), j1, 0.4, 0.28); M.beam('jib', 'safety_yellow', (0.0, 15.2, 10.5), (0.0, 14.4, 14.4), 0.2, 0.2) if False else None
    M.add('jib_pin', 'brushed_metal', tube((-0.45, 16.0, 10.5), (0.45, 16.0, 10.5), 0.14, 8))
    M.add('jib_sheave', 'brushed_metal', tube((-0.2, 15.2, 14.7), (0.2, 15.2, 14.7), 0.28, 10))
    # ropes
    for s in (-0.25, 0.25): M.add('ropes', 'cable_black', tube((s, 13.5, -1.6), (s*0.9, 16.0, 10.5), 0.03, 4))
    M.add('ropes', 'cable_black', tube((0.0, 9.9, 1.45), (0.0, 15.2, 14.7), 0.02, 4)) if False else None
    M.add('ropes', 'cable_black', tube((-0.1, 10.3, -1.0), (-0.1, 15.5, 14.8), 0.02, 4)) if False else None
    M.add('ropes', 'cable_black', tube((0.0, 15.2, 14.9), (0.0, 7.0, 14.9), 0.025, 4))
    M.add('ropes', 'cable_black', tube((0.0, 9.9, -1.1), (0.0, 15.6, 14.6), 0.02, 4))
    # hook block
    M.box('hook_block', 'safety_orange', -0.3, 6.1, 14.6, 0.3, 7.0, 15.2, 0.06)
    M.add('hook', 'brushed_metal', merge([tube((0, 6.1, 14.9), (0, 5.55, 14.9), 0.07, 8), tube((0, 5.55, 14.9), (0.25, 5.2, 14.9), 0.07, 8), tube((0.25, 5.2, 14.9), (0.1, 4.9, 14.9), 0.06, 8), tube((0.1, 4.9, 14.9), (-0.18, 5.05, 14.9), 0.05, 8)]))
    M.cn('rail_centre', (0, 0, 0), (0, -1, 0)); M.cn('hook_point', (0.05, 5.0, 14.9), (0, -1, 0))
    M.det('house', 'slewing house', (0, 7.0, 0)); M.det('boom_chord', 'boom (separately addressable)', (0, 9.0, 1.0)); M.det('jib', 'jib', (0, 16, 10.5)); M.det('hook', 'hook block', (0, 6.5, 14.9)); M.det('legs', 'portal legs', (0, 3, 0))
    return M

def HARBOR_08():
    M = Model('HARBOR_08', 'harbor', 'Double-bitt mooring bollard 0.9 m: oval cast base plate with 8 anchor bolts, twin tapered posts with flared heads, cross web, rope wear grooves')
    base = [(0.55*math.cos(math.radians(a)) if abs(math.cos(math.radians(a))) < 0.99 else 0.55*math.cos(math.radians(a)), 0.32*math.sin(math.radians(a))) for a in range(0, 360, 30)]
    M.ext('base_plate', 'rust_metal', [(0.62*math.cos(math.radians(a)), 0.38*math.sin(math.radians(a))) for a in range(0, 360, 20)], 0, 0.09, [(0.58*math.cos(math.radians(a)), 0.34*math.sin(math.radians(a))) for a in range(0, 360, 20)])
    bolts(M, 'anchor_bolts', [(0.5*math.cos(math.radians(a)), 0.28*math.sin(math.radians(a))) for a in range(0, 360, 45)], 0.09, 0.045, 0.06)
    for x in (-0.3, 0.3):
        M.add('post', 'rubber_dark' if False else 'metal_painted_grey', lathe([(0.22, 0.09), (0.19, 0.2), (0.17, 0.5), (0.2, 0.62), (0.27, 0.72), (0.27, 0.8), (0.2, 0.88), (0.01, 0.9)], 12, x, 0))
        M.add('groove', 'rust_metal', lathe([(0.175, 0.4), (0.18, 0.44), (0.175, 0.48)], 12, x, 0))
    M.box('web', 'metal_painted_grey', -0.3, 0.09, -0.07, 0.3, 0.42, 0.07, 0.02)
    M.cn('rope_loop', (0, 0.6, 0), (0, 1, 0)); M.cn('ground', (0, 0, 0), (0, -1, 0))
    return M

def HARBOR_09():
    M = Model('HARBOR_09', 'harbor', 'Navigation buoy 4.5 m: banded float with fenders ring, keel weight, 4-leg tower, emissive lantern, radar reflector, topmark, mooring eye; origin at waterline')
    M.add('float_red', 'traffic_red', lathe([(0.9, -0.5), (1.1, -0.15), (1.1, 0.35)], 12))
    M.add('float_white', 'white_paint', lathe([(1.1, 0.35), (1.1, 0.65)], 12)) if False else None
    M.add('float_deck', 'traffic_red', lathe([(1.1, 0.35), (0.95, 0.65), (0.55, 0.8)], 12))
    M.add('fender_ring', 'rubber_dark', lathe([(1.12, -0.1), (1.2, -0.05), (1.2, 0.1), (1.12, 0.15)], 12))
    M.add('keel', 'rust_metal', lathe([(0.9, -0.5), (0.6, -1.2), (0.25, -2.0)], 10)); M.add('keel', 'rust_metal', cyl(0.25, 0.4, 10, -2.4, r1=0.12) if False else cyl(0.12, 0.5, 8, -2.5))
    M.add('mooring_eye', 'galvanized_steel', merge([tube((-0.1, -2.6, 0), (-0.1, -2.9, 0), 0.03, 6), tube((0.1, -2.6, 0), (0.1, -2.9, 0), 0.03, 6), tube((-0.1, -2.9, 0), (0.1, -2.9, 0), 0.03, 6)]))
    for a in (45, 135, 225, 315):
        c = math.cos(math.radians(a)); s = math.sin(math.radians(a))
        M.beam('tower', 'metal_painted_grey', (0.7*c, 0.75, 0.7*s), (0.2*c, 3.0, 0.2*s), 0.07, 0.07)
    for y, k in ((1.5, 0.52), (2.3, 0.37)):
        for i in range(4):
            a1 = math.radians(45+90*i); a2 = math.radians(45+90*(i+1))
            M.beam('tower_ring', 'metal_painted_grey', (k*math.cos(a1), y, k*math.sin(a1)), (k*math.cos(a2), y, k*math.sin(a2)), 0.04, 0.04)
    M.add('lantern', 'lamp_emissive', cylb(0.18, 0.4, 8, 3.05, b=0.03)); M.add('lantern_cap', 'metal_painted_grey', lathe([(0.2, 3.45), (0.12, 3.55), (0.02, 3.6)], 8)); M.add('lantern_base', 'metal_painted_grey', cylb(0.22, 0.05, 8, 3.0, b=0.01))
    M.add('topmark', 'traffic_red', merge([tube((0, 3.6, 0), (0, 4.0, 0), 0.03, 5), tbox(-0.22, 4.0, -0.02, 0.22, 4.35, 0.02, 0.1) if False else box(-0.2, 4.0, -0.02, 0.2, 4.4, 0.02)]))
    for a in (0, 90): M.add('radar_reflector', 'brushed_metal', box(-0.2, 0.0, -0.01, 0.2, 0.4, 0.01).rot('y', a).move(0, 2.55, 0)) if False else M.add('radar_reflector', 'brushed_metal', box(-0.25, 2.0, -0.012, 0.25, 2.5, 0.012).rot('y', a))
    M.cn('mooring_point', (0, -2.9, 0), (0, -1, 0)); M.det('lantern', 'lantern', (0, 3.2, 0))
    return M

def HARBOR_10():
    M = Model('HARBOR_10', 'harbor', 'ISO 40-ft shipping container 12.19 x 2.44 x 2.59 m: corrugated side walls + roof, 8 corner castings, top/bottom rails, double doors with 4 locking bars + cam handles, forklift pockets')
    Lh = 6.095; W = 1.22; Hh = 2.59
    def corr_poly(x, sgn, n):
        pts = []; step = 12.19/n
        for i in range(n):
            z = -Lh+i*step
            pts += [(x, z+0.02), (x+sgn*0.0, z+step*0.25), (x+sgn*0.06, z+step*0.4), (x+sgn*0.06, z+step*0.6), (x, z+step*0.75)] if False else [(x, z), (x+sgn*0.06, z+step*0.3), (x+sgn*0.06, z+step*0.5), (x, z+step*0.8)]
        return pts
    for s in (-1, 1):
        xo = s*(W-0.06)
        poly = [(xo+s*0.0+(0.0), z) for _, z in []]
        n = 48; step = 12.19/n; pts = []; 
        for i in range(n):
            z = -Lh+i*step
            pts += [(s*(W-0.06), z), (s*(W-0.0), z+step*0.25), (s*(W-0.0), z+step*0.5), (s*(W-0.06), z+step*0.75)]
        inner = [(s*(W-0.09), -Lh+12.19), (s*(W-0.09), -Lh)]
        poly = pts + inner
        M.add('side_wall', 'container_blue', ext(poly, 0.14, Hh-0.14))
    M.box('floor', 'wood_weathered', -W+0.05, 0.1, -Lh, W-0.05, 0.18, Lh, 0.0)
    for z in [-Lh+0.4+0.5*i for i in range(24)]: M.box('floor_beams', 'rust_metal', -W, 0.0, z, W, 0.1, z+0.1) if False else None
    # roof corrugation (profile extruded along z)
    pr = [(-W+0.1, Hh-0.14)]
    n = 20; w = (2*W-0.2)/n
    for i in range(n): x = -W+0.1+i*w; pr += [(x, Hh-0.14), (x+w*0.25, Hh-0.07), (x+w*0.5, Hh-0.07), (x+w*0.75, Hh-0.14)]
    pr += [(W-0.1, Hh-0.14), (W-0.1, Hh-0.2), (-W+0.1, Hh-0.2)]
    M.add('roof', 'container_blue', profile_ext(pr, -Lh+0.2, Lh-0.2))
    # rails
    for s in (-1, 1):
        M.box('top_rail', 'container_blue', s*W-0.07 if s > 0 else -W-0.07+0.0, Hh-0.14, -Lh, s*W+0.07 if s > 0 else -W+0.07, Hh, Lh, 0.015) if False else M.box('top_rail', 'container_blue', min(s*(W-0.12), s*(W+0.02)), Hh-0.16, -Lh, max(s*(W-0.12), s*(W+0.02)), Hh, Lh, 0.015)
        M.box('bottom_rail', 'container_blue', min(s*(W-0.12), s*(W+0.02)), 0.0, -Lh, max(s*(W-0.12), s*(W+0.02)), 0.16, Lh, 0.015)
        for z in (-3.0, 3.0): M.box('forklift_pocket', 'rust_metal', min(s*(W-0.12), s*(W+0.02)), 0.02, z-0.2, max(s*(W-0.12), s*(W+0.02)), 0.14, z+0.2) if False else None
    for z in (-Lh, Lh-0.2): 
        M.box('end_header', 'container_blue', -W, Hh-0.16, z, W, Hh, z+0.2, 0.015); M.box('end_sill', 'container_blue', -W, 0.0, z, W, 0.16, z+0.2, 0.015)
    # corner castings
    for sx in (-1, 1):
        for sz in (-1, 1):
            for y in (0.0, Hh-0.16):
                x0, x1 = sorted((sx*(W-0.18), sx*(W+0.03))); z0, z1 = sorted((sz*(Lh-0.2), sz*(Lh+0.03)))
                M.box('corner_castings', 'rust_metal' if False else 'metal_painted_grey', x0, y, z0, x1, y+0.16, z1, 0.02)
                M.box('corner_slot', 'rubber_dark', x0+0.05, y+0.05, z0 if sz < 0 else z1-0.0, x1-0.05, y+0.11, z0-0.01 if sz < 0 else z1+0.005) if False else None
    # front (door) end at +z, back end at -z
    M.box('back_panel', 'container_blue', -W+0.05, 0.16, -Lh, W-0.05, Hh-0.16, -Lh+0.1, 0.0) if False else None
    for i in range(10): M.box('back_panel', 'container_blue', -W+0.1+i*(2*W-0.2)/10, 0.16, -Lh+0.02, -W+0.1+i*(2*W-0.2)/10+0.14, Hh-0.16, -Lh+0.1)
    M.box('back_panel_core', 'container_blue', -W+0.1, 0.16, -Lh+0.0, W-0.1, Hh-0.16, -Lh+0.05)
    for s in (-1, 1):
        x0, x1 = (0.01, W-0.1) if s > 0 else (-W+0.1, -0.01)
        M.box('door_leaf', 'container_blue', x0, 0.16, Lh-0.12, x1, Hh-0.16, Lh-0.02, 0.01)
        for i in range(5):
            xx = x0+0.08+i*(x1-x0-0.16)/4.0 if False else x0+0.1+i*(x1-x0-0.2)/4
            M.box('door_ribs', 'container_blue', xx-0.06, 0.2, Lh-0.02, xx+0.06, Hh-0.2, Lh+0.03, 0.01)
        for k in (0.45, 0.75) if False else (0.3, 0.8):
            xb = (x0+x1)/2+ (0.18*s if False else 0) 
        for xb in (x0+0.25, x1-0.25):
            M.add('locking_bars', 'galvanized_steel', tube((xb, 0.2, Lh+0.05), (xb, Hh-0.2, Lh+0.05), 0.022, 6))
            M.box('cam_handle', 'galvanized_steel', xb-0.04, 1.2, Lh+0.03, xb+0.04, 1.34, Lh+0.14, 0.01)
            for y in (0.4, Hh-0.4): M.box('bar_guides', 'galvanized_steel', xb-0.04, y-0.04, Lh+0.02, xb+0.04, y+0.04, Lh+0.08)
        for y in (0.5, 1.3, 2.1): M.add('hinges', 'galvanized_steel', cyl(0.025, 0.2, 6, y, s*(W-0.07), Lh+0.0))
    M.box('door_seal', 'rubber_dark', -0.01, 0.16, Lh-0.12, 0.01, Hh-0.16, Lh-0.02)
    M.box('data_plate', 'sign_white', 0.4, 1.4, Lh+0.03, 0.9, 1.7, Lh+0.035)
    M.cn('lift_points', (0, Hh, 0), (0, 1, 0), note='4 top corner castings'); M.cn('stack_above', (0, Hh, 0), (0, 1, 0), mates='HARBOR_10'); M.cn('door_end', (0, Hh/2, Lh), (0, 0, 1))
    M.det('door_leaf', 'door leaves (hinged)', (W-0.1, 1.3, Lh)); M.det('roof', 'roof sheet', (0, Hh, 0))
    return M

def HARBOR_11():
    M = Model('HARBOR_11', 'harbor', 'Port loading ramp 3.2 m wide: 2.4 m landing platform, 5 m hinged ramp rising to the platform, anti-slip ribs, side rails, I-beam supports, hydraulic rams, wheel stops')
    M.box('platform', 'metal_painted_grey', -1.6, 1.0, 0.0, 1.6, 1.12, 2.4, 0.02)
    for x in (-1.2, 0.0, 1.2): M.add('platform_beams', 'galvanized_steel', prof_beam((x, 0.82, 0.05), (x, 0.82, 2.35), ibeam_poly(0.2, 0.2, 0.02, 0.014)))
    for x in (-1.4, 1.4):
        for z in (0.3, 2.1): M.box('legs', 'galvanized_steel', x-0.1, 0.0, z-0.1, x+0.1, 1.0, z+0.1, 0.015); M.box('foot', 'galvanized_steel', x-0.25, 0.0, z-0.25, x+0.25, 0.04, z+0.25, 0.01)
    for z in (0.3, 2.1): M.beam('leg_brace', 'galvanized_steel', (-1.4, 0.2, z), (1.4, 0.9, z), 0.06, 0.06); M.beam('leg_brace', 'galvanized_steel', (1.4, 0.2, z), (-1.4, 0.9, z), 0.06, 0.06)
    for i in range(20): M.box('platform_grip', 'rubber_dark', -1.5, 1.12, 0.1+i*0.11, 1.5, 1.135, 0.14+i*0.11)
    # ramp from (z=0,y=1.1) down to (z=-5,y=0.05)
    a = (0, 1.1, 0.0); b = (0, 0.1, -5.0); L = math.dist(a, b)
    ang = math.degrees(math.atan2(a[1]-b[1], a[2]-b[2]))
    T = Model('t', 'x')
    T.box('ramp_plate', 'safety_yellow' if False else 'metal_painted_grey', -1.55, -0.06, 0.0, 1.55, 0.0, L, 0.015)
    for x in (-1.1, -0.35, 0.35, 1.1): T.add('ramp_beams', 'galvanized_steel', prof_beam((x, -0.3, 0.1), (x, -0.3, L-0.1), ibeam_poly(0.16, 0.24, 0.02, 0.014)))
    for i in range(26): T.box('ramp_ribs', 'rubber_dark', -1.5, 0.0, 0.15+i*0.19, 1.5, 0.03, 0.2+i*0.19)
    for s in (-1, 1):
        for z in (0.2, L*0.35, L*0.7, L-0.2): T.box('rail_posts', 'safety_yellow', s*1.52-0.03, 0.0, z-0.03, s*1.52+0.03, 0.95, z+0.03, 0.006)
        T.box('rail_top', 'safety_yellow', s*1.52-0.025, 0.9, 0.17, s*1.52+0.025, 0.95, L-0.17, 0.006); T.box('rail_mid', 'safety_yellow', s*1.52-0.02, 0.5, 0.17, s*1.52+0.02, 0.54, L-0.17, 0.006)
    T.box('toe_plate', 'metal_painted_grey', -1.55, -0.1, L-0.02, 1.55, 0.02, L+0.3, 0.02)
    for (g, m), p in T.groups.items(): M.add(g, m, p.copy().rot('x', -ang).move(0, 1.1, 0.0) if False else p.copy().rot('x', ang).rot('y', 180).move(0, 1.1, 0.0) if False else p.copy().rot('x', -ang).move(0, 1.1, 0.0))
    M.add('hinge', 'brushed_metal', tube((-1.5, 1.1, 0.0), (1.5, 1.1, 0.0), 0.07, 10))
    for x in (-1.0, 1.0): M.add('rams', 'paint_blue', tube((x, 0.85, 0.3), (x, 0.55, -1.6), 0.07, 8)); M.add('ram_rods', 'brushed_metal', tube((x, 0.55, -1.6), (x, 0.32, -2.5), 0.04, 6))
    for x in (-1.2, 1.2): M.box('wheel_stops', 'safety_yellow', x-0.3, 0.0, -5.1, x+0.3, 0.12, -4.9, 0.02) if False else M.box('wheel_stops', 'safety_yellow', x-0.3, 0.0, 2.6, x+0.3, 0.16, 2.8, 0.02)
    M.cn('ramp_toe', (0, 0.1, -5.2), (0, 0, -1)); M.cn('platform_edge', (0, 1.12, 2.4), (0, 0, 1))
    M.det('ramp_plate', 'ramp deck (hinged)', (0, 1.1, 0)); M.det('rams', 'hydraulic rams', (0, 0.7, -1))
    return M

def HARBOR_12():
    M = Model('HARBOR_12', 'harbor', 'Coastal pedestrian railing 3 m bay: 3 square posts with base plates + bolts, round top rail, mid rail, 19 balusters, ball finials; bays chain at z=+/-1.5')
    for z in (-1.5, 0.0, 1.5):
        M.box('base_plate', 'galvanized_steel', -0.1, 0, z-0.1, 0.1, 0.02, z+0.1, 0.004)
        bolts(M, 'base_plate', [(-0.07, z-0.07), (0.07, z-0.07), (-0.07, z+0.07), (0.07, z+0.07)], 0.02, 0.012, 0.015)
        M.box('posts', 'paint_navy', -0.04, 0.02, z-0.04, 0.04, 1.12, z+0.04, 0.008)
        M.add('finials', 'galvanized_steel', sphere_like(0, 1.17, z, 0.055))
    M.add('top_rail', 'galvanized_steel', tube((0, 1.1, -1.5), (0, 1.1, 1.5), 0.035, 8)); M.add('mid_rail', 'paint_navy', tube((0, 0.6, -1.5), (0, 0.6, 1.5), 0.025, 6)); M.add('bottom_rail', 'paint_navy', tube((0, 0.15, -1.5), (0, 0.15, 1.5), 0.02, 6))
    for i in range(1, 20):
        z = -1.5+i*0.15
        if abs(z) < 0.01 or abs(abs(z)-1.5) < 0.01: continue
        M.add('balusters', 'paint_navy', tube((0, 0.15, z), (0, 1.1, z), 0.011, 4))
    M.cn('end_A', (0, 0, -1.5), (0, 0, -1), mates='HARBOR_12'); M.cn('end_B', (0, 0, 1.5), (0, 0, 1)); M.cn('mount_pattern', (0, 0, 0), (0, -1, 0), mates='HARBOR_04/ROAD_09 sockets')
    return M

def HARBOR_13():
    M = Model('HARBOR_13', 'harbor', 'Marina pontoon walkway 1.5 x 6 m: 2 white polyethylene floats, aluminium frame, timber deck, rub rails, 6 horn cleats, connector lugs, power pedestal base')
    for x in (-0.5, 0.5):
        M.box('floats', 'white_paint', x-0.3, -0.35, -2.9, x+0.3, 0.2, 2.9, 0.1)
        for z in (-2.0, -1.0, 0.0, 1.0, 2.0): M.box('float_ribs', 'concrete_pale', x-0.31, -0.2, z-0.04, x+0.31, 0.1, z+0.04, 0.01)
    for z in (-2.6, -1.3, 0.0, 1.3, 2.6): M.box('frame', 'brushed_metal', -0.8, 0.2, z-0.04, 0.8, 0.3, z+0.04, 0.008)
    for s in (-1, 1): M.box('frame', 'brushed_metal', s*0.75-0.04, 0.2, -3.0, s*0.75+0.04, 0.3, 3.0, 0.008)
    for i in range(23): M.box('deck', 'timber_warm' if i % 2 else 'wood_weathered', -0.75, 0.3, -2.95+i*0.26+0.015, 0.75, 0.36, -2.95+i*0.26+0.25, 0.005)
    for s in (-1, 1):
        M.box('rub_rail', 'rubber_dark', min(s*0.78, s*0.86), 0.18, -3.0, max(s*0.78, s*0.86), 0.34, 3.0, 0.02)
        for z in (-2.2, 0.0, 2.2): cleat(M, 'cleats', s*0.65, 0.36, z, 90 if s > 0 else 270, 'galvanized_steel', 0.8)
    for z in (-3.0, 3.0):
        for x in (-0.4, 0.4): M.box('connector_lug', 'galvanized_steel', x-0.08, 0.22, z-0.1 if z < 0 else z-0.02, x+0.08, 0.34, z+0.02 if z < 0 else z+0.1, 0.01); M.add('connector_pin', 'brushed_metal', tube((x, 0.22, z), (x, 0.36, z), 0.025, 6))
    M.box('power_pedestal', 'paint_navy', -0.15, 0.36, -0.1, 0.15, 1.0, 0.1, 0.02) if False else None
    M.cn('end_A', (0, 0.36, -3.0), (0, 0, -1), width=1.5); M.cn('end_B', (0, 0.36, 3.0), (0, 0, 1), width=1.5); M.cn('pile_hoop', (0.9, 0.3, 0), (1, 0, 0))
    M.det('deck', 'deck planks', (0, 0.33, 0)); M.det('floats', 'floats', (0, -0.1, 0))
    return M

def HARBOR_14():
    M = Model('HARBOR_14', 'harbor', 'Quay container gantry crane 48 m: 4 braced portal legs on bogies, lattice boom 38 m out over water, backreach girder, A-frame with backstays, machinery house, trolley with ropes + spreader, cab; rail span along X, boom along +Z (water)')
    lx = 7.5; zs = (-7.0, 7.0); H = 22.0
    for x in (-lx, lx):
        for z in zs:
            M.box('bogies', 'metal_painted_grey', x-0.7, 0, z-1.0, x+0.7, 0.9, z+1.0, 0.1)
            for dz in (-0.55, 0.55): M.add('wheels', 'rubber_dark', tube((x-0.9, 0.5, z+dz), (x+0.9, 0.5, z+dz), 0.42, 12)) if False else M.add('wheels', 'rubber_dark', tube((x-0.9 if False else x-0.0, 0.45, z+dz-0.5), (x+0.0, 0.45, z+dz-0.5), 0.4, 12) if False else tube((x, 0.45, z+dz), (x, 0.45, z+dz), 0.4, 12) if False else cyl(0.4, 0.5, 12, 0, 0, 0).rot('z', 90).move(x-0.25, 0.45, z+dz)) if False else None
            M.add('legs', 'safety_orange' if False else 'metal_painted_grey', beam((x, 0.9, z), (x, H, z), 1.1, 1.1))
    for z in (-7.0, 7.0):
        for x in (-lx, lx): pass
    # rails
    for x in (-lx, lx): M.box('rails', 'rust_metal', x-0.15, 0, -9.0, x+0.15, 0.12, 9.0, 0.02) if False else None
    for z in zs: M.box('rails', 'rust_metal', -12.0, 0, z-0.15, 12.0, 0.15, z+0.15, 0.02)
    # portal sills, braces, top beams
    for z in zs:
        M.beam('sill', 'metal_painted_grey', (-lx, 1.5, z), (lx, 1.5, z), 0.9, 0.9)
        M.beam('portal_beam', 'metal_painted_grey', (-lx, H, z), (lx, H, z), 1.0, 1.4)
        M.beam('brace_x', 'metal_painted_grey', (-lx, 2.0, z), (lx, H-1.0, z), 0.4, 0.4); M.beam('brace_x', 'metal_painted_grey', (lx, 2.0, z), (-lx, H-1.0, z), 0.4, 0.4)
        M.beam('brace_x', 'metal_painted_grey', (-lx, 12.0, z), (lx, 12.0, z), 0.5, 0.5)
    for x in (-lx, lx):
        M.beam('sill_z', 'metal_painted_grey', (x, 1.5, zs[0]), (x, 1.5, zs[1]), 0.9, 0.9)
        M.beam('portal_beam_z', 'metal_painted_grey', (x, H, zs[0]), (x, H, zs[1]), 1.0, 1.4)
        M.beam('brace_z', 'metal_painted_grey', (x, 2.0, zs[0]), (x, H-1.0, zs[1]), 0.4, 0.4); M.beam('brace_z', 'metal_painted_grey', (x, 2.0, zs[1]), (x, H-1.0, zs[0]), 0.4, 0.4)
        M.beam('brace_z', 'metal_painted_grey', (x, 12.0, zs[0]), (x, 12.0, zs[1]), 0.5, 0.5)
    # main girder (boom) lattice from z=-16 to z=+30 at y=H+0.7 .. H+3.7 (two truss planes)
    gy = H+0.7; gh = 3.0
    for x in (-1.6, 1.6): truss_plane(M, 'boom', 'safety_yellow' if False else 'paint_blue', (x, gy, -16.0), (x, gy, 30.0), gh, 23, 0.32)
    for z in [-16+2*i for i in range(24)]: M.beam('boom_cross', 'paint_blue', (-1.6, gy, z), (1.6, gy, z), 0.2, 0.2); M.beam('boom_cross', 'paint_blue', (-1.6, gy+gh, z), (1.6, gy+gh, z), 0.2, 0.2)
    for z in (-16, 6, 30): M.beam('boom_cross', 'paint_blue', (-1.6, gy, z), (1.6, gy+gh, z), 0.14, 0.14)
    for x in (-1.6, 1.6): M.beam('boom_tip', 'safety_orange', (x, gy+gh, 30.0), (x, gy+gh+0.8, 31.0), 0.25, 0.25)
    # machinery house
    M.box('machinery_house', 'white_paint', -2.6, gy+gh, -14.0, 2.6, gy+gh+3.3, -6.0, 0.15); M.box('machinery_roof', 'metal_painted_grey', -2.7, gy+gh+3.3, -14.1, 2.7, gy+gh+3.45, -5.9, 0.05)
    for i in range(6): M.box('house_vents', 'rubber_dark', 2.6, gy+gh+0.5+i*0.4, -13.0, 2.63, gy+gh+0.6+i*0.4, -7.0)
    # A-frame + backstays
    for x in (-2.2, 2.2): M.beam('a_frame', 'paint_blue', (x, gy+gh, 2.5), (x*0.35, gy+gh+16.0, 2.5), 0.6, 0.6)
    M.beam('a_frame', 'paint_blue', (-0.9, gy+gh+14.0, 2.5), (0.9, gy+gh+14.0, 2.5), 0.6, 0.6)
    M.beam('a_frame_top', 'paint_blue', (-0.8, gy+gh+16.0, 2.5), (0.8, gy+gh+16.0, 2.5), 0.7, 0.7)
    for x in (-2.2, 2.2): M.beam('a_frame_brace', 'paint_blue', (x, gy+gh+1.0, 2.5), (x*0.4, gy+gh+13.0, 2.5), 0.25, 0.25)
    for x in (-0.55, 0.55):
        M.add('stays', 'cable_black', tube((x, gy+gh+16.0, 2.5), (x*2.5, gy+gh+0.4, -16.0), 0.06, 5))
        M.add('stays', 'cable_black', tube((x, gy+gh+16.0, 2.5), (x*2.5, gy+gh+0.4, 30.0), 0.06, 5))
    # trolley + spreader + container
    tz = 16.0
    M.box('trolley', 'safety_orange', -2.2, gy-0.9, tz-1.8, 2.2, gy, tz+1.8, 0.1)
    for x in (-1.6, 1.6): M.add('trolley_wheels', 'rubber_dark', tube((x, gy-0.5, tz-1.6), (x, gy-0.5, tz+1.6), 0.28, 8)) if False else None
    M.box('trolley_cab', 'white_paint', 2.2, gy-2.7, tz-1.2, 4.0, gy-0.7, tz+1.2, 0.08); M.box('trolley_cab_window', 'glass_tinted', 3.95, gy-2.3, tz-0.9, 4.02, gy-1.1, tz+0.9)
    M.beam('cab_hanger', 'metal_painted_grey', (2.2, gy-0.7, tz), (3.4, gy-0.7, tz), 0.2, 0.2)
    sy = 9.0
    for x in (-1.0, 1.0):
        for z in (tz-0.9, tz+0.9): M.add('hoist_ropes', 'cable_black', tube((x*1.1, gy-0.9, z*1.0), (x*1.2, sy+0.6, z), 0.05, 5)) if False else M.add('hoist_ropes', 'cable_black', tube((x*1.0, gy-0.9, z), (x*1.0, sy+0.6, z), 0.05, 5))
    M.box('spreader', 'safety_orange', -1.3, sy, tz-2.8, 1.3, sy+0.6, tz+2.8, 0.06) if False else M.box('spreader', 'safety_orange', -1.2, sy, tz-6.1, 1.2, sy+0.6, tz+6.1, 0.06)
    for sx in (-1, 1):
        for sz in (-1, 1): M.box('twist_locks', 'brushed_metal', sx*1.2-0.1, sy-0.2, tz+sz*5.9-0.1, sx*1.2+0.1, sy, tz+sz*5.9+0.1, 0.02)
    # container under spreader (simplified shell, corrugation by ribs)
    M.box('container', 'container_red', -1.22, sy-2.59-0.2, tz-6.095*0.5 if False else tz-3.2*1.0-0.0, 1.22, sy-0.2, tz+3.2, 0.04) if False else None
    for s in (-1.0, 1.0):
        M.add('trolley_rails', 'rust_metal', beam((s*1.6, gy+gh+0.08, -15.0), (s*1.6, gy+gh+0.08, 30.0), 0.12, 0.1)) if False else None
    for x in (-1.6, 1.6): M.beam('trolley_rails', 'rust_metal', (x*0.9, gy-0.08, -16), (x*0.9, gy-0.08, 30), 0.14, 0.14)
    for z in (-1.0, 2.0, 5.0): pass
    M.cn('rail_gauge_centre', (0, 0, 0), (0, -1, 0), gauge=15.0, wheel_base=14.0); M.cn('spreader_point', (0, sy, tz), (0, -1, 0)); M.cn('boom_tip', (0, gy+gh+0.8, 31.0), (0, 0, 1))
    M.det('boom', 'boom girder (separately addressable)', (0, gy, 6.0)); M.det('trolley', 'trolley', (0, gy, tz)); M.det('spreader', 'spreader', (0, sy, tz)); M.det('a_frame', 'A-frame', (0, gy+gh, 2.5)); M.det('legs', 'portal legs', (0, 11, 0))
    return M

HARBOR = [HARBOR_01, HARBOR_02, HARBOR_03, HARBOR_04, HARBOR_05, HARBOR_06, HARBOR_07, HARBOR_08, HARBOR_09, HARBOR_10, HARBOR_11, HARBOR_12, HARBOR_13, HARBOR_14]
