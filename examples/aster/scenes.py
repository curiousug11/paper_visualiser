"""ASTER explainer: 3Blue1Brown-style walkthrough of arXiv:2603.26953.

Render one scene:   manim -qh scenes.py S1Transit
Render everything:  ./build.sh
"""
import numpy as np

from common import *  # noqa: F401,F403
from spectrum import DATASETS, bin_spectrum, depth_ppm, native_spectrum, observation


# ============================================================================ helpers
def fade_all(scene, rt=0.6):
    if scene.mobjects:
        scene.play(*[FadeOut(m) for m in scene.mobjects], run_time=rt)


def checkmark(color=GREEN_, s=0.32, w=7):
    m = VMobject().set_points_as_corners([[-0.5, 0.0, 0], [-0.15, -0.38, 0], [0.5, 0.42, 0]])
    return m.scale(s).set_stroke(color, w)


def xmark(color=RED_, s=0.26, w=7):
    return VGroup(Line(UL, DR), Line(UR, DL)).scale(s).set_stroke(color, w)


def person(color=INK, s=1.0):
    head = Circle(radius=0.17).set_fill(color, 1).set_stroke(width=0)
    body = RoundedRectangle(corner_radius=0.22, width=0.62, height=0.5).set_fill(color, 1).set_stroke(width=0)
    body.next_to(head, DOWN, buff=0.06)
    return VGroup(head, body).scale(s)


def labeled_axes(x_range, y_range, x_len, y_len, xticks=(), yticks=(), xlabel=None, ylabel=None, fs=22):
    ax = Axes(
        x_range=x_range, y_range=y_range, x_length=x_len, y_length=y_len, tips=False,
        axis_config=dict(stroke_color=DIM, stroke_width=2, include_ticks=False),
    )
    deco = VGroup()
    for v, s in xticks:
        p = ax.c2p(v, y_range[0])
        tick = Line(p, p + DOWN * 0.08, stroke_color=DIM, stroke_width=2)
        deco.add(tick, T(s, fs, DIM).next_to(tick, DOWN, buff=0.08))
    for v, s in yticks:
        p = ax.c2p(x_range[0], v)
        tick = Line(p, p + LEFT * 0.08, stroke_color=DIM, stroke_width=2)
        deco.add(tick, T(s, fs, DIM).next_to(tick, LEFT, buff=0.08))
    if xlabel:
        deco.add(T(xlabel, fs + 2, DIM).next_to(ax.x_axis, DOWN, buff=0.42 if xticks else 0.15))
    if ylabel:
        deco.add(T(ylabel, fs + 2, DIM).rotate(PI / 2).next_to(ax.y_axis, LEFT, buff=0.55 if yticks else 0.15))
    return ax, deco


def place(ax, deco, pos):
    v = np.array(pos) - ax.get_center()
    ax.shift(v)
    deco.shift(v)


def polyline(ax, xs, ys, color, width=3):
    return VMobject().set_points_as_corners([ax.c2p(x, y) for x, y in zip(xs, ys)]).set_stroke(color, width)


def smooth_curve(ax, f, x0, x1, color, width=3, n=300):
    xs = np.linspace(x0, x1, n)
    return VMobject().set_points_smoothly([ax.c2p(x, f(x)) for x in xs]).set_stroke(color, width)


def data_points(ax, lam, y, err, color, r=0.028, bar_op=0.55):
    g = VGroup()
    for l, v, e in zip(lam, y, err):
        g.add(Line(ax.c2p(l, v - e), ax.c2p(l, v + e), stroke_color=color, stroke_width=1.5, stroke_opacity=bar_op))
        g.add(Dot(ax.c2p(l, v), radius=r, color=color))
    return g


def pipeline_boxes():
    """The four stages of a transmission-spectroscopy analysis."""
    def box(color, title, sub, icon):
        rect = RoundedRectangle(corner_radius=0.18, width=2.75, height=2.15, stroke_color=color, stroke_width=3)
        rect.set_fill(color, 0.07)
        icon.move_to(rect.get_center() + UP * 0.38)
        t = T(title, 26).move_to(rect.get_center() + DOWN * 0.42)
        s = T(sub, 19, DIM).next_to(t, DOWN, buff=0.08)
        return VGroup(rect, icon, t, s)

    db = VGroup(*[Ellipse(width=0.9, height=0.26).shift(UP * 0.22 * i) for i in range(3)])
    db.add(Line(db[0].get_left(), db[2].get_left()), Line(db[0].get_right(), db[2].get_right()))
    db.set_stroke(BLUE_, 3)
    dl = VGroup(Arrow(UP * 0.45, DOWN * 0.15, buff=0, stroke_width=5, max_tip_length_to_length_ratio=0.35),
                VMobject().set_points_as_corners([[-0.45, -0.05, 0], [-0.45, -0.3, 0], [0.45, -0.3, 0], [0.45, -0.05, 0]]))
    dl.set_color(TEAL_)
    xs = np.linspace(0.55, 5.4, 120)
    ys = depth_ppm(xs)
    fm = VMobject().set_points_smoothly([[(x - 3) / 2.6, (v - 21300) / 1900, 0] for x, v in zip(xs, ys)]).set_stroke(YELLOW_, 3)
    gx = np.linspace(-1, 1, 80)
    post = VMobject().set_points_smoothly([[x * 0.55, 0.62 * np.exp(-x * x * 6) - 0.25, 0] for x in gx]).set_stroke(PURPLE_, 3)
    post.add(Line([-0.6, -0.27, 0], [0.6, -0.27, 0], stroke_color=PURPLE_, stroke_width=2))
    boxes = VGroup(
        box(BLUE_, "Archive query", "NASA Exoplanet Archive", db),
        box(TEAL_, "Data download", "JWST spectra", dl),
        box(YELLOW_, "Forward model", "TauREx", fm),
        box(PURPLE_, "Bayesian retrieval", "nested sampling", post),
    ).arrange(RIGHT, buff=0.55)
    return boxes


# ============================================================================ 1. transit
class S1Transit(Narrated):
    def construct(self):
        stars = starfield()
        self.play(FadeIn(stars, lag_ratio=0.002), run_time=1.0)

        # ---------------- face-on transit + light curve
        RS, RP, B = 2.0, 0.30, -0.6
        SC = UP * 1.15
        star = glowing_star(RS).move_to(SC)
        xt = ValueTracker(-4.6)
        atm = Annulus(inner_radius=RP, outer_radius=RP + 0.06, stroke_width=0).set_fill(BLUE_, 0.45)
        body = Circle(radius=RP, stroke_width=1, stroke_color="#2a3142").set_fill("#0d1018", 1)
        planet = VGroup(atm, body)
        planet.add_updater(lambda m: m.move_to(SC + np.array([xt.get_value(), B, 0])))

        def overlap(x):
            d = np.hypot(x, B)
            r, R = RP, RS
            if d >= R + r:
                return 0.0
            if d <= R - r:
                return np.pi * r * r
            a = r * r * np.arccos((d * d + r * r - R * R) / (2 * d * r))
            b = R * R * np.arccos((d * d + R * R - r * r) / (2 * d * R))
            c = 0.5 * np.sqrt((-d + r + R) * (d + r - R) * (d - r + R) * (d + r + R))
            return a + b - c

        def flux(x):
            return 1 - overlap(x) / (np.pi * RS * RS)

        ax, deco = labeled_axes([0, 9.2, 1], [0.972, 1.004, 0.01], 8.6, 1.6)
        lc = lambda x, y: ax.c2p(x + 4.6, y)  # noqa: E731  planet x -> light-curve point
        place(ax, deco, DOWN * 2.75)
        lc_lab = T("brightness", 24, DIM).next_to(ax.y_axis, LEFT, buff=0.2).shift(UP * 0.35)
        t_lab = T("time", 24, DIM).next_to(ax.x_axis, RIGHT, buff=0.15)
        curve = always_redraw(
            lambda: ax.plot(lambda u: flux(u - 4.6), x_range=[0, max(xt.get_value() + 4.6, 0.02), 0.02],
                            color=YELLOW_, stroke_width=3)
        )
        head = always_redraw(lambda: Dot(lc(xt.get_value(), flux(xt.get_value())), radius=0.06, color=YELLOW_))
        star_lab = T("WASP-39", 26, GOLD_).next_to(star[1], UP, buff=0.15).shift(RIGHT * 2.2)
        pl_lab = T("WASP-39b", 26, BLUE_).next_to(SC + np.array([-4.6, B, 0]), UP, buff=0.35)

        self.narrate("s1a")
        self.play(FadeIn(star, scale=0.85), FadeIn(star_lab), run_time=1.2)
        self.play(Create(ax), FadeIn(lc_lab), FadeIn(t_lab), FadeIn(planet), FadeIn(pl_lab), run_time=0.8)
        self.add(curve, head)
        self.play(xt.animate.set_value(-0.2), FadeOut(pl_lab), run_time=self.remaining() - 0.2, rate_func=linear)

        self.narrate("s1b")
        self.play(xt.animate.set_value(4.6), run_time=2.4, rate_func=linear)
        x0 = 3.2
        brace = BraceBetweenPoints(lc(x0, flux(0)), lc(x0, 1.0), direction=RIGHT, color=INK)
        brace_lab = T(r"$\approx 2\%$", 28).next_to(brace, RIGHT, buff=0.1)
        self.play(GrowFromCenter(brace), FadeIn(brace_lab), run_time=0.7)
        curve.clear_updaters()
        head.clear_updaters()
        planet.clear_updaters()
        transit_group = VGroup(star, planet, ax, curve, head, brace, brace_lab, lc_lab, t_lab, star_lab)

        # ---------------- side view: starlight through the atmosphere
        P0 = np.array([0.4, -0.3, 0])
        R_SURF, R_TOP = 1.35, 1.95
        side_star = glowing_star(3.0).move_to([-9.6, -0.3, 0])
        layers = VGroup()
        for i in range(7):
            a = i / 6
            r_out = R_SURF + (R_TOP - R_SURF) * (1 - a)
            layers.add(Circle(radius=r_out, stroke_width=0).set_fill(BLUE_, 0.07 + 0.09 * a))
        layers.move_to(P0)
        pbody = Circle(radius=R_SURF, stroke_width=0).move_to(P0)
        pbody.set_fill(["#46536e", "#10141c"], 1).set_sheen_direction(RIGHT)
        mols = VGroup()
        for ang, txt in [(148, r"H$_2$O"), (32, r"CO$_2$"), (212, r"CO$_2$"), (328, r"H$_2$O"), (180, r"H$_2$O")]:
            a = np.deg2rad(ang)
            mols.add(T(txt, 20, INK).move_to(P0 + 1.84 * np.array([np.cos(a), np.sin(a), 0])).set_opacity(0.75))
        scope = jwst_mirror(0.16).move_to([6.1, -0.3, 0])
        scope_lab = T("JWST", 22, DIM).next_to(scope, DOWN, buff=0.15)
        side = VGroup(side_star, layers, pbody, mols, scope, scope_lab)

        self.play(FadeOut(transit_group), run_time=0.6)
        self.play(FadeIn(side), run_time=0.6)

        def ray(y, color, stop=None):
            y_abs = P0[1] + y
            x_end = stop if stop is not None else 5.55
            return Line([-6.4, y_abs, 0], [x_end, y_abs, 0], stroke_color=color, stroke_width=3.5)

        stop_x = P0[0] - 0.35
        rays_pass = [ray(1.58, BLUE_), ray(-1.58, GREEN_), ray(2.45, INK)]
        rays_abs = [ray(1.50, ORANGE_, stop_x), ray(-1.50, RED_, stop_x)]
        self.play(
            LaggedStart(*[Create(r, rate_func=linear) for r in rays_pass + rays_abs], lag_ratio=0.12),
            run_time=1.6,
        )
        self.play(*[Flash(r.get_end(), color=r.get_color(), line_length=0.14, flash_radius=0.18, num_lines=8)
                    for r in rays_abs], run_time=0.6)

        self.narrate("s1c")
        big = DashedVMobject(Circle(radius=1.66, color=ORANGE_, stroke_width=3), num_dashes=60).move_to(P0)
        small = DashedVMobject(Circle(radius=1.42, color=BLUE_, stroke_width=3), num_dashes=60).move_to(P0)
        big_lab = T("absorbing color: looks bigger", 24, ORANGE_).move_to([3.4, 2.8, 0])
        small_lab = T("transparent color: looks smaller", 24, BLUE_).move_to([3.0, -2.85, 0])
        self.play(Create(big), FadeIn(big_lab, shift=DOWN * 0.2), run_time=1.1)
        self.play(Create(small), FadeIn(small_lab, shift=UP * 0.2), run_time=0.9)
        eq = M(r"\delta(\lambda) = \left(\frac{\textcolor{yel}{R_p(\lambda)}}{R_\star}\right)^{2}", 56)
        eq.to_edge(UP, buff=0.3).shift(LEFT * 3.2)
        eq_bg = BackgroundRectangle(eq, fill_color=BG, fill_opacity=0.0, buff=0.15)
        self.play(FadeIn(eq_bg), Write(eq), run_time=1.5)

        # ---------------- color-by-color: build the spectrum
        self.narrate("s1d")
        rays_all = VGroup(*rays_pass, *rays_abs)
        self.play(
            FadeOut(VGroup(side, rays_all, big, small, big_lab, small_lab)),
            VGroup(eq_bg, eq).animate.scale(0.72).to_corner(UL, buff=0.35),
            run_time=0.7,
        )
        SC2 = np.array([-4.3, -0.6, 0])
        star2 = glowing_star(1.75, n_glow=8).move_to(SC2)
        lt = ValueTracker(0.5)
        ax2, deco2 = labeled_axes(
            [0.5, 5.5, 1], [20500, 22650, 500], 6.6, 3.7,
            xticks=[(v, str(v)) for v in (1, 2, 3, 4, 5)], xlabel=r"wavelength ($\mu$m)", ylabel="transit depth",
        )
        place(ax2, deco2, [2.75, -0.55, 0])

        def r_eff(lam):
            return 0.42 + 0.55 * (depth_ppm(lam) - 20700) / 1650

        pcen = SC2 + np.array([0.25, -0.3, 0])
        ring = always_redraw(lambda: Circle(radius=r_eff(lt.get_value()), stroke_width=2,
                                            stroke_color=wl_color(lt.get_value())).set_fill(wl_color(lt.get_value()), 0.5).move_to(pcen))
        pdisk = Circle(radius=0.42, stroke_width=0).set_fill("#0d1018", 1).move_to(pcen)
        lam_txt = always_redraw(lambda: sans(f"λ = {lt.get_value():.2f} µm", 24, wl_color(lt.get_value()))
                                .next_to(star2[1], DOWN, buff=0.35))
        nts = T("(not to scale)", 18, FAINT).next_to(lam_txt, DOWN, buff=0.12)

        segs_x = np.linspace(0.5, 5.5, 251)
        segs = [ax2.plot(depth_ppm, x_range=[a, b, (b - a) / 3], color=wl_color((a + b) / 2), stroke_width=4)
                for a, b in zip(segs_x[:-1], segs_x[1:])]
        trace = VGroup()

        def upd_trace(m):
            k = int(np.searchsorted(segs_x, lt.get_value())) - 1
            while len(m.submobjects) < max(k, 0):
                m.add(segs[len(m.submobjects)])

        trace.add_updater(upd_trace)
        head2 = always_redraw(lambda: Dot(ax2.c2p(lt.get_value(), depth_ppm(lt.get_value())), radius=0.07,
                                          color=wl_color(lt.get_value())))
        drop = always_redraw(lambda: DashedLine(ax2.c2p(lt.get_value(), 20500), ax2.c2p(lt.get_value(), depth_ppm(lt.get_value())),
                                                stroke_width=1.5, color=wl_color(lt.get_value()), dash_length=0.06))
        self.play(FadeIn(star2), FadeIn(pdisk), FadeIn(ring), FadeIn(lam_txt), FadeIn(nts),
                  Create(ax2), FadeIn(deco2), run_time=0.7)
        self.add(trace, drop, head2)
        self.play(lt.animate.set_value(5.5), run_time=3.4, rate_func=linear)
        trace.clear_updaters()
        feats = VGroup()
        for lam, txt in [(0.589, "Na"), (1.40, r"H$_2$O"), (1.88, r"H$_2$O"), (2.74, r"H$_2$O"), (4.33, r"CO$_2$")]:
            feats.add(T(txt, 20, INK).next_to(ax2.c2p(lam, depth_ppm(lam)), UP, buff=0.12))
        title = T("transmission spectrum", 32, YELLOW_).next_to(ax2, UP, buff=0.25)
        self.play(LaggedStart(*[FadeIn(f, shift=UP * 0.1) for f in feats], lag_ratio=0.15), Write(title), run_time=0.9)
        self.finish_beat()
        fade_all(self, 0.6)


# ============================================================================ 2. pipeline problem
class S2Pipeline(Narrated):
    def construct(self):
        boxes = pipeline_boxes().shift(UP * 0.2)
        arrows = VGroup(*[Arrow(boxes[i].get_right(), boxes[i + 1].get_left(), buff=0.08, stroke_width=4,
                                color=DIM, max_tip_length_to_length_ratio=0.3) for i in range(3)])
        head = T("From photons to physics", 36, INK).to_edge(UP, buff=0.6)

        self.narrate("s2a")
        self.play(FadeIn(head, shift=DOWN * 0.2), run_time=0.8)
        self.wait(1.2)
        for i, t_at in enumerate([2.2, 3.3, 4.6, 6.3]):
            self.wait_until(t_at)
            anims = [FadeIn(boxes[i], shift=UP * 0.25)]
            if i > 0:
                anims.append(GrowArrow(arrows[i - 1]))
            self.play(*anims, run_time=0.6)

        self.narrate("s2b")
        tag_spec = [("*.csv", 0, -0.7, 1.55), ("*.tbl", 0, 0.6, -1.5), ("*.py", 0, -0.6, -1.55),
                    ("wget", 1, 0.0, 1.6), ("*.dat", 1, -0.5, -1.5), ("*.json", 1, 0.7, -1.6),
                    ("opacities", 2, -0.4, 1.6), ("*.h5", 2, 0.8, 1.45), ("*.npy", 2, 0.2, -1.55),
                    ("MultiNest", 3, 0.0, 1.6), ("*.fits", 3, -0.6, -1.5), ("*.ipynb", 3, 0.6, -1.6)]
        rng = np.random.default_rng(4)
        tag_mobs = VGroup()
        for t, bi, dx, dy in tag_spec:
            m = mono(t, 18, color=[BLUE_, TEAL_, YELLOW_, PURPLE_][bi])
            m.move_to(boxes[bi].get_center() + np.array([dx, dy, 0])).rotate(rng.uniform(-0.2, 0.2))
            tag_mobs.add(m)
        tangles = VGroup()
        for i in range(3):
            a, b = boxes[i].get_right(), boxes[i + 1].get_left()
            for k in range(3):
                pts = [a + UP * rng.uniform(-0.6, 0.6)]
                for j in range(5):
                    pts.append(a + (b - a) * (j + 1) / 6 + np.array([0, rng.uniform(-1.0, 1.0), 0]))
                pts.append(b + UP * rng.uniform(-0.6, 0.6))
                tangles.add(VMobject().set_points_smoothly(pts).set_stroke(RED_, 2, opacity=0.75))
        self.play(LaggedStart(*[FadeIn(t, scale=0.6) for t in tag_mobs], lag_ratio=0.08), run_time=1.4)
        self.play(ReplacementTransform(arrows, tangles), run_time=1.0)
        self.play(*[Wiggle(b, scale_value=1.04, rotation_angle=0.02 * TAU) for b in boxes], run_time=1.0)
        self.finish_beat()
        # hand the boxes over to the next scene
        self.play(FadeOut(VGroup(tag_mobs, tangles, head)), run_time=0.5)


# ============================================================================ 3. the agent
def ctx_bar(kind, text=None, width=3.0):
    color = {"System": PINK_, "User": RED_, "Agent": BLUE_, "Tool": YELLOW_}[kind]
    rect = RoundedRectangle(corner_radius=0.1, width=width, height=0.62, stroke_color=color, stroke_width=2.5)
    rect.set_fill(BG, 1)
    tag = sans(kind, 15, color).move_to(rect.get_corner(UL) + RIGHT * 0.42)
    tag_bg = Rectangle(width=tag.width + 0.12, height=tag.height + 0.04, stroke_width=0).set_fill(BG, 1).move_to(tag)
    if text is None:
        body = VGroup(Line(LEFT * 1.0, RIGHT * 1.0), Line(LEFT * 1.0, RIGHT * 0.5)).arrange(DOWN, buff=0.12, aligned_edge=LEFT)
        body.set_stroke(DIM, 2).move_to(rect).shift(DOWN * 0.04)
    else:
        body = mono(text, 13, INK).move_to(rect).shift(DOWN * 0.04)
        if body.width > width - 0.3:
            body.scale_to_fit_width(width - 0.3)
    return VGroup(rect, tag_bg, tag, body)


class S3Agent(Narrated):
    def construct(self):
        boxes = pipeline_boxes().shift(UP * 0.2)
        self.add(boxes)

        # ---------------- title
        self.narrate("s3a")
        self.play(boxes.animate.scale(0.55).to_edge(DOWN, buff=0.95), run_time=1.0)
        flower = ImageMobject(str(ASSETS / "aster_flower.png")).set_height(1.9).move_to([-3.4, 1.85, 0])
        name = Text("ASTER", font="Georgia", weight=BOLD, font_size=110, color=INK).next_to(flower, RIGHT, buff=0.35)
        sub = T(r"\textcolor{yel}{A}gentic \textcolor{yel}{S}cience \textcolor{yel}{T}oolkit for "
                r"\textcolor{yel}{E}xoplanet \textcolor{yel}{R}esearch", 34)
        sub.next_to(Group(flower, name), DOWN, buff=0.3)
        self.play(FadeIn(flower, scale=0.6), FadeIn(name, shift=LEFT * 0.3), run_time=1.0)
        self.play(Write(sub), run_time=1.2)
        hub = sub.get_bottom() + DOWN * 0.15
        links = VGroup(*[Line(hub, b.get_top(), stroke_color=GREEN_, stroke_width=2.5) for b in boxes])
        self.play(LaggedStart(*[Create(l) for l in links], lag_ratio=0.15),
                  *[b[0].animate.set_stroke(GREEN_) for b in boxes], run_time=1.3)
        orch = T("built on the Orchestral AI framework", 22, DIM).next_to(boxes, DOWN, buff=0.22)
        self.play(FadeIn(orch), run_time=0.5)

        # ---------------- anatomy: LLM, context, tools
        self.narrate("s3b")
        self.play(FadeOut(Group(flower, name, sub, links, boxes, orch)), run_time=0.6)
        llm_box = RoundedRectangle(corner_radius=0.25, width=2.7, height=1.7, stroke_color=BLUE_, stroke_width=3)
        llm_box.set_fill(BLUE_, 0.10).move_to([0, 0.9, 0])
        llm_lab = T("LLM", 46).move_to(llm_box).shift(UP * 0.18)
        prov = sans("OpenAI · Anthropic · Google · local", 13, DIM).next_to(llm_lab, DOWN, buff=0.18)
        prov.scale_to_fit_width(2.3)
        llm = VGroup(llm_box, llm_lab, prov)

        ctx_box = RoundedRectangle(corner_radius=0.2, width=3.5, height=5.6, stroke_color=INK, stroke_width=2.5)
        ctx_box.set_fill(INK, 0.03).move_to([-4.65, -0.35, 0])
        ctx_title = T("Context", 32).next_to(ctx_box.get_top(), DOWN, buff=0.2)
        bars = [ctx_bar("System")]
        slots = [ctx_title.get_bottom() + DOWN * (0.55 + 0.82 * i) for i in range(6)]
        bars[0].move_to(slots[0])

        tool_box = RoundedRectangle(corner_radius=0.2, width=3.6, height=5.6, stroke_color=GOLD_, stroke_width=2.5)
        tool_box.set_fill(GOLD_, 0.04).move_to([4.65, -0.35, 0])
        tool_title = T("Tools", 32).next_to(tool_box.get_top(), DOWN, buff=0.2)
        names = [("GetExoplanetParameters", GOLD_), ("DownloadDataset", GOLD_), ("SetTaurexPaths", GOLD_),
                 ("RunTaurexModel", GOLD_), ("SimulateTaurexRetrieval", GOLD_), ("RunPython", BLUE_),
                 ("RunCommand", BLUE_), ("Read / Write / EditFile", BLUE_), ("WebSearch", BLUE_)]
        chips = VGroup(*[chip(n, c, 14, pad=0.11) for n, c in names]).arrange(DOWN, buff=0.12)
        chips.next_to(tool_title, DOWN, buff=0.25)
        for c in chips:
            if c.width > 3.3:
                c.scale_to_fit_width(3.3)
        legend = VGroup(sans("ASTER", 13, GOLD_), sans("built-in", 13, BLUE_)).arrange(RIGHT, buff=0.4)
        legend.next_to(tool_box.get_bottom(), UP, buff=0.15)

        self.wait(0.9)
        self.play(GrowFromCenter(llm), run_time=0.7)
        self.wait(0.45)
        self.play(FadeIn(VGroup(ctx_box, ctx_title)), FadeIn(bars[0], shift=DOWN * 0.15), run_time=0.8)
        self.wait_until(4.7)
        self.play(FadeIn(VGroup(tool_box, tool_title, legend)),
                  LaggedStart(*[FadeIn(c, shift=LEFT * 0.2) for c in chips], lag_ratio=0.1), run_time=1.3)

        # ---------------- the loop
        self.narrate("s3c")
        user_msg = VGroup()
        utxt = sans("Can you give me parameters of wasp39 b?", 20)
        ubox = RoundedRectangle(corner_radius=0.15, width=utxt.width + 0.5, height=utxt.height + 0.45,
                                stroke_color=RED_, stroke_width=2.5).set_fill(BG, 1)
        user_msg.add(ubox, utxt.move_to(ubox), sans("User", 14, RED_).next_to(ubox, UP, buff=0.06, aligned_edge=LEFT))
        user_msg.move_to([-0.6, 3.35, 0])
        self.play(FadeIn(user_msg, shift=DOWN * 0.25), run_time=0.7)
        ub = ctx_bar("User", "parameters of wasp39 b?").move_to(slots[1])
        self.play(ReplacementTransform(user_msg, ub), run_time=0.8)
        bars.append(ub)

        a1 = Arrow(ctx_box.get_right() + UP * 1.25, llm_box.get_left(), buff=0.1, stroke_width=4, color=INK)
        self.play(GrowArrow(a1), run_time=0.5)
        self.play(Indicate(llm_box, color=BLUE_, scale_factor=1.06), run_time=0.6)

        code = mono('GetExoplanetParameters(\n    planet_name="WASP-39b")', 15, INK)
        cbox = RoundedRectangle(corner_radius=0.12, width=code.width + 0.4, height=code.height + 0.4,
                                stroke_color=GOLD_, stroke_width=2.5).set_fill(BG, 1)
        call = VGroup(cbox, code.move_to(cbox), sans("tool call", 13, GOLD_).next_to(cbox, UP, buff=0.05, aligned_edge=LEFT))
        call.next_to(llm_box, DOWN, buff=0.6)
        self.play(TransformFromCopy(llm_box, cbox), FadeIn(VGroup(call[1], call[2])), run_time=0.9)
        self.play(call.animate.scale(0.6).move_to(chips[0]).set_opacity(0), Indicate(chips[0], color=YELLOW_), run_time=0.9)

        resp = mono("pl_radj  = 1.279\npl_bmassj = 0.281\npl_eqt   = 1166 K", 14, INK)
        rbox = RoundedRectangle(corner_radius=0.12, width=resp.width + 0.4, height=resp.height + 0.35,
                                stroke_color=YELLOW_, stroke_width=2.5).set_fill(BG, 1)
        response = VGroup(rbox, resp.move_to(rbox)).move_to([1.4, -1.9, 0])
        self.play(FadeIn(response, shift=LEFT * 0.4), run_time=0.6)
        tb = ctx_bar("Tool", "R_p=1.279 R_J  M_p=0.281 M_J  1166 K").move_to(slots[2])
        self.play(ReplacementTransform(response, tb), run_time=0.8)
        bars.append(tb)

        p_ctx_top = ctx_box.get_right() + UP * 1.25
        p_tool_top = tool_box.get_left() + UP * 1.25
        p_tool_bot = tool_box.get_left() + DOWN * 2.1
        p_ctx_bot = ctx_box.get_right() + DOWN * 2.1
        ret = ArcBetweenPoints(p_tool_bot, p_ctx_bot, angle=-0.55)
        path = VMobject()
        path.set_points_as_corners([p_ctx_top, llm_box.get_left(), llm_box.get_right(), p_tool_top, p_tool_bot])
        path.append_vectorized_mobject(ret)
        path.add_line_to(p_ctx_top)
        arrows = VGroup(
            Arrow(llm_box.get_right(), p_tool_top, buff=0.1, stroke_width=4, color=TEAL_),
            CurvedArrow(p_tool_bot, p_ctx_bot, angle=-0.55, stroke_width=4, color=TEAL_),
            Arrow(p_ctx_top, llm_box.get_left(), buff=0.1, stroke_width=4, color=TEAL_),
        )
        loop_lab = T("repeat until no more tool calls", 22, TEAL_).next_to(ret, DOWN, buff=0.08)
        loop = VGroup(arrows, loop_lab)
        self.play(FadeOut(a1), Create(arrows), FadeIn(loop_lab), run_time=0.8)
        runner = Dot(radius=0.09, color=TEAL_)
        self.play(MoveAlongPath(runner, path), run_time=1.0, rate_func=linear)
        self.play(MoveAlongPath(runner, path), run_time=0.7, rate_func=linear)
        abar = ctx_bar("Agent", "Here are the parameters for WASP-39b...").move_to(slots[3])
        self.play(FadeOut(runner), FadeIn(abar, shift=RIGHT * 0.2), run_time=0.6)
        bars.append(abar)

        # ---------------- safety hooks
        self.narrate("s3d")
        cap = T("the LLM never executes code directly", 30, DIM).to_edge(UP, buff=0.3)
        gate = RoundedRectangle(corner_radius=0.1, width=0.32, height=3.3, stroke_color=TEAL_, stroke_width=2.5)
        gate.set_fill(TEAL_, 0.15).move_to([2.25, -0.35, 0])
        gate_lab = T("hooks", 22, TEAL_).next_to(gate, DOWN, buff=0.12)
        human = person(INK, 0.8).move_to([2.25, 2.6, 0])
        human_lab = T("you", 20, DIM).next_to(human, RIGHT, buff=0.12)
        self.play(FadeOut(loop), FadeIn(cap), FadeIn(VGroup(gate, gate_lab)),
                  VGroup(ctx_box, ctx_title, *bars).animate.set_opacity(0.35), run_time=0.7)
        self.play(FadeIn(VGroup(human, human_lab)), run_time=0.4)

        start = llm_box.get_bottom() + DOWN * 0.55

        def send(label, color):
            c = chip(label, color, 14, pad=0.1).move_to(start)
            return c

        c1 = send("ls linelists/", GREEN_)
        self.play(FadeIn(c1, shift=DOWN * 0.2), run_time=0.3)
        self.play(c1.animate.move_to(gate.get_center() + LEFT * 0.0), run_time=0.45)
        ok = checkmark().next_to(gate, UP, buff=0.1).shift(DOWN * 0.15 + RIGHT * 0.45)
        self.play(c1.animate.move_to(chips[6]).set_opacity(0), FadeIn(ok), gate.animate.set_stroke(GREEN_), run_time=0.6)
        self.play(FadeOut(ok), gate.animate.set_stroke(TEAL_), run_time=0.2)

        c2 = send("rm -rf ~/", RED_)
        self.play(FadeIn(c2, shift=DOWN * 0.2), run_time=0.3)
        self.play(c2.animate.next_to(gate, LEFT, buff=0.05), run_time=0.4)
        no = xmark().move_to(c2)
        self.play(FadeIn(no, scale=1.6), gate.animate.set_stroke(RED_), run_time=0.35)
        self.play(FadeOut(VGroup(c2, no), scale=0.3), gate.animate.set_stroke(TEAL_), run_time=0.4)

        c3 = send("pip install ...", YELLOW_)
        self.play(FadeIn(c3, shift=DOWN * 0.2), run_time=0.3)
        self.play(c3.animate.next_to(gate, LEFT, buff=0.05), gate.animate.set_stroke(YELLOW_), run_time=0.4)
        q = T("?", 40, YELLOW_).next_to(gate, UP, buff=0.05)
        self.play(FadeIn(q), c3.animate.next_to(human, LEFT, buff=0.25), run_time=0.6)
        ok2 = checkmark().next_to(human, UP, buff=0.05)
        self.play(FadeIn(ok2, scale=1.4), run_time=0.35)
        self.play(c3.animate.move_to(chips[5]).set_opacity(0), FadeOut(q), FadeOut(ok2), gate.animate.set_stroke(TEAL_), run_time=0.6)
        self.finish_beat()
        fade_all(self, 0.6)


# ============================================================================ 4. tools vs skills
class S4ToolsSkills(Narrated):
    def construct(self):
        div = DashedLine(UP * 3.2, DOWN * 3.4, color=FAINT, dash_length=0.12)
        lh = T("Tool", 46, GOLD_).move_to([-3.6, 3.0, 0])
        lsub = T("fixed interface — reliable", 24, DIM).next_to(lh, DOWN, buff=0.12)
        rh = T("Skill", 46, TEAL_).move_to([3.6, 3.0, 0])
        rsub = T("plain-language guidance — flexible", 24, DIM).next_to(rh, DOWN, buff=0.12)

        self.narrate("s4a")
        self.play(Create(div), FadeIn(lh), FadeIn(lsub), FadeIn(rh.copy().set_opacity(0.25)), run_time=0.8)
        ghost_r = VGroup(rh, rsub)
        self.wait(0.8)
        llm_tag = sans("LLM writes:", 18, BLUE_).move_to([-5.3, 1.35, 0])
        l1 = mono("import taurex", 20, INK)
        l2 = mono("taurex.run_transit(planet, star)", 20, INK)
        codeg = VGroup(l1, l2).arrange(DOWN, aligned_edge=LEFT, buff=0.18).next_to(llm_tag, DOWN, aligned_edge=LEFT, buff=0.2)
        self.play(FadeIn(llm_tag), AddTextLetterByLetter(l1), run_time=0.7)
        self.play(AddTextLetterByLetter(l2), run_time=1.1)
        self.wait(0.7)
        strike = Line(l2[7].get_left() + LEFT * 0.05, l2[17].get_right() + RIGHT * 0.05, stroke_color=RED_, stroke_width=4)
        err = mono("AttributeError: no attribute 'run_transit'", 15, RED_).next_to(codeg, DOWN, aligned_edge=LEFT, buff=0.25)
        self.play(Create(strike), l2[7:18].animate.set_color(RED_), FadeIn(err, shift=UP * 0.1), run_time=0.9)
        self.wait(max(self.remaining() - 2.2, 0.1))
        sig = mono("RunTaurexModel(\n    star_radius, planet_radius,\n    planet_mass, planet_temp,\n    atm_min_pressure, ...)", 17, INK)
        sbox = RoundedRectangle(corner_radius=0.15, width=sig.width + 0.5, height=sig.height + 0.5,
                                stroke_color=GOLD_, stroke_width=3).set_fill(GOLD_, 0.08)
        tool = VGroup(sbox, sig.move_to(sbox)).move_to([-3.6, -1.75, 0])
        ok = checkmark().next_to(sbox, RIGHT, buff=0.2)
        self.play(FadeIn(tool, shift=UP * 0.3), VGroup(llm_tag, codeg, strike, err).animate.set_opacity(0.35), run_time=1.0)
        self.play(FadeIn(ok, scale=1.5), run_time=0.4)

        self.narrate("s4b")
        doc = VGroup()
        page = VMobject().set_points_as_corners([[-1.4, 1.2, 0], [0.95, 1.2, 0], [1.4, 0.75, 0], [1.4, -1.2, 0],
                                                  [-1.4, -1.2, 0], [-1.4, 1.2, 0]]).set_stroke(TEAL_, 2.5).set_fill(TEAL_, 0.06)
        fold = VMobject().set_points_as_corners([[0.95, 1.2, 0], [0.95, 0.75, 0], [1.4, 0.75, 0]]).set_stroke(TEAL_, 2)
        lines = VGroup(
            mono("corner_plots.md", 15, TEAL_),
            sans("# Corner plot best practices", 14, INK),
            sans("• overlay both retrievals", 14, DIM),
            sans("• blue vs red, label medians", 14, DIM),
            sans("• share axis ranges", 14, DIM),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.16).move_to(page).shift(LEFT * 0.08)
        doc.add(page, fold, lines)
        doc.move_to([2.0, 0.2, 0])
        self.play(FadeIn(ghost_r), FadeIn(doc, shift=UP * 0.2), run_time=0.9)

        # mini corner plot drawn by the agent
        cp = VGroup()
        o = np.array([5.0, -1.9, 0])
        s = 0.95
        for i in range(2):
            for j in range(i + 1):
                frame = Square(side_length=s, stroke_color=FAINT, stroke_width=1.5).move_to(o + np.array([j * s, -i * s, 0]))
                cp.add(frame)
                if i == j:
                    for color, mu, sg in [(BLUE_, 0.0, 0.28), (RED_, 0.18, 0.08)]:
                        xs = np.linspace(-0.45, 0.45, 50)
                        cp.add(VMobject().set_points_smoothly([frame.get_center() + np.array([x, 0.42 * np.exp(-0.5 * ((x - mu) / sg) ** 2) - 0.42, 0]) for x in xs])
                               .set_stroke(color, 2))
                else:
                    cp.add(Ellipse(width=0.6, height=0.25, color=BLUE_, stroke_width=2).rotate(-0.6).move_to(frame))
                    cp.add(Ellipse(width=0.16, height=0.08, color=RED_, stroke_width=2).rotate(-0.6).move_to(frame).shift(RIGHT * 0.15 + UP * 0.1))
        cp.move_to([2.0, -2.45, 0])
        arr = Arrow(doc.get_bottom(), cp.get_top(), buff=0.1, color=DIM, stroke_width=3)
        cp_lab = T("agent writes the plotting code itself", 20, DIM).next_to(cp, RIGHT, buff=0.3)
        self.play(GrowArrow(arr), LaggedStart(*[Create(m) for m in cp], lag_ratio=0.05), FadeIn(cp_lab), run_time=1.6)
        self.finish_beat()
        fade_all(self, 0.6)


# ============================================================================ 5. case study
class S5CaseStudy(Narrated):
    def construct(self):
        self.narrate("s5a")
        head = T("Case study: WASP-39b", 40).to_corner(UL, buff=0.45)
        self.play(FadeIn(head, shift=RIGHT * 0.2), run_time=0.8)

        src = chip("GetExoplanetParameters  →  NASA Exoplanet Archive", GOLD_, 14, pad=0.1)
        rows = [(r"R_\star", r"0.939\,R_\odot"), (r"M_\star", r"0.913\,M_\odot"), (r"T_{\rm eff}", r"5485\,\mathrm{K}"),
                (r"R_p", r"1.279\,R_J"), (r"M_p", r"0.281\,M_J"), (r"T_{\rm eq}", r"1166\,\mathrm{K}")]
        table = VGroup()
        for i, (k, v) in enumerate(rows):
            km = M(k, 36, BLUE_ if i >= 3 else GOLD_)
            vm = M(v, 36)
            table.add(VGroup(km, vm))
        for i, r in enumerate(table):
            r[0].move_to([-5.6, 1.35 - 0.62 * i, 0], aligned_edge=RIGHT)
            r[1].next_to(r[0], RIGHT, buff=0.7)
            r[1].move_to([r[1].get_center()[0], r[0].get_center()[1], 0])
            eqs = M("=", 36, DIM).move_to((r[0].get_right() + r[1].get_left()) / 2)
            r.add(eqs)
        src.next_to(table, UP, buff=0.35).align_to(table, LEFT).shift(LEFT * 0.3)
        self.wait(0.6)
        self.play(FadeIn(src, shift=DOWN * 0.15), run_time=0.5)
        self.play(LaggedStart(*[FadeIn(r, shift=RIGHT * 0.2) for r in table], lag_ratio=0.18), run_time=1.8)

        # forward model on a log-wavelength axis (x = log10(lambda / 0.5))
        L0 = 0.5
        lx = lambda lam: np.log10(lam / L0)  # noqa: E731
        ax, deco = labeled_axes(
            [0, lx(12.0), 0.1], [20500, 24300, 500], 7.8, 4.6,
            xticks=[(lx(v), str(v)) for v in (0.5, 1, 2, 5, 10)], xlabel=r"wavelength ($\mu$m)", ylabel="transit depth",
        )
        place(ax, deco, [2.55, -0.55, 0])
        lam_n, dep_n = native_spectrum()
        sel = np.arange(0, len(lam_n), 6)
        sel = sel[dep_n[sel] < 24250]
        pts = np.array([ax.c2p(lx(l), d) for l, d in zip(lam_n[sel], dep_n[sel])])
        cloud = PMobject(stroke_width=2.5)
        all_rgba = np.tile(np.array([[0.55, 0.57, 0.62, 0.55]]), (len(pts), 1))

        def reveal(m, a):
            k = max(int(a * len(pts)), 1)
            m.points = pts[:k]
            m.rgbas = all_rgba[:k]

        cloud.points = pts[:1]
        cloud.rgbas = all_rgba[:1]
        fm_lab = T("TauREx forward model (native resolution)", 22, DIM).next_to(ax, UP, buff=0.15)
        self.play(Create(ax), FadeIn(deco), run_time=0.8)
        self.add(cloud)
        self.play(UpdateFromAlphaFunc(cloud, reveal), FadeIn(fm_lab), run_time=2.4, rate_func=linear)

        # ---------------- rebinning to instrument resolutions
        self.narrate("s5b")
        prompt = sans("“Can you now bin the forward model down to JWST medium resolution?”", 17, INK)
        prompt.set_style(fill_opacity=0.9).next_to(head, DOWN, buff=0.18, aligned_edge=LEFT)
        self.play(FadeIn(prompt, shift=DOWN * 0.1), run_time=0.7)
        specs = [(700, 0.6, 2.8, BLUE_, "NIRISS-like  R≈700"), (1000, 2.9, 5.3, ORANGE_, "NIRSpec-like  R≈1000"),
                 (100, 5.0, 12.0, GREEN_, "MIRI-like  R≈100")]
        curves, labels = VGroup(), VGroup()
        for i, (R, a, b, col, txt) in enumerate(specs):
            c, v = bin_spectrum(lam_n, dep_n, R, a, b)
            curves.add(polyline(ax, lx(c), v, col, 2.6))
            labels.add(chip(txt, col, 13, mono_font=False, pad=0.08))
        labels.arrange(DOWN, aligned_edge=LEFT, buff=0.1).move_to(ax.c2p(lx(0.62), 23700), aligned_edge=UL)
        for c, l in zip(curves, labels):
            self.play(Create(c, rate_func=linear), FadeIn(l, shift=RIGHT * 0.1), run_time=1.0)
        # Ariel
        prompt2 = sans("“Can you now bin the forward model down to Ariel resolution?”", 17, INK).move_to(prompt, aligned_edge=LEFT)
        ariel = VGroup()
        for R, a, b in [(30, 1.25, 1.95), (60, 1.95, 3.9), (30, 3.9, 7.8)]:
            c, v = bin_spectrum(lam_n, dep_n, R, a, b)
            xs, ys = [], []
            edges = np.sqrt(c[:-1] * c[1:])
            edges = np.concatenate([[a], edges, [b]])
            for k in range(len(c)):
                xs += [lx(edges[k]), lx(edges[k + 1])]
                ys += [v[k], v[k]]
            ariel.add(polyline(ax, xs, ys, PINK_, 3.5))
        ariel_lab = chip("Ariel-like  R≈30–200", PINK_, 13, mono_font=False, pad=0.08).next_to(labels, DOWN, aligned_edge=LEFT, buff=0.1)
        self.play(ReplacementTransform(prompt, prompt2), curves.animate.set_stroke(opacity=0.35), run_time=0.6)
        self.play(Create(ariel), FadeIn(ariel_lab), run_time=1.1)
        note = T("instrument specs never provided — chosen by the agent", 22, YELLOW_).next_to(ax, DOWN, buff=0.75)
        self.play(FadeIn(note, shift=UP * 0.1), run_time=0.6)

        # ---------------- nine public datasets
        self.narrate("s5c")
        base_a = all_rgba[:, 3].copy()

        def fade_cloud(m, a):
            m.rgbas[:, 3] = base_a[: len(m.rgbas)] * (1 - a)

        self.play(FadeOut(VGroup(table, src, ax, deco, curves, labels, ariel, ariel_lab, note, prompt2, fm_lab)),
                  UpdateFromAlphaFunc(cloud, fade_cloud), run_time=0.6)
        self.remove(cloud)
        ax3, deco3 = labeled_axes(
            [0.5, 5.6, 1], [20300, 22900, 500], 11.0, 4.9,
            xticks=[(v, str(v)) for v in (1, 2, 3, 4, 5)], xlabel=r"wavelength ($\mu$m)", ylabel="transit depth",
        )
        place(ax3, deco3, [0.35, -0.5, 0])
        cols = [RED_, ORANGE_, BLUE_, GREEN_, PURPLE_, TEAL_, PINK_, YELLOW_, "#9AA7FF"]
        sets = VGroup()
        for d, c in zip(DATASETS, cols):
            lam, y, e = observation(*d["lam"], d["n"], d["sigma"], d["offset"], d["seed"])
            sets.add(data_points(ax3, lam, y, e, c, r=0.025))
        lab9 = T("9 public JWST NIRSpec datasets, downloaded by the agent", 26).next_to(head, DOWN, buff=0.25, aligned_edge=LEFT)
        self.play(Create(ax3), FadeIn(deco3), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(s, lag_ratio=0.01) for s in sets], lag_ratio=0.3), FadeIn(lab9), run_time=2.6)
        r1 = T("retrieval 1", 24, BLUE_).move_to(ax3.c2p(4.75, 22700))
        r2 = T("retrieval 2", 24, RED_).move_to(ax3.c2p(1.0, 22300))
        self.play(*[s.animate.set_opacity(0.1) for i, s in enumerate(sets) if i not in (0, 2)],
                  FadeIn(r1), FadeIn(r2), run_time=1.0)
        self.finish_beat()
        fade_all(self, 0.6)


# ============================================================================ 6. Bayes + nested sampling
class S6Retrieval(Narrated):
    def construct(self):
        self.narrate("s6a")
        q = T("Which atmospheres could explain this data?", 40).to_edge(UP, buff=0.6)
        self.play(Write(q), run_time=1.3)
        post = M(r"P(\theta \mid D)", 64, YELLOW_)
        eqs = M("=", 64)
        num = VGroup(M(r"\mathcal{L}(D \mid \theta)", 64, BLUE_), M(r"\pi(\theta)", 64, GREEN_)).arrange(RIGHT, buff=0.18)
        den = M(r"\mathcal{Z}", 64, PURPLE_)
        bar = Line(LEFT, RIGHT, stroke_width=3, color=INK).set_width(num.width + 0.25)
        frac = VGroup(num, bar, den).arrange(DOWN, buff=0.16)
        bayes = VGroup(post, eqs, frac).arrange(RIGHT, buff=0.35).move_to(UP * 0.3)
        self.play(Write(bayes), run_time=1.8)
        labs = VGroup(
            T("posterior", 26, YELLOW_).next_to(post, DOWN, buff=0.5),
            T("likelihood", 26, BLUE_).next_to(num[0], UP, buff=0.3),
            T("prior", 26, GREEN_).next_to(num[1], UP, buff=0.3),
            T("evidence", 26, PURPLE_).next_to(den, DOWN, buff=0.3),
        )
        self.play(LaggedStart(*[FadeIn(l, shift=0.1 * DOWN) for l in labs], lag_ratio=0.2), run_time=1.3)
        theta = M(r"\theta = \left(T,\; R_p,\; \log X_{\rm H_2O},\; \log X_{\rm CO_2},\; \dots\right)", 36, DIM).to_edge(DOWN, buff=1.0)
        self.play(FadeIn(theta, shift=UP * 0.1), run_time=0.8)

        # ---------------- nested sampling in a 2D slice
        self.narrate("s6b")
        eq_small = VGroup(bayes, labs)
        self.play(FadeOut(q), FadeOut(theta), eq_small.animate.scale(0.45).to_corner(UR, buff=0.4), run_time=0.8)

        S = 5.6
        C = np.array([-1.6, -0.45, 0])
        plane = Square(side_length=S, stroke_color=DIM, stroke_width=2).move_to(C)
        xl = M("T", 34, DIM).next_to(plane, DOWN, buff=0.15)
        yl = M("R_p", 34, DIM).next_to(plane, LEFT, buff=0.15)

        mu = np.array([0.56, 0.44])
        ang = np.deg2rad(-38)
        rot = np.array([[np.cos(ang), -np.sin(ang)], [np.sin(ang), np.cos(ang)]])
        sig = np.diag([0.17 ** 2, 0.04 ** 2])
        cov = rot @ sig @ rot.T
        icov = np.linalg.inv(cov)

        def logL(u):
            d = u - mu
            return -0.5 * np.einsum("...i,ij,...j->...", d, icov, d)

        def to_scene(u):
            return C + np.array([(u[0] - 0.5) * S, (u[1] - 0.5) * S, 0])

        def contour(c, **kw):
            """Iso-likelihood ellipse with -2 logL = c."""
            e = Ellipse(width=2 * np.sqrt(c) * 0.17 * S, height=2 * np.sqrt(c) * 0.04 * S, **kw)
            return e.rotate(ang).move_to(to_scene(mu))

        heat = VGroup(*[contour(c, stroke_width=0).set_fill(BLUE_, 0.07) for c in (10, 6, 3.5, 2, 1, 0.35)])
        self.play(Create(plane), FadeIn(xl), FadeIn(yl), FadeIn(heat), run_time=0.7)

        rng = np.random.default_rng(11)
        N = 100
        live = rng.random((N, 2))
        L = logL(live)
        dots = [Dot(to_scene(u), radius=0.04, color=INK) for u in live]
        counter = always_redraw(lambda: VGroup(sans("live points: 100", 18, DIM)).next_to(plane, RIGHT, buff=0.3).shift(UP * 1.8))
        self.play(LaggedStart(*[FadeIn(d, scale=0.3) for d in dots], lag_ratio=0.01), FadeIn(counter), run_time=1.0)

        def step():
            i = int(np.argmin(L))
            lmin = L[i]
            while True:
                u = rng.random(2)
                if logL(u) > lmin:
                    break
            live[i] = u
            L[i] = logL(u)
            return i, u, lmin

        iter_txt = sans("iteration 0", 18, DIM).next_to(counter, DOWN, aligned_edge=LEFT)
        self.add(iter_txt)
        it = 0
        cur_contour = None
        # a few slow iterations, one at a time
        for _ in range(6):
            i, u, lmin = step()
            it += 1
            worst = dots[i]
            new = Dot(to_scene(u), radius=0.04, color=GREEN_)
            self.play(worst.animate.set_color(RED_).scale(1.8), run_time=0.17)
            self.play(FadeOut(worst, scale=0.2), FadeIn(new, scale=2), run_time=0.2)
            new.set_color(INK)
            dots[i] = new
            iter_txt.become(sans(f"iteration {it}", 18, DIM).move_to(iter_txt, aligned_edge=LEFT))
        # then fast batches while the iso-likelihood contour shrinks
        lmin_lab = sans("worst live point's contour", 16, TEAL_)
        for b in range(22):
            removed, added = [], []
            batch_lmin = None
            for _ in range(20):
                i, u, lmin = step()
                it += 1
                batch_lmin = lmin
                if dots[i] is not None:
                    removed.append(dots[i])
                nd = Dot(to_scene(u), radius=0.04, color=INK)
                dots[i] = nd
                added.append(nd)
            c = -2 * batch_lmin
            anims = [*[FadeOut(d) for d in removed if d in self.mobjects], *[FadeIn(d) for d in added]]
            new_c = DashedVMobject(contour(c, stroke_color=TEAL_, stroke_width=2.5), num_dashes=40)
            fits = 2 * np.sqrt(c) * 0.17 * S < S * 0.98
            if fits:
                if cur_contour is None:
                    anims += [FadeIn(new_c), FadeIn(lmin_lab.next_to(new_c, UP, buff=0.05))]
                else:
                    anims += [Transform(cur_contour, new_c), lmin_lab.animate.next_to(new_c, UP, buff=0.05)]
            iter_txt.become(sans(f"iteration {it}", 18, DIM).move_to(iter_txt, aligned_edge=LEFT))
            self.play(*anims, run_time=0.16, rate_func=linear)
            if fits and cur_contour is None:
                cur_contour = new_c
            # ghosts of discarded points
            for d in removed:
                if d in self.mobjects:
                    self.remove(d)

        # posterior marginals along the edges
        xs = np.linspace(0, 1, 120)
        sx, sy = np.sqrt(cov[0, 0]), np.sqrt(cov[1, 1])
        top = VMobject().set_points_smoothly([to_scene([x, 1.0]) + UP * (0.75 * np.exp(-0.5 * ((x - mu[0]) / sx) ** 2) + 0.05)
                                              for x in xs]).set_stroke(YELLOW_, 3)
        right = VMobject().set_points_smoothly([to_scene([1.0, y]) + RIGHT * (0.75 * np.exp(-0.5 * ((y - mu[1]) / sy) ** 2) + 0.05)
                                                for y in xs]).set_stroke(YELLOW_, 3)
        plab = T("posterior", 24, YELLOW_).next_to(top, UP, buff=0.0).shift(RIGHT * 1.6)
        self.play(Create(top), Create(right), FadeIn(plab), run_time=0.7)
        self.finish_beat()
        fade_all(self, 0.6)


# ============================================================================ 7. results
class S7Results(Narrated):
    def construct(self):
        self.narrate("s7a")
        ax, deco = labeled_axes(
            [0.5, 5.6, 1], [20400, 22900, 500], 10.6, 3.0,
            xticks=[(v, str(v)) for v in (1, 2, 3, 4, 5)], ylabel="depth", fs=20,
        )
        place(ax, deco, [0.4, 1.75, 0])
        lam_r, y_r, e_r = observation(0.52, 5.4, 120, 90, 40, 1)
        lam_b, y_b, e_b = observation(3.0, 5.5, 75, 120, 90, 3)
        pts_r = data_points(ax, lam_r, y_r, e_r, RED_, r=0.026, bar_op=0.4).set_opacity(0.55)
        pts_b = data_points(ax, lam_b, y_b, e_b, BLUE_, r=0.026, bar_op=0.4).set_opacity(0.55)
        fit_r = smooth_curve(ax, lambda l: depth_ppm(l) + 30, 0.52, 5.4, RED_, 3)
        fit_b = smooth_curve(ax, lambda l: depth_ppm(l) + 70 + 60 * np.sin(l * 2.2), 3.0, 5.5, BLUE_, 3)
        head = T("two retrievals, run autonomously", 30).to_edge(UP, buff=0.25)
        self.play(FadeIn(head), Create(ax), FadeIn(deco), run_time=0.8)
        self.play(FadeIn(pts_r, lag_ratio=0.01), FadeIn(pts_b, lag_ratio=0.01), run_time=1.0)
        self.play(Create(fit_r), Create(fit_b), run_time=1.0)

        def cov_bar(a, b, color, txt, dy):
            y = ax.get_bottom()[1] - 0.55 - dy
            bar = Line(ax.c2p(a, 20400) * [1, 0, 0] + [0, y, 0], ax.c2p(b, 20400) * [1, 0, 0] + [0, y, 0],
                       stroke_color=color, stroke_width=7)
            lab = T(txt, 20, color).next_to(bar, LEFT, buff=0.15)
            return VGroup(bar, lab)

        # posterior panels
        panels = VGroup()
        specs = [(r"$R_p$ [$R_J$]", 1.26, 1.33, [(1.27, "1.27"), (1.30, "1.30")]),
                 (r"$\log X_{\rm H_2O}$", -9.3, -2.7, [(-8, "$-8$"), (-6, "$-6$"), (-4, "$-4$")]),
                 (r"$\log X_{\rm CO_2}$", -9.3, -2.7, [(-8, "$-8$"), (-6, "$-6$"), (-4, "$-4$")])]
        pax = []
        for k, (name, lo, hi, ticks) in enumerate(specs):
            a, d = labeled_axes([lo, hi, (hi - lo) / 5], [0, 1.1, 0.5], 3.6, 1.55, xticks=ticks, fs=18)
            place(a, d, [-4.3 + 4.3 * k, -2.25, 0])
            ttl = T(name, 24).next_to(a, UP, buff=0.12)
            panels.add(VGroup(a, d, ttl))
            pax.append(a)
        self.play(FadeIn(panels), run_time=0.6)

        def dens(a, f, lo, hi, color, op=0.25):
            xs = np.linspace(lo, hi, 220)
            ys = np.array([f(x) for x in xs])
            ys = ys / ys.max()
            curve = VMobject().set_points_smoothly([a.c2p(x, y) for x, y in zip(xs, ys)]).set_stroke(color, 3)
            area = VMobject().set_points_as_corners([a.c2p(lo, 0), *[a.c2p(x, y) for x, y in zip(xs, ys)], a.c2p(hi, 0)])
            area.set_fill(color, op).set_stroke(width=0)
            return VGroup(area, curve)

        g = lambda m, s: (lambda x: np.exp(-0.5 * ((x - m) / s) ** 2))  # noqa: E731
        half = lambda s: (lambda x: np.exp(-0.5 * ((x + 9) / s) ** 2) if x > -9 else 0.0)  # noqa: E731
        red_post = VGroup(dens(pax[0], g(1.300, 0.0013), 1.26, 1.33, RED_),
                          dens(pax[1], g(-4.0, 0.12), -9, -2.7, RED_),
                          dens(pax[2], g(-5.0, 0.17), -9, -2.7, RED_))
        blue_post = VGroup(dens(pax[0], g(1.290, 0.0065), 1.26, 1.33, BLUE_),
                           dens(pax[1], half(0.95), -9, -2.7, BLUE_),
                           dens(pax[2], half(1.05), -9, -2.7, BLUE_))
        cr = cov_bar(0.52, 5.4, RED_, r"PRISM, 0.5--5.5\,$\mu$m", 0.0)
        cb = cov_bar(3.0, 5.5, BLUE_, r"G395H, 3.0--5.5\,$\mu$m", 0.3)
        self.wait_until(3.6)
        self.play(GrowFromEdge(cr[0], LEFT), FadeIn(cr[1]), pts_b.animate.set_opacity(0.15), fit_b.animate.set_stroke(opacity=0.2), run_time=1.0)
        self.wait(1.6)
        self.play(LaggedStart(*[GrowFromEdge(p, DOWN) for p in red_post], lag_ratio=0.2), run_time=1.3)
        self.wait(max(self.remaining() - 3.3, 0.1))
        self.play(GrowFromEdge(cb[0], LEFT), FadeIn(cb[1]), pts_b.animate.set_opacity(0.55), fit_b.animate.set_stroke(opacity=1),
                  run_time=0.9)
        self.play(LaggedStart(*[GrowFromEdge(p, DOWN) for p in blue_post], lag_ratio=0.2), run_time=1.3)

        # ---------------- why: coverage, and the radius agrees
        self.narrate("s7b")
        hl = Rectangle(width=ax.c2p(3.0, 0)[0] - ax.c2p(0.5, 0)[0], height=3.0, stroke_width=0).set_fill(RED_, 0.10)
        hl.move_to([(ax.c2p(3.0, 0)[0] + ax.c2p(0.5, 0)[0]) / 2, ax.get_center()[1], 0])
        hl_lab = T(r"extra H$_2$O bands only PRISM sees", 22, RED_).move_to(hl.get_top() + DOWN * 0.25)
        self.wait(1.1)
        self.play(FadeIn(hl), FadeIn(hl_lab), run_time=0.9)
        self.wait_until(4.6)
        rp_group = VGroup(panels[0], red_post[0], blue_post[0])
        others = VGroup(panels[1], panels[2], red_post[1:], blue_post[1:])
        self.play(FadeOut(others), rp_group.animate.scale(1.3).move_to([-2.2, -2.15, 0]), run_time=1.0)
        a = pax[0]
        lb = T("1.29", 30, BLUE_).next_to(a.c2p(1.290, 1.0), UL, buff=0.05).shift(LEFT * 0.25)
        lr = T("1.30", 30, RED_).next_to(a.c2p(1.300, 1.0), UR, buff=0.05).shift(RIGHT * 0.1)
        rj = VGroup(T(r"planet radius, in Jupiter radii:", 26, INK),
                    T(r"both retrievals agree", 30, YELLOW_)).arrange(DOWN, aligned_edge=LEFT, buff=0.15)
        rj.next_to(a, RIGHT, buff=0.8)
        self.play(FadeIn(lb, shift=UP * 0.1), FadeIn(lr, shift=UP * 0.1), run_time=0.7)
        self.play(FadeIn(rj, shift=LEFT * 0.1), run_time=0.7)
        self.finish_beat()
        fade_all(self, 0.6)


# ============================================================================ 8. outro
class S8Outro(Narrated):
    def construct(self):
        self.narrate("s8a")
        goal = T(r"goal: not to beat past analyses of WASP-39b", 30, DIM).to_edge(UP, buff=0.5)
        self.play(FadeIn(goal), run_time=0.8)
        self.wait(1.0)
        figs = [("fig2_orchestral_ui.png", "agent UI"), ("fig6_jwst_binned.png", "rebinned model"),
                ("fig9_retrievals.png", "two retrievals"), ("fig10_corner.png", "corner plot")]
        cards = Group()
        for fn, cap in figs:
            im = ImageMobject(str(ASSETS / fn)).set_height(2.25)
            if im.width > 3.2:
                im.set_width(3.2)
            frame = SurroundingRectangle(im, buff=0.0, stroke_color=INK, stroke_width=1.5)
            c = T(cap, 20, DIM).next_to(im, DOWN, buff=0.12)
            cards.add(Group(im, frame, c))
        cards.arrange(RIGHT, buff=0.3).move_to(UP * 0.55)
        rots = [0.05, -0.03, 0.03, -0.05]
        cap_all = T("figures generated by ASTER, as shown in the paper", 24, INK).next_to(cards, DOWN, buff=0.35)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 1.5) for c in cards], lag_ratio=0.2),
                  FadeIn(cap_all), run_time=2.2)
        self.wait(max(self.remaining() - 2.8, 0.1))
        flower = ImageMobject(str(ASSETS / "aster_flower.png")).set_height(0.9)
        ag = Group(flower, T("agent: execution", 28, GREEN_)).arrange(RIGHT, buff=0.25)
        hu = VGroup(person(INK, 0.8), T("researcher: judgment", 28, YELLOW_)).arrange(RIGHT, buff=0.25)
        roles = Group(ag, hu).arrange(RIGHT, buff=1.4).to_edge(DOWN, buff=0.55)
        self.play(FadeOut(cap_all), FadeIn(ag, shift=UP * 0.2), run_time=0.8)
        self.play(FadeIn(hu, shift=UP * 0.2), run_time=0.8)

        # ---------------- final card
        self.narrate("s8b")
        self.play(FadeOut(Group(goal, cards, roles)), run_time=0.6)
        stars = starfield(seed=21).set_opacity(0.6)
        flower2 = ImageMobject(str(ASSETS / "aster_flower.png")).set_height(2.2).move_to([-3.0, 1.3, 0])
        name = Text("ASTER", font="Georgia", weight=BOLD, font_size=120, color=INK).next_to(flower2, RIGHT, buff=0.35)
        modules = ["TauREx", "NASA Archive", "retrievals", "+ your tool"]
        mchips = VGroup(*[chip(m, GOLD_ if m != "+ your tool" else TEAL_, 16, mono_font=False, pad=0.12) for m in modules])
        mchips.arrange(RIGHT, buff=0.25).next_to(Group(flower2, name), DOWN, buff=0.45)
        self.play(FadeIn(stars), FadeIn(flower2, scale=0.6), FadeIn(name, shift=LEFT * 0.3), run_time=1.0)
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.3) for c in mchips], lag_ratio=0.15), run_time=1.0)
        tag1 = T("The busywork goes to the agent.", 30, GREEN_)
        tag2 = T("The thinking stays with us.", 30, YELLOW_)
        tags = VGroup(tag1, tag2).arrange(RIGHT, buff=0.35).next_to(mchips, DOWN, buff=0.45)
        self.play(FadeIn(tag1), run_time=0.6)
        self.wait(0.6)
        self.play(FadeIn(tag2), run_time=0.6)
        self.finish_beat()
        cite = VGroup(
            T("Panek, Roman, Shukla, Pagliaro, Matcheva \\& Matchev (2026)", 24, INK),
            T(r"\textit{ASTER -- Agentic Science Toolkit for Exoplanet Research}", 22, DIM),
            mono("arXiv:2603.26953  ·  github.com/emipanek/aster", 18, BLUE_),
        ).arrange(DOWN, buff=0.14).to_edge(DOWN, buff=0.45)
        self.play(FadeIn(cite, shift=UP * 0.15), run_time=0.9)
        self.wait(3.2)
        fade_all(self, 1.2)
