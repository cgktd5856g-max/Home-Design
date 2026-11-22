"""Bake roomkit procedural textures (same maths as pt.cpp) into numpy images for Blender.

All colours are linear RGB. Images are returned as (rows, cols, 3) float32 with row 0 at the BOTTOM
(Blender's image origin), sampled over a rectangle of the material's rest-space plane.
"""
import numpy as np

U = np.uint32


def _pcg(v):
    s = v * U(747796405) + U(2891336453)
    w = ((s >> ((s >> U(28)) + U(4))) ^ s) * U(277803737)
    return (w >> U(22)) ^ w


def _u32(a):
    return np.asarray(a).astype(np.int64).astype(np.uint32)


def hashf(x, y, z):
    with np.errstate(over='ignore'):
        h = (_u32(x) * U(73856093)) ^ (_u32(y) * U(19349663)) ^ (_u32(z) * U(83492791))
        h = _pcg(h)
    return (h >> U(8)).astype(np.float32) * np.float32(1.0 / 16777216.0)


def vnoise(px, py, pz):
    px, py, pz = (np.asarray(a, np.float64) for a in (px, py, pz))
    px, py, pz = np.broadcast_arrays(px, py, pz)
    fx, fy, fz = np.floor(px), np.floor(py), np.floor(pz)
    ix, iy, iz = fx.astype(np.int64), fy.astype(np.int64), fz.astype(np.int64)
    tx, ty, tz = px - fx, py - fy, pz - fz
    tx = tx * tx * (3 - 2 * tx); ty = ty * ty * (3 - 2 * ty); tz = tz * tz * (3 - 2 * tz)
    c000, c100 = hashf(ix, iy, iz), hashf(ix + 1, iy, iz)
    c010, c110 = hashf(ix, iy + 1, iz), hashf(ix + 1, iy + 1, iz)
    c001, c101 = hashf(ix, iy, iz + 1), hashf(ix + 1, iy, iz + 1)
    c011, c111 = hashf(ix, iy + 1, iz + 1), hashf(ix + 1, iy + 1, iz + 1)
    a = c000 + (c100 - c000) * tx; b = c010 + (c110 - c010) * tx
    c = c001 + (c101 - c001) * tx; d = c011 + (c111 - c011) * tx
    e = a + (b - a) * ty; f = c + (d - c) * ty
    return e + (f - e) * tz


def fbm(px, py, pz, octaves):
    a, s, n = 0.5, 0.0, 0.0
    for _ in range(octaves):
        s = s + a * vnoise(px, py, pz); n += a
        px, py, pz = px * 2.03, py * 2.03, pz * 2.03; a *= 0.5
    return s / n


def _plane(rect, axes, fixed, res):
    """rect = (u0, u1, v0, v1) on rest axes (au, av); fixed = (axis, value). Returns x, y, z arrays (rows, cols)."""
    u0, u1, v0, v1 = rect
    nu, nv = res
    uu = u0 + (np.arange(nu) + 0.5) / nu * (u1 - u0)
    vv = v0 + (np.arange(nv) + 0.5) / nv * (v1 - v0)
    V, Uu = np.meshgrid(vv, uu, indexing='ij')           # row = v (bottom first), col = u
    P = [None, None, None]
    P[axes[0]] = Uu; P[axes[1]] = V; P[fixed[0]] = np.full_like(Uu, fixed[1])
    return P


def marble(P, rec):
    c, c2 = rec[1:4], rec[4:7]
    sc, vw, seed, vd = rec[13], rec[14], rec[15], rec[16]
    qx, qy, qz = P[0] * sc + seed * 3.1, P[1] * sc + seed * 1.7, P[2] * sc + seed * 2.3
    w1 = fbm(qx * 0.8, qy * 0.8, qz * 0.8, 5)
    w2 = fbm(qx * 2.4 + 5.2, qy * 2.4 + 1.3, qz * 2.4 + 2.8, 4)
    t = qx * 0.6 + qy * 0.55 + qz * 0.8 + 2.8 * w1 + 0.7 * w2
    v = np.abs(np.sin(t * 1.7))
    thick = vw * (0.25 + 1.0 * fbm(qx * 0.45 + 11, qy * 0.45 + 3, qz * 0.45 + 6, 3))
    ev = np.clip(1 - v / thick, 0, 1)
    vein = np.clip(ev * ev * (3 - 2 * ev) * 1.5, 0, 1)
    t2 = (qy * 0.9 - qx * 0.4 - qz * 0.5) * 1.3 + 2.2 * fbm(qx * 1.5 + 9.1, qy * 1.5 + 4.4, qz * 1.5 + 7.7, 4)
    v2 = np.abs(np.sin(t2 * 2.6))
    vein2 = np.clip(1 - v2 / (vw * 0.22), 0, 1) ** 1.2 * 0.55
    cloud = fbm(qx * 0.7 + 2, qy * 0.7 + 8, qz * 0.7 + 1, 3)
    k = np.clip(np.maximum(vein, vein2) * vd, 0, 1)[..., None]
    base = np.asarray(c)[None, None] * (0.95 + 0.07 * (cloud - 0.5))[..., None]
    return base * (1 - k) + np.asarray(c2)[None, None] * k


def floor_tile(P, rec):
    c, c2, c3 = np.asarray(rec[1:4]), np.asarray(rec[4:7]), np.asarray(rec[20:23])
    ts, fr, gw, dm = rec[13], rec[14], rec[15], rec[16]
    x, y, z = P
    fx, fy = x / ts, y / ts
    ix, iy = np.floor(fx), np.floor(fy)
    rx, ry = fx - ix, fy - iy
    tone = hashf(ix, iy, 31)
    alb = c[None, None] * (0.975 + 0.035 * tone + 0.03 * (fbm(x * 25, y * 25, z * 25, 2) - 0.5))[..., None]
    g = np.minimum(np.minimum(rx, 1 - rx) * ts, np.minimum(ry, 1 - ry) * ts)
    alb = np.where((g < gw * 0.5)[..., None], c[None, None] * 0.84, alb)
    cxn, cyn = np.floor(fx + 0.5), np.floor(fy + 0.5)
    dx, dy = x - cxn * ts, y - cyn * ts
    r, th = np.hypot(dx, dy), np.arctan2(dy, dx)
    rr = fr * (0.20 + 0.80 * np.abs(np.cos(2 * th)) ** 0.6)
    a = ((cxn.astype(np.int64) + cyn.astype(np.int64)) & 1) == 0
    n160 = vnoise(x * 160, y * 160, z * 160)
    fl = np.where(a[..., None], c2[None, None], c3[None, None]) * (0.92 + 0.12 * n160)[..., None]
    fl = np.where((r < fr * 0.15)[..., None], fl * 0.78, fl)
    alb = np.where((r < rr)[..., None], fl, alb)
    d1 = np.abs(x - (ix + 0.5) * ts) + np.abs(y - cyn * ts)
    d2 = np.abs(x - cxn * ts) + np.abs(y - (iy + 0.5) * ts)
    alb = np.where((np.minimum(d1, d2) < dm)[..., None], c3[None, None] * (0.95 + 0.1 * n160)[..., None], alb)
    grout = (g < gw * 0.5).astype(np.float32)
    return alb, grout


def backdrop(P, rec):
    x, z = P[0], P[2]
    hz = rec[13]
    t = np.clip((z - hz) / 2.2, 0, 1)[..., None]
    sky = np.array([1.0, 1.0, 1.0]) * (1 - t) + np.array([0.66, 0.78, 1.0]) * t
    col = sky.copy()
    bi = np.floor(x / 0.11)
    bh = 0.06 + 0.34 * hashf(bi, 5, 2) ** 2.2 + 0.10 * vnoise(x * 0.8, 1.0, 2.0)
    col = np.where((z < hz + bh)[..., None], np.array([0.58, 0.65, 0.76]) * 0.9 + sky * 0.1, col)
    bi2 = np.floor((x + 0.05) / 0.19)
    bh2 = 0.02 + 0.20 * hashf(bi2, 9, 4)
    col = np.where((z < hz + bh2)[..., None], np.array([0.44, 0.51, 0.62]) * 0.92 + sky * 0.08, col)
    th = hz - 0.02 + 0.30 * fbm(x * 2.3, 3.0, 1.0, 3) + 0.05 * vnoise(x * 22, 0.0, 5.0)
    s = (0.75 + 0.5 * vnoise(x * 30, z * 30, 2.0))[..., None]
    col = np.where((z < th)[..., None], np.array([0.20, 0.29, 0.21]) * s * 0.9 + sky * 0.1, col)
    return col


def bake(tex, rec, rect, axes, fixed, res):
    P = _plane(rect, axes, fixed, res)
    if tex == 11:
        return marble(P, rec), None
    if tex == 13:
        return floor_tile(P, rec)
    if tex == 9:
        return backdrop(P, rec), None
    raise ValueError(f'no baker for tex {tex}')
