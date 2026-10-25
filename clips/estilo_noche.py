"""Variante «noche» del estilo: fondo más oscuro, retícula tenue, cabecera con
cápsula a la izquierda y contador a la derecha, portada con número grande en
contorno y título alineado a la izquierda. Misma paleta y mismo ritmo."""

from estilo import *

NOCHE_BASE = "#010207"


def fondo_noche() -> Group:
    fondo = fondo_degradado("#0a2152", "#1b0b36")
    oscuro = Rectangle(width=config.frame_width, height=config.frame_height, stroke_width=0)
    oscuro.set_fill(NOCHE_BASE, opacity=0.35)
    reticula = NumberPlane(
        x_range=[-5, 5, 1], y_range=[-9, 9, 1], x_length=10, y_length=18,
        background_line_style={"stroke_color": AZUL, "stroke_width": 1, "stroke_opacity": 0.07},
        axis_config={"stroke_opacity": 0},
    )
    return Group(fondo, oscuro, reticula)


class ClipNoche(Clip):
    serie = "Álgebra Lineal II"
    total = 10
    indice = 1
    seccion = ""

    def setup(self):
        self.add(fondo_noche())
        self.add(particulas(n=45, seed=self.indice))
        self._t = 0.0
        self._cabecera()
        self.fijos = list(self.mobjects)
        self.cabecera_titulo = VGroup()

    def _cabecera(self):
        top = config.frame_height / 2
        etiqueta = texto(self.serie.upper(), size=19, color=CIELO, fuente=FUENTE_SANS)
        capsula = RoundedRectangle(width=etiqueta.width + 0.5, height=etiqueta.height + 0.32, corner_radius=0.2)
        capsula.set_stroke([CELESTE, VIOLETA], width=2).set_fill("#06102a", 0.8)
        pill = VGroup(capsula, etiqueta.move_to(capsula)).move_to([0, top - 0.8, 0]).to_edge(LEFT, buff=0.55)
        num = texto("%02d / %02d" % (self.indice, self.total), size=22, color=GRIS, fuente=FUENTE_SANS)
        num.move_to([0, top - 0.8, 0]).to_edge(RIGHT, buff=0.6)
        y = top - 1.35
        x0, x1 = -3.95, 3.95
        pista = Line([x0, y, 0], [x1, y, 0], stroke_width=2, color=WHITE).set_opacity(0.10)
        barra = Line([x0, y, 0], [x0 + 0.01, y, 0], stroke_width=3).set_color([TURQUESA, CELESTE, VIOLETA])
        cabeza = Dot([x0, y, 0], radius=0.05, color=TINTA)
        aura = Dot([x0, y, 0], radius=0.14, color=CELESTE).set_opacity(0.25)

        def avanzar(m, dt):
            self._t += dt
            f = min(self._t / self.duracion, 1.0)
            xe = x0 + max(f, 0.002) * (x1 - x0)
            m.put_start_and_end_on([x0, y, 0], [xe, y, 0])
            cabeza.move_to([xe, y, 0])
            aura.move_to([xe, y, 0])

        barra.add_updater(avanzar)
        self.add(pista, barra, aura, cabeza, pill, num)

    def portada(self):
        n = Text("%02d" % self.indice, font=FUENTE, font_size=230, weight=BOLD)
        n.set_fill(opacity=0.06).set_stroke(width=2.5)
        n.set_stroke(color=[TURQUESA, CELESTE, VIOLETA, MAGENTA])
        n.move_to(UP * 1.9)
        t = texto(self.titulo, size=58, weight=BOLD)
        degradado(t, self.colores_titulo)
        sec = texto(self.seccion.upper(), size=20, color=GRIS, fuente=FUENTE_SANS) if self.seccion else VGroup()
        s = texto(self.subtitulo, size=28, color=GRIS, slant=ITALIC) if self.subtitulo else VGroup()
        bloque = VGroup(*[m for m in (sec, t, s) if len(m.points) or len(m.submobjects)])
        bloque.arrange(DOWN, buff=0.3).next_to(n, DOWN, buff=0.35)
        self.play(DrawBorderThenFill(n, run_time=1.4), FadeIn(sec, shift=UP * 0.2, run_time=0.8))
        self.play(Write(t, run_time=1.1), FadeIn(s, shift=UP * 0.2, run_time=1.0))
        self.wait(0.5)
        # el título sube a la izquierda con una barra de acento
        destino = VGroup(t.copy(), s.copy()).scale(0.6)
        destino.arrange(DOWN, aligned_edge=LEFT, buff=0.12)
        destino.to_edge(LEFT, buff=0.85).set_y(config.frame_height / 2 - 2.3)
        acento = Line(UP * 0.5, DOWN * 0.5, stroke_width=5).set_color([CELESTE, MAGENTA])
        acento.set_height(destino.height + 0.1).next_to(destino, LEFT, buff=0.22)
        self.play(
            FadeOut(n, scale=0.6, shift=UP * 1.5), FadeOut(sec),
            Transform(t, destino[0]), Transform(s, destino[1]),
            GrowFromEdge(acento, UP), run_time=1.0,
        )
        self.cabecera_titulo = VGroup(t, s, acento)
        self.remove(t, s, acento)
        self.add(self.cabecera_titulo)
        return self.cabecera_titulo

    def cierre(self, formula: Mobject, frase: str):
        self.limpiar()
        ajustar(formula, 7.0)
        formula.move_to(UP * 0.4)
        r = SurroundingRectangle(formula, buff=0.5)
        largo = 0.55
        esquinas = VGroup()
        for c, dx, dy in ((r.get_corner(UL), 1, -1), (r.get_corner(UR), -1, -1),
                          (r.get_corner(DL), 1, 1), (r.get_corner(DR), -1, 1)):
            esquinas.add(VMobject().set_points_as_corners([c + RIGHT * dx * largo, c, c + UP * dy * largo]))
        esquinas.set_stroke(width=5).set_color([TURQUESA, CELESTE, VIOLETA, MAGENTA])
        velo = RoundedRectangle(width=r.width, height=r.height, corner_radius=0.15, stroke_width=0)
        velo.move_to(r).set_fill("#081430", 0.6)
        etiqueta = texto("IDEA CLAVE", size=18, color=CELESTE, fuente=FUENTE_SANS).next_to(r, UP, buff=0.3)
        f = texto(frase, size=28, color=GRIS, slant=ITALIC)
        ajustar(f, 7.8).next_to(r, DOWN, buff=0.55)
        self.play(FadeIn(velo), LaggedStart(*[Create(e) for e in esquinas], lag_ratio=0.15),
                  FadeIn(etiqueta, shift=DOWN * 0.2), Write(formula), run_time=1.6)
        self.play(FadeIn(f, shift=UP * 0.2), run_time=0.7)
        reloj = [0.0]

        def latir(m, dt):
            reloj[0] += dt
            m.set_stroke(width=4 + 2.5 * np.sin(2.0 * reloj[0]) ** 2)

        esquinas.add_updater(latir)
        brillo_linea = Line(r.get_corner(DL), r.get_corner(DR)).set_stroke(TINTA, 4)
        restante = min(max(self.duracion - self._t - 0.8, 2.5), 7.0)
        self.play(ShowPassingFlash(brillo_linea, time_width=0.4, run_time=1.2))
        self.wait(max(restante - 1.2, 0.5))
        esquinas.clear_updaters()
        self.play(*[FadeOut(m) for m in (formula, esquinas, velo, etiqueta, f)], run_time=0.8)
