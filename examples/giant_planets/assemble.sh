#!/bin/bash
# usage: ./assemble.sh [480p15|1080p60|2160p60]   -> out/final.mp4 (music bed) + out/voice_only.mp4
set -e
cd "$(dirname "$0")"
PY=${PV_VENV:-$HOME/.venvs/papervideo}/bin/python
Q=${1:-1080p60}; MUSIC_VOL=${MUSIC_VOL:-0.07}
mkdir -p out; : > out/list.txt
for s in $(grep -v '^\s*#' scenes.txt | grep .); do
  f="$PWD/media_$s/videos/video/$Q/$s.mp4"; [ -f "$f" ] || { echo "missing $f"; exit 1; }
  echo "file '$f'" >> out/list.txt
done
ffmpeg -loglevel error -y -f concat -safe 0 -i out/list.txt -c:v copy -c:a aac -b:a 192k out/voice_only.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 out/voice_only.mp4)
"$PY" tools/music.py out/music.wav "$D"
ffmpeg -loglevel error -y -i out/voice_only.mp4 -i out/music.wav -filter_complex \
  "[1:a]volume=$MUSIC_VOL[m];[0:a]aresample=44100,pan=stereo|c0=c0|c1=c0[v];[v][m]amix=inputs=2:duration=first:normalize=0,loudnorm=I=-16:TP=-1.5:LRA=11,aresample=44100[a]" \
  -map 0:v -map "[a]" -c:v copy -c:a aac -b:a 192k -movflags +faststart out/final.mp4
ffprobe -v error -show_entries format=duration:stream=width,height,r_frame_rate -of compact out/final.mp4
