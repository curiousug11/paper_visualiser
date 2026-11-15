#!/bin/bash
# One-time environment setup for paper-video. Idempotent; safe to re-run.
# Creates a Python 3.12 venv (Kokoro's spaCy deps do not build on 3.13) holding Manim + Kokoro.
set -e
VENV=${PV_VENV:-$HOME/.venvs/papervideo}

need_apt=()
command -v latex   >/dev/null || need_apt+=(texlive-latex-base texlive-latex-extra texlive-fonts-recommended texlive-science cm-super)
command -v dvisvgm >/dev/null || need_apt+=(dvisvgm)
command -v ffmpeg  >/dev/null || need_apt+=(ffmpeg)
pkg-config --exists pangocairo 2>/dev/null || need_apt+=(libpango1.0-dev libcairo2-dev pkg-config)
command -v espeak-ng >/dev/null || need_apt+=(espeak-ng)
if [ ${#need_apt[@]} -gt 0 ]; then
  if command -v apt-get >/dev/null; then
    SUDO=$([ "$(id -u)" = 0 ] && echo "" || echo sudo)
    $SUDO apt-get update -qq && DEBIAN_FRONTEND=noninteractive $SUDO apt-get install -y -qq "${need_apt[@]}"
  elif command -v brew >/dev/null; then
    brew install ffmpeg pango espeak-ng; echo "Install MacTeX (or BasicTeX + dvisvgm) for LaTeX."
  else
    echo "Install manually: ${need_apt[*]}"; exit 1
  fi
fi

if [ ! -x "$VENV/bin/python" ]; then
  if command -v uv >/dev/null; then uv venv -q -p 3.12 "$VENV"
  else python3.12 -m venv "$VENV"; fi
fi
pipi() {
  if command -v uv >/dev/null; then uv pip install -q --python "$VENV/bin/python" "$@"
  else "$VENV/bin/python" -m pip install -q "$@"; fi
}
# CPU torch is enough for Kokoro (82M params); skip the multi-GB CUDA wheels. (macOS: default wheel.)
if [ "$(uname)" = Linux ]; then pipi torch --index-url https://download.pytorch.org/whl/cpu; else pipi torch; fi
pipi manim kokoro soundfile pip
# warm up: downloads Kokoro weights + spaCy English model once
"$VENV/bin/python" -c "
from kokoro import KPipeline; p=KPipeline(lang_code='a')
for _ in p('Setup complete.', voice='af_heart'): pass
import manim; print('manim', manim.__version__, '| kokoro OK')" 2>&1 | grep -v -i warn | tail -2
echo "Venv: $VENV   (export PV_VENV to change)"
