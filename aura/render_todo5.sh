#!/bin/bash
# Quinto edit (electrostática): renderiza tomas y tarjetas, y monta. Uso: ./render_todo5.sh [BPM]
cd "$(dirname "$0")"
BRUTO=${BRUTO:-/tmp/aura5_bruto}
PY=${PY:-/opt/mvenv/bin/python}
MANIM=${MANIM:-/opt/mvenv/bin/manim}
J=${JOBS:-3}
mkdir -p "$BRUTO/num" "$BRUTO/manim"
$PY -c "import numerico5; print('\n'.join(numerico5.TOMAS))" | \
  xargs -P 2 -I{} sh -c "[ -f $BRUTO/num/{}.mp4 ] || $PY numerico5.py $BRUTO/num {}"
$PY -c "import escenas5; print('\n'.join(escenas5.TOMAS))" 2>/dev/null | \
  xargs -P $J -I{} sh -c "[ -n \"\$(find $BRUTO/manim/{} -name '{}.mp4' 2>/dev/null)\" ] || $MANIM render -q h --disable_caching --media_dir $BRUTO/manim/{} escenas5.py {} > $BRUTO/manim/{}.log 2>&1; echo manim {}"
$PY -c "import escenas5; print('\n'.join(escenas5.CITAS))" 2>/dev/null | \
  xargs -P $J -I{} sh -c "[ -n \"\$(find $BRUTO/manim/{} -name '{}.mov' 2>/dev/null)\" ] || $MANIM render -q h -t --disable_caching --media_dir $BRUTO/manim/{} escenas5.py {} > $BRUTO/manim/{}.log 2>&1; echo tarjeta {}"
$PY montar5.py --bruto "$BRUTO" --bpm ${1:-128}
