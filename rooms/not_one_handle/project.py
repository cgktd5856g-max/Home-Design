"""Not One Handle in Sight: a 9.6 m² bedroom (3.0 x 3.2 m) of flush white push-latch panels with a walk-in closet
behind the west wall. Neutral white + light oak + olive bedding (the one accent); colour from filled storage.
No on-screen text.

    ROOM_REST=1 python3 pipeline/run.py rooms/not_one_handle/project.py <workdir> probe 0.5,1.5,2.5,3.5,4.5,5.5
    python3 pipeline/run.py rooms/not_one_handle/project.py <workdir> preview            # 15 s cut (default)
    ROOM_CUT=long python3 pipeline/run.py ...                                              # 44 s long cut

Units: metres. x = east, y = north, z = up. Room x 0..W, y 0..D, z 0..H.
West: the walk-in block (x 0..1.0, y 1.2..3.2) on a 12 cm platform; aisle face at x = 1.0, south face at y = 1.2.
North: bed head (bed x 1.8..3.0, y 1.0..3.0 on a 0.45 m drawer platform), headboard shelf y 3.0..3.2.
East: window over the bed. South: room door (x 0.1..0.9) in the entry corner; wall unit x 1.75..3.0 with the
fold-down desk and the pull-down rack; oak bench at the bed foot (the desk seat).
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
from camkit import hold_camera, lerp_cam
import figure as fg

REST = os.environ.get('ROOM_REST') == '1'
CUT = os.environ.get('ROOM_CUT', '15')
LONG = CUT == 'long'

W, D, H = 3.0, 3.2, 2.7
FPS = 25
DUR = 6.0 if REST else (44.0 if LONG else 15.0)

PZ = 0.12                     # closet platform height
CX = 1.0                      # closet aisle face (front of the panels)
CY = 1.2                      # closet south face (front of the panels, facing -y)
PT = 2.515                    # panel tops
PNT = 0.02                    # panel thickness
WY0, WY1, WZ0, WZ1 = 1.6, 2.8, 1.0, 2.3          # east window opening
BX0, BX1, BY0, BY1, BZ = 1.8, 3.0, 1.0, 3.0, 0.45  # bed platform
SU0, SUY = 1.75, 0.22         # south wall unit x0 and depth (front face at y = SUY)
DK0, DK1, DKZ, DKD = 1.79, 2.96, 0.76, 0.42       # desk panel x range, hinge height, depth (folds down)
BN = (1.8, 3.0, 0.66, 1.0, 0.45)                  # bench x0, x1, y0, y1, top
RACK_PZ, RACK_R, RACK_A = 1.66, 0.45, math.radians(105)
SUN_DIR = np.array([-0.85, -0.25, -0.42]) / np.linalg.norm([-0.85, -0.25, -0.42])
CAPTIONS = []

# aisle face panels (y ranges) and south face panels (x ranges)
AISLE = dict(pn_a1=(1.2, 1.85), doorA=(1.85, 2.55), pn_bed=(2.55, 3.2))
SOUTHF = dict(pn_s1=(0.0, 0.30), mirror=(0.30, 1.0))
LEDGE = (2.63, 3.12, 0.62, 0.92)                  # bedside flap y0, y1, z0, z1 (bottom-hinged, flips down to a ledge)
TK = dict(tk1=(1.26, 1.80), tk2=(2.60, 3.14))     # toe-kick drawers in the platform front (y ranges)
BD = dict(bd1=(1.06, 1.97), bd2=(2.03, 2.94))     # bed drawers on the aisle side (y ranges)
RAIL_TOP, RAIL_BOT, RAIL_Y = 2.30, 1.26, 2.90


# ------------------------------------------------------------------------------------------- materials
def materials():
    mat('subfloor', tex=3, col=srgb(150, 147, 142), p=(0.12,))
    mat('floor', tex=1, col=srgb(208, 182, 148), col2=srgb(190, 162, 128), rough=0.38, f0=0.04, glossy=True, p=(0.18, 1.6))
    mat('wall', tex=3, col=srgb(236, 236, 234), p=(0.02,))
    mat('ceiling', col=srgb(246, 246, 245))
    mat('panel', col=srgb(243, 243, 241), rough=0.42, f0=0.04, glossy=True)
    mat('white_in', col=srgb(234, 234, 231))
    mat('gapc', col=srgb(128, 128, 126))
    wood_mats('oak', srgb(214, 184, 146), seed=3.0)
    wood_mats('birch', srgb(228, 210, 180), seed=8.0)
    mat('winframe', col=srgb(232, 232, 230), rough=0.4)
    mat('sill', col=srgb(240, 240, 238), rough=0.25, f0=0.04, glossy=True)
    mat('mirror', col=srgb(236, 237, 239), rough=0.02, metal=1)
    mat('olive', tex=3, col=srgb(128, 134, 98), rough=0.9, p=(0.05,))
    mat('olive_knit', tex=5, col=srgb(146, 150, 114), p=(0, 0.012))
    mat('linen_w', tex=3, col=srgb(240, 240, 236), rough=0.9, p=(0.04,))
    mat('throw_w', tex=5, col=srgb(238, 236, 230), p=(0, 0.012))
    mat('mattress', tex=5, col=srgb(246, 246, 243), p=(0, 0.02))
    mat('jute', tex=5, col=srgb(200, 178, 140), p=(0, 0.016))
    mat('alu', col=srgb(200, 202, 206), rough=0.3, metal=1)
    mat('steel', col=srgb(180, 182, 186), rough=0.25, metal=1)
    mat('kb', tex=10, col=srgb(52, 52, 56), p=(0.018,))
    mat('ceramic', col=srgb(242, 242, 238), rough=0.22, f0=0.04, glossy=True)
    mat('terra', col=srgb(200, 136, 104))
    mat('leaf', col=srgb(64, 112, 60)); mat('leaf2', col=srgb(96, 142, 74))
    mat('led', col=(0, 0, 0), emis=(7.0, 6.0, 4.4))
    mat('led_off', col=srgb(236, 236, 232))
    mat('bulb', col=(0, 0, 0), emis=(8.0, 6.9, 5.0))
    mat('shade', col=srgb(242, 240, 234), emis=(0.0, 0.0, 0.0), rough=0.9)
    mat('phone', col=srgb(20, 20, 22), rough=0.08, f0=0.05, glossy=True)
    mat('backdrop', tex=9, emis=(1.35, 1.35, 1.35), p=(1.0, 1.0))
    mat('suitcase', col=srgb(124, 172, 214), rough=0.3, f0=0.05, glossy=True)
    mat('blackm', col=srgb(30, 30, 32), rough=0.4)
    for nm, c in (('vac_teal', (64, 150, 150)), ('vac_plum', (124, 76, 112)), ('vac_grey', (176, 178, 184))):
        mat(nm, tex=3, col=srgb(*c), rough=0.3, f0=0.05, glossy=True, p=(0.08,))
    for nm, c in (('cl_teal', (46, 128, 130)), ('cl_plum', (118, 64, 100)), ('cl_mustard', (204, 164, 82)),
                  ('cl_sky', (132, 174, 218)), ('cl_charcoal', (62, 64, 70)), ('cl_white', (242, 242, 240)),
                  ('cl_denim', (88, 112, 150)), ('cl_olive', (140, 146, 98)), ('cl_rose', (210, 150, 150))):
        mat(nm, tex=5, col=srgb(*c), p=(2, 0.008))
    for nm, c in (('bk_teal', (54, 130, 132)), ('bk_mustard', (216, 170, 66)), ('bk_plum', (120, 70, 104)),
                  ('bk_sky', (138, 178, 216)), ('bk_white', (240, 238, 232)), ('bk_olive', (140, 148, 100)),
                  ('bk_charcoal', (60, 62, 68))):
        mat(nm, col=srgb(*c), rough=0.6)
    mat('box_blue', col=srgb(84, 124, 184), rough=0.55)
    mat('box_linen', tex=3, col=srgb(214, 208, 196), p=(0.06,))
    mat('bin_white', col=srgb(238, 238, 236), rough=0.5)
    mat('shoe_white', col=srgb(244, 244, 240), rough=0.5); mat('shoe_tan', col=srgb(186, 140, 98), rough=0.4, f0=0.04, glossy=True)
    mat('shoe_teal', col=srgb(60, 138, 140), rough=0.5)
    mat('print', tex=7, col=srgb(132, 140, 92), col2=srgb(236, 232, 222), p=(2, 0.12))
    mat('fig_denim', col=srgb(96, 120, 160), rough=0.48, f0=0.04)
    mat('fig_teal', col=srgb(56, 136, 138), rough=0.48, f0=0.04)


# ------------------------------------------------------------------------------------------- helpers
def disc(inst, c, r, z0, z1, m, n=28):
    add(inst, lathe(rprof(r, z0, z1, min(0.004, (z1 - z0) * 0.45), 3), n, c), m)


def garment(inst, x, y, z_top, length, width, m, along='x'):
    """Hanging garment on a rail running along `along` (width is across the rail)."""
    if along == 'x':
        add(inst, tube([(x, y - width * 0.45, z_top - 0.05), (x, y, z_top), (x, y + width * 0.45, z_top - 0.05)], 0.004, 6), 'steel')
        add(inst, rbox((x, y, z_top - 0.06 - length / 2), (0.04, width, length), 0.018, 3), m)
    else:
        add(inst, tube([(x - width * 0.45, y, z_top - 0.05), (x, y, z_top), (x + width * 0.45, y, z_top - 0.05)], 0.004, 6), 'steel')
        add(inst, rbox((x, y, z_top - 0.06 - length / 2), (width, 0.04, length), 0.018, 3), m)


def stack(inst, cx, cy, z0, size, mats_, n, rng):
    z = z0
    for i in range(n):
        sx, sy, sz = size
        jx, jy = rng.uniform(-0.008, 0.008, 2)
        add(inst, rbox((cx + jx, cy + jy, z + sz / 2), (sx * rng.uniform(0.95, 1.0), sy * rng.uniform(0.95, 1.0), sz), sz * 0.45, 3),
            mats_[i % len(mats_)])
        z += sz * 0.96


def plant(inst, cx, cy, z0, r, h, rng, n=9, pot='terra', leaf=1.0):
    add(inst, lathe([(0, z0), (r * 0.8, z0), (r, z0 + h), (r * 1.06, z0 + h + 0.006), (0, z0 + h + 0.006)], 20, (cx, cy)), pot)
    for k in range(n):
        a = 2 * math.pi * k / n + rng.uniform(-0.25, 0.25)
        lean = rng.uniform(0.3, 0.8)
        L = rng.uniform(0.07, 0.13) * (r / 0.05) * leaf
        c = np.array([cx + math.cos(a) * L * 0.4 * lean, cy + math.sin(a) * L * 0.4 * lean, z0 + h + L * 0.55])
        add(inst, xform(ellipsoid(c, (0.016 * (r / 0.05) ** 0.5, 0.016 * (r / 0.05) ** 0.5, L * 0.55), 7),
                        about(c, R('z', a) @ R('x', lean * 0.6))), 'leaf' if k % 2 else 'leaf2')


def tall_plant(inst, cx, cy, rng):
    """Floor plant: a ceramic pot and a fan of long leaves on thin stems."""
    add(inst, lathe([(0, 0), (0.12, 0), (0.15, 0.34), (0.158, 0.35), (0, 0.35)], 24, (cx, cy)), 'ceramic')
    for k in range(13):
        a = 2 * math.pi * k / 13 + rng.uniform(-0.2, 0.2)
        lean = rng.uniform(0.15, 0.55)
        h = rng.uniform(0.38, 0.72)
        tip = np.array([cx + math.cos(a) * lean * h * 0.55, cy + math.sin(a) * lean * h * 0.55, 0.35 + h])
        add(inst, tube([(cx, cy, 0.33), tuple((np.array([cx, cy, 0.33]) + tip) / 2 + np.array([0, 0, 0.04])), tuple(tip)], 0.006, 5), 'leaf')
        c = tip + np.array([math.cos(a) * 0.07, math.sin(a) * 0.07, 0.02])
        add(inst, xform(ellipsoid(c, (0.05, 0.012, 0.13), 8), about(c, R('z', a + math.pi / 2) @ R('y', lean * 1.4))),
            'leaf2' if k % 2 else 'leaf')


def cloth(inst, x0, x1, y0, y1, z_top, z_hem, r, m, seed, sides=('w', 'e', 's'), puff=0.012):
    """Draped fabric: a gently wrinkled top plus rounded edges falling into softly folded skirts."""
    ph = np.random.default_rng(seed).uniform(0, 6.283, 5)
    xc, hw = (x0 + x1) / 2, (x1 - x0) / 2

    def wob(x, y):
        return (0.009 * math.sin(x * 9 + ph[0]) * math.sin(y * 5 + ph[1]) + 0.005 * math.sin(x * 17 + y * 11 + ph[2])
                + puff * max(0.0, 1 - ((x - xc) / hw) ** 2))
    nx, ny = 34, 30
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
    """Puffy pillow: thick in the middle, pinched along the seam and at the corners. size = (width x, thickness y, height z)."""
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


def shoes(inst, cx, cy, z0, m, along='x'):
    """A pair of plain shoes side by side (toes pointing +x when along == 'x')."""
    for d in (-0.05, 0.05):
        if along == 'x':
            add(inst, ellipsoid((cx, cy + d, z0 + 0.03), (0.12, 0.045, 0.032), 10), m)
            add(inst, box(cx - 0.12, cy + d - 0.043, z0, cx + 0.115, cy + d + 0.043, z0 + 0.012), 'shoe_white')
        else:
            add(inst, ellipsoid((cx + d, cy, z0 + 0.03), (0.045, 0.12, 0.032), 10), m)
            add(inst, box(cx + d - 0.043, cy - 0.12, z0, cx + d + 0.043, cy + 0.115, z0 + 0.012), 'shoe_white')


def books_row(inst, x0, x1, y, z0, depth, rng, mats_, axis='x', lean_last=False):
    """Books standing in a row along `axis` from x0 to x1 (y = their back line, depth toward -y or -x)."""
    p = x0
    k = 0
    while p < x1 - 0.02:
        th = rng.uniform(0.02, 0.038)
        h = rng.uniform(0.17, 0.24)
        m = mats_[k % len(mats_)]
        if axis == 'x':
            add(inst, box(p, y - depth, z0, p + th, y, z0 + h), m)
        else:
            add(inst, box(y - depth, p, z0, y, p + th, z0 + h), m)
        p += th + 0.002
        k += 1


# ------------------------------------------------------------------------------------------- shell
def build_shell():
    r = 'room'
    add(r, box(-0.2, -0.2, -0.25, W + 0.2, D + 0.2, -0.012), 'subfloor')
    add(r, box(-0.2, -0.2, H, W + 0.2, D + 0.2, H + 0.1), 'ceiling')
    add(r, box(-0.2, -0.2, -0.25, 0, D + 0.2, H + 0.1), 'wall')                     # west
    add(r, box(-0.2, D, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')                  # north
    # south wall with the room door (flush, edge pull: no handle)
    add(r, box(-0.2, -0.2, -0.25, 0.1, 0, H + 0.1), 'wall'); add(r, box(0.9, -0.2, -0.25, W + 0.2, 0, H + 0.1), 'wall')
    add(r, box(0.1, -0.2, 2.1, 0.9, 0, H + 0.1), 'wall')
    add(r, box(0.1, -0.06, 0, 0.9, -0.02, 2.1), 'panel')
    for b in (box(0.085, -0.02, 0, 0.1, 0.006, 2.115), box(0.9, -0.02, 0, 0.915, 0.006, 2.115), box(0.085, -0.02, 2.1, 0.915, 0.006, 2.115)):
        add(r, b, 'panel')
    # east wall with the window (fixed pane)
    add(r, box(W, -0.2, -0.25, W + 0.2, WY0, H + 0.1), 'wall'); add(r, box(W, WY1, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
    add(r, box(W, WY0, -0.25, W + 0.2, WY1, WZ0), 'wall'); add(r, box(W, WY0, WZ1, W + 0.2, WY1, H + 0.1), 'wall')
    for b in (box(W, WY0, WZ0, W + 0.2, WY0 + 0.006, WZ1), box(W, WY1 - 0.006, WZ0, W + 0.2, WY1, WZ1), box(W, WY0, WZ1 - 0.006, W + 0.2, WY1, WZ1),
              box(W, WY0, WZ0 - 0.006, W + 0.2, WY1, WZ0)):
        add(r, b, 'sill')
    fx0, fx1 = W + 0.10, W + 0.13
    for b in (box(fx0, WY0, WZ0, fx1, WY0 + 0.035, WZ1), box(fx0, WY1 - 0.035, WZ0, fx1, WY1, WZ1),
              box(fx0, WY0, WZ1 - 0.035, fx1, WY1, WZ1), box(fx0, WY0, WZ0, fx1, WY1, WZ0 + 0.035)):
        add(r, b, 'winframe')
    add('bd_day', box(W + 4.0, -10, -5, W + 4.05, 14, 9), 'backdrop')
    # floor planks in five bands (land far to near, seen from the south-east corner)
    edges = [D + 0.01, 2.55, 1.9, 1.25, 0.6, -0.05]
    for k in range(5):
        add(f'floor{k}', box(0, edges[k + 1], -0.012, W, edges[k], 0.0), 'floor')


# ------------------------------------------------------------------------------------------- the walk-in block
def panel_box(inst, x0, y0, z0, x1, y1, z1, m='panel'):
    add(inst, box(x0, y0, z0, x1, y1, z1), m)


def build_closet(rng):
    g = 0.01                                                  # half shadow gap
    # platform with an oak edge (slides out of the west wall), interior floor in birch
    add('cl_plat', box(0.0, CY - PNT, 0.0, CX - 0.03, D, PZ - 0.012), 'white_in')
    add('cl_plat', box(0.0, CY, PZ - 0.012, CX - PNT, D, PZ), 'birch_y')
    edges = [CY - PNT, TK['tk1'][0], TK['tk1'][1], TK['tk2'][0], TK['tk2'][1], D]
    for k in range(0, 5, 2):
        wood('cl_plat', CX - 0.03, edges[k] + (0.002 if k else 0), 0.0, CX, edges[k + 1] - 0.002 if k < 4 else D, PZ, 'oak')
    # top bulkhead (with the closet ceiling) and the LED shadow gap
    add('cl_top', box(0.0, CY - PNT, PT + 0.045, CX, D, H), 'panel')
    add('cl_top', box(CX - 0.05, CY - PNT, PT + 0.005, CX - 0.03, D, PT + 0.045), 'gapc')
    add('cl_top', box(0.0, CY - PNT + 0.03, PT + 0.005, CX - 0.03, CY + 0.01, PT + 0.045), 'gapc')
    add('cl_top', box(0.0, CY + 0.01, PT + 0.035, CX - 0.05, D, PT + 0.045), 'panel')
    # interior: back of the panels is the room's west and north wall; partition behind the bedside recess
    for b in (box(0.86, LEDGE[0] - 0.02, LEDGE[2] - 0.02, 0.88, LEDGE[1] + 0.02, LEDGE[3] + 0.02),
              box(0.86, LEDGE[0] - 0.02, LEDGE[2] - 0.02, CX - PNT, LEDGE[1] + 0.02, LEDGE[2]),
              box(0.86, LEDGE[0] - 0.02, LEDGE[3], CX - PNT, LEDGE[1] + 0.02, LEDGE[3] + 0.02),
              box(0.86, LEDGE[0] - 0.02, LEDGE[2], CX - PNT, LEDGE[0], LEDGE[3]),
              box(0.86, LEDGE[1], LEDGE[2], CX - PNT, LEDGE[1] + 0.02, LEDGE[3])):
        add('cl_recess', b, 'white_in')
    add('cl_recess', box(0.885, LEDGE[0] + 0.02, LEDGE[3] - 0.006, 0.95, LEDGE[1] - 0.02, LEDGE[3]), 'led')
    # shadow-gap backing strips on the aisle face and the south face
    for yb in (1.85, 2.55):
        add('cl_gaps', box(CX - PNT - 0.012, yb - 0.02, PZ, CX - PNT, yb + 0.02, PT), 'gapc')
    add('cl_gaps', box(0.28, CY, PZ, 0.32, CY + 0.012, PT), 'gapc')
    # aisle face panels (front plane x = CX)
    y0, y1 = AISLE['pn_a1']
    panel_box('pn_a1', CX - PNT, y0 + g, PZ + 0.004, CX, y1 - g, PT)
    y0, y1 = AISLE['doorA']
    panel_box('doorA', CX - PNT, y0 + g, PZ + 0.004, CX, y1 - g, PT)
    y0, y1 = AISLE['pn_bed']
    ly0, ly1, lz0, lz1 = LEDGE
    for b in (box(CX - PNT, y0 + g, PZ + 0.004, CX, y1 - g, lz0 - g), box(CX - PNT, y0 + g, lz1 + g, CX, y1 - g, PT),
              box(CX - PNT, y0 + g, lz0 - g, CX, ly0 - g, lz1 + g), box(CX - PNT, ly1 + g, lz0 - g, CX, y1 - g, lz1 + g)):
        add('pn_bed', b, 'panel')
    add('ledge', box(CX - PNT, ly0, lz0, CX, ly1, lz1), 'panel')
    add('ledge', box(CX - PNT - 0.004, ly0 + 0.03, lz0, CX - PNT, ly1 - 0.03, lz0 + 0.012), 'steel')   # stay hinge
    # south face: a fixed panel and the mirror panel on an offset pivot (front plane y = CY - PNT .. CY)
    x0, x1 = SOUTHF['pn_s1']
    panel_box('pn_s1', x0 + g, CY - PNT, PZ + 0.004, x1 - g, CY, PT)
    x0, x1 = SOUTHF['mirror']
    panel_box('mirror', x0 + g, CY - PNT, PZ + 0.004, x1 - g, CY, PT)
    add('mirror', box(x0 + 0.05, CY - PNT - 0.003, PZ + 0.12, x1 - 0.05, CY - PNT, PT - 0.12), 'mirror')
    # mirror back: shallow shelves (8 cm) with jars and a tray
    for z in (1.05, 1.35, 1.65):
        add('mirror', box(x0 + 0.08, CY, z, 0.86, CY + 0.075, z + 0.012), 'birch_x')
        add('mirror', box(x0 + 0.08, CY + 0.07, z + 0.012, 0.86, CY + 0.075, z + 0.05), 'birch_x')
    add('mirror_c', lathe(rprof(0.025, 1.062, 1.14, 0.006, 3), 16, (0.45, CY + 0.04)), 'ceramic')
    add('mirror_c', lathe(rprof(0.022, 1.062, 1.12, 0.006, 3), 16, (0.55, CY + 0.04)), 'bk_mustard')
    add('mirror_c', lathe(rprof(0.025, 1.362, 1.43, 0.006, 3), 16, (0.62, CY + 0.04)), 'bk_teal')
    add('mirror_c', box(0.40, CY + 0.01, 1.662, 0.58, CY + 0.065, 1.682), 'oak_x')
    add('mirror_c', lathe(rprof(0.02, 1.662, 1.73, 0.006, 3), 16, (0.75, CY + 0.04)), 'bk_plum')

    # toe-kick drawers (oak fronts in the platform edge; slide out +x)
    for nm, (a0, a1) in TK.items():
        wood(nm, CX - 0.03, a0 + 0.002, 0.008, CX, a1 - 0.002, PZ - 0.004, 'oak')
        for b in (box(0.62, a0 + 0.03, 0.012, CX - 0.03, a1 - 0.03, 0.022), box(0.62, a0 + 0.03, 0.022, 0.64, a1 - 0.03, 0.10),
                  box(0.62, a0 + 0.03, 0.022, CX - 0.03, a0 + 0.042, 0.10), box(0.62, a1 - 0.042, 0.022, CX - 0.03, a1 - 0.03, 0.10)):
            add(nm, b, 'white_in')
    # toe-kick contents: slippers + socks (tk1), charger tray + socks (tk2)
    a0, a1 = TK['tk1']
    for d in (-0.05, 0.05):
        add('tk1_c', ellipsoid((0.80, (a0 + a1) / 2 - 0.12 + d, 0.045), (0.11, 0.042, 0.022), 10), 'cl_rose')
    for k, m in enumerate(('cl_sky', 'cl_mustard', 'cl_white')):
        add('tk1_c', ellipsoid((0.80, (a0 + a1) / 2 + 0.08 + k * 0.065, 0.045), (0.09, 0.028, 0.022), 8), m)
    a0, a1 = TK['tk2']
    add('tk2_c', rbox((0.80, a0 + 0.17, 0.034), (0.24, 0.20, 0.02), 0.008, 3), 'oak_x')
    add('tk2_c', rbox((0.78, a0 + 0.15, 0.048), (0.06, 0.12, 0.008), 0.003, 3), 'phone')
    for k, m in enumerate(('cl_teal', 'cl_plum', 'cl_charcoal')):
        add('tk2_c', ellipsoid((0.80, a0 + 0.34 + k * 0.06, 0.045), (0.09, 0.027, 0.022), 8), m)

    # inside: double rails across the north end, shelves on the west wall
    t = 0.018
    for zr in (RAIL_TOP, RAIL_BOT):
        add('cl_rails', tube([(0.03, RAIL_Y, zr), (0.84, RAIL_Y, zr)], 0.011, 10), 'steel')
        for xb in (0.03, 0.84):
            add('cl_rails', box(xb - 0.01, RAIL_Y - 0.02, zr - 0.01, xb + 0.01, RAIL_Y + 0.02, zr + 0.06), 'steel')
    add('cl_rails', box(0.0, 2.62, 2.40, 0.86, D, 2.418), 'birch_x')        # hat shelf over the rails
    SH = (0.02, 0.32, CY + 0.02, 2.60)                                       # shelves x0, x1, y0, y1
    add('cl_shelves', box(SH[0], SH[3], PZ, SH[1], SH[3] + t, 2.40), 'birch_y')      # end panel
    for z in (0.40, 0.80, 1.20, 1.60, 2.00):
        add('cl_shelves', box(SH[0], SH[2], z, SH[1], SH[3], z + t), 'birch_y')
    # pre-filled: the top rail (the teaser), folded stacks
    tops = ('cl_olive', 'cl_white', 'cl_mustard', 'cl_sky', 'cl_plum', 'cl_charcoal', 'cl_teal', 'cl_rose', 'cl_white', 'cl_teal')
    for k, m in enumerate(tops):
        garment('cl_top_g', 0.08 + k * 0.078, RAIL_Y, RAIL_TOP, rng.uniform(0.70, 0.84), 0.42, m, along='x')
    folds = [('cl_white', 'cl_sky', 'cl_charcoal', 'cl_white'), ('cl_mustard', 'cl_teal', 'cl_white'),
             ('cl_plum', 'cl_rose', 'cl_sky', 'cl_white'), ('cl_charcoal', 'cl_white', 'cl_olive')]
    for k, (z, yc) in enumerate(((0.818, 1.62), (0.818, 2.20), (1.218, 1.62), (1.218, 2.20))):
        stack('cl_fold', 0.17, yc, z, (0.26, 0.36, 0.05), folds[k], len(folds[k]), rng)
    for k, (z, yc) in enumerate(((1.618, 1.55), (1.618, 2.0), (1.618, 2.40))):
        stack('cl_fold2', 0.17, yc, z, (0.26, 0.30, 0.055), [('cl_teal', 'cl_white', 'cl_sky'), ('cl_rose', 'cl_charcoal', 'cl_white'),
                                                              ('cl_mustard', 'cl_white', 'cl_plum')][k], 3, rng)
    # filled during the walk-in: bottom rail, top-shelf boxes, shoes
    bots = ('cl_sky', 'cl_white', 'cl_plum', 'cl_mustard', 'cl_charcoal', 'cl_teal', 'cl_white', 'cl_rose', 'cl_sky')
    for k, m in enumerate(bots):
        garment(f'cl_bot{k}', 0.09 + k * 0.088, RAIL_Y, RAIL_BOT, rng.uniform(0.62, 0.76), 0.40, m, along='x')
    for k, (yc, m) in enumerate(((1.47, 'box_blue'), (1.86, 'bin_white'), (2.24, 'box_linen'))):
        add(f'cl_box{k}', rbox((0.17, yc, 2.018 + 0.13), (0.27, 0.34, 0.26), 0.02, 3), m)
    for k, (yc, m) in enumerate(((1.42, 'shoe_white'), (1.72, 'shoe_tan'), (2.02, 'shoe_teal'), (2.32, 'shoe_white'))):
        shoes(f'cl_shoe{k}', 0.17, yc, 0.418, m, along='y' if False else 'x')
    for k, (yc, m) in enumerate(((1.45, 'shoe_tan'), (1.82, 'shoe_white'), (2.22, 'shoe_teal'))):
        shoes(f'cl_shoeF{k}', 0.17, yc, PZ, m)


# ------------------------------------------------------------------------------------------- the bed (drawer platform)
def build_bed(rng):
    g = 0.01
    # platform body: white faces, an oak top edge, a recessed plinth
    add('bed_plat', box(BX0 + 0.05, BY0 + 0.05, 0.0, BX1, BY1, 0.05), 'gapc')
    add('bed_plat', box(BX0 + 0.02, BY0 + 0.02, 0.05, BX1, BY1, BZ - 0.04), 'white_in')
    wood('bed_plat', BX0, BY0, BZ - 0.04, BX1, BY1, BZ, 'oak')
    add('bed_plat', box(BX0, BY0, 0.05, BX1, BY0 + 0.02, BZ - 0.04), 'panel')                         # foot face
    for (a, b) in ((BY0, BD['bd1'][0]), (BD['bd1'][1], BD['bd2'][0]), (BD['bd2'][1], BY1)):
        add('bed_plat', box(BX0, a + (g if a > BY0 else 0), 0.05, BX0 + 0.02, b - g, BZ - 0.04), 'panel')
    # drawers (flush fronts, slide out -x)
    for nm, (a0, a1) in BD.items():
        add(nm, box(BX0, a0 + g, 0.055, BX0 + 0.02, a1 - g, BZ - 0.045), 'panel')
        for b in (box(BX0 + 0.02, a0 + 0.03, 0.06, BX0 + 0.62, a1 - 0.03, 0.075), box(BX0 + 0.60, a0 + 0.03, 0.075, BX0 + 0.62, a1 - 0.03, 0.36),
                  box(BX0 + 0.02, a0 + 0.03, 0.075, BX0 + 0.62, a0 + 0.045, 0.36), box(BX0 + 0.02, a1 - 0.045, 0.075, BX0 + 0.62, a1 - 0.03, 0.36)):
            add(nm, b, 'white_in')
    # drawer contents: suitcase + rolled duvet (bd1), three vacuum bags (bd2)
    a0, a1 = BD['bd1']
    add('bd1_suit', rbox((BX0 + 0.31, a0 + 0.30, 0.16), (0.50, 0.46, 0.17), 0.035, 3), 'suitcase')
    add('bd1_suit', tube([(BX0 + 0.12, a0 + 0.20, 0.25), (BX0 + 0.11, a0 + 0.20, 0.258), (BX0 + 0.11, a0 + 0.40, 0.258), (BX0 + 0.12, a0 + 0.40, 0.25)], 0.008, 6), 'blackm')
    add('bd1_roll', xform(lathe(rprof(0.11, -0.25, 0.25, 0.05, 4), 20, (0, 0)), T(BX0 + 0.31, a1 - 0.19, 0.19) @ R('y', math.pi / 2)), 'linen_w')
    a0, a1 = BD['bd2']
    for k, (m, dy) in enumerate((('vac_teal', 0.0), ('vac_plum', 0.29), ('vac_grey', 0.58))):
        add(f'bd2_bag{k}', rbox((BX0 + 0.31, a0 + 0.17 + dy, 0.13 + 0.02 * k), (0.52, 0.27, 0.11), 0.045, 4), m)
    # mattress, olive duvet, pillows
    add('mattress', rbox(((BX0 + BX1) / 2, (BY0 + BY1) / 2, BZ + 0.10), (BX1 - BX0 - 0.03, BY1 - BY0 - 0.03, 0.20), 0.045, 5), 'mattress')
    cloth('duvet', BX0 + 0.01, BX1 - 0.01, BY0 + 0.02, 2.55, 0.665, 0.50, 0.05, 'olive', 3, sides=('w', 's'))
    add('duvet', rbox(((BX0 + BX1) / 2, 2.50, 0.676), (BX1 - BX0 - 0.02, 0.15, 0.03), 0.013, 3), 'linen_w')
    pillow('pil1', (2.10, 2.86, 0.82), (0.56, 0.15, 0.40), -0.36, 'linen_w')
    pillow('pil2', (2.70, 2.86, 0.82), (0.56, 0.15, 0.40), -0.36, 'linen_w')
    pillow('pil3', (2.40, 2.70, 0.78), (0.42, 0.13, 0.38), -0.28, 'olive_knit')
    cloth('throw', BX0 + 0.02, BX1 - 0.02, 1.15, 1.55, 0.690, 0.52, 0.04, 'throw_w', 7, sides=('w',), puff=0.006)
    # headboard shelf (0.2 m deep) and the oak ledge above with books, a plant and an abstract print
    add('hb', box(BX0 - 0.0, BY1, 0.0, BX1, D, 0.98), 'panel')
    add('hb', box(BX0, BY1 - 0.004, 0.98, BX1, D, 1.0), 'oak_x')
    wood('oak_ledge', 1.95, 3.04, 1.42, 2.95, D, 1.445, 'oak')
    books_row('ledge_bk', 1.98, 2.30, D - 0.005, 1.445, 0.14, rng, ('bk_teal', 'bk_white', 'bk_mustard', 'bk_olive', 'bk_plum', 'bk_sky'))
    plant('ledge_pl', 2.82, 3.12, 1.445, 0.05, 0.08, rng, 9, pot='ceramic')
    add('ledge_pr', box(2.38, D - 0.03, 1.445, 2.72, D - 0.01, 1.86), 'oak_x')
    add('ledge_pr', box(2.40, D - 0.032, 1.465, 2.70, D - 0.03, 1.84), 'print')


# ------------------------------------------------------------------------------------------- south wall unit, desk, bench
def build_south(rng):
    g = 0.01
    x0, x1, d = SU0, W, SUY
    add('su_body', box(x0, 0.0, 0.0, x1, d - PNT, PT), 'white_in')
    add('su_body', box(x0, 0.0, PT + 0.045, x1, d, H), 'panel')
    add('su_body', box(x0, 0.0, PT + 0.005, x1, d - 0.03, PT + 0.045), 'gapc')
    add('su_body', box(x0, d - PNT - 0.004, 0.0, x1, d - 0.006, 0.05), 'gapc')
    # desk recess (behind the desk panel), lit
    for b in (box(DK0, 0.0, DKZ - 0.012, DK1, d, DKZ), box(DK0, 0.0, DKZ + 0.45, DK1, d, DKZ + 0.462),
              box(DK0 - 0.012, 0.0, DKZ - 0.012, DK0, d, DKZ + 0.462), box(DK1, 0.0, DKZ - 0.012, DK1 + 0.012, d, DKZ + 0.462)):
        add('su_rec', b, 'white_in')
    add('su_rec', box(DK0 + 0.02, 0.0, DKZ, DK1 - 0.02, 0.012, DKZ + 0.45), 'oak_z')
    add('su_rec', box(DK0 + 0.05, d - 0.06, DKZ + 0.444, DK1 - 0.05, d - 0.04, DKZ + 0.45), 'led')
    # recess contents: laptop (in a slot), notebooks, pen pot, small plant
    add('rec_lap', box(2.05, 0.03, DKZ, 2.07, 0.06, DKZ + 0.16), 'oak_x')
    add('rec_lap', box(2.08, 0.035, DKZ + 0.002, 2.095, 0.20, DKZ + 0.23), 'alu')
    books_row('rec_bk', DK0 + 0.04, DK0 + 0.22, 0.17, DKZ, 0.15, rng, ('bk_sky', 'bk_mustard', 'bk_white', 'bk_teal'))
    add('rec_pot', lathe([(0, DKZ), (0.035, DKZ), (0.035, DKZ + 0.10), (0.03, DKZ + 0.10), (0.03, DKZ + 0.006), (0, DKZ + 0.006)], 18, (2.55, 0.10)), 'ceramic')
    for k in range(3):
        add('rec_pot', tube([(2.55 + 0.01 * (k - 1), 0.10, DKZ + 0.02), (2.55 + 0.02 * (k - 1), 0.10 + 0.005 * k, DKZ + 0.16)], 0.004, 5),
            ('bk_teal', 'bk_mustard', 'bk_plum')[k])
    plant('rec_pl', 2.80, 0.10, DKZ, 0.045, 0.06, rng, 9)
    # front panels (flush, front plane y = d): lower, desk (folds down), mid, upper rack front
    panel_box('su_lo', x0 + g, d - PNT, 0.055, x1 - g, d, DKZ - 0.02)
    panel_box('desk', DK0, d - PNT, DKZ, DK1, d, DKZ + 0.45)
    for b in (box(x0 + g, d - PNT, DKZ - 0.02 + g, DK0 - g, d, 1.60), box(DK1 + g, d - PNT, DKZ - 0.02 + g, x1 - g, d, 1.60)):
        add('su_side', b, 'panel')
    panel_box('su_mid', DK0, d - PNT, DKZ + 0.45 + 2 * g, DK1, d, 1.60)
    # upper cabinet: the rack front + shelf + arms ride together; the cabinet box stays
    for b in (box(x0 + g, d - PNT, 1.62, DK0 - g, d, PT), box(DK1 + g, d - PNT, 1.62, x1 - g, d, PT)):
        add('su_side', b, 'panel')
    add('rack', box(DK0, d - PNT, 1.62, DK1, d, PT), 'panel')
    add('rack', box(DK0 + 0.02, d - 0.26, 1.64, DK1 - 0.02, d - PNT, 1.655), 'birch_x')
    add('rack', box(DK0 + 0.02, d - 0.26, 1.655, DK1 - 0.02, d - 0.245, 1.72), 'birch_x')
    for xs in (DK0 + 0.03, DK1 - 0.03):
        add('rack_arm', tube([(xs, 0.06, RACK_PZ), (xs, 0.06, RACK_PZ + RACK_R)], 0.008, 8), 'steel')
    books_row('rack_bk', 2.86 - 0.0, 2.93, d - 0.03, 1.655, 0.2, rng, ('bk_sky', 'bk_plum'), axis='x')
    for k, (xc, m) in enumerate(((2.05, 'box_blue'), (2.38, 'box_linen'), (2.70, 'bin_white'))):
        add(f'rack_box{k}', rbox((xc, d - 0.13, 1.655 + 0.10), (0.26, 0.22, 0.20), 0.015, 3), m)
    # bench: oak box with a lid hinged on the desk side
    bx0, bx1, by0, by1, bz = BN
    wood('bench', bx0, by0, 0.0, bx1, by0 + 0.02, bz - 0.025, 'oak')
    wood('bench', bx0, by1 - 0.02, 0.0, bx1, by1, bz - 0.025, 'oak')
    wood('bench', bx0, by0, 0.0, bx0 + 0.02, by1, bz - 0.025, 'oak')
    wood('bench', bx1 - 0.02, by0, 0.0, bx1, by1, bz - 0.025, 'oak')
    add('bench', box(bx0 + 0.02, by0 + 0.02, 0.04, bx1 - 0.02, by1 - 0.02, 0.055), 'white_in')
    wood('bench_lid', bx0, by0, bz - 0.025, bx1, by1, bz, 'oak')
    # bench contents (long cut): shoes and two throws
    shoes('bench_c', 2.05, 0.83, 0.055, 'shoe_tan')
    stack('bench_c2', 2.55, 0.83, 0.055, (0.40, 0.26, 0.06), ('cl_olive', 'cl_sky'), 2, rng)
    # runner and tall plant
    add('runner', rbox((1.40, 1.75, 0.006), (0.62, 2.3, 0.012), 0.005, 3), 'jute')
    tall_plant('tplant', 1.24, 0.28, rng)


def build():
    materials()
    rng = np.random.default_rng(7)
    build_shell()
    build_closet(rng)
    build_bed(rng)
    build_south(rng)
    # bedside ledge contents (land on the flipped-down ledge; the ledge is x CX..CX+0.30 at z LEDGE[2])
    lz = LEDGE[2] + PNT
    add('lamp', lathe(rprof(0.05, lz, lz + 0.012, 0.004, 3), 24, (1.12, 3.02)), 'ceramic')
    add('lamp', tube([(1.12, 3.02, lz + 0.01), (1.12, 3.02, lz + 0.20)], 0.006, 8), 'steel')
    add('lamp', lathe([(0.0, lz + 0.30), (0.05, lz + 0.30), (0.075, lz + 0.18), (0.0, lz + 0.18)], 24, (1.12, 3.02)), 'shade')
    add('lamp_on', ellipsoid((1.12, 3.02, lz + 0.22), (0.022, 0.022, 0.022), 8), 'bulb')
    add('ledge_books', box(1.03, 2.66, lz, 1.13, 2.80, lz + 0.03), 'bk_teal')
    add('ledge_books', box(1.035, 2.665, lz + 0.03, 1.125, 2.795, lz + 0.055), 'bk_mustard')
    add('ledge_phone', rbox((1.19, 2.85, lz + 0.005), (0.07, 0.15, 0.009), 0.004, 3), 'phone')
    # LED cove strips (light up one after another around the room)
    add('led0', box(CX - 0.025, 1.2, PT + 0.03, CX - 0.01, 2.2, PT + 0.04), 'led')
    add('led1', box(CX - 0.025, 2.2, PT + 0.03, CX - 0.01, D, PT + 0.04), 'led')
    add('led2', box(SU0, SUY - 0.025, PT + 0.03, W, SUY - 0.01, PT + 0.04), 'led')
    add('led3', box(0.0, CY - 0.025, PT + 0.03, CX, CY - 0.01, PT + 0.04), 'led')
    add('cl_light', box(0.30, 1.6, PT + 0.044, 0.70, 2.8, PT + 0.045), 'led')
    add('cl_light', box(0.10, 2.70, 2.385, 0.78, 2.72, 2.40), 'led')
    # the person (a denim walker and a teal twin who comes out of the mirror; 15 s cut: denim, reaching inside)
    global FIG_D, FIG_T
    FIG_D = fg.figure('figd', 'adult', pose='stand', at=(0.62, 2.20, 0), floor=PZ, mat='fig_denim')
    FIG_T = fg.figure('figt', 'adult', pose='stand', at=(0.62, 0.60, 180), floor=0.0, mat='fig_teal')


FIG_D = FIG_T = None


# ------------------------------------------------------------------------------------------- camera
VFOV = 85.0


def P(x, y, z, yaw, pitch):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch)


F1 = P(2.85, 0.40, 2.10, -38.0, -21.0)                                   # frame 1 = the loop pose
S1 = (F1, P(2.50, 0.85, 1.95, -37.0, -20.0))                               # corner push-in
S2 = (P(1.50, 1.80, 1.40, -28.0, -26.0), P(1.62, 1.25, 1.88, 14.0, -50.0))    # aisle: ledge -> bed drawers
S3a = (P(2.30, 0.95, 1.75, -45.0, -12.0), P(1.75, 1.45, 1.62, -58.0, -8.0))     # door A from the south-east: it swings away
S3b0 = (S3a[1], P(1.30, 2.20, 1.60, -90.0, -7.0))
S3b = (S3b0[1], P(0.72, 2.20, 1.58, -90.0, -8.0))                             # through the doorway
S3c = (P(0.72, 2.20, 1.58, -90.0, -8.0), P(0.66, 1.78, 1.50, -6.0, -9.0))   # turn to the rails
S3d = (P(2.08, 1.42, 2.38, -62.0, -34.0), P(2.58, 1.22, 2.62, -50.0, -39.0))  # dollhouse
OVH = (P(1.48, 1.80, 2.08, 6.0, -88.5), P(1.48, 1.68, 2.24, -26.0, -88.5))     # overhead

L1 = (P(1.45, 0.55, 0.85, -22.0, -24.0), P(1.42, 1.40, 0.80, -42.0, -30.0))     # aisle, low: toe-kicks
L2 = (P(1.62, 1.85, 1.30, -28.0, -24.0), P(1.48, 2.12, 1.22, -34.0, -22.0))     # bed head: the ledge
L3 = (P(2.20, 0.70, 2.05, -30.0, -45.0), P(2.55, 0.85, 2.05, -40.0, -47.0))     # high over the bed foot: drawers
L4 = (P(2.05, 1.75, 1.40, 165.0, -40.0), P(2.55, 1.75, 1.40, 180.0, -40.0))     # bench
L5 = (P(2.40, 1.55, 1.35, 180.0, -22.0), P(2.38, 1.15, 1.10, 180.0, -14.0))     # desk
L6 = (P(2.38, 1.40, 1.00, 180.0, 20.0), P(2.50, 1.30, 1.05, 186.0, 14.0))       # rack, from the bench
L7 = (P(1.70, 0.95, 1.50, -42.0, -10.0), P(1.75, 1.62, 1.55, -68.0, -8.0))      # aisle, push in on door A
LS3c = (S3c[0], P(0.66, 1.78, 1.50, -6.0, -9.0))
LS3e = (LS3c[1], P(0.70, 1.72, 1.45, -55.0, 12.0))                               # back to the top shelf
LS3d = (P(1.85, 2.05, 2.34, -78.0, -32.0), P(2.25, 1.90, 2.56, -72.0, -40.0))   # dollhouse
L9 = (P(1.65, 0.15, 1.55, -10.0, -14.0), P(1.70, 0.60, 1.50, -22.0, -14.0))     # aisle: she walks in
L10 = (P(1.65, 0.30, 1.55, -55.0, -12.0), P(1.45, 0.45, 1.50, -48.0, -10.0))    # entry: out through the mirror
if LONG:
    HOLDS = [(0.0, 3.0, S1), (3.3, 6.2, L1), (6.5, 9.2, L2), (9.5, 13.2, L3), (13.5, 16.2, L4), (16.5, 19.6, L5),
             (19.9, 22.6, L6), (22.9, 26.6, L7), (26.9, 27.45, S3a), (27.45, 27.75, S3b0), (27.75, 28.1, S3b), (28.1, 29.1, LS3c), (29.1, 30.2, LS3e),
             (30.2, 33.3, LS3d), (33.3, 35.6, L9), (35.9, 39.7, L10), (40.0, 42.0, OVH)]
else:
    HOLDS = [(0.0, 3.0, S1), (3.3, 7.0, S2), (7.3, 7.85, S3a), (7.85, 8.15, S3b0), (8.15, 8.5, S3b), (8.5, 9.2, S3c), (9.2, 11.0, S3d),
             (11.0, 13.0, OVH)]
_hold = hold_camera(HOLDS, VFOV, rest=REST)
T_DESC = 13.0 if not LONG else 42.0


def camera(t):
    if REST:
        st = [S1, S2, S3b, S3c, S3d, OVH][min(5, int(t))]
        return dict(st[1] if os.environ.get('ROOM_END') == '1' else st[0], vfov=VFOV)
    if t >= T_DESC:
        u = c01((t - T_DESC) / (DUR - T_DESC))
        e = 1 - (1 - u) ** 2.6
        a = dict(OVH[1]); b = dict(F1)
        return lerp_cam(a, b, e, lift=0.0, vfov=VFOV)
    return _hold(t)


# ------------------------------------------------------------------------------------------- lights (fixed slots)
LSKY = (10.0, 10.6, 11.6)
LSUN = (64000.0, 58000.0, 47000.0)
LFILL = (2.0, 1.97, 1.92)
LCEIL = (0.55, 0.55, 0.54)
LCLOSET = (60.0, 55.0, 44.0)
LREC = (40.0, 33.0, 24.0)
LCOVE = (30.0, 25.0, 17.0)
LLAMP = (80.0, 64.0, 42.0)

T_LIGHTS = 12.55 if not LONG else 41.2


def lights(mats4, vis):
    off = (0.0, 0.0, 0.0)

    def k(L, on, f=1.0):
        return tuple(v * f for v in L) if on else off
    Ls = []
    Ls.append(rect_light((W + 0.16, WY0, WZ0), (0, 0, WZ1 - WZ0), (0, WY1 - WY0, 0), LSKY, always=1))                 # 0 sky (-x)
    sc = np.array([W, (WY0 + WY1) / 2, (WZ0 + WZ1) / 2]) - SUN_DIR * 3.0
    Ls.append(spot_rect(tuple(sc), tuple(SUN_DIR), 0.06, LSUN, 0.0))                                                  # 1 sun
    Ls.append(rect_light((1.0, 0.005, 0.3), (0, 0, 1.9), (0.7, 0, 0), LFILL, always=1))                               # 2 fill +y
    Ls.append(rect_light((1.1, 0.4, H - 0.004), (0, 2.4, 0), (1.6, 0, 0), LCEIL))                                       # 3 ceiling fill (down)
    cl_on = bool(vis.get('cl_light'))
    Ls.append(rect_light((0.30, 1.6, PT + 0.04), (0, 1.2, 0), (0.40, 0, 0), k(LCLOSET, cl_on)))                       # 4 closet light (down)
    Ls.append(rect_light((0.885, LEDGE[0] + 0.02, LEDGE[3] - 0.007), (0, LEDGE[1] - LEDGE[0] - 0.04, 0), (0.065, 0, 0),
                         k(LREC, vis.get('ledge'))))                                                                   # 5 bedside recess
    Ls.append(rect_light((DK0 + 0.05, SUY - 0.06, DKZ + 0.443), (0, 0.02, 0), (DK1 - DK0 - 0.1, 0, 0), k(LREC, vis.get('desk'))))  # 6 desk recess
    cove = [((CX - 0.03, 1.2, PT + 0.028), (0, 1.0, 0), (0.03, 0, 0), 'led0'),
            ((CX - 0.03, 2.2, PT + 0.028), (0, 1.0, 0), (0.03, 0, 0), 'led1'),
            ((SU0, SUY - 0.03, PT + 0.028), (0.03 * 0 + 0.0, 0.03, 0), (W - SU0, 0, 0), 'led2'),
            ((0.0, CY - 0.03, PT + 0.028), (0, 0.03, 0), (CX, 0, 0), 'led3')]
    for c, eu, ev, nm in cove:                                                                                         # 7-10 cove LEDs
        n = np.cross(eu, ev)
        if n[2] > 0:
            eu, ev = ev, eu
        Ls.append(rect_light(c, eu, ev, k(LCOVE, vis.get(nm))))
    if vis.get('lamp'):                                                                                                # 11 lamp
        c = mats4['lamp'] @ np.array([1.12, 3.02, LEDGE[2] + PNT + 0.22, 1.0])
        Ls.append(sphere_light(tuple(c[:3]), 0.02, k(LLAMP, vis.get('lamp_on'))))
    else:
        Ls.append(sphere_light((1.12, 3.02, 0.86), 0.02, off))
    Ls.append(rect_light((0.08, 2.66, 2.392), (0, 0.48, 0), (0.72, 0, 0), k(LCLOSET, cl_on, 0.8)))                       # 12 rail light (down)
    return Ls


BLENDER = dict(
    exposure=-0.30,
    look='AgX - Medium High Contrast',
    translucent={'shade': 0.6},
    separate=['backdrop'],
    fill_lights=[2, 3],
    wood_scale=(55.0, 1.6),
    bake_rect={'backdrop': (-3.0, 7.0, -2.0, 6.0)},
    bake_px={'backdrop': 0.006, 'floor': 0.0015},
)


# ------------------------------------------------------------------------------------------- timeline
def timeline():
    tl = Timeline(rk, FPS)
    I = np.eye(4)
    hidden = lambda t: (I, False)
    if REST:
        for nm in ('led0', 'led1', 'led2', 'led3', 'cl_light', 'lamp_on') + tuple(FIG_T.pieces):
            tl.custom(nm, hidden)
        ldg = math.radians(-90)
        tl.custom('ledge', lambda t: (about((CX, 0, LEDGE[2]), R('y', -ldg)), True))
        tl.custom('desk', lambda t: (about((0, SUY, DKZ), R('x', math.radians(-90))), True))
        return tl
    if LONG:
        return timeline_long(tl)
    return timeline_15(tl)


def helpers(tl):
    I = np.eye(4)
    ev = tl.ev

    def appear(name, t_on, t_off=None):
        tl.custom(name, lambda t: (I, t >= t_on and (t_off is None or t < t_off)))

    def hinge(name, piv, axis, a_open, keys, t_in=None, land=None, vis=None):
        """A hinged piece (panel, door, lid, flap). keys = [(t_open, t_shut), ...]: opens with an overshoot in 0.3 s,
        holds, shuts in 0.17 s with a push-latch bounce. land = (t0, t1, axis, pivot) grows it in first."""
        piv = np.array(piv, float)

        def ang(t):
            a = 0.0
            for (to, ts) in keys:
                if t < to:
                    break
                if ts is None or t < ts:
                    a = a_open * eob(c01((t - to) / 0.30), 1.2)
                    break
                u = (t - ts) / 0.17
                if u < 1:
                    a = a_open * (1 - u * u)
                    break
                tau = t - ts - 0.17
                a = math.copysign(math.radians(1.6), a_open) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))
            return a

        def f(t):
            if t_in is not None and t < t_in:
                return I, False
            if vis is not None and not vis(t):
                return I, False
            M = about(piv, R(axis, ang(t)))
            if land is not None:
                t0, t1, ax, pv = land
                if t < t1:
                    u = (t - t0) / (t1 - t0)
                    s = 0.02 + 0.98 * eob(u, 1.0)
                    sc = [1.0, 1.0, 1.0]; sc['xyz'.index(ax)] = s
                    M = M @ about(pv, S(*sc))
            return M, True
        tl.custom(name, f)
        for (to, ts) in keys:
            ev(to + 0.05, name + '_open', 0.45, 'swish')
            if ts is not None:
                ev(ts + 0.17, name + '_shut', 0.7, 'thud')
        return f

    def drawer(name, off, keys, t_in=0.0, vis=None, latch=True):
        """Push-latch drawer: pops open (overshoot) at each key's open time and shuts with a small bounce."""
        off = np.array(off, float)

        def k_of(t):
            cur = [kk for kk in keys if kk[0] <= t]
            if not cur:
                return 0.0, 0.0
            to, ts = cur[-1]
            if ts is None or t < ts:
                return eob(c01((t - to) / 0.18), 1.4), 0.0
            u = (t - ts) / 0.17
            if u < 1:
                return 1 - smooth(u), 0.0
            tau = t - ts - 0.17
            return 0.0, 0.006 * math.exp(-tau / 0.05) * math.sin(2 * math.pi * tau / 0.12)

        def f(t):
            if t < t_in or (vis is not None and not vis(t)):
                return I, False
            k, wob = k_of(t)
            return T(*(off * k + off / np.linalg.norm(off) * wob)), True
        tl.custom(name, f)
        for (to, ts) in keys:
            ev(to + 0.06, name + '_open', 0.45, 'tick' if latch else 'swish')
            if ts is not None:
                ev(ts + 0.17, name + '_shut', 0.7, 'thud')
        return f

    def ride(name, parent, t_in=0.0, drop=None):
        """Contents riding in a drawer/rack; drop = (t0, t1, height) lands them first."""
        piv = tl.cen[name]

        def f(t):
            if t < t_in:
                return I, False
            M = parent(t)[0]
            if drop is not None:
                t0, t1, h = drop
                if t < t0:
                    return I, False
                u = (t - t0) / (t1 - t0)
                if u < 1:
                    z = h * (1 - u * u); s = 0.5 + 0.5 * smooth(u / 0.35)
                else:
                    tau = t - t1
                    z = 0.05 * h * math.exp(-tau / 0.09) * abs(math.sin(math.pi * tau / 0.13)); s = 1.0
                M = M @ T(0, 0, z) @ about(piv, S(s, s, s))
            return M, True
        tl.custom(name, f)
        if drop is not None:
            ev(drop[1], name, 0.4, 'tick')
        return f
    return appear, hinge, drawer, ride


def shell_opening(tl, appear, hinge, drawer, ride):
    """0.0-3.0 s (both cuts): planks, platform, the panel domino, the door-A teaser, bed, bench, runner, ledge."""
    ev = tl.ev
    drop, slide, grow = tl.drop, tl.slide, tl.grow
    for k in range(5):
        t1 = 0.16 + 0.05 * k
        drop(f'floor{k}', t1 - 0.16, t1, 0.30, 0.05, 0.3 + 0.04 * k, 'tick')
    slide('cl_plat', 0.04, 0.20, (-1.05, 0, 0), 1.0, 0.8)
    slide('cl_top', 0.06, 0.22, (-1.05, 0, 0), 1.0, 0.5)
    appear('cl_gaps', 0.20)
    order = [('pn_a1', 0.30), ('doorA', 0.44), ('pn_bed', 0.58), ('pn_s1', 0.70), ('mirror', 0.80), ('su_lo', 0.92),
             ('desk', 1.04), ('su_side', 1.14), ('su_mid', 1.24), ('rack', 1.34)]
    T_IN = {}
    for nm, t1 in order:
        T_IN[nm] = t1
    for nm in ('pn_s1', 'pn_a1', 'pn_bed', 'su_lo', 'su_side', 'su_mid'):
        grow(nm, T_IN[nm] - 0.14, T_IN[nm], 'z', (0, 0, 0.0), 0.55 if nm != 'pn_bed' else 0.6, 'thud')
    appear('ledge', T_IN['pn_bed'] - 0.14 + 0.07)
    appear('cl_recess', 0.62)
    appear('su_body', 0.80)
    appear('su_rec', 0.92)
    for nm in ('cl_rails', 'cl_shelves', 'cl_top_g', 'cl_fold', 'cl_fold2', 'tk1', 'tk2', 'tk1_c', 'tk2_c', 'mirror_c'):
        appear(nm, 0.16 if nm in ('tk1', 'tk2') else 0.70)
    return T_IN


def s1_bed(tl):
    drop, slide, grow = tl.drop, tl.slide, tl.grow
    # bed, bench, runner, ledge decor (S1)
    drop('bed_plat', 1.30, 1.45, 0.45, 0.02, 0.85, 'thud')
    drop('mattress', 1.52, 1.65, 0.35, 0.03, 0.6, 'thud')
    drop('duvet', 1.66, 1.80, 0.35, 0.03, 0.55, 'thud')
    drop('pil1', 1.78, 1.92, 0.30, 0.08, 0.35); drop('pil2', 1.84, 1.98, 0.30, 0.08, 0.35); drop('pil3', 1.92, 2.06, 0.30, 0.08, 0.3)
    drop('hb', 1.22, 1.36, 0.45, 0.02, 0.5, 'thud')
    drop('bench', 1.92, 2.05, 0.40, 0.03, 0.75, 'thud')
    grow('runner', 2.05, 2.22, 'y', (0, 0.6, 0), 0.4, 'swish')
    slide('oak_ledge', 2.00, 2.12, (0.0, 0.25, 0.0), 1.0, 0.45)
    drop('ledge_bk', 2.18, 2.32, 0.25, 0.05, 0.35)
    drop('ledge_pr', 2.40, 2.54, 0.25, 0.04, 0.35)
    drop('ledge_pl', 2.62, 2.76, 0.25, 0.06, 0.35)


def timeline_15(tl):
    I = np.eye(4)
    ev = tl.ev
    drop, slide, grow, fly = tl.drop, tl.slide, tl.grow, tl.fly
    appear, hinge, drawer, ride = helpers(tl)
    T_IN = shell_opening(tl, appear, hinge, drawer, ride)
    # mirror (lands, never opens in this cut), rack (lands)
    grow('mirror', T_IN['mirror'] - 0.14, T_IN['mirror'], 'z', (0, 0, 0), 0.55, 'thud')
    grow('rack', T_IN['rack'] - 0.14, T_IN['rack'], 'z', (0, 0, 1.62), 0.45, 'thud')
    tl.custom('rack_arm', lambda t: (I, False))
    for k in range(3):
        appear(f'rack_box{k}', 1.4)
    for nm in ('rec_lap', 'rec_bk', 'rec_pot', 'rec_pl'):
        appear(nm, 1.0)
    appear('rack_bk', 1.4)
    # door A: grows in, teaser open on the packed top rail (1.40-1.75), S3 open (7.40), the wave (11.0 / ripple)
    WAVE_T = {}
    hA = (CX, AISLE['doorA'][1], 0)
    # ripple order: anticlockwise around the room starting at the toe-kicks
    ripple = ['tk1', 'doorA', 'tk2', 'bd2', 'bd1', 'bench_lid']
    for i, nm in enumerate(ripple):
        WAVE_T[nm] = 11.75 + 0.15 * i
    hinge('doorA', hA, 'z', math.radians(92), [(0.78, 1.30), (7.15, 9.18), (11.0 + 0.05 * 1, WAVE_T['doorA'])],
          land=(T_IN['doorA'] - 0.14, T_IN['doorA'], 'z', (0, 0, 0)))
    ev(T_IN['doorA'], 'doorA_land', 0.55, 'thud')
    tl.custom('cl_light', lambda t: (I, 0.80 <= t < 1.47 or 7.35 <= t < 11.0))
    ev(7.35, 'closet_light', 0.5, 'chime')
    # desk: lands closed, folds down in the open wave and stays open
    dpiv = (0, SUY, DKZ)

    def desk(t):
        if t < T_IN['desk'] - 0.14:
            return I, False
        if t < T_IN['desk']:
            u = (t - (T_IN['desk'] - 0.14)) / 0.14
            return about((0, 0, 0), S(1, 1, 0.02 + 0.98 * eob(u, 1.0))), True
        if t < 11.15:
            return I, True
        a = math.radians(-90) * eob(c01((t - 11.15) / 0.32), 0.25)
        return about(dpiv, R('x', a)), True
    tl.custom('desk', desk)
    ev(T_IN['desk'], 'desk_land', 0.5, 'thud'); ev(11.47, 'desk_open', 0.6, 'thud')
    s1_bed(tl)
    tl.custom('tplant', lambda t: (np.eye(4), False))
    # S2: bedside flap flips down (3.5); lamp, books, phone (3.8-4.4); bed drawers (4.7 / 4.85); contents; shut (6.3 / 6.45)
    lp = (CX, 0, LEDGE[2])

    def ledge(t):
        if t < T_IN['pn_bed'] - 0.07:
            return I, False
        if t < 3.28:
            # rides the bedside panel's grow
            u = c01((t - (T_IN['pn_bed'] - 0.14)) / 0.14)
            return about((0, 0, 0), S(1, 1, 0.02 + 0.98 * eob(u, 1.0))) if t < T_IN['pn_bed'] else I, True
        a = math.radians(90) * eob(c01((t - 3.28) / 0.30), 0.5)
        return about(lp, R('y', a)), True
    tl.custom('ledge', ledge)
    ev(3.38, 'ledge_open', 0.55, 'swish'); ev(3.58, 'ledge_land', 0.5, 'thud')
    drop('lamp', 3.62, 3.80, 0.35, 0.05, 0.45)
    appear('lamp_on', 3.88); ev(3.88, 'lamp_on', 0.45, 'chime')
    drop('ledge_books', 3.95, 4.11, 0.30, 0.05, 0.4)
    drop('ledge_phone', 4.20, 4.34, 0.25, 0.05, 0.35)
    off = (-0.58, 0, 0)
    f1 = drawer('bd1', off, [(4.85, 6.45), (11.08, WAVE_T['bd1'])], t_in=1.30)
    f2 = drawer('bd2', off, [(4.70, 6.30), (11.06, WAVE_T['bd2'])], t_in=1.30)
    # drawers land with the bed platform
    for nm, f in (('bd1', f1), ('bd2', f2)):
        base = tl.anims['bed_plat']

        def g(t, f=f, base=base):
            M, v = f(t)
            if t < 1.45:
                return base(t)[0] @ M, base(t)[1]
            return M, v
        tl.custom(nm, g)
    ride('bd1_suit', tl.anims['bd1'], drop=(5.10, 5.28, 0.45))
    ride('bd1_roll', tl.anims['bd1'], drop=(5.30, 5.46, 0.40))
    for k in range(3):
        ride(f'bd2_bag{k}', tl.anims['bd2'], drop=(5.48 + 0.15 * k, 5.64 + 0.15 * k, 0.42))
    ev(6.80, 'swing', 0.3, 'swish')
    # S3: door A (opened above at 7.40); bottom rail fills one garment at a time (8.5-9.3)
    for k in range(9):
        t0 = 8.45 + 0.09 * k
        tl.fly(f'cl_bot{k}', t0, t0 + 0.16, (0, -0.18, 0.08), 0.04, 0.3, 'tick')
    # dollhouse (9.4-11.0): the aisle face is hidden; boxes slide in, shoes drop; she reaches for a jacket
    DH = (9.2, 11.0)
    dh = lambda t: not (DH[0] <= t < DH[1])
    for nm in ('pn_a1', 'pn_bed', 'cl_gaps', 'cl_top', 'cl_recess', 'lamp', 'lamp_on', 'ledge_books', 'ledge_phone', 'ledge'):
        base = tl.anims.get(nm, lambda t: (I, True))
        tl.custom(nm, lambda t, base=base: (base(t)[0], base(t)[1] and dh(t)))
    base_dA = tl.anims['doorA']
    tl.custom('doorA', lambda t: (base_dA(t)[0], base_dA(t)[1] and dh(t)))
    for k in range(3):
        tl.fly(f'cl_box{k}', 9.62 + 0.17 * k, 9.80 + 0.17 * k, (0.5, 0, 0.04), 0.04, 0.4, 'thud')
    for k in range(4):
        drop(f'cl_shoe{k}', 10.10 + 0.13 * k, 10.24 + 0.13 * k, 0.30, 0.05, 0.35)
    for k in range(3):
        appear(f'cl_shoeF{k}', 0.70)
    FIG_D.animate(tl, pose=fg.track([(9.2, 'stand'), (9.6, 'reach_up'), (10.9, 'reach_up')]), at=(0.58, 2.30, -15), floor=PZ,
                  visible=lambda t: DH[0] <= t < DH[1])
    FIG_T.animate(tl, visible=False)
    # S4: open wave (11.0-11.3), ripple shut (11.45-12.2), lights on round the room (12.2), drawer pops (12.5), throw (13.2)
    drawer('tk1', (0.34, 0, 0), [(11.02, WAVE_T['tk1']), (12.85, 14.0)], t_in=0.16)
    drawer('tk2', (0.34, 0, 0), [(11.10, WAVE_T['tk2'])], t_in=0.16)
    for nm, f in (('tk1', tl.anims['tk1']), ('tk2', tl.anims['tk2'])):
        base = tl.anims['cl_plat']
        tl.custom(nm, lambda t, f=f, base=base: (base(t)[0] @ f(t)[0], f(t)[1]) if t < 0.20 else f(t))
    ride('tk1_c', tl.anims['tk1'], t_in=0.70)
    ride('tk2_c', tl.anims['tk2'], t_in=0.70)
    bpiv = (0, BN[2], BN[4] - 0.012)

    def blid(t):
        if t < 1.92:
            return I, False
        M = tl.anims['bench'](t)[0]
        a = 0.0
        if 11.12 <= t < WAVE_T['bench_lid']:
            a = math.radians(78) * eob(c01((t - 11.12) / 0.28), 1.2)
        elif t >= WAVE_T['bench_lid']:
            u = (t - WAVE_T['bench_lid']) / 0.17
            a = math.radians(78) * (1 - u * u) if u < 1 else 0.0
        return M @ about(bpiv, R('x', a)), True
    tl.custom('bench_lid', blid)
    ev(11.17, 'bench_open', 0.4, 'swish'); ev(WAVE_T['bench_lid'] + 0.17, 'bench_shut', 0.7, 'thud')
    for nm in ('bench_c', 'bench_c2'):
        appear(nm, 2.05)
    # ripple sound: a latch tick on each thud, rising in pitch (strength steps the tick's gain)
    for i, nm in enumerate(ripple):
        ev(WAVE_T[nm] + 0.175, f'latch{i}', 0.5 + 0.08 * i, 'tick')
    ev(WAVE_T[ripple[-1]] + 0.30, 'clack', 0.6, 'tick')
    for i, nm in enumerate(('led3', 'led0', 'led1', 'led2')):
        appear(nm, T_LIGHTS + 0.12 * i)
    ev(T_LIGHTS, 'lights_on', 0.65, 'chime')
    ev(12.87, 'boing', 0.5, 'swish')
    drop('throw', 13.10, 13.30, 0.45, 0.04, 0.5, 'thud')
    return tl


def timeline_long(tl):
    """44.0 s: the same opening, a new zone every 6-7 s, the walk-in wow at 30.2 s, the person, the overhead finale."""
    I = np.eye(4)
    ev = tl.ev
    drop, slide, grow, fly = tl.drop, tl.slide, tl.grow, tl.fly
    appear, hinge, drawer, ride = helpers(tl)
    T_IN = shell_opening(tl, appear, hinge, drawer, ride)
    s1_bed(tl)
    ripple = ['tk1', 'doorA', 'tk2', 'bd2', 'bd1', 'bench_lid']
    WT = {nm: 40.45 + 0.15 * i for i, nm in enumerate(ripple)}
    TW = 40.0                                                    # open wave
    DH = (30.2, 33.3)
    dh = lambda t: not (DH[0] <= t < DH[1])
    # ---- zone 1b (3.3-6.2): toe-kick drawers open, fill, shut
    tk1 = drawer('tk1', (0.34, 0, 0), [(4.00, 5.20), (TW + 0.02, WT['tk1']), (41.50, 43.0)], t_in=0.16)
    tk2 = drawer('tk2', (0.34, 0, 0), [(4.45, 5.40), (TW + 0.10, WT['tk2'])], t_in=0.16)
    for nm, f in (('tk1', tk1), ('tk2', tk2)):
        base = tl.anims['cl_plat']
        tl.custom(nm, lambda t, f=f, base=base: (base(t)[0] @ f(t)[0], f(t)[1]) if t < 0.20 else f(t))
    ride('tk1_c', tl.anims['tk1'], drop=(4.30, 4.48, 0.30))
    ride('tk2_c', tl.anims['tk2'], drop=(4.72, 4.90, 0.30))
    appear('tplant', 23.15)
    # ---- zone 2a (6.5-9.2): bedside flap, lamp, books, phone
    lp = (CX, 0, LEDGE[2])

    def ledge(t):
        if t < T_IN['pn_bed'] - 0.07:
            return I, False
        if t < 6.75:
            if t < T_IN['pn_bed']:
                u = c01((t - (T_IN['pn_bed'] - 0.14)) / 0.14)
                return about((0, 0, 0), S(1, 1, 0.02 + 0.98 * eob(u, 1.0))), dh(t)
            return I, dh(t)
        a = math.radians(90) * eob(c01((t - 6.75) / 0.30), 0.5)
        return about(lp, R('y', a)), dh(t)
    tl.custom('ledge', ledge)
    ev(6.85, 'ledge_open', 0.55, 'swish'); ev(7.05, 'ledge_land', 0.5, 'thud')
    for nm, (t0, t1, h) in (('lamp', (7.15, 7.33, 0.35)), ('ledge_books', (7.55, 7.71, 0.30)), ('ledge_phone', (7.90, 8.04, 0.25))):
        f = drop(nm, t0, t1, h, 0.05, 0.45)
        tl.custom(nm, lambda t, f=f: (f(t)[0], f(t)[1] and dh(t)))
    tl.custom('lamp_on', lambda t: (I, t >= 7.45 and dh(t)))
    ev(7.45, 'lamp_on', 0.45, 'chime')
    ev(8.45, 'charge', 0.35, 'chime')
    # ---- zone 2b (9.5-13.2): bed drawers out, suitcase, rolled duvet, three bags, shut
    off = (-0.58, 0, 0)
    f1 = drawer('bd1', off, [(9.90, 12.60), (TW + 0.08, WT['bd1'])], t_in=1.30)
    f2 = drawer('bd2', off, [(10.10, 12.40), (TW + 0.06, WT['bd2'])], t_in=1.30)
    for nm, f in (('bd1', f1), ('bd2', f2)):
        base = tl.anims['bed_plat']
        tl.custom(nm, lambda t, f=f, base=base: (base(t)[0] @ f(t)[0], base(t)[1]) if t < 1.45 else f(t))
    ride('bd1_suit', tl.anims['bd1'], drop=(10.45, 10.65, 0.45))
    ride('bd1_roll', tl.anims['bd1'], drop=(10.80, 10.98, 0.40))
    for k in range(3):
        ride(f'bd2_bag{k}', tl.anims['bd2'], drop=(11.20 + 0.25 * k, 11.38 + 0.25 * k, 0.42))
    # ---- zone 3a (13.5-16.2): bench lid lifts, shoes + throws, shuts
    bpiv = (0, BN[2], BN[4] - 0.012)
    LIDK = [(13.90, 15.70), (TW + 0.12, WT['bench_lid'])]

    def lid_ang(t):
        a = 0.0
        for (to, ts) in LIDK:
            if t < to:
                break
            if t < ts:
                a = math.radians(78) * eob(c01((t - to) / 0.28), 1.2); break
            u = (t - ts) / 0.17
            a = math.radians(78) * (1 - u * u) if u < 1 else 0.0
        return a

    def blid(t):
        if t < 1.92:
            return I, False
        return tl.anims['bench'](t)[0] @ about(bpiv, R('x', lid_ang(t))), True
    tl.custom('bench_lid', blid)
    for (to, ts) in LIDK:
        ev(to + 0.05, 'bench_open', 0.4, 'swish'); ev(ts + 0.17, 'bench_shut', 0.7, 'thud')
    drop('bench_c', 14.20, 14.38, 0.45, 0.05, 0.4)
    drop('bench_c2', 14.65, 14.85, 0.45, 0.04, 0.45, 'thud')
    # ---- zone 3b (16.5-19.6): desk folds down, recess lights, laptop + notebooks + pen pot + plant
    dpiv = (0, SUY, DKZ)

    def desk(t):
        if t < T_IN['desk'] - 0.14:
            return I, False
        if t < T_IN['desk']:
            u = (t - (T_IN['desk'] - 0.14)) / 0.14
            return about((0, 0, 0), S(1, 1, 0.02 + 0.98 * eob(u, 1.0))), True
        if t < 16.80:
            return I, True
        return about(dpiv, R('x', math.radians(-90) * eob(c01((t - 16.80) / 0.38), 0.25))), True
    tl.custom('desk', desk)
    ev(T_IN['desk'], 'desk_land', 0.5, 'thud'); ev(17.15, 'desk_open', 0.7, 'thud')
    slide('rec_lap', 17.40, 17.62, (0, 0.40, 0), 1.0, 0.4, 'tick')
    drop('rec_bk', 17.85, 18.02, 0.25, 0.05, 0.4)
    drop('rec_pot', 18.25, 18.40, 0.25, 0.05, 0.35)
    drop('rec_pl', 18.62, 18.80, 0.25, 0.06, 0.35)
    # ---- zone 4a (19.9-22.6): the rack swings out and down, boxes and books land, swings back up
    rp = (0, 0.06, RACK_PZ)

    def th(t):
        if t < 20.20:
            return 0.0
        if t < 22.0:
            return RACK_A * eob(c01((t - 20.20) / 0.55), 0.3)
        return RACK_A * (1 - smooth(c01((t - 22.0) / 0.45)))

    def rack(t):
        if t < T_IN['rack'] - 0.14:
            return I, False
        if t < T_IN['rack']:
            u = (t - (T_IN['rack'] - 0.14)) / 0.14
            return about((0, 0, 1.62), S(1, 1, 0.02 + 0.98 * eob(u, 1.0))), True
        a = th(t)
        return T(0, RACK_R * math.sin(a), -RACK_R * (1 - math.cos(a))), True
    tl.custom('rack', rack)
    ev(T_IN['rack'], 'rack_land', 0.45, 'thud'); ev(20.25, 'rack_down', 0.55, 'swish'); ev(22.47, 'rack_up', 0.7, 'thud')
    tl.custom('rack_arm', lambda t: (about(rp, R('x', -th(t))), 20.15 <= t < 22.5))
    for k in range(3):
        ride(f'rack_box{k}', tl.anims['rack'], drop=(20.70 + 0.22 * k, 20.88 + 0.22 * k, 0.30))
    ride('rack_bk', tl.anims['rack'], drop=(21.36, 21.52, 0.25))
    # ---- zone 4b (22.9-26.6) + zone 5 (26.9-33.3): door A, the walk-in, the dollhouse
    hA = (CX, AISLE['doorA'][1], 0)
    dA = hinge('doorA', hA, 'z', math.radians(92), [(0.78, 1.30), (25.60, 30.2), (34.10, 35.00), (TW + 0.05, WT['doorA'])],
               land=(T_IN['doorA'] - 0.14, T_IN['doorA'], 'z', (0, 0, 0)))
    tl.custom('doorA', lambda t: (dA(t)[0], dA(t)[1] and dh(t)))
    ev(T_IN['doorA'], 'doorA_land', 0.55, 'thud')
    ev(25.40, 'latch', 0.6, 'tick')
    tl.custom('cl_light', lambda t: (I, 0.80 <= t < 1.47 or 25.65 <= t < 39.9))
    ev(25.70, 'closet_light', 0.5, 'chime')
    ev(23.30 + 0.75, 'swish1', 0.25, 'swish')
    for k in range(9):
        t0 = 27.80 + 0.13 * k
        fly(f'cl_bot{k}', t0, t0 + 0.16, (0, -0.18, 0.08), 0.04, 0.3, 'tick')
    for k in range(3):
        fly(f'cl_box{k}', 29.20 + 0.22 * k, 29.38 + 0.22 * k, (0.5, 0, 0.04), 0.04, 0.4, 'thud')
    for k in range(4):
        drop(f'cl_shoe{k}', 30.40 + 0.14 * k, 30.54 + 0.14 * k, 0.30, 0.05, 0.35)
    for k in range(3):
        drop(f'cl_shoeF{k}', 30.95 + 0.12 * k, 31.09 + 0.12 * k, 0.30, 0.05, 0.3)
    for nm, (t0, t1) in (('cl_fold', (31.35, 31.52)), ('cl_fold2', (31.65, 31.82))):
        drop(nm, t0, t1, 0.25, 0.04, 0.45, 'thud')
    for nm in ('pn_a1', 'pn_bed', 'cl_gaps', 'cl_top', 'cl_recess'):
        base = tl.anims.get(nm, lambda t: (I, True))
        tl.custom(nm, lambda t, base=base: (base(t)[0], base(t)[1] and dh(t)))
    # ---- mirror: lands; long leaf swings into the closet (dollhouse 32.0, the walk-out 36.2)
    mp = (0.90, CY - PNT / 2, 0)
    MK = [(31.95, 32.95), (36.20, 37.40)]

    def m_ang(t):
        a = 0.0
        for (to, ts) in MK:
            if t < to:
                break
            if t < ts:
                a = math.radians(-90) * eob(c01((t - to) / 0.35), 0.4); break
            u = (t - ts) / 0.22
            a = math.radians(-90) * (1 - smooth(u)) if u < 1 else 0.0
        return a

    def mirror(t):
        if t < T_IN['mirror'] - 0.14:
            return I, False
        if t < T_IN['mirror']:
            u = (t - (T_IN['mirror'] - 0.14)) / 0.14
            return about((0, 0, 0), S(1, 1, 0.02 + 0.98 * eob(u, 1.0))), True
        return about(mp, R('z', m_ang(t))), True
    tl.custom('mirror', mirror)
    ev(T_IN['mirror'], 'mirror_land', 0.55, 'thud')
    for (to, ts) in MK:
        ev(to + 0.05, 'mirror_open', 0.45, 'swish'); ev(ts + 0.22, 'mirror_shut', 0.7, 'thud')
    mc_piv = tl.cen['mirror_c']

    def mirror_c(t):
        if t < 32.25:
            return I, False
        M = mirror(t)[0]
        u = (t - 32.25) / 0.20
        if u < 1:
            return M @ T(0, 0, 0.18 * (1 - u * u)) @ about(mc_piv, S(*([0.5 + 0.5 * smooth(u / 0.35)] * 3))), True
        return M, True
    tl.custom('mirror_c', mirror_c)
    ev(32.45, 'jars', 0.4, 'tick'); ev(32.60, 'jars2', 0.35, 'tick')
    # ---- zone 6 (33.3-39.7): the person
    walk_in = [(33.30, (1.38, 0.75, 0)), (34.75, (1.38, 2.10, 0)), (35.15, (1.38, 2.10, -90)), (35.85, (0.60, 2.15, -90))]
    pose_w, at_w = fg.walk(walk_in, FIG_D)

    def floor_d(t):
        x = at_w(t)[0]
        return PZ * smooth(c01((1.12 - x) / 0.22))

    def pose_d(t):
        if 35.15 <= t < 35.40:
            return fg.lerp_pose(pose_w(t), 'step_up', math.sin(math.pi * (t - 35.15) / 0.25))
        return pose_w(t)
    FIG_D.animate(tl, pose=pose_d, at=at_w, floor=floor_d, visible=lambda t: 33.3 <= t < 35.95 or DH[0] + 0.4 <= t < DH[1],
                  pop=None)
    # in the dollhouse (30.6-33.3) she is not shown walking: hide the walker there (she arrives at 33.3)
    for nm in FIG_D.pieces:
        base = tl.anims[nm]
        tl.custom(nm, lambda t, base=base: (base(t)[0], base(t)[1] and 33.3 <= t < 35.95))
    walk_out = [(36.45, (0.60, 1.95, 180)), (37.15, (0.60, 0.75, 180)), (37.75, (0.60, 0.75, 0)), (38.55, (0.60, 0.75, 0)),
                (38.80, (0.60, 0.75, 200)), (39.50, (0.45, 0.05, 200))]
    pose_t, at_t = fg.walk(walk_out, FIG_T)

    def floor_t(t):
        y = at_t(t)[1]
        return PZ * smooth(c01((y - 1.10) / 0.22))

    def pose_tt(t):
        if 37.80 <= t < 38.50:
            return fg.lerp_pose('stand', dict(fg.POSES['stand'], sh_r=60, elbow_r=90, neck=-6), math.sin(math.pi * (t - 37.8) / 0.7))
        return pose_t(t)
    FIG_T.animate(tl, pose=pose_tt, at=at_t, floor=floor_t, visible=lambda t: 36.45 <= t < 39.45)
    ev(36.50, 'music_drop', 0.0, 'none')
    # ---- zone 7 (40.0-44.0): open wave, ripple, lights, the drawer gag, the throw
    for i, nm in enumerate(ripple):
        ev(WT[nm] + 0.175, f'latch{i}', 0.5 + 0.08 * i, 'tick')
    ev(WT[ripple[-1]] + 0.30, 'clack', 0.6, 'tick')
    for i, nm in enumerate(('led3', 'led0', 'led1', 'led2')):
        appear(nm, T_LIGHTS + 0.12 * i)
    ev(T_LIGHTS, 'lights_on', 0.65, 'chime')
    ev(41.52, 'boing', 0.5, 'swish')
    drop('throw', 42.10, 42.30, 0.45, 0.04, 0.5, 'thud')
    return tl

if __name__ == '__main__':
    import json
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    timeline().export(DUR, camera, lights, out)
    json.dump({'bpm': 120, 'MUSIC': dict(drop_at=0, chords=[[53, 57, 60, 64], [55, 59, 62, 64], [52, 55, 59, 62], [57, 60, 64, 67]],
                                         roots=[41, 43, 40, 45], pluck_bars=[0, 2], riser=False)},
              open(os.path.join(out, 'music.json'), 'w'))
