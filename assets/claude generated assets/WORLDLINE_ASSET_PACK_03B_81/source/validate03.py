"""Independent validation of an Asset Pack 03B folder: parses the written OBJ/MTL files (not Blender state)."""
import json, os, re, sys, math, hashlib, collections

root = sys.argv[1]
cat = json.load(open(os.path.join(root, "ASSET_CATALOG.json")))
EXPECT = {"animals": 8, "disaster": 14, "celestial": 12, "interiors": 14, "accessories": 12, "emergency": 9, "debris": 12}
res = {}
hashes = collections.defaultdict(list)


def parse_mtl(path):
    mats, cur = {}, None
    for ln in open(path):
        p = ln.split()
        if not p:
            continue
        if p[0] == "newmtl":
            cur = p[1]
            mats[cur] = {}
        elif cur and p[0] in ("Kd", "Ke", "d", "Ns", "Ks", "illum"):
            mats[cur][p[0]] = p[1:]
    return mats


for a in cat["assets"]:
    aid = a["id"]
    r = {"id": aid, "name": a["name"], "category": a["category"], "problems": [], "warnings": []}
    res[aid] = r
    objp = os.path.join(root, a["file"])
    mtlp = os.path.join(root, a["mtl"])
    if not os.path.exists(objp):
        r["problems"].append("OBJ missing"); continue
    if not os.path.exists(mtlp):
        r["problems"].append("MTL missing"); continue
    V, VN, objs, cur = [], [], collections.OrderedDict(), None
    mtllibs, usemtl, curmat = [], set(), None
    nf = 0
    for ln in open(objp):
        p = ln.split()
        if not p:
            continue
        t = p[0]
        if t == "v":
            V.append(tuple(map(float, p[1:4])))
        elif t == "vn":
            VN.append(tuple(map(float, p[1:4])))
        elif t == "o":
            cur = p[1]
            objs[cur] = []
        elif t == "mtllib":
            mtllibs.append(p[1])
        elif t == "usemtl":
            curmat = p[1]; usemtl.add(curmat)
        elif t == "f":
            if cur is None:
                cur = "_unnamed"; objs[cur] = []
            idx = []
            for tok in p[1:]:
                s = tok.split("/")
                vi = int(s[0]); vi = vi - 1 if vi > 0 else len(V) + vi
                ni = None
                if len(s) > 2 and s[2]:
                    ni = int(s[2]); ni = ni - 1 if ni > 0 else len(VN) + ni
                idx.append((vi, ni))
            objs[cur].append((idx, curmat))
            nf += 1
    r["vertices"], r["faces"], r["objects"] = len(V), nf, len(objs)
    if not V or not nf:
        r["problems"].append("no vertices or faces")
    # indices
    bad = 0
    for o, fs in objs.items():
        for idx, _ in fs:
            if len(idx) < 3:
                bad += 1
            for vi, ni in idx:
                if not (0 <= vi < len(V)) or (ni is not None and not (0 <= ni < len(VN))):
                    bad += 1
    if bad:
        r["problems"].append(f"{bad} invalid face index/degenerate face records")
    if any(not all(math.isfinite(c) for c in v) for v in V):
        r["problems"].append("NaN/inf vertex")
    # mtl
    if not mtllibs or not os.path.exists(os.path.join(os.path.dirname(objp), mtllibs[0])):
        r["problems"].append("mtllib reference does not resolve")
    else:
        mats = parse_mtl(os.path.join(os.path.dirname(objp), mtllibs[0]))
        miss = [m for m in usemtl if m not in mats]
        if miss:
            r["problems"].append(f"usemtl not defined in MTL: {miss}")
        nokd = [m for m in mats if "Kd" not in mats[m]]
        if nokd:
            r["problems"].append(f"MTL materials without Kd: {nokd}")
        r["materials"] = sorted(mats)
    # geometry
    xs = [v[0] for v in V]; ys = [v[1] for v in V]; zs = [v[2] for v in V]
    bb = (min(xs), min(ys), min(zs), max(xs), max(ys), max(zs))
    r["bbox_min"] = [round(c, 4) for c in bb[:3]]; r["bbox_max"] = [round(c, 4) for c in bb[3:]]
    dims = a["dimensions_m"]
    got = (bb[3] - bb[0], bb[4] - bb[1], bb[5] - bb[2])
    exp = (dims["x_width_m"], dims["y_height_m"], dims["z_depth_m"])
    if any(abs(g - e) > max(.01, .01 * e) for g, e in zip(got, exp)):
        r["problems"].append(f"OBJ bbox {tuple(round(x, 3) for x in got)} != catalog dims {exp}")
    ground = a["category"] not in ("celestial",) and a["id"] not in ("ANIMAL_02", "ANIMAL_04", "DISASTER_01", "DISASTER_02", "DISASTER_03", "DISASTER_05", "DISASTER_06", "DISASTER_14", "DISASTER_08", "DISASTER_09")
    if ground and abs(bb[1]) > 0.012 and a["id"] not in ("ANIMAL_01", "ANIMAL_03"):
        r["warnings"].append(f"min Y = {bb[1]:.3f} (expected ~0 for a grounded object)")
    # degenerate (zero-area) triangles and per-object signed volume (outward normals)
    degen = 0
    neg = []
    for o, fs in objs.items():
        vol = 0.0
        for idx, _ in fs:
            p0, p1, p2 = (V[i[0]] for i in idx[:3])
            ux, uy, uz = p1[0] - p0[0], p1[1] - p0[1], p1[2] - p0[2]
            vx, vy, vz = p2[0] - p0[0], p2[1] - p0[1], p2[2] - p0[2]
            cx, cy, cz = uy * vz - uz * vy, uz * vx - ux * vz, ux * vy - uy * vx
            if cx * cx + cy * cy + cz * cz < 1e-14:
                degen += 1
            vol += (p0[0] * cx + p0[1] * cy + p0[2] * cz) / 6.0
        if vol < -1e-9:
            neg.append(o)
    r["degenerate_triangles"] = degen
    if degen > 0.01 * max(1, nf):
        r["warnings"].append(f"{degen} zero-area triangles")
    if neg:
        r["warnings"].append(f"negative signed volume (inward/open surface) in: {[n.split(a['id'])[-1] for n in neg]}")
    # duplicate object geometry inside the file
    sigs = collections.Counter()
    for o, fs in objs.items():
        used = sorted({i[0] for idx, _ in fs for i in idx})
        sig = hashlib.md5(str(sorted((round(V[i][0] - V[used[0]][0], 4), round(V[i][1] - V[used[0]][1], 4), round(V[i][2] - V[used[0]][2], 4)) for i in used)).encode()).hexdigest()
        sigs[sig] += 1
    dups = sum(c - 1 for c in sigs.values() if c > 1)
    r["duplicate_object_meshes"] = dups
    if dups:
        r["warnings"].append(f"{dups} object(s) with identical vertex layout to another object in the same file (mirrored/instanced parts count)")
    nm = [o for o in objs if not o.startswith(a["id"])]
    if nm:
        r["problems"].append(f"object names not prefixed with asset id: {nm[:3]}")
    h = hashlib.md5(str(sorted((round(v[0], 3), round(v[1], 3), round(v[2], 3)) for v in V)).encode()).hexdigest()
    hashes[h].append(aid)
    r["geometry_hash"] = h
    # metadata
    mp = os.path.join(root, a["metadata"])
    if not os.path.exists(mp):
        r["problems"].append("metadata JSON missing")
    else:
        m = json.load(open(mp))
        if len(m["parts"]) != len(objs):
            r["problems"].append(f"metadata parts {len(m['parts'])} != OBJ objects {len(objs)}")
    if not a.get("preview") or not os.path.exists(os.path.join(root, a["preview"])):
        r["problems"].append("preview PNG missing")
for h, ids in hashes.items():
    if len(ids) > 1:
        for i in ids:
            res[i]["problems"].append(f"identical geometry to {[x for x in ids if x != i]}")
counts = collections.Counter(a["category"] for a in cat["assets"])
summary = {"total": len(cat["assets"]), "per_category": dict(counts), "expected": EXPECT,
           "counts_ok": dict(counts) == EXPECT and len(cat["assets"]) == 81,
           "assets_with_problems": [k for k, v in res.items() if v["problems"]],
           "assets_with_warnings": [k for k, v in res.items() if v["warnings"] and not v["problems"]],
           "total_vertices": sum(v.get("vertices", 0) for v in res.values()),
           "total_faces": sum(v.get("faces", 0) for v in res.values())}
json.dump({"summary": summary, "assets": res}, open(os.path.join(root, "metadata", "_validation_results.json"), "w"), indent=1)
print(json.dumps(summary, indent=1))
for k, v in res.items():
    if v["problems"] or v["warnings"]:
        print(k, v["name"], "PROBLEMS:", v["problems"], "WARN:", v["warnings"])
