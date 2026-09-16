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
- Qué constante manda: nivel alto o bajo (bin ≥ 7 o ≤ 2) → las globales;
  nivel medio → las específicas de la condición del próximo partido.
- Riesgo de reventón por puntos, cada punto con su motivo. Confianza aparte:
  la muestra de reventones y la estabilidad (DT, ventana, bajas) la suben o
  la bajan, nunca el riesgo.
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

# rival en zona de reventón: a esta distancia (o más allá) de la mediana del
# nivel con el que suele reventar
ZONA_TOLERANCIA = 0.15

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


def _analizar_familia(filas: list[dict], familia: str, proximo: dict | None, estabilidad: dict) -> dict:
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
        "posicion": None,
        "rival": None,
        "riesgo": None,
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

    puntos = 0
    motivos = []
    if k_abs >= med_k:
        puntos += 2
        motivos.append(f"K {_r2(k_abs)} ya está en la mediana con la que revienta ({med_k})")
    elif k_abs >= base["kPico"]["min"]:
        puntos += 1
        motivos.append(f"ya reventó con menos K que la actual (mínimo {base['kPico']['min']})")
    else:
        motivos.append(f"K {_r2(k_abs)} por debajo de todo reventón previo (mínimo {base['kPico']['min']})")
    if k_abs >= base["kPico"]["max"]:
        puntos += 1
        motivos.append(f"nunca aguantó tanta K (máximo previo {base['kPico']['max']})")
    med_p = base["partidos"]["mediana"]
    if ep["partidos"] >= med_p:
        puntos += 1
        motivos.append(f"{ep['partidos']} partidos: en la mediana de racha ({med_p}) o más")
    else:
        motivos.append(f"{ep['partidos']} partidos: por debajo de la mediana de racha ({med_p})")
    if ep["partidos"] >= base["partidos"]["max"]:
        puntos += 1
        motivos.append(f"nunca sostuvo una racha más larga (máximo previo {int(base['partidos']['max'])})")

    if proximo and aplica:
        med_n = base["nivelRival"]["mediana"]
        nivel_prox = float(proximo["nivelRival"])
        distancia = _r2(nivel_prox - med_n)
        # burbuja positiva: revienta ante rivales de este nivel o más;
        # negativa: la racha de derrotas se corta ante rivales de este nivel o menos
        en_zona = (nivel_prox >= med_n - ZONA_TOLERANCIA) if signo == "+" else (nivel_prox <= med_n + ZONA_TOLERANCIA)
        out["rival"] = {
            "nivelProximo": _r2(nivel_prox),
            "medianaReventon": med_n,
            "distancia": distancia,
            "enZona": en_zona,
        }
        if en_zona:
            puntos += 2
            motivos.append(
                f"el próximo rival ({proximo['rival']}, nivel {_r2(nivel_prox)}) está en la zona "
                f"donde suele {'reventar' if signo == '+' else 'cortarse la racha'} (mediana {med_n})")
        else:
            motivos.append(
                f"el próximo rival ({proximo['rival']}, nivel {_r2(nivel_prox)}) queda "
                f"{'por debajo' if signo == '+' else 'por encima'} de la zona de reventón (mediana {med_n})")
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

    bajas = sum(1 for j in plantilla["jugadores"] if j.get("baja"))
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

def mandan_de(bin_: int, proximo: dict | None) -> dict:
    if bin_ >= BIN_GLOBALES_ALTO or bin_ <= BIN_GLOBALES_BAJO:
        return {
            "tipo": "globales",
            "familias": ["total"],
            "motivo": f"nivel {'alto' if bin_ >= BIN_GLOBALES_ALTO else 'bajo'} (bin {bin_}): pesan más las constantes globales",
        }
    fams = ["local", "visita"] if not proximo else ["local" if proximo["condicion"] == "L" else "visita"]
    return {
        "tipo": "especificas",
        "familias": fams,
        "motivo": f"nivel medio (bin {bin_}): pesan más las constantes de la condición"
                  + ("" if not proximo else f" — el próximo es de {'local' if proximo['condicion'] == 'L' else 'visita'}"),
    }


def analizar(filas: list[dict], *, equipo_id: int, nivel: float, bin_: int,
             proximo: dict | None, plantilla: dict | None, hoy: str, nombre: str | None = None) -> dict:
    """`filas`: ConstantesDTO en orden CRONOLÓGICO. `proximo`: {fixtureId, fecha,
    rivalId, rival, condicion 'L'|'V', nivelRival} o None. `hoy`: 'YYYY-MM-DD'."""
    estabilidad = estabilidad_de(plantilla, hoy)
    return {
        "equipoId": equipo_id,
        "nombre": nombre,
        "nivel": _r2(float(nivel)),
        "bin": int(bin_),
        "partidos": len(filas),
        "mandan": mandan_de(int(bin_), proximo),
        "proximo": None if not proximo else {**proximo, "nivelRival": _r2(float(proximo["nivelRival"]))},
        "estabilidad": estabilidad,
        "familias": {f: _analizar_familia(filas, f, proximo, estabilidad) for f in FAMILIAS},
        "aviso": AVISO,
    }
