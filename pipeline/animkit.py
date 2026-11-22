"""animkit: timeline of pieces moving into place + camera path -> frames.bin, plan.txt, frames.json.

    tl = Timeline(rk, fps=30)
    tl.from_camera('desk', 0.12, 0.42, cam_pos, frac=0.42, strength=1.0)      # flies in from the camera, lands 0.42 s
    tl.drop('books', 0.66, 0.82, height=0.22)
    slide = tl.slide('bed_rail', 2.94, 3.10, (-0.75, -0.30, 0))
    tl.custom('drawer', fn)                 # fn(t) -> (4x4, visible); call tl.ev(t, name, strength, kind) for its sounds
    tl.export(dur, camera, lights, outdir)  # camera(t) -> dict(pos, yaw, pitch[, vfov]); lights(mats4, vis) -> [light records]

Each helper hides the piece before t0, moves it during t0..t1, registers a landing event at t1 (sound + camera
punch in the post step) and leaves it at rest afterwards. Strength 0..1 scales the sound and the punch.
Camera: frames where the camera pose equals its neighbours' are "static" and share a group (the denoiser
accumulates samples across a group). Frames where the camera moves are rendered as 3 sub-frames and blurred.
"""
import json
import math
import os

import numpy as np


def c01(x):
    return min(max(x, 0.0), 1.0)


def eoc(u):                      # ease-out cubic
    u = c01(u)
    return 1 - (1 - u) ** 3


def eob(u, k=1.3):               # ease-out back (overshoot k)
    u = c01(u) - 1.0
    return 1 + (k + 1) * u ** 3 + k * u ** 2


def smooth(u):
    u = c01(u)
    return u * u * (3 - 2 * u)


class Timeline:
    def __init__(self, kit, fps=30):
        self.kit, self.fps = kit, fps
        self.anims, self.events, self.cen = {}, [], {}
        for name in kit.ORDER:
            lo, hi = kit.bounds(name)
            self.cen[name] = (lo + hi) / 2.0

    # ------------------------------------------------------------------ events
    def ev(self, t, name, strength=0.5, kind='tick'):
        """kind: 'thud' | 'tick' | 'swish' | 'chime' | 'none'"""
        self.events.append(dict(t=round(t, 3), name=name, strength=strength, kind=kind))

    def custom(self, name, fn):
        self.anims[name] = fn
        return fn

    @staticmethod
    def settle(tau, amp=0.022):
        return 1 + amp * math.exp(-tau / 0.08) * math.sin(2 * math.pi * tau / 0.16)

    # ------------------------------------------------------------------ motion helpers
    def from_camera(self, name, t0, t1, cam, frac=0.4, strength=1.0, kind='thud'):
        """Starts part-way toward the camera (looks bigger) and recedes into place. Good for wall-mounted pieces."""
        K, I = self.kit, np.eye(4)
        piv = self.cen[name]; cam = np.array(cam, float)
        def f(t):
            if t < t0:
                return I, False
            u = (t - t0) / (t1 - t0)
            if u < 1:
                off = (1 - eoc(u)) * frac * (cam - piv)
                s = 0.45 + 0.55 * smooth(u / 0.3)
            else:
                off = np.zeros(3); s = self.settle(t - t1)
            return K.T(*off) @ K.about(piv, K.S(s, s, s)), True
        self.ev(t1, name, strength, kind)
        return self.custom(name, f)

    def drop(self, name, t0, t1, height, bounce=0.05, strength=0.5, kind='tick', parent=None, tilt=0.0):
        """Falls from height and bounces. parent = another piece's function (contents that ride in a drawer)."""
        K, I = self.kit, np.eye(4)
        piv = self.cen[name]
        def f(t):
            if t < t0:
                return I, False
            u = (t - t0) / (t1 - t0)
            if u < 1:
                z = height * (1 - u * u); s = 0.5 + 0.5 * smooth(u / 0.35); a = tilt * (1 - u)
            else:
                tau = t - t1
                z = bounce * height * math.exp(-tau / 0.09) * abs(math.sin(math.pi * tau / 0.13)); s = 1.0; a = 0.0
            M = K.T(0, 0, z) @ K.about(piv, K.S(s, s, s))
            if a:
                M = M @ K.about(piv, K.R('y', a))
            if parent is not None:
                M = parent(t)[0] @ M
            return M, True
        self.ev(t1, name, strength, kind)
        return self.custom(name, f)

    def fly(self, name, t0, t1, off, arc=0.06, strength=0.6, kind='thud'):
        """Arrives from an offset with a small hop. Use when a straight drop would pass through something."""
        K, I = self.kit, np.eye(4)
        piv = self.cen[name]; off = np.array(off, float)
        def f(t):
            if t < t0:
                return I, False
            u = (t - t0) / (t1 - t0)
            if u < 1:
                o = (1 - eoc(u)) * off + np.array([0, 0, arc * math.sin(math.pi * u)]); s = 0.5 + 0.5 * smooth(u / 0.3)
            else:
                o = np.zeros(3); s = self.settle(t - t1, 0.015)
            return K.T(*o) @ K.about(piv, K.S(s, s, s)), True
        self.ev(t1, name, strength, kind)
        return self.custom(name, f)

    def slide(self, name, t0, t1, off, back=1.0, strength=0.7, kind='thud'):
        """Slides in from an offset (rails, panels, appliances)."""
        K, I = self.kit, np.eye(4)
        off = np.array(off, float)
        def f(t):
            if t < t0:
                return I, False
            u = (t - t0) / (t1 - t0)
            k = 1 - eob(u, back) if u < 1 else 0.0
            return K.T(*(off * k)), True
        self.ev(t1, name, strength, kind)
        return self.custom(name, f)

    def grow(self, name, t0, t1, axis='z', pivot=(0, 0, 0), strength=0.7, kind='thud'):
        """Extrudes along an axis from a pivot (panels rising from the floor, units growing out of a wall)."""
        K, I = self.kit, np.eye(4)
        def f(t):
            if t < t0:
                return I, False
            u = (t - t0) / (t1 - t0)
            s = 0.02 + 0.98 * eob(u, 1.0) if u < 1 else 1.0
            sc = [1.0, 1.0, 1.0]; sc['xyz'.index(axis)] = s
            return K.about(pivot, K.S(*sc)), True
        self.ev(t1, name, strength, kind)
        return self.custom(name, f)

    # ------------------------------------------------------------------ export
    def state(self, t):
        mats4, vis = {}, {}
        dt = 1.0 / self.fps
        for name in self.kit.ORDER:
            if name in self.anims:
                M, v = self.anims[name](t)
                v = 1 if v else 0
                if v:
                    Mp, vp = self.anims[name](t - dt); Mn, _ = self.anims[name](t + dt)
                    if (not vp) or np.abs(Mp - M).max() > 1e-6 or np.abs(Mn - M).max() > 1e-6:
                        v = 2          # moving: the denoiser will not reuse its pixels across frames
            else:
                M, v = np.eye(4), 1
            mats4[name] = M; vis[name] = v
        return mats4, vis

    def export(self, dur, camera, lights, outdir='.', shutter=0.6, subframes=3):
        K = self.kit
        nfr = int(round(dur * self.fps))
        dt = 1.0 / self.fps

        def key(c):
            return tuple(round(float(v), 6) for v in (*c['pos'], c['yaw'], c['pitch'], c.get('vfov', 85.0)))

        def record(t):
            mats4, vis = self.state(t)
            c = camera(t)
            return dict(cam=K.cam_record(tuple(c['pos']), c['yaw'], c['pitch'], c.get('vfov', 85.0)), mats=mats4, vis=vis,
                        lights=lights(mats4, vis))

        recs, plan, frames, blur, groups = [], [], [], {}, {}
        for f in range(nfr):
            t = f * dt
            k0 = key(camera(t))
            sub = shutter / subframes * dt
            moving = k0 != key(camera(t - sub)) or k0 != key(camera(t + sub))
            if moving:
                blur[f] = abs(camera(t)['yaw'] - camera(t - sub)['yaw'])
                ids = []
                for k in range(subframes):
                    recs.append(record(t + (k - (subframes - 1) / 2.0) * sub)); plan.append((len(recs) - 1, -1)); ids.append(len(recs) - 1)
                frames.append(ids)
            else:
                g = groups.setdefault(k0, len(groups) + 1)
                recs.append(record(t)); plan.append((len(recs) - 1, g)); frames.append([len(recs) - 1])
        K.write_frames(recs, os.path.join(outdir, 'frames.bin'))
        with open(os.path.join(outdir, 'plan.txt'), 'w') as fh:
            for i, g in plan:
                fh.write(f'{i} {g}\n')
        events = sorted(self.events, key=lambda e: e['t'])
        json.dump(dict(fps=self.fps, nframes=nfr, dur=dur, frames=frames, events=events, plan=plan, blur=blur,
                       vfov=camera(0).get('vfov', 85.0)), open(os.path.join(outdir, 'frames.json'), 'w'))
        print('frames:', nfr, 'records:', len(recs), 'events:', len(events))
        return recs
