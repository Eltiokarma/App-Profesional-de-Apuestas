# Motor de Tensión del Favorito v5 — Predicción de Rupturas

> **Antes:** *Motor Anticulebras*. Renombrado en v3.2 del skill SAD.

Consultar este archivo cuando haya dudas sobre: fórmula del Índice de Favoritismo (ICF), features del modelo ML, sistema de tensión acumulada, calibración del modelo, o fallback heurístico cuando no hay modelo entrenado.

## Concepto

**Principio de fondo:** cuando todos los favoritos van ganando una jornada, eventualmente uno cae. El motor predice **cuándo y cómo** ocurrirá esa ruptura.

A esto antes se le llamaba *"Ley de las Culebras"* (jerga peruana de apuestas: la "culebra" es la racha del favorito que se hace larga y que termina rompiéndose). En este documento se usa el término neutro **Tensión del Favorito**.

## Arquitectura: 3 fases

1. **Índice de Favoritismo (ICF)** → calibrado con regresión Ridge.
2. **Clasificación ML** → Random Forest con 8 features.
3. **Ranking + Tensión Acumulada** → identificación del candidato a ruptura.

## Fase 1: Índice de Favoritismo (ICF)

```
ICF = w_local        × k_pos_local
    + w_goles_a      × k_goles_local_anotado
    - w_goles_r      × k_goles_local_recibido
    - w_negativo     × k_neg_local
    + w_nivel        × nivel_equipo
```

**Pesos por defecto:**

| Componente | Peso |
|---|---|
| `k_local` | 1.0 |
| `k_goles_anotado` | 0.8 |
| `k_goles_recibido` | 0.6 |
| `k_negativo` | 0.3 |
| Nivel del equipo | 1.2 |

Los pesos se calibran con regresión Ridge usando las cuotas de mercado como variable objetivo.

## Conversión ICF → probabilidades 1X2

```
delta         = ICF_home - ICF_away
home_strength = 1 / (1 + exp(-scale_k × delta))
draw_factor   = exp(-0.3 × |delta|)
prob_draw     = 0.26 × (0.5 + draw_factor)   // recortado a [0.15, 0.40]
remaining     = 1 - prob_draw
prob_home     = home_strength × remaining
prob_away     = (1 - home_strength) × remaining
```

**Criterio de favorito:** un equipo se considera favorito cuando su probabilidad supera `FAVORITE_THRESHOLD = 0.40`.

## Fase 2: 8 features del modelo ML (v5)

| # | Feature | Tipo | Descripción |
|---|---|---|---|
| 1 | `prob_draw` | Continua | Probabilidad de empate del ICF. **Es el predictor más importante** para detectar rupturas. |
| 2 | `prob_underdog` | Continua | Probabilidad del no-favorito |
| 3 | `icf_diff` | Continua | `|ICF_home - ICF_away|` (paridad del partido) |
| 4 | `position_normalized` | Continua | Posición del partido dentro de la jornada (0-1) |
| 5 | `is_simultaneous` | Binaria | Partido simultáneo (≤ 15 min de diferencia con otro) |
| 6 | `accumulated_tension` | Continua | Tensión acumulada en la jornada hasta ese punto |
| 7 | `match_importance` | Continua | Importancia del partido según fase de temporada |
| 8 | `rest_days_diff` | Continua | Diferencia de días de descanso desde la perspectiva del favorito |

**Hiperparámetros del Random Forest:**

```
n_estimators     = 100
max_depth        = 10
min_samples_split = 20
class_weight     = balanced
```

## Sistema de tensión acumulada

### Tensión intra-día (dentro de la misma jornada)

```
acumulado = Π(prob_favorito[j], j = 1..i)
tension[i] = (1 - acumulado) + tension_heredada × 0.7
```

Cada vez que un favorito va ganando, el producto acumulado baja → la tensión sube. La idea: cuanto más se prolonga una jornada sin caída de favoritos, más probable es que el siguiente caiga.

### Tensión entre días

- Si la racha del favorito **no se rompe** durante el día → la tensión se hereda con factor **× 0.7** al día siguiente.
- Si la racha **se rompe** → reset a 0.

## Importancia del partido

| Fase | Importancia |
|---|---|
| Final | 1.00 |
| Semifinal | 0.95 |
| Cuartos | 0.90 |
| Playoff | 0.85 |
| Fase decisiva de liga (> 85% de la temporada) | 0.90 |
| Cierre de temporada (70-85%) | 0.70 |
| Media temporada | 0.50 |
| Inicio de temporada (< 25%) | 0.30 |

## Fallback heurístico (cuando no hay modelo ML entrenado)

Si no se puede correr el Random Forest, sumar bonificaciones según condiciones:

| Condición | Bonificación |
|---|---|
| `prob_draw ≥ 0.28` | +12% |
| `icf_diff < 0.3` | +8% |
| `accumulated_tension > 0.5` | +5% |
| `is_simultaneous` | +3% |
| `prob_underdog > 0.30` | +6% |
| `match_importance ≥ 0.7` | +5% |
| `rest_days_diff < -0.3` | +4% |
