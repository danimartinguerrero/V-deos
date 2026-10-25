"""Tomas calculadas del quinto edit (electrostática, temas 1-3).

Motor propio de campos:
  * cargas puntuales (analítico) o conductores (ecuación de Laplace/Poisson en diferencias finitas,
    factorizada una vez con splu cuando la geometría no cambia);
  * equipotenciales de grosor constante en píxeles: |φk − round(φk)| / |∇(φk)|;
  * líneas de campo integradas con RK2 desde semillas repartidas según el flujo, con pulsos que
    viajan a lo largo de ellas;
  * modelo de ruptura dieléctrica (DBM): la descarga crece con probabilidad ∝ |∇φ|^η.

Uso:  python numerico5.py SALIDA_DIR [toma ...]
"""

import sys
from pathlib import Path

import numpy as np
from scipy import ndimage, sparse
from scipy.sparse.linalg import splu, spsolve

from numerico import FPS, escribir, suave, vineta

TAU = 2 * np.pi
W2, H2 = 540, 960
POS = np.array([1.0, 0.36, 0.62])     # potencial positivo: magenta
NEG = np.array([0.25, 0.75, 1.0])     # potencial negativo: cian
LINEA = np.array([0.92, 0.95, 1.0])
METAL = np.array([0.55, 0.6, 0.7])


# ---------------------------------------------------------------------------
# utilidades geométricas
# ---------------------------------------------------------------------------
def malla(ancho, w=W2, h=H2):
    x = (np.arange(w) - w / 2 + 0.5) / w * ancho
    y = -(np.arange(h) - h / 2 + 0.5) / w * ancho
    return np.meshgrid(x, y)


def a_pixel(p, ancho, w=W2, h=H2):
    p = np.atleast_2d(p)
    return np.c_[p[:, 0] / ancho * w + w / 2 - 0.5, -p[:, 1] / ancho * w + h / 2 - 0.5]


# ---------------------------------------------------------------------------
# cargas puntuales
# ---------------------------------------------------------------------------
def potencial_cargas(X, Y, cargas, suav=0.02):
    phi = np.zeros_like(X)
    for q, x0, y0 in cargas:
        phi += q / np.sqrt((X - x0) ** 2 + (Y - y0) ** 2 + suav ** 2)
    return phi


def campo_cargas(P, cargas):
    E = np.zeros_like(P)
    for q, x0, y0 in cargas:
        d = P - np.array([x0, y0])
        r3 = (np.sum(d * d, 1) + 1e-6) ** 1.5
        E += q * d / r3[:, None]
    return E


def lineas_cargas(cargas, ancho, n_por_q=14, paso=None, nmax=2600, giro=0.0, extra_semillas=None):
    """Líneas desde las cargas positivas (y entrando en las negativas desde fuera si sobra flujo)."""
    paso = paso or ancho / W2 * 1.2
    semillas, signos = [], []
    for q, x0, y0 in cargas:
        if q > 0:
            m = max(int(round(n_por_q * q)), 4)
            ang = np.linspace(0, TAU, m, endpoint=False) + giro + 0.13
            semillas += [np.c_[x0 + 0.03 * np.cos(ang), y0 + 0.03 * np.sin(ang)]]
            signos += [1] * m
    neto = sum(q for q, _, _ in cargas)
    if neto < -0.01:
        for q, x0, y0 in cargas:
            if q < 0:
                m = max(int(round(n_por_q * -q)), 4)
                ang = np.linspace(0, TAU, m, endpoint=False) + giro + 0.13
                semillas += [np.c_[x0 + 0.03 * np.cos(ang), y0 + 0.03 * np.sin(ang)]]
                signos += [-1] * m
    if extra_semillas is not None:
        semillas.append(extra_semillas[0]); signos += list(extra_semillas[1])
    P = np.vstack(semillas)
    s = np.array(signos, dtype=float)[:, None]
    lim = np.array([ancho / 2 * 1.05, ancho * H2 / W2 / 2 * 1.05])

    def E(P):
        return campo_cargas(P, cargas)

    def parar(P):
        fuera = np.any(np.abs(P) > lim, 1)
        cerca = np.zeros(len(P), bool)
        for q, x0, y0 in cargas:
            cerca |= np.hypot(P[:, 0] - x0, P[:, 1] - y0) < 0.025
        return fuera | cerca

    return integrar(P, lambda P: E(P) * s, parar, paso, nmax)


def integrar(P, E, parar, paso, nmax):
    """RK2 vectorizado sobre todas las semillas. Devuelve una lista de polilíneas (coordenadas físicas)."""
    vivos = np.ones(len(P), bool)
    tray = [P.copy()]
    activos_hist = [vivos.copy()]
    for k in range(nmax):
        e = E(P)
        e /= np.linalg.norm(e, axis=1, keepdims=True) + 1e-12
        Pm = P + 0.5 * paso * e
        e2 = E(Pm)
        e2 /= np.linalg.norm(e2, axis=1, keepdims=True) + 1e-12
        P = np.where(vivos[:, None], P + paso * e2, P)
        if k > 3:
            vivos &= ~parar(P)
        tray.append(P.copy())
        activos_hist.append(vivos.copy())
        if not vivos.any():
            break
    T = np.array(tray)              # (pasos, n, 2)
    A = np.array(activos_hist)
    lineas = []
    for i in range(T.shape[1]):
        n = A[:, i].sum() + 1
        lineas.append(T[:n, i])
    return lineas


# ---------------------------------------------------------------------------
# Laplace / Poisson con conductores
# ---------------------------------------------------------------------------
class Laplace:
    """Rejilla con nodos fijos (conductores y borde). La matriz se factoriza una sola vez."""

    def __init__(self, fijo, w, h):
        self.w, self.h = w, h
        self.fijo = fijo.copy()
        self.fijo[0, :] = self.fijo[-1, :] = self.fijo[:, 0] = self.fijo[:, -1] = True
        libres = ~self.fijo
        self.idx = -np.ones((h, w), int)
        self.idx[libres] = np.arange(libres.sum())
        n = libres.sum()
        filas, cols, vals = [], [], []
        ys, xs = np.nonzero(libres)
        i0 = self.idx[ys, xs]
        filas.append(i0); cols.append(i0); vals.append(np.full(n, -4.0))
        self.vecinos = []
        for dy, dx in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            yy, xx = ys + dy, xs + dx
            j = self.idx[yy, xx]
            ok = j >= 0
            filas.append(i0[ok]); cols.append(j[ok]); vals.append(np.ones(ok.sum()))
            self.vecinos.append((~ok, i0[~ok], yy[~ok], xx[~ok]))
        A = sparse.csc_matrix((np.concatenate(vals), (np.concatenate(filas), np.concatenate(cols))), shape=(n, n))
        self.lu = splu(A)
        self.n = n

    def resolver(self, valores, rho=None):
        b = np.zeros(self.n)
        for _, i0, yy, xx in self.vecinos:
            np.add.at(b, i0, -valores[yy, xx])
        if rho is not None:
            b -= rho[~self.fijo]
        phi = valores.copy()
        phi[~self.fijo] = self.lu.solve(b)
        return phi


def gradiente(phi, ancho, w, h):
    d = ancho / w
    gy, gx = np.gradient(phi, d)
    return -gx, gy  # Ex, Ey (y física hacia arriba)


def lineas_rejilla(phi, fijo, ancho, n=60, nmax=3000, sentido=1.0, semillas_borde=True):
    """Líneas de campo para una solución en rejilla. Semillas en las fronteras de los nodos fijos
    (conductores y borde), repartidas según el flujo saliente."""
    h, w = phi.shape
    Ex, Ey = gradiente(phi, ancho, w, h)
    Ex, Ey = Ex * sentido, Ey * sentido
    mag = np.hypot(Ex, Ey) + 1e-12
    # frontera de los conductores: nodos libres pegados a un nodo fijo
    borde_c = (~fijo) & ndimage.binary_dilation(fijo & ~_marco(h, w), iterations=1)
    cand = [borde_c]
    if semillas_borde:
        b = np.zeros_like(fijo); b[2, :] = b[-3, :] = b[:, 2] = b[:, -3] = True
        cand.append(b)
    mask = np.zeros_like(fijo)
    for c in cand:
        mask |= c
    ys, xs = np.nonzero(mask)
    # flujo saliente: el campo apunta lejos del nodo fijo vecino / hacia dentro desde el borde
    nx = np.zeros(len(xs)); ny = np.zeros(len(xs))
    f = fijo.astype(float)
    gxf = ndimage.sobel(f, 1); gyf = -ndimage.sobel(f, 0)
    nx = -gxf[ys, xs]; ny = -gyf[ys, xs]
    en_marco = (ys <= 2) | (ys >= h - 3) | (xs <= 2) | (xs >= w - 3)
    nx[en_marco] = np.where(xs[en_marco] <= 2, 1, np.where(xs[en_marco] >= w - 3, -1, 0))
    ny[en_marco] = np.where(ys[en_marco] <= 2, -1, np.where(ys[en_marco] >= h - 3, 1, 0))
    nn = np.hypot(nx, ny) + 1e-12
    flujo = np.clip((Ex[ys, xs] * nx + Ey[ys, xs] * ny) / nn, 0, None)
    if flujo.sum() <= 0:
        return []
    cum = np.cumsum(flujo); cum /= cum[-1]
    elegidos = np.searchsorted(cum, (np.arange(n) + 0.5) / n)
    xp, yp = xs[elegidos].astype(float), ys[elegidos].astype(float)
    P = np.c_[(xp - w / 2 + 0.5) / w * ancho, -(yp - h / 2 + 0.5) / w * ancho]
    exn, eyn = Ex / mag, Ey / mag

    def E(P):
        px = P[:, 0] / ancho * w + w / 2 - 0.5
        py = -P[:, 1] / ancho * w + h / 2 - 0.5
        a = ndimage.map_coordinates(exn, [py, px], order=1, mode="nearest")
        b = ndimage.map_coordinates(eyn, [py, px], order=1, mode="nearest")
        return np.c_[a, b]

    def parar(P):
        px = np.clip(np.round(P[:, 0] / ancho * w + w / 2 - 0.5).astype(int), 0, w - 1)
        py = np.clip(np.round(-P[:, 1] / ancho * w + h / 2 - 0.5).astype(int), 0, h - 1)
        return fijo[py, px] | (px <= 1) | (px >= w - 2) | (py <= 1) | (py >= h - 2)

    return integrar(P, E, parar, ancho / w * 0.9, nmax)


def _marco(h, w):
    m = np.zeros((h, w), bool)
    m[0, :] = m[-1, :] = m[:, 0] = m[:, -1] = True
    return m


# ---------------------------------------------------------------------------
# render
# ---------------------------------------------------------------------------
def equipotenciales(phi, ancho, k=6.0, grosor=0.9, w=W2):
    v = phi * k
    gy, gx = np.gradient(v)
    g = np.hypot(gx, gy) + 1e-9
    d = np.abs(v - np.round(v)) / g
    return np.exp(-(d / grosor) ** 2) * np.clip(1.5 - g * 0.15, 0, 1)


def raster_lineas(lineas, ancho, t, vel=0.9, w=W2, h=H2, pulso=True):
    acc = np.zeros(h * w)
    acc_p = np.zeros(h * w)
    for L in lineas:
        if len(L) < 3:
            continue
        seg = np.diff(L, axis=0)
        s = np.concatenate([[0], np.cumsum(np.hypot(seg[:, 0], seg[:, 1]))])
        # remuestreo a medio píxel
        npts = int(s[-1] / (ancho / w) * 2) + 2
        ss = np.linspace(0, s[-1], npts)
        x = np.interp(ss, s, L[:, 0]); y = np.interp(ss, s, L[:, 1])
        px = (x / ancho * w + w / 2 - 0.5).astype(int)
        py = (-y / ancho * w + h / 2 - 0.5).astype(int)
        ok = (px >= 0) & (px < w) & (py >= 0) & (py < h)
        lin = py[ok] * w + px[ok]
        np.add.at(acc, lin, 0.5)
        if pulso:
            fase = (ss[ok] / (ancho * 0.18) - t * vel * 3) % 1
            np.add.at(acc_p, lin, 0.5 * np.exp(-((fase - 0.5) / 0.06) ** 2))
    return np.minimum(acc.reshape(h, w), 1.5), acc_p.reshape(h, w)


def componer(phi, ancho, lineas, t, fijo=None, k=6.0, escala_phi=1.0, extra=None, brillo_sup=None):
    h, w = phi.shape
    img = np.zeros((h, w, 3))
    # tinte suave del potencial
    p = np.tanh(phi * escala_phi)
    img += np.clip(p, 0, None)[..., None] * POS * 0.10 + np.clip(-p, 0, None)[..., None] * NEG * 0.10
    eq = equipotenciales(phi, ancho, k)
    col_eq = np.where((phi > 0)[..., None], POS, NEG)
    img += eq[..., None] * col_eq * 0.55
    lin, pul = raster_lineas(lineas, ancho, t)
    lin = ndimage.gaussian_filter(lin, 0.6)
    img += lin[..., None] * LINEA * 0.75
    glow = ndimage.gaussian_filter(pul, 1.2) * 2.2 + ndimage.gaussian_filter(pul, 5) * 3
    img += glow[..., None] * np.array([0.7, 0.9, 1.0])
    if fijo is not None:
        borde = fijo & ~ndimage.binary_erosion(fijo, iterations=2)
        interior = fijo & ~borde
        img[interior] = img[interior] * 0.15 + METAL * 0.11
        img[borde] = METAL * 0.65
        if brillo_sup is not None:
            g = ndimage.gaussian_filter(brillo_sup, 3) * 3 + ndimage.gaussian_filter(brillo_sup, 10) * 4
            img += g[..., None] * np.array([1.0, 0.85, 0.65])
    if extra is not None:
        img += extra
    img = 1 - np.exp(-img * 1.4)
    return img * vineta(w, h, 0.35)[..., None]


def glow_cargas(cargas, ancho, w=W2, h=H2, r=0.07):
    X, Y = malla(ancho, w, h)
    out = np.zeros((h, w, 3))
    for q, x0, y0 in cargas:
        d2 = (X - x0) ** 2 + (Y - y0) ** 2
        c = POS if q > 0 else NEG
        out += (np.exp(-d2 / (r * r * 0.25)) * 3 + np.exp(-d2 / (r * r * 4)) * 0.6)[..., None] * c * min(abs(q), 2)
        out += np.exp(-d2 / (r * r * 0.05))[..., None] * 3
    return out


def densidad_superficial(phi, fijo, ancho):
    """|E| justo fuera de los conductores (∝ σ), para iluminar la superficie."""
    h, w = phi.shape
    Ex, Ey = gradiente(phi, ancho, w, h)
    mag = np.hypot(Ex, Ey)
    frontera = (~fijo) & ndimage.binary_dilation(fijo & ~_marco(h, w))
    out = np.zeros_like(phi)
    out[frontera] = mag[frontera]
    return out / (np.percentile(mag[frontera], 99) + 1e-9) if frontera.any() else out


# ---------------------------------------------------------------------------
# tomas con cargas puntuales
# ---------------------------------------------------------------------------
def dipolo(ruta, seg=5.0):
    n = int(seg * FPS)
    A = 4.0
    X, Y = malla(A)

    def f(i):
        s = i / n
        a = PI2 * 0.5 + 1.2 * suave(s)
        d = 0.45
        cargas = [(1, d * np.cos(a), d * np.sin(a)), (-1, -d * np.cos(a), -d * np.sin(a))]
        phi = potencial_cargas(X, Y, cargas)
        L = lineas_cargas(cargas, A, n_por_q=22, giro=a)
        return componer(phi, A, L, i / FPS, k=3.0, escala_phi=0.6, extra=glow_cargas(cargas, A))

    escribir(ruta, n, f, W2, H2)


def cuadrupolo(ruta, seg=5.0):
    n = int(seg * FPS)
    A = 4.4
    X, Y = malla(A)

    def f(i):
        s = i / n
        a = 0.4 * s * TAU / 4
        r = 0.6
        cargas = [((-1) ** k, r * np.cos(a + k * TAU / 4), r * np.sin(a + k * TAU / 4)) for k in range(4)]
        phi = potencial_cargas(X, Y, cargas)
        L = lineas_cargas(cargas, A, n_por_q=16, giro=a)
        return componer(phi, A, L, i / FPS, k=3.5, escala_phi=0.6, extra=glow_cargas(cargas, A))

    escribir(ruta, n, f, W2, H2)


def iguales(ruta, seg=5.0):
    n = int(seg * FPS)
    A = 4.4
    X, Y = malla(A)

    def f(i):
        s = suave(i / n)
        d = 1.6 - 1.15 * s
        cargas = [(1, 0, d), (1, 0, -d)]
        phi = potencial_cargas(X, Y, cargas)
        L = lineas_cargas(cargas, A, n_por_q=20)
        return componer(phi, A, L, i / FPS, k=2.5, escala_phi=0.5, extra=glow_cargas(cargas, A))

    escribir(ruta, n, f, W2, H2)


def imagen(ruta, seg=5.0):
    """Carga frente a un plano conductor a tierra: método de imágenes; σ inducida en el plano."""
    n = int(seg * FPS)
    A = 4.4
    X, Y = malla(A)
    y_plano = -2.6

    def f(i):
        s = suave(i / n)
        hq = 2.4 - 1.6 * s
        qy = y_plano + hq
        cargas = [(1, 0.0, qy), (-1, 0.0, y_plano - hq)]
        phi = potencial_cargas(X, Y, cargas)
        L = lineas_cargas(cargas, A, n_por_q=26)
        L = [l[l[:, 1] >= y_plano] for l in L]
        fijo = Y < y_plano
        phi = np.where(fijo, 0, phi)
        xs = X[0]
        sigma = hq / (xs ** 2 + hq ** 2) ** 1.5
        sup = np.zeros_like(phi)
        fila = np.argmin(np.abs(Y[:, 0] - y_plano))
        sup[fila - 1, :] = sigma / sigma.max()
        return componer(phi, A, L, i / FPS, fijo=fijo, k=3.0, escala_phi=0.6,
                        extra=glow_cargas(cargas[:1], A), brillo_sup=sup)

    escribir(ruta, n, f, W2, H2)


def multipolo(ruta, seg=5.0):
    """Una distribución irregular vista cada vez desde más lejos: las líneas se vuelven radiales."""
    n = int(seg * FPS)
    rng = np.random.default_rng(11)
    base = [(1.0, 0.0, 0.0), (1.0, 0.5, 0.2), (-1.0, -0.4, 0.4), (1.0, -0.2, -0.5), (-0.5, 0.45, -0.45), (0.5, -0.6, -0.1)]

    def f(i):
        s = suave(i / n)
        A = 3.0 * np.exp(np.log(30.0) * s)
        X, Y = malla(A)
        phi = potencial_cargas(X, Y, base, suav=0.02 * A / 3)
        L = lineas_cargas(base, A, n_por_q=10, paso=A / W2 * 1.2, nmax=3000)
        k = 2.0 * (3.0 / A) ** 0.2
        return componer(phi, A, L, i / FPS, k=k, escala_phi=0.6 * A / 3, extra=glow_cargas(base, A, r=0.07 * A / 3))

    escribir(ruta, n, f, W2, H2)


PI2 = np.pi / 2


# ---------------------------------------------------------------------------
# tomas con conductores (Laplace)
# ---------------------------------------------------------------------------
WL, HL = 270, 480     # rejilla de cálculo (se reinterpola al render)


def _upsample(a):
    return ndimage.zoom(a, (H2 / a.shape[0], W2 / a.shape[1]), order=3)


def _up_mask(m):
    return ndimage.zoom(m.astype(float), (H2 / m.shape[0], W2 / m.shape[1]), order=1) > 0.5


def puntas(ruta, seg=5.0):
    """Conductor con forma de gota: la carga y el campo se acumulan en la punta."""
    n = int(seg * FPS)
    A = 4.0
    X, Y = malla(A, WL, HL)
    r = np.hypot(X, Y + 0.5)
    th = np.arctan2(Y + 0.5, X)
    gota = r < 0.7 * (1 - 0.92 * np.clip(np.sin(th), 0, 1) ** 12) + 0.02
    punta = (np.abs(X) < 0.03 + 0.25 * np.clip((0.95 - Y) / 1.2, 0, 1)) & (Y > -0.5) & (Y < 0.95)
    fijo = gota | punta
    lap = Laplace(fijo, WL, HL)
    val = np.where(fijo, 1.0, 0.0)
    phi = _upsample(lap.resolver(val))
    fijoU = _up_mask(fijo)
    phi[fijoU] = 1.0
    L = lineas_rejilla(phi, fijoU, A, n=80, semillas_borde=False)
    sup = densidad_superficial(phi, fijoU, A)

    def f(i):
        return componer(phi, A, L, i / FPS, fijo=fijoU, k=6, escala_phi=1.0, brillo_sup=sup * (0.7 + 0.3 * np.sin(i / FPS * 6) ** 2))

    escribir(ruta, n, f, W2, H2)


def faraday(ruta, seg=5.0):
    """Jaula: el campo exterior gira y el interior sigue en cero."""
    n = int(seg * FPS)
    A = 4.4
    X, Y = malla(A, WL, HL)
    r = np.hypot(X, Y)
    anillo = (r > 1.05) & (r < 1.2)
    rejas = anillo & (np.cos(np.arctan2(Y, X) * 18) > -0.9)   # jaula con huecos pequeños
    fijo = rejas.copy()
    lap = Laplace(fijo, WL, HL)
    marco = _marco(HL, WL)
    fijoU = _up_mask(fijo)

    def f(i):
        a = -np.pi / 2 + 0.9 * np.sin(TAU * i / n * 0.5)
        val = np.zeros((HL, WL))
        externo = -(np.cos(a) * X + np.sin(a) * Y) * 1.0
        val[marco] = externo[marco]
        val[fijo] = 0.0
        phi = _upsample(lap.resolver(val))
        phi[fijoU] = 0
        L = lineas_rejilla(phi, fijoU, A, n=46, semillas_borde=True)
        L = [l for l in L if np.hypot(*l[0]) > 1.1]
        L = [l[:np.argmax(np.hypot(l[:, 0], l[:, 1]) < 1.02)] if (np.hypot(l[:, 0], l[:, 1]) < 1.02).any() else l for l in L]
        return componer(phi, A, L, i / FPS, fijo=fijoU, k=2.6, escala_phi=0.6, brillo_sup=densidad_superficial(phi, fijoU, A) * 0.6)

    escribir(ruta, n, f, W2, H2)


def condensador(ruta, seg=5.0):
    """Placas paralelas finitas cargándose: campo uniforme dentro, bordes curvados fuera."""
    n = int(seg * FPS)
    A = 4.4
    X, Y = malla(A, WL, HL)
    placa1 = (np.abs(Y - 0.55) < 0.05) & (np.abs(X) < 1.4)
    placa2 = (np.abs(Y + 0.55) < 0.05) & (np.abs(X) < 1.4)
    fijo = placa1 | placa2
    lap = Laplace(fijo, WL, HL)
    val = np.where(placa1, 1.0, np.where(placa2, -1.0, 0.0))
    phi0 = _upsample(lap.resolver(val))
    fijoU = _up_mask(fijo)
    L = lineas_rejilla(phi0, fijoU, A, n=60, semillas_borde=False)
    sup = densidad_superficial(phi0, fijoU, A)

    def f(i):
        v = 0.15 + 0.85 * suave(min(i / n * 1.6, 1))
        phi = phi0 * v
        Lv = L
        img = componer(phi, A, Lv, i / FPS, fijo=fijoU, k=4, escala_phi=1.0, brillo_sup=sup * v)
        return img

    escribir(ruta, n, f, W2, H2)


def cavidad(ruta, seg=5.0):
    """Carga dentro de una cavidad: al moverla dentro, el campo exterior no cambia."""
    n = int(seg * FPS)
    A = 4.4
    w, h = 180, 320
    X, Y = malla(A, w, h)
    r = np.hypot(X, Y)
    th = np.arctan2(Y, X)
    ext = 1.45 + 0.12 * np.cos(3 * th)
    cav = 0.95 + 0.1 * np.sin(2 * th)
    cascara = (r < ext) & (r > cav)
    cascU = _up_mask(cascara)
    Xu, Yu = malla(A)

    def f(i):
        s = i / n
        cx, cy = 0.35 * np.cos(TAU * s), 0.3 * np.sin(TAU * s * 2)
        carga = np.hypot(X - cx, Y - cy) < 0.09
        fijo = cascara | carga
        val = np.where(cascara, 0.55, np.where(carga, 3.0, 0.0))
        phi = spsolve_laplace(fijo, val)
        phiU = _upsample(phi)
        cargaU = np.hypot(Xu - cx, Yu - cy) < 0.09
        fijoU = cascU | cargaU
        phiU[cascU] = 0.55
        L = lineas_rejilla(phiU, fijoU, A, n=70, semillas_borde=False)
        sup = densidad_superficial(phiU, cascU, A)
        extra = glow_cargas([(1.5, cx, cy)], A)
        return componer(phiU, A, L, i / FPS, fijo=cascU, k=4.0, escala_phi=0.5, extra=extra, brillo_sup=sup * 0.7)

    escribir(ruta, n, f, W2, H2)


def spsolve_laplace(fijo, val):
    h, w = fijo.shape
    lap = Laplace(fijo, w, h)
    return lap.resolver(val)


def sistema(ruta, seg=5.0):
    """Tres conductores cuyos potenciales van rotando: coeficientes de influencia a la vista."""
    n = int(seg * FPS)
    A = 4.4
    X, Y = malla(A, WL, HL)
    cs = [(0.0, 1.25, 0.55), (-0.95, -0.7, 0.42), (1.0, -0.85, 0.32)]
    fijos = [np.hypot(X - x, Y - y) < r for x, y, r in cs]
    fijo = fijos[0] | fijos[1] | fijos[2]
    lap = Laplace(fijo, WL, HL)
    fijoU = _up_mask(fijo)
    Xu, Yu = malla(A)
    fijosU = [np.hypot(Xu - x, Yu - y) < r for x, y, r in cs]

    def f(i):
        t = TAU * i / n
        V = [np.cos(t), np.cos(t + TAU / 3), np.cos(t + 2 * TAU / 3)]
        val = np.zeros((HL, WL))
        for m, v in zip(fijos, V):
            val[m] = v
        phi = _upsample(lap.resolver(val))
        for m, v in zip(fijosU, V):
            phi[m] = v
        L = lineas_rejilla(phi, fijoU, A, n=60, semillas_borde=True)
        return componer(phi, A, L, i / FPS, fijo=fijoU, k=5.0, escala_phi=1.0, brillo_sup=densidad_superficial(phi, fijoU, A))

    escribir(ruta, n, f, W2, H2)


def esferas_hilo(ruta, seg=5.0):
    """Dos esferas unidas por un hilo (mismo potencial): σ1 R1 = σ2 R2, la pequeña brilla más."""
    n = int(seg * FPS)
    A = 4.4
    X, Y = malla(A, WL, HL)
    s1 = np.hypot(X, Y - 1.1) < 0.75
    s2 = np.hypot(X, Y + 1.55) < 0.22
    hilo = (np.abs(X) < 0.025) & (Y < 0.4) & (Y > -1.4)
    fijo = s1 | s2 | hilo
    lap = Laplace(fijo, WL, HL)
    phi = _upsample(lap.resolver(np.where(fijo, 1.0, 0.0)))
    fijoU = _up_mask(fijo)
    phi[fijoU] = 1.0
    L = lineas_rejilla(phi, fijoU, A, n=90, semillas_borde=False)
    sup = densidad_superficial(phi, fijoU, A)

    def f(i):
        return componer(phi, A, L, i / FPS, fijo=fijoU, k=5, escala_phi=1.0, brillo_sup=sup * (0.8 + 0.2 * np.sin(i / FPS * 5)))

    escribir(ruta, n, f, W2, H2)


def ruptura(ruta, seg=5.0):
    """Ruptura dieléctrica (modelo DBM): la descarga crece desde el electrodo hacia tierra."""
    n = int(seg * FPS)
    w, h = 135, 240
    W3 = 3 * w
    rng = np.random.default_rng(17)
    arbol = np.zeros((h, W3), bool)
    c0 = W3 // 2
    arbol[0:22, c0 - 1:c0 + 2] = True                       # varilla del electrodo
    padre = {}
    orden = np.full((h, W3), -1)
    tierra = np.zeros((h, W3), bool); tierra[-2:, :] = True
    rampa = np.repeat((1 - np.arange(h) / (h - 1))[:, None], W3, 1)
    marco = _marco(h, W3)
    prohibido = marco.copy(); prohibido[:22, :] = True
    paso, eta = 0, 2.0
    while not arbol[-5, :].any() and paso < 1400:
        fijo = arbol | tierra
        val = np.where(arbol, 1.0, 0.0)
        val[marco] = rampa[marco]
        val[tierra] = 0.0
        phi = spsolve_laplace(fijo, val)
        front = (~fijo) & ~prohibido & ndimage.binary_dilation(arbol, structure=np.ones((3, 3)))
        ys, xs = np.nonzero(front)
        p = np.clip(1 - phi[ys, xs], 1e-9, None) ** eta
        p /= p.sum()
        for k in rng.choice(len(ys), size=min(4, len(ys)), replace=False, p=p):
            y, x = ys[k], xs[k]
            vec = arbol[max(y - 1, 0):y + 2, max(x - 1, 0):x + 2]
            vy, vx = np.argwhere(vec)[0]
            padre[(y, x)] = (max(y - 1, 0) + vy, max(x - 1, 0) + vx)
            arbol[y, x] = True
            paso += 1
            orden[y, x] = paso
    total = paso
    arbol, orden = arbol[:, w:2 * w], orden[:, w:2 * w]
    padre = {(y, x - w): (py, px - w) for (y, x), (py, px) in padre.items()}
    y, x = np.argwhere(orden >= 0)[np.argmax(np.argwhere(orden >= 0)[:, 0])]
    principal = np.zeros((h, w), bool)
    principal[:22, w // 2 - 1:w // 2 + 2] = True
    while (y, x) in padre:
        principal[y, x] = True
        y, x = padre[(y, x)]
        if not (0 <= x < w):
            break
    varilla = np.zeros((h, w), bool); varilla[:22, w // 2 - 1:w // 2 + 2] = True

    def f(i):
        s = i / n
        img = np.zeros((h * 4, w * 4, 3))
        if s < 0.7:
            vis = (orden >= 0) & (orden <= total * s / 0.7)
            I = vis.astype(float) * 0.7 + varilla * 0.6
            flash = 0.0
        else:
            k = (s - 0.7) / 0.3
            par = np.exp(-k * 5) * (1 + 0.6 * np.sin(k * 45) ** 2)
            I = (orden >= 0) * 0.4 + principal * (1.5 + 3 * par)
            flash = 0.3 * par
        I = ndimage.zoom(I, 4, order=1)
        nucleo = ndimage.gaussian_filter(I, 1.0)
        halo = ndimage.gaussian_filter(I, 7) * 2.5 + ndimage.gaussian_filter(I, 26) * 7
        img = (1 - np.exp(-nucleo[..., None] * 2.2)) + (1 - np.exp(-halo[..., None] * np.array([0.5, 0.55, 1.2])))
        img = img + flash * np.array([0.45, 0.5, 0.9])
        img[-10:] += np.array([0.25, 0.25, 0.28])      # tierra
        return np.clip(img, 0, 1) * vineta(w * 4, h * 4, 0.35)[..., None]

    escribir(ruta, n, f, w * 4, h * 4)


TOMAS = {
    "dipolo": dipolo, "cuadrupolo": cuadrupolo, "iguales": iguales, "imagen": imagen, "multipolo": multipolo,
    "puntas": puntas, "faraday": faraday, "condensador": condensador, "cavidad": cavidad, "sistema": sistema,
    "esferas_hilo": esferas_hilo, "ruptura": ruptura,
}

if __name__ == "__main__":
    salida = Path(sys.argv[1])
    salida.mkdir(parents=True, exist_ok=True)
    for nom in sys.argv[2:] or list(TOMAS):
        TOMAS[nom](salida / f"{nom}.mp4")
        print("OK", nom, flush=True)
