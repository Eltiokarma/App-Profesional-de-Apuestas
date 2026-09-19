"""Reventón de la burbuja: cuándo una K deja de acumular y vuelve a cero.

No es una probabilidad. Es una GUÍA calculada de la propia historia del equipo:
cuánta K y cuántos partidos aguantó cada racha antes de reventar, y con qué
nivel de rival reventó. Con eso se compara la burbuja abierta hoy y el rival
que viene, y se dice si el terreno es el de siempre o si nunca aguantó tanto.
Lo que no sale de la base (dueños, organización, clima del vestuario) se
declara como sin dato: no se rellena a ojo.

Función pura sobre las filas del contrato `/constantes/{id}` (orden
cronológico) más un contexto (nivel, próximo rival, plantilla). Espejo exacto
en `src/lib/burbuja.ts`; los dos se verifican contra `scripts/casos_burbuja.json`.

Reglas (las mismas en los dos lados):

- Una burbuja es una racha de la K fusionada con el mismo signo. Revienta
  cuando la K vuelve a 0 (empate, o el resultado contrario sin acumular) o
  cuando cambia de signo en el mismo partido (una derrota que arranca la
  racha negativa). El partido que la revienta viaja con su rival y su nivel.
- Local/visita solo miran los partidos de su condición: los de la otra
  conservan el valor y no cuentan como partidos de la racha.
- Por signo: media, mediana y moda de la K pico, de los partidos y del nivel
  del rival del reventón. La moda se busca sobre valores redondeados (K a
  entero, nivel a un decimal); si nada se repite no hay moda, y en empate se
  toma la menor (avisar antes es más barato que avisar tarde).
- Qué constante manda: la total, siempre; la hipótesis del nivel (alto o bajo
  → globales; medio → la condición del próximo) viaja en reglaNivel porque
  el backtest real no la confirmó.
- Riesgo de reventón por puntos CALIBRADOS con el backtest real (§8 del doc):
  la K no puntúa (no adelanta el reventón), la racha ≥ mediana suma 1 y el
  rival frente a la mediana con la que suele reventar suma 3 · 5 · 7 según
  esté en zona, más fuerte o mucho más fuerte. Cada punto con su motivo.
  Confianza aparte: la muestra de reventones y la estabilidad (DT, ventana,
  bajas) la suben o la bajan, nunca el riesgo.
"""
from __future__ import annotations

import math
from datetime import datetime

FAMILIAS = ("total", "local", "visita")
CLAVE_FUSION = {"total": "k", "local": "kLocal", "visita": "kVisita"}

# nivel: fuera de este rango las globales pesan más (equipo grande o chico);
# dentro, las específicas de local/visita
BIN_GLOBALES_ALTO = 7
BIN_GLOBALES_BAJO = 2

# rival frente a la mediana del nivel con el que suele reventar, en la
# dirección del riesgo (más fuerte para la burbuja +, más flojo para la −):
# lejos (< −0.15) · zona (±0.15) · fuerte (≥ 0.15) · muy fuerte (≥ 0.45).
# Puntos calibrados con el backtest real del 16/09/2026 (docs/REVENTON.md §8):
# la logística dio 0.82 · 1.18 · 1.86 de log-odds, un punto cada 0.25.
ZONA_TOLERANCIA = 0.15
RIVAL_FUERTE = 0.45
PUNTOS_RIVAL = {"lejos": 0, "zona": 3, "fuerte": 5, "muy fuerte": 7}
PUNTOS_RACHA = 1               # racha ≥ mediana de partidos (coef 0.32)

# muestra de reventones que sostiene una guía
MUESTRA_BAJA = 3
MUESTRA_ALTA = 6

# estabilidad
DT_ASENTADO_DIAS = 90          # menos que esto: el patrón histórico es de otro DT
MOVIMIENTOS_TRANSICION = 3     # llegadas + salidas de la ventana
MOVIMIENTOS_INESTABLE = 6
BAJAS_TRANSICION = 5
PLANTILLA_VIEJA_DIAS = 30      # la ingesta de jugadores tiene esta edad o más
MAX_REVENTONES_SALIDA = 40     # los más recientes; la estadística usa TODOS

# Tasa de reventón OBSERVADA en el backtest real por nivel de riesgo (§8 del
# doc, segunda corrida del 16/09/2026, 171.260 burbujas, horizonte 1): es la
# referencia contra la que el bucle de aprendizaje compara lo que pasa en
# producción con los casos ciegos. Rango (mín, máx) porque cada nivel junta
# varios puntajes (bajo = 0-1 pts: 42.1-47.3 %; medio = 3 pts: 60.8 %; alto =
# 4-5: 67.2-69.2 %; muy alto = 6-8: 74.7-85.4 %). NO es un peso: no se usa
# para calcular nada, solo para decir «esperábamos esto».
TASA_BACKTEST = {"bajo": (0.421, 0.473), "medio": (0.608, 0.608),
                 "alto": (0.672, 0.692), "muy alto": (0.747, 0.854)}
TASA_BASE_BACKTEST = 0.60

AVISO = ("Guía, no probabilidad: compara la burbuja abierta con lo que este equipo aguantó "
         "antes de reventar (K, partidos y nivel del rival). Sirve para saber cuándo NO apostar.")


# ── utilidades numéricas (idénticas al espejo TS) ────────────────────────────

def _r2(x: float) -> float:
    return math.floor(x * 100 + 0.5) / 100


def _redondear(v: float, escala: int) -> float:
    return math.floor(v * escala + 0.5) / escala


def _dist(vals: list[float], escala_moda: int) -> dict | None:
    n = len(vals)
    if not n:
        return None
    s = sorted(vals)
    media = sum(s) / n
    mediana = s[n // 2] if n % 2 else (s[n // 2 - 1] + s[n // 2]) / 2
    conteo: dict[float, int] = {}
    for v in vals:
        b = _redondear(v, escala_moda)
        conteo[b] = conteo.get(b, 0) + 1
    mx = max(conteo.values())
    moda = min(b for b, c in conteo.items() if c == mx) if mx >= 2 else None
    return {
        "media": _r2(media),
        "mediana": _r2(mediana),
        "moda": None if moda is None else _r2(moda),
        "min": _r2(s[0]),
        "max": _r2(s[-1]),
    }


def _signo(v: float) -> int:
    return 1 if v > 0 else -1 if v < 0 else 0


def _dias_entre(desde: str | None, hoy: str) -> int | None:
    if not desde:
        return None
    try:
        a = datetime.strptime(str(desde)[:10], "%Y-%m-%d")
        b = datetime.strptime(str(hoy)[:10], "%Y-%m-%d")
    except ValueError:
        return None
    return (b - a).days


# ── episodios ────────────────────────────────────────────────────────────────

def _reventon(ep: dict, fila: dict) -> dict:
    return {
        "signo": "+" if ep["signo"] > 0 else "-",
        "partidos": ep["partidos"],
        "kPico": _r2(ep["kPico"]),
        "fixtureId": fila["fixtureId"],
        "fecha": fila["fecha"],
        "rivalId": fila["rivalId"],
        "rival": fila["rivalNombre"],
        "nivelRival": _r2(float(fila["nivelRival"])),
        "condicion": "L" if fila["condicion"] == "Local" else "V",
        "resultado": f"{fila['golesFavor']}-{fila['golesContra']}",
        "esInternacional": bool(fila.get("esInternacional")),
    }


def episodios(filas: list[dict], familia: str) -> tuple[list[dict], dict | None, int]:
    """Recorre la K fusionada de la familia. Devuelve (reventones cerrados,
    burbuja abierta o None, partidos en condición)."""
    clave = CLAVE_FUSION[familia]
    cerrados: list[dict] = []
    ep: dict | None = None
    n_cond = 0
    for fila in filas:
        if familia == "local" and fila["condicion"] != "Local":
            continue
        if familia == "visita" and fila["condicion"] != "Visita":
            continue
        n_cond += 1
        v = float(fila["fusion"][clave])
        s = _signo(v)
        if s == 0:
            if ep:
                cerrados.append(_reventon(ep, fila))
                ep = None
            continue
        if ep and ep["signo"] == s:
            ep["partidos"] += 1
            ep["kPico"] = max(ep["kPico"], abs(v))
            ep["k"] = v
            continue
        if ep:  # cambio de signo en el mismo partido: revienta y arranca la contraria
            cerrados.append(_reventon(ep, fila))
        ep = {"signo": s, "partidos": 1, "kPico": abs(v), "k": v, "desde": fila["fecha"]}
    return cerrados, ep, n_cond


def _historial(cerrados: list[dict]) -> dict:
    out = {}
    for signo, clave in (("+", "positivo"), ("-", "negativo")):
        de = [r for r in cerrados if r["signo"] == signo]
        if not de:
            out[clave] = None
            continue
        out[clave] = {
            "n": len(de),
            "kPico": _dist([r["kPico"] for r in de], 1),
            "partidos": _dist([float(r["partidos"]) for r in de], 1),
            "nivelRival": _dist([r["nivelRival"] for r in de], 10),
        }
    return out


# ── riesgo ───────────────────────────────────────────────────────────────────

def _nivel_riesgo(puntos: int) -> str:
    if puntos >= 6:
        return "muy alto"
    if puntos >= 4:
        return "alto"
    if puntos >= 2:
        return "medio"
    return "bajo"


def _confianza(n: int, estabilidad: dict) -> tuple[str, list[str]]:
    orden = ["baja", "media", "alta"]
    motivos = []
    if n < MUESTRA_BAJA:
        c = "baja"
        motivos.append(f"solo {n} {'reventón' if n == 1 else 'reventones'} de este signo en la historia")
    elif n < MUESTRA_ALTA:
        c = "media"
        motivos.append(f"{n} reventones de este signo: muestra corta")
    else:
        c = "alta"
        motivos.append(f"{n} reventones de este signo")
    grado = estabilidad["grado"]
    tope = {"estable": "alta", "en transición": "media", "inestable": "baja", "sin dato": "media"}[grado]
    if orden.index(tope) < orden.index(c):
        c = tope
        motivos.append(f"estabilidad {grado}: el patrón histórico puede ser de otro equipo")
    elif grado != "estable":
        motivos.append(f"estabilidad {grado}")
    return c, motivos


def _extremo(k_abs: float, partidos: int, base: dict, n_cond: int, signo: str) -> dict:
    """ALERTA DE EXTREMO: prudencia, no probabilidad.

    El backtest (docs/REVENTON.md §8) dice que una K récord no revienta más
    que otra: por eso NO puntúa en el riesgo. Pero una burbuja en su máximo
    histórico es terreno sin precedente para ESTE equipo, y ahí no se carga
    la apuesta a que siga: si revienta, revienta desde lo más alto. Alavés–
    Valencia (0-1, sept. 2026) salió «riesgo bajo» con la K de Valencia en
    −32 sobre un máximo previo de 24: el modelo estaba dentro de su tasa y
    quien puso la plata con esa confianza igual perdió. Esta bandera se
    enciende aparte del riesgo, viaja con el N de partidos y NO se puede
    saltar en el parte."""
    k_rec = k_abs >= base["kPico"]["max"]
    max_p = base["partidos"]["max"]
    max_p = int(max_p) if float(max_p).is_integer() else max_p  # «3 partidos», no «3.0»
    r_rec = partidos >= max_p
    motivos = []
    lado = "alta" if signo == "+" else "baja"
    if k_rec:
        motivos.append(f"K {_r2(k_abs)}: la más {lado} de los {n_cond} partidos que hay en la base "
                       f"(máximo previo {base['kPico']['max']})")
    if r_rec:
        motivos.append(f"{partidos} partidos seguidos: la racha más larga de los {n_cond} partidos que hay "
                       f"en la base (máximo previo {max_p})")
    return {
        "activo": k_rec or r_rec,
        "kRecord": k_rec,
        "rachaRecord": r_rec,
        "partidosHistoria": n_cond,
        "maximoPrevio": {"kPico": base["kPico"]["max"], "partidos": max_p},
        "motivos": motivos,
        "texto": ("" if not (k_rec or r_rec) else
                  "EXTREMO: la burbuja está en su máximo histórico. El modelo no lo puntúa como riesgo "
                  "(la tasa de reventón no sube con la K), pero es terreno sin precedente para este "
                  "equipo: no cargar la apuesta a que la racha siga"),
    }


# ── períodos: la misma referencia, acotada en el tiempo ──────────────────────
#
# El Universitario de hoy no es el de Fossati ni el de la gestión de Ferrari,
# y el City del primer Guardiola no es el de ahora: un cambio institucional
# grande cambia con qué K y ante qué rival revienta un equipo. La referencia
# global (toda la historia) sigue mandando en el riesgo —es la calibrada con
# el backtest—, pero al lado viajan las mismas medidas acotadas: esta
# temporada, este año, con el DT actual y los últimos N partidos. Son
# referencia para el que lee; con n chico dicen `n` y no dicen más. Se
# calculan sobre los MISMOS reventones (fecha en la que reventó dentro del
# período), no sobre episodios recortados: así un episodio nunca cambia de
# forma según la ventana.
ULTIMOS_N = 20


def periodos_de(filas: list[dict], plantilla: dict | None) -> list[dict]:
    """[{clave, etiqueta, desde, hasta, vigente, sinDato}] en orden fijo: todas
    las temporadas y todos los años que hay en la historia (uno por cada),
    el DT vigente y los últimos N. `desde` inclusivo y `hasta` exclusivo, en
    'YYYY-MM-DD'; `hasta` vacío = abierto. `vigente` marca el período en
    curso (la temporada y el año del último partido, el DT, los últimos N):
    la tarjeta muestra esos; la gráfica deja elegir cualquiera. Un período sin
    forma de cortar viaja con `sinDato`."""
    out = []
    if not filas:
        return out
    fecha = lambda f: str(f.get("fecha") or "")[:10]  # noqa: E731
    ultima = filas[-1]
    fecha_ultima = fecha(ultima)
    temporadas = sorted({f.get("temporada") for f in filas if f.get("temporada") is not None})
    if temporadas:
        inicio = {}
        for f in filas:
            t = f.get("temporada")
            if t is not None and t not in inicio:
                inicio[t] = fecha(f)
        for i, t in enumerate(temporadas):
            sig = temporadas[i + 1] if i + 1 < len(temporadas) else None
            out.append({"clave": f"temporada:{t}", "etiqueta": f"temporada {t}", "desde": inicio[t],
                        "hasta": inicio[sig] if sig is not None else "",
                        "vigente": t == ultima.get("temporada"), "sinDato": ""})
    else:
        out.append({"clave": "temporada", "etiqueta": "esta temporada", "desde": "", "hasta": "",
                    "vigente": True, "sinDato": "las filas no traen la temporada del torneo"})
    anios = sorted({fecha(f)[:4] for f in filas if fecha(f)})
    for a in anios:
        out.append({"clave": f"anio:{a}", "etiqueta": f"año {a}", "desde": f"{a}-01-01",
                    "hasta": f"{int(a) + 1}-01-01", "vigente": a == fecha_ultima[:4], "sinDato": ""})
    ent = (plantilla or {}).get("entrenador") or {}
    desde_dt = str(ent.get("desde") or "")[:10]
    if ent.get("nombre") and len(desde_dt) == 10:
        out.append({"clave": "dt", "etiqueta": f"con {ent['nombre']} (desde {desde_dt})", "desde": desde_dt,
                    "hasta": "", "vigente": True, "sinDato": ""})
    else:
        out.append({"clave": "dt", "etiqueta": "con el DT actual", "desde": "", "hasta": "", "vigente": True,
                    "sinDato": "sin DT con fecha de asunción en la plantilla"})
    corte = filas[-ULTIMOS_N] if len(filas) >= ULTIMOS_N else filas[0]
    out.append({"clave": f"ultimos{ULTIMOS_N}", "etiqueta": f"últimos {min(ULTIMOS_N, len(filas))} partidos",
                "desde": fecha(corte), "hasta": "", "vigente": True, "sinDato": ""})
    return out


def _en_periodo(fecha: str, per: dict) -> bool:
    f = str(fecha or "")[:10]
    return f >= per["desde"] and (not per.get("hasta") or f < per["hasta"])


def _historial_por_periodo(filas: list[dict], cerrados: list[dict], periodos: list[dict], familia: str) -> list[dict]:
    out = []
    for per in periodos:
        if per["sinDato"] or not per["desde"]:
            out.append({**per, "partidos": 0, "reventones": 0, "positivo": None, "negativo": None})
            continue
        de = [r for r in cerrados if _en_periodo(r["fecha"], per)]
        partidos = sum(1 for f in filas if _en_periodo(f.get("fecha"), per)
                       and (familia == "total" or f["condicion"] == ("Local" if familia == "local" else "Visita")))
        hist = _historial(de)
        out.append({**per, "partidos": partidos, "reventones": len(de),
                    "positivo": hist["positivo"], "negativo": hist["negativo"]})
    return out


def _analizar_familia(filas: list[dict], familia: str, proximo: dict | None, estabilidad: dict,
                      periodos: list[dict] | None = None) -> dict:
    cerrados, ep, n_cond = episodios(filas, familia)
    hist = _historial(cerrados)
    aplica = None if not proximo else (
        True if familia == "total" else proximo["condicion"] == ("L" if familia == "local" else "V"))
    out = {
        "familia": familia,
        "partidosEnCondicion": n_cond,
        "actual": None,
        "reventones": cerrados[-MAX_REVENTONES_SALIDA:],
        "historial": hist,
        "historialPorPeriodo": _historial_por_periodo(filas, cerrados, periodos or [], familia),
        "posicion": None,
        "rival": None,
        "riesgo": None,
        "extremo": None,
    }
    if not ep:
        return out
    signo = "+" if ep["signo"] > 0 else "-"
    k_abs = abs(ep["k"])
    out["actual"] = {
        "signo": signo,
        "k": _r2(ep["k"]),
        "partidos": ep["partidos"],
        "kPico": _r2(ep["kPico"]),
        "desde": ep["desde"],
        "aplicaAlProximo": aplica,
    }
    base = hist["positivo" if signo == "+" else "negativo"]
    if not base:
        out["riesgo"] = {
            "nivel": "sin base", "puntos": 0,
            "motivos": ["sin reventones previos de este signo: no hay con qué comparar"],
            "confianza": "baja",
            "confianzaMotivos": ["sin historia del signo"],
        }
        return out

    de = [r for r in cerrados if r["signo"] == signo]
    n = len(de)
    pct_k = math.floor(100 * sum(1 for r in de if r["kPico"] <= k_abs) / n + 0.5)
    pct_r = math.floor(100 * sum(1 for r in de if r["partidos"] <= ep["partidos"]) / n + 0.5)
    med_k = base["kPico"]["mediana"]
    out["posicion"] = {
        "percentilK": pct_k,
        "percentilRacha": pct_r,
        "kSobreMediana": None if med_k <= 0 else _r2(k_abs / med_k),
    }
    out["extremo"] = _extremo(k_abs, ep["partidos"], base, n_cond, signo)

    puntos = 0
    motivos = []
    # La K NO puntúa. El backtest real (docs/REVENTON.md §8, 171k burbujas)
    # mostró que estar por encima de la K con la que suele reventar no
    # adelanta el reventón (coeficiente negativo): una K alta es un equipo
    # fuerte, no una burbuja a punto. Se describe para ubicarla, nada más.
    if k_abs >= base["kPico"]["max"]:
        motivos.append(f"K {_r2(k_abs)}: nunca aguantó tanta (máximo previo {base['kPico']['max']}) · informativo, la K no puntúa")
    elif k_abs >= med_k:
        motivos.append(f"K {_r2(k_abs)} por encima de la mediana de reventón ({med_k}) · informativo, la K no puntúa")
    else:
        motivos.append(f"K {_r2(k_abs)} por debajo de la mediana de reventón ({med_k}) · informativo, la K no puntúa")
    med_p = base["partidos"]["mediana"]
    if ep["partidos"] >= med_p:
        puntos += PUNTOS_RACHA
        motivos.append(f"{ep['partidos']} partidos: en la mediana de racha ({med_p}) o más (+{PUNTOS_RACHA})")
    else:
        motivos.append(f"{ep['partidos']} partidos: por debajo de la mediana de racha ({med_p})")

    if proximo and aplica:
        med_n = base["nivelRival"]["mediana"]
        nivel_prox = float(proximo["nivelRival"])
        # distancia EN LA DIRECCIÓN DEL RIESGO: la burbuja + revienta ante rivales
        # más fuertes que la mediana; la − se corta ante rivales más flojos
        d = _r2((nivel_prox - med_n) if signo == "+" else (med_n - nivel_prox))
        tramo = ("lejos" if d < -ZONA_TOLERANCIA else "zona" if d < ZONA_TOLERANCIA
                 else "fuerte" if d < RIVAL_FUERTE else "muy fuerte")
        pts = PUNTOS_RIVAL[tramo]
        puntos += pts
        out["rival"] = {
            "nivelProximo": _r2(nivel_prox),
            "medianaReventon": med_n,
            "distancia": _r2(nivel_prox - med_n),
            "enZona": tramo != "lejos",
            "tramo": tramo,
        }
        quien = f"el próximo rival ({proximo['rival']}, nivel {_r2(nivel_prox)})"
        verbo = "reventar" if signo == "+" else "cortarse la racha"
        lado = "fuerte" if signo == "+" else "flojo"
        if tramo == "lejos":
            motivos.append(f"{quien} queda lejos del nivel con el que suele {verbo} (mediana {med_n})")
        elif tramo == "zona":
            motivos.append(f"{quien} está en la zona donde suele {verbo} (mediana {med_n}) (+{pts})")
        elif tramo == "fuerte":
            motivos.append(f"{quien} es más {lado} que los rivales con los que suele {verbo} (mediana {med_n}) (+{pts})")
        else:
            motivos.append(f"{quien} es mucho más {lado} que los rivales con los que suele {verbo} (mediana {med_n}) (+{pts})")
    elif proximo:
        motivos.append("la familia no se mueve en el próximo partido (otra condición): el rival no puntúa")
    else:
        motivos.append("sin próximo partido programado: el rival no puntúa")

    conf, conf_motivos = _confianza(n, estabilidad)
    out["riesgo"] = {
        "nivel": _nivel_riesgo(puntos),
        "puntos": puntos,
        "motivos": motivos,
        "confianza": conf,
        "confianzaMotivos": conf_motivos,
    }
    return out


# ── estabilidad ──────────────────────────────────────────────────────────────

def estabilidad_de(plantilla: dict | None, hoy: str) -> dict:
    """Grado de estabilidad a partir de la plantilla del contrato. Lo que no
    está en la base (dueños, organización) se DECLARA en sinDato."""
    sin_dato = ["dueños / organización que maneja el club: sin fuente en la base"]
    if not plantilla or not plantilla.get("jugadores"):
        return {
            "grado": "sin dato",
            "motivos": ["plantilla sin capturar: la ingesta de jugadores no corrió para este equipo"],
            "sinDato": sin_dato + ["cuerpo técnico", "plantel", "bajas"],
            "dt": None, "movimientos": None, "bajas": None, "actualizadoEn": None,
        }
    motivos = []
    grado = "estable"
    peor = lambda g: {"estable": 0, "en transición": 1, "inestable": 2}[g]  # noqa: E731

    def subir(g: str):
        nonlocal grado
        if peor(g) > peor(grado):
            grado = g

    ent = plantilla.get("entrenador") or None
    dt = None
    if ent and ent.get("nombre"):
        dias = _dias_entre(ent.get("desde"), hoy)
        dt = {"nombre": ent["nombre"], "desde": ent.get("desde"), "dias": dias}
        if dias is None:
            sin_dato.append("fecha de asunción del DT")
            motivos.append(f"DT {ent['nombre']} sin fecha de asunción")
        elif dias < DT_ASENTADO_DIAS:
            subir("inestable")
            motivos.append(f"DT {ent['nombre']} lleva {dias} días: la historia de K es de otro cuerpo técnico")
        else:
            motivos.append(f"DT {ent['nombre']} asentado ({dias} días)")
    else:
        sin_dato.append("cuerpo técnico")
        motivos.append("sin DT registrado")

    rev = plantilla.get("revolucion") or {"llegadas": 0, "salidas": 0, "ventanaDias": 0}
    mov = int(rev.get("llegadas", 0)) + int(rev.get("salidas", 0))
    movimientos = {"llegadas": int(rev.get("llegadas", 0)), "salidas": int(rev.get("salidas", 0)),
                   "ventanaDias": int(rev.get("ventanaDias", 0))}
    pal = "movimiento" if mov == 1 else "movimientos"
    if mov >= MOVIMIENTOS_INESTABLE:
        subir("inestable")
        motivos.append(f"{mov} {pal} en {movimientos['ventanaDias']} días: plantel en obra")
    elif mov >= MOVIMIENTOS_TRANSICION:
        subir("en transición")
        motivos.append(f"{mov} {pal} en {movimientos['ventanaDias']} días")
    else:
        motivos.append(f"{mov} {pal} en {movimientos['ventanaDias']} días: plantel quieto")

    # un flag «Missing Fixture» leído como ruido (media plantilla marcada) no
    # es una baja: no puede mover la estabilidad (docs/JUGADORES.md)
    bajas = sum(1 for j in plantilla["jugadores"]
                if j.get("baja") and (j["baja"] or {}).get("lectura") != "ruido")
    if bajas >= BAJAS_TRANSICION:
        subir("en transición")
        motivos.append(f"{bajas} bajas en la plantilla")

    act = plantilla.get("actualizadoEn")
    edad = _dias_entre(act, hoy) if act else None
    if edad is not None and edad >= PLANTILLA_VIEJA_DIAS:
        motivos.append(f"plantilla de hace {edad} días: el DT y las bajas pueden estar viejos")

    return {"grado": grado, "motivos": motivos, "sinDato": sin_dato, "dt": dt,
            "movimientos": movimientos, "bajas": bajas, "actualizadoEn": act}


# ── entrada ──────────────────────────────────────────────────────────────────

def regla_nivel(bin_: int, proximo: dict | None) -> dict:
    """La hipótesis del nivel: alto o bajo → globales; medio → la condición del
    próximo. Se conserva como dato porque el backtest NO la confirmó
    (docs/REVENTON.md §8): la total separa más en todos los niveles."""
    if bin_ >= BIN_GLOBALES_ALTO or bin_ <= BIN_GLOBALES_BAJO:
        return {
            "tipo": "globales",
            "familias": ["total"],
            "motivo": f"nivel {'alto' if bin_ >= BIN_GLOBALES_ALTO else 'bajo'} (bin {bin_}): pesarían más las globales",
            "confirmada": False,
        }
    fams = ["local", "visita"] if not proximo else ["local" if proximo["condicion"] == "L" else "visita"]
    return {
        "tipo": "especificas",
        "familias": fams,
        "motivo": f"nivel medio (bin {bin_}): pesarían más las de la condición"
                  + ("" if not proximo else f" — el próximo es de {'local' if proximo['condicion'] == 'L' else 'visita'}"),
        "confirmada": False,
    }


def mandan_de(bin_: int, proximo: dict | None) -> dict:
    """Qué familia pesa: la TOTAL, siempre. En el backtest real la total separa
    más que local/visita en nivel medio (0.25 vs 0.24) y en extremos (0.30 vs
    0.26), y «manda / no manda» por la regla del nivel da lo mismo. La regla
    viaja en reglaNivel para verla, no para decidir."""
    return {
        "tipo": "globales",
        "familias": ["total"],
        "motivo": "la familia total es la que más separa en el backtest (todos los niveles); "
                  "local y visita quedan como detalle",
        "reglaNivel": regla_nivel(bin_, proximo),
    }


def analizar(filas: list[dict], *, equipo_id: int, nivel: float, bin_: int,
             proximo: dict | None, plantilla: dict | None, hoy: str, nombre: str | None = None) -> dict:
    """`filas`: ConstantesDTO en orden CRONOLÓGICO. `proximo`: {fixtureId, fecha,
    rivalId, rival, condicion 'L'|'V', nivelRival} o None. `hoy`: 'YYYY-MM-DD'."""
    estabilidad = estabilidad_de(plantilla, hoy)
    periodos = periodos_de(filas, plantilla)
    return {
        "equipoId": equipo_id,
        "nombre": nombre,
        "nivel": _r2(float(nivel)),
        "bin": int(bin_),
        "partidos": len(filas),
        "mandan": mandan_de(int(bin_), proximo),
        "proximo": None if not proximo else {**proximo, "nivelRival": _r2(float(proximo["nivelRival"]))},
        "estabilidad": estabilidad,
        "familias": {f: _analizar_familia(filas, f, proximo, estabilidad, periodos) for f in FAMILIAS},
        "periodos": periodos,
        "aviso": AVISO,
    }
