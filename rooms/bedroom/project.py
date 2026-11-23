"""11 m² bedroom room-build: bed nook with wardrobe towers, bridge cabinet and fluted sage headboard, lift-up storage bed,
floating desk under the window, sliding-door wardrobe wall with a mirror panel, morning sun to night lights.
Warm white + light oak + sage green + brushed brass. No on-screen text.

    ROOM_REST=1 python3 ../../pipeline/run.py project.py <workdir> probe 0.5,1.5,2.5,3.5,4.5      # finished room, camera stations
    python3 ../../pipeline/run.py project.py <workdir> preview                                      # code-renderer preview with music
    /root/bpyenv/bin/python ../../pipeline/blender_render.py project.py <outdir> --size 720x1280 ...   # photo-real frames

Units: metres. x = east, y = north, z = up. Room x 0..W, y 0..D, z 0..H.
North wall: bed nook. East wall: window + desk. South wall: door (x 0.12..0.98) + sliding wardrobe (x 1.1..W).
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

REST = os.environ.get('ROOM_REST') == '1'
REST_NIGHT = os.environ.get('ROOM_NIGHT') == '1'

W, D, H = 3.4, 3.2, 2.7
FPS = 25
DUR = 6.0 if REST else 32.7

WY0, WY1, WZ0, WZ1 = 1.0, 2.2, 0.95, 2.3          # east window opening
TY = 2.6                                          # front plane of the nook towers (towers y TY..D)
BX0, BX1, BY0, BY1 = 0.95, 2.45, 1.15, 3.13       # bed frame
LIFT_PIV = (BY1 - 0.03, 0.575)                    # bed lift hinge at the head, mattress-top level: the foot end rises
DESK = (2.92, 0.64, 2.56, 0.75)                   # desk front x, y0, y1, top z
WR = (1.1, W, 0.6)                                # wardrobe x0, x1, depth
DL = [(1.0, 1.0), (2.45, 1.0), (1.0, 2.25), (2.45, 2.25)]
SUN_DIR = np.array([-0.75, 0.25, -0.60]) / np.linalg.norm([-0.75, 0.25, -0.60])
T_NIGHT = 28.70
T_BRIDGE, T_SCONCE, T_NICHE, T_DOWN = 29.00, 29.20, 29.35, 29.50
CAPTIONS = []                                     # no on-screen text


# ------------------------------------------------------------------------------------------- materials
def materials():
    mat('subfloor', tex=3, col=srgb(150, 147, 142), p=(0.12,))
    mat('floor', tex=1, col=srgb(202, 170, 132), col2=srgb(182, 148, 112), rough=0.38, f0=0.04, glossy=True, p=(0.18, 1.6))
    mat('wall', tex=3, col=srgb(238, 233, 225), p=(0.02,))
    mat('ceiling', col=srgb(246, 245, 242))
    mat('white_cab', col=srgb(241, 237, 229), rough=0.45)
    mat('white_in', col=srgb(233, 229, 221))
    mat('plinth', col=srgb(70, 66, 62))
    wood_mats('oak', srgb(208, 172, 130), seed=3.0)
    wood_mats('birch', srgb(226, 204, 170), seed=8.0)
    mat('sage', tex=3, col=srgb(150, 168, 144), rough=0.65, p=(0.03,))
    mat('brass', col=srgb(214, 176, 112), rough=0.28, metal=1)
    mat('blackm', col=srgb(26, 26, 28), rough=0.4, f0=0.04, glossy=True)
    mat('winframe', col=srgb(34, 34, 36), rough=0.45)
    mat('sill', col=srgb(238, 236, 231), rough=0.25, f0=0.04, glossy=True)
    mat('mirror', col=srgb(236, 237, 239), rough=0.02, metal=1)
    mat('linen', tex=3, col=srgb(236, 230, 218), rough=0.9, p=(0.045,))
    mat('mattress', tex=5, col=srgb(245, 243, 238), p=(0, 0.02))
    mat('pil_cream', tex=3, col=srgb(240, 234, 222), rough=0.9, p=(0.05,))
    mat('pil_sage', tex=6, col=srgb(158, 174, 150))
    mat('pil_terra', tex=3, col=srgb(196, 130, 98), rough=0.9, p=(0.06,))
    mat('throw', tex=5, col=srgb(150, 166, 142), p=(0, 0.012))
    mat('rug', tex=6, col=srgb(224, 214, 196))
    mat('sheer', tex=3, col=srgb(240, 236, 226), emis=(0.10, 0.098, 0.092), rough=0.9, p=(0.03,))
    mat('alu', col=srgb(196, 198, 202), rough=0.3, metal=1)
    mat('kb', tex=10, col=srgb(52, 52, 56), p=(0.018,))
    mat('lscreen', col=(0, 0, 0), emis=(0.45, 0.55, 0.75))
    mat('ceramic', col=srgb(242, 240, 234), rough=0.22, f0=0.04, glossy=True)
    mat('terra', col=srgb(196, 124, 90))
    mat('leaf', col=srgb(64, 110, 58)); mat('leaf2', col=srgb(94, 140, 72))
    mat('chair_fab', tex=6, col=srgb(228, 220, 206))
    mat('bulb', col=(0, 0, 0), emis=(9.0, 7.6, 5.6))
    mat('led', col=(0, 0, 0), emis=(7.5, 6.8, 5.4))
    mat('led_off', col=srgb(230, 228, 222))
    mat('dl_emis', col=(0, 0, 0), emis=(8.5, 7.6, 6.2))
    mat('charger', col=srgb(238, 238, 236), rough=0.3, f0=0.04, glossy=True)
    mat('charger_glow', col=(0, 0, 0), emis=(0.4, 0.9, 1.4))
    mat('phone', col=srgb(20, 20, 22), rough=0.08, f0=0.05, glossy=True)
    mat('backdrop', tex=9, emis=(1.35, 1.35, 1.35), p=(1.0, 1.0))
    mat('backdrop_night', tex=16, emis=(1.0, 1.0, 1.0), p=(1.0, 1.0))
    mat('box_linen', tex=3, col=srgb(204, 196, 182), p=(0.06,))
    mat('suitcase', col=srgb(198, 114, 84), rough=0.3, f0=0.05, glossy=True)
    mat('vac_bag', tex=3, col=srgb(236, 236, 240), rough=0.35, f0=0.05, glossy=True, p=(0.08,))
    for nm, c in (('cl_cream', (232, 224, 208)), ('cl_sage', (148, 164, 140)), ('cl_navy', (52, 64, 98)), ('cl_rust', (176, 92, 62)),
                  ('cl_grey', (150, 150, 154)), ('cl_white', (242, 242, 240)), ('cl_denim', (88, 112, 150)), ('cl_black', (36, 36, 38)),
                  ('cl_camel', (190, 150, 108)), ('cl_blush', (222, 182, 172))):
        mat(nm, tex=5, col=srgb(*c), p=(2, 0.008))
    for nm, c in (('bk_sage', (150, 168, 144)), ('bk_cream', (232, 222, 200)), ('bk_terra', (190, 112, 82)), ('bk_navy', (54, 66, 100)),
                  ('bk_mustard', (214, 168, 70)), ('bk_white', (240, 238, 232)), ('bk_black', (34, 34, 36))):
        mat(nm, col=srgb(*c), rough=0.6)
    mat('shoe_white', col=srgb(242, 242, 238), rough=0.5); mat('shoe_tan', col=srgb(176, 128, 86), rough=0.4, f0=0.04, glossy=True)
    mat('candle', col=srgb(244, 238, 226)); mat('frame_photo', tex=7, col=srgb(150, 168, 144), col2=srgb(232, 222, 200), p=(2, 0.09))


# ------------------------------------------------------------------------------------------- helpers
def disc(inst, c, r, z0, z1, m, n=28):
    add(inst, lathe(rprof(r, z0, z1, min(0.004, (z1 - z0) * 0.45), 3), n, c), m)


def garment(inst, x, y, z_top, length, width, m, along='x'):
    """Hanging garment on a rail running along `along` (width is across the rail)."""
    hx = 0.20 if along == 'y' else 0.0
    if along == 'x':
        add(inst, tube([(x, y - width * 0.45, z_top - 0.05), (x, y, z_top), (x, y + width * 0.45, z_top - 0.05)], 0.004, 6), 'brass')
        add(inst, rbox((x, y, z_top - 0.06 - length / 2), (0.035, width, length), 0.016, 3), m)
    else:
        add(inst, tube([(x - width * 0.45, y, z_top - 0.05), (x, y, z_top), (x + width * 0.45, y, z_top - 0.05)], 0.004, 6), 'brass')
        add(inst, rbox((x, y, z_top - 0.06 - length / 2), (width, 0.035, length), 0.016, 3), m)


def stack(inst, cx, cy, z0, size, mats_, n, rng):
    z = z0
    for i in range(n):
        sx, sy, sz = size
        jx, jy = rng.uniform(-0.01, 0.01, 2)
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
        M = T(*c) @ R('x', tilt)
        add(inst, xform((P, N), M), m)


# ------------------------------------------------------------------------------------------- shell
def build_shell():
    r = 'room'
    add(r, box(-0.2, -0.2, -0.25, W + 0.2, D + 0.2, -0.012), 'subfloor')
    add(r, box(-0.2, -0.2, H, W + 0.2, D + 0.2, H + 0.1), 'ceiling')
    add(r, box(-0.2, -0.2, -0.25, 0, D + 0.2, H + 0.1), 'wall')
    add(r, box(-0.2, D, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wall')
    add(r, box(-0.2, -0.2, -0.25, 0.12, 0, H + 0.1), 'wall'); add(r, box(0.98, -0.2, -0.25, W + 0.2, 0, H + 0.1), 'wall')
    add(r, box(0.12, -0.2, 2.1, 0.98, 0, H + 0.1), 'wall')
    add(r, box(0.12, -0.06, 0, 0.98, -0.02, 2.1), 'white_cab')                       # door
    add(r, tube([(0.86, -0.02, 1.02), (0.86, 0.035, 1.02), (0.74, 0.035, 1.02)], 0.009, 10), 'brass')
    for b in (box(0.10, -0.02, 0, 0.12, 0.012, 2.12), box(0.98, -0.02, 0, 1.0, 0.012, 2.12), box(0.10, -0.02, 2.1, 1.0, 0.012, 2.12)):
        add(r, b, 'white_cab')                                                       # door casing
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
    # baseboards
    for b in (box(0, 0, 0, 0.012, D, 0.07), box(0, D - 0.012, 0, W, D, 0.07), box(W - 0.012, 0, 0, W, D, 0.07)):
        add(r, b, 'white_cab')
    # downlights (off) in the ceiling
    for (x, y) in DL:
        add(r, lathe([(0.034, H - 0.002), (0.046, H - 0.002), (0.047, H - 0.010), (0.050, H - 0.012), (0.052, H)], 32, (x, y)), 'white_cab')
        disc(r, (x, y), 0.036, H - 0.003, H - 0.0005, 'led_off')
    # window views: day and night (swapped at T_NIGHT)
    add('bd_day', box(W + 4.0, -10, -5, W + 4.05, 14, 9), 'backdrop')
    add('bd_night', box(W + 4.02, -10, -5, W + 4.07, 14, 9), 'backdrop_night')
    # floor planks in six bands (land far to near)
    edges = [-0.05, 0.55, 1.1, 1.65, 2.2, 2.75, D + 0.01]
    for k in range(6):
        add(f'floor{k}', box(0, edges[k], -0.012, W, edges[k + 1], 0.0), 'floor')


# ------------------------------------------------------------------------------------------- bed nook
def build_nook():
    t = 0.018
    for side, (x0, x1) in (('W', (0.0, 0.9)), ('E', (2.5, W))):
        tw = f'tw{side}'
        if side == 'W':
            xo0, xo1, xn0, xn1 = x0, x0 + 0.45, x0 + 0.45, x1             # outer half (wardrobe) / niche half (bed side)
        else:
            xn0, xn1, xo0, xo1 = x0, x0 + 0.45, x0 + 0.45, x1
        zn0, zn1 = 0.46, 0.78
        add(tw, box(x0, TY + 0.05, 0.0, x1, D, 0.06), 'plinth')
        # niche half: solid around the open niche
        add(tw, box(xn0, TY + t, 0.06, xn1, D, zn0), 'white_cab')
        add(tw, box(xn0, TY + t, zn1, xn1, D, H), 'white_cab')
        add(tw, box(xn0, TY + 0.45, zn0, xn1, D, zn1), 'white_cab')
        for b in (box(xn0, TY, zn0, xn1, TY + 0.45, zn0 + 0.014), box(xn0, TY, zn1 - 0.014, xn1, TY + 0.45, zn1),
                  box(xn0, TY + 0.435, zn0, xn1, TY + 0.45, zn1), box(xn0, TY, zn0, xn0 + t, TY + 0.45, zn1), box(xn1 - t, TY, zn0, xn1, TY + 0.45, zn1)):
            add(tw, b, 'oak_x')
        add(tw, box(xn0 + 0.002, TY, zn1 + 0.002, xn1 - 0.002, TY + t, H - 0.003), 'white_cab')        # upper door (fixed)
        hx = xn1 - 0.05 if side == 'W' else xn0 + 0.05
        add(tw, box(hx - 0.006, TY - 0.012, 0.92, hx + 0.006, TY, 1.32), 'brass')
        add(tw, box(xn0 + 0.03, TY + 0.03, zn1 - 0.016, xn1 - 0.03, TY + 0.05, zn1 - 0.014), 'led_off')
        # outer half: hollow wardrobe with a front-to-back rail
        for b in (box(xo0, D - t, 0.06, xo1, D, H), box(xo0, TY + t, 0.06, xo1, D, 0.078), box(xo0, TY + t, H - 0.02, xo1, D, H),
                  box(xo0, TY + t, 2.24, xo1, D, 2.258)):
            add(tw, b, 'white_in')
        add(tw, box(xo0, TY + t, 0.06, xo0 + t, D, H), 'white_cab'); add(tw, box(xo1 - t, TY + t, 0.06, xo1, D, H), 'white_cab')
        xc = (xo0 + xo1) / 2
        add(tw, tube([(xc, TY + 0.06, 2.02), (xc, D - 0.04, 2.02)], 0.011, 10), 'brass')
        # its door (separate: appears open and swings shut)
        hinge_x = xo0 if side == 'W' else xo1
        add(f'{tw}_door', box(xo0 + 0.002, TY, 0.062, xo1 - 0.002, TY + t, H - 0.003), 'white_cab')
        dhx = xo1 - 0.05 if side == 'W' else xo0 + 0.05
        add(f'{tw}_door', box(dhx - 0.006, TY - 0.012, 0.92, dhx + 0.006, TY, 1.32), 'brass')
        # drawer under the niche (opens toward -y)
        dr = f'{tw}_dr'
        add(dr, box(xn0 + 0.002, TY, 0.062, xn1 - 0.002, TY + t, zn0 - 0.002), 'white_cab')
        add(dr, xform(lathe(rprof(0.013, 0, 0.022, 0.006, 3), 16, (0, 0)), T((xn0 + xn1) / 2, TY, 0.30) @ R('x', math.pi / 2)), 'brass')
        add(dr, box(xn0 + 0.03, TY + t, 0.08, xn1 - 0.03, TY + 0.40, 0.09), 'white_in')
        for b in (box(xn0 + 0.03, TY + t, 0.09, xn0 + 0.042, TY + 0.40, 0.38), box(xn1 - 0.042, TY + t, 0.09, xn1 - 0.03, TY + 0.40, 0.38),
                  box(xn0 + 0.03, TY + 0.388, 0.09, xn1 - 0.03, TY + 0.40, 0.38)):
            add(dr, b, 'white_in')
    # garments in the tower wardrobes
    rng = np.random.default_rng(11)
    for side, xc, mats_ in (('W', 0.225, ('cl_camel', 'cl_cream', 'cl_navy', 'cl_sage', 'cl_black')),
                            ('E', W - 0.225, ('cl_white', 'cl_blush', 'cl_denim', 'cl_grey', 'cl_cream'))):
        for k, m in enumerate(mats_):
            garment(f'tw{side}_cl', xc, TY + 0.10 + k * 0.085, 2.02, rng.uniform(0.85, 1.15), 0.38, m, along='y')
    # niche contents
    add('nW_pad', lathe(rprof(0.045, 0.474, 0.482, 0.003, 2), 28, (0.62, 2.80)), 'charger')
    add('nW_phone', rbox((0.62, 2.80, 0.487), (0.075, 0.155, 0.009), 0.004, 3), 'phone')
    add('nW_glow', lathe([(0.04, 0.4822), (0.047, 0.4822), (0.047, 0.4826), (0.04, 0.4826)], 28, (0.62, 2.80)), 'charger_glow')
    add('nW_book', box(0.70, 2.86, 0.474, 0.86, 3.02, 0.50), 'bk_terra')
    add('nW_book', box(0.71, 2.87, 0.50, 0.85, 3.01, 0.52), 'bk_cream')
    add('dW_items', box(0.56, TY + 0.10, 0.09, 0.74, TY + 0.30, 0.12), 'bk_navy')
    add('dW_items', ellipsoid((0.80, TY + 0.22, 0.10), (0.04, 0.02, 0.012), 8), 'blackm')
    add('nE_vase', lathe([(0, 0.474), (0.03, 0.474), (0.045, 0.52), (0.035, 0.6), (0.018, 0.64), (0.022, 0.66), (0, 0.66)], 22, (2.70, 2.82)), 'ceramic')
    for k in range(5):
        a = k * 1.25
        add('nE_vase', tube([(2.70, 2.82, 0.64), (2.70 + 0.05 * math.cos(a), 2.82 + 0.04 * math.sin(a), 0.74 + 0.02 * k)], 0.003, 5), 'cl_camel')
        add('nE_vase', ellipsoid((2.70 + 0.05 * math.cos(a), 2.82 + 0.04 * math.sin(a), 0.745 + 0.02 * k), (0.012, 0.012, 0.02), 6), 'cl_camel')
    add('nE_candle', lathe(rprof(0.035, 0.474, 0.56, 0.004, 3), 22, (2.84, 2.92)), 'candle')
    # bridge cabinet over the bed with lift-up flaps
    bx0, bx1, by0, bz0 = 0.9, 2.5, 2.82, 2.02
    for b in (box(bx0, D - t, bz0, bx1, D, H), box(bx0, by0 + t, bz0, bx1, D, bz0 + t), box(bx0, by0 + t, H - t, bx1, D, H),
              box(bx0, by0 + t, bz0, bx0 + t, D, H), box(bx1 - t, by0 + t, bz0, bx1, D, H), box(1.691, by0 + t, bz0, 1.709, D, H)):
        add('bridge', b, 'white_cab')
    add('bridge', box(bx0 + 0.04, by0 + 0.03, bz0 - 0.006, bx1 - 0.04, by0 + 0.055, bz0), 'led_off')
    for nm, (a0, a1) in (('br_flapL', (bx0, 1.7)), ('br_flapR', (1.7, bx1))):
        add(nm, box(a0 + 0.002, by0, bz0 + 0.002, a1 - 0.002, by0 + t, H - 0.004), 'white_cab')
        add(nm, box(a0 + 0.12, by0 - 0.012, bz0 + 0.03, a1 - 0.12, by0, bz0 + 0.042), 'brass')
    for k, x in enumerate((1.05, 1.36, 1.86, 2.17)):
        add(f'br_box{k}', rbox((x + 0.13, 3.02, bz0 + t + 0.15), (0.27, 0.30, 0.30), 0.02, 3), 'box_linen')
    # fluted sage headboard (eight groups of flutes) on a sage back board
    add('hb_base', box(0.93, D - 0.022, 0.33, 2.47, D, 1.92), 'sage')
    xs = np.arange(0.945, 2.46, 0.03)
    groups = np.array_split(xs, 8)
    for g, xs_g in enumerate(groups):
        for x in xs_g:
            add(f'flute{g}', rbox((x, D - 0.033, 1.125), (0.026, 0.022, 1.58), 0.0095, 3), 'sage')
    # brass reading sconces on the tower sides
    for nm, x, sg in (('scW', 0.9, 1), ('scE', 2.5, -1)):
        add(nm, xform(lathe(rprof(0.04, 0, 0.012, 0.004, 2), 20, (0, 0)), T(x, 2.92, 1.16) @ R('y', sg * math.pi / 2)), 'brass')
        add(nm, tube([(x, 2.92, 1.16), (x + sg * 0.10, 2.92, 1.16), (x + sg * 0.15, 2.92, 1.22)], 0.007, 10), 'brass')
        add(nm, lathe([(0.012, 1.25), (0.03, 1.235), (0.048, 1.19), (0.052, 1.18)], 24, (x + sg * 0.15, 2.92)), 'brass')


# ------------------------------------------------------------------------------------------- bed
def build_bed(rng):
    t = 0.022
    add('bed_floor', box(BX0 + 0.06, BY0 + 0.06, 0.0, BX1 - 0.06, BY1 - 0.04, 0.06), 'plinth')
    add('bed_floor', box(BX0, BY0, 0.06, BX1, BY1, 0.075), 'white_in')
    wood('bed_w', BX0, BY0, 0.06, BX0 + t, BY1, 0.34, 'oak')
    wood('bed_e', BX1 - t, BY0, 0.06, BX1, BY1, 0.34, 'oak')
    wood('bed_n', BX0, BY1 - t, 0.06, BX1, BY1, 0.34, 'oak')
    wood('bed_s', BX0, BY0, 0.06, BX1, BY0 + t, 0.34, 'oak')
    add('bed_div', box(1.689, BY0 + t, 0.075, 1.711, BY1 - t, 0.32), 'white_in')
    add('bed_div', box(BX0 + t, 2.13, 0.075, BX1 - t, 2.152, 0.32), 'white_in')
    # compartment contents
    add('bc_suit', rbox((1.33, 1.64, 0.2), (0.62, 0.44, 0.24), 0.04, 3), 'suitcase')
    add('bc_suit', tube([(1.28, 1.42, 0.28), (1.28, 1.40, 0.29), (1.38, 1.40, 0.29), (1.38, 1.42, 0.28)], 0.008, 6), 'blackm')
    for k, (x, y) in enumerate(((1.95, 1.45), (2.22, 1.45), (1.95, 1.80), (2.22, 1.80))):
        add('bc_boxes', rbox((x, y, 0.19), (0.24, 0.30, 0.22), 0.015, 3), 'box_linen')
    add('bc_bags', rbox((1.33, 2.62, 0.17), (0.64, 0.80, 0.16), 0.07, 5), 'vac_bag')
    add('bc_bags2', rbox((2.07, 2.62, 0.17), (0.64, 0.80, 0.16), 0.07, 5), 'vac_bag')
    # lift-up slatted base with the mattress (hinged at the head end)
    lb = 'bed_lift'
    for b in (box(BX0 + t + 0.004, BY0 + t + 0.004, 0.32, BX1 - t - 0.004, BY0 + t + 0.05, 0.345),
              box(BX0 + t + 0.004, BY1 - t - 0.05, 0.32, BX1 - t - 0.004, BY1 - t - 0.004, 0.345),
              box(BX0 + t + 0.004, BY0 + t + 0.004, 0.32, BX0 + t + 0.05, BY1 - t - 0.004, 0.345),
              box(BX1 - t - 0.05, BY0 + t + 0.004, 0.32, BX1 - t - 0.004, BY1 - t - 0.004, 0.345),
              box(1.68, BY0 + t + 0.004, 0.32, 1.72, BY1 - t - 0.004, 0.345)):
        add(lb, b, 'oak_y')
    for k in range(19):
        y = BY0 + 0.09 + k * 0.098
        add(lb, box(BX0 + 0.08, y, 0.336, 1.68, y + 0.06, 0.348), 'birch_x')
        add(lb, box(1.72, y, 0.336, BX1 - 0.08, y + 0.06, 0.348), 'birch_x')
    add(lb, rbox(((BX0 + BX1) / 2, (BY0 + BY1) / 2, 0.46), (BX1 - BX0 - 0.04, BY1 - BY0 - 0.04, 0.22), 0.045, 5), 'mattress')
    # bedding
    cx = (BX0 + BX1) / 2
    cloth('duvet', BX0, BX1, BY0 + 0.02, 2.56, 0.64, 0.37, 0.05, 'linen', 3)
    add('duvet', rbox((cx, 2.52, 0.652), (BX1 - BX0 + 0.06, 0.15, 0.03), 0.013, 3), 'pil_cream')
    cloth('throw', BX0 - 0.025, BX1 + 0.025, 1.22, 1.64, 0.676, 0.47, 0.04, 'throw', 7, sides=('w', 'e'), puff=0.006)
    pillow('pil1', (1.32, 2.90, 0.82), (0.64, 0.15, 0.42), -0.36, 'pil_cream')
    pillow('pil2', (2.08, 2.90, 0.82), (0.64, 0.15, 0.42), -0.36, 'pil_cream')
    pillow('pil3', (1.47, 2.70, 0.78), (0.44, 0.13, 0.42), -0.28, 'pil_sage')
    pillow('pil4', (1.95, 2.70, 0.78), (0.44, 0.13, 0.42), -0.28, 'pil_terra')
    # rug
    add('rug', rbox((1.7, 1.25, 0.008), (2.0, 1.3, 0.016), 0.006, 3), 'rug')


# ------------------------------------------------------------------------------------------- desk zone
def build_desk(rng):
    dx, dy0, dy1, dz = DESK
    wood('desk', dx, dy0, dz - 0.035, W, dy1, dz, 'oak')
    add('desk', box(W - 0.03, dy0 + 0.05, dz - 0.07, W, dy1 - 0.05, dz - 0.035), 'oak_y')
    # drawer cabinet under the south end (shell) + drawer
    for b in (box(dx + 0.018, dy0, 0.57, W, 1.12, 0.585), box(dx + 0.018, dy0, 0.57, W, dy0 + 0.018, dz - 0.035),
              box(dx + 0.018, 1.102, 0.57, W, 1.12, dz - 0.035), box(W - 0.018, dy0, 0.57, W, 1.12, dz - 0.035)):
        add('desk_cab', b, 'white_in')
    add('desk_dr', box(dx, dy0 + 0.004, 0.574, dx + 0.018, 1.116, dz - 0.039), 'white_cab')
    add('desk_dr', box(dx - 0.012, 0.82, 0.64, dx, 0.94, 0.652), 'brass')
    add('desk_dr', box(dx + 0.018, dy0 + 0.03, 0.59, W - 0.04, 1.09, 0.598), 'white_in')
    for b in (box(dx + 0.018, dy0 + 0.03, 0.598, W - 0.04, dy0 + 0.042, 0.68), box(dx + 0.018, 1.078, 0.598, W - 0.04, 1.09, 0.68),
              box(W - 0.052, dy0 + 0.03, 0.598, W - 0.04, 1.09, 0.68)):
        add('desk_dr', b, 'white_in')
    add('dr_items', box(2.98, 0.70, 0.598, 3.16, 0.92, 0.615), 'bk_sage')
    add('dr_items', tube([(3.2, 0.72, 0.605), (3.2, 1.0, 0.605)], 0.005, 6), 'blackm')
    add('dr_items', tube([(3.24, 0.72, 0.605), (3.24, 1.0, 0.605)], 0.005, 6), 'bk_terra')
    add('dr_items', box(3.06, 0.95, 0.598, 3.3, 1.06, 0.62), 'bk_white')
    # floating shelves beside the window, books, plant, photo
    for k, z in enumerate((1.15, 1.5, 1.85)):
        wood(f'shelf{k}', W - 0.22, 0.66, z, W, 0.96, z + 0.025, 'oak')
    books = [('bk_sage', 0.03, 0.22), ('bk_cream', 0.025, 0.24), ('bk_terra', 0.035, 0.21), ('bk_navy', 0.03, 0.23), ('bk_white', 0.028, 0.2)]
    y = 0.68
    for m, th, h in books:
        add('books0', box(W - 0.19, y, 1.175, W - 0.03, y + th, 1.175 + h), m); y += th + 0.003
    add('books0', box(W - 0.19, 0.86, 1.175, W - 0.03, 0.94, 1.205), 'bk_mustard')
    add('books1', box(W - 0.05, 0.70, 1.525, W - 0.04, 0.86, 1.68), 'frame_photo')
    add('books1', box(W - 0.06, 0.70, 1.525, W - 0.05, 0.86, 1.68), 'oak_z')
    y = 0.88
    for m, th, h in (('bk_black', 0.025, 0.2), ('bk_cream', 0.03, 0.22)):
        add('books1', box(W - 0.19, y, 1.525, W - 0.03, y + th, 1.525 + h), m); y += th + 0.003
    plant('books2', W - 0.11, 0.81, 1.875, 0.05, 0.08, rng, 8, pot='ceramic')
    # laptop (lid hinges at its back edge), lamp, mug, notebook, plant
    add('laptop', box(3.05, 1.30, dz, 3.26, 1.60, dz + 0.012), 'alu')
    add('laptop', box(3.075, 1.33, dz + 0.012, 3.19, 1.57, dz + 0.0125), 'kb')
    add('lid', box(3.05, 1.30, dz + 0.0131, 3.26, 1.60, dz + 0.020), 'alu')
    add('lid', box(3.058, 1.308, dz + 0.0126, 3.252, 1.592, dz + 0.0131), 'lscreen')
    add('lamp', lathe(rprof(0.06, dz, dz + 0.014, 0.005, 3), 28, (3.27, 2.33)), 'brass')
    add('lamp', tube([(3.27, 2.33, dz + 0.01), (3.27, 2.33, 1.17), (3.24, 2.33, 1.21), (3.15, 2.33, 1.22)], 0.006, 10), 'brass')
    add('lamp', lathe([(0.01, 1.235), (0.03, 1.225), (0.052, 1.185), (0.064, 1.15)], 28, (3.15, 2.33)), 'brass')
    add('lamp_on', ellipsoid((3.15, 2.33, 1.17), (0.02, 0.02, 0.02), 8), 'bulb')
    add('mug', lathe([(0, dz), (0.036, dz), (0.04, dz + 0.09), (0.035, dz + 0.09), (0.032, dz + 0.012), (0, dz + 0.012)], 22, (3.12, 1.88)), 'ceramic')
    add('mug', tube([(3.12, 1.92, dz + 0.07), (3.12, 1.95, dz + 0.055), (3.12, 1.92, dz + 0.025)], 0.006, 8), 'ceramic')
    add('notebook', box(3.0, 0.78, dz, 3.22, 1.0, dz + 0.014), 'bk_sage')
    add('notebook', tube([(3.06, 0.84, dz + 0.019), (3.18, 0.95, dz + 0.019)], 0.004, 6), 'brass')
    plant('dplant', 3.30, 2.47, dz, 0.045, 0.07, rng, 9)
    # chair (faces the desk, rolls in)
    cx, cy = 2.66, 0.90
    add('chair', rbox((cx, cy, 0.47), (0.46, 0.46, 0.07), 0.03, 3), 'chair_fab')
    add('chair', xform(rbox((cx - 0.23, cy, 0.79), (0.06, 0.44, 0.40), 0.03, 3), about((cx - 0.23, cy, 0.6), R('y', -0.12))), 'chair_fab')
    add('chair', tube([(cx - 0.12, cy, 0.46), (cx - 0.22, cy, 0.52), (cx - 0.24, cy, 0.62)], 0.012, 8), 'blackm')
    add('chair', tube([(cx, cy, 0.11), (cx, cy, 0.44)], 0.024, 12), 'blackm')
    for k in range(5):
        a = 2 * math.pi * k / 5 + 0.3
        add('chair', tube([(cx, cy, 0.10), (cx + 0.29 * math.cos(a), cy + 0.29 * math.sin(a), 0.06)], 0.014, 8), 'blackm')
        add('chair', ellipsoid((cx + 0.29 * math.cos(a), cy + 0.29 * math.sin(a), 0.028), (0.025, 0.025, 0.026), 8), 'blackm')
    # sheer curtains (built closed; gathered by the timeline during the day)
    add('cur_track', box(W - 0.09, 0.84, 2.62, W - 0.07, 2.36, 2.64), 'brass')
    for nm, (y0, y1) in (('cur_L', (0.88, 1.60)), ('cur_R', (1.60, 2.32))):
        nu, nv = 49, 8
        V = np.zeros((nu, nv, 3))
        for i, y in enumerate(np.linspace(y0, y1, nu)):
            for j, z in enumerate(np.linspace(0.80, 2.60, nv)):
                V[i, j] = (W - 0.075 + 0.022 * math.sin(2 * math.pi * (y - y0) / 0.09), y, z)
        add(nm, grid_tris(V), 'sheer')


# ------------------------------------------------------------------------------------------- wardrobe wall (south)
def build_wardrobe(rng):
    x0, x1, wd = WR
    t = 0.018
    add('wr_body', box(x0, 0, 0.0, x1, wd - 0.06, 0.06), 'plinth')
    for b in (box(x0, 0, 0.06, x1, t, 2.62), box(x0, 0, 0.06, x1, wd - 0.04, 0.078), box(x0, 0, 2.6, x1, wd - 0.04, 2.62)):
        add('wr_body', b, 'white_in')
    add('wr_body', box(x0, 0, 0.06, x0 + t, wd, 2.62), 'white_cab'); add('wr_body', box(x1 - t, 0, 0.06, x1, wd, 2.62), 'white_cab')
    add('wr_body', box(x0, 0, 2.62, x1, wd, H), 'white_cab')
    add('wr_body', box(x0, wd - 0.05, 2.585, x1, wd, 2.62), 'alu')                     # top track
    add('wr_div', box(1.86, t, 0.078, 1.878, wd - 0.04, 2.6), 'white_in')
    add('wr_div', box(2.62, t, 0.078, 2.638, wd - 0.04, 2.6), 'white_in')
    # shelves
    for b in (box(x0 + t, t, 2.2, 1.86, wd - 0.04, 2.218), box(x0 + t, t, 0.26, 1.86, wd - 0.06, 0.276),
              box(1.878, t, 2.2, 2.62, wd - 0.04, 2.218), box(1.878, t, 0.878, 2.62, wd - 0.04, 0.896)):
        add('wr_shelves', b, 'white_in')
    for z in (0.45, 0.85, 1.25):
        add('wr_shelves', box(2.638, t, z, x1 - t, wd - 0.04, z + 0.018), 'white_in')
    # drawers in section B (four)
    for k in range(4):
        z0 = 0.08 + k * 0.198
        nm = 'wr_drB' if k == 2 else 'wr_drawers'
        add(nm, box(1.882, wd - 0.075, z0 + 0.002, 2.616, wd - 0.057, z0 + 0.194), 'oak_x')
        add(nm, box(2.19, wd - 0.057, z0 + 0.16, 2.31, wd - 0.05, z0 + 0.172), 'brass')
        if k == 2:
            add(nm, box(1.90, 0.04, z0 + 0.012, 2.60, wd - 0.075, z0 + 0.022), 'white_in')
            for b in (box(1.90, 0.04, z0 + 0.022, 1.912, wd - 0.075, z0 + 0.16), box(2.588, 0.04, z0 + 0.022, 2.60, wd - 0.075, z0 + 0.16),
                      box(1.90, 0.04, z0 + 0.022, 2.60, 0.052, z0 + 0.16)):
                add(nm, b, 'white_in')
    z0 = 0.08 + 2 * 0.198 + 0.022
    stack('wr_drB_c', 2.05, 0.30, z0, (0.24, 0.30, 0.035), ['cl_white', 'cl_grey', 'cl_navy'], 3, rng)
    stack('wr_drB_c', 2.32, 0.30, z0, (0.24, 0.30, 0.035), ['cl_sage', 'cl_cream', 'cl_black'], 3, rng)
    stack('wr_drB_c', 2.50, 0.30, z0, (0.16, 0.30, 0.035), ['cl_blush', 'cl_white'], 2, rng)
    # rails
    add('wr_rails', tube([(x0 + 0.03, 0.29, 2.0), (1.85, 0.29, 2.0)], 0.011, 10), 'brass')
    add('wr_rails', tube([(1.89, 0.29, 1.85), (2.61, 0.29, 1.85)], 0.011, 10), 'brass')
    # pull-down rail in section C (rail + arms + clothes ride together)
    add('wr_pull', tube([(2.66, 0.29, 2.35), (x1 - 0.04, 0.29, 2.35)], 0.011, 10), 'brass')
    for x in (2.652, x1 - 0.026):
        add('wr_pull', tube([(x, 0.29, 2.35), (x, 0.12, 2.52)], 0.008, 8), 'alu')
    for k, m in enumerate(('cl_cream', 'cl_sage', 'cl_rust', 'cl_white', 'cl_denim')):
        garment('wr_pull', 2.72 + k * 0.13, 0.29, 2.35, 0.62, 0.40, m)
    # garments: long in A, shirts in B
    for k, m in enumerate(('cl_camel', 'cl_black', 'cl_cream', 'cl_navy', 'cl_blush', 'cl_grey')):
        garment('wr_clA', x0 + 0.08 + k * 0.12, 0.29, 2.0, rng.uniform(1.0, 1.25), 0.42, m)
    for k, m in enumerate(('cl_white', 'cl_denim', 'cl_sage', 'cl_white', 'cl_rust', 'cl_navy')):
        garment('wr_clB', 1.93 + k * 0.115, 0.29, 1.85, 0.72, 0.40, m)
    # folded stacks on the C shelves, boxes on top shelves, shoes
    for k, z in enumerate((0.468, 0.868, 1.268)):
        stack(f'wr_fold{k}', 2.84, 0.30, z, (0.30, 0.32, 0.05), [('cl_cream', 'cl_sage', 'cl_grey'), ('cl_navy', 'cl_white', 'cl_camel'),
                                                                 ('cl_blush', 'cl_cream', 'cl_denim')][k], 4, rng)
        stack(f'wr_fold{k}', 3.18, 0.30, z, (0.30, 0.32, 0.05), [('cl_white', 'cl_black', 'cl_white'), ('cl_sage', 'cl_grey', 'cl_cream'),
                                                                 ('cl_rust', 'cl_white', 'cl_navy')][k], 3, rng)
    for x in (1.25, 1.62, 2.06, 2.42):
        add('wr_boxes', rbox((x, 0.30, 2.218 + 0.13), (0.30, 0.40, 0.26), 0.02, 3), 'box_linen')
    for k, x in enumerate((1.18, 1.36, 1.54, 1.72)):
        m = ('shoe_white', 'shoe_tan', 'shoe_white', 'shoe_tan')[k]
        for dy in (-0.06, 0.06):
            add('wr_shoes', ellipsoid((x, 0.30 + dy, 0.30), (0.05, 0.13, 0.035), 10), m)
    # LED strips under the top shelves (shown while the doors are open)
    for (a0, a1) in ((x0 + 0.03, 1.85), (1.89, 2.61), (2.65, x1 - 0.03)):
        add('wr_led', box(a0, wd - 0.13, 2.192, a1, wd - 0.11, 2.2), 'led')
    # sliding door panels: oak / mirror / oak
    add('wr_pA', box(x0, wd - 0.025, 0.07, 1.88, wd - 0.005, 2.58), 'oak_z')
    add('wr_pA', box(1.84, wd - 0.006, 0.9, 1.852, wd + 0.004, 1.6), 'brass')
    add('wr_pC', box(2.62, wd - 0.025, 0.07, x1, wd - 0.005, 2.58), 'oak_z')
    add('wr_pC', box(2.648, wd - 0.006, 0.9, 2.66, wd + 0.004, 1.6), 'brass')
    add('wr_pB', box(1.86, wd - 0.048, 0.07, 2.64, wd - 0.028, 2.58), 'oak_z')
    add('wr_pB', box(1.885, wd - 0.0285, 0.095, 2.615, wd - 0.0275, 2.555), 'mirror')


def build():
    materials()
    rng = np.random.default_rng(5)
    build_shell()
    build_nook()
    build_bed(rng)
    build_desk(rng)
    build_wardrobe(rng)
    # light emitters that switch on (each its own piece so they can cascade)
    add('led_bridge', box(0.94, 2.85, 2.012, 2.46, 2.875, 2.0175), 'led')
    for side, (xn0, xn1) in (('W', (0.45, 0.9)), ('E', (2.5, 2.95))):
        add('led_niche', box(xn0 + 0.03, TY + 0.03, 0.7645, xn1 - 0.03, TY + 0.05, 0.766), 'led')
    for nm, x, sg in (('sc_onW', 0.9, 1), ('sc_onE', 2.5, -1)):
        add(nm, ellipsoid((x + sg * 0.15, 2.92, 1.195), (0.018, 0.018, 0.012), 8), 'bulb')
    for (x, y) in DL:
        disc('dl_on', (x, y), 0.037, H - 0.005, H - 0.0035, 'dl_emis')


# ------------------------------------------------------------------------------------------- camera
VFOV = 85.0
# Each station glides slowly from its start pose to its end pose (the hits' camera never stands still),
# and fast eased swings join the stations.
def P(x, y, z, yaw, pitch):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch)


SA = (P(1.70, 0.66, 1.46, 0.0, -3.0), P(1.70, 0.92, 1.40, 0.0, -4.0))          # nook, straight on: push in
SA2 = (P(0.35, 1.30, 1.42, 60.0, -18.0), P(0.45, 1.55, 1.38, 52.0, -17.0))     # across the bed: lift-up storage, bedding
SB = (P(0.30, 1.02, 1.28, 22.0, 0.0), P(0.36, 1.32, 1.26, 18.0, -1.0))         # west tower, niche, bridge
SC = (P(0.95, 0.85, 1.32, 80.0, -7.0), P(1.22, 1.00, 1.30, 84.0, -7.0))        # desk + window
SD = (P(2.25, 2.55, 1.32, 181.0, -4.0), P(2.22, 2.20, 1.30, 178.0, -4.0))      # wardrobe wall
SE = (P(1.70, 0.64, 1.50, 0.0, -4.0), P(1.70, 0.98, 1.42, 0.0, -5.0))          # final: slow push in through the lights
HOLDS = [(0.0, 3.62, SA), (3.92, 7.30, SA2), (7.60, 12.40, SB), (12.70, 18.20, SC), (18.50, 26.50, SD), (27.10, DUR, SE)]


camera = hold_camera(HOLDS, VFOV, rest=REST)      # glide inside each hold, swings between (pipeline/camkit.py)


# ------------------------------------------------------------------------------------------- lights (fixed slots)
LSKY = (10.0, 10.6, 11.6)
LSUN = (66000.0, 59000.0, 48000.0)
LDOOR = (2.0, 1.95, 1.85)
LBOUNCE = (1.0, 0.98, 0.95)
LBRIDGE = (62.0, 52.0, 38.0)
LSCONCE = (1250.0, 1050.0, 760.0)
LNICHE = (36.0, 30.0, 22.0)
LDOWN = (420.0, 370.0, 290.0)
LLAMP = (90.0, 70.0, 44.0)
LSCREEN = (0.45, 0.55, 0.75)
LWR = (30.0, 27.0, 21.0)


def lights(mats4, vis):
    off = (0.0, 0.0, 0.0)
    night = bool(vis.get('bd_night'))

    def k(L, on, f=1.0):
        return tuple(v * f for v in L) if on else off
    Ls = []
    Ls.append(rect_light((W + 0.16, WY0, WZ0), (0, 0, WZ1 - WZ0), (0, WY1 - WY0, 0), k(LSKY, not night), always=1))      # 0 sky (-x)
    sc = np.array([W, (WY0 + WY1) / 2, (WZ0 + WZ1) / 2]) - SUN_DIR * 3.0      # between the window and the backdrop
    Ls.append(spot_rect(tuple(sc), tuple(SUN_DIR), 0.06, k(LSUN, not night), 0.0))                                       # 1 sun
    Ls.append(rect_light((0.15, 0.005, 0.3), (0, 0, 1.9), (0.80, 0, 0), k(LDOOR, True, 0.06 if night else 1.0), always=1))  # 2 fill +y
    Ls.append(rect_light((0.005, 0.3, 0.6), (0, 2.2, 0), (0, 0, 1.6), k(LBOUNCE, True, 0.07 if night else 1.0)))       # 3 fill +x
    Ls.append(rect_light((0.95, 2.85, 2.008), (0, 0.025, 0), (1.50, 0, 0), k(LBRIDGE, vis.get('led_bridge'))))          # 4 bridge (down)
    for nm, x, sg in (('sc_onW', 0.9, 1), ('sc_onE', 2.5, -1)):                                                         # 5-6 sconces
        Ls.append(spot_rect((x + sg * 0.15, 2.92, 1.175), (sg * 0.15, -0.05, -1.0), 0.03, k(LSCONCE, vis.get(nm)), 6.0))
    for (xn0, xn1) in ((0.45, 0.9), (2.5, 2.95)):                                                                        # 7-8 niche LEDs
        Ls.append(rect_light((xn0 + 0.03, TY + 0.03, 0.7635), (0, 0.02, 0), (xn1 - xn0 - 0.06, 0, 0), k(LNICHE, vis.get('led_niche'))))
    for (x, y) in DL:                                                                                                    # 9-12 downlights
        Ls.append(spot_rect((x, y, H - 0.006), (0, 0, -1), 0.05, k(LDOWN, vis.get('dl_on')), 4.0))
    if vis.get('lamp'):                                                                                                  # 13 desk lamp
        c = mats4['lamp'] @ np.array([3.15, 2.33, 1.17, 1.0])
        Ls.append(sphere_light(tuple(c[:3]), 0.02, k(LLAMP, vis.get('lamp_on'))))
    else:
        Ls.append(sphere_light((3.15, 2.33, 1.17), 0.02, off))
    M = mats4['lid']                                                                                                     # 14 laptop screen
    c0 = (M @ np.array([3.058, 1.308, 0.7625, 1.0]))[:3]
    eu = M[:3, :3] @ np.array([0.194, 0, 0]); ev = M[:3, :3] @ np.array([0, 0.284, 0])
    if np.cross(eu, ev)[0] > 0:
        eu, ev = ev, eu
    Ls.append(rect_light(tuple(c0), tuple(eu), tuple(ev), k(LSCREEN, bool(vis.get('lid')) and M[0, 0] < 0.3)))
    x0, x1, wd = WR
    for (a0, a1) in ((x0 + 0.03, 1.85), (1.89, 2.61), (2.65, x1 - 0.03)):                                                # 15-17 wardrobe LEDs
        Ls.append(rect_light((a0, wd - 0.13, 2.19), (0, 0.02, 0), (a1 - a0, 0, 0), k(LWR, vis.get('wr_led'))))
    return Ls


# Blender (Cycles) look: see pipeline/blender_render.py
BLENDER = dict(
    exposure=-0.38,
    look='AgX - Medium High Contrast',
    translucent={'sheer': 0.55},
    separate=['backdrop', 'backdrop_night'],
    fill_lights=[2, 3],
    wood_scale=(55.0, 1.6),
    bake_rect={'backdrop': (-3.0, 7.0, -2.0, 6.0), 'backdrop_night': (-3.0, 7.0, -2.0, 6.0)},
    bake_px={'backdrop': 0.006, 'backdrop_night': 0.004, 'floor': 0.0015},
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
            for nm in ('bd_night', 'led_bridge', 'led_niche', 'sc_onW', 'sc_onE', 'dl_on', 'lamp_on', 'wr_led'):
                tl.custom(nm, hidden)
        # curtains gathered (day) in the rest view
        if not REST_NIGHT:
            tl.custom('cur_L', lambda t: (about((0, 0.88, 0), S(1, 0.42, 1)), True))
            tl.custom('cur_R', lambda t: (about((0, 2.32, 0), S(1, 0.42, 1)), True))
        return tl
    cen, ev = tl.cen, tl.ev
    drop, fly, slide, grow, from_camera = tl.drop, tl.fly, tl.slide, tl.grow, tl.from_camera

    def appear(name, t_on, t_off=None):
        tl.custom(name, lambda t: (I, t >= t_on and (t_off is None or t < t_off)))

    def door_z(name, hinge, a_open, t_in, t_in1, t_close, dur=0.17, axis='z'):
        """Door that pops in already open (slightly oversized, from above) and swings shut."""
        hinge = np.array(hinge, float)

        def f(t):
            if t < t_in:
                return I, False
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
        ev(t_close + dur, name + '_shut', 0.75, 'thud')

    def drawer_fn(t_appear, t_open, t_close, off, base=None, out=0.10, shut=0.17):
        off = np.array(off, float)

        def f(t):
            if t < t_appear:
                return I, False
            B = base(t)[0] if base is not None else I
            if t < t_open:
                return B, True
            if t < t_close:
                return B @ T(*(off * eob((t - t_open) / out, 1.6))), True
            k = 1 - smooth((t - t_close) / shut)
            tau = t - t_close - shut
            wob = 0.006 * math.exp(-tau / 0.05) * math.sin(2 * math.pi * tau / 0.12) if tau > 0 else 0.0
            return B @ T(*(off * k + off / (np.linalg.norm(off) + 1e-9) * wob)), True
        return f

    # ================= shot A (0.0-3.62, hero): floor, towers, bridge, fluted headboard, bed frame, base + mattress
    for k in range(6):
        t1 = 0.30 + 0.07 * (5 - k)
        drop(f'floor{k}', t1 - 0.16, t1, 0.24, 0.05, 0.3 + 0.03 * k, 'tick')
    sTW = grow('twW', 0.85, 1.10, 'z', (0, 0, 0), 0.9)
    sTE = grow('twE', 1.00, 1.25, 'z', (0, 0, 0), 0.9)
    drop('bridge', 1.35, 1.55, 0.45, 0.02, 0.8, 'thud')
    grow('hb_base', 1.62, 1.80, 'z', (0, 0, 0.33), 0.6)
    for g in range(8):
        grow(f'flute{g}', 1.80 + 0.06 * g, 1.94 + 0.06 * g, 'z', (0, 0, 0.33), 0.25)
    drop('bed_floor', 2.40, 2.52, 0.35, 0.02, 0.6, 'thud')
    slide('bed_w', 2.50, 2.64, (-0.55, 0, 0), 1.0, 0.55)
    slide('bed_e', 2.56, 2.70, (0.55, 0, 0), 1.0, 0.55)
    drop('bed_n', 2.62, 2.74, 0.40, 0.03, 0.5, 'thud')
    slide('bed_s', 2.70, 2.84, (0, -0.6, 0), 1.0, 0.6)
    drop('bed_div', 2.86, 2.98, 0.35, 0.03, 0.35)
    piv = np.array([0.0, *LIFT_PIV])
    OPEN = math.radians(-40)
    LO, LC = 4.05, 5.30                      # lift opens / closes

    def lift(t):
        if t < 3.15:
            return I, False
        if t < 3.40:
            u = (t - 3.15) / 0.25
            return T(0, 0, 0.5 * (1 - u * u)) @ about(cen['bed_lift'], S(*([0.6 + 0.4 * smooth(u / 0.4)] * 3))), True
        if t < LO:
            tau = t - 3.40
            return T(0, 0, 0.02 * math.exp(-tau / 0.06) * abs(math.sin(math.pi * tau / 0.1))), True
        if t < LC:
            return about(piv, R('x', OPEN * eob(min(1.0, (t - LO) / 0.40), 1.15))), True
        u = (t - LC) / 0.28
        if u < 1:
            return about(piv, R('x', OPEN * (1 - smooth(u)))), True
        tau = t - LC - 0.28
        return about(piv, R('x', math.radians(-1.0) * math.exp(-tau / 0.05) * math.sin(2 * math.pi * tau / 0.14))), True
    tl.custom('bed_lift', lift)
    ev(3.40, 'bed_lift_land', 1.0, 'thud'); ev(LO + 0.08, 'bed_lift_open', 0.6, 'swish'); ev(LC + 0.28, 'bed_lift_shut', 1.0, 'thud')

    # ================= shot A2 (3.92-7.30, across the bed): lift-up storage fills, bedding lands
    drop('bc_suit', 4.48, 4.68, 0.55, 0.04, 0.5, 'thud')
    drop('bc_boxes', 4.62, 4.80, 0.55, 0.04, 0.4)
    drop('bc_bags', 4.76, 4.94, 0.55, 0.05, 0.35)
    drop('bc_bags2', 4.88, 5.06, 0.55, 0.05, 0.35)
    drop('duvet', 5.72, 5.92, 0.45, 0.03, 0.6, 'thud')
    for i, nm in enumerate(('pil1', 'pil2', 'pil3', 'pil4')):
        drop(nm, 6.00 + 0.11 * i, 6.18 + 0.11 * i, 0.40, 0.08, 0.35)
    grow('throw', 6.55, 6.83, 'x', (BX0 - 0.07, 0, 0), 0.4)

    # ================= shot B (7.60-12.40): niche drawer, charger, sconce, tower wardrobe, bridge flaps
    fW = drawer_fn(0.85, 7.75, 8.40, (0, -0.34, 0), base=sTW)
    tl.custom('twW_dr', fW)
    ev(7.83, 'twW_dr_open', 0.6, 'swish'); ev(8.57, 'twW_dr_shut', 0.8, 'thud')
    drop('dW_items', 7.98, 8.16, 0.30, 0.04, 0.35, parent=fW)
    tl.custom('twE_dr', lambda t: (sTE(t)[0], t >= 1.00))
    drop('nW_pad', 8.75, 8.89, 0.20, 0.04, 0.25)
    drop('nW_phone', 8.95, 9.12, 0.22, 0.05, 0.35)
    appear('nW_glow', 9.20)
    ev(9.20, 'charger_on', 0.4, 'chime')
    drop('nW_book', 9.30, 9.46, 0.22, 0.04, 0.3)
    slide('scW', 9.52, 9.70, (0.18, 0, 0), 1.0, 0.4)
    door_z('twW_door', (0.0, TY, 1.35), math.radians(-88), 9.85, 10.00, 10.70)
    fly('twW_cl', 10.05, 10.40, (0, -0.55, 0.02), 0.03, 0.4, 'tick')
    door_z('br_flapL', (0, 2.81, 2.69), math.radians(-85), 10.95, 11.10, 11.90, axis='x')
    door_z('br_flapR', (0, 2.81, 2.69), math.radians(-85), 11.02, 11.17, 11.98, axis='x')
    for k in range(4):
        fly(f'br_box{k}', 11.25 + 0.1 * k, 11.45 + 0.1 * k, (0, -0.6, 0.05), 0.04, 0.3, 'tick')
    tl.custom('twE_door', lambda t: (sTE(t)[0], t >= 1.00))
    tl.custom('twE_cl', lambda t: (sTE(t)[0], t >= 1.00))

    # ================= shot C (12.70-18.20): desk, drawer, shelves, books, laptop, lamp, chair, curtains
    slide('desk', 12.85, 13.05, (0.55, 0, 0), 1.0, 0.8)
    slide('desk_cab', 13.12, 13.28, (0.5, 0, 0), 1.0, 0.5)
    fD = drawer_fn(13.12, 15.00, 15.60, (-0.30, 0, 0), base=lambda t: (tl.anims['desk_cab'](t)[0], True))
    tl.custom('desk_dr', fD)
    ev(15.08, 'desk_dr_open', 0.6, 'swish'); ev(15.77, 'desk_dr_shut', 0.8, 'thud')
    drop('dr_items', 15.18, 15.36, 0.30, 0.04, 0.35, parent=fD)
    for k in range(3):
        slide(f'shelf{k}', 13.40 + 0.08 * k, 13.56 + 0.08 * k, (0.3, 0, 0), 1.0, 0.35)
    for k in range(3):
        from_camera(f'books{k}', 13.75 + 0.14 * k, 13.93 + 0.14 * k, np.array(SC[0]['pos']), 0.3, 0.3, 'tick')
    drop('laptop', 14.28, 14.44, 0.30, 0.03, 0.4)
    drop('lid', 14.28, 14.44, 0.30, 0.03, 0.0, 'none')
    drop('lamp', 14.42, 14.60, 0.35, 0.05, 0.4)
    drop('mug', 14.56, 14.70, 0.25, 0.06, 0.3)
    drop('notebook', 14.66, 14.80, 0.25, 0.04, 0.3)
    drop('dplant', 14.76, 14.92, 0.25, 0.06, 0.3)
    lid_base = tl.anims['lid']
    hinge = np.array([3.26, 0.0, DESK[3] + 0.0128])

    def lid(t):
        M, v = lid_base(t)
        if t < 16.45:
            return M, v
        u = c01((t - 16.45) / 0.32)
        return about(hinge, R('y', math.radians(108) * eob(u, 0.6))), True
    tl.custom('lid', lid)
    ev(16.52, 'lid_open', 0.5, 'swish')
    ch_c = cen['chair']
    ch_start = np.array([1.75, 0.95, ch_c[2]])

    def chair(t, t0=15.90, t1=16.24):
        if t < t0:
            return I, False
        u = (t - t0) / (t1 - t0)
        if u < 1:
            off = (1 - eoc(u)) * (ch_start - ch_c)
            ang = math.radians(150) * (1 - eob(u, 1.2))
        else:
            off = np.zeros(3)
            ang = math.radians(5) * math.exp(-(t - t1) / 0.12) * math.sin(2 * math.pi * (t - t1) / 0.3)
        return T(*off) @ about(ch_c, R('z', ang)), True
    tl.custom('chair', chair)
    ev(16.24, 'chair', 0.8, 'thud')
    drop('cur_track', 16.90, 17.04, 0.20, 0.03, 0.3)
    for nm, edge, t0 in (('cur_L', 0.88, 17.08), ('cur_R', 2.32, 17.18)):
        def cur(t, edge=edge, t0=t0):
            if t < t0:
                return I, False
            G = about((0, edge, 0), S(1, 0.42, 1))
            if t < t0 + 0.2:
                u = (t - t0) / 0.2
                return T(0, 0, 0.5 * (1 - u * u)) @ G, True
            if t < T_NIGHT:
                return G, True
            u = c01((t - T_NIGHT - 0.05) / 0.45)
            s = 0.42 + 0.58 * smooth(u)
            return about((0, edge, 0), S(1, s, 1)), True
        tl.custom(nm, cur)
        ev(t0 + 0.2, nm, 0.3, 'tick')

    # ================= shot D (18.50-26.50): rug, wardrobe wall
    grow('rug', 18.52, 18.76, 'y', (0, 1.9, 0), 0.6)
    slide('wr_body', 18.85, 19.10, (0, -0.62, 0), 1.0, 1.0)
    drop('wr_div', 19.15, 19.32, 0.35, 0.03, 0.4)
    from_camera('wr_shelves', 19.38, 19.58, np.array(SD[0]['pos']), 0.3, 0.4, 'tick')
    slide('wr_drawers', 19.65, 19.85, (0, 0.5, 0), 1.0, 0.5)
    fB = drawer_fn(19.65, 22.00, 22.60, (0, 0.34, 0),
                   base=lambda t: (T(0, 0.5 * (1 - eob(c01((t - 19.65) / 0.2), 1.0)), 0) if t < 19.85 else I, True))
    tl.custom('wr_drB', fB)
    ev(22.08, 'wr_drB_open', 0.6, 'swish'); ev(22.77, 'wr_drB_shut', 0.8, 'thud')
    drop('wr_drB_c', 22.20, 22.42, 0.30, 0.04, 0.35, parent=fB)
    drop('wr_rails', 19.90, 20.05, 0.25, 0.03, 0.3)
    slide('wr_clA', 20.10, 20.50, (-0.9, 0, 0), 1.0, 0.45)
    slide('wr_clB', 20.40, 20.80, (0.9, 0, 0), 1.0, 0.45)
    for k in range(3):
        drop(f'wr_fold{k}', 20.95 + 0.12 * k, 21.13 + 0.12 * k, 0.30, 0.05, 0.35)
    drop('wr_shoes', 21.40, 21.58, 0.30, 0.06, 0.35)
    drop('wr_boxes', 21.50, 21.68, 0.30, 0.04, 0.3)
    tl.custom('wr_led', lambda t: (I, 21.80 <= t < 25.05 or 25.35 <= t < 26.25))
    ev(21.80, 'wr_led_on', 0.5, 'chime')

    def pull(t):
        if t < 19.90:
            return I, False
        if t < 20.05:
            u = (t - 19.90) / 0.15
            return T(0, 0, 0.25 * (1 - u * u)), True
        if t < 22.95:
            return I, True
        if t < 23.70:
            k = smooth(c01((t - 22.95) / 0.40))
        else:
            k = 1 - smooth(c01((t - 23.70) / 0.35))
        return T(0, 0.10 * k, -0.62 * k), True
    tl.custom('wr_pull', pull)
    ev(23.00, 'pull_down', 0.5, 'swish'); ev(24.05, 'pull_up', 0.6, 'thud')
    slide('wr_pA', 24.25, 24.45, (-0.75, 0, 0), 1.0, 0.8)
    slide('wr_pC', 24.40, 24.60, (0.75, 0, 0), 1.0, 0.8)
    pB_base = drop('wr_pB', 24.60, 24.84, 0.5, 0.02, 0.9, 'thud')

    def pB(t):
        M, v = pB_base(t)
        if t < 25.30:
            return M, v
        if t < 26.00:
            return T(0.72 * eob(c01((t - 25.30) / 0.30), 0.8), 0, 0), True
        return T(0.72 * (1 - smooth(c01((t - 26.00) / 0.30))), 0, 0), True
    tl.custom('wr_pB', pB)
    ev(25.38, 'mirror_open', 0.5, 'swish'); ev(26.30, 'mirror_shut', 0.8, 'thud')

    # ================= shot E (27.10-32.70): decor, night, lights cascade, hold
    drop('nE_vase', 27.35, 27.52, 0.25, 0.05, 0.35)
    drop('nE_candle', 27.50, 27.66, 0.22, 0.05, 0.3)
    slide('scE', 27.75, 27.95, (-0.18, 0, 0), 1.0, 0.45)
    appear('bd_day', 0.0, T_NIGHT)
    appear('bd_night', T_NIGHT)
    ev(T_NIGHT, 'night', 0.5, 'swish')
    appear('led_bridge', T_BRIDGE); ev(T_BRIDGE, 'bridge_on', 0.7, 'chime')
    appear('sc_onW', T_SCONCE); appear('sc_onE', T_SCONCE + 0.08); ev(T_SCONCE, 'sconces', 0.6, 'chime')
    appear('led_niche', T_NICHE); ev(T_NICHE, 'niche', 0.5, 'chime')
    appear('dl_on', T_DOWN); ev(T_DOWN, 'down', 0.6, 'chime')
    appear('lamp_on', T_DOWN + 0.1)
    return tl


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    timeline().export(DUR, camera, lights, out)
