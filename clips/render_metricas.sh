#!/bin/bash
# Renderiza los clips de Métricas y polaridades (1080x1920, 60 fps) en ../videos/metricas/
cd "$(dirname "$0")"
TMP=${TMP_RENDER:-/tmp/render_clips}
OUT=../videos/metricas
mkdir -p "$TMP" "$OUT"
uno() {
  escena=$1
  /opt/mvenv/bin/manim render -q h --media_dir "$TMP/$escena" metricas.py "$escena" > "$TMP/$escena.log" 2>&1
  f=$(find "$TMP/$escena/videos" -name "$escena.mp4" | head -1)
  if [ -n "$f" ]; then
    ffmpeg -v error -i "$f" -c copy -movflags +faststart -y "$OUT/$escena.mp4" && echo "OK $escena"
  else
    echo "FALLO $escena"
  fi
}
export -f uno; export TMP OUT
grep -oE "^class M[0-9]+_[A-Za-z]+" metricas.py | sed 's/class //' | xargs -P ${JOBS:-4} -I{} bash -c 'uno {}'
