#!/bin/bash
# Cuarto edit (mecánica clásica): renderiza tomas y palabras, y monta. Uso: ./render_todo4.sh [BPM]
cd "$(dirname "$0")"
BRUTO=${BRUTO:-/tmp/aura4_bruto}
PY=${PY:-/opt/mvenv/bin/python}
MANIM=${MANIM:-/opt/mvenv/bin/manim}
J=${JOBS:-3}
mkdir -p "$BRUTO/num" "$BRUTO/manim"
for t in caos_fractal lagrange; do [ -f $BRUTO/num/$t.mp4 ] || $PY numerico4.py $BRUTO/num $t; done
$PY -c "import escenas4; print('\n'.join(escenas4.TOMAS))" 2>/dev/null | \
  xargs -P $J -I{} sh -c "[ -n \"\$(find $BRUTO/manim/{} -name '{}.mp4' 2>/dev/null)\" ] || $MANIM render -q h --disable_caching --media_dir $BRUTO/manim/{} escenas4.py {} > $BRUTO/manim/{}.log 2>&1; echo manim {}"
$PY -c "import escenas4; print('\n'.join(escenas4.CITAS))" 2>/dev/null | \
  xargs -P $J -I{} sh -c "[ -n \"\$(find $BRUTO/manim/{} -name '{}.mov' 2>/dev/null)\" ] || $MANIM render -q h -t --disable_caching --media_dir $BRUTO/manim/{} escenas4.py {} > $BRUTO/manim/{}.log 2>&1; echo palabra {}"
$PY montar4.py --bruto "$BRUTO" --bpm ${1:-124}
