# El registro de casos del TDE · dónde vive y qué tiene roto

## Dónde vive el canónico

**En el repo**: `docs/skills/teorema-del-echado/assets/casos/registro.csv`.

La copia que viaja dentro del paquete del skill (`/mnt/skills/plugins/…`, montada
solo-lectura) es una **instantánea de empaquetado y debe considerarse obsoleta**.
No es un descuido que se pueda arreglar reempaquetando una vez: el registro
cambia **por partido** —dos filas por fecha— y el skill se reempaqueta **por
versión**. Meter un dato de cadencia diaria dentro de un artefacto de cadencia
semanal es la desincronización garantizada, y ya ocurrió tres veces:

1. **v0.1.7** — «resincronización de artefactos»: SKILL.md en v0.1.6,
   CALIBRACION.md en v0.1.5 y el CSV en 17 filas.
2. **TDE-035 a 042** — ocho filas perdidas entre v0.1.16 y v0.1.18 sin que
   ninguna versión lo notara.
3. **La canonización de categorías** — el repo la tiene, el paquete no.

**El estado vigente se identifica por sha256, no por conteo de filas ni por
fecha.** Ninguna de las tres se habría detectado contando filas: la primera y la
tercera no cambian el conteo. `scripts/calibrar-tde.py` verifica el sha en cada
corrida y avisa si el archivo se movió sin que nadie lo declarara.

## Numeraciones ausentes

Una numeración ausente no es un hueco salvo que alguien la declarara **en su
momento**; todo lo demás es pérdida. Ninguna de estas mueve el N de positivos,
y por dos vías independientes: por modo (COND y RETRO quedan fuera del filtro) y
por contenido.

| ID | Etiqueta | Qué se sabe |
|---|---|---|
| TDE-010 | `hueco declarado` | declarado en v0.1.3 como hueco de numeración |
| TDE-019, 020 | `perdida` | cerrados en v0.1.6 (LigaPro Ecuador F24). De 019 sale el primer `ISE 10` fallido; de 020 nace `acierto_no_testeado`. v0.1.7 declara que no están en disco |
| TDE-027, 028 | `perdida` | Atlético Grau y Comerciantes Unidos, Liga 1 F5. Declarados en sesión, nunca llegaron al CSV (v0.1.10) |
| TDE-035, 036 | `perdida` | FC Cajamarca 1-3 Atlético Grau, F6 Clausura Perú. Alta explícita en v0.1.14. Modo `COND`, excluidas del Brier. 035 cierra como falso positivo; 036 como `acierto_no_testeado` |
| TDE-037, 038 | `sin rastro` | no aparecen en ningún archivo del skill. No consta que se hayan escrito |
| TDE-039, 040 | `perdida` | citados en INDICE_IE v0.1.15. Modo RETRO |
| TDE-041, 042 | `perdida` | Hull City 2-0 Manchester United, F1 Premier 2026-27, v0.1.16. Modo RETRO |

**Las filas perdidas NO se reconstruyen desde el changelog.** El changelog trae
IE y hallazgos, así que fabricar una fila que parezca válida es fácil — y sería
inútil además de contaminante: una fila reescrita con el resultado **y con los
hallazgos que el propio caso produjo** no es `ciega` ni `post_resultado`. No
tiene clase válida, y etiquetada con honestidad quedaría excluida de toda
métrica de frecuencia el mismo día que entrara.

## `IE_recomputado_esquema6` mezcla tres poblaciones

De las 16 filas con valor:

| | n | cuáles |
|---|---|---|
| reexpresión real (esquema viejo, valor distinto) | **2** | TDE-011 (4.5 → 4.2), TDE-012 (6.2 → 6.9) |
| **copia literal del `IE`** sobre filas ya `6ind` | **11** | 013, 014, 016, 021, 022, 023, 024, 025, 026, 033, 034 |
| otra cosa | **3** | TDE-017 y 018 traen el recomputo de **v0.1.5**, no un cambio de esquema. **TDE-015 no coincide con nada**: IE 5.5, esq6 5.3, v015 5.5 — pendiente de resolver |

Consecuencia para cualquier consumidor: **la regla sobre las celdas vacías vale,
la inversa no.** Una celda llena en fila `6ind` no significa que hiciera falta
reexpresar, así que «tiene recomputo» nunca fue una prueba válida.

## `estado_recomputo_esq6` · la columna que pone eso en el dato

Esa distinción vivía en un script. Si alguien calculaba la frecuencia con otra
herramienta, la perdía — el mismo modo de falla que venimos corrigiendo toda la
sesión. Ahora es una columna, la 51, puesta **justo después** de la que
describe para que se lean juntas. No se tocó ninguna celda preexistente.

| valor | n | qué significa |
|---|---|---|
| `hecho` | 15 | la celda tiene un valor trazable: reexpresión real (011, 012), copia correcta sobre fila ya `6ind`, o el recomputo de v0.1.5 (017, 018) |
| `hecho_sin_procedencia` | 1 | **TDE-015**: hay un 5.3 que no reproduce ni el `IE` (5.5) ni el recomputo de v0.1.5 (5.5). Nadie sabe de dónde sale |
| `no_requiere` | 10 | nació en el esquema vigente: 029-032, 043-048 |
| `bloqueado` | 3 | **TDE-007, 008, 009**. Reexpresables en principio, pero no consta con qué esquema se puntuaron. No están atrasadas: falta una decisión de fondo |
| `pre_rubrica` | 6 | **TDE-001…006**. **No reexpresables**: sus bloques no son promedios posibles de indicadores 0/0.5/1 con ningún denominador, así que se puntuaron con escala continua y no hay `P1a…P4` que convertir |

**Sobre TDE-015 se decidió etiquetar y no aislar, porque no contamina.** Se
comprobó contra cada métrica: es `modo_evaluacion = COND` **y** `modo = RETRO`,
o sea que queda doblemente fuera del filtro de frecuencia, y no es positivo, así
que tampoco entra en (c) —que solo mira positivos—. El valor raro no participa
de ninguna cuenta. Queda con nombre propio para que quien lo herede sepa que ahí
hay algo sin resolver, en vez de creerle al número.

**La condición (c) se lee de esta columna, y distingue dos cosas que parecen
iguales y no lo son:**

- Un positivo **`bloqueado`** sí bloquea la (c). Se puede arreglar: falta una
  decisión, no información.
- Un positivo **`pre_rubrica`** no bloquea nada. **Sale del conteo de (a).** No
  se puede arreglar ni con todo el trabajo del mundo, porque la información no
  se perdió: nunca existió.

Esa distinción es lo que impide que la (c) se vuelva un candado. Tal como
estaba redactada —«todos los positivos en el esquema vigente»— bastaba TDE-005
para tumbarla, y TDE-005 es inexpresable. Una condición de calidad que no se
puede satisfacer deja de ser una condición.

Hoy: **0 positivos que cuenten**. El único del registro es `pre_rubrica`. El
semáforo se levantará con cinco positivos ciegos nuevos, en el esquema vigente,
al menos dos fuera de la banda 3-5.


## Las nueve bloqueadas: qué consta y qué no

Desbloquear TDE-001…009 exige saber con qué esquema se puntuó cada fila. La
vara es **evidencia documental** —un texto del skill que lo diga— nunca una
inferencia desde el valor del `IE`.

**TDE-006 → `4ind`, con cita.** `references/INDICE_IE.md:190` (nota «Por qué P1
se dividió», v0.1.1): *«En TDE-006, FC Cajamarca fue puntuado 1 por la segunda
cláusula»* — y esa segunda cláusula es la redacción **anterior** a la división
de P1. El CSV declara `IE = 7.6`, que es el valor pre-división. La fila
declarada está en el esquema de 4.

**TDE-001…005 y 007…009 → no consta.** Ningún archivo dice con qué esquema se
puntuaron.

### CUIDADO: el 6.7 de TDE-006 NO es la reexpresión al esquema 6

La misma nota sigue: *«Con P1a = 0 y P1b = 0, el bloque P de ese caso baja de
0.75 a 0.38 y el IE de 7.6 a 6.7»*. Es tentador volcar ese 6.7 en
`IE_recomputado_esquema6` y dar la fila por resuelta. **Sería un error, y
exactamente el que esta columna ya sufrió dos veces.**

La cronología lo decide:

| versión | cambio | indicadores de P |
|---|---|---|
| v0.1.1 | P1 se divide en P1a y P1b | **5** |
| v0.1.3 | entra P1c (de la rama v0.1.2-B) | **6** |

El 6.7 sale de la nota de **v0.1.1**, así que es la reexpresión al esquema de
**cinco**, no al de seis: le falta puntuar `P1c` (coste institucional
acumulado). Meterlo en la columna del esquema 6 repetiría el caso de TDE-017 y
TDE-018, que llevan el recomputo de v0.1.5 en una columna que dice otra cosa.

**TDE-006 sigue `bloqueado`**, y desbloquearlo tampoco movería nada: `se_echo =
no`, no es positivo, y la condición (c) solo mira positivos.

### La asimetría que conviene tener presente

**El único positivo ciego computable es TDE-005, y de él no consta nada.** Las
demás se pueden acotar por cronología —v0.1.1 declara que TDE-001…006 ya
existían cuando se dividió P1— pero **TDE-007, 008 y 009 entraron en la misma
versión que introdujo la división**, y nada dice si se puntuaron antes o
después de aplicarla. Para esas tres no hay ni argumento indirecto.

Esa cronología es **inferencia, no evidencia**, y no se escribe en el dato.


## TDE-005 no es reexpresable, y no por falta de información

La pregunta «¿se puntuó sobre 4 o sobre 5 indicadores?» **está mal formulada
para esa fila**. La aritmética lo decide sin necesidad de ningún documento.

Cada indicador vale 0, 0.5 o 1, así que la suma de k indicadores es un múltiplo
de 0.5 y el bloque solo puede valer `(m/2)/k`. Con eso, el bloque P de cada
fila vieja:

| fila | P | ¿formable? |
|---|---|---|
| TDE-001 | 0.40 | sí (k=5) |
| TDE-002 | 0.70 | sí (k=5) |
| TDE-003 | 0.85 | **imposible con cualquier denominador** |
| TDE-004 | 0.55 | **imposible** |
| **TDE-005** | **0.55** | **imposible** |
| TDE-006 | 0.75 | sí (k=2, 4 o 6) |
| TDE-007 | 0.25 | sí |
| TDE-008 | 0.63 | sí (k=4) |
| TDE-009 | 0.75 | sí |

Y no es solo P. **TDE-001 a 006 tienen bloques `F`, `C` o `S` que tampoco son
formables** (F se promedia sobre 4 → múltiplos de 0.125, y ahí hay 0.70, 0.80,
0.60, 0.55; C sobre 3 → múltiplos de 1/6, y hay 0.15, 0.30, 0.35, 0.85). De
TDE-007 en adelante todas las filas son formables.

**Conclusión: las seis primeras se puntuaron con una escala continua por bloque,
no promediando una rúbrica de indicadores.** No se perdió la información de con
qué esquema se puntuó P: **no hubo esquema de P**. No hay `P1a…P4` que
reexpresar, y por eso TDE-005 no es reexpresable al esquema de 6 ni hoy ni
nunca.

### Lo que esto NO autoriza

Volver a puntuar el partido hoy. TDE-005 está cerrado con `se_echo = si`:
puntuar `P1b` (coste percibido de perder), `P2` (D3, respuesta a la adversidad)
o `P4` sabiendo que el equipo se echó **es hindsight**, y la fila resultante
sería `post_resultado` — excluida de toda métrica el día que entrara. Sería
producir trabajo para obtener una fila que ninguna métrica puede mirar, que es
exactamente el argumento por el que no se reconstruyen las perdidas.

Tampoco lo autoriza traer el partido de la base: el dato que falta **no es del
partido**, es de cómo alguien puntuó en agosto de 2026. Ninguna fuente externa
lo contiene.

### La salida real es de rúbrica, no de datos

La condición (c) dice hoy *«todos los positivos expresados en el esquema
vigente»*. Con una fila estructuralmente inexpresable, eso equivale a **nunca**.
La salida honesta es cambiar la condición, no el dato:

> (c) todos los positivos **computables** expresados en el esquema vigente. Un
> positivo anterior a la rúbrica de indicadores no se reexpresa ni se
> reconstruye: se marca `pre_rubrica` y **queda fuera del conteo de (a)**, que
> pasa a exigir N ≥ 5 positivos ciegos **en el esquema vigente**.

Así el semáforo puede levantarse algún día con cinco positivos limpios, en vez
de quedar bloqueado para siempre por una fila de 2026 que nadie puede arreglar.
Es decisión del autor del skill.
