#!/bin/bash
# usage: new_project.sh <project_dir>   — copies the template into a fresh project folder
set -e
SKILL="$(cd "$(dirname "$0")/.." && pwd)"
DEST=${1:?usage: new_project.sh <project_dir>}
mkdir -p "$DEST"
cp -Rn "$SKILL/template/." "$DEST/" 2>/dev/null || true   # never overwrite existing files
chmod +x "$DEST"/*.sh "$DEST"/tools/*.sh 2>/dev/null || true
echo "Project ready at $DEST"
