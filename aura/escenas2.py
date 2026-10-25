"""Tomas animadas del segundo edit: termodinámica, nanomagnetismo, partículas,
astrofísica, giróscopos, electricidad y fasores. Misma estética que escenas.py."""

from escenas import *  # noqa: F401,F403  (estilo, Toma, eq, punto_brillante, colores)
from escenas import _Cita

FUEGO = "#FF7A45"     # termodinámica
FRIO = "#59B8FF"
MAGN = "#FF5CA8"      # nanomagnetismo
PART = "#C9A6FF"      # partículas
ASTRO = "#FFD27A"     # astrofísica
FASOR = "#7CFFCB"     # electricidad y fasores


def proyector(centro, esc, phi, elev=0.35):
    def proy(x, y, z):
        a = phi.get_value() if hasattr(phi, "get_value") else phi
        X = x * np.cos(a) - y * np.sin(a)
        Yd = x * np.sin(a) + y * np.cos(a)
        return centro + esc * np.array([X, z * np.cos(elev) + Yd * np.sin(elev), 0])
    return proy


# ---------------------------------------------------------------------------
# Termodinámica
# ---------------------------------------------------------------------------
class MaxwellBoltzmann(Toma):
    def construct(self):
        rng = np.random.default_rng(11)
        n = 140
        caja = Rectangle(width=7.4, height=5.6).move_to(UP * 2.6).set_stroke(MARFIL, 1.5, 0.5)
        pos = np.c_[rng.uniform(-3.5, 3.5, n), rng.uniform(-2.6, 2.6, n)]
        dirs = rng.normal(size=(n, 3))
        dirs /= np.linalg.norm(dirs, axis=1)[:, None]
        v_mb = np.linalg.norm(rng.normal(size=(n, 3)), axis=1)
        s = ValueTracker(0)
        puntos = VGroup(*[Dot(radius=0.06) for _ in range(n)])

        def mover(g, dt):
            nonlocal pos
            rap = (1 - s.get_value()) * 1.6 + s.get_value() * v_mb
            v = dirs[:, :2] * rap[:, None] * 1.4
            pos = pos + v * dt
            for k in range(2):
                lim = 3.6 if k == 0 else 2.7
                fuera = np.abs(pos[:, k]) > lim
                dirs[fuera, k] *= -1
                pos[:, k] = np.clip(pos[:, k], -lim, lim)
            for i, d in enumerate(g):
                d.move_to(caja.get_center() + [pos[i, 0], pos[i, 1], 0])
                d.set_color(interpolate_color(ManimColor(FRIO), ManimColor(FUEGO), min(rap[i] / 3.0, 1)))

        mover(puntos, 0)
        puntos.add_updater(mover)
        ejes = Axes(x_range=[0, 4, 1], y_range=[0, 0.7, 0.2], x_length=7.2, y_length=3.2,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.5, "include_ticks": False}).move_to(DOWN * 3.0)
        curva = ejes.plot(lambda v: np.sqrt(2 / np.pi) * v * v * np.exp(-v * v / 2), x_range=[0, 4], stroke_width=4, color=FUEGO)

        def histo():
            rap = (1 - s.get_value()) * 1.6 + s.get_value() * v_mb
            h, b = np.histogram(rap, bins=16, range=(0, 4), density=True)
            g = VGroup()
            for hi, b0 in zip(h, b[:-1]):
                r = Rectangle(width=ejes.x_length / 16 * 0.85, height=max(ejes.y_length * min(hi, 0.7) / 0.7, 0.01))
                r.move_to(ejes.c2p(b0 + 0.125, 0), aligned_edge=DOWN).set_stroke(width=0).set_fill(MARFIL, 0.35)
                g.add(r)
            return g

        hs = always_redraw(histo)
        lab = eq(r"f(v)\propto v^2\,e^{-mv^2/2k_BT}", 46).move_to(DOWN * 5.6)
        self.add(caja, puntos, ejes, hs)
        self.play(s.animate.set_value(1), run_time=3.2, rate_func=smooth)
        self.play(Create(curva), FadeIn(lab), run_time=1.0)
        self.esperar_resto()


class Carnot(Toma):
    def construct(self):
        ejes = Axes(x_range=[0, 6.6, 1], y_range=[0, 1.8, 0.5], x_length=7.4, y_length=6.0,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.6, "include_ticks": False}).move_to(UP * 0.6)
        Th, Tc, g = 1.6, 1.0, 5 / 3
        VA, VB = 1.0, 3.0
        VC, VD = VB * (Th / Tc) ** 1.5, VA * (Th / Tc) ** 1.5
        iso_h = ejes.plot(lambda V: Th / V, x_range=[0.9, 6.6], stroke_width=2, color=FUEGO).set_stroke(opacity=0.35)
        iso_c = ejes.plot(lambda V: Tc / V, x_range=[0.56, 6.6], stroke_width=2, color=FRIO).set_stroke(opacity=0.35)
        tramos = [
            [ejes.c2p(V, Th / V) for V in np.linspace(VA, VB, 40)],
            [ejes.c2p(V, Th * VB ** (g - 1) / V ** g) for V in np.linspace(VB, VC, 40)],
            [ejes.c2p(V, Tc / V) for V in np.linspace(VC, VD, 40)],
            [ejes.c2p(V, Tc * VD ** (g - 1) / V ** g) for V in np.linspace(VD, VA, 40)],
        ]
        ciclo = VMobject().set_points_as_corners(sum(tramos, []))
        ciclo.set_stroke(width=5).set_color([FUEGO, ASTRO, FRIO, PART, FUEGO])
        relleno = ciclo.copy().set_stroke(width=0).set_fill(FUEGO, 0.12)
        self.add(ejes, iso_h, iso_c)
        bola = Dot(radius=0.1, color=WHITE)
        self.play(Create(ciclo), MoveAlongPath(bola, ciclo), run_time=2.8, rate_func=linear)
        self.play(FadeIn(relleno), run_time=0.4)
        lab = eq(r"\eta=1-\frac{T_c}{T_h}", 70, FUEGO).move_to(DOWN * 4.7)
        self.play(FadeIn(lab, scale=1.15), Flash(bola, color=FUEGO), run_time=0.7)
        self.esperar_resto()


class Entropia(Toma):
    def construct(self):
        rng = np.random.default_rng(5)
        n = 160
        caja = Rectangle(width=7.4, height=7.0).move_to(UP * 0.4).set_stroke(MARFIL, 1.5, 0.5)
        tabique = Line(caja.get_top(), caja.get_bottom(), stroke_width=3, color=MARFIL)
        pos = np.c_[np.r_[rng.uniform(-3.5, -0.2, n // 2), rng.uniform(0.2, 3.5, n // 2)], rng.uniform(-3.3, 3.3, n)]
        cols = [FRIO] * (n // 2) + [FUEGO] * (n // 2)
        pts = VGroup(*[Dot(radius=0.06, color=c) for c in cols])
        libre = [False]

        def mover(g, dt):
            nonlocal pos
            pos = pos + rng.normal(0, 1, pos.shape) * np.sqrt(dt) * 1.4
            pos[:, 1] = np.clip(pos[:, 1], -3.35, 3.35)
            pos[:, 0] = np.clip(pos[:, 0], -3.55, 3.55)
            if not libre[0]:
                izq = np.arange(n) < n // 2
                pos[izq, 0] = np.minimum(pos[izq, 0], -0.12)
                pos[~izq, 0] = np.maximum(pos[~izq, 0], 0.12)
            for i, d in enumerate(g):
                d.move_to(caja.get_center() + [pos[i, 0], pos[i, 1], 0])

        pts.add_updater(mover)
        lab = eq(r"S=k_B\ln\Omega", 76).move_to(DOWN * 4.9)
        self.add(caja, tabique, pts)
        self.wait(0.8)
        libre[0] = True
        self.play(FadeOut(tabique, shift=UP * 7), run_time=0.4)
        self.play(FadeIn(lab, shift=UP * 0.2), run_time=0.8)
        self.esperar_resto()


# ---------------------------------------------------------------------------
# Nanomagnetismo
# ---------------------------------------------------------------------------
class PrecesionEspin(Toma):
    def construct(self):
        phi = ValueTracker(0.4)
        proy = proyector(UP * 0.8, 3.0, phi, elev=0.42)
        t = ValueTracker(0)

        def m(tt):
            th = 1.35 * np.exp(-0.42 * tt) + 0.05
            ang = 7.0 * tt
            return np.array([np.sin(th) * np.cos(ang), np.sin(th) * np.sin(ang), np.cos(th)])

        def escena():
            g = VGroup()
            for la in np.linspace(-1.2, 1.2, 7):
                g.add(VMobject().set_points_smoothly([proy(np.cos(la) * np.cos(a), np.cos(la) * np.sin(a), np.sin(la))
                                                      for a in np.linspace(0, TAU, 50)]).set_stroke(MARFIL, 1, 0.18))
            for lo in np.linspace(0, PI, 6, endpoint=False):
                g.add(VMobject().set_points_smoothly([proy(np.cos(b) * np.cos(lo), np.cos(b) * np.sin(lo), np.sin(b))
                                                      for b in np.linspace(-PI / 2, PI / 2, 40)]).set_stroke(MARFIL, 1, 0.18))
            tt = t.get_value()
            ruta = [proy(*m(x)) for x in np.linspace(0, tt, max(int(tt * 60), 2))]
            g.add(VMobject().set_points_smoothly(ruta).set_stroke(MAGN, 3))
            g.add(Arrow(proy(0, 0, 0), proy(0, 0, 1.45), buff=0, stroke_width=4, color=FRIO))
            g.add(Arrow(proy(0, 0, 0), proy(*m(tt)), buff=0, stroke_width=6, color=WHITE))
            g.add(punto_brillante(proy(*m(tt)), MAGN, 0.07))
            return g

        e = always_redraw(escena)
        self.add(e)
        lh = eq(r"\mathbf H_{\rm eff}", 40, FRIO).move_to(UP * 5.6)
        lab = eq(r"\frac{d\mathbf m}{dt}=-\gamma\,\mathbf m\times\mathbf H_{\rm eff}+\alpha\,\mathbf m\times\frac{d\mathbf m}{dt}", 42)
        lab.move_to(DOWN * 5.4)
        self.play(t.animate.set_value(6), phi.animate.set_value(1.3), FadeIn(lh), FadeIn(lab), run_time=self.duracion, rate_func=linear)


class Histeresis(Toma):
    def construct(self):
        ejes = Axes(x_range=[-3, 3, 1], y_range=[-1.3, 1.3, 1], x_length=7.4, y_length=4.6,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.6, "include_ticks": False}).move_to(DOWN * 2.4)
        rng = np.random.default_rng(8)
        nx, ny = 7, 5
        umbral = rng.normal(0, 0.6, nx * ny) + 1.0
        estado = -np.ones(nx * ny)
        H = ValueTracker(-3)
        hist = [-3.0]
        flechas = VGroup(*[Arrow(DOWN * 0.32, UP * 0.32, buff=0, stroke_width=5, max_tip_length_to_length_ratio=0.35)
                           for _ in range(nx * ny)])
        for k, f in enumerate(flechas):
            f.move_to(UP * (3.4 - 0.85 * (k // nx)) + RIGHT * (-3.0 + (k % nx)))

        def actualizar(g):
            h = H.get_value()
            sube = h >= hist[-1]
            if sube:
                estado[(h > umbral)] = 1
            else:
                estado[(h < -umbral)] = -1
            hist.append(h)
            for k, f in enumerate(g):
                arriba = estado[k] > 0
                f.set_color(MAGN if arriba else FRIO)
                f.rotate(0 if (f.get_end()[1] > f.get_start()[1]) == arriba else PI)

        flechas.add_updater(actualizar)
        traza = TracedPath(lambda: ejes.c2p(H.get_value(), estado.mean()), stroke_color=MAGN, stroke_width=4)
        punto = always_redraw(lambda: punto_brillante(ejes.c2p(H.get_value(), estado.mean()), WHITE, 0.07))
        lm = eq(r"M", 40).next_to(ejes.c2p(0, 1.3), RIGHT, buff=0.1)
        lhh = eq(r"H", 40).next_to(ejes.c2p(3, 0), UP, buff=0.1)
        self.add(ejes, flechas, traza, punto, lm, lhh)
        self.play(H.animate.set_value(3), run_time=1.8, rate_func=linear)
        self.play(H.animate.set_value(-3), run_time=1.8, rate_func=linear)
        self.play(H.animate.set_value(0.8), run_time=0.8, rate_func=linear)
        self.esperar_resto()


# ---------------------------------------------------------------------------
# Física de partículas
# ---------------------------------------------------------------------------
class CamaraBurbujas(Toma):
    def construct(self):
        rng = np.random.default_rng(21)

        def espiral(p0, ang, R0, signo, perdida):
            pts, p, a, R = [], np.array(p0, dtype=float), ang, R0
            for _ in range(900):
                pts.append(p.copy())
                ds = 0.03
                a += signo * ds / R
                p = p + ds * np.array([np.cos(a), np.sin(a), 0])
                R *= (1 - perdida)
                if R < 0.05 or abs(p[0]) > 5 or abs(p[1]) > 9:
                    break
            return pts

        trazas = []
        for _ in range(9):
            trazas.append((espiral([rng.uniform(-3, 3), -8.5, 0], PI / 2 + rng.uniform(-0.3, 0.3), rng.uniform(2.5, 9),
                                   rng.choice([-1, 1]), rng.uniform(0.0015, 0.004)), MARFIL, 2))
        v = np.array([0.4, 0.6, 0])
        trazas.append((espiral(v, PI / 2 - 0.3, 2.2, 1, 0.004), MAGN, 4))
        trazas.append((espiral(v, PI / 2 + 0.3, 2.2, -1, 0.004), FRIO, 4))
        curvas = VGroup()
        for pts, c, w in trazas:
            m = VMobject().set_points_smoothly(pts[::2])
            curvas.add(DashedVMobject(m, num_dashes=max(len(pts) // 4, 8), dashed_ratio=0.6).set_stroke(c, w))
        foton = DashedLine(v + DOWN * 9, v, stroke_width=2, color=ASTRO, dash_length=0.25).set_opacity(0.5)
        self.play(Create(foton), LaggedStart(*[Create(c) for c in curvas[:-2]], lag_ratio=0.1), run_time=2.0, rate_func=linear)
        self.play(Flash(v, color=WHITE, flash_radius=0.5), Create(curvas[-2]), Create(curvas[-1]), run_time=1.6, rate_func=linear)
        lab = eq(r"\gamma\to e^-e^+,\qquad r=\frac{p}{qB}", 50).move_to(DOWN * 6.1)
        self.play(FadeIn(lab), run_time=0.6)
        self.esperar_resto()


class DiagramaFeynman(Toma):
    def construct(self):
        a, b = np.array([0, -1.6, 0]), np.array([0, 1.6, 0])
        e1 = Line([-2.6, -4.4, 0], a, color=MARFIL, stroke_width=4)
        e2 = Line([2.6, -4.4, 0], a, color=MARFIL, stroke_width=4)
        m1 = Line(b, [-2.6, 4.4, 0], color=PART, stroke_width=4)
        m2 = Line(b, [2.6, 4.4, 0], color=PART, stroke_width=4)
        foton = ParametricFunction(lambda s: np.array([0.22 * np.sin(s * 18 * np.pi), -1.6 + 3.2 * s, 0]), t_range=[0, 1],
                                   stroke_width=4, color=ASTRO)
        flechas = VGroup(*[Arrow(l.point_from_proportion(0.4), l.point_from_proportion(0.6), buff=0, stroke_width=4,
                                 color=l.get_color(), max_tip_length_to_length_ratio=0.5) for l in (e1, m1)],
                         *[Arrow(l.point_from_proportion(0.6), l.point_from_proportion(0.4), buff=0, stroke_width=4,
                                 color=l.get_color(), max_tip_length_to_length_ratio=0.5) for l in (e2, m2)])
        et = VGroup(eq(r"e^-", 40).next_to(e1.get_start(), DOWN), eq(r"e^+", 40).next_to(e2.get_start(), DOWN),
                    eq(r"\mu^-", 40, PART).next_to(m1.get_end(), UP), eq(r"\mu^+", 40, PART).next_to(m2.get_end(), UP),
                    eq(r"\gamma", 44, ASTRO).next_to(foton, RIGHT, buff=0.3))
        self.play(Create(e1), Create(e2), FadeIn(et[:2]), run_time=0.8, rate_func=linear)
        self.play(Create(foton), FadeIn(punto_brillante(a, WHITE, 0.08)), FadeIn(et[4]), run_time=0.7, rate_func=linear)
        self.play(Create(m1), Create(m2), FadeIn(punto_brillante(b, WHITE, 0.08)), FadeIn(et[2:4]), FadeIn(flechas), run_time=0.8)
        lab = eq(r"\mathcal L=\bar\psi(i\gamma^\mu D_\mu-m)\psi-\tfrac14F_{\mu\nu}F^{\mu\nu}", 44).move_to(DOWN * 6.0)
        self.play(FadeIn(lab, shift=UP * 0.2), run_time=0.6)
        self.esperar_resto()


class Higgs(Toma):
    def construct(self):
        phi = ValueTracker(0.2)
        proy = proyector(UP * 0.6, 1.9, phi, elev=0.5)
        V = lambda r: 0.9 * (r * r - 2.2) ** 2 / 1.6 - 0.9
        bola_r = ValueTracker(0.02)

        def sombrero():
            g = VGroup()
            for r in np.linspace(0.15, 1.95, 12):
                g.add(VMobject().set_points_smoothly([proy(r * np.cos(a), r * np.sin(a), V(r)) for a in np.linspace(0, TAU, 60)])
                      .set_stroke(PART, 1.6, 0.25 + 0.4 * (1 - r / 1.95)))
            for a in np.linspace(0, TAU, 24, endpoint=False):
                g.add(VMobject().set_points_smoothly([proy(r * np.cos(a), r * np.sin(a), V(r)) for r in np.linspace(0, 1.95, 30)])
                      .set_stroke(PART, 1.2, 0.3))
            r = bola_r.get_value()
            g.add(punto_brillante(proy(r * np.cos(0.6), r * np.sin(0.6), V(r) + 0.12), WHITE, 0.12))
            return g

        s = always_redraw(sombrero)
        self.add(s)
        lab = eq(r"V(\phi)=-\mu^2|\phi|^2+\lambda|\phi|^4", 50).move_to(DOWN * 5.4)
        self.play(phi.animate.set_value(0.9), FadeIn(lab), run_time=1.2)
        self.play(bola_r.animate.set_value(np.sqrt(2.2)), phi.animate.set_value(2.0), run_time=2.2, rate_func=rush_into)
        self.play(phi.animate.set_value(2.6), run_time=1.6)


# ---------------------------------------------------------------------------
# Astrofísica
# ---------------------------------------------------------------------------
class OndasGravitatorias(Toma):
    duracion = 5.0

    def construct(self):
        t = ValueTracker(0)
        tc = 3.6

        def fase(tt):
            tau = max(tc - tt, 0.004)
            return -2 * (tau ** (5 / 8)) * 9

        def radio(tt):
            return 1.7 * max(tc - tt, 0.0) ** 0.25 / tc ** 0.25

        centro = UP * 1.6

        def binaria():
            tt = t.get_value()
            g = VGroup()
            if tt < tc:
                r, f = radio(tt), fase(tt)
                for sgn, c in ((1, ASTRO), (-1, FRIO)):
                    g.add(punto_brillante(centro + sgn * r * np.array([np.cos(f), np.sin(f) * 0.55, 0]), c, 0.13))
            else:
                k = tt - tc
                g.add(punto_brillante(centro, WHITE, 0.16 + 0.5 * np.exp(-k * 6)))
            for j in range(9):
                rr = ((tt * 2.2 + j * 0.6) % 5.4)
                g.add(Ellipse(width=2 * rr, height=1.1 * rr).move_to(centro).set_stroke(MARFIL, 1.5, 0.35 * (1 - rr / 5.4)))
            return g

        ejes_y = DOWN * 3.6

        def onda():
            tt = t.get_value()
            xs = np.linspace(0, min(tt, 4.6), max(int(min(tt, 4.6) * 90), 2))
            ys = []
            for x in xs:
                if x < tc:
                    ys.append(0.25 / max(radio(x), 0.25) * np.cos(2 * fase(x)))
                else:
                    ys.append(np.exp(-(x - tc) * 7) * np.cos(40 * (x - tc)))
            pts = [ejes_y + [-3.8 + 7.6 * x / 4.6, 0.9 * y, 0] for x, y in zip(xs, ys)]
            return VMobject().set_points_smoothly(pts).set_stroke(ASTRO, 3)

        self.add(always_redraw(binaria), always_redraw(onda), Line(ejes_y + LEFT * 3.9, ejes_y + RIGHT * 3.9).set_stroke(MARFIL, 1, 0.3))
        lab = eq(r"h(t)", 44, ASTRO).move_to(ejes_y + UP * 1.6 + LEFT * 3.2)
        self.add(lab)
        self.play(t.animate.set_value(4.6), run_time=self.duracion, rate_func=linear)


class Pulsar(Toma):
    def construct(self):
        t = ValueTracker(0)
        c = UP * 1.4
        incl = 0.5

        def escena():
            a = t.get_value() * 6
            eje = np.array([np.sin(incl) * np.cos(a), np.cos(incl), np.sin(incl) * np.sin(a)])
            g = VGroup()
            for sgn in (1, -1):
                d = sgn * eje
                tip = c + 5.5 * np.array([d[0], d[1], 0])
                perp = np.array([-d[1], d[0], 0])
                ancho = 0.35 + 0.6 * abs(d[2])
                haz = Polygon(c, tip + perp * ancho, tip - perp * ancho, stroke_width=0)
                haz.set_fill([WHITE, FRIO], opacity=0.25 + 0.55 * max(d[2], 0))
                g.add(haz)
            g.add(Circle(radius=0.5).move_to(c).set_stroke(FRIO, 2).set_fill(FRIO, 0.25), punto_brillante(c, WHITE, 0.22))
            return g

        e = always_redraw(escena)
        base = DOWN * 4.4

        def pulsos():
            tt = t.get_value()
            xs = np.linspace(0, tt, max(int(tt * 120), 2))
            ys = [np.exp(-((np.cos(x * 6) * np.sin(incl) - 0) ** 2 + (np.sin(x * 6) - 1) ** 2) * 18) for x in xs]
            return VMobject().set_points_smoothly([base + [-3.8 + 7.6 * x / 4.0, 1.2 * y, 0] for x, y in zip(xs, ys)]).set_stroke(FRIO, 3)

        self.add(e, always_redraw(pulsos))
        lab = eq(r"P\approx 1.3\,\mathrm{ms}", 44, FRIO).move_to(DOWN * 6.0)
        self.play(t.animate.set_value(4.0), FadeIn(lab), run_time=self.duracion, rate_func=linear)


class Hubble(Toma):
    def construct(self):
        rng = np.random.default_rng(31)
        n = 60
        p0 = np.c_[rng.uniform(-2.2, 2.2, n), rng.uniform(-3.0, 3.0, n)]
        a = ValueTracker(0.45)
        cols = [interpolate_color(ManimColor(ASTRO), ManimColor(FRIO), rng.uniform()) for _ in range(n)]
        ang = rng.uniform(0, PI, n)

        def galaxias():
            g = VGroup()
            for (x, y), c, an in zip(p0, cols, ang):
                q = UP * 1.4 + a.get_value() * np.array([x, y, 0])
                if abs(q[0]) < 4.6 and -1.4 < q[1] < 7.6:
                    g.add(Ellipse(width=0.24, height=0.1, color=c).set_fill(c, 0.8).rotate(an).move_to(q))
            return g

        ejes = Axes(x_range=[0, 4, 1], y_range=[0, 4, 1], x_length=6.4, y_length=3.6,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.6, "include_ticks": False}).move_to(DOWN * 3.9)
        recta = ejes.plot(lambda d: d, x_range=[0, 3.9], stroke_width=3, color=ASTRO)
        dots = VGroup(*[Dot(ejes.c2p(d, d + rng.normal(0, 0.18)), radius=0.06, color=MARFIL) for d in rng.uniform(0.3, 3.8, 22)])
        self.add(always_redraw(galaxias), ejes)
        self.play(a.animate.set_value(1.6), LaggedStart(*[FadeIn(d, scale=2) for d in dots], lag_ratio=0.08), run_time=3.0, rate_func=smooth)
        lab = eq(r"v=H_0\,d", 60, ASTRO).move_to(DOWN * 6.3)
        self.play(Create(recta), FadeIn(lab), a.animate.set_value(2.0), run_time=1.2)
        self.esperar_resto()


class DiagramaHR(Toma):
    def construct(self):
        rng = np.random.default_rng(41)
        ejes = Axes(x_range=[0, 1, 0.25], y_range=[-4, 6, 2], x_length=7.2, y_length=9.0,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.5, "include_ticks": False}).move_to(UP * 0.4)
        estrellas = []
        for _ in range(330):                          # secuencia principal
            x = rng.uniform(0.02, 0.98)
            estrellas.append((x, 5.2 - 8.6 * x + rng.normal(0, 0.35)))
        for _ in range(45):                           # gigantes
            estrellas.append((rng.uniform(0.6, 0.95), rng.uniform(1.5, 3.3)))
        for _ in range(15):                           # supergigantes
            estrellas.append((rng.uniform(0.1, 0.95), rng.uniform(4.5, 5.6)))
        for _ in range(30):                           # enanas blancas
            estrellas.append((rng.uniform(0.05, 0.4), rng.uniform(-3.6, -2.2)))
        temp = lambda x: interpolate_color(ManimColor("#9BB8FF"), ManimColor("#FF8A5C"), x)
        puntos = VGroup(*[Dot(ejes.c2p(x, y), radius=0.035 + 0.03 * max(y + 4, 0) / 10, color=temp(x)).set_opacity(0.9)
                          for x, y in estrellas])
        sol = punto_brillante(ejes.c2p(0.55, 0.45), ASTRO, 0.09)
        ls = Text("Sol", font="Inter", weight=LIGHT, font_size=26, color=ASTRO).next_to(sol, RIGHT, buff=0.2)
        lx = eq(r"T", 36).next_to(ejes.c2p(1, -4), DOWN, buff=0.1)
        ly = eq(r"L/L_\odot", 36).next_to(ejes.c2p(0, 6), RIGHT, buff=0.1)
        self.add(ejes, lx, ly)
        self.play(LaggedStart(*[FadeIn(p, scale=3) for p in puntos], lag_ratio=0.006), run_time=2.8)
        self.play(FadeIn(sol, scale=2), FadeIn(ls), run_time=0.6)
        lab = eq(r"L=4\pi R^2\sigma T^4", 54, ASTRO).move_to(DOWN * 5.9)
        self.play(FadeIn(lab), run_time=0.5)
        self.esperar_resto()


# ---------------------------------------------------------------------------
# Giróscopos, electricidad y fasores
# ---------------------------------------------------------------------------
class Giroscopio(Toma):
    def construct(self):
        t = ValueTracker(0)
        proy = proyector(DOWN * 1.2, 2.2, 0.35, elev=0.3)

        def escena():
            tt = t.get_value()
            prec = 1.2 * tt
            th = 0.75 + 0.06 * np.sin(14 * tt)
            ax = np.array([np.sin(th) * np.cos(prec), np.sin(th) * np.sin(prec), np.cos(th)])
            centro = ax * 2.0
            u = np.cross(ax, [0, 0, 1]); u /= np.linalg.norm(u)
            w = np.cross(ax, u)
            g = VGroup()
            disco = [proy(*(centro + 0.95 * (np.cos(a) * u + np.sin(a) * w))) for a in np.linspace(0, TAU, 60)]
            g.add(VMobject().set_points_smoothly(disco).set_stroke(MARFIL, 3).set_fill(MARFIL, 0.06))
            giro = 30 * tt
            for k in range(6):
                a = giro + k * TAU / 6
                g.add(Line(proy(*centro), proy(*(centro + 0.95 * (np.cos(a) * u + np.sin(a) * w))), stroke_width=1.5, color=MARFIL).set_opacity(0.6))
            g.add(Line(proy(0, 0, 0), proy(*(ax * 2.6)), stroke_width=4, color=MARFIL))
            g.add(Arrow(proy(*centro), proy(*(centro + ax * 1.8)), buff=0, stroke_width=5, color=FASOR))
            g.add(Arrow(proy(*centro), proy(*(centro + np.array([0, 0, -1.1]))), buff=0, stroke_width=3, color=FUEGO))
            ruta = [proy(*(2.0 * np.array([np.sin(0.75) * np.cos(p), np.sin(0.75) * np.sin(p), np.cos(0.75)])))
                    for p in np.linspace(0, TAU, 80)]
            g.add(DashedVMobject(VMobject().set_points_smoothly(ruta), num_dashes=40).set_stroke(FASOR, 1.5, 0.5))
            g.add(punto_brillante(proy(0, 0, 0), WHITE, 0.08))
            return g

        self.add(always_redraw(escena))
        eqs = VGroup(eq(r"\boldsymbol\tau=\frac{d\mathbf L}{dt}", 54), eq(r"\Omega=\frac{mgr}{I\omega}", 54, FASOR)).arrange(RIGHT, buff=0.9)
        eqs.move_to(DOWN * 5.6)
        self.play(t.animate.set_value(5), FadeIn(eqs), run_time=self.duracion, rate_func=linear)


class FasoresRLC(Toma):
    def construct(self):
        w = ValueTracker(0.45)
        t = ValueTracker(0)
        c = UP * 2.2
        R, L, C = 1.0, 1.0, 1.0

        def escena():
            om = w.get_value()
            Z = complex(R, om * L - 1 / (om * C))
            I = 3.2 / abs(Z)
            rot = np.exp(1j * t.get_value())
            vr, vl, vc = I * R * rot, 1j * I * om * L * rot * 0.9, -1j * I / (om * C) * rot * 0.9
            p0 = c + LEFT * 1.6
            g = VGroup()
            for v, col in ((vr, MARFIL), (vl, FASOR), (vc, MAGN)):
                p1 = p0 + np.array([v.real, v.imag, 0])
                g.add(Arrow(p0, p1, buff=0, stroke_width=5, color=col, max_tip_length_to_length_ratio=0.12))
                p0 = p1
            g.add(Arrow(c + LEFT * 1.6, p0, buff=0, stroke_width=6, color=ASTRO, max_tip_length_to_length_ratio=0.12))
            return g

        ejes = Axes(x_range=[0, 3, 1], y_range=[0, 1.8, 0.5], x_length=7.0, y_length=3.0,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.5, "include_ticks": False}).move_to(DOWN * 3.6)
        res = ejes.plot(lambda om: 1.6 / abs(complex(R, om * L - 1 / (om * C))), x_range=[0.2, 3, 0.01], stroke_width=4, color=ASTRO)
        dot = always_redraw(lambda: punto_brillante(ejes.c2p(w.get_value(), 1.6 / abs(complex(R, w.get_value() * L - 1 / (w.get_value() * C)))), WHITE, 0.08))
        leyenda = VGroup(eq(r"V_R", 34, MARFIL), eq(r"V_L", 34, FASOR), eq(r"V_C", 34, MAGN), eq(r"V", 34, ASTRO)).arrange(RIGHT, buff=0.5)
        leyenda.move_to(UP * 5.2)
        self.add(always_redraw(escena), ejes, res, dot, leyenda)
        lab = eq(r"\omega_0=\frac{1}{\sqrt{LC}}", 54).move_to(DOWN * 6.2)
        self.play(w.animate.set_value(1.0), t.animate.set_value(2.5), run_time=2.6, rate_func=smooth)
        self.play(FadeIn(lab), Flash(ejes.c2p(1.0, 1.6), color=ASTRO), t.animate.set_value(3.3), run_time=0.8)
        self.play(w.animate.set_value(2.4), t.animate.set_value(5), run_time=1.6, rate_func=smooth)


class Trifasica(Toma):
    def construct(self):
        t = ValueTracker(0)
        c = np.array([-2.4, 2.2, 0])
        R = 1.5
        cols = [FASOR, ASTRO, MAGN]

        def escena():
            tt = t.get_value()
            g = VGroup(Circle(radius=R).move_to(c).set_stroke(MARFIL, 1, 0.3))
            p = c.copy()
            for k, col in enumerate(cols):
                a = tt - k * TAU / 3
                tip = c + R * np.array([np.cos(a), np.sin(a), 0])
                g.add(Line(c, tip, stroke_width=5, color=col))
                xs = np.linspace(0, 4.6, 120)
                g.add(VMobject().set_points_smoothly([[c[0] + 1.9 + x, c[1] + R * np.sin(a - 1.6 * x), 0] for x in xs])
                      .set_stroke(col, 3))
                q = p + R * np.array([np.cos(a), np.sin(a), 0]) * 0.7
                g.add(Line(p + DOWN * 5.0, q + DOWN * 5.0, stroke_width=4, color=col))
                p = q
            g.add(punto_brillante(c + DOWN * 5.0, WHITE, 0.07))
            return g

        self.add(always_redraw(escena))
        lab = eq(r"\sum_k V_0\cos\!\big(\omega t-\tfrac{2\pi k}{3}\big)=0", 46).move_to(DOWN * 5.8)
        self.play(t.animate.set_value(3 * TAU / 2), FadeIn(lab), run_time=self.duracion, rate_func=linear)


# ---------------------------------------------------------------------------
# Títulos y citas
# ---------------------------------------------------------------------------
class Titulo2(Toma):
    duracion = 3.0

    def construct(self):
        t = Text("C O S M O S", font="Inter Display", weight=LIGHT, font_size=104, color=MARFIL)
        s = Text("del calor a las estrellas", font="CMU Serif", slant=ITALIC, font_size=40, color=GRIS).next_to(t, DOWN, buff=0.5)
        self.play(FadeIn(t, scale=0.9), run_time=0.9)
        self.play(FadeIn(s, shift=UP * 0.15), run_time=0.7)
        self.esperar_resto()


class CitaEddington(_Cita):
    texto = ("The law that entropy always increases\nholds, I think, the supreme position\namong the laws of Nature.")
    autor = "Arthur Eddington"


class CitaSaganEstrellas(_Cita):
    texto = ("The nitrogen in our DNA, the calcium\nin our teeth, the iron in our blood...\n"
             "were made in the interiors\nof collapsing stars.")
    autor = "Carl Sagan"


class AdAstra(Toma):
    duracion = 4.0

    def construct(self):
        t = Text("Per aspera ad astra.", font="CMU Serif", slant=ITALIC, font_size=80, color=MARFIL)
        t.width = min(t.width, 7.6)
        l = Line(LEFT * 1.4, RIGHT * 1.4, stroke_width=1.2, color=MARFIL).set_opacity(0.6).next_to(t, DOWN, buff=0.55)
        self.play(FadeIn(t, shift=UP * 0.15), run_time=1.4)
        self.play(GrowFromCenter(l), run_time=0.8)
        self.wait(1.2)
        self.play(FadeOut(VGroup(t, l)), run_time=0.6)


TOMAS = ["Titulo2", "MaxwellBoltzmann", "Carnot", "Entropia", "PrecesionEspin", "Histeresis", "CamaraBurbujas",
         "DiagramaFeynman", "Higgs", "OndasGravitatorias", "Pulsar", "Hubble", "DiagramaHR", "Giroscopio",
         "FasoresRLC", "Trifasica", "AdAstra"]
CITAS = ["CitaEddington", "CitaSaganEstrellas"]
