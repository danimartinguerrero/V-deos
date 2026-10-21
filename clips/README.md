# Clips verticales estilo 3Blue1Brown

Quince clips de unos 30 s en formato TikTok (1080×1920, 60 fps, sin voz), hechos con
[Manim Community](https://www.manim.community/) a partir de los PDFs del repositorio.
Los vídeos ya renderizados están en [`../videos/`](../videos/).

| Serie | Clip | Contenido |
|---|---|---|
| EDO lineales | `EDO1_Linealidad` | L lineal, y = y_h + y_p, ker L ≅ ℝⁿ (ejemplo y'' + y = 0), wronskiano |
| | `EDO2_Oscilador` | Ansatz e^{λx}, ecuación característica, raíces del oscilador amortiguado al variar ν |
| | `EDO3_RaicesMultiples` | Lema (D−λ)(e^{λx}g) = e^{λx}g', base x^j e^{λx}, amortiguamiento crítico |
| | `EDO4_VariacionConstantes` | Ansatz k_i(x), sistema W k' = b, ejemplo y'' + ω²y = b, núcleo de Green |
| Función de Green | `Green1_Impulsos` | Fuente como suma de deltas, L G = δ, superposición de respuestas |
| | `Green2_SaltoCoulomb` | Salto en ∂ⁿ⁻¹G, causalidad, Green = variación de constantes, Coulomb |
| Instrumentación | `Instr1_AO` | v_out = A(v₊ − v₋), saturación, AO ideal y reglas (R1), (R2) |
| | `Instr2_InversorNoInversor` | Inversor (−R₂/R₁ = −10) y no inversor (1 + R₂/R₁ = +11) con formas de onda |
| | `Instr3_ImpedanciaLaplace` | Fasores, derivar = multiplicar por jω, Z_R, Z_C, Z_L, transformada de Laplace |
| | `Instr4_FiltroPasoBajo` | H(s) = −Z₂/Z₁, R_F ∥ C, diagrama de Bode con barrido en frecuencia |
| | `Instr5_GBW` | Polo dominante, producto ganancia × ancho de banda, slew rate |
| Termodinámica I (T1) | `Termo1_Sistemas` | Micro vs. macro, gas en un pistón, sistemas aislado/cerrado/abierto |
| | `Termo2_LeyCero` | Relajación, estacionario ≠ equilibrio, ley cero, escala Kelvin |
| | `Termo3_EcuacionEstado` | f(p,V,T) = 0, superficie pV = nRT, funciones de estado, Van der Waals |
| | `Termo4_Coeficientes` | α, κ_T, β, relación cíclica, dV/V = α dT − κ_T dp, mercurio a V constante |

## Cómo volver a renderizar

```bash
python3 -m venv /opt/mvenv && /opt/mvenv/bin/pip install manim "pillow<11.3"
# además: LaTeX (texlive-latex-extra, texlive-science, dvisvgm), libpango1.0-dev y fonts-cmu
./render_todo.sh                       # los 15 clips, en ../videos/
PREVIEW=1 /opt/mvenv/bin/manim render edo.py EDO2_Oscilador   # borrador rápido 360×640
```

`estilo.py` contiene el formato vertical, la paleta (azules dominantes con acentos de toda la gama),
el fondo degradado, la cabecera con barra de progreso, la portada y la tarjeta final.
