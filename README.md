# paper_visualiser

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Turn a research paper into a **3Blue1Brown-style explainer video**: Manim animations, Kokoro
text-to-speech narration, every animation timed to the sentence that describes it, 1080p60 output.

It is a free, open-source [Claude Code](https://code.claude.com/docs) **skill** (MIT licence). Give Claude a PDF and ask for a
video. It reads the paper, writes the script, generates the narration, builds the animations,
checks the rendered frames for layout problems and delivers a finished MP4.

**Example videos** (1080p60):
- [`videos/giant_planets_explainer.mp4`](videos/giant_planets_explainer.mp4) (4 min) explains
  Chachan, Murray-Clay & Fortney, *Quantitative Links between Formation and Atmospheric
  Composition for Giant Planets* ([arXiv:2608.23682](https://arxiv.org/abs/2608.23682)). Its full
  source is in [`examples/giant_planets/`](examples/giant_planets/).
- [`videos/ASTER_explainer.mp4`](videos/ASTER_explainer.mp4) (3 min) explains Panek, Roman,
  Shukla, Pagliaro, Matcheva & Matchev, *ASTER: Agentic Science Toolkit for Exoplanet Research*
  ([arXiv:2603.26953](https://arxiv.org/abs/2603.26953)).

---

## Contents
- [What you get](#what-you-get)
- [Installation](#installation)
- [Usage with Claude Code](#usage-with-claude-code)
- [Usage without Claude Code](#usage-without-claude-code)
- [Making a video by hand](#making-a-video-by-hand)
- [How it works](#how-it-works)
- [Requirements](#requirements)
- [Customisation](#customisation)
- [Troubleshooting](#troubleshooting)
- [Repository layout](#repository-layout)
- [Credits](#credits)
- [License](#license)

## What you get
- A **story-first workflow**: hook → one scene per key idea → real results → recap, with one
  signature animation per idea.
- **Narration written before animation**, split into beats, with a word budget so the video lands
  at the length you ask for.
- **Beat-level sync**: each scene waits for its sentence before animating, and the renderer warns
  when an animation runs past its sentence.
- **3b1b look**: dark background, consistent colour-per-concept, LaTeX typography, numbered
  section headers, transforms, parameter sweeps, zooms and counters.
- **A visual QA loop**: draft renders are turned into contact sheets that Claude inspects for
  overlaps and off-screen elements before the final render.
- **Finished audio**: a quiet procedural music bed and loudness normalisation (−16 LUFS). A
  voice-only version is produced as well.

## Installation

### 1. Get the skill
Choose one option:

**A. For all your projects (personal skill)**
```bash
git clone https://github.com/curiousug11/paper_visualiser.git
mkdir -p ~/.claude/skills
cp -r paper_visualiser/.claude/skills/paper-video ~/.claude/skills/
```

**B. For one project only**: copy the folder into that project and commit it:
```bash
mkdir -p your-project/.claude/skills
cp -r paper_visualiser/.claude/skills/paper-video your-project/.claude/skills/
```

**C. Claude Code on the web / cloud sessions**: open this repository (or any repository that
contains `.claude/skills/paper-video/`) in a session. The skill loads automatically.

To check that it's installed, start `claude` and type `/paper-video`. It should appear in the
command list.

### 2. Install the dependencies (optional — Claude can do this)
Claude runs this step itself the first time you ask for a video, so you can skip it. See
[Requirements](#requirements) for the few things it can't install for you. To do it yourself,
run the setup script once. It is safe to re-run:
```bash
bash ~/.claude/skills/paper-video/scripts/setup.sh
# option B: bash .claude/skills/paper-video/scripts/setup.sh
```
It:
- installs any missing system packages with `apt-get` on Debian/Ubuntu (using `sudo` if you
  aren't root), or with Homebrew on macOS;
- creates a Python 3.12 virtual environment at `~/.venvs/papervideo` containing Manim, Kokoro
  and CPU-only PyTorch;
- downloads the voice model and runs a quick check.

To put the environment somewhere else, set `PV_VENV=/path/to/venv` before running setup and
whenever you render.

**macOS:** setup installs `ffmpeg`, `pango` and `espeak-ng` with Homebrew, but LaTeX is separate.
Install [MacTeX](https://www.tug.org/mactex/), or BasicTeX plus the packages listed in
[Manim's installation docs](https://docs.manim.community/en/stable/installation.html). Make sure
Python 3.12 is available (`brew install uv` is easiest).

### 3. Smoke test (optional, about 1 minute)
```bash
~/.claude/skills/paper-video/scripts/new_project.sh /tmp/pv_test && cd /tmp/pv_test
~/.venvs/papervideo/bin/python tts.py      # narration for the 2-scene template
./render.sh -ql                            # both scenes print "EXIT 0"
./assemble.sh 480p15                       # writes out/final.mp4
```

## Usage with Claude Code
Start Claude Code in a working folder, attach or point to the paper, and ask:

```
Make a 3b1b-style video for paper.pdf, around 3-4 minutes. Go all out.
```

More examples:
```
/paper-video explain arxiv 2608.23682 for first-year grad students, ~3 min, no music
Make a 2-minute explainer of section 3 of this PDF, voice bf_emma
Turn my thesis chapter (chapter3.pdf) into a 5-minute video with a recap at the end
```

Claude will:
1. read the whole paper and choose 3–5 key ideas, each with one signature visual;
2. write and time the narration (`narration.py`), then generate the audio;
3. write the Manim scenes (`video.py`) synced to the narration;
4. render drafts, inspect contact sheets, and fix layout and sync problems;
5. render at 1080p60, assemble, and deliver `out/final.mp4` and `out/voice_only.mp4`, together
   with a list of the simplifications it made.

Useful things to say:
- **Length:** "about 3 minutes" (sets the word budget).
- **Audience:** "for high-school students" or "for experts in the field".
- **Voice/speed:** "use voice am_michael", "a bit slower".
- **Music:** "no background music".
- **Changes after the first cut:** "make scene 2 slower", "the label in scene 3 overlaps the
  curve", "replace the hook with ...". Claude edits and re-renders only what changed.

A first video typically takes 30–60 minutes end to end. Most of that is rendering.

## Usage without Claude Code
[`PROMPT.md`](PROMPT.md) is a self-contained version of the workflow. Paste it, with the paper,
into any coding assistant that can run code. It doesn't use the bundled scripts, so expect more
setup work.

## Making a video by hand
The pipeline also works without an AI assistant:
```bash
SKILL=~/.claude/skills/paper-video
$SKILL/scripts/new_project.sh my_video && cd my_video

# 1. Write narration.py: a dict of scenes, each a list of beats (one sentence-ish idea per beat).
~/.venvs/papervideo/bin/python tts.py [voice] [speed]   # writes audio/, prints per-beat durations

# 2. Write scenes in video.py: subclass Narrated, set KEY, call self.beat(k) before each beat's
#    animations, end with self.finish(). List the scene classes in scenes.txt in playback order.

./render.sh -ql                  # fast drafts, all scenes in parallel; prints [SYNC] overruns
tools/contact_sheet.sh S1Foo     # grid of frames every 3 s -> out/sheet_S1Foo.png
tools/frame.sh S1Foo 27          # a single frame at t = 27 s

./render.sh -qh                  # final 1080p60 render
./assemble.sh 1080p60            # -> out/final.mp4 and out/voice_only.mp4
```
Before writing scenes, read `SKILL.md`, `reference/visual_playbook.md` and
`examples/giant_planets/video.py`.

To re-render the included example:
```bash
cd examples/giant_planets
~/.venvs/papervideo/bin/python tts.py
./render.sh -qh && ./assemble.sh 1080p60
```

## How it works
```
narration.py ──tts.py──▶ audio/<scene>.wav   +   audio/<scene>.json  {"starts": [0.5, 6.8, ...], "duration": 29.8}
                                                        │
video.py:  class S1Foo(Narrated):  KEY = "s1_foo"       ▼
             self.beat(0)  → waits until 0.5 s, then animates sentence 0
             self.beat(1)  → waits until 6.8 s, then animates sentence 1   ([SYNC] warning if late)
             self.finish() → waits for the audio to end, fades out
                                                        │
render.sh ── each scene in parallel, own media dir ─────▶ media_<Scene>/.../<Scene>.mp4
assemble.sh ── concat in scenes.txt order + music bed + loudnorm ──▶ out/final.mp4
```
Change the narration, rerun `tts.py`, re-render, and the animations re-sync automatically.

## Requirements
**You don't need to install most of this yourself.** The first time you ask for a video, Claude
runs the bundled setup script and installs the Python environment, Manim, Kokoro, the voice model
and, on Debian/Ubuntu, the system packages. You only need to provide:
- **Claude Code** itself ([install guide](https://code.claude.com/docs));
- **your password for `sudo`**, if you aren't root and system packages are missing (Claude can't
  type it; run `setup.sh` yourself or install the packages it prints);
- on **macOS**: Homebrew and a LaTeX distribution (MacTeX), which need interactive installers;
- on **Windows**: WSL2 with Ubuntu, then everything else runs inside it.

The full list, for reference or for setting up without Claude:

| | |
|---|---|
| OS | Linux (Ubuntu/Debian tested) or macOS. On Windows, use WSL2 (Ubuntu). |
| Python | **3.12** (Kokoro's dependencies don't build on 3.13). [`uv`](https://docs.astral.sh/uv/) is recommended; setup uses it if present. |
| System packages | LaTeX (`texlive-latex-extra`, `texlive-science`, `cm-super`), `dvisvgm`, `ffmpeg`, Pango/Cairo dev libraries, `espeak-ng` |
| Hardware | Any modern CPU; no GPU needed. About 4 GB of disk for dependencies. |
| Network | Needed once, to download the Kokoro voice model and the spaCy English model. |
| Claude Code | Needed for the automated workflow; [install guide](https://code.claude.com/docs). Not needed for the manual pipeline. |

## Customisation
| What | Where |
|---|---|
| Voice | `tts.py <voice> <speed>`. Default `af_heart`, 1.08. Others: `af_bella`, `bf_emma`, `am_michael`, `bm_george`, … ([full list](https://huggingface.co/hexgrad/Kokoro-82M/blob/main/VOICES.md)) |
| Pauses | `LEAD, GAP, TAIL` at the top of `tts.py` |
| Colours, fonts, background | `common.py` (palette and semantic colour names) |
| Music volume | `MUSIC_VOL=0.04 ./assemble.sh 1080p60` (`0` for none), or use `out/voice_only.mp4` |
| 4K | `./render.sh -qk && ./assemble.sh 2160p60` |
| Draft quality | `./render.sh -qm` (720p30) and `./assemble.sh 720p30` |

## Troubleshooting
| Problem | Fix |
|---|---|
| `pip install kokoro` fails building `blis`/`spacy` | You're on Python 3.13. Use the 3.12 venv from `setup.sh`. |
| `Your installation does not support converting .dvi files to SVG` | Either `dvisvgm` or a LaTeX package is missing (rerun `setup.sh`), or several renders shared one media folder. Use `render.sh`, which gives each scene its own. |
| `LaTeX Error: File 'xyz.sty' not found` | Install the package (`apt-get install texlive-latex-extra texlive-science`, or `tlmgr install xyz`). |
| `[SYNC] s2_foo beat 3 late by 1.2s` | Animations before beat 3 run longer than their sentence. Shorten `run_time`s or split the beat. |
| A word is mispronounced | Respell it in `narration.py` ("H R eighty-seven ninety-nine", "C O") and rerun `tts.py`. |
| First `tts.py` run hangs | It's downloading the voice model and the spaCy model (needs network once). |
| Final render is slow | Normal: 1080p60 takes roughly 5–20 min for 4 minutes of video on 4 cores. Iterate at `-ql`. |
| `No module named manim` / `kokoro` | The scripts use the venv at `~/.venvs/papervideo`. Run `setup.sh`, or set `PV_VENV` to wherever your venv is. |

## Repository layout
```
.claude/skills/paper-video/
├── SKILL.md                     # the workflow Claude follows
├── reference/
│   ├── visual_playbook.md       # 3b1b techniques, layout rules, timing
│   └── narration_guide.md       # writing for TTS, word budgets, pronunciation
├── scripts/
│   ├── setup.sh                 # one-time environment setup
│   └── new_project.sh           # copy the template into a new project
├── template/                    # starting point for every video
│   ├── common.py                # style, helpers, Narrated base class
│   ├── narration.py  tts.py     # script and per-beat TTS with timings
│   ├── video.py  scenes.txt     # scenes and their playback order
│   ├── render.sh  assemble.sh   # parallel render and final assembly
│   └── tools/                   # contact_sheet.sh, frame.sh, music.py
└── examples/                    # the giant-planets video, for Claude to learn from
examples/giant_planets/          # same example as a ready-to-render project
videos/                          # rendered example videos
PROMPT.md                        # copy-paste version of the workflow
```

## Credits
- [Manim Community Edition](https://www.manim.community/) for animation.
- [Kokoro-82M](https://huggingface.co/hexgrad/Kokoro-82M) by hexgrad for text-to-speech.
- Visual style inspired by [3Blue1Brown](https://www.3blue1brown.com/).
- Example papers: Chachan, Murray-Clay & Fortney (2026), arXiv:2608.23682 (an independent
  explainer, not affiliated with the authors); Panek, Roman, Shukla, Pagliaro, Matcheva &
  Matchev (2026), arXiv:2603.26953.

## License
Released under the [MIT License](LICENSE): free to use, modify and redistribute, including
commercially, as long as the copyright notice is kept. Contributions are welcome via issues and
pull requests.

Third-party tools keep their own licences: Manim (MIT) and Kokoro-82M (Apache 2.0) are installed
by `setup.sh` and are not bundled in this repository.
