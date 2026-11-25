"""Rendered PNG frames (Blender) -> 1080x1920 MP4 with the landing punch, light sharpening and music.

usage: mkvideo_png.py <frames_dir> <fps> <frames.json> <out.mp4> <W> <H> [audio.wav] [captions.json] [--grade SAT,WARM[,GAMMA]]
frames.json is the timeline export (landing events in seconds); audio comes from music.py.
captions.json: [[t0, t1, "line one\nline two"], ...] drawn bold white with a black outline near the top.
"""
import glob, json, math, os, subprocess, sys
import cv2, numpy as np

fdir, fps, fj, out, OW, OH = sys.argv[1], float(sys.argv[2]), sys.argv[3], sys.argv[4], int(sys.argv[5]), int(sys.argv[6])
audio = sys.argv[7] if len(sys.argv) > 7 and sys.argv[7] != '-' else None
GRADE = (1.0, 0.0)
if '--grade' in sys.argv:
    i = sys.argv.index('--grade'); GRADE = tuple(float(v) for v in sys.argv[i + 1].split(','))
    del sys.argv[i:i + 2]
captions = json.load(open(sys.argv[8])) if len(sys.argv) > 8 and sys.argv[8] != '-' else []
FONT = '/usr/share/fonts/opentype/inter/Inter-ExtraBold.otf'


def caption_layer(text, W, H):
    from PIL import Image, ImageDraw, ImageFont
    font = ImageFont.truetype(FONT, int(W * 0.066))
    sw = max(3, int(W * 0.0065))
    im = Image.new('RGBA', (W, H), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    y = int(H * 0.115)
    for line in text.split('\n'):
        x0, y0, x1, y1 = d.textbbox((0, 0), line, font=font, stroke_width=sw)
        d.text(((W - (x1 - x0)) // 2 - x0, y - y0), line, font=font, fill=(255, 255, 255, 255), stroke_width=sw, stroke_fill=(0, 0, 0, 255))
        y += int((y1 - y0) * 1.18)
    a = np.array(im).astype(np.float32)
    return a[..., [2, 1, 0]], a[..., 3:] / 255.0


layers = [(t0, t1, *caption_layer(txt, OW, OH)) for t0, t1, txt in captions]
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
    if GRADE[:2] != (1.0, 0.0) or len(GRADE) > 2:   # saturation around luma, then warmth (BGR order), then gamma
        f = img.astype(np.float32)
        yl = (0.114 * f[..., 0] + 0.587 * f[..., 1] + 0.299 * f[..., 2])[..., None]
        f = yl + (f - yl) * GRADE[0]
        f[..., 2] *= 1 + GRADE[1]; f[..., 0] *= 1 - GRADE[1]
        if len(GRADE) > 2:    # optional third value: brightness gamma (1.15 lifts the mids, keeps white and black)
            f = 255.0 * (np.clip(f, 0, 255) / 255.0) ** (1.0 / GRADE[2])
        img = np.clip(f, 0, 255).astype(np.uint8)
    blur = cv2.GaussianBlur(img, (0, 0), 1.1)
    img = cv2.addWeighted(img, 1.35, blur, -0.35, 0)
    img = np.clip(img.astype(np.float32) + rng.normal(0, 1.2, img.shape[:2])[..., None], 0, 255)
    t = i / fps
    for t0, t1, rgb, al in layers:
        if t0 <= t < t1:
            o = min(1.0, (t - t0) / 0.12, (t1 - t) / 0.12) if t0 > 0 else min(1.0, (t1 - t) / 0.12)
            img = img * (1 - al * o) + rgb * (al * o)
    img = img.astype(np.uint8)
    p.stdin.write(img.tobytes())
p.stdin.close()
if p.wait() != 0:
    sys.exit('ffmpeg failed')
os.replace(tmp, out)
print('wrote', out, len(files), 'frames')
