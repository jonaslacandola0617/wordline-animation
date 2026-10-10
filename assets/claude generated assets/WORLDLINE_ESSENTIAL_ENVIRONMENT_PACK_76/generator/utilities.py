from lib import *
from props import put, bolts, base_plate, louvre, insulator

def PYL(M, g, mat, x, z, h=1.0): pass

def UTILITY_01():
    M = Model('UTILITY_01', 'utilities', 'Wooden utility pole 10 m: tapered log, two crossarms with braces, 5 pin insulators, climbing pegs, ground sleeve')
    M.add('pole', 'wood_weathered', cyl(0.2, 10.0, 10, 0, r1=0.12, ph=0.2))
    M.add('ground_sleeve', 'rubber_dark', cyl(0.215, 0.5, 10, 0.0, 0, 0, 0.21, 0.2))
    M.add('pole_cap', 'timber_warm', cyl(0.12, 0.12, 10, 10.0, r1=0.04, ph=0.2) if False else lathe([(0.12, 10.0), (0.08, 10.1), (0.02, 10.16)], 10, 0, 0, 0.2))
    for y, L, tag in ((9.2, 1.3, 'upper'), (8.5, 0.9, 'lower')):
        M.box('crossarm_'+tag, 'timber_warm', -L, y-0.07, -0.07, L, y+0.07, 0.07, 0.015)
        M.box('crossarm_'+tag, 'galvanized_steel', -0.12, y-0.1, -0.11, 0.12, y+0.1, -0.095) if False else None
        for s in (-1, 1):
            M.beam('brace_'+tag, 'timber_warm', (s*0.08, y-0.75, 0.13), (s*(L*0.65), y-0.07, 0.1), 0.06, 0.06)
            M.add('bolt_'+tag, 'galvanized_steel', tube((s*0.35, y, -0.08), (s*0.35, y, 0.1), 0.012, 6))
        M.add('through_bolt', 'galvanized_steel', tube((0, y, -0.14), (0, y, 0.16), 0.018, 6))
        M.box('crossarm_'+tag, 'rubber_dark', -0.04, y-0.04, -0.12, 0.04, y+0.04, -0.07) if False else None
    for x in (-1.1, 0.0, 1.1): insulator(M, 'insulator_upper', x, 9.27, 0, 0.3, 0.075)
    insulator(M, 'insulator_top', 0, 10.1, 0, 0.28, 0.07)
    for x in (-0.8, 0.8): insulator(M, 'insulator_lower', x, 8.57, 0, 0.26, 0.065)
    for i, y in enumerate([2.2+0.5*k for k in range(7)]):
        M.add('pegs', 'galvanized_steel', tube((0.0, y, 0.0), (0.0, y, 0.28), 0.015, 5).rot('y', 70 if i % 2 else 250)) if False else M.add('pegs', 'galvanized_steel', tube((0, y, 0), (0.22 if i % 2 else -0.22, y, 0.0), 0.014, 5) if False else tube((0.0, y, 0.0), (0.0, y, 0.0), 0.0, 3) if False else cyl(0.014, 0.12, 5, 0, 0, 0).rot('x', 90).move(0.0, y, 0.14).rot('y', i*100, (0, y, 0)))
    M.box('ground_wire_staple', 'galvanized_steel', 0.14, 1.0, -0.02, 0.17, 7.0, 0.02, 0.005)
    for nm, p in (('anchor_top', (0, 10.3, 0)), ('anchor_U1', (-1.1, 9.5, 0)), ('anchor_U2', (0, 9.5, 0)), ('anchor_U3', (1.1, 9.5, 0)), ('anchor_L1', (-0.8, 8.78, 0)), ('anchor_L2', (0.8, 8.78, 0))):
        M.cn('cable_'+nm, p, (0, 1, 0))
    M.det('crossarm_upper', 'upper crossarm + insulators', (0, 9.2, 0))
    return M

def UTILITY_02():
    M = Model('UTILITY_02', 'utilities', 'Pole-mounted distribution transformer on 1.8 m pole section: ribbed tank, domed lid, 3 HV bushings, 2 LV terminals, hanger lugs, straps')
    M.add('pole_section', 'wood_weathered', cyl(0.2, 2.2, 10, -0.2, 0, -0.6, 0.17, 0.2))
    M.box('hanger_bar', 'galvanized_steel', -0.04, 0.9, -0.45, 0.04, 1.65, -0.38, 0.01)
    M.add('tank', 'insulator_grey', lathe([(0.0, 0.5), (0.36, 0.5), (0.4, 0.55), (0.4, 1.55), (0.36, 1.62), (0.28, 1.68), (0.0, 1.7)], 14).move(0, 0, 0))
    for y in (0.75, 1.0, 1.25, 1.45): M.add('ribs', 'metal_painted_grey', lathe([(0.4, y), (0.425, y+0.02), (0.425, y+0.06), (0.4, y+0.08)], 14))
    M.add('lid_ring', 'brushed_metal', lathe([(0.29, 1.68), (0.31, 1.7), (0.3, 1.74), (0.25, 1.76)], 14))
    for i, a in enumerate((-0.2, 0.0, 0.2)): insulator(M, 'bushing_HV', a*1.1, 1.74, 0.0 if i != 1 else 0.12, 0.42, 0.075, 'insulator_grey') if False else insulator(M, 'bushing_HV', a*1.1, 1.74 if False else 1.7, 0.0, 0.42, 0.075, 'insulator_grey')
    for a in (-0.22, 0.0, 0.22): M.add('terminal_HV', 'brushed_metal', cyl(0.03, 0.07, 8, 2.12, a*1.1, 0.0, 0.02))
    for s in (-1, 1):
        M.add('terminal_LV', 'brushed_metal', cyl(0.03, 0.14, 8, 1.4, 0, 0).rot('x', 90).move(s*0.17, 1.22, 0.38) if False else tube((s*0.17, 1.35, 0.38), (s*0.17, 1.35, 0.5), 0.03, 8))
        M.add('terminal_LV', 'brushed_metal', tube((s*0.17, 1.35, 0.5), (s*0.17, 1.35, 0.54), 0.045, 8))
        M.add('bushing_LV', 'insulator_ceramic', lathe([(0.05, 1.28), (0.07, 1.3), (0.05, 1.35)], 8, s*0.17, 0.38)) if False else None
    for y in (0.7, 1.4):                  # mounting straps to pole
        M.box('mount_strap', 'galvanized_steel', -0.35, y, -0.41, 0.35, y+0.05, -0.34, 0.01)
    M.box('lug', 'galvanized_steel', -0.2, 0.8, -0.4, 0.2, 0.95, 0.38) if False else None
    for s in (-1, 1): M.box('hanger_lug', 'galvanized_steel', s*0.3-0.03, 1.25, -0.38, s*0.3+0.03, 1.45, -0.28, 0.01)
    M.box('nameplate', 'brushed_metal', -0.1, 0.95, 0.395, 0.1, 1.05, 0.41, 0.003)
    M.add('arrestor', 'insulator_grey', cyl(0.05, 0.3, 8, 1.95, 0.45, -0.3, 0.05)) if False else None
    for nm, p in (('HV1', (-0.22, 2.2, 0)), ('HV2', (0, 2.2, 0)), ('HV3', (0.22, 2.2, 0)), ('LV_L', (-0.17, 1.35, 0.54)), ('LV_R', (0.17, 1.35, 0.54))): M.cn('terminal_'+nm, p, (0, 1, 0))
    M.det('bushing_HV', 'HV bushings', (0, 1.7, 0)); M.det('tank', 'transformer can (falls from hangers)', (0, 1.0, 0))
    return M

def UTILITY_03():
    M = Model('UTILITY_03', 'utilities', 'Pad-mount transformer 1.5 x 1.3 x 1.4 m on chamfered concrete pad: hooded roof, double hinged doors, louvres, padlock, conduits')
    M.box('pad', 'concrete_pale', -1.0, 0, -0.9, 1.0, 0.18, 0.9, 0.03)
    M.box('pad_edge', 'concrete_weathered', -1.0, 0.0, -0.9, 1.0, 0.04, 0.9)
    M.box('cabinet', 'paint_green', -0.75, 0.18, -0.6, 0.75, 1.35, 0.6, 0.025)
    M.add('roof', 'paint_green', tbox(-0.82, 1.35, -0.67, 0.82, 1.52, 0.67, 0.86))
    M.box('roof_cap', 'metal_painted_grey', -0.5, 1.52, -0.4, 0.5, 1.55, 0.4, 0.01)
    for s in (-1, 1):
        x0, x1 = (0.01, 0.7) if s > 0 else (-0.7, -0.01)
        M.box('door', 'paint_green', x0, 0.28, 0.6, x1, 1.25, 0.64, 0.01)
        M.box('door_panel', 'metal_painted_grey', x0+0.08, 0.38, 0.64, x1-0.08, 1.15, 0.655, 0.008)
        for y in (0.4, 0.75, 1.1): M.add('hinge', 'brushed_metal', cyl(0.018, 0.1, 6, y-0.05, s*0.72, 0.62))
    M.box('handle', 'brushed_metal', -0.045, 0.7, 0.64, -0.02, 0.9, 0.68, 0.005); M.box('handle', 'brushed_metal', 0.02, 0.7, 0.64, 0.045, 0.9, 0.68, 0.005)
    M.add('padlock', 'safety_yellow', cylb(0.035, 0.07, 8, 0.58, 0, 0.68, 0.01))
    M.add('padlock', 'brushed_metal', box(-0.018, 0.64, 0.66, 0.018, 0.7, 0.7)) if False else None
    for s in (-1, 1):                      # side louvres
        louvre(M, 'vent', 'rubber_dark', -0.5, 0.5, 0.45, 1.15, s*0.6 if s > 0 else -0.635, 9, 0.025, 0.035) if s > 0 else None
    for i in range(9): M.box('vent_side', 'rubber_dark', 0.75, 0.45+i*0.08, -0.4, 0.785, 0.47+i*0.08, 0.4)
    for i in range(9): M.box('vent_side', 'rubber_dark', -0.785, 0.45+i*0.08, -0.4, -0.75, 0.47+i*0.08, 0.4)
    M.box('warning_label', 'safety_yellow', -0.2, 1.2, 0.64, 0.2, 1.3, 0.652, 0.004)
    M.box('danger_label', 'traffic_red', -0.12, 0.3, 0.64, 0.12, 0.38, 0.65, 0.004)
    for x in (-0.4, 0.4): M.add('conduit', 'galvanized_steel', cyl(0.05, 0.5, 8, -0.3, x, -0.4) if False else tube((x, 0.0, -0.4), (x, 0.0, -0.4), 0.05, 6) if False else cyl(0.06, 0.22, 8, 0.18, x, -0.5))
    bolts(M, 'pad_bolts', [(-0.9, -0.8), (0.9, -0.8), (-0.9, 0.8), (0.9, 0.8)], 0.18, 0.03, 0.04)
    M.cn('ground_cable_entry', (0, 0.18, -0.5), (0, -1, 0)); M.cn('door_L', (-0.7, 0.8, 0.64), (0, 0, 1)); M.cn('door_R', (0.7, 0.8, 0.64), (0, 0, 1))
    M.det('door', 'doors (hinged left/right)', (-0.72, 0.8, 0.62))
    return M

def UTILITY_04():
    M = Model('UTILITY_04', 'utilities', 'High-voltage lattice transmission tower 34 m: tapered 4-leg frame, X-bracing on every panel, ring frames, 3 truss crossarms, 6 insulator strings, earth-wire peak')
    ys = [0, 5, 10, 15, 20, 25, 30]; hw = [3.4, 2.9, 2.4, 1.95, 1.55, 1.25, 1.05]
    corners = [(-1, -1), (1, -1), (1, 1), (-1, 1)]
    def P(k, c): return (c[0]*hw[k], ys[k], c[1]*hw[k])
    for k in range(len(ys)-1):
        for c in corners: M.beam('legs', 'galvanized_steel', P(k, c), P(k+1, c), 0.26-0.02*k, 0.26-0.02*k)
        for i in range(4):
            a, b = corners[i], corners[(i+1) % 4]
            M.beam('x_brace', 'galvanized_steel', P(k, a), P(k+1, b), 0.1, 0.1); M.beam('x_brace', 'galvanized_steel', P(k, b), P(k+1, a), 0.1, 0.1)
    for k in range(len(ys)):
        for i in range(4): M.beam('ring', 'galvanized_steel', P(k, corners[i]), P(k, corners[(i+1) % 4]), 0.12, 0.12)
    # top peak
    for c in corners: M.beam('peak', 'galvanized_steel', P(6, c), (0, 34.0, 0), 0.15, 0.15)
    M.tube('peak', 'galvanized_steel', (0, 33.9, 0), (0, 36.0, 0), 0.07, 6, 0.03)
    # crossarms (truss planes at z=+/-0.3)
    arms = [(25, 4.4), (20, 5.4), (15, 6.4)]
    for y, L in arms:
        k = ys.index(y); w = hw[k]
        for s in (-1, 1):
            for z in (-0.3, 0.3):
                M.beam('crossarm', 'galvanized_steel', (s*w, y, z), (s*L, y, z), 0.14, 0.14)
                M.beam('crossarm', 'galvanized_steel', (s*w, y+1.3, z), (s*L, y+0.2, z), 0.11, 0.11)
                M.beam('crossarm', 'galvanized_steel', (s*L, y+0.2, z), (s*L, y, z), 0.11, 0.11)
                n = 4
                for i in range(n):
                    xa = w+(L-w)*i/n; xb = w+(L-w)*(i+1)/n
                    ya = y+1.3-1.1*i/n; yb = y+1.3-1.1*(i+1)/n
                    M.beam('crossarm', 'galvanized_steel', (s*xa, y, z) if i % 2 == 0 else (s*xa, ya, z), (s*xb, yb, z) if i % 2 == 0 else (s*xb, y, z), 0.07, 0.07)
            M.beam('crossarm', 'galvanized_steel', (s*(L-0.1), y+0.1, -0.3), (s*(L-0.1), y+0.1, 0.3), 0.1, 0.1)
            M.beam('crossarm', 'galvanized_steel', (s*(w+(L-w)/2), y, -0.3), (s*(w+(L-w)/2), y, 0.3), 0.08, 0.08)
            # insulator string
            for i in range(7):
                M.add('insulator_string', 'insulator_ceramic', cylb(0.16, 0.055, 10, 0, s*L, 0, 0.015).move(0, y-0.22-i*0.13, 0))
            M.tube('insulator_string', 'galvanized_steel', (s*L, y, 0), (s*L, y-1.15, 0), 0.025, 6)
            M.add('yoke', 'galvanized_steel', box(s*L-0.1, y-1.3, -0.1, s*L+0.1, y-1.15, 0.1, 0.02))
            M.cn(f'conductor_{"R" if s > 0 else "L"}_{y}', (s*L, y-1.3, 0), (0, -1, 0))
    for s in (-1, 1):                       # earth wire peaks
        M.beam('earth_wire_peak', 'galvanized_steel', (s*0.5, 30.0, 0), (s*3.4, 29.5, 0), 0.1, 0.1) if False else None
        M.cn(f'earth_wire_{s}', (0, 36.0, 0), (0, 1, 0))
    for c in corners:                       # footings
        M.box('footing', 'concrete_weathered', c[0]*3.4-0.5, -0.5, c[1]*3.4-0.5, c[0]*3.4+0.5, 0.3, c[1]*3.4+0.5, 0.05)
        M.box('base_plate', 'brushed_metal', c[0]*3.4-0.3, 0.3, c[1]*3.4-0.3, c[0]*3.4+0.3, 0.35, c[1]*3.4+0.3, 0.01)
    M.det('crossarm', 'crossarm trusses + insulator strings (snap at tower nodes)', (0, 20, 0)); M.det('peak', 'top peak', (0, 30, 0))
    return M

def UTILITY_05():
    M = Model('UTILITY_05', 'utilities', 'Steel portal frame for overhead cable runs 8.5 m: 2 I-beam columns, truss cross-member, 6 hanging insulator strings, gusseted base plates')
    for x in (-3.0, 3.0):
        M.add('column', 'galvanized_steel', prof_beam((x, 0.1, 0), (x, 8.0, 0), ibeam_poly(0.32, 0.32, 0.03, 0.022), 1.0, 0.75))
        M.box('base_plate', 'galvanized_steel', x-0.4, 0.0, -0.4, x+0.4, 0.1, 0.4, 0.01)
        bolts(M, 'base_plate', [(x+a, b) for a in (-0.32, 0.32) for b in (-0.32, 0.32)], 0.1, 0.03, 0.08)
        for dz in (-1, 1): M.beam('gusset', 'galvanized_steel', (x, 0.1, dz*0.45), (x, 0.9, dz*0.18), 0.03, 0.03) if False else M.beam('gusset', 'galvanized_steel', (x, 0.15, dz*0.4), (x, 1.0, dz*0.16), 0.04, 0.04)
        M.box('footing', 'concrete_weathered', x-0.6, -0.6, -0.6, x+0.6, 0.0, 0.6, 0.04)
    for y in (7.4, 8.4): M.beam('chord', 'galvanized_steel', (-3.0, y, 0), (3.0, y, 0), 0.14, 0.14)
    n = 12
    for i in range(n):
        a = -3.0+6.0*i/n; b = -3.0+6.0*(i+1)/n
        M.beam('web', 'galvanized_steel', (a, 7.4 if i % 2 == 0 else 8.4, 0), (b, 8.4 if i % 2 == 0 else 7.4, 0), 0.07, 0.07)
    for x in (-3.0, 3.0):
        for dy in (0.6, 1.0): pass
        M.beam('knee_brace', 'galvanized_steel', (x, 6.5, 0), (x*0.75, 7.4, 0), 0.1, 0.1)
    for x in (-2.4, -1.4, -0.4, 0.4, 1.4, 2.4):
        M.box('mount_plate', 'brushed_metal', x-0.12, 7.25, -0.12, x+0.12, 7.4, 0.12, 0.01)
        for i in range(5): M.add('insulator_string', 'insulator_ceramic', cylb(0.13, 0.05, 10, 0, x, 0, 0.012).move(0, 7.1-i*0.115, 0))
        M.tube('insulator_string', 'galvanized_steel', (x, 7.25, 0), (x, 6.45, 0), 0.02, 6)
        M.box('clamp', 'galvanized_steel', x-0.07, 6.35, -0.07, x+0.07, 6.45, 0.07, 0.01)
        M.cn(f'cable_x{x}', (x, 6.35, 0), (0, -1, 0))
    M.add('ground_lug', 'brushed_metal', cyl(0.03, 0.15, 6, 0.1, -2.7, 0.2)) if False else None
    M.det('web', 'cross-member truss + insulators (spans between columns)', (0, 7.9, 0))
    return M

def UTILITY_06():
    M = Model('UTILITY_06', 'utilities', 'Compact substation module 9 x 7 m: 2 oil transformers with radiators/bushings/conservators, switchgear row, 3-phase busbar gantry, control kiosk, kerb + fence rail')
    M.box('slab', 'concrete_weathered', -4.5, 0, -3.5, 4.5, 0.2, 3.5, 0.03)
    M.box('gravel', 'dusty_stone', -4.3, 0.2, -3.3, 4.3, 0.23, 3.3)
    for tx in (-2.6, 0.2):
        M.box('plinth', 'concrete_pale', tx-1.2, 0.23, -0.4, tx+1.2, 0.5, 2.0, 0.03)
        M.box('tank', 'paint_green', tx-1.0, 0.5, -0.1, tx+1.0, 2.1, 1.7, 0.08)
        M.box('tank_lid', 'metal_painted_grey', tx-1.05, 2.1, -0.15, tx+1.05, 2.2, 1.75, 0.03)
        for i in range(6): M.box('radiator', 'metal_painted_grey', tx+1.0+0.0, 0.7, 0.05+i*0.27, tx+1.4, 1.95, 0.12+i*0.27, 0.01)
        M.box('radiator_header', 'metal_painted_grey', tx+1.0, 1.9, 0.0, tx+1.45, 2.0, 1.6, 0.01); M.box('radiator_header', 'metal_painted_grey', tx+1.0, 0.65, 0.0, tx+1.45, 0.75, 1.6, 0.01)
        M.add('conservator', 'paint_green', cyl(0.28, 1.5, 12, 0, 0, 0).rot('x', 90).rot('z', 0).move(tx-0.2, 2.75, 0.1) if False else tube((tx-0.7, 2.75, 0.85), (tx+0.7, 2.75, 0.85), 0.28, 12))
        for s in (-0.4, 0.0, 0.4): M.add('support', 'metal_painted_grey', beam((tx+s*1.5, 2.2, 0.85), (tx+s*1.5, 2.55, 0.85), 0.06, 0.06))
        for i, bx in enumerate((-0.6, 0.0, 0.6)):
            insulator(M, 'bushing_HV', tx+bx, 2.2, 0.2, 0.9, 0.1, 'insulator_ceramic')
        for i, bx in enumerate((-0.45, 0.0, 0.45)): insulator(M, 'bushing_LV', tx+bx, 2.2, 1.4, 0.45, 0.07, 'insulator_grey')
    for i in range(5): M.box('switchgear', 'paint_blue', -3.9+i*0.95, 0.23, -3.0, -3.1+i*0.95, 2.3, -2.2, 0.03)
    for i in range(5):
        M.box('sw_door', 'metal_painted_grey', -3.82+i*0.95, 0.5, -2.2, -3.18+i*0.95, 2.0, -2.17, 0.015)
        M.box('sw_handle', 'brushed_metal', -3.4+i*0.95, 1.1, -2.17, -3.35+i*0.95, 1.4, -2.13, 0.004)
        M.box('sw_light', 'signal_green' if i % 2 == 0 else 'signal_amber', -3.7+i*0.95, 1.8, -2.17, -3.55+i*0.95, 1.9, -2.14)
    # busbar gantry
    for x in (1.9, 3.1, 4.1):
        M.box('gantry', 'galvanized_steel', x-0.07, 0.23, 2.2, x+0.07, 4.5, 2.34, 0.01)
        M.box('gantry', 'galvanized_steel', x-0.07, 0.23, 3.2, x+0.07, 4.5, 3.34, 0.01) if False else None
    for x in (1.9, 4.1):
        M.beam('gantry_a', 'galvanized_steel', (x, 0.23, 2.1), (x, 4.5, 2.1), 0.14, 0.14); M.beam('gantry_a', 'galvanized_steel', (x, 0.23, 3.1), (x, 4.5, 3.1), 0.14, 0.14)
        M.beam('gantry_a', 'galvanized_steel', (x, 0.3, 2.1), (x, 3.0, 3.1), 0.06, 0.06); M.beam('gantry_a', 'galvanized_steel', (x, 0.3, 3.1), (x, 3.0, 2.1), 0.06, 0.06)
    M.beam('gantry_beam', 'galvanized_steel', (1.9, 4.4, 2.1), (4.1, 4.4, 2.1), 0.14, 0.14); M.beam('gantry_beam', 'galvanized_steel', (1.9, 4.4, 3.1), (4.1, 4.4, 3.1), 0.14, 0.14)
    for z in (2.1, 2.6, 3.1): M.beam('gantry_beam', 'galvanized_steel', (1.9, 4.4, z), (4.1, 4.4, z), 0.1, 0.1) if False else None
    M.beam('gantry_beam', 'galvanized_steel', (1.9, 4.4, 2.1), (1.9, 4.4, 3.1), 0.12, 0.12); M.beam('gantry_beam', 'galvanized_steel', (4.1, 4.4, 2.1), (4.1, 4.4, 3.1), 0.12, 0.12)
    for k, z in enumerate((2.1, 2.6, 3.1)):
        M.tube('busbar', 'brushed_metal', (1.9, 3.7, z), (4.1, 3.7, z), 0.045, 8)
        for x in (1.9, 3.0, 4.1): insulator(M, 'busbar_support', x, 3.1 if False else 3.4, z, 0.3, 0.07, 'insulator_ceramic') if k == 0 else (insulator(M, 'busbar_support', x, 3.4, z, 0.3, 0.07, 'insulator_ceramic'))
        M.cn(f'busbar_phase_{k}', (4.1, 3.7, z), (1, 0, 0))
    M.box('kiosk', 'plaster_cream', 3.1, 0.23, -3.0, 4.2, 2.5, -1.4, 0.03)
    M.add('kiosk_roof', 'paint_blue', tbox(3.0, 2.5, -3.1, 4.3, 2.75, -1.3, 0.8))
    M.box('kiosk_door', 'metal_painted_grey', 3.3, 0.23, -1.4, 3.8, 2.0, -1.37, 0.01)
    M.box('kiosk_window', 'glass_tinted', 3.95, 1.3, -1.4, 4.15, 1.9, -1.37) if False else None
    for x in (-4.4, 4.4):
        for z in (-3.4, 3.4): M.box('fence_post', 'galvanized_steel', x-0.04, 0.2, z-0.04, x+0.04, 1.4, z+0.04, 0.005)
    for z in (-3.4, 3.4): M.beam('fence_rail', 'galvanized_steel', (-4.4, 1.3, z), (4.4, 1.3, z), 0.04, 0.04)
    for x in (-4.4, 4.4): M.beam('fence_rail', 'galvanized_steel', (x, 1.3, -3.4), (x, 1.3, 3.4), 0.04, 0.04)
    M.det('tank', 'transformer tanks', (0, 1.3, 0.8)); M.det('switchgear', 'switchgear cabinets', (-2, 1.2, -2.6))
    return M

def UTILITY_07():
    M = Model('UTILITY_07', 'utilities', 'Rooftop packaged AC unit 2.3 x 1.1 x 1.2 m: sheet-metal housing, fan shroud with 5-blade fan, louvred coil grilles, access panels, refrigerant lines, feet + curb rail')
    M.box('curb_rail', 'galvanized_steel', -1.2, 0, -0.65, 1.2, 0.18, 0.65, 0.02)
    for x in (-1.0, 0.0, 1.0): M.box('feet', 'rubber_dark', x-0.12, 0.0, -0.7, x+0.12, 0.06, 0.7, 0.01)
    M.box('housing', 'white_paint', -1.15, 0.18, -0.55, 1.15, 1.18, 0.55, 0.05)
    M.box('top_panel', 'metal_painted_grey', -1.12, 1.18, -0.52, 1.12, 1.2, 0.52, 0.01)
    M.add('fan_shroud', 'metal_painted_grey', merge([band(0.3, 0.45, 1.2, 1.3, k*45, (k+1)*45, 2, 0.55, 0, rt0=0.33, rt1=0.43) for k in range(8)]) if False else merge([band(0.3, 0.45, 1.2, 1.3, k*45, (k+1)*45, 2, rt0=0.33, rt1=0.43).move(0.55, 0, 0) for k in range(8)]))
    for i in range(8): M.box('fan_guard', 'galvanized_steel', 0.55-0.012+0.0, 1.25, -0.44, 0.55+0.012, 1.285, 0.44, 0.003).rot if False else None
    M.add('fan_guard', 'galvanized_steel', merge([tube((0.55, 1.29, 0), (0.55+0.43*math.cos(math.radians(a)), 1.29, 0.43*math.sin(math.radians(a))), 0.008, 4) for a in range(0, 180, 30)]))
    for r in (0.15, 0.3): M.add('fan_guard', 'galvanized_steel', merge([band(r, r+0.015, 1.285, 1.305, k*60, (k+1)*60, 2).move(0.55, 0, 0) for k in range(6)]))
    M.add('fan_hub', 'rubber_dark', cylb(0.07, 0.1, 8, 1.15, 0.55, 0, 0.01))
    for i in range(5):
        M.add('fan_blades', 'rubber_dark', box(0.0, 1.17, -0.04, 0.34, 1.19, 0.04, 0.005).rot('y', i*72).move(0.55, 0, 0))
    M.box('fan_hole', 'rubber_dark', 0.2, 1.19, -0.35, 0.9, 1.2, 0.35) if False else None
    for s in (-1, 1): louvre(M, 'coil_grille', 'galvanized_steel', -1.0, 0.3, 0.3, 1.05, 0.55 if s > 0 else -0.585, 14, 0.018, 0.035)
    for i in range(10): M.box('end_grille', 'galvanized_steel', 1.15, 0.3+i*0.08, -0.4, 1.19, 0.32+i*0.08, 0.4)
    M.box('access_panel', 'metal_painted_grey', -1.1, 0.3, 0.55, -0.4, 0.95, 0.575, 0.01) if False else M.box('access_panel', 'metal_painted_grey', -0.2, 0.3, 0.55, 0.0, 0.95, 0.575, 0.01)
    M.box('panel_handle', 'brushed_metal', -0.05, 0.6, 0.575, -0.03, 0.75, 0.6, 0.004)
    M.add('line_set', 'cable_black', tube((-1.15, 0.35, 0.2), (-1.5, 0.35, 0.2), 0.04, 8)); M.add('line_set', 'brushed_metal', tube((-1.5, 0.35, 0.2), (-1.5, 0.35, 0.5), 0.04, 8)) if False else None
    M.add('line_set', 'brushed_metal', tube((-1.5, 0.35, 0.2), (-1.5, 0.05, 0.2), 0.03, 8)); M.add('line_set', 'rubber_dark', tube((-1.15, 0.5, 0.2), (-1.38, 0.5, 0.2), 0.05, 8)) if False else None
    M.add('disconnect', 'safety_yellow', box(-1.35, 0.5, -0.1, -1.2, 0.8, 0.1, 0.01)) if False else M.box('disconnect', 'safety_yellow', -1.3, 0.5, -0.35, -1.15, 0.8, -0.1, 0.01)
    M.cn('roof_mount', (0, 0, 0), (0, -1, 0)); M.det('fan_blades', 'fan blades', (0.55, 1.18, 0)); M.det('top_panel', 'top panel', (0, 1.18, 0))
    return M

def UTILITY_08():
    M = Model('UTILITY_08', 'utilities', 'Rooftop water tank 4.4 m high: 16-sided tank with 4 hoop bands, conical roof, hatch + ladder, 4-leg braced steel stand, inlet/outlet piping, gauge')
    for x in (-1.0, 1.0):
        for z in (-1.0, 1.0):
            M.beam('legs', 'galvanized_steel', (x*1.15, 0, z*1.15), (x*0.95, 2.0, z*0.95), 0.14, 0.14)
            M.box('foot', 'galvanized_steel', x*1.15-0.2, 0, z*1.15-0.2, x*1.15+0.2, 0.05, z*1.15+0.2, 0.01)
    for y, k in ((0.7, 1.08), (1.5, 0.99)):
        for i in range(4):
            a = [(-k, -k), (k, -k), (k, k), (-k, k)]; p, q = a[i], a[(i+1) % 4]
            M.beam('stand_ring', 'galvanized_steel', (p[0], y, p[1]), (q[0], y, q[1]), 0.08, 0.08)
    for x, z, x2, z2 in ((-1.1, -1.1, 1.0, -1.0), (1.1, -1.1, -1.0, -1.0), (-1.1, 1.1, 1.0, 1.0), (1.1, 1.1, -1.0, 1.0)):
        M.beam('stand_brace', 'galvanized_steel', (x, 0.1, z), (x2, 1.9, z2), 0.05, 0.05) if False else None
    for sg in (-1, 1):
        M.beam('stand_brace', 'galvanized_steel', (-1.1, 0.7, sg*1.08), (1.0, 1.5, sg*0.99), 0.05, 0.05); M.beam('stand_brace', 'galvanized_steel', (1.1, 0.7, sg*1.08), (-1.0, 1.5, sg*0.99), 0.05, 0.05)
        M.beam('stand_brace', 'galvanized_steel', (sg*1.08, 0.7, -1.1), (sg*0.99, 1.5, 1.0), 0.05, 0.05); M.beam('stand_brace', 'galvanized_steel', (sg*1.08, 0.7, 1.1), (sg*0.99, 1.5, -1.0), 0.05, 0.05)
    M.add('deck', 'galvanized_steel', cylb(1.3, 0.12, 16, 2.0, b=0.02))
    M.add('tank', 'coastal_weathered', lathe([(1.25, 2.12), (1.3, 2.18), (1.3, 3.9), (1.25, 3.96)], 16))
    for y in (2.5, 2.95, 3.4, 3.8): M.add('hoops', 'galvanized_steel', lathe([(1.3, y), (1.34, y+0.01), (1.34, y+0.07), (1.3, y+0.08)], 16))
    M.add('roof', 'rust_metal', lathe([(1.34, 3.96), (1.1, 4.2), (0.5, 4.45), (0.0, 4.52)], 16))
    M.add('hatch', 'galvanized_steel', cylb(0.28, 0.12, 10, 4.25, 0.3, 0.2, 0.02))
    M.add('vent', 'galvanized_steel', cyl(0.07, 0.3, 8, 4.5, -0.4, -0.1)); M.add('vent', 'galvanized_steel', lathe([(0.12, 4.78), (0.0, 4.9)], 8, -0.4, -0.1)) if False else None
    M.add('ladder_rail', 'galvanized_steel', merge([beam((s*0.19, 0.05, 1.45), (s*0.19, 4.2, 1.35), 0.04, 0.04) for s in (-1, 1)]))
    for i in range(14): M.add('ladder_rung', 'galvanized_steel', tube((-0.19, 0.2+i*0.29, 1.44-i*0.0225), (0.19, 0.2+i*0.29, 1.44-i*0.0225), 0.017, 5))
    M.add('pipe', 'rust_metal' if False else 'paint_blue', tube((0.0, 2.0, 0.0), (0.0, 0.1, 0.0), 0.07, 8)); M.add('pipe', 'paint_blue', tube((0.0, 0.1, 0.0), (1.4, 0.1, 0.0), 0.07, 8))
    M.add('valve', 'traffic_red', cylb(0.09, 0.14, 8, 0.2, 0.7, 0.0, 0.015)) if False else M.add('valve', 'traffic_red', cylb(0.09, 0.14, 8, 0.03, 0.7, 0.0, 0.015))
    M.add('inlet_pipe', 'paint_blue', tube((1.3, 3.0, 0.2), (1.8, 3.0, 0.2), 0.05, 8)); M.add('inlet_pipe', 'paint_blue', tube((1.8, 3.0, 0.2), (1.8, 0.1, 0.2), 0.05, 8))
    M.add('gauge', 'glass_tinted', cyl(0.07, 0.04, 10, 0, 0, 0).rot('x', 90).move(-1.0, 3.2, 0.8).rot('y', 0) if False else tube((-0.9, 3.2, 0.82), (-0.9, 3.2, 0.9), 0.07, 10))
    M.cn('level_sensor', (-0.9, 3.2, 0.9), (0, 0, 1)); M.cn('roof_mount', (0, 0, 0), (0, -1, 0)); M.det('roof', 'tank roof + vent + hatch', (0, 3.96, 0)); M.det('tank', 'tank body', (0, 3.0, 0))
    return M

def UTILITY_09():
    M = Model('UTILITY_09', 'utilities', 'Satellite dish 1.6 m: thick parabolic reflector, rim, 3 feed struts, LNB + feed horn, elevation arm, azimuth plate, mast and wall bracket')
    prof = []
    for i in range(0, 11):
        r = 0.01+0.8*i/10; prof.append((r, 0.45*(r/0.8)**2))
    inner = [(r-0.015 if r > 0.05 else 0.01, y+0.02) for r, y in prof[::-1]]
    dish = lathe(prof+[(0.805, 0.47), (0.795, 0.475)] + inner, 20)
    dish.rot('x', 62).move(0, 1.9, 0.0)
    M.add('reflector', 'white_paint', dish)
    ax = (0, math.cos(math.radians(62)), -math.sin(math.radians(62)))   # unused helper
    def D(r, h): # point on dish local (x=r, axis)
        return (r, h)
    # focus point along dish axis (local +y rotated by 62 deg about x)
    fy, fz = math.cos(math.radians(62)), math.sin(math.radians(62))
    def toW(x, y, z): return (x, 1.9 + y*fy - z*fz*0 - z*math.sin(math.radians(62)) + 0*z, y*fz + z*fy*0 + z*math.cos(math.radians(62))*0)
    def w(lx, ly, lz=0.0):
        c = math.cos(math.radians(62)); s = math.sin(math.radians(62)); return (lx, 1.9+ly*c - lz*s, ly*s + lz*c)
    foc = (0, 0.8)
    for a in (90, 210, 330):
        rx = 0.8*math.cos(math.radians(a)); rz = 0.8*math.sin(math.radians(a))
        M.add('feed_strut', 'galvanized_steel', tube(w(rx, 0.45, rz), w(0, 0.75, 0), 0.015, 5))
    M.add('lnb', 'paint_navy', tube(w(0, 0.7, 0), w(0, 0.86, 0), 0.04, 8))
    M.add('feed_horn', 'white_paint', tube(w(0, 0.62, 0), w(0, 0.7, 0), 0.075, 10, 0.04))
    M.add('lnb_cable', 'cable_black', tube(w(0, 0.86, 0), w(0, 0.92, 0), 0.012, 5))
    # back hub + elevation arm
    M.add('hub', 'galvanized_steel', cylb(0.12, 0.1, 10, 0, 0, 0, 0.015).rot('x', 62).move(*w(0, -0.08, 0)))
    M.beam('elevation_arm', 'galvanized_steel', (0, 1.52, -0.12), (0, 1.0, 0.45), 0.07, 0.05)
    M.beam('elevation_arm', 'galvanized_steel', (0, 1.75, -0.25), (0, 1.1, 0.45), 0.05, 0.05)
    M.add('azimuth_plate', 'galvanized_steel', cylb(0.22, 0.06, 12, 1.0, 0, 0.45, 0.012))
    for a in (0, 120, 240): M.add('azimuth_slots', 'rubber_dark', cyl(0.025, 0.065, 5, 1.0, 0.15*math.cos(math.radians(a)), 0.45+0.15*math.sin(math.radians(a))))
    M.add('mast', 'metal_painted_grey', cyl(0.05, 1.0, 10, 0.0, 0, 0.45))
    M.box('wall_plate', 'galvanized_steel', -0.18, 0.0, 0.3, 0.18, 0.04, 0.6, 0.01)
    bolts(M, 'wall_plate', [(-0.12, 0.35), (0.12, 0.35), (-0.12, 0.55), (0.12, 0.55)], 0.04, 0.02, 0.03)
    M.add('ubolt', 'brushed_metal', tube((-0.07, 0.4, 0.45), (0.07, 0.4, 0.45), 0.008, 4)) if False else None
    M.cn('lnb_cable_out', w(0, 0.92, 0), (0, 1, 0)); M.cn('mount', (0, 0, 0.45), (0, -1, 0)); M.det('reflector', 'dish', (0, 1.9, 0)); M.det('feed_strut', 'feed assembly', w(0, 0.75, 0))
    return M

def UTILITY_10():
    M = Model('UTILITY_10', 'utilities', 'Cellular antenna mast 12 m: guyless monopole, triangular platform with rail, 3 sector panels with clamps/tilt bars, 3 RRUs, microwave dish, lightning rod, cable ladder')
    base_plate(M, 'base', 1.0, 0.08, bolt=False)
    bolts(M, 'base', [(0.4*math.cos(a*math.pi/4), 0.4*math.sin(a*math.pi/4)) for a in range(8)], 0.08, 0.04, 0.1)
    M.add('mast', 'galvanized_steel', cyl(0.22, 11.0, 12, 0.08, r1=0.1))
    for y in (3.0, 6.0, 9.0): M.add('flange', 'galvanized_steel', cylb(0.25-0.012*y, 0.1, 12, y, b=0.015))
    # platform
    tri = [(2.0*math.cos(math.radians(a)), 2.0*math.sin(math.radians(a))) for a in (90, 210, 330)]
    M.add('platform', 'metal_painted_grey', ext('x', tri, 0, 0) if False else ext(tri, 10.0, 10.08, [(x*0.98, z*0.98) for x, z in tri]))
    for i in range(3):
        a, b = tri[i], tri[(i+1) % 3]
        M.beam('platform_rail', 'safety_yellow', (a[0], 10.9, a[1]), (b[0], 10.9, b[1]), 0.05, 0.05); M.beam('platform_rail', 'safety_yellow', (a[0], 10.45, a[1]), (b[0], 10.45, b[1]), 0.04, 0.04)
        M.beam('platform_post', 'safety_yellow', (a[0], 10.08, a[1]), (a[0], 10.9, a[1]), 0.05, 0.05)
        M.beam('platform_brace', 'galvanized_steel', (0, 9.4, 0), (a[0]*0.9, 10.0, a[1]*0.9), 0.06, 0.06)
    for k, ang in enumerate((90, 210, 330)):
        T = Model('t', 'x')
        T.box('antenna', 'white_paint', -0.15, 0.0, 0.0, 0.15, 1.7, 0.12, 0.02)
        T.box('antenna_cap', 'insulator_grey', -0.13, 1.7, 0.01, 0.13, 1.76, 0.11, 0.015)
        T.box('antenna_face', 'sign_white', -0.12, 0.05, 0.12, 0.12, 1.65, 0.125)
        for y in (0.2, 1.4): T.box('clamp', 'galvanized_steel', -0.1, y, -0.12, 0.1, y+0.07, 0.0, 0.01)
        T.beam('arm', 'galvanized_steel', (0, 0.235, -0.12), (0, 0.235, -0.6), 0.05, 0.05); T.beam('arm', 'galvanized_steel', (0, 1.435, -0.12), (0, 1.435, -0.6), 0.05, 0.05)
        T.beam('tilt_bar', 'galvanized_steel', (0, 0.1, -0.12), (0, 0.5, -0.6), 0.02, 0.02)
        T.box('rru', 'metal_painted_grey', -0.2, 0.2, -0.95, 0.2, 0.75, -0.62, 0.025)
        T.add('rru_fins', 'galvanized_steel', merge([box(-0.18, 0.25+i*0.07, -1.0, 0.18, 0.27+i*0.07, -0.95) for i in range(7)]))
        # place at radius 1.4 pointing outward (+z local -> angle)
        T.box('rru_cable', 'cable_black', -0.015, 0.1, -0.9, 0.015, 0.2, -0.88) if False else None
        for (g, m), p in T.groups.items():
            q = p.copy().move(0, 10.2, 1.6).rot('y', ang-90+0) if False else p.copy().move(0, 10.2, 1.75).rot('y', -(ang-90))
            M.add(g, m, q)
        M.cn(f'sector_{k}', (1.75*math.sin(math.radians(-(ang-90))), 11.0, 1.75*math.cos(math.radians(-(ang-90)))), (math.sin(math.radians(-(ang-90))), 0, math.cos(math.radians(-(ang-90)))))
    # microwave dish
    dish = lathe([(0.01, 0), (0.15, 0.03), (0.3, 0.1), (0.4, 0.2), (0.37, 0.2), (0.28, 0.12), (0.14, 0.05), (0.01, 0.025)], 12).rot('x', 90).move(0.0, 8.6, 0.0)
    M.add('mw_dish', 'white_paint', dish.copy().move(0, 0, 0.5) if False else lathe([(0.01, 0), (0.15, 0.03), (0.3, 0.1), (0.4, 0.2), (0.37, 0.2), (0.28, 0.12), (0.14, 0.05), (0.01, 0.025)], 12).rot('x', 90).move(0.0, 8.6, 0.32))
    M.tube('mw_mount', 'galvanized_steel', (0.0, 8.6, 0.2), (0.0, 8.6, 0.3), 0.07, 8)
    M.add('lightning_rod', 'brushed_metal', tube((0, 11.0, 0), (0, 12.4, 0), 0.025, 6, 0.01))
    M.add('cable_ladder', 'rubber_dark', beam((0.0, 0.2, -0.28), (0.0, 10.0, -0.2), 0.12, 0.04))
    M.cn('mast_base', (0, 0, 0), (0, -1, 0)); M.det('sector', 'antenna panels', (0, 10.2, 0))
    return M

def UTILITY_11():
    M = Model('UTILITY_11', 'utilities', 'Portable generator 0.95 x 0.55 x 0.75 m: tubular roll cage, engine housing, fuel tank + cap, muffler/exhaust, control panel with outlets, wheels, handle, recoil starter')
    M.box('skid', 'metal_painted_grey', -0.45, 0.12, -0.28, 0.45, 0.18, 0.28, 0.01)
    for x in (-0.38, 0.38): M.box('feet', 'rubber_dark', x-0.06, 0.08, -0.3, x+0.06, 0.12, 0.3, 0.01)
    M.box('engine', 'safety_orange', -0.4, 0.18, -0.22, 0.2, 0.62, 0.22, 0.04)
    M.box('alternator', 'metal_painted_grey', 0.2, 0.18, -0.22, 0.42, 0.55, 0.22, 0.04)
    M.add('fuel_tank', 'safety_orange', tube((-0.38, 0.69, 0), (0.1, 0.69, 0), 0.1, 10))
    M.add('fuel_cap', 'rubber_dark', cylb(0.04, 0.04, 8, 0.78, -0.2, 0, 0.008))
    M.box('air_filter', 'rubber_dark', -0.35, 0.4, 0.22, -0.18, 0.55, 0.3, 0.015)
    M.add('recoil', 'traffic_red', cylb(0.09, 0.07, 10, 0, 0, 0, 0.01).rot('x', 90).move(-0.4, 0.4, -0.22-0.0))
    M.box('recoil_handle', 'rubber_dark', -0.46, 0.38, -0.32, -0.42, 0.44, -0.24) if False else None
    M.add('muffler', 'rust_metal', tube((0.22, 0.66, -0.15), (0.38, 0.66, -0.15), 0.06, 10)); M.add('exhaust', 'rust_metal', tube((0.38, 0.66, -0.15), (0.38, 0.66, -0.34), 0.03, 8))
    M.box('panel', 'paint_navy', 0.2, 0.2, 0.22, 0.45, 0.52, 0.3, 0.015)
    for i, x in enumerate((0.25, 0.33, 0.41)): M.add('outlet', 'rubber_dark', cyl(0.025, 0.012, 8, 0.4, 0, 0).rot('x', 90).move(x, 0.4, 0.3))
    M.box('switch', 'safety_yellow', 0.27, 0.28, 0.3, 0.31, 0.34, 0.32); M.add('gauge', 'glass_tinted', cyl(0.03, 0.012, 8, 0, 0, 0).rot('x', 90).move(0.39, 0.28, 0.3))
    for z in (-0.3, 0.3):
        M.add('cage', 'galvanized_steel', merge([tube((-0.45, 0.12, z), (-0.45, 0.75, z), 0.02, 6), tube((0.45, 0.12, z), (0.45, 0.75, z), 0.02, 6), tube((-0.45, 0.75, z), (0.45, 0.75, z), 0.02, 6), tube((-0.45, 0.12, z), (0.45, 0.12, z), 0.02, 6)]))
    for x in (-0.45, 0.45): M.add('cage', 'galvanized_steel', tube((x, 0.75, -0.3), (x, 0.75, 0.3), 0.02, 6)); M.add('cage', 'galvanized_steel', tube((x, 0.12, -0.3), (x, 0.12, 0.3), 0.02, 6))
    M.add('cage', 'galvanized_steel', tube((0.0, 0.75, -0.3), (0.0, 0.75, 0.3), 0.02, 6))
    for z in (-0.3, 0.3): M.add('wheel', 'rubber_dark', cylb(0.14, 0.07, 12, 0, 0, 0, 0.015).rot('x', 90).move(0.5, 0.14, z+(0.03 if z > 0 else -0.1)))
    for z in (-0.3, 0.3): M.add('hub', 'brushed_metal', cyl(0.05, 0.075, 8, 0, 0, 0).rot('x', 90).move(0.5, 0.14, z+(0.03 if z > 0 else -0.1)))
    M.add('handle', 'metal_painted_grey', merge([tube((-0.45, 0.45, -0.3), (-0.75, 0.2, -0.3), 0.02, 6), tube((-0.45, 0.45, 0.3), (-0.75, 0.2, 0.3), 0.02, 6), tube((-0.75, 0.2, -0.3), (-0.75, 0.2, 0.3), 0.02, 6)]))
    M.add('handle_grip', 'rubber_dark', tube((-0.75, 0.2, -0.2), (-0.75, 0.2, 0.2), 0.03, 8))
    M.cn('power_out', (0.33, 0.4, 0.3), (0, 0, 1)); M.cn('exhaust_out', (0.38, 0.66, -0.34), (0, 0, -1)); M.det('wheel', 'wheels', (0.5, 0.14, 0))
    return M

def UTILITY_12():
    M = Model('UTILITY_12', 'utilities', 'Street electrical cabinet 0.8 x 0.45 x 1.5 m: concrete pedestal, sloped-roof cabinet, double doors with hinges/handle/lock, top louvres, meter window')
    M.box('pedestal', 'concrete_pale', -0.5, 0, -0.35, 0.5, 0.25, 0.35, 0.025)
    M.box('cabinet', 'paint_green', -0.4, 0.25, -0.225, 0.4, 1.5, 0.225, 0.02)
    M.add('roof', 'paint_green', tbox(-0.45, 1.5, -0.27, 0.45, 1.62, 0.27, 0.88))
    for s in (-1, 1):
        x0, x1 = (0.01, 0.38) if s > 0 else (-0.38, -0.01)
        M.box('door', 'paint_green', x0, 0.35, 0.225, x1, 1.4, 0.25, 0.008)
        M.box('door_inset', 'metal_painted_grey', x0+0.04, 0.45, 0.25, x1-0.04, 1.2, 0.262, 0.005)
        for y in (0.5, 0.95, 1.3): M.add('hinge', 'brushed_metal', cyl(0.015, 0.09, 6, y-0.04, s*0.385, 0.24))
    M.box('handle', 'brushed_metal', 0.02, 0.8, 0.25, 0.045, 1.0, 0.285, 0.004); M.box('lock', 'safety_yellow', -0.045, 0.85, 0.25, -0.015, 0.93, 0.28, 0.005)
    louvre(M, 'vent', 'rubber_dark', -0.3, 0.3, 1.3, 1.38, 0.25, 4, 0.02, 0.012) if False else None
    for i in range(5): M.box('vent', 'rubber_dark', -0.3, 1.26+i*0.025, 0.25, 0.3, 1.275+i*0.025, 0.265) if False else None
    M.box('meter_window', 'glass_tinted', -0.3, 1.1, 0.262, -0.1, 1.2, 0.27) if False else M.box('meter_window', 'glass_tinted', 0.08, 1.05, 0.262, 0.32, 1.17, 0.27)
    for i in range(7): M.box('side_louvre', 'rubber_dark', 0.4, 0.6+i*0.1, -0.12, 0.425, 0.63+i*0.1, 0.12); M.box('side_louvre', 'rubber_dark', -0.425, 0.6+i*0.1, -0.12, -0.4, 0.63+i*0.1, 0.12)
    M.add('conduit', 'galvanized_steel', tube((0.3, 0.0, -0.1), (0.3, 0.25, -0.1), 0.04, 8)); M.add('conduit', 'galvanized_steel', tube((-0.3, 0.0, -0.1), (-0.3, 0.25, -0.1), 0.04, 8))
    M.box('warning', 'safety_yellow', -0.15, 1.34, 0.25, 0.15, 1.4, 0.256, 0.003)
    M.cn('cable_in', (0, 0, 0), (0, -1, 0)); M.det('door', 'doors', (-0.38, 0.9, 0.24))
    return M

UTILITIES = [UTILITY_01, UTILITY_02, UTILITY_03, UTILITY_04, UTILITY_05, UTILITY_06, UTILITY_07, UTILITY_08, UTILITY_09, UTILITY_10, UTILITY_11, UTILITY_12]
