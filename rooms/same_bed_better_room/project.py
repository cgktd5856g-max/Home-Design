"""Same Bed, Better Room (idea C4): a 3.0 x 3.1 m bedroom for a couple, seen from above. The usual layout lands
(bed dead centre, wardrobe at its foot bonking it, desk wedged at its corner), then the same pieces slide like a
tile puzzle into a better plan, and the bed rises on one 1 m storage platform with stair drawers, a deep drawer,
a headboard ledge and a 1.4 m pull-out shirt rail. White shell + light oak + ochre duvet, blue only on a pillow
and a throw. No on-screen text.

    ROOM_REST=1 python3 ../../pipeline/run.py project.py <workdir> probe 0.5,1.5,2.5,3.5,4.5,5.5   # finished room
    python3 ../../pipeline/run.py project.py <workdir> preview                                       # preview + music
    ROOM_CUT=long ...                                                                                 # the 45 s cut

Units: metres. x = east, y = north, z = up. Room x 0..W, y 0..D, z 0..H.
South wall: door (x 0.15..0.95). North wall: window (x 0.15..1.35). After: platform bed on the east side,
wardrobe on the west wall, desk under the window.
"""
import json
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
import figure as fg

FIG = [None]

REST = os.environ.get('ROOM_REST') == '1'
CUT = os.environ.get('ROOM_CUT', '15')
LONG = CUT == 'long'

W, D, H = 3.0, 3.1, 2.7
FPS = 25
DUR = 8.0 if REST else (45.0 if LONG else 15.0)
WX0, WX1, WZ0, WZ1 = 0.15, 1.35, 0.85, 2.25        # north window
DX0, DX1, DZ = 0.15, 0.95, 2.1                      # south door opening
BASE_Z = 0.9                                        # the cut-down south wall
CEIL_Z = 2.7
BED_OFF = np.array([-0.75, 0.0, -0.70])             # bed: before (centred, on its legs) relative to its final place
CW, CD = np.array([0.275, 1.5]), np.array([0.75, 2.85])   # wardrobe / desk centres in their final places
CAPTIONS = []                                       # no on-screen text


# ------------------------------------------------------------------------------------------- materials
def materials():
    mat('ground', tex=3, col=srgb(236, 235, 233), rough=0.8, p=(0.05,))
    mat('floor', tex=1, col=srgb(212, 194, 168), col2=srgb(196, 178, 150), rough=0.38, f0=0.04, glossy=True, p=(0.16, 1.4))
    mat('wall', tex=3, col=srgb(243, 243, 241), p=(0.015,))
    mat('ceiling', col=srgb(246, 246, 245))
    mat('white_cab', col=srgb(242, 242, 239), rough=0.45)
    mat('white_in', col=srgb(232, 232, 229))
    mat('plinth', col=srgb(214, 212, 208))
    wood_mats('oak', srgb(216, 196, 164), seed=3.0)
    mat('metal', col=srgb(200, 200, 204), rough=0.3, metal=1)
    mat('winframe', col=srgb(236, 236, 236), rough=0.4)
    mat('sill', col=srgb(240, 240, 238), rough=0.25, f0=0.04, glossy=True)
    mat('duvet', tex=3, col=srgb(234, 234, 232), rough=0.9, p=(0.05,))
    mat('sheet', tex=3, col=srgb(244, 244, 242), rough=0.9, p=(0.03,))
    mat('mattress', tex=5, col=srgb(246, 246, 244), p=(0, 0.02))
    mat('pil_white', tex=3, col=srgb(244, 244, 242), rough=0.9, p=(0.04,))
    mat('pil_blue', tex=6, col=srgb(132, 152, 176))
    mat('throw', tex=5, col=srgb(124, 146, 172), p=(0, 0.012))
    mat('backdrop', tex=9, emis=(1.35, 1.35, 1.35), p=(1.0, 0.0))
    mat('ceramic', col=srgb(242, 242, 238), rough=0.22, f0=0.04, glossy=True)
    mat('terra', col=srgb(196, 124, 90))
    mat('leaf', col=srgb(64, 112, 60)); mat('leaf2', col=srgb(96, 142, 74))
    mat('seat', tex=6, col=srgb(236, 234, 228))
    mat('bulb', col=(0, 0, 0), emis=(9.0, 7.8, 6.0))
    mat('led', col=(0, 0, 0), emis=(14.0, 12.0, 8.5))
    mat('led_off', col=srgb(232, 232, 228))
    mat('shade', col=srgb(244, 240, 232), rough=0.9)
    mat('shade_on', col=srgb(244, 240, 232), emis=(4.5, 3.6, 2.4))
    mat('box_linen', tex=3, col=srgb(214, 208, 196), p=(0.06,))
    mat('box_white', col=srgb(240, 240, 238), rough=0.5)
    mat('suitcase', col=srgb(124, 150, 176), rough=0.3, f0=0.05, glossy=True)
    for nm, c in (('cl_rust', (174, 110, 86)), ('cl_mustard', (206, 178, 112)), ('cl_terra', (198, 126, 92)), ('cl_white', (242, 242, 240)),
                  ('cl_sage', (146, 166, 138)), ('cl_navy', (54, 66, 100)), ('cl_denim', (90, 114, 152)), ('cl_grey', (192, 192, 196))):
        mat(nm, tex=5, col=srgb(*c), p=(2, 0.008))
    for nm, c in (('bk_sage', (150, 168, 144)), ('bk_white', (240, 238, 232)), ('bk_terra', (194, 116, 84)), ('bk_navy', (56, 68, 102)),
                  ('bk_mustard', (214, 168, 70)), ('bk_blue', (110, 138, 172)), ('bk_grey', (176, 176, 180))):
        mat(nm, col=srgb(*c), rough=0.6)
    mat('shoe_white', col=srgb(244, 244, 240), rough=0.5); mat('shoe_tan', col=srgb(184, 140, 98), rough=0.4, f0=0.04, glossy=True)
    mat('sole', col=srgb(236, 232, 224), rough=0.7)


# ------------------------------------------------------------------------------------------- helpers
def disc(inst, c, r, z0, z1, m, n=28):
    add(inst, lathe(rprof(r, z0, z1, min(0.004, (z1 - z0) * 0.45), 3), n, c), m)


def garment(inst, x, y, z_top, length, width, m, along='y', thick=0.05, yaw=0.0):
    """Hanging garment on a rail running along `along` (width is across the rail); a hanger hook on top."""
    if along == 'y':                                 # a shirt: body, rounded shoulders, two sleeves hanging at its sides
        add(inst, tube([(x - width * 0.42, y, z_top - 0.07), (x, y, z_top - 0.02), (x + width * 0.42, y, z_top - 0.07)], 0.004, 6), 'metal')
        add(inst, tube([(x, y, z_top - 0.02), (x, y, z_top + 0.03)], 0.003, 6), 'metal')
        bw = width * 0.74
        if yaw:                                      # turned on its hook: build it into a temp piece, then rotate
            tmp = inst + '__tmp'
            garment(tmp, x, y, z_top, length, width, m, along, thick)
            for P_, N_, mi in rk.INST.pop(tmp):
                rk.ORDER.remove(tmp) if tmp in rk.ORDER else None
                M = about((x, y, 0), R('z', yaw))
                Pw = (P_.reshape(-1, 3) @ M[:3, :3].T + M[:3, 3]).reshape(P_.shape)
                Nw = (N_.reshape(-1, 3) @ M[:3, :3].T).reshape(N_.shape)
                if inst not in rk.INST:
                    rk.INST[inst] = []; rk.ORDER.append(inst)
                rk.INST[inst].append((Pw.astype(np.float32), Nw.astype(np.float32), mi))
            return
        add(inst, rbox((x, y, z_top - 0.07 - length / 2), (bw, thick, length), 0.018, 3), m)
        add(inst, xform(ellipsoid((0, 0, 0), (width * 0.47, thick * 0.55, 0.045), 12), T(x, y, z_top - 0.085)), m)
        for sg in (-1, 1):
            c = np.array([x + sg * (bw / 2 + 0.03), y, z_top - 0.09 - length * 0.36])
            add(inst, xform(rbox(c, (0.075, thick * 0.8, length * 0.72), 0.02, 3), about(c, R('y', -sg * 0.10))), m)
    else:
        add(inst, tube([(x, y - width * 0.45, z_top - 0.05), (x, y, z_top), (x, y + width * 0.45, z_top - 0.05)], 0.004, 6), 'metal')
        add(inst, rbox((x, y, z_top - 0.06 - length / 2), (thick, width, length), 0.018, 3), m)


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
    """Puffy pillow. size = (width x, thickness y, height z)."""
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


def shoe(inst, x, y, z, m, ang=0.0):
    """Plain low shoe (no stripes or logos), long axis along x before rotation `ang` about z."""
    M = about((x, y, z), R('z', ang))
    add(inst, xform(rbox((x, y, z + 0.012), (0.26, 0.095, 0.024), 0.01, 3), M), 'sole')
    add(inst, xform(ellipsoid((x + 0.01, y, z + 0.045), (0.12, 0.045, 0.035), 10), M), m)


def books_row(inst, x0, y, z0, n, rng, along='x', depth=0.15):
    """Upright books with blank solid-colour spines."""
    ms = ['bk_sage', 'bk_white', 'bk_terra', 'bk_navy', 'bk_mustard', 'bk_blue', 'bk_grey', 'bk_white']
    p = x0
    for k in range(n):
        th, h = rng.uniform(0.022, 0.04), rng.uniform(0.17, 0.23)
        if along == 'x':
            add(inst, box(p, y - depth / 2, z0, p + th, y + depth / 2, z0 + h), ms[k % len(ms)])
        else:
            add(inst, box(y - depth / 2, p, z0, y + depth / 2, p + th, z0 + h), ms[k % len(ms)])
        p += th + 0.003
    return p


# ------------------------------------------------------------------------------------------- shell
def build_shell():
    r = 'room'
    add(r, box(-40, -40, -0.35, 40, 40, -0.03), 'ground')
    add(r, box(-0.12, -0.12, -0.03, W + 0.12, D + 0.12, -0.02), 'plinth')
    add(r, box(0, 0, -0.02, W, D, 0.0), 'floor')
    add(r, box(-0.12, -0.12, -0.03, 0, D + 0.12, H), 'wall')                     # west
    add(r, box(W, -0.12, -0.03, W + 0.12, D + 0.12, H), 'wall')                  # east
    for b in (box(0, D, -0.03, WX0, D + 0.12, H), box(WX1, D, -0.03, W, D + 0.12, H),
              box(WX0, D, -0.03, WX1, D + 0.12, WZ0), box(WX0, D, WZ1, WX1, D + 0.12, H)):
        add(r, b, 'wall')                                                        # north, window hole
    for b in (box(0, -0.12, -0.03, DX0, 0, BASE_Z), box(DX1, -0.12, -0.03, W, 0, BASE_Z)):
        add(r, b, 'wall')                                                        # south base (always there)
    # window: reveal, sill, slim white frame with one mullion
    for b in (box(WX0, D, WZ0, WX0 + 0.006, D + 0.12, WZ1), box(WX1 - 0.006, D, WZ0, WX1, D + 0.12, WZ1),
              box(WX0, D, WZ1 - 0.006, WX1, D + 0.12, WZ1)):
        add(r, b, 'sill')
    add(r, box(WX0 - 0.03, D - 0.035, WZ0 - 0.02, WX1 + 0.03, D + 0.06, WZ0), 'sill')
    fy0, fy1 = D + 0.07, D + 0.10
    xm = (WX0 + WX1) / 2
    for b in (box(WX0, fy0, WZ0, WX0 + 0.04, fy1, WZ1), box(WX1 - 0.04, fy0, WZ0, WX1, fy1, WZ1), box(WX0, fy0, WZ1 - 0.04, WX1, fy1, WZ1),
              box(WX0, fy0, WZ0, WX1, fy1, WZ0 + 0.04), box(xm - 0.018, fy0, WZ0, xm + 0.018, fy1, WZ1)):
        add(r, b, 'winframe')
    # baseboards
    for b in (box(0, 0, 0, 0.012, D, 0.07), box(0, D - 0.012, 0, W, D, 0.07), box(W - 0.012, 0, 0, W, D, 0.07),
              box(0, 0, 0, DX0, 0.012, 0.07), box(DX1, 0, 0, W, 0.012, 0.07)):
        add(r, b, 'white_cab')
    # upper south wall (only while the camera is inside the room below the wall tops) + door casing
    u = 'south_up'
    for b in (box(-0.12, -0.12, BASE_Z, DX0, 0, H), box(DX1, -0.12, BASE_Z, W + 0.12, 0, H), box(DX0, -0.12, DZ, DX1, 0, H)):
        add(u, b, 'wall')
    for b in (box(DX0 - 0.05, 0, BASE_Z, DX0, 0.012, DZ + 0.05), box(DX1, 0, BASE_Z, DX1 + 0.05, 0.012, DZ + 0.05),
              box(DX0 - 0.05, 0, DZ, DX1 + 0.05, 0.012, DZ + 0.05)):
        add(u, b, 'white_cab')
    for b in (box(DX0 - 0.05, 0, 0, DX0, 0.012, BASE_Z), box(DX1, 0, 0, DX1 + 0.05, 0.012, BASE_Z)):
        add(r, b, 'white_cab')
    add('door', box(DX0 + 0.004, -0.045, 0.005, DX1 - 0.004, -0.008, DZ - 0.005), 'white_cab')        # door leaf (west hinge)
    add('door', tube([(DX1 - 0.09, -0.008, 1.02), (DX1 - 0.09, 0.04, 1.02), (DX1 - 0.20, 0.04, 1.02)], 0.009, 10), 'metal')
    add('ceiling', box(-0.12, -0.12, CEIL_Z, W + 0.12, D + 0.12, CEIL_Z + 0.1), 'ceiling')
    add('backdrop', box(-6, D + 4.5, -3, 8, D + 4.55, 9), 'backdrop')
    add('fadekey', box(-0.01, -0.01, -5.01, 0.01, 0.01, -4.99), 'ground')        # hidden carrier of the light fade value


# ------------------------------------------------------------------------------------------- bed (built raised, final)
BX0, BX1, BY0, BY1 = 1.505, 2.995, 1.005, 3.095


def build_bed(rng):
    t = 0.03
    wood('bed_frame', BX0, BY0, 0.85, BX0 + t, BY1, 0.99, 'oak')
    wood('bed_frame', BX1 - t, BY0, 0.85, BX1, BY1, 0.99, 'oak')
    wood('bed_frame', BX0 + t, BY0, 0.85, BX1 - t, BY0 + t, 0.99, 'oak')
    wood('bed_frame', BX0, BY1 - 0.05, 0.85, BX1, BY1, 1.80, 'oak')                # headboard
    add('bed_frame', box(BX0 + t, BY0 + t, 0.96, BX1 - t, BY1 - 0.05, 0.985), 'white_in')
    for (x, y) in ((BX0 + 0.06, BY0 + 0.06), (BX1 - 0.06, BY0 + 0.06), (BX0 + 0.06, BY1 - 0.08), (BX1 - 0.06, BY1 - 0.08)):
        add('bed_legs', box(x - 0.03, y - 0.03, 0.70, x + 0.03, y + 0.03, 0.85), 'oak_z')
    add('mattress', rbox((2.25, 2.04, 1.10), (1.40, 2.0, 0.20), 0.04, 5), 'mattress')
    cloth('duvet', 1.53, 2.97, 1.03, 2.62, 1.235, 1.06, 0.045, 'duvet', 3)
    add('duvet', rbox((2.25, 2.60, 1.245), (1.47, 0.15, 0.03), 0.013, 3), 'sheet')
    cloth('throw', 1.50, 3.00, 1.13, 1.52, 1.258, 1.10, 0.04, 'throw', 7, sides=('w', 'e'), puff=0.006)
    pillow('pil_w', (1.92, 2.86, 1.34), (0.62, 0.15, 0.40), -0.36, 'pil_white')
    pillow('pil_b', (2.58, 2.86, 1.34), (0.62, 0.15, 0.40), -0.36, 'pil_blue')


# ------------------------------------------------------------------------------------------- platform, stairs, drawers, rail
def build_platform(rng):
    p = 'plat'
    wood(p, 1.47, 1.0, 0.975, W, D, 1.0, 'oak')                                   # deck with a 3 cm lip on the aisle side
    for b in (box(1.5, 1.0, 0, 1.52, 1.05, 0.975), box(1.5, 2.45, 0, 1.52, D, 0.975), box(1.5, 1.05, 0, 1.52, 2.45, 0.05),
              box(1.5, 1.05, 0.95, 1.52, 2.45, 0.975)):
        add(p, b, 'oak_z')                                                         # west face around the rail opening
    for b in (box(1.5, 1.0, 0, 2.32, 1.02, 0.975), box(2.98, 1.0, 0, W, 1.02, 0.975), box(2.32, 1.0, 0, 2.98, 1.02, 0.05),
              box(2.32, 1.0, 0.90, 2.98, 1.02, 0.975)):
        add(p, b, 'oak_z')                                                         # south face around the deep drawer
    for b in (box(2.12, 1.03, 0.0, 2.14, 2.47, 0.975), box(1.52, 1.03, 0.0, 2.14, 1.05, 0.975), box(1.52, 2.45, 0.0, 2.14, 2.47, 0.975),
              box(1.52, 1.05, 0.0, 2.12, 2.45, 0.03), box(2.30, 1.84, 0, 3.0, 1.86, 0.975), box(2.30, 1.02, 0, 2.32, 1.86, 0.975),
              box(2.32, 1.02, 0, 2.98, 1.84, 0.03)):
        add(p, b, 'white_in')                                                      # the two cavities
    add(p, box(1.476, 1.02, 0.966, 1.49, 3.08, 0.973), 'led_off')                  # LED strip under the lip (off)
    add('led_lip', box(1.4755, 1.02, 0.9655, 1.4905, 3.08, 0.9725), 'led')
    # the stairs: three blocks with side-pull drawers (pull out west)
    for k in range(3):
        y0, y1, top = 0.25 + 0.25 * k, 0.5 + 0.25 * k, 0.25 * (k + 1)
        s = f'step{k}'
        wood(s, 1.5, y0 - 0.02, top - 0.025, 2.25, y1, top, 'oak')                 # tread with a small nose
        for b in (box(2.23, y0, 0, 2.25, y1, top - 0.025), box(1.5, y0, 0, 2.25, y0 + 0.02, top - 0.025),
                  box(1.5, y1 - 0.02, 0, 2.25, y1, top - 0.025)):
            add(s, b, 'oak_x')
        add(s, box(1.5, y0 + 0.02, 0, 1.52, y1 - 0.02, 0.03), 'oak_x')
        add(s, box(1.5, y0 + 0.02, top - 0.045, 1.52, y1 - 0.02, top - 0.025), 'oak_x')
        add(s, box(1.52, y0 + 0.02, 0, 2.23, y1 - 0.02, 0.012), 'white_in')
        add(s, box(1.505, y0 - 0.019, top - 0.034, 2.245, y0 - 0.014, top - 0.029), 'led_off')
        add(f'led_step{k}', box(1.506, y0 - 0.0195, top - 0.0345, 2.244, y0 - 0.0135, top - 0.0285), 'led')
        d = f'sdr{k}'
        z0, z1 = 0.035, top - 0.05
        add(d, box(1.5, y0 + 0.022, z0, 1.52, y1 - 0.022, z1), 'oak_x')
        add(d, box(1.505, (y0 + y1) / 2 - 0.05, z1 - 0.035, 1.5, (y0 + y1) / 2 + 0.05, z1 - 0.02), 'oak_x')
        for b in (box(1.52, y0 + 0.03, z0, 2.08, y1 - 0.03, z0 + 0.012), box(1.52, y0 + 0.03, z0, 2.08, y0 + 0.042, z1 - 0.02),
                  box(1.52, y1 - 0.042, z0, 2.08, y1 - 0.03, z1 - 0.02), box(2.068, y0 + 0.03, z0, 2.08, y1 - 0.03, z1 - 0.02)):
            add(d, b, 'white_in')
        c = f'sdr{k}_c'
        yc = (y0 + y1) / 2
        if k == 0:
            shoe(c, 1.68, yc - 0.0, z0 + 0.012, 'shoe_white'); shoe(c, 1.93, yc, z0 + 0.012, 'shoe_tan')
        else:
            nn = 6 if k == 1 else 9
            stack(c, 1.66, yc, z0 + 0.012, (0.24, 0.16, 0.06), [('cl_rust', 'cl_mustard', 'cl_white', 'cl_terra', 'cl_rust'),
                                                               ('cl_mustard', 'cl_terra', 'cl_white', 'cl_rust', 'cl_mustard')][k - 1], nn, rng)
            stack(c, 1.93, yc, z0 + 0.012, (0.24, 0.16, 0.06), [('cl_sage', 'cl_navy', 'cl_grey', 'cl_denim', 'cl_sage'),
                                                               ('cl_navy', 'cl_denim', 'cl_sage', 'cl_grey', 'cl_navy')][k - 1], nn, rng)
    # deep drawer in the platform's south face (pulls south 0.8 m)
    d = 'ddr'
    add(d, box(2.32, 0.995, 0.055, 2.98, 1.015, 0.895), 'oak_z')
    add(d, box(2.60, 0.99, 0.80, 2.70, 0.995, 0.815), 'oak_x')
    for b in (box(2.34, 1.015, 0.055, 2.96, 1.82, 0.067), box(2.34, 1.015, 0.055, 2.352, 1.82, 0.60), box(2.948, 1.015, 0.055, 2.96, 1.82, 0.60),
              box(2.34, 1.808, 0.055, 2.96, 1.82, 0.60)):
        add(d, b, 'white_in')
    add('ddr_c', rbox((2.65, 1.30, 0.21), (0.52, 0.38, 0.26), 0.04, 3), 'suitcase')
    add('ddr_c', tube([(2.55, 1.10, 0.33), (2.55, 1.09, 0.345), (2.75, 1.09, 0.345), (2.75, 1.10, 0.33)], 0.008, 6), 'metal')
    add('ddr_c', rbox((2.65, 1.66, 0.17), (0.52, 0.26, 0.20), 0.07, 5), 'sheet')
    # the pull-out rail: front panel (part of the west face), base, end posts, tube rail at 0.88 m, 12 shirts
    rl = 'rail'
    add(rl, box(1.5, 1.052, 0.052, 1.52, 2.448, 0.948), 'oak_z')
    add(rl, box(1.494, 1.10, 0.45, 1.5, 1.14, 0.60), 'metal')                      # end handle (south end)
    add(rl, box(1.52, 1.06, 0.052, 2.10, 2.44, 0.066), 'white_in')
    for y in (1.065, 2.435):
        add(rl, box(1.79, y - 0.012, 0.066, 1.83, y + 0.012, 0.90), 'oak_z')
    add(rl, tube([(1.81, 1.07, 0.88), (1.81, 2.43, 0.88)], 0.011, 10), 'metal')
    cols = ['cl_sage', 'cl_denim', 'cl_terra', 'cl_grey', 'cl_navy', 'cl_white', 'cl_rust', 'cl_sage', 'cl_denim', 'cl_white', 'cl_terra', 'cl_navy']
    for k, m in enumerate(cols):
        garment('rail_cl', 1.81, 1.14 + k * 0.111, 0.872, rng.uniform(0.62, 0.70), 0.40, m, along='y', thick=0.035)
    # headboard ledge over the bed head (part of the platform) + its things
    wood('ledge', 1.5, 2.86, 1.81, W, D, 1.85, 'oak')
    add('ledge', box(1.5, D - 0.02, 1.80, W, D, 1.81), 'oak_x')
    books_row('ledge_bk', 1.62, 2.98, 1.85, 7, rng)
    add('ledge_bk', box(1.92, 2.92, 1.85, 2.10, 3.06, 1.88), 'bk_terra'); add('ledge_bk', box(1.93, 2.93, 1.88, 2.09, 3.05, 1.905), 'bk_white')
    plant('ledge_pl', 2.82, 2.98, 1.85, 0.055, 0.09, rng, 9)
    lx, ly = 2.45, 2.98
    add('hb_lamp', lathe(rprof(0.05, 1.85, 1.862, 0.004, 3), 24, (lx, ly)), 'ceramic')
    add('hb_lamp', tube([(lx, ly, 1.86), (lx, ly, 2.02)], 0.008, 8), 'ceramic')
    add('hb_lamp', lathe([(0.055, 1.98), (0.085, 1.98), (0.065, 2.10), (0.04, 2.10)], 24, (lx, ly)), 'shade')
    add('hb_on', lathe([(0.056, 1.979), (0.0862, 1.979), (0.0662, 2.101), (0.041, 2.101)], 24, (lx, ly)), 'shade_on')


# ------------------------------------------------------------------------------------------- wardrobe (final: west wall)
def build_wardrobe(rng):
    w = 'wr'
    t = 0.02
    add(w, box(0.02, 1.02, 0, 0.51, 1.98, 0.06), 'plinth')
    add(w, box(0, 1.0, 0.0, t, 2.0, 2.0), 'white_cab')
    wood(w, 0, 1.0, 0.0, 0.53, 1.0 + t, 2.0, 'oak'); wood(w, 0, 2.0 - t, 0.0, 0.53, 2.0, 2.0, 'oak')
    wood(w, 0, 1.0, 1.98, 0.55, 2.0, 2.0, 'oak')
    add(w, box(t, 1.0 + t, 0.06, 0.53, 2.0 - t, 0.08), 'white_in')
    add(w, box(t, 1.0 + t, 1.78, 0.52, 2.0 - t, 1.795), 'white_in')               # top shelf
    add(w, box(t, 1.0 + t, 0.48, 0.52, 2.0 - t, 0.495), 'white_in')               # shelf over the drawers
    add(w, tube([(0.27, 1.03, 1.70), (0.27, 1.97, 1.70)], 0.011, 10), 'metal')
    add('wr_led', box(0.40, 1.04, 1.772, 0.42, 1.96, 1.778), 'led')
    for k, z0 in enumerate((0.085, 0.285)):
        dn = f'wr_dr{k}'
        add(dn, box(0.50, 1.03, z0, 0.52, 1.97, z0 + 0.19), 'oak_z')
        add(dn, box(0.52, 1.45, z0 + 0.15, 0.526, 1.55, z0 + 0.162), 'metal')
        for b in (box(0.06, 1.05, z0 + 0.01, 0.50, 1.95, z0 + 0.022), box(0.06, 1.05, z0 + 0.01, 0.50, 1.062, z0 + 0.16),
                  box(0.06, 1.938, z0 + 0.01, 0.50, 1.95, z0 + 0.16), box(0.06, 1.05, z0 + 0.01, 0.072, 1.95, z0 + 0.16)):
            add(dn, b, 'white_in')
    for k, yy in enumerate((1.20, 1.42, 1.64, 1.84)):
        stack('wr_dr1_c', 0.29, yy, 0.285 + 0.022, (0.30, 0.18, 0.035), [('cl_white', 'cl_terra', 'cl_mustard'), ('cl_rust', 'cl_white', 'cl_terra'),
                                                                        ('cl_grey', 'cl_navy', 'cl_sage'), ('cl_denim', 'cl_grey', 'cl_white')][k], 3, rng)
    for k, m in enumerate(('cl_rust', 'cl_white', 'cl_terra', 'cl_grey', 'cl_white')):
        garment('wr_cl0', 0.27, 1.88 - k * 0.085, 1.69, rng.uniform(0.85, 1.05), 0.40, m, along='y', thick=0.035, yaw=0.6)
    for k, m in enumerate(('cl_sage', 'cl_navy', 'cl_grey', 'cl_denim', 'cl_navy')):
        garment('wr_cl1', 0.27, 1.12 + k * 0.085, 1.69, rng.uniform(0.85, 1.05), 0.40, m, along='y', thick=0.035, yaw=0.6)
    for k, (yy, mm) in enumerate(((1.15, 'shoe_white'), (1.42, 'shoe_tan'), (1.69, 'shoe_white'))):
        shoe('wr_box', 0.25, yy - 0.06, 0.495, mm, 0.0); shoe('wr_box', 0.25, yy + 0.06, 0.495, mm, 0.0)
    for k, y in enumerate((1.25, 1.75)):
        add('wr_box', rbox((0.27, y, 1.795 + 0.09), (0.36, 0.36, 0.18), 0.02, 3), 'box_linen')
    # oak doors: south door hinges at (0.55, 1.0), north door at (0.55, 2.0)
    for nm, (y0, y1), hy in (('wd_s', (1.002, 1.498), 1.47), ('wd_n', (1.502, 1.998), 1.53)):
        add(nm, box(0.53, y0, 0.065, 0.55, y1, 1.995), 'oak_z')
        add(nm, box(0.55, hy - 0.006, 0.85, 0.558, hy + 0.006, 1.25), 'metal')
    # top cupboard (grows from 2.0 to 2.7 m)
    tc = 'wr_top'
    for b in (box(0, 1.0, 2.0, 0.53, 2.0, 2.02), box(0, 1.0, 2.68, 0.53, 2.0, H), box(0, 1.0, 2.0, t, 2.0, H), box(0, 1.0, 2.0, 0.53, 1.0 + t, H),
              box(0, 2.0 - t, 2.0, 0.53, 2.0, H)):
        add(tc, b, 'white_cab')
    add(tc, box(0.53, 1.002, 2.002, 0.55, 1.498, 2.698), 'oak_z'); add(tc, box(0.53, 1.502, 2.002, 0.55, 1.998, 2.698), 'oak_z')
    for hy in (1.47, 1.53):
        add(tc, box(0.55, hy - 0.006, 2.04, 0.558, hy + 0.006, 2.16), 'metal')


# ------------------------------------------------------------------------------------------- desk (final: under the window)
def build_desk(rng):
    x0, x1, y0, y1, zt = 0.35, 1.15, 2.6, 3.1, 0.75
    wood('desk', x0, y0, zt - 0.03, x1, y1, zt, 'oak')
    for (x, y) in ((x0 + 0.03, y0 + 0.03), (x1 - 0.03, y0 + 0.03), (x0 + 0.03, y1 - 0.03), (x1 - 0.03, y1 - 0.03)):
        add('desk', box(x - 0.02, y - 0.02, 0, x + 0.02, y + 0.02, zt - 0.03), 'oak_z')
    add('desk', box(x0 + 0.02, y1 - 0.04, zt - 0.10, x1 - 0.02, y1 - 0.02, zt - 0.03), 'oak_x')
    for nm, (a0, a1) in (('desk_dr0', (x0 + 0.03, 0.53)), ('desk_dr1', (0.97, x1 - 0.03))):
        add('desk', box(a0, y0 + 0.02, zt - 0.11, a1, y1 - 0.04, zt - 0.10), 'white_in')
        add(nm, box(a0 + 0.004, y0 + 0.01, zt - 0.10, a1 - 0.004, y0 + 0.03, zt - 0.035), 'oak_x')
        add(nm, box((a0 + a1) / 2 - 0.03, y0 + 0.004, zt - 0.075, (a0 + a1) / 2 + 0.03, y0 + 0.01, zt - 0.065), 'metal')
        for b in (box(a0 + 0.01, y0 + 0.03, zt - 0.098, a1 - 0.01, y1 - 0.06, zt - 0.092),
                  box(a0 + 0.01, y1 - 0.07, zt - 0.098, a1 - 0.01, y1 - 0.06, zt - 0.045)):
            add(nm, b, 'white_in')
    add('desk_dr0_c', box(0.40, 2.70, zt - 0.092, 0.50, 2.86, zt - 0.080), 'bk_sage')
    add('desk_dr0_c', tube([(0.405, 2.90, zt - 0.086), (0.495, 2.90, zt - 0.086)], 0.004, 6), 'bk_navy')
    add('desk_dr1_c', box(1.00, 2.68, zt - 0.092, 1.11, 2.84, zt - 0.078), 'bk_mustard')
    add('desk_dr1_c', box(1.00, 2.87, zt - 0.092, 1.11, 3.00, zt - 0.082), 'bk_white')
    # low-back chair, tucked fully under the desk (seat 0.45, back top 0.68)
    cx, cy = 0.75, 2.84
    ch = 'chair'
    add(ch, rbox((cx, cy, 0.44), (0.42, 0.40, 0.05), 0.02, 3), 'seat')
    for (x, y) in ((cx - 0.18, cy - 0.17), (cx + 0.18, cy - 0.17), (cx - 0.18, cy + 0.17), (cx + 0.18, cy + 0.17)):
        add(ch, box(x - 0.016, y - 0.016, 0, x + 0.016, y + 0.016, 0.42), 'oak_z')
    for x in (cx - 0.18, cx + 0.18):
        add(ch, box(x - 0.015, cy - 0.20, 0.42, x + 0.015, cy - 0.17, 0.66), 'oak_z')
    add(ch, rbox((cx, cy - 0.19, 0.61), (0.42, 0.03, 0.12), 0.012, 3), 'oak_x')
    # desk things (land in the last station)
    lx, ly = 1.04, 2.98
    add('desk_lamp', lathe(rprof(0.055, zt, zt + 0.014, 0.005, 3), 24, (lx, ly)), 'ceramic')
    add('desk_lamp', tube([(lx, ly, zt + 0.01), (lx, ly, 1.12), (lx - 0.04, ly - 0.03, 1.16), (lx - 0.12, ly - 0.08, 1.17)], 0.006, 10), 'metal')
    add('desk_lamp', lathe([(0.01, 1.19), (0.03, 1.18), (0.052, 1.14), (0.062, 1.11)], 24, (lx - 0.12, ly - 0.08)), 'ceramic')
    add('desk_on', ellipsoid((lx - 0.12, ly - 0.08, 1.13), (0.022, 0.022, 0.016), 8), 'bulb')
    add('desk_nb', box(0.52, 2.72, zt, 0.74, 2.90, zt + 0.014), 'bk_terra')
    add('desk_nb', box(0.55, 2.74, zt + 0.014, 0.73, 2.89, zt + 0.024), 'bk_white')
    plant('desk_pl', 0.45, 3.0, zt, 0.045, 0.07, rng, 8, pot='terra')
    shoe('slippers', 1.20, 0.30, 0.0, 'shoe_white', 1.45); shoe('slippers', 1.33, 0.32, 0.0, 'shoe_white', 1.62)
    # window shelf at 2.35 m with books and boxes
    wood('wshelf', WX0 - 0.03, 2.88, 2.33, WX1 + 0.03, D, 2.36, 'oak')
    books_row('wsh_bk', 0.20, 2.99, 2.36, 9, rng)
    for k, x in enumerate((0.72, 0.98, 1.22)):
        add('wsh_box', rbox((x, 2.99, 2.36 + 0.08), (0.22, 0.2, 0.16), 0.015, 3), 'box_white' if k != 1 else 'box_linen')


def build():
    materials()
    rng = np.random.default_rng(5)
    build_shell()
    build_bed(rng)
    build_platform(rng)
    build_wardrobe(rng)
    build_desk(rng)
    if LONG:
        mat('fig_mid', col=srgb(128, 132, 140), rough=0.48)               # mid grey: reads against the white walls
        FIG[0] = fg.figure('fig', 'adult', pose='stand', at=(0.74, 0.70, 58.0), mat='fig_mid')


# ------------------------------------------------------------------------------------------- camera
VF_OVER, VF_IN = 48.0, 85.0
ORB_C = np.array([1.5, 2.05, 1.2])
ORB_DIST, ORB_PITCH, ORB_PUSH = 8.25, -68.0, 0.12   # metres closer per second during the opening
PHI0, RATE = -12.0, 6.0                     # frame-1 orbit angle (camera yaw) and circling speed, degrees / s


def P(x, y, z, yaw, pitch, vfov=VF_IN):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch, vfov=vfov)


def orbit(yaw, t=0.0):
    """Overhead orbit pose at camera yaw; t (s from frame 1) pushes in slowly (negative t = before the loop point)."""
    y, p = math.radians(yaw), math.radians(ORB_PITCH)
    d = np.array([math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), math.sin(p)])
    return dict(pos=tuple(ORB_C - (ORB_DIST - ORB_PUSH * t) * d), yaw=yaw, pitch=ORB_PITCH, vfov=VF_OVER)


def mix(a, b, s, sa=None, sv=None, lift=0.0):
    """Pose between a and b: position by s, angles by sa (default s), field of view by sv (default sa)."""
    sa = s if sa is None else sa
    sv = sa if sv is None else sv
    pa, pb = np.array(a['pos']), np.array(b['pos'])
    dyaw = (b['yaw'] - a['yaw'] + 180) % 360 - 180
    return dict(pos=tuple(pa + (pb - pa) * s), yaw=a['yaw'] + dyaw * sa,
                pitch=a['pitch'] + (b['pitch'] - a['pitch']) * sa + lift * math.sin(math.pi * s),
                vfov=a['vfov'] + (b['vfov'] - a['vfov']) * sv)


def ease_in_out(u, k=2.0):
    u = c01(u)
    return u ** k / (u ** k + (1 - u) ** k)


# 15 s cut stations
S2A = (P(1.05, -1.55, 3.05, 14.0, -33.0, VF_OVER), P(0.62, -1.30, 2.92, 20.0, -31.0, VF_OVER))   # low, slow sideways glide
S2C = P(0.45, 0.15, 1.70, 72.0, -34.0)                                                            # just inside the door
S3A = (P(1.42, 1.25, 1.50, 270.0, 14.0), P(1.42, 1.82, 1.36, 262.0, -8.0))                        # wardrobe, straight on
S3B = (P(1.12, 0.10, 1.05, 4.0, -12.0, 56.0), P(0.98, 0.42, 0.98, 14.0, -10.0, 56.0))                      # aisle from the window end
S4 = (P(0.30, 0.25, 2.15, 46.0, -22.0), P(0.85, 0.52, 2.08, 44.0, -17.0))                         # wide from the door corner


def segs_15():
    o_end = orbit(PHI0 + RATE * 4.5, 4.5)
    return [
        (0.0, 4.5, lambda u, t: orbit(PHI0 + RATE * t, t)),
        (4.5, 5.0, lambda u, t: mix(o_end, S2A[0], smooth(u))),
        (5.0, 6.4, lambda u, t: mix(S2A[0], S2A[1], u)),
        (6.4, 7.0, lambda u, t: mix(S2A[1], S2C, ease_in_out(u, 1.6), sa=smooth(u), sv=smooth(c01((u - 0.25) / 0.75)))),
        (7.0, 7.22, lambda u, t: mix(S2C, S3A[0], smooth(u), lift=2.0)),
        (7.22, 8.75, lambda u, t: mix(S3A[0], S3A[1], u)),
        (8.75, 8.97, lambda u, t: mix(S3A[1], S3B[0], smooth(u), lift=2.0)),
        (8.97, 10.95, lambda u, t: mix(S3B[0], S3B[1], u)),
        (10.95, 11.15, lambda u, t: mix(S3B[1], S4[0], smooth(u), lift=2.0)),
        (11.15, 12.4, lambda u, t: mix(S4[0], S4[1], u)),
        (12.4, 15.0, lambda u, t: rise(S4[1], orbit(PHI0 + RATE * (t - 15.0), t - 15.0), u)),
    ]


def rise(a, b, u):
    """Out of the room to the frame-1 orbit: angles and field of view lead, height follows (keeps the sky out)."""
    sa = smooth(c01(u / 0.42))
    s = smooth(u) ** 1.45 if u < 1 else 1.0
    return mix(a, b, s, sa=sa)


def segs_long():
    """45 s cut: orbit, descent, then one zone at a time (see PLAN.md, long cut), rising back to frame 1 at 45 s."""
    o_end = orbit(PHI0 + RATE * 5.0, 5.0)
    LA = P(0.62, -1.30, 2.92, 18.0, -31.0, VF_OVER)
    A = (P(0.74, 0.65, 1.55, -8.0, 6.0), P(0.82, 2.05, 1.40, 8.0, -26.0))                 # window desk, push in
    Bs = (P(1.38, 2.40, 1.45, -70.0, -20.0), P(1.25, 1.40, 1.30, -22.0, -12.0))          # slide along the window
    C = (P(0.50, 0.60, 0.95, 62.0, 6.0), P(1.20, 0.12, 0.90, 14.0, 10.0))                 # low circle, bed corner
    Ds = (P(0.50, 0.30, 1.50, 62.0, -28.0), P(1.05, 0.15, 1.75, 70.0, -36.0))            # along the stairs
    E = (P(1.42, 1.10, 1.55, 276.0, 16.0), P(1.42, 1.80, 1.36, 260.0, -8.0))             # wardrobe, straight on
    F = (P(1.38, 1.05, 1.10, 285.0, -26.0), P(1.30, 2.10, 1.30, 235.0, -18.0))           # wardrobe drawers, toward the desk
    G = (P(1.20, 0.55, 1.45, 28.0, -10.0), P(1.38, 1.05, 2.00, 48.0, -30.0))                # rising glide up the stairs
    Hs = (P(1.15, 0.04, 1.32, -2.0, -18.0, 70.0), P(0.95, 0.42, 1.22, 14.0, -16.0, 70.0))  # the rail, low in the aisle
    J1 = (P(1.28, 2.58, 1.58, 192.0, -16.0), P(1.32, 2.25, 1.45, 210.0, -12.0))            # dolly: the person comes in
    J2 = (P(1.28, 0.06, 1.35, -12.0, -8.0), P(1.20, 0.30, 1.25, 8.0, -10.0))          # window end, down the aisle
    K = (P(2.88, 0.10, 2.40, -46.0, -30.0), P(2.40, 0.38, 2.30, -28.0, -26.0))           # high south-east corner
    sw = lambda a, b: (lambda u, t: mix(a, b, smooth(u), lift=2.0))
    gl = lambda st: (lambda u, t: mix(st[0], st[1], u))
    return [
        (0.0, 5.0, lambda u, t: orbit(PHI0 + RATE * t, t)),
        (5.0, 5.5, lambda u, t: mix(o_end, LA, smooth(u))),
        (5.5, 7.0, lambda u, t: mix(LA, A[0], ease_in_out(u, 1.6), sa=smooth(c01((u - 0.4) / 0.6)), sv=smooth(c01((u - 0.45) / 0.55)))),
        (7.0, 9.8, gl(A)), (9.8, 10.1, sw(A[1], Bs[0])), (10.1, 12.75, gl(Bs)), (12.75, 13.0, sw(Bs[1], C[0])),
        (13.0, 16.0, gl(C)), (16.0, 16.3, sw(C[1], Ds[0])), (16.3, 19.0, gl(Ds)), (19.0, 19.25, sw(Ds[1], E[0])),
        (19.25, 21.45, gl(E)), (21.45, 21.7, sw(E[1], F[0])), (21.7, 24.0, gl(F)), (24.0, 24.25, sw(F[1], G[0])),
        (24.25, 27.3, gl(G)), (27.3, 27.6, sw(G[1], Hs[0])), (27.6, 31.0, gl(Hs)), (31.0, 31.25, sw(Hs[1], J1[0])),
        (31.25, 34.6, gl(J1)), (34.6, 34.9, sw(J1[1], J2[0])), (34.9, 38.6, gl(J2)), (38.6, 38.9, sw(J2[1], K[0])),
        (38.9, 41.0, gl(K)),
        (41.0, 45.0, lambda u, t: rise(K[1], orbit(PHI0 + RATE * (t - 45.0), t - 45.0), u)),
    ]


SEGS = segs_long() if LONG else segs_15()
REST_STATIONS = [orbit(PHI0), S2A[0], S2C, S3A[0], S3B[0], S4[0], orbit(PHI0 + 22.5), mix(S4[1], orbit(PHI0), 0.3)]


def camera(t):
    if REST:
        return dict(REST_STATIONS[min(len(REST_STATIONS) - 1, int(t))])
    for t0, t1, f in SEGS:
        if t < t1:
            return f((t - t0) / (t1 - t0), t)
    t0, t1, f = SEGS[-1]
    return f(1.0, t)


def inside(t):
    c = camera(t)
    return c['pos'][2] < CEIL_Z


# ------------------------------------------------------------------------------------------- lights (fixed slots)
LSKY = (1.25, 1.28, 1.34)
LSUN = (48000.0, 46500.0, 43000.0)
LWIN = (5.0, 5.3, 5.8)
LFILL = (1.45, 1.45, 1.43)
LDOOR = (1.6, 1.58, 1.55)
LHB = (380.0, 290.0, 185.0)
LLED = (80.0, 64.0, 42.0)
LDESK = (200.0, 156.0, 98.0)
LWR = (26.0, 23.0, 17.0)


def lights(mats4, vis):
    off = (0.0, 0.0, 0.0)
    f = float(mats4['fadekey'][0, 3])          # 0 = camera above the room, 1 = inside under the ceiling
    dim = 0.86 if vis.get('led_lip') else 1.0   # lamps on: daylight eases down a little so the warm glow reads

    def k(L, on, s=1.0):
        return tuple(v * s for v in L) if on else off
    Ls = []
    Ls.append(rect_light((-8.5, -8.5, 9.0), (0, 20.0, 0), (20.0, 0, 0), k(LSKY, True, 0.27 * dim), always=1))                                    # 0 sky (down)
    Ls.append(spot_rect((0.70, D + 2.2, 2.35), (0.12, -1.0, -0.58), 0.06, k(LSUN, True, dim), 0.0))                         # 1 window beam
    Ls.append(rect_light((WX0, D + 0.11, WZ0), (WX1 - WX0, 0, 0), (0, 0, WZ1 - WZ0), k(LWIN, True), always=1))         # 2 window sky
    Ls.append(rect_light((0.25, 0.25, CEIL_Z - 0.04), (0, D - 0.5, 0), (W - 0.5, 0, 0), k(LFILL, True, (0.35 + 0.65 * f) * dim), always=1))  # 3 fill (down)
    Ls.append(rect_light((DX0, 0.01, 0.3), (0, 0, 1.7), (DX1 - DX0, 0, 0), k(LDOOR, True, (0.2 + 0.8 * f) * dim), always=1))               # 4 door fill (+y)
    Ls.append(sphere_light((2.45, 2.98, 2.03), 0.025, k(LHB, vis.get('hb_on'))))                                       # 5 ledge lamp
    Ls.append(rect_light((1.48, 1.02, 0.964), (0, 2.06, 0), (0.012, 0, 0), k(LLED, vis.get('led_lip'))))              # 6 lip LED (down)
    Ls.append(rect_light((1.51, 0.20, 0.70), (0, 0.02, 0), (0.72, 0, 0), k(LLED, vis.get('led_step2'), 0.6)))          # 7 stair LEDs
    Ls.append(sphere_light((0.92, 2.90, 1.13), 0.02, k(LDESK, vis.get('desk_on'))))                                    # 8 desk lamp
    Ls.append(rect_light((0.41, 1.04, 1.77), (0, 0.92, 0), (0.02, 0, 0), k(LWR, vis.get('wr_led'))))                   # 9 wardrobe strip
    return Ls


BLENDER = dict(
    exposure=-0.10,
    look='AgX - Medium High Contrast',
    separate=['backdrop'],
    fill_lights=[3, 4],
    world=0.30,
    wood_scale=(55.0, 1.6),
    bake_rect={'backdrop': (-6.0, 8.0, -3.0, 6.0), 'floor': (0.0, 3.1, 0.0, 3.0)},
    bake_px={'backdrop': 0.006, 'floor': 0.0015},
)


# ------------------------------------------------------------------------------------------- timeline
def bed_path(B):
    """Bed transform relative to its final (raised) place: drop at B.bed, slide east, ride up on the platform."""
    def f(t):
        if t < B['bed'] - 0.26:
            return np.eye(4), False
        off = BED_OFF.copy()
        u = (t - (B['bed'] - 0.26)) / 0.26
        if u < 1:
            off[2] += 3.2 * (1 - u * u)
        else:
            tau = t - B['bed']
            off[2] += 0.03 * math.exp(-tau / 0.07) * abs(math.sin(math.pi * tau / 0.11))
        s0, s1 = B['bed_slide']
        if t > s0:
            off[0] += 0.75 * (eob((t - s0) / (s1 - s0), 0.6))
        g0, g1 = B['plat']
        if t > g0:
            off[2] += 0.70 * plat_g(t, g0, g1)
        return T(*off), True
    return f


def plat_g(t, g0, g1):
    u = c01((t - g0) / (g1 - g0))
    g = eoc(u)
    if t > g1:
        tau = t - g1
        g = 1 + 0.012 * math.exp(-tau / 0.07) * math.sin(2 * math.pi * tau / 0.14)
    return min(g, 1.003)


def group_path(final_c, keys):
    """keys: [(t, (cx, cy), angle_deg, mode)] -> transform T(c) Rz(a) T(-final_c); eased between keys.
    mode of a key = how we arrive at it: 'smooth' or ('xy', kx, ky) with separate easing per axis."""
    fc = np.array([final_c[0], final_c[1], 0.0])

    def f(t):
        c, a = np.array(keys[0][1], float), keys[0][2]
        for (ta, ca, aa, _), (tb, cb, ab, mode) in zip(keys, keys[1:]):
            if t <= ta:
                break
            u = c01((t - ta) / (tb - ta))
            if mode == 'smooth':
                ux = uy = ua = smooth(u)
            elif mode == 'back':
                ux = uy = ua = eob(u, 0.5)
            else:
                _, kx, ky = mode
                ux, uy, ua = smooth(c01(u * kx[0] - kx[1])), smooth(c01(u * ky[0] - ky[1])), smooth(u)
            c = np.array([ca[0] + (cb[0] - ca[0]) * ux, ca[1] + (cb[1] - ca[1]) * uy])
            a = aa + (ab - aa) * ua
        return T(c[0], c[1], 0) @ R('z', math.radians(a)) @ T(*(-fc))
    return f


def beats_15():
    return dict(bed=0.30, wr=0.60, bonk=0.90, desk=1.05, knock=1.18, desk_s=(1.30, 1.70), bed_slide=(1.80, 2.50),
                wr_keys=[(2.60, (1.55, 0.275), 90, None), (2.86, (0.80, 0.95), 90, ('xy', (1.5, 0.0), (1.4, 0.4))),
                         (3.06, (0.80, 0.95), 0, 'smooth'), (3.30, (0.275, 1.5), 0, 'back')],
                desk_keys=[(3.40, (2.75, 0.48), -90, None), (3.70, (0.90, 0.55), -90, 'smooth'), (3.86, (0.90, 0.55), 0, 'smooth'),
                           (4.16, (1.025, 2.35), 0, ('xy', (2.5, 0.0), (1.0, 0.0))), (4.40, (0.75, 2.85), 0, 'smooth')],
                wshelf=4.75, legs=(4.95, 5.12), plat=(5.10, 5.90), steps=(5.98, 6.18, 6.38),
                sdr=[(6.48, 6.92), (6.58, 7.00), (6.68, 7.08)], wr_top=(7.26, 7.50), wd_open=7.62, wr_cl=(7.84, 8.02),
                wd_close=8.42, rail_out=(8.95, 9.45), rail_back=(10.55, 10.88), ledge=(11.20, 11.34), ledge_bk=11.44,
                ledge_pl=11.56, hb_lamp=11.68, wsh_bk=11.78, wsh_box=11.88, desk_lamp=11.96, desk_nb=12.04, desk_pl=12.10,
                on=12.18, slippers=11.32, chair_out=(12.85, 14.30), ddr=(13.35, 14.20))


def beats_long():
    """45 s cut: the same opening (shuffle a little slower), then one zone at a time; the bed stays low until 13 s."""
    B = beats_15()
    sc = lambda t: round(1.3 + (t - 1.3) * 1.13, 3) if t >= 1.3 else t
    B['desk_s'] = tuple(sc(t) for t in B['desk_s'])
    B['bed_slide'] = tuple(sc(t) for t in B['bed_slide'])
    B['wr_keys'] = [(sc(t), c, a, m) for (t, c, a, m) in B['wr_keys']]
    B['desk_keys'] = [(sc(t), c, a, m) for (t, c, a, m) in B['desk_keys']]
    B.update(wshelf=7.40, wsh_bk=7.75, wsh_box=7.98, desk_drs=[(8.30, 9.20), (8.50, 9.40)],
             chair_out=(10.30, 12.55), desk_lamp=10.75, desk_nb=11.05, desk_pl=11.35,
             legs=(13.35, 13.52), plat=(13.50, 14.50), steps=(14.80, 15.10, 15.40),
             sdr=[(16.40, 16.95), (16.62, 17.17), (16.84, 17.39)], ddr=(17.85, 18.80),
             wr_top=(19.50, 19.95), wd_opens=[(20.10, 23.40), (32.90, 34.40)], wr_cl=(20.35, 20.75),
             wr_drs=[(21.80, 22.60), (22.05, 22.85)],
             ledge=(24.50, 24.68), ledge_bk=24.85, ledge_pl=25.08, hb_lamp=25.30, slippers=25.50, mslide=(25.80, 26.55),
             rails=[((27.80, 28.50), (29.75, 30.10)), ((37.05, 37.65), (38.60, 38.95))], on=39.40)
    return B


def person(tl, B):
    """Long cut: a faceless stand-in walks in through the door, opens the wardrobe (no bonk), stretches in the aisle,
    steps back and pulls the rail out by its end handle; then stays, so the last wide shows the room in use."""
    fig = FIG[0]
    A0, A1, A2, A3 = (0.55, -0.55, 0.0), (0.72, 0.62, None), (1.15, 1.45, -90.0), (0.74, 0.70, 58.0)
    wpose, wat = fg.walk([(31.35, A0), (31.95, A1), (32.50, A2), (36.0, A2), (36.65, A3)], fig)
    OPEN = dict(sh_r=72, sh_r_out=4, elbow_r=18, sh_l=10, sh_l_out=6, elbow_l=10, spine=4)
    PULL = dict(sh_r=48, sh_l=40, sh_r_out=6, sh_l_out=8, elbow_r=12, elbow_l=20, spine=22, neck=8, hip_l=12, hip_r=6, knee_l=10, knee_r=4)
    poses = fg.track([(32.50, 'stand'), (32.80, OPEN), (33.15, OPEN), (33.45, 'stand'), (34.15, OPEN), (34.50, 'stand'),
                      (34.75, 'stand'), (35.05, 'reach_both'), (35.80, 'reach_both'), (36.0, 'stand'),
                      (36.65, 'stand'), (36.95, PULL), (38.45, PULL), (38.75, 'stand')])

    def pose(t):
        if t < 32.50 or 36.0 <= t < 36.65:
            return wpose(t)
        return poses(t)
    fig.animate(tl, pose=pose, at=wat, visible=lambda t: t >= 31.0)


def timeline():
    tl = Timeline(rk, FPS)
    I = np.eye(4)
    hidden = lambda t: (I, False)

    def ev(t, name, s=0.5, kind='tick', **kw):
        e = dict(t=round(t, 3), name=name, strength=s, kind=kind); e.update(kw)
        tl.events.append(e)

    def cam_vis(name, rule):
        tl.custom(name, lambda t: (I, rule(t)))

    cam_vis('ceiling', inside)
    cam_vis('backdrop', lambda t: camera(t)['pos'][2] < 4.0)
    up = lambda t: inside(t) and camera(t)['pos'][1] > 0.02
    cam_vis('south_up', up)
    dopen = (31.0, 32.75) if LONG else None

    def door(t):                                   # closed, except while the person comes in (long cut)
        a = 0.0
        if dopen and dopen[0] - 0.3 < t < dopen[1] + 0.3:
            a = 92 * (smooth((t - dopen[0] + 0.3) / 0.3) if t < dopen[1] else 1 - smooth((t - dopen[1]) / 0.3))
        return about((DX0, -0.03, 0), R('z', math.radians(a))), up(t)
    tl.custom('door', door)
    if dopen:
        ev(dopen[0], 'door_open', 0.35, 'swish'); ev(dopen[1] + 0.3, 'door_shut', 0.5, 'thud')

    def fade(t):                                 # light fade value carried by a hidden piece
        ts = np.linspace(t - 0.25, t + 0.25, 11)
        return float(np.mean([1.0 if inside(x) else 0.0 for x in ts]))
    tl.custom('fadekey', lambda t: (T(fade(t), 0, 0), False))
    if REST:
        for nm in ('led_lip', 'led_step0', 'led_step1', 'led_step2', 'hb_on', 'desk_on', 'wr_led'):
            tl.custom(nm, hidden)
        return tl
    B = beats_long() if LONG else beats_15()
    drop, fly, slide, grow = tl.drop, tl.fly, tl.slide, tl.grow

    def appear(name, t_on, t_off=None):
        tl.custom(name, lambda t: (I, t >= t_on and (t_off is None or t < t_off)))

    def land(name, t1, h, dur):
        """A whole piece drops from h above its place, lands at t1 with a small bounce (no scaling, nothing grows)."""
        def f(t):
            if t < t1 - dur:
                return I, False
            u = (t - (t1 - dur)) / dur
            z = h * (1 - u * u) if u < 1 else 0.06 * h * math.exp(-(t - t1) / 0.07) * abs(math.sin(math.pi * (t - t1) / 0.11))
            return T(0, 0, z), True
        tl.custom(name, f)
        return f

    def with_base(base, local):
        return lambda t: (base(t)[0] @ local(t)[0], base(t)[1] and local(t)[1])

    # ---------------- the bed (frame, legs, mattress, bedding all ride together)
    bed = bed_path(B)
    l0, l1 = B['legs']
    tl.custom('bed_frame', bed)
    ms = B.get('mslide')

    def bedding(t):                                # long cut: the mattress slides 30 cm toward the aisle and back
        M, v = bed(t)
        if ms is None or t < ms[0]:
            return M, v
        x = -0.30 * (smooth((t - ms[0]) / 0.35) if t < ms[1] else 1 - smooth((t - ms[1]) / 0.35))
        return T(x, 0, 0) @ M, v
    for nm in ('mattress', 'duvet', 'throw', 'pil_w', 'pil_b'):
        tl.custom(nm, bedding)
    if ms is not None:
        ev(ms[0] + 0.35, 'mattress_out', 0.5, 'swish'); ev(ms[1] + 0.35, 'mattress_in', 0.55, 'clack')
    tl.custom('bed_legs', lambda t: (bed(t)[0] @ about((0, 0, 0.85), S(1, 1, 1 - 0.98 * smooth((t - l0) / (l1 - l0)))), bed(t)[1]))
    ev(B['bed'], 'bed_land', 1.0, 'thud')
    ev(B['bed_slide'][0], 'bed_scrape', 0.8, 'scrape', len=0.62)
    ev(B['bed_slide'][1], 'bed_clack', 1.0, 'clack')
    ev(l1, 'legs_up', 0.4, 'tick')

    # ---------------- the wardrobe: lands on the door wall, bonks, then slides + turns to the west wall
    wkeys = B['wr_keys']
    wpath = group_path(CW, wkeys)
    t_w = B['wr']

    def wr(t):
        if t < t_w - 0.2:
            return I, False
        M = wpath(t)
        u = (t - (t_w - 0.2)) / 0.2
        z = 0.7 * (1 - u * u) if u < 1 else 0.025 * math.exp(-(t - t_w) / 0.07) * abs(math.sin(math.pi * (t - t_w) / 0.11))
        return T(0, 0, z) @ M, True
    tl.custom('wr', wr)
    tl.custom('wr_box', wr)
    wdr = B.get('wr_drs')
    for k in range(2):
        if wdr is None:
            tl.custom(f'wr_dr{k}', wr)
            continue
        o, c = wdr[k]
        f = lambda t, o=o, c=c: (wr(t)[0] @ T(0.36 * (eob(c01((t - o) / 0.18), 0.8) if t < c else 1 - smooth((t - c) / 0.16)), 0, 0), wr(t)[1])
        tl.custom(f'wr_dr{k}', f)
        ev(o + 0.1, f'wr_dr{k}_open', 0.35, 'swish'); ev(c + 0.16, f'wr_dr{k}_shut', 0.5, 'clack')
        if k == 1:
            drop('wr_dr1_c', o + 0.22, o + 0.40, 0.3, 0.05, 0.35, parent=f)
    if wdr is None:
        tl.custom('wr_dr1_c', wr)
    ev(t_w, 'wr_land', 0.85, 'thud')
    ev(wkeys[1][0], 'wr_clack1', 0.6, 'clack'); ev(wkeys[2][0], 'wr_clack2', 0.7, 'clack'); ev(wkeys[3][0], 'wr_clack3', 0.9, 'clack')
    tb = B['bonk']
    opens = B.get('wd_opens', [(B.get('wd_open'), B.get('wd_close'))])
    to, tc = opens[0]

    def door_angle(t):
        a = 0.0
        if tb - 0.16 < t < tb + 0.40:                  # the bonk: swing to 64 deg, hit the bed, wobble, close
            if t < tb:
                a = 64 * eoc((t - (tb - 0.16)) / 0.16) ** 1.4
            elif t < tb + 0.22:
                tau = t - tb
                a = 64 - 7 * math.exp(-tau / 0.06) * abs(math.sin(math.pi * tau / 0.07))
            else:
                a = 64 * (1 - smooth((t - tb - 0.22) / 0.18))
        for to_, tc_ in opens:                         # wide open, no bonk
            if to_ - 0.18 < t < tc_ + 0.18:
                if t < to_:
                    a = 100 * eob((t - (to_ - 0.18)) / 0.18, 0.8)
                elif t < tc_:
                    a = 100
                else:
                    a = 100 * (1 - smooth((t - tc_) / 0.18))
        return a
    for nm, hinge, sg in (('wd_s', (0.55, 1.0, 0), -1), ('wd_n', (0.55, 2.0, 0), 1)):
        tl.custom(nm, lambda t, hinge=hinge, sg=sg: (wr(t)[0] @ about(hinge, R('z', math.radians(sg * door_angle(t)))), wr(t)[1]))
    ev(tb, 'bonk', 1.0, 'bonk'); ev(tb + 0.40, 'wd_shut0', 0.4, 'clack')
    ev(to, 'no_bonk', 0.9, 'chime2'); ev(tc + 0.18, 'wd_shut', 0.7, 'thud')
    for k, (to_, tc_) in enumerate(opens[1:]):
        ev(to_, f'no_bonk{k}', 0.45, 'chime2'); ev(tc_ + 0.18, f'wd_shut{k}', 0.6, 'thud')
    # contents fly in while the doors are open
    for k, nm in enumerate(('wr_cl0', 'wr_cl1')):
        ta = B['wr_cl'][k]
        fly(nm, ta, ta + 0.18, (0.9, 0, 0.05), 0.05, 0.45, 'tick')
    tl.custom('wr_led', lambda t: (wr(t)[0], to - 0.1 <= t < tc + 0.1))
    gt0, gt1 = B['wr_top']
    def wtop(t):                                   # one piece, slid in from the aisle with a small hop (the ceiling is too low to drop it)
        if t < gt0:
            return I, False
        u = (t - gt0) / (gt1 - gt0)
        if u < 1:
            return T(0.55 * (1 - eoc(u)), 0, -0.04 * math.sin(math.pi * u)), True
        tau = t - gt1
        return T(0, 0, 0.012 * math.exp(-tau / 0.07) * abs(math.sin(math.pi * tau / 0.11))), True
    tl.custom('wr_top', wtop)
    ev(gt1, 'wr_top', 0.8, 'thud')

    # ---------------- the desk + tucked chair
    dkeys = B['desk_keys']
    dpath0 = group_path(CD, [(0.0, (2.75, 1.15), -90, None), (B['desk_s'][0], (2.75, 1.15), -90, 'smooth'),
                             (B['desk_s'][1], (2.75, 0.48), -90, 'back')] + dkeys[1:])
    t_d = B['desk']

    def desk(t):
        if t < t_d - 0.2:
            return I, False
        u = (t - (t_d - 0.2)) / 0.2
        z = 0.6 * (1 - u * u) if u < 1 else 0.02 * math.exp(-(t - t_d) / 0.07) * abs(math.sin(math.pi * (t - t_d) / 0.11))
        return T(0, 0, z) @ dpath0(t), True
    tl.custom('desk', desk)
    ddrs = B.get('desk_drs')
    for k in range(2):
        if ddrs is None:
            tl.custom(f'desk_dr{k}', desk); tl.custom(f'desk_dr{k}_c', desk)
            continue
        o, c = ddrs[k]
        f = lambda t, o=o, c=c: (desk(t)[0] @ T(0, -0.30 * (eob(c01((t - o) / 0.16), 0.8) if t < c else 1 - smooth((t - c) / 0.15)), 0), desk(t)[1])
        tl.custom(f'desk_dr{k}', f)
        drop(f'desk_dr{k}_c', o + 0.20, o + 0.36, 0.25, 0.05, 0.35, parent=f)
        ev(o + 0.08, f'desk_dr{k}_open', 0.35, 'swish'); ev(c + 0.15, f'desk_dr{k}_shut', 0.5, 'clack')
    tk = B['knock']

    def pull(t):                                   # chair pull-out along the desk's local -y
        if t < tk - 0.10:
            return 0.20
        if t < tk:
            return 0.20 + 0.07 * ((t - (tk - 0.10)) / 0.10) ** 2
        if t < tk + 0.12:
            tau = t - tk
            return 0.27 - 0.05 * math.sin(math.pi * tau / 0.12)
        return 0.27 * (1 - smooth((t - tk - 0.12) / 0.25))
    co0, co1 = B['chair_out']

    def pull2(t):                                  # late: the chair rolls out from the desk and back (room in use)
        if t < co0:
            return pull(t)
        if t < co1:
            return 0.34 * eob(c01((t - co0) / 0.25), 0.6)
        return 0.34 * (1 - smooth((t - co1) / 0.25))
    tl.custom('chair', lambda t: (desk(t)[0] @ T(0, -pull2(t), 0), desk(t)[1]))
    ev(co0 + 0.25, 'chair_out', 0.45, 'clack'); ev(co1 + 0.25, 'chair_in', 0.4, 'clack')
    ev(t_d, 'desk_land', 0.8, 'thud'); ev(tk, 'chair_knock', 0.55, 'thud')
    ev(B['desk_s'][1], 'desk_clack1', 0.7, 'clack')
    for kk, nm in ((1, 'dc2'), (2, 'dc3'), (3, 'dc4'), (4, 'dc5')):
        ev(dkeys[kk][0], nm, 0.6 + 0.08 * kk, 'clack')

    # ---------------- window shelf
    slide('wshelf', B['wshelf'] - 0.16, B['wshelf'], (0, -0.35, 0), 1.0, 0.5, 'clack')

    # ---------------- platform grows under the bed; stairs stack; stair drawers pop
    g0, g1 = B['plat']
    pg = lambda t: (T(0, 0, -1.0 * (1 - plat_g(t, g0, g1))), t >= g0)     # one rigid full-size lift rising from the floor
    tl.custom('plat', pg)
    q0, q1 = B['ddr']

    def ddr(t):                                    # the deep drawer slides out with a suitcase and spare bedding
        M, v = pg(t)
        if t < q0:
            return M, v
        y = -0.78 * (eob(c01((t - q0) / 0.25), 0.5) if t < q1 else 1 - smooth((t - q1) / 0.22))
        return T(0, y, 0), True
    tl.custom('ddr', ddr); tl.custom('ddr_c', ddr)
    ev(q0 + 0.25, 'ddr_open', 0.5, 'swish'); ev(q1 + 0.22, 'ddr_shut', 0.6, 'clack')
    ev(g0 + 0.05, 'plat_whoosh', 0.4, 'swish'); ev(g1, 'plat_land', 1.0, 'thud')
    for k in range(3):
        ts = B['steps'][k]
        sg = land(f'step{k}', ts, 0.45, 0.18)
        ev(ts, f'step{k}', 0.55 + 0.15 * k, 'thud')
        o, c = B['sdr'][k]
        dr = lambda t, ts=ts, o=o, c=c: (T(-0.48 * (eob(c01((t - o) / 0.12), 1.4) if t < c else 1 - smooth((t - c) / 0.14)), 0, 0), t >= ts - 0.16)
        tl.custom(f'sdr{k}', dr)
        tl.custom(f'sdr{k}_c', dr)
        ev(o + 0.06, f'sdr{k}_open', 0.4, 'swish'); ev(c + 0.14, f'sdr{k}_shut', 0.55, 'clack')

    # ---------------- the rail (rides the platform growth, then glides out and back)
    rails = B.get('rails', [(B.get('rail_out'), B.get('rail_back'))])

    def rail(t):
        M, v = pg(t)
        if t < rails[0][0][0]:
            return M, v
        x = 0.0
        for (r0, r1), (b0, b1) in rails:
            if r0 <= t < b0:
                x = -0.55 * eob((t - r0) / (r1 - r0), 0.35)
            elif b0 <= t < b1 + 0.01:
                x = -0.55 * (1 - smooth((t - b0) / (b1 - b0)))
        return T(x, 0, 0), True
    tl.custom('rail', rail); tl.custom('rail_cl', rail)
    for k, ((r0, r1), (b0, b1)) in enumerate(rails):
        ev(r0 + 0.25, f'rail_swish{k}', 0.6 if k == 0 else 0.45, 'swish'); ev(r1, f'rail_out{k}', 0.6, 'clack')
        ev(b1, f'rail_back{k}', 0.6, 'clack')

    # ---------------- headboard ledge, window shelf things, desk things, lights on
    e0, e1 = B['ledge']
    land('ledge', e1, 0.35, e1 - e0)
    ev(e1, 'ledge', 0.6, 'clack')
    drop('ledge_bk', B['ledge_bk'] - 0.16, B['ledge_bk'], 0.3, 0.05, 0.4)
    drop('ledge_pl', B['ledge_pl'] - 0.16, B['ledge_pl'], 0.3, 0.06, 0.4)
    drop('hb_lamp', B['hb_lamp'] - 0.16, B['hb_lamp'], 0.3, 0.06, 0.45)
    drop('wsh_bk', B['wsh_bk'] - 0.16, B['wsh_bk'], 0.25, 0.05, 0.35)
    drop('wsh_box', B['wsh_box'] - 0.16, B['wsh_box'], 0.25, 0.05, 0.35)
    drop('desk_lamp', B['desk_lamp'] - 0.16, B['desk_lamp'], 0.3, 0.05, 0.45)
    drop('desk_nb', B['desk_nb'] - 0.14, B['desk_nb'], 0.2, 0.05, 0.3)
    drop('desk_pl', B['desk_pl'] - 0.14, B['desk_pl'], 0.2, 0.06, 0.3)
    on = B['on']
    for k, (nm, dt) in enumerate((('led_lip', 0.0), ('led_step0', 0.14), ('led_step1', 0.24), ('led_step2', 0.34), ('hb_on', 0.52),
                                  ('desk_on', 0.70))):
        appear(nm, on + dt)
    ev(on, 'lights_on', 0.8, 'chime'); ev(on + 0.52, 'lamp_on', 0.4, 'tick'); ev(on + 0.70, 'desk_on', 0.4, 'tick')
    drop('slippers', B['slippers'] - 0.16, B['slippers'], 0.3, 0.06, 0.4)
    if LONG:
        person(tl, B)
    return tl


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    timeline().export(DUR, camera, lights, out)
    json.dump(dict(bpm=120, MUSIC=dict(drop_at=0, chords=[[57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65], [52, 55, 59, 62]],
                                       roots=[45, 41, 43, 40], pluck_bars=list(range(0, 24)), riser=False)),
              open(os.path.join(out, 'music.json'), 'w'))
