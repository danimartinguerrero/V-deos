"""Clips: Termodinámica I, tema 1 (conceptos básicos)."""

from estilo import *

CALOR = "#FF8A3D"


def gas(caja: Rectangle, n=70, seed=3, vel=1.6, colores=(CIELO, CELESTE, AZUL, VIOLETA)):
    """Partículas que rebotan dentro de un rectángulo (que puede cambiar)."""
    rng = np.random.default_rng(seed)
    g = VGroup()
    for _ in range(n):
        d = Dot(radius=0.055, color=rng.choice(colores))
        d.move_to(caja.get_center() + [rng.uniform(-0.45, 0.45) * caja.width, rng.uniform(-0.45, 0.45) * caja.height, 0])
        a = rng.uniform(0, TAU)
        d.v = vel * rng.uniform(0.6, 1.4) * np.array([np.cos(a), np.sin(a), 0])
        g.add(d)

    def mover(grupo, dt):
        x0, x1 = caja.get_left()[0] + 0.07, caja.get_right()[0] - 0.07
        y0, y1 = caja.get_bottom()[1] + 0.07, caja.get_top()[1] - 0.07
        for d in grupo:
            p = d.get_center() + d.v * dt
            if p[0] < x0 or p[0] > x1:
                d.v[0] *= -1
                p[0] = np.clip(p[0], x0, x1)
            if p[1] < y0 or p[1] > y1:
                d.v[1] *= -1
                p[1] = np.clip(p[1], y0, y1)
            d.move_to(p)

    g.add_updater(mover)
    return g


def flecha_doble(a, b, color, ancho=5):
    return VGroup(
        Arrow(a, b, buff=0, stroke_width=ancho, color=color, max_tip_length_to_length_ratio=0.25).shift(UP * 0.1),
        Arrow(b, a, buff=0, stroke_width=ancho, color=color, max_tip_length_to_length_ratio=0.25).shift(DOWN * 0.1),
    )


class Termo1_Sistemas(Clip):
    serie = "Termodinámica I · Tema 1"
    numero = "1/4"
    titulo = "La simplicidad macroscópica"
    subtitulo = "de 10²³ partículas a cuatro variables"
    colores_titulo = [CIELO, CELESTE, AZUL, VIOLETA]
    fondo = ("#0f3a82", "#3b2058")

    def cuerpo(self):
        cil = Rectangle(width=4.2, height=4.2, stroke_width=0).move_to(UP * 1.2)
        paredes = cable_cilindro(cil)
        piston = Rectangle(width=4.1, height=0.35, stroke_width=3).set_color([GRIS, TINTA]).set_fill(GRIS, 0.8)
        piston.add_updater(lambda m: m.next_to(cil, UP, buff=0))
        vastago = always_redraw(lambda: Line(piston.get_top(), piston.get_top() + UP * 0.7, stroke_width=8, color=GRIS))
        part = gas(cil, n=80)
        self.play(Create(paredes), FadeIn(piston), FadeIn(vastago), run_time=0.9)
        self.play(FadeIn(part), run_time=0.6)
        micro = tex(r"\{\mathbf r_i,\mathbf p_i\},\ \ i=1,\dots,N\approx10^{23}", font_size=40)
        degradado(micro, DEG_FRIO)
        micro.move_to(DOWN * 1.8)
        self.play(Write(micro), run_time=1.2)
        self.wait(1.0)
        # compresión: el pistón baja
        self.play(cil.animate.stretch_to_fit_height(3.0, about_edge=DOWN), run_time=1.4)
        self.play(cil.animate.stretch_to_fit_height(4.2, about_edge=DOWN), run_time=1.2)

        niebla = Rectangle(width=4.1, height=4.15).move_to(cil).set_stroke(width=0)
        niebla.set_fill([AZUL, VIOLETA], opacity=0.0)
        self.add(niebla)
        macro = tex(r"p,\ V,\ T,\ n", font_size=64)
        degradado(macro, DEG_ARCOIRIS)
        macro.move_to(cil)
        self.play(part.animate.set_opacity(0.08), niebla.animate.set_fill(opacity=0.45),
                  TransformMatchingShapes(micro, macro), run_time=1.6)
        r = self.rotulo("las medidas promedian escalas enormes frente a las atómicas", pos=DOWN * 1.6, size=26, color=GRIS)
        self.play(FadeIn(r), run_time=0.6)
        self.wait(0.8)
        part.clear_updaters(); piston.clear_updaters(); vastago.clear_updaters()
        self.limpiar()

        # --- aislado, cerrado, abierto ----------------------------------------
        tipos = [("Aislado", []), ("Cerrado", [CALOR]), ("Abierto", [CALOR, CELESTE])]
        filas = VGroup()
        for k, (nom, cols) in enumerate(tipos):
            y = 3.0 - 2.75 * k
            caja_s = RoundedRectangle(width=2.6, height=1.7, corner_radius=0.2).move_to([-1.6, y, 0])
            caja_s.set_stroke([CELESTE, VIOLETA], width=4).set_fill("#0a1430", 0.7)
            nombre = texto(nom, size=30, color=TINTA, weight=BOLD).move_to(caja_s)
            fl = VGroup()
            for j, c in enumerate(cols):
                fl.add(flecha_doble([0.2, y + 0.35 - 0.7 * j, 0], [2.6, y + 0.35 - 0.7 * j, 0], c))
            filas.add(VGroup(caja_s, nombre, fl))
        etiquetas = VGroup(
            texto("ni energía ni materia", size=22, color=GRIS).move_to([1.9, 3.0, 0]),
            texto("energía", size=22, color=CALOR).next_to(filas[1][2], RIGHT, buff=0.15),
            VGroup(texto("energía", size=22, color=CALOR), texto("materia", size=22, color=CELESTE)).arrange(DOWN, buff=0.4)
            .next_to(filas[2][2], RIGHT, buff=0.15),
        )
        for k in range(3):
            self.play(DrawBorderThenFill(filas[k][0]), Write(filas[k][1]), run_time=0.6)
            anims = [GrowFromCenter(f) for f in filas[k][2]]
            self.play(*(anims or [Wait()]), FadeIn(etiquetas[k]), run_time=0.6)
        ej = self.rotulo("termo  ·  cilindro sellado  ·  turbina", pos=DOWN * 5.0, size=26, color=CIELO)
        self.play(FadeIn(ej), run_time=0.5)
        self.play(*[Indicate(f, color=TINTA, scale_factor=1.06) for f in (filas[1][2], filas[2][2])], run_time=1.0)
        self.wait(0.6)

        final = tex(r"\text{estado }A=\{p_A,\,V_A,\,T_A,\,n_A,\dots\}", font_size=46)
        degradado(final, DEG_AZUL)
        self.cierre(final, "una lista suficiente y no redundante de variables")


def cable_cilindro(r: Rectangle):
    a, b, c, d = r.get_corner(UL), r.get_corner(DL), r.get_corner(DR), r.get_corner(UR)
    m = VMobject(stroke_width=6)
    m.set_points_as_corners([a + UP * 0.9, b, c, d + UP * 0.9])
    m.set_color([CELESTE, AZUL, VIOLETA])
    return m


class Termo2_LeyCero(Clip):
    serie = "Termodinámica I · Tema 1"
    numero = "2/4"
    titulo = "Equilibrio y ley cero"
    subtitulo = "el origen de la temperatura"
    colores_titulo = [AMBAR, CORAL, MAGENTA, CELESTE]
    fondo = ("#123a7e", "#4a1a3a")

    def cuerpo(self):
        ejes = Axes(x_range=[0, 7, 1], y_range=[0, 6, 1], x_length=7.4, y_length=3.0,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(UP * 2.8)
        X = lambda t: 1.0 + 4.5 * np.exp(-t)
        c = ejes.plot(X, x_range=[0, 7, 0.02], stroke_width=5)
        c.set_color([CORAL, MAGENTA, VIOLETA, CELESTE])
        eq = DashedLine(ejes.c2p(0, 1), ejes.c2p(7, 1), color=CELESTE, stroke_width=2)
        lx = tex(r"X(t)", font_size=30, color=CORAL).move_to(ejes.c2p(1.2, 5.2))
        leq = tex(r"X_{eq}", font_size=28, color=CELESTE).next_to(ejes.c2p(7, 1), UP, buff=0.1)
        tau = tex(r"\tau", font_size=34, color=AMBAR).next_to(ejes.c2p(1, 0), DOWN, buff=0.1)
        self.play(Create(ejes), Create(eq), FadeIn(leq), run_time=0.7)
        punto = Dot(ejes.c2p(0, X(0)), radius=0.1, color=TINTA)
        self.play(Create(c), MoveAlongPath(punto, c), FadeIn(lx), run_time=2.0)
        self.play(FadeIn(tau), Flash(ejes.c2p(1, X(1)), color=AMBAR), run_time=0.6)
        rr = self.rotulo("relajación hacia el equilibrio", pos=UP * 0.75, size=26, color=GRIS)
        self.play(FadeIn(rr), run_time=0.4)

        # estado estacionario ≠ equilibrio
        barra = Rectangle(width=7.0, height=0.8, stroke_width=0).move_to(DOWN * 1.2)
        barra.set_fill([CORAL, MAGENTA, VIOLETA, AZUL], opacity=0.9)
        barra.set_sheen_direction(RIGHT)
        cal = texto("caliente", size=22, color=CORAL).next_to(barra, UP, buff=0.12).align_to(barra, LEFT)
        fri = texto("frío", size=22, color=CELESTE).next_to(barra, UP, buff=0.12).align_to(barra, RIGHT)
        self.play(FadeIn(barra), FadeIn(cal, fri), run_time=0.7)
        flujo = VGroup()
        for k in range(8):
            d = Arrow(LEFT * 0.3, RIGHT * 0.3, buff=0, stroke_width=4, color=AMBAR, max_tip_length_to_length_ratio=0.4)
            d.move_to(barra.get_left() + RIGHT * (0.5 + 0.85 * k))
            d.s = k * 0.85
            flujo.add(d)

        def fluir(g, dt):
            for d in g:
                d.s = (d.s + 1.2 * dt) % 6.6
                d.move_to(barra.get_left() + RIGHT * (0.3 + d.s))

        flujo.add_updater(fluir)
        self.add(flujo)
        ne = tex(r"T(x)\ \text{constante en } t\ +\ \text{flujo}\;\neq\;\text{equilibrio}", font_size=32, color=AMBAR)
        ne.move_to(DOWN * 2.35)
        self.play(Write(ne), run_time=1.0)
        self.wait(1.4)
        flujo.clear_updaters()
        self.limpiar()

        # --- ley cero -----------------------------------------------------------
        def sistema(nom, col, pos):
            b = RoundedRectangle(width=2.0, height=1.6, corner_radius=0.2).move_to(pos)
            b.set_stroke(col, 4).set_fill(col, 0.25)
            return VGroup(b, tex(nom, font_size=50, color=TINTA).move_to(b))

        A = sistema("A", CORAL, [-2.6, 2.6, 0])
        C = sistema("C", AMBAR, [0, 0.4, 0])
        B = sistema("B", CELESTE, [2.6, 2.6, 0])
        self.play(*[DrawBorderThenFill(s) for s in (A, C, B)], run_time=1.0)
        pared1 = Line(A[0].get_corner(DR), C[0].get_corner(UL), stroke_width=6).set_color([CORAL, AMBAR])
        self.play(Create(pared1), A[0].animate.set_fill(AMBAR, 0.3).set_stroke(AMBAR), run_time=1.0)
        r1 = tex(r"A\sim C", font_size=40, color=AMBAR).next_to(pared1, LEFT, buff=0.3)
        self.play(FadeIn(r1), run_time=0.4)
        pared2 = Line(B[0].get_corner(DL), C[0].get_corner(UR), stroke_width=6).set_color([CELESTE, AMBAR])
        self.play(Create(pared2), B[0].animate.set_fill(AMBAR, 0.3).set_stroke(AMBAR), run_time=1.0)
        r2 = tex(r"B\sim C", font_size=40, color=AMBAR).next_to(pared2, RIGHT, buff=0.3)
        self.play(FadeIn(r2), run_time=0.4)
        ab = DashedLine(A[0].get_right(), B[0].get_left(), stroke_width=5, color=AMBAR, dash_length=0.15)
        self.play(Create(ab), Flash(ab.get_center(), color=AMBAR, flash_radius=0.6), run_time=0.9)
        ley = tex(r"A\sim C\ \text{ y }\ B\sim C\;\Rightarrow\;A\sim B", font_size=46)
        degradado(ley, DEG_CALIDO)
        ley.move_to(DOWN * 1.9)
        self.play(Write(ley), run_time=1.1)
        rel = tex(r"\text{reflexiva}\cdot\text{sim\'etrica}\cdot\text{transitiva}", font_size=34, color=GRIS)
        rel.move_to(DOWN * 3.0)
        self.play(FadeIn(rel), run_time=0.5)
        kel = tex(r"T\,(\mathrm K)=t\,(^\circ\mathrm C)+273.15", font_size=42)
        degradado(kel, DEG_FRIO)
        kel.move_to(DOWN * 4.3)
        self.play(Write(kel), run_time=1.0)
        self.wait(1.0)

        final = tex(r"A\sim C,\ B\sim C\;\Rightarrow\;A\sim B", font_size=56)
        degradado(final, DEG_CALIDO + [VIOLETA])
        self.cierre(final, "cada clase de equivalencia comparte una temperatura")


class Termo3_EcuacionEstado(Clip):
    serie = "Termodinámica I · Tema 1"
    numero = "3/4"
    titulo = "La ecuación de estado"
    subtitulo = "una superficie en el espacio (p, V, T)"
    colores_titulo = [TURQUESA, CELESTE, AZUL, VIOLETA, MAGENTA]
    fondo = ("#0d3c86", "#2a1a66")

    def cuerpo(self):
        f = tex(r"f(p,V,T)=0", font_size=52)
        degradado(f, DEG_AZUL)
        f.move_to(UP * 4.1)
        self.play(Write(f), run_time=0.9)
        gi = tex(r"pV=nRT", font_size=52)
        degradado(gi, DEG_FRIO)
        gi.move_to(f)

        # superficie p(V,T) en alambre, proyectada a mano
        phi = ValueTracker(-0.9)
        centro = DOWN * 0.2
        esc = 1.2

        def proy(V, T, p):
            P = np.array([V - 2.2, T - 1.25, p * 0.55 - 1.0])
            a = phi.get_value()
            x = P[0] * np.cos(a) - P[1] * np.sin(a)
            yd = P[0] * np.sin(a) + P[1] * np.cos(a)
            el = 0.42
            y = P[2] * np.cos(el) + yd * np.sin(el)
            return centro + esc * np.array([x, y, 0])

        Ts = np.linspace(0.6, 2.0, 9)
        cols = color_gradient([AZUL, CELESTE, VIOLETA, MAGENTA, CORAL], len(Ts))

        def malla():
            g = VGroup()
            for V in np.linspace(0.7, 3.8, 8):
                pts = [proy(V, T, min(T / V * 2.4, 6)) for T in np.linspace(0.6, 2.0, 20)]
                l = VMobject(stroke_width=2, stroke_color=CIELO, stroke_opacity=0.35)
                l.set_points_smoothly(pts)
                g.add(l)
            for T, c in zip(Ts, cols):
                pts = [proy(V, T, min(T / V * 2.4, 6)) for V in np.linspace(0.7, 3.8, 40)]
                l = VMobject(stroke_width=4, stroke_color=c)
                l.set_points_smoothly(pts)
                g.add(l)
            o = proy(0.7, 0.6, 0)
            ejes3 = VGroup(
                Arrow(o, proy(4.1, 0.6, 0), buff=0, stroke_width=3, color=GRIS),
                Arrow(o, proy(0.7, 2.2, 0), buff=0, stroke_width=3, color=GRIS),
                Arrow(o, proy(0.7, 0.6, 6.4), buff=0, stroke_width=3, color=GRIS),
            )
            labs = VGroup(
                tex("V", font_size=32, color=GRIS).move_to(proy(4.4, 0.6, 0)),
                tex("T", font_size=32, color=GRIS).move_to(proy(0.7, 2.5, 0)),
                tex("p", font_size=32, color=GRIS).move_to(proy(0.7, 0.6, 6.9)),
            )
            return VGroup(g, ejes3, labs)

        sup = always_redraw(malla)
        self.play(TransformMatchingShapes(f, gi), FadeIn(sup), run_time=1.4)
        self.play(phi.animate.set_value(0.5), run_time=4.0, rate_func=smooth)
        lib = self.rotulo("con n fija: solo dos variables independientes", pos=DOWN * 4.3, size=26, color=CIELO)
        self.play(FadeIn(lib), phi.animate.set_value(0.0), run_time=1.6)
        sup.clear_updaters()
        self.limpiar(gi)

        # --- dos caminos, mismo cambio de estado --------------------------------
        ejes = Axes(x_range=[0.5, 4.5, 1], y_range=[0, 9, 2], x_length=7.2, y_length=4.4,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(UP * 0.6)
        lV = tex("V", font_size=32, color=GRIS).next_to(ejes.c2p(4.5, 0), UP, buff=0.1)
        lp = tex("p", font_size=32, color=GRIS).next_to(ejes.c2p(0.5, 9), RIGHT, buff=0.1)
        self.play(Create(ejes), FadeIn(lV, lp), run_time=0.7)
        e1, e2 = ejes.c2p(1, 8), ejes.c2p(4, 2)
        d1 = Dot(e1, radius=0.12, color=TURQUESA)
        d2 = Dot(e2, radius=0.12, color=MAGENTA)
        l1 = tex(r"1", font_size=34, color=TURQUESA).next_to(d1, UR, buff=0.1)
        l2 = tex(r"2", font_size=34, color=MAGENTA).next_to(d2, UR, buff=0.1)
        self.play(FadeIn(d1, scale=2), FadeIn(d2, scale=2), FadeIn(l1, l2), run_time=0.6)
        cA = ejes.plot(lambda V: 8 / V, x_range=[1, 4, 0.01], stroke_width=5).set_color([TURQUESA, CELESTE, MAGENTA])
        cB = VMobject(stroke_width=5)
        cB.set_points_as_corners([e1, ejes.c2p(1, 2), e2])
        cB.set_color([TURQUESA, AMBAR, MAGENTA])
        la = tex(r"\text{camino } A", font_size=30, color=CELESTE).move_to(ejes.c2p(2.6, 4.6))
        lb = tex(r"\text{camino } B", font_size=30, color=AMBAR).move_to(ejes.c2p(1.9, 1.3))
        self.play(Create(cA), FadeIn(la), run_time=1.3)
        self.play(Create(cB), FadeIn(lb), run_time=1.3)
        dz = tex(r"\Delta Z=Z(V_2,p_2)-Z(V_1,p_1)", font_size=40)
        degradado(dz, [TURQUESA, CELESTE, MAGENTA])
        dz.move_to(DOWN * 2.9)
        self.play(Write(dz), run_time=1.1)
        r = self.rotulo("los extremos fijan el cambio; el proceso fija el camino", pos=DOWN * 4.1, size=26, color=GRIS)
        self.play(FadeIn(r), run_time=0.5)
        vdw = tex(r"\Big(p+\frac{an^2}{V^2}\Big)(V-nb)=nRT", font_size=40, color=VIOLETA).move_to(DOWN * 5.2)
        self.play(FadeIn(vdw, shift=UP * 0.2), run_time=0.7)
        self.wait(1.0)

        final = tex(r"pV=nRT", font_size=70)
        degradado(final, DEG_ARCOIRIS)
        self.cierre(final, "baja densidad y lejos de la condensación")


class Termo4_Coeficientes(Clip):
    serie = "Termodinámica I · Tema 1"
    numero = "4/4"
    titulo = "Coeficientes de respuesta"
    subtitulo = "cómo reacciona V ante T y p"
    colores_titulo = [CELESTE, VIOLETA, MAGENTA, AMBAR]
    fondo = ("#0e3a80", "#401c58")

    def cuerpo(self):
        defs = VGroup(
            tex(r"\alpha\equiv\frac1V\Big(\frac{\partial V}{\partial T}\Big)_p", font_size=44, color=CORAL),
            tex(r"\kappa_T\equiv-\frac1V\Big(\frac{\partial V}{\partial p}\Big)_T", font_size=44, color=CELESTE),
            tex(r"\beta\equiv\frac1p\Big(\frac{\partial p}{\partial T}\Big)_V", font_size=44, color=VIOLETA),
        ).arrange(DOWN, buff=0.4).move_to(UP * 2.9)
        nombres = VGroup(
            texto("dilatación", size=22, color=CORAL),
            texto("compresibilidad", size=22, color=CELESTE),
            texto("piezotérmico", size=22, color=VIOLETA),
        )
        for n, d in zip(nombres, defs):
            n.next_to(d, RIGHT, buff=0.3)
        defs.shift(LEFT * 0.9); nombres.shift(LEFT * 0.9)
        for d, n in zip(defs, nombres):
            self.play(Write(d), FadeIn(n), run_time=0.9)

        cic = tex(r"\Big(\frac{\partial V}{\partial T}\Big)_p\Big(\frac{\partial T}{\partial p}\Big)_V\Big(\frac{\partial p}{\partial V}\Big)_T=-1",
                  font_size=40)
        degradado(cic, DEG_ARCOIRIS)
        cic.move_to(DOWN * 0.3)
        self.play(Write(cic), run_time=1.3)
        res = tex(r"\alpha=p\,\beta\,\kappa_T", font_size=56)
        degradado(res, [CORAL, VIOLETA, CELESTE])
        res.move_to(DOWN * 1.8)
        self.play(TransformFromCopy(cic, res), run_time=1.1)
        dv = tex(r"\frac{dV}{V}=\alpha\,dT-\kappa_T\,dp", font_size=48)
        degradado(dv, DEG_FRIO)
        dv.move_to(DOWN * 3.3)
        self.play(Write(dv), run_time=1.0)
        self.wait(0.8)
        self.limpiar(dv)
        self.play(dv.animate.move_to(UP * 4.0), run_time=0.7)

        # --- mercurio a volumen constante --------------------------------------
        datos = VGroup(
            tex(r"\alpha=18\times10^{-5}\,\mathrm{K^{-1}}", font_size=34, color=CORAL),
            tex(r"\kappa_T=39\times10^{-12}\,\mathrm{Pa^{-1}}", font_size=34, color=CELESTE),
            tex(r"\Delta T=1\,\mathrm K,\quad \Delta V=0", font_size=34, color=TINTA),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.25).move_to(UP * 2.3)
        self.play(LaggedStart(*[FadeIn(d, shift=RIGHT * 0.2) for d in datos], lag_ratio=0.3), run_time=1.1)

        # manómetro
        cen = DOWN * 1.2 + RIGHT * 1.4
        R = 1.7
        arco = Arc(radius=R, start_angle=PI * 1.25, angle=-PI * 1.5, arc_center=cen, stroke_width=10)
        arco.set_color([CELESTE, VIOLETA, MAGENTA, CORAL])
        marcas = VGroup()
        for k in range(11):
            a = PI * 1.25 - PI * 1.5 * k / 10
            marcas.add(Line(cen + 0.82 * R * np.array([np.cos(a), np.sin(a), 0]),
                            cen + 0.95 * R * np.array([np.cos(a), np.sin(a), 0]), stroke_width=3, color=TINTA))
        nums = VGroup(*[texto(str(v), size=18, color=GRIS).move_to(
            cen + 0.66 * R * np.array([np.cos(PI * 1.25 - PI * 1.5 * v / 50), np.sin(PI * 1.25 - PI * 1.5 * v / 50), 0]))
            for v in (0, 10, 20, 30, 40, 50)])
        ub = texto("bar", size=20, color=GRIS).move_to(cen + DOWN * 0.75)
        pres = ValueTracker(0)

        def aguja():
            a = PI * 1.25 - PI * 1.5 * pres.get_value() / 50
            tip = cen + 0.8 * R * np.array([np.cos(a), np.sin(a), 0])
            return VGroup(Line(cen, tip, stroke_width=6, color=AMBAR), Dot(cen, radius=0.12, color=AMBAR))

        ag = always_redraw(aguja)
        # termómetro
        tb = RoundedRectangle(width=0.4, height=3.0, corner_radius=0.2).move_to(cen + LEFT * 3.4 + UP * 0.2)
        tb.set_stroke(TINTA, 3)
        bulbo = Circle(radius=0.35).next_to(tb, DOWN, buff=-0.15).set_fill(CORAL, 1).set_stroke(TINTA, 3)
        nivel = ValueTracker(0.8)
        liquido = always_redraw(lambda: Rectangle(width=0.22, height=nivel.get_value(), stroke_width=0)
                                .set_fill([CORAL, AMBAR], 1).align_to(tb, DOWN).shift(UP * 0.1).set_x(tb.get_x()))
        lT = tex(r"T+1\,\mathrm K", font_size=30, color=CORAL).next_to(tb, UP, buff=0.15)
        self.play(Create(arco), FadeIn(marcas, nums, ub), FadeIn(ag), FadeIn(tb, bulbo, liquido), run_time=1.0)
        self.play(nivel.animate.set_value(2.2), pres.animate.set_value(46.2), FadeIn(lT), run_time=2.6, rate_func=smooth)
        dp = tex(r"\Delta p=\frac{\alpha}{\kappa_T}\Delta T=4.62\,\mathrm{MPa}\approx46\,\mathrm{bar}", font_size=40)
        degradado(dp, DEG_CALIDO)
        dp.move_to(DOWN * 4.3)
        self.play(Write(dp), run_time=1.2)
        rr = self.rotulo("una dilatación impedida dispara la presión", pos=DOWN * 5.4, size=26, color=CORAL)
        self.play(FadeIn(rr), run_time=0.5)
        self.wait(0.8)
        ag.clear_updaters(); liquido.clear_updaters()

        final = tex(r"\frac{\Delta V}{V}\approx\alpha\,\Delta T-\kappa_T\,\Delta p", font_size=56)
        degradado(final, DEG_FRIO)
        self.cierre(final, "solo dos de los tres coeficientes son independientes")
