"""Generate per-beat narration with Kokoro and write per-scene wav + timing json."""
import json, sys
from pathlib import Path
import numpy as np, soundfile as sf
from kokoro import KPipeline

sys.path.insert(0, str(Path(__file__).parent))
from narration import SCENES

SR = 24000
LEAD, GAP, TAIL = 0.5, 0.4, 0.9   # seconds: before first beat, between beats, after last
VOICE = sys.argv[1] if len(sys.argv) > 1 else "af_heart"   # best-graded Kokoro voice
SPEED = float(sys.argv[2]) if len(sys.argv) > 2 else 1.08
out = Path(__file__).parent / "audio"
out.mkdir(exist_ok=True)
pipe = KPipeline(lang_code="a")

total = 0
for key, beats in SCENES.items():
    pieces, starts = [np.zeros(int(LEAD * SR))], []
    t = LEAD
    for text in beats:
        clip = np.concatenate([a.numpy() if hasattr(a, "numpy") else a
                               for _, _, a in pipe(text, voice=VOICE, speed=SPEED, split_pattern=None)])
        starts.append(round(t, 3))
        pieces += [clip, np.zeros(int(GAP * SR))]
        t += len(clip) / SR + GAP
    pieces.append(np.zeros(int(TAIL * SR)))
    audio = np.concatenate(pieces).astype(np.float32)
    sf.write(out / f"{key}.wav", audio, SR)
    dur = len(audio) / SR
    ends = [s for s in starts[1:]] + [dur - TAIL]
    json.dump({"starts": starts, "duration": round(dur, 3)}, open(out / f"{key}.json", "w"))
    total += dur
    print(f"{key}: {dur:6.1f}s  beats={[round(b - a, 1) for a, b in zip(starts, ends)]}")
print(f"TOTAL {total:.1f}s = {total/60:.2f} min")
