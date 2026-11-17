"""El núcleo de los skills — la guardia de NUCLEO_SKILLS_propuesta.md (sin red).

Desde el 17/11/2026 cada skill del pipeline separa el NÚCLEO (lo que se aplica
al analizar un partido: SKILL.md y sus referencias) del HISTORIAL
(references/HISTORIAL.md: changelog, casos, mediciones). Antes la historia
vivía en el SKILL.md y se cargaba en cada subagente (el TDE pesaba ~54 K
tokens, 25 K de ellos notas de versión), y una regla nueva se escribía en el
changelog y no en el cuerpo (las disciplinas 34-39). Este test lo impide:

1. cada frase ancla de scripts/nucleo_reglas.json está en el núcleo, no solo
   en el historial;
2. ningún archivo del núcleo tiene bloques de versión (`> **v…`);
3. cada skill tiene su references/HISTORIAL.md y su SKILL.md lo nombra;
4. el núcleo no pasa su tope de tokens (caracteres/4): crecer con historia se nota.

    python -m backend.test_nucleo_skills
"""
import glob
import json
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


def nucleo(skill: str) -> dict[str, str]:
    base = os.path.join(RAIZ, "docs", "skills", skill)
    rutas = [os.path.join(base, "SKILL.md")] + sorted(glob.glob(os.path.join(base, "references", "*.md")))
    return {os.path.relpath(p, RAIZ): open(p, encoding="utf-8").read()
            for p in rutas if os.path.basename(p) != "HISTORIAL.md"}


def main():
    reglas = json.load(open(os.path.join(RAIZ, "scripts", "nucleo_reglas.json"), encoding="utf-8"))
    version = re.compile(r"^> \*\*(v\d|Changelog)", re.M)
    for skill, anclas in reglas["anclas"].items():
        archivos = nucleo(skill)
        texto = "\n".join(archivos.values())
        faltan = [a for a in anclas if a not in texto]
        check(f"{skill}: las reglas ancla están en el núcleo, no solo en el historial", not faltan, faltan)
        con_version = [p for p, t in archivos.items() if version.search(t)]
        check(f"{skill}: el núcleo no trae bloques de versión (van a references/HISTORIAL.md)",
              not con_version, con_version)
        hist = os.path.join(RAIZ, "docs", "skills", skill, "references", "HISTORIAL.md")
        skill_md = archivos.get(os.path.join("docs", "skills", skill, "SKILL.md"), "")
        check(f"{skill}: tiene references/HISTORIAL.md y el SKILL.md lo nombra",
              os.path.exists(hist) and "HISTORIAL.md" in skill_md)
        tokens = len(texto) // 4
        tope = reglas["topeTokens"][skill]
        check(f"{skill}: el núcleo pesa {tokens} tokens, debajo del tope de {tope}", tokens <= tope, tokens)
    print("\nTODO OK" if not fallos else f"\n{fallos} FALLAS")
    sys.exit(1 if fallos else 0)


if __name__ == "__main__":
    main()
