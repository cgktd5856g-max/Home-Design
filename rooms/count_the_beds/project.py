"""Count the Beds: a 10.2 m² kids' room for two that sleeps five. Podium with a hollow (a double on castors rolls out
and pops up to chair height), a steel raised bed over a low bed, a fold-out futon under the landing lid, a stair along
the south wall, top cabinets over the west wall (linen / kids' wardrobe with a pull-down rail / guest cabinet), a
fold-down desk for two in a wall niche, a night step. Five reading lights click on with rising notes.
Neutral white shell + light oak + pale-grey steel + one slate accent. No on-screen text.

    ROOM_REST=1 python3 ../../pipeline/run.py project.py <workdir> probe 0.5,1.5,2.5,3.5      # finished room, stations
    ROOM_REST=1 ROOM_NIGHT=1 ...                                                               # dusk version
    ROOM_TOP=1 ROOM_REST=1 ... probe 0.5                                                       # top-down night plan
    python3 ../../pipeline/run.py project.py <workdir> preview                                # 15 s cut
    ROOM_CUT=long python3 ../../pipeline/run.py project.py <workdir> preview                  # long cut (evergreen)

Units: metres. x = east (0..3.4), y = north (0..3.0), z = up (0..2.7).
West wall: pocket door (y 0.10-0.85), desk niche (y 1.70-3.00), top cabinets z 2.20-2.70 the full length.
North wall: window x 0.60-1.60, sill 1.00. East half: podium x 1.90-3.40, top 0.45, hollow under the beds.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'pipeline'))
sys.path.insert(0, HERE)
import roomkit as rk
from roomkit import (srgb, mat, add, box, grid_tris, lathe, rprof, tube, ellipsoid, rbox, T, S, R, about, xform, wood,
                     wood_mats, rect_light, spot_rect)
from animkit import Timeline, c01, eoc, eob, smooth
import figure as fg

REST = os.environ.get('ROOM_REST') == '1'
REST_NIGHT = os.environ.get('ROOM_NIGHT') == '1'
TOP = os.environ.get('ROOM_TOP') == '1'
CUT = os.environ.get('ROOM_CUT', 'short')
LONG = CUT == 'long'
HOLIDAY = not LONG                                # snow on the rooftops in the holiday 15 s cut only

W, D, H = 3.4, 3.0, 2.7
FPS = 25
DUR = 6.0 if REST else (46.0 if LONG else 15.0)
CAPTIONS = []                                     # no on-screen text

PX, PZ = 1.90, 0.45                               # podium front face, podium top
WX0, WX1, WZ0, WZ1 = 0.60, 1.60, 1.00, 2.20       # north window
DX0, DY0, DY1, DZ = 0.0, 1.70, 3.00, 0.70         # desk niche: wall plane, y range, flap hinge height
DBL_DX, DBL_LIFT = 1.20, 0.17                     # the double: stored offset (+x) and pop-up height
FUT_Y0, FUT_L, FUT_TH, FUT_X0, FUT_X1 = 1.07, 0.475, 0.08, 1.93, 2.59
BOX = (2.65, 3.31, 0.575, 1.05, 0.05)             # futon box under the landing lid: x0, x1, y0, y1, floor z
DL = [(0.75, 0.62), (0.75, 1.95), (1.65, 0.62), (1.65, 1.95), (2.22, 1.95)]
NOTES = [72, 74, 76, 79, 81]                      # C5 D5 E5 G5 A5: the count
RL = [  # reading lights: wall point, lamp head, aim
    ((3.40, 2.72, 2.06), (3.27, 2.72, 2.02), (-0.35, 0.0, -1.0)),     # raised bed (east wall, above the deck)
    ((3.40, 2.72, 1.16), (3.27, 2.72, 1.12), (-0.35, 0.0, -1.0)),     # low bed (east wall, under the deck)
    ((2.26, 3.00, 0.98), (2.26, 2.87, 0.94), (0.0, -0.35, -1.0)),     # futon (north wall)
    ((0.88, 3.00, 0.90), (0.88, 2.87, 0.86), (0.0, -0.35, -1.0)),     # double, west (north wall, under the sill)
    ((1.72, 3.00, 0.90), (1.72, 2.87, 0.86), (0.0, -0.35, -1.0)),     # double, east
]


# ------------------------------------------------------------------------------------------- materials
def materials():
    mat('subfloor', tex=3, col=srgb(150, 148, 146), p=(0.12,))
    mat('floor', tex=1, col=srgb(222, 204, 178), col2=srgb(208, 188, 160), rough=0.40, f0=0.04, glossy=True, p=(0.19, 1.8))
    mat('wall', tex=3, col=srgb(242, 241, 238), p=(0.015,))
    mat('ceiling', col=srgb(246, 246, 244))
    mat('white_cab', col=srgb(243, 242, 239), rough=0.45)
    mat('white_in', col=srgb(236, 235, 232))
    mat('shadow_in', col=srgb(200, 198, 195))
    wood_mats('oak', srgb(216, 192, 160), seed=3.0)
    wood_mats('birch', srgb(228, 210, 178), seed=8.0)
    mat('steel', col=srgb(214, 216, 218), rough=0.55)
    mat('slate', tex=3, col=srgb(78, 108, 146), rough=0.6, p=(0.03,))
    mat('oat', tex=3, col=srgb(216, 200, 172), rough=0.85, p=(0.04,))
    mat('sill', col=srgb(244, 243, 240), rough=0.25, f0=0.04, glossy=True)
    mat('mattress', tex=5, col=srgb(246, 246, 244), p=(0, 0.02))
    mat('sheet', tex=3, col=srgb(246, 246, 245), rough=0.9, p=(0.03,))
    mat('duv_slate', tex=3, col=srgb(84, 116, 158), rough=0.9, p=(0.05,))
    mat('duv_oat', tex=3, col=srgb(196, 208, 220), rough=0.9, p=(0.05,))
    mat('pil_white', tex=3, col=srgb(246, 245, 242), rough=0.9, p=(0.04,))
    mat('pil_slate', tex=6, col=srgb(86, 118, 160))
    mat('pil_oat', tex=6, col=srgb(226, 228, 230))
    mat('throw_oat', tex=5, col=srgb(212, 204, 190), p=(0, 0.012))
    mat('futon', tex=5, col=srgb(244, 244, 242), p=(1, 0.03))
    mat('ceramic', col=srgb(244, 243, 240), rough=0.22, f0=0.04, glossy=True)
    mat('blackm', col=srgb(40, 40, 42), rough=0.4, f0=0.04, glossy=True)
    mat('rubber', col=srgb(60, 62, 64), rough=0.7)
    mat('bulb', col=(0, 0, 0), emis=(14.0, 11.5, 8.0))
    mat('led', col=(0, 0, 0), emis=(7.0, 6.4, 5.2))
    mat('led_off', col=srgb(232, 231, 228))
    mat('dl_emis', col=(0, 0, 0), emis=(8.0, 7.6, 6.8))
    mat('suit_slate', col=srgb(58, 98, 148), rough=0.32, f0=0.05, glossy=True)
    mat('suit_oat', col=srgb(204, 202, 196), rough=0.32, f0=0.05, glossy=True)
    mat('rug', tex=6, col=srgb(150, 170, 192))
    mat('pack', tex=3, col=srgb(190, 194, 198), rough=0.8, p=(0.05,))
    mat('sleepbag', tex=5, col=srgb(86, 118, 160), p=(0, 0.02))
    # window views (camera-only emitters)
    mat('sky_day', col=(0, 0, 0), emis=(1.45, 1.70, 2.15))
    mat('sky_dusk', col=(0, 0, 0), emis=(1.85, 1.15, 0.82))
    mat('roof_snow', col=(0, 0, 0), emis=(1.42, 1.44, 1.48))
    mat('roof_tile', col=(0, 0, 0), emis=(0.42, 0.44, 0.48))
    mat('house_day', col=(0, 0, 0), emis=(0.86, 0.84, 0.82))
    mat('house_day2', col=(0, 0, 0), emis=(0.74, 0.78, 0.84))
    mat('roof_snow_dusk', col=(0, 0, 0), emis=(1.40, 1.08, 0.90))
    mat('roof_tile_dusk', col=(0, 0, 0), emis=(0.30, 0.24, 0.24))
    mat('house_dusk', col=(0, 0, 0), emis=(0.78, 0.60, 0.50))
    mat('house_dusk2', col=(0, 0, 0), emis=(0.70, 0.56, 0.50))
    mat('win_glow', col=(0, 0, 0), emis=(2.4, 1.7, 0.9))
    # clear colours for storage
    for nm, c in (('cl_mustard', (220, 176, 84)), ('cl_teal', (72, 150, 150)), ('cl_cobalt', (72, 112, 186)),
                  ('cl_grass', (124, 166, 98)), ('cl_coral', (222, 124, 102)), ('cl_sky', (128, 172, 214)),
                  ('cl_white', (244, 244, 242)), ('cl_slate', (90, 112, 136)), ('cl_oat', (218, 202, 172)),
                  ('cl_grey', (176, 178, 182))):
        mat(nm, tex=5, col=srgb(*c), p=(2, 0.008))
    for nm, c in (('bk_mustard', (220, 176, 84)), ('bk_teal', (72, 150, 150)), ('bk_cobalt', (72, 112, 186)),
                  ('bk_grass', (124, 166, 98)), ('bk_coral', (222, 124, 102)), ('bk_sky', (128, 172, 214)),
                  ('bk_white', (240, 239, 236)), ('bk_slate', (86, 108, 132))):
        mat(nm, col=srgb(*c), rough=0.55)
    fg.materials(['fig_adult', 'fig_blue'])
    mat('fig_slate', col=srgb(132, 156, 188), rough=0.48)
    mat('fig_grey', col=srgb(156, 158, 164), rough=0.48)


# ------------------------------------------------------------------------------------------- helpers
def disc(inst, c, r, z0, z1, m, n=28):
    add(inst, lathe(rprof(r, z0, z1, min(0.004, (z1 - z0) * 0.45), 3), n, c), m)


def garment(inst, x, y, z_top, length, width, m):
    """Hanging kids' garment on a rail running along y (width across the rail, along x)."""
    add(inst, tube([(x - width * 0.45, y, z_top - 0.04), (x, y, z_top), (x + width * 0.45, y, z_top - 0.04)], 0.004, 6), 'steel')
    add(inst, rbox((x, y, z_top - 0.05 - length / 2), (width, 0.035, length), 0.016, 3), m)


def stack(inst, cx, cy, z0, size, mats_, n, rng):
    z = z0
    for i in range(n):
        sx, sy, sz = size
        jx, jy = rng.uniform(-0.008, 0.008, 2)
        add(inst, rbox((cx + jx, cy + jy, z + sz / 2), (sx * rng.uniform(0.96, 1.0), sy * rng.uniform(0.96, 1.0), sz), sz * 0.45, 3),
            mats_[i % len(mats_)])
        z += sz * 0.97


def cloth(inst, x0, x1, y0, y1, z_top, z_hem, r, m, seed, sides=('w', 'e', 's'), puff=0.012):
    """Draped fabric: a gently wrinkled top plus rounded edges falling into softly folded skirts."""
    ph = np.random.default_rng(seed).uniform(0, 6.283, 5)
    xc, hw = (x0 + x1) / 2, (x1 - x0) / 2

    def wob(x, y):
        return (0.008 * math.sin(x * 9 + ph[0]) * math.sin(y * 5 + ph[1]) + 0.004 * math.sin(x * 17 + y * 11 + ph[2])
                + puff * max(0.0, 1 - ((x - xc) / hw) ** 2))
    nx, ny = 30, 30
    V = np.zeros((nx, ny, 3))
    for i, x in enumerate(np.linspace(x0, x1, nx)):
        for j, y in enumerate(np.linspace(y0, y1, ny)):
            V[i, j] = (x, y, z_top + wob(x, y))
    add(inst, grid_tris(V), m)

    def skirt(along, fixed, sign, lo, hi):
        nu, nv = 28, 10
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
        skirt('x', y0, -1, x0 - (r * 0.85 if 'w' in sides else 0.0), x1 + (r * 0.85 if 'e' in sides else 0.0))


def pillow(inst, c, size, tilt, m, yaw=0.0):
    """Puffy pillow: thick in the middle, pinched along the seam. size = (width x, thickness y, height z)."""
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


def frame_box(inst, x0, y0, z0, x1, y1, z1, t, m, open_side):
    """Open box (cabinet carcass) with walls of thickness t; open_side in '+x', '-x', '+z'."""
    parts = []
    if open_side != '-x':
        parts.append(box(x0, y0, z0, x0 + t, y1, z1))
    if open_side != '+x':
        parts.append(box(x1 - t, y0, z0, x1, y1, z1))
    parts += [box(x0, y0, z0, x1, y0 + t, z1), box(x0, y1 - t, z0, x1, y1, z1)]
    parts.append(box(x0, y0, z0, x1, y1, z0 + t))
    if open_side != '+z':
        parts.append(box(x0, y0, z1 - t, x1, y1, z1))
    for b in parts:
        add(inst, b, m)


# ------------------------------------------------------------------------------------------- shell
def build_shell():
    r = 'room'
    add(r, box(-1.6, -0.6, -0.25, W + 0.2, D + 0.2, -0.012), 'subfloor')
    add('ceil', box(-0.2, -0.2, H, W + 0.2, D + 0.2, H + 0.1), 'ceiling')
    add(r, box(0.0, 0.0, -0.012, W, D, 0.0), 'floor')
    # west wall (x -0.20..0): pocket door opening y 0.10-0.85 (head 2.10), desk niche y 1.70-3.00 (x -0.12..0)
    add(r, box(-0.2, -0.2, -0.25, 0.0, 0.10, H + 0.1), 'wall')
    add(r, box(-0.2, 0.10, 2.10, 0.0, 0.85, H + 0.1), 'wall')
    add(r, box(-0.2, 0.85, -0.25, 0.0, DY0, H + 0.1), 'wall')
    add(r, box(-0.2, DY0, -0.25, 0.0, D + 0.2, DZ), 'wall')
    add(r, box(-0.2, DY0, 1.45, 0.0, D + 0.2, H + 0.1), 'wall')
    add(r, box(-0.2, DY0, DZ, -0.12, D + 0.2, 1.45), 'wall')
    # door casing + a slim edge of the pocket door
    for b in (box(-0.012, 0.085, 0, 0.008, 0.10, 2.115), box(-0.012, 0.85, 0, 0.008, 0.865, 2.115),
              box(-0.012, 0.085, 2.10, 0.008, 0.865, 2.115)):
        add(r, b, 'white_cab')
    add(r, box(-0.16, 0.835, 0.0, -0.04, 0.85, 2.09), 'white_cab')
    add(r, box(-0.105, 0.826, 0.98, -0.095, 0.835, 1.12), 'oak_z')
    # hallway beyond the door
    add(r, box(-1.6, -0.6, -0.012, -0.2, 1.6, 0.0), 'floor')
    add(r, box(-0.2, 0.10, -0.012, 0.0, 0.85, 0.0), 'oak_y')
    add(r, box(-1.8, -0.6, -0.25, -1.6, 1.6, H + 0.1), 'wall')
    add(r, box(-1.6, -0.8, -0.25, -0.2, -0.6, H + 0.1), 'wall')
    add(r, box(-1.6, 1.6, -0.25, -0.2, 1.8, H + 0.1), 'wall')
    add(r, box(-1.6, -0.6, H, -0.2, 1.6, H + 0.1), 'ceiling')
    # south wall, east wall
    add(r, box(-0.2, -0.2, -0.25, W + 0.2, 0.0, H + 0.1), 'wall')
    add(r, box(W, -0.2, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
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
        add(r, b, 'sill')
    # skirting
    for b in (box(0, 0, 0, 0.012, 0.085, 0.07), box(0, 0.865, 0, 0.012, D, 0.07), box(0, D - 0.012, 0, PX, D, 0.07),
              box(0, 0, 0, PX, 0.012, 0.07)):
        add(r, b, 'white_cab')
    # downlights (always on)
    for (x, y) in DL:
        add(r, lathe([(0.034, H - 0.002), (0.046, H - 0.002), (0.047, H - 0.010), (0.050, H - 0.012), (0.052, H)], 32, (x, y)), 'white_cab')
        disc('dl_on', (x, y), 0.036, H - 0.004, H - 0.0025, 'dl_emis')
    # window views: sky + rooftops (day, dusk)
    add('bd_day', box(-10, D + 9.0, -6, 12, D + 9.05, 12), 'sky_day')
    add('bd_dusk', box(-10, D + 9.1, -6, 12, D + 9.15, 12), 'sky_dusk')
    rng = np.random.default_rng(21)
    houses = [(-2.2, 5.2, 1.6, 1.4), (-0.6, 6.4, 1.9, 1.7), (1.0, 5.6, 1.5, 2.4), (2.5, 7.0, 2.0, 1.2), (3.9, 5.8, 1.6, 1.9),
              (0.2, 8.0, 2.2, 3.2), (-1.4, 8.4, 1.8, 2.6), (2.0, 8.6, 1.7, 3.6)]
    for k, (cx, dy, w, top) in enumerate(houses):
        y0 = D + dy
        d = 1.4
        sfx = '' if k % 2 else '2'
        for tag, wall_m, tile_m, snow_m in (('day', f'house_day{sfx}', 'roof_tile', 'roof_snow'),
                                             ('dusk', f'house_dusk{sfx}', 'roof_tile_dusk', 'roof_snow_dusk')):
            nm = f'roofs_{tag}'
            add(nm, box(cx - w / 2, y0, -6, cx + w / 2, y0 + d, top), wall_m)
            ridge = top + w * 0.32
            # gable roof: a prism along y (two sloped slabs), white caps in the holiday cut
            for sg in (-1, 1):
                a = math.atan2(ridge - top, w / 2)
                L = math.hypot(w / 2, ridge - top) + 0.08
                M = T(cx + sg * w / 4, y0 + d / 2, (top + ridge) / 2) @ R('y', sg * a)
                add(nm, xform(box(-L / 2, -d / 2 - 0.08, -0.05, L / 2, d / 2 + 0.08, 0.05), M), snow_m if HOLIDAY else tile_m)
            if tag == 'dusk':
                for j in range(2):
                    wx = cx - w / 4 + j * w / 2
                    add('roofs_dusk', box(wx - 0.18, y0 - 0.02, top - 0.9, wx + 0.18, y0, top - 0.45), 'win_glow')
    # control piece (its transform carries light levels; never visible)
    add('ctl', box(1.0, 1.0, -3.0, 1.01, 1.01, -2.99), 'subfloor')


# ------------------------------------------------------------------------------------------- podium + beds
def build_podium():
    t = 0.022
    # three sections: N (y 2.0-3.0) and M (y 1.05-2.0) are decks over the hollow; S (y 0-1.05) is solid with the
    # landing lid, the futon box and the night step drawer.
    PNL = (1.93, 2.585, 1.09, 2.91)                                                 # deck panel over the futon place
    for nm, (y0, y1) in (('pod_N', (2.0, D)), ('pod_M', (1.05, 2.0))):
        ya, yb = max(y0, PNL[2]), min(y1, PNL[3])
        add(nm, box(PX, ya, PZ - 0.04, PNL[0], yb, PZ), 'oak_y')
        add(nm, box(PNL[1], ya, PZ - 0.04, W, yb, PZ), 'oak_y')
        if y0 < PNL[2]:
            add(nm, box(PX, y0, PZ - 0.04, W, PNL[2], PZ), 'oak_x')
        if y1 > PNL[3]:
            add(nm, box(PX, PNL[3], PZ - 0.04, W, y1, PZ), 'oak_x')
        add(nm, box(3.15, y0, 0.0, W, y1, PZ - 0.04), 'white_in')                  # solid east strip
        for yb_ in np.arange(y0 + 0.18, y1 - 0.05, 0.45):                           # steel sub-frame (cutaway)
            add(nm, box(PX + 0.02, yb_, PZ - 0.10, 3.15, yb_ + 0.05, PZ - 0.04), 'steel')
    add('deck_pnl', box(PNL[0] + 0.002, PNL[2] + 0.002, PZ - 0.035, PNL[1] - 0.002, PNL[3] - 0.002, PZ), 'oak_y')
    add('deck_pnl', box(PNL[0] + 0.02, PNL[2] + 0.02, PZ - 0.045, PNL[1] - 0.02, PNL[3] - 0.02, PZ - 0.035), 'steel')
    add('pod_N', box(PX, 2.95, 0.0, 3.15, D, PZ - 0.04), 'oak_x')
    add('pod_N', box(PX, 2.95, 0.0, 3.15, 2.97, PZ - 0.04), 'white_in')
    s = 'pod_S'
    bx0, bx1, by0, by1, bz = BOX
    lx0, lx1, ly0, ly1 = bx0 - 0.03, bx1 + 0.03, 0.55, 1.05
    for b in (box(PX, 0.0, PZ - 0.04, W, ly0, PZ), box(PX, ly0, PZ - 0.04, lx0, ly1, PZ), box(lx1, ly0, PZ - 0.04, W, ly1, PZ)):
        add(s, b, 'oak_x')
    # front face south of the step, with the stool cubby (y 0.08-0.50, z 0-0.40)
    add(s, box(PX, 0.0, 0.0, PX + t, 0.08, PZ - 0.04), 'oak_y')
    add(s, box(PX, 0.50, 0.0, PX + t, 0.62, PZ - 0.04), 'oak_y')
    add(s, box(PX, 0.08, 0.40, PX + t, 0.50, PZ - 0.04), 'oak_y')
    add(s, box(PX, 0.62, 0.215, PX + t, 1.05, PZ - 0.04), 'oak_y')                 # front face above the step
    add(s, box(PX, 1.03, 0.0, PX + t, 1.05, 0.215), 'oak_z')
    add(s, box(2.30, 0.0, 0.0, W, 0.55, PZ - 0.04), 'white_in')                    # solid south block
    for b in (box(PX + t, 0.0, 0.0, 2.30, 0.08, PZ - 0.04), box(PX + t, 0.50, 0.0, 2.30, 0.55, PZ - 0.04),
              box(PX + t, 0.08, 0.40, 2.30, 0.50, PZ - 0.04)):
        add(s, b, 'white_in')
    add(s, box(2.20, 0.55, 0.0, lx0, 1.05, PZ - 0.04), 'white_in')
    frame_box(s, bx0 - 0.015, by0 - 0.015, bz - 0.015, bx1 + 0.015, by1 + 0.0, PZ - 0.04, 0.015, 'white_in', '+z')
    add(s, box(PX + t, 0.60, 0.0, 2.20, 0.62, PZ - 0.04), 'white_in')
    add(s, box(PX + t, 0.62, 0.22, 2.20, 1.03, 0.23), 'white_in')
    # landing lid over the futon box (hinged on its north edge)
    add('lid', box(lx0 + 0.003, ly0 + 0.003, PZ - 0.03, lx1 - 0.003, ly1 - 0.003, PZ - 0.001), 'oak_x')
    add('lid', box((lx0 + lx1) / 2 - 0.06, ly0 + 0.05, PZ - 0.0015, (lx0 + lx1) / 2 + 0.06, ly0 + 0.07, PZ), 'shadow_in')
    # two nesting stools, built in the cubby (A over B)
    for nm, (y0, y1, h, m) in (('stoolA', (0.105, 0.475, 0.37, 'birch')), ('stoolB', (0.14, 0.44, 0.31, 'oak'))):
        x0, x1 = 1.935, 2.215
        add(nm, box(x0, y0, h - 0.025, x1, y1, h), f'{m}_x')
        add(nm, box(x0, y0, 0.0, x1, y0 + 0.02, h - 0.025), f'{m}_z')
        add(nm, box(x0, y1 - 0.02, 0.0, x1, y1, h - 0.025), f'{m}_z')
        add(nm, box(x0 + 0.10, y0 + 0.004, h - 0.06, x1 - 0.10, y0 + 0.016, h - 0.04), 'shadow_in')
    # night step drawer (built pulled out: x 1.53-1.90); its tread is a lid hinged at the back
    n = 'nstep'
    add('nstep_lid', box(1.53, 0.625, 0.20, 1.90, 1.025, 0.22), 'oak_x')
    add('nstep_lid', box(1.525, 0.78, 0.15 + 0.05, 1.53, 0.87, 0.215), 'shadow_in')
    add(n, box(1.53, 0.625, 0.02, 1.552, 1.025, 0.20), 'oak_y')
    for b in (box(1.552, 0.625, 0.02, 1.90, 0.64, 0.20), box(1.552, 1.01, 0.02, 1.90, 1.025, 0.20), box(1.88, 0.64, 0.02, 1.90, 1.01, 0.20),
              box(1.552, 0.64, 0.02, 1.88, 1.01, 0.03)):
        add(n, b, 'white_in')
    for k, y in enumerate((0.70, 0.86)):
        for dy in (0.0, 0.075):
            add('slippers', rbox((1.72, y + dy, 0.055), (0.24, 0.07, 0.05), 0.022, 3), ('cl_slate', 'cl_oat')[k])
    # LED strip in the hollow (long cut)
    add('hol_led', box(PX + 0.05, 1.08, PZ - 0.105, PX + 0.07, 2.92, PZ - 0.10), 'led')
    # castors under the stored double sit on the floor; the hollow floor
    add('pod_M', box(PX + 0.02, 1.05, 0.0, 3.15, 2.95, 0.004), 'white_in')


def build_double():
    # built at its final place, rolled out and popped up: frame z 0.19-0.36, mattress 0.36-0.50
    d = 'dbl'
    x0, x1, y0, y1 = 0.70, PX, 1.05, 2.95
    zb = 0.19
    add(d, box(x0, y0, zb, x0 + 0.022, y1, zb + 0.41), 'oak_y')                    # front panel (= the podium face)
    add(d, box(x0 + 0.004, y0 + 0.30, zb + 0.33, x0 - 0.002, y0 + 0.42, zb + 0.345), 'shadow_in')
    for b in (box(x0 + 0.022, y0, zb, x1 - 0.01, y0 + 0.022, zb + 0.17), box(x0 + 0.022, y1 - 0.022, zb, x1 - 0.01, y1, zb + 0.17),
              box(x1 - 0.032, y0, zb, x1 - 0.01, y1, zb + 0.17)):
        add(d, b, 'oak_x')
    for k in range(14):
        yy = y0 + 0.07 + k * 0.13
        add(d, box(x0 + 0.03, yy, zb + 0.15, x1 - 0.04, yy + 0.07, zb + 0.165), 'birch_x')
    add(d, rbox(((x0 + 0.022 + x1 - 0.01) / 2, (y0 + y1) / 2, 0.43), (x1 - x0 - 0.04, y1 - y0 - 0.03, 0.14), 0.04, 5), 'sheet')
    for (x, y) in ((x0 + 0.10, y0 + 0.10), (x1 - 0.12, y0 + 0.10), (x0 + 0.10, y1 - 0.10), (x1 - 0.12, y1 - 0.10)):
        add(d, xform(lathe(rprof(0.025, -0.012, 0.012, 0.006, 3), 16, (0, 0)), T(x, y, zb - 0.155) @ R('y', math.pi / 2)), 'rubber')
        add(d, box(x - 0.02, y - 0.02, zb - 0.135, x + 0.02, y + 0.02, zb), 'steel')
    for (x, y) in ((x0 + 0.20, y0 + 0.25), (x1 - 0.22, y0 + 0.25), (x0 + 0.20, y1 - 0.25), (x1 - 0.22, y1 - 0.25)):
        add('dbl_legs', tube([(x, y, 0.0), (x, y, zb)], 0.022, 12), 'steel')
        disc('dbl_legs', (x, y), 0.03, 0.0, 0.012, 'rubber')
    pillow('dbl_pil1', (1.00, 2.80, 0.62), (0.52, 0.15, 0.32), -0.32, 'pil_white')
    pillow('dbl_pil2', (1.58, 2.80, 0.62), (0.52, 0.15, 0.32), -0.32, 'pil_white')
    # oat throw: two panels across the foot end (panel B folds onto A along y 1.33)
    add('dbl_thA', rbox((1.30, 1.215, 0.508), (1.26, 0.27, 0.018), 0.008, 3), 'throw_oat')
    add('dbl_thB', rbox((1.30, 1.485, 0.508), (1.26, 0.27, 0.018), 0.008, 3), 'throw_oat')
    add('dbl_thA', tube([(0.67, 1.08, 0.505), (0.67, 1.08, 0.42)], 0.012, 8), 'throw_oat')      # hanging corner
    add('dbl_thA', rbox((0.672, 1.215, 0.45), (0.018, 0.27, 0.11), 0.008, 3), 'throw_oat')


def build_beds(rng):
    # raised bed: east-wall ledger, north-wall bracket, corner post, steel deck with porch, guard rails
    add('rb_ledger', box(W - 0.05, 0.5, 1.40, W, D, 1.50), 'steel')
    add('rb_ledger', box(2.55, D - 0.05, 1.40, W, D, 1.50), 'steel')
    for y in (0.7, 1.6, 2.5):
        add('rb_ledger', box(W - 0.055, y, 1.43, W - 0.05, y + 0.03, 1.46), 'shadow_in')
    add('rb_post', box(2.545, 0.495, PZ, 2.605, 0.555, 1.972), 'steel')
    add('rb_post', box(2.54, 0.49, PZ, 2.61, 0.56, PZ + 0.01), 'steel')
    dk = 'rb_deck'
    for b in (box(2.55, 0.5, 1.48, 2.60, D - 0.05, 1.56), box(2.55, 0.5, 1.48, W - 0.05, 0.55, 1.56),
              box(2.55, 1.08, 1.48, W - 0.05, 1.12, 1.56), box(2.60, 1.75, 1.50, W - 0.05, 1.78, 1.56),
              box(2.60, 2.40, 1.50, W - 0.05, 2.43, 1.56)):
        add(dk, b, 'steel')
    add(dk, box(2.55, 0.5, 1.56, W, D, 1.60), 'steel')
    wood(dk, 2.60, 0.55, 1.60, W, 1.08, 1.612, 'oak')                                # porch boards
    # guard rail along the west edge (bed and porch) and the porch's south edge (gap for the stair at x 3.12-3.4)
    posts = [(2.575, y) for y in (0.525, 1.10, 1.80, 2.45, 2.975)] + [(2.95, 0.525), (3.10, 0.525)]
    for (x, y) in posts:
        if (x, y) != (2.575, 0.525):
            add(dk, box(x - 0.017, y - 0.017, 1.60, x + 0.017, y + 0.017, 1.975), 'steel')
    for z in (1.78, 1.94):
        add(dk, box(2.555, 0.50, z, 2.595, D - 0.01, z + 0.025), 'steel')
        add(dk, box(2.55, 0.505, z, 3.12, 0.545, z + 0.025), 'steel')
    add('rb_mat', rbox((2.98, 2.04, 1.68), (0.76, 1.88, 0.16), 0.04, 5), 'mattress')
    cloth('rb_duvet', 2.62, W - 0.01, 1.12, 2.50, 1.785, 1.67, 0.03, 'duv_slate', 3, sides=('w', 's'))
    pillow('rb_pil', (2.98, 2.80, 1.86), (0.54, 0.14, 0.32), -0.34, 'pil_slate')
    # low bed on the podium, under the deck
    add('lb_mat', rbox((3.00, 2.01, PZ + 0.09), (0.76, 1.88, 0.18), 0.045, 5), 'mattress')
    cloth('lb_duvet', 2.63, W - 0.01, 1.09, 2.48, PZ + 0.205, PZ + 0.08, 0.03, 'duv_oat', 4, sides=('w', 's'))
    pillow('lb_pil', (3.00, 2.80, PZ + 0.27), (0.54, 0.14, 0.30), -0.34, 'pil_oat')
    # stair along the south wall: four blocks with riser drawers (fronts face west)
    xs = [2.28, 2.56, 2.84, 3.12, W]
    for k in range(4):
        x0, x1 = xs[k], xs[k + 1]
        ztop = 0.68 + 0.23 * k
        nm = f'st{k}'
        add(nm, box(x0, 0.0, PZ, x1, 0.48, ztop - 0.03), 'white_cab')
        wood(nm, x0 - 0.01, 0.0, ztop - 0.03, x1, 0.49, ztop, 'oak')
        zlo = PZ if k == 0 else 0.68 + 0.23 * (k - 1)
        m = 'slate' if k == 3 else 'oak_y'
        add(f'sd{k}', box(x0 - 0.02, 0.03, zlo + 0.012, x0, 0.45, ztop - 0.04), m)
        add(f'sd{k}', box(x0 - 0.026, 0.20, ztop - 0.075, x0 - 0.02, 0.28, ztop - 0.065), 'shadow_in')
        for b in (box(x0, 0.05, zlo + 0.02, x0 + 0.24, 0.43, zlo + 0.03), box(x0, 0.05, zlo + 0.03, x0 + 0.24, 0.06, ztop - 0.06),
                  box(x0, 0.42, zlo + 0.03, x0 + 0.24, 0.43, ztop - 0.06), box(x0 + 0.23, 0.05, zlo + 0.03, x0 + 0.24, 0.43, ztop - 0.06)):
            add(f'sd{k}', b, 'white_in')
        cols = ('cl_mustard', 'cl_teal', 'cl_coral', 'cl_cobalt')
        add(f'toys{k}', rbox((x0 + 0.12, 0.17, zlo + 0.08), (0.18, 0.16, 0.10), 0.02, 3), cols[k])
        add(f'toys{k}', rbox((x0 + 0.12, 0.33, zlo + 0.08), (0.18, 0.14, 0.10), 0.02, 3), cols[(k + 2) % 4])
    # book ledge on the inside of the guard rail, slim shelf under the deck at the low bed's head (long cut)
    add('ledge', box(2.60, 1.30, 1.785, 2.70, 2.10, 1.80), 'oak_y')
    add('ledge', box(2.695, 1.30, 1.80, 2.70, 2.10, 1.83), 'oak_y')
    y = 1.32
    j = 0
    bk = ('bk_coral', 'bk_teal', 'bk_mustard', 'bk_cobalt', 'bk_white', 'bk_grass', 'bk_sky', 'bk_coral', 'bk_mustard')
    while y < 2.02:
        th = rng.uniform(0.022, 0.036)
        add(f'ledge_bk{min(2, int((y - 1.32) / 0.24))}', box(2.615, y, 1.80, 2.69, y + th, 1.80 + rng.uniform(0.15, 0.21)), bk[j % len(bk)])
        y += th + 0.004; j += 1
    add('uds', box(2.68, 2.86, 1.00, 3.30, D, 1.018), 'oak_x')
    add('porch_cush', rbox((3.05, 0.78, 1.645), (0.42, 0.42, 0.07), 0.03, 5), 'pil_oat')
    add('uds_items', tube([(2.76, 2.93, 1.035), (2.90, 2.93, 1.035)], 0.017, 12), 'bk_mustard')
    add('uds_items', lathe([(0, 1.018), (0.032, 1.018), (0.034, 1.17), (0.02, 1.20), (0.0, 1.20)], 18, (3.00, 2.93)), 'bk_teal')
    add('uds_items', ellipsoid((3.17, 2.93, 1.075), (0.07, 0.055, 0.06), 12), 'oat')
    add('uds_items', ellipsoid((3.17, 2.93, 1.16), (0.05, 0.045, 0.045), 12), 'oat')
    for dx in (-0.032, 0.032):
        add('uds_items', ellipsoid((3.17 + dx, 2.93, 1.20), (0.016, 0.012, 0.02), 8), 'oat')
    # folded duvets that open on a two-panel hinge (long cut): futon (oat) and double (slate)
    add('fut_duvA', rbox(((FUT_X0 + FUT_X1) / 2, 1.80, PZ + FUT_TH + 0.016), (0.66, 0.44, 0.03), 0.012, 3), 'duv_oat')
    add('fut_duvB', rbox(((FUT_X0 + FUT_X1) / 2, 2.245, PZ + FUT_TH + 0.016), (0.66, 0.44, 0.03), 0.012, 3), 'duv_oat')
    add('dbl_duvA', rbox((1.30, 1.875, 0.516), (1.20, 0.50, 0.03), 0.012, 3), 'duv_slate')
    add('dbl_duvB', rbox((1.30, 2.375, 0.516), (1.20, 0.50, 0.03), 0.012, 3), 'duv_slate')
    # grandpa's mug on the stool once it slides out (long cut)
    add('mug', lathe([(0, 0.37), (0.036, 0.37), (0.04, 0.46), (0.035, 0.46), (0.032, 0.382), (0, 0.382)], 22, (1.66, 0.34)), 'ceramic')
    add('mug', tube([(1.66, 0.38, 0.44), (1.66, 0.405, 0.425), (1.66, 0.38, 0.395)], 0.006, 8), 'ceramic')
    # futon (four rigid flaps, built flat in place) + its pillow
    for k in range(4):
        y0 = FUT_Y0 + k * FUT_L
        add(f'fut{k}', rbox(((FUT_X0 + FUT_X1) / 2, y0 + FUT_L / 2, PZ + FUT_TH / 2), (FUT_X1 - FUT_X0, FUT_L - 0.004, FUT_TH), 0.025, 5), 'futon')
    pillow('fut_pil', (2.26, 2.80, PZ + 0.15), (0.50, 0.13, 0.28), -0.34, 'pil_slate')
    # reading lights (fixtures + emitters)
    for i, (wp, hp_, aim) in enumerate(RL):
        wp, hp_ = np.array(wp), np.array(hp_)
        nrm = np.array([-1.0, 0, 0]) if wp[0] > 3.0 else np.array([0, -1.0, 0])
        base = wp + nrm * 0.012
        if nrm[0] < 0:
            add(f'rl{i}', xform(lathe(rprof(0.045, 0, 0.012, 0.004, 2), 22, (0, 0)), T(*wp) @ R('y', -math.pi / 2)), 'steel')
        else:
            add(f'rl{i}', xform(lathe(rprof(0.045, 0, 0.012, 0.004, 2), 22, (0, 0)), T(*wp) @ R('x', math.pi / 2)), 'steel')
        add(f'rl{i}', tube([tuple(base), tuple(base + nrm * 0.06 + np.array([0, 0, 0.04])), tuple(hp_ + np.array([0, 0, 0.05]))], 0.007, 10), 'steel')
        add(f'rl{i}', lathe([(0.012, hp_[2] + 0.055), (0.030, hp_[2] + 0.045), (0.048, hp_[2] + 0.005), (0.050, hp_[2])], 24,
                            (hp_[0], hp_[1])), 'slate')
        disc(f'rl_on{i}', (hp_[0], hp_[1]), 0.040, hp_[2] + 0.004, hp_[2] + 0.006, 'bulb')


# ------------------------------------------------------------------------------------------- west wall
def build_west(rng):
    t = 0.018
    z0, z1, dep = 2.20, H, 0.40
    tc = 'tc_body'
    for (a, b) in ((0.0, 0.98), (0.98, 1.98), (1.98, D)):
        frame_box(tc, -0.001, a, z0, dep, b, z1, t, 'white_in', '+x')
    add(tc, box(0.02, 0.10, z0 - 0.006, dep - 0.02, D - 0.10, z0), 'led_off')
    # doors: linen (two side-hinged), wardrobe (two side-hinged), guest (one lift-up flap)
    for nm, (a, b) in (('tc_linS', (0.0, 0.49)), ('tc_linN', (0.49, 0.98)), ('tc_wdS', (0.98, 1.48)), ('tc_wdN', (1.48, 1.98))):
        add(nm, box(dep, a + 0.002, z0 + 0.002, dep + t, b - 0.002, z1 - 0.004), 'white_cab')
        hy = b - 0.04 if nm.endswith('S') else a + 0.04
        add(nm, box(dep + t, hy - 0.006, z0 + 0.03, dep + t + 0.008, hy + 0.006, z0 + 0.16), 'oak_z')
    add('tc_guest', box(dep, 1.982, z0 + 0.002, dep + t, D - 0.002, z1 - 0.004), 'white_cab')
    add('tc_guest', box(dep + t, 2.30, z0 + 0.025, dep + t + 0.008, 2.68, z0 + 0.037), 'oak_x')
    # linen stacks: folded duvets and pillows by colour
    for k, (yc, ms) in enumerate(((0.20, ('cl_white', 'cl_white', 'cl_oat', 'cl_oat')), (0.50, ('cl_slate', 'cl_slate', 'cl_oat', 'cl_white')),
                                  (0.80, ('cl_white', 'cl_grey', 'cl_slate', 'cl_white')))):
        stack(f'lin{k}', 0.21, yc, z0 + t, (0.34, 0.27, 0.095), ms, 4, rng)
    # wardrobe: pull-down rail with kids' clothes in clear colours (+ its arms)
    rail_x, rail_z = 0.21, 2.62
    add('wd_rail', tube([(rail_x, 1.01, rail_z), (rail_x, 1.95, rail_z)], 0.010, 10), 'steel')
    cols = ('cl_coral', 'cl_mustard', 'cl_teal', 'cl_cobalt', 'cl_grass', 'cl_sky', 'cl_white', 'cl_coral', 'cl_teal', 'cl_mustard')
    for k, m in enumerate(cols):
        garment('wd_rail', rail_x, 1.06 + k * 0.092, rail_z, rng.uniform(0.28, 0.34), 0.30, m)
    for nm, y in (('wd_armS', 1.005), ('wd_armN', 1.955)):
        add(nm, tube([(0.03, y, 2.66), (rail_x, y, rail_z)], 0.008, 8), 'steel')
    # striped rug in the entry zone (unrolls from the door side)
    add('rug', box(0.20, 0.12, 0.0, 1.45, 0.98, 0.012), 'rug')
    # coat hooks on the bare wall between the door and the niche: two kids' jackets and a tote
    wood('hooks', 0.0, 1.18, 1.43, 0.022, 1.68, 1.50, 'oak')
    for y in (1.28, 1.46, 1.62):
        add('hooks', tube([(0.022, y, 1.465), (0.07, y, 1.47), (0.08, y, 1.49)], 0.009, 8), 'oak_x')
    for y, L, m in ((1.28, 0.42, 'cl_coral'), (1.46, 0.46, 'cl_teal')):
        add('coats', rbox((0.05, y, 1.47 - L / 2), (0.07, 0.17, L), 0.03, 3), m)
        add('coats', rbox((0.05, y, 1.47 - 0.02), (0.075, 0.12, 0.06), 0.025, 3), m)
    add('coats', rbox((0.035, 1.62, 1.30), (0.05, 0.14, 0.24), 0.02, 3), 'cl_mustard')
    add('coats', tube([(0.04, 1.57, 1.42), (0.08, 1.62, 1.49), (0.04, 1.67, 1.42)], 0.008, 8), 'cl_mustard')
    # guest cabinet stays empty until the bags fly in (bags are built in it, see build_bags)
    # desk niche: back, pigeonholes, the flap (built folded up)
    add('niche', box(-0.12, DY0 + 0.01, 1.07, -0.005, D - 0.01, 1.085), 'oak_x')
    for y in np.linspace(DY0 + 0.01, D - 0.03, 7):
        add('niche', box(-0.12, y, 1.085, -0.005, y + 0.016, 1.45), 'oak_z')
    add('niche', box(-0.12, DY0 + 0.01, DZ + 0.03, -0.005, D - 0.01, DZ + 0.045), 'oak_x')
    add('desk_flap', box(-0.024, DY0 + 0.015, DZ, 0.0, D - 0.015, DZ + 0.48), 'oak_z')
    add('desk_flap', box(-0.026, 2.30, DZ + 0.42, -0.024, 2.40, DZ + 0.45), 'shadow_in')
    for y in (DY0 + 0.05, D - 0.05):
        add('desk_flap', box(-0.02, y - 0.006, DZ - 0.004, -0.004, y + 0.006, DZ + 0.01), 'steel')
    # pigeonhole fill: books (upper cells) and pencil pots + notebooks (lower shelf)
    cells = np.linspace(DY0 + 0.01, D - 0.03, 7)
    bk = ('bk_coral', 'bk_mustard', 'bk_teal', 'bk_cobalt', 'bk_white', 'bk_grass', 'bk_sky', 'bk_slate')
    for c in range(6):
        ya, yb = cells[c] + 0.022, cells[c + 1] - 0.006
        y = ya
        j = 0
        while y < yb - 0.03:
            th = rng.uniform(0.022, 0.034)
            h = rng.uniform(0.20, 0.27)
            add(f'pig{c}', box(-0.112, y, 1.087, -0.018, min(y + th, yb), 1.087 + h), bk[(c * 3 + j) % len(bk)])
            y += th + 0.003; j += 1
            if j >= (3 + c % 3):
                break
    for k, y in enumerate((1.85, 2.15, 2.60, 2.85)):
        add('pots', lathe([(0, DZ + 0.045), (0.03, DZ + 0.045), (0.032, DZ + 0.15), (0.0, DZ + 0.15)], 18, (-0.06, y)),
            ('bk_mustard', 'bk_teal', 'bk_coral', 'bk_cobalt')[k])
        for j in range(3):
            add('pots', tube([(-0.06 + 0.01 * (j - 1), y + 0.008 * j, DZ + 0.12), (-0.06 + 0.02 * (j - 1), y + 0.012 * (j - 1), DZ + 0.24)],
                             0.004, 6), ('bk_slate', 'bk_white', 'bk_grass')[j])
    add('pots', box(-0.11, 2.30, DZ + 0.045, -0.02, 2.50, DZ + 0.065), 'bk_sky')


def build_bags():
    """Bags are built where they end (in the guest cabinet); the timeline moves them to the floor and back."""
    out = {}
    # slate cabin suitcase: local upright, width x 0.38, depth y 0.22, height z 0.55 (wheels at z 0)
    def suitcase(nm, wdt, dep, hgt, m, C):
        parts = [(rbox((0, 0, 0.03 + hgt / 2), (wdt, dep, hgt), 0.035, 5), m)]
        parts.append((rbox((0, -dep / 2 - 0.004, 0.03 + hgt / 2), (wdt * 0.82, 0.01, hgt * 0.86), 0.004, 3), m))
        for sx in (-1, 1):
            parts.append((tube([(sx * wdt * 0.32, dep * 0.30, 0.03 + hgt), (sx * wdt * 0.32, dep * 0.30, 0.03 + hgt + 0.05)], 0.008, 8), 'blackm'))
            for sy in (-1, 1):
                parts.append((ellipsoid((sx * wdt * 0.38, sy * dep * 0.32, 0.022), (0.022, 0.022, 0.022), 8), 'rubber'))
        parts.append((tube([(-wdt * 0.32, dep * 0.30, 0.03 + hgt + 0.05), (wdt * 0.32, dep * 0.30, 0.03 + hgt + 0.05)], 0.010, 8), 'blackm'))
        parts.append((rbox((0, -dep * 0.0, 0.03 + hgt + 0.012), (0.12, 0.03, 0.025), 0.01, 3), 'blackm'))
        for g, mm in parts:
            add(nm, xform(g, C), mm)
        out[nm] = C
    suitcase('bag_slate', 0.38, 0.22, 0.52, 'suit_slate', T(0.205, 2.335, 2.22 + 0.13) @ R('x', math.pi / 2) @ T(0, 0, -0.29))
    suitcase('bag_oat', 0.33, 0.19, 0.44, 'suit_oat', T(0.205, 2.31, 2.46 + 0.10) @ R('x', math.pi / 2) @ T(0, 0, -0.25))
    # backpack with a rolled sleeping bag on top (upright in both places)
    C = T(0.20, 2.80, 2.222)
    for g, mm in ((rbox((0, 0, 0.15), (0.28, 0.17, 0.30), 0.06, 5), 'pack'), (rbox((0, -0.09, 0.11), (0.20, 0.04, 0.14), 0.02, 3), 'pack'),
                  (xform(tube([(-0.15, 0, 0), (0.15, 0, 0)], 0.068, 18), T(0, 0.01, 0.37)), 'sleepbag'),
                  (tube([(-0.09, 0.09, 0.28), (-0.09, 0.10, 0.05)], 0.012, 6), 'rubber'), (tube([(0.09, 0.09, 0.28), (0.09, 0.10, 0.05)], 0.012, 6), 'rubber')):
        add('bag_pack', xform(g, C), mm)
    out['bag_pack'] = C
    return out


BAG_C = {}
FIGS = {}


def build():
    rk.reset()
    materials()
    rng = np.random.default_rng(5)
    build_shell()
    build_podium()
    build_double()
    build_beds(rng)
    build_west(rng)
    BAG_C.update(build_bags())
    # grandparents seated on the double's foot end (on the throw), facing the door; a cane leans on the corner
    for nm, x, yaw, m, fl in (('gma', 1.24, 200.0, 'fig_slate', 0.0), ('gpa', 1.70, 185.0, 'fig_grey', 0.22)):
        f = fg.Figure(nm, 'adult', m)
        q = f.sit_pose(0.52, floor=fl)
        q['spine'] = q.get('spine', 0) + 12; q['neck'] = q.get('neck', 0) + 4
        if nm == 'gpa':
            q['sh_r'], q['elbow_r'], q['sh_r_out'] = 30, 40, 18
        f.build(q, at=(x, 1.27, yaw), seat=0.52)
        FIGS[nm] = f
    add('cane', tube([(1.02, 0.98, 0.0), (1.00, 1.03, 0.78), (1.00, 1.03, 0.84), (0.97, 1.03, 0.87), (0.93, 1.03, 0.855)], 0.011, 10), 'oat')


# ------------------------------------------------------------------------------------------- camera
VFOV = 90.0


def P(x, y, z, yaw, pitch):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch)


F1 = P(0.05, 0.47, 1.30, 42.0, -9.0)                                              # frame 1: in the doorway
S1 = (F1, P(0.78, 0.38, 1.30, 72.0, -8.0))                                         # doorway dolly in, turning right
S2 = (P(2.08, 0.32, 1.55, -96.0, 17.0), P(1.86, 0.66, 1.55, -56.0, 13.0))          # west wall: linen + wardrobe
S3 = (P(1.70, 0.95, 1.50, -74.0, 12.0), P(1.42, 1.45, 1.50, -44.0, 17.0))          # desk + guest cabinet
S4 = (P(0.75, 0.28, 1.15, 70.0, -14.0), P(1.08, 0.48, 1.10, 42.0, -14.0))        # the futon comes out of the landing
S5 = (P(0.16, 0.12, 0.70, 62.0, 0.0), P(0.42, 0.34, 0.72, 42.0, -3.0))           # the double rolls at the lens
S6 = (P(-0.42, 0.47, 1.40, 80.0, -10.0), F1)                                       # final: from the hallway, back to frame 1
EASE = {0: lambda u: 1 - (1 - u) ** 1.6, 5: lambda u: u ** 1.4}                    # loop: the last glide speeds into the first
HOLDS = [(0.0, 2.9, S1), (3.2, 5.05, S2), (5.35, 7.0, S3), (7.3, 8.6, S4), (8.85, 10.75, S5), (11.05, DUR, S6)]
TOPCAM = [(0.0, DUR, (P(1.70, 1.50, 5.6, 0.0, -89.9), P(1.70, 1.50, 5.6, 0.0, -89.9)))]

if LONG:
    import long_cut as LC
    HOLDS = LC.HOLDS
    EASE = getattr(LC, 'EASE', {})


def hold_camera(holds, vfov, rest=False, ease=None, lift=2.0, final_lift=4.0):
    """camkit.hold_camera with an optional easing per hold (index -> f(u)), so the last glide can end at the speed
    the first one starts with (a seamless loop)."""
    import camkit as ck
    ease = ease or {}
    stations = [h[2] for h in holds]

    def g(i, u):
        u = c01(u)
        return ck.glide(holds[i][2], ease.get(i, lambda v: v)(u), vfov)

    def camera(t):
        if rest:
            return dict(stations[min(len(stations) - 1, int(t))][0], vfov=vfov)
        for i, (t0, t1, st) in enumerate(holds):
            if t < t1 or i == len(holds) - 1:
                return g(i, (t - t0) / (t1 - t0))
            n0 = holds[i + 1][0]
            if t < n0:
                u = (t - t1) / (n0 - t1)
                a, b = g(i, 1.0), g(i + 1, 0.0)
                if i + 1 == len(holds) - 1:
                    return ck.lerp_cam(a, b, 1 - (1 - c01(u)) ** 3, lift=final_lift, vfov=vfov)
                return ck.lerp_cam(a, b, smooth(u), lift=lift, vfov=vfov)
        return g(len(holds) - 1, 1.0)
    return camera


camera = hold_camera(TOPCAM if TOP else HOLDS, 60.0 if TOP else VFOV, rest=REST, ease=None if TOP else EASE)


# ------------------------------------------------------------------------------------------- lights (fixed slots)
LSKY = (13.0, 13.6, 14.6)
LSKY_DUSK = (8.0, 6.8, 5.8)
LFILL = (1.20, 1.14, 1.04)
LDOOR = (1.62, 1.54, 1.42)
LEAST = (0.94, 0.90, 0.82)
LDOWN = (430.0, 390.0, 325.0)
LREAD = (700.0, 560.0, 380.0)
LHOL = (30.0, 27.0, 22.0)
LHALL = (2.2, 2.1, 2.0)


def lights(mats4, vis):
    off = (0.0, 0.0, 0.0)
    C = mats4.get('ctl', np.eye(4))
    dusk = float(C[0, 3]) if not (REST and REST_NIGHT) else 1.0
    swell = float(C[1, 3]) if not (REST and REST_NIGHT) else 1.0
    if REST and not REST_NIGHT:
        dusk, swell = 0.0, 0.0

    def k(L, f=1.0):
        return tuple(v * f for v in L)
    sky = tuple(a * (1 - dusk) + b * dusk for a, b in zip(LSKY, LSKY_DUSK))
    Ls = []
    Ls.append(rect_light((WX0, D + 0.16, WZ0), (WX1 - WX0, 0, 0), (0, 0, WZ1 - WZ0), sky, always=1))                   # 0 sky (-y)
    Ls.append(rect_light((0.35, 0.35, H - 0.03), (0, 2.3, 0), (1.95, 0, 0), k(LFILL)))                    # 1 ceiling fill (down)
    Ls.append(rect_light((-0.6, 0.12, 0.2), (0, 0.70, 0), (0, 0, 1.85), k(LDOOR, 1 - 0.3 * dusk), always=1))               # 2 door fill (+x)
    Ls.append(rect_light((W - 0.03, 0.30, 1.98), (0, 0, 0.6), (0, 2.4, 0), k(LEAST, 1 - 0.25 * dusk)))                     # 3 east fill (-x)
    for (x, y) in DL:                                                                                                       # 4-8 downlights
        Ls.append(spot_rect((x, y, H - 0.006), (0, 0, -1), 0.05, k(LDOWN, 1.0 if vis.get('dl_on') else 0.0), 4.0))
    for i, (wp, hp_, aim) in enumerate(RL):                                                                                 # 9-13 reading
        on = bool(vis.get(f'rl_on{i}'))
        Mi = mats4.get(f'rl_on{i}', np.eye(4))
        c = (Mi @ np.array([hp_[0], hp_[1], hp_[2] - 0.004, 1.0]))[:3]
        Ls.append(spot_rect(tuple(c), aim, 0.03, k(LREAD, (0.6 + 4.5 * swell) if on else 0.0), 6.0))
    Ls.append(rect_light((PX + 0.05, 1.08, PZ - 0.106), (0, 1.84, 0), (0.02, 0, 0), k(LHOL, 1.0 if vis.get('hol_led') else 0.0)))  # 14
    Ls.append(rect_light((-1.3, -0.3, H - 0.03), (0, 1.6, 0), (0.9, 0, 0), k(LHALL)))                                       # 15 hallway
    return Ls


BLENDER = dict(
    persistent=False,
    exposure=-0.12,
    look='AgX - Medium High Contrast',
    separate=['sky_day', 'sky_dusk', 'roof_snow', 'roof_tile', 'house_day', 'house_day2', 'roof_snow_dusk', 'roof_tile_dusk',
              'house_dusk', 'house_dusk2', 'win_glow'],
    fill_lights=[1, 2, 3],
    wood_scale=(55.0, 1.6),
    bake_px={'floor': 0.0015},
)


# ------------------------------------------------------------------------------------------- motion helpers
I4 = np.eye(4)


def mat2quat(M):
    m = M[:3, :3]
    tr = m.trace()
    if tr > 0:
        s = math.sqrt(tr + 1.0) * 2
        q = np.array([0.25 * s, (m[2, 1] - m[1, 2]) / s, (m[0, 2] - m[2, 0]) / s, (m[1, 0] - m[0, 1]) / s])
    else:
        i = int(np.argmax([m[0, 0], m[1, 1], m[2, 2]]))
        j, k = (i + 1) % 3, (i + 2) % 3
        s = math.sqrt(1.0 + m[i, i] - m[j, j] - m[k, k]) * 2
        q = np.zeros(4)
        q[0] = (m[k, j] - m[j, k]) / s
        q[1 + i] = 0.25 * s
        q[1 + j] = (m[j, i] + m[i, j]) / s
        q[1 + k] = (m[k, i] + m[i, k]) / s
    return q / np.linalg.norm(q)


def quat2mat(q):
    w, x, y, z = q
    return np.array([[1 - 2 * (y * y + z * z), 2 * (x * y - z * w), 2 * (x * z + y * w)],
                     [2 * (x * y + z * w), 1 - 2 * (x * x + z * z), 2 * (y * z - x * w)],
                     [2 * (x * z - y * w), 2 * (y * z + x * w), 1 - 2 * (x * x + y * y)]])


def slerp(q0, q1, u):
    d = float(np.dot(q0, q1))
    if d < 0:
        q1, d = -q1, -d
    if d > 0.9995:
        q = q0 + u * (q1 - q0)
        return q / np.linalg.norm(q)
    th = math.acos(d)
    return (math.sin((1 - u) * th) * q0 + math.sin(u * th) * q1) / math.sin(th)


def pose_lerp(A, B, u, arc=0.0):
    """Blend two rigid poses (4x4) with slerped rotation and an upward arc."""
    q = slerp(mat2quat(A), mat2quat(B), u)
    M = np.eye(4)
    M[:3, :3] = quat2mat(q)
    M[:3, 3] = A[:3, 3] * (1 - u) + B[:3, 3] * u + np.array([0, 0, arc * math.sin(math.pi * u)])
    return M


def settle_z(tau, amp):
    return amp * math.exp(-tau / 0.09) * abs(math.sin(math.pi * tau / 0.13)) if tau > 0 else 0.0


# ------------------------------------------------------------------------------------------- timeline
class Kit:
    """Shared timeline helpers (used by the 15 s cut here and the long cut in long_cut.py)."""

    def __init__(self, tl):
        self.tl = tl

    def note(self, t, i, strength=0.5, name=None):
        self.tl.events.append(dict(t=round(t, 3), name=name or f'note{i}', strength=strength, kind='pluck', note=NOTES[i]))

    def appear(self, name, t_on, t_off=None):
        self.tl.custom(name, lambda t: (I4, t >= t_on and (t_off is None or t < t_off)))

    def door(self, name, hinge, a_open, t_appear, t_open, t_close, axis='z', base=None, dur_o=0.20, dur_c=0.18, snd=True,
             more=()):
        """Cabinet door: closed from t_appear, swings open at t_open (overshoot), slams at t_close (bounce).
        more = extra (t_open, t_close) cycles later on."""
        hinge = np.array(hinge, float)
        cycles = [(t_open, t_close)] + list(more)

        def f(t):
            if t < t_appear:
                return I4, False
            B = base(t)[0] if base is not None else I4
            cyc = None
            for c in cycles:
                if t >= c[0]:
                    cyc = c
            if cyc is None:
                return B, True
            to, tc = cyc
            if t < tc:
                return B @ about(hinge, R(axis, a_open * eob((t - to) / dur_o, 1.2))), True
            u = (t - tc) / dur_c
            if u < 1:
                return B @ about(hinge, R(axis, a_open * (1 - u * u))), True
            tau = t - tc - dur_c
            a = math.copysign(math.radians(2.0), a_open) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))
            return B @ about(hinge, R(axis, a)), True
        self.tl.custom(name, f)
        if snd:
            for to, tc in cycles:
                self.tl.ev(to + 0.06, name + '_open', 0.4, 'swish')
                self.tl.ev(tc + dur_c, name + '_shut', 0.7, 'thud')
        return f

    def two_panel(self, nA, nB, hinge_yz, t_fly, t_land, t_open, off=(-0.9, -0.9, 0.55), base=None):
        """Folded rigid two-panel piece (duvet, throw): flies in folded, lands, panel B opens over its hinge."""
        hinge = np.array([0, hinge_yz[0], hinge_yz[1]])
        off = np.array(off, float)

        def A(t):
            if t < t_fly:
                return I4, False
            u = c01((t - t_fly) / (t_land - t_fly))
            o = (1 - eoc(u)) * off + np.array([0, 0, 0.15 * math.sin(math.pi * u)])
            Bm = base(t) if base is not None else I4
            return T(*o) @ Bm @ T(0, 0, settle_z(t - t_land, 0.02)), True

        def Bf(t):
            M, v = A(t)
            a = math.pi * (1 - eob(c01((t - t_open) / 0.22), 0.4))
            return M @ about(hinge, R('x', a)), v
        self.tl.custom(nA, A)
        self.tl.custom(nB, Bf)
        self.tl.ev(t_land, nA, 0.5, 'thud'); self.tl.ev(t_open + 0.22, nB + '_open', 0.35, 'tick')

    def drawer(self, t_appear, t_open, t_close, off, base=None, out=0.12, shut=0.17):
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

    def fly_pose(self, name, keys, C, arc=0.15, snd=None):
        """Rigid piece built at pose C, moving through keys [(t, pose4x4, kind)] (kind: 'hop' arcs, 'cut' appears).
        Hidden before the first key."""
        Ci = np.linalg.inv(C)

        def f(t):
            if t < keys[0][0]:
                return I4, False
            for (ta, A, _), (tb, B, kind) in zip(keys, keys[1:]):
                if t < tb:
                    if t < ta:
                        break
                    u = (t - ta) / (tb - ta)
                    if kind == 'hold':
                        return A @ Ci, True
                    uu = eoc(u) if kind == 'skid' else smooth(u)
                    return pose_lerp(A, B, uu, arc if kind == 'hop' else 0.02) @ Ci, True
            # at rest at the latest key reached, with a small settle
            last = None
            for (tk, A, _) in keys:
                if t >= tk:
                    last = (tk, A)
            tau = t - last[0]
            return T(0, 0, settle_z(tau, 0.012)) @ last[1] @ Ci, True
        self.tl.custom(name, f)
        return f


def timeline():
    tl = Timeline(rk, FPS)
    hidden = lambda t: (I4, False)
    kit = Kit(tl)
    if REST:
        if REST_NIGHT:
            for nm in ('bd_day', 'roofs_day'):
                tl.custom(nm, hidden)
        else:
            for nm in ('bd_dusk', 'roofs_dusk'):
                tl.custom(nm, hidden)
        tl.custom('hol_led', hidden)
        tl.custom('ctl', hidden)
        if TOP:
            tl.custom('ceil', hidden)
            for nm in ('tc_body', 'tc_linS', 'tc_linN', 'tc_wdS', 'tc_wdN', 'tc_guest', 'lin0', 'lin1', 'lin2', 'wd_rail', 'wd_armS',
                       'wd_armN', 'bag_slate', 'bag_oat', 'bag_pack', 'rb_deck', 'rb_mat', 'rb_duvet', 'rb_pil', 'rb_ledger', 'dl_on'):
                tl.custom(nm, hidden)
        return tl
    if LONG:
        import long_cut as LC
        import types
        return LC.timeline(tl, kit, types.SimpleNamespace(**globals()))
    return short_timeline(tl, kit)


def bag_floor_poses():
    """Where the guests' bags stand on the floor (entry zone), as poses of the local upright bag."""
    return {'bag_slate': T(0.95, 0.92, 0.012) @ R('z', math.radians(-28)),
            'bag_oat': T(1.38, 1.22, 0.0) @ R('z', math.radians(12)),
            'bag_pack': T(0.60, 1.36, 0.0) @ R('z', math.radians(-60))}


def bags(kit, t_land, t_fly, cam_pos):
    """The three bags skid in past the lens and land on the floor, then fly up into the guest cabinet."""
    FP = bag_floor_poses()
    cam = np.array(cam_pos)
    for i, nm in enumerate(('bag_slate', 'bag_oat', 'bag_pack')):
        Fp = FP[nm]
        start = T(cam[0] + 0.05 + 0.08 * i, cam[1] - 0.05 + 0.10 * i, 0.35) @ R('z', math.radians(40 - 30 * i)) @ R('y', math.radians(-15))
        tl0, tf = t_land[i], t_fly[i]
        C = BAG_C[nm]
        keys = [(tl0 - 0.22, start, 'cut'), (tl0, Fp, 'skid'), (tf - 0.70, Fp, 'hold'), (tf, C, 'hop')]
        kit.fly_pose(nm, keys, C, arc=0.35)
        kit.tl.ev(tl0, nm, 0.85 if i == 0 else 0.6, 'thud')
        kit.tl.ev(tf, nm + '_in', 0.4, 'thud')


def futon(kit, t_lid, t_rise, t_slide, t_shut, t_unfold, step=0.17, lid_more=()):
    """Landing lid lifts, the folded futon rises, slides onto its place, the lid shuts, three clacks unfold it north."""
    tl = kit.tl
    bx0, bx1, by0, by1, bz = BOX
    lid_h = np.array([0, 1.05, PZ])
    kit.door('lid', lid_h, math.radians(-100), 0.0, t_lid, t_shut, axis='x', dur_o=0.22, snd=False, more=lid_more)
    for to, tc in lid_more:
        tl.ev(to + 0.08, 'lid_open', 0.45, 'swish'); tl.ev(tc + 0.18, 'lid_shut', 0.6, 'thud')
    tl.ev(t_lid + 0.08, 'lid_open', 0.45, 'swish'); tl.ev(t_shut + 0.18, 'lid_shut', 0.6, 'thud')
    zb, zt, th, L, y0 = PZ, PZ + FUT_TH, FUT_TH, FUT_L, FUT_Y0
    hinges = [(y0 + L, zt + th), (y0 + 2 * L, zt + th / 2), (y0 + 3 * L, zt)]
    in_box = T(bx0 - FUT_X0, by0 - y0, bz - zb)                                   # folded stack in the box
    on_deck = T(0, 0, 0)

    def ang(k, t):
        ta = t_unfold + step * k
        u = c01((t - ta) / step)
        a = math.pi * (1 - eob(u, 0.5))
        if t > ta + step:
            tau = t - ta - step
            a = -math.radians(2.5) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))
        return a

    def base(t):
        if t < t_rise:
            return in_box
        if t < t_slide:
            u = (t - t_rise) / (t_slide - t_rise)
            return T(0, 0, (PZ - bz + 0.06) * eoc(u)) @ in_box
        u = c01((t - t_slide) / 0.28)
        dx, dy = (FUT_X0 - bx0) * eoc(c01(u * 1.4)), (y0 - by0) * smooth(c01(u * 1.6 - 0.6))
        z = (PZ - bz + 0.06) * (1 - smooth(c01(u * 2 - 1.0)))
        return T(dx, dy, z) @ in_box if u < 1 else on_deck

    for j in range(4):
        def f(t, j=j):
            M = base(t)
            for k in range(j):
                hy, hz = hinges[k]
                M = M @ about((0, hy, hz), R('x', ang(k, t)))
            return M, True
        tl.custom(f'fut{j}', f)
    for k in range(3):
        tl.ev(t_unfold + step * (k + 1), f'fut_clack{k}', 0.55, 'thud')
    tl.ev(t_slide + 0.28, 'fut_place', 0.6, 'thud')


def double_out(kit, t_latch, t_roll, t_roll1, t_rise, t_rise1, t_hide=0.0):
    tl = kit.tl
    dur = t_roll1 - t_roll

    def off(t):
        if t < t_roll:
            dx = DBL_DX
        elif t < t_roll1:
            u = (t - t_roll) / dur
            dx = DBL_DX * (1 - (u * u * (3 - 2 * u) * 0.65 + 0.35 * eoc(u)))
        else:
            tau = t - t_roll1
            dx = -0.012 * math.exp(-tau / 0.06) * math.sin(2 * math.pi * tau / 0.14)
        k = smooth(c01((t - t_rise) / (t_rise1 - t_rise)))
        if t > t_rise1:
            tau = t - t_rise1
            k = 1 + 0.2 * math.exp(-tau / 0.07) * math.sin(math.pi / 2 + 2 * math.pi * tau / 0.20) * (tau < 0.6)
        elif t > t_rise:
            k = eob(c01((t - t_rise) / (t_rise1 - t_rise)), 0.6)
        return dx, -DBL_LIFT * (1 - k), k

    def dbl(t):
        dx, dz, k = off(t)
        return T(dx, 0, dz), t >= t_hide

    def legs(t):
        dx, dz, k = off(t)
        if t < t_rise - 0.06:
            return T(dx, 0, 0) @ S(1, 1, 0.08), t >= t_rise - 0.12
        s = (0.02 + 0.17 * min(k, 1.05)) / 0.19
        return T(dx, 0, 0) @ S(1, 1, max(0.08, s)), True
    tl.custom('dbl', dbl)
    tl.custom('dbl_legs', legs)
    tl.ev(t_latch, 'latch', 0.35, 'tick')
    tl.events.append(dict(t=round(t_roll1, 3), name='roll', strength=0.9, kind='rumble', len=round(dur + 0.05, 3)))
    tl.ev(t_roll1, 'roll_stop', 0.9, 'thud')
    tl.ev(t_rise - 0.04, 'legs_clack', 0.5, 'clank')
    tl.ev(t_rise1, 'rise_clack', 0.6, 'clank')
    return off


def throw_open(kit, t_fly, t_land, t_open, off_fn):
    """Folded oat throw flies onto the double and opens on its two-panel hinge."""
    tl = kit.tl
    hinge = np.array([0, 1.35, 0.517])

    def rid(t):
        dx, dz, _ = off_fn(t)
        return T(dx, 0, dz)

    def A(t):
        if t < t_fly:
            return I4, False
        u = c01((t - t_fly) / (t_land - t_fly))
        o = (1 - eoc(u)) * np.array([-0.9, -0.9, 0.55]) + np.array([0, 0, 0.15 * math.sin(math.pi * u)])
        return T(*o) @ rid(t) @ T(0, 0, settle_z(t - t_land, 0.02)), True

    def B(t):
        M, v = A(t)
        a = math.pi * (1 - eob(c01((t - t_open) / 0.22), 0.4))
        return M @ about(hinge, R('x', a)), v
    tl.custom('dbl_thA', A)
    tl.custom('dbl_thB', B)
    tl.ev(t_land, 'throw', 0.5, 'thud'); tl.ev(t_open + 0.22, 'throw_open', 0.35, 'tick')


def short_timeline(tl, kit):
    ev, drop, slide, grow = tl.ev, tl.drop, tl.slide, tl.grow
    cen = tl.cen
    # ---- light levels (ctl piece): x = dusk mix, y = reading-light swell
    T_DUSK, T_SWELL = 12.2, 12.6

    def ctl(t):
        return T(smooth(c01((t - T_DUSK) / 0.4)), smooth(c01((t - T_SWELL) / 0.9)), 0), False
    tl.custom('ctl', ctl)
    kit.appear('bd_day', -1.0, T_DUSK + 0.2); kit.appear('roofs_day', -1.0, T_DUSK + 0.2)
    kit.appear('bd_dusk', T_DUSK + 0.2); kit.appear('roofs_dusk', T_DUSK + 0.2)
    ev(T_DUSK + 0.2, 'dusk', 0.4, 'swish')
    kit.appear('hol_led', 8.80)

    # ================= S1 (0.0-3.0) doorway dolly: bags, podium, both kids' beds, stair, two lights
    tl.events.append(dict(t=0.02, name='doorbell', strength=0.45, kind='bell'))
    grow('rug', 0.10, 0.34, 'x', (0.20, 0, 0), 0.5, 'swish')
    bags(kit, (0.34, 0.52, 0.70), (6.45, 6.60, 6.75), S1[0]['pos'])
    st_N = drop('pod_N', 0.80, 0.95, 0.45, 0.03, 0.85, 'thud')
    st_M = drop('pod_M', 0.95, 1.10, 0.45, 0.03, 0.85, 'thud')
    st_S = drop('pod_S', 1.10, 1.25, 0.45, 0.03, 0.9, 'thud')
    # things stored inside the podium ride with their section's drop
    drop('lb_mat', 1.26, 1.40, 0.40, 0.04, 0.6, 'thud')
    slide('rb_ledger', 1.36, 1.50, (0, 0, 0.5), 1.0, 0.6, 'clank')
    grow('rb_post', 1.46, 1.60, 'z', (0, 0, PZ), 0.6, 'clank')
    drop('rb_deck', 1.58, 1.72, 0.45, 0.03, 0.85, 'thud')
    drop('rb_mat', 1.72, 1.85, 0.35, 0.04, 0.55, 'thud')
    for k in range(4):
        drop(f'st{k}', 1.88 + 0.12 * k, 2.00 + 0.12 * k, 0.40, 0.04, 0.55 + 0.05 * k, 'thud')
        tl.custom(f'sd{k}', (lambda k: lambda t: (tl.anims[f'st{k}'](t)[0], tl.anims[f'st{k}'](t)[1]))(k))
        kit.appear(f'toys{k}', 99.0)
    slide('ledge', 1.92, 2.04, (0, 0, 0.3), 1.0, 0.3, 'none')
    for j in range(3):
        drop(f'ledge_bk{j}', 2.12 + 0.06 * j, 2.24 + 0.06 * j, 0.25, 0.05, 0.25, 'tick')
    slide('uds', 1.50, 1.62, (0, 0, 0.3), 1.0, 0.3, 'none')
    drop('uds_items', 1.62, 1.76, 0.2, 0.05, 0.25, 'tick')
    drop('porch_cush', 2.58, 2.72, 0.3, 0.06, 0.3, 'tick')
    drop('rb_duvet', 2.34, 2.50, 0.35, 0.03, 0.5, 'thud')
    drop('lb_duvet', 2.34, 2.50, 0.30, 0.03, 0.5, 'none')
    for i, (t_on, pil) in enumerate(((2.65, 'rb_pil'), (2.82, 'lb_pil'))):
        drop(f'rl{i}', t_on - 0.14, t_on - 0.02, 0.15, 0.04, 0.2, 'none')
        kit.appear(f'rl_on{i}', t_on)
        kit.note(t_on, i, 0.35)
        drop(pil, t_on - 0.08, t_on + 0.07, 0.30, 0.08, 0.35, 'tick')

    # ================= S2 (3.3-7.0) west storage wall
    tl.slide('hooks', 3.18, 3.32, (0.45, 0, 0), 1.0, 0.5, 'thud')
    tl.from_camera('coats', 3.30, 3.46, np.array(S2[0]['pos']), 0.4, 0.4, 'tick')
    fc = tl.from_camera('tc_body', 3.02, 3.24, np.array(S2[0]['pos']), 0.35, 0.9, 'thud')
    base_tc = lambda t: fc(t)
    hz = 2.20
    kit.door('tc_linS', (0.418, 0.002, 0), math.radians(-95), 3.18, 3.52, 4.12, base=base_tc)
    kit.door('tc_linN', (0.418, 0.978, 0), math.radians(95), 3.18, 3.56, 4.16, base=base_tc, snd=False)
    for k in range(3):
        tl.from_camera(f'lin{k}', 3.66 + 0.12 * k, 3.84 + 0.12 * k, np.array(S2[0]['pos']), 0.45, 0.45, 'tick')
    kit.door('tc_wdS', (0.418, 0.982, 0), math.radians(-95), 3.18, 4.32, 5.12, base=base_tc)
    kit.door('tc_wdN', (0.418, 1.978, 0), math.radians(95), 3.18, 4.36, 5.16, base=base_tc, snd=False)
    RAIL0, PIV = np.array([0.21, 2.62]), np.array([0.03, 2.66])
    t_dn, t_up = 4.48, 4.90

    def rail_off(t):
        if t < t_dn:
            k = 0.0
        elif t < t_up:
            k = eob(c01((t - t_dn) / 0.28), 0.6)
        else:
            k = 1 - smooth(c01((t - t_up) / 0.22))
        return np.array([0.36 * k, -0.62 * k])

    def rail(t):
        if t < 3.18:
            return I4, False
        o = rail_off(t)
        return T(o[0], 0, o[1]) @ fc(t)[0], True
    tl.custom('wd_rail', rail)

    def arm(t):
        if t < 3.18:
            return I4, False
        o = rail_off(t)
        v0 = RAIL0 - PIV
        v = RAIL0 + o - PIV
        ph0, ph1 = math.atan2(v0[0], v0[1]), math.atan2(v[0], v[1])
        s = np.linalg.norm(v) / np.linalg.norm(v0)
        p = (0, 0, 0)
        M = T(PIV[0], 0, PIV[1]) @ R('y', ph1) @ S(1, 1, s) @ R('y', -ph0) @ T(-PIV[0], 0, -PIV[1])
        return fc(t)[0] @ M, True
    tl.custom('wd_armS', arm); tl.custom('wd_armN', arm)
    ev(t_dn + 0.28, 'rail_down', 0.45, 'swish'); ev(t_up + 0.22, 'rail_up', 0.5, 'thud')
    # desk flap drops, pigeonholes fill
    hinge = np.array([0.0, 0, DZ])
    T_FLAP, T_FOLD = 5.40, 6.92

    def flap(t):
        down = about(hinge, R('y', math.pi / 2))
        if t < T_FLAP:
            return I4, True
        if t < T_FOLD:
            u = c01((t - T_FLAP) / 0.24)
            return about(hinge, R('y', math.pi / 2 * (u * u))), True
        u = c01((t - T_FOLD) / 0.24)
        a = math.pi / 2 * (1 - eob(u, 0.8))
        return about(hinge, R('y', a)), True
    tl.custom('desk_flap', flap)
    grow('niche', 5.30, 5.50, 'z', (0, 0, 1.07), 0.4, 'tick')
    ev(T_FLAP + 0.24, 'flap_down', 0.7, 'thud'); ev(T_FOLD + 0.24, 'flap_up', 0.7, 'thud')
    for c in range(6):
        tl.from_camera(f'pig{c}', 5.62 + 0.11 * c, 5.78 + 0.11 * c, np.array(S3[0]['pos']), 0.35, 0.35, 'tick')
    drop('pots', 6.20, 6.34, 0.25, 0.06, 0.35, 'tick')
    # guest cabinet opens, bags fly in, it shuts
    kit.door('tc_guest', (0.418, 0, 2.69), math.radians(-100), 3.18, 6.10, 6.86, axis='y', base=base_tc)

    # ================= S3 (7.3-10.7) podium at night: futon, the double rolls out
    futon(kit, 7.40, 7.56, 7.74, 7.98, 8.04)
    drop('fut_pil', 8.46, 8.62, 0.3, 0.08, 0.35, 'tick')
    drop('rl2', 8.38, 8.48, 0.15, 0.04, 0.2, 'none')
    kit.appear('rl_on2', 8.52); kit.note(8.52, 2, 0.35)
    off = double_out(kit, 8.62, 8.70, 9.50, 9.62, 10.00)
    throw_open(kit, 9.95, 10.12, 10.16, off)
    for j, (t_on, pil) in enumerate(((10.24, 'dbl_pil1'), (10.40, 'dbl_pil2'))):
        i = 3 + j
        drop(f'rl{i}', t_on - 0.12, t_on - 0.02, 0.15, 0.04, 0.2, 'none')
        kit.appear(f'rl_on{i}', t_on)
        kit.note(t_on, i, 0.35)
        drop(pil, t_on - 0.07, t_on + 0.08, 0.30, 0.08, 0.35, 'tick')

    def nstep(t):
        if t < 1.10:
            return I4, False
        B = tl.anims['pod_S'](t)[0]
        u = c01((t - 10.52) / 0.20)
        k = eob(u, 1.2)
        return B @ T(0.37 * (1 - k), 0, 0), True
    tl.custom('nstep', nstep)
    ev(10.72, 'nstep', 0.6, 'thud')

    # ================= S4 (11.05-15.0) final wide: grandparents, dusk, five lights swell
    for nm, tp in (('gma', 11.40), ('gpa', 11.55)):
        FIGS[nm].animate(tl, pop=tp, sound=0.45)
    drop('cane', 11.58, 11.72, 0.25, 0.03, 0.35, 'tick')
    for i in range(5):
        kit.note(T_SWELL + 0.2 * i, i, 0.12, name=f'echo{i}')

    # pieces stored inside the podium ride its drops
    tl.custom('lid', (lambda f0: lambda t: ((st_S(t)[0] @ f0(t)[0]) if t < 7.0 else f0(t)[0], st_S(t)[1]))(tl.anims['lid']))
    for j in range(4):
        tl.custom(f'fut{j}', (lambda f0: lambda t: ((st_S(t)[0] @ f0(t)[0]) if t < 7.0 else f0(t)[0], st_S(t)[1]))(tl.anims[f'fut{j}']))
    dbl0, legs0 = tl.anims['dbl'], tl.anims['dbl_legs']
    tl.custom('dbl', lambda t: ((st_M(t)[0] @ dbl0(t)[0]) if t < 7.0 else dbl0(t)[0], st_M(t)[1]))
    tl.custom('dbl_legs', lambda t: (legs0(t)[0], legs0(t)[1] and t > 9.0))
    tl.custom('deck_pnl', st_M)
    for nm in ('stoolA', 'stoolB'):
        tl.custom(nm, st_S)
    ns0 = tl.anims['nstep']
    tl.custom('nstep_lid', ns0); tl.custom('slippers', ns0)
    for nm in ('fut_duvA', 'fut_duvB', 'dbl_duvA', 'dbl_duvB', 'mug'):
        kit.appear(nm, 99.0)
    return tl


def music_cfg():
    return {"bpm": 120, "MUSIC": {"drop_at": 0.0, "chords": [[48, 52, 55, 59], [45, 48, 52, 55], [41, 45, 48, 52], [43, 47, 50, 53]],
                                  "roots": [36, 33, 41, 43], "pluck_bars": [], "riser": False}}


if __name__ == '__main__':
    import json
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    timeline().export(DUR, camera, lights, out)
    json.dump(music_cfg(), open(os.path.join(out, 'music.json'), 'w'))
