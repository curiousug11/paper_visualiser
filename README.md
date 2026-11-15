# paper_visualizer

Turn research papers into 3Blue1Brown-style explainer videos: Manim animations, Kokoro TTS
narration, every animation synced to the sentence that describes it, rendered at 1080p60.

## Example
[`videos/giant_planets_explainer.mp4`](videos/giant_planets_explainer.mp4) — a 4-minute explainer of
Chachan, Murray-Clay & Fortney, *Quantitative Links between Formation and Atmospheric Composition
for Giant Planets* ([arXiv:2608.23682](https://arxiv.org/abs/2608.23682)).
Source: [`examples/giant_planets/`](examples/giant_planets/).

## Repository layout
| Path | What it is |
|---|---|
| `.claude/skills/paper-video/` | Claude Code skill: the full workflow, style guide, narration guide and tested pipeline. Loads automatically when this repo is opened in Claude Code; ask "make a 3b1b-style video of this paper" or type `/paper-video`. |
| `PROMPT.md` | Copy-paste version of the workflow for use without the skill. |
| `examples/giant_planets/` | Complete source of the example video. |
| `videos/` | Rendered videos. |

## Make a video by hand
```bash
SKILL=.claude/skills/paper-video
$SKILL/scripts/setup.sh                    # one time: Python 3.12 venv with Manim + Kokoro, LaTeX, ffmpeg
$SKILL/scripts/new_project.sh my_video     # copy the template
cd my_video
# 1. write narration.py (scenes -> beats), then:
~/.venvs/papervideo/bin/python tts.py      # per-beat audio + timings; prints durations
# 2. write scenes in video.py (subclass Narrated, call self.beat(k)), list them in scenes.txt
./render.sh -ql                            # fast drafts, all scenes in parallel; prints [SYNC] overruns
tools/contact_sheet.sh S1Foo               # frame grid to check layout
./render.sh -qh && ./assemble.sh 1080p60   # final -> out/final.mp4 and out/voice_only.mp4
```

To re-render the example: run `tts.py` and the two render/assemble steps inside `examples/giant_planets/`.
