from lib import *
from harbor import rock, sphere_like
from props import bolts, put

# ------------------------------------------------------------------ helpers
def clip(poly, n, c):
    out = []
    for k in range(len(poly)):
        a = poly[k]; b = poly[(k+1) % len(poly)]
        da = n[0]*a[0]+n[1]*a[1]-c; db = n[0]*b[0]+n[1]*b[1]-c
        if da <= 0: out.append(a)
        if (da < 0 < db) or (db < 0 < da):
            t = da/(da-db); out.append((a[0]+(b[0]-a[0])*t, a[1]+(b[1]-a[1])*t))
    return out

def vor_cells(x0, y0, x1, y1, seeds):
    cells = []
    for i, s in enumerate(seeds):
        poly = [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
        for j, t in enumerate(seeds):
            if i == j: continue
            poly = clip(poly, (t[0]-s[0], t[1]-s[1]), (t[0]**2+t[1]**2-s[0]**2-s[1]**2)/2)
            if len(poly) < 3: break
        cells.append(poly)
    return cells

def inset(poly, d):
    cx = sum(p[0] for p in poly)/len(poly); cy = sum(p[1] for p in poly)/len(poly); out = []
    for x, y in poly:
        dx, dy = x-cx, y-cy; L = math.hypot(dx, dy)
        k = max(0.35, (L-d)/L) if L > 1e-6 else 1
        out.append((cx+dx*k, cy+dy*k))
    return out

def pxy(poly, z0, z1, top=None):
    """extrude (x,y) polygon along z."""
    t = top or poly
    return loft([[(x, y, z0) for x, y in poly], [(x, y, z1) for x, y in t]])

def chunk(cx, cy, cz, sx, sy, sz, seed, j=0.25, rx=0, ry=0, rz=0):
    rnd = random.Random(seed)
    def J(): return rnd.uniform(-j, j)
    b = [(-sx/2*(1+J()), -sy/2, -sz/2*(1+J())), (sx/2*(1+J()), -sy/2, -sz/2*(1+J())), (sx/2*(1+J()), -sy/2, sz/2*(1+J())), (-sx/2*(1+J()), -sy/2, sz/2*(1+J()))]
    t = [(-sx/2*(1+J()), sy/2*(1+J()*0.8), -sz/2*(1+J())), (sx/2*(1+J()), sy/2*(1+J()*0.8), -sz/2*(1+J())), (sx/2*(1+J()), sy/2*(1+J()*0.8), sz/2*(1+J())), (-sx/2*(1+J()), sy/2*(1+J()*0.8), sz/2*(1+J()))]
    m = [(a[0]*0.9+rnd.uniform(-sx, sx)*0.08, (a[1]+c[1])/2, a[2]*0.9+rnd.uniform(-sz, sz)*0.08) for a, c in zip(b, t)]
    p = loft([b, m, t])
    if rx: p.rot('x', rx)
    if ry: p.rot('y', ry)
    if rz: p.rot('z', rz)
    return p.move(cx, cy, cz)

def rebar(M, g, p0, p1, r=0.014):
    M.add(g, 'rebar', tube(p0, p1, r, 5))

def blit(M, T, rots=(), move=(0, 0, 0), prefix=''):
    for (g, m), p in T.groups.items():
        q = p.copy()
        for ax, d, piv in rots: q.rot(ax, d, piv)
        q.move(*move); M.add(prefix+g, m, q)

def bent_tube(pts, r, seg=6):
    P = Part()
    for i in range(len(pts)-1): P = P + tube(pts[i], pts[i+1], r*(1-0.1*i), seg)
    return P

def jag_poly_edge(x0, x1, y_base, amp, n, seed, y_top=None):
    rnd = random.Random(seed); pts = []
    for i in range(n+1):
        x = x0+(x1-x0)*i/n; pts.append((x, y_base+rnd.uniform(0, amp)))
    return pts

# ------------------------------------------------------------------ D01..D04
def DESTROY_01():
    M = Model('DESTROY_01', 'destruction', 'Cracked concrete wall 4 x 2.6 x 0.3 m: 12 Voronoi-fractured panels with 2-7 cm open cracks of varied depth, offset faces, exposed rebar, spalled corner, footing')
    rnd = random.Random(11)
    seeds = [(rnd.uniform(0.2, 3.8), rnd.uniform(0.2, 2.4)) for _ in range(12)]
    cells = vor_cells(0, 0.12, 4.0, 2.6, seeds)
    M.box('footing', 'concrete_weathered', -0.1, 0, -0.35, 4.1, 0.12, 0.35, 0.02)
    M.box('backing', 'concrete_core', 0.02, 0.12, -0.15, 3.98, 2.58, -0.02)
    for i, c in enumerate(cells):
        d = rnd.choice([0.012, 0.02, 0.03, 0.045])
        ic = inset(c, d)
        off = rnd.uniform(-0.012, 0.03)
        M.add(f'panel_{i+1}', 'concrete_pale' if i % 3 else 'concrete_weathered', pxy(ic, -0.15, 0.15+off))
        if i % 4 == 0:   # spalled/chipped face layer
            M.add(f'panel_{i+1}_spall', 'broken_concrete', pxy(inset(ic, 0.12), 0.15+off, 0.16+off+0.0))
    for (x, y) in ((1.2, 1.1), (2.5, 0.6), (3.0, 1.9)):
        rebar(M, 'rebar', (x-0.18, y, 0.0), (x+0.18, y+0.06, 0.04))
    M.add('spall_chip', 'broken_concrete', chunk(0.1, 0.17, 0.35, 0.18, 0.1, 0.14, 3, 0.3)); M.add('spall_chip', 'broken_concrete', chunk(2.2, 0.16, 0.45, 0.12, 0.08, 0.1, 5, 0.3))
    M.cn('footing_base', (2.0, 0.0, 0.0), (0, -1, 0))
    for i in range(12): M.det(f'panel_{i+1}', 'fracture panel (falls independently)', None)
    return M

def DESTROY_02():
    M = Model('DESTROY_02', 'destruction', 'Partially collapsed plastered concrete wall 4 x 2.8 x 0.34 m: jagged broken top, exposed concrete core between recessed plaster skins, bent rebar, 5 detached fragments')
    rnd = random.Random(21)
    top = [(2.0, 0.0)]; xs = [2.0, 1.4, 0.9, 0.5, 0.1, -0.4, -0.9, -1.4, -2.0]
    hs = [1.1, 2.5, 1.5, 2.7, 1.2, 2.0, 0.9, 1.7, 2.6]
    prof = [(-2.0, 0), (2.0, 0)] + list(zip(xs, hs))
    prof = [(-2.0, 0), (2.0, 0)] + [(x, h) for x, h in zip(xs, hs)]
    M.add('core', 'concrete_core', pxy(prof, -0.12, 0.12))
    skin = [(x*0.985, max(h-0.09, 0.02) if h > 0.3 else h) for x, h in prof]
    skin[0] = (-1.98, 0.0); skin[1] = (1.98, 0.0)
    M.add('skin_front', 'plaster_cream', pxy(skin, 0.12, 0.17)); M.add('skin_back', 'plaster_cream', pxy(skin, -0.17, -0.12))
    M.box('footing', 'concrete_weathered', -2.2, -0.2, -0.4, 2.2, 0.0, 0.4, 0.02) if False else None
    for x, h in zip(xs[1:-1:2], hs[1:-1:2]):
        rebar(M, 'rebar', (x, h-0.3, 0.0), (x+0.05, h+0.35, 0.0)); rebar(M, 'rebar', (x+0.12, h-0.3, 0.05), (x+0.35, h+0.25, 0.1))
    for y in (0.7, 1.3): rebar(M, 'rebar', (-2.0, y, -0.05), (2.0, y, -0.05), 0.011) if False else None
    chunks = [(2.9, 0.18, 0.9, 0.7, 0.35, 0.5, 31, 0, 40, 0), (-2.8, 0.15, 0.8, 0.6, 0.3, 0.4, 32, 0, -25, 0), (1.2, 0.12, 1.4, 0.5, 0.24, 0.35, 33, 10, 70, 0), (-0.7, 0.1, 1.5, 0.35, 0.2, 0.3, 34, 0, 10, 0), (0.2, 0.28, 1.1, 0.4, 0.3, 0.26, 35, 0, 120, 12)]
    for k, (x, y, z, a, b, c, s, rx, ry, rz) in enumerate(chunks):
        M.add(f'fragment_{k+1}', 'concrete_core', chunk(x, y, z, a, b, c, s, 0.22, rx, ry, rz))
        M.add(f'fragment_{k+1}_skin', 'plaster_cream', chunk(x, y+b*0.46, z, a*0.92, 0.04, c*0.92, s+9, 0.1, rx, ry, rz))
        M.det(f'fragment_{k+1}', 'detached fragment', None)
    M.cn('base', (0, 0, 0), (0, -1, 0))
    return M

def DESTROY_03():
    M = Model('DESTROY_03', 'destruction', 'Shattered window assembly 1.4 x 1.7 m: bent aluminium frame (header bowed, right jamb kinked, sill snapped, mullion sheared), glass remnants fanning from corners, fallen shards, plinth')
    rnd = random.Random(41)
    M.box('plinth', 'concrete_weathered', -0.9, 0, -0.2, 0.9, 0.2, 0.2, 0.02)
    f = 0.07; d = 0.1; yb = 0.2; H = 1.7; W = 1.4
    M.box('left_jamb', 'brushed_metal', -W/2, yb, -d/2, -W/2+f, yb+H, d/2, 0.008)
    M.add('right_jamb_lower', 'brushed_metal', box(W/2-f, yb, -d/2, W/2, yb+1.0, d/2, 0.008))
    M.add('right_jamb_upper', 'brushed_metal', box(W/2-f, yb+1.0, -d/2, W/2, yb+H, d/2, 0.008).rot('z', -9, (W/2-f/2, yb+1.0, 0)).move(0, 0, 0.05))
    M.add('header', 'brushed_metal', box(-W/2, yb+H-f, -d/2, W/2, yb+H, d/2, 0.008).rot('z', -6, (-W/2, yb+H, 0)).move(0, 0, 0))
    M.add('sill_left', 'brushed_metal', box(-W/2, yb, -d/2, 0.1, yb+f, d/2, 0.008))
    M.add('sill_right_fallen', 'brushed_metal', box(0.25, 0, -d/2, W/2, f, d/2, 0.008).rot('y', 25).move(0.15, 0.2, 0.55))
    M.add('mullion_upper', 'brushed_metal', box(-0.02, yb+0.9, -0.04, 0.02, yb+H-f, 0.04, 0.005).rot('z', 5, (0, yb+0.9, 0)))
    M.add('mullion_lower_stub', 'brushed_metal', box(-0.02, yb+f, -0.04, 0.02, yb+0.5, 0.04, 0.005))
    # remaining glass: triangular shards fanning from top-left, top-right, bottom-left
    def shard(p0, p1, p2, z, t=0.007): return pxy([p0, p1, p2], z-t/2, z+t/2)
    xl, xr, yt = -W/2+f, W/2-f, yb+H-f
    G = [((xl, yt), (xl+0.55, yt), (xl+0.12, yt-0.7)), ((xl, yt), (xl+0.12, yt-0.7), (xl, yt-1.1)), ((xr, yt), (xr-0.45, yt), (xr-0.1, yt-0.55)), ((xr, yt), (xr-0.1, yt-0.55), (xr-0.02, yt-0.95)),
         ((xl, yb+f), (xl+0.4, yb+f), (xl, yb+0.6)), ((xl+0.55, yt), (xl+0.12+0.55, yt), (xl+0.35, yt-0.3)), ((xr-0.45, yt), (xr-0.9, yt), (xr-0.55, yt-0.35))]
    for i, (a, b, c) in enumerate(G): M.add(f'glass_remnant_{i+1}', 'glass_tinted', shard(a, b, c, 0.0))
    for i in range(14):
        x = rnd.uniform(-0.6, 0.7); z = rnd.uniform(0.15, 0.9)
        n = rnd.choice([3, 4]); r = rnd.uniform(0.05, 0.16)
        pl = [(x+r*math.cos(2*math.pi*k/n+rnd.uniform(-0.4, 0.4))*rnd.uniform(0.5, 1.2), z+r*math.sin(2*math.pi*k/n)*rnd.uniform(0.5, 1.2)) for k in range(n)]
        M.add('glass_fallen', 'glass_tinted', ext(pl, 0.0, 0.007).rot('x', rnd.uniform(-12, 12), (x, 0, z)).move(0, 0.0, 0.0))
    M.cn('plinth_base', (0, 0, 0), (0, -1, 0)); M.det('glass_remnant_1', 'glass remnants', None)
    return M

def DESTROY_04():
    M = Model('DESTROY_04', 'destruction', 'Detached facade panel 3.2 x 2.6 x 0.3 m: plaster front skin, concrete core, 2 window openings with bent frames, jagged torn bottom + top-right corner, protruding rebar, 3 shed fragments')
    rnd = random.Random(51)
    def piece(poly, g, z=0.1, front='plaster_cream'):
        M.add(g+'_core', 'concrete_core', pxy(poly, -z, z)); M.add(g+'_skin', front, pxy([(x, y) for x, y in poly], z, z+0.05))
    bot = [(-1.6, 0.0)] + [(-1.6+0.4*i, rnd.uniform(0.0, 0.28)) for i in range(1, 8)] + [(1.6, 0.05), (1.6, 0.8), (-1.6, 0.8)]
    bot = [(-1.6, 0.8), (-1.6, 0.1)] + [(-1.6+0.4*i, rnd.uniform(0.0, 0.3)) for i in range(1, 8)] + [(1.6, 0.0), (1.6, 0.8)]
    piece(bot, 'sill_band')
    top = [(-1.6, 1.9), (1.6, 1.9), (1.6, 2.15), (1.15, 2.35), (1.0, 2.2), (0.6, 2.6), (-0.2, 2.6), (-0.5, 2.45), (-1.1, 2.6), (-1.6, 2.6)]
    piece(top, 'header_band')
    for (x0, x1, n) in ((-1.6, -1.25, 'pier_L'), (-0.35, 0.35, 'pier_M'), (1.25, 1.6, 'pier_R')): piece([(x0, 0.8), (x1, 0.8), (x1, 1.9), (x0, 1.9)], n)
    for cx in (-0.8, 0.8):
        fx0, fx1 = cx-0.45, cx+0.45
        M.box('window_frame', 'brushed_metal', fx0, 0.8, -0.04, fx0+0.05, 1.9, 0.04, 0.005); M.box('window_frame', 'brushed_metal', fx1-0.05, 0.8, -0.04, fx1, 1.9, 0.04, 0.005)
        M.add('window_frame', 'brushed_metal', box(fx0, 1.85, -0.04, fx1, 1.9, 0.04, 0.005).rot('z', -3 if cx < 0 else 5, (fx0, 1.9, 0))); M.box('window_frame', 'brushed_metal', fx0, 0.8, -0.04, fx1, 0.85, 0.04, 0.005)
        M.add('window_glass', 'glass_tinted', pxy([(fx0+0.05, 1.85), (fx0+0.05+0.35, 1.85), (fx0+0.05, 1.2)], -0.004, 0.004)); M.add('window_glass', 'glass_tinted', pxy([(fx1-0.05, 0.85), (fx1-0.05-0.3, 0.85), (fx1-0.05, 1.15)], -0.004, 0.004))
    for x in (-1.1, -0.3, 0.5, 1.2): rebar(M, 'rebar', (x, 0.1, 0.0), (x+rnd.uniform(-0.1, 0.1), -0.25, 0.05+rnd.uniform(-0.05, 0.05)))
    for x in (0.7, 0.2): rebar(M, 'rebar', (x, 2.5, 0.0), (x+0.15, 2.9, 0.1))
    fr = [(1.9, 0.12, 0.7, 0.6, 0.24, 0.5, 52, 0, 30, 0), (-2.0, 0.09, 0.9, 0.5, 0.2, 0.4, 53, 0, -50, 0), (1.3, 0.1, 1.3, 0.35, 0.18, 0.3, 54, 0, 20, 0)]
    for k, (x, y, z, a, b, c, s, rx, ry, rz) in enumerate(fr):
        M.add(f'fragment_{k+1}', 'concrete_core', chunk(x, y, z, a, b, c, s, 0.25, rx, ry, rz)); M.add(f'fragment_{k+1}_skin', 'plaster_cream', chunk(x, y+b*0.46, z, a*0.9, 0.05, c*0.9, s+4, 0.1, rx, ry, rz))
    for n in ('pier_M', 'header_band', 'pier_R'): M.det(n+'_core', 'falling facade part', None)
    M.cn('base', (0, 0, 0), (0, -1, 0))
    return M

# ------------------------------------------------------------------ D05..D08
def DESTROY_05():
    M = Model('DESTROY_05', 'destruction', 'Collapsed balcony: fractured wall root with rebar, 2.8 x 1.4 m slab hinged down 24 deg, railing with bent/snapped posts and drooping rail, broken corbels, rubble')
    rnd = random.Random(61)
    prof = [(-1.8, 0), (1.8, 0), (1.8, 3.0), (0.7, 3.0), (0.4, 2.7), (-0.1, 3.0), (-1.8, 3.0)]
    M.add('wall_core', 'concrete_core', pxy(prof, -0.15, 0.15)); M.add('wall_skin', 'plaster_cream', pxy(prof, 0.15, 0.2))
    T = Model('t', 'x')
    slab = [(-1.4, 0.0), (1.4, 0.0), (1.4, 1.3), (0.9, 1.45), (0.2, 1.3), (-0.5, 1.4), (-1.4, 1.25)]
    T.ext('slab', 'concrete_pale', [(x, z) for x, z in slab], 0.0, 0.14)
    T.ext('slab_underside', 'concrete_core', [(x*0.97, z*0.97+0.01) for x, z in slab], -0.04, 0.0)
    for x in (-1.0, -0.3, 0.5, 1.1): rebar(T, 'rebar', (x, 0.07, -0.25), (x+0.02, 0.07, 0.35), 0.013)
    for x in (-1.3, 1.3):
        T.add('corbel', 'concrete_weathered', box(x-0.15, -0.35, 0.0, x+0.15, 0.0, 0.5, 0.02))
    # railing along front edge (z=1.3..1.4) and sides
    for i, x in enumerate((-1.4, -0.7, 0.0, 0.7, 1.4)):
        zf = 1.32
        if i == 2: T.add('post_snapped', 'brushed_metal', box(x-0.03, 0.14, zf-0.03, x+0.03, 0.4, zf+0.03, 0.005))
        elif i == 3: T.add('post_bent', 'brushed_metal', bent_tube([(x, 0.14, zf), (x, 0.55, zf), (x+0.1, 0.9, zf+0.25)], 0.03, 6))
        else: T.box('post', 'brushed_metal', x-0.03, 0.14, zf-0.03, x+0.03, 1.1, zf+0.03, 0.005)
    T.add('rail_top_left', 'brushed_metal', tube((-1.4, 1.1, 1.32), (-0.05, 1.06, 1.32), 0.03, 6))
    T.add('rail_top_right', 'brushed_metal', tube((1.4, 1.1, 1.32), (0.7, 0.95, 1.6), 0.03, 6))
    T.add('rail_top_right', 'brushed_metal', tube((0.7, 0.95, 1.6), (0.15, 0.2, 1.9), 0.03, 6))
    for z in (0.3, 0.9): T.add('side_post', 'brushed_metal', box(-1.43, 0.14, z-0.03, -1.37, 1.1, z+0.03, 0.005))
    T.add('side_rail', 'brushed_metal', tube((-1.4, 1.1, 0.3), (-1.4, 1.1, 1.32), 0.03, 6))
    for x in (-1.1, -0.4): T.add('baluster', 'brushed_metal', tube((x, 0.14, 1.32), (x, 1.05, 1.32), 0.012, 4))
    blit(M, T, [('x', 24, (0, 0, 0))], (0, 2.0, 0.15))
    for z in (0.15, -0.15): pass
    for x in (-1.0, -0.2, 0.9): rebar(M, 'wall_rebar', (x, 1.95, 0.3), (x+0.05, 2.1, 1.0))
    for k in range(7): M.add('rubble', 'broken_concrete', chunk(rnd.uniform(-1.4, 1.4), 0.1, rnd.uniform(1.3, 2.4), rnd.uniform(0.15, 0.4), 0.2, rnd.uniform(0.15, 0.4), 70+k, 0.3, 0, rnd.uniform(0, 90), 0))
    M.det('slab', 'balcony slab (hinge at wall)', (0, 2.0, 0.15)); M.det('post_bent', 'railing', None)
    M.cn('base', (0, 0, 0), (0, -1, 0))
    return M

def DESTROY_06():
    M = Model('DESTROY_06', 'destruction', 'Broken pitched roof section 4 x 3.2 m at 30 deg: wall plate + tie beams, rafters (2 snapped), battens, clay-tile courses with a 1.6 m storm hole, ragged eave, torn ridge')
    rnd = random.Random(81); P = math.radians(30)
    M.box('wall_plate', 'wood_weathered', -2.1, 0, -0.1, 2.1, 0.12, 0.1, 0.01)
    M.box('wall_plate', 'wood_weathered', -2.1, 0, 2.7, 2.1, 0.12, 2.9, 0.01)
    for i in range(7):
        x = -1.8+0.6*i
        M.box('tie_beams', 'timber_warm', x-0.05, 0.0, -0.1, x+0.05, 0.12, 2.9, 0.008)
    T = Model('t', 'x'); Ls = 3.4
    for i in range(7):
        x = -1.8+0.6*i
        if i in (3, 4): T.add('rafter_snapped', 'timber_warm', box(x-0.05, 0, 0, x+0.05, 0.14, 1.1+0.5*(i-3), 0.008))
        else: T.box('rafters', 'timber_warm', x-0.05, 0, 0, x+0.05, 0.14, Ls, 0.008)
    T.add('rafter_snapped_end', 'timber_warm', chunk(0.15, 0.1, 2.55, 0.1, 0.12, 0.9, 5, 0.2, 18, 25, 0)); T.add('rafter_snapped_end', 'timber_warm', chunk(-0.45, 0.07, 3.0, 0.1, 0.1, 0.8, 6, 0.2, 5, -35, 0))
    for k in range(10):
        s = 0.2+k*0.33
        for (a, b) in ((-2.0, -0.35), (1.3, 2.0)): T.box('battens', 'wood_weathered', a, 0.14, s-0.025, b, 0.18, s+0.025, 0.004)
        if not (0.8 < s < 2.4): T.box('battens', 'wood_weathered', -0.35, 0.14, s-0.025, 1.3, 0.18, s+0.025, 0.004)
    for k in range(9):                                  # tile courses
        s = 0.16+k*0.33
        for i in range(14):
            x = -2.0+i*0.29+(0.145 if k % 2 else 0)
            hx = x+0.14
            if hx > 2.0: continue
            in_hole = (-0.45 < x < 1.25) and (0.75 < s < 2.45)
            ragged = (k >= 7 and rnd.random() < 0.5) or (k == 0 and i > 11 and rnd.random() < 0.6)
            if in_hole or ragged: continue
            T.add('tiles', 'roof_tile' if (i+k) % 3 else 'brick_red', tbox(x, 0.18, s-0.17, x+0.28, 0.24, s+0.17, 0.92))
    for i in range(3): T.add('loose_tiles', 'roof_tile', tbox(0.1+i*0.3, 0.14, 0.95+i*0.2, 0.38+i*0.3, 0.19, 1.3+i*0.2, 0.9).rot('y', rnd.uniform(-30, 30)))
    T.box('ridge_beam', 'timber_warm', -2.0, 0.0, Ls-0.1, 0.4, 0.16, Ls+0.05, 0.01)
    for i in range(7): T.add('ridge_tiles', 'roof_tile', tbox(-2.0+i*0.3, 0.18, Ls-0.1, -1.72+i*0.3, 0.3, Ls+0.1, 0.8))
    blit(M, T, [('x', -30, (0, 0, 0))], (0, 0.12, 0.0))
    for k in range(5): M.add('debris_tiles', 'roof_tile', tbox(-1.8+k*0.7+rnd.uniform(-0.2, 0.2), 0.0, -0.9-rnd.random()*0.7, -1.5+k*0.7, 0.05, -0.65-rnd.random()*0.7, 0.9).rot('y', rnd.uniform(0, 90)))
    M.det('tiles', 'roof tiles (shed individually)', None); M.det('rafters', 'rafters', None)
    M.cn('base', (0, 0, 0), (0, -1, 0))
    return M

def DESTROY_07():
    M = Model('DESTROY_07', 'destruction', 'Damaged rooftop assembly 4.5 x 3.4 m: slab with broken corner + peeled membrane, collapsed parapet, tipped AC unit on bent mounts, snapped vent stack, leaning tank with kinked legs')
    rnd = random.Random(91)
    slab = [(-2.25, -1.7), (2.25, -1.7), (2.25, 0.7), (1.6, 1.0), (1.55, 1.7), (0.6, 1.4), (-0.4, 1.7), (-2.25, 1.7)]
    M.ext('slab', 'concrete_weathered', slab, 0.0, 0.25)
    M.ext('membrane', 'rubber_dark', [(x*0.98, z*0.98) for x, z in slab if not (x > 1.0 and z > 0.5)] , 0.25, 0.27) if False else M.ext('membrane', 'asphalt_cool', [(-2.2, -1.65), (2.2, -1.65), (2.2, 0.6), (0.5, 0.2), (-0.4, 1.35), (-2.2, 1.65)], 0.25, 0.27)
    M.add('membrane_peeled', 'asphalt_cool', box(0.5, 0.0, 0.2, 2.2, 0.025, 1.2, 0.004).rot('x', -20, (0, 0, 0.2)).rot('z', 8, (0.5, 0, 0)).move(0, 0.3, 0.0))
    # parapet
    M.box('parapet_back', 'plaster_cream', -2.25, 0.25, -1.7, 2.25, 0.85, -1.5, 0.02)
    M.box('parapet_left', 'plaster_cream', -2.25, 0.25, -1.5, -2.05, 0.85, 1.7, 0.02)
    M.add('parapet_right_stub', 'plaster_cream', box(2.05, 0.25, -1.5, 2.25, 0.85, -0.2, 0.02))
    M.add('parapet_right_fallen', 'plaster_cream', box(2.05, 0.0, 0.0, 2.25, 0.6, 1.0, 0.02).rot('x', 12, (2.15, 0, 0)).rot('z', 70, (2.15, 0.0, 0.0)).move(0.5, 0.25, 0.4))
    for k in range(5): M.add('parapet_rubble', 'broken_concrete', chunk(rnd.uniform(1.8, 3.0), 0.18, rnd.uniform(0.2, 1.8), 0.3, 0.2, 0.25, 100+k, 0.3, 0, rnd.uniform(0, 90), 0))
    # tipped AC unit on bent mounts
    T = Model('t', 'x')
    T.box('ac_housing', 'white_paint', -0.7, 0.0, -0.4, 0.7, 0.7, 0.4, 0.04); T.box('ac_top', 'metal_painted_grey', -0.68, 0.7, -0.38, 0.68, 0.73, 0.38, 0.01)
    T.add('ac_fan_ring', 'rubber_dark', cyl(0.28, 0.02, 12, 0.73, 0.25, 0))
    for i in range(6): T.box('ac_grille', 'galvanized_steel', -0.69, 0.1+i*0.1, -0.3, -0.66, 0.12+i*0.1, 0.3)
    blit(M, T, [('z', 28, (-0.7, 0, 0)), ('y', 12, (0, 0, 0))], (-1.0, 0.55, -0.5))
    for x, z, bent in ((-1.6, -0.9, True), (-0.4, -0.9, False), (-1.6, -0.1, True), (-0.4, -0.1, False)):
        if bent: M.add('ac_mount_bent', 'galvanized_steel', bent_tube([(x, 0.25, z), (x, 0.45, z), (x-0.18, 0.6, z+0.05)], 0.03))
        else: M.box('ac_mount', 'galvanized_steel', x-0.03, 0.25, z-0.03, x+0.03, 0.55, z+0.03, 0.005)
    M.box('ac_mount_rail', 'galvanized_steel', -1.8, 0.25, -1.0, -0.3, 0.3, -0.85, 0.01)
    # vent stack snapped
    M.add('vent_stack_stub', 'galvanized_steel', cyl(0.07, 0.35, 8, 0.25, 0.6, -1.0)); M.add('vent_stack_stub', 'galvanized_steel', chunk(0.6, 0.62, -1.0, 0.1, 0.06, 0.1, 9, 0.3))
    M.add('vent_stack_fallen', 'galvanized_steel', tube((0.9, 0.34, -0.5), (1.9, 0.34, -0.1), 0.07, 8)); M.add('vent_cap', 'galvanized_steel', lathe([(0.14, 0.34), (0.0, 0.5)], 8, 1.9, -0.1)) if False else None
    # tank leaning
    TT = Model('t', 'x')
    TT.add('tank', 'coastal_weathered', lathe([(0.55, 0.9), (0.6, 0.95), (0.6, 2.0), (0.55, 2.05)], 12)); TT.add('tank_roof', 'rust_metal', lathe([(0.6, 2.0), (0.3, 2.2), (0.01, 2.25)], 12))
    for dx, dz in ((-0.4, -0.4), (0.4, -0.4), (0.4, 0.4), (-0.4, 0.4)): TT.add('tank_leg', 'galvanized_steel', beam((dx, 0.0, dz), (dx*0.9, 0.95, dz*0.9), 0.07, 0.07))
    blit(M, TT, [('z', 14, (0, 0, 0)), ('x', -6, (0, 0, 0))], (-0.1, 0.25, 0.9)) if False else blit(M, TT, [('z', 14, (0, 0, 0)), ('x', -6, (0, 0, 0))], (-0.1, 0.25, -0.1)) if False else None
    blit(M, TT, [('z', 14, (0.4, 0, 0)), ('x', -6, (0, 0, 0.4))], (-0.6, 0.25, 0.9))
    M.add('mast_bent', 'galvanized_steel', bent_tube([(1.4, 0.25, -1.1), (1.4, 1.4, -1.1), (1.7, 2.3, -0.9), (2.3, 2.6, -0.5)], 0.04))
    M.det('ac_housing', 'AC unit', None); M.det('parapet_right_fallen', 'parapet segment', None); M.det('tank', 'tank', None)
    M.cn('base', (0, 0, 0), (0, -1, 0))
    return M

def DESTROY_08():
    M = Model('DESTROY_08', 'destruction', 'Destroyed storefront 4 x 3.4 m: cracked brick bulkhead, bent aluminium frame, door torn off hinges and dropped, glass remnants, sign board hanging by one bracket, collapsed awning, debris')
    rnd = random.Random(111)
    bulk = [(-2.0, 0.0), (2.0, 0.0), (2.0, 0.65), (1.4, 0.8), (0.9, 0.55), (0.2, 0.78), (-0.5, 0.6), (-1.2, 0.85), (-2.0, 0.7)]
    M.add('bulkhead', 'brick_red', pxy(bulk, -0.18, 0.18))
    for y in (0.2, 0.4, 0.6): M.box('bulkhead_mortar', 'mortar', -2.0, y, 0.18, 1.9 if y > 0.5 else 2.0, y+0.012, 0.185) if False else None
    for i in range(5): M.box('bulkhead_courses', 'mortar', -1.95, 0.12+i*0.14, 0.18, -1.9+3.9*(1-(i % 2)*0.03), 0.125+i*0.14, 0.185) if False else M.box('bulkhead_courses', 'mortar', -1.95, 0.12+i*0.14, 0.18, 1.95, 0.125+i*0.14, 0.185)
    M.box('sill', 'concrete_pale', -2.05, 0.0, 0.0, -1.95, 0.0, 0.0) if False else None
    # frame posts
    for x in (-2.0, -0.6, 0.9):
        M.box('frame_post', 'brushed_metal', x-0.04, 0.7, -0.05, x+0.04, 2.9, 0.05, 0.006) if x != 0.9 else M.add('frame_post_bent', 'brushed_metal', bent_tube([(x, 0.6, 0), (x, 1.6, 0), (x+0.28, 2.3, 0.05), (x+0.5, 2.8, 0.2)], 0.045, 4) if False else merge([beam((x, 0.6, 0), (x, 1.6, 0), 0.08, 0.1), beam((x, 1.6, 0), (x+0.3, 2.3, 0.1), 0.08, 0.1), beam((x+0.3, 2.3, 0.1), (x+0.5, 2.8, 0.25), 0.08, 0.1)]))
    M.add('transom', 'brushed_metal', box(-2.0, 2.85, -0.05, -0.55, 2.93, 0.05, 0.006)); M.add('transom_twisted', 'brushed_metal', box(-0.55, 2.85, -0.05, 0.7, 2.93, 0.05, 0.006).rot('z', 7, (-0.55, 2.89, 0)).rot('x', 18, (0, 2.9, 0)))
    M.box('sill_rail', 'brushed_metal', -2.0, 0.65, -0.05, 0.5, 0.72, 0.05, 0.006)
    for i, (a, b, c) in enumerate((((-1.95, 2.85), (-1.4, 2.85), (-1.95, 2.2)), ((-1.95, 0.72), (-1.5, 0.72), (-1.95, 1.1)), ((-0.55, 2.85), (-0.1, 2.85), (-0.55, 2.4)), ((-0.65, 0.72), (-0.3, 0.72), (-0.65, 1.0)))):
        M.add(f'glass_remnant', 'glass_tinted', pxy([a, b, c], -0.005, 0.005))
    for i in range(16): 
        x = rnd.uniform(-1.8, 0.8); z = rnd.uniform(0.25, 1.4); r = rnd.uniform(0.05, 0.17)
        M.add('glass_fallen', 'glass_tinted', ext([(x, z), (x+r, z+rnd.uniform(0, r)), (x+rnd.uniform(0, r), z+r*1.3)], 0.0, 0.007).rot('y', rnd.uniform(0, 90), (x, 0, z)))
    # door off hinges, dropped & leaning
    D = Model('t', 'x')
    D.box('door_frame', 'brushed_metal', 0.0, 0.0, -0.025, 0.9, 2.1, 0.025, 0.006); D.box('door_glass', 'glass_tinted', 0.07, 0.4, -0.012, 0.83, 1.9, 0.012)
    D.box('door_bar', 'brushed_metal', 0.1, 1.0, 0.025, 0.8, 1.04, 0.07, 0.004)
    blit(M, D, [('y', -40, (0, 0, 0)), ('z', 14, (0, 0, 0))], (1.5, 0.12, 0.9))
    # sign board hanging by one bracket
    S = Model('t', 'x')
    S.box('sign_board', 'sign_blue', 0.0, -0.4, -0.04, 2.2, 0.0, 0.04, 0.01); S.box('sign_text_panel', 'sign_white', 0.12, -0.3, 0.04, 2.08, -0.1, 0.05)
    blit(M, S, [('z', -48, (0, 0, 0))], (-1.6, 3.4, 0.25))
    M.box('sign_bracket', 'galvanized_steel', -1.7, 3.3, 0.1, -1.5, 3.4, 0.4, 0.01) if False else M.box('sign_bracket', 'galvanized_steel', -1.75, 3.35, 0.15, -1.45, 3.42, 0.35, 0.01)
    M.add('sign_bracket_snapped', 'galvanized_steel', box(0.4, 3.35, 0.15, 0.7, 3.42, 0.35, 0.01).rot('z', -35, (0.4, 3.4, 0.2)))
    # awning collapsed
    M.add('awning_attached', 'traffic_red', box(-2.0, 2.9, 0.0, -0.3, 2.93, 1.0, 0.004).rot('x', -35, (0, 2.95, 0.0)).move(0, 0.0, 0.0))
    M.add('awning_fallen', 'traffic_red', box(0.0, 0.0, 0.0, 1.5, 0.03, 1.0, 0.004).rot('x', 18, (0, 0, 0)).rot('y', 15, (0, 0, 0)).move(-0.5, 0.45, 0.8) if False else box(0.0, 0.0, 0.0, 1.5, 0.03, 1.0, 0.004).rot('x', 18, (0, 0, 0)).rot('y', 15, (0, 0, 0)).move(0.1, 0.3, 1.0))
    for k in range(6): M.add('debris', 'brick_red', chunk(rnd.uniform(-1.8, 1.8), 0.05, rnd.uniform(0.3, 1.6), 0.22, 0.07, 0.1, 130+k, 0.2, 0, rnd.uniform(0, 180), 0))
    M.det('door_frame', 'door', None); M.det('sign_board', 'sign', (-1.6, 3.4, 0.25)); M.det('awning_attached', 'awning', None)
    M.cn('base', (0, 0, 0), (0, -1, 0))
    return M

# ------------------------------------------------------------------ D09..D12
def fract_cyl(x0, x1, r, cy, cz, seg, rnd, frac_start=False, frac_end=True, amp=0.35, rr=None):
    rings = []
    def ring(x, jag):
        pts = []
        for i in range(seg):
            a = 2*math.pi*i/seg
            pts.append((x+(jag*rnd.uniform(-1, 1) if jag else 0.0), cy+r*math.sin(a), cz+r*math.cos(a)))
        return pts
    rings.append(ring(x0, amp if frac_start else 0)); 
    for k in range(1, 5): rings.append([(x0+(x1-x0)*k/5, p[1], p[2]) for p in ring(0, 0)])
    rings.append(ring(x1, amp if frac_end else 0))
    return loft(rings)

def DESTROY_09():
    M = Model('DESTROY_09', 'destruction', 'Fallen structural column 4.1 m x 0.7 dia: snapped in two, jagged fracture faces with exposed inner core, 8 longitudinal bars + stirrups bent out of the break, base plate end and flared capital end, spall chunks')
    rnd = random.Random(121); cy = 0.35; seg = 12
    A = fract_cyl(0, 2.4, 0.35, cy, 0, seg, rnd, False, True, 0.3)
    M.add('piece_A_shell', 'concrete_pale', A)
    M.add('piece_A_core', 'concrete_core', fract_cyl(1.9, 2.7, 0.27, cy, 0, 8, rnd, False, True, 0.25))
    M.box('base_plate', 'galvanized_steel', -0.08, 0.0, -0.4, 0.0, 0.8, 0.4, 0.01) if False else M.box('base_plate', 'galvanized_steel', -0.1, cy-0.42, -0.42, 0.0, cy+0.42, 0.42, 0.01)
    for a in range(0, 360, 90): M.add('base_bolt_stubs', 'galvanized_steel', tube((-0.1, cy+0.3*math.sin(math.radians(a)), 0.3*math.cos(math.radians(a))), (-0.3, cy+0.3*math.sin(math.radians(a)), 0.3*math.cos(math.radians(a))), 0.025, 6))
    B = fract_cyl(2.85, 4.05, 0.35, cy+0.0, 0.0, seg, rnd, True, False, 0.28)
    B.rot('y', 7, (2.85, 0, 0)).move(0.0, 0.0, 0.03)
    M.add('piece_B_shell', 'concrete_pale', B)
    M.add('piece_B_core', 'concrete_core', fract_cyl(2.55, 3.4, 0.27, cy, 0.0, 8, rnd, True, False, 0.22).rot('y', 7, (2.85, 0, 0)).move(0, 0, 0.03))
    M.add('capital', 'concrete_pale', lathe([(0.35, 0), (0.55, 0.1), (0.55, 0.35), (0.7, 0.4)], 12).rot('z', -90).move(4.05, cy, 0).rot('y', 7, (2.85, 0, 0)).move(0, 0, 0.03)) if False else M.add('capital', 'concrete_pale', box(4.0, cy-0.5, -0.5, 4.4, cy+0.5, 0.5, 0.04).rot('y', 7, (2.85, 0, 0)).move(0, 0, 0.03))
    for k in range(8):
        a = 2*math.pi*k/8
        ya, za = cy+0.28*math.sin(a), 0.28*math.cos(a)
        rebar(M, 'bars_A', (1.95, ya, za), (2.75+rnd.uniform(0, 0.1), ya+0.1*math.sin(a)+rnd.uniform(-0.05, 0.1), za+0.12*math.cos(a)), 0.016)
        P = bent_tube([(3.0, ya, za), (2.6, ya+0.05*math.sin(a), za+0.05*math.cos(a)), (2.45, ya+0.2*math.sin(a), za+0.2*math.cos(a))], 0.016, 5)
        M.add('bars_B', 'rebar', P.copy().rot('y', 7, (2.85, 0, 0)).move(0, 0, 0.03))
    for x in (2.1, 2.4):
        M.add('stirrups', 'rebar', merge([tube((x, cy+0.3*math.sin(2*math.pi*k/8), 0.3*math.cos(2*math.pi*k/8)), (x, cy+0.3*math.sin(2*math.pi*(k+1)/8), 0.3*math.cos(2*math.pi*(k+1)/8)), 0.008, 4) for k in range(8)]))
    for k in range(6): M.add('spall', 'broken_concrete', chunk(rnd.uniform(1.8, 3.4), 0.06, rnd.uniform(-0.8, 0.8), 0.18, 0.1, 0.15, 150+k, 0.3, 0, rnd.uniform(0, 90), 0))
    M.det('piece_B_shell', 'column upper piece', (2.85, cy, 0)); M.det('piece_A_shell', 'column lower piece', (0, cy, 0))
    M.cn('piece_A_end', (0, cy, 0), (-1, 0, 0))
    return M

def DESTROY_10():
    M = Model('DESTROY_10', 'destruction', 'Fractured steel I-beam 6.4 m: sheared at mid-span with torn staggered flange/web ends; far half buckled and drooped in 4 kinks with flange crumple; end plates + bolt holes')
    w, h, tf, tw = 0.2, 0.4, 0.022, 0.014; Y = 1.2
    def flange_web(x0, x1, ww, hh, pos=(0, 0, 0)): pass
    # near half (straight), staggered torn ends
    M.box('near_flange_top', 'metal_painted_grey', 0.0, Y+h/2-tf, -w/2, 2.7, Y+h/2, w/2, 0.004)
    M.box('near_flange_bottom', 'metal_painted_grey', 0.0, Y-h/2, -w/2, 3.05, Y-h/2+tf, w/2, 0.004)
    M.box('near_web', 'metal_painted_grey', 0.0, Y-h/2+tf, -tw/2, 2.85, Y+h/2-tf, tw/2, 0.003)
    M.add('near_tear_flap', 'metal_painted_grey', box(2.7, Y+h/2-tf, -w/2, 3.1, Y+h/2, w/2, 0.003).rot('z', -22, (2.7, Y+h/2, 0)).rot('x', 9, (2.7, 0, 0)))
    M.add('near_web_tear', 'metal_painted_grey', pxy([(2.85, Y-h/2+tf), (3.05, Y-h/2+tf), (2.95, Y), (3.0, Y+0.12), (2.85, Y+h/2-tf)], -tw/2, tw/2))
    # far half: path with kinks
    pts = [(3.0, Y), (3.6, Y-0.12), (4.2, Y-0.45), (4.8, Y-0.95), (5.3, Y-1.1), (6.4, Y-1.15)]
    scale_f = [1.0, 0.9, 0.78, 0.9, 1.0]
    for i in range(len(pts)-1):
        a = (pts[i][0], pts[i][1], 0.0); b = (pts[i+1][0], pts[i+1][1], 0.0)
        wp = w*scale_f[i]
        poly = ibeam_poly(wp, h, tf, tw)
        M.add('far_beam', 'metal_painted_grey', prof_beam(a, b, poly))
    M.add('far_crumple', 'rust_metal', chunk(4.8, Y-0.95+0.17, 0.0, 0.3, 0.1, 0.22, 3, 0.35, 0, 0, -35)); M.add('far_crumple', 'rust_metal', chunk(4.2, Y-0.45+0.2, 0.05, 0.25, 0.08, 0.2, 4, 0.35, 8, 0, -25))
    M.add('far_flange_peeled', 'metal_painted_grey', box(3.2, Y+h/2-tf, -w/2, 3.9, Y+h/2, w/2, 0.003).rot('z', -33, (3.2, Y+h/2, 0)).rot('x', -14, (3.2, 0, 0)).move(0, -0.1, 0))
    M.box('end_plate_near', 'galvanized_steel', -0.04, Y-0.28, -0.14, 0.0, Y+0.28, 0.14, 0.004)
    for (dy, dz) in ((-0.2, -0.09), (-0.2, 0.09), (0.2, -0.09), (0.2, 0.09)): M.add('bolts_near', 'brushed_metal', tube((-0.06, Y+dy, dz), (0.03, Y+dy, dz), 0.017, 6))
    M.add('end_plate_far', 'galvanized_steel', box(6.4, Y-1.15-0.28, -0.14, 6.44, Y-1.15+0.28, 0.14, 0.004))
    for (dy, dz) in ((-0.2, -0.09), (-0.2, 0.09), (0.2, -0.09), (0.2, 0.09)): M.add('bolts_far', 'brushed_metal', tube((6.3, Y-1.15+dy, dz), (6.5, Y-1.15+dy, dz), 0.017, 6))
    for x in (0.2, 6.1): M.add('support_blocks', 'concrete_weathered', box(x-0.3, 0.0, -0.3, x+0.3, 0.5 if x < 1 else 0.05, 0.3, 0.02)) if x < 1 else None
    M.add('support_blocks', 'concrete_weathered', box(0.0, 0.0, -0.3, 0.6, 0.9, 0.3, 0.02))
    M.add('support_blocks', 'concrete_weathered', box(5.9, 0.0, -0.3, 6.5, 0.0+0.02, 0.3, 0.02))
    for k in range(4): M.add('debris', 'broken_concrete', chunk(3.8+k*0.4, 0.1, rnd_u(k)*0.8, 0.2, 0.15, 0.2, 170+k, 0.3, 0, k*40, 0))
    M.det('far_beam', 'far half of beam', (3.0, Y, 0)); M.det('near_flange_top', 'near half', (0, Y, 0))
    M.cn('near_end', (0, Y, 0), (-1, 0, 0))
    return M

def rnd_u(k): return math.sin(k*12.9898)*0.9

def DESTROY_11():
    M = Model('DESTROY_11', 'destruction', 'Broken concrete slab 3.6 x 2.8 x 0.25 m: 8 Voronoi fracture plates, three tilted/stacked, 0.25 m exposed cross-sections, top finish skin, rebar mesh across gaps')
    rnd = random.Random(131)
    seeds = [(rnd.uniform(0.2, 3.4), rnd.uniform(0.2, 2.6)) for _ in range(8)]
    cells = vor_cells(0, 0, 3.6, 2.8, seeds)
    tilts = [(0, 0, 0), (6, 3, 0.0), (-9, 5, 0.0), (22, -8, 0.22), (-5, 4, 0.0), (14, 12, 0.18), (0, -6, 0.0), (-17, 2, 0.12)]
    for i, c in enumerate(cells):
        ic = inset(c, 0.02+0.01*(i % 3)); cx = sum(p[0] for p in ic)/len(ic); cz = sum(p[1] for p in ic)/len(ic)
        T = Model('t', 'x')
        T.ext('plate', 'concrete_core', ic, 0.0, 0.25); T.ext('skin', 'concrete_pale', [(x, z) for x, z in ic], 0.25, 0.285)
        T.ext('underside', 'broken_concrete', inset(ic, 0.09), -0.02, 0.0)
        a, b, lift = tilts[i]
        blit(M, T, [('x', a, (cx, 0, cz)), ('z', b, (cx, 0, cz))], (0, lift, 0), f'p{i+1}_')
        M.det(f'p{i+1}_plate', 'slab fracture plate', (cx, 0.12, cz))
    for (x, z) in ((1.2, 1.0), (2.4, 1.6), (0.8, 2.2), (2.9, 0.7)):
        rebar(M, 'rebar', (x-0.25, 0.14, z-0.1), (x+0.25, 0.2, z+0.15)); rebar(M, 'rebar', (x-0.1, 0.14, z-0.3), (x+0.1, 0.18, z+0.3))
    for k in range(6): M.add('chips', 'broken_concrete', chunk(rnd.uniform(-0.3, 3.9), 0.05, rnd.uniform(-0.3, 3.0), 0.16, 0.08, 0.12, 190+k, 0.3, 0, rnd.uniform(0, 90), 0))
    M.cn('base', (1.8, 0, 1.4), (0, -1, 0))
    return M

def DESTROY_12():
    M = Model('DESTROY_12', 'destruction', 'Construction debris pile r~2.3 m: 20 concrete blocks, 16 bricks, 7 plastered panel shards, 5 timber beams, 9 protruding rebar spikes, mortar chunks; heap-shaped placement, no random triangles')
    rnd = random.Random(141)
    def hgt(r): return max(0.0, 1.15*(1-(r/2.5)**2))
    def place(n, fn):
        for k in range(n):
            a = rnd.uniform(0, 2*math.pi); r = 2.3*math.sqrt(rnd.random()); fn(k, r*math.cos(a), r*math.sin(a), hgt(r))
    place(20, lambda k, x, z, h: M.add('concrete_blocks', 'broken_concrete' if k % 2 else 'concrete_pale', chunk(x, h+0.1, z, rnd.uniform(0.3, 0.7), rnd.uniform(0.2, 0.4), rnd.uniform(0.3, 0.6), 200+k, 0.28, rnd.uniform(-20, 20), rnd.uniform(0, 180), rnd.uniform(-25, 25))))
    place(16, lambda k, x, z, h: M.add('bricks', 'brick_red', box(-0.11, -0.035, -0.05, 0.11, 0.035, 0.05, 0.005).rot('x', rnd.uniform(-40, 40)).rot('y', rnd.uniform(0, 180)).rot('z', rnd.uniform(-40, 40)).move(x, h+0.15, z)))
    place(7, lambda k, x, z, h: M.add('panels', 'plaster_cream', chunk(x, h+0.15, z, rnd.uniform(0.5, 0.9), 0.06, rnd.uniform(0.4, 0.7), 240+k, 0.15, rnd.uniform(-35, 35), rnd.uniform(0, 180), rnd.uniform(-40, 40))))
    place(5, lambda k, x, z, h: M.add('timber', 'timber_warm', beam((x-0.6, h+0.12, z-0.2), (x+0.6, h+0.12+rnd.uniform(0, 0.3), z+0.2), 0.1, 0.07)))
    for k in range(9):
        a = rnd.uniform(0, 2*math.pi); r = rnd.uniform(0.3, 1.8); x, z = r*math.cos(a), r*math.sin(a); h = hgt(r)
        rebar(M, 'rebar', (x, h+0.1, z), (x+rnd.uniform(-0.5, 0.5), h+rnd.uniform(0.7, 1.4), z+rnd.uniform(-0.5, 0.5)), 0.014)
    place(8, lambda k, x, z, h: M.add('mortar_chunks', 'mortar', chunk(x, h+0.05, z, 0.12, 0.07, 0.1, 280+k, 0.3, 0, rnd.uniform(0, 90), 0)))
    M.add('base_dust', 'dusty_stone', ext([(2.9*math.cos(a/6), 2.9*math.sin(a/6)) for a in range(0, 38) if False] or [(2.7*math.cos(math.radians(a))*rnd.uniform(0.9, 1.1), 2.7*math.sin(math.radians(a))*rnd.uniform(0.9, 1.1)) for a in range(0, 360, 30)], 0.0, 0.03))
    M.cn('base', (0, 0, 0), (0, -1, 0))
    return M

# ------------------------------------------------------------------ D13..D18
def brick(x, y, z, L=0.215, rot=(0, 0, 0), half=False, mat='brick_red'):
    P = box(-L/2, -0.0325, -0.05, L/2, 0.0325, 0.05, 0.004)
    return P

def DESTROY_13():
    M = Model('DESTROY_13', 'destruction', 'Brick rubble: 3 mortar-bonded wall fragments (staggered courses, jagged outlines, mortar beds) plus ~40 loose whole/half bricks and mortar crumbs')
    rnd = random.Random(151)
    def cluster(name, courses, base_len, ox, oy, oz, rots, seed):
        T = Model('t', 'x'); r = random.Random(seed); y = 0.0
        for c in range(courses):
            n = max(2, base_len-int(r.random()*3)-(c//2))
            off = 0.107 if c % 2 else 0.0
            for i in range(n):
                T.box('bricks', 'brick_red' if r.random() > 0.15 else 'brick_red', i*0.22+off, y, 0, i*0.22+off+0.215, y+0.065, 0.1, 0.004)
            T.box('mortar_bed', 'mortar', 0.005, y+0.065, 0.005, n*0.22+off-0.01, y+0.075, 0.095)
            y += 0.075
        blit(M, T, rots, (ox, oy, oz), name+'_')
    cluster('wall_A', 7, 8, -0.8, 0.0, 0.2, [('z', 6, (0, 0, 0)), ('y', 12, (0, 0, 0))], 1)
    cluster('wall_B', 5, 6, 0.9, 0.0, -0.9, [('y', -30, (0, 0, 0))], 2)
    cluster('wall_C_tilted', 4, 5, -0.4, 0.0, -1.2, [('x', 0, (0, 0, 0)), ('z', -78, (0, 0, 0)), ('y', 20, (0, 0, 0))], 3)
    for k in range(40):
        x = rnd.uniform(-2.0, 2.0); z = rnd.uniform(-1.8, 1.8); half = rnd.random() < 0.35
        L = 0.11 if half else 0.215
        P = box(-L/2, -0.0325, -0.05, L/2, 0.0325, 0.05, 0.004)
        if half: P = chunk(0, 0, 0, L, 0.065, 0.1, 300+k, 0.12)
        P.rot('y', rnd.uniform(0, 180)).rot('z', rnd.choice([0, 0, 0, 90, rnd.uniform(-30, 30)])).rot('x', rnd.uniform(-15, 15)).move(x, 0.06, z)
        M.add('loose_bricks', 'brick_red', P)
    for k in range(10): M.add('mortar_crumbs', 'mortar', chunk(rnd.uniform(-2, 2), 0.02, rnd.uniform(-1.8, 1.8), 0.08, 0.04, 0.07, 340+k, 0.35, 0, rnd.uniform(0, 90), 0))
    M.cn('base', (0, 0, 0), (0, -1, 0)); M.det('loose_bricks', 'loose bricks', None)
    return M

def DESTROY_14():
    M = Model('DESTROY_14', 'destruction', 'Glass shard collection: 30 angular shards (tri/quad/pent, 6-12 mm thick, 0.1-0.55 m) lying, leaning and wedged against 3 aluminium frame slivers')
    rnd = random.Random(161)
    for k in range(30):
        n = rnd.choice([3, 3, 4, 5]); r = rnd.uniform(0.06, 0.28)
        pts = []
        for i in range(n):
            a = 2*math.pi*i/n+rnd.uniform(-0.35, 0.35); rr = r*rnd.uniform(0.45, 1.25)
            pts.append((rr*math.cos(a)*rnd.uniform(0.6, 1.5), rr*math.sin(a)))
        P = ext(pts, 0.0, rnd.uniform(0.006, 0.012))
        stand = k < 6
        P.rot('x', rnd.uniform(60, 82) if stand else rnd.uniform(-14, 14)).rot('z', rnd.uniform(-20, 20)).rot('y', rnd.uniform(0, 360))
        lo = min(v[1] for v in P.V)
        P.move(rnd.uniform(-1.0, 1.0), -lo+0.003+(0.012 if k > 20 else 0.0), rnd.uniform(-0.9, 0.9))
        M.add('shards_standing' if stand else 'shards_flat', 'glass_tinted', P)
    for k in range(3):
        M.add('frame_slivers', 'brushed_metal', box(-0.35, 0.0, -0.025, 0.35, 0.05, 0.025, 0.004).rot('y', rnd.uniform(0, 180)).rot('z', rnd.uniform(-8, 8)).move(rnd.uniform(-0.8, 0.8), 0.02, rnd.uniform(-0.7, 0.7)))
    for k in range(18): M.add('glass_crumbs', 'glass_tinted', ext([(0, 0), (0.03, 0.01), (0.015, 0.035)], 0.0, 0.006).rot('y', rnd.uniform(0, 360)).move(rnd.uniform(-1.1, 1.1), 0.0, rnd.uniform(-1.0, 1.0)))
    M.cn('base', (0, 0, 0), (0, -1, 0))
    return M

def DESTROY_15():
    M = Model('DESTROY_15', 'destruction', 'Twisted structural steel I-beam 5.6 m: continuous 150-degree torsion, S-bend in two planes, crumpled flange widths, torn-off end flanges, end plate')
    n = 22; L = 5.6; rings = []
    poly0 = ibeam_poly(0.2, 0.38, 0.022, 0.014)
    def sm(t): return t*t*(3-2*t)
    pts = []
    for i in range(n+1):
        t = i/n
        pts.append((L*t, 0.55+0.3*math.sin(math.pi*t*1.3)-0.2*t, 0.35*math.sin(2*math.pi*t*0.9)))
    for i, c in enumerate(pts):
        t = i/n
        d = norm(sub(pts[min(i+1, n)], pts[max(i-1, 0)]))
        up = (0, 1, 0); u = norm(cross(up, d)); v = cross(d, u)
        th = math.radians(150*sm(min(1, max(0, (t-0.2)/0.6))))
        k = 1.0-0.18*abs(math.sin(t*14)) if 0.15 < t < 0.9 else 1.0
        taper = 1.0 if t > 0.04 else 0.0
        ring = []
        for a, b in poly0:
            a2 = a*k; aa = a2*math.cos(th)-b*math.sin(th); bb = a2*math.sin(th)+b*math.cos(th)
            ring.append((c[0]+u[0]*aa+v[0]*bb, c[1]+u[1]*aa+v[1]*bb, c[2]+u[2]*aa+v[2]*bb))
        rings.append(ring)
    M.add('beam', 'metal_painted_grey', loft(rings))
    p0 = pts[0]
    M.box('end_plate', 'galvanized_steel', -0.04, 0.55-0.28, -0.14, 0.0, 0.55+0.28, 0.14, 0.004)
    for dy, dz in ((-0.2, -0.09), (-0.2, 0.09), (0.2, -0.09), (0.2, 0.09)): M.add('bolts', 'brushed_metal', tube((-0.06, 0.55+dy, dz), (0.03, 0.55+dy, dz), 0.017, 6))
    M.add('torn_flange_a', 'rust_metal', box(0.0, 0.0, -0.1, 0.9, 0.022, 0.1, 0.003).rot('z', 18, (0, 0, 0)).rot('y', 25, (0, 0, 0)).move(L-0.4, 0.05, 0.9))
    M.add('torn_flange_b', 'rust_metal', box(0.0, 0.0, -0.1, 0.5, 0.022, 0.1, 0.003).rot('y', -40, (0, 0, 0)).move(L-1.4, 0.0, -0.9))
    M.add('far_end_tear', 'metal_painted_grey', chunk(pts[-1][0]+0.08, pts[-1][1], pts[-1][2], 0.18, 0.3, 0.16, 12, 0.35))
    M.add('support_block', 'concrete_weathered', box(1.0, 0.0, -0.45, 1.5, 0.45, 0.45, 0.02)) if False else None
    M.cn('end_plate', (0, 0.55, 0), (-1, 0, 0)); M.det('beam', 'beam', None)
    return M

def splintered_top(M, g, x, z, r0, r1, y0, y1, rnd, seg=10, mat='wood_weathered', amp=0.5):
    rings = [circ(r0, y0, seg, x, z, 0.2), circ((r0+r1)/2, (y0+y1)/2, seg, x, z, 0.2)]
    top = []
    for i in range(seg):
        a = 0.2+2*math.pi*i/seg; top.append((x+r1*math.cos(a), y1+rnd.uniform(-amp*0.5, amp)*(1+(i % 2)), z+r1*math.sin(a)))
    rings.append(top)
    M.add(g, mat, loft(rings))
    for i in range(0, seg, 2):
        a = 0.2+2*math.pi*i/seg; px, py, pz = top[i]
        M.add(g+'_splinters', mat, tube((px, py, pz), (px+0.05*math.cos(a), py+rnd.uniform(0.25, 0.55), pz+0.05*math.sin(a)), 0.035, 4, 0.006))

def DESTROY_16():
    M = Model('DESTROY_16', 'destruction', 'Snapped wooden utility pole: 2.8 m stump with splintered fracture + splinters; 7 m upper section fallen leaning, splintered lower end, crossarm with insulators, severed cables draped; stump and upper section are separate groups')
    rnd = random.Random(171)
    splintered_top(M, 'stump', 0, 0, 0.2, 0.17, 0.0, 2.8, rnd)
    M.add('ground_sleeve', 'rubber_dark', cyl(0.215, 0.5, 10, 0.0, 0, 0))
    M.box('pole_staples', 'galvanized_steel', 0.16, 0.8, -0.02, 0.19, 2.6, 0.02, 0.004)
    U = Model('t', 'x')
    splintered_top(U, 'upper_section', 0, 0, 0.17, 0.12, 0.0, 7.0, random.Random(5), 10, amp=0.0)
    # fracture end at y=0 (jagged): rebuild bottom ring jag
    U.add('upper_fracture_cap', 'timber_warm', chunk(0, 0.0, 0, 0.3, 0.18, 0.3, 4, 0.3))
    U.box('crossarm', 'timber_warm', -1.2, 6.3, -0.07, 1.2, 6.45, 0.07, 0.015)
    for s in (-1, 1): U.add('crossarm_brace', 'timber_warm', beam((s*0.1, 5.6, 0.1), (s*0.8, 6.3, 0.1), 0.06, 0.06))
    for x in (-1.0, 0.0, 1.0):
        T2 = Model('x', 'x'); 
        from props import insulator
        insulator(U, 'insulators', x, 6.45, 0, 0.3, 0.07)
    blit(M, U, [('z', -68, (0, 0, 0)), ('y', 20, (0, 0, 0))], (0.55, 2.55, 0.0), '')
    # cables: from insulators sagging to ground
    ends = []
    for x in (-1.0, 0.0, 1.0):
        P = Part(); a = (x, 6.8, 0.0)
        p = Part(); q = Part()
        T3 = Model('x', 'x')
        import copy
        pp = tube((x, 6.75, 0.0), (x, 6.76, 0.0), 0.001, 3)
        ends.append(x)
    cab = Model('t', 'x')
    for i, x in enumerate((-1.0, 0.0, 1.0)):
        cab.add('cable', 'cable_black', bent_tube([(x, 6.75, 0), (x+0.3, 6.0, 0.4), (x+0.5, 4.8, 0.8)], 0.02, 5))
    blit(M, cab, [('z', -68, (0, 0, 0)), ('y', 20, (0, 0, 0))], (0.55, 2.55, 0.0))
    for i in range(3):
        M.add('cable_on_ground', 'cable_black', bent_tube([(2.4+i*0.3, 0.05, 1.8-i*0.4), (3.2+i*0.3, 0.04, 2.3-i*0.4), (4.1+i*0.3, 0.04, 2.0-i*0.4), (5.0+i*0.3, 0.04, 2.6-i*0.4)], 0.02, 5))
    for k in range(5): M.add('splinter_chips', 'wood_weathered', chunk(rnd.uniform(-0.8, 1.5), 0.04, rnd.uniform(-0.8, 0.8), 0.25, 0.05, 0.06, 360+k, 0.35, 0, rnd.uniform(0, 180), 0))
    M.det('upper_section', 'upper pole', (0.55, 2.55, 0)); M.det('crossarm', 'crossarm', None); M.det('insulators', 'insulators', None); M.det('stump', 'stump', (0, 0, 0)); M.det('cable', 'cables', None)
    M.cn('stump_base', (0, 0, 0), (0, -1, 0)); M.cn('upper_fracture', (0.55, 2.55, 0), (0, 1, 0))
    return M

def DESTROY_17():
    M = Model('DESTROY_17', 'destruction', 'Broken metal railing 3 m: 4 posts (intact / bent 22 deg / snapped at 0.4 m / leaning), top & mid rails kinked, snapped and drooping, detached rail piece, bent balusters, flattened tube ends')
    rnd = random.Random(181)
    zs = [0.0, 1.0, 2.0, 3.0]
    for z in zs: 
        M.box('base_plate', 'galvanized_steel', -0.1, 0, z-0.1, 0.1, 0.02, z+0.1, 0.004); bolts(M, 'base_plate', [(-0.07, z-0.07), (0.07, z-0.07), (-0.07, z+0.07), (0.07, z+0.07)], 0.02, 0.012, 0.015)
    M.box('post_1', 'paint_navy', -0.04, 0.02, -0.04, 0.04, 1.1, 0.04, 0.008)
    M.add('post_2_bent', 'paint_navy', merge([beam((0, 0.02, 1.0), (0, 0.6, 1.0), 0.08, 0.08), beam((0, 0.6, 1.0), (0.25, 1.0, 1.12), 0.08, 0.08)]))
    M.box('post_3_stub', 'paint_navy', -0.04, 0.02, 1.96, 0.04, 0.4, 2.04, 0.008); M.add('post_3_stub', 'paint_navy', chunk(0, 0.43, 2.0, 0.09, 0.08, 0.09, 4, 0.35))
    M.add('post_3_fallen', 'paint_navy', box(-0.04, 0.0, -0.04, 0.04, 0.8, 0.04, 0.008).rot('x', 82, (0, 0, 0)).rot('y', -25, (0, 0, 0)).move(0.45, 0.05, 2.4))
    M.add('post_4_lean', 'paint_navy', box(-0.04, 0.02, -0.04, 0.04, 1.1, 0.04, 0.008).rot('x', -17, (0, 0.02, 3.0)).move(0, 0, 3.0))
    M.add('rail_top_12', 'galvanized_steel', bent_tube([(0, 1.1, 0), (0.05, 1.08, 0.5), (0.2, 1.1, 0.8), (0.25, 1.0, 1.12)], 0.035, 8))
    M.add('rail_top_2_hang', 'galvanized_steel', bent_tube([(0.25, 1.0, 1.12), (0.3, 0.8, 1.5), (0.35, 0.45, 1.9), (0.3, 0.12, 2.1)], 0.035, 8))
    M.add('rail_top_4_stub', 'galvanized_steel', tube((0.0, 1.1+0.05, 3.0-0.02), (0.1, 1.08, 2.45), 0.035, 8)); M.add('rail_end_flat', 'galvanized_steel', box(-0.04, 1.05, 2.4, 0.2, 1.1, 2.5, 0.004).rot('y', 15, (0, 1.08, 2.45)))
    M.add('rail_detached', 'galvanized_steel', tube((0.6, 0.04, 0.4), (0.9, 0.04, 1.3), 0.035, 8)); M.add('rail_detached', 'galvanized_steel', tube((0.9, 0.04, 1.3), (1.1, 0.04, 1.6), 0.035, 8))
    M.add('rail_mid_12', 'paint_navy', tube((0, 0.6, 0), (0.0, 0.6, 0.98), 0.025, 6)); M.add('rail_mid_23_snapped', 'paint_navy', bent_tube([(0.12, 0.6, 1.0), (0.15, 0.4, 1.35), (0.15, 0.2, 1.5)], 0.025, 6))
    for z, bent in ((0.15, False), (0.3, True), (0.45, False), (0.6, False), (0.75, True), (0.9, False)):
        if bent: M.add('baluster_bent', 'paint_navy', bent_tube([(0, 0.15, z), (0.0, 0.6, z), (0.1, 1.05, z+0.1)], 0.011, 4))
        else: M.add('baluster', 'paint_navy', tube((0, 0.15, z), (0, 1.1, z), 0.011, 4))
    M.add('baluster_fallen', 'paint_navy', tube((0.5, 0.02, 2.6), (0.7, 0.02, 3.4), 0.011, 4)); M.add('baluster_fallen', 'paint_navy', tube((0.8, 0.02, 2.2), (0.9, 0.02, 2.9), 0.011, 4))
    M.cn('bay_end_A', (0, 0, 0), (0, 0, -1)); M.cn('bay_end_B', (0, 0, 3), (0, 0, 1))
    for n in ('post_2_bent', 'rail_top_12', 'rail_detached', 'post_3_fallen'): M.det(n, 'railing part', None)
    return M

def DESTROY_18():
    M = Model('DESTROY_18', 'destruction', 'Collapsed skybridge segment 8 x 2.8 m: steel Warren side trusses (one buckled), floor deck with torn end, partly glazed canopy with shattered panels, interior handrails, torn connection plates, tilted 13 deg onto debris; glazing, railing, truss groups separable')
    rnd = random.Random(191)
    T = Model('t', 'x')
    L = 8.0; W = 2.8
    T.box('deck', 'concrete_weathered', -W/2, 0.0, -L/2, W/2, 0.22, L/2, 0.03)
    T.box('deck_finish', 'concrete_pale', -W/2+0.1, 0.22, -L/2+0.05, W/2-0.1, 0.25, L/2-0.05, 0.01)
    for z in [-3.2, -1.6, 0.0, 1.6, 3.2]: T.box('floor_joists', 'metal_painted_grey', -W/2, -0.25, z-0.06, W/2, 0.0, z+0.06, 0.01)
    for s in (-1, 1):
        x = s*W/2
        class _M: pass
        TM = Model('tr', 'x')
        truss_plane = __import__('harbor').truss_plane
        truss_plane(TM, 'truss', 'metal_painted_grey', (x, 0.25, -L/2), (x, 0.25, L/2), 2.4, 8, 0.12)
        for (g, m), p in TM.groups.items(): T.add('truss_R' if s > 0 else 'truss_L', m, p)
        # glazing panels between verticals
        for i in range(8):
            z0 = -L/2+L*i/8+0.08; z1 = -L/2+L*(i+1)/8-0.08
            if s < 0 and i in (2, 3, 6): 
                pts = [(z0, 0.35), (z0+0.35, 0.35), (z0, 1.2)]
                T.add('glazing_shards_L', 'glass_tinted', pxy([(a, b) for a, b in pts], x-0.01, x+0.01).rot('y', 0))
                continue
            if s > 0 and i in (1, 5): continue
            T.box('glazing_R' if s > 0 else 'glazing_L', 'glass_tinted', x-0.012, 0.35, z0, x+0.012, 2.4, z1)
        T.add('handrail_R' if s > 0 else 'handrail_L', 'brushed_metal', tube((s*(W/2-0.12), 1.0, -L/2+0.1), (s*(W/2-0.12), 1.0, L/2-0.1), 0.03, 8))
        for z in (-3.5, -1.75, 0, 1.75, 3.5): T.box('handrail_R' if s > 0 else 'handrail_L', 'brushed_metal', s*(W/2-0.12)-0.025, 0.25, z-0.025, s*(W/2-0.12)+0.025, 1.0, z+0.025, 0.004)
    T.box('roof_frame', 'metal_painted_grey', -W/2-0.1, 2.65, -L/2, W/2+0.1, 2.75, L/2, 0.02)
    for i in range(6):
        z0 = -L/2+L*i/6+0.05; z1 = -L/2+L*(i+1)/6-0.05
        if i in (1, 4): continue
        T.box('roof_glazing', 'glass_tinted', -W/2+0.1, 2.75, z0, W/2-0.1, 2.78, z1)
    for z in [-L/2+L*i/6 for i in range(7)]: T.box('roof_ribs', 'metal_painted_grey', -W/2-0.1, 2.5, z-0.05, W/2+0.1, 2.75, z+0.05, 0.01)
    for s in (-1, 1): T.add('roof_edge_bent', 'metal_painted_grey', box(s*(W/2+0.1)-0.05, 2.65, -L/2, s*(W/2+0.1)+0.05, 2.78, L/2, 0.01))
    # torn connection end (z=-L/2): plates + bolts
    for x in (-1.0, 0.0, 1.0): T.box('conn_plates', 'galvanized_steel', x-0.15, 0.0, -L/2-0.06, x+0.15, 0.4, -L/2, 0.01); T.add('conn_bolts', 'brushed_metal', tube((x, 0.2, -L/2-0.09), (x, 0.2, -L/2+0.03), 0.03, 6))
    # jagged deck end broken into teeth at z=+L/2
    for k in range(5): T.add('deck_teeth', 'concrete_core', chunk(-1.1+k*0.55, 0.1, L/2+0.18, 0.3, 0.22, 0.4, 400+k, 0.3))
    blit(M, T, [('x', -13, (0, 0, -L/2)), ('z', 3, (0, 0, 0))], (0.0, 0.0, L/2))
    # rubble support under raised end + debris
    for k in range(10): M.add('rubble', 'broken_concrete' if k % 2 else 'concrete_pale', chunk(rnd.uniform(-1.6, 1.6), 0.2+rnd.uniform(0, 0.6), rnd.uniform(5.2, 7.8), rnd.uniform(0.4, 0.9), rnd.uniform(0.3, 0.6), rnd.uniform(0.4, 0.8), 420+k, 0.28, rnd.uniform(-15, 15), rnd.uniform(0, 180), rnd.uniform(-20, 20)))
    for k in range(2): rebar(M, 'rebar', (-0.9+k*1.8, 0.5, 7.9), (-0.7+k*1.8, 1.2, 8.8), 0.02)
    # detached railing sections and glass lying on ground
    M.add('handrail_detached', 'brushed_metal', tube((2.2, 0.06, 1.0), (2.7, 0.06, 3.4), 0.03, 8)); M.add('handrail_detached', 'brushed_metal', tube((-2.2, 0.06, 2.2), (-1.9, 0.06, 4.0), 0.03, 8))
    M.add('glazing_fallen', 'glass_tinted', box(-0.5, 0.0, -0.01, 0.5, 1.0, 0.01, 0.0).rot('x', 78, (0, 0, 0)).rot('y', 20, (0, 0, 0)).move(2.9, 0.02, 4.4)) if False else M.add('glazing_fallen', 'glass_tinted', box(-0.45, 0.0, -0.012, 0.45, 0.9, 0.012).rot('x', 82, (0, 0, 0)).rot('y', 20, (0, 0, 0)).move(2.8, 0.02, 4.4))
    for k in range(10): M.add('glass_shards', 'glass_tinted', ext([(0, 0), (rnd.uniform(0.08, 0.2), rnd.uniform(0, 0.08)), (rnd.uniform(0, 0.1), rnd.uniform(0.08, 0.22))], 0.0, 0.008).rot('y', rnd.uniform(0, 360)).move(rnd.uniform(-2.8, 2.8), 0.0, rnd.uniform(1.0, 5.0)))
    M.add('truss_fallen_member', 'metal_painted_grey', beam((-3.0, 0.1, 5.0), (-2.2, 0.1, 6.4), 0.12, 0.12))
    M.cn('conn_end_fixed', (0, 0, 0), (0, 0, -1)); M.cn('conn_end_free', (0, 1.75, 8.0), (0, 0, 1))
    for n in ('truss_L', 'truss_R', 'glazing_R', 'glazing_L', 'handrail_R', 'handrail_L', 'roof_glazing', 'deck', 'handrail_detached'): M.det(n, 'skybridge part (separately animatable)', (0, 0.5, 0))
    return M

DESTROY = [DESTROY_01, DESTROY_02, DESTROY_03, DESTROY_04, DESTROY_05, DESTROY_06, DESTROY_07, DESTROY_08, DESTROY_09, DESTROY_10, DESTROY_11, DESTROY_12, DESTROY_13, DESTROY_14, DESTROY_15, DESTROY_16, DESTROY_17, DESTROY_18]
