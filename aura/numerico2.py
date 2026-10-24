"""Tomas calculadas del segundo edit: skyrmiones, galaxia espiral, agujero negro con disco
de acreción, nebulosa y descarga eléctrica (figura de Lichtenberg).

Son simulaciones o composiciones procedurales con aspecto realista, no fotografías.
Uso:  python numerico2.py SALIDA_DIR [toma1 toma2 ...]
"""

import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

from numerico import FPS, escribir, exponer, hsv_rgb, longitud_onda_rgb, rejilla, suave, vineta

TAU = 2 * np.pi


def skyrmiones(ruta, seg=4.0):
    """Red hexagonal de skyrmiones magnéticos: color = dirección en el plano, brillo = m_z."""
    w, h = 540, 960
    X, Y = rejilla(w, h, 9.0)
    n = int(seg * FPS)
    a = 2.5
    centros = []
    for i in range(-4, 5):
        for j in range(-6, 7):
            centros.append((i * a + (j % 2) * a / 2, j * a * np.sqrt(3) / 2))
    centros = np.array(centros)
    R = 1.15

    def f(i):
        s = i / n
        dx, dy = 0.5 * np.sin(TAU * s * 0.5), 0.9 * s
        chi = TAU * s * 0.5                       # helicidad: de Néel a Bloch
        px, py = X + dx, Y + dy
        mz = -np.ones_like(X)
        ang = np.zeros_like(X)
        sinth = np.zeros_like(X)
        for cx, cy in centros:
            rx, ry = px - cx, py - cy
            r = np.hypot(rx, ry)
            dentro = r < R
            th = np.pi * r[dentro] / R
            mz[dentro] = np.cos(th)
            sinth[dentro] = np.sin(th)
            ang[dentro] = np.arctan2(ry[dentro], rx[dentro]) + chi
        hue = (ang / TAU) % 1
        val = 0.04 + 0.96 * ((1 + mz) / 2) ** 0.55
        img = hsv_rgb(hue, 0.8 * sinth, val)
        return img * vineta(w, h, 0.45)[..., None]

    escribir(ruta, n, f, w, h)


def galaxia(ruta, seg=4.0):
    """Galaxia espiral: estrellas en brazos de onda de densidad con rotación diferencial."""
    w, h = 720, 1280
    n = int(seg * FPS)
    rng = np.random.default_rng(12)
    N = 220000
    r = np.abs(rng.gamma(2.0, 0.55, N)) + 0.03
    brazo = rng.integers(0, 2, N)
    th0 = np.log(r + 0.2) / 0.32 + brazo * np.pi + rng.normal(0, 0.55, N)
    disco = rng.uniform(0, 1, N) < 0.35
    th0[disco] = rng.uniform(0, TAU, disco.sum())
    bulbo = rng.uniform(0, 1, N) < 0.15
    r[bulbo] = np.abs(rng.normal(0, 0.35, bulbo.sum()))
    th0[bulbo] = rng.uniform(0, TAU, bulbo.sum())
    brillo = rng.pareto(3.0, N) * 0.12 + 0.04
    brillo[bulbo] *= 1.6
    col = np.where(bulbo[:, None], np.array([1.0, 0.82, 0.55]), np.array([0.62, 0.78, 1.0]))
    col = col * (0.8 + 0.4 * rng.uniform(size=(N, 1)))
    hii = (~bulbo) & (rng.uniform(0, 1, N) < 0.025)
    col[hii] = np.array([1.0, 0.35, 0.6])
    brillo[hii] *= 3

    def f(i):
        s = i / n
        om = 0.9 / (r + 0.35)                         # rotación diferencial (curva plana)
        th = th0 + om * s * 1.2
        zoom = 1.0 + 0.15 * suave(s)
        x = r * np.cos(th) * zoom
        y = r * np.sin(th) * 0.55 * zoom              # inclinación
        ca, sa = np.cos(0.5), np.sin(0.5)
        x, y = x * ca - y * sa, x * sa + y * ca
        px = ((x / 4.3 + 0.5) * w).astype(int)
        py = ((-y / 4.3 * w / h + 0.5) * h).astype(int)
        ok = (px >= 0) & (px < w) & (py >= 0) & (py < h)
        img = np.zeros((h, w, 3))
        for c in range(3):
            img[..., c] = np.bincount(py[ok] * w + px[ok], weights=(brillo * col[:, c])[ok], minlength=w * h).reshape(h, w)
        img = ndimage.gaussian_filter(img, (0.7, 0.7, 0)) + ndimage.gaussian_filter(img, (7, 7, 0)) * 0.9
        img = 1 - np.exp(-img * 1.6)
        return img * vineta(w, h, 0.4)[..., None]

    escribir(ruta, n, f, w, h)


def gargantua(ruta, seg=5.0):
    """Agujero negro con disco de acreción: sombra, anillo de fotones, disco con efecto Doppler
    y la imagen del disco trasero curvada por encima y por debajo (composición estilizada)."""
    w, h = 720, 1280
    X, Y = rejilla(w, h, 3.2)
    n = int(seg * FPS)
    rng = np.random.default_rng(13)
    textura = ndimage.gaussian_filter(rng.normal(0, 1, (64, 720)), (1.2, 6), mode="wrap")
    textura = (textura - textura.min()) / np.ptp(textura)
    estrellas = np.zeros((h, w))
    idx = rng.integers(0, h * w, 900)
    estrellas.flat[idx] = rng.pareto(2.5, 900) * 0.4
    estrellas = ndimage.gaussian_filter(estrellas, 0.7)
    rs = 0.26
    incl = 0.16

    def muestra_disco(rr, phi, t):
        u = ((phi / TAU) % 1 * 720 + t * 160 / np.maximum(rr, 0.3)).astype(int) % 720
        v = np.clip(((rr - 0.42) / 1.3 * 63), 0, 63).astype(int)
        return textura[v, u]

    def f(i):
        t = i / FPS
        zoom = 1.0 - 0.08 * suave(i / n)
        x, y = X * zoom, Y * zoom
        img = estrellas[..., None] * np.array([0.8, 0.85, 1.0])
        # disco delantero (elipse aplanada)
        rd = np.hypot(x, y / incl)
        phi = np.arctan2(y / incl, x)
        en_disco = (rd > 0.42) & (rd < 1.75)
        perfil = np.clip((rd - 0.42) / 0.08, 0, 1) * np.exp(-(rd - 0.42) / 0.55)
        doppler = 1 + 0.75 * np.cos(phi)            # el lado que se acerca brilla más
        I_disco = en_disco * perfil * doppler * (0.45 + 0.8 * muestra_disco(rd, phi, t))
        delante = y < 0
        # imagen del disco trasero curvada alrededor de la sombra
        r = np.hypot(x, y)
        ang = np.arctan2(y, x)
        rb = 0.42 + (r - 0.31) * 3.2
        arco = (r > 0.31) & (r < 0.72)
        I_arco = arco * np.clip((rb - 0.42) / 0.08, 0, 1) * np.exp(-(rb - 0.42) / 0.5) * (1 + 0.6 * np.cos(ang)) \
            * (0.5 + 0.8 * muestra_disco(rb, ang, t))
        anillo = np.exp(-((r - 0.285) / 0.012) ** 2) * 1.3
        sombra = np.clip((r - rs) / 0.01, 0, 1)
        I = (I_arco * 0.9 + anillo) * sombra + I_disco * np.where(delante | (r > 0.36), 1, 0)
        I = np.where(delante, np.maximum(I, I_disco), I)
        luz = exponer(I * 1.6, (1.15, 0.72, 0.38))
        img = img * sombra[..., None] + luz
        img = img + ndimage.gaussian_filter(luz, (14, 14, 0)) * 0.6
        return img * vineta(w, h, 0.4)[..., None]

    escribir(ruta, n, f, w, h)


def nebulosa(ruta, seg=4.0):
    """Nebulosa de emisión procedural (ruido fractal) con estrellas en varias capas de paralaje."""
    w, h = 720, 1280
    n = int(seg * FPS)
    rng = np.random.default_rng(14)
    W2, H2 = int(w * 1.35), int(h * 1.35)

    def fbm(semilla):
        r = np.random.default_rng(semilla)
        acc = np.zeros((H2, W2))
        for k, s in enumerate((140, 70, 35, 17, 8)):
            acc += ndimage.gaussian_filter(r.normal(0, 1, (H2, W2)), s) * s ** 1.5
        acc = (acc - acc.mean()) / acc.std()
        return acc

    gas = np.clip(fbm(1) * 0.9 + 0.2, 0, None) ** 1.6
    polvo = np.clip(fbm(2), 0, None)
    oiii = np.clip(fbm(3) * 0.8, 0, None) ** 1.5
    base = gas[..., None] * np.array([0.95, 0.32, 0.42]) + oiii[..., None] * np.array([0.15, 0.62, 0.75])
    base = base * np.exp(-polvo * 0.9)[..., None]
    capas = []
    for k in range(3):
        e = np.zeros((H2, W2))
        m = [1600, 500, 120][k]
        e.flat[rng.integers(0, H2 * W2, m)] = rng.pareto(2.0, m) * [0.25, 0.6, 1.4][k]
        capas.append(ndimage.gaussian_filter(e, [0.6, 0.8, 1.3][k]))

    def f(i):
        s = suave(i / n)
        img = np.zeros((h, w, 3))
        for k, (capa, vel) in enumerate(((base, 0.2), (capas[0], 0.35), (capas[1], 0.6), (capas[2], 1.0))):
            ox = int((W2 - w) / 2 + vel * 80 * (s - 0.5))
            oy = int((H2 - h) / 2 - vel * 120 * (s - 0.5))
            trozo = capa[oy:oy + h, ox:ox + w]
            if trozo.ndim == 2:
                trozo = trozo[..., None] * np.array([0.9, 0.93, 1.0])
            img += trozo * (0.42 if k == 0 else 1)
        img = 1 - np.exp(-img * 2.0)
        return img * vineta(w, h, 0.4)[..., None]

    escribir(ruta, n, f, w, h)


def rayo(ruta, seg=3.0):
    """Descarga eléctrica ramificada: el líder avanza a saltos, después el destello de retorno."""
    w, h = 540, 960
    n = int(seg * FPS)
    rng = np.random.default_rng(15)
    segmentos = []                          # (x0, y0, x1, y1, orden, grosor)
    puntas = [(w / 2, 0.0, np.pi / 2, 1.0)]
    paso = 0
    while puntas and paso < 260:
        nuevas = []
        for x, y, a, g in puntas:
            a2 = a + rng.normal(0, 0.45)
            a2 = np.clip(a2, 0.25, np.pi - 0.25)
            L = rng.uniform(5, 11)
            x2, y2 = x + L * np.cos(a2), y + L * np.sin(a2)
            segmentos.append((x, y, x2, y2, paso, g))
            if y2 < h - 5 and 0 < x2 < w:
                nuevas.append((x2, y2, (a2 + np.pi / 2) / 2 + rng.normal(0, 0.15), g))
                if rng.uniform() < 0.07 * g and len(nuevas) < 40:
                    nuevas.append((x2, y2, a2 + rng.choice([-1, 1]) * rng.uniform(0.5, 1.0), g * 0.5))
        puntas = [p for p in nuevas if p[3] > 0.1 or rng.uniform() < 0.97]
        paso += 1
    orden_max = paso

    def lienzo(hasta, principal_brillo):
        acc = np.zeros((h, w))
        for x0, y0, x1, y1, o, g in segmentos:
            if o > hasta:
                continue
            k = int(np.hypot(x1 - x0, y1 - y0)) + 2
            xs = np.linspace(x0, x1, k).astype(int).clip(0, w - 1)
            ys = np.linspace(y0, y1, k).astype(int).clip(0, h - 1)
            acc[ys, xs] += g * (principal_brillo if g >= 1 else 1)
        return acc

    def f(i):
        s = i / n
        if s < 0.55:
            hasta = int(orden_max * s / 0.55)
            acc = lienzo(hasta, 1.0) * 0.8
            flash = 0.0
        else:
            k = (s - 0.55) / 0.45
            parpadeo = np.exp(-k * 5) * (1 + 0.6 * np.sin(k * 40) ** 2)
            acc = lienzo(orden_max, 3.0) * (0.6 + 2.5 * parpadeo)
            flash = 0.35 * parpadeo
        nucleo = ndimage.gaussian_filter(acc, 0.8)
        halo = ndimage.gaussian_filter(acc, 6) * 2.5 + ndimage.gaussian_filter(acc, 25) * 6
        img = exponer(nucleo * 2.2, (1, 1, 1)) + exponer(halo, (0.55, 0.45, 1.25))
        img = img + flash * np.array([0.5, 0.45, 0.9])
        return img * vineta(w, h, 0.4)[..., None]

    escribir(ruta, n, f, w, h)


TOMAS = {"skyrmiones": skyrmiones, "galaxia": galaxia, "gargantua": gargantua, "nebulosa": nebulosa, "rayo": rayo}

if __name__ == "__main__":
    salida = Path(sys.argv[1])
    salida.mkdir(parents=True, exist_ok=True)
    for nom in sys.argv[2:] or list(TOMAS):
        TOMAS[nom](salida / f"{nom}.mp4")
        print("OK", nom, flush=True)
