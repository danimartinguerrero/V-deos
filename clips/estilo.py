"""Estilo común de los clips verticales (TikTok, 1080x1920) al modo 3Blue1Brown.

Cada clip hereda de ``Clip`` y define ``cuerpo()``. La clase se encarga del
fondo degradado, la cabecera con la serie, la barra de progreso, el título
inicial y la tarjeta final.
"""

from __future__ import annotations

import numpy as np
from manim import *

# ---------------------------------------------------------------------------
# Formato vertical
# ---------------------------------------------------------------------------
import os

if os.environ.get("PREVIEW"):  # borrador rápido para revisar la composición
    config.pixel_width, config.pixel_height, config.frame_rate = 360, 640, 15
else:
    config.pixel_width, config.pixel_height, config.frame_rate = 1080, 1920, 60
config.frame_height = 16.0
config.frame_width = 9.0
config.background_color = "#02040c"

FUENTE = "CMU Serif"
FUENTE_SANS = "CMU Sans Serif"

# ---------------------------------------------------------------------------
# Paleta: dominan los azules, con acentos de toda la gama cromática
# ---------------------------------------------------------------------------
CIELO = "#8FD8FF"
CELESTE = "#4FC3F7"
AZUL = "#2F80ED"
ZAFIRO = "#1E4FD8"
INDIGO = "#5B5BF0"
VIOLETA = "#9B6CFF"
MAGENTA = "#E86BD8"
CORAL = "#FF7A7A"
AMBAR = "#FFC15E"
LIMA = "#B8F07A"
TURQUESA = "#3FE0C5"
TINTA = "#E9F1FF"
GRIS = "#8A9BC2"

DEG_AZUL = [CIELO, CELESTE, AZUL, INDIGO]
DEG_FRIO = [TURQUESA, CELESTE, AZUL, VIOLETA]
DEG_CALIDO = [AMBAR, CORAL, MAGENTA]
DEG_ARCOIRIS = [TURQUESA, CELESTE, AZUL, VIOLETA, MAGENTA, CORAL, AMBAR]

PLANTILLA = TexTemplate()
PLANTILLA.add_to_preamble(r"\usepackage{amsmath,amssymb,bm,mathtools}")


ESCALA = 1.3  # todo un poco más grande: se ve en un móvil
ANCHO_MAX = 8.3


def ajustar(mob, ancho=ANCHO_MAX):
    if mob.width > ancho:
        mob.width = ancho
    return mob


def tex(*cadenas, color=TINTA, font_size=48, **kw) -> MathTex:
    kw.setdefault("tex_template", PLANTILLA)
    return ajustar(MathTex(*cadenas, color=color, font_size=font_size * ESCALA, **kw))


def texto(cad, size=34, color=TINTA, fuente=FUENTE, **kw) -> Text:
    return ajustar(Text(cad, font=fuente, font_size=size * ESCALA, color=color, **kw))


def degradado(mob, colores=DEG_AZUL):
    mob.set_color_by_gradient(*colores)
    return mob


def brillo(mob, color=CELESTE, capas=6, ancho=14, opacidad=0.10):
    """Halo suave: copias del trazo cada vez más anchas y transparentes."""
    halo = VGroup()
    for i in range(1, capas + 1):
        c = mob.copy()
        c.set_fill(opacity=0)
        c.set_stroke(color, width=ancho * i / capas, opacity=opacidad * (1 - (i - 1) / capas))
        halo.add(c)
    return halo


def fondo_degradado(tono_alto="#123d86", tono_bajo="#3a1764") -> ImageMobject:
    """Fondo: brillo azul arriba, violeta tenue abajo, viñeta oscura."""
    w, h = 270, 480  # se escala sin perder suavidad
    y, x = np.mgrid[0:h, 0:w].astype(float)
    x = (x - w / 2) / w
    y = y / h
    base = np.array([2, 4, 12], dtype=float)

    def hexrgb(c):
        c = c.lstrip("#")
        return np.array([int(c[i:i + 2], 16) for i in (0, 2, 4)], dtype=float)

    g1 = np.exp(-((x / 0.75) ** 2 + ((y - 0.18) / 0.42) ** 2))
    g2 = np.exp(-(((x - 0.15) / 0.8) ** 2 + ((y - 0.95) / 0.35) ** 2))
    img = base + g1[..., None] * (hexrgb(tono_alto) - base) * 0.85
    img = img + g2[..., None] * (hexrgb(tono_bajo) - base) * 0.55
    vin = 1 - 0.55 * (np.abs(x) * 1.4) ** 2.2
    img = np.clip(img * vin[..., None], 0, 255).astype(np.uint8)
    rgba = np.dstack([img, np.full((h, w), 255, np.uint8)])
    fondo = ImageMobject(rgba)
    fondo.set_resampling_algorithm(RESAMPLING_ALGORITHMS["linear"])
    fondo.height = config.frame_height
    fondo.width = config.frame_width
    return fondo


def caja(mob, colores=(CELESTE, VIOLETA), buff=0.3, radio=0.25):
    marco = SurroundingRectangle(mob, buff=buff, corner_radius=radio)
    marco.set_stroke(width=3)
    marco.set_color(list(colores))
    marco.set_fill("#0a1430", opacity=0.55)
    return marco


def particulas(n=60, seed=1, zona=(4.4, 7.8)):
    """Polvo de estrellas que flota lentamente en el fondo."""
    rng = np.random.default_rng(seed)
    puntos = VGroup()
    for _ in range(n):
        p = Dot(
            [rng.uniform(-zona[0], zona[0]), rng.uniform(-zona[1], zona[1]), 0],
            radius=rng.uniform(0.008, 0.03),
            color=rng.choice([CIELO, CELESTE, VIOLETA, TINTA]),
        ).set_opacity(rng.uniform(0.15, 0.55))
        p.v = rng.uniform(0.03, 0.12)
        puntos.add(p)

    def flotar(grupo, dt):
        for p in grupo:
            p.shift(UP * p.v * dt)
            if p.get_y() > zona[1]:
                p.set_y(-zona[1])

    puntos.add_updater(flotar)
    return puntos


# ---------------------------------------------------------------------------
# Escena base
# ---------------------------------------------------------------------------
class Clip(Scene):
    serie = "SERIE"
    numero = "1/1"
    titulo = "Título"
    subtitulo = ""
    colores_titulo = DEG_AZUL
    duracion = 30.0
    fondo = ("#123d86", "#3a1764")

    def setup(self):
        self.add(fondo_degradado(*self.fondo))
        self.add(particulas())
        self._t = 0.0
        self._cabecera()
        self.fijos = list(self.mobjects)
        self.cabecera_titulo = VGroup()

    def _cabecera(self):
        top = config.frame_height / 2
        etiqueta = texto(self.serie.upper(), size=22, color=GRIS, fuente=FUENTE_SANS)
        num = texto(self.numero, size=22, color=CELESTE, fuente=FUENTE_SANS)
        fila = VGroup(etiqueta, num).arrange(RIGHT, buff=0.35)
        fila.move_to([0, top - 0.75, 0])
        pista = Line([-3.6, top - 1.15, 0], [3.6, top - 1.15, 0], stroke_width=3, color=WHITE)
        pista.set_opacity(0.12)
        barra = Line([-3.6, top - 1.15, 0], [-3.59, top - 1.15, 0], stroke_width=4)
        barra.set_color([CELESTE, VIOLETA])
        x0, x1 = -3.6, 3.6

        def avanzar(m, dt):
            self._t += dt
            f = min(self._t / self.duracion, 1.0)
            m.put_start_and_end_on([x0, top - 1.15, 0], [x0 + max(f, 0.002) * (x1 - x0), top - 1.15, 0])

        barra.add_updater(avanzar)
        self.add(fila, pista, barra)

    # -- piezas reutilizables ------------------------------------------------
    def portada(self):
        t = texto(self.titulo, size=64, weight=BOLD)
        if t.width > 8:
            t.width = 8
        degradado(t, self.colores_titulo)
        grupo = VGroup(t)
        if self.subtitulo:
            s = texto(self.subtitulo, size=30, color=GRIS, slant=ITALIC)
            if s.width > 8:
                s.width = 8
            grupo.add(s)
        grupo.arrange(DOWN, buff=0.35).move_to(UP * 0.3)
        linea = Line(LEFT * 2.5, RIGHT * 2.5, stroke_width=3).next_to(grupo, DOWN, buff=0.45)
        linea.set_color([CELESTE, VIOLETA, MAGENTA])
        self.play(Write(t, run_time=1.4), GrowFromCenter(linea, run_time=1.2))
        if self.subtitulo:
            self.play(FadeIn(grupo[1], shift=UP * 0.2), run_time=0.7)
        self.wait(0.6)
        self.play(
            grupo.animate.scale(0.62).to_edge(UP, buff=1.55),
            linea.animate.scale(0.62).move_to(UP * (config.frame_height / 2 - 1.55 - 1.45)),
            run_time=0.9,
        )
        self.cabecera_titulo = VGroup(grupo, linea)
        self.remove(*grupo, linea)
        self.add(self.cabecera_titulo)
        return self.cabecera_titulo

    def rotulo(self, cad, pos=DOWN * 5.0, size=30, color=CIELO):
        r = texto(cad, size=size, color=color, slant=ITALIC)
        if r.width > 8.2:
            r.width = 8.2
        r.move_to(pos)
        return r

    def limpiar(self, *excepto, run_time=0.6):
        quedan = list(excepto) + [self.cabecera_titulo] + self.fijos
        fuera = [m for m in self.mobjects if all(m is not q for q in quedan)]
        if fuera:
            self.play(*[FadeOut(m) for m in fuera], run_time=run_time)
        for m in fuera:
            m.clear_updaters()
            self.remove(m)

    def cierre(self, formula: Mobject, frase: str):
        self.limpiar()
        ajustar(formula, 7.2)
        formula.move_to(UP * 0.6)
        marco = caja(formula, buff=0.45)
        halo = brillo(marco, CELESTE, capas=8, ancho=30, opacidad=0.08)
        f = texto(frase, size=30, color=GRIS, slant=ITALIC)
        if f.width > 8:
            f.width = 8
        f.next_to(marco, DOWN, buff=0.6)
        self.play(FadeIn(halo), Create(marco), Write(formula), run_time=1.6)
        self.play(FadeIn(f, shift=UP * 0.2), run_time=0.8)
        # el halo respira mientras se lee la idea clave
        reloj = [0.0]

        for c in halo:
            c.base = c.get_stroke_opacity()

        def respirar(m, dt):
            reloj[0] += dt
            k = 0.55 + 0.9 * np.sin(1.8 * reloj[0]) ** 2
            for c in m:
                c.set_stroke(opacity=c.base * k)

        halo.add_updater(respirar)
        destello = marco.copy().set_fill(opacity=0).set_stroke(TINTA, width=5)
        restante = min(max(self.duracion - self._t - 0.8, 2.5), 6.0)
        self.play(ShowPassingFlash(destello, time_width=0.25, run_time=1.4))
        self.wait(max(restante - 1.4, 0.5))
        halo.clear_updaters()
        self.play(*[FadeOut(m) for m in (formula, marco, halo, f)], run_time=0.8)

    def construct(self):
        self.portada()
        self.cuerpo()

    def cuerpo(self):
        pass
