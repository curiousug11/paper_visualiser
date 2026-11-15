#!/bin/bash
# usage: tools/contact_sheet.sh <Scene> [quality=480p15] [every_s=3]  -> out/sheet_<Scene>.png
# A 3-column grid of frames sampled every N seconds. LOOK at it: overlaps, off-screen items,
# curves leaving their axes and labels sitting on data are only visible this way.
cd "$(dirname "$0")/.."
s=$1; Q=${2:-480p15}; E=${3:-3}; f=media_$s/videos/video/$Q/$s.mp4
D=$(ffprobe -v error -show_entries format=duration -of csv=p=0 "$f"); R=$(python3 -c "import math;print(math.ceil($D/$E/3))")
mkdir -p out; ffmpeg -loglevel error -y -i "$f" -vf "fps=1/$E,scale=640:-1,tile=3x$R" -frames:v 1 out/sheet_$s.png
echo out/sheet_$s.png
