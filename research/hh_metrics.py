#!/usr/bin/env python3
"""Measure a room-build video the same way the Haven Haus hits and flops were measured.

Usage:
    python3 research/hh_metrics.py out/kitchen_build.mp4 [more.mp4 ...]
    python3 research/hh_metrics.py --json out/kitchen_build.mp4

Every 0.2 s the video is shrunk to 45x80 pixels (the same grid the browser analysis used on YouTube), and
each frame gives brightness, saturation, warmth (red minus blue) and the change from the previous frame.
The targets are the middle range of 25 Haven Haus hits, each paired with a flop from the same weeks
(see report.md, section 13). Needs ffmpeg and numpy.
"""
import json
import subprocess
import sys

import numpy as np

STEP, W, H = 0.2, 45, 80

# metric: (low, high, what it means). Ranges are the hits' 25th-75th percentile unless noted.
TARGETS = {
    'dmed': (7.5, None, 'motion: median change per 0.2 s (hits 8.4, flops 5.1)'),
    's10': (0.39, None, 'share of 0.2 s steps with a clear change (hits 0.43, flops 0.35)'),
    'calm': (None, 1.8, 'longest near-still stretch in seconds (hits 1.4, flops 2.6)'),
    'camera': (1.8, None, 'camera movement: change in the quietest tiles per 0.4 s (hits 2.9, flops 1.0)'),
    'fb': (None, 0.4, 'first clear movement in seconds'),
    'lum': (138, 178, 'mean brightness 0-255 (hits 10th-90th percentile)'),
    'sat': (0.17, 0.38, 'mean saturation (hits 10th-90th percentile; flops run warmer and more saturated)'),
    'warm': (22, 57, 'mean red minus blue (hits 10th-90th percentile; above 60: cream or orange cast)'),
    'len': (34, 46, 'seconds, for the long cut (hits 25th-75th percentile; the 15 s cut is a separate test)'),
}


def frames(path):
    cmd = ['ffmpeg', '-v', 'error', '-i', path, '-vf', f'fps={1 / STEP},scale={W}:{H}:flags=bilinear',
           '-f', 'rawvideo', '-pix_fmt', 'rgb24', '-']
    raw = subprocess.run(cmd, capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W, 3).astype(np.float32)


def samples(fr):
    out, prev, prev_h = [], None, None
    n_px = W * H
    for i, f in enumerate(fr):
        r, g, b = f[..., 0], f[..., 1], f[..., 2]
        y = 0.299 * r + 0.587 * g + 0.114 * b
        mx, mn = f.max(-1), f.min(-1)
        sat = np.where(mx > 0, (mx - mn) / np.maximum(mx, 1e-9), 0)
        hist = np.bincount(np.minimum(15, y.astype(np.int32) >> 4).ravel(), minlength=16).astype(np.float64)
        edge = (np.abs(y[:-1, 1:] - y[:-1, :-1]) + np.abs(y[1:, :-1] - y[:-1, :-1])).mean()
        df = hd = 0.0
        if prev is not None:
            df = float(np.abs(y - prev).mean())
            hd = float(np.abs(hist - prev_h).sum() / n_px)
        out.append(dict(t=round(i * STEP, 2), lum=float(y.mean()), sat=float(sat.mean()),
                        warm=float((r - b).mean()), edge=float(edge), df=df, hd=hd))
        prev, prev_h = y, hist
    return out


def summary(S):
    n = len(S)
    a = 0
    while a < n and S[a]['lum'] < 25:  # leading black
        a += 1
    z = n - 1
    while z > a and S[z]['lum'] < 40 and S[z]['sat'] < 0.35:  # trailing black end card
        z -= 1
    C = S[a:z + 1]
    m = len(C)
    cuts = []
    for i in range(a + 1, z + 1):
        if S[i]['df'] > 22 and S[i]['hd'] > 0.25 and (not cuts or S[i]['t'] - cuts[-1] > 0.6):
            cuts.append(S[i]['t'])
    dfs = sorted(s['df'] for s in C[1:])
    run = calm = 0
    first = None
    for i in range(1, m):
        run = run + 1 if C[i]['df'] < 4 else 0
        calm = max(calm, run)
        if first is None and C[i]['df'] > 10:
            first = C[i]['t']
    mean = lambda k: sum(s[k] for s in C) / m
    return dict(len=round(n * STEP, 1), cuts=len(cuts), dmed=round(dfs[(len(dfs) - 1) // 2], 1),
                s10=round(sum(x > 10 for x in dfs) / len(dfs), 2), calm=round(calm * STEP, 1), fb=first,
                lum=round(mean('lum')), sat=round(mean('sat'), 2), warm=round(mean('warm'), 1),
                cut_times=' '.join(f'{x:.1f}' for x in cuts))


def camera(fr):
    """Median change, per 0.4 s, in the quietest quarter of a 3x4 tile grid. A locked-off camera keeps those tiles
    near zero even while pieces fly in; a gliding camera moves every tile."""
    fr = fr[::2]  # 0.2 s frames -> 0.4 s steps, as measured on YouTube
    y = 0.299 * fr[..., 0] + 0.587 * fr[..., 1] + 0.114 * fr[..., 2]
    quiet = []
    for i in range(1, len(y)):
        if y[i].mean() < 40:  # black frames and end cards
            continue
        d = np.abs(y[i] - y[i - 1])
        tiles = sorted(d[r * 20:(r + 1) * 20, c * 15:(c + 1) * 15].mean() for r in range(4) for c in range(3))
        quiet.append(tiles[2])
    quiet.sort()
    return round(float(quiet[(len(quiet) - 1) // 2]), 2) if quiet else None


def check(res):
    lines = []
    for k, (lo, hi, what) in TARGETS.items():
        v = res.get(k)
        ok = v is not None and (lo is None or v >= lo) and (hi is None or v <= hi)
        rng = f"{'' if lo is None else lo}-{'' if hi is None else hi}"
        lines.append(f"  {'ok ' if ok else 'OFF'} {k:5s} {v!s:>6}  target {rng:<10} {what}")
    return '\n'.join(lines)


if __name__ == '__main__':
    args = [a for a in sys.argv[1:] if a != '--json']
    if not args:
        sys.exit(__doc__)
    for p in args:
        fr = frames(p)
        res = summary(samples(fr))
        res['camera'] = camera(fr)
        if '--json' in sys.argv:
            print(json.dumps({'file': p, **res}))
        else:
            print(p)
            print(check(res))
