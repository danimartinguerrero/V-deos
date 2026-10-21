#!/bin/bash
# Renderiza todos los clips en 1080x1920 a 60 fps y los copia a ../videos/
cd "$(dirname "$0")"
TMP=${TMP_RENDER:-/tmp/render_clips}
OUT=../videos
mkdir -p "$TMP" "$OUT"
uno() {
  archivo=$1; escena=$2
  /opt/mvenv/bin/manim render -q h --media_dir "$TMP/$escena" "$archivo" "$escena" > "$TMP/$escena.log" 2>&1
  f=$(find "$TMP/$escena/videos" -name "$escena.mp4" | head -1)
  if [ -n "$f" ]; then
    ffmpeg -v error -i "$f" -c copy -movflags +faststart -y "$OUT/$escena.mp4" && echo "OK $escena"
  else
    echo "FALLO $escena"
  fi
}
export -f uno; export TMP OUT
cat <<LISTA | xargs -P ${JOBS:-4} -L1 bash -c 'uno "$0" "$1"'
edo.py EDO1_Linealidad
edo.py EDO2_Oscilador
edo.py EDO3_RaicesMultiples
edo.py EDO4_VariacionConstantes
green.py Green1_Impulsos
green.py Green2_SaltoCoulomb
instrumentacion.py Instr1_AO
instrumentacion.py Instr2_InversorNoInversor
instrumentacion.py Instr3_ImpedanciaLaplace
instrumentacion.py Instr4_FiltroPasoBajo
instrumentacion.py Instr5_GBW
termo.py Termo1_Sistemas
termo.py Termo2_LeyCero
termo.py Termo3_EcuacionEstado
termo.py Termo4_Coeficientes
LISTA
