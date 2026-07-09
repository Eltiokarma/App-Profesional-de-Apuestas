"""Carga inicial de datos en el despliegue: baja las DBs al volumen si faltan.

Con SAD_BOOTSTRAP_URL apuntando a un zip con las 4 SQLite (sad, levels,
constants, discreto), la primera vez que arranca el contenedor las descarga a
SAD_DATA_DIR. Si sad.db ya existe (o no hay URL) no hace nada, así que es
seguro dejarlo en el arranque de siempre.

    python -m backend.bootstrap_datos && uvicorn backend.app:app …
"""
import os
import sys
import urllib.request
import zipfile


def main() -> int:
    data = os.environ.get("SAD_DATA_DIR", ".")
    url = os.environ.get("SAD_BOOTSTRAP_URL", "").strip()
    if not url or os.path.exists(os.path.join(data, "sad.db")):
        return 0
    os.makedirs(data, exist_ok=True)
    tmp = os.path.join(data, "_bootstrap.zip")
    print(f"bootstrap: descargando DBs de {url} …", flush=True)
    urllib.request.urlretrieve(url, tmp)
    with zipfile.ZipFile(tmp) as z:
        z.extractall(data)
    os.remove(tmp)
    faltan = [f for f in ("sad.db", "levels.db", "constants.db", "discreto.db") if not os.path.exists(os.path.join(data, f))]
    if faltan:
        print(f"bootstrap: el zip no traía {', '.join(faltan)}", file=sys.stderr)
        return 1
    print("bootstrap: DBs listas", flush=True)
    return 0


if __name__ == "__main__":
    sys.exit(main())
