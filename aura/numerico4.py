"""Tomas calculadas del cuarto edit (mecánica clásica).

caos_fractal: mapa de condiciones iniciales (θ1, θ2) de un péndulo doble; el color es el estado
              (θ1, θ2) en el instante t, así que la imagen se rompe en un fractal a medida que avanza.
lagrange:     potencial efectivo del problema restringido de tres cuerpos en el sistema que gira,
              con los cinco puntos de Lagrange.
Uso:  python numerico4.py SALIDA_DIR [toma ...]
"""

import sys
from pathlib import Path

import numpy as np
from scipy import ndimage

from numerico import FPS, escribir, exponer, hsv_rgb, rejilla, suave, vineta

TAU = 2 * np.pi
W2, H2 = 540, 960


def caos_fractal(ruta, seg=5.0):
    n = int(seg * FPS)
    w, h = 360, 640
    t1, t2 = np.meshgrid(np.linspace(-np.pi, np.pi, w), np.linspace(np.pi * 16 / 9 / 2, -np.pi * 16 / 9 / 2, h))
    y = np.stack([t1, t2, np.zeros_like(t1), np.zeros_like(t1)])

    def f(y):
        a, b, wa, wb = y
        d = a - b
        den = 3 - np.cos(2 * d)
        aa = (-3 * np.sin(a) - np.sin(a - 2 * b) - 2 * np.sin(d) * (wb ** 2 + wa ** 2 * np.cos(d))) / den
        ab = (2 * np.sin(d) * (2 * wa ** 2 + 2 * np.cos(a) + wb ** 2 * np.cos(d))) / den
        return np.stack([wa, wb, aa, ab])

    T = 9.0
    pasos = 6
    dt = T / n / pasos
    estado = [y]

    def cuadro(i):
        nonlocal y
        if i > 0:
            for _ in range(pasos):
                k1 = f(y); k2 = f(y + dt / 2 * k1); k3 = f(y + dt / 2 * k2); k4 = f(y + dt * k3)
                y = y + dt / 6 * (k1 + 2 * k2 + 2 * k3 + k4)
        a, b = y[0], y[1]
        hue = (np.arctan2(np.sin(a), np.sin(b)) / TAU) % 1
        sat = np.clip(0.35 + 0.65 * np.abs(np.sin(a / 2)), 0, 1)
        val = 0.25 + 0.75 * (0.5 + 0.5 * np.cos(b))
        img = hsv_rgb(hue, sat * 0.8, val * 0.9)
        return img * vineta(w, h, 0.4)[..., None]

    escribir(ruta, n, cuadro, w, h)


def lagrange(ruta, seg=5.0):
    n = int(seg * FPS)
    mu = 0.12
    X, Y = rejilla(W2, H2, 3.4)
    x1, x2 = -mu, 1 - mu
    rng = np.random.default_rng(9)
    estrellas = np.zeros((H2, W2))
    estrellas.flat[rng.integers(0, W2 * H2, 500)] = rng.pareto(2.5, 500) * 0.35
    estrellas = ndimage.gaussian_filter(estrellas, 0.6)
    # puntos de Lagrange (colineales por Newton-Raphson sobre la derivada del potencial)
    def dphi(x):
        return x - (1 - mu) * (x - x1) / abs(x - x1) ** 3 - mu * (x - x2) / abs(x - x2) ** 3
    L = []
    for x0 in (0.6, 1.2, -1.0):
        x = x0
        for _ in range(60):
            h = 1e-6
            x -= dphi(x) / ((dphi(x + h) - dphi(x - h)) / (2 * h))
        L.append((x, 0.0))
    L += [(0.5 - mu, np.sqrt(3) / 2), (0.5 - mu, -np.sqrt(3) / 2)]

    def cuadro(i):
        s = i / n
        ang = TAU * 0.12 * s
        ca, sa = np.cos(ang), np.sin(ang)
        x, y = X * ca + Y * sa, -X * sa + Y * ca          # el sistema gira con los dos cuerpos
        r1 = np.hypot(x - x1, y) + 1e-3
        r2 = np.hypot(x - x2, y) + 1e-3
        phi = -(1 - mu) / r1 - mu / r2 - 0.5 * (x * x + y * y)
        v = np.clip(-phi, 1.4, 4.0)
        bandas = (v * 14) % 1
        lineas = np.exp(-((bandas - 0.5) / 0.06) ** 2) * np.clip((2.6 - v) / 1.0, 0, 1)
        prof = np.clip(((1 - mu) / r1 + mu / r2 - 1.2) / 2.5, 0, 1)
        img = estrellas[..., None] * np.array([0.8, 0.85, 1])
        img += exponer(lineas * 0.9, (0.55, 0.75, 1.2)) * suave(min(s * 3, 1))
        img += exponer(prof ** 3 * 0.25, (1.0, 0.65, 0.35))
        for k, (lx, ly) in enumerate(L):
            px, py = lx * ca - ly * sa, lx * sa + ly * ca
            d2 = (X - px) ** 2 + (Y - py) ** 2
            on = suave(np.clip(s * 4 - 0.6 - k * 0.25, 0, 1))
            img += (np.exp(-d2 / 0.0006) * 2 + np.exp(-d2 / 0.006) * 0.4)[..., None] * np.array([0.6, 1.0, 0.85]) * on
        for (bx, m, c) in ((x1, 1 - mu, (1.0, 0.75, 0.45)), (x2, mu, (0.6, 0.75, 1.0))):
            px, py = bx * ca, bx * sa
            d2 = (X - px) ** 2 + (Y - py) ** 2
            img += (np.exp(-d2 / (0.002 * (0.4 + m))) * 3 + np.exp(-d2 / 0.02) * 0.5)[..., None] * np.array(c)
        img = 1 - np.exp(-img * 1.2)
        return img * vineta(W2, H2, 0.4)[..., None]

    escribir(ruta, n, cuadro, W2, H2)


TOMAS = {"caos_fractal": caos_fractal, "lagrange": lagrange}

if __name__ == "__main__":
    salida = Path(sys.argv[1])
    salida.mkdir(parents=True, exist_ok=True)
    for nom in sys.argv[2:] or list(TOMAS):
        TOMAS[nom](salida / f"{nom}.mp4")
        print("OK", nom, flush=True)
