"""Plantilla de edit «Física con aura».

1. Etalonaje: a cada toma en bruto (Manim o numpy) le añade bloom, viñeta y la deja
   lista como clip suelto en videos/aura/clips/ para editarla a mano (CapCut, etc.).
2. Montaje: corta los clips al ritmo de un BPM, con golpes de zoom, destellos,
   aberración cromática en los cortes, rótulos y grano de película, y exporta
   videos/aura/fisica_aura_<BPM>bpm.mp4 (sin audio: pon tú la canción).

Tus propias fotos (jpg/png) en aura/fotos/ se convierten en clips con movimiento
(Ken Burns) y se intercalan automáticamente en el montaje.

Uso:
    python montar.py --bruto DIR_TOMAS [--bpm 120] [--solo-montaje]
"""

import argparse
import glob
import shutil
import subprocess
from pathlib import Path

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ.parent / "videos" / "aura"
CLIPS = SALIDA / "clips"
FUENTE = "/usr/share/fonts/opentype/inter/Inter-Light.otf"
W, H, FPS = 1080, 1920, 60

# Tomas: nombre -> (tipo, rótulo).  tipo "vector" = Manim (bloom fuerte), "luz" = numpy.
TOMAS = {
    "Titulo": ("vector", ""),
    "Maxwell": ("vector", "ELECTRODINÁMICA"),
    "Dipolo": ("vector", "ELECTRODINÁMICA"),
    "OndaEM": ("vector", "ONDAS ELECTROMAGNÉTICAS"),
    "Schrodinger": ("vector", "MECÁNICA CUÁNTICA"),
    "AccionMinima": ("vector", "MECÁNICA LAGRANGIANA"),
    "Kepler": ("vector", "GRAVITACIÓN"),
    "TresCuerpos": ("vector", "PROBLEMA DE TRES CUERPOS"),
    "PozoGravitatorio": ("vector", "RELATIVIDAD GENERAL"),
    "Lorenz": ("vector", "CAOS"),
    "PenduloFase": ("vector", "ESPACIO DE FASES"),
    "Euler": ("vector", "EXPONENCIAL COMPLEJA"),
    "Fourier": ("vector", "SERIES DE FOURIER"),
    "Conforme": ("vector", "VARIABLE COMPLEJA"),
    "Prisma": ("vector", "ÓPTICA"),
    "Estacionarias": ("vector", "ONDAS"),
    "Cierre": ("vector", ""),
    "Elegante": ("vector", ""),
    "dominio_color": ("luz", "VARIABLE COMPLEJA"),
    "interferencia": ("luz", "INTERFERENCIA"),
    "doble_rendija": ("luz", "DOBLE RENDIJA"),
    "airy": ("luz", "DIFRACCIÓN"),
    "causticas": ("luz", "CÁUSTICAS"),
    "pelicula_jabon": ("luz", "PELÍCULA DELGADA"),
    "orbital": ("luz", "ÁTOMO DE HIDRÓGENO"),
    "lente_gravitacional": ("luz", "LENTE GRAVITACIONAL"),
    "espectro": ("luz", "SERIE DE BALMER"),
}

# Guion del montaje: (toma, segundo de inicio dentro de la toma, pulsos, efecto)
#   efecto: "suave" (entra desde negro y empuja), "corte" (golpe de zoom), "flash" (destello blanco)
GUION = [
    ("Titulo", 0.2, 6, "suave"),
    # A — presentación (las citas se superponen a la toma, que se atenúa)
    ("Lorenz", 0.0, 10, "suave", "CitaFeynman"),
    ("doble_rendija", 0.8, 4, "corte"),
    ("Schrodinger", 0.0, 10, "corte", "CitaHeisenberg"),
    ("Kepler", 0.3, 4, "corte"),
    # B — subida: 2 pulsos por plano
    ("Dipolo", 1.4, 2, "flash"),
    ("interferencia", 1.5, 2, "corte"),
    ("Maxwell", 1.6, 2, "flash"),
    ("orbital", 1.0, 2, "corte"),
    ("Euler", 0.8, 2, "flash"),
    ("pelicula_jabon", 1.0, 2, "corte"),
    ("TresCuerpos", 1.2, 2, "flash"),
    ("causticas", 1.0, 2, "corte"),
    # C — drop: 1 pulso por plano
    ("airy", 1.5, 1, "flash"),
    ("OndaEM", 1.5, 1, "flash"),
    ("dominio_color", 1.0, 1, "flash"),
    ("AccionMinima", 2.6, 1, "flash"),
    ("espectro", 2.0, 1, "flash"),
    ("PozoGravitatorio", 2.0, 1, "flash"),
    ("PenduloFase", 2.0, 1, "flash"),
    ("Prisma", 2.6, 1, "flash"),
    ("Conforme", 3.0, 1, "flash"),
    ("Estacionarias", 2.0, 1, "flash"),
    ("lente_gravitacional", 1.6, 1, "flash"),
    ("Maxwell", 3.0, 1, "flash"),
    ("orbital", 2.5, 1, "flash"),
    ("interferencia", 2.8, 1, "flash"),
    ("Lorenz", 4.0, 1, "flash"),
    ("doble_rendija", 2.6, 1, "flash"),
    # D — final
    ("lente_gravitacional", 0.0, 10, "corte", "CitaSagan"),
    ("Fourier", 0.0, 10, "corte", "CitaCox"),
    ("Cierre", 0.0, 4, "flash"),
    ("Elegante", 0.0, 8, "suave"),
]


def ff(*args):
    subprocess.run(["ffmpeg", "-v", "error", "-y", *map(str, args)], check=True)


def duracion(ruta):
    r = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", str(ruta)],
                       capture_output=True, text=True, check=True)
    return float(r.stdout.strip())


# ---------------------------------------------------------------------------
def etalonar(bruto: Path, nombre: str, tipo: str):
    """Bloom + viñeta + ligera curva de contraste. Sin grano (se añade en el montaje)."""
    if tipo == "vector":
        # el bloom se calcula a 1/4 de resolución (mismo aspecto, mucho más rápido)
        bloom = (f"split=3[a][b][c];[b]scale={W//4}:{H//4},gblur=sigma=6.5,scale={W}:{H}[b1];"
                 f"[c]scale={W//2}:{H//2},gblur=sigma=3.5,scale={W}:{H}[c1];"
                 "[a][c1]blend=all_mode=screen:all_opacity=0.85[ac];[ac][b1]blend=all_mode=screen:all_opacity=0.75,")
    else:
        bloom = (f"split=2[a][b];[b]scale={W//4}:{H//4},gblur=sigma=6,scale={W}:{H}[b1];"
                 "[a][b1]blend=all_mode=screen:all_opacity=0.45,")
    vf = (f"scale={W}:{H}:flags=lanczos,{bloom}"
          "curves=all='0/0 0.25/0.22 0.7/0.76 1/1',vignette=angle=PI/5,format=yuv420p")
    ff("-i", bruto, "-filter_complex", vf, "-r", FPS, "-c:v", "libx264", "-crf", 16, "-preset", "medium",
       "-movflags", "+faststart", CLIPS / f"{nombre}.mp4")


def clip_foto(img: Path, nombre: str, seg=4.0):
    """Ken Burns sobre una foto propia: recorte vertical, acercamiento lento, contraste."""
    n = int(seg * FPS)
    vf = (f"scale={W*2}:{H*2}:force_original_aspect_ratio=increase,crop={W*2}:{H*2},"
          f"zoompan=z='1+0.12*on/{n}':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d={n}:s={W}x{H}:fps={FPS},"
          "eq=contrast=1.12:saturation=1.08:gamma=0.95,vignette=angle=PI/4.5,format=yuv420p")
    ff("-loop", 1, "-i", img, "-vf", vf, "-t", seg, "-c:v", "libx264", "-crf", 16, "-preset", "slow",
       CLIPS / f"{nombre}.mp4")


# ---------------------------------------------------------------------------
def rotulo(texto):
    espaciado = "  ".join(texto)  # tracking amplio a mano
    espaciado = espaciado.replace(":", r"\:").replace("'", r"\'")
    return (f"drawtext=fontfile={FUENTE}:text='{espaciado}':fontsize=30:fontcolor=white@0.85:"
            f"x=(w-text_w)/2:y=h*0.115:alpha='min(1,t*6)'")


def segmento(ruta, inicio, dur, efecto, texto, salida, grano=8, cita=None):
    # duración exacta: se rellena con el último fotograma y se recorta, para que los cortes caigan en el pulso
    exacto = f"tpad=stop_mode=clone:stop_duration=3,trim=duration={dur:.4f},setpts=PTS-STARTPTS"
    filtros = [exacto]
    if efecto == "flash":
        filtros += [f"scale=w='{W}*(1+0.14*exp(-t*14))':h=-2:eval=frame", f"crop={W}:{H}",
                    "rgbashift=rh=-10:bh=10:enable='lt(t,0.10)'", "fade=t=in:st=0:d=0.12:color=white"]
    elif efecto == "corte":
        filtros += [f"scale=w='{W}*(1+0.06*exp(-t*10))':h=-2:eval=frame", f"crop={W}:{H}",
                    "rgbashift=rh=-6:bh=6:enable='lt(t,0.07)'"]
    else:  # suave
        filtros += [f"scale=w='{W}*(1+0.05*t/{dur:.3f})':h=-2:eval=frame", f"crop={W}:{H}",
                    "fade=t=in:st=0:d=0.35"]
    final = f"noise=c0s={grano}:c0f=t+u,format=yuv420p"
    cod = ["-r", FPS, "-c:v", "libx264", "-crf", 21, "-preset", "medium", "-an", salida]
    if cita:  # la toma se desenfoca y se atenúa; la cita (con transparencia) va encima
        base = ",".join(filtros) + (f",split=2[n][m];[m]scale={W//4}:{H//4},gblur=sigma=5,scale={W}:{H}[m2];"
                                    "[n][m2]blend=all_mode=normal:all_opacity=0.7,colorlevels=romax=0.42:gomax=0.42:bomax=0.42")
        grafo = (f"[0:v]{base}[b];[1:v]{exacto},format=rgba,scale={W}:{H}[c];"
                 f"[b][c]overlay=0:0,{final}")
        ff("-ss", f"{inicio:.3f}", "-i", ruta, "-i", cita, "-filter_complex", grafo, *cod)
        return
    if texto and dur >= 0.9:
        filtros.append(rotulo(texto))
    filtros.append(final)
    ff("-ss", f"{inicio:.3f}", "-i", ruta, "-vf", ",".join(filtros), *cod)


def montar(bpm, bruto=None):
    pulso = 60.0 / bpm
    tmp = SALIDA / "_tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    fotos = sorted(CLIPS.glob("foto_*.mp4"))
    guion = list(GUION)
    if fotos:  # intercala las fotos propias en la subida y en el drop
        huecos = [i for i, g in enumerate(guion) if g[2] in (1, 2)][1::3]
        for k, i in enumerate(huecos):
            f = fotos[k % len(fotos)]
            guion[i] = (f.stem, 0.5, guion[i][2], guion[i][3], *guion[i][4:])
    lista = []
    t_acum = 0.0
    for k, (nom, inicio, pulsos, efecto, *extra) in enumerate(guion):
        ruta = CLIPS / f"{nom}.mp4"
        # duración exacta en fotogramas para no acumular deriva respecto al ritmo
        fin = round((t_acum + pulsos * pulso) * FPS) / FPS
        dur = fin - t_acum
        t_acum = fin
        inicio = min(inicio, max(duracion(ruta) - dur - 0.05, 0))
        texto = TOMAS.get(nom, ("", ""))[1]
        seg = tmp / f"{k:03d}.mp4"
        cita = None
        if extra:
            cita = CLIPS / "citas" / f"{extra[0]}.mov"
        segmento(ruta, inicio, dur, efecto, texto, seg, cita=cita)
        lista.append(seg)
        print(f"  {k:02d} {nom:<22} {pulsos} pulsos  {efecto}", flush=True)
    (tmp / "lista.txt").write_text("".join(f"file '{p.name}'\n" for p in lista))
    final = SALIDA / f"fisica_aura_{bpm}bpm.mp4"
    ff("-f", "concat", "-safe", 0, "-i", tmp / "lista.txt", "-c", "copy", "-movflags", "+faststart", final)
    print(f"  duración real: {duracion(final):.2f} s")
    shutil.rmtree(tmp)
    print(f"Montaje: {final}  ({t_acum:.2f} s, {bpm} BPM, {t_acum / pulso:.0f} pulsos)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bruto", help="carpeta con las tomas en bruto (Manim y numpy)")
    ap.add_argument("--bpm", type=int, default=120)
    ap.add_argument("--solo-montaje", action="store_true")
    a = ap.parse_args()
    CLIPS.mkdir(parents=True, exist_ok=True)
    if not a.solo_montaje:
        for nom, (tipo, _) in TOMAS.items():
            hall = glob.glob(f"{a.bruto}/**/{nom}.mp4", recursive=True)
            if not hall:
                print("falta", nom)
                continue
            etalonar(Path(hall[0]), nom, tipo)
            print("etalonado", nom, flush=True)
        (CLIPS / "citas").mkdir(exist_ok=True)
        for c in glob.glob(f"{a.bruto}/**/Cita*.mov", recursive=True):
            shutil.copy(c, CLIPS / "citas" / Path(c).name)
        for i, img in enumerate(sorted(glob.glob(str(RAIZ / "fotos" / "*.[jJpP][pPnN]*[gG]")))):
            clip_foto(Path(img), f"foto_{i + 1:02d}")
            print("foto", img, flush=True)
    montar(a.bpm)
