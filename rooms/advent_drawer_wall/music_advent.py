"""Original festive cue for the advent drawer wall: the shared synth cue from pipeline/music.py (120 BPM, F major)
plus synthesized sleigh bells and a glockenspiel figure. No samples, no licensed melodies.

usage: python3 music_advent.py <workdir> [glock_t0,glock_t1]    reads <workdir>/frames.json
       -> <workdir>/music.wav (cue + bells + landing sounds) and <workdir>/sfx_only.wav (landing sounds only)
"""
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'pipeline'))
import music as mu

SR = mu.SR
rng = np.random.default_rng(24)
BPM = 120.0
MUSIC = dict(drop_at=0, chords=[[53, 57, 60, 64], [50, 53, 57, 60], [46, 50, 53, 57], [48, 52, 55, 58]],
             roots=[41, 38, 34, 36], pluck_bars=[], riser=False)


def jingle(gain=1.0):
    """One sleigh-bell shake: a few tiny bells (inharmonic high partials) struck within ~25 ms."""
    n = int(0.22 * SR); t = mu.t_arr(n); out = np.zeros(n)
    for k in range(3):
        d = int(rng.uniform(0, 0.025) * SR)
        for _ in range(5):
            f = rng.uniform(4200, 9800)
            out[d:] += np.sin(2 * np.pi * f * t[:n - d] + rng.uniform(0, 6.28)) * np.exp(-t[:n - d] / rng.uniform(0.03, 0.08))
        out[d:] += mu.hp(rng.standard_normal(n - d), 6000) * np.exp(-t[:n - d] / 0.012) * 0.8
    return mu.hp(out, 3500) * gain / 12.0


def glock(m, length=0.9):
    n = int(length * SR); t = mu.t_arr(n); f = mu.hz(m)
    return (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(2 * np.pi * f * 2.76 * t) * np.exp(-t / 0.08)) * np.exp(-t / 0.45)


def bells_track(dur, glock_spans):
    N = int(SR * (dur + 0.5)); x = np.zeros(N)
    beat = 60.0 / BPM
    nb = int(dur / beat * 2)
    for i in range(nb):
        tt = i * beat / 2
        acc = 0.9 if i % 2 else 0.45
        if tt > dur - 1.0:
            acc *= 0.5
        mu.add(x, jingle(), tt, acc)
    # a shake roll into every second bar
    for b in range(1, int(dur / (4 * beat)) + 1, 2):
        t0 = b * 4 * beat - beat
        for k in range(6):
            mu.add(x, jingle(), t0 + k * beat / 6, 0.35 + 0.08 * k)
    g = np.zeros(N)
    motif = [72, 77, 81, 79, 77, 72, 74, 76]          # original figure in F major
    for (a, b) in glock_spans:
        k = 0
        tt = a
        while tt < b:
            mu.add(g, glock(motif[k % len(motif)]), tt, 0.16)
            k += 1; tt += beat / 2
    return x * 0.55 + mu.reverb(g, 1.4, 0.3)


def main():
    workdir = sys.argv[1]
    spans = [(0.0, 2.0)]
    if len(sys.argv) > 2:
        a, b = (float(v) for v in sys.argv[2].split(','))
        spans.append((a, b))
    cfg = mu.load_cfg(workdir, BPM)
    cfg.MUSIC = MUSIC
    # the stair plays an original rising scale: drawer n opens on the n-th note of F major, closes back down it
    degrees = [0, 2, 4, 5, 7, 9, 11]
    note = lambda n: 65 + 12 * (n // 7) + degrees[n % 7]
    for e in cfg.EVENTS:
        nm = e['name']
        if nm.startswith('advc') and nm[4:].isdigit():
            e['sfx'] = dict(kind='tick', gain=0.16, freq=mu.hz(note(int(nm[4:]))))
        elif nm.startswith('adv') and nm[3:].isdigit():
            e['sfx'] = dict(kind='tick', gain=0.42, freq=mu.hz(note(int(nm[3:]))))
        elif nm == 'adv_tease':
            e['sfx'] = dict(kind='tick', gain=0.5, freq=mu.hz(note(23)))
    base = mu.build(cfg)
    bells = bells_track(cfg.DUR, spans)[: len(base)]
    tt = mu.t_arr(len(base))
    bells *= np.clip((cfg.DUR + 0.2 - tt) / 1.0, 0, 1)
    mix = base + bells
    mix = mix / (np.max(np.abs(mix)) + 1e-9) * 0.89
    mu.write_wav(os.path.join(workdir, 'music.wav'), mix)
    mu.write_wav(os.path.join(workdir, 'sfx_only.wav'), mu.build(cfg, sfx_only=True))
    print('wrote music.wav (with sleigh bells) and sfx_only.wav in', workdir)


if __name__ == '__main__':
    main()
