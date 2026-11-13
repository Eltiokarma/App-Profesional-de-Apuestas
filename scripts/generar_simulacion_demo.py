"""Regenera `src/data/simulacionDemo.ts` con la MISMA cuenta del backend.

    python scripts/generar_simulacion_demo.py

La demo de la pantalla Simulación no tiene copia de la cuenta en TS: sale de
`backend.analisis.simulacion.simular` sobre apuestas inventadas (estas). Cada
apuesta lleva su marcador declarado, las espinas del parte y su semáforo
calculado con `backend.analisis.semaforo` (por las espinas desde el
13/11/2026); las del 13/11 en adelante son las que cuentan para el criterio.
"""
from __future__ import annotations

import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault("SAD_SIN_HILOS", "1")

from backend.analisis import semaforo as sem  # noqa: E402
from backend.analisis import simulacion as sim  # noqa: E402

# (fixture, pitazo UTC, local, visita, liga, depositado, 1X2 nuestro, cuotas, mercado sin margen, resultado, marcador,
#  espinas del parte (a, b))
APUESTAS = [
    (900001, "2026-10-28 15:00:00", "Real Betis", "Sevilla FC", "LaLiga", "2026-10-28 09:58:00",
     (48.0, 28.0, 24.0), (2.05, 3.4, 3.9), (47.0, 28.3, 24.7), "local", "2-1", ("positiva", "negativa")),
    (900002, "2026-10-28 15:00:00", "Arsenal", "Tottenham", "Premier League", "2026-10-28 10:10:00",
     (62.0, 22.0, 16.0), (1.62, 4.1, 5.4), (59.0, 23.3, 17.7), "empate", "2-0", ("positiva", "cero")),
    (900003, "2026-10-28 19:45:00", "Inter", "Milan", "Serie A", "2026-10-28 14:55:00",
     (52.0, 27.0, 21.0), (2.0, 3.5, 4.0), (48.3, 27.6, 24.1), "local", "1-1", ("positiva", "negativa")),
    (900004, "2026-10-28 20:00:00", "Atlético", "Villarreal", "LaLiga", "2026-10-28 15:02:00",
     (55.0, 27.0, 18.0), (1.75, 3.7, 5.0), (54.9, 25.9, 19.2), "visita", "1-0", ("positiva", "positiva")),
    (900005, "2026-10-29 19:30:00", "Liverpool", "Chelsea", "Premier League", "2026-10-29 09:55:00",
     (60.0, 22.0, 18.0), (1.75, 3.9, 4.6), (54.7, 24.5, 20.8), "local", "2-1", ("positiva", "negativa")),
    (900006, "2026-10-29 20:00:00", "Real Madrid", "Barcelona", "LaLiga", "2026-10-29 15:01:00",
     (40.0, 26.0, 34.0), (2.2, 3.7, 3.2), (43.8, 26.1, 30.1), "local", "2-2", ("cero", "positiva")),
    (900007, "2026-11-11 19:00:00", "Bayern", "Dortmund", "Bundesliga", "2026-11-11 12:05:00",
     (58.0, 22.0, 20.0), (1.68, 4.2, 4.6), (57.2, 22.9, 19.9), "local", "2-1", ("positiva", "negativa")),
    (900008, "2026-11-11 21:00:00", "PSG", "Marseille", "Ligue 1", "2026-11-11 12:20:00",
     (63.0, 20.0, 17.0), (1.52, 4.4, 6.0), (63.4, 21.3, 15.3), "empate", "3-1", ("positiva", "negativa")),
    (900009, "2026-11-12 01:00:00", "Alianza Lima", "Universitario", "Liga 1", "2026-11-11 15:40:00",
     (38.0, 31.0, 31.0), (2.6, 3.0, 3.0), (35.9, 32.0, 32.1), "visita", "1-0", ("negativa", "positiva")),
    (900012, "2026-11-13 19:45:00", "Benfica", "Porto", "Liga Portugal", "2026-11-13 12:10:00",
     (46.0, 27.0, 27.0), (2.1, 3.4, 3.6), (45.6, 28.2, 26.2), "local", "2-1", ("positiva", "negativa")),
    (900013, "2026-11-13 21:00:00", "Juventus", "Lazio", "Serie A", "2026-11-13 12:30:00",
     (50.0, 28.0, 22.0), (1.95, 3.4, 4.2), (49.5, 28.4, 22.1), "empate", "1-0", ("negativa", "positiva")),
    (900011, "2026-11-12 20:00:00", "Napoli", "Roma", "Serie A", "2026-11-12 10:30:00",
     (47.0, 28.0, 25.0), (2.05, 3.35, 3.9), (46.4, 28.4, 24.4), None, "1-0", ("positiva", "negativa")),
]
EXCLUIDOS = [{"fixtureId": 900010, "pitazo": "2026-10-28 23:00:00",
              "partido": {"local": "Villarreal", "visita": "Real Betis", "liga": "LaLiga"},
              "motivo": "sin las tres cuotas del 1X2 capturadas"}]


def armar() -> list[dict]:
    out = []
    for fid, pit, loc, vis, liga, dep, p, c, m, res, marcador, (ea, eb) in APUESTAS:
        probs = dict(zip(sim.CLAVES, p))
        mercado = dict(zip(sim.CLAVES, m))
        out.append({
            "fixtureId": fid, "pitazo": pit, "partido": {"local": loc, "visita": vis, "liga": liga},
            "depositadoEn": dep, "versiones": {s: sim.version_al(s, dep) for s in sim.SKILLS},
            "versionPrompt": "v2.5", "probabilidades": probs, "cuotas": dict(zip(sim.CLAVES, c)),
            "mercado": mercado, "resultado": res,
            "semaforo": sem.semaforo(probs, {"a": ea, "b": eb}, mercado, marcador),
        })
    return out


def main() -> None:
    out = sim.simular(armar())
    out["excluidos"] = EXCLUIDOS
    out["nota"] = "DEMO: apuestas inventadas para ver la pantalla; en producción salen de los partes depositados"
    destino = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "src", "data",
                           "simulacionDemo.ts")
    with open(destino, "w", encoding="utf-8") as f:
        f.write("// Generado con backend.analisis.simulacion.simular sobre apuestas inventadas:\n"
                "// la demo usa la MISMA cuenta que el backend (no una copia en TS).\n"
                "// Se rehace con: python scripts/generar_simulacion_demo.py\n"
                "import type { SimulacionApuesta } from '../api/types'\n\n"
                "export const SIMULACION_DEMO: SimulacionApuesta = "
                + json.dumps(out, ensure_ascii=False, indent=1) + "\n")
    print(f"escrita {destino}: {len(out['apuestas'])} apuestas, semáforo {out['semaforo']['criterio']['texto']}")


if __name__ == "__main__":
    main()
