---
name: paper-video
description: Make a 3Blue1Brown-style explainer video (Manim visuals + Kokoro TTS narration, synced, 1080p60) from a research paper, PDF, or technical topic. Use when the user asks for an explainer/animated/3b1b-style video, a video summary of a paper, or a Manim + narration video.
---

# Paper → 3b1b-style explainer video

You produce a finished MP4 where every animation lands on the sentence that describes it.
The quality comes from four things, in this order: **a story with one visual idea per step,
narration written before any animation, beat-level audio sync, and actually looking at
rendered frames before the final render.** Do not skip any of them.

Bundled files (paths relative to this skill's folder):
- `scripts/setup.sh` – one-time env (Python 3.12 venv with Manim + Kokoro, LaTeX, ffmpeg). Idempotent.
- `scripts/new_project.sh <dir>` – copies `template/` into a new project.
- `template/` – `common.py` (style + `Narrated` base class), `narration.py`, `tts.py`, `video.py`,
  `scenes.txt`, `render.sh`, `assemble.sh`, `tools/{contact_sheet.sh,frame.sh,music.py}`.
- `examples/giant_planets_*.py` – a complete, polished 4-minute video (6 scenes). **Read
  `examples/giant_planets_video.py` before writing scenes**; copy its patterns.
- `reference/visual_playbook.md` – 3b1b moves and the layout bugs that recur. Read before Step 4.
- `reference/narration_guide.md` – writing for TTS. Read before Step 2.

## Step 0 — Setup (start it first, in the background)
Run `scripts/setup.sh` in the background right away (it takes minutes); read the paper meanwhile.
Venv defaults to `~/.venvs/papervideo`; override with `PV_VENV`. Then `scripts/new_project.sh <dir>`.
Do not use system Python 3.13 for Kokoro: its spaCy/blis deps fail to build there.

## Step 1 — Understand, then outline (no code yet)
- Read the **whole** paper (PDFs: in page chunks). Collect the real numbers you'll show.
- Pick the 3–5 ideas a smart non-specialist must leave with. Typical arc:
  **hook (concrete image + question) → title → idea 1 → idea 2 → … → real-data payoff →
  surprising result → recap/outro.** One scene per idea; 4–7 scenes total.
- For each idea decide its **one signature visual** — a transformation that *is* the idea
  (bars "pouring" into an average, a slider sweeping a parameter, a bar hitting a ceiling,
  pebbles shedding ice at a line). If you can't name the visual, the idea isn't ready.
- Assign each recurring concept **one colour** for the whole video (in `common.py`).

## Step 2 — Write the narration (`narration.py`)
- Dict of scenes → list of **beats**; a beat = one sentence-ish idea = one visual change, 4–14 s.
- **Word budget: ~150 words/min.** 3–4 min ⇒ 480–580 words. Count before generating;
  first drafts always run long — cut adjectives and asides, not ideas.
- Write for the ear (see `reference/narration_guide.md`): spell out acronyms/numbers that TTS
  mangles, one number per sentence, no parentheses or symbols.
- Run `"$PV_VENV/bin/python" tts.py [voice] [speed]` (defaults `af_heart`, 1.08). It prints each
  scene's length and per-beat durations and writes `audio/<key>.wav` + `audio/<key>.json`.
  If total is off target, **edit the text and regenerate** — don't speed past ~1.1.

## Step 3 — Sync model (how scenes use the audio)
Every scene subclasses `Narrated` (in `common.py`) with `KEY = "<narration key>"`:
```python
self.beat(k)     # wait until beat k's audio starts, then animate what that sentence says
...              # keep total run_time of a beat's animations < that beat's duration
self.finish()    # wait for narration end, fade everything out
```
`beat()` prints `[SYNC] <key> beat k late by Xs` when the previous beat's animations overran.
Fix every SYNC warning by shortening `run_time`s or splitting/merging beats. Plan run_times from
the per-beat durations tts.py printed. Use `self.wait()` inside a beat to land a reveal on a
specific phrase (e.g. wait 2 s, then show the "?").

## Step 4 — Build scenes (`video.py`, list them in `scenes.txt`)
- Read `reference/visual_playbook.md` and the example video first.
- Use `T()` for text and `M()` for math (LaTeX, CMU serif = the 3b1b look), `self.header(n, title)`
  for numbered section headers, `starfield()`, `glow_star()`, `split_bar()` as needed.
- Show the paper's real equations and numbers; label anything illustrative as such.
- Every scene starts from an empty frame and ends with `self.finish()` (clean concatenation).

## Step 5 — Draft render and LOOK (mandatory, iterate until clean)
```bash
./render.sh -ql                  # all scenes in parallel, 480p15, prints SYNC/Error/EXIT per scene
tools/contact_sheet.sh S1Foo     # grid of frames every 3 s -> out/sheet_S1Foo.png
tools/frame.sh S1Foo 27          # one frame at t=27 s
```
Open every contact sheet with the image viewer/Read tool and check, scene by scene:
overlapping text, labels sitting on data, things off-frame, curves leaving their axes, text too
small (< ~22 at 1080p is hard to read), empty halves of the frame, a beat with nothing moving
for > 4 s, colours that break the concept mapping. Fix, re-render only the changed scenes
(`./render.sh -ql S2Bar S4Baz`), re-check. Expect 2–3 passes.

## Step 6 — Final render and assembly
```bash
./render.sh -qh        # 1080p60; ~10–20 min for 4 min of video on 4 cores (run in background)
./assemble.sh 1080p60  # -> out/final.mp4 (quiet procedural music bed, -16 LUFS) + out/voice_only.mp4
```
`MUSIC_VOL=0` (or use voice_only.mp4) if the user doesn't want music. Spot-check 4–6 frames of
the final file, confirm duration and resolution with ffprobe, then deliver.

## Delivering
Give the user the final MP4 (and voice-only version), the runtime, and an honest list of:
simplifications/illustrative visuals, any numbers you rounded or recomputed differently from
the paper, and that you could not listen to the audio (pronunciation unverified by ear).
Tell them how to edit: change `narration.py` → `tts.py` → `render.sh -qh` → `assemble.sh`;
animations re-sync automatically.

## Known environment pitfalls (already handled by the scripts — don't undo)
- Parallel renders sharing one media dir race on the LaTeX cache ("does not support converting
  .dvi files to SVG"): `render.sh` gives each scene its own `media_<Scene>` dir.
- `\checkmark`/`\times` look wrong as marks; use `T(r"\ding{51}")` / `T(r"\ding{55}")` (pifont is loaded).
- `M()` accepts several tex strings (for `TransformMatchingTex` / colouring parts) plus a trailing
  size int and colour string: `M(r"a", "=", r"b", 48, GOLD_)`.
- Kokoro downloads weights + the spaCy English model on first use (needs network once).
