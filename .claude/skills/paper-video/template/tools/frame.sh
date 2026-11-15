#!/bin/bash
# usage: tools/frame.sh <Scene> <seconds> [quality=480p15]  -> out/<Scene>_<t>.png (one full-size frame)
cd "$(dirname "$0")/.."
mkdir -p out; ffmpeg -loglevel error -y -ss "$2" -i "media_$1/videos/video/${3:-480p15}/$1.mp4" -frames:v 1 "out/$1_$2.png"
echo "out/$1_$2.png"
