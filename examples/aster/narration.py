"""Narration script + TTS generation (Kokoro, voice af_heart).

Each beat becomes audio/<key>.wav; durations are written to audio/durations.json
so the Manim scenes can time their animations to the voiceover.

Usage:  python narration.py <path/to/kokoro-v1.0.onnx> <path/to/voices-v1.0.bin> [key ...]
"""
import json
import os
import sys
from pathlib import Path

# Text is written for the ear: numbers and acronyms are spelled the way they should be spoken.
BEATS = [
    # --- 1. Transit + transmission spectroscopy ---------------------------------
    ("s1a", "Every four days, a gas giant called WASP thirty-nine b passes in front of its star."),
    ("s1b", "As it does, a sliver of starlight filters through the planet's atmosphere, "
            "and the molecules there absorb some colors more than others."),
    ("s1c", "Where the gas absorbs strongly, the planet looks a little bigger, "
            "and blocks a little more light."),
    ("s1d", "Measure that dip, color by color, and you get a transmission spectrum. "
            "A chemical fingerprint."),
    # --- 2. The pipeline problem ---------------------------------------------------
    ("s2a", "But reading that fingerprint means chaining together archive queries, data downloads, "
            "radiative transfer models, and Bayesian retrievals."),
    ("s2b", "Each with its own software, its own formats, and its own learning curve."),
    # --- 3. The agent ----------------------------------------------------------------
    ("s3a", "Aster, the Agentic Science Toolkit for Exoplanet Research, "
            "hands that whole chain to an A.I. agent."),
    ("s3b", "An agent has three parts. A language model. A context that records everything. "
            "And a set of tools."),
    ("s3c", "Ask for the planet's parameters, and the model doesn't guess. It writes a tool call. "
            "The tool runs, its output joins the context, and the loop repeats until the job is done."),
    ("s3d", "The model never runs code directly. Every call passes through safety hooks, "
            "and anything uncertain goes to the human."),
    # --- 4. Tools vs skills ------------------------------------------------------------
    ("s4a", "One lesson. When the model stumbled setting up the Tau Rex modeling code, "
            "even inventing a function that doesn't exist, a dedicated tool fixed it."),
    ("s4b", "But for open-ended work, like plotting, a plain-language skill file worked better."),
    # --- 5. Case study ------------------------------------------------------------------
    ("s5a", "So the team pointed Aster at WASP thirty-nine b. It pulled the planet's parameters "
            "from the NASA Exoplanet Archive, and built a forward model."),
    ("s5b", "Asked to match J W S T and Ariel resolution, it chose sensible settings for each instrument, "
            "without being told their specs."),
    ("s5c", "Then it downloaded nine public J W S T datasets, and ran retrievals on two of them."),
    # --- 6. Bayesian retrieval / nested sampling ---------------------------------------------
    ("s6a", "A retrieval asks: which atmospheres could explain this data? "
            "Bayes' theorem frames the answer as a posterior."),
    ("s6b", "To map it, Aster uses nested sampling. Scatter live points. Repeatedly discard the worst. "
            "And the cloud contracts onto the most likely atmospheres."),
    # --- 7. Results ------------------------------------------------------------------------------
    ("s7a", "Here are the two retrievals, run autonomously. The red one used prism data, "
            "spanning half a micron to five and a half, and its posteriors are sharp. "
            "The blue one, from three microns up, is broad and degenerate."),
    ("s7b", "Exactly as expected. Wider coverage, more features. And the planet's radius agrees in both: "
            "one point two nine, versus one point three zero, Jupiter radii."),
    # --- 8. Conclusion ------------------------------------------------------------------------------
    ("s8a", "The goal isn't to beat past analyses. It's that one agent ran the whole pipeline, end to end, "
            "while the scientific judgment stayed with the researcher."),
    ("s8b", "Aster is open, and modular. The busywork goes to the agent. The thinking stays with us."),
]

VOICE = "af_heart"
SPEED = 0.98


def main():
    import soundfile as sf
    from kokoro_onnx import Kokoro

    model, voices, *only = sys.argv[1:]
    out = Path(__file__).parent / "audio"
    out.mkdir(exist_ok=True)
    dur_path = out / "durations.json"
    durations = json.loads(dur_path.read_text()) if dur_path.exists() else {}

    from kokoro_onnx import EspeakConfig
    # espeak-ng silently ignores data paths longer than ~160 chars, so allow a short override
    espeak_data = os.environ.get("ESPEAK_NG_DATA")
    kokoro = Kokoro(model, voices, espeak_config=EspeakConfig(data_path=espeak_data) if espeak_data else None)
    for key, text in BEATS:
        if only and key not in only:
            continue
        samples, sr = kokoro.create(text, voice=VOICE, speed=SPEED, lang="en-us")
        sf.write(out / f"{key}.wav", samples, sr)
        durations[key] = round(len(samples) / sr, 3)
        print(f"{key}: {durations[key]:.2f}s")

    dur_path.write_text(json.dumps(durations, indent=2))
    print(f"total: {sum(durations.values()):.1f}s")


if __name__ == "__main__":
    main()
