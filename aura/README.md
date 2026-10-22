# Plantilla «Física con aura»

Un edit vertical de física (1080×1920, 60 fps, sin audio) cortado al ritmo de un BPM,
y todas sus piezas sueltas para reeditarlas a mano con tu canción.

## Qué hay

- `videos/aura/fisica_aura_120bpm.mp4`: el edit montado (~45 s a 120 BPM).
- `videos/aura/clips/`: cada toma etalonada por separado (con bloom y viñeta, sin grano) para
  montarla tú en CapCut o en otro editor.
- `videos/aura/clips/citas/`: las citas como vídeo con transparencia (`.mov`), listas para
  superponerlas sobre cualquier toma.

## Estética

Negro puro, trazo fino marfil, un único acento de color por rama de la física
(cian para el electromagnetismo, violeta para la cuántica, oro para la gravitación, carmesí para el caos)
y luz en las tomas de óptica. En el etalonaje se añaden bloom, curva de contraste y viñeta. En los cortes
entran el golpe de zoom, el destello blanco y la aberración cromática, y sobre todo el montaje va el grano de película.

## Tomas

| Rama | Tomas animadas (Manim) | Tomas calculadas (numpy) |
|---|---|---|
| Electrodinámica | `Maxwell`, `Dipolo`, `OndaEM` | |
| Cuántica y lagrangiana | `Schrodinger`, `AccionMinima` | `orbital` (|ψ₅₃₁|²), `espectro` (serie de Balmer) |
| Gravitación y órbitas | `Kepler`, `TresCuerpos` (ocho de Chenciner–Montgomery), `PozoGravitatorio` | `lente_gravitacional` (anillo de Einstein) |
| EDO | `Lorenz`, `PenduloFase` | |
| Variable compleja | `Conforme` (w = z²) | `dominio_color` |
| Exponencial compleja | `Euler`, `Fourier` (epiciclos que dibujan ψ) | |
| Ondas y óptica | `Prisma`, `Estacionarias` | `interferencia`, `doble_rendija`, `airy`, `causticas`, `pelicula_jabon` |

Las tomas «calculadas» son simulaciones físicas con aspecto fotográfico (láser con moteado sobre una pared,
cáusticas de una piscina, colores de película delgada integrados sobre el espectro, etc.). **No son fotografías.**

## Citas

| Cita | Autor | Fuente |
|---|---|---|
| “Nature uses only the longest threads to weave her patterns…” | Richard Feynman | *The Character of Physical Law* (1965) |
| “What we observe is not nature itself, but nature exposed to our method of questioning.” | Werner Heisenberg | *Physics and Philosophy* (1958) |
| “The cosmos is also within us. We're made of star stuff…” | Carl Sagan | *Cosmos*, episodio 1 (1980) |
| “We are the cosmos made conscious…” | Brian Cox | *Wonders of the Universe* (BBC, 2011) |

El vídeo termina con *Science is elegant.*

## Tus fotos

Mete fotos (`.jpg` o `.png`) en `aura/fotos/` y vuelve a ejecutar el script. Cada foto se convierte en un clip con
movimiento lento (Ken Burns), recibe el mismo etalonaje y se intercala sola en la subida y en el drop.
Usa fotos con licencia libre (por ejemplo, de NASA, ESA o Wikimedia Commons) y respeta la atribución que pidan.

## Cambiar el ritmo o el orden

```bash
./render_todo.sh 128                                   # todo, cortado a 128 BPM
/opt/mvenv/bin/python montar.py --solo-montaje --bpm 95  # solo re-montar con los clips ya hechos
```

El orden, la duración en pulsos y el efecto de cada plano están en la lista `GUION` de `montar.py`:
`(toma, segundo de inicio, pulsos, efecto[, cita])`, donde el efecto puede ser `suave`, `corte` o `flash`.
La estructura es: título, presentación (4 pulsos por plano), subida (2), drop (1) y final con las citas lentas.
Busca una canción del BPM elegido y alinea su primer golpe con el principio del vídeo.
