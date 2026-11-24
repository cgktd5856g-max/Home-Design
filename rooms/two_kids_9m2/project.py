"""Tape Line, Turning Wall: two kids, one 12 m² room. A two-tone tape line zips down the middle of the empty room, two
different-but-fair halves build at the same time, and at bedtime a loaded double-sided wardrobe swings 90° off the far
wall on a steel pivot post, lands exactly on the tape and telescopes into a wall: one playroom becomes two bedrooms.
It swings back for the loop.

West half (child A, celery): loft bed at 1.6 m with a ladder, a book wall facing the door, under-loft desk.
East half (child B, soft blue): mid-sleeper at 0.9 m with four stair drawers and a den under it, small desk.
White shell + light oak + the two muted accents (wardrobe faces + bedding). No on-screen text.

    ROOM_REST=1 python3 ../../pipeline/run.py project.py <workdir> probe 0.5,1.5,2.5,3.5     # finished room, stations
    ROOM_REST=1 ROOM_SWUNG=1 ...                                                             # ... with the wardrobe swung
    python3 ../../pipeline/run.py project.py <workdir> preview                               # code-renderer preview (15 s)
    ROOM_CUT=long ...                                                                        # the long cut

Units: metres. x = east, y = north, z = up. Room x 0..W, y 0..D, z 0..H. Door: centre of the south wall (onto a short
hallway). Windows: one in each side wall. Pivot post: centre of the north wall, 0.25 m out.
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
REST_OPEN = os.environ.get('ROOM_OPEN') == '1'          # rest view with storage open
REST_SWUNG = os.environ.get('ROOM_SWUNG') == '1'        # rest view with the wardrobe swung onto the tape + the kids
CUT = os.environ.get('ROOM_CUT', 'short')

W, D, H = 3.6, 3.4, 2.7
CX = W / 2
FPS = 25
DUR = 8.0 if REST else (44.0 if CUT == 'long' else 15.0)

DX0, DX1 = 1.40, 2.20                                  # door opening (south wall)
WY0, WY1, WZ0, WZ1 = 0.55, 1.45, 0.95, 2.25            # side windows (both walls)
# west: loft bed
LX1, LY0 = 1.00, 1.40                                  # loft x 0..LX1, y LY0..D
LZ0, LZ1 = 1.55, 1.60                                  # deck underside / top
BW_Y0 = 1.24                                           # book wall y BW_Y0..LY0 (faces the door)
# east: mid-sleeper
BX0, BY1 = 2.65, 2.00                                  # bed x BX0..W, y 0.05..BY1
BZ0, BZ1 = 0.85, 0.90                                  # deck underside / top
SX0 = 2.20                                             # stair drawers x SX0..BX0, columns along y
SRUN, SRZ, SY0 = 0.25, 0.21, 0.10
# the turning wardrobe (parked against the north wall), pivot post, track
PIV = (CX, D - 0.25)
WRX0, WRX1, WRY0, WRY1, WRZ0, WRZ1 = CX - 0.25, CX + 1.25, D - 0.50, D, 0.05, 2.23
PNL = 0.80                                             # telescoping end panel
TRK_R = 1.12                                           # floor track radius
SUN_DIR = np.array([0.80, 0.18, -0.57]) / np.linalg.norm([0.80, 0.18, -0.57])
DL = [(1.0, 0.8), (2.6, 0.8)]
CAPTIONS = []                                          # no on-screen text


# ------------------------------------------------------------------------------------------- materials
def materials():
    mat('subfloor', tex=3, col=srgb(204, 203, 200), p=(0.05,))
    mat('floor', tex=1, col=srgb(218, 192, 158), col2=srgb(200, 172, 136), rough=0.4, f0=0.04, glossy=True, p=(0.16, 1.5))
    mat('wall', tex=3, col=srgb(240, 240, 238), p=(0.015,))
    mat('ceiling', col=srgb(247, 247, 246))
    mat('white_cab', col=srgb(244, 243, 240), rough=0.42)
    mat('white_in', col=srgb(236, 235, 232))
    mat('plinth', col=srgb(196, 194, 190))
    wood_mats('oak', srgb(216, 184, 142), seed=4.0)
    mat('celery', tex=3, col=srgb(184, 197, 158), rough=0.6, p=(0.02,))
    mat('sky_blue', tex=3, col=srgb(160, 181, 204), rough=0.6, p=(0.02,))
    mat('tapeA', col=srgb(150, 176, 118), rough=0.5)
    mat('tapeB', col=srgb(118, 152, 198), rough=0.5)
    mat('steel', col=srgb(196, 198, 200), rough=0.32, metal=1)
    mat('track_m', col=srgb(206, 206, 204), rough=0.35, f0=0.04, glossy=True)
    mat('caster', col=srgb(60, 62, 66), rough=0.5)
    mat('alu', col=srgb(200, 202, 206), rough=0.3, metal=1)
    mat('winframe', col=srgb(238, 238, 236), rough=0.35)
    mat('sill', col=srgb(242, 241, 238), rough=0.25, f0=0.04, glossy=True)
    mat('mattress', tex=5, col=srgb(246, 245, 241), p=(0, 0.02))
    mat('linen_w', tex=3, col=srgb(240, 238, 232), rough=0.9, p=(0.04,))
    mat('duvetA', tex=5, col=srgb(196, 207, 172), p=(0, 0.012))
    mat('duvetB', tex=5, col=srgb(176, 194, 214), p=(0, 0.012))
    mat('pilA', tex=6, col=srgb(186, 199, 160))
    mat('pilB', tex=6, col=srgb(164, 184, 206))
    mat('pil_white', tex=3, col=srgb(244, 242, 238), rough=0.9, p=(0.05,))
    mat('pil_mustard', tex=3, col=srgb(222, 192, 124), rough=0.9, p=(0.05,))
    mat('pil_terra', tex=3, col=srgb(204, 150, 122), rough=0.9, p=(0.05,))
    mat('rug', tex=6, col=srgb(232, 228, 220))
    mat('ceramic', col=srgb(243, 242, 238), rough=0.22, f0=0.04, glossy=True)
    mat('leaf', col=srgb(70, 116, 64)); mat('leaf2', col=srgb(100, 146, 78))
    mat('bulb', col=(0, 0, 0), emis=(9.0, 7.8, 6.0))
    mat('led', col=(0, 0, 0), emis=(7.5, 6.9, 5.6))
    mat('led_off', col=srgb(232, 231, 228))
    mat('dl_emis', col=(0, 0, 0), emis=(8.5, 7.8, 6.6))
    mat('backdrop', tex=9, emis=(1.9, 1.9, 1.9), p=(1.0, 1.0))
    mat('backdrop_night', tex=16, emis=(1.0, 1.0, 1.0), p=(1.0, 1.0))
    mat('box_linen', tex=3, col=srgb(214, 208, 196), p=(0.06,))
    mat('bin_grey', tex=6, col=srgb(206, 206, 204))
    for nm, c in (('cl_cream', (236, 230, 216)), ('cl_celery', (184, 198, 156)), ('cl_blue', (156, 178, 204)), ('cl_navy', (70, 84, 118)),
                  ('cl_mustard', (220, 182, 104)), ('cl_grey', (168, 170, 174)), ('cl_white', (244, 244, 242)),
                  ('cl_denim', (104, 128, 164)), ('cl_terra', (196, 128, 100)), ('cl_sage', (150, 170, 146))):
        mat(nm, tex=5, col=srgb(*c), p=(2, 0.008))
    for nm, c in (('bk_sage', (156, 176, 148)), ('bk_cream', (234, 224, 204)), ('bk_terra', (198, 124, 96)), ('bk_navy', (64, 78, 112)),
                  ('bk_mustard', (220, 176, 84)), ('bk_rust', (176, 96, 70)), ('bk_white', (242, 240, 236)), ('bk_blue', (130, 160, 196)), ('bk_grey', (176, 178, 180))):
        mat(nm, col=srgb(*c), rough=0.6)
    for nm, c in (('toy_red', (204, 112, 96)), ('toy_yellow', (230, 194, 100)), ('toy_blue', (110, 150, 200)), ('toy_green', (128, 176, 120)),
                  ('toy_white', (242, 240, 236))):
        mat(nm, col=srgb(*c), rough=0.45, f0=0.04, glossy=True)
    for nm, c in (('fb_sage', (172, 190, 150)), ('fb_blue', (150, 174, 204)), ('fb_mustard', (216, 192, 138)), ('fb_terra', (201, 154, 134)),
                  ('fb_cream', (230, 222, 204)), ('fb_grey', (190, 190, 190))):
        mat(nm, tex=3, col=srgb(*c), rough=0.85, p=(0.035,))
    mat('shoe_white', col=srgb(244, 244, 240), rough=0.5)
    fg.materials()


# ------------------------------------------------------------------------------------------- helpers
def disc(inst, c, r, z0, z1, m, n=28):
    add(inst, lathe(rprof(r, z0, z1, min(0.004, (z1 - z0) * 0.45), 3), n, c), m)


def knob(inst, c, facing, m='oak_x', r=0.016):
    """Round knob on a front at c, sticking out along facing ('-y', '+x', '-x')."""
    rot = {'-y': R('x', math.pi / 2), '+x': R('y', math.pi / 2), '-x': R('y', -math.pi / 2)}[facing]
    add(inst, xform(lathe(rprof(r, 0, 0.02, 0.006, 3), 16, (0, 0)), T(*c) @ rot), m)


def drawer(inst, facing, f, a0, a1, z0, z1, depth, front='white_cab', inner='white_in', knobs=1):
    """Drawer with its front at plane f facing `facing` ('-y', '+x', '-x'), spanning a0..a1 along the front, z0..z1."""
    L = a1 - a0
    parts = [(box(-L / 2 + 0.003, 0, z0 + 0.004, L / 2 - 0.003, 0.018, z1 - 0.004), front),
             (box(-L / 2 + 0.02, 0.018, z0 + 0.016, L / 2 - 0.02, depth - 0.012, z0 + 0.028), inner),
             (box(-L / 2 + 0.02, 0.018, z0 + 0.028, -L / 2 + 0.032, depth - 0.012, z1 - 0.045), inner),
             (box(L / 2 - 0.032, 0.018, z0 + 0.028, L / 2 - 0.02, depth - 0.012, z1 - 0.045), inner),
             (box(-L / 2 + 0.02, depth - 0.024, z0 + 0.028, L / 2 - 0.02, depth - 0.012, z1 - 0.045), inner)]
    ang, c = {'-y': (0.0, ((a0 + a1) / 2, f, 0)), '+x': (math.pi / 2, (f, (a0 + a1) / 2, 0)),
              '-x': (-math.pi / 2, (f, (a0 + a1) / 2, 0))}[facing]
    M = T(*c) @ R('z', ang)
    for pn, m in parts:
        add(inst, xform(pn, M), m)
    zc = (z0 + z1) / 2 + (z1 - z0) * 0.12
    for k in range(knobs):
        u = 0.0 if knobs == 1 else (-0.25 + 0.5 * k) * L
        p = M @ np.array([u, 0.0, zc, 1.0])
        knob(inst, p[:3], facing)


def garment(inst, x, y, z_top, length, width, m):
    """Hanging garment on a rail running along y (faces +-y)."""
    add(inst, tube([(x - width * 0.45, y, z_top - 0.045), (x, y, z_top), (x + width * 0.45, y, z_top - 0.045)], 0.0035, 6), 'alu')
    add(inst, rbox((x, y, z_top - 0.05 - length / 2), (width, 0.032, length), 0.014, 3), m)


def stack(inst, cx, cy, z0, size, mats_, n, rng):
    z = z0
    for i in range(n):
        sx, sy, sz = size
        jx, jy = rng.uniform(-0.008, 0.008, 2)
        add(inst, rbox((cx + jx, cy + jy, z + sz / 2), (sx * rng.uniform(0.95, 1.0), sy * rng.uniform(0.95, 1.0), sz), sz * 0.45, 3),
            mats_[i % len(mats_)])
        z += sz * 0.96


def plant(inst, cx, cy, z0, r, h, rng, n=9, pot='ceramic'):
    add(inst, lathe([(0, z0), (r * 0.8, z0), (r, z0 + h), (r * 1.06, z0 + h + 0.006), (0, z0 + h + 0.006)], 20, (cx, cy)), pot)
    for k in range(n):
        a = 2 * math.pi * k / n + rng.uniform(-0.25, 0.25)
        lean = rng.uniform(0.3, 0.8)
        L = rng.uniform(0.07, 0.13) * (r / 0.05)
        c = np.array([cx + math.cos(a) * L * 0.4 * lean, cy + math.sin(a) * L * 0.4 * lean, z0 + h + L * 0.55])
        add(inst, xform(ellipsoid(c, (0.016, 0.016, L * 0.55), 7), about(c, R('z', a) @ R('x', lean * 0.6))), 'leaf' if k % 2 else 'leaf2')


def cloth(inst, x0, x1, y0, y1, z_top, z_hem, r, m, seed, sides=('w', 'e', 's'), puff=0.012):
    """Draped fabric: a gently wrinkled top plus rounded edges falling into softly folded skirts."""
    ph = np.random.default_rng(seed).uniform(0, 6.283, 5)
    xc, hw = (x0 + x1) / 2, (x1 - x0) / 2

    def wob(x, y):
        return (0.009 * math.sin(x * 9 + ph[0]) * math.sin(y * 5 + ph[1]) + 0.005 * math.sin(x * 17 + y * 11 + ph[2])
                + puff * max(0.0, 1 - ((x - xc) / hw) ** 2))
    nx, ny = 30, 34
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


def pillow(inst, c, size, tilt, m, yaw=0.0):
    """Puffy pillow: thick in the middle, pinched at the seam. size = (width, thickness, height); faces -y before yaw."""
    c = np.array(c, float)
    hw, t0, hh = size[0] / 2, size[1], size[2] / 2
    n = 20
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


def books_row(inst, x0, x1, y, z, spec, along='y'):
    """Books standing on a shelf: spines face the room. spec = [(mat, thickness, height), ...]; they run along y from y."""
    for m, th, h in spec:
        add(inst, box(x0, y, z, x1, y + th, z + h), m)
        y += th + 0.003
    return y




# ------------------------------------------------------------------------------------------- shell
def build_shell():
    r = 'room'
    add(r, box(-0.2, -1.8, -0.25, W + 0.2, D + 0.2, -0.012), 'subfloor')
    add(r, box(-0.2, -1.8, H, W + 0.2, D + 0.2, H + 0.1), 'ceiling')
    add(r, box(-0.2, D, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
    # south wall + door opening + hallway
    add(r, box(-0.2, -0.2, -0.25, DX0, 0, H + 0.1), 'wall'); add(r, box(DX1, -0.2, -0.25, W + 0.2, 0, H + 0.1), 'wall')
    add(r, box(DX0, -0.2, 2.1, DX1, 0, H + 0.1), 'wall')
    for b in (box(DX0 - 0.06, -0.012, 0, DX0, 0.012, 2.16), box(DX1, -0.012, 0, DX1 + 0.06, 0.012, 2.16),
              box(DX0 - 0.06, -0.012, 2.1, DX1 + 0.06, 0.012, 2.16)):
        add(r, b, 'white_cab')
    add(r, box(DX0 - 0.6, -1.8, -0.012, DX1 + 0.6, -0.2, 0.0), 'floor')
    add(r, box(DX0 - 0.8, -1.8, -0.25, DX0 - 0.6, -0.2, H + 0.1), 'wall')
    add(r, box(DX1 + 0.6, -1.8, -0.25, DX1 + 0.8, -0.2, H + 0.1), 'wall')
    add(r, box(DX0 - 0.8, -2.0, -0.25, DX1 + 0.8, -1.8, H + 0.1), 'wall')
    # side walls, each with a window
    for x0, x1, xf0, xf1, xs in ((-0.2, 0.0, -0.13, -0.10, 0.0), (W, W + 0.2, W + 0.10, W + 0.13, W)):
        add(r, box(x0, -0.2, -0.25, x1, WY0, H + 0.1), 'wall'); add(r, box(x0, WY1, -0.25, x1, D + 0.2, H + 0.1), 'wall')
        add(r, box(x0, WY0, -0.25, x1, WY1, WZ0), 'wall'); add(r, box(x0, WY0, WZ1, x1, WY1, H + 0.1), 'wall')
        for b in (box(x0, WY0, WZ0, x1, WY0 + 0.006, WZ1), box(x0, WY1 - 0.006, WZ0, x1, WY1, WZ1), box(x0, WY0, WZ1 - 0.006, x1, WY1, WZ1)):
            add(r, b, 'sill')
        sx0, sx1 = (xs - 0.17, xs + 0.035) if xs == 0.0 else (xs - 0.035, xs + 0.17)
        add(r, box(sx0, WY0 - 0.03, WZ0 - 0.02, sx1, WY1 + 0.03, WZ0), 'sill')
        ym = (WY0 + WY1) / 2
        for b in (box(xf0, WY0, WZ0, xf1, WY0 + 0.04, WZ1), box(xf0, WY1 - 0.04, WZ0, xf1, WY1, WZ1), box(xf0, WY0, WZ1 - 0.04, xf1, WY1, WZ1),
                  box(xf0, WY0, WZ0, xf1, WY1, WZ0 + 0.04), box(xf0, ym - 0.018, WZ0, xf1, ym + 0.018, WZ1)):
            add(r, b, 'winframe')
    for b in (box(0, 0, 0, 0.012, D, 0.07), box(W - 0.012, 0, 0, W, D, 0.07), box(0, D - 0.012, 0, W, D, 0.07),
              box(0, 0, 0, DX0 - 0.06, 0.012, 0.07), box(DX1 + 0.06, 0, 0, W, 0.012, 0.07)):
        add(r, b, 'white_cab')
    for (x, y) in DL:
        add(r, lathe([(0.034, H - 0.002), (0.046, H - 0.002), (0.047, H - 0.010), (0.050, H - 0.012), (0.052, H)], 32, (x, y)), 'white_cab')
        disc(r, (x, y), 0.036, H - 0.003, H - 0.0005, 'led_off')
    add('bd_day', box(-4.05, -10, -5, -4.0, 14, 9), 'backdrop')
    add('bd_day', box(W + 4.0, -10, -5, W + 4.05, 14, 9), 'backdrop')
    add('bd_night', box(-4.07, -10, -5, -4.02, 14, 9), 'backdrop_night')
    add('bd_night', box(W + 4.02, -10, -5, W + 4.07, 14, 9), 'backdrop_night')
    edges = [D + 0.01, 2.85, 2.30, 1.75, 1.20, 0.62, -0.05]
    for k in range(6):
        add(f'floorW{k}', box(0, edges[k + 1], -0.012, CX, edges[k], 0.0), 'floor')
        add(f'floorE{k}', box(CX, edges[k + 1], -0.012, W, edges[k], 0.0), 'floor')
    # the tape line: half celery, half blue
    add('tape', box(CX - 0.04, 0.0, 0.0, CX, D, 0.0016), 'tapeA')
    add('tape', box(CX, 0.0, 0.0, CX + 0.04, D, 0.0016), 'tapeB')
    mat('rugA', tex=6, col=srgb(222, 228, 210)); mat('rugB', tex=6, col=srgb(214, 222, 232))
    add('rugA', rbox((CX - 0.40, 1.40, 0.007), (0.66, 0.92, 0.014), 0.006, 3), 'rugA')
    add('rugB', rbox((CX + 0.40, 1.40, 0.007), (0.66, 0.92, 0.014), 0.006, 3), 'rugB')


# ------------------------------------------------------------------------------------------- west: loft (child A)
def build_west(rng):
    for (y0, y1) in ((LY0 - 0.004, LY0 + 0.056), (D - 0.06, D)):        # the front post stands 4 mm proud of the deck face
        add('loftPosts', box(LX1 - 0.058, y0, 0.0, LX1 + 0.006, y1, LZ1 + 0.33), 'oak_z')
    add('loftDeck', box(0, LY0, LZ0, LX1, D, LZ0 + 0.004), 'white_in')
    wood('loftDeck', 0, LY0, LZ0 + 0.004, LX1 + 0.004, D, LZ1, 'oak')
    add('loftDeck', box(0.0, LY0 - 0.008, LZ0 - 0.006, LX1 - 0.058, LY0 - 0.001, LZ1 + 0.002), 'oak_x')     # front fascia
    add('loftDeck', box(LX1 - 0.09, LY0 + 0.1, LZ0 - 0.012, LX1 - 0.075, D - 0.1, LZ0), 'led_off')
    g = 'loftRail'
    wood(g, LX1 - 0.035, 1.78, LZ1 + 0.30, LX1, D, LZ1 + 0.33, 'oak')
    wood(g, 0.0, LY0, LZ1 + 0.30, LX1 - 0.06, LY0 + 0.035, LZ1 + 0.33, 'oak')
    for y in np.arange(1.80, D - 0.07, 0.075):
        add(g, box(LX1 - 0.03, y, LZ1, LX1 - 0.006, y + 0.03, LZ1 + 0.30), 'oak_z')
    for x in np.arange(0.03, LX1 - 0.08, 0.075):
        add(g, box(x, LY0 + 0.006, LZ1, x + 0.03, LY0 + 0.03, LZ1 + 0.30), 'oak_z')
    # ladder on the east face, south end
    for y in (1.47, 1.75):
        add('ladder', box(LX1 + 0.004, y - 0.018, 0.0, LX1 + 0.04, y + 0.018, LZ1 + 0.36), 'oak_z')
    for z in (0.32, 0.64, 0.96, 1.28):
        add('ladder', tube([(LX1 + 0.022, 1.47, z), (LX1 + 0.022, 1.75, z)], 0.016, 10), 'oak_y')
    add('matA', rbox((LX1 / 2 - 0.02, (LY0 + D) / 2, LZ1 + 0.075), (LX1 - 0.10, D - LY0 - 0.08, 0.15), 0.04, 5), 'mattress')
    cloth('duvetA', 0.02, LX1 - 0.07, LY0 + 0.05, 2.90, LZ1 + 0.165, LZ1 + 0.10, 0.032, 'duvetA', 3, sides=('e', 's'))
    add('duvetA', rbox((LX1 / 2 - 0.03, 2.87, LZ1 + 0.175), (LX1 - 0.08, 0.14, 0.025), 0.011, 3), 'linen_w')
    pillow('pilA1', (0.44, 3.27, LZ1 + 0.27), (0.56, 0.13, 0.34), -0.30, 'pil_white')
    pillow('pilA2', (0.62, 3.12, LZ1 + 0.24), (0.34, 0.11, 0.28), -0.22, 'pilA')
    # reading light on the west wall over the loft pillow
    rl = 'rlA'
    add(rl, xform(lathe(rprof(0.05, 0, 0.012, 0.004, 2), 24, (0, 0)), T(0.0, 2.95, LZ1 + 0.62) @ R('y', math.pi / 2)), 'oak_x')
    add(rl, tube([(0.012, 2.95, LZ1 + 0.62), (0.08, 2.95, LZ1 + 0.64)], 0.008, 8), 'oak_x')
    add(rl, lathe([(0.0, LZ1 + 0.565), (0.05, LZ1 + 0.565), (0.058, LZ1 + 0.60), (0.04, LZ1 + 0.655), (0, LZ1 + 0.66)], 24, (0.08, 2.95)), 'ceramic')
    # book wall: the south face of the under-loft, facing the door, four shelves
    f = 'bwFrame'
    xb1 = LX1 - 0.06
    add(f, box(0.0, LY0 - 0.012, 0.0, xb1, LY0, LZ0), 'white_in')
    add(f, box(xb1 - 0.018, BW_Y0, 0.0, xb1, LY0, LZ0), 'white_cab')
    add(f, box(0.0, BW_Y0, LZ0 - 0.02, xb1 - 0.018, LY0 - 0.012, LZ0 - 0.001), 'white_cab')   # top: closes the gap under the deck corner
    add(f, box(xb1, BW_Y0, LZ0 - 0.14, LX1, BW_Y0 + 0.018, LZ0), 'white_cab')
    for z in (0.0, 0.39, 0.77, 1.15):
        add(f, box(0.0, BW_Y0, z, xb1, LY0, z + 0.022), 'white_cab')
    pal = ['bk_terra', 'bk_mustard', 'bk_cream', 'bk_sage', 'bk_terra', 'bk_rust', 'bk_white', 'bk_mustard', 'bk_blue', 'bk_cream']
    for r_, z in enumerate((0.022, 0.412, 0.792, 1.172)):
        x = 0.02
        for g_ in range(3):
            nm = f'bw{r_}{g_}'
            xend = 0.02 + (xb1 - 0.06) * (g_ + 1) / 3
            while x < xend - 0.03:
                th = rng.uniform(0.022, 0.038)
                h = rng.uniform(0.20, 0.30) if r_ < 3 else rng.uniform(0.18, 0.28)
                m = pal[rng.integers(len(pal))]
                add(nm, box(x, BW_Y0 + 0.012, z, x + th, LY0 - 0.02, z + h), m)
                x += th + 0.003
            x += 0.01
    # under-loft desk, drawer, lamp, stool, LED
    wood('deskA', 0.0, 1.55, 0.68, 0.56, 2.60, 0.71, 'oak')
    add('deskA', box(0.52, 2.52, 0.0, 0.56, 2.56, 0.68), 'oak_z')
    drawer('ddrA', '+x', 0.56, 1.66, 2.42, 0.585, 0.675, 0.48, front='celery')
    add('ddcA', box(0.14, 1.72, 0.601, 0.40, 1.90, 0.616), 'bk_white')
    for k, m in enumerate(('toy_red', 'toy_yellow', 'toy_blue', 'toy_green')):
        add('ddcA', tube([(0.14 + 0.05 * k, 1.96, 0.612), (0.14 + 0.05 * k, 2.32, 0.612)], 0.007, 8), m)
    lp = 'lampA'
    disc(lp, (0.12, 2.42), 0.05, 0.71, 0.722, 'ceramic')
    add(lp, tube([(0.12, 2.42, 0.715), (0.12, 2.42, 1.0), (0.16, 2.38, 1.04)], 0.006, 8), 'ceramic')
    add(lp, lathe([(0.008, 1.07), (0.03, 1.06), (0.05, 1.02), (0.058, 0.995)], 24, (0.19, 2.35)), 'ceramic')
    add('lampOnA', ellipsoid((0.19, 2.35, 1.01), (0.018, 0.018, 0.018), 8), 'bulb')
    st = 'stoolA'
    for a in (0.6, 2.2, 3.8, 5.4):
        add(st, tube([(0.78 + 0.09 * math.cos(a), 2.05 + 0.09 * math.sin(a), 0.42), (0.78 + 0.15 * math.cos(a), 2.05 + 0.15 * math.sin(a), 0.0)],
                     0.013, 8), 'oak_z')
    disc(st, (0.78, 2.05), 0.16, 0.42, 0.45, 'oak_x')
    disc(st, (0.78, 2.05), 0.15, 0.45, 0.48, 'celery')


# ------------------------------------------------------------------------------------------- east: mid-sleeper (child B)
def build_east(rng):
    t = 0.018
    b = 'bedB'
    dy0, dy1, dz1 = 1.15, 1.75, 0.75                    # den door opening
    add(b, box(BX0, 0.05, 0.0, W, BY1, 0.02), 'white_in')
    add(b, box(BX0, 0.05, 0.0, BX0 + t, dy0, BZ0), 'white_cab')
    add(b, box(BX0, dy1, 0.0, BX0 + t, BY1, BZ0), 'white_cab')
    add(b, box(BX0, dy0, dz1, BX0 + t, dy1, BZ0), 'white_cab')
    add(b, box(BX0, BY1 - t, 0.0, W, BY1, BZ0), 'white_cab')
    add(b, box(BX0, 0.05, BZ0, W, BY1, BZ0 + 0.004), 'white_in')
    wood(b, BX0 - 0.004, 0.05, BZ0 + 0.004, W, BY1, BZ1, 'oak')
    add(b, box(BX0 + 0.03, 0.10, BZ0 - 0.012, W - 0.05, BY1 - 0.06, BZ0 - 0.002), 'white_in')
    g = 'railB'
    wood(g, BX0, 1.12, BZ1 + 0.28, BX0 + 0.035, BY1, BZ1 + 0.31, 'oak')
    wood(g, BX0, BY1 - 0.035, BZ1 + 0.28, W, BY1, BZ1 + 0.31, 'oak')
    for y in np.arange(1.14, BY1 - 0.06, 0.075):
        add(g, box(BX0 + 0.006, y, BZ1, BX0 + 0.03, y + 0.03, BZ1 + 0.28), 'oak_z')
    for x in np.arange(BX0 + 0.04, W - 0.04, 0.075):
        add(g, box(x, BY1 - 0.03, BZ1, x + 0.03, BY1 - 0.006, BZ1 + 0.28), 'oak_z')
    # den door (hinged at its south edge, opens out into the room)
    add('denDoor', box(BX0 - 0.004, dy0 + 0.004, 0.024, BX0 + 0.014, dy1 - 0.004, dz1 - 0.004), 'sky_blue')
    knob('denDoor', (BX0 - 0.004, dy1 - 0.07, 0.42), '-x')
    # den contents: floor cushions, picture books, a plush ball
    for k, (y, m) in enumerate(((0.45, 'pil_mustard'), (0.95, 'pilB'), (1.45, 'pil_white'))):
        add('denC', rbox((3.12, y, 0.09), (0.70, 0.46, 0.12), 0.05, 4), m)
    pillow('denC', (3.45, 1.25, 0.32), (0.44, 0.12, 0.34), 0.0, 'pil_terra', yaw=math.pi / 2)
    for k, m in enumerate(('bk_mustard', 'bk_blue', 'bk_terra', 'bk_sage')):
        add('denC', box(2.82 + 0.03 * k, 1.62, 0.15, 2.84 + 0.03 * k, 1.86, 0.40), m)
    add('denC', ellipsoid((2.95, 1.30, 0.23), (0.07, 0.07, 0.07), 14), 'toy_yellow')
    add('denLed', box(BX0 + 0.04, 0.15, BZ0 - 0.0135, BX0 + 0.06, BY1 - 0.1, BZ0 - 0.0125), 'led')
    # stair drawers: four columns rising north along the bed's west side, drawers facing the room (-x)
    for k in range(4):
        y0, y1 = SY0 + SRUN * k, SY0 + SRUN * (k + 1)
        top = SRZ * (k + 1)
        c = f'stB{k}'
        if k > 0:
            add(c, box(SX0, y0, 0.0, BX0, y1, SRZ * k), 'white_cab')
        add(c, box(SX0 + 0.02, y0, SRZ * k, BX0, y0 + 0.012, top - 0.028), 'white_in')
        add(c, box(SX0 + 0.02, y1 - 0.012, SRZ * k, BX0, y1, top - 0.028), 'white_in')
        wood(c, SX0 - 0.02, y0, top - 0.028, BX0, y1, top, 'oak')
        drawer(f'sdB{k}', '-x', SX0, y0 + 0.012, y1 - 0.012, SRZ * k + (0.012 if k == 0 else 0.0), top - 0.03, BX0 - SX0 - 0.03,
               front='oak_y')
    # contents (shoes, tees, blocks, art supplies)
    for dy in (-0.045, 0.045):
        add('sdBc0', ellipsoid((2.42, SY0 + 0.125 + dy, 0.065), (0.085, 0.032, 0.03), 10), 'shoe_white')
    stack('sdBc1', 2.44, SY0 + SRUN * 1.5, SRZ + 0.03, (0.30, 0.18, 0.04), ['cl_blue', 'cl_white', 'cl_mustard', 'cl_cream'], 3, rng)
    for k, (dx, dy, m) in enumerate(((-0.08, -0.05, 'toy_red'), (0.0, -0.05, 'toy_yellow'), (0.08, -0.05, 'toy_blue'),
                                     (-0.08, 0.05, 'toy_green'), (0.0, 0.05, 'toy_blue'), (0.08, 0.05, 'toy_red'))):
        add('sdBc2', rbox((2.44 + dx, SY0 + SRUN * 2.5 + dy, 2 * SRZ + 0.06), (0.07, 0.07, 0.06), 0.01, 3), m)
    for k, m in enumerate(('toy_red', 'toy_yellow', 'toy_blue', 'toy_green', 'bk_terra')):
        add('sdBc3', tube([(2.30, SY0 + SRUN * 3 + 0.05 + 0.03 * k, 3 * SRZ + 0.04), (2.56, SY0 + SRUN * 3 + 0.05 + 0.03 * k, 3 * SRZ + 0.04)],
                          0.008, 8), m)
    add('matB', rbox(((BX0 + W) / 2, (0.05 + BY1) / 2, BZ1 + 0.075), (W - BX0 - 0.06, BY1 - 0.13, 0.15), 0.04, 5), 'mattress')
    cloth('duvetB', BX0 + 0.04, W - 0.02, 0.10, 1.48, BZ1 + 0.165, BZ1 + 0.10, 0.032, 'duvetB', 5, sides=('w',))
    add('duvetB', rbox(((BX0 + W) / 2 + 0.01, 1.46, BZ1 + 0.175), (W - BX0 - 0.08, 0.14, 0.025), 0.011, 3), 'linen_w')
    pillow('pilB1', (3.12, 1.86, BZ1 + 0.27), (0.56, 0.13, 0.34), 0.30, 'pil_white', yaw=math.pi)
    pillow('pilB2', (2.94, 1.74, BZ1 + 0.24), (0.34, 0.11, 0.28), 0.22, 'pilB', yaw=math.pi)
    rl = 'rlB'
    add(rl, xform(lathe(rprof(0.05, 0, 0.012, 0.004, 2), 24, (0, 0)), T(W, 1.62, BZ1 + 0.95) @ R('y', -math.pi / 2)), 'oak_x')
    add(rl, tube([(W - 0.012, 1.62, BZ1 + 0.95), (W - 0.08, 1.62, BZ1 + 0.97)], 0.008, 8), 'oak_x')
    add(rl, lathe([(0.0, BZ1 + 0.895), (0.05, BZ1 + 0.895), (0.058, BZ1 + 0.93), (0.04, BZ1 + 0.985), (0, BZ1 + 0.99)], 24, (W - 0.08, 1.62)),
        'ceramic')
    # small desk north of the bed (outside the swing arc)
    wood('deskB', 3.16, 2.16, 0.68, W, 2.86, 0.71, 'oak')
    add('deskB', box(3.16, 2.16, 0.0, 3.20, 2.20, 0.68), 'oak_z'); add('deskB', box(3.16, 2.82, 0.0, 3.20, 2.86, 0.68), 'oak_z')
    drawer('ddrB', '-x', 3.16, 2.24, 2.78, 0.585, 0.675, 0.40, front='sky_blue')
    add('ddcB', box(3.26, 2.30, 0.601, 3.46, 2.48, 0.616), 'bk_white')
    for k, m in enumerate(('toy_green', 'toy_blue', 'toy_yellow', 'toy_red')):
        add('ddcB', tube([(3.26, 2.54 + 0.04 * k, 0.612), (3.50, 2.54 + 0.04 * k, 0.612)], 0.007, 8), m)
    lp = 'lampB'
    disc(lp, (W - 0.10, 2.76), 0.05, 0.71, 0.722, 'ceramic')
    add(lp, tube([(W - 0.10, 2.76, 0.715), (W - 0.10, 2.76, 1.0), (W - 0.14, 2.72, 1.04)], 0.006, 8), 'ceramic')
    add(lp, lathe([(0.008, 1.07), (0.03, 1.06), (0.05, 1.02), (0.058, 0.995)], 24, (W - 0.17, 2.69)), 'ceramic')
    add('lampOnB', ellipsoid((W - 0.17, 2.69, 1.01), (0.018, 0.018, 0.018), 8), 'bulb')
    wood('shB', W - 0.22, 2.20, 1.25, W, 2.84, 1.275, 'oak')
    y = 2.24
    for m, th, h in (('bk_blue', 0.03, 0.21), ('bk_white', 0.026, 0.18), ('bk_mustard', 0.034, 0.22), ('bk_navy', 0.03, 0.2), ('bk_cream', 0.028, 0.19)):
        add('shB', box(W - 0.19, y, 1.275, W - 0.03, y + th, 1.275 + h), m); y += th + 0.004
    plant('shB', W - 0.11, 2.70, 1.275, 0.045, 0.07, rng, 8)


# ------------------------------------------------------------------------------------------- the turning wardrobe (parked)
WR_PIECES = []


def wadd(inst, pn, m):
    if inst not in WR_PIECES:
        WR_PIECES.append(inst)
    add(inst, pn, m)


def build_wardrobe(rng):
    t = 0.018
    x0, x1, y0, y1, z0, z1 = WRX0, WRX1, WRY0, WRY1, WRZ0, WRZ1
    yc = (y0 + y1) / 2
    hx0, hx1, hz0, hz1 = 2.62, 3.00, 1.02, 1.30          # the hatch tunnel (both faces)
    xv = 2.565                                           # face A: doors | right column
    B = 'wrBody'
    for b in (box(x0, y0, z0, x0 + t, y1, z1), box(x1 - t, y0, z0, x1, y1, z1), box(x0, y0, z1 - t, x1, y1, z1),
              box(x0, y0, z0, x1, y1, z0 + t)):
        wadd(B, b, 'white_cab')
    wadd(B, box(x0 - 0.002, y0 - 0.002, z1, x1 + 0.002, y1 + 0.002, z1 + 0.02), 'oak_x')
    # centre divider with the hatch hole
    for b in (box(x0, yc - 0.008, z0, hx0, yc + 0.008, z1), box(hx1, yc - 0.008, z0, x1, yc + 0.008, z1),
              box(hx0, yc - 0.008, z0, hx1, yc + 0.008, hz0), box(hx0, yc - 0.008, hz1, hx1, yc + 0.008, z1)):
        wadd(B, b, 'white_in')
    # face A interior: drawer housing, doors' shelves, right column shelves, hatch tunnel
    wadd(B, box(x0 + t, y0, 0.645, x1 - t, yc, 0.663), 'white_in')
    wadd(B, box(xv, y0, 0.663, xv + t, yc, z1 - t), 'white_in')
    for z in (1.08, 1.50, 1.90):
        wadd(B, box(x0 + t, y0 + 0.02, z, xv, yc, z + 0.016), 'white_in')
    for z in (hz0 - 0.016, hz1, 1.75):
        wadd(B, box(xv + t, y0, z, x1 - t, yc, z + 0.016), 'white_in')
    wadd(B, box(xv + t, y0, 0.663, x1 - t, y0 + t, hz0 - 0.016), 'oak_x')           # closed panel under the hatch
    for b in (box(hx0 - 0.02, y0, hz0, hx0, y1, hz1), box(hx1, y0, hz0, hx1 + 0.02, y1, hz1), box(hx0, y0, hz0 - 0.016, hx1, y1, hz0),
              box(hx0, y0, hz1, hx1, y1, hz1 + 0.016)):
        wadd(B, b, 'oak_y')
    # face B: open cubby grid (blue frame), the hatch in the right column
    cols = [x0 + t, x0 + (x1 - x0) / 3, x0 + 2 * (x1 - x0) / 3, x1 - t]
    for xd in cols[1:3]:
        wadd(B, box(xd - 0.009, yc, z0 + t, xd + 0.009, y1, z1 - t), 'sky_blue')
    rows = [z0 + t, 0.60, hz0 - 0.016, hz1 + 0.016, 1.76, z1 - t]
    for z in rows[1:5]:
        wadd(B, box(x0 + t, yc, z - 0.009, x1 - t, y1, z + 0.009), 'sky_blue')
    # casters + base rail
    for (cx, cy) in ((x0 + 0.08, y0 + 0.07), (x0 + 0.08, y1 - 0.07), (x1 - 0.08, y0 + 0.07), (x1 - 0.08, y1 - 0.07), ((x0 + x1) / 2, yc)):
        wadd('wrBody', xform(lathe(rprof(0.024, -0.012, 0.012, 0.006, 3), 16, (0, 0)), T(cx, cy, 0.025) @ R('x', math.pi / 2)), 'caster')
        wadd('wrBody', box(cx - 0.02, cy - 0.02, 0.045, cx + 0.02, cy + 0.02, z0), 'steel')
    # face A fronts: two drawers, two doors, hatch door
    drawer('wrDrA0', '-y', y0, x0 + t, x1 - t, z0 + 0.02, 0.36, yc - y0 - 0.02, front='oak_x', knobs=2)
    drawer('wrDrA1', '-y', y0, x0 + t, x1 - t, 0.36, 0.643, yc - y0 - 0.02, front='oak_x', knobs=2)
    for nm in ('wrDrA0', 'wrDrA1'):
        WR_PIECES.append(nm)
    wadd('wrDoorA1', box(x0 + t + 0.002, y0 - 0.018, 0.666, (x0 + xv) / 2 - 0.002, y0, z1 - t - 0.002), 'oak_z')
    wadd('wrDoorA2', box((x0 + xv) / 2 + 0.002, y0 - 0.018, 0.666, xv + t - 0.002, y0, z1 - t - 0.002), 'oak_z')
    knob('wrDoorA1', ((x0 + xv) / 2 - 0.04, y0 - 0.018, 1.25), '-y')
    knob('wrDoorA2', ((x0 + xv) / 2 + 0.04, y0 - 0.018, 1.25), '-y')
    wadd('wrHatchA', box(hx0 + 0.003, y0 - 0.018, hz0 + 0.003, hx1 - 0.003, y0, hz1 - 0.003), 'celery')
    knob('wrHatchA', (hx1 - 0.05, y0 - 0.018, (hz0 + hz1) / 2), '-y', r=0.012)
    wadd('wrHatchB', box(hx0 + 0.003, y1, hz0 + 0.003, hx1 - 0.003, y1 + 0.018, hz1 - 0.003), 'sky_blue')
    # contents: folded stacks behind the doors, boxes in the right column, drawer contents, face B bins + books
    for k, z in enumerate((0.663, 1.096, 1.516, 1.916)):
        for j, xc in enumerate((1.75, 2.15, 2.42)):
            if xc + 0.12 > xv:
                continue
            stack('wrFold', xc, y0 + 0.13, z, (0.26, 0.20, 0.045), [('cl_white', 'cl_celery', 'cl_grey'), ('cl_cream', 'cl_sage', 'cl_navy'),
                                                                   ('cl_mustard', 'cl_white', 'cl_denim'), ('cl_celery', 'cl_cream', 'cl_terra')][(k + j) % 4],
                  3 if z < 1.9 else 2, rng)
    WR_PIECES.append('wrFold')
    for z in (1.316, 1.766):
        wadd('wrBoxA', rbox(((xv + x1) / 2, y0 + 0.13, z + 0.17), (0.38, 0.22, 0.30), 0.015, 3), 'fb_blue' if z < 1.5 else 'fb_sage')
    stack('wrDrAc', 1.85, y0 + 0.13, 0.39, (0.30, 0.18, 0.04), ['cl_white', 'cl_celery', 'cl_grey'], 3, rng)
    stack('wrDrAc', 2.25, y0 + 0.13, 0.39, (0.30, 0.18, 0.04), ['cl_mustard', 'cl_cream', 'cl_sage'], 3, rng)
    stack('wrDrAc', 2.68, y0 + 0.13, 0.39, (0.30, 0.18, 0.04), ['cl_denim', 'cl_white', 'cl_terra'], 3, rng)
    WR_PIECES.append('wrDrAc')
    binm = ['fb_terra', 'fb_mustard', 'fb_cream', 'fb_sage', 'fb_terra', 'fb_mustard', 'fb_cream', 'fb_sage', 'fb_mustard', 'fb_terra', 'fb_sage', 'fb_cream']
    k = 0
    for ri in (0, 1, 3, 4):
        za, zb = rows[ri] + 0.012, rows[ri + 1] - 0.012
        for ci in range(3):
            xa, xb = cols[ci] + 0.012, cols[ci + 1] - 0.012
            h = min(0.30, zb - za - 0.06)
            wadd(f'wrBin{k}', rbox(((xa + xb) / 2, y1 - 0.12, za + h / 2), (xb - xa - 0.05, 0.20, h), 0.006, 2), binm[k])
            k += 1
    for ci in range(2):
        xa = cols[ci] + 0.03
        xx = xa
        for m in ('bk_blue', 'bk_mustard', 'bk_white', 'bk_terra', 'bk_navy', 'bk_cream', 'bk_sage'):
            wadd('wrBooksB', box(xx, y1 - 0.20, hz0 + 0.002, xx + 0.03, y1 - 0.03, hz0 + 0.2), m); xx += 0.034
            if xx > cols[ci + 1] - 0.08:
                break
    # telescoping end panel (stored inside the far end; slides out along the wardrobe)
    wadd('wrPanel', box(x1 - PNL, yc - 0.006, z0 + 0.03, x1 - 0.004, yc + 0.006, z1 - 0.03), 'white_in')
    for xs in np.arange(x1 - PNL + 0.01, x1 - 0.03, 0.06):
        wadd('wrPanel', box(xs, yc - 0.024, z0 + 0.03, xs + 0.038, yc + 0.024, z1 - 0.03), 'oak_z')
    wadd('wrPanel', box(x1 - 0.004, yc - 0.025, z0 + 0.03, x1 + 0.016, yc + 0.025, z1 - 0.03), 'oak_z')
    # pivot post and floor track (fixed)
    add('pivot', tube([(PIV[0], PIV[1], 0.0), (PIV[0], PIV[1], H)], 0.022, 14), 'steel')
    disc('pivot', PIV, 0.06, 0.0, 0.012, 'steel')
    disc('pivot', PIV, 0.06, H - 0.012, H, 'steel')
    n = 40
    V = np.zeros((n, 2, 3))
    for i, a in enumerate(np.linspace(-math.pi / 2 - 0.05, 0.05, n)):
        for j, rr in enumerate((TRK_R - 0.022, TRK_R + 0.022)):
            V[i, j] = (PIV[0] + rr * math.cos(a), PIV[1] + rr * math.sin(a), 0.0035)
    add('track', grid_tris(V), 'track_m')


LONG_ONLY = ('table', 'tableLid', 'tableC', 'stool1', 'stool2', 'beanbag', 'floorLamp', 'hatchBook')


def build_long_extras(rng):
    """Shared play corner for the long cut: a round play table with a lift-up lid + two stools on the rug; a beanbag."""
    c = (CX, 1.42)
    disc('table', c, 0.30, 0.30, 0.33, 'oak_x')
    for a in (0.8, 2.4, 3.9, 5.5):
        add('table', tube([(c[0] + 0.2 * math.cos(a), c[1] + 0.2 * math.sin(a), 0.30), (c[0] + 0.26 * math.cos(a), c[1] + 0.26 * math.sin(a), 0.015)],
                          0.014, 8), 'oak_z')
    add('table', lathe([(0.0, 0.33), (0.26, 0.33), (0.26, 0.42), (0.245, 0.42), (0.245, 0.345), (0.0, 0.345)], 32, c), 'white_cab')
    disc('tableLid', c, 0.275, 0.42, 0.445, 'oak_x')
    for k, (dx, dy, m) in enumerate(((-0.1, -0.05, 'toy_red'), (0.05, -0.1, 'toy_yellow'), (0.1, 0.06, 'toy_blue'), (-0.05, 0.1, 'toy_green'))):
        add('tableC', rbox((c[0] + dx, c[1] + dy, 0.39), (0.08, 0.08, 0.07), 0.01, 3), m)
    for nm, x, m in (('stool1', CX - 0.48, 'celery'), ('stool2', CX + 0.48, 'sky_blue')):
        disc(nm, (x, 1.42), 0.14, 0.0, 0.22, m)
    add('plushB', ellipsoid((2.18, 1.22, 0.104), (0.09, 0.08, 0.09), 16), 'toy_white')
    add('plushB', ellipsoid((2.18, 1.22, 0.224), (0.065, 0.06, 0.06), 14), 'toy_white')
    add('hatchBook', box(1.72, 2.07, 1.035, 1.88, 2.21, 1.062), 'bk_mustard')
    add('beanbag', ellipsoid((2.55, 2.55, 0.20), (0.36, 0.34, 0.22), 18), 'fb_blue')
    add('floorLamp', lathe(rprof(0.11, 0.0, 0.015, 0.005, 3), 24, (3.38, 3.18)), 'ceramic')
    add('floorLamp', tube([(3.38, 3.18, 0.01), (3.38, 3.18, 1.35)], 0.008, 8), 'ceramic')
    add('floorLamp', lathe([(0.0, 1.50), (0.06, 1.50), (0.13, 1.36), (0.12, 1.355), (0.0, 1.49)], 24, (3.38, 3.18)), 'ceramic')


LONG_SIT = dict(hip_l=88, hip_r=88, knee_l=6, knee_r=6, ankle_l=10, ankle_r=10, spine=10, neck=14, sh_l=42, sh_r=42,
                elbow_l=62, elbow_r=62, sh_l_out=8, sh_r_out=8)
KID_A = KID_B = None


def build():
    global KID_A, KID_B
    materials()
    rng = np.random.default_rng(9)
    build_shell()
    build_west(rng)
    build_east(rng)
    build_wardrobe(rng)
    build_long_extras(rng)
    add('ledLoft', box(LX1 - 0.09, LY0 + 0.1, LZ0 - 0.0125, LX1 - 0.075, D - 0.1, LZ0 - 0.0115), 'led')
    add('rlOnA', ellipsoid((0.08, 2.95, LZ1 + 0.565), (0.04, 0.04, 0.008), 10), 'bulb')
    add('rlOnB', ellipsoid((W - 0.08, 1.62, BZ1 + 0.895), (0.04, 0.04, 0.008), 10), 'bulb')
    for (x, y) in DL:
        disc('dlOn', (x, y), 0.037, H - 0.005, H - 0.0035, 'dl_emis')
    KID_A = fg.figure('kidA', 'child', pose=LONG_SIT, at=(0.33, 2.55, 90), seat=LZ1 + 0.15, mat='fig_white')
    KID_B = fg.figure('kidB', 'child', pose=LONG_SIT, at=(3.02, 1.72, 180), seat=BZ1 + 0.15, mat='fig_blue')


# ------------------------------------------------------------------------------------------- camera
VFOV = 85.0


def P(x, y, z, yaw, pitch, vf=VFOV):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch, vf=vf)


F1 = P(CX, -0.45, 1.40, 0.0, -12.0, 88.0)
S1 = (F1, P(CX, 0.55, 1.50, 0.0, -15.0, 88.0))                                             # doorway, down the tape
S1B = (P(1.80, 0.64, 1.50, -32.0, -13.0), P(1.62, 0.78, 1.44, -42.0, -12.0))          # A: book wall + loft                                               # doorway, down the tape
S2 = (P(1.12, 0.18, 0.98, 60.0, -11.0), P(1.42, 0.72, 0.86, 74.0, -6.0))              # B: stair drawers + den
S3 = (P(1.30, 0.30, 1.95, 16.0, -17.0), P(0.92, 0.16, 1.86, 18.0, -16.0))
S3B = (P(2.98, 1.62, 1.74, -44.0, -13.0), P(2.86, 1.76, 1.72, -58.0, -11.0))
S3W = (P(CX, 0.04, 1.92, 0.0, -19.0, 95.0), P(CX, 0.14, 1.86, 0.0, -19.0, 95.0))        # daylight payoff wide on the tape (inside the door)
S3O = (P(1.95, 0.40, 2.56, 4.0, -57.0, 100.0), P(2.10, 0.56, 2.54, -8.0, -62.0, 100.0))  # near-overhead: the swing          # face B: the cubbies fill   # near-overhead: the swing (wow)
S4 = (P(CX, 0.14, 2.22, -24.0, -22.0, 98.0), P(CX, 0.16, 2.18, -10.0, -23.0, 98.0))      # night: A's side
S5 = (P(CX, 0.16, 2.18, 20.0, -24.0, 98.0), F1)                                        # B's side -> frame 1                                                # the two bedrooms -> frame 1
HOLDS = [(0.0, 2.45, S1), (2.70, 3.70, S1B), (3.72, 7.00, S2), (7.04, 8.00, S3), (8.04, 9.56, S3O), (9.60, 10.32, S3W),
         (10.52, 11.45, S3B), (11.65, 12.40, S4), (12.60, DUR, S5)]


def make_camera(holds):
    base = hold_camera(holds, VFOV, rest=REST)

    def vf_at(t):
        if REST:
            return holds[min(len(holds) - 1, int(t))][2][0].get('vf', VFOV)
        for i, (t0, t1, st) in enumerate(holds):
            a = st[0].get('vf', VFOV); b = st[1].get('vf', VFOV)
            if t < t1 or i == len(holds) - 1:
                return a + (b - a) * c01((t - t0) / (t1 - t0))
            n0 = holds[i + 1][0]
            if t < n0:
                nb = holds[i + 1][2][0].get('vf', VFOV)
                return b + (nb - b) * smooth((t - t1) / (n0 - t1))
        return VFOV

    def camera(t):
        c = dict(base(t))
        c['vfov'] = vf_at(t)
        return c
    return camera


# ------------------------------------------------------------------------------------------- lights (fixed slots)
LSKY = (9.0, 9.5, 10.4)
LSUN = (95000.0, 86000.0, 72000.0)
LDOOR = (2.2, 2.2, 2.15)
LFILL = (0.6, 0.6, 0.59)
LLED = (40.0, 36.0, 29.0)
LRL = (1300.0, 1060.0, 760.0)
LLAMP = (110.0, 90.0, 62.0)
LDOWN = (1050.0, 1065.0, 1070.0)
LDEN = (70.0, 60.0, 44.0)


def lights(mats4, vis):
    off = (0.0, 0.0, 0.0)
    night = bool(vis.get('bd_night'))
    dim = 0.85 if (not night and vis.get('rlOnA')) else 1.0    # lamps on in daylight (long cut): daylight eases to 85 %

    def k(L, on, f=1.0):
        return tuple(v * f for v in L) if on else off
    Ls = []
    Ls.append(rect_light((-0.16, WY0, WZ0), (0, WY1 - WY0, 0), (0, 0, WZ1 - WZ0), k(LSKY, not night, dim), always=1))          # 0 sky W (+x)
    Ls.append(rect_light((W + 0.16, WY0, WZ0), (0, 0, WZ1 - WZ0), (0, WY1 - WY0, 0), k(LSKY, not night, dim), always=1))       # 1 sky E (-x)
    sc = np.array([0.0, (WY0 + WY1) / 2, (WZ0 + WZ1) / 2]) - SUN_DIR * 3.0
    Ls.append(spot_rect(tuple(sc), tuple(SUN_DIR), 0.06, k(LSUN, not night, dim), 0.0))                                  # 2 sun (W)
    Ls.append(rect_light((DX0, -0.4, 0.2), (0, 0, 1.9), (DX1 - DX0, 0, 0), k(LDOOR, True, 0.7 if night else 1.0), always=1))  # 3 +y
    Ls.append(rect_light((0.4, 0.3, H - 0.012), (0, D - 0.6, 0), (W - 0.8, 0, 0), k(LFILL, True, 1.6 if night else 1.0)))     # 4 down
    Ls.append(spot_rect((0.08, 2.95, LZ1 + 0.56), (0.35, 0.0, -1.0), 0.03, k(LRL, vis.get('rlOnA')), 5.0))                # 5
    Ls.append(spot_rect((W - 0.08, 1.62, BZ1 + 0.89), (-0.35, 0.0, -1.0), 0.03, k(LRL, vis.get('rlOnB')), 5.0))           # 6
    Ls.append(rect_light((LX1 - 0.09, LY0 + 0.1, LZ0 - 0.013), (0, D - LY0 - 0.2, 0), (0.015, 0, 0), k(LLED, vis.get('ledLoft'))))  # 7
    Ls.append(sphere_light((0.19, 2.35, 1.01), 0.018, k(LLAMP, vis.get('lampOnA'))))                                       # 8
    Ls.append(sphere_light((W - 0.17, 2.69, 1.01), 0.018, k(LLAMP, vis.get('lampOnB'))))                                   # 9
    for (x, y) in DL:                                                                                                    # 10-11
        Ls.append(spot_rect((x, y, H - 0.006), (0, 0, -1), 0.05, k(LDOWN, vis.get('dlOn')), 4.0))
    Ls.append(rect_light((BX0 + 0.04, 0.15, BZ0 - 0.014), (0, BY1 - 0.25, 0), (0.02, 0, 0), k(LDEN, vis.get('denLed'))))  # 12 den
    return Ls


BLENDER = dict(
    exposure=-0.30,
    look='AgX - Medium High Contrast',
    separate=['backdrop', 'backdrop_night'],
    fill_lights=[3, 4],
    wood_scale=(55.0, 1.6),
    bake_rect={'backdrop': (-3.0, 7.0, -2.0, 6.0), 'backdrop_night': (-3.0, 7.0, -2.0, 6.0)},
    bake_px={'backdrop': 0.006, 'backdrop_night': 0.004, 'floor': 0.0015},
)


# ------------------------------------------------------------------------------------------- timeline
NIGHT_PIECES = ('bd_night', 'ledLoft', 'rlOnA', 'rlOnB', 'dlOn', 'lampOnA', 'lampOnB', 'denLed')


def swung_local(name):
    """Local transform of a wardrobe piece in the swung rest view."""
    if name == 'wrPanel':
        return T(PNL - 0.02, 0, 0)
    return np.eye(4)


def swing_M(a_deg):
    return about((PIV[0], PIV[1], 0.0), R('z', math.radians(a_deg)))


def timeline():
    tl = Timeline(rk, FPS)
    if REST:
        return rest_timeline(tl)
    st = Story(tl)
    return st.short() if CUT != 'long' else st.long()


def rest_timeline(tl):
    I = np.eye(4)
    hidden = lambda t: (I, False)
    if REST_NIGHT:
        tl.custom('bd_day', hidden)
    else:
        for nm in NIGHT_PIECES:
            tl.custom(nm, hidden)
    for nm in LONG_ONLY:
        tl.custom(nm, hidden)
    if not REST_SWUNG:
        for nm in KID_A.pieces + KID_B.pieces:
            tl.custom(nm, hidden)
    else:
        for nm in WR_PIECES:
            tl.custom(nm, lambda t, nm=nm: (swing_M(-90) @ swung_local(nm), True))
    if REST_OPEN:
        for k in range(4):
            for nm in (f'sdB{k}', f'sdBc{k}'):
                tl.custom(nm, lambda t: (T(-0.28, 0, 0), True))
        tl.custom('denDoor', lambda t: (about((BX0, 1.15, 0), R('z', math.radians(100))), True))
        for nm, sg in (('ddrA', 1), ('ddcA', 1), ('ddrB', -1), ('ddcB', -1)):
            tl.custom(nm, lambda t, sg=sg: (T(sg * 0.28, 0, 0), True))
    return tl


class Story:
    """Grouped beats; the short and long cuts share them. Wardrobe pieces are animated in their parked (local) frame and
    composed with the landing slam and the swing at the end (finish_wardrobe)."""

    def __init__(self, tl):
        self.tl, self.I = tl, np.eye(4)
        self.swings = []                      # (t0, t1, a0, a1, kind)
        self.wr_land = 1.50

    # ---------------------------------------------------------------- primitives
    def appear(self, name, t_on, t_off=None):
        self.tl.custom(name, lambda t: (self.I, t >= t_on and (t_off is None or t < t_off)))

    def hide(self, *names):
        for nm in names:
            self.tl.custom(nm, lambda t: (self.I, False))

    def drawer_fn(self, t_appear, t_open, t_close, off, base=None, out=0.16, shut=0.17):
        I, off = self.I, np.array(off, float)

        def f(t):
            if base is not None:
                B, bv = base(t)
                if not bv:
                    return I, False
            else:
                B = I
                if t < t_appear:
                    return I, False
            if t < t_open:
                return B, True
            if t < t_close:
                return B @ T(*(off * eob((t - t_open) / out, 1.6))), True
            kk = 1 - smooth((t - t_close) / shut)
            tau = t - t_close - shut
            wob = 0.006 * math.exp(-tau / 0.05) * math.sin(2 * math.pi * tau / 0.12) if tau > 0 else 0.0
            return B @ T(*(off * kk + off / (np.linalg.norm(off) + 1e-9) * wob)), True
        return f

    def hinge_fn(self, hinge, a_open, t_open, t_close, base=None, axis='z', out=0.28, shut=0.2):
        I, hinge = self.I, np.array(hinge, float)

        def f(t):
            B, bv = base(t) if base is not None else (I, True)
            if not bv:
                return I, False
            if t < t_open:
                return B, True
            if t < t_close:
                return about(hinge, R(axis, a_open * eob(c01((t - t_open) / out), 1.2))) @ B, True
            u = (t - t_close) / shut
            if u < 1:
                return about(hinge, R(axis, a_open * (1 - u * u))) @ B, True
            tau = t - t_close - shut
            a = math.copysign(math.radians(1.5), a_open) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))
            return about(hinge, R(axis, a)) @ B, True
        return f

    def static_after(self, name, t_vis, base=None):
        self.tl.custom(name, lambda t: ((base(t)[0] if base else self.I), t >= t_vis and (base is None or base(t)[1])))

    # ---------------------------------------------------------------- the swing
    def swing(self, t0, t1, a0, a1, kind='swing'):
        self.swings.append((t0, t1, a0, a1, kind))
        if kind == 'swing':
            self.tl.ev(t0 + 0.12, 'whoosh', 0.7, 'swish')
            self.tl.ev(t1, 'latch', 1.0, 'thud')
        else:
            self.tl.ev(t0 + 0.05, 'nudge', 0.4, 'swish')

    def angle(self, t):
        a = 0.0
        for (t0, t1, a0, a1, kind) in sorted(self.swings):
            if t < t0:
                break
            if kind == 'nudge':                   # out to a1 and back to a0, with a settle
                tm = t0 + 0.42 * (t1 - t0)
                if t < tm:
                    a = a0 + (a1 - a0) * eoc((t - t0) / (tm - t0))
                elif t < t1:
                    a = a1 + (a0 - a1) * smooth((t - tm) / (t1 - tm))
                else:
                    tau = t - t1
                    a = a0 + (a1 - a0) * -0.05 * math.exp(-tau / 0.06) * math.sin(math.pi * tau / 0.1)
            else:
                if t < t1:
                    u = (t - t0) / (t1 - t0)
                    a = a0 + (a1 - a0) * smooth(smooth(u))
                else:
                    tau = t - t1
                    a = a1 + (a1 - a0) * 0.012 * math.exp(-tau / 0.06) * math.sin(math.pi * tau / 0.09)
        return a

    def finish_wardrobe(self):
        tl, I = self.tl, self.I
        tw = self.wr_land
        tl.ev(tw, 'wardrobe_slam', 1.0, 'thud')

        def land(t):
            if t < tw - 0.2:
                return I, False
            u = (t - tw + 0.2) / 0.2
            if u < 1:
                return T(0, -0.9 * (1 - eob(u, 0.6)), 0.25 * (1 - u * u)), True
            tau = t - tw
            return T(0, 0.006 * math.exp(-tau / 0.05) * math.sin(2 * math.pi * tau / 0.1), 0), True
        for nm in WR_PIECES:
            L = tl.anims.get(nm, lambda t: (I, True))

            def f(t, L=L):
                Ml, vl = land(t)
                if not vl:
                    return I, False
                M, v = L(t)
                return swing_M(self.angle(t)) @ Ml @ M, v
            tl.custom(nm, f)

    def panel(self, t_out, t_in=None):
        def f(t):
            if t < t_out:
                return self.I, True
            if t_in is None or t < t_in:
                return T((PNL - 0.02) * eob(c01((t - t_out) / 0.32), 0.5), 0, 0), True
            return T((PNL - 0.02) * (1 - smooth(c01((t - t_in) / 0.30))), 0, 0), True
        self.tl.custom('wrPanel', f)
        self.tl.ev(t_out + 0.32, 'panel_out', 0.8, 'thud')
        if t_in is not None:
            self.tl.ev(t_in + 0.06, 'panel_in', 0.4, 'swish')

    # ---------------------------------------------------------------- beats
    def build_beat(self, t0):
        tl, drop, slide, grow = self.tl, self.tl.drop, self.tl.slide, self.tl.grow
        grow('tape', t0 - 0.10, t0 + 0.24, 'y', (0, D, 0), 0.6, 'swish')
        for k in range(6):
            t1 = t0 + 0.32 + 0.08 * k
            drop(f'floorW{k}', t1 - 0.18, t1, 0.45, 0.05, 0.3 + 0.03 * k, 'tick')
            drop(f'floorE{k}', t1 - 0.18, t1, 0.45, 0.05, 0.0, 'none')
        drop('loftPosts', t0 + 0.96, t0 + 1.12, 0.6, 0.02, 0.0, 'none')
        drop('loftDeck', t0 + 1.06, t0 + 1.22, 0.5, 0.03, 1.0, 'thud')
        drop('bedB', t0 + 1.06, t0 + 1.22, 0.5, 0.03, 0.0, 'none')
        self.static_after('denDoor', t0 + 1.06, base=tl.anims['bedB'])
        drop('pivot', t0 + 1.20, t0 + 1.34, 0.6, 0.02, 0.7, 'thud')
        drop('track', t0 + 1.28, t0 + 1.42, 0.25, 0.02, 0.35, 'tick')
        self.wr_land = t0 + 1.55
        slide('ladder', t0 + 1.66, t0 + 1.80, (0.4, 0, 0), 1.0, 0.0, 'none')
        for k in range(4):
            tt = t0 + 1.68 + 0.09 * k
            drop(f'stB{k}', tt - 0.13, tt, 0.35, 0.03, 0.5, 'thud')
            self.static_after(f'sdB{k}', tt - 0.13, base=tl.anims[f'stB{k}'])
        slide('loftRail', t0 + 2.02, t0 + 2.16, (0.4, 0, 0), 1.0, 0.0, 'none')
        slide('railB', t0 + 2.02, t0 + 2.16, (-0.4, 0, 0), 1.0, 0.5, 'thud')
        self.swing(t0 + 2.05, t0 + 2.70, 0.0, -28.0, 'nudge')
        drop('matA', t0 + 2.26, t0 + 2.42, 0.4, 0.05, 0.7, 'thud')
        drop('matB', t0 + 2.26, t0 + 2.42, 0.4, 0.05, 0.0, 'none')
        tl.ev(t0 + 2.72, 'nudge_clunk', 0.7, 'thud')
        drop('duvetA', t0 + 2.50, t0 + 2.66, 0.35, 0.03, 0.0, 'none')
        drop('duvetB', t0 + 2.50, t0 + 2.66, 0.35, 0.03, 0.0, 'none')
        for i, (a, b) in enumerate((('pilA1', 'pilB1'), ('pilA2', 'pilB2'))):
            tt = t0 + 2.80 + 0.10 * i
            drop(a, tt - 0.16, tt, 0.35, 0.08, 0.35)
            drop(b, tt - 0.16, tt, 0.35, 0.08, 0.0, 'none')
        # the book wall fills left to right (whole columns at a time)
        tl.drop('bwFrame', t0 + 2.70, t0 + 2.84, 0.3, 0.02, 0.0, 'none')
        for g in range(3):
            for r in range(4):
                tt = t0 + 3.00 + 0.18 * g + 0.035 * r
                tl.from_camera(f'bw{r}{g}', tt - 0.16, tt, np.array(F1['pos']), 0.25, 0.35 if r == 0 else 0.0, 'tick' if r == 0 else 'none')
        slide('rlA', t0 + 3.20, t0 + 3.34, (0.25, 0, 0), 1.0, 0.0, 'none')
        slide('rlB', t0 + 3.20, t0 + 3.34, (-0.25, 0, 0), 1.0, 0.35, 'tick')
        drop('rugA', t0 + 3.42, t0 + 3.58, 0.3, 0.02, 0.4, 'thud')
        drop('rugB', t0 + 3.42, t0 + 3.58, 0.3, 0.02, 0.0, 'none')
        for s in ('A', 'B'):
            self.static_after(f'desk{s}', 0.0)

    def desks_quick(self, t0):
        """Both desks (seen in the long cut; in the 15 s cut they land off-screen during S2)."""
        tl = self.tl
        a = tl.slide('deskA', t0, t0 + 0.16, (-0.6, 0, 0), 1.0, 0.0, 'none')
        b = tl.slide('deskB', t0, t0 + 0.16, (0.5, 0, 0), 1.0, 0.0, 'none')
        self.static_after('ddrA', t0, base=a); self.static_after('ddrB', t0, base=b)
        tl.drop('lampA', t0 + 0.2, t0 + 0.34, 0.3, 0.05, 0.0, 'none'); tl.drop('lampB', t0 + 0.2, t0 + 0.34, 0.3, 0.05, 0.0, 'none')
        tl.drop('stoolA', t0 + 0.3, t0 + 0.44, 0.3, 0.05, 0.0, 'none'); tl.drop('shB', t0 + 0.3, t0 + 0.44, 0.3, 0.05, 0.0, 'none')
        return a, b

    def stairs_beat(self, t0, step=0.15, hold=0.60):
        """B's stair drawers open in a wave bottom to top, fill, and close top to bottom."""
        tl = self.tl
        for k in range(4):
            to = t0 + step * k
            tc = t0 + step * 3 + hold + step * (3 - k)
            f = self.drawer_fn(0.0, to, tc, (-0.28, 0, 0), base=tl.anims[f'stB{k}'])
            tl.custom(f'sdB{k}', f)
            tl.ev(to + 0.08, f'sdB{k}_open', 0.45 if k == 0 else 0.25, 'swish')
            tl.ev(tc + 0.17, f'sdB{k}_shut', 0.8, 'thud')
            tl.drop(f'sdBc{k}', to + 0.20, to + 0.36, 0.22, 0.05, 0.4, 'tick', parent=f)

    def den_beat(self, t0, t_close):
        tl = self.tl
        base = tl.anims['denDoor']

        def f(t):
            M, v = base(t)
            if not v or t < t0:
                return M, v
            if t < t_close:
                return T(-0.02 * min(1, (t - t0) / 0.05), 0.56 * eob(c01((t - t0) / 0.25), 0.6), 0) @ M, v
            u = c01((t - t_close) / 0.2)
            return T(-0.02 * (1 - u), 0.56 * (1 - smooth(u)), 0) @ M, v
        tl.custom('denDoor', f)
        tl.ev(t0 + 0.1, 'den_open', 0.5, 'swish'); tl.ev(t_close + 0.2, 'den_shut', 0.85, 'thud')
        self.appear('denLed', t0 + 0.12, t_close + 0.2)
        tl.ev(t0 + 0.12, 'den_led', 0.4, 'chime')
        tl.fly('denC', t0 + 0.26, t0 + 0.46, (-0.6, 0, 0.05), 0.05, 0.5, 'thud')

    def den_door(self, opens):
        tl = self.tl
        base = tl.anims['denDoor']

        def f(t):
            M, v = base(t)
            if not v:
                return M, v
            for (t0, t1) in opens:
                if t0 <= t < t1 + 0.25:
                    if t < t1:
                        return T(-0.02, 0.56 * eob(c01((t - t0) / 0.25), 0.6), 0) @ M, v
                    u = c01((t - t1) / 0.2)
                    return T(-0.02 * (1 - u), 0.56 * (1 - smooth(u)), 0) @ M, v
            return M, v
        tl.custom('denDoor', f)
        for (t0, t1) in opens:
            tl.ev(t0 + 0.1, 'den_open', 0.5, 'swish'); tl.ev(t1 + 0.2, 'den_shut', 0.85, 'thud')

    def kid_track(self, kid, segs):
        """segs = [(t0, t1, animate-kwargs)]: the kid shows each segment's animation inside [t0, t1), hidden otherwise."""
        tl, I = self.tl, self.I
        fns = []
        for (t0, t1, kw) in segs:
            kid.animate(tl, **kw)
            fns.append((t0, t1, {nm: tl.anims[nm] for nm in kid.pieces}))
        for nm in kid.pieces:
            def f(t, nm=nm):
                for (t0, t1, d) in fns:
                    if t0 <= t < t1:
                        return d[nm](t)
                return I, False
            tl.custom(nm, f)

    def play_beat(self, t0):
        """Play table + toys on the rugs; both kids kneel and play, then walk to their own sides; the table rolls into the den."""
        tl = self.tl
        c = np.array([CX, 1.42, 0.0])
        drop_t = tl.drop('table', t0, t0 + 0.18, 0.5, 0.04, 0.8, 'thud')
        lid_h = np.array([CX - 0.275, 0, 0.445])
        t_away = t0 + 3.70

        def roll(t):
            if t < t_away:
                return np.eye(4)
            return T(1.35 * smooth(c01((t - t_away) / 0.5)), 0.02, 0)

        def table(t):
            M, v = drop_t(t)
            return roll(t) @ M, v and t < t_away + 0.75
        tl.custom('table', table)

        def lid(t):
            M, v = drop_t(t)
            a = 0.0
            if t0 + 0.55 <= t < t0 + 1.35:
                a = -math.radians(70) * eob(c01((t - t0 - 0.55) / 0.25), 1.0)
            elif t0 + 1.35 <= t < t0 + 1.55:
                a = -math.radians(70) * (1 - smooth((t - t0 - 1.35) / 0.2))
            return roll(t) @ M @ about(lid_h, R('y', a)), v and t < t_away + 0.75
        tl.custom('tableLid', lid)
        tl.ev(t0 + 0.65, 'lid_open', 0.45, 'swish'); tl.ev(t0 + 1.55, 'lid_shut', 0.7, 'thud')
        cdrop = tl.drop('tableC', t0 + 0.8, t0 + 0.96, 0.3, 0.06, 0.45)
        tl.custom('tableC', lambda t: (roll(t) @ cdrop(t)[0], cdrop(t)[1] and t < t_away + 0.75))
        tl.ev(t_away + 0.5, 'table_home', 0.5, 'thud')
        self.den_door([(13.05, 14.40), (t_away - 0.15, t_away + 0.55)])
        crouch = fg.pose_of('crouch')

        def play_pose(sg):
            def f(t):
                p = dict(crouch)
                p['sh_r'] = 40 + 25 * math.sin(2 * math.pi * 1.4 * (t - t0) + sg)
                p['sh_l'] = 40 + 25 * math.sin(2 * math.pi * 1.4 * (t - t0) + sg + 2.0)
                return p
            return f
        tp, tw0, tw1 = t0 + 1.65, t0 + 2.75, t0 + 3.60
        pa, aa = fg.walk([(tw0, (1.38, 1.42, 90)), (tw1, (1.10, 0.78, 180))], KID_A)
        pb, ab = fg.walk([(tw0, (2.22, 1.42, -90)), (tw1, (2.20, 0.72, 180))], KID_B)
        return dict(A=[(tp, tw0, dict(pose=play_pose(0.0), at=(1.38, 1.42, 90), seat=None, pop=tp)),
                       (tw0, 30.65, dict(pose=pa, at=aa, seat=None))],
                    B=[(tp, tw0, dict(pose=play_pose(1.5), at=(2.22, 1.42, -90), seat=None, pop=tp + 0.1)),
                       (tw0, 30.65, dict(pose=pb, at=ab, seat=None))])

    def hatch_beat(self, t0):
        """Both hatch doors open; A passes a book through to B; the doors close."""
        tl = self.tl
        hx0 = 2.62
        tl.custom('wrHatchA', self.hinge_fn((hx0, WRY0, 0), math.radians(-100), t0, t0 + 1.30))
        tl.custom('wrHatchB', self.hinge_fn((hx0, WRY1, 0), math.radians(100), t0 + 0.05, t0 + 1.25))
        tl.ev(t0 + 0.1, 'hatch_open', 0.5, 'swish'); tl.ev(t0 + 1.5, 'hatch_shut', 0.7, 'thud')

        def book(t):
            if t < t0 + 0.2 or t > t0 + 1.25:
                return np.eye(4), False
            u = smooth(c01((t - t0 - 0.25) / 0.6))
            return T(-0.33 + 0.70 * u, 0, 0), True
        tl.custom('hatchBook', book)
        tl.ev(t0 + 0.85, 'book_pass', 0.45, 'tick')
        reach = dict(sh_r=82, sh_r_out=4, elbow_r=12, sh_l_out=6, elbow_l=10, spine=6)
        return dict(A=[(t0 - 0.3, t0 + 1.9, dict(pose=reach, at=(1.30, 2.14, 90), seat=None, pop=t0 - 0.3))],
                    B=[(t0 - 0.3, t0 + 1.9, dict(pose=fg.mirror(reach), at=(2.30, 2.14, -90), seat=None, pop=t0 - 0.25))])

    def drawerA_beat(self, t0):
        tl = self.tl
        f = self.drawer_fn(0.0, t0, t0 + 0.55, (0, -0.26, 0))
        tl.custom('wrDrA1', f)
        tl.ev(t0 + 0.08, 'wrDrA1_open', 0.45, 'swish'); tl.ev(t0 + 0.72, 'wrDrA1_shut', 0.8, 'thud')
        tl.drop('wrDrAc', t0 + 0.16, t0 + 0.32, 0.22, 0.05, 0.4, 'tick', parent=f)

    def doorsA_beat(self, t0, t_close):
        """Face A's doors swing open on the loaded shelves (plus the drawer), then close: it is full before it moves."""
        tl, t = self.tl, 0.018
        xv, y0 = 2.565, WRY0
        tl.custom('wrDoorA1', self.hinge_fn((WRX0 + t, y0, 0), math.radians(-105), t0, t_close))
        tl.custom('wrDoorA2', self.hinge_fn((xv + t, y0, 0), math.radians(105), t0 + 0.04, t_close + 0.04))
        tl.ev(t0 + 0.1, 'doorsA_open', 0.5, 'swish'); tl.ev(t_close + 0.24, 'doorsA_shut', 0.9, 'thud')
        tl.drop('wrFold', t0 + 0.16, t0 + 0.34, 0.25, 0.04, 0.45)
        f = self.drawer_fn(0.0, t0 + 0.08, t_close - 0.05, (0, -0.26, 0))
        tl.custom('wrDrA1', f)
        tl.drop('wrDrAc', t0 + 0.30, t0 + 0.46, 0.22, 0.05, 0.4, 'tick', parent=f)

    def bins_beat(self, t0, gap=0.055):
        tl = self.tl
        for k in range(12):
            tt = t0 + gap * k
            tl.fly(f'wrBin{k}', tt - 0.16, tt, (0, 0.5, 0.03), 0.03, 0.35 if k % 2 == 0 else 0.0, 'tick' if k % 2 == 0 else 'none')
        tl.fly('wrBooksB', t0 + gap * 12, t0 + gap * 12 + 0.16, (0, 0.4, 0.03), 0.03, 0.35, 'tick')

    def night_beat(self, tn, long=False):
        if long:                                  # long cut: daylight stays at about 85 % while the lamps come on
            self.appear('bd_night', 99.0)
        else:
            self.appear('bd_day', -1.0, tn); self.appear('bd_night', tn)
            self.tl.ev(tn, 'night', 0.5, 'swish')
        cas = (('rlOnA', 0.35, 0.7), ('ledLoft', 0.60, 0.5), ('lampOnA', 0.80, 0.45), ('rlOnB', 1.25, 0.7), ('lampOnB', 1.25, 0.0),
               ('denLed', 0.95, 0.0), ('dlOn', 1.45, 0.5))
        for nm, dt, s in cas:
            if nm == 'denLed':
                continue
            self.appear(nm, tn + dt)
            if s:
                self.tl.ev(tn + dt, nm, s, 'chime')

    # ---------------------------------------------------------------- cuts
    def short(self):
        tl = self.tl
        self.build_beat(0.0)
        self.desks_quick(4.0)
        self.stairs_beat(4.00, step=0.25, hold=0.45)
        self.den_beat(6.00, 6.78)
        self.doorsA_beat(7.10, 7.72)
        self.swing(8.08, 9.43, 0.0, -90.0)
        self.panel(9.72, 12.62)
        self.bins_beat(10.62, gap=0.05)
        self.night_beat(11.55, long=True)
        KID_A.animate(tl, pop=11.75)
        KID_B.animate(tl, pop=12.50)
        self.swing(12.95, 13.95, -90.0, 0.0)
        tl.drop('plushB', 14.30, 14.48, 0.5, 0.12, 0.4)
        self.hide(*LONG_ONLY)
        self.finish_wardrobe()
        return tl

    def long(self):
        tl = self.tl
        self.build_beat(0.0)
        a, b = self.desks_quick(5.30)
        for s_, base, sg in (('A', a, 1), ('B', b, -1)):
            f = self.drawer_fn(0.0, 6.30, 7.00, (sg * 0.28, 0, 0), base=base)
            tl.custom(f'ddr{s_}', f)
            tl.drop(f'ddc{s_}', 6.48, 6.64, 0.22, 0.05, 0.4 if s_ == 'A' else 0.0, 'tick' if s_ == 'A' else 'none', parent=f)
        tl.ev(6.38, 'ddr_open', 0.5, 'swish'); tl.ev(7.17, 'ddr_shut', 0.85, 'thud')
        tl.ev(5.46, 'desks', 0.7, 'thud')
        self.stairs_beat(9.05, step=0.25, hold=0.60)
        tl.fly('denC', 13.31, 13.51, (-0.6, 0, 0.05), 0.05, 0.5, 'thud')
        self.appear('denLed', 13.17, 14.6)
        tl.ev(13.17, 'den_led', 0.4, 'chime')
        self.doorsA_beat(16.05, 17.55)
        for k, nm in enumerate(('wrHatchA',)):
            pass
        kids = self.play_beat(20.05)
        self.swing(25.55, 26.60, 0.0, -90.0)
        self.panel(27.15, 40.45)
        self.bins_beat(28.85)
        hk = self.hatch_beat(30.95)
        tl.drop('beanbag', 33.30, 33.50, 0.5, 0.08, 0.6, 'thud')
        bb = tl.anims['beanbag']
        tl.custom('beanbag', lambda t: (bb(t)[0] @ about((2.55, 2.55, 0), S(*([max(0.02, 1 - smooth((t - 40.0) / 0.2))] * 3))) if t > 40.0
                                        else bb(t)[0], bb(t)[1] and t < 40.2))
        tl.drop('floorLamp', 33.62, 33.80, 0.4, 0.04, 0.5)
        tl.drop('plushB', 34.10, 34.28, 0.5, 0.12, 0.4)
        self.night_beat(35.45, long=True)
        sitA = dict(pose=LONG_SIT, at=(0.33, 2.55, 90), seat=LZ1 + 0.15)
        sitB = dict(pose=LONG_SIT, at=(3.02, 1.72, 180), seat=BZ1 + 0.15)
        self.kid_track(KID_A, kids['A'] + hk['A'] + [(35.75, 99, dict(sitA, pop=35.75))])
        self.kid_track(KID_B, kids['B'] + hk['B'] + [(37.65, 99, dict(sitB, pop=37.65))])
        self.swing(40.85, 41.90, -90.0, 0.0)
        self.hide('stool1', 'stool2')
        self.finish_wardrobe()
        return tl


LA = (P(1.64, 1.66, 1.24, -70.0, -13.0), P(1.38, 2.32, 1.08, -108.0, -8.0))            # long: A's under-loft desk
LDN = (P(1.32, 0.72, 1.06, 76.0, -9.0), P(1.60, 1.42, 0.88, 110.0, -4.0))             # long: B's den
LC = (P(0.78, 0.42, 1.64, 34.0, -10.0), P(1.52, 0.20, 1.44, 2.0, -13.0))            # long: wardrobe face A
LD = (P(CX - 0.28, -0.08, 1.86, -8.0, -29.0), P(CX + 0.26, 0.32, 1.64, 8.0, -33.0))               # long: shared play table
LF = (P(2.95, 2.80, 1.35, -116.0, -8.0), P(2.85, 2.62, 1.30, -124.0, -7.0))            # long: the hatch handover
LF2 = (P(1.85, 0.95, 1.62, 32.0, -18.0), P(2.00, 1.10, 1.58, 40.0, -20.0))           # long: B's freed corner
S5L = (P(CX, 0.14, 2.20, 12.0, -24.0, 98.0), P(1.98, 0.34, 2.02, 32.0, -21.0, 98.0))   # long: bedtime, B's side
LH = (P(1.98, 0.34, 2.02, 18.0, -22.0, 98.0), F1)
S2L = (P(0.98, 0.04, 1.04, 50.0, -10.0), P(1.55, 0.86, 0.84, 84.0, -5.0))               # long: stair drawers                                      # long: swing back -> frame 1
if CUT == 'long' and not REST:
    HOLDS = [(0.0, 2.45, S1), (2.70, 4.90, S1B), (5.15, 8.60, LA), (8.90, 12.60, S2L), (12.90, 15.60, LDN), (15.90, 19.60, LC),
             (19.90, 24.50, LD), (24.80, 26.80, S3), (26.84, 28.40, S3W), (28.70, 30.30, S3B), (30.60, 32.90, LF),
             (33.20, 35.00, LF2), (35.30, 37.30, S4), (37.50, 39.90, S5L), (40.20, DUR, LH)]
camera = make_camera(HOLDS)

if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    timeline().export(DUR, camera, lights, out)
