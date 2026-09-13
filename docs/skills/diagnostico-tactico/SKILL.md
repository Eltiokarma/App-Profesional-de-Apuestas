---
name: diagnostico-tactico
description: "Analisis tactico-tecnico del juego de un partido de futbol, no estructural. Es la capa de juego del sistema SAD y complementa al EFE. Produce el Diagnostico Tactico de Partido: lectura de alineacion, clasificacion del bloque rival, mapa de duelos por carriles, plan por fases, autopsia de goles con responsables y deteccion de mecanismos abiertos. Funciona como cadena rodante: cada analisis es pre-partido y abre cerrando el anterior. Activar cuando el usuario quiera analizar tacticamente un partido o diga analicemos la formacion o la alineacion, como debe jugar tal equipo para ganar o empatar, por que no funciono el juego, analicemos los goles o la derrota o la victoria, analicemos el equipo que presentara el rival, dame un plan de partido o un mapa de duelos, sea pre o post. Activar tambien tras un EFE cuando se quiere bajar al futbol del partido. No usar para el clasificador EFE ni para constantes K o apuestas."
---

# Diagnóstico Táctico de Partido (DTP) — Capa de Juego del SAD

> **v1.2 · 30.08.2026 — Post-caso CD Moquegua 1-4 Alianza Atlético (F7 Clausura Perú).** Dos altas. La **sexta pregunta del checklist de clasificación del bloque** y con ella la clase **`no probado`**: un bloque puede dar estructural en las cinco preguntas de insumo y no haber sido puesto a prueba nunca, y en ese caso la alerta de degradación **no** se suprime. Y la **regla de posesión condicional**: el perfil de balón es una constante de la interacción, no del equipo, y se declara junto al estado de marcador que lo produjo. Caso de referencia del falso positivo: un bloque con cinco de cinco del lado estructural que concedió tres goles, y cuyo perfil de posesión importado —77% de balón cedido— se invirtió en el partido, terminando con más pases que el rival.

> **v1.1 · 22.08.2026 — Post-caso Hull City 2-0 Manchester United.** Tres altas: el **checklist de clasificación del bloque** (obligatorio en M2 antes de invocar cualquier número de minutos), el mecanismo **`MECANISMO-ABIERTO`** (trasladado desde el clasificador EFE, donde estaba mal alojado) y la **regla de minutos compartidos**, que baja del Bloque F del EFE y alimenta el seguro tras la pérdida.

## Qué es y qué NO es

El SAD tiene tres capas. No las mezcles:

| Capa | Pregunta que responde | Skill |
|------|----------------------|-------|
| **EFE** | ¿Puedo confiar en la señal histórica (K) de este equipo? | `efe-dashboard` |
| **DTP** *(este skill)* | ¿Cómo se juega y se decide ESTE partido? | `diagnostico-tactico` |
| **K / mercado** | ¿Qué dicen las constantes y el mercado de apuestas? | `sad-analysis` |

El DTP **no usa constantes K ni clasifica estabilidad**. Trabaja con lo que se ve en cancha: sistemas, perfiles individuales, duelos, fases del juego y el contexto del partido. El EFE te dice *cuánto creerle a los datos*; el DTP te dice *el fútbol*.

> **Origen:** el DTP es el "Bloque H" del EFE crecido. El Bloque H del EFE queda como un "DTP-lite" que dispara este análisis completo.

---

## EL PRINCIPIO ORGANIZADOR: LA CADENA RODANTE

**Todo DTP es un documento pre-partido que ABRE cerrando el partido anterior.**

```
DTP(N)  =  [ CIERRE de N-1 ]  +  [ APERTURA de N ]
              M4 + M5              M1 + M2 + M3 + M6
           (post, validación)      (pre, proyección)
```

```
DTP(1):           [APERTURA 1]
DTP(2): [CIERRE 1][APERTURA 2]
DTP(3): [CIERRE 2][APERTURA 3]
```

**Por qué importa:** el pre-partido es lo accionable, pero al obligar a cada pre-partido a empezar cerrando el anterior, el modelo se autovalida continuamente.

**Reglas de la cadena:**
- Si **no hay partido anterior** en la serie → omitir el CIERRE, anotar "Sin partido anterior en la cadena".
- Si **sí hay** un DTP previo → recuperar M2 y M3 del documento anterior y **validarlos honestamente**. No reescribir el pasado.
- "Partido anterior" = el último partido del MISMO equipo foco, sin importar competición.
- **Si el partido anterior es un amistoso** *(v1.1)*, el CIERRE se hace igual pero se declara nivel de dato C: los estímulos son asimétricos y las conclusiones no se transfieren.

---

## FLUJO DE EJECUCIÓN

1. **Investiga en la web (obligatorio).** Para ambos equipos: XI confirmado o el más reciente/probable, sistema, bajas/dudas, **minutos compartidos de las líneas clave**, y el contexto: amistoso o competitivo, rotación, días de descanso, estímulo.
2. **CIERRE del partido anterior** (si aplica): M4 + M5, contrastando con lo pronosticado.
3. **APERTURA:** M1 → M2 → M3.
4. **M6** cruza y matiza todo.
5. **Método de Responsables** en cada evento decisivo.
6. **Entrega** en el formato pedido.

> **Investigación web:** consultas en español con año y nombres entre comillas; consultas secuenciales y específicas por tipo de dato (XI, sistema, bajas, resultado) en vez de una sola amplia. `fetch_sports_data` sirve para EPL/LaLiga/Serie A; NO para Liga 1 Perú ni Liga MX.

---

## MÓDULOS

### M1 — Lectura de Alineación *(pre)*

Lee el XI como una declaración de intenciones. No describas: interpreta.

- **Dibujo y cambios respecto al partido anterior.**
- **Roles reasignados** — el dato más jugoso. Un jugador fuera de su puesto natural suele ser la grieta.
- **Qué señala el XI:** ¿plan conservador u ofensivo? ¿busca tener la pelota o cederla?
- **Vulnerabilidad que el propio XI introduce.** Todo plan abre un flanco. Nómbralo.
- **Forma sin balón:** cómo se reordena el dibujo al defender.
- **Minutos compartidos** *(v1.1)*: ¿hay dos titulares de la misma línea que nunca jugaron juntos? Si el EFE ya activó `EJE-DEBUTANTE`, heredarlo sin re-investigar.

### M2 — Mapa de Enfrentamiento *(pre)*

Cruza los dos perfiles. El fútbol es interacción, no equipos aislados.

- **Sistema vs sistema:** qué produce el choque de esquemas.
- **Duelos por carril** e identificación de **mismatches** concretos.
- **Vida útil del planteo rival** → ver el checklist obligatorio abajo.
- **Vías de gol probables de CADA lado** (no solo del equipo foco): pelota parada, transición, desborde, llegada de segunda línea, cutback.
- **Rest defense / seguro tras la pérdida** de cada equipo. Este dato **viaja directo** al indicador de sobreexposición del módulo del tramo final; no se re-estima allá.
- **Veredicto:** MATCHUP FAVORABLE / NEUTRO / DESFAVORABLE, con la razón táctica.

#### CHECKLIST DE CLASIFICACIÓN DEL BLOQUE *(NUEVO v1.1, obligatorio)*

> **Antes de invocar cualquier número de minutos de vida útil**, clasificar. La diferencia entre un bloque improvisado y uno estructural no es de grado, es de clase, y confundirlas es un error documentado del sistema.

| # | Pregunta | Improvisado | Estructural |
|---|----------|-------------|-------------|
| 1 | ¿Cuántos meses lleva el equipo jugando con ese modelo defensivo? | <3 | ≥6 |
| 2 | ¿Cuántos minutos competitivos acumula **esa línea de fondo concreta**? | <300 | ≥800 |
| 3 | ¿Los centrales son de oficio o improvisados? | Improvisados / laterales reconvertidos | De oficio |
| 4 | ¿Hay capacidad de refresco? (banco con carrileros y centrales de recambio) | No | Sí |
| 5 | ¿El repliegue está documentado como plan o es una reacción al marcador? | Reacción | Plan |
| **6** *(v1.2)* | **¿Este bloque sostuvo el resultado alguna vez estando empatado o en desventaja, contra un rival obligado a atacar?** | **No: todas las vallas invictas salieron de partidos sin presión real** | **Sí, con caso concreto nombrado** |

**Lectura:**
- **3 o más respuestas en la columna izquierda (preguntas 1-5) → bloque improvisado. Vida útil 55-65 minutos.**
- **3 o más en la derecha (preguntas 1-5) → bloque estructural. Vida útil 80-90 minutos.**
- **La pregunta 6 no cuenta para el recuento: es una llave aparte.** Un bloque estructural con la 6 en la columna izquierda se clasifica **`estructural no probado`**: conserva la vida útil de 80-90 minutos —los insumos son reales— pero **la alerta de degradación SÍ se emite**, y en el módulo del tramo final `C1` puntúa **0.5** en lugar de 0.
- **Empate en las cinco primeras → declarar la ambigüedad y publicar las dos lecturas.** No elegir la que conviene a la narrativa.

> **De dónde sale la pregunta 6 — falso positivo con cinco de cinco.** CD Moquegua, F7 del Clausura peruano 2026: tres temporadas con el mismo cuerpo técnico, misma línea de fondo desde febrero, centrales de oficio, recambios en el banco, repliegue como plan declarado. Cinco de cinco del lado estructural, alerta de degradación suprimida, y el equipo concedió tres goles. **Sus porterías a cero venían de tres empates y un 0-0: partidos donde el rival nunca tuvo que ir a buscar de verdad.** Las cinco preguntas originales miden lo que el equipo *tiene*; ninguna mide si eso fue puesto a prueba. Un bloque que solo aguantó contra rivales sin urgencia no demostró que aguanta, demostró que no lo atacaron.
>
> **Corolario sobre precedentes.** Un caso anterior del mismo equipo en la misma cancha no vale como precedente si tampoco hubo presión. Y vale al revés: si el bloque sostuvo un resultado contra un rival que necesitaba el gol, nombrar ese partido en el output es lo que convierte la clasificación en evidencia.

> **Trampa frecuente:** el dibujo cambió pero el modelo no. Un equipo que pasó de línea de cuatro a línea de tres sigue teniendo su repliegue entrenado si el modelo de bloque medio-bajo lleva una temporada. La pregunta 1 es sobre el **modelo**, la pregunta 2 sobre la **línea concreta**. Son distintas y las dos cuentan.
>
> **Caso de referencia — falso positivo.** Hull City, F1 Premier League 2026-27: dibujo nuevo (3-4-2-1 en lugar del 4-2-3-1 del ascenso) pero modelo de una temporada entera, centrales de oficio, carrileros con fondo y banco recién comprado. Cuatro de cinco preguntas del lado estructural. El bloque aguantó los 90 con 11 despejes y dos atajadas del arquero.

#### REGLA DE POSESIÓN CONDICIONAL *(NUEVO v1.2, obligatoria)*

> **El perfil de balón es una constante de la interacción, no del equipo.** Nunca importar un porcentaje de posesión de un partido anterior sin declarar **contra quién** y **con qué marcador** se produjo.

| Lo que se declara | Ejemplo correcto | Ejemplo incorrecto |
|-------------------|------------------|--------------------|
| Rival y su intención con el balón | "Cedió el 77% ante un rival que también quería la pelota" | "Cede el 77%" |
| Estado de marcador dominante | "Cedió el 77% yendo empatado o arriba" | "Es un equipo que cede la pelota" |
| Altitud, sede y competición | "En altura, a 3.050 m, partido de copa" | *(omitido)* |

**Caso de referencia.** En el F7 del Clausura peruano 2026 se modeló al local como bloque medio-bajo cediendo el balón, usando el 77% cedido de su partido anterior en altura. Le empataron al minuto 24 y terminó con **más pases que el visitante**, 351 contra 300, y 19 remates en contra. El mismo equipo, tres días después, con el perfil de posesión invertido, porque el marcador lo obligó a perseguir. **Con el partido a favor un equipo cede; con el partido en contra el mismo equipo acumula pases.**

### M3 — Plan por Fases *(pre)* — es la Matriz de Escenarios

Plan accionable dividido en tramos.

- **0-25':** cómo arrancar (aguantar el ímpetu / golpear si el rival arranca frío).
- **25-65':** gestión del bloque, tempo, alturas de laterales, rol del 9, rest defense.
- **65-80'+:** decisiones según marcador, piernas frescas, balón parado como palanca, riesgos de fatiga.
- Para cada fase, **palancas concretas** — no "jugar mejor", sino "circular vertical en 2-3 toques", "cargar el área con dos centrales altos en córner", "un hombre fijo al rechace del primer palo".
- Si el usuario lo pide, expandir a la **Matriz clásica** (ganar / empatar / no perder).

### M4 — Autopsia de Gol *(post — vive en el CIERRE)*

Por **cada** gol del partido anterior:

```
DISPARADOR  →  SECUENCIA  →  DEFINICIÓN
```

Y aplicar el **Método de Responsables**. Distinguir siempre **mérito** de **error**.

**Formato:**
Gol — Jugador X (min'), marcador. Vía: pelota parada / transición / juego abierto.
- *Disparador:* qué lo originó.
- *Secuencia:* cómo se construyó.
- *Definición:* cómo terminó en gol.
- *Responsables (mérito):* quién asistió, quién definió, qué hicieron bien.
- *Responsables (en contra):* con jerarquía — principal, secundario, estructural.

#### MECANISMO-ABIERTO *(NUEVO v1.1 — trasladado desde el clasificador EFE)*

> **Por qué vive acá y no en el EFE.** Es una observación de la capa de juego: describe cómo se concede, no cuánta confianza merece la serie histórica. En el clasificador estaba declarado como candidato y no tenía dónde aterrizar.

**Activación:** ≥2 goles recibidos que comparten mecanismo identificable —centro y cabezazo, rechace de córner no atacado, pase interior entre líneas, transición por el mismo carril— **en el mismo partido o en partidos consecutivos**.

**Procedimiento:**
1. Nombrar el mecanismo con precisión. No "pelota parada": *"envío al segundo palo con marca zonal y sin hombre asignado al rechace"*.
2. Verificar si **la línea implicada repite ≥80% de sus intérpretes** para la fecha siguiente.
3. Verificar si **hubo corrección en vivo** entre el primer gol y el segundo. Dos concesiones del mismo tipo separadas por más de 15 minutos sin ajuste es un fallo de lectura del banco, no de calidad de los jugadores.

**Efecto:** degradar las K defensivas del equipo **para el partido siguiente** y anotar el mecanismo como vía de gol probable del próximo rival en M2. **No es coeficiente**: es una vía declarada.

> **Caso de referencia.** Manchester United en el MKM Stadium, F1 2026-27: gol al 17' por rechace de córner no atacado, gol al 38' por marca perdida al segundo palo en tiro libre. Veintiún minutos entre los dos, sin ajuste visible del marcaje. La misma línea de fondo repetía intérpretes para la fecha siguiente.

### M5 — Diagnóstico de Fase de Juego *(post — vive en el CIERRE)*

- ¿Funcionó el plan (M3) pronosticado? **¿Hasta qué minuto?** Sé honesto.
- Separa **juego abierto vs balón parado vs transición**: ¿de dónde salió el peligro real?
- **Cronología del giro:** cuándo y por qué cambió el partido.
- **Contraste con el pronóstico previo:** qué acertó, qué no, y qué lección entra a M6/M3 del siguiente.
- **Chequeo de MECANISMO-ABIERTO** *(v1.1)*: ¿hubo dos goles del mismo mecanismo? Si sí, declararlo acá.
- **Chequeo del checklist de bloque** *(v1.1)*: si se clasificó el bloque rival y el partido lo contradijo, anotar **qué pregunta del checklist se respondió mal**, no solo que la alerta falló. El aprendizaje está en la pregunta, no en el número.

### M6 — Moduladores de Contexto *(transversal)*

- **Amistoso vs competitivo:** bajar la confianza; estímulos asimétricos.
- **Rotación / protección de figuras:** un XI muy rotado arranca descoordinado los primeros 20-30'.
- **Fatiga:** segundo partido en pocos días, viaje, falta de fondo de banco.
- **Ausencias estrella:** quitar a un desequilibrante de 1v1 cambia las vías de gol del rival.
- **Equipo en reconstrucción / XI nuevo:** sin automatismos ensayados, el ataque posicional contra defensas ordenadas suele fallar.
- **Primera fecha del torneo** *(v1.1)*: la ventana de referencia son amistosos, los dos equipos llegan sin automatismos competitivos y **el peso relativo de la pelota parada sube**, porque es la vía que menos depende de coordinación acumulada en juego abierto. Declararlo en M2.

---

## EL MÉTODO DE RESPONSABLES — el sello del DTP

Por cada evento decisivo (gol, ocasión clara, error grave):

1. **Mérito** — quién lo construyó, acción por acción.
2. **Error** — quién lo concedió.
3. **Jerarquía** — reparte: **principal** (el gatillo), **secundario** (mala cobertura), **estructural** (línea alta sin seguro). No descargues todo en una persona si la estructura también falló; tampoco diluyas un error individual claro en "fue colectivo".
4. **Absolución cuando toca** — si la definición fue de mérito en un mano a mano inevitable, el arquero no es responsable. Dilo.

---

## DISCIPLINA — lo que lo salva de ser puro relato

1. **Hecho observable vs interpretación.** Etiqueta la interpretación como tal y dale un nivel de confianza.
2. **Respeto a la varianza.** Un 2-1 tiene poquísimos eventos decisivos. El DTP **describe mecanismos, no decreta causas**.
3. **Anti-hindsight estricto en el CIERRE.** Reconstruye solo con lo reportado. Si el DTP previo falló, regístralo como fallo.
4. **No fabricar mecánica de gol.** Si las fuentes solo dicen "asistencia de X a Y", di lo que hay y marca lo que falta.
5. **Clasificar antes de alarmar** *(v1.1)*. Ninguna alerta de vida útil, degradación o colapso se emite sin haber corrido antes el checklist que le corresponde. Cuando una alerta falla, revisar primero si el paso de clasificación existía.
6. **Declarar la contaminación en el momento en que ocurre** *(v1.1)*. Si el resultado aparece durante la investigación —típicamente al buscar el XI confirmado— decirlo antes de escribir el primer módulo, no al cerrar. Un analista que conoce el desenlace siempre encuentra buenos motivos para haber estado donde el desenlace lo deja parado.

---

## SALIDAS / FORMATOS DE ENTREGA

### A) Dashboard JSX interactivo
React de un solo archivo en `/mnt/user-data/outputs/dtp_[equipos].jsx`:
- **Pizarra de goles:** croquis SVG de cada gol con disparador → secuencia → definición y responsables.
- **Mapa de duelos:** carriles con los mismatches marcados (M2).
- **Checklist de clasificación del bloque** como tabla visible, con su veredicto.
- **Plan por fases:** las tres franjas (M3) con sus palancas.
- **Cierre vs Apertura:** dos secciones claras.
- Tema claro, colores reales de cada club, tipografía legible.

**Validación JSX:** `@babel/parser` con plugin JSX. Copiar a `/mnt/user-data/outputs/` y usar `present_files`.

### B) Reporte escrito estructurado
Orden CIERRE → APERTURA con los módulos como secciones. Prosa directa.

> **Si se usa el visualizer:** caracteres ASCII-safe y JavaScript ES5 (sin arrow functions, sin template literals).

---

## REGISTRO DE LA CADENA — validación acumulada

| Partido | Pronóstico clave del DTP | Qué pasó | Acierto / Fallo | Lección → siguiente |
|---------|--------------------------|----------|-----------------|---------------------|
| N-1 vs … | (vía de gol / matchup / plan) | (resultado real) | ✅ / 🔶 / ❌ | (ajuste que entra a M6/M3) |

Añadir la entrada al cerrar cada partido (M5). Marcar `RETRO` y el tipo de selección cuando corresponda: los casos contaminados fijan rúbrica pero **no acreditan**.

---

## INTEGRACIÓN CON EL ECOSISTEMA SAD

- **Tras un EFE** (`efe-dashboard`): el EFE aporta el contexto de confianza; el DTP, el juego. **Heredar sin re-investigar** B5, D3, F4, F6/`EJE-DEBUTANTE`, el matchup H y las alertas activas.
- **Hacia el módulo del tramo final** (`teorema-del-echado`): el **rest defense de M2 viaja directo** al indicador de seguro tras la pérdida. La **clasificación del bloque de M2** viaja directo al indicador de repliegue entrenado. No se re-estiman.
- **Matriz de Escenarios:** es la salida M3 en modo prospectivo.
- **Timeline** (`futbol-timeline`): aporta el "qué viene pasando" institucional.
- **Idioma:** español para fútbol latinoamericano y español; inglés para Premier League. **Si el usuario escribe en español, el idioma del usuario manda** sobre esta regla.

> **Cierre de cada entrega:** ofrecer el siguiente paso — la pizarra si entregaste texto, la Matriz ampliada, el timeline de contexto, o el módulo del tramo final.
