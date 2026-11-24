"""9 m² bedroom with a sofa and a desk: a made double bed docks on the ceiling and glides 2.06 m down onto the sofa.
Warm white shell + light oak + muted blue-grey accent (sofa and wall pads), brushed steel guide posts. No on-screen text.

    ROOM_REST=1 python3 ../../pipeline/run.py project.py <workdir> probe 0.5,1.5,2.5,3.5      # finished room, camera stations
    python3 ../../pipeline/run.py project.py <workdir> preview                                  # code-renderer preview with music
    /root/bpyenv/bin/python ../../pipeline/blender_render.py project.py <outdir> --size 720x1280 ...
    ROOM_CUT=long selects the 49.5 s long cut (same build(), its own timeline and camera).

Units: metres. x = east, y = north, z = up. Room x 0..W, y 0..D, z 0..H.
West wall: bed bay (sofa under the parked bed, two book towers, four steel guide posts, ceiling rail).
North wall: window + desk + bedside alcove. East wall: sliding wardrobe. South wall: door at the east end, peg hooks.
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
from camkit import lerp_cam
import figure as fg

REST = os.environ.get('ROOM_REST') == '1'
LONG = os.environ.get('ROOM_CUT') == 'long'

W, D, H = 3.0, 3.0, 2.85
FPS = 25
DUR = 6.0 if REST else (49.5 if LONG else 15.0)

WX0, WX1, WZ0, WZ1 = 1.80, 2.80, 0.95, 2.25        # north window opening
DOOR = (2.15, 2.85, 2.05)                           # south door x0, x1, height
# bed (built parked under the ceiling: underside at Z_UP); BED_DROP = travel down onto the sofa
BX0, BX1, BY0, BY1 = 0.08, 1.48, 0.50, 2.50
Z_UP = 2.50
BED_DROP = 2.06                                     # underside 0.44 when down, 2 cm over the sofa cushions (0.42)
POSTS = [(0.30, 0.46), (1.51, 0.46), (0.30, 2.54), (1.51, 2.54)]      # back-south, front-south, back-north, front-north
PR = 0.0325                                          # 65 mm posts
TWS = (0.0, 0.40, 0.0, 0.42)                         # south-west tower x0, x1, y0, y1
TWN = (0.0, 0.40, 2.58, 3.0)                         # north-west tower
SOFA = (0.06, 0.81, 0.50, 2.50)                      # sofa x0, x1, y0, y1 (seat 0.42)
DESK = (1.60, 3.00, 2.45, 0.75)                      # desk x0, x1, front y, top z
WR = (2.40, 3.00, 0.90, 2.30)                        # wardrobe x0, x1, y0, y1
WRM = 1.60                                           # wardrobe divider (south section y0..WRM: hanging)
SUN_DIR = np.array([-0.42, -0.72, -0.56]) / np.linalg.norm([-0.42, -0.72, -0.56])
DL = [(0.45, 0.85), (1.15, 0.85), (0.45, 2.15), (1.15, 2.15)]        # downlights under the bed
CAPTIONS = []                                        # no on-screen text


# ------------------------------------------------------------------------------------------- materials
def materials():
    mat('subfloor', tex=3, col=srgb(128, 128, 131), p=(0.08,))
    mat('floor', tex=1, col=srgb(210, 180, 142), col2=srgb(190, 158, 120), rough=0.38, f0=0.04, glossy=True, p=(0.18, 1.6))
    mat('wall', tex=3, col=srgb(242, 241, 238), p=(0.02,))
    mat('ceiling', col=srgb(247, 246, 243))
    mat('white_cab', col=srgb(243, 242, 239), rough=0.45)
    mat('white_in', col=srgb(237, 236, 233))
    mat('plinth', col=srgb(214, 210, 202))
    wood_mats('oak', srgb(212, 178, 136), seed=3.0)
    wood_mats('birch', srgb(228, 208, 176), seed=8.0)
    mat('steel', tex=14, col=srgb(196, 199, 203), rough=0.28, metal=1, p=(2,))
    mat('steel_h', tex=14, col=srgb(196, 199, 203), rough=0.28, metal=1, p=(0,))
    mat('steel_d', col=srgb(120, 124, 130), rough=0.35, metal=1)
    mat('blackm', col=srgb(30, 30, 32), rough=0.4, f0=0.04, glossy=True)
    mat('winframe', col=srgb(238, 238, 236), rough=0.4)
    mat('sill', col=srgb(240, 238, 233), rough=0.25, f0=0.04, glossy=True)
    mat('mirror', col=srgb(236, 237, 239), rough=0.22, metal=1)
    mat('linen', tex=3, col=srgb(244, 242, 238), rough=0.9, p=(0.04,))
    mat('blind', tex=4, col=srgb(236, 230, 218), emis=(0.05, 0.05, 0.048), p=(0.12,))
    mat('mattress', tex=5, col=srgb(246, 245, 241), p=(0, 0.02))
    mat('pil_white', tex=3, col=srgb(246, 244, 240), rough=0.9, p=(0.04,))
    mat('pil_mustard', tex=6, col=srgb(208, 162, 66))
    mat('pil_paleblue', tex=3, col=srgb(184, 198, 210), rough=0.9, p=(0.05,))
    mat('throw', tex=5, col=srgb(198, 128, 100), p=(0, 0.012))
    mat('throw2', tex=5, col=srgb(214, 200, 176), p=(0, 0.012))
    mat('sofa', tex=6, col=srgb(124, 142, 158))
    mat('sofa_pad', tex=6, col=srgb(132, 150, 166))
    mat('strap', col=srgb(214, 214, 210), rough=0.7)
    mat('buckle', col=srgb(200, 202, 206), rough=0.25, metal=1)
    mat('sensor', col=srgb(40, 42, 46), rough=0.3, f0=0.04, glossy=True)
    mat('button', col=srgb(242, 242, 240), rough=0.3, f0=0.04, glossy=True)
    mat('alu', col=srgb(200, 202, 206), rough=0.3, metal=1)
    mat('kb', tex=10, col=srgb(56, 56, 60), p=(0.018,))
    mat('lscreen', col=(0, 0, 0), emis=(0.45, 0.58, 0.80))
    mat('ceramic', col=srgb(243, 241, 236), rough=0.22, f0=0.04, glossy=True)
    mat('ceramic_s', col=srgb(170, 186, 168), rough=0.25, f0=0.04, glossy=True)
    mat('terra', col=srgb(196, 124, 90))
    mat('leaf', col=srgb(66, 112, 60)); mat('leaf2', col=srgb(96, 142, 74))
    mat('chair_fab', tex=6, col=srgb(226, 220, 208))
    mat('bulb', col=(0, 0, 0), emis=(9.0, 7.8, 6.0))
    mat('led', col=(0, 0, 0), emis=(7.5, 6.9, 5.6))
    mat('led_off', col=srgb(232, 230, 226))
    mat('dl_emis', col=(0, 0, 0), emis=(8.5, 7.8, 6.6))
    mat('shade', tex=3, col=srgb(240, 234, 222), emis=(0.0, 0.0, 0.0), rough=0.9, p=(0.03,))
    mat('phone', col=srgb(22, 22, 24), rough=0.08, f0=0.05, glossy=True)
    mat('backdrop', tex=9, emis=(1.35, 1.35, 1.35), p=(1.0, 0.0))
    mat('rug', tex=6, col=srgb(228, 220, 204))
    for nm, c in (('cl_white', (242, 242, 240)), ('cl_rust', (166, 104, 80)), ('cl_denim', (90, 114, 150)), ('cl_sage', (150, 166, 142)),
                  ('cl_camel', (192, 152, 110)), ('cl_cream', (234, 226, 210)), ('cl_grey', (156, 156, 160)), ('cl_navy', (60, 72, 104)),
                  ('cl_mustard', (206, 162, 70))):
        mat(nm, tex=5, col=srgb(*c), p=(2, 0.008))
    for nm, c in (('bk_mustard', (212, 166, 64)), ('bk_ochre', (196, 136, 66)), ('bk_sage', (150, 170, 142)), ('bk_slate', (98, 118, 146)),
                  ('bk_cream', (234, 224, 204)), ('bk_white', (242, 240, 234)), ('bk_terra', (190, 112, 82))):
        mat(nm, col=srgb(*c), rough=0.6)
    for nm, c in (('gm_sage', (160, 178, 150)), ('gm_terra', (200, 122, 92)), ('gm_slate', (110, 130, 156)), ('gm_mustard', (220, 176, 80)),
                  ('gm_cream', (236, 228, 210))):
        mat(nm, col=srgb(*c), rough=0.5)
    mat('shoe_white', col=srgb(242, 242, 238), rough=0.5); mat('shoe_tan', col=srgb(176, 128, 86), rough=0.4, f0=0.04, glossy=True)
    mat('board', col=srgb(212, 214, 216))


# ------------------------------------------------------------------------------------------- helpers
def disc(inst, c, r, z0, z1, m, n=28):
    add(inst, lathe(rprof(r, z0, z1, min(0.004, (z1 - z0) * 0.45), 3), n, c), m)


def garment(inst, x, y, z_top, length, width, m, along='y'):
    """Hanging garment on a rail running along `along`: hanger, rounded shoulders and a softly flared body."""
    c = np.array([x, y, z_top])
    if along == 'y':                     # rail along y: the garment's width runs along x
        Rm = np.eye(4)
    else:
        Rm = R('z', math.pi / 2)
    hook = [(-width * 0.42, 0, -0.05), (0, 0, 0), (width * 0.42, 0, -0.05)]
    add(inst, xform(tube(hook, 0.004, 6), T(*c) @ Rm), 'steel_d')
    add(inst, xform(ellipsoid((0, 0, -0.085), (width * 0.48, 0.045, 0.05), 12), T(*c) @ Rm), m)
    nu, nv = 9, 8
    V = np.zeros((nu, nv, 3))
    for i, u in enumerate(np.linspace(0, 1, nu)):
        zz = -0.09 - u * length
        hw = width * (0.47 + 0.06 * u)
        for j, v in enumerate(np.linspace(0, 2 * math.pi, nv)):
            V[i, j] = (hw * math.cos(v), (0.045 - 0.012 * u) * math.sin(v) + 0.006 * math.sin(6 * u + v), zz)
    P_, N_ = grid_tris(V, closed_v=True)
    add(inst, xform((P_, N_), T(*c) @ Rm), m)
    add(inst, xform(ellipsoid((0, 0, -0.09 - length), (width * 0.53, 0.034, 0.012), 10), T(*c) @ Rm), m)


def stack(inst, cx, cy, z0, size, mats_, n, rng):
    z = z0
    for i in range(n):
        sx, sy, sz = size
        jx, jy = rng.uniform(-0.008, 0.008, 2)
        add(inst, rbox((cx + jx, cy + jy, z + sz / 2), (sx * rng.uniform(0.95, 1.0), sy * rng.uniform(0.95, 1.0), sz), sz * 0.45, 3),
            mats_[i % len(mats_)])
        z += sz * 0.96


def plant(inst, cx, cy, z0, r, h, rng, n=9, pot='terra'):
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
        return (0.008 * math.sin(x * 9 + ph[0]) * math.sin(y * 5 + ph[1]) + 0.004 * math.sin(x * 17 + y * 11 + ph[2])
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
        skirt('y', x0, -1, y0 - (r * 0.85 if 's' in sides else 0.0), y1)
    if 'e' in sides:
        skirt('y', x1, +1, y0 - (r * 0.85 if 's' in sides else 0.0), y1)
    if 's' in sides:
        skirt('x', y0, -1, x0 - (r * 0.85 if 'w' in sides else 0.0), x1 + r * 0.85)


def pillow(inst, c, size, tilt, m, yaw=0.0):
    """Puffy pillow: thick in the middle, pinched along the seam. size = (width, thickness, height); tilt about x, then yaw."""
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
        M = T(*c) @ R('z', yaw) @ R('x', tilt)
        add(inst, xform((P, N), M), m)


# ------------------------------------------------------------------------------------------- shell
def build_shell():
    r = 'room'
    add(r, box(-0.2, -0.2, -0.25, W + 0.2, D + 0.2, -0.012), 'subfloor')
    add(r, box(-0.2, -0.2, H, W + 0.2, D + 0.2, H + 0.1), 'ceiling')
    add(r, box(-0.2, -0.2, -0.25, 0, D + 0.2, H + 0.1), 'wall')                                   # west
    add(r, box(W, -0.2, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')                                # east
    # south wall with the door at the east end
    dx0, dx1, dh = DOOR
    add(r, box(-0.2, -0.2, -0.25, dx0, 0, H + 0.1), 'wall'); add(r, box(dx1, -0.2, -0.25, W + 0.2, 0, H + 0.1), 'wall')
    add(r, box(dx0, -0.2, dh, dx1, 0, H + 0.1), 'wall')
    add(r, box(dx0, -0.06, 0, dx1, -0.02, dh), 'white_cab')
    add(r, tube([(dx0 + 0.07, -0.02, 1.02), (dx0 + 0.07, 0.035, 1.02), (dx0 + 0.19, 0.035, 1.02)], 0.009, 10), 'steel')
    for b in (box(dx0 - 0.02, -0.02, 0, dx0, 0.012, dh + 0.02), box(dx1, -0.02, 0, dx1 + 0.02, 0.012, dh + 0.02),
              box(dx0 - 0.02, -0.02, dh, dx1 + 0.02, 0.012, dh + 0.02)):
        add(r, b, 'white_cab')
    # north wall with the window
    add(r, box(-0.2, D, -0.25, WX0, D + 0.2, H + 0.1), 'wall'); add(r, box(WX1, D, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
    add(r, box(WX0, D, -0.25, WX1, D + 0.2, WZ0), 'wall'); add(r, box(WX0, D, WZ1, WX1, D + 0.2, H + 0.1), 'wall')
    for b in (box(WX0, D, WZ0, WX0 + 0.006, D + 0.2, WZ1), box(WX1 - 0.006, D, WZ0, WX1, D + 0.2, WZ1),
              box(WX0, D, WZ1 - 0.006, WX1, D + 0.2, WZ1)):
        add(r, b, 'sill')
    add(r, box(WX0 - 0.03, D - 0.035, WZ0 - 0.02, WX1 + 0.03, D + 0.17, WZ0), 'sill')
    fy0, fy1 = D + 0.10, D + 0.13
    xm = (WX0 + WX1) / 2
    for b in (box(WX0, fy0, WZ0, WX0 + 0.04, fy1, WZ1), box(WX1 - 0.04, fy0, WZ0, WX1, fy1, WZ1), box(WX0, fy0, WZ1 - 0.04, WX1, fy1, WZ1),
              box(WX0, fy0, WZ0, WX1, fy1, WZ0 + 0.04), box(xm - 0.018, fy0, WZ0, xm + 0.018, fy1, WZ1)):
        add(r, b, 'winframe')
    # baseboards (west wall is behind the sofa / towers; north and east)
    for b in (box(0, D - 0.012, 0, W, D, 0.07), box(W - 0.012, 0, 0, W, D, 0.07), box(0, 0, 0, dx0, 0.012, 0.07)):
        add(r, b, 'white_cab')
    add('bd_day', box(-10, D + 4.0, -5, 14, D + 4.05, 9), 'backdrop')
    # floor planks in six bands along x (land west to east: far to near from the frame-1 corner)
    edges = [-0.01, 0.5, 1.0, 1.5, 2.0, 2.5, W + 0.01]
    for k in range(6):
        add(f'floor{k}', box(edges[k], 0, -0.012, edges[k + 1], D, 0.0), 'floor')


# ------------------------------------------------------------------------------------------- bed bay
def build_bay(rng):
    t = 0.018
    # ---- guide posts (grow down from the ceiling), floor + ceiling plates
    for k, (x, y) in enumerate(POSTS):
        p = f'post{k}'
        add(p, tube([(x, y, 0.012), (x, y, H - 0.012)], PR, 20), 'steel')
        add(p, lathe(rprof(0.065, 0.0, 0.012, 0.004, 3), 28, (x, y)), 'steel')
        add(p, lathe(rprof(0.065, H - 0.012, H, 0.004, 3), 28, (x, y)), 'steel')
    # belt slot on the front posts (a thin dark groove facing the room)
    for k in (1, 3):
        x, y = POSTS[k]
        add(f'post{k}', box(x + PR - 0.004, y - 0.006, 0.14, x + PR + 0.0015, y + 0.006, H - 0.14), 'blackm')
    # crank socket on the front-south post, button pad on the front-north post (1.1 m, facing east)
    x, y = POSTS[1]
    add('crank', rbox((x + PR + 0.006, y, 1.10), (0.024, 0.06, 0.08), 0.008, 3), 'steel')
    add('crank', xform(lathe(rprof(0.012, 0, 0.008, 0.003, 3), 20, (0, 0)), T(x + PR + 0.018, y, 1.10) @ R('y', math.pi / 2)), 'steel_d')
    x, y = POSTS[3]
    add('btnpad', rbox((x + PR + 0.008, y, 1.10), (0.022, 0.07, 0.12), 0.008, 3), 'button')
    add('btnpad', xform(lathe(rprof(0.016, 0, 0.007, 0.003, 3), 20, (0, 0)), T(x + PR + 0.019, y, 1.10) @ R('y', math.pi / 2)), 'steel')
    # ---- ceiling rail tying the post tops together (+ its LED strip on the front run)
    rz0 = H - 0.05
    for b in (box(POSTS[0][0] - 0.02, POSTS[0][1] - 0.02, rz0, POSTS[1][0] + 0.02, POSTS[0][1] + 0.02, H),
              box(POSTS[2][0] - 0.02, POSTS[2][1] - 0.02, rz0, POSTS[3][0] + 0.02, POSTS[2][1] + 0.02, H),
              box(POSTS[1][0] - 0.02, POSTS[1][1], rz0, POSTS[1][0] + 0.02, POSTS[3][1], H)):
        add('rail', b, 'steel_h')
    add('rail', box(POSTS[1][0] - 0.012, POSTS[1][1] + 0.03, rz0 - 0.002, POSTS[1][0] + 0.012, POSTS[3][1] - 0.03, rz0), 'led_off')
    add('rail_led', box(POSTS[1][0] - 0.012, POSTS[1][1] + 0.03, rz0 - 0.0035, POSTS[1][0] + 0.012, POSTS[3][1] - 0.03, rz0 - 0.002), 'led')
    # ---- two book towers (open to the east), shelves every ~0.36 m
    zs = [0.06, 0.40, 0.76, 1.12, 1.48, 1.84, 2.20, 2.56, H]
    for nm, (x0, x1, y0, y1) in (('twS', TWS), ('twN', TWN)):
        add(nm, box(x0, y0, 0.0, x1 - 0.02, y1, 0.06), 'plinth')
        add(nm, box(x0, y0, 0.0, x1, y0 + t, H), 'white_cab'); add(nm, box(x0, y1 - t, 0.0, x1, y1, H), 'white_cab')
        add(nm, box(x0, y0, 0.0, x0 + 0.012, y1, H), 'white_in')
        for z in zs[:-1]:
            wood(nm, x0 + 0.012, y0 + t, z, x1, y1 - t, z + 0.022, 'oak')
        add(f'{nm}_led', box(x1 - 0.05, y0 + t + 0.02, 2.534, x1 - 0.035, y1 - t - 0.02, 2.5355), 'led')
    # motor box in the top of the north-west tower (unlabelled)
    x0, x1, y0, y1 = TWN
    add('motor', box(x0 + 0.02, y0 + t + 0.005, 2.58, x1 - 0.005, y1 - t - 0.005, H - 0.004), 'white_cab')
    # books: a gradient mustard -> ochre -> sage -> slate across the shelves (blank spines)
    grad = ['bk_mustard', 'bk_mustard', 'bk_ochre', 'bk_ochre', 'bk_cream', 'bk_sage', 'bk_sage', 'bk_slate', 'bk_slate', 'bk_white']
    shelf_rows = {'twN': [0, 1, 2, 3, 4, 5, 6], 'twS': [1, 2, 3, 4, 5, 6]}
    for nm, (x0, x1, y0, y1) in (('twN', TWN), ('twS', TWS)):
        for si in shelf_rows[nm]:
            z = zs[si] + 0.022
            gap = zs[si + 1] - z
            if nm == 'twS' and si == 3:
                continue                                    # the empty cubby (pillows hop in before the long-cut descent)
            y = y0 + t + 0.01
            g0 = (si * 1.4 + (0 if nm == 'twN' else 0.7)) % len(grad)
            ymax = y1 - t - 0.01
            kk = 0
            piece = f'bk_{nm}{si}'
            while y < ymax - 0.03:
                th = rng.uniform(0.022, 0.04)
                h = min(gap - 0.03, rng.uniform(0.20, 0.27))
                m = grad[int(g0 + kk * 0.5) % len(grad)]
                if kk == 6 and si % 2 == 0:                  # a short stack lying flat
                    for q in range(3):
                        add(piece, box(x1 - 0.30, y, z + q * 0.032, x1 - 0.06, y + 0.10, z + q * 0.032 + 0.03), grad[(int(g0) + q * 3) % len(grad)])
                    y += 0.105
                    kk += 1
                    continue
                d = rng.uniform(0.18, 0.24)
                add(piece, box(x1 - 0.03 - d, y, z, x1 - 0.03, y + th, z + h), m)
                y += th + 0.002
                kk += 1
    plant('tw_plant', 0.22, 0.21, zs[7] + 0.022, 0.05, 0.08, rng, 9, pot='ceramic')
    # ---- sofa under the bed: seat box, two lidded seat cushions, three wall pads
    sx0, sx1, sy0, sy1 = SOFA
    add('sofa', rbox(((sx0 + sx1) / 2, (sy0 + sy1) / 2, 0.16), (sx1 - sx0, sy1 - sy0, 0.28), 0.03, 3), 'sofa')
    add('sofa', box(sx0 + 0.04, sy0 + 0.04, 0.0, sx1 - 0.04, sy1 - 0.04, 0.03), 'plinth')
    for k, (y0, y1) in enumerate(((sy0, 1.5), (1.5, sy1))):
        lid = f'sofa_lid{k}'
        add(lid, box(sx0 + 0.02, y0 + 0.02, 0.30, sx1 - 0.02, y1 - 0.02, 0.318), 'oak_y')
        add(lid, rbox(((sx0 + sx1) / 2 + 0.01, (y0 + y1) / 2, 0.37), (sx1 - sx0 - 0.03, y1 - y0 - 0.03, 0.11), 0.04, 5), 'sofa')
    for k in range(3):
        y0 = sy0 + 0.02 + k * (sy1 - sy0 - 0.04) / 3
        y1 = y0 + (sy1 - sy0 - 0.04) / 3 - 0.012
        add(f'pad{k}', rbox((0.03, (y0 + y1) / 2, 0.70), (0.06, y1 - y0, 0.48), 0.025, 5), 'sofa_pad')
    # sofa contents (long cut reveal): board games + folded throws
    for k, (m, h) in enumerate((('gm_terra', 0.07), ('gm_sage', 0.06), ('gm_slate', 0.08), ('gm_mustard', 0.06))):
        add('sofa_games', rbox((0.40, 0.75 + 0.02 * (k % 2), 0.05 + sum([0.07, 0.06, 0.08, 0.06][:k]) + h / 2), (0.44, 0.34, h), 0.005, 3), m)
    stack('sofa_throws', 0.42, 1.95, 0.04, (0.50, 0.70, 0.06), ['throw2', 'cl_rust', 'cl_cream'], 3, rng)
    # sofa pillows (mustard + pale blue-grey) against the wall pads
    pillow('spil0', (0.18, 1.05, 0.62), (0.46, 0.16, 0.44), 0.0, 'pil_mustard', yaw=math.radians(90) - 0.0)
    pillow('spil1', (0.18, 1.95, 0.62), (0.46, 0.16, 0.44), 0.0, 'pil_paleblue', yaw=math.radians(90))
    # ottoman on castors (bedside alcove)
    ox, oy = 1.10, 2.79
    add('ottoman', rbox((ox, oy, 0.23), (0.40, 0.40, 0.33), 0.03, 3), 'sofa_pad')
    add('ottoman_lid', rbox((ox, oy, 0.42), (0.41, 0.41, 0.06), 0.025, 3), 'oak_x')
    for dx in (-0.15, 0.15):
        for dy in (-0.15, 0.15):
            add('ottoman', ellipsoid((ox + dx, oy + dy, 0.03), (0.03, 0.03, 0.03), 8), 'blackm')
    # fold-out nightstand on the north-west tower's east face (hinged at its bottom edge, flips up + out)
    x1 = TWN[1]
    add('nstand', box(x1, 2.64, 0.665, x1 + 0.34, 2.95, 0.687), 'oak_x')
    add('nstand', box(x1, 2.64, 0.64, x1 + 0.02, 2.95, 0.665), 'oak_x')
    add('ns_lamp', lathe(rprof(0.05, 0.687, 0.70, 0.004, 3), 24, (0.62, 2.84)), 'ceramic_s')
    add('ns_lamp', tube([(0.62, 2.84, 0.70), (0.62, 2.84, 0.92)], 0.006, 8), 'steel')
    add('ns_lamp', lathe([(0.03, 1.00), (0.09, 0.88), (0.0905, 0.87), (0.031, 0.999)], 28, (0.62, 2.84)), 'shade')
    add('ns_bulb', ellipsoid((0.62, 2.84, 0.92), (0.022, 0.022, 0.026), 8), 'bulb')
    add('ns_phone', rbox((0.50, 2.72, 0.692), (0.075, 0.155, 0.009), 0.004, 3), 'phone')
    add('ns_mug', lathe([(0, 0.687), (0.036, 0.687), (0.04, 0.777), (0.035, 0.777), (0.032, 0.699), (0, 0.699)], 22, (0.66, 2.70)), 'ceramic')
    add('ns_mug', tube([(0.66, 2.66, 0.757), (0.66, 2.635, 0.742), (0.66, 2.66, 0.712)], 0.006, 8), 'ceramic')
    add('ns_glow', box(0.466, 2.648, 0.6965, 0.534, 2.792, 0.6975), 'lscreen')
    # ottoman contents (slippers + a spare throw) and the rug (long cut)
    for dy in (-0.05, 0.05):
        add('ot_items', ellipsoid((ox - 0.08, oy + dy, 0.30), (0.12, 0.045, 0.03), 10), 'cl_cream')
    add('ot_items', rbox((ox + 0.08, oy, 0.31), (0.16, 0.30, 0.06), 0.025, 3), 'throw')
    add('rug', rbox((1.20, 1.50, 0.008), (1.10, 1.60, 0.016), 0.006, 3), 'rug')


# ------------------------------------------------------------------------------------------- the bed (built parked)
def build_bed(rng):
    z0 = Z_UP
    t = 0.024
    # oak underside + side rails
    wood('bed', BX0, BY0, z0, BX1, BY1, z0 + 0.03, 'oak')
    wood('bed', BX0, BY0, z0 + 0.03, BX0 + t, BY1, z0 + 0.15, 'oak')
    wood('bed', BX0, BY0, z0 + 0.03, BX1, BY0 + t, z0 + 0.15, 'oak')
    wood('bed', BX0, BY1 - t, z0 + 0.03, BX1, BY1, z0 + 0.15, 'oak')
    # front rail around the drawer opening (drawer y 1.15..1.85)
    wood('bed', BX1 - t, BY0, z0 + 0.03, BX1, 1.15, z0 + 0.15, 'oak')
    wood('bed', BX1 - t, 1.85, z0 + 0.03, BX1, BY1, z0 + 0.15, 'oak')
    wood('bed', BX1 - t, 1.15, z0 + 0.13, BX1, 1.85, z0 + 0.15, 'oak')
    add('bed', box(BX1, BY0 + 0.04, z0 + 0.142, BX1 + 0.004, BY1 - 0.04, z0 + 0.148), 'sensor')       # safety-sensor strip
    # corner sleeves to the posts
    for (px, py) in POSTS:
        cx = min(max(px, BX0), BX1); cy = min(max(py, BY0), BY1)
        add('bed', box(min(px, cx) - 0.02, min(py, cy) - 0.02, z0 + 0.02, max(px, cx) + 0.02, max(py, cy) + 0.02, z0 + 0.13), 'steel_d')
        add('bed', lathe(rprof(PR + 0.012, z0 + 0.0, z0 + 0.15, 0.006, 3), 24, (px, py)), 'steel')
    # downlight trims under the bed (lit discs are 'bed_dl')
    for (x, y) in DL:
        add('bed', lathe([(0.034, z0 + 0.002), (0.046, z0 + 0.002), (0.048, z0 - 0.004), (0.052, z0 - 0.005), (0.054, z0)], 28, (x, y)), 'white_cab')
        add('bed', lathe([(0.0, z0 - 0.0015), (0.035, z0 - 0.0015), (0.035, z0 + 0.001), (0.0, z0 + 0.001)], 24, (x, y)), 'led_off')
        disc('bed_dl', (x, y), 0.036, z0 - 0.0035, z0 - 0.002, 'dl_emis')
    # mattress + bedding
    add('bed', rbox(((BX0 + BX1) / 2, (BY0 + BY1) / 2, z0 + 0.12), (BX1 - BX0 - 0.05, BY1 - BY0 - 0.05, 0.17), 0.04, 5), 'mattress')
    cloth('bed', BX0 + 0.03, BX1, BY0, 2.12, z0 + 0.215, z0 + 0.155, 0.035, 'linen', 3, sides=('e', 's'), puff=0.010)
    add('bed', rbox(((BX0 + BX1) / 2 + 0.01, 2.10, z0 + 0.225), (BX1 - BX0 - 0.02, 0.12, 0.03), 0.013, 3), 'pil_white')
    cloth('bed', BX0 + 0.03, BX1 + 0.02, 0.62, 0.94, z0 + 0.240, z0 + 0.01, 0.03, 'throw', 7, sides=('e',), puff=0.004)
    # straps across the bedding (unclip once it is down)
    for y in (1.12, 1.92):
        add('bed_straps', box(BX0 + 0.03, y - 0.022, z0 + 0.252, BX1 + 0.006, y + 0.022, z0 + 0.258), 'strap')
        add('bed_straps', box(BX1 + 0.0, y - 0.022, z0 + 0.15, BX1 + 0.006, y + 0.022, z0 + 0.255), 'strap')
        add('bed_straps', box(BX1 - 0.03, y - 0.028, z0 + 0.250, BX1 + 0.01, y + 0.028, z0 + 0.262), 'buckle')
    # pillows at the head (north)
    pillow('bed_pillows', (0.45, 2.33, z0 + 0.26), (0.58, 0.13, 0.36), -1.2, 'pil_white')
    pillow('bed_pillows', (1.11, 2.33, z0 + 0.26), (0.58, 0.13, 0.36), -1.2, 'pil_white')
    # drawer in the front rail (y 1.15..1.85), slides out east
    dz0 = z0 + 0.035
    add('bed_drawer', box(BX1 - t + 0.002, 1.152, dz0, BX1, 1.848, z0 + 0.128), 'oak_y')
    add('bed_drawer', box(BX1, 1.45, z0 + 0.10, BX1 + 0.012, 1.55, z0 + 0.11), 'steel')
    add('bed_drawer', box(1.02, 1.17, dz0, BX1 - t, 1.83, dz0 + 0.008), 'white_in')
    for b in (box(1.02, 1.17, dz0, 1.032, 1.83, z0 + 0.12), box(1.02, 1.17, dz0, BX1 - t, 1.182, z0 + 0.12),
              box(1.02, 1.818, dz0, BX1 - t, 1.83, z0 + 0.12)):
        add('bed_drawer', b, 'white_in')
    stack('bd_pj', 1.22, 1.35, dz0 + 0.008, (0.26, 0.24, 0.03), ['cl_denim', 'cl_cream'], 2, rng)
    add('bd_book', box(1.12, 1.56, dz0 + 0.008, 1.30, 1.70, dz0 + 0.035), 'bk_sage')
    add('bd_mask', rbox((1.32, 1.74, dz0 + 0.016), (0.16, 0.07, 0.016), 0.007, 3), 'cl_sage')


# ------------------------------------------------------------------------------------------- desk (north wall)
def build_desk(rng):
    x0, x1, fy, dz = DESK
    wood('desk', x0, fy, dz - 0.035, x1, D, dz, 'oak')
    add('desk', box(x0, D - 0.03, dz - 0.10, 2.55, D, dz - 0.035), 'oak_x')
    add('desk', tube([(x1 - 0.04, fy + 0.04, dz - 0.035), (x1 - 0.04, fy + 0.04, 0.0)], 0.015, 12), 'steel')
    # pedestal at the west end (x 1.60..2.05): shell + three drawers (top one opens toward the room)
    px0, px1 = 1.60, 2.05
    for b in (box(px0, fy + 0.02, 0.0, px1, D, 0.04), box(px0, fy + 0.02, 0.04, px0 + 0.018, D, dz - 0.035),
              box(px1 - 0.018, fy + 0.02, 0.04, px1, D, dz - 0.035), box(px0, D - 0.018, 0.04, px1, D, dz - 0.035)):
        add('ped', b, 'white_cab')
    zs = [0.045, 0.27, 0.49, dz - 0.04]
    for k in range(3):
        nm = 'ped_dr' if k == 2 else 'ped_fixed'
        a, b = zs[k], zs[k + 1]
        add(nm, box(px0 + 0.002, fy + 0.02, a + 0.003, px1 - 0.002, fy + 0.04, b - 0.003), 'oak_x')
        add(nm, box(1.77, fy + 0.008, b - 0.05, 1.89, fy + 0.02, b - 0.04), 'steel')
        if k == 2:
            add(nm, box(px0 + 0.03, fy + 0.04, a + 0.01, px1 - 0.03, D - 0.03, a + 0.02), 'white_in')
            for bb in (box(px0 + 0.03, fy + 0.04, a + 0.02, px0 + 0.042, D - 0.03, b - 0.03), box(px1 - 0.042, fy + 0.04, a + 0.02, px1 - 0.03, D - 0.03, b - 0.03),
                       box(px0 + 0.03, D - 0.042, a + 0.02, px1 - 0.03, D - 0.03, b - 0.03)):
                add(nm, bb, 'white_in')
    a = zs[2] + 0.02
    add('ped_items', box(1.66, 2.55, a, 1.84, 2.75, a + 0.016), 'bk_sage')
    add('ped_items', box(1.67, 2.56, a + 0.016, 1.83, 2.74, a + 0.030), 'bk_mustard')
    add('ped_items', rbox((1.93, 2.62, a + 0.012), (0.07, 0.07, 0.024), 0.008, 3), 'ceramic')
    add('ped_items', tube([(1.93, 2.62, a + 0.02), (1.97, 2.70, a + 0.02), (1.91, 2.80, a + 0.02)], 0.004, 6), 'cl_white')
    add('ped_items', box(1.70, 2.80, a, 1.96, 2.90, a + 0.012), 'bk_cream')
    # laptop (lid hinges at its north edge), desk lamp, mug, plant
    lx, ly = 2.40, 2.72
    add('laptop', box(lx - 0.15, ly - 0.105, dz, lx + 0.15, ly + 0.105, dz + 0.012), 'alu')
    add('laptop', box(lx - 0.13, ly - 0.03, dz + 0.012, lx + 0.13, ly + 0.09, dz + 0.0125), 'kb')
    add('lid', box(lx - 0.15, ly - 0.105, dz + 0.0131, lx + 0.15, ly + 0.105, dz + 0.020), 'alu')
    add('lid', box(lx - 0.142, ly - 0.097, dz + 0.0126, lx + 0.142, ly + 0.097, dz + 0.0131), 'lscreen')
    lpx, lpy = 2.86, 2.86
    add('lamp', lathe(rprof(0.06, dz, dz + 0.014, 0.005, 3), 28, (lpx, lpy)), 'steel')
    add('lamp', tube([(lpx, lpy, dz + 0.01), (lpx, lpy, 1.16), (lpx - 0.04, lpy - 0.03, 1.20), (lpx - 0.12, lpy - 0.09, 1.21)], 0.006, 10), 'steel')
    add('lamp', lathe([(0.01, 1.225), (0.03, 1.215), (0.052, 1.175), (0.064, 1.14)], 28, (lpx - 0.12, lpy - 0.09)), 'ceramic_s')
    add('lamp_on', ellipsoid((lpx - 0.12, lpy - 0.09, 1.16), (0.02, 0.02, 0.02), 8), 'bulb')
    add('mug', lathe([(0, dz), (0.036, dz), (0.04, dz + 0.09), (0.035, dz + 0.09), (0.032, dz + 0.012), (0, dz + 0.012)], 22, (2.45, 2.62)), 'ceramic_s')
    add('mug', tube([(2.49, 2.62, dz + 0.07), (2.515, 2.62, dz + 0.055), (2.49, 2.62, dz + 0.025)], 0.006, 8), 'ceramic_s')
    plant('dplant', 1.70, 2.88, dz, 0.05, 0.08, rng, 9)
    # chair (faces north, tucked under the desk)
    cx, cy = 2.45, 2.62
    add('chair', rbox((cx, cy, 0.47), (0.46, 0.44, 0.07), 0.03, 3), 'chair_fab')
    add('chair', xform(rbox((cx, cy - 0.21, 0.78), (0.42, 0.06, 0.36), 0.03, 3), about((cx, cy - 0.21, 0.6), R('x', 0.12))), 'chair_fab')
    add('chair', tube([(cx, cy, 0.11), (cx, cy, 0.44)], 0.024, 12), 'blackm')
    add('chair', tube([(cx, cy - 0.10, 0.46), (cx, cy - 0.20, 0.52), (cx, cy - 0.22, 0.62)], 0.012, 8), 'blackm')
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.3
        add('chair', tube([(cx, cy, 0.10), (cx + 0.27 * math.cos(a), cy + 0.27 * math.sin(a), 0.06)], 0.014, 8), 'blackm')
        add('chair', ellipsoid((cx + 0.27 * math.cos(a), cy + 0.27 * math.sin(a), 0.028), (0.025, 0.025, 0.026), 8), 'blackm')
    # roller blind (roll + fabric hanging to z0 of the fabric; the long cut rolls it up)
    add('blind_roll', tube([(WX0 - 0.03, D - 0.05, WZ1 + 0.07), (WX1 + 0.03, D - 0.05, WZ1 + 0.07)], 0.032, 16), 'white_cab')
    add('blind', box(WX0 - 0.01, D - 0.085, 1.92, WX1 + 0.01, D - 0.079, WZ1 + 0.07), 'blind')
    add('blind', box(WX0 - 0.01, D - 0.09, 1.905, WX1 + 0.01, D - 0.074, 1.925), 'oak_x')
    # peg hooks west of the door, coat + tote
    add('pegs', box(1.32, 0.0, 1.62, 2.03, 0.02, 1.72), 'oak_x')
    for x in (1.45, 1.70, 1.95):
        add('pegs', xform(lathe(rprof(0.014, 0, 0.07, 0.006, 3), 16, (0, 0)), T(x, 0.02, 1.67) @ R('x', -math.pi / 2)), 'oak_z')
    add('coat', rbox((1.70, 0.07, 1.20), (0.40, 0.06, 0.88), 0.03, 3), 'cl_camel')
    add('coat', ellipsoid((1.70, 0.09, 1.60), (0.12, 0.04, 0.06), 10), 'cl_camel')
    add('tote', rbox((1.95, 0.06, 1.38), (0.32, 0.05, 0.36), 0.012, 3), 'cl_sage')
    add('tote', tube([(1.86, 0.06, 1.56), (1.95, 0.05, 1.67), (2.04, 0.06, 1.56)], 0.008, 6), 'cl_sage')


# ------------------------------------------------------------------------------------------- wardrobe (east wall)
def build_wardrobe(rng):
    x0, x1, y0, y1 = WR
    t = 0.018
    add('wr_body', box(x0 + 0.04, y0, 0.0, x1, y1, 0.06), 'plinth')
    for b in (box(x1 - t, y0, 0.06, x1, y1, H), box(x0 + 0.04, y0, 0.06, x1, y1, 0.078), box(x0 + 0.04, y0, 2.40, x1, y1, 2.418)):
        add('wr_body', b, 'white_in')
    add('wr_body', box(x0, y0, 0.0, x1, y0 + t, H), 'white_cab'); add('wr_body', box(x0, y1 - t, 0.0, x1, y1, H), 'white_cab')
    add('wr_body', box(x0, y0, 2.418, x1, y1, H), 'white_cab')
    add('wr_body', box(x0, y0, 2.385, x0 + 0.05, y1, 2.418), 'alu')                  # top track
    add('wr_body', box(x0 + 0.04, WRM - 0.009, 0.078, x1 - t, WRM + 0.009, 2.40), 'white_in')
    # south section: long hanging over a shoe pull-out
    add('wr_body', tube([(x0 + 0.29, y0 + 0.03, 2.25), (x0 + 0.29, WRM - 0.03, 2.25)], 0.011, 10), 'steel')
    add('wr_body', box(x0 + 0.04, y0 + t, 0.40, x1 - t, WRM - 0.009, 0.418), 'white_in')
    for k, m in enumerate(('cl_camel', 'cl_rust', 'cl_cream', 'cl_denim', 'cl_sage', 'cl_grey')):
        garment('wr_cl', x0 + 0.29, y0 + 0.08 + k * 0.105, 2.25, rng.uniform(1.15, 1.45) if k % 2 else rng.uniform(1.0, 1.25), 0.42, m, along='y')
    # shoe pull-out (x out toward the room)
    sp = 'wr_shoe'
    add(sp, box(x0 + 0.06, y0 + 0.03, 0.09, x1 - 0.04, WRM - 0.03, 0.10), 'white_in')
    add(sp, box(x0 + 0.045, y0 + 0.03, 0.08, x0 + 0.06, WRM - 0.03, 0.38), 'oak_y')
    for k, m in enumerate(('shoe_white', 'shoe_tan', 'shoe_white')):
        for dy in (-0.05, 0.05):
            add(sp, ellipsoid((x0 + 0.30, y0 + 0.15 + k * 0.20 + dy, 0.135), (0.12, 0.045, 0.035), 10), m)
    # north section: tee drawers at the bottom, ironing board upright, folded stacks on shelves
    for k in range(3):
        a = 0.08 + k * 0.17
        nm = 'wr_dr' if k == 1 else 'wr_drs'
        add(nm, box(x0 + 0.05, WRM + 0.012, a + 0.003, x0 + 0.068, y1 - t - 0.003, a + 0.167), 'oak_y')
        add(nm, box(x0 + 0.042, 1.90, a + 0.13, x0 + 0.05, 2.00, a + 0.14), 'steel')
        if k == 1:
            add(nm, box(x0 + 0.068, WRM + 0.03, a + 0.012, x1 - 0.04, y1 - 0.04, a + 0.022), 'white_in')
            for b in (box(x0 + 0.068, WRM + 0.03, a + 0.022, x1 - 0.04, WRM + 0.042, a + 0.15), box(x0 + 0.068, y1 - 0.052, a + 0.022, x1 - 0.04, y1 - 0.04, a + 0.15),
                      box(x1 - 0.052, WRM + 0.03, a + 0.022, x1 - 0.04, y1 - 0.04, a + 0.15)):
                add(nm, b, 'white_in')
    a = 0.08 + 0.17 + 0.022
    stack('wr_tees', 2.62, 1.78, a, (0.30, 0.22, 0.03), ['cl_white', 'cl_mustard', 'cl_grey'], 3, rng)
    stack('wr_tees', 2.62, 2.08, a, (0.30, 0.22, 0.03), ['cl_denim', 'cl_cream', 'cl_rust'], 3, rng)
    add('wr_body', box(x0 + 0.04, WRM + 0.009, 0.60, x1 - t, y1 - t, 0.618), 'white_in')
    # ironing board stored upright (hinged at its bottom, folds out west at 0.85 m)
    add('iron', rbox((x0 + 0.115, 1.95, 1.25), (0.03, 0.36, 0.80), 0.012, 3), 'board')
    add('iron', box(x0 + 0.10, 1.80, 0.85, x0 + 0.13, 2.10, 0.87), 'steel')
    add('iron_leg', tube([(x0 + 0.14, 1.95, 1.55), (x0 + 0.14, 1.95, 0.71)], 0.010, 8), 'steel')
    add('iron_leg', box(x0 + 0.13, 1.85, 0.70, x0 + 0.15, 2.05, 0.72), 'steel')
    for z in (1.45, 1.80, 2.10):
        add('wr_body', box(x0 + 0.20, WRM + 0.009, z, x1 - t, y1 - t, z + 0.018), 'white_in')
    for k, z in enumerate((1.468, 1.818, 2.118)):
        stack(f'wr_fold{k}', 2.78, 1.80, z, (0.32, 0.28, 0.05), [('cl_cream', 'cl_sage', 'cl_grey'), ('cl_navy', 'cl_white', 'cl_camel'),
                                                                ('cl_rust', 'cl_cream', 'cl_denim')][k], 3 + (k == 1), rng)
        stack(f'wr_fold{k}', 2.78, 2.12, z, (0.32, 0.28, 0.05), [('cl_white', 'cl_mustard', 'cl_white'), ('cl_sage', 'cl_grey', 'cl_cream'),
                                                                ('cl_white', 'cl_denim', 'cl_sage')][k], 3, rng)
    # sliding fronts: oak (inner track, north section) and mirror (outer track, south section); steel pulls
    add('wr_oak', box(x0 - 0.02, WRM - 0.01, 0.07, x0, y1, 2.38), 'oak_z')
    add('wr_oak', box(x0 - 0.03, WRM + 0.03, 0.95, x0 - 0.02, WRM + 0.042, 1.55), 'steel')
    add('wr_mir', box(x0 - 0.045, y0, 0.07, x0 - 0.025, WRM + 0.01, 2.38), 'oak_z')
    add('wr_mir', box(x0 - 0.0455, y0 + 0.02, 0.09, x0 - 0.0445, WRM - 0.01, 2.36), 'mirror')
    add('wr_mir', box(x0 - 0.055, WRM - 0.04, 0.95, x0 - 0.045, WRM - 0.028, 1.55), 'steel')


def build():
    materials()
    fg.materials()
    rng = np.random.default_rng(9)
    build_shell()
    build_bay(rng)
    build_bed(rng)
    build_desk(rng)
    build_wardrobe(rng)
    global FIG
    FIG = fg.figure('fig', 'adult', pose='stand', at=(1.95, 1.95, -60), mat='fig_adult')


FIG = None

# ------------------------------------------------------------------------------------------- the bed's track
if LONG:
    T_UP0, T_UP1 = 0.60, 1.20
    T_DN0, T_DN1 = 27.60, 30.00
    T_RE0, T_RE1 = 44.70, 47.00
else:
    T_UP0, T_UP1 = 0.60, 1.20
    T_DN0, T_DN1 = 7.95, 10.15
    T_RE0, T_RE1 = 1e9, 1e9


def ease_move(u):
    """Smootherstep: zero velocity and acceleration at both ends (a motor move, no overshoot)."""
    u = c01(u)
    return u * u * u * (u * (u * 6 - 15) + 10)


def bed_dz(t):
    """Height offset of the bed from its parked position (0 = parked, -BED_DROP = down on the sofa)."""
    if t < T_UP1:
        return -Z_UP * (1 - smooth_rise((t - T_UP0 - 0.12) / (T_UP1 - T_UP0 - 0.12)))
    if t < T_DN0:
        return 0.0
    if t < T_RE0:
        return -BED_DROP * ease_move((t - T_DN0) / (T_DN1 - T_DN0))
    return -BED_DROP * (1 - ease_move((t - T_RE0) / (T_RE1 - T_RE0)))


def smooth_rise(u):
    """The frame-1 build rise: quick start, eased into the dock."""
    u = c01(u)
    return u * u * (3 - 2 * u) * 0.35 + (1 - (1 - u) ** 2.2) * 0.65


def descent_progress(t):
    return -bed_dz(t) / BED_DROP if t >= T_DN0 else 0.0


# ------------------------------------------------------------------------------------------- camera
VFOV = 85.0


def P(x, y, z, yaw, pitch):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch)


S1 = (P(2.34, 0.12, 1.70, -40.0, -11.0), P(2.18, 0.40, 1.55, -54.0, 8.0))
S2 = (P(1.00, 0.80, 1.34, 74.0, -6.0), P(1.75, 1.85, 1.32, 10.0, -18.0))
S3 = (P(2.30, 0.12, 1.50, -38.0, 12.0), P(2.22, 0.20, 1.15, -44.0, 0.0))
S4 = (P(2.10, 0.85, 1.05, -38.0, -16.0), S1[0])
HOLDS = [(0.0, 3.08, S1), (3.3, 7.08, S2), (7.3, 10.78, S3), (11.0, DUR, S4)]
RIDE = 2                                             # index of the ride hold
EASE_IN = {0: 0.0}                                   # holds whose glide eases in over the first x seconds
EASE_OUT = {3: 0.4}                                  # ... or eases out over the last x seconds


def warp(u, dur, a_in, a_out):
    """Progress 0..1 at constant speed, with optional quadratic ease-in / ease-out windows (in seconds)."""
    u = c01(u)
    ai, ao = a_in / dur, a_out / dur
    # piecewise: accelerate over [0, ai], constant, decelerate over [1 - ao, 1]; normalised to reach 1
    v = 1.0 / (1 - ai / 2 - ao / 2)
    if ai > 0 and u < ai:
        return v * u * u / (2 * ai)
    if ao <= 0 or u < 1 - ao:
        return v * (ai / 2 + (u - ai))
    w = 1 - u
    return 1 - v * w * w / (2 * ao)


def make_camera(holds, ride, ease_in, ease_out, ride_fn=None):
    def at_hold(i, t):
        t0, t1, (a, b) = holds[i]
        u = (t - t0) / (t1 - t0)
        if i == ride and ride_fn is not None:
            return ride_fn(a, b, t)
        s = warp(u, t1 - t0, ease_in.get(i, 0.0), ease_out.get(i, 0.0))
        c = lerp_cam(a, b, s, lift=0.0, vfov=VFOV)
        if i == 0 and t0 == 0.0:                      # frame-1 station: the tilt follows the rising bed
            c['pitch'] = a['pitch'] + (b['pitch'] - a['pitch']) * (0.15 * s + 0.85 * smooth((t - 0.62) / 0.75))
        return c

    def camera(t):
        if REST:
            return dict(holds[min(len(holds) - 1, int(t))][2][0], vfov=VFOV)
        for i, (t0, t1, st) in enumerate(holds):
            if t < t1 or i == len(holds) - 1:
                return at_hold(i, min(max(t, t0), t1))
            n0 = holds[i + 1][0]
            if t < n0:
                u = (t - t1) / (n0 - t1)
                return lerp_cam(at_hold(i, t1), at_hold(i + 1, n0), smooth(u), lift=2.0, vfov=VFOV)
        return at_hold(len(holds) - 1, holds[-1][1])
    return camera


def ride_cam(a, b, t, hold=None):
    """The ride: x/y/yaw drift sideways at constant speed through the whole station, height and pitch follow the bed."""
    t0, t1 = hold if hold else HOLDS[RIDE][:2]
    u = c01((t - t0) / (t1 - t0))
    p = descent_progress(t)
    pa, pb = np.array(a['pos']), np.array(b['pos'])
    xy = pa[:2] + (pb[:2] - pa[:2]) * u
    z = pa[2] + (pb[2] - pa[2]) * (0.12 * u + 0.88 * p)
    pitch = a['pitch'] + (b['pitch'] - a['pitch']) * (0.12 * u + 0.88 * p)
    yaw = a['yaw'] + (b['yaw'] - a['yaw']) * u
    return dict(pos=(float(xy[0]), float(xy[1]), float(z)), yaw=yaw, pitch=pitch, vfov=VFOV)


L_ST = [
    (0.0, 3.0, S1),
    (3.3, 4.45, (P(1.50, 1.05, 1.25, -128.0, 0.0), P(1.40, 0.90, 1.38, -134.0, 4.0))),      # L2a south tower fills
    (4.6, 6.6, (P(1.45, 2.00, 1.25, -50.0, 0.0), P(1.35, 2.10, 1.38, -44.0, 4.0))),          # L2b north tower fills        # L2 low slide along the bay
    (6.9, 10.2, (P(1.75, 0.80, 1.75, -66.0, -42.0), P(1.75, 2.20, 1.75, -114.0, -42.0))),   # L3 orbit the sofa
    (10.5, 13.4, (P(2.35, 1.45, 0.82, -84.0, -6.0), P(1.95, 1.55, 0.78, -88.0, -6.0))),    # L4 push in at seat height
    (13.7, 16.6, (P(2.05, 1.90, 0.95, -48.0, 8.0), P(1.98, 2.00, 1.95, -70.0, 16.0))),    # L5 crane up beside the bed
    (16.9, 20.1, (P(1.30, 1.50, 1.30, 12.0, -10.0), P(1.85, 1.55, 1.30, 2.0, -10.0))),     # L6 slide toward the window
    (20.4, 23.4, (P(1.55, 1.45, 1.45, 30.0, -14.0), P(2.05, 1.40, 1.45, 8.0, -14.0))),   # L7 orbit behind the chair
    (23.7, 25.2, (P(2.92, 2.92, 2.40, -136.0, -30.0), P(2.80, 2.80, 2.32, -133.0, -26.0))),  # L8a NE corner: chair, ottoman, pillows hop
    (25.35, 26.8, (P(0.90, 1.30, 1.40, 42.0, -4.0), P(1.00, 1.42, 1.38, 40.0, -2.0))),      # L8b front-on to the button press
    (27.1, 31.0, (P(2.30, 0.12, 1.50, -38.0, 12.0), P(2.22, 0.20, 1.15, -44.0, 0.0))),     # L9 the ride
    (31.3, 34.4, (P(2.45, 0.85, 0.85, -58.0, -12.0), P(2.45, 1.20, 0.90, -85.0, -12.0))), # L10 low slide along the front rail
    (34.7, 37.5, (P(2.40, 1.10, 1.40, -38.0, -12.0), P(2.05, 1.55, 1.30, -62.0, -14.0))),  # L11 orbit round the head end
    (37.8, 40.9, (P(0.95, 0.95, 1.35, 100.0, -8.0), P(1.15, 1.90, 1.30, 78.0, -6.0))),     # L12 facing east, slide north
    (41.2, 44.0, (P(1.28, 0.50, 1.30, 46.0, -20.0), P(1.40, 0.72, 1.25, 38.0, -20.0))),    # L13 push in on the north section
    (44.3, 47.2, (P(2.22, 0.20, 1.15, -44.0, 2.0), P(2.30, 0.12, 1.45, -40.0, 14.0))),  # L14 NE corner, tilt up with the bed
    (47.5, 49.5, (P(2.32, 0.12, 1.60, -40.0, 4.0), S1[0])),                                # L15 drifting wide back to frame 1
]
if LONG:
    HOLDS = L_ST
    RIDE = 10
    EASE_IN = {0: 0.0}
    EASE_OUT = {16: 0.4}

camera = make_camera(HOLDS, RIDE, EASE_IN, EASE_OUT, ride_cam)


# ------------------------------------------------------------------------------------------- lights (fixed slots)
LSKY = (10.0, 10.6, 11.6)
LSUN = (78000.0, 70000.0, 56000.0)
LFILL = (1.9, 1.86, 1.80)
LFILL2 = (1.1, 1.08, 1.04)
LDOWN = (380.0, 340.0, 270.0)
LRAIL = (95.0, 84.0, 64.0)
LSHELF = (48.0, 41.0, 30.0)
LLAMP = (150.0, 118.0, 76.0)
T_CLOUD0, T_CLOUD1 = (12.0, 14.0) if not LONG else (1e9, 1e9)


def cloud(t):
    """Sun factor: a passing cloud dims the sun by about 25%, then it comes back for the loop."""
    if t < T_CLOUD0:
        return 1.0
    if t < T_CLOUD1:
        return 1.0 - 0.14 * smooth((t - T_CLOUD0) / 0.35)
    return 0.86 + 0.14 * smooth((t - T_CLOUD1) / 0.8)


def lights(mats4, vis):
    off = (0.0, 0.0, 0.0)

    def k(L, on, f=1.0):
        return tuple(v * f for v in L) if on else off
    sunf = mats4['bd_day'][2, 2] if 'bd_day' in mats4 else 1.0         # the cloud factor rides on the backdrop's z scale
    Ls = []
    Ls.append(rect_light((WX0, D + 0.16, WZ0), (WX1 - WX0, 0, 0), (0, 0, WZ1 - WZ0), k(LSKY, True, 0.85 + 0.15 * sunf), always=1))  # 0 sky (-y)
    sc = np.array([(WX0 + WX1) / 2, D, (WZ0 + WZ1) / 2]) - SUN_DIR * 3.0
    Ls.append(spot_rect(tuple(sc), tuple(SUN_DIR), 0.06, k(LSUN, True, sunf), 0.0))                                      # 1 sun
    Ls.append(rect_light((0.15, 0.005, 0.3), (0, 0, 1.9), (1.85, 0, 0), k(LFILL, True), always=1))                       # 2 fill +y
    Ls.append(rect_light((W - 0.005, 0.08, 0.4), (0, 0, 1.6), (0, 0.75, 0), k(LFILL2, True)))                            # 3 fill -x
    Mb = mats4['bed']
    on_dl = bool(vis.get('bed_dl'))
    for (x, y) in DL:                                                                                                     # 4-7 downlights
        c = Mb @ np.array([x, y, Z_UP - 0.006, 1.0])
        Ls.append(spot_rect(tuple(c[:3]), (0, 0, -1), 0.05, k(LDOWN, on_dl), 4.0))
    Ls.append(rect_light((POSTS[1][0] - 0.012, POSTS[1][1] + 0.03, H - 0.054), (0, POSTS[3][1] - POSTS[1][1] - 0.06, 0), (0.024, 0, 0),
                         k(LRAIL, vis.get('rail_led'))))                                                                   # 8 rail LED (down)
    for nm, (x0, x1, y0, y1) in (('twS', TWS), ('twN', TWN)):                                                          # 9-10 shelf LEDs
        Ls.append(rect_light((x1 - 0.05, y0 + 0.04, 2.533), (0, y1 - y0 - 0.08, 0), (0.015, 0, 0), k(LSHELF, vis.get(f'{nm}_led'))))
    if vis.get('ns_lamp'):                                                                                                # 11 nightstand lamp
        c = mats4['ns_lamp'] @ np.array([0.62, 2.84, 0.92, 1.0])
        Ls.append(sphere_light(tuple(c[:3]), 0.022, k(LLAMP, vis.get('ns_bulb'))))
    else:
        Ls.append(sphere_light((0.62, 2.84, 0.92), 0.022, off))
    if vis.get('lamp'):                                                                                                   # 12 desk lamp
        c = mats4['lamp'] @ np.array([2.74, 2.77, 1.16, 1.0])
        Ls.append(sphere_light(tuple(c[:3]), 0.02, k(LLAMP, vis.get('lamp_on'))))
    else:
        Ls.append(sphere_light((2.74, 2.77, 1.16), 0.02, off))
    return Ls


# Blender (Cycles) look: see pipeline/blender_render.py
BLENDER = dict(
    exposure=-0.38,
    look='AgX - Medium High Contrast',
    translucent={'blind': 0.45},
    separate=['backdrop'],
    fill_lights=[2, 3],
    wood_scale=(55.0, 1.6),
    bake_rect={'backdrop': (-6.0, 9.0, -2.0, 6.0)},
    bake_px={'backdrop': 0.006, 'floor': 0.0015},
)


# ------------------------------------------------------------------------------------------- timeline helpers
I4 = np.eye(4)


class Kit:
    """Shared timeline helpers bound to one Timeline."""

    def __init__(self, tl):
        self.tl = tl

    def appear(self, name, t_on, t_off=None):
        self.tl.custom(name, lambda t: (I4, t >= t_on and (t_off is None or t < t_off)))

    def door(self, name, hinge, a_open, t_in, t_in1, t_close, dur=0.17, axis='z', base=None, open_again=None):
        """Pops in already open and swings shut; open_again = (t_open, t_close2) swings it open and shut once more."""
        hinge = np.array(hinge, float)
        tl = self.tl

        def ang(t):
            if t < t_close:
                return a_open
            u = (t - t_close) / dur
            if u < 1:
                return a_open * (1 - u * u)
            if open_again and t >= open_again[0]:
                to, tc = open_again
                if t < tc:
                    return a_open * eob(c01((t - to) / 0.30), 1.1)
                u2 = (t - tc) / dur
                return a_open * (1 - c01(u2) ** 2)
            tau = t - t_close - dur
            return math.copysign(math.radians(2.0), a_open) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))

        def f(t):
            if t < t_in:
                return I4, False
            B = base(t)[0] if base is not None else I4
            if t < t_in1:
                u = (t - t_in) / (t_in1 - t_in)
                s = 1.15 - 0.15 * eoc(u)
                return B @ T(0, 0, 0.12 * (1 - eoc(u))) @ about(hinge, R(axis, a_open) @ S(s, s, s)), True
            return B @ about(hinge, R(axis, ang(t))), True
        tl.custom(name, f)
        tl.ev(t_in1, name, 0.3, 'tick')
        tl.ev(t_close + dur, name + '_shut', 0.75, 'thud')
        return f

    def drawer(self, t_appear, t_open, t_close, off, base=None, out=0.10, shut=0.17):
        off = np.array(off, float)

        def f(t):
            if t < t_appear:
                return I4, False
            B = base(t)[0] if base is not None else I4
            if t < t_open:
                return B, True
            if t < t_close:
                return B @ T(*(off * eob((t - t_open) / out, 1.6))), True
            k = 1 - smooth((t - t_close) / shut)
            tau = t - t_close - shut
            wob = 0.006 * math.exp(-tau / 0.05) * math.sin(2 * math.pi * tau / 0.12) if tau > 0 else 0.0
            return B @ T(*(off * k + off / (np.linalg.norm(off) + 1e-9) * wob)), True
        return f


def bed_fn(t):
    if t < T_UP0:
        return I4, False
    dz = bed_dz(t)
    M = T(0, 0, dz)
    if t < T_UP0 + 0.10:                                  # pops onto the new floor
        s = 0.7 + 0.3 * smooth((t - T_UP0) / 0.10)
        M = M @ about(((BX0 + BX1) / 2, (BY0 + BY1) / 2, Z_UP), S(s, s, s))
    elif T_UP1 <= t < T_UP1 + 0.4:                        # the dock: a tiny settle up into the rail
        tau = t - T_UP1
        M = T(0, 0, -0.006 * math.exp(-tau / 0.06) * abs(math.sin(math.pi * tau / 0.09))) @ M
    return M, True


def common_fixed(tl, kit):
    """Pieces that ride on the bed."""
    tl.custom('bed', bed_fn)


# ------------------------------------------------------------------------------------------- 15 s timeline
def timeline_15(tl, kit):
    ev, drop, fly, slide, grow = tl.ev, tl.drop, tl.fly, tl.slide, tl.grow
    appear = kit.appear
    # ---- S1 (0.0-3.0): planks, the bed rises and docks, rail, posts, towers, motor, books, sofa
    for k in range(6):
        t1 = 0.16 + 0.06 * k
        drop(f'floor{k}', t1 - 0.14, t1, 0.55, 0.05, 0.3 + 0.03 * k, 'tick')
    tl.custom('bed', bed_fn)
    ev(T_UP0 + 0.1, 'bed_pop', 0.4, 'tick')
    ev(T_UP1, 'bed_dock', 1.0, 'clunk')
    slide('rail', 1.25, 1.40, (0.6, 0, 0), 1.0, 0.5, 'swish')
    land_posts(tl, 1.40, True)
    slide('twN', 1.85, 2.08, (0.55, 0, 0), 1.0, 0.8)
    slide('twS', 1.88, 2.10, (0.55, 0, 0), 1.0, 0.0, 'none')
    tl.custom('twN_led', lambda t: (I4, t >= 12.50))
    tl.custom('twS_led', lambda t: (I4, t >= 12.55))
    drop('motor', 2.00, 2.15, 0.25, 0.02, 0.45, 'tick')
    cam = np.array(S1[0]['pos'])
    rows = [('twN', s) for s in range(7)] + [('twS', s) for s in (1, 2, 4, 5, 6)]
    for i, (nm, si) in enumerate(rows):
        t0 = 2.10 + 0.028 * i
        fly(f'bk_{nm}{si}', t0, t0 + 0.14, (0.35, 0, 0.05), 0.04, 0.25 if i % 3 == 0 else 0.0, 'riffle' if i % 3 == 0 else 'none')
    drop('tw_plant', 2.50, 2.64, 0.25, 0.06, 0.3)
    drop('sofa', 2.40, 2.55, 0.40, 0.02, 0.8, 'thud')
    for k in range(2):
        drop(f'sofa_lid{k}', 2.74 + 0.08 * k, 2.85 + 0.08 * k, 0.30, 0.05, 0.45, 'thud' if k == 0 else 'none')
    for k in range(3):
        slide(f'pad{k}', 2.55 + 0.05 * k, 2.68 + 0.05 * k, (0.35, 0, 0), 1.0, 0.35, 'tick')
    for nm in ('sofa_games', 'sofa_throws', 'ot_items', 'rug'):
        tl.custom(nm, lambda t: (I4, False))
    drop('spil0', 2.90, 3.02, 0.30, 0.08, 0.3)
    drop('spil1', 2.96, 3.08, 0.30, 0.08, 0.0, 'none')
    drop('ottoman', 2.88, 3.00, 0.35, 0.04, 0.5, 'thud')
    drop('ottoman_lid', 2.88, 3.00, 0.35, 0.04, 0.0, 'none')
    # ---- S2 (3.3-7.0): wardrobe, tee drawer, fronts, desk, pedestal drawer, chair, laptop, lamp
    slide('wr_body', 3.16, 3.32, (0.60, 0, 0), 1.0, 0.9)
    slide('pegs', 3.48, 3.60, (0, 0.25, 0), 1.0, 0.3, 'tick')
    fly('coat', 3.58, 3.76, (0.0, 0.35, 0.10), 0.05, 0.3, 'swish')
    fly('tote', 3.66, 3.82, (0.0, 0.35, 0.10), 0.05, 0.25, 'tick')
    slide('wr_cl', 3.70, 4.02, (0, -0.75, 0), 1.0, 0.4, 'swish')
    slide('wr_shoe', 3.86, 4.00, (-0.30, 0, 0), 1.0, 0.3, 'tick')
    slide('wr_drs', 3.48, 3.62, (-0.35, 0, 0), 1.0, 0.4, 'tick')
    fd = kit.drawer(3.48, 4.12, 4.62, (-0.36, 0, 0), base=lambda t: (T(-0.35 * (1 - eob(c01((t - 3.48) / 0.14), 1.0)), 0, 0) if t < 3.62 else I4, True))
    tl.custom('wr_dr', fd)
    ev(4.15, 'wr_dr_open', 0.6, 'swish'); ev(4.79, 'wr_dr_shut', 0.8, 'thud')
    drop('wr_tees', 4.28, 4.48, 0.30, 0.04, 0.35, parent=fd)
    for k in range(3):
        drop(f'wr_fold{k}', 4.30 + 0.09 * k, 4.44 + 0.09 * k, 0.25, 0.04, 0.3 if k == 1 else 0.0, 'tick' if k == 1 else 'none')
    tl.custom('iron', lambda t: (I4, t >= 3.45))
    tl.custom('iron_leg', lambda t: (I4, t >= 3.45))
    slide('wr_oak', 4.80, 4.96, (0, -0.62, 0), 1.0, 0.6, 'thud')
    slide('wr_mir', 4.92, 5.10, (0, 0.62, 0), 1.0, 0.7, 'thud')
    slide('desk', 5.10, 5.25, (0, 0.55, 0), 1.0, 0.8)
    drop('ped', 5.30, 5.45, 0.40, 0.02, 0.6, 'thud')
    drop('ped_fixed', 5.30, 5.45, 0.40, 0.02, 0.0, 'none')
    ped_base = tl.anims['ped']
    fp = kit.drawer(5.30, 5.58, 6.02, (0, -0.30, 0), base=lambda t: (ped_base(t)[0], True))
    tl.custom('ped_dr', fp)
    ev(5.62, 'ped_open', 0.6, 'swish'); ev(6.19, 'ped_shut', 0.8, 'thud')
    drop('ped_items', 5.74, 5.92, 0.28, 0.04, 0.35, parent=fp)
    ch_c = tl.cen['chair']
    ch_start = np.array([1.80, 2.05, ch_c[2]])

    def chair(t, t0=6.02, t1=6.35):
        if t < t0:
            return I4, False
        u = (t - t0) / (t1 - t0)
        if u < 1:
            off = (1 - eoc(u)) * (ch_start - ch_c)
            ang = math.radians(150) * (1 - eob(u, 1.2))
        else:
            off = np.zeros(3)
            ang = math.radians(5) * math.exp(-(t - t1) / 0.12) * math.sin(2 * math.pi * (t - t1) / 0.3)
        return T(*off) @ about(ch_c, R('z', ang)), True
    tl.custom('chair', chair)
    ev(6.35, 'chair', 0.8, 'thud')
    drop('laptop', 6.40, 6.55, 0.30, 0.03, 0.4)
    drop('lid', 6.40, 6.55, 0.30, 0.03, 0.0, 'none')
    drop('lamp', 6.55, 6.70, 0.35, 0.05, 0.4)
    drop('mug', 6.70, 6.82, 0.25, 0.06, 0.3)
    drop('dplant', 6.80, 6.94, 0.25, 0.06, 0.3)
    appear('blind_roll', 0.0)
    appear('blind', 0.0)
    # ---- S3 (7.3-10.7): the ride
    fig_rig(tl, [
        dict(t=7.30, kind='pop', at=(1.88, 2.24, -49)),
        dict(t=7.42, kind='pose', pose='stand'),
        dict(t=7.62, kind='pose', pose=PRESS),
        dict(t=7.74, kind='pose', pose=PRESS),
        dict(t=8.15, kind='walk', to=(1.86, 1.95, -45), pose=LOOKUP),
        dict(t=10.40, kind='pose', pose=LOOKUP),
        dict(t=10.85, kind='sit', at=(1.36, 2.08, 92), seat=BED_SEAT),
    ])
    ev(7.65, 'button', 0.35, 'bip')
    tl.custom('bed_dl', lambda t: (bed_fn(t)[0], 7.85 <= t < T_DN1 + 0.05))
    ev(7.85, 'downlights', 0.3, 'chime')
    tl.events.append(dict(t=T_DN0, name='hum', strength=0.0, kind='hum', dur=T_DN1 - T_DN0))
    ev(T_DN1, 'bed_land', 1.0, 'deep')

    def straps(t):
        if t < T_UP0:
            return I4, False
        B = bed_fn(t)[0]
        if t < 10.25:
            return B, True
        u = c01((t - 10.25) / 0.18)
        return B @ about((BX1, 0, Z_UP + 0.26), S(1 - 0.98 * eoc(u), 1, 1)), u < 1
    tl.custom('bed_straps', straps)
    ev(10.25, 'straps', 0.4, 'tick')

    def pillows(t):
        if t < T_UP0:
            return I4, False
        B = bed_fn(t)[0]
        tau = t - 10.30
        z = 0.06 * math.exp(-tau / 0.10) * abs(math.sin(math.pi * tau / 0.16)) if tau > 0 else 0.0
        return B @ T(0, 0, z), True
    tl.custom('bed_pillows', pillows)
    ev(10.35, 'pillows', 0.4, 'boing')
    # ---- S4 (11.0-15.0): bed drawer, nightstand, cloud, lights on, drift back to frame 1
    fb = kit.drawer(T_UP0, 11.10, 11.42, (0.40, 0, 0), base=bed_fn)
    tl.custom('bed_drawer', fb)
    ev(11.15, 'bed_dr_open', 0.6, 'swish'); ev(11.59, 'bed_dr_shut', 0.8, 'thud')
    for nm, t0 in (('bd_pj', 11.20), ('bd_book', 11.27), ('bd_mask', 11.32)):
        drop(nm, t0, t0 + 0.10, 0.22, 0.04, 0.3 if nm == 'bd_pj' else 0.0, 'tick' if nm == 'bd_pj' else 'none', parent=fb)
    hinge = (TWN[1], 0, 0.665)
    kit_flip(tl, 'nstand', hinge, 11.45, 11.62)
    drop('ns_lamp', 11.68, 11.80, 0.25, 0.05, 0.35)
    drop('ns_phone', 11.82, 11.92, 0.20, 0.05, 0.3)
    drop('ns_mug', 11.95, 12.05, 0.20, 0.05, 0.3)
    tl.custom('bd_day', lambda t: (S(1, 1, cloud(t)), True))
    ev(12.0, 'cloud', 0.0, 'none')
    appear('rail_led', 12.20); ev(12.20, 'rail_on', 0.6, 'chime')
    ev(12.50, 'shelf_on', 0.35, 'tick')
    appear('ns_bulb', 12.80); ev(12.80, 'ns_lamp_on', 0.4, 'tick')
    appear('lamp_on', 13.10); ev(13.10, 'desk_lamp_on', 0.4, 'tick')
    appear('ns_glow', 13.40); ev(13.40, 'phone_glow', 0.3, 'bip')


def land_posts(tl, t0, fitted):
    """The four posts swing in whole from the room side (one rigid piece each) and land with a steel tink."""
    for k, nm in enumerate(('post2', 'post0', 'post3', 'post1')):
        a = t0 + 0.07 * k
        tl.fly(nm, a, a + 0.18, (0.45, 0, 0.0), 0.10, 0.45, 'tink')
    if fitted:
        tl.custom('btnpad', lambda t, f=tl.anims['post3']: f(t))
        tl.custom('crank', lambda t, f=tl.anims['post1']: f(t))


def kit_flip(tl, name, hinge, t0, t1):
    """Nightstand flap: flips down out of the tower face about a y-axis hinge at its inner bottom edge."""
    hinge = np.array(hinge, float)

    def f(t):
        if t < t0:
            return I4, False
        u = (t - t0) / (t1 - t0)
        a = math.radians(-90) * (1 - eob(u, 1.4)) if u < 1 else 0.0
        return about(hinge, R('y', a)), True
    tl.custom(name, f)
    tl.ev(t1, name, 0.55, 'thud')


# ------------------------------------------------------------------------------------------- the stand-in
PRESS = dict(sh_r=62, sh_r_out=4, elbow_r=12, sh_l_out=6, elbow_l=10, spine=4, neck=4)
LOOKUP = dict(sh_l_out=6, sh_r_out=6, elbow_l=10, elbow_r=10, neck=-26, spine=-4)
BED_SEAT = Z_UP - BED_DROP + 0.235


def fig_rig(tl, keys):
    """Drive the stand-in from keys (time-ordered dicts). kinds:
    pop (at): pops in standing | show (at, pose): appears | hide: disappears | pose (pose): eases into a pose in place
    walk (to, pose): walks from the previous spot to `to` (x, y, yaw), arriving in `pose` | sit (at, seat): sits (instantly
    unless sit_from is given) | stand (at): stands up in place."""
    keys = sorted(keys, key=lambda k: k['t'])
    pop_t = next((k['t'] for k in keys if k['kind'] == 'pop'), None)
    # resolve the state after each key: (at, pose, seat, visible)
    states = []
    at, pose, seat, vis = keys[0].get('at', (0, 0, 0)), 'stand', None, False
    for k in keys:
        kd = k['kind']
        if kd in ('pop', 'show'):
            at, pose, seat, vis = k['at'], k.get('pose', 'stand'), None, True
        elif kd == 'hide':
            vis = False
        elif kd == 'pose':
            pose = k['pose']
        elif kd == 'walk':
            at, pose, seat = k['to'], k.get('pose', 'stand'), None
        elif kd == 'sit':
            at, pose, seat = k['at'], FIG.sit_pose(k['seat']), k['seat']
        elif kd == 'stand':
            at, pose, seat = k.get('at', at), k.get('pose', 'stand'), None
        states.append((at, pose, seat, vis))

    def idx(t):
        i = -1
        for j, k in enumerate(keys):
            if k['t'] <= t:
                i = j
        return i

    def blend(t):
        i = idx(t)
        if i < 0:
            return states[0][0], 'stand', None, False
        at, pose, seat, vis = states[i]
        if i + 1 < len(keys):
            k = keys[i + 1]
            t0, t1 = keys[i]['t'], k['t']
            u = c01((t - t0) / max(1e-6, t1 - t0))
            if k['kind'] == 'walk':
                to = k['to']
                e = smooth(u)
                dyaw = (to[2] - at[2] + 180) % 360 - 180
                d = math.hypot(to[0] - at[0], to[1] - at[1])
                p = (at[0] + (to[0] - at[0]) * e, at[1] + (to[1] - at[1]) * e, at[2] + dyaw * e)
                amt = smooth(min(u, 1 - u) * 5) if d > 0.05 else 0.0
                q = fg.lerp_pose(fg.lerp_pose(pose, k.get('pose', 'stand'), e), fg.walk_pose(e * d / 1.25), amt)
                return p, q, None, vis
            if k['kind'] == 'pose':
                return at, fg.lerp_pose(pose, k['pose'], smooth(u)), seat, vis
        return at, pose, seat, vis

    cache = {}

    def st(t):
        if t not in cache:
            if len(cache) > 32:
                cache.clear()
            cache[t] = blend(t)
        return cache[t]
    FIG.animate(tl, pose=lambda t: fg.pose_of(st(t)[1]), at=lambda t: st(t)[0], seat=lambda t: st(t)[2],
                visible=lambda t: st(t)[3], pop=pop_t, sound=0.3)


# ------------------------------------------------------------------------------------------- rest probe
def timeline_rest(tl, kit):
    hide = lambda t: (I4, False)
    for nm in ('bed_dl', 'rail_led', 'twS_led', 'twN_led', 'ns_bulb', 'lamp_on', 'sofa_games', 'sofa_throws', 'ot_items', 'ns_glow'):
        tl.custom(nm, hide)
    FIG.animate(tl, visible=False)


def timeline():
    tl = Timeline(rk, FPS)
    kit = Kit(tl)
    if REST:
        timeline_rest(tl, kit)
    elif LONG:
        timeline_long(tl, kit)
    else:
        timeline_15(tl, kit)
    return tl


def timeline_long(tl, kit):
    ev, drop, fly, slide, grow = tl.ev, tl.drop, tl.fly, tl.slide, tl.grow
    appear = kit.appear
    hide = lambda t: (I4, False)
    # ---- L1 (0.0-3.0): planks, the bed rises and docks, rail, posts, towers, motor, first shelf of books
    for k in range(6):
        t1 = 0.16 + 0.06 * k
        drop(f'floor{k}', t1 - 0.14, t1, 0.55, 0.05, 0.3 + 0.03 * k, 'tick')
    tl.custom('bed', bed_fn)
    ev(T_UP0 + 0.1, 'bed_pop', 0.4, 'tick')
    ev(T_UP1, 'bed_dock', 1.0, 'clunk')
    slide('rail', 1.25, 1.40, (0.6, 0, 0), 1.0, 0.5, 'swish')
    land_posts(tl, 1.40, False)
    slide('twN', 1.62, 1.84, (0.55, 0, 0), 1.0, 0.8)
    slide('twS', 1.70, 1.92, (0.55, 0, 0), 1.0, 0.5)
    drop('motor', 2.26, 2.40, 0.25, 0.02, 0.45, 'tick')
    fly('bk_twN0', 2.36, 2.50, (0.35, 0, 0.05), 0.04, 0.3, 'riffle')
    fly('bk_twN1', 2.62, 2.76, (0.35, 0, 0.05), 0.04, 0.3, 'riffle')
    # ---- L2 (3.3-6.6): books shelf by shelf (south tower first, then north), crank socket, button pad
    rows = [('twS', s_) for s_ in (1, 2, 4, 5, 6)] + [('twN', s_) for s_ in (2, 3, 4, 5, 6)]
    for i, (nm, si) in enumerate(rows):
        t1 = 3.55 + 0.22 * i
        fly(f'bk_{nm}{si}', t1 - 0.14, t1, (0.35, 0, 0.05), 0.04, 0.3, 'riffle')
    drop('tw_plant', 5.70, 5.84, 0.25, 0.06, 0.3)
    fly('crank', 5.76, 5.90, (0.30, 0, 0.02), 0.03, 0.4, 'tink')
    fly('btnpad', 6.06, 6.20, (0.30, 0, 0.02), 0.03, 0.4, 'tink')
    # ---- L3 (6.9-10.2): sofa box, wall pads, lids (cushions); lids lift, games + throws, lids shut
    drop('sofa', 6.85, 7.00, 0.40, 0.02, 0.8, 'thud')
    for k in range(3):
        slide(f'pad{k}', 7.18 + 0.12 * k, 7.30 + 0.12 * k, (0.35, 0, 0), 1.0, 0.35, 'tick')
    for k in range(2):
        hinge = np.array([0.10, 0, 0.30])
        t_in, t_l = 7.66 + 0.08 * k, 7.80 + 0.08 * k

        def lid(t, t_in=t_in, t_l=t_l, k=k, hinge=hinge):
            if t < t_in:
                return I4, False
            if t < t_l:
                u = (t - t_in) / (t_l - t_in)
                return T(0, 0, 0.3 * (1 - u * u)), True
            if t < 8.15 + 0.06 * k:
                return I4, True
            if t < 9.55:
                a = math.radians(-58) * eob(c01((t - 8.15 - 0.06 * k) / 0.35), 0.6)
            else:
                a = math.radians(-58) * (1 - smooth(c01((t - 9.55 - 0.05 * k) / 0.22)))
            return about(hinge, R('y', a)), True
        tl.custom(f'sofa_lid{k}', lid)
    ev(7.80, 'lids', 0.6, 'thud'); ev(8.20, 'struts', 0.4, 'swish'); ev(9.80, 'lids_shut', 0.7, 'thud')
    drop('sofa_games', 8.40, 8.62, 0.45, 0.04, 0.4)
    tl.custom('sofa_games', lambda t, f=tl.anims['sofa_games']: f(t) if t < 8.62 else (I4, True))
    for k, nm in enumerate(('sofa_games',)):
        pass
    drop('sofa_throws', 8.95, 9.20, 0.45, 0.06, 0.4, 'swish')
    # ---- L4 (10.5-13.4): pillows, ottoman rolls in (lid lifts on slippers + throw), rug, plant
    drop('spil0', 10.48, 10.60, 0.30, 0.08, 0.35)
    drop('spil1', 10.68, 10.80, 0.30, 0.08, 0.35)
    OT = np.array([1.05 - 1.10, 1.50 - 2.79, 0.0])           # day spot in front of the sofa (built in the alcove)

    def ottoman(t, lid=False):
        if t < 10.70:
            return I4, False
        if t < 11.00:
            u = eoc((t - 10.70) / 0.30)
            return T(*(OT + np.array([0.9 * (1 - u), 0, 0]))), True
        if t < 24.30:
            M = T(*OT)
        elif t < 24.60:
            M = T(*(OT * (1 - smooth((t - 24.30) / 0.30))))
        else:
            M = I4
        if lid and 11.35 <= t < 12.45:
            hz = np.array([0.90, 0, 0.45])
            a = math.radians(-70) * eob(c01((t - 11.35) / 0.25), 0.8) if t < 12.20 else math.radians(-70) * (1 - smooth(c01((t - 12.20) / 0.2)))
            M = M @ about(hz, R('y', a))
        return M, True
    tl.custom('ottoman', ottoman)
    tl.custom('ottoman_lid', lambda t: ottoman(t, True))
    ev(11.0, 'ottoman', 0.6, 'thud'); ev(11.42, 'ot_open', 0.4, 'swish'); ev(12.40, 'ot_shut', 0.6, 'thud'); ev(24.6, 'ot_park', 0.4, 'thud')
    ot_items_drop = drop('ot_items', 11.55, 11.75, 0.30, 0.04, 0.3)
    tl.custom('ot_items', lambda t: (ottoman(t)[0] @ ot_items_drop(t)[0], ot_items_drop(t)[1]))
    drop('rug', 12.48, 12.62, 0.25, 0.02, 0.5, 'swish')
    tl.custom('dplant', lambda t, f=drop('dplant', 12.88, 13.00, 0.25, 0.06, 0.3): f(t))
    # ---- L5 (13.7-16.6): downlights blink twice (tease), crane up past the mechanism
    tl.custom('bed_dl', lambda t: (bed_fn(t)[0], (14.40 <= t < 14.58) or (14.72 <= t < 14.90) or (26.40 <= t < T_DN1 + 0.05)
                                    or (44.60 <= t < T_RE1 + 0.3)))
    ev(14.40, 'tease', 0.3, 'bip')
    # ---- L6 (16.9-20.1): desk, pedestal drawers cascade, laptop, lamp, mug, chair
    slide('desk', 16.85, 17.00, (0, 0.55, 0), 1.0, 0.8)
    drop('ped', 17.15, 17.30, 0.40, 0.02, 0.6, 'thud')
    drop('ped_fixed', 17.15, 17.30, 0.40, 0.02, 0.0, 'none')
    ped_base = tl.anims['ped']
    fp = kit.drawer(17.15, 17.60, 18.30, (0, -0.30, 0), base=lambda t: (ped_base(t)[0], True))
    tl.custom('ped_dr', fp)
    ev(17.65, 'ped_open', 0.6, 'swish'); ev(18.47, 'ped_shut', 0.8, 'thud')
    drop('ped_items', 17.80, 18.00, 0.28, 0.04, 0.35, parent=fp)
    ev(18.65, 'ped2', 0.5, 'swish'); ev(18.95, 'ped3', 0.6, 'thud')
    drop('laptop', 19.05, 19.20, 0.30, 0.03, 0.4)
    lid_drop = drop('lid', 19.05, 19.20, 0.30, 0.03, 0.0, 'none')
    drop('lamp', 19.30, 19.45, 0.35, 0.05, 0.4)
    drop('mug', 19.58, 19.70, 0.25, 0.06, 0.3)
    hinge_l = np.array([0, 2.825, DESK[3] + 0.013])

    def lid(t):
        if t < 21.70:
            return lid_drop(t)
        return about(hinge_l, R('x', math.radians(-102) * eob(c01((t - 21.70) / 0.32), 0.6))), True
    tl.custom('lid', lid)
    ev(21.75, 'lid_open', 0.4, 'swish')
    ch_c = tl.cen['chair']

    def chair(t):
        if t < 19.55:
            return I4, False
        if t < 19.90:
            u = (t - 19.55) / 0.35
            off = (1 - eoc(u)) * np.array([-0.5, -0.9, 0.0])
            return T(*off) @ about(ch_c, R('z', math.radians(150) * (1 - eob(u, 1.2)))), True
        if t < 21.15:
            return I4, True
        if t < 24.05:
            return T(0, -0.28 * smooth((t - 21.15) / 0.25), 0), True
        return T(0, -0.28 * (1 - smooth((t - 24.05) / 0.25)), 0), True
    tl.custom('chair', chair)
    ev(19.90, 'chair', 0.8, 'thud'); ev(24.30, 'chair_in', 0.5, 'thud')
    # ---- L7 (20.4-23.4): stand-in walks in and sits at the desk, laptop opens, blind rolls up
    tl.custom('blind_roll', lambda t: (I4, t >= 17.30))
    ev(17.30, 'blind', 0.2, 'tick')

    def blind(t):
        if t < 17.30:
            return I4, False
        if t < 22.30:
            return I4, True
        u = smooth((t - 22.30) / 0.45)
        return about((0, 0, WZ1 + 0.07), S(1, 1, 1 - 0.85 * u)), True
    tl.custom('blind', blind)
    ev(22.75, 'blind_up', 0.4, 'swish')
    # ---- L8 (23.7-26.8): stands, chair in, ottoman parks, pillows hop into the cubby, button, downlights
    cub = {'spil0': (0.12, 0.21, 1.31), 'spil1': (0.28, 0.21, 1.31)}
    for nm, t0 in (('spil0', 24.70), ('spil1', 24.90)):
        base = tl.anims[nm]
        c0 = tl.cen[nm]
        c1 = np.array(cub[nm])

        def hop(t, base=base, c0=c0, c1=c1, t0=t0):
            if t < t0:
                return base(t)
            u = c01((t - t0) / 0.22)
            e = eoc(u)
            p = c0 + (c1 - c0) * e + np.array([0, 0, 0.35 * math.sin(math.pi * u)])
            s_ = 1 - 0.25 * e
            return T(*(p - c0)) @ about(c0, R('z', 0.0) @ S(s_, s_, s_)), True
        tl.custom(nm, hop)
        ev(t0 + 0.22, nm + '_hop', 0.35, 'boing' if nm == 'spil1' else 'tick')
    ev(25.80, 'button', 0.35, 'bip')
    ev(26.40, 'downlights', 0.3, 'chime')
    # ---- L9 (27.1-31.0): the ride
    tl.events.append(dict(t=T_DN0, name='hum', strength=0.0, kind='hum', dur=T_DN1 - T_DN0))
    ev(T_DN1, 'bed_land', 1.0, 'deep')
    tl.events.append(dict(t=T_RE0, name='hum2', strength=0.0, kind='hum', dur=T_RE1 - T_RE0))
    ev(T_RE1, 'bed_dock2', 0.45, 'clunk')

    def straps(t):
        if t < T_UP0:
            return I4, False
        B = bed_fn(t)[0]
        if t < 30.10:
            return B, True
        if t < 44.20:
            u = c01((t - 30.10) / 0.18)
        else:
            u = 1 - c01((t - 44.20) / 0.20)
        return B @ about((BX1, 0, Z_UP + 0.26), S(1 - 0.98 * eoc(u), 1, 1)), u < 1
    tl.custom('bed_straps', straps)
    ev(30.10, 'straps', 0.4, 'tick'); ev(44.40, 'straps_on', 0.3, 'tick')

    def pillows(t):
        if t < T_UP0:
            return I4, False
        tau = t - 30.15
        z = 0.06 * math.exp(-tau / 0.10) * abs(math.sin(math.pi * tau / 0.16)) if tau > 0 else 0.0
        return bed_fn(t)[0] @ T(0, 0, z), True
    tl.custom('bed_pillows', pillows)
    ev(30.20, 'pillows', 0.4, 'boing')
    # ---- L10 (31.3-34.4): bed drawer, stand-in sits on the bed edge
    fb = kit.drawer(T_UP0, 31.45, 32.30, (0.40, 0, 0), base=bed_fn)
    tl.custom('bed_drawer', fb)
    ev(31.50, 'bed_dr_open', 0.6, 'swish'); ev(32.47, 'bed_dr_shut', 0.8, 'thud')
    for nm, t0 in (('bd_pj', 31.62), ('bd_book', 31.86), ('bd_mask', 32.06)):
        drop(nm, t0, t0 + 0.12, 0.22, 0.04, 0.3, 'tick', parent=fb)
    # ---- L11 (34.7-37.5): nightstand, lamp, phone, mug, phone glow
    kit_flip(tl, 'nstand', (TWN[1], 0, 0.665), 34.75, 34.92)
    drop('ns_lamp', 35.10, 35.22, 0.25, 0.05, 0.35)
    drop('ns_phone', 35.32, 35.42, 0.20, 0.05, 0.3)
    drop('ns_mug', 35.50, 35.60, 0.20, 0.05, 0.3)
    appear('ns_glow', 35.90, 37.6); ev(35.90, 'glow', 0.3, 'bip')
    # ---- L12 (37.8-40.9): wardrobe carcass, garments, tee drawer, folded stacks, mirror front
    slide('wr_body', 37.75, 37.90, (0.60, 0, 0), 1.0, 0.9)
    tl.custom('iron', lambda t: iron_fn(t))
    tl.custom('iron_leg', lambda t: iron_leg_fn(t))
    slide('wr_drs', 37.95, 38.10, (-0.35, 0, 0), 1.0, 0.4, 'tick')
    slide('wr_cl', 38.25, 38.80, (0, -0.75, 0), 1.0, 0.4, 'swish')
    slide('wr_shoe', 38.55, 38.70, (-0.30, 0, 0), 1.0, 0.3, 'tick')
    fd = kit.drawer(37.95, 39.00, 39.62, (-0.36, 0, 0), base=lambda t: (T(-0.35 * (1 - eob(c01((t - 37.95) / 0.15), 1.0)), 0, 0) if t < 38.10 else I4, True))
    tl.custom('wr_dr', fd)
    ev(39.03, 'wr_dr_open', 0.6, 'swish'); ev(39.79, 'wr_dr_shut', 0.8, 'thud')
    drop('wr_tees', 39.18, 39.40, 0.30, 0.04, 0.35, parent=fd)
    for k in range(3):
        drop(f'wr_fold{k}', 40.00 + 0.18 * k, 40.14 + 0.18 * k, 0.25, 0.04, 0.3)
    mir_in = slide('wr_mir', 40.55, 40.72, (0, 0.62, 0), 1.0, 0.7, 'thud')

    def mir(t):
        if t < 42.95:
            return mir_in(t)
        return T(0, 0.70 * smooth((t - 42.95) / 0.30), 0), True     # slides back over the north section
    tl.custom('wr_mir', mir)
    ev(43.25, 'mir_back', 0.5, 'swish')
    def oak(t):                                          # lands over the hanging section once the mirror has slid back
        if t < 43.70:
            return I4, False
        u = c01((t - 43.70) / 0.18)
        return T(0, -0.70, 0.30 * (1 - u * u)), True
    tl.custom('wr_oak', oak)
    ev(43.88, 'oak_front', 0.7, 'thud')
    # ---- L13 (41.2-44.0): ironing board down and up, shoe pull-out out and back
    ev(42.35, 'board_down', 0.6, 'thud'); ev(42.95, 'board_up', 0.6, 'thud')
    shoe_in = tl.anims['wr_shoe']

    def shoe(t):
        if t < 43.10:
            return shoe_in(t)
        if t < 43.60:
            return T(-0.42 * eob(c01((t - 43.10) / 0.25), 0.8), 0, 0), True
        return T(-0.42 * (1 - smooth(c01((t - 43.60) / 0.25))), 0, 0), True
    tl.custom('wr_shoe', shoe)
    ev(43.15, 'shoe_out', 0.5, 'swish'); ev(43.85, 'shoe_in', 0.6, 'thud')
    # ---- L14 (44.3-47.2) / L15 (47.5-49.5): button, downlights, the bed rises, lights on
    ev(44.40, 'button2', 0.35, 'bip')
    ev(44.60, 'downlights2', 0.3, 'chime')
    appear('rail_led', 47.50); ev(47.50, 'rail_on', 0.6, 'chime')
    appear('twN_led', 47.58); appear('twS_led', 47.62)
    appear('lamp_on', 47.70); appear('ns_bulb', 47.80); ev(47.75, 'lamps_on', 0.4, 'tick')
    # ---- the stand-in
    fig_rig(tl, [
        dict(t=20.40, kind='show', at=(2.45, 0.25, 0)),
        dict(t=21.30, kind='walk', to=(2.45, 2.10, 0)),
        dict(t=21.40, kind='sit', at=(2.45, 2.30, 0), seat=0.505),
        dict(t=23.80, kind='stand', at=(2.45, 2.08, 0)),
        dict(t=24.05, kind='pose', pose=dict(sh_l=60, sh_r=60, elbow_l=20, elbow_r=20, spine=14)),
        dict(t=24.35, kind='pose', pose='stand'),
        dict(t=25.45, kind='walk', to=(1.88, 2.24, -49)),
        dict(t=25.72, kind='pose', pose=PRESS),
        dict(t=25.86, kind='pose', pose=PRESS),
        dict(t=26.15, kind='walk', to=(1.66, 1.55, -45), pose=LOOKUP),
        dict(t=30.40, kind='pose', pose=LOOKUP),
        dict(t=30.80, kind='pose', pose='stand'),
        dict(t=31.40, kind='walk', to=(2.10, 2.35, -45)),
        dict(t=33.60, kind='pose', pose='stand'),
        dict(t=34.40, kind='walk', to=(1.80, 1.40, 92)),
        dict(t=34.50, kind='sit', at=(1.36, 1.40, 92), seat=BED_SEAT),
        dict(t=37.60, kind='hide'),
        dict(t=41.20, kind='show', at=(1.95, 0.45, 0)),
        dict(t=42.00, kind='walk', to=(2.05, 1.70, -10)),
        dict(t=42.20, kind='pose', pose=dict(sh_r=70, elbow_r=30, sh_l=50, elbow_l=40, spine=10, neck=10)),
        dict(t=42.55, kind='pose', pose=dict(sh_r=40, elbow_r=40, sh_l=30, elbow_l=40, spine=8, neck=16)),
        dict(t=42.85, kind='pose', pose=dict(sh_r=70, elbow_r=30, sh_l=50, elbow_l=40, spine=10, neck=10)),
        dict(t=43.10, kind='pose', pose='stand'),
        dict(t=44.15, kind='walk', to=(1.88, 2.24, -49)),
        dict(t=44.30, kind='pose', pose=PRESS),
        dict(t=44.42, kind='pose', pose=PRESS),
        dict(t=44.70, kind='walk', to=(1.66, 1.55, -45), pose=LOOKUP),
        dict(t=47.30, kind='pose', pose=LOOKUP),
        dict(t=47.90, kind='pose', pose='stand'),
    ])


IRON_H = np.array([WR[0] + 0.115, 0, 0.85])          # ironing board hinge (bottom of the stored board)


def iron_angle(t):
    if not LONG or t < 42.20:
        return 0.0
    if t < 42.80:
        return math.radians(-90) * smooth(c01((t - 42.20) / 0.25))
    return math.radians(-90) * (1 - smooth(c01((t - 42.80) / 0.25)))


def iron_fn(t):
    vis = t >= (37.75 if LONG else 3.45)
    return about(IRON_H, R('y', iron_angle(t))), vis


def iron_leg_fn(t):
    M, v = iron_fn(t)
    a = iron_angle(t) / math.radians(-90)
    piv = np.array(M @ np.array([WR[0] + 0.14, 0, 1.55, 1.0]))[:3]
    return about(piv, R('y', math.radians(90) * smooth(c01((a - 0.5) / 0.5)))) @ M, v


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    json.dump({'bpm': 118}, open(os.path.join(out, 'music.json'), 'w'))
    timeline().export(DUR, camera, lights, out)
