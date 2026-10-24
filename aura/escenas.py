"""Tomas animadas para el edit de Física «con aura».

Estética: negro puro, trazo fino marfil y un único acento por rama de la física.
El brillo (bloom), el grano y la viñeta se añaden después en montar.py.
Cada toma dura unos 4 s; el montaje recorta el trozo que necesita.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "clips"))
from estilo import *  # noqa: E402  (formato vertical, tex(), texto())

config.background_color = "#000000"

MARFIL = "#F3EFE6"
ELEC = "#5CE1FF"      # electrodinámica
CUANT = "#B98CFF"     # cuántica y lagrangiana
GRAV = "#FFC266"      # gravitación
EDOC = "#FF4D6D"      # sistemas dinámicos
COMP = "#7CFFCB"      # variable compleja
ESPECTRO = ["#8B5CF6", "#3B82F6", "#22D3EE", "#34D399", "#FDE047", "#FB923C", "#EF4444"]


def eq(cadena, size=56, color=MARFIL):
    return tex(cadena, font_size=size, color=color)


def punto_brillante(p, color=MARFIL, r=0.09):
    g = VGroup()
    for k, (rr, op) in enumerate(((r * 4, 0.06), (r * 2.4, 0.14), (r * 1.5, 0.35))):
        g.add(Dot(p, radius=rr, color=color).set_opacity(op))
    g.add(Dot(p, radius=r, color=WHITE))
    return g


class Toma(Scene):
    duracion = 5.0

    def esperar_resto(self):
        resto = self.duracion - self.renderer.time
        if resto > 0.02:
            self.wait(resto)


# ---------------------------------------------------------------------------
# Electrodinámica
# ---------------------------------------------------------------------------
class Maxwell(Toma):
    def construct(self):
        eqs = VGroup(
            eq(r"\nabla\cdot\mathbf E=\frac{\rho}{\varepsilon_0}"),
            eq(r"\nabla\cdot\mathbf B=0"),
            eq(r"\nabla\times\mathbf E=-\frac{\partial\mathbf B}{\partial t}"),
            eq(r"\nabla\times\mathbf B=\mu_0\mathbf J+\mu_0\varepsilon_0\frac{\partial\mathbf E}{\partial t}"),
        ).arrange(DOWN, buff=0.7)
        ajustar(eqs, 8.0)
        for e in eqs:
            e[0][0].set_color(ELEC)
        self.play(LaggedStart(*[FadeIn(e, shift=UP * 0.25, scale=1.08) for e in eqs], lag_ratio=0.35), run_time=1.8)
        self.play(eqs.animate.scale(1.06), *[Indicate(e[0][0], color=WHITE, scale_factor=1.3) for e in eqs], run_time=1.2)
        self.play(eqs.animate.scale(1.03), run_time=0.9, rate_func=linear)
        self.esperar_resto()


class Dipolo(Toma):
    def construct(self):
        q1, q2 = np.array([0, 1.7, 0]), np.array([0, -1.7, 0])

        def campo(p):
            a, b = p - q1, p - q2
            return a / np.linalg.norm(a) ** 3 - b / np.linalg.norm(b) ** 3

        lineas = VGroup()
        for ang in np.linspace(0, TAU, 26, endpoint=False) + 0.06:
            p = q1 + 0.12 * np.array([np.cos(ang), np.sin(ang), 0])
            pts = [p]
            for _ in range(900):
                v = campo(p)
                p = p + 0.03 * v / np.linalg.norm(v)
                pts.append(p)
                if np.linalg.norm(p - q2) < 0.1 or abs(p[0]) > 5 or abs(p[1]) > 8.5:
                    break
            c = VMobject().set_points_smoothly(pts[::3] + [pts[-1]])
            lineas.add(c.set_stroke(interpolate_color(ManimColor(ELEC), ManimColor(MARFIL), abs(np.cos(ang))), 2.2, 0.75))
        self.add(punto_brillante(q1, ELEC, 0.14), punto_brillante(q2, "#FF5C8A", 0.14))
        self.play(LaggedStart(*[Create(l) for l in lineas], lag_ratio=0.03), run_time=1.4)
        chispas = VGroup(*[Dot(radius=0.05, color=WHITE) for _ in range(len(lineas) * 2)])
        fases = np.random.default_rng(1).uniform(0, 1, len(chispas))
        reloj = [0.0]

        def mover(g, dt):
            reloj[0] += dt
            for k, d in enumerate(g):
                d.move_to(lineas[k // 2].point_from_proportion((fases[k] + 0.35 * reloj[0]) % 1))

        chispas.add_updater(mover)
        mover(chispas, 0)
        self.add(chispas)
        lab = eq(r"\mathbf E=\frac{1}{4\pi\varepsilon_0}\frac{q}{r^2}\,\hat{\mathbf r}", 50).move_to(DOWN * 5.8)
        self.play(FadeIn(lab), run_time=0.6)
        self.esperar_resto()


class OndaEM(Toma):
    def construct(self):
        t = ValueTracker(0)
        u = np.array([0.45, 0.89, 0])   # dirección de propagación (diagonal)
        e_dir = np.array([0.89, -0.45, 0]) * 1.0
        b_dir = np.array([-0.35, -0.25, 0])

        def onda():
            s = np.linspace(-8, 8, 260)
            fase = 1.6 * s - 5 * t.get_value()
            base = [u * x for x in s]
            E = VMobject(stroke_width=4, stroke_color=ELEC).set_points_smoothly([b + e_dir * 1.3 * np.sin(f) for b, f in zip(base, fase)])
            B = VMobject(stroke_width=4, stroke_color="#FF5C8A").set_points_smoothly([b + b_dir * 2.4 * np.sin(f) for b, f in zip(base, fase)])
            palos = VGroup(*[Line(base[k], base[k] + e_dir * 1.3 * np.sin(fase[k]), stroke_width=1.5, color=ELEC).set_opacity(0.45)
                             for k in range(0, 260, 7)])
            eje = Line(u * -9, u * 9, stroke_width=1.5, color=MARFIL).set_opacity(0.5)
            return VGroup(eje, palos, B, E)

        o = always_redraw(onda)
        self.add(o)
        lab = eq(r"c=\frac{1}{\sqrt{\mu_0\varepsilon_0}}", 50).move_to(DOWN * 5.6)
        self.play(t.animate.set_value(4), FadeIn(lab, shift=UP * 0.2), run_time=self.duracion, rate_func=linear)


# ---------------------------------------------------------------------------
# Cuántica y lagrangiana
# ---------------------------------------------------------------------------
class Schrodinger(Toma):
    def construct(self):
        top = eq(r"i\hbar\,\frac{\partial\psi}{\partial t}=\hat H\psi", 64).move_to(UP * 4.6)
        top[0][0:2].set_color(CUANT)
        ejes_c = np.array([0, -0.8, 0])
        sx, sy = 1.0, 2.4
        t = ValueTracker(0)
        V = FunctionGraph(lambda x: 0.12 * x * x, x_range=[-4.2, 4.2]).shift(ejes_c).set_stroke(MARFIL, 1.5, 0.35)

        def psi():
            tt = t.get_value()
            x = np.linspace(-4.2, 4.2, 300)
            x0 = 2.0 * np.cos(tt)
            p0 = -2.0 * np.sin(tt)
            env = np.exp(-(x - x0) ** 2 / 2) / np.pi ** 0.25
            re = env * np.cos(p0 * x - tt / 2 - 0.5 * x0 * p0 + 6 * tt)
            dens = env ** 2
            curva_re = VMobject(stroke_width=3, stroke_color=CUANT).set_points_smoothly([ejes_c + [sx * a, sy * b * 0.6, 0] for a, b in zip(x, re)])
            curva_d = VMobject(stroke_width=4, stroke_color=WHITE).set_points_smoothly([ejes_c + [sx * a, sy * b, 0] for a, b in zip(x, dens)])
            area = curva_d.copy().add_line_to(ejes_c + [sx * x[-1], 0, 0]).add_line_to(ejes_c + [sx * x[0], 0, 0])
            area.set_stroke(width=0).set_fill(CUANT, 0.25)
            return VGroup(area, curva_re, curva_d)

        ps = always_redraw(psi)
        self.add(V, ps)
        self.play(FadeIn(top, shift=DOWN * 0.3), t.animate.set_value(PI), run_time=2.0, rate_func=linear)
        self.play(t.animate.set_value(2 * PI), run_time=2.0, rate_func=linear)


class AccionMinima(Toma):
    def construct(self):
        A, B = np.array([-3.4, -3.0, 0]), np.array([3.4, -3.0, 0])
        rng = np.random.default_rng(3)
        modos = [rng.normal(0, 1, 6) for _ in range(28)]
        k = ValueTracker(1.0)

        def camino(c, amp):
            s = np.linspace(0, 1, 80)
            y = 7.0 * s * (1 - s)
            for j, a in enumerate(c):
                y = y + amp * a * 0.9 * np.sin((j + 1) * np.pi * s) / (j + 1) ** 0.5
            return [A + (B - A) * si + UP * yi for si, yi in zip(s, y)]

        def caminos():
            g = VGroup()
            amp = k.get_value()
            for idx, c in enumerate(modos):
                m = VMobject(stroke_width=1.6, stroke_color=interpolate_color(ManimColor(CUANT), ManimColor(GRAV), idx / 28))
                g.add(m.set_points_smoothly(camino(c, amp)).set_stroke(opacity=0.2 + 0.5 * (1 - amp)))
            real = VMobject(stroke_width=6, stroke_color=GRAV).set_points_smoothly(camino(np.zeros(6), 0))
            g.add(real.set_stroke(opacity=1 - amp * 0.85))
            return g

        cs = always_redraw(caminos)
        self.add(cs, punto_brillante(A), punto_brillante(B))
        S = eq(r"S=\int L\,dt", 60).move_to(UP * 5.2)
        dS = eq(r"\delta S=0", 72, GRAV).move_to(DOWN * 5.0)
        self.play(FadeIn(S), run_time=0.6)
        self.play(k.animate.set_value(0), run_time=2.6, rate_func=smooth)
        self.play(FadeIn(dS, scale=1.2), run_time=0.5)
        self.esperar_resto()


# ---------------------------------------------------------------------------
# Gravitación y órbitas
# ---------------------------------------------------------------------------
class Kepler(Toma):
    def construct(self):
        a, e = 3.4, 0.62
        b = a * np.sqrt(1 - e * e)
        foco = np.array([0, 0.4, 0])
        centro = foco + np.array([0, a * e, 0])  # eje mayor vertical

        def pos(M):
            E = M
            for _ in range(30):
                E = E - (E - e * np.sin(E) - M) / (1 - e * np.cos(E))
            return centro + np.array([b * np.sin(E), -a * np.cos(E), 0])

        orb = VMobject().set_points_smoothly([pos(m) for m in np.linspace(0, TAU, 200)])
        orb.set_stroke(MARFIL, 1.5, 0.35)
        self.add(orb, punto_brillante(foco, GRAV, 0.2))
        M = ValueTracker(0)
        planeta = always_redraw(lambda: punto_brillante(pos(M.get_value()), WHITE, 0.08))
        estela = TracedPath(lambda: pos(M.get_value()), stroke_color=GRAV, stroke_width=4, dissipating_time=0.9)
        self.add(estela, planeta)
        sectores = VGroup()
        for k in range(6):
            m0 = k * TAU / 6
            pts = [foco] + [pos(m) for m in np.linspace(m0, m0 + TAU / 12, 20)]
            sec = Polygon(*pts, stroke_width=0).set_fill(GRAV, 0.18 if k % 2 == 0 else 0.08)
            sectores.add(sec)
        ley = eq(r"\frac{dA}{dt}=\frac{L}{2m}", 54).move_to(DOWN * 5.5)
        self.play(M.animate.set_value(TAU), LaggedStart(*[FadeIn(s) for s in sectores], lag_ratio=0.6),
                  FadeIn(ley), run_time=self.duracion, rate_func=linear)


class TresCuerpos(Toma):
    def construct(self):
        x = np.array([[0.97000436, -0.24308753], [-0.97000436, 0.24308753], [0.0, 0.0]])
        v3 = np.array([-0.93240737, -0.86473146])
        v = np.array([-v3 / 2, -v3 / 2, v3])
        T = 6.32591398
        N = 1600
        dt = T / N

        def acc(x):
            a = np.zeros_like(x)
            for i in range(3):
                for j in range(3):
                    if i != j:
                        d = x[j] - x[i]
                        a[i] += d / np.linalg.norm(d) ** 3
            return a

        tray = [x.copy()]
        for _ in range(N):
            k1v = acc(x); k1x = v
            k2v = acc(x + dt / 2 * k1x); k2x = v + dt / 2 * k1v
            k3v = acc(x + dt / 2 * k2x); k3x = v + dt / 2 * k2v
            k4v = acc(x + dt * k3x); k4x = v + dt * k3v
            x = x + dt / 6 * (k1x + 2 * k2x + 2 * k3x + k4x)
            v = v + dt / 6 * (k1v + 2 * k2v + 2 * k3v + k4v)
            tray.append(x.copy())
        tray = np.array(tray)
        esc = 3.6
        rot = lambda p: np.array([p[1] * esc, p[0] * esc * 1.25, 0]) + UP * 0.3  # vertical
        s = ValueTracker(0)
        cols = [WHITE, GRAV, "#FF8A5C"]
        for i in range(3):
            pos = (lambda i: lambda: rot(tray[int(min(s.get_value(), 0.9999) * N), i]))(i)
            self.add(TracedPath(pos, stroke_color=cols[i], stroke_width=3.5, dissipating_time=1.1))
            self.add(always_redraw((lambda p, c: lambda: punto_brillante(p(), c, 0.1))(pos, cols[i])))
        lab = eq(r"\ddot{\mathbf r}_i=\sum_{j\neq i}\frac{Gm_j(\mathbf r_j-\mathbf r_i)}{|\mathbf r_j-\mathbf r_i|^3}", 44).move_to(DOWN * 5.4)
        self.play(s.animate.set_value(1), FadeIn(lab), run_time=self.duracion, rate_func=linear)


class PozoGravitatorio(Toma):
    def construct(self):
        phi = ValueTracker(0.3)
        el = 0.5

        def proy(x, y, z):
            a = phi.get_value()
            X = x * np.cos(a) - y * np.sin(a)
            Yd = x * np.sin(a) + y * np.cos(a)
            return np.array([X, z * np.cos(el) + Yd * np.sin(el), 0]) * 1.0 + DOWN * 0.2

        prof = lambda r: -2.6 / np.sqrt(r * r + 0.35)

        def malla():
            g = VGroup()
            for c in np.linspace(-4, 4, 17):
                l1 = VMobject().set_points_smoothly([proy(c, y, prof(np.hypot(c, y)) + 1.6) for y in np.linspace(-4, 4, 60)])
                l2 = VMobject().set_points_smoothly([proy(x, c, prof(np.hypot(x, c)) + 1.6) for x in np.linspace(-4, 4, 60)])
                op = 0.2 + 0.5 * (1 - abs(c) / 4)
                g.add(l1.set_stroke(GRAV, 1.6, op), l2.set_stroke(GRAV, 1.6, op))
            ang = phi.get_value() * 3.2
            r0 = 1.6
            g.add(punto_brillante(proy(r0 * np.cos(ang), r0 * np.sin(ang), prof(r0) + 1.6), WHITE, 0.09))
            g.add(punto_brillante(proy(0, 0, prof(0) + 1.6), GRAV, 0.22))
            return g

        m = always_redraw(malla)
        self.add(m)
        ein = eq(r"G_{\mu\nu}+\Lambda g_{\mu\nu}=\frac{8\pi G}{c^4}T_{\mu\nu}", 50).move_to(UP * 5.0)
        self.play(phi.animate.set_value(0.3 + 2.4), FadeIn(ein, shift=DOWN * 0.2), run_time=self.duracion, rate_func=linear)


# ---------------------------------------------------------------------------
# EDO y sistemas dinámicos
# ---------------------------------------------------------------------------
class Lorenz(Toma):
    duracion = 5.0

    def construct(self):
        s, r, b = 10.0, 28.0, 8 / 3
        p = np.array([0.1, 0.0, 0.0])
        pts = []
        dt = 0.005
        for _ in range(7000):
            x, y, z = p
            d = np.array([s * (y - x), x * (r - z) - y, x * y - b * z])
            p = p + dt * d
            pts.append(p.copy())
        pts = np.array(pts[300:])
        phi = ValueTracker(0)
        k = ValueTracker(0.02)

        def curva():
            a = phi.get_value()
            n = int(len(pts) * k.get_value())
            q = pts[:n:3]
            X = (q[:, 0] * np.cos(a) - q[:, 1] * np.sin(a)) * 0.17
            Y = (q[:, 2] - 25) * 0.24
            m = VMobject(stroke_width=2.4).set_points_as_corners(np.c_[X, Y, np.zeros_like(X)])
            m.set_color([EDOC, "#FF8A5C", GRAV, MARFIL])
            return m

        c = always_redraw(curva)
        self.add(c)
        eqs = eq(r"\dot x=\sigma(y-x),\ \ \dot y=x(\rho-z)-y,\ \ \dot z=xy-\beta z", 34).move_to(DOWN * 6.0)
        self.play(k.animate.set_value(1), phi.animate.set_value(1.6), FadeIn(eqs), run_time=self.duracion, rate_func=smooth)


class PenduloFase(Toma):
    def construct(self):
        sx, sy = 1.25, 1.55
        sep = VGroup()
        for sg in (1, -1):
            th = np.linspace(-2 * PI, 2 * PI, 300)
            sep.add(VMobject().set_points_smoothly([[sx * t / 1.6, sg * sy * 2 * np.cos(t / 2), 0] for t in th]))
        sep.set_stroke(EDOC, 3)
        rng = np.random.default_rng(9)
        estado = [np.array([rng.uniform(-6, 6), rng.uniform(-2.6, 2.6)]) for _ in range(90)]
        flujo = VGroup(*[Line(ORIGIN, RIGHT * 0.01) for _ in estado])

        def avanzar(g, dt):
            for i, l in enumerate(g):
                th, w = estado[i]
                for _ in range(3):
                    h = dt / 3
                    w = w - np.sin(th) * h
                    th = th + w * h
                if th > 6.4:
                    th -= 4 * PI
                if th < -6.4:
                    th += 4 * PI
                estado[i] = np.array([th, w])
                cola = np.array([th - 0.25 * w, w + 0.25 * np.sin(th)])
                l.put_start_and_end_on([sx * cola[0] / 1.6, sy * cola[1], 0], [sx * th / 1.6, sy * w, 0])
                l.set_stroke(interpolate_color(ManimColor(MARFIL), ManimColor(EDOC), min(abs(w) / 2.5, 1)), 3)

        avanzar(flujo, 0)
        flujo.add_updater(avanzar)
        self.add(sep, flujo)
        lab = eq(r"\ddot\theta+\frac gl\sin\theta=0", 58).move_to(DOWN * 5.3)
        self.play(FadeIn(lab, shift=UP * 0.2), run_time=0.6)
        self.esperar_resto()


# ---------------------------------------------------------------------------
# Variable compleja y exponenciales complejas
# ---------------------------------------------------------------------------
class Euler(Toma):
    def construct(self):
        c0 = UP * 2.2
        R = 1.8
        circ = Circle(radius=R).move_to(c0).set_stroke(MARFIL, 1.5, 0.45)
        th = ValueTracker(0)

        def fasor():
            a = th.get_value()
            tip = c0 + R * np.array([np.cos(a), np.sin(a), 0])
            g = VGroup(Line(c0, tip, stroke_width=5, color=COMP), punto_brillante(tip, COMP, 0.08),
                       DashedLine(tip, [tip[0], c0[1] - R - 0.4, 0], stroke_width=1.5, color=MARFIL).set_opacity(0.5))
            xs = np.linspace(0, a, max(int(a * 20), 2))
            onda = VMobject().set_points_smoothly([[c0[0] + R * np.cos(v), c0[1] - R - 0.4 - (a - v) * 0.55, 0] for v in xs])
            g.add(onda.set_stroke(COMP, 3))
            return g

        f = always_redraw(fasor)
        self.add(circ, f)
        lab = eq(r"e^{i\theta}=\cos\theta+i\sin\theta", 50).move_to(UP * 5.2)
        self.play(th.animate.set_value(TAU + PI), FadeIn(lab), run_time=2.8, rate_func=smooth)
        final = eq(r"e^{i\pi}+1=0", 96).move_to(DOWN * 4.8)
        self.play(FadeIn(final, scale=1.25), run_time=0.5)
        self.esperar_resto()


class Fourier(Toma):
    duracion = 5.0

    def construct(self):
        glifo = MathTex(r"\psi", font_size=700).move_to(UP * 0.4)
        trazo = max(glifo.family_members_with_points(), key=lambda m: len(m.points))
        N = 512
        pts = np.array([trazo.point_from_proportion(i / N) for i in range(N)])
        z = pts[:, 0] + 1j * pts[:, 1]
        C = np.fft.fft(z) / N
        freqs = np.fft.fftfreq(N, 1 / N)
        orden = np.argsort(-np.abs(C))[:70]
        t = ValueTracker(0)

        def cadena():
            tt = t.get_value()
            p = 0j
            g = VGroup()
            for k in orden:
                q = p + C[k] * np.exp(2j * np.pi * freqs[k] * tt)
                r = abs(C[k])
                if r > 0.02:
                    g.add(Circle(radius=r, stroke_width=1, color=MARFIL).set_stroke(opacity=0.3).move_to([p.real, p.imag, 0]))
                g.add(Line([p.real, p.imag, 0], [q.real, q.imag, 0], stroke_width=1.6, color=MARFIL).set_opacity(0.7))
                p = q
            g.add(punto_brillante([p.real, p.imag, 0], COMP, 0.06))
            return g, p

        cad = always_redraw(lambda: cadena()[0])
        punta = lambda: np.array([cadena()[1].real, cadena()[1].imag, 0])
        traza = TracedPath(punta, stroke_color=COMP, stroke_width=4)
        self.add(cad, traza)
        lab = eq(r"f(t)=\sum_n c_n\,e^{2\pi i n t}", 54).move_to(DOWN * 5.6)
        self.play(t.animate.set_value(1.0), FadeIn(lab), run_time=self.duracion - 0.2, rate_func=linear)


class Conforme(Toma):
    def construct(self):
        plano = ComplexPlane(x_range=[-2.2, 2.2, 0.25], y_range=[-2.2, 2.2, 0.25], x_length=7.6, y_length=7.6,
                             background_line_style={"stroke_color": COMP, "stroke_width": 1.6, "stroke_opacity": 0.6},
                             axis_config={"stroke_color": MARFIL, "stroke_width": 2})
        plano.move_to(UP * 0.2)
        plano.prepare_for_nonlinear_transform(60)
        lab = eq(r"w=z^2", 70).move_to(DOWN * 5.3)
        self.add(plano)
        self.play(FadeIn(lab), run_time=0.4)
        self.play(plano.animate.apply_complex_function(lambda z: z * z / 2.6), run_time=2.6, rate_func=smooth)
        self.esperar_resto()


# ---------------------------------------------------------------------------
# Ondas y óptica
# ---------------------------------------------------------------------------
class Prisma(Toma):
    def construct(self):
        L = 4.2
        c = np.array([0, 0.3, 0])
        P = [c + L * np.array([np.cos(a), np.sin(a), 0]) / np.sqrt(3) for a in (PI / 2, PI / 2 + TAU / 3, PI / 2 + 2 * TAU / 3)]
        pr = Polygon(*P, stroke_width=3, color=MARFIL).set_fill(WHITE, 0.04)
        entrada = (P[0] + P[1]) / 2 + np.array([0.05, -0.2, 0])
        origen = entrada + np.array([-4.5, -1.7, 0])
        haz = Line(origen, entrada, stroke_width=6, color=WHITE)
        salida = (P[0] + P[2]) / 2
        interno = VGroup(*[Line(entrada, salida + np.array([0, -0.22 + 0.07 * k, 0]), stroke_width=2, color=c_)
                           for k, c_ in enumerate(ESPECTRO)]).set_opacity(0.55)
        fan = VGroup()
        for k, c_ in enumerate(ESPECTRO):
            a = -0.55 - 0.085 * (6 - k)
            p0 = salida + np.array([0, -0.22 + 0.07 * k, 0])
            fan.add(Line(p0, p0 + 6 * np.array([np.cos(a), np.sin(a), 0]), stroke_width=5, color=c_))
        self.add(pr)
        self.play(Create(haz), run_time=0.8, rate_func=linear)
        self.play(Create(interno), run_time=0.4, rate_func=linear)
        self.play(LaggedStart(*[Create(f) for f in fan], lag_ratio=0.08), run_time=1.0)
        lab = eq(r"n_1\sin\theta_1=n_2\sin\theta_2", 52).move_to(DOWN * 5.2)
        self.play(FadeIn(lab), *[f.animate.set_stroke(width=7) for f in fan], run_time=0.6)
        self.esperar_resto()


class Estacionarias(Toma):
    def construct(self):
        t = ValueTracker(0)
        ys = [3.3, 1.1, -1.1, -3.3]

        def cuerdas():
            g = VGroup()
            for n, y0 in enumerate(ys, start=1):
                x = np.linspace(-3.6, 3.6, 200)
                y = 0.75 * np.sin(n * np.pi * (x + 3.6) / 7.2) * np.cos(n * 2.2 * t.get_value())
                c = interpolate_color(ManimColor(ELEC), ManimColor(CUANT), (n - 1) / 3)
                g.add(VMobject(stroke_width=4, stroke_color=c).set_points_smoothly([[a, y0 + b, 0] for a, b in zip(x, y)]))
                for k in range(n + 1):
                    g.add(Dot([-3.6 + 7.2 * k / n, y0, 0], radius=0.06, color=WHITE))
            return g

        cs = always_redraw(cuerdas)
        self.add(cs)
        lab = eq(r"\frac{\partial^2u}{\partial t^2}=c^2\frac{\partial^2u}{\partial x^2}", 54).move_to(DOWN * 5.6)
        self.play(t.animate.set_value(4), FadeIn(lab), run_time=self.duracion, rate_func=linear)


class Titulo(Toma):
    """Tarjeta de apertura."""
    duracion = 3.0

    def construct(self):
        t = Text("F Í S I C A", font="Inter Display", weight=LIGHT, font_size=110, color=MARFIL)
        s = Text("el universo, en ecuaciones", font="CMU Serif", slant=ITALIC, font_size=40, color=GRIS)
        s.next_to(t, DOWN, buff=0.5)
        l = Line(LEFT * 1.6, RIGHT * 1.6, stroke_width=1.5, color=MARFIL).next_to(s, DOWN, buff=0.5)
        self.play(FadeIn(t, scale=1.15), run_time=1.0)
        self.play(FadeIn(s, shift=UP * 0.15), GrowFromCenter(l), run_time=0.8)
        self.esperar_resto()


class Cierre(Toma):
    duracion = 3.0

    def construct(self):
        e = eq(r"e^{i\pi}+1=0", 120)
        self.play(FadeIn(e, scale=0.9), run_time=0.8)
        self.wait(2.2)


TOMAS = ["Titulo", "Maxwell", "Dipolo", "OndaEM", "Schrodinger", "AccionMinima", "Kepler", "TresCuerpos",
         "PozoGravitatorio", "Lorenz", "PenduloFase", "Euler", "Fourier", "Conforme", "Prisma", "Estacionarias", "Cierre"]


# ---------------------------------------------------------------------------
# Citas (se renderizan con fondo transparente: manim -t) y cierre
# ---------------------------------------------------------------------------
class _Cita(Scene):
    texto = ""
    autor = ""
    duracion = 5.0

    def construct(self):
        lineas = self.texto.split("\n")
        filas = VGroup(*[Text(l, font="CMU Serif", slant=ITALIC, font_size=50, color=MARFIL) for l in lineas])
        filas.arrange(DOWN, buff=0.32)
        if filas.width > 8.0:
            filas.width = 8.0
        comilla = Text("“", font="CMU Serif", font_size=150, color=MARFIL).set_opacity(0.35)
        comilla.next_to(filas, UP, buff=0.05).align_to(filas, LEFT).shift(LEFT * 0.15)
        autor = Text("—  " + "  ".join(self.autor.upper()), font="Inter", weight=LIGHT, font_size=24, color=MARFIL)
        autor.set_opacity(0.75).next_to(filas, DOWN, buff=0.7)
        bloque = VGroup(comilla, filas, autor).move_to(UP * 0.4)
        palabras = [w for fila in filas for w in fila]
        self.play(FadeIn(comilla, scale=0.9), run_time=0.3)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.08) for p in palabras], lag_ratio=0.04), run_time=1.6)
        self.play(FadeIn(autor), run_time=0.4)
        self.wait(max(self.duracion - 3.0, 0.2))
        self.play(FadeOut(bloque, shift=UP * 0.1), run_time=0.7)


class CitaFeynman(_Cita):
    texto = ("Nature uses only the longest threads\nto weave her patterns, so each small\n"
             "piece of her fabric reveals the\norganization of the entire tapestry.")
    autor = "Richard Feynman"


class CitaHeisenberg(_Cita):
    texto = "What we observe is not nature itself,\nbut nature exposed to our\nmethod of questioning."
    autor = "Werner Heisenberg"


class CitaSagan(_Cita):
    texto = "The cosmos is also within us.\nWe're made of star stuff.\nWe are a way for the cosmos\nto know itself."
    autor = "Carl Sagan"


class CitaCox(_Cita):
    texto = "We are the cosmos made conscious,\nand life is the means by which\nthe universe understands itself."
    autor = "Brian Cox"


class Elegante(Toma):
    duracion = 4.0

    def construct(self):
        t = Text("Science is elegant.", font="CMU Serif", slant=ITALIC, font_size=84, color=MARFIL)
        t.width = min(t.width, 7.4)
        l = Line(LEFT * 1.4, RIGHT * 1.4, stroke_width=1.2, color=MARFIL).set_opacity(0.6).next_to(t, DOWN, buff=0.55)
        self.play(FadeIn(t, shift=UP * 0.15), run_time=1.4)
        self.play(GrowFromCenter(l), run_time=0.8)
        self.wait(1.2)
        self.play(FadeOut(VGroup(t, l)), run_time=0.6)


CITAS = ["CitaFeynman", "CitaHeisenberg", "CitaSagan", "CitaCox"]
TOMAS = TOMAS + ["Elegante"]
