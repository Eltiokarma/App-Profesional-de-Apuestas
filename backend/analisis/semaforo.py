"""EL SEMÁFORO DEL ELEGIDO, POR LAS ESPINAS (13/11/2026; antes, 11/11/2026).

El usuario no lee la prosa del parte: mira la etiqueta del elegido, y este
color le dice si meter plata a ese lado o no. NO mira la cuota: «no
encontramos value a la cuota; el semáforo es el veredicto que dice: por más
que la casa diga esto, estas otras cosas hacen que mejor no apostemos».
Desde el 13/11/2026 el color sale de las ESPINAS que el analista escribió en
el parte (`lecturaSad.espina.{a,b}.lectura`, su lectura de las K de cada
equipo), CALCULADO aquí:

- 🟢 `confirma`: la espina del elegido lo acompaña (positiva = su K sigue
  ganando) y la del rival dice que el rival no sigue (negativa o neutra).
- 🟡 `duda`: la espina del elegido es cero (empate), o la del rival dice que
  el rival sigue (positiva) o empata (cero). `motivos` dice cuál.
- 🔴 `noApostar`: la espina del propio elegido es NEGATIVA: el analista leyó
  que su elegido pierde y lo eligió igual (Italia 3-1 Francia, 12/11/2026).
- ⚪ `sinDato`: sin el 1X2 o sin la espina del elegido (falta o es neutra).
- El elegido EMPATE: verde si las dos espinas dicen cero; si no, amarillo.

Medido el 13/11/2026 sobre 721 partes acreditables (14/09-12/11, sin copas
nacionales): con la espina del elegido positiva el elegido ganó 59 % (n 601),
con cero 44 % (34) y con negativa 26 % (19); la regla del amarillo («espina
del elegido negativa o cero, o la del rival positiva o cero») dio verde 59 %
contra amarillo 43 % (n 75), +16 pts al elegirla (hasta el 01/11) y +17 al
comprobarla (02/11-12/11). Se encontró en esos datos: cuenta hacia adelante
desde `DESDE` con un criterio fijo (`simulacion.resumen_semaforo`,
`docs/METODO_APUESTA.md`). La regla del 11/11 (≤ 2 pts de la casa y el
marcador con el elegido) quedó atrás: medía cercanía a la cuota, no
desconfianza, y pintaba verde casi todo.

`distancia` (nuestro 1X2 contra la casa) y `marcadorSigno` viajan como
información: NO deciden el color.

REGLA ANTI-GOODHART: el semáforo NO se le muestra a Cowork ni al analista
—ni en el recibo, ni en el prompt, ni en un endpoint que lea su token—. Lee
su espina; si viera el color, aprendería a escribirla a favor de su elegido.
Viaja en `/analisis/simulacion` y en `/analisis/semaforo`, que el token de
Cowork no abre (`backend/app.py`, `_COWORK_PERMITIDO`).
"""
from __future__ import annotations

import re

CLAVES = ("local", "empate", "visita")
# el criterio de las espinas cuenta desde los partidos del 13/11/2026, 00:00
# de Lima (UTC−5): la regla se eligió con los partidos hasta el 12/11
DESDE = "2026-11-13 05:00:00"
REGLA = "espinas"

ESTADOS = ("confirma", "duda", "noApostar", "sinDato")
LECTURAS = ("positiva", "cero", "negativa")
# qué lado es el elegido y cuál el rival, por equipo del parte (a = local)
_LADO = {"local": ("a", "b"), "visita": ("b", "a")}


def _pct(probs) -> dict | None:
    """El 1X2 normalizado a 100, o None si no está completo."""
    try:
        vals = {k: float(probs[k]) for k in CLAVES}
    except (KeyError, TypeError, ValueError):
        return None
    tot = sum(vals.values())
    if tot <= 0 or any(v < 0 for v in vals.values()):
        return None
    return {k: 100 * v / tot for k, v in vals.items()}


def signo_marcador(marcador) -> str | None:
    """local · empate · visita del marcador declarado («2-1», «1-1 (o 2-2)»:
    manda el primero, como en el veredicto). None si no hay un N-N."""
    m = re.search(r"(\d+)\s*[-–:]\s*(\d+)", str(marcador or ""))
    if not m:
        return None
    gl, gv = int(m.group(1)), int(m.group(2))
    return "local" if gl > gv else "visita" if gv > gl else "empate"


def _lectura(espinas, lado: str) -> str | None:
    """positiva · cero · negativa de la espina de un lado; None si falta o es
    neutra (la neutra no se juzga)."""
    e = (espinas or {}).get(lado)
    lec = e.get("lectura") if isinstance(e, dict) else e
    lec = str(lec or "").strip().lower()
    return lec if lec in LECTURAS else None


def semaforo(probs, espinas, mercado=None, marcador=None) -> dict:
    """`probs` = `pronostico.probabilidades` del parte (en % o en fracción, se
    normaliza); `espinas` = `lecturaSad.espina` ({a, b}, cada una con su
    `lectura`, o la lectura sola); `mercado` (el 1X2 de la casa SIN margen, en
    %) y `marcador` solo viajan como información."""
    p = _pct(probs)
    m = _pct(mercado) if mercado else None
    elegido = max(CLAVES, key=lambda k: p[k]) if p else None
    distancia = round(max(abs(p[k] - m[k]) for k in CLAVES), 1) if p and m else None
    lec_a, lec_b = _lectura(espinas, "a"), _lectura(espinas, "b")
    if elegido in _LADO:
        lado_e, lado_r = _LADO[elegido]
        esp_e, esp_r = (lec_a, lec_b) if lado_e == "a" else (lec_b, lec_a)
    else:
        esp_e = esp_r = None
    base = {"elegido": elegido, "regla": REGLA, "espinaElegido": esp_e, "espinaRival": esp_r,
            "espinas": {"a": lec_a, "b": lec_b},
            "distancia": distancia, "marcadorSigno": signo_marcador(marcador)}
    motivos = []
    if not p:
        motivos.append({"codigo": "SIN-1X2", "detalle": "el parte no trae el 1X2 completo"})
        return {"estado": "sinDato", "motivos": motivos, **base}
    if elegido == "empate":
        if lec_a is None or lec_b is None:
            motivos.append({"codigo": "SIN-ESPINA",
                            "detalle": "el elegido es el empate y falta la espina de un equipo (o es neutra)"})
            return {"estado": "sinDato", "motivos": motivos, **base}
        fuera = [x for x, lec in (("local", lec_a), ("visita", lec_b)) if lec != "cero"]
        if fuera:
            motivos.append({"codigo": "ESPINA-NO-EMPATA",
                            "detalle": "el elegido es el empate y la espina de " + " y ".join(
                                f"{x} dice {lec_a if x == 'local' else lec_b}" for x in fuera)})
        return {"estado": "duda" if motivos else "confirma", "motivos": motivos, **base}
    if esp_e is None:
        motivos.append({"codigo": "SIN-ESPINA",
                        "detalle": f"falta la espina del elegido ({elegido}) o es neutra: no se juzga"})
        return {"estado": "sinDato", "motivos": motivos, **base}
    if esp_e == "negativa":
        motivos.append({"codigo": "ESPINA-CONTRA-EL-ELEGIDO",
                        "detalle": f"la espina del elegido ({elegido}) dice que pierde: se lo eligió contra su propia lectura"})
    elif esp_e == "cero":
        motivos.append({"codigo": "ESPINA-ELEGIDO-EMPATA",
                        "detalle": f"la espina del elegido ({elegido}) dice empate, no que gane"})
    if esp_r in ("positiva", "cero"):
        motivos.append({"codigo": "ESPINA-RIVAL-SIGUE",
                        "detalle": f"la espina del rival dice {esp_r}: "
                                   + ("que gana" if esp_r == "positiva" else "que no pierde")})
    estado = "noApostar" if esp_e == "negativa" else "duda" if motivos else "confirma"
    return {"estado": estado, "motivos": motivos, **base}


def del_parte(parte: dict, mercado=None, dto: dict | None = None) -> dict:
    """El semáforo de un parte ya leído; el mercado sin margen en % (solo
    para `distancia`, que no decide). Con `dto` (el parte ENRIQUECIDO de
    `parte.dto`, lo que devuelve el GET) se calibra con las RAZONES
    (`calibrar`); sin él sale el color de las espinas solo, que es el que mide
    la serie fija de la simulación desde `DESDE`."""
    pron = (parte or {}).get("pronostico") or {}
    espinas = ((parte or {}).get("lecturaSad") or {}).get("espina") or {}
    s = semaforo(pron.get("probabilidades") or {}, espinas, mercado, pron.get("marcador"))
    s["estadoBase"] = s["estado"]
    s["calibrado"] = None
    if dto:
        s.update(calibrar(s, razones(dto, s.get("elegido"))))
    return s


# ── LAS RAZONES: el semáforo calibrado hacia atrás (25/11/2026) ──────────────
# El usuario, tras Manchester City (1 victoria en 7, seis veces en verde): «el
# analista dice semáforo en amarillo por tal razón, en rojo por tal razón, en
# verde por tal razón… viendo cuál razón se repite más y dándole más peso, a eso
# me refiero con calibrar. Eso incluye hacer que el verde no diga verde cuando
# perdimos». Las razones son lo que el parte sabía ANTES del pitazo (nunca el
# `veredicto`): alertas, burbujas y tarjetas calculadas, EFE, TDE, DTP, motor,
# ciego, DESCONFIAR, el 1X2 y el marcador, y lo que el analista escribió al
# justificar cada espina. El peso de cada una = log(su frecuencia en los VERDES
# que perdimos / en los verdes que ganamos), con suavizado; el puntaje de un
# partido es la suma. Medido en `backend/backtest_semaforo_razones.py`
# (docs/METODO_APUESTA.md, «El semáforo calibrado por razones»).
#
# - verde con puntaje ≥ CORTE → amarillo (las razones contra el elegido pesan);
# - amarillo con puntaje < CORTE → verde (las razones no lo confirman);
# - rojo → rojo; `confirmado` dice si las razones también lo sostienen.
#
# Los pesos se aprendieron SOLO con los verdes y separaron también los amarillos,
# que no vieron (con razones ganó 39,5 %, sin ellas 58,8 %, diciendo lo mismo).

_RAZONES_TEXTO = {
    "tarjeta fuerte": r"tarjeta fuerte", "tarjeta débil": r"tarjeta d[eé]bil",
    "sin tarjeta": r"sin tarjeta|k (total )?en (0|cero)",
    "deciden los skills": r"deciden? (los )?skills?|decide el skill", "contra el riesgo": r"contra el riesgo",
    "sigue al 1X2 (sin lectura propia)": r"sin lectura propia|sigue al 1x2", "riesgo muy alto": r"riesgo muy alto",
    "riesgo alto": r"riesgo alto", "riesgo bajo": r"riesgo bajo",
    "racha de un partido": r"(racha|burbuja)[^.]{0,30}de un partido|1 partido",
    "récord o extremo": r"r[eé]cord|extremo", "el corte al otro signo": r"otro signo|se corta|revienta|cambio de signo",
    "el mercado": r"mercado|cuota|casa", "el EFE": r"\befe\b", "el DTP": r"\bdtp\b|\bm2\b|carril|duelo",
    "el TDE": r"\btde\b|\bie\b|\bise\b", "el perfil DC": r"perfil|no pierde|doble oportunidad",
    "el once o las bajas": r"\bonce\b|rotaci|baja|lesi|suplente|titular", "el DT": r"t\.54|\bdt\b|entrenador",
    "la localía": r"de local|localía|de visita|en casa", "el nivel o μ": r"nivel|\bμ|favorito",
    "goles o volumen": r"xg|volumen|remat|goles",
}
_NUM3 = re.compile(r"(\d+(?:[.,]\d+)?)\s*/\s*(\d+(?:[.,]\d+)?)\s*/\s*(\d+(?:[.,]\d+)?)")
_MARC = re.compile(r"\s*(\d+)\s*-\s*(\d+)")


def _num(x):
    try:
        return float(x)
    except (TypeError, ValueError):
        return None


def razones(dto: dict, elegido: str | None) -> set[str]:
    """Las razones PREVIAS del parte enriquecido, orientadas al elegido y al rival.
    Sin elegido local o visita no hay razones (el empate no se calibra)."""
    if not isinstance(dto, dict) or elegido not in _LADO:
        return set()
    le, lr = _LADO[elegido]
    s: set[str] = set()
    pron = dto.get("pronostico") or {}
    ls = dto.get("lecturaSad") or {}
    p = _pct(pron.get("probabilidades") or {})

    # lo que el analista escribió al justificar cada espina
    esp = ls.get("espina") or {}
    for lado, quien in ((le, "espina elegido"), (lr, "espina rival")):
        e = esp.get(lado)
        t = str(e.get("porque") or "").lower() if isinstance(e, dict) else ""
        s |= {f"TXT[{quien}]:{k}" for k, rx in _RAZONES_TEXTO.items() if re.search(rx, t)}
    if isinstance(esp.get(le), dict) and esp[le].get("guia") == "pronostico":
        s.add("ESPINA-ELEGIDO-COPIA-1X2")

    # burbujas y tarjetas calculadas por la app
    rc = ls.get("reventonCalculado") or {}
    for lado, quien in ((le, "ELEGIDO"), (lr, "RIVAL")):
        r = rc.get(lado) or {}
        act = r.get("actual") or {}
        sg = act.get("signo")
        niv = (r.get("riesgo") or {}).get("nivel")
        s.add(f"BURB-{quien}-SIGNO{sg}" if sg else f"BURB-{quien}-SIN-RACHA")
        if sg and niv:
            s.add(f"BURB-{quien}{sg}-RIESGO-{niv}")
            if niv in ("alto", "muy alto"):
                s.add(f"BURB-{quien}{sg}-RIESGO-ALTO+")
        if sg and act.get("partidos") == 1:
            s.add(f"BURB-{quien}{sg}-DE-1")
        if act.get("contramano"):
            s.add(f"BURB-{quien}-CONTRAMANO")
        ex = r.get("extremo") or {}
        if ex.get("activo"):
            s.add(f"BURB-{quien}-EXTREMO")
        if ex.get("cerca"):
            s.add(f"BURB-{quien}-CERCA-EXTREMO")
        t = r.get("espinaTarjeta") or {}
        if t:
            s |= {f"TARJ-{quien}-{t.get('lectura')}-{t.get('fuerza')}", f"TARJ-{quien}-{t.get('lectura')}"}
        else:
            s.add(f"TARJ-{quien}-NINGUNA")
        c = r.get("condicion") or {}
        ca, cn = c.get("actual") or {}, (c.get("riesgo") or {}).get("nivel")
        if ca.get("signo") and cn in ("alto", "muy alto"):
            s.add(f"BURBCOND-{quien}{ca['signo']}-RIESGO-ALTO+")
        for fam in ((r.get("otrasFamilias") or {}).get("familias") or []):
            if fam.get("record") not in (None, "no") and fam.get("valor"):
                s.add(f"FAM-{quien}-RECORD-{fam.get('familia')}")
            if fam.get("cuidado"):
                s.add(f"FAM-{quien}-CUIDADO")

    # alertas del parte, por lado
    for a in dto.get("alertas") or []:
        if isinstance(a, dict) and a.get("codigo"):
            eq = a.get("equipo")
            s.add(f"AL-{a['codigo']}@" + ("ELEGIDO" if eq == le else "RIVAL" if eq == lr else "PARTIDO"))

    # EFE, disponibilidad, DT
    eqs = dto.get("equipos") or {}
    ee, er = eqs.get(le) or {}, eqs.get(lr) or {}
    pe_efe, pr_efe = _num(ee.get("porcentaje")), _num(er.get("porcentaje"))
    if pe_efe is not None and pr_efe is not None:
        if pe_efe < pr_efe:
            s.add("EFE-ELEGIDO-POR-DEBAJO")
        if abs(pe_efe - pr_efe) < 5:
            s.add("EFE-BRECHA<5")
        if pe_efe - pr_efe >= 10:
            s.add("EFE-ELEGIDO-10+ARRIBA")
    for q, eqd in (("ELEGIDO", ee), ("RIVAL", er)):
        if eqd.get("clasificacion"):
            s.add(f"EFE-{q}-{eqd['clasificacion']}")
        disp = eqd.get("disponibilidad") or {}
        if disp.get("ipNivel"):
            s.add(f"DISP-{q}-{disp['ipNivel']}")
        if disp.get("zonasCriticas"):
            s.add(f"DISP-{q}-ZONA-CRITICA")
        if disp.get("dudas"):
            s.add(f"DISP-{q}-DUDAS")
        if eqd.get("factorX"):
            s.add(f"FACTORX-{q}")
        m = _num((eqd.get("dt") or {}).get("meses"))
        if m is not None and m < 6:
            s.add(f"DT-{q}-<6M")
        if eqd.get("d3"):
            s.add(f"D3-{q}-{eqd['d3']}")

    # TDE
    for b in (dto.get("tde") or {}).get("bloques") or []:
        q = "ELEGIDO" if b.get("equipo") == le else "RIVAL" if b.get("equipo") == lr else None
        if not q:
            continue
        ie, ise = _num(b.get("ie")), _num(b.get("ise"))
        if ie is not None and ie >= 6:
            s.add(f"TDE-{q}-IE>=6")
        if ise is not None and ise >= 6:
            s.add(f"TDE-{q}-ISE>=6")
        if b.get("tipologia"):
            s.add(f"TDE-{q}-{b['tipologia']}")

    # DTP
    fav = (dto.get("matchup") or {}).get("favorece")
    s.add("DTP-FAVORECE-ELEGIDO" if fav == le else "DTP-FAVORECE-RIVAL" if fav == lr else "DTP-NEUTRO")
    for b in (dto.get("dtp") or {}).get("bloques") or []:
        q = "ELEGIDO" if b.get("equipo") == le else "RIVAL" if b.get("equipo") == lr else None
        if not q:
            continue
        v = ((b.get("apertura") or {}).get("m2") or {}).get("veredicto")
        if v:
            s.add(f"DTP-M2-{q}-{v}")
        cal = b.get("calculado") or {}
        if (cal.get("contraElOnce") or {}).get("rehacer"):
            s.add(f"DTP-{q}-REHACER")
        cl = (cal.get("bloqueRival") or {}).get("clase")
        if cl:
            s.add(f"DTP-{q}-BLOQUE-{cl}")

    # motor, ciego, entrar, DESCONFIAR, el 1X2 y el marcador
    pe = p[elegido] if p else None
    m = _NUM3.search(str(pron.get("motor") or ""))
    if m and pe is not None:
        v = [float(x.replace(",", ".")) for x in m.groups()]
        mot = v[0] if elegido == "local" else v[2]
        if pe - mot >= 10:
            s.add("MOTOR-10+BAJO-PUBLICADO")
        if pe - mot >= 20:
            s.add("MOTOR-20+BAJO-PUBLICADO")
        if max(range(3), key=lambda i: v[i]) != (0 if elegido == "local" else 2):
            s.add("MOTOR-NO-ELIGE-IGUAL")
    cg = dto.get("ciego") or {}
    if cg.get(elegido) is not None and pe is not None:
        if pe - float(cg[elegido]) >= 10:
            s.add("CIEGO-10+BAJO-PUBLICADO")
        if cg.get("elegido") not in (None, elegido):
            s.add("CIEGO-ELIGE-OTRO")
    ent = (pron.get("entrar") or {}).get("decision")
    if ent:
        s.add(f"ENTRAR-{ent}")
    if ((dto.get("desconfianza") or {}).get("alerta") or {}).get("activa"):
        s.add("DESCONFIAR")
    if elegido == "visita":
        s.add("ELEGIDO-VISITA")
    if p and p["empate"] >= 27:
        s.add("EMPATE-27+")
    mm = _MARC.match(str(pron.get("marcador") or ""))
    if mm:
        a, b = int(mm.group(1)), int(mm.group(2))
        s.add("MARCADOR-EMPATE" if a == b else "MARCADOR-POR-1" if abs(a - b) == 1 else "MARCADOR-POR-2+")
    return s


def texto_razon(codigo: str) -> str:
    """La razón en palabras, para el chip."""
    return _texto_razon(codigo).replace(" de el ", " del ").replace(" a el ", " al ")


def _texto_razon(codigo: str) -> str:
    quien = lambda q: "el elegido" if q == "ELEGIDO" else "el rival"  # noqa: E731
    if codigo.startswith("TXT["):
        lado, k = codigo[4:].split("]:", 1)
        return f"la {lado.replace('espina', 'espina del')} se apoya en {k}"
    m = re.match(r"AL-(.+)@(ELEGIDO|RIVAL|PARTIDO)$", codigo)
    if m:
        return f"alerta {m.group(1)}" + ("" if m.group(2) == "PARTIDO" else f" sobre {quien(m.group(2))}")
    m = re.match(r"BURB(COND)?-(ELEGIDO|RIVAL)([+-])-RIESGO-(.+)$", codigo)
    if m:
        racha = "ganar" if m.group(3) == "+" else "no ganar"
        cond = " en su condición" if m.group(1) else ""
        return f"{quien(m.group(2))} viene de {racha}{cond}, riesgo {m.group(4).replace('ALTO+', 'alto o muy alto')} de que se corte"
    m = re.match(r"BURB-(ELEGIDO|RIVAL)([+-])-DE-1$", codigo)
    if m:
        return f"{quien(m.group(1))} tiene una racha de {'ganar' if m.group(2) == '+' else 'no ganar'} de un solo partido"
    m = re.match(r"TARJ-(ELEGIDO|RIVAL)-(\w+)(?:-(\w+))?$", codigo)
    if m:
        if m.group(2) == "NINGUNA":
            return f"{quien(m.group(1))} no tiene tarjeta de burbuja"
        return f"la tarjeta de {quien(m.group(1))} dice {m.group(2)}" + (f" ({m.group(3)})" if m.group(3) else "")
    m = re.match(r"FAM-(ELEGIDO|RIVAL)-RECORD-(.+)$", codigo)
    if m:
        return f"{quien(m.group(1))} está en récord de «{m.group(2)}»"
    m = re.match(r"DTP-M2-(ELEGIDO|RIVAL)-(.+)$", codigo)
    if m:
        return f"el DTP de {quien(m.group(1))} da {m.group(2).lower()}"
    fijos = {
        "EMPATE-27+": "le dimos al empate 27 % o más (partido parejo)",
        "MARCADOR-EMPATE": "el marcador declarado es un empate", "MARCADOR-POR-1": "el marcador declarado es por un gol",
        "DTP-NEUTRO": "el DTP no favorece a ningún lado", "DTP-FAVORECE-ELEGIDO": "el DTP favorece al elegido",
        "DTP-FAVORECE-RIVAL": "el DTP favorece al rival", "DESCONFIAR": "saltó DESCONFIAR",
        "MOTOR-10+BAJO-PUBLICADO": "el motor da 10+ puntos menos que lo publicado",
        "MOTOR-20+BAJO-PUBLICADO": "el motor da 20+ puntos menos que lo publicado",
        "MOTOR-NO-ELIGE-IGUAL": "el motor elige otro resultado", "CIEGO-ELIGE-OTRO": "el ciego eligió otro resultado",
        "CIEGO-10+BAJO-PUBLICADO": "el ciego daba 10+ puntos menos", "ELEGIDO-VISITA": "el elegido juega de visita",
        "EFE-ELEGIDO-POR-DEBAJO": "el EFE del elegido queda por debajo del rival",
        "EFE-BRECHA<5": "el EFE de los dos está a menos de 5 puntos",
        "ESPINA-ELEGIDO-COPIA-1X2": "la espina del elegido copia el 1X2 (sin lectura propia)",
    }
    return fijos.get(codigo, codigo)


def calibrar(base: dict, rz: set[str], pesos: dict | None = None, corte: float | None = None) -> dict:
    """El color calibrado por las razones (ver arriba). Devuelve lo que se suma al
    semáforo: `estado` (calibrado), `estadoBase`, `calibrado` {puntaje, corte,
    confirmado, contra, aFavor}. `pesos` y `corte` de afuera solo para el backtest."""
    pesos = PESOS if pesos is None else pesos
    corte = CORTE if corte is None else corte
    est = base.get("estado")
    con = sorted(((pesos[c], c) for c in rz if pesos.get(c, 0) > 0), reverse=True)
    fav = sorted((pesos[c], c) for c in rz if pesos.get(c, 0) < 0)
    puntaje = round(sum(w for w, _ in con) + sum(w for w, _ in fav), 3)
    alto = puntaje > 0 and puntaje >= corte   # sin razones en contra nunca baja un verde
    nuevo = est
    if est == "confirma" and alto:
        nuevo = "duda"
    elif est == "duda" and not alto and base.get("elegido") in _LADO:
        nuevo = "confirma"
    fila = lambda w, c: {"codigo": c, "texto": texto_razon(c), "peso": round(w, 2)}  # noqa: E731
    return {
        "estado": nuevo, "estadoBase": est,
        "calibrado": {
            "puntaje": puntaje, "corte": corte, "cambio": nuevo != est,
            "confirmado": alto if est in ("duda", "noApostar") else (not alto if est == "confirma" else None),
            "contra": [fila(w, c) for w, c in con[:5]], "aFavor": [fila(w, c) for w, c in fav[:3]],
            "fuente": CALIBRACION,
        },
    }


# Pesos y corte: `python -m backend.backtest_semaforo_razones --desde-json …
# --tabla` (aprende con TODOS los verdes; la comprobación temporal está en
# docs/METODO_APUESTA.md). Recalibrar = correr eso y pegar la salida acá.
CALIBRACION = {"fecha": "2026-11-25", "partes": 1018, "verdes": 787, "desde": "2026-09-14", "hasta": "2026-11-25"}
CORTE = 2.264
PESOS: dict[str, float] = {
    "AL-DTP-SIN-REFERENCIA@RIVAL": 0.763,
    "AL-G-CLÁSICO@PARTIDO": 0.618,
    "BURBCOND-RIVAL--RIESGO-ALTO+": 0.584,
    "AL-G-SORPRESA@RIVAL": 0.569,
    "MARCADOR-EMPATE": 0.567,
    "FAM-RIVAL-RECORD-mas2.5": 0.541,
    "BURB-RIVAL--RIESGO-muy alto": 0.531,
    "EMPATE-27+": 0.519,
    "DTP-M2-ELEGIDO-NEUTRO": 0.501,
    "DTP-NEUTRO": 0.5,
    "BURB-ELEGIDO--RIESGO-alto": 0.487,
    "DESCONFIAR": 0.485,
    "AL-DESCONFIAR@ELEGIDO": 0.485,
    "DTP-M2-RIVAL-NEUTRO": 0.481,
    "AL-1X2-CARGA-CONTRA-RIESGO@PARTIDO": 0.477,
    "AL-T.54-B@ELEGIDO": 0.455,
    "TXT[espina elegido]:el TDE": 0.452,
    "TDE-RIVAL-ECHADA-PSI": 0.438,
    "TXT[espina elegido]:racha de un partido": 0.423,
    "EFE-ELEGIDO-SIN_FORMACION": 0.413,
    "AL-R-KT.2@ELEGIDO": 0.403,
    "FAM-ELEGIDO-RECORD-pierde2+": 0.399,
    "TARJ-RIVAL-positiva-debil": 0.39,
    "AL-DT-DISCREPANCIA@ELEGIDO": 0.384,
    "TXT[espina rival]:contra el riesgo": 0.383,
    "AL-EJE-DEBUTANTE@ELEGIDO": 0.374,
    "BURB-RIVAL--RIESGO-ALTO+": 0.359,
    "EFE-BRECHA<5": 0.358,
    "TARJ-RIVAL-positiva": 0.356,
    "BURBCOND-ELEGIDO+-RIESGO-ALTO+": 0.34,
    "AL-DTP-SIN-REFERENCIA@ELEGIDO": 0.34,
    "TXT[espina elegido]:sin tarjeta": 0.34,
    "TXT[espina rival]:goles o volumen": 0.34,
    "TXT[espina elegido]:deciden los skills": 0.34,
    "TXT[espina rival]:el TDE": 0.34,
    "BURB-RIVAL--RIESGO-alto": 0.318,
    "EFE-ELEGIDO-POR-DEBAJO": 0.301,
    "TXT[espina rival]:riesgo alto": 0.298,
    "BURB-RIVAL+-RIESGO-alto": 0.271,
    "BURB-ELEGIDO--DE-1": 0.267,
    "ENTRAR-dudo": 0.257,
    "DISP-RIVAL-ZONA-CRITICA": -0.266,
    "AL-R-KT.2@RIVAL": -0.267,
    "TXT[espina rival]:el nivel o μ": -0.271,
    "MOTOR-NO-ELIGE-IGUAL": -0.276,
    "AL-G-BLOQUE@ELEGIDO": -0.285,
    "EFE-ELEGIDO-FORMADO": -0.299,
    "TXT[espina elegido]:riesgo bajo": -0.301,
    "TXT[espina rival]:tarjeta fuerte": -0.306,
    "TDE-RIVAL-ECHADA-FIS": -0.319,
    "AL-TIPOLOGIA-VS-INDICES@RIVAL": -0.331,
    "TARJ-RIVAL-negativa-fuerte": -0.338,
    "BURB-RIVAL--RIESGO-bajo": -0.338,
    "BURB-ELEGIDO+-RIESGO-bajo": -0.365,
    "TARJ-ELEGIDO-positiva-fuerte": -0.365,
    "AL-ESCALA-LIGAS@PARTIDO": -0.369,
    "FAM-ELEGIDO-RECORD-ambosMarcan": -0.376,
    "TXT[espina rival]:el perfil DC": -0.389,
    "CIEGO-10+BAJO-PUBLICADO": -0.397,
    "FAM-RIVAL-RECORD-recibe": -0.415,
    "FAM-RIVAL-RECORD-pierde2+": -0.422,
    "AL-DIV-MOTOR-MERCADO@PARTIDO": -0.439,
    "DTP-ELEGIDO-BLOQUE-estructural": -0.467,
    "FAM-RIVAL-RECORD-noGana": -0.481,
    "D3-ELEGIDO-si": -0.485,
    "D3-RIVAL-no": -0.507,
    "TXT[espina rival]:riesgo bajo": -0.522,
    "TXT[espina elegido]:récord o extremo": -0.527,
    "BURB-ELEGIDO+-RIESGO-medio": -0.533,
    "ENTRAR-entraria": -0.598,
    "BURB-ELEGIDO-CERCA-EXTREMO": -0.609,
    "AL-K-CERCA-EXTREMO@ELEGIDO": -0.609,
    "AL-G-ASCENDIDO@ELEGIDO": -0.629,
    "AL-K-EXTREMO-CONDICION@ELEGIDO": -0.629,
    "AL-TIPOLOGIA-VS-INDICES@ELEGIDO": -0.65,
    "AL-K-EXTREMO@ELEGIDO": -0.696,
    "BURB-ELEGIDO-EXTREMO": -0.696,
    "AL-K-EXTREMO-CONDICION@RIVAL": -0.696,
    "AL-COLAPSO-EN-CASCADA@RIVAL": -0.706,
    "FAM-RIVAL-RECORD-gana3+": -0.758,
    "FAM-ELEGIDO-RECORD-mas2.5": -0.758,
    "AL-K-EXTREMO@RIVAL": -0.758,
    "BURB-RIVAL-EXTREMO": -0.758,
    "MOTOR-10+BAJO-PUBLICADO": -0.78,
    "TARJ-ELEGIDO-negativa-fuerte": -0.933,
    "BURB-ELEGIDO--RIESGO-bajo": -0.933,
    "MOTOR-20+BAJO-PUBLICADO": -1.038,
    "FAM-RIVAL-RECORD-gana2+": -1.068,
    "AL-DIV-MOTOR-MERCADO@ELEGIDO": -1.139,
    "AL-G-SORPRESA@ELEGIDO": -1.269,
    "MARCADOR-POR-2+": -1.335,
}


def de_partidos(ids) -> dict[int, dict]:
    """{fixtureId: semáforo} de los partidos con parte, para la web. La cuota
    (solo para `distancia`) es la misma de la simulación
    (`lecciones.cuotas_mercado`: la última captura prepartido, media de las
    casas, sin margen)."""
    import json

    from backend.analisis.lecciones import cuotas_mercado
    from backend.analisis.parte import _conectar
    ids = sorted({int(i) for i in ids})[:300]
    if not ids:
        return {}
    with _conectar() as con:
        filas = con.execute(
            "SELECT fixture_id, parte_json FROM parte_cowork "
            f"WHERE fixture_id IN ({','.join('?' * len(ids))})", tuple(ids)).fetchall()
    mercados = cuotas_mercado([f["fixture_id"] for f in filas])
    from backend.analisis.parte import dto as parte_dto
    out = {}
    for f in filas:
        try:
            parte = json.loads(f["parte_json"])
        except (TypeError, ValueError):
            continue
        try:
            enriquecido = parte_dto(f["fixture_id"])
        except Exception:  # noqa: BLE001 — sin el parte enriquecido el color sale de las espinas solas (estadoBase)
            enriquecido = None
        out[f["fixture_id"]] = del_parte(parte, (mercados.get(f["fixture_id"]) or {}).get("prob"), enriquecido)
    return out
