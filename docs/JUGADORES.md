# Capa de jugadores — spec e implementación

Objetivo: que "Romario no juega hoy" deje de ser un nombre suelto. La app
calcula indicadores por jugador desde API-Football y los sirve en dos formas:
**Plantilla** (página de Equipo) y **Ficha de partido** (los dos planteles
juntos, con bajas y congestión), que además se **cruza con los skills**
(EFE / DTP / timeline): los números vienen de nuestra base, la
interpretación la pone el análisis.

Principio rector: la app calcula, los skills interpretan. Ningún número de
esta capa entra al Motor SAD (capa 3, solo con backtest en mano).

## Arquitectura

```
backend/ingesta/jugadores.py   ESCRIBE (única capa que escribe, como el extractor):
                               players/injuries/transfers/coachs → sad.db
backend/jugadores.py           LEE sad.db y calcula los indicadores (0 requests)
backend/app.py                 GET /equipos/{id}/plantilla · GET /fixtures/{id}/ficha
backend/analisis/motor.py      inyecta la ficha en datos_cacheados del EFE/timeline
src/sections/Equipo.tsx        sección Plantilla (mock y http, mismo contrato)
```

## Ingesta (backend/ingesta/jugadores.py)

```bash
python -m backend.ingesta.jugadores               # equipos con NS en <= 3 días
python -m backend.ingesta.jugadores --dias 7      # ventana más ancha
python -m backend.ingesta.jugadores --equipo 541 --temporada 2026  # un equipo a mano
python -m backend.ingesta.jugadores --ttl-horas 24  # refresco más agresivo
```

- Selección: equipos de NUESTRAS ligas con fixtures NS próximos (default 3 días).
- TTL por equipo (default 168 h = 7 días, en `plantillas_meta`): fuera de
  ventana de traspasos la plantilla casi no cambia; en ventana, bajar el TTL.
- Presupuesto por equipo: `players` paginado (~2-3 req) + `injuries` (1) +
  `transfers` (1) + `coachs` (1) ≈ **5-6 requests/equipo**, contra el MISMO
  presupuesto autoajustado del extractor (cabeceras x-ratelimit, respaldo
  RapidAPI incluido). La corrida diaria lo ejecuta tras el extractor.

Tablas nuevas en sad.db (todas `IF NOT EXISTS`, el backend degrada a vacío
si no existen):

- `jugadores` (id, nombre, edad, foto, nacionalidad)
- `jugador_stats` (player_id, team_id, league_id, season, posicion, partidos,
  titularidades, minutos, rating, goles, asistencias, goles_encajados,
  paradas, tiros, tiros_puerta, pases_clave, amarillas, rojas, …)
  — una fila por competición; los indicadores agregan por (player, team, season).
- `jugador_bajas` (player_id, team_id, season, tipo, detalle, fecha)
  — de `injuries` (lesiones Y sanciones reportadas por la API).
- `traspasos` (player_id, fecha, tipo, team_in, team_in_nombre, team_out, team_out_nombre)
- `entrenadores` (team_id, coach_id, nombre, foto, desde)
- `plantillas_meta` (team_id, season, actualizado_en) — el TTL.

## Indicadores (backend/jugadores.py) — fórmulas

Todo se calcula EN LECTURA desde sad.db (0 requests). Reglas estadísticas:

1. **Por 90 minutos, nunca en bruto**: `x90 = x / minutos * 90` (minutos > 0).
2. **Encogimiento bayesiano (shrinkage)** de la producción ofensiva:

   ```
   gaP90Ajustado = (minutos · gaP90 + M · prior_posicion) / (minutos + M),  M = 900
   ```

   `prior_posicion` = media de (G+A)/90 de TODOS los jugadores de esa posición
   en nuestra base con ≥ 180 min (fallback: prior global). Con 300 minutos
   manda el prior; con 2 500, sus datos. El indicador no miente por muestra chica.
3. **Confianza visible**: `A` ≥ 1800 min · `B` ≥ 600 · `C` < 600. La UI y los
   skills degradan el peso de lo que afirmen según este grado.
4. `pctMinutos = minutos / max(minutos de la plantilla)` — proxy de titularidad
   robusto a equipos con distinto nº de partidos capturados.
5. `participacionOfensiva = (G+A) / Σ goles de la plantilla` (cruda, para la
   cuota del equipo; la ajustada es gaP90Ajustado).
6. **Dependencia (HHI)** del equipo: `Σ share_i²` sobre los shares de G+A
   (solo jugadores con G+A > 0). ~1/n = coral · →1 = él-dependiente. Se sirven
   además los 3 mayores shares (`top`).
7. **Porteros**: `paradasP90` y `golesEncajadosP90` (la participación ofensiva
   no aplica y va en 0; la UI muestra sus métricas propias).
8. **En capilla** (descriptivo): `amarillas ≥ 4` sin roja — riesgo de sanción
   por acumulación. La regla exacta varía por torneo: es bandera, no veredicto.
9. **Recién llegado**: traspaso hacia el equipo en ≤ 90 días → flag con origen
   y fecha. Sus stats vienen de otro contexto: la confianza baja un grado
   (regla de reseteo, misma filosofía que q*/k* del motor).
10. **Revolución de plantilla**: llegadas/salidas en los últimos 120 días
    (conteo de traspasos). Alimenta la lectura de estabilidad del EFE.
11. **Congestión** (solo ficha de partido, sale de fixtures ya capturados —
    0 requests): `diasDescanso` desde el último jugado y `partidos21d`.

Sin datos de jugadores para un equipo → `jugadores: []` y agregados en null:
la UI lo dice ("plantilla sin capturar") y NADA se inventa.

## Contrato (docs/openapi.yaml)

- `GET /equipos/{equipoId}/plantilla` → `PlantillaDTO`
- `GET /fixtures/{fixtureId}/ficha` → `FichaPartidoDTO` (Plantilla de ambos
  + `bajas` resumidas + `congestion` por lado)

La ficha es EL puente con los skills: JSON determinista calculado por código.

## Cruce con los skills (backend/analisis/motor.py)

El EFE ya recibía `datos_cacheados` locales (tabla, resultados, próximos) y
`xi_reciente`/`bajas` de la API. Ahora, si hay datos de jugadores en sad.db:

- tipo `plantel`: resumen cuantitativo por jugador (pos, % min, G+A, rating,
  confianza, flags) — deja de buscarse en la web y el IP ponderado de
  disponibilidad se apoya en minutos REALES, no estimados.
- tipo `dt`: entrenador actual con fecha de asunción (de `entrenadores`).
- tipo `bajas`: se enriquece con las bajas de `jugador_bajas` + el PESO de
  cada baja (pctMinutos, participación) — "falta Romario" pasa a "falta el
  84% de minutos y 28% de los goles".
- timeline: recibe `movimientos_db` (traspasos y cambio de DT con fechas
  exactas) como eventos confirmados; la web queda para el contexto narrativo.

La búsqueda web sigue cubriendo lo que la base no puede: alineación filtrada,
rumores, contexto. División del trabajo: números de la base, criterio del skill.

## Presupuesto de requests (resumen)

| Pieza | Endpoint | Costo |
|---|---|---|
| Plantilla + stats | `players?team&season` | ~2-3/equipo, TTL 7d |
| Bajas | `injuries?team&season` | 1/equipo, TTL 7d (la corrida diaria la refresca) |
| Traspasos | `transfers?team` | 1/equipo, TTL 7d |
| DT | `coachs?team` | 1/equipo, TTL 7d |
| Indicadores + ficha | — | 0 (lectura de sad.db) |
| Congestión | — | 0 (fixtures ya capturados) |

## Capas siguientes (no implementadas aquí)

- **Capa 2**: forma reciente (EWMA de rating últimos 5 vs temporada, z-score) y
  **con/sin ajustado por nivel SAD** vía backfill de `fixtures/players`
  (~1 req/partido pasado, cacheable para siempre; la request trae AMBOS equipos).
- **Capa 3**: ajuste del λ Poisson por bajas (solo si el backtest tipo §5
  mejora la calibración) y cruce baja-vs-movimiento-de-cuota con odds_history.
- Valor de mercado: **descartado** (Transfermarkt sin API; scraping frágil y
  contra ToS). Los niveles SAD ya miden calidad real del equipo.
