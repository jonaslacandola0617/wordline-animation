import math, os
import numpy as np
from PIL import Image, ImageDraw, ImageFilter

def load_mtl(path):
    mats = {}; cur = None
    if not os.path.exists(path): return mats
    for ln in open(path):
        t = ln.split()
        if not t: continue
        if t[0] == 'newmtl': cur = t[1]; mats[cur] = dict(kd=(0.7, 0.7, 0.7), d=1.0, ke=None)
        elif cur and t[0] == 'Kd': mats[cur]['kd'] = tuple(map(float, t[1:4]))
        elif cur and t[0] == 'd': mats[cur]['d'] = float(t[1])
        elif cur and t[0] == 'Ke': mats[cur]['ke'] = tuple(map(float, t[1:4]))
    return mats

def load_obj(path):
    """Independent OBJ parser -> (verts Nx3, tris Mx3 idx, colors Mx3, flags)."""
    V = []; N = []; T = []; C = []; EM = []; GL = []; mats = {}; cur = None
    base = os.path.dirname(path)
    for ln in open(path):
        t = ln.split()
        if not t: continue
        if t[0] == 'v': V.append(tuple(map(float, t[1:4])))
        elif t[0] == 'vn': N.append(tuple(map(float, t[1:4])))
        elif t[0] == 'mtllib': mats.update(load_mtl(os.path.join(base, t[1])))
        elif t[0] == 'usemtl': cur = t[1]
        elif t[0] == 'f':
            ids = [int(x.split('/')[0])-1 for x in t[1:]]
            m = mats.get(cur, dict(kd=(0.7, 0.7, 0.7), d=1.0, ke=None))
            for k in range(1, len(ids)-1):
                T.append((ids[0], ids[k], ids[k+1])); C.append(m['kd']); EM.append(1 if m['ke'] else 0); GL.append(1 if m['d'] < 0.6 else 0)
    return np.array(V), np.array(T), np.array(C), np.array(EM), np.array(GL)

def look(eye, tgt, up=(0, 1, 0)):
    f = np.array(tgt)-np.array(eye); f /= np.linalg.norm(f)
    r = np.cross(f, up); r /= np.linalg.norm(r); u = np.cross(r, f)
    return np.array(eye, float), f, r, u

def render(V, T, C, EM, GL, eye, tgt, size=(960, 720), fov=38, ss=2, bg_top=(196, 220, 240), bg_bot=(236, 240, 244),
           ground=True, shadow_y=None, ground_r=None, ground_col=(176, 184, 176), water=None, light=(-0.45, 0.8, 0.4), amb=0.42):
    W, Hh = size[0]*ss, size[1]*ss
    img = Image.new('RGB', (W, Hh)); d = ImageDraw.Draw(img)
    for y in range(Hh):
        k = y/Hh; d.line([(0, y), (W, y)], fill=tuple(int(bg_top[i]*(1-k)+bg_bot[i]*k) for i in range(3)))
    e, f, r, u = look(eye, tgt)
    foc = 0.5*Hh/math.tan(math.radians(fov)/2)
    def proj(P):
        Q = P-e; x = Q@r; y = Q@u; z = Q@f
        z = np.maximum(z, 1e-3)
        return np.stack([W/2 + foc*x/z, Hh/2 - foc*y/z], 1), z
    L = np.array(light, float); L /= np.linalg.norm(L)
    lo = V.min(0); hi = V.max(0); cen = (lo+hi)/2; rad = float(np.linalg.norm(hi-lo))/2
    # ground / water plane
    gr = ground_r or rad*1.8
    if ground:
        gy = lo[1]-0.002 if water is None else water
        g = np.array([[cen[0]-gr, gy, cen[2]-gr], [cen[0]+gr, gy, cen[2]-gr], [cen[0]+gr, gy, cen[2]+gr], [cen[0]-gr, gy, cen[2]+gr]])
        p2, z = proj(g)
        d.polygon([tuple(p) for p in p2], fill=ground_col)
    # fake shadows from ground plane
    if ground or shadow_y is not None:
        gy = lo[1] if shadow_y is None else shadow_y
        A = V[T[:, 0]]; B = V[T[:, 1]]; Cc = V[T[:, 2]]
        sm = Image.new('L', (W, Hh), 0); sd = ImageDraw.Draw(sm)
        def shadow(P):
            t = (P[:, 1]-gy)/L[1]
            return P - L*t[:, None]
        sa, sb, sc = shadow(A), shadow(B), shadow(Cc)
        pa, za_ = proj(sa); pb, zb_ = proj(sb); pc, zc_ = proj(sc)
        okz = (za_ > 0.5) & (zb_ > 0.5) & (zc_ > 0.5)
        step = max(1, len(T)//60000)
        for i in range(0, len(T), step):
            if not okz[i]: continue
            sd.polygon([tuple(pa[i]), tuple(pb[i]), tuple(pc[i])], fill=255)
        sm = sm.filter(ImageFilter.GaussianBlur(2.5*ss))
        dark = Image.new('RGB', (W, Hh), (40, 50, 60)); img = Image.composite(dark, img, sm.point(lambda v: int(v*0.32))); d = ImageDraw.Draw(img)
    # triangles
    A = V[T[:, 0]]; B = V[T[:, 1]]; Cc = V[T[:, 2]]
    Nn = np.cross(B-A, Cc-A); ln = np.linalg.norm(Nn, axis=1); ok = ln > 1e-12
    Nn[ok] /= ln[ok, None]
    cen_t = (A+B+Cc)/3; vd = e-cen_t
    facing = (Nn*vd).sum(1) > 0
    dif = np.clip(Nn@L, 0, 1); hemi = 0.5+0.5*Nn[:, 1]
    sh = amb*(0.75+0.25*hemi) + 0.62*dif
    rim = np.clip(Nn@np.array([0.6, 0.2, -0.7]), 0, 1)*0.08
    col = np.clip(C*(sh+rim)[:, None]*1.02, 0, 1)
    col = np.where(EM[:, None] == 1, np.clip(C*1.1, 0, 1), col)
    col = np.where(GL[:, None] == 1, col*0.6+np.array([0.35, 0.5, 0.58])*0.4, col)
    R = np.stack([r, u, f], 1); near = 0.15
    Qa = (A-e)@R; Qb = (B-e)@R; Qc = (Cc-e)@R
    bad = np.minimum(np.minimum(Qa[:, 2], Qb[:, 2]), Qc[:, 2]) < near
    good = np.where(~bad)[0]; ex = []
    for i in np.where(bad)[0]:
        poly = [Qa[i], Qb[i], Qc[i]]; out = []
        for k in range(3):
            a = poly[k]; b = poly[(k+1) % 3]; ina = a[2] >= near; inb = b[2] >= near
            if ina: out.append(a)
            if ina != inb: out.append(a+(b-a)*((near-a[2])/(b[2]-a[2])))
        for k in range(1, len(out)-1): ex.append((out[0], out[k], out[k+1], i))
    if ex:
        Qa = np.concatenate([Qa[good], np.array([x[0] for x in ex])]); Qb = np.concatenate([Qb[good], np.array([x[1] for x in ex])])
        Qc = np.concatenate([Qc[good], np.array([x[2] for x in ex])]); CI = np.concatenate([good, np.array([x[3] for x in ex])])
    else:
        Qa, Qb, Qc, CI = Qa[good], Qb[good], Qc[good], good
    def sp(Q): return np.stack([W/2+foc*Q[:, 0]/Q[:, 2], Hh/2-foc*Q[:, 1]/Q[:, 2]], 1)
    P1, P2, P3 = sp(Qa), sp(Qb), sp(Qc); z1, z2, z3 = Qa[:, 2], Qb[:, 2], Qc[:, 2]
    col8 = (col*255).astype(np.uint8)[CI]; GLc = GL[CI]; facing_c = facing[CI]
    fb = np.array(img); zb = np.full((Hh, W), np.inf, np.float32)
    zc = (z1+z2+z3)/3
    def tri_pass(ids, blend=None):
        for i in ids:
            a, b, c = P1[i], P2[i], P3[i]
            xmin = max(int(math.floor(min(a[0], b[0], c[0]))), 0); xmax = min(int(math.ceil(max(a[0], b[0], c[0]))), W-1)
            ymin = max(int(math.floor(min(a[1], b[1], c[1]))), 0); ymax = min(int(math.ceil(max(a[1], b[1], c[1]))), Hh-1)
            if xmax < xmin or ymax < ymin: continue
            den = (b[1]-c[1])*(a[0]-c[0])+(c[0]-b[0])*(a[1]-c[1])
            if abs(den) < 1e-9: continue
            xs = np.arange(xmin, xmax+1)+0.5; ys = (np.arange(ymin, ymax+1)+0.5)[:, None]
            l1 = ((b[1]-c[1])*(xs-c[0])+(c[0]-b[0])*(ys-c[1]))/den
            l2 = ((c[1]-a[1])*(xs-c[0])+(a[0]-c[0])*(ys-c[1]))/den
            l3 = 1-l1-l2
            m = (l1 >= -1e-4) & (l2 >= -1e-4) & (l3 >= -1e-4)
            if not m.any(): continue
            z = 1.0/(l1/z1[i]+l2/z2[i]+l3/z3[i])
            sub_z = zb[ymin:ymax+1, xmin:xmax+1]
            m &= z < sub_z-1e-4*(1+0*z)
            if not m.any(): continue
            if blend is None:
                sub_z[m] = z[m]; fb[ymin:ymax+1, xmin:xmax+1][m] = col8[i]
            else:
                reg = fb[ymin:ymax+1, xmin:xmax+1]
                reg[m] = (reg[m]*0.55+col8[i]*0.45).astype(np.uint8)
    opaque = np.where(facing_c & (GLc == 0))[0]
    tri_pass(opaque)
    glass = np.where(GLc == 1)[0]
    tri_pass(glass[np.argsort(-zc[glass])], blend=True)
    img = Image.fromarray(fb)
    return img.resize(size, Image.LANCZOS)

def auto_cam(V, yaw=38, pitch=26, dist=2.6, fov=38):
    lo = V.min(0); hi = V.max(0); cen = (lo+hi)/2; rad = float(np.linalg.norm(hi-lo))/2
    dd = rad*dist*(38/fov)
    y = math.radians(yaw); p = math.radians(pitch)
    eye = cen + dd*np.array([math.sin(y)*math.cos(p), math.sin(p), math.cos(y)*math.cos(p)])
    return eye, cen
