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
    wood_mats('oak', srgb(212, 180, 140), seed=3.0)
    wood_mats('birch', srgb(228, 208, 174), seed=8.0)
    mat('groove', col=srgb(170, 150, 120))
    mat('tile', tex=12, col=srgb(172, 194, 168), col2=srgb(232, 234, 228), rough=0.18, f0=0.04, glossy=True,
        p=(0.075, 0.30, 0.0022, 1, 0.0))
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
                  ('tin_red', (196, 66, 52)), ('teal', (58, 140, 140)), ('pot_blue', (70, 112, 176)),
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
    fg.materials(['fig_adult'])


# ------------------------------------------------------------------------------------------- helpers
def disc(inst, c, r, z0, z1, m, n=28):
    add(inst, lathe(rprof(r, z0, z1, min(0.004, (z1 - z0) * 0.45), 3), n, c), m)


def jar(inst, x, y, z, r, h, fill, lid='cork', frac=0.75):
    add(inst, lathe([(0, z), (r, z), (r + 0.003, z + 0.01), (r + 0.003, z + h), (r - 0.004, z + h + 0.004), (0, z + h + 0.004)], 22, (x, y)), 'jar')
    add(inst, lathe([(0, z + 0.008), (r - 0.002, z + 0.008), (r - 0.002, z + h * frac), (0, z + h * frac)], 18, (x, y)), fill)
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
    if back:
        add(inst, box(x0, y1 - t, z0, x1, y1, z1), m)
    if bottom:
        add(inst, box(x0, y0, z0, x1, y1, z0 + t), m)
    if top:
        add(inst, box(x0, y0, z1 - t, x1, y1, z1), m)


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
    add('room', box(TX + 0.02, FRI[0], 0.10, W, FRI[1], UZ1 - 0.10), 'white_in')               # fridge body (behind door)
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
    wood(nm, XDW[0] + 0.003, FB, 0.102, XDW[1] - 0.003, FB + 0.02, CB - 0.004, 'oak')
    add(nm, box(XDW[0] + 0.02, FB - 0.006, CB - 0.05, XDW[1] - 0.02, FB, CB - 0.035), 'groove')
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
    for (z0, z1) in ((0.102, 0.66), (0.66, CB - 0.004)):
        wood(nm, XSINK[0] + 0.003, FB, z0 + 0.0015, XSINK[1] - 0.003, FB + 0.02, z1 - 0.0015, 'oak')
        add(nm, box(XSINK[0] + 0.06, FB - 0.005, z1 - 0.03, XSINK[1] - 0.06, FB, z1 - 0.018), 'groove')
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
    add(nm, box(x0 + 0.003, UY, UZ0 + 0.002, x1 - 0.003, UY + 0.02, UZ1 - 0.002), 'white_cab')
    add(nm, box(x0 + 0.06, UY - 0.006, UZ0 + 0.01, x1 - 0.06, UY, UZ0 + 0.025), 'groove')
    # open corner shelves over the blind corner (x 3.40-4.0)
    for k, z in enumerate((1.50, 1.86, 2.22)):
        wood('oshelf', TX + 0.01, 3.02, z, W - 0.002, D - 0.012, z + 0.025, 'oak')
    add('oshelf', box(TX + 0.004, 3.02, 1.50, TX + 0.022, D - 0.012, UZ1), 'white_cab')
    # hood (matte white, underside 1.55) + telescoping duct into the bulkhead
    hx0, hx1 = XHOB
    add('hood', box(hx0 + 0.004, 3.08, 1.55, hx1 - 0.004, D - 0.012, 1.72), 'white_cab')
    add('hood', box(hx0 + 0.03, 3.10, 1.548, hx1 - 0.03, D - 0.04, 1.552), 'grille')
    add('hood', box(hx0 + 0.20, 3.07, 1.60, hx1 - 0.20, 3.08, 1.66), 'groove')
    add('duct', box(1.68, 3.18, 1.72, 1.90, 3.42, UZ1), 'steel_x')
    for z in (1.98, 2.24):
        add('duct', box(1.676, 3.176, z, 1.904, 3.424, z + 0.012), 'steel')
    # LED pieces that switch on
    add('led_up', box(XDW[0] + 0.03, UY + 0.03, UZ0 - 0.004, XDW[1] - 0.03, UY + 0.05, UZ0 - 0.001), 'led')
    add('led_up', box(XCOR[0] + 0.03, UY + 0.03, UZ0 - 0.004, XCOR[1] - 0.03, UY + 0.05, UZ0 - 0.001), 'led')
    add('led_jar', box(XSINK[0] + 0.04, UY + 0.03, 1.744, XSINK[1] - 0.04, UY + 0.06, 1.7475), 'led')
    add('hood_on', box(hx0 + 0.12, 3.20, 1.546, hx1 - 0.12, 3.26, 1.5485), 'led')
    # late props
    plant('herb', 3.54, 3.26, 1.525, 0.055, 0.09, rng, 9, pot_m='ceramic')
    plant('herb2', 3.52, 3.30, 1.885, 0.045, 0.075, rng, 8, pot_m='mug_sage')
    jar('herb2', 3.74, 3.30, 1.885, 0.04, 0.16, 'pasta')
    add('board', xform(rbox((0, 0, 0.17), (0.28, 0.018, 0.34), 0.008, 3), T(3.04, 3.44, CT) @ R('x', -0.12)), 'board')
    add('board', xform(rbox((0, 0, 0.13), (0.22, 0.018, 0.26), 0.008, 3), T(3.22, 3.43, CT) @ R('x', -0.10)), 'oak_z')
    # kettle on the worktop over the blind corner
    kx, ky = 3.56, 3.12
    add('kettle', lathe([(0, CT), (0.07, CT), (0.085, CT + 0.06), (0.08, CT + 0.16), (0.05, CT + 0.20), (0.02, CT + 0.21),
                         (0.02, CT + 0.22), (0, CT + 0.22)], 28, (kx, ky)), 'enamel')
    add('kettle', tube([(kx - 0.06, ky, CT + 0.17), (kx - 0.02, ky, CT + 0.26), (kx + 0.04, ky, CT + 0.25), (kx + 0.07, ky, CT + 0.17)], 0.008, 8), 'oak_x')
    add('kettle', tube([(kx + 0.07, ky, CT + 0.10), (kx + 0.13, ky, CT + 0.17)], 0.011, 8), 'enamel')


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
        add(nm, box(x0, y0, z, x1, y1, z + 0.012), 'white_in')
        for b in (box(x0, y0, z, x1, y0 + 0.012, z + 0.11), box(x0, y1 - 0.012, z, x1, y1, z + 0.11), box(x1 - 0.012, y0, z, x1, y1, z + 0.11)):
            add(nm, b, 'white_in')
        wood(nm, x0, y0, z, x0 + 0.016, y1, z + 0.13, 'oak')
        cn = f'lar_c{k}'
        zz = z + 0.012
        if fills[k][0] == 'tins':
            for i, yy in enumerate(np.linspace(y0 + 0.07, y1 - 0.07, 4)):
                for j, xx in enumerate((x0 + 0.10, x0 + 0.21, x0 + 0.32, x0 + 0.43)):
                    tin(cn, xx, yy, zz, 0.036, 0.10, ('tin_blue', 'tin_green', 'tin_yel', 'tin_red')[(i + j) % 4])
        else:
            for i, yy in enumerate(np.linspace(y0 + 0.08, y1 - 0.08, 3)):
                for j, xx in enumerate((x0 + 0.11, x0 + 0.26, x0 + 0.41)):
                    jar(cn, xx, yy, zz, 0.05, 0.16 + (0.04 if k == 0 else 0.0), fills[k][(i + j) % 2])


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
    add('dimmer', box(-5.0, -5.0, -5.0, -4.99, -4.99, -4.99), 'white_in')        # hidden; its x offset = daylight dip
    global COOK
    COOK = fg.Figure('cook', 'adult')
    COOK.build(COOK.sit_pose(SEAT, base='sit_desk'), at=(STOOL_DESK[0], STOOL_DESK[1] + 0.02, 0.0), seat=SEAT)


COOK = None

# ------------------------------------------------------------------------------------------- camera
VFOV = 85.0


def P(x, y, z, yaw, pitch):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch)


P1 = P(1.95, 0.20, 1.32, -2.0, -7.0)                                                  # frame 1 (and the loop end)
S1 = (P1, P(1.95, 0.80, 1.28, 2.0, -8.0))                                             # doorway push-in on the birch wall
S2 = (P(1.80, 1.05, 1.45, -6.0, -6.0), P(2.70, 0.95, 1.45, 10.0, -7.0))                # cooking run, slide east
S3 = (P(1.15, 0.45, 1.50, 42.0, -14.0), P(1.45, 0.25, 1.46, 22.0, -12.0))             # larder + desk, orbit
S4 = (P(1.95, -0.60, 1.373, -7.33, -5.67), P1)                                         # wide, drifts into frame 1
HOLDS = [(0.0, 3.0, S1), (3.3, 7.0, S2), (7.3, 10.7, S3), (11.0, DUR_CUT, S4)]
DUR = float(len(HOLDS)) if REST else DUR_CUT

camera = hold_camera(HOLDS, VFOV, rest=REST)

# ------------------------------------------------------------------------------------------- lights (fixed slots)
LSKY = (9.0, 9.6, 10.6)
LSUN = (62000.0, 58500.0, 52000.0)
LDOOR = (2.2, 2.2, 2.15)
LBOUNCE = (1.1, 1.1, 1.08)
LNICHE = (5.0, 5.0, 4.9)
LUP = (60.0, 53.0, 41.0)
LJAR = (52.0, 46.0, 35.0)
LHOOD = (520.0, 470.0, 370.0)
LLAMP = (110.0, 88.0, 58.0)


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
    Ls.append(rect_light((KX0 + 0.05, NY + 0.02, UZ1 - 0.004), (W - KX0 - 0.1, 0, 0), (0, 0.24, 0), LNICHE))  # 5 niche (down)
    up = vis.get('led_up')
    Ls.append(rect_light((XDW[0] + 0.03, UY + 0.03, UZ0 - 0.005), (0, 0.02, 0), (XDW[1] - XDW[0] - 0.06, 0, 0), k(LUP, up)))   # 6
    Ls.append(rect_light((XCOR[0] + 0.03, UY + 0.03, UZ0 - 0.005), (0, 0.02, 0), (XCOR[1] - XCOR[0] - 0.06, 0, 0), k(LUP, up)))  # 7
    Ls.append(rect_light((XSINK[0] + 0.04, UY + 0.03, 1.743), (0, 0.03, 0), (XSINK[1] - XSINK[0] - 0.08, 0, 0), k(LJAR, vis.get('led_jar'))))  # 8
    Ls.append(spot_rect(((XHOB[0] + XHOB[1]) / 2, 3.23, 1.545), (0, 0, -1), 0.08, k(LHOOD, vis.get('hood_on')), 3.0))  # 9 hood
    Ls.append(sphere_light((1.66, 3.30, CT + 0.345), 0.022, k(LLAMP, vis.get('lamp_on'))))                    # 10 desk lamp
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
    panels_anim(tl, [(0.10, 0.0, 0.0), (0.42, 90.0, 0.0), (0.46, 90.0, 0.0), (0.64, 90.0, SLIDE_IN),
                     (13.75, 90.0, SLIDE_IN), (13.92, 90.0, 0.0), (14.40, 0.0, 0.0)],
                clacks=[(0.16, 0.55, 140), (0.24, 0.6, 160), (0.32, 0.65, 180), (0.40, 0.7, 200),
                        (13.98, 0.7, 200), (14.12, 0.65, 180), (14.26, 0.6, 160), (14.40, 0.75, 120)])
    ev(0.64, 'pocket', 0.35, 'swish')
    # ---- sage tiles slap onto the back wall right to left (0.30-1.00)
    for i, k in enumerate(range(9, -1, -1)):
        t1 = 0.30 + 0.078 * i
        from_camera(f'tile{k}', t1 - 0.14, t1, cam_s1, 0.22, 0.25, 'tick')
    # ---- base units grow out of the back wall (1.05-1.65)
    for i, nm in enumerate(('b_dw', 'b_hob', 'b_sink', 'b_corner')):
        grow(nm, 0.92 + 0.15 * i, 1.08 + 0.15 * i, 'y', (0, D, 0), 0.75)
    base_cor = tl.anims['b_corner']
    drop('worktop', 1.68, 1.85, 0.40, 0.02, 0.9, 'thud')
    drop('sink', 2.02, 2.15, 0.30, 0.03, 0.5, 'thud')
    drop('hob', 2.16, 2.30, 0.30, 0.03, 0.6, 'thud')
    drop('fruit', 2.38, 2.55, 0.35, 0.05, 0.4)
    drop('tap', 2.60, 2.75, 0.30, 0.04, 0.35)

    # ---- S2: uppers, hood, duct, jars, two-door cupboard, corner shelves
    from_camera('up_narrow', 3.30, 3.52, cam_s2, 0.35, 0.8, 'thud')
    from_camera('up_two', 3.40, 3.64, cam_s2, 0.35, 0.8, 'thud')
    from_camera('up_pull', 3.52, 3.76, cam_s2, 0.35, 0.8, 'thud')
    up2 = tl.anims['up_two']
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
    lar = door_oc('lar_door', (TX, LAR[0] + 0.002, 0), math.radians(115), 7.35, 8.80, out=0.22)
    for k in range(5):
        f = drawer_fn(7.45 + 0.1 * k, 8.70 - 0.1 * k, (-0.42, 0, 0), out=0.16)
        tl.custom(f'lar_dr{k}', f)
        ev(7.55 + 0.1 * k, f'lar_dr{k}_out', 0.3, 'tick')
        drop(f'lar_c{k}', 7.53 + 0.15 * k, 7.65 + 0.15 * k, 0.25, 0.04, 0.4, 'tick', parent=f)
    ev(8.87, 'lar_dr_shut', 0.6, 'thud')

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
    lid_path('lid_hob', 8.40, 8.65)
    ls0 = lid_path('lid_sink', 8.60, 8.85)

    def lid_sink(t):
        M, v = ls0(t)
        if t < 8.90:
            return M, v
        if t < 11.00:
            return T(0, -0.245 * eob(c01((t - 8.90) / 0.16), 1.0), 0), True
        return T(0, -0.245 * (1 - smooth(c01((t - 11.00) / 0.15))), 0), True
    tl.custom('lid_sink', lid_sink)
    ev(9.00, 'ledge', 0.45, 'swish'); ev(11.15, 'ledge_back', 0.5, 'thud')
    # stool: bed head -> desk -> bed head (the book on it hops off while it is the desk seat)
    d_bed = np.array([STOOL_BED[0] - STOOL_DESK[0], STOOL_BED[1] - STOOL_DESK[1], 0.0])

    def stool(t):
        if t < 9.00:
            return T(*d_bed), True
        if t < 9.45:
            u = (t - 9.00) / 0.45
            return T(*(d_bed * (1 - smooth(u)))) @ about((*STOOL_DESK, 0), R('z', 0.9 * math.sin(math.pi * u))), True
        if t < 11.05:
            tau = t - 9.45
            return about((*STOOL_DESK, 0), R('z', 0.05 * math.exp(-tau / 0.1) * math.sin(2 * math.pi * tau / 0.25))), True
        u = c01((t - 11.05) / 0.40)
        return T(*(d_bed * smooth(u))) @ about((*STOOL_DESK, 0), R('z', -0.7 * math.sin(math.pi * u))), True
    tl.custom('stool', stool)
    ev(9.45, 'stool', 0.7, 'thud'); ev(11.45, 'stool_back', 0.6, 'thud')

    pc = np.array([STOOL_DESK[0], STOOL_DESK[1], SEAT])

    def stool_top(t):
        if t < 8.80:
            return T(*d_bed), True
        if t < 8.95:
            u = (t - 8.80) / 0.15
            return T(*d_bed) @ T(0, 0, 0.12 * u) @ about(pc, S(*([1 - u] * 3))), True
        if t < 11.47:
            return I, False
        u = (t - 11.47) / 0.15
        if u < 1:
            return T(*d_bed) @ T(0, 0, 0.12 * (1 - u)) @ about(pc, S(*([0.2 + 0.8 * u] * 3))), True
        return T(*d_bed), True
    tl.custom('stool_top', stool_top)
    ev(8.88, 'book_off', 0.25, 'tick'); ev(11.62, 'book_back', 0.3, 'tick')
    on_cover = lambda t: (lid_sink(t)[0] @ T(0, 0.245, 0), True)
    for nm, t0, t1 in (('laptop', 9.02, 9.15), ('lamp', 9.16, 9.30), ('mug', 9.72, 9.85)):
        drop(nm, t0, t1, 0.25, 0.04, 0.45 if nm != 'mug' else 0.3, 'thud' if nm != 'mug' else 'tick',
             parent=(on_cover if nm != 'lamp' else None))
    # the figure pops in seated, turns its head to the window, is hidden during the swing
    sit = COOK.sit_pose(SEAT, base='sit_desk')
    look = dict(sit, neck_turn=-55, neck=4)
    COOK.animate(tl, pose=fg.track([(10.05, sit), (10.40, look)]), visible=lambda t: t < 10.75, pop=9.60)

    # ---- S4: put back, lights on, then the wall closes and the room returns to frame 1
    drop('herb', 11.18, 11.30, 0.25, 0.06, 0.35)
    appear('led_up', 11.60, 14.40); ev(11.60, 'led_on', 0.7, 'chime')
    appear('led_jar', 11.80, 14.40); ev(11.80, 'jar_on', 0.5, 'chime')
    appear('hood_on', 12.00, 14.40); ev(12.00, 'hood_on', 0.5, 'chime')
    appear('lamp_on', 11.90, 14.40); ev(11.90, 'lamp_on', 0.5, 'chime')
    tl.custom('dimmer', lambda t: (T(0.12 * smooth(c01((t - 11.45) / 0.5)) * (1 - smooth(c01((t - 13.85) / 0.55))), 0, 0), False))
    drop('board', 12.26, 12.40, 0.25, 0.04, 0.4)
    drop('kettle', 12.64, 12.80, 0.30, 0.04, 0.45, 'thud')
    drop('herb2', 13.06, 13.20, 0.22, 0.05, 0.35)


def timeline_rest(tl):
    I = np.eye(4)
    for k, M in enumerate(panel_mats(math.pi / 2, SLIDE_IN)):
        tl.custom(f'pan{k}', lambda t, M=M: (M, True))
    for nm in ('led_up', 'led_jar', 'hood_on', 'lamp_on'):
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
    raise NotImplementedError('long cut: built after the 15 s cut')


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    timeline().export(DUR, camera, lights, out)
