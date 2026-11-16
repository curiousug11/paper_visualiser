"""Procedurally generated ambient bed (soft pad + sparse plucked arpeggio + reverb).

Usage: python music.py <duration_seconds> <out.wav>
"""
import sys

import numpy as np
import soundfile as sf
from scipy.signal import butter, fftconvolve, sosfilt

SR = 44100
rng = np.random.default_rng(39)


def hz(n):
    return 440.0 * 2 ** ((n - 69) / 12)


# Lydian-flavoured loop: Cmaj9 -> Am9 -> Fmaj7#11 -> G6sus
CHORDS = [
    [48, 55, 59, 62, 64],
    [45, 52, 55, 59, 60],
    [41, 48, 52, 57, 59],
    [43, 50, 57, 60, 64],
]
CHORD_LEN = 8.0


def pad_note(f, n):
    t = np.arange(n) / SR
    x = np.zeros(n)
    for detune, phase in [(1.0, 0.0), (1.0031, 1.3), (0.9969, 2.1)]:
        x += np.sin(2 * np.pi * f * detune * t + phase)
    x += 0.22 * np.sin(2 * np.pi * 2 * f * t + 0.4) + 0.07 * np.sin(2 * np.pi * 3 * f * t + 1.1)
    x *= 0.85 + 0.15 * np.sin(2 * np.pi * 0.11 * t + f)
    return x


def pluck(f, dur=3.0, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    x = np.zeros(n)
    for k, a in enumerate([1.0, 0.45, 0.22, 0.1, 0.05], start=1):
        x += a * np.sin(2 * np.pi * f * k * (1 + 0.0004 * k * k) * t) * np.exp(-t * (1.1 + 0.9 * k))
    env = np.minimum(t / 0.006, 1.0)
    return vel * x * env


def main():
    dur = float(sys.argv[1])
    out = sys.argv[2]
    n = int((dur + 4) * SR)
    pad = np.zeros(n)
    arp = np.zeros(n)

    # pad: overlapping chords with raised-cosine envelopes
    xf = 2.5
    t0 = 0.0
    i = 0
    while t0 < dur + 4:
        chord = CHORDS[i % len(CHORDS)]
        seg = int((CHORD_LEN + xf) * SR)
        s = int(t0 * SR)
        e = min(s + seg, n)
        m = e - s
        tt = np.arange(m) / SR
        env = np.ones(m)
        a = int(xf * SR)
        env[:a] = 0.5 - 0.5 * np.cos(np.pi * np.arange(min(a, m)) / a)[: m]
        if m > a:
            env[-a:] = 0.5 + 0.5 * np.cos(np.pi * np.arange(a) / a)
        voice = sum(pad_note(hz(p), m) * (0.9 if j == 0 else 0.55) for j, p in enumerate(chord))
        pad[s:e] += voice * env

        # sparse arpeggio, two octaves up
        beat = 0.75
        for b in range(int(CHORD_LEN / beat)):
            if rng.random() < 0.55:
                p = chord[rng.integers(1, len(chord))] + 24
                when = t0 + b * beat + rng.normal(0, 0.015)
                ps = int(max(when, 0) * SR)
                if ps >= n:
                    continue
                note = pluck(hz(p), vel=rng.uniform(0.35, 0.8))
                pe = min(ps + len(note), n)
                arp[ps:pe] += note[: pe - ps]
        t0 += CHORD_LEN
        i += 1

    pad = sosfilt(butter(2, 1800, "low", fs=SR, output="sos"), pad)
    pad /= np.abs(pad).max() + 1e-9
    arp = sosfilt(butter(2, 5000, "low", fs=SR, output="sos"), arp)
    arp /= np.abs(arp).max() + 1e-9
    dry = 0.75 * pad + 0.32 * arp

    # reverb: exponentially decaying filtered noise
    ir_n = int(2.8 * SR)
    ir = rng.normal(0, 1, ir_n) * np.exp(-np.arange(ir_n) / SR / 0.75)
    ir = sosfilt(butter(2, 3500, "low", fs=SR, output="sos"), ir)
    ir /= np.sqrt((ir ** 2).sum())
    wet = fftconvolve(dry, ir)[:n]
    mix = 0.6 * dry + 0.55 * wet

    mix = mix[: int(dur * SR)]
    fade_in, fade_out = int(3.0 * SR), int(4.0 * SR)
    mix[:fade_in] *= np.linspace(0, 1, fade_in) ** 2
    mix[-fade_out:] *= np.linspace(1, 0, fade_out) ** 1.5
    mix *= 0.5 / (np.abs(mix).max() + 1e-9)
    stereo = np.stack([mix, np.roll(mix, int(0.012 * SR))], axis=1)  # slight width
    sf.write(out, stereo, SR)
    print(f"wrote {out} ({dur:.1f}s)")


if __name__ == "__main__":
    main()
