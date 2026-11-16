"""Schematic WASP-39b transmission spectrum used throughout the video.

This is NOT TauREx output: it is a hand-tuned sum of absorption bands whose shape
follows the published JWST NIRSpec spectrum (paper Fig. 9), so the animations look
right without shipping the real data.
"""
import numpy as np

# (center [um], width [um], amplitude [ppm], label)
BANDS = [
    (0.589, 0.018, 650, "Na"),
    (0.768, 0.020, 220, "K"),
    (0.94, 0.045, 160, None),
    (1.14, 0.055, 330, r"H_2O"),
    (1.40, 0.075, 640, r"H_2O"),
    (1.88, 0.095, 700, r"H_2O"),
    (2.74, 0.20, 1150, r"H_2O"),
    (3.25, 0.18, 280, None),
    (4.05, 0.035, 380, r"SO_2"),
    (4.33, 0.10, 1450, r"CO_2"),
    (4.62, 0.14, 520, "CO"),
    (5.15, 0.30, 330, None),
    (6.30, 0.45, 900, None),   # extends the model into the MIRI range
    (7.40, 0.35, 650, None),
    (8.9, 0.8, 300, None),
]

BASE_PPM = 20700.0


def depth_ppm(lam):
    """Smooth transit depth (ppm) vs wavelength (microns)."""
    lam = np.asarray(lam, dtype=float)
    d = BASE_PPM + 380.0 * np.exp(-(lam - 0.5) / 0.18)  # short-wavelength scattering slope
    d = d + 250.0 / (1 + np.exp(-(lam - 4.4) / 0.15))  # raised continuum redward of CO2
    for c, w, a, _ in BANDS:
        d = d + a * np.exp(-0.5 * ((lam - c) / w) ** 2)
    return d


def native_spectrum(lam_min=0.5, lam_max=12.0, n=24000, seed=3):
    """High-resolution 'line-by-line' version: smooth envelope plus spiky line forest."""
    rng = np.random.default_rng(seed)
    lam = np.geomspace(lam_min, lam_max, n)
    smooth = depth_ppm(lam)
    floor = BASE_PPM - 150
    excess = np.clip(smooth - floor, 0, None)
    # lognormal 'line forest' modulation: dense lines inside bands, flat floor in windows
    sig = 0.6
    mod = np.clip(rng.lognormal(mean=-sig**2 / 2, sigma=sig, size=n), 0, 4)  # E[mod] ~ 1
    native = floor + excess * mod
    return lam, native


def bin_spectrum(lam, flux, R, lam_min, lam_max):
    """Average onto constant-resolving-power bins (width = lambda / R)."""
    edges = [lam_min]
    while edges[-1] < lam_max:
        edges.append(edges[-1] * (1 + 1.0 / R))
    edges = np.array(edges)
    centers, values = [], []
    for lo, hi in zip(edges[:-1], edges[1:]):
        m = (lam >= lo) & (lam < hi)
        if m.any():
            centers.append(np.sqrt(lo * hi))
            values.append(flux[m].mean())
    return np.array(centers), np.array(values)


def observation(lam_min, lam_max, n, sigma_ppm, offset_ppm=0.0, seed=0):
    rng = np.random.default_rng(seed)
    lam = np.linspace(lam_min, lam_max, n)
    err = sigma_ppm * (0.7 + 0.6 * rng.random(n))
    y = depth_ppm(lam) + offset_ppm + rng.normal(0, 1, n) * err
    return lam, y, err


# Nine public NIRSpec datasets (2 PRISM, 7 G395H-like), schematic
DATASETS = [
    dict(lam=(0.52, 5.4), n=120, sigma=90, offset=40, seed=1),
    dict(lam=(0.55, 5.3), n=110, sigma=110, offset=-60, seed=2),
    dict(lam=(3.0, 5.5), n=80, sigma=120, offset=90, seed=3),
    dict(lam=(2.85, 3.7), n=40, sigma=100, offset=-40, seed=4),
    dict(lam=(3.80, 5.15), n=55, sigma=110, offset=-20, seed=5),
    dict(lam=(2.90, 5.2), n=80, sigma=130, offset=10, seed=6),
    dict(lam=(2.85, 5.5), n=85, sigma=140, offset=-90, seed=7),
    dict(lam=(2.95, 3.72), n=35, sigma=95, offset=60, seed=8),
    dict(lam=(3.82, 5.2), n=50, sigma=105, offset=-10, seed=9),
]

if __name__ == "__main__":
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    fig, ax = plt.subplots(2, 1, figsize=(10, 8))
    l = np.linspace(0.5, 5.5, 800)
    ax[0].plot(l, depth_ppm(l), "r")
    lo, y, e = observation(0.52, 5.4, 150, 90, seed=1)
    ax[0].errorbar(lo, y, e, fmt="o", alpha=0.4)
    ax[0].set_ylim(20400, 23000)
    lam, nat = native_spectrum()
    ax[1].plot(lam, nat, ".", color="0.7", ms=1)
    for R, a, b in [(700, 0.6, 2.8), (1000, 2.9, 5.3), (100, 5.0, 12.0)]:
        c, v = bin_spectrum(lam, nat, R, a, b)
        ax[1].plot(c, v)
    ax[1].set_xscale("log")
    fig.savefig("/tmp/spec_preview.png" if len(__import__("sys").argv) < 2 else __import__("sys").argv[1], dpi=80)
