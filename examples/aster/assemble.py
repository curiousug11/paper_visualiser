"""Concatenate rendered scenes, add the music bed (ducked under the voice), normalize loudness.

Usage: python assemble.py <quality_dir e.g. media/videos/scenes/1080p60> <out.mp4>
"""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).parent
SCENES = ["S1Transit", "S2Pipeline", "S3Agent", "S4ToolsSkills", "S5CaseStudy", "S6Retrieval", "S7Results", "S8Outro"]
FFMPEG = str(Path(sys.executable).parent / "ffmpeg")
FFPROBE = str(Path(sys.executable).parent / "ffprobe")


def duration(path, stream="v:0"):
    out = subprocess.run([FFPROBE, "-v", "error", "-select_streams", stream, "-show_entries", "stream=duration",
                          "-of", "json", str(path)], capture_output=True, text=True, check=True).stdout
    return float(json.loads(out)["streams"][0]["duration"])


def main():
    qdir, out = Path(sys.argv[1]), Path(sys.argv[2])
    files = [qdir / f"{s}.mp4" for s in SCENES]
    durs = [duration(f) for f in files]
    total = sum(durs)
    print("scene durations:", [round(d, 2) for d in durs], "total", round(total, 2))

    music = ROOT / "audio" / "music.wav"
    subprocess.run([sys.executable, str(ROOT / "music.py"), f"{total:.3f}", str(music)], check=True)

    args = [FFMPEG, "-y", "-v", "error", "-stats"]
    for f in files:
        args += ["-i", str(f)]
    args += ["-i", str(music)]
    parts = []
    for i, d in enumerate(durs):
        # pad/trim each narration track to its video so the concat never drifts
        parts.append(f"[{i}:a]aresample=48000,aformat=channel_layouts=stereo,apad,atrim=0:{d:.4f},asetpts=N/SR/TB[a{i}]")
    concat_in = "".join(f"[{i}:v][a{i}]" for i in range(len(files)))
    m = len(files)
    graph = ";".join(parts) + ";" + (
        f"{concat_in}concat=n={len(files)}:v=1:a=1[v][voice];"
        f"[voice]asplit=2[vx][vk];"
        f"[{m}:a]aresample=48000,volume=0.30[mus];"
        f"[mus][vk]sidechaincompress=threshold=0.02:ratio=5:attack=40:release=700[duck];"
        f"[vx][duck]amix=inputs=2:duration=first:normalize=0,"
        f"loudnorm=I=-16:TP=-1.5:LRA=11[a]"
    )
    args += ["-filter_complex", graph, "-map", "[v]", "-map", "[a]",
             "-c:v", "libx264", "-preset", "slow", "-crf", "17", "-pix_fmt", "yuv420p",
             "-c:a", "aac", "-b:a", "192k", "-ar", "48000", "-movflags", "+faststart", str(out)]
    subprocess.run(args, check=True)
    print("wrote", out, f"({duration(out):.1f}s)")


if __name__ == "__main__":
    main()
