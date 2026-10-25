"""Tomas animadas del quinto edit (electrostática) y tarjetas-ecuación con transparencia."""

from escenas import *  # noqa: F401,F403


def suave(t):
    return t * t * (3 - 2 * t)

CIAN = "#40C8FF"
MAG = "#FF5CA0"
ORO = "#FFC266"
VERDE = "#7CFFCB"


def carga(p, q, r=0.22):
    c = MAG if q > 0 else CIAN
    g = VGroup(punto_brillante(p, c, r * 0.6))
    s = Text("+" if q > 0 else "−", font="Inter", weight=BOLD, font_size=30, color="#000000").move_to(p)
    return VGroup(g, s)


def flecha(a, b, color, ancho=5):
    return Arrow(a, b, buff=0, stroke_width=ancho, color=color, max_tip_length_to_length_ratio=0.2,
                 max_stroke_width_to_length_ratio=20)


# ---------------------------------------------------------------------------
# Tema 1
# ---------------------------------------------------------------------------
class Coulomb(Toma):
    def construct(self):
        r = ValueTracker(3.6)
        y0 = UP * 2.6
        ejes = Axes(x_range=[0.8, 4.2, 1], y_range=[0, 1.6, 0.5], x_length=7.2, y_length=3.4,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.4, "include_ticks": False}).move_to(DOWN * 3.0)
        curva = ejes.plot(lambda x: 1 / x ** 2, x_range=[0.8, 4.2, 0.01], stroke_width=4, color=ORO)

        def escena():
            d = r.get_value()
            a, b = y0 + LEFT * d / 2, y0 + RIGHT * d / 2
            F = 1.0 / d ** 2
            g = VGroup(carga(a, 1), carga(b, 1), flecha(a, a + LEFT * (0.4 + 2.2 * F), MAG), flecha(b, b + RIGHT * (0.4 + 2.2 * F), MAG),
                       DashedLine(a + DOWN * 0.6, b + DOWN * 0.6, stroke_width=1.5, color=MARFIL).set_opacity(0.5),
                       eq("r", 36).move_to(y0 + DOWN * 0.95), punto_brillante(ejes.c2p(d, 1 / d ** 2), WHITE, 0.07))
            return g

        self.add(ejes, curva, always_redraw(escena))
        lab = eq(r"\mathbf F=\frac{1}{4\pi\varepsilon_0}\frac{q_1q_2}{r^2}\,\hat{\mathbf u}_r", 54).move_to(DOWN * 6.0)
        self.play(r.animate.set_value(1.0), FadeIn(lab), run_time=2.6, rate_func=smooth)
        self.play(r.animate.set_value(2.4), run_time=self.duracion - 2.6, rate_func=smooth)


class DeltaDirac(Toma):
    def construct(self):
        c = UP * 2.2
        flechas = VGroup()
        for rr in (0.9, 1.6, 2.4, 3.3):
            for a in np.linspace(0, TAU, 16, endpoint=False) + rr:
                u = np.array([np.cos(a), np.sin(a), 0])
                L = 0.55 / rr ** 1.2
                flechas.add(flecha(c + u * rr, c + u * (rr + L), CIAN, 3).set_opacity(0.8))
        self.add(flechas, punto_brillante(c, MAG, 0.14))
        R = ValueTracker(0.6)
        esfera = always_redraw(lambda: DashedVMobject(Circle(radius=R.get_value()).move_to(c), num_dashes=40).set_stroke(ORO, 3))
        lect = eq(r"\oint\frac{\hat{\mathbf u}_R}{R^2}\cdot d\mathbf S=4\pi", 48, ORO).move_to(DOWN * 1.9)
        self.add(esfera)
        self.play(R.animate.set_value(3.6), FadeIn(lect), run_time=2.0, rate_func=there_and_back)
        ejes = Axes(x_range=[-2, 2, 1], y_range=[0, 4, 1], x_length=7, y_length=2.6,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.4, "include_ticks": False}).move_to(DOWN * 4.3)
        eps = ValueTracker(0.8)
        pico = always_redraw(lambda: ejes.plot(lambda x: np.exp(-x * x / (2 * eps.get_value() ** 2)) / (eps.get_value() * np.sqrt(TAU)),
                                               x_range=[-2, 2, 0.005], stroke_width=4, color=MAG))
        d = eq(r"\nabla\cdot\frac{\hat{\mathbf u}_R}{R^2}=4\pi\,\delta^3(\mathbf R)", 48).move_to(DOWN * 6.2)
        self.add(ejes, pico)
        self.play(eps.animate.set_value(0.1), FadeIn(d), run_time=self.duracion - 2.0, rate_func=smooth)


class Distribuciones(Toma):
    def construct(self):
        a = ValueTracker(0.0)   # 0: anillo, 1: disco, >1: disco que crece hacia plano
        c = UP * 2.6
        ejes = Axes(x_range=[0, 4, 1], y_range=[0, 1.1, 0.5], x_length=7.2, y_length=3.4,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.4, "include_ticks": False}).move_to(DOWN * 3.0)

        def ez(z, s):
            if s < 1:
                anillo = 3 * np.sqrt(3) / 2 * z / (1 + z * z) ** 1.5
                disco = 1 - z / np.sqrt(z * z + 1)
                return (1 - s) * anillo + s * disco
            R = 1 + (s - 1) * 8
            return 1 - z / np.sqrt(z * z + R * R)

        def escena():
            s = a.get_value()
            R = 1.6 * (1 + max(s - 1, 0) * 1.6)
            g = VGroup()
            if s < 1:
                for k in np.linspace(0, 1, 8):
                    rr = R * (1 - s * k)
                    g.add(Ellipse(width=2 * rr, height=0.6 * rr).move_to(c).set_stroke(MAG, 3 if k == 0 else 1.5, 1 - 0.1 * k * 8 * (1 - s)))
            else:
                g.add(Ellipse(width=min(2 * R, 9.5), height=0.6 * min(R, 4.75)).move_to(c).set_stroke(MAG, 3).set_fill(MAG, 0.18))
            g.add(Line(c, c + UP * 3.0, stroke_width=1.5, color=MARFIL).set_opacity(0.5))
            for z in (0.5, 1.2, 2.0, 2.8):
                v = ez(z / 1.4, s)
                g.add(flecha(c + UP * z, c + UP * (z + 0.15 + 0.9 * v), ORO, 4))
            g.add(ejes.plot(lambda z: ez(z, s), x_range=[0.001, 4, 0.01], stroke_width=4, color=ORO))
            nombre = ("anillo" if s < 0.5 else ("disco" if s < 1.6 else "plano"))
            g.add(Text(nombre, font="Inter", weight=LIGHT, font_size=30, color=MARFIL).move_to(ejes.c2p(3.2, 0.9)))
            return g

        self.add(ejes, always_redraw(escena))
        lab = eq(r"E_z^{\rm disco}=\frac{\sigma}{2\varepsilon_0}\Big(1-\frac{z}{\sqrt{z^2+a^2}}\Big)", 48).move_to(DOWN * 6.0)
        self.play(a.animate.set_value(1.0), FadeIn(lab), run_time=2.2, rate_func=smooth)
        self.play(a.animate.set_value(2.0), run_time=self.duracion - 2.2, rate_func=smooth)


class GaussSimetrias(Toma):
    def construct(self):
        r = ValueTracker(0.2)
        c = UP * 2.4
        Rs = 1.2
        ejes = Axes(x_range=[0, 4, 1], y_range=[0, 1.15, 0.5], x_length=7.2, y_length=3.2,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.4, "include_ticks": False}).move_to(DOWN * 3.2)
        E = lambda x: x / Rs if x < Rs else (Rs / x) ** 2
        curva = ejes.plot(E, x_range=[0.01, 4, 0.01], stroke_width=4, color=ORO)
        rng = np.random.default_rng(1)
        pts = VGroup(*[Dot(c + np.array([*(np.sqrt(rng.uniform()) * Rs * np.array([np.cos(a), np.sin(a)])), 0]), radius=0.04, color=MAG)
                       for a in rng.uniform(0, TAU, 80)])
        esfera = Circle(radius=Rs).move_to(c).set_stroke(MAG, 2).set_fill(MAG, 0.12)

        def gauss():
            rr = r.get_value()
            g = VGroup(DashedVMobject(Circle(radius=rr).move_to(c), num_dashes=36).set_stroke(ORO, 3))
            m = E(rr)
            for a in np.linspace(0, TAU, 12, endpoint=False):
                u = np.array([np.cos(a), np.sin(a), 0])
                g.add(flecha(c + u * rr, c + u * (rr + 0.2 + 0.8 * m), CIAN, 3))
            g.add(punto_brillante(ejes.c2p(rr, m), WHITE, 0.07))
            return g

        self.add(esfera, pts, ejes, curva, always_redraw(gauss))
        lab = eq(r"\oint\mathbf E\cdot d\mathbf S=\frac{Q_{\rm int}}{\varepsilon_0}", 58).move_to(DOWN * 6.0)
        self.play(r.animate.set_value(3.3), FadeIn(lab), run_time=self.duracion, rate_func=smooth)


class Contorno(Toma):
    def construct(self):
        sig = ValueTracker(0.0)
        interfaz = Line(LEFT * 4.6, RIGHT * 4.6, stroke_width=3, color=MAG).shift(UP * 0.4)
        caja = Rectangle(width=1.4, height=1.0).move_to(UP * 0.4 + LEFT * 2.2).set_stroke(ORO, 2)
        lazo = Rectangle(width=1.6, height=0.8).move_to(UP * 0.4 + RIGHT * 2.2).set_stroke(VERDE, 2)
        En1, Et = 0.9, 1.0

        def campos():
            s = sig.get_value()
            g = VGroup()
            for x in np.linspace(-3.6, 3.6, 6):
                for lado, En in ((-1, En1), (1, En1 + s)):
                    base = np.array([x, 0.4 + lado * 1.7, 0])
                    v = np.array([Et, En, 0]) * 1.1
                    g.add(flecha(base - v / 2, base + v / 2, CIAN if lado < 0 else ORO, 4))
            return g

        self.add(always_redraw(campos), interfaz, caja, lazo)
        marcas = VGroup(*[Text("+", font="Inter", font_size=24, color=MAG).move_to([x, 0.4, 0]) for x in np.linspace(-4.2, 4.2, 15)])
        l1 = eq(r"E_{2n}-E_{1n}=\frac{\sigma}{\varepsilon_0}", 50, ORO).move_to(DOWN * 3.6)
        l2 = eq(r"E_{2t}=E_{1t},\qquad \phi_2=\phi_1", 50, VERDE).move_to(DOWN * 4.9)
        self.play(sig.animate.set_value(1.4), FadeIn(marcas), FadeIn(l1), run_time=2.6, rate_func=smooth)
        self.play(FadeIn(l2), sig.animate.set_value(0.6), run_time=self.duracion - 2.6)


class RelievePotencial(Toma):
    def construct(self):
        phi = ValueTracker(0.3)
        el = 0.6
        c = UP * 0.2

        def proy(x, y, z):
            a = phi.get_value()
            X = x * np.cos(a) - y * np.sin(a)
            Yd = x * np.sin(a) + y * np.cos(a)
            return c + 1.25 * np.array([X, z * np.cos(el) + Yd * np.sin(el), 0])

        def V(x, y):
            v = 1 / np.sqrt((x - 0.9) ** 2 + y * y + 0.12) - 1 / np.sqrt((x + 0.9) ** 2 + y * y + 0.12)
            return np.clip(v, -2.2, 2.2) * 0.9

        def malla():
            g = VGroup()
            for k in np.linspace(-3, 3, 25):
                for eje in (0, 1):
                    pts = [proy(k, s, V(k, s)) if eje == 0 else proy(s, k, V(s, k)) for s in np.linspace(-3, 3, 70)]
                    vals = [V(k, s) if eje == 0 else V(s, k) for s in np.linspace(-3, 3, 70)]
                    m = VMobject().set_points_smoothly(pts)
                    col = MAG if np.mean(vals) > 0.05 else (CIAN if np.mean(vals) < -0.05 else MARFIL)
                    g.add(m.set_stroke(col, 1.4, 0.55))
            return g

        self.add(always_redraw(malla))
        lab = eq(r"\nabla^2\phi=-\frac{\rho}{\varepsilon_0}", 60).move_to(DOWN * 5.4)
        self.play(phi.animate.set_value(0.3 + 2.4), FadeIn(lab), run_time=self.duracion, rate_func=linear)


class Teoremas(Toma):
    def construct(self):
        fuentes = [(1.0, np.array([-0.8, 1.6, 0])), (0.7, np.array([0.9, 2.4, 0])), (-0.6, np.array([0.4, 0.6, 0]))]

        def F(p):
            v = np.zeros(3)
            for q, s in fuentes:
                d = p - s
                v += q * d / (np.linalg.norm(d) ** 3 + 0.05)
            return v

        campo = VGroup()
        for x in np.linspace(-4, 4, 13):
            for y in np.linspace(-1.6, 5.2, 13):
                p = np.array([x, y, 0])
                v = F(p)
                m = np.linalg.norm(v)
                campo.add(flecha(p, p + v / m * 0.42, interpolate_color(ManimColor(CIAN), ManimColor(MAG), min(m / 2, 1)), 2.5).set_opacity(0.75))
        self.add(campo)
        for q, s in fuentes:
            self.add(punto_brillante(s, MAG if q > 0 else CIAN, 0.12))
        curva = VMobject().set_points_smoothly([np.array([0.05 + 2.4 * np.cos(a) + 0.35 * np.cos(3 * a), 1.6 + 1.9 * np.sin(a), 0])
                                                for a in np.linspace(0, TAU, 80)]).set_stroke(ORO, 4)
        self.play(Create(curva), run_time=1.2)
        lab = eq(r"\oint_S\mathbf F\cdot d\mathbf S=\int_V\nabla\cdot\mathbf F\,dV", 50).move_to(DOWN * 3.7)
        lab2 = eq(r"\oint_C\mathbf E\cdot d\mathbf l=\int_S(\nabla\times\mathbf E)\cdot d\mathbf S=0", 44, VERDE).move_to(DOWN * 5.2)
        self.play(FadeIn(lab, shift=UP * 0.2), run_time=0.7)
        punto = Dot(radius=0.1, color=WHITE)
        self.play(MoveAlongPath(punto, curva), FadeIn(lab2), run_time=self.duracion - 1.9, rate_func=linear)


class FlujoGauss(Toma):
    """Una superficie cerrada se pasea entre cargas: el flujo saliente es la carga encerrada / ε0."""

    def construct(self):
        cargas = [(1, np.array([-1.6, 2.6, 0])), (1, np.array([1.4, 1.2, 0])), (-1, np.array([-0.6, -0.4, 0])),
                  (1, np.array([1.2, -2.0, 0])), (-1, np.array([-1.5, -2.6, 0]))]

        def E(p):
            v = np.zeros(3)
            for q, s in cargas:
                d = p - s
                v += q * d / (np.linalg.norm(d) ** 3 + 0.03)
            return v

        for q, s in cargas:
            self.add(carga(s, q))
        c = ValueTracker(0.0)

        def centro(u):
            return np.array([1.6 * np.sin(u * TAU), 2.8 * np.cos(u * TAU * 0.5) - 0.2, 0])

        def escena():
            p0 = centro(c.get_value())
            R = 1.15
            g = VGroup(Circle(radius=R).move_to(p0).set_stroke(ORO, 3).set_fill(ORO, 0.05))
            Q = 0
            for q, s in cargas:
                if np.linalg.norm(s - p0) < R:
                    Q += q
            for a in np.linspace(0, TAU, 20, endpoint=False):
                nrm = np.array([np.cos(a), np.sin(a), 0])
                p = p0 + nrm * R
                v = E(p)
                fn = np.dot(v, nrm)
                col = MAG if fn > 0 else CIAN
                L = np.clip(abs(fn) * 0.6, 0.08, 0.7)
                g.add(flecha(p, p + nrm * L * np.sign(fn), col, 3))
            g.add(eq(r"\Phi_E=\frac{%+d\,q}{\varepsilon_0}" % Q if Q else r"\Phi_E=0", 54,
                     MAG if Q > 0 else (CIAN if Q < 0 else MARFIL)).move_to(DOWN * 5.6))
            return g

        self.add(always_redraw(escena))
        self.play(c.animate.set_value(1.0), run_time=self.duracion, rate_func=linear)


class DivergenciaLocal(Toma):
    """∇·E como flujo por unidad de volumen: un cubito que se encoge alrededor de un punto."""

    def construct(self):
        fuente = np.array([0.0, 1.0, 0])

        def E(p):
            d = p - fuente
            return 0.9 * d / (np.linalg.norm(d) ** 2 + 0.6) + np.array([0.35, 0.15, 0])

        campo = VGroup()
        for x in np.linspace(-4, 4, 12):
            for y in np.linspace(-2.6, 4.8, 15):
                p = np.array([x, y, 0])
                v = E(p)
                campo.add(flecha(p - v * 0.3, p + v * 0.3, interpolate_color(ManimColor(CIAN), ManimColor(MAG), min(np.linalg.norm(v), 1)), 3.5).set_opacity(0.85))
        self.add(campo)
        lado = ValueTracker(2.4)

        def caja():
            l = lado.get_value()
            g = VGroup(Square(l).move_to(fuente).set_stroke(ORO, 3).set_fill(ORO, 0.06))
            for nrm in (RIGHT, LEFT, UP, DOWN):
                for t in (-0.25, 0.25):
                    p = fuente + nrm * l / 2 + np.array([nrm[1], nrm[0], 0]) * t * l
                    fn = np.dot(E(p), nrm)
                    g.add(flecha(p, p + nrm * np.clip(fn, -0.6, 0.6) * 1.2, MAG if fn > 0 else CIAN, 4))
            return g

        self.add(always_redraw(caja), punto_brillante(fuente, MAG, 0.08))
        lab = eq(r"\nabla\cdot\mathbf E=\lim_{\Delta V\to0}\frac{1}{\Delta V}\oint\mathbf E\cdot d\mathbf S=\frac{\rho}{\varepsilon_0}", 44)
        lab.move_to(DOWN * 4.6)
        self.play(FadeIn(lab, shift=UP * 0.2), run_time=0.6)
        self.play(lado.animate.set_value(0.45), run_time=self.duracion - 0.6, rate_func=smooth)


# ---------------------------------------------------------------------------
# Tema 2
# ---------------------------------------------------------------------------
class Legendre(Toma):
    def construct(self):
        P = [lambda x: np.ones_like(x), lambda x: x, lambda x: 0.5 * (3 * x * x - 1), lambda x: 0.5 * (5 * x ** 3 - 3 * x)]
        nombres = ["monopolo", "dipolo", "cuadrupolo", "octupolo"]
        c = UP * 1.4
        l = ValueTracker(0.0)

        def forma():
            v = l.get_value()
            k = min(int(v), 2)
            u = v - k if v < 3 else 1.0
            u = suave(min(max(u, 0), 1))
            th = np.linspace(0, TAU, 360)
            f = (1 - u) * P[k](np.cos(th)) + u * P[min(k + 1, 3)](np.cos(th))
            g = VGroup()
            for sg, col in ((1, MAG), (-1, CIAN)):
                rr = np.clip(sg * f, 0, None) * 2.6
                pts = [c + rr[j] * np.array([np.sin(th[j]), np.cos(th[j]), 0]) for j in range(360)]
                m = VMobject().set_points_smoothly(pts).set_stroke(col, 4).set_fill(col, 0.15)
                g.add(m)
            idx = min(int(round(v)), 3)
            g.add(Text(nombres[idx], font="Inter", weight=LIGHT, font_size=34, color=MARFIL).move_to(DOWN * 2.4))
            g.add(eq(r"\ell=%d" % idx, 40, ORO).move_to(DOWN * 3.2))
            return g

        self.add(always_redraw(forma))
        lab = eq(r"\frac1R=\sum_{\ell=0}^\infty\frac{r'^\ell}{r^{\ell+1}}P_\ell(\cos\theta')", 50).move_to(DOWN * 5.0)
        self.play(l.animate.set_value(3.0), FadeIn(lab), run_time=self.duracion, rate_func=linear)


class Polarizacion(Toma):
    def construct(self):
        rng = np.random.default_rng(4)
        losa = Rectangle(width=6.0, height=4.6).move_to(UP * 0.9).set_stroke(MARFIL, 2).set_fill(MARFIL, 0.04)
        ang0 = rng.uniform(0, TAU, 63)
        s = ValueTracker(0)
        pos = [np.array([x, y, 0]) for x in np.linspace(-2.5, 2.5, 7) for y in np.linspace(-1.2, 3.0, 9)][:63]

        def dipolos():
            u = s.get_value()
            g = VGroup()
            for p, a0 in zip(pos, ang0):
                a = (1 - u) * a0 + u * (PI / 2)
                d = 0.22 * np.array([np.cos(a), np.sin(a), 0])
                g.add(Line(p - d, p + d, stroke_width=4).set_color([CIAN, MAG]), Dot(p + d, radius=0.04, color=MAG), Dot(p - d, radius=0.04, color=CIAN))
            for x in np.linspace(-2.8, 2.8, 11):
                g.add(Text("+", font="Inter", font_size=26, color=MAG).move_to([x, 3.4, 0]).set_opacity(u))
                g.add(Text("−", font="Inter", font_size=26, color=CIAN).move_to([x, -1.6, 0]).set_opacity(u))
            return g

        campo = VGroup(*[flecha([x, -3.0, 0], [x, 4.8, 0], ORO, 2).set_opacity(0.35) for x in (-4.0, -3.4, 3.4, 4.0)])
        self.add(campo, losa, always_redraw(dipolos))
        lab = VGroup(eq(r"\sigma_b=\mathbf P\cdot\hat{\mathbf n}", 50, MAG), eq(r"\rho_b=-\nabla\cdot\mathbf P", 50, CIAN)).arrange(RIGHT, buff=0.8)
        lab.move_to(DOWN * 4.6)
        self.play(s.animate.set_value(1), FadeIn(lab), run_time=self.duracion * 0.7, rate_func=smooth)
        self.esperar_resto()


# ---------------------------------------------------------------------------
# Tema 3
# ---------------------------------------------------------------------------
class Condensadores(Toma):
    def construct(self):
        c = UP * 1.6
        fase = ValueTracker(0)

        def forma():
            v = fase.get_value()
            g = VGroup()
            if v < 1:
                u = suave(v)
                for y, col in ((0.8, MAG), (-0.8, CIAN)):
                    g.add(Line(c + [-2.4, y, 0], c + [2.4, y, 0], stroke_width=8, color=col))
                for x in np.linspace(-2.0, 2.0, 9):
                    g.add(flecha(c + [x, 0.7, 0], c + [x, -0.7, 0], ORO, 3).set_opacity(0.8))
                g.set_opacity(1 - u)
                g.add(Circle(radius=0.5).move_to(c).set_stroke(MAG, 7, u), Circle(radius=2.2).move_to(c).set_stroke(CIAN, 7, u))
            else:
                u = suave(min(v - 1, 1))
                g.add(Circle(radius=0.5 + 0.4 * u).move_to(c).set_stroke(MAG, 7).set_fill(MAG, 0.12 * u),
                      Circle(radius=2.2).move_to(c).set_stroke(CIAN, 7))
                for a in np.linspace(0, TAU, 16, endpoint=False):
                    uu = np.array([np.cos(a), np.sin(a), 0])
                    g.add(flecha(c + uu * (0.65 + 0.4 * u), c + uu * 2.05, ORO, 3).set_opacity(0.8))
            return g

        txt = [eq(r"C=\frac{\varepsilon_0S}{d}", 64), eq(r"C=\frac{2\pi\varepsilon_0L}{\ln(b/a)}", 64), eq(r"C=\frac{4\pi\varepsilon_0ab}{b-a}", 64)]
        for t in txt:
            t.move_to(DOWN * 4.4)
        self.add(always_redraw(forma), txt[0])
        self.wait(1.2)
        self.play(fase.animate.set_value(1), ReplacementTransform(txt[0], txt[1]), run_time=1.3)
        self.wait(0.6)
        self.play(fase.animate.set_value(2), ReplacementTransform(txt[1], txt[2]), run_time=1.3)
        self.esperar_resto()


class Coeficientes(Toma):
    def construct(self):
        m = tex(r"\begin{pmatrix}Q_1\\Q_2\\Q_3\end{pmatrix}=\begin{pmatrix}C_{11}&C_{12}&C_{13}\\C_{21}&C_{22}&C_{23}\\C_{31}&C_{32}&C_{33}\end{pmatrix}\begin{pmatrix}V_1\\V_2\\V_3\end{pmatrix}",
                font_size=50, color=MARFIL)
        m.move_to(UP * 2.4)
        self.play(FadeIn(m, shift=UP * 0.2), run_time=0.8)
        caja1 = SurroundingRectangle(m, buff=0.3, color=ORO, corner_radius=0.15)
        prop = VGroup(eq(r"C_{ii}>0", 54, MAG), eq(r"C_{ij}=C_{ji}\le0", 54, CIAN), eq(r"\sum_jC_{ij}\ge0", 54, ORO)).arrange(DOWN, buff=0.45)
        prop.move_to(DOWN * 2.6)
        self.play(Create(caja1), run_time=0.6)
        self.play(LaggedStart(*[FadeIn(p, shift=RIGHT * 0.2) for p in prop], lag_ratio=0.4), run_time=1.6)
        self.esperar_resto()


class Tierra(Toma):
    def construct(self):
        c = UP * 2.6
        R = 1.5
        on = ValueTracker(0)
        rng = np.random.default_rng(2)
        angs = rng.uniform(0, TAU, 26)
        suelo_y = -4.2

        def escena():
            u = on.get_value()
            g = VGroup(Circle(radius=R).move_to(c).set_stroke(MARFIL, 3).set_fill(MARFIL, 0.06))
            cerrado = u > 0.02
            g.add(Line(c + DOWN * R, c + DOWN * (R + 1.2), stroke_width=4, color=MARFIL))
            if cerrado:
                g.add(Line(c + DOWN * (R + 1.2), [0, suelo_y, 0], stroke_width=4, color=ORO))
            else:
                g.add(Line(c + DOWN * (R + 1.2), c + DOWN * (R + 1.2) + np.array([0.9, -0.8, 0]), stroke_width=4, color=MARFIL))
                g.add(Line([0, suelo_y + 2.0, 0], [0, suelo_y, 0], stroke_width=4, color=MARFIL))
            for k in range(4):
                w_ = 1.4 - 0.4 * k
                g.add(Line([-w_ / 2, suelo_y - 0.2 * k, 0], [w_ / 2, suelo_y - 0.2 * k, 0], stroke_width=4, color=MARFIL))
            for k, a in enumerate(angs):
                f = np.clip(u * 1.6 - k / len(angs) * 0.6, 0, 1)
                p0 = c + R * 0.92 * np.array([np.cos(a), np.sin(a), 0])
                if f <= 0:
                    p = p0
                elif f < 0.4:
                    p = p0 + (c + DOWN * R - p0) * (f / 0.4)
                else:
                    p = c + DOWN * R + (np.array([0, suelo_y, 0]) - (c + DOWN * R)) * ((f - 0.4) / 0.6)
                if f < 1:
                    g.add(Text("+", font="Inter", weight=BOLD, font_size=30, color=MAG).move_to(p))
            V = max(1 - u * 1.25, 0)
            g.add(eq(r"\phi=%.1f\,\mathrm{kV}" % (12 * V), 52, MAG if V > 0.01 else MARFIL).move_to(DOWN * 6.0))
            return g

        self.add(always_redraw(escena))
        self.wait(1.0)
        self.play(on.animate.set_value(1), run_time=self.duracion - 1.0, rate_func=rush_into)


# ---------------------------------------------------------------------------
# Tarjetas-ecuación (transparentes): la ecuación entra parpadeando como un tubo fluorescente
# ---------------------------------------------------------------------------
class _Tarjeta(Scene):
    ecuacion = ""
    pie = ""
    duracion = 3.2

    def construct(self):
        e = eq(self.ecuacion, 110)
        if e.width > 7.0:
            e.width = 7.0
        e.move_to(UP * 0.4)
        e.set_color(WHITE)
        halo = e.copy().set_stroke(CIAN, 14, 0.25).set_fill(opacity=0)
        p = Text(self.pie, font="Inter", weight=LIGHT, font_size=30, color=MARFIL).set_opacity(0.8) if self.pie else VGroup()
        if self.pie:
            if p.width > 6.8:
                p.width = 6.8
            p.next_to(e, DOWN, buff=0.7)
        grupo = VGroup(halo, e)
        grupo.set_opacity(0)
        self.add(grupo)
        for op, dt in ((0.9, 0.05), (0.1, 0.06), (0.7, 0.05), (0.0, 0.08), (1.0, 0.05), (0.3, 0.04), (1.0, 0.05)):
            e.set_opacity(op); halo.set_stroke(opacity=0.25 * op)
            self.wait(dt)
        if self.pie:
            self.play(FadeIn(p, shift=UP * 0.1), run_time=0.5)
        self.wait(max(self.duracion - 1.4, 0.3))
        self.play(FadeOut(VGroup(grupo, p)), run_time=0.5)


class TarjetaGauss(_Tarjeta):
    ecuacion = r"\nabla\cdot\mathbf E=\frac{\rho}{\varepsilon_0}"


class TarjetaMultipolo(_Tarjeta):
    ecuacion = r"\phi\simeq\frac{Q}{4\pi\varepsilon_0r}+\frac{\mathbf p\cdot\hat{\mathbf u}_r}{4\pi\varepsilon_0r^2}+\cdots"


class TarjetaConductor(_Tarjeta):
    ecuacion = r"\mathbf E_{\rm int}=0"


class TarjetaFinal(_Tarjeta):
    ecuacion = r"\oint\mathbf E\cdot d\mathbf S=\frac{Q}{\varepsilon_0}"
    pie = "every field line begins and ends on a charge."
    duracion = 4.4


TOMAS = ["FlujoGauss", "DivergenciaLocal", "Coulomb", "DeltaDirac", "Distribuciones", "GaussSimetrias", "Contorno", "RelievePotencial", "Teoremas",
         "Legendre", "Polarizacion", "Condensadores", "Coeficientes", "Tierra"]
CITAS = ["TarjetaGauss", "TarjetaMultipolo", "TarjetaConductor", "TarjetaFinal"]
