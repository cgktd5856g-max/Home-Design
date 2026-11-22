"""Kitchen room-build reel (Douyin / TikTok style), modelled on the white-and-wood L kitchen that
went viral on reposting accounts: wood base cabinets, white uppers, black quartz, marble backsplash,
cement floor tiles with flower inserts, window with blind at the end. Everything here is our own model.

    python3 ../../pipeline/run.py project.py <workdir> preview
    python3 ../../pipeline/run.py project.py <workdir> final --out ../../out/kitchen_build.mp4
    ROOM_REST=1 python3 ../../pipeline/run.py project.py <workdir> probe 0.5,1.5,2.5,3.5    # finished room, 4 camera stations

Units: metres. x = east, y = north (window wall), z = up. Room: x 0..W, y 0..D, z 0..H.
Camera stands in the doorway (y < 0) like the reference shot.
"""
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', '..', 'pipeline'))
import roomkit as rk
from roomkit import (srgb, mat, add, box, lathe, rprof, tube, ellipsoid, rbox, T, S, R, about, xform, wood, wood_mats,
                     rect_light, spot_rect)
from animkit import Timeline, c01, eoc, eob, smooth

REST = os.environ.get('ROOM_REST') == '1'                 # probe mode: finished room, camera station by time
REST_LIGHTS = os.environ.get('ROOM_LIGHTS', '1') == '1'

W, D, H = 2.10, 3.90, 2.65
FPS = 30
DUR = 4.0 if REST else 15.5

CT, CB, PL = 0.85, 0.81, 0.10            # countertop top, countertop bottom (= carcass top), plinth height
BD, UD = 0.60, 0.35                      # base depth (to door face), upper depth
UZ0, UZ1 = 1.50, 2.50                    # upper cabinets
BW, BZ = 0.30, 2.50                      # ceiling band width / bottom
WX0, WX1, WZ0, WZ1 = 0.475, 1.675, 1.05, 2.20     # window opening (far wall)
BLIND_Z = 1.46                           # blind bottom when lowered
SINK = (0.73, 1.42, 3.40, 3.80)          # countertop cut-out x0, x1, y0, y1
DL = [(1.05, 1.45), (1.05, 2.75)]        # downlights
PSH = [0.16, 0.56, 0.96, 1.36, 1.76, 2.16]   # pull-out pantry shelf heights
T_ON = 12.45                             # lights switch on
PO, PB = 12.80, 13.98                    # pull-out pantry: slides out / slides back
CAPTIONS = [(0.0, 2.6, 'Designing a small kitchen\nin 15 sec'), (14.0, 15.5, 'Comment the room\nyou want next')]


# ------------------------------------------------------------------------------------------- the scene
def materials():
    for name, ax in (('wtile_x', 0), ('wtile_y', 1)):
        mat(name, tex=12, col=srgb(238, 237, 233), col2=srgb(206, 204, 199), rough=0.16, f0=0.04, glossy=True, p=(0.60, 0.30, 0.0022, ax, 0.0))
    mat('ceiling', col=srgb(244, 244, 242))
    mat('subfloor', tex=3, col=srgb(146, 144, 140), p=(0.12,))
    mat('floortile', tex=13, col=srgb(236, 234, 229), col2=srgb(150, 104, 72), col3=srgb(142, 142, 145), rough=0.30, f0=0.04,
        glossy=True, p=(0.60, 0.085, 0.0016, 0.026))
    wood_mats('oakf', srgb(180, 137, 100), seed=2.0)
    wood_mats('birch', srgb(222, 200, 166), seed=7.0)
    mat('white_cab', col=srgb(239, 238, 235), rough=0.45)
    mat('white_in', col=srgb(229, 228, 225))
    mat('handle', col=srgb(22, 22, 24), rough=0.35, f0=0.04, glossy=True)
    mat('quartz', tex=15, col=srgb(24, 24, 26), col2=srgb(118, 118, 122), rough=0.10, f0=0.05, glossy=True, p=(700.0, 0.80))
    mat('marble', tex=11, col=srgb(243, 243, 241), col2=srgb(34, 34, 38), rough=0.10, f0=0.045, glossy=True, p=(2.1, 0.17, 5.0, 0.90))
    mat('plinth', col=srgb(70, 68, 66))
    mat('steel', tex=14, col=srgb(206, 207, 211), rough=0.26, metal=1, p=(2,))
    mat('steel_x', tex=14, col=srgb(206, 207, 211), rough=0.30, metal=1, p=(0,))
    mat('drain', col=srgb(60, 60, 64), rough=0.3, metal=1)
    mat('basin', col=srgb(176, 178, 182), rough=0.28, f0=0.07, glossy=True)
    mat('hob', col=srgb(12, 12, 14), rough=0.05, f0=0.05, glossy=True)
    mat('hob_ring', col=srgb(78, 78, 82))
    mat('enamel', col=srgb(242, 240, 235), rough=0.22, f0=0.04, glossy=True)
    mat('knob', tex=2, col=srgb(150, 106, 72), p=(2, 4.0))
    mat('hood', col=srgb(48, 48, 52), rough=0.22, f0=0.05, glossy=True)
    mat('winframe', col=srgb(66, 68, 72), rough=0.45)
    mat('sill', col=srgb(238, 238, 235), rough=0.2, f0=0.04, glossy=True)
    mat('blind', tex=4, col=srgb(238, 236, 230), emis=(0.30, 0.295, 0.28), p=(0.026,))
    mat('blindbar', col=srgb(222, 220, 214))
    mat('backdrop', tex=9, emis=(1.35, 1.35, 1.35), p=(1.0,))
    mat('led_off', col=srgb(226, 225, 221))
    mat('led', col=(0, 0, 0), emis=(7.5, 7.0, 6.0))
    mat('dl_emis', col=(0, 0, 0), emis=(9.0, 8.4, 7.3))
    mat('heater', col=srgb(243, 243, 241), rough=0.25, f0=0.04, glossy=True)
    mat('display', col=(0, 0, 0), emis=(0.25, 0.85, 1.4))
    mat('plate', col=srgb(245, 244, 240), rough=0.22, f0=0.04, glossy=True)
    mat('bowl_blue', col=srgb(112, 134, 156), rough=0.28, f0=0.04, glossy=True)
    mat('bowl_grey', col=srgb(170, 168, 162), rough=0.3, f0=0.04, glossy=True)
    mat('mug_sage', col=srgb(146, 166, 136), rough=0.3, f0=0.04, glossy=True)
    mat('mug_terra', col=srgb(192, 112, 82), rough=0.3, f0=0.04, glossy=True)
    mat('mug_cream', col=srgb(232, 222, 200), rough=0.3, f0=0.04, glossy=True)
    mat('jar', col=srgb(206, 212, 208), rough=0.08, f0=0.06, glossy=True)
    mat('jar_fill', col=srgb(214, 176, 120))
    mat('cork', tex=3, col=srgb(186, 148, 108), p=(0.18,))
    mat('tin', col=srgb(58, 58, 62), rough=0.35, f0=0.04, glossy=True)
    mat('tin_lid', col=srgb(196, 190, 180), rough=0.3, metal=1)
    mat('drawer_in', col=srgb(206, 206, 204))
    mat('bin', col=srgb(92, 94, 98), rough=0.4, f0=0.04, glossy=True)
    mat('bottle_b', col=srgb(64, 128, 192), rough=0.2, f0=0.05, glossy=True)
    mat('bottle_g', col=srgb(104, 170, 108), rough=0.2, f0=0.05, glossy=True)
    mat('cap_white', col=srgb(240, 240, 238))
    mat('leaf', col=srgb(66, 112, 58))
    mat('leaf2', col=srgb(92, 140, 70))
    mat('terra', col=srgb(196, 122, 88))
    mat('lemon', col=srgb(242, 202, 58), rough=0.4, f0=0.04, glossy=True)
    mat('apple', col=srgb(150, 186, 70), rough=0.35, f0=0.04, glossy=True)
    mat('rug', tex=7, col=srgb(216, 210, 198), col2=srgb(148, 144, 138), p=(1, 0.075))
    mat('board', tex=2, col=srgb(198, 152, 106), p=(2, 6.0))
    mat('soap', col=srgb(236, 234, 228), rough=0.25, f0=0.04, glossy=True)
    for nm, c in (('can_red', (186, 52, 40)), ('can_green', (58, 128, 72)), ('can_yel', (232, 182, 52)),
                  ('cer_a', (214, 70, 52)), ('cer_b', (240, 196, 70)), ('cer_c', (62, 118, 188)), ('tea', (52, 96, 70))):
        mat(nm, col=srgb(*c), rough=0.32, f0=0.04, glossy=True)
    mat('pasta', tex=3, col=srgb(232, 192, 96), p=(0.25,)); mat('beans', tex=3, col=srgb(118, 70, 42), p=(0.3,))
    mat('rice', tex=3, col=srgb(240, 237, 228), p=(0.15,)); mat('oil', col=srgb(206, 156, 52), rough=0.08, f0=0.06, glossy=True)
    mat('bag', tex=3, col=srgb(226, 214, 190), p=(0.12,))


def ring_disc(inst, c, r, z0, z1, m, n=28):
    add(inst, lathe(rprof(r, z0, z1, min(0.004, (z1 - z0) * 0.45), 3), n, c), m)


def build_room():
    r = 'room'
    add(r, box(-0.2, -1.2, -0.25, W + 0.2, D + 0.2, -0.012), 'subfloor')
    add(r, box(-0.2, -1.2, H, W + 0.2, D + 0.2, H + 0.1), 'ceiling')
    for b in (box(0, 0, BZ, W, BW, H), box(0, D - BW, BZ, W, D, H), box(0, BW, BZ, BW, D - BW, H), box(W - BW, BW, BZ, W, D - BW, H)):
        add(r, b, 'ceiling')
    add(r, box(-0.2, -1.2, -0.25, 0, D + 0.2, H + 0.1), 'wtile_x')
    add(r, box(W, -1.2, -0.25, W + 0.2, D + 0.2, H + 0.1), 'wtile_x')
    # south wall with the doorway the camera stands in
    add(r, box(0, -0.12, -0.25, 0.85, 0, H), 'wtile_y'); add(r, box(1.75, -0.12, -0.25, W, 0, H), 'wtile_y')
    add(r, box(0.85, -0.12, 2.10, 1.75, 0, H), 'wtile_y')
    add(r, box(-0.2, -1.4, -0.25, W + 0.2, -1.2, H + 0.1), 'wtile_y')
    # north wall with window
    add(r, box(0, D, -0.25, WX0, D + 0.2, H), 'wtile_y'); add(r, box(WX1, D, -0.25, W, D + 0.2, H), 'wtile_y')
    add(r, box(WX0, D, -0.25, WX1, D + 0.2, WZ0), 'wtile_y'); add(r, box(WX0, D, WZ1, WX1, D + 0.2, H), 'wtile_y')
    for b in (box(WX0, D, WZ0, WX0 + 0.006, D + 0.2, WZ1), box(WX1 - 0.006, D, WZ0, WX1, D + 0.2, WZ1), box(WX0, D, WZ1 - 0.006, WX1, D + 0.2, WZ1)):
        add(r, b, 'sill')
    add(r, box(WX0 - 0.03, D - 0.035, WZ0 - 0.02, WX1 + 0.03, D + 0.17, WZ0), 'sill')
    fy0, fy1 = D + 0.10, D + 0.14
    xm = (WX0 + WX1) / 2
    for b in (box(WX0, fy0, WZ0, WX0 + 0.045, fy1, WZ1), box(WX1 - 0.045, fy0, WZ0, WX1, fy1, WZ1), box(WX0, fy0, WZ1 - 0.045, WX1, fy1, WZ1),
              box(WX0, fy0, WZ0, WX1, fy1, WZ0 + 0.045), box(xm - 0.022, fy0, WZ0, xm + 0.022, fy1, WZ1)):
        add(r, b, 'winframe')
    add(r, box(-10, D + 4.0, -5, 14, D + 4.05, 9), 'backdrop')
    # cove LED strips (off) on the inner faces of the ceiling band, downlights (off)
    zs0, zs1 = BZ + 0.012, BZ + 0.032
    for b in (box(BW, BW, zs0, BW + 0.004, D - BW, zs1), box(W - BW - 0.004, BW, zs0, W - BW, D - BW, zs1),
              box(BW, BW, zs0, W - BW, BW + 0.004, zs1), box(BW, D - BW - 0.004, zs0, W - BW, D - BW, zs1)):
        add(r, b, 'led_off')
    for (x, y) in DL:
        add(r, lathe([(0.034, H - 0.002), (0.046, H - 0.002), (0.047, H - 0.010), (0.050, H - 0.012), (0.052, H)], 32, (x, y)), 'white_cab')
        ring_disc(r, (x, y), 0.036, H - 0.003, H - 0.0005, 'led_off')
    # floor tiles, one piece per row (they slap down row by row)
    edges = [-0.40, 0.60, 1.20, 1.80, 2.40, 3.00, 3.60, D + 0.01]
    for k in range(len(edges) - 1):
        add(f'floor{k}', box(0, edges[k], -0.012, W, edges[k + 1], 0.0), 'floortile')


def base_left(inst, y0, y1, fronts, handle='top'):
    """Base unit on the west wall, doors facing +x. fronts: list of (z0, z1, y0, y1) door/drawer panels."""
    add(inst, box(0.02, y0, PL, BD - 0.018, y1, CB), 'white_in')
    add(inst, box(0.02, y0, 0.0, BD - 0.05, y1, PL), 'plinth')
    for (z0, z1, a0, a1) in fronts:
        wood(inst, BD - 0.018, a0 + 0.0015, z0 + 0.0015, BD, a1 - 0.0015, z1 - 0.0015, 'oakf')
        yc = (a0 + a1) / 2
        zh = z1 - 0.045 if handle == 'top' else (z0 + z1) / 2
        add(inst, box(BD, yc - 0.065, zh - 0.006, BD + 0.012, yc + 0.065, zh + 0.006), 'handle')


def base_far(inst, x0, x1, fronts, open_front=False):
    """Base unit on the north wall, fronts facing -y at y = D - BD."""
    yf = D - BD
    if open_front:
        y1 = yf + 0.018
        add(inst, box(x0, y1, PL, x0 + 0.018, D - 0.02, CB - 0.02), 'white_in')
        add(inst, box(x1 - 0.018, y1, PL, x1, D - 0.02, CB - 0.02), 'white_in')
        add(inst, box(x0, y1, PL, x1, D - 0.02, PL + 0.018), 'white_in')
        add(inst, box(x0, D - 0.038, PL, x1, D - 0.02, CB - 0.02), 'white_in')
        add(inst, box(x0, y1, CB - 0.04, x1, y1 + 0.05, CB), 'white_in')
    else:
        add(inst, box(x0, yf + 0.018, PL, x1, D - 0.02, CB), 'white_in')
    add(inst, box(x0, yf + 0.05, 0.0, x1, D - 0.02, PL), 'plinth')
    for (z0, z1, a0, a1) in fronts:
        wood(inst, a0 + 0.0015, yf, z0 + 0.0015, a1 - 0.0015, yf + 0.018, z1 - 0.0015, 'oakf')
        xc = (a0 + a1) / 2
        add(inst, box(xc - 0.065, yf - 0.012, (z0 + z1) / 2 - 0.006, xc + 0.065, yf, (z0 + z1) / 2 + 0.006), 'handle')


def upper(inst, y0, y1):
    """Open upper carcass on the west wall (doors are separate pieces), one shelf."""
    t = 0.018
    add(inst, box(0.0, y0, UZ0, 0.012, y1, UZ1), 'white_in')
    add(inst, box(0.0, y0, UZ0, UD - t, y0 + t, UZ1), 'white_cab')
    add(inst, box(0.0, y1 - t, UZ0, UD - t, y1, UZ1), 'white_cab')
    add(inst, box(0.0, y0, UZ0, UD - t, y1, UZ0 + t), 'white_cab')
    add(inst, box(0.0, y0, UZ1 - t, UD - t, y1, UZ1), 'white_cab')
    add(inst, box(0.012, y0 + t, 2.00 - t / 2, UD - t - 0.01, y1 - t, 2.00 + t / 2), 'white_in')


def upper_door(inst, y0, y1):
    add(inst, box(UD - 0.018, y0 + 0.0015, UZ0 + 0.0015, UD, y1 - 0.0015, UZ1 - 0.0015), 'white_cab')
    add(inst, box(UD, y0 + 0.035, UZ0 + 0.04, UD + 0.012, y0 + 0.047, UZ0 + 0.20), 'handle')


def mug(inst, x, y, z, m, r=0.040, h=0.090):
    prof = [(0, z), (r - 0.006, z), (r, z + 0.006), (r, z + h), (r - 0.005, z + h), (r - 0.005, z + 0.012), (0, z + 0.012)]
    add(inst, lathe(prof, 24, (x, y)), m)
    arc = [(x + r - 0.002 + 0.028 * math.sin(a), y, z + h / 2 + 0.028 * math.cos(a)) for a in np.linspace(0.2, math.pi - 0.2, 9)]
    add(inst, tube(arc, 0.0055, 8), m)


def bowl(inst, x, y, z, r, h, m):
    prof = [(0, z), (r * 0.55, z), (r * 0.88, z + h * 0.35), (r, z + h), (r - 0.006, z + h), (r * 0.84, z + h * 0.38), (r * 0.5, z + 0.008), (0, z + 0.008)]
    add(inst, lathe(prof, 28, (x, y)), m)


def build_cabinets():
    # tall pull-out pantry: the carcass stays, the front and its shelves slide out into the room
    t = 0.018
    py0, py1 = 0.80, 1.40
    add('pantry', box(0.02, py0, PL, BD - t, py0 + t, UZ1), 'white_cab')
    add('pantry', box(0.02, py1 - t, PL, BD - t, py1, UZ1), 'white_cab')
    add('pantry', box(0.02, py0, PL, 0.038, py1, UZ1), 'white_in')
    add('pantry', box(0.02, py0, UZ1 - t, BD - t, py1, UZ1), 'white_cab')
    add('pantry', box(0.02, py0, PL, BD - t, py1, PL + t), 'white_in')
    add('pantry', box(0.02, py0, 0.0, BD - 0.05, py1, PL), 'plinth')
    add('pan_pull', box(BD - t, py0 + 0.0015, PL + 0.0015, BD, py1 - 0.0015, UZ1 - 0.0015), 'white_cab')
    add('pan_pull', box(BD, py0 + 0.045, 0.98, BD + 0.012, py0 + 0.057, 1.38), 'handle')
    add('pan_pull', box(0.06, py0 + 0.03, PL + t + 0.01, 0.075, py1 - 0.03, UZ1 - t - 0.01), 'white_in')
    for z in PSH:
        add('pan_pull', box(0.075, py0 + 0.03, z, BD - t, py1 - 0.03, z + 0.016), 'white_in')
        for yy in (py0 + 0.03, py1 - 0.036):
            add('pan_pull', box(0.075, yy, z + 0.05, BD - t, yy + 0.006, z + 0.058), 'steel_x')
    for x in (0.075, BD - t - 0.012):
        for yy in (py0 + 0.03, py1 - 0.042):
            add('pan_pull', box(x, yy, PL + t + 0.01, x + 0.012, yy + 0.012, UZ1 - t - 0.01), 'steel_x')
    # pantry contents, one piece per shelf (they fly in once the pantry is out)
    z = PSH[0] + 0.016
    for k, yy in enumerate((0.88, 0.99, 1.10)):
        add('pan_c0', lathe([(0, z), (0.042, z), (0.044, z + 0.24), (0.018, z + 0.30), (0.014, z + 0.33), (0, z + 0.33)], 20, (0.17, yy)), 'oil')
        add('pan_c0', lathe([(0, z + 0.33), (0.016, z + 0.33), (0.016, z + 0.36), (0, z + 0.36)], 12, (0.17, yy)), 'cap_white')
    add('pan_c0', rbox((0.42, 1.08, z + 0.15), (0.26, 0.30, 0.30), 0.05, 5), 'bag')
    add('pan_c0', rbox((0.42, 1.27, z + 0.12), (0.22, 0.12, 0.24), 0.04, 5), 'bag')
    z = PSH[1] + 0.016
    for i, xx in enumerate((0.16, 0.28, 0.40, 0.52)):
        for j, yy in enumerate((0.89, 1.00, 1.11, 1.25)):
            m = ('can_red', 'can_green', 'can_yel')[(i + j) % 3]
            add('pan_c1', lathe([(0, z), (0.037, z), (0.038, z + 0.11), (0, z + 0.11)], 18, (xx, yy)), m)
            add('pan_c1', lathe([(0, z + 0.11), (0.036, z + 0.11), (0.036, z + 0.116), (0, z + 0.116)], 18, (xx, yy)), 'steel')
    z = PSH[2] + 0.016
    for i, (xx, fill) in enumerate(((0.17, 'pasta'), (0.30, 'beans'), (0.43, 'rice'), (0.54, 'pasta'))):
        for yy in (0.92, 1.20):
            h = 0.22 if yy < 1.0 else 0.17
            add('pan_c2', lathe([(0, z), (0.055, z), (0.058, z + 0.01), (0.058, z + h), (0.05, z + h + 0.005), (0, z + h + 0.005)], 22, (xx, yy)), 'jar')
            add('pan_c2', lathe([(0, z + 0.01), (0.052, z + 0.01), (0.052, z + h * 0.8), (0, z + h * 0.8)], 18, (xx, yy)), fill)
            add('pan_c2', lathe(rprof(0.056, z + h + 0.004, z + h + 0.03, 0.006, 3), 22, (xx, yy)), 'cork')
    z = PSH[3] + 0.016
    for i, (xx, m) in enumerate(((0.16, 'cer_a'), (0.30, 'cer_b'), (0.44, 'cer_c'))):
        add('pan_c3', box(xx - 0.05, 0.85, z, xx + 0.05, 1.06, z + 0.30), m)
        add('pan_c3', box(xx - 0.05, 1.12, z, xx + 0.05, 1.33, z + 0.27), ('cer_c', 'cer_a', 'cer_b')[i])
    z = PSH[4] + 0.016
    for i, xx in enumerate((0.14, 0.24, 0.34, 0.44, 0.54)):
        for yy in (0.88, 0.98):
            add('pan_c4', lathe([(0, z), (0.03, z), (0.03, z + 0.10), (0, z + 0.10)], 16, (xx, yy)), 'jar')
            add('pan_c4', lathe([(0, z + 0.005), (0.027, z + 0.005), (0.027, z + 0.07), (0, z + 0.07)], 14, (xx, yy)), ('beans', 'pasta', 'can_red', 'tea', 'rice')[i])
            add('pan_c4', lathe([(0, z + 0.10), (0.031, z + 0.10), (0.031, z + 0.125), (0, z + 0.125)], 16, (xx, yy)), 'handle')
    add('pan_c4', box(0.10, 1.10, z, 0.30, 1.30, z + 0.14), 'tea')
    add('pan_c4', box(0.34, 1.10, z, 0.54, 1.30, z + 0.16), 'cer_b')
    # west base run
    yA, yB, yC, yD = 1.40, 2.00, 2.70, 3.30
    t = 0.018
    # L1: drawer unit, top drawer is its own piece
    add('L1', box(0.02, yA, PL, BD - t, yA + t, CB), 'white_in'); add('L1', box(0.02, yB - t, PL, BD - t, yB, CB), 'white_in')
    add('L1', box(0.02, yA, PL, 0.038, yB, CB), 'white_in'); add('L1', box(0.02, yA, PL, BD - t, yB, PL + t), 'white_in')
    add('L1', box(0.02, yA, CB - 0.02, BD - t, yB, CB), 'white_in'); add('L1', box(0.02, yA, 0.600, BD - t, yB, 0.618), 'white_in')
    add('L1', box(0.02, yA, 0.0, BD - 0.05, yB, PL), 'plinth')
    for (z0, z1) in ((PL, 0.355), (0.355, 0.62)):
        wood('L1', BD - t, yA + 0.0015, z0 + 0.0015, BD, yB - 0.0015, z1 - 0.0015, 'oakf')
        add('L1', box(BD, (yA + yB) / 2 - 0.065, (z0 + z1) / 2 - 0.006, BD + 0.012, (yA + yB) / 2 + 0.065, (z0 + z1) / 2 + 0.006), 'handle')
    # the top drawer
    z0, z1 = 0.62, CB
    wood('L1_dr', BD - t, yA + 0.0015, z0 + 0.0015, BD, yB - 0.0015, z1 - 0.0015, 'oakf')
    add('L1_dr', box(BD, 1.635, 0.709, BD + 0.012, 1.765, 0.721), 'handle')
    add('L1_dr', box(0.07, 1.43, 0.635, BD - t, 1.97, 0.645), 'drawer_in')
    add('L1_dr', box(0.07, 1.43, 0.645, BD - t, 1.442, 0.775), 'drawer_in'); add('L1_dr', box(0.07, 1.958, 0.645, BD - t, 1.97, 0.775), 'drawer_in')
    add('L1_dr', box(0.07, 1.442, 0.645, 0.082, 1.958, 0.775), 'drawer_in')
    # cutlery organiser + cutlery (ride in the drawer)
    tz = 0.645
    add('L1_tray', box(0.10, 1.455, tz, 0.56, 1.945, tz + 0.006), 'birch_y')
    for b in (box(0.10, 1.455, tz, 0.56, 1.463, tz + 0.045), box(0.10, 1.937, tz, 0.56, 1.945, tz + 0.045),
              box(0.10, 1.455, tz, 0.108, 1.945, tz + 0.045), box(0.552, 1.455, tz, 0.56, 1.945, tz + 0.045)):
        add('L1_tray', b, 'birch_x')
    for yy in (1.575, 1.70, 1.825):
        add('L1_tray', box(0.108, yy - 0.004, tz, 0.552, yy + 0.004, tz + 0.04), 'birch_x')
    zc = tz + 0.012
    for k, yy in enumerate((1.495, 1.52, 1.545, 1.615, 1.64, 1.665, 1.74, 1.765, 1.79, 1.865, 1.90)):
        add('L1_cut', tube([(0.16, yy, zc), (0.40, yy, zc + 0.004)], 0.0042, 8), 'steel_x')
        if k < 3:      # forks: flat head
            add('L1_cut', box(0.40, yy - 0.011, zc, 0.47, yy + 0.011, zc + 0.004), 'steel_x')
        elif k < 6:    # spoons
            add('L1_cut', ellipsoid((0.44, yy, zc + 0.006), (0.036, 0.017, 0.006), 8), 'steel_x')
        elif k < 9:    # knives
            add('L1_cut', box(0.40, yy - 0.008, zc, 0.50, yy + 0.008, zc + 0.003), 'steel_x')
        else:          # ladle / spatula
            add('L1_cut', ellipsoid((0.47, yy, zc + 0.01), (0.04, 0.026, 0.01), 8), 'steel_x')
    # L2 hob unit (2 doors), L3 (1 door), corner box
    base_left('L2', yB, yC, [(PL, CB, yB, (yB + yC) / 2), (PL, CB, (yB + yC) / 2, yC)])
    base_left('L3', yC, yD, [(PL, CB, yC, yD)])
    wood('LC', 0.02, yD, PL, 0.65, D - 0.02, CB, 'oakf')
    add('LC', box(0.02, yD, 0.0, 0.60, D - 0.02, PL), 'plinth')
    # north run: sink unit F1 (open, doors separate), drawer unit F2
    base_far('F1', 0.65, 1.50, [], open_front=True)
    yf = D - BD
    xm = (0.65 + 1.50) / 2
    wood('F1_dl', 0.6515, yf, PL + 0.0015, xm - 0.0015, yf + t, CB - 0.0015, 'oakf')
    add('F1_dl', box(xm - 0.135, yf - 0.012, CB - 0.051, xm - 0.035, yf, CB - 0.039), 'handle')
    wood('F1_dr', xm + 0.0015, yf, PL + 0.0015, 1.4985, yf + t, CB - 0.0015, 'oakf')
    add('F1_dr', box(xm + 0.035, yf - 0.012, CB - 0.051, xm + 0.135, yf, CB - 0.039), 'handle')
    base_far('F2', 1.50, W, [(0.62, CB, 1.50, W), (0.355, 0.62, 1.50, W), (PL, 0.355, 1.50, W)])
    # F1 contents
    add('F1_bin', lathe([(0, PL + 0.018), (0.11, PL + 0.018), (0.12, PL + 0.32), (0.125, PL + 0.335), (0, PL + 0.34)], 28, (0.86, 3.62)), 'bin')
    add('F1_bot', lathe([(0, PL + 0.018), (0.04, PL + 0.018), (0.042, PL + 0.20), (0.02, PL + 0.26), (0.015, PL + 0.29), (0, PL + 0.29)], 20, (1.24, 3.56)), 'bottle_b')
    add('F1_bot', lathe([(0, PL + 0.29), (0.017, PL + 0.29), (0.017, PL + 0.32), (0, PL + 0.32)], 12, (1.24, 3.56)), 'cap_white')
    add('F1_bot', lathe([(0, PL + 0.018), (0.035, PL + 0.018), (0.037, PL + 0.17), (0.018, PL + 0.22), (0.013, PL + 0.25), (0, PL + 0.25)], 20, (1.34, 3.64)), 'bottle_g')
    add('F1_bot', lathe([(0, PL + 0.25), (0.015, PL + 0.25), (0.015, PL + 0.28), (0, PL + 0.28)], 12, (1.34, 3.64)), 'cap_white')
    # countertops (black quartz), sink cut-out in the north run
    add('CL', box(0.0, yA, CB, BD + 0.02, D, CT), 'quartz')
    sx0, sx1, sy0, sy1 = SINK
    for b in (box(BD + 0.02, yf - 0.02, CB, sx0, D, CT), box(sx1, yf - 0.02, CB, W, D, CT), box(sx0, yf - 0.02, CB, sx1, sy0, CT), box(sx0, sy1, CB, sx1, D, CT)):
        add('CF', b, 'quartz')
    # marble backsplash on the west wall
    add('splash', box(0.0, yA, CT, 0.012, yD, UZ0), 'marble')
    # upper cabinets + doors + contents
    upper('U1', yA, yB); upper('U2', yB, yC); upper('U3', yC, yD)
    upper_door('U1_door', yA, yB); upper_door('U2_door', yB, yC); upper_door('U3_door', yC, yD)
    for k in range(7):
        z = UZ0 + 0.018 + k * 0.0145
        add('U1_plt', lathe(rprof(0.115, z, z + 0.013, 0.0055, 3), 32, (0.17, 1.70)), 'plate')
    for k in range(3):
        bowl('U1_bwl', 0.17, 1.60, 2.009 + k * 0.022, 0.075, 0.06, 'bowl_blue')
        bowl('U1_bwl', 0.17, 1.80, 2.009 + k * 0.022, 0.075, 0.06, 'plate')
    for k, (yy, m) in enumerate(((2.12, 'mug_sage'), (2.26, 'mug_terra'), (2.40, 'mug_cream'), (2.54, 'mug_sage'))):
        mug('U2_mug', 0.16, yy, UZ0 + 0.018, m)
    for k, yy in enumerate((2.13, 2.30, 2.47)):
        h = 0.16 - 0.02 * k
        add('U2_jar', lathe([(0, 2.009), (0.05, 2.009), (0.055, 2.02), (0.055, 2.009 + h), (0.05, 2.012 + h), (0, 2.012 + h)], 24, (0.17, yy)), 'jar')
        add('U2_jar', lathe([(0, 2.02), (0.049, 2.02), (0.049, 2.009 + h * 0.62), (0, 2.009 + h * 0.62)], 20, (0.17, yy)), 'jar_fill')
        add('U2_jar', lathe(rprof(0.053, 2.012 + h, 2.04 + h, 0.006, 3), 24, (0.17, yy)), 'cork')
    for k, yy in enumerate((2.83, 2.98, 3.13)):
        add('U3_tin', lathe([(0, UZ0 + 0.018), (0.055, UZ0 + 0.018), (0.055, UZ0 + 0.17), (0, UZ0 + 0.17)], 24, (0.17, yy)), 'tin')
        add('U3_tin', lathe(rprof(0.057, UZ0 + 0.17, UZ0 + 0.195, 0.005, 3), 24, (0.17, yy)), 'tin_lid')
    for k in range(4):
        bowl('U3_bwl', 0.17, 2.90, 2.009 + k * 0.02, 0.08, 0.055, 'bowl_grey')
        bowl('U3_bwl', 0.17, 3.10, 2.009 + k * 0.02, 0.07, 0.05, 'plate')
    # slim hood under U2
    add('hood', box(0.012, 2.06, 1.415, 0.40, 2.64, UZ0), 'hood')
    add('hood', box(0.40, 2.06, 1.415, 0.406, 2.64, UZ0 - 0.012), 'steel_x')
    # hob + pots
    add('hob', box(0.07, 2.05, CT, 0.53, 2.65, CT + 0.007), 'hob')
    for (y, rr) in ((2.20, 0.10), (2.50, 0.09)):
        add('hob', lathe([(rr - 0.004, CT + 0.0072), (rr, CT + 0.0072), (rr, CT + 0.0078), (rr - 0.004, CT + 0.0078)], 40, (0.30, y)), 'hob_ring')
    for name, (y, rr, hh) in (('pot1', (2.20, 0.105, 0.115)), ('pot2', (2.50, 0.092, 0.095))):
        z0 = CT + 0.007
        prof = [(0, z0), (rr - 0.008, z0), (rr, z0 + 0.008), (rr, z0 + hh), (rr + 0.004, z0 + hh + 0.004), (rr - 0.002, z0 + hh + 0.008),
                (rr * 0.75, z0 + hh + 0.022), (rr * 0.3, z0 + hh + 0.03), (0, z0 + hh + 0.031)]
        add(name, lathe(prof, 36, (0.30, y)), 'enamel')
        add(name, lathe(rprof(0.016, z0 + hh + 0.03, z0 + hh + 0.05, 0.007, 3), 16, (0.30, y)), 'knob')
        for sg in (-1, 1):
            arc = [(0.30 + 0.014 * math.cos(a) * 0 + 0.0, y + sg * (rr + 0.012 * math.sin(a)), z0 + hh * 0.78 + 0.016 * math.cos(a)) for a in np.linspace(0.3, math.pi - 0.3, 7)]
            add(name, tube(arc, 0.006, 8), 'enamel')
    # sink basin (undermount), faucet, soap
    bx0, bx1, by0, by1 = sx0 + 0.015, sx1 - 0.015, sy0 + 0.015, sy1 - 0.015
    zb = 0.62
    for b in (box(bx0, by0, zb, bx1, by1, zb + 0.01), box(bx0, by0, zb, bx0 + 0.01, by1, CB), box(bx1 - 0.01, by0, zb, bx1, by1, CB),
              box(bx0, by0, zb, bx1, by0 + 0.01, CB), box(bx0, by1 - 0.01, zb, bx1, by1, CB), box(sx0 - 0.01, sy0 - 0.01, CB - 0.004, sx0, sy1 + 0.01, CB),
              box(sx1, sy0 - 0.01, CB - 0.004, sx1 + 0.01, sy1 + 0.01, CB)):
        add('sink', b, 'basin')
    add('sink', lathe(rprof(0.034, zb + 0.010, zb + 0.013, 0.002, 2), 24, ((bx0 + bx1) / 2, (by0 + by1) / 2)), 'drain')
    fx, fyy = (sx0 + sx1) / 2, 3.835
    add('faucet', lathe(rprof(0.026, CT, CT + 0.035, 0.006, 3), 24, (fx, fyy)), 'steel')
    neck = [(fx, fyy, CT + 0.03), (fx, fyy, CT + 0.22)]
    for a in np.linspace(0, math.pi, 13)[1:]:
        neck.append((fx, fyy - 0.085 + 0.085 * math.cos(a), CT + 0.22 + 0.085 * math.sin(a)))
    neck.append((fx, fyy - 0.17, CT + 0.17))
    add('faucet', tube(neck, 0.011, 12), 'steel')
    add('faucet', tube([(fx, fyy, CT + 0.12), (fx + 0.06, fyy, CT + 0.12)], 0.006, 8), 'steel')
    add('soap', lathe([(0, CT), (0.03, CT), (0.032, CT + 0.11), (0.012, CT + 0.13), (0, CT + 0.13)], 20, (1.52, 3.80)), 'soap')
    add('soap', tube([(1.52, 3.80, CT + 0.13), (1.52, 3.80, CT + 0.155), (1.52, 3.775, CT + 0.155)], 0.004, 8), 'handle')
    # blind (unrolls down from the top of the window)
    add('blind', box(WX0 + 0.01, D + 0.028, BLIND_Z, WX1 - 0.01, D + 0.038, WZ1 - 0.01), 'blind')
    add('blind', box(WX0 + 0.012, D + 0.024, BLIND_Z - 0.022, WX1 - 0.012, D + 0.042, BLIND_Z), 'blindbar')
    # water heater on the east wall
    add('heater', rbox((1.99, 3.575, 2.07), (0.22, 0.44, 0.64), 0.05, 5), 'heater')
    add('heater', box(1.876, 3.53, 2.14, 1.882, 3.62, 2.18), 'display')
    for yy in (3.50, 3.65):
        add('heater', tube([(2.04, yy, 1.76), (2.04, yy, CT)], 0.009, 8), 'steel')
    # sill plant and herb pot
    add('plant', lathe([(0, WZ0), (0.042, WZ0), (0.05, WZ0 + 0.085), (0.054, WZ0 + 0.09), (0, WZ0 + 0.09)], 20, (1.42, 3.935)), 'terra')
    rng = np.random.default_rng(3)
    for k in range(9):
        a = 2 * math.pi * k / 9 + rng.uniform(-0.2, 0.2)
        lean = rng.uniform(0.35, 0.8)
        L = rng.uniform(0.09, 0.14)
        c = np.array([1.42 + math.cos(a) * L * 0.45 * lean, 3.935 + math.sin(a) * L * 0.25 * lean, WZ0 + 0.09 + L * 0.6])
        add('plant', xform(ellipsoid(c, (0.018, 0.018, L * 0.55), 8), about(c, R('z', a) @ R('x', lean * 0.6))), 'leaf' if k % 2 else 'leaf2')
    add('herb', lathe([(0, CT), (0.05, CT), (0.058, CT + 0.11), (0, CT + 0.11)], 20, (1.90, 3.68)), 'cap_white')
    for k in range(11):
        a = 2 * math.pi * k / 11 + rng.uniform(-0.2, 0.2)
        rr = rng.uniform(0.0, 0.035)
        c = np.array([1.90 + math.cos(a) * rr, 3.68 + math.sin(a) * rr, CT + 0.15 + rng.uniform(0, 0.06)])
        add('herb', ellipsoid(c, (0.03, 0.03, 0.02), 7), 'leaf2' if k % 3 else 'leaf')
    # final-shot decor: runner rug, fruit bowl, cutting board
    add('rug', box(0.80, 1.15, 0.0, 1.42, 2.95, 0.009), 'rug')
    bowl('fruit', 0.30, 1.62, CT, 0.13, 0.06, 'plate')
    for (dx, dy, m) in ((-0.04, -0.03, 'lemon'), (0.04, -0.02, 'lemon'), (0.0, 0.045, 'apple'), (0.05, 0.05, 'lemon')):
        add('fruit', ellipsoid((0.30 + dx, 1.62 + dy, CT + 0.045), (0.034, 0.034, 0.03), 10), m)
    cb = np.array([0.08, 3.05, CT + 0.215])
    add('board', xform(rbox(cb, (0.018, 0.30, 0.42), 0.008, 3), about(cb, R('y', math.radians(-10)))), 'board')
    # lights-on: everything that glows once the lights switch on
    zs0, zs1 = BZ + 0.011, BZ + 0.033
    for b in (box(BW + 0.004, BW, zs0, BW + 0.006, D - BW, zs1), box(W - BW - 0.006, BW, zs0, W - BW - 0.004, D - BW, zs1),
              box(BW, BW + 0.004, zs0, W - BW, BW + 0.006, zs1), box(BW, D - BW - 0.006, zs0, W - BW, D - BW - 0.004, zs1)):
        add('led_on', b, 'led')
    add('led_on', box(0.28, yA + 0.02, UZ0 - 0.006, 0.31, yD - 0.02, UZ0 - 0.001), 'led')
    for (x, y) in DL:
        ring_disc('led_on', (x, y), 0.037, H - 0.005, H - 0.0035, 'dl_emis')


def build():
    materials()
    build_room()
    build_cabinets()


# ------------------------------------------------------------------------------------------- camera
VFOV = 85.0
STA = dict(pos=(1.25, -0.15, 1.25), yaw=-10.0, pitch=0.0)       # doorway, whole kitchen
STB = dict(pos=(1.86, 1.12, 1.20), yaw=-56.0, pitch=3.0)       # west wall: hob, uppers, drawer
STC = dict(pos=(1.20, 2.00, 1.20), yaw=6.0, pitch=2.0)         # north wall: sink, window, heater
STD = dict(pos=(1.30, -0.22, 1.40), yaw=-9.0, pitch=-1.5)      # final wide
SHOTS = [(0.0, STA), (3.00, None), (3.30, STB), (7.50, None), (7.80, STC), (10.70, None), (11.40, STD)]


def lerp_cam(a, b, s, lift=2.0):
    pa, pb = np.array(a['pos']), np.array(b['pos'])
    return dict(pos=tuple(pa + (pb - pa) * s), yaw=a['yaw'] + (b['yaw'] - a['yaw']) * s,
                pitch=a['pitch'] + (b['pitch'] - a['pitch']) * s + lift * math.sin(math.pi * s), vfov=VFOV)


def camera(t):
    if REST:
        return dict([STA, STB, STC, STD][min(3, int(t))], vfov=VFOV)
    for i in range(0, len(SHOTS) - 1, 2):
        t0, st = SHOTS[i]
        t1 = SHOTS[i + 1][0]
        if t < t1:
            return dict(st, vfov=VFOV)
        t2, nxt = SHOTS[i + 2]
        if t < t2:
            u = (t - t1) / (t2 - t1)
            if i + 2 == len(SHOTS) - 1:          # final pull-back: fast start, long settle
                s = 1 - (1 - c01(u)) ** 3
                return lerp_cam(st, nxt, s, lift=3.0)
            return lerp_cam(st, nxt, smooth(u))
    return dict(SHOTS[-1][1], vfov=VFOV)


# ------------------------------------------------------------------------------------------- lights
LSKY = (11.0, 11.6, 12.6)
LBLIND = (5.4, 5.3, 5.0)
LDOOR = (2.6, 2.5, 2.35)            # soft fill from the room behind the camera
LBOUNCE = (1.3, 1.28, 1.24)         # bounce off the bright east wall (lights the open cabinets)
LCOVE = (20.0, 18.2, 15.2)
LUNDER = (34.0, 31.0, 26.0)
LDOWN = (1300.0, 1200.0, 1020.0)


def lights(mats4, vis):
    """Fixed slots (a light that is off has zero radiance) so a light keeps its index across frames (Blender)."""
    Ls = []
    top = WZ1 - 0.01
    if vis.get('blind'):
        top = float((mats4['blind'] @ np.array([1.0, D + 0.03, BLIND_Z - 0.022, 1.0]))[2])
        top = min(max(top, WZ0 + 0.02), WZ1 - 0.01)
    off = (0.0, 0.0, 0.0)
    # 0 sky through the open part of the window (below the blind): shines toward -y
    Ls.append(rect_light((WX0, D + 0.16, WZ0), (WX1 - WX0, 0, 0), (0, 0, top - WZ0), LSKY, always=1))
    Ls.append(rect_light((0.85, -0.11, 0.0), (0, 0, 2.10), (0.90, 0, 0), LDOOR, always=1))        # 1 faces +y
    Ls.append(rect_light((W - 0.01, 0.6, 0.9), (0, 0, 1.5), (0, 2.7, 0), LBOUNCE))                 # 2 faces -x
    blind_on = bool(vis.get('blind')) and top < WZ1 - 0.03
    Ls.append(rect_light((WX0 + 0.01, D + 0.024, top), (WX1 - WX0 - 0.02, 0, 0), (0, 0, max(WZ1 - 0.01 - top, 0.002)),
                         LBLIND if blind_on else off))                                              # 3 glow through the blind
    led = bool(vis.get('led_on'))
    z0, h = BZ + 0.011, 0.022
    L1, L2 = D - 2 * BW, W - 2 * BW
    lc, lu, ld = (LCOVE, LUNDER, LDOWN) if led else (off, off, off)
    Ls.append(rect_light((BW + 0.007, BW, z0), (0, L1, 0), (0, 0, h), lc))                          # 4-7 cove strips
    Ls.append(rect_light((W - BW - 0.007, BW, z0), (0, 0, h), (0, L1, 0), lc))
    Ls.append(rect_light((BW, BW + 0.007, z0), (0, 0, h), (L2, 0, 0), lc))
    Ls.append(rect_light((BW, D - BW - 0.007, z0), (L2, 0, 0), (0, 0, h), lc))
    Ls.append(rect_light((0.28, 1.42, UZ0 - 0.007), (0, 1.86, 0), (0.03, 0, 0), lu))                # 8 under-cabinet strip
    for (x, y) in DL:                                                                               # 9-10 downlights
        Ls.append(spot_rect((x, y, H - 0.006), (0, 0, -1), 0.05, ld, 4.0))
    return Ls


# Blender (Cycles) look: see pipeline/blender_render.py
BLENDER = dict(
    exposure=-0.35,
    look='AgX - Medium High Contrast',
    sun=dict(dir=(0.12, -0.80, -0.58), strength=26.0, color=(1.0, 0.93, 0.82), angle=1.0),
    glass=['jar'],
    bevel={'oakf_x': 0.004, 'oakf_y': 0.004, 'oakf_z': 0.004, 'white_cab': 0.003, 'quartz': 0.003, 'hood': 0.003,
           'handle': 0.002, 'heater': 0.004, 'sill': 0.003, 'white_in': 0.002, 'birch_x': 0.002, 'birch_y': 0.002},
    separate=['backdrop'],                 # own object: seen through the window, casts no shadow, lights nothing
    fill_lights=[1, 2],                    # fake fill: not visible in reflections
    wood_scale=(55.0, 1.6),                # grain: across, along
    bake_rect={'backdrop': (-6.0, 8.0, -3.0, 6.0)},
    bake_px={'backdrop': 0.006, 'floortile': 0.0012, 'marble': 0.0008},
)


# ------------------------------------------------------------------------------------------- timeline
def timeline():
    tl = Timeline(rk, FPS)
    I = np.eye(4)
    if REST:
        if not REST_LIGHTS:
            tl.custom('led_on', lambda t: (I, False))
        return tl
    cen, ev = tl.cen, tl.ev
    drop, fly, slide, grow, from_camera = tl.drop, tl.fly, tl.slide, tl.grow, tl.from_camera
    camB = np.array(STB['pos'])

    # ---------------- shot A (doorway): tiles slap down far to near, base run extrudes from the walls
    for k in range(7):
        t1 = 0.30 + 0.065 * (6 - k)
        drop(f'floor{k}', t1 - 0.16, t1, 0.24, 0.05, 0.30 + 0.03 * k, 'tick')
    sL1 = slide('L1', 0.78, 0.98, (-0.64, 0, 0), 1.0, 0.75)
    slide('L2', 0.88, 1.08, (-0.64, 0, 0), 1.0, 0.75)
    slide('L3', 0.98, 1.18, (-0.64, 0, 0), 1.0, 0.75)
    slide('LC', 1.04, 1.24, (-0.66, 0, 0), 1.0, 0.4)
    slide('F1', 1.12, 1.32, (0, 0.64, 0), 1.0, 0.75)
    slide('F2', 1.22, 1.42, (0, 0.64, 0), 1.0, 0.75)
    drop('CL', 1.50, 1.70, 0.55, 0.03, 1.0, 'thud')
    drop('CF', 1.62, 1.82, 0.55, 0.03, 0.9, 'thud')
    sPan = grow('pantry', 1.92, 2.18, 'z', (0, 0, 0), 0.9)
    slide('heater', 2.26, 2.44, (0.30, 0, 0), 1.0, 0.5)
    grow('splash', 2.48, 2.72, 'y', (0, 1.40, 0), 0.6)

    # sink unit doors: appear open right after the unit lands, slam shut in shot C
    yf = D - BD

    def door(name, hinge, a_open, t_in, t_in1, t_close, dur=0.17, drop_h=0.14):
        hinge = np.array(hinge, float)

        def f(t):
            if t < t_in:
                return I, False
            if t < t_in1:
                u = (t - t_in) / (t_in1 - t_in)
                s = 1.2 - 0.2 * eoc(u)
                return T(0, 0, drop_h * (1 - eoc(u))) @ about(hinge, R('z', a_open) @ S(s, s, s)), True
            if t < t_close:
                return about(hinge, R('z', a_open)), True
            u = (t - t_close) / dur
            if u < 1:
                return about(hinge, R('z', a_open * (1 - u * u))), True
            tau = t - t_close - dur
            a = math.copysign(math.radians(2.5), a_open) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))
            return about(hinge, R('z', a)), True
        tl.custom(name, f)
        ev(t_in1, name, 0.3, 'tick')
        ev(t_close + dur, name + '_shut', 0.75, 'thud')
    door('F1_dl', (0.65, yf, 0.45), math.radians(-88), 1.36, 1.50, 8.92)
    door('F1_dr', (1.50, yf, 0.45), math.radians(88), 1.40, 1.54, 8.98)

    # ---------------- shot B (west wall): uppers, hood, hob, pots, drawer moment, contents, doors
    from_camera('U1', 3.38, 3.64, camB, 0.42, 0.85)
    from_camera('U2', 3.50, 3.76, camB, 0.42, 0.85)
    from_camera('U3', 3.62, 3.88, camB, 0.42, 0.85)
    fly('hood', 3.96, 4.16, (0.45, 0, -0.22), 0.04, 0.6)
    drop('hob', 4.22, 4.38, 0.30, 0.02, 0.55, 'thud')
    drop('pot1', 4.44, 4.60, 0.34, 0.06, 0.45)
    drop('pot2', 4.52, 4.68, 0.34, 0.06, 0.45)
    D_OPEN = 0.40

    def drawer(t):
        if t < 0.78:
            return I, False
        if t < 4.80:
            return sL1(t)[0], True
        if t < 5.42:
            k = eob((t - 4.80) / 0.10, 1.6)
            return T(D_OPEN * k, 0, 0), True
        k = 1 - smooth((t - 5.42) / 0.17)
        x = D_OPEN * k
        if t > 5.59:
            x += 0.006 * math.exp(-(t - 5.59) / 0.05) * math.sin(2 * math.pi * (t - 5.59) / 0.12)
        return T(x, 0, 0), True
    tl.custom('L1_dr', drawer)
    ev(4.88, 'drawer_open', 0.6, 'swish')
    ev(5.59, 'drawer_close', 0.85, 'thud')
    drop('L1_tray', 4.96, 5.12, 0.40, 0.04, 0.40, parent=drawer)
    drop('L1_cut', 5.08, 5.24, 0.40, 0.05, 0.40, parent=drawer)
    for k, name in enumerate(('U1_plt', 'U1_bwl', 'U2_mug', 'U2_jar', 'U3_tin', 'U3_bwl')):
        from_camera(name, 5.66 + 0.08 * k, 5.84 + 0.08 * k, camB, 0.30, 0.35, 'tick')
    door('U1_door', (UD, 2.00, 2.0), math.radians(90), 6.30, 6.48, 6.78)
    door('U2_door', (UD, 2.70, 2.0), math.radians(90), 6.37, 6.55, 6.85)
    door('U3_door', (UD, 3.30, 2.0), math.radians(90), 6.44, 6.62, 6.92)

    # ---------------- shot C (north wall): sink, faucet, soap, under-sink contents, doors shut, blind, plants
    drop('sink', 7.90, 8.08, 0.42, 0.02, 0.75, 'thud')
    drop('faucet', 8.14, 8.30, 0.30, 0.05, 0.55)
    drop('soap', 8.30, 8.44, 0.25, 0.06, 0.35)
    fly('F1_bin', 8.46, 8.64, (0, -0.55, 0.10), 0.05, 0.4, 'tick')
    fly('F1_bot', 8.56, 8.74, (0, -0.55, 0.12), 0.05, 0.35, 'tick')
    grow('blind', 9.30, 9.74, 'z', (0, 0, WZ1 - 0.01), 0.55)
    ev(9.32, 'blind_go', 0.45, 'swish')
    drop('plant', 9.86, 10.02, 0.25, 0.06, 0.35)
    drop('herb', 10.04, 10.20, 0.25, 0.06, 0.35)

    # ---------------- shot D (final wide): rug, decor, lights on, hold
    grow('rug', 11.50, 11.78, 'y', (0, 2.95, 0), 0.5)
    drop('fruit', 11.92, 12.08, 0.30, 0.06, 0.4)
    drop('board', 12.04, 12.20, 0.30, 0.04, 0.4)
    tl.custom('led_on', lambda t: (I, t >= T_ON))
    ev(T_ON, 'lights', 0.9, 'chime')

    # finale: the tall cabinet is a hidden pull-out pantry
    OUT = 0.50

    def pull(t):
        if t < 1.92:
            return I, False
        if t < PO:
            return sPan(t)[0], True
        if t < PB:
            return T(OUT * eob((t - PO) / 0.24, 1.2), 0, 0), True
        x = OUT * (1 - smooth((t - PB) / 0.22))
        tau = t - PB - 0.22
        if tau > 0:
            x += 0.008 * math.exp(-tau / 0.05) * math.sin(2 * math.pi * tau / 0.12)
        return T(x, 0, 0), True
    tl.custom('pan_pull', pull)
    ev(PO + 0.14, 'pantry_out', 0.7, 'swish')
    ev(PB + 0.22, 'pantry_in', 1.0, 'thud')
    camD = np.array(STD['pos'])

    def fill(name, t0, t1):
        piv = np.array([*cen[name], 1.0])

        def f(t):
            if t < t0:
                return I, False
            Mp = pull(t)[0]
            pc = (Mp @ piv)[:3]
            if t < t1:
                u = (t - t0) / (t1 - t0)
                off = (1 - eoc(u)) * 0.28 * (camD - pc)
                s = 0.45 + 0.55 * smooth(u / 0.3)
                return T(*off) @ about(pc, S(s, s, s)) @ Mp, True
            s = tl.settle(t - t1, 0.015)
            return about(pc, S(s, s, s)) @ Mp, True
        tl.custom(name, f)
        ev(t1, name, 0.35, 'tick')
    for k in range(5):
        fill(f'pan_c{k}', 13.10 + 0.09 * k, 13.28 + 0.09 * k)
    return tl


if __name__ == '__main__':
    out = sys.argv[1] if len(sys.argv) > 1 else '.'
    os.makedirs(out, exist_ok=True)
    build()
    rk.write_scene(os.path.join(out, 'scene.bin'))
    timeline().export(DUR, camera, lights, out)
