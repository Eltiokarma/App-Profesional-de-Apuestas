"""Corrida diaria de ingesta: extractor (ventana hoy−3d..+10d) + pipeline.

Pensada para el despliegue con un solo servicio (SAD_DATA_DIR = volumen con
las 4 DBs) y utilizable igual en local:

    python -m backend.ingesta.corrida_diaria

Corre en subprocesos con cwd en SAD_DATA_DIR para que el marcador de cuota
(.extractor_cuota.json) persista junto a las DBs. Si el extractor falla
(p. ej. cuota agotada), el pipeline corre igual con lo que haya en sad.db.
"""
import os
import subprocess
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def main() -> int:
    data = os.environ.get("SAD_DATA_DIR", RAIZ)
    # PYTHONUNBUFFERED: el stdout de los subprocesos es un pipe (Railway); sin
    # esto los prints quedan retenidos en el buffer hasta que el proceso muere.
    env = {**os.environ, "PYTHONPATH": RAIZ, "PYTHONUTF8": "1", "PYTHONUNBUFFERED": "1"}
    ext = subprocess.run([sys.executable, "-m", "backend.ingesta.extractor"], cwd=data, env=env)
    if ext.returncode != 0:
        print(f"extractor terminó con código {ext.returncode}; el pipeline corre igual", file=sys.stderr)
    # jugadores (docs/JUGADORES.md): plantillas/bajas/traspasos/DT de los
    # equipos con NS próximos — mismo presupuesto compartido, TTL 7 días
    jug = subprocess.run([sys.executable, "-m", "backend.ingesta.jugadores"], cwd=data, env=env)
    if jug.returncode != 0:
        print(f"ingesta de jugadores terminó con código {jug.returncode}; el pipeline corre igual",
              file=sys.stderr)
    pipe = subprocess.run([sys.executable, "-m", "backend.ingesta.pipeline", "--out", "."], cwd=data, env=env)
    return pipe.returncode


if __name__ == "__main__":
    sys.exit(main())
