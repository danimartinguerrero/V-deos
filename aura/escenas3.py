"""Tomas animadas del tercer edit (solo óptica) y textos cinéticos con transparencia."""

from escenas import *  # noqa: F401,F403
from escenas import _Cita  # noqa: F401

ROJO_L = "#FF3B30"
VERDE_L = "#39FF6A"
AZUL_L = "#4D7CFF"
CAUCHY = lambda lam_nm: 1.50 + 9000.0 / lam_nm ** 2   # vidrio con dispersión exagerada (para verla)
LAMS = [690, 620, 580, 540, 500, 460, 420]


def color_lam(l):
    return ESPECTRO[::-1][LAMS.index(l)] if l in LAMS else MARFIL


def refractar(d, nrm, n1, n2):
    """Ley de Snell vectorial. Devuelve (dirección, es_reflexión_total)."""
    cos_i = -np.dot(nrm, d)
    if cos_i < 0:
        nrm, cos_i = -nrm, -cos_i
    eta = n1 / n2
    k = 1 - eta ** 2 * (1 - cos_i ** 2)
    if k < 0:
        return d + 2 * cos_i * nrm, True
    return eta * d + (eta * cos_i - np.sqrt(k)) * nrm, False


def trazar(p, d, poligono, n_vidrio, rebotes=4, largo=12):
    """Traza un rayo 2D a través de un polígono convexo de índice n_vidrio."""
    pts = [p]
    dentro = False
    for _ in range(rebotes):
        mejor, cara = None, None
        for k in range(len(poligono)):
            a, b = poligono[k], poligono[(k + 1) % len(poligono)]
            e = b - a
            M = np.array([[d[0], -e[0]], [d[1], -e[1]]])
            if abs(np.linalg.det(M)) < 1e-9:
                continue
            t, u = np.linalg.solve(M, (a - p)[:2])
            if t > 1e-6 and 0 <= u <= 1 and (mejor is None or t < mejor):
                mejor, cara = t, k
        if mejor is None:
            break
        p = p + mejor * d
        pts.append(p)
        a, b = poligono[cara], poligono[(cara + 1) % len(poligono)]
        e = (b - a) / np.linalg.norm(b - a)
        nrm = np.array([e[1], -e[0], 0.0])
        n1, n2 = (n_vidrio, 1.0) if dentro else (1.0, n_vidrio)
        d, total = refractar(d, nrm, n1, n2)
        d = d / np.linalg.norm(d)
        if not total:
            dentro = not dentro
        if not dentro:
            break
    pts.append(p + largo * d)
    return pts


# ---------------------------------------------------------------------------
class SnellTIR(Toma):
    def construct(self):
        vidrio = Rectangle(width=9.5, height=8.5, stroke_width=0).set_fill("#9FC8FF", 0.06).move_to(DOWN * 4.25)
        interfaz = Line(LEFT * 4.8, RIGHT * 4.8, stroke_width=2, color=MARFIL).set_opacity(0.7)
        normal = DashedLine(DOWN * 4, UP * 4, stroke_width=1.5, color=MARFIL).set_opacity(0.35)
        th = ValueTracker(np.radians(8))
        n1 = 1.5
        crit = np.arcsin(1 / n1)

        def rayos():
            a = th.get_value()
            g = VGroup()
            origen = -6.5 * np.array([np.sin(a), np.cos(a), 0])
            g.add(Line(origen, ORIGIN, stroke_width=6, color=WHITE))
            g.add(punto_brillante(ORIGIN, WHITE, 0.07))
            if a < crit:
                t = np.arcsin(n1 * np.sin(a))
                ci, ct = np.cos(a), np.cos(t)
                R = ((n1 * ci - ct) / (n1 * ci + ct)) ** 2
                for k, c in enumerate(ESPECTRO):
                    tk = np.arcsin(min(n1 * (1 + 0.008 * (k - 3)) * np.sin(a), 0.999))
                    g.add(Line(ORIGIN, 7 * np.array([np.sin(tk), np.cos(tk), 0]), stroke_width=3, color=c).set_opacity(0.85 * (1 - R)))
            else:
                R = 1.0
            ref = Line(ORIGIN, 6.5 * np.array([np.sin(a), -np.cos(a), 0]), stroke_width=6, color=WHITE)
            g.add(ref.set_opacity(0.15 + 0.85 * R))
            return g

        self.add(vidrio, normal, interfaz, always_redraw(rayos))
        self.play(th.animate.set_value(crit - 0.02), run_time=2.4, rate_func=smooth)
        self.play(th.animate.set_value(np.radians(62)), run_time=1.2, rate_func=smooth)
        self.play(th.animate.set_value(np.radians(50)), run_time=1.4)


class FibraTIR(Toma):
    def construct(self):
        anch = 0.55
        def curva(y):
            return 1.4 * np.sin(y * 0.45)
        ys = np.linspace(-9, 9, 200)
        pared1 = VMobject().set_points_smoothly([[curva(y) - anch, y, 0] for y in ys]).set_stroke(MARFIL, 2, 0.6)
        pared2 = VMobject().set_points_smoothly([[curva(y) + anch, y, 0] for y in ys]).set_stroke(MARFIL, 2, 0.6)
        nucleo = VMobject().set_points_smoothly([[curva(y), y, 0] for y in ys]).set_stroke(AZUL_L, 40, 0.07)
        # zigzag en coordenadas locales (u a lo ancho, y a lo largo) y luego curvado
        pts, u, y, du = [], -anch, -9.0, 1
        while y < 9.5:
            pts.append([curva(y) + u, y, 0])
            y += 0.95
            u = anch if du > 0 else -anch
            du = -du
        ruta = VMobject().set_points_as_corners(pts)
        self.add(nucleo, pared1, pared2)
        haz = ruta.copy().set_stroke(VERDE_L, 4)
        self.play(Create(haz), run_time=2.2, rate_func=linear)
        fotones = VGroup(*[Dot(radius=0.07, color=WHITE) for _ in range(10)])
        fases = np.linspace(0, 1, 10, endpoint=False)
        reloj = [0.0]

        def mover(g, dt):
            reloj[0] += dt
            for k, d in enumerate(g):
                d.move_to(ruta.point_from_proportion((fases[k] + 0.3 * reloj[0]) % 1))

        fotones.add_updater(mover)
        mover(fotones, 0)
        self.add(fotones, punto_brillante([curva(9), 8.9, 0], VERDE_L, 0.25))
        self.esperar_resto()


class Fermat(Toma):
    def construct(self):
        A, B = np.array([-3.0, 5.0, 0]), np.array([3.2, -5.2, 0])
        n1, n2 = 1.0, 1.6
        agua = Rectangle(width=9.5, height=8.0, stroke_width=0).set_fill(AZUL_L, 0.08).move_to(DOWN * 4.0)
        interfaz = Line(LEFT * 4.8, RIGHT * 4.8, stroke_width=2, color=MARFIL).set_opacity(0.6)
        xs = np.linspace(-3.5, 3.8, 34)
        T = lambda x: n1 * np.hypot(x - A[0], A[1]) + n2 * np.hypot(B[0] - x, B[1])
        tiempos = np.array([T(x) for x in xs])
        tmin = xs[np.argmin(tiempos)]
        norm = (tiempos - tiempos.min()) / np.ptp(tiempos)
        caminos = VGroup(*[VMobject().set_points_as_corners([A, [x, 0, 0], B]).set_stroke(
            interpolate_color(ManimColor(GRAV), ManimColor(CUANT), v), 1.6, 0.25 + 0.4 * (1 - v)) for x, v in zip(xs, norm)])
        mejor = VMobject().set_points_as_corners([A, [tmin, 0, 0], B]).set_stroke(WHITE, 6)
        self.add(agua, interfaz, punto_brillante(A), punto_brillante(B))
        self.play(LaggedStart(*[Create(c) for c in caminos], lag_ratio=0.04), run_time=2.2)
        self.play(Create(mejor), caminos.animate.set_stroke(opacity=0.12), run_time=1.0)
        self.play(Flash([tmin, 0, 0], color=WHITE, flash_radius=0.5), run_time=0.6)
        self.esperar_resto()


class Polarizacion(Toma):
    def construct(self):
        fase = ValueTracker(0.0)
        t = ValueTracker(0.0)
        u = np.array([0.0, 1.0, 0])

        def onda():
            ph = fase.get_value()
            s = np.linspace(-7.5, 4.5, 300)
            g = VGroup(Line(u * -8, u * 5, stroke_width=1.5, color=MARFIL).set_opacity(0.4))
            puntas = []
            for x in s:
                arg = 2.2 * x - 6 * t.get_value()
                ex, ey = np.cos(arg), np.cos(arg + ph)
                puntas.append(u * x + np.array([1.6 * ex, 0.55 * ey, 0]) + np.array([0, 0.5 * ey, 0]))
            g.add(VMobject().set_points_smoothly(puntas).set_stroke([CUANT, ELEC, COMP], 4))
            for k in range(0, 300, 10):
                g.add(Line(u * s[k], puntas[k], stroke_width=1.2, color=ELEC).set_opacity(0.35))
            # vista de frente (lo que ve un detector)
            c = UP * 6.4
            arg0 = -6 * t.get_value()
            el = VMobject().set_points_smoothly([c + np.array([1.2 * np.cos(a), 1.2 * np.cos(a + ph) * 0.9, 0])
                                                 for a in np.linspace(0, TAU, 80)]).set_stroke(MARFIL, 1.5, 0.6)
            g.add(el, Arrow(c, c + np.array([1.2 * np.cos(arg0), 1.08 * np.cos(arg0 + ph), 0]), buff=0, stroke_width=5, color=WHITE))
            return g

        self.add(always_redraw(onda))
        self.play(t.animate.set_value(1.6), run_time=1.6, rate_func=linear)
        self.play(t.animate.set_value(3.2), fase.animate.set_value(PI / 2), run_time=1.8, rate_func=linear)
        self.play(t.animate.set_value(4.6), fase.animate.set_value(PI / 4), run_time=1.6, rate_func=linear)


class Malus(Toma):
    def construct(self):
        th = ValueTracker(0)

        def polarizador(c, ang, col):
            g = VGroup(Circle(radius=1.5).move_to(c).set_stroke(col, 3).set_fill(col, 0.05))
            for k in np.linspace(-1.3, 1.3, 11):
                L = np.sqrt(max(1.5 ** 2 - k ** 2, 0)) * 0.95
                l = Line([k, -L, 0], [k, L, 0], stroke_width=1.5, color=col).set_opacity(0.6)
                g.add(l.rotate(ang, about_point=ORIGIN).shift(c))
            return g

        c1, c2 = UP * 2.6, DOWN * 1.2

        def escena():
            a = th.get_value()
            I = np.cos(a) ** 2
            g = VGroup(
                Line(UP * 7, c1, stroke_width=10, color=WHITE).set_opacity(0.9),
                Line(c1, c2, stroke_width=10, color=WHITE).set_opacity(0.55),
                Line(c2, DOWN * 4.6, stroke_width=10, color=WHITE).set_opacity(0.05 + 0.6 * I),
                polarizador(c1, 0, MARFIL), polarizador(c2, a, ELEC),
            )
            return g

        ejes = Axes(x_range=[0, PI, PI / 2], y_range=[0, 1, 1], x_length=6, y_length=1.6,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.4, "include_ticks": False}).move_to(DOWN * 6.2)
        curva = ejes.plot(lambda a: np.cos(a) ** 2, x_range=[0, PI], stroke_width=3, color=ELEC)
        punto = always_redraw(lambda: punto_brillante(ejes.c2p(th.get_value() % PI, np.cos(th.get_value()) ** 2), WHITE, 0.07))
        self.add(always_redraw(escena), ejes, curva, punto)
        self.play(th.animate.set_value(PI), run_time=self.duracion, rate_func=smooth)


class PrismaGiratorio(Toma):
    def construct(self):
        rot = ValueTracker(-0.35)
        L = 4.0

        def escena():
            r = rot.get_value()
            P = [np.array([L / np.sqrt(3) * np.cos(a + r), L / np.sqrt(3) * np.sin(a + r), 0]) + UP * 0.6
                 for a in (PI / 2, PI / 2 + TAU / 3, PI / 2 + 2 * TAU / 3)]
            g = VGroup(Polygon(*P, stroke_width=3, color=MARFIL).set_fill(WHITE, 0.05))
            p0 = np.array([-5.5, -1.2, 0])
            d0 = np.array([1.0, 0.32, 0]); d0 /= np.linalg.norm(d0)
            primero = trazar(p0, d0, P, CAUCHY(550))
            g.add(Line(p0, primero[1], stroke_width=7, color=WHITE))
            for lam in LAMS:
                pts = trazar(p0, d0, P, CAUCHY(lam))
                if len(pts) > 2:
                    tramo = VMobject().set_points_as_corners(pts[1:]).set_stroke(color_lam(lam), 4.5, 0.9)
                    g.add(tramo)
            return g

        self.add(always_redraw(escena))
        self.play(rot.animate.set_value(0.35), run_time=self.duracion, rate_func=there_and_back)


class ModeLocking(Toma):
    def construct(self):
        N = ValueTracker(1)
        ejes_c = UP * 1.6

        def tren():
            n = max(int(N.get_value()), 1)
            t = np.linspace(-1.5, 1.5, 900)
            k = np.arange(n) - (n - 1) / 2
            campo = np.cos(np.outer(t, 40 + k * 2 * np.pi)).sum(1)
            env = np.abs(np.exp(1j * np.outer(t, k * 2 * np.pi)).sum(1)) ** 2
            env = env / env.max()
            campo = campo / max(n, 1)
            g = VGroup()
            g.add(VMobject().set_points_smoothly([ejes_c + [4.2 * x / 1.5, 2.2 * y * np.sqrt(e), 0] for x, y, e in zip(t[::2], campo[::2], env[::2])])
                  .set_stroke(ROJO_L, 2, 0.8))
            g.add(VMobject().set_points_smoothly([ejes_c + [4.2 * x / 1.5, 2.6 * e, 0] for x, e in zip(t[::3], env[::3])]).set_stroke(WHITE, 4))
            base = DOWN * 4.3
            for kk in k:
                h = 2.2 * np.exp(-(kk / max(n / 2.2, 1)) ** 2)
                g.add(Line(base + RIGHT * kk * min(7.4 / max(n, 1), 0.6), base + RIGHT * kk * min(7.4 / max(n, 1), 0.6) + UP * h,
                           stroke_width=3, color=ROJO_L))
            return g

        self.add(always_redraw(tren))
        self.play(N.animate.set_value(36), run_time=self.duracion - 0.6, rate_func=rush_into)
        self.wait(0.6)


class PulsoChirp(Toma):
    def construct(self):
        t = ValueTracker(0)

        def pulso():
            tt = t.get_value()
            x = np.linspace(-4.6, 4.6, 700)
            c = -4 + 8 * tt / 4
            ancho = 1.6 - 1.25 * min(tt / 3, 1)
            chirp = 2.5 * (1 - min(tt / 3, 1))
            env = np.exp(-((x - c) / ancho) ** 2)
            campo = env * np.cos(14 * (x - c) + chirp * (x - c) ** 2)
            cols = [interpolate_color(ManimColor(ROJO_L), ManimColor(AZUL_L), (np.tanh(chirp * (xi - c)) + 1) / 2) for xi in x]
            g = VGroup()
            for k in range(0, 699, 3):
                g.add(Line([x[k] * 0.9, 2.6 * campo[k], 0], [x[k + 3] * 0.9 if k + 3 < 700 else x[-1], 2.6 * campo[min(k + 3, 699)], 0],
                           stroke_width=3.5, color=cols[k]))
            g.add(VMobject().set_points_smoothly([[xi * 0.9, 2.6 * e, 0] for xi, e in zip(x[::5], env[::5])]).set_stroke(WHITE, 1.5, 0.5))
            g.add(VMobject().set_points_smoothly([[xi * 0.9, -2.6 * e, 0] for xi, e in zip(x[::5], env[::5])]).set_stroke(WHITE, 1.5, 0.5))
            return g

        self.add(always_redraw(pulso))
        self.play(t.animate.set_value(4), run_time=self.duracion, rate_func=linear)


class CavidadLaser(Toma):
    def construct(self):
        arriba, abajo = 4.2, -4.2
        esp1 = Line([-2.4, abajo, 0], [2.4, abajo, 0], stroke_width=8, color=MARFIL)
        esp2 = Line([-2.4, arriba, 0], [2.4, arriba, 0], stroke_width=8, color=MARFIL).set_opacity(0.55)
        medio = Rectangle(width=2.4, height=4.0).set_stroke(ROJO_L, 1.5, 0.6).set_fill(ROJO_L, 0.08)
        A = ValueTracker(0.05)
        t = ValueTracker(0)

        def onda():
            a = A.get_value()
            y = np.linspace(abajo, arriba, 300)
            g = VGroup()
            for sgn in (1, -1):
                g.add(VMobject().set_points_smoothly([[sgn * a * 1.8 * np.sin(3.5 * (yy - abajo)) * np.cos(8 * t.get_value()), yy, 0] for yy in y])
                      .set_stroke(ROJO_L, 3, 0.8))
            haz = Line([0, arriba, 0], [0, 9, 0], stroke_width=4 + 26 * a, color=ROJO_L).set_opacity(min(a * 1.3, 1))
            g.add(haz, Line([0, arriba, 0], [0, 9, 0], stroke_width=2 + 6 * a, color=WHITE).set_opacity(min(a * 1.5, 1)))
            return g

        self.add(medio, esp1, esp2, always_redraw(onda))
        self.play(A.animate.set_value(1.0), t.animate.set_value(5), run_time=self.duracion, rate_func=rush_into)


# ---------------------------------------------------------------------------
# Texto cinético (transparente): sans fina, minúsculas, alineado a la izquierda
# ---------------------------------------------------------------------------
class _Frase(Scene):
    lineas = [""]
    etiqueta = ""
    duracion = 3.2
    grande = False

    def construct(self):
        tam = 170 if self.grande else 84
        filas = VGroup(*[Text(l, font="Inter Display", weight=THIN, font_size=tam, color=MARFIL) for l in self.lineas])
        filas.arrange(DOWN, aligned_edge=LEFT, buff=0.28)
        if filas.width > 7.6:
            filas.width = 7.6
        filas.to_edge(LEFT, buff=0.75).set_y(-2.6 if not self.grande else 0.4)
        raya = Line(ORIGIN, RIGHT * min(filas.width, 5.5), stroke_width=2).next_to(filas, DOWN, buff=0.4, aligned_edge=LEFT)
        raya.set_color(ESPECTRO)
        tag = Text(self.etiqueta, font="JetBrains Mono", font_size=26, color=MARFIL).set_opacity(0.65)
        tag.next_to(filas, UP, buff=0.4, aligned_edge=LEFT)
        palabras = [w for f in filas for w in f]
        self.play(FadeIn(tag, shift=RIGHT * 0.2), Create(raya),
                  LaggedStart(*[FadeIn(p, shift=RIGHT * 0.12) for p in palabras], lag_ratio=0.035), run_time=1.0)
        self.wait(max(self.duracion - 1.5, 0.3))
        self.play(FadeOut(VGroup(filas, raya, tag), shift=UP * 0.15), run_time=0.5)


class FraseLuz(_Frase):
    lineas = ["light"]
    etiqueta = "c = 299 792 458 m/s"
    grande = True


class FraseCamino(_Frase):
    lineas = ["it always finds", "the fastest way."]
    etiqueta = "δ ∫ n ds = 0"


class FraseColores(_Frase):
    lineas = ["every color was", "hiding in the white."]
    etiqueta = "380 — 750 nm"


class FraseInstante(_Frase):
    lineas = ["a trillionth of a second,", "frozen."]
    etiqueta = "Δt ≈ 10⁻¹⁵ s"


class FraseFinal(_Frase):
    lineas = ["everything we know,", "we know by light."]
    etiqueta = "∎"
    duracion = 4.0


TOMAS = ["SnellTIR", "FibraTIR", "Fermat", "Polarizacion", "Malus", "PrismaGiratorio", "ModeLocking", "PulsoChirp",
         "CavidadLaser"]
CITAS = ["FraseLuz", "FraseCamino", "FraseColores", "FraseInstante", "FraseFinal"]
