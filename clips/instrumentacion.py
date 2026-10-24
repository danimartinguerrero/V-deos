"""Clips: Instrumentación electrónica (amplificadores operacionales, impedancias, Laplace, Bode)."""

from estilo import *

CABLE = dict(stroke_color=CIELO, stroke_width=4)


# ---------------------------------------------------------------------------
# Piezas de circuito
# ---------------------------------------------------------------------------
def cable(*puntos, color=CIELO, ancho=4):
    l = VMobject(stroke_color=color, stroke_width=ancho)
    l.set_points_as_corners([np.array([*p, 0]) if len(p) == 2 else np.array(p) for p in puntos])
    return l


def resistencia(a, b, picos=6, alto=0.18, color=CELESTE):
    a, b = np.array([*a, 0]), np.array([*b, 0])
    d = b - a
    L = np.linalg.norm(d)
    u = d / L
    n = np.array([-u[1], u[0], 0])
    lead = 0.22 * L
    pts = [a, a + u * lead]
    paso = (L - 2 * lead) / (2 * picos)
    for k in range(2 * picos):
        pts.append(a + u * (lead + paso * (k + 0.5)) + n * alto * (1 if k % 2 == 0 else -1))
    pts += [b - u * lead, b]
    r = VMobject(stroke_width=4)
    r.set_points_as_corners(pts)
    r.set_color([CIELO, color, CIELO])
    return r


def condensador(a, b, color=AMBAR, gap=0.16, ancho=0.7):
    a, b = np.array([*a, 0]), np.array([*b, 0])
    m = (a + b) / 2
    u = (b - a) / np.linalg.norm(b - a)
    n = np.array([-u[1], u[0], 0])
    g = VGroup(
        Line(a, m - u * gap / 2, **CABLE),
        Line(m + u * gap / 2, b, **CABLE),
        Line(m - u * gap / 2 - n * ancho / 2, m - u * gap / 2 + n * ancho / 2, stroke_width=6, color=color),
        Line(m + u * gap / 2 - n * ancho / 2, m + u * gap / 2 + n * ancho / 2, stroke_width=6, color=color),
    )
    return g


def tierra(p):
    p = np.array([*p, 0])
    return VGroup(*[Line(p + DOWN * 0.13 * k + LEFT * (0.32 - 0.1 * k), p + DOWN * 0.13 * k + RIGHT * (0.32 - 0.1 * k),
                         stroke_width=4, color=GRIS) for k in range(3)])


def terminal(p, color=TINTA):
    return Circle(radius=0.09, color=color, stroke_width=4).set_fill("#02040c", 1).move_to([*p, 0])


def ao(x0=0.0, y0=0.0, w=2.0, h=2.4, menos_arriba=True):
    tri = Polygon([x0, y0 + h / 2, 0], [x0, y0 - h / 2, 0], [x0 + w, y0, 0], stroke_width=5)
    tri.set_color([CELESTE, AZUL, VIOLETA])
    tri.set_fill([ZAFIRO, "#0a1430"], opacity=0.6)
    s1 = tex(r"-" if menos_arriba else r"+", font_size=40, color=TINTA).move_to([x0 + 0.32, y0 + 0.55, 0])
    s2 = tex(r"+" if menos_arriba else r"-", font_size=40, color=TINTA).move_to([x0 + 0.32, y0 - 0.55, 0])
    g = VGroup(tri, s1, s2)
    g.arriba = np.array([x0, y0 + 0.55, 0])
    g.abajo = np.array([x0, y0 - 0.55, 0])
    g.salida = np.array([x0 + w, y0, 0])
    return g


def corriente(camino: VMobject, n=7, color=AMBAR, vel=0.22):
    """Puntos luminosos que recorren un cable (sentido de la corriente)."""
    g = VGroup()
    for k in range(n):
        d = Dot(radius=0.07, color=color)
        d.s = k / n
        g.add(d)

    def mover(grupo, dt):
        for d in grupo:
            d.s = (d.s + vel * dt) % 1
            d.move_to(camino.point_from_proportion(d.s))

    g.add_updater(mover)
    mover(g, 0)
    return g


# ---------------------------------------------------------------------------
class Instr1_AO(Clip):
    serie = "Instrumentación electrónica"
    numero = "1/5"
    titulo = "El amplificador operacional"
    subtitulo = "una ganancia enorme, domada"
    colores_titulo = [CELESTE, AZUL, VIOLETA, MAGENTA]
    fondo = ("#0e3a7c", "#123a5a")

    def cuerpo(self):
        A = ao(-1.0, 2.0, w=2.4, h=2.6)
        vm = tex(r"v_-", font_size=34, color=CELESTE)
        vp = tex(r"v_+", font_size=34, color=VIOLETA)
        e1 = cable((-2.6, 2.55), (-1.0, 2.55)); e2 = cable((-2.6, 1.45), (-1.0, 1.45))
        s = cable((1.4, 2.0), (2.8, 2.0))
        vm.next_to(e1, LEFT, buff=0.1); vp.next_to(e2, LEFT, buff=0.1)
        vo = tex(r"v_{out}", font_size=34, color=AMBAR).next_to(s, RIGHT, buff=0.1)
        self.play(DrawBorderThenFill(A[0]), FadeIn(A[1:]), run_time=1.1)
        self.play(Create(VGroup(e1, e2, s)), FadeIn(vm, vp, vo), run_time=0.9)
        f = tex(r"v_{out}=A\,(v_+-v_-)", font_size=50)
        degradado(f, DEG_FRIO)
        f.move_to(UP * 4.1)
        self.play(Write(f), run_time=1.1)

        ejes = Axes(x_range=[-200, 200, 100], y_range=[-11, 11, 9], x_length=7.4, y_length=4.0,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(DOWN * 2.2)
        lx = tex(r"v_+-v_-\ (\mu\mathrm V)", font_size=26, color=GRIS).next_to(ejes.c2p(200, 0), DOWN, buff=0.15).shift(LEFT * 0.8)
        ly = tex(r"v_{out}", font_size=28, color=AMBAR).next_to(ejes.c2p(0, 11), RIGHT, buff=0.1)
        sat = lambda x: np.clip(0.1 * x, -9, 9)
        car = ejes.plot(sat, x_range=[-200, 200, 0.5], stroke_width=6)
        car.set_color([MAGENTA, VIOLETA, CELESTE, TURQUESA])
        self.play(Create(ejes), FadeIn(lx, ly), run_time=0.8)
        self.play(Create(car), run_time=1.4)
        zona = Rectangle(width=ejes.c2p(90, 0)[0] - ejes.c2p(-90, 0)[0], height=4.0,
                         stroke_width=0).move_to(ejes.c2p(0, 0)).set_fill(AMBAR, opacity=0.13)
        zl = tex(r"|v_+-v_-|<90\,\mu\mathrm V", font_size=30, color=AMBAR).next_to(zona, DOWN, buff=0.15)
        vs = tex(r"\pm V_{sat}", font_size=28, color=MAGENTA).move_to(ejes.c2p(150, 6.5))
        self.play(FadeIn(zona), FadeIn(zl), FadeIn(vs), run_time=0.8)
        comp = self.rotulo("sin realimentación: un comparador", pos=DOWN * 5.3, size=28, color=CORAL)
        self.play(FadeIn(comp), run_time=0.5)
        self.wait(0.8)
        self.play(FadeOut(VGroup(ejes, lx, ly, car, zona, zl, vs, comp)), run_time=0.6)

        # --- realimentación negativa --------------------------------------
        lazo = cable((2.2, 2.0), (2.2, 3.55), (-1.9, 3.55), (-1.9, 2.55), color=TURQUESA)
        self.play(Create(lazo), run_time=1.0)
        flujo = corriente(lazo, n=6, color=TURQUESA, vel=0.35)
        self.add(flujo)
        rl = self.rotulo("realimentación negativa: si la salida sube, v₋ sube y la corrige",
                         pos=DOWN * 0.1, size=24, color=TURQUESA)
        self.play(FadeIn(rl), run_time=0.5)
        hip = tex(r"R_{in}\to\infty,\quad R_{out}\to 0,\quad A\to\infty", font_size=40)
        degradado(hip, DEG_AZUL)
        hip.move_to(DOWN * 1.4)
        self.play(Write(hip), run_time=1.2)
        r1 = tex(r"\text{(R1)}\quad i_+=i_-=0", font_size=44, color=CELESTE).move_to(DOWN * 2.8)
        r2 = tex(r"\text{(R2)}\quad v_+=v_-", font_size=44, color=VIOLETA).move_to(DOWN * 3.9)
        self.play(FadeIn(r1, shift=RIGHT * 0.3), run_time=0.7)
        self.play(FadeIn(r2, shift=RIGHT * 0.3), run_time=0.7)
        tv = self.rotulo("cortocircuito virtual: v₊ = v₋ sin unir los terminales", pos=DOWN * 5.1, size=24, color=GRIS)
        self.play(FadeIn(tv), run_time=0.5)
        self.wait(1.2)
        flujo.clear_updaters()

        final = tex(r"i_\pm=0", r"\qquad", r"v_+=v_-", font_size=60)
        final[0].set_color(CELESTE); final[2].set_color(VIOLETA)
        self.cierre(final, "la ganancia la fija la red de realimentación, no el AO")


class Instr2_InversorNoInversor(Clip):
    serie = "Instrumentación electrónica"
    numero = "2/5"
    titulo = "Inversor y no inversor"
    subtitulo = "dos reglas, dos amplificadores"
    colores_titulo = [AMBAR, CORAL, CELESTE]
    fondo = ("#0f3c80", "#3a1d5c")

    def ondas(self, ganancia, y0):
        ejes = Axes(x_range=[0, 2, 0.5], y_range=[-6, 6, 5], x_length=7.4, y_length=2.6,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(UP * y0)
        vin = ejes.plot(lambda t: 0.5 * np.sin(TAU * t), x_range=[0, 2, 0.01], stroke_width=5, color=CELESTE)
        vout = ejes.plot(lambda t: ganancia * 0.5 * np.sin(TAU * t), x_range=[0, 2, 0.01], stroke_width=5)
        vout.set_color([AMBAR, CORAL])
        li = tex(r"v_{in}", font_size=28, color=CELESTE).move_to(ejes.c2p(1.9, 1.6))
        lo = tex(r"v_{out}", font_size=28, color=AMBAR).move_to(ejes.c2p(1.9, 4.8))
        return ejes, vin, vout, VGroup(li, lo)

    def cuerpo(self):
        # ----- inversor -----
        oy = 2.0
        A = ao(0.2, oy, w=2.0, h=2.4)
        vin_t = terminal((-3.6, oy + 0.55), CELESTE)
        w_in = cable((-3.5, oy + 0.55), (-3.1, oy + 0.55))
        R1 = resistencia((-3.1, oy + 0.55), (-1.0, oy + 0.55))
        w_n = cable((-1.0, oy + 0.55), (0.2, oy + 0.55))
        fb = cable((-0.5, oy + 0.55), (-0.5, oy + 2.0), (0.0, oy + 2.0))
        R2 = resistencia((0.0, oy + 2.0), (2.8, oy + 2.0), color=VIOLETA)
        fb2 = cable((2.8, oy + 2.0), (2.8, oy), (2.2, oy))
        w_out = cable((2.8, oy), (3.5, oy))
        out_t = terminal((3.6, oy), AMBAR)
        w_p = cable((0.2, oy - 0.55), (-0.5, oy - 0.55), (-0.5, oy - 1.2))
        gnd = tierra((-0.5, oy - 1.2))
        l1 = tex(r"R_1", font_size=32, color=CELESTE).next_to(R1, DOWN, buff=0.15)
        l2 = tex(r"R_2", font_size=32, color=VIOLETA).next_to(R2, UP, buff=0.15)
        lvin = tex(r"v_{in}", font_size=32, color=CELESTE).next_to(vin_t, UP, buff=0.12)
        lvo = tex(r"v_{out}", font_size=32, color=AMBAR).next_to(out_t, UP, buff=0.12)
        circ = VGroup(A, w_in, R1, w_n, fb, R2, fb2, w_out, w_p, gnd, vin_t, out_t, l1, l2, lvin, lvo)
        self.play(LaggedStart(DrawBorderThenFill(A), *[Create(m) for m in (w_in, R1, w_n, fb, R2, fb2, w_out, w_p)],
                              FadeIn(gnd), FadeIn(vin_t, out_t), lag_ratio=0.12), run_time=1.8)
        self.play(FadeIn(VGroup(l1, l2, lvin, lvo)), run_time=0.5)

        nodo = Dot([-0.5, oy + 0.55, 0], radius=0.1, color=TURQUESA)
        tvirt = tex(r"v_-=0", font_size=30, color=TURQUESA).move_to(nodo.get_center() + DOWN * 0.5 + LEFT * 0.45)
        self.play(FadeIn(nodo, scale=2), FadeIn(brillo(Circle(radius=0.1).move_to(nodo), TURQUESA, 6, 30, 0.25)),
                  Write(tvirt), run_time=0.8)
        camino = cable((-3.5, oy + 0.55), (-0.5, oy + 0.55), (-0.5, oy + 2.0), (2.8, oy + 2.0), (2.8, oy))
        flujo = corriente(camino, n=10, color=AMBAR, vel=0.28)
        self.add(flujo)
        pasos = [
            tex(r"i_1=\frac{v_{in}}{R_1}", font_size=40, color=CELESTE),
            tex(r"i_2=i_1", font_size=40, color=TINTA),
            tex(r"v_{out}=-i_2R_2", font_size=40, color=AMBAR),
        ]
        fila = VGroup(*pasos).arrange(RIGHT, buff=0.55).move_to(DOWN * 0.3)
        ajustar(fila)
        for p in pasos:
            self.play(FadeIn(p, shift=UP * 0.2), run_time=0.55)
        av = tex(r"A_V=-\frac{R_2}{R_1}=-10", font_size=50)
        degradado(av, [AMBAR, CORAL])
        av.move_to(DOWN * 1.8)
        self.play(Write(av), run_time=1.0)
        ejes, vi, vo, lb = self.ondas(-10, -4.3)
        self.play(Create(ejes), Create(vi), FadeIn(lb), run_time=0.8)
        self.play(Create(vo), run_time=1.0)
        cf = self.rotulo("contrafase: 180°", pos=DOWN * 5.9, size=26, color=CORAL)
        self.play(FadeIn(cf), run_time=0.4)
        self.wait(0.8)
        flujo.clear_updaters()
        self.limpiar()

        # ----- no inversor -----
        A2 = ao(0.2, oy, w=2.0, h=2.4, menos_arriba=False)
        vin2 = terminal((-3.6, oy + 0.55), CELESTE)
        w1 = cable((-3.5, oy + 0.55), (0.2, oy + 0.55))
        w2 = cable((0.2, oy - 0.55), (-0.5, oy - 0.55), (-0.5, oy - 1.3))
        Rb1 = resistencia((-0.5, oy - 1.3), (-0.5, oy - 3.0))
        g2 = tierra((-0.5, oy - 3.0))
        Rb2 = resistencia((-0.5, oy - 1.3), (2.8, oy - 1.3), color=VIOLETA)
        w3 = cable((2.8, oy - 1.3), (2.8, oy), (2.2, oy))
        w4 = cable((2.8, oy), (3.5, oy))
        out2 = terminal((3.6, oy), AMBAR)
        m1 = tex(r"R_1", font_size=32, color=CELESTE).next_to(Rb1, LEFT, buff=0.15)
        m2 = tex(r"R_2", font_size=32, color=VIOLETA).next_to(Rb2, DOWN, buff=0.15)
        mvi = tex(r"v_{in}", font_size=32, color=CELESTE).next_to(vin2, UP, buff=0.12)
        mvo = tex(r"v_{out}", font_size=32, color=AMBAR).next_to(out2, UP, buff=0.12)
        self.play(LaggedStart(DrawBorderThenFill(A2), *[Create(m) for m in (w1, w2, Rb1, Rb2, w3, w4)],
                              FadeIn(g2, vin2, out2, m1, m2, mvi, mvo), lag_ratio=0.12), run_time=1.6)
        div = tex(r"v_-=v_{in}=\frac{R_1}{R_1+R_2}\,v_{out}", font_size=40)
        degradado(div, DEG_FRIO)
        div.move_to(DOWN * 2.2)
        self.play(Write(div), run_time=1.1)
        av2 = tex(r"A_V=1+\frac{R_2}{R_1}=+11", font_size=50)
        degradado(av2, [TURQUESA, CELESTE])
        av2.move_to(DOWN * 3.45)
        self.play(Write(av2), run_time=1.0)
        ejes2, vi2, vo2, lb2 = self.ondas(11, -5.3)
        ejes2.set_opacity(0.8)
        self.play(Create(ejes2), Create(vi2), Create(vo2), FadeIn(lb2), run_time=1.2)
        self.wait(0.8)

        final = tex(r"A_V=-\frac{R_2}{R_1}", r"\qquad", r"A_V=1+\frac{R_2}{R_1}", font_size=52)
        final[0].set_color_by_gradient(AMBAR, CORAL); final[2].set_color_by_gradient(TURQUESA, CELESTE)
        self.cierre(final, "R₁ = 1 kΩ, R₂ = 10 kΩ: ganancias −10 y +11")


class Instr3_ImpedanciaLaplace(Clip):
    serie = "Instrumentación electrónica"
    numero = "3/5"
    titulo = "Impedancia y Laplace"
    subtitulo = "derivar es multiplicar"
    colores_titulo = [TURQUESA, CELESTE, AZUL, VIOLETA]
    fondo = ("#0c3f86", "#1c2f6a")

    def cuerpo(self):
        f = tex(r"v(t)=\mathrm{Re}\{V e^{j\omega t}\}", font_size=46)
        degradado(f, DEG_AZUL)
        f.move_to(UP * 4.1)
        self.play(Write(f), run_time=1.0)

        c0 = np.array([-2.7, 1.4, 0])
        R = 1.2
        circ = Circle(radius=R, stroke_width=2, color=GRIS).move_to(c0).set_stroke(opacity=0.6)
        ejes_c = VGroup(Line(c0 + LEFT * 1.5, c0 + RIGHT * 1.5), Line(c0 + DOWN * 1.5, c0 + UP * 1.5)).set_stroke(GRIS, 1.5, 0.5)
        t = ValueTracker(0)
        x0, x1 = -1.1, 3.9
        k = 2.2

        def fasor():
            a = t.get_value()
            tip = c0 + R * np.array([np.cos(a), np.sin(a), 0])
            v = Arrow(c0, tip, buff=0, stroke_width=6, max_tip_length_to_length_ratio=0.18).set_color([CELESTE, AZUL])
            return v

        def fasor_d():
            a = t.get_value() + PI / 2
            tip = c0 + R * 0.85 * np.array([np.cos(a), np.sin(a), 0])
            return Arrow(c0, tip, buff=0, stroke_width=5, max_tip_length_to_length_ratio=0.2).set_color([MAGENTA, CORAL])

        def onda():
            a = t.get_value()
            g = FunctionGraph(lambda x: c0[1] + R * np.sin(a - k * (x - x0)), x_range=[x0, x1, 0.02], stroke_width=5)
            g.set_color([CELESTE, AZUL, VIOLETA])
            tip = c0 + R * np.array([np.cos(a), np.sin(a), 0])
            enlace = DashedLine(tip, [x0, tip[1], 0], stroke_width=2, color=CIELO)
            return VGroup(g, enlace, Dot([x0, tip[1], 0], radius=0.07, color=CIELO))

        def onda_d():
            a = t.get_value() + PI / 2
            g = FunctionGraph(lambda x: c0[1] + 0.85 * R * np.sin(a - k * (x - x0)), x_range=[x0, x1, 0.02],
                              stroke_width=3)
            return g.set_color([MAGENTA, CORAL]).set_stroke(opacity=0.8)

        fa, on = always_redraw(fasor), always_redraw(onda)
        self.play(Create(circ), FadeIn(ejes_c), GrowArrow(fa), Create(on), run_time=1.0)
        self.play(t.animate.set_value(2 * TAU), run_time=3.0, rate_func=linear)
        der = tex(r"\frac{d}{dt}e^{j\omega t}=j\omega\,e^{j\omega t}", font_size=42)
        degradado(der, [MAGENTA, CORAL, AMBAR])
        der.move_to(DOWN * 0.8)
        fd, od = always_redraw(fasor_d), always_redraw(onda_d)
        self.play(Write(der), GrowArrow(fd), Create(od), t.animate.set_value(2 * TAU + 1.5), run_time=1.6, rate_func=linear)
        giro = self.rotulo("derivar = girar 90° y escalar por ω", pos=DOWN * 1.95, size=26, color=CORAL)
        self.play(FadeIn(giro), t.animate.set_value(3 * TAU + 1.5), run_time=1.8, rate_func=linear)

        zs = VGroup(
            tex(r"Z_R=R", font_size=40, color=CELESTE),
            tex(r"Z_C=\frac{1}{j\omega C}", font_size=40, color=AMBAR),
            tex(r"Z_L=j\omega L", font_size=40, color=MAGENTA),
        ).arrange(RIGHT, buff=0.6).move_to(DOWN * 3.3)
        ajustar(zs)
        self.play(LaggedStart(*[FadeIn(z, shift=UP * 0.3) for z in zs], lag_ratio=0.3),
                  t.animate.set_value(4 * TAU + 1.5), run_time=1.8, rate_func=linear)
        for m in (fa, on, fd, od):
            m.clear_updaters()
        self.wait(0.4)
        self.limpiar()

        # --- Laplace ---------------------------------------------------------
        L = tex(r"F(s)=\int_0^\infty f(t)\,e^{-st}\,dt", font_size=48)
        degradado(L, DEG_FRIO)
        L.move_to(UP * 3.9)
        self.play(Write(L), run_time=1.2)
        props = VGroup(
            tex(r"\frac{df}{dt}\;\longleftrightarrow\;sF(s)-f(0)", font_size=40, color=MAGENTA),
            tex(r"\int_0^t f\,d\tau\;\longleftrightarrow\;\frac{F(s)}{s}", font_size=40, color=AMBAR),
        ).arrange(DOWN, buff=0.45).move_to(UP * 1.8)
        self.play(LaggedStart(*[FadeIn(p, shift=LEFT * 0.3) for p in props], lag_ratio=0.4), run_time=1.3)
        jw = tex(r"j\omega\;\to\;s", r"\qquad", r"Z_C(s)=\frac{1}{sC}", font_size=44)
        jw[0].set_color(CIELO); jw[2].set_color(AMBAR)
        jw.move_to(DOWN * 0.2)
        self.play(Write(jw), run_time=1.1)
        ejes = Axes(x_range=[0, 10, 1], y_range=[0, 5, 1], x_length=7.0, y_length=2.6,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(DOWN * 3.0)
        zc = ejes.plot(lambda w: min(1.5 / w, 5), x_range=[0.3, 10, 0.02], stroke_width=5)
        zc.set_color([AMBAR, CORAL, MAGENTA, VIOLETA])
        lz = tex(r"|Z_C|", font_size=30, color=AMBAR).next_to(ejes.c2p(0, 5), RIGHT, buff=0.15)
        lw = tex(r"\omega", font_size=32, color=GRIS).next_to(ejes.c2p(10, 0), UP, buff=0.1)
        self.play(Create(ejes), Create(zc), FadeIn(lz, lw), run_time=1.3)
        a1 = texto("abierto en continua", size=22, color=AMBAR).move_to(ejes.c2p(2.6, 4.3))
        a2 = texto("cortocircuito a alta f", size=22, color=VIOLETA).move_to(ejes.c2p(7.4, 1.3))
        self.play(FadeIn(a1), FadeIn(a2), run_time=0.7)
        self.wait(1.0)

        final = tex(r"Z_R=R,\quad Z_C=\frac{1}{sC},\quad Z_L=sL", font_size=48)
        degradado(final, DEG_ARCOIRIS)
        self.cierre(final, "con impedancias, un circuito con C se resuelve como uno resistivo")


class Instr4_FiltroPasoBajo(Clip):
    serie = "Instrumentación electrónica"
    numero = "4/5"
    titulo = "Filtro paso bajo activo"
    subtitulo = "inversor generalizado con RF ∥ C"
    colores_titulo = [CELESTE, VIOLETA, MAGENTA, CORAL]
    fondo = ("#103b84", "#45184e")

    def cuerpo(self):
        oy = 1.5
        A = ao(0.2, oy, w=1.8, h=2.2)
        w_in = cable((-3.6, oy + 0.55), (-3.2, oy + 0.55))
        R = resistencia((-3.2, oy + 0.55), (-1.2, oy + 0.55))
        w_n = cable((-1.2, oy + 0.55), (0.2, oy + 0.55))
        fbA = cable((-0.5, oy + 0.55), (-0.5, oy + 2.3), (-0.1, oy + 2.3))
        fbB = cable((-0.5, oy + 1.5), (-0.1, oy + 1.5))
        RF = resistencia((-0.1, oy + 2.3), (2.6, oy + 2.3), color=VIOLETA)
        C = condensador((-0.1, oy + 1.5), (2.6, oy + 1.5))
        fbC = cable((2.6, oy + 2.3), (2.6, oy), (2.0, oy))
        w_out = cable((2.6, oy), (3.5, oy))
        w_p = cable((0.2, oy - 0.55), (-0.5, oy - 0.55), (-0.5, oy - 1.1))
        gnd = tierra((-0.5, oy - 1.1))
        ti, to = terminal((-3.7, oy + 0.55), CELESTE), terminal((3.6, oy), AMBAR)
        lr = tex(r"R", font_size=32, color=CELESTE).next_to(R, DOWN, buff=0.12)
        lrf = tex(r"R_F", font_size=30, color=VIOLETA).next_to(RF, UP, buff=0.08)
        lc = tex(r"C", font_size=30, color=AMBAR).next_to(C, DOWN, buff=0.05).shift(RIGHT * 0.6)
        self.play(LaggedStart(DrawBorderThenFill(A), *[Create(m) for m in (w_in, R, w_n, fbA, fbB, RF, C, fbC, w_out, w_p)],
                              FadeIn(gnd, ti, to), lag_ratio=0.08), run_time=1.8)
        self.play(FadeIn(lr, lrf, lc), run_time=0.4)

        h1 = tex(r"H(s)=-\frac{Z_2}{Z_1}", font_size=46)
        degradado(h1, DEG_FRIO)
        h1.move_to(DOWN * 1.2)
        self.play(Write(h1), run_time=0.9)
        z2 = tex(r"Z_2=R_F\parallel C=\frac{R_F}{1+sR_FC}", font_size=38, color=VIOLETA).move_to(DOWN * 2.6)
        self.play(FadeIn(z2, shift=UP * 0.2), run_time=0.8)
        h2 = tex(r"H(s)=-\frac{R_F}{R}\,\frac{1}{1+sR_FC}", font_size=46)
        degradado(h2, [CELESTE, VIOLETA, MAGENTA])
        h2.move_to(h1)
        self.play(TransformMatchingShapes(h1, h2), FadeOut(z2), run_time=1.1)
        fc = tex(r"f_c=\frac{1}{2\pi R_FC}", font_size=40, color=AMBAR).move_to(DOWN * 2.6)
        self.play(Write(fc), run_time=0.7)
        self.wait(0.4)
        self.play(FadeOut(VGroup(A, w_in, R, w_n, fbA, fbB, RF, C, fbC, w_out, w_p, gnd, ti, to, lr, lrf, lc)),
                  h2.animate.move_to(UP * 4.0), fc.animate.scale(0.8).move_to(UP * 2.55), run_time=0.8)

        # --- Bode -------------------------------------------------------------
        ejes = Axes(x_range=[-2, 2, 1], y_range=[-22, 24, 10], x_length=7.6, y_length=3.6,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(UP * 0.0)
        mag = lambda u: 20 * np.log10(10 / np.sqrt(1 + 10 ** (2 * u)))
        curva = ejes.plot(mag, x_range=[-2, 2, 0.01], stroke_width=6)
        curva.set_color([TURQUESA, CELESTE, AZUL, VIOLETA, MAGENTA])
        asint = VGroup(DashedLine(ejes.c2p(-2, 20), ejes.c2p(0, 20)), DashedLine(ejes.c2p(0, 20), ejes.c2p(2, -20))).set_stroke(GRIS, 2)
        ly = tex(r"|A_V|\,(\mathrm{dB})", font_size=26, color=GRIS).next_to(ejes.c2p(-2, 24), RIGHT, buff=0.1)
        lx = tex(r"\log f", font_size=28, color=GRIS).next_to(ejes.c2p(2, -22), UP, buff=0.1)
        self.play(Create(ejes), FadeIn(ly, lx), run_time=0.6)
        self.play(Create(asint), Create(curva), run_time=1.6)
        p3 = Dot(ejes.c2p(0, mag(0)), radius=0.09, color=AMBAR)
        t3 = tex(r"-3\,\mathrm{dB}", font_size=28, color=AMBAR).next_to(p3, DL, buff=0.08)
        pend = tex(r"-20\,\mathrm{dB/d\acute ec}", font_size=28, color=MAGENTA).move_to(ejes.c2p(1.3, 4))
        self.play(FadeIn(p3, scale=2), FadeIn(t3), FadeIn(pend), run_time=0.7)

        u = ValueTracker(-1.8)
        caja_ondas = Axes(x_range=[0, 3, 1], y_range=[-1.3, 1.3, 1], x_length=7.4, y_length=2.2,
                          axis_config={"stroke_color": GRIS, "include_ticks": False, "stroke_opacity": 0.4}).move_to(DOWN * 3.5)

        def barrido():
            v = u.get_value()
            g = 10 / np.sqrt(1 + 10 ** (2 * v))
            fase = PI - np.arctan(10 ** v)
            d = Dot(ejes.c2p(v, mag(v)), radius=0.11, color=TINTA)
            vin = caja_ondas.plot(lambda x: 0.45 * np.sin(TAU * x), x_range=[0, 3, 0.01], stroke_width=3, color=CELESTE)
            vout = caja_ondas.plot(lambda x: 0.11 * g * np.sin(TAU * x + fase), x_range=[0, 3, 0.01], stroke_width=5)
            vout.set_color([AMBAR, CORAL])
            lect = tex(r"|A_V|=%.1f\qquad \varphi=%d^\circ" % (g, round(np.degrees(fase))), font_size=32, color=TINTA)
            lect.move_to(DOWN * 5.15)
            return VGroup(d, vin, vout, lect)

        bar = always_redraw(barrido)
        self.play(Create(caja_ondas), FadeIn(bar), run_time=0.7)
        self.play(u.animate.set_value(1.8), run_time=5.5, rate_func=smooth)
        bar.clear_updaters()
        self.wait(0.4)

        final = tex(r"|A_V(f)|=\frac{R_F/R}{\sqrt{1+(f/f_c)^2}}", font_size=52)
        degradado(final, DEG_ARCOIRIS)
        self.cierre(final, "meseta RF/R, corte a −3 dB en fc, fase de 180° a 90°")


class Instr5_GBW(Clip):
    serie = "Instrumentación electrónica"
    numero = "5/5"
    titulo = "Ganancia × ancho de banda"
    subtitulo = "el precio de un AO real"
    colores_titulo = [AMBAR, CORAL, MAGENTA, VIOLETA]
    fondo = ("#0f3a80", "#4a1d3c")

    def cuerpo(self):
        A = tex(r"A(s)=\frac{A_0}{1+s/\omega_b}", font_size=50)
        degradado(A, DEG_AZUL)
        A.move_to(UP * 4.0)
        self.play(Write(A), run_time=1.1)
        datos = tex(r"A_0=2\cdot10^5\ (106\,\mathrm{dB}),\quad f_b\approx5\,\mathrm{Hz}", font_size=34, color=GRIS)
        datos.next_to(A, DOWN, buff=0.3)
        self.play(FadeIn(datos), run_time=0.6)

        ejes = Axes(x_range=[0, 7, 1], y_range=[0, 115, 20], x_length=7.6, y_length=4.6,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(DOWN * 0.3)
        etq = VGroup(*[tex(s, font_size=24, color=GRIS).next_to(ejes.c2p(x, 0), DOWN, buff=0.12)
                       for x, s in [(0, r"1"), (3, r"1\,\mathrm{k}"), (6, r"1\,\mathrm{M}")]])
        ly = tex(r"\mathrm{dB}", font_size=26, color=GRIS).next_to(ejes.c2p(0, 115), RIGHT, buff=0.1)
        lx = tex(r"f\,(\mathrm{Hz})", font_size=26, color=GRIS).next_to(ejes.c2p(7, 0), UP, buff=0.1)
        A0, fb, ft = 2e5, 5.0, 1e6
        abierto = ejes.plot(lambda u: 20 * np.log10(A0 / np.sqrt(1 + (10 ** u / fb) ** 2)), x_range=[0, 7, 0.01],
                            stroke_width=5)
        abierto.set_color([CELESTE, AZUL, VIOLETA])
        self.play(Create(ejes), FadeIn(etq, ly, lx), run_time=0.8)
        self.play(Create(abierto), run_time=1.6)
        pft = Dot(ejes.c2p(6, 0), radius=0.09, color=CELESTE)
        lft = tex(r"f_t\approx 1\,\mathrm{MHz}", font_size=28, color=CELESTE).move_to(ejes.c2p(6.2, 28))
        pend = tex(r"-20\,\mathrm{dB/d\acute ec}", font_size=26, color=VIOLETA).move_to(ejes.c2p(3.8, 70))
        self.play(FadeIn(pft, lft, pend), run_time=0.6)

        G = ValueTracker(3.0)  # log10 de la ganancia en lazo cerrado

        def lazo():
            g = 10 ** G.get_value()
            f3 = ft / g
            c = ejes.plot(lambda u: 20 * np.log10(g / np.sqrt(1 + (10 ** u / f3) ** 2)), x_range=[0, 7, 0.01],
                          stroke_width=6)
            c.set_color([AMBAR, CORAL])
            esq = Dot(ejes.c2p(np.log10(f3), 20 * np.log10(g) - 3), radius=0.1, color=AMBAR)
            area = Rectangle(width=ejes.c2p(np.log10(f3), 0)[0] - ejes.c2p(0, 0)[0],
                             height=ejes.c2p(0, 20 * np.log10(g))[1] - ejes.c2p(0, 0)[1], stroke_width=0)
            area.set_fill([AMBAR, CORAL], opacity=0.12).align_to(ejes.c2p(0, 0), DL)
            lect = tex(r"|A_V|=%s\qquad f_{3dB}=%s" % (fmt(g), fmt(f3) + r"\,\mathrm{Hz}"), font_size=34)
            lect.set_color_by_gradient(AMBAR, CORAL).move_to(DOWN * 3.3)
            return VGroup(area, c, esq, lect)

        def fmt(x):
            if x >= 1e6:
                return r"%.0f\,\mathrm{M}" % (x / 1e6)
            if x >= 1e3:
                return r"%.0f\,\mathrm{k}" % (x / 1e3)
            return r"%.0f" % x

        lz = always_redraw(lazo)
        self.play(FadeIn(lz), run_time=0.8)
        self.play(G.animate.set_value(1.0), run_time=4.0, rate_func=smooth)
        self.play(G.animate.set_value(2.0), run_time=1.6, rate_func=smooth)
        lz.clear_updaters()
        prod = tex(r"|A_V|\cdot f_{3dB}\approx f_t", font_size=48)
        degradado(prod, DEG_CALIDO)
        prod.move_to(DOWN * 4.5)
        self.play(Write(prod), run_time=1.0)
        sr = tex(r"\text{slew rate:}\ \ 2\pi f V_p\le SR", font_size=34, color=GRIS).move_to(DOWN * 5.5)
        self.play(FadeIn(sr), run_time=0.6)
        self.wait(1.0)

        final = tex(r"f_{3dB}=\frac{f_t}{1+R_2/R_1}", font_size=56)
        degradado(final, DEG_CALIDO + [VIOLETA])
        self.cierre(final, "inversor ×10:  1 MHz / 11 ≈ 91 kHz de ancho de banda")
