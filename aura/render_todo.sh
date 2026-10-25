#!/bin/bash
# Renderiza todas las tomas (Manim + numpy + citas) en alta calidad y monta el edit.
# Uso: ./render_todo.sh [BPM]
cd "$(dirname "$0")"
BRUTO=${BRUTO:-/tmp/aura_bruto}
PY=${PY:-/opt/mvenv/bin/python}
MANIM=${MANIM:-/opt/mvenv/bin/manim}
J=${JOBS:-3}
mkdir -p "$BRUTO/num" "$BRUTO/manim"
grep -oE '^def [a-z_]+\(ruta' numerico.py | sed 's/def //; s/(ruta//' | grep -v escribir | \
  xargs -P $J -I{} sh -c "[ -f $BRUTO/num/{}.mp4 ] || $PY numerico.py $BRUTO/num {}"
$PY -c "import escenas; print('\n'.join(escenas.TOMAS))" 2>/dev/null | \
  xargs -P $J -I{} sh -c "[ -n \"\$(find $BRUTO/manim/{} -name '{}.mp4' 2>/dev/null)\" ] || $MANIM render -q h --disable_caching --media_dir $BRUTO/manim/{} escenas.py {} > $BRUTO/manim/{}.log 2>&1; echo manim {}"
$PY -c "import escenas; print('\n'.join(escenas.CITAS))" 2>/dev/null | \
  xargs -P $J -I{} sh -c "[ -n \"\$(find $BRUTO/manim/{} -name '{}.mov' 2>/dev/null)\" ] || $MANIM render -q h -t --disable_caching --media_dir $BRUTO/manim/{} escenas.py {} > $BRUTO/manim/{}.log 2>&1; echo cita {}"
$PY montar.py --bruto "$BRUTO" --bpm ${1:-120}
