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
- Salida: alertas de tipo `dato` (`COHERENCIA-*`), junto a `rechazos` en el
  recibo del POST. **No mueve un solo número** y no pone nada en cuarentena
  sola: la cuarentena es por criterio y con motivo.
- Costo: un parte son ~2–4k tokens → menos de una diezmilésima de dólar.
  Con 70–500 ms cabe dentro del POST sin que se note.
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
