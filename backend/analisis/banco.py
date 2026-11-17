"""El banco probable — UNA lista para EFE, DTP y TDE (A8 de la EFE v1.10).

Qué hueco tapa. Las tres propuestas aprobadas el 10/11 piden lo mismo con tres
nombres: el EFE «banco probable» en la F1 y B5 por rol, el DTP `bancoOfensivo`
(cambio 5 y 12) y el TDE el banco de la hoja en `GET …/tde/{id}` (punto 2 de su
«Para la app»). Sin la lista, cada skill la armaba con dos nombres de memoria:
nombraba titulares de banco, gente que no estaba en la hoja, y le faltaba quien
decidió (estudio de las lecciones del 10-16/11: 16 lecciones del TDE y 16 del
DTP; DTP v1.8, 22 partidos).

La regla, la misma para los tres (decidida en las propuestas):
- **Con el once oficial, el banco es la hoja**: los suplentes publicados, sin
  ningún titular. Cada uno con lo que la base sabe de él.
- **Antes del once es «probable»**: los que en los últimos partidos entraron
  del banco seguido o hicieron goles o asistencias entrando.

Lo que la base dice de cada uno: titularidades en los últimos 10 onces (el
titular habitual que hoy arranca en el banco va primero: Meerveld, Heerenveen
1552221), entradas desde el banco, goles y asistencias entrando, y si su último
partido lo tuvo de lateral (el lateral fresco que llega es banco ofensivo por
rol, DTP v1.8 cambio 12).

Lo que NO hace: no decide quién entra ni en qué minuto (el banco va sin minuto
fijo, DTP v1.8 5 (b)), no puntúa B5 y no mueve ningún número. Sale de nuestra
base: 0 tokens, 0 requests.
"""
from backend import db as saddb
from backend.nombres import limpiar_nombre

ULTIMOS = 10          # los onces recientes que cuentan (los mismos 10 de `rolSugerido` en la F1)
HABITUAL = 5          # titular en 5 de los últimos 10: titular habitual
ENTRADAS_SEGUIDAS = 3  # entró del banco en 3 de los últimos 10: suplente de uso
TERMINADOS = ("FT", "AET", "PEN")
# una banca publicada con menos suplentes que esto es la parcial que la API
# sube antes de la completa (parte.BANCA_MIN_COMPLETA, 1427)
BANCA_MIN = 5
TITULARES_MIN = 7


def _q(sql: str, args: tuple) -> list[dict]:
    try:
        return [dict(r) for r in saddb.query("sad", sql, args)]
    except Exception:  # noqa: BLE001 — base sin la ficha de partido: no hay banco que calcular
        return []


def _previos(team_id: int, fecha: str, fixture_id: int) -> list[int]:
    """Los últimos partidos jugados del equipo con hoja capturada, del más nuevo al más viejo."""
    marca = ",".join("?" * len(TERMINADOS))
    filas = _q(f"SELECT DISTINCT f.id, f.date FROM fixtures f JOIN alineaciones a ON a.fixture_id = f.id "
               f"WHERE a.team_id = ? AND a.titular = 1 AND f.id != ? AND f.date < ? "
               f"AND f.status_short IN ({marca}) ORDER BY f.date DESC LIMIT ?",
               (team_id, fixture_id, fecha, *TERMINADOS, ULTIMOS))
    return [f["id"] for f in filas]


def _laterales(filas: list[dict]) -> set[int]:
    """Los ids que el grid pone en una punta de la línea de atrás (fila 2 con 4 o
    más): laterales o carrileros. Sin grid, nadie."""
    linea = []
    for f in filas:
        g = str(f.get("grid") or "")
        if f.get("titular") and g.startswith("2:"):
            try:
                linea.append((int(g.split(":")[1]), f["player_id"]))
            except (ValueError, IndexError):
                continue
    if len(linea) < 4:
        return set()
    cols = [c for c, _ in linea]
    return {pid for c, pid in linea if c in (min(cols), max(cols))}


def historia(team_id: int, fecha: str, fixture_id: int) -> dict[int, dict]:
    """Por jugador, lo que dicen los últimos 10 partidos del equipo."""
    previos = _previos(team_id, fecha, fixture_id)
    out: dict[int, dict] = {}
    for orden, fid in enumerate(previos):
        hoja = _q("SELECT player_id, jugador, posicion, grid, titular FROM alineaciones "
                  "WHERE fixture_id = ? AND team_id = ?", (fid, team_id))
        eventos = _q("SELECT lower(tipo) AS tipo, detalle, jugador_id, asistente_id FROM fixture_eventos "
                     "WHERE fixture_id = ? AND equipo_id = ?", (fid, team_id))
        en_cambio = {i for e in eventos if e["tipo"] == "subst" for i in (e["jugador_id"], e["asistente_id"]) if i}
        goles = [e for e in eventos if e["tipo"] == "goal"
                 and "own" not in (e["detalle"] or "").lower() and "missed" not in (e["detalle"] or "").lower()]
        laterales = _laterales(hoja)
        for f in hoja:
            pid = f["player_id"]
            if not pid:
                continue
            h = out.setdefault(pid, {"nombre": limpiar_nombre(f["jugador"] or "") or "", "titularidades": 0,
                                     "entradas": 0, "golesDesdeBanco": 0, "asistenciasDesdeBanco": 0,
                                     "posicion": f["posicion"] or "", "lateral": False, "_visto": orden})
            if orden <= h["_visto"]:   # el partido más reciente manda en posición y rol
                h.update(_visto=orden, posicion=f["posicion"] or h["posicion"], lateral=pid in laterales)
            if f["titular"]:
                h["titularidades"] += 1
            elif pid in en_cambio:
                h["entradas"] += 1
                h["golesDesdeBanco"] += sum(1 for g in goles if g["jugador_id"] == pid)
                h["asistenciasDesdeBanco"] += sum(1 for g in goles if g["asistente_id"] == pid)
    for h in out.values():
        h.pop("_visto", None)
    return out


def _porque(h: dict) -> list[str]:
    p = []
    if h["titularidades"] >= HABITUAL:
        p.append(f"titular habitual ({h['titularidades']} de los últimos {ULTIMOS})")
    if h["golesDesdeBanco"] or h["asistenciasDesdeBanco"]:
        p.append(f"{h['golesDesdeBanco']} g y {h['asistenciasDesdeBanco']} a entrando")
    if h["entradas"] >= ENTRADAS_SEGUIDAS:
        p.append(f"entró del banco en {h['entradas']} de los últimos {ULTIMOS}")
    if h["lateral"]:
        p.append("lateral en su último partido: llega al área por rol")
    return p


def _orden(x: dict) -> tuple:
    # el titular habitual primero (es el que más se olvida), después lo que hizo entrando
    return (-(x["titularidades"] >= HABITUAL), -(x["golesDesdeBanco"] + x["asistenciasDesdeBanco"]),
            -x["entradas"], -x["titularidades"], x["nombre"])


def de_equipo(fixture_id: int, team_id: int, fecha: str) -> dict:
    hist = historia(team_id, fecha, fixture_id)
    hoja = _q("SELECT player_id, jugador, posicion, titular FROM alineaciones WHERE fixture_id = ? AND team_id = ?",
              (fixture_id, team_id))
    titulares = [f for f in hoja if f["titular"]]
    banca = [f for f in hoja if not f["titular"]]
    vacio = {"titularidades": 0, "entradas": 0, "golesDesdeBanco": 0, "asistenciasDesdeBanco": 0, "lateral": False}
    if len(titulares) >= TITULARES_MIN and len(banca) >= BANCA_MIN:
        lista = []
        for f in banca:
            h = hist.get(f["player_id"]) or {**vacio, "posicion": f["posicion"] or ""}
            lista.append({"jugadorId": f["player_id"] if f["player_id"] and f["player_id"] > 0 else None,
                          "nombre": limpiar_nombre(f["jugador"] or "") or "", "posicion": f["posicion"] or h["posicion"],
                          **{k: h[k] for k in vacio}, "titularHabitual": h["titularidades"] >= HABITUAL,
                          "porque": _porque(h)})
        lista.sort(key=_orden)
        return {"fuente": "hoja", "lista": lista,
                "titularesHabitualesEnElBanco": [x["nombre"] for x in lista if x["titularHabitual"]],
                "nota": "con el once oficial el banco es la hoja: estos son todos los suplentes publicados y "
                        "ninguno es titular. Nombrar a otro como banco es escribir sobre otro equipo"}
    if len(titulares) >= TITULARES_MIN:
        aviso = (f"la hoja trae {len(banca)} suplente(s): la API publica primero una banca parcial; "
                 "hasta la completa, el banco sigue siendo probable")
    else:
        aviso = ""
    en_once = {f["player_id"] for f in titulares}
    lista = []
    for pid, h in hist.items():
        if pid in en_once:
            continue
        if not (h["golesDesdeBanco"] or h["asistenciasDesdeBanco"] or h["entradas"] >= ENTRADAS_SEGUIDAS):
            continue
        lista.append({"jugadorId": pid if pid > 0 else None, "nombre": h["nombre"], "posicion": h["posicion"],
                      **{k: h[k] for k in vacio}, "titularHabitual": h["titularidades"] >= HABITUAL,
                      "porque": _porque(h)})
    lista.sort(key=_orden)
    return {"fuente": "probable", "lista": lista, "titularesHabitualesEnElBanco": [],
            "nota": "sin once oficial el banco es PROBABLE y se escribe así: los que entraron del banco "
                    f"seguido o hicieron goles o asistencias entrando en los últimos {ULTIMOS}. No trae al "
                    "titular habitual que hoy puede rotar ni a la duda que puede ir al banco: eso es de la "
                    "tabla F1 (estado «banco probable»). Con el once, se reescribe con la hoja"
                    + (f". Ojo: {aviso}" if aviso else "")}


def banco_probable(fixture_id: int) -> dict | None:
    """Los dos lados. None si el fixture no está en la base."""
    fx = (_q("SELECT id, date, home_team_id, away_team_id FROM fixtures WHERE id = ?", (fixture_id,)) or [None])[0]
    if not fx:
        return None
    fecha = str(fx["date"])
    return {"a": de_equipo(fixture_id, fx["home_team_id"], fecha),
            "b": de_equipo(fixture_id, fx["away_team_id"], fecha)}
