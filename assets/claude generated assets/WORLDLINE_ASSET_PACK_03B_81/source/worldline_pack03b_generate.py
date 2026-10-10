"""
WORLDLINE LAB - ASSET PACK 03B : 81-MODEL GENERATOR (single self-contained Blender Python script)
==============================================================================================
    blender -b -P worldline_pack03b_generate.py -- --out ./WORLDLINE_ASSET_PACK_03B_81 [--only ANIMAL,CELESTIAL_01] [--no-render]

Builds every model procedurally with bpy/bmesh (no add-ons, no external textures), exports OBJ + MTL per asset
(Y-up, forward = -Z, metres, grounded objects rest at y = 0), writes per-asset metadata JSON, a preview PNG
and ASSET_CATALOG.json.  Tested with Blender 5.2 (bpy module); needs Blender 3.2+ for the wm.obj_export operator.
"""
import argparse
import json
import math
import os
import random
import sys

import bmesh
import bpy
from mathutils import Vector

# ==========================================================================
# WORLDLINE KIT (embedded in every script so each one is self-contained)
# ==========================================================================
# STYLE BIBLE
#  UNITS   : metres, Z-up (glTF export converts to Y-up). Front of every
#            vehicle/building/character faces -Y in Blender.
#  ORIGINS : root empty at ground level; each part's origin sits at its joint
#            (wheels at axle centre, doors/arms at hinges) so it can animate.
#  SHADING : flat/faceted, 1-segment chamfers on hard edges.
#  MATERIAL: Principled BSDF, flat colours, no textures -> self-contained GLB.
#  NAMING  : WL_<Category>_<Name>_<Variant>_<Part>[_<Side>]

LIB_FOLDERS = ["characters", "vehicles", "buildings", "vegetation", "streets",
               "props", "harbor", "terrain", "disaster", "previews", "blender_source"]


def parse_args():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=os.path.join(os.getcwd(), "WORLDLINE_3D_ASSET_LIBRARY"))
    p.add_argument("--no-render", action="store_true")
    p.add_argument("--quick", action="store_true", help="tiny low-sample test renders")
    p.add_argument("--engine", default="CYCLES")
    p.add_argument("--samples", type=int, default=32)
    args, _ = p.parse_known_args(argv)
    return args


def ensure_dirs(root):
    dirs = {}
    for f in LIB_FOLDERS:
        path = os.path.join(root, f)
        os.makedirs(path, exist_ok=True)
        dirs[f] = path
    return dirs


# ---------------------------------------------------------------- scene/mats

def reset_scene():
    for o in list(bpy.data.objects):
        bpy.data.objects.remove(o, do_unlink=True)
    for block in (bpy.data.meshes, bpy.data.materials, bpy.data.cameras,
                  bpy.data.lights, bpy.data.collections, bpy.data.worlds):
        for d in list(block):
            block.remove(d)
    sc = bpy.context.scene
    sc.unit_settings.system = "METRIC"
    sc.unit_settings.scale_length = 1.0


def new_collection(name):
    c = bpy.data.collections.new(name)
    bpy.context.scene.collection.children.link(c)
    return c


def srgb_hex_to_linear(h):
    h = h.lstrip("#")
    out = []
    for i in (0, 2, 4):
        c = int(h[i:i + 2], 16) / 255.0
        out.append(c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4)
    return (out[0], out[1], out[2], 1.0)


def make_material(name, hex_color, rough=0.8, metallic=0.0, emit=0.0):
    m = bpy.data.materials.new(name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    col = srgb_hex_to_linear(hex_color)
    bsdf.inputs["Base Color"].default_value = col
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metallic
    if emit > 0:
        try:
            bsdf.inputs["Emission Color"].default_value = col
            bsdf.inputs["Emission Strength"].default_value = emit
        except KeyError:
            pass
    m.diffuse_color = col
    return m


def build_materials(prefix, palette):
    mats = {}
    for k, v in palette.items():
        hexc, rough = v[0], v[1]
        metal = v[2] if len(v) > 2 else 0.0
        emit = v[3] if len(v) > 3 else 0.0
        mats[k] = make_material(f"{prefix}_{k}", hexc, rough, metal, emit)
    return mats


# ------------------------------------------------------------------ geometry
# rings are (t, c1, c2, h1, h2); each ring is an n-gon whose FLAT FACES sit at
# +-h1 / +-h2 about the centre (c1, c2).
#   axis z: t=z, c1=x, c2=y     axis y: t=y, c1=x, c2=z     axis x: t=x, c1=y, c2=z

def ring_verts(bm, rings, n, axis):
    k = 1.0 / math.cos(math.pi / n)
    out = []
    for (t, c1, c2, h1, h2) in rings:
        row = []
        for i in range(n):
            a = 2.0 * math.pi * (i + 0.5) / n
            u = c1 + h1 * math.cos(a) * k
            v = c2 + h2 * math.sin(a) * k
            if axis == "z":
                co = (u, v, t)
            elif axis == "y":
                co = (u, t, v)
            else:
                co = (t, u, v)
            row.append(bm.verts.new(co))
        out.append(row)
    return out


def skin(bm, rows, cap0=True, cap1=True):
    m = len(rows[0])
    for r0, r1 in zip(rows, rows[1:]):
        for j in range(m):
            try:
                bm.faces.new((r0[j], r0[(j + 1) % m], r1[(j + 1) % m], r1[j]))
            except ValueError:
                pass
    try:
        if cap0:
            bm.faces.new(rows[0][::-1])
        if cap1:
            bm.faces.new(rows[-1])
    except ValueError:
        pass


def loft(bm, rings, n=8, axis="z"):
    skin(bm, ring_verts(bm, rings, n, axis))


def loft_pts(bm, stations, axis="y"):
    """stations = [(t, [(u, v), ...]), ...] with the same point count per station."""
    rows = []
    for t, pts in stations:
        row = []
        for (u, v) in pts:
            co = (u, v, t) if axis == "z" else ((u, t, v) if axis == "y" else (t, u, v))
            row.append(bm.verts.new(co))
        rows.append(row)
    skin(bm, rows)


def rect_profile(bot, top, hw_bot, hw_top=None, cb=0.05, ct=0.08, cx=0.0):
    """8-point cross-section: vertical-ish sides, chamfered corners, optional tumblehome."""
    hw_top = hw_bot if hw_top is None else hw_top
    return [(cx - hw_bot + cb, bot), (cx + hw_bot - cb, bot), (cx + hw_bot, bot + cb),
            (cx + hw_top, top - ct), (cx + hw_top - ct, top), (cx - hw_top + ct, top),
            (cx - hw_top, top - ct), (cx - hw_bot, bot + cb)]


def box(bm, x0, x1, y0, y1, z0, z1):
    x0, x1 = min(x0, x1), max(x0, x1)
    y0, y1 = min(y0, y1), max(y0, y1)
    z0, z1 = min(z0, z1), max(z0, z1)
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    hw, hd = (x1 - x0) / 2, (y1 - y0) / 2
    loft(bm, [(z0, cx, cy, hw, hd), (z1, cx, cy, hw, hd)], n=4)


def frustum(bm, z0, z1, cx, cy, hw0, hd0, hw1, hd1, n=4):
    loft(bm, [(z0, cx, cy, hw0, hd0), (z1, cx, cy, hw1, hd1)], n=n)


def solid(bm, bottom, top):
    """Closed solid from two equal-length point loops (bottom, top)."""
    b = [bm.verts.new(p) for p in bottom]
    t = [bm.verts.new(p) for p in top]
    skin(bm, [b, t])


def _basis(d, up=(0, 0, 1)):
    d = Vector(d).normalized()
    up = Vector(up)
    if abs(d.dot(up)) > 0.98:
        up = Vector((1, 0, 0)) if abs(d.x) < 0.9 else Vector((0, 1, 0))
    s = d.cross(up).normalized()
    u = s.cross(d).normalized()
    return s, u


def beam(bm, p0, p1, w, h, w2=None, h2=None, up=(0, 0, 1)):
    p0, p1 = Vector(p0), Vector(p1)
    s, u = _basis(p1 - p0, up)
    rows = []
    for p, ww, hh in ((p0, w, h), (p1, w if w2 is None else w2, h if h2 is None else h2)):
        rows.append([bm.verts.new(p + s * sx * ww / 2 + u * uy * hh / 2)
                     for sx, uy in ((-1, -1), (1, -1), (1, 1), (-1, 1))])
    skin(bm, rows)


def cyl(bm, p0, p1, r0, r1=None, n=12, rot=0.0, cap0=True, cap1=True):
    p0, p1 = Vector(p0), Vector(p1)
    r1 = r0 if r1 is None else r1
    s, u = _basis(p1 - p0)
    rows = []
    for p, r in ((p0, r0), (p1, r1)):
        rows.append([bm.verts.new(p + (s * math.cos(a) + u * math.sin(a)) * r)
                     for a in (2 * math.pi * (i + 0.5) / n + rot for i in range(n))])
    skin(bm, rows, cap0, cap1)


def ico(bm, c, r, sub=1, squash=(1, 1, 1), jitter=0.0, rng=None):
    try:
        res = bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=1.0)
    except TypeError:
        res = bmesh.ops.create_icosphere(bm, subdivisions=sub, diameter=2.0)
    rng = rng or random.Random(1)
    c = Vector(c)
    for v in res["verts"]:
        j = Vector((rng.uniform(-1, 1), rng.uniform(-1, 1), rng.uniform(-1, 1))) * jitter * r
        v.co = Vector((v.co.x * squash[0] * r, v.co.y * squash[1] * r, v.co.z * squash[2] * r)) + c + j


def bevel_hard_edges(bm, width, min_angle_deg=50.0):
    lim = math.radians(min_angle_deg)
    edges = []
    for e in bm.edges:
        if len(e.link_faces) == 2:
            try:
                if e.calc_face_angle() > lim:
                    edges.append(e)
            except ValueError:
                pass
    if edges and width > 0:
        try:
            bmesh.ops.bevel(bm, geom=edges, offset=width, segments=1, affect="EDGES")
        except Exception as ex:
            print(f"  [warn] bevel skipped: {ex}")


class Rig:
    """Parts with joint-located origins and a clean parent hierarchy."""

    def __init__(self, coll, asset, mats):
        self.coll, self.asset, self.mats = coll, asset, mats
        self.objs, self.pivots, self.info = {}, {}, []
        root = bpy.data.objects.new(f"{asset}_Root", None)
        root.empty_display_type = "PLAIN_AXES"
        root.empty_display_size = 0.5
        coll.objects.link(root)
        self.objs["root"] = root
        self.pivots["root"] = Vector((0, 0, 0))
        self.root = root

    def add(self, key, shapes, mat, pivot=(0, 0, 0), parent="root", bevel=0.0,
            mirror=False, bevel_angle=50.0):
        name = f"{self.asset}_{key}"
        pivot = Vector(pivot)
        bm = bmesh.new()
        for sh in shapes:
            before = set(bm.verts)
            smir = False
            if callable(sh):
                sh(bm)
            else:
                smir = sh.get("mirror", False)
                if "fn" in sh:
                    sh["fn"](bm)
                elif "stations" in sh:
                    loft_pts(bm, sh["stations"], axis=sh.get("axis", "y"))
                else:
                    loft(bm, sh["rings"], n=sh.get("n", 8), axis=sh.get("axis", "z"))
            if smir != mirror:
                for v in bm.verts:
                    if v not in before:
                        v.co.x = -v.co.x
        if not bm.faces:
            print(f"  [warn] part {name} has no faces")
        bmesh.ops.translate(bm, vec=-pivot, verts=bm.verts)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        bevel_hard_edges(bm, bevel, bevel_angle)
        bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        for p in mesh.polygons:
            p.use_smooth = False
        mesh.update()
        mesh.materials.append(self.mats[mat])
        obj = bpy.data.objects.new(name, mesh)
        self.coll.objects.link(obj)
        obj.parent = self.objs[parent]
        obj.location = pivot - self.pivots[parent]
        self.objs[key] = obj
        self.pivots[key] = pivot
        tris = sum(len(p.vertices) - 2 for p in mesh.polygons)
        self.info.append({"name": name, "parent": self.objs[parent].name,
                          "pivot_world": [round(c, 4) for c in pivot],
                          "material": self.mats[mat].name, "triangles": tris})
        return obj

    def meshes(self):
        return [o for o in self.objs.values() if o.type == "MESH"]


# ---------------------------------------------------------- validate / export

def world_bounds(objs):
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        if o.type != "MESH":
            continue
        for c in o.bound_box:
            w = o.matrix_world @ Vector(c)
            for i in range(3):
                mn[i] = min(mn[i], w[i])
                mx[i] = max(mx[i], w[i])
    return mn, mx


def validate(rig, height_range=None, max_tris=40000, on_ground=True):
    bpy.context.view_layer.update()
    meshes = rig.meshes()
    mn, mx = world_bounds(meshes)
    height = mx.z - mn.z
    problems = []
    if height_range and not (height_range[0] <= height <= height_range[1]):
        problems.append(f"height {height:.3f} m outside {height_range}")
    if on_ground and abs(mn.z) > 0.02:
        problems.append(f"asset not resting on ground (min z = {mn.z:.3f})")
    for o in meshes:
        if len(o.data.polygons) == 0:
            problems.append(f"{o.name} has no faces")
        if not o.data.materials:
            problems.append(f"{o.name} has no material")
    tris = sum(i["triangles"] for i in rig.info)
    if tris > max_tris:
        problems.append(f"triangle budget exceeded: {tris}")
    print(f"[validate] parts={len(meshes)} tris={tris} size="
          f"{mx.x - mn.x:.2f} x {mx.y - mn.y:.2f} x {height:.2f} m")
    for p in problems:
        print(f"[validate][PROBLEM] {p}")
    if not problems:
        print("[validate] all checks passed")
    return {"width_m": round(mx.x - mn.x, 3), "depth_m": round(mx.y - mn.y, 3),
            "height_m": round(height, 3), "triangles": tris,
            "part_count": len(meshes), "problems": problems}


def export_glb(rig, path):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    for o in rig.objs.values():
        o.select_set(True)
    bpy.context.view_layer.objects.active = rig.root
    try:
        bpy.ops.export_scene.gltf(filepath=path, export_format="GLB", use_selection=True)
        print(f"[export] GLB written: {path}")
        return True
    except Exception as ex:
        print(f"[export][ERROR] GLB export failed: {ex}")
        return False


def verify_glb(path, expected_nodes):
    before = set(bpy.data.objects)
    try:
        bpy.ops.import_scene.gltf(filepath=path)
    except Exception as ex:
        print(f"[verify][ERROR] re-import failed: {ex}")
        return False
    new = [o for o in bpy.data.objects if o not in before]
    meshes = [o for o in new if o.type == "MESH"]
    print(f"[verify] re-imported {len(new)} nodes ({len(meshes)} meshes); source had {expected_nodes} nodes")
    for o in new:
        bpy.data.objects.remove(o, do_unlink=True)
    return True


# ------------------------------------------------------------------ rendering

def setup_engine(scene, engine, samples):
    if engine == "CYCLES":
        scene.render.engine = "CYCLES"
        scene.cycles.samples = samples
        scene.cycles.device = "CPU"
        try:
            scene.cycles.use_denoising = True
        except Exception:
            pass
    else:
        for cand in ("BLENDER_EEVEE_NEXT", "BLENDER_EEVEE"):
            try:
                scene.render.engine = cand
                break
            except TypeError:
                continue
    try:
        scene.view_settings.view_transform = "Standard"
    except Exception:
        pass
    scene.render.image_settings.file_format = "PNG"


def setup_lighting(coll, sky="#BFD9EE", key=3.6, fill=1.0, key_rot=(52, 0, 28)):
    world = bpy.data.worlds.new("WLWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = srgb_hex_to_linear(sky)
    bg.inputs[1].default_value = 1.0
    bpy.context.scene.world = world

    def sun(name, energy, rot, color):
        d = bpy.data.lights.new(name, "SUN")
        d.energy = energy
        d.color = color
        d.angle = math.radians(6)
        o = bpy.data.objects.new(name, d)
        o.rotation_euler = tuple(math.radians(a) for a in rot)
        coll.objects.link(o)
    sun("Key", key, key_rot, (1.0, 0.96, 0.90))
    sun("Fill", fill, (65, 0, -140), (0.80, 0.88, 1.0))


def ground_slab(coll, cx, cy, half, color="#D9D4C7", name="PreviewGround"):
    bm = bmesh.new()
    box(bm, cx - half, cx + half, cy - half, cy + half, -0.04, 0.0)
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    mesh = bpy.data.meshes.new(name)
    bm.to_mesh(mesh)
    bm.free()
    mesh.materials.append(make_material(name + "_mat", color, 0.95))
    o = bpy.data.objects.new(name, mesh)
    coll.objects.link(o)
    return o


def frame_camera(cam, corners, center, az, el, lens, res, margin=0.92):
    a, e = math.radians(az), math.radians(el)
    toward = Vector((-math.sin(a) * math.cos(e), math.cos(a) * math.cos(e), -math.sin(e)))
    f = toward.normalized()
    right = f.cross(Vector((0, 0, 1))).normalized()
    up = right.cross(f).normalized()
    big = 18.0 / lens
    W, H = res
    tx = big if W >= H else big * W / H
    ty = big if H >= W else big * H / W
    d = 1.0
    for c in corners:
        rel = c - center
        xr, yr, w = rel.dot(right), rel.dot(up), rel.dot(f)
        d = max(d, abs(xr) / (tx * margin) - w, abs(yr) / (ty * margin) - w)
    loc = center - f * d
    cam.location = loc
    cam.rotation_euler = (center - loc).to_track_quat("-Z", "Y").to_euler()


def render_views(dirs, args, name, rig, views=None, res=(1400, 1000), ground=True,
                 ground_color="#D9D4C7", sky="#BFD9EE"):
    scene = bpy.context.scene
    pcoll = new_collection("Preview_Rig")
    setup_engine(scene, args.engine, args.samples)
    mn, mx = world_bounds(rig.meshes())
    center = (mn + mx) / 2
    half = max(mx.x - mn.x, mx.y - mn.y) * 1.2 + 2
    if ground:
        ground_slab(pcoll, center.x, center.y, half, ground_color)
    setup_lighting(pcoll, sky)
    cam_data = bpy.data.cameras.new("PreviewCam")
    cam_data.lens = 50
    cam = bpy.data.objects.new("PreviewCam", cam_data)
    pcoll.objects.link(cam)
    scene.camera = cam
    corners = [Vector((x, y, z)) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
    views = views or {"three_quarter": (35, 14), "front": (0, 6), "side": (90, 6), "back": (200, 10)}
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    paths = []
    for vname, (az, el) in views.items():
        frame_camera(cam, corners, center, az, el, cam_data.lens, res)
        out = os.path.join(dirs["previews"], f"{name}_{vname}.png")
        scene.render.filepath = out
        try:
            bpy.ops.render.render(write_still=True)
            print(f"[render] {out}")
            paths.append(out)
        except Exception as ex:
            print(f"[render][ERROR] {vname}: {ex}")
            break
    return paths




# ==========================================================================
# PACK 03B LIBRARY  (builds on the Worldline kit above)
# ==========================================================================
# CONVENTIONS (Pack 03B)
#   Build space (Blender): Z-up, FRONT = +Y, +X = object's left when facing front... (x is simply "right-handed")
#   OBJ export maps Blender (x, y, z) -> file (x, z, -y):   file Y-up, FRONT = -Z.
#   Grounded objects rest at z = 0 (file y = 0).  Celestial objects are centred on the origin.
import hashlib
from mathutils import noise as mnoise

REGISTRY = []


def asset(aid, name, folder, style="ground", pose=None, notes=None):
    def deco(fn):
        REGISTRY.append(dict(id=aid, name=name, folder=folder, style=style, fn=fn, pose=pose, notes=notes or {}))
        return fn
    return deco


# ------------------------------------------------------------------ palette
# spec: (hex, roughness, metallic, emission_strength, alpha)
PAL = {
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
}


def pal_spec(name):
    s = PAL[name]
    hexc, rough = s[0], s[1]
    metal = s[2] if len(s) > 2 else 0.0
    emit = s[3] if len(s) > 3 else 0.0
    alpha = s[4] if len(s) > 4 else 1.0
    return hexc, rough, metal, emit, alpha


def mk_mat(name):
    hexc, rough, metal, emit, alpha = pal_spec(name)
    m = bpy.data.materials.new("WL_" + name)
    m.use_nodes = True
    bsdf = m.node_tree.nodes.get("Principled BSDF")
    col = srgb_hex_to_linear(hexc)
    bsdf.inputs["Base Color"].default_value = col
    bsdf.inputs["Roughness"].default_value = rough
    bsdf.inputs["Metallic"].default_value = metal
    if emit > 0:
        try:
            bsdf.inputs["Emission Color"].default_value = col
            bsdf.inputs["Emission Strength"].default_value = emit
        except KeyError:
            pass
    if alpha < 1.0:
        bsdf.inputs["Alpha"].default_value = alpha
        try:
            m.blend_method = "BLEND"
        except Exception:
            pass
    m.diffuse_color = col
    return m


def world_bounds(objs):
    """Exact world-space bounds from the real vertices (kit.world_bounds uses object bound boxes, which over-estimate rotated parts)."""
    mn = Vector((1e9, 1e9, 1e9))
    mx = Vector((-1e9, -1e9, -1e9))
    for o in objs:
        if o.type != "MESH":
            continue
        M = o.matrix_world
        for v in o.data.vertices:
            w = M @ v.co
            for i in range(3):
                if w[i] < mn[i]:
                    mn[i] = w[i]
                if w[i] > mx[i]:
                    mx[i] = w[i]
    return mn, mx


# ------------------------------------------------------------------ builder
def with_mat(idx, fn):
    """Run fn(bm) and tag every newly-created face with material slot idx."""
    def run(bm):
        before = set(bm.faces)
        fn(bm)
        for f in bm.faces:
            if f not in before:
                f.material_index = idx
    return run



def fix_normals(bm):
    """Make every closed island outward-facing by testing its signed volume (recalc alone is not always right)."""
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])
    seen = set()
    for f0 in bm.faces[:]:
        if f0 in seen:
            continue
        island, stack = [], [f0]
        seen.add(f0)
        while stack:
            f = stack.pop()
            island.append(f)
            for e in f.edges:
                for g in e.link_faces:
                    if g not in seen:
                        seen.add(g)
                        stack.append(g)
        closed = all(len(e.link_faces) == 2 for f in island for e in f.edges)
        if not closed:
            continue
        vol = 0.0
        for f in island:
            vs = [v.co for v in f.verts]
            for i in range(1, len(vs) - 1):
                vol += vs[0].dot(vs[i].cross(vs[i + 1]))
        if vol < 0:
            bmesh.ops.reverse_faces(bm, faces=island)


class Builder:
    def __init__(self, coll, asset_name):
        self.coll, self.asset = coll, asset_name
        self.mats = {}
        self.objs, self.pivots, self.info = {}, {}, []
        root = bpy.data.objects.new(f"{asset_name}_Root", None)
        coll.objects.link(root)
        self.objs["root"], self.root = root, root
        self.pivots["root"] = Vector((0, 0, 0))
        self.attach = {}      # name -> (x,y,z) attachment / grip points in build space

    def m(self, name):
        if name not in self.mats:
            self.mats[name] = mk_mat(name)
        return self.mats[name]

    def point(self, name, p):
        self.attach[name] = tuple(p)

    def add(self, key, shapes, mat, pivot=(0, 0, 0), parent="root", bevel=0.0, mirror=False,
            face_mat=None, smooth=False, bevel_angle=50.0):
        name = f"{self.asset}_{key}"
        pivot = Vector(pivot)
        mats = [mat] if isinstance(mat, str) else list(mat)
        bm = bmesh.new()
        for sh in shapes:
            before = set(bm.verts)
            smir = False
            if callable(sh):
                sh(bm)
            else:
                smir = sh.get("mirror", False)
                if "fn" in sh:
                    sh["fn"](bm)
                else:
                    loft(bm, sh["rings"], n=sh.get("n", 8), axis=sh.get("axis", "z"))
            if smir != mirror:
                for v in bm.verts:
                    if v not in before:
                        v.co.x = -v.co.x
        if not bm.faces:
            print(f"  [warn] part {name} has no faces")
        if face_mat:
            for f in bm.faces:
                f.material_index = face_mat(f)
        bmesh.ops.translate(bm, vec=-pivot, verts=bm.verts)
        fix_normals(bm)
        if bevel:
            bevel_hard_edges(bm, bevel, bevel_angle)
            fix_normals(bm)
        # clean-up: triangulate and drop zero-area triangles (collapsed apex rings, degenerate tapers)
        bmesh.ops.triangulate(bm, faces=bm.faces[:])
        zero = [f for f in bm.faces if f.calc_area() < 1e-10]
        if zero:
            bmesh.ops.delete(bm, geom=zero, context="FACES")
        mesh = bpy.data.meshes.new(name)
        bm.to_mesh(mesh)
        bm.free()
        for p in mesh.polygons:
            p.use_smooth = smooth
        mesh.update()
        for mn in mats:
            mesh.materials.append(self.m(mn))
        obj = bpy.data.objects.new(name, mesh)
        self.coll.objects.link(obj)
        obj.parent = self.objs[parent]
        obj.location = pivot - self.pivots[parent]
        self.objs[key] = obj
        self.pivots[key] = pivot
        tris = sum(len(p.vertices) - 2 for p in mesh.polygons)
        self.info.append({"name": name, "key": key, "parent": self.objs[parent].name,
                          "pivot_build": [round(c, 4) for c in pivot], "materials": [self.mats[x].name for x in mats],
                          "triangles": tris})
        return obj

    def place(self, rot=(0, 0, 0), drop=True):
        """Rotate the whole asset (about its root) and optionally drop it so its lowest point touches z=0."""
        from mathutils import Euler
        self.root.rotation_euler = Euler(tuple(math.radians(a) for a in rot), "XYZ")
        bpy.context.view_layer.update()
        M = self.root.matrix_world.copy()
        for i in self.info:
            i["pivot_build"] = [round(c, 4) for c in (M @ Vector(i["pivot_build"]))]
        self.attach = {k: tuple(M @ Vector(v)) for k, v in self.attach.items()}
        if drop:
            mn, _ = world_bounds(self.meshes())
            self.root.location.z -= mn.z
            bpy.context.view_layer.update()
            for i in self.info:
                i["pivot_build"][2] = round(i["pivot_build"][2] - mn.z, 4)
            self.attach = {k: (v[0], v[1], v[2] - mn.z) for k, v in self.attach.items()}

    def meshes(self):
        return [o for o in self.objs.values() if o.type == "MESH"]

    # compatibility with kit.world_bounds / validators
    @property
    def rig(self):
        return self


def to_file(v):
    return (round(v[0], 5), round(v[2], 5), round(-v[1], 5))


# ------------------------------------------------------------- geometry kit
def lathe(bm, profile, n=12, c=(0, 0, 0), closed=False, rot=0.0, cap0=True, cap1=True, scale_xy=(1.0, 1.0)):
    """Revolve [(r, h), ...] about the Z axis through c.  r<=0 collapses to an apex vertex."""
    cx, cy, cz = c
    rows = []
    for (r, h) in profile:
        if r <= 1e-7:
            rows.append(bm.verts.new((cx, cy, cz + h)))
        else:
            rows.append([bm.verts.new((cx + math.cos(2 * math.pi * i / n + rot) * r * scale_xy[0],
                                       cy + math.sin(2 * math.pi * i / n + rot) * r * scale_xy[1], cz + h))
                         for i in range(n)])
    pairs = list(zip(rows, rows[1:]))
    if closed:
        pairs.append((rows[-1], rows[0]))
    for a, b in pairs:
        la, lb = isinstance(a, list), isinstance(b, list)
        for j in range(n):
            k = (j + 1) % n
            try:
                if la and lb:
                    bm.faces.new((a[j], a[k], b[k], b[j]))
                elif la:
                    bm.faces.new((a[j], a[k], b))
                elif lb:
                    bm.faces.new((a, b[k], b[j]))
            except ValueError:
                pass
    if not closed:
        try:
            if cap0 and isinstance(rows[0], list):
                bm.faces.new(rows[0][::-1])
            if cap1 and isinstance(rows[-1], list):
                bm.faces.new(rows[-1])
        except ValueError:
            pass


def torus(bm, c, R, r, n=18, m=8, axis="z", squash=1.0):
    prof = [(R + r * math.cos(2 * math.pi * k / m), r * math.sin(2 * math.pi * k / m) * squash) for k in range(m)]
    tmp = bmesh.new()
    lathe(tmp, prof, n=n, closed=True)
    if axis == "x":
        bmesh.ops.rotate(tmp, verts=tmp.verts, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(math.pi / 2, 3, "Y"))
    elif axis == "y":
        bmesh.ops.rotate(tmp, verts=tmp.verts, cent=(0, 0, 0), matrix=__import__("mathutils").Matrix.Rotation(math.pi / 2, 3, "X"))
    bmesh.ops.translate(tmp, vec=c, verts=tmp.verts)
    mesh = bpy.data.meshes.new("_tmp")
    tmp.to_mesh(mesh)
    tmp.free()
    bm.from_mesh(mesh)
    bpy.data.meshes.remove(mesh)


def _frame_rows(bm, pts, radii, n, rot=0.0):
    pts = [Vector(p) for p in pts]
    if not isinstance(radii, (list, tuple)):
        radii = [radii] * len(pts)
    tang = []
    for i in range(len(pts)):
        a = pts[max(i - 1, 0)]
        b = pts[min(i + 1, len(pts) - 1)]
        t = (b - a)
        tang.append(t.normalized() if t.length > 1e-9 else Vector((0, 0, 1)))
    s, u = _basis(tang[0])
    rows = []
    for i, p in enumerate(pts):
        if i > 0:
            t = tang[i]
            s = s - t * s.dot(t)
            if s.length < 1e-6:
                s, u = _basis(t)
            else:
                s.normalize()
            u = t.cross(s).normalized()
        r = radii[i]
        rx, ry = (r, r) if not isinstance(r, (list, tuple)) else r
        rows.append([bm.verts.new(p + s * math.cos(2 * math.pi * k / n + rot) * rx + u * math.sin(2 * math.pi * k / n + rot) * ry)
                     for k in range(n)])
    return rows


def tube(bm, pts, radii, n=6, cap0=True, cap1=True, rot=0.0):
    rows = _frame_rows(bm, pts, radii, n, rot)
    skin(bm, rows, cap0, cap1)


def blade(bm, pts, half_widths, thick, up=(0, 0, 1)):
    """Thin lens-shaped strip along a centreline (feathers, wings, leaves, ears, fabric)."""
    pts = [Vector(p) for p in pts]
    up = Vector(up)
    rows = []
    for i, p in enumerate(pts):
        a, b = pts[max(i - 1, 0)], pts[min(i + 1, len(pts) - 1)]
        t = (b - a).normalized()
        w = up.cross(t)
        if w.length < 1e-6:
            w = Vector((1, 0, 0))
        w.normalize()
        nrm = t.cross(w).normalized()
        hw = half_widths[i] if isinstance(half_widths, (list, tuple)) else half_widths
        th = thick[i] if isinstance(thick, (list, tuple)) else thick
        rows.append([bm.verts.new(p - w * hw), bm.verts.new(p + nrm * th), bm.verts.new(p + w * hw),
                     bm.verts.new(p - nrm * th)])
    skin(bm, rows)


def fbm(p, octaves=3, lac=2.0, gain=0.5):
    amp, s, tot = 1.0, 0.0, 0.0
    q = Vector(p)
    for _ in range(octaves):
        s += amp * mnoise.noise(q)
        tot += amp
        q = q * lac
        amp *= gain
    return s / tot


def icosphere(bm, sub=2, radius=1.0):
    try:
        res = bmesh.ops.create_icosphere(bm, subdivisions=sub, radius=radius)
    except TypeError:
        res = bmesh.ops.create_icosphere(bm, subdivisions=sub, diameter=radius * 2)
    return res["verts"]


def blob(bm, c, radii, sub=2, seed=0.0, rough=0.25, freq=1.4, octaves=3, flat=None, bias=None, craters=None):
    """Irregular rock: displaced icosphere. radii=(rx,ry,rz). flat=(nx,ny,nz,d) optional clipping plane."""
    c = Vector(c)
    verts = icosphere(bm, sub, 1.0)
    for v in verts:
        d = v.co.normalized()
        h = 1.0 + rough * fbm(d * freq + Vector((seed, seed * 1.7, seed * 0.6)), octaves)
        if bias:
            h += bias(d)
        if craters:
            h += crater_height(d, craters)
        p = Vector((d.x * radii[0], d.y * radii[1], d.z * radii[2])) * h
        if flat:
            n = Vector(flat[:3])
            ex = p.dot(n) - flat[3]
            if ex > 0:
                p -= n * ex
        v.co = p + c
    return verts


def crater_height(d, craters):
    """d: unit vector. craters: [(dir, angular_radius, depth, rim_height)] -> radial offset (fraction of R)."""
    h = 0.0
    for (cd, R, depth, rim) in craters:
        a = math.acos(max(-1.0, min(1.0, d.dot(cd))))
        t = a / R
        if t < 1.0:
            floor = 1.0 - t * t
            h -= depth * min(1.0, floor * 2.2)
        h += rim * math.exp(-((t - 1.02) / 0.22) ** 2)
    return h


def cut(bm, co, no, keep="pos", interior=1):
    """Planar cut of the whole bmesh, closing the hole with faces in material slot `interior`."""
    geom = bm.verts[:] + bm.edges[:] + bm.faces[:]
    res = bmesh.ops.bisect_plane(bm, geom=geom, plane_co=Vector(co), plane_no=Vector(no),
                                 clear_inner=(keep == "pos"), clear_outer=(keep == "neg"))
    bnd = [e for e in bm.edges if e.is_boundary]
    if bnd:
        try:
            r = bmesh.ops.triangle_fill(bm, use_beauty=True, use_dissolve=False, edges=bnd)
            for f in r["geom"]:
                if isinstance(f, bmesh.types.BMFace):
                    f.material_index = interior
        except Exception as ex:
            print(f"  [warn] cut fill failed: {ex}")
    bmesh.ops.recalc_face_normals(bm, faces=bm.faces[:])


def poly_prism(bm, outline, z0, z1, taper=None):
    """Extrude a 2D outline [(x,y)...] (any convex-ish polygon) between z0 and z1; taper=(sx,sy) scales top."""
    bot = [bm.verts.new((x, y, z0)) for x, y in outline]
    cx = sum(p[0] for p in outline) / len(outline)
    cy = sum(p[1] for p in outline) / len(outline)
    sx, sy = taper if taper else (1.0, 1.0)
    top = [bm.verts.new((cx + (x - cx) * sx, cy + (y - cy) * sy, z1)) for x, y in outline]
    skin(bm, [bot, top])


def gprism(bm, z0, z1, outline0, outline1=None):
    """Prism with different top/bottom outlines (same count)."""
    outline1 = outline1 or outline0
    bot = [bm.verts.new((x, y, z0)) for x, y in outline0]
    top = [bm.verts.new((x, y, z1)) for x, y in outline1]
    skin(bm, [bot, top])


def arc_pts(c, r, a0, a1, n, plane="xz", extra=0.0):
    pts = []
    for i in range(n):
        a = math.radians(a0 + (a1 - a0) * i / max(1, n - 1))
        if plane == "xz":
            pts.append((c[0] + r * math.cos(a), c[1], c[2] + r * math.sin(a)))
        elif plane == "yz":
            pts.append((c[0], c[1] + r * math.cos(a), c[2] + r * math.sin(a)))
        else:
            pts.append((c[0] + r * math.cos(a), c[1] + r * math.sin(a), c[2]))
    return pts


def bez(p0, p1, p2, n=8, p3=None):
    p0, p1, p2 = Vector(p0), Vector(p1), Vector(p2)
    out = []
    for i in range(n):
        t = i / (n - 1)
        if p3 is None:
            out.append((p0 * (1 - t) ** 2 + p1 * 2 * (1 - t) * t + p2 * t * t))
        else:
            q = Vector(p3)
            out.append(p0 * (1 - t) ** 3 + p1 * 3 * (1 - t) ** 2 * t + p2 * 3 * (1 - t) * t * t + q * t ** 3)
    return out


def mirror_x(pts):
    return [(-p[0], p[1], p[2]) for p in pts]


def ring_pts(c, rx, ry, n, z=None):
    return [(c[0] + rx * math.cos(2 * math.pi * i / n), c[1] + ry * math.sin(2 * math.pi * i / n)) for i in range(n)]


def smoothstep(a, b, x):
    t = max(0.0, min(1.0, (x - a) / (b - a)))
    return t * t * (3 - 2 * t)


# ----------------------------------------------------------- stats / export

def rotate_bm(bm, verts, axis, ang_deg, center=(0, 0, 0)):
    from mathutils import Matrix
    bmesh.ops.rotate(bm, verts=verts, cent=center, matrix=Matrix.Rotation(math.radians(ang_deg), 3, axis))


def merge_bm(dst, src):
    me = bpy.data.meshes.new("_merge")
    src.to_mesh(me)
    dst.from_mesh(me)
    bpy.data.meshes.remove(me)
    src.free()


def terrain_slab(bm, nx, ny, sx, sy, hfn, base_z):
    """Closed solid terrain block: height-field top, vertical skirt, flat bottom."""
    top = {}
    for j in range(ny + 1):
        for i in range(nx + 1):
            x = -sx / 2 + sx * i / nx
            y = -sy / 2 + sy * j / ny
            top[(i, j)] = bm.verts.new((x, y, hfn(x, y)))
    for j in range(ny):
        for i in range(nx):
            bm.faces.new((top[(i, j)], top[(i + 1, j)], top[(i + 1, j + 1)], top[(i, j + 1)]))
    per = [(i, 0) for i in range(nx)] + [(nx, j) for j in range(ny)] + [(i, ny) for i in range(nx, 0, -1)] + [(0, j) for j in range(ny, 0, -1)]
    bot = []
    for (i, j) in per:
        v = top[(i, j)].co
        bot.append(bm.verts.new((v.x, v.y, base_z)))
    m = len(per)
    for k in range(m):
        a, b2 = per[k], per[(k + 1) % m]
        bm.faces.new((top[a], top[b2], bot[(k + 1) % m], bot[k]))
    bm.faces.new(bot[::-1])


def jag_outline(rng, n, rx, ry, jag=0.3, cx=0.0, cy=0.0, rot=0.0):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + rot + rng.uniform(-0.18, 0.18)
        r = 1.0 + jag * rng.uniform(-1, 1)
        pts.append((cx + math.cos(a) * rx * r, cy + math.sin(a) * ry * r))
    return pts


def mesh_stats(b):
    bpy.context.view_layer.update()
    meshes = b.meshes()
    mn, mx = world_bounds(meshes)
    tris = sum(i["triangles"] for i in b.info)
    verts = sum(len(o.data.vertices) for o in meshes)
    neg_vol, open_parts = [], []
    for o in meshes:
        bm = bmesh.new()
        bm.from_mesh(o.data)
        if any(e.is_boundary or not e.is_manifold for e in bm.edges):
            open_parts.append(o.name)
        try:
            vol = bm.calc_volume(signed=True)
            if vol < 0:
                neg_vol.append(o.name)
        except Exception:
            pass
        bm.free()
    h = hashlib.md5()
    pts = sorted((round(c, 3) for o in meshes for v in o.data.vertices
                  for c in (o.matrix_world @ v.co)))
    h.update(str(len(pts)).encode() + str(pts[:: max(1, len(pts) // 600)]).encode())
    return {"min": mn, "max": mx, "tris": tris, "verts": verts, "neg_volume_parts": neg_vol,
            "open_parts": open_parts, "geom_hash": h.hexdigest()}


def export_obj(b, path):
    for o in bpy.context.scene.objects:
        o.select_set(False)
    for o in b.objs.values():
        o.select_set(True)
    bpy.context.view_layer.objects.active = b.root
    bpy.ops.wm.obj_export(filepath=path, export_selected_objects=True, export_materials=True,
                          export_triangulated_mesh=True, forward_axis="NEGATIVE_Z", up_axis="Y",
                          apply_modifiers=True, export_normals=True, export_uv=False,
                          export_smooth_groups=False, global_scale=1.0)


def render_asset_preview(b, style, path, res=(640, 640), samples=12, az=145, el=14):
    scene = bpy.context.scene
    pcoll = new_collection("Preview_Rig")
    mn, mx = world_bounds(b.meshes())
    center = (mn + mx) / 2
    setup_engine(scene, "CYCLES", samples)
    if style == "space":
        sky = "#05070E"
    elif style == "debris":
        sky = "#C7DBEA"
    else:
        sky = "#C7DBEA"
    world = bpy.data.worlds.new("WLWorld")
    world.use_nodes = True
    bg = world.node_tree.nodes["Background"]
    bg.inputs[0].default_value = srgb_hex_to_linear(sky)
    bg.inputs[1].default_value = 0.35 if style == "space" else 1.0
    scene.world = world

    def sun(name, energy, rot, color):
        d = bpy.data.lights.new(name, "SUN")
        d.energy = energy
        d.color = color
        d.angle = math.radians(5)
        o = bpy.data.objects.new(name, d)
        o.rotation_euler = tuple(math.radians(a) for a in rot)
        pcoll.objects.link(o)
    if style == "space":
        sun("Key", 5.0, (62, 0, 215), (1.0, 0.97, 0.92))
        sun("Fill", 0.35, (110, 0, 40), (0.6, 0.7, 1.0))
    else:
        sun("Key", 3.6, (52, 0, 215), (1.0, 0.96, 0.90))
        sun("Fill", 1.1, (65, 0, 40), (0.80, 0.88, 1.0))
    if style in ("ground", "debris"):
        size = max(mx.x - mn.x, mx.y - mn.y) * 1.8 + 1.0
        ground_slab(pcoll, center.x, center.y, size, "#DAD5C8")
    cam_data = bpy.data.cameras.new("PreviewCam")
    cam_data.lens = 50
    cam_data.clip_end = 5000
    cam = bpy.data.objects.new("PreviewCam", cam_data)
    pcoll.objects.link(cam)
    scene.camera = cam
    corners = [Vector((x, y, z)) for x in (mn.x, mx.x) for y in (mn.y, mx.y) for z in (mn.z, mx.z)]
    frame_camera(cam, corners, center, az, el, cam_data.lens, res, margin=0.88)
    scene.render.resolution_x, scene.render.resolution_y = res
    scene.render.resolution_percentage = 100
    scene.render.filepath = path
    bpy.ops.render.render(write_still=True)




# ==========================================================================
# CATEGORY A - ANIMALS (8)       front = +Y in build space (-Z in the OBJ)
# ==========================================================================

def lr(b, key, fn, mat, pivot, parent="root", **kw):
    """Add key_L (+X side) and key_R (mirrored) from one builder function fn(bm) that models the +X side."""
    pl = parent + "_L" if (parent + "_L") in b.objs else parent
    pr = parent + "_R" if (parent + "_R") in b.objs else parent
    b.add(key + "_L", [fn], mat, pivot=pivot, parent=pl, **kw)
    b.add(key + "_R", [fn], mat, pivot=(-pivot[0], pivot[1], pivot[2]), parent=pr, mirror=True, **kw)


def feather(bm, base, tip, hw, thick=0.004, bow=0.0, up=(0, 0, 1)):
    base, tip = Vector(base), Vector(tip)
    mid = (base + tip) / 2 + Vector((0, 0, bow))
    blade(bm, [base, mid, tip], [hw * 0.85, hw, hw * 0.3], [thick, thick * 1.2, thick * 0.5], up=up)


def bird_wing(b, side, S, span, chord, sweep, dih, droop, prim_n, sec_n, m, s=1.0):
    """Layered wing: Arm (coverts) + Coverts layer + Secondaries + Primaries (+ dark Tip feathers)."""
    S = Vector(S)
    rise = span * math.tan(math.radians(dih))
    sx = 1.0 if side == "L" else -1.0

    def P(t):
        return Vector((S.x + span * t, S.y - sweep * span * (t ** 1.7), S.z + rise * t - droop * span * t * t))

    def c(t):
        return 1.0 - 0.22 * min(t, 0.5) / 0.5

    def arm(bm):
        ts = [0.0, 0.14, 0.28, 0.42, 0.5]
        pts = [P(t) + Vector((0, -chord * 0.5 * c(t), 0)) for t in ts]
        blade(bm, pts, [chord * 0.5 * c(t) for t in ts], [0.016 * s, 0.015 * s, 0.013 * s, 0.011 * s, 0.009 * s])

    def coverts(bm):
        ts = [0.04, 0.16, 0.28, 0.40]
        pts = [P(t) + Vector((0, -chord * (0.52 * c(t) + 0.02), 0.012 * s)) for t in ts]
        blade(bm, pts, [chord * 0.20] * 4, [0.006 * s] * 4)

    def secondaries(bm):
        for i in range(sec_n):
            t = 0.03 + 0.42 * i / max(1, sec_n - 1)
            base = P(t) + Vector((0, -chord * 0.80 * c(t), -0.006 * s))
            tip = base + Vector((0.03 * span * 0.3, -chord * 0.70, -0.01 * s))
            feather(bm, base, tip, span * 0.036, 0.004 * s, bow=-0.004 * s)

    def prim(lo, hi):
        def f(bm):
            for i in range(lo, hi):
                fr = i / max(1, prim_n - 1)
                base = P(0.40 + 0.06 * fr) + Vector((0, -chord * 0.45, -0.004 * s))
                tip = P(1.0 - 0.28 * fr ** 1.2) + Vector((0, -chord * (0.05 + 0.85 * fr), -0.006 * s - 0.012 * span * fr))
                feather(bm, base, tip, span * 0.034, 0.004 * s, bow=0.006 * s * (1 - fr))
        return f

    shoulder_pivot = (sx * S.x, S.y, S.z)
    key = f"Wing_{side}"
    b.add(key + "_Arm", [arm], m["arm"], pivot=shoulder_pivot, parent="Body", mirror=(sx < 0))
    b.add(key + "_Coverts", [coverts], m["cov"], pivot=shoulder_pivot, parent=key + "_Arm", mirror=(sx < 0))
    b.add(key + "_Secondaries", [secondaries], m["sec"], pivot=shoulder_pivot, parent=key + "_Arm", mirror=(sx < 0))
    n_tip = 2 if m.get("tip") else 0
    b.add(key + "_Primaries", [prim(n_tip, prim_n)], m["prim"], pivot=shoulder_pivot, parent=key + "_Arm", mirror=(sx < 0))
    if n_tip:
        b.add(key + "_Tips", [prim(0, n_tip)], m["tip"], pivot=shoulder_pivot, parent=key + "_Arm", mirror=(sx < 0))


def bird_build(b, P):
    s = P["s"]
    L, bw, bh, z0 = P["L"], P["bw"], P["bh"], P["z0"]
    mb = P["m"]
    st = [(-0.50, .16, .18, .02), (-0.32, .56, .58, .0), (-0.08, .96, .94, -.01), (.16, 1.0, 1.0, .0),
          (.36, .82, .90, .02), (.50, .46, .60, .04)]
    rings = [(L * y, 0, z0 + bh * dz, bw * w, bh * h) for (y, w, h, dz) in st]
    belly = P.get("belly")
    b.add("Body", [dict(rings=rings, axis="y", n=10)], [mb["body"], belly] if belly else mb["body"],
          face_mat=(lambda f: 1 if f.calc_center_median().z < z0 - bh * 0.30 else 0) if belly else None)

    hz = z0 + bh * P["neck_rise"]
    hy = L * P["head_y"]
    neck_pts = bez((0, L * 0.34, z0 + bh * 0.25), (0, L * 0.44, z0 + bh * 0.55), (0, hy - L * 0.04, hz - P["hr"] * 0.4), 6)
    b.add("Neck", [lambda bm: tube(bm, neck_pts, [bw * 0.80, bw * 0.62, P["hr"] * 0.85, P["hr"] * 0.8, P["hr"] * 0.78, P["hr"] * 0.75], n=8)],
          mb.get("neck", mb["body"]), parent="Body")
    b.add("Head", [lambda bm: ico(bm, (0, hy, hz), P["hr"], 1, (0.92, 1.12, 0.95))], mb.get("head", mb["body"]), pivot=(0, hy, hz),
          parent="Neck", smooth=False)
    hr = P["hr"]
    # beak ----------------------------------------------------------------
    bl, bd = P["beak_len"], P["beak_d"]
    by0 = hy + hr * 0.78
    hook = P.get("hook", 0.0)
    brings = [(by0, 0, hz - hr * 0.10, bd * 0.95, bd * 0.85), (by0 + bl * 0.45, 0, hz - hr * 0.12, bd * 0.7, bd * 0.62),
              (by0 + bl * 0.85, 0, hz - hr * 0.12 - hook * 0.4, bd * 0.34, bd * 0.40),
              (by0 + bl, 0, hz - hr * 0.12 - hook, bd * 0.12, bd * 0.16)]
    b.add("Beak", [dict(rings=brings, axis="y", n=6)], mb["beak"], pivot=(0, hy, hz), parent="Head", bevel=0.0)
    if P.get("cere"):
        b.add("Cere", [lambda bm: box(bm, -bd * 0.8, bd * 0.8, by0 + bl * 0.08, by0 + bl * 0.28, hz + hr * 0.02, hz + hr * 0.2)],
              P["cere"], pivot=(0, hy, hz), parent="Head")
    if P.get("gonys"):
        b.add("Beak_Spot", [lambda bm: box(bm, -bd * 0.2, bd * 0.2, by0 + bl * 0.55, by0 + bl * 0.78, hz - hr * 0.5, hz - hr * 0.3)],
              P["gonys"], pivot=(0, hy, hz), parent="Head")
    eye_m = P["eye"]
    lr(b, "Eye", lambda bm: ico(bm, (hr * 0.78, hy + hr * 0.30, hz + hr * 0.22), hr * 0.20, 1), eye_m,
       pivot=(hr * 0.78, hy + hr * 0.30, hz + hr * 0.22), parent="Head")
    if P.get("brow"):
        lr(b, "Brow", lambda bm: box(bm, hr * 0.55, hr * 0.98, hy + hr * 0.1, hy + hr * 0.62, hz + hr * 0.42, hz + hr * 0.52),
           P["brow"], pivot=(hr * 0.75, hy + hr * 0.3, hz + hr * 0.45), parent="Head")
    if P.get("neck_patch"):
        b.add("Neck_Patch", [dict(rings=[(hy - L * 0.10, 0, hz - hr * 1.1, hr * 0.95, hr * 0.9),
                                         (hy - L * 0.02, 0, hz - hr * 0.8, hr * 1.0, hr * 0.95)], axis="y", n=8)],
              P["neck_patch"], pivot=(0, hy, hz), parent="Neck")

    # tail ---------------------------------------------------------------
    tl, tn = P["tail_len"], P["tail_n"]

    def tail(bm):
        for i in range(tn):
            a = (i - (tn - 1) / 2) * P["tail_spread"]
            base = Vector((0, -L * 0.46, z0 + bh * 0.10))
            tip = base + Vector((math.sin(a) * tl, -math.cos(a) * tl, -0.012 * s + 0.01 * s * (i % 2)))
            feather(bm, base, tip, P["tail_w"], 0.004 * s)
    b.add("Tail", [tail], mb["tail"], pivot=(0, -L * 0.46, z0 + bh * 0.10), parent="Body")
    if P.get("tail_tip"):
        b.add("Tail_Band", [lambda bm: [feather(bm, Vector((0, -L * 0.46, z0 + bh * .1)) + Vector((math.sin(a) * tl * 0.72, -math.cos(a) * tl * 0.72, -0.012 * s)),
                                                Vector((0, -L * 0.46, z0 + bh * .1)) + Vector((math.sin(a) * tl, -math.cos(a) * tl, -0.012 * s)),
                                                P["tail_w"] * 0.9, 0.0045 * s)
                                        for a in [(i - (tn - 1) / 2) * P["tail_spread"] for i in range(tn)]]],
              P["tail_tip"], pivot=(0, -L * 0.46, z0 + bh * 0.10), parent="Tail")

    # wings --------------------------------------------------------------
    W = P["wing"]
    for side in ("L", "R"):
        bird_wing(b, side, (bw * 0.78, L * 0.14, z0 + bh * 0.55), W["span"], W["chord"], W["sweep"], W["dih"], W["droop"],
                  W["prim"], W["sec"], W["m"], s)

    # legs ---------------------------------------------------------------
    leg = P["legs"]
    lm, fm = leg["m"], leg["foot_m"]
    ly = L * 0.02
    lx = bw * 0.45
    if leg["mode"] == "stand":
        ankle_z = leg["h"] * 0.28

        def legf(bm):
            tube(bm, [(lx, ly, z0 - bh * 0.55), (lx, ly - 0.01 * s, ankle_z * 1.5), (lx, ly - 0.005 * s, ankle_z)], [0.012 * s, 0.009 * s, 0.008 * s], n=5)

        def footf(bm):
            for ang in (-30, 0, 30):
                a = math.radians(ang)
                tip = Vector((lx + math.sin(a) * 0.035 * s, ly + math.cos(a) * 0.045 * s * 1.2, 0.004 * s))
                beam(bm, (lx, ly - 0.004 * s, ankle_z * 0.6), tip, 0.007 * s, 0.006 * s, 0.006 * s, 0.004 * s)
            beam(bm, (lx, ly - 0.004 * s, ankle_z * 0.6), (lx, ly - 0.035 * s, 0.004 * s), 0.007 * s, 0.006 * s, 0.006 * s, 0.004 * s)
        lr(b, "Leg", legf, lm, pivot=(lx, ly, z0 - bh * 0.5), parent="Body")
        lr(b, "Foot", footf, fm, pivot=(lx, ly, ankle_z), parent="Leg")
    elif leg["mode"] == "tuck":
        def legf(bm):
            tube(bm, [(lx, ly, z0 - bh * 0.7), (lx, ly - 0.07 * s, z0 - bh * 1.0), (lx, ly - 0.17 * s, z0 - bh * 0.95)], [0.012 * s, 0.009 * s, 0.008 * s], n=5)

        def footf(bm):
            for ang in (-20, 0, 20):
                a = math.radians(ang)
                beam(bm, (lx, ly - 0.17 * s, z0 - bh * 0.95), (lx + math.sin(a) * 0.03 * s, ly - 0.17 * s - 0.045 * s, z0 - bh * 0.95 - 0.004 * s), 0.006 * s, 0.005 * s, 0.005 * s, 0.003 * s)
        lr(b, "Leg", legf, lm, pivot=(lx, ly, z0 - bh * 0.6), parent="Body")
        lr(b, "Foot", footf, fm, pivot=(lx, ly - 0.17 * s, z0 - bh * 0.95), parent="Leg")
    else:  # talons: legs hang forward with spread claws (raptor)
        def legf(bm):
            tube(bm, [(lx, ly, z0 - bh * 0.5), (lx, ly + 0.05 * s, z0 - bh * 1.5), (lx, ly + 0.12 * s, z0 - bh * 2.1)], [0.030 * s, 0.022 * s, 0.020 * s], n=6)

        def footf(bm):
            base = Vector((lx, ly + 0.12 * s, z0 - bh * 2.1))
            for ang, ln in ((-28, .09), (-8, .11), (10, .11), (30, .09)):
                a = math.radians(ang)
                p1 = base + Vector((math.sin(a) * ln * s * 1.0, math.cos(a) * ln * s * 0.8, -0.03 * s))
                p2 = p1 + Vector((math.sin(a) * 0.02 * s, math.cos(a) * 0.02 * s, -0.045 * s))
                tube(bm, [base, p1, p2], [0.010 * s, 0.009 * s, 0.003 * s], n=5)
        lr(b, "Leg", legf, lm, pivot=(lx, ly, z0 - bh * 0.5), parent="Body")
        lr(b, "Talons", footf, fm, pivot=(lx, ly + 0.12 * s, z0 - bh * 2.1), parent="Leg")


# ---------------------------------------------------------------- the birds
@asset("ANIMAL_01", "Pigeon", "animals", pose="standing, wings half-open (take-off display)",
       notes={"wingspan_m": 0.62, "named_groups": "Body, Neck, Head, Beak, Wing_L/R_{Arm,Coverts,Secondaries,Primaries}, Tail, Leg_L/R, Foot_L/R"})
def pigeon(b):
    s = 1.0
    P = dict(s=s, L=0.30, bw=0.062, bh=0.062, z0=0.125, neck_rise=0.9, head_y=0.50, hr=0.034, beak_len=0.030, beak_d=0.010,
             hook=0.004, cere=None, eye="eye_orange", tail_len=0.13, tail_n=5, tail_spread=0.10, tail_w=0.020,
             m=dict(body="pigeon_grey", head="pigeon_grey", neck="pigeon_grey", beak="beak_dark", tail="pigeon_dark"),
             belly="pigeon_grey", neck_patch="pigeon_neck", cere_m=None,
             wing=dict(span=0.30, chord=0.10, sweep=0.55, dih=22, droop=0.10, prim=7, sec=6,
                       m=dict(arm="pigeon_grey", cov="pigeon_dark", sec="pigeon_dark", prim="pigeon_dark")),
             legs=dict(mode="stand", h=0.10, m="pigeon_pink", foot_m="pigeon_pink"))
    P["cere"] = "offwhite"
    bird_build(b, P)


@asset("ANIMAL_02", "Seagull", "animals", style="air", pose="gliding flight, wings fully spread",
       notes={"wingspan_m": 1.28, "origin": "centre of body"})
def seagull(b):
    s = 1.6
    P = dict(s=s, L=0.46, bw=0.066, bh=0.066, z0=0.0, neck_rise=0.75, head_y=0.52, hr=0.040, beak_len=0.075, beak_d=0.014,
             hook=0.012, cere=None, gonys="gull_red", eye="eye_dark", tail_len=0.15, tail_n=5, tail_spread=0.07, tail_w=0.028,
             m=dict(body="white", head="white", neck="white", beak="beak_yellow", tail="white"), belly="white",
             wing=dict(span=0.62, chord=0.12, sweep=0.35, dih=6, droop=0.08, prim=8, sec=8,
                       m=dict(arm="white", cov="gull_grey", sec="gull_grey", prim="gull_grey", tip="crow_black")),
             legs=dict(mode="tuck", m="beak_yellow", foot_m="beak_yellow"))
    bird_build(b, P)


@asset("ANIMAL_03", "Crow", "animals", pose="standing, wings half-open",
       notes={"wingspan_m": 0.95})
def crow(b):
    s = 1.45
    P = dict(s=s, L=0.44, bw=0.072, bh=0.072, z0=0.215, neck_rise=0.95, head_y=0.52, hr=0.044, beak_len=0.075, beak_d=0.024,
             hook=0.007, cere=None, eye="eye_dark", tail_len=0.20, tail_n=6, tail_spread=0.085, tail_w=0.024,
             m=dict(body="crow_black", head="crow_black", neck="crow_sheen", beak="rubber", tail="crow_black"), belly="crow_sheen",
             wing=dict(span=0.46, chord=0.14, sweep=0.60, dih=20, droop=0.11, prim=7, sec=7,
                       m=dict(arm="crow_black", cov="crow_sheen", sec="crow_black", prim="crow_black")),
             legs=dict(mode="stand", h=0.16, m="rubber", foot_m="rubber"))
    bird_build(b, P)


@asset("ANIMAL_04", "Eagle", "animals", style="air", pose="soaring flight, talons extended, wings fully spread",
       notes={"wingspan_m": 2.25, "origin": "centre of body"})
def eagle(b):
    s = 2.8
    P = dict(s=s, L=0.86, bw=0.115, bh=0.115, z0=0.0, neck_rise=0.70, head_y=0.54, hr=0.066, beak_len=0.095, beak_d=0.034,
             hook=0.030, cere="beak_yellow", eye="beak_yellow", brow="eagle_white", tail_len=0.34, tail_n=6, tail_spread=0.08, tail_w=0.044,
             m=dict(body="eagle_brown", head="eagle_white", neck="eagle_white", beak="beak_yellow", tail="eagle_white"), belly="eagle_light",
             wing=dict(span=1.0, chord=0.28, sweep=0.30, dih=8, droop=0.10, prim=9, sec=9,
                       m=dict(arm="eagle_brown", cov="eagle_light", sec="eagle_brown", prim="eagle_brown", tip="rubber")),
             legs=dict(mode="talons", m="beak_yellow", foot_m="talon"))
    bird_build(b, P)




# ---------------------------------------------------------------- mammals
def limb_fn(pts, radii, n=6):
    return lambda bm: tube(bm, pts, radii, n=n)


def hoof_fn(x, y, z1, hw0, hd0, hw1, hd1):
    return lambda bm: frustum(bm, 0.0, z1, x, y, hw0, hd0, hw1, hd1)


@asset("ANIMAL_05", "Dog", "animals", pose="standing, tail raised",
       notes={"named_groups": "Body, Neck, Head, Muzzle, Ear_L/R, Leg_Front/Rear_L/R, Paw_*, Tail"})
def dog(b):
    body = [(-.36, 0, .50, .075, .11), (-.28, 0, .50, .108, .145), (-.10, 0, .48, .105, .14), (.08, 0, .49, .12, .165),
            (.22, 0, .49, .135, .19), (.33, 0, .51, .12, .17), (.40, 0, .53, .085, .12)]
    b.add("Body", [dict(rings=body, axis="y", n=10)], ["dog_tan", "dog_light"],
          face_mat=lambda f: 1 if f.calc_center_median().z < .40 and f.calc_center_median().y > .05 else 0)
    b.add("Neck", [lambda bm: tube(bm, [(0, .30, .52), (0, .42, .62), (0, .49, .69)], [.092, .075, .062], n=8)], "dog_tan", parent="Body")
    hp = (0, .52, .72)
    b.add("Head", [lambda bm: ico(bm, hp, .072, 1, (.92, 1.05, .95))], "dog_tan", pivot=hp, parent="Neck")
    b.add("Muzzle", [dict(rings=[(.545, 0, .700, .048, .042), (.615, 0, .695, .040, .036), (.680, 0, .690, .031, .029)], axis="y", n=8)],
          "dog_light", pivot=hp, parent="Head", bevel=0.002)
    b.add("Nose", [lambda bm: box(bm, -.020, .020, .675, .692, .688, .712)], "rubber", pivot=hp, parent="Head", bevel=0.002)
    b.add("Jaw", [dict(rings=[(.54, 0, .665, .036, .022), (.60, 0, .662, .030, .018), (.655, 0, .660, .024, .015)], axis="y", n=6)],
          "dog_light", pivot=hp, parent="Head")
    lr(b, "Ear", lambda bm: blade(bm, [(.055, .50, .78), (.082, .49, .73), (.100, .475, .64)], [.020, .036, .030], .006, up=(1, 0, 0)),
       "dog_dark", pivot=(.055, .50, .78), parent="Head")
    lr(b, "Eye", lambda bm: ico(bm, (.040, .578, .745), .011, 1), "eye_dark", pivot=(.04, .578, .745), parent="Head")
    lr(b, "Brow", lambda bm: box(bm, .028, .056, .57, .60, .757, .766), "dog_dark", pivot=(.04, .58, .76), parent="Head")
    # legs
    fl = [(.085, .25, .38), (.085, .245, .22), (.085, .265, .10), (.085, .275, .04)]
    rl = [(.095, -.30, .41), (.095, -.20, .26), (.095, -.31, .15), (.095, -.29, .04)]
    lr(b, "Leg_Front", limb_fn(fl, [.052, .040, .028, .025]), "dog_tan", pivot=fl[0], parent="Body")
    lr(b, "Leg_Rear", limb_fn(rl, [.072, .048, .030, .026]), "dog_tan", pivot=rl[0], parent="Body")
    lr(b, "Paw_Front", hoof_fn(.085, .285, .042, .030, .050, .027, .042), "dog_light", pivot=(.085, .275, .04), parent="Leg_Front", bevel=0.003)
    lr(b, "Paw_Rear", hoof_fn(.095, -.275, .042, .030, .050, .027, .042), "dog_light", pivot=(.095, -.29, .04), parent="Leg_Rear", bevel=0.003)
    tp = bez((0, -.35, .53), (0, -.52, .55), (0, -.50, .74), 7)
    b.add("Tail", [lambda bm: tube(bm, tp, [.032, .028, .025, .022, .019, .015, .010], n=6)], "dog_tan", pivot=tp[0], parent="Body")
    b.add("Tail_Tip", [lambda bm: tube(bm, tp[4:], [.021, .019, .015, .010], n=6)], "dog_light", pivot=tp[0], parent="Tail")
    b.add("Collar", [lambda bm: tube(bm, [(0, .385, .573), (0, .405, .595)], [(.085, .075), (.082, .072)], n=10)], "coral", parent="Neck")


@asset("ANIMAL_06", "Cat", "animals", pose="standing, tail curved up",
       notes={"named_groups": "Body, Head, Ear_L/R, Leg_*_L/R, Tail, Tail_Stripes, Whiskers"})
def cat(b):
    body = [(-.22, 0, .285, .052, .078), (-.14, 0, .29, .072, .098), (0, 0, .285, .076, .092), (.12, 0, .29, .082, .102),
            (.22, 0, .305, .072, .092), (.27, 0, .315, .050, .070)]

    def stripes(f):
        c = f.calc_center_median()
        return 1 if (int(math.floor((c.y + .22) / .035)) % 2 == 0 and c.z > .27) else 0
    b.add("Body", [dict(rings=body, axis="y", n=10)], ["cat_grey", "cat_stripe"], face_mat=stripes)
    hp = (0, .335, .365)
    b.add("Neck", [lambda bm: tube(bm, [(0, .22, .31), (0, .29, .34), (0, .325, .355)], [.055, .046, .042], n=8)], "cat_grey", parent="Body")
    b.add("Head", [lambda bm: ico(bm, hp, .062, 1, (1.10, .95, .95))], "cat_grey", pivot=hp, parent="Neck")
    b.add("Muzzle", [lambda bm: ico(bm, (0, .385, .345), .028, 1, (1.1, 1.0, .8))], "offwhite", pivot=hp, parent="Head")
    b.add("Nose", [lambda bm: box(bm, -.007, .007, .405, .413, .347, .357)], "pink_nose", pivot=hp, parent="Head")
    lr(b, "Ear", lambda bm: loft(bm, [(.405, .044, .325, .024, .012), (.462, .056, .322, .003, .003)], n=3), "cat_grey",
       pivot=(.044, .325, .405), parent="Head")
    lr(b, "Ear_Inner", lambda bm: loft(bm, [(.408, .044, .334, .015, .006), (.446, .053, .333, .003, .003)], n=3), "pink_nose",
       pivot=(.044, .33, .408), parent="Head")
    lr(b, "Eye", lambda bm: ico(bm, (.032, .383, .383), .0115, 1, (1.0, .6, 1.0)), "plant_green", pivot=(.032, .383, .383), parent="Head")

    def whisk(bm):
        for dz, dy in ((.012, .012), (.0, .0), (-.012, -.006)):
            beam(bm, (.03, .39 + dy * 0, .345 + dz * .3), (.115, .395 + dy, .345 + dz * 2.2), .0025, .0025)
    lr(b, "Whiskers", whisk, "white", pivot=(.03, .39, .345), parent="Head")
    fl = [(.045, .17, .245), (.045, .165, .13), (.045, .18, .035)]
    rl = [(.05, -.17, .26), (.055, -.10, .15), (.055, -.18, .095), (.055, -.16, .03)]
    lr(b, "Leg_Front", limb_fn(fl, [.032, .021, .018], 6), "cat_grey", pivot=fl[0], parent="Body")
    lr(b, "Leg_Rear", limb_fn(rl, [.046, .028, .019, .017], 6), "cat_grey", pivot=rl[0], parent="Body")
    lr(b, "Paw_Front", hoof_fn(.045, .192, .028, .021, .035, .019, .028), "offwhite", pivot=(.045, .18, .035), parent="Leg_Front", bevel=0.002)
    lr(b, "Paw_Rear", hoof_fn(.055, -.145, .028, .021, .035, .019, .028), "offwhite", pivot=(.055, -.16, .03), parent="Leg_Rear", bevel=0.002)
    tp = bez((0, -.21, .31), (0, -.40, .22), (0, -.45, .44), 10, p3=(0, -.34, .58))
    rad = [.020, .019, .018, .018, .017, .016, .015, .014, .013, .011]
    b.add("Tail", [lambda bm: tube(bm, tp, rad, n=6)], "cat_grey", pivot=tp[0], parent="Body")
    b.add("Tail_Stripes", [lambda bm: [tube(bm, tp[k:k + 2], [rad[k] + .003, rad[k + 1] + .003], n=6) for k in range(1, 9, 2)]],
          "cat_stripe", pivot=tp[0], parent="Tail")


@asset("ANIMAL_07", "Deer", "animals", pose="standing alert, antlered stag variant",
       notes={"variant": "stag with antlers (Antlers_L/R are separate parts, delete them for a doe)"})
def deer(b):
    body = [(-.46, 0, .88, .10, .16), (-.34, 0, .90, .14, .20), (-.10, 0, .86, .13, .18), (.14, 0, .88, .14, .20),
            (.30, 0, .90, .125, .19), (.40, 0, .93, .09, .15)]
    b.add("Body", [dict(rings=body, axis="y", n=10)], ["deer_brown", "deer_belly"],
          face_mat=lambda f: 1 if f.calc_center_median().z < .80 else 0)
    b.add("Neck", [lambda bm: tube(bm, [(0, .32, .98), (0, .44, 1.14), (0, .52, 1.29)], [.105, .082, .062], n=8)], "deer_brown", parent="Body")
    hp = (0, .565, 1.36)
    b.add("Head", [lambda bm: ico(bm, hp, .062, 1, (.85, 1.15, .90))], "deer_brown", pivot=hp, parent="Neck")
    b.add("Muzzle", [dict(rings=[(.60, 0, 1.335, .042, .040), (.68, 0, 1.318, .035, .033), (.745, 0, 1.305, .029, .027)], axis="y", n=8)],
          "deer_belly", pivot=hp, parent="Head", bevel=0.002)
    b.add("Nose", [lambda bm: box(bm, -.020, .020, .738, .756, 1.298, 1.322)], "rubber", pivot=hp, parent="Head", bevel=0.002)
    lr(b, "Ear", lambda bm: blade(bm, [(.05, .525, 1.40), (.12, .505, 1.46), (.20, .495, 1.50)], [.020, .046, .018], .005, up=(0, 1, 0)),
       "deer_brown", pivot=(.05, .525, 1.40), parent="Head")
    lr(b, "Eye", lambda bm: ico(bm, (.047, .60, 1.385), .012, 1), "eye_dark", pivot=(.047, .6, 1.385), parent="Head")

    def antler(bm):
        tube(bm, [(.035, .54, 1.41), (.07, .50, 1.55), (.10, .46, 1.70), (.115, .50, 1.84)], [.017, .014, .011, .007], n=6)
        tube(bm, [(.07, .50, 1.55), (.16, .56, 1.65)], [.010, .005], n=5)
        tube(bm, [(.10, .46, 1.70), (.19, .44, 1.81)], [.010, .004], n=5)
        tube(bm, [(.10, .46, 1.70), (.08, .57, 1.80)], [.010, .004], n=5)
        tube(bm, [(.115, .50, 1.84), (.17, .50, 1.93)], [.007, .003], n=5)
    lr(b, "Antlers", antler, "antler", pivot=(.035, .54, 1.41), parent="Head")
    fl = [(.085, .26, .80), (.085, .29, .52), (.085, .27, .22), (.085, .275, .05)]
    rl = [(.09, -.36, .82), (.095, -.26, .60), (.095, -.40, .44), (.095, -.38, .16), (.095, -.38, .05)]
    lr(b, "Leg_Front", limb_fn(fl, [.052, .034, .024, .020]), "deer_brown", pivot=fl[0], parent="Body")
    lr(b, "Leg_Rear", limb_fn(rl, [.068, .042, .026, .020, .018]), "deer_brown", pivot=rl[0], parent="Body")
    lr(b, "Hoof_Front", hoof_fn(.085, .282, .07, .018, .034, .016, .028), "hoof", pivot=(.085, .275, .05), parent="Leg_Front", bevel=0.002)
    lr(b, "Hoof_Rear", hoof_fn(.095, -.372, .07, .018, .034, .016, .028), "hoof", pivot=(.095, -.38, .05), parent="Leg_Rear", bevel=0.002)
    b.add("Rump_Patch", [lambda bm: ico(bm, (0, -.40, .90), .095, 1, (.85, .55, 1.0))], "offwhite", pivot=(0, -.4, .9), parent="Body")
    b.add("Tail", [lambda bm: ico(bm, (0, -.52, .94), .042, 1, (.65, 1.25, 1.0))], "offwhite", pivot=(0, -.5, .94), parent="Body")


@asset("ANIMAL_08", "Cow", "animals", pose="standing",
       notes={"named_groups": "Body, Neck, Head, Muzzle, Horn_L/R, Ear_L/R, Leg_*_L/R, Hoof_*, Udder, Teats, Tail, Tail_Tuft"})
def cow(b):
    body = [(-.88, 0, 1.00, .17, .24), (-.70, 0, 1.02, .29, .36), (-.35, 0, .98, .30, .40), (0, 0, .96, .30, .42),
            (.35, 0, .97, .32, .44), (.62, 0, 1.00, .29, .40), (.80, 0, 1.02, .20, .30)]

    def spots(f):
        c = f.calc_center_median()
        return 1 if fbm(Vector((c.x * 2.2, c.y * 2.0, c.z * 2.2)) + Vector((3.1, 1.7, .4)), 2) > .10 else 0
    b.add("Body", [dict(rings=body, axis="y", n=12)], ["cow_white", "cow_black"], face_mat=spots)
    b.add("Neck", [lambda bm: tube(bm, [(0, .66, 1.10), (0, .86, 1.12), (0, 1.00, 1.05)], [.21, .17, .135], n=8)], "cow_white", parent="Body")
    hp = (0, 1.08, .98)
    b.add("Head", [lambda bm: ico(bm, hp, .14, 1, (.85, 1.22, .95))], "cow_white", pivot=hp, parent="Neck")
    b.add("Muzzle", [dict(rings=[(1.19, 0, .885, .105, .088), (1.27, 0, .875, .098, .082), (1.335, 0, .868, .088, .072)], axis="y", n=8)],
          "cow_pink", pivot=hp, parent="Head", bevel=0.003)
    b.add("Nostrils", [lambda bm: [box(bm, x - .018, x + .018, 1.335, 1.345, .870, .895) for x in (-.04, .04)]], "rubber", pivot=hp, parent="Head")
    lr(b, "Ear", lambda bm: blade(bm, [(.11, 1.00, 1.08), (.22, .99, 1.10), (.35, .98, 1.085)], [.03, .058, .028], .007), "cow_white",
       pivot=(.11, 1.0, 1.08), parent="Head")
    lr(b, "Horn", lambda bm: tube(bm, [(.09, 1.02, 1.14), (.15, 1.00, 1.25), (.12, 1.00, 1.35)], [.022, .015, .005], n=6), "stone",
       pivot=(.09, 1.02, 1.14), parent="Head")
    lr(b, "Eye", lambda bm: ico(bm, (.098, 1.14, 1.04), .016, 1), "eye_dark", pivot=(.098, 1.14, 1.04), parent="Head")
    fl = [(.17, .55, .60), (.17, .55, .34), (.17, .56, .12)]
    rl = [(.18, -.62, .64), (.17, -.55, .38), (.17, -.67, .25), (.17, -.65, .10)]
    lr(b, "Leg_Front", limb_fn(fl, [.092, .062, .046], 7), "cow_white", pivot=fl[0], parent="Body")
    lr(b, "Leg_Rear", limb_fn(rl, [.115, .074, .052, .046], 7), "cow_white", pivot=rl[0], parent="Body")
    lr(b, "Hoof_Front", hoof_fn(.17, .566, .12, .056, .070, .048, .060), "hoof", pivot=(.17, .56, .12), parent="Leg_Front", bevel=0.004)
    lr(b, "Hoof_Rear", hoof_fn(.17, -.655, .12, .056, .070, .048, .060), "hoof", pivot=(.17, -.65, .12), parent="Leg_Rear", bevel=0.004)
    b.add("Udder", [lambda bm: ico(bm, (0, -.42, .58), .12, 1, (.95, 1.15, .75))], "cow_pink", pivot=(0, -.42, .58), parent="Body")
    b.add("Teats", [lambda bm: [cyl(bm, (x, y, .52), (x, y, .42), .015, .011, n=6) for x in (-.05, .05) for y in (-.37, -.47)]],
          "cow_pink", pivot=(0, -.42, .55), parent="Udder")
    tp = [(0, -.88, 1.28), (0, -.95, 1.05), (0, -.97, .72), (0, -.95, .40)]
    b.add("Tail", [lambda bm: tube(bm, tp, [.032, .024, .017, .013], n=6)], "cow_white", pivot=tp[0], parent="Body")
    b.add("Tail_Tuft", [lambda bm: ico(bm, (0, -.95, .33), .06, 1, (.7, .7, 1.5))], "cow_black", pivot=tp[0], parent="Tail")




# ==========================================================================
# CATEGORY B - DISASTER OBJECTS (14)
# ==========================================================================
def C(x, y, z):
    return Vector((x, y, z)).normalized()


@asset("DISASTER_01", "Atmospheric Impact Asteroid", "disaster", pose="resting; scorched leading face toward +Y (-Z in file)",
       notes={"size_note": "~4.8 m long impactor; asymmetric lobes, scorched ablation face, ember hot-spots"})
def impactor(b):
    craters = [(C(.3, .6, .7), .45, .10, .04), (C(-.7, .2, .4), .35, .08, .03), (C(.1, -.7, .3), .30, .07, .03), (C(.8, -.3, -.2), .28, .06, .02)]

    def shape(bm):
        blob(bm, (0, 0, 0), (2.1, 1.6, 1.5), sub=3, seed=3.1, rough=.40, freq=1.1, craters=craters)
        blob(bm, (1.55, .5, .45), (1.0, .85, .75), sub=2, seed=7.7, rough=.32)
        blob(bm, (-1.35, -.6, -.15), (1.05, .75, .85), sub=2, seed=11.3, rough=.34)
        blob(bm, (.2, 1.0, -.5), (.75, .6, .5), sub=2, seed=2.2, rough=.3)

    def mat(f):
        c = f.calc_center_median()
        if fbm(c * 2.4 + Vector((5, 1, 3)), 2) > .42:
            return 2
        return 1 if (c.y > .15 + .5 * fbm(c * 1.2, 2)) else 0
    b.add("Body", [shape], ["rock_dark", "rock_char", "ember"], face_mat=mat)
    b.place(rot=(8, 12, 25))


@asset("DISASTER_02", "Meteor Fragment", "disaster", pose="resting",
       notes={"materials": "slot0 fusion crust, slot1 fractured interior"})
def meteor_fragment(b):
    pits = [(C(*d), r, .05, .0) for d, r in (((.5, .5, .7), .35), ((-.6, .3, .5), .3), ((.1, -.8, .3), .32), ((.7, -.2, -.1), .26), ((-.2, .9, .1), .28), ((-.5, -.5, .6), .24))]

    def shape(bm):
        blob(bm, (0, 0, 0), (.55, .40, .42), sub=3, seed=1.7, rough=.22, freq=1.3, craters=pits)
        facet(bm, (.55, .25, .80), .30)
        facet(bm, (-.80, .10, .20), .36)
        facet(bm, (.10, -.85, .15), .26)
    b.add("Fragment", [shape], ["crust_black", "meteor_core"])
    b.place(rot=(15, 5, 40))


@asset("DISASTER_03", "Lunar Fragment", "disaster", pose="resting",
       notes={"materials": "regolith surface, banded fractured interior (lunar_dark / lunar_fresh)"})
def lunar_fragment(b):
    cr = [(C(.1, .3, 1), .42, .08, .05), (C(-.6, .5, .7), .3, .06, .04), (C(.7, -.2, .6), .26, .05, .03), (C(-.2, -.8, .4), .33, .07, .04)]

    def shape(bm):
        blob(bm, (0, 0, 0), (.98, .72, .78), sub=3, seed=4.4, rough=.22, freq=1.2, craters=cr)
        cut(bm, (0, 0, -.42), (.15, -.20, -1), "neg", 1)       # flat underside so it rests
        facet(bm, (.85, .25, .20), .62)
        facet(bm, (-.20, -.90, .15), .50)
        for f in bm.faces:
            if f.material_index == 1:
                c = f.calc_center_median()
                f.material_index = 1 if int(math.floor(c.z * 9 + 20)) % 2 == 0 else 2
    b.add("Fragment", [shape], ["regolith", "lunar_dark", "lunar_fresh"])
    b.place(rot=(0, 0, 15))


@asset("DISASTER_04", "Fractured Rock", "disaster", pose="three matching sections, slightly separated",
       notes={"sections": "Section_A/B/C are cut from one rock along two planes; break faces match across gaps"})
def fractured_rock(b):
    n1, p1 = Vector((1, .35, .08)).normalized(), Vector((-.25, 0, 0))
    n2, p2 = Vector((-.15, 1, .25)).normalized(), Vector((.5, .1, 0))

    def piece(cuts, off):
        tmp = bmesh.new()
        blob(tmp, (0, 0, 0), (1.75, 1.25, 1.15), sub=3, seed=6.6, rough=.30, freq=1.1)
        for co, no, keep in cuts:
            cut(tmp, co, no, keep, 1)
        bmesh.ops.translate(tmp, verts=tmp.verts, vec=off)
        return tmp
    mats = ["rock_dark", "ash"]
    b.add("Section_A", [lambda bm: merge_bm(bm, piece([(p1, n1, "neg")], -n1 * .16 + Vector((0, 0, .04))))], mats)
    b.add("Section_B", [lambda bm: merge_bm(bm, piece([(p1, n1, "pos"), (p2, n2, "neg")], n1 * .06 - n2 * .10 + Vector((0, 0, .02))))], mats)
    b.add("Section_C", [lambda bm: merge_bm(bm, piece([(p1, n1, "pos"), (p2, n2, "pos")], n1 * .08 + n2 * .17 + Vector((0, 0, -.03))))], mats)
    b.place(rot=(0, 0, 10))


def facet(bm, n, d):
    """Shave a flat broken facet: remove everything beyond distance d from the centre along n."""
    n = Vector(n).normalized()
    cut(bm, n * d, n, "neg", 1)


def _fissure_noise(p, seed):
    return fbm(p * 3.0 + Vector((seed, seed * .7, seed * 1.3)), 2)


@asset("DISASTER_05", "Volcanic Bomb", "disaster", pose="resting",
       notes={"materials": "basalt crust, ember fissure bands recessed into the crust"})
def volcanic_bomb(b):
    def shape(bm):
        lathe(bm, [(0, -.42), (.07, -.38), (.17, -.26), (.25, -.08), (.27, .08), (.22, .24), (.12, .35), (.05, .41), (0, .45)], n=14)
        for v in bm.verts:
            p = v.co.copy()
            d = p.normalized() if p.length > 1e-6 else Vector((0, 0, 1))
            v.co = p + d * (fbm(p * 3.2, 2) * .035)
            ang = p.z * 1.1                      # twisted spindle ends
            x, y = v.co.x, v.co.y
            v.co.x = x * math.cos(ang) - y * math.sin(ang)
            v.co.y = x * math.sin(ang) + y * math.cos(ang)
            if abs(_fissure_noise(p, 2.0)) < .055:
                v.co *= .93
        rotate_bm(bm, bm.verts, "Y", 90)
    def mat(f):
        c = f.calc_center_median()
        q = Vector((-c.z, c.y, c.x))      # undo the 90 degree rotation for the noise lookup
        return 1 if abs(_fissure_noise(q, 2.0)) < .07 else 0
    b.add("Bomb", [shape], ["basalt", "ember"], face_mat=mat)
    b.place(rot=(0, 6, 20))


@asset("DISASTER_06", "Lava Rock", "disaster", pose="resting",
       notes={"materials": "basalt body, crust plates, recessed glowing cracks (emissive)"})
def lava_rock(b):
    def shape(bm):
        blob(bm, (0, 0, 0), (.55, .46, .38), sub=3, seed=9.1, rough=.42, freq=1.5, octaves=3)
        for v in bm.verts:
            if abs(fbm(v.co * 2.6, 2)) < .05:
                v.co *= .93
    def mat(f):
        c = f.calc_center_median()
        if abs(fbm(c * 2.6, 2)) < .06:
            return 2
        return 1 if fbm(c * 1.7 + Vector((4, 4, 1)), 2) > .12 else 0
    b.add("Rock", [shape], ["basalt", "crust_black", "lava_glow"], face_mat=mat)
    b.place(rot=(0, 0, 30))


@asset("DISASTER_07", "Lava Crust Piece", "disaster", pose="flat on ground",
       notes={"layers": "Slab (basalt), Crust_Plate, Rope_Ridges, Glow_Edge (emissive broken edge)"})
def lava_crust(b):
    rng = random.Random(14)
    outline = jag_outline(rng, 11, 1.15, .82, .30)

    def inset(o, k, rot=0):
        cx = sum(p[0] for p in o) / len(o)
        cy = sum(p[1] for p in o) / len(o)
        return [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in o]
    b.add("Slab", [lambda bm: gprism(bm, 0.0, .13, outline, inset(outline, .97))], "basalt", bevel=0.01)
    b.add("Crust_Plate", [lambda bm: gprism(bm, .125, .21, inset(outline, .88), inset(outline, .80))], "crust_black", bevel=0.008)
    b.add("Glow_Edge", [lambda bm: gprism(bm, 0.0, .045, inset(outline, 1.012), inset(outline, 1.0))], "lava_glow", parent="Slab")

    def ropes(bm):
        for k in range(6):
            r0 = .10 + .13 * k
            a0 = rng.uniform(-60, 20) + k * 14
            pts = [(r0 * 1.25 * math.cos(math.radians(a0 + a * 9)) + .05 * k - .15, r0 * .85 * math.sin(math.radians(a0 + a * 9)),
                    .205 + .018 * math.sin(a * 1.3)) for a in range(10)]
            tube(bm, pts, [.030 + .012 * math.sin(a * .8) for a in range(10)], n=5)
    b.add("Rope_Ridges", [ropes], "rock_dark", parent="Crust_Plate", bevel=0.0)
    b.place(rot=(0, 0, 0))


@asset("DISASTER_08", "Ground Fissure Module", "disaster", style="terrain", pose="terrain module 4 x 4 m, top surface at y=0",
       notes={"parts": "Plate_West, Plate_East, Chasm_Floor, Chasm_Rubble, Slab_Fallen (collapsed bridge section)"})
def ground_fissure(b):
    rng = random.Random(8)
    N = 14
    ys = [-2 + 4 * i / (N - 1) for i in range(N)]

    def gap(y):
        return .30 + .62 * math.sin(math.pi * (y + 2) / 4) ** 1.3 + .10 * fbm(Vector((y * 1.7, 0, 3)), 2)
    top, depth = 0.0, 1.5

    def plate(sign):
        def f(bm):
            inner = [(sign * (gap(y) + .09 * rng.uniform(-1, 1)), y) for y in ys]
            outline = [(sign * 2.0, ys[0])] + inner + [(sign * 2.0, ys[-1])]
            if sign < 0:
                outline = outline[::-1]
            gprism(bm, -depth, top, outline)
        return f

    def side_mat(f):
        c = f.calc_center_median()
        return 0 if c.z > top - .02 else 1
    b.add("Plate_West", [plate(-1)], ["soil", "rock_mid"], face_mat=side_mat, bevel=0.01)
    b.add("Plate_East", [plate(1)], ["soil", "rock_mid"], face_mat=side_mat, bevel=0.01)
    b.add("Chasm_Floor", [lambda bm: box(bm, -1.2, 1.2, -2.0, 2.0, -depth - .25, -depth + .01)], "rock_char")
    r2 = random.Random(5)
    b.add("Chasm_Rubble", [lambda bm: [blob(bm, (r2.uniform(-.35, .35), r2.uniform(-1.7, 1.7), -depth + .12), (.22 * r2.uniform(.7, 1.5), .2 * r2.uniform(.7, 1.4), .16),
                                            sub=1, seed=r2.uniform(0, 9), rough=.35) for _ in range(9)]], "rock_dark")

    def fallen(bm):
        pts = [(-.40, -.55), (.46, -.62), (.62, .10), (.18, .52), (-.50, .38)]
        gprism(bm, -.22, 0, pts)
        rotate_bm(bm, bm.verts, "X", 14, center=(0, 0, 0))
        rotate_bm(bm, bm.verts, "Y", -8, center=(0, 0, 0))
        bmesh.ops.translate(bm, verts=bm.verts, vec=(-.15, -.55, -.78))
    b.add("Slab_Fallen", [fallen], ["soil", "rock_mid"], face_mat=side_mat, bevel=0.01)
    b.place(drop=False)


@asset("DISASTER_09", "Impact Crater", "disaster", style="terrain", pose="terrain module 10 x 10 m, undisturbed ground at y=0",
       notes={"parts": "Terrain (bowl, raised irregular rim, ejecta ridges), Ejecta_Boulders", "crater_rim_radius_m": 3.6})
def impact_crater(b):
    R = 3.6

    def h(x, y):
        r = math.hypot(x, y)
        ang = math.atan2(y, x)
        Rr = R * (1 + .10 * fbm(Vector((math.cos(ang) * 1.4, math.sin(ang) * 1.4, 2.1)), 2))
        t = r / Rr
        z = 0.0
        if t < 1.0:
            z -= 1.9 * (1 - t * t) ** 1.15
        z += .62 * math.exp(-((t - 1.04) / .20) ** 2)
        z += .12 * math.exp(-((t - 1.55) / .35) ** 2) * (1 + fbm(Vector((x * .8, y * .8, 4)), 2))
        z += .10 * fbm(Vector((x * 1.1, y * 1.1, 7)), 3) * smoothstep(0.2, 1.0, t)
        return z

    def mat(f):
        c = f.calc_center_median()
        r = math.hypot(c.x, c.y)
        if c.z < -1.45:
            return 0
        if c.z < -.35:
            return 1
        if c.z > .25:
            return 2
        return 3
    b.add("Terrain", [lambda bm: terrain_slab(bm, 44, 44, 10.0, 10.0, h, -2.6)], ["dirt_dark", "soil", "rock_mid", "sand"], face_mat=mat)
    rr = random.Random(21)

    def boulders(bm):
        for k in range(16):
            a = rr.uniform(0, 6.283)
            rad = rr.uniform(R * .95, R * 1.35)
            x, y = math.cos(a) * rad, math.sin(a) * rad
            if abs(x) > 4.6 or abs(y) > 4.6:
                continue
            s = rr.uniform(.14, .42)
            blob(bm, (x, y, h(x, y) + s * .35), (s, s * rr.uniform(.7, 1.2), s * .75), sub=1, seed=rr.uniform(0, 20), rough=.4)
    b.add("Ejecta_Boulders", [boulders], "rock_dark")
    b.place(drop=False)




def placed(fn, ax, ang, off=(0, 0, 0), pivot=(0, 0, 0)):
    """Build with fn(bm), then rotate (about pivot) and translate only the newly created verts."""
    def run(bm):
        before = set(bm.verts)
        fn(bm)
        new = [v for v in bm.verts if v not in before]
        if ang:
            rotate_bm(bm, new, ax, ang, center=pivot)
        bmesh.ops.translate(bm, verts=new, vec=off)
    return run


def vlerp(a, b, t):
    return Vector(a).lerp(Vector(b), t)


def sstep(a, b, x):
    return smoothstep(a, b, x)


# ---------------------------------------------------------------------- DISASTER_10
@asset("DISASTER_10", "Uprooted Tree", "disaster", pose="fallen along +Y (-Z in file); root plate at the rear, snapped crown at the front",
       notes={"parts": "Trunk, Root_Plate (soil disc + clods), Roots, Branches, Foliage, Splinters (snapped crown end)"})
def uprooted_tree(b):
    rng = random.Random(10)
    y0, y1, N = -.9, 4.4, 14

    def rad(t):
        return .15 + .42 * (1 - t) ** .85

    cl, rr = [], []
    for i in range(N + 1):
        t = i / N
        cl.append(Vector((.22 * math.sin(t * 3.0), y0 + (y1 - y0) * t, rad(t) + .02 + .04 * math.sin(t * 6))))
        rr.append(rad(t))
    b.add("Trunk", [lambda bm: tube(bm, cl, rr, n=9)], "bark", bevel=0.0)

    def plate(bm):
        blob(bm, (0, -1.05, 1.0), (1.25, .27, 1.0), sub=2, seed=3.3, rough=.16, freq=1.6, flat=(0, 0, -1, .96))
        for k in range(7):
            a = rng.uniform(0, 6.283)
            rd = rng.uniform(.25, .85)
            blob(bm, (math.cos(a) * rd * 1.1, -1.28 - rng.uniform(0, .1), 1.0 + math.sin(a) * rd * .8),
                 (.2, .12, .17), sub=1, seed=rng.uniform(0, 9), rough=.35)

    def pmat(f):
        c = f.calc_center_median()
        return 1 if (c.y < -1.22 and fbm(c * 3, 2) > -.1) else 0
    b.add("Root_Plate", [plate], ["soil", "dirt_dark"], face_mat=pmat)

    def roots(bm):
        for k in range(11):
            a = 2 * math.pi * k / 11 + .2
            p0 = Vector((math.cos(a) * .85 * rng.uniform(.5, 1), -1.15, 1.0 + math.sin(a) * .8 * rng.uniform(.5, 1)))
            d = Vector((math.cos(a) * .55, -1, max(-.3, math.sin(a) * .4 - .15)))
            pts = [p0, p0 + d * .5, p0 + d * 1.0 + Vector((rng.uniform(-.2, .2), 0, rng.uniform(-.2, .1))),
                   p0 + d * 1.5 + Vector((rng.uniform(-.3, .3), 0, rng.uniform(-.3, .0)))]
            pts = [Vector((p.x, p.y, max(p.z, .05))) for p in pts]
            tube(bm, pts, [.15, .11, .07, .025], n=5)
    b.add("Roots", [roots], "root")

    br, fol = [], []
    def branches(bm):
        for i, t in enumerate((.20, .32, .44, .55, .66, .78, .88)):
            k = int(t * N)
            p = cl[k]
            side = 1 if i % 2 == 0 else -1
            d = Vector((side * .85, .45, .55 + .2 * rng.random())).normalized()
            L = 1.1 + 1.6 * (1 - t)
            pts = [p + d * (L * s) + Vector((0, 0, -.25 * s * s * 0)) for s in (0, .33, .66, 1.0)]
            pts[2].z += .15
            pts[3].z += .22
            r0 = .10 * (1 - t) + .045
            tube(bm, pts, [r0, r0 * .8, r0 * .55, r0 * .35], n=5)
            if i not in (1, 4):
                fol.append(pts[3])
    b.add("Branches", [branches], "bark")

    def foliage(bm):
        for i, c in enumerate(fol):
            s = .55 + .35 * rng.random()
            blob(bm, c + Vector((0, 0, s * .2)), (s, s * .95, s * .75), sub=1, seed=rng.uniform(0, 9), rough=.38, freq=1.7)
        for k in range(4):
            c = cl[N - 1 - k] + Vector((rng.uniform(-.2, .2), rng.uniform(-.1, .2), .3))
            blob(bm, c, (.5, .5, .4), sub=1, seed=rng.uniform(0, 9), rough=.38)

    def fmat(f):
        return 0 if fbm(f.calc_center_median() * 1.8 + Vector((3, 1, 2)), 2) > -.05 else 1
    b.add("Foliage", [foliage], ["foliage_mid", "foliage_deep"], face_mat=fmat)

    def splint(bm):
        e = cl[-1]
        for k in range(8):
            a = 2 * math.pi * k / 8
            r = rr[-1] * .85
            p0 = e + Vector((math.cos(a) * r, -.04, math.sin(a) * r * .9 - .0))
            L = rng.uniform(.25, .6)
            tip = p0 + Vector((math.cos(a) * rng.uniform(-.05, .08), L, math.sin(a) * rng.uniform(-.05, .08)))
            beam(bm, p0, tip, .07, .035, .008, .006, up=(0, 0, 1))
    b.add("Splinters", [splint], "bark_fresh", parent="Trunk")
    b.place(rot=(0, 0, 0))


# ---------------------------------------------------------------------- DISASTER_11
def _interp_profiles(keys, n):
    """keys: [(y, [(u,v)..])]; returns n stations linearly interpolated."""
    out = []
    ys = [k[0] for k in keys]
    for i in range(n):
        y = ys[0] + (ys[-1] - ys[0]) * i / (n - 1)
        for j in range(len(keys) - 1):
            if ys[j] <= y <= ys[j + 1]:
                t = (y - ys[j]) / max(1e-9, ys[j + 1] - ys[j])
                pts = [tuple(vlerp(a, c, t)) for a, c in zip(keys[j][1], keys[j + 1][1])]
                out.append((y, pts))
                break
    return out


@asset("DISASTER_11", "Overturned Vehicle Shell", "disaster",
       pose="car shell resting on its crushed roof; wheels up, front-right wheel and door torn off beside it",
       notes={"parts": "Body_Shell (modelled crush damage), Cabin_Roof (crushed), Pillars, Glass_Remnants, Hood (buckled), Door_FL, Door_FR_Detached, Bumpers, Underbody, Wheel_*",
              "note": "built as a damaged shell (crumpled roof, torn panels, exposed chassis), not a rotated intact car"})
def overturned_car(b):
    rng = random.Random(11)
    RP = rect_profile
    keys = [(-2.2, RP(.34, .70, .72, .68, .10, .08)), (-2.0, RP(.30, .88, .86, .82, .12, .10)),
            (-1.0, RP(.28, .97, .90, .85, .12, .12)), (1.0, RP(.28, .95, .90, .85, .12, .12)),
            (1.75, RP(.28, .84, .89, .82, .12, .10)), (2.2, RP(.32, .62, .78, .70, .12, .08))]
    stations = _interp_profiles(keys, 16)

    def dent(v):
        x, y, z = v.co
        # buckled flank + crushed front + sagging roof line (all in upright build space)
        dz = 0.0
        if z > .7:
            dz -= .13 * sstep(.2, 1.0, y) * (.5 + fbm(Vector((x * 2, y * 2, 1)), 2))
            dz -= .06 * sstep(-1.5, -.2, -y) * (1 + fbm(Vector((x * 2, y * 2, 4)), 2))
        v.co.z += dz
        if y > 1.7:
            v.co.y -= .17 * sstep(1.7, 2.2, y) * (.6 + fbm(Vector((x * 3, z * 3, 5)), 2))
        if x > .55 and -.7 < y < 1.2:
            v.co.x -= .10 * math.exp(-((y - .3) / .55) ** 2) * (.6 + fbm(Vector((z * 3, y * 3, 2)), 2))
        if x < -.55 and -1.4 < y < .0:
            v.co.x += .07 * math.exp(-((y + .7) / .5) ** 2)

    def body(bm):
        loft_pts(bm, stations, axis="y")
        for v in bm.verts:
            dent(v)

    def bmat(f):
        return 1 if f.calc_center_median().z < .42 else 0
    b.add("Body_Shell", [body], ["car_red", "car_dark"], face_mat=bmat, bevel=0.012)

    def roof(bm):
        def h(x, y):
            return 1.20 + .05 * fbm(Vector((x * 2, y * 2, 1)), 2) - .20 * math.exp(-((x - .3 - .3 * y) / .5) ** 2) * .9 - .06 * sstep(-.2, .7, y)
        terrain_slab(bm, 6, 8, 1.40, 1.50, h, 1.10)
        bmesh.ops.translate(bm, verts=bm.verts, vec=(0, -.15, 0))
    b.add("Cabin_Roof", [roof], "car_red", bevel=0.01)

    def pillars(bm):
        spec = [(.76, .85, -.05, .72, .42, .0), (-.76, .85, .0, -.70, .40, .0),   # A pillars
                (.80, -.15, .0, .68, -.1, -.0), (-.80, -.15, .0, -.62, -.05, .0),     # B
                (.78, -1.05, .0, .66, -.85, .0), (-.78, -1.05, .0, -.70, -.95, .0)]   # C
        for (x0, y0, _, x1, y1, __) in spec:
            top = Vector((x1 - .03 * rng.random(), y1, 1.17 + (.03 if x0 > 0 else -.02)))
            mid = Vector(((x0 + x1) / 2 + rng.uniform(-.05, .06), (y0 + y1) / 2, .98))
            tube(bm, [Vector((x0, y0, .93)), mid, top], [(.045, .03), (.035, .025), (.04, .03)], n=4)
    b.add("Pillars", [pillars], "car_red")

    def glass(bm):
        for (x, y) in ((.0, .62), (-.45, .6), (.50, -1.0), (-.5, -1.02)):
            p = [Vector((x - .18, y, .96)), Vector((x + .15, y + rng.uniform(-.04, .04), .96)), Vector((x + rng.uniform(-.1, .1), y + .1, 1.12))]
            solid(bm, p, [q + Vector((0, .012, 0)) for q in p])
    b.add("Glass_Remnants", [glass], "glass", parent="Cabin_Roof")

    def door_fn(side, ylo, yhi, z0=.34, crush=.08):
        def f(bm):
            sts = []
            for i in range(7):
                y = ylo + (yhi - ylo) * i / 6
                w = fbm(Vector((y * 3, side, 2)), 2)
                x = side * (.90 + crush * w)
                top = .98 - .06 * i / 6 + .05 * w
                sts.append((y, [(x - .035, z0 + .02 * w), (x + .035, z0 + .02 * w), (x + .035, top), (x - .035, top)]))
            loft_pts(bm, sts, axis="y")
        return f
    b.add("Door_FL", [door_fn(-1, -.3, .78, crush=.12)], "car_red", pivot=(-.9, -.3, .65), bevel=0.008)

    def door_flat(bm):
        door_fn(1, -.3, .78)(bm)
        new = list(bm.verts)
        rotate_bm(bm, new, "Y", 90, center=(.9, .24, .66))
        bmesh.ops.translate(bm, verts=new, vec=(1.25, 0, 1.17 - .66 - .005))
    b.add("Door_FR_Detached", [door_flat], "car_red", pivot=(2.2, .24, 1.1), bevel=0.008)

    def hood(bm):
        def h(x, y):
            return .02 * fbm(Vector((x * 3, y * 3, 3)), 2) + .06 * math.sin(y * 9 + x * 3) * (y / 1.2) - .1 * math.exp(-((x + .2) / .4) ** 2) * (y / 1.2) ** 2
        terrain_slab(bm, 8, 6, 1.6, 1.2, h, -.035)
        for v in bm.verts:
            v.co.y += .6
        rotate_bm(bm, bm.verts, "X", 24, center=(0, 0, 0))
        rotate_bm(bm, bm.verts, "Y", 7, center=(0, 0, 0))
        bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 1.02, .9))
    b.add("Hood", [hood], "car_red", pivot=(0, 1.02, .9), bevel=0.008)

    def bump(sign, droop):
        def f(bm):
            pts = [Vector((x, sign * (2.28 + .02 * abs(x)), .42 - droop * sstep(.1, 1.0, x))) for x in (-.9, -.45, 0, .45, .9)]
            tube(bm, pts, [(.07, .1)] * 5, n=6)
        return f
    b.add("Bumper_Front", [bump(1, .38)], "car_dark", pivot=(0, 2.3, .42))
    b.add("Bumper_Rear", [bump(-1, .0)], "car_dark", pivot=(0, -2.3, .42))

    def under(bm):
        for sx in (-.52, .52):
            beam(bm, (sx, -2.0, .17), (sx, 1.95, .17), .09, .12)
        for yy in (-1.5, -.2, 1.0):
            beam(bm, (-.55, yy, .2), (.55, yy, .2), .07, .06)
        for yy in (-1.37, 1.37):
            cyl(bm, (-.95, yy, .34), (.95, yy, .34), .035, n=8)
        cyl(bm, (.22, -2.0, .13), (.22, .6, .13), .045, n=7)
        cyl(bm, (.22, -1.9, .13), (.22, -1.15, .13), .12, n=9)
        cyl(bm, (0, -.9, .2), (0, 1.3, .2), .035, n=6)
        box(bm, -.3, .3, -1.95, -1.4, .09, .22)
    b.add("Underbody", [under], ["steel"])

    def wheel(cx, cy, cz, tilt=0):
        def f(bm):
            torus(bm, (0, 0, 0), .245, .098, n=18, m=8, axis="x", squash=1.0)
        return f

    def wheel_part(name, c, flat=False):
        def tire(bm):
            torus(bm, c, .245, .098, n=18, m=8, axis="x")
        def hub(bm):
            cyl(bm, (c[0] - .06, c[1], c[2]), (c[0] + .06, c[1], c[2]), .17, n=10)
        b.add(name, [with_mat(0, tire), with_mat(1, hub)], ["rubber", "steel"], pivot=c)
    wheel_part("Wheel_FL", (-.93, 1.37, .34))
    wheel_part("Wheel_RL", (-.93, -1.37, .34))
    wheel_part("Wheel_RR", (.93, -1.37, .34))
    wheel_part("Wheel_FR_Detached", (2.05, 1.95, 1.2 - .343))
    b.place(rot=(0, 180, 0))


# ---------------------------------------------------------------------- DISASTER_12
@asset("DISASTER_12", "Collapsed Boat Hull", "disaster", pose="wrecked timber fishing boat heeled over on the ground, keel broken amidships",
       notes={"parts": "Keel_Aft/Keel_Fore (broken), Ribs, Planks_Port, Planks_Starboard (strakes missing/splintered), Stem, Transom, Deck_Beams, Cabin_Posts, Mast_Broken, Rudder_Detached"})
def boat_hull(b):
    rng = random.Random(12)
    L, Bm, D, TH = 7.0, 1.15, 1.0, 1.32

    def hb(s):
        if s < .4:
            return Bm * (.62 + .38 * (s / .4) ** .6)
        u = (s - .4) / .6
        return Bm * max(.04, 1 - u ** 2.3)

    def dp(s):
        return D * (.78 + .22 * s)

    def warp(p):
        x, y, z = p
        m = math.exp(-((y - .3) / 1.3) ** 2)
        w = sstep(-.9, 0, z)
        x *= 1 - .42 * m * w
        z -= .42 * m * w + .26 * m
        z += .08 * math.sin(y * 2)
        return Vector((x, y, z))

    def P(s, th, sg, off=0.0):
        hbs, d = hb(s) + off, dp(s) + off
        return warp((sg * hbs * math.sin(th), -L / 2 + L * s, -d * math.cos(th)))

    # ---- keel (two broken halves)
    def keel(s0, s1, jag):
        def f(bm):
            n = 8
            pts = [P(s0 + (s1 - s0) * i / n, 0, 1, .02) for i in range(n + 1)]
            tube(bm, pts, [(.07, .10)] * (n + 1), n=4)
            for sgn, sv in ((jag, s1 if jag > 0 else s0),):
                e = P(sv, 0, 1, .02)
                for k in range(4):
                    a = k * math.pi / 2 + .4
                    p0 = e + Vector((math.cos(a) * .05, 0, math.sin(a) * .07))
                    beam(bm, p0, p0 + Vector((rng.uniform(-.03, .03), jag * rng.uniform(.18, .34), rng.uniform(-.03, .05))), .035, .03, .006, .006)
        return f
    b.add("Keel_Aft", [keel(0, .47, 1)], "timber")
    b.add("Keel_Fore", [keel(.55, 1, -1)], "timber")

    # ---- ribs
    def ribs(bm):
        for j in range(10):
            s = .06 + .86 * j / 9
            for sg in (-1, 1):
                top = TH - (.5 * rng.random() if (.25 < s < .75 and rng.random() < .7) else 0)
                pts = [P(s, top * i / 8, sg, -.015) for i in range(9)]
                tube(bm, pts, [(.03, .045)] * 9, n=4)
    b.add("Ribs", [ribs], "timber")

    # ---- planking
    def planks(sg):
        def f(bm):
            K = 9
            for k in range(K):
                th0, th1 = TH * k / K, TH * (k + 1) / K
                segs = [(0.0, 1.0)]
                if k >= 4 and sg < 0 or (k >= 6 and sg > 0):
                    g0 = rng.uniform(.25, .5)
                    g1 = g0 + rng.uniform(.2, .35)
                    segs = [(rng.uniform(0, .05), g0), (g1, 1 - rng.uniform(0, .1))]
                    if k >= 7 and rng.random() < .5:
                        segs = segs[:1]
                if k <= 2 and sg > 0 and rng.random() < .5:
                    segs = [(0.0, rng.uniform(.5, .7)), (rng.uniform(.78, .86), 1.0)]
                for (a0, a1) in segs:
                    if a1 - a0 < .08:
                        continue
                    n = max(3, int((a1 - a0) * 13))
                    rows = []
                    for i in range(n + 1):
                        s = a0 + (a1 - a0) * i / n
                        r = [P(s, th0, sg, .04), P(s, th1, sg, .04), P(s, th1, sg, 0), P(s, th0, sg, 0)]
                        if i in (0, n) and (a0 > .01 or a1 < .99):
                            r = [q + Vector((0, rng.uniform(-.12, .12), 0)) for q in r]
                        rows.append([bm.verts.new(q) for q in r])
                    skin(bm, rows)
        return f

    def pm(f):
        return 0 if f.calc_center_median().z < -.62 else 1
    b.add("Planks_Port", [planks(-1)], ["hull_blue", "hull_white"], face_mat=pm)
    b.add("Planks_Starboard", [planks(1)], ["hull_blue", "hull_white"], face_mat=pm)

    def stem(bm):
        pts = [P(1.0, 0, 1, .02), warp((0, L / 2 + .12, -.55)), warp((0, L / 2 + .24, -.05)), warp((0, L / 2 + .3, .5))]
        tube(bm, pts, [(.06, .08), (.06, .08), (.055, .07), (.05, .06)], n=4)
    b.add("Stem", [stem], "timber")

    def transom(bm):
        ths = [-TH + 2 * TH * i / 10 for i in range(11)]
        outer = [P(0, abs(t), 1 if t > 0 else -1, .0) for t in ths]
        outer = [Vector((q.x, q.y - .02, q.z)) for q in outer]
        inner = [q + Vector((0, .07, 0)) for q in outer]
        # tear the top edge
        for i in (6, 7, 8):
            outer[i].z -= .25 + .1 * rng.random()
            inner[i].z -= .25 + .1 * rng.random()
        skin(bm, [[bm.verts.new(q) for q in outer], [bm.verts.new(q) for q in inner]])
    b.add("Transom", [transom], "hull_white")

    def deck(bm):
        for i, s in enumerate((.12, .27, .42, .57, .72)):
            pl, pr = P(s, TH, -1, .0), P(s, TH, 1, .0)
            pl.z += .02
            pr.z += .02
            if i in (1, 2):
                pr = vlerp(pl, pr, .45 + .1 * rng.random())
            if i == 3:
                pl = vlerp(pl, pr, .5)
            beam(bm, pl, pr, .09, .1, .09, .1)
    b.add("Deck_Beams", [deck], "wood_dark")

    def posts(bm):
        base = [P(.24, TH * .9, -1), P(.24, TH * .9, 1), P(.42, TH * .9, 1), P(.42, TH * .9, -1)]
        for k, bp in enumerate(base):
            top = bp + Vector((rng.uniform(-.15, .15), rng.uniform(-.1, .1), 1.0 - .45 * (k % 2)))
            tube(bm, [bp + Vector((0, 0, -.05)), vlerp(bp, top, .5), top], [(.05, .05), (.045, .045), (.04, .04)], n=4)
        beam(bm, base[0] + Vector((0, 0, .9)), base[3] + Vector((.0, -.05, .85)), .08, .06)
    b.add("Cabin_Posts", [posts], "wood_light")

    def mast(bm):
        p0 = P(.55, 0, 1, -.02) + Vector((0, 0, .3))
        pts = [p0, p0 + Vector((.35, -.4, 1.0)), p0 + Vector((.8, -1.0, 1.9)), p0 + Vector((1.5, -1.9, 2.3))]
        tube(bm, pts, [(.07, .07), (.06, .06), (.05, .05), (.04, .04)], n=6)
        e = pts[-1]
        for k in range(5):
            a = k * 1.256
            beam(bm, e + Vector((math.cos(a) * .03, 0, math.sin(a) * .03)),
                 e + Vector((.18 + rng.uniform(-.05, .08), -.25 - rng.uniform(0, .15), .1 * rng.random())), .04, .02, .006, .006)
        # trailing rope
        rp = [pts[2], pts[2] + Vector((.5, -.2, -.5)), pts[2] + Vector((1.2, .1, -1.5)), pts[2] + Vector((1.5, .5, -2.1))]
        tube(bm, rp, [.018] * 4, n=4)
    b.add("Mast_Broken", [mast], "wood_light")

    def rudder(bm):
        beam(bm, (2.1, -3.3, .05), (2.2, -3.3, 1.3), .06, .5, .06, .5, up=(0, 1, 0))
        beam(bm, (2.1, -3.3, 1.3), (2.12, -3.35, 1.55), .07, .08)
    b.add("Rudder_Detached", [rudder], "wood_dark", pivot=(2.1, -3.3, .1))
    b.place(rot=(-3, 33, 8))


# ---------------------------------------------------------------------- DISASTER_13
@asset("DISASTER_13", "Broken Road Slab", "disaster", pose="three broken asphalt/concrete slabs, one flat, two tilted with exposed rebar",
       notes={"parts": "Slab_A (flat), Slab_B (tilted ramp), Slab_C (leaning), Rebar, Rubble_Chunks", "layers": "concrete base / asphalt wearing course / painted line"})
def broken_road(b):
    rng = random.Random(13)

    def inset(o, k):
        cx = sum(p[0] for p in o) / len(o)
        cy = sum(p[1] for p in o) / len(o)
        return [(cx + (x - cx) * k, cy + (y - cy) * k) for x, y in o]

    def slab_fn(outline, line=True):
        def f(bm):
            with_mat(0, lambda m: gprism(m, -.34, 0, inset(outline, .96), outline))(bm)
            with_mat(1, lambda m: gprism(m, 0, .09, outline, inset(outline, .985)))(bm)
            if line:
                with_mat(2, lambda m: gprism(m, .09, .1, [(-1.3, -.07), (1.3, -.07), (1.3, .07), (-1.3, .07)]))(bm)
        return f
    oA = jag_outline(rng, 10, 2.3, 1.55, .10)
    oB = jag_outline(rng, 9, 1.9, 1.4, .13)
    oC = jag_outline(rng, 8, 1.4, 1.25, .15)
    mats = ["concrete", "asphalt", "road_line"]
    b.add("Slab_A", [slab_fn(oA)], mats, bevel=0.012)
    b.add("Slab_B", [placed(slab_fn(oB), "X", -22, (.25, 3.6, .35))], mats, bevel=0.012, pivot=(.25, 3.6, .35))
    b.add("Slab_C", [placed(slab_fn(oC, line=False), "X", 44, (-.4, -3.0, .55))], mats, bevel=0.012, pivot=(-.4, -3.0, .55))

    def rebar(bm):
        for (ax, ang, off, ys, ye) in (("X", 0, (0, 0, 0), 1.0, 2.2), ("X", -22, (.25, 3.6, .35), -1.3, -.3), ("X", 44, (-.4, -3.0, .55), 1.0, 1.9)):
            for k in range(6):
                x = -1.1 + 2.2 * k / 5 + rng.uniform(-.1, .1)
                pts = [Vector((x, ys, -.17)), Vector((x + rng.uniform(-.08, .08), (ys + ye) / 2, -.17 + rng.uniform(-.03, .1))), Vector((x + rng.uniform(-.2, .2), ye * rng.uniform(.9, 1.0), -.17 + rng.uniform(.0, .25)))]
                before = set(bm.verts)
                tube(bm, pts, [.016] * 3, n=5)
                new = [v for v in bm.verts if v not in before]
                if ang:
                    rotate_bm(bm, new, ax, ang)
                bmesh.ops.translate(bm, verts=new, vec=off)
    b.add("Rebar", [rebar], "metal_rust")

    def chunks(bm):
        for k in range(9):
            s = rng.uniform(.12, .3)
            x, y = rng.uniform(-1.8, 1.8), rng.choice((rng.uniform(1.5, 2.4), rng.uniform(-2.4, -1.6)))
            blob(bm, (x, y, s * .5), (s * 1.2, s, s * .7), sub=1, seed=rng.uniform(0, 9), rough=.4)
    b.add("Rubble_Chunks", [chunks], "concrete")
    b.place(rot=(0, 0, 0))


# ---------------------------------------------------------------------- DISASTER_14
@asset("DISASTER_14", "Ice Fragment", "disaster", pose="resting on its flat base",
       notes={"parts": "Ice_Shell (faceted, translucent), Inner_Core, Frost_Cap", "note": "translucency is material alpha (MTL d)"})
def ice_fragment(b):
    rng = random.Random(14)

    def shell(bm):
        blob(bm, (0, 0, 0), (.62, .50, .78), sub=3, seed=14.2, rough=.16, freq=1.3)
        cut(bm, (0, 0, -.30), (.12, -.1, -1), "neg", 1)
        for n, d in (((.9, .35, .3), .42), ((-.8, .4, .5), .42), ((.1, -.9, .35), .40), ((-.3, .7, .7), .52), ((.5, -.5, .85), .56)):
            nv = Vector(n).normalized()
            cut(bm, nv * d, nv, "neg", 1)
        for f in bm.faces:
            f.material_index = f.material_index
    b.add("Ice_Shell", [shell], ["ice_pale", "ice_white"], smooth=False)

    def core(bm):
        blob(bm, (0, 0, .05), (.28, .22, .42), sub=2, seed=3.3, rough=.2)
    b.add("Inner_Core", [core], "ice_deep", parent="Ice_Shell")

    def cap(bm):
        for k in range(5):
            a = rng.uniform(0, 6.283)
            r = rng.uniform(.0, .22)
            blob(bm, (math.cos(a) * r, math.sin(a) * r, .62 + rng.uniform(-.05, .0)), (.13, .12, .05), sub=1, seed=rng.uniform(0, 9), rough=.25)
    b.add("Frost_Cap", [cap], "ice_white", parent="Ice_Shell")
    b.place(rot=(0, 0, 0))




# ==========================================================================
# CATEGORY C - CELESTIAL OBJECTS (12).  Origin = body centre, +Y (file) = north pole, 1.0 model unit = mean equatorial radius
# ==========================================================================
def llvec(lat, lon):
    a, o = math.radians(lat), math.radians(lon)
    return Vector((-math.cos(a) * math.sin(o), math.cos(a) * math.cos(o), math.sin(a)))


def to_ll(d):
    return math.degrees(math.asin(max(-1.0, min(1.0, d.z)))), math.degrees(math.atan2(-d.x, d.y))


def adeg(d, lat, lon):
    return math.degrees(math.acos(max(-1.0, min(1.0, d.dot(llvec(lat, lon))))))


def fdir(f):
    return f.calc_center_median().normalized()


def sphere(bm, sub, rad, squash=1.0):
    for v in icosphere(bm, sub, 1.0):
        d = v.co.normalized()
        r = rad(d)
        v.co = Vector((d.x * r, d.y * r, d.z * r * squash))


def rand_craters(rng, spec, avoid=None):
    out = []
    for (n, rmin, rmax, depth, rim) in spec:
        for _ in range(n):
            d = Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1))).normalized()
            if avoid and avoid(d) and rng.random() < .8:
                continue
            R = rmin + (rmax - rmin) * rng.random() ** 2.2
            out.append((d, R, depth * (.6 + .8 * rng.random()) * (R / rmax) ** .5, rim * (.7 + .6 * rng.random())))
    return out


def crater_class(d, craters):
    """0 none, 1 rim, 2 floor"""
    cls = 0
    for (cd, R, depth, rim) in craters:
        c = d.dot(cd)
        if c < math.cos(min(3.0, R * 1.35)):
            continue
        t = math.acos(max(-1.0, min(1.0, c))) / R
        if t < .93:
            return 2
        if t < 1.3:
            cls = 1
    return cls


def crater_h(d, craters):
    h = 0.0
    for (cd, R, depth, rim) in craters:
        if d.dot(cd) < math.cos(min(3.0, R * 2.2)):
            continue
        h += crater_height(d, [(cd, R, depth, rim)])
    return h


def planet_part(b, key, sub, rad, mat, mats, smooth=False, squash=1.0):
    b.add(key, [lambda bm: sphere(bm, sub, rad, squash)], mats, face_mat=lambda f: mat(fdir(f)), smooth=smooth)


def _inpoly(lon, lat, poly):
    inside = False
    n = len(poly)
    j = n - 1
    for i in range(n):
        xi, yi = poly[i]
        xj, yj = poly[j]
        if (yi > lat) != (yj > lat) and lon < (xj - xi) * (lat - yi) / (yj - yi + 1e-12) + xi:
            inside = not inside
        j = i
    return inside


# ---------------------------------------------------------------------- CELESTIAL_01 Moon
MARIA = [(33, -16, 20), (28, 18, 12), (8, 31, 14), (17, 59, 8), (-5, 52, 10), (-21, -16, 12), (18, -55, 26), (-24, -39, 6), (46, 0, 9)]


def _mare_w(d):
    w = 0.0
    for i, (la, lo, r) in enumerate(MARIA):
        a = adeg(d, la, lo)
        rr = r * (1 + .28 * fbm(d * 3.0 + Vector((i * 3.1, 1, 2)), 2))
        w = max(w, 1 - smoothstep(rr * .8, rr, a))
    return w


@asset("CELESTIAL_01", "Detailed Moon", "celestial", style="space", pose="near side toward +Y (-Z in file), north pole +Y(file)",
       notes={"scale": "1 model unit = 1737.4 km (mean radius)", "geometry": "~110 modelled craters with raised rims, 8 maria as lowered smooth basins, Tycho ray system in the material layout",
              "_view": (180, 8)})
def moon(b):
    rng = random.Random(1)
    cr = rand_craters(rng, [(8, .12, .22, .030, .011), (34, .05, .11, .018, .007), (70, .035, .06, .009, .004)],
                      avoid=lambda d: _mare_w(d) > .5)
    cr.append((llvec(-43, -11), .055, .018, .008))      # Tycho
    cr.append((llvec(10, -38), .06, .016, .008))        # Copernicus-like
    cr.append((llvec(9, 20), .035, .01, .005))

    def rad(d):
        w = _mare_w(d)
        return 1 + .010 * fbm(d * 2.5, 3) - .011 * w + .004 * fbm(d * 9, 2) * (1 - w) + crater_h(d, cr)
    tyc = llvec(-43, -11)

    def mat(d):
        c = crater_class(d, cr)
        if c == 2:
            return 3
        if c == 1:
            return 2
        if _mare_w(d) > .5:
            return 1
        a = adeg(d, -43, -11)
        if a < 55:
            q = d - tyc * d.dot(tyc)
            ang = math.atan2(q.y, q.x) if q.length > 1e-6 else 0
            if a > 4 and math.sin(ang * 9 + 2 * fbm(d * 4, 2)) > .93 - .2 * (a / 55):
                return 2
        return 0
    planet_part(b, "Moon", 6, rad, mat, ["moon_hi", "moon_mare", "moon_rim", "moon_floor"])


# ---------------------------------------------------------------------- CELESTIAL_02 Earth
CONT = {
    "namerica": [(-168, 66), (-162, 70), (-140, 70), (-125, 70), (-95, 72), (-82, 69), (-62, 60), (-56, 52), (-66, 45), (-70, 42), (-76, 35), (-81, 30), (-80, 25), (-84, 30), (-90, 29), (-97, 26), (-97, 21), (-92, 18), (-88, 21), (-87, 15), (-83, 10), (-79, 8), (-84, 8), (-92, 14), (-105, 20), (-110, 24), (-113, 31), (-118, 34), (-124, 40), (-124, 48), (-130, 54), (-140, 60), (-150, 60), (-158, 58), (-166, 60)],
    "samerica": [(-78, 8), (-72, 12), (-62, 10), (-52, 5), (-50, 0), (-35, -6), (-39, -14), (-41, -22), (-48, -26), (-58, -35), (-65, -41), (-66, -48), (-69, -53), (-74, -52), (-74, -40), (-71, -30), (-70, -18), (-76, -14), (-81, -5), (-80, 2)],
    "africa": [(-17, 21), (-10, 30), (-6, 36), (10, 37), (20, 32), (32, 31), (34, 28), (43, 12), (51, 12), (40, -3), (40, -15), (35, -24), (32, -29), (26, -34), (18, -34), (12, -18), (13, -8), (9, 0), (9, 4), (-8, 4), (-15, 11)],
    "eurasia": [(-9, 37), (-9, 43), (-2, 44), (-5, 48), (2, 51), (8, 54), (10, 57), (5, 60), (12, 66), (25, 71), (40, 68), (60, 70), (80, 73), (110, 76), (140, 72), (170, 70), (180, 66), (165, 60), (160, 54), (156, 51), (143, 52), (140, 46), (131, 42), (129, 35), (122, 30), (120, 22), (108, 20), (106, 10), (100, 13), (103, 2), (98, 8), (94, 17), (88, 22), (80, 15), (77, 8), (73, 17), (70, 22), (67, 25), (57, 25), (56, 27), (50, 30), (48, 29), (51, 25), (56, 24), (59, 22), (52, 16), (43, 13), (39, 21), (35, 28), (34, 31), (36, 36), (30, 36), (27, 37), (26, 40), (23, 40), (23, 36), (21, 38), (19, 41), (14, 45), (12, 44), (16, 41), (18, 40), (16, 38), (12, 42), (9, 44), (3, 43), (-1, 37), (-5, 36)],
    "australia": [(114, -22), (122, -18), (130, -12), (137, -12), (142, -11), (146, -19), (153, -26), (151, -34), (146, -39), (140, -38), (135, -34), (129, -32), (115, -34)],
    "greenland": [(-55, 60), (-45, 60), (-20, 70), (-20, 80), (-60, 82), (-72, 78)],
    "madagascar": [(44, -25), (47, -25), (50, -15), (49, -12), (44, -17)],
    "japan": [(130, 31), (135, 34), (141, 38), (142, 43), (140, 41), (135, 36), (130, 33)],
    "uk": [(-5, 50), (1, 51), (-2, 57), (-5, 58), (-6, 54)],
    "sumatra": [(95, 5), (105, -5), (102, -4)],
    "borneo": [(109, 2), (117, 7), (119, 1), (116, -4), (110, -3)],
    "nz_n": [(172, -35), (178, -38), (174, -41)],
    "nz_s": [(172, -41), (174, -42), (168, -46), (166, -45)],
    "iceland": [(-24, 64), (-14, 64), (-14, 66), (-23, 66)],
}


def _land(lat, lon):
    if lat < -68 + 2.5 * math.sin(math.radians(lon) * 3):
        return True
    for k, p in CONT.items():
        if _inpoly(lon, lat, p):
            return True
    return False


def _land_d(d):
    la, lo = to_ll(d)
    return _land(la, lo)


def _near_land(d):
    la, lo = to_ll(d)
    for dla, dlo in ((5, 0), (-5, 0), (0, 5), (0, -5), (3.5, 3.5), (-3.5, -3.5), (3.5, -3.5), (-3.5, 3.5)):
        if _land(max(-89, min(89, la + dla)), lo + dlo):
            return True
    return False


def _in_box(la, lo, la0, la1, lo0, lo1):
    return la0 <= la <= la1 and lo0 <= lo <= lo1


@asset("CELESTIAL_02", "Earth", "celestial", style="space", pose="Atlantic/Africa/Europe facing +Y (-Z in file)",
       notes={"scale": "1 model unit = 6378 km (equatorial radius)", "geometry": "continents are hand-built lat/lon polygons (approximate), raised above the ocean; mountain ranges displaced; Clouds is a separate translucent part",
              "_view": (180, 10)})
def earth(b):
    def rad(d):
        la, lo = to_ll(d)
        if _land_d(d):
            h = .014 + .012 * max(0, fbm(d * 5, 3) + .1)
            if _in_box(la, lo, 26, 37, 75, 100) or _in_box(la, lo, -50, 8, -78, -66) or _in_box(la, lo, 35, 60, -125, -108):
                h += .02 * (1 - abs(fbm(d * 9, 2)))
            return 1 + h
        return 1 - .004 + .003 * fbm(d * 3, 2)

    def mat(d):
        la, lo = to_ll(d)
        if _land_d(d):
            if abs(la) > 72 or la < -66 or _inpoly(lo, la, CONT["greenland"]):
                return 7
            n = fbm(d * 4 + Vector((2, 2, 2)), 2)
            if (_in_box(la, lo, 14, 30, -16, 35) or _in_box(la, lo, 16, 30, 38, 58) or _in_box(la, lo, -34, -20, 120, 140)
                    or _in_box(la, lo, 38, 46, 90, 112) or _in_box(la, lo, 30, 38, -118, -105) or _in_box(la, lo, -28, -18, 12, 24)) and n > -.25:
                return 6
            if (_in_box(la, lo, 26, 37, 75, 100) or _in_box(la, lo, -50, 8, -78, -66) or _in_box(la, lo, 35, 60, -125, -108)) and fbm(d * 9, 2) > -.1:
                return 5
            if la > 55 or la < -45:
                return 4
            return 3 if (abs(la) > 24 or n > .1) else 4
        if _near_land(d):
            return 2
        return 0 if fbm(d * 2.6 + Vector((7, 1, 3)), 2) > -.05 else 1
    planet_part(b, "Earth", 6, rad, mat, ["ocean", "ocean_deep", "ocean_shallow", "land_green", "land_dark", "land_brown", "desert", "polar"])

    rng = random.Random(2)

    def clouds(bm):
        for k in range(90):
            lat = rng.uniform(-70, 70)
            if rng.random() < .35:
                lat = rng.choice((-1, 1)) * rng.uniform(5, 20)
            n = llvec(lat, rng.uniform(-180, 180))
            s = rng.uniform(.45, 1.0)
            tmp = bmesh.new()
            blob(tmp, (0, 0, 0), (.15 * s, .08 * s, .022), sub=1, seed=rng.uniform(0, 9), rough=.3)
            q = Vector((0, 0, 1)).rotation_difference(n)
            bmesh.ops.rotate(tmp, verts=tmp.verts, cent=(0, 0, 0), matrix=q.to_matrix())
            bmesh.ops.translate(tmp, verts=tmp.verts, vec=n * 1.03)
            merge_bm(bm, tmp)
    b.add("Clouds", [clouds], "cloud", parent="Earth")


# ---------------------------------------------------------------------- CELESTIAL_03 Mars
@asset("CELESTIAL_03", "Mars", "celestial", style="space", pose="Tharsis hemisphere toward +Y",
       notes={"scale": "1 model unit = 3396 km", "geometry": "Olympus Mons cone + caldera, Tharsis bulge, Valles Marineris trench, Hellas basin, ~45 craters, polar caps", "_view": (180, 8)})
def mars(b):
    rng = random.Random(3)
    cr = rand_craters(rng, [(5, .09, .15, .02, .008), (40, .035, .08, .012, .005)])
    DARK = [(8, 70, 12), (45, -20, 18), (-3, 0, 10), (-35, -155, 15), (-20, 100, 10), (10, -50, 8)]

    def valles(d):
        la, lo = to_ll(d)
        if not (-95 < lo < -40):
            return 9
        cla = -9 + 2.2 * math.sin((lo + 95) / 14.0)
        return abs(la - cla) * 1.0

    def rad(d):
        h = .006 * fbm(d * 3, 3) + .01 * fbm(d * 12, 2)
        a = adeg(d, 0, -105)
        h += .022 * math.exp(-(a / 26) ** 2)
        a = adeg(d, 18, -134)
        if a < 6:
            h += .05 * (1 - smoothstep(0, 6, a)) ** 0.8 - (.012 if a < 1.3 else 0)
        v = valles(d)
        h -= .016 * (1 - smoothstep(.8, 2.6, v))
        a = adeg(d, -42, 70)
        if a < 15:
            h -= .02 * (1 - (a / 15) ** 2)
        la, lo = to_ll(d)
        if abs(la) > 80 + 2 * fbm(d * 5, 2):
            h += .004
        return 1 + h + crater_h(d, cr)

    def mat(d):
        la, lo = to_ll(d)
        if abs(la) > 80 + 2 * fbm(d * 5, 2):
            return 3
        c = crater_class(d, cr)
        if c == 2:
            return 1
        if c == 1:
            return 2
        if valles(d) < 1.8:
            return 1
        if adeg(d, 18, -134) < 6:
            return 2
        for (a, o, r) in DARK:
            if adeg(d, a, o) < r * (1 + .3 * fbm(d * 3, 2)):
                return 1
        if adeg(d, -42, 70) < 12 or adeg(d, 20, 0) < 14 and fbm(d * 4, 2) > 0:
            return 2
        return 0
    planet_part(b, "Mars", 6, rad, mat, ["mars_red", "mars_dark", "mars_light", "mars_ice"])


# ---------------------------------------------------------------------- CELESTIAL_04 Jupiter
JUP_LAT = [-62, -45, -35, -27, -18, -8, 0, 8, 17, 24, 32, 44, 60]
JUP_MAT = ["jup_tan", "jup_cream", "jup_brown", "jup_white", "jup_rust", "jup_cream", "jup_brown", "jup_white", "jup_tan", "jup_rust", "jup_cream", "jup_tan", "jup_brown", "jup_cream"]


def _band_idx(lat, bounds):
    i = 0
    while i < len(bounds) and lat > bounds[i]:
        i += 1
    return i


@asset("CELESTIAL_04", "Jupiter", "celestial", style="space", pose="Great Red Spot toward +Y; oblate (polar/equatorial 0.935)",
       notes={"scale": "1 model unit = 71,492 km (equatorial)", "geometry": "latitude bands with turbulent edges as slightly raised zones, Great Red Spot raised oval with swirl ring, white ovals", "_view": (180, 6)})
def jupiter(b):
    mats = ["jup_cream", "jup_tan", "jup_brown", "jup_rust", "jup_white", "jup_red"]
    names = sorted(set(JUP_MAT) | {"jup_red"})
    idx = {n: i for i, n in enumerate(names)}

    def warped(d):
        la, lo = to_ll(d)
        return la + 2.6 * fbm(Vector((math.radians(lo) * 3.0, math.radians(la) * 5.0, 1.3)), 2) + 1.2 * math.sin(math.radians(lo) * 5 + la * .2), la, lo

    def grs(la, lo):
        return ((la + 22) / 6.8) ** 2 + (((lo - 8 + 180) % 360 - 180) / 12.5) ** 2

    def rad(d):
        w, la, lo = warped(d)
        h = .004 * math.sin(math.radians(w) * 14)
        q = grs(la, lo)
        if q < 1.3:
            h += .011 * (1 - smoothstep(.15, 1.3, q))
        return 1 + h

    def mat(d):
        w, la, lo = warped(d)
        q = grs(la, lo)
        if q < .30:
            return idx["jup_red"]
        if q < .65:
            return idx["jup_rust"]
        if q < 1.0:
            return idx["jup_white"]
        for (a, o) in ((-33, 0), (-33, -25), (-33, 40)):
            if ((la - a) / 2.5) ** 2 + (((lo - o + 180) % 360 - 180) / 4.0) ** 2 < 1:
                return idx["jup_white"]
        return idx[JUP_MAT[_band_idx(w, JUP_LAT)]]
    planet_part(b, "Jupiter", 6, rad, mat, names, smooth=True, squash=.935)


# ---------------------------------------------------------------------- CELESTIAL_05 Saturn
SAT_LAT = [-70, -52, -40, -28, -16, -6, 4, 14, 26, 38, 52, 66]
SAT_MAT = ["sat_dark", "sat_gold", "sat_cream", "sat_pale", "sat_gold", "sat_cream", "sat_pale", "sat_gold", "sat_cream", "sat_pale", "sat_gold", "sat_cream", "sat_dark"]


@asset("CELESTIAL_05", "Saturn", "celestial", style="space", pose="equatorial ring plane horizontal; oblate (0.902)",
       notes={"scale": "1 model unit = 60,268 km (equatorial); rings extend to 2.34 units", "geometry": "banded globe with north polar hexagon; Rings = separate solid annulus meshes (C, B ringlets, A, Encke gap and Cassini Division left as true gaps, thin F ring)",
              "_view": (170, 30)})
def saturn(b):
    names = sorted(set(SAT_MAT))
    idx = {n: i for i, n in enumerate(names)}

    def hexa(d):
        la, lo = to_ll(d)
        pol = 90 - la
        if la < 0:
            return False
        ang = math.radians(((lo % 60) - 30))
        return pol < 13.0 * math.cos(math.radians(30)) / math.cos(ang)

    def rad(d):
        la, lo = to_ll(d)
        h = .003 * math.sin(math.radians(la) * 11 + 3 * fbm(d * 2, 2))
        if hexa(d):
            h -= .006
        return 1 + h

    def mat(d):
        if hexa(d):
            return idx["sat_dark"]
        la, lo = to_ll(d)
        w = la + 1.8 * fbm(Vector((math.radians(lo) * 2.0, math.radians(la) * 4, 3)), 2)
        return idx[SAT_MAT[_band_idx(w, SAT_LAT)]]
    planet_part(b, "Saturn", 6, rad, mat, names, smooth=True, squash=.902)

    ring_defs = [(1.24, 1.53, 0), (1.53, 1.60, 1), (1.60, 1.67, 0), (1.67, 1.77, 1), (1.77, 1.83, 0), (1.83, 1.95, 1),
                 (2.03, 2.21, 2), (2.23, 2.27, 2)]

    def rings(bm):
        for (r0, r1, m) in ring_defs:
            with_mat(m, lambda bb, r0=r0, r1=r1: lathe(bb, [(r0, .004), (r1, .004), (r1, -.004), (r0, -.004)], n=120, closed=True))(bm)
        with_mat(3, lambda bb: lathe(bb, [(2.32, .005), (2.345, .005), (2.345, -.005), (2.32, -.005)], n=120, closed=True))(bm)
    b.add("Rings", [rings], ["ring_c", "ring_b", "ring_a", "ring_gap"], parent="Saturn")




def _rdir(rng):
    return Vector((rng.gauss(0, 1), rng.gauss(0, 1), rng.gauss(0, 1))).normalized()


def _smax(a, b, k):
    h = max(k - abs(a - b), 0) / k
    return max(a, b) + h * h * k * .25


def _rock_boulders(bm, rng, n, rad_fn, smin, smax_):
    for _ in range(n):
        d = _rdir(rng)
        s = rng.uniform(smin, smax_)
        blob(bm, d * rad_fn(d) * (1 - s * .25), (s, s * rng.uniform(.7, 1), s * rng.uniform(.6, .9)), sub=1, seed=rng.uniform(0, 30), rough=.3)


# ---------------------------------------------------------------------- CELESTIAL_06 Venus
@asset("CELESTIAL_06", "Venus", "celestial", style="space", pose="north pole +Y(file)",
       notes={"scale": "1 model unit = 6051.8 km", "geometry": "smooth globe with swirling cloud-deck bands, polar vortex dimples and chevron wave ridges modelled as shallow displacement", "_view": (180, 10)})
def venus(b):
    def sw(d):
        la, lo = to_ll(d)
        chev = abs(la) * .35 + 5 * abs(math.sin(math.radians(lo) * .5)) * 0
        return math.sin(math.radians(la) * 13 + 3.2 * fbm(d * 2.1 + Vector((1, 4, 2)), 3) + chev * .0 + abs(la) * .03 * math.sin(math.radians(lo) * 2))

    def rad(d):
        la, lo = to_ll(d)
        h = .006 * sw(d) + .003 * fbm(d * 7, 2)
        if abs(la) > 80:
            h -= .006 * (abs(la) - 80) / 10
        return 1 + h

    def mat(d):
        v = sw(d) + .35 * fbm(d * 5 + Vector((8, 2, 1)), 2)
        return 0 if v < -.45 else (1 if v < 0 else (2 if v < .5 else 3))
    planet_part(b, "Venus", 6, rad, mat, ["venus_a", "venus_b", "venus_c", "venus_d"], smooth=True)


# ---------------------------------------------------------------------- CELESTIAL_07 Mercury
@asset("CELESTIAL_07", "Mercury", "celestial", style="space", pose="Caloris Basin toward +Y",
       notes={"scale": "1 model unit = 2439.7 km", "geometry": "~170 modelled craters (power-law sizes, raised rims), multi-ring Caloris Basin, lobate scarps, smooth plains in the material layout", "_view": (180, 8)})
def mercury(b):
    rng = random.Random(7)
    cr = rand_craters(rng, [(6, .12, .2, .03, .012), (40, .05, .1, .018, .008), (130, .032, .055, .01, .005)])
    cal = llvec(30, 0)

    def cal_h(d):
        a = math.acos(max(-1, min(1, d.dot(cal))))
        t = a / .43
        h = 0.0
        if t < 1:
            h -= .022 * (1 - t * t) ** .8
        for r0, ht in ((.55, .008), (1.0, .014), (1.5, .006)):
            h += ht * math.exp(-((t - r0) / .07) ** 2)
        return h

    def rad(d):
        return 1 + .006 * fbm(d * 3, 3) + crater_h(d, cr) + cal_h(d) + .003 * fbm(d * 11, 2)

    def mat(d):
        c = crater_class(d, cr)
        a = adeg(d, 30, 0)
        if a < 24.5:
            return 3 if c != 1 else 2
        if a < 29 and a > 24.5:
            return 2
        if c == 2:
            return 1
        if c == 1:
            return 2
        return 3 if fbm(d * 2.4 + Vector((3, 3, 3)), 2) > .22 else 0
    planet_part(b, "Mercury", 6, rad, mat, ["merc_a", "merc_b", "merc_c", "merc_d"])


# ---------------------------------------------------------------------- CELESTIAL_08 Neptune
@asset("CELESTIAL_08", "Neptune", "celestial", style="space", pose="Great Dark Spot toward +Y; oblate 0.983",
       notes={"scale": "1 model unit = 24,764 km", "geometry": "banded ice giant with Great Dark Spot (depressed oval), Scooter and bright cirrus streaks", "_view": (180, 8)})
def neptune(b):
    def spot(la, lo, a, c):
        return ((la - a) / 7.5) ** 2 + (((lo - c + 180) % 360 - 180) / 15.0) ** 2

    def rad(d):
        la, lo = to_ll(d)
        q = spot(la, lo, -20, 0)
        h = .003 * math.sin(math.radians(la) * 9 + 2 * fbm(d * 2, 2))
        if q < 1.4:
            h -= .008 * (1 - smoothstep(.2, 1.4, q))
        return 1 + h

    def mat(d):
        la, lo = to_ll(d)
        if spot(la, lo, -20, 0) < .9:
            return 2
        if ((la + 42) / 3) ** 2 + (((lo - 40 + 180) % 360 - 180) / 7) ** 2 < 1:
            return 3
        if ((la + 28) / 2.2) ** 2 + (((lo + 28 + 180) % 360 - 180) / 18) ** 2 < 1:
            return 3
        if ((la - 30) / 1.6) ** 2 + (((lo - 90 + 180) % 360 - 180) / 22) ** 2 < 1:
            return 3
        w = la + 2 * fbm(Vector((math.radians(lo) * 2, math.radians(la) * 4, 5)), 2)
        k = _band_idx(w, [-60, -38, -12, 10, 36, 58])
        return [0, 1, 0, 1, 0, 1, 0][k]
    planet_part(b, "Neptune", 6, rad, mat, ["nep_a", "nep_b", "nep_c", "nep_d"], smooth=True, squash=.983)


# ---------------------------------------------------------------------- CELESTIAL_09 Rocky Rogue Planet
@asset("CELESTIAL_09", "Rocky Rogue Planet", "celestial", style="space", pose="north pole +Y(file)",
       notes={"scale": "1 model unit = planet radius (fictional, ~1.2 Earth radii)", "geometry": "unlit starless world: ridged mountain chains, canyon network, 30 craters; faint geothermal glow only inside canyon floors and 5 volcanic vents (emissive material)", "_view": (180, 8)})
def rogue_rocky(b):
    rng = random.Random(9)
    cr = rand_craters(rng, [(4, .1, .18, .03, .012), (26, .04, .09, .015, .007)])
    vents = [llvec(rng.uniform(-60, 60), rng.uniform(-180, 180)) for _ in range(5)]

    def ridge(d):
        return 1 - abs(fbm(d * 2.3 + Vector((1, 5, 2)), 3))

    def canyon(d):
        return abs(fbm(d * 2.0 + Vector((9, 2, 4)), 2))

    def rad(d):
        h = .05 * ridge(d) ** 3 + .012 * fbm(d * 6, 2)
        if canyon(d) < .035:
            h -= .022 * (1 - canyon(d) / .035)
        return .975 + h + crater_h(d, cr)

    def mat(d):
        for v in vents:
            if d.dot(v) > math.cos(.04):
                return 3
        if canyon(d) < .012:
            return 3
        c = crater_class(d, cr)
        if c == 1:
            return 2
        if c == 2:
            return 0
        r = ridge(d)
        return 2 if r > .86 else (1 if r > .66 else 0)
    planet_part(b, "Rogue_Rocky", 6, rad, mat, ["rogue_dark", "rogue_mid", "rogue_hi", "rogue_glow"])


# ---------------------------------------------------------------------- CELESTIAL_10 Icy Rogue Planet
@asset("CELESTIAL_10", "Icy Rogue Planet", "celestial", style="space", pose="north pole +Y(file)",
       notes={"scale": "1 model unit = planet radius (fictional)", "geometry": "fractured ice crust: recessed crack network, raised pressure ridges, 14 craters; plates alternate in tone", "_view": (180, 8)})
def rogue_icy(b):
    rng = random.Random(10)
    cr = rand_craters(rng, [(3, .1, .16, .02, .01), (11, .04, .08, .012, .006)])

    def c1(d):
        return abs(fbm(d * 3.1 + Vector((2, 7, 1)), 2))

    def c2(d):
        return abs(fbm(d * 5.4 + Vector((6, 1, 9)), 2))

    def rad(d):
        h = .004 * fbm(d * 4, 2)
        a = c1(d)
        if a < .05:
            h -= .016 * (1 - a / .05)
        elif a < .1:
            h += .009 * math.sin((a - .05) / .05 * math.pi)
        return 1 + h + crater_h(d, cr)

    def mat(d):
        c = crater_class(d, cr)
        if c == 1:
            return 2
        if c == 2:
            return 3
        if c1(d) < .05:
            return 3
        if c1(d) < .1:
            return 2
        la = to_ll(d)[0]
        if abs(la) > 68:
            return 2
        if fbm(d * 4 + Vector((9, 9, 0)), 2) > .5:
            return 4
        return 0 if fbm(d * 1.7, 2) > .03 else 1
    planet_part(b, "Rogue_Icy", 6, rad, mat, ["ice_rog_a", "ice_rog_b", "ice_rog_c", "ice_rog_d", "ice_rog_e"])


# ---------------------------------------------------------------------- CELESTIAL_11 Asteroid
@asset("CELESTIAL_11", "Detailed Astronomical Asteroid", "celestial", style="space", pose="long axis along X",
       notes={"scale": "1 model unit = mean semi-axis (long axis ~2.5 units)", "geometry": "elongated rubble-pile body with saddle depression, 5 large + 30 small craters, 70 separate boulder meshes on Boulders part", "_view": (200, 14)})
def asteroid(b):
    rng = random.Random(11)
    cr = rand_craters(rng, [(5, .28, .5, .05, .02), (30, .1, .2, .03, .012)])
    A, B, Cc = 1.30, .78, .66

    def base(d):
        return 1 / math.sqrt((d.x / A) ** 2 + (d.y / B) ** 2 + (d.z / Cc) ** 2)

    def rad(d):
        r = base(d) * (1 + .16 * fbm(d * 1.4 + Vector((3, 1, 8)), 3))
        r -= .09 * math.exp(-(d.x / .3) ** 2) * (1 - abs(d.z) * .3)       # saddle
        r += .03 * (1 - abs(fbm(d * 5, 2))) ** 3
        return r * (1 + crater_h(d, cr))

    def mat(d):
        c = crater_class(d, cr)
        if c == 2:
            return 1
        if c == 1:
            return 2
        n = fbm(d * 3 + Vector((5, 5, 5)), 2)
        return 3 if n > .3 else (2 if n > .05 else 0)
    planet_part(b, "Asteroid", 6, rad, mat, ["aster_a", "aster_b", "aster_c", "aster_d"])
    b.add("Boulders", [lambda bm: _rock_boulders(bm, random.Random(12), 70, rad, .035, .1)], ["aster_c"], parent="Asteroid")


# ---------------------------------------------------------------------- CELESTIAL_12 Comet nucleus
@asset("CELESTIAL_12", "Comet Nucleus", "celestial", style="space", pose="bilobate; lobes along X",
       notes={"scale": "1 model unit = ~1 km (nucleus ~4.8 units long)", "geometry": "bilobate nucleus (smooth union of two lobes via a neck), terraced cliffs, 7 sinkhole pits with active vents (emissive), ice patches, 55 boulders; no tail or coma modelled", "_view": (190, 16)})
def comet(b):
    rng = random.Random(13)
    c1, R1 = Vector((-1.0, 0, 0)), .85
    c2, R2 = Vector((.9, .06, .02)), .62
    pits = [(_rdir(rng), rng.uniform(.1, .2), .07, .02) for _ in range(7)]
    vent_i = set(range(0, 7, 2))

    def far(d, c, R):
        bq = d.dot(c)
        disc = bq * bq - (c.length_squared - R * R)
        return bq + math.sqrt(disc) if (disc > 0 and bq > 0) else 0.0

    def rad(d):
        r = _smax(_smax(far(d, c1, R1), far(d, c2, R2), .18), .5, .2)
        n = fbm(d * 2.2 + Vector((4, 2, 7)), 3)
        r *= 1 + .08 * n
        r += .05 * (1 - abs(fbm(d * 4 + Vector((2, 6, 1)), 2))) ** 3 - .02
        return r + crater_h(d, pits) * r

    def mat(d):
        for i, p in enumerate(pits):
            if d.dot(p[0]) > math.cos(p[1] * .6):
                return 3 if i in vent_i else 1
        c = crater_class(d, pits)
        if c == 2:
            return 1
        n = fbm(d * 4 + Vector((1, 1, 1)), 2)
        if n > .38:
            return 2
        return 1 if n > 0 else 0
    planet_part(b, "Nucleus", 6, rad, mat, ["comet_dark", "comet_mid", "comet_ice", "comet_vent"])
    b.add("Boulders", [lambda bm: _rock_boulders(bm, random.Random(14), 55, rad, .04, .11)], ["comet_mid"], parent="Nucleus")




# ==========================================================================
# CATEGORY D - INTERIOR / COMMERCIAL (14).  Ground y=0, front = +Y (-Z in file), origin = footprint centre on the floor
# ==========================================================================
def cb(bm, cx, cy, cz, sx, sy, sz):
    box(bm, cx - sx / 2, cx + sx / 2, cy - sy / 2, cy + sy / 2, cz - sz / 2, cz + sz / 2)


def tleg(bm, x, y, h, r0, r1, n=8):
    cyl(bm, (x, y, 0), (x, y, h), r0, r1, n=n)


def rbox(bm, x0, x1, y0, y1, z0, z1, k=.88):
    """slightly tapered box (reads as upholstered / rounded when bevelled)"""
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    frustum(bm, z0, z1, cx, cy, (x1 - x0) / 2, (y1 - y0) / 2, (x1 - x0) / 2 * k + .0, (y1 - y0) / 2 * k + .0)


@asset("INTERIOR_01", "Chair", "interiors", pose="upright, facing +Y", notes={"parts": "Seat, Backrest, Legs, Stretchers"})
def chair(b):
    def legs(bm):
        for x in (-.2, .2):
            tleg(bm, x, -.19, .96, .02, .02, 6)
            tleg(bm, x, .19, .45, .022, .016, 6)
    b.add("Seat", [lambda bm: cb(bm, 0, .0, .46, .46, .44, .04)], "wood_light", bevel=.008)
    b.add("Legs", [legs], "wood_dark")
    b.add("Stretchers", [lambda bm: [beam(bm, (x, -.19, .17), (x, .19, .17), .02, .02) for x in (-.2, .2)] + [beam(bm, (-.2, 0, .2), (.2, 0, .2), .02, .02)]], "wood_dark")
    b.add("Backrest", [lambda bm: [cb(bm, 0, -.19, z, .4, .02, .07) for z in (.62, .72, .82)] + [cb(bm, 0, -.19, .93, .42, .025, .06)]], "wood_light", bevel=.006)
    b.add("Seat_Cushion", [lambda bm: rbox(bm, -.21, .21, -.2, .2, .48, .53, .94)], "fabric_coral", parent="Seat", bevel=.012)
    b.place()


@asset("INTERIOR_02", "Table", "interiors", pose="dining table", notes={"parts": "Top, Apron, Legs"})
def table(b):
    b.add("Top", [lambda bm: gprism(bm, .72, .76, [(x * 1.0, y * .55) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))], [(x * .98, y * .54) for x, y in ((-1, -1), (1, -1), (1, 1), (-1, 1))])], "wood_light", bevel=.015)
    b.add("Apron", [lambda bm: [cb(bm, 0, sy * .44, .68, 1.64, .03, .08) for sy in (-1, 1)] + [cb(bm, sx * .8, 0, .68, .03, .88, .08) for sx in (-1, 1)]], "wood_dark")
    b.add("Legs", [lambda bm: [tleg(bm, sx * .84, sy * .44, .72, .04, .025, 8) for sx in (-1, 1) for sy in (-1, 1)]], "wood_dark")
    b.place()


@asset("INTERIOR_03", "Sofa", "interiors", pose="three-seat sofa", notes={"parts": "Base, Cushions, Backs, Arms, Pillow, Feet"})
def sofa(b):
    b.add("Base", [lambda bm: cb(bm, 0, 0, .27, 2.0, .9, .26)], "fabric_blue", bevel=.03)
    b.add("Arms", [lambda bm: [rbox(bm, sx * .86 - .12, sx * .86 + .12, -.44, .44, .14, .6, .92) for sx in (-1, 1)]], "fabric_blue", bevel=.04)
    b.add("Back", [lambda bm: rbox(bm, -.9, .9, -.46, -.2, .4, .88, .94)], "fabric_blue", bevel=.04)
    b.add("Seat_Cushions", [lambda bm: [rbox(bm, -.9 + i * .6 + .01, -.9 + (i + 1) * .6 - .01, -.2, .42, .4, .55, .94) for i in range(3)]], "fabric_blue", bevel=.03)
    b.add("Back_Cushions", [lambda bm: [rbox(bm, -.9 + i * .6 + .02, -.9 + (i + 1) * .6 - .02, -.22, -.06, .55, .82, .9) for i in range(3)]], "fabric_blue", bevel=.03)
    b.add("Pillow", [lambda bm: rbox(bm, .45, .8, -.1, .04, .56, .86, .8)], "fabric_coral", bevel=.035)
    b.add("Feet", [lambda bm: [cyl(bm, (sx * .88, sy * .38, 0), (sx * .88, sy * .38, .14), .03, .022, n=6) for sx in (-1, 1) for sy in (-1, 1)]], "wood_dark")
    b.place()


@asset("INTERIOR_04", "Office Desk", "interiors", pose="drawers facing +Y side of the user (-Y)", notes={"parts": "Top, Pedestal, Drawer_1..3 (slide along +Y), Side_Panel, Modesty_Panel, Grommet"})
def desk(b):
    b.add("Top", [lambda bm: cb(bm, 0, 0, .74, 1.5, .75, .04)], "wood_light", bevel=.01)
    b.add("Pedestal", [lambda bm: [cb(bm, -.54, 0, .36, .38, .68, .72), ] + [cb(bm, -.54, .34, .02, .38, .02, .04)]], "concrete", bevel=.006)
    for i in range(3):
        z = .12 + i * .21
        b.add(f"Drawer_{i + 1}", [lambda bm, z=z: [cb(bm, -.54, .355, z + .08, .34, .02, .18), cb(bm, -.54, .37, z + .08, .14, .02, .02)]],
              ["wood_dark"], pivot=(-.54, .35, z + .08), parent="Pedestal", bevel=.004)
    b.add("Side_Panel", [lambda bm: cb(bm, .72, 0, .36, .03, .68, .72)], "wood_dark")
    b.add("Modesty_Panel", [lambda bm: cb(bm, .15, -.3, .5, 1.1, .02, .4)], "wood_dark")
    b.add("Grommet", [lambda bm: cyl(bm, (.5, -.2, .76), (.5, -.2, .765), .035, n=12)], "plastic_black", parent="Top")
    b.place()


@asset("INTERIOR_05", "Office Chair", "interiors", pose="swivel office chair facing +Y", notes={"swivel_pivot": "Seat, Backrest, Arms rotate about the Column axis; Casters roll", "parts": "Base, Casters, Column, Seat, Backrest, Arms"})
def office_chair(b):
    def base(bm):
        for i in range(5):
            a = 2 * math.pi * i / 5 + .3
            beam(bm, (0, 0, .14), (math.cos(a) * .31, math.sin(a) * .31, .1), .06, .035, .035, .03)
        cyl(bm, (0, 0, .1), (0, 0, .19), .06, .045, n=10)
    b.add("Base", [base], "plastic_black", bevel=.004)

    def casters(bm):
        for i in range(5):
            a = 2 * math.pi * i / 5 + .3
            x, y = math.cos(a) * .31, math.sin(a) * .31
            cyl(bm, (x, y, .09), (x, y, .13), .015, n=6)
            cyl(bm, (x - .012, y, .05), (x + .012, y, .05), .045, n=10)
    b.add("Casters", [casters], "rubber", parent="Base")
    b.add("Column", [lambda bm: cyl(bm, (0, 0, .19), (0, 0, .44), .03, .025, n=10)], "chrome")
    b.add("Seat", [lambda bm: [rbox(bm, -.26, .26, -.25, .27, .44, .52, .9), cb(bm, 0, 0, .43, .18, .18, .03)]], ["fabric_grey"], pivot=(0, 0, .44), bevel=.02)
    b.add("Backrest", [lambda bm: [rbox(bm, -.25, .25, -.04, .04, .6, .98, .92), beam(bm, (0, -.22, .5), (0, -.1, .66), .05, .03)]], "fabric_grey", pivot=(0, -.22, .52), parent="Seat", bevel=.02)
    b.add("Arms", [lambda bm: [x for sx in (-1, 1) for x in (beam(bm, (sx * .29, -.05, .5), (sx * .29, -.05, .66), .03, .03), cb(bm, sx * .29, .0, .68, .06, .26, .03))]], "plastic_black", parent="Seat", bevel=.006)
    b.place()


@asset("INTERIOR_06", "Shelf", "interiors", pose="bookcase", notes={"parts": "Frame, Shelves, Back_Panel, Books"})
def shelf(b):
    b.add("Frame", [lambda bm: [cb(bm, sx * .4, 0, .9, .03, .3, 1.8) for sx in (-1, 1)] + [cb(bm, 0, 0, 1.815, .83, .3, .03)]], "wood_dark", bevel=.004)
    b.add("Shelves", [lambda bm: [cb(bm, 0, 0, .03 + i * .44, .78, .29, .03) for i in range(5)]], "wood_light", bevel=.004)
    b.add("Back_Panel", [lambda bm: cb(bm, 0, -.14, .9, .78, .015, 1.76)], "concrete")
    rng = random.Random(6)

    def books(bm):
        cols = 6
        for i in range(4):
            x = -.36
            while x < .3:
                w = rng.uniform(.025, .05)
                h = rng.uniform(.22, .36)
                before = set(bm.faces)
                cb(bm, x + w / 2, -.02, .045 + i * .44 + h / 2, w * .96, .2, h)
                for f in set(bm.faces) - before:
                    f.material_index = rng.randrange(cols)
                x += w + .003
                if rng.random() < .1:
                    x += .12
    b.add("Books", [books], ["coral", "fabric_blue", "yellow", "foliage_mid", "offwhite", "wood_dark"], parent="Shelves", bevel=.002)
    b.place()


@asset("INTERIOR_07", "Commercial Counter", "interiors", pose="shop counter, customer side +Y", notes={"parts": "Counter_Body, Counter_Top, Front_Panel, Display_Glass, Back_Shelf"})
def counter(b):
    b.add("Counter_Body", [lambda bm: [cb(bm, 0, 0, .52, 2.2, .6, 1.0), cb(bm, 0, .02, .04, 2.1, .56, .08)]], ["concrete"], bevel=.008)
    b.add("Counter_Top", [lambda bm: cb(bm, 0, .03, 1.04, 2.34, .78, .06)], "wood_light", bevel=.012)
    b.add("Front_Panel", [lambda bm: [cb(bm, -.7 + i * .7, .31, .52, .6, .015, .8) for i in range(3)]], "coral", bevel=.004)
    b.add("Display_Glass", [lambda bm: [cb(bm, .0, .2, 1.28, 1.4, .012, .38), cb(bm, -.7, .1, 1.28, .012, .2, .38), cb(bm, .7, .1, 1.28, .012, .2, .38)]], "glass")
    b.add("Back_Shelf", [lambda bm: [cb(bm, 0, -.26, 1.45, 2.1, .22, .04), cb(bm, 0, -.26, 1.82, 2.1, .22, .04)] + [cb(bm, sx * 1.05, -.26, 1.44, .05, .22, .76) for sx in (-1, 1)]], "wood_dark", bevel=.004)
    b.place()


@asset("INTERIOR_08", "Refrigerator", "interiors", pose="doors face +Y; both doors hinged on the left", notes={"parts": "Body, Door_Freezer, Door_Fridge (hinge pivots in metadata), Handles, Feet"})
def fridge(b):
    b.add("Body", [lambda bm: cb(bm, 0, 0, .9, .7, .68, 1.74)], "safety_white", bevel=.02)
    for name, z0, z1 in (("Door_Freezer", 1.19, 1.78), ("Door_Fridge", .08, 1.17)):
        b.add(name, [lambda bm, z0=z0, z1=z1: cb(bm, 0, .36, (z0 + z1) / 2, .7, .04, z1 - z0)], "safety_white", pivot=(-.35, .38, (z0 + z1) / 2), parent="Body", bevel=.015)
    b.add("Handles", [lambda bm: [cb(bm, .28, .42, z, .03, .04, h) for z, h in ((1.45, .22), (.9, .5))]], "chrome", parent="Body", bevel=.004)
    b.add("Feet", [lambda bm: [cyl(bm, (sx * .3, sy * .26, 0), (sx * .3, sy * .26, .04), .03, n=8) for sx in (-1, 1) for sy in (-1, 1)]], "plastic_black", parent="Body")
    b.place()


@asset("INTERIOR_09", "Vending Machine", "interiors", pose="front faces +Y", notes={"parts": "Cabinet, Window_Glass, Products, Keypad, Display, Dispensing_Flap (hinged at its top), Coin_Slot"})
def vending(b):
    b.add("Cabinet", [lambda bm: [cb(bm, 0, 0, .94, .95, .85, 1.84), cb(bm, 0, 0, 1.87, .97, .87, .06)]], "red_paint", bevel=.015)
    b.add("Window_Glass", [lambda bm: cb(bm, -.12, .435, 1.18, .62, .015, 1.15)], "glass", parent="Cabinet")
    rng = random.Random(9)

    def prods(bm):
        for r in range(5):
            for c in range(6):
                before = set(bm.faces)
                cyl(bm, (-.38 + c * .1, .3, .66 + r * .21), (-.38 + c * .1, .3, .66 + r * .21 + .14), .035, n=8)
                for f in set(bm.faces) - before:
                    f.material_index = (r + c) % 4
        for r in range(5):
            box(bm, -.42, .17, .22, .38, .6 + r * .21, .62 + r * .21)
    b.add("Products", [prods], ["fabric_blue", "yellow", "foliage_mid", "coral"], parent="Cabinet")
    b.add("Keypad", [lambda bm: [cb(bm, .33 + (i % 3) * .06 - .06, .435, 1.35 - (i // 3) * .07, .045, .02, .045) for i in range(9)]], "plastic_white", parent="Cabinet", bevel=.003)
    b.add("Display", [lambda bm: cb(bm, .33, .435, 1.55, .16, .015, .06)], "screen_lit", parent="Cabinet")
    b.add("Coin_Slot", [lambda bm: cb(bm, .33, .435, 1.0, .05, .02, .09)], "plastic_black", parent="Cabinet")
    b.add("Dispensing_Flap", [lambda bm: cb(bm, -.05, .44, .26, .6, .02, .22)], "plastic_black", pivot=(-.05, .45, .37), parent="Cabinet", bevel=.004)
    b.place()


@asset("INTERIOR_10", "Market Cart", "interiors", pose="hand cart, handles toward -Y", notes={"parts": "Cart_Bed, Wheel_L/R (axle pivots), Handles, Awning_Poles, Awning, Produce, Crates"})
def market_cart(b):
    b.add("Cart_Bed", [lambda bm: [cb(bm, 0, .1, .55, 1.3, 1.7, .05)] + [cb(bm, sx * .65, .1, .7, .04, 1.7, .26) for sx in (-1, 1)] + [cb(bm, 0, .93, .7, 1.3, .04, .26), cb(bm, 0, -.73, .7, 1.3, .04, .26)]], "wood_light", bevel=.006)
    b.add("Handles", [lambda bm: [beam(bm, (sx * .5, -.7, .6), (sx * .5, -1.4, .85), .05, .05) for sx in (-1, 1)] + [cyl(bm, (-.5, -1.4, .85), (.5, -1.4, .85), .03, n=8)]], "wood_dark")
    for nm, sx in (("Wheel_L", -1), ("Wheel_R", 1)):
        def wh(bm, sx=sx):
            torus(bm, (sx * .72, .2, .42), .36, .035, n=20, m=6, axis="x")
            for k in range(8):
                a = k * math.pi / 4
                beam(bm, (sx * .72, .2, .42), (sx * .72, .2 + math.cos(a) * .35, .42 + math.sin(a) * .35), .035, .03)
            cyl(bm, (sx * .68, .2, .42), (sx * .76, .2, .42), .06, n=8)
        b.add(nm, [wh], "wood_dark", pivot=(sx * .72, .2, .42), parent="Cart_Bed", bevel=.0)
    b.add("Awning_Poles", [lambda bm: [cyl(bm, (sx * .6, sy * .85, .58), (sx * .6, sy * .85, 1.9 - (.15 if sy < 0 else 0)), .02, n=6) for sx in (-1, 1) for sy in (-1, 1)]], "wood_dark", parent="Cart_Bed")

    def awning(bm):
        for i in range(6):
            x0 = -.72 + i * .24
            with_mat(i % 2, lambda m, x0=x0: solid(m, [(x0, -.95, 1.75), (x0 + .24, -.95, 1.75), (x0 + .24, .95, 1.9), (x0, .95, 1.9)],
                                                   [(x0, -.95, 1.78), (x0 + .24, -.95, 1.78), (x0 + .24, .95, 1.93), (x0, .95, 1.93)]))(bm)
    b.add("Awning", [awning], ["coral", "offwhite"], parent="Cart_Bed")
    rng = random.Random(10)

    def produce(bm):
        for i in range(26):
            x, y = rng.uniform(-.5, .5), rng.uniform(-.55, .75)
            before = set(bm.faces)
            ico(bm, (x, y, .72 + rng.uniform(0, .05)), rng.uniform(.06, .09), sub=1, squash=(1, 1, .9), jitter=.03, rng=rng)
            m = rng.randrange(3)
            for f in set(bm.faces) - before:
                f.material_index = m
    b.add("Produce", [produce], ["coral", "yellow", "foliage_mid"], parent="Cart_Bed")
    b.place()


@asset("INTERIOR_11", "Restaurant Table", "interiors", pose="round pedestal table, set for two", notes={"parts": "Top, Pedestal, Base, Tablecloth, Plates, Glasses, Candle, Menu_Stand"})
def restaurant_table(b):
    b.add("Base", [lambda bm: lathe(bm, [(0, 0), (.3, 0), (.32, .02), (.3, .04), (.1, .08), (0, .08)], n=16)], "steel", bevel=.0)
    b.add("Pedestal", [lambda bm: lathe(bm, [(0, .08), (.06, .08), (.045, .4), (.045, .66), (.07, .7), (0, .7)], n=12)], "steel")
    b.add("Top", [lambda bm: lathe(bm, [(0, .69), (.4, .69), (.42, .715), (.4, .74), (0, .74)], n=24)], "wood_light", bevel=.004)
    b.add("Tablecloth", [lambda bm: lathe(bm, [(0, .745), (.36, .745), (.38, .74), (.37, .6), (.34, .62), (.3, .6), (.26, .62), (.2, .59), (0, .59)], n=24)], "offwhite", parent="Top")
    b.add("Plates", [lambda bm: [lathe(bm, [(0, .748), (.1, .748), (.12, .762), (.1, .752), (0, .752)], c=(0, sy * .22, 0), n=16) for sy in (-1, 1)]], "safety_white", parent="Top")
    b.add("Glasses", [lambda bm: [lathe(bm, [(.0, .748), (.03, .748), (.035, .82), (.0, .82)], c=(sx * .22, sy * .08, 0), n=10) for sx in (-1, 1) for sy in (-1, 1)]], "glass", parent="Top")
    b.add("Candle", [lambda bm: [cyl(bm, (0, 0, .748), (0, 0, .8), .025, n=8)]], "yellow", parent="Top")
    b.add("Menu_Stand", [lambda bm: [beam(bm, (.12, 0, .75), (.12, .0, .86), .1, .006, .1, .006), cb(bm, .12, .0, .752, .12, .05, .01)]], "wood_dark", parent="Top")
    b.place()


@asset("INTERIOR_12", "Outdoor Umbrella", "interiors", pose="open parasol on weighted base", notes={"parts": "Base, Pole, Canopy (8 alternating panels), Ribs, Finial, Crank"})
def outdoor_umbrella(b):
    b.add("Base", [lambda bm: lathe(bm, [(0, 0), (.3, 0), (.32, .04), (.28, .1), (.08, .12), (0, .12)], n=12)], "concrete", bevel=.0)
    b.add("Pole", [lambda bm: cyl(bm, (0, 0, .12), (0, 0, 2.4), .028, .022, n=10)], "metal_gal")

    def canopy(bm):
        n = 8
        for i in range(n):
            a0, a1 = 2 * math.pi * i / n, 2 * math.pi * (i + 1) / n
            def panel(m, a0=a0, a1=a1):
                rows = []
                for r, z in ((.0, 2.62), (.5, 2.55), (1.0, 2.42), (1.45, 2.22), (1.5, 2.2)):
                    rows.append([m.verts.new((math.cos(a0) * r, math.sin(a0) * r, z)), m.verts.new((math.cos(a1) * r, math.sin(a1) * r, z)),
                                 m.verts.new((math.cos(a1) * r, math.sin(a1) * r, z - .018)), m.verts.new((math.cos(a0) * r, math.sin(a0) * r, z - .018))])
                skin(m, rows)
            with_mat(i % 2, panel)(bm)
    b.add("Canopy", [canopy], ["coral", "offwhite"], parent="Pole")

    def ribs(bm):
        for i in range(8):
            a = 2 * math.pi * i / 8
            pts = [(math.cos(a) * r, math.sin(a) * r, z - .02) for r, z in ((.0, 2.6), (.5, 2.53), (1.0, 2.4), (1.45, 2.2))]
            tube(bm, pts, [.012] * 4, n=4)
            tube(bm, [(math.cos(a) * .15, math.sin(a) * .15, 2.2), (math.cos(a) * .8, math.sin(a) * .8, 2.34)], [.008, .008], n=4)
    b.add("Ribs", [ribs], "metal_gal", parent="Pole")
    b.add("Finial", [lambda bm: [lathe(bm, [(0, 2.62), (.03, 2.62), (.02, 2.7), (0, 2.72)], n=8)]], "wood_dark", parent="Pole")
    b.add("Crank", [lambda bm: [cyl(bm, (0, 0, 1.2), (0, 0, 1.3), .04, n=8), cyl(bm, (.04, 0, 1.25), (.14, 0, 1.25), .01, n=6)]], "wood_dark", parent="Pole")
    b.place()


@asset("INTERIOR_13", "Cash Register", "interiors", pose="counter-top register, screen faces +Y", notes={"parts": "Body, Keys, Drawer (slides +Y), Screen (tilt pivot), Screen_Arm, Receipt_Roll"})
def cash_register(b):
    b.add("Body", [lambda bm: frustum(bm, 0, .16, 0, 0, .21, .2, .2, .17)], "plastic_black", bevel=.01)
    b.add("Keys", [lambda bm: [cb(bm, -.14 + (i % 6) * .055, .02 + (i // 6) * -.0 - (i // 6) * .06 + .06, .165, .042, .042, .014) for i in range(18)]], "plastic_white", parent="Body", bevel=.003)
    b.add("Drawer", [lambda bm: cb(bm, 0, .21, .05, .38, .06, .09)], "steel", pivot=(0, .2, .05), parent="Body", bevel=.004)
    b.add("Screen_Arm", [lambda bm: [cyl(bm, (0, -.1, .16), (0, -.1, .3), .018, n=8)]], "steel", parent="Body")
    b.add("Screen", [lambda bm: [cb(bm, 0, -.1, .36, .26, .025, .17), cb(bm, 0, -.085, .36, .23, .004, .14)]], ["plastic_black"], pivot=(0, -.1, .3), parent="Screen_Arm", bevel=.004)
    b.add("Screen_Face", [lambda bm: cb(bm, 0, -.084, .36, .23, .004, .14)], "screen_lit", parent="Screen")
    b.add("Receipt_Roll", [lambda bm: cyl(bm, (-.07, -.12, .2), (.07, -.12, .2), .035, n=12)], "safety_white", parent="Body")
    b.place()


@asset("INTERIOR_14", "Display Cabinet", "interiors", pose="glass display cabinet, door on +Y face", notes={"parts": "Frame, Shelves, Glass_Sides, Door (hinged at left edge), Items, Light_Strip"})
def display_cabinet(b):
    b.add("Frame", [lambda bm: [cb(bm, sx * .45, sy * .2, .9, .05, .05, 1.8) for sx in (-1, 1) for sy in (-1, 1)] +
                       [cb(bm, 0, 0, .06, .95, .45, .12), cb(bm, 0, 0, 1.78, .95, .45, .05)]], "wood_dark", bevel=.006)
    b.add("Shelves", [lambda bm: [cb(bm, 0, 0, .35 + i * .42, .84, .36, .015) for i in range(4)]], "glass", parent="Frame")
    b.add("Glass_Sides", [lambda bm: [cb(bm, sx * .44, 0, .95, .01, .36, 1.62) for sx in (-1, 1)] + [cb(bm, 0, -.19, .95, .84, .01, 1.62)]], "glass", parent="Frame")
    b.add("Door", [lambda bm: [cb(bm, 0, .2, .95, .84, .012, 1.6), cb(bm, .38, .21, .95, .02, .015, .2)]], ["glass"], pivot=(-.42, .2, .95), parent="Frame")
    b.add("Door_Handle", [lambda bm: cb(bm, .36, .225, .95, .018, .03, .22)], "chrome", parent="Door", bevel=.003)
    rng = random.Random(14)

    def items(bm):
        for i in range(4):
            z = .36 + i * .42
            for k in range(3):
                x = -.28 + k * .28 + rng.uniform(-.04, .04)
                m = rng.randrange(3)
                before = set(bm.faces)
                lathe(bm, [(0, z), (.05, z), (.07 + rng.uniform(0, .03), z + .07), (.04, z + .14), (.03, z + .2 + rng.uniform(0, .06)), (.045, z + .22), (0, z + .22)], c=(x, rng.uniform(-.06, .06), 0), n=10)
                for f in set(bm.faces) - before:
                    f.material_index = m
    b.add("Items", [items], ["coral", "fabric_blue", "yellow"], parent="Shelves")
    b.add("Light_Strip", [lambda bm: cb(bm, 0, -.17, 1.74, .8, .02, .02)], "screen_lit", parent="Frame")
    b.place()




# ==========================================================================
# CATEGORY E - ACCESSORIES (12).  Ground y=0 (resting pose), front = +Y.  grip / attachment points are in metadata "attachment_points_file_xyz"
# ==========================================================================
def disc_x(bm, c, r, w, n=12):
    cyl(bm, (c[0] - w / 2, c[1], c[2]), (c[0] + w / 2, c[1], c[2]), r, n=n)


@asset("ACCESSORY_01", "Smartphone", "accessories", pose="lying flat, screen up", notes={"parts": "Body, Screen, Camera_Bump, Lenses, Buttons", "grip": "hand_grip / thumb_rest in metadata"})
def smartphone(b):
    b.add("Body", [lambda bm: cb(bm, 0, 0, .004, .072, .15, .008)], "plastic_black", bevel=.004)
    b.add("Screen", [lambda bm: cb(bm, 0, 0, .0085, .066, .141, .001)], "screen_lit", parent="Body")
    b.add("Notch", [lambda bm: cb(bm, 0, .062, .0092, .02, .006, .0006)], "plastic_black", parent="Body")
    b.add("Camera_Bump", [lambda bm: cb(bm, -.016, .052, -.0005, .032, .032, .002)], "plastic_black", parent="Body", bevel=.003)
    b.add("Lenses", [lambda bm: [cyl(bm, (-.024 + .016 * (i % 2), .044 + .016 * (i // 2), -.0006), (-.024 + .016 * (i % 2), .044 + .016 * (i // 2), -.0036), .006, n=10) for i in range(3)]], "chrome", parent="Camera_Bump")
    b.add("Buttons", [lambda bm: [cb(bm, .0375, y, .004, .003, .018, .004) for y in (.03, .0)] + [cb(bm, -.0375, .02, .004, .003, .03, .004)]], "steel", parent="Body", bevel=.001)
    b.point("hand_grip", (0, -.03, .004))
    b.point("thumb_rest", (.02, -.02, .0085))
    b.place()


@asset("ACCESSORY_02", "Backpack", "accessories", pose="standing upright, front +Y", notes={"parts": "Body, Front_Pocket, Top_Flap, Straps, Side_Pockets, Handle, Zip_Pulls", "grip": "carry_handle; shoulder_strap_L/R"})
def backpack(b):
    prof = [(-.18, .0, .3, .15), (-.18, .02, .3, .15), (-.18, .0, .3, .15)]
    rings = [(0.0, 0, 0, .16, .09), (.04, 0, 0, .20, .115), (.30, 0, .0, .21, .13), (.50, 0, 0, .19, .115), (.52, 0, 0, .17, .10)]
    b.add("Body", [{"rings": rings, "n": 8, "axis": "z"}], "canvas_green", bevel=.01, pivot=(0, 0, 0))
    b.add("Top_Flap", [lambda bm: rbox(bm, -.19, .19, -.13, .16, .43, .54, .96)], "canvas_green", parent="Body", bevel=.012)
    b.add("Front_Pocket", [lambda bm: rbox(bm, -.16, .16, .09, .19, .06, .33, .93)], "canvas_red", parent="Body", bevel=.012)
    b.add("Side_Pockets", [lambda bm: [rbox(bm, sx * .2 - .045, sx * .2 + .045, -.04, .08, .03, .26, .9) for sx in (-1, 1)]], "canvas_red", parent="Body", bevel=.01)
    b.add("Straps", [lambda bm: [tube(bm, [(sx * .1, -.1, .46), (sx * .115, -.145, .34), (sx * .12, -.15, .2), (sx * .09, -.12, .05)], [(.03, .008)] * 4, n=4) for sx in (-1, 1)]], "rubber", parent="Body", bevel=.0)
    b.add("Handle", [lambda bm: tube(bm, [(-.05, -.02, .55), (-.05, -.02, .6), (.05, -.02, .6), (.05, -.02, .55)], [.011] * 4, n=5)], "rubber", parent="Body")
    b.add("Zip_Pulls", [lambda bm: [cb(bm, x, .195, z, .012, .006, .035) for x, z in ((.0, .27), (.0, .46))]], "chrome", parent="Body", bevel=.002)
    b.point("carry_handle", (0, -.02, .6))
    b.point("shoulder_strap_L", (-.1, -.12, .4))
    b.point("shoulder_strap_R", (.1, -.12, .4))
    b.place()


@asset("ACCESSORY_03", "Handbag", "accessories", pose="standing, flap closed", notes={"parts": "Body, Flap, Handles, Clasp, Base_Studs", "grip": "handle_grip at the top of the handles"})
def handbag(b):
    b.add("Body", [lambda bm: frustum(bm, .01, .22, 0, 0, .15, .06, .17, .075)], "leather", bevel=.012)
    b.add("Flap", [lambda bm: gprism(bm, .19, .225, [(-.17, -.07), (.17, -.07), (.17, .085), (-.17, .085)], [(-.165, -.065), (.165, -.065), (.165, .09), (-.165, .09)])], "leather_dark", parent="Body", bevel=.006)
    b.add("Handles", [lambda bm: [tube(bm, arc_pts((0, sy * .07, .22), .11, 0, 180, 10, plane="xz"), [.01] * 10, n=6) for sy in (-1, 1)]], "leather_dark", parent="Body")
    b.add("Clasp", [lambda bm: cb(bm, 0, .095, .2, .04, .01, .03)], "yellow", parent="Flap", bevel=.003)
    b.add("Base_Studs", [lambda bm: [cyl(bm, (x, y, 0), (x, y, .012), .01, n=6) for x in (-.11, .11) for y in (-.04, .04)]], "yellow", parent="Body")
    b.point("handle_grip", (0, 0, .33))
    b.place()


@asset("ACCESSORY_04", "Suitcase", "accessories", pose="standing on wheels, handle retracted... extended 0.3 m", notes={"parts": "Shell, Ribs, Handle_Extended, Wheels, Carry_Handle, Latches", "grip": "telescopic_handle_grip, carry_handle"})
def suitcase(b):
    b.add("Shell", [lambda bm: [cb(bm, 0, 0, .35, .46, .27, .64), ]], "blue_steel", bevel=.03)
    b.add("Ribs", [lambda bm: [cb(bm, x, .14, .35, .018, .014, .56) for x in (-.15, -.05, .05, .15)] + [cb(bm, x, -.14, .35, .018, .014, .56) for x in (-.15, -.05, .05, .15)]], "blue_steel", parent="Shell", bevel=.004)
    b.add("Seam", [lambda bm: cb(bm, 0, 0, .35, .47, .275, .012)], "plastic_black", parent="Shell")
    b.add("Latches", [lambda bm: [cb(bm, sx * .12, 0, .35, .06, .28, .035) for sx in (-1, 1)]], "chrome", parent="Shell", bevel=.003)
    b.add("Handle_Extended", [lambda bm: [cyl(bm, (sx * .1, -.12, .66), (sx * .1, -.12, .98), .008, n=6) for sx in (-1, 1)] + [cb(bm, 0, -.12, .99, .24, .03, .028)]], "chrome", parent="Shell", bevel=.003)
    b.add("Carry_Handle", [lambda bm: cb(bm, 0, 0, .675, .14, .05, .025)], "plastic_black", parent="Shell", bevel=.006)
    b.add("Wheels", [lambda bm: [x for sx in (-1, 1) for x in (cyl(bm, (sx * .18 - .015, -.1, .04), (sx * .18 + .015, -.1, .04), .04, n=10), cb(bm, sx * .18, -.1, .08, .05, .06, .03))]], "rubber", parent="Shell")
    b.point("telescopic_handle_grip", (0, -.12, .99))
    b.point("carry_handle", (0, 0, .675))
    b.place()


@asset("ACCESSORY_05", "Umbrella", "accessories", pose="open umbrella standing on its handle tip", notes={"parts": "Canopy (8 panels), Ribs, Shaft, Handle, Tip", "grip": "hook_grip"})
def umbrella(b):
    def canopy(bm):
        for i in range(8):
            a0, a1 = 2 * math.pi * i / 8, 2 * math.pi * (i + 1) / 8

            def panel(m, a0=a0, a1=a1):
                rows = []
                for r, z in ((.0, 1.0), (.25, .965), (.5, .89), (.72, .78), (.76, .77)):
                    rows.append([m.verts.new((math.cos(a0) * r, math.sin(a0) * r, z)), m.verts.new((math.cos(a1) * r, math.sin(a1) * r, z)),
                                 m.verts.new((math.cos(a1) * r, math.sin(a1) * r, z - .008)), m.verts.new((math.cos(a0) * r, math.sin(a0) * r, z - .008))])
                skin(m, rows)
            with_mat(i % 2, panel)(bm)
    b.add("Canopy", [canopy], ["fabric_blue", "offwhite"], pivot=(0, 0, .8))
    b.add("Shaft", [lambda bm: cyl(bm, (0, 0, .12), (0, 0, 1.02), .007, n=8)], "chrome", parent="Canopy")

    def ribs(bm):
        for i in range(8):
            a = 2 * math.pi * i / 8
            tube(bm, [(math.cos(a) * r, math.sin(a) * r, z - .01) for r, z in ((.0, 1.0), (.25, .965), (.5, .89), (.72, .78))], [.004] * 4, n=4)
            tube(bm, [(math.cos(a) * .05, math.sin(a) * .05, .82), (math.cos(a) * .35, math.sin(a) * .35, .9)], [.003, .003], n=4)
    b.add("Ribs", [ribs], "steel", parent="Canopy")
    b.add("Handle", [lambda bm: tube(bm, [(0, 0, .13)] + arc_pts((.04, 0, .13), .04, 180, 360 + 20, 9, plane="xz") + [(.08 + .005, 0, .13 + .0)], [.013] * 11, n=8)], "wood_dark", parent="Canopy")
    b.add("Tip", [lambda bm: cyl(bm, (0, 0, 1.0), (0, 0, 1.07), .01, .003, n=6)], "chrome", parent="Canopy")
    b.point("hook_grip", (.04, 0, .15))
    b.place()


@asset("ACCESSORY_06", "Hard Hat", "accessories", pose="resting on brim, upright", notes={"parts": "Shell, Brim, Ridges, Suspension, Adjust_Knob, Badge", "grip": "wear_point (crown centre) in metadata"})
def hard_hat(b):
    def shell(bm):
        lathe(bm, [(0, .15), (.07, .148), (.12, .13), (.15, .09), (.16, .05), (.17, .03), (.17, .015), (0, .015)], n=18, scale_xy=(1, 1.12))
    b.add("Shell", [shell], "yellow", bevel=.004, smooth=False)
    b.add("Brim", [lambda bm: [lathe(bm, [(.17, .016), (.19, .01), (.192, .0), (.17, .0)], n=18, scale_xy=(1, 1.12)), cb(bm, 0, .2, .008, .14, .07, .012)]], "yellow", parent="Shell", bevel=.003)
    prof = [(0, .15), (.07, .148), (.12, .13), (.15, .09), (.16, .05), (.17, .03)]

    def hh(r):
        for (r0, h0), (r1, h1) in zip(prof, prof[1:]):
            if r0 <= r <= r1:
                return h0 + (h1 - h0) * (r - r0) / (r1 - r0)
        return .03

    def ridges(bm):
        for sx in (-.05, 0, .05):
            pts = []
            for k in range(13):
                y = -.17 + .34 * k / 12
                r = math.hypot(sx, y / 1.12)
                pts.append((sx, y, hh(min(r, .169)) + .003))
            tube(bm, pts, [.007] * 13, n=4)
    b.add("Ridges", [ridges], "yellow", parent="Shell")
    b.add("Suspension", [lambda bm: [torus(bm, (0, 0, .045), .15, .004, n=18, m=5, squash=1.0)] + [tube(bm, arc_pts((0, 0, .03), .15, 0, 180, 7, plane="xz"), [.004] * 7, n=4)]], "offwhite", parent="Shell")
    b.add("Adjust_Knob", [lambda bm: cyl(bm, (0, -.19, .06), (0, -.22, .06), .018, n=8)], "plastic_black", parent="Shell", bevel=.002)
    b.add("Badge", [lambda bm: cb(bm, 0, .185, .1, .04, .006, .025)], "offwhite", parent="Shell")
    b.point("wear_point", (0, 0, .15))
    b.place()


@asset("ACCESSORY_07", "Safety Vest", "accessories", pose="open-front vest hanging in worn shape (torso-shaped), hem at y=0", notes={"parts": "Back, Front_Left, Front_Right, Shoulder_Straps, Reflective_Bands, Zip_Placket, Side_Bands", "grip": "collar_point"})
def vest(b):
    RX, RY, H = .2, .115, .6

    def rp(th, z, off=0.0):
        t = math.radians(th)
        return (math.sin(t) * (RX + off), math.cos(t) * (RY + off), z)

    def ztop(th, front):
        a = abs(((th + 180) % 360) - 180)         # 0 = front, 180 = back
        return H * (1 - .22 * max(0.0, 1 - a / 70.0)) if front else H

    def strip(bm, th0, th1, front, thick=.008, nz=5, nth=7):
        rows = []
        for i in range(nz):
            row_o, row_i = [], []
            for k in range(nth):
                th = th0 + (th1 - th0) * k / (nth - 1)
                z = ztop(th, front) * i / (nz - 1)
                row_o.append(bm.verts.new(rp(th, z, thick)))
                row_i.append(bm.verts.new(rp(th, z, 0.0)))
            rows.append(row_o + row_i[::-1])
        skin(bm, rows)
    b.add("Back", [lambda bm: strip(bm, 95, 265, False)], "hiviz_orange")
    b.add("Front_Left", [lambda bm: strip(bm, -95, -14, True)], "hiviz_orange")
    b.add("Front_Right", [lambda bm: strip(bm, 14, 95, True)], "hiviz_orange")

    def straps(bm):
        for sx in (-1, 1):
            f = rp(sx * 58, ztop(sx * 58, True) - .005, .004)
            bk = rp(sx * 122, H - .005, .004)
            mid = ((f[0] + bk[0]) / 2 + sx * .01, (f[1] + bk[1]) / 2, H + .012)
            beam(bm, f, mid, .055, .012)
            beam(bm, mid, bk, .055, .012)
    b.add("Shoulder_Straps", [straps], "hiviz_orange", parent="Back")

    def bands(bm):
        for sx in (-1, 1):
            for th in (sx * 34,):
                pts = [rp(th, z, .0105) for z in (.07, .3, .5)]
                for (x0, y0, z0), (x1, y1, z1) in zip(pts, pts[1:]):
                    beam(bm, (x0, y0, z0), (x1, y1, z1), .05, .004, up=(0, 1, 0) if False else (0, 0, 1))
        for z in (.12, .33):
            for th0 in range(100, 260, 20):
                a, c = rp(th0, z, .0105), rp(th0 + 20, z, .0105)
                beam(bm, a, c, .004, .05, up=(0, 0, 1))
    b.add("Reflective_Bands", [bands], "reflective", parent="Back")
    b.add("Zip_Placket", [lambda bm: [beam(bm, rp(sx * 14, .02, .01), rp(sx * 14, .42, .01), .008, .008) for sx in (-1, 1)]], "plastic_black", parent="Front_Left")
    b.point("collar_point", (0, 0, H))
    b.place()


@asset("ACCESSORY_08", "Flashlight", "accessories", pose="standing on tail cap", notes={"parts": "Body, Grip_Rings, Head, Lens (emissive), Switch, Tail_Cap, Lanyard", "grip": "grip_centre"})
def flashlight(b):
    b.add("Body", [lambda bm: lathe(bm, [(0, 0), (.02, 0), (.022, .01), (.021, .12), (.027, .15), (0, .15)], n=12)], "plastic_black", bevel=.0)
    b.add("Grip_Rings", [lambda bm: [torus(bm, (0, 0, .03 + .018 * i), .0215, .0035, n=12, m=5) for i in range(5)]], "rubber", parent="Body")
    b.add("Head", [lambda bm: lathe(bm, [(.027, .15), (.04, .185), (.05, .21), (.05, .22), (.0, .22), (.0, .15)], n=14)], "silver", parent="Body")
    b.add("Lens", [lambda bm: lathe(bm, [(0, .218), (.043, .218), (.043, .224), (0, .224)], n=14)], "screen_lit", parent="Head")
    b.add("Switch", [lambda bm: cb(bm, 0, .027, .1, .012, .01, .022)], "red_paint", parent="Body", bevel=.002)
    b.add("Tail_Cap", [lambda bm: lathe(bm, [(.0, -.0), (.021, .0), (.023, .015), (0, .015)], n=12)], "steel", parent="Body")
    b.add("Lanyard", [lambda bm: tube(bm, [(0, -.0, .01), (.03, 0, .0), (.05, 0, -0.0) , (.04, 0, .03), (.02, 0, .02)], [.0035] * 5, n=4)], "coral", parent="Tail_Cap")
    b.point("grip_centre", (0, 0, .07))
    b.place()


@asset("ACCESSORY_09", "Binoculars", "accessories", pose="lying on its barrels, lenses toward +Y", notes={"parts": "Barrel_L/R, Bridge, Focus_Wheel, Eyecups, Objective_Lenses, Strap_Lugs", "grip": "grip_L / grip_R"})
def binoculars(b):
    for nm, sx in (("Barrel_L", -1), ("Barrel_R", 1)):
        def barrel_y(bm, sx=sx):
            tmp = bmesh.new()
            lathe(tmp, [(0, -.075), (.026, -.075), (.03, -.05), (.03, 0), (.034, .03), (.034, .09), (.04, .11), (.04, .14), (0, .14)], n=14)
            rotate_bm(tmp, tmp.verts, "X", -90)
            bmesh.ops.translate(tmp, verts=tmp.verts, vec=(sx * .045, 0, .04))
            merge_bm(bm, tmp)
        b.add(nm, [barrel_y], "plastic_black", pivot=(sx * .045, 0, .04), bevel=.0)
    b.add("Bridge", [lambda bm: [cb(bm, 0, -.01, .045, .06, .05, .02), cb(bm, 0, .0, .068, .036, .02, .012)]], "plastic_black", parent="Barrel_L", bevel=.003)
    b.add("Focus_Wheel", [lambda bm: cyl(bm, (0, .0, .07), (0, .0, .08), .014, n=10)], "rubber", parent="Bridge", bevel=.0)
    b.add("Objective_Lenses", [lambda bm: [cyl(bm, (sx * .045, .136, .04), (sx * .045, .141, .04), .034, n=14) for sx in (-1, 1)]], "glass", parent="Barrel_L")
    b.add("Eyecups", [lambda bm: [torus(bm, (sx * .045, -.082, .04), .02, .008, n=12, m=5, axis="y") for sx in (-1, 1)]], "rubber", parent="Barrel_L")
    b.add("Strap_Lugs", [lambda bm: [cb(bm, sx * .088, .0, .045, .008, .02, .016) for sx in (-1, 1)]], "steel", parent="Barrel_L", bevel=.002)
    b.point("grip_L", (-.07, .02, .04))
    b.point("grip_R", (.07, .02, .04))
    b.place()


@asset("ACCESSORY_10", "Telescope", "accessories", pose="tripod-mounted refractor telescope pointing up-and-forward", notes={"parts": "Tripod_Legs, Mount_Head, Tube (tilt pivot), Dew_Shield, Finder_Scope, Eyepiece, Focuser, Tube_Rings", "grip": "focus_knob"})
def telescope(b):
    def legs(bm):
        for i in range(3):
            a = 2 * math.pi * i / 3 + .5
            tube(bm, [(0, 0, 1.0), (math.cos(a) * .3, math.sin(a) * .3, .5), (math.cos(a) * .6, math.sin(a) * .6, .0)], [.016, .014, .012], n=6)
            cyl(bm, (math.cos(a) * .6, math.sin(a) * .6, 0), (math.cos(a) * .6, math.sin(a) * .6, .03), .02, n=6)
    b.add("Tripod_Legs", [legs], "wood_dark")
    b.add("Mount_Head", [lambda bm: [cb(bm, 0, 0, 1.02, .12, .1, .08), cyl(bm, (-.08, 0, 1.08), (.08, 0, 1.08), .028, n=10), cyl(bm, (0, 0, .99), (0, 0, 1.06), .05, n=10)]], "steel", parent="Tripod_Legs", bevel=.003)
    tilt = 35

    def tube_fn(bm):
        tmp = bmesh.new()
        lathe(tmp, [(.0, -.3), (.04, -.3), (.04, .0), (.05, .02), (.05, .5), (.056, .52), (.056, .75), (0, .75)], n=18)
        merge_bm(bm, tmp)
        rotate_bm(bm, bm.verts, "X", -(90 - tilt))
        bmesh.ops.translate(bm, verts=bm.verts, vec=(0, 0, 1.12))
    b.add("Tube", [tube_fn], "safety_white", parent="Mount_Head", pivot=(0, 0, 1.12), bevel=.0)

    base = Vector((0, 0, 1.12))
    a = math.radians(90 - tilt)
    axis = Vector((0, math.sin(a), math.cos(a)))
    side = Vector((1, 0, 0))
    upv = axis.cross(side)

    def at(t, off=(0, 0, 0)):
        return base + axis * t + side * off[0] + upv * off[1]
    b.add("Dew_Shield", [lambda bm: cyl(bm, at(.68), at(.88), .066, .07, n=18, cap0=False, cap1=False)], "plastic_black", parent="Tube", bevel=.0)
    b.add("Tube_Rings", [lambda bm: [cyl(bm, at(t), at(t + .04), .066, n=14) for t in (.1, .42)]], "steel", parent="Tube")
    b.add("Finder_Scope", [lambda bm: [cyl(bm, at(.2, (0, .09)), at(.45, (0, .09)), .017, n=10), cb(bm, *at(.2, (0, .06)), .02, .02, .02), cb(bm, *at(.42, (0, .06)), .02, .02, .02)]], "plastic_black", parent="Tube", bevel=.002)
    b.add("Focuser", [lambda bm: cyl(bm, at(-.34), at(-.2), .035, n=12)], "steel", parent="Tube")
    b.add("Eyepiece", [lambda bm: cyl(bm, at(-.42), at(-.33), .018, .022, n=12)], "plastic_black", parent="Tube")
    b.add("Focus_Knob", [lambda bm: [cyl(bm, at(-.27, (sx * .04, 0)), at(-.27, (sx * .06, 0)), .016, n=8) for sx in (-1, 1)]], "rubber", parent="Tube")
    b.point("focus_knob", tuple(at(-.27, (.05, 0))))
    b.place()


@asset("ACCESSORY_11", "First-Aid Kit", "accessories", pose="closed case on ground", notes={"parts": "Case, Lid, Cross, Latches, Handle, Corner_Guards", "grip": "carry_handle"})
def first_aid(b):
    b.add("Case", [lambda bm: cb(bm, 0, 0, .09, .3, .12, .16)], "med_green", bevel=.01)
    b.add("Lid", [lambda bm: cb(bm, 0, 0, .185, .31, .13, .03)], "med_green", pivot=(0, -.06, .17), parent="Case", bevel=.008)
    b.add("Cross", [lambda bm: [cb(bm, 0, .0, .2, .03, .075, .004), cb(bm, 0, .0, .2, .09, .025, .004)]], "offwhite", parent="Lid")
    b.add("Cross_Front", [lambda bm: [cb(bm, 0, .064, .09, .06, .004, .016), cb(bm, 0, .064, .09, .016, .004, .06)]], "offwhite", parent="Case")
    b.add("Latches", [lambda bm: [cb(bm, sx * .09, .068, .15, .045, .014, .06) for sx in (-1, 1)]], "chrome", parent="Case", bevel=.003)
    b.add("Handle", [lambda bm: tube(bm, [(-.06, 0, .2), (-.06, 0, .24), (.06, 0, .24), (.06, 0, .2)], [.008] * 4, n=6)], "plastic_black", parent="Lid")
    b.add("Corner_Guards", [lambda bm: [cb(bm, sx * .148, sy * .058, .02, .02, .02, .04) for sx in (-1, 1) for sy in (-1, 1)]], "plastic_black", parent="Case", bevel=.003)
    b.point("carry_handle", (0, 0, .24))
    b.place()


@asset("ACCESSORY_12", "Handheld Radio", "accessories", pose="standing on its base", notes={"parts": "Body, Antenna, Display, Keys, Knobs, PTT_Button, Speaker_Grille, Belt_Clip", "grip": "grip_centre"})
def radio(b):
    b.add("Body", [lambda bm: frustum(bm, 0, .13, 0, 0, .029, .019, .027, .017, n=4)], "plastic_black", bevel=.006)
    b.add("Antenna", [lambda bm: tube(bm, [(.015, 0, .13), (.016, 0, .2), (.019, 0, .3)], [.007, .006, .004], n=6)], "rubber", parent="Body")
    b.add("Display", [lambda bm: cb(bm, 0, .0185, .105, .03, .003, .02)], "screen_lit", parent="Body")
    b.add("Keys", [lambda bm: [cb(bm, -.015 + i * .015, .019, .075 - j * .015, .011, .003, .009) for i in range(3) for j in range(3)]], "plastic_white", parent="Body")
    b.add("Knobs", [lambda bm: [cyl(bm, (-.012, 0, .13), (-.012, 0, .145), .008, n=8), cyl(bm, (.0, 0, .13), (.0, 0, .138), .006, n=8)]], "red_paint", parent="Body")
    b.add("PTT_Button", [lambda bm: cb(bm, -.03, .0, .095, .008, .02, .04)], "red_paint", parent="Body", bevel=.002)
    b.add("Speaker_Grille", [lambda bm: [cb(bm, 0, .0188, .115 + k * .0, .0, .0, .0) for k in range(0)] + [cb(bm, 0, .0185, .045 + k * .009, .03, .003, .003) for k in range(5)]], "rubber", parent="Body")
    b.add("Belt_Clip", [lambda bm: cb(bm, 0, -.021, .06, .02, .004, .08)], "steel", parent="Body", bevel=.001)
    b.point("grip_centre", (0, 0, .07))
    b.place()




# ==========================================================================
# CATEGORY F - EMERGENCY / RESCUE (9).  Ground y=0, front = +Y
# ==========================================================================
@asset("RESCUE_01", "Stretcher", "emergency", pose="flat on ground, head toward -Y", notes={"parts": "Rails, Bed, Handles (4), Cross_Bars, Straps, Feet", "grip": "handle_head_L/R, handle_foot_L/R"})
def stretcher(b):
    b.add("Rails", [lambda bm: [cyl(bm, (sx * .3, -1.0, .13), (sx * .3, 1.0, .13), .014, n=8) for sx in (-1, 1)]], "metal_gal")
    b.add("Cross_Bars", [lambda bm: [cyl(bm, (-.3, y, .13), (.3, y, .13), .011, n=6) for y in (-.7, -.2, .2, .7)]], "metal_gal", parent="Rails")
    b.add("Bed", [lambda bm: cb(bm, 0, 0, .135, .58, 1.86, .012)], "canvas_green", parent="Rails", bevel=.003)
    b.add("Handles", [lambda bm: [x for sx in (-1, 1) for sy in (-1, 1) for x in (cyl(bm, (sx * .3, sy * 1.0, .13), (sx * .3, sy * 1.2, .13), .017, n=8), cyl(bm, (sx * .3, sy * 1.0, .13), (sx * .3, sy * 1.0, .0), .01, n=6))]], "rubber", parent="Rails")
    b.add("Feet", [lambda bm: [cb(bm, sx * .3, sy * .5, .03, .05, .09, .06) for sx in (-1, 1) for sy in (-1, 1)] + [cyl(bm, (sx * .3, sy * .5, .13), (sx * .3, sy * .5, .06), .01, n=6) for sx in (-1, 1) for sy in (-1, 1)]], "rubber", parent="Rails", bevel=.004)
    b.add("Straps", [lambda bm: [cb(bm, 0, y, .146, .6, .06, .008) for y in (-.45, .0, .45)] + [cb(bm, 0, y, .15, .06, .07, .012) for y in (-.45, 0, .45)]], ["coral"], parent="Bed", bevel=.001)
    b.add("Head_Pad", [lambda bm: rbox(bm, -.12, .12, -.85, -.55, .141, .18, .85)], "offwhite", parent="Bed", bevel=.008)
    b.point("handle_head_L", (-.3, -1.1, .13)); b.point("handle_head_R", (.3, -1.1, .13))
    b.point("handle_foot_L", (-.3, 1.1, .13)); b.point("handle_foot_R", (.3, 1.1, .13))
    b.place()


@asset("RESCUE_02", "Rescue Ladder", "emergency", pose="extension ladder lying on the ground, hooks toward +Y", notes={"parts": "Rail_L, Rail_R, Rungs, Foot_Pads, Hooks, Extension_Lock", "grip": "rungs"})
def rescue_ladder(b):
    L = 3.2
    for nm, sx in (("Rail_L", -1), ("Rail_R", 1)):
        b.add(nm, [lambda bm, sx=sx: [cb(bm, sx * .22, 0, .03, .045, L, .06), cb(bm, sx * .22, 0, .062, .02, L, .005)]], "metal_gal", bevel=.004)
    b.add("Rungs", [lambda bm: [cyl(bm, (-.22, y, .03), (.22, y, .03), .014, n=8) for y in [-L / 2 + .15 + i * .28 for i in range(12)]]], "steel", parent="Rail_L")
    b.add("Foot_Pads", [lambda bm: [cb(bm, sx * .22, -L / 2 - .01, .025, .07, .06, .05) for sx in (-1, 1)]], "rubber", parent="Rail_L", bevel=.004)
    b.add("Hooks", [lambda bm: [x for sx in (-1, 1) for x in (cb(bm, sx * .22, L / 2 + .04, .03, .04, .09, .04), cb(bm, sx * .22, L / 2 + .08, .1, .04, .03, .14))]], "steel", parent="Rail_L", bevel=.003)
    b.add("Extension_Lock", [lambda bm: [cb(bm, sx * .22, .4, .075, .055, .1, .04) for sx in (-1, 1)]], "red_paint", parent="Rail_L", bevel=.004)
    b.point("rungs", (0, 0, .03))
    b.place()


@asset("RESCUE_03", "Portable Barricade", "emergency", pose="standing, panel faces +Y", notes={"parts": "Frame, Boards (striped), Legs (A-frame pivots), Reflectors, Lamp"})
def barricade(b):
    b.add("Frame", [lambda bm: [cb(bm, sx * .95, 0, .5, .05, .05, 1.0) for sx in (-1, 1)] + [cb(bm, 0, 0, .1, 1.9, .05, .05)]], "steel", bevel=.004)

    def board(z):
        def f(bm):
            n = 10
            for i in range(n):
                x0 = -.95 + 1.9 * i / n
                before = set(bm.faces)
                cb(bm, x0 + .095, 0, z, .19, .035, .2)
                for fc in set(bm.faces) - before:
                    fc.material_index = i % 2
        return f
    for nm, z in (("Board_Top", .88), ("Board_Mid", .62), ("Board_Low", .36)):
        b.add(nm, [board(z)], ["offwhite", "red_paint"], parent="Frame", bevel=.003)
    b.add("Reflectors", [lambda bm: [cyl(bm, (x, .02, .88), (x, .028, .88), .035, n=10) for x in (-.7, -.2, .3, .8)]], "reflective", parent="Frame")
    b.add("Legs_L", [lambda bm: [beam(bm, (-.85, 0, .95), (-.85, sy * .55, 0), .045, .045) for sy in (-1, 1)]], "steel", pivot=(-.85, 0, .95), parent="Frame", bevel=.002)
    b.add("Legs_R", [lambda bm: [beam(bm, (.85, 0, .95), (.85, sy * .55, 0), .045, .045) for sy in (-1, 1)]], "steel", pivot=(.85, 0, .95), parent="Frame", bevel=.002)
    b.add("Lamp", [lambda bm: [cyl(bm, (0, 0, 1.0), (0, 0, 1.06), .05, n=10), lathe(bm, [(0, 1.06), (.06, 1.06), (.05, 1.14), (.0, 1.16)], n=10)]], ["yellow"], parent="Frame")
    b.add("Lamp_Lens", [lambda bm: lathe(bm, [(0, 1.062), (.062, 1.062), (.052, 1.142), (.0, 1.162)], n=10)], "led_red", parent="Lamp") if False else None
    b.place()


@asset("RESCUE_04", "Warning Siren", "emergency", pose="pole-mounted four-horn siren on a weighted tripod", notes={"parts": "Tripod, Mast, Siren_Head, Horns (4), Beacon, Battery_Box", "note": "static model; no sound or animation"})
def siren(b):
    def tri(bm):
        for i in range(3):
            a = 2 * math.pi * i / 3
            tube(bm, [(0, 0, .9), (math.cos(a) * .25, math.sin(a) * .25, .45), (math.cos(a) * .5, math.sin(a) * .5, .02)], [.022, .02, .02], n=6)
    b.add("Tripod", [tri], "steel", bevel=0)
    b.add("Mast", [lambda bm: cyl(bm, (0, 0, .85), (0, 0, 1.9), .04, .035, n=10)], "metal_gal", parent="Tripod")
    b.add("Battery_Box", [lambda bm: cb(bm, 0, .1, .3, .3, .2, .3)], "med_red", parent="Tripod", bevel=.008) if False else None
    b.add("Siren_Head", [lambda bm: [cyl(bm, (0, 0, 1.78), (0, 0, 2.0), .12, n=12), cb(bm, 0, 0, 1.87, .08, .08, .2)]], "red_paint", parent="Mast", bevel=.004)

    def horns(bm):
        for i in range(4):
            a = math.pi / 2 * i
            d = Vector((math.cos(a), math.sin(a), 0))
            tmp = bmesh.new()
            lathe(tmp, [(.03, .0), (.05, .12), (.1, .24), (.17, .34), (.2, .36), (0, .36)], n=14, cap0=True)
            rotate_bm(tmp, tmp.verts, "Y", 90)
            rotate_bm(tmp, tmp.verts, "Z", math.degrees(a))
            bmesh.ops.translate(tmp, verts=tmp.verts, vec=d * .1 + Vector((0, 0, 1.9)))
            merge_bm(bm, tmp)
    b.add("Horns", [horns], "silver", parent="Siren_Head", bevel=0)
    b.add("Beacon", [lambda bm: lathe(bm, [(0, 2.0), (.07, 2.0), (.06, 2.14), (0, 2.18)], n=10)], "led_red", parent="Siren_Head")
    b.add("Battery_Box", [lambda bm: cb(bm, 0, 0, .12, .3, .2, .24)], "plastic_black", parent="Tripod", bevel=.01)
    b.place()


@asset("RESCUE_05", "Megaphone", "emergency", pose="resting on its handle and bell rim, mouth toward +Y", notes={"parts": "Horn, Rim, Body, Handle, Trigger, Mic_Port, Strap_Loop", "grip": "handle_grip, trigger_finger"})
def megaphone(b):
    def horn(bm):
        tmp = bmesh.new()
        lathe(tmp, [(.035, .0), (.04, .04), (.07, .14), (.12, .24), (.17, .34), (.175, .36), (.165, .36), (.03, .02)], n=16, cap0=True, cap1=False)
        rotate_bm(tmp, tmp.verts, "X", -90)
        bmesh.ops.translate(tmp, verts=tmp.verts, vec=(0, -.05, .24))
        merge_bm(bm, tmp)
    b.add("Horn", [horn], "hiviz_orange", bevel=0)
    b.add("Rim", [lambda bm: torus(bm, (0, .31, .24), .17, .01, n=18, m=5, axis="y")], "safety_white", parent="Horn")
    b.add("Body", [lambda bm: cb(bm, 0, -.1, .24, .1, .14, .12)], "plastic_black", parent="Horn", bevel=.012)
    b.add("Handle", [lambda bm: cb(bm, 0, -.08, .16, .045, .05, .13)], "plastic_black", parent="Body", bevel=.008)
    b.add("Trigger", [lambda bm: cb(bm, 0, -.03, .17, .02, .03, .05)], "red_paint", parent="Handle", pivot=(0, -.03, .2), bevel=.003)
    b.add("Mic_Port", [lambda bm: cyl(bm, (0, -.17, .24), (0, -.2, .24), .03, n=10)], "rubber", parent="Body")
    b.add("Strap_Loop", [lambda bm: torus(bm, (0, -.08, .3), .03, .005, n=10, m=4, axis="x")], "steel", parent="Body")
    b.point("handle_grip", (0, -.08, .17)); b.point("trigger_finger", (0, -.03, .17))
    b.place()


@asset("RESCUE_06", "Fire Extinguisher", "emergency", pose="standing, gauge faces +Y", notes={"parts": "Cylinder, Label, Valve_Head, Lever, Pin, Handle, Hose, Nozzle, Gauge", "grip": "carry_handle, lever_grip"})
def extinguisher(b):
    b.add("Cylinder", [lambda bm: lathe(bm, [(0, 0), (.06, 0), (.08, .02), (.08, .38), (.07, .44), (.03, .48), (0, .48)], n=14)], "red_paint", bevel=0)
    b.add("Label", [lambda bm: lathe(bm, [(.0805, .14), (.0805, .3)], n=14, cap0=False, cap1=False)], "offwhite", parent="Cylinder") if False else None
    b.add("Label", [lambda bm: [cb(bm, 0, .0805, .22, .09, .004, .13), cb(bm, 0, .082, .24, .04, .003, .04)]], ["offwhite"], parent="Cylinder")
    b.add("Valve_Head", [lambda bm: [cyl(bm, (0, 0, .46), (0, 0, .53), .035, n=10), cb(bm, 0, 0, .56, .1, .05, .05)]], "chrome", parent="Cylinder", bevel=.004)
    b.add("Handle", [lambda bm: cb(bm, 0, 0, .595, .16, .028, .018)], "red_paint", parent="Valve_Head", bevel=.004)
    b.add("Lever", [lambda bm: cb(bm, 0, .0, .545, .15, .02, .014)], "red_paint", pivot=(-.07, 0, .55), parent="Valve_Head", bevel=.003)
    b.add("Pin", [lambda bm: [cyl(bm, (.0, -.03, .57), (.0, .05, .57), .004, n=4), torus(bm, (.0, .06, .57), .015, .003, n=8, m=4, axis="x")]], "yellow", parent="Valve_Head")
    b.add("Gauge", [lambda bm: cyl(bm, (.03, .035, .56), (.03, .06, .56), .022, n=12)], "screen_lit", parent="Valve_Head")
    b.add("Hose", [lambda bm: tube(bm, [(-.05, 0, .55), (-.12, .0, .5), (-.14, 0, .38), (-.1, .0, .3), (-.1, .0, .25)], [.012] * 5, n=6)], "plastic_black", parent="Valve_Head")
    b.add("Nozzle", [lambda bm: cyl(bm, (-.1, 0, .25), (-.1, 0, .18), .012, .022, n=8)], "plastic_black", parent="Hose")
    b.point("carry_handle", (0, 0, .6)); b.point("lever_grip", (0, 0, .545))
    b.place()


@asset("RESCUE_07", "Flotation Ring", "emergency", pose="lying flat", notes={"parts": "Ring (8 alternating orange/white segments), Grab_Rope, Reflective_Tape, Rope_Toggles", "grip": "grab_rope_loop"})
def flotation_ring(b):
    R, r = .33, .07

    def ring(bm):
        n, m = 32, 8
        rows = []
        for i in range(n):
            a = 2 * math.pi * i / n
            rows.append([bm.verts.new(((R + r * math.cos(2 * math.pi * k / m)) * math.cos(a), (R + r * math.cos(2 * math.pi * k / m)) * math.sin(a), r + r * math.sin(2 * math.pi * k / m))) for k in range(m)])
        for i in range(n):
            for k in range(m):
                f = bm.faces.new((rows[i][k], rows[i][(k + 1) % m], rows[(i + 1) % n][(k + 1) % m], rows[(i + 1) % n][k]))
                f.material_index = (i // 4) % 2
    b.add("Ring", [ring], ["hiviz_orange", "offwhite"], bevel=0)

    def tape(bm):
        for i in (2, 6):
            a0 = math.radians((i * 4 + 1.0) * 360 / 32)
            for k in range(2):
                pass
        for i in (1, 3, 5, 7):
            a = math.radians((i * 4 + 2) * 360 / 32)
            cb_ang = a
            p = Vector((math.cos(a) * (R + r + .004), math.sin(a) * (R + r + .004), r))
            beam(bm, p - Vector((math.cos(a), math.sin(a), 0)) * .0, p + Vector((math.cos(a), math.sin(a), 0)) * .004, .06, .06, up=(0, 0, 1))
    b.add("Reflective_Tape", [tape], "reflective", parent="Ring")

    def rope(bm):
        pts = []
        for i in range(25):
            a = 2 * math.pi * i / 24
            pts.append((math.cos(a) * (R + r * 1.02 + .012), math.sin(a) * (R + r * 1.02 + .012), r + .012 * math.sin(a * 8) * 0 + .0))
        # looped scallops hanging outside the ring
        for k in range(4):
            a0 = 2 * math.pi * k / 4 + .3
            a1 = a0 + .9
            pts2 = [(math.cos(a0 + (a1 - a0) * t) * (R + r + .02 + .05 * math.sin(math.pi * t)), math.sin(a0 + (a1 - a0) * t) * (R + r + .02 + .05 * math.sin(math.pi * t)),
                     r - .045 * math.sin(math.pi * t)) for t in [j / 8 for j in range(9)]]
            tube(bm, pts2, [.007] * 9, n=5)
    b.add("Grab_Rope", [rope], "canvas", parent="Ring")
    b.add("Rope_Toggles", [lambda bm: [cb(bm, math.cos(2 * math.pi * k / 4 + .3) * (R + r + .02), math.sin(2 * math.pi * k / 4 + .3) * (R + r + .02), r, .02, .02, .02) for k in range(4)]], "wood_dark", parent="Ring", bevel=.003)
    b.point("grab_rope_loop", (R + r + .05, 0, r))
    b.place()


@asset("RESCUE_08", "Portable Floodlight", "emergency", pose="tripod floodlight, beam toward +Y", notes={"parts": "Tripod, Mast, Lamp_Head (tilt pivot), Lens_Grid (emissive), Handle, Battery_Pack, Cable", "grip": "carry_handle"})
def floodlight(b):
    def tri(bm):
        for i in range(3):
            a = 2 * math.pi * i / 3 + .5
            tube(bm, [(0, 0, 1.0), (math.cos(a) * .3, math.sin(a) * .3, .5), (math.cos(a) * .6, math.sin(a) * .6, .0)], [.018, .016, .014], n=6)
            cyl(bm, (math.cos(a) * .6, math.sin(a) * .6, 0), (math.cos(a) * .6, math.sin(a) * .6, .035), .025, n=6)
    b.add("Tripod", [tri], "steel")
    b.add("Mast", [lambda bm: cyl(bm, (0, 0, .95), (0, 0, 1.75), .022, n=8)], "metal_gal", parent="Tripod")
    b.add("Lamp_Head", [lambda bm: cb(bm, 0, .05, 1.82, .5, .12, .34)], "yellow", pivot=(0, 0, 1.8), parent="Mast", bevel=.012)
    b.add("Lens_Grid", [lambda bm: [cb(bm, -.18 + i * .12, .115, 1.82 + (j - .5) * .14 + .0, .1, .01, .12) for i in range(4) for j in range(2)]], "screen_lit", parent="Lamp_Head", bevel=.002)
    b.add("Handle", [lambda bm: tube(bm, [(-.15, .0, 2.0), (-.15, -.0, 2.07), (.15, 0, 2.07), (.15, 0, 2.0)], [.012] * 4, n=6)], "plastic_black", parent="Lamp_Head")
    b.add("Battery_Pack", [lambda bm: cb(bm, 0, -.1, 1.82, .3, .1, .22)], "plastic_black", parent="Lamp_Head", bevel=.01)
    b.add("Cable", [lambda bm: tube(bm, [(0, -.15, 1.78), (0, -.2, 1.5), (-.1, -.25, 1.0), (-.2, -.2, .3), (-.35, -.15, .02), (-.7, -.1, .02)], [.01] * 6, n=5)], "rubber", parent="Mast")
    b.point("carry_handle", (0, 0, 2.07))
    b.place()


@asset("RESCUE_09", "Emergency Supply Crate", "emergency", pose="opened plastic crate; lid hinged open ~100 degrees, contents visible", notes={"parts": "Crate_Body, Lid (hinge pivot in metadata), Latches, Handles, Water_Bottles, Ration_Packs, Blanket_Roll, Label", "grip": "side_handle_L/R"})
def supply_crate(b):
    b.add("Crate_Body", [lambda bm: [frustum(bm, 0, .45, 0, 0, .35, .25, .38, .28, n=4)]], "med_green", bevel=.01)
    b.add("Label", [lambda bm: cb(bm, 0, .275, .22, .24, .006, .14)], "offwhite", parent="Crate_Body")
    b.add("Label_Cross", [lambda bm: [cb(bm, 0, .279, .22, .03, .004, .1), cb(bm, 0, .279, .22, .1, .004, .03)]], "med_red", parent="Label")
    b.add("Handles", [lambda bm: [cb(bm, sx * .385, 0, .36, .02, .14, .05) for sx in (-1, 1)]], "plastic_black", parent="Crate_Body", bevel=.008)

    def lid(bm):
        tmp = bmesh.new()
        cb(tmp, 0, 0, 0, .78, .56, .05)
        cb(tmp, 0, .0, .04, .7, .5, .03)
        rotate_bm(tmp, tmp.verts, "X", -100, center=(0, 0, 0))
        bmesh.ops.translate(tmp, verts=tmp.verts, vec=(0, -.29, .47))
        merge_bm(bm, tmp)
    b.add("Lid", [lid], "med_green", pivot=(0, -.29, .47), parent="Crate_Body", bevel=.008)
    b.add("Latches", [lambda bm: [cb(bm, sx * .2, .285, .4, .07, .02, .08) for sx in (-1, 1)]], "chrome", parent="Crate_Body", bevel=.003)
    b.add("Water_Bottles", [lambda bm: [lathe(bm, [(0, .3), (.05, .3), (.055, .38), (.04, .42), (.02, .46), (.02, .48), (0, .48)], c=(-.22 + i * .1, .1 + (i % 2) * .02, 0), n=10) for i in range(5)]], "glass", parent="Crate_Body")
    b.add("Ration_Packs", [lambda bm: [cb(bm, .1 + (i % 2) * .12, -.13 + (i // 2) * .1, .37 + (i // 2) * .0, .1, .08, .16 if i % 2 else .13) for i in range(4)]], "canvas_red", parent="Crate_Body", bevel=.004)
    b.add("Blanket_Roll", [lambda bm: cyl(bm, (-.28, -.12, .36), (.0, -.12, .36), .06, n=10)], "hiviz_orange", parent="Crate_Body")
    b.point("side_handle_L", (-.385, 0, .36)); b.point("side_handle_R", (.385, 0, .36))
    b.place()




# ==========================================================================
# CATEGORY G - FLOATING DEBRIS (12).  Resting (y=0) pose; origin footprint centre; front = +Y
# ==========================================================================
def _wood_mats():
    return ["wood_light", "bark_fresh", "wood_dark"]


@asset("DEBRIS_01", "Driftwood", "debris", style="debris", pose="resting on the ground", notes={"parts": "Trunk (bleached), Branches, Root_Knuckle, Broken_Ends"})
def driftwood(b):
    rng = random.Random(21)
    spine = [Vector((-1.3 + 2.6 * t, .12 * math.sin(t * 5), .12 + .08 * math.sin(t * 4 + 1))) for t in [i / 12 for i in range(13)]]
    rr = [.12 + .05 * math.sin(i * 1.3) + .05 * (1 - i / 12) for i in range(13)]
    b.add("Trunk", [lambda bm: tube(bm, spine, [(r, r * .85) for r in rr], n=7)], "wood_light", bevel=.0)

    def branches(bm):
        for k, t in enumerate((.25, .45, .62, .8)):
            p = spine[int(t * 12)]
            d = Vector((rng.uniform(-.3, .3), (1 if k % 2 else -1) * .8, rng.uniform(.4, .8))).normalized()
            pts = [p + d * (.0 + L) + Vector((0, 0, -.1 * L * L)) for L in (0, .15, .32, .5)]
            tube(bm, pts, [.045, .04, .03, .018], n=5)
    b.add("Branches", [branches], "wood_dark", parent="Trunk")

    def knuckle(bm):
        e = spine[0]
        blob(bm, e, (.26, .22, .2), sub=2, seed=2.1, rough=.4)
        for k in range(6):
            a = k * 1.05
            tube(bm, [e + Vector((0, 0, .0)), e + Vector((-math.cos(a) * .2 - .1, math.sin(a) * .25, .04 + .08 * math.sin(a))), e + Vector((-math.cos(a) * .4 - .2, math.sin(a) * .5, .1 + .12 * math.cos(a)))], [.05, .04, .015], n=5)
    b.add("Root_Knuckle", [knuckle], "wood_dark", parent="Trunk")

    def ends(bm):
        e = spine[-1]
        for k in range(7):
            a = 2 * math.pi * k / 7
            p0 = e + Vector((0, .0, 0)) + Vector((.0, math.cos(a) * rr[-1] * .8, math.sin(a) * rr[-1] * .7))
            beam(bm, p0, p0 + Vector((rng.uniform(.1, .28), 0, rng.uniform(-.02, .04))), .035, .02, .006, .006)
    b.add("Broken_Ends", [ends], "bark_fresh", parent="Trunk")
    b.place()


@asset("DEBRIS_02", "Wooden Plank", "debris", style="debris", pose="lying on the ground, warped", notes={"parts": "Board, Split_End, Nails, Chipped_Corner"})
def plank(b):
    rng = random.Random(22)

    def board(bm):
        sts = []
        for i in range(13):
            y = -1.0 + 2.0 * i / 12
            w = .12
            warp = .02 * math.sin(y * 2.2) + .012 * math.sin(y * 7)
            sts.append((y, [(-w, .0 + warp), (w, .0 + warp), (w, .04 + warp), (-w, .04 + warp)]))
        loft_pts(bm, sts, axis="y")
    b.add("Board", [board], ["wood_light"], bevel=.004)

    def split(bm):
        for k in range(4):
            x = -.1 + k * .07
            beam(bm, (x, 1.0, .02), (x + rng.uniform(-.03, .03), 1.0 + rng.uniform(.1, .32), .02 + rng.uniform(.0, .04)), .045, .035, .01, .01)
    b.add("Split_End", [split], "bark_fresh", parent="Board")
    b.add("Nails", [lambda bm: [cyl(bm, (x, y, .04), (x, y, .075), .006, n=5) for x, y in ((-.05, -.8), (.06, -.5), (0, .3))] + [cyl(bm, (x, y, .075), (x + .02, y, .076), .016, n=6) for x, y in ()]], "metal_rust", parent="Board")
    b.add("Nail_Heads", [lambda bm: [cyl(bm, (x, y, .075), (x, y, .082), .014, n=6) for x, y in ((-.05, -.8), (.06, -.5), (0, .3))]], "metal_rust", parent="Nails")
    b.add("Chipped_Corner", [lambda bm: [beam(bm, (-.12, -1.0, .0), (-.1, -.95, .05), .03, .02, .01, .01)]], "bark_fresh", parent="Board")
    b.place()


@asset("DEBRIS_03", "Broken Crate", "debris", style="debris", pose="resting; one side smashed in, slats missing", notes={"parts": "Corner_Posts, Slats_Intact, Slats_Broken (splintered), Floor, Nails"})
def broken_crate(b):
    rng = random.Random(23)
    S = .6
    b.add("Corner_Posts", [lambda bm: [cb(bm, sx * S / 2, sy * S / 2, S / 2, .06, .06, S * (.55 if (sx, sy) == (1, 1) else 1)) for sx in (-1, 1) for sy in (-1, 1)]], "wood_dark", bevel=.004)
    b.add("Floor", [lambda bm: cb(bm, 0, 0, .02, S, S, .03)], "wood_light", parent="Corner_Posts", bevel=.003)

    def slats(bm):
        for side in range(4):
            for k in range(5):
                z = .08 + k * .11
                if (side == 0 and k in (2, 3)) or (side == 3 and k == 4) or (side == 1 and k == 0):
                    continue
                if side == 0:
                    cb(bm, 0, S / 2 + .02, z, S, .02, .09)
                elif side == 1:
                    cb(bm, S / 2 + .02, 0, z, .02, S, .09)
                elif side == 2:
                    cb(bm, 0, -S / 2 - .02, z, S, .02, .09)
                else:
                    cb(bm, -S / 2 - .02, 0, z, .02, S, .09)
    b.add("Slats_Intact", [slats], "wood_light", parent="Corner_Posts", bevel=.003)

    def broken(bm):
        for (y, z, L) in ((S / 2 + .02, .30, .32), (S / 2 + .02, .41, .22), (-S / 2 - .02, .08, .18)):
            x0 = -S / 2 if L > .2 else S / 2 - L
            cb(bm, x0 + L / 2, y, z, L, .02, .09)
            for k in range(3):
                beam(bm, (x0 + L + .0, y, z - .03 + k * .03), (x0 + L + rng.uniform(.04, .1), y + rng.uniform(-.02, .03), z - .03 + k * .03 + rng.uniform(-.02, .02)), .02, .018, .004, .004)
        # slat that fell outside
        beam(bm, (.45, .55, .01), (.15, .85, .035), .085, .02)
    b.add("Slats_Broken", [broken], "bark_fresh", parent="Corner_Posts", bevel=.002)
    b.add("Nails", [lambda bm: [cyl(bm, (sx * S / 2, S / 2 + .031, z), (sx * S / 2, S / 2 + .045, z), .006, n=5) for sx in (-1, 1) for z in (.08, .19)]], "metal_rust", parent="Corner_Posts")
    b.place()


@asset("DEBRIS_04", "Floating Barrel", "debris", style="debris", pose="lying on its side", notes={"parts": "Staves, Hoops (3, steel), Lid_Top, Lid_Bottom, Bung, Dent"})
def barrel(b):
    def staves(bm):
        n = 14
        prof = [(0, -.45), (.27, -.45), (.30, -.3), (.335, 0), (.30, .3), (.27, .45), (0, .45)]
        tmp = bmesh.new()
        lathe(tmp, prof, n=n, cap0=True, cap1=True)
        for v in tmp.verts:
            ang = math.atan2(v.co.y, v.co.x)
            if abs(v.co.z) < .25 and 1.0 < ang < 2.2:           # dent
                k = (1 - abs(ang - 1.6) / .6) * (1 - abs(v.co.z) / .25)
                v.co.x *= 1 - .1 * k
                v.co.y *= 1 - .1 * k
            v.co.x *= 1 + .01 * math.sin(ang * n)
        rotate_bm(tmp, tmp.verts, "Y", 90)
        merge_bm(bm, tmp)
    b.add("Staves", [staves], "wood_dark", bevel=0)

    def hoops(bm):
        for z, r in ((-.37, .285), (-.1, .338), (.1, .338), (.37, .285)):
            tmp = bmesh.new()
            torus(tmp, (0, 0, z), r + .004, .011, n=14, m=5)
            rotate_bm(tmp, tmp.verts, "Y", 90)
            merge_bm(bm, tmp)
    b.add("Hoops", [hoops], "metal_rust", parent="Staves")
    b.add("Bung", [lambda bm: cyl(bm, (0, .0, .335), (0, 0, .36), .03, n=8)], "wood_light", parent="Staves")
    b.place()


@asset("DEBRIS_05", "Pallet", "debris", style="debris", pose="lying flat, damaged", notes={"parts": "Stringers, Top_Boards, Bottom_Boards, Broken_Board, Nails"})
def pallet(b):
    b.add("Stringers", [lambda bm: [cb(bm, x, 0, .07, .09, 1.2, .1) for x in (-.5, 0, .5)]], "wood_dark", bevel=.003)
    b.add("Bottom_Boards", [lambda bm: [cb(bm, 0, y, .015, 1.1, .1, .03) for y in (-.55, 0, .55)]], "wood_light", parent="Stringers", bevel=.003)

    def top(bm):
        for i, y in enumerate((-.55, -.37, -.18, .0, .18, .37, .55)):
            if i == 4:
                continue
            L = 1.1 if i != 2 else .62
            x0 = -.55 if i != 2 else -.55
            cb(bm, x0 + L / 2, y, .13, L, .15, .03)
    b.add("Top_Boards", [top], "wood_light", parent="Stringers", bevel=.003)

    def snapped(bm):
        beam(bm, (.25, -.18, .13), (.58, -.2, .125), .15, .03)
        for k in range(4):
            beam(bm, (.24, -.18 + (k - 1.5) * .035, .13), (.24 + .02 + k * .015, -.18 + (k - 1.5) * .035 + .01, .13), .03, .03, .008, .008) if False else None
        beam(bm, (.62, .18, .01), (.2, .5, .03), .14, .03)       # board knocked loose beside pallet
    b.add("Broken_Board", [snapped], "bark_fresh", parent="Stringers", bevel=.003)
    b.add("Nails", [lambda bm: [cyl(bm, (x, y, .145), (x, y, .152), .011, n=6) for x in (-.5, 0, .5) for y in (-.55, -.37, .55)]], "metal_rust", parent="Top_Boards")
    b.place()


@asset("DEBRIS_06", "Road Sign Fragment", "debris", style="debris", pose="bent sign plate on a snapped pole stub, lying on the ground", notes={"parts": "Plate, Plate_Face, Text_Bars, Pole, Bolts, Torn_Edge"})
def sign_fragment(b):
    rng = random.Random(26)
    outline = [(-.5, -.28), (.1, -.3), (.52, -.26), (.55, .1), (.35, .3), (.1, .22), (-.1, .32), (-.5, .26)]

    def plate(bm):
        gprism(bm, 0, .02, outline)
        for v in bm.verts:
            v.co.z += .13 * smoothstep(-.1, .55, v.co.x) + .02 * math.sin(v.co.y * 6)
            v.co.y += 0
    b.add("Plate", [plate], "metal_gal", bevel=.002)

    def face(bm):
        inn = [(x * .92, y * .9) for x, y in outline]
        gprism(bm, .021, .03, inn)
        for v in bm.verts:
            if v.co.z > .02 and v.co.z < .035:
                v.co.z += .13 * smoothstep(-.1, .55, v.co.x) + .02 * math.sin(v.co.y * 6)
    b.add("Plate_Face", [face], "sign_green", parent="Plate")

    def text(bm):
        for k, (w, y) in enumerate(((.55, .12), (.4, .0), (.62, -.12))):
            cb(bm, -.05, y, .035, w, .035, .008)
            for i in range(3):
                pass
        cb(bm, .35, .0, .036, .1, .1, .006)
    b.add("Text_Bars", [text], "sign_white", parent="Plate_Face")
    b.add("Pole", [lambda bm: [beam(bm, (-.46, 0, .035), (-1.1, .15, .05), .05, .04), ]], "steel", parent="Plate", bevel=.003)
    b.add("Pole_Break", [lambda bm: [beam(bm, (-1.1, .15, .05), (-1.18 - .04 * k, .15 + (k - 1.5) * .02, .05 + .01 * k), .035, .03, .006, .006) for k in range(4)]], "bark_fresh", parent="Pole") if False else None
    b.add("Bolts", [lambda bm: [cyl(bm, (-.4, y, .04), (-.4, y, .056), .014, n=6) for y in (-.12, .12)]], "chrome", parent="Plate")
    b.place()


@asset("DEBRIS_07", "Roof Tile Cluster", "debris", style="debris", pose="loose cluster of clay roof tiles with a batten", notes={"parts": "Tiles (overlapping, curved), Cracked_Halves, Batten"})
def roof_tiles(b):
    rng = random.Random(27)

    def tile_fn(cx, cy, ang, crack=False, flip=False):
        def f(bm):
            sts = []
            for i in range(5):
                y = -.19 + .38 * i / 4
                w = .1 + .015 * (y / .19)
                pts = []
                for k in range(7):
                    t = -1 + 2 * k / 6
                    pts.append((t * w, .035 * (1 - t * t) * (1.0 if not flip else -1.0)))
                pts2 = [(x, z + .012) for x, z in pts]
                sts.append((y, pts + pts2[::-1]))
            tmp = bmesh.new()
            loft_pts(tmp, sts, axis="y")
            if crack:
                cut(tmp, (0, .03, 0), (.3, 1, 0), "neg", 0)
            rotate_bm(tmp, tmp.verts, "Z", ang)
            bmesh.ops.translate(tmp, verts=tmp.verts, vec=(cx, cy, 0))
            merge_bm(bm, tmp)
        return f
    shapes = []
    for r in range(3):
        for c in range(4):
            shapes.append(tile_fn((c - 1.5) * .205 + .05 * r, r * .3 - .3 + rng.uniform(-.02, .02), rng.uniform(-8, 8)))
    b.add("Tiles", shapes, "pot_clay", bevel=.0015)
    b.add("Cracked_Halves", [tile_fn(.55, -.45, 70, crack=True), tile_fn(-.55, .5, -50, crack=True), tile_fn(.5, .55, 150, flip=True)], "rust", parent="Tiles", bevel=.0015)
    b.add("Batten", [lambda bm: cb(bm, 0, .0, .015, .05, 1.0, .03)], "wood_dark", parent="Tiles") if False else None
    b.place()


@asset("DEBRIS_08", "Shattered Window Panel", "debris", style="debris", pose="window frame lying flat, glass cracked with missing shards", notes={"parts": "Frame, Glass_Shards (radial fracture), Sill, Loose_Shards, Glazing_Putty"})
def shattered_window(b):
    rng = random.Random(28)
    W, H = .9, 1.2
    b.add("Frame", [lambda bm: [cb(bm, 0, (H / 2 + .03) * s, .025, W + .12, .06, .05) for s in (-1, 1)] + [cb(bm, (W / 2 + .03) * s, 0, .025, .06, H, .05) for s in (-1, 1)] +
                    [cb(bm, 0, 0, .025, .04, H, .04), cb(bm, 0, .1, .025, W, .04, .04)]], "offwhite", bevel=.004)
    imp = (.15, -.1)
    angs = sorted(rng.uniform(0, 6.283) for _ in range(11))
    rings = [0.0, .22, .55, 1.6]

    def shard_pts():
        out = []
        for i in range(len(angs)):
            a0, a1 = angs[i], angs[(i + 1) % len(angs)]
            if a1 < a0:
                a1 += 6.283
            for j in range(len(rings) - 1):
                r0, r1 = rings[j], rings[j + 1]
                pts = []
                for r, a in ((r0, a0), (r0, a1), (r1, a1), (r1, a0)):
                    if r == 0:
                        pts.append(imp)
                    else:
                        pts.append((imp[0] + math.cos(a) * r, imp[1] + math.sin(a) * r))
                if r0 == 0:
                    pts = [pts[0], pts[2], pts[3]]
                out.append((i, j, pts))
        return out
    shards = shard_pts()

    def clip(p):
        return (max(-W / 2 + .004, min(W / 2 - .004, p[0])), max(-H / 2 + .004, min(H / 2 - .004, p[1])))

    def glass(bm):
        for (i, j, pts) in shards:
            if (i in (2, 3, 7) and j == 0) or (i in (5,) and j == 1) or (i == 9 and j == 2):
                continue
            pts = [clip(p) for p in pts]
            # shrink slightly for visible crack lines
            cx = sum(p[0] for p in pts) / len(pts)
            cy = sum(p[1] for p in pts) / len(pts)
            pts = [(cx + (p[0] - cx) * .965, cy + (p[1] - cy) * .965) for p in pts]
            if len(set(pts)) < len(pts):
                continue
            n = len(pts)
            z0 = .018 + .0015 * rng.random()
            try:
                solid(bm, [(x, y, z0) for x, y in pts], [(x, y, z0 + .01) for x, y in pts])
            except ValueError:
                pass
    b.add("Glass_Shards", [glass], "glass", parent="Frame")
    b.add("Loose_Shards", [lambda bm: [solid(bm, [(x, y, 0), (x + .12, y + .02, 0), (x + .04, y + .14, 0)], [(x, y, .008), (x + .12, y + .02, .008), (x + .04, y + .14, .008)]) for x, y in ((.7, -.2), (.62, .5), (-.75, .3), (.55, -.7))]], "glass", parent="Frame")
    b.add("Sill", [lambda bm: cb(bm, 0, -H / 2 - .1, .02, W + .3, .1, .04)], "concrete", parent="Frame", bevel=.004)
    b.place()


@asset("DEBRIS_09", "Broken Dock Timber", "debris", style="debris", pose="snapped pile section with decking plank still bolted", notes={"parts": "Pile, Splintered_End, Decking_Plank, Bolts, Bracket, Rope"})
def dock_timber(b):
    rng = random.Random(29)
    b.add("Pile", [lambda bm: tube(bm, [(0, -1.3, .17), (0, -.3, .17), (0, .6, .17), (0, 1.1, .17)], [.16, .16, .15, .14], n=8)], "wood_dark", bevel=.0)

    def splint(bm):
        for k in range(10):
            a = 2 * math.pi * k / 10
            p0 = Vector((math.cos(a) * .1, 1.1, .17 + math.sin(a) * .1))
            beam(bm, p0, p0 + Vector((math.cos(a) * rng.uniform(-.03, .05), rng.uniform(.12, .5), math.sin(a) * rng.uniform(-.03, .05))), .055, .035, .008, .008)
    b.add("Splintered_End", [splint], "bark_fresh", parent="Pile")
    b.add("Decking_Plank", [lambda bm: cb(bm, 0, -.4, .365, .7, .24, .045)], "wood_light", parent="Pile", bevel=.004)
    b.add("Bracket", [lambda bm: [cb(bm, sx * .12, -.4, .3, .02, .1, .12) for sx in (-1, 1)] + [cb(bm, 0, -.4, .335, .26, .11, .02)]], "metal_rust", parent="Pile", bevel=.002)
    b.add("Bolts", [lambda bm: [cyl(bm, (x, -.4, .39), (x, -.4, .42), .02, n=6) for x in (-.2, .2)]], "steel", parent="Decking_Plank")
    b.add("Rope", [lambda bm: tube(bm, [(.17, -.25, .17), (.3, -.1, .06), (.55, .25, .03), (.7, .6, .03), (.8, .95, .04)], [.022] * 5, n=6)], "canvas", parent="Pile")
    b.place()


@asset("DEBRIS_10", "Metal Sheet", "debris", style="debris", pose="corrugated sheet, bent and torn, lying on the ground", notes={"parts": "Sheet (corrugated), Torn_Edge, Rust_Patches, Fasteners"})
def metal_sheet(b):
    rng = random.Random(30)

    def sheet(bm):
        W, Ln = 1.0, 1.6
        sts = []
        for i in range(17):
            y = -Ln / 2 + Ln * i / 16
            row = []
            for k in range(17):
                x = -W / 2 + W * k / 16
                z = .035 * math.sin(k * math.pi / 1.0 * 1) * 1.0
                z = .03 * math.sin(x * 2 * math.pi * 4.0)
                bend = .22 * smoothstep(.0, .8, y) ** 1.6 + .04 * fbm(Vector((x * 3, y * 3, 2)), 2)
                row.append((x, z + bend))
            top = [(x, z + .008) for x, z in row]
            sts.append((y + .02 * fbm(Vector((row[0][0] * 3, y * 2, 1)), 2), row + top[::-1]))
        # torn trailing edge
        for k in range(len(sts[-1][1])):
            pass
        loft_pts(bm, sts, axis="y")
        for v in bm.verts:
            if v.co.y > .7:
                v.co.y -= .09 * abs(math.sin(v.co.x * 11)) * ((v.co.y - .7) / .1)
    b.add("Sheet", [sheet], ["metal_gal"], bevel=0.0)
    b.add("Rust_Patches", [lambda bm: [blob(bm, (rng.uniform(-.35, .35), rng.uniform(-.6, .4), .02 + .0), (.1, .08, .014), sub=1, seed=rng.uniform(0, 9), rough=.3) for _ in range(5)]], "metal_rust", parent="Sheet")
    b.add("Fasteners", [lambda bm: [cyl(bm, (x, -.7, .045), (x, -.7, .06), .018, n=6) for x in (-.4, -.14, .12, .38)]], "steel", parent="Sheet")
    b.place()


@asset("DEBRIS_11", "Broken Furniture", "debris", style="debris", pose="smashed wooden chair: seat split, one leg snapped, back detached", notes={"parts": "Seat_Left, Seat_Right (split), Legs, Leg_Snapped, Backrest_Fallen, Splinters"})
def broken_furniture(b):
    rng = random.Random(31)
    b.add("Seat_Left", [lambda bm: cb(bm, -.12, 0, .3, .2, .42, .04)], "wood_light", bevel=.004)

    def right(bm):
        tmp = bmesh.new()
        cb(tmp, .12, 0, 0, .24, .42, .04)
        rotate_bm(tmp, tmp.verts, "Y", 12)
        bmesh.ops.translate(tmp, verts=tmp.verts, vec=(.0, .0, .28))
        merge_bm(bm, tmp)
    b.add("Seat_Right", [right], "wood_light", bevel=.004)
    b.add("Legs", [lambda bm: [tleg(bm, -.2, -.17, .28, .02, .02, 6), tleg(bm, -.2, .17, .28, .022, .018, 6), tleg(bm, .2, -.17, .22, .02, .02, 6)]], "wood_dark", parent="Seat_Left")
    b.add("Leg_Snapped", [lambda bm: [cyl(bm, (.55, .1, .02), (.9, .25, .02), .022, n=6), *[beam(bm, (.9, .25, .02), (.9 + rng.uniform(.02, .07), .25 + rng.uniform(-.03, .03), .02 + rng.uniform(-.01, .02)), .02, .015, .004, .004) for _ in range(4)]]], "wood_dark", parent="Seat_Left")
    b.add("Backrest_Fallen", [lambda bm: [beam(bm, (-.2, -.7, .02), (.2, -.7, .02), .04, .04)] + [beam(bm, (sx * .19, -.7, .02), (sx * .19, -.28, .06), .04, .04) for sx in (-1, 1)] + [beam(bm, (-.19, -.55 + k * .1, .03), (.19, -.55 + k * .1, .03), .018, .06) for k in range(3)]], "wood_light", parent="Seat_Left", bevel=.003)
    b.add("Splinters", [lambda bm: [beam(bm, (0, -.2 + k * .1, .3), (rng.uniform(-.04, .05), -.2 + k * .1 + rng.uniform(-.02, .02), .3 + rng.uniform(.02, .08)), .025, .018, .004, .004) for k in range(5)]], "bark_fresh", parent="Seat_Left")
    b.add("Cushion_Torn", [lambda bm: rbox(bm, -.35, -.05, -.18, .17, .32, .37, .8)], "fabric_coral", parent="Seat_Left", bevel=.015) if False else None
    b.place()


@asset("DEBRIS_12", "Uprooted Planter", "debris", style="debris", pose="clay pot tipped on its side, cracked, with spilled soil and a pulled-up plant", notes={"parts": "Pot, Crack_Chunk, Soil_Spill, Root_Ball, Stem_Leaves"})
def uprooted_planter(b):
    rng = random.Random(32)

    def pot(bm):
        tmp = bmesh.new()
        lathe(tmp, [(0, 0), (.14, 0), (.19, .05), (.24, .3), (.265, .36), (.27, .38), (.25, .38), (.22, .3), (.17, .06), (.0, .04)], n=16)
        rotate_bm(tmp, tmp.verts, "X", -90)
        # crack: remove a wedge by pushing verts
        for v in tmp.verts:
            if v.co.z > .22 and v.co.y < -.15 and abs(v.co.x) < .06:
                v.co.y += .05
        bmesh.ops.translate(tmp, verts=tmp.verts, vec=(0, -.1, .27))
        merge_bm(bm, tmp)
    b.add("Pot", [pot], "pot_clay", bevel=0.0)
    b.add("Rim_Ring", [lambda bm: torus(bm, (0, .28, .27), .26, .018, n=16, m=5, axis="y")], "pot_clay", parent="Pot")
    b.add("Crack_Chunk", [lambda bm: poly_prism(bm, [(0, 0), (.12, .03), (.14, .12), (.02, .16)], 0, .02)], "pot_clay", parent="Pot", pivot=(.5, .5, 0)) if False else None
    b.add("Crack_Chunk", [lambda bm: [rotate_bm(bm, bm.verts, "Z", 25), bmesh.ops.translate(bm, verts=bm.verts, vec=(.45, .2, 0))] if False else (poly_prism(bm, [(.4, .15), (.52, .18), (.54, .27), (.42, .31)], 0, .018))], "pot_clay", parent="Pot", bevel=.002)

    def spill(bm):
        blob(bm, (0, .62, .06), (.45, .38, .1), sub=2, seed=4.4, rough=.35, flat=(0, 0, -1, .05))
        for k in range(8):
            blob(bm, (rng.uniform(-.4, .4), rng.uniform(.4, .95), .03), (.06, .05, .03), sub=1, seed=rng.uniform(0, 9), rough=.3, flat=(0, 0, -1, .02))
    b.add("Soil_Spill", [spill], "dirt_dark", parent="Pot")
    b.add("Root_Ball", [lambda bm: blob(bm, (.05, .45, .13), (.2, .17, .13), sub=2, seed=1.2, rough=.3, flat=(0, 0, -1, .1))], "soil", parent="Pot")

    def stem(bm):
        base = Vector((.05, .52, .2))
        tube(bm, [base, base + Vector((.08, .12, .12)), base + Vector((.1, .3, .15)), base + Vector((.05, .5, .1))], [.02, .017, .014, .01], n=5)
        for k in range(7):
            t = k / 6
            p = base + Vector((.08 * t + .02, .3 * t + .1, .12 + .02 * t))
            a = rng.uniform(0, 6.28)
            d = Vector((math.cos(a), math.sin(a) * .6, .3 + .2 * rng.random())).normalized()
            blade(bm, [p, p + d * .12, p + d * .24 + Vector((0, 0, -.04))], [.01, .045, .005], .003, up=(0, 0, 1))
    b.add("Stem_Leaves", [stem], ["plant_green"], parent="Root_Ball")
    b.add("Roots", [lambda bm: [tube(bm, [(.05 + rng.uniform(-.1, .1), .38, .1), (.05 + rng.uniform(-.12, .12), .3, .06), (.05 + rng.uniform(-.2, .2), .22, .03)], [.012, .009, .004], n=4) for _ in range(6)]], "root", parent="Root_Ball")
    b.place()


# ==========================================================================
# DRIVER
# ==========================================================================
FOLDERS = {"animals": "animals", "disaster": "disaster_objects", "celestial": "celestial", "interiors": "interiors",
           "accessories": "accessories", "emergency": "emergency", "debris": "floating_debris"}


def parse_args03():
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    p = argparse.ArgumentParser()
    p.add_argument("--out", default=os.path.join(os.getcwd(), "WORLDLINE_ASSET_PACK_03B_81"))
    p.add_argument("--only", default="", help="comma separated asset IDs or prefixes, e.g. ANIMAL_01,CELESTIAL")
    p.add_argument("--no-render", action="store_true")
    p.add_argument("--samples", type=int, default=12)
    p.add_argument("--res", type=int, default=640)
    p.add_argument("--az", type=float, default=145.0)
    p.add_argument("--el", type=float, default=14.0)
    p.add_argument("--suffix", default="")
    a, _ = p.parse_known_args(argv)
    return a


def generate(entry, out, args, catalog):
    aid, name = entry["id"], entry["name"]
    base = f"{aid}_{name.replace(' ', '').replace('-', '')}"
    folder = FOLDERS[entry["folder"]]
    view = (entry.get("notes") or {}).pop("_view", None)
    reset_scene()
    coll = new_collection(base)
    b = Builder(coll, base)
    problems = []
    try:
        entry["fn"](b)
    except Exception as ex:
        import traceback
        traceback.print_exc()
        print(f"[{aid}] BUILD ERROR: {ex}")
        catalog[aid] = {"id": aid, "name": name, "status": "FAILED", "error": str(ex)}
        return
    st = mesh_stats(b)
    mn, mx = st["min"], st["max"]
    dims = {"x_width_m": round(mx.x - mn.x, 4), "y_height_m": round(mx.z - mn.z, 4), "z_depth_m": round(mx.y - mn.y, 4)}
    if entry["style"] == "ground" and abs(mn.z) > 0.012:
        problems.append(f"not resting on ground (min height {mn.z:.3f})")
    if st["neg_volume_parts"]:
        problems.append("inverted/negative volume parts: " + ", ".join(p.split(base + '_')[-1] for p in st["neg_volume_parts"]))
    if st["tris"] < 80:
        problems.append(f"very low triangle count {st['tris']}")
    obj_dir = os.path.join(out, folder)
    os.makedirs(obj_dir, exist_ok=True)
    obj_path = os.path.join(obj_dir, base + ".obj")
    export_obj(b, obj_path)
    if not os.path.exists(obj_path) or not os.path.exists(obj_path[:-4] + ".mtl"):
        problems.append("OBJ/MTL not written")
    parts = []
    for i in b.info:
        parts.append({"object": i["name"], "parent": i["parent"], "pivot_file_xyz": list(to_file(i["pivot_build"])),
                      "materials": i["materials"], "triangles": i["triangles"]})
    meta = {"id": aid, "name": name, "category": entry["folder"], "obj": f"{folder}/{base}.obj", "mtl": f"{folder}/{base}.mtl",
            "units": "metres" if entry["style"] != "space" else "model units (see notes)", "up": "Y", "forward": "-Z",
            "origin": "ground contact (y=0) at the footprint centre" if entry["style"] == "ground" else
                      "centre of the object" if entry["style"] == "space" else "centre of mass (airborne / floating)",
            "pose": entry["pose"], "dimensions": dims,
            "bounds_file_min": list(to_file((mn.x, mn.y, mx.z)))[:0] or [round(mn.x, 4), round(mn.z, 4), round(-mx.y, 4)],
            "bounds_file_max": [round(mx.x, 4), round(mx.z, 4), round(-mn.y, 4)],
            "triangles": st["tris"], "parts": parts,
            "attachment_points_file_xyz": {k: list(to_file(v)) for k, v in b.attach.items()},
            "notes": entry["notes"], "open_part_count": len(st["open_parts"]), "geometry_hash": st["geom_hash"]}
    with open(os.path.join(out, "metadata", base + ".json"), "w") as f:
        json.dump(meta, f, indent=2)
    prev = None
    if not args.no_render:
        prev = f"previews/{base}{args.suffix}.png"
        try:
            render_asset_preview(b, entry["style"], os.path.join(out, prev), res=(args.res, args.res), samples=args.samples, az=view[0] if view else args.az, el=view[1] if view else args.el)
        except Exception as ex:
            problems.append(f"preview failed: {ex}")
            prev = None
    catalog[aid] = {"id": aid, "name": name, "category": entry["folder"], "file": f"{folder}/{base}.obj", "mtl": f"{folder}/{base}.mtl",
                    "metadata": f"metadata/{base}.json", "preview": prev, "dimensions_m": dims, "triangles": st["tris"],
                    "parts": len(b.info), "status": "OK" if not problems else "WARN", "problems": problems,
                    "geometry_hash": st["geom_hash"], "pose": entry["pose"]}
    print(f"[{aid}] {name}: parts={len(b.info)} tris={st['tris']} size={dims['x_width_m']:.2f}x{dims['y_height_m']:.2f}x{dims['z_depth_m']:.2f}"
          f"{'  PROBLEMS: ' + '; '.join(problems) if problems else ''}")


def main03():
    args = parse_args03()
    out = args.out
    for d in list(FOLDERS.values()) + ["previews", "metadata"]:
        os.makedirs(os.path.join(out, d), exist_ok=True)
    cat_path = os.path.join(out, "ASSET_CATALOG.json")
    catalog = {}
    if os.path.exists(cat_path):
        try:
            catalog = {e["id"]: e for e in json.load(open(cat_path))["assets"]}
        except Exception:
            catalog = {}
    sel = [s.strip() for s in args.only.split(",") if s.strip()]
    todo = [e for e in REGISTRY if not sel or any(e["id"].startswith(s) for s in sel)]
    print(f"[pack03b] generating {len(todo)} of {len(REGISTRY)} registered assets -> {out}")
    for e in todo:
        generate(e, out, args, catalog)
        order = {e2["id"]: i for i, e2 in enumerate(REGISTRY)}
        with open(cat_path, "w") as f:
            json.dump({"pack": "WORLDLINE_ASSET_PACK_03B_81", "count": len(catalog),
                       "assets": sorted(catalog.values(), key=lambda x: order.get(x["id"], 999))}, f, indent=2)
    bad = [k for k, v in catalog.items() if v["status"] != "OK"]
    print(f"[pack03b] done. assets in catalog: {len(catalog)}; with warnings/failures: {len(bad)} {bad}")


if __name__ == "__main__":
    main03()
