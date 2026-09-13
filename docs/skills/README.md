# Snapshot de los skills — material de referencia, no fuente de verdad

Copia de los cinco skills del pipeline SAD tal como estaban el **13.09.2026**,
subidos por el usuario para diseñar el bucle de aprendizaje
(`docs/APRENDIZAJE.md`).

Tres cosas que conviene tener claras antes de tocar nada aquí:

1. **La fuente de verdad son los skills de la cuenta de Cowork**, no esta
   carpeta. Esto es una foto para poder diseñar contra algo concreto y, el día
   que toque regenerar los `.zip`, tener una línea base con la que comparar.
2. **La app nunca escribe aquí.** Lo que la app acumula son *lecciones* en
   `efe.db`; convertirlas en una versión nueva de un skill es un paso manual
   que el usuario autoriza (ver la fase D del diseño).
3. **Si el usuario actualiza un skill en Cowork, esta copia queda vieja.**
   Antes de usarla como base de un `.zip`, pedir la versión del día.

## Qué hay dentro que importa para el bucle

| Skill | Su superficie de aprendizaje | Disciplina que impone |
|---|---|---|
| `teorema-del-echado` | `assets/casos/registro.csv` (44 columnas: lo declarado, lo observado y la `leccion`) + `references/CALIBRACION.md` | tres poblaciones (`ciega`, `por_resultado`, `post_resultado`) y **solo la ciega calibra**; Brier objetivo < 0.20; umbral binding N ≥ 5 |
| `diagnostico-tactico` | "REGISTRO DE LA CADENA — validación acumulada" (M5) | "los casos contaminados fijan rúbrica pero **no acreditan**" |
| `efe-clasificador` | registro de casos de validación (bloques A-H) | cada corrección derivada se ata a un caso numerado |
| `sad-analysis` | `references/casos_referencia.md` + `scripts/audit_protocol.py` | el script detecta pasos faltantes, **no modifica veredictos** |
| `futbol-timeline` | — | no tiene registro propio: su acierto se mide indirectamente |

La coincidencia entre los dos primeros no es casual y es lo que sostiene todo
el diseño: **un caso elegido porque pasó algo no prueba nada.** Cualquier
acumulación automática que mezcle las dos poblaciones infla la tasa de acierto
y produce exactamente el error que la calibración del TDE ya detectó una vez
(11% real contra 31% mezclado).
