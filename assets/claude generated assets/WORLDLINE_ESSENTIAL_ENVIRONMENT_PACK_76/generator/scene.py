import json, os, sys, math, time, collections
import numpy as np
from PIL import Image
from lib import *
from pack import CATS, ROOT, build_models
from render import load_obj, render

FN = {fn.__name__: fn for c, l in CATS for fn in l}
_cache = {}
def get(n):
    if n not in _cache: _cache[n] = FN[n]()
    return _cache[n]

items = []      # (name, x, y, z, ry, scale, matmap)
def P(n, x, z, ry=0, y=0.0, sc=1.0, mm=None): items.append((n, x, y, z, ry, sc, mm))

# ------------------------------------------------------------------ road network (all connect on the 12 m grid)
P('ROAD_05', 0, 0)
for k in (1, 2):
    P('ROAD_01', 0, 12*k); P('ROAD_01', 0, -12*k); P('ROAD_01', -12*k, 0, 90)
for k in (1, 2): P('ROAD_01', 12*k, 0, 90)
P('ROAD_04', 36, 0, 90)                                  # T-junction: arms S,W,N (closed east)
P('ROAD_09', 36, 12); P('ROAD_09', 36, -12); P('ROAD_09', 36, -24)
P('ROAD_09', 36, 24) if False else None
# sidewalks (ROAD_12 offset 0.65 from the 12 m grid by corner module size) and corners (ROAD_13)
for sd in (1, -1):
    for k in (0, 1):
        z = sd*(12.65+12*k)
        P('ROAD_12', 5.15, z, 0); P('ROAD_12', -5.15, z, 180)
        P('ROAD_12', -z if False else sd*-(12.65+12*k)*1, 5.15, 270) if False else None
for k in (0, 1):
    x = -(12.65+12*k)
    P('ROAD_12', x, 5.15, 270); P('ROAD_12', x, -5.15, 90)
for k in (0, 1):
    pass
for ang in (0, 90, 180, 270): P('ROAD_13', 0, 0, ang)
# east arm sidewalks (22.7 m between main corners and T corners -> 2 strips scaled 0.946 on length)
for z, ry in ((5.15, 270), (-5.15, 90)):
    for x in (12.325, 23.675): items.append(('ROAD_12', x, 0.0, z, ry, ('z', 11.35/12), None))
P('ROAD_13', 36, 0, 180); P('ROAD_13', 36, 0, 270)       # SW + NW corners of the T (fillets exist on those corners)
for k in (0, 1):
    z = 12.65+12*k
    P('ROAD_12', 36-5.15, z, 180)
    P('ROAD_12', 36-5.15, -z, 180)

# ------------------------------------------------------------------ street furniture
for z in (14, 26, -14, -26):
    P('PROP_03', 4.3, z, 180, 0.15); P('PROP_03', -4.3, z, 0, 0.15)
for x in (-14, -26):
    P('PROP_03', x, 4.3, 90, 0.15); P('PROP_03', x, -4.3, 270, 0.15)
P('PROP_01', 4.3, 4.3, 180, 0.15); P('PROP_01', -4.3, -4.3, 0, 0.15); P('PROP_01', -4.3, 4.3, 90, 0.15); P('PROP_01', 4.3, -4.3, 270, 0.15)
P('PROP_02', 3.95, 5.6, 270, 0.15); P('PROP_02', -3.95, -5.6, 90, 0.15)
P('PROP_13', 6.2, 4.0, 0, 0.15); P('PROP_13', -6.2, -4.0, 180, 0.15)
P('PROP_05', 5.6, 20, 270, 0.15)
P('PROP_06', 6.0, 11.0, 270, 0.15); P('PROP_06', -6.0, 18.0, 90, 0.15); P('PROP_06', 6.0, -12.0, 270, 0.15)
P('PROP_07', 4.4, 16.5, 0, 0.15); P('PROP_07', -4.4, 11.0, 0, 0.15); P('PROP_07', 4.4, -9.5, 0, 0.15)
P('PROP_08', 4.4, 9.5, 0, 0.15); P('PROP_08', -4.4, -16, 0, 0.15)
for z in (7.8, 9.0, 10.2): pass
for i in range(3): P('PROP_09', 3.9, -7.5-i*1.0, 0, 0.15)
P('PROP_17', 5.9, 25, 0, 0.15); P('PROP_17', -5.9, 8.5, 0, 0.15)
for z in (22.5, 23.7): P('PROP_18', 4.3, z, 270, 0.15)
P('PROP_15', -5.9, 14, 90, 0.15); P('PROP_16', -5.9, 22, 90, 0.15); P('PROP_16', -5.9, 26, 90, 0.15)
P('PROP_14', -22, 14, 0, 0.0)                                         # billboard on the west lot
# road-works closure on the south arm
for z in (-16.0, -19.2, -22.4): P('PROP_11', 1.7, z, 0, 0.0)
for z in (-14.0, -14.8, -15.6): P('PROP_12', 2.2, z, 0, 0.0)
P('PROP_10', -3.9, -32, 0, 0.0) if False else None
for z in (-9, -6): pass
for k in range(6): P('PROP_10', 3.62+0.0, 30-0, 0, 0.0) if False else None
# promenade railings (HARBOR_12) on the ROAD_09 parapet + highway-style guardrail across the lot edge
for k in range(4): P('HARBOR_12', 43.68, 7.5+3*k, 0, 0.73)
for z in (-18, -21, -24, -27, -30): pass
for k in range(8): P('HARBOR_12', 43.68, -6.5-3*k if False else -(7.5+3*k), 0, 0.73)

# ------------------------------------------------------------------ utilities
P('UTILITY_01', -8.5, 14); P('UTILITY_01', -8.5, 30); P('UTILITY_02', -8.5, 22); P('UTILITY_01', -8.5, -14)
P('UTILITY_03', -10, -22, 90); P('UTILITY_12', -9.5, -26, 90); P('UTILITY_05', -9.0, -34, 90)
P('UTILITY_04', -38, 36, 0); P('UTILITY_06', -30, -22, 0)
P('UTILITY_10', -30, 12, 0); P('UTILITY_11', -7.0, -24.5, 90)
for x, n in ((-22, 'UTILITY_07'), (-26, 'UTILITY_09'), (-18, 'UTILITY_08')):
    P('PROP_16', x, 26, 0, 0.0) if False else None
    items.append(('PLINTH', x, 0, 28, 0, 1.0, None)); P(n, x, 28, 0, 0.35)

# ------------------------------------------------------------------ harbor (+X side, water at y=-2.6)
WY = -2.6
for z in (-24, -12, 0): P('HARBOR_04', 45.4, z, 0, -2.2)
P('HARBOR_02', 51.6, -4, 90, -1.9); P('HARBOR_01', 51.6, -14, 90, -1.5)
P('HARBOR_03', 54.0, 2.5, 90, WY); P('HARBOR_13', 54.0, -19.0, 90, WY); P('HARBOR_13', 54.0, -22.0, 90, WY)
for (bx, bz) in ((48.6, -1.8), (54.6, -1.8), (48.6, -6.2), (54.6, -6.2)): P('HARBOR_08', bx, bz, 0, -0.28)
P('HARBOR_09', 72, -12, 0, WY); P('HARBOR_09', 96, 4, 0, WY); P('HARBOR_09', 70, 50, 0, WY)
P('HARBOR_05', 88, -22, 0, -4.2); P('HARBOR_05', 88, -10, 0, -4.2); P('HARBOR_06', 88, -27.5, 0, -1.3, 0.45)
P('HARBOR_14', 66, 22, 0, 0.0); P('HARBOR_07', 86, 12, 0, 0.0)
P('HARBOR_11', 88.0, 30, 90, 0.0)
cm = ['container_blue', 'container_red', 'container_green', 'container_orange']
n = 0
for z, row in ((10.5, (3, 2, 3)), (13.7, (2, 3, 1)), (34.8, (2, 1, 2))):
    for xi, h in zip((50.5, 63.5, 76.5), row):
        for lv in range(h):
            P('HARBOR_10', xi+(0.15 if lv % 2 else 0), z, 90, lv*2.59, 1.0, {'container_blue': cm[(n) % 4]}); n += 1
P('HARBOR_10', 66, 42, 90, 6.2, 1.0, {'container_blue': 'container_red'})      # container hanging from the gantry spreader
for k in range(4): P('HARBOR_08', 62+k*5.0, 39.4, 0, 0.0) if False else None
for k in range(5): P('HARBOR_08', 50+k*9.0, 39.2, 0, 0.0)

# ------------------------------------------------------------------ separate damaged-area showcase
DX0, DZ0 = -30, -48
order = [f'DESTROY_{i:02d}' for i in range(1, 19)]
D_POS = {}
for i, nme in enumerate(order):
    col = i % 6; row = i//6
    x = DX0+col*9.5+(2.0 if nme in ('DESTROY_01', 'DESTROY_02') else 0); z = DZ0-row*9.0
    D_POS[nme] = (x, z)
    ry = {'DESTROY_02': 0, 'DESTROY_10': 0, 'DESTROY_09': 0}.get(nme, 0)
    off = {'DESTROY_01': (-2, 0), 'DESTROY_02': (0, 0), 'DESTROY_09': (-2, 0), 'DESTROY_10': (-3, 0), 'DESTROY_11': (-1.8, -1.4), 'DESTROY_15': (-2.8, 0), 'DESTROY_04': (0, 0), 'DESTROY_08': (0, 0), 'DESTROY_13': (0, 0), 'DESTROY_16': (-0.6, 0), 'DESTROY_17': (0, -1.5), 'DESTROY_18': (0, -3.0), 'DESTROY_06': (0, -1.5), 'DESTROY_05': (0, 0), 'DESTROY_07': (0, 0), 'DESTROY_12': (0, 0), 'DESTROY_14': (0, 0), 'DESTROY_03': (0, 0)}[nme]
    P(nme, x+off[0], z+off[1], ry)

# ------------------------------------------------------------------ assembly
def solid(group, mat, x0, y0, z0, x1, y1, z1): return (group, mat, box(x0, y0, z0, x1, y1, z1))

def assemble():
    out = []
    # terrain / water / quay slab (scene-only, not part of the 76)
    out.append(('terrain', 'ground_tan', box(-80, -0.6, -80, 44.0, -0.02, 110)))
    out.append(('terrain', 'concrete_weathered', box(-34, -0.6, -66, 26, -0.01, -39)))      # damaged-area pad
    out.append(('lawn', 'grass_muted', box(7.0, -0.03, 7.0, 29.0, 0.0, 60.0)))
    out.append(('lawn', 'grass_muted', box(-60, -0.03, 7.0, -7.0, 0.0, 60.0)))
    out.append(('lawn', 'grass_muted', box(-60, -0.03, -38.0, -7.0, 0.0, -7.0)))
    out.append(('lawn', 'grass_muted', box(7.0, -0.03, -38.0, 29.0, 0.0, -7.0)))
    out.append(('lawn', 'grass_muted', box(-60, -0.03, -7.0, -7.0, 0.0, 7.0)) if False else ('lawn', 'grass_muted', box(7.0, -0.03, -7.0, 29.0, 0.0, -7.0+0.01)))
    out.append(('water', 'sea_deep', box(46, -3.6, -90, 170, WY, 110)))
    out.append(('quay', 'concrete_pale', box(44.0, -2.6, 6.0, 92.0, 0.0, 40.0)))
    out.append(('quay_edge', 'rubber_dark', box(44.0, -1.4, 39.9, 92.0, -0.4, 40.15)))
    out.append(('quay_edge', 'rubber_dark', box(91.9, -1.4, 6.0, 92.15, -0.4, 40.0)))
    for x in range(46, 92, 4): out.append(('quay_joints', 'concrete_weathered', box(x, 0.0, 6.0, x+0.05, 0.012, 40.0)))
    for z in range(10, 40, 4): out.append(('quay_joints', 'concrete_weathered', box(44.0, 0.0, z, 92.0, 0.012, z+0.05)))
    out.append(('plinth', 'concrete_pale', box(-29, 0.0, 26.5, -15.0, 0.35, 29.5)))
    for (n, x, y, z, ry, sc, mm) in items:
        if n == 'PLINTH': continue
        M = get(n)
        for (g, m), p in M.groups.items():
            q = p.copy()
            if isinstance(sc, tuple): q.scale(1.0, 1.0, sc[1])
            elif sc != 1.0: q.scale(sc)
            if ry: q.rot('y', ry)
            q.move(x, y, z)
            out.append((f'{n}_{len(out)}_{g}', (mm or {}).get(m, m), q))
    return out

def world_conn(n, x, y, z, ry):
    M = get(n); res = []
    c, s = math.cos(math.radians(ry)), math.sin(math.radians(ry))
    def tr(p): return (p[0]*c+p[2]*s+x, p[1]+y, -p[0]*s+p[2]*c+z)
    for cn in M.conn:
        d = cn['direction']; p = cn['position']
        res.append((n, cn['name'], tr(p), (d[0]*c+d[2]*s, d[1], -d[0]*s+d[2]*c), cn.get('carriageway_width')))
    return res

def check_road_connections():
    roads = [(n, x, y, z, ry) for (n, x, y, z, ry, sc, mm) in items if n in ('ROAD_01', 'ROAD_04', 'ROAD_05', 'ROAD_09')]
    pts = []
    for r in roads:
        for c in world_conn(*r):
            if c[4]: pts.append(c)
    ok = 0; open_ends = []
    for i, a in enumerate(pts):
        match = [b for j, b in enumerate(pts) if j != i and math.dist(a[2], b[2]) < 0.01 and (a[3][0]*b[3][0]+a[3][2]*b[3][2]) < -0.99 and abs(a[4]-b[4]) < 1e-6]
        if match: ok += 1
        else: open_ends.append((a[0], a[1], tuple(round(v, 2) for v in a[2])))
    return len(pts), ok, open_ends

def write_scene_obj(parts, path):
    S = Model('SHOWCASE_SCENE', 'showcase', 'Assembled coastal city intersection + harbor + damaged-area showcase')
    for g, m, p in parts: S.add(g, m, p)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    S.write(os.path.dirname(path))
    return S

def view(V, T, C, EM, GL, eye, tgt, size, fov, name, **k):
    im = render(V, T, C, EM, GL, eye, tgt, size, fov=fov, ss=2, ground=False, shadow_y=0.0, **k)
    im.save(f'{ROOT}/previews/showcase/{name}.png'); return im

if __name__ == '__main__':
    t0 = time.time()
    os.makedirs(f'{ROOT}/previews/showcase', exist_ok=True); os.makedirs(f'{ROOT}/showcase', exist_ok=True)
    tot, ok, op = check_road_connections()
    print('road connection check: points', tot, 'matched', ok, 'open', len(op))
    json.dump(dict(connection_points=tot, matched=ok, open_ends=op), open('/tmp/scene_conn.json', 'w'))
    parts = assemble(); S = write_scene_obj(parts, f'{ROOT}/showcase/SHOWCASE_SCENE.obj')
    print('scene tris', S.tri_count(), round(time.time()-t0, 1), 's')
    V, T, C, EM, GL = load_obj(f'{ROOT}/showcase/SHOWCASE_SCENE.obj')
    views = {
      '01_street_level': ((-9.0, 1.7, -17.5), (6.0, 2.6, 6.0), (1600, 900), 62),
      '02_elevated_urban': ((-38.0, 36.0, 40.0), (20.0, 0.0, 2.0), (1600, 900), 52),
      '03_harbor_panorama': ((30.0, 14.0, -34.0), (68.0, 3.0, 12.0), (1920, 800), 62),
      '05_modular_road_network_test': ((15.0, 15.0, -13.0), (2.0, 0.0, 3.0), (1600, 900), 48),
      '04_destruction_closeup': ((-27.5, 2.3, -42.0), (-17.0, 1.2, -55.0), (1600, 900), 58),
    }
    for nme, (e, t, sz, fov) in views.items():
        view(V, T, C, EM, GL, np.array(e, float), np.array(t, float), sz, fov, nme); print('rendered', nme, round(time.time()-t0, 1), 's')
