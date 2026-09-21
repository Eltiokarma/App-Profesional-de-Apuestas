# Jev (System One) en el SAD — dónde encaja y dónde no

Jev es un modelo de TypeSafe AI (15/09/2026) que **no genera texto**: recibe un
estado sin estructurar y devuelve valores tipados definidos de antemano —una
elección de una lista, un puntaje sobre una rúbrica ordenada, un sí/no
probabilístico— con su distribución y su confianza. 70–500 ms, $0.042 por
millón de tokens de entrada, salida gratis.

- Blog: https://typesafe.ai/blog/introducing-system-one-models-and-jev
- Docs: https://docs.typesafe.ai/ · `POST https://api.typesafe.ai/v1/systemone`
- Adaptador: `backend/analisis/jev.py` · tests: `python -m backend.test_jev`

## La regla madre

**Jev es un clasificador de texto, no un pronosticador.** Está calibrado contra
modelos de frontera, no contra resultados deportivos: no sabe de fútbol más que
un LLM cualquiera. No toca la matemática del motor (K, niveles, Poisson,
burbuja, gap §5) ni nada que salga de nuestra base. Sigue mandando la regla del
proyecto: *lo que está en nuestra base se calcula, no se le pregunta a un
modelo*.

Entra en UN solo hueco: donde hoy hay **texto que nadie revisa**, o un **juicio
cerrado** que hoy cuesta un LLM caro y lento.

## Lo que el propio modelo declara que hace mal

`docs.typesafe.ai/model-jaggedness/jev-1.13`. Esto no es letra chica: define el
borde de lo que se le puede preguntar.

| Falla declarada | Qué queda prohibido aquí |
|---|---|
| Números y conteo poco fiables | Nada aritmético: totales, sub-scores, IP, puntos del reventón |
| Fechas como texto, sin orden | Nada de calendario, TTL, ventana del TDE, `edadDias` del DT |
| **No trata el estado como hostil** | La prensa entra como `state`, **jamás** en `instructions` ni en los criterios |
| Indirección y dobles negaciones | Una pregunta, un salto |
| Lectura literal | Los criterios se escriben con sus casos límite |
| No procesa imágenes | El pantallazo del once a mano NO es trabajo suyo |
| **No es determinista** (cookbook de self-consistency: 15 corridas del mismo texto y la etiqueta se mueve en los bordes) | Su salida NO se recalcula al leer, como todo lo demás aquí: se guarda sellada con la versión que respondió |
| 64k tokens por petición · 32k para el estado · 1200 req/min | Un barrido grande se reparte; `preguntar()` corta antes de salir |

La tercera fila es la de seguridad: el modelo admite inyección de instrucciones
desde el contenido. Por eso la salida es siempre un enum de una lista que
escribimos nosotros, y **nunca dispara una acción con efectos**: lo peor que
puede lograr un texto envenenado es elegir mal dentro de esa lista.

## Sin clave: corre, pero no decide

`jev.preguntar()` sin `TYPESAFE_API_KEY` responde en modo **simulado**,
determinista por el estado, con `simulado=True` y `confianza=0.0`. Como todo
consumidor decide por umbral (`.fiable()`), un simulado no pasa ninguno: el
código se recorre entero, pero no fabrica juicios. Para probar una lógica
concreta se le pone un guion fijo con `SAD_JEV_GUION=/ruta/respuestas.json`.

## Los candidatos, con veredicto

### 1. Guardrail de coherencia del parte de Cowork — **SÍ, es el primero**

Hoy `backend/analisis/parte.py` atrapa errores de **tipo y estructura**: un
número en `ieNivel`, una oración como nombre de DT, claves raras, un once que
casa con menos de 7 nombres. Todo eso viaja en `rechazos`.

Lo que **nada** atrapa hoy es la **incoherencia semántica**: notas que
describen un plantel desarmado con el bloque A en 9; una `lecturaSad` que dice
lo contrario que el 1X2 declarado; un `factorX` que repite una baja ya contada
en `fuera`. Eso es juicio de sentido común sobre prosa: el dominio exacto de
Jev, y el único trabajo del parte que no es calculable ni es análisis.

- Forma: `noul` por invariante, sobre el parte ya normalizado como estado.
  **El trabajo se parte**: Jev clasifica la PROSA sola («¿este texto describe
  un plantel estable?») y el CÓDIGO compara esa etiqueta con el sub-score. No
  se le pide comparar «bloque A = 9» con las notas: eso es aritmética, que es
  su falla declarada nº 2. Todas las preguntas en UNA petición: 13 preguntas
  batcheadas salen 12x más baratas y 10x más rápidas que 13 llamadas, porque
  el estado se manda una vez.
- Salida: alertas de tipo `dato` (`COHERENCIA-*`), junto a `rechazos` en el
  recibo del POST. **No mueve un solo número** y no pone nada en cuarentena
  sola: la cuarentena es por criterio y con motivo.
- Costo: un parte son ~2–4k tokens → menos de una diezmilésima de dólar.
  Con 70–500 ms cabe dentro del POST sin que se note.
- **El resultado se guarda, no se deriva.** El proyecto recalcula lo derivado
  al leer para que no haya copias viejas; con una salida no determinista esa
  regla se da vuelta: dos GET del mismo parte darían alertas distintas sin que
  nadie tocara nada. La alerta se sella con `jev-1.13.0` y la fecha, y se
  rehace solo cuando cambia el parte.
- Sitio: `backend/analisis/coherencia.py`, llamado desde `POST /analisis/cowork`.

### 2. Validador semántico de la despensa — **SÍ, y es el más barato**

La regla de la despensa es que *un campo sin fuente va VACÍO, nunca rellenado a
ojo* (`docs/DESPENSA_DESKTOP.md`). Hoy esa regla la sostiene la disciplina de
quien investiga y la revisión del PR. Un `noul` por campo —«¿este texto nombra
jugadores concretos con su situación, o es una generalidad?»— la convierte en
un **lint que corre en CI** sobre `backend/analisis/despensa/*.json`: centavos
por barrido quincenal, cero riesgo (no escribe datos, marca el PR).

### 3. Alertas EFE desde texto — **NO como está planteado**

Las bajas y las alineaciones ya vienen **estructuradas** de API-Football, y la
señal de `missingFixture` ya está calculada con su umbral
(`backend/jugadores.py`). Pedirle a un modelo que reconstruya de texto algo que
la base ya tiene es exactamente lo que el proyecto prohíbe. El único texto real
que queda en ese terreno son las `notas` y el `factorX` del parte — y eso es el
candidato 1. El pantallazo del once a mano no cuenta: Jev no procesa imágenes.

### 4. Triage del EFE antes de gastar búsqueda web — **el que más ahorra**

Lo caro del EFE no son los tokens: son las búsquedas web (~$10 / 1000, ver
`docs/efe-dtp/COSTO_IA.md`), y el techo se reparte a ojo por campos faltantes.
Un `choice` de 70 ms por campo faltante —«¿esto lo decide prensa de esta semana,
o da igual con lo que ya hay en la despensa?»— es el patrón *confidence
routing* de su documentación aplicado al único sitio donde tenemos una factura
grande. Se engancha en `backend/test_preflight.py` / el preflight del EFE, que
ya existe para medir lo que va a costar antes de gastarlo.

## ¿Esto "potencia" a Cowork?

No lo hace más listo ni lo reemplaza: Cowork sigue siendo quien juzga, y Jev no
sabe de fútbol. Lo que hace es **quitarle trabajo mecánico y ponerle un control
de calidad a la salida** — que es justo donde se pierde hoy: partes con el
índice en la etiqueta, bloques incoherentes, campos rellenados a ojo. Un
guardrail de 300 ms que cuesta una diezmilésima de dólar por parte no compite
con el análisis: lo audita.

Y lo que NO hay que hacer: darle a Jev el pronóstico, el 1X2, los puntos del
reventón o cualquier peso del skill. No está calibrado contra resultados, y
mover un peso exige el backtest a la vista y la población `ciega`+`PRE`
(`docs/APRENDIZAJE.md`). Un modelo rápido y barato que opina de fútbol es la
forma más cómoda de contaminar una rúbrica que costó 171k burbujas calibrar.

## Catálogo completo — todo lo que Jev puede hacer aquí

Los candidatos de arriba son los primeros; este es el barrido entero del
proyecto. El patrón se repite: **texto de una fuente ajena que hoy se descarta
en silencio**, o **una elección entre candidatos resuelta con heurística de
tokens**. Nada de esto decide solo: todos PROPONEN y un humano confirma, salvo
donde se diga.

### Ingesta — texto de una API que cambia sin avisar

| Dónde | Qué haría | Por qué hoy duele |
|---|---|---|
| `backend/cuota_mercados.py` | `choice` a la FAMILIA del mercado (1X2 · doble oportunidad · over/under · ambos marcan · hándicap · ninguna), para cada `bet_name` que hoy cae en `None`. **La LÍNEA no**: «Over 2.5» vs «Over 1.5» y «Home -0.5» vs «-1.5» son números, su falla declarada — eso lo saca una regex sobre el `value`, y si la regex no la reconoce, el mercado queda fuera como hoy | `cuota_key` descarta lo que no mapea **en silencio**, y desde el 18/09 eso además decide lo que se GUARDA. Si mañana el catálogo renombra «Match Winner», el 1X2 deja de entrar y nadie se entera hasta que una gráfica sale vacía |
| `extractor --buscar` | `choice` entre los candidatos de `/leagues` (nombre · país · tipo) | Descubrir el id de un torneo nuevo es leer una lista a ojo |
| `_fase_de_round` (`app.py`) | `choice` al vocabulario nuestro para la ronda que no casa con la regex. Mapear «1/8 Finals» → octavos es traducir un nombre, no ordenar magnitudes: eso sí lo hace. Decidir si octavos es «más decisivo» que cuartos, no — ese orden ya vive en el código | «Relegation Round», «Final Stage - 2». Y `league_round` decide también la fase decisiva del padrón de la agenda: una ronda desconocida ahí mueve qué partidos se analizan |
| `backend/nombres.py` | `choice` entre los candidatos cuando `canonizar` queda AMBIGUO | Hoy vuelve tal cual y el dato se deposita bajo un nombre que nadie consulta: se paga la búsqueda igual |

En las cuatro, la salida es una **propuesta en un informe** (o un PR), nunca
una escritura. La regla de que un mapeo mal hecho es peor que un hueco declarado
no cambia porque el que lo proponga sea rápido y barato.

### Bloque F — el once pegado a mano (deuda 5)

`bloque_f._casa()` cruza por tokens, y con menos de 7 nombres casados el bloque
NO cierra: devuelve el conflicto en vez de un IP inventado. Correcto, y también
el sitio donde más trabajo manual se pierde — Primera B de Colombia y Primera de
Uruguay no dan alineaciones, así que el pantallazo es el procedimiento.

El patrón no es el `noul` binario que propuse primero: el cookbook de
*knowledge graph entity alignment* resuelve esto con un **`score` de tres
niveles** —distinto · posiblemente el mismo · el mismo— acompañado de `noul`
por campo, todo en una petición. Y sin constante de umbral: el nivel sale de
redondear. El nivel del medio es lo que hace que valga la pena, porque es
exactamente lo que el bloque F ya hace hoy: **no cierra, va a revisión**. Un
match perdido cuesta un pantallazo; un match falso mete a otro jugador en el
once y contamina el IP.

Así desatasca los fallos de tipeo, acento, apellido compuesto e inicial
(«M. Vucetich» vs «Manuel Vucetich Rojas»), **solo sobre los que NO casaron**
por tokens. Condiciones, porque este es el único de la lista que toca un
cálculo:

- solo desempata lo que quedó sin casar; **nunca deshace** un match de tokens,
- exige confianza alta y deja la procedencia declarada, como `xi/auto`,
- si el bloque sigue sin llegar a 7, sigue sin cerrar. El umbral no se toca.

### Operación

- **Triage de la corrida diaria**: `choice` sobre el log de Deploy —¿corrida
  normal, degradada o fallida?— para que el silencio no sea el único aviso. Lo
  que NO hace es contar ni comparar fechas: los números de la corrida los pone
  el latido, que ya existe.

### Frontend — el buscador inteligente

Una consulta en lenguaje natural («el equipo peruano que juega el jueves»)
resuelta como `choice` sobre los candidatos es el caso de libro. **No mientras
siga abierta la deuda 1**: `VITE_API_KEY` viaja al bundle, así que un endpoint
que gasta expuesto al navegador es una llave de gasto regalada. Primero el
proxy o el token de solo lectura; después esto.

## Revisión del 21/09 — lo que no se sostuvo y lo que apareció

Segunda pasada por la documentación, buscando dónde se cae lo propuesto.

**Tres cosas que había dicho mal**, ya corregidas arriba:

1. **Los mercados no se clasifican de una vez.** «Over 2.5» y «Over 1.5» se
   distinguen por un número, y el modelo declara que trabaja peor con
   representaciones numéricas que semánticas («convierta valores numéricos a
   categorías nombradas antes de pasarlos»). La familia sí, la línea con
   regex — clasificación en dos etapas, que es su cookbook jerárquico.
2. **El guardrail no compara la prosa con el sub-score.** Eso es aritmética.
   Jev etiqueta la prosa, el código compara con el número.
3. **El cruce de nombres no es un sí/no**, es el score de tres niveles del
   cookbook de entidades, con el nivel medio yendo a revisión.

**Y tres que cambian el diseño, no solo el detalle:**

4. **Jev no es determinista.** El cookbook de self-consistency corre la misma
   rúbrica 15 veces sobre el mismo texto y la etiqueta se mueve en los casos
   de borde; con un umbral de abstención el acuerdo sube a 99,2 % automatizando
   el 74 %. Aquí eso choca con una regla del proyecto —lo derivado se recalcula
   al leer— y gana la regla nueva: **lo que responda Jev se guarda sellado con
   su versión de modelo**, nunca se vuelve a derivar. Si no, dos lecturas del
   mismo parte dan alertas distintas y nadie sabe por qué.
5. **Probabilidad y confianza no son lo mismo, y el umbral es por uso.** Un
   `noul` en 0.72 es accionable para el cookbook de guardrails (actuar ≥ 0.70)
   y a la vez tiene confianza 0.44, por debajo de la zona media. Un 0.9 global
   sobre un noul equivale a exigir p ≥ 0.95: no decidir nunca. El cookbook de
   entidades directamente no usa umbral.
6. **Hay límites y conviene batchear.** 64k tokens por petición, 32k para el
   estado, 1200 req/min. Trece preguntas en una llamada cuestan 12x menos y
   tardan 10x menos que trece llamadas, porque el estado se manda una vez: la
   unidad natural es «un estado, todas sus preguntas».

**Usos nuevos que aparecieron en los cookbooks:**

- **Recuperación de estructura** (*autoformat*): el once pegado a mano llega
  como texto crudo —una lista mal cortada, con dorsales y posiciones
  mezcladas—. Convertirlo en lista de nombres ataca la deuda 5 por delante,
  antes del cruce.
- **Extracción de fechas con opciones cerradas**: el `desde` del DT que hoy
  sale de prensa («llegó en julio de 2025»). Rehabilita parcialmente lo que
  había descartado: el modelo NO ordena fechas, pero sí puede elegir mes y año
  de listas cerradas, y la aritmética la hace `parte._dt_equipo`. Con eso, el
  `desde` de prensa deja de depender de que alguien lo escriba en formato.
- **Verificación de citas**: la despensa exige `fuentes[]`. Preguntar si la
  fuente citada respalda el dato es el complemento del lint de generalidades.
- **Sugerencia de skill / function calling**: enrutar una petición al skill del
  SAD que le toca (EFE, DTP, TDE, burbujas). Útil el día que el pipeline tenga
  entrada en lenguaje natural; hoy no la tiene.
- **Re-ranking y búsqueda línea a línea**: el buscador inteligente, que sigue
  bloqueado por la deuda 1.

**El criterio de aceptación, que faltaba.** Antes de cablear cualquiera de
estos: correr el mismo caso N veces (el cookbook usa 15, con un `uid` distinto
por corrida para aislar la volatilidad del modelo) y medir cuánto baila la
respuesta. Si baila en los casos que importan, ese uso no entra — o entra con
abstención, que es lo que sube el acuerdo a 99,2 %. **Ningún uso se da por
bueno porque suene razonable en una tabla.**

## Lo que Jev NO puede hacer aquí — la lista corta

No es cautela: cada una tiene su motivo y es definitiva.

1. **Pronosticar.** 1X2, marcador, puntos del reventón, sub-scores del EFE,
   índices del TDE, pesos de un skill. No está calibrado contra resultados.
2. **La población del caso** en el aprendizaje (`ciega` / `por_resultado` /
   `post_resultado`). Es justo lo que no se puede deducir y lo que decide si un
   caso acredita; lo declara quien analizó. Deducirlo con un modelo es romper
   el bucle por dentro y no se notaría hasta que las métricas mientan.
3. **Cualquier cosa con fechas o cuentas**: TTL, `edadDias` del DT, ventanas del
   TDE, retención, días de descanso. El modelo declara que cuenta mal y que lee
   las fechas como texto sin orden.
4. **Poner en cuarentena.** Es por criterio y con motivo, nunca por resultado.
5. **Leer el pantallazo del once.** No procesa imágenes.
6. **Ser la defensa contra contenido hostil.** Él mismo admite inyección desde
   el estado: no puede ser el que vigile lo que no sabe mirar.

## El costo real no son los centavos

$0.042 por millón de tokens de entrada hace que cualquiera de estos usos sea
gratis en la práctica. Lo que sí se paga es **una dependencia externa más**: un
servicio que puede caerse, cambiar de precio o de versión de modelo. Por eso
todo uso entra por `jev.disponible()` y **degrada a lo que hace hoy** —el hueco
declarado, el conflicto devuelto, el descarte silencioso que ya existía—, nunca
a un valor inventado. Un sitio donde apagar Jev rompa el pipeline es un sitio
donde Jev estaba decidiendo, y eso ya es un error de diseño.

## Orden propuesto

1. Adaptador + tests. **Hecho** (`backend/analisis/jev.py`, `backend/test_jev.py`).
2. Guardrail de coherencia del parte, con las alertas apagadas hasta ver 20
   partes reales: se miden contra lo que un humano habría marcado antes de
   dejarlas salir en el recibo.
3. Lint de la despensa en CI.
4. Triage del preflight del EFE, midiendo búsquedas ahorradas contra el costo.

Nada de esto arranca de verdad hasta que llegue la clave (`TYPESAFE_API_KEY`,
early access). Mientras tanto el código corre en simulado y los tests pasan sin
red.
