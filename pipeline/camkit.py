"""camkit: gliding camera stations joined by fast swings (shared by the room projects).

    import camkit as ck
    def P(x, y, z, yaw, pitch): return dict(pos=(x, y, z), yaw=yaw, pitch=pitch)
    SA = (P(1.70, 0.66, 1.46, 0.0, -3.0), P(1.70, 0.92, 1.40, 0.0, -4.0))     # (start pose, end pose): a push-in
    HOLDS = [(0.0, 3.62, SA), (3.92, 7.30, SB), ..., (27.10, DUR, SE)]          # (t0, t1, station)
    camera = ck.hold_camera(HOLDS, vfov=85.0, rest=REST)                         # camera(t) -> dict(pos, yaw, pitch, vfov)

During a hold the camera glides at constant speed from the station's start pose to its end pose (the hits'
camera never stands still). Between holds it swings with a smoothstep and a small upward arc (`lift` degrees of
pitch); the last swing (into the final wide) eases out with `final_lift`. rest=True is the ROOM_REST probe:
camera(t) shows station int(t) at its start pose, so probe 0.5, 1.5, ... steps through the stations.
Poses: yaw in degrees east of north (0 = looking +y), pitch up, positions in metres.
"""
import math

import numpy as np

from animkit import c01, smooth


def lerp_cam(a, b, s, lift=2.0, vfov=85.0):
    """Pose between a and b at s (0..1), yaw the short way round, plus lift * sin(pi s) degrees of pitch."""
    pa, pb = np.array(a['pos']), np.array(b['pos'])
    dyaw = (b['yaw'] - a['yaw'] + 180) % 360 - 180
    return dict(pos=tuple(pa + (pb - pa) * s), yaw=a['yaw'] + dyaw * s,
                pitch=a['pitch'] + (b['pitch'] - a['pitch']) * s + lift * math.sin(math.pi * s), vfov=vfov)


def glide(st, u, vfov=85.0):
    """Station st = (start pose, end pose) at progress u (clamped to 0..1)."""
    a, b = st
    return lerp_cam(a, b, c01(u), lift=0.0, vfov=vfov)


def hold_camera(holds, vfov=85.0, lift=2.0, final_lift=4.0, rest=False):
    """camera(t) for HOLDS = [(t0, t1, (start, end)), ...]; the last hold's t1 is normally the clip length."""
    stations = [h[2] for h in holds]

    def camera(t):
        if rest:
            return dict(stations[min(len(stations) - 1, int(t))][0], vfov=vfov)
        for i, (t0, t1, st) in enumerate(holds):
            if t < t1 or i == len(holds) - 1:
                return glide(st, (t - t0) / (t1 - t0), vfov)
            n0, _, nst = holds[i + 1]
            if t < n0:
                u = (t - t1) / (n0 - t1)
                a, b = glide(st, 1.0, vfov), glide(nst, 0.0, vfov)
                if i + 1 == len(holds) - 1:
                    return lerp_cam(a, b, 1 - (1 - c01(u)) ** 3, lift=final_lift, vfov=vfov)
                return lerp_cam(a, b, smooth(u), lift=lift, vfov=vfov)
        return glide(holds[-1][2], 1.0, vfov)
    return camera
