"""roomkit: describe a room and its furniture as triangle meshes for the path tracer (pt.cpp).

Units: metres. x = east, y = north, z = up. Mesh vertices are written in their REST (final) world position;
each named piece ("instance") then gets a per-frame 4x4 transform from animkit (identity = at rest), so
procedural textures stick to the piece while it moves.

    import roomkit as rk
    rk.mat('wall', tex=3, col=rk.srgb(192, 187, 182), p=(0.055,))
    rk.wood_mats('oak', rk.srgb(216, 192, 160))
    rk.add('room', rk.box(-0.2, -0.2, -0.1, W + 0.2, D + 0.2, 0), 'floor')
    rk.wood('desk', 0, 2.85, 0.75, 1.20, D, 0.78)          # box with the grain along its longest side
    rk.write_scene('scene.bin')

Material texture types (tex=, params p=):
  0 solid colour                         1 floor planks along y (p: plank width, plank length; col, col2)
  2 wood board (p: grain axis 0/1/2, seed)   3 wallpaper speckle (p: amplitude)
  4 roman blind folds (p: fold spacing; emis = back-light)    5 knit ribs (p: axis, rib spacing)
  6 boucle                               7 stripes (p: axis, period; col, col2)
  8 monitor screen, emissive (p: x0, width, z0, height of the screen in rest coords; faces -y)
  9 window backdrop: hazy sky + skyline + trees, emissive (p: horizon height)
  10 keyboard key grid (p: key pitch)
  11 marble (p: scale, vein width, seed, vein strength; col base, col2 veins)
  12 tiles + grout (p: tile u, tile v, grout width, plane normal axis 0/1/2, row offset; col tile, col2 grout)
  13 cement floor tile with four-petal flowers (p: tile size, flower radius, grout, diamond size; col, col2, col3)
  14 brushed metal (p: brushing axis)        15 quartz with flecks (p: fleck scale, threshold; col, col2 flecks)
Other material fields: rough, f0 (0 = pure diffuse), metal, emis (camera-visible glow), glossy=True (trace a
separate mirror-ish lobe at the first hit: floors, black plastic).
"""
import math
import struct

import numpy as np

MATS, MATIDX = [], {}
INST, ORDER = {}, []


def reset():
    MATS.clear(); MATIDX.clear(); INST.clear(); ORDER.clear()


def srgb(r, g, b):
    c = np.array([r, g, b], np.float64) / 255.0
    return tuple(np.where(c <= 0.04045, c / 12.92, ((c + 0.055) / 1.055) ** 2.4))


def mat(name, tex=0, col=(0.5, 0.5, 0.5), col2=(0, 0, 0), rough=0.6, f0=0.0, metal=0, emis=(0, 0, 0), p=(), glossy=False, col3=(0, 0, 0)):
    assert len(p) <= 6, 'at most 6 texture params (slots 13..18)'
    rec = np.zeros(24, np.float32)
    rec[20:23] = col3
    rec[0] = tex; rec[1:4] = col; rec[4:7] = col2; rec[7] = rough; rec[8] = f0; rec[9] = metal; rec[10:13] = emis
    for i, v in enumerate(p):
        rec[13 + i] = v
    rec[19] = 1 if glossy else 0
    MATIDX[name] = len(MATS)
    MATS.append(rec)


def wood_mats(name, col, seed=1.0):
    """Register name_x / name_y / name_z (grain along each axis) for rk.wood()."""
    for i, ax in enumerate('xyz'):
        mat(f'{name}_{ax}', tex=2, col=col, p=(i, seed + i))


def add(inst, PN, m):
    """Add triangles (P, N) with material m to the named piece."""
    P, N = PN
    if inst not in INST:
        INST[inst] = []
        ORDER.append(inst)
    INST[inst].append((np.asarray(P, np.float32).reshape(-1, 3, 3), np.asarray(N, np.float32).reshape(-1, 3, 3), MATIDX[m]))


def bounds(inst):
    P = np.concatenate([p[0].reshape(-1, 3) for p in INST[inst]])
    return P.min(0), P.max(0)


# ------------------------------------------------------------------------------------------- primitives
def box(x0, y0, z0, x1, y1, z1):
    v = np.array([[x0, y0, z0], [x1, y0, z0], [x1, y1, z0], [x0, y1, z0], [x0, y0, z1], [x1, y0, z1], [x1, y1, z1], [x0, y1, z1]], np.float64)
    faces = [(0, 3, 2, 1, (0, 0, -1)), (4, 5, 6, 7, (0, 0, 1)), (0, 1, 5, 4, (0, -1, 0)), (2, 3, 7, 6, (0, 1, 0)), (1, 2, 6, 5, (1, 0, 0)), (3, 0, 4, 7, (-1, 0, 0))]
    P, N = [], []
    for a, b, c, d, n in faces:
        P += [[v[a], v[b], v[c]], [v[a], v[c], v[d]]]
        N += [[n, n, n], [n, n, n]]
    return np.array(P), np.array(N, np.float64)


def grid_tris(V, Nn=None, closed_u=False, closed_v=False):
    """Triangles from a (nu, nv, 3) vertex grid; smooth normals are computed if Nn is None."""
    nu, nv = V.shape[:2]
    if Nn is None:
        def diff(A, axis, closed):
            return np.roll(A, -1, axis) - np.roll(A, 1, axis) if closed else np.gradient(A, axis=axis)
        Nn = np.cross(diff(V, 0, closed_u), diff(V, 1, closed_v))
        Nn /= (np.linalg.norm(Nn, axis=2, keepdims=True) + 1e-12)
    iu = list(range(nu)) if closed_u else list(range(nu - 1))
    jv = list(range(nv)) if closed_v else list(range(nv - 1))
    P, N = [], []
    for i in iu:
        i2 = (i + 1) % nu
        for j in jv:
            j2 = (j + 1) % nv
            P += [[V[i, j], V[i2, j], V[i2, j2]], [V[i, j], V[i2, j2], V[i, j2]]]
            N += [[Nn[i, j], Nn[i2, j], Nn[i2, j2]], [Nn[i, j], Nn[i2, j2], Nn[i, j2]]]
    return np.array(P), np.array(N)


def lathe(prof, n=32, c=(0.0, 0.0), a0=0.0, a1=2 * math.pi):
    """Revolve a (radius, z) profile about the vertical axis through c."""
    prof = np.array(prof, float)
    tang = np.gradient(prof, axis=0)
    nr, nz = tang[:, 1].copy(), -tang[:, 0].copy()
    l = np.hypot(nr, nz) + 1e-12
    nr /= l; nz /= l
    closed = abs((a1 - a0) - 2 * math.pi) < 1e-6
    angs = np.linspace(a0, a1, n, endpoint=not closed)
    V = np.zeros((len(angs), len(prof), 3)); Nn = np.zeros_like(V)
    for i, a in enumerate(angs):
        ca, sa = math.cos(a), math.sin(a)
        V[i, :, 0] = c[0] + prof[:, 0] * ca; V[i, :, 1] = c[1] + prof[:, 0] * sa; V[i, :, 2] = prof[:, 1]
        Nn[i, :, 0] = nr * ca; Nn[i, :, 1] = nr * sa; Nn[i, :, 2] = nz
    return grid_tris(V, Nn, closed_u=closed)


def rprof(r, z0, z1, rad, k=6):
    """Lathe profile of a disc with a rounded rim (cushions, lamp bases)."""
    pts = [(0.0, z0), (max(r - rad, 0.0) * 0.5, z0)]
    for i in range(k + 1):
        a = -math.pi / 2 + (math.pi / 2) * i / k
        pts.append((r - rad + rad * math.cos(a), z0 + rad + rad * math.sin(a)))
    for i in range(k + 1):
        a = (math.pi / 2) * i / k
        pts.append((r - rad + rad * math.cos(a), z1 - rad + rad * math.sin(a)))
    pts += [(max(r - rad, 0.0) * 0.5, z1), (0.0, z1)]
    return pts


def tube(points, r, n=12, caps=True):
    """Sweep a circle along a polyline (legs, stems, rails). r may be a list (taper)."""
    pts = np.array(points, float)
    m = len(pts)
    rr = np.full(m, r, float) if np.isscalar(r) else np.array(r, float)
    tang = np.gradient(pts, axis=0)
    tang /= (np.linalg.norm(tang, axis=1, keepdims=True) + 1e-12)
    ref = np.array([0, 0, 1.0]) if abs(tang[0, 2]) < 0.9 else np.array([1.0, 0, 0])
    u = np.cross(tang[0], ref); u /= np.linalg.norm(u)
    V = np.zeros((m, n, 3)); Nn = np.zeros_like(V)
    for i in range(m):
        u = u - tang[i] * np.dot(u, tang[i]); u /= (np.linalg.norm(u) + 1e-12)
        v = np.cross(tang[i], u)
        for j in range(n):
            a = 2 * math.pi * j / n
            d = u * math.cos(a) + v * math.sin(a)
            V[i, j] = pts[i] + d * rr[i]; Nn[i, j] = d
    P, N = grid_tris(V, Nn, closed_v=True)
    if caps:
        P = list(P); N = list(N)
        for i, sgn in ((0, -1.0), (m - 1, 1.0)):
            nn = tang[i] * sgn
            for j in range(n):
                P.append([pts[i], V[i, j], V[i, (j + 1) % n]]); N.append([nn, nn, nn])
        P = np.array(P); N = np.array(N)
    return P, N


def ellipsoid(c, rad, n=14):
    c = np.array(c, float); rad = np.array(rad, float)
    nu, nv = n * 2, n + 1
    V = np.zeros((nu, nv, 3)); Nn = np.zeros_like(V)
    for i in range(nu):
        ph = 2 * math.pi * i / nu
        for j in range(nv):
            th = math.pi * j / (nv - 1)
            d = np.array([math.sin(th) * math.cos(ph), math.sin(th) * math.sin(ph), -math.cos(th)])
            V[i, j] = c + d * rad
            nn = d / rad; Nn[i, j] = nn / np.linalg.norm(nn)
    return grid_tris(V, Nn, closed_u=True)


def rbox(c, size, rad, n=5):
    """Rounded box (soft things: folded clothes, cushions, mattresses). n must be odd."""
    c = np.array(c, float); h = np.array(size, float) / 2.0
    rad = min(rad, float(h.min()) * 0.999)
    hin = h - rad
    lin = np.linspace(-1, 1, n + 1)
    P, N = [], []
    for ax in range(3):
        for sg in (-1.0, 1.0):
            V = np.zeros((n + 1, n + 1, 3)); Nn = np.zeros_like(V)
            a1, a2 = (ax + 1) % 3, (ax + 2) % 3
            for i, u in enumerate(lin):
                for j, v in enumerate(lin):
                    d = np.zeros(3); d[ax] = sg; d[a1] = u; d[a2] = v
                    d /= np.linalg.norm(d)
                    V[i, j] = c + rad * d + hin * np.sign(d); Nn[i, j] = d
            p, nn = grid_tris(V, Nn)
            P.append(p); N.append(nn)
    return np.concatenate(P), np.concatenate(N)


def wood(inst, x0, y0, z0, x1, y1, z1, name='oak'):
    """Box whose wood grain runs along its longest side (needs wood_mats(name, ...))."""
    ax = int(np.argmax((x1 - x0, y1 - y0, z1 - z0)))
    add(inst, box(x0, y0, z0, x1, y1, z1), f'{name}_{"xyz"[ax]}')


# ------------------------------------------------------------------------------------------- transforms
def T(x, y, z):
    M = np.eye(4); M[:3, 3] = (x, y, z); return M


def S(sx, sy, sz):
    return np.diag([sx, sy, sz, 1.0])


def R(axis, a):
    c, s = math.cos(a), math.sin(a)
    M = np.eye(4)
    i, j = {'x': (1, 2), 'y': (2, 0), 'z': (0, 1)}[axis]
    M[i, i] = c; M[i, j] = -s; M[j, i] = s; M[j, j] = c
    return M


def about(p, M):
    return T(*p) @ M @ T(-p[0], -p[1], -p[2])


def xform(PN, M):
    """Bake a transform into a mesh (for placing rotated parts at build time)."""
    P, N = PN
    A = M[:3, :3]
    P2 = P @ A.T + M[:3, 3]
    N2 = N @ np.linalg.inv(A)
    return P2, N2 / (np.linalg.norm(N2, axis=-1, keepdims=True) + 1e-12)


# ------------------------------------------------------------------------------------------- camera / lights
def cam_record(pos, yaw, pitch, vfov=85.0):
    """yaw in degrees east of north (0 = looking +y), pitch up, vfov = vertical field of view."""
    y, p = math.radians(yaw), math.radians(pitch)
    d = np.array([math.sin(y) * math.cos(p), math.cos(y) * math.cos(p), math.sin(p)])
    tgt = np.array(pos) + d
    return [pos[0], pos[1], pos[2], tgt[0], tgt[1], tgt[2], 0, 0, 1, vfov, 0, 0]


def rect_light(corner, eu, ev, L, axis=(0, 0, 0), spot=0.0, always=0):
    """Rectangle light. It shines toward cross(eu, ev) - check the sign! spot > 0 adds a cos^spot beam around axis.
    always=1: sampled at every bounce (use for the main window); other lights are picked by importance."""
    return [0, *corner, *eu, *ev, *L, *axis, spot, always, 0, 0]


def sphere_light(c, r, L):
    return [1, *c, r, 0, 0, 0, 0, 0, *L, 0, 0, 1, 0, 0, 0, 0]


def spot_rect(center, axis, size, L, spot=10.0):
    """Small square light at center facing along axis (ceiling spotlights)."""
    a = np.array(axis, float); a /= np.linalg.norm(a)
    ref = np.array([0, 1.0, 0]) if abs(a[1]) < 0.9 else np.array([1.0, 0, 0])
    u = np.cross(a, ref); u /= np.linalg.norm(u); v = np.cross(u, a)
    c = np.array(center, float) - u * size / 2 - v * size / 2
    eu, ev = u * size, v * size
    if np.dot(np.cross(eu, ev), a) < 0:
        eu, ev = ev, eu
    return rect_light(tuple(c), tuple(eu), tuple(ev), L, tuple(a), spot)


# ------------------------------------------------------------------------------------------- writers
def write_scene(path='scene.bin'):
    with open(path, 'wb') as f:
        f.write(struct.pack('<iii', 0x43535450, len(MATS), len(ORDER)))
        f.write(np.array(MATS, np.float32).tobytes())
        total = 0
        for name in ORDER:
            parts = INST[name]
            n = sum(len(p[0]) for p in parts)
            total += n
            f.write(struct.pack('<i', n))
            rec = np.zeros(n, dtype=[('p', '<f4', 9), ('n', '<f4', 9), ('m', '<i4')])
            k = 0
            for P, N, m in parts:
                rec['p'][k:k + len(P)] = P.reshape(-1, 9); rec['n'][k:k + len(P)] = N.reshape(-1, 9); rec['m'][k:k + len(P)] = m
                k += len(P)
            f.write(rec.tobytes())
    print('scene:', len(MATS), 'materials,', len(ORDER), 'pieces,', total, 'triangles')


def write_frames(records, path='frames.bin'):
    """records: list of dict(cam=[12 floats], mats={piece: 4x4}, vis={piece: 0 hidden | 1 visible | 2 visible and moving},
    lights=[[20 floats], ...])"""
    with open(path, 'wb') as f:
        f.write(struct.pack('<i', len(records)))
        for r in records:
            f.write(np.array(r['cam'], np.float32).tobytes())
            xf = np.zeros((len(ORDER), 13), np.float32)
            for i, name in enumerate(ORDER):
                M = r['mats'].get(name, np.eye(4))
                xf[i, :12] = M[:3, :].reshape(-1)
                xf[i, 12] = float(r['vis'].get(name, True))
            f.write(xf.tobytes())
            L = np.array(r['lights'], np.float32).reshape(-1, 20)
            f.write(struct.pack('<i', len(L)))
            f.write(L.tobytes())
