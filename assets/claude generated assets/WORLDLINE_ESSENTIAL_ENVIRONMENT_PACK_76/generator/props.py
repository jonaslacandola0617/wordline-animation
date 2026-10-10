from lib import *

def put(M, T, ox=0, oy=0, oz=0, ry=0):
    for (g, m), p in T.groups.items(): M.add(g, m, p.copy().rot('y', ry).move(ox, oy, oz) if ry else p.copy().move(ox, oy, oz))

def bolts(M, g, pts, y, r=0.022, h=0.03, mat='galvanized_steel'):
    for x, z in pts: M.add(g, mat, cyl(r, h, 6, y, x, z, r*0.85))

def base_plate(M, g, s=0.5, t=0.04, mat='galvanized_steel', x=0, z=0, bolt=True):
    M.add(g, mat, box(x-s/2, 0, z-s/2, x+s/2, t, z+s/2, 0.008))
    if bolt:
        o = s/2-0.05; bolts(M, g, [(x+a, z+b) for a in (-o, o) for b in (-o, o)], t)

def louvre(M, g, mat, x0, x1, y0, y1, z, n, t=0.014, d=0.035):
    for i in range(n):
        y = y0+(y1-y0)*i/max(n-1, 1); M.add(g, mat, box(x0, y, z, x1, y+t, z+d))

def insulator(M, g, x, y, z, h=0.3, r=0.07, mat='insulator_ceramic'):
    k = h/0.3
    pr = [(0.03, 0), (0.045, 0.03), (r, 0.05), (r, 0.075), (0.045, 0.09), (0.045, 0.13), (r*0.9, 0.15), (r*0.9, 0.17), (0.04, 0.19),
          (0.04, 0.26), (0.03, 0.3)]
    M.add(g, mat, lathe([(a, b*k) for a, b in pr], 8, x, z).move(0, y, 0))

# ---------------------------------------------------------------- PROP_01 / 02
def sig_head(n=3, tag='head'):
    T = Model('t', 'x')
    T.box('housing', 'paint_navy', -0.21, -0.6, -0.16, 0.21, 0.6, 0.16, 0.05)
    T.box('backplate', 'rubber_dark', -0.31, -0.7, -0.2, 0.31, 0.7, -0.15, 0.015)
    for i, m in enumerate(['signal_red', 'signal_amber', 'signal_green'][:n]):
        y = 0.38-i*0.38
        T.tube('lens_'+m, m, (0, y, 0.15), (0, y, 0.2), 0.12, 12)
        T.box('visor', 'rubber_dark', -0.17, y+0.11, 0.15, 0.17, y+0.15, 0.44, 0.01)
        T.box('visor', 'rubber_dark', -0.17, y-0.13, 0.15, -0.145, y+0.14, 0.42)
        T.box('visor', 'rubber_dark', 0.145, y-0.13, 0.15, 0.17, y+0.14, 0.42)
    T.box('mount', 'galvanized_steel', -0.08, 0.6, -0.08, 0.08, 0.72, 0.08, 0.01)
    T.box('mount', 'galvanized_steel', -0.08, -0.72, -0.08, 0.08, -0.6, 0.08, 0.01)
    return T

def PROP_01():
    M = Model('PROP_01', 'street_props', 'Mast-arm vehicle traffic signal, 3 heads (red/amber/green lenses emissive), 5.2 m')
    base_plate(M, 'base', 0.6)
    M.add('pole', 'metal_painted_grey', cylb(0.2, 0.45, 10, 0.04, b=0.04))
    M.add('pole', 'metal_painted_grey', cyl(0.135, 4.6, 12, 0.49, r1=0.085))
    M.add('pole', 'metal_painted_grey', cylb(0.12, 0.12, 10, 5.0, b=0.02))
    M.tube('mast_arm', 'metal_painted_grey', (0, 4.85, 0), (3.9, 4.95, 0), 0.075, 10, 0.045)
    M.beam('mast_arm', 'metal_painted_grey', (0, 4.05, 0), (1.7, 4.88, 0), 0.07, 0.07)
    M.beam('mast_arm', 'metal_painted_grey', (0.1, 4.45, 0), (0.9, 4.9, 0), 0.05, 0.05)
    M.cyl('mast_arm', 'galvanized_steel', 0.1, 0.1, 10, 4.9, 3.95, 0, 0.1) if False else None
    for x in (2.0, 3.4):
        h = sig_head(); put(M, h, x, 4.0, 0.0, 0)
        M.tube('head_hanger', 'galvanized_steel', (x, 4.78, 0), (x, 4.72, 0), 0.05, 8)
    h = sig_head(); put(M, h, 0, 2.9, 0.43, 0)
    M.beam('pole_bracket', 'galvanized_steel', (-0.05, 3.5, 0.1), (-0.05, 3.5, 0.28), 0.05, 0.05)
    M.beam('pole_bracket', 'galvanized_steel', (-0.05, 2.3, 0.1), (-0.05, 2.3, 0.28), 0.05, 0.05)
    M.box('junction_box', 'paint_navy', -0.13, 1.0, 0.12, 0.13, 1.45, 0.3, 0.02)
    M.box('junction_box', 'rubber_dark', -0.1, 1.05, 0.3, 0.1, 1.4, 0.31)
    M.tube('conduit', 'cable_black', (0.06, 1.45, 0.14), (0.06, 4.9, 0.14), 0.02, 6)
    M.tube('conduit', 'cable_black', (0.06, 4.95, 0.14), (3.3, 5.05, 0.1), 0.018, 6)
    M.cn('cable_anchor_mast_tip', (3.9, 4.95, 0), (1, 0, 0)); M.cn('base_ground', (0, 0, 0), (0, -1, 0))
    M.det('mast_arm', 'mast arm + brace + hanging heads (snaps off at pole top)', (0, 4.85, 0))
    return M

def PROP_02():
    M = Model('PROP_02', 'street_props', 'Pedestrian crossing signal with red-hand / walking-figure displays and push-button, 3.1 m')
    base_plate(M, 'base', 0.34, 0.035)
    M.add('pole', 'metal_painted_grey', cyl(0.075, 2.9, 10, 0.035, r1=0.06))
    M.add('pole', 'metal_painted_grey', cylb(0.09, 0.06, 10, 2.9, b=0.015))
    # head housing facing +z
    M.box('housing', 'paint_navy', -0.3, 2.35, 0.06, 0.3, 3.1, 0.34, 0.04)
    M.box('housing', 'rubber_dark', -0.26, 2.39, 0.335, 0.26, 3.06, 0.352, 0.01)
    M.box('hood', 'rubber_dark', -0.31, 3.08, 0.06, 0.31, 3.13, 0.46, 0.012)
    M.box('hood', 'rubber_dark', -0.31, 2.33, 0.34, 0.31, 2.37, 0.46, 0.012)
    # red hand (top) + walking figure (bottom), inset on the display face
    M.box('display_hand', 'signal_red', -0.1, 2.78, 0.35, 0.1, 2.88, 0.37)
    for i in range(4): M.box('display_hand', 'signal_red', -0.1+i*0.055, 2.88, 0.35, -0.065+i*0.055, 3.0, 0.37)
    M.box('display_hand', 'signal_red', -0.17, 2.8, 0.35, -0.11, 2.86, 0.37)
    M.box('display_walk', 'lamp_emissive', -0.06, 2.40, 0.35, -0.01, 2.55, 0.37); M.box('display_walk', 'lamp_emissive', 0.01, 2.40, 0.35, 0.06, 2.55, 0.37)
    M.box('display_walk', 'lamp_emissive', -0.06, 2.55, 0.35, 0.06, 2.68, 0.37)
    M.add('display_walk', 'lamp_emissive', cyl(0.035, 0.02, 8, 0, 0, 0).rot('x', 90).move(0, 2.72, 0.35))
    # push button unit
    M.box('button_unit', 'safety_yellow', -0.09, 1.0, 0.07, 0.09, 1.3, 0.14, 0.02)
    M.add('button_unit', 'brushed_metal', cylb(0.045, 0.03, 10, 1.12, 0, 0.14).rot('x', 90, (0, 1.12, 0.14)).move(0, 0, 0.0) if False else cyl(0.045, 0.035, 10, 0, 0, 0).rot('x', 90).move(0, 1.2, 0.14))
    M.box('button_unit', 'sign_white', -0.07, 1.03, 0.14, 0.07, 1.1, 0.145)
    M.tube('conduit', 'cable_black', (0.05, 0.04, 0.0), (0.05, 2.4, 0.0), 0.012, 6) if False else None
    M.cn('button_press', (0, 1.2, 0.18), (0, 0, 1)); M.cn('cable_anchor', (0, 2.9, 0), (0, 1, 0))
    return M

# ---------------------------------------------------------------- PROP_03 / 04 lights
def PROP_03():
    M = Model('PROP_03', 'street_props', 'Urban streetlight: tapered octagonal post, swan-neck arm, shaped luminaire, 6.4 m')
    base_plate(M, 'base', 0.5)
    M.add('post', 'metal_painted_grey', cylb(0.23, 0.55, 8, 0.04, b=0.04))
    M.add('post', 'metal_painted_grey', cyl(0.15, 5.4, 8, 0.59, r1=0.07, ph=math.pi/8))
    M.box('handhole', 'galvanized_steel', -0.08, 0.7, 0.12, 0.08, 1.2, 0.2, 0.012)
    M.box('handhole', 'rubber_dark', -0.02, 0.9, 0.2, 0.02, 1.0, 0.215)
    pts = [(0, 5.9), (0.1, 6.25), (0.45, 6.5), (0.95, 6.55), (1.45, 6.4), (1.75, 6.25)]
    for i in range(len(pts)-1):
        r0 = 0.07-0.012*i; r1 = 0.07-0.012*(i+1)
        M.tube('arm', 'metal_painted_grey', (pts[i][0], pts[i][1], 0), (pts[i+1][0], pts[i+1][1], 0), r0, 8, r1)
        M.add('arm', 'metal_painted_grey', lathe([(r1, -0.0), (r1, 0.0)], 8, pts[i+1][0], 0).move(0, pts[i+1][1], 0)) if False else None
    M.cyl('arm', 'metal_painted_grey', 0.085, 0.14, 8, 5.85, 0, 0)
    # luminaire (cobra-style)
    lum = tbox(1.55, 6.12, -0.17, 2.35, 6.34, 0.17, 0.8)
    M.add('luminaire', 'metal_painted_grey', lum)
    M.box('luminaire', 'metal_painted_grey', 1.5, 6.3, -0.12, 1.75, 6.42, 0.12, 0.03)
    M.box('lens', 'lamp_emissive', 1.68, 6.1, -0.13, 2.2, 6.125, 0.13)
    M.cn('lamp_centre', (1.95, 6.1, 0), (0, -1, 0)); M.cn('cable_anchor', (1.75, 6.25, 0), (1, 0, 0))
    M.det('arm', 'swan-neck arm + luminaire', (0, 5.9, 0))
    return M

def PROP_04():
    M = Model('PROP_04', 'street_props', 'Highway lamp: 10 m 12-sided pole, twin truss arms with cobra luminaires, flanged base with gussets')
    M.add('base', 'galvanized_steel', cylb(0.5, 0.06, 12, 0, b=0.01))
    bolts(M, 'base', [(0.42*math.cos(a*math.pi/3), 0.42*math.sin(a*math.pi/3)) for a in range(6)], 0.06, 0.03, 0.06)
    for a in range(4):
        M.add('base', 'galvanized_steel', ext('x', [(0.2, -0.03), (0.42, -0.03), (0.2, -0.03)], 0, 0.0) if False else prof_beam((0.2*math.cos(a*math.pi/2), 0.06, 0.2*math.sin(a*math.pi/2)), (0.2*math.cos(a*math.pi/2), 0.6, 0.2*math.sin(a*math.pi/2)), [(-0.015, -0.015), (0.2, -0.015), (0.2, 0.015), (-0.015, 0.015)]) if False else
              beam((0.3*math.cos(a*math.pi/2), 0.33, 0.3*math.sin(a*math.pi/2)), (0.15*math.cos(a*math.pi/2), 0.55, 0.15*math.sin(a*math.pi/2)), 0.04, 0.04))
    M.add('pole', 'metal_painted_grey', cyl(0.2, 9.6, 12, 0.06, r1=0.095))
    M.add('pole', 'metal_painted_grey', cylb(0.14, 0.25, 12, 9.6, b=0.03))
    M.box('winch_door', 'galvanized_steel', -0.1, 1.0, 0.16, 0.1, 1.7, 0.22, 0.015)
    for s in (-1, 1):
        M.tube('arm', 'metal_painted_grey', (s*0.1, 9.75, 0), (s*3.2, 10.15, 0), 0.07, 8, 0.045)
        M.beam('arm', 'metal_painted_grey', (s*0.1, 9.15, 0), (s*2.2, 10.08, 0), 0.06, 0.06)
        M.beam('arm', 'metal_painted_grey', (s*0.8, 9.55, 0), (s*2.2, 10.08, 0), 0.04, 0.04) if False else None
        lum = tbox(s*3.0-0.6, 10.0, -0.22, s*3.0+0.6, 10.3, 0.22, 0.75) if s > 0 else tbox(-3.6, 10.0, -0.22, -2.4, 10.3, 0.22, 0.75)
        M.add('luminaire', 'metal_painted_grey', lum)
        M.box('lens', 'lamp_emissive', s*3.0-0.45, 9.985, -0.17, s*3.0+0.45, 10.0, 0.17)
        M.cn('lamp_'+('R' if s > 0 else 'L'), (s*3.0, 9.98, 0), (0, -1, 0))
    M.det('arm', 'twin arms + luminaires (top assembly)', (0, 9.7, 0))
    return M

# ---------------------------------------------------------------- PROP_05 bus stop
def PROP_05():
    M = Model('PROP_05', 'street_props', 'Bus stop shelter 3.8 x 1.7 m: canopy, glazed back/side panels, slatted bench, lit ad panel, route sign pole')
    M.box('plinth', 'concrete_weathered', -2.0, 0, -1.0, 2.0, 0.1, 1.0, 0.02)
    for x in (-1.75, 1.75):
        for z in (-0.75, 0.75):
            M.box('columns', 'galvanized_steel', x-0.05, 0.1, z-0.05, x+0.05, 2.6, z+0.05, 0.012)
    M.add('canopy', 'metal_painted_grey', box(-2.05, 2.6, -1.0, 2.05, 2.7, 1.0, 0.02))
    M.add('canopy', 'paint_blue', tbox(-2.15, 2.7, -1.1, 2.15, 2.85, 1.1, 0.88))
    for z in (-1.1, 1.1): M.box('canopy', 'galvanized_steel', -2.15, 2.62, z-0.02, 2.15, 2.72, z+0.02)
    M.box('back_panel', 'glass_tinted', -1.7, 0.45, -0.72, 1.7, 2.55, -0.7)
    M.box('side_panel', 'glass_tinted', -1.72, 0.45, -0.7, -1.7, 2.55, 0.72) if False else None
    M.box('side_panel', 'glass_tinted', 1.7, 0.45, -0.7, 1.72, 2.55, 0.0) if False else None
    for x in (-1.0, 0.0, 1.0): M.box('back_frame', 'galvanized_steel', x-0.025, 0.4, -0.73, x+0.025, 2.6, -0.69)
    M.box('back_frame', 'galvanized_steel', -1.75, 0.4, -0.73, 1.75, 0.46, -0.69); M.box('back_frame', 'galvanized_steel', -1.75, 2.53, -0.73, 1.75, 2.6, -0.69)
    # bench
    for i in range(4): M.box('bench', 'timber_warm', -1.0, 0.5, -0.5+i*0.13, 1.0, 0.54, -0.4+i*0.13, 0.01)
    for x in (-1.0, 0.0, 1.0): M.box('bench', 'galvanized_steel', x-0.025, 0.1, -0.5, x+0.025, 0.5, -0.45) if False else M.box('bench', 'galvanized_steel', x-0.03, 0.1, -0.45, x+0.03, 0.5, -0.4)
    M.box('bench', 'galvanized_steel', -1.02, 0.46, -0.52, 1.02, 0.5, -0.4) if False else None
    for x in (-1.0, 1.0): M.beam('bench', 'galvanized_steel', (x, 0.5, 0.0), (x, 0.8, 0.0), 0.04, 0.04); M.box('bench', 'galvanized_steel', x-0.03, 0.78, -0.5, x+0.03, 0.82, 0.0)
    # ad panel (end)
    M.box('ad_frame', 'brushed_metal', 1.82, 0.5, -0.5, 1.98, 2.3, 0.45, 0.02)
    M.box('ad_panel', 'ad_panel', 1.98, 0.6, -0.42, 2.0, 2.2, 0.37)
    M.box('ad_panel', 'glass_tinted', 2.0, 0.6, -0.42, 2.012, 2.2, 0.37)
    # route sign
    M.add('sign_pole', 'metal_painted_grey', cyl(0.035, 3.3, 8, 0.1, -2.3, 0.6, 0.03))
    M.box('sign', 'sign_blue', -2.5, 2.7, 0.57, -2.1, 3.1, 0.6, 0.01)
    M.box('sign_pictogram', 'sign_white', -2.42, 2.78, 0.6, -2.18, 2.98, 0.612)
    M.cn('kerb_edge', (0, 0, 1.0), (0, 0, 1), note='front faces +Z; place with +Z toward road')
    M.det('canopy', 'roof canopy (separates from columns)', (0, 2.6, 0)); M.det('back_panel', 'glass panel', (0, 1.5, -0.7))
    return M

def PROP_06():
    M = Model('PROP_06', 'street_props', 'Public bench 1.8 m: timber seat/back slats, cast-iron style side frames with armrests')
    for sx in (-0.82, 0.82):
        M.box('foot', 'rubber_dark', sx-0.06, 0, -0.26, sx+0.06, 0.03, 0.26, 0.01)
        M.beam('frame', 'rust_metal' if False else 'metal_painted_grey', (sx, 0.03, 0.2), (sx, 0.43, 0.2), 0.055, 0.055)
        M.beam('frame', 'metal_painted_grey', (sx, 0.03, -0.2), (sx, 0.46, -0.2), 0.055, 0.055)
        M.beam('frame', 'metal_painted_grey', (sx, 0.46, -0.2), (sx, 0.9, -0.3), 0.05, 0.05)
        M.beam('frame', 'metal_painted_grey', (sx, 0.43, -0.22), (sx, 0.43, 0.25), 0.055, 0.04)
        M.beam('frame', 'metal_painted_grey', (sx, 0.65, -0.25), (sx, 0.65, 0.24), 0.045, 0.04)
        M.beam('frame', 'metal_painted_grey', (sx, 0.65, 0.24), (sx, 0.43, 0.2), 0.04, 0.04) if False else None
        M.add('armrest', 'brushed_metal', box(sx-0.035, 0.62, -0.18, sx+0.035, 0.68, 0.26, 0.02))
        M.beam('frame', 'metal_painted_grey', (sx, 0.45, 0.2), (sx, 0.65, 0.22), 0.04, 0.04)
    for i in range(5): M.add('seat', 'timber_warm', box(-0.88, 0.46, -0.22+i*0.1, 0.88, 0.5, -0.14+i*0.1, 0.008))
    for i in range(3):
        y = 0.58+i*0.14
        M.add('backrest', 'timber_warm', box(-0.88, y, -0.3-(y-0.5)*0.12-0.035, 0.88, y+0.1, -0.3-(y-0.5)*0.12, 0.008))
    M.cn('seat_centre', (0, 0.5, 0), (0, 1, 0)); M.cn('ground', (0, 0, 0), (0, -1, 0))
    return M

def PROP_07():
    M = Model('PROP_07', 'street_props', 'Urban trash bin 0.55 m dia: tapered shell, banded straps, rim, lid with opening, hinged flap, base ring')
    M.add('shell', 'paint_green', lathe([(0.2, 0.06), (0.255, 0.1), (0.27, 0.2), (0.27, 0.85)], 14))
    M.add('base_ring', 'rubber_dark', lathe([(0.19, 0), (0.24, 0.0), (0.24, 0.07), (0.2, 0.08)], 14) if False else cylb(0.24, 0.07, 14, 0, b=0.012))
    for y in (0.3, 0.62): M.add('straps', 'brushed_metal', lathe([(0.274, y), (0.279, y+0.01), (0.279, y+0.05), (0.274, y+0.06)], 14))
    for a in range(0, 360, 45):
        M.add('slats', 'brushed_metal', box(-0.012, 0.12, 0.268, 0.012, 0.82, 0.282, 0.004).rot('y', a)) if False else None
    M.add('rim', 'brushed_metal', merge([band(0.14, 0.29, 0.85, 0.93, k*45, (k+1)*45, 2, rt0=0.16, rt1=0.28) for k in range(8)]))
    M.add('lid', 'paint_green', merge([band(0.12, 0.3, 0.93, 0.98, k*45, (k+1)*45, 2) for k in range(8)]))
    M.add('cavity', 'rubber_dark', cyl(0.135, 0.01, 12, 0.84))
    M.box('flap', 'brushed_metal', -0.11, 0.9, -0.12, 0.11, 0.935, -0.02, 0.008) if False else M.box('flap', 'brushed_metal', -0.1, 0.99, 0.0, 0.1, 1.02, 0.12, 0.008)
    M.add('flap_hinge', 'brushed_metal', tube((-0.11, 1.0, -0.0), (0.11, 1.0, 0.0), 0.012, 6))
    return M

def PROP_08():
    M = Model('PROP_08', 'street_props', 'Fire hydrant 0.8 m: base flange, barrel, bonnet, 2 side nozzles + pumper nozzle, pentagonal operating nut, chains')
    M.add('base', 'brushed_metal', cylb(0.17, 0.05, 10, 0, b=0.01))
    M.add('barrel', 'traffic_red', lathe([(0.115, 0.05), (0.125, 0.12), (0.12, 0.45), (0.14, 0.5), (0.14, 0.56)], 12))
    M.add('bonnet', 'safety_yellow', lathe([(0.13, 0.56), (0.15, 0.58), (0.15, 0.62), (0.12, 0.68), (0.06, 0.74), (0.01, 0.76)], 12))
    M.add('nut', 'brushed_metal', cyl(0.045, 0.06, 5, 0.76))
    for s in (-1, 1):
        M.tube('nozzle', 'traffic_red', (s*0.1, 0.4, 0), (s*0.25, 0.4, 0), 0.06, 10)
        M.add('nozzle_cap', 'brushed_metal', cylb(0.075, 0.05, 10, 0, 0, 0, 0.01).rot('z', -90*s).move(s*0.26, 0.4, 0))
        M.tube('nozzle_cap', 'brushed_metal', (s*0.275, 0.4, 0), (s*0.3, 0.4, 0), 0.03, 6)
    M.tube('pumper', 'traffic_red', (0, 0.32, 0.1), (0, 0.32, 0.25), 0.085, 12)
    M.add('pumper_cap', 'brushed_metal', cylb(0.1, 0.05, 12, 0, 0, 0, 0.012).rot('x', 90).move(0, 0.32, 0.255))
    M.tube('chain', 'rubber_dark', (0.25, 0.4, 0.0), (0.2, 0.3, 0.1), 0.008, 4) if False else None
    M.cn('ground', (0, 0, 0), (0, -1, 0)); M.det('bonnet', 'bonnet + nut (shears off)', (0, 0.56, 0))
    return M

def PROP_09():
    M = Model('PROP_09', 'street_props', 'Street bollard 1.0 m: base flange with bolts, collar, chamfered shaft, reflective band, domed cap')
    base_plate(M, 'base', 0.3, 0.025)
    M.add('collar', 'galvanized_steel', cylb(0.13, 0.1, 12, 0.025, b=0.02))
    M.add('shaft', 'metal_painted_grey', cyl(0.085, 0.62, 12, 0.125))
    M.add('band', 'safety_yellow', cyl(0.09, 0.09, 12, 0.7)); M.add('band', 'safety_yellow', cyl(0.09, 0.09, 12, 0.5)) if False else None
    M.add('band', 'marking_white', cyl(0.088, 0.04, 12, 0.56))
    M.add('cap', 'brushed_metal', lathe([(0.09, 0.745), (0.1, 0.76), (0.1, 0.79), (0.085, 0.9), (0.05, 0.97), (0.015, 1.0)], 12))
    M.det('shaft', 'bollard shaft + cap (sheared at collar)', (0, 0.125, 0))
    return M

def PROP_10():
    M = Model('PROP_10', 'street_props', 'Modular W-beam guardrail 4 m: I-section posts, spacer blocks, corrugated rail with splice bolts; modules chain at z=+/-2')
    for z in (-1.9, 0.0, 1.9):
        M.add('posts', 'galvanized_steel', prof_beam((0, -0.1, z), (0, 0.78, z), ibeam_poly(0.1, 0.15, 0.012, 0.01)))
        M.box('plate', 'galvanized_steel', -0.1, -0.1, z-0.1, 0.1, -0.085, z+0.1) if False else None
        M.box('spacer', 'timber_warm' if False else 'concrete_weathered', 0.07, 0.4, z-0.05, 0.19, 0.66, z+0.05, 0.01)
        M.add('bolts', 'brushed_metal', tube((0.19, 0.53, z), (0.26, 0.53, z), 0.02, 6))
    W = [(-.155, 0), (-.12, 0), (-.095, .07), (-.06, .07), (-.035, 0), (.035, 0), (.06, .07), (.095, .07), (.12, 0), (.155, 0), (.155, .014),
         (.12, .014), (.095, .084), (.06, .084), (.035, .014), (-.035, .014), (-.06, .084), (-.095, .084), (-.12, .014), (-.155, .014)]
    M.add('rail', 'galvanized_steel', loft([[(0.19+b, 0.53+a, z) for a, b in W] for z in (-2.0, 2.0)]))
    for z in (-1.9, 1.9):
        for dy in (-0.07, 0.07): M.add('bolts', 'brushed_metal', cyl(0.018, 0.03, 6, 0.0, 0, 0).rot('z', 90).move(0.29, 0.53+dy, z))
    M.cn('end_A', (0.19, 0.53, -2.0), (0, 0, -1), mates='PROP_10'); M.cn('end_B', (0.19, 0.53, 2.0), (0, 0, 1), mates='PROP_10')
    M.det('rail', 'W-beam rail', (0.19, 0.53, 0)); M.det('posts', 'posts', (0, 0, 0))
    return M

def PROP_11():
    M = Model('PROP_11', 'street_props', 'Jersey concrete barrier 3 m: sloped faces, chamfered edges, lifting loops, interlocking end pockets, reflectors')
    pr = [(-0.3, 0), (-0.3, 0.09), (-0.215, 0.33), (-0.125, 0.8), (-0.1, 0.82), (0.1, 0.82), (0.125, 0.8), (0.215, 0.33), (0.3, 0.09), (0.3, 0)]
    M.add('body', 'concrete_pale', profile_ext(pr, -1.5, 1.5))
    M.box('foot_skirt', 'concrete_weathered', -0.31, 0, -1.5, 0.31, 0.04, 1.5, 0.01)
    for z in (-1.5, 1.5):
        sgn = 1 if z < 0 else -1
        M.box('end_pocket', 'concrete_core', -0.1, 0.35, z, 0.1, 0.6, z+sgn*0.05) if False else None
        M.beam('lifting_loop', 'rebar', (-0.07, 0.82, z+sgn*0.45), (-0.07, 0.9, z+sgn*0.45), 0.02, 0.02)
        M.beam('lifting_loop', 'rebar', (0.07, 0.82, z+sgn*0.45), (0.07, 0.9, z+sgn*0.45), 0.02, 0.02)
        M.beam('lifting_loop', 'rebar', (-0.07, 0.9, z+sgn*0.45), (0.07, 0.9, z+sgn*0.45), 0.02, 0.02)
    for s in (-1, 1):
        for z in (-1.0, 0.0, 1.0):
            M.box('reflector', 'traffic_red' if s > 0 else 'marking_white', s*0.19-0.0 if False else (0.17 if s > 0 else -0.19), 0.5, z-0.05, (0.19 if s > 0 else -0.17), 0.55, z+0.05, 0.005) if False else M.box('reflector', 'safety_orange', s*0.165-0.005 if False else min(s*0.17, s*0.185), 0.52, z-0.05, max(s*0.17, s*0.185), 0.56, z+0.05)
    M.box('top_stripe', 'safety_yellow', -0.1, 0.82, -1.5, 0.1, 0.83, -0.9) if False else None
    M.cn('end_A', (0, 0.4, -1.5), (0, 0, -1)); M.cn('end_B', (0, 0.4, 1.5), (0, 0, 1))
    return M

def PROP_12():
    M = Model('PROP_12', 'street_props', 'Traffic cone 0.72 m: weighted square rubber base, orange body, two reflective collars')
    M.add('base', 'rubber_dark', box(-0.23, 0, -0.23, 0.23, 0.045, 0.23, 0.012))
    M.add('base', 'rubber_dark', tbox(-0.2, 0.045, -0.2, 0.2, 0.07, 0.2, 0.9))
    r = lambda y: 0.135-0.115*(y-0.07)/0.65
    segs = [(0.07, 0.2, 'safety_orange', 0), (0.2, 0.3, 'marking_white', 0.004), (0.3, 0.4, 'safety_orange', 0), (0.4, 0.5, 'marking_white', 0.004), (0.5, 0.72, 'safety_orange', 0)]
    for y0, y1, m, o in segs: M.add('body_'+m, m, lathe([(r(y0)+o, y0), (r(y1)+o, y1)], 14))
    M.add('tip', 'safety_orange', cyl(0.02, 0.025, 14, 0.72, r1=0.016))
    M.add('tip', 'safety_orange', lathe([(0.02, 0.72), (0.012, 0.745)], 14))
    return M

def PROP_13():
    M = Model('PROP_13', 'street_props', 'Street-name sign: 3.2 m pole, finial, two perpendicular blades with white borders on brackets; sign_face groups are decal surfaces')
    base_plate(M, 'base', 0.22, 0.02, bolt=False)
    M.add('pole', 'galvanized_steel', cyl(0.04, 3.1, 8, 0.02))
    M.add('pole', 'galvanized_steel', lathe([(0.045, 3.12), (0.055, 3.15), (0.045, 3.2), (0.01, 3.26)], 8))
    for yb, ry, L in ((2.8, 0, 0.9), (2.5, 90, 0.75)):
        T = Model('t', 'x')
        T.box('blade_border', 'sign_white', 0.06, -0.11, -0.012, 0.06+L, 0.11, 0.012, 0.006)
        T.box('sign_face_decal', 'sign_green', 0.075, -0.095, 0.012, 0.045+L, 0.095, 0.016)
        T.box('bracket', 'galvanized_steel', 0.0, 0.1, -0.015, 0.1, 0.12, 0.015)
        T.box('bracket', 'galvanized_steel', 0.0, -0.12, -0.015, 0.1, -0.1, 0.015)
        T.tube('bracket', 'galvanized_steel', (0.0, -0.13, 0), (0.0, 0.13, 0), 0.0, 6) if False else None
        T.add('clamp', 'brushed_metal', cyl(0.05, 0.03, 8, -0.12, 0, 0) if False else tube((0.0, -0.12, 0), (0.0, -0.09, 0), 0.052, 8))
        T.add('clamp', 'brushed_metal', tube((0.0, 0.09, 0), (0.0, 0.12, 0), 0.052, 8))
        put(M, T, 0, yb, 0, ry)
        # back-side border
    M.cn('decal_A', (0.45, 2.8, 0.016), (0, 0, 1)); M.cn('decal_B', (0.0, 2.5, 0.38), (1, 0, 0))
    return M

def PROP_14():
    M = Model('PROP_14', 'street_props', 'Billboard 8 x 3.5 m: twin I-beam columns on footings, rear bracing, service catwalk with rail, frame + face panel, two floodlights')
    for x in (-2.6, 2.6):
        M.box('footing', 'concrete_weathered', x-0.6, 0, -0.6, x+0.6, 0.35, 0.6, 0.04)
        M.add('column', 'galvanized_steel', prof_beam((x, 0.35, 0), (x, 6.2, 0), ibeam_poly(0.4, 0.4, 0.04, 0.03)))
        M.box('base_plate', 'galvanized_steel', x-0.3, 0.35, -0.3, x+0.3, 0.4, 0.3, 0.01)
    M.beam('brace', 'galvanized_steel', (-2.6, 0.9, -0.05), (2.6, 3.8, -0.05), 0.12, 0.12)
    M.beam('brace', 'galvanized_steel', (2.6, 0.9, -0.05), (-2.6, 3.8, -0.05), 0.12, 0.12)
    for x in (-2.6, 2.6):
        M.beam('rear_strut', 'galvanized_steel', (x, 0.4, -0.2), (x*1.0, 3.6, -2.0), 0.14, 0.14) if False else M.beam('rear_strut', 'galvanized_steel', (x, 0.4, -1.8), (x, 4.0, -0.2), 0.14, 0.14)
        M.box('rear_foot', 'concrete_weathered', x-0.4, 0, -2.2, x+0.4, 0.3, -1.4, 0.03)
    for y in (4.6, 6.0): M.box('girder', 'metal_painted_grey', -4.1, y-0.1, -0.25, 4.1, y+0.1, -0.05, 0.015)
    M.box('frame', 'paint_navy', -4.3, 4.3, -0.15, 4.3, 7.9, 0.12, 0.04)
    M.box('face', 'ad_panel', -4.05, 4.55, 0.12, 4.05, 7.65, 0.15)
    M.box('catwalk', 'brushed_metal', -4.2, 4.0, 0.12, 4.2, 4.06, 0.85)
    for x in [-4.2+0.84*i for i in range(11)]: M.box('catwalk_rail', 'safety_yellow', x-0.025, 4.06, 0.8, x+0.025, 5.0, 0.85)
    M.box('catwalk_rail', 'safety_yellow', -4.2, 4.95, 0.8, 4.2, 5.0, 0.85); M.box('catwalk_rail', 'safety_yellow', -4.2, 4.5, 0.8, 4.2, 4.54, 0.85)
    for x in (-2.0, 2.0):
        M.beam('flood_arm', 'galvanized_steel', (x, 7.9, 0.0), (x, 7.95, 1.2), 0.05, 0.05)
        M.add('flood', 'metal_painted_grey', tbox(x-0.3, 7.78, 1.1, x+0.3, 7.95, 1.45, 0.8))
        M.box('flood_lens', 'lamp_emissive', x-0.26, 7.76, 1.12, x+0.26, 7.78, 1.42)
    M.cn('face_centre', (0, 6.1, 0.15), (0, 0, 1), width=8.1, height=3.1)
    M.det('face', 'face panel', (0, 6.1, 0.1))
    return M

def PROP_15():
    M = Model('PROP_15', 'street_props', 'Double-sided advertising kiosk 1.2 x 2.2 m: plinth, frame, glazed display panels, lit crown, feet')
    M.box('plinth', 'concrete_weathered', -0.7, 0, -0.3, 0.7, 0.12, 0.3, 0.03)
    M.box('foot', 'rubber_dark', -0.62, 0.12, -0.22, 0.62, 0.2, 0.22, 0.015)
    M.box('body', 'paint_navy', -0.55, 0.2, -0.17, 0.55, 2.1, 0.17, 0.04)
    for s in (-1, 1):
        z = s*0.17
        M.box('display', 'ad_panel', -0.47, 0.35, z if s > 0 else z-0.012, 0.47, 1.95, z+0.012 if s > 0 else z)
        M.box('glass', 'glass_tinted', -0.47, 0.35, z+0.012 if s > 0 else z-0.024, 0.47, 1.95, z+0.024 if s > 0 else z-0.012)
        M.box('trim', 'brushed_metal', -0.5, 0.31, z if s > 0 else z-0.03, 0.5, 0.35, z+0.03 if s > 0 else z)
        M.box('trim', 'brushed_metal', -0.5, 1.95, z if s > 0 else z-0.03, 0.5, 1.99, z+0.03 if s > 0 else z)
    M.add('crown', 'metal_painted_grey', tbox(-0.6, 2.1, -0.22, 0.6, 2.28, 0.22, 0.85))
    M.box('crown_light', 'lamp_emissive', -0.45, 2.08, -0.15, 0.45, 2.1, 0.15)
    M.box('side_vent', 'rubber_dark', 0.55, 0.5, -0.1, 0.57, 1.5, 0.1)
    M.cn('display_front', (0, 1.15, 0.24), (0, 0, 1)); M.cn('display_back', (0, 1.15, -0.24), (0, 0, -1))
    return M

def PROP_16():
    M = Model('PROP_16', 'street_props', 'Public planter 1.5 x 0.8 x 0.65 m: real 0.1 m walls, floor, coping, corner pilasters, recessed soil bed with planting hole (no plant)')
    w, d, h, t = 1.5, 0.8, 0.65, 0.1
    M.box('floor', 'concrete_weathered', -w/2, 0, -d/2, w/2, 0.1, d/2, 0.015)
    M.box('wall', 'concrete_pale', -w/2, 0.1, -d/2, w/2, h, -d/2+t, 0.015); M.box('wall', 'concrete_pale', -w/2, 0.1, d/2-t, w/2, h, d/2, 0.015)
    M.box('wall', 'concrete_pale', -w/2, 0.1, -d/2+t, -w/2+t, h, d/2-t, 0.015); M.box('wall', 'concrete_pale', w/2-t, 0.1, -d/2+t, w/2, h, d/2-t, 0.015)
    M.box('coping', 'concrete_weathered', -w/2-0.03, h, -d/2-0.03, w/2+0.03, h+0.06, d/2+0.03, 0.015) if False else None
    for sx in (-1, 1):
        for sz in (-1, 1): M.box('pilaster', 'concrete_weathered', sx*(w/2-0.06)-0.07 if False else min(sx*(w/2+0.02), sx*(w/2-0.15)), 0.05, min(sz*(d/2+0.02), sz*(d/2-0.15)), max(sx*(w/2+0.02), sx*(w/2-0.15)), h+0.06, max(sz*(d/2+0.02), sz*(d/2-0.15)), 0.02)
    M.box('band', 'concrete_weathered', -w/2-0.012, 0.3, -d/2-0.012, w/2+0.012, 0.36, -d/2) if False else None
    for s in (-1, 1): M.box('band', 'concrete_weathered', -w/2+0.17, 0.3, s*(d/2+0.012) - (0.012 if s < 0 else 0)*0 if False else (-d/2-0.012 if s < 0 else d/2), w/2-0.17, 0.36, (-d/2 if s < 0 else d/2+0.012))
    M.add('soil', 'soil', tbox(-w/2+t, 0.1, -d/2+t, w/2-t, 0.52, d/2-t, 0.97))
    M.add('planting_hole', 'rubber_dark', cyl(0.14, 0.01, 12, 0.521))
    M.add('soil_ring', 'soil', merge([band(0.14, 0.22, 0.52, 0.56, k*60, (k+1)*60, 2) for k in range(6)]))
    M.cn('planting_point', (0, 0.52, 0), (0, 1, 0), note='attach foliage/tree asset here')
    return M

def PROP_17():
    M = Model('PROP_17', 'street_props', 'Bicycle rack: 5 inverted-U hoops with cross-bar and grounded flange plates, 3 m run')
    zs = [-1.2+0.6*i for i in range(5)]
    for z in zs:
        pts = [(0.0, 0.02)]
        arc = [(0.0, 0.0)]
        P = [(-0.4, 0.0), (-0.4, 0.6)] + [(-0.4*math.cos(math.radians(a)) if False else 0.4*math.cos(math.radians(180-a)), 0.6+0.4*math.sin(math.radians(a))) for a in range(15, 166, 15)] + [(0.4, 0.6), (0.4, 0.0)]
        for i in range(len(P)-1): M.add('hoop', 'galvanized_steel', tube((P[i][0], P[i][1], z), (P[i+1][0], P[i+1][1], z), 0.025, 8))
        for sx in (-0.4, 0.4):
            M.box('flange', 'brushed_metal', sx-0.07, 0, z-0.07, sx+0.07, 0.015, z+0.07, 0.004)
            bolts(M, 'flange', [(sx-0.045, z-0.045), (sx+0.045, z+0.045)], 0.015, 0.012, 0.012)
    M.add('crossbar', 'galvanized_steel', tube((0.0, 0.3, zs[0]), (0.0, 0.3, zs[-1]), 0.02, 8)) if False else None
    for sx in (-0.4, 0.4): M.add('crossbar', 'galvanized_steel', tube((sx, 0.22, zs[0]), (sx, 0.22, zs[-1]), 0.018, 8))
    M.cn('end_A', (0, 0, -1.5), (0, 0, -1), mates='PROP_17'); M.cn('end_B', (0, 0, 1.5), (0, 0, 1))
    return M

def PROP_18():
    M = Model('PROP_18', 'street_props', 'Parking meter 1.45 m: base plate, post, rounded head with glass display, keypad, coin/card slots, solar panel')
    base_plate(M, 'base', 0.26, 0.02)
    M.add('post', 'metal_painted_grey', cyl(0.04, 1.0, 10, 0.02))
    M.add('post', 'metal_painted_grey', cylb(0.06, 0.08, 10, 0.02, b=0.015))
    M.box('head', 'paint_navy', -0.13, 1.02, -0.09, 0.13, 1.4, 0.09, 0.04)
    M.add('head', 'paint_navy', tbox(-0.13, 1.4, -0.09, 0.13, 1.45, 0.09, 0.8))
    M.box('screen', 'glass_tinted', -0.095, 1.28, 0.088, 0.095, 1.37, 0.098)
    M.box('screen_text', 'signal_green', -0.06, 1.31, 0.098, 0.06, 1.34, 0.103)
    M.box('keypad', 'rubber_dark', -0.09, 1.1, 0.088, 0.03, 1.24, 0.096, 0.005)
    for i in range(3):
        for j in range(3): M.box('keys', 'brushed_metal', -0.085+i*0.04, 1.11+j*0.04, 0.096, -0.055+i*0.04, 1.135+j*0.04, 0.104, 0.004)
    M.box('coin_slot', 'rubber_dark', 0.05, 1.16, 0.088, 0.1, 1.2, 0.098); M.box('coin_slot', 'brushed_metal', 0.065, 1.17, 0.098, 0.085, 1.19, 0.103)
    M.box('card_slot', 'rubber_dark', 0.045, 1.07, 0.088, 0.105, 1.1, 0.098)
    M.add('solar', 'paint_blue', box(-0.1, 1.45, -0.07, 0.1, 1.465, 0.07, 0.004).rot('x', -15, (0, 1.45, 0)))
    M.box('sticker', 'safety_yellow', -0.11, 1.05, 0.088, -0.095, 1.09, 0.093) if False else None
    M.cn('head_top', (0, 1.465, 0), (0, 1, 0))
    return M

PROPS = [PROP_01, PROP_02, PROP_03, PROP_04, PROP_05, PROP_06, PROP_07, PROP_08, PROP_09, PROP_10, PROP_11, PROP_12, PROP_13, PROP_14, PROP_15, PROP_16, PROP_17, PROP_18]
