"""Calendario SAD — el mapa de rivales del bloque G, calculado de NUESTRA base.

SOLO LECTURA y CERO tokens. El protocolo EFE (bloque G2) define siete etiquetas
contextuales con criterio numérico explícito, y seis se pueden calcular con lo
que ya está en sad.db — pagarle a un modelo por buscarlas en la web era pagar
por un dato propio:

| Etiqueta            | Criterio del protocolo                        | De dónde sale |
|---------------------|-----------------------------------------------|---------------|
| 🆕 RECIÉN ASCENDIDO | ascendió en la última temporada               | primera temporada del club en esa liga en nuestro histórico |
| 🔥 EQUIPO SORPRESA  | rinde por encima de su expectativa            | el gap §5 del motor (forma reciente vs μ esperada) |
| 🏠 LOCAL FUERTE     | ≥70% de victorias como local                  | cuenta de sus partidos en casa |
| ✈️ VISITA DÉBIL     | <25% de victorias como visitante              | cuenta de sus partidos fuera |
| 📉 EN CRISIS        | 3+ derrotas seguidas o cambio de DT en 4 sem. | resultados + tabla `entrenadores` |
| 🛡️ BLOQUE BAJO      | esquema con 5 defensores                      | formación dominante en `alineaciones` (fase A del DTP) |
| ⚔️ CLÁSICO          | rivalidad histórica documentada               | PARCIAL: solo derbi de ciudad (mismo `venue_city`) |

Cada etiqueta viaja con el DATO que la sostiene ("3 derrotas seguidas",
"78% en casa"): sin el número es una opinión, y una opinión no debería costar
ni un token ni entrar en un análisis.

`CLASICO` es el único que se queda a medias: una rivalidad nacional sin
vecindad geográfica (Boca–River es de ciudad, pero Alianza–Cienciano no) no
está en los datos. Se marca `parcial: true` para que quien lo lea sepa que ahí
la ausencia de etiqueta no prueba nada.
"""
from datetime import datetime, timedelta, timezone
from functools import lru_cache

from backend import db

PROXIMOS_DEFAULT = 4
FORMA_N = 5              # ventana de forma reciente (misma que el gap §5)
CRISIS_DERROTAS = 3      # criterio G2
CRISIS_DT_DIAS = 28      # "cambió de DT en las últimas 4 semanas"
LOCAL_FUERTE_PCT = 0.70
VISITA_DEBIL_PCT = 0.25
MIN_PARTIDOS_PCT = 4     # sin muestra no se etiqueta (un 100% de 1 partido no dice nada)
SORPRESA_GAP = -0.35     # gap = μ esperada − forma real: negativo = sobrerrinde

_FIN = "(f.status_short IN ('FT','AET','PEN') OR f.status_long='Match Finished')"
_GH = "COALESCE(f.fulltime_home, f.goals_home)"
_GA = "COALESCE(f.fulltime_away, f.goals_away)"


def _hora() -> int:
    return int(datetime.now(timezone.utc).timestamp() // 3600)


def _q(sql: str, params: tuple = ()) -> list:
    try:
        return db.query("sad", sql, params)
    except Exception:
        return []


# ── piezas por rival (todas de sad.db) ──────────────────────────────────────

def _resultados(team_id: int, limite: int = 10) -> list[dict]:
    """Últimos partidos terminados, del más reciente al más viejo."""
    filas = _q(
        f"""SELECT f.date, f.home_team_id, {_GH} AS gh, {_GA} AS ga, f.league_id, f.league_season
            FROM fixtures f
            WHERE (f.home_team_id=? OR f.away_team_id=?) AND {_FIN}
              AND {_GH} IS NOT NULL AND {_GA} IS NOT NULL
            ORDER BY f.date DESC LIMIT ?""",
        (team_id, team_id, limite),
    )
    out = []
    for r in filas:
        es_local = r["home_team_id"] == team_id
        gf, gc = (r["gh"], r["ga"]) if es_local else (r["ga"], r["gh"])
        out.append({"fecha": r["date"], "esLocal": es_local, "gf": gf, "gc": gc,
                    "res": 1 if gf > gc else 0 if gf == gc else -1,
                    "ligaId": r["league_id"], "temporada": r["league_season"]})
    return out


def _derrotas_seguidas(res: list[dict]) -> int:
    n = 0
    for r in res:
        if r["res"] == -1:
            n += 1
        else:
            break
    return n


def _sin_ganar(res: list[dict]) -> int:
    n = 0
    for r in res:
        if r["res"] != 1:
            n += 1
        else:
            break
    return n


def _pct_condicion(team_id: int, liga_id: int | None, temporada: int | None, local: bool) -> tuple[int, int]:
    """(victorias, jugados) del equipo en esa condición y temporada."""
    if liga_id is None or temporada is None:
        return 0, 0
    lado = "home_team_id" if local else "away_team_id"
    filas = _q(
        f"""SELECT {_GH} AS gh, {_GA} AS ga FROM fixtures f
            WHERE f.{lado}=? AND f.league_id=? AND f.league_season=? AND {_FIN}
              AND {_GH} IS NOT NULL AND {_GA} IS NOT NULL""",
        (team_id, liga_id, temporada),
    )
    ganados = sum(1 for r in filas if (r["gh"] > r["ga"]) == local and r["gh"] != r["ga"])
    return ganados, len(filas)


def _dt_reciente(team_id: int) -> str | None:
    """Fecha de asunción del DT si cambió hace poco (tabla de la capa de
    jugadores). None si no hay ingesta o el DT lleva tiempo."""
    filas = _q("SELECT desde FROM entrenadores WHERE team_id=? AND desde IS NOT NULL "
               "ORDER BY desde DESC LIMIT 1", (team_id,))
    if not filas or not filas[0]["desde"]:
        return None
    try:
        desde = datetime.strptime(str(filas[0]["desde"])[:10], "%Y-%m-%d").replace(tzinfo=timezone.utc)
    except ValueError:
        return None
    dias = (datetime.now(timezone.utc) - desde).days
    return str(filas[0]["desde"])[:10] if 0 <= dias <= CRISIS_DT_DIAS else None


def _formacion_dominante(team_id: int) -> str | None:
    """La formación más repetida en sus últimas alineaciones capturadas."""
    filas = _q(
        """SELECT a.formacion, COUNT(*) AS n FROM alineaciones a
           JOIN fixtures f ON f.id = a.fixture_id
           WHERE a.team_id=? AND a.formacion IS NOT NULL AND a.titular=1
           GROUP BY a.fixture_id, a.formacion ORDER BY f.date DESC LIMIT 5""",
        (team_id,),
    )
    if not filas:
        return None
    conteo: dict[str, int] = {}
    for r in filas:
        conteo[r["formacion"]] = conteo.get(r["formacion"], 0) + 1
    return max(conteo, key=lambda k: conteo[k])


def _es_ascendido(team_id: int, liga_id: int | None, temporada: int | None) -> bool:
    """Sin partidos en ESA liga la temporada anterior, pero sí en el histórico:
    subió de categoría. (Un equipo que nunca vimos no se etiqueta: sería un
    falso positivo de nuestra propia falta de datos.)"""
    if liga_id is None or temporada is None:
        return False
    previos = _q(
        "SELECT COUNT(*) AS n FROM fixtures WHERE (home_team_id=? OR away_team_id=?) "
        "AND league_id=? AND league_season=?",
        (team_id, team_id, liga_id, temporada - 1),
    )
    if previos and previos[0]["n"]:
        return False
    historia = _q(
        "SELECT COUNT(*) AS n FROM fixtures WHERE (home_team_id=? OR away_team_id=?) "
        "AND league_season < ?",
        (team_id, team_id, temporada),
    )
    return bool(historia and historia[0]["n"])


def _ciudad(team_id: int) -> str | None:
    filas = _q("SELECT venue_city, COUNT(*) AS n FROM fixtures WHERE home_team_id=? "
               "AND venue_city IS NOT NULL AND venue_city<>'' "
               "GROUP BY venue_city ORDER BY n DESC LIMIT 1", (team_id,))
    return filas[0]["venue_city"] if filas else None


@lru_cache(maxsize=32)
def _posiciones(liga_id: int, temporada: int, bucket: int) -> dict[int, int]:
    """{equipoId: posición} de la tabla del año (caché por hora)."""
    from backend.app import standings  # import perezoso: app importa este módulo
    try:
        return {r["equipoId"]: r["posicion"] for r in standings(liga_id, temporada)}
    except Exception:
        return {}


def _gap(team_id: int, fecha: str | None) -> dict | None:
    from backend.app import gap_equipo
    try:
        return gap_equipo(team_id, fecha)
    except Exception:
        return None


# ── etiquetas ───────────────────────────────────────────────────────────────

def etiquetas_de_rival(rival_id: int, rival_local: bool, liga_id: int | None,
                       temporada: int | None, fecha: str | None,
                       ciudad_equipo: str | None) -> list[dict]:
    """Las etiquetas G2 que los DATOS sostienen, cada una con su número."""
    et: list[dict] = []
    res = _resultados(rival_id)

    if _es_ascendido(rival_id, liga_id, temporada):
        et.append({"codigo": "RECIEN_ASCENDIDO", "label": "RECIÉN ASCENDIDO",
                   "dato": "primera temporada en la categoría",
                   "nota": "sus K están en cuarentena (R-KT.2): no hay línea base fiable"})

    derrotas = _derrotas_seguidas(res)
    dt_nuevo = _dt_reciente(rival_id)
    if derrotas >= CRISIS_DERROTAS or dt_nuevo:
        motivos = []
        if derrotas >= CRISIS_DERROTAS:
            motivos.append(f"{derrotas} derrotas seguidas")
        if dt_nuevo:
            motivos.append(f"DT nuevo desde {dt_nuevo}")
        et.append({"codigo": "EN_CRISIS", "label": "EN CRISIS", "dato": " · ".join(motivos),
                   "nota": "posible efecto rebote, en cualquiera de los dos sentidos"})

    ganados, jugados = _pct_condicion(rival_id, liga_id, temporada, rival_local)
    if jugados >= MIN_PARTIDOS_PCT:
        pct = ganados / jugados
        if rival_local and pct >= LOCAL_FUERTE_PCT:
            et.append({"codigo": "LOCAL_FUERTE", "label": "LOCAL FUERTE",
                       "dato": f"{round(pct * 100)}% de victorias en casa ({ganados}/{jugados})"})
        elif not rival_local and pct < VISITA_DEBIL_PCT:
            et.append({"codigo": "VISITA_DEBIL", "label": "VISITA DÉBIL",
                       "dato": f"{round(pct * 100)}% de victorias fuera ({ganados}/{jugados})"})

    g = _gap(rival_id, fecha)
    if g and g.get("gap") is not None and g["gap"] <= SORPRESA_GAP:
        et.append({"codigo": "EQUIPO_SORPRESA", "label": "EQUIPO SORPRESA",
                   "dato": f"rinde {abs(g['gap']):.2f} pts/partido por encima de su nivel",
                   "nota": "candidato a regresión: la ventaja puede no sostenerse"})

    formacion = _formacion_dominante(rival_id)
    if formacion and formacion.split("-")[0] == "5":
        et.append({"codigo": "BLOQUE_BAJO", "label": "BLOQUE BAJO",
                   "dato": f"formación dominante {formacion}"})

    ciudad_rival = _ciudad(rival_id)
    if ciudad_equipo and ciudad_rival and ciudad_equipo.strip().lower() == ciudad_rival.strip().lower():
        et.append({"codigo": "CLASICO", "label": "CLÁSICO", "dato": f"derbi de {ciudad_rival}",
                   "parcial": True,
                   "nota": "solo detectamos derbis de ciudad: una rivalidad nacional no sale de los datos"})
    return et


# ── calendario ──────────────────────────────────────────────────────────────

def calendario_de(team_id: int, n: int = PROXIMOS_DEFAULT) -> list[dict]:
    """Los próximos `n` partidos del equipo con el mapa de rivales del bloque G.
    [] si no hay fixtures programados. 0 requests, 0 tokens."""
    filas = _q(
        """SELECT f.id, f.date, f.home_team_id, f.away_team_id, f.league_id, f.league_season,
                  f.league_round, f.venue_city, l.name AS liga,
                  ht.name AS local, at.name AS visitante
           FROM fixtures f
           JOIN teams ht ON ht.id=f.home_team_id JOIN teams at ON at.id=f.away_team_id
           LEFT JOIN leagues l ON l.id=f.league_id
           WHERE (f.home_team_id=? OR f.away_team_id=?) AND f.status_short IN ('NS','TBD')
             AND f.date >= ? ORDER BY f.date ASC LIMIT ?""",
        (team_id, team_id, datetime.now(timezone.utc).strftime("%Y-%m-%d 00:00:00"), n),
    )
    if not filas:
        return []
    ciudad_equipo = _ciudad(team_id)
    ultimos = _resultados(team_id, limite=1)
    previo = ultimos[0]["fecha"] if ultimos else None
    bucket = _hora()

    salida = []
    for i, f in enumerate(filas):
        es_local = f["home_team_id"] == team_id
        rival_id = f["away_team_id"] if es_local else f["home_team_id"]
        rival_nombre = f["visitante"] if es_local else f["local"]
        fecha = (f["date"] or "")[:10]
        posiciones = _posiciones(f["league_id"], f["league_season"], bucket) if f["league_id"] else {}
        pos = posiciones.get(rival_id)
        total = len(posiciones)
        # descanso: contra el partido anterior para el primero, y entre fechas
        # para los siguientes — la congestión se lee de un vistazo
        ref = previo if i == 0 else (filas[i - 1]["date"] or "")
        dias = None
        if ref and f["date"]:
            try:
                dias = (datetime.strptime(str(f["date"])[:10], "%Y-%m-%d")
                        - datetime.strptime(str(ref)[:10], "%Y-%m-%d")).days
            except ValueError:
                dias = None
        salida.append({
            "fixtureId": f["id"],
            "fecha": fecha,
            "rivalId": rival_id,
            "rival": rival_nombre,
            "condicion": "L" if es_local else "V",
            "torneo": f["liga"],
            "ronda": f["league_round"],
            "posicionRival": pos,
            "equiposEnLaTabla": total or None,
            # zona: lo que importa del rival en la tabla, sin adjetivos
            "zonaRival": None if not pos or not total else (
                "alta" if pos <= 4 else "descenso" if pos > total - 3 else "media"),
            "diasDescanso": dias,
            "etiquetas": etiquetas_de_rival(rival_id, not es_local, f["league_id"],
                                            f["league_season"], fecha, ciudad_equipo),
        })
    return salida


def items_para_efe(team_id: int, n: int = PROXIMOS_DEFAULT) -> list[dict]:
    """El bloque G del EFE con la forma de su esquema (CALENDARIO_ITEM), para
    RELLENARLO EN CÓDIGO en vez de pagarle al modelo por copiar lo que ya
    calculamos. Además de ahorrar tokens de salida cierra la puerta a que el
    calendario salga adornado: aquí no cabe una etiqueta sin su dato."""
    return [
        {
            "rival": c["rival"],
            "fecha": c["fecha"],
            "condicion": c["condicion"],
            "etiquetas": [f"{e['label']} ({e['dato']})" for e in c["etiquetas"]],
            "posicion": c["posicionRival"] or 0,  # 0 = se desconoce, según el esquema
            "nota": ", ".join(filter(None, [
                f"zona {c['zonaRival']}" if c["zonaRival"] else "",
                f"{c['diasDescanso']}d de descanso" if c["diasDescanso"] is not None else "",
            ])),
        }
        for c in calendario_de(team_id, n)
    ]


def texto_para_skills(team_id: int, n: int = PROXIMOS_DEFAULT) -> str:
    """El mismo calendario como texto denso para `datos_cacheados` del EFE/DTP:
    con esto el modelo NO investiga el bloque G — ni busca ni deduce lo que ya
    está calculado. Vacío si no hay fixtures."""
    cal = calendario_de(team_id, n)
    if not cal:
        return ""
    partes = []
    for c in cal:
        et = "; ".join(f"{e['label']} ({e['dato']})" for e in c["etiquetas"]) or "sin etiqueta"
        pos = f"{c['posicionRival']}º" if c["posicionRival"] else "s/pos"
        descanso = f", {c['diasDescanso']}d de descanso" if c["diasDescanso"] is not None else ""
        partes.append(f"{c['fecha']} {c['condicion']} vs {c['rival']} ({pos}"
                      f"{', zona ' + c['zonaRival'] if c['zonaRival'] else ''}{descanso}): {et}")
    return ("Calendario SAD calculado de nuestra base (bloque G ya resuelto, NO lo investigues): "
            + " | ".join(partes))
