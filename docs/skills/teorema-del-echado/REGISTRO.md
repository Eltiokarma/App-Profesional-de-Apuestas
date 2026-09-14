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
reexpresar. Por eso la condición (c) del alta del semáforo no se prueba con
«tiene recomputo» sino con:

```
en_esquema_vigente = esquema_P == '6ind' or IE_recomputado_esquema6 no vacío
```

Las 19 celdas vacías sí se leen limpio: **10** son `6ind` (nacieron en el
esquema vigente, no hace falta) y **9** son 001-009 (falta hacerlo). Esas nueve
no están atrasadas, están **bloqueadas**: reexpresarlas exige decidir fila por
fila si se puntuaron sobre 4 o sobre 5 indicadores, y eso es cambio de fondo.

El único positivo ciego computable, TDE-005, está en ese grupo bloqueado. Por eso
**(c) da falso y va a seguir dándolo aunque aparezcan cuatro positivos más.**
