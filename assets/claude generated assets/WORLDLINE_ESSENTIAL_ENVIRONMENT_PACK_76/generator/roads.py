from lib import *

LW = 3.4; CH = 0.15; CW = 0.25; SL = 0.4; H = 3.4; RF = 1.5   # lane width, curb height/width, slab depth, junction half-width, fillet radius
ANG = {'N': 0, 'E': 90, 'S': 180, 'W': 270}
NEXT = {'N': 'E', 'E': 'S', 'S': 'W', 'W': 'N'}

def rprof(x0, x1, y0, y1): return [(x0, y0), (x1, y0), (x1, y1), (x0, y1)]
def curb_prof(x, side, ch=CH):
    p = [(x, 0), (x+CW, 0), (x+CW, ch), (x+0.07, ch), (x, ch-0.07)]
    return p if side > 0 else [(-a, b) for a, b in p]

def sweep2(profs, pts):
    rings = []
    for i, p in enumerate(pts):
        a = pts[max(i-1, 0)]; b = pts[min(i+1, len(pts)-1)]
        t = norm(sub(b, a)); L = norm((t[2], 0, -t[0]))
        rings.append([(p[0]+L[0]*x, p[1]+y, p[2]+L[2]*x) for x, y in profs[i]])
    return loft(rings)

def markline(M, P, x, w, a, b, mat='marking_white', h=0.02):
    M.sweep('markings', mat, rprof(x-w/2, x+w/2, 0, h), P.pts(a, b, 1.5))

def arrow(M, P, xc, s, dirsign, sc=1.0):
    """Painted directional arrow (shaft + tapered head) following the path."""
    sh0, sh1 = (s-1.0*sc, s+0.3*sc) if dirsign > 0 else (s-0.3*sc, s+1.0*sc)
    M.sweep('markings', 'marking_white', rprof(xc-0.15*sc, xc+0.15*sc, 0, 0.02), P.pts(sh0, sh1, 1.5))
    hb, ht = (s+0.3*sc, s+1.1*sc) if dirsign > 0 else (s-1.1*sc, s-0.3*sc)
    w0, w1 = (0.48*sc, 0.03) if dirsign > 0 else (0.03, 0.48*sc)
    pts = P.pts(hb, ht, 10); pts = [pts[0], pts[-1]]
    M.add('markings', 'marking_white', sweep2([rprof(xc-w0, xc+w0, 0, 0.02), rprof(xc-w1, xc+w1, 0, 0.02)], pts))

def build_road(M, P, n=1, med=0.0, mtype='none', lw=LW, curbs=True, arrows=True):
    L = P.L; hw = med/2 + n*lw
    for side in (-1, 1):
        xa, xb = sorted((side*med/2, side*hw))
        for k in range(3):
            mat = 'asphalt_warm' if (k + (side > 0)) % 2 == 0 else 'asphalt_cool'
            M.sweep('surface', mat, rprof(xa, xb, -SL, 0), P.pts(L*k/3, L*(k+1)/3, 1.5))
        # shoulder wear band + edge line
        M.sweep('markings', 'asphalt_cool', rprof(*sorted((side*(hw-0.45), side*hw)), 0, 0.012), P.pts(0, L, 1.5))
        markline(M, P, side*(hw-0.6), 0.12, 0, L)
    if curbs:
        for side in (-1, 1): M.sweep('curb', 'concrete_pale', curb_prof(hw, side), P.pts(0, L, 1.5))
    # medians
    if med > 0:
        m = med/2
        if mtype == 'planted':
            M.sweep('median_base', 'concrete_weathered', rprof(-m, m, -SL, 0), P.pts(0, L, 1.5))
            for side in (-1, 1):
                a, b = sorted((side*m, side*(m-0.22)))
                prof = [(a, 0), (b, 0), (b, 0.25), (b + (0.04 if side < 0 else -0.04), 0.25), (a, 0.2)]
                if side < 0: prof = [(a, 0), (b, 0), (b-0.0, 0.2), (b, 0.25), (a+0.04, 0.25), (a, 0.2)]
                M.sweep('median_curb', 'concrete_pale', [(a, 0), (b, 0), (b, 0.25), (a+0.04, 0.25), (a, 0.21)] if side < 0 else [(a, 0), (b, 0), (b, 0.21), (b-0.04, 0.25), (a, 0.25)], P.pts(0, L, 1.5))
            M.sweep('median_soil', 'soil', [(-m+0.22, 0), (m-0.22, 0), (m-0.22, 0.17), (m-0.5, 0.23), (-m+0.5, 0.23), (-m+0.22, 0.17)], P.pts(0, L, 1.5))
            for f in (1/6, 3/6, 5/6):
                x, y, z = P.f(L*f)
                M.add('tree_pit', 'concrete_weathered', band(0.36, 0.52, 0.0, 0.3, 0, 360, 12, x, z, rt0=0.40, rt1=0.50).move(0, y, 0))
        elif mtype == 'stone':
            M.sweep('median_base', 'concrete_weathered', rprof(-m, m, -SL, 0), P.pts(0, L, 1.5))
            M.sweep('median_block', 'concrete_pale', [(-m, 0), (m, 0), (m, 0.2), (m-0.08, 0.28), (-m+0.08, 0.28), (-m, 0.2)], P.pts(0, L, 1.5))
            for k in range(1, 8): 
                s = L*k/8
                M.sweep('median_seams', 'concrete_weathered', rprof(-m+0.1, m-0.1, 0.28, 0.295), P.pts(s-0.025, s+0.025, 1))
            for f in (0.25, 0.75):
                x, y, z = P.f(L*f)
                M.add('lamp_socket', 'galvanized_steel', box(-0.3, 0.28, -0.3, 0.3, 0.33, 0.3, 0.015).move(x, y, z))
    # lane markings
    for side in (-1, 1):
        for k in range(1, n):
            x = side*(med/2 + k*lw)
            s0 = 0
            while s0 < L-0.1:
                markline(M, P, x, 0.12, s0, min(s0+3, L)); s0 += 6
    if med == 0:
        markline(M, P, -0.11, 0.09, 0, L, 'marking_yellow'); markline(M, P, 0.11, 0.09, 0, L, 'marking_yellow')
    # expansion seams + wear tracks + arrows
    for s in (L/3, 2*L/3):
        for side in (-1, 1):
            M.sweep('seams', 'concrete_weathered', rprof(*sorted((side*med/2, side*hw)), 0, 0.012), P.pts(s-0.04, s+0.04, 0.04))
    for side in (-1, 1):
        for k in range(n):
            xc = side*(med/2 + (k+0.5)*lw)
            a, b = ((0.8, L*0.42) if (k+(side > 0)) % 2 == 0 else (L*0.55, L-0.8))
            for off in (-0.8, 0.8):
                M.sweep('wear', 'asphalt_cool', rprof(xc+off-0.25, xc+off+0.25, 0, 0.008), P.pts(a, b, 1.5))
            if arrows and P.straight:
                arrow(M, P, xc, L*0.5 + (2.2 if side > 0 else -2.2), +1 if side < 0 else -1)
    # connections
    e0, e1 = P.f(0), P.f(L)
    for nm, e, dr in (('end_A', e0, (0, 0, -1)), ('end_B', e1, (0, 0, 1))):
        M.cn(nm, e, dr, carriageway_width=round(2*hw, 3), total_width_with_curbs=round(2*hw+2*CW, 3), curb_height=CH, lanes=2*n, lane_width=lw, surface_y=round(e[1], 3))
    return hw

def straight(z0=-6, z1=6, rise=0.0): return line_path((0, 0, z0), (0, rise, z1))

# ------------------------------------------------------------------ straight modules
def ROAD_01():
    M = Model('ROAD_01', 'roads', 'Two-lane city road, 12 m module'); build_road(M, straight(), 1); return M
def ROAD_02():
    M = Model('ROAD_02', 'roads', 'Four-lane boulevard with planted median, 12 m module'); build_road(M, straight(), 2, 1.6, 'planted'); return M
def ROAD_03():
    M = Model('ROAD_03', 'roads', 'Six-lane main avenue with paved median, 12 m module'); build_road(M, straight(), 3, 2.4, 'stone'); return M

# ------------------------------------------------------------------ junction helpers
def arm_local(M, with_curb_left, with_curb_right, ctr_from=5.6):
    """Arm in local +Z (N) frame: slab from z=H..6, crosswalk, stop line, markings, optional curb stubs."""
    M.box('surface', 'asphalt_cool', -H, -SL, H, H, 0, 6.0)
    for sd in (-1, 1):
        M.add('markings', 'asphalt_cool', box(*sorted((sd*(H-0.45), sd*H))[:1], 0, H+RF, sorted((sd*(H-0.45), sd*H))[1], 0.012, 6.0)) if False else None
        x0, x1 = sorted((sd*(H-0.45), sd*H))
        M.box('markings', 'asphalt_cool', x0, 0, H+RF, x1, 0.012, 6.0)
        M.box('markings', 'marking_white', sd*(H-0.6)-0.06, 0, H+RF, sd*(H-0.6)+0.06, 0.02, 6.0)
    M.box('markings', 'marking_yellow', -0.155, 0, ctr_from, -0.065, 0.02, 6.0)
    M.box('markings', 'marking_yellow', 0.065, 0, ctr_from, 0.155, 0.02, 6.0)
    for i in range(6):                       # zebra crossing
        xc = -2.25 + 0.9*i
        M.box('crosswalk', 'marking_white', xc-0.25, 0, 3.65, xc+0.25, 0.02, 4.55)
    M.box('markings', 'marking_white', 0.25, 0, 5.1, H-0.7, 0.02, 5.35)   # stop line (inbound lane = +x side)
    # small guide arrows
    for xc, sg in ((-1.7, +1), (1.7, -1)):
        p = line_path((0, 0, 0), (0, 0, 10))
        arrow(M, p, xc, 5.45 if False else 5.62, sg, 0.38) if False else None
    if with_curb_right: M.add('curb', 'concrete_pale', profile_ext(curb_prof(H, +1), H+RF, 6.0))
    if with_curb_left: M.add('curb', 'concrete_pale', profile_ext(curb_prof(H, -1), H+RF, 6.0))

def corner_fillet(M):
    """NE corner fillet (local N frame): asphalt fill + chamfered curb arc."""
    C = (H+RF, H+RF)
    arc = arc_pts(C[0], C[1], RF, 180, 270, 6)
    M.ext('surface', 'asphalt_warm', [(H, H), (H, H+RF)] + arc[1:], -SL, 0)
    M.add('curb', 'concrete_pale', band(RF-CW, RF, 0, CH, 180, 270, 6, C[0], C[1], rt1=RF-0.07))

def junction(M, arms):
    M.box('surface', 'asphalt_warm', -H, -SL, -H, H, 0, H)
    for i in range(6):                       # subtle centre-box seams
        pass
    tmp = Model('t', 'x')
    for a in arms:
        t = Model('t', 'x')
        arm_local(t, NEXT[a] and (list(NEXT.keys())[(list(NEXT.keys()).index(a)-1) % 4] in arms), NEXT[a] in arms)
        for (g, m), p in t.groups.items(): M.add(g, m, p.rot('y', ANG[a]))
        if NEXT[a] in arms:
            t = Model('t', 'x'); corner_fillet(t)
            for (g, m), p in t.groups.items(): M.add(g, m, p.rot('y', ANG[a]))
    for x in ANG:
        if x not in arms:
            M.add('curb', 'concrete_pale', profile_ext(curb_prof(H, +1), -6.0, 6.0).rot('y', ANG[x]-90))
    # central wear / seam detail
    M.box('markings', 'concrete_weathered', -H+0.02, 0, -0.03, H-0.02, 0.01, 0.03) if False else None
    for a in arms:
        d = {'N': (0, 1), 'E': (1, 0), 'S': (0, -1), 'W': (-1, 0)}[a]
        M.cn(f'arm_{a}', (d[0]*6, 0, d[1]*6), (d[0], 0, d[1]), carriageway_width=2*H, total_width_with_curbs=2*H+2*CW, curb_height=CH, lanes=2, lane_width=LW, surface_y=0)

def ROAD_04():
    M = Model('ROAD_04', 'roads', 'T-intersection (arms E,S,W; north closed), 12x12 m'); junction(M, ['E', 'S', 'W']); return M
def ROAD_05():
    M = Model('ROAD_05', 'roads', 'Four-way intersection, 12x12 m'); junction(M, ['N', 'E', 'S', 'W']); return M

# ------------------------------------------------------------------ roundabout
def ROAD_06():
    M = Model('ROAD_06', 'roads', 'Roundabout with raised planted island, 24x24 m (arms along +/-X,+/-Z)')
    R0, R1 = 4.25, 8.5
    for k in range(8):
        M.add('surface', 'asphalt_warm' if k % 2 == 0 else 'asphalt_cool', band(R0, R1, -SL, 0, k*45, (k+1)*45, 6))
    for ang in range(0, 360, 20): M.add('markings', 'marking_white', band(6.34, 6.46, 0, 0.02, ang, ang+11, 2))
    # island curb + soil + stone bed
    M.add('island_curb', 'concrete_pale', band(4.0, R0, 0, CH, 0, 360, 1, rt1=4.18) if False else merge([band(4.0, R0, 0, CH, k*30, (k+1)*30, 2, rt1=R0-0.07) for k in range(12)]))
    M.add('island_soil', 'soil', lathe([(0.01, -0.4), (4.0, -0.4), (4.0, 0.1), (3.85, 0.2), (2.4, 0.3), (0.01, 0.3)], 24))
    M.add('island_bed', 'dusty_stone', merge([band(1.55, 2.0, 0.25, 0.65, k*45, (k+1)*45, 2, rt0=1.65, rt1=1.9, ) for k in range(8)]))
    M.add('island_plinth', 'concrete_pale', cylb(0.9, 0.9, 12, 0.25, b=0.08))
    M.add('island_plinth', 'soil', cyl(0.62, 0.02, 12, 1.14))
    # outer curbs between arms
    a = math.degrees(math.asin((H+CW)/R1))
    for k in range(4):
        M.add('curb', 'concrete_pale', band(R1, R1+CW, 0, CH, k*90+a+1.5, (k+1)*90-a-1.5, 8, rt1=R1+CW, rt0=R1+0.07) if False else band(R1, R1+CW, 0, CH, k*90+a, (k+1)*90-a, 8, rt0=R1+0.07))
    zc = lambda x: math.sqrt(R1*R1 - x*x)
    for ang in (0, 90, 180, 270):
        xs = [-H + 2*H*i/6 for i in range(7)]
        poly = [(-H, 12.0), (-H, zc(-H))] + [(x, zc(x)) for x in xs[1:-1]] + [(H, zc(H)), (H, 12.0)]
        t = Model('t', 'x')
        t.ext('surface', 'asphalt_cool', poly, -SL, 0)
        z0 = zc(H)+0.1
        for sd in (-1, 1):
            x0, x1 = sorted((sd*(H-0.45), sd*H))
            t.box('markings', 'asphalt_cool', x0, 0, z0+0.6, x1, 0.012, 12.0)
            t.box('markings', 'marking_white', sd*(H-0.6)-0.06, 0, z0+0.6, sd*(H-0.6)+0.06, 0.02, 12.0)
            t.add('curb', 'concrete_pale', profile_ext(curb_prof(H, sd), z0, 12.0))
        t.box('markings', 'marking_yellow', -0.155, 0, 11.0, -0.065, 0.02, 12.0); t.box('markings', 'marking_yellow', 0.065, 0, 11.0, 0.155, 0.02, 12.0)
        for i in range(6):
            xc = -2.25 + 0.9*i; t.box('crosswalk', 'marking_white', xc-0.25, 0, 10.7, xc+0.25, 0.02, 11.4)
        for i in range(4):                      # yield "shark teeth" on inbound lane
            xc = 0.6 + 0.7*i
            t.ext('markings', 'marking_white', [(xc-0.28, 11.55), (xc+0.28, 11.55), (xc, 11.95)], 0, 0.02)
        # splitter island
        sp = [(0, 9.1), (0.9, 9.9), (0.9, 10.4), (0, 10.55), (-0.9, 10.4), (-0.9, 9.9)]
        cx = sum(p[0] for p in sp)/6; cz = sum(p[1] for p in sp)/6
        t.ext('splitter', 'concrete_pale', sp, 0, CH, [(cx+(x-cx)*0.82, cz+(z-cz)*0.82) for x, z in sp])
        for (g, m), p in t.groups.items(): M.add(g, m, p.rot('y', ang))
        d = {0: (0, 1), 90: (1, 0), 180: (0, -1), 270: (-1, 0)}[ang]
        M.cn(f'arm_{ang}', (d[0]*12, 0, d[1]*12), (d[0], 0, d[1]), carriageway_width=2*H, total_width_with_curbs=2*H+2*CW, curb_height=CH, lanes=2, lane_width=LW, surface_y=0)
    M.notes.append('Module is 24 m; arms join standard 12 m two-lane modules at +/-12 m.')
    return M

# ------------------------------------------------------------------ curved / sloped / coastal
def ROAD_07():
    M = Model('ROAD_07', 'roads', '90-degree curved two-lane road, centreline radius 12 m; enters (0,0,-6) heading +Z, exits (12,0,6) heading +X')
    P = arc_path(12, -6, 12, 180, 90); build_road(M, P, 1, arrows=False); return M

def ROAD_08():
    M = Model('ROAD_08', 'roads', 'Sloped two-lane road: +1.5 m over 12 m, with embankment fill')
    P = line_path((0, 0, -6), (0, 1.5, 6)); hw = build_road(M, P, 1, arrows=False)
    M.sweep('embankment', 'dusty_stone', rprof(-hw-CW, hw+CW, -1.8, -SL), P.pts(0, P.L))
    for f in (0.25, 0.5, 0.75):                      # slope chevrons
        s = P.L*f
        for xc, sg in ((-1.7, +1),):
            pass
    for s in (4.0, 8.0):
        M.add('markings', 'marking_white', sweep2([rprof(-1.9, -1.4, 0, 0.02), rprof(-1.7, -1.7, 0, 0.02)], P.pts(s, s+0.5, 9)[:2]) if False else sweep(rprof(-2.15, -1.25, 0, 0.02), P.pts(s, s+0.3, 1)))
    return M

def ROAD_09():
    M = Model('ROAD_09', 'roads', 'Coastal boulevard: two lanes + 4.2 m sea-side promenade (+X side), parapet with railing sockets, seawall lip')
    P = straight(); hw = build_road(M, P, 1)
    x0 = hw+CW; x1 = x0+4.2
    M.sweep('promenade', 'concrete_weathered', rprof(x0, x1, -SL, 0.07), P.pts(0, 12))
    M.sweep('promenade', 'concrete_pale', rprof(x0, x1-0.35, 0.07, CH), P.pts(0, 12))
    for k in range(1, 10):
        M.sweep('promenade_seams', 'concrete_weathered', rprof(x0, x1-0.35, CH, CH+0.012), P.pts(k*1.2-0.02, k*1.2+0.02, 1))
    for xs in (x0+1.4, x0+2.8):
        M.sweep('promenade_seams', 'concrete_weathered', rprof(xs-0.02, xs+0.02, CH, CH+0.012), P.pts(0, 12))
    M.sweep('parapet', 'concrete_pale', [(x1-0.35, CH), (x1, CH), (x1, 0.62), (x1-0.06, 0.68), (x1-0.29, 0.68), (x1-0.35, 0.62)], P.pts(0, 12))
    M.sweep('seawall_lip', 'concrete_weathered', rprof(x1-0.7, x1+0.1, -2.2, -SL), P.pts(0, 12))
    M.sweep('seawall_lip', 'coastal_weathered', rprof(x1-0.1, x1+0.4, -2.2, -1.9), P.pts(0, 12))
    for z in (-4.5, -1.5, 1.5, 4.5):
        M.add('railing_socket', 'galvanized_steel', cylb(0.09, 0.05, 8, 0.68, x1-0.17, z, 0.01))
        M.cn(f'railing_mount_z{z}', (x1-0.17, 0.73, z), (0, 1, 0), mates='HARBOR_12')
    M.cn('seawall_interface', (x1+0.1, -0.4, 0), (1, 0, 0), mates='HARBOR_04')
    return M

# ------------------------------------------------------------------ highway
def ROAD_10():
    M = Model('ROAD_10', 'roads', 'Highway section: 2 lanes per direction (3.5 m), 2.5 m paved shoulders, jersey median, edge parapets with guardrail sockets')
    P = straight(); lw = 3.5; m = 0.6; hw = m + 2*lw; sh = 2.5
    for side in (-1, 1):
        xa, xb = sorted((side*m, side*(hw+sh)))
        for k in range(3):
            M.sweep('surface', 'asphalt_warm' if (k+(side > 0)) % 2 == 0 else 'asphalt_cool', rprof(xa, xb, -SL, 0), P.pts(4*k, 4*k+4))
        M.sweep('shoulder', 'asphalt_cool', rprof(*sorted((side*hw, side*(hw+sh))), 0, 0.012), P.pts(0, 12))
        markline(M, P, side*(hw-0.1), 0.15, 0, 12); markline(M, P, side*(m+0.2), 0.15, 0, 12, 'marking_yellow')
        x = side*(m+lw)
        for s0 in (0, 6): markline(M, P, x, 0.15, s0, s0+3)
        e = side*(hw+sh)
        M.sweep('edge_parapet', 'concrete_pale', [(e, -SL), (e+side*0.45, -SL), (e+side*0.45, 0.4), (e+side*0.32, 0.5), (e+side*0.1, 0.5), (e, 0.35)] if side > 0 else
                [(e-0.45, -SL), (e, -SL), (e, 0.35), (e-0.1, 0.5), (e-0.32, 0.5), (e-0.45, 0.4)], P.pts(0, 12))
        for z in (-4, 0, 4):
            M.add('guardrail_socket', 'galvanized_steel', cylb(0.08, 0.05, 8, 0.5, e+side*0.22, z, 0.01))
            M.cn(f'guardrail_mount_{"R" if side > 0 else "L"}_z{z}', (e+side*0.22, 0.55, z), (0, 1, 0), mates='PROP_10')
        for s in range(2, 12, 4):
            M.sweep('seams', 'concrete_weathered', rprof(*sorted((side*m, side*(hw+sh))), 0, 0.012), P.pts(s-0.04, s+0.04, 1))
        for k in range(2):
            xc = side*(m+(k+0.5)*lw)
            M.sweep('wear', 'asphalt_cool', rprof(xc-1.05, xc-0.55, 0, 0.008), P.pts(1, 5)); M.sweep('wear', 'asphalt_cool', rprof(xc+0.55, xc+1.05, 0, 0.008), P.pts(7, 11))
        arrow(M, P, side*(m+1.5*lw), 6.0, +1 if side < 0 else -1)
    M.sweep('median_barrier', 'concrete_pale', [(-0.6, -SL), (0.6, -SL), (0.6, 0.12), (0.4, 0.35), (0.27, 0.8), (-0.27, 0.8), (-0.4, 0.35), (-0.6, 0.12)], P.pts(0, 12))
    for z in (-6, 6): pass
    M.sweep('median_cap', 'concrete_weathered', rprof(-0.27, 0.27, 0.8, 0.84), P.pts(0, 12))
    for e0, dr in ((P.f(0), (0, 0, -1)), (P.f(12), (0, 0, 1))):
        M.cn('end', e0, dr, carriageway_width=2*(hw), total_width_incl_shoulders_and_parapets=2*(hw+sh+0.45), lanes=4, lane_width=lw, shoulder=sh, surface_y=0)
    return M

def ROAD_11():
    M = Model('ROAD_11', 'roads', 'Elevated curved highway ramp: 60 deg arc R=28 m, +4 m rise, one-way 2 x 3.5 m lanes, girder + pier, parapet sockets')
    P = arc_path(28, -6, 28, 180, 120, 0, 4.0); lw = 3.5; hw = lw
    M.sweep('deck', 'asphalt_warm', rprof(-hw-0.6, hw+0.6, -0.6, 0), P.pts(0, P.L, 2))
    M.sweep('girder', 'concrete_weathered', [(-3.2, -0.6), (3.2, -0.6), (2.3, -1.6), (-2.3, -1.6)], P.pts(0, P.L, 2))
    for side in (-1, 1):
        e = side*(hw+0.6)
        M.sweep('parapet', 'concrete_pale', [(e, -0.6), (e+side*0.0, 0.0), (e - side*0.0, 0), (e, 0.6), (e-side*0.25, 0.6), (e-side*0.35, 0.2), (e-side*0.55, 0.0), (e-side*0.55, -0.6)] if False else
                ([(e-0.55, -0.6), (e, -0.6), (e, 0.85), (e-0.2, 0.9), (e-0.3, 0.85), (e-0.38, 0.35), (e-0.55, 0.0)] if side > 0 else [(e, -0.6), (e+0.55, -0.6), (e+0.55, 0.0), (e+0.38, 0.35), (e+0.3, 0.85), (e+0.2, 0.9), (e, 0.85)]), P.pts(0, P.L, 2))
        markline(M, P, side*(hw-0.2), 0.14, 0, P.L)
        for s in range(2, int(P.L), 5):
            x, y, z = P.f(s); t = norm(sub(P.f(min(s+0.5, P.L)), P.f(max(s-0.5, 0)))); Lv = (t[2], 0, -t[0])
            px, pz = x+Lv[0]*(e-side*0.45), z+Lv[2]*(e-side*0.45)
            M.add('guardrail_socket', 'galvanized_steel', cylb(0.08, 0.05, 8, y+0.9, px, pz, 0.01))
    s0 = 0
    while s0 < P.L-1: markline(M, P, 0, 0.14, s0, min(s0+3, P.L)); s0 += 6
    arrow_p = P
    x, y, z = P.f(P.L*0.85)
    M.add('pier', 'concrete_weathered', cylb(0.55, y-1.6, 10, 0, x, z, 0.06))
    M.add('pier_cap', 'concrete_pale', box(x-2.2, y-1.9, z-0.7, x+2.2, y-1.6, z+0.7, 0.05).rot('y', -math.degrees(math.atan2(P.f(P.L*0.85+0.3)[2]-z, P.f(P.L*0.85+0.3)[0]-x))+0, (x, y, z)) if False else cylb(1.0, 0.3, 10, y-1.9, x, z, 0.04))
    M.add('pier_foot', 'concrete_weathered', box(x-1.0, -0.4, z-1.0, x+1.0, 0, z+1.0, 0.05))
    M.cn('end_A', P.f(0), (0, 0, -1), width=2*(hw+0.6), lanes=2, lane_width=lw, surface_y=0)
    M.cn('end_B', P.f(P.L), (norm(sub(P.f(P.L), P.f(P.L-0.5)))), width=2*(hw+0.6), lanes=2, lane_width=lw, surface_y=4.0)
    return M

# ------------------------------------------------------------------ sidewalk, corner, island
def ROAD_12():
    M = Model('ROAD_12', 'roads', 'Sidewalk module 3 x 12 m, top at +0.15 m; road-side edge at x=-1.5; furniture slots at x=-0.85')
    M.box('base', 'concrete_weathered', -1.5, -SL, -6, 1.5, 0.1, 6)
    g = 0.02
    for i in range(3):
        for j in range(12):
            M.box('tiles', 'concrete_pale' if (i+j) % 2 == 0 else 'concrete_weathered' if False else 'concrete_pale', -1.5+i+g, 0.1, -6+j+g, -0.5+i-g, 0.15, -5+j-g)
    M.box('building_edge', 'concrete_weathered', 1.38, 0.1, -6, 1.5, 0.17, 6, 0.01)
    for z in (-4, 0, 4):
        M.box('furniture_slot', 'concrete_weathered', -1.1, 0.15, z-0.3, -0.6, 0.165, z+0.3, 0.01)
        M.cn(f'furniture_slot_z{z}', (-0.85, 0.165, z), (0, 1, 0), mates='PROP_*')
    M.add('manhole', 'brushed_metal', cylb(0.32, 0.02, 12, 0.15, 0.6, 2.0, 0.008))
    for r in (0.12, 0.22): M.add('manhole', 'rubber_dark', cyl(r, 0.005, 10, 0.17, 0.6, 2.0))
    M.cn('end_A', (0, 0.15, -6), (0, 0, -1), width=3.0, surface_y=0.15); M.cn('end_B', (0, 0.15, 6), (0, 0, 1), width=3.0, surface_y=0.15)
    M.notes.append('Place with road-side edge against curb outer face (x = carriageway half-width + 0.25).')
    return M

def ROAD_13():
    M = Model('ROAD_13', 'roads', 'Street corner sidewalk 3x3 m with R=1.25 m rounded curb corner, tactile paving. Origin = JUNCTION CENTRE (NE corner; rotate 90 deg steps)')
    C = (H+RF, H+RF); r = RF-CW; a0 = 3.65
    arc = arc_pts(C[0], C[1], r, 180, 270, 7)
    poly = [(6.65, a0), (6.65, 6.65), (a0, 6.65)] + arc
    M.ext('base', 'concrete_weathered', poly, -SL, 0.1)
    M.ext('paving', 'concrete_pale', poly, 0.1, 0.15)
    for x in (4.65, 5.65): M.box('seams', 'concrete_weathered', x-0.02, 0.15, 3.9 if x < 5 else 3.65, x+0.02, 0.157, 6.65)
    for z in (4.65, 5.65): M.box('seams', 'concrete_weathered', 3.9 if z < 5 else 3.65, 0.15, z-0.02, 6.65, 0.157, z+0.02)
    for (px, pz, sw) in ((3.75, 5.45, False), (5.45, 3.75, True)):
        w, d = (0.8, 0.5) if not sw else (0.5, 0.8)
        M.box('tactile', 'tactile_yellow', px, 0.15, pz, px+(0.5 if not sw else 0.8), 0.162, pz+(0.8 if not sw else 0.5), 0.005)
        nx, nz = (4, 5) if not sw else (5, 4)
        for i in range(nx):
            for j in range(nz):
                M.add('tactile', 'tactile_yellow', cyl(0.055, 0.025, 5, 0.162, px+0.08+i*0.115 if False else px+0.07+i*(0.5/nx if not sw else 0.8/nx), pz+0.07+j*(0.8/nz if not sw else 0.5/nz), 0.035))
    M.add('curb_cap', 'concrete_pale', band(r-0.0, r+0.04, 0.15, 0.17, 180, 270, 7, C[0], C[1]))
    M.cn('end_x', (6.65, 0.15, 5.15), (1, 0, 0), width=3.0, mates='ROAD_12 (offset)'); M.cn('end_z', (5.15, 0.15, 6.65), (0, 0, 1), width=3.0, mates='ROAD_12 (rotated)')
    return M

def ROAD_14():
    M = Model('ROAD_14', 'roads', 'Pedestrian-refuge traffic island on a four-lane boulevard (matches ROAD_02 profile at ends)')
    P = straight(); build_road(M, P, 2, 1.6, 'none')
    M.sweep('median_base', 'concrete_weathered', rprof(-0.8, 0.8, -SL, 0), P.pts(0, 12))
    poly = [(-0.8, -6), (0.8, -6), (1.8, -3), (1.8, 3), (0.8, 6), (-0.8, 6)]
    top = [(x*0.9 if abs(x) > 1 else x*0.96, z*0.985) for x, z in poly]
    M.ext('island_curb', 'concrete_pale', poly, 0, 0.22, top)
    M.ext('island_deck', 'concrete_weathered', [(x*0.8, z*0.9) for x, z in poly], 0.22, 0.25)
    M.ext('island_planter', 'soil', [(x*0.55, z*0.6) for x, z in poly if True][:6], 0.25, 0.3) if False else None
    for sz in (-1, 1):
        M.box('refuge_bed', 'soil', -0.35, 0.25, sz*3.9-0.9 if False else (sz*3.8-0.8), 0.35, 0.29, sz*3.8+0.8)
        M.add('bollard_socket', 'galvanized_steel', cylb(0.14, 0.03, 8, 0.25, 0, sz*5.2, 0.01))
        M.cn(f'bollard_mount_z{sz*5.2}', (0, 0.28, sz*5.2), (0, 1, 0), mates='PROP_09')
    M.box('refuge_crossing', 'tactile_yellow', -1.3, 0.25, -0.5, 1.3, 0.262, 0.5, 0.005)
    for i in range(6):
        for j in range(3): M.add('tactile', 'tactile_yellow', cyl(0.05, 0.025, 5, 0.262, -1.1+i*0.44, -0.3+j*0.3, 0.03))
    for z in (-5.3, 5.3): M.box('nose_marking', 'safety_yellow', -0.5, 0.22, z-0.3, 0.5, 0.227, z+0.3, 0.005)
    return M

ROADS = [ROAD_01, ROAD_02, ROAD_03, ROAD_04, ROAD_05, ROAD_06, ROAD_07, ROAD_08, ROAD_09, ROAD_10, ROAD_11, ROAD_12, ROAD_13, ROAD_14]
