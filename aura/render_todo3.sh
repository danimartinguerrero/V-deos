#!/bin/bash
# Tercer edit (óptica): renderiza tomas y textos, y monta. Uso: ./render_todo3.sh [BPM]
# Reutiliza airy, doble_rendija y pelicula_jabon del primer edit (BRUTO1).
cd "$(dirname "$0")"
BRUTO=${BRUTO:-/tmp/aura3_bruto}
BRUTO1=${BRUTO1:-/tmp/aura_bruto}
PY=${PY:-/opt/mvenv/bin/python}
MANIM=${MANIM:-/opt/mvenv/bin/manim}
J=${JOBS:-3}
mkdir -p "$BRUTO/num" "$BRUTO/manim" "$BRUTO1/num"
for t in airy doble_rendija pelicula_jabon; do [ -f $BRUTO1/num/$t.mp4 ] || $PY numerico.py $BRUTO1/num $t; done
$PY -c "import numerico3; print('\n'.join(numerico3.TOMAS))" | \
  xargs -P $J -I{} sh -c "[ -f $BRUTO/num/{}.mp4 ] || $PY numerico3.py $BRUTO/num {}"
$PY -c "import escenas3; print('\n'.join(escenas3.TOMAS))" 2>/dev/null | \
  xargs -P $J -I{} sh -c "[ -n \"\$(find $BRUTO/manim/{} -name '{}.mp4' 2>/dev/null)\" ] || $MANIM render -q h --disable_caching --media_dir $BRUTO/manim/{} escenas3.py {} > $BRUTO/manim/{}.log 2>&1; echo manim {}"
$PY -c "import escenas3; print('\n'.join(escenas3.CITAS))" 2>/dev/null | \
  xargs -P $J -I{} sh -c "[ -n \"\$(find $BRUTO/manim/{} -name '{}.mov' 2>/dev/null)\" ] || $MANIM render -q h -t --disable_caching --media_dir $BRUTO/manim/{} escenas3.py {} > $BRUTO/manim/{}.log 2>&1; echo texto {}"
$PY montar3.py --bruto "$BRUTO" --bruto "$BRUTO1" --bpm ${1:-128}
