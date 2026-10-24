"""Tercer edit «Física con aura»: solo óptica.

Formato distinto a los anteriores:
  - etalonaje anamórfico (destellos horizontales en las luces intensas, típicos del cine con láseres);
  - visor de cámara/laboratorio: esquinas de encuadre, ● REC, código de tiempo y una lectura técnica
    en monoespaciada por plano (sin decir qué fenómeno es);
  - textos cinéticos propios (sans fina, minúsculas, a la izquierda) en lugar de citas;
  - transiciones nuevas: espectral (separación RGB que converge), estela (entra desde arriba con
    desenfoque vertical), sobreexposición y estrobo, además de corte, zoom y flash.

Uso:  python montar3.py --bruto DIR [--bruto-extra DIR] [--bpm 128] [--solo-montaje]
"""

import argparse
import glob
import shutil
from pathlib import Path

import montar as M

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ.parent / "videos" / "aura3"
CLIPS = SALIDA / "clips"
W, H, FPS = M.W, M.H, M.FPS
MONO = "/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"

# toma -> lectura técnica del visor
TOMAS = {
    "laser_abanico": "λ 532 nm   P 5 W", "laser_cruce": "RGB 638 / 520 / 450 nm", "laser_espejos": "λ 633 nm   R 0.999",
    "speckle": "λ 633 nm   coherente", "michelson": "Δd = λ/2   →   1 franja", "fraunhofer": "I ~ |F{A}|²",
    "airy": "θ ≈ 1.22 λ/D", "doble_rendija": "d sin θ = m λ", "CavidadLaser": "L = q λ/2",
    "SnellTIR": "θc = 41.8°   n = 1.50", "FibraTIR": "n1 > n2", "fibras": "NA 0.50", "Fermat": "δ ∫ n ds = 0",
    "espejismo": "dn/dz > 0", "huygens": "λ = 0.32", "PrismaGiratorio": "n(λ) = A + B/λ²", "arcoiris": "42°   51°",
    "rayleigh": "I ~ λ^-4", "lineas_fraunhofer": "D 589 nm   C 656 nm", "newton": "r² = m λ R",
    "pelicula_jabon": "2 n d = m λ", "holograma": "I = |R + O|²", "fotoelasticidad": "δ = C t (σ1 − σ2)",
    "Polarizacion": "Ex / Ey = e^iφ", "Malus": "I = I0 cos²θ", "nefroide": "r = R/2",
    "ModeLocking": "Δν · Δt ≈ 0.44", "PulsoChirp": "Δt ≈ 12 fs",
}

# (toma, inicio, pulsos, efecto, opciones)  —  opciones: {"texto": FraseX, "vel": 1.4}
GUION = [
    ("laser_abanico", 0.3, 6, "suave", {"texto": "FraseLuz"}),
    # ráfaga de láseres
    ("laser_cruce", 1.0, 1, "espectral", {}), ("speckle", 1.0, 1, "estrobo", {}),
    ("michelson", 1.5, 1, "flash", {}), ("laser_espejos", 2.0, 1, "espectral", {}),
    ("fraunhofer", 1.0, 1, "sobreexp", {}), ("airy", 1.6, 1, "estrobo", {}),
    ("doble_rendija", 2.0, 1, "flash", {}), ("CavidadLaser", 3.4, 1, "espectral", {}),
    # rayos
    ("SnellTIR", 1.2, 2, "estela", {"vel": 1.3}),
    ("FibraTIR", 1.4, 6, "corte", {"texto": "FraseCamino"}),
    ("fibras", 1.0, 2, "sobreexp", {}), ("Fermat", 1.4, 2, "estela", {"vel": 1.3}),
    ("espejismo", 1.0, 2, "corte", {}), ("huygens", 1.4, 2, "espectral", {}),
    # color, dispersión e interferencia
    ("PrismaGiratorio", 0.6, 6, "zoom", {"texto": "FraseColores"}),
    ("arcoiris", 1.6, 2, "sobreexp", {}), ("rayleigh", 0.6, 2, "estela", {"vel": 1.4}),
    ("lineas_fraunhofer", 2.0, 2, "espectral", {}), ("newton", 1.2, 2, "zoom", {}),
    ("pelicula_jabon", 1.5, 1, "flash", {}), ("holograma", 1.0, 2, "espectral", {}),
    ("fotoelasticidad", 1.4, 2, "sobreexp", {}), ("Polarizacion", 1.6, 2, "estela", {}),
    ("Malus", 2.0, 1, "flash", {"vel": 1.5}), ("nefroide", 1.0, 2, "zoom", {}),
    # pulsos ultracortos: drop
    ("ModeLocking", 0.8, 6, "corte", {"texto": "FraseInstante"}),
    ("PulsoChirp", 1.4, 1, "espectral", {"vel": 1.4}), ("laser_abanico", 2.0, 1, "estrobo", {}),
    ("laser_cruce", 2.4, 1, "flash", {}), ("speckle", 2.4, 1, "espectral", {}),
    ("fraunhofer", 2.6, 1, "sobreexp", {}), ("michelson", 2.8, 1, "estrobo", {}),
    ("CavidadLaser", 4.0, 1, "flash", {}), ("laser_espejos", 3.0, 1, "espectral", {}),
    ("laser_abanico", 3.0, 0.5, "flash", {}), ("laser_cruce", 3.0, 0.5, "espectral", {}),
    ("speckle", 3.0, 0.5, "estrobo", {}), ("fraunhofer", 3.4, 0.5, "flash", {}),
    ("laser_espejos", 3.4, 0.5, "espectral", {}), ("michelson", 3.4, 0.5, "estrobo", {}),
    ("airy", 2.4, 0.5, "flash", {}), ("laser_abanico", 3.5, 0.5, "espectral", {}),
    # final
    ("rayleigh", 1.2, 8, "suave", {"texto": "FraseFinal", "vel": 0.8}),
]


def etalonar(bruto: Path, nombre: str):
    """Bloom suave + destello anamórfico horizontal azulado + curva y viñeta."""
    vf = (f"scale={W}:{H}:flags=lanczos,split=3[a][b][c];"
          f"[b]scale={W//4}:{H//4},gblur=sigma=5,scale={W}:{H}[b1];"
          f"[c]scale={W//8}:{H//8},gblur=sigma=26:sigmaV=0.5,scale={W}:{H},"
          "colorchannelmixer=rr=0.55:gg=0.8:bb=1.35[c1];"
          "[a][b1]blend=all_mode=screen:all_opacity=0.6[ab];[ab][c1]blend=all_mode=screen:all_opacity=0.85,"
          "curves=all='0/0 0.2/0.17 0.7/0.75 1/1',vignette=angle=PI/5,format=yuv420p")
    M.ff("-i", bruto, "-filter_complex", vf, "-r", FPS, "-c:v", "libx264", "-crf", 16, "-preset", "medium",
         "-movflags", "+faststart", CLIPS / f"{nombre}.mp4")


def entrada(efecto, dur):
    zoom = f"scale=w='{W}*(1+0.06*exp(-t*12))':h=-2:eval=frame,crop={W}:{H}"
    if efecto == "espectral":   # los canales llegan separados y convergen
        return [zoom, "rgbashift=rh=-52:bh=52:enable='lt(t,0.035)'", "rgbashift=rh=-26:bh=26:enable='between(t,0.035,0.07)'",
                "rgbashift=rh=-10:bh=10:enable='between(t,0.07,0.11)'"]
    if efecto == "estrobo":
        return [zoom, "drawbox=x=0:y=0:w=iw:h=ih:color=black:t=fill:enable='lt(t,0.22)*lt(mod(n,6),3)'"]
    if efecto == "sobreexp":    # quema el plano y lo deja respirar
        return [zoom, "colorlevels=rimax=0.25:gimax=0.25:bimax=0.25:enable='lt(t,0.05)'",
                "colorlevels=rimax=0.55:gimax=0.55:bimax=0.55:enable='between(t,0.05,0.1)'",
                "colorlevels=rimax=0.8:gimax=0.8:bimax=0.8:enable='between(t,0.1,0.15)'"]
    if efecto == "flash":
        return [f"scale=w='{W}*(1+0.14*exp(-t*14))':h=-2:eval=frame", f"crop={W}:{H}", "fade=t=in:st=0:d=0.1:color=white"]
    if efecto == "zoom":
        return [f"scale=w='{W}*(1+0.45*exp(-t*16))':h=-2:eval=frame", f"crop={W}:{H}",
                "gblur=sigma=14:enable='lt(t,0.06)'", "gblur=sigma=6:enable='between(t,0.06,0.13)'"]
    if efecto == "corte":
        return [zoom]
    if efecto == "estela":      # el lienzo se añade en segmento()
        return [f"scale={W}:{H}", "gblur=sigma=0.01:sigmaV=50:enable='lt(t,0.13)'"]
    return [f"scale=w='{W}*(1+0.05*t/{dur:.3f})':h=-2:eval=frame", f"crop={W}:{H}", "fade=t=in:st=0:d=0.35"]


def visor(lectura_txt: Path, tiempo_txt: Path):
    """Esquinas de encuadre, ● REC parpadeante, lectura técnica y código de tiempo."""
    m, L, g = 56, 64, 3
    cajas = []
    for x, y, w_, h_ in ((m, m, L, g), (m, m, g, L), (W - m - L, m, L, g), (W - m - g, m, g, L),
                         (m, H - m - g, L, g), (m, H - m - L, g, L), (W - m - L, H - m - g, L, g), (W - m - g, H - m - L, g, L)):
        cajas.append(f"drawbox=x={x}:y={y}:w={w_}:h={h_}:color=white@0.7:t=fill")
    texto = [
        f"drawtext=fontfile={MONO}:text='● REC':fontsize=26:fontcolor=0xFF3B30:x={m + 20}:y={m + 26}:enable='lt(mod(t,1),0.6)'",
        f"drawtext=fontfile={MONO}:text='4K 60P':fontsize=24:fontcolor=white@0.75:x=w-{m + 20}-text_w:y={m + 28}",
        f"drawtext=fontfile={MONO}:textfile={lectura_txt}:fontsize=26:fontcolor=white@0.85:x={m + 20}:y=h-{m + 60}",
        f"drawtext=fontfile={MONO}:textfile={tiempo_txt}:fontsize=26:fontcolor=white@0.75:x=w-{m + 20}-text_w:y=h-{m + 60}",
    ]
    return ",".join(cajas + texto)


def segmento(ruta, inicio, dur, efecto, lectura, t0, salida, texto=None, vel=1.0, grano=8):
    tmp = salida.parent
    lt, tt = tmp / f"{salida.stem}_l.txt", tmp / f"{salida.stem}_t.txt"
    lt.write_text(lectura)
    tt.write_text(f"%{{pts:hms:{t0:.3f}}}")
    exacto = f"setpts=PTS/{vel},fps={FPS},tpad=stop_mode=clone:stop_duration=4,trim=end_frame={round(dur * FPS)},setpts=PTS-STARTPTS"
    cadena = ",".join([exacto] + entrada(efecto, dur))
    if efecto == "estela":
        cadena = (f"color=black:s={W}x{H}:r={FPS}:d={dur:.4f}[lienzo];[0:v]{cadena}[v];"
                  f"[lienzo][v]overlay=x=0:y='-{H}*pow(max(0,1-t/0.14),2)':shortest=1")
    else:
        cadena = f"[0:v]{cadena}"
    final = f"{visor(lt, tt)},noise=c0s={grano}:c0f=t+u,format=yuv420p"
    cod = ["-r", FPS, "-c:v", "libx264", "-crf", 20, "-preset", "medium", "-an", salida]
    if texto:
        grafo = (f"{cadena},colorlevels=romax=0.55:gomax=0.55:bomax=0.55[b];"
                 f"[1:v]tpad=stop_mode=clone:stop_duration=4,trim=end_frame={round(dur * FPS)},setpts=PTS-STARTPTS,format=rgba,scale={W}:{H}[c];"
                 f"[b][c]overlay=0:0,{final}")
        M.ff("-ss", f"{inicio:.3f}", "-i", ruta, "-i", texto, "-filter_complex", grafo, *cod)
    else:
        M.ff("-ss", f"{inicio:.3f}", "-i", ruta, "-filter_complex", f"{cadena},{final}", *cod)


def montar(bpm):
    pulso = 60.0 / bpm
    tmp = SALIDA / "_tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    guion = list(GUION)
    fotos = sorted(CLIPS.glob("foto_*.mp4"))
    if fotos:
        huecos = [i for i, g in enumerate(guion) if g[2] in (1, 2)][1::3]
        for k, i in enumerate(huecos):
            guion[i] = (fotos[k % len(fotos)].stem, 0.5, *guion[i][2:])
    lista, t_acum, pulsos_acum = [], 0.0, 0.0
    for k, (nom, inicio, pulsos, efecto, op) in enumerate(guion):
        pulsos_acum += pulsos
        fin = round(pulsos_acum * pulso * FPS) / FPS
        dur, t0, t_acum = fin - t_acum, t_acum, fin
        texto = CLIPS / "textos" / f"{op['texto']}.mov" if "texto" in op else None
        seg = tmp / f"{k:03d}.mp4"
        segmento(CLIPS / f"{nom}.mp4", inicio, dur, efecto, TOMAS.get(nom, ""), t0, seg, texto=texto, vel=op.get("vel", 1.0))
        lista.append(seg)
        print(f"  {k:02d} {nom:<18} {pulsos:>4} pulsos  {efecto}", flush=True)
    (tmp / "lista.txt").write_text("".join(f"file '{p.name}'\n" for p in lista))
    final = SALIDA / f"optica_aura_{bpm}bpm.mp4"
    M.ff("-f", "concat", "-safe", 0, "-i", tmp / "lista.txt", "-c", "copy", "-movflags", "+faststart", final)
    shutil.rmtree(tmp)
    print(f"Montaje: {final}  ({M.duracion(final):.2f} s, {bpm} BPM, {t_acum / pulso:.1f} pulsos)")


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
            for c in glob.glob(f"{b}/**/Frase*.mov", recursive=True):
                shutil.copy(c, CLIPS / "textos" / Path(c).name)
        for i, img in enumerate(sorted(glob.glob(str(RAIZ / "fotos" / "*.[jJpP][pPnN]*[gG]")))):
            M.CLIPS = CLIPS
            M.clip_foto(Path(img), f"foto_{i + 1:02d}")
    montar(a.bpm)
