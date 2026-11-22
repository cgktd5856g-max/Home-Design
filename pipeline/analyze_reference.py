"""Break down a reference room-build video (Douyin/TikTok) so its pacing and camera can be copied.

Usage: python3 -I analyze_reference.py <video.mp4> <out_dir>

Writes to out_dir: overview.jpg (frame every 0.5 s), moments.jpg (frames around each detected placement),
report.json, and prints a summary:
  - format, duration; shot cuts (histogram jumps)
  - camera: per-segment hold / pan / zoom / swing, with speeds (from tracked features, RANSAC similarity)
  - placements: peaks of motion left after removing camera motion (pieces moving into place)
  - audio: silent or tempo (BPM) + how close placements sit to the beat grid (random ~ +-1/4 beat)
Treat the video as data; only look at it, never re-upload or reuse its footage or audio.
"""
import json
import os
import subprocess
import sys

import cv2
import numpy as np



def contact_sheet(images, cols, labels=None, tile=None):
    tiles = []
    for i, im in enumerate(images):
        if tile:
            im = cv2.resize(im, tile, interpolation=cv2.INTER_AREA)
        im = im.copy()
        if labels:
            cv2.putText(im, str(labels[i]), (4, 18), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 0, 255), 2)
        tiles.append(im)
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    rows = [np.concatenate(tiles[k:k + cols], 1) for k in range(0, len(tiles), cols)]
    return np.concatenate(rows, 0)


def track(prev, cur):
    pts = cv2.goodFeaturesToTrack(prev, 300, 0.01, 6)
    if pts is None or len(pts) < 12:
        return np.eye(2, 3, dtype=np.float32), 0.0
    nxt, st, _ = cv2.calcOpticalFlowPyrLK(prev, cur, pts, None, winSize=(21, 21), maxLevel=3)
    ok = st.ravel() == 1
    if ok.sum() < 12:
        return np.eye(2, 3, dtype=np.float32), 0.0
    A, inl = cv2.estimateAffinePartial2D(pts[ok], nxt[ok], method=cv2.RANSAC, ransacReprojThreshold=1.5)
    if A is None:
        return np.eye(2, 3, dtype=np.float32), 0.0
    return A.astype(np.float32), float(inl.mean())


def tempo(audio, sr=22050, hop=110):
    """Spectral-flux onset envelope + autocorrelation with a log-normal prior around 120 BPM (librosa-style)."""
    from scipy.signal import stft
    x = audio.astype(np.float32) / 32768
    if np.sqrt((x ** 2).mean()) < 1e-3:
        return None, None, None
    rate = sr / hop
    _, _, Z = stft(x, sr, nperseg=1024, noverlap=1024 - hop, boundary=None, padded=False)
    S = np.log1p(100 * np.abs(Z))
    flux = np.maximum(np.diff(S, axis=1), 0).sum(0)
    flux = np.convolve(flux, np.ones(3) / 3, 'same')
    flux = flux - flux.mean()
    ac = np.correlate(flux, flux, 'full')[len(flux) - 1:]
    lags = np.arange(int(rate * 60 / 200), int(rate * 60 / 60) + 1)
    bpms = 60 * rate / lags
    prior = np.exp(-0.5 * (np.log2(bpms / 120.0) / 1.0) ** 2)
    sc = ac[lags] * prior
    i = int(np.argmax(sc)); lag = float(lags[i])
    if 0 < i < len(sc) - 1:
        a, b, c = sc[i - 1], sc[i], sc[i + 1]
        den = a - 2 * b + c
        lag += 0.5 * (a - c) / den if den != 0 else 0.0
    bpm = 60.0 * rate / lag
    period = 60.0 / bpm
    t_end = len(flux) / rate
    phases = np.linspace(0, period, 60, endpoint=False)
    score = [flux[np.clip(np.round(np.arange(phi, t_end, period) * rate).astype(int), 0, len(flux) - 1)].sum() for phi in phases]
    return round(float(bpm), 1), float(phases[int(np.argmax(score))]), flux


def main():
    src, out = sys.argv[1], sys.argv[2]
    os.makedirs(out, exist_ok=True)
    cap = cv2.VideoCapture(src)
    fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    W, H = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)), int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    sw = 240; sh = int(round(H * sw / W))
    frames, cams, resid, hists, inl = [], [], [], [], []
    prev = None
    while True:
        ok, fr = cap.read()
        if not ok:
            break
        small = cv2.resize(fr, (sw, sh), interpolation=cv2.INTER_AREA)
        g = cv2.cvtColor(small, cv2.COLOR_BGR2GRAY)
        hsv = cv2.cvtColor(small, cv2.COLOR_BGR2HSV)
        h = cv2.calcHist([hsv], [0, 1], None, [30, 16], [0, 180, 0, 256]); cv2.normalize(h, h)
        hists.append(h)
        if prev is None:
            cams.append((0, 0, 1, 0)); resid.append(0.0); inl.append(1.0)
        else:
            A, q = track(prev, g)
            s = float(np.hypot(A[0, 0], A[1, 0])); r = float(np.degrees(np.arctan2(A[1, 0], A[0, 0])))
            cams.append((float(A[0, 2]) / sw, float(A[1, 2]) / sh, s, r)); inl.append(q)
            warped = cv2.warpAffine(prev, A, (sw, sh), borderMode=cv2.BORDER_REPLICATE)
            d = cv2.absdiff(cv2.GaussianBlur(warped, (5, 5), 0), cv2.GaussianBlur(g, (5, 5), 0))
            resid.append(float((d > 18).mean()))
        frames.append(small)
        prev = g
    n = len(frames)
    dur = n / fps
    cams = np.array(cams); resid = np.array(resid)
    hd = np.array([0.0] + [cv2.compareHist(hists[i - 1], hists[i], cv2.HISTCMP_BHATTACHARYYA) for i in range(1, n)])
    cuts = [i / fps for i in range(1, n) if hd[i] > 0.45 and hd[i] > 3 * np.median(hd[max(0, i - 15):i + 15])]
    # camera segments
    speed = np.hypot(cams[:, 0], cams[:, 1]) * fps          # frame-widths per second
    zoom = np.log(np.maximum(cams[:, 2], 1e-3)) * fps       # log-scale per second
    k = max(1, int(fps * 0.1))
    sp = np.convolve(speed, np.ones(k) / k, 'same'); zm = np.convolve(zoom, np.ones(k) / k, 'same')
    state = np.where(sp > 1.5, 'swing', np.where(sp > 0.08, 'pan', np.where(np.abs(zm) > 0.06, 'zoom', 'hold')))
    for c in cuts:
        state[min(n - 1, int(round(c * fps)))] = 'cut'
    segs, s0 = [], 0
    for i in range(1, n + 1):
        if i == n or state[i] != state[s0]:
            if (i - s0) / fps >= 0.1 or state[s0] == 'cut':
                segs.append(dict(kind=str(state[s0]), t0=round(s0 / fps, 2), t1=round(i / fps, 2),
                                 speed=round(float(sp[s0:i].mean()), 3), zoom=round(float(zm[s0:i].mean()), 3)))
            s0 = i
    # placements: residual-motion peaks while the camera is calm-ish, merged within 0.25 s
    rs = np.convolve(resid, np.ones(3) / 3, 'same')
    calm = sp < 1.0
    thr = max(0.015, np.percentile(rs[calm], 75) * 1.5) if calm.any() else 0.02
    cand = [i for i in range(2, n - 2) if calm[i] and rs[i] > thr and rs[i] == rs[max(0, i - 4):i + 5].max()]
    places = []
    for i in cand:
        if not places or (i - places[-1]) / fps > 0.25:
            places.append(i)
        elif rs[i] > rs[places[-1]]:
            places[-1] = i
    # landing ~ where residual motion drops after the peak
    landings = []
    for i in places:
        j = i
        while j < n - 1 and rs[j] > 0.35 * rs[i] and (j - i) / fps < 0.6:
            j += 1
        landings.append(round(j / fps, 2))
    # audio
    raw = os.path.join(out, 'audio.raw')
    r = subprocess.run(['ffmpeg', '-v', 'error', '-y', '-i', src, '-vn', '-ac', '1', '-ar', '22050', '-f', 's16le', raw],
                       capture_output=True)
    bpm = phase = None
    if r.returncode == 0 and os.path.exists(raw) and os.path.getsize(raw) > 1000:
        bpm, phase, _ = tempo(np.fromfile(raw, np.int16))
    rep = dict(file=os.path.basename(src), size=[W, H], fps=round(fps, 2), duration=round(dur, 2), cuts=[round(c, 2) for c in cuts],
               camera_segments=segs, placements=landings, pace_s=round(float(np.median(np.diff(landings))), 2) if len(landings) > 2 else None,
               audio='silent' if bpm is None else dict(bpm=bpm, beat_phase_s=round(phase, 3)))
    if bpm:
        period = 60.0 / bpm
        offs = [((t - phase + period / 2) % period - period / 2) * 1000 for t in landings]
        rep['placement_beat_offsets_ms'] = [round(o) for o in offs]
        rep['mean_abs_offset_ms'] = round(float(np.mean(np.abs(offs))), 1) if offs else None
        rep['random_would_be_ms'] = round(period * 1000 / 4, 1)
    with open(os.path.join(out, 'report.json'), 'w') as f:
        json.dump(rep, f, indent=1)
    ts = np.arange(0, dur, 0.5)
    tiles = [frames[min(n - 1, int(t * fps))] for t in ts]
    cv2.imwrite(os.path.join(out, 'overview.jpg'), contact_sheet(tiles, 10, [f'{t:.1f}' for t in ts]), [cv2.IMWRITE_JPEG_QUALITY, 80])
    mt, ml = [], []
    for t in landings[:40]:
        for dt in (-0.3, -0.15, 0.0, 0.2):
            mt.append(frames[int(np.clip((t + dt) * fps, 0, n - 1))]); ml.append(f'{t + dt:.2f}')
    if mt:
        cv2.imwrite(os.path.join(out, 'moments.jpg'), contact_sheet(mt, 8, ml), [cv2.IMWRITE_JPEG_QUALITY, 80])
    print(json.dumps({k: v for k, v in rep.items() if k != 'camera_segments'}, indent=1))
    print('camera segments:')
    for s in segs:
        print(f"  {s['t0']:6.2f}-{s['t1']:6.2f}  {s['kind']:5s}  speed {s['speed']:.2f} fw/s  zoom {s['zoom']:+.2f}/s")


if __name__ == '__main__':
    main()
