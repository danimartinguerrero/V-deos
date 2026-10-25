"""Cuarto edit «Física con aura»: mecánica clásica.

Formato propio:
  - etalonaje en tono partido (sombras frías, luces cálidas) con bloom suave;
  - cabecera de capítulo arriba a la izquierda (numeral romano en serif + nombre espaciado);
  - una «regla de compases» en el borde derecho con una marca que avanza al ritmo;
  - palabras enormes en serif cursiva (inertia, resonance, symmetry, chaos) que abren cada capítulo;
  - transiciones «mecánicas»: rebote (zoom amortiguado), péndulo (vaivén horizontal amortiguado),
    giro (entra rotando) y dividir (las dos mitades se encajan), además de corte, flash y suave.

Uso:  python montar4.py --bruto DIR [--bruto DIR2] [--bpm 124] [--solo-montaje]
"""

import argparse
import glob
import shutil
from pathlib import Path

import montar as M

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ.parent / "videos" / "aura4"
CLIPS = SALIDA / "clips"
W, H, FPS = M.W, M.H, M.FPS
SERIF = "/usr/share/fonts/truetype/cmu/cmunti.ttf"
SANS = "/usr/share/fonts/opentype/inter/Inter-Light.otf"

TOMAS = ["PlanoInclinado", "Explosion", "Rodadura", "Steiner", "Patinadora", "TresRegimenes", "Pohl", "Acoplados",
         "Lissajous", "Liouville", "Atwood", "Cohete", "CunaNewton", "Colision2D", "Galileo", "Hodografa", "PenduloDoble",
         "caos_fractal", "lagrange"]

# (toma, inicio, pulsos, efecto, opciones)  opciones: texto, vel, cap (abre capítulo: "I|NEWTON")
GUION = [
    ("Explosion", 0.0, 6, "suave", {"texto": "PalabraInercia", "cap": "I|NEWTON"}),
    ("PlanoInclinado", 1.4, 2, "rebote", {}), ("CunaNewton", 0.8, 2, "pendulo", {}),
    ("Colision2D", 1.8, 2, "dividir", {}), ("Galileo", 1.0, 2, "giro", {}),
    ("Atwood", 1.6, 2, "rebote", {}), ("Cohete", 1.8, 2, "dividir", {}),
    ("Rodadura", 1.4, 2, "pendulo", {}), ("Steiner", 1.6, 2, "giro", {}), ("Patinadora", 2.4, 2, "rebote", {}),
    ("Pohl", 1.6, 6, "corte", {"texto": "PalabraResonancia", "cap": "II|OSCILACIONES"}),
    ("TresRegimenes", 1.5, 2, "pendulo", {}), ("Acoplados", 2.0, 2, "dividir", {}),
    ("Lissajous", 2.0, 2, "giro", {}), ("Pohl", 3.4, 1, "flash", {}), ("Acoplados", 3.5, 1, "rebote", {}),
    ("Liouville", 0.6, 6, "suave", {"texto": "PalabraSimetria", "cap": "III|LAGRANGE · HAMILTON"}),
    ("Liouville", 2.6, 2, "rebote", {}), ("Lissajous", 3.6, 2, "pendulo", {}),
    ("lagrange", 0.6, 6, "corte", {"texto": "PalabraCaos", "cap": "IV|GRAVITACIÓN · CAOS"}),
    ("Hodografa", 1.0, 2, "giro", {}), ("PenduloDoble", 1.0, 2, "dividir", {}), ("caos_fractal", 1.6, 2, "rebote", {}),
    ("PenduloDoble", 2.8, 1, "flash", {}), ("caos_fractal", 3.0, 1, "giro", {}), ("lagrange", 2.6, 1, "flash", {}),
    ("Explosion", 1.6, 1, "rebote", {}), ("CunaNewton", 2.2, 1, "pendulo", {}), ("Rodadura", 3.0, 1, "flash", {}),
    ("Lissajous", 4.0, 1, "giro", {}), ("Pohl", 4.2, 1, "flash", {}), ("caos_fractal", 3.8, 1, "flash", {}),
    ("Hodografa", 3.0, 1, "dividir", {}),
    ("caos_fractal", 4.0, 0.5, "flash", {}), ("PenduloDoble", 3.6, 0.5, "giro", {}),
    ("caos_fractal", 4.3, 0.5, "flash", {}), ("PenduloDoble", 4.0, 0.5, "giro", {}),
    ("caos_fractal", 4.6, 0.5, "flash", {}), ("lagrange", 4.0, 0.5, "giro", {}),
    ("caos_fractal", 4.8, 0.5, "flash", {}), ("PenduloDoble", 4.4, 0.5, "giro", {}),
    ("caos_fractal", 0.3, 10, "suave", {"texto": "PalabraFinal", "vel": 0.8}),
]


def etalonar(bruto: Path, nombre: str):
    vf = (f"scale={W}:{H}:flags=lanczos,split=2[a][b];[b]scale={W//4}:{H//4},gblur=sigma=6,scale={W}:{H}[b1];"
          "[a][b1]blend=all_mode=screen:all_opacity=0.55,"
          "colorbalance=rs=-0.06:gs=0.0:bs=0.07:rh=0.07:gh=0.03:bh=-0.05,"
          "curves=all='0/0 0.25/0.21 0.7/0.76 1/1',vignette=angle=PI/5,format=yuv420p")
    M.ff("-i", bruto, "-filter_complex", vf, "-r", FPS, "-c:v", "libx264", "-crf", 16, "-preset", "medium",
         "-movflags", "+faststart", CLIPS / f"{nombre}.mp4")


def entrada(efecto, dur):
    if efecto == "rebote":     # zoom que oscila amortiguado, como un muelle
        return [f"scale=w='{W}*(1+0.16*exp(-6*t)*(1+cos(26*t))/2)':h=-2:eval=frame", f"crop={W}:{H}"]
    if efecto == "pendulo":    # vaivén horizontal amortiguado
        return [f"scale={int(W * 1.1)}:-2", f"crop={W}:{H}:x='(iw-{W})/2+52*exp(-5*t)*cos(22*t)':y='(ih-{H})/2'"]
    if efecto == "giro":
        return [f"scale=w='{W}*(1.12+0.3*exp(-t*12))':h=-2:eval=frame", f"crop={W}:{H}",
                "rotate=a='0.45*exp(-t*13)':fillcolor=black"]
    if efecto == "flash":
        return [f"scale=w='{W}*(1+0.12*exp(-t*14))':h=-2:eval=frame", f"crop={W}:{H}", "fade=t=in:st=0:d=0.1:color=white"]
    if efecto == "corte":
        return [f"scale=w='{W}*(1+0.05*exp(-t*10))':h=-2:eval=frame", f"crop={W}:{H}"]
    if efecto == "dividir":    # se resuelve en el grafo
        return [f"scale={W}:{H}"]
    return [f"scale=w='{W}*(1+0.05*t/{dur:.3f})':h=-2:eval=frame", f"crop={W}:{H}", "fade=t=in:st=0:d=0.35"]


def capas(cap, t0, total, sin_cabecera):
    """Regla de compases a la derecha y cabecera de capítulo."""
    x = W - 70
    y0, y1 = 300, H - 300
    f = [f"drawbox=x={x}:y={y0}:w=2:h={y1 - y0}:color=white@0.22:t=fill"]
    for k in range(9):
        f.append(f"drawbox=x={x - 6}:y={y0 + k * (y1 - y0) // 8}:w=14:h=2:color=white@0.35:t=fill")
    f.append(f"drawbox=x={x - 12}:y='{y0}+({t0:.4f}+t)/{total:.4f}*{y1 - y0}':w=26:h=4:color=white@0.95:t=fill")
    if cap and not sin_cabecera:
        num, nombre = cap.split("|")
        nombre = "  ".join(nombre).replace(":", r"\:")
        f.append(f"drawtext=fontfile={SERIF}:text='{num}':fontsize=84:fontcolor=white@0.9:x=80:y=150")
        f.append(f"drawbox=x=80:y=262:w=60:h=2:color=white@0.6:t=fill")
        f.append(f"drawtext=fontfile={SANS}:text='{nombre}':fontsize=24:fontcolor=white@0.75:x=80:y=284")
    return ",".join(f)


def segmento(ruta, inicio, dur, efecto, salida, cap, t0, total, texto=None, vel=1.0, grano=9):
    nf = round(dur * FPS)
    exacto = f"setpts=PTS/{vel},fps={FPS},tpad=stop_mode=clone:stop_duration=4,trim=end_frame={nf},setpts=PTS-STARTPTS"
    cadena = ",".join([exacto] + entrada(efecto, dur))
    if efecto == "dividir":
        cadena = (f"color=black:s={W}x{H}:r={FPS}:d={dur:.4f}[lz];[0:v]{cadena},split=2[a][b];"
                  f"[a]crop={W}:{H // 2}:0:0[sup];[b]crop={W}:{H // 2}:0:{H // 2}[inf];"
                  f"[lz][sup]overlay=0:'-{H // 2}*pow(max(0,1-t/0.16),2)':shortest=1[m];"
                  f"[m][inf]overlay=0:'{H // 2}+{H // 2}*pow(max(0,1-t/0.16),2)'")
    else:
        cadena = f"[0:v]{cadena}"
    final = f"{capas(cap, t0, total, texto is not None)},noise=c0s={grano}:c0f=t+u,format=yuv420p"
    cod = ["-r", FPS, "-c:v", "libx264", "-crf", 20, "-preset", "medium", "-an", salida]
    if texto:
        grafo = (f"{cadena},colorlevels=romax=0.45:gomax=0.45:bomax=0.45[b];"
                 f"[1:v]tpad=stop_mode=clone:stop_duration=4,trim=end_frame={nf},setpts=PTS-STARTPTS,format=rgba,scale={W}:{H}[c];"
                 f"[b][c]overlay=0:0,{final}")
        M.ff("-ss", f"{inicio:.3f}", "-i", ruta, "-i", texto, "-filter_complex", grafo, *cod)
    else:
        M.ff("-ss", f"{inicio:.3f}", "-i", ruta, "-filter_complex", f"{cadena},{final}", *cod)


def montar(bpm):
    pulso = 60.0 / bpm
    total = sum(g[2] for g in GUION) * pulso
    tmp = SALIDA / "_tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    lista, t_acum, pulsos_acum, cap = [], 0.0, 0.0, ""
    for k, (nom, inicio, pulsos, efecto, op) in enumerate(GUION):
        cap = op.get("cap", cap)
        pulsos_acum += pulsos
        fin = round(pulsos_acum * pulso * FPS) / FPS
        dur, t0, t_acum = fin - t_acum, t_acum, fin
        texto = CLIPS / "textos" / f"{op['texto']}.mov" if "texto" in op else None
        seg = tmp / f"{k:03d}.mp4"
        segmento(CLIPS / f"{nom}.mp4", inicio, dur, efecto, seg, cap, t0, total, texto=texto, vel=op.get("vel", 1.0))
        lista.append(seg)
        print(f"  {k:02d} {nom:<16} {pulsos:>4} pulsos  {efecto}", flush=True)
    (tmp / "lista.txt").write_text("".join(f"file '{p.name}'\n" for p in lista))
    final = SALIDA / f"mecanica_aura_{bpm}bpm.mp4"
    M.ff("-f", "concat", "-safe", 0, "-i", tmp / "lista.txt", "-c", "copy", "-movflags", "+faststart", final)
    shutil.rmtree(tmp)
    print(f"Montaje: {final}  ({M.duracion(final):.2f} s, {bpm} BPM, {pulsos_acum:.1f} pulsos)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bruto", action="append", default=[])
    ap.add_argument("--bpm", type=int, default=124)
    ap.add_argument("--solo-montaje", action="store_true")
    a = ap.parse_args()
    CLIPS.mkdir(parents=True, exist_ok=True)
    (CLIPS / "textos").mkdir(exist_ok=True)
    if not a.solo_montaje:
        for nom in TOMAS:
            hall = [h for b in a.bruto for h in glob.glob(f"{b}/**/{nom}.mp4", recursive=True)]
            if not hall:
                print("falta", nom)
                continue
            etalonar(Path(hall[0]), nom)
            print("etalonado", nom, flush=True)
        for b in a.bruto:
            for c in glob.glob(f"{b}/**/Palabra*.mov", recursive=True):
                shutil.copy(c, CLIPS / "textos" / Path(c).name)
    montar(a.bpm)
