"""3b1b-style explainer for Chachan, Murray-Clay & Fortney (arXiv:2608.23682)."""
from common import *


# --------------------------------------------------------------------------- #
# 0. Hook + title
# --------------------------------------------------------------------------- #
class S0Hook(Narrated):
    KEY = "s0_hook"

    def construct(self):
        stars = starfield()
        star = glow_star(0.5).move_to(LEFT * 1.8 + UP * 0.2)
        orbit = Ellipse(width=8.4, height=2.4).move_to(star).set_stroke(GREY_, 1.2, 0.45)
        planet = gas_giant(0.3, seed=1)
        t = ValueTracker(0.62)
        planet.add_updater(lambda m: m.move_to(orbit.point_from_proportion(t.get_value() % 1)))

        # beat 0 — a planet's atmosphere is a fossil record
        self.beat(0)
        self.play(FadeIn(stars, run_time=1.6), FadeIn(star, scale=0.5, run_time=1.6),
                  Create(orbit, run_time=2.0))
        self.add(planet)
        self.play(FadeIn(planet), t.animate.set_value(1.0), run_time=1.5, rate_func=linear)
        planet.clear_updaters()
        big = gas_giant(2.1, seed=1).move_to(LEFT * 3.9 + DOWN * 0.2)
        self.play(Transform(planet, big), FadeOut(star, scale=2), FadeOut(orbit),
                  stars.animate.scale(1.4).set_opacity(0.35), run_time=1.4)
        atmo = Arc(radius=2.25, start_angle=-PI / 2.6, angle=PI / 1.3, arc_center=big.get_center())
        atmo.set_stroke(BLUE_, 10, 0.8)
        atmo_lbl = T("atmosphere", 30, BLUE_).move_to(big.get_center() + np.array([1.2, 2.55, 0]))
        self.play(Create(atmo), FadeIn(atmo_lbl, shift=LEFT * 0.2), run_time=1.0)

        # beat 1 — telescopes read the record
        self.beat(1)
        ax = Axes(x_range=[0.9, 5.3, 1], y_range=[0, 1.15, 0.5], x_length=6.2, y_length=2.6,
                  axis_config={"color": GREY_, "stroke_width": 2, "include_ticks": False},
                  tips=False).move_to(RIGHT * 3.1 + UP * 1.4)
        xl = T(r"wavelength ($\mu$m)", 22, GREY_).next_to(ax.x_axis, DOWN, buff=0.12)
        yl = T("flux", 22, GREY_).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.12)
        dips = [(1.4, 0.10, 0.35), (1.9, 0.12, 0.4), (2.35, 0.03, 0.3), (2.7, 0.15, 0.45),
                (3.9, 0.06, 0.22), (4.65, 0.08, 0.5)]

        def spec(l):
            bb = 1.05 * np.exp(-((l - 2.2) / 1.6) ** 2) + 0.08
            s = 1 - sum(d * np.exp(-((l - c) / w) ** 2) for c, w, d in dips)
            wig = 0.025 * np.sin(23 * l) + 0.015 * np.sin(57 * l + 1)
            return bb * s + wig * bb

        curve = ax.plot(spec, x_range=[0.95, 5.2, 0.005], color=WHITE, stroke_width=2.4)
        ray = Line(big.get_right() + UP * 0.6, ax.get_left() + DOWN * 0.2, color=BLUE_,
                   stroke_width=3).set_opacity(0.6)
        mol = VGroup(
            T(r"H$_2$O", 22, BLUE_).move_to(ax.c2p(1.9, 0.2)),
            T(r"CO", 22, GREEN_).move_to(ax.c2p(4.65, 0.42)),
            T(r"H$_2$S", 22, "#F4E26B").move_to(ax.c2p(2.35, 0.36)),
        )
        self.play(ShowPassingFlash(ray.copy().set_stroke(width=6), time_width=0.6), Create(ax),
                  FadeIn(xl), FadeIn(yl), run_time=1.2)
        self.play(Create(curve), run_time=2.2)
        self.play(LaggedStart(*[FadeIn(m, shift=UP * 0.15) for m in mol], lag_ratio=0.25),
                  run_time=1.2)

        chips = VGroup()
        for el, val, col in [("C", "4.2", "#C9CDD6"), ("O", "4.9", BLUE_), ("N", "21", GREEN_),
                             ("S", "5.2", "#F4E26B")]:
            box = RoundedRectangle(corner_radius=0.12, width=1.45, height=0.95)
            box.set_stroke(col, 2).set_fill(col, 0.12)
            lab = M(rf"\mathrm{{{el}}}", 34, col).move_to(box.get_center() + UP * 0.17)
            v = M(rf"{val}\times", 26, INK).move_to(box.get_center() + DOWN * 0.22)
            chips.add(VGroup(box, lab, v))
        chips.arrange(RIGHT, buff=0.22).move_to(RIGHT * 3.1 + DOWN * 1.35)
        cap = T(r"HR 8799 b, relative to its host star", 22, GREY_).next_to(chips, DOWN, buff=0.2)
        self.play(LaggedStart(*[GrowFromCenter(c) for c in chips], lag_ratio=0.18), run_time=1.6)
        self.play(FadeIn(cap), run_time=0.6)

        # beat 2 — numbers are not a story yet
        self.beat(2)
        self.play(FadeOut(VGroup(ax, xl, yl, curve, mol)), chips.animate.move_to(RIGHT * 3.1 + UP * 1.7),
                  cap.animate.next_to(RIGHT * 3.1 + UP * 1.7, DOWN, buff=0.75), run_time=1.3)
        q1 = T(r"How much rock \& ice\\did it swallow?", 32)
        q2 = T(r"Where did it\\come from?", 32)
        qm = M(r"?", 120, METAL_C)
        VGroup(q1, qm, q2).arrange(RIGHT, buff=0.45).move_to(RIGHT * 3.0 + DOWN * 1.1)
        self.wait(2.0)
        self.play(Write(qm), run_time=0.8)
        self.play(FadeIn(q1, shift=UP * 0.2), run_time=0.9)
        self.wait(1.2)
        self.play(FadeIn(q2, shift=UP * 0.2), run_time=0.9)

        # beat 3 — the paper
        self.beat(3)
        self.play(*[FadeOut(m) for m in [planet, atmo, atmo_lbl, chips, cap, q1, q2, qm]],
                  stars.animate.set_opacity(0.2), run_time=1.0)
        title = T(r"Quantitative Links between Formation and\\Atmospheric Composition for Giant Planets",
                  46).move_to(UP * 1.3)
        auth = T(r"Yayaati Chachan \quad Ruth Murray-Clay \quad Jonathan J. Fortney", 28, GREY_)
        auth.next_to(title, DOWN, buff=0.45)
        inst = T(r"UC Santa Cruz \quad$\cdot$\quad arXiv:2608.23682", 24, GREY_).next_to(auth, DOWN, buff=0.18)
        left = T("atmospheric abundances", 30, BLUE_)
        right = T("formation history", 30, SOLID_C)
        arr = Arrow(LEFT, RIGHT, color=METAL_C, stroke_width=5).scale(0.9)
        row = VGroup(left, arr, right).arrange(RIGHT, buff=0.4).move_to(DOWN * 1.9)
        dict_lbl = T(r"\textit{a dictionary}", 24, METAL_C).next_to(arr, UP, buff=0.1)
        self.play(Write(title), run_time=1.8)
        self.play(FadeIn(auth, shift=UP * 0.1), FadeIn(inst, shift=UP * 0.1), run_time=0.8)
        self.play(FadeIn(left, shift=RIGHT * 0.2), GrowArrow(arr), FadeIn(dict_lbl),
                  FadeIn(right, shift=LEFT * 0.2), run_time=1.2)
        self.finish()


# --------------------------------------------------------------------------- #
# 1. Enrichment -> metal mass fraction
# --------------------------------------------------------------------------- #
class S1Mass(Narrated):
    KEY = "s1_mass"

    def construct(self):
        hdr = self.header("1", r"Enrichment $\to$ mass")

        # beat 0 — define x
        self.beat(0)
        self.play(FadeIn(hdr, shift=RIGHT * 0.3), run_time=0.8)
        eq = M(r"x_i \;=\; \frac{(n_i/n_{\rm H})_{\rm planet}}{(n_i/n_{\rm H})_{\star}}", 60)
        eq.move_to(UP * 0.4)
        self.play(Write(eq), run_time=2.0)
        n1 = T("planet's atmosphere", 26, BLUE_).next_to(eq, RIGHT, buff=0.5).shift(UP * 0.45)
        n2 = T("host star", 26, GOLD_).next_to(eq, RIGHT, buff=0.5).shift(DOWN * 0.45)
        self.play(FadeIn(n1, shift=LEFT * 0.2), run_time=0.6)
        self.play(FadeIn(n2, shift=LEFT * 0.2), run_time=0.6)
        ex = VGroup(M(r"x=1:\ \text{same as the star}", 32, GREY_),
                    M(r"x=5:\ \text{five times stellar}", 32, GREY_)).arrange(DOWN, buff=0.2)
        ex.next_to(eq, DOWN, buff=0.8)
        self.play(FadeIn(ex[0], shift=UP * 0.1), run_time=0.6)
        self.play(FadeIn(ex[1], shift=UP * 0.1), run_time=0.6)

        # beat 1 — the Sun's metal budget
        self.beat(1)
        self.play(FadeOut(VGroup(n1, n2, ex)), eq.animate.scale(0.6).to_corner(UR, buff=0.5).shift(DOWN * 0.15),
                  run_time=1.0)
        W, base_y = 11.0, -2.7
        segs = VGroup()
        x0 = -W / 2
        for el, f, col in SOLAR_SHARES:
            w = W * f
            r = Rectangle(width=w, height=0.8).set_fill(col, 0.85).set_stroke(BG, 2)
            r.move_to([x0 + w / 2, 0.2, 0])
            segs.add(r)
            x0 += w
        sym = VGroup()
        for (el, f, col), r in zip(SOLAR_SHARES, segs):
            if el == "rest":
                sym.add(VMobject())
                continue
            s = M(rf"\mathrm{{{el}}}", 30 if f > 0.04 else 22, BG).move_to(r)
            sym.add(s)
        pct = VGroup()
        for (el, f, col), r in zip(SOLAR_SHARES[:4], segs[:4]):
            pct.add(T(f"{100 * f:.0f}\\%", 26, col).next_to(r, DOWN, buff=0.15))
        brace = Brace(segs, UP, color=GREY_)
        blab = T(r"where the Sun's heavy-element mass lives", 28, GREY_).next_to(brace, UP, buff=0.12)
        self.play(LaggedStart(*[GrowFromEdge(r, LEFT) for r in segs], lag_ratio=0.12), run_time=2.2)
        self.play(FadeIn(sym), GrowFromCenter(brace), FadeIn(blab), run_time=0.9)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in pct[:2]], lag_ratio=0.5), run_time=1.0)
        self.wait(0.6)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.1) for p in pct[2:]], lag_ratio=0.4), run_time=0.8)

        # beat 2 — weighted average: widths = shares, heights = enrichment
        self.beat(2)
        h1 = 0.2  # screen units per 1x enrichment
        star_bars = VGroup()
        for r in segs:
            b = r.copy().stretch_to_fit_height(h1)
            b.move_to([r.get_center()[0], base_y + h1 / 2, 0])
            star_bars.add(b)
        xbar_eq = M(r"\bar{x} \;=\; \sum_i \Big(\tfrac{Z_i}{Z}\Big)_{\!\star} x_i", 46)
        xbar_eq.move_to(UP * 2.3 + LEFT * 2.6)
        wlab = T(r"width $=$ share of star's metal mass", 24, GREY_)
        hlab = T(r"height $=$ enrichment $x_i$", 24, GREY_)
        VGroup(wlab, hlab).arrange(DOWN, aligned_edge=LEFT, buff=0.12).next_to(xbar_eq, RIGHT, buff=0.9)
        self.play(FadeOut(VGroup(brace, blab, pct, sym, eq)), Transform(segs, star_bars), run_time=1.0)
        base = Line([-W / 2 - 0.2, base_y, 0], [W / 2 + 0.2, base_y, 0], color=GREY_, stroke_width=2)
        star_lbl = T(r"star: every $x_i=1$", 24, GOLD_).next_to(base, UP, buff=0.35).shift(LEFT * 3.2)
        self.play(Write(xbar_eq), FadeIn(base), FadeIn(star_lbl), run_time=1.1)
        self.play(FadeIn(wlab, shift=LEFT * 0.1), FadeIn(hlab, shift=LEFT * 0.1), run_time=0.6)
        # HR 8799 b values (Xuan et al. 2026); Fe, Mg, Si follow S; unmeasured Ne set to 0
        xs = {"O": 4.9, "C": 4.2, "Ne": 0.0, "Fe": 5.2, "N": 21.2, "Si": 5.2, "Mg": 5.2, "S": 5.2, "rest": 0.0}
        targets = VGroup()
        for (el, f, col), r in zip(SOLAR_SHARES, segs):
            hh = max(h1 * xs[el], 0.004)
            b = r.copy().stretch_to_fit_height(hh).move_to([r.get_center()[0], base_y + hh / 2, 0])
            targets.add(b)
        self.play(Transform(segs, targets), FadeOut(star_lbl), run_time=1.8, rate_func=smooth)
        el_lbls = VGroup(*[
            M(rf"\mathrm{{{el}}}", 22 if f < 0.06 else 26, col).next_to(t, UP, buff=0.08)
            for (el, f, col), t in zip(SOLAR_SHARES, targets) if xs[el] > 0
        ])
        self.play(FadeIn(el_lbls), run_time=0.5)
        xbar = sum(f * xs[e] for e, f, _ in SOLAR_SHARES)
        level = Rectangle(width=W, height=h1 * xbar).set_fill(METAL_C, 0.28).set_stroke(METAL_C, 2.5)
        level.move_to([0, base_y + h1 * xbar / 2, 0])
        self.play(TransformFromCopy(segs, level), run_time=1.5)
        xl = M(r"\bar{x}\approx 5", 34, METAL_C).move_to([-3.4, base_y + h1 * xbar + 0.75, 0])
        same = T("same total area", 22, METAL_C).next_to(xl, DOWN, buff=0.05)
        self.play(FadeIn(xl), FadeIn(same), run_time=0.5)

        # beat 3 — the compact formula + the curve
        self.beat(3)
        hist = VGroup(segs, base, el_lbls, level, xl, same, wlab, hlab)
        self.play(FadeOut(hist), xbar_eq.animate.scale(0.75).to_corner(UR, buff=0.5).shift(DOWN * 0.1),
                  run_time=1.0)
        zp1 = M(r"Z_p", r"=", r"\frac{\bar{x}}{(1-Z_\star)/Z_\star + \bar{x}}", 52).move_to(UP * 1.9)
        zp2 = M(r"Z_p", r"\approx", r"\frac{\bar{x}}{70 + \bar{x}}", 52).move_to(UP * 1.9)
        self.play(Write(zp1), run_time=1.3)
        zsun = T(r"Sun: $Z_\odot\approx0.014$", 24, GREY_).next_to(zp1, RIGHT, buff=0.6)
        self.play(FadeIn(zsun), run_time=0.5)
        self.play(TransformMatchingTex(zp1, zp2), run_time=1.0)
        zp = zp2
        self.play(zp.animate.scale(0.8).to_edge(LEFT, buff=0.6).shift(UP * 0.3), FadeOut(zsun), run_time=0.8)

        def zfun(u):
            x = 10 ** u
            return x / (70.4 + x)

        ax = Axes(x_range=[0, 3.3, 1], y_range=[0, 1, 0.25], x_length=7.6, y_length=4.3,
                  axis_config={"color": GREY_, "stroke_width": 2}, tips=False).move_to(RIGHT * 1.9 + DOWN * 1.15)
        xt = VGroup(*[M(lbl, 26, GREY_).next_to(ax.c2p(u, 0), DOWN, buff=0.15)
                      for u, lbl in [(0, r"1\times"), (1, r"10\times"), (2, r"100\times"), (3, r"1000\times")]])
        yt = VGroup(*[T(f"{int(v * 100)}\\%", 22, GREY_).next_to(ax.c2p(0, v), LEFT, buff=0.12)
                      for v in [0.25, 0.5, 0.75, 1.0]])
        xlab = M(r"\bar{x}", 30, GREY_).next_to(ax.x_axis, RIGHT, buff=0.15)
        ylab = T("metal mass fraction", 24, GREY_).next_to(ax.y_axis, UP, buff=0.15).shift(RIGHT * 0.9)
        crv = ax.plot(zfun, x_range=[0, 3.3, 0.01], color=METAL_C, stroke_width=4)
        self.play(Create(ax), FadeIn(xt), FadeIn(yt), FadeIn(xlab), FadeIn(ylab), run_time=1.0)
        self.play(Create(crv), run_time=1.3)
        u = ValueTracker(0)
        dot = always_redraw(lambda: Dot(ax.c2p(u.get_value(), zfun(u.get_value())), color=WHITE, radius=0.07))
        rd = always_redraw(lambda: T(f"{100 * zfun(u.get_value()):.0f}\\% metal", 24, INK)
                           .next_to(ax.c2p(u.get_value(), zfun(u.get_value())), UL, buff=0.12))
        self.add(dot, rd)
        self.play(u.animate.set_value(3.0), run_time=1.8)

        # beat 4 — zoom in, two contrasting examples
        self.beat(4)
        self.play(FadeOut(rd), FadeOut(dot), run_time=0.3)
        ax2 = Axes(x_range=[0, 1.5, 0.5], y_range=[0, 0.3, 0.05], x_length=7.6, y_length=4.3,
                   axis_config={"color": GREY_, "stroke_width": 2}, tips=False).move_to(ax)
        xt2 = VGroup(*[M(lbl, 26, GREY_).next_to(ax2.c2p(np.log10(v), 0), DOWN, buff=0.15)
                       for v, lbl in [(1, r"1\times"), (3, r"3\times"), (10, r"10\times"), (30, r"30\times")]])
        yt2 = VGroup(*[T(f"{int(v * 100)}\\%", 22, GREY_).next_to(ax2.c2p(0, v), LEFT, buff=0.12)
                       for v in [0.05, 0.1, 0.15, 0.2, 0.25, 0.3]])
        crv2 = ax2.plot(zfun, x_range=[0, 1.47, 0.005], color=METAL_C, stroke_width=4)
        self.play(ReplacementTransform(ax, ax2), ReplacementTransform(crv, crv2),
                  ReplacementTransform(xt, xt2), ReplacementTransform(yt, yt2), run_time=1.5)

        def mark(xv, col, text, direction, buff=0.25):
            p = ax2.c2p(np.log10(xv), zfun(np.log10(xv)))
            d = Dot(p, color=col, radius=0.08)
            h = DashedLine(ax2.c2p(0, zfun(np.log10(xv))), p, color=col, stroke_width=1.5, dash_length=0.08)
            lab = T(text, 24, col).next_to(p, direction, buff=buff)
            return d, h, lab

        d1, h1_, l1 = mark(10, INK, r"10$\times$ in \emph{all} metals $\to$ 12\%", UL)
        self.play(GrowFromCenter(d1), Create(h1_), FadeIn(l1, shift=DOWN * 0.1), run_time=1.0)
        self.wait(0.8)
        d2, h2_, l2 = mark(4.74, BLUE_, r"10$\times$ in oxygen only $\to$ 6\%", DR, 0.2)
        self.play(GrowFromCenter(d2), Create(h2_), FadeIn(l2, shift=UP * 0.1), run_time=1.0)

        # beat 5 — HR 8799 b
        self.beat(5)
        d3, h3_, l3 = mark(5.09, METAL_C, r"HR 8799 b $\to$ 6.5\%", RIGHT, 0.35)
        l3.shift(DOWN * 0.15 + RIGHT * 1.4)
        self.play(FadeOut(l1), FadeOut(l2), d1.animate.set_opacity(0.3), d2.animate.set_opacity(0.3),
                  h1_.animate.set_opacity(0.2), h2_.animate.set_opacity(0.2), run_time=0.6)
        self.play(GrowFromCenter(d3), Create(h3_), FadeIn(l3), run_time=1.0)
        pie_c = ax2.c2p(0.33, 0.215)
        body = gas_giant(0.85, seed=2).move_to(pie_c)
        wedge = AnnularSector(inner_radius=0, outer_radius=0.85, angle=0.065 * TAU, start_angle=PI / 2,
                              color=METAL_C, fill_opacity=0.95).move_arc_center_to(pie_c)
        body[0].set_fill(opacity=1)
        pie_lbl = T(r"$\approx 6.5\%$ of the planet's\\mass is metal", 24, METAL_C).next_to(body, RIGHT, buff=0.3)
        self.play(FadeIn(body, scale=0.7), run_time=0.8)
        self.play(GrowFromPoint(wedge, pie_c), FadeIn(pie_lbl), run_time=1.0)
        self.finish()


# --------------------------------------------------------------------------- #
# 2. Solids vs gas
# --------------------------------------------------------------------------- #
SNOW = [("H$_2$O", -3.0), ("CO$_2$", -0.2), ("CO", 3.0)]


def f_oxygen(x):
    """Toy fraction of oxygen in solids vs. disk position (screen x)."""
    lv = [0.25, 0.6, 0.75, 1.0]
    f = lv[0]
    for (name, xs), lo, hi in zip(SNOW, lv[:-1], lv[1:]):
        f += (hi - lo) / (1 + np.exp(-(x - xs) / 0.12))
    return f


def disk_shape(x0=-6.0, x1=7.2, h0=0.12, h1=1.15, y=0.0):
    xs = np.linspace(x0, x1, 40)
    hs = h0 + (h1 - h0) * ((xs - x0) / (x1 - x0)) ** 1.25
    top = [[x, y + h, 0] for x, h in zip(xs, hs)]
    bot = [[x, y - h, 0] for x, h in zip(xs[::-1], hs[::-1])]
    p = Polygon(*top, *bot).set_stroke(BLUE_, 1, 0.35).set_fill(BLUE_, 0.10)
    return p, (lambda x: h0 + (h1 - h0) * ((x - x0) / (x1 - x0)) ** 1.25)


class S2Split(Narrated):
    KEY = "s2_split"

    def construct(self):
        hdr = self.header("2", r"Solids vs.\ gas")
        dy = 0.9
        disk, hfun = disk_shape(y=dy)
        star = glow_star(0.32).move_to([-6.35, dy, 0])
        rng = np.random.default_rng(7)
        gas = VGroup()
        for _ in range(260):
            x = rng.uniform(-5.8, 7.1)
            hh = hfun(x)
            d = Dot([x, dy + rng.uniform(-0.9, 0.9) * hh, 0], radius=0.022, color=BLUE_)
            d.set_opacity(rng.uniform(0.25, 0.6))
            gas.add(d)
        peb = VGroup()
        for _ in range(70):
            x = rng.uniform(-5.6, 7.0)
            d = Dot([x, dy + rng.normal(0, 0.05), 0], radius=rng.uniform(0.03, 0.055), color=SOLID_C)
            peb.add(d)
        lines = VGroup()
        for name, xs in SNOW:
            hh = hfun(xs) + 0.25
            ln = DashedLine([xs, dy - hh, 0], [xs, dy + hh, 0], color=INK, stroke_width=1.5, dash_length=0.08)
            lab = T(name, 22, INK).next_to(ln, UP, buff=0.08)
            lines.add(VGroup(ln, lab))
        sl_lbl = T("snowlines", 22, GREY_).next_to(lines[-1], RIGHT, buff=0.25).shift(UP * 0.25)

        # beat 0
        self.beat(0)
        self.play(FadeIn(hdr, shift=RIGHT * 0.3), run_time=0.6)
        self.play(FadeIn(star), DrawBorderThenFill(disk), run_time=1.2)
        self.play(FadeIn(gas, lag_ratio=0.01), FadeIn(peb, lag_ratio=0.02), run_time=1.0)
        self.play(LaggedStart(*[Create(l[0]) for l in lines], lag_ratio=0.2),
                  LaggedStart(*[FadeIn(l[1]) for l in lines], lag_ratio=0.2), FadeIn(sl_lbl), run_time=1.0)
        tag_s = T("solids", 26, SOLID_C).move_to([-4.6, dy - 1.0, 0])
        tag_g = T("gas", 26, GAS_C).move_to([-4.6, dy + 1.0, 0])
        a_s = Arrow(tag_s.get_top(), [-4.2, dy - 0.05, 0], buff=0.08, color=SOLID_C, stroke_width=3,
                    max_tip_length_to_length_ratio=0.3)
        a_g = Arrow(tag_g.get_bottom(), [-4.3, dy + 0.12, 0], buff=0.08, color=GAS_C, stroke_width=3,
                    max_tip_length_to_length_ratio=0.3)
        self.play(FadeIn(tag_s), GrowArrow(a_s), FadeIn(tag_g), GrowArrow(a_g), run_time=0.7)

        # beat 1 — refractories ride only on solids
        self.beat(1)
        planet = gas_giant(0.42, seed=4).move_to([1.4, dy, 0])
        self.play(FadeIn(planet, scale=0.4), run_time=0.8)
        rbox = VGroup(
            T(r"\textbf{Refractories}: S, Fe, Mg, Si", 30, SOLID_C),
            T(r"locked in rock $\Rightarrow$ arrive \emph{only} with solids", 26, INK),
        ).arrange(DOWN, buff=0.15).move_to(DOWN * 1.55)
        self.play(FadeIn(rbox[0], shift=UP * 0.1), run_time=0.8)
        self.play(LaggedStart(*[Indicate(p, color=YELLOW, scale_factor=1.8) for p in peb[::3]],
                              lag_ratio=0.03), FadeIn(rbox[1], shift=UP * 0.1), run_time=1.8)
        # a handful of pebbles get eaten
        near = [p for p in peb if 0.0 < p.get_x() < 2.9][:8]
        self.play(LaggedStart(*[p.animate.move_to(planet.get_center()).scale(0.2).set_opacity(0)
                                for p in near], lag_ratio=0.12), run_time=1.6)
        xr = VGroup(M(r"x_{\mathcal R}", 48, SOLID_C), T(r"$=$ solid accreted per unit hydrogen", 30))
        xr.arrange(RIGHT, buff=0.2).move_to(DOWN * 2.9)
        box = SurroundingRectangle(xr, color=SOLID_C, buff=0.18, corner_radius=0.1)
        self.play(Write(xr), Create(box), run_time=1.4)

        # beat 2 — volatiles split by snowlines
        self.beat(2)
        self.play(FadeOut(VGroup(rbox, xr, box, tag_s, tag_g, a_s, a_g)), run_time=0.6)
        rx = ValueTracker(-5.0)
        probe = always_redraw(lambda: DashedLine([rx.get_value(), dy - 1.35, 0], [rx.get_value(), dy + 1.35, 0],
                                                 color=METAL_C, stroke_width=2.5, dash_length=0.1))
        BW = 6.0

        def obar():
            f = f_oxygen(rx.get_value())
            g = VGroup()
            s = Rectangle(width=max(BW * f, 1e-3), height=0.45).set_fill(SOLID_C, 0.9).set_stroke(width=0)
            gg = Rectangle(width=max(BW * (1 - f), 1e-3), height=0.45).set_fill(GAS_C, 0.9).set_stroke(width=0)
            s.move_to([-BW / 2 + BW * f / 2, -1.75, 0])
            gg.move_to([-BW / 2 + BW * f + BW * (1 - f) / 2, -1.75, 0])
            frame = Rectangle(width=BW, height=0.45).set_stroke(INK, 1.5).move_to([0, -1.75, 0])
            ls = M(rf"f_{{\mathcal V,s}}={f:.2f}", 30, SOLID_C).next_to(frame, DOWN, buff=0.18).align_to(frame, LEFT)
            lg = T(r"gas: $1-f$", 26, GAS_C).next_to(frame, DOWN, buff=0.2).align_to(frame, RIGHT)
            g.add(s, gg, frame, ls, lg)
            return g

        bar = always_redraw(obar)
        otitle = T(r"\textbf{Oxygen}: in solids \emph{vs.} gas", 28).move_to(DOWN * 1.05)
        self.play(FadeIn(probe), FadeIn(bar), FadeIn(otitle), run_time=0.8)
        self.play(rx.animate.set_value(6.4), run_time=4.5, rate_func=there_and_back_with_pause)
        self.play(rx.animate.set_value(1.4), run_time=1.6)

        # beat 3 — bookkeeping rule
        self.beat(3)
        probe.clear_updaters()
        bar.clear_updaters()
        scene_disk = VGroup(disk, star, gas, peb, lines, sl_lbl, planet, probe, bar, otitle)
        self.play(FadeOut(scene_disk), run_time=0.8)
        eq = M(r"x_{\mathcal V}", r"=", r"x_{\mathcal R}\, f_{\mathcal V,s}", r"+", r"(1-f_{\mathcal V,s})", 60)
        eq[2].set_color(SOLID_C)
        eq[4].set_color(GAS_C)
        eq.move_to(UP * 2.0)
        self.play(Write(eq), run_time=1.6)
        bs = Brace(eq[2], DOWN, color=SOLID_C)
        bg = Brace(eq[4], DOWN, color=GAS_C)
        ts = T("from solids", 24, SOLID_C).next_to(bs, DOWN, buff=0.08)
        tg = T("from gas", 24, GAS_C).next_to(bg, DOWN, buff=0.08)
        self.play(GrowFromCenter(bs), GrowFromCenter(bg), FadeIn(ts), FadeIn(tg), run_time=0.8)

        U = 1.55
        X0 = -5.6
        nl = NumberLine(x_range=[0, 7, 1], length=7 * U, color=GREY_, include_numbers=False,
                        stroke_width=2).move_to([X0 + 3.5 * U, -2.2, 0])
        nums = VGroup(*[M(rf"{k}\times", 24, GREY_).next_to(nl.n2p(k), DOWN, buff=0.15) for k in range(0, 8)])
        xrt = ValueTracker(1.0)
        fv = ValueTracker(0.73)

        def vbar():
            f, xR = fv.get_value(), xrt.get_value()
            ws, wg = U * xR * f, U * (1 - f)
            s = Rectangle(width=max(ws, 1e-3), height=0.55).set_fill(SOLID_C, 0.9).set_stroke(BG, 1)
            g = Rectangle(width=max(wg, 1e-3), height=0.55).set_fill(GAS_C, 0.9).set_stroke(BG, 1)
            s.move_to([X0 + ws / 2, -1.55, 0])
            g.move_to([X0 + ws + wg / 2, -1.55, 0])
            return VGroup(s, g)

        vb = always_redraw(vbar)
        xr_read = always_redraw(lambda: M(rf"x_{{\mathcal R}} = {xrt.get_value():.1f}", 32, SOLID_C)
                                .move_to([-4.4, 0.05, 0]))
        f_read = always_redraw(lambda: M(rf"f_{{\mathcal V,s}} = {fv.get_value():.2f}", 32, INK)
                               .next_to(xr_read, DOWN, buff=0.15))
        self.play(Create(nl), FadeIn(nums), FadeIn(vb), FadeIn(xr_read), FadeIn(f_read), run_time=1.0)
        self.play(xrt.animate.set_value(5.0), run_time=3.2)
        gas_note = T("gas share never grows:\\\\it brings its own hydrogen", 24, GAS_C)
        gas_note.move_to([1.2, -0.25, 0])
        gas_arr = Arrow(gas_note.get_bottom(), [X0 + U * 5 * 0.73 + U * 0.27 / 2, -1.25, 0], color=GAS_C,
                        stroke_width=3, buff=0.1)
        self.play(FadeIn(gas_note), GrowArrow(gas_arr), run_time=0.9)

        # beat 4 — the ceiling, and the excess
        self.beat(4)
        self.play(FadeOut(gas_note), FadeOut(gas_arr), run_time=0.4)
        ceil = DashedLine(nl.n2p(5) + UP * 1.05, nl.n2p(5) + DOWN * 0.05, color=INK, stroke_width=2.5)
        ceil_l = T(r"ceiling: $x_{\mathcal V}\le x_{\mathcal R}$", 24, INK).next_to(ceil, UP, buff=0.1)
        self.play(fv.animate.set_value(1.0), run_time=1.6)
        self.play(Create(ceil), FadeIn(ceil_l), run_time=0.8)
        self.play(fv.animate.set_value(0.73), run_time=1.0)
        meas = Dot(nl.n2p(6.6) + UP * 0.65, color=EXCESS_C, radius=0.1)
        meas_l = T("measured", 24, EXCESS_C).next_to(meas, UP, buff=0.4)
        self.play(FadeIn(meas, scale=2), FadeIn(meas_l), run_time=0.7)
        right_end = X0 + U * (5 * 0.73 + 0.27)
        exc = Rectangle(width=nl.n2p(6.6)[0] - right_end, height=0.55).set_fill(EXCESS_C, 0.85).set_stroke(BG, 1)
        exc.move_to([(right_end + nl.n2p(6.6)[0]) / 2, -1.55, 0])
        self.play(GrowFromEdge(exc, LEFT), run_time=0.9)
        exc_l = T(r"\textbf{excess}", 24, BG).move_to(exc)
        self.play(FadeIn(exc_l), run_time=0.4)
        eq15 = M(r"x_{\mathcal V}", r"=", r"x_{\mathcal R}\, f_{\mathcal V,s}", r"+", r"(1-f_{\mathcal V,s})", r"+",
                 r"g_{\mathcal V,\rm excess}", 56)
        eq15[2].set_color(SOLID_C)
        eq15[4].set_color(GAS_C)
        eq15[6].set_color(EXCESS_C)
        eq15.move_to(UP * 2.0)
        self.play(FadeOut(VGroup(bs, bg, ts, tg)), TransformMatchingTex(eq, eq15), run_time=1.2)
        be = Brace(eq15[6], DOWN, color=EXCESS_C)
        te = T(r"enriched gas, e.g.\ from\\drifting, evaporating pebbles", 22, EXCESS_C).next_to(be, DOWN, buff=0.08)
        self.play(GrowFromCenter(be), FadeIn(te), run_time=0.8)
        # tiny vignette: pebble crosses a snowline and loses its ice
        vx = 4.6
        sl = DashedLine([vx, 0.0, 0], [vx, 1.1, 0], color=INK, stroke_width=1.5, dash_length=0.06)
        pb = VGroup(Circle(0.17).set_fill(SOLID_C, 1).set_stroke(width=0),
                    Annulus(inner_radius=0.17, outer_radius=0.26).set_fill(GAS_C, 0.9).set_stroke(width=0))
        pb.move_to([vx + 1.2, 0.55, 0])
        self.play(FadeOut(te), FadeOut(be), Create(sl), FadeIn(pb), run_time=0.5)
        puff = VGroup(*[Dot([vx, 0.55, 0], radius=0.04, color=GAS_C) for _ in range(12)])
        self.play(pb.animate.move_to([vx - 1.3, 0.55, 0]), run_time=1.6, rate_func=linear)
        self.add(puff)
        self.play(FadeOut(pb[1], scale=1.6),
                  *[d.animate.shift(0.45 * np.array([np.cos(a), np.sin(a), 0])).set_opacity(0.5)
                    for d, a in zip(puff, np.linspace(0, TAU, 12, endpoint=False))], run_time=0.8)

        # beat 5 — excess is measurable
        self.beat(5)
        vign = VGroup(sl, pb, puff)
        self.play(FadeOut(vign), run_time=0.4)
        x_ex = M(r"\bar{x}_{\rm excess} = \big[(x_{\mathcal V}-1)-(x_{\mathcal R}-1)f_{\mathcal V,s}\big]"
                 r"\Big(\tfrac{Z_{\mathcal V}}{Z}\Big)_{\!\star}", 40, EXCESS_C)
        x_ex.move_to(UP * 0.55)
        bx = SurroundingRectangle(x_ex, color=EXCESS_C, buff=0.2, corner_radius=0.1)
        self.play(Write(x_ex), Create(bx), run_time=1.6)
        self.finish()


# --------------------------------------------------------------------------- #
# 3. Real planets: AF Lep b and HR 8799
# --------------------------------------------------------------------------- #
class S3Apps(Narrated):
    KEY = "s3_apps"

    def construct(self):
        hdr = self.header("3", r"Real planets")

        # beat 0 — AF Lep b, static disk works
        self.beat(0)
        self.play(FadeIn(hdr, shift=RIGHT * 0.3), run_time=0.8)
        pl = gas_giant(1.25, seed=5, base="#C9A27A",
                       band_colors=("#A57D5A", "#E0C29F", "#8F6A4B", "#D8B48E")).move_to(LEFT * 4.3 + DOWN * 0.1)
        name = T(r"\textbf{AF Lep b}", 34).next_to(pl, UP, buff=0.35)
        dist = T(r"$\sim$9 au from its star", 24, GREY_).next_to(pl, DOWN, buff=0.3)
        self.play(FadeIn(pl, scale=0.6), FadeIn(name), FadeIn(dist), run_time=1.2)
        rows = VGroup()
        for el, f, col, err in [("O", 0.73, BLUE_, r"0.73^{+0.22}_{-0.16}"), ("C", 0.51, "#C9CDD6", r"0.51^{+0.18}_{-0.13}")]:
            lab = M(rf"\mathrm{{{el}}}", 40, col)
            bar = split_bar([f, 1 - f], [SOLID_C, GAS_C], width=5.0, height=0.5)
            val = M(rf"f_s = {err}", 30, INK)
            r = VGroup(lab, bar, val).arrange(RIGHT, buff=0.35)
            rows.add(r)
        rows.arrange(DOWN, buff=0.55, aligned_edge=LEFT).move_to(RIGHT * 2.2 + UP * 0.25)
        legend = VGroup(
            VGroup(Square(0.22).set_fill(SOLID_C, 1).set_stroke(width=0), T("in solids", 22, SOLID_C)).arrange(RIGHT, buff=0.12),
            VGroup(Square(0.22).set_fill(GAS_C, 1).set_stroke(width=0), T("in gas", 22, GAS_C)).arrange(RIGHT, buff=0.12),
        ).arrange(RIGHT, buff=0.5).next_to(rows, UP, buff=0.4)
        self.play(FadeIn(legend), run_time=0.5)
        for r in rows:
            self.play(FadeIn(r[0]), GrowFromEdge(r[1], LEFT), FadeIn(r[2]), run_time=1.2)
        ok = T(r"static disk works \ding{51}", 30, GREEN_).next_to(rows, DOWN, buff=0.6)
        self.wait(2.0)
        self.play(FadeIn(ok, scale=1.2), run_time=0.7)
        note = T(r"$\approx$ half the carbon stays in refractory organics", 22, GREY_).next_to(ok, DOWN, buff=0.2)
        self.play(FadeIn(note), run_time=0.6)

        # beat 1 — 56 Earth masses of solids vs isolation masses
        self.beat(1)
        self.play(FadeOut(VGroup(rows, legend, ok, note)), run_time=0.6)
        ax_x0, ax_len = -1.0, 7.0
        to_x = lambda m: ax_x0 + ax_len * np.log10(m) / 2.0  # 1..100 Earth masses, log
        items = [("planetesimal isolation", 1.9, GREY_), ("flow isolation", 5.3, GREY_),
                 ("pebble isolation", 17, GREY_), ("AF Lep b metals (solids)", 56, METAL_C)]
        bars, lbls, vals = VGroup(), VGroup(), VGroup()
        for i, (lab, m, col) in enumerate(items):
            y = 1.4 - i * 0.85
            b = Rectangle(width=to_x(m) - ax_x0, height=0.5).set_fill(col, 0.85 if col == METAL_C else 0.55)
            b.set_stroke(width=0).move_to([ax_x0 + (to_x(m) - ax_x0) / 2, y, 0])
            bars.add(b)
            lbls.add(T(lab, 24, col if col == METAL_C else INK).next_to([ax_x0, y, 0], LEFT, buff=0.2))
            vals.add(M(rf"{m:g}\,M_\oplus", 28, col if col == METAL_C else INK).next_to(b, RIGHT, buff=0.15))
        axis = NumberLine(x_range=[0, 2, 1], length=ax_len, color=GREY_, include_ticks=True).move_to(
            [ax_x0 + ax_len / 2, -1.75, 0])
        ticks = VGroup(*[M(t, 24, GREY_).next_to(axis.n2p(k), DOWN, buff=0.12)
                         for k, t in enumerate([r"1", r"10", r"100\ M_\oplus"])])
        lbls.shift(RIGHT * 0)
        pl_small = VGroup(pl, name, dist)
        self.play(pl_small.animate.scale(0.45).to_corner(UR, buff=0.5).shift(DOWN * 0.4), run_time=0.8)
        self.play(Create(axis), FadeIn(ticks), run_time=0.6)
        for b, l, v in zip(bars[:3], lbls[:3], vals[:3]):
            self.play(FadeIn(l), GrowFromEdge(b, LEFT), FadeIn(v), run_time=0.55)
        self.play(FadeIn(lbls[3]), GrowFromEdge(bars[3], LEFT), run_time=1.3)
        self.play(FadeIn(vals[3], scale=1.3), Flash(vals[3], color=METAL_C), run_time=0.8)

        # beat 2 — HR 8799, static disk fails for inner three
        self.beat(2)
        self.play(FadeOut(VGroup(bars, lbls, vals, axis, ticks, pl_small)), run_time=0.8)
        star = glow_star(0.35).move_to(LEFT * 6.1 + DOWN * 0.3)
        au = lambda a: -5.5 + 11.6 * a / 90
        y0 = -0.3
        nl = NumberLine(x_range=[0, 90, 10], length=11.6, color=GREY_, stroke_width=1.5).move_to([au(45), -2.4, 0])
        nlab = VGroup(*[M(f"{k}", 20, GREY_).next_to(nl.n2p(k), DOWN, buff=0.1) for k in range(0, 91, 20)])
        au_l = T("au", 22, GREY_).next_to(nl, RIGHT, buff=0.15)
        P = [("e", 16), ("d", 27), ("c", 43), ("b", 68)]
        planets = VGroup()
        for i, (n, a) in enumerate(P):
            g = gas_giant(0.36, seed=10 + i).move_to([au(a), y0, 0])
            lab = T(f"\\textbf{{{n}}}", 28).next_to(g, DOWN, buff=0.2)
            orb = Arc(radius=au(a) - star.get_x(), start_angle=-0.22, angle=0.44, arc_center=star.get_center())
            orb.set_stroke(GREY_, 1, 0.3)
            planets.add(VGroup(orb, g, lab))
        title = T(r"\textbf{HR 8799}: four giant planets", 32).move_to(UP * 2.35)
        self.play(FadeIn(star), FadeIn(title), Create(nl), FadeIn(nlab), FadeIn(au_l), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(p, scale=0.5) for p in planets], lag_ratio=0.25), run_time=1.6)
        fails = VGroup()
        for p in planets[:3]:
            t = VGroup(M(r"f_s>1", 28, EXCESS_C), T(r"\ding{55}", 30, EXCESS_C)).arrange(RIGHT, buff=0.15)
            t.next_to(p[1], UP, buff=0.35)
            fails.add(t)
        st = T(r"static disk: needs $>$100\% of C and O in solids", 26, EXCESS_C).move_to(UP * 1.6)
        self.wait(2.8)
        self.play(LaggedStart(*[FadeIn(f, shift=DOWN * 0.15) for f in fails], lag_ratio=0.25), run_time=1.2)
        self.play(FadeIn(st), run_time=0.6)

        # beat 3 — CO-enriched gas inside the CO snowline; N2 for b
        self.beat(3)
        co_zone = Rectangle(width=au(55) - au(0), height=3.6).set_fill(BLUE_, 0.12).set_stroke(width=0)
        co_zone.move_to([(au(0) + au(55)) / 2, y0 + 0.2, 0])
        n2_zone = Rectangle(width=au(80) - au(55), height=3.6).set_fill(GREEN_, 0.12).set_stroke(width=0)
        n2_zone.move_to([(au(55) + au(80)) / 2, y0 + 0.2, 0])
        co_l = DashedLine([au(55), y0 - 1.6, 0], [au(55), y0 + 2.0, 0], color=BLUE_, stroke_width=2)
        n2_l = DashedLine([au(80), y0 - 1.6, 0], [au(80), y0 + 2.0, 0], color=GREEN_, stroke_width=2)
        co_t = T(r"CO snowline", 22, BLUE_).next_to(co_l, DOWN, buff=0.08).shift(RIGHT * 0.05)
        n2_t = T(r"N$_2$ snowline", 22, GREEN_).next_to(n2_l, DOWN, buff=0.08)
        self.play(FadeOut(st), FadeIn(co_zone), Create(co_l), FadeIn(co_t), run_time=1.0)
        co_gas = T(r"gas enriched in CO: $\sim$3$\times$ solar", 28, BLUE_).move_to([au(27), 1.55, 0])
        self.play(FadeIn(co_gas), run_time=0.7)
        oks = VGroup(*[T(r"\ding{51}", 40, GREEN_).move_to(f) for f in fails])
        self.play(LaggedStart(*[ReplacementTransform(f, o) for f, o in zip(fails, oks)], lag_ratio=0.2),
                  run_time=1.2)
        one = T("one value fits all three", 24, INK).next_to(co_gas, DOWN, buff=0.12)
        self.play(FadeIn(one), run_time=0.6)
        self.wait(1.6)
        self.play(FadeIn(n2_zone), Create(n2_l), FadeIn(n2_t), run_time=1.0)
        n2_gas = T(r"N$_2$-rich gas", 26, GREEN_).next_to(planets[3][1], UP, buff=0.4)
        self.play(FadeIn(n2_gas, shift=DOWN * 0.1), run_time=0.7)

        # beat 4 — no large migration required
        self.beat(4)
        msg = T(r"inferred birthplaces $\approx$ today's orbits: no large migration needed", 28, METAL_C)
        msg.move_to(UP * 2.35)
        self.play(ReplacementTransform(title, msg), run_time=1.0)
        self.play(LaggedStart(*[Indicate(p[1], color=METAL_C, scale_factor=1.25) for p in planets],
                              lag_ratio=0.2), run_time=1.6)
        mm = T(r"together: $\sim$410 $M_\oplus$ of metals", 24, GREY_).next_to(msg, DOWN, buff=0.12)
        self.play(FadeIn(mm), run_time=0.6)
        self.finish()


# --------------------------------------------------------------------------- #
# 4. Weighing the disk
# --------------------------------------------------------------------------- #
class S4Disk(Narrated):
    KEY = "s4_disk"

    def construct(self):
        hdr = self.header("4", r"Weighing the disk")

        # beat 0
        self.beat(0)
        self.play(FadeIn(hdr, shift=RIGHT * 0.3), run_time=0.8)
        big = T(r"A new \emph{minimum disk mass}", 56, METAL_C)
        sub = T(r"from the excess metals in a planet's atmosphere", 30, GREY_).next_to(big, DOWN, buff=0.3)
        self.play(Write(big), run_time=1.6)
        self.play(FadeIn(sub, shift=UP * 0.1), run_time=0.7)

        # beat 1 — pebbles cross the CO snowline, shedding ~17% of their mass
        self.beat(1)
        self.play(FadeOut(big), FadeOut(sub), run_time=0.6)
        my = 0.6
        mid = Line([-7.2, my, 0], [7.2, my, 0], color=GREY_, stroke_width=1).set_opacity(0.4)
        snow_x = 0.8
        sl = DashedLine([snow_x, my - 1.3, 0], [snow_x, my + 1.4, 0], color=BLUE_, stroke_width=2.5)
        sl_t = T("CO snowline", 24, BLUE_).next_to(sl, UP, buff=0.1)
        inside = T(r"$\leftarrow$ CO is gas", 22, BLUE_).move_to([snow_x - 1.4, my + 1.25, 0])
        outside = T(r"CO is ice $\rightarrow$", 22, GREY_).move_to([snow_x + 1.4, my + 1.25, 0])
        planet = gas_giant(0.45, seed=21).move_to([-4.6, my, 0])
        self.play(Create(mid), Create(sl), FadeIn(sl_t), FadeIn(inside), FadeIn(outside),
                  FadeIn(planet), run_time=1.0)

        clock = ValueTracker(0)
        rng = np.random.default_rng(11)
        N = 16
        phase = rng.uniform(0, 1, N)
        yoff = rng.normal(0, 0.28, N)
        speed, span, x_start = 2.2, 15.0, 7.4

        def pebbles():
            t = clock.get_value()
            g = VGroup()
            for k in range(N):
                s = (t * speed / span + phase[k]) % 1.0
                x = x_start - s * span
                y = my + yoff[k] * (0.6 + 0.4 * abs(x - planet.get_x()) / 7)
                core = Circle(0.09).set_fill(SOLID_C, 1).set_stroke(width=0).move_to([x, y, 0])
                g.add(core)
                if x > snow_x:
                    g.add(Annulus(inner_radius=0.09, outer_radius=0.14).set_fill(GAS_C, 0.95)
                          .set_stroke(width=0).move_to([x, y, 0]))
                else:
                    age = (snow_x - x) / speed
                    for j in range(5):
                        a = TAU * j / 5 + k
                        rr = 0.12 + 0.55 * min(age, 1.4)
                        d = Dot([snow_x - 0.6 * age * speed * 0.5 + rr * np.cos(a), y + rr * np.sin(a), 0],
                                radius=0.035, color=GAS_C).set_opacity(max(0.0, 0.85 - 0.3 * age))
                        g.add(d)
            return g

        peb = always_redraw(pebbles)
        self.add(peb)
        clock.add_updater(lambda m, dt: m.increment_value(dt))
        self.add(clock)
        # pie: pebble composition
        pie_c = np.array([4.6, -2.0, 0])
        ice = AnnularSector(inner_radius=0, outer_radius=0.7, angle=0.17 * TAU, start_angle=PI / 2,
                            color=GAS_C, fill_opacity=1).move_arc_center_to(pie_c)
        rock = AnnularSector(inner_radius=0, outer_radius=0.7, angle=0.83 * TAU, start_angle=PI / 2 + 0.17 * TAU,
                             color=SOLID_C, fill_opacity=1).move_arc_center_to(pie_c)
        pie_t = T(r"$\approx$17\% of a pebble's\\mass is CO ice", 26, GAS_C).next_to(pie_c, LEFT, buff=1.0)
        self.wait(3.0)
        self.play(FadeIn(rock), GrowFromPoint(ice, pie_c), FadeIn(pie_t), run_time=1.0)
        self.play(ice.animate.shift(0.18 * np.array([np.cos(PI / 2 + 0.17 * PI), np.sin(PI / 2 + 0.17 * PI), 0])),
                  run_time=0.8)

        # beat 2 — the arithmetic
        self.beat(2)
        eq = M(r"M_{\rm pebbles}\ \gtrsim\ \frac{M_{Z,\rm excess}}{\sum_{\mathcal V} f_{\mathcal V,[\rm mol]}\,(Z_{\mathcal V}/Z)_\star}",
               40).move_to([-2.8, -2.0, 0])
        self.play(FadeOut(pie_t), Write(eq), run_time=1.6)
        num = M(r"\frac{128\,M_\oplus}{0.17}", 46).move_to([-3.4, -2.0, 0])
        self.wait(1.5)
        self.play(ReplacementTransform(eq, num), run_time=1.0)
        eqs = M(r"\approx", 46).next_to(num, RIGHT, buff=0.3)
        val = DecimalNumber(0, num_decimal_places=0, font_size=60, color=METAL_C)
        unit = M(r"M_\oplus", 46, METAL_C)
        val.next_to(eqs, RIGHT, buff=0.3)
        unit.next_to(val, RIGHT, buff=0.15)
        grp = VGroup(val, unit)
        val.add_updater(lambda d: d.next_to(eqs, RIGHT, buff=0.3))
        unit.add_updater(lambda d: d.next_to(val, RIGHT, buff=0.15))
        self.play(FadeIn(eqs), FadeIn(unit), FadeIn(val), run_time=0.4)
        self.play(ChangeDecimalToValue(val, 750), run_time=2.0, rate_func=smooth)
        pm = M(r"\pm 200", 30, GREY_).next_to(unit, RIGHT, buff=0.2)
        unit.clear_updaters()
        self.play(FadeIn(pm), run_time=0.4)

        # beat 3 — nearly double the planets' metals
        self.beat(3)
        val.clear_updaters()
        clock.clear_updaters()
        self.play(FadeOut(VGroup(num, eqs, grp, pm, rock, ice, mid, sl, sl_t, inside, outside, planet, peb)),
                  run_time=0.8)
        base_y = -2.6
        k = 4.4 / 800
        b1 = Rectangle(width=1.6, height=750 * k).set_fill(SOLID_C, 0.85).set_stroke(width=0)
        b1.move_to([-1.8, base_y + 750 * k / 2, 0])
        b2 = Rectangle(width=1.6, height=410 * k).set_fill(METAL_C, 0.85).set_stroke(width=0)
        b2.move_to([1.8, base_y + 410 * k / 2, 0])
        gl = Line([-4, base_y, 0], [4, base_y, 0], color=GREY_)
        t1 = T(r"pebbles that drifted\\past the planets", 24).next_to(b1, DOWN, buff=0.15)
        t2 = T(r"metals in all\\four planets", 24).next_to(b2, DOWN, buff=0.15)
        v1 = M(r"\gtrsim 750\,M_\oplus", 32, SOLID_C).next_to(b1, UP, buff=0.12)
        v2 = M(r"\sim 410\,M_\oplus", 32, METAL_C).next_to(b2, UP, buff=0.12)
        VGroup(b1, b2, gl, t1, t2, v1, v2).shift(UP * 0.35)
        self.play(Create(gl), GrowFromEdge(b1, DOWN), GrowFromEdge(b2, DOWN), FadeIn(t1), FadeIn(t2), run_time=1.4)
        self.play(FadeIn(v1), FadeIn(v2), run_time=0.6)
        self.finish()


# --------------------------------------------------------------------------- #
# 5. Recipe + outro
# --------------------------------------------------------------------------- #
class S5Outro(Narrated):
    KEY = "s5_outro"

    def construct(self):
        steps = [
            (r"measure\\C, O + a refractory", BLUE_),
            (r"enrichment\\$\to$ mass", METAL_C),
            (r"split solids\\from gas", SOLID_C),
            (r"read the disk's\\history", EXCESS_C),
        ]
        boxes = VGroup()
        for txt, col in steps:
            t = T(txt, 29, col)
            b = RoundedRectangle(corner_radius=0.15, width=2.85, height=1.45).set_stroke(col, 2.5).set_fill(col, 0.08)
            boxes.add(VGroup(b, t.move_to(b)))
        boxes.arrange(RIGHT, buff=0.45).move_to(UP * 0.4)
        arrows = VGroup(*[Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.06, color=GREY_,
                                stroke_width=3, max_tip_length_to_length_ratio=0.35) for i in range(3)])
        title = T(r"\textbf{The recipe}", 40).move_to(UP * 2.5)

        # beat 0
        self.beat(0)
        self.play(FadeIn(title, shift=DOWN * 0.15), run_time=0.8)
        gaps = [2.3, 1.2, 1.1, 1.3]
        for i, b in enumerate(boxes):
            anims = [FadeIn(b, shift=UP * 0.15)]
            if i:
                anims.append(GrowArrow(arrows[i - 1]))
            self.play(*anims, run_time=0.8)
            self.wait(gaps[i])

        # beat 1
        self.beat(1)
        self.play(VGroup(title, boxes, arrows).animate.scale(0.7).shift(UP * 0.9), run_time=1.0)
        code = VGroup(T(r"\texttt{accomp}", 40, METAL_C),
                      T(r"open-source code: \texttt{github.com/y-chachan/accomp}", 26, GREY_)).arrange(DOWN, buff=0.15)
        code.move_to(DOWN * 1.0)
        cite = T(r"Chachan, Murray-Clay \& Fortney (2026), arXiv:2608.23682", 24, GREY_).move_to(DOWN * 2.6)
        stars = starfield(120, seed=9).set_opacity(0.35)
        self.play(FadeIn(code, shift=UP * 0.15), run_time=1.0)
        self.wait(2.0)
        self.play(FadeIn(cite), FadeIn(stars), run_time=1.2)
        self.finish(fade=1.5)
