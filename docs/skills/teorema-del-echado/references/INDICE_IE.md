# Índice de Echada (IE) — indicadores y rúbrica

> **v0.1.18 (30.08.2026).** Alta del **tope del bloque C**: con `C3 = 1` el bloque no promedia por debajo de **0.60**. Alta de la clase **`no probado`** en `C1`, para el bloque que da estructural en el checklist pero nunca fue puesto a prueba. Alta del **`CHEQUEO DE RELEVANCIA DEL MODULO`** antes de derivar la ventana. `mu_partido` **no se corrige por localia a mano** en ningun caso. El perfil de posesion se declara **condicional al marcador**. Candidato declarado y NO aplicado: **dispersion entre casas**, cuatro campos registrados sin umbral, revision con 20 filas. **Ningun peso tocado, ningun indicador anadido.**

> **v0.1.16 (22.08.2026).** Alta del **`PROTOCOLO FECHA-1`**: `F1`, `F3` y `C3` se declaran automaticamente `sin dato` en el partido inaugural de un torneo, y la caja de sensibilidad pasa a obligatoria. Alta de la **`FICHA MINIMA DEL MOTOR`**: lista de campos verificable en el paso cero, porque `mu esperado` no es `mu_partido` y confundirlos es puntuar `P1a` con la cantidad equivocada. **`P(gol | sobreexposicion)` pasa a publicarse en sus dos versiones** cuando la regla de interaccion entre vias esta activa. Candidato declarado y NO aplicado: **`SOB2` heredado de un M2 contaminado** se declara con nivel de dato C. Segundo caso del registro donde la caja **cruza la banda**, por causa distinta al primero (TDE-042: calendario; TDE-032: cambio de entrenador). **Ningun peso tocado, ningun indicador anadido.**

> **v0.1.15 (22.08.2026).** Regla nueva de **doble ventana `SOB`** cuando la obligación de arranque y el gol en contra activan juntas. Dos candidatos declarados y NO aplicados: **`F2 × F4`** (el coste de altitud/viaje se atenúa con `F4 = 0`: el bloque bajo no paga la altura como el que presiona — TDE-040) y **`C3` desdoblado por magnitud de la ventaja** (la rúbrica solo nombra "ventajas de un gol"; una ventaja doble es otro objeto — TDE-040 defendió 2-0 durante 44'). **Segundo caso de la regla de interacción entre vías** (TDE-039, tras TDE-016), sin coeficiente por ser RETRO. Alta de la **disciplina 39**: todo RETRO declara qué indicadores no eran puntuables en PRE. **Ningún peso tocado, ningún indicador añadido.**

> **v0.1.12 (16.08.2026).** Candidato declarado y NO aplicado: **desdoblar la disciplina 16 por marcador al momento de la expulsión** — roja yendo empatado o ganando anula el ISE, roja yendo perdiendo lo **agrava**. Hueco de rúbrica nuevo: la **pérdida del organizador y ejecutor de pelota parada en los primeros minutos** no tiene representación en ninguna capa. `S1` acertó el indicador y falló el mecanismo: su redacción cubre faltas y corte táctico y **no cubre la conducta violenta**. Primer error de ventana cero desde TDE-001, **declinado** por la disciplina 24. Bandera `ARQUERO-NUEVO` activada y **sin testear**. **Ningún peso tocado, ningún indicador añadido.**
>
> **v0.1.11 (15.08.2026).** La regla de XI no confirmado se extiende al **cambio de entrenador en los siete días previos**: fuerza `F1` y `C2` a `sin dato`. Alta de la bandera **`ARQUERO-NUEVO`** como agravante declarado de `P(fractura | echada)`, sin coeficiente. La **caja de sensibilidad pasa a ser salida obligatoria** cuando algún indicador se declara `sin dato` (2 de 2 a favor). Dos candidatos declarados y NO aplicados: la contradicción interna de `SOB1` y la posible saturación del ISE. **Ningún peso tocado, ningún indicador añadido.**
>
> **v0.1.10 (15.08.2026).** Se corrige la forma de escribir la condición de `rama_abandonada`: se declara **por vía y nombrando la premisa**, no por evento del partido. Alta de la regla de **XI no confirmado**: ante levantamiento de inhibición, habilitación masiva de fichas o cierre de mercado en la semana previa, `F1` y `C2` se declaran `sin dato`. Se separa `gol_del_partido` de `gol_del_tramo_final` en el cierre. Primera vindicación de bajar `P(gol | fractura)` del default alto con justificación explícita. **Ningún peso tocado, ningún indicador añadido.**
>
> **v0.1.8 (11.08.2026).** Se declara el **hueco de la ventana `90+`**: las seis ventanas terminan en el 90 y en TDE-023/024 los dos goles del tramo cayeron en el añadido. Candidato de ventana `90+` con duración endógena **declarado y NO aplicado**. Sesgo arbitral **descartado como variable** por razones de calibración, no de criterio. **Ningún peso tocado, ningún indicador añadido.**
>
> **v0.1.7 (10.08.2026).** Chequeo de calibración completo. La advertencia de sobreestimación se extiende de la banda 5-7 a **toda la escala** de `P(echada)`. `P(gol | fractura)` arranca en la banda alta por defecto. **F2 pasa a ser dato obligatorio del motor**: sin salida de Regresión al Nivel, el bloque F se declara `sin dato`. Candidato de reescalado del mapeo declarado y no aplicado; candidato de `C1` despriorizado. **Ningún peso tocado**, ahora porque el grupo de echadas observadas ciegas tiene un solo miembro.
>
> **v0.1.5 (10.08.2026).** Se cierra el ítem abierto de P1a con **dos modos de evaluación**, `PRE` y `COND`. Se elimina la cláusula "o ya obtenida" de la escala pre-partido y se formaliza el IE condicional de ventana. Alta de la bandera `VENTAJA-INESPERADA`, de la regla de procedencia del dato de F2 y de la regla de interacción entre vías en `P(gol | sobreexposición)`. Hipótesis nueva sobre el driver de la banda 5-7 y candidato de reescalado de C1, declarado y no aplicado. **Ningún peso tocado: N = 6 declarados, el umbral es 8.**
>
> **v0.1.4 (10.08.2026).** Se cierra la definición de "favorito" para P1a con la Ley de la Regresión al Nivel del motor: el input es `μ_partido`, nunca el gap. Se añaden tres prohibiciones al bloque P derivadas del backtest del motor. **Ningún peso tocado.**
>
> **v0.1.3 (09.08.2026).** Fusión de las dos ramas de v0.1.2. Del parche de rúbrica: tres compuertas correctoras, desdoble de P4, disciplina de puntuación de P1a por número, advertencia de banda 5–7 y declaración de dos candidatos no ratificados. De la rama de segunda vía: el **ISE**, la regla `n/a` de S3 y el indicador P1c. **Los pesos del IE siguen sin cambiar.**
>
> **v0.1.1 (09.08.2026).** Correcciones de rúbrica derivadas del cierre de TDE-005 y TDE-006. **Los pesos NO cambiaron** — con N = 2 casos declarados estamos por debajo del primer umbral de revisión de `CALIBRACION.md`. Lo que cambió: P1 se dividió en P1a y P1b, F3 recibió una regla de procedencia del dato, y la ventana modal se desacopló del bloque dominante.

```
IE = [ F×3 + C×2 + P×2 + S×1.5 ] / 8.5 × 10
```

Cada bloque se puntúa de **0 a 1** como fracción de riesgo. El score del bloque es el promedio de sus indicadores, salvo las reglas especiales indicadas.

Cada indicador se puntúa **0 (bajo) / 0.5 (medio) / 1 (alto)**.

---

## PROTOCOLO FECHA-1 — dominio del modulo *(NUEVO v0.1.16)*

Se activa cuando el equipo evaluado **no ha jugado ningun partido oficial** del torneo analizado. No es una excepcion de un caso: es la delimitacion de donde el modulo puede puntuar.

| Indicador | Redaccion original | Por que falla en fecha 1 | Tratamiento |
|-----------|--------------------|--------------------------|-------------|
| `F1` | "Rotacion en los ultimos 3 partidos" | Los ultimos 3 son amistosos | **`sin dato`** |
| `F3` | "Impacto documentado **en la temporada en curso**" | No hay temporada en curso | **`sin dato`** |
| `C3` | "Sostuvo >=2 ventajas de un gol **esta temporada**" | Idem | **`sin dato`** |

**Reglas de aplicacion:**

1. **Caja de sensibilidad obligatoria.** Publicar el IE con los tres en 0 y con los tres en 1.
2. Con tres `sin dato` en bloques de peso x3 y x2, **es esperable que la caja cruce una banda**. Si cruza, el output dice que la lectura depende de datos que no existen todavia, y **no** publica un punto medio.
3. **Proxy de temporada anterior:** admisible **solo** si no hubo cambio de categoria, declarado como proxy y con nivel de dato C. Con `R-KT.2` activo en el equipo, **prohibido**.
4. **`F2`** se toma del fixture con nivel de dato B si el motor no trae la tarjeta de proximos.
5. El output declara explicitamente: *"el bloque de mayor peso del modulo esta incompleto por dominio, no por falta de investigacion"*.

> **De donde sale.** TDE-042, Manchester United en la fecha 1 de la Premier League 2026-27: `F1`, `F3`, `C3` y `P1a` sin dato, IE entre **3.87 y 6.62**, o sea entre "riesgo dependiente del marcador" y la banda declarada sobreestimada. Es el segundo caso del registro donde la caja cruza la banda y el primero donde la causa es el calendario y no un evento del club.

---

## FICHA MINIMA DEL MOTOR *(NUEVO v0.1.16)*

Verificar en el paso cero, no al puntuar.

| Campo requerido | Alimenta | Si falta |
|-----------------|----------|----------|
| `mu_partido` de los dos equipos | `P1a` (unico input admitido) | `P1a` = `sin dato` + caja |
| `nivel` de los dos equipos | Recomputo de `mu_partido` con la formula | Sin recomputo posible |
| Dias de descanso | `F2` | Fixture, nivel B |
| Proximo rival con etiqueta duro/blando | `F2` | Fixture, nivel B |
| Fecha del snapshot | Verificar contaminacion de la tira de forma | Declarar no verificable |
| Localia modelada de la liga | Correccion antes de comparar `mu` | Usar +0.382 y declararlo |

> **`mu esperado` no es `mu_partido`.** El primero se calcula contra los rivales reales de los ultimos 5 partidos y sirve para el gap. El segundo se calcula contra el rival de **este** partido, con localia, y es el unico que puntua `P1a`. Una captura recortada que muestre solo el primero **no es una salida del motor** a efectos de este modulo.

---

## LAS TRES COMPUERTAS · aplicar siempre, antes de promediar

No son opcionales y **su activación se declara en el output aunque no cambie el número**. Se aplican después de puntuar los indicadores y antes de calcular los scores de bloque.

### Compuerta 1 — P1a sobre el bloque P

```
Si P1a = 0  →  score del bloque P = min( promedio(P1a..P4), 0.5 )
```

**Razón.** Sin algo que proteger no hay echada psicológica. P1b, P1c, P2, P3 y P4 describen *cómo se administra* un resultado, no *si existe uno* que administrar. Sin la compuerta, un equipo que necesita ganar y va a ir al frente los 90 minutos puede acumular un bloque P alto por contexto y crisis, y eso no es riesgo de echada.

### Compuerta 2 — C1 sobre S2

```
Si C1 = 0  o  C1 = 0.5  →  S2 = min( S2, 0.5 )
```

**Razón.** Bajar el punto de referencia por plan, con estructura entrenada, no es echarse. Meter un central dentro de un bloque ensayado es ejecutar el plan. **S2 solo puede puntuar 1 cuando el repliegue NO está documentado**, o sea con `C1 = 1`.

### Compuerta 3 — desdoble de P4

| P4 | Criterio |
|----|----------|
| 1 | Crisis que **toca al plantel**: impagos, amenazas, conflicto interno, salida conflictiva del DT en la semana |
| 0.5 | Crisis institucional que **no llega al vestuario en cancha**: sanción de tribuna, puertas cerradas, quita administrativa de puntos, público hostil, presión mediática |
| 0 | Ambiente sano |

**Razón.** La redacción anterior metía en el mismo casillero un impago de tres meses y una tribuna silbando. Lo primero desarma un vestuario; lo segundo lo incomoda.

**Interacción con la regla `n/a` de S3.** Las compuertas 2 y 3 y la regla `n/a` de S3 **se apilan** sobre el mismo perfil de equipo: bloque bajo entrenado, sin presión alta, con ruido institucional que no llega al plantel. En TDE-013 las tres operaron juntas y bajaron el IE de 3.4 a 3.0. Eso es correcto y no es doble conteo: cada una corrige un indicador distinto.

---

## BLOQUE F — Carga física · peso ×3

Es la causa más común y la menos reconocida. Presionar alto cuesta muchísimo; cuando los volantes ya no llegan al segundo balón, la línea de fondo retrocede para no dejar la espalda descubierta.

| # | Indicador | Bajo (0) | Medio (0.5) | Alto (1) |
|---|-----------|----------|-------------|----------|
| F1 | Rotación en los últimos 3 partidos | 3+ titulares rotados con nivel titularizable | 1–2 rotados | 0 rotados, mismos once nombres |
| F2 | Descanso, viaje y calendario | 6+ días, sin viaje exigente, próximo partido accesible | 4–5 días o viaje con cambio de altitud | ≤3 días, o altura/calor extremo, o próximo partido de altísima exigencia |
| F3 | Profundidad de banco *(hereda B5 del EFE)* | ≥2 recambios con impacto documentado | 1 recambio de impacto | Banco sin alternativas que cambien el trámite |
| F4 | Costo energético del modelo | Bloque medio, salida directa | Presión selectiva | Presión alta sostenida y/o construcción obligada desde el arquero |

**Regla especial F**: si F1 = 1 **y** F3 = 1 (sin rotación y sin banco), el bloque F no puede puntuar menos de 0.75 — es la combinación que produce la echada física clásica del minuto 60.

**Regla de procedencia de F3** *(v0.1.1)*: F3 se puntúa **solo** con goles, asistencias o cambios de trámite documentados desde el banco **en la temporada en curso**. Nunca con la posición en la tabla, el presupuesto del club, la condición de recién ascendido ni la reputación del plantel. Antes de puntuar F3 es obligatorio revisar `assets/casos/registro.csv`: si un caso previo ya documentó impacto de suplentes de ese equipo, ese dato manda.

> **Por qué existe esta regla.** En TDE-006, FC Cajamarca fue puntuado F3 = 1 por ser colista y recién ascendido, cuando el propio registro ya contenía TDE-003, donde Barcos entró desde el banco y marcó tres goles entre el 78' y el 90+2'. El banco es lo mejor que tiene ese equipo. La rúbrica se aplicó con reputación en lugar de evidencia.

---

## BLOQUE C — Control del repliegue · peso ×2

Este bloque no mide si el equipo va a retroceder, mide si va a hacerlo ordenado. **Es la fuente principal de `P(fractura | echada)`.**

| # | Indicador | Bajo (0) | Medio (0.5) | Alto (1) |
|---|-----------|----------|-------------|----------|
| C1 | ¿Tiene bloque bajo entrenado y documentado? | Sí, repliegue ensayado con ≥8 partidos de rodaje **y probado bajo presión real** | Estructura existe pero con poco rodaje, **o estructural pero `no probado`** | No, repliegue improvisado |
| C2 | Coordinación línea–volantes | Pivote que acompaña el descenso de la línea de forma documentada | Depende del intérprete | Sin evidencia, o línea defensiva armada en el último mercado |
| C3 | Disciplina en cierres previos | Sostuvo ≥2 ventajas de un gol esta temporada | Una sostenida y una perdida | No sostuvo ninguna |

> **TOPE DEL BLOQUE C *(NUEVO v0.1.18, obligatorio)*.** Si `C3 = 1`, entonces `C >= 0.60` sin importar `C1` y `C2`.
>
> ```
> C = max( (C1 + C2 + C3) / 3 , 0.60 )   si C3 = 1
> C = (C1 + C2 + C3) / 3                 en cualquier otro caso
> ```
>
> **Razon.** `C1` y `C2` miden **insumos** —repliegue ensayado, coordinacion de la linea— y `C3` mide **resultado**: si el equipo cerro ventajas o no. Un promedio simple deja que dos indicadores de insumo entierren al unico que ya observo el fenomeno. En TDE-045 el bloque promedio 0.333 con `C3 = 1`, se estimo `P(fractura | echada)` en 28% y el equipo perdio la ventaja de un gol en cuatro minutos. Es el mismo patron que el clasificador estructural corrigio en su dia poniendole tope al bloque D cuando la respuesta a la adversidad esta en negativo.
>
> **Es un tope de lectura, no un peso.** La formula del IE y la ponderacion ×2 del bloque C no cambian, asi que la disciplina 22 —los umbrales se cuentan en positivos— sigue intacta. Cuando el tope opere, el output publica **el promedio aritmetico al lado del valor topeado** para que la fila siga siendo comparable con las anteriores.

> **CLASE `no probado` en `C1` *(NUEVO v0.1.18)*.** El checklist de clasificacion del bloque vive en el skill `diagnostico-tactico` y mide cinco insumos. Su **sexta pregunta**, alta de v1.2, es: *¿este bloque sostuvo el resultado alguna vez estando empatado o en desventaja contra un rival obligado a atacar?* Si la respuesta es no —todas las vallas invictas salieron de partidos sin presion real— el bloque se clasifica **`no probado`**, `C1` puntua **0.5** en lugar de 0, y **la alerta de degradacion NO se suprime**. En TDE-045 el bloque dio cinco de cinco del lado estructural, `C1` se puntuo 0, se declaro vida util 80-90 y concedio tres goles.
>
> **Corolario sobre precedentes.** Un caso anterior del mismo equipo en la misma cancha **no es precedente si tampoco hubo presion**. TDE-001 se uso para estimar la fractura de TDE-045 en el extremo bajo de la banda; era un 0-0 contra un rival que no iba a buscar.

> **Hipótesis sobre C1 y la banda 5-7** *(v0.1.5)*. Los siete casos de la banda 5-7 sin echada del registro —TDE-006, TDE-011, TDE-012, TDE-015 y los tres declarados nuevos— **comparten `C1 = 1`**. Hasta v0.1.4 se atribuía la sobreestimación al peso del bloque C; la hipótesis nueva es que el problema está un nivel más abajo, en la rúbrica de C1: exige "repliegue ensayado con ≥8 partidos de rodaje" para puntuar 0, y eso deja en 1 a casi cualquier equipo sin bloque bajo entrenado, o sea a la mayoría de los equipos. Un indicador que puntúa alto en el 80% de los casos no discrimina, solo desplaza la escala hacia arriba.
>
> **Candidato declarado y NO aplicado**: reescalar C1 con un nivel intermedio, 0.5 para el equipo que no tiene bloque bajo ensayado pero sí una línea de fondo estable con ≥8 partidos de rodaje conjunto. Distingue al que no ensayó el repliegue del que además no se conoce entre sí. Revisión a N = 8; aplicarlo ahora movería todos los IE del registro sin evidencia.

**Mapeo sugerido a P(fractura | echada)**, a ajustar con el registro:

| C promedio | P(fractura \| echada) |
|-----------|----------------------|
| 0.00–0.25 | 15–25% |
| 0.26–0.50 | 25–40% |
| 0.51–0.75 | 40–55% |
| 0.76–1.00 | 55–70% |

**Agravante declarado**: si la bandera `VENTAJA-INESPERADA` está activa, subir la estimación dentro de la banda que corresponda y decirlo en el output. Sin coeficiente: es criterio declarado, no fórmula.

**Agravante declarado `ARQUERO-NUEVO`** *(v0.1.11)*: si el arquero que va a jugar **no es el titular habitual** —transferencia, lesión, sanción o apartamiento disciplinario—, subir la estimación dentro de la banda y declararlo. **Sin coeficiente.**

> **Por qué existe y por qué no vive dentro de `C2`.** `C2` mide coordinación línea–volantes y está redactado sobre el pivote y la línea de fondo. El arquero rompe el mismo mecanismo por otra puerta: los automatismos de comunicación con la línea tardan meses en construirse y no hay rotación natural que los reparta, porque es la única posición del campo sin distribución de carga. En TDE-031 el capitán y arquero titular de Guaraní fue apartado del plantel por conflicto interno cuatro días antes y debutó un suplente sin recorrido en la categoría; hubo que subir la estimación dentro de la banda 25-40% y explicarlo en prosa, que es el síntoma exacto de un hueco de rúbrica. El clasificador de estabilidad ya captura esto dos veces —en la continuidad de portería y en el multiplicador de impacto por fecha—; este módulo no lo capturaba ninguna.
>
> **Nota de alcance.** La bandera se activa por el hecho observable de que el arquero es otro, no por el motivo. El apartamiento disciplinario es el caso más agudo porque llega acompañado de la ruptura de vestuario que lo produjo, pero eso entra por `P4`, no por acá. No contar el mismo evento dos veces en el mismo bloque.

---

## BLOQUE P — Psicológico · peso ×2

Miedo a perder lo que ya se tiene. El caso de máximo riesgo es el favorito que va 1-0: deja de jugar para ganar y empieza a jugar para no perder, que son dos cosas distintas.

| # | Indicador | Bajo (0) | Medio (0.5) | Alto (1) |
|---|-----------|----------|-------------|----------|
| P1a | Rol de protector del resultado *(dos modos, ver más abajo)* | Necesita ganar y va a ir al frente los 90 minutos | Escenario abierto | Modo `PRE`: favorito con ventaja esperada · Modo `COND`: ventaja ya obtenida |
| P1b | Coste percibido de perder **este partido** | Bajo — sin expectativa social de ganar este partido concreto | Medio | Alto — perder este partido se lee como fracaso |
| P1c | Coste institucional acumulado *(v0.1.2-B)* | Sin riesgo de descenso ni de cese del DT | Uno de los dos presente | Riesgo de descenso **y** de cese, o crisis de permanencia declarada |
| P2 | D3 del EFE (respuesta a adversidad) | ✅ documentada | 🔶 parcial | ❌ sin respuesta |
| P3 | Relevancia asimétrica | El partido es uno más del calendario | Importa | Obligado a ganar, o con un tramo posterior brutal que invita a administrar |
| P4 | Contexto emocional y extra-cancha *(desdoblado, ver compuerta 3)* | Ambiente sano | Crisis institucional que no llega al vestuario: público hostil, presión mediática, sanción de tribuna, quita administrativa | Crisis que toca al plantel: impagos, amenazas, conflicto interno, salida conflictiva del DT en la semana |

> **Por qué P1 se dividió** *(v0.1.1)*. La redacción anterior metía en el mismo casillero de riesgo alto dos situaciones que empíricamente van en direcciones contrarias: *"favorito con ventaja esperada, **o** equipo que espera recibir el primer gol"*. En TDE-006, FC Cajamarca fue puntuado 1 por la segunda cláusula, recibió el primer gol al minuto 10 de visitante y respondió metiendo cuatro. **Recibir un gol temprano siendo el que no tiene nada que perder libera, no repliega.** El mecanismo de la echada psicológica es miedo a perder lo que ya se tiene; un equipo que va perdiendo no tiene nada que proteger. Con P1a = 0 y P1b = 0, el bloque P de ese caso baja de 0.75 a 0.38 y el IE de 7.6 a 6.7.

> **Nunca puntuar P1a = 1 sobre un equipo que va perdiendo o que no es favorito.** Si el equipo evaluado es el que probablemente reciba el primer gol y además no carga expectativa de ganar, ambos indicadores van a 0 y el riesgo psicológico entra, si entra, por P4.

> **Por qué se separó P1c.** En TDE-013, Wanderers llegaba 6° en la Tabla Anual y a la vez en zona de descenso por promedios: coste institucional altísimo, coste de perder ese partido concreto bajo, porque era visitante y nadie le exigía ganar. La rúbrica anterior colapsaba las dos cosas en P1b. **Van en direcciones opuestas**: el coste del partido empuja a proteger un resultado (echada); el coste institucional acumulado empuja a ir a buscarlo (sobreexposición). Por eso P1c alimenta también SOB1.

### Disciplina de puntuación de P1a — el número, no el relato

P1a se puntúa con el dato disponible, no con la narrativa periodística sobre el equipo. **Si en la sesión hay una salida de Regresión al Nivel (Ley §5) de `sad-analysis`, ese es el número que manda**: el µ del partido y el gap diferencial deciden si el equipo tiene un resultado esperado que administrar. Un equipo "en crisis" puede ser favorito por µ, y entonces P1a **no** es 0.

**Error registrado.** En TDE-012 se puntuó `P1a = 0` por narrativa cuando el módulo daba al equipo como favorito (µ 1.55 vs 1.23, gap ajustado +0.35). Con `P1a = 0.5` el IE sube de 6.2 a 6.5 y la compuerta 1 ni se activa.

**Dos trampas del dato**, documentadas en TDE-013/014:
1. **Contaminación post-partido.** La forma de los últimos 5 de una salida de Regresión al Nivel puede incluir el partido que se está evaluando. Verificar la fecha del snapshot antes de usar el gap.
2. **El gap diferencial y el diferencial de µ pueden apuntar en direcciones opuestas.** En TDE-014 el gap diferencial ajustado era +0.72 y el diferencial de µ del partido −0.16. Decir explícitamente cuál de los dos se usó.
3. **La localía de µ está subestimada en Sudamérica.** La ventaja real ronda +0.5 a +0.7 y µ la modela en +0.38. Corregir el µ del local hacia arriba antes de decidir quién es favorito.

### Definición de "favorito" para P1a — cerrada con el motor *(v0.1.4)*

El ítem quedó abierto un turno y lo resuelve la Ley de la Regresión al Nivel tal como está implementada en el repo. **No era una pregunta de calibración, era de definición**, y el motor la contesta.

```
favorito = el equipo con mayor μ_partido, corregido por localía real de la liga

μ_partido = μ(nivel propio, nivel del rival REAL, localía real)
          = 1.241 + 0.334·nivel − 0.357·nivel_rival + 0.382·localía
```

**Regla de input, inviolable: P1a se puntúa con `μ_partido`. Nunca con el gap ni con el gap diferencial.** Son cantidades distintas que responden preguntas distintas: `μ_partido` dice quién tiene más puntos esperados en este partido, el `gap` dice cuánto se desvía cada equipo de su propia expectativa genérica. **Pueden apuntar en direcciones opuestas sin que ninguno esté mal.** Fue exactamente lo que pasó en TDE-014: gap diferencial ajustado +0.72 contra diferencial de μ −0.16. El número correcto era μ, y daba 0.5.

**Corrección obligatoria de localía antes de comparar.** μ modela la localía global en +0.382 y la real en Sudamérica va de **+0.48 a +0.73** (Perú +0.73). Sumar la diferencia al μ del local antes de decidir quién es favorito. En **Argentina**, además, nivel propio y de rival van ponderados a la mitad (~±0.15): un diferencial de μ chico ahí es compresión de liga, no paridad real, y no debe leerse como escenario abierto.

**Escala de P1a**, con el margen de μ ya corregido:

| P1a | Condición |
|-----|-----------|
| 1 | Tiene el μ_partido más alto **y** el margen supera 0.30 |
| 0.5 | Los μ_partido están dentro de 0.30 — escenario abierto |
| 0 | Tiene el μ_partido más bajo por más de 0.30, o necesita ganar y va a ir al frente los 90 |

> **El umbral de 0.30 es prestado, no validado.** Sale de los umbrales del propio gap de la Ley (`0.3–0.5` leve), que están calibrados para otra magnitud. Se adopta porque es preferible un umbral explícito y trazable a criterio libre del analista, pero **hay que decir en el output que se usó y cuál sería el IE con el corte en otro lado** si el caso queda cerca del borde.

**Consecuencia sobre el registro.** Recomputando TDE-012 con esta regla: Danubio μ 1.55 contra 1.23 es +0.32, y corrigiendo la localía uruguaya el margen sube a ~+0.44/+0.64. Supera 0.30 → **P1a = 1**, bloque P 0.83, **IE 6.9** (el parche había fijado 0.5 e IE 6.5). Misma banda, distinto número. Queda como recomputación en `IE_recomputado_esquema6`; **la fila declarada no se sobreescribe.**

### Los dos modos de evaluación de P1a *(v0.1.5)*

El ítem quedó abierto un turno y **no era de calibración, era de definición**, exactamente como el de v0.1.4. La escala de v0.1.4 puntúa por `μ_partido`; la tabla de indicadores decía "favorito con ventaja esperada **o ya obtenida**". Las dos cláusulas no caben en un casillero, y en TDE-015 se vio por qué: un visitante con `μ_partido` 0.84 contra 1.94 que iba ganando 2-1 desde el minuto 65 puntuaba **0 por μ y 1 por ventaja obtenida**, y el escenario que describe la segunda es precisamente la echada clásica — el equipo chico aguantando. Puntuado por μ, el módulo le asignaba riesgo psicológico bajo a los 25 minutos más peligrosos del partido.

**Modo `PRE` — pre-partido. Es el canónico y el único que acredita validación.**

```
favorito = el equipo con mayor μ_partido, corregido por localía real de la liga
```

| P1a | Condición |
|-----|-----------|
| 1 | Tiene el `μ_partido` más alto **y** el margen supera 0.30 |
| 0.5 | Los `μ_partido` están dentro de 0.30 — escenario abierto |
| 0 | Tiene el `μ_partido` más bajo por más de 0.30, o necesita ganar y va a ir al frente los 90 |

**Se elimina de esta escala la cláusula "o ya obtenida".** Antes del partido no hay ventaja obtenida, y mantener las dos vías en el mismo casillero era la contradicción.

**Modo `COND` — IE condicional de ventana. No acredita validación.**

Se usa cuando se pide el riesgo de un tramo con el marcador ya definido. Obliga a declarar `modo_evaluacion = COND` y `estado_marcador` en el registro, y vale lo mismo que un `RETRO`: fija rúbrica, no acredita aciertos (disciplina 13 del SKILL).

| P1a | Condición |
|-----|-----------|
| 1 | Tiene ventaja de un gol o más y el resultado le sirve |
| 0.5 | Empate que le alcanza para su objetivo |
| 0 | Va perdiendo, o empata y necesita ganar |

**Bandera `VENTAJA-INESPERADA`.** Si el equipo con ventaja obtenida tiene además el `μ_partido` más bajo por más de 0.30, anotarla. **No mueve P1a**, que ya está en 1: entra como **agravante declarado de `P(fractura | echada)`**, porque el equipo está protegiendo algo que no esperaba tener y sin estructura entrenada para administrarlo. Se combina de forma natural con `C1 = 1`. **Sin coeficiente numérico**: con un solo caso (TDE-015) poner un número sería inventar precisión.

**Consecuencia sobre el registro.** TDE-015 se declaró con P1a = 1 e IE 5.5 usando la cláusula de ventaja obtenida; la reconciliación estricta de v0.1.4 lo bajó a P1a = 0 e IE 5.3 activando la compuerta 1. Con el modo `COND` de v0.1.5 vuelve a P1a = 1 e **IE 5.5**, con la bandera `VENTAJA-INESPERADA` activa y la compuerta 1 sin activarse. El 5.3 queda registrado como lo que era: el síntoma numérico del hueco de definición, no una corrección. Las tres cifras conviven en columnas distintas y **la fila declarada no se sobreescribe**.

### F2 es dato del motor o no es dato *(v0.1.7)*

Van **3 de 3**: cada vez que la salida de Regresión al Nivel apareció después de una estimación propia de F2, la corrigió. TDE-017 de 0.5 a 0 (y salió de la banda 5-7), TDE-018 de 0 a 0.5, TDE-021 de 0 a 0.5 (IE de 6.3 a 6.8). Cero aciertos en tres intentos sobre un indicador del bloque de peso ×3.

**Sin salida del motor en la sesión, el bloque F se declara `sin dato`** y el IE se emite señalando que su bloque de mayor peso está incompleto. No se estima a ojo: un número inventado en un bloque ×3 finge una precisión que el registro ya midió como inexistente.

### Regla de procedencia del dato de F2 *(v0.1.5)*

Los días de descanso y la dureza del próximo rival **se toman de la salida del motor de Regresión al Nivel cuando existe** (campos de días y de μ del próximo partido, con su etiqueta duro o blando), no de estimación propia. Corrigió dos casos en la misma pasada: TDE-017 bajó F2 de 0.5 a 0 —6 días, sin viaje, próximo rival accesible— y con eso el IE cayó de 5.4 a 4.9 y **salió de la banda 5-7**; TDE-018 subió F2 de 0 a 0.5 porque el motor daba 5 días de descanso y no 6. Un indicador del bloque de peso ×3 no se estima a ojo si hay un número disponible.

### Prohibiciones que trae la Ley al bloque P

Tres cosas que el módulo **no** puede hacer con una salida de Regresión al Nivel, todas medidas en el backtest del motor (n = 8 816, sin fuga):

1. **No usar `tiende a mejorar` / `tiende a empeorar` como input de un partido.** Al partido siguiente el gap tiene **≤0.1 pts de residual**. Su horizonte es ~5 partidos. El TDE es un módulo de 15 minutos de un partido: la tendencia del gap no le sirve y meterla es prestarle autoridad que no tiene.
2. **Prohibido puntuar P hacia arriba porque un equipo esté sobre-rindiendo.** El único hallazgo que replicó en dos muestras es que el **sobre-rendimiento fuerte PERSISTE** (+0.11 ± 0.05). Es anti-reversión. La frase "está por encima de su nivel, le toca caerse en el tramo final" está medida como falsa.
3. **Verificar que la ventana de 5 partidos no sean amistosos.** Son el bucket más grande de la base del motor (12 783 fixtures) y alimentan forma y nivel como cualquier partido oficial. Un "bajón" de forma armado sobre pretemporada es ruido, y arrastraría a P1a y a F1 con él.

**Si la salida de Regresión dice "sin datos"** —menos de 5 partidos para el gap o menos de 20 para el nivel— P1a vuelve a criterio cualitativo y **hay que declararlo en el output**. No se estima un μ para tapar el hueco.

### Candidatos declarados y NO ratificados

Se documentan para que no se reinventen, y **no se aplican**:

| Candidato | Propuesta | Por qué no entra |
|-----------|-----------|------------------|
| Cuantificar P1a por diferencial de μ | ≥ +0.30 → 1 · −0.30 a +0.30 → 0.5 · ≤ −0.30 → 0 | **Input resuelto en v0.1.4**: es `μ_partido`, no el gap. El **umbral de 0.30 sigue sin validar** — está prestado de los umbrales del gap, que miden otra magnitud. Se aplica de forma provisional y se declara en el output. Revisión a N = 8 |
| F1 condicionado a F2 | No rotar con 6+ días de descanso y sin viaje es cohesión, no carga acumulada | Razonable y sin validar. Cambiaría el signo de F1 en un subconjunto de casos sin evidencia acumulada |
| Ventana `90+` con duración endógena *(v0.1.8)* | Séptima ventana estimada desde eventos contables (VAR, goles, cambios, atenciones), operando como **amplificador de la vía activa** y no como vía nueva | Un solo caso (TDE-023/024). Añadir una ventana desplaza las ventanas modales de todo el registro sobre un MAE ya sesgado tardío seis veces seguidas. Revisión cuando haya **≥3 casos con gol del tramo caído en el añadido** |

Si se usan como referencia en un análisis, **decirlo y dar también el número sin el candidato**.

**Regla especial P**: si P2 = 1 (D3 ❌) y el equipo va a recibir el primer gol con probabilidad alta, activar además `COLAPSO EN CASCADA` del EFE y anotar el vínculo. Nótese que esta regla opera por P2, no por P1 — la vulnerabilidad la aporta la ausencia de respuesta a la adversidad, no el hecho de ir perdiendo.

---

## BLOQUE S — Estructural del partido · peso ×1.5

| # | Indicador | Bajo (0) | Medio (0.5) | Alto (1) |
|---|-----------|----------|-------------|----------|
| S1 | Riesgo de inferioridad numérica | Sin antecedente disciplinario, pocas faltas | Faltas en zona media, amarillas sueltas | 15+ faltas por partido, jugadores al límite, corta con falta en zona propia |
| S2 | Cambios defensivos previsibles del DT *(ver compuerta 2)* | Cambia por cambios ofensivos | Depende del marcador | Patrón documentado de meter perfil defensivo y bajar el punto de referencia, **con `C1 = 1`** |
| S3 | ¿El rival puede superar su primera línea de presión? | No, rival sin salida limpia | Ocasionalmente | Sí, rival con hombres entre líneas y pase interior — mecanismo `ECHADA-SUP` |

> **`S1` no cubre la conducta violenta, y eso ya produjo un mecanismo errado** *(v0.1.12)*. Los tres niveles del indicador están redactados sobre **faltas, amarillas acumuladas y corte táctico en zona propia**: describen al defensor o al pivote que llega tarde bajo presión. En TDE-034 se puntuó `S1 = 1` con evidencia dura —tres expulsiones de Huracán en la temporada— y llegó la cuarta, así que el **indicador acertó**. Pero el agravante nombrado en el output fue un lateral improvisado con antecedente de roja, y la expulsión real fue de un **delantero por conducta violenta** a los 66 minutos. Es un mecanismo con otra distribución, otro perfil de jugador y otro minuto modal, y la rúbrica no lo distingue. **Se declara y no se parcha**: refuerza el candidato de `S1` subponderado en lugar de abrir un cuarto nivel con un caso.
>
> **Hueco de rúbrica declarado: la pérdida del organizador en los primeros minutos** *(v0.1.12)*. En TDE-034, Leonardo Gil —armador y ejecutor de pelota parada— salió sustituido al minuto **9**. No es expulsión, así que la disciplina 16 no lo alcanza; no es ausencia previa, así que el bloque F tampoco; y no es coordinación línea–volantes, así que `C2` queda corto. Reordena el partido igual, y hay que subir la estimación en prosa, que es el síntoma conocido de un hueco. Se declara sin coeficiente, igual que el hueco de la roja al arquero.

**Regla `n/a` de S3**: la pregunta presupone que el equipo evaluado **presiona alto**. Si su modelo es bloque medio o bajo por diseño —F4 = 0 y C1 = 0—, no hay primera línea de presión que superar: S3 se marca `n/a` y **se excluye del promedio de S**, que pasa a calcularse sobre S1 y S2. Puntuarlo 0.5 "por prudencia" le inventa riesgo a un equipo que no está corriendo ese riesgo, y fue lo que ocurrió en TDE-013.

---

## Ventana modal — regla de adelanto *(v0.1.1)*

La ventana modal **no se deriva del bloque dominante**. Ese acoplamiento producía un sesgo sistemático: con `F×3`, el bloque físico domina casi todos los IE, y la echada física es por definición del minuto 60-65, así que el módulo declaraba ventanas tardías incluso cuando el mecanismo real era otro.

Evidencia acumulada al 09.08.2026, sobre los cinco casos con echada observada:

| Caso | Ventana declarada | Ventana real | Error |
|---|---|---|---|
| TDE-001 | 45-60 | 45-60 (min 50) | 0 |
| TDE-002 | 45-60 | 0-15 (min 13) | 3 |
| TDE-003 | 75-90 | 60-75 (min 70) | 1 |
| TDE-004 | 75-90 | 60-75 (min 70) | 1 |
| TDE-005 | 75-90 | 15-30 (min 20) | 4 |

MAE ≈ 1.8 ventanas contra un objetivo de < 1, y el error es **siempre tardío, nunca temprano**.

Procedimiento corregido:

1. Elegir el **tipo modal** por mecanismo, no por peso de bloque.
2. Derivar la ventana del **tipo**, no del IE: `SUP` → 0-45 · `PSI` → la ventana inmediatamente posterior al evento que la dispara (gol, jugada polémica) · `FIS` → 60-75 · `VOL` → la ventana posterior al cambio defensivo esperado · `NUM` → instantánea al evento.
3. **Regla de adelanto por S3.** Si S3 = 1 (el rival puede superar la primera línea de presión con un pase), adelantar la ventana **dos ventanas** respecto de la que sugiere el bloque dominante y asignar `ECHADA-SUP` como tipo modal, salvo que P1a = 1, en cuyo caso el tipo es `ECHADA-PSI` y el adelanto es de una ventana.
4. Test de coherencia obligatorio, tomado de la ficha de `ECHADA-SUP`: **si la echada aparece antes del minuto 45, casi nunca es física.** Si el módulo declara una ventana temprana con tipo `FIS`, la asignación está mal.

**Hipótesis reformulada — S3 como condición habilitante.** TDE-007 registró un equipo con C1 = 1, F = 0.50 y 57 minutos por administrar a 3.400 msnm en su tercer partido en siete días que **no se echó**: el rival no podía salir jugando (S3 = 0) y nunca forzó el repliegue. TDE-013 aporta el caso simétrico: ahí el rival **sí** podía superar la primera línea, y el equipo evaluado tampoco se echó — porque no presionaba, así que no había nada que superar.

Redacción corregida: **S3 habilita la echada solo si el equipo evaluado presiona alto.** No es "el rival sabe salir jugando", es "el rival sabe salir jugando *contra la presión que este equipo ejerce*". Con tres casos (TDE-002 a favor, TDE-007 y TDE-013 en contra por vías distintas) la reformulación entra vía la regla `n/a`. Convertir S3 en gatillo formal con peso propio sigue **no implementado**: hace falta N ≥ 8 declarados.

## Mapeo de IE a probabilidad

| IE | P(echada) | Lectura |
|----|-----------|---------|
| 0–3 | 10–25% | Improbable. Si repliega, será por decisión y ordenado |
| 3–5 | 25–45% | Riesgo de tramo final dependiente del marcador |
| **5–7** | **45–70%** | **BANDA DECLARADA SOBREESTIMADA — ver advertencia** |
| 7–8.5 | 70–90% | Casi seguro. El análisis debe centrarse en la fractura, no en la echada |

Nunca reportar 0% ni 100%: el techo del módulo es 90% y el piso 10%.

### Advertencia de escala completa · obligatoria en el output *(v0.1.7)*

**La escala entera está declarada sobreestimada, no solo la banda 5-7.** Sobre los 9 casos ciegos y cerrados del registro: IE medio 5.04 contra 11.1% de echadas observadas, y Brier 0.247. El único caso que se echó tenía IE 4.6; el IE 7.6 no se echó. **En cualquier valor de IE hay que decir en el output que la escala sobreestima y apoyarse en el riesgo compuesto.** El candidato de recorte a la mitad está declarado y no aplicado.

### Advertencia de banda 5–7 · obligatoria en el output

Cuatro casos con `P(echada)` estimada ≥ 45% **no se echaron**: TDE-006, TDE-011, TDE-012 y TDE-015. Las compuertas recortan 0.3–0.4 de IE, que no alcanza para explicar la brecha. Hasta v0.1.4 el driver probable era el **peso relativo del bloque C**; desde v0.1.5 la hipótesis preferida es la **rúbrica de C1**, porque los cuatro casos la comparten en 1 (ver el bloque C).

Si el IE de un equipo cae entre 5 y 7:

1. **Decirlo explícitamente en el output.** La banda está sobreestimada y el lector tiene que saberlo.
2. **Apoyarse en el riesgo compuesto** `P(echada) × P(fractura|echada) × P(gol|fractura)`, nunca en `P(echada)` sola.
3. **No tocar los pesos.** Van 4 declarados y 2 cerrados; el primer umbral de revisión es N = 8.

## P(gol | fractura)

No sale del IE. Se estima desde la capacidad ofensiva del rival y las vías de gol del DTP:

| Perfil del rival | P(gol \| fractura) |
|------------------|--------------------|
| Sin referencia de área ni desequilibrante 1v1 | 25–35% |
| Ataque funcional, una vía clara | 40–50% |
| Referencia de área + balón parado + banco fresco | 50–65% |

> **Default alto** *(v0.1.7)*. Las tres fracturas observadas del registro (TDE-002, TDE-003, TDE-005) terminaron **todas** en gol, contra un 45-55% declarado. Con 3 de 3 y el signo unánime, **`P(gol | fractura)` arranca en la banda 50-65% y bajarla exige justificación explícita en el output**. La echada es menos frecuente de lo que el módulo creía y más letal cuando ocurre.

---

## La ventana que la rúbrica no cubre — hueco declarado *(v0.1.8)*

Las seis ventanas del módulo terminan en el 90. En **TDE-023/024** el partido tuvo doce minutos de añadido y **los dos goles del tramo final cayeron ahí**: 90+2 y 90+10, ambos de penal por revisión de VAR. La ventana modal declarada —75-90 en los dos equipos— no es ni acierto ni error, porque no existe el casillero.

**Obligación de output mientras el candidato no se aplique:** decir que la ventana modal **no incluye el tiempo añadido**, y en el cierre anotar si el gol del tramo cayó dentro o fuera de las seis ventanas.

**Sub-hipótesis del candidato, la parte con mecanismo.** El añadido no es exógeno: el equipo que administra lo produce. Pérdidas de tiempo en saques, cambios y atenciones alargan el partido, y el equipo termina **teniendo que sobrevivir la prolongación que él mismo generó**. Es observable, falsable y encaja en la ficha de `ECHADA-VOL`.

**Lo que este hueco NO habilita.** Codificar sesgo arbitral como variable del módulo. En TDE-023/024 el añadido perjudicó al que iba ganando, así que el signo tampoco acompaña; pero el motivo real es de calibración: un término de parcialidad que se asume en vez de medirse **absorbe todos los fallos del índice** y lo vuelve incalibrable — es la disciplina 9 con nombre nuevo. Test admisible si se abre la línea: añadido concedido e intervenciones de VAR a nivel árbitro, partido a partido, separado por local y visitante, contra la media de liga.

**Observación anotada, no medida.** Reportes de Liga MX con dos y tres goles en tiempo añadido. Si el fenómeno tiene densidad de liga, `90+` deja de ser un borde y pasa a ser un tramo con tasa propia. Hipótesis a testear con conteo de goles por minuto, no evidencia.

---

## ISE — Índice de Sobreexposición · la vía espejo

Mide el riesgo de conceder en el tramo final **por no replegar cuando correspondía**. Mismo síntoma observable que la echada, mecanismo opuesto. Tres indicadores, puntuados 0 / 0.5 / 1:

| # | Indicador | Bajo (0) | Medio (0.5) | Alto (1) |
|---|-----------|----------|-------------|----------|
| SOB1 | Obligación de ir a buscar el resultado | Le sirve el empate o va ganando | Prefiere ganar pero puede administrar | Necesita ganar sí o sí: objetivo en juego, presión de tribuna, o coste institucional acumulado alto (P1c = 1) |
| SOB2 | Seguro tras la pérdida *(hereda el rest defense del Bloque H / M2 del DTP)* | Pivote fijo por delante de los centrales, un lateral queda bajo | Depende del intérprete o del marcador | Sin volante de contención cuando los dos laterales suben; línea alta sin cobertura documentada |
| SOB3 | Capacidad de transición del rival | Rival sin velocidad ni banco fresco para contragolpear | Una vía de contra | Rival con contragolpe como plan A, banco de piernas frescas y referencia de área |

> **Contradicción interna de `SOB1`, declarada y NO resuelta** *(v0.1.11)*. El criterio de nivel alto incluye la cláusula *"o coste institucional acumulado alto (`P1c = 1`)"*, y esa cláusula choca con la disciplina 18, que manda puntuar el estado de objetivo con la tabla y no con el adjetivo. En TDE-032, Rubio Ñu tenía `P1c = 1` por riesgo de descenso más cese del DT en la misma semana, y a la vez era un visitante al que el empate le servía para cortar ocho partidos sin ganar: la cláusula lo empuja a 1, la tabla a 0. Se puntuó **0.5 declarando la tensión**, que es lo mejor que permite la redacción actual y es un parche.
>
> **Candidato declarado y NO aplicado**: mover la cláusula de `P1c` de criterio de nivel alto a **modificador** de `SOB1`. La razón es la misma que justificó separar `P1c` de `P1b` en el bloque P — el coste institucional acumulado y el coste de perder este partido concreto empujan en direcciones opuestas, y colapsarlos en un casillero fue el error que ya se corrigió una vez. No entra con un caso.

```
ISE = ( SOB1 + SOB2 + SOB3 ) / 3 × 10
```

Sin pesos diferenciados: con N = 0 casos declarados sobre esta vía, ponderar sería inventar precisión. **Deliberado.**

| ISE | P(sobreexposición) | Lectura |
|-----|--------------------|---------|
| 0–3 | 10–25% | El equipo no va a quedar partido buscando el gol |
| 3.1–5 | 25–45% | Riesgo real en el tramo 75-90 si sigue sin marcar |
| 5.1–7 | 45–70% | Va a comprar el riesgo. La contramedida es un pivote fijo, no más ataque |
| 7.1–10 | 70–90% | El gol en contra es el escenario modal del tramo final |

`P(gol | sobreexposición)` se estima desde SOB3 y las vías de gol del rival en el DTP, con la misma tabla que `P(gol | fractura)`.

**Regla de interacción entre vías, obligatoria** *(v0.1.5)*. Antes de cerrar `P(gol | sobreexposición)` hay que mirar el estado del rival: si el rival tiene ventaja, `P1a = 1` y perfil administrador (`S2` alto, cambios defensivos previsibles), **la echada voluntaria del rival cancela parte de la sobreexposición propia** — no hay contragolpe si el que podría contragolpear eligió replegarse. Se **declara** la interacción y **no se le aplica coeficiente** hasta N ≥ 8 declarados en la vía 2.

> **De dónde sale.** TDE-016: ISE 10, se expuso los 25 minutos finales con un lateral improvisado y sin volante de contención, y **no concedió**. La explicación no está en su estructura, que efectivamente quedó partida, sino en la del rival, que ganando de visitante priorizó administrar. Es el primer caso del registro donde las dos vías interactúan entre equipos y el resultado de una depende de la decisión de la otra.

**Primer dato empírico de la vía 2** *(v0.1.5)*: dos casos con ISE 10, un gol concedido. TDE-014 concedió al minuto 90; TDE-016 no. Frecuencia observada 50%, consistente con el 55% que la tabla asigna al perfil de rival más peligroso. Con N = 2 y los dos sin declarar no concluye nada, pero es el primer dato que el índice tiene sobre sí mismo.

> **Candidato de medición: el ISE puede tener la enfermedad de `C1`** *(v0.1.11)*. TDE-031 llegó al techo de **10.0** con un perfil que cumple buena parte de cualquier campeonato: equipo obligado a ganar, un solo volante de contención con los dos laterales altos, y rival con transición como plan A. Van **tres dieces** en el registro: TDE-014, TDE-016 y TDE-031. Un índice de tres indicadores sin pesos que satura con facilidad no discrimina — solo desplaza la escala hacia arriba, que es literalmente el diagnóstico que se le hizo a `C1` en la banda 5-7.
>
> **Es candidato de medición antes que de cambio.** Primer paso: contar la distribución completa de valores del ISE sobre el registro y ver qué fracción supera 7. Si la mayoría de los casos cae ahí, el problema está en la rúbrica y no en los casos, y el reescalado va sobre `SOB2`, que es el indicador que más fácil llega a 1 —basta con que los dos laterales suban sin contención fija, que es la configuración por defecto de cualquier equipo que persigue un resultado—. **No tocar nada hasta tener el conteo.**

> **Candidato declarado y NO aplicado: la anulación del ISE por expulsión depende del marcador** *(v0.1.12)*. La disciplina 16 manda leer el ISE como **anulado** cuando hay roja, sobre el argumento de que un equipo con un hombre menos y en desventaja *"no compra riesgo, lo evita"*. En TDE-034 el delantero y goleador del torneo fue expulsado por conducta violenta al minuto 66 con el equipo **perdiendo 0-1**, y el ISE no se anuló en la práctica: Huracán siguió persiguiendo porque el marcador no le dejaba otra opción, con un hombre menos y sin su única referencia de área, y concedió a los 86. La regla original salió de TDE-019, donde el expulsado iba **empatando** — y ahí sí podía elegir resistir.
>
> **Propuesta, sin aplicar:** roja yendo empatado o ganando → `ECHADA-NUM`, ISE anulado, como está hoy. Roja yendo perdiendo → el ISE **no se anula, se agrava**, y `SOB2` se lee al alza porque el equipo pierde estructura sin poder dejar de exponerse. Con un solo caso no entra. Revisión con **≥3 casos de expulsión con el equipo en desventaja**.

**Doble publicacion obligatoria cuando la interaccion esta activa** *(v0.1.16)*. Si el rival tiene ventaja, `P1a = 1` y perfil administrador, el output publica `P(gol | sobreexposicion)` **en sus dos versiones**:

```
P(gol | sobreexposicion) con el rival administrando   = X%
P(gol | sobreexposicion) sin administracion del rival = Y%
```

La disciplina 14 sigue prohibiendo el coeficiente de forma estructural. Prohibir el coeficiente **no obliga a elegir un numero en silencio**: es el mismo criterio de la caja de sensibilidad, publicar los dos extremos con su origen. Van tres casos del mecanismo con el mismo signo (TDE-016, TDE-039, TDE-042) y dos de los tres son RETRO.

**Regla de emisión.** El ISE se calcula y se reporta **siempre**, incluso —y sobre todo— cuando el IE es bajo. El riesgo del tramo final es el **máximo** de las dos vías, nunca la suma.

**Regla de asimetría.** En un cruce, lo normal es que las dos vías estén activas en equipos distintos: el que aguanta corre riesgo de echada, el que necesita el gol corre riesgo de sobreexposición. Si el módulo asigna la misma vía a los dos equipos, revisar SOB1 antes de seguir.

**Ventana modal de `SOB`**: no se deriva del reloj ni del bloque físico, sino del minuto en que el equipo empieza a necesitar el gol. Con SOB1 = 1 desde el arranque, la ventana es 75-90. Si la necesidad aparece por un gol en contra, es la ventana posterior a ese gol. **Si las dos cláusulas activan a la vez** —obligación desde el arranque y además gol en contra—, **se declaran las dos ventanas y se puntúan por separado** *(v0.1.15, mismo criterio que la disciplina 37)*. En TDE-039 ambas activaron y el gol del segundo tiempo cayó fuera de las dos, al 46', que no es tramo final.

---

## Caja de sensibilidad — salida obligatoria *(v0.1.11)*

Cada vez que un indicador se declara `sin dato`, el output publica el IE calculado en **los dos extremos** del rango que ese hueco abre. Dejó de ser buena práctica y es requisito, con dos casos a favor y ninguno en contra:

| Caso | Rango publicado | Recomputado con el motor |
|---|---|---|
| TDE-026 | 5.2 anticipado con `F2 = 1` | 4.95 |
| TDE-031 | 5.54 (`F2 = 0`) a 6.42 (`F2 = 1`) | **6.42 exacto** |

**Para qué sirve, que no es lo mismo que declarar el hueco.** La disciplina 21 protege del número inventado; la caja responde una pregunta distinta: **si el faltante importa o no**. Si los dos extremos caen en la misma banda, el hueco es cosmético y el análisis se sostiene tal como está. Si la cruzan —el bloque F de TDE-032 va de 5.59 a 7.35 con `F1` y `F2` ausentes— el output tiene que decir que la lectura depende de un dato que no se tiene, en lugar de presentar un punto medio con cara de estimación.

---

## Salida mínima obligatoria

Para cada equipo evaluado: `IE`, **la caja de sensibilidad si algún indicador quedó `sin dato`**, `P(echada)`, `P(fractura|echada)`, `P(gol|fractura)`, riesgo compuesto de la vía 1, **`ISE`, `P(sobreexposición)` y `P(gol|sobreexposición)`**, tipo modal entre los seis códigos, ventana modal, los **dos indicadores que más empujan el score** nombrados explícitamente, **las compuertas que operaron** (aunque no hayan cambiado el número) y **la advertencia de banda si el IE cae entre 5 y 7**.

Y, desde v0.1.1, el **falsador**: la observación concreta que dejaría el pronóstico en evidencia. Debe escribirse como condición observable pura, sin cláusulas de estado del marcador que puedan invertirse. El falsador de TDE-005 decía *"si retrocede antes del 60 sin ir ganando"*; Melgar retrocedió antes del 60 **yendo ganando**, así que el falsador no se gatilló pese a que el pronóstico había fallado por completo. Un falsador mal redactado es peor que ninguno, porque da falsa tranquilidad.
