"""Quinto edit «Física con aura»: electrostática (temas 1, 2 y 3).

Formato propio:
  - etalonaje frío con halación (las luces intensas sangran un halo rojizo, como en película) y bloom;
  - un pequeño medidor horizontal arriba a la izquierda que se dispara en cada pulso y decae;
  - etiqueta de tema arriba a la derecha (TEMA 1 · leyes básicas, TEMA 2 · desarrollo multipolar,
    TEMA 3 · conductores);
  - tarjetas-ecuación que se encienden parpadeando como un tubo fluorescente;
  - transiciones eléctricas: descarga (destello con barras de interferencia), chispa (parpadeo),
    polaridad (inversión de tono de un instante) e implosión (el plano entra desde pequeño).

Uso:  python montar5.py --bruto DIR [--bpm 128] [--solo-montaje]
"""

import argparse
import glob
import shutil
from pathlib import Path

import montar as M

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ.parent / "videos" / "aura5"
CLIPS = SALIDA / "clips"
W, H, FPS = M.W, M.H, M.FPS
NEGRA = "/usr/share/fonts/opentype/inter/Inter-SemiBold.otf"
FINA = "/usr/share/fonts/opentype/inter/Inter-Light.otf"

TOMAS = ["FlujoGauss", "DivergenciaLocal", "divergencia_mapa", "polarizacion_campo", "Coulomb", "DeltaDirac", "Distribuciones", "GaussSimetrias", "Contorno", "RelievePotencial", "Teoremas",
         "Legendre", "Polarizacion", "Condensadores", "Coeficientes", "Tierra",
         "dipolo", "cuadrupolo", "iguales", "imagen", "multipolo", "faraday", "condensador", "cavidad",
         "sistema", "esferas_hilo", "ruptura"]

T1, T2, T3 = "TEMA 1|leyes básicas", "TEMA 2|desarrollo multipolar", "TEMA 3|conductores"

# (toma, inicio, pulsos, efecto, opciones)  opciones: texto, vel, tema
GUION = [
    ("dipolo", 0.0, 6, "suave", {"texto": "TarjetaGauss", "tema": T1}),
    ("divergencia_mapa", 1.0, 2, "descarga", {}), ("DivergenciaLocal", 2.4, 2, "implosion", {}),
    ("Coulomb", 1.0, 2, "chispa", {}), ("FlujoGauss", 1.2, 2, "polaridad", {}),
    ("DeltaDirac", 2.6, 2, "descarga", {}), ("divergencia_mapa", 2.6, 2, "implosion", {}),
    ("Teoremas", 1.6, 2, "chispa", {}), ("Distribuciones", 1.6, 2, "polaridad", {}),
    ("GaussSimetrias", 1.4, 2, "descarga", {}), ("Contorno", 2.6, 2, "implosion", {}),
    ("RelievePotencial", 1.2, 2, "chispa", {}), ("FlujoGauss", 3.0, 1, "descarga", {}),
    ("divergencia_mapa", 3.8, 1, "polaridad", {}), ("iguales", 3.6, 1, "chispa", {}), ("dipolo", 2.6, 1, "descarga", {}),
    ("multipolo", 0.0, 6, "suave", {"texto": "TarjetaMultipolo", "tema": T2}),
    ("polarizacion_campo", 1.4, 2, "implosion", {}), ("Legendre", 1.6, 2, "descarga", {}),
    ("cuadrupolo", 1.4, 2, "chispa", {}), ("Polarizacion", 2.2, 2, "polaridad", {}),
    ("polarizacion_campo", 3.4, 2, "descarga", {}), ("multipolo", 3.0, 1, "chispa", {}),
    ("Legendre", 3.8, 1, "polaridad", {}), ("cuadrupolo", 3.4, 1, "descarga", {}), ("dipolo", 4.0, 1, "chispa", {}),
    ("faraday", 0.3, 6, "suave", {"texto": "TarjetaConductor", "tema": T3}),
    ("esferas_hilo", 1.4, 2, "implosion", {}), ("cavidad", 1.0, 2, "chispa", {}),
    ("imagen", 1.6, 2, "polaridad", {}), ("condensador", 0.8, 2, "descarga", {}),
    ("Condensadores", 3.0, 2, "implosion", {}), ("sistema", 1.0, 2, "chispa", {}),
    ("Coeficientes", 2.6, 2, "polaridad", {}), ("Tierra", 2.4, 2, "descarga", {}),
    ("ruptura", 0.4, 4, "corte", {}),
    ("faraday", 2.6, 1, "descarga", {}), ("divergencia_mapa", 4.0, 1, "chispa", {}), ("cavidad", 3.0, 1, "polaridad", {}),
    ("sistema", 3.0, 1, "descarga", {}), ("polarizacion_campo", 4.2, 1, "implosion", {}), ("dipolo", 3.4, 1, "chispa", {}),
    ("multipolo", 4.0, 1, "descarga", {}), ("ruptura", 3.8, 1, "polaridad", {}),
    ("ruptura", 3.9, 0.5, "descarga", {}), ("faraday", 3.6, 0.5, "chispa", {}),
    ("ruptura", 4.0, 0.5, "descarga", {}), ("cavidad", 4.0, 0.5, "chispa", {}),
    ("ruptura", 4.1, 0.5, "descarga", {}), ("divergencia_mapa", 4.4, 0.5, "polaridad", {}),
    ("ruptura", 4.2, 0.5, "descarga", {}), ("esferas_hilo", 4.0, 0.5, "chispa", {}),
    ("sistema", 0.3, 9, "suave", {"texto": "TarjetaFinal", "vel": 0.8}),
]


def etalonar(bruto: Path, nombre: str):
    vf = (f"scale={W}:{H}:flags=lanczos,split=3[a][b][c];"
          f"[b]scale={W//4}:{H//4},gblur=sigma=5,scale={W}:{H}[b1];"
          f"[c]scale={W//4}:{H//4},curves=all='0/0 0.55/0 1/1',gblur=sigma=9,scale={W}:{H},"
          "colorchannelmixer=rr=1.2:gg=0.35:bb=0.15[c1];"
          "[a][b1]blend=all_mode=screen:all_opacity=0.55[ab];[ab][c1]blend=all_mode=screen:all_opacity=0.5,"
          "colorbalance=rs=-0.04:bs=0.05:rm=-0.02:bm=0.03,curves=all='0/0 0.22/0.19 0.7/0.76 1/1',"
          "vignette=angle=PI/5,format=yuv420p")
    M.ff("-i", bruto, "-filter_complex", vf, "-r", FPS, "-c:v", "libx264", "-crf", 16, "-preset", "medium",
         "-movflags", "+faststart", CLIPS / f"{nombre}.mp4")


def entrada(efecto, dur):
    zoom = f"scale=w='{W}*(1+0.06*exp(-t*12))':h=-2:eval=frame,crop={W}:{H}"
    if efecto == "descarga":   # destello con barras horizontales de interferencia
        barras = [f"drawbox=x=0:y={y}:w=iw:h={hh}:color=white@0.85:t=fill:enable='lt(t,0.07)'"
                  for y, hh in ((260, 14), (700, 6), (1150, 22), (1480, 8))]
        return [zoom, "fade=t=in:st=0:d=0.09:color=white", *barras, "rgbashift=rh=-18:bh=18:enable='lt(t,0.07)'"]
    if efecto == "chispa":     # parpadeo de tubo
        return [zoom, "drawbox=x=0:y=0:w=iw:h=ih:color=black@0.85:t=fill:enable='lt(t,0.25)*lt(mod(n,5),2)'"]
    if efecto == "polaridad":  # inversión de tono de un instante
        return [zoom, "hue=h='180*lt(t,0.09)'"]
    if efecto == "implosion":  # se resuelve en el grafo (entra desde pequeño)
        return [f"scale={W}:{H}"]
    if efecto == "corte":
        return [zoom]
    return [f"scale=w='{W}*(1+0.05*t/{dur:.3f})':h=-2:eval=frame", f"crop={W}:{H}", "fade=t=in:st=0:d=0.35"]


def capas(tema, t0, pulso, sin_tema):
    """Medidor de pulso pequeño arriba a la izquierda y etiqueta de tema arriba a la derecha."""
    f = []
    # medidor pequeño y discreto, horizontal, arriba a la izquierda (8 segmentos)
    n, x0, y, ancho, alto = 8, 80, 152, 12, 5
    nivel = f"exp(-mod({t0:.4f}+t\\,{pulso:.5f})/{pulso * 0.45:.4f})"
    for j in range(n):
        x = x0 + j * (ancho + 4)
        color = "0x40C8FF" if j < 5 else ("0xFFC266" if j < 7 else "0xFF5CA0")
        f.append(f"drawbox=x={x}:y={y}:w={ancho}:h={alto}:color=white@0.12:t=fill")
        f.append(f"drawbox=x={x}:y={y}:w={ancho}:h={alto}:color={color}@0.75:t=fill:enable='gt({nivel}\\,{(j + 0.5) / n:.3f})'")
    if tema and not sin_tema:
        cab, sub = tema.split("|")
        cab = "  ".join(cab)
        f.append(f"drawtext=fontfile={NEGRA}:text='{cab}':fontsize=28:fontcolor=white@0.9:x=w-tw-80:y=140")
        f.append(f"drawtext=fontfile={FINA}:text='{sub}':fontsize=34:fontcolor=white@0.7:x=w-tw-80:y=186")
        f.append(f"drawbox=x=iw-80-170:y=240:w=170:h=2:color=0x40C8FF@0.8:t=fill")
    return ",".join(f)


def segmento(ruta, inicio, dur, efecto, salida, tema, t0, pulso, texto=None, vel=1.0, grano=8):
    nf = round(dur * FPS)
    exacto = f"setpts=PTS/{vel},fps={FPS},tpad=stop_mode=clone:stop_duration=4,trim=end_frame={nf},setpts=PTS-STARTPTS"
    cadena = ",".join([exacto] + entrada(efecto, dur))
    if efecto == "implosion":
        cadena = (f"color=black:s={W}x{H}:r={FPS}:d={dur:.4f}[lz];[0:v]{cadena},"
                  f"scale=w='{W}*(1-0.35*exp(-t*16))':h=-2:eval=frame[v];"
                  f"[lz][v]overlay=x='({W}-w)/2':y='({H}-h)/2':shortest=1")
    else:
        cadena = f"[0:v]{cadena}"
    final = f"{capas(tema, t0, pulso, texto is not None)},noise=c0s={grano}:c0f=t+u,format=yuv420p"
    cod = ["-r", FPS, "-c:v", "libx264", "-crf", 20, "-preset", "medium", "-an", salida]
    if texto:
        grafo = (f"{cadena},colorlevels=romax=0.42:gomax=0.42:bomax=0.42[b];"
                 f"[1:v]tpad=stop_mode=clone:stop_duration=4,trim=end_frame={nf},setpts=PTS-STARTPTS,format=rgba,scale={W}:{H}[c];"
                 f"[b][c]overlay=0:0,{final}")
        M.ff("-ss", f"{inicio:.3f}", "-i", ruta, "-i", texto, "-filter_complex", grafo, *cod)
    else:
        M.ff("-ss", f"{inicio:.3f}", "-i", ruta, "-filter_complex", f"{cadena},{final}", *cod)


def montar(bpm):
    pulso = 60.0 / bpm
    tmp = SALIDA / "_tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    lista, t_acum, pulsos_acum, tema = [], 0.0, 0.0, ""
    for k, (nom, inicio, pulsos, efecto, op) in enumerate(GUION):
        tema = op.get("tema", tema)
        pulsos_acum += pulsos
        fin = round(pulsos_acum * pulso * FPS) / FPS
        dur, t0, t_acum = fin - t_acum, t_acum, fin
        texto = CLIPS / "textos" / f"{op['texto']}.mov" if "texto" in op else None
        seg = tmp / f"{k:03d}.mp4"
        segmento(CLIPS / f"{nom}.mp4", inicio, dur, efecto, seg, tema, t0, pulso, texto=texto, vel=op.get("vel", 1.0))
        lista.append(seg)
        print(f"  {k:02d} {nom:<16} {pulsos:>4} pulsos  {efecto}", flush=True)
    (tmp / "lista.txt").write_text("".join(f"file '{p.name}'\n" for p in lista))
    final = SALIDA / f"electro_aura_{bpm}bpm.mp4"
    M.ff("-f", "concat", "-safe", 0, "-i", tmp / "lista.txt", "-c", "copy", "-movflags", "+faststart", final)
    shutil.rmtree(tmp)
    print(f"Montaje: {final}  ({M.duracion(final):.2f} s, {bpm} BPM, {pulsos_acum:.1f} pulsos)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bruto", action="append", default=[])
    ap.add_argument("--bpm", type=int, default=128)
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
            for c in glob.glob(f"{b}/**/Tarjeta*.mov", recursive=True):
                shutil.copy(c, CLIPS / "textos" / Path(c).name)
    montar(a.bpm)
