"""Clips: Álgebra Lineal y Geometría II (estilo «noche»)."""

from estilo_noche import *

ClipNoche.total = 11


# ---------------------------------------------------------------------------
# Utilidades de geometría en el plano
# ---------------------------------------------------------------------------
def recortar(p0, p1, B):
    """Recorta el segmento p0-p1 a la caja [-B, B]^2 (Liang-Barsky)."""
    x0, y0 = p0
    dx, dy = p1[0] - x0, p1[1] - y0
    t0, t1 = 0.0, 1.0
    for p, q in ((-dx, x0 + B), (dx, B - x0), (-dy, y0 + B), (dy, B - y0)):
        if abs(p) < 1e-12:
            if q < 0:
                return None
        else:
            r = q / p
            if p < 0:
                t0 = max(t0, r)
            else:
                t1 = min(t1, r)
            if t0 > t1:
                return None
    return (x0 + t0 * dx, y0 + t0 * dy), (x0 + t1 * dx, y0 + t1 * dy)


class Plano:
    """Sistema de coordenadas propio: centro en pantalla y unidades por cuadro."""

    def __init__(self, centro=ORIGIN, u=1.0, B=3.2):
        self.c, self.u, self.B = np.array(centro, dtype=float), u, B

    def p(self, x, y=None):
        if y is None:
            x, y = x
        return self.c + self.u * np.array([x, y, 0.0])

    def marco(self):
        m = Square(side_length=2 * self.B * self.u).move_to(self.c)
        return m.set_stroke(GRIS, 1.5, 0.35)

    def rejilla(self, M=np.eye(2), base=np.eye(2), R=8, colores=(AZUL, CELESTE), opacidad=0.55, ancho=2):
        g = VGroup()
        T = M @ base
        for k in range(-R, R + 1):
            for d, col in ((0, colores[0]), (1, colores[1])):
                a = np.zeros(2); b = np.zeros(2)
                a[d], b[d] = k, k
                a[1 - d], b[1 - d] = -R, R
                seg = recortar(T @ a, T @ b, self.B)
                if seg is None:
                    continue
                eje = k == 0
                l = Line(self.p(seg[0]), self.p(seg[1]), stroke_width=ancho * (1.8 if eje else 1),
                         color=TINTA if eje else col)
                l.set_stroke(opacity=0.9 if eje else opacidad)
                g.add(l)
        return g

    def flecha(self, v, color=CELESTE, ancho=6):
        return Arrow(self.p(0, 0), self.p(v), buff=0, stroke_width=ancho, color=color,
                     max_tip_length_to_length_ratio=0.18, max_stroke_width_to_length_ratio=12)

    def recta(self, d, color=AMBAR, ancho=3):
        d = np.array(d, dtype=float)
        seg = recortar(-20 * d, 20 * d, self.B)
        return DashedLine(self.p(seg[0]), self.p(seg[1]), color=color, stroke_width=ancho, dash_length=0.12)


def interp(A, s):
    return (1 - s) * np.eye(2) + s * np.array(A, dtype=float)


def pmat(filas, color=TINTA, font_size=40):
    cuerpo = r"\\".join("&".join(str(x) for x in f) for f in filas)
    return tex(r"\begin{pmatrix}" + cuerpo + r"\end{pmatrix}", font_size=font_size, color=color)


# ---------------------------------------------------------------------------
class AL01_VectoresPropios(ClipNoche):
    indice = 1
    seccion = "Endomorfismos"
    titulo = "Vectores propios"
    subtitulo = "las direcciones que no giran"
    colores_titulo = [TURQUESA, CELESTE, AZUL, VIOLETA]

    def cuerpo(self):
        eq = tex(r"T(v)=\lambda\,v", font_size=56)
        degradado(eq, DEG_FRIO)
        eq.move_to(UP * 4.3)
        self.play(Write(eq), run_time=1.0)

        P = Plano(UP * 0.4, u=1.05, B=3.3)
        A = np.array([[2.0, 1.0], [1.0, 2.0]])
        s = ValueTracker(0)
        grid = always_redraw(lambda: P.rejilla(interp(A, s.get_value())))
        angs = np.linspace(0, PI, 9, endpoint=False) + 0.07
        cols = color_gradient([TURQUESA, CELESTE, AZUL, VIOLETA, MAGENTA, CORAL], len(angs))
        vecs0 = [np.array([np.cos(a), np.sin(a)]) * 1.15 for a in angs]
        vecs0[2] = np.array([1, 1]) / np.sqrt(2) * 1.15   # propio, λ = 3
        vecs0[6] = np.array([-1, 1]) / np.sqrt(2) * 1.15  # propio, λ = 1

        def flechas():
            M = interp(A, s.get_value())
            g = VGroup()
            for k, v in enumerate(vecs0):
                w = M @ v
                propio = k in (2, 6)
                f = P.flecha(w, color=AMBAR if propio else cols[k], ancho=7 if propio else 4)
                if not propio:
                    f.set_opacity(0.75)
                g.add(f)
            return g

        fl = always_redraw(flechas)
        A_tex = tex(r"A=", r"\begin{pmatrix}2&1\\1&2\end{pmatrix}", font_size=40, color=TINTA)
        A_tex.move_to(DOWN * 3.65 + LEFT * 2.3)
        self.play(FadeIn(P.marco()), Create(grid), run_time=1.0)
        self.play(LaggedStart(*[GrowArrow(f) for f in flechas()], lag_ratio=0.08), run_time=1.0)
        self.add(fl)
        self.play(FadeIn(A_tex), run_time=0.5)
        self.play(s.animate.set_value(1), run_time=3.0, rate_func=smooth)
        l1 = P.recta((1, 1)); l2 = P.recta((-1, 1))
        e1 = tex(r"\lambda=3", font_size=36, color=AMBAR).move_to(P.p(2.2, 2.75))
        e2 = tex(r"\lambda=1", font_size=36, color=AMBAR).move_to(P.p(-2.2, 2.75))
        self.play(Create(l1), Create(l2), FadeIn(e1, e2), run_time=1.0)
        self.play(s.animate.set_value(0), run_time=1.8, rate_func=smooth)
        self.play(s.animate.set_value(1), run_time=1.8, rate_func=smooth)
        cp = tex(r"\det(A-\lambda I)=(2-\lambda)^2-1=0", font_size=38)
        degradado(cp, [CELESTE, VIOLETA])
        cp.move_to(DOWN * 4.75)
        r = tex(r"\Rightarrow\ \lambda\in\{1,3\}", font_size=40, color=AMBAR).move_to(DOWN * 3.65 + RIGHT * 2.0)
        self.play(Write(cp), run_time=1.2)
        self.play(FadeIn(r, shift=LEFT * 0.2), run_time=0.6)
        self.wait(1.2)
        for m in (grid, fl):
            m.clear_updaters()

        final = tex(r"C_T(\lambda)=\det(A-\lambda I)=0", font_size=52)
        degradado(final, DEG_FRIO)
        self.cierre(final, "solo se estiran: sus raíces son los valores propios")


class AL02_Diagonalizar(ClipNoche):
    indice = 2
    seccion = "Endomorfismos"
    titulo = "Diagonalizar"
    subtitulo = "mirar T desde la base adecuada"
    colores_titulo = [CELESTE, AZUL, VIOLETA, MAGENTA]

    def cuerpo(self):
        dec = tex(r"E=\ker(T-\lambda_1)\oplus\cdots\oplus\ker(T-\lambda_r)", font_size=40)
        degradado(dec, DEG_AZUL)
        dec.move_to(UP * 4.3)
        self.play(Write(dec), run_time=1.3)

        P = Plano(UP * 0.5, u=0.95, B=3.4)
        v1, v2 = np.array([1.0, 0.45]), np.array([-0.35, 1.0])
        Pm = np.column_stack([v1, v2])
        A = Pm @ np.diag([2.0, 0.6]) @ np.linalg.inv(Pm)
        s = ValueTracker(0)
        canon = P.rejilla(colores=(GRIS, GRIS), opacidad=0.18, ancho=1)
        eig = always_redraw(lambda: P.rejilla(interp(A, s.get_value()), base=Pm, colores=(CORAL, TURQUESA), opacidad=0.6))
        f1 = always_redraw(lambda: P.flecha(interp(A, s.get_value()) @ v1, CORAL, 7))
        f2 = always_redraw(lambda: P.flecha(interp(A, s.get_value()) @ v2, TURQUESA, 7))
        self.play(FadeIn(P.marco()), FadeIn(canon), run_time=0.6)
        self.play(Create(eig), GrowArrow(f1), GrowArrow(f2), run_time=1.2)
        l1 = tex(r"\times 2", font_size=36, color=CORAL).move_to(P.p(2.6, 0.55))
        l2 = tex(r"\times 0.6", font_size=36, color=TURQUESA).move_to(P.p(-1.25, 2.4))
        self.play(s.animate.set_value(1), FadeIn(l1, l2), run_time=2.6, rate_func=smooth)
        frase = self.rotulo("en la base de vectores propios, T solo estira cada eje", pos=DOWN * 3.0, size=24, color=GRIS)
        D = tex(r"A=P\,", r"\begin{pmatrix}2&0\\0&0.6\end{pmatrix}", r"\,P^{-1}", font_size=44)
        D[1].set_color_by_gradient(CORAL, TURQUESA)
        D.move_to(DOWN * 4.2)
        self.play(FadeIn(frase), Write(D), run_time=1.2)
        self.play(s.animate.set_value(0), run_time=1.2)
        self.play(s.animate.set_value(1), run_time=1.2)
        for m in (eig, f1, f2):
            m.clear_updaters()
        self.limpiar(dec)

        # --- contraejemplo: la cizalla ---------------------------------------
        crit = tex(r"n_i=\dim\ker(T-\lambda_iI)", font_size=44)
        degradado(crit, [AMBAR, CORAL])
        crit.move_to(DOWN * 4.3)
        P2 = Plano(UP * 0.5, u=0.95, B=3.4)
        Sh = np.array([[1.0, 1.0], [0.0, 1.0]])
        s2 = ValueTracker(0)
        g2 = always_redraw(lambda: P2.rejilla(interp(Sh, s2.get_value())))
        lab = tex(r"\begin{pmatrix}1&1\\0&1\end{pmatrix}", font_size=40, color=TINTA).move_to(P2.p(-2.3, 2.6))
        self.play(FadeIn(P2.marco()), Create(g2), FadeIn(lab), run_time=0.8)
        eje = P2.recta((1, 0), color=AMBAR, ancho=5)
        self.play(s2.animate.set_value(1), run_time=2.0, rate_func=smooth)
        self.play(Create(eje), run_time=0.6)
        no = tex(r"\lambda=1\ \text{doble},\ \ \dim\ker=1", font_size=36, color=CORAL).move_to(DOWN * 3.1)
        self.play(FadeIn(no), Write(crit), run_time=1.1)
        self.play(Indicate(crit, color=TINTA), run_time=0.9)
        g2.clear_updaters()
        self.wait(0.6)

        final = tex(r"A=P\,D\,P^{-1}", font_size=64)
        degradado(final, DEG_ARCOIRIS)
        self.cierre(final, "diagonalizable ⟺ multiplicidad algebraica = geométrica")


class AL03_Recurrencias(ClipNoche):
    indice = 3
    seccion = "Diagonalización aplicada"
    titulo = "Recurrencias lineales"
    subtitulo = "potencias de una matriz"
    colores_titulo = [AMBAR, CORAL, MAGENTA, VIOLETA]

    def cuerpo(self):
        sis = tex(r"u_n=3u_{n-1}+3v_{n-1},\quad v_n=5u_{n-1}+v_{n-1}", font_size=36, color=TINTA)
        sis.move_to(UP * 4.35)
        mat = tex(r"X_n=", r"\begin{pmatrix}3&3\\5&1\end{pmatrix}", r"X_{n-1}", font_size=44)
        mat[1].set_color_by_gradient(AMBAR, CORAL)
        mat.move_to(UP * 3.2)
        self.play(Write(sis), run_time=1.1)
        self.play(FadeIn(mat, shift=UP * 0.2), run_time=0.7)

        P = Plano(DOWN * 0.6, u=1.7, B=1.45)
        circ = Circle(radius=1.3 * P.u).move_to(P.c).set_stroke(GRIS, 1.5, 0.4)
        ejes = VGroup(Line(P.p(-1.45, 0), P.p(1.45, 0)), Line(P.p(0, -1.45), P.p(0, 1.45))).set_stroke(GRIS, 1.5, 0.5)
        d6 = P.recta((1, 1), color=AMBAR, ancho=3)
        d2 = P.recta((-3, 5), color=VIOLETA, ancho=3)
        e6 = tex(r"\lambda=6", font_size=32, color=AMBAR).move_to(P.p(1.25, 1.55))
        e2 = tex(r"\lambda=-2", font_size=32, color=VIOLETA).move_to(P.p(-1.3, 1.55))
        self.play(Create(circ), Create(ejes), run_time=0.6)
        self.play(Create(d6), Create(d2), FadeIn(e6, e2), run_time=0.8)

        A = np.array([[3, 3], [5, 1]])
        X = np.array([0, 1])
        cols = color_gradient([TURQUESA, CELESTE, AZUL, VIOLETA, MAGENTA, CORAL, AMBAR], 8)
        prev = None
        lect = None
        for n in range(8):
            d = X / np.linalg.norm(X) * 1.3
            f = P.flecha(d, color=cols[n], ancho=6)
            l = tex(r"n=%d:\ (u_n,v_n)=(%d,\,%d)" % (n, X[0], X[1]), font_size=34, color=cols[n]).move_to(DOWN * 3.15)
            anims = [GrowArrow(f)] if prev is None else [ReplacementTransform(prev, f)]
            if prev is not None:
                fantasma = prev.copy().set_opacity(0.18)
                self.add(fantasma)
            anims.append(FadeIn(l) if lect is None else ReplacementTransform(lect, l))
            self.play(*anims, run_time=0.55)
            prev, lect = f, l
            X = A @ X
        cierre_n = tex(r"u_n=\tfrac38\big(6^n-(-2)^n\big)", font_size=44)
        degradado(cierre_n, [AMBAR, CORAL, VIOLETA])
        cierre_n.move_to(DOWN * 4.35)
        self.play(Write(cierre_n), run_time=1.1)
        dom = self.rotulo("el valor propio dominante impone la dirección", pos=DOWN * 5.35, size=24, color=GRIS)
        self.play(FadeIn(dom), Indicate(d6, color=AMBAR), run_time=0.9)
        self.wait(0.8)

        final = tex(r"X_n=P\,D^n\,P^{-1}X_0", font_size=60)
        degradado(final, DEG_CALIDO + [VIOLETA])
        self.cierre(final, "una potencia n-ésima = n potencias de números")


class AL04_Markov(ClipNoche):
    indice = 4
    seccion = "Diagonalización aplicada"
    titulo = "Cadenas de Markov"
    subtitulo = "el sistema olvida de dónde vino"
    colores_titulo = [AMBAR, CELESTE, AZUL]

    def cuerpo(self):
        Pm = tex(r"\begin{pmatrix}S_n\\L_n\end{pmatrix}=", r"\begin{pmatrix}0.8&0.4\\0.2&0.6\end{pmatrix}",
                 r"\begin{pmatrix}S_{n-1}\\L_{n-1}\end{pmatrix}", font_size=40)
        Pm[1].set_color_by_gradient(AMBAR, CELESTE)
        Pm.move_to(UP * 4.0)
        self.play(Write(Pm), run_time=1.3)
        leyenda = VGroup(texto("S: sol", size=22, color=AMBAR), texto("L: lluvia", size=22, color=CELESTE)).arrange(RIGHT, buff=0.6)
        leyenda.move_to(UP * 2.75)
        self.play(FadeIn(leyenda), run_time=0.5)

        ejes = Axes(x_range=[0, 10, 1], y_range=[0, 1.05, 0.5], x_length=7.4, y_length=3.6,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(UP * 0.3)
        eq = DashedLine(ejes.c2p(0, 2 / 3), ejes.c2p(10, 2 / 3), color=TINTA, stroke_width=2).set_opacity(0.6)
        leq = tex(r"S_\infty=\tfrac23", font_size=30, color=TINTA).next_to(ejes.c2p(10, 2 / 3), UP, buff=0.12).shift(LEFT * 0.5)
        ln = tex(r"n", font_size=30, color=GRIS).next_to(ejes.c2p(10, 0), UP, buff=0.1)
        self.play(Create(ejes), Create(eq), FadeIn(leq, ln), run_time=0.8)
        M = np.array([[0.8, 0.4], [0.2, 0.6]])
        inicios = [(np.array([0.0, 1.0]), CELESTE), (np.array([1.0, 0.0]), AMBAR), (np.array([0.3, 0.7]), VIOLETA)]
        series = []
        for X0, c in inicios:
            pts, X = [], X0.copy()
            for n in range(11):
                pts.append(ejes.c2p(n, X[0]))
                X = M @ X
            series.append((pts, c))
        # barras de la primera cadena (empieza lloviendo)
        bx = ejes.c2p(0, 0)[0]
        base_y = DOWN * 3.3
        barS = Rectangle(width=1.2, height=0.01).set_stroke(width=0).set_fill([AMBAR, CORAL], 1)
        barL = Rectangle(width=1.2, height=0.01).set_stroke(width=0).set_fill([CELESTE, AZUL], 1)
        k = ValueTracker(0)

        def barras():
            X = np.linalg.matrix_power(M, int(k.get_value())) @ np.array([0.0, 1.0])
            g = VGroup()
            for j, (b, c) in enumerate(((barS, AMBAR), (barL, CELESTE))):
                r = b.copy().stretch_to_fit_height(max(X[j] * 2.2, 0.01)).move_to(base_y + RIGHT * (1.6 * j - 0.8), aligned_edge=DOWN)
                t = tex("%.3f" % X[j], font_size=28, color=c).next_to(r, UP, buff=0.1)
                g.add(r, t)
            g.add(tex(r"n=%d" % int(k.get_value()), font_size=30, color=GRIS).move_to(base_y + RIGHT * 2.8 + UP * 0.6))
            return g

        br = always_redraw(barras)
        self.add(br)
        lineas = VGroup()
        for pts, c in series:
            l = VMobject(stroke_width=4, stroke_color=c).set_points_as_corners(pts)
            ds = VGroup(*[Dot(p, radius=0.06, color=c) for p in pts])
            lineas.add(VGroup(l, ds))
        self.play(Create(lineas[0][0]), LaggedStart(*[FadeIn(d, scale=2) for d in lineas[0][1]], lag_ratio=0.3),
                  k.animate.set_value(10), run_time=4.0, rate_func=linear)
        self.play(*[Create(g[0]) for g in lineas[1:]], *[FadeIn(g[1]) for g in lineas[1:]], run_time=1.6)
        br.clear_updaters()
        esp = tex(r"\lambda_1=1,\qquad \lambda_2=0.4\ \Rightarrow\ 0.4^n\to0", font_size=38)
        degradado(esp, [AMBAR, CELESTE, VIOLETA])
        esp.move_to(DOWN * 4.75)
        self.play(Write(esp), run_time=1.1)
        self.wait(1.2)

        final = tex(r"P^\infty=\begin{pmatrix}2/3&2/3\\1/3&1/3\end{pmatrix}", font_size=52)
        degradado(final, [AMBAR, CORAL, CELESTE])
        self.cierre(final, "λ = 1 manda; el resto se apaga: 2/3 de días de sol")


class AL05_Espectral(ClipNoche):
    indice = 5
    seccion = "Teorema espectral"
    titulo = "Matrices simétricas"
    subtitulo = "diagonalización garantizada"
    colores_titulo = [TURQUESA, CELESTE, VIOLETA, MAGENTA]

    def cuerpo(self):
        h = tex(r"A=A^t", font_size=56)
        degradado(h, DEG_FRIO)
        h.move_to(UP * 4.35)
        self.play(Write(h), run_time=0.8)
        P = Plano(UP * 0.6, u=1.0, B=3.3)
        A = np.array([[2.2, 0.9], [0.9, 1.1]])
        lam, V = np.linalg.eigh(A)
        s = ValueTracker(0)
        angs = np.linspace(0, TAU, 24, endpoint=False)
        cols = color_gradient([TURQUESA, CELESTE, AZUL, VIOLETA, MAGENTA, CORAL, AMBAR, TURQUESA], len(angs))

        def figura():
            M = interp(A, s.get_value())
            curva = VMobject().set_points_smoothly([P.p(M @ [np.cos(a), np.sin(a)]) for a in np.linspace(0, TAU, 90)])
            curva.set_stroke(width=4).set_color([CELESTE, VIOLETA, MAGENTA, CELESTE])
            radios = VGroup(*[Line(P.p(0, 0), P.p(M @ [np.cos(a), np.sin(a)]), stroke_width=2.5, color=c).set_opacity(0.7)
                              for a, c in zip(angs, cols)])
            puntas = VGroup(*[Dot(P.p(M @ [np.cos(a), np.sin(a)]), radius=0.045, color=c) for a, c in zip(angs, cols)])
            return VGroup(radios, curva, puntas)

        fig = always_redraw(figura)
        self.play(FadeIn(P.rejilla(colores=(GRIS, GRIS), opacidad=0.15, ancho=1)), FadeIn(P.marco()), run_time=0.5)
        self.play(Create(fig), run_time=1.2)
        self.play(s.animate.set_value(1), run_time=2.6, rate_func=smooth)
        fig.clear_updaters()
        ejes = VGroup()
        for k, c in ((1, AMBAR), (0, TURQUESA)):
            ejes.add(P.flecha(V[:, k] * lam[k], color=c, ancho=7))
        ang = RightAngle(Line(P.p(0, 0), P.p(V[:, 1])), Line(P.p(0, 0), P.p(V[:, 0])), length=0.3, color=TINTA)
        lbl = VGroup(
            tex(r"\lambda_1=%.2f" % lam[1], font_size=32, color=AMBAR).move_to(P.p(V[:, 1] * (lam[1] + 0.55))),
            tex(r"\lambda_2=%.2f" % lam[0], font_size=32, color=TURQUESA).move_to(P.p(V[:, 0] * (lam[0] + 0.75))),
        )
        self.play(LaggedStart(*[GrowArrow(e) for e in ejes], lag_ratio=0.3), FadeIn(lbl), run_time=1.1)
        self.play(Create(ang), run_time=0.5)
        props = VGroup(
            tex(r"\lambda_i\in\mathbb R", font_size=40, color=AMBAR),
            tex(r"V_{\lambda_i}\perp V_{\lambda_j}", font_size=40, color=TURQUESA),
            tex(r"P^{-1}=P^t", font_size=40, color=VIOLETA),
        ).arrange(RIGHT, buff=0.55).move_to(DOWN * 3.4)
        ajustar(props)
        self.play(LaggedStart(*[FadeIn(p, shift=UP * 0.25) for p in props], lag_ratio=0.35), run_time=1.6)
        cc = self.rotulo("el círculo unidad se vuelve una elipse: sus ejes son los vectores propios",
                         pos=DOWN * 4.6, size=22, color=GRIS)
        self.play(FadeIn(cc), run_time=0.6)
        self.wait(1.4)

        final = tex(r"A=P\,D\,P^{\,t}", font_size=64)
        degradado(final, DEG_FRIO + [MAGENTA])
        self.cierre(final, "real y simétrica ⇒ base ortonormal de vectores propios")


class AL06_Exponencial(ClipNoche):
    indice = 6
    seccion = "Sistemas diferenciales"
    titulo = "La exponencial de una matriz"
    subtitulo = "X' = AX como un flujo"
    colores_titulo = [TURQUESA, CELESTE, VIOLETA, MAGENTA, CORAL]

    def cuerpo(self):
        serie = tex(r"e^{tA}=\sum_{k\ge0}\frac{t^k}{k!}A^k", font_size=48)
        degradado(serie, DEG_FRIO)
        serie.move_to(UP * 4.2)
        self.play(Write(serie), run_time=1.1)
        sol = tex(r"X(t)=e^{tA}C=\sum_i c_i\,e^{\lambda_i t}\,v_i", font_size=40, color=TINTA)
        sol.move_to(UP * 2.65)
        self.play(FadeIn(sol, shift=UP * 0.2), run_time=0.7)

        P = Plano(DOWN * 1.1, u=0.92, B=3.2)
        A1 = np.array([[0.0, 1.0], [1.0, 0.0]])
        A2 = np.array([[-0.25, -1.0], [1.0, -0.25]])
        mez = ValueTracker(0)
        rng = np.random.default_rng(7)

        def A():
            m = mez.get_value()
            return (1 - m) * A1 + m * A2

        def nuevo():
            return rng.uniform(-3.0, 3.0, 2)

        estado = [nuevo() for _ in range(70)]
        edades = list(rng.uniform(0, 3, 70))
        cols = color_gradient([TURQUESA, CELESTE, AZUL, VIOLETA, MAGENTA], 70)
        flujo = VGroup(*[Line(ORIGIN, RIGHT * 0.01) for _ in range(70)])

        def avanzar(g, dt):
            M = A()
            E = np.eye(2) + dt * M + (dt * M) @ (dt * M) / 2
            for i, l in enumerate(g):
                x = E @ estado[i]
                edades[i] += dt
                if np.max(np.abs(x)) > 3.15 or np.linalg.norm(x) < 0.06 or edades[i] > 5:
                    x, edades[i] = nuevo(), 0.0
                estado[i] = x
                v = M @ x
                cola = x - 0.22 * v / max(np.linalg.norm(v), 0.4)
                l.put_start_and_end_on(P.p(cola), P.p(x))
                l.set_stroke(cols[i], width=4, opacity=min(1.0, edades[i] * 2) * 0.9)

        avanzar(flujo, 0)
        self.play(FadeIn(P.marco()), FadeIn(P.rejilla(colores=(GRIS, GRIS), opacidad=0.12, ancho=1)), run_time=0.5)
        flujo.add_updater(avanzar)
        self.add(flujo)
        dirs = VGroup(P.recta((1, 1), AMBAR, 3), P.recta((1, -1), CORAL, 3))
        tsilla = tex(r"\lambda=\pm1:\ \text{silla}", font_size=36, color=AMBAR).move_to(DOWN * 4.75)
        self.play(Create(dirs), FadeIn(tsilla), run_time=0.8)
        self.wait(3.2)
        tesp = tex(r"\lambda=-\tfrac14\pm i:\ \text{espiral}", font_size=36, color=VIOLETA).move_to(DOWN * 4.75)
        self.play(FadeOut(dirs), mez.animate.set_value(1), ReplacementTransform(tsilla, tesp), run_time=2.5)
        self.wait(3.5)
        der = tex(r"\tfrac{d}{dt}e^{tA}=A\,e^{tA}", font_size=38, color=CIELO).move_to(DOWN * 5.6)
        self.play(FadeIn(der), run_time=0.6)
        self.wait(1.0)
        flujo.clear_updaters()

        final = tex(r"e^{tA}=P\,e^{tD}P^{-1}", font_size=60)
        degradado(final, DEG_ARCOIRIS)
        self.cierre(final, "la solución es una superposición de modos normales")


class AL07_Dunford(ClipNoche):
    indice = 7
    seccion = "Triangulación"
    titulo = "Dunford–Jordan"
    subtitulo = "diagonal + nilpotente"
    colores_titulo = [AMBAR, CORAL, MAGENTA, VIOLETA]

    def cuerpo(self):
        tdn = tex(r"T=D+N,\qquad D\circ N=N\circ D", font_size=44)
        degradado(tdn, DEG_CALIDO + [VIOLETA])
        tdn.move_to(UP * 4.3)
        self.play(Write(tdn), run_time=1.1)

        def M(filas, colores):
            m = Matrix(filas, element_to_mobject=lambda x: MathTex(x, tex_template=PLANTILLA, font_size=44 * ESCALA),
                       h_buff=0.85, v_buff=0.75, bracket_h_buff=0.18)
            for e, c in zip(m.get_entries(), colores):
                e.set_color(c)
            m.get_brackets().set_color(GRIS)
            return m

        Z, U = GRIS, TINTA
        A = M([["2", "1", "0"], ["0", "2", "1"], ["0", "0", "2"]], [AMBAR, CORAL, Z, Z, AMBAR, CORAL, Z, Z, AMBAR])
        D = M([["2", "0", "0"], ["0", "2", "0"], ["0", "0", "2"]], [AMBAR, Z, Z, Z, AMBAR, Z, Z, Z, AMBAR])
        N = M([["0", "1", "0"], ["0", "0", "1"], ["0", "0", "0"]], [Z, CORAL, Z, Z, Z, CORAL, Z, Z, Z])
        fila = VGroup(A, tex("=", font_size=48), D, tex("+", font_size=48), N).arrange(RIGHT, buff=0.22)
        ajustar(fila, 8.4).move_to(UP * 2.2)
        self.play(FadeIn(A, shift=UP * 0.2), run_time=0.7)
        self.play(FadeIn(fila[1]), TransformFromCopy(A, D), FadeIn(fila[3]), TransformFromCopy(A, N), run_time=1.4)
        ld = texto("diagonalizable", size=22, color=AMBAR).next_to(D, DOWN, buff=0.2)
        ln = texto("nilpotente", size=22, color=CORAL).next_to(N, DOWN, buff=0.2)
        self.play(FadeIn(ld, ln), run_time=0.5)

        # potencias de N: los unos suben hacia la esquina y desaparecen
        N2 = M([["0", "0", "1"], ["0", "0", "0"], ["0", "0", "0"]], [Z, Z, MAGENTA, Z, Z, Z, Z, Z, Z])
        N3 = M([["0", "0", "0"], ["0", "0", "0"], ["0", "0", "0"]], [Z] * 9)
        pot = VGroup(tex(r"N^2=", font_size=40, color=MAGENTA), N2, tex(r"N^3=", font_size=40, color=VIOLETA), N3)
        pot.arrange(RIGHT, buff=0.2)
        ajustar(pot, 8.0).move_to(DOWN * 0.8)
        self.play(FadeIn(pot[0]), TransformFromCopy(N, N2), run_time=1.1)
        self.play(FadeIn(pot[2]), TransformFromCopy(N2, N3), run_time=1.1)
        cero = SurroundingRectangle(N3, color=VIOLETA, corner_radius=0.1, buff=0.08)
        self.play(Create(cero), run_time=0.5)
        bin_ = tex(r"A^n=2^nI+n\,2^{n-1}N+\tbinom n2 2^{n-2}N^2", font_size=40)
        degradado(bin_, [AMBAR, CORAL, MAGENTA])
        bin_.move_to(DOWN * 3.0)
        self.play(Write(bin_), run_time=1.4)
        exp_ = tex(r"e^{tA}=e^{2t}\Big(I+tN+\tfrac{t^2}{2}N^2\Big)", font_size=40)
        degradado(exp_, [CORAL, MAGENTA, VIOLETA])
        exp_.move_to(DOWN * 4.4)
        self.play(Write(exp_), run_time=1.3)
        corta = self.rotulo("como D y N conmutan, el binomio de Newton vale y la serie se corta", pos=DOWN * 5.45, size=22, color=GRIS)
        self.play(FadeIn(corta), run_time=0.6)
        self.wait(1.4)

        final = tex(r"e^{tA}=e^{tD}\sum_{k<h}\frac{t^k}{k!}N^k", font_size=56)
        degradado(final, DEG_CALIDO + [VIOLETA])
        self.cierre(final, "N^h = 0: una serie infinita se vuelve un polinomio")


class AL08_Sylvester(ClipNoche):
    indice = 8
    seccion = "Métricas y formas cuadráticas"
    titulo = "Ley de inercia de Sylvester"
    subtitulo = "la signatura no depende de la base"
    colores_titulo = [CELESTE, VIOLETA, MAGENTA, CORAL]

    def cuerpo(self):
        q = tex(r"q(x)=x^t G\,x", r"\qquad", r"q=x^2+b\,y^2", font_size=44)
        q[0].set_color_by_gradient(CELESTE, VIOLETA); q[2].set_color(TINTA)
        q.move_to(UP * 4.3)
        self.play(Write(q), run_time=1.1)

        P = Plano(UP * 0.5, u=1.0, B=3.2)
        b = ValueTracker(1.0)
        niveles = [0.5, 1.4, 2.8, 4.8]
        cols_p = color_gradient([TURQUESA, CELESTE, AZUL, VIOLETA], 4)
        cols_n = color_gradient([AMBAR, CORAL, MAGENTA, VIOLETA], 4)

        def curva(pts, c):
            pts = [p for p in pts if max(abs(p[0]), abs(p[1])) <= P.B]
            if len(pts) < 2:
                return VMobject()
            m = VMobject(stroke_width=4, stroke_color=c)
            m.set_points_smoothly([P.p(p) for p in pts])
            return m

        def contornos():
            bb = b.get_value()
            g = VGroup()
            for c, cp, cn in zip(niveles, cols_p, cols_n):
                if bb > 0.03:
                    th = np.linspace(0, TAU, 120)
                    pts = np.c_[np.sqrt(c) * np.cos(th), np.sqrt(c / bb) * np.sin(th)]
                    # trozos dentro del marco
                    dentro = (np.abs(pts[:, 1]) <= P.B)
                    if dentro.all():
                        m = VMobject(stroke_width=4, stroke_color=cp).set_points_smoothly([P.p(p) for p in pts])
                        g.add(m)
                    else:
                        for sgn in (1, -1):
                            u = np.linspace(-np.arcsin(min(1, P.B / np.sqrt(c / bb))), np.arcsin(min(1, P.B / np.sqrt(c / bb))), 60)
                            g.add(curva(np.c_[sgn * np.sqrt(c) * np.cos(u), np.sqrt(c / bb) * np.sin(u)], cp))
                elif bb > -0.03:
                    for sgn in (1, -1):
                        g.add(Line(P.p(sgn * np.sqrt(c), -P.B), P.p(sgn * np.sqrt(c), P.B), stroke_width=4, color=cp))
                else:
                    k = np.sqrt(c / -bb)
                    for sgn in (1, -1):
                        umax = np.arccosh(max(P.B / np.sqrt(c), 1.0001))
                        u = np.linspace(-umax, umax, 60)
                        g.add(curva(np.c_[sgn * np.sqrt(c) * np.cosh(u), k * np.sinh(u)], cp))
                        umax2 = np.arccosh(max(P.B / k, 1.0001))
                        u2 = np.linspace(-umax2, umax2, 60)
                        g.add(curva(np.c_[np.sqrt(c) * np.sinh(u2), sgn * k * np.cosh(u2)], cn))
            return g

        def etiqueta():
            bb = b.get_value()
            if bb > 0.03:
                s, c, sig = "definida positiva", TURQUESA, r"(r_+,r_-,r_0)=(2,0,0)"
            elif bb > -0.03:
                s, c, sig = "degenerada: radical no nulo", AMBAR, r"(r_+,r_-,r_0)=(1,0,1)"
            else:
                s, c, sig = "indefinida", CORAL, r"(r_+,r_-,r_0)=(1,1,0)"
            return VGroup(texto(s, size=28, color=c, slant=ITALIC).move_to(DOWN * 3.3),
                          tex(sig, font_size=38, color=c).move_to(DOWN * 4.25),
                          tex(r"b=%.2f" % bb, font_size=32, color=GRIS).move_to(P.p(2.3, 2.85)))

        cont, et = always_redraw(contornos), always_redraw(etiqueta)
        self.play(FadeIn(P.marco()), FadeIn(P.rejilla(colores=(GRIS, GRIS), opacidad=0.12, ancho=1)), run_time=0.5)
        self.play(Create(cont), FadeIn(et), run_time=1.2)
        self.play(b.animate.set_value(0.25), run_time=2.0)
        self.play(b.animate.set_value(0.0), run_time=1.3)
        self.wait(0.6)
        self.play(b.animate.set_value(-0.6), run_time=2.2)
        self.wait(0.8)
        for m in (cont, et):
            m.clear_updaters()
        des = tex(r"E=V_+\perp V_-\perp V_0", font_size=46)
        degradado(des, [TURQUESA, CORAL, AMBAR])
        des.move_to(DOWN * 5.3)
        self.play(Write(des), run_time=1.1)
        self.wait(1.2)

        final = tex(r"\dim V_+,\ \dim V_-,\ \dim V_0\ \ \text{invariantes}", font_size=46)
        degradado(final, [TURQUESA, CELESTE, CORAL, AMBAR])
        self.cierre(final, "cambiar de base no cambia cuántas direcciones suman, restan o se anulan")


class AL09_Schwarz(ClipNoche):
    indice = 9
    seccion = "Espacio euclídeo"
    titulo = "Desigualdad de Schwarz"
    subtitulo = "por qué existe el ángulo"
    colores_titulo = [TURQUESA, CELESTE, AZUL, AMBAR]

    def cuerpo(self):
        f = tex(r"f(t)=\|e_1-t\,e_2\|^2\ \ge 0", font_size=46)
        degradado(f, DEG_FRIO)
        f.move_to(UP * 4.3)
        self.play(Write(f), run_time=1.1)

        P = Plano(UP * 1.65, u=0.95, B=2.0)
        P.c = P.c + LEFT * 0.4
        e1, e2 = np.array([1.0, 1.9]), np.array([1.7, 0.3])
        t = ValueTracker(-0.3)
        ejes = Axes(x_range=[-0.5, 2.3, 0.5], y_range=[0, 8, 2], x_length=7.0, y_length=3.0,
                    axis_config={"stroke_color": GRIS, "include_ticks": False}).move_to(DOWN * 2.15)
        a, bq, c = e2 @ e2, -2 * (e1 @ e2), e1 @ e1
        fun = lambda x: a * x * x + bq * x + c
        par = ejes.plot(fun, x_range=[-0.5, 2.3, 0.01], stroke_width=5).set_color([CORAL, AMBAR, TURQUESA, CELESTE])
        lt = tex("t", font_size=30, color=GRIS).next_to(ejes.c2p(2.3, 0), UP, buff=0.1)

        def vectores():
            tv = t.get_value()
            g = VGroup(
                P.flecha(e1, CELESTE, 6), P.flecha(tv * e2 if abs(tv) > 0.02 else e2 * 0.02, AMBAR, 6),
                Line(P.p(tv * e2), P.p(e1), stroke_width=5, color=MAGENTA),
                Dot(ejes.c2p(tv, fun(tv)), radius=0.1, color=MAGENTA),
                DashedLine(ejes.c2p(tv, 0), ejes.c2p(tv, fun(tv)), color=MAGENTA, stroke_width=2),
            )
            return g

        lab = VGroup(tex(r"e_1", font_size=32, color=CELESTE).move_to(P.p(e1 * 1.13)),
                     tex(r"t\,e_2", font_size=32, color=AMBAR).move_to(P.p(e2 * 1.2 + np.array([0.3, -0.35]))))
        vec = always_redraw(vectores)
        self.play(FadeIn(P.rejilla(colores=(GRIS, GRIS), opacidad=0.12, ancho=1)), Create(ejes), Create(par), FadeIn(lt), run_time=1.0)
        self.play(FadeIn(vec), FadeIn(lab), run_time=0.6)
        ts = (e1 @ e2) / a
        self.play(t.animate.set_value(2.1), run_time=2.6, rate_func=smooth)
        self.play(t.animate.set_value(ts), run_time=1.6, rate_func=smooth)
        vec.clear_updaters()
        ra = RightAngle(Line(P.p(ts * e2), P.p(e1)), Line(P.p(ts * e2), P.p(0, 0)), length=0.22, color=TINTA)
        self.play(Create(ra), Flash(ejes.c2p(ts, fun(ts)), color=MAGENTA), run_time=0.7)
        disc = tex(r"\Delta=4\langle e_1,e_2\rangle^2-4\|e_1\|^2\|e_2\|^2\le0", font_size=36, color=TINTA)
        disc.move_to(DOWN * 4.1)
        self.play(Write(disc), run_time=1.3)
        cos = tex(r"\cos\theta=\frac{\langle e_1,e_2\rangle}{\|e_1\|\,\|e_2\|}\in[-1,1]", font_size=38)
        degradado(cos, [AMBAR, CORAL, MAGENTA])
        cos.move_to(DOWN * 5.3)
        self.play(Write(cos), run_time=1.2)
        self.wait(1.2)

        final = tex(r"|\langle e_1,e_2\rangle|\le\|e_1\|\,\|e_2\|", font_size=58)
        degradado(final, DEG_FRIO + [AMBAR])
        self.cierre(final, "la parábola nunca cruza el eje: discriminante ≤ 0")


class AL10_Isometrias(ClipNoche):
    indice = 10
    seccion = "Espacio euclídeo"
    titulo = "Isometrías"
    subtitulo = "giros y simetrías: det = ±1"
    colores_titulo = [CELESTE, VIOLETA, MAGENTA]

    def cuerpo(self):
        o = tex(r"A^tA=I\ \Rightarrow\ \det A=\pm1", font_size=48)
        degradado(o, DEG_AZUL + [MAGENTA])
        o.move_to(UP * 4.3)
        self.play(Write(o), run_time=1.1)
        P = Plano(UP * 0.7, u=0.95, B=3.2)
        forma = np.array([[0, 0], [0.45, 0], [0.45, 1.0], [1.3, 1.0], [1.3, 1.4], [0.45, 1.4], [0.45, 2.0],
                          [1.6, 2.0], [1.6, 2.45], [0, 2.45]]) + np.array([0.25, 0.2])
        M = [np.eye(2)]

        def figura(Mat):
            pol = Polygon(*[P.p(Mat @ v) for v in forma], stroke_width=4)
            pol.set_stroke([TURQUESA, CELESTE, VIOLETA]).set_fill([AZUL, VIOLETA], opacity=0.45)
            # flecha de orientación (sentido antihorario de los vértices)
            arco = ArcBetweenPoints(P.p(Mat @ [1.4, 0.4]), P.p(Mat @ [0.6, 1.2]), angle=PI / 2)
            det = np.linalg.det(Mat)
            arco.set_stroke(AMBAR if det > 0 else CORAL, 4).add_tip(tip_length=0.2)
            return VGroup(pol, arco)

        th = ValueTracker(0)
        sref = ValueTracker(0)
        phi = 1.2
        S = np.array([[np.cos(2 * phi), np.sin(2 * phi)], [np.sin(2 * phi), -np.cos(2 * phi)]])

        def actual():
            R = np.array([[np.cos(th.get_value()), -np.sin(th.get_value())], [np.sin(th.get_value()), np.cos(th.get_value())]])
            s = sref.get_value()
            return ((1 - s) * np.eye(2) + s * S) @ R

        fig = always_redraw(lambda: figura(actual()))

        def lectura():
            Mt = actual()
            m = tex(r"\begin{pmatrix}%.2f&%.2f\\%.2f&%.2f\end{pmatrix}" % (Mt[0, 0], Mt[0, 1], Mt[1, 0], Mt[1, 1]),
                    font_size=36, color=TINTA).move_to(DOWN * 3.4 + LEFT * 1.9)
            d = np.linalg.det(Mt)
            dd = tex(r"\det=%+.2f" % d, font_size=40, color=AMBAR if d > 0.05 else (CORAL if d < -0.05 else GRIS))
            dd.move_to(DOWN * 3.4 + RIGHT * 2.0)
            return VGroup(m, dd)

        lec = always_redraw(lectura)
        self.play(FadeIn(P.marco()), FadeIn(P.rejilla(colores=(GRIS, GRIS), opacidad=0.14, ancho=1)), run_time=0.5)
        self.play(DrawBorderThenFill(fig), FadeIn(lec), run_time=1.0)
        giro = tex(r"R(\theta)=\begin{pmatrix}\cos\theta&-\sin\theta\\ \sin\theta&\cos\theta\end{pmatrix}", font_size=36, color=AMBAR)
        giro.move_to(DOWN * 4.9)
        self.play(FadeIn(giro), th.animate.set_value(2 * PI / 3), run_time=3.0, rate_func=smooth)
        self.wait(0.4)
        eje = P.recta((np.cos(phi), np.sin(phi)), color=CORAL, ancho=4)
        sim = texto("simetría: invierte la orientación", size=26, color=CORAL, slant=ITALIC).move_to(DOWN * 4.9)
        self.play(Create(eje), FadeOut(giro), FadeIn(sim), run_time=0.8)
        self.play(sref.animate.set_value(1), run_time=3.0, rate_func=smooth)
        self.wait(0.6)
        fig.clear_updaters(); lec.clear_updaters()
        grupos = tex(r"SO(E)=\{\det=+1\}\subset O(E)", font_size=40)
        degradado(grupos, [AMBAR, CORAL, VIOLETA])
        grupos.move_to(DOWN * 5.85)
        self.play(Write(grupos), run_time=1.1)
        self.wait(1.0)

        final = tex(r"\tau^*T_2=T_2\iff \|\tau(e)\|=\|e\|", font_size=52)
        degradado(final, DEG_AZUL + [MAGENTA])
        self.cierre(final, "conservan módulos, distancias y ángulos")


class AL11_Tensores(ClipNoche):
    indice = 11
    seccion = "Álgebra tensorial"
    titulo = "Tensores"
    subtitulo = "multilinealidad en todas las direcciones"
    colores_titulo = [TURQUESA, CELESTE, VIOLETA, MAGENTA, AMBAR]

    def cuerpo(self):
        d = tex(r"T^q_p:\ E\times\overset{p}{\cdots}\times E\times E^*\times\overset{q}{\cdots}\times E^*\to k", font_size=40)
        degradado(d, DEG_FRIO)
        d.move_to(UP * 4.3)
        self.play(Write(d), run_time=1.4)
        ej = VGroup(
            tex(r"\text{m\'etrica}\in T_2", font_size=34, color=CELESTE),
            tex(r"\mathrm{End}\,E=T^1_1", font_size=34, color=VIOLETA),
            tex(r"E^*=T_1", font_size=34, color=AMBAR),
        ).arrange(RIGHT, buff=0.55).move_to(UP * 3.1)
        ajustar(ej)
        self.play(LaggedStart(*[FadeIn(e, shift=UP * 0.2) for e in ej], lag_ratio=0.3), run_time=1.2)

        # producto tensorial u ⊗ v: tabla de productos
        u = np.array([1.0, 0.6, -0.4, 0.9])
        v = np.array([0.8, -0.7, 0.5, 1.0])
        lado = 0.78
        org = np.array([-1.2, 0.9, 0])
        cel = lambda i, j: org + np.array([j * lado, -i * lado, 0])

        def color(x):
            return interpolate_color(ManimColor(CORAL), ManimColor(CELESTE), (x + 1) / 2)

        colU = VGroup(*[Square(lado * 0.92).move_to(cel(i, -1.35)).set_stroke(width=0).set_fill(color(x), 0.9) for i, x in enumerate(u)])
        filV = VGroup(*[Square(lado * 0.92).move_to(cel(-1.35, j)).set_stroke(width=0).set_fill(color(x), 0.9) for j, x in enumerate(v)])
        lu = tex(r"u", font_size=36, color=TINTA).next_to(colU, LEFT, buff=0.2)
        lv = tex(r"v", font_size=36, color=TINTA).next_to(filV, UP, buff=0.15)
        self.play(LaggedStart(*[GrowFromCenter(c) for c in colU], lag_ratio=0.1),
                  LaggedStart(*[GrowFromCenter(c) for c in filV], lag_ratio=0.1), FadeIn(lu, lv), run_time=1.0)
        tabla = VGroup()
        for i in range(4):
            for j in range(4):
                tabla.add(Square(lado * 0.92).move_to(cel(i, j)).set_stroke(width=0).set_fill(color(u[i] * v[j]), 0.9))
        self.play(LaggedStart(*[FadeIn(c, scale=0.3) for c in tabla], lag_ratio=0.05), run_time=2.0)
        formu = tex(r"(u\otimes v)_{ij}=u_i\,v_j", font_size=42)
        degradado(formu, [CORAL, MAGENTA, CELESTE])
        formu.move_to(DOWN * 2.6)
        self.play(Write(formu), run_time=1.0)
        prod = tex(r"(T\otimes T')(x,y)=T(x)\,T'(y)", font_size=38, color=TINTA).move_to(DOWN * 3.7)
        self.play(FadeIn(prod, shift=UP * 0.2), run_time=0.8)
        self.wait(0.6)

        # un tensor de orden 3: cubo de n^3 componentes
        self.play(FadeOut(VGroup(colU, filV, lu, lv, formu, prod)), tabla.animate.scale(0.6).move_to(LEFT * 2.2 + UP * 0.8), run_time=0.9)
        cubo = VGroup()
        n = 3
        ladoc = 0.5
        base = RIGHT * 1.4 + UP * 0.2
        dx, dy = np.array([ladoc, 0, 0]), np.array([0, ladoc, 0])
        dz = np.array([0.32, 0.22, 0])
        rng = np.random.default_rng(2)
        for k in range(n - 1, -1, -1):
            for i in range(n):
                for j in range(n):
                    p = base + j * dx + (n - 1 - i) * dy + k * dz
                    cara = Polygon(p, p + dx, p + dx + dy, p + dy).set_stroke(TINTA, 1, 0.5)
                    cara.set_fill(color(rng.uniform(-1, 1)), 0.85)
                    cubo.add(cara)
        l2 = tex(r"n^2", font_size=36, color=CELESTE).next_to(tabla, DOWN, buff=0.25)
        l3 = tex(r"n^3", font_size=36, color=VIOLETA).next_to(cubo, DOWN, buff=0.25)
        self.play(LaggedStart(*[FadeIn(c, shift=DOWN * 0.2) for c in cubo], lag_ratio=0.02), FadeIn(l2), run_time=1.8)
        self.play(FadeIn(l3), run_time=0.5)
        dim = tex(r"\dim T^q_p(E)=n^{\,p+q}", font_size=48)
        degradado(dim, DEG_ARCOIRIS)
        dim.move_to(DOWN * 3.2)
        self.play(Write(dim), run_time=1.1)
        self.wait(1.2)

        final = tex(r"T^q_p\otimes T'^{q'}_{p'}\in T^{q+q'}_{p+p'}", font_size=58)
        degradado(final, DEG_ARCOIRIS)
        self.cierre(final, "se multiplican evaluando por separado y sumando los órdenes")
