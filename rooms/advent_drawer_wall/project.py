"""Advent drawer wall: a 10 m² kids' room that builds itself while snow falls outside. The hero is a floor-to-ceiling
wall of 24 light-oak drawers (4 x 6) beside a niche for a slim tree; a loft bed with stair drawers and a desk under
it on the west wall; a window seat with drawers under the snowy east window. White + light oak + forest green.
No on-screen text: no numbers or letters on the drawers (the days are told apart by position, rhythm and contents).

    ROOM_REST=1 python3 ../../pipeline/run.py project.py <workdir> probe 0.5,1.5,2.5,3.5,4.5     # finished room, stations
    python3 ../../pipeline/run.py project.py <workdir> preview                                     # code-renderer preview
    ROOM_CUT=long ...                                                                              # the long cut

Units: metres. x = east, y = north, z = up. Room x 0..W, y 0..D, z 0..H.
North wall: drawer wall + tree niche. West wall: loft bed, stair drawers, desk. East wall: window + window seat.
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

W, D, H = 3.4, 3.5, 2.7
FPS = 25
DUR_SHORT, DUR_LONG = 15.0, 45.0
DUR = 6.0 if REST else (DUR_LONG if CUT == 'long' else DUR_SHORT)

WY0, WY1, WZ0, WZ1 = 1.65, 2.75, 0.95, 2.30        # east window opening
FY = 3.12                                          # front plane of the drawer wall (unit y FY..D)
UX0 = 1.15                                         # drawer wall west edge (it runs to the east wall)
NX0, NX1 = 1.168, 1.70                             # tree niche
GX0, GX1 = 1.718, 3.382                            # drawer grid x
GZ0, GZ1 = 0.54, 2.12                              # drawer grid z
NCOL, NROW = 4, 6
CW, RH = (GX1 - GX0) / NCOL, (GZ1 - GZ0) / NROW
GAP = 0.006
OPEN = 0.22                                        # how far a drawer slides out
SPECIAL = (2, 0)                                   # (row, col) of the last drawer: opened by the child
LX1, LY0, LZ = 1.0, 1.40, 1.36                     # loft bed: x 0..LX1, y LY0..D, platform underside LZ
SEAT = (2.95, 1.55, 2.85, 0.44)                    # window seat front x, y0, y1, top z
DESK = (0.62, 1.95, 3.40, 0.72)                    # desk front x, y0, y1, top z
DL = [(1.7, 1.0), (2.75, 1.0), (1.7, 2.3), (2.75, 2.3)]
SUN_DIR = np.array([-0.70, -0.20, -0.62]) / np.linalg.norm([-0.70, -0.20, -0.62])
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


# Drawer contents by (row, col): neighbours differ in colour and silhouette; the special one is the child's drawer.
GRID_TOYS = [
    ['car', 'bauble_gold', 'teddy', 'cane'],
    ['bell', 'blocks', 'snowman', 'gift_red'],
    ['gift_special', 'duck', 'rocket', 'mitten'],
    ['minitree', 'sock', 'star', 'yoyo'],
    ['penguin', 'bauble_red', 'drum', 'bunny'],
    ['star_wood', 'train', 'house', 'top'],
]


# ------------------------------------------------------------------------------------------- shell + outside
def build_shell():
    r = 'room'
    add(r, box(-0.2, -0.2, -0.25, W + 0.2, D + 0.2, -0.012), 'subfloor')
    add(r, box(-0.2, -0.2, H, W + 0.2, D + 0.2, H + 0.1), 'ceiling')
    add(r, box(-0.2, -0.2, -0.25, 0, D + 0.2, H + 0.1), 'wall')
    add(r, box(-0.2, D, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
    add(r, box(-0.2, -0.2, -0.25, W + 0.2, 0, H + 0.1), 'wall')
    # east wall with window
    add(r, box(W, -0.2, -0.25, W + 0.2, WY0, H + 0.1), 'wall'); add(r, box(W, WY1, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
    add(r, box(W, WY0, -0.25, W + 0.2, WY1, WZ0), 'wall'); add(r, box(W, WY0, WZ1, W + 0.2, WY1, H + 0.1), 'wall')
    for b in (box(W, WY0, WZ0, W + 0.2, WY0 + 0.006, WZ1), box(W, WY1 - 0.006, WZ0, W + 0.2, WY1, WZ1), box(W, WY0, WZ1 - 0.006, W + 0.2, WY1, WZ1)):
        add(r, b, 'sill')
    add(r, box(W - 0.02, WY0 - 0.03, WZ0 - 0.02, W + 0.17, WY1 + 0.03, WZ0), 'sill')
    fx0, fx1 = W + 0.10, W + 0.14
    ym = (WY0 + WY1) / 2
    for b in (box(fx0, WY0, WZ0, fx1, WY0 + 0.05, WZ1), box(fx0, WY1 - 0.05, WZ0, fx1, WY1, WZ1), box(fx0, WY0, WZ1 - 0.05, fx1, WY1, WZ1),
              box(fx0, WY0, WZ0, fx1, WY1, WZ0 + 0.05), box(fx0, ym - 0.022, WZ0, fx1, ym + 0.022, WZ1),
              box(fx0, WY0, 1.62 - 0.02, fx1, WY1, 1.62 + 0.02)):
        add(r, b, 'winframe')
    # baseboards
    for b in (box(0, 0, 0, 0.012, D, 0.07), box(0, 0, 0, W, 0.012, 0.07), box(W - 0.012, 0, 0, W, D, 0.07)):
        add(r, b, 'white_cab')
    # downlights (off) in the ceiling
    for (x, y) in DL:
        add(r, lathe([(0.034, H - 0.002), (0.046, H - 0.002), (0.047, H - 0.010), (0.050, H - 0.012), (0.052, H)], 32, (x, y)), 'white_cab')
        disc(r, (x, y), 0.036, H - 0.003, H - 0.0005, 'led_off')
    # floor planks in six bands (land far to near: north to south)
    edges = [-0.05, 0.6, 1.2, 1.8, 2.4, 3.0, D + 0.01]
    for k in range(6):
        add(f'floor{k}', box(0, edges[k], -0.012, W, edges[k + 1], 0.0), 'floor')


def build_outside():
    """Snowy view through the east window, as camera-only emitters (day + dusk versions), and falling snow."""
    for sfx in ('day', 'dusk'):
        o = f'out_{sfx}'
        add(o, box(W + 6.0 + (0.02 if sfx == 'dusk' else 0), -12, -6, W + 6.05 + (0.02 if sfx == 'dusk' else 0), 16, 10), f'sky_{sfx}')
        add(o, box(W + 0.4, -12, -3.2, W + 6.0, 16, -2.2), f'snow_{sfx}')          # snowy ground far below (upper floor)
        # a neighbour's house: wall, snowy gable roof
        hy0, hy1, hx = 0.2, 3.6, W + 4.6
        add(o, box(hx, hy0, -2.2, hx + 0.3, hy1, 0.7), f'house_{sfx}')
        ridge = 1.55
        for sg in (1, -1):
            yc = (hy0 + hy1) / 2
            P = np.array([[(hx - 0.2, yc + sg * (hy1 - hy0) / 2 + sg * 0.2, 0.62), (hx - 0.2, yc, ridge), (hx + 0.5, yc, ridge)],
                          [(hx - 0.2, yc + sg * (hy1 - hy0) / 2 + sg * 0.2, 0.62), (hx + 0.5, yc, ridge), (hx + 0.5, yc + sg * (hy1 - hy0) / 2 + sg * 0.2, 0.62)]])
            Nn = np.tile(np.array([-1.0, 0, 0]), (2, 3, 1))
            add(o, (P, Nn), f'snow_{sfx}')
            add(o, box(hx - 0.21, yc + sg * 0.0 - 0.02, ridge - 0.02, hx + 0.5, yc + 0.02, ridge + 0.03), f'roof_day' if sfx == 'day' else 'house_dusk')
        for wy in (0.9, 2.1, 2.9):
            add(o, box(hx - 0.01, wy - 0.18, -0.4, hx, wy + 0.18, 0.15), 'win_dusk' if sfx == 'dusk' else 'roof_day')
        # snowy pines
        rng = np.random.default_rng(21)
        for k in range(22):
            px = W + rng.uniform(1.9, 4.0)
            py = rng.uniform(-2.0, 5.5)
            if 0.1 < py < 3.7 and px > W + 4.3:
                continue
            h = rng.uniform(2.6, 4.2)
            base = -2.4
            r0 = h * 0.24
            for tier in range(4):
                z0 = base + h * (0.18 + 0.2 * tier)
                rr = r0 * (1 - 0.22 * tier)
                add(o, lathe([(0, z0), (rr, z0), (rr * 0.25, z0 + h * 0.3), (0, z0 + h * 0.31)], 10, (px, py)), f'pineo_{sfx}')
                add(o, lathe([(0, z0 + h * 0.10), (rr * 0.7, z0 + h * 0.10 + 0.02), (rr * 0.22, z0 + h * 0.30), (0, z0 + h * 0.312)], 10,
                             (px - 0.03, py)), f'snow_{sfx}')
    # falling snow: two layers in tall columns that slide down (no wrap inside the clip)
    rng = np.random.default_rng(3)
    for k, (x0, x1, rmin, rmax) in enumerate(((W + 0.9, W + 1.6, 0.010, 0.016), (W + 1.6, W + 3.0, 0.008, 0.012))):
        ztop = 3.6 + SNOW_V[k] * DUR_LONG + 0.5
        n = int(70 * (ztop + 0.8) * (x1 - x0) * 5.0 / (1.0 + k))
        for i in range(n):
            c = (rng.uniform(x0, x1), rng.uniform(-0.6, 4.4), rng.uniform(-0.8, ztop))
            rr = rng.uniform(rmin, rmax)
            add(f'snow{k}', ellipsoid(c, (rr, rr, rr), 3), 'flake')


# ------------------------------------------------------------------------------------------- drawer wall (north)
def cell(r, c):
    x0 = GX0 + c * CW
    z0 = GZ0 + r * RH
    return x0, x0 + CW, z0, z0 + RH


def build_drawer_wall():
    t = 0.018
    b = 'dw_body'
    add(b, box(UX0, FY + 0.04, 0.0, W, D, 0.06), 'plinth')
    add(b, box(UX0, FY, 0.0, UX0 + t, D, H), 'white_cab')                       # west side panel
    add(b, box(W - t, FY, 0.06, W, D, H), 'white_cab')                          # east side (against the wall)
    add(b, box(UX0, D - 0.012, 0.06, W, D, H), 'white_in')                      # back
    add(b, box(NX1, FY, 0.06, GX0, D, H), 'white_cab')                          # niche / grid divider
    add(b, box(UX0, FY, H - 0.03, W, D, H), 'white_cab')                        # top
    add(b, box(GX0, FY, 0.06, W - t, D, 0.075), 'white_in')                     # bins floor
    for zb in [GZ0 + RH * k for k in range(NROW + 1)] + [GZ0 - 0.02]:
        add(b, box(GX0, FY, zb - 0.006, W - t, D - 0.012, zb + 0.006), 'white_in')
    for k in range(1, NCOL):
        xb = GX0 + CW * k
        add(b, box(xb - 0.006, FY, GZ0, xb + 0.006, D - 0.012, GZ1), 'white_in')
    # niche: oak-lined, floor plinth top at 0.075
    add(b, box(NX0, FY + 0.05, 0.06, NX1, D - 0.012, 0.075), 'oak_x')
    add(b, box(NX0, D - 0.03, 0.075, NX1, D - 0.012, 2.40), 'oak_z')
    add(b, box(NX0, FY, 2.40, NX1, D, 2.418), 'oak_x')
    add(b, box(NX0, FY, 2.418, NX1, FY + 0.018, H - 0.03), 'white_cab')         # fixed panel over the niche
    add(b, box(NX0 + 0.03, FY + 0.03, 2.392, NX1 - 0.03, FY + 0.05, 2.40), 'led_off')
    add(b, box(GX0 + 0.03, FY + 0.03, GZ1 + 0.012, GX1 - 0.03, FY + 0.05, GZ1 + 0.018), 'led_off')
    # 24 drawers: plain oak fronts, a small white knob, an open tray behind
    for r in range(NROW):
        for c in range(NCOL):
            x0, x1, z0, z1 = cell(r, c)
            nm = f'dr_{r}_{c}'
            add(nm, box(x0 + GAP, FY, z0 + GAP, x1 - GAP, FY + 0.018, z1 - GAP), 'oak_x')
            add(nm, xform(lathe(rprof(0.013, 0, 0.018, 0.006, 3), 14), T((x0 + x1) / 2, FY, z0 + RH * 0.6) @ R('x', math.pi / 2)), 'knob')
            add(nm, box(x0 + 0.02, FY + 0.018, z0 + 0.022, x1 - 0.02, FY + 0.30, z0 + 0.032), 'white_in')
            for bb in (box(x0 + 0.02, FY + 0.018, z0 + 0.032, x0 + 0.03, FY + 0.30, z0 + 0.11),
                       box(x1 - 0.03, FY + 0.018, z0 + 0.032, x1 - 0.02, FY + 0.30, z0 + 0.11),
                       box(x0 + 0.02, FY + 0.29, z0 + 0.032, x1 - 0.02, FY + 0.30, z0 + 0.11)):
                add(nm, bb, 'white_in')
            kind = GRID_TOYS[r][c]
            put(f'toy_{r}_{c}', toy(kind), ((x0 + x1) / 2, FY + 0.13, z0 + 0.032), 1.0, 0.0)
    # toy bins in the plinth zone (two wide drawers on castors)
    rng = np.random.default_rng(4)
    for k, (x0, x1) in enumerate(((GX0, GX0 + 2 * CW), (GX0 + 2 * CW, GX1))):
        nm = f'bin{k}'
        z0, z1 = 0.08, GZ0 - 0.026
        add(nm, box(x0 + GAP, FY, z0, x1 - GAP, FY + 0.018, z1), 'oak_x')
        add(nm, box(x0 + 0.25, FY - 0.004, z1 - 0.09, x1 - 0.25, FY, z1 - 0.07), 'knob')
        add(nm, box(x0 + 0.03, FY + 0.018, z0 + 0.0, x1 - 0.03, FY + 0.33, z0 + 0.012), 'white_in')
        for bb in (box(x0 + 0.03, FY + 0.018, z0, x0 + 0.042, FY + 0.33, z1 - 0.06), box(x1 - 0.042, FY + 0.018, z0, x1 - 0.03, FY + 0.33, z1 - 0.06),
                   box(x0 + 0.03, FY + 0.318, z0, x1 - 0.03, FY + 0.33, z1 - 0.06)):
            add(nm, bb, 'white_in')
        cx = (x0 + x1) / 2
        if k == 0:
            put('binc0', toy('teddy'), (cx - 0.18, FY + 0.17, z0 + 0.012), 1.9, 0.3)
            put('binc0', toy('bunny'), (cx + 0.16, FY + 0.15, z0 + 0.012), 1.7, -0.3)
            put('binc1', toy('blocks'), (cx - 0.0, FY + 0.20, z0 + 0.012), 1.4, 0.5)
        else:
            put('binc2', toy('penguin'), (cx - 0.17, FY + 0.16, z0 + 0.012), 1.8, 0.2)
            add('binc2', ellipsoid((cx + 0.05, FY + 0.17, z0 + 0.012 + 0.075), (0.075, 0.075, 0.075), 10), 'toy_red')
            put('binc3', toy('train'), (cx + 0.22, FY + 0.15, z0 + 0.012), 1.5, 0.0)
            put('binc3', toy('drum'), (cx + 0.02, FY + 0.24, z0 + 0.012), 1.4, 0.0)
    # three lift-up flaps on top (white), gifts inside (long cut)
    for k, (x0, x1) in enumerate(((GX0, GX0 + 0.555), (GX0 + 0.555, GX0 + 1.11), (GX0 + 1.11, GX1))):
        nm = f'flap{k}'
        add(nm, box(x0 + GAP, FY, GZ1 + 0.03, x1 - GAP, FY + 0.018, H - 0.034), 'white_cab')
        add(nm, box((x0 + x1) / 2 - 0.08, FY - 0.012, GZ1 + 0.05, (x0 + x1) / 2 + 0.08, FY, GZ1 + 0.062), 'oak_x')
        for j in range(2):
            cx = x0 + (x1 - x0) * (0.3 + 0.4 * j)
            put(f'gifts{k}', toy('gift_green' if (j + k) % 2 else 'gift_red'), (cx, FY + 0.18, GZ1 + 0.03), 2.2, 0.2 * j)
    # slim tree in a white basket, baubles, string lights, star (slots into the niche)
    tx, ty = (NX0 + NX1) / 2, D - 0.21
    tr = 'tree'
    add(tr, lathe([(0, 0.075), (0.13, 0.075), (0.15, 0.30), (0.155, 0.31), (0, 0.31)], 22, (tx, ty)), 'basket')
    add(tr, tube([(tx, ty, 0.28), (tx, ty, 0.42)], 0.025, 8), 'toy_wood')
    tiers = 9
    for k in range(tiers):
        z0 = 0.40 + k * 0.17
        rr = 0.235 * (1 - k / (tiers + 0.6)) + 0.03
        prof = [(0, z0), (rr, z0 + 0.0), (rr * 0.92, z0 + 0.03), (rr * 0.35, z0 + 0.22), (0, z0 + 0.23)]
        add(tr, lathe(prof, 18, (tx, ty)), 'pine' if k % 2 else 'pine2')
    rng = np.random.default_rng(9)
    for k in range(16):
        zz = rng.uniform(0.50, 1.80)
        rr = 0.235 * (1 - (zz - 0.40) / (0.17 * (tiers + 0.6))) + 0.02
        a = rng.uniform(-math.pi * 0.95, -math.pi * 0.05)
        m = ('toy_red', 'gold', 'toy_white', 'toy_red')[k % 4]
        add(tr, ellipsoid((tx + rr * math.cos(a), ty + rr * math.sin(a), zz), (0.022, 0.022, 0.022), 7), m)
    lights_pts = []
    for k in range(34):
        u = k / 33
        zz = 0.48 + u * 1.42
        rr = 0.235 * (1 - (zz - 0.40) / (0.17 * (tiers + 0.6))) + 0.035
        a = -math.pi / 2 + u * 2 * math.pi * 3.3
        p = (tx + rr * math.cos(a), ty + rr * math.sin(a), zz)
        if math.sin(a) < 0.3:
            lights_pts.append(p)
    for p in lights_pts:
        add('tree_bulbs', ellipsoid(p, (0.009, 0.009, 0.011), 5), 'bulb_off')
        add('tree_on', ellipsoid(p, (0.0105, 0.0105, 0.0125), 5), 'bulb_on')
    add('star', star_prism((tx, ty - 0.02, 2.03), 0.075, 0.032, 0.022), 'gold')
    add('star_on', star_prism((tx, ty - 0.02, 2.03), 0.077, 0.033, 0.024), 'star_glow')


# ------------------------------------------------------------------------------------------- loft bed, stairs, desk (west)
def build_loft(rng):
    t = 0.05
    # posts and ledgers
    add('loft_posts', box(LX1 - t, LY0, 0.0, LX1, LY0 + t, 1.86), 'oak_z')
    add('loft_posts', box(LX1 - t, D - t, 0.0, LX1, D, 1.86), 'oak_z')
    # platform with an oak edge
    add('loft_plat', box(0.0, LY0, LZ, LX1, D, LZ + 0.06), 'white_cab')
    add('loft_plat', box(0.0, LY0, LZ - 0.10, LX1 - t, LY0 + 0.03, LZ), 'oak_x')
    add('loft_plat', box(LX1 - 0.03, LY0 + t, LZ - 0.10, LX1, D - t, LZ + 0.06), 'oak_y')
    # guard rail: top rail + slats on the room side, end rail at the head (north) and at the foot beside the stairs
    rl = 'loft_rail'
    add(rl, box(LX1 - 0.045, LY0 + 0.45, 1.80, LX1, D - t, 1.84), 'oak_y')
    for y in np.arange(LY0 + 0.47, D - 0.08, 0.11):
        add(rl, box(LX1 - 0.034, y, LZ + 0.06, LX1 - 0.012, y + 0.035, 1.80), 'oakl_z')
    add(rl, box(0.55, LY0, 1.80, LX1, LY0 + 0.04, 1.84), 'oak_x')
    add(rl, box(0.55, LY0, LZ + 0.06, 0.59, LY0 + 0.04, 1.80), 'oak_z')
    for x in np.arange(0.66, LX1 - 0.05, 0.11):
        add(rl, box(x, LY0 + 0.008, LZ + 0.06, x + 0.035, LY0 + 0.03, 1.80), 'oakl_z')
    # mattress and bedding
    add('loft_mat', rbox((0.49, (LY0 + 0.05 + D) / 2, LZ + 0.06 + 0.075), (0.88, D - LY0 - 0.10, 0.15), 0.04, 5), 'mattress')
    zt = LZ + 0.06 + 0.15
    cloth('loft_duvet', 0.05, 0.93, LY0 + 0.10, D - 0.50, zt + 0.04, zt - 0.08, 0.04, 'linen', 5, sides=('e', 's'))
    pillow('loft_pil', (0.49, D - 0.25, zt + 0.12), (0.62, 0.14, 0.36), -0.30, 'linen_grey')
    cloth('loft_throw', 0.05, 0.94, LY0 + 0.25, LY0 + 0.75, zt + 0.065, zt - 0.10, 0.035, 'green_knit', 8, sides=('e',), puff=0.004)
    # string-light garland on the top rail
    n = 18
    pts = []
    for k in range(n + 1):
        y = LY0 + 0.47 + (D - 0.08 - LY0 - 0.47) * k / n
        sag = 0.05 * abs(math.sin(math.pi * (k % 3) / 3))
        pts.append((LX1 + 0.012, y, 1.80 - 0.01 - sag))
    add('garland', tube(pts, 0.003, 5), 'wire')
    for p in pts[::1]:
        add('garland', ellipsoid((p[0] + 0.004, p[1], p[2] - 0.022), (0.011, 0.011, 0.016), 6), 'bulb_off')
        add('garland_on', ellipsoid((p[0] + 0.004, p[1], p[2] - 0.022), (0.0125, 0.0125, 0.0175), 6), 'bulb_on')


def build_stairs(rng):
    """Three steps up to the loft; each step is a stack of drawers facing east (+x)."""
    sx1 = 0.55
    steps = [(0.56, 0.84, 0.34), (0.84, 1.12, 0.68), (1.12, LY0, 1.02)]
    k = 0
    for i, (y0, y1, ztop) in enumerate(steps):
        st = f'step{i}'
        add(st, box(0.0, y0, 0.0, sx1, y1, 0.04), 'plinth')
        add(st, box(0.0, y0, 0.04, sx1, y0 + 0.018, ztop - 0.03), 'white_cab')
        add(st, box(0.0, y1 - 0.018, 0.04, sx1, y1, ztop - 0.03), 'white_cab')
        add(st, box(0.0, y0, 0.04, 0.02, y1, ztop - 0.03), 'white_in')
        wood(st, 0.0, y0 - 0.01, ztop - 0.03, sx1 + 0.01, y1, ztop, 'oak')
        for j in range(i + 1):
            z0 = 0.045 + j * 0.34
            z1 = z0 + 0.34 - 0.04
            nm = f'sd{k}'
            add(nm, box(sx1 - 0.018, y0 + 0.022, z0 + 0.004, sx1, y1 - 0.022, z1 - 0.004), 'oak_y')
            add(nm, box(sx1, (y0 + y1) / 2 - 0.06, z1 - 0.07, sx1 + 0.012, (y0 + y1) / 2 + 0.06, z1 - 0.058), 'knob')
            add(nm, box(0.05, y0 + 0.03, z0 + 0.01, sx1 - 0.018, y1 - 0.03, z0 + 0.022), 'white_in')
            for bb in (box(0.05, y0 + 0.03, z0 + 0.022, sx1 - 0.018, y0 + 0.042, z0 + 0.16), box(0.05, y1 - 0.042, z0 + 0.022, sx1 - 0.018, y1 - 0.03, z0 + 0.16),
                       box(0.05, y0 + 0.03, z0 + 0.022, 0.062, y1 - 0.03, z0 + 0.16)):
                add(nm, bb, 'white_in')
            yc, zb = (y0 + y1) / 2, z0 + 0.022
            cont = f'sdc{k}'
            if k == 0:      # slippers
                for dy in (-0.04, 0.04):
                    add(cont, ellipsoid((0.30, yc + dy, zb + 0.025), (0.11, 0.035, 0.025), 8), 'plush_white')
            elif k == 1:    # books on their sides
                zz = zb
                for m, hh in (('bk_green', 0.03), ('bk_mustard', 0.025), ('bk_sky', 0.03), ('bk_red', 0.022)):
                    add(cont, box(0.14, yc - 0.09, zz, 0.42, yc + 0.09, zz + hh), m); zz += hh
            elif k == 2:    # plush
                put(cont, toy('teddy'), (0.30, yc, zb), 1.6, math.pi / 2 + 0.3)
            elif k == 3:    # crayons in a cup
                add(cont, lathe([(0, zb), (0.04, zb), (0.044, zb + 0.09), (0, zb + 0.09)], 16, (0.30, yc)), 'toy_white')
                for q, m in enumerate(('toy_red', 'toy_blue', 'toy_mustard', 'toy_green', 'toy_sky', 'toy_red')):
                    ang = q * 1.05
                    add(cont, tube([(0.30 + 0.02 * math.cos(ang), yc + 0.02 * math.sin(ang), zb + 0.02),
                                    (0.30 + 0.03 * math.cos(ang), yc + 0.03 * math.sin(ang), zb + 0.16)], 0.006, 6), m)
            elif k == 4:    # blocks
                put(cont, toy('blocks'), (0.30, yc, zb), 1.4, 0.3)
            else:           # socks rolled
                for q, (dx, m) in enumerate(((-0.08, 'knit_red'), (0.0, 'knit_white'), (0.08, 'toy_sky'))):
                    add(cont, ellipsoid((0.30 + dx, yc, zb + 0.035), (0.035, 0.05, 0.035), 8), m)
            k += 1


def build_desk(rng):
    dx, dy0, dy1, dz = DESK
    wood('desk', 0.0, dy0, dz - 0.03, dx, dy1, dz, 'oak')
    add('desk', box(dx - 0.04, dy0, 0.0, dx - 0.01, dy0 + 0.03, dz - 0.03), 'white_cab')
    add('desk', box(dx - 0.04, dy1 - 0.03, 0.0, dx - 0.01, dy1, dz - 0.03), 'white_cab')
    # drawer under the desk top (faces east)
    add('desk_dr', box(dx - 0.018, 2.35, dz - 0.15, dx, 2.95, dz - 0.035), 'oak_y')
    add('desk_dr', box(dx, 2.6, dz - 0.08, dx + 0.012, 2.7, dz - 0.068), 'knob')
    add('desk_dr', box(0.08, 2.37, dz - 0.14, dx - 0.018, 2.93, dz - 0.13), 'white_in')
    add('desk_drc', box(0.25, 2.45, dz - 0.13, 0.48, 2.65, dz - 0.118), 'bk_sky')
    for q, m in enumerate(('toy_red', 'toy_blue', 'toy_mustard', 'toy_green')):
        add('desk_drc', tube([(0.2, 2.70 + 0.03 * q, dz - 0.122), (0.48, 2.70 + 0.03 * q, dz - 0.122)], 0.005, 6), m)
    # shelf on the wall above the desk (under the loft), books, a frame
    wood('dshelf', 0.0, 2.05, 1.06, 0.24, 3.38, 1.085, 'oak')
    y = 2.10
    for m, th, hh in (('bk_green', 0.03, 0.20), ('bk_white', 0.025, 0.22), ('bk_red', 0.035, 0.19), ('bk_sky', 0.03, 0.21),
                      ('bk_mustard', 0.028, 0.18), ('bk_white', 0.03, 0.2), ('bk_blue', 0.032, 0.21)):
        add('dbooks', box(0.04, y, 1.085, 0.21, y + th, 1.085 + hh), m); y += th + 0.004
    put('dbooks', toy('penguin'), (0.12, 2.75, 1.085), 1.3, math.pi / 2)
    put('dbooks', toy('minitree'), (0.12, 3.15, 1.085), 1.4, 0.0)
    # lamp
    lx, ly = 0.20, 3.20
    add('dlamp', lathe(rprof(0.06, dz, dz + 0.016, 0.005, 3), 24, (lx, ly)), 'toy_white')
    add('dlamp', tube([(lx, ly, dz + 0.01), (lx, ly, 1.02), (lx + 0.12, ly - 0.05, 1.10)], 0.007, 8), 'toy_white')
    add('dlamp', lathe([(0.012, 1.12), (0.04, 1.105), (0.07, 1.04), (0.072, 1.03)], 22, (lx + 0.13, ly - 0.06)), 'lampshade')
    add('dlamp_on', ellipsoid((lx + 0.13, ly - 0.06, 1.06), (0.02, 0.02, 0.02), 8), 'lamp_bulb')
    # notebook + pencil cup on the desk
    add('dstuff', box(0.18, 2.30, dz, 0.42, 2.62, dz + 0.012), 'bk_green')
    add('dstuff', lathe([(0, dz), (0.035, dz), (0.038, dz + 0.09), (0, dz + 0.09)], 16, (0.18, 2.82)), 'toy_sky')
    for q, m in enumerate(('toy_red', 'toy_mustard', 'toy_blue')):
        add('dstuff', tube([(0.18 + 0.012 * q - 0.012, 2.82, dz + 0.03), (0.18 + 0.02 * q - 0.02, 2.82 + 0.01, dz + 0.16)], 0.005, 6), m)
    # kid's chair (white frame, green seat pad), faces the desk (west)
    cx, cy = 0.82, 2.60
    for x in (cx - 0.16, cx + 0.16):
        for y2 in (cy - 0.16, cy + 0.16):
            add('chair', tube([(x, y2, 0.0), (x, y2, 0.40)], 0.014, 8), 'toy_white')
    add('chair', rbox((cx, cy, 0.41), (0.38, 0.38, 0.03), 0.01, 3), 'toy_white')
    add('chair', rbox((cx, cy, 0.44), (0.34, 0.34, 0.04), 0.018, 3), 'green')
    add('chair', tube([(cx + 0.17, cy - 0.16, 0.40), (cx + 0.17, cy - 0.16, 0.76)], 0.014, 8), 'toy_white')
    add('chair', tube([(cx + 0.17, cy + 0.16, 0.40), (cx + 0.17, cy + 0.16, 0.76)], 0.014, 8), 'toy_white')
    add('chair', rbox((cx + 0.17, cy, 0.68), (0.03, 0.36, 0.12), 0.012, 3), 'toy_white')


# ------------------------------------------------------------------------------------------- window seat (east)
def build_seat(rng):
    sx, sy0, sy1, sz = SEAT
    add('seat', box(sx, sy0, 0.0, W, sy1, 0.05), 'plinth')
    add('seat', box(sx, sy0, 0.05, W, sy0 + 0.018, sz - 0.03), 'white_cab')
    add('seat', box(sx, sy1 - 0.018, 0.05, W, sy1, sz - 0.03), 'white_cab')
    add('seat', box(sx, sy0, 0.05, W, sy1, 0.065), 'white_in')
    ym = (sy0 + sy1) / 2
    add('seat', box(sx, ym - 0.009, 0.05, W, ym + 0.009, sz - 0.03), 'white_in')
    wood('seat', sx - 0.02, sy0, sz - 0.03, W, sy1, sz, 'oak')
    for k, (y0, y1) in enumerate(((sy0 + 0.018, ym - 0.009), (ym + 0.009, sy1 - 0.018))):
        nm = f'seat_dr{k}'
        add(nm, box(sx, y0 + 0.004, 0.07, sx + 0.018, y1 - 0.004, sz - 0.035), 'oak_y')
        add(nm, box(sx - 0.012, (y0 + y1) / 2 - 0.10, sz - 0.11, sx, (y0 + y1) / 2 + 0.10, sz - 0.098), 'knob')
        add(nm, box(sx + 0.018, y0 + 0.02, 0.075, W - 0.03, y1 - 0.02, 0.087), 'white_in')
        for bb in (box(sx + 0.018, y0 + 0.02, 0.087, W - 0.03, y0 + 0.032, 0.30), box(sx + 0.018, y1 - 0.032, 0.087, W - 0.03, y1 - 0.02, 0.30),
                   box(W - 0.042, y0 + 0.02, 0.087, W - 0.03, y1 - 0.02, 0.30)):
            add(nm, bb, 'white_in')
        yc = (y0 + y1) / 2
        if k == 0:
            zz = 0.087
            for m, mm, hh in (('bk_blue', 'bk_white', 0.05), ('bk_red', 'bk_white', 0.045), ('bk_green', 'bk_mustard', 0.05)):
                add('seat_c0', box(3.02, yc - 0.20, zz, 3.30, yc + 0.20, zz + hh), m)
                add('seat_c0', box(3.05, yc - 0.12, zz + hh, 3.27, yc + 0.12, zz + hh + 0.002), mm)
                zz += hh + 0.003
        else:
            put('seat_c1', toy('train'), (3.16, yc - 0.12, 0.087), 1.8, math.pi / 2)
            put('seat_c1', toy('blocks'), (3.16, yc + 0.16, 0.087), 1.5, 0.4)
    # cushion, pillows, blanket
    add('seat_cush', rbox(((sx + W) / 2, ym, sz + 0.045), (W - sx - 0.02, sy1 - sy0 - 0.03, 0.09), 0.035, 5), 'green')
    pillow('seat_pil0', (3.30, sy0 + 0.25, sz + 0.27), (0.40, 0.13, 0.34), 0.0, 'linen', yaw=-math.pi / 2 + 0.35)
    pillow('seat_pil1', (3.30, sy1 - 0.25, sz + 0.25), (0.34, 0.12, 0.30), 0.0, 'linen_grey', yaw=-math.pi / 2 - 0.35)
    cloth('seat_throw', sx + 0.02, W - 0.02, ym - 0.18, ym + 0.12, sz + 0.105, sz - 0.05, 0.03, 'knit_white', 4, sides=('w',), puff=0.004)


def build():
    materials()
    rng = np.random.default_rng(5)
    build_shell()
    build_outside()
    build_drawer_wall()
    build_loft(rng)
    build_stairs(rng)
    build_desk(rng)
    build_seat(rng)
    add('rug', rbox((2.15, 1.55, 0.008), (1.7, 1.3, 0.016), 0.006, 3), 'rug')
    # light emitters that switch on
    add('cove_on', box(GX0 + 0.03, FY + 0.03, GZ1 + 0.011, GX1 - 0.03, FY + 0.05, GZ1 + 0.0115), 'led')
    add('niche_on', box(NX0 + 0.03, FY + 0.03, 2.3915, NX1 - 0.03, FY + 0.05, 2.392), 'led')
    for (x, y) in DL:
        disc('dl_on', (x, y), 0.037, H - 0.005, H - 0.0035, 'dl_emis')
    KID[0] = fg.figure('kid', 'child', pose='stand', at=(1.86, 2.50, 0))


# ------------------------------------------------------------------------------------------- camera
VFOV = 85.0


def P(x, y, z, yaw, pitch):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch)


SA = (P(1.05, 0.25, 1.45, 28.0, -5.0), P(1.15, 0.50, 1.42, 27.0, -6.0))         # hero corner: drawer wall + snowy window
SB = (P(2.45, 0.80, 1.38, -62.0, -6.0), P(2.30, 1.10, 1.36, -70.0, -6.0))       # loft, stair drawers, desk
SC = (P(1.30, 2.10, 1.30, 92.0, -8.0), P(1.66, 2.18, 1.28, 90.0, -6.0))         # window seat with snow
SD = (P(2.62, 1.12, 1.38, -5.0, 1.0), P(2.04, 1.22, 1.36, 5.0, 1.0))            # drawer wall close: lateral drift
SE = (P(1.30, 1.00, 1.50, 28.0, -6.0), SA[0])                                   # final: pull back into the frame-1 pose
HOLDS_SHORT = [(0.0, 3.40, SA), (3.70, 6.40, SB), (6.70, 8.60, SC), (8.90, 12.80, SD), (13.10, DUR_SHORT, SE)]
HOLDS = HOLDS_SHORT

camera = hold_camera(HOLDS, VFOV, rest=REST)


# ------------------------------------------------------------------------------------------- lights (fixed slots)
LSKY = (11.0, 11.4, 12.2)
LSKY_DUSK = (1.2, 1.5, 3.2)
LSUN = (30000.0, 27500.0, 23000.0)
LFILL = (2.2, 2.2, 2.15)
LCEIL = (0.55, 0.55, 0.55)
LCOVE = (60.0, 50.0, 36.0)
LNICHE = (40.0, 33.0, 24.0)
LTREE = (60.0, 46.0, 26.0)
LGARL = (30.0, 24.0, 15.0)
LDOWN = (420.0, 370.0, 290.0)
LLAMP = (90.0, 70.0, 44.0)


def lights(mats4, vis):
    off = (0.0, 0.0, 0.0)
    dusk = bool(vis.get('out_dusk'))

    def k(L, on, f=1.0):
        return tuple(v * f for v in L) if on else off
    Ls = []
    Ls.append(rect_light((W + 0.16, WY0, WZ0), (0, 0, WZ1 - WZ0), (0, WY1 - WY0, 0), LSKY_DUSK if dusk else LSKY, always=1))  # 0 sky
    sc = np.array([W, (WY0 + WY1) / 2, (WZ0 + WZ1) / 2]) - SUN_DIR * 0.8
    Ls.append(spot_rect(tuple(sc), tuple(SUN_DIR), 0.04, k(LSUN, not dusk), 0.0))                                           # 1 sun
    Ls.append(rect_light((0.9, 0.005, 0.3), (0, 0, 1.9), (1.8, 0, 0), k(LFILL, True, 0.15 if dusk else 1.0), always=1))       # 2 fill +y
    Ls.append(rect_light((1.2, 0.6, H - 0.004), (0, 2.2, 0), (1.8, 0, 0), k(LCEIL, True, 0.15 if dusk else 1.0)))           # 3 ceiling fill
    Ls.append(rect_light((GX0 + 0.03, FY + 0.03, GZ1 + 0.01), (0, 0.02, 0), (GX1 - GX0 - 0.06, 0, 0), k(LCOVE, vis.get('cove_on'))))  # 4
    Ls.append(rect_light((NX0 + 0.03, FY + 0.03, 2.39), (0, 0.02, 0), (NX1 - NX0 - 0.06, 0, 0), k(LNICHE, vis.get('niche_on'))))   # 5
    tc = mats4['tree'] @ np.array([(NX0 + NX1) / 2, D - 0.21 - 0.32, 1.15, 1.0])
    Ls.append(sphere_light(tuple(tc[:3]), 0.06, k(LTREE, vis.get('tree_on'))))                                              # 6 tree glow
    Ls.append(rect_light((LX1 + 0.02, LY0 + 0.47, 1.74), (0, D - 0.08 - LY0 - 0.47, 0), (0.02, 0, 0), k(LGARL, vis.get('garland_on'))))  # 7
    for (x, y) in DL:                                                                                                      # 8-11
        Ls.append(spot_rect((x, y, H - 0.006), (0, 0, -1), 0.05, k(LDOWN, vis.get('dl_on')), 4.0))
    Ls.append(sphere_light((0.33, 3.14, 1.06), 0.02, k(LLAMP, vis.get('dlamp_on'))))                                        # 12 desk lamp
    return Ls


# Blender (Cycles) look: see pipeline/blender_render.py
SEPARATE = ['sky_day', 'sky_dusk', 'snow_day', 'snow_dusk', 'pineo_day', 'pineo_dusk', 'house_day', 'house_dusk',
            'roof_day', 'win_dusk', 'flake']
BLENDER = dict(
    exposure=-0.30,
    look='AgX - Medium High Contrast',
    translucent={'lampshade': 0.5},
    separate=SEPARATE,
    fill_lights=[2, 3],
    wood_scale=(55.0, 1.6),
    bake_px={'floor': 0.0015},
)


# ------------------------------------------------------------------------------------------- timeline helpers
def make_helpers(tl):
    I = np.eye(4)
    ev = tl.ev

    def appear(name, t_on, t_off=None):
        tl.custom(name, lambda t: (I, t >= t_on and (t_off is None or t < t_off)))

    def door_x(name, hinge, a_open, t_in, t_in1, t_close, dur=0.17):
        """Lift-up flap (hinged on x) that pops in already open and swings shut."""
        hinge = np.array(hinge, float)

        def f(t):
            if t < t_in:
                return I, False
            if t < t_in1:
                u = (t - t_in) / (t_in1 - t_in)
                s = 1.12 - 0.12 * eoc(u)
                return T(0, 0, 0.10 * (1 - eoc(u))) @ about(hinge, R('x', a_open) @ S(s, s, s)), True
            if t < t_close:
                return about(hinge, R('x', a_open)), True
            u = (t - t_close) / dur
            if u < 1:
                return about(hinge, R('x', a_open * (1 - u * u))), True
            tau = t - t_close - dur
            a = math.copysign(math.radians(2.0), a_open) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))
            return about(hinge, R('x', a)), True
        tl.custom(name, f)
        ev(t_in1, name, 0.3, 'tick')
        ev(t_close + dur, name + '_shut', 0.7, 'thud')

    def drawer_multi(t_appear, cycles, off, base=None, out=0.10, shut=0.15):
        """A drawer that opens and closes several times: cycles = [(t_open, t_close), ...]."""
        off = np.array(off, float)
        nrm = off / (np.linalg.norm(off) + 1e-9)

        def f(t):
            if t < t_appear:
                return I, False
            B = base(t)[0] if base is not None else I
            k = 0.0
            for (to, tc) in cycles:
                if t < to:
                    break
                if t < tc:
                    k = eob((t - to) / out, 1.6)
                    break
                u = (t - tc) / shut
                if u < 1:
                    k = 1 - smooth(u)
                    break
                tau = t - tc - shut
                if tau < 0.3:
                    k = -0.025 * math.exp(-tau / 0.05) * math.sin(2 * math.pi * tau / 0.12)
            return B @ T(*(off * k)), True
        return f

    return appear, door_x, drawer_multi


def toy_hop(drawer_f, piv, hops, t_vis=0.0, rise=0.30, scale=1.25):
    """Toy that rides its drawer and hops up out of it: hops = [(t0, t_up, t_down, t1), ...]: rises t0..t_up, hovers
    (turning) until t_down, drops back until t1."""
    piv = np.array(piv, float)

    def f(t):
        B, v = drawer_f(t)
        if t < t_vis:
            return B, False
        h, s, yaw = 0.0, 1.0, 0.0
        for (t0, tu, td, t1) in hops:
            if t0 <= t < t1:
                if t < tu:
                    u = eob((t - t0) / (tu - t0), 1.4)
                    h, s = rise * u, 1 + (scale - 1) * u
                    yaw = -0.5 * u
                elif t < td:
                    w = (t - tu)
                    h = rise + 0.012 * math.sin(2 * math.pi * w / 0.5)
                    s = scale
                    yaw = -0.5 + 1.0 * smooth((t - tu) / max(td - tu, 1e-3))
                else:
                    u = (t - td) / (t1 - td)
                    h, s = rise * (1 - u * u), scale - (scale - 1) * smooth(u)
                    yaw = 0.5 * (1 - u)
                break
        M = T(0, 0, h) @ about(piv, R('z', yaw) @ S(s, s, s))
        return B @ M, v
    return f


# ------------------------------------------------------------------------------------------- timeline: 15 s cut
def timeline():
    tl = Timeline(rk, FPS)
    I = np.eye(4)
    hidden = lambda t: (I, False)
    kid = KID[0]
    if REST:
        if REST_NIGHT:
            for nm in ('out_day',):
                tl.custom(nm, hidden)
        else:
            for nm in ('out_dusk', 'cove_on', 'niche_on', 'tree_on', 'star_on', 'garland_on', 'dl_on', 'dlamp_on'):
                tl.custom(nm, hidden)
        kid.animate(tl, visible=False)
        return tl
    if CUT == 'long':
        return timeline_long(tl)
    return timeline_short(tl)


def wall_build(tl, t_rows, appear_t):
    """Drawer fronts fly in row by row (bottom to top); returns base functions per drawer."""
    I = np.eye(4)
    bases = {}
    for r in range(NROW):
        for c in range(NCOL):
            t0 = t_rows + 0.18 * r + 0.025 * c
            t1 = t0 + 0.16

            def base(t, t0=t0, t1=t1, r=r, c=c):
                if t < t0:
                    return I, False
                u = (t - t0) / (t1 - t0)
                if u < 1:
                    return T(0, -0.9 * (1 - eoc(u)), 0.06 * math.sin(math.pi * u)) @ about(tl.cen[f'dr_{r}_{c}'], S(*([0.6 + 0.4 * smooth(u / 0.4)] * 3))), True
                return I, True
            bases[(r, c)] = base
        tl.ev(t_rows + 0.18 * r + 0.16 + 0.04, f'row{r}', 0.35 + 0.05 * r, 'tick')
    return bases


def timeline_short(tl):
    I = np.eye(4)
    hidden = lambda t: (I, False)
    cen, ev = tl.cen, tl.ev
    drop, fly, slide, grow = tl.drop, tl.fly, tl.slide, tl.grow
    appear, door_x, drawer_multi = make_helpers(tl)
    kid = KID[0]

    # falling snow, always
    for k in range(2):
        tl.custom(f'snow{k}', lambda t, k=k: (T(0, 0.04 * math.sin(0.9 * t + k), -SNOW_V[k] * t), True))

    # ================= A (0.0-3.40, hero corner): floor, drawer wall, window seat, 24 fronts, toy bins
    for k in range(6):
        t1 = 0.24 + 0.06 * (5 - k)
        drop(f'floor{k}', t1 - 0.16, t1, 0.24, 0.05, 0.3 + 0.03 * k, 'tick')
    grow('dw_body', 0.56, 0.80, 'z', (0, 0, 0), 0.9)
    slide('seat', 0.84, 1.02, (0.7, 0, 0), 1.0, 0.7)
    bases = wall_build(tl, 1.08, 1.08)
    TB = 2.28
    for k in range(2):
        nm = f'bin{k}'
        t_in = TB + 0.06 * k

        def bbase(t, t_in=t_in):
            if t < t_in:
                return I, False
            u = (t - t_in) / 0.14
            return (T(0, -0.6 * (1 - eob(u, 1.0)), 0) if u < 1 else I), True
        fbin = drawer_multi(t_in, [(2.52 + 0.05 * k, 3.06 + 0.06 * k)], (0, -0.34, 0), base=bbase, out=0.14, shut=0.16)
        tl.custom(nm, fbin)
        if k == 0:
            drop('binc0', 2.62, 2.80, 0.45, 0.06, 0.4, parent=fbin)
            drop('binc1', 2.76, 2.92, 0.40, 0.06, 0.35, parent=fbin)
        else:
            drop('binc2', 2.70, 2.88, 0.45, 0.06, 0.4, parent=fbin)
            drop('binc3', 2.84, 3.00, 0.40, 0.06, 0.35, parent=fbin)
    ev(TB + 0.2, 'bins_in', 0.6, 'thud'); ev(2.58, 'bins_open', 0.5, 'swish'); ev(3.24, 'bins_shut', 0.8, 'thud')
    for k in range(3):
        door_x(f'flap{k}', (0, FY, H - 0.034), math.radians(-80), 3.0 + 0.05 * k, 3.12 + 0.05 * k, 3.18 + 0.05 * k, 0.14)
        tl.custom(f'gifts{k}', hidden)
    grow('rug', 3.20, 3.40, 'y', (0, 0.9, 0), 0.4)

    # ================= B (3.70-6.40): loft, stair drawers, desk
    grow('loft_posts', 3.72, 3.92, 'z', (0, 0, 0), 0.7)
    drop('loft_plat', 3.86, 4.04, 0.45, 0.02, 0.8, 'thud')
    slide('loft_rail', 4.08, 4.24, (0.5, 0, 0), 1.0, 0.5)
    drop('loft_mat', 4.22, 4.38, 0.35, 0.03, 0.5, 'thud')
    steps = []
    for i in range(3):
        steps.append(grow(f'step{i}', 4.36 + 0.13 * i, 4.52 + 0.13 * i, 'z', (0, 0, 0), 0.75))
    step_of = [0, 1, 1, 2, 2, 2]
    for k in range(6):
        to = 4.95 + 0.07 * k
        tc = 5.62 + 0.06 * k
        f = drawer_multi(4.36 + 0.13 * step_of[k], [(to, tc)], (0.30, 0, 0), base=steps[step_of[k]], out=0.12)
        tl.custom(f'sd{k}', f)
        drop(f'sdc{k}', to + 0.10, to + 0.26, 0.40, 0.05, 0.3, parent=f)
        ev(tc + 0.15, f'sd{k}_shut', 0.45, 'thud')
    ev(5.0, 'sd_open', 0.5, 'swish')
    drop('loft_duvet', 5.10, 5.28, 0.30, 0.03, 0.5, 'thud')
    drop('loft_pil', 5.30, 5.46, 0.25, 0.06, 0.3)
    slide('desk', 5.50, 5.66, (0.55, 0, 0), 1.0, 0.7)
    fdd = drawer_multi(5.50, [(6.00, 6.26)], (0.24, 0, 0), base=lambda t: (tl.anims['desk'](t)[0], t >= 5.50), out=0.10)
    tl.custom('desk_dr', fdd)
    drop('desk_drc', 6.06, 6.18, 0.2, 0.03, 0.25, parent=fdd)
    ev(6.43, 'desk_dr_shut', 0.5, 'thud')
    fly('chair', 5.70, 5.90, (0.6, -0.3, 0.0), 0.05, 0.6, 'thud')
    drop('dlamp', 5.80, 5.96, 0.3, 0.05, 0.35)
    tl.custom('dlamp_on', hidden)
    slide('dshelf', 5.88, 6.02, (0.3, 0, 0), 1.0, 0.3)
    drop('dbooks', 5.98, 6.14, 0.25, 0.04, 0.3)
    drop('dstuff', 6.10, 6.24, 0.22, 0.04, 0.3)
    drop('garland', 6.20, 6.36, 0.25, 0.04, 0.3)
    grow('loft_throw', 6.28, 6.48, 'y', (0, LY0, 0), 0.35)

    # ================= C (6.70-8.60): window seat drawers, cushion, pillows (snow outside)
    for k in range(2):
        f = drawer_multi(0.84, [(6.82 + 0.08 * k, 7.62 + 0.08 * k)], (-0.32, 0, 0), base=lambda t: (tl.anims['seat'](t)[0], t >= 0.84), out=0.12)
        tl.custom(f'seat_dr{k}', f)
        drop(f'seat_c{k}', 7.02 + 0.16 * k, 7.20 + 0.16 * k, 0.40, 0.05, 0.4, parent=f)
        ev(7.77 + 0.08 * k, f'seat_dr{k}_shut', 0.6, 'thud')
    ev(6.86, 'seat_open', 0.45, 'swish')
    drop('seat_cush', 7.96, 8.12, 0.30, 0.03, 0.55, 'thud')
    drop('seat_pil0', 8.14, 8.30, 0.30, 0.07, 0.3)
    drop('seat_pil1', 8.24, 8.40, 0.30, 0.07, 0.3)
    grow('seat_throw', 8.36, 8.56, 'y', (0, SEAT[1], 0), 0.3)

    # ================= D (8.90-12.80): tree slots in, the advent cascade, the child's drawer, slam
    slide('tree', 8.98, 9.24, (0, -1.1, 0.25), 0.9, 0.9)
    tl.custom('tree_bulbs', lambda t: (tl.anims['tree'](t)[0], t >= 8.98))
    drop('star', 9.30, 9.46, 0.30, 0.05, 0.4)
    TW = 9.60
    TS_OPEN, TS_SHUT = 12.14, 12.50
    special_open = 11.42
    for r in range(NROW):
        for c in range(NCOL):
            nm = f'dr_{r}_{c}'
            base = bases[(r, c)]
            d = r + c
            ts = TS_OPEN + 0.025 * d
            if (r, c) == SPECIAL:
                to = special_open
                cyc = [(to, 12.04), (ts, TS_SHUT)]
                hops = [(to + 0.06, to + 0.20, 11.88, 12.00)]
            else:
                p = 0 if r % 2 == 0 else 1
                to = TW + 0.75 * p + 0.07 * c
                cyc = [(to, to + 0.52), (ts, TS_SHUT)]
                hops = [(to + 0.06, to + 0.18, to + 0.38, to + 0.48)]
            f = drawer_multi(1.08, cyc, (0, -OPEN, 0), base=base, out=0.10, shut=0.14)
            tl.custom(nm, f)
            x0, x1, z0, z1 = cell(r, c)
            piv = ((x0 + x1) / 2, FY + 0.13, z0 + 0.032)
            tl.custom(f'toy_{r}_{c}', toy_hop(f, piv, hops, t_vis=1.08))
    for p in range(2):
        for c in range(NCOL):
            to = TW + 0.75 * p + 0.07 * c
            ev(to + 0.08, f'cas{p}{c}', 0.22, 'tick')
            ev(to + 0.52 + 0.14, f'cas{p}{c}_shut', 0.25, 'thud')
    # the child pops in, reaches, opens the last drawer
    reach = dict(sh_r=122, sh_r_out=6, elbow_r=12, sh_l=18, sh_l_out=10, elbow_l=20, spine=-4, neck=-16, ankle_l=-10, ankle_r=-10)
    kid.animate(tl, pose=fg.track([(11.05, 'stand'), (11.30, reach), (12.30, reach), (12.60, 'wave')]), at=(1.86, 2.50, 0),
                pop=10.92, sound=0.4)
    ev(special_open + 0.08, 'dr24_open', 0.45, 'swish'); ev(special_open + 0.20, 'dr24_pop', 0.5, 'chime')
    ev(TS_OPEN + 0.12, 'all_open', 0.5, 'swish'); ev(TS_SHUT + 0.14, 'all_shut', 1.0, 'thud')

    # ================= E (13.10-15.0): blue hour, lights cascade, held wide back to frame 1
    T_DUSK = 13.12
    appear('out_day', 0.0, T_DUSK)
    appear('out_dusk', T_DUSK)
    ev(T_DUSK, 'dusk', 0.45, 'swish')
    appear('garland_on', 13.32); ev(13.32, 'garland_on', 0.55, 'chime')
    tl.custom('tree_on', lambda t: (tl.anims['tree'](t)[0], t >= 13.50)); ev(13.50, 'tree_on', 0.6, 'chime')
    tl.custom('star_on', lambda t: (tl.anims['star'](t)[0], t >= 13.56))
    appear('niche_on', 13.56)
    appear('cove_on', 13.68); ev(13.68, 'cove_on', 0.5, 'chime')
    appear('dl_on', 13.84); ev(13.84, 'down_on', 0.5, 'chime')
    return tl


def timeline_long(tl):
    raise NotImplementedError('long cut: see PLAN.md (built after the 15 s cut)')


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    timeline().export(DUR, camera, lights, out)
