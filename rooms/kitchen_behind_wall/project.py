"""14 m² studio room-build: "The Kitchen Behind the Wall". A storage bed on the west wall, a birch wall of four bi-fold
panels on the north wall that folds away on frame 1, a kitchen that builds and fills behind it, a tall fridge + larder
return on the east wall, and a run that turns into a desk (lids over the hob and sink, a stool, a seated stand-in).
Neutral white shell, birch + light oak, one accent (pale sage stack-bond tile). No on-screen text.

    ROOM_REST=1 python3 pipeline/run.py rooms/kitchen_behind_wall/project.py <work> probe 0.5,1.5,2.5,3.5   # stations
    python3 pipeline/run.py rooms/kitchen_behind_wall/project.py <work> preview                             # preview + music
    ROOM_CUT=long ...                                                                                       # the 46 s cut

Units: metres. x = east, y = north, z = up. Room x 0..W, y 0..D, z 0..H.
North: kitchen enclosure y NY..D behind the panels (x 0.84..W), bathroom door in the recess x 0..0.80.
East: tall return (larder y 1.57-2.17, fridge 2.17-2.77, filler 2.77-2.85), window y 0.45-1.45.
South: entrance doorway x 1.50-2.40 (camera side). West: storage bed x 0..1.40, y 0..2.0.
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
LONG = os.environ.get('ROOM_CUT', '15') == 'long'

W, D, H = 4.0, 3.5, 2.7
FPS = 25
DUR_CUT = 46.0 if LONG else 15.0

NY = 2.85                                  # front plane of the kitchen enclosure (back face of the closed panels)
PX0, PW, PT, NP = 0.84, 0.64, 0.025, 4     # panel span starts at PX0, four panels 0.64 x 2.45 x 0.025
KX0 = 1.04                                 # kitchen interior starts here (pocket x 0.84-1.04)
FB = 2.88                                  # base unit front face
CT, CB = 0.90, 0.87                        # worktop top / bottom
UZ0, UZ1, UY = 1.45, 2.45, 3.15            # uppers bottom / top / front face
TX = 3.40                                  # tall return front face (doors x 3.40-3.42)
LAR = (1.57, 2.17)                         # larder y range
FRI = (2.17, 2.77)                         # fridge y range
WY0, WY1, WZ0, WZ1 = 0.45, 1.45, 0.95, 2.20
SUN_DIR = np.array([-0.74, 0.34, -0.56]) / np.linalg.norm([-0.74, 0.34, -0.56])
# x ranges of the run
XDW, XHOB, XSINK, XCOR = (1.04, 1.49), (1.49, 2.09), (2.09, 2.84), (2.84, 3.40)
STOOL_BED = (1.62, 1.78)                   # stool at the bed head (bedside table)
STOOL_DESK = (2.465, 2.30)                 # stool at the desk
SEAT = 0.65
CAPTIONS = []


# ------------------------------------------------------------------------------------------- materials
def materials():
    mat('subfloor', tex=3, col=srgb(150, 147, 142), p=(0.12,))
    mat('floor', tex=1, col=srgb(226, 206, 174), col2=srgb(212, 190, 156), rough=0.40, f0=0.04, glossy=True, p=(0.18, 1.6))
    mat('wall', tex=3, col=srgb(242, 241, 238), p=(0.012,))
    mat('ceiling', col=srgb(246, 246, 244))
    mat('white_cab', col=srgb(243, 242, 239), rough=0.42)
    mat('white_in', col=srgb(236, 235, 232))
    mat('plinth', col=srgb(214, 212, 208))
    wood_mats('oak', srgb(214, 188, 154), seed=3.0)
    wood_mats('birch', srgb(228, 208, 174), seed=8.0)
    mat('groove', col=srgb(170, 150, 120))
    mat('tile', tex=12, col=srgb(172, 190, 170), col2=srgb(226, 230, 222), rough=0.18, f0=0.04, glossy=True,
        p=(0.075, 0.30, 0.0035, 1, 0.0))
    mat('worktop', tex=15, col=srgb(222, 222, 220), col2=srgb(176, 176, 178), rough=0.18, f0=0.045, glossy=True, p=(700.0, 0.86))
    mat('steel', tex=14, col=srgb(206, 207, 211), rough=0.26, metal=1, p=(2,))
    mat('steel_x', tex=14, col=srgb(206, 207, 211), rough=0.30, metal=1, p=(0,))
    mat('basin', col=srgb(184, 186, 190), rough=0.28, f0=0.07, glossy=True)
    mat('drain', col=srgb(70, 70, 74), rough=0.3, metal=1)
    mat('hob', col=srgb(14, 14, 16), rough=0.05, f0=0.05, glossy=True)
    mat('hob_ring', col=srgb(86, 86, 90))
    mat('alu', col=srgb(200, 202, 206), rough=0.3, metal=1)
    mat('grille', tex=7, col=srgb(222, 220, 216), col2=srgb(150, 148, 144), p=(2, 0.018))
    mat('winframe', col=srgb(236, 236, 234), rough=0.4)
    mat('sill', col=srgb(240, 240, 238), rough=0.25, f0=0.04, glossy=True)
    mat('backdrop', tex=9, emis=(1.35, 1.35, 1.35), p=(1.0, 1.0))
    mat('led', col=(0, 0, 0), emis=(7.5, 7.1, 6.3))
    mat('led_off', col=srgb(230, 230, 228))
    mat('ceramic', col=srgb(244, 243, 240), rough=0.22, f0=0.04, glossy=True)
    mat('plate', col=srgb(246, 245, 242), rough=0.22, f0=0.04, glossy=True)
    mat('bowl_blue', col=srgb(104, 140, 186), rough=0.26, f0=0.04, glossy=True)
    mat('mug_sage', col=srgb(150, 176, 140), rough=0.3, f0=0.04, glossy=True)
    mat('mug_yel', col=srgb(238, 204, 92), rough=0.3, f0=0.04, glossy=True)
    mat('mug_blue', col=srgb(92, 132, 190), rough=0.3, f0=0.04, glossy=True)
    mat('jar', col=srgb(226, 230, 228), rough=0.12, f0=0.06, glossy=True)
    mat('cork', tex=3, col=srgb(198, 166, 126), p=(0.16,))
    mat('lemon', col=srgb(244, 206, 58), rough=0.4, f0=0.04, glossy=True)
    mat('apple', col=srgb(148, 190, 72), rough=0.35, f0=0.04, glossy=True)
    mat('pasta', tex=3, col=srgb(238, 200, 96), p=(0.25,))
    mat('peas', tex=3, col=srgb(132, 172, 82), p=(0.25,))
    mat('beans', tex=3, col=srgb(176, 58, 50), p=(0.3,))
    mat('flour', tex=3, col=srgb(244, 242, 236), p=(0.08,))
    mat('oats', tex=3, col=srgb(222, 204, 168), p=(0.2,))
    for nm, c in (('tin_blue', (62, 110, 178)), ('tin_green', (64, 140, 96)), ('tin_yel', (236, 192, 64)),
                  ('tin_red', (196, 66, 52)), ('teal', (84, 140, 136)), ('pot_blue', (92, 124, 168)),
                  ('bot_b', (64, 128, 196)), ('bot_g', (96, 168, 104)), ('bot_y', (236, 196, 70))):
        mat(nm, col=srgb(*c), rough=0.3, f0=0.04, glossy=True)
    mat('enamel', col=srgb(246, 244, 240), rough=0.22, f0=0.04, glossy=True)
    mat('linen', tex=3, col=srgb(242, 242, 240), rough=0.9, p=(0.035,))
    mat('mattress', tex=5, col=srgb(246, 246, 244), p=(0, 0.02))
    mat('pil_blue', tex=3, col=srgb(176, 198, 222), rough=0.9, p=(0.05,))
    mat('pil_white', tex=3, col=srgb(244, 244, 242), rough=0.9, p=(0.04,))
    mat('throw', tex=5, col=srgb(156, 178, 150), p=(0, 0.012))
    mat('leaf', col=srgb(64, 120, 62)); mat('leaf2', col=srgb(98, 150, 76))
    mat('laptop', col=srgb(214, 216, 220), rough=0.3, metal=1)
    mat('screen', col=srgb(30, 34, 40), rough=0.08, f0=0.05, glossy=True)
    mat('kb', tex=10, col=srgb(200, 202, 206), p=(0.018,))
    mat('lamp_sh', col=srgb(246, 244, 240), rough=0.5)
    mat('bulb', col=(0, 0, 0), emis=(9.0, 8.0, 6.4))
    mat('shade_glow', col=(0, 0, 0), emis=(2.4, 2.1, 1.6))
    mat('board', tex=2, col=srgb(214, 182, 142), p=(2, 6.0))
    mat('handle', col=srgb(206, 207, 211), rough=0.3, metal=1)
    for nm, c in (('cl_white', (242, 242, 240)), ('cl_sage', (150, 172, 142)), ('cl_blue', (104, 136, 182)),
                  ('cl_yel', (232, 200, 100)), ('cl_grey', (168, 170, 174)), ('cl_navy', (62, 78, 116))):
        mat(nm, tex=5, col=srgb(*c), p=(2, 0.008))
    for nm, c in (('bk_sage', (150, 172, 142)), ('bk_blue', (96, 130, 178)), ('bk_yel', (232, 196, 92)),
                  ('bk_white', (240, 238, 234)), ('bk_grey', (150, 152, 156)), ('bk_teal', (70, 140, 140))):
        mat(nm, col=srgb(*c), rough=0.6)
    mat('fig_denim', col=srgb(132, 148, 168), rough=0.48, f0=0.04)


# ------------------------------------------------------------------------------------------- helpers
def disc(inst, c, r, z0, z1, m, n=28):
    add(inst, lathe(rprof(r, z0, z1, min(0.004, (z1 - z0) * 0.45), 3), n, c), m)


def jar(inst, x, y, z, r, h, fill, lid='cork', frac=0.75):
    zf = z + h * frac                               # coloured contents up to zf, a pale band of glass above
    add(inst, lathe([(0, z), (r, z), (r + 0.003, z + 0.01), (r + 0.003, zf), (0, zf)], 22, (x, y)), fill)
    add(inst, lathe([(0, zf), (r + 0.003, zf), (r + 0.003, z + h), (r - 0.004, z + h + 0.004), (0, z + h + 0.004)], 22, (x, y)), 'jar')
    add(inst, lathe(rprof(r + 0.004, z + h, z + h + 0.025, 0.006, 3), 22, (x, y)), lid)


def tin(inst, x, y, z, r, h, m):
    add(inst, lathe([(0, z), (r, z), (r, z + h), (0, z + h)], 18, (x, y)), m)
    add(inst, lathe([(0, z + h), (r - 0.002, z + h), (r - 0.002, z + h + 0.006), (0, z + h + 0.006)], 18, (x, y)), 'steel')


def mug(inst, x, y, z, m, r=0.040, h=0.090, ang=0.0):
    prof = [(0, z), (r - 0.006, z), (r, z + 0.006), (r, z + h), (r - 0.005, z + h), (r - 0.005, z + 0.012), (0, z + 0.012)]
    add(inst, lathe(prof, 24, (x, y)), m)
    ca, sa = math.cos(ang), math.sin(ang)
    arc = [(x + ca * (r - 0.002 + 0.026 * math.sin(a)), y + sa * (r - 0.002 + 0.026 * math.sin(a)), z + h / 2 + 0.026 * math.cos(a))
           for a in np.linspace(0.2, math.pi - 0.2, 9)]
    add(inst, tube(arc, 0.0055, 8), m)


def bowl(inst, x, y, z, r, h, m):
    prof = [(0, z), (r * 0.55, z), (r * 0.88, z + h * 0.35), (r, z + h), (r - 0.006, z + h), (r * 0.84, z + h * 0.38),
            (r * 0.5, z + 0.008), (0, z + 0.008)]
    add(inst, lathe(prof, 28, (x, y)), m)


def plates(inst, x, y, z, r, n, m='plate'):
    for k in range(n):
        zz = z + k * 0.014
        add(inst, lathe([(0, zz), (r * 0.6, zz), (r, zz + 0.012), (r - 0.004, zz + 0.014), (r * 0.6, zz + 0.004), (0, zz + 0.004)], 32, (x, y)), m)


def pot(inst, x, y, z, r, h, m):
    add(inst, lathe([(0, z), (r - 0.01, z), (r, z + 0.012), (r, z + h), (r + 0.006, z + h + 0.004), (r - 0.004, z + h + 0.004),
                     (r - 0.006, z + 0.01), (0, z + 0.01)], 28, (x, y)), m)
    add(inst, lathe([(0, z + h + 0.004), (r + 0.004, z + h + 0.004), (r * 0.5, z + h + 0.03), (0.012, z + h + 0.034),
                     (0.012, z + h + 0.05), (0, z + h + 0.05)], 28, (x, y)), m)
    for sg in (-1, 1):
        add(inst, rbox((x + sg * (r + 0.02), y, z + h * 0.8), (0.04, 0.03, 0.015), 0.006, 3), m)


def stack(inst, cx, cy, z0, size, mats_, n, rng):
    z = z0
    for i in range(n):
        sx, sy, sz = size
        jx, jy = rng.uniform(-0.008, 0.008, 2)
        add(inst, rbox((cx + jx, cy + jy, z + sz / 2), (sx * rng.uniform(0.95, 1.0), sy * rng.uniform(0.95, 1.0), sz), sz * 0.45, 3),
            mats_[i % len(mats_)])
        z += sz * 0.96


def plant(inst, cx, cy, z0, r, h, rng, n=9, pot_m='ceramic'):
    add(inst, lathe([(0, z0), (r * 0.8, z0), (r, z0 + h), (r * 1.06, z0 + h + 0.006), (0, z0 + h + 0.006)], 20, (cx, cy)), pot_m)
    for k in range(n):
        a = 2 * math.pi * k / n + rng.uniform(-0.25, 0.25)
        lean = rng.uniform(0.3, 0.8)
        L = rng.uniform(0.07, 0.13) * (r / 0.05)
        c = np.array([cx + math.cos(a) * L * 0.4 * lean, cy + math.sin(a) * L * 0.4 * lean, z0 + h + L * 0.55])
        add(inst, xform(ellipsoid(c, (0.016, 0.016, L * 0.55), 7), about(c, R('z', a) @ R('x', lean * 0.6))), 'leaf' if k % 2 else 'leaf2')


def cloth(inst, x0, x1, y0, y1, z_top, z_hem, r, m, seed, sides=('w', 'e', 's'), puff=0.012):
    ph = np.random.default_rng(seed).uniform(0, 6.283, 5)
    xc, hw = (x0 + x1) / 2, (x1 - x0) / 2

    def wob(x, y):
        return (0.009 * math.sin(x * 9 + ph[0]) * math.sin(y * 5 + ph[1]) + 0.005 * math.sin(x * 17 + y * 11 + ph[2])
                + puff * max(0.0, 1 - ((x - xc) / hw) ** 2))
    nx, ny = 30, 30
    V = np.zeros((nx, ny, 3))
    for i, x in enumerate(np.linspace(x0, x1, nx)):
        for j, y in enumerate(np.linspace(y0, y1, ny)):
            V[i, j] = (x, y, z_top + wob(x, y))
    add(inst, grid_tris(V), m)

    def skirt(along, fixed, sign, lo, hi):
        nu, nv = 30, 11
        V = np.zeros((nu, nv, 3))
        for i, u in enumerate(np.linspace(lo, hi, nu)):
            fold = 0.011 * math.sin(u * 14 + ph[3]) + 0.005 * math.sin(u * 31 + ph[4])
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
        skirt('y', x0, -1, y0 - (r * 0.85 if 's' in sides else 0.0), y1)
    if 'e' in sides:
        skirt('y', x1, +1, y0 - (r * 0.85 if 's' in sides else 0.0), y1)
    if 's' in sides:
        skirt('x', y0, -1, x0 - r * 0.85, x1 + r * 0.85)


def pillow(inst, c, size, tilt, m):
    c = np.array(c, float)
    hw, t0, hh = size[0] / 2, size[1], size[2] / 2
    n = 22
    us = np.linspace(-1, 1, n)
    for sg in (1, -1):
        V = np.zeros((n, n, 3))
        for i, u in enumerate(us):
            for j, v in enumerate(us):
                th = t0 * 0.5 * max(0.0, (1 - abs(u) ** 3.5) * (1 - abs(v) ** 3.5)) ** 0.55 + 0.004
                corner = 1 - 0.06 * (abs(u) * abs(v)) ** 3
                V[i, j] = (u * hw * corner, sg * th, v * hh * corner)
        P, N = grid_tris(V)
        add(inst, xform((P, N), T(*c) @ R('x', tilt)), m)


def carcass(inst, x0, x1, y0, y1, z0, z1, t=0.018, m='white_in', back=True, top=True, bottom=True):
    """Open-front box (front at y0)."""
    add(inst, box(x0, y0, z0, x0 + t, y1, z1), m); add(inst, box(x1 - t, y0, z0, x1, y1, z1), m)
    e = 0.0005                                      # panels butt between the sides: no coplanar overlapping faces
    if back:
        add(inst, box(x0 + t + e, y1 - t, z0 + (t + e if bottom else 0), x1 - t - e, y1, z1 - (t + e if top else 0)), m)
    if bottom:
        add(inst, box(x0 + t + e, y0 + e, z0, x1 - t - e, y1 - (t + e if back else 0), z0 + t), m)
    if top:
        add(inst, box(x0 + t + e, y0 + e, z1 - t, x1 - t - e, y1 - (t + e if back else 0), z1), m)


# ------------------------------------------------------------------------------------------- shell
def build_shell():
    r = 'room'
    add(r, box(-0.2, -1.4, -0.25, W + 0.2, D + 0.2, -0.012), 'subfloor')
    add(r, box(0, -0.12, -0.012, W, D, 0.0), 'floor')
    add(r, box(1.50, -1.4, -0.012, 2.40, -0.12, 0.0), 'floor')
    add(r, box(-0.2, -1.4, H, W + 0.2, D + 0.2, H + 0.1), 'ceiling')
    add(r, box(-0.2, -1.4, -0.25, 0, D + 0.2, H + 0.1), 'wall')                                  # west
    add(r, box(-0.2, D, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')                               # north (behind the niche)
    # south wall with the entrance doorway (x 1.50-2.40) and a short corridor behind it
    add(r, box(-0.2, -0.12, -0.25, 1.50, 0, H + 0.1), 'wall'); add(r, box(2.40, -0.12, -0.25, W + 0.2, 0, H + 0.1), 'wall')
    add(r, box(1.50, -0.12, 2.10, 2.40, 0, H + 0.1), 'wall')
    add(r, box(1.30, -1.4, -0.25, 1.50, -0.12, H + 0.1), 'wall'); add(r, box(2.40, -1.4, -0.25, 2.60, -0.12, H + 0.1), 'wall')
    add(r, box(1.30, -1.6, -0.25, 2.60, -1.4, H + 0.1), 'wall')
    # east wall with window
    add(r, box(W, -0.2, -0.25, W + 0.2, WY0, H + 0.1), 'wall'); add(r, box(W, WY1, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
    add(r, box(W, WY0, -0.25, W + 0.2, WY1, WZ0), 'wall'); add(r, box(W, WY0, WZ1, W + 0.2, WY1, H + 0.1), 'wall')
    for b in (box(W, WY0, WZ0, W + 0.2, WY0 + 0.006, WZ1), box(W, WY1 - 0.006, WZ0, W + 0.2, WY1, WZ1), box(W, WY0, WZ1 - 0.006, W + 0.2, WY1, WZ1)):
        add(r, b, 'sill')
    add(r, box(W - 0.035, WY0 - 0.03, WZ0 - 0.02, W + 0.17, WY1 + 0.03, WZ0), 'sill')
    fx0, fx1 = W + 0.10, W + 0.13
    ym = (WY0 + WY1) / 2
    for b in (box(fx0, WY0, WZ0, fx1, WY0 + 0.04, WZ1), box(fx0, WY1 - 0.04, WZ0, fx1, WY1, WZ1), box(fx0, WY0, WZ1 - 0.04, fx1, WY1, WZ1),
              box(fx0, WY0, WZ0, fx1, WY1, WZ0 + 0.04), box(fx0, ym - 0.018, WZ0, fx1, ym + 0.018, WZ1)):
        add(r, b, 'winframe')
    add('bd_day', box(W + 4.0, -10, -5, W + 4.05, 14, 9), 'backdrop')
    # baseboards
    for b in (box(0, 0, 0, 0.012, D, 0.07), box(0, 0, 0, 1.50, 0.012, 0.07), box(2.40, 0, 0, W, 0.012, 0.07),
              box(W - 0.012, 0, 0, W, LAR[0], 0.07)):
        add(r, b, 'white_cab')
    # door casing of the entrance
    for b in (box(1.48, -0.02, 0, 1.50, 0.012, 2.12), box(2.40, -0.02, 0, 2.42, 0.012, 2.12), box(1.48, -0.02, 2.10, 2.42, 0.012, 2.12)):
        add(r, b, 'white_cab')
    # bathroom recess (x 0-0.80) with its door; enclosure end wall x 0.80-0.84
    add(r, box(0.80, NY, 0, 0.84, D, H), 'wall')
    add(r, box(0.05, D - 0.05, 0, 0.80, D - 0.02, 2.05), 'white_cab')
    for b in (box(0.03, D - 0.03, 0, 0.05, D, 2.07), box(0.03, D - 0.03, 2.05, 0.80, D, 2.07)):
        add(r, b, 'white_cab')
    add(r, tube([(0.70, D - 0.05, 1.02), (0.70, D - 0.09, 1.02), (0.60, D - 0.09, 1.02)], 0.009, 10), 'handle')
    # bulkhead over the panels and over the tall return (no slot in its face), top track
    add(r, box(PX0, NY - 0.03, UZ1, W, D, H), 'white_cab')
    add(r, box(TX, LAR[0], UZ1, W, NY, H), 'white_cab')
    add(r, box(PX0, NY - 0.026, UZ1 - 0.02, TX, NY - 0.004, UZ1), 'alu')
    # pocket partition (x 1.02-1.04) between the panel pocket and the dishwasher
    add(r, box(KX0 - 0.02, NY + 0.01, 0, KX0, D, UZ1), 'white_in')
    # tall return: carcass sides, filler, fridge (fixed door) with grilles, larder carcass
    add(r, box(TX + 0.02, LAR[0], 0, W, LAR[0] + 0.02, UZ1), 'white_cab')                       # south end panel
    add(r, box(TX, LAR[0] - 0.002, 0.0, TX + 0.02, LAR[0] + 0.02, UZ1), 'white_cab')
    add(r, box(TX, FRI[1], 0, W, NY, UZ1), 'white_cab')                                          # 80 mm filler
    add(r, box(TX + 0.05, LAR[0] + 0.02, 0, W, NY, 0.10), 'plinth')
    wood('fr_door', TX, FRI[0] + 0.002, 0.102, TX + 0.022, FRI[1] - 0.002, UZ1 - 0.10, 'birch')
    add('room', box(TX + 0.03, FRI[0], 0.005, TX + 0.05, FRI[1], 0.095), 'grille')            # plinth grille
    add('room', box(TX + 0.004, FRI[0] + 0.004, UZ1 - 0.096, TX + 0.022, FRI[1] - 0.004, UZ1 - 0.004), 'grille')
    fx0 = TX + 0.03
    add('room', box(fx0, FRI[0] + 0.004, 0.10, W, FRI[0] + 0.03, UZ1 - 0.10), 'white_in')      # fridge liner (open to -x)
    add('room', box(fx0, FRI[1] - 0.03, 0.10, W, FRI[1] - 0.004, UZ1 - 0.10), 'white_in')
    add('room', box(W - 0.03, FRI[0], 0.10, W, FRI[1], UZ1 - 0.10), 'white_in')
    add('room', box(fx0, FRI[0], 0.10, W, FRI[1], 0.13), 'white_in')
    add('room', box(fx0, FRI[0], UZ1 - 0.13, W, FRI[1], UZ1 - 0.10), 'white_in')
    for z in (0.52, 0.92, 1.32, 1.72):
        add('room', box(3.56, FRI[0] + 0.03, z, W - 0.03, FRI[1] - 0.03, z + 0.012), 'white_cab')
    add('room', box(3.60, FRI[0] + 0.05, 1.95, 3.64, FRI[1] - 0.05, 1.97), 'led')
    carcass('room', TX + 0.02, W, LAR[0] + 0.02, LAR[1], 0.10, UZ1, m='white_in', back=False)  # larder box (open to -x)
    add('room', box(W - 0.02, LAR[0] + 0.02, 0.10, W, LAR[1], UZ1), 'white_in')
    add('room', box(TX + 0.02, LAR[1] - 0.009, 0.10, W, LAR[1] + 0.009, UZ1), 'white_in')
    add('room', box(TX + 0.02, LAR[0] + 0.02, 0.10, W, LAR[1], 0.118), 'white_in')
    add('room', box(TX + 0.02, LAR[0] + 0.02, UZ1 - 0.018, W, LAR[1], UZ1), 'white_in')


# ------------------------------------------------------------------------------------------- the birch wall
def build_panels():
    for k in range(NP):
        x0 = PX0 + k * PW
        nm = f'pan{k}'
        wood(nm, x0 + 0.002, NY - PT, 0.012, x0 + PW - 0.002, NY, UZ1 - 0.024, 'birch')
        for g in (1, 2):                                                   # two shallow grooves per panel
            gx = x0 + PW * g / 3
            add(nm, box(gx - 0.0025, NY - PT - 0.0008, 0.012, gx + 0.0025, NY - PT + 0.002, UZ1 - 0.024), 'groove')
        add(nm, box(x0 + 0.006, NY - 0.004, UZ1 - 0.04, x0 + 0.03, NY + 0.004, UZ1 - 0.02), 'alu')   # roller


def panel_mats(theta, slide=0.0):
    """Transforms of the four panels for fold angle theta (0 flat .. pi/2 stacked) and a slide north into the pocket."""
    c, s = math.cos(theta), math.sin(theta)
    offs = (1, 1, 3, 3)
    out = []
    xs = PX0
    for k in range(NP):
        if k > 0:
            xs = PX0 + k * PW * c
        sx = xs + PT * s * offs[k]
        sy = NY if k % 2 == 0 else NY - PW * s
        rest = np.array([PX0 + k * PW, NY, 0.0])
        a = -theta if k % 2 == 0 else theta
        M = T(sx - rest[0], sy - rest[1] + slide, 0) @ about(rest, R('z', a))
        out.append(M)
    return out


# ------------------------------------------------------------------------------------------- kitchen
def build_tiles():
    n = 10
    xs = np.linspace(KX0, W, n + 1)
    for k in range(n):
        add(f'tile{k}', box(xs[k], D - 0.012, 0.0, xs[k + 1], D - 0.002, UZ1), 'tile')


def build_base(rng):
    t = 0.018
    yb = D - 0.012
    # dishwasher: oak integrated front
    nm = 'b_dw'
    add(nm, box(XDW[0] + 0.002, FB + 0.04, 0.0, XDW[1] - 0.002, yb, 0.10), 'plinth')
    carcass(nm, XDW[0] + 0.002, XDW[1] - 0.002, FB + 0.02, yb, 0.10, CB, m='white_in')
    add(nm, box(XDW[0] + 0.02, FB + 0.02, 0.12, XDW[1] - 0.02, yb - 0.02, CB - 0.03), 'steel')       # tub
    wood('dw_door', XDW[0] + 0.003, FB, 0.102, XDW[1] - 0.003, FB + 0.02, CB - 0.004, 'oak')
    add('dw_door', box(XDW[0] + 0.02, FB - 0.006, CB - 0.05, XDW[1] - 0.02, FB, CB - 0.035), 'groove')
    add('dw_door', box(XDW[0] + 0.02, FB + 0.02, 0.13, XDW[1] - 0.02, FB + 0.028, CB - 0.03), 'steel')
    for k, z in enumerate((0.16, 0.50)):
        nm2 = f'dw_rack{k}'
        x0r, x1r, y0r, y1r = XDW[0] + 0.035, XDW[1] - 0.035, FB + 0.05, yb - 0.04
        for b in (box(x0r, y0r, z, x1r, y1r, z + 0.008), box(x0r, y0r, z, x1r, y0r + 0.008, z + 0.07), box(x0r, y1r - 0.008, z, x1r, y1r, z + 0.07),
                  box(x0r, y0r, z, x0r + 0.008, y1r, z + 0.07), box(x1r - 0.008, y0r, z, x1r, y1r, z + 0.07)):
            add(nm2, b, 'alu')
        if k == 0:
            for i, yy in enumerate(np.linspace(y0r + 0.06, y1r - 0.06, 9)):
                M = T(XDW[0] + 0.225, yy, z + 0.13) @ R('x', math.pi / 2)
                add(nm2, xform(lathe([(0, -0.006), (0.10, -0.006), (0.115, 0.004), (0, 0.0)], 28, (0, 0)), M), 'plate' if i % 3 else 'bowl_blue')
        else:
            for i, xx in enumerate(np.linspace(x0r + 0.05, x1r - 0.05, 4)):
                for j, yy in enumerate(np.linspace(y0r + 0.06, y1r - 0.06, 4)):
                    add(nm2, lathe([(0, z + 0.008), (0.032, z + 0.008), (0.036, z + 0.11), (0, z + 0.11)], 18, (xx, yy)),
                        ('mug_sage', 'ceramic', 'mug_blue', 'mug_yel')[(i + j) % 4])
    # hob base: three drawers
    nm = 'b_hob'
    add(nm, box(XHOB[0] + 0.002, FB + 0.04, 0.0, XHOB[1] - 0.002, yb, 0.10), 'plinth')
    carcass(nm, XHOB[0] + 0.002, XHOB[1] - 0.002, FB + 0.02, yb, 0.10, CB)
    for (z0, z1) in ((0.102, 0.40), (0.40, 0.64), (0.64, CB - 0.004)):
        wood(nm, XHOB[0] + 0.003, FB, z0 + 0.0015, XHOB[1] - 0.003, FB + 0.02, z1 - 0.0015, 'oak')
        add(nm, box(XHOB[0] + 0.06, FB - 0.005, z1 - 0.03, XHOB[1] - 0.06, FB, z1 - 0.018), 'groove')
    # sink base: false front + deep U drawer
    nm = 'b_sink'
    add(nm, box(XSINK[0] + 0.002, FB + 0.04, 0.0, XSINK[1] - 0.002, yb, 0.10), 'plinth')
    carcass(nm, XSINK[0] + 0.002, XSINK[1] - 0.002, FB + 0.02, yb, 0.10, CB)
    for k, (z0, z1) in enumerate(((0.102, 0.66), (0.66, CB - 0.004))):
        n2 = 'sink_dr' if k == 0 else nm
        wood(n2, XSINK[0] + 0.003, FB, z0 + 0.0015, XSINK[1] - 0.003, FB + 0.02, z1 - 0.0015, 'oak')
        add(n2, box(XSINK[0] + 0.06, FB - 0.005, z1 - 0.03, XSINK[1] - 0.06, FB, z1 - 0.018), 'groove')
    ux0, ux1, uy0, uy1, uz = XSINK[0] + 0.03, XSINK[1] - 0.03, FB + 0.02, 3.40, 0.13
    for b in (box(ux0, uy0, uz, 2.36, uy1, uz + 0.012), box(2.58, uy0, uz, ux1, uy1, uz + 0.012), box(2.36, uy0, uz, 2.58, 3.08, uz + 0.012),
              box(ux0, uy0, uz, ux0 + 0.012, uy1, 0.56), box(ux1 - 0.012, uy0, uz, ux1, uy1, 0.56), box(2.348, 3.08, uz, 2.36, uy1, 0.50),
              box(2.58, 3.08, uz, 2.592, uy1, 0.50), box(2.36, 3.068, uz, 2.58, 3.08, 0.50), box(ux0, uy1 - 0.012, uz, 2.36, uy1, 0.50),
              box(2.58, uy1 - 0.012, uz, ux1, uy1, 0.50)):
        add('sink_dr', b, 'white_in')
    rngb = np.random.default_rng(9)
    for (xa, xb) in ((ux0 + 0.05, 2.30), (2.64, ux1 - 0.05)):
        for i, xx in enumerate(np.linspace(xa, xb, 2)):
            for j, yy in enumerate(np.linspace(uy0 + 0.07, uy1 - 0.07, 4)):
                h = rngb.uniform(0.20, 0.28)
                m = ('bot_b', 'bot_g', 'bot_y')[(i + j + (xa > 2.5)) % 3]
                add('sink_bot', lathe([(0, uz + 0.012), (0.036, uz + 0.012), (0.038, uz + h * 0.7), (0.016, uz + h * 0.85),
                                       (0.014, uz + h), (0, uz + h)], 18, (xx, yy)), m)
                add('sink_bot', lathe(rprof(0.016, uz + h, uz + h + 0.03, 0.004, 2), 14, (xx, yy)), 'ceramic')
    add('sink', tube([(2.47, 3.19, 0.70), (2.47, 3.19, 0.52), (2.47, 3.27, 0.46), (2.47, 3.34, 0.52), (2.47, 3.48, 0.52)], 0.022, 12), 'ceramic')
    # corner: blind-corner carcass x 2.84-4.0 behind the corner door
    nm = 'b_corner'
    add(nm, box(XCOR[0] + 0.002, FB + 0.04, 0.0, W, yb, 0.10), 'plinth')
    add(nm, box(XCOR[0] + 0.002, FB + 0.02, 0.10, XCOR[0] + 0.02, yb, CB), 'white_in')
    add(nm, box(XCOR[0] + 0.002, FB + 0.02, 0.10, W, yb, 0.118), 'white_in')
    add(nm, box(XCOR[0] + 0.002, FB + 0.02, CB - 0.018, W, yb, CB), 'white_in')
    add(nm, box(W - 0.02, FB + 0.02, 0.10, W, yb, CB), 'white_in')
    add(nm, box(XCOR[1], FB, 0.10, W, FB + 0.02, CB), 'white_in')                     # blind part of the front
    add(nm, box(XCOR[0] + 0.02, yb - 0.01, 0.10, W - 0.02, yb, CB), 'white_in')
    # corner door (hinged on its west edge) and the two kidney shelves with pots
    wood('cor_door', XCOR[0] + 0.003, FB, 0.102, XCOR[1] - 0.003, FB + 0.02, CB - 0.004, 'oak')
    add('cor_door', box(XCOR[1] - 0.04, FB - 0.006, CB - 0.05, XCOR[1] - 0.025, FB, CB - 0.035), 'groove')
    for k, z in enumerate((0.20, 0.50)):
        nm = f'cs{k}'
        add(nm, rbox((3.42, 3.18, z), (0.50, 0.46, 0.022), 0.02, 3), 'white_cab')
        add(nm, rbox((3.42, 2.96, z + 0.03), (0.50, 0.02, 0.05), 0.008, 3), 'alu')
        pn = f'pots{k}'
        if k == 0:
            pot(pn, 3.30, 3.18, z + 0.011, 0.095, 0.12, 'teal')
            pot(pn, 3.55, 3.20, z + 0.011, 0.085, 0.14, 'pot_blue')
        else:
            pot(pn, 3.30, 3.18, z + 0.011, 0.09, 0.10, 'pot_blue')
            pot(pn, 3.55, 3.20, z + 0.011, 0.08, 0.15, 'teal')
    # worktop with the sink cut-out
    sx0, sx1, sy0, sy1 = 2.22, 2.72, 3.00, 3.38
    for b in (box(KX0, 2.86, CB, sx0, D, CT), box(sx1, 2.86, CB, W, D, CT), box(sx0, 2.86, CB, sx1, sy0, CT), box(sx0, sy1, CB, sx1, D, CT)):
        add('worktop', b, 'worktop')
    # sink (undermount basin), tap
    zb = 0.70
    for b in (box(sx0, sy0, zb, sx1, sy1, zb + 0.01), box(sx0, sy0, zb, sx0 + 0.01, sy1, CB), box(sx1 - 0.01, sy0, zb, sx1, sy1, CB),
              box(sx0, sy0, zb, sx1, sy0 + 0.01, CB), box(sx0, sy1 - 0.01, zb, sx1, sy1, CB)):
        add('sink', b, 'basin')
    add('sink', lathe(rprof(0.034, zb + 0.010, zb + 0.013, 0.002, 2), 24, ((sx0 + sx1) / 2, (sy0 + sy1) / 2)), 'drain')
    fx, fyy = (sx0 + sx1) / 2, 3.43
    add('tap', lathe(rprof(0.024, CT, CT + 0.035, 0.006, 3), 24, (fx, fyy)), 'steel')
    neck = [(fx, fyy, CT + 0.03), (fx, fyy, CT + 0.24)]
    for a in np.linspace(0, math.pi, 13)[1:]:
        neck.append((fx, fyy - 0.08 + 0.08 * math.cos(a), CT + 0.24 + 0.08 * math.sin(a)))
    neck.append((fx, fyy - 0.16, CT + 0.20))
    add('tap', tube(neck, 0.011, 12), 'steel')
    add('soap', lathe([(0, CT), (0.03, CT), (0.03, CT + 0.13), (0.012, CT + 0.15), (0.012, CT + 0.17), (0, CT + 0.17)], 18, (2.84, 3.40)), 'mug_sage')
    add('tap', tube([(fx + 0.04, fyy, CT + 0.12), (fx + 0.09, fyy, CT + 0.13)], 0.006, 8), 'steel')
    # hob (black glass) with rings
    hx0, hx1, hy0, hy1 = XHOB[0] + 0.05, XHOB[1] - 0.05, 2.98, 3.46
    add('hob', box(hx0, hy0, CT, hx1, hy1, CT + 0.006), 'hob')
    for (cx, cy, rr) in ((hx0 + 0.13, hy0 + 0.13, 0.085), (hx1 - 0.13, hy0 + 0.13, 0.07), (hx0 + 0.13, hy1 - 0.13, 0.07), (hx1 - 0.13, hy1 - 0.13, 0.095)):
        add('hob', lathe([(rr - 0.004, CT + 0.0062), (rr, CT + 0.0062), (rr, CT + 0.0068), (rr - 0.004, CT + 0.0068)], 40, (cx, cy)), 'hob_ring')
    # fruit bowl over the dishwasher
    bowl('fruit', 1.27, 3.22, CT, 0.13, 0.07, 'ceramic')
    for (dx, dy, m) in ((-0.05, -0.03, 'lemon'), (0.04, -0.04, 'apple'), (0.0, 0.05, 'lemon'), (0.06, 0.04, 'apple'), (-0.06, 0.04, 'apple')):
        add('fruit', ellipsoid((1.27 + dx, 3.22 + dy, CT + 0.055), (0.038, 0.038, 0.036), 12), m)
    # desk kit: hob lid and sink cover (oak)
    wood('lid_hob', XHOB[0] + 0.004, 2.875, CT + 0.007, XHOB[1] - 0.004, 3.47, CT + 0.032, 'oak')
    wood('lid_sink', XSINK[0] + 0.004, 2.875, CT + 0.001, XSINK[1] - 0.004, 3.47, CT + 0.026, 'oak')


def build_uppers(rng):
    t = 0.018
    # narrow cupboard
    nm = 'up_narrow'
    carcass(nm, XDW[0] + 0.002, XDW[1] - 0.002, UY + 0.02, D - 0.012, UZ0, UZ1, m='white_cab')
    add(nm, box(XDW[0] + 0.003, UY, UZ0 + 0.002, XDW[1] - 0.003, UY + 0.02, UZ1 - 0.002), 'white_cab')
    add(nm, box(XDW[1] - 0.04, UY - 0.006, UZ0 + 0.01, XDW[1] - 0.025, UY, UZ0 + 0.20), 'groove')
    # two-door cupboard (1.75-2.45) over the oak jar shelf (1.50)
    x0, x1 = XSINK
    nm = 'up_two'
    carcass(nm, x0 + 0.002, x1 - 0.002, UY + 0.02, D - 0.012, 1.75, UZ1, m='white_in')
    add(nm, box(x0 + 0.002, UY + 0.02, 2.10, x1 - 0.002, D - 0.012, 2.118), 'white_in')
    add(nm, box(x0 + 0.04, UY + 0.03, 1.744, x1 - 0.04, UY + 0.06, 1.75), 'led_off')
    xm = (x0 + x1) / 2
    add('ud_L', box(x0 + 0.003, UY, 1.752, xm - 0.0015, UY + 0.02, UZ1 - 0.002), 'white_cab')
    add('ud_L', box(xm - 0.04, UY - 0.006, 1.77, xm - 0.025, UY, 1.95), 'groove')
    add('ud_R', box(xm + 0.0015, UY, 1.752, x1 - 0.003, UY + 0.02, UZ1 - 0.002), 'white_cab')
    add('ud_R', box(xm + 0.025, UY - 0.006, 1.77, xm + 0.04, UY, 1.95), 'groove')
    plates('up_plates', x0 + 0.16, 3.33, 1.768, 0.12, 8)
    plates('up_plates', x0 + 0.42, 3.33, 1.768, 0.10, 6, 'bowl_blue')
    for k in range(3):
        bowl('up_bowls', x0 + 0.17 + k * 0.20, 3.33, 2.118 + 0.0, 0.08, 0.06, 'bowl_blue')
        bowl('up_bowls', x0 + 0.17 + k * 0.20, 3.33, 2.150, 0.08, 0.06, 'bowl_blue' if k != 1 else 'plate')
    mug('up_bowls', x0 + 0.60, 3.30, 1.768, 'mug_yel', ang=math.pi)
    # oak jar shelf
    wood('jshelf', x0 + 0.01, UY + 0.03, 1.50, x1 - 0.01, D - 0.012, 1.525, 'oak')
    specs = [('jar', 'pasta'), ('jar', 'peas'), ('mug', 'mug_sage'), ('jar', 'beans'), ('mug', 'mug_blue'), ('jar', 'oats')]
    for k, (kind, m) in enumerate(specs):
        x = x0 + 0.08 + k * 0.118
        if kind == 'jar':
            jar(f'jar{k}', x, 3.34, 1.525, 0.042, 0.14 + 0.03 * (k % 2), m)
        else:
            mug(f'jar{k}', x, 3.32, 1.525, m, ang=-math.pi / 2 + 0.3)
    # pull-down cupboard (closed in the 15 s cut)
    x0, x1 = XCOR
    nm = 'up_pull'
    carcass(nm, x0 + 0.002, x1 - 0.002, UY + 0.02, D - 0.012, UZ0, UZ1, m='white_cab')
    add('pull_flap', box(x0 + 0.003, UY, UZ0 + 0.002, x1 - 0.003, UY + 0.02, UZ1 - 0.002), 'white_cab')
    add('pull_flap', box(x0 + 0.06, UY - 0.006, UZ0 + 0.01, x1 - 0.06, UY, UZ0 + 0.025), 'groove')
    bx0, bx1, by0, by1 = x0 + 0.04, x1 - 0.04, UY + 0.05, D - 0.04
    for z in (UZ0 + 0.03, 1.84):
        add('pull_bk', box(bx0, by0, z, bx1, by1, z + 0.012), 'white_in')
        add('pull_bk', box(bx0, by0, z, bx1, by0 + 0.01, z + 0.05), 'alu')
    for xx in (bx0, bx1 - 0.012):
        add('pull_bk', box(xx, by0, UZ0 + 0.03, xx + 0.012, by1, 2.30), 'alu')
    for k in range(3):
        bowl('pull_bk', bx0 + 0.08 + k * 0.155, 3.32, UZ0 + 0.042, 0.065, 0.055, ('bowl_blue', 'plate', 'bowl_blue')[k])
        bowl('pull_bk', bx0 + 0.08 + k * 0.155, 3.32, UZ0 + 0.072, 0.065, 0.055, ('plate', 'bowl_blue', 'plate')[k])
        mug('pull_bk', bx0 + 0.08 + k * 0.155, 3.32, 1.852, ('mug_yel', 'mug_sage', 'mug_blue')[k], ang=-math.pi / 2)
    # open corner shelves over the blind corner (x 3.40-4.0)
    for k, z in enumerate((1.50, 1.86, 2.22)):
        wood('oshelf', TX + 0.01, 3.02, z, W - 0.002, D - 0.012, z + 0.025, 'oak')
    add('oshelf', box(TX + 0.004, 3.02, 1.50, TX + 0.022, D - 0.012, UZ1), 'white_cab')
    # hood (matte white, underside 1.55) + telescoping duct into the bulkhead
    hx0, hx1 = XHOB
    add('hood', box(hx0 + 0.004, 3.08, 1.55, hx1 - 0.004, D - 0.012, 1.72), 'white_cab')
    add('hood', box(hx0 + 0.03, 3.10, 1.548, hx1 - 0.03, D - 0.04, 1.552), 'grille')
    add('hood', box(hx0 + 0.20, 3.07, 1.60, hx1 - 0.20, 3.08, 1.66), 'groove')
    add('duct', box(1.64, 3.16, 1.72, 1.94, D - 0.012, UZ1), 'white_cab')
    # LED pieces that switch on
    add('led_up', box(XDW[0] + 0.03, UY + 0.03, UZ0 - 0.004, XDW[1] - 0.03, UY + 0.05, UZ0 - 0.001), 'led')
    add('led_up', box(XCOR[0] + 0.03, UY + 0.03, UZ0 - 0.004, XCOR[1] - 0.03, UY + 0.05, UZ0 - 0.001), 'led')
    add('led_jar', box(XSINK[0] + 0.04, UY + 0.03, 1.744, XSINK[1] - 0.04, UY + 0.06, 1.7475), 'led')
    add('hood_on', box(hx0 + 0.12, 3.20, 1.546, hx1 - 0.12, 3.26, 1.5485), 'led')
    # late props
    plant('herb', 3.54, 3.26, 1.525, 0.055, 0.09, rng, 9, pot_m='ceramic')
    plant('herb2', 3.52, 3.30, 1.885, 0.045, 0.075, rng, 8, pot_m='mug_sage')
    jar('herb2', 3.74, 3.30, 1.885, 0.04, 0.16, 'pasta')
    bdx = 0.62 if LONG else 0.0                   # long cut: keep the worktop under the pull-down clear
    add('board', xform(rbox((0, 0, 0.17), (0.28, 0.018, 0.34), 0.008, 3), T(3.04 + bdx, 3.44, CT) @ R('x', -0.12)), 'board')
    add('board', xform(rbox((0, 0, 0.13), (0.22, 0.018, 0.26), 0.008, 3), T(3.22 + bdx, 3.43, CT) @ R('x', -0.10)), 'oak_z')
    # kettle on the worktop over the blind corner
    kx, ky = 3.56, 3.12
    add('kettle', lathe([(0, CT), (0.07, CT), (0.085, CT + 0.06), (0.08, CT + 0.16), (0.05, CT + 0.20), (0.02, CT + 0.21),
                         (0.02, CT + 0.22), (0, CT + 0.22)], 28, (kx, ky)), 'enamel')
    add('kettle', tube([(kx - 0.06, ky, CT + 0.17), (kx - 0.02, ky, CT + 0.26), (kx + 0.04, ky, CT + 0.25), (kx + 0.07, ky, CT + 0.17)], 0.008, 8), 'oak_x')
    add('kettle', tube([(kx + 0.07, ky, CT + 0.10), (kx + 0.13, ky, CT + 0.17)], 0.011, 8), 'enamel')


def build_fridge_contents():
    y0, y1 = FRI
    yy = np.linspace(y0 + 0.08, y1 - 0.08, 4)
    for i, y in enumerate(yy):                                   # fruit on the bottom shelf
        for j, x in enumerate((3.66, 3.80)):
            add('fr_c0', ellipsoid((x, y, 0.572), (0.038, 0.038, 0.036), 12), ('apple', 'lemon')[(i + j) % 2])
    for i, y in enumerate(np.linspace(y0 + 0.07, y1 - 0.07, 5)):  # blue yoghurt pots
        for j, x in enumerate((3.64, 3.76)):
            add('fr_c1', lathe([(0, 0.932), (0.036, 0.932), (0.04, 1.02), (0, 1.02)], 18, (x, y)), 'pot_blue' if (i + j) % 2 else 'ceramic')
    for i, y in enumerate(yy):                                   # peppers
        add('fr_c2', ellipsoid((3.70, y, 1.375), (0.045, 0.045, 0.05), 12), ('tin_red', 'apple', 'tin_yel', 'tin_red')[i])
    for i, y in enumerate(np.linspace(y0 + 0.09, y1 - 0.09, 3)):  # milk bottles
        add('fr_c3', lathe([(0, 1.732), (0.04, 1.732), (0.04, 1.90), (0.02, 1.95), (0.02, 1.98), (0, 1.98)], 20, (3.72, y)), 'ceramic')
        add('fr_c3', lathe(rprof(0.022, 1.975, 1.995, 0.004, 2), 14, (3.72, y)), 'bot_b')
    for z in (0.60, 1.10, 1.60):                                 # door bins (ride the door) and their bottles
        add('fr_door', box(3.425, FRI[0] + 0.05, z, 3.53, FRI[1] - 0.05, z + 0.01), 'white_cab')
        add('fr_door', box(3.52, FRI[0] + 0.05, z, 3.53, FRI[1] - 0.05, z + 0.08), 'white_cab')
        for i, y in enumerate(np.linspace(FRI[0] + 0.10, FRI[1] - 0.10, 5)):
            m = ('bot_g', 'bot_y', 'bot_b', 'ceramic', 'bot_g')[(i + int(z * 10)) % 5]
            add('fr_bins', lathe([(0, z + 0.01), (0.03, z + 0.01), (0.03, z + 0.16), (0.014, z + 0.21), (0, z + 0.21)], 16, (3.475, y)), m)


def build_shared_extras():
    tin('tea', 1.44, 3.36, CT, 0.045, 0.13, 'teal')
    mx = (1.48, 1.40) if LONG else (2.96, 3.08)
    my = (3.06, 3.00) if LONG else (3.30, 3.36)
    mug('mugs2', mx[0], my[0], CT, 'mug_sage', ang=-1.2)
    mug('mugs2', mx[1], my[1], CT, 'mug_yel', ang=-1.9)
    add('vase', lathe([(0, CT), (0.035, CT), (0.045, CT + 0.08), (0.025, CT + 0.15), (0.02, CT + 0.17), (0, CT + 0.17)], 22, (1.12, 3.40)), 'ceramic')
    for k in range(5):
        a = k * 1.3
        tip = (1.12 + 0.06 * math.cos(a), 3.40 + 0.05 * math.sin(a), CT + 0.30 + 0.02 * k)
        add('vase', tube([(1.12, 3.40, CT + 0.15), tip], 0.003, 5), 'leaf')
        add('vase', ellipsoid(tip, (0.02, 0.012, 0.035), 7), 'leaf2')


def build_long_extras(rng):
    # utensil rail on the tile over the sink (x 2.12-2.80; gap at the tap)
    add('rail', tube([(2.14, 3.46, 1.30), (2.80, 3.46, 1.30)], 0.008, 10), 'oak_x')
    for xx in (2.14, 2.80):
        add('rail', box(xx - 0.01, 3.46, 1.29, xx + 0.01, 3.488, 1.31), 'oak_x')
    for i, xx in enumerate((2.20, 2.27, 2.34, 2.60, 2.67, 2.74)):
        add('utens', tube([(xx, 3.455, 1.31), (xx, 3.455, 1.12)], 0.005, 6), 'oak_z' if i % 2 else 'ceramic')
        add('utens', ellipsoid((xx, 3.455, 1.10), (0.022, 0.008, 0.04), 10), 'oak_z' if i % 2 == 0 else 'mug_sage')
    # oils and a plant on the open corner shelves, tea tin by the fruit
    for i, xx in enumerate((3.66, 3.74, 3.82)):
        add('oils', lathe([(0, 1.525), (0.03, 1.525), (0.03, 1.70), (0.012, 1.75), (0.012, 1.78), (0, 1.78)], 18, (xx, 3.22)),
            ('bot_g', 'bot_y', 'bot_b')[i])
    plant('cplant', 3.62, 3.26, 2.245, 0.05, 0.08, rng, 9)
    # over-bed cupboard on the west wall: two lift-up flaps + an open book bay
    oz0, oz1, ox1 = 1.85, 2.45, 0.32
    carcass_y = (0.15, 1.95)
    add('ob_cab', box(0.0, carcass_y[0], oz0, ox1, carcass_y[0] + 0.018, oz1), 'white_cab')
    add('ob_cab', box(0.0, carcass_y[1] - 0.018, oz0, ox1, carcass_y[1], oz1), 'white_cab')
    add('ob_cab', box(0.0, carcass_y[0], oz0, ox1, carcass_y[1], oz0 + 0.018), 'white_cab')
    add('ob_cab', box(0.0, carcass_y[0], oz1 - 0.018, ox1, carcass_y[1], oz1), 'white_cab')
    add('ob_cab', box(0.0, 1.341, oz0, ox1, 1.359, oz1), 'white_cab')
    add('ob_cab', box(0.0, 0.741, oz0, ox1, 0.759, oz1), 'white_in')
    add('ob_cab', box(0.0, carcass_y[0], oz0, 0.012, carcass_y[1], oz1), 'white_in')
    add('ob_cab', box(0.03, carcass_y[0] + 0.03, oz0 - 0.004, 0.06, 1.33, oz0), 'led_off')
    for nm, (ya, yb_) in (('ob_flapA', (carcass_y[0], 0.75)), ('ob_flapB', (0.75, 1.35))):
        add(nm, box(ox1, ya + 0.002, oz0 + 0.002, ox1 + 0.02, yb_ - 0.002, oz1 - 0.002), 'white_cab')
        add(nm, box(ox1 + 0.02, ya + 0.08, oz0 + 0.01, ox1 + 0.026, yb_ - 0.08, oz0 + 0.025), 'groove')
    for (yc, mats_) in ((0.45, ('cl_white', 'cl_sage', 'cl_white', 'cl_blue')), (1.05, ('cl_grey', 'cl_white', 'cl_yel', 'cl_white'))):
        stack('ob_bedding', 0.16, yc - 0.13, oz0 + 0.018, (0.26, 0.24, 0.10), mats_, 4, rng)
        stack('ob_bedding', 0.16, yc + 0.13, oz0 + 0.018, (0.26, 0.24, 0.12), mats_[::-1], 3, rng)
    y = 1.37
    for i, (m, th, h) in enumerate((('bk_sage', 0.03, 0.24), ('bk_white', 0.025, 0.22), ('bk_blue', 0.035, 0.26), ('bk_yel', 0.03, 0.21),
                                    ('bk_teal', 0.028, 0.25), ('bk_grey', 0.03, 0.23), ('bk_white', 0.025, 0.2), ('bk_blue', 0.03, 0.24),
                                    ('bk_sage', 0.035, 0.22), ('bk_yel', 0.03, 0.26))):
        add('ob_books', box(0.03, y, oz0 + 0.018, 0.25, y + th, oz0 + 0.018 + h), m); y += th + 0.003
    add('ob_books', box(0.03, y + 0.02, oz0 + 0.018, 0.25, 1.93, oz0 + 0.05), 'bk_sage')
    plant('ob_plant', 0.16, 1.85, oz0 + 0.05, 0.045, 0.07, rng, 8)
    # wall light over the bed (switches on in the final)
    add('bedlight', box(0.0, 0.93, 1.48, 0.02, 1.07, 1.62), 'white_cab')
    add('bedlight', ellipsoid((0.06, 1.0, 1.55), (0.06, 0.06, 0.06), 14), 'lamp_sh')
    add('bedlight_on', ellipsoid((0.06, 1.0, 1.55), (0.061, 0.061, 0.061), 14), 'shade_glow')


def build_larder():
    """Five inner drawers inside the larder (open toward -x) + the birch door hinged on its south edge."""
    wood('lar_door', TX, LAR[0] + 0.002, 0.102, TX + 0.022, LAR[1] - 0.002, UZ1 - 0.004, 'birch')
    add('lar_door', box(TX - 0.006, LAR[1] - 0.05, 1.0, TX, LAR[1] - 0.035, 1.25), 'groove')
    y0, y1 = LAR[0] + 0.04, LAR[1] - 0.03
    fills = [('flour', 'oats'), ('pasta', 'peas'), ('beans', 'pasta'), ('tins', None), ('peas', 'beans')]
    for k in range(5):
        z = 1.70 - k * 0.36
        nm = f'lar_dr{k}'
        x0, x1 = TX + 0.03, W - 0.04
        add(nm, box(x0 + 0.0165, y0 + 0.0125, z, x1 - 0.0125, y1 - 0.0125, z + 0.012), 'white_in')
        for b in (box(x0 + 0.0165, y0, z, x1, y0 + 0.012, z + 0.11), box(x0 + 0.0165, y1 - 0.012, z, x1, y1, z + 0.11),
                  box(x1 - 0.012, y0 + 0.0125, z, x1, y1 - 0.0125, z + 0.11)):
            add(nm, b, 'white_in')
        wood(nm, x0, y0, z, x0 + 0.016, y1, z + 0.13, 'oak')
        for yy in (y0 - 0.008, y1):
            add(nm, box(x0 + 0.02, yy, z + 0.03, x1, yy + 0.008, z + 0.05), 'alu')
        add('room', box(x0 + 0.02, y0 - 0.016, z + 0.03, W - 0.03, y0 - 0.008, z + 0.05), 'alu')
        add('room', box(x0 + 0.02, y1 + 0.008, z + 0.03, W - 0.03, y1 + 0.016, z + 0.05), 'alu')
        cn = f'lar_c{k}'
        zz = z + 0.012
        if fills[k][0] == 'tins':
            for i, yy in enumerate(np.linspace(y0 + 0.07, y1 - 0.07, 4)):
                for j, xx in enumerate((x0 + 0.10, x0 + 0.21, x0 + 0.32, x0 + 0.43)):
                    tin(cn, xx, yy, zz, 0.036, 0.10, ('tin_blue', 'tin_green', 'tin_yel', 'tin_red')[(i + j) % 4])
        else:
            for i, yy in enumerate(np.linspace(y0 + 0.08, y1 - 0.08, 3)):
                for j, xx in enumerate((x0 + 0.11, x0 + 0.26, x0 + 0.41)):
                    hh = (0.13, 0.17, 0.15, 0.19)[(i * 3 + j + k) % 4] + (0.04 if k == 0 else 0.0)
                    jar(cn, xx, yy, zz, 0.05 if (i + j) % 3 else 0.045, hh, fills[k][(i + j) % 2],
                        lid=('cork', 'ceramic', 'oak_z')[(i + 2 * j + k) % 3], frac=0.6 + 0.1 * ((i + j + k) % 3))


def build_bed(rng):
    """Storage bed: white platform x 0-1.40, y 0-2.0, top 0.60, three deep drawers facing east, head to the north."""
    bx1, by1 = 1.40, 2.0
    add('bed', box(0.0, 0.0, 0.0, bx1 - 0.05, by1, 0.06), 'plinth')
    add('bed', box(0.0, 0.0, 0.06, bx1, by1, 0.38), 'white_cab')
    add('bed', box(0.0, 0.0, 0.38, bx1, by1, 0.40), 'white_cab')
    for k in range(3):
        y0 = 0.02 + k * 0.66
        nm = f'bed_dr{k}'
        wood(nm, bx1, y0 + 0.003, 0.065, bx1 + 0.02, y0 + 0.65, 0.37, 'birch')
        for b in (box(0.82, y0 + 0.03, 0.08, bx1, y0 + 0.62, 0.092), box(0.82, y0 + 0.03, 0.08, 0.832, y0 + 0.62, 0.34),
                  box(0.82, y0 + 0.03, 0.08, bx1, y0 + 0.042, 0.34), box(0.82, y0 + 0.608, 0.08, bx1, y0 + 0.62, 0.34)):
            add(nm, b, 'white_in')
        cm = [('cl_blue', 'cl_white', 'cl_sage'), ('cl_yel', 'cl_grey', 'cl_white'), ('cl_sage', 'cl_navy', 'cl_blue')][k]
        stack(f'bed_c{k}', 0.98, y0 + 0.19, 0.092, (0.26, 0.24, 0.05), cm, 4, rng)
        stack(f'bed_c{k}', 1.25, y0 + 0.19, 0.092, (0.24, 0.24, 0.05), cm[::-1], 3, rng)
        stack(f'bed_c{k}', 1.10, y0 + 0.46, 0.092, (0.40, 0.22, 0.06), cm[1:] + cm[:1], 3, rng)
        add(nm, box(bx1 + 0.02, y0 + 0.28, 0.33, bx1 + 0.026, y0 + 0.38, 0.345), 'groove')
    wood('bed', -0.0, by1 - 0.04, 0.38, bx1, by1, 1.05, 'oak')                       # headboard
    add('bed', rbox((0.69, 1.0, 0.50), (1.36, 1.92, 0.20), 0.05, 5), 'mattress')
    cloth('bed', 0.0, 1.40, 0.04, 1.55, 0.62, 0.43, 0.05, 'linen', 3)
    add('bed', rbox((0.70, 1.51, 0.632), (1.44, 0.14, 0.03), 0.013, 3), 'pil_white')
    cloth('bed', -0.02, 1.42, 0.10, 0.55, 0.656, 0.46, 0.04, 'throw', 7, sides=('e',), puff=0.006)
    pillow('bed', (0.37, 1.86, 0.78), (0.58, 0.15, 0.40), -0.36, 'pil_white')
    pillow('bed', (1.03, 1.86, 0.78), (0.58, 0.15, 0.40), -0.36, 'pil_white')
    pillow('bed', (0.48, 1.70, 0.74), (0.42, 0.13, 0.38), -0.28, 'pil_blue')
    pillow('bed', (0.92, 1.70, 0.74), (0.42, 0.13, 0.38), -0.28, 'pil_blue')


def build_stool():
    cx, cy = STOOL_DESK
    add('stool', lathe(rprof(0.185, SEAT - 0.035, SEAT, 0.012, 3), 32, (cx, cy)), 'oak_x')
    for k in range(4):
        a = math.pi / 4 + k * math.pi / 2
        add('stool', tube([(cx + 0.13 * math.cos(a), cy + 0.13 * math.sin(a), SEAT - 0.035),
                           (cx + 0.19 * math.cos(a), cy + 0.19 * math.sin(a), 0.0)], 0.014, 8), 'oak_z')
    ring = [(cx + 0.17 * math.cos(a), cy + 0.17 * math.sin(a), 0.24) for a in np.linspace(0, 2 * math.pi, 25)]
    add('stool', tube(ring, 0.008, 8), 'white_cab')
    # a book and a small plant on the stool while it is the bedside table
    add('stool_top', box(cx - 0.09, cy - 0.06, SEAT, cx + 0.06, cy + 0.10, SEAT + 0.025), 'bk_sage')
    add('stool_top', box(cx - 0.085, cy - 0.055, SEAT + 0.025, cx + 0.055, cy + 0.095, SEAT + 0.045), 'bk_white')


def build_desk_props(rng):
    # laptop on the sink cover (cover extended 0.25 m: y 2.625..3.22)
    lx, ly, lz = 2.465, 2.80, CT + 0.026
    add('laptop', box(lx - 0.16, ly - 0.11, lz, lx + 0.16, ly + 0.11, lz + 0.012), 'laptop')
    add('laptop', box(lx - 0.14, ly - 0.02, lz + 0.012, lx + 0.14, ly + 0.09, lz + 0.0125), 'kb')
    lid = xform(box(-0.16, -0.006, 0.0, 0.16, 0.0, 0.21), T(lx, ly + 0.11, lz + 0.006) @ R('x', math.radians(-12)))
    add('laptop', lid, 'laptop')
    add('laptop', xform(box(-0.15, -0.0075, 0.01, 0.15, -0.006, 0.20), T(lx, ly + 0.11, lz + 0.006) @ R('x', math.radians(-12))), 'screen')
    # table lamp on the hob lid
    ax, ay, az = 1.66, 3.30, CT + 0.032
    add('lamp', lathe(rprof(0.07, az, az + 0.016, 0.006, 3), 28, (ax, ay)), 'white_cab')
    add('lamp', tube([(ax, ay, az + 0.01), (ax, ay, az + 0.30)], 0.007, 10), 'alu')
    add('lamp', lathe([(0.0, az + 0.42), (0.03, az + 0.42), (0.10, az + 0.29), (0.105, az + 0.28), (0.0, az + 0.28)], 32, (ax, ay)), 'lamp_sh')
    add('lamp_on', lathe([(0.0, az + 0.30), (0.022, az + 0.30), (0.022, az + 0.33), (0.0, az + 0.34)], 16, (ax, ay)), 'bulb')
    add('lamp_on', lathe([(0.0, az + 0.285), (0.098, az + 0.285), (0.098, az + 0.288), (0.0, az + 0.288)], 32, (ax, ay)), 'shade_glow')
    mug('mug', 2.20, 2.76, CT + 0.026, 'mug_blue', ang=-0.6)
    # a notebook by the laptop
    add('laptop', box(2.68, 2.70, lz, 2.80, 2.86, lz + 0.012), 'bk_yel')


def build():
    materials()
    rng = np.random.default_rng(5)
    build_shell()
    build_panels()
    build_tiles()
    build_base(rng)
    build_uppers(rng)
    build_larder()
    build_bed(rng)
    build_stool()
    build_desk_props(rng)
    build_fridge_contents()
    build_shared_extras()
    if LONG:
        build_long_extras(rng)
    add('dimmer', box(-5.0, -5.0, -5.0, -4.99, -4.99, -4.99), 'white_in')        # hidden; its x offset = daylight dip
    global COOK
    COOK = fg.Figure('cook', 'adult', mat='fig_denim')
    COOK.build(COOK.sit_pose(SEAT, base='sit_desk'), at=(STOOL_DESK[0], STOOL_DESK[1] + 0.02, 0.0), seat=SEAT)


COOK = None

# ------------------------------------------------------------------------------------------- camera
VFOV = 85.0


def P(x, y, z, yaw, pitch):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch)


P1 = P(1.95, 0.20, 1.45, -4.0, -4.0)                                                  # frame 1 (and the loop end)
S1 = (P1, P(1.95, 0.85, 1.40, 4.0, -6.0))                                             # doorway push-in on the birch wall
S2 = (P(1.80, 1.05, 1.45, -6.0, -6.0), P(2.70, 0.95, 1.45, 16.0, -8.0))                # cooking run, slide east
S3 = (P(1.55, 0.85, 1.55, 53.0, -16.0), P(1.80, 0.72, 1.48, 47.0, -14.0))             # larder, drawers at ~45 deg
S3B = (P(3.35, 1.35, 1.42, -40.0, -13.0), P(3.22, 1.58, 1.36, -31.0, -11.0))          # the desk, three-quarter
S4 = (P(1.85, 1.05, 1.55, -14.0, -8.0), P(2.55, 1.45, 1.22, 6.0, -3.0))               # lit run, slide east
S5 = (P(1.95, -0.038, 1.468, -6.93, -3.27), P1)                                       # closing wide, drifts into frame 1
HOLDS = [(0.0, 3.0, S1), (3.3, 7.0, S2), (7.3, 8.36, S3), (8.56, 10.75, S3B), (11.0, 13.6, S4), (13.9, DUR_CUT, S5)]
if LONG:
    A1 = (P1, P(1.95, 0.88, 1.275, 2.5, -8.0))                                         # the wall opens, the run builds
    A2 = (P(2.50, 1.45, 1.32, 0.0, -27.0), P(2.25, 1.60, 1.30, -36.0, -26.0))          # low slide west: U drawer, dishwasher
    A3 = (P(1.60, 1.15, 1.50, -6.0, 4.0), P(1.75, 1.55, 1.50, -2.0, 6.0))             # push-in on the hob end: uppers, hood, duct
    A4 = (P(2.05, 1.40, 1.55, -4.0, -2.0), P(2.60, 1.55, 1.55, 16.0, -2.0))           # slide east: cupboard, rail, corner shelf
    A5 = (P(2.30, 1.25, 1.30, 26.0, -24.0), P(2.80, 1.35, 1.25, 12.0, -26.0))         # corner shelves, orbit
    A6 = (P(2.10, 2.62, 1.45, 104.0, -10.0), P(2.55, 2.50, 0.85, 104.0, -24.0))       # the fridge, push-in ending low
    A7 = (P(1.55, 0.55, 0.75, 52.0, 6.0), P(1.70, 0.70, 1.30, 50.0, -8.0))            # larder, low angle rising
    A8 = (P(2.05, 0.55, 2.05, 48.0, -32.0), P(2.30, 0.80, 2.05, 56.0, -34.0))         # larder, high slide
    A9 = (P(1.20, 0.85, 1.55, 34.0, -17.0), P(1.85, 0.90, 1.55, 6.0, -17.0))          # orbit around the new desk
    A10 = (P(2.72, 1.62, 1.40, 9.0, 6.0), P(2.82, 1.82, 1.42, 4.0, 9.0))            # pull-down over the figure
    A11 = (P(3.10, 1.05, 1.40, -104.0, -16.0), P(2.70, 1.00, 1.32, -104.0, -16.0))    # beside the larder, the bed drawers
    A12 = (P(2.00, 1.85, 1.55, -100.0, 5.0), P(2.00, 1.05, 1.55, -88.0, 5.0))         # over-bed cupboard, slide south
    A13 = (P(1.95, -0.73, 1.382, -8.2, -5.45), P1)                                     # the lit wide, drifts into frame 1
    HOLDS = [(0.0, 3.4, A1), (3.7, 7.4, A2), (7.7, 10.9, A3), (11.2, 14.6, A4), (14.9, 18.2, A5), (18.5, 21.9, A6),
             (22.2, 25.3, A7), (25.6, 28.2, A8), (28.5, 31.9, A9), (32.2, 34.95, A10), (34.95, 38.2, A11),
             (38.5, 41.35, A12), (41.35, DUR_CUT, A13)]
DUR = float(len(HOLDS)) if REST else DUR_CUT

camera = hold_camera(HOLDS, VFOV, rest=REST)

# ------------------------------------------------------------------------------------------- lights (fixed slots)
LSKY = (9.0, 9.6, 10.6)
LSUN = (62000.0, 58500.0, 52000.0)
LDOOR = (2.2, 2.2, 2.15)
LBOUNCE = (1.1, 1.1, 1.08)
LNICHE = (3.0, 3.0, 2.95)
LUP = (95.0, 85.0, 66.0)
LJAR = (80.0, 71.0, 55.0)
LHOOD = (800.0, 720.0, 560.0)
LLAMP = (170.0, 136.0, 92.0)
LBED = (160.0, 130.0, 90.0)
LOB = (40.0, 35.0, 27.0)


def lights(mats4, vis):
    off = (0.0, 0.0, 0.0)

    def k(L, on, f=1.0):
        return tuple(v * f for v in L) if on else off
    Ls = []
    day = 1.0 - float(mats4['dimmer'][0, 3]) if 'dimmer' in mats4 else 1.0
    Ls.append(rect_light((W + 0.16, WY0, WZ0), (0, 0, WZ1 - WZ0), (0, WY1 - WY0, 0), k(LSKY, True, day), always=1))   # 0 sky (-x)
    sc = np.array([W, (WY0 + WY1) / 2, (WZ0 + WZ1) / 2]) - SUN_DIR * 3.0
    Ls.append(spot_rect(tuple(sc), tuple(SUN_DIR), 0.06, k(LSUN, True, day), 0.0))                          # 1 sun
    Ls.append(rect_light((0.2, 0.005, 0.3), (0, 0, 1.9), (1.2, 0, 0), LDOOR, always=1))                       # 2 fill +y
    Ls.append(rect_light((2.6, 0.005, 0.3), (0, 0, 1.9), (1.2, 0, 0), LDOOR))                                 # 3 fill +y
    Ls.append(rect_light((0.005, 0.2, 1.0), (0, 1.8, 0), (0, 0, 1.4), LBOUNCE))                               # 4 fill +x
    Ls.append(rect_light((KX0 + 0.05, NY + 0.02, UZ1 - 0.004), (0, 0.24, 0), (W - KX0 - 0.1, 0, 0), LNICHE))  # 5 niche (down)
    up = vis.get('led_up')
    Ls.append(rect_light((XDW[0] + 0.03, UY + 0.03, UZ0 - 0.005), (0, 0.02, 0), (XDW[1] - XDW[0] - 0.06, 0, 0), k(LUP, up)))   # 6
    Ls.append(rect_light((XCOR[0] + 0.03, UY + 0.03, UZ0 - 0.005), (0, 0.02, 0), (XCOR[1] - XCOR[0] - 0.06, 0, 0), k(LUP, up)))  # 7
    Ls.append(rect_light((XSINK[0] + 0.04, UY + 0.03, 1.743), (0, 0.03, 0), (XSINK[1] - XSINK[0] - 0.08, 0, 0), k(LJAR, vis.get('led_jar'))))  # 8
    Ls.append(spot_rect(((XHOB[0] + XHOB[1]) / 2, 3.23, 1.545), (0, 0, -1), 0.08, k(LHOOD, vis.get('hood_on')), 3.0))  # 9 hood
    Ls.append(sphere_light((1.66, 3.30, CT + 0.345), 0.022, k(LLAMP, vis.get('lamp_on'))))                    # 10 desk lamp
    Ls.append(sphere_light((0.07, 1.0, 1.55), 0.05, k(LBED, vis.get('bedlight_on'))))                          # 11 bed wall light
    Ls.append(rect_light((0.03, 0.18, 1.845), (0, 1.15, 0), (0.03, 0, 0), k(LOB, vis.get('bedlight_on'))))     # 12 under-cupboard
    return Ls


BLENDER = dict(
    exposure=-0.30,
    look='AgX - Medium High Contrast',
    separate=['backdrop'],
    fill_lights=[2, 3, 4, 5],
    glass=[],
    wood_scale=(55.0, 1.6),
    bake_rect={'backdrop': (-3.0, 7.0, -2.0, 6.0)},
    bake_px={'backdrop': 0.006, 'floor': 0.0015},
)


# ------------------------------------------------------------------------------------------- timeline helpers
def make_tl():
    tl = Timeline(rk, FPS)
    I = np.eye(4)

    def appear(name, t_on, t_off=None):
        tl.custom(name, lambda t: (I, t >= t_on and (t_off is None or t < t_off)))

    def door_oc(name, hinge, a_open, t_open, t_close, base=None, axis='z', out=0.16, shut=0.17, snd=True):
        """A door that is closed, swings open at t_open (with overshoot), holds, and slams shut at t_close."""
        hinge = np.array(hinge, float)

        def f(t):
            B, v = base(t) if base is not None else (I, True)
            if t < t_open:
                return B, v
            if t < t_close:
                return B @ about(hinge, R(axis, a_open * eob((t - t_open) / out, 1.3))), v
            u = (t - t_close) / shut
            if u < 1:
                return B @ about(hinge, R(axis, a_open * (1 - u * u))), v
            tau = t - t_close - shut
            a = math.copysign(math.radians(1.5), a_open) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))
            return B @ about(hinge, R(axis, a)), v
        tl.custom(name, f)
        if snd:
            tl.ev(t_open + 0.06, name + '_open', 0.45, 'swish')
            tl.ev(t_close + shut, name + '_shut', 0.7, 'thud')
        return f

    def drawer_fn(t_open, t_close, off, base=None, out=0.14, shut=0.17, t_appear=-1.0):
        off = np.array(off, float)

        def f(t):
            B, v = base(t) if base is not None else (I, True)
            if t < t_appear:
                return I, False
            if t < t_open:
                return B, v
            if t < t_close:
                return B @ T(*(off * eob((t - t_open) / out, 1.4))), v
            k = 1 - smooth((t - t_close) / shut)
            tau = t - t_close - shut
            wob = 0.005 * math.exp(-tau / 0.05) * math.sin(2 * math.pi * tau / 0.12) if tau > 0 else 0.0
            return B @ T(*(off * k + off / (np.linalg.norm(off) + 1e-9) * wob)), v
        return f

    def ride(name, parent, t_on=-1.0):
        tl.custom(name, lambda t: (parent(t)[0], t >= t_on and parent(t)[1]))

    tl.appear, tl.door_oc, tl.drawer_fn, tl.ride = appear, door_oc, drawer_fn, ride
    return tl


def panels_anim(tl, keys, clacks=()):
    """keys: [(t, theta_deg, slide)] eased; the four panels follow panel_mats."""
    keys = sorted(keys)

    def state(t):
        if t <= keys[0][0]:
            return keys[0][1], keys[0][2]
        for i in range(len(keys) - 1):
            t0, a0, s0 = keys[i]; t1, a1, s1 = keys[i + 1]
            if t < t1:
                u = (t - t0) / (t1 - t0)
                e = eoc(u) if a1 > a0 or s1 > s0 else smooth(u)
                return a0 + (a1 - a0) * e, s0 + (s1 - s0) * e
        return keys[-1][1], keys[-1][2]
    cache = {}

    def mats(t):
        if t not in cache:
            if len(cache) > 32:
                cache.clear()
            a, s = state(t)
            cache[t] = panel_mats(math.radians(a), s)
        return cache[t]
    for k in range(NP):
        tl.custom(f'pan{k}', lambda t, k=k: (mats(t)[k], True))
    for (tc, st, f0) in clacks:
        tl.events.append(dict(t=round(tc, 3), name='clack', strength=st, kind='thud', f0=f0))


SLIDE_IN = 0.632


# ------------------------------------------------------------------------------------------- 15 s timeline
def timeline_15(tl):
    I = np.eye(4)
    cen, ev = tl.cen, tl.ev
    drop, fly, slide, grow, from_camera = tl.drop, tl.fly, tl.slide, tl.grow, tl.from_camera
    appear, door_oc, drawer_fn, ride = tl.appear, tl.door_oc, tl.drawer_fn, tl.ride
    cam_s1 = np.array(S1[0]['pos']); cam_s2 = np.array(S2[0]['pos'])

    # ---- the wall folds open (0.10-0.44), the stack slides into the pocket (0.44-0.62); closes 13.75-14.40
    panels_anim(tl, [(0.04, 0.0, 0.0), (0.30, 90.0, 0.0), (0.36, 90.0, 0.0), (0.54, 90.0, SLIDE_IN),
                     (13.95, 90.0, SLIDE_IN), (14.10, 90.0, 0.0), (14.55, 0.0, 0.0)],
                clacks=[(0.10, 0.55, 140), (0.17, 0.6, 160), (0.24, 0.65, 180), (0.30, 0.7, 200),
                        (14.16, 0.7, 200), (14.29, 0.65, 180), (14.42, 0.6, 160), (14.55, 0.75, 120)])
    ev(0.54, 'pocket', 0.35, 'swish')
    # ---- sage tiles slap onto the back wall right to left (0.30-1.00)
    for i, k in enumerate(range(9, -1, -1)):
        t1 = 0.30 + 0.078 * i
        from_camera(f'tile{k}', t1 - 0.16, t1, cam_s1, 0.40, 0.25, 'tick')
    # ---- base units grow out of the back wall (1.05-1.65)
    for i, nm in enumerate(('b_dw', 'b_hob', 'b_sink', 'b_corner')):
        slide(nm, 0.90 + 0.15 * i, 1.08 + 0.15 * i, (0, -0.75, 0.0), 0.9, 0.75)
    base_cor = tl.anims['b_corner']
    for nm in ('dw_door', 'dw_rack0', 'dw_rack1'):
        ride(nm, tl.anims['b_dw'])
    for nm in ('sink_dr', 'sink_bot'):
        ride(nm, tl.anims['b_sink'])
    drop('worktop', 1.68, 1.85, 0.40, 0.02, 0.9, 'thud')
    drop('sink', 2.02, 2.15, 0.30, 0.03, 0.5, 'thud')
    drop('hob', 2.16, 2.30, 0.30, 0.03, 0.6, 'thud')
    drop('fruit', 2.38, 2.55, 0.35, 0.05, 0.4)
    drop('tap', 2.60, 2.75, 0.30, 0.04, 0.35)
    drop('soap', 2.98, 3.12, 0.25, 0.06, 0.3)

    # ---- S2: uppers, hood, duct, jars, two-door cupboard, corner shelves
    from_camera('up_narrow', 3.30, 3.52, cam_s2, 0.35, 0.8, 'thud')
    from_camera('up_two', 3.40, 3.64, cam_s2, 0.35, 0.8, 'thud')
    from_camera('up_pull', 3.52, 3.76, cam_s2, 0.35, 0.8, 'thud')
    up2 = tl.anims['up_two']
    for nm in ('pull_flap', 'pull_bk'):
        ride(nm, tl.anims['up_pull'])
    fly('oshelf', 3.66, 3.86, (0.5, 0, 0.1), 0.05, 0.5, 'thud')
    drop('hood', 3.80, 3.95, 0.35, 0.02, 0.7, 'thud')
    grow('duct', 4.10, 4.35, 'z', (0, 0, 1.72), 0.4, 'swish')
    slide('jshelf', 4.12, 4.28, (0, -0.5, 0), 1.0, 0.4)
    for k in range(6):
        drop(f'jar{k}', 4.28 + 0.1 * k, 4.40 + 0.1 * k, 0.22, 0.06, 0.32)
    xm = (XSINK[0] + XSINK[1]) / 2
    door_oc('ud_L', (XSINK[0] + 0.003, UY + 0.02, 0), math.radians(-100), 4.95, 5.40, base=up2)
    door_oc('ud_R', (XSINK[1] - 0.003, UY + 0.02, 0), math.radians(100), 4.98, 5.42, base=up2, snd=False)
    drop('up_plates', 5.00, 5.14, 0.22, 0.03, 0.45)
    drop('up_bowls', 5.16, 5.30, 0.22, 0.04, 0.4)
    cd = door_oc('cor_door', (XCOR[0] + 0.003, FB, 0), math.radians(-105), 5.55, 6.90, base=base_cor)

    def kidney(k, t_out, t_back):
        out = np.array([-0.28, -0.58, 0.0])

        def f(t):
            if t < t_out:
                return I, False
            if t < t_back:
                u = c01((t - t_out) / 0.40)
                a = eoc(min(1.0, u * 2)); b = eob(max(0.0, u * 2 - 1), 1.2)       # first to the west, then out
                return T(out[0] * a, out[1] * b, 0), True
            u = c01((t - t_back) / 0.30)                                          # back in, then east
            a = 1 - smooth(max(0.0, u * 2 - 1)); b = 1 - smooth(min(1.0, u * 2))
            return T(out[0] * a, out[1] * b, 0), t < t_back + 0.30
        return f
    for k in range(2):
        f = kidney(k, 5.65 + 0.06 * k, 6.50 + 0.05 * k)
        tl.custom(f'cs{k}', f)
        ev(6.05 + 0.06 * k, f'cs{k}_out', 0.4, 'swish')
        drop(f'pots{k}', 6.10 + 0.15 * k, 6.24 + 0.15 * k, 0.28, 0.04, 0.5, 'thud', parent=f)
        tl.anims[f'pots{k}'] = (lambda g, f=f: (lambda t: (g(t)[0], g(t)[1] and f(t)[1])))(tl.anims[f'pots{k}'])
    ev(6.80, 'cs_back', 0.4, 'swish')

    # ---- S3: the larder cascade, then the kitchen becomes a desk
    lar = door_oc('lar_door', (TX, LAR[0] + 0.002, 0), math.radians(115), 7.35, 8.36, out=0.22)
    for k in range(5):
        f = drawer_fn(7.45 + 0.08 * k, 8.30 - 0.06 * k, (-0.42, 0, 0), out=0.16)
        tl.custom(f'lar_dr{k}', f)
        ev(7.55 + 0.08 * k, f'lar_dr{k}_out', 0.3, 'tick')
        drop(f'lar_c{k}', 7.50 + 0.12 * k, 7.62 + 0.12 * k, 0.25, 0.04, 0.4, 'tick', parent=f)

    def lid_path(name, t0, t1, dz=0.10, dy=-0.45):
        def f(t):
            if t < t0:
                return I, False
            u = (t - t0) / (t1 - t0)
            if u < 1:
                a = eoc(min(1.0, u / 0.6)); b = smooth(max(0.0, (u - 0.5) / 0.5))
                return T(0, dy * (1 - a), dz * (1 - b)), True
            tau = t - t1
            return T(0, 0, 0.006 * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))), True
        tl.custom(name, f)
        ev(t1, name, 0.8, 'thud')
        return f
    lid_path('lid_hob', 8.72, 9.00, dz=0.16)
    ls0 = lid_path('lid_sink', 8.92, 9.20, dz=0.16)

    def lid_sink(t):
        M, v = ls0(t)
        if t < 9.24:
            return M, v
        if t < 11.00:
            return T(0, -0.245 * eob(c01((t - 9.24) / 0.16), 1.0), 0), True
        return T(0, -0.245 * (1 - smooth(c01((t - 11.00) / 0.15))), 0), True
    tl.custom('lid_sink', lid_sink)
    ev(9.36, 'ledge', 0.45, 'swish'); ev(11.15, 'ledge_back', 0.5, 'thud')
    # stool: bed head -> desk -> bed head (the book on it hops off while it is the desk seat)
    d_bed = np.array([STOOL_BED[0] - STOOL_DESK[0], STOOL_BED[1] - STOOL_DESK[1], 0.0])

    def stool(t):
        if t < 9.30:
            return T(*d_bed), True
        if t < 9.70:
            u = (t - 9.30) / 0.40
            return T(*(d_bed * (1 - smooth(u)))) @ about((*STOOL_DESK, 0), R('z', 0.9 * math.sin(math.pi * u))), True
        if t < 11.05:
            tau = t - 9.70
            return about((*STOOL_DESK, 0), R('z', 0.05 * math.exp(-tau / 0.1) * math.sin(2 * math.pi * tau / 0.25))), True
        u = c01((t - 11.05) / 0.40)
        return T(*(d_bed * smooth(u))) @ about((*STOOL_DESK, 0), R('z', -0.7 * math.sin(math.pi * u))), True
    tl.custom('stool', stool)
    ev(9.70, 'stool', 0.7, 'thud'); ev(11.45, 'stool_back', 0.6, 'thud')

    pc = np.array([STOOL_DESK[0], STOOL_DESK[1], SEAT])

    def stool_top(t):
        if t < 9.12:
            return T(*d_bed), True
        if t < 9.27:
            u = (t - 9.12) / 0.15
            return T(*d_bed) @ T(0, 0, 0.12 * u) @ about(pc, S(*([1 - u] * 3))), True
        if t < 11.47:
            return I, False
        u = (t - 11.47) / 0.15
        if u < 1:
            return T(*d_bed) @ T(0, 0, 0.12 * (1 - u)) @ about(pc, S(*([0.2 + 0.8 * u] * 3))), True
        return T(*d_bed), True
    tl.custom('stool_top', stool_top)
    ev(9.20, 'book_off', 0.25, 'tick'); ev(11.62, 'book_back', 0.3, 'tick')
    on_cover = lambda t: (lid_sink(t)[0] @ T(0, 0.245, 0), True)
    for nm, t0, t1 in (('laptop', 9.38, 9.52), ('lamp', 9.50, 9.64), ('mug', 10.20, 10.33)):
        drop(nm, t0, t1, 0.25, 0.04, 0.45 if nm != 'mug' else 0.3, 'thud' if nm != 'mug' else 'tick',
             parent=(on_cover if nm != 'lamp' else None))
    # the figure pops in seated, turns its head to the window, is hidden during the swing
    sit = COOK.sit_pose(SEAT, base='sit_desk')
    look = dict(sit, neck_turn=-60, neck=4, spine_twist=-8)
    stand = fg.pose_of('stand')
    at_c = (STOOL_DESK[0], STOOL_DESK[1] + 0.02, 0.0)
    M_st = COOK.root(stand, (at_c[0], at_c[1] - 0.30, 0.0), 0.0)
    M_si = COOK.root(sit, at_c, seat=SEAT)
    T_SIT0, T_SIT1 = 9.86, 10.18                       # pops in standing behind the stool, then lowers onto it

    def cook_M(t):
        u = smooth(c01((t - T_SIT0) / (T_SIT1 - T_SIT0)))
        M = M_si.copy(); M[:3, 3] = M_st[:3, 3] * (1 - u) + M_si[:3, 3] * u
        return M
    COOK.animate(tl, pose=fg.track([(T_SIT0, stand), (T_SIT1, sit), (10.36, sit), (10.62, look)]), M=cook_M,
                 floor=0.0, visible=lambda t: t < 10.80, pop=9.66)
    ev(T_SIT1, 'sit', 0.45, 'thud')

    # ---- S4: put back, lights on, then the wall closes and the room returns to frame 1
    drop('herb', 11.18, 11.30, 0.25, 0.06, 0.35)
    appear('led_up', 11.60, 14.55); ev(11.60, 'led_on', 0.7, 'chime')
    appear('led_jar', 11.80, 14.55); ev(11.80, 'jar_on', 0.5, 'chime')
    appear('hood_on', 12.00, 14.55); ev(12.00, 'hood_on', 0.5, 'chime')
    appear('lamp_on', 11.90, 14.55); ev(11.90, 'lamp_on', 0.5, 'chime')
    tl.custom('dimmer', lambda t: (T(0.15 * smooth(c01((t - 11.15) / 0.5)) * (1 - smooth(c01((t - 13.80) / 0.60))), 0, 0), False))
    drop('tea', 11.92, 12.04, 0.25, 0.05, 0.35)
    drop('board', 12.26, 12.40, 0.25, 0.04, 0.4)
    drop('mugs2', 12.48, 12.60, 0.22, 0.05, 0.3)
    drop('kettle', 12.64, 12.80, 0.30, 0.04, 0.45, 'thud')
    drop('herb2', 13.06, 13.20, 0.22, 0.05, 0.35)
    drop('vase', 13.42, 13.56, 0.25, 0.06, 0.35)


def timeline_rest(tl):
    I = np.eye(4)
    for k, M in enumerate(panel_mats(math.pi / 2, SLIDE_IN)):
        tl.custom(f'pan{k}', lambda t, M=M: (M, True))
    for nm in ('led_up', 'led_jar', 'hood_on', 'lamp_on', 'bedlight_on'):
        tl.custom(nm, lambda t: (I, False))
    tl.custom('lid_sink', lambda t: (T(0, -0.245, 0), True))
    tl.custom('stool_top', lambda t: (I, False))
    tl.custom('dimmer', lambda t: (I, False))


def timeline():
    tl = make_tl()
    if REST:
        timeline_rest(tl)
    elif LONG:
        timeline_long(tl)
    else:
        timeline_15(tl)
    return tl


def timeline_long(tl):
    """46.0 s = 23 bars at 120 BPM. 7 zones, 13 angles (A1..A13), the wow at 29.1-30.9 s."""
    I = np.eye(4)
    cen, ev = tl.cen, tl.ev
    drop, fly, slide, grow, from_camera = tl.drop, tl.fly, tl.slide, tl.grow, tl.from_camera
    appear, door_oc, drawer_fn, ride = tl.appear, tl.door_oc, tl.drawer_fn, tl.ride
    cam1, cam3 = np.array(A1[0]['pos']), np.array(A3[0]['pos'])

    # ===== Z1 a1 (0.0-3.4): the wall opens and the run builds
    panels_anim(tl, [(0.10, 0.0, 0.0), (0.42, 90.0, 0.0), (0.46, 90.0, 0.0), (0.64, 90.0, SLIDE_IN)],
                clacks=[(0.16, 0.55, 140), (0.24, 0.6, 160), (0.32, 0.65, 180), (0.40, 0.7, 200)])
    ev(0.64, 'pocket', 0.35, 'swish')
    for i, k in enumerate(range(9, -1, -1)):
        t1 = 0.30 + 0.11 * i
        from_camera(f'tile{k}', t1 - 0.15, t1, cam1, 0.22, 0.25, 'tick')
    for i, nm in enumerate(('b_dw', 'b_hob', 'b_sink', 'b_corner')):
        slide(nm, 1.18 + 0.22 * i, 1.38 + 0.22 * i, (0, -0.75, 0.0), 0.9, 0.75)
    base_cor = tl.anims['b_corner']
    drop('worktop', 2.07, 2.24, 0.40, 0.02, 0.9, 'thud')
    drop('sink', 2.34, 2.47, 0.30, 0.03, 0.5, 'thud')
    drop('hob', 2.52, 2.66, 0.30, 0.03, 0.6, 'thud')
    drop('fruit', 2.68, 2.85, 0.35, 0.05, 0.4)
    drop('tap', 2.80, 2.95, 0.30, 0.04, 0.35)
    drop('soap', 3.10, 3.24, 0.25, 0.06, 0.3)

    # ===== Z1 a2 (3.7-7.4): U drawer around the trap, dishwasher racks
    bs = tl.anims['b_sink']
    fU = drawer_fn(3.85, 4.70, (0, -0.42, 0), base=bs, out=0.18)
    tl.custom('sink_dr', fU)
    ev(3.95, 'u_open', 0.5, 'swish'); ev(4.87, 'u_shut', 0.75, 'thud')
    def bottles(t):
        if t < 4.02:
            return I, False
        u = c01((t - 4.02) / 0.40)
        z = 0.30 * (1 - u * u) if u < 1 else 0.012 * math.exp(-(t - 4.42) / 0.06) * abs(math.sin(math.pi * (t - 4.42) / 0.1))
        return fU(t)[0] @ T(0, 0, z), True
    tl.custom('sink_bot', bottles)
    for k in range(4):
        ev(4.12 + 0.1 * k, 'bottle', 0.3, 'tick')
    bdw = tl.anims['b_dw']
    hinge_dw = np.array([0.0, FB, 0.102])

    def dw_door(t):
        B, v = bdw(t)
        if t < 5.30:
            return B, v
        if t < 6.70:
            return about(hinge_dw, R('x', math.radians(88) * eob(c01((t - 5.30) / 0.25), 0.6))), True
        u = c01((t - 6.70) / 0.22)
        return about(hinge_dw, R('x', math.radians(88) * (1 - u * u))), True
    tl.custom('dw_door', dw_door)
    ev(5.50, 'dw_open', 0.6, 'thud'); ev(6.92, 'dw_shut', 0.8, 'thud')
    for k in range(2):
        f = drawer_fn(5.62 + 0.12 * k, 6.35 + 0.10 * (1 - k), (0, -0.50, 0), base=bdw, out=0.18)
        tl.custom(f'dw_rack{k}', f)
        ev(5.75 + 0.12 * k, f'dw_rack{k}', 0.35, 'tick')
    ev(6.58, 'racks_in', 0.4, 'swish')

    # ===== Z2 a3 (7.7-10.9): uppers, hood, duct, jars, kettle, tea
    from_camera('up_narrow', 7.55, 7.75, cam3, 0.35, 0.8, 'thud')
    from_camera('up_two', 7.75, 7.95, cam3, 0.35, 0.8, 'thud')
    from_camera('up_pull', 7.95, 8.15, cam3, 0.35, 0.8, 'thud')
    up2 = tl.anims['up_two']
    for nm in ('pull_flap', 'pull_bk'):
        ride(nm, tl.anims['up_pull'])
    fly('oshelf', 8.05, 8.24, (0.5, 0, 0.1), 0.05, 0.5, 'thud')
    drop('hood', 8.20, 8.35, 0.35, 0.02, 0.7, 'thud')
    grow('duct', 8.55, 8.85, 'z', (0, 0, 1.72), 0.4, 'swish')
    slide('jshelf', 8.80, 8.96, (0, -0.5, 0), 1.0, 0.4)
    for k in range(6):
        drop(f'jar{k}', 8.98 + 0.14 * k, 9.10 + 0.14 * k, 0.22, 0.06, 0.32)
    drop('kettle', 9.94, 10.10, 0.30, 0.04, 0.5, 'thud')
    drop('tea', 10.26, 10.40, 0.25, 0.05, 0.35)
    drop('mugs2', 10.42, 10.54, 0.22, 0.05, 0.3)
    drop('herb', 10.58, 10.70, 0.25, 0.06, 0.3)

    # ===== Z2 a4 (11.2-14.6): two-door cupboard, utensil rail, oils + plant
    door_oc('ud_L', (XSINK[0] + 0.003, UY + 0.02, 0), math.radians(-100), 11.35, 12.05, base=up2)
    door_oc('ud_R', (XSINK[1] - 0.003, UY + 0.02, 0), math.radians(100), 11.38, 12.08, base=up2, snd=False)
    drop('up_plates', 11.50, 11.64, 0.22, 0.03, 0.45)
    drop('up_bowls', 11.72, 11.86, 0.22, 0.04, 0.4)
    slide('rail', 12.36, 12.50, (0, -0.4, 0), 1.0, 0.4)
    def utens(t):
        if t < 12.55:
            return I, False
        u = c01((t - 12.55) / 0.5)
        return T(0, 0, 0.25 * (1 - eob(u, 1.1))), True
    tl.custom('utens', utens)
    for k in range(4):
        ev(12.65 + 0.14 * k, 'utensil', 0.3, 'tick')
    drop('oils', 13.30, 13.44, 0.25, 0.05, 0.35)
    drop('herb2', 13.62, 13.76, 0.22, 0.05, 0.35)
    drop('cplant', 13.96, 14.10, 0.22, 0.06, 0.35)
    drop('board', 14.24, 14.38, 0.25, 0.04, 0.35)

    # ===== Z3 a5 (14.9-18.2): corner shelves
    door_oc('cor_door', (XCOR[0] + 0.003, FB, 0), math.radians(-105), 15.05, 17.62, base=base_cor)

    def kidney(t_out, t_back):
        out = np.array([-0.28, -0.58, 0.0])

        def f(t):
            if t < t_out:
                return I, False
            if t < t_back:
                u = c01((t - t_out) / 0.45)
                a = eoc(min(1.0, u * 2)); b = eob(max(0.0, u * 2 - 1), 1.2)
                return T(out[0] * a, out[1] * b, 0), True
            u = c01((t - t_back) / 0.32)
            a = 1 - smooth(max(0.0, u * 2 - 1)); b = 1 - smooth(min(1.0, u * 2))
            return T(out[0] * a, out[1] * b, 0), t < t_back + 0.32
        return f
    for k in range(2):
        f = kidney(15.20 + 0.10 * k, 17.12 + 0.08 * k)
        tl.custom(f'cs{k}', f)
        ev(15.65 + 0.10 * k, f'cs{k}_out', 0.45, 'swish')
        g = drop(f'pots{k}', 15.95 + 0.35 * k, 16.10 + 0.35 * k, 0.30, 0.04, 0.5, 'thud', parent=f)
        tl.anims[f'pots{k}'] = (lambda g, f: (lambda t: (g(t)[0], g(t)[1] and f(t)[1])))(g, f)
    ev(17.45, 'cs_back', 0.4, 'swish')

    # ===== Z3 a6 (18.5-21.9): the fridge
    hinge_fr = np.array([TX, FRI[0] + 0.002, 0])

    def frd(t):
        if t < 18.60:
            return I, True
        if t < 20.90:
            return about(hinge_fr, R('z', math.radians(110) * eob(c01((t - 18.60) / 0.35), 0.8))), True
        u = c01((t - 20.90) / 0.20)
        if u < 1:
            return about(hinge_fr, R('z', math.radians(110) * (1 - u * u))), True
        tau = t - 21.10
        return about(hinge_fr, R('z', math.radians(1.2) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08)))), True
    tl.custom('fr_door', frd)
    ev(18.70, 'fr_open', 0.5, 'swish'); ev(21.10, 'fr_shut', 0.8, 'thud')
    for k in range(4):
        fly(f'fr_c{k}', 19.00 + 0.33 * k, 19.20 + 0.33 * k, (-0.45, 0, 0.05), 0.05, 0.4, 'tick')
    g = drop('fr_bins', 20.30, 20.50, 0.25, 0.04, 0.4, 'tick', parent=frd)
    for k in range(2):
        ev(20.62 + 0.14 * k, 'bin_fill', 0.3, 'tick')

    # ===== Z4 a7 + a8 (22.2-28.2): the larder
    door_oc('lar_door', (TX, LAR[0] + 0.002, 0), math.radians(115), 22.35, 27.55, out=0.22)
    for k in range(5):
        f = drawer_fn(22.50 + 0.15 * k, 27.30 - 0.12 * k, (-0.42, 0, 0), out=0.16)
        tl.custom(f'lar_dr{k}', f)
        ev(22.62 + 0.15 * k, f'lar_dr{k}_out', 0.3, 'tick')
        t_fill = (23.30 + 0.32 * k) if k < 4 else 25.80
        drop(f'lar_c{k}', t_fill - 0.14, t_fill, 0.28, 0.04, 0.45, 'tick', parent=f)
    ev(26.05, 'oats', 0.3, 'tick')
    ev(27.72, 'lar_shut2', 0.6, 'thud')

    # ===== Z5 a9 (28.5-31.9): wow, the kitchen becomes a desk
    def lid_path(name, t0, t1, dz=0.10, dy=-0.45):
        def f(t):
            if t < t0:
                return I, False
            u = (t - t0) / (t1 - t0)
            if u < 1:
                a = eoc(min(1.0, u / 0.6)); b = smooth(max(0.0, (u - 0.5) / 0.5))
                return T(0, dy * (1 - a), dz * (1 - b)), True
            tau = t - t1
            return T(0, 0, 0.006 * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))), True
        tl.custom(name, f)
        ev(t1, name, 0.8, 'thud')
        return f
    lid_path('lid_hob', 28.85, 29.10)
    ls0 = lid_path('lid_sink', 29.10, 29.35)

    def lid_sink(t):
        M, v = ls0(t)
        if t < 29.40:
            return M, v
        return T(0, -0.245 * eob(c01((t - 29.40) / 0.16), 1.0), 0), True
    tl.custom('lid_sink', lid_sink)
    ev(29.55, 'ledge', 0.45, 'swish')
    d_bed = np.array([STOOL_BED[0] - STOOL_DESK[0], STOOL_BED[1] - STOOL_DESK[1], 0.0])

    def stool(t):
        if t < 29.60:
            return T(*d_bed), True
        if t < 30.05:
            u = (t - 29.60) / 0.45
            return T(*(d_bed * (1 - smooth(u)))) @ about((*STOOL_DESK, 0), R('z', 0.9 * math.sin(math.pi * u))), True
        tau = t - 30.05
        return about((*STOOL_DESK, 0), R('z', 0.05 * math.exp(-tau / 0.1) * math.sin(2 * math.pi * tau / 0.25))), True
    tl.custom('stool', stool)
    ev(30.05, 'stool', 0.7, 'thud')
    pc = np.array([STOOL_DESK[0], STOOL_DESK[1], SEAT])

    def stool_top(t):
        if t < 29.45:
            return T(*d_bed), True
        if t < 29.60:
            u = (t - 29.45) / 0.15
            return T(*d_bed) @ T(0, 0, 0.12 * u) @ about(pc, S(*([1 - u] * 3))), True
        return I, False
    tl.custom('stool_top', stool_top)
    on_cover = lambda t: (lid_sink(t)[0] @ T(0, 0.245, 0), True)
    for nm, t0, t1 in (('laptop', 29.66, 29.80), ('lamp', 29.86, 30.00), ('mug', 30.76, 30.90)):
        drop(nm, t0, t1, 0.25, 0.04, 0.45 if nm != 'mug' else 0.3, 'thud' if nm != 'mug' else 'tick',
             parent=(on_cover if nm != 'lamp' else None))
    sit = COOK.sit_pose(SEAT, base='sit_desk')
    look_up = dict(sit, neck=-30, neck_turn=-18, spine=4)
    stretch = dict(sit, sh_l=160, sh_r=160, sh_l_out=14, sh_r_out=14, elbow_l=30, elbow_r=30, spine=-4, neck=-14)
    look_win = dict(sit, neck_turn=-50, neck=4)
    COOK.animate(tl, pose=fg.track([(32.45, sit), (32.85, look_up), (34.10, look_up), (34.50, sit),
                                    (43.85, sit), (44.30, stretch), (44.90, stretch), (45.35, look_win)]), pop=30.30)

    # ===== Z5 a10 (32.2-34.95): the pull-down
    pu = tl.anims['up_pull']
    hinge_pf = np.array([0.0, UY, UZ1])

    def flap(t):
        B, v = pu(t)
        if t < 32.25:
            return B, v
        if t < 34.15:
            return about(hinge_pf, R('x', math.radians(-84) * eob(c01((t - 32.25) / 0.22), 0.5))), True
        u = c01((t - 34.15) / 0.18)
        return about(hinge_pf, R('x', math.radians(-84) * (1 - u * u))), True
    tl.custom('pull_flap', flap)
    ev(32.30, 'flap_up', 0.35, 'swish'); ev(34.33, 'flap_shut', 0.6, 'thud')

    def basket(t):
        B, v = pu(t)
        if t < 32.35:
            return B, v
        if t < 33.60:
            k = smooth(c01((t - 32.35) / 0.45))
            tau = t - 32.80
            if tau > 0:
                k += 0.03 * math.exp(-tau / 0.08) * math.sin(2 * math.pi * tau / 0.18)
        else:
            u = c01((t - 33.60) / 0.40)
            k = 1 - eob(u, 1.6)
        return T(0, -0.12 * k, -0.42 * k), True
    tl.custom('pull_bk', basket)
    ev(32.80, 'pull_down', 0.6, 'swish')
    tl.events.append(dict(t=34.0, name='boing', strength=0.6, kind='boing'))

    # ===== Z6 a11 + a12 (34.95-41.35): bed drawers, over-bed cupboard
    for k in range(3):
        f = drawer_fn(35.25 + 0.12 * k, 36.80 + 0.18 * k, (0.45, 0, 0), out=0.18)
        tl.custom(f'bed_dr{k}', f)
        ev(35.35 + 0.12 * k, f'bed_dr{k}_out', 0.4, 'swish' if k == 0 else 'tick')
        drop(f'bed_c{k}', 35.56 + 0.30 * k, 35.70 + 0.30 * k, 0.30, 0.05, 0.45, 'tick', parent=f)
        ev(37.00 + 0.18 * k, f'bed_dr{k}_shut', 0.55, 'thud')
    drop('ob_cab', 37.42, 37.60, 0.45, 0.02, 0.8, 'thud')
    obc = tl.anims['ob_cab']
    for i, nm in enumerate(('ob_flapA', 'ob_flapB')):
        door_oc(nm, (0.34, 0, UZ1), math.radians(-100), 38.60 + 0.08 * i, 39.22 + 0.08 * i, base=obc, axis='y', out=0.2,
                snd=(i == 0))
    ride('ob_bedding', obc)
    def books(t):
        if t < 39.50:
            return I, False
        u = c01((t - 39.50) / 0.55)
        return T(0.45 * (1 - eob(u, 0.8)), 0, 0), True
    tl.custom('ob_books', books)
    for k in range(5):
        ev(39.62 + 0.15 * k, 'book', 0.3, 'tick')
    drop('ob_plant', 40.46, 40.60, 0.25, 0.06, 0.4)
    drop('bedlight', 40.86, 41.00, 0.20, 0.04, 0.35)

    # ===== Z7 a13 (41.35-46.0): lights on, late beats
    appear('led_up', 41.90); ev(41.90, 'led_on', 0.7, 'chime')
    appear('led_jar', 42.10); ev(42.10, 'jar_on', 0.45, 'chime')
    appear('hood_on', 42.40); ev(42.40, 'hood_on', 0.5, 'chime')
    appear('lamp_on', 42.60); ev(42.60, 'lamp_on', 0.45, 'chime')
    appear('bedlight_on', 42.80); ev(42.80, 'bed_on', 0.55, 'chime')
    tl.custom('dimmer', lambda t: (T(0.12 * smooth(c01((t - 41.60) / 0.6)), 0, 0), False))
    ev(44.30, 'stretch', 0.3, 'swish')
    drop('vase', 44.64, 44.80, 0.25, 0.06, 0.4)


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    timeline().export(DUR, camera, lights, out)
