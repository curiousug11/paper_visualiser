# ASTER explainer video

3Blue1Brown-style explainer (≈3 min, 1080p60) for arXiv:2603.26953. The output is `../ASTER_explainer.mp4`.

| file | role |
|---|---|
| `narration.py` | narration script (21 beats) and Kokoro TTS → `audio/*.wav` + `durations.json` |
| `scenes.py` | 8 Manim scenes, each timed to its voiceover beats |
| `common.py` | palette, narration-driven `Narrated` scene, LaTeX helper (pdflatex + PyMuPDF, no dvisvgm needed) |
| `spectrum.py` | schematic WASP-39b spectrum (hand-tuned to the shape of paper Fig. 9, not real data) |
| `music.py` | procedurally generated ambient music bed |
| `assemble.py` | concatenates the scenes, ducks the music under the voice, normalizes to −16 LUFS |

Rebuild (needs Manim CE 0.22, pdflatex, PyMuPDF, soundfile, scipy, ffmpeg; Kokoro + model files only to regenerate the voice):

```bash
python narration.py kokoro-v1.0.onnx voices-v1.0.bin   # optional: ESPEAK_NG_DATA=<short path> if espeak can't find its data
for s in S1Transit S2Pipeline S3Agent S4ToolsSkills S5CaseStudy S6Retrieval S7Results S8Outro; do manim -qh scenes.py $s & done; wait
python assemble.py media/videos/scenes/1080p60 ../ASTER_explainer.mp4
```
