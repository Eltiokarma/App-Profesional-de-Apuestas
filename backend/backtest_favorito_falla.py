"""¿El FAVORITO que viene fallándole a lo esperado gana menos? (25/11/2026)

El caso: Manchester City, 1 victoria en 7 (24/10 → 24/11/2026) con la casa
dándole entre 55 y 75 % en cada uno; ante Fulham y Napoli empató con 69 y
75 %. El sistema no lo marcó: la regresión al nivel decía «gap fuerte ·
mejora» y la burbuja «−» con riesgo alto decía que la racha se cortaba. El
usuario: «no nos iremos hasta cazarlo».

La señal, fijada ANTES de mirar: el residuo de los últimos 5 partidos
oficiales del favorito, victorias reales − victorias esperadas, en −1,5 o
menos. Contra la casa (cuota de cada partido previo) dio, en 1.890 favoritos
con cuota (agosto → 24/11/2026), 51 % de victorias contra 61 % que decía la
casa (−14 pts, IC −28,6 a 0,0, n 49): una pista, no una prueba. Esto la pone a
prueba donde la cuota no llega: **contra el NIVEL, en 5 años** (pedido del
usuario, 25/11/2026: «solo 5 años»).

- **Lo esperado de cada partido previo** sale del nivel: la frecuencia de
  victoria de TODOS los partidos oficiales con la misma ventaja de nivel previo
  (tramo de 0,1) y la misma condición. Es una tabla de calibración del nivel,
  no del equipo: el partido que se evalúa pesa uno en decenas de miles.
- **El residuo** usa solo partidos de días ANTERIORES al evaluado (los del
  mismo día no entran) y los niveles previos de los dos lados (§13.1 de
  REVENTON: el nivel de la fila ya trae el resultado).
- **El favorito** tiene 0,5+ de nivel previo sobre el rival (o la casa le da
  50 %+). Con la señal contra sin ella, en el MISMO tramo fino de ventaja y
  condición (o de probabilidad de la casa), con IC por bootstrap de equipos,
  por época (las dos mitades) y liga por liga con la prueba del signo.
- **Se mide como pide el usuario** (apostamos por acierto): cuánto más falla
  el favorito con la señal, qué parte de los partidos marca y qué parte de los
  tropiezos caza, y si se repite. No se mide valor.

Variantes, todas escritas antes de correr: la de 5 en −1,5 (la fijada), 3 en
−1,0, 5 en −1,0 y el espejo (5 en +1,5: el que viene sobrerindiendo). Contra
la casa, la misma con la cuota de cada partido previo, donde hay cuotas.
Amistosos fuera de la ventana y de los casos; copas nacionales fuera de los
casos (sí cuentan en la ventana: son partidos que el equipo jugó). Lee, no
escribe.

    python -m backend.backtest_favorito_falla --padron [--anos 5] [--json salida.json]
    python -m backend.backtest_favorito_falla --padron --grandes 3.0 --temporada-internacional
    python -m backend.backtest_favorito_falla --desde-dir carpeta [--anos 5]
      (carpeta: c/<id>.json de /constantes, n/<id>.json de /niveles,
       ligas.json {id: nombre} de /ligas/{id} y, si hay, cuotas.json
       {fixture: {"1","X","2"}} de /cuotas/{id})
"""
from __future__ import annotations

import argparse
import json
import os
import random
from bisect import bisect_left
from collections import defaultdict, deque
from datetime import date, timedelta

from backend.backtest_rival_resiste import _boot, _signo

AMISTOSOS = {667}
FAVORITO_NIVEL = 0.5
FAVORITO_CASA = 0.5
ANOS = 5
VENTANA_CASA_DIAS = 120      # la ventana de la casa no salta un hueco de cuotas más largo
MIN_LIGA = 30
MIN_BIN = 30

SENALES = {
    "n5-1.5": ("nivel", 5, lambda r: r <= -1.5, "residuo de 5 en −1,5 o menos (la fijada)"),
    "n3-1.0": ("nivel", 3, lambda r: r <= -1.0, "residuo de 3 en −1,0 o menos"),
    "n5-1.0": ("nivel", 5, lambda r: r <= -1.0, "residuo de 5 en −1,0 o menos"),
    "n5+1.5": ("nivel", 5, lambda r: r >= 1.5, "espejo: residuo de 5 en +1,5 o más (sobrerinde)"),
    "c5-1.5": ("casa", 5, lambda r: r <= -1.5, "contra la cuota de cada previo: 5 en −1,5 o menos"),
}

SEGMENTOS = {
    "favorito por nivel (0,5+)": lambda c: c["porNivel"],
    "muy favorito por nivel (1,0+)": lambda c: c["porNivel"] and c["ventaja"] >= 1.0,
    "gigante: nivel 3,5+ y 1,0+ de ventaja": lambda c: c["porNivel"] and c["ventaja"] >= 1.0 and (c["nivel"] or 0) >= 3.5,
    "favorito de local": lambda c: c["porNivel"] and c["local"],
    "favorito de visita": lambda c: c["porNivel"] and not c["local"],
}


def _antes(fechas: list[str], valores: list[float], fecha: str) -> float | None:
    i = bisect_left(fechas, fecha)
    return valores[i - 1] if i > 0 else None


def _bin_v(v: float, local: bool) -> tuple:
    return (max(-30, min(30, round(v / 0.1))), local)


# ── lo que se sabía antes de cada partido ────────────────────────────────────

def partidos(historias: dict[int, dict], nivel_rival=None) -> dict[int, list[dict]]:
    """{equipo: [partido oficial con niveles previos y resultado], en orden}."""
    niv = {t: ([n["fecha"] for n in sorted(h.get("niveles") or [], key=lambda n: n["fecha"])],
               [float(n["nivel"]) for n in sorted(h.get("niveles") or [], key=lambda n: n["fecha"])])
           for t, h in historias.items()}
    out = {}
    for t, h in historias.items():
        filas = sorted((f for f in h["filas"] if f.get("golesFavor") is not None and f.get("golesContra") is not None
                        and f.get("ligaId") not in AMISTOSOS and f.get("condicion") in ("Local", "Visita")),
                       key=lambda f: str(f.get("fecha") or ""))
        lista = []
        for f in filas:
            fecha = str(f["fecha"])
            propio = _antes(*niv[t], fecha) if niv.get(t) and niv[t][0] else None
            rid = f.get("rivalId")
            if rid in niv and niv[rid][0]:
                rival = _antes(*niv[rid], fecha)
            elif nivel_rival is not None and rid is not None:
                rival = nivel_rival(rid, fecha)
            else:
                rival = None
            gf, gc = int(f["golesFavor"]), int(f["golesContra"])
            lista.append({"fixtureId": f["fixtureId"], "fecha": fecha[:10], "liga": f.get("ligaId"), "rival": rid,
                          "temporada": f.get("temporada"), "internacional": bool(f.get("esInternacional")),
                          "local": f["condicion"] == "Local", "gana": gf > gc,
                          "nivel": propio, "ventaja": (propio - rival) if propio is not None and rival is not None else None})
        out[t] = lista
    return out


def tabla_esperada(pts: dict[int, list[dict]]) -> dict[tuple, float]:
    """P(gana | tramo de 0,1 de ventaja previa, condición) sobre todos los oficiales.
    Un tramo con menos de MIN_BIN se junta con sus vecinos hasta llegar."""
    cuenta = defaultdict(lambda: [0, 0])
    for lista in pts.values():
        for p in lista:
            if p["ventaja"] is not None:
                k = _bin_v(p["ventaja"], p["local"])
                cuenta[k][0] += p["gana"]
                cuenta[k][1] += 1
    out = {}
    for loc in (True, False):
        for b in range(-30, 31):
            g = n = 0
            for r in range(0, 31):
                for bb in {b - r, b + r}:
                    g += cuenta[(bb, loc)][0] if (bb, loc) in cuenta else 0
                    n += cuenta[(bb, loc)][1] if (bb, loc) in cuenta else 0
                if n >= MIN_BIN:
                    break
            if n:
                out[(b, loc)] = g / n
    return out


def casos(historias: dict[int, dict], cuotas: dict | None = None, excluir: set | None = None,
          nivel_rival=None, desde: str = "") -> list[dict]:
    """Un caso por favorito (por nivel o por casa) desde `desde`, con los residuos de su
    ventana previa. `cuotas[fx] = (pL, pX, pV, …)` sin margen."""
    pts = partidos(historias, nivel_rival)
    esp = tabla_esperada(pts)
    cuotas = cuotas or {}
    out = []
    for t, lista in pts.items():
        rn: deque = deque(maxlen=5)      # residuos contra el nivel
        rc: deque = deque(maxlen=5)      # (fecha, residuo) contra la casa
        pendientes, dia = [], None
        for p in lista:
            if p["fecha"] != dia:          # lo del mismo día no entra a la ventana
                for kind, x in pendientes:
                    (rn if kind == "n" else rc).append(x)
                pendientes, dia = [], p["fecha"]
            c = cuotas.get(p["fixtureId"])
            pc = (c[0] if p["local"] else c[2]) if c else None
            if p["fecha"] >= desde and not (excluir and p["fixtureId"] in excluir):
                por_nivel = p["ventaja"] is not None and p["ventaja"] >= FAVORITO_NIVEL
                por_casa = pc is not None and pc >= FAVORITO_CASA
                if por_nivel or por_casa:
                    lim = (date.fromisoformat(p["fecha"]) - timedelta(days=VENTANA_CASA_DIAS)).isoformat()
                    rcv = [r for f, r in rc if f >= lim]
                    out.append({
                        "fixtureId": p["fixtureId"], "team": t, "fecha": p["fecha"], "liga": p["liga"],
                        "temporada": p["temporada"],
                        "local": p["local"], "gana": p["gana"], "ventaja": p["ventaja"], "nivel": p["nivel"],
                        "porNivel": por_nivel, "p": pc, "porCasa": por_casa,
                        "nivel5": sum(rn) if len(rn) == 5 else None,
                        "nivel3": sum(list(rn)[-3:]) if len(rn) >= 3 else None,
                        "casa5": sum(rcv) if len(rcv) == 5 else None,
                    })
            if p["ventaja"] is not None:
                k = _bin_v(p["ventaja"], p["local"])
                if k in esp:
                    pendientes.append(("n", (1 if p["gana"] else 0) - esp[k]))
            if pc is not None:
                pendientes.append(("c", (p["fecha"], (1 if p["gana"] else 0) - pc)))
    out.sort(key=lambda x: (x["fecha"], x["fixtureId"]))
    return out


# ── el grupo: grandes en temporada internacional (25/11/2026) ─────────────────
# El usuario: «córrelo solo con equipos grandes y en temporadas de torneos
# internacionales». GRANDE es del equipo, no del momento: su nivel MEDIANO en
# los años evaluados (el City entró a Napoli con 2,93 en plena mala racha y su
# mediana es 3,67). Es una clasificación del grupo, no un rasgo previo del
# partido: no entra a la señal. TEMPORADA INTERNACIONAL: la `temporada` en la
# que el equipo jugó al menos un partido de torneo internacional de clubes
# (`esInternacional`: Champions, Libertadores, Mundial de Clubes…); entran
# todos sus partidos oficiales de esa temporada, liga incluida.

# El nivel es relativo a la liga: con el corte solo, La Fiorita (San Marino),
# Kauno Žalgiris o Lincoln Red Imps eran «grandes». Grande es además jugar en
# una liga grande: la liga principal del equipo (la más frecuente de sus
# oficiales, sin torneos internacionales ni copas) está en esta lista.
LIGAS_GRANDES = {
    39: "Premier League", 140: "La Liga", 135: "Serie A", 78: "Bundesliga", 61: "Ligue 1",
    94: "Primeira Liga", 88: "Eredivisie", 71: "Brasil - Serie A", 128: "Argentina - Liga Profesional",
}


def liga_principal(h: dict, desde: str = "") -> int | None:
    from collections import Counter
    # sin mirar copas: la liga siempre tiene más partidos que la copa
    c = Counter(f.get("ligaId") for f in h["filas"] if str(f.get("fecha") or "")[:10] >= desde
                and not f.get("esInternacional") and f.get("ligaId") not in AMISTOSOS)
    return c.most_common(1)[0][0] if c else None


def grandes(historias: dict[int, dict], corte: float, desde: str = "", ligas=LIGAS_GRANDES,
            hasta: str | None = None) -> set[int]:
    """`hasta` deja afuera el nivel desde esa fecha: quien mide una predicción no puede
    elegir el grupo con el futuro (un grande con un bache «se recupera» por construcción)."""
    out = set()
    for t, h in historias.items():
        nv = sorted(float(n["nivel"]) for n in h.get("niveles") or []
                    if str(n["fecha"])[:10] >= desde and (hasta is None or str(n["fecha"])[:10] < hasta))
        if len(nv) >= 50 and nv[len(nv) // 2] >= corte and (ligas is None or liga_principal(h, desde) in ligas):
            out.add(t)
    return out


def temporadas_internacionales(historias: dict[int, dict]) -> set[tuple[int, int]]:
    return {(t, f["temporada"]) for t, h in historias.items() for f in h["filas"]
            if f.get("esInternacional") and f.get("temporada") is not None and f.get("ligaId") not in AMISTOSOS}


def filtrar(cs: list[dict], historias: dict[int, dict], corte: float | None, internacional: bool,
            desde: str = "") -> list[dict]:
    if corte is not None:
        g = grandes(historias, corte, desde)
        cs = [c for c in cs if c["team"] in g]
    if internacional:
        ti = temporadas_internacionales(historias)
        cs = [c for c in cs if (c["team"], c["temporada"]) in ti]
    return cs


# ── la cuenta ────────────────────────────────────────────────────────────────

def _valor(c: dict, clave: str) -> float | None:
    fuente, n, _, _ = SENALES[clave]
    return c[f"{fuente}{n}"]


def _marca(c: dict, clave: str) -> bool:
    v = _valor(c, clave)
    return v is not None and SENALES[clave][2](v)


def _bin_caso(c: dict, por: str) -> tuple:
    if por == "casa":
        return (min(19, int(c["p"] / 0.05)), c["local"])
    return (min(int(c["ventaja"] / 0.1), 30), c["local"])


def separa(seg: list[dict], clave: str, por: str = "nivel", semilla: int = 7) -> dict:
    """Con la señal contra sin ella, en el segmento (solo los casos con la ventana
    completa). `diferencia` = cuánto más NO GANA el favorito con la señal que los sin
    señal de su mismo tramo fino y condición (> 0 = marca dónde no entrar)."""
    seg = [c for c in seg if _valor(c, clave) is not None]
    con = [c for c in seg if _marca(c, clave)]
    sin = [c for c in seg if not _marca(c, clave)]
    tropiezos = sum(1 for c in seg if not c["gana"])
    out = {"n": len(seg), "conSenal": len(con), "parte": round(len(con) / len(seg), 4) if seg else None,
           "fallaCon": round(sum(1 for c in con if not c["gana"]) / len(con), 4) if con else None,
           "fallaSin": round(sum(1 for c in sin if not c["gana"]) / len(sin), 4) if sin else None,
           "caza": round(sum(1 for c in con if not c["gana"]) / tropiezos, 4) if tropiezos else None}
    base = defaultdict(lambda: [0, 0])
    for c in sin:
        base[_bin_caso(c, por)][0] += 0 if c["gana"] else 1
        base[_bin_caso(c, por)][1] += 1
    esp = {k: s / n for k, (s, n) in base.items() if n >= 10}
    por_eq = defaultdict(lambda: [0.0, 0])
    for c in con:
        k = _bin_caso(c, por)
        if k in esp:
            por_eq[c["team"]][0] += (0 if c["gana"] else 1) - esp[k]
            por_eq[c["team"]][1] += 1
    if por == "casa" and con:
        out["casaDecia"] = round(sum(1 - c["p"] for c in con) / len(con), 4)
    b = _boot(list(por_eq.values()), semilla)
    if b:
        out.update({"diferencia": round(b[0], 4), "ic95": [round(b[1], 4), round(b[2], 4)],
                    "separa": b[1] > 0 or b[2] < 0})
    else:
        out["sinDato"] = "menos de 30 casos o de 5 equipos con la señal"
    return out


def por_epoca(seg: list[dict], clave: str, por: str = "nivel") -> list[dict]:
    fechas = sorted(c["fecha"] for c in seg if _valor(c, clave) is not None)
    if not fechas:
        return []
    corte = fechas[len(fechas) // 2]
    return [{"epoca": f"antes de {corte}", **separa([c for c in seg if c["fecha"] < corte], clave, por)},
            {"epoca": f"desde {corte}", **separa([c for c in seg if c["fecha"] >= corte], clave, por)}]


def por_liga(seg: list[dict], clave: str) -> dict:
    """En cada liga con MIN_LIGA+ casos con la señal: el residuo contra los SIN señal de
    TODAS las ligas en el mismo tramo y condición; cuántas van en el sentido de la señal."""
    seg = [c for c in seg if _valor(c, clave) is not None]
    base = defaultdict(lambda: [0, 0])
    for c in seg:
        if not _marca(c, clave):
            base[_bin_caso(c, "nivel")][0] += 0 if c["gana"] else 1
            base[_bin_caso(c, "nivel")][1] += 1
    esp = {k: s / n for k, (s, n) in base.items() if n}
    ligas = defaultdict(list)
    for c in seg:
        if _marca(c, clave) and _bin_caso(c, "nivel") in esp:
            ligas[c["liga"]].append((0 if c["gana"] else 1) - esp[_bin_caso(c, "nivel")])
    filas = sorted(({"liga": lg, "n": len(v), "residuo": round(sum(v) / len(v), 4)}
                    for lg, v in ligas.items() if len(v) >= MIN_LIGA), key=lambda x: -x["n"])
    pos = sum(1 for f in filas if f["residuo"] > 0)
    return {"ligas": filas, "enElSentido": pos, "alReves": len(filas) - pos, "pSigno": _signo(pos, len(filas))}


def se_repite(r: dict, epocas: list[dict], sentido: int) -> bool:
    """Separa en todo el período y en las dos mitades, en el mismo sentido."""
    ok = lambda d: d.get("separa") and (d["diferencia"] > 0) == (sentido > 0)  # noqa: E731
    return bool(ok(r) and len(epocas) == 2 and all(ok(e) for e in epocas))


def evaluar(cs: list[dict]) -> dict:
    if not cs:
        return {"casos": 0, "lectura": "sin casos"}
    nv = [c for c in cs if c["porNivel"]]
    cc = [c for c in cs if c["porCasa"]]
    out = {"casos": len(cs), "porNivel": len(nv), "porCasa": len(cc),
           "desde": cs[0]["fecha"], "hasta": cs[-1]["fecha"], "senales": []}
    for clave, (fuente, _, _, nombre) in SENALES.items():
        sentido = -1 if clave.endswith("+1.5") else 1
        fila = {"senal": clave, "nombre": nombre, "fuente": fuente}
        if fuente == "nivel":
            fila["nivel"] = separa(nv, clave)
            fila["porEpoca"] = por_epoca(nv, clave)
            fila["seRepite"] = se_repite(fila["nivel"], fila["porEpoca"], sentido)
            fila["porLiga"] = por_liga(nv, clave)
            fila["segmentos"] = [{"segmento": sn, **separa([c for c in nv if sf(c)], clave)}
                                 for sn, sf in SEGMENTOS.items()]
        fila["casa"] = separa(cc, clave, "casa")
        fila["casaPorEpoca"] = por_epoca(cc, clave, "casa")
        out["senales"].append(fila)
    out["lectura"] = lectura(out)
    return out


def lectura(r: dict) -> str:
    partes = []
    for s in r["senales"]:
        d = s.get("nivel") if s["fuente"] == "nivel" else s["casa"]
        if not d or "diferencia" not in d:
            partes.append(f"{s['senal']}: sin muestra")
            continue
        txt = (f"{s['senal']}: el favorito no gana {d['diferencia']:+.1%} contra los sin señal "
               f"(IC {d['ic95'][0]:+.1%} a {d['ic95'][1]:+.1%}, {d['conSenal']} con la señal, "
               f"{d['parte']:.1%} de los favoritos, caza {d['caza']:.1%} de los tropiezos), "
               + ("separa y se repite" if s.get("seRepite") else "separa sin repetirse" if d.get("separa")
                  else "no separa"))
        if s.get("porLiga"):
            lg = s["porLiga"]
            txt += f"; ligas en el sentido {lg['enElSentido']} de {lg['enElSentido'] + lg['alReves']} (p {lg['pSigno']})"
        partes.append(txt)
    return " · ".join(partes)


# ── de dónde salen los datos ─────────────────────────────────────────────────

def _desde(anos: int, hoy: date | None = None) -> str:
    h = hoy or date.today()
    try:
        return h.replace(year=h.year - anos).isoformat()
    except ValueError:                      # 29 de febrero
        return (h.replace(month=2, day=28, year=h.year - anos)).isoformat()


def correr_padron(anos: int = ANOS, corte: float | None = None, internacional: bool = False) -> dict:
    os.environ.setdefault("SAD_SIN_HILOS", "1")
    from backend.backtest_burbuja import nivel_rival_previo
    from backend.backtest_burbuja_1x2 import cuotas_1x2
    from backend.backtest_dc_record import historias_padron
    from backend.backtest_rival_resiste import _copas
    historias = historias_padron()
    fxs = sorted({f["fixtureId"] for h in historias.values() for f in h["filas"]
                  if f.get("ligaId") not in AMISTOSOS and f.get("golesFavor") is not None})
    cuotas = cuotas_1x2(fxs)
    excluir = _copas(fxs)
    cs = filtrar(casos(historias, cuotas, excluir, nivel_rival_previo, _desde(anos)), historias, corte,
                 internacional, _desde(anos))
    r = evaluar(cs)
    r.update({"equipos": len({c["team"] for c in cs}), "partidosConCuota": len(cuotas),
              "copasNacionalesFuera": len(excluir), "anos": anos, "grandes": corte, "temporadaInternacional": internacional})
    return r


def correr_dir(carpeta: str, anos: int = ANOS, corte: float | None = None, internacional: bool = False) -> dict:
    from backend.analisis.escala import es_copa_nacional
    from backend.backtest_dc_record import historias_desde_dir
    try:
        from backend.ingesta.extractor import LIGAS_INTERNACIONALES
        internacionales = set(LIGAS_INTERNACIONALES)
    except Exception:  # noqa: BLE001 — sin el extractor, el nombre basta para las internacionales
        internacionales = set()
    historias = historias_desde_dir(carpeta)
    nombres = {}
    if os.path.exists(os.path.join(carpeta, "ligas.json")):
        nombres = {int(k): v for k, v in json.load(open(os.path.join(carpeta, "ligas.json"))).items()}
    copas = {lg for lg, nom in nombres.items() if es_copa_nacional(lg, nom or "", internacionales)}
    excluir = {f["fixtureId"] for h in historias.values() for f in h["filas"] if f.get("ligaId") in copas}
    cuotas = {}
    ruta = os.path.join(carpeta, "cuotas.json")
    if os.path.exists(ruta):
        for fx, o in json.load(open(ruta)).items():
            if o and all(s in o for s in ("1", "X", "2")):
                inv = [1 / o["1"], 1 / o["X"], 1 / o["2"]]
                tot = sum(inv)
                cuotas[int(fx)] = (inv[0] / tot, inv[1] / tot, inv[2] / tot)
    cs = filtrar(casos(historias, cuotas, excluir, None, _desde(anos)), historias, corte, internacional, _desde(anos))
    r = evaluar(cs)
    r.update({"equipos": len({c["team"] for c in cs}), "partidosConCuota": len(cuotas),
              "copasNacionalesFuera": len(excluir), "anos": anos, "grandes": corte, "temporadaInternacional": internacional,
              "ligasSinNombre": sum(1 for v in nombres.values() if not v)})
    return r


def _imprimir(r: dict) -> None:
    if not r.get("casos"):
        print(r.get("lectura"))
        return
    print(f"\n{r['casos']:,} favoritos ({r['porNivel']:,} por nivel, {r['porCasa']:,} por casa) · "
          f"{r['desde']} → {r['hasta']} · {r.get('equipos', 0):,} equipos · "
          f"copas nacionales fuera: {r.get('copasNacionalesFuera', 0):,}\n")

    def x(d):
        if not d or not d.get("conSenal"):
            return f"n {d.get('n', 0) if d else 0:>6}  sin casos con la señal"
        base = (f"n {d['n']:>6}  marca {d['parte']:5.1%}  falla {d['fallaCon']:5.1%} con / {d['fallaSin']:5.1%} sin"
                f"  caza {d['caza']:5.1%}")
        if "casaDecia" in d:
            base += f"  (la casa decía que fallaba {d['casaDecia']:.1%})"
        if "diferencia" not in d:
            return base + f"  · {d.get('sinDato', '')}"
        return (base + f"  · diferencia {d['diferencia']:+.1%} IC [{d['ic95'][0]:+.1%}, {d['ic95'][1]:+.1%}]"
                + ("  SEPARA" if d["separa"] else ""))
    for s in r["senales"]:
        print(f"FAVORITO: {s['nombre']}")
        if s["fuente"] == "nivel":
            print(f"  contra el nivel     {x(s['nivel'])}" + ("  · SE REPITE" if s["seRepite"] else ""))
            for e in s["porEpoca"]:
                print(f"    {e['epoca']:<17} {x(e)}")
            lg = s["porLiga"]
            print(f"  por liga: {lg['enElSentido']} en el sentido, {lg['alReves']} al revés (p signo {lg['pSigno']})")
            for sg in s["segmentos"]:
                print(f"    {sg['segmento']:<38} {x(sg)}")
        print(f"  contra la casa      {x(s['casa'])}")
        for e in s["casaPorEpoca"]:
            print(f"    {e['epoca']:<17} {x(e)}")
        print()
    print("(diferencia > 0 = con la señal el favorito NO GANA más que los sin señal de su mismo tramo: "
          "marca dónde no entrar; en el espejo se espera < 0)")
    print(r["lectura"])


def main() -> None:
    ap = argparse.ArgumentParser(description="¿El favorito que viene fallándole a lo esperado gana menos?")
    ap.add_argument("--padron", action="store_true", help="historias, niveles y cuotas del padrón (en el servidor)")
    ap.add_argument("--desde-dir", help="carpeta con c/, n/, ligas.json y cuotas.json bajados de la API")
    ap.add_argument("--anos", type=int, default=ANOS, help=f"años hacia atrás que se evalúan (por defecto {ANOS})")
    ap.add_argument("--grandes", type=float, help="solo equipos con nivel MEDIANO del período en este corte o más (p. ej. 3.0)")
    ap.add_argument("--temporada-internacional", action="store_true",
                    help="solo las temporadas en que el equipo jugó un torneo internacional de clubes")
    ap.add_argument("--json", help="guardar el resumen en este archivo")
    a = ap.parse_args()
    if a.desde_dir:
        r = correr_dir(a.desde_dir, a.anos, a.grandes, a.temporada_internacional)
    elif a.padron:
        r = correr_padron(a.anos, a.grandes, a.temporada_internacional)
    else:
        ap.error("falta --padron (en el servidor) o --desde-dir")
    _imprimir(r)
    if a.json:
        json.dump(r, open(a.json, "w"), ensure_ascii=False, indent=1)
        print(f"\nresumen en {a.json}")


if __name__ == "__main__":
    random.seed(7)
    main()
