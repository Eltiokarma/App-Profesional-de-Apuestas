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
- Riesgo de reventón por puntos CALIBRADOS con el backtest real y limpio de
  fuga (§13.2 del doc, 14/10/2026): la K no puntúa (no adelanta el
  reventón), la racha ≥ mediana suma 1, el rival frente a la mediana con la
  que suele reventar suma 0 · 1 · 2 según esté en zona, más fuerte o mucho
  más fuerte (`PUNTOS_RIVAL`), la contramano suma 1 y el favorito resta
  1 · 3. Cada punto con su motivo.
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
# Recalibrado el 14/10/2026 con el backtest LIMPIO (REVENTON §13.1: el rival
# medido ANTES del partido; la corrida de la mañana leía el nivel de después y
# daba AUC 0.715 con 2 · 3 · 5). Limpio: AUC 0.615, coef 0.10 · 0.19 · 0.38 →
# la zona sola ya no suma (medio punto, por debajo del paso).
PUNTOS_RIVAL = {"lejos": 0, "zona": 0, "fuerte": 1, "muy fuerte": 2}
PUNTOS_RACHA = 1               # racha ≥ mediana de partidos (coef 0.25 limpio)
# Las dos señales del backtest de las lecciones (REVENTON §12, 14/10/2026):
# la racha hecha en la condición contraria a la del próximo (+5,8 puntos de
# tasa SOBRE el riesgo; +2,2 en la corrida limpia) y la diferencia de nivel a
# favor de que la racha siga —el favorito con racha +, el débil con racha −—
# (−14,8 limpio, −20,6 con la fuga: la burbuja revienta MENOS y el riesgo no lo
# veía). Los puntos salen de `backtest_burbuja --calibrar`; los de favor RESTAN.
PUNTOS_CONTRAMANO = 1           # coef 0.207 (no depende del nivel del rival: igual con y sin fuga)
PUNTOS_FAVOR = {"no": 0, "favorito": -1, "muy favorito": -3}   # coef limpio −0.371 / −0.709
FAVORITO, MUY_FAVORITO = 0.5, 1.0

# muestra de reventones que sostiene una guía
MUESTRA_BAJA = 3
MUESTRA_ALTA = 6

# estabilidad
DT_ASENTADO_DIAS = 90          # menos que esto: el patrón histórico es de otro DT
# llegadas + salidas CON MINUTOS de la ventana (incidencia 43). Eran 3 y 6
# sobre el conteo en papeles; con los que juegan, la agenda del 23/10 (82
# equipos) dio 0 estables: el mercado de verano cambia 10+ jugadores con
# minutos en casi cualquier club y Arsenal (9, Arteta hace 7 años) salía tan
# «en obra» como Torino (28). Decisión del usuario (23/10/2026): 10 y 20.
# Primer corte, sin backtest: revisar con casos.
MOVIMIENTOS_TRANSICION = 10
MOVIMIENTOS_INESTABLE = 20
BAJAS_TRANSICION = 5
PLANTILLA_VIEJA_DIAS = 30      # la ingesta de jugadores tiene esta edad o más
MAX_REVENTONES_SALIDA = 40     # los más recientes; la estadística usa TODOS

# Tasa de reventón OBSERVADA en el backtest real por nivel de riesgo (§13.2 del
# doc, corrida LIMPIA del 14/10/2026, 173.615 observaciones, horizonte 1): es la
# referencia contra la que el bucle de aprendizaje compara lo que pasa en
# producción con los casos ciegos. Rango (mín, máx) porque cada nivel junta
# varios puntajes (bajo = −4 a −1 pts: 39.7-50.0 %; medio = 0: 55.2 %;
# alto = 1-2: 62.0-67.1 %; muy alto = 3+: 71.0-75.0 %). NO es un peso: no se
# usa para calcular nada, solo para decir «esperábamos esto».
TASA_BACKTEST = {"bajo": (0.397, 0.500), "medio": (0.552, 0.552),
                 "alto": (0.620, 0.671), "muy alto": (0.710, 0.750)}
TASA_BASE_BACKTEST = 0.60

# Cómo se mueve la K TOTAL en el partido siguiente, por signo y nivel de riesgo
# (backtest --calibrar limpio del 14/10/2026, 87.379 burbujas de la familia
# total, REVENTON §14): sigue · a cero (empate) · al otro signo. El «a cero»
# casi no cambia con el riesgo (25-28 %: la tasa de empates); lo que el riesgo
# mueve es seguir contra darse vuelta. Guía para la espina del parte, no peso.
MOVIMIENTO_BACKTEST = {
    "+": {"bajo": (0.539, 0.247, 0.213), "medio": (0.459, 0.264, 0.276),
          "alto": (0.352, 0.277, 0.371), "muy alto": (0.272, 0.269, 0.459)},
    "-": {"bajo": (0.523, 0.250, 0.227), "medio": (0.462, 0.272, 0.266),
          "alto": (0.354, 0.269, 0.378), "muy alto": (0.280, 0.273, 0.446)},
}


# Lo mismo para las K de la condición, en su próximo partido de esa condición
# (backtest --calibrar del 15/10/2026, padrón): la asimetría que el usuario ve
# en la cancha está en los números. La burbuja + DE LOCAL aguanta más que la
# total (sigue 63 % con riesgo bajo, contra 54 %) y la + DE VISITA menos (47 %);
# la − de visita es la que más se sostiene (61 %: el que pierde afuera sigue
# perdiendo afuera) y la − de local la que más se corta. Guía para la espina
# leída con la K de la condición (`guia: condicion`), no peso.
MOVIMIENTO_CONDICION = {
    "local": {
        "+": {"bajo": (0.627, 0.219, 0.154), "medio": (0.500, 0.262, 0.238),
              "alto": (0.426, 0.275, 0.299), "muy alto": (0.346, 0.288, 0.366)},
        "-": {"bajo": (0.454, 0.266, 0.280), "medio": (0.346, 0.292, 0.363),
              "alto": (0.267, 0.270, 0.463), "muy alto": (0.214, 0.255, 0.530)},
    },
    "visita": {
        "+": {"bajo": (0.468, 0.261, 0.272), "medio": (0.331, 0.289, 0.379),
              "alto": (0.273, 0.271, 0.456), "muy alto": (0.197, 0.256, 0.546)},
        "-": {"bajo": (0.607, 0.227, 0.166), "medio": (0.509, 0.257, 0.234),
              "alto": (0.418, 0.285, 0.297), "muy alto": (0.355, 0.276, 0.370)},
    },
}


def _movimiento_esperado(familia: str, signo: str, nivel: str) -> dict | None:
    tabla = MOVIMIENTO_BACKTEST if familia == "total" else MOVIMIENTO_CONDICION.get(familia, {})
    m = tabla.get(signo, {}).get(nivel)
    return None if not m else {"sigue": m[0], "cero": m[1], "cambio": m[2]}

# LA ESPINA DE LA TARJETA (19/10/2026, pedido del usuario: «la espina viene de
# las tarjetas, que tienen una base estadística»). Es el movimiento MÁS PROBABLE
# de la guía calibrada (`riesgo.movimiento`), dicho como resultado del equipo:
# sigue → la racha continúa (gana con +, pierde con −) · cero → empata ·
# cambio → se da vuelta. `fuerte` cuando ese movimiento llega al 50 %: con
# riesgo bajo «sigue» pesa 52-54 % y acertó 17 de 20 lados el 17-18/10; con
# riesgo alto los tres quedan casi parejos (35-46 %) y la tarjeta dice bien que
# la burbuja revienta, no cómo. Es el punto de partida del analista, no su
# respuesta: los skills la confirman o la contradicen, y Aprendizaje mide quién
# tenía razón (`acreditables.espina.tarjeta`).
ESPINA_FUERTE = 0.50


def espina_tarjeta(signo: str | None, movimiento: dict | None) -> dict | None:
    if signo not in ("+", "-") or not movimiento:
        return None
    mov, prob = max(((k, float(movimiento.get(k) or 0)) for k in ("sigue", "cero", "cambio")),
                    key=lambda kv: kv[1])
    lectura = {"sigue": "positiva" if signo == "+" else "negativa", "cero": "cero",
               "cambio": "negativa" if signo == "+" else "positiva"}[mov]
    return {"lectura": lectura, "movimiento": mov, "prob": round(prob, 3),
            "fuerza": "fuerte" if prob >= ESPINA_FUERTE else "debil"}


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

def _reventon(ep: dict, fila: dict, termina: str) -> dict:
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
        # CÓMO se cortó (14/10/2026): la K se REINICIÓ a 0 (empate) o pasó
        # directo al otro signo (la racha + perdió, la − ganó). Para leer el
        # partido no es lo mismo un equipo que primero empata que uno que se cae
        "termina": termina,
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
                cerrados.append(_reventon(ep, fila, "cero"))
                ep = None
            continue
        amistoso = 1 if fila.get("ligaId") in AMISTOSOS else 0
        if ep and ep["signo"] == s:
            ep["partidos"] += 1
            ep["amistosos"] += amistoso
            ep["kPico"] = max(ep["kPico"], abs(v))
            ep["k"] = v
            continue
        if ep:  # cambio de signo en el mismo partido: revienta y arranca la contraria
            cerrados.append(_reventon(ep, fila, "cambio"))
        ep = {"signo": s, "partidos": 1, "kPico": abs(v), "k": v, "desde": fila["fecha"], "amistosos": amistoso}
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
            # cómo se cortaron: a 0 (empate) o al otro signo (resultado opuesto)
            "termina": {"cero": sum(1 for r in de if r["termina"] == "cero"),
                        "cambio": sum(1 for r in de if r["termina"] == "cambio")},
        }
    return out


# ── riesgo ───────────────────────────────────────────────────────────────────

def _nivel_riesgo(puntos: int) -> str:
    # cortes de la corrida LIMPIA del 14/10/2026 sobre la tasa isotónica (§13.2):
    # con los puntos que RESTAN (favorito) el puntaje puede ser negativo
    if puntos >= 3:
        return "muy alto"
    if puntos >= 1:
        return "alto"
    if puntos >= 0:
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


# Franja alta: la burbuja abierta ya pasó al CERCA_PCT % de las de su signo
# que reventaron, sin llegar al récord. ADT (sept. 2026): K −17.9 con un
# récord previo de −19.5 y por encima del 95 % de sus 39 reventones negativos
# no encendía nada porque no era récord, y la pantalla decía «riesgo bajo» a
# secas. Es el mismo principio del extremo en un escalón más suave: no puntúa,
# no mueve el riesgo, dice cuánto se carga.
CERCA_PCT = 90
# RÉCORD DE RACHA: SUPERAR, y con 3 partidos o más (incidencia 67, decisión del
# usuario 23/10/2026). «2 seguidos por primera vez» gritaba EXTREMO en rojo
# igual que el Leipzig con 11 de local sobre un récord de 9; en la agenda del
# 23/10, 3 de 15 extremos eran rachas de 2 que solo IGUALABAN un máximo de 2
# (Cusco, Medellín, Juan Pablo II). Igualar el máximo con 3+ queda en ámbar
# (`cerca`, si pasa el 90 % de sus reventones); una racha de 1-2 no es récord
# ni «cerca». La K récord no cambia.
RACHA_RECORD_MIN = 3

# Amistosos de clubes (la liga de la API). CUENTAN en la burbuja —el
# espectáculo se arma para el hincha también en pretemporada, y una racha se
# construye o se rompe ahí con causas que interesan—, pero el extremo hecho
# con la mitad o más de amistosos se marca INFLADO: Lazio llegó a su racha
# récord de 9 con 5 de pretemporada y la Real Madrid a K-CERCA con 3 de 6
# (estudios de reventones fuera de Perú, 13/10/2026). La marca no apaga la
# alerta ni mueve el riesgo: dice de qué está hecho el récord.
AMISTOSOS = {667}


def _con_signo(v: float, signo: str) -> str:
    return f"{'+' if signo == '+' else '-'}{_r2(abs(v))}"


def _extremo(k_abs: float, partidos: int, base: dict, n_cond: int, signo: str,
             de: list[dict] | None = None, amistosos: int = 0) -> dict:
    """ALERTA DE EXTREMO: prudencia, no probabilidad.

    El backtest (docs/REVENTON.md §8) dice que una K récord no revienta más
    que otra: por eso NO puntúa en el riesgo. Pero una burbuja en su máximo
    histórico es terreno sin precedente para ESTE equipo, y ahí no se carga
    la apuesta a que siga: si revienta, revienta desde lo más alto. Alavés–
    Valencia (0-1, sept. 2026) salió «riesgo bajo» con la K de Valencia en
    −32 sobre un máximo previo de 24: el modelo estaba dentro de su tasa y
    quien puso la plata con esa confianza igual perdió. Esta bandera se
    enciende aparte del riesgo, viaja con el N de partidos y NO se puede
    saltar en el parte.

    `cerca` es el escalón de abajo (§10): sin récord, la K o la racha ya
    superan al CERCA_PCT % de los reventones del signo (estricto: «más alta
    que»). Se avisa en ámbar, no en rojo, y `activo` sigue siendo solo el
    récord: la alerta K-EXTREMO y el veredicto no cambian de significado."""
    k_rec = k_abs >= base["kPico"]["max"]
    max_p = base["partidos"]["max"]
    max_p = int(max_p) if float(max_p).is_integer() else max_p  # «3 partidos», no «3.0»
    r_rec = partidos > max_p and partidos >= RACHA_RECORD_MIN
    de = de or []
    n = len(de)
    pct_k = math.floor(100 * sum(1 for r in de if r["kPico"] < k_abs) / n + 0.5) if n else 0
    pct_r = math.floor(100 * sum(1 for r in de if r["partidos"] < partidos) / n + 0.5) if n else 0
    k_cerca = not k_rec and pct_k >= CERCA_PCT
    r_cerca = not r_rec and partidos >= RACHA_RECORD_MIN and pct_r >= CERCA_PCT
    cerca = not (k_rec or r_rec) and (k_cerca or r_cerca)
    motivos = []
    lado = "alta" if signo == "+" else "baja"
    k_txt, max_txt = _con_signo(k_abs, signo), _con_signo(base["kPico"]["max"], signo)
    if k_rec:
        motivos.append(f"K {k_txt}: la más {lado} de los {n_cond} partidos que hay en la base "
                       f"(récord previo {max_txt})")
    if r_rec:
        motivos.append(f"{partidos} partidos seguidos: la racha más larga de los {n_cond} partidos que hay "
                       f"en la base (máximo previo {max_p})")
    if cerca and k_cerca:
        motivos.append(f"K {k_txt}: más {lado} que el {pct_k} % de las {n} burbujas {signo} que reventaron "
                       f"(récord previo {max_txt}, a {_r2(base['kPico']['max'] - k_abs)})")
    if cerca and r_cerca:
        motivos.append(f"{partidos} partidos seguidos: más que el {pct_r} % de las {n} burbujas {signo} que "
                       f"reventaron (máximo previo {max_p})")
    texto = ""
    if k_rec or r_rec:
        texto = ("EXTREMO: la burbuja está en su máximo histórico. El modelo no lo puntúa como riesgo "
                 "(la tasa de reventón no sube con la K), pero es terreno sin precedente para este "
                 "equipo: no cargar la apuesta a que la racha siga")
    elif cerca:
        texto = (f"CERCA DEL EXTREMO: la burbuja está en la franja más alta de su historia (por encima "
                 f"del {CERCA_PCT} % de las que reventaron). El modelo no lo puntúa como riesgo, pero "
                 "queda poco margen antes del récord: no cargar fuerte a que la racha siga")
    inflada = None
    # o la racha récord solo es récord contando los amistosos (Saint-Étienne,
    # 2 de 7; Elversberg, 1 de 3 igualando un máximo de 3 — 14/10/2026)
    sin_am = partidos - amistosos
    solo_por_amistosos = (r_rec and not k_rec and amistosos > 0
                          and (sin_am <= max_p or sin_am < RACHA_RECORD_MIN))
    # LA MARCA VA EN CUALQUIER RACHA ABIERTA, no solo en el récord (incidencia
    # 311, decisión del usuario 23/10/2026): Stuttgart perdió 0-1 con el
    # Dortmund en casa y dos amistosos de septiembre (3-0 Heidenheim, 5-0
    # Fürth) le dieron «+18 de local, 2 seguidas»; nada lo decía. Los
    # amistosos siguen contando: la marca dice de qué está hecha la racha.
    if amistosos > 0 and (amistosos * 2 >= partidos or solo_por_amistosos):
        alerta = k_rec or r_rec or cerca
        inflada = {"amistosos": amistosos, "partidos": partidos,
                   "texto": f"INFLADA: {amistosos} de los {partidos} partidos de la racha son amistosos"
                            + (f" y sin ellos la racha ({sin_am}) no sería récord (máximo previo "
                               f"{max_p})" if solo_por_amistosos else "")
                            + (". Cuentan (la racha es del equipo), pero el récord se armó en buena parte fuera "
                               "de la competición: leer la alerta con eso a la vista" if alerta else
                               ". Cuentan (la racha es del equipo), pero se armó en buena parte fuera de la "
                               "competición: el último partido oficial puede contar otra historia")}
        if alerta:
            motivos.append(f"inflada: {amistosos} de {partidos} partidos de la racha son amistosos")
    return {
        "activo": k_rec or r_rec,
        "kRecord": k_rec,
        "inflada": inflada,
        "rachaRecord": r_rec,
        "cerca": cerca,
        "partidosHistoria": n_cond,
        "maximoPrevio": {"kPico": base["kPico"]["max"], "partidos": max_p},
        "motivos": motivos,
        "texto": texto,
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
                      periodos: list[dict] | None = None, *, franja: bool = False,
                      nivel_equipo: float | None = None) -> dict:
    """`franja=True` solo lo pide el backtest: agrega `_franja` con los
    percentiles ESTRICTOS de K y racha (los de `extremo.cerca`) para medir el
    umbral de la franja alta sin rehacer los episodios. La API no lo lleva."""
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
        "amistosos": ep.get("amistosos", 0),
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
    out["extremo"] = _extremo(k_abs, ep["partidos"], base, n_cond, signo, de, ep.get("amistosos", 0))
    if franja:
        out["_franja"] = {"pctK": 100 * sum(1 for r in de if r["kPico"] < k_abs) / n,
                          "pctR": 100 * sum(1 for r in de if r["partidos"] < ep["partidos"]) / n}

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
            motivos.append(f"{quien} está en la zona donde suele {verbo} (mediana {med_n})" + (f" (+{pts})" if pts else ""))
        elif tramo == "fuerte":
            motivos.append(f"{quien} es más {lado} que los rivales con los que suele {verbo} (mediana {med_n})" + (f" (+{pts})" if pts else ""))
        else:
            motivos.append(f"{quien} es mucho más {lado} que los rivales con los que suele {verbo} (mediana {med_n})" + (f" (+{pts})" if pts else ""))
        # A FAVOR DE QUE LA RACHA SIGA: el favorito con racha +, el débil con racha −
        if nivel_equipo is not None:
            g = _r2((float(nivel_equipo) - nivel_prox) if signo == "+" else (nivel_prox - float(nivel_equipo)))
            fav = "muy favorito" if g >= MUY_FAVORITO else "favorito" if g >= FAVORITO else "no"
            out["rival"]["aFavor"] = g
            out["rival"]["favorito"] = fav
            pf = PUNTOS_FAVOR[fav]
            puntos += pf
            if fav != "no":
                # dicho desde el lado de la racha: con racha − el favorito es el RIVAL
                # («el rival es mucho más fuerte … (favorito)» confundía, Albion 18/10)
                mucho = fav == "muy favorito"
                quien_f = (f"el equipo es {'muy ' if mucho else ''}favorito: {abs(g)} de nivel sobre el rival"
                           if signo == "+" else
                           f"el rival es {'mucho ' if mucho else ''}más fuerte: {abs(g)} de nivel sobre el equipo")
                motivos.append(f"{quien_f}, a favor de que la racha siga" + (f" ({pf:+d})" if pf else ""))
        # la racha hecha en la condición CONTRARIA a la del próximo partido
        racha = [f for f in filas if familia == "total" or f["condicion"] == ("Local" if familia == "local" else "Visita")]
        racha = racha[-ep["partidos"]:]
        cond_prox = "Local" if proximo["condicion"] == "L" else "Visita"
        contra = sum(1 for f in racha if f["condicion"] != cond_prox)
        if racha and contra * 3 >= 2 * len(racha):
            out["actual"]["contramano"] = True
            puntos += PUNTOS_CONTRAMANO
            motivos.append(f"{contra} de {len(racha)} partidos de la racha en la otra condición: el próximo es de "
                           f"{'local' if cond_prox == 'Local' else 'visita'}"
                           + (f" (+{PUNTOS_CONTRAMANO})" if PUNTOS_CONTRAMANO else ""))
        else:
            out["actual"]["contramano"] = False
    elif proximo:
        motivos.append("la familia no se mueve en el próximo partido (otra condición): el rival no puntúa")
    else:
        motivos.append("sin próximo partido programado: el rival no puntúa")

    conf, conf_motivos = _confianza(n, estabilidad)
    nivel = _nivel_riesgo(puntos)
    out["riesgo"] = {
        "nivel": nivel,
        "puntos": puntos,
        "motivos": motivos,
        "confianza": conf,
        "confianzaMotivos": conf_motivos,
        # la guía calibrada de adónde va la K con este riesgo; una familia que
        # no se mueve en el próximo (otra condición) no tiene adónde ir
        "movimiento": None if aplica is False else _movimiento_esperado(familia, signo, nivel),
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
        elif dias < DT_ASENTADO_DIAS and ent.get("fuente") == "coachs":
            # LA LLEGADA DE /coachs ES APROXIMADA (el mes de la carrera, a veces
            # meses corrida): Atlético-MG salía «inestable» con un DT de ~8 meses
            # que la base daba de 50 días (incidencia 186). Solo la llegada vista
            # en el banco (fuente alineacion) mueve la estabilidad; esta se declara.
            sin_dato.append("fecha de asunción del DT confirmada")
            motivos.append(f"DT {ent['nombre']}: la base dice {dias} días, pero la llegada es la aproximada de la "
                           "carrera de la API; no mueve la estabilidad hasta confirmarla en prensa")
        elif dias < DT_ASENTADO_DIAS:
            subir("inestable")
            motivos.append(f"DT {ent['nombre']} lleva {dias} días: la historia de K es de otro cuerpo técnico")
        elif ent.get("fuente") == "coachs":
            # asentado igual, pero los días de /coachs no son dato: Alavés salía
            # «asentado (387 días)» con 7,7 meses en el cargo (incidencia 385)
            sin_dato.append("fecha de asunción del DT confirmada")
            motivos.append(f"DT {ent['nombre']} asentado (unos {dias} días según la carrera de la API, "
                           "aproximado: confirmar en prensa)")
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
    # con minutos en el primer equipo (incidencia 43): si la plantilla trae el
    # total en papeles, se dice al lado para que se vea la diferencia
    pap = rev.get("enPapeles")
    if pap:
        pal += f" con minutos (de {int(pap.get('llegadas', 0)) + int(pap.get('salidas', 0))} en papeles)"
    if mov >= MOVIMIENTOS_INESTABLE:
        subir("inestable")
        motivos.append(f"{mov} {pal} en {movimientos['ventanaDias']} días: plantel en obra")
    elif mov >= MOVIMIENTOS_TRANSICION:
        subir("en transición")
        motivos.append(f"{mov} {pal} en {movimientos['ventanaDias']} días")
    else:
        motivos.append(f"{mov} {pal} en {movimientos['ventanaDias']} días: plantel quieto")

    # un flag «Missing Fixture» leído como ruido (media plantilla marcada) no
    # es una baja, ni una que el once desmintió: no mueven la estabilidad
    # (docs/JUGADORES.md)
    bajas = sum(1 for j in plantilla["jugadores"]
                if j.get("baja") and (j["baja"] or {}).get("lectura") not in ("ruido", "desmentida"))
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
        "familias": {f: _analizar_familia(filas, f, proximo, estabilidad, periodos, nivel_equipo=nivel)
                     for f in FAMILIAS},
        "periodos": periodos,
        "aviso": AVISO,
    }
