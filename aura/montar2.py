"""Segundo edit «Física con aura»: termodinámica, nanomagnetismo, partículas, astrofísica,
giróscopos y fasores. Más rápido que el primero, con transiciones nuevas y solo dos citas.

Reutiliza el etalonaje de montar.py. Salida:
    videos/aura2/fisica_aura2_<BPM>bpm.mp4   y   videos/aura2/clips/
Uso:
    python montar2.py --bruto DIR_TOMAS [--bpm 120] [--solo-montaje]
"""

import argparse
import glob
import shutil
from pathlib import Path

import montar as M

RAIZ = Path(__file__).resolve().parent
SALIDA = RAIZ.parent / "videos" / "aura2"
CLIPS = SALIDA / "clips"
W, H, FPS = M.W, M.H, M.FPS
FUENTE = "/usr/share/fonts/opentype/inter/Inter-Light.otf"

TOMAS = {
    "Titulo2": ("vector", ""), "AdAstra": ("vector", ""),
    "MaxwellBoltzmann": ("vector", "TERMODINÁMICA"), "Carnot": ("vector", "TERMODINÁMICA"),
    "Entropia": ("vector", "TERMODINÁMICA"),
    "PrecesionEspin": ("vector", "NANOMAGNETISMO"), "Histeresis": ("vector", "NANOMAGNETISMO"),
    "CamaraBurbujas": ("vector", "FÍSICA DE PARTÍCULAS"), "DiagramaFeynman": ("vector", "ELECTRODINÁMICA CUÁNTICA"),
    "Higgs": ("vector", "MECANISMO DE HIGGS"),
    "OndasGravitatorias": ("vector", "ONDAS GRAVITACIONALES"), "Pulsar": ("vector", "PÚLSAR"),
    "Hubble": ("vector", "COSMOLOGÍA"), "DiagramaHR": ("vector", "ASTROFÍSICA ESTELAR"),
    "Giroscopio": ("vector", "GIRÓSCOPO"), "FasoresRLC": ("vector", "FASORES"), "Trifasica": ("vector", "CORRIENTE TRIFÁSICA"),
    "skyrmiones": ("luz", "SKYRMIONES"), "galaxia": ("luz", "GALAXIA ESPIRAL"), "gargantua": ("luz", "AGUJERO NEGRO"),
    "nebulosa": ("luz", "NEBULOSA"), "rayo": ("luz", "DESCARGA ELÉCTRICA"),
}

# (toma, segundo de inicio, pulsos, efecto, opciones)
#   efectos: suave, corte, flash, barrido, glitch, sacudida, invertir, zoom
#   opciones: {"cita": nombre} superpone una cita; {"vel": 1.6} acelera la toma
GUION = [
    ("Titulo2", 0.1, 4, "suave", {}),
    ("Entropia", 0.0, 10, "suave", {"cita": "CitaEddington"}),
    # subida
    ("MaxwellBoltzmann", 2.2, 2, "barrido", {"vel": 1.3}),
    ("Carnot", 1.2, 2, "zoom", {}),
    ("nebulosa", 1.0, 2, "barrido", {}),
    ("PrecesionEspin", 1.0, 2, "flash", {"vel": 1.4}),
    ("skyrmiones", 0.5, 2, "glitch", {}),
    ("Histeresis", 1.6, 2, "barrido", {"vel": 1.5}),
    ("rayo", 1.2, 2, "invertir", {}),
    ("FasoresRLC", 1.0, 2, "corte", {"vel": 1.3}),
    ("Trifasica", 1.0, 2, "barrido", {}),
    ("Giroscopio", 1.0, 2, "zoom", {}),
    ("CamaraBurbujas", 2.4, 2, "flash", {}),
    # drop: un pulso por plano, varios acelerados
    ("DiagramaFeynman", 2.4, 1, "flash", {}),
    ("Higgs", 2.6, 1, "glitch", {"vel": 1.5}),
    ("galaxia", 1.5, 1, "flash", {}),
    ("gargantua", 1.5, 1, "sacudida", {}),
    ("Pulsar", 2.0, 1, "flash", {"vel": 1.6}),
    ("OndasGravitatorias", 3.0, 1, "invertir", {}),
    ("Hubble", 3.0, 1, "flash", {}),
    ("DiagramaHR", 3.2, 1, "barrido", {}),
    ("skyrmiones", 2.5, 1, "glitch", {}),
    ("rayo", 1.9, 1, "flash", {}),
    ("MaxwellBoltzmann", 3.8, 1, "zoom", {}),
    ("Carnot", 3.6, 1, "flash", {}),
    ("nebulosa", 2.5, 1, "barrido", {}),
    ("PrecesionEspin", 3.5, 1, "flash", {"vel": 1.6}),
    ("gargantua", 3.0, 1, "sacudida", {}),
    ("galaxia", 3.0, 1, "invertir", {}),
    # tartamudeo de medio pulso
    ("gargantua", 2.0, 0.5, "flash", {}), ("rayo", 2.0, 0.5, "invertir", {}),
    ("galaxia", 2.0, 0.5, "flash", {}), ("Pulsar", 3.0, 0.5, "glitch", {}),
    ("gargantua", 2.5, 0.5, "flash", {}), ("rayo", 2.2, 0.5, "invertir", {}),
    ("galaxia", 2.5, 0.5, "flash", {}), ("Pulsar", 3.5, 0.5, "glitch", {}),
    # final
    ("OndasGravitatorias", 2.4, 6, "corte", {}),
    ("gargantua", 0.0, 10, "zoom", {"cita": "CitaSaganEstrellas"}),
    ("AdAstra", 0.0, 8, "suave", {}),
]


def rotulo(texto):
    t = "  ".join(texto).replace(":", r"\:")
    return (f"drawbox=x=80:y=ih*0.118:w=26:h=2:color=white@0.8:t=fill,"
            f"drawtext=fontfile={FUENTE}:text='{t}':fontsize=27:fontcolor=white@0.85:x=124:y=h*0.111:alpha='min(1,t*8)'")


def entrada(efecto, dur):
    """Filtros de entrada del plano (todos terminan en W x H)."""
    if efecto == "flash":
        return [f"scale=w='{W}*(1+0.14*exp(-t*14))':h=-2:eval=frame", f"crop={W}:{H}",
                "rgbashift=rh=-10:bh=10:enable='lt(t,0.10)'", "fade=t=in:st=0:d=0.12:color=white"]
    if efecto == "corte":
        return [f"scale=w='{W}*(1+0.06*exp(-t*10))':h=-2:eval=frame", f"crop={W}:{H}"]
    if efecto == "zoom":  # entra desde muy cerca y desenfocado
        return [f"scale=w='{W}*(1+0.45*exp(-t*16))':h=-2:eval=frame", f"crop={W}:{H}",
                "gblur=sigma=14:enable='lt(t,0.06)'", "gblur=sigma=6:enable='between(t,0.06,0.13)'"]
    if efecto == "glitch":
        return [f"scale={int(W*1.05)}:-2", f"crop={W}:{H}:x='(iw-{W})/2+30*sin(t*95)*lt(t,0.16)':y='(ih-{H})/2'",
                "rgbashift=rh=-34:gv=12:bh=26:enable='lt(t,0.16)'", "noise=alls=70:allf=t:enable='lt(t,0.12)'"]
    if efecto == "sacudida":
        return [f"scale={int(W*1.08)}:-2",
                f"crop={W}:{H}:x='(iw-{W})/2+26*sin(t*63)*exp(-t*7)':y='(ih-{H})/2+22*cos(t*51)*exp(-t*7)'",
                "fade=t=in:st=0:d=0.06:color=white"]
    if efecto == "invertir":
        return [f"scale=w='{W}*(1+0.1*exp(-t*12))':h=-2:eval=frame", f"crop={W}:{H}",
                "negate=enable='lt(t,0.05)'"]
    if efecto == "barrido":  # se resuelve en el grafo (necesita lienzo)
        return [f"scale={W}:{H}", "gblur=sigma=45:sigmaV=0.01:enable='lt(t,0.13)'"]
    return [f"scale=w='{W}*(1+0.05*t/{dur:.3f})':h=-2:eval=frame", f"crop={W}:{H}", "fade=t=in:st=0:d=0.35"]


def segmento(ruta, inicio, dur, efecto, texto, salida, cita=None, vel=1.0, grano=9):
    exacto = f"setpts=PTS/{vel},fps={FPS},tpad=stop_mode=clone:stop_duration=4,trim=duration={dur:.4f},setpts=PTS-STARTPTS"
    cadena = ",".join([exacto] + entrada(efecto, dur))
    final = f"noise=c0s={grano}:c0f=t+u,format=yuv420p"
    cod = ["-r", FPS, "-c:v", "libx264", "-crf", 20, "-preset", "medium", "-an", salida]
    if efecto == "barrido":
        cadena = (f"color=black:s={W}x{H}:r={FPS}:d={dur:.4f}[lienzo];[0:v]{cadena}[v];"
                  f"[lienzo][v]overlay=x='{W}*pow(max(0,1-t/0.14),2)':y=0:shortest=1")
    else:
        cadena = f"[0:v]{cadena}"
    if cita:
        grafo = (f"{cadena},split=2[n][m];[m]scale={W//4}:{H//4},gblur=sigma=5,scale={W}:{H}[m2];"
                 "[n][m2]blend=all_mode=normal:all_opacity=0.7,colorlevels=romax=0.42:gomax=0.42:bomax=0.42[b];"
                 f"[1:v]tpad=stop_mode=clone:stop_duration=3,trim=duration={dur:.4f},setpts=PTS-STARTPTS,format=rgba,scale={W}:{H}[c];"
                 f"[b][c]overlay=0:0,{final}")
        M.ff("-ss", f"{inicio:.3f}", "-i", ruta, "-i", cita, "-filter_complex", grafo, *cod)
        return
    if texto and dur >= 0.9:
        cadena += "," + rotulo(texto)
    M.ff("-ss", f"{inicio:.3f}", "-i", ruta, "-filter_complex", f"{cadena},{final}", *cod)


def montar(bpm):
    pulso = 60.0 / bpm
    tmp = SALIDA / "_tmp"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    fotos = sorted(CLIPS.glob("foto_*.mp4"))
    guion = list(GUION)
    if fotos:
        huecos = [i for i, g in enumerate(guion) if g[2] in (1, 2)][1::3]
        for k, i in enumerate(huecos):
            guion[i] = (fotos[k % len(fotos)].stem, 0.5, *guion[i][2:])
    lista, t_acum = [], 0.0
    for k, (nom, inicio, pulsos, efecto, op) in enumerate(guion):
        ruta = CLIPS / f"{nom}.mp4"
        fin = round((t_acum + pulsos * pulso) * FPS) / FPS
        dur, t_acum = fin - t_acum, fin
        cita = CLIPS / "citas" / f"{op['cita']}.mov" if "cita" in op else None
        seg = tmp / f"{k:03d}.mp4"
        segmento(ruta, inicio, dur, efecto, TOMAS.get(nom, ("", ""))[1], seg, cita=cita, vel=op.get("vel", 1.0))
        lista.append(seg)
        print(f"  {k:02d} {nom:<20} {pulsos:>4} pulsos  {efecto}", flush=True)
    (tmp / "lista.txt").write_text("".join(f"file '{p.name}'\n" for p in lista))
    final = SALIDA / f"fisica_aura2_{bpm}bpm.mp4"
    M.ff("-f", "concat", "-safe", 0, "-i", tmp / "lista.txt", "-c", "copy", "-movflags", "+faststart", final)
    shutil.rmtree(tmp)
    print(f"Montaje: {final}  ({M.duracion(final):.2f} s, {bpm} BPM, {t_acum / pulso:.1f} pulsos)")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--bruto")
    ap.add_argument("--bpm", type=int, default=120)
    ap.add_argument("--solo-montaje", action="store_true")
    a = ap.parse_args()
    CLIPS.mkdir(parents=True, exist_ok=True)
    M.CLIPS = CLIPS
    if not a.solo_montaje:
        for nom, (tipo, _) in TOMAS.items():
            hall = glob.glob(f"{a.bruto}/**/{nom}.mp4", recursive=True)
            if not hall:
                print("falta", nom)
                continue
            M.etalonar(Path(hall[0]), nom, tipo)
            print("etalonado", nom, flush=True)
        (CLIPS / "citas").mkdir(exist_ok=True)
        for c in glob.glob(f"{a.bruto}/**/Cita*.mov", recursive=True):
            shutil.copy(c, CLIPS / "citas" / Path(c).name)
        for i, img in enumerate(sorted(glob.glob(str(RAIZ / "fotos" / "*.[jJpP][pPnN]*[gG]")))):
            M.clip_foto(Path(img), f"foto_{i + 1:02d}")
    montar(a.bpm)
