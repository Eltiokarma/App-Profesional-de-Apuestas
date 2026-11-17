# Estudio de las lecciones pendientes — 17/11/2026 (paso 1 de la revisión)

> **Estado: DIAGNÓSTICO. No se modificó ningún skill.** Base: las lecciones
> `pendiente` de `GET /analisis/cowork/lecciones` (cohorte vigente) bajadas el
> 17/11/2026 a las 09:58; todas de partidos del 10 al 16/11, posteriores a la
> subida de TDE v0.1.26, DTP v1.8, EFE v1.10 y sad-analysis v4.5. Población
> ciega PRE. Muestra de UNA semana, con mayoría de partidos de selecciones
> (fecha FIFA).

Cada lección se leyó entera y se clasificó por lo que dice su prosa, no por
el veredicto del lado (que es del partido, no de la regla) ni por la etiqueta
de Jev. Clases: `regla_sostuvo` (lo escrito se cumplió aunque el lado fallara),
`mal_aplicada` (la regla era correcta y el análisis se apartó), `regla_fallo`
(regla bien aplicada que no describió lo que pasó), `insumo`, `imprevisto`,
`otro_skill`, `no_dice`. Detalle por skill en `estudio_<skill>.md`; la
clasificación por lección, en `clasif_<skill>.json`.

## 1. La etiqueta `lectura_efe` de Jev no mide lo que dice

| Skill | Fallos etiquetados `lectura_efe` | De esos, la prosa menciona el EFE |
|---|---:|---:|
| teorema-del-echado | 107 | 7 |
| diagnostico-tactico | 102 | 4 |
| efe-clasificador | 31 | 28 |
| sad-analysis | 7 | 0 |

Fuera del EFE, Jev usa `lectura_efe` para «se aplicó mal una regla del
propio skill» (la descripción del modo dice «la rúbrica se aplicó mal»), porque
la taxonomía de `backend/analisis/modo_fallo.py` no tiene ese modo. Además,
Jev solo etiqueta la PRIMERA lección de cada lado (`orden` 1), y la mayoría de
las pendientes son `orden` ≥ 2: sin etiqueta por diseño, no por baja confianza.
Los «sin etiqueta» de orden 1 sí son confianza < 0,6 (en el TDE, casi siempre
lados con fallo donde la rama del TDE se cumplió).
**El DTP no heredó ningún fallo del EFE** (0 de 131); hay 4 casos al revés: el
EFE o el TDE tenían bien el dato y el DTP no lo tomó.

## 2. Por clase

| Skill | Lecciones | sostuvo | mal aplicada | regla falló | insumo | imprevisto | no dice | otro skill |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| TDE v0.1.26 | 276 | 198 | 31 | 19 | 6 | 7 | 15 | 0 |
| DTP v1.8 | 347 | 187 | 93 | 38 | 15 | 5 | 9 | 0 |
| EFE v1.10 | 189 | 123 | 35 | 14 | 9 | 0 | 7 | 1 |
| sad-analysis v4.5 | 70 | 35 | 14 | 20 | 0 | 1 | 0 | 0 |

(DTP: 59 de las 347 son de copas nacionales; sin ellas, 161 / 78 / 33 / 12 / 3 / 1 / 0.)

Lectura: las reglas vigentes se sostienen en su mayoría; lo que más se repite
es **no cumplir una regla que ya está escrita**, casi siempre por el mismo
motivo: **el once oficial no se propaga** (banco desde la hoja, grid, tabla F1,
B y F del EFE al rehacer).

## 3. Lo que tiene material (≥ 3 partidos distintos)

**Transversal — el once oficial al rehacer (app antes que skill):**
banco nombrado con un titular o incompleto (TDE disc 66: 16 mal aplicadas; DTP:
16 en 15 partidos), grid sin copiar (DTP 8/8), piezas sin rehacer (DTP 6/6),
tabla F1 sin rehacer con titulares sin fila (EFE: 19 lecciones, 15 partidos).
Repetir la regla en el skill no cambió la conducta: pide que la app entregue
los suplentes de la hoja (ya en PENDIENTES como «banco probable») y que el
recibo frene un depósito con ONCE-SIN-FILA-F1.

**TDE v0.1.27** (además de lo aprobado: `ventajaPorFuerza`, sin contradicciones):
- Pieza del seguro en la rama de ventaja (candidato de v0.1.26): 3 partidos firmes → pasa a texto.
- `siExpulsion` incompleta (falta la línea «ganando») en 4 partidos: aclaración.
- SOB1 = 1 por tabla sin régimen de exposición, 5 partidos: escribir la SOB condicionada al once; bajar el peso es solo candidato a medir.
- Superioridad numérica: desdoblar por marcador y roja propia ganando (3 a 1): candidatos a medir, n chico.

**DTP v1.9:**
- Posesión por rama: 12 de 12 mal aplicadas (perfil del rival fuera de su condición de hoy; falta la rama «arriba» separada).
- Candidatos de v1.8 que llegan al umbral: el reconvertido también ataca (4 casos) y la presión alta con su vuelta (3).
- Aclaraciones: materia de pelota parada desde los córners del cruce; con 0-1 penales en la base el 9 titular va en la lista de ejecutores.
- Numérico, a backtest y no al skill: 14 de 20 veredictos de rama fallados eran NEUTRO que el volumen decidió (banda de «parejo»).

**EFE v1.11:**
- F1 con el once oficial: alinear «sin umbral» de la rúbrica con el «corte de 3» que citan las lecciones.
- Arquero suplente/nuevo no fue la vía de gol en 9 partidos: aclaración; bajar el ×1,5 de F2c, candidato a medir.
- Rama «once alternativo» faltante o corta en 6 casos (cuando se escribió, 10 de 14).
- Alertas: COLAPSO EN CASCADA 10/11, EJE-DEBUTANTE 9/14 (lo que falla es el insumo), F3 se cumple como «baja la confianza». EFE-EMPATE-TECNICO 27/27 «cumplida»: así escrita no se puede refutar; la prueba es la medición de la app.

**sad-analysis v4.6** (además de lo aprobado):
- El falsador del 1X2 nombra un gol suelto del débil: 6 de 6 mal aplicadas → aclarar que el falsador es lo que hace imposible el pronóstico.
- BURBUJA-DE-UN-PARTIDO (aprobada) sale apoyada con muestra chica: la desconfianza acertó 3 de 3 y ~6 rachas de un partido con riesgo alto reventaron.
- K-CERCA-EXTREMO declarado y apostado igual en 4 de 8: cumplimiento, no regla.
- La burbuja revienta a cero y no al otro signo (5 + 4 partidos) y lo que toca el 1X2 o el empate: **solo con backtest** (puntos calibrados).
- SOBRE-LA-CASA y las observaciones (h) e (i): sin material nuevo.

## 4. Sin material (1-2 casos) — no entra

SOB de la hora con 0-0, lista del 44 (f) en `siLeEmpatan`, defecto por quien
persigue, roja propia perdiendo (2 a 2), ventana desde el cambio ofensivo
(sigue en «medir primero»: hay casos, falta denominador).

## 5. Decisiones para el usuario

1. **Jev / `modo_fallo`:** agregar a la taxonomía un modo para «regla del propio
   skill mal aplicada» y re-etiquetar. Hoy el dossier agrupa por una etiqueta
   que en el TDE y el DTP es mayormente falsa. Re-etiquetar las selladas
   necesita un endpoint nuevo (de mantenimiento, fuera de Cowork) y la clave de
   Jev en el servidor; no es zona sagrada.
2. **El once oficial** se arregla en la app (suplentes de la hoja, recibo que
   frena ONCE-SIN-FILA-F1) antes que en el texto de los skills.
3. Con esto, el **paso 2** (redactar las propuestas) tiene material para las
   cuatro versiones, en su mayoría aclaraciones; ningún número se mueve sin
   backtest.
