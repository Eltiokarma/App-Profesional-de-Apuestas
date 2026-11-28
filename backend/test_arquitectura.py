"""EL ESCANEO PREVENTIVO DEL CÓDIGO (30/10/2026, pedido del usuario: «un
escaneo preventivo sobre nuestro código, para en el futuro no fallar»).

El escaneo de `backend/analisis/escaneo.py` mira los DATOS. Este mira el
CÓDIGO: cada regla nace de una clase de falla que ya pasó (docs/FALLAS.md) y
falla en CI si alguien la vuelve a abrir, antes de que llegue a un parte. Una
clase de falla nueva que se pueda verificar leyendo el repo se suma acá.

    python -m backend.test_arquitectura
"""
import ast as _ast
import glob
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
fallos = 0


def check(nombre, cond, detalle=""):
    global fallos
    if not cond:
        fallos += 1
    print(f"{'OK ' if cond else 'FALLA'} {nombre}" + (f" -> {detalle}" if detalle and not cond else ""))


def leer(rel: str) -> str:
    with open(os.path.join(RAIZ, rel), encoding="utf-8") as f:
        return f.read()


def fuentes() -> list[str]:
    """El código del backend, sin los tests."""
    return sorted(os.path.relpath(p, RAIZ) for p in glob.glob(os.path.join(RAIZ, "backend", "**", "*.py"), recursive=True)
                  if not os.path.basename(p).startswith("test_"))


# ── 1 · QUIÉN ES QUIÉN SE DECIDE EN UN SOLO LUGAR (FALLAS.md: identidad) ────
# La identidad del jugador se parchó ocho veces en un mes en cinco módulos con
# cuatro versiones de «una letra». Comparar letras de nombres fuera de
# backend/identidad.py vuelve a abrir esa clase.
_LETRAS = re.compile(r"sum\(\s*\w+\s*!=\s*\w+\s+for\s+\w+\s*,\s*\w+\s+in\s+zip|SequenceMatcher")
_DEF_IDENTIDAD = re.compile(r"^def (mismo_jugador|misma_pila|apellido_casi|_casi_igual|_casi|_una_letra_|mismo_dt|"
                            r"mismo_nombre_dt)\(", re.M)
fuera = []
for rel in fuentes():
    if rel == os.path.join("backend", "identidad.py"):
        continue
    txt = leer(rel)
    fuera += [f"{rel}: {m.group(0)}" for m in _LETRAS.finditer(txt)]
    fuera += [f"{rel}: def {m.group(1)}" for m in _DEF_IDENTIDAD.finditer(txt)]
check("identidad: ninguna comparación de letras de nombres fuera de backend/identidad.py", not fuera, fuera)
# …ni otra forma de quitar tildes a un NOMBRE (incidencia 811: el NFKD suelto de
# dtp_cowork tiraba la «ð»). Fuera de identidad.py solo se normaliza texto que
# no es un nombre de persona, con su motivo:
NFKD_PERMITIDO = {os.path.join("backend", "analisis", "incidencias.py"): "títulos de incidencias, no nombres",
                  os.path.join("backend", "analisis", "parte.py"): "_palabras: nombres de liga/torneo, no personas"}
nfkd = [rel for rel in fuentes() if rel != os.path.join("backend", "identidad.py") and rel not in NFKD_PERMITIDO
        and 'normalize("NFKD"' in leer(rel)]
check("identidad: ningún módulo quita tildes a un nombre por su cuenta (usa identidad.plano)", not nfkd, nfkd)

# ── 2 · UN TEST QUE NO CORRE NO PROTEGE (FALLAS.md: tests fuera de CI) ──────
# El 30/10/2026 siete tests existían y CI no los corría (Jev, coherencia, modo
# de fallo, familias…): se podían romper sin que nadie lo viera.
ci = leer(os.path.join(".github", "workflows", "ci.yml"))
FUERA_DE_CI = {"backend.ingesta.test_paridad": "compara contra las bases del pipeline viejo, que no viven en el repo"}
tests = sorted(os.path.splitext(os.path.relpath(p, RAIZ))[0].replace(os.sep, ".")
               for p in glob.glob(os.path.join(RAIZ, "backend", "test_*.py"))
               + glob.glob(os.path.join(RAIZ, "backend", "ingesta", "test_*.py")))
sin_ci = [t for t in tests if f"python -m {t}" not in ci and t not in FUERA_DE_CI]
check("CI: cada test del backend corre en CI (o está en FUERA_DE_CI con su motivo)", not sin_ci, sin_ci)
import json  # noqa: E402
npm = [k for k in json.loads(leer("package.json")).get("scripts", {}) if k.startswith("test:")]
check("CI: cada `npm run test:*` corre en CI", all(f"npm run {k}" in ci for k in npm),
      [k for k in npm if f"npm run {k}" not in ci])

# 2-bis · un backtest sin test no protege de la fuga (FALLAS.md clase 8: «todo
# backtest nuevo lleva un test que plante la fuga y la detecte»). El 15/11/2026
# backtest_unxdos_motor.py, el que dio los coeficientes del 1X2 del motor, no
# tenía ninguno. Cada backend/backtest_*.py lo importa algún test del backend.
_tests_src = "\n".join(leer(os.path.relpath(p, RAIZ)) for p in glob.glob(os.path.join(RAIZ, "backend", "test_*.py")))
_backtests = sorted(os.path.splitext(os.path.basename(p))[0] for p in glob.glob(os.path.join(RAIZ, "backend", "backtest_*.py")))
_bt_sin_test = [b for b in _backtests
                if not re.search(rf"(from backend\.{b} import|from backend import {b}\b|import backend\.{b}\b)", _tests_src)]
check("fuga: cada backend/backtest_*.py lo importa un test (que plante la fuga y la detecte)",
      bool(_backtests) and not _bt_sin_test, _bt_sin_test)

# ── 3 · CONTRATO PRIMERO (CLAUDE.md: «primero docs/openapi.yaml») ───────────
app = leer(os.path.join("backend", "app.py"))
oa = leer(os.path.join("docs", "openapi.yaml"))
rutas = [r for _, r in re.findall(r'@app\.(get|post|put|delete)\(API \+ "([^"]+)"', app)]
documentadas = {re.sub(r"\{[^}]+\}", "{}", p) for p in re.findall(r"^  (/[^:\s]+):", oa, re.M)}
sin_doc = [r for r in rutas if re.sub(r"\{[^}]+\}", "{}", r) not in documentadas]
check("contrato: cada endpoint de backend/app.py está en docs/openapi.yaml", not sin_doc, sin_doc)

parte = leer(os.path.join("backend", "analisis", "parte.py"))
codigos = []
for conj in ("_ALERTAS_CALCULADAS", "_ALERTAS_CAPTURADAS"):
    m = re.search(conj + r" = \{(.*?)\}", parte, re.S)
    codigos += re.findall(r'"([A-Z0-9.\-]+)"', m.group(1)) if m else []
check("contrato: cada alerta calculada o capturada está documentada en docs/openapi.yaml",
      codigos and all(c in oa for c in codigos), [c for c in codigos if c not in oa])

# ── 4 · UN FALLO NO SE TRAGA CALLADO (FALLAS.md: deuda 8) ───────────────────
# Tres semanas sin cuotas prepartido: un except que tragaba el error en cada
# corrida. Un `except Exception` dice POR QUÉ es seguro seguir: un comentario
# en su línea o en la primera de su cuerpo, o el cuerpo lo deja escrito
# (print / log).
mudos = []
for rel in fuentes():
    lineas = leer(rel).split("\n")
    for i, l in enumerate(lineas):
        if re.search(r"^\s*except\s*(\(?\s*(Exception|BaseException)[^:]*)?:\s*(#.*)?$", l):
            cuerpo = lineas[i + 1] if i + 1 < len(lineas) else ""
            if "#" in l or "#" in cuerpo or re.search(r"\b(print|log\w*)\(", cuerpo):
                continue
            if re.search(r"except\s+\w+Error|except\s+\(\w+Error", l):
                continue
            mudos.append(f"{rel}:{i + 1}")
check("excepciones: cada `except Exception` dice por qué es seguro seguir (o lo registra)", not mudos, mudos)

# ── 5 · LO QUE LOS SKILLS PIDEN, EXISTE (FALLAS.md: rutas inventadas) ───────
# El prompt pedía `/estadisticas/gap`, que no existía, y la corrida improvisaba.
rx = [re.compile("^" + re.sub(r"\\\{[^}]+\\\}", r"[^/]+", re.escape(r)) + "(/|$)") for r in rutas]


def existe(p: str) -> bool:
    p = p.rstrip("/")
    return any(x.match(p) for x in rx) or any(r.startswith(p + "/") for r in rutas)


inventadas = []
# El skill de la corrida va partido en un archivo por modo (1377): se revisan TODOS.
_corrida = os.path.join(".claude", "skills", "corrida-sad")
_corrida_md = sorted(os.path.relpath(os.path.join(d, f), RAIZ)
                     for d, _, fs in os.walk(os.path.join(RAIZ, _corrida)) for f in fs if f.endswith(".md"))
# …y el NÚCLEO de cada skill del pipeline (17/11/2026, prevención del mantenimiento):
# desde la v0.1.27/v1.9/v1.11/v4.6 el TDE, el DTP y el EFE también mandan leer rutas
# de la app (`tde/{id}`, `dtp/{id}`, `f1/{id}`, `bancoProbable`) y antes solo se
# miraba sad-analysis. El HISTORIAL no: cita rutas de su época a propósito.
_nucleos = sorted(os.path.relpath(os.path.join(d, f), RAIZ)
                  for d, _, fs in os.walk(os.path.join(RAIZ, "docs", "skills"))
                  for f in fs if f.endswith(".md") and f != "HISTORIAL.md"
                  and os.path.basename(os.path.dirname(os.path.join(d, f))) in (
                      "teorema-del-echado", "diagnostico-tactico", "efe-clasificador", "efe-dashboard",
                      "sad-analysis", "references"))
for rel in (*_corrida_md, os.path.join("docs", "COWORK.md"), *_nucleos):
    t = leer(rel)
    t = re.sub(r"\$(B|SAD_API_BASE)/", " /", t)
    # `antecedentes/` también: el encargo pedía «GET antecedentes/{id}», que no
    # existe (es /analisis/cowork/antecedentes/{id}) y daba 403 (1177)
    t = re.sub(r"(GET|POST)\s+(?=analisis/|equipos/|fixtures/|cuotas/|predicciones/|antecedentes/)", r"\1 /", t)
    t = re.sub(r"\{[^}/\n]*\}", "{x}", t)
    for m in re.finditer(r"(?<![\w.…])(/(?:analisis|equipos|fixtures|cuotas|constantes|constantes-cuota|predicciones|"
                         r"niveles|health|ligas|analisis-prepartido|antecedentes)(?:/[A-Za-z0-9_{}\-]+)*)", t):
        if not existe(m.group(1)):
            inventadas.append(f"{rel}: {m.group(1)}")
check("skills y prompt: cada ruta que citan existe en backend/app.py", not inventadas, sorted(set(inventadas)))

# ── 5-ter · LA CORRIDA ES AHORRADORA (incidencia 1377, usuario 11/11/2026) ──
# Una corrida vacía cargaba el SKILL.md entero (5 modos + «No se reporta»,
# ~60 KB). El índice queda chico, cada modo en su archivo y la lista aparte:
# si alguien vuelve a pegar un modo en el índice, esto lo frena.
_indice = leer(os.path.join(_corrida, "SKILL.md"))
_modos = ("partes", "rehacer", "veredictos", "reventones", "mantenimiento")
_faltan_modos = [m for m in _modos if not os.path.exists(os.path.join(RAIZ, _corrida, "modos", f"{m}.md"))
                 or f"modos/{m}.md" not in _indice and "modos/<modo>.md" not in _indice]
check("corrida-sad: un archivo por modo en modos/ y el índice los nombra", not _faltan_modos, _faltan_modos)
check("corrida-sad: el índice SKILL.md es chico (≤ 9.000 caracteres) y no trae los modos ni «No se reporta»",
      len(_indice) <= 9000 and "## Modo `" not in _indice and "desde la pasada" not in _indice, len(_indice))
# Y CLAUDE.md se carga en CADA paso de CADA agente: el resumen operativo queda
# ahí y la regla entera, con su historia, en docs/REGLAS.md (1377: 49 KB → 18 KB).
_claude = leer("CLAUDE.md")
check("CLAUDE.md es el resumen (≤ 24.000 caracteres) y remite a docs/REGLAS.md, que existe",
      len(_claude) <= 24000 and "docs/REGLAS.md" in _claude and os.path.exists(os.path.join(RAIZ, "docs", "REGLAS.md")),
      len(_claude))
check("corrida-sad: partes y veredictos terminan en una línea con la lista vacía (como rehacer)",
      all(x in _indice for x in ("veredictos/pendientes", "porHacer", "pendientes` vacío")))

# ── 5-bis · LOS DÍAS DE DESCANSO SE CUENTAN EN UN SOLO LUGAR ──────────────
# Incidencias 769 y 870: el calendario restaba días del calendario y el F2 del
# TDE horas, y el mismo descanso salía 3 en una pantalla y 2 en la otra. Un
# `.days` cerca de «descanso» fuera de backend/jugadores.dias_descanso reabre eso.
descanso_suelto = []
for rel in fuentes():
    lineas = leer(rel).split("\n")
    for i, ln in enumerate(lineas):
        if ".days" in ln and "descanso" in " ".join(lineas[max(0, i - 6):i + 4]).lower():
            descanso_suelto.append(f"{rel}:{i + 1}")
check("descanso: los días entre partidos salen de jugadores.dias_descanso (por horas), no de restar fechas",
      not descanso_suelto, descanso_suelto)
# Y el descanso SIN su liga en la base no es dato (1357, Anaitasuna «38 días»):
# todo módulo que cuenta el descanso de un equipo antes de un partido pasa por
# `jugadores.sin_liga_en_la_base` (directo o vía `_congestion`).
sin_regla = [rel for rel in ("backend/analisis/tde.py", "backend/analisis/dtp_cowork.py", "backend/calendario.py")
             if "sin_liga_en_la_base" not in leer(rel) and "_congestion(" not in leer(rel)]
check("descanso: el TDE, el DTP y el calendario aplican la regla de «sin su liga en la base»",
      not sin_regla, sin_regla)

# 3-bis · un `no`, `off`, `yes` u `on` sin comillas en un enum del contrato es un
# booleano en YAML 1.1 (incidencia 1059: `escenario.aparecio` y `d3` traían
# [si, parcial, no] y un validador rechazaba «no»)
_bools = [f"docs/openapi.yaml:{i}" for i, ln in enumerate(oa.split("\n"), 1)
          for m in re.finditer(r"enum: \[([^\]]*)\]", ln)
          if any(x.strip() in ("no", "yes", "on", "off", "No", "Yes", "On", "Off") for x in m.group(1).split(","))]
check("contrato: ningún enum de docs/openapi.yaml trae un no/yes/on/off sin comillas (YAML lo lee booleano)",
      not _bools, _bools)

# 5-ter · cada copa nacional de la base tiene su formato decidido (FALLAS.md: una
# regla del fútbol leída del marcador; 1106: la KNVB Beker entró a LIGAS el
# 29/10 y sus partidos únicos salían con `avanza` null sin que nadie lo notara)
from backend import eliminatoria as _elim  # noqa: E402
from backend.analisis.escala import COPAS as _COPAS  # noqa: E402
from backend.ingesta.extractor import LIGAS as _LIGAS  # noqa: E402
_sin_formato = sorted(f"{i} {_LIGAS[i]}" for i in set(_LIGAS) & _COPAS
                      if i not in _elim.PARTIDO_UNICO and i not in _elim.FORMATO_SIN_AFIRMAR)
check("copas: cada copa nacional de extractor.LIGAS está en eliminatoria.PARTIDO_UNICO o en "
      "FORMATO_SIN_AFIRMAR con su motivo", not _sin_formato, _sin_formato)
_doble = sorted(set(_elim.PARTIDO_UNICO) & set(_elim.FORMATO_SIN_AFIRMAR))
check("copas: ninguna copa está a la vez en PARTIDO_UNICO y en FORMATO_SIN_AFIRMAR", not _doble, _doble)

# 5-quater · una hora de pitazo que viaja a un agente lleva la de Lima al lado
# (FALLAS.md: contrato; 1230: la agenda daba «18:00» en UTC sin decirlo y el
# orquestador fijó la hora tope cuatro horas después del pitazo de Aldosivi–River)
_horas_sin_lima = []
for _rel in ("backend/analisis/parte.py", "backend/analisis/escaneo.py"):
    _ls = leer(_rel).split("\n")
    for _i, _ln in enumerate(_ls):
        if re.search(r'"hora":\s*[^,]*\[11:16\]', _ln) and not any("hora_lima" in x for x in _ls[_i:_i + 8]):
            _horas_sin_lima.append(f"{_rel}:{_i + 1}")
check("contrato: cada «hora» de pitazo cortada de la fecha UTC viaja con hora_lima al lado",
      not _horas_sin_lima, _horas_sin_lima)

# 5-quinquies · una regla pensada para CLUBES mira antes si el equipo es una
# selección (FALLAS.md clase 16; 1395 y 1396: en la Nations League la tabla F1
# mandaba a los convocados «a otro equipo» por su club y el calendario daba
# «recién ascendidas» a casi todas). Quién es selección sale de UNA lista:
# `escala.torneos_selecciones` / `escala.es_seleccion`.
_club_sin_sel = [r for r, fn in (("backend/analisis/f1_base.py", "es_seleccion"),
                                 ("backend/calendario.py", "torneos_selecciones"))
                 if fn not in leer(r)]
check("selecciones: juegan_en_otro y _es_ascendido saltan a las selecciones con la lista única de escala",
      not _club_sin_sel, _club_sin_sel)
# el banco probable usa la regla única de «se fue» (FALLAS.md clase 4; 1443: el
# banco probable no miraba ni convocatorias ni salidas, y nombraba a un jugador
# fallecido del Tenerife y a otro que la tabla F1 daba en otro equipo)
_banco_src = leer("backend/analisis/banco.py")
check("banco probable: saca a los idos con f1_base.juegan_en_otro/salidos y a los no convocados (CONVOCATORIAS)",
      "juegan_en_otro" in _banco_src and "salidos" in _banco_src and "CONVOCATORIAS" in _banco_src)

# 5-sexies · lo que la app SUMA a una fila al leer vuelve en el eco del GET, y
# el POST lo tiene que aceptar (FALLAS.md clase 5; 1404: `con_filas_del_once`
# agregaba `delOnceOficial` y `agregadaPorLaApp` y el re-depósito los rechazaba
# como «campo desconocido»). Cada clave del dict de la fila agregada está en
# `_CLAVES_JUGADOR` o `_ECO_JUGADOR`.
_src_parte = leer("backend/analisis/parte.py")
_m_filas = re.search(r"def con_filas_del_once.*?extra = \[\{(.*?)\} for c in nuevos\]", _src_parte, re.S)
_claves_filas = set(re.findall(r'"(\w+)":', _m_filas.group(1))) if _m_filas else set()
_m_cj = re.search(r"_CLAVES_JUGADOR = \{(.*?)\}", _src_parte, re.S)
_m_ej = re.search(r"_ECO_JUGADOR = \{(.*?)\}", _src_parte, re.S)
_aceptadas = set(re.findall(r'"(\w+)"', (_m_cj.group(1) if _m_cj else "") + (_m_ej.group(1) if _m_ej else "")))
check("eco: cada clave que con_filas_del_once agrega a una fila del plantel la acepta el POST",
      bool(_claves_filas) and _claves_filas <= _aceptadas, sorted(_claves_filas - _aceptadas))

# 5-septies · el grid se lee como posiciones SOLO si es confiable (FALLAS.md
# clase 11; 1413/1415: el grid revuelto de Nacional–Albion daba DEF al arquero y
# «el central en el arco»). Los lectores de roles por la fila del grid pasan por
# `ficha_tactica.grid_confiable`.
_sin_gc = [r for r in ("backend/analisis/f1_base.py", "backend/analisis/dtp_cowork.py")
           if "grid_confiable" not in leer(r)]
check("grid: la F1 y el rol contra el grid leen la fila solo con ficha_tactica.grid_confiable",
      not _sin_gc, _sin_gc)

# 5-octies · las copas nacionales quedan fuera de TODA métrica (FALLAS.md clase
# 13; usuario, 29/10/2026: las copas inflaban el tramo de 60 %+). Las tres
# poblaciones que se miden —el valor contra el mercado, Aprendizaje y la
# simulación— filtran con `escala.copas_nacionales`; y toda función de
# `backend/analisis/` que arme una población de veredictos (lee `veredicto_json
# IS NOT NULL`) también, salvo la huella de una caché, que solo cuenta filas
# (prevención del mantenimiento, 19/11/2026: una métrica nueva nacía sin el filtro).
_METRICAS = {("backend/analisis/parte.py", "historial_valor"), ("backend/analisis/lecciones.py", "_casos"),
             ("backend/analisis/simulacion.py", "_insumos")}


def _funciones(rel: str) -> dict[str, str]:
    src = leer(rel)
    return {n.name: _ast.get_source_segment(src, n) or "" for n in _ast.walk(_ast.parse(src))
            if isinstance(n, (_ast.FunctionDef, _ast.AsyncFunctionDef))}


# LO QUE LEE VEREDICTOS SIN MEDIRLOS, con su motivo (una entrada nueva acá se
# justifica igual que una métrica: por escrito)
_NO_METRICA = {
    ("backend/analisis/modo_fallo.py", "reetiquetar"):
        "etiqueta el modo de fallo que Jev no selló (402, 24/11/2026); no mide nada y las lecciones de copa "
        "también van al dossier con su etiqueta",
}
_sin_copas = [f"{r}:{fn}" for r, fn in sorted(_METRICAS) if "copas_nacionales" not in _funciones(r).get(fn, "")]
for _r in sorted(glob.glob(os.path.join(RAIZ, "backend", "analisis", "*.py"))):
    _rel = os.path.relpath(_r, RAIZ)
    for _fn, _cuerpo in _funciones(_rel).items():
        if ("veredicto_json IS NOT NULL" in _cuerpo and "huella" not in _fn
                and "copas_nacionales" not in _cuerpo and (_rel, _fn) not in _NO_METRICA):
            _sin_copas.append(f"{_rel}:{_fn}")
check("métricas: cada población de veredictos saca las copas nacionales con escala.copas_nacionales",
      not _sin_copas, _sin_copas)

# ── 5-ter · LA HISTORIA DE UN EQUIPO SIN EL HOMÓNIMO ──────────────────────
# Incidencias 1371 y 1473: el id 1137 de Atlético Nacional trae partidos de la
# Copa Perú de otro club; el calendario, el TDE y el DTP los sacaban con
# partido_ajeno.sql_fuera, pero el banco probable lo tomaba como «último
# partido». Cada lector de los partidos recientes de un equipo usa la regla.
_LECTORES_HISTORIA = (("backend/analisis/banco.py", "_previos"), ("backend/analisis/banco.py", "ultima_sin_hoja"),
                      ("backend/analisis/f1_base.py", "onces_recientes"),
                      ("backend/analisis/f1_base.py", "_partidos_temporada"),
                      ("backend/analisis/arquero.py", "perfil"))
_sin_ajeno = [f"{r}:{fn}" for r, fn in _LECTORES_HISTORIA if "sql_fuera" not in _funciones(r).get(fn, "")]
_sin_ajeno += [r for r in ("backend/analisis/tde.py", "backend/analisis/dtp_cowork.py", "backend/calendario.py",
                           "backend/cronologia.py") if "sql_fuera" not in leer(r)]
check("homónimo: el banco, la F1, el arquero, el TDE, el DTP, el calendario y la cronología usan partido_ajeno.sql_fuera",
      not _sin_ajeno, _sin_ajeno)

# 5-nonies · el lado del parte no se cruza con la ficha si la API dio vuelta el
# fixture (FALLAS.md clase 11; 1522, Racing–Liverpool de Montevideo: xi/auto le
# pegó al lado a el once del local de hoy). `cerrar_onces_pendientes` pregunta
# `lados_invertidos` ANTES de pedir el once de la ficha por `home_team_id`.
_cop = _funciones("backend/analisis/parte.py").get("cerrar_onces_pendientes", "")
check("lado invertido: xi/auto mira parte.lados_invertidos antes de cruzar el once de la ficha",
      "lados_invertidos" in _cop and _cop.index("lados_invertidos") < _cop.index("xi_de_ficha"),
      "lados_invertidos" in _cop)

# ── 5-quater · «EN JUEGO» TIENE FECHA ─────────────────────────────────────
# 22/11/2026: dos partidos de agosto y septiembre en SUSP eran candidatos
# perpetuos del ciclo en vivo (cada minuto, feed + /fixtures?ids=) y el 21/11
# el plan se agotó a las 13:50 de Lima. Cada consulta del ciclo que pregunta
# por los estados EN_JUEGO lleva el piso de fecha (en_vivo.piso_en_juego).
_vivo = leer(os.path.join("backend", "ingesta", "en_vivo.py"))
_con_en_juego = len(re.findall(r"\*EN_JUEGO\b", _vivo))
_con_piso = len(re.findall(r"\*EN_JUEGO, piso_en_juego\(\)", _vivo))
check("costo: cada consulta del ciclo en vivo por estados EN_JUEGO lleva el piso de fecha (piso_en_juego)",
      _con_en_juego >= 4 and _con_en_juego == _con_piso, (_con_en_juego, _con_piso))

# ── 6 · CADA CLASE DE FALLA TIENE SU GUARDIA ESCRITA ────────────────────────
fallas = leer(os.path.join("docs", "FALLAS.md"))
clases = re.findall(r"^### ", fallas, re.M)
sin_guardia = [b.split("\n")[0] for b in re.split(r"^### ", fallas, flags=re.M)[1:] if "**Guardia" not in b]
check("docs/FALLAS.md: cada clase de falla dice cuál es su guardia", len(clases) >= 10 and not sin_guardia,
      (len(clases), sin_guardia))

print("\nTODO OK" if not fallos else f"\n{fallos} FALLA(S)")
sys.exit(1 if fallos else 0)
