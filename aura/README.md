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

---

# Cuarto edit: mecánica clásica

`videos/aura4/mecanica_aura_124bpm.mp4`: 40,6 s exactos (84 pulsos a 124 BPM). Piezas sueltas en
`videos/aura4/clips/` y palabras en `videos/aura4/clips/textos/` (`.mov` transparente y `.mp4` sobre negro).

**Formato.**
- **Capítulos:** cuatro, con numeral romano en serif y nombre espaciado arriba a la izquierda:
  I Newton · II Oscilaciones · III Lagrange · Hamilton · IV Gravitación · Caos.
- **Regla de compases** en el borde derecho, con una marca que baja al ritmo durante todo el vídeo.
- **Palabras** enormes en serif cursiva con su ecuación debajo, una por capítulo: *inertia*, *resonance*,
  *symmetry*, *chaos*. Cierre: *everything moves.*
- **Transiciones mecánicas:** `rebote` (zoom amortiguado, como un muelle), `pendulo` (vaivén horizontal
  amortiguado), `giro`, `dividir` (las dos mitades encajan), además de `corte`, `flash` y `suave`.
- **Etalonaje:** tono partido, con sombras frías y luces cálidas.

**Tomas.**
- **Newton y sólido rígido:** plano inclinado con diagrama de fuerzas, explosión con el centro de masas en parábola,
  rodadura con cicloide (König), Steiner, conservación del momento angular, Atwood, cohete (Tsiolkovski),
  cuna de Newton, colisión elástica 2D y transformación de Galileo.
- **Oscilaciones:** los tres regímenes de amortiguamiento, péndulo de Pohl con curva de resonancia, péndulos
  acoplados (batidos) y curvas de Lissajous.
- **Lagrange y Hamilton:** flujo en el espacio de fases del péndulo; el área se conserva (Liouville).
- **Gravitación y caos:** hodógrafa de Kepler, puntos de Lagrange en el sistema que gira, péndulos dobles que
  divergen y el fractal de condiciones iniciales del péndulo doble.

```bash
./render_todo4.sh 124                                    # todo
/opt/mvenv/bin/python montar4.py --solo-montaje --bpm 128  # solo re-montar
```

---

# Quinto edit: electrostática (temas 1, 2 y 3)

`videos/aura5/electro_aura_128bpm.mp4`: 46,4 s exactos (99 pulsos a 128 BPM). Piezas sueltas en
`videos/aura5/clips/` y tarjetas en `videos/aura5/clips/textos/` (`.mov` transparente y `.mp4` sobre negro).

**Formato.**
- **Etalonaje frío con halación:** las luces intensas sangran un halo rojizo, como en película.
- **Medidor de pulso:** pequeño y horizontal, arriba a la izquierda (8 segmentos cian, ámbar y magenta) que
  se dispara en cada golpe y decae.
- **Etiqueta de tema** arriba a la derecha: TEMA 1 · leyes básicas, TEMA 2 · desarrollo multipolar,
  TEMA 3 · conductores.
- **Tarjetas-ecuación** que se encienden parpadeando como un tubo fluorescente: ∇·E = ρ/ε₀, el desarrollo
  multipolar y E_int = 0. Cierre: ∮E·dS = Q/ε₀ y *every field line begins and ends on a charge.*
- **Transiciones eléctricas:** `descarga`, `chispa`, `polaridad` e `implosion`.

**Motor de campos (`numerico5.py`).** Cargas puntuales analíticas o conductores resueltos con Laplace en
diferencias finitas (factorización LU reutilizada cuando la geometría no cambia). Las equipotenciales tienen
grosor constante y las líneas de campo se siembran según el flujo, con pulsos que viajan por ellas.

**Tomas.**
- **Tema 1:** ∇·E = ρ/ε₀ con densidades de carga que se mueven y miles de trazadores que nacen en las fuentes y
  mueren en los sumideros, divergencia como flujo por unidad de volumen (un cubito que se encoge), una superficie
  de Gauss que se pasea entre cargas con su flujo, Coulomb, divergencia de û/R² y delta de Dirac, anillo → disco → plano, Gauss con esfera
  uniforme, condiciones de contorno con σ, relieve 3D del potencial, teoremas de Gauss y Stokes, dipolo que
  gira y dos cargas iguales que se acercan.
- **Tema 2:** esfera dieléctrica cuyos dipolos se alinean (P no uniforme: ρ_b = −∇·P dentro y σ_b = P·n en la
  superficie), desarrollo multipolar visto desde cada vez más lejos, polinomios de Legendre (de monopolo a
  octupolo), cuadrupolo y polarización con cargas de polarización.
- **Tema 3:** dos esferas unidas por un hilo, cavidad con carga que se mueve sin cambiar el
  campo exterior, jaula de Faraday en un campo que gira, carga frente a un plano a tierra (σ inducida),
  condensador que se carga, los tres condensadores canónicos, sistema de tres conductores con potenciales
  variables, coeficientes de capacidad e influencia, descarga a tierra y ruptura dieléctrica (modelo DBM).

```bash
./render_todo5.sh 128                                    # todo
/opt/mvenv/bin/python montar5.py --solo-montaje --bpm 120  # solo re-montar
```
