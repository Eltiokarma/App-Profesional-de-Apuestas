"""EL ESCANEO PREVENTIVO DEL CÓDIGO (30/10/2026, pedido del usuario: «un
escaneo preventivo sobre nuestro código, para en el futuro no fallar»).

El escaneo de `backend/analisis/escaneo.py` mira los DATOS. Este mira el
CÓDIGO: cada regla nace de una clase de falla que ya pasó (docs/FALLAS.md) y
falla en CI si alguien la vuelve a abrir, antes de que llegue a un parte. Una
clase de falla nueva que se pueda verificar leyendo el repo se suma acá.

    python -m backend.test_arquitectura
"""
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
for rel in (os.path.join(".claude", "skills", "corrida-sad", "SKILL.md"), os.path.join("docs", "COWORK.md"),
            os.path.join("docs", "skills", "sad-analysis", "SKILL.md")):
    t = leer(rel)
    t = re.sub(r"\$(B|SAD_API_BASE)/", " /", t)
    t = re.sub(r"(GET|POST)\s+(?=analisis/|equipos/|fixtures/|cuotas/|predicciones/)", r"\1 /", t)
    t = re.sub(r"\{[^}/\n]*\}", "{x}", t)
    for m in re.finditer(r"(?<![\w.…])(/(?:analisis|equipos|fixtures|cuotas|constantes|constantes-cuota|predicciones|"
                         r"niveles|health|ligas|analisis-prepartido)(?:/[A-Za-z0-9_{}\-]+)*)", t):
        if not existe(m.group(1)):
            inventadas.append(f"{rel}: {m.group(1)}")
check("skills y prompt: cada ruta que citan existe en backend/app.py", not inventadas, sorted(set(inventadas)))

# ── 6 · CADA CLASE DE FALLA TIENE SU GUARDIA ESCRITA ────────────────────────
fallas = leer(os.path.join("docs", "FALLAS.md"))
clases = re.findall(r"^### ", fallas, re.M)
sin_guardia = [b.split("\n")[0] for b in re.split(r"^### ", fallas, flags=re.M)[1:] if "**Guardia" not in b]
check("docs/FALLAS.md: cada clase de falla dice cuál es su guardia", len(clases) >= 10 and not sin_guardia,
      (len(clases), sin_guardia))

print("\nTODO OK" if not fallos else f"\n{fallos} FALLA(S)")
sys.exit(1 if fallos else 0)
