"""Clips: el método de la función de Green."""

from estilo import *


def fuente(x):
    return 1.15 * np.exp(-((x - 2.6) ** 2) / 1.1) + 0.7 * np.exp(-((x - 6.2) ** 2) / 0.5)


class Green1_Impulsos(Clip):
    serie = "Función de Green"
    numero = "1/2"
    titulo = "Fuente = suma de impulsos"
    subtitulo = "linealidad ⇒ superposición"
    colores_titulo = [AMBAR, CORAL, MAGENTA, VIOLETA]
    fondo = ("#163a80", "#4a1650")

    def cuerpo(self):
        sup = tex(r"b=\sum_k b_k", r"\;\Rightarrow\;", r"y_p=\sum_k y_{p,k}", font_size=46)
        sup[0].set_color(AMBAR); sup[2].set_color(CELESTE)
        sup.move_to(UP * 4.0)
        self.play(Write(sup), run_time=1.2)

        ejes = Axes(x_range=[0, 10, 1], y_range=[0, 1.4, 0.5], x_length=7.6, y_length=2.6,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(UP * 1.5)
        bl = tex(r"b(x)", font_size=32, color=AMBAR).move_to(ejes.c2p(8.6, 1.15))
        b = ejes.plot(fuente, x_range=[0, 10, 0.02], stroke_width=5)
        b.set_color([AMBAR, CORAL, MAGENTA])
        self.play(Create(ejes), Create(b), FadeIn(bl), run_time=1.3)

        dx = 0.4
        rects = ejes.get_riemann_rectangles(b, x_range=[0, 9.6], dx=dx, stroke_width=1,
                                            stroke_color="#02040c", fill_opacity=0.85)
        rects.set_color_by_gradient(TURQUESA, CELESTE, AZUL, VIOLETA, MAGENTA, CORAL)
        self.play(Create(rects), run_time=1.3)
        xs = np.arange(0, 9.6, dx) + dx / 2
        picos = VGroup()
        for r, xk in zip(rects, xs):
            l = Line(ejes.c2p(xk, 0), ejes.c2p(xk, fuente(xk)), stroke_width=4, color=r.get_fill_color())
            d = Dot(ejes.c2p(xk, fuente(xk)), radius=0.05, color=r.get_fill_color())
            picos.add(VGroup(l, d))
        self.play(ReplacementTransform(rects, picos), b.animate.set_stroke(opacity=0.25), run_time=1.3)
        filt = tex(r"b(x)=\int b(\tilde x)\,\delta(x-\tilde x)\,d\tilde x", font_size=42)
        degradado(filt, DEG_CALIDO)
        filt.move_to(sup)
        self.play(FadeOut(sup, shift=UP * 0.3), FadeIn(filt, shift=UP * 0.3), run_time=1.0)
        self.wait(0.5)

        green = tex(r"L_x\,G(x,\tilde x)=\delta(x-\tilde x)", font_size=42)
        degradado(green, DEG_FRIO)
        green.move_to(DOWN * 0.6)
        osc = tex(r"y''+y=b\;\Rightarrow\;G=\theta(x-\tilde x)\,\sin(x-\tilde x)", font_size=34, color=GRIS)
        osc.next_to(green, DOWN, buff=0.3)
        self.play(Write(green), run_time=1.1)
        self.play(FadeIn(osc), run_time=0.6)

        ejes2 = Axes(x_range=[0, 10, 1], y_range=[-1.6, 2.4, 1], x_length=7.6, y_length=3.0,
                     axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(DOWN * 3.7)
        self.play(Create(ejes2), run_time=0.6)
        cols = [p[0].get_color() for p in picos]

        def resp(k):
            xk = xs[k]
            amp = fuente(xk) * dx
            return ejes2.plot(lambda x: amp * np.sin(x - xk) * (x > xk), x_range=[0, 10, 0.03],
                              stroke_width=2, color=cols[k]).set_stroke(opacity=0.6)

        resps = VGroup(*[resp(k) for k in range(len(xs))])
        n = ValueTracker(0)

        def suma(x, m):
            tot = 0.0
            for k in range(m):
                if x > xs[k]:
                    tot += fuente(xs[k]) * dx * np.sin(x - xs[k])
            return tot

        def total():
            m = int(n.get_value())
            g = ejes2.plot(lambda x: suma(x, m), x_range=[0, 10, 0.03], stroke_width=6)
            g.set_color([TURQUESA, CELESTE, TINTA])
            return g

        tot = always_redraw(total)
        self.add(tot)
        self.play(
            LaggedStart(*[AnimationGroup(Indicate(picos[k], color=TINTA, scale_factor=1.4), Create(resps[k]))
                          for k in range(len(xs))], lag_ratio=0.25),
            n.animate.set_value(len(xs)),
            run_time=5.0, rate_func=linear,
        )
        tot.clear_updaters()
        lab = tex(r"y_p(x)=\int G(x,\tilde x)\,b(\tilde x)\,d\tilde x", font_size=40)
        degradado(lab, [TURQUESA, CELESTE, TINTA])
        lab.move_to(DOWN * 5.75)
        self.play(resps.animate.set_stroke(opacity=0.18), Write(lab), run_time=1.2)
        self.wait(1.4)

        final = tex(r"y_p(x)=\int G(x,\tilde x)\,b(\tilde x)\,d\tilde x", font_size=50)
        degradado(final, DEG_ARCOIRIS)
        self.cierre(final, "G depende del operador, no de la fuente: se calcula una vez")


class Green2_SaltoCoulomb(Clip):
    serie = "Función de Green"
    numero = "2/2"
    titulo = "Saltos, causalidad y Coulomb"
    subtitulo = "la misma idea en 1D y en 3D"
    colores_titulo = [CELESTE, VIOLETA, MAGENTA]
    fondo = ("#103a7a", "#2d1a6a")

    def cuerpo(self):
        salto = tex(r"\Big[\partial_x^{\,n-1}G\Big]_{\tilde x^-}^{\tilde x^+}=\frac{1}{a_n(\tilde x)}", font_size=46)
        degradado(salto, DEG_FRIO)
        salto.move_to(UP * 3.9)
        self.play(Write(salto), run_time=1.3)
        r = self.rotulo("la delta solo se equilibra con un salto en la derivada más alta",
                        pos=UP * 2.75, size=24, color=GRIS)
        self.play(FadeIn(r), run_time=0.5)

        ejes = Axes(x_range=[0, 10, 1], y_range=[-1.2, 1.2, 1], x_length=7.6, y_length=2.6,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(UP * 0.9)
        ejes_d = Axes(x_range=[0, 10, 1], y_range=[-1.2, 1.2, 1], x_length=7.6, y_length=2.2,
                      axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(DOWN * 2.2)
        xt = ValueTracker(3.0)

        def G():
            a = xt.get_value()
            g = ejes.plot(lambda x: np.sin(x - a) * (x > a), x_range=[0, 10, 0.01], stroke_width=5)
            g.set_color([CELESTE, AZUL, VIOLETA])
            return g

        def Gp():
            a = xt.get_value()
            izq = ejes_d.plot(lambda x: 0 * x, x_range=[0, a], stroke_width=5, color=MAGENTA)
            der = ejes_d.plot(lambda x: np.cos(x - a), x_range=[a, 10, 0.01], stroke_width=5, color=MAGENTA)
            salto_l = DashedLine(ejes_d.c2p(a, 0), ejes_d.c2p(a, 1), color=AMBAR, stroke_width=4)
            return VGroup(izq, der, salto_l)

        def marca():
            a = xt.get_value()
            d = Dot(ejes.c2p(a, 0), radius=0.09, color=AMBAR)
            l = tex(r"\tilde x", font_size=30, color=AMBAR).next_to(d, DOWN, buff=0.15)
            return VGroup(brillo(Circle(radius=0.1).move_to(d), AMBAR, 5, 22, 0.2), d, l)

        lg = tex(r"G=\theta(x-\tilde x)\,\tfrac{\sin\omega(x-\tilde x)}{\omega}", font_size=32, color=CELESTE)
        lg.move_to([0, -0.78, 0]).align_to(ejes, RIGHT)
        lgp = tex(r"\partial_x G", font_size=32, color=MAGENTA).next_to(ejes_d, UP, buff=0.0).align_to(ejes_d, RIGHT)
        gg, gp, mk = always_redraw(G), always_redraw(Gp), always_redraw(marca)
        self.play(Create(ejes), Create(ejes_d), FadeIn(lg, lgp), run_time=0.9)
        self.play(Create(gg), Create(gp), FadeIn(mk), run_time=1.3)
        sl = tex(r"\text{salto}=1", font_size=32, color=AMBAR).move_to(DOWN * 4.0)
        cz = self.rotulo("causal: nada responde antes del impulso", pos=DOWN * 4.8, size=26, color=CIELO)
        self.play(FadeIn(sl), FadeIn(cz), run_time=0.6)
        self.play(xt.animate.set_value(5.5), run_time=1.8)
        self.play(xt.animate.set_value(2.0), run_time=1.6)
        for m in (gg, gp, mk):
            m.clear_updaters()
        self.limpiar()

        # --- variación de constantes = Green -------------------------------
        vc = tex(r"G(x,\tilde x)=\theta(x-\tilde x)\,\hat{\mathbf y}^T(x)\,W^{-1}(\tilde x)\,\frac{\mathbf e_n}{a_n(\tilde x)}",
                 font_size=38)
        degradado(vc, DEG_AZUL)
        vc.move_to(UP * 3.9)
        dos = self.rotulo("variación de constantes y Green: el mismo cálculo", pos=UP * 2.8, size=26, color=GRIS)
        self.play(Write(vc), run_time=1.4)
        self.play(FadeIn(dos), run_time=0.5)

        # --- Coulomb ---------------------------------------------------------
        centro = DOWN * 0.6
        nube = Ellipse(width=4.2, height=2.6).move_to(centro + LEFT * 1.2)
        nube.set_fill([AZUL, VIOLETA], opacity=0.25).set_stroke([CELESTE, VIOLETA], width=2)
        rng = np.random.default_rng(4)
        cargas = VGroup()
        for _ in range(14):
            ang, rr = rng.uniform(0, TAU), np.sqrt(rng.uniform(0, 0.8))
            p = nube.get_center() + np.array([2.1 * rr * np.cos(ang), 1.3 * rr * np.sin(ang), 0])
            cargas.add(Dot(p, radius=0.07, color=rng.choice([CIELO, CELESTE, VIOLETA, MAGENTA])))
        rho = tex(r"\rho(\mathbf r')", font_size=34, color=VIOLETA).next_to(nube, UP, buff=0.1)
        self.play(DrawBorderThenFill(nube), FadeIn(rho), run_time=0.9)
        self.play(LaggedStart(*[GrowFromCenter(c) for c in cargas], lag_ratio=0.08), run_time=1.0)
        ondas = VGroup()
        for c in cargas:
            for k in range(2):
                o = Circle(radius=0.05, color=c.get_color(), stroke_width=2).move_to(c)
                ondas.add(o)
        self.play(LaggedStart(*[o.animate.scale(22).set_stroke(opacity=0) for o in ondas], lag_ratio=0.03),
                  run_time=2.0)
        self.remove(ondas)
        sonda = Dot(centro + RIGHT * 2.9 + UP * 0.6, radius=0.11, color=AMBAR)
        sl = tex(r"\mathbf r", font_size=34, color=AMBAR).next_to(sonda, UR, buff=0.05)
        rayos = VGroup(*[Line(c.get_center(), sonda.get_center(), stroke_width=1.5, color=c.get_color())
                         .set_opacity(0.6) for c in cargas])
        self.play(FadeIn(sonda, sl), LaggedStart(*[Create(r) for r in rayos], lag_ratio=0.05), run_time=1.3)
        pois = tex(r"\nabla^2 G=-\delta^3(\mathbf r-\mathbf r')\;\Rightarrow\;G=\frac{1}{4\pi|\mathbf r-\mathbf r'|}",
                   font_size=38)
        degradado(pois, DEG_FRIO)
        pois.move_to(DOWN * 3.5)
        self.play(Write(pois), run_time=1.4)
        cou = self.rotulo("es la ley de Coulomb: suma de cargas puntuales", pos=DOWN * 5.0, size=28, color=AMBAR)
        self.play(FadeIn(cou), run_time=0.6)
        self.wait(1.0)

        final = tex(r"\phi(\mathbf r)=\frac{1}{\varepsilon_0}\int G(\mathbf r,\mathbf r')\,\rho(\mathbf r')\,d^3r'",
                    font_size=48)
        degradado(final, DEG_ARCOIRIS)
        self.cierre(final, "respuesta a un impulso × fuente, sumado sobre todo el espacio")
