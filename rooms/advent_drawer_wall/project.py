"""The Advent Stair: an 8 m² kids' room (2.6 x 3.1 m, 2.8 m ceiling) that builds itself while snow falls past the
window. A loft bed on the north wall; its six-step storage stair on the east wall hides 24 small drawers (21 in the
stepped side face, 3 in the top risers). They ripple open bottom to top on a rising scale, each dropping its front
into a little ledge with a tiny treasure on it, then shut in a descending ripple. The child climbs, opens the top
drawer and puts its star on the tree in the loft as the fairy lights come on. White + light oak + forest green.
No on-screen text: no numbers or letters on the drawers.

    ROOM_REST=1 python3 ../../pipeline/run.py project.py <workdir> probe 0.5,1.5,2.5,3.5,4.5     # finished room, stations
    python3 ../../pipeline/run.py project.py <workdir> preview                                     # code-renderer preview
    ROOM_CUT=long ...                                                                              # the long cut

Units: metres. x = east, y = north, z = up. Room x 0..W, y 0..D, z 0..H.
North wall: loft bed (deck y 2.15..3.1 at 1.38 m) under a snowy window, a den beneath it. East wall: the stair.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'pipeline'))
import roomkit as rk
from roomkit import (srgb, mat, add, box, grid_tris, lathe, rprof, tube, ellipsoid, rbox, T, S, R, about, xform, wood,
                     wood_mats, rect_light, sphere_light, spot_rect)
from animkit import Timeline, c01, eoc, eob, smooth
from camkit import hold_camera
import figure as fg

REST = os.environ.get('ROOM_REST') == '1'
REST_NIGHT = os.environ.get('ROOM_NIGHT') == '1'
CUT = os.environ.get('ROOM_CUT', 'short')

W, D, H = 2.6, 3.1, 2.8
FPS = 25
DUR_SHORT, DUR_LONG = 15.0, 44.0
DUR = 6.0 if REST else (DUR_LONG if CUT == 'long' else DUR_SHORT)

WX0, WX1, WZ0, WZ1 = 0.95, 2.00, 1.62, 2.55        # north window opening (above the loft)
LY0, LZ0, LZ1 = 2.15, 1.30, 1.38                   # loft deck front edge, underside, top (deck spans x 0..W, y LY0..D)
SX0, SX1 = 2.10, 2.60                              # stair x (side face at SX0 faces west, into the room)
SY0, TD, RZ, NST = 0.83, 0.22, 0.23, 6             # stair start y, tread depth, riser, steps
SDEP = 0.24                                          # side-drawer depth (west half of the stair)
GAP = 0.005
SLIDE = 0.10                                       # a drawer tray slides out this far, then its front drops into a ledge
TREE = (2.36, 2.78, LZ1)                           # tree on the loft landing
DL = [(0.95, 1.05), (1.75, 1.05)]
SUN_DIR = np.array([0.25, -0.55, -0.80]) / np.linalg.norm([0.25, -0.55, -0.80])
SNOW_V = (0.34, 0.22)                              # fall speed of the near / far snow layers
CAPTIONS = []                                      # no on-screen text

KID = [None]


# ------------------------------------------------------------------------------------------- materials
def materials():
    mat('subfloor', tex=3, col=srgb(150, 148, 146), p=(0.12,))
    mat('floor', tex=1, col=srgb(214, 188, 152), col2=srgb(198, 170, 134), rough=0.40, f0=0.04, glossy=True, p=(0.18, 1.5))
    mat('wall', tex=3, col=srgb(240, 239, 236), p=(0.015,))
    mat('ceiling', col=srgb(247, 247, 246))
    mat('white_cab', col=srgb(243, 242, 239), rough=0.42)
    mat('white_in', col=srgb(235, 234, 231))
    mat('plinth', col=srgb(226, 224, 220))
    wood_mats('oak', srgb(216, 186, 146), seed=3.0)
    wood_mats('oakl', srgb(226, 202, 166), seed=8.0)
    mat('knob', col=srgb(246, 245, 242), rough=0.25, f0=0.04, glossy=True)
    mat('winframe', col=srgb(244, 244, 242), rough=0.35)
    mat('sill', col=srgb(242, 241, 238), rough=0.25, f0=0.04, glossy=True)
    mat('green', tex=6, col=srgb(52, 96, 72))
    mat('green_knit', tex=5, col=srgb(56, 100, 76), p=(0, 0.012))
    mat('linen', tex=3, col=srgb(240, 239, 236), rough=0.9, p=(0.04,))
    mat('linen_grey', tex=3, col=srgb(214, 214, 212), rough=0.9, p=(0.05,))
    mat('mattress', tex=5, col=srgb(246, 246, 244), p=(0, 0.02))
    mat('rug', tex=6, col=srgb(232, 229, 222))
    mat('ceramic', col=srgb(244, 243, 240), rough=0.22, f0=0.04, glossy=True)
    mat('basket', tex=5, col=srgb(206, 186, 150), p=(2, 0.01))
    mat('pine', tex=3, col=srgb(40, 78, 54), rough=0.8, p=(0.12,))
    mat('pine2', tex=3, col=srgb(54, 96, 66), rough=0.8, p=(0.12,))
    mat('gold', col=srgb(222, 184, 112), rough=0.25, metal=1)
    mat('wire', col=srgb(60, 70, 60), rough=0.5)
    mat('bulb_off', col=srgb(246, 242, 228), rough=0.15, f0=0.05, glossy=True)
    mat('bulb_on', col=(0, 0, 0), emis=(9.0, 7.2, 4.6))
    mat('led', col=(0, 0, 0), emis=(7.5, 6.6, 5.0))
    mat('led_off', col=srgb(232, 230, 226))
    mat('dl_emis', col=(0, 0, 0), emis=(8.5, 7.6, 6.2))
    mat('lamp_bulb', col=(0, 0, 0), emis=(9.0, 7.6, 5.6))
    mat('lampshade', col=srgb(244, 242, 236), rough=0.6, emis=(0.0, 0.0, 0.0))
    mat('glint_glow', col=(0, 0, 0), emis=(16.0, 14.5, 11.0))
    mat('duvet_gold', tex=3, col=srgb(208, 188, 146), rough=0.9, p=(0.04,))
    mat('star_glow', col=(0, 0, 0), emis=(9.0, 7.4, 4.0))
    mat('blackm', col=srgb(34, 34, 36), rough=0.4, f0=0.04, glossy=True)
    # outside (camera-only emitters: they never light the room)
    mat('sky_day', col=(0, 0, 0), emis=(0.70, 0.78, 0.96))
    mat('sky_dusk', col=(0, 0, 0), emis=(0.16, 0.22, 0.50))
    mat('snow_day', col=(0, 0, 0), emis=(1.18, 1.20, 1.26))
    mat('snow_dusk', col=(0, 0, 0), emis=(0.26, 0.32, 0.56))
    mat('pineo_day', col=(0, 0, 0), emis=(0.07, 0.13, 0.10))
    mat('pineo_dusk', col=(0, 0, 0), emis=(0.03, 0.05, 0.08))
    mat('house_day', col=(0, 0, 0), emis=(0.80, 0.78, 0.78))
    mat('house_dusk', col=(0, 0, 0), emis=(0.12, 0.13, 0.22))
    mat('roof_day', col=(0, 0, 0), emis=(0.42, 0.44, 0.50))
    mat('win_dusk', col=(0, 0, 0), emis=(2.4, 1.7, 0.9))
    mat('flake', col=(0, 0, 0), emis=(1.7, 1.7, 1.75))
    # toys (colour from filled storage)
    for nm, c in (('toy_red', (196, 52, 48)), ('toy_mustard', (226, 178, 64)), ('toy_blue', (104, 150, 204)),
                  ('toy_green', (52, 104, 74)), ('toy_white', (245, 244, 241)), ('toy_black', (32, 32, 34)),
                  ('toy_sky', (150, 190, 226)), ('toy_ginger', (196, 146, 98))):
        mat(nm, col=srgb(*c), rough=0.32, f0=0.04, glossy=True)
    mat('plush', tex=6, col=srgb(214, 194, 166))
    mat('plush_light', tex=6, col=srgb(240, 230, 214))
    mat('plush_white', tex=6, col=srgb(244, 243, 240))
    mat('knit_red', tex=5, col=srgb(186, 52, 50), p=(2, 0.008))
    mat('knit_white', tex=5, col=srgb(244, 243, 240), p=(2, 0.008))
    mat('cane', tex=7, col=srgb(246, 245, 242), col2=srgb(196, 46, 44), p=(2, 0.018))
    mat('toy_wood', tex=2, col=srgb(222, 190, 148), p=(0, 4.0))
    for nm, c in (('bk_green', (60, 104, 80)), ('bk_red', (190, 62, 56)), ('bk_blue', (96, 140, 196)),
                  ('bk_mustard', (222, 176, 70)), ('bk_white', (242, 240, 236)), ('bk_sky', (160, 196, 226)),
                  ('bk_grey', (176, 178, 182))):
        mat(nm, col=srgb(*c), rough=0.6)
    mat('kid_top', col=srgb(156, 180, 210), rough=0.5, f0=0.04)
    fg.materials()


# ------------------------------------------------------------------------------------------- helpers
def disc(inst, c, r, z0, z1, m, n=28):
    add(inst, lathe(rprof(r, z0, z1, min(0.004, (z1 - z0) * 0.45), 3), n, c), m)


def put(inst, parts, c, s=1.0, yaw=0.0):
    M = T(*c) @ R('z', yaw) @ S(s, s, s)
    for PN, m in parts:
        add(inst, xform(PN, M), m)


def star_prism(c, r_out, r_in, th, n=5):
    """Five-point star standing upright in the x-z plane (faces -y / +y), centred at c."""
    c = np.array(c, float)
    pts = []
    for k in range(2 * n):
        a = math.pi / 2 + math.pi * k / n
        r = r_out if k % 2 == 0 else r_in
        pts.append(np.array([math.cos(a) * r, 0.0, math.sin(a) * r]))
    P, N = [], []
    for sgn in (-1, 1):
        off = np.array([0, sgn * th / 2, 0])
        cc = c + off
        for k in range(2 * n):
            a, b = c + pts[k] + off, c + pts[(k + 1) % (2 * n)] + off
            tri = [cc, a, b] if sgn > 0 else [cc, b, a]
            P.append(tri); N.append([(0, sgn, 0)] * 3)
    for k in range(2 * n):
        a, b = pts[k], pts[(k + 1) % (2 * n)]
        a0, b0 = c + a + [0, -th / 2, 0], c + b + [0, -th / 2, 0]
        a1, b1 = c + a + [0, th / 2, 0], c + b + [0, th / 2, 0]
        e = b - a
        nn = np.array([e[2], 0, -e[0]]); nn /= np.linalg.norm(nn) + 1e-12
        if np.dot(nn, (a + b) / 2) < 0:
            nn = -nn
        P += [[a0, b0, b1], [a0, b1, a1]]; N += [[nn] * 3, [nn] * 3]
    return np.array(P), np.array(N)


def torus(c, R0, r, z, n=20, m=8):
    prof = [(R0 + r * math.cos(2 * math.pi * k / m), z + r * math.sin(2 * math.pi * k / m)) for k in range(m + 1)]
    return lathe(prof, n, c)


def wheel(c, r, w, axis='y'):
    """Disc with its axis along y (car wheels seen from the side)."""
    PN = lathe(rprof(r, -w / 2, w / 2, min(0.004, w * 0.4), 2), 14)
    return xform(PN, T(*c) @ R('x', math.pi / 2))


def cloth(inst, x0, x1, y0, y1, z_top, z_hem, r, m, seed, sides=('w', 'e', 's'), puff=0.012):
    """Draped fabric: a gently wrinkled top plus rounded edges falling into softly folded skirts."""
    ph = np.random.default_rng(seed).uniform(0, 6.283, 5)
    xc, hw = (x0 + x1) / 2, (x1 - x0) / 2

    def wob(x, y):
        return (0.008 * math.sin(x * 9 + ph[0]) * math.sin(y * 5 + ph[1]) + 0.004 * math.sin(x * 17 + y * 11 + ph[2])
                + puff * max(0.0, 1 - ((x - xc) / hw) ** 2))
    nx, ny = 26, 30
    V = np.zeros((nx, ny, 3))
    for i, x in enumerate(np.linspace(x0, x1, nx)):
        for j, y in enumerate(np.linspace(y0, y1, ny)):
            V[i, j] = (x, y, z_top + wob(x, y))
    add(inst, grid_tris(V), m)

    def skirt(along, fixed, sign, lo, hi):
        nu, nv = 30, 9
        V = np.zeros((nu, nv, 3))
        for i, u in enumerate(np.linspace(lo, hi, nu)):
            fold = 0.010 * math.sin(u * 14 + ph[3]) + 0.004 * math.sin(u * 31 + ph[4])
            for j in range(nv):
                tt = j / (nv - 1)
                if tt < 0.4:
                    th = (tt / 0.4) * math.pi / 2
                    o, dz = r * math.sin(th), -r * (1 - math.cos(th))
                else:
                    q = (tt - 0.4) / 0.6
                    o, dz = r + fold * q, -r - (z_top - r - z_hem) * q
                w = wob(fixed, u) if along == 'y' else wob(u, fixed)
                if along == 'y':
                    V[i, j] = (fixed + sign * o, u, z_top + w * (1 - tt) + dz)
                else:
                    V[i, j] = (u, fixed + sign * o, z_top + w * (1 - tt) + dz)
        add(inst, grid_tris(V), m)
    if 'w' in sides:
        skirt('y', x0, -1, y0, y1)
    if 'e' in sides:
        skirt('y', x1, +1, y0, y1)
    if 's' in sides:
        skirt('x', y0, -1, x0, x1)
    if 'n' in sides:
        skirt('x', y1, +1, x0, x1)


def pillow(inst, c, size, tilt, m, yaw=0.0):
    """Puffy pillow: thick in the middle, pinched along the seam. size = (width, thickness, height); faces -y before yaw."""
    c = np.array(c, float)
    hw, t0, hh = size[0] / 2, size[1], size[2] / 2
    n = 18
    us = np.linspace(-1, 1, n)
    for sg in (1, -1):
        V = np.zeros((n, n, 3))
        for i, u in enumerate(us):
            for j, v in enumerate(us):
                th = t0 * 0.5 * max(0.0, (1 - abs(u) ** 3.5) * (1 - abs(v) ** 3.5)) ** 0.55 + 0.004
                corner = 1 - 0.06 * (abs(u) * abs(v)) ** 3
                V[i, j] = (u * hw * corner, sg * th, v * hh * corner)
        P, N = grid_tris(V)
        add(inst, xform((P, N), T(*c) @ R('z', yaw) @ R('x', tilt)), m)


# ------------------------------------------------------------------------------------------- toys (bottom at z=0)
def toy(kind):
    """Geometry parts [(PN, material)] of one small toy, centred on x=y=0, standing on z=0, about 0.10-0.15 m."""
    P = []
    a = P.append
    if kind == 'bauble_red' or kind == 'bauble_gold' or kind == 'bauble_green':
        m = {'bauble_red': 'toy_red', 'bauble_gold': 'gold', 'bauble_green': 'toy_green'}[kind]
        a((ellipsoid((0, 0, 0.058), (0.058, 0.058, 0.058), 10), m))
        a((lathe(rprof(0.015, 0.112, 0.128, 0.003, 2), 12), 'gold'))
        a((tube([(-0.009, 0, 0.127), (0, 0, 0.142), (0.009, 0, 0.127)], 0.0025, 6), 'gold'))
    elif kind == 'car':
        a((rbox((0, 0, 0.045), (0.17, 0.08, 0.045), 0.014, 3), 'toy_red'))
        a((rbox((-0.012, 0, 0.083), (0.085, 0.07, 0.042), 0.012, 3), 'toy_white'))
        for x in (-0.052, 0.052):
            for y in (-0.042, 0.042):
                a((wheel((x, y, 0.022), 0.022, 0.016), 'toy_black'))
    elif kind == 'sweet':
        a((ellipsoid((0, 0, 0.042), (0.052, 0.038, 0.038), 10), 'toy_mustard'))
        for sg in (1, -1):
            a((xform(lathe([(0.006, 0), (0.016, 0.012), (0.034, 0.036), (0.0, 0.037)], 10), T(sg * 0.045, 0, 0.042) @ R('y', sg * math.pi / 2)),
               'toy_mustard'))
        a((ellipsoid((0, -0.034, 0.042), (0.03, 0.006, 0.03), 8), 'toy_white'))
    elif kind in ('teddy', 'bunny'):
        m = 'plush' if kind == 'teddy' else 'plush_white'
        a((ellipsoid((0, 0, 0.048), (0.046, 0.040, 0.050), 9), m))
        a((ellipsoid((0, -0.004, 0.112), (0.036, 0.034, 0.034), 9), m))
        if kind == 'teddy':
            for sg in (1, -1):
                a((ellipsoid((sg * 0.028, 0, 0.142), (0.013, 0.008, 0.013), 6), m))
        else:
            for sg in (1, -1):
                a((xform(ellipsoid((0, 0, 0.0), (0.011, 0.007, 0.040), 7), T(sg * 0.015, 0.0, 0.172) @ R('y', sg * 0.18)), m))
        for sg in (1, -1):
            a((ellipsoid((sg * 0.046, -0.012, 0.062), (0.016, 0.016, 0.030), 7), m))
            a((ellipsoid((sg * 0.026, -0.024, 0.016), (0.018, 0.022, 0.016), 7), m))
            a((ellipsoid((sg * 0.012, -0.034, 0.122), (0.004, 0.003, 0.004), 5), 'toy_black'))
        a((ellipsoid((0, -0.036, 0.104), (0.013, 0.010, 0.010), 6), 'plush_light' if kind == 'teddy' else 'toy_sky'))
    elif kind == 'star':
        a((star_prism((0, 0, 0.075), 0.075, 0.032, 0.026), 'gold'))
    elif kind == 'star_wood':
        a((star_prism((0, 0, 0.075), 0.075, 0.034, 0.03), 'toy_wood'))
        a((tube([(0, 0, 0.15), (0, 0, 0.17)], 0.002, 5), 'toy_red'))
    elif kind == 'bell':
        a((lathe([(0, 0.004), (0.054, 0.004), (0.056, 0.012), (0.044, 0.032), (0.035, 0.072), (0.026, 0.094), (0.0, 0.099)], 18), 'gold'))
        a((ellipsoid((0, 0, 0.008), (0.012, 0.012, 0.012), 6), 'gold'))
        for sg in (1, -1):
            a((xform(ellipsoid((0, 0, 0), (0.026, 0.008, 0.014), 7), T(sg * 0.02, -0.01, 0.108) @ R('y', sg * 0.4)), 'toy_red'))
    elif kind == 'snowman':
        a((ellipsoid((0, 0, 0.038), (0.042, 0.042, 0.040), 9), 'toy_white'))
        a((ellipsoid((0, 0, 0.094), (0.029, 0.029, 0.028), 9), 'toy_white'))
        a((lathe(rprof(0.019, 0.116, 0.148, 0.003, 2), 14, (0, 0)), 'toy_black'))
        a((lathe(rprof(0.030, 0.114, 0.12, 0.002, 2), 14, (0, 0)), 'toy_black'))
        a((torus((0, 0), 0.026, 0.009, 0.072, 16, 6), 'toy_green'))
        a((xform(lathe([(0.006, 0), (0.0, 0.026)], 8), T(0, -0.026, 0.094) @ R('x', math.pi / 2)), 'toy_mustard'))
    elif kind == 'cane':
        pts = [(0.0, 0, 0.0), (0.0, 0, 0.11)] + [(0.025 - 0.025 * math.cos(math.pi * k / 8), 0, 0.11 + 0.025 * math.sin(math.pi * k / 8)) for k in range(1, 9)]
        pts.append((0.05, 0, 0.095))
        a((tube(pts, 0.009, 10), 'cane'))
    elif kind in ('gift_green', 'gift_red', 'gift_special'):
        body, rib = {'gift_green': ('toy_green', 'toy_white'), 'gift_red': ('toy_red', 'gold'),
                     'gift_special': ('toy_green', 'toy_red')}[kind]
        s = 0.12 if kind == 'gift_special' else 0.10
        a((rbox((0, 0, s / 2), (s, s, s), 0.006, 3), body))
        a((box(-0.011, -s / 2 - 0.002, 0, 0.011, s / 2 + 0.002, s + 0.002), rib))
        a((box(-s / 2 - 0.002, -0.011, 0, s / 2 + 0.002, 0.011, s + 0.002), rib))
        for sg in (1, -1):
            a((xform(ellipsoid((0, 0, 0), (0.024, 0.009, 0.016), 7), T(sg * 0.018, 0, s + 0.012) @ R('y', -sg * 0.5)), rib))
    elif kind == 'rocket':
        a((lathe([(0, 0.02), (0.028, 0.02), (0.031, 0.04), (0.031, 0.09), (0.0, 0.092)], 16), 'toy_white'))
        a((lathe([(0.0, 0.09), (0.0305, 0.09), (0.022, 0.115), (0.0, 0.142)], 16), 'toy_red'))
        for k in range(3):
            ang = 2 * math.pi * k / 3 + math.pi / 2
            a((xform(box(0.02, -0.003, 0.0, 0.05, 0.003, 0.05), R('z', ang)), 'toy_red'))
        a((xform(lathe(rprof(0.012, -0.003, 0.003, 0.002, 2), 12), T(0, -0.030, 0.068) @ R('x', math.pi / 2)), 'toy_sky'))
    elif kind == 'blocks':
        a((rbox((-0.03, 0, 0.034), (0.068, 0.068, 0.068), 0.006, 3), 'toy_blue'))
        a((xform(rbox((0, 0, 0), (0.058, 0.058, 0.058), 0.006, 3), T(-0.026, 0.004, 0.098) @ R('z', 0.35)), 'toy_mustard'))
        a((rbox((0.045, -0.006, 0.026), (0.052, 0.052, 0.052), 0.006, 3), 'toy_red'))
    elif kind == 'duck':
        a((ellipsoid((-0.008, 0, 0.036), (0.058, 0.042, 0.036), 10), 'toy_mustard'))
        a((ellipsoid((-0.05, 0, 0.058), (0.02, 0.018, 0.016), 7), 'toy_mustard'))
        a((ellipsoid((0.026, 0, 0.088), (0.028, 0.027, 0.028), 9), 'toy_mustard'))
        a((ellipsoid((0.056, 0, 0.083), (0.018, 0.013, 0.006), 7), 'toy_red'))
        for sg in (1, -1):
            a((ellipsoid((0.04, sg * 0.022, 0.098), (0.004, 0.003, 0.004), 5), 'toy_black'))
    elif kind == 'top':
        a((lathe([(0, 0.0), (0.006, 0.004), (0.052, 0.048), (0.05, 0.062), (0.014, 0.068), (0.0, 0.07)], 20), 'toy_red'))
        a((lathe([(0.0, 0.065), (0.008, 0.066), (0.007, 0.12), (0.0, 0.122)], 10), 'toy_wood'))
        a((torus((0, 0), 0.051, 0.004, 0.055, 20, 6), 'toy_white'))
    elif kind == 'minitree':
        a((lathe(rprof(0.026, 0.0, 0.03, 0.004, 2), 14), 'toy_white'))
        for k, (r, z0, z1) in enumerate(((0.05, 0.03, 0.085), (0.04, 0.065, 0.115), (0.028, 0.10, 0.145))):
            a((lathe([(0, z0), (r, z0), (0.0, z1)], 14), 'pine2'))
        a((star_prism((0, 0, 0.152), 0.014, 0.006, 0.006), 'gold'))
    elif kind == 'mitten':
        a((rbox((0, 0, 0.068), (0.072, 0.034, 0.10), 0.03, 3), 'knit_red'))
        a((xform(ellipsoid((0, 0, 0), (0.016, 0.014, 0.03), 7), T(0.042, 0, 0.07) @ R('y', 0.5)), 'knit_red'))
        a((rbox((0, 0, 0.012), (0.078, 0.04, 0.026), 0.012, 3), 'knit_white'))
    elif kind == 'drum':
        a((lathe(rprof(0.052, 0.0, 0.07, 0.004, 2), 20), 'toy_red'))
        for z in (0.004, 0.066):
            a((torus((0, 0), 0.053, 0.006, z, 20, 6), 'toy_white'))
        for k in range(8):
            ang = 2 * math.pi * k / 8
            a((tube([(0.054 * math.cos(ang), 0.054 * math.sin(ang), 0.008), (0.054 * math.cos(ang + 0.4), 0.054 * math.sin(ang + 0.4), 0.062)], 0.0018, 4), 'gold'))
        for sg in (1, -1):
            a((tube([(-0.05, sg * 0.02, 0.074), (0.05, -sg * 0.01, 0.10)], 0.004, 6), 'toy_wood'))
    elif kind == 'house':
        a((rbox((0, 0, 0.034), (0.11, 0.08, 0.068), 0.004, 3), 'toy_ginger'))
        a((xform(box(0.0, -0.048, 0.0, 0.075, 0.048, 0.008), T(0, 0, 0.102) @ R('y', 0.58)), 'toy_white'))
        a((xform(box(-0.075, -0.048, 0.0, 0.0, 0.048, 0.008), T(0, 0, 0.102) @ R('y', -0.58)), 'toy_white'))
        a((xform(box(-0.045, -0.04, 0.0, 0.045, 0.04, 0.04), T(0, 0, 0.066) @ R('y', math.pi / 4) @ S(0.55, 1, 0.55)), 'toy_ginger'))
        a((box(-0.014, -0.0415, 0.0, 0.014, -0.039, 0.036), 'toy_red'))
        for x in (-0.038, 0.038):
            a((box(x - 0.01, -0.0415, 0.03, x + 0.01, -0.039, 0.05), 'toy_white'))
    elif kind == 'yoyo':
        for y in (-0.016, 0.016):
            a((xform(lathe(rprof(0.05, -0.011, 0.011, 0.006, 3), 20), T(0, y, 0.052) @ R('x', math.pi / 2)), 'toy_blue'))
        a((xform(lathe(rprof(0.012, -0.006, 0.006, 0.002, 2), 10), T(0, 0, 0.052) @ R('x', math.pi / 2)), 'toy_white'))
        a((tube([(0, 0, 0.052), (0.02, 0, 0.11), (0.0, 0, 0.15)], 0.0018, 4), 'toy_white'))
    elif kind == 'sock':
        pts = [(0, 0, 0.15), (0, 0, 0.06)] + [(0.025 - 0.025 * math.cos(math.pi / 2 * k / 5), 0, 0.06 - 0.03 * math.sin(math.pi / 2 * k / 5)) for k in range(1, 6)]
        pts.append((0.065, 0, 0.03))
        a((tube(pts, 0.026, 12), 'knit_red'))
        a((tube([(0, 0, 0.17), (0, 0, 0.14)], 0.029, 12), 'knit_white'))
    elif kind == 'penguin':
        a((ellipsoid((0, 0, 0.06), (0.042, 0.04, 0.06), 10), 'toy_black'))
        a((ellipsoid((0, -0.018, 0.055), (0.032, 0.026, 0.048), 9), 'toy_white'))
        a((ellipsoid((0, -0.04, 0.09), (0.01, 0.012, 0.006), 6), 'toy_mustard'))
        for sg in (1, -1):
            a((ellipsoid((sg * 0.018, -0.022, 0.006), (0.016, 0.022, 0.006), 6), 'toy_mustard'))
            a((ellipsoid((sg * 0.04, 0, 0.06), (0.008, 0.02, 0.034), 6), 'toy_black'))
            a((ellipsoid((sg * 0.013, -0.038, 0.102), (0.004, 0.003, 0.004), 5), 'toy_white'))
    elif kind == 'train':
        a((xform(lathe(rprof(0.03, -0.045, 0.045, 0.006, 2), 16), T(0.025, 0, 0.055) @ R('y', math.pi / 2)), 'toy_green'))
        a((rbox((-0.045, 0, 0.06), (0.06, 0.07, 0.08), 0.008, 3), 'toy_red'))
        a((rbox((-0.045, 0, 0.104), (0.075, 0.08, 0.012), 0.004, 3), 'toy_black'))
        a((lathe(rprof(0.012, 0.08, 0.115, 0.003, 2), 10, (0.045, 0)), 'toy_black'))
        for x in (-0.05, 0.0, 0.045):
            for y in (-0.038, 0.038):
                a((wheel((x, y, 0.02), 0.02, 0.012), 'toy_black'))
    else:
        raise ValueError(kind)
    return P


# Advent order (bottom to top): neighbours differ in colour and silhouette; the last (top riser) holds the star.
ADVENT_TOYS = ['car', 'bauble_gold', 'duck', 'cane', 'blocks', 'bell', 'rocket', 'mitten', 'teddy', 'gift_red', 'yoyo',
               'minitree', 'sock', 'drum', 'sweet', 'train', 'bauble_red', 'star_wood', 'top', 'bunny', 'house',
               'bauble_green', 'gift_green', 'star']


def advent_drawers():
    """The 24 drawers: dicts with kind ('side' faces -x, 'riser' faces -y), column, row and the front rectangle."""
    out = []
    for i in range(NST):
        y0, y1 = SY0 + TD * i, SY0 + TD * (i + 1)
        for r in range(i + 1):
            out.append(dict(kind='side', col=i, row=r, y0=y0, y1=y1, z0=RZ * r, z1=RZ * (r + 1)))
        if i >= 3:
            out.append(dict(kind='riser', col=i, row=i, y0=y0, y1=y1, z0=RZ * i, z1=RZ * (i + 1)))
    out.sort(key=lambda d: (d['z0'], d['kind'] == 'riser', d['y0']))
    return out


DRAWERS = advent_drawers()
TEASE = next(k for k, d in enumerate(DRAWERS) if d['kind'] == 'side' and d['row'] == 0 and d['col'] == 2)


# ------------------------------------------------------------------------------------------- shell + outside
def build_shell():
    r = 'room'
    add(r, box(-0.2, -0.2, -0.25, W + 0.2, D + 0.2, -0.012), 'subfloor')
    add(r, box(-0.2, -0.2, H, W + 0.2, D + 0.2, H + 0.1), 'ceiling')
    add(r, box(-0.2, -0.2, -0.25, 0, D + 0.2, H + 0.1), 'wall')
    add(r, box(W, -0.2, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
    add(r, box(-0.2, -0.2, -0.25, W + 0.2, 0, H + 0.1), 'wall')
    # north wall with the window
    add(r, box(-0.2, D, -0.25, WX0, D + 0.2, H + 0.1), 'wall'); add(r, box(WX1, D, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
    add(r, box(WX0, D, -0.25, WX1, D + 0.2, WZ0), 'wall'); add(r, box(WX0, D, WZ1, WX1, D + 0.2, H + 0.1), 'wall')
    for b in (box(WX0, D, WZ0, WX0 + 0.006, D + 0.2, WZ1), box(WX1 - 0.006, D, WZ0, WX1, D + 0.2, WZ1), box(WX0, D, WZ1 - 0.006, WX1, D + 0.2, WZ1)):
        add(r, b, 'sill')
    add(r, box(WX0 - 0.03, D - 0.03, WZ0 - 0.02, WX1 + 0.03, D + 0.17, WZ0), 'sill')
    fy0, fy1 = D + 0.10, D + 0.14
    xm = (WX0 + WX1) / 2
    for b in (box(WX0, fy0, WZ0, WX0 + 0.05, fy1, WZ1), box(WX1 - 0.05, fy0, WZ0, WX1, fy1, WZ1), box(WX0, fy0, WZ1 - 0.05, WX1, fy1, WZ1),
              box(WX0, fy0, WZ0, WX1, fy1, WZ0 + 0.05), box(xm - 0.022, fy0, WZ0, xm + 0.022, fy1, WZ1)):
        add(r, b, 'winframe')
    for b in (box(0, 0, 0, 0.012, D, 0.07), box(0, 0, 0, W, 0.012, 0.07)):
        add(r, b, 'white_cab')
    for (x, y) in DL:
        add(r, lathe([(0.034, H - 0.002), (0.046, H - 0.002), (0.047, H - 0.010), (0.050, H - 0.012), (0.052, H)], 32, (x, y)), 'white_cab')
        disc(r, (x, y), 0.036, H - 0.003, H - 0.0005, 'led_off')
    edges = [-0.05, 0.55, 1.1, 1.65, 2.2, 2.7, D + 0.01]
    for k in range(6):
        add(f'floor{k}', box(0, edges[k], -0.012, W, edges[k + 1], 0.0), 'floor')


def build_outside():
    """Snowy view through the north window (camera-only emitters) and two layers of falling snow. Built facing east
    (x outward, as if the window were at x = 0) and turned to face north."""
    xc = (WX0 + WX1) / 2
    M = T(xc, D, 0) @ R('z', math.pi / 2)            # local (x out, y along) -> world (y out, -x along)
    ZO = 0.7

    def A(inst, PN, m):
        add(inst, xform(PN, M), m)
    o = 'out_day'
    A(o, box(6.0, -14, -6, 6.05, 14, 10), 'sky_day')
    A(o, box(0.4, -14, -3.2 + ZO, 6.0, 14, -2.2 + ZO), 'snow_day')
    hy0, hy1, hx = -2.6, 0.6, 4.4                  # a neighbour's house with a snowy gable roof
    add_h = lambda PN, m: A(o, PN, m)
    add_h(box(hx, hy0, -2.2 + ZO, hx + 0.3, hy1, 0.9 + ZO), 'house_day')
    ridge = 1.75 + ZO
    yc = (hy0 + hy1) / 2
    for sg in (1, -1):
        e = yc + sg * ((hy1 - hy0) / 2 + 0.2)
        P = np.array([[(hx - 0.2, e, 0.82 + ZO), (hx - 0.2, yc, ridge), (hx + 0.5, yc, ridge)],
                      [(hx - 0.2, e, 0.82 + ZO), (hx + 0.5, yc, ridge), (hx + 0.5, e, 0.82 + ZO)]])
        add_h((P, np.tile(np.array([-1.0, 0, 0]), (2, 3, 1))), 'snow_day')
    add_h(box(hx - 0.21, yc - 0.02, ridge - 0.02, hx + 0.5, yc + 0.02, ridge + 0.03), 'roof_day')
    for wy in (-1.9, -0.9, 0.0):
        add_h(box(hx - 0.01, wy - 0.18, -0.2 + ZO, hx, wy + 0.18, 0.35 + ZO), 'roof_day')
    rng = np.random.default_rng(21)
    for k in range(20):
        px, py = rng.uniform(1.9, 4.0), rng.uniform(-3.5, 3.5)
        if hy0 - 0.3 < py < hy1 + 0.3 and px > 3.6:
            continue
        h = rng.uniform(2.6, 4.2)
        base = -2.4 + ZO
        r0 = h * 0.24
        for tier in range(4):
            z0 = base + h * (0.18 + 0.2 * tier)
            rr = r0 * (1 - 0.22 * tier)
            A(o, lathe([(0, z0), (rr, z0), (rr * 0.25, z0 + h * 0.3), (0, z0 + h * 0.31)], 10, (px, py)), 'pineo_day')
            A(o, lathe([(0, z0 + h * 0.10), (rr * 0.7, z0 + h * 0.10 + 0.02), (rr * 0.22, z0 + h * 0.30), (0, z0 + h * 0.312)], 10,
                       (px - 0.03, py)), 'snow_day')
    rng = np.random.default_rng(3)
    for k, (x0, x1, rmin, rmax) in enumerate(((0.6, 1.3, 0.013, 0.019), (1.3, 2.7, 0.017, 0.022))):
        ztop = 4.2 + SNOW_V[k] * DUR_LONG + 0.5
        n = int(48 * (ztop + 0.2) * (x1 - x0) * 4.0 / (1.0 + 1.5 * k))
        for i in range(n):
            c = (rng.uniform(x0, x1), rng.uniform(-2.0, 2.0), rng.uniform(0.0, ztop))
            rr = rng.uniform(rmin, rmax)
            A(f'snow{k}', ellipsoid(c, (rr, rr, rr), 3), 'flake')


# ------------------------------------------------------------------------------------------- loft + den (north)
def build_loft(rng):
    for x in (0.0, 2.04):
        add('loft_posts', box(x, LY0, 0.0, x + 0.06, LY0 + 0.06, 1.80), 'oak_z')
    add('loft_deck', box(0.0, LY0, LZ0, W, D, LZ1), 'white_cab')
    add('loft_deck', box(0.0, LY0 - 0.004, LZ0 - 0.06, SX0, LY0 + 0.02, LZ1), 'oak_x')
    add('loft_deck', box(0.0, LY0, LZ0 - 0.06, W, LY0 + 0.06, LZ0), 'oak_x')
    rl = 'loft_rail'
    add(rl, box(0.06, LY0, 1.76, 2.04, LY0 + 0.045, 1.80), 'oak_x')
    for x in np.arange(0.12, 2.0, 0.11):
        add(rl, box(x, LY0 + 0.006, LZ1, x + 0.035, LY0 + 0.03, 1.76), 'oakl_z')
    add('loft_mat', rbox((1.16, (LY0 + 0.05 + D) / 2, LZ1 + 0.075), (1.70, D - LY0 - 0.10, 0.15), 0.04, 5), 'mattress')
    zt = LZ1 + 0.15
    cloth('loft_duvet', 0.62, 2.02, LY0 + 0.07, D - 0.06, zt + 0.04, zt - 0.08, 0.04, 'duvet_gold', 5, sides=('s', 'e'))
    pillow('loft_pil', (0.50, 2.62, zt + 0.12), (0.62, 0.13, 0.32), -0.22, 'linen_grey', yaw=math.pi / 2)
    cloth('loft_throw', 1.45, 1.85, LY0 + 0.05, D - 0.06, zt + 0.065, zt - 0.10, 0.035, 'green_knit', 8, sides=('s',), puff=0.004)
    # headboard cubby at the west end of the deck: books and a torch
    add('loft_cubby', box(0.0, LY0 + 0.05, LZ1, 0.28, D, LZ1 + 0.018), 'oak_x')
    add('loft_cubby', box(0.0, LY0 + 0.05, LZ1 + 0.30, 0.28, D, LZ1 + 0.318), 'oak_x')
    add('loft_cubby', box(0.262, LY0 + 0.05, LZ1, 0.28, D, LZ1 + 0.318), 'oak_z')
    y = LY0 + 0.12
    for m, th in (('bk_sky', 0.03), ('bk_red', 0.025), ('bk_white', 0.03), ('bk_mustard', 0.028), ('bk_green', 0.03)):
        add('loft_books', box(0.03, y, LZ1 + 0.018, 0.24, y + th, LZ1 + 0.018 + 0.2), m); y += th + 0.004
    add('loft_books', xform(lathe(rprof(0.02, -0.06, 0.06, 0.006, 2), 12), T(0.14, 2.75, LZ1 + 0.04) @ R('x', math.pi / 2)), 'toy_mustard')
    # fairy lights along the rail
    n = 18
    pts = []
    for k in range(n + 1):
        x = 0.08 + (1.96 - 0.08) * k / n
        sag = 0.045 * abs(math.sin(math.pi * (k % 3) / 3))
        pts.append((x, LY0 - 0.012, 1.79 - sag))
    add('garland', tube(pts, 0.003, 5), 'wire')
    for p in pts:
        add('garland', ellipsoid((p[0], p[1] - 0.004, p[2] - 0.022), (0.011, 0.011, 0.016), 6), 'bulb_off')
        add('garland_on', ellipsoid((p[0], p[1] - 0.004, p[2] - 0.022), (0.0125, 0.0125, 0.0175), 6), 'bulb_on')
    # slim tree on the landing
    tx, ty, tz = TREE
    tr = 'tree'
    add(tr, lathe([(0, tz), (0.10, tz), (0.115, tz + 0.18), (0.12, tz + 0.19), (0, tz + 0.19)], 20, (tx, ty)), 'basket')
    add(tr, tube([(tx, ty, tz + 0.16), (tx, ty, tz + 0.26)], 0.02, 8), 'toy_wood')
    tiers = 6
    for k in range(tiers):
        z0 = tz + 0.24 + k * 0.105
        rr = 0.17 * (1 - k / (tiers + 0.4)) + 0.025
        add(tr, lathe([(0, z0), (rr, z0), (rr * 0.9, z0 + 0.02), (rr * 0.3, z0 + 0.15), (0, z0 + 0.16)], 16, (tx, ty)), 'pine' if k % 2 else 'pine2')
    for k in range(9):
        zz = tz + 0.30 + rng.uniform(0, 0.52)
        rr = 0.17 * (1 - (zz - tz - 0.24) / (0.105 * (tiers + 0.4))) + 0.015
        a = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)
        add(tr, ellipsoid((tx + rr * math.cos(a), ty + rr * math.sin(a), zz), (0.017, 0.017, 0.017), 7), ('toy_red', 'gold', 'toy_white')[k % 3])
    ttop = tz + 0.24 + tiers * 0.105 + 0.07
    for k in range(26):
        u = k / 25
        zz = tz + 0.28 + u * 0.62
        rr = 0.17 * (1 - (zz - tz - 0.24) / (0.105 * (tiers + 0.4))) + 0.028
        a = -math.pi / 2 + u * 2 * math.pi * 3.0
        if math.sin(a) < 0.35:
            p = (tx + rr * math.cos(a), ty + rr * math.sin(a), zz)
            add('tree', ellipsoid(p, (0.008, 0.008, 0.010), 5), 'bulb_off')
            add('tree_on', ellipsoid(p, (0.0095, 0.0095, 0.0115), 5), 'bulb_on')
    add('star_on', star_prism((tx, ty - 0.02, ttop), 0.064, 0.027, 0.022), 'star_glow')
    return ttop


def build_den(rng):
    # under-landing cupboard (closed; white, oak knob)
    add('cupboard', box(SX0, LY0, 0.0, W, D, 0.05), 'plinth')
    add('cupboard', box(SX0, LY0, 0.05, W, D, LZ0), 'white_in')
    add('cupboard', box(SX0 - 0.018, LY0 + 0.02, 0.055, SX0, D - 0.01, LZ0 - 0.01), 'white_cab')
    add('cupboard', xform(lathe(rprof(0.016, 0, 0.02, 0.007, 3), 14), T(SX0 - 0.018, LY0 + 0.10, 0.70) @ R('y', -math.pi / 2)), 'oak_x')
    # desk against the north wall
    dx0, dx1, dy0, dz = 0.95, 1.98, 2.58, 0.66
    wood('desk', dx0, dy0, dz - 0.03, dx1, D, dz, 'oak')
    for x in (dx0, dx1 - 0.03):
        add('desk', box(x, dy0, 0.0, x + 0.03, D, dz - 0.03), 'white_cab')
    add('desk_dr', box(1.25, dy0 - 0.004, dz - 0.13, 1.75, dy0 + 0.014, dz - 0.035), 'oak_x')
    add('desk_dr', xform(lathe(rprof(0.013, 0, 0.016, 0.006, 3), 14), T(1.50, dy0 - 0.004, dz - 0.08) @ R('x', math.pi / 2)), 'oak_x')
    add('desk_dr', box(1.27, dy0 + 0.014, dz - 0.12, 1.73, D - 0.04, dz - 0.11), 'white_in')
    add('desk_drc', box(1.33, dy0 + 0.06, dz - 0.11, 1.55, dy0 + 0.34, dz - 0.098), 'bk_white')
    for q, m in enumerate(('toy_red', 'toy_blue', 'toy_mustard', 'toy_green')):
        add('desk_drc', tube([(1.58 + 0.03 * q, dy0 + 0.06, dz - 0.104), (1.58 + 0.03 * q, dy0 + 0.32, dz - 0.104)], 0.005, 6), m)
    # desk top things + lamp
    add('dstuff', box(1.10, 2.72, dz, 1.34, 2.96, dz + 0.012), 'bk_green')
    add('dstuff', lathe([(0, dz), (0.034, dz), (0.037, dz + 0.085), (0, dz + 0.085)], 16, (1.45, 2.95)), 'toy_sky')
    for q, m in enumerate(('toy_red', 'toy_mustard', 'toy_blue')):
        add('dstuff', tube([(1.44 + 0.01 * q, 2.95, dz + 0.03), (1.43 + 0.02 * q, 2.96, dz + 0.15)], 0.005, 6), m)
    lx, ly = 1.85, 2.98
    add('dlamp', lathe(rprof(0.055, dz, dz + 0.015, 0.005, 3), 22, (lx, ly)), 'toy_white')
    add('dlamp', tube([(lx, ly, dz + 0.01), (lx, ly, 1.00), (lx - 0.10, ly - 0.05, 1.07)], 0.007, 8), 'toy_white')
    add('dlamp', lathe([(0.012, 1.09), (0.04, 1.075), (0.066, 1.01), (0.068, 1.0)], 22, (lx - 0.11, ly - 0.06)), 'lampshade')
    add('dlamp_on', ellipsoid((lx - 0.11, ly - 0.06, 1.03), (0.02, 0.02, 0.02), 8), 'lamp_bulb')
    # kid's chair
    cx, cy = 1.45, 2.30
    for x in (cx - 0.16, cx + 0.16):
        for y2 in (cy - 0.16, cy + 0.16):
            add('chair', tube([(x, y2, 0.0), (x, y2, 0.38)], 0.014, 8), 'toy_white')
    add('chair', rbox((cx, cy, 0.39), (0.38, 0.38, 0.03), 0.01, 3), 'toy_white')
    add('chair', rbox((cx, cy, 0.42), (0.34, 0.34, 0.04), 0.018, 3), 'green')
    for x in (cx - 0.16, cx + 0.16):
        add('chair', tube([(x, cy - 0.17, 0.38), (x, cy - 0.17, 0.72)], 0.014, 8), 'toy_white')
    add('chair', rbox((cx, cy - 0.17, 0.64), (0.36, 0.03, 0.12), 0.012, 3), 'toy_white')
    # low cubby with four fabric bins (west of the desk)
    bx0, bx1, by0 = 0.06, 0.90, 2.70
    for b in (box(bx0, by0, 0.0, bx1, D, 0.02), box(bx0, by0, 0.30, bx1, D, 0.32), box(bx0, by0, 0.60, bx1, D, 0.62),
              box(bx0, by0, 0.0, bx0 + 0.02, D, 0.62), box(bx1 - 0.02, by0, 0.0, bx1, D, 0.62), box(0.47, by0, 0.0, 0.49, D, 0.62)):
        add('cubby', b, 'white_cab')
    bins = [(0.08, 0.02, 'linen_grey', 'teddy'), (0.49, 0.02, 'green', 'blocks'), (0.08, 0.32, 'linen', 'train'), (0.49, 0.32, 'linen_grey', 'bunny')]
    for j, (x0, z0, m, kind) in enumerate(bins):
        add(f'bin{j}', rbox((x0 + 0.195, by0 + 0.19, z0 + 0.125), (0.36, 0.34, 0.25), 0.03, 3), m)
        put(f'bin{j}', toy(kind), (x0 + 0.195, by0 + 0.19, z0 + 0.20), 1.25, 0.2 * j)
    put('cubby_top', toy('drum'), (0.30, 2.92, 0.62), 1.3, 0.0)
    put('cubby_top', toy('top'), (0.66, 2.92, 0.62), 1.3, 0.0)
    # book wall: two oak shelves on the north wall under the deck, books in a sweep of colour
    for z in (0.86, 1.10):
        wood('bshelf', 0.06, 2.88, z, 2.04, D, z + 0.02, 'oak')
    order = ['bk_red', 'bk_red', 'bk_mustard', 'bk_mustard', 'bk_white', 'bk_green', 'bk_green', 'bk_sky', 'bk_sky', 'bk_blue', 'bk_blue',
             'bk_grey', 'bk_white']
    for row, z in enumerate((0.88, 1.12)):
        x = 0.10
        k = 0
        while x < 1.98:
            g = min(4, int((x - 0.10) / (1.88 / 5)))
            th = rng.uniform(0.022, 0.036)
            hh = rng.uniform(0.15, 0.17)
            if x + th > 1.98:
                break
            m = order[min(len(order) - 1, int((x - 0.10) / 1.88 * len(order)))]
            add(f'books{g}', box(x, 2.92, z, x + th, D - 0.01, z + hh), m)
            x += th + 0.003
            k += 1
    add('rug', rbox((1.05, 1.25, 0.008), (1.5, 1.1, 0.016), 0.006, 3), 'rug')


# ------------------------------------------------------------------------------------------- the advent stair (east)
def build_stair():
    for i in range(NST):
        y0, y1 = SY0 + TD * i, SY0 + TD * (i + 1)
        zt = RZ * (i + 1)
        st = f'stc{i}'
        add(st, box(SX0 + 0.02, y0, 0.0, SX1, y1, zt - 0.025), 'white_in')
        add(st, box(SX0, y0, 0.0, SX0 + 0.02, y1, 0.012), 'white_in')
        add(st, box(SX0 - 0.014, y0 - 0.02, zt - 0.025, SX1, y1, zt), 'oak_y' if False else 'oak_x')   # tread with a nosing
        add(st, box(SX0, y1 - 0.004, 0.0, SX0 + 0.004, y1, zt - 0.025), 'white_cab')                   # thin divider lines
    for k, d in enumerate(DRAWERS):
        kind = ADVENT_TOYS[k]
        sc = 0.80
        if d['kind'] == 'side':
            yc = (d['y0'] + d['y1']) / 2
            add(f'af{k}', box(SX0, d['y0'] + GAP, d['z0'] + GAP, SX0 + 0.012, d['y1'] - GAP, d['z1'] - GAP), 'oakl_y')
            add(f'af{k}', box(SX0 + 0.012, d['y0'] + GAP + 0.003, d['z0'] + GAP, SX0 + 0.018, d['y1'] - GAP - 0.003, d['z1'] - GAP - 0.003), 'white_cab')
            add(f'af{k}', xform(lathe(rprof(0.012, 0, 0.016, 0.006, 3), 14), T(SX0, yc, d['z0'] + RZ * 0.6) @ R('y', -math.pi / 2)), 'knob')
            add(f'at{k}', box(SX0 + 0.018, d['y0'] + 0.012, d['z0'] + 0.02, SX0 + SDEP, d['y1'] - 0.012, d['z0'] + 0.03), 'white_in')
            for bb in (box(SX0 + 0.018, d['y0'] + 0.012, d['z0'] + 0.03, SX0 + SDEP, d['y0'] + 0.02, d['z0'] + 0.08),
                       box(SX0 + 0.018, d['y1'] - 0.02, d['z0'] + 0.03, SX0 + SDEP, d['y1'] - 0.012, d['z0'] + 0.08)):
                add(f'at{k}', bb, 'white_in')
            put(f'ay{k}', toy(kind), (SX0 + 0.13, yc, d['z0'] + 0.03), sc, -math.pi / 2)
        else:
            xc = (SX0 + SDEP + SX1) / 2
            add(f'af{k}', box(SX0 + SDEP + GAP, d['y0'], d['z0'] + GAP, SX1 - GAP, d['y0'] + 0.012, d['z1'] - GAP), 'oakl_x')
            add(f'af{k}', box(SX0 + SDEP + GAP + 0.003, d['y0'] + 0.012, d['z0'] + GAP, SX1 - GAP - 0.003, d['y0'] + 0.018, d['z1'] - GAP - 0.003), 'white_cab')
            add(f'af{k}', xform(lathe(rprof(0.012, 0, 0.016, 0.006, 3), 14), T(xc, d['y0'], d['z0'] + RZ * 0.6) @ R('x', math.pi / 2)), 'knob')
            add(f'at{k}', box(SX0 + SDEP + 0.012, d['y0'] + 0.018, d['z0'] + 0.02, SX1 - 0.012, d['y1'] - 0.01, d['z0'] + 0.03), 'white_in')
            put(f'ay{k}', toy(kind), (xc, d['y0'] + 0.12, d['z0'] + 0.03), sc * (1.15 if kind == 'star' else 1.0), 0.0)
    # oak guard on the open side of treads 4-6: two balusters and a rail that runs into the loft rail
    gx = SX0 + 0.014
    ya, za, yb, zb = SY0 + TD * 3.5, 1.70, LY0 + 0.01, 1.79          # handrail along the stair pitch into the loft rail
    for i in (3, 4):
        y = SY0 + TD * (i + 0.5)
        zt = RZ * (i + 1)
        ztop = za + (zb - za) * (y - ya) / (yb - ya)
        add('stair_guard', box(gx - 0.012, y - 0.012, zt, gx + 0.012, y + 0.012, ztop), 'oak_z')
    add('stair_guard', tube([(gx, ya - 0.06, za - 0.011), (gx, yb, zb)], 0.018, 10), 'oak_x')
    # tease glint (a small sparkle)
    d = DRAWERS[TEASE]
    add('glint', star_prism((SX0 - 0.20, (d['y0'] + d['y1']) / 2, d['z1'] + 0.04), 0.08, 0.016, 0.004, n=4), 'glint_glow')


def build():
    materials()
    rng = np.random.default_rng(5)
    build_shell()
    build_outside()
    TREE_TOP[0] = build_loft(rng)
    build_den(rng)
    build_stair()
    add('den_on', box(0.10, LY0 + 0.07, LZ0 - 0.002, 2.0, LY0 + 0.09, LZ0 - 0.0015), 'led')
    for (x, y) in DL:
        disc('dl_on', (x, y), 0.037, H - 0.005, H - 0.0035, 'dl_emis')
    KID[0] = fg.figure('kid', 'child', mat='kid_top', pose='stand', at=(2.36, SY0 + TD * 3.5, 0), floor=RZ * 3)


TREE_TOP = [LZ1 + 0.9]


# ------------------------------------------------------------------------------------------- camera
VFOV = 85.0


def P(x, y, z, yaw, pitch):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch)


SA = (P(0.20, 0.15, 2.10, 38.0, -18.0), P(0.50, 0.60, 1.60, 28.0, -9.0))       # high doorway corner, craning down
SB = (P(0.55, 1.05, 1.00, -12.0, 2.0), P(1.55, 1.35, 0.90, 10.0, 4.0))         # the den under the loft
SC = (P(1.10, 1.08, 0.62, 74.0, -7.0), P(1.02, 1.70, 1.05, 84.0, -9.0))        # tight push up the stair with the ripple
SC2 = (P(0.42, 1.30, 0.82, 84.0, -4.0), P(0.70, 1.46, 0.84, 88.0, -4.0))       # all 24 open: slow push, level
SD = (P(1.02, 0.66, 1.48, 44.0, 8.0), P(1.16, 0.82, 1.58, 39.0, 11.0))        # the child, the top drawer, the star, lights on
SE = (P(0.42, 0.46, 1.90, 33.0, -15.0), SA[0])                                  # final: drift back into the frame-1 pose
HOLDS_SHORT = [(0.0, 2.90, SA), (3.15, 5.20, SB), (5.42, 8.55, SC), (8.75, 10.75, SC2), (11.0, 12.75, SD), (13.02, DUR_SHORT, SE)]
HOLDS = HOLDS_SHORT

camera = hold_camera(HOLDS, VFOV, rest=REST)


# ------------------------------------------------------------------------------------------- lights (fixed slots)
LSKY = (12.4, 12.4, 12.4)
LSUN = (42000.0, 38500.0, 33000.0)
LFILL = (2.4, 2.4, 2.35)
LCEIL = (0.6, 0.6, 0.6)
LTREE = (40.0, 30.0, 17.0)
LGARL = (26.0, 21.0, 13.0)
LDEN = (30.0, 25.0, 18.0)
LDOWN = (380.0, 335.0, 265.0)
LLAMP = (70.0, 55.0, 35.0)


def lights(mats4, vis):
    off = (0.0, 0.0, 0.0)

    def k(L, on, f=1.0):
        return tuple(v * f for v in L) if on else off
    Ls = []
    Ls.append(rect_light((WX0, D + 0.16, WZ0), (WX1 - WX0, 0, 0), (0, 0, WZ1 - WZ0), LSKY, always=1))                  # 0 sky (-y)
    sc = np.array([(WX0 + WX1) / 2, D, (WZ0 + WZ1) / 2]) - SUN_DIR * 0.8
    Ls.append(spot_rect(tuple(sc), tuple(SUN_DIR), 0.04, LSUN, 0.0))                                                     # 1 sun
    Ls.append(rect_light((0.4, 0.005, 0.3), (0, 0, 1.9), (1.8, 0, 0), LFILL, always=1))                                 # 2 fill +y
    Ls.append(rect_light((0.4, 0.4, H - 0.004), (0, 1.6, 0), (1.6, 0, 0), LCEIL))                                       # 3 ceiling fill
    tc = mats4['tree'] @ np.array([TREE[0], TREE[1] - 0.25, TREE[2] + 0.5, 1.0])
    Ls.append(sphere_light(tuple(tc[:3]), 0.05, k(LTREE, vis.get('tree_on'))))                                          # 4 tree glow
    Ls.append(rect_light((0.08, LY0 - 0.03, 1.74), (1.88, 0, 0), (0, 0.02, 0), k(LGARL, vis.get('garland_on'))))        # 5 rail lights
    Ls.append(rect_light((0.10, LY0 + 0.07, LZ0 - 0.003), (0, 0.02, 0), (1.9, 0, 0), k(LDEN, vis.get('den_on'))))       # 6 den strip
    for (x, y) in DL:                                                                                                    # 7-8
        Ls.append(spot_rect((x, y, H - 0.006), (0, 0, -1), 0.05, k(LDOWN, vis.get('dl_on')), 4.0))
    Ls.append(sphere_light((1.74, 2.92, 1.03), 0.02, k(LLAMP, vis.get('dlamp_on'))))                                    # 9 desk lamp
    return Ls


SEPARATE = ['sky_day', 'snow_day', 'pineo_day', 'house_day', 'roof_day', 'flake', 'bulb_on', 'star_glow', 'led', 'dl_emis', 'lamp_bulb', 'glint_glow']
BLENDER = dict(
    exposure=-0.30,
    look='AgX - Medium High Contrast',
    translucent={'lampshade': 0.5},
    separate=SEPARATE,
    fill_lights=[2, 3],
    wood_scale=(55.0, 1.6),
    bake_px={'floor': 0.0015},
)


# ------------------------------------------------------------------------------------------- the drawer mechanism
def advent_fns(k, cycles, base):
    """Drawer k: the tray slides out, the front drops into a ledge, the toy hops onto the ledge. cycles = [(t_open,
    t_close, hop), ...]. Returns (front_fn, tray_fn, toy_fn)."""
    d = DRAWERS[k]
    side = d['kind'] == 'side'
    off = np.array([-SLIDE, 0, 0]) if side else np.array([0, -SLIDE, 0])
    if side:
        hinge = np.array([SX0, 0.0, d['z0'] + GAP])
        hop = np.array([-0.235, 0, 0.012])
        piv = np.array([SX0 + 0.13, (d['y0'] + d['y1']) / 2, d['z0'] + 0.03])
    else:
        hinge = np.array([0.0, d['y0'], d['z0'] + GAP])
        hop = np.array([0, -0.225, 0.012])
        piv = np.array([(SX0 + SDEP + SX1) / 2, d['y0'] + 0.12, d['z0'] + 0.03])

    def st(t):
        s = a = h = 0.0
        g = 0.12
        for cyc_ in cycles:
            to, tc, hp = cyc_[:3]
            if t < to:
                break
            g = cyc_[3] if len(cyc_) > 3 else 0.12
            if t < tc:
                s = eoc((t - to) / 0.08)
                a = eob(c01((t - to - 0.05) / 0.10), 0.6)
                h = eoc(c01((t - to - 0.13) / 0.16)) if hp else 0.0
            else:
                u = t - tc
                h = (1 - smooth(u / 0.10)) if hp else 0.0
                a = 1 - smooth((u - (0.07 if hp else 0.0)) / 0.08)
                s = 1 - smooth((u - (0.14 if hp else 0.07)) / 0.07)
        return s, a, h, g

    def B(t):
        return base(t)

    def front(t):
        M0, v = B(t)
        s, a, h, g = st(t)
        Rm = R('y', -a * math.pi / 2) if side else R('x', a * math.pi / 2)
        return M0 @ T(*(off * s)) @ about(hinge, Rm), v

    def tray(t):
        M0, v = B(t)
        s, a, h, g = st(t)
        return M0 @ T(*(off * s)), v

    def toyf(t):
        M0, v = B(t)
        s, a, h, g = st(t)
        lift = 0.06 * math.sin(math.pi * h)
        sc = 1 + g * h
        return M0 @ T(*(off * s)) @ T(*(hop * h + np.array([0, 0, lift]))) @ about(piv, S(sc, sc, sc)), v
    return front, tray, toyf


# ------------------------------------------------------------------------------------------- timeline
def timeline():
    tl = Timeline(rk, FPS)
    I = np.eye(4)
    hidden = lambda t: (I, False)
    kid = KID[0]
    if REST:
        for nm in ('tree_on', 'star_on', 'garland_on', 'dl_on', 'dlamp_on', 'den_on', 'glint'):
            tl.custom(nm, hidden)
        if REST_NIGHT:
            for nm in ('tree_on', 'star_on', 'garland_on', 'dl_on', 'dlamp_on', 'den_on'):
                tl.custom(nm, lambda t: (I, True))
        kid.animate(tl, visible=False)
        return tl
    if CUT == 'long':
        return timeline_long(tl)
    return timeline_short(tl)


def timeline_short(tl):
    I = np.eye(4)
    hidden = lambda t: (I, False)
    cen, ev = tl.cen, tl.ev
    drop, fly, slide, grow = tl.drop, tl.fly, tl.slide, tl.grow
    kid = KID[0]

    def appear(name, t_on, t_off=None):
        tl.custom(name, lambda t: (I, t >= t_on and (t_off is None or t < t_off)))

    for k in range(2):
        tl.custom(f'snow{k}', lambda t, k=k: (T(0.04 * math.sin(0.9 * t + k), 0, -SNOW_V[k] * t), True))

    # ================= S1 (0-2.9, high corner): planks, the stair lands (and teases one drawer), posts, deck, bed
    for k in range(6):
        t1 = 0.14 + 0.05 * (5 - k)
        drop(f'floor{k}', t1 - 0.14, t1, 0.24, 0.05, 0.3 + 0.03 * k, 'tick')
    for i in range(NST):
        drop(f'stc{i}', 0.16 + 0.07 * i, 0.32 + 0.07 * i, 0.55, 0.03, 0.55 + 0.05 * i, 'thud')
    T_TEASE = 1.02
    T_C = 5.70                                    # cascade start
    STEP = 0.12
    T_CL = T_C + STEP * 23 + 1.50                # all 24 open, held 1.5 s: the close starts at 9.96 s
    T_KID_OPEN = 11.70
    T_STAR0, T_STAR1 = 11.92, 12.16
    T_LIGHTS = 12.20
    for k, d in enumerate(DRAWERS):
        col = d['col']
        base = (lambda t, col=col: tl.anims[f'stc{col}'](t))
        cyc = []
        if k == TEASE:
            cyc.append((T_TEASE, T_TEASE + 0.52, True, 0.9))
        to = T_C + STEP * k
        tc = T_CL + 0.02 * (23 - k)
        cyc.append((to, tc, True))
        if k == 23:
            cyc.append((T_KID_OPEN, 12.45, False))
        f_front, f_tray, f_toy = advent_fns(k, cyc, base)
        tl.custom(f'af{k}', f_front); tl.custom(f'at{k}', f_tray)
        if k == 23:
            tx, ty, _ = TREE
            dest = np.array([tx, ty - 0.02, TREE_TOP[0] - 0.064 * 0.8]) - cen[f'ay{k}'] + np.array([0, 0, 0.0])

            def star(t, f_toy=f_toy, dest=dest):
                if t < T_STAR0:
                    return f_toy(t)
                M0, v = tl.anims['stc5'](t)
                u = c01((t - T_STAR0) / (T_STAR1 - T_STAR0))
                e = smooth(u)
                p = dest * e + np.array([0, 0, 0.25 * math.sin(math.pi * u)])
                sc = 1 + 0.6 * math.sin(math.pi * u)
                return M0 @ T(*p) @ about(cen['ay23'], R('y', 2 * math.pi * e) @ S(sc, sc, sc)), v
            tl.custom(f'ay{k}', star)
        else:
            tl.custom(f'ay{k}', f_toy)
        ev(to + 0.06, f'adv{k}', 0.26, 'tick')
        ev(tc + 0.02, f'advc{k}', 0.12, 'tick')
    ev(T_TEASE + 0.08, 'adv_tease', 0.35, 'tick'); ev(T_TEASE + 0.52 + 0.24, 'tease_shut', 0.45, 'thud')

    def glint(t):
        u = (t - T_TEASE - 0.22) / 0.34
        if u < 0 or u > 1:
            return I, False
        s = math.sin(math.pi * u)
        return about(cen['glint'], R('x', 0) @ S(s, s, s) @ np.eye(4)), True
    tl.custom('glint', glint)
    ev(T_CL + 0.02 * 23 + 0.22, 'all_shut', 0.9, 'thud')
    ev(9.15, 'sparkle', 0.45, 'chime')
    grow('loft_posts', 1.30, 1.48, 'z', (0, 0, 0), 0.8)
    drop('loft_deck', 1.50, 1.68, 0.45, 0.02, 0.9, 'thud')
    tl.custom('cupboard', lambda t: (tl.anims['loft_deck'](t)[0], t >= 1.50))
    slide('loft_rail', 1.74, 1.90, (0, -0.5, 0), 1.0, 0.5)
    drop('stair_guard', 1.88, 2.02, 0.35, 0.03, 0.45)
    drop('loft_mat', 1.94, 2.10, 0.35, 0.03, 0.6, 'thud')
    drop('loft_duvet', 2.16, 2.32, 0.30, 0.03, 0.45)
    drop('loft_pil', 2.30, 2.44, 0.25, 0.06, 0.3)
    grow('loft_throw', 2.40, 2.56, 'x', (1.45, 0, 0), 0.3)
    drop('tree', 2.50, 2.68, 0.40, 0.05, 0.5, 'thud')
    drop('garland', 2.66, 2.80, 0.22, 0.04, 0.3)
    drop('loft_cubby', 2.72, 2.86, 0.25, 0.03, 0.3)
    drop('loft_books', 2.82, 2.96, 0.22, 0.04, 0.25)

    # ================= S2 (3.2-5.2): the den: desk, chair, bins, book wall
    slide('desk', 3.24, 3.40, (0, 0.5, 0), 1.0, 0.7)
    fly('chair', 3.40, 3.58, (0.0, -0.6, 0.0), 0.05, 0.5, 'thud')
    drop('cubby', 3.52, 3.66, 0.35, 0.02, 0.5, 'thud')
    for j in range(4):
        drop(f'bin{j}', 3.66 + 0.08 * j, 3.82 + 0.08 * j, 0.35, 0.05, 0.3)
    drop('cubby_top', 4.00, 4.14, 0.25, 0.05, 0.3)
    deskb = lambda t: (tl.anims['desk'](t)[0], t >= 3.24)
    o0, c0 = 4.14, 4.62

    def ddr(t):
        M0, v = deskb(t)
        if t < o0:
            return M0, v
        if t < c0:
            return M0 @ T(0, -0.26 * eob((t - o0) / 0.10, 1.4), 0), v
        u = (t - c0) / 0.14
        return M0 @ T(0, -0.26 * (1 - smooth(u)), 0), v
    tl.custom('desk_dr', ddr)
    drop('desk_drc', 4.28, 4.42, 0.25, 0.04, 0.3, parent=ddr)
    ev(4.20, 'desk_open', 0.4, 'swish'); ev(4.78, 'desk_shut', 0.5, 'thud')
    drop('dstuff', 4.44, 4.58, 0.2, 0.04, 0.25)
    drop('dlamp', 4.52, 4.66, 0.25, 0.05, 0.3)
    tl.custom('dlamp_on', hidden)
    slide('bshelf', 4.62, 4.76, (0, 0.3, 0), 1.0, 0.35)
    for g in range(5):
        from_ = 4.80 + 0.07 * g
        tl.from_camera(f'books{g}', from_, from_ + 0.16, np.array(SB[1]['pos']), 0.3, 0.25, 'tick')
    grow('rug', 5.08, 5.26, 'y', (0, 0.7, 0), 0.35)

    # ================= S4 (11.0-12.6): the child climbs, opens the top drawer, the star flies to the tree, lights
    ys = lambda i: SY0 + TD * (i + 0.5)
    bend_reach = dict(sh_r=48, sh_r_out=4, elbow_r=6, sh_l=24, sh_l_out=10, elbow_l=24, spine=36, neck=14,
                      hip_l=20, hip_r=20, knee_l=14, knee_r=14)
    at_fn = lambda t: (2.38, ys(2) + (ys(3) - ys(2)) * smooth(c01((t - 11.10) / 0.50)), 0)
    floor_fn = lambda t: RZ * 3 + RZ * smooth(c01((t - 11.10) / 0.50))
    kid.animate(tl, pose=fg.track([(11.10, 'stand'), (11.30, 'step_up'), (11.58, 'stand'), (11.66, bend_reach), (11.90, bend_reach),
                                   (12.10, 'reach_up'), (12.70, 'reach_up'), (13.0, 'wave')]),
                at=at_fn, floor=floor_fn, pop=10.98, sound=0.4)
    ev(T_KID_OPEN + 0.08, 'top_open', 0.45, 'swish'); ev(T_STAR1, 'star_on_tree', 0.6, 'tick')
    ev(12.45 + 0.22, 'top_shut', 0.5, 'thud')
    tl.custom('tree_on', lambda t: (tl.anims['tree'](t)[0], t >= T_LIGHTS)); ev(T_LIGHTS, 'tree_on', 0.7, 'chime')
    tl.custom('star_on', lambda t: (tl.anims['tree'](t)[0], t >= T_LIGHTS))
    appear('garland_on', T_LIGHTS + 0.12)
    appear('den_on', T_LIGHTS + 0.26); ev(T_LIGHTS + 0.26, 'den_on', 0.45, 'chime')
    appear('dlamp_on', T_LIGHTS + 0.34)
    appear('dl_on', T_LIGHTS + 0.44); ev(T_LIGHTS + 0.44, 'down_on', 0.4, 'chime')
    return tl


def timeline_long(tl):
    raise NotImplementedError('long cut: see PLAN.md (built after the 15 s cut)')


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    timeline().export(DUR, camera, lights, out)
