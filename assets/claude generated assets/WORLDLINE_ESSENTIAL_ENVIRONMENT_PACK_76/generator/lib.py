"""WORLDLINE LAB - Asset Pack 02 procedural modelling kit.
Units: metres. Y-up. Right-handed. Flat-shaded (faceted) output with per-face normals."""
import math, os, random
from collections import OrderedDict

# ---------------------------------------------------------------- vector utils
def sub(a, b): return (a[0]-b[0], a[1]-b[1], a[2]-b[2])
def add(a, b): return (a[0]+b[0], a[1]+b[1], a[2]+b[2])
def mul(a, k): return (a[0]*k, a[1]*k, a[2]*k)
def dot(a, b): return a[0]*b[0]+a[1]*b[1]+a[2]*b[2]
def cross(a, b): return (a[1]*b[2]-a[2]*b[1], a[2]*b[0]-a[0]*b[2], a[0]*b[1]-a[1]*b[0])
def norm(a):
    l = math.sqrt(dot(a, a))
    return (a[0]/l, a[1]/l, a[2]/l) if l > 1e-12 else (0.0, 0.0, 0.0)
def centroid(pts):
    n = len(pts)
    return (sum(p[0] for p in pts)/n, sum(p[1] for p in pts)/n, sum(p[2] for p in pts)/n)
def newell(poly):
    n = [0.0, 0.0, 0.0]
    for i in range(len(poly)):
        p = poly[i]; q = poly[(i+1) % len(poly)]
        n[0] += (p[1]-q[1])*(p[2]+q[2]); n[1] += (p[2]-q[2])*(p[0]+q[0]); n[2] += (p[0]-q[0])*(p[1]+q[1])
    return tuple(n)

def triangulate(V, idx):
    """Ear-clip a (possibly concave) planar polygon, preserving its winding."""
    n = len(idx)
    if n < 3: return []
    if n == 3: return [tuple(idx)]
    pts = [V[i] for i in idx]
    nv = newell(pts)
    ax = max(range(3), key=lambda i: abs(nv[i]))
    if abs(nv[ax]) < 1e-12: return []
    if ax == 0: p2 = [(p[1], p[2]) for p in pts]
    elif ax == 1: p2 = [(p[2], p[0]) for p in pts]
    else: p2 = [(p[0], p[1]) for p in pts]
    sgn = 1 if nv[ax] > 0 else -1
    order = list(range(n)) if sgn > 0 else list(range(n))[::-1]
    def cr(a, b, c): return (p2[b][0]-p2[a][0])*(p2[c][1]-p2[a][1])-(p2[b][1]-p2[a][1])*(p2[c][0]-p2[a][0])
    def inside(a, b, c, p):
        d1 = cr(a, b, p); d2 = cr(b, c, p); d3 = cr(c, a, p)
        return d1 >= -1e-12 and d2 >= -1e-12 and d3 >= -1e-12
    tris = []; L = order[:]; guard = 0
    while len(L) > 3 and guard < 10000:
        guard += 1; found = False
        m = len(L)
        for i in range(m):
            a, b, c = L[i-1], L[i], L[(i+1) % m]
            if cr(a, b, c) <= 1e-12: continue
            if any(inside(a, b, c, q) for q in L if q not in (a, b, c)): continue
            tris.append((a, b, c)); L.pop(i); found = True; break
        if not found:
            # degenerate / collinear: drop a collinear vertex or fan
            for i in range(m):
                a, b, c = L[i-1], L[i], L[(i+1) % m]
                if abs(cr(a, b, c)) <= 1e-12: L.pop(i); found = True; break
            if not found:
                for i in range(1, len(L)-1): tris.append((L[0], L[i], L[i+1]))
                L = []; break
    if len(L) == 3: tris.append((L[0], L[1], L[2]))
    out = []
    for a, b, c in tris:
        t = (idx[a], idx[b], idx[c])
        out.append(t if sgn > 0 else (t[2], t[1], t[0]))
    return out

# ---------------------------------------------------------------- Part
class Part:
    def __init__(s, V=None, F=None): s.V = list(V or []); s.F = list(F or [])
    def copy(s): return Part(s.V, s.F)
    def move(s, x=0, y=0, z=0):
        s.V = [(a+x, b+y, c+z) for a, b, c in s.V]; return s
    def scale(s, sx, sy=None, sz=None):
        sy = sx if sy is None else sy; sz = sx if sz is None else sz
        s.V = [(a*sx, b*sy, c*sz) for a, b, c in s.V]; return s
    def rot(s, ax, deg, p=(0, 0, 0)):
        c = math.cos(math.radians(deg)); sn = math.sin(math.radians(deg)); out = []
        for v in s.V:
            x, y, z = v[0]-p[0], v[1]-p[1], v[2]-p[2]
            if ax == 'x': y, z = y*c - z*sn, y*sn + z*c
            elif ax == 'y': x, z = x*c + z*sn, -x*sn + z*c
            else: x, y = x*c - y*sn, x*sn + y*c
            out.append((x+p[0], y+p[1], z+p[2]))
        s.V = out; return s
    def bend(s, fn):
        s.V = [fn(v) for v in s.V]; return s
    def __add__(s, o):
        n = len(s.V)
        return Part(s.V + o.V, s.F + [(a+n, b+n, c+n) for a, b, c in o.F])

def merge(parts):
    r = Part()
    for p in parts: r = r + p
    return r

# ---------------------------------------------------------------- core builders
def loft(rings, cap0=True, cap1=True):
    n = len(rings[0])
    d = sub(centroid(rings[-1]), centroid(rings[0]))
    if dot(newell(rings[0]), d) < 0: rings = [r[::-1] for r in rings]
    V = []; F = []
    for r in rings: V += list(r)
    def quad(a, b, c, d_):
        ids = [a, b, c, d_]; q = []
        for i in ids:
            if not q or sum(abs(V[i][k]-V[q[-1]][k]) for k in range(3)) > 1e-9: q.append(i)
        if len(q) > 1 and sum(abs(V[q[0]][k]-V[q[-1]][k]) for k in range(3)) < 1e-9: q.pop()
        if len(q) == 4: F.extend([(q[0], q[1], q[2]), (q[0], q[2], q[3])])
        elif len(q) == 3: F.append(tuple(q))
    for k in range(len(rings)-1):
        for i in range(n):
            j = (i+1) % n
            quad(k*n+i, k*n+j, (k+1)*n+j, (k+1)*n+i)
    if cap0: F += triangulate(V, list(range(n))[::-1])
    if cap1: F += triangulate(V, [(len(rings)-1)*n+i for i in range(n)])
    vol = sum(dot(V[a], cross(V[b], V[c])) for a, b, c in F)/6.0
    if vol < 0: F = [(a, c, b) for a, b, c in F]       # guarantee outward winding
    return Part(V, F)

def rect(x0, x1, z0, z1, y): return [(x0, y, z0), (x1, y, z0), (x1, y, z1), (x0, y, z1)]
def circ(r, y, seg=8, cx=0, cz=0, ph=0):
    return [(cx+r*math.cos(ph+2*math.pi*i/seg), y, cz+r*math.sin(ph+2*math.pi*i/seg)) for i in range(seg)]

def box(x0, y0, z0, x1, y1, z1, b=0.0):
    if b <= 0: return loft([rect(x0, x1, z0, z1, y0), rect(x0, x1, z0, z1, y1)])
    b = min(b, (x1-x0)/2.05, (y1-y0)/2.05, (z1-z0)/2.05)
    return loft([rect(x0+b, x1-b, z0+b, z1-b, y0), rect(x0, x1, z0, z1, y0+b),
                 rect(x0, x1, z0, z1, y1-b), rect(x0+b, x1-b, z0+b, z1-b, y1)])

def tbox(x0, y0, z0, x1, y1, z1, top=0.7, b=0.0):
    """Tapered box: top face scaled about its centre (0<top)."""
    cx, cz = (x0+x1)/2, (z0+z1)/2; hx, hz = (x1-x0)/2*top, (z1-z0)/2*top
    return loft([rect(x0, x1, z0, z1, y0), rect(cx-hx, cx+hx, cz-hz, cz+hz, y1)])

def lathe(profile, seg=8, cx=0, cz=0, ph=0):
    return loft([circ(r, y, seg, cx, cz, ph) for r, y in profile])

def cyl(r, h, seg=8, y0=0, cx=0, cz=0, r1=None, ph=0):
    r1 = r if r1 is None else r1
    return loft([circ(r, y0, seg, cx, cz, ph), circ(r1, y0+h, seg, cx, cz, ph)])

def cylb(r, h, seg=10, y0=0, cx=0, cz=0, b=0.03):
    """Chamfered cylinder."""
    b = min(b, r*0.4, h*0.4)
    return lathe([(r-b, y0), (r, y0+b), (r, y0+h-b), (r-b, y0+h)], seg, cx, cz)

def ext(poly, y0, y1, top=None):
    """Extrude xz polygon [(x,z)] from y0 to y1 (optionally to another polygon `top`)."""
    t = top or poly
    return loft([[(x, y0, z) for x, z in poly], [(x, y1, z) for x, z in t]])

def frame(p0, p1):
    d = norm(sub(p1, p0)); up = (0, 1, 0) if abs(d[1]) < 0.98 else (1, 0, 0)
    u = norm(cross(up, d)); v = cross(d, u); return d, u, v

def prof_beam(p0, p1, poly2, p0s=1.0, p1s=1.0):
    d, u, v = frame(p0, p1)
    def ring(p, k): return [add(p, add(mul(u, a*k), mul(v, b*k))) for a, b in poly2]
    return loft([ring(p0, p0s), ring(p1, p1s)])

def beam(p0, p1, w, h, p1s=1.0):
    return prof_beam(p0, p1, [(-w/2, -h/2), (w/2, -h/2), (w/2, h/2), (-w/2, h/2)], 1.0, p1s)

def tube(p0, p1, r, seg=6, r1=None):
    k = 1.0 if r1 is None else r1/r
    pl = [(r*math.cos(2*math.pi*i/seg), r*math.sin(2*math.pi*i/seg)) for i in range(seg)]
    return prof_beam(p0, p1, pl, 1.0, k)

def ibeam_poly(w, h, tf, tw):
    hw, hh = w/2, h/2
    return [(-hw, -hh), (hw, -hh), (hw, -hh+tf), (tw/2, -hh+tf), (tw/2, hh-tf), (hw, hh-tf), (hw, hh), (-hw, hh),
            (-hw, hh-tf), (-tw/2, hh-tf), (-tw/2, -hh+tf), (-hw, -hh+tf)]

def profile_ext(profile, z0, z1):
    """Extrude an (x,y) profile along z."""
    return loft([[(x, y, z0) for x, y in profile], [(x, y, z1) for x, y in profile]])

def arc_pts(cx, cz, r, a0, a1, n):
    return [(cx+r*math.cos(math.radians(a0+(a1-a0)*i/n)), cz+r*math.sin(math.radians(a0+(a1-a0)*i/n))) for i in range(n+1)]

def band(r0, r1, y0, y1, a0=0, a1=360, n=24, cx=0, cz=0, rt0=None, rt1=None, y_off=0):
    """Arc band (annular sector) extrusion. rt0/rt1 = radii at top (for chamfers)."""
    o = arc_pts(cx, cz, r1, a0, a1, n); i_ = arc_pts(cx, cz, r0, a1, a0, n)
    poly = o + i_
    ot = arc_pts(cx, cz, rt1 if rt1 else r1, a0, a1, n); it = arc_pts(cx, cz, rt0 if rt0 else r0, a1, a0, n)
    return ext(poly, y0, y1, ot + it)

def jag(cx, cz, rx, rz, n=9, j=0.35, seed=1, a0=0, a1=360):
    """Star-shaped jagged polygon (simple polygon guaranteed)."""
    rnd = random.Random(seed); pts = []
    for i in range(n):
        a = math.radians(a0 + (a1-a0)*(i + rnd.uniform(-0.25, 0.25))/n)
        k = 1 - j*rnd.random()
        pts.append((cx+rx*k*math.cos(a), cz+rz*k*math.sin(a)))
    return pts

def sweep(profile, pts, close_start=True):
    """Sweep (lateral, up) profile along a polyline of 3D points."""
    rings = []
    for i, p in enumerate(pts):
        a = pts[max(i-1, 0)]; b = pts[min(i+1, len(pts)-1)]
        t = norm(sub(b, a)); L = norm((t[2], 0, -t[0]))
        rings.append([(p[0]+L[0]*x, p[1]+y, p[2]+L[2]*x) for x, y in profile])
    return loft(rings)

class Path:
    def __init__(s, f, L, straight=False): s.f = f; s.L = L; s.straight = straight
    def pts(s, a=0, b=None, step=1.5):
        b = s.L if b is None else b
        n = 1 if s.straight else max(1, int(math.ceil((b-a)/step)))
        return [s.f(a+(b-a)*i/n) for i in range(n+1)]

def line_path(a, b):
    L = math.dist(a, b)
    return Path(lambda s: (a[0]+(b[0]-a[0])*s/L, a[1]+(b[1]-a[1])*s/L, a[2]+(b[2]-a[2])*s/L), L, True)

def arc_path(cx, cz, r, a0, a1, y0=0, y1=0):
    L = abs(math.radians(a1-a0))*r
    def f(s):
        t = s/L; a = math.radians(a0+(a1-a0)*t)
        return (cx+r*math.cos(a), y0+(y1-y0)*t, cz+r*math.sin(a))
    return Path(f, L)

# ---------------------------------------------------------------- materials
def _m(kd, ks=0.05, ns=12, d=1.0, ke=None): return dict(kd=kd, ks=ks, ns=ns, d=d, ke=ke)
MATS = {
 'asphalt_warm': _m((0.30, 0.285, 0.275)), 'asphalt_cool': _m((0.225, 0.255, 0.30)),
 'concrete_pale': _m((0.76, 0.755, 0.73)), 'concrete_weathered': _m((0.55, 0.55, 0.53)),
 'metal_painted_grey': _m((0.42, 0.47, 0.52), 0.3, 40), 'galvanized_steel': _m((0.68, 0.72, 0.75), 0.6, 80),
 'brushed_metal': _m((0.6, 0.62, 0.65), 0.5, 60), 'safety_yellow': _m((0.98, 0.80, 0.08), 0.2, 30),
 'safety_orange': _m((0.97, 0.43, 0.08), 0.2, 30), 'traffic_red': _m((0.80, 0.10, 0.10), 0.2, 30),
 'wood_weathered': _m((0.46, 0.37, 0.28)), 'timber_warm': _m((0.72, 0.50, 0.28)),
 'rubber_dark': _m((0.07, 0.07, 0.08), 0.02, 4), 'glass_tinted': _m((0.30, 0.52, 0.62), 0.8, 90, 0.45),
 'water_blue': _m((0.12, 0.42, 0.68), 0.7, 90, 0.85), 'rust_metal': _m((0.55, 0.28, 0.15), 0.1, 10),
 'coastal_weathered': _m((0.50, 0.60, 0.58)), 'dusty_stone': _m((0.60, 0.55, 0.48)),
 'broken_concrete': _m((0.63, 0.61, 0.57)), 'marking_white': _m((0.95, 0.95, 0.93)),
 'marking_yellow': _m((0.98, 0.80, 0.15)), 'brick_red': _m((0.62, 0.28, 0.20)),
 'mortar': _m((0.76, 0.73, 0.66)), 'soil': _m((0.30, 0.20, 0.12)), 'foliage_green': _m((0.30, 0.60, 0.25)),
 'signal_red': _m((1.0, 0.15, 0.12), 0, 1, 1, (0.9, 0.1, 0.08)), 'signal_amber': _m((1.0, 0.7, 0.1), 0, 1, 1, (0.9, 0.6, 0.05)),
 'signal_green': _m((0.1, 0.9, 0.35), 0, 1, 1, (0.05, 0.8, 0.3)), 'lamp_emissive': _m((1.0, 0.95, 0.72), 0, 1, 1, (1.0, 0.92, 0.6)),
 'ad_panel': _m((0.88, 0.91, 0.95), 0.1), 'sign_green': _m((0.04, 0.42, 0.24), 0.1), 'sign_blue': _m((0.08, 0.30, 0.65), 0.1),
 'sign_white': _m((0.93, 0.94, 0.95), 0.1), 'container_blue': _m((0.12, 0.33, 0.62), 0.2, 30),
 'container_red': _m((0.70, 0.16, 0.12), 0.2, 30), 'container_green': _m((0.14, 0.45, 0.30), 0.2, 30),
 'container_orange': _m((0.88, 0.44, 0.12), 0.2, 30), 'concrete_core': _m((0.46, 0.44, 0.41)),
 'rebar': _m((0.40, 0.25, 0.18), 0.2, 20), 'cable_black': _m((0.05, 0.05, 0.06), 0.02, 4),
 'white_paint': _m((0.90, 0.91, 0.90), 0.2, 30), 'insulator_ceramic': _m((0.62, 0.47, 0.32), 0.5, 70),
 'insulator_grey': _m((0.72, 0.74, 0.76), 0.5, 70), 'paint_green': _m((0.20, 0.38, 0.28), 0.2, 30),
 'paint_blue': _m((0.16, 0.34, 0.58), 0.2, 30), 'tactile_yellow': _m((0.95, 0.76, 0.12)), 'paint_navy': _m((0.10, 0.17, 0.30), 0.2, 30),
 'roof_tile': _m((0.58, 0.24, 0.18)), 'plaster_cream': _m((0.84, 0.80, 0.70)),
 'grass_muted': _m((0.40, 0.56, 0.32)), 'ground_tan': _m((0.70, 0.65, 0.55)), 'sea_deep': _m((0.10, 0.36, 0.60), 0.6, 80),
}

# ---------------------------------------------------------------- model
class Model:
    def __init__(s, name, cat, desc=''):
        s.name = name; s.cat = cat; s.desc = desc
        s.groups = OrderedDict(); s.conn = []; s.detach = {}; s.notes = []
    def add(s, group, mat, part):
        assert mat in MATS, mat
        k = (group, mat)
        s.groups[k] = (s.groups[k] + part) if k in s.groups else part
        return s
    def box(s, g, m, *a, **k): return s.add(g, m, box(*a, **k))
    def cyl(s, g, m, *a, **k): return s.add(g, m, cyl(*a, **k))
    def tube(s, g, m, *a, **k): return s.add(g, m, tube(*a, **k))
    def beam(s, g, m, *a, **k): return s.add(g, m, beam(*a, **k))
    def ext(s, g, m, *a, **k): return s.add(g, m, ext(*a, **k))
    def sweep(s, g, m, prof, pts): return s.add(g, m, sweep(prof, pts))
    def cn(s, name, pos, direction, **info):
        s.conn.append(dict(name=name, position=[round(c, 3) for c in pos], direction=list(direction), **info))
    def det(s, group, desc, pivot=None):
        s.detach[group] = dict(description=desc, pivot=pivot)
    def all_parts(s):
        return [(g, m, p) for (g, m), p in s.groups.items()]
    def bbox(s):
        vs = [v for p in s.groups.values() for v in p.V]
        return (tuple(min(v[i] for v in vs) for i in range(3)), tuple(max(v[i] for v in vs) for i in range(3)))
    def tri_count(s):
        n = 0
        for p in s.groups.values():
            for a, b, c in p.F:
                if dot(cross(sub(p.V[b], p.V[a]), sub(p.V[c], p.V[a])), (1, 1, 1)) != 0 or True: n += 1
        return n
    def instance(s, ox=0, oy=0, oz=0, ry=0, tag=''):
        """Return list of (group, mat, Part) transformed for scene assembly."""
        out = []
        for (g, m), p in s.groups.items():
            q = p.copy()
            if ry: q.rot('y', ry)
            q.move(ox, oy, oz); out.append((f"{s.name}{tag}_{g}", m, q))
        return out

    def write(s, folder):
        os.makedirs(folder, exist_ok=True)
        used = []
        L = [f"# WORLDLINE LAB ASSET PACK 02 - {s.name}", f"# {s.desc}",
             "# Units: metres | Up axis: +Y | Forward: +Z | Flat-shaded, per-face normals",
             f"mtllib {s.name}.mtl", f"o {s.name}"]
        vo = 1; nmap = {}; nlist = []
        for (g, m), p in s.groups.items():
            if m not in used: used.append(m)
            fl = []
            for a, b, c in p.F:
                n = cross(sub(p.V[b], p.V[a]), sub(p.V[c], p.V[a]))
                if dot(n, n) < 1e-14: continue
                fl.append(((a, b, c), norm(n)))
            if not fl: continue
            L.append(f"g {s.name}__{g}"); L.append(f"usemtl {m}")
            L += [f"v {x:.5f} {y:.5f} {z:.5f}" for x, y, z in p.V]
            fs = []
            for (a, b, c), n in fl:
                k = (round(n[0], 4), round(n[1], 4), round(n[2], 4))
                if k not in nmap: nmap[k] = len(nmap)+1; L.append(f"vn {k[0]:.4f} {k[1]:.4f} {k[2]:.4f}")
                ni = nmap[k]
                fs.append(f"f {a+vo}//{ni} {b+vo}//{ni} {c+vo}//{ni}")
            L += fs; vo += len(p.V)
        open(os.path.join(folder, f"{s.name}.obj"), 'w').write("\n".join(L)+"\n")
        write_mtl(os.path.join(folder, f"{s.name}.mtl"), used)

def write_mtl(path, used):
    L = ["# WORLDLINE LAB ASSET PACK 02 shared material library (subset)"]
    for m in used:
        d = MATS[m]; kd = d['kd']
        L += [f"newmtl {m}", f"Ka {kd[0]*0.35:.3f} {kd[1]*0.35:.3f} {kd[2]*0.35:.3f}", f"Kd {kd[0]:.3f} {kd[1]:.3f} {kd[2]:.3f}",
              f"Ks {d['ks']:.3f} {d['ks']:.3f} {d['ks']:.3f}", f"Ns {d['ns']}", f"d {d['d']}", "illum 2"]
        if d['ke']: L.append(f"Ke {d['ke'][0]:.3f} {d['ke'][1]:.3f} {d['ke'][2]:.3f}")
        L.append("")
    open(path, 'w').write("\n".join(L))
