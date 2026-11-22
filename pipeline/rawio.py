import numpy as np, cv2


def load_raw(path):
    with open(path, 'rb') as f:
        W, H = np.frombuffer(f.read(8), '<i4')
        n = W * H
        alb = np.frombuffer(f.read(n * 3), np.uint8).reshape(H, W, 3).astype(np.float32) / 255.0
        alb = alb * alb
        nrm = np.frombuffer(f.read(n * 3), np.int8).reshape(H, W, 3).astype(np.float32) / 127.0
        dep = np.frombuffer(f.read(n * 4), '<f4').reshape(H, W)
        idb = np.frombuffer(f.read(n * 2), '<u2').reshape(H, W)
        E = np.frombuffer(f.read(n * 6), '<f2').reshape(H, W, 3).astype(np.float32)
        irr = np.frombuffer(f.read(n * 6), '<f2').reshape(H, W, 3).astype(np.float32)
        spec = np.frombuffer(f.read(n * 6), '<f2').reshape(H, W, 3).astype(np.float32)
    return dict(alb=alb, nrm=nrm, dep=dep, id=idb, E=E, irr=irr, spec=spec)


def tonemap(x, exposure=1.0):
    x = np.maximum(x, 0) * exposure
    a, b, c, d, e = 2.51, 0.03, 2.43, 0.59, 0.14
    y = np.clip((x * (a * x + b)) / (x * (c * x + d) + e), 0, 1)
    return y ** (1 / 2.2)


def to_bgr8(rgb):
    return (np.clip(rgb[..., ::-1], 0, 1) * 255 + 0.5).astype(np.uint8)
