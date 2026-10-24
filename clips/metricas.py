"""Clips: Métricas y polaridades (Álgebra Lineal y Geometría II), estilo «noche»."""

from estilo_noche import *
from algebra import Plano, recortar, interp


class ClipMetrica(ClipNoche):
    serie = "Métricas y polaridades"
    total = 11


def pila(P: Plano, w, cmax=6, paso=1.0, ancho=3, opacidad=0.75):
    """Una forma lineal x ↦ w·x dibujada como su familia de rectas de nivel."""
    w = np.array(w, dtype=float)
    g = VGroup()
    n2 = w @ w
    if n2 < 1e-6:
        return g
    d = np.array([-w[1], w[0]]) / np.sqrt(n2)
    cols = color_gradient([CORAL, MAGENTA, VIOLETA, AZUL, CELESTE, TURQUESA], 2 * cmax + 1)
    for k, c in enumerate(np.arange(-cmax, cmax + 1) * paso):
        p0 = c * w / n2
        seg = recortar(p0 - 30 * d, p0 + 30 * d, P.B)
        if seg is None:
            continue
        l = Line(P.p(seg[0]), P.p(seg[1]), stroke_width=ancho * (1.6 if c == 0 else 1), color=cols[k])
        g.add(l.set_stroke(opacity=opacidad if c != 0 else 0.95))
    return g


def proyector(centro, esc, phi, elev=0.38):
    def proy(x, y, z):
        a = phi.get_value()
        X = x * np.cos(a) - y * np.sin(a)
        Yd = x * np.sin(a) + y * np.cos(a)
        Y = z * np.cos(elev) + Yd * np.sin(elev)
        return centro + esc * np.array([X, Y, 0])
    return proy


# ---------------------------------------------------------------------------
class M01_Metrica(ClipMetrica):
    indice = 1
    seccion = "Definición"
    titulo = "¿Qué es una métrica?"
    subtitulo = "una aplicación bilineal"
    colores_titulo = [TURQUESA, CELESTE, AZUL, VIOLETA]

    def cuerpo(self):
        d = tex(r"T_2:\ E\times E\longrightarrow k", font_size=50)
        degradado(d, DEG_FRIO)
        d.move_to(UP * 4.35)
        self.play(Write(d), run_time=1.0)
        l1 = tex(r"T_2(\lambda e_1+\mu e_2,\,e)=\lambda T_2(e_1,e)+\mu T_2(e_2,e)", font_size=36, color=CELESTE)
        l2 = tex(r"T_2(e,\,\lambda e_1+\mu e_2)=\lambda T_2(e,e_1)+\mu T_2(e,e_2)", font_size=36, color=VIOLETA)
        VGroup(l1, l2).arrange(DOWN, buff=0.35).move_to(UP * 2.85)
        self.play(FadeIn(l1, shift=RIGHT * 0.3), run_time=0.9)
        self.play(FadeIn(l2, shift=RIGHT * 0.3), run_time=0.9)

        P = Plano(DOWN * 1.0, u=0.95, B=2.6)
        e = np.array([1.2, 0.5])
        lam = ValueTracker(-1.6)
        a = np.array([0.55, 1.0])
        niveles = pila(P, e, cmax=5, paso=0.6)
        fe = P.flecha(e, AMBAR, 7)
        le = tex(r"e", font_size=34, color=AMBAR).move_to(P.p(e * 1.25))
        self.play(FadeIn(P.marco()), Create(niveles), GrowArrow(fe), FadeIn(le), run_time=1.2)
        lbl = self.rotulo("con e fijo, T₂(−, e) es una forma lineal: sus niveles son rectas paralelas",
                          pos=DOWN * 4.05, size=22, color=GRIS)
        self.play(FadeIn(lbl), run_time=0.5)

        def mover():
            x = lam.get_value() * a
            f = P.flecha(x if abs(lam.get_value()) > 0.03 else a * 0.03, TURQUESA, 6)
            val = tex(r"T_2(\lambda a,e)=%.2f" % (x @ e), font_size=36, color=TURQUESA).move_to(DOWN * 4.9)
            ll = tex(r"\lambda a", font_size=30, color=TURQUESA).move_to(P.p(x + np.array([0.35, 0.1])))
            return VGroup(f, val, ll)

        mv = always_redraw(mover)
        self.play(FadeIn(mv), run_time=0.4)
        self.play(lam.animate.set_value(1.9), run_time=3.2, rate_func=smooth)
        mv.clear_updaters()
        self.limpiar(d)

        # --- aviso: bilineal no es lineal en E×E -------------------------------
        av = tex(r"T_2(2e_1,\,2e_2)=4\,T_2(e_1,e_2)\neq 2\,T_2(e_1,e_2)", font_size=40)
        degradado(av, [CORAL, MAGENTA])
        av.move_to(UP * 2.9)
        aviso = self.rotulo("bilineal ≠ lineal sobre el espacio producto", pos=UP * 1.9, size=26, color=CORAL)
        self.play(Write(av), FadeIn(aviso), run_time=1.3)
        esp = tex(r"\mathcal T_2(E)", font_size=52)
        degradado(esp, DEG_AZUL)
        esp.move_to(UP * 0.4)
        ops = VGroup(
            tex(r"(T_2+T_2')(e,e')=T_2(e,e')+T_2'(e,e')", font_size=36, color=TURQUESA),
            tex(r"(\lambda T_2)(e,e')=\lambda\,T_2(e,e')", font_size=36, color=CELESTE),
        ).arrange(DOWN, buff=0.35).move_to(DOWN * 1.3)
        self.play(Write(esp), run_time=0.8)
        self.play(LaggedStart(*[FadeIn(o, shift=UP * 0.2) for o in ops], lag_ratio=0.35), run_time=1.2)
        ej = tex(r"\langle e_1,e_2\rangle=\|e_1\|\,\|e_2\|\cos\theta", font_size=40, color=AMBAR).move_to(DOWN * 3.2)
        self.play(FadeIn(ej, shift=UP * 0.2), run_time=0.7)
        self.wait(1.3)

        final = tex(r"T_2\ \text{lineal en cada factor}", font_size=56)
        degradado(final, DEG_FRIO)
        self.cierre(final, "las métricas forman un espacio vectorial: suma y escalar punto a punto")


class M02_Polaridad(ClipMetrica):
    indice = 2
    seccion = "Polaridad asociada"
    titulo = "Polaridad asociada"
    subtitulo = "cada vector se convierte en un covector"
    colores_titulo = [AMBAR, CORAL, MAGENTA, VIOLETA]

    def cuerpo(self):
        d = tex(r"\phi_{T_2}:E\to E^*,\qquad [\phi_{T_2}(e)](e')=T_2(e,e')", font_size=40)
        degradado(d, DEG_CALIDO + [VIOLETA])
        d.move_to(UP * 4.35)
        self.play(Write(d), run_time=1.3)

        P = Plano(UP * 0.6, u=0.95, B=3.0)
        G = np.array([[2.0, 0.6], [0.6, 1.0]])
        ang, rad = ValueTracker(0.3), ValueTracker(0.9)

        def escena():
            e = rad.get_value() * np.array([np.cos(ang.get_value()), np.sin(ang.get_value())])
            w = G.T @ e
            return VGroup(pila(P, w, cmax=7, paso=1.0), P.flecha(e, AMBAR, 7),
                          tex(r"e", font_size=32, color=AMBAR).move_to(P.p(e * 1.15 + np.array([0.15, 0.15]))))

        esc = always_redraw(escena)
        lab = tex(r"\phi(e)=T_2(e,-)", font_size=36, color=CELESTE).move_to(DOWN * 2.85)
        self.play(FadeIn(P.marco()), FadeIn(esc), FadeIn(lab), run_time=1.0)
        self.play(ang.animate.set_value(0.3 + 1.8), run_time=2.4, rate_func=smooth)
        self.play(rad.animate.set_value(1.9), run_time=1.4)
        r = self.rotulo("más largo e ⇒ niveles más juntos: φ es lineal", pos=DOWN * 3.75, size=24, color=GRIS)
        self.play(FadeIn(r), rad.animate.set_value(0.6), ang.animate.set_value(3.6), run_time=2.0)
        esc.clear_updaters()
        self.limpiar(d)

        # --- demostración de la linealidad -------------------------------------
        pasos = VGroup(
            tex(r"[\phi(\lambda e_1+\mu e_2)](e)", r"=", r"T_2(\lambda e_1+\mu e_2,\,e)", font_size=36),
            tex(r"=", r"\lambda T_2(e_1,e)+\mu T_2(e_2,e)", font_size=36),
            tex(r"=", r"[\lambda\phi(e_1)+\mu\phi(e_2)](e)", font_size=36),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.4).move_to(UP * 2.2)
        pasos[0][0].set_color(AMBAR); pasos[0][2].set_color(CELESTE)
        pasos[1][1].set_color(VIOLETA); pasos[2][1].set_color(AMBAR)
        for p in pasos:
            self.play(Write(p), run_time=0.9)
        iso = tex(r"\mathcal T_2(E)\ \xrightarrow{\ \sim\ }\ \mathrm{Hom}_k(E,E^*)", font_size=44)
        degradado(iso, DEG_ARCOIRIS)
        iso.move_to(DOWN * 0.8)
        self.play(Write(iso), run_time=1.2)
        inv = tex(r"\phi\ \longmapsto\ T_2^\phi(e,e')=[\phi(e)](e')", font_size=36, color=GRIS).move_to(DOWN * 2.0)
        self.play(FadeIn(inv), run_time=0.7)
        dim = tex(r"\dim\mathcal T_2(E)=n\cdot n=n^2", font_size=44, color=AMBAR).move_to(DOWN * 3.4)
        self.play(Write(dim), run_time=0.9)
        self.wait(1.0)

        final = tex(r"T_2\ \longleftrightarrow\ \phi_{T_2}", font_size=64)
        degradado(final, DEG_CALIDO + [VIOLETA])
        self.cierre(final, "métrica y polaridad: el mismo objeto visto de dos maneras")


class M03_Transformada(ClipMetrica):
    indice = 3
    seccion = "Polaridad transformada"
    titulo = "Retroceso de una polaridad"
    subtitulo = "τ*φ = τ* ∘ φ ∘ τ"
    colores_titulo = [CELESTE, VIOLETA, MAGENTA]

    def cuerpo(self):
        # diagrama conmutativo
        pos = {"E": LEFT * 2.2 + UP * 3.5, "E*": RIGHT * 2.2 + UP * 3.5,
               "Eb": LEFT * 2.2 + UP * 1.3, "Eb*": RIGHT * 2.2 + UP * 1.3}
        nodos = {
            "E": tex(r"E", font_size=48, color=CELESTE), "E*": tex(r"E^*", font_size=48, color=CELESTE),
            "Eb": tex(r"\bar E", font_size=48, color=VIOLETA), "Eb*": tex(r"\bar E^*", font_size=48, color=VIOLETA),
        }
        for k, m in nodos.items():
            m.move_to(pos[k])
        fl = {
            "top": Arrow(pos["E"], pos["E*"], buff=0.5, color=AMBAR, stroke_width=5),
            "izq": Arrow(pos["E"], pos["Eb"], buff=0.45, color=GRIS, stroke_width=4),
            "abajo": Arrow(pos["Eb"], pos["Eb*"], buff=0.5, color=MAGENTA, stroke_width=5),
            "der": Arrow(pos["Eb*"], pos["E*"], buff=0.45, color=GRIS, stroke_width=4),
        }
        et = VGroup(
            tex(r"\tau^*\phi", font_size=34, color=AMBAR).next_to(fl["top"], UP, buff=0.1),
            tex(r"\tau", font_size=34, color=GRIS).next_to(fl["izq"], LEFT, buff=0.1),
            tex(r"\phi", font_size=34, color=MAGENTA).next_to(fl["abajo"], DOWN, buff=0.1),
            tex(r"\tau^*", font_size=34, color=GRIS).next_to(fl["der"], RIGHT, buff=0.1),
        )
        self.play(LaggedStart(*[FadeIn(m, scale=0.7) for m in nodos.values()], lag_ratio=0.15), run_time=0.9)
        self.play(LaggedStart(*[GrowArrow(f) for f in fl.values()], lag_ratio=0.2), FadeIn(et), run_time=1.3)
        camino = VMobject().set_points_as_corners([pos["E"] + DOWN * 0.45, pos["Eb"] + UP * 0.45, pos["Eb"] + RIGHT * 0.5,
                                                   pos["Eb*"] + LEFT * 0.5, pos["Eb*"] + UP * 0.45, pos["E*"] + DOWN * 0.45])
        bola = Dot(radius=0.12, color=TINTA)
        bola2 = Dot(radius=0.12, color=AMBAR)
        self.play(MoveAlongPath(bola, camino), MoveAlongPath(bola2, Line(pos["E"] + RIGHT * 0.5, pos["E*"] + LEFT * 0.6)),
                  run_time=1.8, rate_func=smooth)
        self.play(Flash(pos["E*"], color=AMBAR), FadeOut(bola, bola2), run_time=0.6)
        ev = tex(r"[(\tau^*\phi)(e_1)](e_2)=[\phi(\tau e_1)](\tau e_2)", font_size=38)
        degradado(ev, [AMBAR, MAGENTA])
        ev.move_to(UP * 0.0)
        self.play(Write(ev), run_time=1.1)

        # --- ejemplo del PDF ------------------------------------------------------
        datos = tex(r"\tau(x,y)=(x+y,\,x-y,\,2y),\quad \phi=\text{prod. escalar en }\mathbb R^3", font_size=30, color=GRIS)
        datos.move_to(DOWN * 1.1)
        self.play(FadeIn(datos), run_time=0.6)
        izq = VGroup(
            tex(r"\tau e_1=(3,-1,4)", font_size=32, color=MAGENTA),
            tex(r"\tau e_2=(2,4,-2)", font_size=32, color=MAGENTA),
            tex(r"6-4-8", font_size=32, color=MAGENTA),
        ).arrange(DOWN, buff=0.25)
        der = VGroup(
            tex(r"\tau^*\phi=2x_1x_2+6y_1y_2", font_size=32, color=AMBAR),
            tex(r"e_1=(1,2),\ e_2=(3,-1)", font_size=32, color=AMBAR),
            tex(r"6-12", font_size=32, color=AMBAR),
        ).arrange(DOWN, buff=0.25)
        VGroup(izq, der).arrange(RIGHT, buff=0.7).move_to(DOWN * 2.75)
        ajustar(VGroup(izq, der))
        for a, b in zip(izq, der):
            self.play(FadeIn(a, shift=DOWN * 0.15), FadeIn(b, shift=DOWN * 0.15), run_time=0.6)
        res = tex(r"=-6", font_size=56)
        degradado(res, [MAGENTA, AMBAR])
        res.move_to(DOWN * 4.6)
        self.play(TransformFromCopy(VGroup(izq[2], der[2]), res), run_time=1.0)
        self.play(Indicate(res, color=TINTA), run_time=0.7)
        self.wait(0.8)

        final = tex(r"\tau^*\phi_{\bar T_2}=\phi_{\tau^*\bar T_2}", font_size=58)
        degradado(final, [CELESTE, VIOLETA, MAGENTA, AMBAR])
        self.cierre(final, "métricas equivalentes ⟺ polaridades equivalentes")


class M04_SimetricaHemisimetrica(ClipMetrica):
    indice = 4
    seccion = "Métricas simétricas y hemisimétricas"
    titulo = "Simétrica + hemisimétrica"
    subtitulo = "una descomposición única"
    colores_titulo = [TURQUESA, CELESTE, MAGENTA, CORAL]

    def cuerpo(self):
        tr = tex(r"T_2^*(e,e')=T_2(e',e)", font_size=46)
        degradado(tr, DEG_FRIO)
        tr.move_to(UP * 4.35)
        self.play(Write(tr), run_time=0.9)

        def M(filas, cols, fs=40):
            m = Matrix(filas, element_to_mobject=lambda x: MathTex(x, tex_template=PLANTILLA, font_size=fs * ESCALA),
                       h_buff=0.9, v_buff=0.75, bracket_h_buff=0.15)
            for e, c in zip(m.get_entries(), cols):
                e.set_color(c)
            m.get_brackets().set_color(GRIS)
            return m

        G = [["1", "4", "-2"], ["0", "3", "5"], ["2", "-1", "2"]]
        diag, sup, inf = AMBAR, CELESTE, MAGENTA
        cg = [diag, sup, sup, inf, diag, sup, inf, inf, diag]
        Gm = M(G, cg).move_to(UP * 2.3 + LEFT * 2.0)
        Gt = M([[G[j][i] for j in range(3)] for i in range(3)], [diag, inf, inf, sup, diag, inf, sup, sup, diag]).move_to(UP * 2.3 + RIGHT * 2.0)
        lg = tex(r"G", font_size=36, color=TINTA).next_to(Gm, DOWN, buff=0.15)
        lgt = tex(r"G^t", font_size=36, color=TINTA).next_to(Gt, DOWN, buff=0.15)
        self.play(FadeIn(Gm), FadeIn(lg), run_time=0.7)
        # espejo respecto a la diagonal
        copia = Gm.copy()
        self.play(Rotate(copia, PI, axis=np.array([1, -1, 0]), about_point=Gm.get_center()), run_time=1.2)
        self.play(copia.animate.move_to(Gt), run_time=0.7)
        self.remove(copia)
        self.add(Gt)
        self.play(FadeIn(lgt), run_time=0.3)
        S = M([["1", "2", "0"], ["2", "3", "2"], ["0", "2", "2"]], [TURQUESA] * 9, fs=36)
        H = M([["0", "2", "-2"], ["-2", "0", "3"], ["2", "-3", "0"]], [CORAL] * 9, fs=36)
        fila = VGroup(tex(r"G=", font_size=40), S, tex("+", font_size=40), H).arrange(RIGHT, buff=0.2)
        ajustar(fila, 8.0).move_to(DOWN * 0.5)
        ls = tex(r"S_2=\tfrac12(T_2+T_2^*)", font_size=32, color=TURQUESA).next_to(S, DOWN, buff=0.25)
        lh = tex(r"H_2=\tfrac12(T_2-T_2^*)", font_size=32, color=CORAL).next_to(H, DOWN, buff=0.25)
        self.play(FadeIn(fila[0]), TransformFromCopy(VGroup(Gm, Gt), S), FadeIn(fila[2]), TransformFromCopy(VGroup(Gm, Gt), H),
                  run_time=1.6)
        self.play(FadeIn(ls, lh), run_time=0.6)
        car = self.rotulo("dividir por 2 exige característica ≠ 2", pos=DOWN * 2.85, size=24, color=AMBAR)
        self.play(FadeIn(car), run_time=0.5)
        uni = tex(r"S_2-S_2'=H_2'-H_2\ \ \Rightarrow\ \ 0", font_size=38, color=TINTA).move_to(DOWN * 3.8)
        self.play(Write(uni), run_time=1.0)
        dims = tex(r"n^2=\tfrac{n(n+1)}2+\tfrac{n(n-1)}2", font_size=40)
        degradado(dims, [TURQUESA, CORAL])
        dims.move_to(DOWN * 4.95)
        self.play(Write(dims), run_time=1.0)
        self.wait(1.0)

        final = tex(r"\mathcal T_2(E)=\mathcal S_2(E)\oplus\mathcal H_2(E)", font_size=56)
        degradado(final, [TURQUESA, CELESTE, MAGENTA, CORAL])
        self.cierre(final, "clasificar métricas se reduce a los casos simétrico y hemisimétrico")


class M05_Matriz(ClipMetrica):
    indice = 5
    seccion = "Representación matricial"
    titulo = "Matriz y cambio de base"
    subtitulo = "congruencia, no semejanza"
    colores_titulo = [AMBAR, CORAL, VIOLETA, CELESTE]

    def cuerpo(self):
        g = tex(r"g_{ij}=T_2(e_i,e_j)", r"\qquad", r"T_2(u,v)=U^t\,G\,V", font_size=42)
        g[0].set_color(AMBAR); g[2].set_color_by_gradient(CELESTE, VIOLETA)
        g.move_to(UP * 4.35)
        self.play(Write(g), run_time=1.2)
        prod = tex(r"\begin{pmatrix}1&2\end{pmatrix}", r"\begin{pmatrix}2&-1\\-1&2\end{pmatrix}",
                   r"\begin{pmatrix}3\\-1\end{pmatrix}", r"=", r"\begin{pmatrix}0&3\end{pmatrix}",
                   r"\begin{pmatrix}3\\-1\end{pmatrix}", r"=-3", font_size=38)
        prod[0].set_color(CELESTE); prod[1].set_color(AMBAR); prod[2].set_color(VIOLETA)
        prod[4].set_color(TURQUESA); prod[5].set_color(VIOLETA); prod[6].set_color(MAGENTA)
        ajustar(prod).move_to(UP * 2.9)
        self.play(FadeIn(prod[:3]), run_time=0.7)
        self.play(FadeIn(prod[3]), TransformFromCopy(prod[:2], prod[4]), FadeIn(prod[5]), run_time=1.0)
        self.play(Write(prod[6]), run_time=0.6)

        # misma elipse, dos sistemas de coordenadas
        P = Plano(DOWN * 0.55, u=0.72, B=3.4)
        Gm = np.array([[2.0, -1.0], [-1.0, 2.0]])
        Bm = np.array([[3.0, 1 / 3], [2.0, 1 / 3]])
        L = np.linalg.cholesky(np.linalg.inv(Gm))
        can = P.rejilla(colores=(GRIS, GRIS), opacidad=0.25, ancho=1)
        elipses = VGroup()
        for c, col in ((1, AMBAR), (4, CORAL), (9, MAGENTA)):
            el = VMobject().set_points_smoothly([P.p(np.sqrt(c) * (L @ [np.cos(a), np.sin(a)])) for a in np.linspace(0, TAU, 100)])
            elipses.add(el.set_stroke(col, 4))
        self.play(FadeIn(P.marco()), FadeIn(can), LaggedStart(*[Create(e) for e in elipses], lag_ratio=0.3), run_time=1.3)
        b1, b2 = P.flecha(Bm[:, 0], CELESTE, 7), P.flecha(Bm[:, 1], VIOLETA, 7)
        lb = VGroup(tex(r"e_1'=3e_1+2e_2", font_size=30, color=CELESTE).move_to(P.p(1.75, 2.75)),
                    tex(r"e_2'=\tfrac13(e_1+e_2)", font_size=30, color=VIOLETA).move_to(P.p(-1.6, 2.75)))
        self.play(GrowArrow(b1), GrowArrow(b2), FadeIn(lb), run_time=1.0)
        val = tex(r"q(e_1')=\bar g_{11}=14", font_size=32, color=AMBAR).move_to(P.p(1.75, -2.8))
        self.play(FadeIn(val), Indicate(b1, color=TINTA), run_time=0.9)
        cong = tex(r"\bar G=B^t\,G\,B", font_size=48)
        degradado(cong, [CELESTE, AMBAR, VIOLETA])
        cong.move_to(DOWN * 3.5)
        self.play(Write(cong), run_time=0.9)
        res = tex(r"B=\begin{pmatrix}3&\frac13\\2&\frac13\end{pmatrix}\ \Rightarrow\ \bar G=\begin{pmatrix}14&\frac53\\ \frac53&\frac29\end{pmatrix}",
                  font_size=36, color=TINTA).move_to(DOWN * 4.9)
        self.play(FadeIn(res, shift=UP * 0.2), run_time=0.8)
        self.wait(1.4)

        final = tex(r"\bar G=B^t\,G\,B", font_size=66)
        degradado(final, [CELESTE, AMBAR, VIOLETA])
        self.cierre(final, "la elipse no cambia; cambian sus coordenadas")


class M06_BaseMetricas(ClipMetrica):
    indice = 6
    seccion = "Base del espacio de métricas"
    titulo = "Producto tensorial ω ⊗ ω′"
    subtitulo = "la base del espacio de métricas"
    colores_titulo = [TURQUESA, CELESTE, VIOLETA, MAGENTA]

    def cuerpo(self):
        pt = tex(r"(\omega\otimes\omega')(e,e')=\omega(e)\,\omega'(e')", font_size=44)
        degradado(pt, DEG_FRIO)
        pt.move_to(UP * 4.35)
        self.play(Write(pt), run_time=1.1)
        n = 3
        lado = 1.0
        org = np.array([-1.0, 2.2, 0])
        cel = lambda i, j: org + np.array([j * lado, -i * lado, 0])
        celdas = VGroup(*[Square(lado * 0.92).move_to(cel(i, j)).set_stroke(GRIS, 1.5, 0.6).set_fill("#081430", 0.7)
                          for i in range(n) for j in range(n)])
        fil = VGroup(*[tex(r"\omega_%d" % (i + 1), font_size=32, color=CELESTE).move_to(cel(i, -1)) for i in range(n)])
        col = VGroup(*[tex(r"\omega_%d" % (j + 1), font_size=32, color=VIOLETA).move_to(cel(-1, j)) for j in range(n)])
        self.play(FadeIn(celdas), FadeIn(fil, col), run_time=0.8)
        lab = tex(r"\omega_1\otimes\omega_1", font_size=38, color=AMBAR).move_to(DOWN * 1.3)
        luz = celdas[0].copy().set_fill(AMBAR, 0.85).set_stroke(TINTA, 2)
        self.play(FadeIn(luz), FadeIn(lab), run_time=0.4)
        cols = color_gradient([TURQUESA, CELESTE, AZUL, VIOLETA, MAGENTA, CORAL, AMBAR, LIMA, TURQUESA], 9)
        for k in range(1, 9):
            i, j = divmod(k, 3)
            nl = celdas[k].copy().set_fill(cols[k], 0.85).set_stroke(TINTA, 2)
            nlab = tex(r"\omega_%d\otimes\omega_%d\ \leftrightarrow\ M_{%d%d}" % (i + 1, j + 1, i + 1, j + 1), font_size=38,
                       color=cols[k]).move_to(DOWN * 1.3)
            self.play(Transform(luz, nl), Transform(lab, nlab), run_time=0.3)
        self.play(FadeOut(luz), run_time=0.3)
        vals = [["2", "-1", "0"], ["-1", "3", "1"], ["0", "1", "2"]]
        nums = VGroup()
        for i in range(n):
            for j in range(n):
                nums.add(tex(vals[i][j], font_size=34, color=cols[3 * i + j]).move_to(cel(i, j)))
        expr = tex(r"T_2=\sum_{i,j}T_2(e_i,e_j)\,\omega_i\otimes\omega_j", font_size=42)
        degradado(expr, DEG_ARCOIRIS)
        expr.move_to(DOWN * 1.3)
        self.play(ReplacementTransform(lab, expr), LaggedStart(*[FadeIn(x, scale=0.5) for x in nums], lag_ratio=0.08), run_time=1.4)
        ind = tex(r"\sum c_{ij}\,\omega_i\otimes\omega_j=0\ \xrightarrow{(e_h,e_k)}\ c_{hk}=0", font_size=36, color=GRIS)
        ind.move_to(DOWN * 2.6)
        self.play(FadeIn(ind), run_time=0.7)
        # base simétrica: pares (i,j) y (j,i) encendidos a la vez
        sim = tex(r"S_{ij}=\omega_i\otimes\omega_j+\omega_j\otimes\omega_i,\ \ i\le j", font_size=38, color=TURQUESA)
        sim.move_to(DOWN * 3.85)
        self.play(Write(sim), run_time=1.0)
        pares = VGroup()
        for i in range(n):
            for j in range(i, n):
                g2 = VGroup(celdas[3 * i + j].copy(), celdas[3 * j + i].copy()).set_fill(TURQUESA, 0.35).set_stroke(TURQUESA, 3)
                pares.add(g2)
        self.play(LaggedStart(*[FadeIn(p) for p in pares], lag_ratio=0.25), run_time=1.6)
        cnt = tex(r"\dim\mathcal S_2(E)=\tfrac{n(n+1)}{2}=6", font_size=38, color=TURQUESA).move_to(DOWN * 4.95)
        self.play(FadeIn(cnt), run_time=0.6)
        self.wait(0.8)

        final = tex(r"\{\omega_i\otimes\omega_j\}_{i,j}\ \text{base de}\ \mathcal T_2(E)", font_size=50)
        degradado(final, DEG_ARCOIRIS)
        self.cierre(final, "n² métricas elementales: la matriz de ωᵢ ⊗ ωⱼ es Mᵢⱼ")


class M07_Radical(ClipMetrica):
    indice = 7
    seccion = "Radical y rango"
    titulo = "Radical e irreducibilidad"
    subtitulo = "los vectores que no ven a nadie"
    colores_titulo = [CORAL, MAGENTA, VIOLETA, CELESTE]

    def cuerpo(self):
        r = tex(r"\mathrm{rad}\,T_2=\ker\phi_{T_2}=\{e:\ T_2(e,e')=0\ \ \forall e'\}", font_size=38)
        degradado(r, [CORAL, MAGENTA, VIOLETA])
        r.move_to(UP * 4.35)
        self.play(Write(r), run_time=1.3)
        P = Plano(UP * 0.7, u=0.95, B=2.9)
        G = np.array([[1.0, 0.0], [0.0, 0.0]])
        ang = ValueTracker(0.2)

        def escena():
            e = 1.5 * np.array([np.cos(ang.get_value()), np.sin(ang.get_value())])
            return VGroup(pila(P, G @ e, cmax=6, paso=0.7), P.flecha(e, AMBAR, 7))

        esc = always_redraw(escena)
        gl = tex(r"G=\begin{pmatrix}1&0\\0&0\end{pmatrix}", font_size=36, color=TINTA).move_to(P.p(-1.7, 2.3))
        self.play(FadeIn(P.marco()), FadeIn(esc), FadeIn(gl), run_time=0.9)
        self.play(ang.animate.set_value(PI / 2 - 0.25), run_time=2.0, rate_func=smooth)
        self.play(ang.animate.set_value(PI / 2), run_time=1.2)
        eje = Line(P.p(0, -2.9), P.p(0, 2.9), stroke_width=8).set_color([CORAL, MAGENTA, CORAL])
        lr = tex(r"\mathrm{rad}\,T_2", font_size=34, color=CORAL).move_to(P.p(0.9, -2.4))
        self.play(Create(eje), FadeIn(lr), Flash(P.p(0, 1.5), color=CORAL), run_time=0.9)
        nada = self.rotulo("φ(e) = 0: e es ortogonal a todo el espacio", pos=DOWN * 2.6, size=24, color=CORAL)
        self.play(FadeIn(nada), run_time=0.5)
        self.play(ang.animate.set_value(PI / 2 + 0.9), run_time=1.4)
        esc.clear_updaters()
        rn = tex(r"\dim E=\dim\mathrm{rad}\,T_2+\mathrm{rango}\,T_2", font_size=40)
        degradado(rn, [AMBAR, CORAL, CELESTE])
        rn.move_to(DOWN * 3.6)
        self.play(Write(rn), run_time=1.1)
        ej = tex(r"2=1+1", font_size=38, color=GRIS).move_to(DOWN * 4.55)
        self.play(FadeIn(ej), run_time=0.4)
        irr = tex(r"\text{irreducible}\iff\phi_{T_2}\ \text{iso}\iff\det G\neq0", font_size=36, color=TURQUESA).move_to(DOWN * 5.45)
        self.play(Write(irr), run_time=1.0)
        self.wait(1.0)

        final = tex(r"\mathrm{rad}\,T_2=\{0\}\iff \phi_{T_2}:E\xrightarrow{\sim}E^*", font_size=50)
        degradado(final, [CORAL, MAGENTA, CELESTE, TURQUESA])
        self.cierre(final, "métrica irreducible: rango máximo, toda forma lineal es T₂(e, −)")


class M08_Ortogonal(ClipMetrica):
    indice = 8
    seccion = "Subespacio ortogonal"
    titulo = "El subespacio ortogonal"
    subtitulo = "¿siempre es un suplementario?"
    colores_titulo = [TURQUESA, CELESTE, AMBAR, CORAL]

    def cuerpo(self):
        d = tex(r"V^\perp=\{e\in E:\ T_2(e,v)=0\ \ \forall v\in V\}=\phi^{-1}(V^\circ)", font_size=36)
        degradado(d, DEG_FRIO)
        d.move_to(UP * 4.35)
        self.play(Write(d), run_time=1.3)
        P = Plano(UP * 0.6, u=0.9, B=3.0)
        G = ValueTracker(0)  # 0: euclídea, 1: Minkowski (1, -1)
        a = ValueTracker(0.35)

        def lineas():
            m = G.get_value()
            Gm = np.diag([1.0, 1 - 2 * m])
            v = np.array([np.cos(a.get_value()), np.sin(a.get_value())])
            w = Gm @ v
            vp = np.array([-w[1], w[0]])
            g = VGroup(
                Line(P.p(-4 * v), P.p(4 * v), stroke_width=6, color=CELESTE),
                Line(P.p(-4 * vp / np.linalg.norm(vp)), P.p(4 * vp / np.linalg.norm(vp)), stroke_width=6, color=AMBAR),
            )
            for l in g:
                seg = recortar(np.array(l.get_start()[:2] - P.c[:2]) / P.u, np.array(l.get_end()[:2] - P.c[:2]) / P.u, P.B)
                l.put_start_and_end_on(P.p(seg[0]), P.p(seg[1]))
            et = VGroup(tex(r"V", font_size=34, color=CELESTE).move_to(P.p(2.55 * v + np.array([0.3, -0.25]))),
                        tex(r"V^\perp", font_size=34, color=AMBAR).move_to(P.p(2.55 * vp / np.linalg.norm(vp) + np.array([0.35, 0.1]))))
            return VGroup(g, et)

        ln = always_redraw(lineas)
        tipo = always_redraw(lambda: tex(r"G=\begin{pmatrix}1&0\\0&%d\end{pmatrix}" % (1 if G.get_value() < 0.5 else -1),
                                         font_size=34, color=TINTA).move_to(P.p(-1.9, 2.35)))
        self.play(FadeIn(P.marco()), FadeIn(P.rejilla(colores=(GRIS, GRIS), opacidad=0.12, ancho=1)), FadeIn(ln), FadeIn(tipo), run_time=1.0)
        self.play(a.animate.set_value(1.2), run_time=1.6)
        self.play(G.animate.set_value(1), run_time=1.4)
        cono = VGroup(P.recta((1, 1), MAGENTA, 3), P.recta((1, -1), MAGENTA, 3))
        lc = tex(r"q=0", font_size=30, color=MAGENTA).move_to(P.p(2.3, 2.7))
        self.play(Create(cono), FadeIn(lc), a.animate.set_value(0.35), run_time=1.6)
        self.play(a.animate.set_value(PI / 4), run_time=2.0, rate_func=smooth)
        aviso = tex(r"V=V^\perp:\ \ V\cap V^\perp\neq\{0\}", font_size=38, color=CORAL).move_to(DOWN * 2.9)
        self.play(Write(aviso), Flash(P.p(1.5, 1.5), color=CORAL), run_time=1.0)
        self.play(a.animate.set_value(PI / 4 + 0.5), run_time=1.2)
        ln.clear_updaters(); tipo.clear_updaters()
        teo = tex(r"E=V\oplus V^\perp\iff T_2|_V\ \text{irreducible}", font_size=40)
        degradado(teo, [CELESTE, TURQUESA, AMBAR])
        teo.move_to(DOWN * 4.1)
        self.play(Write(teo), run_time=1.1)
        dim = tex(r"T_2\ \text{irreducible}\ \Rightarrow\ \dim V^\perp=n-\dim V", font_size=34, color=GRIS).move_to(DOWN * 5.1)
        self.play(FadeIn(dim), run_time=0.6)
        self.wait(1.0)

        final = tex(r"E=V\oplus V^\perp\iff V\cap V^\perp=\{0\}", font_size=52)
        degradado(final, [CELESTE, TURQUESA, AMBAR, CORAL])
        self.cierre(final, "un subespacio isótropo coincide con su ortogonal")


class M09_FormasCuadraticas(ClipMetrica):
    indice = 9
    seccion = "Formas cuadráticas"
    titulo = "Formas cuadráticas"
    subtitulo = "y la identidad de polarización"
    colores_titulo = [AMBAR, CORAL, MAGENTA, VIOLETA, CELESTE]

    def cuerpo(self):
        q = tex(r"q(e)=T_2(e,e)=\sum_{i,j}g_{ij}x_ix_j", font_size=44)
        degradado(q, DEG_CALIDO + [VIOLETA])
        q.move_to(UP * 4.35)
        self.play(Write(q), run_time=1.1)

        phi = ValueTracker(-0.6)
        proy = proyector(UP * 0.8, 1.0, phi, elev=0.42)
        f = lambda x, y: (x * x + 1.5 * x * y - y * y) * 0.45
        cols = color_gradient([TURQUESA, CELESTE, AZUL, VIOLETA, MAGENTA, CORAL], 11)

        def malla():
            g = VGroup()
            us = np.linspace(-2, 2, 11)
            for k, x0 in enumerate(us):
                l1 = VMobject(stroke_width=3, stroke_color=cols[k]).set_points_smoothly([proy(x0, y, f(x0, y)) for y in np.linspace(-2, 2, 30)])
                l2 = VMobject(stroke_width=2, stroke_color=cols[k]).set_points_smoothly([proy(x, x0, f(x, x0)) for x in np.linspace(-2, 2, 30)])
                l2.set_stroke(opacity=0.55)
                g.add(l1, l2)
            ejes = VGroup(*[Arrow(proy(*a), proy(*b), buff=0, stroke_width=3, color=GRIS) for a, b in
                            (((-2.4, 0, 0), (2.6, 0, 0)), ((0, -2.4, 0), (0, 2.6, 0)), ((0, 0, -1.8), (0, 0, 2.4)))])
            return VGroup(ejes, g)

        sup = always_redraw(malla)
        lab = tex(r"q=x^2+\tfrac32xy-y^2", font_size=34, color=CORAL).move_to(DOWN * 2.15)
        self.play(FadeIn(sup), FadeIn(lab), run_time=1.0)
        self.play(phi.animate.set_value(0.9), run_time=3.2, rate_func=smooth)
        sup.clear_updaters()
        inv = self.rotulo("polinomio homogéneo de grado 2: lo es en cualquier base", pos=DOWN * 3.05, size=24, color=GRIS)
        self.play(FadeIn(inv), run_time=0.5)
        self.wait(0.6)
        self.limpiar(q)

        # --- polarización: el paralelogramo -----------------------------------
        P = Plano(UP * 1.0, u=1.0, B=2.6)
        u, v = np.array([1.6, 0.4]), np.array([0.5, 1.4])
        fu, fv = P.flecha(u, CELESTE, 6), P.flecha(v, VIOLETA, 6)
        fs = P.flecha(u + v, AMBAR, 7)
        lados = VGroup(DashedLine(P.p(u), P.p(u + v), color=GRIS), DashedLine(P.p(v), P.p(u + v), color=GRIS))
        et = VGroup(tex("u", font_size=34, color=CELESTE).move_to(P.p(u + np.array([0.25, -0.25]))),
                    tex("v", font_size=34, color=VIOLETA).move_to(P.p(v + np.array([-0.3, 0.1]))),
                    tex("u+v", font_size=34, color=AMBAR).move_to(P.p(u + v + np.array([0.3, 0.25]))))
        self.play(FadeIn(P.marco()), GrowArrow(fu), GrowArrow(fv), FadeIn(et[:2]), run_time=0.8)
        self.play(Create(lados), GrowArrow(fs), FadeIn(et[2]), run_time=0.9)
        des = tex(r"q(u+v)=q(u)+2\,T_2(u,v)+q(v)", font_size=40, color=TINTA).move_to(DOWN * 2.3)
        self.play(Write(des), run_time=1.1)
        pol = tex(r"T_2(u,v)=\tfrac12\big(q(u+v)-q(u)-q(v)\big)", font_size=42)
        degradado(pol, [AMBAR, CORAL, MAGENTA])
        pol.move_to(DOWN * 3.6)
        self.play(TransformFromCopy(des, pol), run_time=1.1)
        iso = tex(r"\mathcal S_2(E)\cong Q(E)\quad(\mathrm{car}\,k\neq2)", font_size=38, color=CELESTE).move_to(DOWN * 4.8)
        self.play(FadeIn(iso, shift=UP * 0.2), run_time=0.7)
        self.wait(1.0)

        final = tex(r"T_2(u,v)=\tfrac12\big(q(u+v)-q(u)-q(v)\big)", font_size=48)
        degradado(final, [AMBAR, CORAL, MAGENTA, VIOLETA])
        self.cierre(final, "la forma cuadrática recupera entera su métrica simétrica")


class M10_Minkowski(ClipMetrica):
    indice = 10
    seccion = "Isotropía"
    titulo = "El cono de Minkowski"
    subtitulo = "q = x² + y² − t²"
    colores_titulo = [AMBAR, CORAL, MAGENTA, VIOLETA, CELESTE]

    def cuerpo(self):
        h = tex(r"H=\{x\in E:\ q(x)=0\}", font_size=46)
        degradado(h, DEG_CALIDO + [VIOLETA])
        h.move_to(UP * 4.35)
        self.play(Write(h), run_time=1.0)
        phi = ValueTracker(0.0)
        proy = proyector(UP * 0.3, 1.15, phi, elev=0.32)
        T = 2.2

        def cono():
            g = VGroup()
            angs = np.linspace(0, TAU, 28, endpoint=False)
            cols = color_gradient([AMBAR, CORAL, MAGENTA, VIOLETA, AZUL, CELESTE, TURQUESA, AMBAR], len(angs))
            for a, c in zip(angs, cols):
                g.add(Line(proy(-T * np.cos(a), -T * np.sin(a), -T), proy(T * np.cos(a), T * np.sin(a), T),
                           stroke_width=2, color=c).set_stroke(opacity=0.55))
            for z in (-T, -T / 2, T / 2, T):
                circ = VMobject().set_points_smoothly([proy(abs(z) * np.cos(a), abs(z) * np.sin(a), z) for a in np.linspace(0, TAU, 60)])
                g.add(circ.set_stroke(CIELO, 2.5, 0.8))
            ejes = VGroup(
                Arrow(proy(0, 0, -T - 0.5), proy(0, 0, T + 0.7), buff=0, stroke_width=3, color=TINTA),
                Arrow(proy(-T - 0.3, 0, 0), proy(T + 0.6, 0, 0), buff=0, stroke_width=2, color=GRIS),
                Arrow(proy(0, -T - 0.3, 0), proy(0, T + 0.6, 0), buff=0, stroke_width=2, color=GRIS),
            )
            labs = VGroup(tex("t", font_size=34, color=TINTA).move_to(proy(0, 0, T + 1.0)),
                          tex("x", font_size=30, color=GRIS).move_to(proy(T + 0.9, 0, 0)),
                          tex("y", font_size=30, color=GRIS).move_to(proy(0, T + 0.9, 0)))
            # línea de universo (tipo tiempo) y rayo de luz
            mundo = VMobject().set_points_smoothly([proy(0.5 * np.sin(1.3 * s), 0.4 * np.sin(0.8 * s), s) for s in np.linspace(-T, T, 40)])
            mundo.set_stroke(TURQUESA, 5)
            luz = Line(proy(0, 0, 0), proy(T * np.cos(0.7), T * np.sin(0.7), T), stroke_width=6, color=AMBAR)
            espacio = Arrow(proy(0, 0, 0), proy(1.9, -0.6, 0.5), buff=0, stroke_width=5, color=MAGENTA)
            return VGroup(g, ejes, labs, mundo, luz, espacio)

        c = always_redraw(cono)
        self.play(FadeIn(c), run_time=1.2)
        self.play(phi.animate.set_value(1.4), run_time=3.5, rate_func=smooth)
        ley = VGroup(
            tex(r"q<0\ \ \text{tipo tiempo}", font_size=34, color=TURQUESA),
            tex(r"q=0\ \ \text{luz (is\'otropo)}", font_size=34, color=AMBAR),
            tex(r"q>0\ \ \text{tipo espacio}", font_size=34, color=MAGENTA),
        ).arrange(DOWN, aligned_edge=LEFT, buff=0.22).move_to(DOWN * 3.5)
        self.play(LaggedStart(*[FadeIn(x, shift=RIGHT * 0.2) for x in ley], lag_ratio=0.3), phi.animate.set_value(2.4),
                  run_time=2.4)
        self.play(phi.animate.set_value(3.3), run_time=2.0)
        c.clear_updaters()
        sig = tex(r"(r_+,r_-)=(2,1),\qquad i=1", font_size=36, color=GRIS).move_to(DOWN * 5.15)
        self.play(FadeIn(sig), run_time=0.6)
        self.wait(0.8)

        final = tex(r"\dim V_{\max}=i(T_2)+\dim\mathrm{rad}\,T_2", font_size=52)
        degradado(final, DEG_CALIDO + [VIOLETA, CELESTE])
        self.cierre(final, "en el cono solo caben rectas: subespacios totalmente isótropos de dimensión 1")


class M11_Clasificacion(ClipMetrica):
    indice = 11
    seccion = "Clasificación"
    titulo = "Clasificar métricas"
    subtitulo = "en ℂ basta el rango; en ℝ, la signatura"
    colores_titulo = [TURQUESA, CELESTE, VIOLETA, MAGENTA, CORAL]

    def cuerpo(self):
        p = tex(r"e_i\ \longmapsto\ \frac{e_i}{\sqrt{|\lambda_i|}}", font_size=46)
        degradado(p, DEG_FRIO)
        p.move_to(UP * 4.3)
        self.play(Write(p), run_time=1.0)
        P = Plano(UP * 0.6, u=0.85, B=3.2)
        lam = ValueTracker(0)  # 0: diag(1/4, 1)  -> 1: diag(1,1)
        signo = ValueTracker(1)

        def curvas():
            s = lam.get_value()
            a = (1 - s) * 0.25 + s * 1.0
            b = (1 - s) * 1.0 + s * 1.0
            g = VGroup()
            for c, col in zip((1.0, 2.2, 4.0), (TURQUESA, CELESTE, VIOLETA)):
                if signo.get_value() > 0:
                    m = VMobject().set_points_smoothly([P.p(np.sqrt(c / a) * np.cos(t), np.sqrt(c / b) * np.sin(t))
                                                        for t in np.linspace(0, TAU, 90)])
                    pts = [p for p in m.get_anchors()]
                    m.set_stroke(col, 4)
                    if max(abs(np.sqrt(c / a)), np.sqrt(c / b)) <= P.B:
                        g.add(m)
                else:
                    for sg in (1, -1):
                        um = np.arccosh(max(P.B / np.sqrt(c / a), 1.001))
                        g.add(VMobject().set_points_smoothly([P.p(sg * np.sqrt(c / a) * np.cosh(u), np.sqrt(c / b) * np.sinh(u))
                                                              for u in np.linspace(-um, um, 50)
                                                              if abs(np.sqrt(c / b) * np.sinh(u)) <= P.B]).set_stroke(col, 4))
                        um2 = np.arccosh(max(P.B / np.sqrt(c / b), 1.001))
                        g.add(VMobject().set_points_smoothly([P.p(np.sqrt(c / a) * np.sinh(u), sg * np.sqrt(c / b) * np.cosh(u))
                                                              for u in np.linspace(-um2, um2, 50)
                                                              if abs(np.sqrt(c / a) * np.sinh(u)) <= P.B]).set_stroke(CORAL, 3))
            mat = tex(r"\begin{pmatrix}%.2f&0\\0&%s\end{pmatrix}" % (a, "1" if signo.get_value() > 0 else "-1"),
                      font_size=36, color=TINTA).move_to(DOWN * 3.0)
            return VGroup(g, mat)

        cv = always_redraw(curvas)
        self.play(FadeIn(P.marco()), FadeIn(P.rejilla(colores=(GRIS, GRIS), opacidad=0.12, ancho=1)), FadeIn(cv), run_time=1.0)
        self.play(lam.animate.set_value(1), run_time=2.4, rate_func=smooth)
        r1 = self.rotulo("reescalar la base ortogonal: los λᵢ pasan a ±1 o 0", pos=DOWN * 3.95, size=24, color=GRIS)
        self.play(FadeIn(r1), run_time=0.5)
        self.play(lam.animate.set_value(0), run_time=0.8)
        self.play(signo.animate.set_value(-1), run_time=0.1)
        self.play(lam.animate.set_value(1), run_time=2.2, rate_func=smooth)
        cv.clear_updaters()
        self.play(FadeOut(r1), run_time=0.3)
        R = tex(r"\mathbb R:\ \ \mathrm{diag}(1,\dots,1,-1,\dots,-1,0,\dots,0)", font_size=36, color=CELESTE).move_to(DOWN * 3.95)
        C = tex(r"\mathbb C:\ \ \mathrm{diag}(1,\dots,1,0,\dots,0)", font_size=36, color=MAGENTA).move_to(DOWN * 4.85)
        self.play(Write(R), run_time=1.0)
        self.play(Write(C), run_time=0.9)
        ii = tex(r"y\mapsto i\,y:\ \ x^2-y^2\ \sim\ x^2+y^2", font_size=34, color=GRIS).move_to(DOWN * 5.7)
        self.play(FadeIn(ii), run_time=0.6)
        self.wait(1.0)

        final = tex(r"\mathbb C:\ \text{rango}\qquad \mathbb R:\ (r_+,\,r_-)", font_size=54)
        degradado(final, [MAGENTA, VIOLETA, CELESTE, TURQUESA])
        self.cierre(final, "los invariantes que deciden si dos métricas son equivalentes")
