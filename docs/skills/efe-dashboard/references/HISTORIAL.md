# Historial · `efe-dashboard`

Se lee **solo al revisar el skill** (fase D, modo mantenimiento, una propuesta
nueva), nunca al analizar un partido. Toda regla vigente está en el cuerpo de
`SKILL.md`; acá quedan las notas de cada versión, sus casos y lo que se movió
a otro skill, tal cual (núcleo, `docs/revisiones/NUCLEO_SKILLS_propuesta.md`,
aplicado con la v1.14).

---

## Notas de versión

> **v1.14 · 17.11.2026 — Alineado con el clasificador EFE v1.11.** Ningún peso, indicador ni alerta del clasificador tocado; la banda de goleada sigue sin números. Aprobada por el usuario el 17/11 con todas las recomendaciones. Propuesta: `docs/revisiones/EFE_v1.11_propuesta.md` (§12).
>
> **1. La matriz no usa el arco como gatillo de gol** («Para perder», PASO 6) sin GK-FALLA-ACTIVA o errores documentados: B6 🔶, la zona GK en rojo y GK-DOWNGRADE van a la caja como rango (clasificador v1.11, punto 2; Albania 1528963, Chequia 1528985, Inglaterra 1528984).
>
> **2. La palanca del reloj** (PASO 6) sale de `bancoProbable` de `GET …/f1/{id}` (clasificador v1.11, punto 4), condicionada al once con la rama abierta.
>
> **3. La descripción** pasa a «EFE v1.11 (skill v1.14)».
>
> **4. Núcleo:** las notas v1.13 … v1.7, «Movido a otro skill en v1.6» y la «Nota de actualización manual» pasan a este archivo. Antes de mover, al cuerpo (núcleo §2.4): el suplente de impacto es factor X (PASO 1, F5; regla D1 de la v1.8) y el once probable es nivel de dato C con la ventana de confirmación pendiente (PASO 0-bis; regla D2 de la v1.8).

> **v1.13 · 10.11.2026 — Alineado con el clasificador EFE v1.10.** Ningún peso, indicador ni alerta del clasificador tocado; la banda de goleada sigue sin números. De dónde sale: dossier del 10/11, 2 lecciones del dashboard (las dos acertadas) y las del clasificador, partidos del 01 al 09/11. Propuesta: `docs/revisiones/EFE_v1.10_propuesta.md`.
>
> **1. La caja de sensibilidad dibuja las dos variantes del sistema** con D1 🔶 o T.54 de ≤ 2 partidos (cada una con su línea y la pieza que entra) y la rama abierta por anuncio, costumbre o equipo sin nada en juego, con los rotables de todas las líneas.
>
> **2. La palanca del reloj y el banco de la matriz salen del banco probable de la tabla F1** (B5 por rol), no de los dos nombres más conocidos (Independiente: Tempone).
>
> **3. La alerta F3 copia la tabla del clasificador:** suma la zona > 40 % de la v1.7 (faltaba) y la nota dice qué anuncia la zona (DEF: vía del rival o volumen concedido, y el arquero; ATK: volumen, dónde se remata o conversión) y quién la cubre.
>
> **4. La descripción** pasa a «EFE v1.10 (skill v1.13)». La lección de Konyaspor (la goleada como rama de «Para perder») ya estaba aplicada en la v1.12 y se marca aplicada.

> **v1.12 · 01.11.2026 — Alineado con el clasificador EFE v1.9.** Ningún peso, indicador ni alerta del clasificador tocado; tampoco números en la banda de goleada (se calibra con más casos). Propuesta: `docs/revisiones/EFE_v1.9_propuesta.md`.
>
> **1. Un récord de racha no baja la banda de goleada.** `FAMILIA-RECORD` y `K-EXTREMO` son prudencia con la carga, no probabilidad (REVENTON §10 y §15.2): en su récord la burbuja no da probabilidad de corte (Delfín: la banda baja de goleada se apoyó en una racha récord de 13 visitas sin perder por 2+, y FAMILIA-RECORD ya lo avisaba).
>
> **2. La goleada se nombra como rama en «Para perder»** cuando el gatillo es un gol temprano del rival y el inferior queda obligado a perseguir, no solo como banda base (Konyaspor: la banda base de 8-15 % se escribió y la goleada llegó por el gatillo declarado, gol temprano que obliga a abrirse, cumplido antes del 30').
>
> **3. Lo que baja de la v1.9 al dibujo.** La caja de sensibilidad dibuja la zona **«degradada, cubierta de oficio»** (rango más ancho, mismo centro), **el arco del día** (la zona GK sobre el arquero que ataja hoy; con dos que se alternan, la ausencia del que no ataja no la reduce) y **la rama del once alternativo de los dos lados, con el sistema y el banco que vuelve**. El F6 muestra `EJE-DEBUTANTE` con su **origen** (`calculado` / `declarado`) y, sin once oficial, como condicional («si repiten X–Y»). Hoy la app calcula las parejas nuevas sobre el XI de referencia (`parejasNuevas` de los insumos del DTP); sobre el once oficial está **pendiente de la app**: hasta entonces, `calculado` vale solo para el XI de referencia y con el once oficial el eje es `declarado`.
>
> **v1.11 · 28.10.2026 — Alineado con el clasificador EFE v1.8.** La caja de sensibilidad baja al matchup: un supuesto con declaración pública del DT se dibuja como **rama** del H («si juega con línea de cinco…»), y una zona que la sensibilidad da como crítica (DEF o GK) baja la confianza un escalón antes de la matriz. T.54 se muestra en los dos lados con la fecha del DT; el arco «sin dueño» abre los tres escenarios en la caja. Lo demás de la v1.8 se puntúa en el clasificador.
>
> **v1.10 · 25.10.2026 — Alineado con el clasificador EFE v1.7.** `EJE-DEBUTANTE` pasa a la rúbrica del clasificador con el umbral **≤ 1 partido juntos como titulares** (antes 0 minutos) y las posiciones de la línea se leen del grid del once; el F6 de acá cita esa regla. Lo demás de la v1.7 (F3 por zona, recambio de oficio o reconvertido, jerarquía de fuentes, D3 con contexto, rama «once alternativo», brecha solo en la misma base) se puntúa en el clasificador y se dibuja como hasta ahora: la caja de sensibilidad lleva la rama alternativa y la alerta F3 nombra la zona.

> **v1.9 · 21.10.2026 — Limpieza de lo que no existe y reparto con `sad-analysis` v4.0.** Ningún peso, indicador ni alerta del clasificador tocado.
>
> **1. La lectura integrada (paso 5) pasa a `sad-analysis` v4.0**, que es el skill de la síntesis (pronóstico y lectura de las K). Este skill la muestra en el dashboard; la define y la escribe aquel.
>
> **2. Sale el «Contexto emocional: Anticulebra, Fe Perdida».** Los dos eran motores del sistema anterior que no existen en la app SAD: la Ley 5 (Tensión del Favorito) quedó suspendida por el backtest del 19.10.2026 (63.475 partidos, sin culebra) y la Fe Perdida no tiene péndulo que la calcule. En la cohorte c3 dos partes los invocaron sin dato (Boca–São Paulo, derbi de Montevideo). Queda un **contexto con fuente**: presión de tabla, hinchada, clima del club, citados.
>
> **3. `ANTICULEBRA-INVERTIDA` se renombra `FAVORITO-RELAJADO`.** El contexto del candidato se queda; el nombre de un motor suspendido, no.
>
> **4. Se quitan el «checklist de 9 puntos» y la «Ficha de Mecanismo»** del paso 6: no existen en disco y nadie podía recorrerlos. Quedan los principios que sí están escritos.
>
> **5. La matriz se compara con el 1X2 del motor calculado** (`unXDos` de `/predicciones`, logística calibrada sobre 51.254 partidos), nunca con un Poisson armado con μ: μ son puntos esperados, no goles.

> **v1.8 · 13.09.2026 — Post-caso Alianza Lima 1-2 Universitario (F9 Clausura Perú).** Tres altas y ninguna toca pesos ni indicadores del clasificador.
>
> **1. `F5` mira la nómina completa, no el once probable.** El texto del protocolo siempre dijo *revisar la convocatoria*, y la aplicación lo redujo al once. Resultado del caso: los dos `FACTOR-X` declarados **no fueron titulares** en ninguno de los dos equipos, y el jugador que decidió el partido estaba en la tabla de plantilla del propio dashboard marcado como rotación, sin casillero de factor. **Un suplente con impacto documentado desde el banco en la temporada en curso es factor X por derecho propio**, se proyecte titular o no. El mecanismo vive en el banco: en el fútbol de cinco cambios, el que entra al 70 contra defensas fatigadas es exactamente el perfil que las K no capturan. Es alinear la aplicación con lo que la regla ya pedía, no una regla nueva.
>
> **2. El once probable es nivel de dato C, no B, por muchas fuentes que converjan.** Cuatro medios peruanos publicaron la misma alineación del local y jugó un titular que ninguno había nombrado. **Cuatro fuentes que coinciden no son cuatro observaciones: son una previa copiada cuatro veces.** Consecuencia: cuando el dashboard se genera antes de la publicación del once oficial —alrededor de sesenta minutos antes del inicio—, la banda de protocolos declara la **ventana de confirmación pendiente** y ofrece el recomputo, en lugar de presentar el once probable como si fuera la lista. Los indicadores que se apoyan en el once (`B1`, `B5`, todo el Bloque F) heredan ese nivel.
>
> **3. Candidato declarado y NO aplicado — `GK-FALLA-ACTIVA`.** `B6` mide **continuidad de portería y recorrido en la categoría**, y en este caso puntuó ✅ con toda la razón: arquero titular indiscutido con ocho temporadas en la liga. Lo que `B6` no mira —ni tiene por qué mirar— es si ese arquero **está fallando ahora**. El del caso acumulaba dos errores con gol documentados en el torneo en curso, el mecanismo se declaró por escrito dos veces antes del partido, y el gol que lo decidió al 90+7 fue exactamente eso. **Propuesta: alerta paralela, no modificación de `B6`**, que se activa con ≥2 errores con gol documentados en el torneo en curso del arquero titular habitual, y que entra como agravante declarado y **sin coeficiente**. No entra con un caso, y tiene un riesgo de calibración propio: "error con gol" es una categoría que el periodismo asigna con generosidad, así que el indicador podría terminar midiendo cobertura en lugar de rendimiento. Revisión con ≥3 casos y la definición fijada antes de contarlos. La versión operativa vive en `teorema-del-echado/references/INDICE_IE.md`.
>
> **Lo que el clasificador acertó y conviene no borrar.** El diagnóstico de equivalencia estructural (68,5% contra 65,7%, los dos en formación) describió bien un partido que se decidió en el añadido. La caja de sensibilidad hizo su trabajo: se declaró que la clasificación del local dependía de `B1` y se publicaron los dos extremos en vez de un punto medio. `D3 = ✅` en los dos se confirmó —el local remontó por cuarta vez en la temporada— y `COLAPSO EN CASCADA` se descartó con razón. `B5 = ✅` del visitante se materializó en la jugada del gol decisivo, con el suplente fresco definiendo.

> **v1.7 · 30.08.2026 — Post-caso CD Moquegua 1-4 Alianza Atlético (F7 Clausura Perú).** Dos alertas nuevas: **`COLAPSO POR VENTAJA PERDIDA`** (la secuencia inversa a la del colapso en cascada, que el sistema no contemplaba) y **`BLOQUE NO PROBADO`** (baja del checklist de `diagnostico-tactico` v1.2). Ninguna toca pesos ni indicadores del clasificador: son alertas de contexto. **El prompt del proyecto sigue siendo la fuente de verdad y hay que actualizarlo a mano** — ver la nota al pie de este archivo.

---

## Movido a otro skill en v1.6

- **`MECANISMO-ABIERTO`** (≥2 goles recibidos con mecanismo idéntico y línea que repite intérpretes) pasa al skill **`diagnostico-tactico`**, módulos M4 y M5. Es una observación de la capa de juego, no del clasificador estructural.

---

## Nota de actualización manual — el prompt del proyecto *(v1.7)*

Este skill **no manda** sobre `/mnt/project/EFE_v1_5_prompt.md`, que es la fuente de verdad y es de solo lectura desde el contenedor. Las dos alertas de v1.7 tienen que copiarse a mano a la tabla de alertas del prompt. El texto listo para pegar está en `assets/PARCHE_PROMPT_PROYECTO.md` de este mismo skill.
