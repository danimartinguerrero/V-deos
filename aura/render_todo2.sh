#!/bin/bash
# Segundo edit: renderiza tomas (numpy + Manim + citas) y monta. Uso: ./render_todo2.sh [BPM]
cd "$(dirname "$0")"
BRUTO=${BRUTO:-/tmp/aura2_bruto}
PY=${PY:-/opt/mvenv/bin/python}
MANIM=${MANIM:-/opt/mvenv/bin/manim}
J=${JOBS:-3}
mkdir -p "$BRUTO/num" "$BRUTO/manim"
$PY -c "import numerico2; print('\n'.join(numerico2.TOMAS))" | \
  xargs -P $J -I{} sh -c "[ -f $BRUTO/num/{}.mp4 ] || $PY numerico2.py $BRUTO/num {}"
$PY -c "import escenas2; print('\n'.join(escenas2.TOMAS))" 2>/dev/null | \
  xargs -P $J -I{} sh -c "[ -n \"\$(find $BRUTO/manim/{} -name '{}.mp4' 2>/dev/null)\" ] || $MANIM render -q h --disable_caching --media_dir $BRUTO/manim/{} escenas2.py {} > $BRUTO/manim/{}.log 2>&1; echo manim {}"
$PY -c "import escenas2; print('\n'.join(escenas2.CITAS))" 2>/dev/null | \
  xargs -P $J -I{} sh -c "[ -n \"\$(find $BRUTO/manim/{} -name '{}.mov' 2>/dev/null)\" ] || $MANIM render -q h -t --disable_caching --media_dir $BRUTO/manim/{} escenas2.py {} > $BRUTO/manim/{}.log 2>&1; echo cita {}"
$PY montar2.py --bruto "$BRUTO" --bpm ${1:-120}
