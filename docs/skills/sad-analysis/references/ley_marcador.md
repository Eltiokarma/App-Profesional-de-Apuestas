# Ley del Marcador — Predictor de Goles v6 (modelo Poisson)

Consultar este archivo cuando haya dudas sobre: fórmulas Poisson, features del modelo de goles, umbrales de sugerencia, o discretización de niveles.

## Fundamento: distribución de Poisson

```
P(X = k) = (λ^k × e^(-λ)) / k!
```

donde **λ = goles esperados** y **k = número de goles**.

### Probabilidades derivadas de λ

- **Over N goles:** `P(Over N) = 1 - CDF(N, λ)`
- **Total de goles del partido:** convolución de dos distribuciones Poisson independientes (una por equipo).
- **Ambos equipos marcan (BTTS / "Both Teams To Score"):**
  ```
  P(home ≥ 1) × P(away ≥ 1) = (1 - e^(-λ_home)) × (1 - e^(-λ_away))
  ```
- **Marcador exacto:** matriz 7×7 donde `P(h-a) = P(home = h) × P(away = a)`.

**Ventaja de v6:** todas las probabilidades derivan de un solo λ por equipo → coherencia garantizada (`P(Over N+1) ≤ P(Over N)` siempre se cumple).

## Arquitectura v6

Dos `GradientBoostingRegressor` independientes (uno para `λ_home`, otro para `λ_away`).

| Hiperparámetro | Valor |
|---|---|
| `n_estimators` | 100 |
| `max_depth` | 4 |
| `learning_rate` | 0.1 |
| `min_samples_split` | 20 |
| Split temporal | 80 / 20 |
| Scaler | `StandardScaler` |
| Serialización | `joblib` |

## 21 features de entrada

| # | Feature | Descripción |
|---|---|---|
| 1-5 | `home_level`, `away_level`, `level_bins`, `level_diff` | Niveles continuos y discretos + diferencia entre equipos |
| 6-9 | `home/away_attack`, `home/away_defense` | Promedios de **goles a favor / goles en contra** como local o visitante (últimos 10 partidos) |
| 10-11 | `attack_vs_defense` cruzados | Interacciones: ataque local × defensa visitante, y viceversa |
| 12-15 | `home/away_k_for`, `home/away_k_against` | Constantes K de goles anotados / recibidos (promedio últimos 10) |
| 16-19 | `clean_sheet_rate`, `failed_rate` | Tasa de arco en cero y tasa de partidos sin anotar |
| 20-21 | `h2h_home_avg`, `h2h_away_avg` | Promedio de goles en el **historial directo** entre ambos equipos |

`level_diff ≥ 3` = **favorito claro**, con λ significativamente mayor.

## Umbrales calibrados de sugerencias

Sugerir una apuesta de **Over** cuando la probabilidad supera el umbral:

| Línea | Confianza alta 🔥 | Confianza media ⚠️ |
|---|---|---|
| Home Over 0.5 | ≥ 91% | ≥ 84% |
| Home Over 1.5 | ≥ 70% | ≥ 63% |
| Home Over 2.5 | ≥ 51% | ≥ 44% |
| Away Over 0.5 | ≥ 86% | ≥ 79% |
| Away Over 1.5 | ≥ 61% | ≥ 54% |
| Away Over 2.5 | ≥ 50% | ≥ 43% |
| Total Over 2.5 | ≥ 70% | ≥ 63% |
| Total Over 3.5 | ≥ 67% | ≥ 60% |
| Ambos equipos marcan (Sí) | ≥ 78% | ≥ 71% |

## Discretización de niveles (10 bins)

| Bin | Rango | Etiqueta |
|---|---|---|
| 0 | < 0.6 | Sin datos |
| 1 | 0.6 – 1.3 | Muy débil |
| 2 | 1.3 – 1.6 | Débil |
| 3 | 1.6 – 1.9 | Regular bajo |
| 4 | 1.9 – 2.1 | Promedio bajo |
| 5 | 2.1 – 2.35 | Promedio |
| 6 | 2.35 – 2.55 | Promedio alto |
| 7 | 2.55 – 2.85 | Fuerte |
| 8 | 2.85 – 3.2 | Muy fuerte |
| 9 | > 3.2 | Élite |

## Bases de datos consultadas

- `sad.db` (fixtures, teams) → resultados históricos.
- `levels.db` (`team_levels`) → nivel continuo por equipo y fecha.
- `constants.db` (`constants`) → K de goles para las features 12-15.
