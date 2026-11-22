"""Rendered PNG frames (Blender) -> 1080x1920 MP4 with the landing punch, light sharpening and music.

usage: mkvideo_png.py <frames_dir> <fps> <frames.json> <out.mp4> <W> <H> [audio.wav]
frames.json is the timeline export (landing events in seconds); audio comes from music.py.
"""
import glob, json, math, os, subprocess, sys
import cv2, numpy as np

fdir, fps, fj, out, OW, OH = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6])
audio = sys.argv[7] if len(sys.argv) > 7 else None
events = json.load(open(fj))['events']


def punch(t):
    s, dy = 1.012, 0.0
    for e in events:
        tau = t - e['t']
        if 0 <= tau < 0.6:
            a = e['strength']
            s += a * 0.011 * math.exp(-tau / 0.11)
            dy -= a * 5.0 * math.exp(-tau / 0.08) * math.sin(2 * math.pi * tau / 0.14)
    return s, dy


files = sorted(glob.glob(os.path.join(fdir, 'f_*.png')))
tmp = out[:-4] + '.tmp.mp4'
cmd = ['ffmpeg', '-v', 'error', '-y', '-f', 'rawvideo', '-pix_fmt', 'bgr24', '-s', f'{OW}x{OH}', '-r', str(fps), '-i', '-']
if audio:
    cmd += ['-i', audio, '-map', '0:v', '-map', '1:a', '-c:a', 'aac', '-b:a', '192k', '-ar', '44100',
            '-af', 'loudnorm=I=-14:TP=-1.5:LRA=11', '-shortest']
cmd += ['-c:v', 'libx264', '-crf', '17', '-preset', 'medium', '-pix_fmt', 'yuv420p', '-movflags', '+faststart', tmp]
p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
rng = np.random.default_rng(1)
for i, f in enumerate(files):
    img = cv2.imread(f)
    H, W = img.shape[:2]
    s, dy = punch(i / fps)
    k = OW / W * s
    M = np.float32([[k, 0, (OW - W * k) / 2], [0, k, (OH - H * k) / 2 + dy * OH / 1920.0]])
    img = cv2.warpAffine(img, M, (OW, OH), flags=cv2.INTER_LANCZOS4, borderMode=cv2.BORDER_REFLECT)
    blur = cv2.GaussianBlur(img, (0, 0), 1.1)
    img = cv2.addWeighted(img, 1.35, blur, -0.35, 0)
    img = np.clip(img.astype(np.float32) + rng.normal(0, 1.2, img.shape[:2])[..., None], 0, 255).astype(np.uint8)
    p.stdin.write(img.tobytes())
p.stdin.close()
if p.wait() != 0:
    sys.exit('ffmpeg failed')
os.replace(tmp, out)
print('wrote', out, len(files), 'frames')
