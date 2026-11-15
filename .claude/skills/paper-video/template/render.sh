#!/bin/bash
# usage: ./render.sh -ql|-qh [Scene ...]     (no scenes -> every line of scenes.txt)
# Each scene renders in parallel into its OWN media dir: a shared LaTeX cache races and fails
# with "Your installation does not support converting .dvi files to SVG".
cd "$(dirname "$0")"
PY=${PV_VENV:-$HOME/.venvs/papervideo}/bin/python
Q=${1:?quality flag, e.g. -ql or -qh}; shift
SCENES=("$@"); [ ${#SCENES[@]} -eq 0 ] && mapfile -t SCENES < <(grep -v '^\s*#' scenes.txt | grep .)
mkdir -p logs
for s in "${SCENES[@]}"; do
  ( "$PY" -m manim $Q --disable_caching -v WARNING --progress_bar none --media_dir media_$s video.py $s \
      > logs/$s.log 2>&1; echo "EXIT $?" >> logs/$s.log ) &
done
wait
for s in "${SCENES[@]}"; do echo "== $s"; grep -E "SYNC|Error|EXIT" logs/$s.log | head -8; done
