"""Shared helpers for the ASTER explainer: narration timing, LaTeX rendering, palette."""
import hashlib
import json
import os
import subprocess
from pathlib import Path

import numpy as np
from manim import *  # noqa: F401,F403

ROOT = Path(__file__).parent
AUDIO = ROOT / "audio"
ASSETS = ROOT / "assets"
TEX_CACHE = ROOT / "media" / "tex_pdf"
DUR = json.loads((AUDIO / "durations.json").read_text())

# ---------------------------------------------------------------- palette
BG = "#0b0d13"
INK = "#ECECEC"
DIM = "#8A8F98"
FAINT = "#3A3F4A"
BLUE_ = "#58C4DD"
TEAL_ = "#5CD0B3"
YELLOW_ = "#FFD866"
GOLD_ = "#F0AC5F"
RED_ = "#FC6255"
GREEN_ = "#83C167"
PURPLE_ = "#B189E0"
PINK_ = "#E07AC6"
ORANGE_ = "#FF9F43"
STAR_CORE = "#FFF4D6"
STAR_EDGE = "#FF9A3C"

config.background_color = BG

# ---------------------------------------------------------------- LaTeX without dvisvgm
# This machine has pdflatex but no dvisvgm, so compile to PDF and convert the page to SVG
# with PyMuPDF. Colors are set inside the TeX source with \textcolor{name}{...}.
PREAMBLE = r"""
\documentclass[border=1pt]{standalone}
\usepackage{amsmath,amssymb}
\usepackage{xcolor}
\usepackage[T1]{fontenc}
\definecolor{ink}{HTML}{ECECEC}
\definecolor{dim}{HTML}{8A8F98}
\definecolor{blu}{HTML}{58C4DD}
\definecolor{tea}{HTML}{5CD0B3}
\definecolor{yel}{HTML}{FFD866}
\definecolor{gol}{HTML}{F0AC5F}
\definecolor{red}{HTML}{FC6255}
\definecolor{grn}{HTML}{83C167}
\definecolor{pur}{HTML}{B189E0}
\definecolor{pnk}{HTML}{E07AC6}
\definecolor{ora}{HTML}{FF9F43}
\begin{document}
\color{ink}
"""
PT = 0.047  # manim units per TeX point at font_size 48 (10pt document)


def _tex_svg(body: str) -> Path:
    TEX_CACHE.mkdir(parents=True, exist_ok=True)
    key = hashlib.sha1(body.encode()).hexdigest()[:16]
    svg = TEX_CACHE / f"{key}.svg"
    if svg.exists():
        return svg
    tex = TEX_CACHE / f"{key}.tex"
    tex.write_text(PREAMBLE + body + "\n\\end{document}\n")
    r = subprocess.run(
        ["pdflatex", "-interaction=nonstopmode", "-halt-on-error", tex.name],
        cwd=TEX_CACHE, capture_output=True, text=True,
    )
    if r.returncode != 0:
        raise RuntimeError(f"LaTeX failed for {body!r}:\n{r.stdout[-1500:]}")
    import pymupdf

    doc = pymupdf.open(TEX_CACHE / f"{key}.pdf")
    svg.write_text(doc[0].get_svg_image(text_as_path=True))
    for ext in (".aux", ".log"):
        (TEX_CACHE / f"{key}{ext}").unlink(missing_ok=True)
    return svg


def _tex_mob(body: str, font_size: float, color=None) -> SVGMobject:
    svg = _tex_svg(body)
    import pymupdf

    h_pt = pymupdf.open(svg.with_suffix(".pdf"))[0].rect.height - 2  # minus border
    units_per_pt = PT * font_size / 48
    # per-process copy: SVGMobject writes a temporary "<name>_.svg" next to the file, which
    # races when several scenes render in parallel
    local = svg.with_name(f"{svg.stem}-{os.getpid()}.svg")
    if not local.exists():
        local.write_bytes(svg.read_bytes())
    mob = SVGMobject(str(local), height=None, should_center=True)
    sw_native = [sm.get_stroke_width() for sm in mob.family_members_with_points()]
    mob.set_height(max(h_pt, 1) * units_per_pt)
    for sm, sw in zip(mob.family_members_with_points(), sw_native):
        if sm.get_fill_opacity() < 0.01 and sw > 0:  # rules (fraction bars, roots) are strokes
            sm.set_stroke(width=sw * units_per_pt * 100, opacity=1)
            if color is not None:
                sm.set_stroke(color)
        else:
            sm.set_stroke(width=0)
            if color is not None:
                sm.set_fill(color, 1)
    return mob


def T(text: str, font_size: float = 36, color=None) -> SVGMobject:
    """Text-mode LaTeX (Computer Modern), e.g. T(r'Transit depth')."""
    return _tex_mob(text, font_size, color)


def M(math: str, font_size: float = 48, color=None) -> SVGMobject:
    """Display-math LaTeX, e.g. M(r'\\delta(\\lambda)')."""
    return _tex_mob(f"${math}$", font_size, color)


def mono(text: str, size: float = 22, color=INK, weight=NORMAL) -> Text:
    return Text(text, font="Menlo", font_size=size, color=color, weight=weight)


def sans(text: str, size: float = 24, color=INK, weight=NORMAL) -> Text:
    return Text(text, font="Helvetica Neue", font_size=size, color=color, weight=weight)


# ---------------------------------------------------------------- narration-driven scene
class Narrated(MovingCameraScene):
    """Scene whose beats are driven by the voiceover clips in audio/."""

    GAP = 0.3  # silence after each beat

    def setup(self):
        super().setup()
        self._beat_end = 0.0

    @property
    def now(self) -> float:
        return self.renderer.time

    def narrate(self, key: str, pause: float = 0.0) -> float:
        self.finish_beat()
        if pause:
            self.wait(pause)
        self.add_sound(str(AUDIO / f"{key}.wav"))
        self._beat_start = self.now
        self._beat_end = self.now + DUR[key] + self.GAP
        return DUR[key]

    def elapsed(self) -> float:
        """Seconds since the current beat started."""
        return self.now - (self._beat_start if hasattr(self, "_beat_start") else 0.0)

    def wait_until(self, t: float):
        """Wait until t seconds into the current beat."""
        dt = t - self.elapsed()
        if dt > 1 / 30:
            self.wait(dt)

    def remaining(self) -> float:
        return max(self._beat_end - self.now, 0.0)

    def finish_beat(self, extra: float = 0.0):
        rem = self.remaining() + extra
        if rem > 1 / 30:
            self.wait(rem)


# ---------------------------------------------------------------- reusable pieces
def starfield(n=260, seed=7, w=16, h=9.5):
    rng = np.random.default_rng(seed)
    dots = VGroup()
    for _ in range(n):
        r = rng.uniform(0.006, 0.022)
        d = Dot(
            [rng.uniform(-w / 2, w / 2), rng.uniform(-h / 2, h / 2), 0],
            radius=r,
            color=interpolate_color(ManimColor(WHITE), ManimColor(BLUE_), rng.uniform(0, 0.5)),
        )
        d.set_opacity(rng.uniform(0.15, 0.8))
        dots.add(d)
    return dots


def glowing_star(radius=2.0, n_core=22, n_glow=14, glow_extent=1.6):
    """Limb-darkened star disk with a soft corona, built from concentric circles."""
    glow = VGroup()
    for i in range(n_glow):
        a = i / (n_glow - 1)
        r = radius * (1 + glow_extent * (1 - a) * 0.6)
        c = Circle(radius=r, stroke_width=0)
        c.set_fill(STAR_EDGE, opacity=0.035 + 0.02 * a)
        glow.add(c)
    core = VGroup()
    for i in range(n_core):
        a = i / (n_core - 1)
        r = radius * (1 - 0.97 * a)
        c = Circle(radius=r, stroke_width=0)
        c.set_fill(interpolate_color(ManimColor(STAR_EDGE), ManimColor(STAR_CORE), a ** 0.6), opacity=1)
        core.add(c)
    return VGroup(glow, core)


def jwst_mirror(size=0.18, color=GOLD_):
    """18-segment hexagonal primary mirror, JWST style."""
    hexes = VGroup()
    dx = size * np.sqrt(3)
    coords = []
    for ring in range(3):
        if ring == 0:
            continue  # JWST has no central segment
        for k in range(6 * ring):
            side, step = divmod(k, ring)
            a0 = np.pi / 3 * side + np.pi / 6
            a1 = np.pi / 3 * (side + 1) + np.pi / 6
            p0 = ring * dx * np.array([np.cos(a0), np.sin(a0)])
            p1 = ring * dx * np.array([np.cos(a1), np.sin(a1)])
            coords.append(p0 + (p1 - p0) * step / ring)
    for x, y in coords:
        h = RegularPolygon(6, start_angle=np.pi / 6).scale(size * 0.97)
        h.move_to([x, y, 0]).set_fill(color, 0.85).set_stroke(YELLOW_, 0.6)
        hexes.add(h)
    return hexes


def chip(label: str, color=BLUE_, size=20, mono_font=True, pad=0.16):
    txt = mono(label, size, color=INK) if mono_font else sans(label, size)
    box = RoundedRectangle(
        corner_radius=0.08, width=txt.width + 2 * pad, height=txt.height + 1.6 * pad,
        stroke_color=color, stroke_width=2,
    ).set_fill(color, 0.12)
    return VGroup(box, txt.move_to(box))


def wl_color(lam, lo=0.5, hi=5.5):
    """False color for wavelength: blue (short) -> red (long)."""
    a = np.clip((lam - lo) / (hi - lo), 0, 1)
    stops = [ManimColor(c) for c in ("#6A7BFF", BLUE_, GREEN_, YELLOW_, ORANGE_, RED_)]
    x = a * (len(stops) - 1)
    i = min(int(x), len(stops) - 2)
    return interpolate_color(stops[i], stops[i + 1], x - i)
