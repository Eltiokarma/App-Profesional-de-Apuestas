"""Qué veredictos llevan el reporte de la PRENSA (13/11/2026, pedido del usuario).

Buscar la crónica en internet cuesta: medido el 13/11 sobre 8 partidos de la
Nations League, ~1,15 M tokens leídos de caché, ~59 mil nuevos y ~9 mil de
salida por partido, con 4-8 búsquedas y 2-6 páginas. En un domingo de 50
partidos de liga eso es un tercio más de corrida, y la mitad de esos partidos
no tiene crónica con detalle. Por eso la búsqueda no va a todos: el backend
elige, con datos, y el modelo no decide.

La regla (usuario, 13/11/2026):

1. Los partidos IMPORTANTES entran siempre:
   - selecciones: todo torneo oficial (amistosos, no);
   - torneos internacionales de clubes (Champions, Europa League, Conference,
     Libertadores, Sudamericana): desde las eliminatorias, y la ÚLTIMA fecha de
     la fase de liga de la Champions (a veces define);
   - ligas nacionales: solo las fases decisivas (playoffs, liguilla,
     cuadrangulares, ronda por el título o el descenso, semifinales, final);
   - copas nacionales: solo la final.
2. Después, hasta llegar al 50 % de los partidos de ESE día (redondeando para
   arriba), los que el 1X2 PERDIÓ, el más confiado primero: es donde la
   crónica enseña más.
3. Si los perdidos no alcanzan, completan los acertados con menos
   confianza, y al final los que no tenían 1X2 declarado.

El veredicto corre muchas horas después del partido justamente para que la
crónica ya esté publicada.
"""
from __future__ import annotations

import math
import re

# torneos internacionales de clubes que cuentan (Mundial de Clubes = 15)
TOP_CLUBES = {2, 3, 848, 13, 11, 15}
CHAMPIONS = 2
# la fase de liga de la Champions tiene 8 fechas desde 2024-25
CHAMPIONS_ULTIMA_FECHA_LIGA = re.compile(r"^League Stage - 8$", re.I)
AMISTOSOS_SELECCIONES = 10

_PREVIA = re.compile(r"qualif|preliminary", re.I)
_ELIMINATORIA = re.compile(r"round of|quarter|semi|final|play-?off|knockout", re.I)
# fases decisivas de una liga (la API escribe «Apertura - Quarter-finals»,
# «Championship Round - 3», «Relegation Round», «Clausura - Quadrangulars»…)
_DECISIVA_LIGA = re.compile(r"play-?off|quarter|semi|final|liguilla|quadrangular|cuadrangular|"
                            r"championship round|relegation|promotion|knockout|round of", re.I)
_FINAL = re.compile(r"(^|- )finals?$", re.I)

CUPO = 0.5


def importancia(liga_id: int | None, ronda: str | None, *, selecciones: set[int],
                copa_nacional: bool) -> str:
    """El motivo por el que el partido es IMPORTANTE, o "" si no lo es."""
    ronda = (ronda or "").strip()
    if liga_id in selecciones:
        return "" if liga_id == AMISTOSOS_SELECCIONES else "selecciones: torneo oficial"
    if liga_id in TOP_CLUBES:
        if _PREVIA.search(ronda):
            return ""
        if liga_id == CHAMPIONS and CHAMPIONS_ULTIMA_FECHA_LIGA.match(ronda):
            return "Champions: última fecha de la fase de liga"
        return f"internacional de clubes: {ronda}" if _ELIMINATORIA.search(ronda) else ""
    if copa_nacional:
        return "copa nacional: final" if _FINAL.search(ronda) else ""
    return f"liga: fase decisiva ({ronda})" if _DECISIVA_LIGA.search(ronda) else ""


def marcar(pendientes: list[dict]) -> None:
    """Pone `prensa` (bool) y `prensaMotivo` en cada pendiente, en el lugar.

    Cada pendiente trae `fecha`, `importante` (motivo o "") y `unXDos`
    ({acerto: bool|None, probabilidad: float}). El cupo se cuenta por día."""
    por_dia: dict[str, list[dict]] = {}
    for p in pendientes:
        por_dia.setdefault(p.get("fecha") or "", []).append(p)
    for dia in por_dia.values():
        cupo = math.ceil(len(dia) * CUPO)

        def orden(p: dict) -> tuple:
            ux = p.get("unXDos") or {}
            acerto, prob = ux.get("acerto"), float(ux.get("probabilidad") or 0)
            if acerto is False:
                return (0, -prob)          # perdidos: el más confiado primero
            if acerto is True:
                return (1, prob)           # acertados: el menos confiado primero
            return (2, 0.0)                # sin 1X2 declarado

        elegidos = 0
        for p in dia:
            if p.get("importante"):
                p["prensa"], p["prensaMotivo"] = True, p["importante"]
                elegidos += 1
        for p in sorted((p for p in dia if not p.get("importante")), key=orden):
            if elegidos >= cupo:
                p["prensa"], p["prensaMotivo"] = False, f"fuera del 50 % del día ({cupo} de {len(dia)})"
                continue
            acerto = (p.get("unXDos") or {}).get("acerto")
            p["prensa"] = True
            p["prensaMotivo"] = ("el 1X2 perdió" if acerto is False else
                                 "completa el 50 %: 1X2 acertado con poca confianza" if acerto else
                                 "completa el 50 %: sin 1X2 declarado")
            elegidos += 1
