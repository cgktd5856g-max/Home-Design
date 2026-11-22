#!/usr/bin/env python3
"""Pipeline driver for a code-rendered room-build clip.

usage: run.py <project.py> <workdir> preview|final|probe [times] [options]
  preview          360x640 render -> 540x960 MP4 with music   (about 1 s per record on 2 CPU cores)
  final            720x1280 render -> 1080x1920 MP4           (about 4 s per record + 1 s denoise)
  probe t1,t2,..   stills at those times -> <workdir>/probe/sheet.jpg (check poses BEFORE a full render)
options: --size WxH      render size            --outsize WxH   size of the MP4
         --out file.mp4  output path            --nl N          light samples per pixel per frame (default 2)
         --naa N         anti-aliasing samples (default 4)      --keep  keep the raw buffers after denoising
         --dnk K         denoiser temporal window: reuse up to K records each side during camera holds (default 6)
The project file writes scene.bin, frames.bin, plan.txt and frames.json into <workdir> (see examples/boys_room).
Needs g++ with OpenMP, ffmpeg, numpy, scipy and opencv. No network, no GPU.
"""
import json, os, subprocess, sys, shutil

SK = os.path.dirname(os.path.abspath(__file__))


def sh(cmd, **kw):
    print('+', ' '.join(str(c) for c in cmd), flush=True)
    subprocess.run([str(c) for c in cmd], check=True, **kw)


def build_bins(workdir):
    b = os.path.join(workdir, 'bin')
    os.makedirs(b, exist_ok=True)
    for name in ('pt', 'dn'):
        src, dst = os.path.join(SK, name + '.cpp'), os.path.join(b, name)
        if not os.path.exists(dst) or os.path.getmtime(dst) < os.path.getmtime(src):
            sh(['g++', '-O3', '-march=native', '-ffast-math', '-fopenmp', '-o', dst, src])
    return os.path.join(b, 'pt'), os.path.join(b, 'dn')


def opt(args, name, default=None):
    if name in args:
        return args[args.index(name) + 1]
    return default


def main():
    if len(sys.argv) < 4:
        sys.exit(__doc__)
    project, workdir, mode = os.path.abspath(sys.argv[1]), os.path.abspath(sys.argv[2]), sys.argv[3]
    args = sys.argv[4:]
    os.makedirs(workdir, exist_ok=True)
    pt, dn = build_bins(workdir)
    sh([sys.executable, project, workdir], cwd=os.path.dirname(project))
    j = json.load(open(os.path.join(workdir, 'frames.json')))
    nrec = len(j['plan'])
    naa, nl = opt(args, '--naa', '4'), opt(args, '--nl', '2')
    scene, frames = os.path.join(workdir, 'scene.bin'), os.path.join(workdir, 'frames.bin')
    if mode == 'probe':
        import cv2, numpy as np
        sys.path.insert(0, SK)
        from post import load_dn, grade, to_bgr8
        times = [float(t) for t in args[0].split(',')]
        W, H = (int(v) for v in opt(args, '--size', '432x768').split('x'))
        pd = os.path.join(workdir, 'probe')
        shutil.rmtree(pd, ignore_errors=True); os.makedirs(pd)
        recs = [j['frames'][min(int(round(t * j['fps'])), j['nframes'] - 1)][0] for t in times]
        with open(os.path.join(pd, 'plan.txt'), 'w') as f:
            for r in recs:
                subprocess.run([pt, scene, frames, os.path.join(pd, 'p'), str(r), str(r + 1), str(W), str(H), '4', '4'], check=True,
                               stderr=subprocess.DEVNULL)
                f.write(f'{r} -1\n')
        subprocess.run([dn, os.path.join(pd, 'p'), os.path.join(pd, 'd'), os.path.join(pd, 'plan.txt'), '0', '5'], check=True, stderr=subprocess.DEVNULL)
        tiles = []
        for r, t in zip(recs, times):
            im = to_bgr8(grade(load_dn(os.path.join(pd, f'd_{r:04d}.bin'))))
            cv2.putText(im, f'{t:.2f}', (8, 28), 0, 0.9, (0, 0, 255), 2)
            tiles.append(im)
        cols = min(6, len(tiles))
        while len(tiles) % cols:
            tiles.append(np.zeros_like(tiles[0]))
        cv2.imwrite(os.path.join(pd, 'sheet.jpg'), np.vstack([np.hstack(tiles[k:k + cols]) for k in range(0, len(tiles), cols)]),
                    [cv2.IMWRITE_JPEG_QUALITY, 88])
        print('wrote', os.path.join(pd, 'sheet.jpg'))
        return
    if mode not in ('preview', 'final'):
        sys.exit(__doc__)
    size = opt(args, '--size', '360x640' if mode == 'preview' else '720x1280')
    outsize = opt(args, '--outsize', '540x960' if mode == 'preview' else '1080x1920')
    out = os.path.abspath(opt(args, '--out', os.path.join(workdir, f'{mode}.mp4')))
    W, H = size.split('x'); OW, OH = outsize.split('x')
    raw, dnd = os.path.join(workdir, f'raw_{mode}'), os.path.join(workdir, f'dn_{mode}')
    for d in (raw, dnd):
        shutil.rmtree(d, ignore_errors=True); os.makedirs(d)
    sh([pt, scene, frames, os.path.join(raw, 'r'), 0, nrec, W, H, naa, nl])
    sh([dn, os.path.join(raw, 'r'), os.path.join(dnd, 'd'), os.path.join(workdir, 'plan.txt'), opt(args, '--dnk', '6'), 5])
    if '--keep' not in args:
        shutil.rmtree(raw, ignore_errors=True)
    sh([sys.executable, os.path.join(SK, 'music.py'), workdir])
    sh([sys.executable, os.path.join(SK, 'mkvideo.py'), workdir, os.path.join(dnd, 'd'), out, OW, OH, os.path.join(workdir, 'music.wav')])
    sh([sys.executable, os.path.join(SK, 'mkvideo.py'), workdir, os.path.join(dnd, 'd'), out[:-4] + '_sfx_only.mp4', OW, OH,
        os.path.join(workdir, 'sfx_only.wav')])
    print('done:', out)


if __name__ == '__main__':
    main()
