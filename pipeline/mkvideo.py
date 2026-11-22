"""Denoised HDR frames -> graded MP4 (tonemap, bloom, landing punch, swing blur, music).

usage: mkvideo.py <workdir> <dn prefix> <out.mp4> <W> <H> [audio.wav]
Reads <workdir>/frames.json. Frames rendered smaller than W x H are enlarged with Lanczos.
"""
import json, math, os, subprocess, sys
import numpy as np, cv2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from post import load_dn, grade, to_bgr8

workdir, prefix, out, OW, OH = sys.argv[1], sys.argv[2], sys.argv[3], int(sys.argv[4]), int(sys.argv[5])
audio = sys.argv[6] if len(sys.argv) > 6 else None
j = json.load(open(os.path.join(workdir, 'frames.json')))
fps, events = j['fps'], j['events']


def punch(t):
    """Small zoom pulse and vertical shake at every landing (base zoom 1.2% hides the shifted edges)."""
    s, dy = 1.012, 0.0
    for e in events:
        tau = t - e['t']
        if 0 <= tau < 0.6:
            a = e['strength']
            s += a * 0.011 * math.exp(-tau / 0.11)
            dy -= a * 5.0 * math.exp(-tau / 0.08) * math.sin(2 * math.pi * tau / 0.14)
    return s, dy


tmp = out[:-4] + '.tmp.mp4'
cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{OW}x{OH}', '-r', str(fps), '-i', '-']
if audio:
    cmd += ['-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100',
            '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-shortest']
cmd += ['-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', tmp]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
rng = np.random.default_rng(1)
for f, recs in enumerate(j['frames']):
    hdr = None
    for r in recs:
        h = load_dn(f'{prefix}_{r:04d}.bin')
        hdr = h if hdr is None else hdr + h
    hdr = hdr / len(recs)
    img = to_bgr8(grade(hdr), grain=0.006, rng=rng)
    H, W = img.shape[:2]
    bd = j.get('blur', {}).get(str(f), 0.0)
    if bd > 0:      # camera swing: fill the gaps between the sub-frames with a horizontal box blur
        hf = 2 * math.atan(math.tan(math.radians(j.get('vfov', 85.0)) / 2) * W / H)
        px = int(round(bd * math.pi / 180.0 * (W / 2) / math.tan(hf / 2)))
        if px >= 2:
            img = cv2.blur(img, (px, max(1, px // 8)))
    s, dy = punch(f / fps)
    k = OW / W * s
    M = np.float32([[k, 0, (OW - W * k) / 2], [0, k, (OH - H * k) / 2 + dy * OH / 1920.0]])
    img = cv2.warpAffine(img, M, (OW, OH), flags=cv2.INTER_LANCZOS4 if k > 1.01 else cv2.INTER_AREA, borderMode=cv2.BORDER_REFLECT)
    p.stdin.write(img.tobytes())
p.stdin.close()
if p.wait() != 0:
    sys.exit('ffmpeg failed')
os.replace(tmp, out)
print('wrote', out)
