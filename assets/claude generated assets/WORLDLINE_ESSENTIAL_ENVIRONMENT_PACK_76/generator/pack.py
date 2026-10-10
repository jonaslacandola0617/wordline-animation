import json, os, sys, math, time, shutil, collections
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from lib import *
import roads, props, utilities, harbor, destroy
from render import load_obj, render, auto_cam, load_mtl

ROOT = '/home/claude/WORLDLINE_ESSENTIAL_ENVIRONMENT_PACK_76'
CATS = [('roads', roads.ROADS), ('street_props', props.PROPS), ('utilities', utilities.UTILITIES), ('harbor', harbor.HARBOR), ('destruction', destroy.DESTROY)]
BUDGET = {'roads': (200, 4000), 'street_props': (150, 2500), 'utilities': (500, 4000), 'harbor': (1000, 10000), 'destruction': (400, 5000)}

def build_models():
    models = collections.OrderedDict()
    for cat, lst in CATS:
        for fn in lst:
            M = fn(); models[M.name] = M
    return models

def export(models):
    if os.path.exists(ROOT): shutil.rmtree(ROOT)
    for cat, lst in CATS:
        os.makedirs(f'{ROOT}/{cat}', exist_ok=True); os.makedirs(f'{ROOT}/previews/{cat}', exist_ok=True)
    os.makedirs(f'{ROOT}/metadata', exist_ok=True)
    for name, M in models.items(): M.write(f'{ROOT}/{M.cat}')

# ------------------------------------------------------------- independent validation
def validate_obj(path):
    rep = dict(file=os.path.basename(path), errors=[], warnings=[])
    V = []; N = []; F = []; groups = collections.OrderedDict(); cur = None; cur_m = None; mtl = None; usem = set()
    for ln in open(path):
        t = ln.split()
        if not t or t[0] == '#': continue
        if t[0] == 'v': V.append(tuple(map(float, t[1:4])))
        elif t[0] == 'vn': N.append(tuple(map(float, t[1:4])))
        elif t[0] == 'mtllib': mtl = t[1]
        elif t[0] == 'g': cur = t[1]; groups.setdefault(cur, [])
        elif t[0] == 'usemtl': cur_m = t[1]; usem.add(cur_m)
        elif t[0] == 'f':
            if len(t) != 4: rep['errors'].append('non-triangle face')
            ids = []
            for x in t[1:]:
                a = x.split('/'); vi = int(a[0]); ni = int(a[2]) if len(a) > 2 and a[2] else None
                ids.append((vi, ni))
            groups[cur].append(ids)
    rep['vertices'] = len(V); rep['normals'] = len(N); rep['triangles'] = sum(len(g) for g in groups.values()); rep['groups'] = len(groups)
    if not V or not rep['triangles']: rep['errors'].append('empty geometry')
    arr = np.array(V) if V else np.zeros((0, 3))
    if not np.isfinite(arr).all(): rep['errors'].append('non-finite vertex')
    bad_idx = 0; degenerate = 0; nmis = 0; edges = collections.Counter(); 
    def key(i): v = V[i-1]; return (round(v[0], 4), round(v[1], 4), round(v[2], 4))
    for g, fl in groups.items():
        for f in fl:
            for vi, ni in f:
                if not (1 <= vi <= len(V)): bad_idx += 1
                if ni is None or not (1 <= ni <= len(N)): bad_idx += 1
            if bad_idx: continue
            a, b, c = (np.array(V[f[k][0]-1]) for k in range(3))
            n = np.cross(b-a, c-a); ln_ = np.linalg.norm(n)
            if ln_ < 1e-10: degenerate += 1; continue
            if np.dot(n/ln_, np.array(N[f[0][1]-1])) < 0.99: nmis += 1
            ks = [key(f[k][0]) for k in range(3)]
            for k in range(3):
                e = tuple(sorted((ks[k], ks[(k+1) % 3]))); edges[(g, e)] += 1
    rep['bad_indices'] = bad_idx; rep['degenerate_tris'] = degenerate; rep['normal_mismatch'] = nmis
    if bad_idx: rep['errors'].append(f'{bad_idx} bad indices')
    if nmis: rep['errors'].append(f'{nmis} faces disagree with their vn')
    if N and abs(np.linalg.norm(np.array(N), axis=1) - 1).max() > 0.01: rep['errors'].append('non-unit normals')
    tot = len(edges); two = sum(1 for c in edges.values() if c == 2)
    rep['watertight_edge_pct'] = round(100*two/max(tot, 1), 1)
    # mtl resolution
    base = os.path.dirname(path)
    if not mtl or not os.path.exists(os.path.join(base, mtl)): rep['errors'].append('mtl missing')
    else:
        defined = set(load_mtl(os.path.join(base, mtl)).keys())
        miss = usem - defined
        if miss: rep['errors'].append(f'undefined materials {sorted(miss)}')
        rep['materials'] = sorted(usem)
    if len(arr):
        lo = arr.min(0); hi = arr.max(0); rep['bbox_min'] = [round(float(x), 3) for x in lo]; rep['bbox_max'] = [round(float(x), 3) for x in hi]
        rep['dimensions'] = [round(float(x), 3) for x in hi-lo]
        if (hi-lo).max() > 120: rep['warnings'].append('very large extents')
    rep['group_names'] = [g.split('__', 1)[1] if '__' in g else g for g in groups]
    return rep

def catalog(models, reps):
    cat = collections.OrderedDict()
    for name, M in models.items():
        r = reps[name]
        groups = collections.OrderedDict()
        for (g, m), p in M.groups.items(): groups.setdefault(g, []).append(m)
        cat[name] = dict(name=name, category=M.cat, description=M.desc, obj=f'{M.cat}/{name}.obj', mtl=f'{M.cat}/{name}.mtl', preview=f'previews/{M.cat}/{name}.png',
                         triangles=r['triangles'], vertices=r['vertices'], dimensions_m=r['dimensions'], bounding_box_m=dict(min=r['bbox_min'], max=r['bbox_max']),
                         pivot_origin='model origin (0,0,0) - see description/connection points; Y-up, +Z forward', materials=r['materials'],
                         groups={g: sorted(set(ms)) for g, ms in groups.items()}, connection_points=M.conn, notes=M.notes,
                         suggested_triangle_range=list(BUDGET[M.cat]), watertight_edge_pct=r['watertight_edge_pct'])
    return cat

def damage_parts(models):
    out = {}
    for name, M in models.items():
        entries = []
        gn = list(dict.fromkeys(g for (g, m) in M.groups))
        for key, d in M.detach.items():
            members = [g for g in gn if g == key or g.startswith(key+'_')] or ([key] if key in gn else [])
            if not members: continue
            vs = [v for (g, m), p in M.groups.items() if g in members for v in p.V]
            lo = [min(v[i] for v in vs) for i in range(3)]; hi = [max(v[i] for v in vs) for i in range(3)]
            piv = d['pivot'] or [round((lo[0]+hi[0])/2, 3), round(lo[1], 3), round((lo[2]+hi[2])/2, 3)]
            entries.append(dict(part=key, obj_groups=[f'{name}__{g}' for g in members], description=d['description'], pivot_m=list(piv), pivot_source='authored' if d['pivot'] else 'bbox base-centre',
                                bbox_min=[round(x, 3) for x in lo], bbox_max=[round(x, 3) for x in hi]))
        if entries or M.cat == 'destruction':
            out[name] = dict(category=M.cat, all_obj_groups=[f'{name}__{g}' for g in gn], detachable_parts=entries)
    return out

CONN_SPEC = dict(
    grid='Road modules use a 12 m nominal module along local Z (ends at z=-6 and z=+6, centreline x=0). Larger modules are multiples (roundabout 24 m).',
    lane_width_m=3.4, curb_height_m=0.15, curb_width_m=0.25, slab_depth_m=0.4,
    traffic='Right-hand traffic: lanes at x<0 travel +Z, lanes at x>0 travel -Z (arrows follow this).',
    junction_arms='Junctions (ROAD_04/05): arm directions N=+Z, E=+X, S=-Z, W=-X; connection plane at 6 m from centre. ROAD_04 has its closed side to the North.',
    sidewalk='Sidewalk (ROAD_12) 3 m wide, top y=+0.15; road-side edge at x=-1.5 local; place its centreline at carriageway half-width + 0.25 + 1.5 m. Corner module ROAD_13 origin = junction centre.',
    modules={})

def write_json(models, reps):
    cat = catalog(models, reps)
    json.dump(dict(pack='WORLDLINE_ESSENTIAL_ENVIRONMENT_PACK_76', units='metres', up_axis='Y', forward_axis='+Z', handedness='right', assets=cat), open(f'{ROOT}/metadata/ASSET_CATALOG.json', 'w'), indent=1)
    cp = dict(CONN_SPEC); cp['modules'] = {n: dict(description=M.desc, connection_points=M.conn) for n, M in models.items() if M.conn}
    json.dump(cp, open(f'{ROOT}/metadata/CONNECTION_POINTS.json', 'w'), indent=1)
    json.dump(damage_parts(models), open(f'{ROOT}/metadata/DAMAGE_PARTS.json', 'w'), indent=1)
    return cat

# ------------------------------------------------------------- previews
def label(img, text):
    d = ImageDraw.Draw(img); d.rectangle([0, 0, img.width, 26], fill=(24, 30, 40))
    d.text((8, 7), text, fill=(235, 240, 245))
    return img

def previews(models):
    thumbs = {}
    for name, M in models.items():
        V, T, C, EM, GL = load_obj(f'{ROOT}/{M.cat}/{name}.obj')
        if M.cat == 'roads': yaw, pitch, dist = 32, 50, 2.3
        elif M.cat == 'destruction': yaw, pitch, dist = 35, 30, 2.5
        else: yaw, pitch, dist = 38, 24, 2.5
        if name in ('UTILITY_04', 'HARBOR_14', 'HARBOR_06', 'UTILITY_10', 'PROP_14'): dist = 2.4
        ext_ = V.max(0)-V.min(0)
        if ext_[1] > 1.8*max(ext_[0], ext_[2]): dist *= 1.45
        eye, cen = auto_cam(V, yaw, pitch, dist)
        im = render(V, T, C, EM, GL, eye, cen, (960, 720), ss=2)
        im.save(f'{ROOT}/previews/{M.cat}/{name}.png'); thumbs[name] = im
    return thumbs

def contact_sheet(models, thumbs):
    cols = 10; tw, th = 360, 270; names = list(models)
    rows = (len(names)+cols-1)//cols
    sheet = Image.new('RGB', (cols*tw, rows*th+60), (20, 24, 30)); d = ImageDraw.Draw(sheet)
    d.text((12, 20), 'WORLDLINE LAB - ASSET PACK 02 - 76 models (software-rendered previews, flat shaded)', fill=(240, 240, 240))
    for i, n in enumerate(names):
        im = thumbs[n].resize((tw, th), Image.LANCZOS); label(im, f'{n}  {models[n].tri_count()} tris')
        sheet.paste(im, ((i % cols)*tw, 60+(i//cols)*th))
    sheet.save(f'{ROOT}/previews/contact_sheet.png')
    return sheet

if __name__ == '__main__':
    t0 = time.time()
    models = build_models(); print('built', len(models), 'models', round(time.time()-t0, 1), 's')
    export(models)
    reps = {n: validate_obj(f'{ROOT}/{M.cat}/{n}.obj') for n, M in models.items()}
    errs = {n: r['errors'] for n, r in reps.items() if r['errors']}
    print('validation errors:', errs or 'none')
    cat = write_json(models, reps)
    json.dump(reps, open('/tmp/validation_raw.json', 'w'))
    if '--nopreview' not in sys.argv:
        th = previews(models); contact_sheet(models, th); print('previews done', round(time.time()-t0, 1), 's')
