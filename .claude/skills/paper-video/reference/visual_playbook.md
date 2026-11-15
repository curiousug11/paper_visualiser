# Visual playbook

## Look
- Near-black background (`BG = #0C0F16`), off-white ink, a small fixed palette (blue, teal, green,
  gold, orange, red, purple, grey). Gold = the key quantity. Red = "breaks / excess / impossible".
- **Colour is meaning.** Each recurring concept gets one colour in every scene (in the example:
  solids = orange, gas = blue, excess = red, metals = gold). Equation terms are coloured to match
  the bars/regions they produce.
- LaTeX for all text (`T`, `M`): consistent CMU serif. Sizes at 1080p: titles 44–56, equations
  40–60, labels 24–30, captions ≥ 22. Nothing smaller.
- Numbered section headers (`self.header("2", "Solids vs. gas")`) orient the viewer.
- Polish details that cost little: starfield behind astro scenes, glow on stars, shaded planets,
  small `shift=` on every FadeIn, `LaggedStart` for groups, `rate_func=smooth` for big moves.

## The 3b1b moves (use at least one per scene)
| Move | How | Example use |
|---|---|---|
| Transform one representation into another | `Transform`, `ReplacementTransform`, `TransformFromCopy` | stacked bar → histogram (width = share, height = value) |
| Reveal an average as "levelling" | `TransformFromCopy(bars, single_rect)` with equal area | weighted mean x̄ |
| Parameter sweep | `ValueTracker` + `always_redraw` for the dependent shapes and readouts | slide a probe across a disk; grow a bar with x_R |
| Equation grows a term | `TransformMatchingTex(eq, eq_with_new_term)` with matching substrings | add `+ g_excess` |
| Braces that name parts | `Brace(eq[k], DOWN)` + coloured label | "from solids" / "from gas" |
| Zoom | build a second `Axes` with a narrower range and `ReplacementTransform` axes, curve, ticks | full 1–1000× curve → zoom to 1–30× |
| A ceiling / threshold | dashed line + something visibly exceeding it in red | static-disk limit |
| Counting up | `DecimalNumber` + `ChangeDecimalToValue` | 128/0.17 → 750 |
| Continuous process | `ValueTracker` clock with `add_updater(lambda m, dt: m.increment_value(dt))` + `always_redraw` of a whole particle system computed from time | pebbles crossing a snowline, losing ice |
| Comparison payoff | two bars with a shared baseline | pebbles that drifted vs. metals in planets |
| Recap | flow chart of boxes lit one by one on the beats | recipe |

## Layout rules (each of these was a real bug)
1. **Readouts and annotations must not share space.** Live numbers (`x_R = 5.0`) go in a fixed
   empty corner, away from where labels like "ceiling" and "measured" will appear later.
2. **Clip curves to their axes.** When zooming, set the plot's `x_range` so y never exceeds the
   axes' `y_range`; otherwise the curve runs into the header.
3. **Labels never sit on data.** Put value labels inside a bar (contrasting colour) or clearly
   beside it with a buff ≥ 0.3; drop labels for zero-height bars.
4. **Arrange, don't hand-place, rows of related items** (`VGroup(...).arrange(RIGHT, buff=...)`):
   hand-placed question text overlapped the big "?".
5. Fade out objects you no longer need (old equations in corners) before adding new text nearby.
6. Use the whole frame. If the top half holds everything, move it to centre or enlarge.
7. Anything coming from an updater (`always_redraw`) must `clear_updaters()` before you fade it or
   move on, and trackers driven by a clock must stop (`clock.clear_updaters()`).
8. Use `pifont` marks (`\ding{51}` ✓, `\ding{55}` ✗); a math `\times` next to "f>1" reads as "times".
9. A label that follows a moving number (`DecimalNumber`) needs an updater, or the number grows into it.

## Timing
- Something should change at least every ~4 s. Use `self.wait(x)` to land reveals on the phrase.
- Typical run_times: FadeIn 0.5–0.8, Write equation 1.2–1.8, Create curve 1.3–2, big Transform
  1.5–2, sweeps 2–4.5. Sum per beat must be < the beat's duration (tts.py prints them).
- Start each scene with the header (0.6 s) on beat 0; end with `self.finish()`.

## Accuracy
- Use the paper's actual equations (simplified notation is fine) and real numbers with sources
  in a small grey caption ("HR 8799 b, relative to its host star").
- When you recompute something (e.g. with a different table), label it "≈" and mention it to the user.
- Stylised visuals (spectra, disk cartoons, step functions) are fine but must not show fake data
  as if measured.
