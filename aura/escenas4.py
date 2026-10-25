"""Tomas animadas del cuarto edit (mecánica clásica) y palabras con transparencia."""

from escenas import *  # noqa: F401,F403

ACERO = "#9EC5FF"
COBRE = "#F0A878"
MENTA = "#7CFFCB"
ROSA = "#FF6B9A"
G = 9.8


def resorte(a, b, espiras=9, ancho=0.32, color=MARFIL, grosor=3):
    a, b = np.array(a, dtype=float), np.array(b, dtype=float)
    d = b - a
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0], 0])
    pts = [a, a + u * L * 0.1]
    for k in range(2 * espiras):
        pts.append(a + u * L * (0.1 + 0.8 * (k + 0.5) / (2 * espiras)) + n * ancho * (1 if k % 2 == 0 else -1))
    pts += [a + u * L * 0.9, b]
    return VMobject(stroke_width=grosor, stroke_color=color).set_points_as_corners(pts)


def flecha(a, b, color, ancho=5):
    return Arrow(a, b, buff=0, stroke_width=ancho, color=color, max_tip_length_to_length_ratio=0.22,
                 max_stroke_width_to_length_ratio=20)


def rk4(f, y, dt, n):
    out = [y.copy()]
    for _ in range(n):
        k1 = f(y); k2 = f(y + dt / 2 * k1); k3 = f(y + dt / 2 * k2); k4 = f(y + dt * k3)
        y = y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        out.append(y.copy())
    return np.array(out)


# ---------------------------------------------------------------------------
# I. Newton y sistemas de partículas
# ---------------------------------------------------------------------------
class PlanoInclinado(Toma):
    def construct(self):
        ang = np.radians(30)
        A, B = np.array([-4.2, -3.2, 0]), np.array([4.2, -3.2, 0])
        C = A + np.array([8.4, 8.4 * np.tan(ang), 0])
        rampa = Polygon(A, B, C, stroke_width=2, color=MARFIL).set_fill(MARFIL, 0.04)
        u = (A - C) / np.linalg.norm(A - C)
        nrm = np.array([-u[1], u[0], 0]) * -1
        if nrm[1] < 0:
            nrm = -nrm
        s = ValueTracker(0.6)

        def escena():
            p = C + u * s.get_value() + nrm * 0.42
            caja = Square(0.8).rotate(-ang + PI).move_to(p).set_stroke(ACERO, 3).set_fill(ACERO, 0.15)
            g = VGroup(caja)
            g.add(flecha(p, p + DOWN * 2.0, COBRE), flecha(p, p + nrm * 2.0 * np.cos(ang), ACERO),
                  flecha(p, p - u * 0.75, ROSA), flecha(p, p + u * 1.0, WHITE, 3).set_opacity(0.7))
            return g

        self.add(rampa, always_redraw(escena))
        lab = VGroup(eq(r"m\mathbf g", 40, COBRE), eq(r"\mathbf N", 40, ACERO), eq(r"\mathbf f_r", 40, ROSA)).arrange(RIGHT, buff=0.8)
        lab.move_to(UP * 5.6)
        ley = eq(r"m\,\mathbf a=\sum\mathbf F", 66).move_to(DOWN * 5.4)
        self.add(lab)
        self.play(s.animate.set_value(8.5), FadeIn(ley), run_time=self.duracion, rate_func=lambda t: t * t)


class Explosion(Toma):
    def construct(self):
        rng = np.random.default_rng(3)
        v0 = np.array([2.4, 7.2])
        p0 = np.array([-3.6, -5.5])
        g = np.array([0, -G * 0.55])
        te = 1.1
        n = 26
        dv = rng.normal(0, 1.6, (n, 2))
        dv -= dv.mean(0)
        masas = rng.uniform(0.5, 1.5, n)
        dv -= (masas[:, None] * dv).sum(0) / masas.sum()
        t = ValueTracker(0)

        def cm(tt):
            return p0 + v0 * tt + 0.5 * g * tt * tt

        def escena():
            tt = t.get_value()
            grp = VGroup()
            if tt < te:
                grp.add(punto_brillante([*cm(tt), 0], WHITE, 0.14))
            else:
                k = tt - te
                pe, ve = cm(te), v0 + g * te
                for i in range(n):
                    q = pe + (ve + dv[i]) * k + 0.5 * g * k * k
                    c = interpolate_color(ManimColor(COBRE), ManimColor(ACERO), i / n)
                    grp.add(Dot([*q, 0], radius=0.05 + 0.04 * masas[i], color=c))
                grp.add(punto_brillante([*cm(tt), 0], MENTA, 0.1))
            return grp

        traza = VMobject().set_points_smoothly([[*cm(x), 0] for x in np.linspace(0, 2.6, 60)])
        traza = DashedVMobject(traza, num_dashes=40).set_stroke(MENTA, 2, 0.6)
        self.add(always_redraw(escena))
        lab = eq(r"M\,\ddot{\mathbf R}_{cm}=\mathbf F_{ext}", 60).move_to(DOWN * 6.2)
        self.play(t.animate.set_value(te), run_time=1.3, rate_func=linear)
        self.play(t.animate.set_value(2.6), Create(traza), FadeIn(lab), run_time=self.duracion - 1.3, rate_func=linear)


class Rodadura(Toma):
    def construct(self):
        R = 1.2
        suelo = Line(LEFT * 5, RIGHT * 5, stroke_width=2, color=MARFIL).shift(DOWN * 1.2)
        x = ValueTracker(-4.0)

        def rueda():
            xc = x.get_value()
            c = np.array([xc, -1.2 + R, 0])
            phi = -(xc + 4.0) / R
            g = VGroup(Circle(radius=R).move_to(c).set_stroke(MARFIL, 3))
            for k in range(6):
                a = phi + k * TAU / 6
                g.add(Line(c, c + R * np.array([np.sin(a), np.cos(a), 0]), stroke_width=1.5, color=MARFIL).set_opacity(0.5))
            contacto = np.array([xc, -1.2, 0])
            for k in range(8):
                a = phi + k * TAU / 8
                p = c + R * np.array([np.sin(a), np.cos(a), 0])
                r = p - contacto
                v = np.array([r[1], -r[0], 0]) * 0.55
                g.add(flecha(p, p + v, ACERO, 3).set_opacity(0.8))
            punta = c + R * np.array([np.sin(phi), np.cos(phi), 0])
            g.add(punto_brillante(punta, COBRE, 0.08), punto_brillante(c, WHITE, 0.06))
            return g

        punta = lambda: np.array([x.get_value(), -1.2 + R, 0]) + R * np.array(
            [np.sin(-(x.get_value() + 4) / R), np.cos(-(x.get_value() + 4) / R), 0])
        self.add(suelo, TracedPath(punta, stroke_color=COBRE, stroke_width=4), always_redraw(rueda))
        lab = eq(r"T=\tfrac12Mv_{cm}^2+\tfrac12I_{cm}\omega^2", 52).move_to(DOWN * 5.0)
        self.play(x.animate.set_value(4.0), FadeIn(lab), run_time=self.duracion, rate_func=linear)


class Steiner(Toma):
    def construct(self):
        L = 6.0
        d = ValueTracker(0.0)
        th = ValueTracker(0.0)
        piv = UP * 0.8

        def escena():
            dd = d.get_value()
            a = th.get_value()
            u = np.array([np.cos(a), np.sin(a), 0])
            centro = piv + u * dd
            barra = Line(centro - u * L / 2, centro + u * L / 2, stroke_width=14, color=ACERO)
            circ = Circle(radius=dd).move_to(piv).set_stroke(COBRE, 1.5, 0.4) if dd > 0.05 else VGroup()
            I = 1 / 12 + (dd / L) ** 2
            lect = eq(r"\frac{I}{ML^2}=%.3f" % I, 48, COBRE).move_to(DOWN * 4.0)
            return VGroup(circ, barra, punto_brillante(centro, WHITE, 0.07), punto_brillante(piv, COBRE, 0.1), lect)

        def girar(m, dt):
            I = 1 / 12 + (d.get_value() / L) ** 2
            th.increment_value(dt * 1.6 / np.sqrt(I * 12))

        e = always_redraw(escena)
        motor = Mobject()
        motor.add_updater(girar)
        self.add(e, motor)
        lab = eq(r"I=I_{cm}+Md^2", 66).move_to(DOWN * 5.6)
        self.play(FadeIn(lab), run_time=0.5)
        self.play(d.animate.set_value(L / 2), run_time=self.duracion - 0.5, rate_func=smooth)


class Patinadora(Toma):
    def construct(self):
        r = ValueTracker(3.2)
        th = ValueTracker(0.0)
        c = UP * 0.8
        L0 = 3.2 ** 2

        def escena():
            rr = r.get_value()
            a = th.get_value()
            u = np.array([np.cos(a), np.sin(a) * 0.45, 0])
            g = VGroup(Ellipse(width=2 * rr, height=0.9 * rr).move_to(c).set_stroke(MARFIL, 1, 0.3))
            g.add(Line(c - u * rr, c + u * rr, stroke_width=3, color=MARFIL))
            g.add(punto_brillante(c + u * rr, COBRE, 0.16), punto_brillante(c - u * rr, COBRE, 0.16))
            g.add(flecha(c, c + UP * (0.6 + 2.4 * L0 / (rr * rr) / 10.5), ACERO, 6))
            g.add(eq(r"\omega=%.1f" % (L0 / rr ** 2), 44, ACERO).move_to(DOWN * 3.6))
            return g

        motor = Mobject()
        motor.add_updater(lambda m, dt: th.increment_value(dt * 2.2 * L0 / r.get_value() ** 2))
        self.add(always_redraw(escena), motor)
        lab = eq(r"\mathbf L=I\boldsymbol\omega=\text{cte}", 62).move_to(DOWN * 5.4)
        self.play(FadeIn(lab), run_time=0.6)
        self.play(r.animate.set_value(1.0), run_time=2.6, rate_func=smooth)
        self.esperar_resto()


# ---------------------------------------------------------------------------
# II. Oscilaciones
# ---------------------------------------------------------------------------
class TresRegimenes(Toma):
    def construct(self):
        t = ValueTracker(0)
        def x_sub(tt): return np.exp(-0.35 * tt) * np.cos(2.6 * tt)
        def x_cri(tt): return (1 + 2.6 * tt) * np.exp(-2.6 * tt)
        def x_sob(tt):
            l1, l2 = -0.6, -11.2
            return (l2 * np.exp(l1 * tt) - l1 * np.exp(l2 * tt)) / (l2 - l1)
        funcs = [(x_sub, ACERO), (x_cri, COBRE), (x_sob, ROSA)]
        techo = 5.6
        ejes = Axes(x_range=[0, 6, 1], y_range=[-1.1, 1.1, 1], x_length=7.6, y_length=3.4,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.4, "include_ticks": False}).move_to(DOWN * 3.6)

        def escena():
            tt = t.get_value()
            g = VGroup(Line([-3.6, techo, 0], [3.6, techo, 0], stroke_width=3, color=MARFIL))
            for k, (f, c) in enumerate(funcs):
                xk = -2.6 + 2.6 * k
                y = 1.6 + 1.3 * f(tt)
                g.add(resorte([xk, techo, 0], [xk, y + 0.35, 0], color=c),
                      Square(0.7).move_to([xk, y, 0]).set_stroke(c, 3).set_fill(c, 0.25))
                xs = np.linspace(0, tt, max(int(tt * 40), 2))
                g.add(VMobject().set_points_smoothly([ejes.c2p(a, f(a)) for a in xs]).set_stroke(c, 4))
            return g

        self.add(ejes, always_redraw(escena))
        lab = eq(r"\ddot x+2\gamma\dot x+\omega_0^2x=0", 52).move_to(DOWN * 6.2)
        self.play(t.animate.set_value(6), FadeIn(lab), run_time=self.duracion, rate_func=linear)


class Pohl(Toma):
    def construct(self):
        w0, gam = 1.0, 0.09
        Om = ValueTracker(0.45)
        fase = ValueTracker(0)
        A = lambda W: 0.22 / np.sqrt((w0 ** 2 - W ** 2) ** 2 + 4 * gam ** 2 * W ** 2)
        dl = lambda W: np.arctan2(2 * gam * W, w0 ** 2 - W ** 2)
        c = UP * 2.6
        ejes = Axes(x_range=[0.4, 1.6, 0.2], y_range=[0, 1.35, 0.5], x_length=7.4, y_length=3.0,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.4, "include_ticks": False}).move_to(DOWN * 3.3)
        curva = ejes.plot(lambda W: A(W), x_range=[0.4, 1.6, 0.005], stroke_width=4, color=COBRE)

        def escena():
            W = Om.get_value()
            ang = A(W) * np.cos(fase.get_value() - dl(W)) * 1.4
            g = VGroup(Circle(radius=2.0).move_to(c).set_stroke(ACERO, 4).set_fill(ACERO, 0.05))
            for k in range(8):
                a = ang + k * TAU / 8
                g.add(Line(c, c + 2.0 * np.array([np.sin(a), np.cos(a), 0]), stroke_width=1.5, color=ACERO).set_opacity(0.4))
            g.add(Line(c, c + 2.5 * np.array([np.sin(ang), np.cos(ang), 0]), stroke_width=5, color=WHITE))
            esp = VMobject().set_points_smoothly([c + (0.12 + 0.03 * s) * np.array([np.cos(s + ang), np.sin(s + ang), 0])
                                                  for s in np.linspace(0, 5 * TAU, 160)]).set_stroke(COBRE, 2)
            exc = np.array([0.35 * np.cos(fase.get_value()), 0.35 * np.sin(fase.get_value()), 0])
            g.add(esp, Line(c + RIGHT * 3.0 + exc, c + RIGHT * 2.1, stroke_width=3, color=MARFIL).set_opacity(0.6),
                  Circle(radius=0.35).move_to(c + RIGHT * 3.0).set_stroke(MARFIL, 1.5, 0.5))
            g.add(punto_brillante(ejes.c2p(W, A(W)), WHITE, 0.08))
            return g

        motor = Mobject()
        motor.add_updater(lambda m, dt: fase.increment_value(dt * 9 * Om.get_value()))
        self.add(ejes, curva, always_redraw(escena), motor)
        lab = eq(r"A(\Omega)=\frac{F_0/I}{\sqrt{(\omega_0^2-\Omega^2)^2+4\gamma^2\Omega^2}}", 40).move_to(DOWN * 6.0)
        self.play(FadeIn(lab), run_time=0.4)
        self.play(Om.animate.set_value(1.55), run_time=self.duracion - 0.4, rate_func=smooth)


class Acoplados(Toma):
    def construct(self):
        t = ValueTracker(0)
        wbar, dw = 5.0, 0.55
        th1 = lambda tt: 0.45 * np.cos(dw * tt) * np.cos(wbar * tt)
        th2 = lambda tt: 0.45 * np.sin(dw * tt) * np.sin(wbar * tt)
        L = 4.2
        s1, s2 = np.array([-1.6, 5.2, 0]), np.array([1.6, 5.2, 0])
        ejes = Axes(x_range=[0, 6, 1], y_range=[-0.5, 0.5, 0.5], x_length=7.6, y_length=2.4,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.4, "include_ticks": False}).move_to(DOWN * 3.9)

        def escena():
            tt = t.get_value()
            p1 = s1 + L * np.array([np.sin(th1(tt)), -np.cos(th1(tt)), 0])
            p2 = s2 + L * np.array([np.sin(th2(tt)), -np.cos(th2(tt)), 0])
            q1, q2 = s1 + (p1 - s1) * 0.55, s2 + (p2 - s2) * 0.55
            g = VGroup(Line(s1 + LEFT, s2 + RIGHT, stroke_width=3, color=MARFIL), Line(s1, p1, stroke_width=2, color=MARFIL),
                       Line(s2, p2, stroke_width=2, color=MARFIL), resorte(q1, q2, espiras=7, ancho=0.18, color=MENTA, grosor=2),
                       punto_brillante(p1, ACERO, 0.22), punto_brillante(p2, COBRE, 0.22))
            xs = np.linspace(0, tt, max(int(tt * 60), 2))
            g.add(VMobject().set_points_smoothly([ejes.c2p(a, th1(a)) for a in xs]).set_stroke(ACERO, 2.5))
            g.add(VMobject().set_points_smoothly([ejes.c2p(a, th2(a)) for a in xs]).set_stroke(COBRE, 2.5))
            return g

        self.add(ejes, always_redraw(escena))
        lab = eq(r"\omega_\pm^2=\frac gl,\ \frac gl+\frac{2k}{m}", 46).move_to(DOWN * 6.0)
        self.play(t.animate.set_value(6), FadeIn(lab), run_time=self.duracion, rate_func=linear)


class Lissajous(Toma):
    def construct(self):
        t = ValueTracker(0)
        R = 3.3
        def punto(tt, d):
            e = np.exp(-0.035 * tt)
            return np.array([R * np.sin(3 * tt + d) * e, 1.3 * R * np.sin(2 * tt) * e, 0]) + UP * 0.6

        def curva():
            tt = t.get_value()
            xs = np.linspace(0, tt, max(int(tt * 30), 2))
            d = 0.3 + 0.02 * tt
            m = VMobject().set_points_smoothly([punto(a, d) for a in xs])
            m.set_stroke(width=2.5).set_color([ACERO, MENTA, COBRE, ROSA])
            return VGroup(m, punto_brillante(punto(tt, d), WHITE, 0.07))

        self.add(always_redraw(curva))
        lab = eq(r"x=A\sin(3t+\delta),\quad y=B\sin(2t)", 48).move_to(DOWN * 5.7)
        self.play(t.animate.set_value(26), FadeIn(lab), run_time=self.duracion, rate_func=linear)


# ---------------------------------------------------------------------------
# III. Lagrange y Hamilton
# ---------------------------------------------------------------------------
class Liouville(Toma):
    def construct(self):
        sx, sy = 1.15, 1.2
        c = UP * 0.4
        nivel = VGroup()
        for E in [-0.7, -0.3, 0.2, 0.6, 1.0, 1.4, 2.0]:
            for sg in (1, -1):
                th = np.linspace(-PI, PI, 200)
                p2 = 2 * (E + np.cos(th))
                ok = p2 >= 0
                pts = [c + [sx * a, sg * sy * np.sqrt(b), 0] for a, b in zip(th[ok], p2[ok])]
                if len(pts) > 2:
                    nivel.add(VMobject().set_points_smoothly(pts).set_stroke(MARFIL, 1.2, 0.25))
        rng = np.random.default_rng(2)
        n = 700
        r = np.sqrt(rng.uniform(0, 1, n)) * 0.35
        a = rng.uniform(0, TAU, n)
        est = np.c_[-1.9 + r * np.cos(a), 0.0 + r * np.sin(a)]
        cols = [interpolate_color(ManimColor(MENTA), ManimColor(ROSA), (np.cos(x) + 1) / 2) for x in a]
        puntos = VGroup(*[Dot(radius=0.025, color=cl) for cl in cols])

        def avanzar(g, dt):
            nonlocal est
            h = dt * 1.6 / 4
            for _ in range(4):
                est[:, 1] -= h / 2 * np.sin(est[:, 0])
                est[:, 0] += h * est[:, 1]
                est[:, 1] -= h / 2 * np.sin(est[:, 0])
            for i, d in enumerate(g):
                d.move_to(c + [sx * ((est[i, 0] + PI) % TAU - PI), sy * est[i, 1], 0])

        avanzar(puntos, 0)
        puntos.add_updater(avanzar)
        self.add(nivel, puntos)
        top = eq(r"\frac{d}{dt}\frac{\partial L}{\partial\dot q}-\frac{\partial L}{\partial q}=0", 52).move_to(UP * 5.4)
        bot = eq(r"\dot q=\frac{\partial H}{\partial p},\qquad \dot p=-\frac{\partial H}{\partial q}", 52, MENTA).move_to(DOWN * 5.0)
        self.play(FadeIn(top), run_time=0.6)
        self.play(FadeIn(bot), run_time=0.6)
        self.esperar_resto()


# ---------------------------------------------------------------------------
# IV. Máquinas, masa variable, colisiones y Galileo
# ---------------------------------------------------------------------------
class Atwood(Toma):
    def construct(self):
        R = 1.0
        c = UP * 5.0
        m1, m2 = 3.0, 2.0
        a = (m1 - m2) * G / (m1 + m2 + 1.0) * 0.18
        t = ValueTracker(0)

        def escena():
            y = 0.5 * a * t.get_value() ** 2
            phi = -y / R
            g = VGroup(Line(c + UP * 1.4, c, stroke_width=3, color=MARFIL), Line(c + UP * 1.4 + LEFT * 2, c + UP * 1.4 + RIGHT * 2, stroke_width=4, color=MARFIL))
            g.add(Circle(radius=R).move_to(c).set_stroke(ACERO, 3).set_fill(ACERO, 0.06))
            for k in range(6):
                ang = phi + k * TAU / 6
                g.add(Line(c, c + R * np.array([np.cos(ang), np.sin(ang), 0]), stroke_width=1.5, color=ACERO).set_opacity(0.5))
            y1, y2 = -1.0 - y, -1.0 + y
            g.add(Line(c + LEFT * R, [-R, y1 + 0.55, 0] + 0 * c, stroke_width=2.5, color=MARFIL),
                  Line(c + RIGHT * R, [R, y2 + 0.45, 0], stroke_width=2.5, color=MARFIL))
            g.add(Square(1.1).move_to([-R, y1, 0]).set_stroke(COBRE, 3).set_fill(COBRE, 0.25),
                  Square(0.9).move_to([R, y2, 0]).set_stroke(MENTA, 3).set_fill(MENTA, 0.25))
            g.add(eq("m_1", 34).move_to([-R, y1, 0]), eq("m_2", 30).move_to([R, y2, 0]))
            return g

        self.add(always_redraw(escena))
        lab = eq(r"a=\frac{(m_1-m_2)\,g}{m_1+m_2+I/R^2}", 54).move_to(DOWN * 5.6)
        self.play(t.animate.set_value(3.2), FadeIn(lab), run_time=self.duracion, rate_func=linear)


class Cohete(Toma):
    def construct(self):
        rng = np.random.default_rng(5)
        t = ValueTracker(0)
        u, m0, k = 2.2, 1.0, 0.16
        v = lambda tt: u * np.log(m0 / (m0 - k * tt))
        y = lambda tt: -2.5 + 0.55 * (u * ((m0 - k * tt) / k) * np.log((m0 - k * tt) / m0) + u * tt)
        gases = []
        humo = VGroup()

        def emitir(g, dt):
            tt = t.get_value()
            base = np.array([-1.6, y(tt) - 0.9, 0])
            for _ in range(5):
                gases.append([base.copy() + RIGHT * rng.normal(0, 0.08), np.array([rng.normal(0, 0.35), -u * 1.6 + rng.normal(0, 0.3), 0]), 0.0])
            for gas in gases:
                gas[0] = gas[0] + gas[1] * dt
                gas[2] += dt
            while len(gases) > 260:
                gases.pop(0)
            g.become(VGroup(*[Dot(p, radius=0.05 + 0.1 * e, color=interpolate_color(ManimColor(WHITE), ManimColor(COBRE), min(e * 2, 1)))
                              .set_opacity(max(0.9 - e * 1.1, 0)) for p, _, e in gases]))

        humo.add_updater(emitir)

        def nave():
            yy = y(t.get_value())
            cuerpo = Polygon([-1.95, yy - 0.8, 0], [-1.25, yy - 0.8, 0], [-1.25, yy + 0.9, 0], [-1.6, yy + 1.6, 0], [-1.95, yy + 0.9, 0],
                             stroke_width=3, color=MARFIL).set_fill(MARFIL, 0.12)
            return cuerpo

        ejes = Axes(x_range=[0, 5, 1], y_range=[0, 3.4, 1], x_length=4.4, y_length=4.6,
                    axis_config={"stroke_color": MARFIL, "stroke_opacity": 0.4, "include_ticks": False}).move_to(RIGHT * 2.0 + UP * 0.4)
        curva = always_redraw(lambda: VMobject().set_points_smoothly([ejes.c2p(a, v(a)) for a in np.linspace(0, max(t.get_value(), 0.01), 40)])
                              .set_stroke(MENTA, 4))
        self.add(humo, always_redraw(nave), ejes, curva, eq("v", 34, MENTA).next_to(ejes.c2p(0, 3.4), RIGHT, buff=0.1))
        lab = eq(r"\Delta v=u\ln\frac{m_0}{m_f}", 64).move_to(DOWN * 5.4)
        self.play(t.animate.set_value(5), FadeIn(lab), run_time=self.duracion, rate_func=linear)


class CunaNewton(Toma):
    def construct(self):
        r, L, techo = 0.5, 4.6, 4.0
        xs = [(-4 + 2 * k) * r for k in range(5)]
        t = ValueTracker(0)

        def escena():
            th = 0.6 * np.sin(4.2 * t.get_value())
            g = VGroup(Line([-3.6, techo, 0], [3.6, techo, 0], stroke_width=4, color=MARFIL))
            for k, x0 in enumerate(xs):
                a = th if (k == 0 and th < 0) or (k == 4 and th > 0) else 0.0
                piv = np.array([x0, techo, 0])
                p = piv + L * np.array([np.sin(a), -np.cos(a), 0])
                g.add(Line(piv, p, stroke_width=1.5, color=MARFIL))
                g.add(Circle(radius=r).move_to(p).set_stroke(ACERO, 2).set_fill([WHITE, ACERO], 0.85))
            return g

        self.add(always_redraw(escena))
        lab = VGroup(eq(r"\sum p_i=\text{cte}", 52), eq(r"\sum\tfrac12m v_i^2=\text{cte}", 52, COBRE)).arrange(DOWN, buff=0.4)
        lab.move_to(DOWN * 4.6)
        self.play(t.animate.set_value(self.duracion), FadeIn(lab), run_time=self.duracion, rate_func=linear)


class Colision2D(Toma):
    def construct(self):
        R = 0.55
        v = np.array([0, 2.4, 0])
        B0 = np.array([0, 1.0, 0])
        b = 0.62
        A0 = np.array([-b, -5.5, 0])
        tc = (np.linalg.norm(B0 - A0) * 0 + (B0[1] - A0[1] - np.sqrt((2 * R) ** 2 - b ** 2))) / v[1]
        n = (B0 - (A0 + v * tc)); n = n / np.linalg.norm(n)
        vA = v - np.dot(v, n) * n
        vB = np.dot(v, n) * n
        t = ValueTracker(0)

        def pos(tt):
            if tt < tc:
                return A0 + v * tt, B0
            k = tt - tc
            return A0 + v * tc + vA * k, B0 + vB * k

        def escena():
            pa, pb = pos(t.get_value())
            return VGroup(Circle(radius=R).move_to(pa).set_stroke(COBRE, 3).set_fill(COBRE, 0.3),
                          Circle(radius=R).move_to(pb).set_stroke(ACERO, 3).set_fill(ACERO, 0.3))

        self.add(TracedPath(lambda: pos(t.get_value())[0], stroke_color=COBRE, stroke_width=3),
                 TracedPath(lambda: pos(t.get_value())[1], stroke_color=ACERO, stroke_width=3), always_redraw(escena))
        self.play(t.animate.set_value(tc + 1.6), run_time=self.duracion - 1.0, rate_func=linear)
        pc = A0 + v * tc
        angulo = RightAngle(Line(pc, pc + vA), Line(pc, pc + vB * 0 + (B0 - pc)), length=0.4, color=WHITE)
        lab = eq(r"m_1=m_2\ \Rightarrow\ \mathbf v_1'\perp\mathbf v_2'", 52).move_to(DOWN * 6.0)
        self.play(Create(angulo), FadeIn(lab), run_time=1.0)


class Galileo(Toma):
    def construct(self):
        t = ValueTracker(0)
        V = 1.6
        g2 = 1.4
        T = 2.4

        def panel(y0, en_tren):
            tt = t.get_value() % T
            ancla = y0
            g = VGroup(Line([-4.5, ancla - 2.4, 0], [4.5, ancla - 2.4, 0], stroke_width=2, color=MARFIL))
            xt = -2.0 + V * tt if not en_tren else 0.0
            g.add(Rectangle(width=3.0, height=1.0).move_to([xt, ancla - 1.85, 0]).set_stroke(ACERO, 3).set_fill(ACERO, 0.1))
            for k in range(-6, 7):
                xp = k * 1.2 - (V * tt if en_tren else 0)
                if abs(xp) < 4.5:
                    g.add(Line([xp, ancla - 2.4, 0], [xp, ancla - 2.6, 0], stroke_width=2, color=MARFIL).set_opacity(0.6))
            xs = np.linspace(0, tt, max(int(tt * 40), 2))
            pts = [[(-2.0 + V * a if not en_tren else 0.0), ancla + 1.6 - g2 * a * a / 2 * 1.0, 0] for a in xs]
            g.add(VMobject().set_points_smoothly(pts).set_stroke(COBRE, 4))
            g.add(punto_brillante(pts[-1], WHITE, 0.1))
            return g

        self.add(always_redraw(lambda: panel(3.6, False)), always_redraw(lambda: panel(-2.2, True)))
        self.add(Line(LEFT * 4.5 + UP * 0.9, RIGHT * 4.5 + UP * 0.9, stroke_width=1, color=MARFIL).set_opacity(0.3))
        lab = eq(r"x'=x-vt,\qquad t'=t", 56).move_to(DOWN * 6.0)
        self.play(t.animate.set_value(T * 0.999), FadeIn(lab), run_time=self.duracion, rate_func=linear)


# ---------------------------------------------------------------------------
# V. Gravitación y caos
# ---------------------------------------------------------------------------
class Hodografa(Toma):
    def construct(self):
        e = 0.6
        a = 2.4
        c_orb = UP * 3.2
        def orb(th):
            r = a * (1 - e * e) / (1 + e * np.cos(th))
            return c_orb + np.array([r * np.cos(th) * 0.95, r * np.sin(th) * 0.95, 0]) + RIGHT * 1.2
        def vel(th):
            return np.array([-np.sin(th), e + np.cos(th), 0])
        c_hod = DOWN * 3.4
        M = ValueTracker(0)

        def th_de(Mv):
            E = Mv
            for _ in range(25):
                E = E - (E - e * np.sin(E) - Mv) / (1 - e * np.cos(E))
            return 2 * np.arctan2(np.sqrt(1 + e) * np.sin(E / 2), np.sqrt(1 - e) * np.cos(E / 2))

        orbita = VMobject().set_points_smoothly([orb(x) for x in np.linspace(0, TAU, 200)]).set_stroke(MARFIL, 1.5, 0.4)
        hod = Circle(radius=1.7).move_to(c_hod + UP * 1.7 * e).set_stroke(MARFIL, 1.5, 0.3)

        def escena():
            th = th_de(M.get_value())
            p = orb(th)
            w = vel(th) * 1.7
            return VGroup(punto_brillante(p, WHITE, 0.09), flecha(p, p + w * 0.6, MENTA, 4), flecha(c_hod, c_hod + w, MENTA, 5),
                          punto_brillante(c_hod + w, MENTA, 0.07))

        th0 = lambda: th_de(M.get_value())
        self.add(orbita, hod, punto_brillante(c_orb + RIGHT * 1.2, COBRE, 0.2),
                 TracedPath(lambda: c_hod + vel(th0()) * 1.7, stroke_color=MENTA, stroke_width=4), always_redraw(escena))
        lab = eq(r"\mathbf v=\frac{GM}{h}\big(\hat{\boldsymbol\theta}+e\,\hat{\mathbf y}\big)", 50).move_to(DOWN * 6.4)
        self.play(M.animate.set_value(TAU), FadeIn(lab), run_time=self.duracion, rate_func=linear)


class PenduloDoble(Toma):
    def construct(self):
        def f(y):
            t1, t2, w1, w2 = y
            d = t1 - t2
            den = 3 - np.cos(2 * d)
            a1 = (-3 * np.sin(t1) - np.sin(t1 - 2 * t2) - 2 * np.sin(d) * (w2 ** 2 + w1 ** 2 * np.cos(d))) / den
            a2 = (2 * np.sin(d) * (2 * w1 ** 2 + 2 * np.cos(t1) + w2 ** 2 * np.cos(d))) / den
            return np.array([w1, w2, a1, a2]) * 3.2
        N = 1500
        trayes = [rk4(f, np.array([2.2 + k * 1e-3, 2.5, 0, 0]), self.duracion / N, N) for k in range(3)]
        cols = [COBRE, ACERO, ROSA]
        L = 2.3
        piv = UP * 1.8
        s = ValueTracker(0)

        def pos(k, i):
            t1, t2 = trayes[k][i, 0], trayes[k][i, 1]
            p1 = piv + L * np.array([np.sin(t1), -np.cos(t1), 0])
            return p1, p1 + L * np.array([np.sin(t2), -np.cos(t2), 0])

        for k in range(3):
            self.add(TracedPath(lambda k=k: pos(k, int(s.get_value() * N))[1], stroke_color=cols[k], stroke_width=3, dissipating_time=1.2))

        def escena():
            i = int(s.get_value() * N)
            g = VGroup()
            for k in range(3):
                p1, p2 = pos(k, i)
                g.add(Line(piv, p1, stroke_width=2, color=MARFIL).set_opacity(0.6), Line(p1, p2, stroke_width=2, color=MARFIL).set_opacity(0.6),
                      Dot(p1, radius=0.08, color=MARFIL), punto_brillante(p2, cols[k], 0.1))
            return g

        self.add(always_redraw(escena), punto_brillante(piv, WHITE, 0.06))
        lab = eq(r"|\delta(t)|\sim|\delta_0|\,e^{\lambda t}", 60).move_to(DOWN * 5.6)
        self.play(s.animate.set_value(0.999), FadeIn(lab), run_time=self.duracion, rate_func=linear)


# ---------------------------------------------------------------------------
# Palabras (transparentes): serif enorme en minúscula, centrada, con su ecuación debajo
# ---------------------------------------------------------------------------
class _Palabra(Scene):
    palabra = ""
    ecuacion = ""
    numeral = ""
    duracion = 3.4

    def construct(self):
        p = Text(self.palabra, font="CMU Serif", slant=ITALIC, font_size=190, color=MARFIL)
        if p.width > 8.0:
            p.width = 8.0
        p.move_to(UP * 0.6)
        num = Text(self.numeral, font="CMU Serif", font_size=40, color=MARFIL).set_opacity(0.6).next_to(p, UP, buff=0.5)
        linea = Line(LEFT * 1.8, RIGHT * 1.8, stroke_width=1.5, color=MARFIL).set_opacity(0.7).next_to(p, DOWN, buff=0.45)
        e = eq(self.ecuacion, 52).next_to(linea, DOWN, buff=0.45) if self.ecuacion else VGroup()
        self.play(LaggedStart(*[FadeIn(c, shift=UP * 0.35, scale=1.15) for c in p], lag_ratio=0.07),
                  FadeIn(num), GrowFromCenter(linea), run_time=0.9)
        self.play(FadeIn(e, shift=UP * 0.15), run_time=0.5)
        self.wait(max(self.duracion - 1.9, 0.3))
        self.play(FadeOut(VGroup(p, num, linea, e), scale=1.05), run_time=0.5)


class PalabraInercia(_Palabra):
    palabra, ecuacion, numeral = "inertia", r"\sum\mathbf F=0\ \Rightarrow\ \mathbf v=\text{cte}", "I"


class PalabraResonancia(_Palabra):
    palabra, ecuacion, numeral = "resonance", r"\Omega\to\omega_0", "II"


class PalabraSimetria(_Palabra):
    palabra, ecuacion, numeral = "symmetry", r"\frac{\partial L}{\partial q}=0\ \Rightarrow\ p=\text{cte}", "III"


class PalabraCaos(_Palabra):
    palabra, ecuacion, numeral = "chaos", r"\lambda>0", "IV"


class PalabraFinal(_Palabra):
    palabra, ecuacion, numeral = "everything moves.", r"\mathbf F=\frac{d\mathbf p}{dt}", ""
    duracion = 4.4


TOMAS = ["PlanoInclinado", "Explosion", "Rodadura", "Steiner", "Patinadora", "TresRegimenes", "Pohl", "Acoplados",
         "Lissajous", "Liouville", "Atwood", "Cohete", "CunaNewton", "Colision2D", "Galileo", "Hodografa", "PenduloDoble"]
CITAS = ["PalabraInercia", "PalabraResonancia", "PalabraSimetria", "PalabraCaos", "PalabraFinal"]
