"""Checks for a finished clip. usage: qa.py <workdir> <video.mp4>
Prints the format, writes <workdir>/qa_sequence.jpg (a frame every 0.25 s) and qa_events.jpg (each landing at
-0.10 s, 0, +0.10 s), and compares each landing time with the nearest sound onset in sfx_only.wav (keep within 50 ms).
Landings closer together than about 80 ms merge into one detected onset, so offsets up to their spacing are expected there.
"""
import json, os, subprocess, sys, wave
import cv2, numpy as np


def sheet(images, cols, labels):
    tiles = []
    for im, lab in zip(images, labels):
        im = im.copy(); cv2.putText(im, lab, (4, 18), 0, 0.55, (0, 0, 255), 2); tiles.append(im)
    while len(tiles) % cols:
        tiles.append(np.zeros_like(tiles[0]))
    return np.vstack([np.hstack(tiles[k:k + cols]) for k in range(0, len(tiles), cols)])


def onsets(path):
    with wave.open(path) as w:
        sr = w.getframerate(); ch = w.getnchannels()
        x = np.frombuffer(w.readframes(w.getnframes()), np.int16).astype(np.float32).reshape(-1, ch).mean(1) / 32768
    hop = int(sr * 0.005)
    env = np.sqrt(np.convolve(x * x, np.ones(hop * 2) / (hop * 2), 'same')[::hop] + 1e-9)
    flux = np.maximum(np.diff(np.log(env + 1e-4)), 0)
    thr = np.percentile(flux, 97)
    peaks = [i for i in range(1, len(flux) - 1) if flux[i] > thr and flux[i] >= flux[i - 1] and flux[i] >= flux[i + 1]]
    return np.array(peaks) * hop / sr


workdir, video = sys.argv[1], sys.argv[2]
j = json.load(open(os.path.join(workdir, 'frames.json')))
info = json.loads(subprocess.run(['ffprobe', '-v', 'error', '-show_streams', '-show_format', '-of', 'json', video], capture_output=True, text=True).stdout or '{}')
for s in info.get('streams', []):
    if s['codec_type'] == 'video':
        print(f"video {s['width']}x{s['height']} {s['codec_name']} {s.get('r_frame_rate')} fps, {s.get('pix_fmt')}")
    else:
        print(f"audio {s['codec_name']} {s.get('sample_rate')} Hz {s.get('channels')} ch")
print('duration', info.get('format', {}).get('duration'), 's')
cap = cv2.VideoCapture(video)
fps = cap.get(cv2.CAP_PROP_FPS) or j['fps']; n = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))


def at(t):
    cap.set(cv2.CAP_PROP_POS_FRAMES, int(np.clip(round(t * fps), 0, n - 1)))
    ok, fr = cap.read()
    return cv2.resize(fr, (270, 480), interpolation=cv2.INTER_AREA)


ts = np.arange(0, j['dur'], 0.25)
cv2.imwrite(os.path.join(workdir, 'qa_sequence.jpg'), sheet([at(t) for t in ts], 8, [f'{t:.2f}s' for t in ts]), [cv2.IMWRITE_JPEG_QUALITY, 82])
rows, labels = [], []
for e in j['events']:
    for d in (-0.10, 0.0, 0.10):
        rows.append(at(e['t'] + d)); labels.append(f"{e['name'][:10]} {e['t'] + d:.2f}")
cv2.imwrite(os.path.join(workdir, 'qa_events.jpg'), sheet(rows, 6, labels), [cv2.IMWRITE_JPEG_QUALITY, 82])
print('wrote qa_sequence.jpg and qa_events.jpg in', workdir)
sfx = os.path.join(workdir, 'sfx_only.wav')
if os.path.exists(sfx):
    on = onsets(sfx)
    print('landing        time   nearest sound   offset')
    for e in j['events']:
        if e.get('kind') == 'none' or not len(on):
            continue
        k = int(np.argmin(np.abs(on - e['t'])))
        print(f"{e['name'][:12]:12s} {e['t']:6.2f}   {on[k]:6.3f}   {1000 * (on[k] - e['t']):+6.0f} ms")
