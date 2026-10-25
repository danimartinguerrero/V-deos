"""Tomas calculadas píxel a píxel con numpy (óptica, ondas, cuántica, variable compleja).

No son fotografías: son simulaciones físicas con aspecto fotográfico (láser sobre
una pared, cáusticas en una piscina, película de jabón...). Cada toma se escribe
directamente a vídeo 1080x1920 a 60 fps.

Uso:  python numerico.py SALIDA_DIR [toma1 toma2 ...]
"""

import subprocess
import sys
from pathlib import Path

import numpy as np
from scipy import ndimage, special

W, H, FPS = 1080, 1920, 60


# ---------------------------------------------------------------------------
# utilidades
# ---------------------------------------------------------------------------
def escribir(ruta, n, frame_fn, w=W, h=H):
    """Genera n fotogramas con frame_fn(i) -> array (h, w, 3) en [0,1] y los codifica."""
    cmd = ["ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
           "-r", str(FPS), "-i", "-", "-vf", f"scale={W}:{H}:flags=lanczos", "-c:v", "libx264",
           "-crf", "14", "-preset", "slow", "-pix_fmt", "yuv420p", str(ruta)]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for i in range(n):
        img = np.clip(frame_fn(i), 0, 1)
        p.stdin.write((img * 255 + 0.5).astype(np.uint8).tobytes())
    p.stdin.close()
    p.wait()


def rejilla(w, h, ancho):
    """Coordenadas físicas centradas: x en [-ancho/2, ancho/2], y con la misma escala."""
    x = (np.arange(w) - w / 2 + 0.5) / w * ancho
    y = (np.arange(h) - h / 2 + 0.5) / w * ancho
    return np.meshgrid(x, -y)


def suave(t):
    return t * t * (3 - 2 * t)


def longitud_onda_rgb(wl):
    """Color sRGB aproximado de una longitud de onda en nm (Bruton)."""
    wl = np.asarray(wl, dtype=float)
    r = np.zeros_like(wl); g = np.zeros_like(wl); b = np.zeros_like(wl)
    m = (wl >= 380) & (wl < 440); r[m] = -(wl[m] - 440) / 60; b[m] = 1
    m = (wl >= 440) & (wl < 490); g[m] = (wl[m] - 440) / 50; b[m] = 1
    m = (wl >= 490) & (wl < 510); g[m] = 1; b[m] = -(wl[m] - 510) / 20
    m = (wl >= 510) & (wl < 580); r[m] = (wl[m] - 510) / 70; g[m] = 1
    m = (wl >= 580) & (wl < 645); r[m] = 1; g[m] = -(wl[m] - 645) / 65
    m = (wl >= 645) & (wl <= 780); r[m] = 1
    f = np.ones_like(wl)
    m = (wl >= 380) & (wl < 420); f[m] = 0.3 + 0.7 * (wl[m] - 380) / 40
    m = (wl > 700) & (wl <= 780); f[m] = 0.3 + 0.7 * (780 - wl[m]) / 80
    f[(wl < 380) | (wl > 780)] = 0
    return np.stack([r, g, b], -1) * f[..., None]


def exponer(energia, color, exposicion=1.0):
    """Mapa tonal tipo película: las zonas muy iluminadas saturan hacia el blanco."""
    c = np.asarray(color, dtype=float)
    return 1 - np.exp(-exposicion * energia[..., None] * c)


def ruido_sensor(img, rng, s=0.018):
    return img + rng.normal(0, s, img.shape[:2])[..., None]


def vineta(w, h, fuerza=0.55):
    x, y = np.meshgrid(np.linspace(-1, 1, w), np.linspace(-1, 1, h) * h / w)
    return 1 - fuerza * np.clip((x * x + y * y * 0.55) / 1.6, 0, 1) ** 1.3


def hsv_rgb(hh, s, v):
    i = np.floor(hh * 6).astype(int) % 6
    f = hh * 6 - np.floor(hh * 6)
    p, q, t = v * (1 - s), v * (1 - f * s), v * (1 - (1 - f) * s)
    sel = [(v, t, p), (q, v, p), (p, v, t), (p, q, v), (t, p, v), (v, p, q)]
    out = np.zeros(hh.shape + (3,))
    for k, (a, b, c) in enumerate(sel):
        m = i == k
        out[m, 0], out[m, 1], out[m, 2] = a[m], b[m], c[m]
    return out


# ---------------------------------------------------------------------------
# tomas
# ---------------------------------------------------------------------------
def dominio_color(ruta, seg=4.0):
    """Coloreado de dominio de una función meromorfa con ceros y polos en movimiento."""
    w, h = 720, 1280
    X, Y = rejilla(w, h, 4.6)
    Z = X + 1j * Y
    n = int(seg * FPS)

    def f(i):
        t = i / n * TAU
        ceros = [1.1 * np.exp(1j * (t + k * TAU / 3)) for k in range(3)]
        polos = [0.6j * np.exp(-1j * t) + 0.9, -0.9 - 0.4j * np.exp(1j * 2 * t)]
        F = np.ones_like(Z)
        for c in ceros:
            F = F * (Z - c)
        for p in polos:
            F = F / (Z - p)
        arg = (np.angle(F) / TAU) % 1
        mod = np.log2(np.abs(F) + 1e-12)
        bandas = mod - np.floor(mod)
        lineas = np.abs(np.sin(np.angle(F) * 6)) ** 0.15
        v = (0.55 + 0.45 * bandas ** 0.6) * (0.75 + 0.25 * lineas)
        img = hsv_rgb(arg, np.full_like(arg, 0.68), v * 0.82)
        img *= np.clip(np.abs(F) ** 0.35, 0, 1)[..., None] ** 0.6  # ceros negros
        return img * vineta(w, h, 0.45)[..., None]

    escribir(ruta, n, f, w, h)


def interferencia(ruta, seg=4.0):
    """Dos fuentes puntuales: el campo de ondas y sus franjas hiperbólicas."""
    w, h = 720, 1280
    X, Y = rejilla(w, h, 9.0)
    n = int(seg * FPS)
    k = 2 * np.pi / 0.55
    rng = np.random.default_rng(1)

    def f(i):
        t = i / FPS
        d = 0.9 + 0.5 * suave(min(i / n * 1.4, 1))
        campo = 0
        for s in (-1, 1):
            r = np.hypot(X - s * d, Y + 5.2)
            campo = campo + np.cos(k * r - 2 * np.pi * 1.6 * t) / np.sqrt(r + 0.3)
        amp = np.abs(campo)
        img = exponer(amp ** 2 * 0.9, (0.35, 0.85, 1.25), 1.0)
        img = img + exponer(np.clip(campo, 0, None) ** 3 * 0.15, (1, 1, 1))
        for s in (-1, 1):
            r = np.hypot(X - s * d, Y + 5.2)
            img += np.exp(-(r / 0.08) ** 2)[..., None] * np.array([1, 1, 1])
        return ruido_sensor(img * vineta(w, h)[..., None], rng, 0.01)

    escribir(ruta, n, f, w, h)


def doble_rendija(ruta, seg=4.0):
    """Patrón de un láser rojo tras una doble rendija, proyectado en una pared."""
    w, h = 720, 1280
    X, Y = rejilla(w, h, 1.0)
    n = int(seg * FPS)
    rng = np.random.default_rng(2)
    pared = ndimage.gaussian_filter(rng.normal(0, 1, (h, w)), 6)
    pared = 0.012 + 0.006 * pared / pared.std()
    speckle = ndimage.gaussian_filter(rng.normal(0, 1, (h, w)), 1.2)
    speckle = 1 + 0.35 * speckle / speckle.std()

    def f(i):
        s = i / n
        zoom = 1.0 + 0.06 * s
        x, y = X / zoom, (Y + 0.02 * np.sin(2 * s)) / zoom
        fr = 13.0                       # frecuencia de las franjas (d/λL)
        env = 2.6                       # envolvente de una rendija (a/λL)
        I = np.cos(np.pi * fr * y) ** 2 * np.sinc(env * y) ** 2
        I = I * np.exp(-(x / 0.11) ** 2)
        encendido = suave(min(s * 2.5, 1))
        E = I * speckle * 9 * encendido
        img = exponer(E, (1.0, 0.11, 0.05), 1.0) + exponer(E * 0.08, (0.6, 0.6, 0.5))
        img = img + pared[..., None] * np.array([1.0, 0.85, 0.8]) * (0.6 + 0.6 * encendido)
        halo = ndimage.gaussian_filter(E, 18)
        img = img + exponer(halo * 0.6, (1, 0.1, 0.06))
        return ruido_sensor(img * vineta(w, h, 0.6)[..., None], rng, 0.015)

    escribir(ruta, n, f, w, h)


def airy(ruta, seg=3.0):
    """Disco de Airy: difracción de un láser verde por una abertura circular."""
    w, h = 720, 1280
    X, Y = rejilla(w, h, 1.0)
    R = np.hypot(X, Y)
    n = int(seg * FPS)
    rng = np.random.default_rng(3)
    speckle = 1 + 0.25 * ndimage.gaussian_filter(rng.normal(0, 1, (h, w)), 1.3) / 0.33

    def f(i):
        s = i / n
        escala = 55 - 25 * suave(s)       # la abertura se cierra: los anillos crecen
        u = escala * R + 1e-6
        I = (2 * special.j1(u) / u) ** 2
        E = I * 60 * speckle
        img = exponer(E, (0.1, 1.0, 0.25)) + exponer(ndimage.gaussian_filter(E, 10) * 0.5, (0.1, 0.9, 0.3))
        return ruido_sensor(img * vineta(w, h)[..., None], rng, 0.014)

    escribir(ruta, n, f, w, h)


def causticas(ruta, seg=4.0):
    """Cáusticas en el fondo de una piscina: rayos refractados por una superficie ondulada."""
    w, h = 540, 960
    n = int(seg * FPS)
    sobre = 3
    gx, gy = np.meshgrid(np.arange(w * sobre) / sobre, np.arange(h * sobre) / sobre)
    rng = np.random.default_rng(4)
    ondas = []
    for _ in range(12):
        ang = rng.uniform(0, 2 * np.pi)
        lam = rng.uniform(45, 140)
        ondas.append((np.cos(ang) * 2 * np.pi / lam, np.sin(ang) * 2 * np.pi / lam,
                      rng.uniform(0.6, 1.4), rng.uniform(0, 2 * np.pi), rng.uniform(0.6, 1.0)))

    def f(i):
        t = i / FPS
        dx = np.zeros_like(gx); dy = np.zeros_like(gy)
        for kx, ky, om, ph, a in ondas:
            fase = kx * gx + ky * gy - om * t * 2 + ph
            c = np.cos(fase) * a
            dx += c * kx; dy += c * ky
        D = 75.0
        px = (gx + D * dx).astype(int) % w
        py = (gy + D * dy).astype(int) % h
        I = np.bincount((py * w + px).ravel(), minlength=w * h).reshape(h, w) / sobre ** 2
        I = ndimage.gaussian_filter(I, 0.8)
        img = exponer(I * 0.42, (0.45, 0.95, 1.05)) * 0.95 + np.array([0.0, 0.05, 0.10])
        return img * vineta(w, h, 0.5)[..., None]

    escribir(ruta, n, f, w, h)


def pelicula_jabon(ruta, seg=4.0):
    """Interferencia de película delgada en una pompa de jabón (colores calculados del espectro)."""
    w, h = 540, 960
    X, Y = rejilla(w, h, 2.0)
    R = np.hypot(X, Y + 0.05)
    n = int(seg * FPS)
    wls = np.linspace(400, 700, 31)
    cols = longitud_onda_rgb(wls)
    cols = cols / cols.sum(0)
    disco = np.clip((0.82 - R) / 0.01, 0, 1)
    nz = np.sqrt(np.clip(1 - (R / 0.82) ** 2, 0, 1))
    rng = np.random.default_rng(5)
    rem = [(rng.uniform(1, 4), rng.uniform(1, 4), rng.uniform(0, 6), rng.uniform(0.4, 1.2)) for _ in range(6)]

    def f(i):
        t = i / FPS
        u, v = X.copy(), Y.copy()
        for a, b, ph, sp in rem:  # remolinos que arrastran el espesor
            u = u + 0.06 * np.sin(b * v + ph + sp * t)
            v = v + 0.06 * np.sin(a * u + ph * 1.3 - sp * t)
        espesor = 60 + 950 * np.clip(0.55 - 0.55 * v, 0, None) ** 0.8 + 110 * np.sin(5 * u + 3 * v + t)
        espesor = np.clip(espesor, 0, None)
        delta = 4 * np.pi * 1.33 * espesor[..., None] / wls
        Rf = np.sin(delta / 2) ** 2
        rgb = (Rf @ cols) * 1.6
        gris = rgb.mean(-1, keepdims=True)
        rgb = gris + (rgb - gris) * 1.25
        brillo = 0.22 + 0.78 * (1 - nz) ** 2
        img = rgb * brillo[..., None] * disco[..., None]
        esp = np.exp(-(((X + 0.35) ** 2 + (Y - 0.4) ** 2) / 0.006))
        img += (esp * disco)[..., None] * 0.9
        return img * vineta(w, h, 0.4)[..., None]

    escribir(ruta, n, f, w, h)


def orbital(ruta, seg=4.0):
    """Densidad de probabilidad del hidrógeno, |ψ_{5,3,1}|², en un plano que gira."""
    w, h = 540, 960
    X, Y = rejilla(w, h, 105.0)
    n = int(seg * FPS)
    nq, l, m = 5, 3, 1

    def psi2(x, y, z):
        r = np.sqrt(x * x + y * y + z * z) + 1e-9
        rho = 2 * r / nq
        Rr = rho ** l * np.exp(-rho / 2) * special.eval_genlaguerre(nq - l - 1, 2 * l + 1, rho)
        th = np.arccos(np.clip(z / r, -1, 1))
        ph = np.arctan2(y, x)
        Y_ = special.lpmv(m, l, np.cos(th)) * np.cos(m * ph)
        return (Rr * Y_) ** 2

    def f(i):
        s = i / n
        a = np.pi * s * 0.9
        x3, y3, z3 = X * np.cos(a), X * np.sin(a), Y
        d = psi2(x3 * (1 - 0.15 * s), y3, z3 * (1 - 0.15 * s))
        d = d / np.percentile(d, 99.7)
        img = exponer(d * 1.4, (0.75, 0.45, 1.35))
        return img * vineta(w, h, 0.4)[..., None]

    escribir(ruta, n, f, w, h)


def lente_gravitacional(ruta, seg=5.0):
    """Un agujero negro cruza delante de una galaxia: aparece el anillo de Einstein."""
    w, h = 720, 1280
    X, Y = rejilla(w, h, 2.0)
    n = int(seg * FPS)
    rng = np.random.default_rng(6)
    # plano fuente: estrellas + galaxia espiral
    fuente = np.zeros((h, w, 3))
    for _ in range(7000):
        px, py = rng.integers(0, w), rng.integers(0, h)
        b = rng.pareto(2.2) * 0.6
        fuente[py, px] += b * longitud_onda_rgb(rng.uniform(430, 680)) * 0.5 + b * 0.5
    fuente = ndimage.gaussian_filter(fuente, (0.8, 0.8, 0))
    r = np.hypot(X, Y); th = np.arctan2(Y, X)
    brazos = (np.cos(2 * th - 7 * r) * 0.5 + 0.5) ** 3
    gal = np.exp(-(r / 0.22) ** 2) * (0.45 + brazos) + np.exp(-(r / 0.05) ** 2) * 2
    fuente += gal[..., None] * np.array([1.0, 0.82, 0.6]) * 0.9
    thE = 0.32

    def f(i):
        s = i / n
        lx, ly = -0.9 + 1.8 * suave(s), 0.08
        dx, dy = X - lx, Y - ly
        r2 = dx * dx + dy * dy + 1e-6
        bx = X - thE ** 2 * dx / r2
        by = Y - thE ** 2 * dy / r2
        cx = (bx / 2.0 + 0.5) * w - 0.5
        cy = (-by / 2.0 * w / h + 0.5) * h - 0.5
        img = np.stack([ndimage.map_coordinates(fuente[..., c], [cy, cx], order=1, mode="constant") for c in range(3)], -1)
        rr = np.sqrt(r2)
        horizonte = np.clip((rr - 0.075) / 0.01, 0, 1)
        anillo = np.exp(-((rr - 0.11) / 0.012) ** 2) * 0.8
        img = img * horizonte[..., None] + anillo[..., None] * np.array([1.0, 0.75, 0.45])
        return img * vineta(w, h, 0.35)[..., None]

    escribir(ruta, n, f, w, h)


def espectro(ruta, seg=3.0):
    """Líneas de emisión de Balmer del hidrógeno sobre un espectro continuo tenue."""
    w, h = 720, 1280
    n = int(seg * FPS)
    x = np.linspace(380, 720, w)
    rng = np.random.default_rng(7)
    lineas = [(656.3, 1.0), (486.1, 0.55), (434.0, 0.35), (410.2, 0.25)]
    yy = (np.arange(h) - h / 2) / h
    banda = np.exp(-(yy / 0.11) ** 8)

    def f(i):
        s = i / n
        E = np.zeros((h, w))
        for k, (wl, a) in enumerate(lineas):
            on = suave(np.clip(s * 4 - k * 0.6, 0, 1))
            perfil = np.exp(-((x - wl) / 0.9) ** 2) * a * on
            E += perfil[None, :] * banda[:, None]
        cont = 0.012 * suave(np.clip(s * 2 - 1, 0, 1)) * banda[:, None]
        col = longitud_onda_rgb(x)[None, :, :]
        img = 1 - np.exp(-(E[..., None] * 18 + cont[..., None] * 6) * (col + 0.08))
        img = img + ndimage.gaussian_filter(img, (14, 6, 0)) * 0.8
        return ruido_sensor(img, rng, 0.008)

    escribir(ruta, n, f, w, h)


TOMAS = {
    "dominio_color": dominio_color,
    "interferencia": interferencia,
    "doble_rendija": doble_rendija,
    "airy": airy,
    "causticas": causticas,
    "pelicula_jabon": pelicula_jabon,
    "orbital": orbital,
    "lente_gravitacional": lente_gravitacional,
    "espectro": espectro,
}
TAU = 2 * np.pi

if __name__ == "__main__":
    salida = Path(sys.argv[1])
    salida.mkdir(parents=True, exist_ok=True)
    nombres = sys.argv[2:] or list(TOMAS)
    for nom in nombres:
        TOMAS[nom](salida / f"{nom}.mp4")
        print("OK", nom, flush=True)
