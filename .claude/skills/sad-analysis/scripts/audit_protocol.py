#!/usr/bin/env python3
"""
SAD Protocol Audit Script v3.2
Verifica que un análisis pre-partido ejecutó TODOS los pasos del protocolo
con el formato y profundidad requeridos.

Cambios v3.2 (compatibilidad hacia atrás preservada):
  - "Anticulebra"     → "Tensión del Favorito"      (Paso 3)
  - "DC trampa"       → "Doble oportunidad trampa"  (Paso 2)
  - "§Anti-Sesgo-1"   → "Auditoría 1"
  - "§Anti-Sesgo-2"   → "Auditoría 2"
  - "ECG"             → "trayectoria histórica"
El script detecta tanto los términos v3.1 como los v3.2.

Uso desde Claude:
  1. Guardar el texto del análisis en un archivo temporal
  2. Ejecutar: python scripts/audit_protocol.py /path/to/analisis.txt
  3. Leer el reporte y completar pasos faltantes

El script NO modifica veredictos — solo detecta pasos faltantes,
constantes no analizadas, y violaciones de protocolo.
"""

import sys
import re
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class AuditResult:
    paso: str
    nombre: str
    ejecutado: bool
    completo: bool
    problemas: list = field(default_factory=list)
    severidad: str = "INFO"  # INFO, WARNING, CRITICAL


@dataclass
class ProtocolAudit:
    results: list = field(default_factory=list)
    violations: list = field(default_factory=list)
    missing_constants: list = field(default_factory=list)

    def add(self, paso, nombre, ejecutado, completo=True, problemas=None, severidad="INFO"):
        self.results.append(AuditResult(
            paso=paso, nombre=nombre, ejecutado=ejecutado,
            completo=completo, problemas=problemas or [], severidad=severidad
        ))

    def add_violation(self, rule, description, severidad="CRITICAL"):
        self.violations.append({"rule": rule, "description": description, "severidad": severidad})


def audit_analysis(text: str) -> ProtocolAudit:
    audit = ProtocolAudit()
    text_lower = text.lower()

    # =========================================================================
    # PASO 0.5 — LEY 4 (Filtro XI)
    # =========================================================================
    ley4_markers = [
        "ley 4:", "ley 4 :", "escenario 1", "escenario 2", "escenario 3",
        "filtro xi", "formación", "paso 0.5", "bajas"
    ]
    ley4_found = any(m in text_lower for m in ley4_markers)
    ley4_format = bool(re.search(r'LEY\s*4.*?Escenario\s*\[?[123]', text, re.IGNORECASE))

    problemas_ley4 = []
    if ley4_found and not ley4_format:
        problemas_ley4.append("Ley 4 mencionada pero sin formato de veredicto obligatorio (LEY 4: [Equipo] → Escenario [1/2/3])")

    # Check both teams
    equipos_ley4 = len(re.findall(r'LEY\s*4.*?→', text, re.IGNORECASE))
    if ley4_found and equipos_ley4 < 2:
        problemas_ley4.append(f"Ley 4 aplicada a {equipos_ley4} equipo(s), se requieren 2")

    audit.add("0.5", "Ley 4 — Filtro XI", ley4_found,
              completo=ley4_format and equipos_ley4 >= 2,
              problemas=problemas_ley4,
              severidad="CRITICAL" if not ley4_found else "WARNING" if problemas_ley4 else "INFO")

    # =========================================================================
    # PASO 1 — CONSTANTES K
    # =========================================================================
    k_markers = ["veredicto k", "paso 1", "constantes k", "k_general", "k_local",
                 "k_visita", "k_goles", "gatillo",
                 "electrocardiograma", "ecg",
                 "trayectoria histórica", "trayectoria historica"]
    k_found = any(m in text_lower for m in k_markers)

    # Check 6 constants mentioned
    constant_names = [
        ("k_general", ["k_general", "k general", "k fusionada general"]),
        ("k_local/visita", ["k_local", "k_visita", "k local", "k visita"]),
        ("k_goles_anotado", ["k_goles_anotado", "k_goles_general_anotado", "kg_a", "kg_ga"]),
        ("k_goles_recibido", ["k_goles_recibido", "k_goles_general_recibido", "kg_r", "kg_gr"]),
        ("k_goles_contexto_anotado", ["k_goles_local_anotado", "k_goles_visita_anotado",
                                       "kg_la", "kg_va", "k_goles_contexto_anotado"]),
        ("k_goles_contexto_recibido", ["k_goles_local_recibido", "k_goles_visita_recibido",
                                        "kg_lr", "kg_vr", "k_goles_contexto_recibido"]),
    ]

    missing_k = []
    for const_name, aliases in constant_names:
        if not any(alias in text_lower for alias in aliases):
            missing_k.append(const_name)

    problemas_k = []
    if missing_k:
        problemas_k.append(f"Constantes no mencionadas: {', '.join(missing_k)}")
        audit.missing_constants = missing_k

    # Check veredicto K format
    veredicto_k = bool(re.search(r'VEREDICTO\s*K\s*:', text, re.IGNORECASE))
    if k_found and not veredicto_k:
        problemas_k.append("Análisis K presente pero falta VEREDICTO K con formato obligatorio")

    # Check marcador K
    marcador_k = bool(re.search(r'[Mm]arcador\s*K\s*:', text))
    if veredicto_k and not marcador_k:
        problemas_k.append("Veredicto K sin Marcador K (debe derivarse del cruce de distribuciones GF/GC)")

    # Check confianza K
    confianza_k = bool(re.search(r'[Cc]onfianza\s*K\s*:\s*(ALTA|MEDIA|BAJA)', text))
    if veredicto_k and not confianza_k:
        problemas_k.append("Veredicto K sin nivel de Confianza K (ALTA/MEDIA/BAJA)")

    # Check gatillos listed
    gatillos = bool(re.search(r'[Gg]atillos?\s*(activos?|:)', text))
    if k_found and not gatillos:
        problemas_k.append("Análisis K sin listado de gatillos activos")

    # Check trayectoria histórica (antes "ECG")
    ecg_found = any(m in text_lower for m in [
        "trayectoria histórica", "trayectoria historica",
        "electrocardiograma", "ecg",
        "ciclo", "patrón",
    ])
    if k_found and not ecg_found:
        problemas_k.append("Sin mención de trayectoria histórica / patrón de ciclo K")

    # Check shift(1) / anti-tautología
    has_correlation = bool(re.search(r'value_counts|distribución|filtrar.*partidos', text_lower))
    has_shift = "shift" in text_lower or "k_prev" in text_lower or "pre-match" in text_lower or "pre_match" in text_lower
    if has_correlation and not has_shift:
        problemas_k.append("⚠️ POSIBLE TAUTOLOGÍA: correlación K-resultado detectada sin mención de shift(1) o k_prev")
        audit.add_violation("Anti-tautología", "Correlación K-resultado posiblemente circular")

    audit.add("1", "Constantes K", k_found,
              completo=veredicto_k and not missing_k,
              problemas=problemas_k,
              severidad="CRITICAL" if not k_found else "WARNING" if problemas_k else "INFO")

    # =========================================================================
    # PASO 1.5 — LEY 3-B (Proyección Trayectoria K)
    # =========================================================================
    ley3b_markers = ["ley 3-b", "ley 3b", "paso 1.5", "veredicto 3-b", "veredicto 3b",
                     "alimentación", "inflación", "cobro", "trayectoria k", "cadena"]
    ley3b_found = any(m in text_lower for m in ley3b_markers)
    ley3b_format = bool(re.search(r'VEREDICTO\s*3-?B', text, re.IGNORECASE))

    problemas_3b = []
    if ley3b_found and not ley3b_format:
        problemas_3b.append("Ley 3-B mencionada pero sin formato de veredicto")
    if not ley3b_found:
        problemas_3b.append("Ley 3-B no ejecutada (proyección de trayectoria K)")

    audit.add("1.5", "Ley 3-B — Proyección Trayectoria K", ley3b_found,
              completo=ley3b_format,
              problemas=problemas_3b,
              severidad="WARNING" if not ley3b_found else "INFO")

    # =========================================================================
    # AUDITORÍA 1 (antes "§ANTI-SESGO-1")
    # =========================================================================
    as1_markers = [
        # Nuevos (v3.2)
        "auditoría 1", "auditoria 1", "auditoría-1", "auditoria-1",
        # Antiguos (v3.1, mantenidos para compatibilidad)
        "anti-sesgo-1", "anti-sesgo 1", "as-1", "§as-1",
        "anti sesgo 1", "antisesgo 1",
        # Comunes
        "hipótesis de no-victoria", "hipótesis de derrota",
        "hipotesis de no-victoria", "hipotesis de derrota",
    ]
    as1_found = any(m in text_lower for m in as1_markers)
    as1_format = bool(re.search(
        r'(HIPÓTESIS\s+DE\s+NO[- ]VICTORIA|HIPÓTESIS\s+DE\s+DERROTA|HIPOTESIS\s+DE\s+NO[- ]VICTORIA|HIPOTESIS\s+DE\s+DERROTA)',
        text, re.IGNORECASE
    ))

    problemas_as1 = []
    if not as1_found:
        problemas_as1.append("Auditoría 1 NO ejecutada (obligatoria entre Paso 1 y Paso 2)")
    if as1_found and not as1_format:
        problemas_as1.append("Auditoría 1 presente pero sin formato obligatorio de hipótesis")

    # Check Ley 9 violation in Auditoría 1
    if as1_found:
        as1_violations = [
            "rival.*débil", "rival.*no.*suficiente", "contra este.*no revienta",
            "nivel.*rival.*no.*provocar?", "demasiado débil",
            "rival.*no provoca estallido", "rival.*no provoca burst",
        ]
        for pattern in as1_violations:
            if re.search(pattern, text_lower):
                problemas_as1.append(f"⚠️ POSIBLE violación Ley 9 en Auditoría 1: patrón '{pattern}' detectado")
                audit.add_violation("Ley 9 en Auditoría 1",
                                    f"Patrón '{pattern}' encontrado — puede estar usando rival para atenuar gatillo propio")

    # Check severidad
    severidad_as1 = bool(re.search(r'[Ss]everidad\s*:\s*(ALTA|MEDIA|BAJA)', text))
    if as1_found and not severidad_as1:
        problemas_as1.append("Auditoría 1 sin clasificación de Severidad (ALTA/MEDIA/BAJA)")

    audit.add("Auditoría 1", "Auditoría 1 (hipótesis de no-victoria)", as1_found,
              completo=as1_format and severidad_as1,
              problemas=problemas_as1,
              severidad="CRITICAL" if not as1_found else "WARNING" if problemas_as1 else "INFO")

    # =========================================================================
    # PASO 2 — DOBLE OPORTUNIDAD TRAMPA (antes "DC Trampa")
    # =========================================================================
    dc_markers = [
        # Nuevos (v3.2)
        "doble oportunidad trampa", "doble oportunidad",
        # Antiguos (v3.1, mantenidos para compatibilidad)
        "dc trampa", "dc 1x", "dc 2x", "doble chance", "double chance",
        "dc>1.05", "dc >1.05", "dc > 1.05",
        # Comunes
        "paso 2", "cuotas invariables",
    ]
    dc_found = any(m in text_lower for m in dc_markers)

    problemas_dc = []
    if not dc_found:
        problemas_dc.append("Paso 2 (Doble oportunidad trampa) no ejecutado")

    audit.add("2", "Doble oportunidad trampa", dc_found,
              problemas=problemas_dc,
              severidad="WARNING" if not dc_found else "INFO")

    # =========================================================================
    # PASO 3 — TENSIÓN DEL FAVORITO (antes "Anticulebra")
    # =========================================================================
    # Compatibilidad: se detectan tanto los nombres v3.1 (anticulebra/culebra)
    # como los nombres v3.2 (tensión del favorito / favorito tensionado).
    anti_markers = [
        # Nuevos (v3.2)
        "tensión del favorito", "tension del favorito",
        "favorito tensionado", "tensión favorito", "tension favorito",
        # Antiguos (v3.1, mantenidos para compatibilidad)
        "anticulebra", "culebra", "snake",
        # Comunes a ambas versiones
        "icf", "ruptura", "paso 3", "probabilidad ruptura",
        "índice de favoritismo", "indice de favoritismo",
    ]
    anti_found = any(m in text_lower for m in anti_markers)

    problemas_anti = []
    if not anti_found:
        problemas_anti.append("Paso 3 (Tensión del Favorito) no ejecutado")

    # Check convergence rule
    if anti_found and dc_found:
        dc_trap = bool(
            re.search(r'dc.*[>≥].*1\.0[5-9]', text_lower)
            or re.search(r'doble\s+oportunidad.*[>≥].*1\.0[5-9]', text_lower)
            or "trampa" in text_lower
        )
        k_techo = bool(re.search(r'techo|ceiling|máximo', text_lower))
        if dc_trap and k_techo:
            convergence_noted = any(m in text_lower for m in
                                     ["convergen", "convergencia", "triple", "no gana"])
            if not convergence_noted:
                problemas_anti.append("⚠️ K techo + doble oportunidad trampa detectados pero convergencia no declarada explícitamente")

    audit.add("3", "Tensión del Favorito", anti_found,
              problemas=problemas_anti,
              severidad="WARNING" if not anti_found else "INFO")

    # =========================================================================
    # PASO 3.5 — GOLES × FECHA × CONDICIÓN
    # =========================================================================
    goles_markers = ["goles.*fecha", "goles.*condición", "paso 3.5", "ley 7",
                     "últimos 6", "últimos.*local", "últimos.*visita",
                     "goles×fecha", "goles x fecha"]
    goles_found = any(re.search(m, text_lower) for m in goles_markers)

    problemas_goles = []
    if not goles_found:
        problemas_goles.append("Paso 3.5 (Goles × Fecha × Condición) no ejecutado")

    audit.add("3.5", "Goles × Fecha × Condición", goles_found,
              problemas=problemas_goles,
              severidad="WARNING" if not goles_found else "INFO")

    # =========================================================================
    # PASO 4 — RIESGO NO-VICTORIA
    # =========================================================================
    riesgo_markers = ["riesgo.*no.*victoria", "no.*victoria", "paso 4",
                      "puede no ganar", "condiciones para que.*no gane",
                      "riesgo de no-victoria", "factores de riesgo"]
    riesgo_found = any(re.search(m, text_lower) for m in riesgo_markers)

    problemas_riesgo = []
    if not riesgo_found:
        problemas_riesgo.append("Paso 4 (Riesgo de No-Victoria) no ejecutado")

    # Check underdog minimum
    pct_pattern = re.findall(r'(\d+(?:\.\d+)?)\s*%', text)
    has_zero_pct = any(float(p) == 0 for p in pct_pattern if float(p) < 5)
    if riesgo_found and has_zero_pct:
        problemas_riesgo.append("⚠️ Se detectó 0% asignado — verificar regla mínimo underdog v3.1")

    audit.add("4", "Riesgo No-Victoria", riesgo_found,
              problemas=problemas_riesgo,
              severidad="WARNING" if not riesgo_found else "INFO")

    # =========================================================================
    # PASO 5 — COMPLEMENTARIAS
    # =========================================================================
    comp_checks = {
        "Regresión al Nivel": ["regresión", "gap", "nivel.*real", "sobrerendimiento", "subrendimiento"],
        "Fe Perdida": ["fe perdida", "péndulo", "flag.*home", "flag.*away", "flag.*none",
                       "fe_perdida", "pendulum"],
    }

    for nombre, markers in comp_checks.items():
        found = any(m in text_lower for m in markers)
        problemas = [] if found else [f"{nombre} no mencionada en Paso 5"]
        audit.add("5", f"Complementaria: {nombre}", found,
                  problemas=problemas,
                  severidad="WARNING" if not found else "INFO")

    # Check Fe Perdida FLAG=NONE violation
    if "flag" in text_lower and "none" in text_lower:
        emotional_after_none = bool(re.search(
            r'none.*?(ventaja\s+emocional|impulso|ánimo|moral)',
            text_lower
        ))
        if emotional_after_none:
            audit.add_violation("Fe Perdida NONE",
                                "Se detectó narrativa emocional después de FLAG=NONE — prohibido")

    # =========================================================================
    # AUDITORÍA 2 (antes "§ANTI-SESGO-2")
    # =========================================================================
    as2_markers = [
        # Nuevos (v3.2)
        "auditoría 2", "auditoria 2", "auditoría-2", "auditoria-2",
        # Antiguos (v3.1, mantenidos para compatibilidad)
        "anti-sesgo-2", "anti-sesgo 2", "as-2", "§as-2",
        "anti sesgo 2", "antisesgo 2",
        # Comunes
        "autodestrucción", "autodestruccion",
        "pregunta de autodestrucción", "pregunta de autodestruccion",
        "contra-caso",
    ]
    as2_found = any(m in text_lower for m in as2_markers)

    problemas_as2 = []
    if not as2_found:
        problemas_as2.append("Auditoría 2 NO ejecutada (obligatoria antes de la conclusión)")

    audit.add("Auditoría 2", "Auditoría 2 (autodestrucción / contra-caso)", as2_found,
              problemas=problemas_as2,
              severidad="CRITICAL" if not as2_found else "INFO")

    # =========================================================================
    # VERIFICACIONES GLOBALES
    # =========================================================================

    # Check fusión K
    fusion_ok = any(m in text_lower for m in
                     ["fusión", "fusionada", "k_positivo + k_negativo",
                      "k_positivo+k_negativo", "fusión k", "k fusionada"])
    if not fusion_ok and k_found:
        audit.add_violation("Fusión K",
                            "No se detectó mención explícita de fusión K (k_positivo + k_negativo)",
                            severidad="WARNING")

    # Check both teams analyzed symmetrically
    # Simple heuristic: count team-specific analysis sections
    team_sections = len(re.findall(r'#{1,3}\s+.*?(local|visita|home|away)', text_lower))
    if team_sections < 2:
        audit.add_violation("Simetría",
                            f"Solo {team_sections} sección(es) de equipo detectada(s) — se requiere análisis simétrico de ambos equipos",
                            severidad="WARNING")

    return audit


def format_report(audit: ProtocolAudit) -> str:
    """Format audit results as a readable report."""
    lines = []
    lines.append("=" * 70)
    lines.append("  SAD PROTOCOL AUDIT REPORT v3.2")
    lines.append("=" * 70)

    # Summary counts
    total = len(audit.results)
    executed = sum(1 for r in audit.results if r.ejecutado)
    complete = sum(1 for r in audit.results if r.ejecutado and r.completo)
    critical = sum(1 for r in audit.results if r.severidad == "CRITICAL")
    warnings = sum(1 for r in audit.results if r.severidad == "WARNING")

    lines.append(f"\n  Pasos ejecutados: {executed}/{total}")
    lines.append(f"  Pasos completos:  {complete}/{total}")
    lines.append(f"  Críticos:         {critical}")
    lines.append(f"  Advertencias:     {warnings}")
    lines.append(f"  Violaciones:      {len(audit.violations)}")

    # Overall status
    if critical > 0:
        lines.append("\n  ❌ ESTADO: FALLA — hay pasos críticos sin ejecutar")
    elif warnings > 0:
        lines.append("\n  ⚠️  ESTADO: INCOMPLETO — hay advertencias pendientes")
    else:
        lines.append("\n  ✅ ESTADO: APROBADO — protocolo ejecutado completamente")

    # Detail per step
    lines.append("\n" + "-" * 70)
    lines.append("  DETALLE POR PASO")
    lines.append("-" * 70)

    for r in audit.results:
        icon = "✅" if r.ejecutado and r.completo else "⚠️" if r.ejecutado else "❌"
        lines.append(f"\n  {icon} Paso {r.paso}: {r.nombre}")
        lines.append(f"     Ejecutado: {'Sí' if r.ejecutado else 'NO'}  |  Completo: {'Sí' if r.completo else 'NO'}  |  Severidad: {r.severidad}")
        for p in r.problemas:
            lines.append(f"     → {p}")

    # Missing constants
    if audit.missing_constants:
        lines.append("\n" + "-" * 70)
        lines.append("  CONSTANTES K NO DETECTADAS EN EL ANÁLISIS")
        lines.append("-" * 70)
        for k in audit.missing_constants:
            lines.append(f"  ❌ {k}")

    # Violations
    if audit.violations:
        lines.append("\n" + "-" * 70)
        lines.append("  VIOLACIONES DE PROTOCOLO")
        lines.append("-" * 70)
        for v in audit.violations:
            icon = "🚨" if v["severidad"] == "CRITICAL" else "⚠️"
            lines.append(f"\n  {icon} [{v['rule']}] {v['description']}")

    # Action items
    action_items = []
    for r in audit.results:
        if not r.ejecutado:
            action_items.append(f"EJECUTAR Paso {r.paso} ({r.nombre})")
        elif not r.completo:
            action_items.append(f"COMPLETAR Paso {r.paso}: {'; '.join(r.problemas)}")

    for v in audit.violations:
        if v["severidad"] == "CRITICAL":
            action_items.append(f"CORREGIR violación: {v['rule']} — {v['description']}")

    if action_items:
        lines.append("\n" + "-" * 70)
        lines.append("  ACCIONES REQUERIDAS")
        lines.append("-" * 70)
        for i, item in enumerate(action_items, 1):
            lines.append(f"  {i}. {item}")

    lines.append("\n" + "=" * 70)
    return "\n".join(lines)


def main():
    if len(sys.argv) < 2:
        # If no file argument, read from stdin
        text = sys.stdin.read()
    else:
        filepath = Path(sys.argv[1])
        if not filepath.exists():
            print(f"Error: archivo '{filepath}' no encontrado")
            sys.exit(1)
        text = filepath.read_text(encoding="utf-8")

    if not text.strip():
        print("Error: el texto del análisis está vacío")
        sys.exit(1)

    audit = audit_analysis(text)
    report = format_report(audit)
    print(report)

    # Exit code: 1 if critical issues, 0 otherwise
    has_critical = any(r.severidad == "CRITICAL" and not r.ejecutado for r in audit.results)
    has_critical_violations = any(v["severidad"] == "CRITICAL" for v in audit.violations)
    sys.exit(1 if (has_critical or has_critical_violations) else 0)


if __name__ == "__main__":
    main()
