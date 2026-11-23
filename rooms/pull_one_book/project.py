"""Pull One Book: a 9.2 m² kids' loft room (3.4 x 2.7 m) that builds around a loft bed and a wall of colourful books.
A child tugs one coral book, pushes a loaded bookcase section back and slides it aside like a pocket door onto a lit
den under the loft, and the toys on the floor fly in. Neutral white shell + pale birch + one muted coral accent.
No on-screen text.

    ROOM_REST=1 python3 ../../pipeline/run.py project.py <workdir> probe 0.5,1.5,2.5,3.5     # finished room, stations
    ROOM_REST=1 ROOM_OPEN=1 ...                                                              # same, section open, den lit
    python3 ../../pipeline/run.py project.py <workdir> preview                               # code-renderer preview
    /root/bpyenv/bin/python ../../pipeline/blender_render.py project.py <outdir> ...         # photo-real frames
    ROOM_CUT=long selects the 45 s cut (default: the 15 s cut).

Units: metres. x = east, y = north, z = up. Room x 0..W, y 0..D, z 0..H.
West wall: loft deck (x 0..1.20, top 1.50) over the book wall (front x 1.20) and the den behind it.
North wall: the book stair (y 2.10..2.70, rising west from x 2.40) and the wardrobe tower (x 2.90..3.40).
South wall: window (x 1.45..2.35) and desk. East wall: door (y 0.90..1.70), hooks, print, plant.
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
REST_OPEN = os.environ.get('ROOM_OPEN') == '1'
REST_NIGHT = os.environ.get('ROOM_NIGHT') == '1'
CUT = os.environ.get('ROOM_CUT', 'short')
LONG = CUT == 'long'

W, D, H = 3.4, 2.7, 2.7
FPS = 25
DUR = 6.0 if REST else (45.5 if LONG else 15.0)

DECK_X, DECK_Z0, DECK_Z1 = 1.20, 1.45, 1.50        # loft deck: x 0..1.20, underside / top
BW_X0, BW_X1 = 0.95, 1.20                           # book wall back / front
SEC_Y0, SEC_Y1 = 0.70, 1.55                         # sliding section (closed)
SHELF_Z = (0.42, 0.78, 1.12)                        # shelf boards (bottom faces)
WIN = (1.45, 2.35, 0.85, 2.20)                      # south window x0, x1, z0, z1
DL = [(1.80, 0.85), (2.75, 0.85), (1.80, 1.80), (2.75, 1.80)]
SUN_DIR = np.array([-0.12, 0.80, -0.58]) / np.linalg.norm([-0.12, 0.80, -0.58])
STAIR_X = [2.40 - 0.24 * k for k in range(5)]       # riser faces (east) of the five treads
CAPTIONS = []                                       # no on-screen text


# ------------------------------------------------------------------------------------------- materials
BOOK_COLS = {
    'bk_terra': (192, 116, 86), 'bk_mustard': (218, 172, 76), 'bk_rust': (172, 94, 66), 'bk_sage': (150, 170, 140),
    'bk_slate': (92, 108, 128), 'bk_dusty': (140, 164, 192), 'bk_white': (238, 237, 233), 'bk_yellow': (230, 202, 118),
    'bk_grey': (178, 180, 182), 'bk_teal': (98, 146, 146), 'bk_blush': (220, 170, 156), 'bk_greyblue': (124, 144, 168),
}
WALL_MIX = ['bk_mustard', 'bk_yellow', 'bk_sage', 'bk_slate', 'bk_dusty', 'bk_white', 'bk_teal', 'bk_grey', 'bk_mustard',
            'bk_yellow', 'bk_sage', 'bk_greyblue']
WARM_MIX = ['bk_terra', 'bk_mustard', 'bk_rust', 'bk_sage', 'bk_slate', 'bk_dusty', 'bk_white', 'bk_yellow', 'bk_terra',
            'bk_mustard', 'bk_teal', 'bk_blush', 'bk_sage', 'bk_grey']


def materials():
    mat('subfloor', tex=3, col=srgb(160, 158, 155), p=(0.12,))
    mat('floor', tex=1, col=srgb(214, 190, 156), col2=srgb(196, 170, 136), rough=0.4, f0=0.04, glossy=True, p=(0.16, 1.4))
    mat('wall', tex=3, col=srgb(242, 241, 238), p=(0.015,))
    mat('ceiling', col=srgb(246, 246, 244))
    mat('white_cab', col=srgb(241, 241, 238), rough=0.45)
    mat('white_in', col=srgb(236, 236, 233))
    wood_mats('birch', srgb(230, 212, 182), seed=6.0)
    wood_mats('oak', srgb(214, 186, 148), seed=2.0)
    mat('coral', tex=3, col=srgb(222, 130, 110), rough=0.55, p=(0.02,))
    mat('coral_book', col=srgb(226, 120, 100), rough=0.5)
    mat('alu', col=srgb(200, 202, 206), rough=0.3, metal=1)
    mat('rubber', col=srgb(206, 208, 210), rough=0.7)
    mat('track', col=srgb(222, 222, 220), rough=0.55)
    mat('winframe', col=srgb(236, 236, 234), rough=0.35)
    mat('sill', col=srgb(240, 239, 236), rough=0.25, f0=0.04, glossy=True)
    mat('mattress', tex=5, col=srgb(245, 244, 240), p=(0, 0.02))
    mat('linen', tex=3, col=srgb(240, 240, 238), rough=0.9, p=(0.04,))
    mat('pil_coral', tex=6, col=srgb(226, 150, 128))
    mat('pil_white', tex=3, col=srgb(242, 241, 238), rough=0.9, p=(0.05,))
    mat('pil_sage', tex=6, col=srgb(166, 184, 158))
    mat('rug', tex=6, col=srgb(226, 224, 218))
    mat('blind', tex=3, col=srgb(240, 239, 235), emis=(0.08, 0.08, 0.078), rough=0.9, p=(0.03,))
    mat('weave', tex=5, col=srgb(160, 180, 156), p=(1, 0.01))
    mat('weave_w', tex=5, col=srgb(226, 224, 216), p=(1, 0.01))
    mat('plush', tex=6, col=srgb(214, 204, 190))
    mat('plush2', tex=6, col=srgb(170, 190, 210))
    mat('ceramic', col=srgb(244, 243, 240), rough=0.22, f0=0.04, glossy=True)
    mat('terra', col=srgb(200, 132, 100))
    mat('leaf', col=srgb(70, 118, 64)); mat('leaf2', col=srgb(100, 146, 78))
    mat('blackm', col=srgb(40, 40, 42), rough=0.4, f0=0.04, glossy=True)
    mat('paper', col=srgb(244, 243, 240))
    mat('fig_kid', col=srgb(118, 160, 212), rough=0.48, f0=0.04)
    for nm, c in BOOK_COLS.items():
        mat(nm, col=srgb(*c), rough=0.6)
    for nm, c in (('toy_coral', (226, 122, 100)), ('toy_mustard', (226, 180, 70)), ('toy_sage', (140, 176, 130)),
                  ('toy_blue', (110, 156, 206)), ('toy_white', (240, 240, 236)), ('toy_teal', (88, 156, 150))):
        mat(nm, col=srgb(*c), rough=0.35, f0=0.04, glossy=True)
    for nm, c in (('cl_white', (242, 242, 240)), ('cl_coral', (224, 140, 120)), ('cl_sky', (160, 190, 220)),
                  ('cl_mustard', (220, 182, 96)), ('cl_sage', (156, 178, 148)), ('cl_grey', (176, 178, 182)),
                  ('cl_denim', (98, 126, 166)), ('cl_blush', (226, 186, 176))):
        mat(nm, tex=5, col=srgb(*c), p=(2, 0.008))
    mat('shoe_white', col=srgb(242, 242, 238), rough=0.5); mat('shoe_blue', col=srgb(120, 156, 200), rough=0.5)
    mat('backpack', tex=3, col=srgb(150, 172, 146), rough=0.8, p=(0.04,))
    mat('panel', col=(0, 0, 0), emis=(6.2, 5.9, 5.2))
    mat('panel_off', col=srgb(244, 244, 242), rough=0.3)
    mat('bulb', col=(0, 0, 0), emis=(9.0, 7.8, 6.0))
    mat('dl_emis', col=(0, 0, 0), emis=(8.5, 7.9, 6.8))
    mat('led_off', col=srgb(232, 232, 228))
    mat('backdrop', tex=9, emis=(1.35, 1.35, 1.35), p=(1.0, 0.0))
    mat('backdrop_night', tex=9, emis=(0.80, 0.86, 1.0), p=(1.0, 0.0))     # early evening: the day view, dimmed and cooler


# ------------------------------------------------------------------------------------------- helpers
def disc(inst, c, r, z0, z1, m, n=28):
    add(inst, lathe(rprof(r, z0, z1, min(0.004, (z1 - z0) * 0.45), 3), n, c), m)


def garment(inst, x, y, z_top, length, width, m, along='x'):
    """Hanging garment on a rail running along `along` (width is across the rail)."""
    if along == 'x':
        add(inst, tube([(x, y - width * 0.45, z_top - 0.05), (x, y, z_top), (x, y + width * 0.45, z_top - 0.05)], 0.004, 6), 'alu')
        add(inst, rbox((x, y, z_top - 0.06 - length / 2), (0.035, width, length), 0.016, 3), m)
    else:
        add(inst, tube([(x - width * 0.45, y, z_top - 0.05), (x, y, z_top), (x + width * 0.45, y, z_top - 0.05)], 0.004, 6), 'alu')
        add(inst, rbox((x, y, z_top - 0.06 - length / 2), (width, 0.035, length), 0.016, 3), m)


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
        add(inst, xform(ellipsoid(c, (0.016 * leaf ** 0.5, 0.016 * leaf ** 0.5, L * 0.55), 7), about(c, R('z', a) @ R('x', lean * 0.6))),
            'leaf' if k % 2 else 'leaf2')


def pillow(inst, c, size, tilt, m, yaw=0.0):
    """Puffy pillow: thick in the middle, pinched along the seam. size = (width x, thickness y, height z)."""
    c = np.array(c, float)
    hw, t0, hh = size[0] / 2, size[1], size[2] / 2
    n = 18
    us = np.linspace(-1, 1, n)
    for sg in (1, -1):
        V = np.zeros((n, n, 3))
        for i, u in enumerate(us):
            for j, v in enumerate(us):
                th = t0 * 0.5 * max(0.0, (1 - abs(u) ** 3.5) * (1 - abs(v) ** 3.5)) ** 0.55 + 0.004
                corner = 1 - 0.06 * (abs(u) * abs(v)) ** 3
                V[i, j] = (u * hw * corner, sg * th, v * hh * corner)
        add(inst, xform(grid_tris(V), T(*c) @ R('z', yaw) @ R('x', tilt)), m)


def basket(inst, cx, cy, z0, sx, sy, h, m, t=0.012):
    for b in (box(cx - sx / 2, cy - sy / 2, z0, cx + sx / 2, cy + sy / 2, z0 + t),
              box(cx - sx / 2, cy - sy / 2, z0, cx + sx / 2, cy - sy / 2 + t, z0 + h),
              box(cx - sx / 2, cy + sy / 2 - t, z0, cx + sx / 2, cy + sy / 2, z0 + h),
              box(cx - sx / 2, cy - sy / 2, z0, cx - sx / 2 + t, cy + sy / 2, z0 + h),
              box(cx + sx / 2 - t, cy - sy / 2, z0, cx + sx / 2, cy + sy / 2, z0 + h)):
        add(inst, b, m)


def books_x(inst, x_front, y0, y1, z0, hmax, rng, palette, gap_every=0, lean_end=False):
    """Spine-out books facing +x (spines at x_front), standing on z0, filling y0..y1."""
    y = y0 + 0.004
    while y < y1 - 0.02:
        th = rng.uniform(0.018, 0.042)
        if y + th > y1 - 0.003:
            break
        h = hmax * rng.uniform(0.62, 0.96)
        d = rng.uniform(0.15, 0.19)
        xf = x_front - rng.uniform(0.004, 0.014)
        add(inst, box(xf - d, y, z0, xf, y + th, z0 + h), palette[int(rng.integers(len(palette)))])
        y += th + 0.0015


def books_mx(inst, x_back, y0, y1, z0, hmax, rng, palette, depth=(0.15, 0.19)):
    """Spine-out books facing +x inside a cubby whose open face is at x_back + depth."""
    books_x(inst, x_back + depth[1] + 0.01, y0, y1, z0, hmax, rng, palette)


# ------------------------------------------------------------------------------------------- shell
def build_shell():
    r = 'room'
    x0w, x1w, z0w, z1w = WIN
    add(r, box(-0.2, -0.2, -0.25, W + 0.2, D + 0.2, -0.012), 'subfloor')
    add(r, box(-0.2, -0.2, H, W + 0.2, D + 0.2, H + 0.1), 'ceiling')
    add(r, box(-0.2, -0.2, -0.25, 0, D + 0.2, H + 0.1), 'wall')                     # west
    add(r, box(-0.2, D, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')                  # north
    # south wall with the window
    add(r, box(-0.2, -0.2, -0.25, x0w, 0, H + 0.1), 'wall'); add(r, box(x1w, -0.2, -0.25, W + 0.2, 0, H + 0.1), 'wall')
    add(r, box(x0w, -0.2, -0.25, x1w, 0, z0w), 'wall'); add(r, box(x0w, -0.2, z1w, x1w, 0, H + 0.1), 'wall')
    for b in (box(x0w, -0.2, z0w, x0w + 0.006, 0, z1w), box(x1w - 0.006, -0.2, z0w, x1w, 0, z1w), box(x0w, -0.2, z1w - 0.006, x1w, 0, z1w)):
        add(r, b, 'sill')
    add(r, box(x0w - 0.03, -0.17, z0w - 0.02, x1w + 0.03, 0.035, z0w), 'sill')
    fy0, fy1 = -0.13, -0.10
    xm = (x0w + x1w) / 2
    for b in (box(x0w, fy0, z0w, x0w + 0.04, fy1, z1w), box(x1w - 0.04, fy0, z0w, x1w, fy1, z1w), box(x0w, fy0, z1w - 0.04, x1w, fy1, z1w),
              box(x0w, fy0, z0w, x1w, fy1, z0w + 0.04), box(xm - 0.018, fy0, z0w, xm + 0.018, fy1, z1w)):
        add(r, b, 'winframe')
    # east wall with the door (y 0.90..1.70)
    add(r, box(W, -0.2, -0.25, W + 0.2, 0.90, H + 0.1), 'wall'); add(r, box(W, 1.70, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
    add(r, box(W, 0.90, 2.10, W + 0.2, 1.70, H + 0.1), 'wall')
    add(r, box(W + 0.02, 0.90, 0, W + 0.06, 1.70, 2.10), 'white_cab')               # door slab
    add(r, tube([(W + 0.02, 0.98, 1.0), (W - 0.04, 0.98, 1.0), (W - 0.04, 1.10, 1.0)], 0.009, 10), 'alu')
    for b in (box(W - 0.012, 0.88, 0, W + 0.02, 0.90, 2.12), box(W - 0.012, 1.70, 0, W + 0.02, 1.72, 2.12),
              box(W - 0.012, 0.88, 2.10, W + 0.02, 1.72, 2.12)):
        add(r, b, 'white_cab')
    # baseboards
    for b in (box(DECK_X, D - 0.012, 0, W, D, 0.07), box(W - 0.012, 0, 0, W, 0.88, 0.07), box(W - 0.012, 1.72, 0, W, D, 0.07),
              box(DECK_X, 0, 0, x0w, 0.012, 0.07), box(x1w, 0, 0, W, 0.012, 0.07)):
        add(r, b, 'white_cab')
    # downlights (off) in the ceiling
    for (x, y) in DL:
        add(r, lathe([(0.034, H - 0.002), (0.046, H - 0.002), (0.047, H - 0.010), (0.050, H - 0.012), (0.052, H)], 32, (x, y)), 'white_cab')
        disc(r, (x, y), 0.036, H - 0.003, H - 0.0005, 'led_off')
    # window views: day and blue hour
    add('bd_day', box(-10, -4.05, -5, 14, -4.0, 9), 'backdrop')
    add('bd_night', box(-10, -4.07, -5, 14, -4.02, 9), 'backdrop_night')
    # floor planks in six bands across the room (land far to near, seen from the east)
    edges = [-0.05, 0.60, 1.20, 1.75, 2.30, 2.85, W + 0.01]
    for k in range(6):
        add(f'floor{k}', box(edges[k], 0, -0.012, edges[k + 1], D, 0.0), 'floor')


# ------------------------------------------------------------------------------------------- loft + book wall + den
def build_loft(rng):
    t = 0.018
    # deck (with a fascia over the book wall and a plain sixth riser at the stair end)
    wood('deck', 0.0, 0.0, DECK_Z0, DECK_X, D, DECK_Z1, 'birch')
    add('deck', box(DECK_X - t, 2.10, 1.25, DECK_X, D, DECK_Z0), 'birch_y')
    # coral guard rail along the deck edge, y 0..2.30 (the way up is y 2.30..2.70)
    rl = 'rail'
    for y in (0.02, 0.78, 1.54, 2.26):
        add(rl, box(DECK_X - 0.045, y, DECK_Z1, DECK_X - 0.005, y + 0.04, 2.08), 'coral')
    add(rl, box(DECK_X - 0.05, 0.0, 2.04, DECK_X, 2.30, 2.09), 'coral')
    for y in np.arange(0.12, 2.24, 0.11):
        add(rl, box(DECK_X - 0.035, y, DECK_Z1, DECK_X - 0.015, y + 0.022, 2.04), 'coral')
    # mattress, duvet, pillows, plush, clip-on reading lamp
    add('mattress', rbox((0.56, 1.00, 1.585), (0.90, 1.90, 0.15), 0.05, 5), 'mattress')
    add('duvet', rbox((0.56, 0.78, 1.675), (0.94, 1.46, 0.05), 0.022, 4), 'linen')
    add('duvet', rbox((0.56, 1.46, 1.69), (0.94, 0.16, 0.07), 0.03, 4), 'linen')
    pillow('pillow', (0.56, 1.75, 1.72), (0.62, 0.12, 0.30), -1.25, 'pil_white')
    pillow('pillow2', (0.40, 1.60, 1.73), (0.30, 0.10, 0.28), -1.0, 'pil_coral', yaw=0.3)
    plush_toy('loft_plush', (0.80, 1.55, 1.70), 0.85, 'plush2', yaw=-0.6)
    add('loft_throw', rbox((0.56, 0.26, 1.705), (0.92, 0.30, 0.05), 0.02, 4), 'pil_sage')
    for k, m in enumerate(('bk_dusty', 'bk_mustard', 'bk_terra')):
        add('loft_books', box(0.40 - 0.01 * k, 2.28 + 0.008 * k, DECK_Z1 + 0.02 * k, 0.62 - 0.01 * k, 2.44 + 0.008 * k, DECK_Z1 + 0.02 * (k + 1)), m)
    basket('loft_basket', 0.80, 2.48, DECK_Z1, 0.30, 0.24, 0.18, 'weave')
    ll = 'loft_lamp'
    add(ll, box(DECK_X - 0.06, 1.92, 2.04, DECK_X + 0.01, 1.98, 2.10), 'white_cab')
    add(ll, tube([(DECK_X - 0.03, 1.95, 2.09), (DECK_X - 0.06, 1.95, 2.20), (DECK_X - 0.16, 1.95, 2.22)], 0.007, 8), 'white_cab')
    add(ll, lathe([(0.008, 2.245), (0.03, 2.235), (0.055, 2.18), (0.06, 2.17)], 24, (DECK_X - 0.18, 1.95)), 'white_cab')
    add('loft_lamp_on', ellipsoid((DECK_X - 0.18, 1.95, 2.19), (0.018, 0.018, 0.012), 8), 'bulb')


def plush_toy(inst, c, s, m, yaw=0.0):
    """A generic soft toy: body, head, two round ears, little arms and feet. No face."""
    c = np.array(c, float)
    M = T(*c) @ R('z', yaw) @ S(s, s, s)
    parts = [ellipsoid((0, 0, 0.0), (0.065, 0.055, 0.075), 12), ellipsoid((0, 0, 0.11), (0.055, 0.05, 0.05), 12),
             ellipsoid((-0.038, 0, 0.155), (0.018, 0.012, 0.018), 8), ellipsoid((0.038, 0, 0.155), (0.018, 0.012, 0.018), 8),
             ellipsoid((-0.07, 0.01, 0.01), (0.02, 0.02, 0.04), 8), ellipsoid((0.07, 0.01, 0.01), (0.02, 0.02, 0.04), 8),
             ellipsoid((-0.035, 0.035, -0.065), (0.025, 0.03, 0.02), 8), ellipsoid((0.035, 0.035, -0.065), (0.025, 0.03, 0.02), 8)]
    for p in parts:
        add(inst, xform(p, M), m)


def build_bookwall(rng):
    t = 0.018
    x0, x1 = BW_X0, BW_X1
    top = DECK_Z0
    # fixed runs: south y 0..0.70, north y 1.55..2.10 (carcass: gables, base, top, back)
    for nm, (y0, y1) in (('bwS', (0.0, SEC_Y0)), ('bwN', (SEC_Y1, 2.10))):
        c = f'{nm}_car'
        add(c, box(x0, y0, 0.0, x1, y0 + t, top), 'birch_z'); add(c, box(x0, y1 - t, 0.0, x1, y1, top), 'birch_z')
        add(c, box(x0 + 0.01, y0 + t, 0.0, x1 - 0.02, y1 - t, 0.06), 'white_cab')
        add(c, box(x0, y0 + t, 0.06, x1, y1 - t, 0.078), 'birch_y')
        add(c, box(x0, y0 + t, top - 0.018, x1, y1 - t, top), 'birch_y')
        add(c, box(x0, y0 + t, 0.06, x0 + 0.008, y1 - t, top), 'white_in')
        sh = f'{nm}_sh'
        for z in SHELF_Z:
            add(sh, box(x0 + 0.008, y0 + t, z, x1, y1 - t, z + t), 'birch_y')
            add(sh, box(x1 - 0.004, y0 + t, z + t, x1, y1 - t, z + t + 0.02), 'birch_y')       # 2 cm shelf lip
    # the sliding section, y 0.70..1.55, top 1.42 (the top track runs above it)
    c = 'sec_car'
    st = 1.42
    add(c, box(x0, SEC_Y0, 0.012, x1, SEC_Y0 + t, st), 'birch_z'); add(c, box(x0, SEC_Y1 - t, 0.012, x1, SEC_Y1, st), 'birch_z')
    add(c, box(x0 + 0.01, SEC_Y0 + t, 0.012, x1 - 0.02, SEC_Y1 - t, 0.06), 'white_cab')
    add(c, box(x0, SEC_Y0 + t, 0.06, x1, SEC_Y1 - t, 0.078), 'birch_y')
    add(c, box(x0, SEC_Y0 + t, st - t, x1, SEC_Y1 - t, st), 'birch_y')
    add(c, box(x0, SEC_Y0 + t, 0.06, x0 + 0.012, SEC_Y1 - t, st), 'birch_x')                   # back panel (den side)
    add(c, box(x0 - 0.02, 1.05, 0.62, x0 - 0.008, 1.20, 0.65), 'alu')                          # pull on the back face
    add(c, box(x0 + 0.02, SEC_Y0 - 0.006, 0.08, x1 - 0.02, SEC_Y0, st - 0.04), 'rubber')       # finger guard (leading edge)
    add(c, box(x1 - 0.06, SEC_Y1 - 0.05, st - 0.004, x1 - 0.01, SEC_Y1 - 0.02, st + 0.012), 'alu')  # latch
    for y in (SEC_Y0 + 0.08, SEC_Y1 - 0.08):                                                   # castors on the floor runners
        for x in (x0 + 0.05, x1 - 0.05):
            add(c, xform(lathe(rprof(0.022, -0.011, 0.011, 0.004, 2), 14, (0, 0)), T(x, y, 0.024) @ R('x', math.pi / 2)), 'blackm')
    sh = 'sec_sh'
    for z in SHELF_Z:
        add(sh, box(x0 + 0.012, SEC_Y0 + t, z, x1, SEC_Y1 - t, z + t), 'birch_y')
        add(sh, box(x1 - 0.004, SEC_Y0 + t, z + t, x1, SEC_Y1 - t, z + t + 0.02), 'birch_y')
    # floor runners (L: into the den, then south behind the fixed run) and the top track
    for y in (SEC_Y0 + 0.08, SEC_Y1 - 0.08):
        add('runners', box(0.62, y - 0.012, 0.0, x1 - 0.01, y + 0.012, 0.003), 'track')
    for x in (0.70, 0.85):
        add('runners', box(x - 0.012, 0.02, 0.0, x + 0.012, SEC_Y1 - 0.05, 0.003), 'track')
    add('track', box(0.62, SEC_Y0 + 0.10, 1.425, x1 - 0.01, SEC_Y1 - 0.10, DECK_Z0 - 0.013), 'track')
    add('track', box(0.70, 0.02, 1.425, 0.86, SEC_Y1 - 0.10, DECK_Z0 - 0.013), 'track')
    # books: per run and shelf level (z0, height)
    levels = [(0.078, 0.33), (0.438, 0.33), (0.798, 0.31), (1.138, 0.27)]
    pal = WALL_MIX
    for k, (z0, hm) in enumerate(levels):
        y0, y1 = 0.0 + t, SEC_Y0 - t
        if k == 0:
            basket('bw_baskets', (x0 + x1) / 2 - 0.005, 0.20, z0, 0.22, 0.30, 0.20, 'weave')
            y0 = 0.36
        books_x(f'bkS{k}', x1 - 0.005, y0, y1, z0, hm, rng, pal)
        y0, y1 = SEC_Y1 + t, 2.10 - t
        if k == 0:
            basket('bw_baskets', (x0 + x1) / 2 - 0.005, 1.90, z0, 0.22, 0.32, 0.20, 'weave')
            y1 = 1.73
        books_x(f'bkN{k}', x1 - 0.005, y0, y1, z0, hm, rng, pal)
        y0, y1 = SEC_Y0 + t, SEC_Y1 - t
        if k == 3:                    # the clue book's shelf: warm books, then a run of slate and grey-blue spines
            books_x('bkM3', x1 - 0.005, y0, 1.22, z0, hm, rng, ['bk_white', 'bk_grey', 'bk_dusty', 'bk_white'])
            books_x('bkM3', x1 - 0.005, 1.22, 1.395, z0, hm, rng, ['bk_slate', 'bk_greyblue', 'bk_dusty', 'bk_grey'])
            books_x('bkM3', x1 - 0.005, 1.445, y1, z0, hm, rng, ['bk_slate', 'bk_greyblue', 'bk_grey'])
        else:
            books_x(f'bkM{k}', x1 - 0.005, y0, y1, z0, hm, rng, pal)
    # the clue book: coral, 5 cm proud, a little tilted
    add('clue', box(x1 + 0.075 - 0.19, 1.396, 1.138, x1 + 0.075, 1.444, 1.138 + 0.235), 'coral_book')
    add('clue', box(x1 + 0.0735, 1.398, 1.30, x1 + 0.0755, 1.442, 1.31), 'bk_white')                 # a plain band, no letters


def build_den(rng):
    t = 0.018
    # bench toy chest along the west wall (x 0.02..0.32, y 0.90..2.50), two lift-up lids
    b = 'bench'
    add(b, box(0.02, 0.90, 0.0, 0.30, 0.90 + t, 0.40), 'birch_z'); add(b, box(0.02, 2.50 - t, 0.0, 0.30, 2.50, 0.40), 'birch_z')
    add(b, box(0.02, 1.70 - t / 2, 0.0, 0.30, 1.70 + t / 2, 0.40), 'birch_z')
    add(b, box(0.30, 0.90, 0.0, 0.32, 2.50, 0.40), 'birch_y')                       # front
    add(b, box(0.02, 0.90 + t, 0.0, 0.30, 2.50 - t, 0.03), 'white_in')
    add(b, box(0.0, 0.90, 0.0, 0.02, 2.50, 0.40), 'white_in')
    for nm, (y0, y1) in (('lidA', (0.90, 1.70)), ('lidB', (1.70, 2.50))):
        add(nm, box(0.02, y0 + 0.003, 0.40, 0.33, y1 - 0.003, 0.422), 'birch_y')
        add(nm, box(0.312, (y0 + y1) / 2 - 0.06, 0.37, 0.332, (y0 + y1) / 2 + 0.06, 0.40), 'birch_y')     # finger pull
    # six cubbies above the bench (3 columns x 2 rows), open to the east
    c = 'cubby'
    ys = (0.95, 1.25, 1.55, 1.85)
    for z in (0.75, 1.05, 1.35):
        add(c, box(0.0, ys[0], z, 0.28, ys[-1], z + t), 'birch_y')
    for y in ys:
        add(c, box(0.0, y - t / 2, 0.75 + t, 0.276, y + t / 2, 1.35), 'birch_z')
    add(c, box(0.0, ys[0], 0.75, 0.01, ys[-1], 1.368), 'white_in')
    # floor pad in front of the bench, cushions on the lid, a pouf in the south end
    add('pad', rbox((0.48, 1.40, 0.05), (0.30, 1.00, 0.10), 0.035, 4), 'pil_sage')
    pillow('cush', (0.20, 1.20, 0.62), (0.36, 0.11, 0.30), -0.30, 'pil_coral', yaw=math.pi / 2)
    pillow('cush', (0.20, 1.55, 0.62), (0.36, 0.11, 0.30), -0.30, 'pil_white', yaw=math.pi / 2)
    add('pouf', lathe(rprof(0.17, 0.0, 0.26, 0.07, 5), 28, (0.30, 0.45)), 'weave_w')
    # the den light panel across the underside of the deck
    add('den_housing', box(0.10, 0.10, DECK_Z0 - 0.012, 1.18, 2.50, DECK_Z0), 'panel_off')
    add('den_panel', box(0.12, 0.12, DECK_Z0 - 0.0135, 1.10, 2.48, DECK_Z0 - 0.012), 'panel')


def build_toys(rng):
    """The floor mess, each toy built where it ends up (chest or cubby)."""
    toys = []
    blocks = [(0.10, 1.00), (0.21, 1.06), (0.11, 1.16), (0.22, 1.26), (0.10, 1.36), (0.21, 1.46), (0.12, 1.57), (0.20, 1.62)]
    cols = ['toy_coral', 'toy_mustard', 'toy_sage', 'toy_blue', 'toy_white', 'toy_teal', 'toy_coral', 'toy_mustard']
    for k, (x, y) in enumerate(blocks):
        nm = f'toy_bl{k}'
        add(nm, xform(rbox((0, 0, 0), (0.075, 0.075, 0.075), 0.009, 3), T(x, y, 0.07) @ R('z', rng.uniform(-0.4, 0.4))), cols[k])
        toys.append((nm, 'chest', 0.0375))
    for k, (y, m) in enumerate(((1.04, 'toy_blue'), (1.16, 'toy_mustard'))):
        nm = f'toy_ball{k}'
        add(nm, ellipsoid((0.15, y, 0.768 + 0.058), (0.058, 0.058, 0.058), 14), m)
        toys.append((nm, 'cubby', 0.058))
    plush_toy('toy_plush0', (0.15, 1.40, 0.768 + 0.087), 1.0, 'plush', yaw=math.pi / 2)
    toys.append(('toy_plush0', 'cubby', 0.087))
    plush_toy('toy_plush1', (0.15, 1.40, 1.068 + 0.087), 1.0, 'plush2', yaw=math.pi / 2 + 0.3)
    toys.append(('toy_plush1', 'cubby', 0.087))
    for k, (y, m) in enumerate(((1.62, 'bk_terra'), (1.66, 'bk_sage'), (1.70, 'bk_mustard'))):
        nm = f'toy_pb{k}'
        add(nm, box(0.05, y, 0.768, 0.25, y + 0.03, 0.768 + 0.23 - 0.02 * k), m)
        toys.append((nm, 'cubby', 0.11))
    car = 'toy_car'
    add(car, rbox((0.15, 1.10, 1.068 + 0.05), (0.10, 0.20, 0.06), 0.02, 3), 'toy_coral')
    add(car, rbox((0.15, 1.08, 1.068 + 0.09), (0.085, 0.10, 0.04), 0.015, 3), 'toy_white')
    for y in (1.03, 1.17):
        for x in (0.10, 0.20):
            add(car, xform(lathe(rprof(0.024, -0.009, 0.009, 0.004, 2), 14, (0, 0)), T(x, y, 1.068 + 0.024) @ R('y', math.pi / 2)), 'blackm')
    toys.append((car, 'cubby', 0.05))
    rg = 'toy_rings'
    add(rg, lathe(rprof(0.06, 1.068, 1.088, 0.008, 3), 24, (0.15, 1.70)), 'toy_white')
    add(rg, tube([(0.15, 1.70, 1.07), (0.15, 1.70, 1.26)], 0.012, 10), 'toy_white')
    for k, (r_, m) in enumerate(((0.055, 'toy_blue'), (0.047, 'toy_sage'), (0.040, 'toy_mustard'), (0.032, 'toy_coral'))):
        z0 = 1.088 + k * 0.034
        add(rg, lathe([(0.012, z0), (r_ * 0.8, z0), (r_, z0 + 0.017), (r_ * 0.8, z0 + 0.033), (0.012, z0 + 0.033)], 24, (0.15, 1.70)), m)
    toys.append((rg, 'cubby', 0.10))
    basket('toy_basket', 0.17, 2.12, 0.422, 0.26, 0.30, 0.18, 'weave_w')
    return toys


# ------------------------------------------------------------------------------------------- north wall: book stair + wardrobe
def build_stair(rng):
    t = 0.018
    y0, y1 = 2.10, D
    for k, xr in enumerate(STAIR_X):
        st = f'st{k}'
        xb = xr - 0.24
        z0, z1 = 0.25 * k, 0.25 * (k + 1)
        if k > 0:
            add(st, box(xb, y0, 0.0, xr, y1, z0), 'birch_x')                    # solid base under the cubby
        add(st, box(xb, y0, z1 - 0.022, xr + 0.015, y1, z1), 'birch_x')         # tread (with a small nosing)
        add(st, box(xb, y0 + t, z0 + 0.012, xb + t, y1 - t, z1 - 0.022), 'birch_z')   # back
        add(st, box(xb, y0, z0, xr, y0 + t, z1 - 0.022), 'birch_x')             # side (south)
        add(st, box(xb, y1 - t, z0, xr, y1, z1 - 0.022), 'birch_x')             # side (north)
        add(st, box(xb, y0 + t, z0, xr, y1 - t, z0 + 0.012), 'birch_x')         # cubby floor
        books_x(f'stb{k}', xr - 0.004, y0 + t, y1 - t, z0 + 0.012, 0.20, rng, WARM_MIX)
    plush_toy('stair_plush', (2.80, 2.58, 0.087), 1.1, 'plush', yaw=-2.2)
    # handrail on posts along the open (south) side
    hr = 'handrail'
    for k in (0, 2, 4):
        x = STAIR_X[k] - 0.05
        add(hr, box(x - 0.018, 2.115, 0.25 * (k + 1), x + 0.018, 2.151, 0.25 * (k + 1) + 0.80), 'birch_z')
    add(hr, box(DECK_X + 0.002, 2.115, DECK_Z1 - 0.2, DECK_X + 0.038, 2.151, 2.08), 'birch_z')
    p0 = np.array([STAIR_X[0] - 0.05, 2.133, 0.25 + 0.80])
    p1 = np.array([DECK_X + 0.02, 2.133, 0.25 * 5 + 0.80])
    add(hr, tube([tuple(p0), tuple(p1)], 0.02, 12), 'birch_x')


def build_wardrobe(rng):
    t = 0.018
    x0, x1, y0, y1, z1 = 2.90, W, 2.10, D, 2.20
    b = 'wd_body'
    add(b, box(x0, y0, 0.10, x0 + t, y1, z1), 'white_cab'); add(b, box(x1 - t, y0, 0.10, x1, y1, z1), 'white_cab')
    add(b, box(x0 + t, y1 - t, 0.118, x1 - t, y1, z1 - t), 'white_in')
    add(b, box(x0 + t, y0, z1 - t, x1 - t, y1 - t, z1), 'white_cab')
    add(b, box(x0 + t, y0, 0.10, x1 - t, y1 - t, 0.118), 'white_in')
    add(b, box(x0 + 0.01, y0 + 0.06, 0.0, x1 - 0.01, y1, 0.10), 'white_in')        # plinth (the toe-kick drawer sits in it)
    for z in (0.50, 0.86):
        add(b, box(x0 + t, y0 + 0.02, z, x1 - t, y1 - t, z + t), 'birch_x')
    add(b, box(x0 + t, y0 + 0.02, 1.96, x1 - t, y1 - t, 1.96 + t), 'birch_x')
    add(b, tube([(x0 + 0.02, 2.40, 1.86), (x1 - 0.02, 2.40, 1.86)], 0.011, 10), 'alu')
    # coral door, hinged at the east edge
    dr = 'wd_door'
    add(dr, box(x0 + 0.002, y0 - 0.02, 0.102, x1 - 0.002, y0, z1 - 0.002), 'coral')
    add(dr, box(x0 + 0.04, y0 - 0.032, 0.95, x0 + 0.052, y0 - 0.02, 1.25), 'birch_z')
    # toe-kick step drawer (front flush with the plinth face)
    tk = 'wd_tk'
    add(tk, box(x0 + 0.012, y0 + 0.02, 0.012, x1 - 0.012, y0 + 0.04, 0.098), 'birch_x')
    add(tk, box(x0 + 0.03, y0 + 0.04, 0.012, x1 - 0.03, y0 + 0.40, 0.022), 'white_in')
    for bb in (box(x0 + 0.03, y0 + 0.04, 0.022, x0 + 0.042, y0 + 0.40, 0.09), box(x1 - 0.042, y0 + 0.04, 0.022, x1 - 0.03, y0 + 0.40, 0.09),
               box(x0 + 0.03, y0 + 0.388, 0.022, x1 - 0.03, y0 + 0.40, 0.09)):
        add(tk, bb, 'white_in')
    for k, (x, m) in enumerate(((3.02, 'shoe_white'), (3.12, 'shoe_white'), (3.24, 'shoe_blue'), (3.32, 'shoe_blue'))):
        add('wd_shoes', ellipsoid((x, 2.30, 0.045), (0.035, 0.085, 0.025), 10), m)
    # small clothes, folded stacks, baskets
    for k, m in enumerate(('cl_coral', 'cl_white', 'cl_sky', 'cl_mustard', 'cl_sage', 'cl_denim')):
        garment('wd_cl', 2.97 + k * 0.07, 2.40, 1.86, rng.uniform(0.45, 0.65), 0.34, m)
    stack('wd_st', 3.03, 2.38, 0.868 + 0.008, (0.20, 0.26, 0.045), ['cl_white', 'cl_sky', 'cl_blush'], 4, rng)
    stack('wd_st', 3.27, 2.38, 0.868 + 0.008, (0.20, 0.26, 0.045), ['cl_sage', 'cl_grey', 'cl_coral'], 3, rng)
    stack('wd_st2', 3.03, 2.38, 0.518, (0.20, 0.26, 0.05), ['cl_denim', 'cl_white', 'cl_mustard'], 3, rng)
    stack('wd_st2', 3.27, 2.38, 0.518, (0.20, 0.26, 0.05), ['cl_blush', 'cl_sky', 'cl_white', 'cl_grey'], 4, rng)
    basket('wd_bk', 3.03, 2.40, 0.118, 0.20, 0.30, 0.16, 'weave')
    basket('wd_bk', 3.27, 2.40, 0.118, 0.20, 0.30, 0.16, 'weave_w')
    add('wd_bk', box(2.95, 2.30, 1.978, 3.35, 2.60, 2.10), 'weave_w')


# ------------------------------------------------------------------------------------------- south + east walls
def build_desk(rng):
    t = 0.018
    dx0, dx1, dy1, dz = 1.40, 2.40, 0.55, 0.62
    d = 'desk'
    wood(d, dx0, 0.0, dz - 0.022, dx1, dy1, dz, 'birch')
    add(d, box(dx0, 0.0, 0.0, dx0 + t, dy1 - 0.02, dz - 0.022), 'white_cab')
    add(d, box(dx1 - t, 0.0, 0.0, dx1, dy1 - 0.02, dz - 0.022), 'white_cab')
    add(d, box(1.95, 0.0, 0.44, dx1 - t, dy1 - 0.02, 0.458), 'white_cab')          # drawer housing floor
    add(d, box(1.95 - t, 0.0, 0.44, 1.95, dy1 - 0.02, dz - 0.022), 'white_cab')
    add(d, box(dx0 + t, 0.0, 0.25, 1.95 - t, 0.012, dz - 0.022), 'white_in')       # modesty back
    dr = 'desk_dr'
    add(dr, box(1.952, dy1 - 0.02, 0.462, dx1 - 0.02, dy1, dz - 0.026), 'coral')
    add(dr, box(2.11, dy1, 0.52, 2.23, dy1 + 0.012, 0.532), 'birch_x')
    add(dr, box(1.97, 0.06, 0.462, dx1 - 0.04, dy1 - 0.02, 0.472), 'white_in')
    for bb in (box(1.97, 0.06, 0.472, 1.982, dy1 - 0.02, 0.56), box(dx1 - 0.052, 0.06, 0.472, dx1 - 0.04, dy1 - 0.02, 0.56),
               box(1.97, 0.06, 0.472, dx1 - 0.04, 0.072, 0.56)):
        add(dr, bb, 'white_in')
    for k, m in enumerate(('toy_coral', 'toy_mustard', 'toy_blue', 'toy_sage', 'toy_teal')):
        add('dr_items', tube([(2.02 + 0.03 * k, 0.15, 0.48), (2.02 + 0.03 * k, 0.34, 0.48)], 0.006, 6), m)
    add('dr_items', box(2.20, 0.12, 0.472, 2.24, 0.45, 0.478), 'birch_y')            # blank ruler stick
    add('dr_items', box(2.26, 0.14, 0.472, 2.34, 0.30, 0.50), 'paper')
    # lamp, plant, crayon jar on the desk
    lp = 'dlamp'
    add(lp, lathe(rprof(0.055, dz, dz + 0.014, 0.005, 3), 28, (2.28, 0.14)), 'white_cab')
    add(lp, tube([(2.28, 0.14, dz + 0.01), (2.28, 0.14, 0.98), (2.24, 0.16, 1.02), (2.17, 0.22, 1.02)], 0.007, 10), 'white_cab')
    add(lp, lathe([(0.01, 1.045), (0.03, 1.035), (0.05, 0.99), (0.058, 0.975)], 28, (2.17, 0.22)), 'coral')
    add('dlamp_on', ellipsoid((2.17, 0.22, 0.995), (0.018, 0.018, 0.014), 8), 'bulb')
    plant('dplant', 1.55, 0.16, dz, 0.045, 0.07, rng, 9, pot='ceramic')
    add('jar', lathe([(0, dz), (0.035, dz), (0.036, dz + 0.10), (0.032, dz + 0.10), (0.031, dz + 0.01), (0, dz + 0.01)], 20, (1.72, 0.12)), 'ceramic')
    for k, m in enumerate(('toy_coral', 'toy_mustard', 'toy_blue', 'toy_sage')):
        a = k * 1.6
        add('jar', tube([(1.72 + 0.012 * math.cos(a), 0.12 + 0.012 * math.sin(a), dz + 0.02),
                         (1.72 + 0.02 * math.cos(a), 0.12 + 0.02 * math.sin(a), dz + 0.15)], 0.005, 6), m)
    # kids' chair (tucks in under the east half)
    cx, cy = 2.17, 0.62
    ch = 'chair'
    add(ch, rbox((cx, cy, 0.34), (0.34, 0.32, 0.03), 0.01, 3), 'birch_x')
    add(ch, rbox((cx, cy + 0.15, 0.55), (0.32, 0.025, 0.14), 0.01, 3), 'birch_x')
    for sx in (-1, 1):
        add(ch, tube([(cx + sx * 0.14, cy + 0.15, 0.62), (cx + sx * 0.15, cy + 0.14, 0.0)], 0.014, 8), 'birch_z')
        add(ch, tube([(cx + sx * 0.14, cy - 0.12, 0.33), (cx + sx * 0.15, cy - 0.13, 0.0)], 0.014, 8), 'birch_z')
    # rolling cart (three tiers) under the west end
    ct = 'cart'
    for z in (0.06, 0.24, 0.42):
        basket(ct, 1.62, 0.25, z, 0.32, 0.36, 0.06, 'white_cab', t=0.008)
    for x in (1.47, 1.77):
        for y in (0.08, 0.42):
            add(ct, box(x - 0.006, y - 0.006, 0.03, x + 0.006, y + 0.006, 0.48), 'white_cab')
            add(ct, ellipsoid((x, y, 0.02), (0.02, 0.02, 0.02), 8), 'blackm')
    for k, (z, ms) in enumerate(((0.068, ('toy_blue', 'toy_mustard', 'toy_coral')), (0.248, ('paper', 'toy_sage', 'paper')),
                                 (0.428, ('toy_teal', 'toy_coral', 'toy_white')))):
        for j, m in enumerate(ms):
            add(f'cart_it{k}', rbox((1.53 + 0.09 * j, 0.25, z + 0.04), (0.07, 0.24, 0.07), 0.01, 3), m)
    # roller blind (cassette + fabric, built down)
    x0w, x1w, z0w, z1w = WIN
    add('blind_box', rbox(((x0w + x1w) / 2, 0.045, z1w + 0.06), (x1w - x0w + 0.08, 0.07, 0.07), 0.02, 3), 'white_cab')
    add('blind', box(x0w - 0.02, 0.035, z0w + 0.05, x1w + 0.02, 0.04, z1w + 0.03), 'blind')
    add('blind', box(x0w - 0.02, 0.03, z0w + 0.03, x1w + 0.02, 0.045, z0w + 0.05), 'white_cab')
    # rug
    add('rug', rbox((2.45, 1.05, 0.006), (0.80, 0.70, 0.012), 0.005, 3), 'rug')


def build_east(rng):
    add('hooks', box(W - 0.02, 0.18, 1.12, W, 0.80, 1.20), 'birch_y')
    for y in (0.30, 0.49, 0.68):
        add('hooks', tube([(W - 0.02, y, 1.16), (W - 0.07, y, 1.16), (W - 0.08, y, 1.19)], 0.012, 8), 'birch_x')
    bp = 'backpack'
    add(bp, rbox((W - 0.10, 0.49, 0.98), (0.12, 0.26, 0.32), 0.05, 4), 'backpack')
    add(bp, rbox((W - 0.165, 0.49, 0.92), (0.03, 0.20, 0.14), 0.02, 3), 'backpack')
    add(bp, tube([(W - 0.08, 0.42, 1.12), (W - 0.075, 0.49, 1.17), (W - 0.08, 0.56, 1.12)], 0.01, 8), 'blackm')
    pr = 'print'
    add(pr, box(W - 0.025, 0.22, 1.42, W, 0.76, 1.92), 'birch_y')
    add(pr, box(W - 0.028, 0.25, 1.45, W - 0.025, 0.73, 1.89), 'paper')
    add(pr, xform(lathe(rprof(0.08, 0, 0.003, 0.001, 2), 28, (0, 0)), T(W - 0.03, 0.38, 1.76) @ R('y', -math.pi / 2)), 'toy_mustard')
    add(pr, box(W - 0.031, 0.50, 1.50, W - 0.028, 0.68, 1.62), 'coral')
    add(pr, box(W - 0.031, 0.31, 1.50, W - 0.028, 0.44, 1.56), 'bk_dusty')
    plant('cplant', W - 0.20, 0.20, 0.0, 0.13, 0.32, rng, 13, pot='ceramic', leaf=2.2)


def build():
    materials()
    rng = np.random.default_rng(13)
    build_shell()
    build_loft(rng)
    build_bookwall(rng)
    build_den(rng)
    global TOYS
    TOYS = build_toys(rng)
    build_stair(rng)
    build_wardrobe(rng)
    build_desk(rng)
    build_east(rng)
    for (x, y) in DL:
        disc('dl_on', (x, y), 0.037, H - 0.005, H - 0.0035, 'dl_emis')
    global KID
    KID = fg.figure('kid', 'child', pose='stand', at=(1.50, 1.31, 270), mat='fig_kid')


TOYS = []
KID = None

# ------------------------------------------------------------------------------------------- camera
VFOV = 85.0


def P(x, y, z, yaw, pitch):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch)


F1 = P(3.30, 1.30, 2.30, 270.0, -25.0)                                          # frame 1: high over the door, looking west
S1 = (F1, P(2.70, 1.24, 2.02, 266.0, -22.0))                                     # push in on the book wall
S1B = (P(2.62, 2.08, 2.38, 238.0, -31.0), P(2.40, 1.62, 2.42, 252.0, -34.0))      # over the room onto the loft
S2 = (P(2.68, 1.18, 1.06, 316.0, -10.0), P(2.40, 1.50, 0.98, 330.0, -13.0))       # book stair, sliding round
S2B = (P(2.40, 0.50, 1.28, 26.0, -15.0), P(2.80, 0.40, 1.32, 334.0, -25.0))        # wardrobe + the mess
S3 = (P(2.62, 0.36, 0.82, 303.0, 1.0), P(2.42, 0.54, 0.78, 299.0, 1.0))          # the pull: low, from the south-east, child in profile
S4A = (P(3.05, 1.40, 1.34, 214.0, -17.0), P(2.80, 1.18, 1.22, 204.0, -21.0))      # desk, drawer, chair, rug
S4 = (P(3.05, 1.80, 1.45, 236.0, -12.0), F1)                                     # lights, the den, crane back to frame 1
HOLDS = [(0.0, 1.62, S1), (1.86, 3.00, S1B), (3.30, 4.65, S2), (4.95, 7.00, S2B), (7.30, 10.85, S3), (11.10, 12.60, S4A),
         (12.90, 15.0, S4)]
if LONG:
    LH = [(0.0, 3.30, (F1, P(2.70, 1.30, 2.08, 270.0, -21.0))),
          (3.60, 6.80, (P(1.64, 2.30, 1.98, 242.0, -30.0), P(1.64, 0.95, 1.98, 288.0, -30.0))),
          (7.10, 10.30, (P(2.95, 1.25, 0.72, 318.0, -4.0), P(2.60, 1.45, 0.74, 326.0, -4.0))),
          (10.60, 13.90, (P(2.25, 0.55, 1.22, 18.0, -15.0), P(2.05, 0.72, 1.16, 28.0, -19.0))),
          (14.20, 17.20, (P(1.90, 1.75, 1.30, 180.0, -14.0), P(1.90, 1.28, 1.22, 180.0, -18.0))),
          (17.50, 20.50, (P(3.05, 0.80, 0.80, 252.0, -8.0), P(2.95, 0.62, 0.78, 246.0, -8.0))),
          (20.80, 24.00, (P(1.55, 1.20, 1.30, 95.0, -8.0), P(1.70, 0.90, 1.30, 80.0, -8.0))),
          (24.30, 27.20, (P(3.10, 0.30, 1.85, 322.0, -22.0), P(3.00, 0.40, 1.95, 318.0, -24.0))),
          (27.50, 30.80, S3),
          (31.10, 34.30, (P(2.20, 1.55, 0.95, 248.0, -5.0), P(1.65, 1.35, 0.90, 250.0, -6.0))),
          (34.60, 37.70, (P(0.60, 0.98, 0.80, 330.0, 6.0), P(0.62, 1.08, 0.84, 338.0, 2.0))),
          (38.00, 40.90, (P(2.00, 1.55, 1.30, 250.0, -8.0), P(2.85, 0.75, 1.80, 285.0, -18.0))),
          (41.20, 43.20, (P(2.60, 0.80, 0.90, 282.0, -3.0), P(2.45, 1.05, 0.90, 268.0, -3.0))),
          (43.50, 45.50, (P(2.95, 1.30, 2.05, 270.0, -22.0), F1))]
    HOLDS = LH
if REST and LONG:
    HOLDS = [(h[0], h[1], h[2]) for h in LH]
elif REST:
    HOLDS = [(0.0, 1.62, S1), (1.86, 3.00, S1B), (3.30, 4.65, S2), (4.95, 7.00, S2B), (7.30, 10.85, S3), (11.10, 12.60, S4A),
             (12.90, 15.0, S4), (15.3, 16, (S4[1], S4[1])),
             (16.3, 17, (S1[1], S1[1]))]

camera = hold_camera(HOLDS, VFOV, rest=REST)


# ------------------------------------------------------------------------------------------- lights (fixed slots)
LSKY = (11.0, 11.6, 12.6)
LSUN = (70000.0, 64000.0, 54000.0)
LDOOR = (2.2, 2.15, 2.05)
LCEIL = (1.3, 1.28, 1.24)
LDEN = (30.0, 27.5, 23.5)
LDENFILL = (2.5, 2.4, 2.2)
LDOWN = (420.0, 380.0, 310.0)
LLAMP = (80.0, 64.0, 44.0)
T_DUSK = 12.95


def lights(mats4, vis):
    off = (0.0, 0.0, 0.0)
    night = bool(vis.get('bd_night'))

    def k(L, on, f=1.0):
        return tuple(v * f for v in L) if on else off
    x0w, x1w, z0w, z1w = WIN
    Ls = []
    Ls.append(rect_light((x0w, -0.16, z0w), (0, 0, z1w - z0w), (x1w - x0w, 0, 0), k(LSKY, True, 0.55 if night else 1.0), always=1))  # 0 sky (+y)
    sc = np.array([(x0w + x1w) / 2, 0.0, (z0w + z1w) / 2]) - SUN_DIR * 3.0
    Ls.append(spot_rect(tuple(sc), tuple(SUN_DIR), 0.06, k(LSUN, not night), 0.0))                                   # 1 sun
    Ls.append(rect_light((W - 0.005, 0.25, 0.25), (0, 0, 1.9), (0, 2.2, 0), k(LDOOR, True, 0.75 if night else 1.0), always=1))  # 2 fill (-x)
    Ls.append(rect_light((1.45, 0.35, H - 0.01), (0, 1.9, 0), (1.8, 0, 0), k(LCEIL, True, 0.8 if night else 1.0)))    # 3 fill (down)
    Ls.append(rect_light((0.12, 0.30, DECK_Z0 - 0.016), (0, 2.18, 0), (0.98, 0, 0), k(LDEN, vis.get('den_panel'), 1.4)))    # 4 den panel
    Ls.append(rect_light((1.9, 0.9, 0.2), (0, 0, 0.9), (0, 0.6, 0), k(LDENFILL, vis.get('den_fill_on'))))              # 5 den fill (-x)
    for (x, y) in DL:                                                                                                  # 6-9 downlights
        Ls.append(spot_rect((x, y, H - 0.006), (0, 0, -1), 0.05, k(LDOWN, vis.get('dl_on')), 4.0))
    Ls.append(sphere_light((DECK_X - 0.18, 1.95, 2.19), 0.02, k(LLAMP, vis.get('loft_lamp_on'), 0.7)))                 # 10 loft lamp
    Ls.append(sphere_light((2.17, 0.22, 0.995), 0.02, k(LLAMP, vis.get('dlamp_on'))))                                  # 11 desk lamp
    return Ls


BLENDER = dict(
    exposure=-0.48,
    shutter=0.3,
    look='AgX - Medium High Contrast',
    translucent={'blind': 0.5},
    separate=['backdrop', 'backdrop_night'],
    fill_lights=[2, 3, 5],
    wood_scale=(55.0, 1.6),
    bake_rect={'backdrop': (-3.0, 7.0, -2.0, 6.0), 'backdrop_night': (-3.0, 7.0, -2.0, 6.0)},
    bake_px={'backdrop': 0.006, 'backdrop_night': 0.004, 'floor': 0.0015},
)


# ------------------------------------------------------------------------------------------- timeline helpers
I4 = np.eye(4)


def sec_offset(t, tc, tb0, tb1, ts0, ts1):
    """Section offset: latch pop at tc, pushed 0.30 m back (tb0..tb1), slid 0.70 m south (ts0..ts1)."""
    if t < tc:
        return np.zeros(3)
    a = smooth(c01((t - tb0) / (tb1 - tb0)))
    b = c01((t - ts0) / (ts1 - ts0))
    b = b * b * (3 - 2 * b) * 0.85 + 0.15 * b if b < 1 else 1.0     # slow start, slow end, never quite still
    pop = 0.004 * math.sin(math.pi * c01((t - tc) / 0.10))
    return np.array([-0.30 * a + pop, -0.70 * b, 0.0])


def toy_motion(tl, name, kind, half, t_spill, mess, mess_yaw, basket_mouth, t_fly, fly_dur, gate, toss=None, t_hop=None):
    """Hidden until the basket spills it onto the floor at `mess` (centre xy), then it flies through the opening
    (via `gate`) to where it was built."""
    lo, hi = rk.bounds(name)
    cen = (lo + hi) / 2.0
    zf = cen[2]
    p_mess = np.array([mess[0], mess[1], half + 0.001])
    p_mouth = np.array(basket_mouth, float)
    p_end = cen.copy() + (np.array(toss[:3]) if toss is not None else 0.0)
    end_yaw = toss[3] if toss is not None else 0.0
    gate = np.array(gate, float)
    C = 2 * gate - (p_mess + p_end) / 2
    spill = 0.26

    def M_at(p, yaw):
        return T(*(p - cen)) @ about(cen, R('z', yaw))

    def f(t):
        if t < t_spill:
            return I4, False
        if t < t_spill + spill:
            u = (t - t_spill) / spill
            p = p_mouth + (p_mess - p_mouth) * eoc(u)
            p = p + np.array([0, 0, 0.12 * math.sin(math.pi * min(1.0, u * 1.3))])
            return M_at(p, mess_yaw * u), True
        if t < t_fly:
            tau = t - t_spill - spill
            p = p_mess + np.array([0, 0, 0.03 * math.exp(-tau / 0.07) * abs(math.sin(math.pi * tau / 0.11))])
            return M_at(p, mess_yaw), True
        u = (t - t_fly) / fly_dur
        if u < 1:
            v = smooth(u) * 0.6 + 0.4 * u
            p = (1 - v) ** 2 * p_mess + 2 * v * (1 - v) * C + v * v * p_end
            return M_at(p, mess_yaw * (1 - v) + end_yaw * v + 2 * math.pi * v * (0.5 if kind == 'chest' else 0.0)), True
        if t_hop is not None and t < t_hop + 0.2:
            if t < t_hop:
                return M_at(p_end, end_yaw), True
            u = (t - t_hop) / 0.2
            p = p_end + (cen - p_end) * smooth(u) + np.array([0, 0, 0.07 * math.sin(math.pi * u)])
            return M_at(p, end_yaw * (1 - smooth(u))), True
        tau = t - (t_hop + 0.2 if t_hop is not None else t_fly + fly_dur)
        bz = 0.012 * math.exp(-tau / 0.06) * abs(math.sin(math.pi * tau / 0.1))
        if toss is not None and t_hop is None:
            return M_at(p_end + np.array([0, 0, bz]), end_yaw), True
        return T(0, 0, bz), True
    tl.custom(name, f)
    return f


# ------------------------------------------------------------------------------------------- timeline (15 s cut)
def timeline():
    tl = Timeline(rk, FPS)
    hidden = lambda t: (I4, False)
    if REST:
        for nm in ('bd_night', 'dl_on', 'loft_lamp_on', 'dlamp_on', 'den_fill_on') + tuple(KID.pieces):
            tl.custom(nm, hidden)
        if not REST_OPEN:
            tl.custom('den_panel', hidden)
        else:
            o = sec_offset(99, 0, 0, 1, 1, 2)
            for nm in ['sec_car', 'sec_sh', 'clue'] + [f'bkM{k}' for k in range(4)]:
                tl.custom(nm, lambda t, o=o: (T(*o), True))
        return tl
    return timeline_long(tl) if LONG else timeline_short(tl)


def common(tl):
    """Helpers shared by both cuts."""
    ev = tl.ev

    def appear(name, t_on, t_off=None):
        tl.custom(name, lambda t: (I4, t >= t_on and (t_off is None or t < t_off)))

    def door_z(name, hinge, a_open, t_in, t_in1, t_close, dur=0.17, axis='z'):
        hinge = np.array(hinge, float)

        def f(t):
            if t < t_in:
                return I4, False
            if t < t_in1:
                u = (t - t_in) / (t_in1 - t_in)
                s = 1.15 - 0.15 * eoc(u)
                return T(0, 0, 0.12 * (1 - eoc(u))) @ about(hinge, R(axis, a_open) @ S(s, s, s)), True
            if t < t_close:
                return about(hinge, R(axis, a_open)), True
            u = (t - t_close) / dur
            if u < 1:
                return about(hinge, R(axis, a_open * (1 - u * u))), True
            tau = t - t_close - dur
            a = math.copysign(math.radians(2.0), a_open) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))
            return about(hinge, R(axis, a)), True
        tl.custom(name, f)
        ev(t_in1, name, 0.3, 'tick')
        ev(t_close + dur, name + '_shut', 0.8, 'thud')

    def drawer_fn(t_appear, t_open, t_close, off, base=None, out=0.12, shut=0.17):
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

    def lid_fn(name, t_open, t_close, a_open=math.radians(-78), t_on=0.0):
        piv = np.array([0.02, 0.0, 0.41])

        def f(t):
            if t < t_on:
                return I4, False
            if t < t_open:
                return I4, True
            if t < t_close:
                return about(piv, R('y', a_open * eob(c01((t - t_open) / 0.16), 1.1))), True
            u = (t - t_close) / 0.12
            if u < 1:
                return about(piv, R('y', a_open * (1 - u * u))), True
            tau = t - t_close - 0.12
            return about(piv, R('y', math.radians(-1.5) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08)))), True
        tl.custom(name, f)
        ev(t_open + 0.12, name + '_open', 0.4, 'swish'); ev(t_close + 0.12, name + '_shut', 0.85, 'thud')

    def section(tc, tb0, tb1, ts0, ts1, t_sh=1.02, t_bk0=1.12, t_clue=1.48, t_car=0.52):
        """Builds the section's pieces (carcass grows, shelves slide, books riffle) and rides them on its L path."""
        off = lambda t: T(*sec_offset(t, tc, tb0, tb1, ts0, ts1))
        base_car = tl.grow('sec_car', t_car, t_car + 0.18, 'z', (0, 0, 0), 0.6)
        tl.custom('sec_car', lambda t: (off(t) @ base_car(t)[0], base_car(t)[1]))
        base_sh = tl.slide('sec_sh', t_sh, t_sh + 0.16, (0.45, 0, 0), 1.0, 0.45)
        tl.custom('sec_sh', lambda t: (off(t) @ base_sh(t)[0], base_sh(t)[1]))
        for k in range(4):
            b = tl.fly(f'bkM{k}', t_bk0 + 0.09 * k, t_bk0 + 0.09 * k + 0.16, (0.4, 0, 0.04), 0.04, 0.25, 'tick')
            tl.custom(f'bkM{k}', lambda t, b=b: (off(t) @ b(t)[0], b(t)[1]))
        cb = tl.drop('clue', t_clue - 0.16, t_clue, 0.30, 0.06, 0.55, 'tick')
        piv = np.array([BW_X1 + 0.075, 1.42, 1.138])

        def clue(t):
            M, v = cb(t)
            tilt = math.radians(5.0)
            if t >= tc - 0.12:
                tilt += math.radians(13.0) * eob(c01((t - (tc - 0.12)) / 0.12), 1.4)
            return off(t) @ about(piv, R('y', tilt)) @ M, v
        tl.custom('clue', clue)
        return off

    def kid_pose_fn(walk_pose, acts):
        """acts = [(t0, t1, pose_or_fn, blend)]: overlay poses on the walk/stand pose, blended in and out over `blend` s."""
        def f(t):
            p = walk_pose(t)
            for (t0, t1, q, bl) in acts:
                if t0 - bl <= t <= t1 + bl:
                    w = smooth(c01((t - (t0 - bl)) / bl)) if t < t0 else (1 - smooth(c01((t - t1) / bl)) if t > t1 else 1.0)
                    qq = q(t) if callable(q) else q
                    p = fg.lerp_pose(p, qq, w)
            return p
        return f

    return appear, door_z, drawer_fn, lid_fn, section, kid_pose_fn


PUSH = dict(sh_l=92, sh_r=92, sh_l_out=12, sh_r_out=12, elbow_l=18, elbow_r=18, spine=14, neck=-6, hip_l=6, hip_r=6)
REACH = fg.lerp_pose('stand', 'reach_up', 0.78)


def mess_tidy(tl, tb_land, spill0, land0, step, t_basket_fly, hop=None, fly=0.5):
    """The toy basket lands by the stair foot and tips west, the toys spill across the floor, then they fly through
    the opening into the chest and cubbies (landing land0 + step * i). hop = (t0, dt): cubby toys land jumbled and
    hop into order one by one."""
    ev = tl.ev
    # the basket lands by the stair foot and tips west; the toys spill across the floor
    bx, by = 2.52, 1.58
    bpiv = np.array([bx - 0.15, by, 0.0])
    TB_LAND, TB_TIP = tb_land, tb_land + 0.12
    lo, hi = rk.bounds('toy_basket')
    bcen = (lo + hi) / 2
    B_REST = T(bx - bcen[0], by - bcen[1], -0.422)

    def basket_fn(t, t_fly=t_basket_fly, fly_dur=0.30):
        if t < TB_LAND - 0.18:
            return I4, False
        if t < TB_LAND:
            u = (t - (TB_LAND - 0.18)) / 0.18
            return T(0, 0, 0.5 * (1 - u * u)) @ B_REST, True
        tip = math.radians(-100) * eob(c01((t - TB_TIP) / 0.20), 0.6)
        M = about(bpiv, R('y', tip)) @ B_REST
        if t < t_fly:
            return M, True
        u = (t - t_fly) / fly_dur
        if u < 1:
            v = smooth(u)
            p0 = (M @ np.array([*bcen, 1.0]))[:3]
            gate = np.array([BW_X0 + 0.12, 1.40, 1.12])
            C = 2 * gate - (p0 + bcen) / 2
            p = (1 - v) ** 2 * p0 + 2 * v * (1 - v) * C + v * v * bcen
            return T(*(p - bcen)) @ about(bcen, R('y', tip * (1 - v))), True
        tau = t - t_fly - fly_dur
        return T(0, 0, 0.015 * math.exp(-tau / 0.06) * abs(math.sin(math.pi * tau / 0.1))), True
    tl.custom('toy_basket', basket_fn)
    ev(TB_LAND, 'basket', 0.6, 'thud'); ev(TB_TIP + 0.2, 'basket_tip', 0.5, 'thud'); ev(t_basket_fly + 0.30, 'basket_in', 0.3, 'tick')
    rngm = np.random.default_rng(3)
    mess = [(1.76, 1.02), (1.98, 1.20), (2.14, 1.00), (1.86, 1.42), (2.24, 1.30), (2.04, 1.62), (1.74, 1.24), (2.20, 1.52),
            (2.36, 1.12), (1.92, 1.06), (2.10, 1.40), (1.80, 1.68), (2.30, 1.74), (2.00, 1.36), (1.90, 1.58), (2.28, 0.96),
            (2.06, 1.80)]
    order = list(range(len(TOYS)))
    rngm.shuffle(order)
    mouth = (bx - 0.30, by, 0.12)
    land = land0
    for i, (nm, kind, half) in enumerate(TOYS):
        ts = spill0 + 0.022 * order[i]
        t_land = land + step * i
        lo, hi = rk.bounds(nm)
        yc = (lo[1] + hi[1]) / 2
        gate = (BW_X0 + 0.12, min(max(yc, 0.98), 1.42), 1.18 if kind == 'chest' else 1.12)
        toss = None
        if hop is not None:
            toss = (rngm.uniform(-0.03, 0.03), rngm.uniform(-0.04, 0.04), 0.0, rngm.uniform(-0.9, 0.9)) if kind != 'chest' else None
        toy_motion(tl, nm, kind, half, ts, mess[i], rngm.uniform(-2.5, 2.5), mouth, t_land - fly, fly, gate,
                   toss=toss, t_hop=None if (hop is None or toss is None) else hop[0] + hop[1] * i)
        if toss is not None:
            tl.events.append(dict(t=round(hop[0] + hop[1] * i + 0.2, 3), name=nm + '_hop', strength=0.25, kind='pluck', note=i + 3))
        if i % 3 == 0:
            ev(ts + 0.26, nm + '_spill', 0.3, 'tick')
        tl.events.append(dict(t=round(t_land, 3), name=nm + '_in', strength=0.5, kind='pluck', note=i))


def chair_in(tl, t0_, t1_):
    ch_c = tl.cen['chair']

    def chair(t, t0=t0_, t1=t1_):
        if t < t0:
            return I4, False
        u = (t - t0) / (t1 - t0)
        if u < 1:
            off_ = (1 - eoc(u)) * np.array([0.10, 0.75, 0.0])
            ang = math.radians(-120) * (1 - eob(u, 1.2))
        else:
            off_ = np.zeros(3)
            ang = math.radians(4) * math.exp(-(t - t1) / 0.12) * math.sin(2 * math.pi * (t - t1) / 0.3)
        return T(*off_) @ about(ch_c, R('z', ang)), True
    tl.custom('chair', chair)
    tl.ev(t1_, 'chair', 0.8, 'thud')


def blind_up(tl, t_in, t_up):
    appear = lambda name, t_on: tl.custom(name, lambda t: (I4, t >= t_on))
    appear('blind_box', t_in)
    z1b = WIN[3] + 0.03

    def blind(t):
        if t < t_in:
            return I4, False
        u = c01((t - t_up) / 0.30)
        s = 0.40 * (1 - u) + 0.03 * u if t >= t_up else 0.40 * eoc(c01((t - t_in) / 0.12))
        return about((0, 0, z1b), S(1, 1, max(s, 0.03))), True
    tl.custom('blind', blind)
    tl.ev(t_up + 0.25, 'blind_up', 0.4, 'swish')


def s1_build(tl, sec, bed=True):
    """S1 / A1: planks, the book wall, deck, runners, shelves, books, the clue book, rail, mattress, bedding."""
    drop, fly, slide, grow = tl.drop, tl.fly, tl.slide, tl.grow
    appear, door_z, drawer_fn, lid_fn, section, kid_pose_fn = common(tl)
    for k in range(6):
        t1 = 0.12 + 0.05 * k
        drop(f'floor{k}', t1 - 0.10, t1, 0.22, 0.05, 0.25 + 0.03 * k, 'tick')
    gS = grow('bwS_car', 0.03, 0.22, 'z', (0, 0, 0), 0.6)
    gN = grow('bwN_car', 0.14, 0.34, 'z', (0, 0, 0), 0.6)
    off = section(t_sh=1.02, t_bk0=1.12, t_clue=1.48, t_car=0.24, **sec)
    drop('deck', 0.42, 0.60, 0.60, 0.02, 0.95, 'thud')
    slide('runners', 0.70, 0.82, (0.6, 0, 0), 1.0, 0.55)
    slide('track', 0.74, 0.86, (0.6, 0, 0), 1.0, 0.0, 'none')
    slide('bwS_sh', 0.98, 1.14, (0.45, 0, 0), 1.0, 0.4)
    slide('bwN_sh', 1.06, 1.22, (0.45, 0, 0), 1.0, 0.4)
    for k in range(4):
        fly(f'bkS{k}', 1.08 + 0.09 * k, 1.24 + 0.09 * k, (0.4, 0, 0.04), 0.04, 0.22, 'tick')
        fly(f'bkN{k}', 1.15 + 0.09 * k, 1.31 + 0.09 * k, (0.4, 0, 0.04), 0.04, 0.22, 'tick')
    drop('bw_baskets', 1.30, 1.46, 0.25, 0.05, 0.3)
    for nm in ('bench', 'lidA', 'lidB', 'cubby', 'pad', 'pouf', 'den_housing', 'cush'):
        appear(nm, 1.40)
    slide('rail', 1.80, 2.02, (0, -0.9, 0), 1.0, 0.7)
    drop('mattress', 2.08, 2.26, 0.45, 0.03, 0.85, 'thud')
    drop('duvet', 2.34, 2.50, 0.35, 0.03, 0.5)
    drop('pillow', 2.48, 2.62, 0.30, 0.06, 0.35)
    if bed:
        drop('pillow2', 2.58, 2.72, 0.30, 0.06, 0.3)
        drop('loft_plush', 2.68, 2.84, 0.30, 0.08, 0.3)
        slide('loft_lamp', 2.80, 2.96, (0, 0, 0.35), 1.0, 0.35, 'tick')
        drop('loft_throw', 2.86, 3.00, 0.25, 0.04, 0.25)
        drop('loft_books', 2.90, 3.04, 0.25, 0.05, 0.2, 'none')
        drop('loft_basket', 2.92, 3.06, 0.25, 0.05, 0.2, 'none')



def timeline_short(tl):
    ev = tl.ev
    drop, fly, slide, grow = tl.drop, tl.fly, tl.slide, tl.grow
    appear, door_z, drawer_fn, lid_fn, section, kid_pose_fn = common(tl)

    # ================= S1 (0.0-3.0): planks, book wall, deck, runners, shelves, books, the clue book, rail, bed
    s1_build(tl, dict(tc=8.05, tb0=8.15, tb1=8.60, ts0=8.60, ts1=9.90), bed=True)

    # ================= S2 (3.3-7.0): book stair, wardrobe, mess
    for k in range(5):
        drop(f'st{k}', 3.30 + 0.08 * k, 3.44 + 0.08 * k, 0.45, 0.03, 0.55 + 0.08 * k, 'thud')
        fly(f'stb{k}', 3.82 + 0.11 * k, 3.98 + 0.11 * k, (0.35, 0, 0.03), 0.03, 0.30, 'tick')
    drop('handrail', 4.40, 4.55, 0.35, 0.03, 0.6, 'thud')
    drop('stair_plush', 4.56, 4.70, 0.30, 0.08, 0.3)
    slide('wd_body', 4.82, 5.00, (0, 0, 0.9), 1.0, 0.9)
    appear('wd_tk', 4.82)
    door_z('wd_door', (W - 0.002, 2.10, 1.0), math.radians(86), 5.06, 5.20, 6.02)
    fly('wd_cl', 5.24, 5.42, (0, -0.55, 0.03), 0.03, 0.4, 'tick')
    drop('wd_st', 5.46, 5.62, 0.30, 0.05, 0.35)
    drop('wd_st2', 5.60, 5.76, 0.30, 0.05, 0.35)
    drop('wd_bk', 5.74, 5.90, 0.30, 0.05, 0.3)
    appear('wd_shoes', 0.0, 0.0)
    for nm in ('hooks', 'backpack', 'print', 'cplant'):
        appear(nm, 5.0)
    mess_tidy(tl, tb_land=6.30, spill0=6.50, land0=10.20, step=0.03, t_basket_fly=10.30, fly=0.65)

    # ================= S3 (7.3-10.7): the pull
    KT = 7.30
    keys = [(KT, (1.56, 0.92, 330)), (KT + 0.08, (1.56, 0.92, 330)), (7.90, (1.48, 1.54, 270)), (8.15, (1.48, 1.54, 270)),
            (8.60, (1.30, 1.46, 270)), (9.90, (1.34, 0.66, 252)), (10.25, (1.30, 0.40, 330)), (12.70, (1.30, 0.40, 330)),
            (13.10, (1.10, 1.12, 300)),
            (13.42, (0.66, 1.20, 275)), (13.60, (0.54, 1.22, 90))]
    walk_pose, at_fn = fg.walk(keys, KID)
    sitp = KID.sit_pose(0.10)
    wave_sit = fg.lerp_pose(sitp, {**sitp, **{k: v for k, v in fg.POSES['wave'].items() if k.startswith(('sh_r', 'elbow_r'))}}, 1.0)

    def waving(t):
        q = dict(wave_sit)
        q['elbow_r'] = 95 + 22 * math.sin(2 * math.pi * (t - 14.0) / 0.42)
        return q
    look_toys = dict(neck=-8, neck_turn=-55, spine_twist=-20)
    acts = [(7.98, 8.10, fg.mirror(REACH), 0.10), (8.16, 9.90, PUSH, 0.08), (10.3, 11.0, look_toys, 0.2),
            (13.66, 15.0, sitp, 0.22), (14.0, 14.75, waving, 0.16)]
    KID.animate(tl, pose=kid_pose_fn(walk_pose, acts), at=at_fn, pop=KT, sound=0.4)
    ev(8.05, 'click', 0.9, 'click')
    tl.events.append(dict(t=8.17, name='creak', strength=0.7, kind='creak', dur=1.75))
    ev(8.60, 'pushed_back', 0.45, 'thud')
    tl.custom('den_panel', lambda t: (I4, (8.92 <= t < 8.98) or t >= 9.06)); ev(8.92, 'den_flick', 0.3, 'tick'); ev(9.06, 'den_on', 0.7, 'chime')
    ev(8.64, 'runner_clank', 0.4, 'thud'); ev(9.34, 'runner_tick', 0.3, 'tick')
    ev(9.90, 'parked', 0.55, 'thud')
    lid_fn('lidA', 9.48, 10.74, t_on=1.40)

    # ================= S4 (11.0-15.0): desk, drawer, chair, rug, blind, lights, the kid sits in the den, wide
    slide('desk', 10.98, 11.14, (0, 0.0, 0.7), 1.0, 0.85)
    fD = drawer_fn(10.98, 11.20, 11.56, (0, 0.30, 0), base=lambda t: (tl.anims['desk'](t)[0], True))
    tl.custom('desk_dr', fD)
    ev(11.28, 'desk_dr_open', 0.5, 'swish'); ev(11.73, 'desk_dr_shut', 0.8, 'thud')
    drop('dr_items', 11.30, 11.44, 0.30, 0.04, 0.35, parent=fD)
    chair_in(tl, 11.62, 11.86)
    slide('cart', 11.30, 11.46, (0, 0.6, 0), 1.0, 0.45)
    for k in range(3):
        drop(f'cart_it{k}', 11.40 + 0.05 * k, 11.52 + 0.05 * k, 0.25, 0.04, 0.2)
    drop('dlamp', 11.70, 11.86, 0.35, 0.05, 0.35)
    drop('dplant', 11.92, 12.06, 0.25, 0.06, 0.3)
    drop('jar', 12.02, 12.16, 0.25, 0.06, 0.3)
    grow('rug', 11.88, 12.08, 'x', (2.05, 0, 0), 0.45, 'tick')
    blind_up(tl, 11.80, 11.95)
    appear('bd_day', 0.0, T_DUSK)
    appear('bd_night', T_DUSK)
    appear('dl_on', 13.08); ev(13.08, 'downlights', 0.6, 'chime')
    appear('loft_lamp_on', 13.28); ev(13.28, 'loft_lamp_on', 0.45, 'chime')
    appear('dlamp_on', 13.46); ev(13.46, 'desk_lamp_on', 0.45, 'chime')
    appear('den_fill_on', 99.0)
    appear('wd_shoes', 99.0)
    ev(13.72, 'sit', 0.35, 'tick')
    drop('pouf', 14.20, 14.36, 0.3, 0.05, 0.3, 'none')
    drop('cush', 13.92, 14.08, 0.30, 0.06, 0.4)
    return tl


HUG = dict(sh_l=55, sh_r=55, sh_l_out=-8, sh_r_out=-8, elbow_l=95, elbow_r=95, spine=-12, neck=4)
POINT = dict(sh_r=105, sh_r_out=35, elbow_r=8, spine_twist=35, neck_turn=55, neck=-10)


def timeline_long(tl):
    ev = tl.ev
    drop, fly, slide, grow, from_camera = tl.drop, tl.fly, tl.slide, tl.grow, tl.from_camera
    appear, door_z, drawer_fn, lid_fn, section, kid_pose_fn = common(tl)
    TC = 27.60
    # ================= A1 (0.0-3.3): the S1 push-in, ending with the rail, mattress, duvet, pillow
    s1_build(tl, dict(tc=TC, tb0=TC + 0.10, tb1=TC + 0.50, ts0=TC + 0.50, ts1=TC + 1.90), bed=False)
    # ================= A2 (3.6-6.8): over the rail: bedding, plush, reading lamp, throw, books, basket
    drop('pillow2', 3.70, 3.86, 0.30, 0.06, 0.35)
    drop('loft_plush', 4.04, 4.22, 0.35, 0.08, 0.35)
    drop('loft_throw', 4.40, 4.56, 0.30, 0.04, 0.35)
    slide('loft_lamp', 4.78, 4.96, (0, 0, 0.35), 1.0, 0.4, 'tick')
    appear('loft_lamp_on', 5.10, 5.45); ev(5.10, 'lamp_test', 0.3, 'chime')
    drop('loft_books', 5.62, 5.78, 0.30, 0.05, 0.3)
    drop('loft_basket', 6.02, 6.18, 0.30, 0.05, 0.35)
    # ================= B1 (7.1-10.3): the book stair
    for k in range(5):
        drop(f'st{k}', 7.22 + 0.10 * k, 7.38 + 0.10 * k, 0.45, 0.03, 0.55 + 0.08 * k, 'thud')
        fly(f'stb{k}', 7.92 + 0.15 * k, 8.10 + 0.15 * k, (0.35, 0, 0.03), 0.03, 0.30, 'tick')
    drop('handrail', 8.80, 8.96, 0.35, 0.03, 0.65, 'thud')
    drop('stair_plush', 9.40, 9.56, 0.30, 0.08, 0.35)
    for nm in ('hooks', 'backpack', 'print', 'cplant'):
        tl.custom(nm, lambda t: (I4, False))
    # ================= B2 (10.6-13.9): wardrobe tower, toe-kick drawer, door, clothes
    slide('wd_body', 10.60, 10.78, (0, 0, 0.9), 1.0, 0.9)
    fT = drawer_fn(10.60, 11.05, 11.66, (0, -0.35, 0), base=lambda t: (tl.anims['wd_body'](t)[0], True))
    tl.custom('wd_tk', fT)
    ev(11.13, 'tk_open', 0.5, 'swish'); ev(11.83, 'tk_shut', 0.8, 'thud')
    drop('wd_shoes', 11.24, 11.40, 0.30, 0.05, 0.35, parent=fT)
    door_z('wd_door', (W - 0.002, 2.10, 1.0), math.radians(86), 11.92, 12.06, 13.20)
    fly('wd_cl', 12.14, 12.34, (0, -0.55, 0.03), 0.03, 0.4, 'tick')
    drop('wd_st', 12.42, 12.58, 0.30, 0.05, 0.35)
    drop('wd_st2', 12.64, 12.80, 0.30, 0.05, 0.35)
    drop('wd_bk', 12.86, 13.02, 0.30, 0.05, 0.35)
    # ================= W1 (14.2-17.2): desk, drawer, jar, plant, lamp
    slide('desk', 14.30, 14.48, (0, 0.0, 0.7), 1.0, 0.85)
    fD = drawer_fn(14.30, 14.80, 15.44, (0, 0.30, 0), base=lambda t: (tl.anims['desk'](t)[0], True))
    tl.custom('desk_dr', fD)
    ev(14.88, 'desk_dr_open', 0.5, 'swish'); ev(15.61, 'desk_dr_shut', 0.8, 'thud')
    drop('dr_items', 14.96, 15.14, 0.30, 0.04, 0.4, parent=fD)
    drop('jar', 15.84, 16.00, 0.30, 0.06, 0.35)
    drop('dplant', 16.18, 16.34, 0.30, 0.06, 0.35)
    drop('dlamp', 16.56, 16.74, 0.40, 0.05, 0.45)
    # ================= W2 (17.5-20.5): chair, rolling cart out / fill / back, blind
    chair_in(tl, 17.62, 17.86)
    sC = slide('cart', 18.02, 18.20, (0, 0.6, 0), 1.0, 0.5)
    fC = drawer_fn(18.02, 18.50, 19.30, (0, 0.38, 0), base=sC, out=0.18)
    tl.custom('cart', fC)
    ev(18.60, 'cart_out', 0.45, 'swish'); ev(19.47, 'cart_in', 0.7, 'thud')
    for k in range(3):
        drop(f'cart_it{k}', 18.66 + 0.18 * k, 18.82 + 0.18 * k, 0.25, 0.04, 0.3, parent=fC)
    blind_up(tl, 19.62, 19.80)
    # ================= F1 (20.8-24.0): rug, hooks, backpack, print, plant
    grow('rug', 20.92, 21.14, 'x', (2.05, 0, 0), 0.5, 'tick')
    for nm in ('hooks', 'backpack', 'print', 'cplant'):
        tl.anims.pop(nm, None)
    slide('hooks', 21.40, 21.56, (-0.4, 0, 0), 1.0, 0.4, 'tick')
    drop('backpack', 21.80, 21.98, 0.35, 0.04, 0.45)
    from_camera('print', 22.22, 22.42, (1.6, 1.05, 1.3), 0.4, 0.5, 'tick')
    drop('cplant', 22.70, 22.88, 0.35, 0.05, 0.45)
    # ================= M (24.3-27.2): the mess; the child walks in and reaches up
    mess_tidy(tl, tb_land=24.55, spill0=24.75, land0=29.85, step=0.045, t_basket_fly=30.62, hop=(34.90, 0.085))
    KT = 25.35
    keys = [(KT, (3.15, 1.62, 280)), (KT + 0.08, (3.15, 1.62, 280)), (26.05, (2.55, 1.95, 285)), (26.65, (1.62, 1.93, 250)),
            (27.05, (1.50, 1.31, 270)),
            (TC + 0.10, (1.50, 1.31, 270)), (TC + 0.50, (1.30, 1.31, 270)), (TC + 1.90, (1.34, 0.60, 252)), (31.40, (1.34, 0.60, 252)),
            (31.80, (1.10, 1.15, 300)), (32.15, (0.66, 1.52, 285)), (32.35, (0.52, 1.58, 90)), (41.00, (0.52, 1.58, 90)),
            (41.45, (1.00, 1.25, 90))]
    walk_pose, at_fn = fg.walk(keys, KID)
    sitp = KID.sit_pose(0.10)
    point = fg.lerp_pose(sitp, {**sitp, **POINT}, 1.0)
    hug = fg.lerp_pose(sitp, {**sitp, **HUG}, 1.0)

    def waving(t):
        q = dict(fg.POSES['wave'])
        q['elbow_r'] = 95 + 22 * math.sin(2 * math.pi * (t - 41.6) / 0.42)
        return q
    look_toys = dict(neck=-8, neck_turn=-55, spine_twist=-20)
    acts = [(27.15, TC + 0.05, REACH, 0.12), (TC + 0.11, TC + 1.90, PUSH, 0.08), (TC + 2.0, 30.8, look_toys, 0.2),
            (32.40, 40.95, sitp, 0.22), (33.30, 33.95, point, 0.18), (36.60, 37.50, hug, 0.2), (41.60, 42.45, waving, 0.16)]
    KID.animate(tl, pose=kid_pose_fn(walk_pose, acts), at=at_fn, pop=KT, sound=0.4)
    # ================= D1 (27.5-30.8): the pull and the tidy-up
    ev(TC, 'click', 0.9, 'click')
    tl.events.append(dict(t=TC + 0.12, name='creak', strength=0.7, kind='creak', dur=1.85))
    ev(TC + 0.50, 'pushed_back', 0.45, 'thud')
    appear('den_panel', 28.70); ev(28.70, 'den_on', 0.7, 'chime')
    ev(TC + 1.90, 'parked', 0.55, 'thud')
    lid_fn('lidA', 29.52, 31.05, t_on=1.40)
    # ================= D2 (31.1-34.3): the child walks in and sits, cushions, points
    cb = drop('cush', 32.80, 32.98, 0.35, 0.06, 0.45)
    ev(32.50, 'sit', 0.35, 'tick')
    drop('pouf', 33.30, 33.48, 0.35, 0.05, 0.4, 'none')
    # ================= E (34.6-37.7): inside the den, the toys hop into order
    appear('den_fill_on', 34.30, 38.00)
    # ================= L (38.0-40.9): blue hour, the lights cascade
    appear('bd_day', 0.0, 38.30)
    appear('bd_night', 38.30); ev(38.30, 'dusk', 0.4, 'swish')
    appear('dl_on', 38.60); ev(38.60, 'downlights', 0.6, 'chime')
    tl.anims.pop('loft_lamp_on', None)
    appear('loft_lamp_on', 38.95); ev(38.95, 'loft_lamp_on', 0.45, 'chime')
    tl.custom('loft_lamp_on', lambda t: (I4, 5.10 <= t < 5.45 or t >= 38.95))
    appear('dlamp_on', 39.30); ev(39.30, 'desk_lamp_on', 0.45, 'chime')
    ev(41.30, 'stand', 0.3, 'tick')
    return tl


def music_cfg():
    """Original cue for this room (pipeline/music.py reads <workdir>/music.json)."""
    hush = [[7.55, 8.05]] if not LONG else [[27.1, 27.6]]
    return dict(bpm=120, MUSIC=dict(drop_at=0, chords=[[62, 66, 69, 73], [59, 62, 66, 69], [55, 59, 62, 66], [57, 61, 64, 69]],
                                    roots=[50, 47, 43, 45], pluck_bars=[0, 1], riser=False, hush=hush))


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    timeline().export(DUR, camera, lights, out)
    json.dump(music_cfg(), open(os.path.join(out, 'music.json'), 'w'))
