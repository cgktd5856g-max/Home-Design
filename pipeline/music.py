"""Original chill-house cue + landing SFX, synthesized from scratch (no samples, no copyrighted audio).

Usage: python3 music.py <workdir> [bpm]     reads <workdir>/frames.json (written by animkit.Timeline.export)
       -> <workdir>/music.wav and <workdir>/sfx_only.wav
Optional <workdir>/music.json overrides: {"bpm": 126, "MUSIC": {"drop_at": 0, "chords": [[..],..], "roots": [..],
"pluck_bars": [0, 1], "riser": false}}
Event kinds from the timeline: 'thud' (big pieces; strength sets gain and pitch), 'tick' (small items), 'swish'
(drawer / door opening), 'chime' (lights on), 'none'.
"""
import os
import sys
import wave

import numpy as np
from scipy.signal import butter, fftconvolve, sosfilt

import json

SR = 44100
rng = np.random.default_rng(7)


def t_arr(n):
    return np.arange(n) / SR


def env_adsr(n, a=0.01, d=0.1, s=0.7, r=0.2):
    hold = n / SR - a - d - r
    e = np.concatenate([np.linspace(0, 1, max(int(a * SR), 1), endpoint=False),
                        np.linspace(1, s, max(int(d * SR), 1), endpoint=False),
                        np.full(max(int(max(hold, 0) * SR), 0), s),
                        np.linspace(s, 0, max(int(r * SR), 1))])
    return np.pad(e, (0, max(0, n - len(e))))[:n]


def lp(x, fc, order=2):
    return sosfilt(butter(order, min(fc, SR * 0.45), 'low', fs=SR, output='sos'), x)


def hp(x, fc, order=2):
    return sosfilt(butter(order, fc, 'high', fs=SR, output='sos'), x)


def bp(x, f1, f2, order=2):
    return sosfilt(butter(order, [f1, min(f2, SR * 0.45)], 'band', fs=SR, output='sos'), x)


def add(buf, sig, t0, gain=1.0):
    i = int(round(t0 * SR))
    if i >= len(buf) or i + len(sig) <= 0:
        return
    if i < 0:
        sig = sig[-i:]; i = 0
    j = min(len(buf), i + len(sig))
    buf[i:j] += gain * sig[:j - i]


def hz(m):
    return 440.0 * 2 ** ((m - 69) / 12.0)


def saw(f, n, detune=0.0):
    ph = f * (1 + detune) * t_arr(n)
    return 2 * (ph - np.floor(ph + 0.5))


def tri(f, n):
    return 2 * np.abs(saw(f, n)) - 1


def kick():
    n = int(0.45 * SR); t = t_arr(n)
    f = 52 + 110 * np.exp(-t / 0.035)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.20)
    click = hp(rng.standard_normal(n) * np.exp(-t / 0.004), 1500) * 0.25
    return np.tanh(1.6 * (body + click))


def clap():
    n = int(0.35 * SR); t = t_arr(n)
    e = np.zeros(n)
    for k, off in enumerate([0, 0.011, 0.022]):
        i = int(off * SR); e[i:] += np.exp(-t[:n - i] / (0.012 if k < 2 else 0.11))
    return bp(rng.standard_normal(n) * e, 900, 5200) * 0.9


def hat(open_=False):
    n = int((0.28 if open_ else 0.06) * SR); t = t_arr(n)
    return hp(rng.standard_normal(n), 7000, 4) * np.exp(-t / (0.09 if open_ else 0.014))


def epiano(notes, length):
    n = int(length * SR); t = t_arr(n); out = np.zeros(n)
    for m in notes:
        f = hz(m)
        mod = np.sin(2 * np.pi * f * 2 * t) * 1.2 * np.exp(-t / 0.25)
        out += np.sin(2 * np.pi * f * t + mod) * np.exp(-t / 0.9) + 0.25 * np.sin(2 * np.pi * f * 3 * t) * np.exp(-t / 0.15)
    return out * env_adsr(n, 0.004, 0.05, 0.9, 0.08) / max(len(notes), 1)


def pad_synth(notes, length, cutoff=1800):
    n = int(length * SR); out = np.zeros(n)
    for m in notes:
        f = hz(m); out += saw(f, n, -0.004) + saw(f, n, 0.005) + 0.5 * tri(f / 2, n)
    return lp(out, cutoff) * env_adsr(n, 0.35, 0.3, 0.8, 0.6) / (len(notes) * 2.5)


def bass(m, length):
    n = int(length * SR); f = hz(m)
    x = 0.7 * np.sin(2 * np.pi * f * t_arr(n)) + 0.45 * lp(saw(f, n), 900)
    return np.tanh(1.3 * x) * env_adsr(n, 0.005, 0.08, 0.75, 0.05)


def pluck(m, length=0.35):
    n = int(length * SR); t = t_arr(n); f = hz(m)
    return lp((tri(f, n) + 0.3 * np.sin(2 * np.pi * 2 * f * t)) * np.exp(-t / 0.10), 5000)


def whoosh(length, up=True):
    n = max(int(length * SR), 64); t = t_arr(n)
    nz = rng.standard_normal(n); out = np.zeros(n); segs = 24
    for k in range(segs):
        a, b = k * n // segs, (k + 1) * n // segs
        frac = k / (segs - 1)
        fc = 400 * (12 ** (frac if up else 1 - frac))
        out[a:b] = bp(nz[a:b], fc * 0.7, fc * 1.6)
    e = (t / length) ** 2 if up else np.exp(-t / (length * 0.4))
    return lp(out, 9000) * e


def thud(f0=70):
    n = int(0.5 * SR); t = t_arr(n)
    f = f0 + 60 * np.exp(-t / 0.03)
    body = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t / 0.13)
    knock = bp(rng.standard_normal(n), 120, 900) * np.exp(-t / 0.02) * 0.6
    return np.tanh(1.4 * (body + knock))


def tick(f=1200):
    n = int(0.18 * SR); t = t_arr(n)
    return np.sin(2 * np.pi * f * t) * np.exp(-t / 0.035) + 0.4 * np.sin(2 * np.pi * f * 1.5 * t) * np.exp(-t / 0.02)


def chime():
    n = int(1.6 * SR); t = t_arr(n); out = np.zeros(n)
    for m, d in [(84, 0.0), (88, 0.05), (91, 0.10), (96, 0.16)]:
        i = int(d * SR); out[i:] += np.sin(2 * np.pi * hz(m) * t[:n - i]) * np.exp(-t[:n - i] / 0.5)
    return out * 0.35 + hp(rng.standard_normal(n), 3000) * np.exp(-t / 0.003) * 0.5


def reverb(x, secs=1.6, mix=0.18):
    n = int(secs * SR); t = t_arr(n)
    ir = lp(rng.standard_normal(n) * np.exp(-t / (secs / 5.5)), 6000)
    ir /= np.sqrt(np.sum(ir ** 2))
    return x * (1 - mix) + fftconvolve(x, ir)[:len(x)] * mix * 1.6


def default_sfx(e):
    m = e.get('motion')
    if m == 'cut':
        return dict(kind='swish', gain=0.25)
    if m == 'none':
        return dict(kind='chime', gain=0.55) if e.get('tgt') else dict(kind='none')
    if e.get('dur', 0) >= 0.4:
        return dict(kind='thud', gain=0.6, f0=70, whoosh=0.45)
    return dict(kind='tick', gain=0.35, freq=1300)


def build(cfg, sfx_only=False):
    bpm, dur = cfg.BPM, cfg.DUR
    beat = 60.0 / bpm; bar = 4 * beat
    N = int(SR * (dur + 0.5))
    M = getattr(cfg, 'MUSIC', {}) or {}
    events = sorted(cfg.EVENTS, key=lambda e: e['land'])
    first_land = min([e['land'] for e in events if e.get('motion') not in ('cut',)] or [0.0])
    drop_at = M.get('drop_at', None)
    drop_at = first_land if drop_at is None else drop_at
    drop_bar = int(round(drop_at / bar))
    chords = M.get('chords', [[53, 57, 60, 64], [52, 55, 59, 62], [50, 53, 57, 60], [48, 52, 55, 59]])
    roots = M.get('roots', [41, 40, 38, 36])
    drums = np.zeros(N); music = np.zeros(N); sfx = np.zeros(N); duck = np.ones(N)
    nbars = int(np.ceil(dur / bar))
    for b in range(nbars):
        t0 = b * bar
        ch = chords[b % len(chords)]
        last = b == nbars - 1
        intro = b < drop_bar
        add(music, pad_synth([m + 12 for m in ch], bar + 0.6 if not last else 2.6, cutoff=900 if intro else 1900), t0,
            0.72 * (0.55 if intro else 0.8))
        if not intro and not last:
            for k in range(4):
                add(music, epiano([m + 12 for m in ch], 0.32), t0 + k * beat + beat / 2, 0.40)
            for k in range(8):
                add(music, bass(roots[b % len(roots)] + (12 if k % 2 else 0), beat / 2 * 0.9), t0 + k * beat / 2, 0.36)
        if last:
            add(music, epiano([m + 12 for m in ch], 2.2), t0, 0.6)
            add(music, bass(roots[b % len(roots)], 1.6), t0, 0.6)
        for k in range(4):
            tb = t0 + k * beat
            if not intro and not last:
                add(drums, kick(), tb, 0.85)
                i = int(tb * SR); j = min(N, i + int(0.22 * SR))
                duck[i:j] = np.minimum(duck[i:j], 0.45 + 0.55 * np.linspace(0, 1, j - i) ** 0.6)
                if k in (1, 3):
                    add(drums, clap(), tb, 0.38)
            for hh in range(2):
                th = tb + hh * beat / 2
                if intro and hh == 1:
                    add(drums, hp(hat(), 9000), th, 0.07)
                elif not intro and not last:
                    add(drums, hat(open_=(k == 3 and hh == 1)), th, 0.11 if hh == 1 else 0.055)
        if last:
            add(drums, kick(), t0, 0.9)
    arp = [72, 76, 79, 84, 79, 76]
    for b in M.get('pluck_bars', []):
        for k in range(8):
            add(music, pluck(arp[k % len(arp)]), b * bar + k * beat / 2 + beat / 4, 0.11)
    if M.get('riser', True) and drop_at > 0.5:
        add(sfx, whoosh(min(1.6, drop_at)), drop_at - min(1.6, drop_at), 0.28)
    for e in events:
        s = dict(default_sfx(e)); s.update(e.get('sfx', {}))
        t = e['land']; k = s.get('kind', 'none'); g = s.get('gain', 0.5)
        if s.get('whoosh'):
            add(sfx, whoosh(s['whoosh']), t - s['whoosh'], s.get('whoosh_gain', 0.22 * g / 0.8))
        if k == 'thud':
            add(sfx, thud(s.get('f0', 70)), t, g)
        elif k == 'tick':
            add(sfx, tick(s.get('freq', 1300)), t, g)
        elif k == 'chime':
            add(sfx, chime(), t, g)
            add(sfx, whoosh(1.2, up=False), t, 0.10)
        elif k == 'swish':
            add(sfx, whoosh(0.3, up=True), t - 0.3, g)
    if sfx_only:
        mix = 0.8 * reverb(sfx, 1.0, 0.12)
    else:
        mix = drums * 0.9 + reverb(music * duck, 1.8, 0.22) + 0.8 * reverb(sfx, 1.0, 0.12)
    mix = hp(mix, 28)
    mix = np.tanh(mix * 1.1) / np.tanh(1.1)
    tt = t_arr(N)
    mix *= np.clip(tt / 0.15, 0, 1) * np.clip((dur + 0.4 - tt) / 0.9, 0, 1)
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.89
    return mix[: int(SR * dur)]


def write_wav(path, x):
    st = np.stack([x, x], 1)
    d = int(0.009 * SR); st[d:, 1] = 0.85 * x[:-d] + 0.15 * x[d:]
    with wave.open(path, 'wb') as w:
        w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR)
        w.writeframes((np.clip(st, -1, 1) * 32767).astype(np.int16).tobytes())


class Cfg:
    pass


def load_cfg(workdir, bpm=None):
    j = json.load(open(os.path.join(workdir, 'frames.json')))
    over = {}
    p = os.path.join(workdir, 'music.json')
    if os.path.exists(p):
        over = json.load(open(p))
    cfg = Cfg()
    cfg.BPM = float(bpm or over.get('bpm', 126.0))
    cfg.DUR = j['dur']
    cfg.MUSIC = over.get('MUSIC', dict(drop_at=0, chords=[[57, 60, 64, 67], [53, 57, 60, 64], [55, 59, 62, 65], [52, 55, 59, 62]],
                                        roots=[45, 41, 43, 40], pluck_bars=[0, 1], riser=False))
    cfg.EVENTS = []
    for i, e in enumerate(j['events']):
        a = e.get('strength', 0.5); k = e.get('kind', 'tick')
        if k == 'thud':
            sfx = dict(kind='thud', gain=0.30 + 0.5 * a, f0=58 + 45 * (1 - a))
        elif k == 'swish':
            sfx = dict(kind='swish', gain=0.35)
        elif k == 'chime':
            sfx = dict(kind='chime', gain=0.5)
        elif k == 'none':
            sfx = dict(kind='none')
        else:
            sfx = dict(kind='tick', gain=0.26 + 0.25 * a, freq=980 + 140 * (i % 6))
        if 'f0' in e:                                    # per-event pitch override (e.g. wooden clacks)
            sfx['f0'] = e['f0']
        cfg.EVENTS.append(dict(name=e['name'], land=e['t'], dur=0.2, motion='drop', sfx=sfx))
    return cfg


def main():
    workdir = sys.argv[1]
    cfg = load_cfg(workdir, sys.argv[2] if len(sys.argv) > 2 else None)
    write_wav(os.path.join(workdir, 'music.wav'), build(cfg))
    write_wav(os.path.join(workdir, 'sfx_only.wav'), build(cfg, sfx_only=True))
    print('wrote', os.path.join(workdir, 'music.wav'), 'and sfx_only.wav')


if __name__ == '__main__':
    main()
