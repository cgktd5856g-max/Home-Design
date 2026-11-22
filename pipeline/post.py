"""Tonemap / bloom / grade for denoised HDR frames."""
import numpy as np, cv2
from rawio import tonemap


def load_dn(path):
    with open(path, 'rb') as f:
        W, H = np.frombuffer(f.read(8), '<i4')
        return np.frombuffer(f.read(W * H * 6), '<f2').reshape(H, W, 3).astype(np.float32)


_vig = {}


def grade(hdr, exposure=1.05, bloom=0.07, sat=1.06, vignette=0.16):
    H, W = hdr.shape[:2]
    small = cv2.resize(hdr, (W // 4, H // 4), interpolation=cv2.INTER_AREA)
    bright = np.maximum(small - 1.1, 0)
    bl = cv2.GaussianBlur(bright, (0, 0), W / 220.0) + 0.6 * cv2.GaussianBlur(bright, (0, 0), W / 70.0)
    hdr = hdr + bloom * cv2.resize(bl, (W, H), interpolation=cv2.INTER_LINEAR)
    img = tonemap(hdr, exposure)
    img = img + 0.22 * (img * img * (3 - 2 * img) - img)
    g = img.mean(axis=2, keepdims=True)
    img = g + (img - g) * sat
    if (W, H) not in _vig:
        yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
        r2 = ((xx - W / 2) / (W / 2)) ** 2 * 0.55 + ((yy - H / 2) / (H / 2)) ** 2 * 0.45
        _vig[(W, H)] = (1 - vignette * np.clip(r2, 0, 1.5) ** 1.3)[..., None]
    img = img * _vig[(W, H)]
    return np.clip(img, 0, 1)


def to_bgr8(img, grain=0.0, rng=None):
    if grain > 0:
        img = img + (rng or np.random.default_rng(0)).normal(0, grain, img.shape[:2])[..., None].astype(np.float32)
    return (np.clip(img[..., ::-1], 0, 1) * 255 + 0.5).astype(np.uint8)


if __name__ == '__main__':
    import sys
    hdr = load_dn(sys.argv[1])
    cv2.imwrite(sys.argv[2], to_bgr8(grade(hdr, float(sys.argv[3]) if len(sys.argv) > 3 else 1.05)), [cv2.IMWRITE_JPEG_QUALITY, 93])
    print('wrote', sys.argv[2])
