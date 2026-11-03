# Propuesta: núcleo y historial de los skills de la corrida

> **Estado: PROPUESTA (03/11/2026). No se modificó ningún skill.** Pedido del
> usuario: bajar los tokens que cada subagente de la corrida de partes carga al
> leer los skills, **sin cambiar ninguna regla**. Base medida: la copia de
> `docs/skills/` en `origin/main` (a328e55): TDE v0.1.25, DTP v1.7, EFE v1.9
> (rúbrica), efe-dashboard v1.12 y sad-analysis v4.4. Tokens ≈ caracteres / 4.
> **La fuente de verdad son los skills de la cuenta** (`docs/skills/README.md`):
> lo que se apruebe acá se aplica al zip que se sube, y la copia del repo se
> actualiza igual.

## 0. Resumen

| Qué carga un subagente de `partes` | Hoy | Después (fase 1) | Ahorro |
|---|---:|---:|---:|
| `teorema-del-echado` (SKILL + INDICE_IE + TIPOLOGIA + DETECCION_DATOS) | 69,2 K | 41,8 K | 27,4 K |
| `diagnostico-tactico` (SKILL) | 18,3 K | 14,3 K | 4,0 K |
| `efe-clasificador` (SKILL + rúbrica v1.9) | 22,9 K | 19,7 K | 3,2 K |
| `sad-analysis` (SKILL) | 15,0 K | 13,5 K | 1,5 K |
| Prompt de `docs/COWORK.md` (v2.6) | 17,4 K | 17,4 K | 0 (no se toca en la fase 1) |
| **Total por subagente** | **142,8 K** | **106,7 K** | **36,1 K (−25 %)** |
| *Aparte, si se lee:* `registro.csv` del TDE (PASO 0, punto 4) | 16,5 K | 16,5 K | ver §3.3 |
| *Aparte, si se carga:* `efe-dashboard` (el encargo no lo carga) | 7,2 K | 5,2 K | 2,0 K |

- **El grueso es el changelog del TDE**: 23,3 K de los 50,9 K de su `SKILL.md`
  son las notas de versión v0.1.25 → v0.1.1, y otros 2,9 K son el esquema del
  registro (columnas, `pre_rubrica`, numeraciones ausentes).
- **Reglas que hoy viven SOLO en un historial: 13** (10 del TDE, 1 del DTP,
  2 de efe-dashboard; EFE y sad-analysis ya tienen todo integrado en el
  cuerpo). Dos de las del TDE tienen la vigencia en duda y una choca con una
  disciplina posterior: **no se copian sin decisión del usuario** (§2.1).
- **Ahorro estimado: ≈ 0,65 USD por parte** (§4).

---

## 1. Secciones por archivo, con tokens y clase

Clases: **núcleo** (se aplica al analizar un partido) · **historial** (notas
de versión, casos que motivaron una regla, mediciones, esquema del registro,
notas de revisión) · **mixto** (regla y su historia en el mismo párrafo).

### 1.1 `teorema-del-echado/SKILL.md` — 50,9 K

| Líneas | Sección | Tokens | Clase |
|---|---|---:|---|
| 1-7 | frontmatter y título | 0,2 K | núcleo |
| 8-15 | «Dónde vive el registro canónico» (sha256 del CSV) | 0,3 K | mixto: la regla del sha256 vale para quien LEA el registro; queda resumida en PASO 0 |
| 16-294 | notas de versión v0.1.25 … v0.1.1 (25 bloques: v0.1.25 1,2 K · v0.1.24 0,6 · v0.1.23 1,0 · v0.1.22 0,2 · v0.1.21 1,0 · v0.1.20 0,6 · v0.1.19 1,2 · v0.1.18 1,4 · v0.1.17 1,3 · v0.1.16 0,9 · v0.1.15 0,7 · v0.1.14 1,6 · v0.1.13 1,7 · v0.1.12 1,4 · v0.1.11 1,5 · v0.1.10 1,3 · v0.1.9 1,1 · v0.1.8 0,8 · v0.1.7 0,9 · v0.1.6 0,6 · v0.1.5 0,7 · v0.1.4 0,3 · v0.1.3.1 0,3 · v0.1.3 0,7 · v0.1.1 0,3) | 23,3 K | **historial** |
| 295-307 | Qué mide y qué NO mide | 0,3 K | núcleo |
| 308-331 | LA TESIS | 0,4 K | núcleo (ojo: «la lectura que se comunica es el riesgo compuesto» quedó vieja con la v0.1.20; no se toca acá) |
| 332-488 | Flujo: PASO 0, 0-bis (FECHA-1, FICHA MÍNIMA), 1, 2, 3, 4, 5, 6 | 5,2 K | núcleo |
| 489-657 | Disciplina 1-66 (y la nota «Desfase de documentación», 554) | 17,2 K | **mixto**: la regla en negrita suma ≈ 3,5 K; el resto son casos (TDE-0xx, partidos), conteos e intervalos |
| 658-755 | EL REGISTRO: esquema de 51 columnas, `pre_rubrica`, trampa de `IE_recomputado_esquema6`, numeraciones ausentes, filtro de frecuencia, TDE-026 | 2,9 K | **historial** (se usa al calibrar o al escribir filas; el parte no escribe CSV: COWORK §5) |
| 756-fin | Integración con el ecosistema SAD | 1,0 K | núcleo |

### 1.2 Referencias del TDE que manda leer el PASO 0

| Archivo | Tokens | Clase |
|---|---:|---|
| `references/INDICE_IE.md` líneas 3-27: notas de versión v0.1.19 … v0.1.1 | 1,9 K | **historial** (todo lo que dicen está en el cuerpo del mismo archivo o en las disciplinas; ver §2) |
| `references/INDICE_IE.md` resto (fórmula, FECHA-1, FICHA MÍNIMA, compuertas, bloques F/C/P/S, ventana, mapeo, ISE, caja, salida mínima) | 12,6 K | núcleo (con casos adentro; «Candidatos NO ratificados» se queda: dice qué hacer si se usan) |
| `references/TIPOLOGIA.md` | 2,5 K | núcleo |
| `references/DETECCION_DATOS.md` | 1,3 K | núcleo |
| `assets/casos/registro.csv` | 16,5 K | historial de casos; el propio skill lo declara «instantánea obsoleta» salvo chequeo de sha256 (§3.3) |
| `references/CALIBRACION.md` (no lo pide el PASO 0; lo cita la corrida para cerrar casos) | 9,1 K | historial / cierre |
| `REGISTRO.md`, `references/PLANTILLA_CASO.md` | 4,2 K + 1,7 K | historial / cierre (no se leen al analizar) |

### 1.3 `diagnostico-tactico/SKILL.md` — 18,3 K

| Líneas | Sección | Tokens | Clase |
|---|---|---:|---|
| 1-7 | frontmatter y título | 0,2 K | núcleo |
| 8-95 | notas de versión v1.7 (1,2 K) · v1.6 (0,5) · v1.5 (0,7) · v1.4 (0,9) · v1.3 (0,6) · v1.2 (0,2) · v1.1 (0,1) | 4,2 K | **historial** |
| 96-150 | Qué es / cadena rodante / flujo | 0,7 K | núcleo |
| 153-168 | M1 Lectura de alineación | 1,3 K | mixto (reglas con su versión y su caso entre paréntesis) |
| 169-272 | M2 Mapa de enfrentamiento (checklist de 6, vías, carriles, dos capas) | 7,7 K | mixto |
| 273-283 | M3 Plan por fases | 0,6 K | núcleo |
| 284-342 | M4 Autopsia de gol · M5 Diagnóstico de fase (cierre) | 2,3 K | núcleo del cierre (veredictos); en `partes` se usa para el cierre del anterior |
| 343-375 | M6 · método de responsables · disciplina | 0,7 K | núcleo |
| 376-395 | Salidas (JSX / reporte) | 0,2 K | núcleo (modo interactivo) |
| 396-405 | REGISTRO DE LA CADENA | 0,1 K | núcleo (plantilla + regla «contaminados no acreditan»; se queda) |
| 406-fin | Integración | 0,3 K | núcleo |

### 1.4 `efe-clasificador` — 1,7 K + rúbrica 21,2 K

| Archivo · líneas | Sección | Tokens | Clase |
|---|---|---:|---|
| `SKILL.md` entero | cómo usarlo, reglas que no se negocian, sin XI, archivo de referencia | 1,7 K | núcleo |
| rúbrica 1-4 | título | 0,0 K | núcleo |
| rúbrica 5-57 | Changelog v1.9 · v1.8 · v1.7 · v1.6 · v1.5 · v1.4 | 2,3 K | **historial** |
| rúbrica 59-665 | instrucciones, bloques A-H, F1-F5, G, H, tabla de puntuación, implicaciones, alertas, diagnóstico | 17,9 K | mixto: ≈ 9,3 K son blockquotes con la regla, su «Fundamento» y el caso; se quedan (separarlos es reescribir) |
| rúbrica 666-fin | APÉNDICE: registro de casos de validación (Caso 1 Estudiantes, Caso 2 Junior) | 0,9 K | **historial** |

### 1.5 `efe-dashboard/SKILL.md` — 7,2 K (el encargo NO lo carga)

| Líneas | Sección | Tokens | Clase |
|---|---|---:|---|
| 1-7 | frontmatter y título | 0,2 K | núcleo |
| 8-43 | notas v1.12 · v1.11 · v1.10 · v1.9 · v1.8 · v1.7 | 2,0 K | **historial** |
| 44-281 | Qué hace, fuente de verdad, PASO 0 a 7, coordinación con timeline | 3,9 K | núcleo |
| 282-311 | Notas finales, errores comunes, «Alertas de v1.7 — detalle» | 0,7 K | núcleo (la alerta con su caso de referencia) |
| 312-320 | Candidatos declarados y NO aplicados | 0,2 K | núcleo (se ejecutan y reportan como candidatos) |
| 321-fin | «Movido a otro skill en v1.6» y «Nota de actualización manual» | 0,2 K | historial |

### 1.6 `sad-analysis` — 15,0 K (+ referencias bajo demanda)

| Archivo · líneas | Sección | Tokens | Clase |
|---|---|---:|---|
| `SKILL.md` 1-7 | frontmatter y título | 0,2 K | núcleo |
| `SKILL.md` 8-35 | notas v4.4 · v4.3 · v4.2 · v4.1 · v4.0 | 1,6 K | **historial** |
| `SKILL.md` 36-fin | qué hace, glosario, insumos, leyes, pasos 0.5-6, auditorías, prohibiciones, cuándo consultar `references/` | 13,2 K | núcleo (mixto en 1.6 y 6-B, donde la regla trae su medición) |
| `references/ley_regresion_nivel.md` | vigente, «bajo demanda» | 4,0 K | núcleo bajo demanda |
| `references/casos_referencia.md`, `ley_marcador.md`, `ley_fe_perdida.md`, `motor_tension_favorito.md` | suspendidas o historia | 1,2 + 0,9 + 0,8 + 1,2 K | historial (ya dice «solo bajo demanda»: no se leen) |
| `scripts/audit_protocol.py` | suspendido | 5,6 K | no se lee |

### 1.7 Prompt de `docs/COWORK.md` («# PROMPT COWORK — SAD BATCH NOCTURNO v2.6» hasta «# PROMPT CORTO — "LLEGÓ EL ONCE"») — 17,4 K

| Líneas del bloque | Sección | Tokens | Clase |
|---|---|---:|---|
| 1-6 | título y cómo pegarlo | 0,0 K | — |
| 7-30 | 0. Rol y modo | 0,3 K | núcleo |
| 31-49 | 1. La app es el destino (credenciales) | 0,2 K | núcleo; el encargo manda ignorar las credenciales |
| 50-116 | 2. Qué partidos | 1,0 K | núcleo de la corrida, **no del subagente** (el encargo lo manda ignorar) |
| 117-122 | 3. Una sesión limpia | 0,1 K | núcleo |
| 123-269 | 4. Qué escribir: EFE, DT, F1, fuentes, T.54, calendario, brecha, matchup | 2,5 K | mixto (fechas e incidencias que motivaron cada regla; repite reglas de la rúbrica v1.7/v1.8) |
| 270-459 | 4. Reventón, espina, otras burbujas | 3,4 K | mixto (tablas de calibración y backtests citados) |
| 460-574 | 4. Lectura SAD, caja, TDE, goles acotados, sancionados, nivel del motor, cadena, pronóstico, «NO escribas» | 2,7 K | mixto |
| 575-776 | 5. Documentos (dtp 2,8 K, matriz, tde, timeline, ensayo) | 3,6 K | mixto (el bloque dtp repite DTP v1.2-v1.6 con fechas) |
| 777-849 | 6. El problema del once | 1,2 K | núcleo |
| 850-1017 | 7. Depositar y leer el recibo | 2,5 K | núcleo |
| 1018-1065 | 8. Cuando llegue el once | 0,6 K | núcleo de otra etapa (no del depósito) |
| 1066-1084 | 9-10. Reglas duras, al terminar | 0,2 K | núcleo |

El prompt no tiene changelog: su historia son incisos («pasó el 16/09»,
«incidencia 860», «Auditoría del 15/10») metidos en la regla. Se estiman en
≈ 1,5-2 K; además repite reglas de los skills (≈ 3 K). **No se toca en la
fase 1**: el encargo dice que el prompt «manda en todo» y recortarlo es otra
revisión (§3.4).

---

## 2. Reglas operativas que hoy viven SOLO en un historial

Método: se leyeron enteros los changelogs de los cinco skills y las notas de
versión de `INDICE_IE.md`; cada regla con verbo de mandato («se declara»,
«obligatorio», «prohibido», «no se…») se buscó con `grep` en el núcleo que
queda (el `SKILL.md` sin historial + las referencias que manda leer). La
mayoría ya está integrada: los changelogs del TDE desde la v0.1.17, y los del
DTP, EFE y sad-analysis desde la v1.4 / v1.6 / v4.0, citan la disciplina o la
sección donde quedó escrita. Lo que **no** está:

### 2.1 `teorema-del-echado` (10)

| # | Regla (cita corta) | Vive en | Destino en el núcleo | ¿Ya está? |
|---|---|---|---|---|
| T1 | **Disciplina 34** — «con dos o más indicadores abiertos, la caja publica el rango conjunto (mínimo y máximo combinatorios de todos los abiertos a la vez), no un rango por indicador» | changelog v0.1.13 | disciplina 32 e `INDICE_IE.md` § «Caja de sensibilidad» | **No.** La disciplina 32 y la caja hablan de «un indicador» |
| T2 | **Disciplina 35** — «sin XI confirmado, `F1` se declara `sin dato` y entra en la caja conjunta; no se puntúa con nivel de dato C sobre listas de probables» | changelog v0.1.13 | disciplinas 28/30 y fila `F1` de `INDICE_IE.md` | **No, y choca** con la disciplina 55 (v0.1.19: «un once probable es nivel de dato C; `F1` y `C2` solo pasan a nivel A con el once oficial»), que admite `F1` en C. El EFE y el prompt (§6) citan «Disciplina 35» con otro sentido (el bloque F del EFE). **Decide el usuario** cuál vale antes de copiar |
| T3 | **Disciplina 36** — «cuando `F1 = 0` por rotación de ≥ 3 titulares, el output declara que el descuento físico se está pagando en coordinación y que el módulo no lo representa» | changelog v0.1.14 | fila `F1` de `INDICE_IE.md` / PASO 2 | **No** |
| T4 | **Disciplina 37** — «la ventana modal se declara para la vía de mayor riesgo compuesto; a menos de 5 puntos, las dos ventanas y se puntúan por separado» | changelog v0.1.14 | PASO 3 | **No como regla**; el núcleo la CITA («mismo criterio que la disciplina 37», `INDICE_IE.md`, doble ventana SOB). **Vigencia en duda**: el riesgo compuesto está suspendido desde la v0.1.20. Decide el usuario: copiar reescrita sobre el ISE/IE o declararla caída |
| T5 | **Disciplina 38** — «el sesgo tardío es una propiedad de la serie: su corrección solo entra como cambio de regla autorizado al alcanzar el umbral, nunca como ajuste de una fila» | changelog v0.1.14 | PASO 3 (ventana) | **No** |
| T6 | **Disciplina 39** — «todo caso `RETRO` declara su traza `PRE`: los indicadores que no habrían sido puntuables antes del partido y con qué valor entraron» | changelog v0.1.15 | disciplina 2 / 19 | **No.** Importa en el modo `reventones` de la corrida, que trabaja hacia atrás |
| T7 | «"rival poco goleador" no basta para bajar `P(gol)` del default, y **el default no se baja nunca con ejecutor de penales designado con conversión documentada**» | changelog v0.1.14 | `INDICE_IE.md` § «P(gol \| fractura)» (default alto) | **No.** Vigencia a confirmar: la tabla de `P(gol | fractura)` sigue en el núcleo, las de `P(echada)` y `P(SOB)` están suspendidas |
| T8 | «`F3` no admite puntuación alta por ausencia de evidencia: sin datos de impacto de banco en la temporada, `F3` es `sin dato` y entra en la caja conjunta» | changelog v0.1.14 | fila `F3` de `INDICE_IE.md` | **Parcial**: solo dentro de la tabla de FECHA-1 (PASO 0-bis); fuera de la fecha 1 no está |
| T9 | «Apartarse de una declaración previa solo es admisible hacia más medición, nunca hacia menos» | changelog v0.1.10 | disciplina 27 | **No** (la 27 dice cómo se escribe la condición de abandono, no esto) |
| T10 | El chequeo de integridad del registro: «antes de cualquier corrida que lea el registro se compara el sha256 … si difieren manda la del repo y se declara» | «Dónde vive el registro canónico» (sale con el historial) | PASO 0, punto 4 | **Sí, pero en la sección que se mueve**: hay que dejar 2 líneas en el PASO 0 |

Para que no se copie por error: **derogada** la «corrección de localía
obligatoria antes de comparar μ» (v0.1.4), que la disciplina 47 y la FICHA
MÍNIMA prohíben desde la v0.1.18. Y quedan como **candidatos**, no reglas, los
de cada changelog (`F1` en U, `F2 × F4`, `C3` por magnitud, ventana `90+`,
encadenamiento de vías, `SOB2` heredado de un M2 RETRO, dispersión entre
casas, «doble golpe», defecto por quien persigue): ya figuran como candidatos
en las disciplinas o en `INDICE_IE.md`.

Nota de forma: la propia línea 554 («Desfase de documentación declarado») dice
que las disciplinas 34-39 «no se reconstruyen de memoria (disciplina 11)».
Copiarlas **literalmente** del changelog no es reconstruirlas de memoria, pero
es dar de alta seis disciplinas que el skill dejó afuera a propósito: por eso
T1-T6 van al usuario aunque solo sean un copiar y pegar.

### 2.2 `diagnostico-tactico` (1)

| # | Regla | Vive en | Destino | ¿Ya está? |
|---|---|---|---|---|
| P1 | «El once probable es nivel de dato C aunque converjan cuatro fuentes: la convergencia entre redacciones es copia, no observación independiente; si el análisis se cierra antes del once oficial, el documento declara la **ventana de confirmación pendiente** y ofrece rehacer el mapa» | v1.3, punto 2 | M1 (junto a «XI de referencia obligatorio») | **Parcial**: está «dos capas cuando el once es nivel C» (v1.4) y DTP-REHACER, pero no que la convergencia no sube el nivel ni la ventana de confirmación (sí está en el TDE, disciplina 55) |

Todo lo demás de v1.1-v1.7 está en M1-M6 con su marca de versión (verificado
punto por punto: dos ramas, vía entera por rama, banco por rol, ejecutor de
penales en lista de dos, pregunta 6 con sede, costo de rearmar, posesión por
perfil, grid del once, pelota parada con materia, media distancia, frecuencia
de MECANISMO-ABIERTO, dos capas, umbral ≥ 2 errores del arquero, `no
probado`, posesión condicional, minutos compartidos).

### 2.3 `efe-clasificador` (0)

Cada punto de los changelogs v1.4-v1.9 está en el cuerpo de la rúbrica o en
el `SKILL.md` con su marca *(v1.x)*: recambio probable y arquero suplente en
la F1, rama «once alternativo» de los dos lados, rodaje en la categoría, arco
del día, jerarquía de fuentes en las dos direcciones y con fecha, F3 por zona
con quién cubre, D3 por condición y cuántos casos, EJE-DEBUTANTE con el grid,
T.54 en los dos lados con `dt.desde`, 15 partidos del suplente, caja al
matchup H, confianza un escalón, brecha y empate técnico, barrido fijo de F5,
B5 sin evidencia, B6 con el once oficial, GK-FALLA-ACTIVA, G-SORPRESA. Los de
v1.4/v1.5 son altas de indicadores que existen en sus bloques.

### 2.4 `efe-dashboard` (2)

| # | Regla | Vive en | Destino | ¿Ya está? |
|---|---|---|---|---|
| D1 | «`F5` mira la nómina completa, no el once probable: **un suplente con impacto documentado desde el banco en la temporada en curso es factor X por derecho propio**, se proyecte titular o no» | v1.8, punto 1 | PASO 1 (F5) de este skill; conviene también como quinta lista del «barrido fijo de F5» de la rúbrica | **No**: el barrido fijo (rúbrica v1.6) recorre regresos, altas, titulares sin fila y habilitación; el suplente de impacto no está |
| D2 | «El once probable es nivel de dato C … los indicadores que se apoyan en el once (`B1`, `B5`, todo el bloque F) heredan ese nivel; antes del once oficial la banda de protocolos declara la ventana de confirmación pendiente y ofrece el recomputo» | v1.8, punto 2 | PASO 0-bis | **No** (en el EFE solo para T.54 de ≤ 2 partidos) |

### 2.5 `sad-analysis` (0)

Los puntos de v4.0-v4.4 están en sus pasos (la nota de versión los cita:
6-A, 6-B, 1.6, 1.7, 3.5, 6-C, 6-E, Ley 4 por zona, combinada de favoritos,
calibración de la cohorte que se lee y no se aplica, perfiles DC alineados).

### 2.6 Prompt de COWORK (no aplica)

No tiene historial separado: sus incisos de fecha van pegados a la regla y
la regla está escrita. No hay regla que viva solo en una anécdota.

---

## 3. La propuesta

### 3.1 Qué pasa a `references/HISTORIAL.md` de cada skill

Se lee **solo al revisar el skill** (fase D, modo mantenimiento, una
propuesta nueva), nunca al analizar. Se mueve tal cual, sin editar:

| Skill | Pasa a `references/HISTORIAL.md` | Tokens |
|---|---|---:|
| teorema-del-echado | `SKILL.md` 16-294 (notas v0.1.25 … v0.1.1), 8-15 (registro canónico, entero) y 658-755 (EL REGISTRO: esquema, `pre_rubrica`, trampa del recomputo, numeraciones ausentes, filtro de frecuencia, TDE-026); `INDICE_IE.md` 3-27 (sus notas de versión) | 26,5 K + 1,9 K |
| diagnostico-tactico | `SKILL.md` 8-95 (notas v1.7 … v1.1, con sus candidatos y «Queda fuera») | 4,2 K |
| efe-clasificador | rúbrica 5-57 (Changelog v1.9 … v1.4) y 666-fin (APÉNDICE de casos de validación) | 3,2 K |
| efe-dashboard | `SKILL.md` 8-43 (notas v1.12 … v1.7) y 321-fin (Movido a otro skill, Nota de actualización manual) | 2,1 K |
| sad-analysis | `SKILL.md` 8-35 (notas v4.4 … v4.0) | 1,6 K |

**No se mueve en la fase 1** (mixto: la regla y su caso en el mismo párrafo):
las disciplinas del TDE, M1/M2 del DTP, los blockquotes de la rúbrica y los
pasos 1.6/6-B de sad-analysis. Separarlos es reescribir reglas, y eso es una
revisión de skill con su propia propuesta (§3.4).

### 3.2 Qué queda arriba de cada `SKILL.md`

Una línea, debajo del título, igual en los cinco (cambiando versión y ruta):

> Versión vigente: **v0.1.25 (01.11.2026)**. Las notas de cada versión, los
> casos que motivaron cada regla y el esquema del registro están en
> `references/HISTORIAL.md`: **no hace falta leerlo para analizar un
> partido**; se lee al revisar el skill.

Más, solo en el TDE: en el **PASO 0, punto 4**, dos líneas con lo operativo
de «Dónde vive el registro canónico»: «la copia de `assets/casos/` es una
instantánea; antes de usarla se compara su sha256 con el fijado en
`scripts/calibrar-tde.py` y, si difieren, manda la del repo y se dice».
Y en la nota de la línea 554, cambiar «descritas en los changelogs de v0.1.14
y v0.1.15» por «… (`references/HISTORIAL.md`, v0.1.13-v0.1.15)».

En la rúbrica del EFE, el apéndice deja una línea: «Casos de validación 1 y 2:
`references/HISTORIAL.md`».

### 3.3 Lo que hay que copiar al núcleo ANTES de mover

Sin decisión del usuario (no cambian nada, solo dejan escrito lo que hoy
manda desde el historial):

1. **T3** (disciplina 36) en la fila `F1` de `INDICE_IE.md`, como nota.
2. **T5** (disciplina 38) en el PASO 3, debajo de «Orden correcto desde v0.1.1».
3. **T6** (disciplina 39) como punto de la disciplina 19.
4. **T8** en la fila `F3` de `INDICE_IE.md` («fuera de la fecha 1 también»).
5. **T9** como última frase de la disciplina 27.
6. **T10** en el PASO 0 (§3.2).
7. **P1** en el M1 del DTP, una frase junto a «XI de referencia obligatorio».
8. **D1** en el PASO 1 de efe-dashboard (F5) y, si el usuario lo acepta, como
   quinta lista del barrido fijo de F5 de la rúbrica.
9. **D2** en el PASO 0-bis de efe-dashboard.

Con decisión del usuario (§2.1): **T1** (disciplina 34: copiarla como 34 en
la lista numerada y en la caja), **T2** (disciplina 35 contra la 55: cuál
vale), **T4** (disciplina 37: reescrita sin riesgo compuesto o declarada
caída) y **T7** (`P(gol)` y el ejecutor de penales: vigente o caída con la
suspensión de la v0.1.20). Hasta que decida, la propuesta es **copiarlas
literales en un bloque «Disciplinas 34-39 (texto de v0.1.13-v0.1.15, sin
reconstruir)»** al final de la Disciplina, con la marca de duda: mover el
changelog sin eso las dejaría citadas («disciplina 35», «disciplina 37») y sin
texto en ningún archivo que se lea.

Costo de lo copiado: ≈ 1,0 K en el TDE, 0,1 K en el DTP, 0,2 K en el dashboard
(ya sumado en la tabla del §0).

### 3.4 Lo que la corrida manda leer y podría no leerse siempre

El encargo de `.claude/skills/corrida-sad/SKILL.md` («Encargo de un partido»)
carga cuatro skills con la herramienta Skill (que trae el `SKILL.md` entero) y
el prompt de COWORK. Las referencias las piden los skills:

- **`registro.csv` del TDE (16,5 K).** El PASO 0 dice «leer antes de estimar»
  y la regla de procedencia de `F3` dice «obligatorio revisar
  `assets/casos/registro.csv`». Pero el mismo skill declara la copia
  empaquetada «obsoleta» salvo chequeo de sha256, el prompt dice «tu memoria
  es la app» (antecedentes) y el parte no escribe CSV. **Duda para el usuario**:
  que el encargo diga «del registro, solo buscá con Grep el nombre de los dos
  equipos para `F3`; no lo leas entero». No toca la regla de `F3` (sigue
  revisándose), solo cómo se lee: −16,5 K cuando hoy se lee entero.
- **Rúbrica del EFE (21,2 K)**: «siempre, antes de puntuar». Se queda.
- **`INDICE_IE`, `TIPOLOGIA`, `DETECCION_DATOS`**: el PASO 0 las pide siempre;
  se quedan (núcleo).
- **`ley_regresion_nivel.md` (4,0 K)** y las suspendidas de sad-analysis: ya
  dicen «solo bajo demanda». Bien así.
- **`efe-dashboard`**: el encargo no lo carga, pero el prompt lo lista en
  «Skills disponibles» y la matriz cita su v2.0. Si un subagente lo carga
  igual, son 7,2 K (5,2 K después). Conviene que el encargo diga si se carga o
  no; hoy queda al criterio del subagente.
- **Prompt de COWORK**: el encargo hace leer el punto 2 (1,0 K) y el 8 (0,6 K)
  para después ignorarlos. Si el encargo diera los números de línea del punto
  3 al 7 y del 9 al 10, serían −1,6 K sin tocar el prompt.

Fase 2 posible, **no propuesta acá** (cada una es una revisión con su
propuesta): separar regla y caso en las disciplinas del TDE (17,2 K, la regla
en negrita es ≈ 3,5 K: el techo de ahorro está en ≈ 8-10 K), en los
blockquotes de la rúbrica (≈ 9,3 K mixtos) y sacar del prompt las reglas que
repiten los skills (≈ 3 K) y las anécdotas (≈ 1,5-2 K).

---

## 4. Ahorro estimado

Supuestos del pedido: ~50 pasos por subagente; lectura de caché a 0,20 USD/M
tokens en cada paso; escritura de caché a 8 USD/M, una vez por subagente.

| | Tokens de skills + prompt | Lectura (50 pasos) | Escritura (1 vez) | Total por parte |
|---|---:|---:|---:|---:|
| Hoy | 142,8 K | 1,43 USD | 1,14 USD | **2,57 USD** |
| Fase 1 | 106,7 K | 1,07 USD | 0,85 USD | **1,92 USD** |
| **Ahorro** | **36,1 K** | **0,36 USD** | **0,29 USD** | **≈ 0,65 USD por parte** |

- Con 20 partes por día, ≈ 13 USD por día.
- Cota conservadora: los skills se cargan después de los primeros GET (paso
  ~8-10), así que pesan en ~40 pasos y no en 50: ahorro ≈ 0,58 USD por parte.
- Si hoy el subagente lee `registro.csv` entero y se adopta la duda del §3.4:
  +16,5 K → +0,30 USD de ahorro adicional por parte (≈ 0,95 USD en total).
- El modo `rehacer` carga DTP y sad-analysis: −5,6 K por subagente
  (≈ 0,10 USD). El modo `veredictos` y `reventones` cargan los mismos skills
  que `partes`: mismo ahorro.

---

## 5. Riesgos y cómo se verifica

**Riesgos**

1. **Perder una regla al mover.** Es el riesgo principal y por eso el §2 la
   lista entera. Las 13 reglas se copian (o se deciden) antes de mover.
2. **Referencias huérfanas.** El núcleo cita disciplinas que solo tienen
   texto en el changelog (la 37 en `INDICE_IE.md`, la 35 en el EFE y en el
   prompt). Sin el bloque del §3.3 quedarían citadas y sin texto.
3. **Contradicciones que hoy están tapadas.** Al mover salen a la luz: la
   disciplina 35 contra la 55; «la lectura que se comunica es el riesgo
   compuesto» (LA TESIS) contra la suspensión de la v0.1.20; la tabla
   «Mapeo de IE a probabilidad» de `INDICE_IE.md` sin la marca de suspendida;
   «Eres … EFE v1.7» en la rúbrica v1.9 y «aplicando EFE v1.6» en el
   dashboard. **No se arreglan en esta propuesta** (sería cambiar reglas);
   van como hallazgos para la próxima revisión de cada skill.
4. **La cuenta y el repo se separan.** El cambio vale cuando se sube el zip a
   la cuenta; la copia de `docs/skills/` es la foto. `docs/skills/README.md`
   ya está viejo (dice TDE v0.1.22 y la copia tiene v0.1.25).
5. **El mantenimiento y las revisiones de skill necesitan la historia.** Las
   propuestas `docs/revisiones/*_propuesta.md` y la fase D leen los changelogs
   para no repetir candidatos: tienen que apuntar a `references/HISTORIAL.md`
   (una línea en el skill de la corrida, modo mantenimiento, y en
   `docs/DEUDA.md`).
6. **Una regla nueva se escribe en el historial y no en el núcleo.** Pasó con
   las disciplinas 34-39. La guardia del punto siguiente lo impide.

**Verificación** (un test en CI, como pide `docs/FALLAS.md`):

- `scripts/nucleo_reglas.json`: por regla, `id` (T1…D2 más las ya
  integradas que se quieran blindar), `skill`, archivo de núcleo y una
  **frase ancla** literal.
- `backend/test_nucleo_skills.py` (sumarlo a CI y a la lista de
  `test_arquitectura`):
  1. cada ancla aparece en el `SKILL.md` o en una referencia que su PASO 0
     manda leer, **no** solo en `references/HISTORIAL.md`;
  2. ningún `SKILL.md` (ni `INDICE_IE.md`, ni la rúbrica) tiene bloques de
     versión (`^> \*\*v\d`, `^> \*\*Changelog`) más allá de la línea que
     apunta al historial;
  3. cada skill tiene su `references/HISTORIAL.md` y la línea que lo nombra;
  4. toda «disciplina N» citada en el núcleo tiene su texto en la lista
     numerada o en el bloque de huecos declarados;
  5. tope de tokens por skill (caracteres / 4) con margen del 10 % sobre lo
     medido después de la fase 1, para que el núcleo no vuelva a crecer con
     historia sin que nadie lo note.
- Antes de mover, una pasada de control a mano: `diff` entre el
  `SKILL.md` viejo y la concatenación `SKILL.md` nuevo + `HISTORIAL.md`
  (tiene que dar solo las líneas agregadas del §3.2/§3.3), y el mismo `grep`
  de este documento sobre el núcleo nuevo.

## Dudas para el usuario

1. **Disciplina 35 contra 55** (T2): ¿`F1` sin XI confirmado es `sin dato`
   o nivel C?
2. **Disciplinas 34, 37 y la regla de `P(gol)`** (T1, T4, T7): ¿se copian
   literales al núcleo como vigentes, reescritas sin el riesgo compuesto, o
   se declaran caídas con la v0.1.20?
3. **`registro.csv` en la corrida**: ¿el encargo puede pedir solo un Grep por
   equipo para `F3` en vez de leerlo entero?
4. ¿**D1** entra también al barrido fijo de F5 de la rúbrica (es otro skill)?
5. ¿El encargo debe decir explícitamente si carga o no `efe-dashboard`?
