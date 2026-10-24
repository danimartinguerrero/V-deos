"""Tomas calculadas del tercer edit (solo óptica). Simulaciones físicas con aspecto
fotográfico; no son fotografías.

Uso:  python numerico3.py SALIDA_DIR [toma1 toma2 ...]
"""

import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

from numerico import FPS, escribir, exponer, hsv_rgb, longitud_onda_rgb, rejilla, suave, vineta

TAU = 2 * np.pi
W2, H2 = 540, 960  # resolución de cálculo (se escala a 1080x1920 con lanczos)
WLS = np.linspace(400, 700, 31)
CMF = longitud_onda_rgb(WLS)
CMF = CMF / CMF.sum(0)


def espectral(R):
    """R[..., λ] -> RGB integrando sobre el espectro visible."""
    return R @ CMF


def niebla(rng, w=W2, h=H2):
    capas = [ndimage.gaussian_filter(rng.normal(0, 1, (h * 2, w * 2)), s) for s in (40, 14)]
    return [(c - c.min()) / np.ptp(c) for c in capas]


def dist_segmento(X, Y, a, b):
    ax, ay = a; bx, by = b
    dx, dy = bx - ax, by - ay
    t = np.clip(((X - ax) * dx + (Y - ay) * dy) / (dx * dx + dy * dy + 1e-9), 0, 1)
    return np.hypot(X - ax - t * dx, Y - ay - t * dy)


# ---------------------------------------------------------------------------
# láseres
# ---------------------------------------------------------------------------
def laser_show(ruta, variante=0, seg=4.0):
    """Haces láser atravesando humo: solo se ven por la luz que esparce la niebla."""
    w, h = W2, H2
    n = int(seg * FPS)
    rng = np.random.default_rng(40 + variante)
    capas = niebla(rng)
    X, Y = np.meshgrid(np.arange(w), np.arange(h))
    polvo = np.zeros((h, w))
    polvo.flat[rng.integers(0, w * h, 2500)] = rng.uniform(0.3, 1, 2500)

    def f(i):
        t = i / FPS
        s = i / n
        dens = 0.08 + 1.6 * (0.6 * capas[0][int(t * 18) % h: int(t * 18) % h + h, 40: 40 + w]
                              + 0.4 * capas[1][int(t * 40) % h: int(t * 40) % h + h, 80: 80 + w])
        img = np.zeros((h, w, 3))
        haces = []
        if variante == 0:      # abanico verde que barre desde abajo
            o = (w / 2, h + 10)
            for k in range(9):
                a = -np.pi / 2 + (k - 4) * 0.13 + 0.35 * np.sin(TAU * 0.35 * t + k * 0.4)
                haces.append((o, (o[0] + 2000 * np.cos(a), o[1] + 2000 * np.sin(a)), (0.25, 1.0, 0.3), 2.2))
        elif variante == 1:    # rojo, verde y azul cruzándose desde los lados
            for k, (c, lado) in enumerate((((1.0, 0.12, 0.08), -1), ((0.2, 1.0, 0.3), 1), ((0.25, 0.4, 1.0), -1),
                                           ((1.0, 0.12, 0.08), 1), ((0.2, 1.0, 0.3), -1))):
                o = (w / 2 + lado * (w / 2 + 10), h * (0.25 + 0.15 * k))
                a = (np.pi if lado > 0 else 0) + lado * (0.35 * np.sin(TAU * 0.25 * t + k) + 0.15 * (k - 2))
                haces.append((o, (o[0] + 2000 * np.cos(a), o[1] - 2000 * np.sin(a) * 0.5), c, 2.0))
        else:                  # un haz que rebota entre dos espejos
            pts = [(30.0, 40.0)]
            ang = 0.32 + 0.06 * np.sin(TAU * 0.3 * t)
            x, y, d = 30.0, 40.0, 1
            while y < h + 50 and len(pts) < 40:
                x2 = w - 30 if d > 0 else 30
                y2 = y + abs(x2 - x) * np.tan(ang)
                pts.append((x2, y2)); x, y, d = x2, y2, -d
            corte = int(len(pts) * min(1, 0.15 + s * 1.3)) + 1
            for a_, b_ in zip(pts[:corte - 1], pts[1:corte]):
                haces.append((a_, b_, (1.0, 0.1, 0.06), 2.0))
            for p in pts[1:corte]:
                img += np.exp(-((X - p[0]) ** 2 + (Y - p[1]) ** 2) / 60)[..., None] * np.array([1, 0.4, 0.3]) * 1.5
        for a_, b_, c, ancho in haces:
            d = dist_segmento(X, Y, a_, b_)
            nucleo = np.exp(-(d / ancho) ** 2)
            halo = np.exp(-(d / (ancho * 9)) ** 2)
            I = (nucleo * 1.6 + halo * 0.9) * dens ** 1.6 + nucleo * polvo * 4 + np.exp(-(d / (ancho * 30)) ** 2) * 0.12 * dens
            img += I[..., None] * np.array(c)
        img = 1 - np.exp(-img * 1.3)
        return img * vineta(w, h, 0.45)[..., None]

    escribir(ruta, n, f, w, h)


def speckle(ruta, seg=4.0):
    """Moteado de un láser rojo sobre una superficie rugosa: hierve al moverse."""
    n = int(seg * FPS)
    N = 1024
    rng = np.random.default_rng(41)
    fase = rng.uniform(0, TAU, (N, N))
    fy, fx = np.meshgrid(np.fft.fftfreq(N), np.fft.fftfreq(N), indexing="ij")
    X, Y = rejilla(W2, H2, 1.0)
    haz = np.exp(-(X ** 2 + Y ** 2) / 0.18)

    def f(i):
        s = i / n
        cx, cy = 0.02 * np.cos(TAU * s * 0.4), 0.015 * np.sin(TAU * s * 0.3)
        ap = (np.hypot(fx - cx, fy - cy) < 0.035).astype(float)
        E = np.fft.ifft2(ap * np.exp(1j * (fase + 2.5 * s * fx * 40)))
        I = np.abs(E[:H2, :W2]) ** 2
        I = I / I.mean() * haz * 0.9
        img = exponer(I, (1.0, 0.08, 0.04)) + exponer(I * 0.06, (1, 0.8, 0.7))
        return img * vineta(W2, H2, 0.5)[..., None]

    escribir(ruta, n, f, W2, H2)


def michelson(ruta, seg=4.0):
    """Anillos de un interferómetro de Michelson: al mover el espejo nacen en el centro."""
    n = int(seg * FPS)
    X, Y = rejilla(W2, H2, 1.0)
    r2 = X ** 2 + Y ** 2
    rng = np.random.default_rng(42)
    mot = 1 + 0.2 * ndimage.gaussian_filter(rng.normal(0, 1, (H2, W2)), 1.0) / 0.3

    def f(i):
        s = i / n
        orden = 8.0 * s                               # 2d/λ crece: un anillo nuevo por orden
        fase = TAU * (orden - 55 * r2)
        I = np.cos(fase / 2) ** 2 * np.exp(-r2 / 0.12) * mot
        img = exponer(I * 3, (1.0, 0.1, 0.06)) + exponer(ndimage.gaussian_filter(I, 8) * 0.8, (1, 0.15, 0.1))
        return img * vineta(W2, H2, 0.45)[..., None]

    escribir(ruta, n, f, W2, H2)


def fraunhofer(ruta, seg=4.0):
    """Difracción de Fraunhofer: |TF de la abertura|² mientras la abertura cambia de forma."""
    n = int(seg * FPS)
    N = 1024
    y, x = np.mgrid[-N // 2:N // 2, -N // 2:N // 2] / (N / 2)
    r, th = np.hypot(x, y), np.arctan2(y, x)

    def poligono(m, rot, R=0.03):
        if m == 0:
            return (r < R).astype(float)
        a = (th - rot) % (TAU / m) - np.pi / m
        return (r * np.cos(a) < R * np.cos(np.pi / m)).astype(float)

    formas = [3, 4, 6, 0, 5, 8]

    def f(i):
        s = i / n * (len(formas) - 1)
        k = int(s)
        u = suave(s - k)
        rot = i / n * 1.4
        ap = (1 - u) * poligono(formas[k], rot) + u * poligono(formas[min(k + 1, len(formas) - 1)], rot)
        F = np.fft.fftshift(np.fft.fft2(ap))
        I = np.abs(F) ** 2
        I = np.log1p(I / I.max() * 3e4) / np.log1p(3e4)
        I = I[(N - H2) // 2:(N + H2) // 2, (N - W2) // 2:(N + W2) // 2]
        img = exponer(I ** 2.2 * 4, (0.2, 1.0, 0.35))
        return img * vineta(W2, H2, 0.4)[..., None]

    escribir(ruta, n, f, W2, H2)


# ---------------------------------------------------------------------------
# luz blanca: interferencia y dispersión
# ---------------------------------------------------------------------------
def newton(ruta, seg=4.0):
    """Anillos de Newton con luz blanca: al apretar la lente, los colores se mueven."""
    n = int(seg * FPS)
    X, Y = rejilla(W2, H2, 1.0)
    r2 = X ** 2 + Y ** 2
    lente = np.clip((0.46 - np.sqrt(r2)) / 0.01, 0, 1)

    def f(i):
        s = i / n
        d = 5200 * r2 + 900 * (1 - suave(s))          # espesor de la cuña de aire (nm)
        delta = TAU * 2 * d[..., None] / WLS + np.pi   # salto de fase de π en la reflexión
        R = np.cos(delta / 2) ** 2
        rgb = espectral(R) * 0.55
        img = rgb * lente[..., None] + (1 - lente)[..., None] * 0.02
        return img * vineta(W2, H2, 0.4)[..., None]

    escribir(ruta, n, f, W2, H2)


def fotoelasticidad(ruta, seg=4.0):
    """Disco comprimido entre polarizadores cruzados: franjas isocromáticas de colores."""
    n = int(seg * FPS)
    X, Y = rejilla(W2, H2, 1.2)
    R = 0.45
    x, y = X / R, (Y - 0.02) / R
    r1 = x ** 2 + (1 - y) ** 2 + 1e-4
    r2 = x ** 2 + (1 + y) ** 2 + 1e-4
    sx = (1 - y) * x ** 2 / r1 ** 2 + (1 + y) * x ** 2 / r2 ** 2 - 0.5
    sy = (1 - y) ** 3 / r1 ** 2 + (1 + y) ** 3 / r2 ** 2 - 0.5
    txy = (1 - y) ** 2 * x / r1 ** 2 - (1 + y) ** 2 * x / r2 ** 2
    dif = np.sqrt((sx - sy) ** 2 + 4 * txy ** 2)
    disco = np.clip((1 - np.hypot(x, y)) / 0.012, 0, 1)

    def f(i):
        carga = 60 + 900 * suave(i / n)             # nm de retardo por unidad de tensión
        delta = np.clip(dif * carga, 0, 9000)
        Rl = np.sin(np.pi * delta[..., None] / WLS) ** 2
        img = espectral(Rl) * 0.85 * disco[..., None]
        borde = np.exp(-((np.hypot(x, y) - 1) / 0.01) ** 2)
        img += borde[..., None] * 0.15
        return img * vineta(W2, H2, 0.35)[..., None]

    escribir(ruta, n, f, W2, H2)


def cielo_rayleigh(X, Y, sol_elev, sol_x=0.0):
    """Cielo por esparcimiento de Rayleigh (aproximación de dispersión simple, 3 canales)."""
    lam = np.array([680.0, 550.0, 440.0])
    beta = (440.0 / lam) ** 4 * 0.33
    elev = np.clip(Y * 0.9 + 0.02, 0.005, 1.5)
    def masa(e):
        e_deg = np.degrees(np.clip(e, -0.05, None))
        return 1 / (np.sin(np.clip(e, 0.003, None)) + 0.15 * (e_deg + 3.885) ** -1.253)
    m_sol = masa(np.array(sol_elev))
    m_vista = masa(elev)
    cosang = np.cos(elev) * np.cos(sol_elev) * np.cos(X - sol_x) + np.sin(elev) * np.sin(sol_elev)
    fase = 0.75 * (1 + cosang ** 2)
    T_sol = np.exp(-beta * m_sol)
    L = beta * fase[..., None] * T_sol * (1 - np.exp(-beta * m_vista[..., None])) / (beta * m_vista[..., None]) * m_vista[..., None]
    L = L * 1.6 * np.clip(np.sin(sol_elev) + 0.12, 0, None) ** 0.5
    ang_sol = np.arccos(np.clip(cosang, -1, 1))
    disco = np.exp(-(ang_sol / 0.012) ** 8) * 30 + np.exp(-(ang_sol / 0.08) ** 2) * 1.2
    L = L + disco[..., None] * T_sol
    return L


def rayleigh(ruta, seg=4.0):
    """Atardecer: el sol baja, el camino óptico crece y el azul se esparce antes de llegar."""
    n = int(seg * FPS)
    X, Y = rejilla(W2, H2, 1.4)
    rng = np.random.default_rng(43)
    xs = np.arange(W2)
    perfil = ndimage.gaussian_filter1d(rng.normal(0, 1, W2), 25) * 0.06 - 0.36 + ndimage.gaussian_filter1d(rng.normal(0, 1, W2), 4) * 0.008
    suelo = Y < perfil[None, :]

    def f(i):
        s = suave(i / n)
        el = np.radians(22 - 24 * s)
        L = cielo_rayleigh(X * 1.1, Y + 0.36, el, 0.05)
        img = 1 - np.exp(-L * 2.6)
        img[suelo] = img[suelo] * 0.03
        return img * vineta(W2, H2, 0.35)[..., None]

    escribir(ruta, n, f, W2, H2)


def arcoiris(ruta, seg=4.0):
    """Arco primario y secundario (colores invertidos) con la banda oscura de Alejandro."""
    n = int(seg * FPS)
    X, Y = rejilla(W2, H2, 1.6)
    L0 = cielo_rayleigh(X, Y + 0.45, np.radians(18), np.pi) * 0.9
    cx, cy = 0.0, -1.05
    ang = np.degrees(np.arctan2(np.hypot(X - cx, (Y - cy)), 1.0) * 1.0)
    ang = np.degrees(np.hypot(X - cx, Y - cy) * 0.7)
    lam = WLS
    # ángulos de desviación aproximados (agua, n(λ) de Cauchy)
    nl = 1.3245 + 3.1e3 / lam ** 2
    def angulo_rayo(k):
        i = np.arccos(np.sqrt((nl ** 2 - 1) / (k * (k + 2))))
        r = np.arcsin(np.sin(i) / nl)
        D = 2 * (i - (k + 1) * r) + k * np.pi
        return np.degrees(np.abs(np.pi - D)) if k == 1 else np.degrees(D - np.pi)
    a1, a2 = angulo_rayo(1), angulo_rayo(2)

    def f(i):
        s = suave(min(i / n * 1.6, 1))
        R1 = np.exp(-((ang[..., None] - a1) / 0.55) ** 2)
        R2 = np.exp(-((ang[..., None] - a2) / 0.9) ** 2) * 0.3
        dentro = np.clip((a1.min() - ang) / 6, 0, 1) * 0.12
        fuera = np.clip((ang - a2.max()) / 6, 0, 1) * 0.06
        luz = espectral(R1 + R2) * 2.4 + (dentro + fuera)[..., None]
        img = 1 - np.exp(-(L0 * 1.3 + luz * s * 0.9))
        img[Y < -0.62] *= 0.08
        return img * vineta(W2, H2, 0.35)[..., None]

    escribir(ruta, n, f, W2, H2)


def espejismo(ruta, seg=4.0):
    """Espejismo inferior: el aire caliente sobre el asfalto curva la luz del cielo hacia arriba."""
    n = int(seg * FPS)
    X, Y = rejilla(W2, H2, 1.0)
    rng = np.random.default_rng(44)
    hz = -0.12
    cielo = 1 - np.exp(-cielo_rayleigh(X * 1.4, Y - hz + 0.02, np.radians(30), 0.6) * 1.2)
    sil = np.zeros(W2)
    for _ in range(14):
        c, a, hgt = rng.uniform(0, W2), rng.uniform(4, 22), rng.uniform(0.01, 0.06)
        sil = np.maximum(sil, hgt * np.exp(-((np.arange(W2) - c) / a) ** 2))
    xs = np.arange(W2)
    ruido = [ndimage.gaussian_filter(rng.normal(0, 1, (H2 * 2, W2)), (3, 10)) for _ in range(2)]

    def f(i):
        t = i / FPS
        img = cielo.copy()
        sobre = (Y > hz) & (Y < hz + sil[None, :])
        img[sobre] = np.array([0.05, 0.05, 0.06])
        abajo = Y <= hz
        prof = (hz - Y)
        persp = np.clip(1 - prof * 3.0, 0, 1)
        img[abajo] = (np.array([0.12, 0.11, 0.1]) * (0.6 + 0.4 * persp[abajo, None]))
        zona = abajo & (prof < 0.09)
        k = int(t * 60) % H2
        temblor = ruido[0][k:k + H2] * 0.006
        fy = np.clip(((hz + (hz - Y) + temblor) / (H2 / W2) * -1 + 0.5) * H2, 0, H2 - 1).astype(int)
        fx = np.clip(((X + ruido[1][k:k + H2] * 0.003) + 0.5) * W2, 0, W2 - 1).astype(int)
        reflejo = cielo[fy, fx]
        sil_ref = (hz + (hz - Y)) < hz + sil[fx]
        reflejo[sil_ref] = np.array([0.05, 0.05, 0.06])
        mezcla = np.clip(1 - prof / 0.09, 0, 1) ** 1.5 * 0.85
        img[zona] = img[zona] * (1 - mezcla[zona, None]) + reflejo[zona] * mezcla[zona, None]
        return img * vineta(W2, H2, 0.35)[..., None]

    escribir(ruta, n, f, W2, H2)


def holograma(ruta, seg=4.0):
    """Superficie holográfica de surcos concéntricos (red de difracción): al girar la luz,
    cada surco devuelve una longitud de onda distinta y aparecen los arcoíris cruzados."""
    n = int(seg * FPS)
    X, Y = rejilla(W2, H2, 1.0)
    r = np.hypot(X, Y)
    phi = np.arctan2(Y, X)
    disco = np.clip((0.47 - r) / 0.006, 0, 1) * np.clip((r - 0.07) / 0.006, 0, 1)
    rng = np.random.default_rng(49)
    micro = 1 + 0.08 * ndimage.gaussian_filter(rng.normal(0, 1, (H2, W2)), 0.8)

    def f(i):
        s = i / n
        luz = 0.6 + TAU * 0.45 * s
        img = np.zeros((H2, W2, 3))
        for orden, peso in ((1, 1.0), (2, 0.45)):
            for desfase in (0.0, np.pi):
                da = (phi - luz - desfase + np.pi) % TAU - np.pi
                banda = np.exp(-(da / (0.18 + 0.1 * orden)) ** 2)
                lam = 400 + 320 * np.clip((r - 0.08) / 0.38 + 0.25 * da / orden, 0, 1)
                img += banda[..., None] * longitud_onda_rgb(lam) * peso
        base = 0.05 + 0.12 * (0.5 + 0.5 * np.cos(2 * (phi - luz)))
        img = (img * 1.3 + base[..., None] * np.array([0.8, 0.85, 0.95])) * micro[..., None] * disco[..., None]
        brillo = np.exp(-((phi - luz + np.pi / 2) % TAU - np.pi) ** 2 / 0.02) * np.exp(-((r - 0.3) / 0.15) ** 2) * 0.6
        img += (brillo * disco)[..., None]
        return img * vineta(W2, H2, 0.4)[..., None]

    escribir(ruta, n, f, W2, H2)


def huygens(ruta, seg=4.0):
    """Frente de onda plano que atraviesa una pantalla con 1, 2 y 5 rendijas (Huygens–Fresnel)."""
    n = int(seg * FPS)
    X, Y = rejilla(W2, H2, 6.0)
    k = TAU / 0.32
    yb = -2.2

    def f(i):
        t = i / FPS
        s = i / n
        m = 1 if s < 0.33 else (2 if s < 0.66 else 5)
        sep = 0.9 if m == 2 else 0.55
        centros = (np.arange(m) - (m - 1) / 2) * sep
        campo = np.zeros_like(X)
        for c in centros:
            for dx in np.linspace(-0.06, 0.06, 4):
                r = np.hypot(X - c - dx, Y - yb) + 1e-3
                campo += np.cos(k * r - TAU * 2.0 * t) / np.sqrt(r + 0.2)
        campo /= (m * 4) ** 0.5 * 2
        abajo = Y < yb
        campo[abajo] = np.cos(k * (Y[abajo] - yb) - TAU * 2.0 * t) * 0.9
        I = np.abs(campo)
        img = exponer(I ** 2 * 1.5, (0.4, 0.75, 1.3)) + exponer(np.clip(campo, 0, None) ** 3 * 0.2, (1, 1, 1))
        pared = (np.abs(Y - yb) < 0.04)
        hueco = np.zeros_like(X, dtype=bool)
        for c in centros:
            hueco |= np.abs(X - c) < 0.08
        img[pared & ~hueco] = np.array([0.85, 0.85, 0.9])
        return img * vineta(W2, H2, 0.4)[..., None]

    escribir(ruta, n, f, W2, H2)


def nefroide(ruta, seg=4.0):
    """Cáustica en una taza: la luz reflejada en una pared circular dibuja una nefroide."""
    n = int(seg * FPS)
    rng = np.random.default_rng(46)
    R = 0.42
    M = 9000
    hs = np.linspace(-0.999, 0.999, M) * R
    pasos = np.linspace(0.0, 1.0, 260)

    def f(i):
        s = i / n
        a = 0.6 * np.sin(TAU * s * 0.4)
        d = np.array([np.cos(a), np.sin(a)])
        perp = np.array([-d[1], d[0]])
        P = -np.sqrt(R ** 2 - hs ** 2)[:, None] * -d * -1
        P = (np.sqrt(R ** 2 - hs ** 2)[:, None] * d) + hs[:, None] * perp
        nrm = P / R
        dr = d - 2 * (nrm @ d)[:, None] * nrm
        pts = P[:, None, :] + pasos[None, :, None] * 2 * R * dr[:, None, :]
        dentro = np.hypot(pts[..., 0], pts[..., 1]) < R
        px = ((pts[..., 0] / 1.0 + 0.5) * W2).astype(int)
        py = ((-pts[..., 1] / 1.0 * W2 / H2 + 0.5) * H2).astype(int)
        ok = dentro & (px >= 0) & (px < W2) & (py >= 0) & (py < H2)
        I = np.bincount((py[ok] * W2 + px[ok]), minlength=W2 * H2).reshape(H2, W2).astype(float)
        I = ndimage.gaussian_filter(I, 1.0) / 18
        X, Y = rejilla(W2, H2, 1.0)
        rr = np.hypot(X, Y)
        fondo = np.where(rr < R, 0.07, 0.02)
        borde = np.exp(-((rr - R) / 0.006) ** 2) * 0.5
        img = exponer(I, (1.0, 0.82, 0.5)) + (fondo + borde)[..., None] * np.array([0.9, 0.85, 0.8])
        return img * vineta(W2, H2, 0.45)[..., None]

    escribir(ruta, n, f, W2, H2)


def fibras(ruta, seg=4.0):
    """Lámpara de fibra óptica: la luz sale por las puntas tras rebotar dentro de cada fibra."""
    n = int(seg * FPS)
    rng = np.random.default_rng(47)
    m = 140
    ang = rng.uniform(-1.25, 1.25, m)
    largo = rng.uniform(0.55, 0.95, m)
    fase = rng.uniform(0, TAU, m)
    prof = rng.uniform(0, 1, m)
    base = np.array([0.0, -0.95])

    def f(i):
        t = i / FPS
        img = np.zeros((H2, W2, 3))
        acc_f = np.zeros((H2, W2))
        puntas = np.zeros((H2, W2, 3))
        for k in range(m):
            sway = 0.04 * np.sin(1.3 * t + fase[k])
            u = np.linspace(0, 1, 60)
            x = base[0] + np.sin(ang[k] + sway) * largo[k] * u
            y = base[1] + largo[k] * 1.6 * u - 0.55 * (np.sin(ang[k]) ** 2) * u ** 2 * largo[k]
            px = ((x / 1.2 + 0.5) * W2).astype(int).clip(0, W2 - 1)
            py = ((-y / 1.2 * W2 / H2 + 0.5) * H2).astype(int).clip(0, H2 - 1)
            acc_f[py, px] += 0.6
            hue = (fase[k] / TAU + 0.12 * t) % 1
            col = hsv_rgb(np.array([hue]), np.array([0.85]), np.array([1.0]))[0]
            puntas[py[-1], px[-1]] += col * (2.5 + 1.5 * np.sin(2 * t + fase[k]) ** 2) * (0.6 + prof[k])
        bokeh = ndimage.gaussian_filter(puntas, (6, 6, 0)) * 60 + ndimage.gaussian_filter(puntas, (1.2, 1.2, 0)) * 3
        img = exponer(ndimage.gaussian_filter(acc_f, 0.6), (0.5, 0.55, 0.7)) * 0.5 + 1 - np.exp(-bokeh)
        return img * vineta(W2, H2, 0.4)[..., None]

    escribir(ruta, n, f, W2, H2)


def lineas_fraunhofer(ruta, seg=4.0):
    """Espectro solar con sus líneas oscuras de absorción (Fraunhofer)."""
    n = int(seg * FPS)
    x = np.linspace(380, 720, W2)
    yy = (np.arange(H2) - H2 / 2) / H2
    rng = np.random.default_rng(48)
    lineas = [(393.4, 1.6, .9), (396.8, 1.4, .85), (430.8, 1.0, .7), (486.1, 1.0, .8), (516.7, 0.8, .6), (518.4, 0.8, .6),
              (527.0, 0.6, .5), (589.0, 0.6, .85), (589.6, 0.6, .85), (656.3, 1.1, .85), (686.7, 1.4, .7)]
    lineas += [(w, rng.uniform(0.15, 0.4), rng.uniform(0.2, 0.5)) for w in rng.uniform(400, 700, 90)]
    planck = 1 / (x ** 5 * (np.exp(1.4388e7 / (x * 5778)) - 1))
    planck = planck / planck.max()

    def f(i):
        s = i / n
        banda = np.exp(-(yy / (0.05 + 0.12 * suave(min(s * 2, 1)))) ** 8)
        absor = np.ones_like(x)
        for k, (w0, a, prof) in enumerate(lineas):
            on = suave(np.clip(s * 3 - (k % 12) * 0.08, 0, 1))
            absor *= 1 - prof * on * np.exp(-((x - w0) / a) ** 2)
        E = (planck * absor)[None, :] * banda[:, None]
        col = longitud_onda_rgb(x)[None, :, :]
        img = 1 - np.exp(-E[..., None] * 1.25 * (col * 0.9 + 0.04))
        img = img + ndimage.gaussian_filter(img, (16, 0, 0)) * 0.5
        return img * vineta(W2, H2, 0.3)[..., None]

    escribir(ruta, n, f, W2, H2)


TOMAS = {
    "laser_abanico": lambda r: laser_show(r, 0), "laser_cruce": lambda r: laser_show(r, 1),
    "laser_espejos": lambda r: laser_show(r, 2), "speckle": speckle, "michelson": michelson,
    "fraunhofer": fraunhofer, "newton": newton, "fotoelasticidad": fotoelasticidad, "rayleigh": rayleigh,
    "arcoiris": arcoiris, "espejismo": espejismo, "holograma": holograma, "huygens": huygens,
    "nefroide": nefroide, "fibras": fibras, "lineas_fraunhofer": lineas_fraunhofer,
}

if __name__ == "__main__":
    salida = Path(sys.argv[1])
    salida.mkdir(parents=True, exist_ok=True)
    for nom in sys.argv[2:] or list(TOMAS):
        TOMAS[nom](salida / f"{nom}.mp4")
        print("OK", nom, flush=True)
