"""Procedural soft ambient pad to sit under the narration."""
import sys
import numpy as np, soundfile as sf

SR = 44100
dur = float(sys.argv[2])
t = np.arange(int(SR * dur)) / SR
# Slow progression (Hz): Cmaj9, Am9, Fmaj7#11, G6/D
chords = [[130.8, 196.0, 246.9, 293.7, 329.6], [110.0, 164.8, 196.0, 246.9, 261.6],
          [87.3, 130.8, 174.6, 220.0, 329.6], [98.0, 146.8, 196.0, 246.9, 293.7]]
seg = 9.0
out = np.zeros_like(t)
rng = np.random.default_rng(0)
for k in range(int(dur / seg) + 2):
    c = chords[k % len(chords)]
    t0 = k * seg - 1.5
    env = np.clip((t - t0) / 3.0, 0, 1) * np.clip((t0 + seg + 3.0 - t) / 3.0, 0, 1)
    env = np.sin(env * np.pi / 2) ** 2
    for f in c:
        det = 1 + rng.uniform(-0.002, 0.002)
        ph = rng.uniform(0, 2 * np.pi)
        vib = 1 + 0.002 * np.sin(2 * np.pi * 0.2 * t + ph)
        out += env * (np.sin(2 * np.pi * f * det * vib * t + ph) + 0.25 * np.sin(4 * np.pi * f * det * t + ph))
# gentle low-pass (one-pole) and slow tremolo
a = np.exp(-2 * np.pi * 1200 / SR)
y = np.zeros_like(out)
acc = 0.0
for i in range(0, len(out)):
    acc = (1 - a) * out[i] + a * acc
    y[i] = acc
y *= 1 + 0.08 * np.sin(2 * np.pi * 0.07 * t)
fade = np.clip(t / 3.0, 0, 1) * np.clip((dur - t) / 4.0, 0, 1)
y *= fade
y /= np.abs(y).max() + 1e-9
st = np.stack([y, np.roll(y, int(0.012 * SR))], 1) * 0.5
sf.write(sys.argv[1], st.astype(np.float32), SR)
