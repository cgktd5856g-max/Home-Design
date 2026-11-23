"""Dinner for Eight: an 11.5 m² kitchen (3.2 x 3.6 m) whose slim island unfolds into a table for eight, with eight
folding chairs (seats matching eight coloured plates) hopping out of a plain oak wall. White + light oak + clay.
No on-screen text.

    ROOM_REST=1 python3 ../../pipeline/run.py project.py <workdir> probe 0.5,1.5,2.5,3.5      # finished room, stations
    python3 ../../pipeline/run.py project.py <workdir> preview                                 # code-renderer preview
    ROOM_CUT=long ...                                                                          # the 46 s long cut
    /root/bpyenv/bin/python ../../pipeline/blender_render.py project.py <outdir> --size 720x1280 ...

Units: metres. x = east, y = north, z = up. Room x 0..W, y 0..D, z 0..H.
West wall (x=0): the whole kitchen run. East wall: flush oak panels (broom cupboard, chair wall, open shelves).
North wall: window centred on the table. South wall: doorway on the same centre line.
"""
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'pipeline'))
import roomkit as rk
from roomkit import (srgb, mat, add, box, lathe, rprof, tube, ellipsoid, rbox, T, S, R, about, xform, wood,
                     wood_mats, rect_light, sphere_light, spot_rect)
from animkit import Timeline, c01, eoc, eob, smooth
from camkit import hold_camera
import figure as fg

REST = os.environ.get('ROOM_REST') == '1'
REST_LIT = os.environ.get('ROOM_LIT') == '1'
LONG = os.environ.get('ROOM_CUT') == 'long'

W, D, H = 3.2, 3.6, 2.6
FPS = 25
DUR = 6.0 if REST else (46.0 if LONG else 15.0)
CAPTIONS = []

# ---- layout
FX = 0.60            # base front plane (west run)
WT = 0.62            # worktop front edge
WZ = 0.90            # worktop top
UZ0, UX = 1.45, 0.35  # uppers bottom, depth
EX = 3.05            # east panel wall front plane
DX0, DX1 = 1.45, 2.30  # doorway (south) and table x span
TCX = (DX0 + DX1) / 2  # table centre line x = 1.875
WIN = (1.275, 2.475, 0.95, 2.25)  # north window x0, x1, z0, z1
TZ = 0.76            # table top
TY0, TY1 = 0.80, 2.80  # extended table y span
CY = 1.80            # table centre y
# west run, south to north
Y_PAN, Y_FR, Y_SINK, Y_DW, Y_DIN, Y_OV, Y_SP = 0.0, 0.45, 1.05, 1.65, 2.10, 2.70, 3.40
SIDE_Y = (1.13, 1.80, 2.47)

GLAZES = [('g_sage', (146, 170, 138)), ('g_celery', (196, 208, 140)), ('g_blue', (132, 160, 192)),
          ('g_slate', (104, 118, 134)), ('g_clay', (200, 128, 98)), ('g_ochre', (220, 170, 72)),
          ('g_plum', (150, 122, 140)), ('g_butter', (240, 220, 140))]

# eight places, clockwise from the north end (seen from above): (plate x, y, chair origin x, y, chair yaw deg)
PLACES = [(TCX, 2.63, TCX, 3.08, 180.0)]
PLACES += [(2.13, y, 2.57, y, 90.0) for y in (2.47, 1.80, 1.13)]
PLACES += [(TCX, 0.97, TCX, 0.52, 0.0)]
PLACES += [(1.62, y, 1.18, y, -90.0) for y in (1.13, 1.80, 2.47)]
# glaze per place (plate, tumbler and chair seat share it)
PG = [0, 2, 5, 4, 7, 3, 1, 6]
# chair hanging slots in the oak wall: 4 columns x 2 rows
SLOT_Y = [0.65 + 0.2875 + 0.575 * k for k in range(4)]
SLOT_Z = [0.10, 1.22]


def tumbler_pos(i):
    px, py, _, _, yaw = PLACES[i]
    a = math.radians(yaw)
    fwd = np.array([-math.sin(a), math.cos(a)])       # direction the sitter faces
    right = np.array([fwd[1], -fwd[0]])
    p = np.array([px, py]) + 0.16 * right + 0.11 * fwd
    return float(p[0]), float(p[1])


# ------------------------------------------------------------------------------------------- materials
def materials():
    mat('screed', tex=3, col=srgb(186, 185, 182), p=(0.10,))
    mat('floor', tex=1, col=srgb(222, 204, 176), col2=srgb(204, 184, 154), rough=0.4, f0=0.04, glossy=True, p=(0.19, 1.8))
    mat('wall', tex=3, col=srgb(242, 241, 238), p=(0.015,))
    mat('ceiling', col=srgb(246, 246, 244))
    mat('white_cab', col=srgb(243, 242, 239), rough=0.45)
    mat('white_in', col=srgb(234, 233, 230))
    mat('plinth', col=srgb(206, 204, 200))
    wood_mats('oak', srgb(216, 186, 148), seed=3.0)
    wood_mats('oakl', srgb(226, 202, 168), seed=6.0)
    mat('worktop', tex=15, col=srgb(222, 222, 220), col2=srgb(186, 186, 186), rough=0.18, f0=0.045, glossy=True, p=(600.0, 0.82))
    mat('clay', tex=12, col=srgb(196, 136, 110), col2=srgb(232, 222, 212), rough=0.2, f0=0.04, glossy=True,
        p=(0.075, 0.30, 0.003, 0, 0.5))
    mat('steel', tex=14, col=srgb(208, 209, 212), rough=0.26, metal=1, p=(1,))
    mat('basin', col=srgb(184, 186, 190), rough=0.28, f0=0.07, glossy=True)
    mat('hob', col=srgb(16, 16, 18), rough=0.06, f0=0.05, glossy=True)
    mat('hob_ring', col=srgb(84, 84, 88))
    mat('ovenglass', col=srgb(28, 28, 30), rough=0.08, f0=0.05, glossy=True)
    mat('grille', col=srgb(120, 120, 124), rough=0.4)
    mat('vent', col=srgb(60, 60, 64))
    mat('winframe', col=srgb(236, 236, 234), rough=0.4)
    mat('sill', col=srgb(240, 240, 238), rough=0.2, f0=0.04, glossy=True)
    mat('backdrop', tex=9, emis=(1.45, 1.47, 1.52), p=(1.0,))
    mat('backdrop_dusk', tex=9, emis=(1.15, 0.92, 0.74), p=(1.0,))
    mat('snow', col=srgb(244, 246, 250), emis=(1.25, 1.28, 1.34))
    mat('snow_sill', col=srgb(248, 249, 252), rough=0.8)
    mat('led_off', col=srgb(232, 231, 228))
    mat('led', col=(0, 0, 0), emis=(7.5, 7.0, 6.0))
    mat('bulb', col=(0, 0, 0), emis=(9.0, 8.2, 6.6))
    mat('dome', col=srgb(244, 243, 240), rough=0.3, f0=0.04, glossy=True)
    mat('cord', col=srgb(232, 230, 226))
    for nm, c in GLAZES:
        mat(nm, col=srgb(*c), rough=0.22, f0=0.045, glossy=True)
        mat(nm + '_f', tex=6, col=srgb(*c))
    mat('plate_in', col=srgb(244, 242, 236), rough=0.2, f0=0.045, glossy=True)
    mat('linen', tex=3, col=srgb(236, 232, 222), rough=0.9, p=(0.04,))
    mat('napkin', tex=3, col=srgb(240, 238, 232), rough=0.9, p=(0.04,))
    mat('red_pot', col=srgb(196, 66, 54), rough=0.2, f0=0.05, glossy=True)
    for nm, c in (('j_lentil', (200, 110, 70)), ('j_pasta', (232, 196, 104)), ('j_rice', (240, 238, 230)),
                  ('j_bean', (128, 82, 58)), ('j_tea', (96, 128, 84)), ('j_oat', (222, 206, 172)),
                  ('j_pea', (150, 176, 90))):
        mat(nm, tex=3, col=srgb(*c), p=(0.25,))
    mat('jar', col=srgb(232, 234, 232), rough=0.1, f0=0.05, glossy=True)
    mat('lid_wood', tex=2, col=srgb(210, 176, 136), p=(2, 4.0))
    for nm, c in (('bk_sage', (150, 168, 144)), ('bk_cream', (236, 226, 204)), ('bk_clay', (194, 120, 92)),
                  ('bk_blue', (110, 138, 170)), ('bk_ochre', (214, 168, 74)), ('bk_white', (242, 240, 234)),
                  ('bk_slate', (96, 106, 120))):
        mat(nm, col=srgb(*c), rough=0.6)
    mat('orange', col=srgb(236, 140, 46), rough=0.45, f0=0.04, glossy=True)
    mat('apple', col=srgb(150, 186, 70), rough=0.35, f0=0.04, glossy=True)
    mat('bread', tex=3, col=srgb(206, 156, 98), p=(0.2,))
    mat('board', tex=2, col=srgb(214, 178, 132), p=(1, 5.0))
    mat('fir', tex=3, col=srgb(62, 104, 70), p=(0.2,))
    mat('berry', col=srgb(196, 34, 40), rough=0.25, f0=0.05, glossy=True)
    mat('pot_white', col=srgb(240, 238, 232), rough=0.3, f0=0.04, glossy=True)
    mat('hall_floor', col=srgb(224, 208, 182))
    mat('broom', col=srgb(140, 160, 132))


# ------------------------------------------------------------------------------------------- helpers
def disc(inst, c, r, z0, z1, m, n=28):
    add(inst, lathe(rprof(r, z0, z1, min(0.004, (z1 - z0) * 0.45), 3), n, c), m)


def plate(inst, x, y, z, m):
    prof = [(0, z + 0.003), (0.072, z + 0.003), (0.076, z), (0.088, z), (0.094, z + 0.007), (0.128, z + 0.019),
            (0.132, z + 0.022), (0.127, z + 0.023), (0.092, z + 0.012), (0, z + 0.012)]
    add(inst, lathe(prof, 36, (x, y)), m)


def tumbler(inst, x, y, z, m, r=0.034, h=0.095):
    prof = [(0, z), (r - 0.005, z), (r - 0.002, z + 0.004), (r, z + h), (r - 0.004, z + h), (r - 0.006, z + 0.012), (0, z + 0.012)]
    add(inst, lathe(prof, 24, (x, y)), m)


def bowl(inst, x, y, z, r, h, m):
    prof = [(0, z), (r * 0.55, z), (r * 0.88, z + h * 0.35), (r, z + h), (r - 0.006, z + h), (r * 0.84, z + h * 0.38),
            (r * 0.5, z + 0.008), (0, z + 0.008)]
    add(inst, lathe(prof, 28, (x, y)), m)


def jar(inst, x, y, z, r, h, fill):
    add(inst, lathe(rprof(r, z, z + h, 0.008, 3), 22, (x, y)), fill)
    add(inst, lathe(rprof(r * 1.02, z + h, z + h + 0.022, 0.006, 3), 22, (x, y)), 'lid_wood')


def stack(inst, cx, cy, z0, size, mats_, n, rng):
    z = z0
    for i in range(n):
        sx, sy, sz = size
        jx, jy = rng.uniform(-0.006, 0.006, 2)
        add(inst, rbox((cx + jx, cy + jy, z + sz / 2), (sx, sy, sz), sz * 0.45, 3), mats_[i % len(mats_)])
        z += sz * 0.96


def place_mat(yaw, x, y, z=0.0):
    return T(x, y, z) @ R('z', math.radians(yaw))


# ------------------------------------------------------------------------------------------- folding chair
# Local frame: sitter faces +y, origin on the floor under the seat centre.
HB = np.array([0.0, -0.19, 0.445])          # seat hinge (back)
HC = np.array([0.0, 0.17, 0.43])            # front-leg hinge (seat front)


def chair_parts(seat_m):
    A, B, C = [], [], []
    for sx in (-0.19, 0.19):
        A.append((tube([(sx, -0.19, 0.0), (sx, -0.205, 0.45), (sx, -0.225, 0.86)], 0.014, 10), 'oak_z'))
    A.append((box(-0.205, -0.243, 0.62, 0.205, -0.221, 0.84), 'oak_x'))
    A.append((tube([(-0.19, -0.195, 0.16), (0.19, -0.195, 0.16)], 0.009, 8), 'oak_x'))
    B.append((box(-0.20, -0.19, 0.425, 0.20, 0.19, 0.445), 'oak_x'))
    B.append((rbox((0, 0.0, 0.458), (0.38, 0.36, 0.028), 0.012, 3), seat_m))
    for sx in (-0.175, 0.175):
        C.append((tube([(sx, 0.17, 0.0), (sx, 0.17, 0.43)], 0.013, 10), 'oak_z'))
    C.append((tube([(-0.175, 0.17, 0.12), (0.175, 0.17, 0.12)], 0.009, 8), 'oak_x'))
    return A, B, C


def fold_mats(theta):
    """Local transforms of parts (A, B, C) for a fold angle theta (0 = open, pi/2 = flat)."""
    Mb = about(HB, R('x', theta))
    hc = (Mb @ np.array([*HC, 1.0]))[:3]
    Mc = T(*(hc - HC))
    return np.eye(4), Mb, Mc


def build_chairs():
    for i, (_, _, cx, cy, yaw) in enumerate(PLACES):
        Mp = place_mat(yaw, cx, cy)
        A, B, C = chair_parts(GLAZES[PG[i]][0] + '_f')
        for part, lst in zip('abc', (A, B, C)):
            for PN, m in lst:
                add(f'ch{i}_{part}', xform(PN, Mp), m)


# ------------------------------------------------------------------------------------------- shell
def build_shell():
    r = 'room'
    add(r, box(-0.2, -1.6, -0.25, W + 0.2, D + 0.2, -0.012), 'screed')
    add(r, box(-0.2, -1.6, H, W + 0.2, D + 0.2, H + 0.1), 'ceiling')
    add(r, box(-0.2, -0.2, -0.25, 0, D + 0.2, H + 0.1), 'wall')
    add(r, box(W, -0.2, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
    # south wall with doorway + hallway behind
    add(r, box(-0.2, -0.12, -0.25, DX0, 0, H + 0.1), 'wall'); add(r, box(DX1, -0.12, -0.25, W + 0.2, 0, H + 0.1), 'wall')
    add(r, box(DX0, -0.12, 2.1, DX1, 0, H + 0.1), 'wall')
    for b in (box(DX0 - 0.02, -0.005, 0, DX0, 0.012, 2.12), box(DX1, -0.005, 0, DX1 + 0.02, 0.012, 2.12),
              box(DX0 - 0.02, -0.005, 2.1, DX1 + 0.02, 0.012, 2.12)):
        add(r, b, 'white_cab')
    add(r, box(0.6, -1.6, -0.25, 0.8, -0.12, H), 'wall'); add(r, box(3.0, -1.6, -0.25, 3.2, -0.12, H), 'wall')
    add(r, box(0.6, -1.8, -0.25, 3.2, -1.6, H), 'wall')
    add(r, box(0.8, -1.6, -0.012, 3.0, -0.12, 0.0), 'hall_floor')
    # north wall with window
    wx0, wx1, wz0, wz1 = WIN
    add(r, box(-0.2, D, -0.25, wx0, D + 0.2, H + 0.1), 'wall'); add(r, box(wx1, D, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
    add(r, box(wx0, D, -0.25, wx1, D + 0.2, wz0), 'wall'); add(r, box(wx0, D, wz1, wx1, D + 0.2, H + 0.1), 'wall')
    for b in (box(wx0, D, wz0, wx0 + 0.006, D + 0.2, wz1), box(wx1 - 0.006, D, wz0, wx1, D + 0.2, wz1),
              box(wx0, D, wz1 - 0.006, wx1, D + 0.2, wz1)):
        add(r, b, 'sill')
    add(r, box(wx0 - 0.03, D - 0.04, wz0 - 0.02, wx1 + 0.03, D + 0.17, wz0), 'sill')
    fy0, fy1 = D + 0.10, D + 0.13
    xm = (wx0 + wx1) / 2
    for b in (box(wx0, fy0, wz0, wx0 + 0.045, fy1, wz1), box(wx1 - 0.045, fy0, wz0, wx1, fy1, wz1),
              box(wx0, fy0, wz1 - 0.045, wx1, fy1, wz1), box(wx0, fy0, wz0, wx1, fy1, wz0 + 0.045),
              box(xm - 0.02, fy0, wz0, xm + 0.02, fy1, wz1)):
        add(r, b, 'winframe')
    add(r, rbox((xm, D + 0.30, wz0 - 0.005), (wx1 - wx0 + 0.3, 0.30, 0.06), 0.025, 3), 'snow_sill')
    # outside: snowy ground and the sky view (day / dusk)
    add('snow', box(-6, D + 0.6, -0.4, W + 6, D + 7.0, -0.35), 'snow')
    add('bd_day', box(-10, D + 7.0, -5, W + 10, D + 7.05, 9), 'backdrop')
    add('bd_dusk', box(-10, D + 7.02, -5, W + 10, D + 7.07, 9), 'backdrop_dusk')
    # baseboards on the free walls
    add(r, box(wx0 - 0.2, D - 0.012, 0, wx1 + 0.2, D, 0.07), 'white_cab')
    # floor planks in six bands (far = south first)
    edges = [-0.12, 0.6, 1.2, 1.8, 2.4, 3.0, D + 0.01]
    for k in range(6):
        add(f'floor{k}', box(0, edges[k], -0.012, W, edges[k + 1], 0.0), 'floor')


# ------------------------------------------------------------------------------------------- west run
def base_box(inst, y0, y1, fronts, rng=None):
    """Base carcass y0..y1 with a plinth and oak fronts. fronts: list of (z0, z1) drawer/door fronts."""
    add(inst, box(0, y0 + 0.002, 0, FX - 0.05, y1 - 0.002, 0.10), 'plinth')
    add(inst, box(0, y0 + 0.002, 0.10, FX - 0.02, y1 - 0.002, WZ - 0.03), 'white_in')
    for z0, z1 in fronts:
        add(inst, box(FX - 0.02, y0 + 0.003, z0 + 0.002, FX, y1 - 0.003, z1 - 0.002), 'oak_y' if y1 - y0 > z1 - z0 else 'oak_z')


def build_run(rng):
    t = 0.018
    # --- tall pull-out pantry (by the door): carcass + pull-out unit
    add('pantry', box(0, Y_PAN, 0, FX - 0.02, Y_PAN + t, H), 'white_cab')
    add('pantry', box(0, Y_FR - t, 0, FX - 0.02, Y_FR, H), 'white_cab')
    add('pantry', box(0, Y_PAN, 0, 0.02, Y_FR, H), 'white_in')
    add('pantry', box(0, Y_PAN, H - 0.03, FX - 0.02, Y_FR, H), 'white_cab')
    pu = 'pan_pull'
    add(pu, box(FX - 0.02, Y_PAN + 0.003, 0.10, FX, Y_FR - 0.003, H - 0.035), 'white_cab')
    add(pu, box(FX - 0.035, Y_PAN + 0.04, 0.05, FX - 0.02, Y_FR - 0.04, 0.10), 'plinth')
    PZ = [0.16, 0.52, 0.88, 1.24, 1.60, 1.96]
    for z in PZ:
        add(pu, box(0.06, Y_PAN + 0.04, z - 0.015, FX - 0.02, Y_FR - 0.04, z), 'white_in')
        for yy in (Y_PAN + 0.04, Y_FR - 0.052):
            add(pu, box(0.06, yy, z + 0.05, FX - 0.02, yy + 0.012, z + 0.062), 'steel')
    add(pu, box(0.06, Y_PAN + 0.04, 0.10, 0.075, Y_FR - 0.04, 2.30), 'white_in')
    fills = ['j_lentil', 'j_pasta', 'j_rice', 'j_bean', 'j_tea', 'j_oat', 'j_pea']
    for k, z in enumerate(PZ):
        n = 0
        for x in (0.14, 0.26, 0.38, 0.50):
            for y in (0.12, 0.33):
                f = fills[(k * 3 + n) % len(fills)]
                h = (0.20, 0.16, 0.24, 0.14)[(n + k) % 4]
                jar(f'jar{k}', x, y, z, 0.048, h, f)
                n += 1
    # --- fridge column (white panel, vent grille in the plinth, vent gap at the top)
    fr = 'fridge'
    add(fr, box(0, Y_FR, 0, 0.02, Y_SINK, H), 'white_in')
    add(fr, box(0, Y_SINK - t, 0, FX - 0.02, Y_SINK, H), 'white_cab')
    add(fr, box(0.02, Y_FR + 0.01, 0, FX - 0.04, Y_SINK - 0.03, 0.10), 'vent')
    add(fr, box(FX - 0.02, Y_FR + 0.003, 0.10, FX, Y_SINK - 0.003, 1.80), 'white_cab')
    add(fr, box(FX - 0.02, Y_FR + 0.003, 1.802, FX, Y_SINK - 0.003, H - 0.08), 'white_cab')
    add(fr, box(0.02, Y_FR + 0.01, H - 0.075, FX - 0.02, Y_SINK - 0.02, H - 0.03), 'vent')
    add(fr, box(0.02, Y_FR, H - 0.03, FX - 0.02, Y_SINK, H), 'white_cab')
    add('grille', box(FX - 0.05, Y_FR + 0.02, 0.015, FX - 0.035, Y_SINK - 0.04, 0.085), 'grille')
    for k in range(9):
        z = 0.022 + k * 0.007
        add('grille', box(FX - 0.036, Y_FR + 0.025, z, FX - 0.030, Y_SINK - 0.045, z + 0.003), 'vent')
    # --- sink unit with three pull-out bins (one sage)
    base_box('base_sink', Y_SINK, Y_DW, [(0.10, WZ - 0.03)])
    for k, (y0, y1, m) in enumerate(((1.08, 1.27, 'white_in'), (1.27, 1.45, 'g_sage'), (1.45, 1.62, 'white_in'))):
        add(f'bin{k}', rbox((0.30, (y0 + y1) / 2, 0.34), (0.44, y1 - y0 - 0.02, 0.40), 0.02, 3), m)
    # --- dishwasher
    base_box('base_dw', Y_DW, Y_DIN, [(0.10, WZ - 0.03)])
    # --- dinner column base: carcass + plate drawer (top) + pan drawer (bottom)
    add('base_din', box(0, Y_DIN + 0.002, 0, FX - 0.05, Y_OV - 0.002, 0.10), 'plinth')
    for b in (box(0, Y_DIN + 0.002, 0.10, FX - 0.02, Y_DIN + 0.02, WZ - 0.03), box(0, Y_OV - 0.02, 0.10, FX - 0.02, Y_OV - 0.002, WZ - 0.03),
              box(0, Y_DIN, 0.10, 0.02, Y_OV, WZ - 0.03), box(0, Y_DIN, 0.10, FX - 0.02, Y_OV, 0.12)):
        add('base_din', b, 'white_in')
    for nm, z0, z1 in (('plate_dr', 0.48, WZ - 0.03), ('pan_dr', 0.10, 0.48)):
        add(nm, box(FX - 0.02, Y_DIN + 0.003, z0 + 0.002, FX, Y_OV - 0.003, z1 - 0.002), 'oak_y')
        add(nm, box(0.05, Y_DIN + 0.03, z0 + 0.02, FX - 0.02, Y_OV - 0.03, z0 + 0.032), 'white_in')
        for b in (box(0.05, Y_DIN + 0.03, z0 + 0.032, 0.062, Y_OV - 0.03, z1 - 0.06), box(0.05, Y_DIN + 0.03, z0 + 0.032, FX - 0.02, Y_DIN + 0.042, z1 - 0.06),
                  box(0.05, Y_OV - 0.042, z0 + 0.032, FX - 0.02, Y_OV - 0.03, z1 - 0.06)):
            add(nm, b, 'white_in')
    for k in range(6):            # pegs
        a = 2 * math.pi * k / 6
        x, y = 0.30 + 0.155 * math.cos(a), 2.40 + 0.155 * math.sin(a)
        add('plate_dr', tube([(x, y, 0.512), (x, y, 0.60)], 0.010, 8), 'oak_z')
    # pots in the pan drawer
    add('pan_dr', lathe([(0, 0.132), (0.12, 0.132), (0.125, 0.30), (0.118, 0.30), (0.113, 0.145), (0, 0.145)], 28, (0.22, 2.40)), 'red_pot')
    add('pan_dr', lathe([(0, 0.132), (0.10, 0.132), (0.105, 0.26), (0.098, 0.26), (0.093, 0.145), (0, 0.145)], 28, (0.44, 2.28)), 'g_sage')
    add('pan_dr', lathe([(0, 0.132), (0.08, 0.132), (0.085, 0.22), (0.078, 0.22), (0.073, 0.145), (0, 0.145)], 24, (0.44, 2.54)), 'steel')
    # --- oven base (black glass door, blank display)
    base_box('base_ov', Y_OV, Y_SP, [(0.10, 0.18), (0.78, WZ - 0.03)])
    add('base_ov', box(FX - 0.025, Y_OV + 0.01, 0.18, FX - 0.003, Y_SP - 0.01, 0.78), 'ovenglass')
    add('base_ov', box(FX - 0.003, Y_OV + 0.08, 0.70, FX + 0.02, Y_SP - 0.08, 0.715), 'steel')
    # --- spice pull-out (narrow)
    base_box('base_sp', Y_SP, D, [(0.10, WZ - 0.03)])
    sp_cols = ['g_clay', 'g_ochre', 'g_sage', 'red_pot', 'g_blue', 'g_butter']
    for k, z in enumerate((0.20, 0.42, 0.64)):
        for j, x in enumerate((0.12, 0.24, 0.36, 0.48)):
            add(f'spice{k}', lathe(rprof(0.026, z, z + 0.09, 0.006, 2), 16, (x, 3.50)), 'jar')
            add(f'spice{k}', lathe(rprof(0.028, z + 0.09, z + 0.115, 0.006, 2), 16, (x, 3.50)), sp_cols[(k * 4 + j) % 6])
    # --- worktop (with a hole for the sink)
    wtz0 = WZ - 0.03
    for b in (box(0, Y_SINK, wtz0, WT, 1.13, WZ), box(0, 1.53, wtz0, WT, Y_SP + 0.2, WZ), box(0, 1.13, wtz0, 0.10, 1.53, WZ),
              box(0.52, 1.13, wtz0, WT, 1.53, WZ)):
        add('worktop', b, 'worktop')
    # sink + tap
    for b in (box(0.10, 1.13, 0.70, 0.52, 1.53, 0.71), box(0.10, 1.13, 0.71, 0.112, 1.53, WZ - 0.002), box(0.508, 1.13, 0.71, 0.52, 1.53, WZ - 0.002),
              box(0.10, 1.13, 0.71, 0.52, 1.142, WZ - 0.002), box(0.10, 1.518, 0.71, 0.52, 1.53, WZ - 0.002)):
        add('sink', b, 'basin')
    add('sink', tube([(0.06, 1.33, WZ), (0.06, 1.33, 1.22), (0.10, 1.33, 1.26), (0.20, 1.33, 1.24), (0.24, 1.33, 1.16)], 0.012, 10), 'steel')
    # hob
    add('hob', box(0.06, 2.78, WZ, 0.56, 3.32, WZ + 0.006), 'hob')
    for (x, y, rr) in ((0.20, 2.92, 0.08), (0.42, 2.92, 0.065), (0.20, 3.18, 0.065), (0.42, 3.18, 0.08)):
        add('hob', lathe([(rr - 0.004, WZ + 0.0062), (rr, WZ + 0.0062), (rr, WZ + 0.0066), (rr - 0.004, WZ + 0.0066)], 32, (x, y)), 'hob_ring')
    # the red and sage pots on the hob
    add('pots', lathe([(0, WZ + 0.006), (0.10, WZ + 0.006), (0.105, WZ + 0.13), (0.098, WZ + 0.13), (0.093, WZ + 0.02), (0, WZ + 0.02)], 28, (0.20, 2.92)), 'red_pot')
    add('pots', lathe([(0.0, WZ + 0.13), (0.10, WZ + 0.13), (0.06, WZ + 0.15), (0.0, WZ + 0.16)], 28, (0.20, 2.92)), 'red_pot')
    add('pots', lathe([(0, WZ + 0.006), (0.085, WZ + 0.006), (0.088, WZ + 0.10), (0.082, WZ + 0.10), (0.078, WZ + 0.02), (0, WZ + 0.02)], 28, (0.42, 3.18)), 'g_sage')
    # clay splashback strip, in six groups (ripples on)
    ys = np.linspace(Y_SINK, Y_SP, 7)
    for g in range(6):
        add(f'splash{g}', box(0, ys[g], WZ, 0.008, ys[g + 1], UZ0), 'clay')
    # uppers: from the fridge to the window wall, with a hood cabinet over the hob and the dinner column's
    # lift-up (tumblers) and top cabinet (dish lift) as separate pieces
    for (y0, y1) in ((Y_SINK, Y_DIN), (Y_SP, D)):
        add('uppers', box(0, y0 + 0.002, UZ0, UX - 0.02, y1 - 0.002, H), 'white_in')
        nd = max(1, int(round((y1 - y0) / 0.5)))
        for k in range(nd):
            a0, a1 = y0 + (y1 - y0) * k / nd, y0 + (y1 - y0) * (k + 1) / nd
            add('uppers', box(UX - 0.02, a0 + 0.002, UZ0 + 0.002, UX, a1 - 0.002, H - 0.002), 'white_cab')
    # dinner column uppers: carcass (part of 'uppers'), lift-up door, top door, tumbler shelf
    add('uppers', box(0, Y_DIN, UZ0, UX - 0.02, Y_DIN + 0.018, H), 'white_in')
    add('uppers', box(0, Y_OV - 0.018, UZ0, UX - 0.02, Y_OV, H), 'white_in')
    add('uppers', box(0, Y_DIN, UZ0, 0.02, Y_OV, H), 'white_in')
    add('uppers', box(0, Y_DIN, UZ0, UX - 0.02, Y_OV, UZ0 + 0.018), 'white_in')
    add('uppers', box(0, Y_DIN, 1.86, UX - 0.02, Y_OV, 1.878), 'white_in')
    add('uppers', box(0, Y_DIN, H - 0.018, UX - 0.02, Y_OV, H), 'white_in')
    add('liftup', box(UX - 0.02, Y_DIN + 0.002, UZ0 + 0.002, UX, Y_OV - 0.002, 1.868), 'oak_y')
    add('topdoor', box(UX - 0.02, Y_DIN + 0.002, 1.872, UX, Y_OV - 0.002, H - 0.002), 'white_cab')
    # dish lift in the top cabinet: basket + two arms, the platter on it
    add('dlift', box(0.05, Y_DIN + 0.05, 1.92, 0.30, Y_OV - 0.05, 1.93), 'steel')
    for y in (Y_DIN + 0.05, Y_OV - 0.06):
        add('dlift', box(0.05, y, 1.93, 0.30, y + 0.01, 2.00), 'steel')
    add('dlift_arms', tube([(0.03, Y_DIN + 0.04, 2.45), (0.06, Y_DIN + 0.04, 1.97)], 0.008, 8), 'steel')
    add('dlift_arms', tube([(0.03, Y_OV - 0.04, 2.45), (0.06, Y_OV - 0.04, 1.97)], 0.008, 8), 'steel')
    add('platter', xform(lathe([(0, 1.932), (0.14, 1.932), (0.18, 1.952), (0.175, 1.956), (0.13, 1.942), (0, 1.942)], 36, (0, 0)),
                         T(0.175, 2.40, 0) @ S(0.62, 1.0, 1.0)), 'plate_in')
    # bowls / mugs / jars in the uppers over the sink (shown in the long cut) -- they live inside the closed cabinets
    for k, y in enumerate(np.arange(1.12, 2.06, 0.135)):
        bowl('up_bowls', 0.16, y, 1.47, 0.06, 0.05, ['g_blue', 'g_sage', 'g_clay', 'g_butter'][k % 4])
        bowl('up_bowls', 0.16, y, 1.52, 0.06, 0.05, ['g_celery', 'g_ochre', 'g_slate', 'g_plum'][k % 4])
    # hood cabinet over the hob with a steel visor
    add('hood', box(0, Y_OV + 0.002, UZ0 + 0.12, UX - 0.02, Y_SP - 0.002, H), 'white_in')
    add('hood', box(UX - 0.02, Y_OV + 0.002, UZ0 + 0.122, UX, Y_SP - 0.002, H - 0.002), 'white_cab')
    add('hood', box(0.02, Y_OV + 0.01, UZ0 + 0.08, UX + 0.02, Y_SP - 0.01, UZ0 + 0.12), 'steel')
    # LED strip under the uppers
    for (y0, y1) in ((Y_SINK + 0.03, Y_OV - 0.03), (Y_SP + 0.03, D - 0.03)):
        add('room', box(0.26, y0, UZ0 - 0.006, 0.29, y1, UZ0), 'led_off')
        add('led_under', box(0.26, y0, UZ0 - 0.0075, 0.29, y1, UZ0 - 0.0062), 'led')


# ------------------------------------------------------------------------------------------- east wall
BF_HINGE = [(0.65, 1), (2.95, -1)]


def build_east(rng):
    t = 0.02
    ew = 'ewall'
    add(ew, box(EX, 0, 0, W, D, 0.06), 'plinth')
    add(ew, box(W - 0.02, 0, 0, W, D, H), 'oakl_z')
    add(ew, box(EX, 0, H - 0.04, W, D, H), 'oakl_y')
    # broom cupboard (south)
    add(ew, box(EX, 0.002, 0.06, EX + t, 0.648, H - 0.042), 'oakl_z')
    add(ew, box(EX + 0.02, 0.0, 0.06, W, 0.02, H), 'oakl_z')
    add(ew, box(EX, 0.645, 0.06, W, 0.655, H), 'oakl_z')
    # chair recess back + dividers
    add(ew, box(EX + 0.02, 2.945, 0.06, W, 2.955, H), 'oakl_z')
    # open shelving (north), 0.25 deep
    add(ew, box(2.95, 2.955, 0.0, W, 2.975, H), 'oakl_z')
    add(ew, box(2.95, D - 0.02, 0.0, W, D, H), 'oakl_z')
    for z in (0.06, 0.48, 0.90, 1.32, 1.74, 2.16):
        add(ew, box(2.95, 2.975, z, W - 0.02, D - 0.02, z + 0.025), 'oakl_y')
    add(ew, box(2.95, 2.975, 0.0, W, D - 0.02, 0.06), 'plinth')
    # four bi-fold leaves (0.575 each) over the chair recess
    for k in range(4):
        y0 = 0.65 + 0.575 * k
        add(f'bf{k}', box(EX, y0 + 0.002, 0.065, EX + t, y0 + 0.573, H - 0.045), 'oakl_z')
    # cookbooks in the open shelves (three rows: a colour ripple), a jug and a small plant
    cols = ['bk_sage', 'bk_cream', 'bk_clay', 'bk_blue', 'bk_ochre', 'bk_white', 'bk_slate']
    for row, z in enumerate((0.925, 1.345, 1.765)):
        y = 3.00
        k = row * 2
        while y < D - 0.06 - (0.0 if row != 1 else 0.20):
            th = 0.028 + 0.012 * ((k * 7) % 3)
            h = 0.22 + 0.03 * ((k * 5) % 3)
            add(f'books{row}', box(3.0, y, z, 3.17, y + th, z + h), cols[k % len(cols)])
            y += th + 0.002
            k += 1
    bowl('books1', 3.08, 3.45, 1.345, 0.07, 0.08, 'g_clay')
    for k, z in enumerate((0.505, 2.185)):
        stack(f'shelfst{k}', 3.08, 3.28, z, (0.20, 0.24, 0.035), ['g_blue', 'napkin', 'g_butter', 'linen'], 3, rng)
    # broom in the cupboard (never seen)
    add('room', box(3.10, 0.30, 0.06, 3.12, 0.32, 1.4), 'broom')


# ------------------------------------------------------------------------------------------- island / table
ISL_HALF = 0.40          # each half slides this far


def build_island():
    t0, t1 = TZ - 0.03, TZ
    # halves (built where they rest when extended)
    add('isl_s', box(DX0, TY0, t0, DX1, TY0 + 0.60, t1), 'oak_x')
    add('isl_n', box(DX0, TY1 - 0.60, t0, DX1, TY1, t1), 'oak_x')
    add('isl_s', box(DX0 + 0.04, TY0 + 0.04, t0 - 0.06, DX0 + 0.06, TY0 + 0.56, t0), 'oak_y')
    add('isl_s', box(DX1 - 0.06, TY0 + 0.04, t0 - 0.06, DX1 - 0.04, TY0 + 0.56, t0), 'oak_y')
    add('isl_n', box(DX0 + 0.04, TY1 - 0.56, t0 - 0.06, DX0 + 0.06, TY1 - 0.04, t0), 'oak_y')
    add('isl_n', box(DX1 - 0.06, TY1 - 0.56, t0 - 0.06, DX1 - 0.04, TY1 - 0.04, t0), 'oak_y')
    # leaf (two panels, hinged at the centre line)
    add('leaf_s', box(DX0, TY0 + 0.60, t0, DX1, CY, t1), 'oak_x')
    add('leaf_n', box(DX0, CY, t0, DX1, TY1 - 0.60, t1), 'oak_x')
    # spine (steel-cored, oak clad) on a foot plate
    add('spine', box(TCX - 0.07, CY - 0.45, 0.02, TCX + 0.07, CY + 0.45, 0.52), 'oak_y')
    add('spine', box(TCX - 0.30, CY - 0.45, 0.50, TCX + 0.30, CY + 0.45, 0.52), 'steel')
    add('spine', box(TCX - 0.16, CY - 0.47, 0.0, TCX + 0.16, CY + 0.47, 0.02), 'steel')
    # four fold-down legs at the outer ends of the halves
    for nm, y, xs in (('leg_s', TY0 + 0.07, (DX0 + 0.08, DX1 - 0.08)), ('leg_n', TY1 - 0.07, (DX0 + 0.12, DX1 - 0.12))):
        for x in xs:
            add(nm, box(x - 0.018, y - 0.018, 0.0, x + 0.018, y + 0.018, t0 - 0.06), 'oak_z')


# ------------------------------------------------------------------------------------------- table setting
def build_setting(rng):
    for i, (px, py, _, _, _) in enumerate(PLACES):
        g = GLAZES[PG[i]][0]
        plate(f'plate{i}', px, py, TZ, g)
        tx, ty = tumbler_pos(i)
        tumbler(f'tum{i}', tx, ty, TZ, g)
        add(f'nap{i}', rbox((px, py, TZ + 0.030), (0.15, 0.15, 0.014), 0.006, 3), 'napkin')
    # linen runner, stopping short of the end places
    add('runner', box(TCX - 0.15, 1.17, TZ, TCX + 0.15, 2.43, TZ + 0.003), 'linen')
    # bread board, fruit bowl, potted fir (+ berries)
    add('bread', box(TCX - 0.10, 1.32, TZ + 0.003, TCX + 0.10, 1.56, TZ + 0.02), 'board')
    add('bread', ellipsoid((TCX, 1.44, TZ + 0.055), (0.07, 0.10, 0.045), 12), 'bread')
    bowl('fruit', TCX, 2.16, TZ + 0.003, 0.11, 0.06, 'g_slate')
    for k, (dx, dy, m) in enumerate(((0, 0, 'orange'), (0.05, 0.03, 'apple'), (-0.05, 0.02, 'orange'), (0.01, -0.05, 'apple'),
                                     (-0.03, -0.04, 'orange'))):
        add('fruit', ellipsoid((TCX + dx, 2.16 + dy, TZ + 0.07 + (0.03 if k == 0 else 0)), (0.037, 0.037, 0.035), 10), m)
    add('fir', lathe([(0, TZ + 0.003), (0.055, TZ + 0.003), (0.065, TZ + 0.10), (0.068, TZ + 0.105), (0, TZ + 0.105)], 22, (TCX, CY)), 'pot_white')
    for k, (z, r, h) in enumerate(((0.10, 0.11, 0.14), (0.19, 0.085, 0.13), (0.27, 0.06, 0.12), (0.34, 0.035, 0.10))):
        add('fir', lathe([(0, TZ + z), (r, TZ + z), (0.004, TZ + z + h), (0, TZ + z + h)], 18, (TCX, CY)), 'fir')
    for k in range(11):
        a = k * 2.4
        z = 0.12 + (k % 4) * 0.075
        rr = 0.105 - (k % 4) * 0.022
        add('berries', ellipsoid((TCX + rr * math.cos(a), CY + rr * math.sin(a), TZ + z + 0.01), (0.011, 0.011, 0.011), 6), 'berry')
    # pendant over the table centre
    pz = 0.10
    add('pendant', tube([(TCX, CY, H), (TCX, CY, 1.86 + pz)], 0.004, 6), 'cord')
    add('pendant', lathe([(0.0, 1.88 + pz), (0.025, 1.88 + pz), (0.075, 1.85 + pz), (0.125, 1.79 + pz), (0.15, 1.72 + pz), (0.155, 1.70 + pz),
                          (0.150, 1.70 + pz), (0.12, 1.785 + pz), (0.03, 1.865 + pz), (0, 1.865 + pz)], 40, (TCX, CY)), 'dome')
    add('pend_on', ellipsoid((TCX, CY, 1.70 + pz), (0.04, 0.045, 0.045), 10), 'bulb')


# ------------------------------------------------------------------------------------------- build
HOST_SEAT = 7
HOST_AT = (1.13, 2.47, 90.0)


def build():
    materials()
    fg.materials(['fig_adult'])
    rng = np.random.default_rng(8)
    build_shell()
    build_run(rng)
    build_east(rng)
    build_island()
    build_setting(rng)
    build_chairs()
    add('led_shelf', box(2.97, 3.0, 2.152, 2.99, D - 0.04, 2.158), 'led')
    global HOST
    HOST = fg.Figure('host', 'adult')
    HOST.build(HOST.sit_pose(0.472), at=HOST_AT)


# ------------------------------------------------------------------------------------------- camera
VFOV = 85.0


def P(x, y, z, yaw, pitch):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch)


F1 = P(2.80, 3.38, 2.08, 212.0, -40.0)                       # frame-1 pose: high north-east corner, looking at the door
S1 = (F1, P(2.68, 3.12, 2.00, 210.0, -35.0))                   # slow push-in
S2 = (P(2.92, 2.45, 2.00, 262.0, -13.0), P(2.92, 1.50, 1.95, 246.0, -11.0))   # the run: slide south, turn to the pantry
S3a = (P(0.80, 0.20, 2.15, 6.0, -33.0), P(0.90, 0.24, 2.12, 17.0, -32.0))   # SW corner: the island clacks, plates out
S3b = (P(0.80, 0.45, 2.15, 54.0, -27.0), P(0.92, 0.70, 2.12, 62.0, -26.0))    # orbit on to the chair wall
S4 = (P(2.85, 0.45, 2.05, 318.0, -30.0), F1)                   # wide drift north and round into the frame-1 pose
HOLDS = [(0.0, 3.00, S1), (3.30, 7.00, S2), (7.30, 8.55, S3a), (8.75, 10.75, S3b), (11.00, 15.0, S4)]
if os.environ.get('ROOM_ST'):                                   # probe arbitrary stations: ROOM_ST="S3a,S3b"
    HOLDS = [(k, k + 1, globals()[nm]) for k, nm in enumerate(os.environ['ROOM_ST'].split(','))]

if LONG:
    HOLDS = []            # set in the long-cut section below

camera = None


# ------------------------------------------------------------------------------------------- lights (fixed slots)
LSKY = (11.0, 11.5, 12.4)
LDOOR = (3.2, 2.9, 2.4)
LBOUNCE = (1.15, 1.13, 1.10)
LTOP = (0.55, 0.54, 0.52)
LPEND = (260.0, 225.0, 170.0)
LUNDER = (30.0, 27.0, 21.0)
LSHELF = (22.0, 19.0, 15.0)
LSPILL = (900.0, 720.0, 470.0)


def lights(mats4, vis):
    off = (0.0, 0.0, 0.0)
    dusk = bool(vis.get('bd_dusk'))

    def k(L, on, f=1.0):
        return tuple(v * f for v in L) if on else off
    wx0, wx1, wz0, wz1 = WIN
    Ls = []
    Ls.append(rect_light((wx0, D + 0.16, wz0), (wx1 - wx0, 0, 0), (0, 0, wz1 - wz0),
                         (LSKY[0] * 0.85, LSKY[1] * 0.72, LSKY[2] * 0.60) if dusk else LSKY, always=1))   # 0 sky (-y)
    Ls.append(rect_light((DX0, -0.9, 0.1), (0, 0, 2.0), (DX1 - DX0, 0, 0), LDOOR, always=1))                  # 1 door fill (+y)
    Ls.append(rect_light((W - 0.03, 0.4, 0.5), (0, 0, 1.7), (0, 2.8, 0), LBOUNCE))                             # 2 bounce (-x)
    Ls.append(rect_light((0.6, 0.5, H - 0.02), (0, 2.6, 0), (2.0, 0, 0), LTOP))                                # 3 ceiling bounce (down)
    Ls.append(spot_rect((TCX, CY, 1.80), (0, 0, -1), 0.09, k(LPEND, vis.get('pend_on')), 1.5))                 # 4 pendant
    Ls.append(rect_light((0.26, Y_SINK + 0.03, UZ0 - 0.008), (0, Y_OV - Y_SINK - 0.06, 0), (0.03, 0, 0),
                         k(LUNDER, vis.get('led_under'))))                                                    # 5 under-cabinet
    Ls.append(rect_light((2.97, 3.0, 2.15), (0, D - 3.04, 0), (0.02, 0, 0), k(LSHELF, vis.get('led_shelf'))))  # 6 shelf
    Ls.append(spot_rect((TCX, -1.2, 1.9), (0.0, 1.0, -0.70), 0.30, LSPILL, 18.0))                              # 7 warm spill
    return Ls


BLENDER = dict(
    exposure=-0.30,
    look='AgX - Medium High Contrast',
    separate=['backdrop', 'backdrop_dusk', 'snow'],
    fill_lights=[1, 2, 3],
    wood_scale=(55.0, 1.6),
    bake_rect={'backdrop': (-8.0, 12.0, -3.0, 8.0), 'backdrop_dusk': (-8.0, 12.0, -3.0, 8.0)},
    bake_px={'backdrop': 0.008, 'backdrop_dusk': 0.008, 'floor': 0.0015},
)


# ------------------------------------------------------------------------------------------- timeline helpers
I4 = np.eye(4)


class Kit:
    """Shared timeline helpers (used by both cuts)."""

    def __init__(self, tl):
        self.tl = tl

    def appear(self, name, t_on, t_off=None):
        self.tl.custom(name, lambda t: (I4, t >= t_on and (t_off is None or t < t_off)))

    def track(self, name, ref, keys, sound=('tick', 0.35)):
        """A piece that hops between places. ref = its reference point at rest (world). keys:
        ('at', t, pos, parent)  appears at t (scales in) at pos;  ('hop', t0, t1, pos, parent, arc[, kind, strength]).
        pos is in the parent's rest frame (world when parent is None); parent(t) -> (4x4, vis)."""
        tl = self.tl
        ref = np.array(ref, float)

        def world(pos, parent, t):
            p = np.array([*pos, 1.0])
            return (parent(t)[0] @ p)[:3] if parent is not None else p[:3]

        segs = []
        for k in keys:
            if k[0] == 'at':
                segs.append(dict(kind='at', t0=k[1], t1=k[1], pos=np.array(k[2], float), parent=k[3]))
            else:
                _, t0, t1, pos, parent, arc = k[:6]
                kind = k[6] if len(k) > 6 else sound[0]
                st = k[7] if len(k) > 7 else sound[1]
                segs.append(dict(kind='hop', t0=t0, t1=t1, pos=np.array(pos, float), parent=parent, arc=arc))
                if kind != 'none':
                    tl.ev(t1, name, st, kind)

        def f(t):
            if t < segs[0]['t0']:
                return I4, False
            cur = segs[0]
            for i, s in enumerate(segs):
                if t >= s['t0']:
                    cur, ci = s, i
            if cur['kind'] == 'hop' and t < cur['t1']:
                prev = segs[ci - 1]
                a = world(prev['pos'], prev['parent'], cur['t0'])
                b = world(cur['pos'], cur['parent'], cur['t1'])
                u = (t - cur['t0']) / (cur['t1'] - cur['t0'])
                p = a + (b - a) * smooth(u) * 0 + (b - a) * u
                p = p + np.array([0, 0, cur['arc'] * 4 * u * (1 - u)])
                return T(*(p - ref)), True
            if cur['kind'] == 'at' and t < cur['t0'] + 0.12:
                u = (t - cur['t0']) / 0.12
                s = 0.5 + 0.5 * smooth(u)
                p = world(cur['pos'], cur['parent'], t)
                return T(*(p - ref)) @ about(ref, S(s, s, s)), True
            p = world(cur['pos'], cur['parent'], t)
            tau = t - cur['t1']
            if cur['kind'] == 'hop' and tau < 0.25:
                p = p + np.array([0, 0, 0.012 * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.09))])
            return T(*(p - ref)), True
        tl.custom(name, f)
        return f

    def drawer(self, t_appear, t_open, t_close, off, base=None, out=0.16, shut=0.18, events=None):
        """Drawer / pull-out: rides `base` (a piece function), opens at t_open, closes at t_close.
        t_open / t_close may be lists for several open-close cycles."""
        off = np.array(off, float)
        opens = t_open if isinstance(t_open, (list, tuple)) else [t_open]
        closes = t_close if isinstance(t_close, (list, tuple)) else [t_close]

        def f(t):
            if t < t_appear:
                return I4, False
            B = base(t)[0] if base is not None else I4
            k = 0.0
            for to, tc in zip(opens, closes):
                if to <= t < tc:
                    k = eob((t - to) / out, 1.4)
                elif tc <= t < tc + shut + 0.4:
                    k = 1 - smooth((t - tc) / shut)
                    tau = t - tc - shut
                    if tau > 0:
                        k = -0.02 * math.exp(-tau / 0.05) * math.sin(2 * math.pi * tau / 0.12)
            return B @ T(*(off * k)), True
        if events:
            for to, tc in zip(opens, closes):
                self.tl.ev(to + out * 0.5, events + '_open', 0.55, 'swish')
                self.tl.ev(tc + shut, events + '_shut', 0.75, 'thud')
        return f

    def flap(self, name, hinge, axis, a_open, base, t_open, t_close, out=0.22, shut=0.2):
        """Door / lift-up riding `base`, swinging open about a hinge and back."""
        hinge = np.array(hinge, float)
        opens = t_open if isinstance(t_open, (list, tuple)) else [t_open]
        closes = t_close if isinstance(t_close, (list, tuple)) else [t_close]

        def ang(t):
            for to, tc in zip(opens, closes):
                if to <= t < tc:
                    return a_open * eob((t - to) / out, 1.1)
                if tc <= t < tc + shut + 0.3:
                    u = (t - tc) / shut
                    if u < 1:
                        return a_open * (1 - u * u)
                    tau = t - tc - shut
                    return -math.copysign(math.radians(1.5), a_open) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))
            return 0.0

        def f(t):
            M, v = base(t)
            return M @ about(hinge, R(axis, ang(t))), v
        self.tl.custom(name, f)
        for to, tc in zip(opens, closes):
            self.tl.ev(to + out * 0.4, name + '_open', 0.5, 'swish')
            self.tl.ev(tc + shut, name + '_shut', 0.7, 'thud')
        return f


def stage_island(kit, t_drop, t_split, t_leaf, t_legs, t_pre=None):
    """Island: drops in whole (closed), then splits (clack 1), the leaf rises and opens (clack 2), legs fold down (clack 3)."""
    tl = kit.tl

    def drop_off(t):
        if t < t_drop:
            return None
        u = (t - t_drop) / 0.22
        if u < 1:
            return 0.9 * (1 - u * u)
        tau = t - t_drop - 0.22
        return 0.02 * math.exp(-tau / 0.08) * abs(math.sin(math.pi * tau / 0.13))
    tl.ev(t_drop + 0.22, 'island', 1.0, 'thud')

    def split_k(t):                       # 1 = closed, 0 = extended
        if t < t_split:
            return 1.0
        return 1 - eob((t - t_split) / 0.22, 0.6)
    tl.ev(t_split + 0.22, 'clack1', 0.9, 'clack')

    def half(sign):
        def f(t):
            z = drop_off(t)
            if z is None:
                return I4, False
            return T(0, -sign * ISL_HALF * split_k(t), z), True
        return f
    sF, nF = half(-1), half(1)
    tl.custom('isl_s', sF); tl.custom('isl_n', nF)

    def spine(t):
        z = drop_off(t)
        return (I4, False) if z is None else (T(0, 0, z), True)
    tl.custom('spine', spine)
    # leaf: stored flat and folded (north panel flipped onto the south panel), 0.12 below the top
    hinge = np.array([0.0, CY, TZ])

    def leaf_rise(t):
        if t < t_leaf:
            return -0.20
        return -0.20 * (1 - eob((t - t_leaf) / 0.16, 0.8))

    def leaf_flip(t):
        if t < t_leaf + 0.10:
            return math.pi
        return math.pi * (1 - eob((t - t_leaf - 0.10) / 0.24, 0.5))
    tl.ev(t_leaf + 0.34, 'clack2', 0.9, 'clack')

    def leaf_s(t):
        z = drop_off(t)
        if z is None:
            return I4, False
        return T(0, 0, z + leaf_rise(t)), True

    def leaf_n(t):
        z = drop_off(t)
        if z is None:
            return I4, False
        return T(0, 0, z + leaf_rise(t)) @ about(hinge, R('x', leaf_flip(t))), True
    tl.custom('leaf_s', leaf_s); tl.custom('leaf_n', leaf_n)

    # legs: stowed horizontal under each half (pointing to the centre), fold down to vertical
    def legs(nm, sign, base, y):
        hz = TZ - 0.09
        piv = np.array([0.0, y, hz])

        def ang(t):
            if t < t_legs:
                return math.pi / 2
            return math.pi / 2 * (1 - eob((t - t_legs) / 0.2, 0.7))

        def f(t):
            M, v = base(t)
            return M @ about(piv, R('x', sign * ang(t))), v
        tl.custom(nm, f)
    legs('leg_s', 1, sF, TY0 + 0.07)
    legs('leg_n', -1, nF, TY1 - 0.07)
    tl.ev(t_legs + 0.2, 'clack3', 0.9, 'clack')
    return sF, nF


def stage_chairs(kit, wall, t_start, gap=0.2, flight=0.4, order=None):
    """Chairs hang folded in the oak wall (riding `wall`) and hop out to their places, unfolding in the air."""
    tl = kit.tl
    order = order or [1, 2, 3, 0, 4, 7, 6, 5]
    # slots: lower row for east side + ends, upper row for the west side
    slot_of = {}
    lower = [(SLOT_Y[c], SLOT_Z[0]) for c in range(4)]
    upper = [(SLOT_Y[c], SLOT_Z[1]) for c in range(4)]
    slot_of.update({3: lower[0], 2: lower[1], 1: lower[2], 0: lower[3], 4: upper[0], 5: upper[1], 6: upper[2], 7: upper[3]})
    lands = []
    for n, i in enumerate(order):
        _, _, cx, cy, yaw = PLACES[i]
        Mp = place_mat(yaw, cx, cy)
        Mp_inv = np.linalg.inv(Mp)
        sy, sz = slot_of[i]
        p_hang = np.array([2.95, sy, sz])
        p_land = np.array([cx, cy, 0.0])
        t0 = t_start + gap * n
        t1 = t0 + flight
        lands.append(t1)
        yaw_h = 90.0
        dyaw = (yaw - yaw_h + 180) % 360 - 180

        def pose(t, p_hang=p_hang, p_land=p_land, t0=t0, t1=t1, dyaw=dyaw):
            if t < t0:
                Mw = wall(t)[0] @ T(*p_hang) @ R('z', math.radians(yaw_h))
                return Mw, math.pi / 2
            u = (t - t0) / (t1 - t0)
            if u < 1:
                p0 = (wall(t0)[0] @ np.array([*p_hang, 1.0]))[:3]
                p = p0 + (p_land - p0) * smooth(u) + np.array([0, 0, 0.55 * 4 * u * (1 - u)])
                yw = yaw_h + dyaw * smooth(u)
                th = math.pi / 2 * (1 - smooth(c01((u - 0.15) / 0.6)))
                return T(*p) @ R('z', math.radians(yw)), th
            tau = t - t1
            wob = math.radians(3.0) * math.exp(-tau / 0.09) * math.sin(2 * math.pi * tau / 0.22)
            return T(*p_land) @ R('z', math.radians(yaw_h + dyaw)) @ about((0, 0.2, 0), R('x', wob)), 0.0
        for pi_, part in enumerate('abc'):
            def f(t, pose=pose, pi_=pi_, Mp_inv=Mp_inv):
                if t < 0:
                    return I4, False
                Mw, th = pose(t)
                return Mw @ fold_mats(th)[pi_] @ Mp_inv, wall(t)[1]
            tl.custom(f'ch{i}_{part}', f)
        tl.ev(t1, f'chair{i}', 0.85, 'thud')
    return lands


def stage_bifold(kit, wall, t_open, t_close, out=0.25, shut=0.22):
    tl = kit.tl

    def phi(t):
        if t < t_open:
            return 0.0
        if t < t_close:
            return math.pi / 2 * 0.97 * eob((t - t_open) / out, 0.5)
        u = (t - t_close) / shut
        return math.pi / 2 * 0.97 * (1 - smooth(u)) if u < 1 else 0.0
    for d, (y_h, sg) in enumerate(BF_HINGE):
        a_nm, b_nm = (f'bf{0}', f'bf{1}') if d == 0 else (f'bf{3}', f'bf{2}')
        P0 = np.array([EX, y_h, 0.0])
        PA = np.array([EX, y_h + sg * 0.575, 0.0])

        def fa(t, P0=P0, sg=sg):
            M, v = wall(t)
            return M @ about(P0, R('z', sg * phi(t))), v

        def fb(t, P0=P0, PA=PA, sg=sg):
            M, v = wall(t)
            Ma = about(P0, R('z', sg * phi(t)))
            pa = (Ma @ np.array([*PA, 1.0]))[:3]
            return M @ T(*(pa - PA)) @ about(PA, R('z', -sg * phi(t))) @ T(0.022 * math.sin(phi(t)) * 0, 0, 0), v
        tl.custom(a_nm, fa); tl.custom(b_nm, fb)
    tl.ev(t_open + out * 0.5, 'bifold_open', 0.6, 'swish')
    tl.ev(t_close + shut, 'bifold_shut', 0.9, 'thud')


def host_hand(pose, at):
    """World position of the host's right hand for a pose and place."""
    Mr = HOST.root(pose, at)
    Ms = HOST.fk(pose, Mr)
    p = HOST.p
    return (Ms['farm_r'] @ np.array([0, 0.0, -p['fore'] - 0.07, 1.0]))[:3]


SIT = None


def host_poses():
    global SIT
    SIT = HOST.sit_pose(0.472)
    grab = dict(SIT, sh_r=48, elbow_r=40, sh_r_out=4)
    lift = dict(SIT, sh_r=78, elbow_r=78, sh_r_out=8, neck=-4)
    return SIT, grab, lift


# ------------------------------------------------------------------------------------------- 15 s timeline
def timeline_short():
    tl = Timeline(rk, FPS)
    kit = Kit(tl)
    ev, drop, slide, grow = tl.ev, tl.drop, tl.slide, tl.grow
    cen = tl.cen
    # --- S1 (0.0-3.0): the plate ring, planks, base run, columns, island, worktop, oak wall
    T_PL = [0.30 + 0.10 * k for k in range(8)]                     # plates land on the bare screed
    band_t = [0.62 + 0.15 * k for k in range(6)]                   # planks land far (south) to near
    edges = [-0.12, 0.6, 1.2, 1.8, 2.4, 3.0, D + 0.01]
    for k in range(6):
        drop(f'floor{k}', band_t[k] - 0.14, band_t[k], 0.30, 0.04, 0.35 + 0.05 * k, 'thud' if k % 2 == 0 else 'tick')
    for k, (y, nm, t) in enumerate(((Y_SINK, 'base_sink', 1.30), (Y_DW, 'base_dw', 1.42), (Y_DIN, 'base_din', 1.54),
                                    (Y_OV, 'base_ov', 1.66), (Y_SP, 'base_sp', 1.78))):
        slide(nm, t - 0.16, t, (-0.62, 0, 0), 0.8, 0.7)
    sP = grow('pantry', 1.70, 1.92, 'z', (0, 0, 0), 0.8)
    grow('fridge', 1.82, 2.02, 'z', (0, 0, 0), 0.9)
    slide('grille', 6.78, 6.92, (0.25, 0, 0), 0.8, 0.5, 'clack')
    slide_din = tl.anims['base_din']
    sF, nF = stage_island(kit, 2.00, 7.32, 7.62, 7.98)
    drop('worktop', 2.52, 2.68, 0.35, 0.02, 0.8, 'thud')
    sW = slide('ewall', 2.70, 2.95, (0.35, 0, 0), 0.9, 1.0)
    for k in range(3):
        tl.custom(f'books{k}', lambda t, k=k: (sW(t)[0], t >= 2.70))
        if k < 2:
            tl.custom(f'shelfst{k}', lambda t: (sW(t)[0], t >= 2.70))
    # plates: ring on the floor -> hop as their plank lands -> stack on the island -> plate drawer -> places
    def plank_t(y):
        for k in range(6):
            if edges[k] <= y < edges[k + 1]:
                return band_t[k]
        return band_t[-1]
    fD = kit.drawer(1.54, [3.30, 8.22], [3.96, 8.80], (0.45, 0, 0), base=slide_din, events='plate_dr')
    tl.custom('plate_dr', fD)
    tl.custom('pan_dr', lambda t: (slide_din(t)[0], t >= 1.38))
    din_in = lambda t: (I4, True)
    order = list(range(8))                       # clockwise from the north end
    for i in order:
        px, py = PLACES[i][0], PLACES[i][1]
        ref = (px, py, TZ)
        floor0 = (px, py, -0.012)
        floor1 = (px, py, 0.0)
        tp = plank_t(py)
        stack_pos = (TCX, CY - ISL_HALF, TZ + 0.018 * i)
        dr_pos = (0.30, 2.40, 0.512 + 0.016 * i)
        th_in = 3.40 + 0.05 * i
        th_out = 8.30 + 0.06 * i
        keys = [('at', T_PL[i], floor0, None),
                ('hop', tp - 0.02, tp + 0.12, floor1, None, 0.05, 'none'),
                ('hop', 2.24 + 0.035 * i, 2.40 + 0.035 * i, stack_pos, sF, 0.25, 'tick', 0.3),
                ('hop', th_in, th_in + 0.16, dr_pos, fD, 0.28, 'clink', 0.4),
                ('hop', th_out, th_out + 0.22, (px, py, TZ), None, 0.35, 'clink', 0.45)]
        kit.track(f'plate{i}', ref, keys)
        ev(T_PL[i], f'plate_ring{i}', 0.5, 'clink')
    # --- S2 (3.3-7.0): plate drawer, uppers, hob / hood / sink, pantry pull-out fills, splashback
    sU = drop('uppers', 4.10, 4.28, 0.45, 0.02, 0.9, 'thud')
    tl.custom('up_bowls', lambda t: (sU(t)[0], t >= 4.10))
    tl.custom('topdoor', lambda t: (sU(t)[0], t >= 4.10))
    tl.custom('dlift', lambda t: (sU(t)[0], t >= 4.10)); tl.custom('dlift_arms', lambda t: (sU(t)[0], t >= 4.10))
    tl.custom('platter', lambda t: (sU(t)[0], t >= 4.10))
    fL = kit.flap('liftup', (UX, 0.0, 1.868), 'y', math.radians(-95), lambda t: (sU(t)[0], t >= 4.10), 11.12, 12.05)
    drop('hood', 4.30, 4.46, 0.35, 0.02, 0.6, 'thud')
    drop('hob', 4.40, 4.54, 0.25, 0.02, 0.5, 'thud')
    drop('sink', 4.52, 4.66, 0.30, 0.02, 0.5, 'thud')
    PO, PB = 5.02, 6.50
    pull = kit.drawer(1.70, PO, PB, (0.52, 0, 0), base=sP, out=0.24, shut=0.22, events='pantry')
    tl.custom('pan_pull', pull)
    camS2 = np.array([2.55, 1.6, 1.9])
    for k in range(6):
        t0 = 5.28 + 0.17 * k
        name = f'jar{k}'
        piv = np.array([*cen[name], 1.0])

        def fill(t, t0=t0, piv=piv):
            if t < t0:
                return I4, False
            Mp = pull(t)[0]
            pc = (Mp @ piv)[:3]
            if t < t0 + 0.18:
                u = (t - t0) / 0.18
                off = (1 - eoc(u)) * 0.35 * (camS2 - pc)
                s = 0.45 + 0.55 * smooth(u / 0.3)
                return T(*off) @ about(pc, S(s, s, s)) @ Mp, True
            s = tl.settle(t - t0 - 0.18, 0.015)
            return about(pc, S(s, s, s)) @ Mp, True
        tl.custom(name, fill)
        ev(t0 + 0.18, name, 0.4, 'tick')
    for g in range(6):
        grow(f'splash{g}', 4.66 + 0.04 * g, 4.78 + 0.04 * g, 'z', (0, 0, WZ), 0.35, 'tick')
    drop('pots', 4.84, 4.98, 0.30, 0.04, 0.5, 'thud')
    # bins, spice jars live inside closed units: ride their carcass
    for k in range(3):
        tl.custom(f'bin{k}', lambda t: (tl.anims['base_sink'](t)[0], t >= 1.14))
        tl.custom(f'spice{k}', lambda t: (tl.anims['base_sp'](t)[0], t >= 1.62))
    # --- S3 (7.3-10.7): clack, clack, clack; plates to the places; the chair wall
    stage_bifold(kit, sW, 8.48, 10.58)
    lands = stage_chairs(kit, sW, 8.72, gap=0.2, flight=0.40)
    # --- S4 (11.0-15.0): runner, tumblers, pendant + lights, centrepiece, host, napkins, berries
    grow('runner', 11.00, 11.30, 'y', (0, 1.17, 0), 0.4, 'swish')
    SITp, GRAB, LIFT = host_poses()
    for n, i in enumerate(order):
        tx, ty = tumbler_pos(i)
        r = n % 4
        c = n // 4
        cab = (0.10 + 0.11 * c, Y_DIN + 0.09 + 0.14 * r, UZ0 + 0.018)
        t0 = 11.30 + 0.075 * n
        keys = [('at', 4.10, cab, lambda t: (sU(t)[0], True)),
                ('hop', t0, t0 + 0.2, (tx, ty, TZ), None, 0.30, 'tick', 0.35)]
        kit.track(f'tum{i}', (tx, ty, TZ), keys)
    drop('pendant', 11.86, 12.06, 0.7, 0.03, 0.5, 'tick')
    pend_base = tl.anims['pendant']

    def pend(t):
        M, v = pend_base(t)
        if t < 12.06:
            return M, v
        a = math.radians(4.0) * math.exp(-(t - 12.06) / 0.5) * math.sin(2 * math.pi * (t - 12.06) / 1.1)
        return M @ about((TCX, CY, H), R('x', a)), v
    tl.custom('pendant', pend)
    T_ON = 12.20
    kit.appear('pend_on', T_ON); kit.appear('led_under', T_ON + 0.06); kit.appear('led_shelf', T_ON + 0.12)
    kit.appear('bd_day', 0.0, T_ON); kit.appear('bd_dusk', T_ON)
    ev(T_ON, 'lights_on', 0.9, 'chime')
    drop('bread', 12.30, 12.46, 0.35, 0.04, 0.4)
    drop('fruit', 12.42, 12.58, 0.35, 0.05, 0.4)
    drop('fir', 12.56, 12.74, 0.35, 0.04, 0.45, 'thud')
    for n, i in enumerate(order):
        drop(f'nap{i}', 13.00 + 0.08 * n, 13.14 + 0.08 * n, 0.25, 0.03, 0.25)
    kit.appear('berries', 13.82); ev(13.82, 'berries', 0.5, 'tick')
    # host: pops in beside the window-end chair, sits, then lifts the tumbler
    at0 = (0.98, 2.98, 120.0)

    def at_fn(t):
        u = smooth(c01((t - 12.42) / 0.36))
        return (at0[0] + (HOST_AT[0] - at0[0]) * u, at0[1] + (HOST_AT[1] - at0[1]) * u, at0[2] + (HOST_AT[2] - at0[2]) * u)
    pose_fn = fg.track([(12.30, 'stand'), (12.42, 'stand'), (12.80, SITp), (13.80, SITp), (14.00, GRAB), (14.08, GRAB),
                        (14.34, LIFT)])
    HOST.animate(tl, pose=pose_fn, at=at_fn, pop=12.30)
    hand_grab = host_hand(GRAB, HOST_AT)
    tum_base = tl.anims[f'tum{HOST_SEAT}']

    def tum_h(t):
        M, v = tum_base(t)
        if t < 14.08:
            return M, v
        h = host_hand(pose_fn(t), HOST_AT)
        return T(*(h - hand_grab)), True
    tl.custom(f'tum{HOST_SEAT}', tum_h)
    ev(14.34, 'cheers', 0.4, 'clink')
    return tl


# ------------------------------------------------------------------------------------------- long cut (set below)
def timeline_long():
    raise NotImplementedError


def rest_timeline():
    tl = Timeline(rk, FPS)
    hidden = lambda t: (I4, False)
    if not REST_LIT:
        for nm in ('bd_dusk', 'pend_on', 'led_under', 'led_shelf'):
            tl.custom(nm, hidden)
    else:
        tl.custom('bd_day', hidden)
    return tl


def timeline():
    if REST:
        return rest_timeline()
    return timeline_long() if LONG else timeline_short()


camera = hold_camera(HOLDS, VFOV, rest=REST) if HOLDS else None


def music_cfg():
    return dict(bpm=120, MUSIC=dict(drop_at=0.0, chords=[[50, 54, 57, 61], [47, 50, 54, 57], [43, 47, 50, 54], [45, 49, 52, 55]],
                                    roots=[38, 35, 31, 33], pluck_bars=list(range(0, 30, 2)), riser=False))


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    json.dump(music_cfg(), open(os.path.join(out, 'music.json'), 'w'))
    timeline().export(DUR, camera, lights, out)
