"""Shared style, helpers, and the narration-synced Scene base class."""
import json
from pathlib import Path

import numpy as np
from manim import *

ROOT = Path(__file__).parent
AUDIO = ROOT / "audio"

BG = "#0C0F16"
config.background_color = BG

# Palette (3b1b-ish)
BLUE_ = "#58C4DD"
TEAL_ = "#5CD0B3"
GREEN_ = "#83C167"
GOLD_ = "#F7C873"
ORANGE_ = "#E8935A"
RED_ = "#FC6255"
PURPLE_ = "#B189C6"
GREY_ = "#888C96"
INK = "#ECEFF4"

SOLID_C = ORANGE_      # material delivered by solids
GAS_C = BLUE_          # material delivered by gas
EXCESS_C = RED_        # redistribution / excess
METAL_C = GOLD_        # metals in general

# Solar metal-mass shares, Asplund et al. 2021 (Table 1 of the paper)
SOLAR_SHARES = [
    ("O", 0.416, "#58C4DD"),
    ("C", 0.184, "#C9CDD6"),
    ("Ne", 0.123, PURPLE_),
    ("Fe", 0.0856, RED_),
    ("N", 0.0503, GREEN_),
    ("Si", 0.0483, ORANGE_),
    ("Mg", 0.0458, TEAL_),
    ("S", 0.0225, "#F4E26B"),
    ("rest", 0.0252, "#4A4F5C"),
]

TEX = TexTemplate()
TEX.add_to_preamble(r"\usepackage{amsmath}\usepackage{amssymb}\usepackage{pifont}")


def T(s, size=36, color=INK, **kw):
    """Text in LaTeX (CMU-like serif, the 3b1b look)."""
    return Tex(s, font_size=size, color=color, tex_template=TEX, **kw)


def M(*args, **kw):
    """MathTex; trailing positional int = font size, trailing '#rrggbb' = color."""
    args = list(args)
    color, size = INK, 40
    while args and (isinstance(args[-1], (int, float)) or str(args[-1]).startswith("#")):
        a = args.pop()
        if isinstance(a, (int, float)):
            size = a
        else:
            color = a
    size, color = kw.pop("size", size), kw.pop("color", color)
    return MathTex(*args, font_size=size, color=color, tex_template=TEX, **kw)


def starfield(n=160, seed=3, w=15, h=8.5):
    rng = np.random.default_rng(seed)
    dots = VGroup()
    for _ in range(n):
        r = rng.uniform(0.006, 0.022)
        d = Dot(point=[rng.uniform(-w / 2, w / 2), rng.uniform(-h / 2, h / 2), 0],
                radius=r, color=WHITE)
        d.set_opacity(rng.uniform(0.15, 0.7))
        dots.add(d)
    return dots


def glow_star(r=0.45, color="#FFD58A", layers=14, spread=2.6):
    glow = VGroup(*[
        Circle(radius=r * (1 + spread * i / layers)).set_fill(color, opacity=0.06)
        .set_stroke(width=0)
        for i in range(layers, 0, -1)
    ])
    core = Circle(radius=r).set_fill("#FFF6DE", 1).set_stroke(color, 2)
    return VGroup(glow, core)


def gas_giant(r=1.0, base="#D7A46C", band_colors=("#B9784A", "#EBCB9A", "#A86A3E", "#E2B988"),
              atmo=BLUE_, seed=0):
    rng = np.random.default_rng(seed)
    body = Circle(radius=r).set_fill(base, 1).set_stroke(width=0)
    bands = VGroup()
    ys = np.linspace(-0.75, 0.75, 7)
    for i, y in enumerate(ys):
        h = r * rng.uniform(0.08, 0.17)
        rect = Rectangle(width=2.4 * r, height=h).move_to(UP * y * r)
        band = Intersection(body, rect, fill_color=band_colors[i % len(band_colors)],
                            fill_opacity=1, stroke_width=0)
        bands.add(band)
    shade = Difference(body, body.copy().shift(r * np.array([-0.32, 0.18, 0])).scale(1.02),
                       fill_color=BLACK, fill_opacity=0.55, stroke_width=0)
    rim = Circle(radius=r * 1.045).set_stroke(atmo, width=5 * r, opacity=0.35).set_fill(opacity=0)
    return VGroup(body, bands, shade, rim)


def split_bar(fracs, colors, width=3.0, height=0.36, labels=None, size=24):
    """Horizontal bar split into fractional segments."""
    segs = VGroup()
    x = 0
    for f, c in zip(fracs, colors):
        w = max(width * f, 1e-3)
        seg = Rectangle(width=w, height=height).set_fill(c, 0.9).set_stroke(BG, 1.5)
        seg.move_to(RIGHT * (x + w / 2))
        segs.add(seg)
        x += w
    segs.move_to(ORIGIN)
    return segs


class Narrated(Scene):
    """Scene whose timeline is synced to a narration track built by tts.py."""
    KEY = None

    def setup(self):
        meta = json.loads((AUDIO / f"{self.KEY}.json").read_text())
        self.starts = meta["starts"]
        self.dur = meta["duration"]
        self.add_sound(str(AUDIO / f"{self.KEY}.wav"))

    def beat(self, k):
        dt = self.starts[k] - self.time
        if dt < -0.05:
            print(f"[SYNC] {self.KEY} beat {k} late by {-dt:.2f}s")
        if dt > 1 / 30:
            self.wait(dt)

    def until(self, t):
        """Wait until an absolute scene time."""
        dt = t - self.time
        if dt > 1 / 30:
            self.wait(dt)

    def finish(self, fade=1.0):
        self.until(self.dur - fade)
        mobs = [m for m in self.mobjects]
        if mobs:
            self.play(*[FadeOut(m) for m in mobs], run_time=fade)
        self.until(self.dur)

    def header(self, num, text):
        n = T(rf"\textbf{{{num}}}", 34, METAL_C)
        t = T(text, 34)
        g = VGroup(n, t).arrange(RIGHT, buff=0.25).to_corner(UL, buff=0.45)
        line = Line(g.get_left(), g.get_left() + RIGHT * 13, stroke_width=1.2, color=GREY_)
        line.next_to(g, DOWN, buff=0.15, aligned_edge=LEFT).set_opacity(0.5)
        return VGroup(g, line)
