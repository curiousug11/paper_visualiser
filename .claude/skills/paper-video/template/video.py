"""Scenes for the video. One class per narration scene; KEY links it to narration.py.

Pattern for every scene:
    self.beat(k)      -> waits until beat k's sentence starts, then you animate what it says
    keep each beat's animations shorter than the beat (render prints [SYNC] ... late by Xs if not)
    self.finish()     -> waits for the narration to end, fades everything out
"""
from common import *


class S0Hook(Narrated):
    KEY = "s0_hook"

    def construct(self):
        stars = starfield()
        q = T(r"How do we know?", 60)

        self.beat(0)
        self.play(FadeIn(stars, run_time=1.5), Write(q, run_time=1.5))

        self.beat(1)
        title = T(r"Paper Title Goes Here\\on Two Lines", 46).move_to(UP * 0.8)
        auth = T(r"Author One \quad Author Two", 28, GREY_).next_to(title, DOWN, buff=0.4)
        self.play(FadeOut(q, shift=UP * 0.3), stars.animate.set_opacity(0.25), run_time=0.8)
        self.play(Write(title), run_time=1.6)
        self.play(FadeIn(auth, shift=UP * 0.1), run_time=0.6)
        self.finish()


class S1Idea(Narrated):
    KEY = "s1_idea"

    def construct(self):
        hdr = self.header("1", r"The first idea")

        self.beat(0)
        self.play(FadeIn(hdr, shift=RIGHT * 0.3), run_time=0.6)
        ax = Axes(x_range=[0, 4, 1], y_range=[0, 1, 0.25], x_length=7, y_length=3.8,
                  axis_config={"color": GREY_}, tips=False).shift(DOWN * 0.6 + RIGHT * 1.5)
        f = lambda x: x ** 2 / (1 + x ** 2)
        curve = ax.plot(f, x_range=[0, 4], color=HILITE_C, stroke_width=4)
        eq = M(r"y = \frac{x^2}{1+x^2}", 44).to_edge(LEFT, buff=0.7).shift(UP * 1.2)
        self.play(Write(eq), Create(ax), run_time=1.2)
        self.play(Create(curve), run_time=1.4)

        self.beat(1)
        t = ValueTracker(0.2)
        dot = always_redraw(lambda: Dot(ax.c2p(t.get_value(), f(t.get_value())), color=WHITE))
        lab = always_redraw(lambda: M(rf"{f(t.get_value()):.2f}", 30)
                            .next_to(ax.c2p(t.get_value(), f(t.get_value())), UL, buff=0.1))
        self.add(dot, lab)
        self.play(t.animate.set_value(3.5), run_time=2.5)
        self.finish()
