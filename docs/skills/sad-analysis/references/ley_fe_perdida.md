# Ley de la Fe Perdida — El péndulo de la hinchada

Consultar este archivo cuando haya dudas sobre: flags, péndulos, zonas emocionales, tabla empírica de probabilidades, o goal flags.

## Concepto

Modela el **estado emocional de la hinchada** como un péndulo en el rango `[-100, +100]`. Calibrado sobre 42.452 partidos.

**El veredicto operativo es el flag, no los péndulos individuales.**

## Pipeline: 5 fases

1. **Estatura** del equipo → Grande / Medio / Chico (por percentil de cuotas dentro de su liga).
2. **Faith** (fe) → impacto emocional de cada resultado, diferenciado por estatura.
3. **Péndulo** → agregación con decay 0.88 sobre una ventana de 10 partidos.
4. **Gap y Flag** → `gap = péndulo_local - péndulo_visitante`.
5. **Probabilidades** → tabla empírica de búsqueda.

## Estatura (por percentil dentro de su liga)

| Estatura | Percentil | Significado |
|---|---|---|
| **Grande** | Top 25% (cuotas más bajas) | Se espera que gane siempre |
| **Medio** | 25% – 75% | Resultado incierto |
| **Chico** | Bottom 25% (cuotas más altas) | Se espera que pierda |

## Faith (fe) por estatura

Valores clave del impacto emocional según resultado:

**Equipo Grande:**
- Victoria: `+1.0`
- Empate: `-0.5` (el empate es decepción)
- Derrota: `-1.0`

**Equipo Medio:**
- Victoria: `+1.0`
- Empate: `+0.3`
- Derrota sin marcar: `-1.0`
- Derrota anotando: `-0.7`

**Equipo Chico:**
- Victoria: `+1.5`
- Empate: `+0.8`
- Derrota ajustada anotando: `+0.1`
- Derrota sin marcar: `-0.8`

**Weight (peso)** = función de `team_prob` (probabilidad del equipo según cuota pre-partido).

## Péndulo

```
weighted_sum   = Σ(faith[j] × weight[j] × 0.88^(N-1-j))
max_possible   = Σ(1.5 × 0.88^(N-1-j))
pendulum_score = (weighted_sum / max_possible) × 100   // recortado a [-100, +100]
```

Los últimos 3-4 partidos concentran ≈ 75% del peso total.

## Zonas emocionales

| Zona | Rango del péndulo | Estado de la hinchada |
|---|---|---|
| Euforia | +18 a +100 | Hinchada enloquecida |
| Confianza | +6 a +18 | Optimismo |
| Neutral | -6 a +6 | Sin emoción fuerte |
| Tensión | -18 a -6 | Preocupación |
| Frustración | -35 a -18 | Rabia |
| Fe destruida | -100 a -35 | Abatimiento total |

## Flags de oportunidad (operativos)

| Flag | Condición | Edge (puntos porcentuales) |
|---|---|---|
| `HOME_STRONG` | `gap ≥ +35` | +16 |
| `HOME` | `gap ≥ +25` | +10 |
| `NONE` | `-25 < gap < +25` | 0 |
| `AWAY` | `gap ≤ -25` | +10 |
| `AWAY_STRONG` | `gap ≤ -35` | +12 |

> **Regla SAD:** flag `NONE` = sin señal. **Prohibido fabricar una ventaja emocional cuando el flag es `NONE`.**

## Goal flags (por equipo individual)

| Goal flag | Condición | P(anota local) | P(anota visitante) |
|---|---|---|---|
| `SCORES` | péndulo ≥ +18 | 85.9% | 73.8% |
| `NORMAL` | -18 < péndulo < +18 | 76.3% | 66.0% |
| `SECO` | péndulo ≤ -18 | 69.5% | 55.1% |

## Baseline (sin señal de Fe Perdida)

- Victoria local: ≈ 45%.
- Empate: ≈ 26%.
- Victoria visitante: ≈ 29%.
- Margen esperado: ≈ +0.3 goles a favor del local.
