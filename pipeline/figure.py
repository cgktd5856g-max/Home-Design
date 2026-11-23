"""figure: a friendly, faceless stand-in person (adult or child) made from roomkit primitives, posed by joint angles.

Mannequin style: smooth tapered limbs with ball joints, an egg head with no face or hair, mitten hands, one soft
colour. Every body segment is its own piece (<inst>_pelvis, <inst>_torso, <inst>_head, <inst>_uarm_l, ...), so a
pose change is just a set of rigid per-piece transforms: it works with Timeline.custom, the code renderer and Blender.

    import figure as fg
    # build(): the figure is built at rest in the pose and place you give (a static figure needs nothing else)
    mom = fg.figure('mom', 'adult', pose='stand', at=(0.55, 1.95, 115))              # at = (x, y, facing yaw)
    kid = fg.figure('kid', 'child', pose='sit', at=(2.25, 1.55, 90), seat=0.64)       # sitting on a 0.64 m surface
    # timeline(): animate it (each argument is a constant or a function of t)
    mom.animate(tl, pose=fg.track([(20.0, 'stand'), (20.5, 'reach_up'), (21.4, 'reach_up'), (21.9, 'stand')]),
                at=(1.5, 0.95, 180), visible=lambda t: t >= 19.0, pop=19.0)
    pose_fn, at_fn = fg.walk([(10.0, (0.5, 1.0, 90)), (12.0, (2.0, 1.0, 90))], kid)     # walk between points
    kid.animate(tl, pose=pose_fn, at=at_fn)

Placement: `at=(x, y, yaw)` puts the pelvis over (x, y), facing yaw degrees east of north (0 = facing +y, the same
convention as the camera), and drops the figure until its lowest foot touches `floor` (default 0). With `seat=z`
the pelvis/thighs rest on a surface at height z instead. `M=4x4` places the pelvis (hip-joint centre) directly.

Poses are dicts of joint angles in degrees (missing joints are 0, i.e. standing straight, arms hanging):
  spine / neck              bend forward (negative leans back, looks up)
  spine_twist / neck_turn   turn left;  spine_side: lean to the figure's right
  hip_l, hip_r              thigh forward / up       hip_l_out, hip_r_out   leg out to the side
  knee_l, knee_r            bend (shin goes back)    ankle_l, ankle_r       toes up (negative: on tiptoe)
  sh_l, sh_r                arm forward / up (180 = straight up)          sh_l_out, sh_r_out   arm out to the side
  sh_l_rot, sh_r_rot        twist the arm so the bent forearm points up when the arm is out (wave)
  elbow_l, elbow_r          bend the forearm forward / up
Presets in POSES: stand, sit, sit_desk, reach_up, reach_both, step_up, crouch, wave, plus walk_pose(phase).
lerp_pose(a, b, u), mirror(pose) (swap left and right), track(keys) (pose keyframes -> pose(t)), walk(keys, fig),
Figure.sit_pose(seat) (sitting with feet on the floor for any seat height).
"""
import math

import numpy as np

import roomkit as rk
from animkit import c01, smooth
from roomkit import R, S, T, about, ellipsoid, lathe, tube, xform

SEGS = ('pelvis', 'torso', 'head', 'uarm_l', 'farm_l', 'uarm_r', 'farm_r',
        'thigh_l', 'shin_l', 'foot_l', 'thigh_r', 'shin_r', 'foot_r')

# Body proportions (metres). Limb radii are listed from the top joint down (tube taper).
PROPS = {
    'adult': dict(                                   # about 1.68 m
        ankle=0.075, shin=0.42, thigh=0.43, hip=0.088, waist=0.10, chest=0.40, sh=(0.178, 0.343), neck=0.075,
        head=(0.080, 0.094, 0.112), upper=0.29, fore=0.25, girth=1.0, tz=1.0,
        r_hip=0.073, r_thigh=(0.074, 0.073, 0.067, 0.058, 0.050), r_knee=0.049,
        r_shin=(0.049, 0.051, 0.046, 0.039, 0.033), r_ankle=0.031, foot=(0.088, 0.25, 0.068, 0.055),
        r_sh=0.050, r_upper=(0.046, 0.044, 0.041, 0.037, 0.034), r_elbow=0.034,
        r_fore=(0.033, 0.034, 0.031, 0.027, 0.024), r_wrist=0.024, hand=(0.021, 0.042, 0.078), r_neck=0.043),
    'child': dict(                                   # about 1.15 m (six or seven years old): bigger head, shorter legs
        ankle=0.05, shin=0.27, thigh=0.28, hip=0.062, waist=0.07, chest=0.27, sh=(0.121, 0.230), neck=0.05,
        head=(0.074, 0.086, 0.098), upper=0.19, fore=0.165, girth=0.72, tz=0.675,
        r_hip=0.053, r_thigh=(0.054, 0.053, 0.048, 0.042, 0.037), r_knee=0.036,
        r_shin=(0.036, 0.037, 0.034, 0.029, 0.025), r_ankle=0.024, foot=(0.064, 0.17, 0.05, 0.04),
        r_sh=0.037, r_upper=(0.034, 0.033, 0.031, 0.028, 0.026), r_elbow=0.026,
        r_fore=(0.025, 0.026, 0.024, 0.021, 0.019), r_wrist=0.019, hand=(0.016, 0.031, 0.054), r_neck=0.033),
}

# Pelvis and torso outlines for the adult, (half width, height); depth is a fraction of the width. Children scale them.
PELVIS = [(0.0, -0.100), (0.07, -0.096), (0.115, -0.080), (0.148, -0.050), (0.163, -0.010), (0.162, 0.040),
          (0.150, 0.085), (0.138, 0.120), (0.10, 0.150), (0.0, 0.160)]
TORSO = [(0.0, -0.06), (0.10, -0.055), (0.130, -0.03), (0.135, 0.02), (0.142, 0.08), (0.158, 0.15), (0.172, 0.22),
         (0.175, 0.28), (0.165, 0.33), (0.140, 0.37), (0.095, 0.395), (0.0, 0.41)]
DEPTH_PELVIS, DEPTH_TORSO = 0.70, 0.64

# Soft, clean colours (sRGB) with a satin finish. figure() registers the material it needs the first time.
COLOURS = {
    'fig_adult': (214, 216, 220),       # light cool grey: reads against warm white walls and oak
    'fig_child': (238, 214, 196),       # soft peach
    'fig_sage': (186, 200, 182),
    'fig_blue': (190, 204, 222),
    'fig_white': (240, 238, 234),
}


def materials(names=None, rough=0.48):
    """Register figure materials (all of COLOURS by default). Safe to call more than once."""
    for nm in (names or COLOURS):
        if nm not in rk.MATIDX:
            rk.mat(nm, col=rk.srgb(*COLOURS[nm]), rough=rough, f0=0.04)


# ------------------------------------------------------------------------------------------- poses
POSES = {
    'stand': dict(sh_l_out=5, sh_r_out=5, elbow_l=8, elbow_r=8),
    'sit': dict(hip_l=88, hip_r=88, knee_l=88, knee_r=88, spine=6, neck=8, sh_l=22, sh_r=22, sh_l_out=6, sh_r_out=6,
                elbow_l=46, elbow_r=46),
    'sit_desk': dict(hip_l=86, hip_r=86, knee_l=80, knee_r=80, ankle_l=-6, ankle_r=-6, spine=10, neck=12,
                     sh_l=42, sh_r=42, sh_l_out=8, sh_r_out=8, elbow_l=58, elbow_r=58),
    'reach_up': dict(sh_r=168, sh_r_out=6, elbow_r=10, sh_l=24, sh_l_out=10, elbow_l=22, spine=-5, neck=-24,
                     ankle_l=-16, ankle_r=-16, hip_l=2, hip_r=2),
    'reach_both': dict(sh_r=165, sh_l=165, sh_r_out=10, sh_l_out=10, elbow_r=14, elbow_l=14, spine=-6, neck=-26,
                       ankle_l=-16, ankle_r=-16),
    'step_up': dict(hip_r=58, knee_r=78, ankle_r=20, hip_l=-8, knee_l=6, ankle_l=6, spine=12, neck=4,
                    sh_l=28, sh_l_out=6, elbow_l=28, sh_r=-14, sh_r_out=6, elbow_r=18),
    'crouch': dict(hip_l=105, hip_r=105, knee_l=125, knee_r=125, ankle_l=22, ankle_r=22, spine=22, neck=10,
                   sh_l=40, sh_r=40, elbow_l=30, elbow_r=30, hip_l_out=10, hip_r_out=10),
    'wave': dict(sh_r=20, sh_r_out=78, sh_r_rot=85, elbow_r=105, sh_l_out=5, elbow_l=10, neck_turn=0),
}


def pose_of(p):
    return dict(POSES[p]) if isinstance(p, str) else dict(p)


def lerp_pose(a, b, u):
    """Blend two poses (names or dicts) joint by joint; u = 0 gives a, 1 gives b."""
    a, b = pose_of(a), pose_of(b)
    return {k: a.get(k, 0.0) + (b.get(k, 0.0) - a.get(k, 0.0)) * u for k in set(a) | set(b)}


def mirror(p):
    """Swap left and right (e.g. reach with the left arm)."""
    out = {}
    for k, v in pose_of(p).items():
        if k in ('spine_twist', 'spine_side', 'neck_turn'):
            out[k] = -v
        elif '_l' in k:
            out[k.replace('_l', '_r', 1)] = v
        elif '_r' in k:
            out[k.replace('_r', '_l', 1)] = v
        else:
            out[k] = v
    return out


def track(keys, ease=smooth):
    """keys = [(t, pose), ...] -> pose(t): held before the first and after the last key, eased between keys.
    A pose may also be a function of t (e.g. a walk cycle), which lets a walk blend into a standing pose."""
    keys = sorted(keys, key=lambda k: k[0])

    def at(i, t):
        p = keys[i][1]
        return p(t) if callable(p) else p

    def f(t):
        if t <= keys[0][0]:
            return pose_of(at(0, t))
        for i in range(len(keys) - 1):
            t0, t1 = keys[i][0], keys[i + 1][0]
            if t < t1:
                return lerp_pose(at(i, t), at(i + 1, t), ease((t - t0) / (t1 - t0)) if t1 > t0 else 1.0)
        return pose_of(at(len(keys) - 1, t))
    return f


def _gait_foot(g):
    """Foot pitch (deg, toes up) over the gait cycle, g in degrees: 0 heel strike, 180 toe-off."""
    ks = [(0, 12), (25, 0), (115, 0), (180, -30), (250, -4), (330, 8), (360, 12)]
    g %= 360
    for (a0, v0), (a1, v1) in zip(ks, ks[1:]):
        if g <= a1:
            u = (g - a0) / (a1 - a0)
            return v0 + (v1 - v0) * (0.5 - 0.5 * math.cos(math.pi * u))
    return ks[-1][1]


def walk_pose(phase, amount=1.0):
    """Walking pose at phase (cycles; one cycle = two steps). amount 0..1 blends from standing to a full stride."""
    a = 2 * math.pi * phase
    p = {}
    for side, sg in (('r', 1.0), ('l', -1.0)):
        aa = a if sg > 0 else a + math.pi
        s = math.sin(aa)
        hip = 24 * s
        knee = 5 + 55 * max(0.0, math.cos(aa + 0.5)) ** 1.3
        g = math.degrees(aa) - 90                       # 0 at heel strike (thigh furthest forward)
        p[f'hip_{side}'] = hip
        p[f'knee_{side}'] = knee
        p[f'ankle_{side}'] = _gait_foot(g) - (hip - knee)
        p[f'sh_{side}'] = -20 * s                       # the arm swings against its leg
        p[f'sh_{side}_out'] = 6
        p[f'elbow_{side}'] = 14 + 12 * max(0.0, -s)
    p['spine'] = 4
    p['spine_twist'] = 4 * math.sin(a)
    return lerp_pose('stand', p, c01(amount))


def walk(keys, fig=None, stride=None, ease=smooth, settle='stand'):
    """Walk through keys = [(t, (x, y, yaw)), ...] (yaw None: face the way it walks). Returns (pose_fn, at_fn)
    for Figure.animate. With the default ease the figure starts and stops at every key. The legs cycle with the distance
    covered (stride = one step, default 0.7 x leg length) and the stride opens over the first half step and closes over
    the last, so the feet come together as it stops. Where it stands still it holds the `settle` pose."""
    keys = sorted(keys, key=lambda k: k[0])
    if stride is None:
        stride = 0.7 * (fig.p['ankle'] + fig.p['shin'] + fig.p['thigh']) if fig is not None else 0.62
    pts = [np.array(k[1][:2], float) for k in keys]
    seg_len = [float(np.linalg.norm(pts[i + 1] - pts[i])) for i in range(len(keys) - 1)]
    cum = np.concatenate([[0.0], np.cumsum(seg_len)])

    def heading(i):
        d = pts[i + 1] - pts[i]
        return math.degrees(math.atan2(d[0], d[1]))

    yaws = []
    for i, k in enumerate(keys):
        y = k[1][2] if len(k[1]) > 2 else None
        if y is None:
            y = heading(min(i, len(keys) - 2)) if len(keys) > 1 else 0.0
        yaws.append(y)

    def where(t):
        if t <= keys[0][0]:
            return 0, 0.0, 0.0
        for i in range(len(keys) - 1):
            t0, t1 = keys[i][0], keys[i + 1][0]
            if t < t1:
                u = (t - t0) / (t1 - t0)
                h = 1e-3
                du = (ease(min(1.0, u + h)) - ease(max(0.0, u - h))) / (min(1.0, u + h) - max(0.0, u - h))
                return i, ease(u), seg_len[i] * du / (t1 - t0)
        return len(keys) - 2, 1.0, 0.0

    def at_fn(t):
        i, e, _ = where(t)
        if len(keys) == 1:
            return (*pts[0], yaws[0])
        p = pts[i] + (pts[i + 1] - pts[i]) * e
        dy = (yaws[i + 1] - yaws[i] + 180) % 360 - 180
        return (float(p[0]), float(p[1]), yaws[i] + dy * e)

    def pose_fn(t):
        i, e, _ = where(t)
        if len(keys) == 1:
            return pose_of(settle)
        d = cum[i] + seg_len[i] * e
        amt = smooth(min(e, 1 - e) * seg_len[i] / (0.5 * stride))
        return lerp_pose(settle, walk_pose(d / (2 * stride)), amt)
    return pose_fn, at_fn


# ------------------------------------------------------------------------------------------- the figure
class Figure:
    def __init__(self, inst, kind='adult', mat=None):
        assert kind in PROPS, f'kind must be one of {list(PROPS)}'
        self.inst, self.kind, self.p = inst, kind, PROPS[kind]
        self.mat = mat or ('fig_child' if kind == 'child' else 'fig_adult')
        if self.mat not in rk.MATIDX:
            assert self.mat in COLOURS, f'material {self.mat!r} is not registered: add it with rk.mat() or use one of {list(COLOURS)}'
            materials([self.mat])
        self.local = self._meshes()
        self.vtx = {s: np.unique(np.round(P.reshape(-1, 3), 6), axis=0) for s, (P, _) in self.local.items()}
        # what rests on a seat: the pelvis and the upper 40% of each thigh (the knees may reach past the seat edge)
        self.seat_vtx = {s: v[v[:, 2] >= -0.4 * self.p['thigh']] if s.startswith('thigh') else v for s, v in self.vtx.items()}
        self.bind = self.bind_inv = None
        self.build_pose, self.build_root = 'stand', np.eye(4)

    @property
    def pieces(self):
        return [f'{self.inst}_{s}' for s in SEGS]

    # -- geometry of each segment in its own frame (joint at the origin, limbs hanging along -z)
    def _meshes(self):
        p = self.p
        g, tz = p['girth'], p['tz']

        def cat(*parts):
            return np.concatenate([q[0] for q in parts]), np.concatenate([q[1] for q in parts])

        def ball(c, r, n=10):
            return ellipsoid(c, (r, r, r), n)

        def limb(L, radii):
            return tube([(0, 0, -L * k / (len(radii) - 1)) for k in range(len(radii))], list(radii), 14)

        out = {}
        out['pelvis'] = xform(lathe([(r * g, z * tz) for r, z in PELVIS], 32), S(1, DEPTH_PELVIS, 1))
        out['torso'] = xform(lathe([(r * g, z * tz) for r, z in TORSO], 32), S(1, DEPTH_TORSO, 1))
        hx, hy, hz = p['head']
        out['head'] = cat(tube([(0, 0, -0.03 * tz), (0, 0, p['neck'] + 0.03)], p['r_neck'], 14),
                          ellipsoid((0, 0.012 * g, p['neck'] + 0.6 * hz), (hx, hy, hz), 16))
        hw, hd, hl = p['hand']
        for side, sg in (('l', -1.0), ('r', 1.0)):
            out[f'uarm_{side}'] = cat(ball((0, 0, 0), p['r_sh']), limb(p['upper'], p['r_upper']),
                                      ball((0, 0, -p['upper']), p['r_elbow']))
            hand = ellipsoid((0, 0.004, -p['fore'] - hl * 0.92), (hw, hd, hl), 10)
            thumb_c = np.array([-sg * hw * 0.45, hd * 0.85, -p['fore'] - hl * 0.55])
            thumb = xform(ellipsoid(thumb_c, (hw * 0.6, hw * 0.6, hl * 0.42), 8), about(thumb_c, R('x', 0.45)))
            out[f'farm_{side}'] = cat(limb(p['fore'], p['r_fore']), ball((0, 0, -p['fore']), p['r_wrist']), hand, thumb)
            out[f'thigh_{side}'] = cat(ball((0, 0, 0), p['r_hip']), limb(p['thigh'], p['r_thigh']),
                                       ball((0, 0, -p['thigh']), p['r_knee']))
            out[f'shin_{side}'] = cat(limb(p['shin'], p['r_shin']), ball((0, 0, -p['shin']), p['r_ankle']))
            fw, fl, fh, heel = p['foot']                  # a low sole plus an instep that rises to the ankle
            sh_ = fh * 0.6
            sole = rk.rbox((0, fl / 2 - heel, -p['ankle'] + sh_ / 2), (fw, fl, sh_), sh_ * 0.48, 5)
            z0, z1 = -p['ankle'] + sh_ * 0.3, -p['ankle'] * 0.25      # inside the sole .. just under the ankle joint
            instep = ellipsoid((0, fl * 0.12, (z0 + z1) / 2), (fw * 0.46, fl * 0.36, (z1 - z0) / 2), 12)
            out[f'foot_{side}'] = cat(sole, instep)
        return out

    # -- forward kinematics: pose + pelvis transform -> 4x4 per segment
    def fk(self, pose, M):
        p, q = self.p, pose_of(pose)
        a = lambda k: math.radians(q.get(k, 0.0))
        out = {'pelvis': M}
        Mt = M @ T(0, 0, p['waist']) @ R('z', a('spine_twist')) @ R('y', a('spine_side')) @ R('x', -a('spine'))
        out['torso'] = Mt
        out['head'] = Mt @ T(0, 0, p['chest']) @ R('z', a('neck_turn')) @ R('x', -a('neck'))
        sx, sz = p['sh']
        for side, sg in (('l', -1.0), ('r', 1.0)):
            Mu = (Mt @ T(sg * sx, 0, sz) @ R('y', -sg * a(f'sh_{side}_out')) @ R('x', a(f'sh_{side}'))
                  @ R('z', -sg * a(f'sh_{side}_rot')))
            out[f'uarm_{side}'] = Mu
            out[f'farm_{side}'] = Mu @ T(0, 0, -p['upper']) @ R('x', a(f'elbow_{side}'))
            Mh = M @ T(sg * p['hip'], 0, 0) @ R('y', -sg * a(f'hip_{side}_out')) @ R('x', a(f'hip_{side}'))
            out[f'thigh_{side}'] = Mh
            Ms = Mh @ T(0, 0, -p['thigh']) @ R('x', -a(f'knee_{side}'))
            out[f'shin_{side}'] = Ms
            out[f'foot_{side}'] = Ms @ T(0, 0, -p['shin']) @ R('x', a(f'ankle_{side}'))
        return out

    def _minz(self, segs, Ms, vtx=None):
        vtx = vtx or self.vtx
        return min(float((vtx[s] @ Ms[s][2, :3]).min() + Ms[s][2, 3]) for s in segs)

    def root(self, pose, at, floor=0.0, seat=None):
        """Pelvis transform for at = (x, y, yaw): lowest foot on `floor`, or seated on a surface at height `seat`."""
        x, y, yaw = at
        M0 = T(x, y, 0.0) @ R('z', -math.radians(yaw))
        Ms = self.fk(pose, M0)
        if seat is not None:
            z = seat - self._minz(('pelvis', 'thigh_l', 'thigh_r'), Ms, self.seat_vtx)
        else:
            z = (floor or 0.0) - self._minz(('foot_l', 'foot_r', 'shin_l', 'shin_r'), Ms)
        return T(0, 0, z) @ M0

    def sit_pose(self, seat, floor=0.0, base='sit'):
        """A sitting pose for a seat at height `seat`: feet flat on the floor with upright shins when the legs reach,
        otherwise thighs level and the feet dangling (a child on a bed)."""
        p = self.p
        q = pose_of(base)
        knee_h = p['shin'] + p['ankle']
        lift = -self._minz(('pelvis', 'thigh_l', 'thigh_r'), self.fk(q, np.eye(4)), self.seat_vtx)   # hip joint above seat
        sd = (seat + lift - floor - knee_h) / p['thigh']
        if sd > math.sin(math.radians(40)):
            hip, knee = 86.0, 76.0
        else:
            hip = 90.0 - math.degrees(math.asin(max(-0.6, sd)))
            knee = hip
        for s in 'lr':
            q[f'hip_{s}'], q[f'knee_{s}'], q[f'ankle_{s}'] = hip, knee, 0.0
        return q

    # -- build and animate
    def build(self, pose='stand', M=None, at=None, floor=0.0, seat=None):
        """Add the segment pieces at rest in this pose and place (at = (x, y, yaw), or M = pelvis 4x4)."""
        if M is None:
            M = self.root(pose, at or (0.0, 0.0, 0.0), floor, seat)
        self.build_pose, self.build_root = pose_of(pose), M
        self.build_at, self.build_floor, self.build_seat = at, floor, seat
        self.bind = self.fk(pose, M)
        self.bind_inv = {s: np.linalg.inv(m) for s, m in self.bind.items()}
        for s in SEGS:
            rk.add(f'{self.inst}_{s}', xform(self.local[s], self.bind[s]), self.mat)
        return self

    def transforms(self, pose, M):
        """Per-piece transforms (relative to the built rest pose) for this pose and pelvis transform."""
        Ms = self.fk(pose, M)
        return {f'{self.inst}_{s}': Ms[s] @ self.bind_inv[s] for s in SEGS}

    def animate(self, tl, pose=None, at=None, M=None, floor=None, seat=None, visible=True, pop=None, sound=0.35):
        """Register Timeline.custom functions for every segment. pose / at / M / floor / seat / visible are constants or
        functions of t (defaults: what build() used). pop = time the figure pops in (scales up from its feet, with a
        landing sound of strength `sound`); before that it is hidden."""
        val = lambda v, t: v(t) if callable(v) else v
        pose = self.build_pose if pose is None else pose
        if M is None and at is None:
            at = self.build_at
            if at is None:
                M = self.build_root
        floor = self.build_floor if floor is None else floor
        seat = self.build_seat if (seat is None and at is self.build_at) else seat
        cache = {}

        def state(t):
            if t in cache:
                return cache[t]
            vis = bool(val(visible, t)) and (pop is None or t >= pop)
            q = val(pose, t)
            Mr = val(M, t) if M is not None else self.root(q, val(at, t), val(floor, t), val(seat, t))
            rel = self.transforms(q, Mr)
            if pop is not None and t >= pop:
                tau = t - pop
                s = 0.55 + 0.45 * smooth(tau / 0.2) if tau < 0.2 else tl.settle(tau - 0.2, 0.02)
                Pv = about((Mr[0, 3], Mr[1, 3], val(floor, t) or 0.0), S(s, s, s))
                rel = {k: Pv @ m for k, m in rel.items()}
            if len(cache) > 64:
                cache.clear()
            cache[t] = (rel, vis)
            return cache[t]

        for name in self.pieces:
            tl.custom(name, lambda t, name=name: (state(t)[0][name], state(t)[1]))
        if pop is not None:
            tl.ev(pop + 0.2, self.inst, sound, 'tick')
        return self


def figure(inst, kind='adult', pose='stand', M=None, at=None, floor=0.0, seat=None, mat=None):
    """Build a stand-in person as pieces <inst>_<segment>, at rest in `pose`. Returns the Figure (call .animate later).
    kind 'adult' (about 1.68 m) or 'child' (about 1.15 m); mat defaults to fig_adult / fig_child (see COLOURS)."""
    return Figure(inst, kind, mat).build(pose, M=M, at=at, floor=floor, seat=seat)
