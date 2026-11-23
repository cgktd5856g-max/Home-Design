"""Two kids, one 9 m² room: no bunk bed, a privacy split. The halves build as mirror images so most pieces land in pairs.

West half (child A, celery): raised bed over a kid-height wardrobe with sliding slatted doors, stair drawers up to it,
desk + shelves in the near corner. East half (child B, soft blue): low bed with under-bed drawers, overhead cabinets with
lift-up flaps, a chest with a toe-kick step drawer, mirrored desk. Final beat: a slatted oak partition telescopes out
between the beds, dusk, lights. White shell + light oak + two muted accents. No on-screen text.

    ROOM_REST=1 python3 ../../pipeline/run.py project.py <workdir> probe 0.5,1.5,2.5,3.5,4.5   # finished room, stations
    python3 ../../pipeline/run.py project.py <workdir> preview                                 # code-renderer preview
    ROOM_CUT=long ...                                                                          # the 45 s long cut

Units: metres. x = east, y = north, z = up. Room x 0..W, y 0..D, z 0..H. Door: south wall (x 0.85..1.75) onto a short
hallway. Window: north wall, centred on the aisle. Mirror axis x = W/2.
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
REST_OPEN = os.environ.get('ROOM_OPEN') == '1'          # rest view with the storage open (probing interiors)
REST_SPLIT = os.environ.get('ROOM_SPLIT') == '1'        # rest view with the partition closed + the kids
CUT = os.environ.get('ROOM_CUT', 'short')

W, D, H = 2.6, 3.5, 2.7
CX = W / 2
FPS = 25
DUR = 8.0 if REST else (45.0 if CUT == 'long' else 15.0)

DX0, DX1 = 0.85, 1.75                                  # door opening (south wall)
WX0, WX1, WZ0, WZ1 = 0.95, 1.65, 0.55, 2.35            # window (north wall)
BY0 = 1.45                                             # beds y 1.45..D
DK = 0.95                                              # bed width (west deck x 0..DK, east bed W-DK..W)
DKZ = 1.28                                             # underside of the raised deck (wardrobe headroom)
DKT = 1.32                                             # deck top
SY0, SY1 = 1.0, 1.45                                   # stair / chest depth band
SW = DK / 4                                            # stair column width
RZ = 0.265                                             # stair riser
EB = W - DK                                            # east bed inner edge x (1.65)
OCX0, OCZ0, OCZ1 = W - 0.40, 1.86, 2.56                # east overhead cabinets
PX = (CX - 0.031, CX - 0.010, CX + 0.011)              # partition panel tracks (x0 of each 0.02 panel)
PL = 0.72                                              # partition panel length
SUN_DIR = np.array([0.12, -0.80, -0.56]) / np.linalg.norm([0.12, -0.80, -0.56])
DL = [(0.42, 0.40), (W - 0.42, 0.40), (CX, 1.05)]
CAPTIONS = []                                          # no on-screen text


# ------------------------------------------------------------------------------------------- materials
def materials():
    mat('subfloor', tex=3, col=srgb(150, 148, 145), p=(0.12,))
    mat('floor', tex=1, col=srgb(218, 192, 158), col2=srgb(200, 172, 136), rough=0.4, f0=0.04, glossy=True, p=(0.16, 1.5))
    mat('wall', tex=3, col=srgb(241, 241, 239), p=(0.015,))
    mat('ceiling', col=srgb(247, 247, 246))
    mat('white_cab', col=srgb(244, 243, 240), rough=0.42)
    mat('white_in', col=srgb(236, 235, 232))
    mat('plinth', col=srgb(196, 194, 190))
    wood_mats('oak', srgb(216, 184, 142), seed=4.0)
    mat('celery', tex=3, col=srgb(184, 197, 158), rough=0.75, p=(0.03,))
    mat('sky_blue', tex=3, col=srgb(162, 182, 204), rough=0.75, p=(0.03,))
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
    mat('pil_blush', tex=3, col=srgb(226, 196, 186), rough=0.9, p=(0.05,))
    mat('pil_mustard', tex=3, col=srgb(222, 190, 120), rough=0.9, p=(0.05,))
    mat('rug', tex=6, col=srgb(232, 228, 220))
    mat('ceramic', col=srgb(243, 242, 238), rough=0.22, f0=0.04, glossy=True)
    mat('terra', col=srgb(200, 140, 110))
    mat('leaf', col=srgb(70, 116, 64)); mat('leaf2', col=srgb(100, 146, 78))
    mat('bulb', col=(0, 0, 0), emis=(9.0, 7.8, 6.0))
    mat('led', col=(0, 0, 0), emis=(7.5, 6.9, 5.6))
    mat('led_off', col=srgb(232, 231, 228))
    mat('dl_emis', col=(0, 0, 0), emis=(8.5, 7.8, 6.6))
    mat('backdrop', tex=9, emis=(1.35, 1.35, 1.35), p=(1.0, 0.0))
    mat('backdrop_night', tex=16, emis=(1.0, 1.0, 1.0), p=(1.0, 0.0))
    mat('box_linen', tex=3, col=srgb(214, 208, 196), p=(0.06,))
    mat('bin_grey', tex=6, col=srgb(206, 206, 204))
    for nm, c in (('cl_cream', (236, 230, 216)), ('cl_celery', (184, 198, 156)), ('cl_blue', (156, 178, 204)), ('cl_navy', (70, 84, 118)),
                  ('cl_mustard', (220, 182, 104)), ('cl_blush', (228, 190, 180)), ('cl_grey', (168, 170, 174)), ('cl_white', (244, 244, 242)),
                  ('cl_denim', (104, 128, 164)), ('cl_terra', (196, 128, 100)), ('cl_sage', (150, 170, 146))):
        mat(nm, tex=5, col=srgb(*c), p=(2, 0.008))
    for nm, c in (('bk_sage', (156, 176, 148)), ('bk_cream', (234, 224, 204)), ('bk_terra', (198, 124, 96)), ('bk_navy', (64, 78, 112)),
                  ('bk_mustard', (220, 176, 84)), ('bk_white', (242, 240, 236)), ('bk_blue', (130, 160, 196)), ('bk_blush', (226, 176, 168))):
        mat(nm, col=srgb(*c), rough=0.6)
    for nm, c in (('toy_red', (210, 112, 96)), ('toy_yellow', (232, 196, 100)), ('toy_blue', (110, 150, 200)), ('toy_green', (128, 176, 120)),
                  ('toy_white', (242, 240, 236))):
        mat(nm, col=srgb(*c), rough=0.45, f0=0.04, glossy=True)
    mat('shoe_white', col=srgb(244, 244, 240), rough=0.5)
    mat('shoe_pink', col=srgb(226, 180, 172), rough=0.5)
    mat('shoe_blue', col=srgb(140, 164, 196), rough=0.5)
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
    add(r, box(-0.2, -0.2, -0.25, 0, D + 0.2, H + 0.1), 'wall')
    add(r, box(W, -0.2, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
    # south wall with the door opening
    add(r, box(-0.2, -0.2, -0.25, DX0, 0, H + 0.1), 'wall'); add(r, box(DX1, -0.2, -0.25, W + 0.2, 0, H + 0.1), 'wall')
    add(r, box(DX0, -0.2, 2.1, DX1, 0, H + 0.1), 'wall')
    for b in (box(DX0 - 0.06, -0.012, 0, DX0, 0.012, 2.16), box(DX1, -0.012, 0, DX1 + 0.06, 0.012, 2.16),
              box(DX0 - 0.06, -0.012, 2.1, DX1 + 0.06, 0.012, 2.16)):
        add(r, b, 'white_cab')
    # short hallway behind the door (seen in the reverse angle)
    add(r, box(DX0 - 0.6, -1.8, -0.012, DX1 + 0.6, -0.2, 0.0), 'floor')
    add(r, box(DX0 - 0.8, -1.8, -0.25, DX0 - 0.6, -0.2, H + 0.1), 'wall')
    add(r, box(DX1 + 0.6, -1.8, -0.25, DX1 + 0.8, -0.2, H + 0.1), 'wall')
    add(r, box(DX0 - 0.8, -2.0, -0.25, DX1 + 0.8, -1.8, H + 0.1), 'wall')
    # north wall with the window
    add(r, box(-0.2, D, -0.25, WX0, D + 0.2, H + 0.1), 'wall'); add(r, box(WX1, D, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
    add(r, box(WX0, D, -0.25, WX1, D + 0.2, WZ0), 'wall'); add(r, box(WX0, D, WZ1, WX1, D + 0.2, H + 0.1), 'wall')
    for b in (box(WX0, D, WZ0, WX0 + 0.006, D + 0.2, WZ1), box(WX1 - 0.006, D, WZ0, WX1, D + 0.2, WZ1),
              box(WX0, D, WZ1 - 0.006, WX1, D + 0.2, WZ1)):
        add(r, b, 'sill')
    add(r, box(WX0 - 0.03, D - 0.04, WZ0 - 0.02, WX1 + 0.03, D + 0.17, WZ0), 'sill')
    fy0, fy1 = D + 0.10, D + 0.13
    for b in (box(WX0, fy0, WZ0, WX0 + 0.04, fy1, WZ1), box(WX1 - 0.04, fy0, WZ0, WX1, fy1, WZ1), box(WX0, fy0, WZ1 - 0.04, WX1, fy1, WZ1),
              box(WX0, fy0, WZ0, WX1, fy1, WZ0 + 0.04), box(CX - 0.018, fy0, WZ0, CX + 0.018, fy1, WZ1),
              box(WX0, fy0, 1.60, WX1, fy1, 1.635)):
        add(r, b, 'winframe')
    # baseboards
    for b in (box(0, 0, 0, 0.012, D, 0.07), box(W - 0.012, 0, 0, W, D, 0.07), box(0, 0, 0, DX0 - 0.06, 0.012, 0.07),
              box(DX1 + 0.06, 0, 0, W, 0.012, 0.07)):
        add(r, b, 'white_cab')
    # downlights (off) in the ceiling
    for (x, y) in DL:
        add(r, lathe([(0.034, H - 0.002), (0.046, H - 0.002), (0.047, H - 0.010), (0.050, H - 0.012), (0.052, H)], 32, (x, y)), 'white_cab')
        disc(r, (x, y), 0.036, H - 0.003, H - 0.0005, 'led_off')
    # window views: day and night
    add('bd_day', box(-10, D + 4.0, -5, 14, D + 4.05, 9), 'backdrop')
    add('bd_night', box(-10, D + 4.02, -5, 14, D + 4.07, 9), 'backdrop_night')
    # floor planks in six bands, each split in the two halves (land in mirrored pairs, far to near)
    edges = [D + 0.01, 2.92, 2.34, 1.76, 1.18, 0.6, -0.05]
    for k in range(6):
        add(f'floorW{k}', box(0, edges[k + 1], -0.012, CX, edges[k], 0.0), 'floor')
        add(f'floorE{k}', box(CX, edges[k + 1], -0.012, W, edges[k], 0.0), 'floor')


# ------------------------------------------------------------------------------------------- west: raised bed + wardrobe
def build_west(rng):
    t = 0.018
    d = 'deckW'
    # carcass under the deck: south panel, east front frame (two openings for the sliding doors), deck slab
    add(d, box(0, BY0, 0.0, DK, BY0 + t, DKZ), 'white_cab')
    add(d, box(DK - t, BY0, 0.0, DK, BY0 + 0.04, DKZ), 'white_cab')                  # front stiles
    add(d, box(DK - t, D - 0.04, 0.0, DK, D, DKZ), 'white_cab')
    add(d, box(DK - 0.06, BY0, 0.0, DK - 0.02, D, 0.05), 'plinth')
    add(d, box(0, BY0 + t, 0.0, DK - 0.02, D, 0.02), 'white_in')                     # wardrobe floor
    add(d, box(0, BY0, DKZ, DK, D, DKZ + 0.004), 'white_in')
    wood(d, 0, BY0, DKZ + 0.004, DK + 0.004, D, DKT, 'oak')                            # deck slab
    add(d, box(DK - 0.035, BY0 + 0.05, DKZ - 0.012, DK - 0.02, D - 0.05, DKZ), 'led_off')
    # slatted guard rail (L: along the east edge and the south edge beside the stair top)
    g = 'railW'
    wood(g, DK - 0.035, BY0, DKT + 0.30, DK, D, DKT + 0.33, 'oak')
    wood(g, 0.30, BY0, DKT + 0.30, DK, BY0 + 0.035, DKT + 0.33, 'oak')
    for y in np.arange(BY0 + 0.02, D - 0.02, 0.075):
        add(g, box(DK - 0.03, y, DKT, DK - 0.006, y + 0.03, DKT + 0.30), 'oak_z')
    for x in np.arange(0.32, DK - 0.04, 0.075):
        add(g, box(x, BY0 + 0.006, DKT, x + 0.03, BY0 + 0.03, DKT + 0.30), 'oak_z')
    # mattress, bedding
    add('matW', rbox((DK / 2 - 0.01, (BY0 + D) / 2 + 0.01, DKT + 0.08), (DK - 0.08, D - BY0 - 0.06, 0.16), 0.04, 5), 'mattress')
    cloth('duvetW', 0.02, DK - 0.06, BY0 + 0.05, 2.95, DKT + 0.175, DKT + 0.11, 0.035, 'duvetA', 3, sides=('e', 's'))
    add('duvetW', rbox((DK / 2 - 0.02, 2.92, DKT + 0.185), (DK - 0.06, 0.14, 0.025), 0.011, 3), 'linen_w')
    pillow('pilW1', (0.42, 3.36, DKT + 0.29), (0.56, 0.13, 0.36), -0.30, 'pil_white')
    pillow('pilW2', (0.52, 3.20, DKT + 0.26), (0.36, 0.11, 0.30), -0.22, 'pilA')
    pillow('pilW3', (0.24, 3.14, DKT + 0.25), (0.28, 0.10, 0.26), -0.18, 'pil_blush')
    # reading light over the pillow (north wall)
    rl = 'rlW'
    add(rl, xform(lathe(rprof(0.05, 0, 0.012, 0.004, 2), 24, (0, 0)), T(0.66, D, DKT + 0.62) @ R('x', math.pi / 2)), 'oak_x')
    add(rl, lathe([(0.0, DKT + 0.565), (0.05, DKT + 0.565), (0.058, DKT + 0.60), (0.04, DKT + 0.655), (0, DKT + 0.66)], 24, (0.66, D - 0.07)), 'ceramic')
    add(rl, tube([(0.66, D - 0.012, DKT + 0.62), (0.66, D - 0.07, DKT + 0.64)], 0.008, 8), 'oak_x')
    # sliding slatted doors on the wardrobe front (two tracks)
    for nm, (y0, y1), x0 in (('wdoor1', (BY0 + 0.04, 2.50), DK + 0.004), ('wdoor2', (2.46, D - 0.04), DK + 0.026)):
        add(nm, box(x0, y0, 0.05, x0 + 0.02, y1, 0.09), 'oak_y')
        add(nm, box(x0, y0, DKZ - 0.05, x0 + 0.02, y1, DKZ - 0.01), 'oak_y')
        add(nm, box(x0 + 0.002, y0, 0.09, x0 + 0.004, y1, DKZ - 0.05), 'white_in')
        for y in np.arange(y0, y1 - 0.03, 0.05):
            add(nm, box(x0, y + 0.004, 0.09, x0 + 0.02, y + 0.034, DKZ - 0.05), 'oak_z')
    add('deckW', box(DK + 0.002, BY0 + 0.04, DKZ - 0.01, DK + 0.05, D - 0.04, DKZ + 0.004), 'alu')   # top track
    # wardrobe contents: rail along y, kids' garments, shoes on the floor, folded stacks on a back shelf, boxes
    add('wrRail', tube([(0.52, BY0 + 0.05, 1.13), (0.52, D - 0.05, 1.13)], 0.011, 10), 'alu')
    for y in (BY0 + 0.05, D - 0.05):
        add('wrRail', box(0.50, y - 0.02, 1.13, 0.54, y + 0.02, DKZ), 'alu')
    gm = ['cl_celery', 'cl_cream', 'cl_denim', 'cl_mustard', 'cl_blush', 'cl_white', 'cl_navy', 'cl_sage', 'cl_terra', 'cl_grey',
          'cl_blue', 'cl_celery', 'cl_cream', 'cl_denim']
    for k, m in enumerate(gm):
        garment(f'gW{k}', 0.52, BY0 + 0.13 + k * 0.135, 1.13, rng.uniform(0.48, 0.66), 0.36, m)
    add('wrShelf', box(0.02, BY0 + t, 0.62, 0.26, D, 0.638), 'white_in')
    for k, y in enumerate((1.62, 1.94, 2.26, 2.58, 2.90, 3.22)):
        stack(f'wrStack{k // 3}', 0.14, y, 0.638, (0.22, 0.26, 0.045),
              [('cl_white', 'cl_celery', 'cl_grey'), ('cl_blush', 'cl_cream', 'cl_navy'), ('cl_mustard', 'cl_white', 'cl_denim'),
               ('cl_sage', 'cl_cream', 'cl_blue'), ('cl_grey', 'cl_white', 'cl_terra'), ('cl_cream', 'cl_celery', 'cl_navy')][k], 4, rng)
    for k, y in enumerate(np.arange(1.62, 3.3, 0.24)):
        m = ('shoe_white', 'shoe_pink', 'shoe_blue')[k % 3]
        for dx in (-0.045, 0.045):
            add('wrShoes', ellipsoid((0.70 + dx, y, 0.055), (0.035, 0.085, 0.032), 10), m)
    for k, y in enumerate((1.66, 2.0, 2.34)):
        add('wrBoxes', rbox((0.14, y, 0.32), (0.22, 0.30, 0.22), 0.015, 3), ('bin_grey', 'box_linen', 'bin_grey')[k])
    # stair drawers: four columns rising toward the west wall, each with a drawer in its top band (opens to -y)
    for k in range(4):
        x0, x1 = DK - SW * (k + 1), DK - SW * k
        top = RZ * (k + 1)
        c = f'stW{k}'
        if k > 0:
            add(c, box(x0, SY0, 0.0, x1, SY1, RZ * k), 'white_cab')
        add(c, box(x0, SY0 + 0.02, RZ * k, x0 + 0.012, SY1, top - 0.028), 'white_in')
        add(c, box(x1 - 0.012, SY0 + 0.02, RZ * k, x1, SY1, top - 0.028), 'white_in')
        add(c, box(x0, SY1 - 0.012, RZ * k, x1, SY1, top - 0.028), 'white_in')
        wood(c, x0, SY0 - 0.02, top - 0.028, x1, SY1, top, 'oak')
        drawer(f'sdW{k}', '-y', SY0, x0 + 0.012, x1 - 0.012, RZ * k + (0.012 if k == 0 else 0.0), top - 0.03, SY1 - SY0 - 0.04)
    # stair drawer contents
    for dx in (-0.04, 0.04):
        add('sdWc0', ellipsoid((DK - SW / 2 + dx, 1.22, 0.07), (0.032, 0.09, 0.03), 10), 'shoe_pink')
    stack('sdWc1', DK - SW * 1.5, 1.22, RZ + 0.03, (0.17, 0.30, 0.04), ['cl_celery', 'cl_white', 'cl_blush', 'cl_cream'], 4, rng)
    yb = 1.06
    for m, th in (('bk_sage', 0.035), ('bk_mustard', 0.03), ('bk_blush', 0.04), ('bk_blue', 0.03), ('bk_cream', 0.035), ('bk_terra', 0.03)):
        add('sdWc2', box(DK - SW * 3 + 0.03, yb, 2 * RZ + 0.03, DK - SW * 2 - 0.03, yb + th, 2 * RZ + 0.03 + 0.17), m); yb += th + 0.008
    for k, m in enumerate(('toy_red', 'toy_yellow', 'toy_blue', 'toy_green', 'toy_red', 'toy_blue')):
        add('sdWc3', tube([(0.05 + 0.025 * k, 1.08, 3 * RZ + 0.042), (0.05 + 0.025 * k, 1.30, 3 * RZ + 0.042)], 0.008, 8), m)
    add('sdWc3', box(0.04, 1.32, 3 * RZ + 0.03, 0.20, 1.40, 3 * RZ + 0.05), 'bk_white')


# ------------------------------------------------------------------------------------------- east: low bed, cabinets, chest
def build_east(rng):
    t = 0.018
    b = 'bedE'
    add(b, box(EB + 0.06, BY0 + 0.03, 0.0, W, D, 0.05), 'plinth')
    add(b, box(EB, BY0, 0.05, W, D, 0.07), 'white_in')
    add(b, box(EB, BY0, 0.05, W, BY0 + t, 0.31), 'white_cab')
    add(b, box(EB, D - t, 0.05, W, D, 0.31), 'white_cab')
    add(b, box(W - t, BY0, 0.05, W, D, 0.31), 'white_cab')
    add(b, box(EB, 2.47, 0.05, EB + 0.03, 2.50, 0.31), 'white_cab')
    wood(b, EB - 0.004, BY0, 0.29, W, D, 0.31, 'oak')
    wood(b, EB, D - 0.035, 0.31, W, D, 0.92, 'oak')                                 # low headboard
    for k, (y0, y1) in enumerate(((BY0 + 0.025, 2.465), (2.505, D - 0.025))):
        drawer(f'ubE{k}', '-x', EB, y0, y1, 0.07, 0.285, 0.80, knobs=2)
    add('matE', rbox(((EB + W) / 2 + 0.01, (BY0 + D) / 2 - 0.01, 0.39), (DK - 0.06, D - BY0 - 0.08, 0.16), 0.04, 5), 'mattress')
    cloth('duvetE', EB + 0.04, W - 0.02, BY0 + 0.05, 2.95, 0.485, 0.15, 0.035, 'duvetB', 5, sides=('w', 's'))
    add('duvetE', rbox(((EB + W) / 2 + 0.01, 2.92, 0.495), (DK - 0.06, 0.14, 0.025), 0.011, 3), 'linen_w')
    pillow('pilE1', (2.18, 3.36, 0.60), (0.56, 0.13, 0.36), -0.30, 'pil_white')
    pillow('pilE2', (2.08, 3.20, 0.57), (0.36, 0.11, 0.30), -0.22, 'pilB')
    pillow('pilE3', (2.36, 3.14, 0.56), (0.28, 0.10, 0.26), -0.18, 'pil_mustard')
    rl = 'rlE'
    add(rl, xform(lathe(rprof(0.05, 0, 0.012, 0.004, 2), 24, (0, 0)), T(1.94, D, 1.16) @ R('x', math.pi / 2)), 'oak_x')
    add(rl, lathe([(0.0, 1.105), (0.05, 1.105), (0.058, 1.14), (0.04, 1.195), (0, 1.20)], 24, (1.94, D - 0.07)), 'ceramic')
    add(rl, tube([(1.94, D - 0.012, 1.16), (1.94, D - 0.07, 1.18)], 0.008, 8), 'oak_x')
    # overhead cabinets with two lift-up flaps (facing the aisle)
    o = 'ocE'
    for bb in (box(OCX0, BY0, OCZ0, W, BY0 + t, OCZ1), box(OCX0, D - t, OCZ0, W, D, OCZ1), box(OCX0, BY0, OCZ0, W, D, OCZ0 + t),
               box(OCX0, BY0, OCZ1 - t, W, D, OCZ1), box(OCX0, 2.465, OCZ0, W, 2.485, OCZ1)):
        add(o, bb, 'white_cab')
    add(o, box(OCX0 + 0.02, BY0 + 0.05, OCZ0 - 0.006, OCX0 + 0.045, D - 0.05, OCZ0), 'led_off')
    for nm, (y0, y1) in (('flE1', (BY0 + 0.003, 2.473)), ('flE2', (2.477, D - 0.003))):
        add(nm, box(OCX0 - t, y0, OCZ0 + 0.003, OCX0, y1, OCZ1 - 0.003), 'white_cab')
        add(nm, box(OCX0 - t - 0.012, (y0 + y1) / 2 - 0.12, OCZ0 + 0.03, OCX0 - t, (y0 + y1) / 2 + 0.12, OCZ0 + 0.045), 'oak_y')
    for k, y in enumerate((1.70, 2.20, 2.73, 3.23)):
        add(f'ocBox{k}', rbox((W - 0.20, y, OCZ0 + t + 0.17), (0.32, 0.42, 0.34), 0.02, 3), ('box_linen', 'bin_grey')[k % 2])
    # chest at the bed foot: toe-kick step drawer + three drawers (open to -y), oak top
    c = 'chE'
    for bb in (box(EB, SY0, 0.10, EB + t, SY1, 1.035), box(W - t, SY0, 0.10, W, SY1, 1.035), box(EB, SY1 - t, 0.0, W, SY1, 1.035),
               box(EB, SY0 + 0.05, 0.0, W, SY1, 0.10)):
        add(c, bb, 'white_cab')
    wood(c, EB - 0.004, SY0 - 0.02, 1.035, W, SY1, 1.06, 'oak')
    drawer('tkE', '-y', SY0 + 0.03, EB + 0.02, W - 0.02, 0.006, 0.098, 0.38, front='oak_x', knobs=0)
    for k, (z0, z1) in enumerate(((0.10, 0.41), (0.41, 0.72), (0.72, 1.03))):
        drawer(f'cdE{k}', '-y', SY0, EB + t, W - t, z0, z1, SY1 - SY0 - 0.03, knobs=2)
    plant('chTop', W - 0.14, 1.22, 1.06, 0.05, 0.08, rng, 9, pot='ceramic')
    # chest + toe-kick contents
    for k, (x, m) in enumerate(((1.80, 'toy_red'), (1.92, 'toy_yellow'), (2.04, 'toy_blue'), (2.16, 'toy_green'), (2.28, 'toy_yellow'),
                                (2.40, 'toy_red'))):
        add('tkEc', rbox((x, 1.20, 0.05), (0.09, 0.09, 0.06), 0.012, 3), m)
    for k, x in enumerate((1.80, 2.06, 2.32)):
        stack('cdEc0', x + 0.08, 1.23, 0.135, (0.22, 0.30, 0.045), [('cl_blue', 'cl_white', 'cl_navy', 'cl_grey'),
                                                                    ('cl_white', 'cl_mustard', 'cl_blue', 'cl_cream'),
                                                                    ('cl_denim', 'cl_cream', 'cl_blush', 'cl_white')][k], 4, rng)
    for k, (x, m) in enumerate(((1.84, 'toy_blue'), (2.06, 'toy_yellow'), (2.30, 'toy_red'), (2.48, 'toy_green'))):
        add('cdEc1', ellipsoid((x, 1.21, 0.52), (0.075, 0.075, 0.075), 14), m)
    for k in range(4):
        disc('cdEc1', (2.17, 1.33), 0.06 - 0.01 * k, 0.45 + 0.035 * k, 0.48 + 0.035 * k, ('toy_red', 'toy_yellow', 'toy_green', 'toy_blue')[k])
    for k, x in enumerate(np.arange(1.74, 2.52, 0.075)):
        for j, y in enumerate((1.11, 1.22, 1.33)):
            m = ('cl_blush', 'cl_blue', 'cl_mustard', 'cl_white', 'cl_celery', 'cl_navy')[(k + j * 2) % 6]
            add('cdEc2', ellipsoid((x, y, 0.785), (0.033, 0.045, 0.028), 8), m)
    # under-bed drawer contents (long cut): fabric bins with toys
    for k, (y0, y1) in enumerate(((BY0 + 0.025, 2.465), (2.505, D - 0.025))):
        for j, yc in enumerate(np.linspace(y0 + 0.2, y1 - 0.2, 3)):
            add(f'ubEc{k}', rbox((2.05, yc, 0.165), (0.62, 0.26, 0.15), 0.02, 3), ('bin_grey', 'box_linen', 'bin_grey')[j])
            add(f'ubEc{k}', ellipsoid((1.92, yc, 0.23), (0.05, 0.05, 0.05), 12), ('toy_red', 'toy_blue', 'toy_yellow', 'toy_green')[(j + k) % 4])
            add(f'ubEc{k}', rbox((2.12, yc + 0.03, 0.24), (0.08, 0.08, 0.06), 0.01, 3), ('toy_yellow', 'toy_green', 'toy_red', 'toy_blue')[(j + k) % 4])


# ------------------------------------------------------------------------------------------- desks (mirrored)
def build_desks(rng):
    for side, sg in (('W', 1), ('E', -1)):
        X = (lambda x: x) if sg > 0 else (lambda x: W - x)

        def bx(x0, y0, z0, x1, y1, z1):
            a, b = sorted((X(x0), X(x1)))
            return box(a, y0, z0, b, y1, z1)

        def wd(inst, x0, y0, z0, x1, y1, z1):
            a, b = sorted((X(x0), X(x1)))
            wood(inst, a, y0, z0, b, y1, z1, 'oak')
        dk = f'desk{side}'
        wd(dk, 0, 0.0, 0.655, 0.56, 0.68, 0.685)
        add(dk, bx(0.50, 0.60, 0.0, 0.54, 0.64, 0.655), 'oak_z')                         # one slim leg at the aisle corner
        add(dk, bx(0.0, 0.0, 0.62, 0.012, 0.68, 0.655), 'white_in')                       # wall cleat
        drawer(f'ddr{side}', '+x' if sg > 0 else '-x', X(0.54), 0.08, 0.56, 0.565, 0.65, 0.46, front='oak_y')
        # desk drawer contents: pencil tray, crayons, notebook
        add(f'ddc{side}', bx(0.12, 0.14, 0.581, 0.36, 0.30, 0.596), 'bk_white')
        for k, m in enumerate(('toy_red', 'toy_yellow', 'toy_blue', 'toy_green', 'bk_blush')):
            a = X(0.14 + 0.04 * k)
            add(f'ddc{side}', tube([(a, 0.34, 0.592), (a, 0.52, 0.592)], 0.007, 8), m)
        add(f'ddc{side}', bx(0.36, 0.36, 0.581, 0.48, 0.52, 0.60), 'bk_sage' if sg > 0 else 'bk_blue')
        # two shelves + books
        for k, z in enumerate((1.06, 1.38)):
            wd(f'sh{side}{k}', 0, 0.04, z, 0.24, 0.66, z + 0.025)
        a0, a1 = sorted((X(0.02), X(0.19)))
        sp0 = [('bk_sage', 0.03, 0.21), ('bk_cream', 0.028, 0.19), ('bk_terra', 0.034, 0.22), ('bk_white', 0.026, 0.18), ('bk_mustard', 0.03, 0.2),
               ('bk_blue', 0.032, 0.22)] if sg > 0 else \
              [('bk_blue', 0.032, 0.22), ('bk_white', 0.026, 0.18), ('bk_blush', 0.034, 0.21), ('bk_navy', 0.03, 0.2), ('bk_cream', 0.028, 0.19),
               ('bk_mustard', 0.03, 0.21)]
        books_row(f'bk{side}0', a0, a1, 0.08, 1.085, sp0)
        add(f'bk{side}0', ellipsoid((X(0.11), 0.56, 1.145), (0.06, 0.06, 0.06), 14), 'toy_white')
        sp1 = sp0[::-1][:4]
        y = books_row(f'bk{side}1', a0, a1, 0.36, 1.405, sp1)
        plant(f'bk{side}1', X(0.12), 0.18, 1.405, 0.045, 0.07, rng, 8)
        # desk lamp
        lp = f'lamp{side}'
        disc(lp, (X(0.12), 0.58), 0.055, 0.685, 0.697, 'ceramic')
        add(lp, tube([(X(0.12), 0.58, 0.69), (X(0.12), 0.58, 0.98), (X(0.16), 0.56, 1.02)], 0.006, 8), 'ceramic')
        add(lp, lathe([(0.008, 1.05), (0.03, 1.04), (0.05, 1.0), (0.058, 0.975)], 24, (X(0.19), 0.54)), 'ceramic')
        add(f'lampOn{side}', ellipsoid((X(0.19), 0.54, 0.99), (0.018, 0.018, 0.018), 8), 'bulb')
        # chair: small oak chair with an accent cushion, facing the desk
        ch = f'chair{side}'
        cx, cy = X(0.70), 0.34
        for dx in (-0.15, 0.15):
            for dy in (-0.15, 0.15):
                add(ch, tube([(cx + dx * 0.9, cy + dy * 0.9, 0.38), (cx + dx, cy + dy, 0.0)], 0.014, 8), 'oak_z')
        add(ch, rbox((cx, cy, 0.39), (0.36, 0.36, 0.03), 0.01, 3), 'oak_x')
        add(ch, rbox((cx, cy, 0.42), (0.32, 0.32, 0.04), 0.015, 3), 'celery' if sg > 0 else 'sky_blue')
        bxc = X(0.88)
        for dy in (-0.14, 0.14):
            add(ch, tube([(bxc, cy + dy, 0.40), (bxc + sg * 0.02, cy + dy, 0.72)], 0.012, 8), 'oak_z')
        add(ch, rbox((bxc + sg * 0.02, cy, 0.66), (0.025, 0.34, 0.12), 0.01, 3), 'oak_y')
        add(f'mug{side}', lathe([(0, 0.685), (0.03, 0.685), (0.033, 0.76), (0.029, 0.76), (0.027, 0.695), (0, 0.695)], 20, (X(0.40), 0.12)), 'ceramic')
        add(f'mug{side}', box(X(0.20) - 0.1, 0.18, 0.685, X(0.20) + 0.1, 0.42, 0.697), 'bk_sage' if sg > 0 else 'bk_blue')


# ------------------------------------------------------------------------------------------- partition + rug
def build_partition():
    add('ptTrack', box(CX - 0.045, BY0, H - 0.04, CX + 0.045, D, H), 'white_cab')
    add('ptTrack', box(CX - 0.035, BY0, H - 0.045, CX + 0.035, D, H - 0.04), 'alu')
    for k, x0 in enumerate(PX):
        nm = f'pt{k}'
        y0 = D - PL                                   # parked at the north wall, in front of the window mullion
        wood(nm, x0, y0, 0.02, x0 + 0.02, y0 + PL, 0.06)
        wood(nm, x0, y0, H - 0.10, x0 + 0.02, y0 + PL, H - 0.06)
        for y in np.arange(y0, y0 + PL - 0.02, 0.06):
            add(nm, box(x0 + 0.002, y + 0.004, 0.06, x0 + 0.018, y + 0.040, H - 0.10), 'oak_z')
    add('rug', rbox((CX, 1.0, 0.007), (0.66, 1.7, 0.014), 0.006, 3), 'rug')


LONG_ONLY = ('dkShelf', 'dkBooks', 'dkPlush', 'fairy', 'fairyOn', 'throwW', 'rugToys')


def build_long_extras(rng):
    """Pieces used only in the long cut: a shelf over the loft bed, fairy lights on the rail, a throw, toys on the rug."""
    wood('dkShelf', 0.10, D - 0.20, DKT + 0.80, 0.86, D, DKT + 0.825, 'oak')
    books_row('dkBooks', 0.14, 0.30, D - 0.17, DKT + 0.825, [], 'y')
    x = 0.14
    for m, th, h in (('bk_sage', 0.03, 0.20), ('bk_blush', 0.035, 0.18), ('bk_cream', 0.028, 0.21), ('bk_mustard', 0.03, 0.19),
                     ('bk_blue', 0.032, 0.2)):
        add('dkBooks', box(x, D - 0.17, DKT + 0.825, x + th, D - 0.02, DKT + 0.825 + h), m); x += th + 0.004
    add('dkPlush', ellipsoid((0.62, D - 0.10, DKT + 0.905), (0.085, 0.07, 0.08), 16), 'toy_white')
    add('dkPlush', ellipsoid((0.76, D - 0.10, DKT + 0.875), (0.05, 0.05, 0.05), 12), 'pil_mustard')
    for k, y in enumerate(np.arange(BY0 + 0.08, D - 0.05, 0.11)):
        zz = DKT + 0.335 - 0.025 * math.sin(math.pi * ((y - BY0) % 0.44) / 0.44)
        add('fairy', ellipsoid((DK - 0.018, y, zz), (0.011, 0.011, 0.014), 8), 'led_off')
        add('fairyOn', ellipsoid((DK - 0.018, y, zz), (0.012, 0.012, 0.015), 8), 'bulb')
    add('fairy', tube([(DK - 0.018, BY0 + 0.05, DKT + 0.335), (DK - 0.018, D - 0.05, DKT + 0.335)], 0.002, 5), 'alu')
    cloth('throwW', 0.03, DK - 0.07, 1.62, 2.05, DKT + 0.195, DKT + 0.12, 0.03, 'pil_mustard', 11, sides=('e',), puff=0.004)
    for k, (x, y, m) in enumerate(((1.18, 0.62, 'toy_red'), (1.30, 0.70, 'toy_yellow'), (1.24, 0.80, 'toy_blue'), (1.40, 0.58, 'toy_green'))):
        add('rugToys', rbox((x, y, 0.045), (0.07, 0.07, 0.06), 0.01, 3), m)
    add('rugToys', ellipsoid((1.42, 0.86, 0.075), (0.06, 0.06, 0.06), 14), 'toy_blue')


def build():
    materials()
    rng = np.random.default_rng(9)
    build_shell()
    build_west(rng)
    build_east(rng)
    build_desks(rng)
    build_partition()
    build_long_extras(rng)
    # emitters that switch on
    add('ledDeck', box(DK - 0.035, BY0 + 0.05, DKZ - 0.0125, DK - 0.02, D - 0.05, DKZ - 0.0115), 'led')
    add('ledOc', box(OCX0 + 0.02, BY0 + 0.05, OCZ0 - 0.0065, OCX0 + 0.045, D - 0.05, OCZ0 - 0.0055), 'led')
    add('ledWr', box(0.70, BY0 + 0.08, DKZ - 0.004, 0.73, D - 0.08, DKZ - 0.002), 'led')
    add('rlOnW', ellipsoid((0.66, D - 0.07, DKT + 0.565), (0.04, 0.04, 0.008), 10), 'bulb')
    add('rlOnE', ellipsoid((1.94, D - 0.07, 1.105), (0.04, 0.04, 0.008), 10), 'bulb')
    for (x, y) in DL:
        disc('dlOn', (x, y), 0.037, H - 0.005, H - 0.0035, 'dl_emis')
    # the kids (stand-in mannequins, one per half)
    global KID_A, KID_B
    KID_A = fg.figure('kidA', 'child', pose='stand', at=(1.12, 1.22, -90), mat='fig_sage')
    KID_B = fg.figure('kidB', 'child', pose='sit', at=(EB + 0.20, 2.10, -90), seat=0.47, mat='fig_blue')


KID_A = KID_B = None


# ------------------------------------------------------------------------------------------- camera
VFOV = 85.0


def P(x, y, z, yaw, pitch):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch)


F1 = P(CX, -0.55, 1.52, 0.0, -6.0)                                               # frame 1: from the doorway
S1 = (F1, P(CX, 0.30, 1.40, 0.0, -9.0))                                         # hero push-in
S2 = (P(CX + 0.26, -0.66, 1.28, -9.0, -12.0), P(CX - 0.24, -0.12, 1.12, 9.0, -17.0))   # drawer pairs (stair / chest)
S3 = (P(1.72, 0.48, 1.14, -38.0, -8.0), P(1.44, 1.02, 0.98, -64.0, -4.0))         # wardrobe under the raised bed (wow)
S4 = (P(CX, 0.38, 2.64, 74.0, -84.0), P(CX, 0.54, 2.42, 106.0, -84.0))  # reverse: both desks
S5 = (P(1.62, 0.25, 1.92, -14.0, -15.0), F1)                                     # partition, lights, back to frame 1
STATIONS = [S1, S2, S3, S4, S5]
HOLDS = [(0.0, 3.00, S1), (3.30, 6.40, S2), (6.70, 9.90, S3), (10.20, 11.90, S4), (12.20, DUR, S5)]
S3B = (P(1.58, 0.75, 1.15, -48.0, -8.0), P(1.45, 1.05, 1.05, -60.0, -6.0))         # long: wardrobe, outside
L1 = (P(0.80, 0.95, 1.28, 42.0, -27.0), P(0.86, 1.22, 1.22, 36.0, -28.0))         # long: under-bed drawers
L2 = (P(0.92, 1.05, 1.48, 46.0, 12.0), P(0.98, 1.30, 1.46, 40.0, 14.0))           # long: overhead flaps
L3 = (P(1.38, 1.55, 2.36, -55.0, -30.0), P(1.30, 1.90, 2.30, -62.0, -30.0))       # long: deck top
L4 = (P(0.80, 1.53, 0.80, 2.0, -4.0), P(0.78, 1.78, 0.80, 0.0, -4.0))             # long: inside the wardrobe
L5 = (P(CX, 0.50, 1.56, 0.0, -10.0), P(CX, 0.86, 1.50, 0.0, -10.0))               # long: the kids
if CUT == 'long' and not REST:
    DUR = 40.0
    HOLDS = [(0.0, 3.00, S1), (3.30, 6.00, S4), (6.30, 9.60, S2), (9.90, 12.90, L1), (13.20, 16.00, L2), (16.30, 19.40, L3),
             (19.70, 22.60, S3), (22.90, 26.60, S3B), (26.90, 31.00, L4), (31.30, 34.00, L5), (34.30, DUR, S5)]
camera = hold_camera(HOLDS, VFOV, rest=REST)


# ------------------------------------------------------------------------------------------- lights (fixed slots)
LSKY = (11.0, 11.6, 12.6)
LSUN = (64000.0, 58000.0, 48000.0)
LDOOR = (2.2, 2.2, 2.15)
LFILL = (0.55, 0.55, 0.54)
LLED = (40.0, 36.0, 29.0)
LWR = (34.0, 30.0, 23.0)
LRL = (900.0, 800.0, 640.0)
LLAMP = (80.0, 64.0, 42.0)
LDOWN = (760.0, 720.0, 650.0)


def lights(mats4, vis):
    off = (0.0, 0.0, 0.0)
    night = bool(vis.get('bd_night'))

    def k(L, on, f=1.0):
        return tuple(v * f for v in L) if on else off
    Ls = []
    Ls.append(rect_light((WX0, D + 0.16, WZ0), (WX1 - WX0, 0, 0), (0, 0, WZ1 - WZ0), k(LSKY, not night), always=1))   # 0 sky (-y)
    sc = np.array([CX, D, (WZ0 + WZ1) / 2]) - SUN_DIR * 3.0
    Ls.append(spot_rect(tuple(sc), tuple(SUN_DIR), 0.06, k(LSUN, not night), 0.0))                                      # 1 sun
    Ls.append(rect_light((DX0, -0.4, 0.2), (0, 0, 1.9), (DX1 - DX0, 0, 0), k(LDOOR, True, 0.25 if night else 1.0), always=1))  # 2 +y
    Ls.append(rect_light((0.4, 0.3, H - 0.012), (0, D - 0.6, 0), (W - 0.8, 0, 0), k(LFILL, True, 0.45 if night else 1.0)))   # 3 down
    Ls.append(rect_light((DK - 0.035, BY0 + 0.05, DKZ - 0.013), (0, D - BY0 - 0.1, 0), (0.015, 0, 0), k(LLED, vis.get('ledDeck'))))  # 4
    Ls.append(rect_light((OCX0 + 0.02, BY0 + 0.05, OCZ0 - 0.007), (0, D - BY0 - 0.1, 0), (0.025, 0, 0), k(LLED, vis.get('ledOc'))))  # 5
    Ls.append(rect_light((0.70, BY0 + 0.08, DKZ - 0.005), (0, D - BY0 - 0.16, 0), (0.03, 0, 0), k(LWR, vis.get('ledWr'))))         # 6
    Ls.append(spot_rect((0.66, D - 0.07, DKT + 0.56), (0.0, -0.35, -1.0), 0.03, k(LRL, vis.get('rlOnW')), 5.0))                  # 7
    Ls.append(spot_rect((1.94, D - 0.07, 1.10), (0.0, -0.35, -1.0), 0.03, k(LRL, vis.get('rlOnE')), 5.0))                        # 8
    for side, x in (('W', 0.19), ('E', W - 0.19)):                                                                              # 9-10
        Ls.append(sphere_light((x, 0.54, 0.99), 0.018, k(LLAMP, vis.get(f'lampOn{side}'))))
    for (x, y) in DL:                                                                                                           # 11-13
        Ls.append(spot_rect((x, y, H - 0.006), (0, 0, -1), 0.05, k(LDOWN, vis.get('dlOn')), 4.0))
    return Ls


BLENDER = dict(
    exposure=-0.30,
    look='AgX - Medium High Contrast',
    separate=['backdrop', 'backdrop_night'],
    fill_lights=[2, 3],
    wood_scale=(55.0, 1.6),
    bake_rect={'backdrop': (-6.0, 8.0, -3.0, 6.0), 'backdrop_night': (-6.0, 8.0, -3.0, 6.0)},
    bake_px={'backdrop': 0.006, 'backdrop_night': 0.004, 'floor': 0.0015},
)


# ------------------------------------------------------------------------------------------- timeline
def timeline():
    tl = Timeline(rk, FPS)
    I = np.eye(4)
    hidden = lambda t: (I, False)
    if REST:
        return rest_timeline(tl, hidden)
    return Story(tl).short() if CUT != 'long' else Story(tl).long()


def rest_timeline(tl, hidden):
    I = np.eye(4)
    if REST_NIGHT:
        tl.custom('bd_day', hidden)
    else:
        for nm in ('bd_night', 'ledDeck', 'ledOc', 'ledWr', 'rlOnW', 'rlOnE', 'dlOn', 'lampOnW', 'lampOnE'):
            tl.custom(nm, hidden)
    kids = KID_A.pieces + KID_B.pieces
    if not REST_SPLIT:
        for nm in kids:
            tl.custom(nm, hidden)
    else:
        for k, dy in enumerate((-(D - PL - BY0), -(D - PL - BY0) / 2, 0.0)):
            tl.custom(f'pt{k}', lambda t, dy=dy: (T(0, dy, 0), True))
        KID_A.animate(tl, pose=Story(tl).kids_final(0, 0, False)(0), at=(0.46, 2.45, 180), seat=DKT + 0.16)
    if REST_OPEN:
        tl.custom('wdoor1', lambda t: (T(0, 0.92, 0), True))
        for k in range(4):
            tl.custom(f'sdW{k}', lambda t: (T(0, -0.28, 0), True))
            tl.custom(f'sdWc{k}', lambda t: (T(0, -0.28, 0), True))
        for nm in ('tkE', 'tkEc'):
            tl.custom(nm, lambda t: (T(0, -0.30, 0), True))
        for k in range(3):
            tl.custom(f'cdE{k}', lambda t: (T(0, -0.28, 0), True)); tl.custom(f'cdEc{k}', lambda t: (T(0, -0.28, 0), True))
        for k in range(2):
            tl.custom(f'ubE{k}', lambda t: (T(-0.55, 0, 0), True)); tl.custom(f'ubEc{k}', lambda t: (T(-0.55, 0, 0), True))
        for s, sg in (('W', 1), ('E', -1)):
            tl.custom(f'ddr{s}', lambda t, sg=sg: (T(sg * 0.28, 0, 0), True)); tl.custom(f'ddc{s}', lambda t, sg=sg: (T(sg * 0.28, 0, 0), True))
    else:
        for nm in ('ledWr',):
            tl.custom(nm, hidden)
    return tl


class Story:
    """Grouped animation beats. Each beat takes its start time, so the short and long cuts share the same moves."""

    def __init__(self, tl):
        self.tl = tl
        self.I = np.eye(4)
        self.used = set()

    # ---------------------------------------------------------------- primitives
    def appear(self, name, t_on, t_off=None):
        self.tl.custom(name, lambda t: (self.I, t >= t_on and (t_off is None or t < t_off)))

    def door(self, name, hinge, a_open, t_in, t_in1, t_close, dur=0.17, axis='z', sound=True):
        """Pops in already open and swings shut."""
        I, hinge = self.I, np.array(hinge, float)

        def f(t):
            if t < t_in:
                return I, False
            if t < t_in1:
                u = (t - t_in) / (t_in1 - t_in)
                s = 1.12 - 0.12 * eoc(u)
                return T(0, 0, 0.10 * (1 - eoc(u))) @ about(hinge, R(axis, a_open) @ S(s, s, s)), True
            if t < t_close:
                return about(hinge, R(axis, a_open)), True
            u = (t - t_close) / dur
            if u < 1:
                return about(hinge, R(axis, a_open * (1 - u * u))), True
            tau = t - t_close - dur
            a = math.copysign(math.radians(2.0), a_open) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))
            return about(hinge, R(axis, a)), True
        self.tl.custom(name, f)
        if sound:
            self.tl.ev(t_in1, name, 0.3, 'tick')
        self.tl.ev(t_close + dur, name + '_shut', 0.75, 'thud')

    def flap(self, name, hinge, a_open, t_vis, t_open, t_close, dur=0.2, axis='y'):
        """Already in place (visible from t_vis); swings open at t_open, slams at t_close."""
        I, hinge = self.I, np.array(hinge, float)

        def f(t):
            if t < t_vis:
                return I, False
            if t < t_open:
                return I, True
            if t < t_close:
                return about(hinge, R(axis, a_open * eob(c01((t - t_open) / 0.3), 1.2))), True
            u = (t - t_close) / dur
            if u < 1:
                return about(hinge, R(axis, a_open * (1 - u * u))), True
            tau = t - t_close - dur
            a = math.copysign(math.radians(1.5), a_open) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))
            return about(hinge, R(axis, a)), True
        self.tl.custom(name, f)
        self.tl.ev(t_open + 0.1, name + '_open', 0.45, 'swish')
        self.tl.ev(t_close + dur, name + '_shut', 0.75, 'thud')

    def drawer_fn(self, t_appear, t_open, t_close, off, base=None, out=0.16, shut=0.17):
        I, off = self.I, np.array(off, float)

        def f(t):
            if t < t_appear:
                return I, False
            if base is not None:
                B, bv = base(t)
                if not bv:
                    return I, False
            else:
                B = I
            if t < t_open:
                return B, True
            if t < t_close:
                return B @ T(*(off * eob((t - t_open) / out, 1.6))), True
            kk = 1 - smooth((t - t_close) / shut)
            tau = t - t_close - shut
            wob = 0.006 * math.exp(-tau / 0.05) * math.sin(2 * math.pi * tau / 0.12) if tau > 0 else 0.0
            return B @ T(*(off * kk + off / (np.linalg.norm(off) + 1e-9) * wob)), True
        return f

    def drawer_beat(self, name, t_vis, t_open, t_close, off, contents=None, t_fill=None, base=None, strength=0.8):
        f = self.drawer_fn(t_vis, t_open, t_close, off, base=base)
        self.tl.custom(name, f)
        self.tl.ev(t_open + 0.08, name + '_open', 0.45, 'swish')
        self.tl.ev(t_close + 0.17, name + '_shut', strength, 'thud')
        if contents:
            tf = t_fill if t_fill is not None else t_open + 0.18
            self.tl.drop(contents, tf, tf + 0.16, 0.22, 0.05, 0.4, 'tick', parent=f)
        return f

    def static_after(self, name, t_vis, base=None):
        self.tl.custom(name, lambda t: ((base(t)[0] if base else self.I), t >= t_vis))

    def hide(self, *names):
        for nm in names:
            self.tl.custom(nm, lambda t: (self.I, False))

    # ---------------------------------------------------------------- beats
    def build_beat(self, t0):
        """The empty room fills: floor pairs, both bed structures, stair + chest, rails + cabinets, mattresses, bedding."""
        tl, drop, slide, grow = self.tl, self.tl.drop, self.tl.slide, self.tl.grow
        for k in range(6):
            t1 = t0 + 0.22 + 0.07 * k
            drop(f'floorW{k}', t1 - 0.16, t1, 0.24, 0.05, 0.3 + 0.03 * k, 'tick')
            drop(f'floorE{k}', t1 - 0.16, t1, 0.24, 0.05, 0.0, 'none')
        grow('deckW', t0 + 0.62, t0 + 0.90, 'z', (0, 0, 0), 1.0)
        drop('bedE', t0 + 0.70, t0 + 0.90, 0.6, 0.03, 0.0, 'none')
        for k in range(2):
            self.tl.slide(f'ubE{k}', t0 + 1.02 + 0.06 * k, t0 + 1.18 + 0.06 * k, (-0.5, 0, 0), 1.0, 0.0 if k else 0.5, 'none' if k else 'thud')
        slide('wdoor1', t0 + 1.02, t0 + 1.18, (0.5, 0, 0), 1.0, 0.0, 'none')
        slide('wdoor2', t0 + 1.08, t0 + 1.24, (0.5, 0, 0), 1.0, 0.0, 'none')
        self.hide_until('ubEc0', 99); self.hide_until('ubEc1', 99)
        # stair columns (rise to the wall) and the chest + drawers, in mirrored pairs
        for k in range(4):
            tt = t0 + 1.36 + 0.10 * k
            drop(f'stW{k}', tt - 0.14, tt, 0.35, 0.03, 0.55, 'thud')
            self.static_after(f'sdW{k}', tt - 0.14, base=tl.anims[f'stW{k}'])
        drop('chE', t0 + 1.22, t0 + 1.36, 0.35, 0.03, 0.0, 'none')
        self.static_after('tkE', t0 + 1.22, base=tl.anims['chE'])
        for k in range(3):
            slide(f'cdE{k}', t0 + 1.32 + 0.10 * k, t0 + 1.46 + 0.10 * k, (0, -0.4, 0), 1.0, 0.0, 'none')
        slide('railW', t0 + 1.82, t0 + 1.98, (0.45, 0, 0), 1.0, 0.6)
        slide('ocE', t0 + 1.82, t0 + 1.98, (0.5, 0, 0), 1.0, 0.0, 'none')
        for nm in ('flE1', 'flE2'):
            slide(nm, t0 + 1.88, t0 + 2.04, (0.5, 0, 0), 1.0, 0.0, 'none')
        drop('matW', t0 + 1.98, t0 + 2.14, 0.4, 0.05, 0.7, 'thud')
        drop('matE', t0 + 1.98, t0 + 2.14, 0.4, 0.05, 0.0, 'none')
        drop('ptTrack', t0 + 2.12, t0 + 2.24, 0.15, 0.02, 0.35)
        drop('duvetW', t0 + 2.30, t0 + 2.48, 0.35, 0.03, 0.6, 'thud')
        drop('duvetE', t0 + 2.30, t0 + 2.48, 0.35, 0.03, 0.0, 'none')
        for i, (a, b) in enumerate((('pilW1', 'pilE1'), ('pilW2', 'pilE2'), ('pilW3', 'pilE3'))):
            tt = t0 + 2.62 + 0.10 * i
            drop(a, tt - 0.16, tt, 0.35, 0.08, 0.35)
            drop(b, tt - 0.16, tt, 0.35, 0.08, 0.0, 'none')
        slide('rlW', t0 + 2.86, t0 + 3.0, (0, -0.2, 0), 1.0, 0.4, 'tick')
        slide('rlE', t0 + 2.86, t0 + 3.0, (0, -0.2, 0), 1.0, 0.0, 'none')
        grow('rug', t0 + 3.05, t0 + 3.30, 'y', (0, 1.85, 0), 0.4)
        drop('chTop', t0 + 3.10, t0 + 3.26, 0.25, 0.05, 0.3)
        for k in range(4):
            self.static_after(f'ocBox{k}', t0 + 1.98)

    def hide_until(self, name, t_on):
        self.tl.custom(name, lambda t: (self.I, t >= t_on))

    def pairs_beat(self, t0, step=0.70):
        """Stair drawer k and chest drawer k open, fill and shut at the same instant (toe-kick first)."""
        tl = self.tl
        chest = [('tkE', 'tkEc', (0, -0.32, 0))] + [(f'cdE{k}', f'cdEc{k}', (0, -0.30, 0)) for k in range(3)]
        for k in range(4):
            to = t0 + step * k
            tc = to + step - 0.12
            fW = self.drawer_beat(f'sdW{k}', 0.0, to, tc, (0, -0.30, 0), f'sdWc{k}', base=tl.anims[f'stW{k}'])
            dn, cn, off = chest[k]
            base = tl.anims['chE'] if k == 0 else None
            vis = 0.0 if k == 0 else tl.anims[dn]
            if k == 0:
                f = self.drawer_fn(0.0, to, tc, off, base=base)
            else:
                f0 = tl.anims[dn]
                f = self.drawer_fn(0.0, to, tc, off, base=f0)
            tl.custom(dn, f)
            tl.drop(cn, to + 0.18, to + 0.34, 0.22, 0.05, 0.0, 'none', parent=f)
        self.used |= {'pairs'}

    def wardrobe_beat(self, t0, t_close, gap=0.055, late=None, late_gap=0.14):
        """Sliding slatted door opens, LED on, rail, garments one by one, shoes, stacks, boxes; the door slams."""
        tl = self.tl
        d1 = tl.anims['wdoor1']

        def door(t):
            M, v = d1(t)
            if t < t0:
                return M, v
            if t < t_close:
                return T(0, 0.92 * eob(c01((t - t0) / 0.30), 0.6), 0), True
            u = c01((t - t_close) / 0.22)
            tau = t - t_close - 0.22
            wob = 0.008 * math.exp(-tau / 0.05) * math.sin(2 * math.pi * tau / 0.12) if tau > 0 else 0.0
            return T(0, 0.92 * (1 - smooth(u)) - wob, 0), True
        tl.custom('wdoor1', door)
        tl.ev(t0 + 0.1, 'wdoor_open', 0.5, 'swish'); tl.ev(t_close + 0.22, 'wdoor_shut', 0.9, 'thud')
        self.appear('ledWr', t0 + 0.32); tl.ev(t0 + 0.32, 'ledWr', 0.6, 'chime')
        tl.drop('wrRail', t0 + 0.40, t0 + 0.54, 0.2, 0.03, 0.45)
        every = 2 if gap < 0.1 else 1
        for k in range(14):
            tt = t0 + 0.62 + gap * k
            on = k % every == 0
            tl.fly(f'gW{k}', tt - 0.16, tt, (0.0, -0.45, 0.03), 0.02, 0.32 if on else 0.0, 'tick' if on else 'none')
        tz = late if late is not None else t0 + 0.62 + gap * 14 + 0.10
        for i, (nm, kind) in enumerate((('wrShoes', 'drop'), ('wrShelf', 'fly'), ('wrStack0', 'drop'), ('wrStack1', 'drop'),
                                        ('wrBoxes', 'drop'))):
            ta = tz + late_gap * i
            if kind == 'fly':
                tl.fly(nm, ta, ta + 0.14, (0.4, 0, 0), 0.03, 0.4)
            else:
                tl.drop(nm, ta, ta + 0.14, 0.28, 0.04, 0.45)

    def climb_beat(self, kid, t0, dt=0.30, end=None):
        """Child A pops in by the aisle and climbs the stair drawers to the deck."""
        pts = [(DK - SW * (k + 0.5), 1.23, RZ * (k + 1)) for k in range(4)]
        times = [t0 + 0.25 + dt * i for i in range(len(pts))]
        up = fg.lerp_pose('stand', 'step_up', 0.85)

        def seg(t):
            for i in range(len(times) - 1):
                if t < times[i + 1]:
                    return i, c01((t - times[i]) / (times[i + 1] - times[i]))
            return len(times) - 2, 1.0

        def at_fn(t):
            if t < times[0]:
                x, y, _ = pts[0]
                return (x, y, -90)
            i, u = seg(t)
            a, b = pts[i], pts[i + 1]
            s = smooth(u)
            return (a[0] + (b[0] - a[0]) * s, a[1] + (b[1] - a[1]) * s, -90)

        def floor_fn(t):
            if t < times[0]:
                return pts[0][2]
            i, u = seg(t)
            a, b = pts[i], pts[i + 1]
            return a[2] + (b[2] - a[2]) * smooth(c01((u - 0.25) / 0.45))

        def pose_fn(t):
            if t < times[0]:
                return fg.pose_of('stand')
            i, u = seg(t)
            if u >= 1.0:
                return fg.lerp_pose('stand', 'reach_up', 0.0)
            p = up if i % 2 == 0 else fg.mirror(up)
            return fg.lerp_pose('stand', p, math.sin(math.pi * u))
        vis = (lambda t: t < end) if end is not None else True
        kid.animate(self.tl, pose=pose_fn, at=at_fn, floor=floor_fn, pop=t0, visible=vis)
        for i in range(1, len(times)):
            self.tl.ev(times[i] - 0.05, f'kid_step{i}', 0.25, 'tick')

    def desks_beat(self, t0):
        tl = self.tl
        for s, sg in (('W', 1), ('E', -1)):
            snd = (lambda st, kd: (st, kd)) if s == 'W' else (lambda st, kd: (0.0, 'none'))
            st, kd = snd(0.75, 'thud')
            dsk = tl.slide(f'desk{s}', t0, t0 + 0.18, (-sg * 0.6, 0, 0), 1.0, st, kd)
            self.static_after(f'ddr{s}', t0, base=dsk)
            for k in range(2):
                st, kd = snd(0.4, 'tick')
                tl.slide(f'sh{s}{k}', t0 + 0.22 + 0.10 * k, t0 + 0.36 + 0.10 * k, (-sg * 0.3, 0, 0), 1.0, st, kd)
            cam = np.array(S4[0]['pos'])
            for k in range(2):
                st, kd = snd(0.35, 'tick')
                tl.from_camera(f'bk{s}{k}', t0 + 0.46 + 0.12 * k, t0 + 0.62 + 0.12 * k, cam, 0.3, st, kd)
            st, kd = snd(0.35, 'tick')
            tl.drop(f'lamp{s}', t0 + 0.72, t0 + 0.86, 0.3, 0.05, st, kd)
            tl.drop(f'mug{s}', t0 + 0.80, t0 + 0.94, 0.25, 0.05, 0.0, 'none')
            ch_c = tl.cen[f'chair{s}']

            def chair(t, ta=t0 + 0.86, tb=t0 + 1.12, sg=sg, ch_c=ch_c):
                if t < ta:
                    return self.I, False
                u = (t - ta) / (tb - ta)
                if u < 1:
                    off = np.array([sg * 0.5 * (1 - eoc(u)), -0.1 * (1 - eoc(u)), 0])
                    ang = sg * math.radians(70) * (1 - eob(u, 1.2))
                else:
                    off = np.zeros(3)
                    ang = math.radians(4) * math.exp(-(t - tb) / 0.12) * math.sin(2 * math.pi * (t - tb) / 0.3)
                return T(*off) @ about(ch_c, R('z', ang)), True
            tl.custom(f'chair{s}', chair)
            if s == 'W':
                tl.ev(t0 + 1.12, 'chairs', 0.6, 'thud')
            f = self.drawer_fn(t0, t0 + 1.20, t0 + 1.62, (sg * 0.28, 0, 0), base=dsk)
            tl.custom(f'ddr{s}', f)
            tl.drop(f'ddc{s}', t0 + 1.34, t0 + 1.48, 0.2, 0.04, 0.4 if s == 'W' else 0.0, 'tick' if s == 'W' else 'none', parent=f)
        tl.ev(t0 + 1.28, 'ddr_open', 0.45, 'swish'); tl.ev(t0 + 1.79, 'ddr_shut', 0.8, 'thud')

    def final_beat(self, t0, long=False):
        """Partition telescopes out, the kids, dusk, the lights cascade."""
        tl = self.tl
        for k in range(3):
            tl.drop(f'pt{k}', t0 - 0.30 + 0.05 * k, t0 - 0.14 + 0.05 * k, 0.9, 0.02, 0.5 if k == 0 else 0.0, 'thud' if k == 0 else 'none')
        for k, (dy, ts) in enumerate(((-(D - PL - BY0), 0.0), (-(D - PL - BY0) / 2, 0.08))):
            base = tl.anims[f'pt{k}']

            def f(t, dy=dy, ts=ts, base=base):
                M, v = base(t)
                if t < t0 + ts:
                    return M, v
                u = c01((t - t0 - ts) / 0.42)
                return T(0, dy * eob(u, 0.5), 0), True
            tl.custom(f'pt{k}', f)
        tl.ev(t0 + 0.10, 'pt_slide', 0.4, 'swish')
        tl.ev(t0 + 0.47, 'pt_clack1', 0.7, 'thud'); tl.ev(t0 + 0.54, 'pt_clack2', 0.6, 'thud')
        tn = t0 + 0.75
        self.appear('bd_day', -1.0, tn); self.appear('bd_night', tn)
        tl.ev(tn, 'night', 0.5, 'swish')
        if not long:
            cas = (('ledDeck', 0.18, 0.7), ('ledOc', 0.26, 0.5), ('rlOnW', 0.36, 0.6), ('rlOnE', 0.36, 0.0), ('lampOnW', 0.46, 0.4),
                   ('lampOnE', 0.46, 0.0), ('dlOn', 0.56, 0.6))
        else:
            cas = (('ledDeck', 0.20, 0.7), ('ledOc', 0.40, 0.5), ('rlOnW', 0.60, 0.6), ('rlOnE', 0.80, 0.6), ('fairyOn', 1.00, 0.6),
                   ('lampOnW', 1.15, 0.0), ('lampOnE', 1.15, 0.0), ('dlOn', 1.25, 0.7))
        for nm, dt, st in cas:
            self.appear(nm, tn + dt)
            if st:
                tl.ev(tn + dt, nm, st, 'chime')

    def kids_final(self, t_pop_a, t_pop_b, wave=True):
        wv = dict(fg.pose_of('wave'), hip_l=90, hip_r=90, knee_l=4, knee_r=4, ankle_l=10, ankle_r=10, spine=4, sh_l=30, elbow_l=30)

        def pose_a(t):
            if not wave:
                return wv
            p = dict(wv)
            p['elbow_r'] = 105 + 22 * math.sin(2 * math.pi * 1.6 * (t - t_pop_a))
            return p
        return pose_a

    def kids_on_beds(self, t_b, t_a):
        """B pops onto the low bed; A (the same figure that climbed) pops sitting on the deck, waving."""
        tl = self.tl
        KID_B.animate(tl, pop=t_b, visible=True)
        climb = {nm: tl.anims[nm] for nm in KID_A.pieces}
        KID_A.animate(tl, pose=self.kids_final(t_a, t_a), at=(0.46, 2.45, 180), seat=DKT + 0.16, pop=t_a)
        deck = {nm: tl.anims[nm] for nm in KID_A.pieces}
        for nm in KID_A.pieces:
            tl.custom(nm, lambda t, nm=nm: deck[nm](t) if t >= t_a else climb[nm](t))

    def underbed_beat(self, t0):
        tl = self.tl
        for k in range(2):
            to = t0 + 0.95 * k
            base = tl.anims[f'ubE{k}']
            f = self.drawer_fn(0.0, to, to + 0.80, (-0.55, 0, 0), base=base)
            tl.custom(f'ubE{k}', f)
            tl.ev(to + 0.08, f'ubE{k}_open', 0.5, 'swish'); tl.ev(to + 0.97, f'ubE{k}_shut', 0.85, 'thud')
            tl.drop(f'ubEc{k}', to + 0.22, to + 0.40, 0.3, 0.05, 0.5, 'tick', parent=f)

    def flaps_beat(self, t0):
        tl = self.tl
        for k, nm in enumerate(('flE1', 'flE2')):
            to = t0 + 1.05 * k
            base = tl.anims[nm]
            hinge = (OCX0 - 0.018, 0, OCZ1)
            fl = self.flap_on(nm, base, hinge, math.radians(80), to, to + 0.85)
            for j in range(2):
                b = 2 * k + j
                tl.fly(f'ocBox{b}', to + 0.28 + 0.13 * j, to + 0.46 + 0.13 * j, (-0.6, 0, 0.05), 0.04, 0.35, 'tick')

    def flap_on(self, name, base, hinge, a_open, t_open, t_close, dur=0.2):
        tl, hinge = self.tl, np.array(hinge, float)

        def f(t):
            M, v = base(t)
            if t < t_open:
                return M, v
            if t < t_close:
                return about(hinge, R('y', a_open * eob(c01((t - t_open) / 0.3), 1.2))), True
            u = (t - t_close) / dur
            if u < 1:
                return about(hinge, R('y', a_open * (1 - u * u))), True
            tau = t - t_close - dur
            return about(hinge, R('y', math.radians(1.5) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08)))), True
        tl.custom(name, f)
        tl.ev(t_open + 0.1, name + '_open', 0.45, 'swish'); tl.ev(t_close + dur, name + '_shut', 0.8, 'thud')
        return f

    def deck_beat(self, t0):
        tl = self.tl
        tl.slide('dkShelf', t0, t0 + 0.16, (0, -0.3, 0), 1.0, 0.5, 'thud')
        tl.from_camera('dkBooks', t0 + 0.24, t0 + 0.42, np.array(L3[0]['pos']), 0.3, 0.4, 'tick')
        tl.drop('dkPlush', t0 + 0.55, t0 + 0.72, 0.3, 0.1, 0.4)
        tl.drop('fairy', t0 + 0.85, t0 + 1.02, 0.25, 0.04, 0.35)
        self.appear('fairyOn', 99)
        tl.grow('throwW', t0 + 1.15, t0 + 1.40, 'x', (0.0, 0, 0), 0.45)
        for i, nm in enumerate(('pilW2', 'pilW3')):
            base = tl.anims[nm]
            ta = t0 + 1.6 + 0.25 * i

            def hop(t, base=base, ta=ta, nm=nm):
                M, v = base(t)
                if t < ta:
                    return M, v
                tau = t - ta
                z = 0.12 * math.exp(-tau / 0.12) * abs(math.sin(math.pi * tau / 0.22))
                return T(0, 0, z) @ M, v
            tl.custom(nm, hop)
            tl.ev(ta + 0.22, nm + '_hop', 0.25, 'tick')

    # ---------------------------------------------------------------- cuts
    def short(self):
        self.build_beat(0.0)
        self.pairs_beat(3.50)
        self.wardrobe_beat(6.80, 9.30)
        self.climb_beat(KID_A, 8.85, dt=0.27, end=10.05)
        self.desks_beat(10.25)
        self.final_beat(12.25)
        self.kids_on_beds(12.35, 12.45)
        self.appear('ledWr', 7.12, 9.52)
        self.hide('ubEc0', 'ubEc1', *LONG_ONLY)
        return self.tl

    def long(self):
        tl = self.tl
        self.build_beat(0.0)
        self.desks_beat(3.45)
        self.pairs_beat(6.45, step=0.75)
        self.underbed_beat(10.10)
        self.flaps_beat(13.40)
        self.deck_beat(16.50)
        self.climb_beat(KID_A, 19.85, dt=0.32, end=22.65)
        self.wardrobe_beat(23.05, 30.40, gap=0.12, late=27.10, late_gap=0.32)
        self.kids_on_beds(31.45, 31.80)
        tl.drop('rugToys', 32.25, 32.42, 0.3, 0.06, 0.4)
        self.final_beat(34.55, long=True)
        self.appear('ledWr', 23.37, 30.62)
        return tl


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    timeline().export(DUR, camera, lights, out)
