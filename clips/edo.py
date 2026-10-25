"""Clips: EDO lineales de orden superior."""

from estilo import *


class EDO1_Linealidad(Clip):
    serie = "EDO lineales · orden n"
    numero = "1/4"
    titulo = "Todo es linealidad"
    subtitulo = "el operador L y el espacio de soluciones"

    def cuerpo(self):
        eq = tex(r"L[y]", r"=", r"a_n y^{(n)}+\dots+a_1y'+a_0y", r"=", r"b(x)", font_size=46)
        eq[0].set_color(CELESTE)
        eq[4].set_color(AMBAR)
        eq.move_to(UP * 3.4)
        self.play(Write(eq), run_time=1.6)

        lin = tex(r"L[\alpha y_1+\beta y_2]", r"=", r"\alpha L[y_1]+\beta L[y_2]", font_size=46)
        degradado(lin, DEG_FRIO)
        lin.move_to(UP * 2.0)
        self.play(FadeIn(lin, shift=DOWN * 0.3), run_time=1.0)
        self.wait(0.6)

        estr = tex(r"y", r"=", r"\sum_{i=1}^{n} c_i\,\hat y_i", r"+", r"y_p", font_size=54)
        estr[2].set_color(CELESTE)
        estr[4].set_color(AMBAR)
        estr.move_to(UP * 0.4)
        llave = Brace(estr[2], DOWN, color=CELESTE)
        lab = tex(r"y_h\in\ker L", font_size=36, color=CELESTE).next_to(llave, DOWN, buff=0.15)
        llave2 = Brace(estr[4], DOWN, color=AMBAR)
        lab2 = texto("particular", size=24, color=AMBAR).next_to(llave2, DOWN, buff=0.2)
        self.play(TransformMatchingTex(lin.copy(), estr), run_time=1.3)
        self.play(GrowFromCenter(llave), FadeIn(lab), GrowFromCenter(llave2), FadeIn(lab2), run_time=1.0)
        self.wait(0.8)
        self.limpiar()

        # --- dim ker L = n: ejemplo y'' + y = 0 -----------------------------
        ej = tex(r"y''+y=0", r"\;\Rightarrow\;", r"y=c_1\cos x+c_2\sin x", font_size=42)
        ej[2].set_color_by_gradient(CELESTE, VIOLETA)
        ej.move_to(UP * 4.0)
        self.play(Write(ej), run_time=1.2)

        plano = NumberPlane(
            x_range=[-2, 2, 1], y_range=[-2, 2, 1], x_length=4, y_length=4,
            background_line_style={"stroke_color": AZUL, "stroke_opacity": 0.35, "stroke_width": 1.5},
            axis_config={"stroke_color": GRIS},
        ).move_to(UP * 1.1)
        e1 = tex(r"c_1", font_size=30, color=CELESTE).next_to(plano.c2p(2, 0), DOWN, buff=0.1)
        e2 = tex(r"c_2", font_size=30, color=VIOLETA).next_to(plano.c2p(0, 2), LEFT, buff=0.1)
        ang = ValueTracker(0.6)
        rad = ValueTracker(1.5)

        def coef():
            return rad.get_value() * np.cos(ang.get_value()), rad.get_value() * np.sin(ang.get_value())

        flecha = always_redraw(lambda: Arrow(
            plano.c2p(0, 0), plano.c2p(*coef()), buff=0, stroke_width=6,
            max_tip_length_to_length_ratio=0.15).set_color([CELESTE, MAGENTA]))
        punto = always_redraw(lambda: Dot(plano.c2p(*coef()), radius=0.08, color=MAGENTA))
        ejes = Axes(x_range=[0, 4 * PI, PI], y_range=[-2.2, 2.2, 1], x_length=7.6, y_length=3.0,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(DOWN * 3.2)

        def curva():
            c1, c2 = coef()
            g = ejes.plot(lambda x: c1 * np.cos(x) + c2 * np.sin(x), x_range=[0, 4 * PI], stroke_width=5)
            g.set_color([CELESTE, AZUL, VIOLETA, MAGENTA])
            return g

        graf = always_redraw(curva)
        flecha_link = tex(r"\Phi", font_size=40, color=AMBAR).move_to(DOWN * 1.35)
        self.play(Create(plano), FadeIn(e1, e2), Create(ejes), run_time=1.2)
        self.play(GrowArrow(flecha), FadeIn(punto), Create(graf), FadeIn(flecha_link), run_time=1.0)
        self.play(ang.animate.set_value(0.6 + 2 * PI), run_time=4.0, rate_func=smooth)
        self.play(rad.animate.set_value(0.6), run_time=1.0)
        self.play(rad.animate.set_value(1.9), ang.animate.set_value(0.6 + 2.6 * PI), run_time=1.4)

        iso = tex(r"\ker L\;\cong\;\mathbb{R}^n", font_size=52)
        degradado(iso, DEG_ARCOIRIS)
        iso.move_to(DOWN * 5.3)
        self.play(Write(iso), run_time=1.0)
        self.wait(0.6)
        for m in (flecha, punto, graf):
            m.clear_updaters()

        final = tex(r"\{\hat y_i\}\text{ base}\iff\det W(x_0)\neq 0", font_size=46)
        degradado(final, DEG_AZUL)
        self.cierre(final, "n soluciones independientes, n constantes")


class EDO2_Oscilador(Clip):
    serie = "EDO lineales · orden n"
    numero = "2/4"
    titulo = "El ansatz exponencial"
    subtitulo = "la exponencial es autofunción de D"

    def cuerpo(self):
        a = tex(r"D\,e^{\lambda x}", r"=", r"\lambda\, e^{\lambda x}", font_size=56)
        a[0].set_color(CELESTE); a[2].set_color(VIOLETA)
        a.move_to(UP * 1.6)
        self.play(Write(a), run_time=1.2)
        b = tex(r"p(D)\,e^{\lambda x}", r"=", r"p(\lambda)\, e^{\lambda x}", font_size=56)
        b[0].set_color(CELESTE); b[2].set_color(VIOLETA)
        b.move_to(a)
        self.play(TransformMatchingTex(a, b), run_time=1.0)
        c = tex(r"p(\lambda)=a_n\lambda^n+\dots+a_1\lambda+a_0=0", font_size=42)
        degradado(c, DEG_FRIO)
        c.next_to(b, DOWN, buff=0.7)
        r = self.rotulo("es solución  ⟺  λ es raíz de la ecuación característica", pos=DOWN * 1.6, size=24, color=GRIS)
        self.play(FadeIn(c, shift=UP * 0.3), run_time=0.9)
        self.play(FadeIn(r), run_time=0.5)
        self.wait(0.8)
        self.play(FadeOut(r), run_time=0.3)
        self.play(FadeOut(b), FadeOut(c), run_time=0.5)

        # --- oscilador amortiguado ----------------------------------------
        osc = tex(r"y''+\nu\omega\,y'+\omega^2y=0", font_size=48)
        degradado(osc, DEG_AZUL)
        osc.move_to(UP * 4.0)
        raiz = tex(r"\lambda_\pm=\tfrac{\omega}{2}\big(-\nu\pm\sqrt{\nu^2-4}\big)", font_size=40, color=TINTA)
        raiz.next_to(osc, DOWN, buff=0.35)
        self.play(Write(osc), run_time=1.0)
        self.play(FadeIn(raiz, shift=UP * 0.2), run_time=0.8)

        plano = ComplexPlane(
            x_range=[-3, 1, 1], y_range=[-1.5, 1.5, 1], x_length=6.4, y_length=3.6,
            background_line_style={"stroke_color": AZUL, "stroke_opacity": 0.3, "stroke_width": 1.2},
            axis_config={"stroke_color": GRIS},
        ).move_to(UP * 0.35)
        re_lab = tex(r"\mathrm{Re}\,\lambda", font_size=26, color=GRIS).next_to(plano.c2p(1, 0), DOWN, buff=0.1)
        im_lab = tex(r"\mathrm{Im}\,\lambda", font_size=26, color=GRIS).next_to(plano.c2p(0, 1.5), RIGHT, buff=0.1)
        nu = ValueTracker(0.35)
        w = 1.0

        def raices():
            n = nu.get_value()
            d = n * n - 4
            if d < 0:
                return complex(-n / 2, np.sqrt(-d) / 2), complex(-n / 2, -np.sqrt(-d) / 2)
            return complex((-n + np.sqrt(d)) / 2, 0), complex((-n - np.sqrt(d)) / 2, 0)

        def color_reg():
            n = nu.get_value()
            if abs(n - 2) < 0.04:
                return AMBAR
            return CELESTE if n < 2 else MAGENTA

        def puntos():
            r1, r2 = raices()
            g = VGroup()
            for r in (r1, r2):
                p = Dot(plano.n2p(r), radius=0.11, color=color_reg())
                g.add(brillo(Circle(radius=0.12).move_to(p), color_reg(), capas=5, ancho=20, opacidad=0.18), p)
            return g

        traza = TracedPath(lambda: plano.n2p(raices()[0]), stroke_color=CELESTE, stroke_width=2, stroke_opacity=0.5)
        traza2 = TracedPath(lambda: plano.n2p(raices()[1]), stroke_color=VIOLETA, stroke_width=2, stroke_opacity=0.5)
        pts = always_redraw(puntos)

        ejes = Axes(x_range=[0, 14, 2], y_range=[-1.1, 1.1, 1], x_length=7.6, y_length=3.0,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(DOWN * 3.4)

        def sol(x):
            n = nu.get_value()
            r1, r2 = raices()
            if abs(n - 2) < 1e-3:
                return (1 + x) * np.exp(-x)
            if n < 2:
                g, W = -r1.real, r1.imag
                return np.exp(-g * x) * (np.cos(W * x) + g / W * np.sin(W * x))
            l1, l2 = r1.real, r2.real
            return (l2 * np.exp(l1 * x) - l1 * np.exp(l2 * x)) / (l2 - l1)

        graf = always_redraw(lambda: ejes.plot(sol, x_range=[0, 14, 0.05], stroke_width=5, color=color_reg()))

        def regimen():
            n = nu.get_value()
            if abs(n - 2) < 0.04:
                s, c = "crítico: raíz doble", AMBAR
            elif n < 2:
                s, c = "subamortiguado: oscila", CELESTE
            else:
                s, c = "sobreamortiguado: no oscila", MAGENTA
            t = texto(s, size=30, color=c, slant=ITALIC).move_to(DOWN * 5.4)
            v = tex(r"\nu=%.2f" % n, font_size=34, color=c).move_to(DOWN * 1.65 + RIGHT * 2.9)
            return VGroup(t, v)

        reg = always_redraw(regimen)
        self.play(Create(plano), FadeIn(re_lab, im_lab), Create(ejes), run_time=1.0)
        self.add(traza, traza2)
        self.play(FadeIn(pts), Create(graf), FadeIn(reg), run_time=0.8)
        self.play(nu.animate.set_value(1.2), run_time=2.2, rate_func=linear)
        self.play(nu.animate.set_value(2.0), run_time=2.2, rate_func=smooth)
        self.wait(1.0)
        self.play(nu.animate.set_value(3.2), run_time=2.6, rate_func=smooth)
        self.wait(0.6)
        for m in (pts, graf, reg, traza, traza2):
            m.clear_updaters()

        final = tex(r"e^{-\gamma x}\big(A\cos\Omega x+B\sin\Omega x\big)", font_size=46)
        degradado(final, DEG_FRIO)
        self.cierre(final, "el discriminante decide si el sistema oscila")


class EDO3_RaicesMultiples(Clip):
    serie = "EDO lineales · orden n"
    numero = "3/4"
    titulo = "Raíces múltiples"
    subtitulo = "¿de dónde sale el factor x?"
    colores_titulo = DEG_CALIDO + [VIOLETA]

    def cuerpo(self):
        p = tex(r"L=a_n(D-\lambda_1)^{m_1}\cdots(D-\lambda_r)^{m_r}", font_size=42)
        degradado(p, DEG_AZUL)
        p.move_to(UP * 3.9)
        self.play(Write(p), run_time=1.3)

        lema = tex(r"(D-\lambda)\big(e^{\lambda x}g\big)", r"=", r"e^{\lambda x}\,g'", font_size=50)
        lema[0].set_color(CELESTE); lema[2].set_color(AMBAR)
        lema.move_to(UP * 2.5)
        self.play(FadeIn(lema, shift=DOWN * 0.3), run_time=1.0)
        nota = self.rotulo("conjugar con la exponencial: D − λ actúa como d/dx", pos=UP * 1.55, size=26, color=GRIS)
        self.play(FadeIn(nota), run_time=0.6)
        lema_m = tex(r"(D-\lambda)^m\big(e^{\lambda x}g\big)", r"=", r"e^{\lambda x}\,g^{(m)}", font_size=50)
        lema_m[0].set_color(CELESTE); lema_m[2].set_color(AMBAR)
        lema_m.move_to(lema)
        self.play(TransformMatchingTex(lema, lema_m), run_time=1.1)
        g = tex(r"g^{(m)}=0", r"\iff", r"g=c_0+c_1x+\dots+c_{m-1}x^{m-1}", font_size=38)
        g[2].set_color_by_gradient(AMBAR, CORAL)
        g.move_to(UP * 0.5)
        self.play(Write(g), run_time=1.3)
        ker = tex(r"\ker(D-\lambda)^m=\mathrm{span}\{e^{\lambda x},\,x e^{\lambda x},\dots,x^{m-1}e^{\lambda x}\}",
                  font_size=36)
        degradado(ker, DEG_ARCOIRIS)
        ker.move_to(DOWN * 0.6)
        self.play(Write(ker), run_time=1.5)
        self.wait(0.8)
        self.play(FadeOut(VGroup(p, nota, lema_m, g)), ker.animate.move_to(UP * 4.0), run_time=0.8)

        ejes = Axes(x_range=[0, 8, 1], y_range=[0, 1.1, 0.5], x_length=7.6, y_length=3.6,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(UP * 0.9)
        cols = [CELESTE, VIOLETA, MAGENTA]
        nombres = [r"e^{-x}", r"x\,e^{-x}", r"\tfrac{x^2}{2}e^{-x}"]
        self.play(Create(ejes), run_time=0.6)
        curvas = VGroup()
        for k, (c, n) in enumerate(zip(cols, nombres)):
            f = (lambda k: lambda x: x ** k * np.exp(-x) / [1, 1, 2][k])(k)
            cv = ejes.plot(f, x_range=[0, 8], stroke_width=5, color=c)
            l = tex(n, font_size=32, color=c).move_to(ejes.c2p(5.6, 0.95 - 0.22 * k))
            curvas.add(cv)
            self.play(Create(cv), FadeIn(l), run_time=0.8)

        # comparación de regímenes: el crítico vuelve antes sin oscilar
        ejes2 = Axes(x_range=[0, 10, 1], y_range=[-0.5, 1.1, 0.5], x_length=7.6, y_length=3.2,
                     axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(DOWN * 3.3)
        sub = ejes2.plot(lambda x: np.exp(-0.4 * x) * (np.cos(0.92 * x) + 0.4 / 0.92 * np.sin(0.92 * x)),
                         x_range=[0, 10], stroke_width=3, color=CELESTE).set_stroke(opacity=0.55)
        l1, l2 = -0.27, -3.73
        sob = ejes2.plot(lambda x: (l2 * np.exp(l1 * x) - l1 * np.exp(l2 * x)) / (l2 - l1),
                         x_range=[0, 10], stroke_width=3, color=MAGENTA).set_stroke(opacity=0.55)
        cri = ejes2.plot(lambda x: (1 + x) * np.exp(-x), x_range=[0, 10], stroke_width=7, color=AMBAR)
        lab = tex(r"(c_0+c_1x)\,e^{-\omega x}", font_size=34, color=AMBAR).move_to(ejes2.c2p(6.3, 0.85))
        self.play(Create(ejes2), Create(sub), Create(sob), run_time=1.2)
        self.play(Create(cri), FadeIn(lab), FadeIn(brillo(cri, AMBAR, capas=5, ancho=22, opacidad=0.12)), run_time=1.4)
        r = self.rotulo("ν = 2: el regreso al equilibrio más rápido sin oscilar", pos=DOWN * 5.5, size=26, color=AMBAR)
        self.play(FadeIn(r), run_time=0.6)
        self.wait(1.2)

        final = tex(r"y_h=\sum_{k}\Big(\sum_{j<m_k} c_{k,j}\,x^j\Big)e^{\lambda_k x}", font_size=48)
        degradado(final, DEG_AZUL)
        self.cierre(final, "cada raíz de multiplicidad m aporta m soluciones")


class EDO4_VariacionConstantes(Clip):
    serie = "EDO lineales · orden n"
    numero = "4/4"
    titulo = "Variación de constantes"
    subtitulo = "Euler · Lagrange"
    colores_titulo = [TURQUESA, CELESTE, VIOLETA]

    def cuerpo(self):
        a = tex(r"y_h=\sum_i k_i\,\hat y_i", font_size=52)
        a.set_color(CELESTE)
        a.move_to(UP * 3.9)
        self.play(Write(a), run_time=1.0)
        b = tex(r"y_p=\sum_i k_i(x)\,\hat y_i(x)", font_size=52)
        degradado(b, [CELESTE, AMBAR])
        b.move_to(a)
        self.play(TransformMatchingShapes(a, b), run_time=1.2)
        r = self.rotulo("promovemos las constantes a funciones", pos=UP * 2.9, size=26, color=GRIS)
        self.play(FadeIn(r), run_time=0.5)

        W = tex(r"""\begin{pmatrix}\hat y_1&\cdots&\hat y_n\\ \hat y_1'&\cdots&\hat y_n'\\
                 \vdots&&\vdots\\ \hat y_1^{(n-1)}&\cdots&\hat y_n^{(n-1)}\end{pmatrix}""",
                r"\begin{pmatrix}k_1'\\ \vdots\\ \vdots \\ k_n'\end{pmatrix}", r"=",
                r"\begin{pmatrix}0\\ \vdots\\ 0\\ b/a_n\end{pmatrix}", font_size=36)
        W[0].set_color_by_gradient(CELESTE, AZUL, VIOLETA)
        W[1].set_color(AMBAR)
        W[3].set_color(CORAL)
        W.move_to(UP * 0.9)
        lw = Brace(W[0], DOWN, color=CELESTE)
        lwl = tex(r"W(x)\ \text{wronskiana}", font_size=30, color=CELESTE).next_to(lw, DOWN, buff=0.12)
        self.play(Write(W), run_time=1.8)
        self.play(GrowFromCenter(lw), FadeIn(lwl), run_time=0.7)
        sol = tex(r"y_p(x)=\hat{\mathbf y}^T(x)\int_{x_0}^{x}W^{-1}(s)\,\mathbf b(s)\,ds", font_size=42)
        degradado(sol, DEG_FRIO)
        sol.move_to(DOWN * 2.5)
        self.play(Write(sol), run_time=1.4)
        self.wait(1.0)
        self.limpiar()

        ej = tex(r"y''+\omega^2y=b(x)", font_size=48)
        degradado(ej, DEG_AZUL)
        ej.move_to(UP * 4.0)
        k = tex(r"y_p(x)=\frac1\omega\int_{x_0}^{x}", r"\sin\omega(x-s)", r"\,b(s)\,ds", font_size=46)
        k[1].set_color(MAGENTA)
        k.move_to(UP * 2.4)
        self.play(Write(ej), run_time=0.8)
        self.play(Write(k), run_time=1.4)

        ejes = Axes(x_range=[0, 13, 2], y_range=[0, 2.3, 1], x_length=7.6, y_length=3.4,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(DOWN * 1.2)
        bfun = ejes.plot(lambda x: 1.0, x_range=[0, 13], stroke_width=3, color=AMBAR).set_opacity(0.7)
        bl = tex(r"b=1", font_size=30, color=AMBAR).next_to(ejes.c2p(13, 1), UP, buff=0.1)
        self.play(Create(ejes), Create(bfun), FadeIn(bl), run_time=1.0)
        yp = ejes.plot(lambda x: 1 - np.cos(x), x_range=[0, 13, 0.03], stroke_width=6)
        yp.set_color([TURQUESA, CELESTE, AZUL, VIOLETA, MAGENTA])
        yl = tex(r"y_p=\frac{1-\cos\omega x}{\omega^2}", font_size=36).move_to(DOWN * 4.0)
        degradado(yl, DEG_FRIO)
        self.play(Create(yp), FadeIn(brillo(yp, CELESTE, capas=4, ancho=18, opacidad=0.1)), run_time=2.2)
        self.play(Write(yl), run_time=0.9)
        nucleo = SurroundingRectangle(k[1], color=MAGENTA, buff=0.1, corner_radius=0.1)
        r2 = self.rotulo("ese núcleo es una función de Green", pos=DOWN * 5.3, size=30, color=MAGENTA)
        self.play(Create(nucleo), FadeIn(r2), run_time=0.8)
        self.wait(1.4)

        final = tex(r"W\,\mathbf k'=\mathbf b", r"\quad\Longrightarrow\quad", r"\mathbf k=\int W^{-1}\mathbf b", font_size=46)
        degradado(final, DEG_AZUL)
        self.cierre(final, "vale siempre que se conozca la homogénea")
