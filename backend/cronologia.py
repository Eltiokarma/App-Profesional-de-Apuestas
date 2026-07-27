"""Cronología SAD — los partidos del timeline, calculados de NUESTRA base.

SOLO LECTURA y CERO tokens. Es el mismo recorte que ya se le hizo al bloque G
del EFE (`backend/calendario.py`), aplicado ahora al skill futbol-timeline.

Un timeline de seis meses son ~30-40 partidos POR EQUIPO. Hasta aquí el modelo
los buscaba en la web ("[Equipo] resultados [liga] [año]", "[Equipo] tabla
posiciones") y después los escribía uno por uno en el JSON de salida: fecha,
marcador, jornada, rival. Tres facturas por el mismo dato —búsqueda,
razonamiento y salida— cuando el marcador exacto ya está en `fixtures` desde la
ingesta, con su fecha y su jornada.

Aquí se calcula:

| Pieza del esquema TIMELINE | De dónde sale |
|----------------------------|---------------|
| eventos `resultado`/`derrota`/`empate` | `fixtures` terminados del período |
| `marcador` y `jornada`     | `fulltime_*` (regla de 90') y `league_round` |
| enfrentamiento directo (`equipo: "ambos"`) | el mismo fixture con los dos equipos |
| `equipos[].stats` (posición, puntos, última victoria) | la tabla del año |

Lo que NO se calcula y se sigue pagando: los eventos institucionales —crisis,
sanciones, cambios de DT, el arco narrativo—. Eso es juicio y contexto del
mundo, no una consulta a nuestra base.

La regla de 90' es la misma de todo el proyecto: `fulltime_*` manda sobre
`goals_*` (que incluye prórroga en AET/PEN).
"""
import re
from datetime import datetime, timedelta, timezone

from backend import db

VENTANA_DIAS = 182       # default del protocolo TIMELINE: últimos 6 meses
MAX_PARTIDOS = 60        # techo por equipo: un semestre no da para más
FUENTE = "sad.db (ingesta API-Football)"

_FIN = "(f.status_short IN ('FT','AET','PEN') OR f.status_long='Match Finished')"
_GH = "COALESCE(f.fulltime_home, f.goals_home)"
_GA = "COALESCE(f.fulltime_away, f.goals_away)"

_RE_JORNADA = re.compile(r"(\d+)\s*$")

TIPOS_PARTIDO = ("resultado", "derrota", "empate")


def _q(sql: str, params: tuple = ()) -> list:
    try:
        return db.query("sad", sql, params)
    except Exception:
        return []


def _jornada(ronda: str | None) -> int:
    """"Regular Season - 7" → 7. 0 cuando la ronda no numera (Final, Semis…):
    el esquema pide entero y el frontend oculta el J cuando es 0."""
    m = _RE_JORNADA.search(ronda or "")
    return int(m.group(1)) if m else 0


def ventana(hasta: str | None = None, dias: int = VENTANA_DIAS) -> tuple[str, str]:
    """(desde, hasta) en ISO. `hasta` por defecto es hoy en UTC."""
    fin = datetime.now(timezone.utc).date() if not hasta else \
        datetime.strptime(hasta[:10], "%Y-%m-%d").date()
    return (fin - timedelta(days=dias)).isoformat(), fin.isoformat()


def _partidos(team_id: int, desde: str, hasta: str) -> list[dict]:
    """Partidos terminados del equipo en el período, del más viejo al más nuevo
    (el esquema TIMELINE exige orden cronológico estricto)."""
    return _q(
        f"""SELECT f.id, f.date, f.home_team_id, f.away_team_id, f.league_round AS ronda,
                   {_GH} AS gh, {_GA} AS ga, ht.name AS local, at.name AS visitante,
                   l.name AS liga
            FROM fixtures f
            JOIN teams ht ON ht.id=f.home_team_id
            JOIN teams at ON at.id=f.away_team_id
            LEFT JOIN leagues l ON l.id=f.league_id
            WHERE (f.home_team_id=? OR f.away_team_id=?) AND {_FIN}
              AND {_GH} IS NOT NULL AND {_GA} IS NOT NULL
              AND f.date >= ? AND f.date <= ?
            ORDER BY f.date ASC LIMIT ?""",
        (team_id, team_id, desde, hasta + " 23:59:59", MAX_PARTIDOS),
    )


def _evento(fecha: str, equipo: str, tipo: str, titulo: str, detalle: str,
            jornada: int, marcador: str, destacado: bool) -> dict:
    return {"fecha": fecha, "aproximada": False, "equipo": equipo, "tipo": tipo,
            "titulo": titulo, "detalle": detalle, "jornada": jornada,
            "marcador": marcador, "destacado": destacado,
            "alerta_relacionada": "", "fuente": FUENTE}


def eventos_de(team_id: int, nombre: str, desde: str, hasta: str,
               rival_id: int | None = None) -> list[dict]:
    """Eventos de partido del equipo en el período. Los cruces contra
    `rival_id` (el otro equipo del timeline) salen como `equipo: "ambos"`, que
    es como el frontend los centra en el eje."""
    out = []
    for r in _partidos(team_id, desde, hasta):
        es_local = r["home_team_id"] == team_id
        gf, gc = (r["gh"], r["ga"]) if es_local else (r["ga"], r["gh"])
        rival = r["visitante"] if es_local else r["local"]
        fecha = (r["date"] or "")[:10]
        jornada = _jornada(r["ronda"])
        liga = r["liga"] or ""
        directo = rival_id is not None and rival_id in (r["home_team_id"], r["away_team_id"])
        if directo:
            # el cruce entre los dos equipos del timeline: uno solo, centrado
            out.append(_evento(
                fecha, "ambos", "empate" if r["gh"] == r["ga"] else "resultado",
                f"{r['local']} {r['gh']}-{r['ga']} {r['visitante']}",
                " · ".join(x for x in ["Enfrentamiento directo", liga] if x),
                jornada, f"{r['gh']}-{r['ga']}", True,
            ))
            continue
        tipo = "resultado" if gf > gc else "empate" if gf == gc else "derrota"
        verbo = {"resultado": "Victoria", "empate": "Empate", "derrota": "Derrota"}[tipo]
        out.append(_evento(
            fecha, nombre, tipo, f"{verbo} {gf}-{gc} ante {rival}",
            " · ".join(x for x in [("Local" if es_local else "Visitante"), liga] if x),
            jornada, f"{gf}-{gc}", False,
        ))
    return out


def eventos_del_partido(home_id: int, home_nombre: str, away_id: int, away_nombre: str,
                        desde: str, hasta: str) -> list[dict]:
    """Los eventos de partido de AMBOS equipos, ya en orden cronológico y sin
    duplicar el enfrentamiento directo (que aparecería en las dos listas)."""
    eventos = eventos_de(home_id, home_nombre, desde, hasta, rival_id=away_id)
    vistos = {(e["fecha"], e["marcador"]) for e in eventos if e["equipo"] == "ambos"}
    for e in eventos_de(away_id, away_nombre, desde, hasta, rival_id=home_id):
        if e["equipo"] == "ambos" and (e["fecha"], e["marcador"]) in vistos:
            continue
        eventos.append(e)
    return ordenar(eventos)


def ordenar(eventos: list[dict]) -> list[dict]:
    """Orden cronológico estricto, tolerante a las fechas aproximadas del
    modelo ("~2026-03" ordena al principio de su mes, que es lo honesto: no
    sabemos el día)."""
    return sorted(eventos, key=lambda e: str(e.get("fecha", "")).lstrip("~"))


def stats_de(team_id: int, liga_id: int | None, temporada: int | None,
             desde: str | None = None, hasta: str | None = None) -> dict:
    """`equipos[].stats` del esquema TIMELINE: posición y puntos de la tabla
    del año, y la última victoria del período. Todo de sad.db."""
    stats = {"posicion": 0, "puntos": 0, "ultima_victoria": "", "otros": []}
    if liga_id and temporada:
        try:
            from backend.app import standings
            for fila in standings(liga_id, temporada):
                if fila.get("equipoId") == team_id:
                    stats["posicion"] = int(fila.get("posicion") or 0)
                    stats["puntos"] = int(fila.get("puntos") or 0)
                    break
        except Exception:
            pass
    d, h = (desde, hasta) if desde and hasta else ventana()
    for r in reversed(_partidos(team_id, d, h)):
        es_local = r["home_team_id"] == team_id
        gf, gc = (r["gh"], r["ga"]) if es_local else (r["ga"], r["gh"])
        if gf > gc:
            rival = r["visitante"] if es_local else r["local"]
            stats["ultima_victoria"] = f"{(r['date'] or '')[:10]} {gf}-{gc} vs {rival}"
            break
    return stats


# ── lo que se le dice al modelo ──────────────────────────────────────────────

ORDEN_PARA_SKILLS = (
    "NO busques ni escribas los eventos de partido (tipo resultado/derrota/empate) ni "
    "`equipos[].stats`: los calculamos de nuestra base con el marcador exacto, la jornada y "
    "el enfrentamiento directo, y los insertamos después de tu respuesta. Devuelve `eventos` "
    "SOLO con lo institucional (institucional, tecnico, sancion, hito) y deja `stats` en 0/\"\". "
    "Copiar partidos que ya tenemos solo gastaría tokens. Usa el resumen de resultados de "
    "`datos_cacheados` para la narrativa y para decidir qué hito merece contarse."
)


def resumen_para_skills(eventos: list[dict], nombre: str) -> str:
    """Una línea con el balance del período para que el modelo escriba la
    narrativa sin recibir los 40 eventos de vuelta como entrada."""
    suyos = [e for e in eventos if e["equipo"] == nombre]
    if not suyos:
        return ""  # un equipo sin partidos no tiene balance que resumir
    g = sum(e["tipo"] == "resultado" for e in suyos)
    e_ = sum(e["tipo"] == "empate" for e in suyos)
    p = sum(e["tipo"] == "derrota" for e in suyos)
    # el cruce directo se muestra (es contexto), pero no se le atribuye a un lado
    propios = [e for e in eventos if e["equipo"] in (nombre, "ambos")]
    ultimos = " · ".join(f"{e['fecha']} {e['titulo']}" for e in propios[-5:])
    return (f"{g}G {e_}E {p}D en el período (calculado, ya insertado en el timeline). "
            f"Últimos: {ultimos}")
