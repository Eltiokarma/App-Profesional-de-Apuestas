"""LA CALIBRACIÓN DE LAS DOS LECTURAS CONTRA LOS RESULTADOS (24/11/2026).

El usuario: «para calibrar esos porcentajes se tiene que salir de lo que dice
el analista y calibrar con los resultados; incluso podemos tomar más
resultados pasados como calibración».

Cada lectura es una pregunta de sí o no sobre UN equipo («¿gana el local?»,
«¿gana el visitante?»), así que se calibra como cualquier probabilidad
binaria: se mira, en los partidos ya jugados, cuánto ganó de verdad el equipo
cuando el analista dijo X, y se aprende la curva que lleva lo dicho a lo que
pasa. La curva es una recalibración logística (Platt) por lado:

    logit(calibrada) = a + b · logit(dicha)

- `b < 1` dice que el analista exagera (sus 70 valen menos); `b > 1` que se
  queda corto (comprime hacia el medio: sus 55 valen más); `a` corre todo
  hacia arriba o hacia abajo.
- Con pocos partidos la curva casi no se mueve: `a` y `b` arrancan en la
  identidad (0 y 1) y se apartan solo lo que los resultados empujan
  (`PRIOR_SD`, un previo gaussiano). Con muchos, mandan los resultados.
- Después de calibrar las dos lecturas, el 1X2 sale igual que siempre:
  `ciego.calzar` (empate = 100 − las dos; si se cruzan, el del motor).

No mira la cuota: aprende solo de lo dicho y lo que pasó. El previo y si la
curva entra al número publicado se deciden con
`python -m backend.backtest_calibracion_lecturas` a la vista (CLAUDE.md:
números calibrados solo con el backtest). 0 tokens, 0 cuota.
"""
from __future__ import annotations

import math

LADOS = ("local", "visita")
# el previo de la curva, centrado en la identidad: cuánto puede moverse a y b
# sin datos que lo pidan. Medido con el backtest (docs/METODO_APUESTA.md,
# «La calibración de las dos lecturas»).
PRIOR_SD = 0.5
# lo dicho se recorta a [1 %, 99 %] para que el logit no explote
_EPS = 0.01


def _logit(p: float) -> float:
    p = min(1 - _EPS, max(_EPS, p))
    return math.log(p / (1 - p))


def _sig(z: float) -> float:
    if z >= 0:
        return 1 / (1 + math.exp(-z))
    e = math.exp(z)
    return e / (1 + e)


def ajustar(puntos: list[tuple[float, bool]], prior_sd: float = PRIOR_SD) -> dict:
    """[(lo dicho en %, si pasó)] → {a, b, n}. Máxima verosimilitud penalizada
    (previo gaussiano en a ~ N(0, sd) y b ~ N(1, sd)), por Newton. Sin puntos,
    la identidad."""
    xs = [(_logit(float(p) / 100), 1.0 if y else 0.0) for p, y in puntos if p is not None]
    a, b = 0.0, 1.0
    if not xs:
        return {"a": a, "b": b, "n": 0}
    lam = 1.0 / (prior_sd * prior_sd)
    for _ in range(50):
        ga, gb = lam * a, lam * (b - 1)
        haa, hab, hbb = lam, 0.0, lam
        for x, y in xs:
            q = _sig(a + b * x)
            r = q - y
            w = q * (1 - q)
            ga += r
            gb += r * x
            haa += w
            hab += w * x
            hbb += w * x * x
        det = haa * hbb - hab * hab
        if det <= 1e-12:
            break
        da = (hbb * ga - hab * gb) / det
        db = (haa * gb - hab * ga) / det
        a, b = a - da, b - db
        if abs(da) < 1e-9 and abs(db) < 1e-9:
            break
    return {"a": round(a, 5), "b": round(b, 5), "n": len(xs)}


def aplicar(coef: dict | None, p_pct: float) -> float:
    """Lo dicho (en %) → lo calibrado (en %), con una decimal."""
    if not coef:
        return round(float(p_pct), 1)
    return round(100 * _sig(coef["a"] + coef["b"] * _logit(float(p_pct) / 100)), 1)


def puntos_de(filas: list[dict]) -> dict:
    """Las filas: {ganaLocal, ganaVisita, resultado} → {local: [(dicho, ganó)],
    visita: [...]}. Solo las cerradas."""
    out = {"local": [], "visita": []}
    for f in filas:
        r = f.get("resultado")
        if r not in ("local", "empate", "visita"):
            continue
        if f.get("ganaLocal") is not None:
            out["local"].append((float(f["ganaLocal"]), r == "local"))
        if f.get("ganaVisita") is not None:
            out["visita"].append((float(f["ganaVisita"]), r == "visita"))
    return out


def ajuste_de(filas: list[dict], prior_sd: float = PRIOR_SD) -> dict:
    """Las dos curvas, una por lado, aprendidas de las filas cerradas."""
    pts = puntos_de(filas)
    return {lado: ajustar(pts[lado], prior_sd) for lado in LADOS}


def calibrar(gana_local: float, gana_visita: float, coefs: dict, empate_motor=None) -> dict:
    """Las dos lecturas del analista → las dos calibradas y su 1X2 (`calzar`)."""
    from backend.analisis import ciego
    gl = aplicar(coefs.get("local"), gana_local)
    gv = aplicar(coefs.get("visita"), gana_visita)
    return {"ganaLocal": gl, "ganaVisita": gv, **ciego.calzar(gl, gv, empate_motor)}


def lectura(coef: dict) -> str:
    """La curva en castellano: qué hace con lo que dice el analista."""
    if not coef or not coef.get("n"):
        return "sin partidos: la curva es la identidad (lo dicho vale lo que dice)"
    ejemplos = ", ".join(f"{p} → {aplicar(coef, p):g}" for p in (30, 50, 70))
    if coef["b"] > 1.05:
        tipo = "te quedás corto: lo calibrado se aparta más del medio que lo que decís"
    elif coef["b"] < 0.95:
        tipo = "exagerás: lo calibrado queda más cerca del medio que lo que decís"
    else:
        tipo = "la pendiente está cerca de la justa"
    return f"{tipo} ({coef['n']} partidos; {ejemplos})"


def log_loss(puntos: list[tuple[float, bool]], coef: dict | None = None) -> float | None:
    """Pérdida logarítmica binaria (más baja es mejor) de lo dicho o de lo calibrado."""
    if not puntos:
        return None
    s = 0.0
    for p, y in puntos:
        q = min(1 - 1e-6, max(1e-6, aplicar(coef, p) / 100))
        s -= math.log(q) if y else math.log(1 - q)
    return s / len(puntos)


def brier(puntos: list[tuple[float, bool]], coef: dict | None = None) -> float | None:
    if not puntos:
        return None
    return sum((aplicar(coef, p) / 100 - (1.0 if y else 0.0)) ** 2 for p, y in puntos) / len(puntos)
