"""A6 de la EFE v1.10: ¿la brecha del EFE ordena el partido, con y sin EFE-EMPATE-TECNICO?

Aprobada el 10/11/2026 y pedida otra vez en la EFE v1.11 («Para la app» 2): la
alerta EFE-EMPATE-TECNICO (brecha ≥ 5 puntos con T.54 / R-KT.2 en un lado o
ESCALA-LIGAS) dice que esa brecha NO ordena el partido. Las lecciones la dan por
«declarada y cumplida» 27 de 27 veces, sin contenido: así escrita no se puede
refutar. Esto la mide:

- con brecha ≥ 5 y SIN la alerta: ¿cuánto gana el de mayor porcentaje del EFE?
- con la alerta: ¿cuánto gana el de mayor porcentaje? (si la alerta tiene razón,
  bastante menos);
- en los MISMOS partidos, ¿cuánto gana el favorito de la casa? (la referencia).

Solo partes que acreditan (ciega + PRE, sin cuarentena ni copa nacional). Lee lo
que el GET del parte ya trae (porcentajes, alertas, resultado, mercado): no
recalcula nada ni toca el EFE. Después de medir, la decisión de la corrida
(dejar de escribir una lección por cada empate técnico cumplido) es del usuario.

    python -m backend.medir_brecha_efe --api [--cache carpeta] [--json]
"""
import argparse
import json
import os
import sys
import time
import urllib.request

BRECHA_MIN = 5.0
CLAVES = ("local", "empate", "visita")


def _wilson(k: int, n: int) -> list[float] | None:
    from backend.analisis.lecciones import intervalo_wilson
    return intervalo_wilson(k, n) if n else None


def caso_de_parte(p: dict) -> dict | None:
    """Del GET de un parte cerrado: porcentajes, si sonó la alerta, el resultado y el mercado.
    None si falta algo (sin veredicto jugado, sin porcentajes o sin cuota)."""
    eq = p.get("equipos") or {}
    pa, pb = (eq.get("a") or {}).get("porcentaje"), (eq.get("b") or {}).get("porcentaje")
    obj = ((p.get("veredicto") or {}).get("objetivo") or {})
    real = (obj.get("unXDos") or {}).get("real")
    sel = ((p.get("vsMercado") or {}).get("seleccion") or {})
    mercado = {k: (sel.get(k) or {}).get("mercado") for k in CLAVES}
    if not isinstance(pa, (int, float)) or not isinstance(pb, (int, float)) or real not in CLAVES:
        return None
    if any(v is None for v in mercado.values()):
        return None
    return {"fixtureId": p.get("fixtureId"), "a": float(pa), "b": float(pb), "real": real, "mercado": mercado,
            "empateTecnico": any(a.get("codigo") == "EFE-EMPATE-TECNICO" for a in p.get("alertas") or [])}


def _tasa(k: int, n: int) -> dict:
    return {"n": n, "aciertos": k, "tasa": round(k / n, 3) if n else None, "intervalo": _wilson(k, n)}


def medir(casos: list[dict]) -> dict:
    """La tabla de A6 sobre casos ya extraídos (`caso_de_parte`)."""
    grupos = {"conEmpateTecnico": [], "sinAlerta": [], "brechaChica": []}
    for c in casos:
        brecha = abs(c["a"] - c["b"])
        if c["empateTecnico"]:
            grupos["conEmpateTecnico"].append(c)
        elif brecha >= BRECHA_MIN:
            grupos["sinAlerta"].append(c)
        else:
            grupos["brechaChica"].append(c)
    out = {}
    for nombre, cs in grupos.items():
        gana_efe = gana_casa = coinciden = 0
        for c in cs:
            mayor = "local" if c["a"] > c["b"] else "visita"
            fav = max(("local", "visita"), key=lambda k: c["mercado"][k])
            gana_efe += c["real"] == mayor
            gana_casa += c["real"] == fav
            coinciden += mayor == fav
        out[nombre] = {"partidos": len(cs), "ganaElMayorEfe": _tasa(gana_efe, len(cs)),
                       "ganaElFavoritoDeLaCasa": _tasa(gana_casa, len(cs)),
                       "mayorEfeEsElFavorito": coinciden}
    out["nota"] = (f"brecha = |EFE a − EFE b|; «sinAlerta» = brecha ≥ {BRECHA_MIN:g} sin EFE-EMPATE-TECNICO; "
                   "«brechaChica» = menos de 5 puntos y sin alerta. Gana = el resultado real del 1X2 (el empate "
                   "no lo gana nadie). Intervalo de Wilson al 95 %. Si la alerta tiene razón, el mayor EFE gana "
                   "bastante menos «conEmpateTecnico» que «sinAlerta»; la casa es la referencia en los mismos partidos")
    return out


def _get(base: str, token: str, ruta: str):
    for intento in range(4):
        try:
            req = urllib.request.Request(base + ruta, headers={"Authorization": "Bearer " + token})
            return json.load(urllib.request.urlopen(req, timeout=120))
        except Exception:  # noqa: BLE001 — red: se reintenta con espera y al cuarto se rinde
            if intento == 3:
                raise
            time.sleep(2 ** intento)


def ids_acreditables(base: str, token: str) -> list[int]:
    """Los fixtures de las lecciones que acreditan (ciega + PRE, sin cuarentena ni copa), cohorte vigente."""
    ids, desde = set(), 0
    while True:
        d = _get(base, token, f"/analisis/cowork/lecciones?cohorte=vigente&limite=2000&cuantas=500&desde={desde}")
        items = d.get("items") or []
        for i in items:
            if i.get("acredita") and not i.get("copa") and not i.get("cuarentena"):
                ids.add(int(i["fixtureId"]))
        desde += len(items)
        if not items or desde >= int(d.get("total") or 0):
            return sorted(ids)


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--api", action="store_true", help="bajar por la API (SAD_API_BASE y SAD_TOKEN_COWORK)")
    ap.add_argument("--cache", help="carpeta donde guardar/leer los partes bajados")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    if not a.api and not a.cache:
        ap.error("hace falta --api o --cache con partes ya bajados")
    partes = []
    if a.api:
        base = os.environ["SAD_API_BASE"].rstrip("/")
        token = os.environ.get("SAD_TOKEN_COWORK") or os.environ["SAD_API_TOKEN"]
        for fid in ids_acreditables(base, token):
            ruta = os.path.join(a.cache, f"{fid}.json") if a.cache else None
            if ruta and os.path.exists(ruta):
                partes.append(json.load(open(ruta, encoding="utf-8")))
                continue
            p = _get(base, token, f"/analisis/cowork/{fid}")
            if ruta:
                os.makedirs(a.cache, exist_ok=True)
                json.dump(p, open(ruta, "w", encoding="utf-8"), ensure_ascii=False)
            partes.append(p)
    else:
        for n in sorted(os.listdir(a.cache)):
            if n.endswith(".json"):
                partes.append(json.load(open(os.path.join(a.cache, n), encoding="utf-8")))
    casos = [c for c in (caso_de_parte(p) for p in partes) if c]
    r = medir(casos)
    r["partesLeidos"], r["casosMedidos"] = len(partes), len(casos)
    if a.json:
        print(json.dumps(r, ensure_ascii=False, indent=1))
        return
    print(f"A6 · {len(casos)} partidos medidos de {len(partes)} partes que acreditan\n")
    for g in ("conEmpateTecnico", "sinAlerta", "brechaChica"):
        x = r[g]
        e, f = x["ganaElMayorEfe"], x["ganaElFavoritoDeLaCasa"]
        fmt = lambda t: "—" if t["tasa"] is None else f"{t['tasa']:.0%} ({t['aciertos']}/{t['n']}, IC {t['intervalo'][0]:.0%}-{t['intervalo'][1]:.0%})"  # noqa: E731
        print(f"{g:18s} n={x['partidos']:4d} · gana el mayor EFE {fmt(e)} · gana el favorito de la casa {fmt(f)} "
              f"· coinciden {x['mayorEfeEsElFavorito']}")
    print("\n" + r["nota"])


if __name__ == "__main__":
    sys.exit(main())
