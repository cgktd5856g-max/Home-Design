"""Three of Us in 3 x 2 m: a 6 m2 bedroom for two parents and a newborn (idea C1).

The double bed goes up wall to wall on a 1.2 m deck, a floor-level crib parks under it by day and rolls out beside
the drawer stair at night, and the baby gets two of the three wardrobe bays. Warm white + light birch + celery accent.
No on-screen text.

    ROOM_REST=1 python3 ../../pipeline/run.py project.py <workdir> probe 0.5,1.5,2.5,3.5        # finished room, stations
    python3 ../../pipeline/run.py project.py <workdir> preview                                   # code-renderer preview
    /root/bpyenv/bin/python ../../pipeline/blender_render.py project.py <outdir> --size 720x1280 ...
ROOM_CUT=15 (default) is the 15 s cut; ROOM_CUT=long is the long cut (same build(), its own holds and timeline).

Units: metres. x = east (0..2.0), y = north (0..3.0), z = up (0..2.9).
North: window over the bed deck (deck y 1.5..3.0, top 1.20). West: 4-step drawer stair (y 0.5..1.5).
East: wardrobe (y 0..1.5, x 1.55..2.0, bays A/B/C). South: doorway (x 0.55..1.45) with a bridge cabinet over it.
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
from camkit import hold_camera
import figure as fg

REST = os.environ.get('ROOM_REST') == '1'
REST_NIGHT = os.environ.get('ROOM_NIGHT') == '1'
CUT = os.environ.get('ROOM_CUT', '15')
LONG = CUT == 'long'

W, D, H = 2.0, 3.0, 2.9
FPS = 25
DUR = 6.0 if REST else (44.0 if LONG else 15.0)

DECK_Y, DECK_Z = 1.5, 1.20                 # deck front edge, deck top
UNDER = 1.10                               # underside of the deck
MAT_Y0, MAT_Y1, MAT_Z = 1.63, 2.98, 1.40   # mattress (x 0.05..1.95), top
WIN = (0.5, 1.5, 1.55, 2.6)                # north window x0, x1, z0, z1
NICHE = (1.60, 1.95, 3.0, 3.12, 1.64, 2.02)  # north-wall niche beside the window: x0, x1, y0 (wall), y1 (back), z0, z1
CRIB = (0.555, 1.115, 0.50, 1.42)          # crib footprint at its night spot (x0, x1, y0, y1)
CRIB_PARK = 1.05                           # +y shift into the day bay (y 1.55..2.47)
PO = (1.17, 1.53, 1.55, 2.90)              # baby pull-out x0, x1, y0 (front), y1
PO_OUT = 1.22
WR_X = 1.55                                # wardrobe front plane
STEP_Y = [0.50, 0.75, 1.00, 1.25]          # stair riser fronts
STEP_Z = [0.24, 0.48, 0.72, 0.96]          # tread tops
DR_OUT = [0.44, 0.64, 0.70, 0.75]          # riser-drawer pull-out
SUN_DIR = np.array([0.18, -0.62, -0.60]) / np.linalg.norm([0.18, -0.62, -0.60])
CAPTIONS = []                              # no on-screen text


# ------------------------------------------------------------------------------------------- materials
def materials():
    mat('subfloor', tex=3, col=srgb(214, 212, 207), p=(0.05,))
    mat('floor', tex=1, col=srgb(226, 200, 164), col2=srgb(210, 182, 146), rough=0.38, f0=0.04, glossy=True, p=(0.16, 1.4))
    mat('wall', tex=3, col=srgb(242, 241, 238), p=(0.02,))
    mat('ceiling', col=srgb(246, 245, 242))
    mat('white_cab', col=srgb(241, 237, 229), rough=0.45)
    mat('white_in', col=srgb(234, 230, 223))
    mat('pgrey', col=srgb(208, 208, 206), rough=0.35, f0=0.04)
    mat('castor', col=srgb(120, 120, 122), rough=0.4)
    wood_mats('birch', srgb(228, 206, 172), seed=8.0)
    mat('celery', tex=3, col=srgb(192, 208, 150), rough=0.5, p=(0.02,))
    mat('winframe', col=srgb(236, 236, 234), rough=0.4)
    mat('sill', col=srgb(240, 238, 233), rough=0.25, f0=0.04, glossy=True)
    mat('mattress', tex=5, col=srgb(245, 243, 238), p=(0, 0.02))
    mat('duvet', tex=5, col=srgb(150, 172, 140), p=(0, 0.014))
    mat('pil_white', tex=3, col=srgb(242, 238, 230), rough=0.9, p=(0.05,))
    mat('pil_sage', tex=6, col=srgb(166, 184, 156))
    mat('throw', tex=5, col=srgb(218, 184, 112), p=(1, 0.012))
    mat('sheet_sky', tex=3, col=srgb(150, 194, 228), rough=0.9, p=(0.04,))
    mat('backdrop', tex=9, emis=(1.35, 1.35, 1.35), p=(1.0, 0.0, 0.0))
    mat('backdrop_dusk', tex=9, emis=(1.05, 0.78, 0.82), p=(1.0, 0.0, 1.0))
    mat('led', col=(0, 0, 0), emis=(7.5, 6.6, 5.0))
    mat('led_off', col=srgb(232, 230, 224))
    mat('bulb', col=(0, 0, 0), emis=(9.0, 7.4, 5.2))
    mat('nl_shell', col=srgb(246, 242, 234), rough=0.3, f0=0.04, glossy=True)
    mat('nl_glow', col=(0, 0, 0), emis=(8.0, 6.0, 3.6))
    mat('phone', col=srgb(20, 20, 22), rough=0.08, f0=0.05, glossy=True)
    mat('mon_glow', col=(0, 0, 0), emis=(0.55, 0.62, 0.70))
    for nm, c in (('cl_coral', (232, 128, 104)), ('cl_teal', (56, 150, 148)), ('cl_mustard', (224, 172, 58)),
                  ('cl_sky', (132, 186, 226)), ('cl_navy', (52, 64, 98)), ('cl_denim', (88, 112, 150)),
                  ('cl_grey', (150, 150, 154)), ('cl_white', (244, 243, 240)), ('cl_sage', (148, 170, 140)),
                  ('cl_lilac', (186, 170, 214))):
        mat(nm, tex=5, col=srgb(*c), p=(2, 0.008))
    for nm, c in (('pk_sky', (140, 190, 228)), ('pk_coral', (236, 140, 116)), ('pk_teal', (70, 160, 156)),
                  ('pk_mustard', (228, 182, 72)), ('pk_white', (246, 245, 242))):
        mat(nm, col=srgb(*c), rough=0.35, f0=0.04)
    for nm, c in (('bk_sage', (150, 168, 144)), ('bk_coral', (214, 128, 100)), ('bk_navy', (54, 66, 100)),
                  ('bk_mustard', (214, 168, 70)), ('bk_white', (240, 238, 232))):
        mat(nm, col=srgb(*c), rough=0.6)
    mat('basket', tex=6, col=srgb(214, 196, 166))
    mat('swaddle', tex=5, col=srgb(244, 240, 232), p=(0, 0.01))
    fg.materials(['fig_adult'])
    mat('fig_p2', col=srgb(150, 172, 206), rough=0.48, f0=0.04)


# ------------------------------------------------------------------------------------------- helpers
def disc(inst, c, r, z0, z1, m, n=28):
    add(inst, lathe(rprof(r, z0, z1, min(0.004, (z1 - z0) * 0.45), 3), n, c), m)


def garment(inst, x, y, z_top, length, width, m, along='x', hanger='pgrey'):
    """Hanging garment on a rail running along `along` (width is across the rail)."""
    if along == 'x':
        add(inst, tube([(x, y - width * 0.45, z_top - 0.04), (x, y, z_top), (x, y + width * 0.45, z_top - 0.04)], 0.0035, 6), hanger)
        add(inst, rbox((x, y, z_top - 0.05 - length / 2), (0.03, width, length), min(0.014, length * 0.2), 3), m)
    else:
        add(inst, tube([(x - width * 0.45, y, z_top - 0.04), (x, y, z_top), (x + width * 0.45, y, z_top - 0.04)], 0.0035, 6), hanger)
        add(inst, rbox((x, y, z_top - 0.05 - length / 2), (width, 0.03, length), min(0.014, length * 0.2), 3), m)


def stack(inst, cx, cy, z0, size, mats_, n, rng):
    z = z0
    for i in range(n):
        sx, sy, sz = size
        jx, jy = rng.uniform(-0.006, 0.006, 2)
        add(inst, rbox((cx + jx, cy + jy, z + sz / 2), (sx * rng.uniform(0.95, 1.0), sy * rng.uniform(0.95, 1.0), sz), sz * 0.45, 3),
            mats_[i % len(mats_)])
        z += sz * 0.96


def cloth(inst, x0, x1, y0, y1, z_top, z_hem, r, m, seed, sides=('s',), puff=0.012):
    """Draped fabric: a gently wrinkled top plus rounded edges falling into softly folded skirts."""
    ph = np.random.default_rng(seed).uniform(0, 6.283, 5)
    yc, hw = (y0 + y1) / 2, (y1 - y0) / 2

    def wob(x, y):
        return (0.008 * math.sin(x * 9 + ph[0]) * math.sin(y * 5 + ph[1]) + 0.005 * math.sin(x * 17 + y * 11 + ph[2])
                + puff * max(0.0, 1 - ((y - yc) / hw) ** 2))
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
            fold = 0.010 * math.sin(u * 14 + ph[3]) + 0.005 * math.sin(u * 31 + ph[4])
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
    if 's' in sides:
        skirt('x', y0, -1, x0, x1)


def pillow(inst, c, size, tilt, yaw, m):
    """Puffy pillow: thick in the middle, pinched at the seam. size = (width, thickness, height) before the yaw."""
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
        add(inst, xform((P, N), T(*c) @ R('z', yaw) @ R('x', tilt)), m)


# ------------------------------------------------------------------------------------------- shell
def build_shell():
    r = 'room'
    add(r, box(-0.004, -3.6, -0.25, W + 0.3, D + 0.2, -0.012), 'subfloor')     # room + hall floor (pale grey)
    add(r, box(-0.6, -0.2, -0.25, -0.004, D + 0.2, -0.004), 'white_cab')         # cut edge under the west wall
    for b in (box(-12, -10, -0.30, 14, 10, -0.26), box(-12, -10, 8.0, 14, 10, 8.1), box(-12, -10, -0.3, -11.9, 10, 8),
              box(13.9, -10, -0.3, 14, 10, 8), box(-12, -10, -0.3, 14, -9.9, 8), box(-12, 9.9, -0.3, 14, 10, 8)):
        add('studio', b, 'ceiling')                                              # white studio around the set
    add(r, box(-0.2, -0.2, H, W + 0.2, D + 0.2, H + 0.35), 'ceiling')
    x0, x1, z0, z1 = WIN
    # north wall with the window
    nx0, nx1, ny0, ny1, nz0, nz1 = NICHE
    add(r, box(-0.2, D, -0.25, x0, D + 0.2, H + 0.35), 'wall'); add(r, box(nx1 + 0.012, D, -0.25, W + 0.2, D + 0.2, H + 0.35), 'wall')
    add(r, box(x1, D, -0.25, nx1 + 0.012, D + 0.2, nz0 - 0.012), 'wall'); add(r, box(x1, D, nz1 + 0.012, nx1 + 0.012, D + 0.2, H + 0.35), 'wall')
    add(r, box(x1, D, nz0 - 0.012, nx0 - 0.012, D + 0.2, nz1 + 0.012), 'wall')
    add(r, box(x0, D, -0.25, x1, D + 0.2, z0), 'wall'); add(r, box(x0, D, z1, x1, D + 0.2, H + 0.35), 'wall')
    for b in (box(x0, D, z0, x0 + 0.006, D + 0.2, z1), box(x1 - 0.006, D, z0, x1, D + 0.2, z1), box(x0, D, z1 - 0.006, x1, D + 0.2, z1)):
        add(r, b, 'sill')
    add(r, box(x0 - 0.03, D - 0.03, z0 - 0.02, x1 + 0.03, D + 0.17, z0), 'sill')
    fy0, fy1 = D + 0.10, D + 0.13
    xm = (x0 + x1) / 2
    for b in (box(x0, fy0, z0, x0 + 0.045, fy1, z1), box(x1 - 0.045, fy0, z0, x1, fy1, z1), box(x0, fy0, z1 - 0.045, x1, fy1, z1),
              box(x0, fy0, z0, x1, fy1, z0 + 0.045), box(xm - 0.02, fy0, z0, xm + 0.02, fy1, z1)):
        add(r, b, 'winframe')
    add(r, box(W, -0.2, -0.25, W + 0.2, D + 0.2, H + 0.35), 'wall')                 # east wall
    # headboard niche in the north wall beside the window (birch-lined)
    nx0, nx1, ny0, ny1, nz0, nz1 = NICHE
    for b in (box(nx0, ny0, nz0 - 0.012, nx1, ny1, nz0), box(nx0, ny0, nz1, nx1, ny1, nz1 + 0.012),
              box(nx0 - 0.012, ny0, nz0, nx0, ny1, nz1), box(nx1, ny0, nz0, nx1 + 0.012, ny1, nz1)):
        add(r, b, 'birch_x')
    add(r, box(nx0, ny1 - 0.012, nz0, nx1, ny1, nz1), 'wall')
    # baseboard on the east wall by the bed bay (rest hidden by furniture)
    # west wall (hidden in the west cut-away shots)
    add('wall_W', box(-0.2, -0.2, -0.25, -0.004, D + 0.2, H + 0.35), 'wall')
    add('wall_W', box(0, 1.55, 0, 0.012, D, 0.07), 'white_cab')
    # south wall with the doorway, plus a white hall stub (hidden in the hall shots)
    s = 'wall_S'
    add(s, box(-0.2, -0.2, -0.25, 0.55, -0.004, H + 0.35), 'wall'); add(s, box(1.45, -0.2, -0.25, W + 0.2, -0.004, H + 0.35), 'wall')
    add(s, box(0.55, -0.2, 2.10, 1.45, -0.004, H + 0.35), 'wall')
    for b in (box(0.53, -0.02, 0, 0.55, 0.012, 2.12), box(1.45, -0.02, 0, 1.47, 0.012, 2.12), box(0.53, -0.02, 2.10, 1.47, 0.012, 2.12)):
        add(s, b, 'white_cab')
    add(s, box(-0.2, -1.8, -0.25, 0.0, -0.2, H + 0.35), 'wall'); add(s, box(W, -1.8, -0.25, W + 0.2, -0.2, H + 0.35), 'wall')
    add(s, box(-0.2, -1.8, -0.25, W + 0.2, -1.6, H + 0.35), 'wall'); add(s, box(-0.2, -1.8, H, W + 0.2, -0.2, H + 0.35), 'ceiling')
    # window views: day and dusk (swapped at T_DUSK)
    add('bd_day', box(-10, D + 4.0, -5, 12, D + 4.05, 9), 'backdrop')
    add('bd_dusk', box(-10, D + 4.02, -5, 12, D + 4.07, 9), 'backdrop_dusk')
    # floor planks in six bands (land far to near)
    edges = [-0.012, 0.5, 1.0, 1.5, 2.0, 2.5, D + 0.01]
    for k in range(6):
        add(f'floor{k}', box(0, edges[k], -0.012, W, edges[k + 1], 0.0), 'floor')


# ------------------------------------------------------------------------------------------- bed deck
def build_deck(rng):
    add('deck', box(0, DECK_Y + 0.02, UNDER, W, D, DECK_Z - 0.02), 'white_cab')
    add('deck', box(0, DECK_Y, DECK_Z - 0.02, W, D, DECK_Z), 'birch_x')
    add('deck', box(0, DECK_Y, UNDER, W, DECK_Y + 0.02, DECK_Z - 0.02), 'birch_x')          # fascia
    add('deck', box(0.52, DECK_Y + 0.03, UNDER - 0.012, 1.14, DECK_Y + 0.05, UNDER), 'led_off')   # crib-bay LED (off)
    add('deck', box(0.0, DECK_Y + 0.02, 0.0, 0.012, D, UNDER), 'white_cab')                     # closed space behind the stair
    add('deck', box(0.50, DECK_Y + 0.05, 0.0, 0.518, D, UNDER), 'white_cab')
    for (a, b) in ((0.48, 0.52), (1.535, 1.575)):
        add('posts', box(a, DECK_Y + 0.005, 0, b, DECK_Y + 0.045, UNDER), 'pgrey')
    # barred guard rail along the deck front (open above the stair)
    g = 'grail'
    gy = DECK_Y + 0.018
    add(g, tube([(0.50, gy, 1.70), (W - 0.02, gy, 1.70)], 0.016, 12), 'pgrey')
    add(g, box(0.50, gy - 0.012, DECK_Z, W - 0.02, gy + 0.012, DECK_Z + 0.03), 'pgrey')
    add(g, box(0.49, gy - 0.015, DECK_Z, 0.52, gy + 0.015, 1.70), 'pgrey')
    for x in np.arange(0.60, W - 0.04, 0.095):
        add(g, box(x - 0.007, gy - 0.007, DECK_Z + 0.03, x + 0.007, gy + 0.007, 1.69), 'pgrey')
    # mattress, duvet, pillows, throw
    add('mattress', rbox((1.0, (MAT_Y0 + MAT_Y1) / 2, (DECK_Z + MAT_Z) / 2), (1.88, MAT_Y1 - MAT_Y0, MAT_Z - DECK_Z), 0.045, 5), 'mattress')
    cloth('duvet', 0.06, 1.56, MAT_Y0 - 0.01, MAT_Y1 - 0.01, MAT_Z + 0.035, MAT_Z - 0.10, 0.04, 'duvet', 3, sides=('s',))
    add('duvet', rbox((1.55, (MAT_Y0 + MAT_Y1) / 2, MAT_Z + 0.05), (0.13, MAT_Y1 - MAT_Y0 - 0.02, 0.035), 0.015, 3), 'duvet')
    pillow('pil1', (1.80, 1.95, MAT_Z + 0.20), (0.60, 0.14, 0.40), -0.30, -math.pi / 2, 'pil_white')
    pillow('pil2', (1.80, 2.50, MAT_Z + 0.20), (0.60, 0.14, 0.40), -0.30, -math.pi / 2, 'pil_sage')
    add('throw', rbox((0.30, 2.30, MAT_Z + 0.075), (0.38, 1.20, 0.05), 0.02, 3), 'throw')
    # niche: night light (shell + glow) and two books with blank spines
    nx0, nx1, ny0, ny1, nz0, nz1 = NICHE
    NL = (1.69, 3.055)
    add('nlight', lathe([(0, nz0), (0.045, nz0), (0.047, nz0 + 0.012), (0.042, nz0 + 0.05), (0.028, nz0 + 0.085), (0, nz0 + 0.095)], 24,
                        NL), 'nl_shell')
    add('nl_on', ellipsoid((NL[0], NL[1], nz0 + 0.04), (0.034, 0.034, 0.042), 10), 'nl_glow')
    add('books', box(1.79, 3.01, nz0, 1.82, 3.10, nz0 + 0.24), 'bk_navy')
    add('books', box(1.822, 3.01, nz0, 1.85, 3.10, nz0 + 0.22), 'bk_mustard')
    add('books', box(1.852, 3.01, nz0, 1.885, 3.10, nz0 + 0.25), 'bk_coral')
    add('books', box(1.887, 3.01, nz0, 1.915, 3.10, nz0 + 0.21), 'bk_sage')
    # reading light clipped onto the guard rail (shade over the pillows)
    rl, cx = 'rlight', 1.78
    add(rl, rbox((cx, gy, 1.70), (0.05, 0.05, 0.06), 0.012, 3), 'pgrey')
    add(rl, tube([(cx, gy, 1.73), (cx, gy + 0.04, 1.86), (cx + 0.02, gy + 0.14, 1.92)], 0.007, 8), 'pgrey')
    add(rl, xform(lathe([(0.012, 0.0), (0.03, -0.012), (0.046, -0.05), (0.05, -0.062)], 24, (0, 0)),
                  T(cx + 0.02, gy + 0.16, 1.92) @ R('x', 0.6)), 'pgrey')
    add('rl_on', ellipsoid((cx + 0.02, gy + 0.18, 1.89), (0.016, 0.016, 0.012), 8), 'bulb')


# ------------------------------------------------------------------------------------------- stair
def build_stair(rng):
    for k in range(4):
        y0, zt = STEP_Y[k], STEP_Z[k]
        zb = zt - 0.24
        st = f'step{k + 1}'
        add(st, box(0, y0 + 0.02, zb, 0.012, DECK_Y, zt - 0.02), 'white_cab')
        add(st, box(0.488, y0 + 0.02, zb, 0.5, DECK_Y, zt - 0.02), 'white_cab')
        add(st, box(0.012, y0 + 0.02, zb, 0.488, DECK_Y, zb + 0.012), 'white_in')
        add(st, box(0, y0 - 0.012, zt - 0.022, 0.5, y0 + 0.25 if k < 3 else DECK_Y, zt), 'birch_x')     # tread
        add(st, box(0.03, y0 - 0.012, zt - 0.034, 0.47, y0 - 0.002, zt - 0.024), 'led_off')                # LED (off)
        # riser drawer: celery front, white box running back (up to 0.95 m)
        dr = f'dr{k + 1}'
        L = 0.95
        add(dr, box(0.016, y0, zb + 0.01, 0.484, y0 + 0.02, zt - 0.03), 'celery')
        add(dr, box(0.18, y0 - 0.004, zt - 0.046, 0.32, y0, zt - 0.038), 'pgrey')               # slim pull
        add(dr, box(0.04, y0 + 0.02, zb + 0.02, 0.46, y0 + L, zb + 0.03), 'white_in')
        for b in (box(0.04, y0 + 0.02, zb + 0.03, 0.052, y0 + L, zt - 0.06), box(0.448, y0 + 0.02, zb + 0.03, 0.46, y0 + L, zt - 0.06),
                  box(0.04, y0 + L - 0.012, zb + 0.03, 0.46, y0 + L, zt - 0.06)):
            add(dr, b, 'white_in')
    # drawer contents (only the front half shows when open)
    sets = [(('cl_navy', 'cl_denim', 'cl_navy'), ('cl_denim', 'cl_grey', 'cl_navy')),
            (('cl_white', 'cl_white', 'cl_white'), ('cl_white', 'cl_sky', 'cl_white')),
            (('cl_teal', 'cl_mustard', 'cl_teal'), ('cl_mustard', 'cl_teal', 'cl_mustard')),
            (('cl_coral', 'cl_sky', 'cl_coral'), ('cl_sky', 'cl_white', 'cl_coral'))]
    for k in range(4):
        y0, zb = STEP_Y[k], STEP_Z[k] - 0.24
        for j, xc in enumerate((0.15, 0.35)):
            for i, yc in enumerate((y0 + 0.17, y0 + 0.43)):
                stack(f'dc{k + 1}_{i}', xc, yc, zb + 0.03, (0.17, 0.22, 0.045), sets[k][j], 3 if k != 1 else 3, rng)
        if k == 3:
            stack('dc4_2', 0.15, y0 + 0.68, zb + 0.03, (0.17, 0.22, 0.045), ('cl_white', 'cl_sky', 'cl_white'), 3, rng)
            stack('dc4_2', 0.35, y0 + 0.68, zb + 0.03, (0.17, 0.22, 0.045), ('cl_sky', 'cl_coral', 'cl_white'), 3, rng)
    # tread LEDs (on)
    for k in range(4):
        y0, zt = STEP_Y[k], STEP_Z[k]
        add(f'led{k + 1}', box(0.03, y0 - 0.013, zt - 0.0345, 0.47, y0 - 0.0015, zt - 0.0235), 'led')
    # handrail on the open (east) side
    hx = 0.505
    p0, p1 = (hx, 0.62, STEP_Z[0]), (hx, 1.37, STEP_Z[3])
    add('handrail', tube([p0, (hx, 0.62, STEP_Z[0] + 0.92)], 0.016, 10), 'pgrey')
    add('handrail', tube([p1, (hx, 1.37, STEP_Z[3] + 0.92)], 0.016, 10), 'pgrey')
    add('handrail', tube([(hx, 0.50, STEP_Z[0] + 0.86), (hx, 0.62, STEP_Z[0] + 0.92), (hx, 1.37, STEP_Z[3] + 0.92),
                          (hx, 1.49, STEP_Z[3] + 0.98)], 0.020, 12), 'pgrey')


# ------------------------------------------------------------------------------------------- crib, crib bay, pull-out
def build_crib(rng):
    x0, x1, y0, y1 = CRIB
    c = 'crib'
    p = 0.038
    for (x, y) in ((x0, y0), (x1 - p, y0), (x0, y1 - p), (x1 - p, y1 - p)):
        add(c, box(x, y, 0.06, x + p, y + p, 0.85), 'birch_z')
        disc(c, (x + p / 2, y + p / 2), 0.022, 0.0, 0.06, 'castor', 16)
    for (a, b, cc, d) in ((x0, y0, x1, y0 + 0.03), (x0, y1 - 0.03, x1, y1)):
        add(c, box(a, b, 0.81, cc, d, 0.85), 'birch_x'); add(c, box(a, b, 0.20, cc, d, 0.25), 'birch_x')
    for (a, b, cc, d) in ((x0, y0, x0 + 0.03, y1), (x1 - 0.03, y0, x1, y1)):
        add(c, box(a, b, 0.81, cc, d, 0.85), 'birch_y'); add(c, box(a, b, 0.20, cc, d, 0.25), 'birch_y')
    for x in np.arange(x0 + 0.075, x1 - 0.05, 0.062):
        for (yy) in (y0 + 0.008, y1 - 0.022):
            add(c, box(x - 0.008, yy, 0.25, x + 0.008, yy + 0.014, 0.81), 'birch_z')
    for y in np.arange(y0 + 0.08, y1 - 0.05, 0.064):
        for xx in (x0 + 0.008, x1 - 0.022):
            add(c, box(xx, y - 0.008, 0.25, xx + 0.014, y + 0.008, 0.81), 'birch_z')
    add(c, box(x0 + 0.03, y0 + 0.03, 0.215, x1 - 0.03, y1 - 0.03, 0.235), 'birch_x')
    add(c, box(x0 + 0.04, y0 - 0.002, 0.075, x1 - 0.04, y0 + 0.02, 0.19), 'birch_x')          # crib drawer front
    add(c, box(x0 + 0.24, y0 - 0.008, 0.155, x1 - 0.24, y0, 0.163), 'pgrey')
    add('crib_mat', rbox(((x0 + x1) / 2, (y0 + y1) / 2, 0.285), (x1 - x0 - 0.075, y1 - y0 - 0.075, 0.10), 0.03, 4), 'sheet_sky')
    # crib-bay open shelf behind the parked crib (with an LED under the deck)
    s = 'cshelf'
    sx0, sx1, sy0, sy1 = 0.53, 1.13, 2.55, 2.95
    add(s, box(sx0, sy1 - 0.015, 0.0, sx1, sy1, 1.08), 'white_in')
    add(s, box(sx0, sy0, 0.0, sx0 + 0.018, sy1, 1.08), 'white_cab'); add(s, box(sx1 - 0.018, sy0, 0.0, sx1, sy1, 1.08), 'white_cab')
    for z in (0.0, 0.36, 0.72):
        add(s, box(sx0, sy0, z, sx1, sy1, z + 0.02), 'birch_x')
    fills = [  # (z, items) nappy packs / wipes / sleepsuit stacks
        [('pk_sky', 0.62, 0.25, 0.20, 0.28), ('pk_sky', 0.84, 0.25, 0.20, 0.28), ('pk_coral', 1.03, 0.20, 0.15, 0.18)],
        [('pk_teal', 0.63, 0.20, 0.17, 0.24), ('pk_coral', 0.83, 0.18, 0.17, 0.22), ('pk_teal', 1.02, 0.18, 0.15, 0.24)],
        [('pk_mustard', 0.64, 0.20, 0.17, 0.16), ('pk_sky', 0.85, 0.18, 0.17, 0.20), ('pk_white', 1.03, 0.16, 0.16, 0.12)],
    ]
    for k, row in enumerate(fills):
        z = (0.02, 0.38, 0.74)[k]
        for i, (m, x, w, d, h) in enumerate(row):
            add(f'cs_f{k}{i}', rbox((x, (sy0 + sy1) / 2 + 0.01, z + h / 2), (w * 0.9, d * 1.6, h), 0.02, 3), m)
    # baby pull-out: birch front, end-on rail of tiny outfits, two bins below
    px0, px1, py0, py1 = PO
    p = 'pullout'
    add(p, box(px0 + 0.004, py0, 0.02, px1 - 0.004, py0 + 0.02, 0.36), 'birch_x')
    add(p, box(px0 + 0.12, py0 - 0.01, 0.30, px1 - 0.12, py0, 0.312), 'pgrey')
    add(p, box((px0 + px1) / 2 - 0.012, py0 + 0.005, 0.36, (px0 + px1) / 2 + 0.012, py0 + 0.03, 1.0), 'pgrey')
    add(p, box(px0 + 0.02, py0 + 0.02, 0.03, px1 - 0.02, py1, 0.045), 'white_in')
    add(p, box(px0 + 0.02, py1 - 0.02, 0.03, px1 - 0.02, py1, 1.0), 'white_in')
    add(p, tube([((px0 + px1) / 2, py0 + 0.03, 0.96), ((px0 + px1) / 2, py1 - 0.03, 0.96)], 0.009, 10), 'pgrey')
    for b in (box(px0 + 0.03, py0 + 0.05, 0.045, px1 - 0.03, py0 + 0.55, 0.30), box(px0 + 0.03, py0 + 0.62, 0.045, px1 - 0.03, py0 + 1.12, 0.30)):
        add(p, b, 'basket')
    for k, m in enumerate(('cl_coral', 'cl_sky', 'cl_mustard', 'cl_teal', 'cl_coral', 'cl_lilac', 'cl_sky')):
        garment(f'po_cl{k}', (px0 + px1) / 2, py0 + 0.12 + k * 0.10, 0.96, rng.uniform(0.30, 0.40), 0.26, m, along='y')
    for k, (m, y) in enumerate((('cl_coral', 0.22), ('cl_teal', 0.42), ('cl_mustard', 0.80), ('cl_sky', 1.00))):
        stack(f'po_bin{k}', (px0 + px1) / 2, py0 + y, 0.30, (0.22, 0.14, 0.03), (m, 'cl_white'), 2, rng)


# ------------------------------------------------------------------------------------------- wardrobe
def build_wardrobe(rng):
    x0, x1 = WR_X, W
    t = 0.018
    b = 'wr_body'
    add(b, box(x1 - t, 0, 0, x1, DECK_Y, H), 'white_in')                          # back
    for y in (0.0, 0.5 - t / 2, 1.0 - t / 2, DECK_Y - t):
        add(b, box(x0 + 0.02, y, 0, x1, y + t, H), 'white_cab' if y in (0.0, DECK_Y - t) else 'white_in')
    add(b, box(x0 + 0.02, 0, 0.20, x1, DECK_Y, 0.218), 'white_in')               # bottom
    add(b, box(x0 + 0.06, 0.5, 0, x0 + 0.08, DECK_Y, 0.20), 'white_cab')         # toe-kick (bays B, C)
    add(b, box(x0 + 0.02, 0, 2.04, x1, DECK_Y, 2.058), 'white_in')               # top-cabinet floor
    add(b, box(x0 + 0.02, 0, H - 0.01, x1, DECK_Y, H), 'white_in')
    add(b, box(x0 + 0.018, 0.0, 0.20, x0 + 0.02, DECK_Y, 0.218), 'white_cab')
    # bay A (baby): changing shelf at 0.90, shelves above, sock shelf below
    for z in (0.90, 1.45, 1.75):
        add(b, box(x0 + 0.06 if z == 0.90 else x0 + 0.03, t, z - 0.018, x1 - t, 0.5 - t / 2, z), 'white_in')
    add(b, box(x0 + 0.03, t, 0.58, x1 - t, 0.5 - t / 2, 0.598), 'white_in')
    # bay B (baby): rail at 1.92, shelves at 1.30 / 0.95 / 0.60
    for z in (1.30, 0.95, 0.60):
        add(b, box(x0 + 0.03, 0.5 + t / 2, z - 0.018, x1 - t, 1.0 - t / 2, z), 'white_in')
    add(b, tube([(1.79, 0.5 + t, 1.92), (1.79, 1.0 - t, 1.92)], 0.009, 10), 'pgrey')
    # bay C (parents): shelf at 0.55 (laundry basket below)
    # top cabinets over B and C (fixed birch doors) + the lift-up flap over A (separate)
    for (a, c2) in ((0.5, 1.0), (1.0, DECK_Y)):
        add(b, box(x0, a + 0.003, 2.06, x0 + t, c2 - 0.003, H - 0.005), 'birch_z')
        add(b, box(x0 - 0.008, c2 - 0.06, 2.10, x0, c2 - 0.05, 2.20), 'pgrey')
    add('wr_topA', box(x0, 0.003, 2.06, x0 + t, 0.497, H - 0.005), 'birch_z')
    add('wr_topA', box(x0 - 0.008, 0.20, 2.08, x0, 0.30, 2.09), 'pgrey')
    # toe-kick step drawer under bay A
    add('wr_step', box(x0, 0.006, 0.02, x0 + t, 0.494, 0.19), 'birch_y')
    add('wr_step', box(x0 + t, 0.03, 0.02, x1 - 0.06, 0.47, 0.035), 'white_in')
    # doors (hinged at their south edges, open toward -x)
    for nm, (a, c2) in (('wr_dA', (0.0, 0.5)), ('wr_dB', (0.5, 1.0)), ('wr_dC', (1.0, DECK_Y))):
        add(nm, box(x0, a + 0.003, 0.215, x0 + t, c2 - 0.003, 2.045), 'birch_z')
        add(nm, box(x0 - 0.01, c2 - 0.055, 0.95, x0, c2 - 0.043, 1.25), 'pgrey')
    # changing flap inside bay A (hinged at the bottom, folds down toward -x) + nappy drawer under it
    fx = x0 + 0.04
    add('wr_flap', box(fx, t + 0.004, 0.902, fx + t, 0.5 - t / 2 - 0.004, 1.40), 'birch_z')
    add('wr_flap', box(fx - 0.006, 0.20, 1.34, fx, 0.30, 1.35), 'pgrey')
    add('wr_mat', rbox((fx - 0.25 + 0.01, 0.25, 0.902 + 0.018 + 0.025), (0.47, 0.42, 0.05), 0.022, 3), 'cl_sky')
    add('wr_mat', rbox((fx - 0.25 + 0.01, 0.25, 0.902 + 0.018 + 0.051), (0.44, 0.39, 0.004), 0.002, 2), 'cl_white')
    n = 'wr_nap'
    add(n, box(fx, t + 0.006, 0.61, fx + t, 0.5 - t / 2 - 0.006, 0.875), 'birch_y')
    add(n, box(fx - 0.006, 0.20, 0.83, fx, 0.30, 0.84), 'pgrey')
    add(n, box(fx + t, 0.04, 0.62, x1 - 0.04, 0.46, 0.632), 'white_in')
    for bb in (box(fx + t, 0.04, 0.632, x1 - 0.04, 0.052, 0.80), box(fx + t, 0.448, 0.632, x1 - 0.04, 0.46, 0.80),
               box(x1 - 0.052, 0.04, 0.632, x1 - 0.04, 0.46, 0.80)):
        add(n, bb, 'white_in')
    stack('wn_c0', 1.70, 0.15, 0.632, (0.18, 0.13, 0.05), ('pk_white', 'pk_white'), 3, rng)
    stack('wn_c0', 1.70, 0.34, 0.632, (0.18, 0.13, 0.05), ('pk_white', 'pk_white'), 3, rng)
    add('wn_c1', rbox((1.86, 0.20, 0.66), (0.10, 0.18, 0.05), 0.015, 3), 'pk_teal')
    add('wn_c1', rbox((1.86, 0.34, 0.655), (0.10, 0.07, 0.04), 0.015, 3), 'pk_coral')
    # wow fills: bay A shelves and bay B rail / shelves (tiny outfits, nappy stacks, baskets)
    stack('wa_f0', 1.72, 0.14, 1.45, (0.30, 0.14, 0.055), ('pk_white', 'pk_white'), 4, rng)
    stack('wa_f0', 1.72, 0.33, 1.45, (0.30, 0.14, 0.055), ('pk_white', 'pk_white'), 4, rng)
    add('wa_f1', rbox((1.76, 0.25, 1.75 + 0.09), (0.32, 0.40, 0.18), 0.03, 3), 'basket')
    for k, (m, y) in enumerate((('cl_coral', 0.12), ('cl_sky', 0.20), ('cl_mustard', 0.28), ('cl_teal', 0.36))):
        add('wa_f1', ellipsoid((1.68, y, 1.95), (0.035, 0.03, 0.022), 8), m)
    add('wa_f2', rbox((1.76, 0.25, 0.218 + 0.10), (0.32, 0.40, 0.20), 0.03, 3), 'basket')
    for k, (m, y) in enumerate((('cl_sky', 0.13), ('cl_coral', 0.22), ('cl_white', 0.30), ('cl_mustard', 0.38))):
        add('wa_f2', ellipsoid((1.67, y, 0.43), (0.035, 0.03, 0.022), 8), m)
    for k, m in enumerate(('cl_coral', 'cl_teal', 'cl_mustard', 'cl_sky', 'cl_coral', 'cl_lilac')):
        garment(f'wb_cl{k}', 1.79, 0.56 + k * 0.073, 1.92, rng.uniform(0.32, 0.42), 0.28, m, along='y')
    for k, z in enumerate((1.30, 0.95, 0.60)):
        mats_ = [('cl_sky', 'cl_white', 'cl_coral'), ('cl_teal', 'cl_mustard', 'cl_white'), ('cl_lilac', 'cl_sky', 'cl_coral')][k]
        stack(f'wb_f{k}', 1.70, 0.63, z, (0.26, 0.20, 0.04), mats_, 4, rng)
        stack(f'wb_f{k}', 1.70, 0.87, z, (0.26, 0.20, 0.04), mats_[::-1], 4, rng)
    add('wb_f3', rbox((1.76, 0.63, 0.218 + 0.13), (0.30, 0.21, 0.26), 0.03, 3), 'basket')
    add('wb_f3', rbox((1.76, 0.87, 0.218 + 0.13), (0.30, 0.21, 0.26), 0.03, 3), 'basket')
    for k, (m, y) in enumerate((('cl_coral', 0.58), ('cl_sky', 0.68), ('cl_teal', 0.82), ('cl_mustard', 0.92))):
        add('wb_f3', ellipsoid((1.66, y, 0.49), (0.04, 0.035, 0.025), 8), m)
    # bay C: one skinny end-on rail (runner + five adult garments) that slides out toward -x
    c = 'wr_rail'
    add(c, tube([(1.79, 1.0 + t, 1.95), (1.79, DECK_Y - t, 1.95)], 0.009, 10), 'pgrey')
    for k, m in enumerate(('cl_navy', 'cl_denim', 'cl_grey')):
        garment(c, 1.79, 1.16 + k * 0.08, 1.95, 0.58 + 0.04 * (k % 2), 0.38, m, along='y')


# ------------------------------------------------------------------------------------------- bridge cabinet over the door
def build_bridge():
    t = 0.018
    b = 'bridge'
    x0, x1, y1, z0 = 0.0, WR_X, 0.35, 2.15
    for bb in (box(x0, 0, z0, x1, y1, z0 + t), box(x0, 0, H - t, x1, y1, H), box(x0, 0, z0, x1, t, H),
               box(x0, 0, z0, x0 + t, y1, H), box(x1 - t, 0, z0, x1, y1, H), box(0.77, 0, z0, 0.788, y1, H)):
        add(b, bb, 'white_cab')
    for (a, c) in ((x0, 0.78), (0.78, x1)):
        add(b, box(a + 0.003, y1, z0 + 0.003, c - 0.003, y1 + t, H - 0.004), 'white_cab')
        add(b, box((a + c) / 2 - 0.06, y1 + t, z0 + 0.03, (a + c) / 2 + 0.06, y1 + t + 0.008, z0 + 0.04), 'pgrey')


def build():
    materials()
    rng = np.random.default_rng(5)
    build_shell()
    build_deck(rng)
    build_stair(rng)
    build_crib(rng)
    build_wardrobe(rng)
    build_bridge()
    add('cshelf_led', box(0.54, DECK_Y + 0.031, UNDER - 0.011, 1.12, DECK_Y + 0.049, UNDER - 0.001), 'led')
    # the people (faceless mannequins): parent 1 on step 2 beside the crib, parent 2 sitting up on the bed
    global P1, P2
    P1 = fg.figure('p1', 'adult', pose=P1_POSE(), at=P1_AT, seat=STEP_Z[1], mat='fig_adult')
    P2 = fg.figure('p2', 'adult', pose=P2_SIT, at=P2_AT, seat=MAT_Z + 0.03, mat='fig_p2')


P1_AT = (0.25, 0.90, 180.0)
P2_AT = (1.55, 2.20, -90.0)
P2_SIT = dict(hip_l=84, hip_r=84, knee_l=8, knee_r=12, ankle_l=10, ankle_r=10, spine=4, neck=6, sh_l=30, sh_r=30,
              sh_l_out=8, sh_r_out=8, elbow_l=30, elbow_r=30)
P2_LIE = dict(hip_l=40, hip_r=40, knee_l=6, knee_r=10, ankle_l=10, ankle_r=10, spine=-6, neck=10, sh_l=20, sh_r=20,
              sh_l_out=14, sh_r_out=14, elbow_l=60, elbow_r=60)
P1, P2 = None, None


def P1_POSE(hand=0.0):
    q = dict(hip_l=88, hip_r=88, knee_l=86, knee_r=86, ankle_l=0, ankle_r=0, spine=8, neck=10,
             sh_l=22, sh_r=30, sh_l_out=6, sh_r_out=6, elbow_l=46, elbow_r=60)
    if hand:
        q = fg.lerp_pose(q, dict(q, sh_l=40, sh_l_out=52, elbow_l=26, spine_side=-8, neck_turn=28, spine=10), hand)
    return q


# ------------------------------------------------------------------------------------------- camera
VFOV = 62.0


def P(x, y, z, yaw, pitch):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch)


P0 = P(1.0, -2.80, 1.40, 0.0, -1.0)
S1 = (P0, P(0.62, -2.20, 2.05, 5.0, -9.0))                       # hall: crane up + push in, tilting down
S2 = (P(0.55, -0.85, 2.15, 1.0, -37.0), P(0.95, -0.95, 2.10, 11.0, -35.0))   # high from the hall: slide east, pan right   # high west over the stair: slide south
S3 = (P(-0.85, 0.95, 1.62, 90.0, -8.0), P(-0.78, 0.62, 1.60, 92.0, -8.0))   # wardrobe, full height: slide south
S4 = (P(1.05, -2.10, 1.18, 3.0, -5.0), P(0.60, -1.98, 1.22, -7.0, -6.0))   # low on the crib + stair: truck left
S5 = (P(1.0, -3.30, 1.02, 0.0, 3.0), P0)                        # hall wide: crane up into P0 (loops to frame 1)
HOLDS15 = [(0.0, 3.2, S1), (3.5, 7.0, S2), (7.3, 10.7, S3), (11.0, 12.95, S4), (13.25, 15.0, S5)]
HALL15 = [0, 1, 3, 4]                                                 # hall holds (south wall hidden), others: west wall hidden

HOLDS, HALL = HOLDS15, HALL15
camera = hold_camera(HOLDS, VFOV, lift=1.0, final_lift=1.5, rest=REST)


def wall_mode(t):
    """'hall' | 'west' | 'swing' for the hold (or the swing) at time t."""
    for i, (t0, t1, _) in enumerate(HOLDS):
        if t0 <= t < t1 or (i == len(HOLDS) - 1 and t >= t0) or (i == 0 and t < t0):
            return 'hall' if i in HALL else 'west'
        if i + 1 < len(HOLDS) and t1 <= t < HOLDS[i + 1][0] and i in HALL and i + 1 in HALL:
            return 'hall'                                            # swing between two hall holds
    return 'swing'


# ------------------------------------------------------------------------------------------- lights (fixed slots)
LSKY = (9.0, 9.6, 10.6)
LDUSK = (9.6, 8.0, 8.6)
LSUN = (38000.0, 34000.0, 28500.0)
LHALL = (1.15, 1.12, 1.06)
LWEST = (1.10, 1.07, 1.02)
LCEIL = (0.55, 0.54, 0.52)
LUNDER = (0.45, 0.43, 0.40)
LHALLTOP = (0.8, 0.78, 0.75)
LREAD = (900.0, 760.0, 540.0)
LTREAD = (80.0, 68.0, 48.0)
LSHELF = (150.0, 128.0, 94.0)
LNIGHT = (45.0, 32.0, 18.0)
T_DUSK = 11.10


def lights(mats4, vis):
    off = (0.0, 0.0, 0.0)
    dusk = bool(vis.get('bd_dusk'))
    fillk = 0.9 if dusk else 1.0

    def k(L, on, f=1.0):
        return tuple(v * f for v in L) if on else off
    x0, x1, z0, z1 = WIN
    Ls = []
    Ls.append(rect_light((x0, D + 0.1, z0), (x1 - x0, 0, 0), (0, 0, z1 - z0), LDUSK if dusk else LSKY, always=1))      # 0 sky (-y)
    sc = np.array([(x0 + x1) / 2, D, (z0 + z1) / 2]) - SUN_DIR * 3.0
    sun = spot_rect(tuple(sc), tuple(SUN_DIR), 0.06, k(LSUN, True, 0.85 if dusk else 1.0), 0.0)
    sun[17] = 1                                                                  # always sampled (the deck shades most points)
    Ls.append(sun)                                                                                                     # 1 sun
    Ls.append(rect_light((0.1, -1.2, 0.3), (0, 0, 2.4), (1.8, 0, 0), k(LHALL, True, fillk)))                          # 2 hall fill (+y)
    Ls.append(rect_light((-0.7, 0.1, 0.3), (0, 2.8, 0), (0, 0, 2.4), k(LWEST, True, fillk)))                          # 3 west fill (+x)
    Ls.append(rect_light((0.15, 0.15, H - 0.04), (0, 1.25, 0), (1.3, 0, 0), k(LCEIL, True, fillk)))                   # 4 ceiling fill (-z)
    Ls.append(rect_light((0.55, 1.6, UNDER - 0.02), (0, 1.3, 0), (0.95, 0, 0), k(LUNDER, True, fillk)))               # 5 under-deck fill
    if vis.get('rlight'):                                                                                              # 6 reading light
        c = mats4['rlight'] @ np.array([1.80, DECK_Y + 0.198, 1.885, 1.0])
        Ls.append(spot_rect(tuple(c[:3]), (0.0, 0.45, -1.0), 0.03, k(LREAD, vis.get('rl_on')), 5.0))
    else:
        Ls.append(spot_rect((1.80, DECK_Y + 0.198, 1.885), (0.0, 0.45, -1.0), 0.03, off, 5.0))
    for i in range(4):                                                                                                 # 7-10 tread LEDs
        y0, zt = STEP_Y[i], STEP_Z[i]
        Ls.append(rect_light((0.03, y0 - 0.006, zt - 0.036), (0.44, 0, 0), (0, -0.006, 0), k(LTREAD, vis.get(f'led{i + 1}'))))
    Ls.append(rect_light((0.54, DECK_Y + 0.03, UNDER - 0.013), (0, 0.02, 0), (0.58, 0, 0), k(LSHELF, vis.get('cshelf_led'))))  # 11
    nz0 = NICHE[4]
    Ls.append(sphere_light((1.69, 3.055 - 0.05, nz0 + 0.06), 0.03, k(LNIGHT, vis.get('nl_on'))))                              # 12 night light
    Ls.append(rect_light((0.1, -1.5, 2.6), (0, 1.4, 0), (1.8, 0, 0), k(LHALLTOP, True, fillk)))                           # 13 hall floor fill
    return Ls


# Blender (Cycles) look: see pipeline/blender_render.py
BLENDER = dict(
    exposure=-0.30,
    look='AgX - Medium High Contrast',
    separate=['backdrop', 'backdrop_dusk'],
    fill_lights=[2, 3, 4, 5, 13],
    wood_scale=(55.0, 1.6),
    bake_rect={'backdrop': (-6.0, 8.0, -2.0, 6.0), 'backdrop_dusk': (-6.0, 8.0, -2.0, 6.0)},
    bake_px={'backdrop': 0.006, 'backdrop_dusk': 0.006, 'floor': 0.0015},
)


# ------------------------------------------------------------------------------------------- timeline
def timeline():
    tl = Timeline(rk, FPS)
    I = np.eye(4)
    hidden = lambda t: (I, False)
    if REST:
        if REST_NIGHT:
            tl.custom('bd_day', hidden)
        else:
            for nm in ('bd_dusk', 'led1', 'led2', 'led3', 'led4', 'cshelf_led', 'nl_on', 'rl_on'):
                tl.custom(nm, hidden)
        # station 0, 3 are hall views (no south wall), 1, 2 west views (no west wall); the crib parked by day
        tl.custom('wall_S', lambda t: (I, int(t) == 2))
        tl.custom('bridge', lambda t: (I, int(t) == 2))
        tl.custom('wall_W', lambda t: (I, int(t) != 2))
        tl.custom('handrail', lambda t: (I, int(t) != 2))
        tl.custom('wr_mat', hidden)
        if not REST_NIGHT:
            tl.custom('crib', lambda t: (T(0, CRIB_PARK, 0), True))
            tl.custom('crib_mat', lambda t: (T(0, CRIB_PARK, 0), True))
            for nm in P1.pieces + P2.pieces:
                tl.custom(nm, hidden)
        return tl
    return timeline_long(tl) if LONG else timeline_15(tl)


def helpers(tl):
    I = np.eye(4)
    ev = tl.ev

    def appear(name, t_on, t_off=None):
        tl.custom(name, lambda t: (I, t >= t_on and (t_off is None or t < t_off)))

    def drawer_fn(t_appear, t_open, t_close, off, base=None, out=0.12, shut=0.17):
        off = np.array(off, float)

        def f(t):
            if t < t_appear:
                return I, False
            B = base(t)[0] if base is not None else I
            if t < t_open:
                return B, True
            if t < t_close:
                return B @ T(*(off * eob((t - t_open) / out, 1.4))), True
            k = 1 - smooth((t - t_close) / shut)
            tau = t - t_close - shut
            wob = 0.006 * math.exp(-tau / 0.05) * math.sin(2 * math.pi * tau / 0.12) if tau > 0 else 0.0
            return B @ T(*(off * k + off / (np.linalg.norm(off) + 1e-9) * wob)), True
        return f

    def hinge(name, piv, axis, a_open, t_open, t_close, d_open=0.22, d_close=0.18, base=None, t_appear=None):
        """Closed -> swings open (ease-out back) -> holds -> swings shut with a small rebound."""
        piv = np.array(piv, float)

        def ang(t):
            if t < t_open:
                return 0.0
            if t < t_close:
                return a_open * eob(c01((t - t_open) / d_open), 0.9)
            u = (t - t_close) / d_close
            if u < 1:
                return a_open * (1 - u * u)
            tau = t - t_close - d_close
            return math.copysign(math.radians(1.6), a_open) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))

        def f(t):
            if t_appear is not None and t < t_appear:
                return I, False
            B = base(t)[0] if base is not None else I
            return B @ about(piv, R(axis, ang(t))), True
        tl.custom(name, f)
        return f

    def wall_vis():
        tl.custom('wall_S', lambda t: (I, wall_mode(t) == 'west'))
        tl.custom('wall_W', lambda t: (I, wall_mode(t) == 'hall'))
    return appear, drawer_fn, hinge, wall_vis


def timeline_15(tl):
    I = np.eye(4)
    cen, ev = tl.cen, tl.ev
    drop, fly, slide, grow = tl.drop, tl.fly, tl.slide, tl.grow
    appear, drawer_fn, hinge, wall_vis = helpers(tl)
    tl.custom('wall_S', lambda t: (I, wall_mode(t) == 'west'))
    tl.custom('wall_W', lambda t: (I, wall_mode(t) == 'hall'))

    # ================= S1 hall (0.0-3.2): crib, planks, posts, DECK SLAM, crib-bay shelf, crib parks, bed
    OFF0 = np.array([0.10, -1.9, 0.75])                              # starts big, near the lens, and lands at 0.26 s

    def crib_land(t, t0=-0.16, t1=0.26):
        u = (t - t0) / (t1 - t0)
        if u < 1:
            return T(*((1 - eoc(u)) * OFF0 + np.array([0, 0, 0.18 * math.sin(math.pi * u)]))), True
        tau = t - t1
        return T(0, 0, 0.04 * math.exp(-tau / 0.09) * abs(math.sin(math.pi * tau / 0.13))), True
    ev(0.26, 'crib', 0.6, 'thud')

    def crib_y(t):
        if t < 1.40:
            return 0.0
        if t < 1.75:
            return CRIB_PARK * smooth((t - 1.40) / 0.35)
        if t < 11.30:
            return CRIB_PARK
        if t < 11.90:
            return CRIB_PARK * (1 - eoc((t - 11.30) / 0.60))
        return 0.0

    def crib_extra(t):
        M = I
        if 0.32 < t < 0.56:                                          # hops as its plank row lands
            M = T(0, 0, 0.025 * math.sin(math.pi * (t - 0.32) / 0.24))
        if 13.90 < t < 14.40:                                        # rocks ~1 cm under parent 1's hand
            M = M @ T(0.010 * math.sin(2 * math.pi * (t - 13.9) / 0.25) * (1 - (t - 13.9) / 0.5), 0, 0)
        return M

    def crib(t):
        M, v = crib_land(t)
        return T(0, crib_y(t), 0) @ crib_extra(t) @ M, v
    tl.custom('crib', crib)
    tl.custom('crib_mat', crib)                                      # the sky sheet rides in with the crib
    ev(1.75, 'crib_park', 0.5, 'roll'); ev(11.90, 'crib_night', 0.5, 'roll')
    for k in range(6):                                               # far to near (band 5 is the north end)
        t1 = 0.16 + 0.06 * (5 - k)
        drop(f'floor{k}', t1 - 0.14, t1, 0.22, 0.05, 0.3 + 0.03 * (5 - k), 'tick')
    drop('posts', 0.50, 0.62, 0.6, 0.04, 0.6, 'thud')
    drop('deck', 0.66, 0.82, 1.2, 0.035, 1.0, 'thud')
    drop('cshelf', 0.84, 0.94, 0.5, 0.03, 0.55, 'thud')
    for i, nm in enumerate(['cs_f00', 'cs_f01', 'cs_f02', 'cs_f10', 'cs_f11', 'cs_f12', 'cs_f20', 'cs_f21', 'cs_f22']):
        t1 = 0.98 + 0.045 * i
        drop(nm, t1 - 0.10, t1, 0.18, 0.06, 0.3, 'pip' if i % 2 == 0 else 'none')
    drop('grail', 1.80, 1.92, 0.40, 0.03, 0.5, 'thud')
    drop('mattress', 1.94, 2.06, 0.45, 0.04, 0.6, 'thud')
    duv = drop('duvet', 2.10, 2.22, 0.40, 0.03, 0.45, 'tick')

    def duvet(t):                                                    # settles when parent 2 lies back
        M, v = duv(t)
        if 14.4 < t < 14.9:
            u = (t - 14.4) / 0.5
            M = about((1.0, 2.3, MAT_Z), S(1, 1, 1 - 0.05 * math.sin(math.pi * u) * (1 - u))) @ M
        return M, v
    tl.custom('duvet', duvet)
    drop('pil1', 2.26, 2.36, 0.35, 0.08, 0.35, 'tick')
    drop('pil2', 2.36, 2.46, 0.35, 0.08, 0.35, 'tick')
    grow('throw', 2.48, 2.62, 'y', (0, 1.70, 0), 0.4, 'tick')
    drop('nlight', 2.66, 2.76, 0.16, 0.05, 0.3, 'pip')
    drop('books', 2.78, 2.88, 0.18, 0.05, 0.3, 'tick')
    slide('rlight', 2.90, 3.04, (0, 0, 0.25), 1.0, 0.35, 'tick')
    rl = tl.anims['rlight']
    tl.custom('rl_on', lambda t: (rl(t)[0], t >= 12.2))
    ev(12.2, 'read_on', 0.6, 'chime')

    # ================= S2 high west (3.5-7.0): stair blocks, handrail, riser drawers fill, baby pull-out
    br = drop('bridge', 7.30, 7.44, 0.35, 0.02, 0.6, 'thud')
    tl.custom('bridge', lambda t: (br(t)[0], br(t)[1] and wall_mode(t) == 'west'))
    steps = []
    for k in range(4):
        t1 = 3.56 + 0.13 * k
        steps.append(drop(f'step{k + 1}', t1 - 0.14, t1, 0.45, 0.03, 0.45 + 0.1 * k, 'thud'))
    hr = drop('handrail', 4.00, 4.10, 0.35, 0.04, 0.4, 'tick')
    tl.custom('handrail', lambda t: (hr(t)[0], hr(t)[1] and not (7.15 <= t < 10.85)))     # hidden in the wardrobe shot
    times = [(4.16, 4.52), (4.48, 4.86), (4.82, 5.22), (5.16, 5.66)]
    for k in range(4):
        to, tc = times[k]
        f = drawer_fn(3.42 + 0.13 * k, to, tc, (0, -DR_OUT[k], 0), base=steps[k], out=0.13 if k < 3 else 0.2)
        tl.custom(f'dr{k + 1}', f)
        ev(to + 0.08, f'dr{k + 1}_open', 0.4, 'swish'); ev(tc + 0.17, f'dr{k + 1}_shut', 0.55 + 0.1 * k, 'thud')
        for i in range(2 if k < 3 else 3):
            nm = f'dc{k + 1}_{i}'
            t1 = to + 0.14 + 0.07 * i + (0.08 if k == 3 else 0.0)
            kind = 'tick' if k == 0 else 'pip'
            drop(nm, t1 - 0.10, t1, 0.16, 0.06, 0.32, kind, parent=f)
    pf = PO_OUT

    def pull(t):
        if t < 5.76:
            return I, False
        if t < 6.00:
            return T(0, -pf * eob((t - 5.76) / 0.24, 0.6), 0), True
        if t < 6.62:
            return T(0, -pf, 0), True
        u = (t - 6.62) / 0.26
        if u < 1:
            return T(0, -pf * (1 - smooth(u)), 0), True
        tau = t - 6.88
        return T(0, -0.006 * math.exp(-tau / 0.05) * math.sin(2 * math.pi * tau / 0.12), 0), True
    tl.custom('pullout', pull)
    ev(5.84, 'po_open', 0.45, 'swish'); ev(6.88, 'po_shut', 0.85, 'thud')
    for k in range(7):
        t1 = 6.04 + 0.075 * k
        drop(f'po_cl{k}', t1 - 0.10, t1, 0.18, 0.05, 0.3, 'pip', parent=pull)
    for k in range(4):
        t1 = 6.10 + 0.09 * k
        drop(f'po_bin{k}', t1 - 0.10, t1, 0.15, 0.05, 0.25, 'none', parent=pull)

    # ================= S3 wardrobe (7.3-10.7): carcass slides out, WOW (doors open, skinny rail, baby bays fill),
    # changing flap, nappy drawer
    body = slide('wr_body', 7.36, 7.70, (0.47, 0, 0), 0.8, 0.85, 'thud')
    for nm in ('wr_topA', 'wr_step'):
        tl.custom(nm, body)
    hinge('wr_dA', (WR_X, 0.0, 0), 'z', math.radians(98), 8.22, 10.60, base=body, t_appear=7.36)
    hinge('wr_dB', (WR_X, 0.5, 0), 'z', math.radians(96), 8.28, 10.64, base=body, t_appear=7.36)
    hinge('wr_dC', (WR_X, 1.0, 0), 'z', math.radians(94), 7.82, 10.68, base=body, t_appear=7.36)
    ev(8.32, 'doors_open', 0.5, 'swish'); ev(10.86, 'doors_shut', 0.85, 'thud')

    tl.custom('wr_rail', body)                   # the parents' skinny rail stays in: their bay is the sparse one
    ev(7.92, 'bayC_bwomp', 0.6, 'bwomp')
    fills = ['wb_cl0', 'wa_f0', 'wb_cl1', 'wb_f0', 'wb_cl2', 'wa_f1', 'wb_cl3', 'wb_f1', 'wb_cl4', 'wa_f2', 'wb_cl5', 'wb_f2', 'wb_f3']
    for i, nm in enumerate(fills):
        t1 = 8.42 + 0.058 * i
        if nm.startswith('wb_cl'):
            fly(nm, t1 - 0.12, t1, (-0.35, 0, 0.05), 0.04, 0.3, 'pip')
        else:
            fly(nm, t1 - 0.12, t1, (-0.45, 0, 0.10), 0.05, 0.3, 'pip')
    fpiv = (WR_X + 0.04, 0, 0.902)

    def flap_ang(t):
        if t < 9.30:
            return 0.0
        if t < 10.40:
            return -math.radians(90) * min(1.0, eob(c01((t - 9.30) / 0.24), 0.4))
        return -math.radians(90) * (1 - smooth(c01((t - 10.40) / 0.18)))

    def flap(t):
        return body(t)[0] @ about(fpiv, R('y', flap_ang(t))), t >= 7.36
    tl.custom('wr_flap', flap)
    ev(9.48, 'flap_down', 0.6, 'thud')
    md = drop('wr_mat', 9.56, 9.68, 0.25, 0.05, 0.4, 'pip')
    tl.custom('wr_mat', lambda t: (flap(t)[0] @ about(fpiv, R('y', math.radians(90))) @ md(t)[0], md(t)[1] and t < 10.42))
    fn = drawer_fn(7.36, 9.78, 10.22, (-0.40, 0, 0), base=body)
    tl.custom('wr_nap', fn)
    ev(9.86, 'nap_open', 0.4, 'swish'); ev(10.39, 'nap_shut', 0.7, 'thud')
    drop('wn_c0', 9.88, 9.98, 0.18, 0.05, 0.3, 'pip', parent=fn)
    drop('wn_c1', 10.00, 10.10, 0.16, 0.05, 0.3, 'pip', parent=fn)

    # ================= S4 hall wide (11.0-15.0): dusk, crib rolls out, parents pop in, staggered lights, late beats
    appear('bd_day', -1.0, T_DUSK)
    appear('bd_dusk', T_DUSK)
    ev(T_DUSK, 'dusk', 0.4, 'swish')
    for i, tt in enumerate((12.40, 12.55, 12.70, 12.85)):
        appear(f'led{i + 1}', tt); ev(tt, f'led{i + 1}', 0.5 + 0.05 * i, 'chime')
    appear('cshelf_led', 13.45); ev(13.45, 'shelf_led', 0.6, 'chime')
    nl = tl.anims['nlight']
    tl.custom('nl_on', lambda t: (nl(t)[0], t >= 13.7)); ev(13.7, 'nightlight', 0.6, 'chime')
    P2.animate(tl, pose=fg.track([(0.0, P2_SIT), (14.0, P2_SIT), (14.6, P2_LIE)]),
               at=P2_AT, seat=MAT_Z + 0.03, pop=11.7)
    P1.animate(tl, pose=lambda t: P1_POSE(smooth(c01((t - 13.6) / 0.3))), at=P1_AT, seat=STEP_Z[1], pop=11.95)
    return tl


def timeline_long(tl):
    raise NotImplementedError('long cut: to do after the 15 s cut')


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    timeline().export(DUR, camera, lights, out)
    json.dump({'bpm': 120, 'MUSIC': dict(drop_at=0, chords=[[57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65], [52, 55, 59, 62]],
                                         roots=[45, 41, 43, 40], pluck_bars=list(range(12)), riser=False)},
              open(os.path.join(out, 'music.json'), 'w'))
