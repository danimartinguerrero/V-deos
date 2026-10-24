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

---

# Segundo edit: «Cosmos, del calor a las estrellas»

`videos/aura2/fisica_aura2_120bpm.mp4`: 40 s exactos (80 pulsos a 120 BPM), más rápido que el primero.
Las piezas sueltas están en `videos/aura2/clips/`.

**Contenido.**
- **Termodinámica:** distribución de Maxwell–Boltzmann, ciclo de Carnot, entropía de mezcla.
- **Nanomagnetismo:** precesión LLG del espín, ciclo de histéresis con dominios, red de skyrmiones.
- **Partículas:** cámara de burbujas con creación de pares, diagrama de Feynman, potencial de Higgs.
- **Astrofísica:** galaxia espiral con rotación diferencial, agujero negro con disco de acreción, nebulosa,
  ondas gravitacionales (chirp y fusión), púlsar, ley de Hubble, diagrama HR.
- **Electricidad y fasores:** descarga ramificada, fasores RLC y resonancia, corriente trifásica.
- **Mecánica:** giróscopo con precesión y nutación.

**Transiciones nuevas** (`efecto` en `GUION` de `montar2.py`): `barrido` (entra en lateral con desenfoque de movimiento),
`glitch`, `sacudida`, `invertir` (destello en negativo), `zoom` (entra desde muy cerca y desenfocado), además de
`flash`, `corte` y `suave`. La opción `{"vel": 1.5}` acelera una toma, y los planos de medio pulso hacen el tartamudeo
antes del final.

**Citas.**
- Arthur Eddington, *The Nature of the Physical World* (1928): “The law that entropy always increases holds, I think,
  the supreme position among the laws of Nature.”
- Carl Sagan, *Cosmos*, episodio 9 (1980): “The nitrogen in our DNA, the calcium in our teeth, the iron in our blood…
  were made in the interiors of collapsing stars.”

Cierre: *Per aspera ad astra.*

```bash
./render_todo2.sh 124                                     # todo, a 124 BPM
/opt/mvenv/bin/python montar2.py --solo-montaje --bpm 95    # solo re-montar
```

---

# Tercer edit: óptica

`videos/aura3/optica_aura_128bpm.mp4`: 37,5 s exactos (80 pulsos a 128 BPM). Las piezas sueltas están en
`videos/aura3/clips/`, y los textos en `videos/aura3/clips/textos/` (`.mov` con transparencia y `.mp4` sobre negro).

**Formato distinto:**
- **Etalonaje anamórfico:** destellos horizontales azulados en las luces intensas.
- **Visor de cámara:** esquinas de encuadre, ● REC, «4K 60P», código de tiempo y una lectura técnica por plano en
  monoespaciada. No se nombra ningún fenómeno.
- **Textos cinéticos:** sans fina en minúsculas, alineados a la izquierda, con una línea espectral debajo.
  Sustituyen a las citas: *light* · *it always finds the fastest way* · *every color was hiding in the white* ·
  *a trillionth of a second, frozen* · *everything we know, we know by light*.
- **Transiciones:** `espectral` (los canales RGB llegan separados y convergen), `estrobo`, `sobreexp`
  (sobreexposición que se recupera), `estela` (entra desde arriba con desenfoque vertical), además de `zoom`,
  `flash` y `corte`.

**Tomas:**
- **Láseres:** en humo (abanico, cruce RGB, rebotes entre espejos), moteado, anillos de Michelson, cavidad láser,
  mode-locking (de los modos al tren de pulsos) y un pulso ultracorto comprimiéndose (chirp).
- **Difracción:** Fraunhofer con aberturas que cambian de forma, disco de Airy, doble rendija y Huygens con
  1, 2 y 5 rendijas.
- **Rayos:** Snell y reflexión total, guiado en una fibra, lámpara de fibras, principio de Fermat, espejismo y
  cáustica nefroide.
- **Color:** prisma giratorio con trazado de rayos real, arcoíris primario y secundario, atardecer de Rayleigh y
  espectro solar con líneas de Fraunhofer.
- **Interferencia y polarización:** anillos de Newton, película de jabón, disco holográfico, fotoelasticidad,
  polarización lineal, circular y elíptica, y ley de Malus.

```bash
./render_todo3.sh 128                                    # todo
/opt/mvenv/bin/python montar3.py --solo-montaje --bpm 140  # solo re-montar
```
