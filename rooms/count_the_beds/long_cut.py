"""Long cut (46 s, evergreen) of Count the Beds: the same room and helpers as project.py, its own camera and timeline.
Selected with ROOM_CUT=long. Seven zones of 6-7 s, two gliding angles each, the wow (the double rolling out) at 28-30 s.
"""
import math

import numpy as np

from roomkit import T, R, about
from animkit import c01, eob, smooth
import figure as fg


def P(x, y, z, yaw, pitch):
    return dict(pos=(x, y, z), yaw=yaw, pitch=pitch)


F1 = P(0.05, 0.47, 1.30, 42.0, -9.0)
A1 = (F1, P(0.70, 0.40, 1.30, 74.0, -8.0))                                        # doorway dolly
A2 = (P(1.30, 0.70, 1.10, 82.0, 10.0), P(1.55, 1.55, 1.05, 44.0, 6.0))            # low slide north along the podium face
B1 = (P(0.95, 0.50, 1.10, 108.0, -2.0), P(1.55, 0.30, 1.00, 76.0, -8.0))          # push in on the stair
B2 = (P(2.05, 0.65, 1.15, 34.0, -4.0), P(2.18, 0.85, 2.05, 4.0, -24.0))           # crane up beside the porch
C1 = (P(2.08, 0.32, 1.55, -98.0, 17.0), P(1.86, 0.70, 1.55, -62.0, 13.0))         # west wall, slide north + pan
C2 = (P(1.75, 0.90, 1.50, -78.0, 12.0), P(1.35, 1.50, 1.52, -44.0, 16.0))         # desk + guest cabinet
D1 = (P(1.70, 1.60, 1.55, -48.0, 14.0), P(1.55, 0.95, 1.50, -84.0, 12.0))         # the bags fly in; the desk folds
D2 = (P(1.20, 1.10, 1.30, 112.0, -22.0), P(1.00, 1.85, 1.20, 84.0, -18.0))        # cutaway + futon from the open floor
E1 = (P(0.16, 0.12, 0.70, 62.0, 0.0), P(0.42, 0.34, 0.72, 42.0, -3.0))            # the double rolls at the lens
E2 = (P(2.30, 0.75, 1.60, -58.0, -12.0), P(2.10, 1.20, 1.60, -84.0, -8.0))       # orbit above the beds' heads
F1s = (P(0.20, 0.25, 1.15, 62.0, -12.0), P(0.35, 0.55, 1.15, 84.0, -12.0))       # side view along the double's foot
F2 = (P(0.55, 0.14, 2.08, 40.0, -30.0), P(0.70, 0.24, 2.00, 68.0, -28.0))         # high from the doorway corner
G1 = (P(0.80, 0.25, 1.35, 72.0, -12.0), P(0.10, 0.18, 1.80, 46.0, -21.0))         # rising orbit, ends near the door
G2 = (P(-0.42, 0.47, 1.40, 80.0, -10.0), F1)                                       # through the door, back to frame 1 (loop)
EASE = {0: lambda u: 1 - (1 - u) ** 1.6}
HOLDS = [(0.0, 3.3, A1), (3.6, 6.5, A2), (6.8, 9.9, B1), (10.2, 13.5, B2), (13.8, 17.0, C1), (17.3, 20.5, C2),
         (20.8, 23.6, D1), (23.9, 27.0, D2), (27.3, 30.6, E1), (30.9, 33.5, E2), (33.8, 36.9, F1s), (37.2, 40.0, F2),
         (40.3, 43.7, G1), (44.0, 46.0, G2)]


def timeline(tl, kit, M):
    """M is the project module (geometry constants and shared helpers)."""
    ev, drop, slide, grow = tl.ev, tl.drop, tl.slide, tl.grow
    I4 = np.eye(4)
    T_DUSK, T_SWELL = 39.9, 40.6

    def ctl(t):
        return T(smooth(c01((t - T_DUSK) / 0.4)), smooth(c01((t - T_SWELL) / 1.2)), 0), False
    tl.custom('ctl', ctl)
    kit.appear('bd_day', -1.0, T_DUSK + 0.2); kit.appear('roofs_day', -1.0, T_DUSK + 0.2)
    kit.appear('bd_dusk', T_DUSK + 0.2); kit.appear('roofs_dusk', T_DUSK + 0.2)
    ev(T_DUSK + 0.2, 'dusk', 0.4, 'swish')

    # ================= Z1 (0.0-6.5) arrival and both kids' beds
    tl.events.append(dict(t=0.02, name='doorbell', strength=0.45, kind='bell'))
    grow('rug', 0.10, 0.34, 'x', (0.20, 0, 0), 0.5, 'swish')
    M.bags(kit, (0.34, 0.52, 0.70), (21.05, 21.25, 21.45), F1['pos'])
    st_N = drop('pod_N', 0.80, 0.95, 0.45, 0.03, 0.85, 'thud')
    st_M = drop('pod_M', 0.95, 1.10, 0.45, 0.03, 0.85, 'thud')
    st_S = drop('pod_S', 1.10, 1.25, 0.45, 0.03, 0.9, 'thud')
    drop('lb_mat', 1.30, 1.45, 0.40, 0.04, 0.6, 'thud')
    slide('rb_ledger', 1.55, 1.70, (0, 0, 0.5), 1.0, 0.6, 'clank')
    grow('rb_post', 1.75, 1.90, 'z', (0, 0, M.PZ), 0.6, 'clank')
    drop('rb_deck', 2.00, 2.15, 0.45, 0.03, 0.85, 'thud')
    drop('rb_mat', 2.22, 2.35, 0.35, 0.04, 0.55, 'thud')
    for k in range(4):
        drop(f'st{k}', 2.43 + 0.2 * k, 2.55 + 0.2 * k, 0.40, 0.04, 0.55 + 0.05 * k, 'thud')
    drop('rb_duvet', 3.70, 3.86, 0.35, 0.03, 0.5, 'thud')
    drop('lb_duvet', 3.90, 4.05, 0.30, 0.03, 0.45, 'thud')
    for i, (t_on, pil) in enumerate(((4.40, 'rb_pil'), (4.90, 'lb_pil'))):
        drop(f'rl{i}', t_on - 0.14, t_on - 0.02, 0.15, 0.04, 0.2, 'none')
        kit.appear(f'rl_on{i}', t_on)
        kit.note(t_on, i, 0.35)
        drop(pil, t_on - 0.06, t_on + 0.10, 0.30, 0.08, 0.35, 'tick')
    slide('uds', 5.35, 5.50, (0, 0, 0.35), 1.0, 0.45, 'thud')
    drop('uds_items', 5.70, 5.86, 0.25, 0.06, 0.35, 'tick')
    drop('porch_cush', 6.05, 6.22, 0.30, 0.06, 0.35, 'tick')

    # ================= Z2 (6.5-13.5) kids' storage on the podium: riser drawers, lid tease, under-deck shelf, ledge
    for k in range(4):
        base = tl.anims[f'st{k}']
        x0 = (2.28, 2.56, 2.84, 3.12)[k]
        to, tc = 6.95 + 0.22 * k, 7.62 + 0.24 * k
        f = kit.drawer(0.0, to, tc, (-0.22, 0, 0), base=base)
        tl.custom(f'sd{k}', (lambda f, base: lambda t: (f(t)[0], base(t)[1]))(f, base))
        ev(to + 0.06, f'sd{k}_open', 0.35, 'swish'); ev(tc + 0.17, f'sd{k}_shut', 0.55 + 0.1 * (k == 3), 'thud')
        drop(f'toys{k}', to + 0.14, to + 0.30, 0.30, 0.05, 0.35, 'tick', parent=f)
    lid_tease = (8.80, 9.55)
    slide('ledge', 10.55, 10.70, (0, 0, 0.30), 1.0, 0.45, 'thud')
    for j in range(3):
        drop(f'ledge_bk{j}', 10.95 + 0.25 * j, 11.10 + 0.25 * j, 0.25, 0.05, 0.35, 'tick')

    # ================= Z3 (13.5-20.5) west storage wall
    S2p = np.array(C1[0]['pos'])
    tl.slide('hooks', 13.90, 14.04, (0.45, 0, 0), 1.0, 0.5, 'thud')
    tl.from_camera('coats', 14.10, 14.26, S2p, 0.4, 0.4, 'tick')
    fc = tl.from_camera('tc_body', 14.40, 14.60, S2p, 0.35, 0.9, 'thud')
    kit.door('tc_linS', (0.418, 0.002, 0), math.radians(-95), 14.40, 14.72, 15.32, base=fc, more=[(31.40, 32.95)])
    kit.door('tc_linN', (0.418, 0.978, 0), math.radians(95), 14.40, 14.76, 15.36, base=fc, snd=False, more=[(31.44, 32.99)])
    for k in range(3):
        tl.from_camera(f'lin{k}', 14.86 + 0.13 * k, 15.04 + 0.13 * k, S2p, 0.45, 0.45, 'tick')
    kit.door('tc_wdS', (0.418, 0.982, 0), math.radians(-95), 14.40, 15.52, 16.40, base=fc)
    kit.door('tc_wdN', (0.418, 1.978, 0), math.radians(95), 14.40, 15.56, 16.44, base=fc, snd=False)
    RAIL0, PIV = np.array([0.21, 2.62]), np.array([0.03, 2.66])
    t_dn, t_up = 15.70, 16.15

    def rail_off(t):
        if t < t_dn:
            k = 0.0
        elif t < t_up:
            k = eob(c01((t - t_dn) / 0.28), 0.6)
        else:
            k = 1 - smooth(c01((t - t_up) / 0.22))
        return np.array([0.36 * k, -0.62 * k])

    def rail(t):
        if t < 14.40:
            return I4, False
        o = rail_off(t)
        return T(o[0], 0, o[1]) @ fc(t)[0], True
    tl.custom('wd_rail', rail)

    def arm(t):
        if t < 14.40:
            return I4, False
        o = rail_off(t)
        v0 = RAIL0 - PIV
        v = RAIL0 + o - PIV
        ph0, ph1 = math.atan2(v0[0], v0[1]), math.atan2(v[0], v[1])
        s = np.linalg.norm(v) / np.linalg.norm(v0)
        Mx = T(PIV[0], 0, PIV[1]) @ R('y', ph1) @ np.diag([1, 1, s, 1.0]) @ R('y', -ph0) @ T(-PIV[0], 0, -PIV[1])
        return fc(t)[0] @ Mx, True
    tl.custom('wd_armS', arm); tl.custom('wd_armN', arm)
    ev(t_dn + 0.28, 'rail_down', 0.45, 'swish'); ev(t_up + 0.22, 'rail_up', 0.5, 'thud')
    hinge = np.array([0.0, 0, M.DZ])
    T_FLAP, T_FOLD = 16.75, 22.20

    def flap(t):
        if t < T_FLAP:
            return I4, True
        if t < T_FOLD:
            u = c01((t - T_FLAP) / 0.24)
            return about(hinge, R('y', math.pi / 2 * (u * u))), True
        u = c01((t - T_FOLD) / 0.24)
        return about(hinge, R('y', math.pi / 2 * (1 - eob(u, 0.8)))), True
    tl.custom('desk_flap', flap)
    ev(T_FLAP + 0.24, 'flap_down', 0.7, 'thud'); ev(T_FOLD + 0.24, 'flap_up', 0.7, 'thud')
    for c in range(6):
        tl.from_camera(f'pig{c}', 17.05 + 0.15 * c, 17.22 + 0.15 * c, np.array(C2[0]['pos']), 0.35, 0.35, 'tick')
    drop('pots', 18.05, 18.20, 0.25, 0.06, 0.35, 'tick')
    # guest cabinet: opens empty (a tease), shuts; reopens for the bags in Z4
    kit.door('tc_guest', (0.418, 0, 2.69), math.radians(-100), 14.40, 18.80, 19.85, axis='y', base=fc, more=[(20.70, 21.62)])

    # ================= Z4 (20.5-27.0) the guests' turn: bags in, desk folds, cutaway, futon
    tl.events.append(dict(t=20.55, name='doorbell2', strength=0.35, kind='bell'))
    PNL_H = np.array([2.585, 0, M.PZ])

    def pnl(t):
        B = st_M(t)[0] if t < 5.0 else I4
        if t < 23.95:
            return B, st_M(t)[1]
        if t < 24.70:
            a = math.radians(62) * eob(c01((t - 23.95) / 0.28), 0.5)
        else:
            u = c01((t - 24.70) / 0.20)
            a = math.radians(62) * (1 - u * u)
            if u >= 1:
                tau = t - 24.90
                a = -math.radians(1.5) * math.exp(-tau / 0.05) * abs(math.sin(math.pi * tau / 0.08))
        return about(PNL_H, R('y', a)), True
    tl.custom('deck_pnl', pnl)
    ev(24.00, 'pnl_open', 0.45, 'swish'); ev(24.90, 'pnl_shut', 0.75, 'thud')
    kit.appear('hol_led', 24.12); ev(24.12, 'hollow_led', 0.35, 'chime')
    M.futon(kit, 25.05, 25.22, 25.40, 25.64, 25.72, lid_more=[lid_tease])
    drop('fut_pil', 26.22, 26.38, 0.3, 0.08, 0.35, 'tick')
    drop('rl2', 26.38, 26.48, 0.15, 0.04, 0.2, 'none')
    kit.appear('rl_on2', 26.52); kit.note(26.52, 2, 0.35)

    # ================= Z5 (27.0-33.5) the wow: the double rolls out and pops up; duvets and throw
    off = M.double_out(kit, 27.62, 27.95, 29.55, 29.85, 30.25)
    for j, (t_on, pil) in enumerate(((30.80, 'dbl_pil1'), (31.00, 'dbl_pil2'))):
        i = 3 + j
        drop(f'rl{i}', t_on - 0.12, t_on - 0.02, 0.15, 0.04, 0.2, 'none')
        kit.appear(f'rl_on{i}', t_on)
        kit.note(t_on, i, 0.35)
        drop(pil, t_on - 0.06, t_on + 0.10, 0.30, 0.08, 0.35, 'tick')
    lin_from = (0.85, -1.2, 1.9)                     # out of the linen cabinet (relative offsets)
    kit.two_panel('fut_duvA', 'fut_duvB', (2.0225, M.PZ + M.FUT_TH + 0.031), 31.62, 31.90, 31.95,
                  off=(-1.9, -1.35, 1.95))
    rid = lambda t: T(off(t)[0], 0, off(t)[1])
    kit.two_panel('dbl_duvA', 'dbl_duvB', (2.125, 0.531), 31.92, 32.20, 32.25, off=(-0.95, -1.40, 1.95), base=rid)
    M.throw_open(kit, 32.40, 32.62, 32.68, off)

    # ================= Z6 (33.5-40.0) the person moment
    gq = M.FIGS['gpa'].build_pose
    reach = dict(gq); reach.update(spine=gq.get('spine', 0) + 14, sh_r=62, sh_r_out=24, elbow_r=12, neck=gq.get('neck', 0) + 10)
    M.FIGS['gma'].animate(tl, pop=34.00, sound=0.45)
    M.FIGS['gpa'].animate(tl, pose=fg.track([(35.30, gq), (35.70, reach), (36.10, reach), (36.45, gq)]), pop=34.20, sound=0.45)
    drop('cane', 34.40, 34.55, 0.25, 0.03, 0.35, 'tick')

    def stool(t):
        B = st_S(t)[0] if t < 5.0 else I4
        if t < 35.00:
            return B, st_S(t)[1]
        k = eob(c01((t - 35.00) / 0.28), 1.0)
        return T(-0.40 * k, 0, 0), True
    tl.custom('stoolA', stool)
    tl.custom('stoolB', st_S)
    ev(35.28, 'stool_out', 0.6, 'thud')
    drop('mug', 35.62, 35.78, 0.30, 0.05, 0.4, 'tick')

    def nstep(t):
        if t < 1.10:
            return I4, False
        B = st_S(t)[0]
        k = eob(c01((t - 33.70) / 0.22), 1.2)
        return B @ T(0.37 * (1 - k), 0, 0), True
    tl.custom('nstep', nstep)
    tl.custom('slippers', nstep)
    ev(33.92, 'nstep', 0.6, 'thud')
    LH = np.array([1.90, 0, 0.22])

    def nlid(t):
        Mb, v = nstep(t)
        if t < 37.45:
            return Mb, v
        if t < 38.15:
            a = math.radians(-105) * eob(c01((t - 37.45) / 0.22), 0.6)
        else:
            u = c01((t - 38.15) / 0.18)
            a = math.radians(-105) * (1 - u * u)
        return Mb @ about(LH, R('y', a)), v
    tl.custom('nstep_lid', nlid)
    ev(37.55, 'nlid_open', 0.4, 'swish'); ev(38.33, 'nlid_shut', 0.6, 'thud')

    # ================= Z7 (40.0-46.0) lights and loop
    for i in range(5):
        kit.note(T_SWELL + 0.3 * i, i, 0.14, name=f'echo{i}')

    # pieces stored inside the podium ride its drops
    lid0 = tl.anims['lid']
    tl.custom('lid', lambda t: ((st_S(t)[0] @ lid0(t)[0]) if t < 5.0 else lid0(t)[0], st_S(t)[1]))
    for j in range(4):
        f0 = tl.anims[f'fut{j}']
        tl.custom(f'fut{j}', (lambda f0: lambda t: ((st_S(t)[0] @ f0(t)[0]) if t < 5.0 else f0(t)[0], st_S(t)[1]))(f0))
    dbl0, legs0 = tl.anims['dbl'], tl.anims['dbl_legs']
    tl.custom('dbl', lambda t: ((st_M(t)[0] @ dbl0(t)[0]) if t < 5.0 else dbl0(t)[0], st_M(t)[1]))
    tl.custom('dbl_legs', lambda t: (legs0(t)[0], legs0(t)[1] and t > 27.0))
    return tl
