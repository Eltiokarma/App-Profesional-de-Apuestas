# Cowork → la app: el parte de análisis

El análisis pre-partido lo escribe **Cowork** con la suscripción plana y lo
**deposita** en la app. La app lo guarda, calcula lo que es aritmética y lo
pinta. El motor por API de Claude (`/analisis/efe`, `backend/analisis/motor.py`)
queda **de emergencia**: sigue ahí, pero ya no es el camino normal.

Dos cosas cambiaron respecto de lo anterior, y las dos por el mismo motivo —
que escribir cuesta tiempo:

| Antes | Ahora |
|---|---|
| El modelo emitía `EFE_COMPARATIVO`: 92 campos anidados, ~4-5k tokens de JSON por partido | Manda sub-scores, la tabla F1 y prosa. El resto lo calcula el backend |
| Cada corrida pasaba por la API y se facturaba | Cowork escribe con la suscripción; la app no paga nada |
| El bloque F se quedaba a medias y alguien lo cerraba a mano | Llega el once (ficha o pantallazo) y el bloque se cierra solo, en milisegundos |

## La regla que ordena el contrato

> Lo que está en nuestra base **se calcula**. Lo que es juicio, se escribe.
> Y lo calculado no se le hace copiar a la salida.

Es la misma de `docs/efe-dtp/COSTO_IA.md`, aplicada ahora al **tiempo de
escritura** en vez de a la factura. Por eso el parte **no lleva**:

| No se manda | Porque lo pone | Dónde |
|---|---|---|
| `total`, `maximoAlcanzable`, `porcentaje`, `clasificacion` | la tabla de puntuación (A + B×1.5 + C + D + E×2, sobre 27 o 23) | `backend/analisis/parte.py` |
| `ip`, `reduccion` por zona, `multiplicadorGk`, `F3`, `F4` | las fórmulas del bloque F | `backend/analisis/bloque_f.py` |
| las ramas A y B del impacto | se derivan de la tabla F1 + las bajas públicas | `bloque_f.ramas()` |
| nombres de los equipos, fecha, liga | el fixture de `sad.db` | `parte.guardar()` |
| el calendario de próximos rivales (bloque G) | ya se calcula con criterio numérico | `backend/calendario.py` |
| los partidos del timeline | ya se calculan | `backend/cronologia.py` |

Si llegan igual, se ignoran. Un campo calculado que viaja en el depósito es
trabajo pagado dos veces y una fuente más de desacuerdo.

## Qué produce cada skill y dónde se ve

El parte no es un volcado de texto: cada skill del pipeline tiene un sitio
propio en la pantalla. Si algo no aparece en esta tabla, no tiene dónde caer y
se perdería.

| Skill / bloque | Qué manda Cowork | Dónde se ve |
|---|---|---|
| `efe-clasificador` A-E | sub-scores crudos + una nota por bloque | pestaña **Bloques EFE** |
| bloque F | tabla F1 + bajas públicas | pestaña **Bloque F** (IP, zonas y ramas calculadas aquí) |
| bloque G · calendario | **nada** | pestaña **Calendario** — `backend/calendario.py` |
| reventón de la burbuja (K) | **nada**: se lee de `GET /equipos/{id}/burbujas` (`docs/REVENTON.md`), 0 tokens | tarjeta **Reventón · guía** en Burbujas y Equipo — `backend/analisis/burbuja.py` |
| bloque H · matchup | diagnóstico, razón, perfiles y `h2a/h2b/h2c` | pestaña **Matchup** |
| lectura SAD | módulo operativo, 1X2, contexto, dato estructural, paradoja | pestaña **Lectura SAD** |
| reventón de la burbuja | `lecturaSad.reventon`: UNA línea por equipo con su lectura (qué racha no seguir y por qué), tras leer `GET /equipos/{id}/burbujas`; los números **no**: el backend los recalcula al leer en `reventonCalculado` (`docs/REVENTON.md`). Si `familias.total.extremo.activo` es true, la línea dice EXTREMO con el N de partidos y el pronóstico no recomienda carga a que esa racha siga | pestaña **Lectura SAD**, caja «Reventón de la burbuja»; la alerta **K-EXTREMO** la agrega el backend a la tira de alertas del parte |
| escala del nivel entre ligas | **nada** | alerta **ESCALA-LIGAS** en la tira del parte, la agrega el backend al leer cuando los dos equipos vienen de ligas distintas (el nivel se calcula contra los rivales de cada uno y NO compara entre bases; un 12.º de LaLiga puede salir con menos nivel que un 15.º de la Premier). Viaja con la liga doméstica de cada lado en `ligas` |
| caja de sensibilidad | `sensibilidad` por equipo | pestaña **Lectura SAD** |
| `sad-analysis` | las tres fuentes de probabilidad + falsador | pestaña **Lectura SAD** |
| `teorema-del-echado` | P1a, F2 y F1 **los calcula el backend** (`GET /analisis/cowork/tde/{id}`); el resto lo escribís vos | pestaña **Teorema del Echado** |
| `teorema-del-echado` | `tde.bloques[]`: IE, ISE, tipología, ventana, vías — **uno por equipo** | pestaña **Teorema del Echado** |
| *(cualquiera)* | `veredicto.porLado[l].leccion` + `skill` + `reglaTocada` | sección **Aprendizaje** |
| reventón, después del partido | **nada**: `objetivo.reventon` reconstruye la burbuja declarada antes del partido y dice si ese partido la reventó (`docs/REVENTON.md` §11); observación, no veredicto | banda del veredicto (`↯ reventó` / `→ siguió`) y sección **Aprendizaje** (tasa por nivel de riesgo contra el backtest) |
| `futbol-timeline` | `timelineEventos` (solo institucional) + narrativa | pestaña **Timeline** (fundida con los partidos calculados) |
| `diagnostico-tactico` | documento `dtp` + `cadena.{a,b}.pronostico` | pestaña **Documentos** y la cadena de la página de **Equipo** |
| matriz de escenarios | documento `matriz` | pestaña **Documentos** |
| ensayo | documento `ensayo` | pestaña **Documentos** |

Dos matices que se ganan al mandar estructura en vez de prosa:

- El **timeline** llega como lista de eventos institucionales, no como HTML. El
  backend le funde los partidos, la jornada y el marcador de `fixtures` y la
  pantalla lo pinta con el mismo componente que el resto de la app. Si Cowork
  manda un evento de tipo `resultado`, se descarta: el marcador es de la
  ingesta, no de una página web.
- El **TDE** trae sus índices como números. Los niveles (verde/ámbar/rojo) los
  manda el skill, no el backend: la escala del IE es suya, y ponerle umbrales
  aquí sería duplicar una tabla que vive en otro lado y desalinearla con el
  tiempo. Sin nivel, la pantalla pinta el número en neutro.

## El ciclo, de noche a mediodía

```
  1. GET  /analisis/cowork/agenda        ¿qué partidos importan mañana?   (lo decide la base)
  2. …análisis por partido, sesión limpia cada uno…
  3. POST /analisis/cowork               el parte, con el bloque F congelado
  ────────── dormir ──────────
  4. POST /analisis/cowork/{id}/xi       llega el once → bloque F cerrado, gratis
       · {"desdeFicha": true}            lo que ya capturó API-Football
       · {"a": {"once": [...]}}          el pantallazo que le pasás a Cowork
  ────────── se juega ──────────
  5. GET  /analisis/cowork/veredictos/pendientes   ¿qué falta validar? (12 h después)
  6. POST /analisis/cowork/{id}/veredicto          ¿acertó? el juicio; el marcador lo pone la app
```

El paso 4 es el que hace que el parte valga: todo lo caro de escribir ya estaba
hecho la noche anterior, y lo único que faltaba —quién juega— entra por una
lista de once nombres y recalcula el impacto con las fórmulas del protocolo.

### Por qué el bloque F llega congelado

Ninguna fuente publica el XI confirmado la noche anterior, y el protocolo lo
prohíbe explícitamente (Disciplina 35: **el bloque F no se puntúa sin XI
confirmado**). Así que el parte llega con:

- la **tabla F1** completa (14-16 jugadores con zona, rol y apps) — que es lo
  que más tiempo toma y no depende del once;
- las **bajas públicas** (lesión larga, sanción, selección) en `fuera`;
- la columna Estado **vacía**;
- y una marca bien visible en pantalla: `⚠️ XI NO CONFIRMADO`.

El backend, mientras tanto, calcula las **dos ramas**: la A (juegan todos los
disponibles conocidos, el piso del impacto) y la B (además falta el 🔴 más
pesado, el techo razonable). Entre esas dos va a caer el número real, y con eso
el partido ya se puede leer.

### Cuando el once no casa

Si el once que llega casa con **menos de 7** nombres de la tabla F1, el bloque
**no** se cierra: se devuelve el conflicto con los nombres que no casaron. Un
once que casa con 3 de 11 no describe a un equipo diezmado — describe una hoja
que no corresponde a esa tabla. Preferimos el hueco declarado a un IP falso.

Lo mismo con un apellido que aparece dos veces en la tabla: va a `dudas` y ese
jugador queda como estaba. No se adivina.

## El endpoint, en corto

Todo bajo `/api/v1`, con `Authorization: Bearer <SAD_TOKEN_COWORK>`.

### Qué token se le da a Cowork (y cuál no)

**No le des `SAD_API_TOKEN`.** Es la llave maestra y abre, entre otras cosas,
los tres endpoints que queman créditos de la API de Claude
(`/analisis/efe|timeline|dtp`), los dos que pueden tirar de
`SAD_EMERGENCIA_KEY` —la clave que factura excedente de API-Football—
(`/fixtures/{id}/vip`, `/ligas/{id}/refrescar`) y el borrado de partes. Es
justo lo que esta arquitectura existe para no hacer.

`SAD_TOKEN_COWORK` es un token acotado a la superficie del parte y a las
lecturas que el pipeline necesita. Lo demás responde **403 diciendo qué token
haría falta**, así que un fallo se lee en el log en vez de aparecer en la
factura.

| Con el token de Cowork | Resultado |
|---|---|
| `GET /analisis/cowork/*`, `POST /analisis/cowork`, `.../xi`, `.../veredicto` | ✅ |
| `GET` de fixtures, equipos, ligas, cuotas, constantes, niveles, predicciones | ✅ |
| `DELETE /analisis/cowork/{id}` | 🚫 403 — borrar es cosa tuya |
| `POST /analisis/efe`, `/timeline`, `/dtp`, `/despensa` | 🚫 403 — gasta créditos |
| `POST /fixtures/{id}/vip`, `/ligas/{id}/refrescar` | 🚫 403 — puede gastar cuota |

Es una **lista de permitidos**: un endpoint nuevo nace denegado para Cowork y
hay que abrirlo a mano. Al revés, cada endpoint que añadiéramos sería un
agujero hasta que alguien se acordara de cerrarlo.

Por qué acotado y no el mismo: Cowork lee páginas de prensa y pantallazos, o
sea contenido que no controlamos. Mínimo privilegio ahí no es paranoia — es
que un texto en una página de resultados no debería tener ni la posibilidad
teórica de acabar en una llamada que cuesta dinero. Y de paso el token se rota
solo, sin tocar el acceso del frontend.

> Si pones `SAD_TOKEN_COWORK` con el mismo valor que `SAD_API_TOKEN`, no
> recorta nada: se ignora y el backend lo avisa al arrancar.

| Método | Ruta | Para qué |
|---|---|---|
| GET | `/analisis/cowork/agenda?limite=&liga=&fecha=&grupos=&segundas=` | lo que viene (24 h desde ahora, o el día de `fecha`) por prioridad, con motivo; `liga` acota por texto (país o nombre) |
| POST | `/analisis/cowork` | depositar el parte (idempotente por `fixtureId`) |
| GET | `/analisis/cowork/{fixtureId}` | leerlo con todo lo calculable ya calculado |
| POST | `/analisis/cowork/{fixtureId}/xi` | llega el once → se cierra el bloque F |
| GET | `/analisis/cowork/pendientes` | qué partes siguen esperando once |
| GET | `/analisis/cowork/marcas?ids=1,2,3` | cuáles de esos partidos ya tienen parte (la marca al costado de cada tarjeta en la lista de partidos; no está abierto al token de Cowork) |
| GET | `/analisis/cowork/veredictos/pendientes?horas=12` | qué casos jugados siguen sin cerrar |
| POST | `/analisis/cowork/{fixtureId}/veredicto` | cerrar el caso: ¿acertó el pronóstico? |
| GET | `/analisis/cowork/{fixtureId}/veredicto` | leerlo con su parte objetiva recalculada |
| DELETE | `/analisis/cowork/{fixtureId}` | descartarlo y volver a depositar limpio |

El esquema completo está en `docs/openapi.yaml` (`ParteCoworkEntrada`).

El POST devuelve un **recibo**: cuántos jugadores entraron por lado, qué
documentos se guardaron y —lo importante— `discrepancias`, la lista de nombres
que Cowork mandó y no casan con el fixture. No se corrigen en silencio:
analizar el partido equivocado es justo el error que ese campo hace visible.

## La prioridad del día la decide la base

El padrón de la agenda es **el mismo que el de las cuotas en vivo**
(`extractor.ligas_vivo()` = `LIGAS − LIGAS_MENORES`). Una sola fuente: tener
dos listas de "ligas importantes" en dos archivos garantiza que se separen, y
ya se separaron una vez.

| Prioridad | Criterio |
|---|---|
| 1 | Liga 1 Perú (la casa) |
| 2 | torneo internacional en **fase decisiva** (de octavos en adelante) |
| 3 | clásico / derbi **dentro del padrón** |
| 4 | liga del padrón con equipo en el top 6 o en crisis |
| 5 | torneo internacional en fase de grupos / fase liga — **solo con `grupos=true`**; por defecto va a `descartados` |
| 6 | resto de las primeras divisiones |
| 7 | segundas divisiones — **solo con `segundas=true`**; por defecto van a `descartados` |
| 0 | descartado, y viaja **con su motivo y el ID de la liga** |

Quedan fuera a propósito las **copas nacionales** y los amistosos: se ingestan
igual —las constantes de un equipo necesitan todos sus partidos— pero no son
candidatos de análisis. La fase de grupos internacional y las segundas
quedaron fuera por defecto después de la corrida del 16/09: un jueves de
Europa League llenó los ocho cupos con Levski–Salzburg y OFI–Hoffenheim
mientras la jornada de LaLiga esperaba. Sin `fecha` la agenda es «desde ahora
y por 24 h» —antes era «mañana en UTC», y a las 07:00 de un miércoles
devolvía el jueves entero—, y `liga=<texto>` acota por país o nombre
(«España») sin buscar el id.

### Tres cosas que este criterio arregló

**El padrón se decidía por NOMBRE.** El efecto real, que nadie vio durante
semanas: Brasil, Colombia, Chile, Uruguay, Ecuador, Paraguay, Bolivia,
Venezuela, Portugal, Bélgica, la Europa League y la Conference caían siempre en
«fuera del padrón» y se descartaban enteras. Un descarte silencioso no se
audita.

**El clásico se miraba ANTES del padrón.** Así, un torneo fuera de él entraba o
no según se activara el etiquetador de derbis: la Copa Uruguay entró para un
partido y se descartó para otros tres del mismo torneo y el mismo día. Ahora el
padrón manda primero y el descarte es el mismo siempre.

**El corte por límite no se veía.** Con `limite=4` y cuatro llaves
internacionales el mismo día, una jornada entera de LaLiga no entra — y desde
afuera parece que la liga no está cubierta. La respuesta ahora trae `corte`:
cuántos candidatos hubo, cuántos quedaron fuera, de qué prioridad y de qué
ligas. Si querés cubrir más, el que se sube es `limite`.

Las **fases decisivas** se leen de `league_round`: `final` cubre también
*Quarter-finals*, *Semi-finals* y *8th Finals*, que es como las nombra
API-Football.

`CLÁSICO` sigue siendo parcial, igual que en el bloque G: una rivalidad
nacional sin vecindad geográfica (Alianza–Cienciano) no sale de nuestros datos.
Está declarado en la respuesta.

### Los mandos manuales

Para apuntar el batch a mano (probar una liga, cubrir lo que queda de esta
noche) sin tocar el padrón:

| Parámetro | Qué hace |
|---|---|
| `ligaId=262` | solo esa liga, por id |
| `liga=España` | solo las ligas **del padrón** cuyo país o nombre contiene ese texto; la respuesta lista `filtro.ligasQueCasan` (vacío = esa liga no está en el padrón, y ahí se para) |
| `desdeAhora=true&horas=6` | ventana rodante desde este momento, no el día natural (1 a 72 h) |
| `grupos=true` / `segundas=true` | meten la fase de grupos internacional y las segundas divisiones, que quedan fuera por defecto |
| `incluirDescartados=true` | los de prioridad 0 entran al final, **con su motivo** |
| `limite=N` | tope de la lista (1 a 20) y tope de partes de la corrida; `corte` dice qué quedó fuera solo por él |

`desdeAhora` existe por una razón concreta: a las 20:00 de Lima el día UTC ya
es el siguiente, así que un filtro por fecha se comería justo los partidos de
esta noche. La ventana rodante no tiene ese problema.

**Un filtro manual NO contamina la población del caso.** Elegir "Liga MX de
esta noche" antes del pitazo es selección ex ante: el veredicto se escribe con
`seleccion: "ciega"` igual. Lo que contamina es elegir un partido PORQUE pasó
algo en él. La respuesta lo dice en `notaSeleccion` para que no haya que
deducirlo doce horas después.

## El veredicto: 12 horas después (fase B de `docs/APRENDIZAJE.md`)

Un pronóstico que nadie comprueba no es un pronóstico. Doce horas después del
partido hay que decir si acertó, y **la mitad de esa respuesta ya está en
nuestra base**:

| Lo calcula el backend | Lo escribe Cowork |
|---|---|
| marcador final (a 90') y ganador | por qué falló |
| ¿acertó el 1X2 declarado? | qué mecanismo no vio |
| ¿acertó el marcador exacto? | la lección, en una frase accionable |
| el Brier del caso | a qué skill le toca esa lección |
| ¿cayó gol en la ventana del TDE? | **si el caso es ciego o está contaminado** |
| ¿reventó la burbuja de cada lado? (lo declarado antes y lo que pasó) | si el falsador se cumplió |
| los goles con su minuto y su lado | si tu línea de `lecturaSad.reventon` se sostuvo |

Tres fronteras que conviene entender, porque explican por qué el reparto es
ese y no otro:

- **El falsador no lo verifica el backend.** Es prosa, y verificar prosa
  arbitraria con un 80% de acierto sería peor que no hacerlo: nadie sabría de
  cuál 20% desconfiar. Lo que la app hace es servir la evidencia con la que se
  comprueba —los goles con minuto y lado— y dejar que Cowork declare.
- **La ventana del TDE sí se comprueba**, porque "75-90'" son dos números y un
  gol tiene un minuto. Se cuentan solo los goles CONTRA el equipo evaluado: la
  echada se observa en lo que recibe, no en lo que hace.
- **El reventón se observa, no se juzga.** `objetivo.reventon` trae, por lado,
  la burbuja tal como estaba antes del partido (signo, K, racha, riesgo, si
  tenía K-EXTREMO) y si ese partido la reventó (`docs/REVENTON.md` §11). No
  hay `acerto`: un riesgo alto que revienta no es un acierto ni uno bajo que
  revienta un fallo, porque el riesgo es una tasa y se compara en conjunto
  contra el backtest en `/analisis/cowork/lecciones`. Lo que sí es tuyo es la
  línea que escribiste en `lecturaSad.reventon`: si recomendaste no seguir la
  racha y la racha siguió (o al revés), eso va en `queP` y, si enseña algo, en
  `leccion`, con `skill: "sad-analysis"`.

### La población del caso: el campo que decide si esto vale

`seleccion` es obligatorio y **no se puede deducir desde el backend**:

| Valor | Cuándo | ¿Acredita? |
|---|---|---|
| `ciega` | el partido se eligió sin saber nada — de la agenda, la noche anterior | **sí**, con `PRE` |
| `por_resultado` | se eligió porque pasó algo (sembrado) | no |
| `post_resultado` | se puntuó con el marcador ya a la vista | no |

El parte de Cowork **nace ciego**, y esa es la razón por la que vale: es la
primera vez que el sistema produce casos ciegos en volumen. Mezclar poblaciones
no es un matiz: la calibración del TDE ya midió el precio (11% de echadas
reales contra 31% con los sembrados dentro).

`modoEvaluacion` dice **contra qué se puntuó**, no cuánto vio quien puntúa:
`PRE` = el caso se cerró contra el **resultado final**; `COND` = se cerró
contra un marcador **parcial**, con el partido todavía en juego, así que el
acierto es condicional y podría darse vuelta. Todo veredicto se escribe
después del partido y eso no lo vuelve COND. Haber seguido el partido en vivo
tampoco: el pronóstico ya estaba sellado y el backend no deja pisarlo. Si eso
pesa, va en `mancha`. Solo `ciega` + `PRE` acredita.

**El backend lo comprueba**: `terminado` sale de nuestra base, así que
declarar `PRE` sobre un partido que sigue rodando devuelve 422 y no guarda
nada. No es un criterio a discutir — es una contradicción con un dato que ya
tenemos.

**Y si el caso es ciego pero hay algo que contar:** `mancha`, una frase. No
cambia la población ni el `acredita` —eso lo decide `seleccion`— pero queda en
campo propio, la pantalla lo marca **CON SALVEDAD** y una auditoría lo
encuentra filtrando en vez de leyendo. Ejemplo real: el parte se retocó con el
partido ya rodando aunque el pronóstico no se movió. Las tres etiquetas de
población dicen *cuánto se sabía del resultado*; si no había resultado que
mirar, `post_resultado` sería mentir en la otra dirección.

### Anti-hindsight

Sin pronóstico previo declarado, **la cadena del equipo no recibe veredicto**.
El caso se guarda igual y los equipos afectados vuelven en
`sinPronosticoPrevio`. Un juicio sobre algo que nunca se declaró no es
auditable: es una opinión escrita después.

Por lo mismo, re-depositar el parte después del partido **no cambia el
pronóstico ya declarado ni borra el veredicto ya escrito**. Si mandás otro
pronóstico, se conserva el primero y el recibo lo delata en `cadenaIgnorada`.

## Qué hace el depósito con lo que no entiende

Tres cosas que la primera corrida real destapó, y que ahora están cerradas:

**1. Se aceptan las formas naturales.** La rúbrica del EFE nombra los roles con
símbolos y con su etiqueta, y las posiciones en español. Exigir las siglas
internas era pedir una traducción, y cuando salía mal el jugador desaparecía.
Ahora valen las tres:

| Campo | Formas aceptadas |
|---|---|
| `rol` | `TF` · `🔴` · `Titular fijo` (ídem TH/🟠, ROT/🟡, SUP/⚪) |
| `zona` | `GK` · `POR` · `Portero` · `Arquero` (ídem DEF, MID, ATK) — y si falta `zona`, se deduce de `posicion` |
| `bloques.A` | `3` · `{"score": 3, "nota": "…"}` |

**1-bis. Un campo con el nombre equivocado se delata.** Es el fallo más caro,
porque no se parece a un fallo: la clave se descarta entera y el POST responde
200 como si todo hubiera ido bien. Ahora cualquier clave desconocida —en la
raíz, en un equipo, en un jugador, en una alerta o en una baja— vuelve en
`rechazos` con la sugerencia más parecida.

También se aceptan dos alias que salían naturales y se perdían:

| Antes se perdía | Ahora |
|---|---|
| `alertas[].texto` | alias válido de `detalle` |
| `alertas[].equipo: "ambos"` | vocabulario válido del protocolo (se normalizaba a `global`) |

Y una alerta que llega sin texto se declara como cáscara vacía en vez de
guardarse muda.

**2. Lo que se rechaza se DICE.** El recibo trae `rechazos`, con dónde estaba,
por qué no entró y qué se esperaba:

```json
{"donde": "equipos.a.plantel[3]", "jugador": "Nombre",
 "porque": "rol no reconocido: 'crack'",
 "esperado": "TF / TH / ROT / SUP (o 🔴 🟠 🟡 ⚪, o «Titular fijo»)"}
```

Un sub-score que se recorta también se declara (`99 → 6`): un bloque recortado
cambia la clasificación del equipo, y cambiarla en silencio es peor que
rechazar el depósito.

**3. El POST reemplaza el parte ENTERO, y ahora avisa.** Es idempotente a
propósito: con merge no habría forma de *quitar* una alerta que dejó de
aplicar. Pero un cuerpo incompleto borraba lo anterior sin que nadie se
enterara. Ahora el recibo trae `perdido` y `aviso`:

```
"perdido": ["alertas: 5 → 0", "fuentes: 3 → 0", "jugadores: 32 → 0"],
"aviso": "Este depósito dejó el parte con MENOS contenido del que tenía…"
```

**4. El parte se puede reconstruir desde su propia lectura.** Como el POST
reemplaza entero, corregir algo es `GET` → modificar → `POST`. Para que ese
viaje no pierda nada, la lectura devuelve un bloque `entrada` con lo que no se
puede deducir del resto: `timelineEventos`, `timelineNarrativa`, `cadena` y
`descartados`.

**Toma la respuesta del `GET`, cambia lo que quieras cambiar y mándala de
vuelta entera.** No hace falta desarmar nada: `entrada` va anidada tal como
vino, y lo calculado que también trae la lectura (`partido`, `estado`,
`timeline`, `veredicto`, `xi`, los `total`/`porcentaje`/`clasificacion` de
cada equipo) se ignora en silencio — no es un campo desconocido, es nuestra
propia respuesta. Si prefieres escribir un campo suelto en la raíz
(`"timelineNarrativa": "…"` al lado de `entrada`), **lo suelto gana**: es lo
que alguien acaba de escribir.

> **Regla para probar formas de campo:** hazlo sobre un fixture de descarte,
> nunca sobre uno que ya tiene un parte bueno. Si igual pasa, el `aviso` te lo
> dice y vuelves a depositar completo.

### El contrato se lee, no se adivina

`GET /analisis/cowork/contrato` devuelve la forma del cuerpo del POST: las
claves de cada nivel, los indicadores del TDE por bloque, los ids de documento
que la pantalla titula sola, y lo que NO hay que mandar porque se calcula.

Sale de **las mismas constantes que validan el depósito**, así que no puede
desincronizarse del código: un campo nuevo aparece ahí con solo agregarlo al
validador. `/openapi.json` está apagado en despliegue —y con razón, expone
también lo que gasta dinero—, pero dejar a quien deposita adivinando la forma
garantiza depósitos a medias.

### El `tde` es POR EQUIPO y caben los dos

El índice **es de un equipo**, no del partido: el IE de quien se puede echar no
dice nada del riesgo del rival. El parte guardaba **uno solo** y el del otro
equipo terminaba en `notas` —prosa que no se puede consultar, no se puede
comprobar contra los goles recibidos y no entra en ninguna métrica—. Ahora los
dos son dato de primera clase:

```json
"tde": {"bloques": [
  {"equipo": "a", "ieNivel": "verde", "ventana": "60-75'", "indicadores": {...}},
  {"equipo": "b", "ieNivel": "rojo", "ventana": "75-90'", "indicadores": {...}}
]}
```

Se aceptan **cuatro formas** y las cuatro se guardan igual, en `bloques`: la
canónica de arriba —que es la que devuelve el GET, para poder re-depositar la
respuesta tal cual—, un objeto plano con `equipo` adentro (la de siempre),
`{"a": {...}, "b": {...}}` como los equipos, y una lista de bloques. Antes tres
de esas cuatro se guardaban como `{}` **sin un solo rechazo**: el trabajo se
perdía y el recibo decía que todo estaba bien.

Lo que sigue delatándose: `tde` como string, `vias` con strings adentro (que
reventaba por 500, y **un 500 en un batch desatendido pierde el parte entero
sin decir por qué**), `equipo` con el nombre del club en vez del LADO
(`"a"` / `"b"`), **dos bloques del mismo lado** —no se elige uno en silencio— y
la llave que contradice al `equipo` de adentro.

**El índice es un número y el nivel es una etiqueta, en dos campos.** `ie` y
`ise` llevan el valor —no hay ningún `ieValor`: ese campo es `ie`— y
`ieNivel`/`iseNivel` la banda `verde`/`ambar`/`rojo` que decide el skill. El
pipeline mandó el índice numérico en `ieNivel` durante diez partes (1550133,
1557408, 1549491…) y el backend lo tiraba guardando `""` **sin un rechazo**:
nueve partes sin nivel que nadie vio hasta el décimo. Ahora un número en
`ieNivel` vuelve en `rechazos` con su sitio y, si `ie` venía vacío, se rescata
ahí; una etiqueta fuera de las tres se rechaza y queda `""`; y
`disciplina43: true` sin vías, sin indicadores y sin índice se rechaza y queda
`false`, porque no hay nada que sostenga esa declaración.

El recibo trae `ladosTde` con los equipos que quedaron, y si solo mandaste uno,
`faltan` cobra el otro: del lado que no declaraste **no hay ventana que
comprobar** cuando se cierre el caso. El veredicto devuelve
`objetivo.tde.bloques`, una comprobación por bloque: la echada de cada equipo
se mide en los goles que **recibe**.

### Un hueco no es un cero

Un parte sin sub-scores se pintaba **«0.0/27 · 0% · SIN FORMACIÓN»**: el
veredicto más duro de la rúbrica, inventado sobre un dato que nadie puntuó. Y
el re-depósito que los había borrado no lo decía, porque `perdido` contaba
documentos y jugadores pero no la rúbrica.

Ahora:

- Cada bloque viaja con `declarado`. Sin puntuar → `porcentaje: null`,
  `clasificacion: ""`, `sinBloques: true`, y la pantalla dice **SIN BLOQUES
  DECLARADOS** en vez de un 0%.
- Un parte a medias declara `bloquesSinDeclarar`: esos cuentan como 0 en el
  total (la rúbrica los pide todos) pero el hueco se dice, para que nadie lea
  el porcentaje como completo.
- `perdido` mira ahora los sub-scores del EFE, los bloques del TDE, los
  pronósticos de la cadena, el reparto 1X2, el falsador, la lectura SAD y la
  caja de sensibilidad. **El POST reemplaza el parte entero**: un cuerpo
  recortado borra lo anterior, y eso tiene que salir en el recibo.
- El eco del GET devuelve `declarado: false` en los huecos y el POST lo
  respeta: re-depositar la respuesta ya no inventa un 0 que nadie escribió.
- Los partes depositados ANTES de que existiera `declarado` no tienen la clave.
  Para esos la declaración se INFIERE del sub-score (>0 lo puso alguien) y se
  marca `declaradoInferido`: tratar «ausente» como «no declarado» les habría
  borrado el EFE de la pantalla a todos — el mismo error, girado del otro lado.

### El veredicto también se re-deposita

`POST /analisis/cowork/{id}/veredicto` acepta la respuesta de su propio GET, igual
que el parte: `acredita`, `falsador`, `rechazos`, `cerradoEn`, `actualizadoEn`,
`objetivo` y `sinPronosticoPrevio` son eco y se ignoran, no se rechazan.

Dos reglas que salieron de romperlo:

- **Una clave ausente conserva lo que había.** Re-postear el eco (que trae
  `falsador: {texto, cumplido}` y no `falsadorCumplido`) degradaba un
  `cumplido: false` guardado a `null`: el caso perdía su prueba más dura sin que
  nadie lo pidiera. Para borrarlo hay que mandar `falsadorCumplido: null` a
  propósito.
- **`cerradoEn` es evidencia, no un `updated_at`.** Es la fecha con la que se
  comprueba que el juicio se escribió cuando se dice, así que el primer cierre
  manda y un re-depósito no la re-sella. Una corrección posterior queda en
  `actualizadoEn`, aparte.

### Las fichas que no van a llegar nunca

`xi/auto` separa dos cosas que antes se llamaban igual:

- `sinFichaTodavia` — el partido no empezó o acaba de empezar: puede cerrar solo.
- `nuncaVaALlegar` — el partido **ya terminó** y la ingesta nunca trajo la
  alineación. Esa liga no da onces por API-Football: reintentar no sirve, y el
  pantallazo a mano es el procedimiento para esa liga, no la excepción.
  `ligasSinOnce` junta los ids para verlo como patrón.

### La lección es un campo, no una promesa

Cada lado del veredicto puede traer `leccion` + `skill` + `reglaTocada`. Eso es
lo que alimenta la sección **Aprendizaje** (`GET /analisis/cowork/lecciones`):
las lecciones se agrupan por skill, y 4 fallos con lección pendiente del mismo
skill ABREN la revisión —no autorizan ningún cambio—.

Dos cosas que conviene saber al escribir el veredicto:

- **Declará el `skill`.** Sin él la lección sale en `sinSkill`, aparte: no se
  reparte a ojo.
- **La población decide qué puede hacer la lección.** Un caso `ciega`+`PRE`
  puede sostener un cambio de peso; uno contaminado solo fija rúbrica —aclara
  cómo se aplica una regla, sin mover ningún número—. Eso viaja calculado en
  `puedeMoverNumeros`, no queda al criterio de quien lea el dossier ese día.

Mover una lección de estado (`pendiente` → `en_revision` / `aplicada` /
`descartada`) **no** está abierto al token de Cowork: el agente lee sus
lecciones, declarar aplicada la suya es del usuario.

### El once se cierra solo: no hay carrera de 30 minutos

**Cerrar el bloque F no necesita al modelo.** Es cruzar dos listas de nombres y
aplicar los pesos de rol — aritmética que vive en `bloque_f.py`. Por eso seis
partidos que arrancan juntos **no son seis análisis contra el reloj**: son seis
cierres de milisegundos.

`POST /analisis/cowork/xi/auto` cierra el bloque F de **todos** los partes cuya
alineación ya trajo la ingesta. Idempotente, sin tokens, sin cuota de
API-Football. Devuelve tres listas:

| | qué es |
|---|---|
| `cerrados` | quedaron resueltos, con el lado y el estado |
| `reemplazados` | lados que estaban a mano y ahora vienen de la ficha (`fuenteAnterior` dice de dónde venían) |
| `sinFichaTodavia` | la ficha aún no trae la alineación → **estos son los del pantallazo a mano** |
| `conConflicto` | el once casa con menos de 7 nombres de la tabla F1: **no se fuerza**, un IP inventado es peor que un bloque abierto |

**La procedencia del once es dato, y la ficha manda.** Un POST de prueba dejó
el once del 1549492 idéntico pero etiquetado «carga manual» en vez de «ficha
de API-Football», y el barrido lo salteaba para siempre porque «ese lado ya
estaba cerrado». Dos reglas: `POST /analisis/cowork/{id}/xi` **no pisa** un
lado que ya viene de la ficha —lo conserva y lo devuelve en `xiConservados`
con el motivo— salvo `reemplazar: true` en ese lado; y `xi/auto` **reemplaza**
un lado manual cuando la ficha llega (el pantallazo existía porque la ficha no
estaba), listándolo en `reemplazados`. Un lado que ya viene de la ficha no se
vuelve a tocar.

La consecuencia para el diseño del batch: **el análisis pesado va la noche
anterior, sin prisa**, y el once se cierra solo cuando aparece. Lo único que
queda para vos es el pantallazo de los que salen en `sinFichaTodavia`.

### Retomar donde se cortó

La agenda trae `porHacer` y `yaHechos`, y marca cada candidato con
`tieneParte`, `onceCerrado` y `conVeredicto`. Si la corrida se quedó sin
tokens a mitad de camino, la siguiente arranca por `porHacer` y no rehace nada.

**Re-depositar un parte REEMPLAZA el anterior**, así que no se vuelve sobre
`yaHechos` salvo que se quiera rehacerlos a propósito. Eso es lo que convierte
la agenda en la lista de trabajo: nadie tiene que llevar la cuenta aparte.

### Cómo saber que esto sigue corriendo

`GET /analisis/cowork/latido` contesta de una sola llamada si el pipeline está
vivo. **El silencio cuenta como fallo**: cero partes en la ventana devuelve
`rojo`, no «sin novedad» — que es la diferencia entre un monitor y un adorno.

Mira cuatro señales:

| señal | qué delata |
|---|---|
| `depositadosEnLaVentana` + `horasDesdeElUltimo` | el batch dejó de correr |
| `coberturaDeAyer` | corrió pero se saltó partidos — **compara contra lo que la agenda habría elegido**, que es lo único que no se puede deducir mirando los partes |
| `veredictosVencidos` | los partidos terminaron y nadie cerró el caso |
| `sinOnceCerrado` | hay partes con el bloque F congelado |

En la app aparece en la pantalla de **Partidos**, arriba de todo, **solo cuando
hay algo que hacer**. Un aviso que sale siempre se deja de leer a la semana.

El latido no dispara nada ni corrige nada: mira y dice. Quien arregla sos vos.

### El TDE no se escribe entero: la mitad ya está calculada

`GET /analisis/cowork/tde/{fixtureId}` devuelve los insumos del Teorema del
Echado que salen de nuestra base. **No devuelve el IE** — devuelve lo que el
propio skill manda tomar del motor:

| Insumo | De dónde sale | Por qué lo calcula el backend |
|---|---|---|
| `p1a` · protector del resultado | los dos `μ_partido` contra el umbral 0.30 | el skill lo llama **input inviolable** y prohíbe derivarlo del gap o corregir μ por localía a mano |
| `f2` · descanso y calendario | días de descanso antes + señal duro/blando del próximo | **«dato del motor o no es dato»** (Disciplina 21): sin él, el bloque F entero se declara sin dato |
| `f1` · rotación en los últimos 3 | `alineaciones` ya ingestadas | la ingesta captura justo 3 fichas por equipo, que es la ventana exacta de F1 |

Tres cuidados que la respuesta trae escritos:

- **`f2` da un PISO, no un score cerrado.** El viaje largo, el cambio de
  altitud y el calor extremo son parte de la rúbrica y NO están en nuestra
  base: si los hay, el score sube a mano.
- **`p1a` puede bajar.** «Necesita ganar» lleva P1a a 0 y eso no sale de la
  base. Y si P1a queda en 0, la compuerta 1 topa el bloque P entero en 0.5.
- **`f1` dice `sinDato` en vez de inventar.** Sin dos onces capturados no hay
  rotación que contar. Ojo con el sentido de la rúbrica: **0 rotados puntúa 1**
  (mismo once = carga acumulada).

Y `noCalculables` lista los **16 indicadores que siguen siendo tuyos**, con el
motivo de cada uno. No es decoración: un insumo que falta tiene que verse, no
adivinarse.

### Una baja que no está en la tabla F1 no pesa en el IP

El Impacto Ponderado pondera **todos** los roles (TF ×3, TH ×2, ROT ×1,
SUP ×0.5) — pero solo de los jugadores que están en la tabla F1. Una baja
listada únicamente en `fuera`, sin estar en `plantel`, no tenía rol con el que
pesar y desaparecía del cálculo. El IP salía corto y parecía que el ponderador
estaba roto.

Dos formas de evitarlo, y la primera es la buena:

1. **Ponla en `plantel`.** Es lo que pide el protocolo: la tabla F1 lista a
   todos los relevantes, *disponibles y no disponibles*.
2. O dale `zona` y `rol` dentro de `fuera`. El backend la incorpora a la tabla
   para el bloque F y la marca `soloBaja`.

Si no haces ninguna de las dos, el recibo te lo dice con nombre y apellido:
*«esta baja no está en la tabla F1 y no trae zona/rol: NO pesa en el Impacto
Ponderado»*.

---

## Los prompts que hay, y cuál mandar

Cinco, y se eligen por lo que querés cubrir, no por la hora:

| Prompt | Cuándo | Cómo elige los partidos |
|---|---|---|
| **BATCH NOCTURNO v2.5** | la corrida programada | padrón de prioridades, ventana «desde ahora y por 24 h» |
| **«LA LIGA X, AHORA»** | a cualquier hora, una liga entera | `liga=` por texto + ventana rodante (`desdeAhora&horas`), sin tocar el padrón |
| **«RETOMAR HOY»** | el batch se cortó o se saltó partidos | padrón, pero solo `porHacer` de lo que todavía no arrancó |
| **«LLEGÓ EL ONCE»** | llegó un pantallazo de alineación | ninguno: cierra el bloque F de un parte ya depositado |
| **«VALIDAR LO DE AYER»** | 12 h después de los partidos | `veredictos/pendientes`; no analiza nada nuevo |

La **CORRIDA DE PRUEBA SOBRE UNA LIGA** del final es la versión mínima de la
segunda (por `ligaId`, tres partidos, sin veredictos ni `xi/auto`): sirve para
probar la tubería, no para cubrir una jornada.

**Ninguno de los cinco depende de la hora.** La agenda sin `fecha` es «desde
ahora y por N horas», así que el mismo prompt mandado a las 07:18 y a las 14:00
devuelve cosas distintas y las dos correctas: lo que falta por jugarse en ese
momento. Lo único que NO se puede hacer a ninguna hora es analizar un partido
que ya arrancó — eso no es un parte, es hindsight.

---

# PROMPT COWORK — SAD BATCH NOCTURNO v2.5

> Pegar como instrucción de la tarea en Claude Cowork.
> Reemplazar lo que está entre `<< >>` antes de correr.

```text
## 0. ROL Y MODO

Sos un analista del sistema SAD corriendo en modo batch desatendido. No hay
nadie del otro lado: toda duda se resuelve declarándola por escrito en el
parte, nunca frenando la tarea ni inventando el dato.

Tres reglas de siempre:
- Modo PRE / selección ciega. Todo se declara antes del pitazo inicial.
- "Sin dato" es una respuesta válida. Prohibido estimar para rellenar.
- Falsadores obligatorios: toda predicción viene con la condición observable
  que la declara fallada.

Skills disponibles en esta cuenta: efe-clasificador, efe-dashboard,
diagnostico-tactico, futbol-timeline, teorema-del-echado, sad-analysis. Si
alguno no aparece en tu lista, NO lo simules: dejás ese documento fuera del
parte y lo anotás en `pendientes`.

## 1. LA APP ES EL DESTINO, NO UNA CARPETA

Todo lo que produzcas termina en la app por HTTP. No generes archivos sueltos
ni carpetas de entregables: el parte ES el entregable.

Base:  << https://TU-APP.up.railway.app/api/v1 >>
Token: << SAD_TOKEN_COWORK >>   → cabecera `Authorization: Bearer <token>`
       (es el token ACOTADO; si algo responde 403, NO cambies de token:
        ese endpoint no es para vos, anotalo y seguí)

Anclá la fecha real con la herramienta de hora del sistema. No asumas qué día
es. Zona de referencia: America/Lima.

ANTES DE NADA, LEÉ EL CONTRATO:
  GET {base}/analisis/cowork/contrato
Sale de las mismas constantes que validan el depósito, así que no puede estar
desactualizado. Si algo de este prompt y el contrato no coinciden, manda el
contrato — y decilo al terminar.

## 2. QUÉ PARTIDOS (0 deducción: lo decide la base)

  GET {base}/analisis/cowork/agenda?limite=<<5>>&liga=<<>>

ALCANCE: <<todo el padrón / «España» / «Perú» / …>>. Si el alcance nombra un
país o una liga, pasalo TAL CUAL en `liga=` (texto: casa por país o por nombre
—«España» trae LaLiga; «Copa del Rey» no existe en el padrón y la agenda lo va
a decir con `ligasQueCasan: []`, no lo busques por otro lado—). Si el alcance
es «todo», dejá `liga=` vacío. No deduzcas el alcance de una palabra suelta:
si no lo entendés, decilo y pará.

SIN `fecha` la agenda es «desde ahora y por 24 h», a la hora que se corra:
mandada a las 23:00 de Lima trae los de mañana, mandada a las 06:00 trae los
de hoy. NO pases `fecha=` salvo que el usuario te dé un día concreto.

El padrón es el mismo que el de las cuotas en vivo: primeras divisiones de
cada país y los seis torneos internacionales EN FASE DECISIVA (de octavos en
adelante). La fase de grupos / fase liga (Europa League un jueves son
dieciocho partidos) y las segundas divisiones quedan FUERA por defecto y van a
`descartados` con ese motivo; entran solo si el usuario lo pide, con
`grupos=true` / `segundas=true`. Las copas nacionales quedan fuera a
propósito. Cada candidato viene con su `prioridad`, su `motivo` y su `ronda`.

TOPE POR CORRIDA: el `limite` es también el tope de partes de ESTA corrida.
Una corrida de dieciséis partes en una sola conversación se cuelga antes de
terminar (pasó el 16/09). Hacé los de `porHacer`, cerrá, y el usuario vuelve a
mandar el prompt: la agenda trae `yaHechos` y seguís donde quedó.

Mirá también `corte`: dice cuántos candidatos quedaron FUERA solo por el
`limite` y de qué ligas. Si ves ahí una liga que el usuario esperaba, decilo al
terminar — se arregla subiendo el límite, no cambiando el padrón. Y los
`descartados` traen el motivo Y el id de la liga: si una debería entrar, decí
su id.

Devuelve `analizar` (los que tocan, ya ordenados por prioridad y con su
`fixtureId`), `enEspera` y `descartados` con su motivo. Usá `analizar` tal
cual. No re-ordenes, no agregues partidos por tu cuenta.

Cada candidato trae `conflicto`: vacío casi siempre. Si dice que un equipo
«también figura en» otro partido a pocas horas, uno de los dos fixtures está
mal (un aplazado que la ingesta no marcó, o un duplicado). Si chocan LOS DOS
equipos, la agenda ya lo manda a `descartados` con el motivo; si choca uno
solo, se queda en la lista y lo decidís vos: analizalo si la fecha se
confirma en prensa, y si no, saltalo y anotá el `conflicto` en el cierre.
Nunca gastes una sesión en un partido que otra fuente dice que no se juega.

RETOMAR DONDE SE CORTÓ: cada candidato trae `tieneParte`, `onceCerrado` y
`conVeredicto`, y la agenda trae `porHacer` (los que faltan) y `yaHechos`. Si
la corrida anterior se quedó sin tokens, arrancá por `porHacer` y NO vuelvas a
analizar los de `yaHechos`: re-depositar un parte lo reemplaza entero.

SI CORRÉS DE DÍA para cubrir lo que el batch no subió, NO uses el día
natural: `fecha=` trae también los partidos que ya arrancaron. La agenda sin
`fecha` (o con `desdeAhora=true&horas=<<10>>`) devuelve solo los que TODAVÍA
NO EMPEZARON, que son los únicos que se pueden analizar sin el resultado a la
vista, y `porHacer` ya viene filtrado a los que no tienen parte. Elegir así sigue siendo selección ciega (lo dice
`notaSeleccion`). Y `GET {base}/analisis/cowork/latido` es el monitor: dice
cuántos partes entraron en la ventana, qué faltó de la agenda de ayer
(`coberturaDeAyer.faltaron`) y qué casos vencieron sin veredicto.

Si el endpoint falla o devuelve `analizar` vacío: NO inventes un fixtureId.
Terminá el turno diciendo qué respondió la API. Sin fixtureId no hay parte que
depositar, y un id adivinado ensucia el partido de otro.

Si un partido de la lista ya se jugó cuando llegás a él, lo saltás y lo
anotás: un análisis con el resultado a la vista no sirve para calibrar nada.

## 3. UNA SESIÓN LIMPIA POR PARTIDO

Cada partido se trabaja en su propia sesión. Nunca arrastres el contexto de un
partido al siguiente: los datos de un equipo no deben contaminar el scoring
del otro. Si un partido falla, seguís con el próximo.

## 4. QUÉ ESCRIBIR (y qué NO)

Leé la rúbrica de `efe-clasificador` ANTES de puntuar nada.

EL EFE ES TUYO Y ES EL NÚCLEO DEL PARTE. Lo que la app calcula sola es el
TOTAL, el porcentaje y la clasificación —no los sub-scores—. Un parte sin
bloques A-E no es un parte incompleto: es un parte sin EFE, y la pantalla lo
va a mostrar como SIN BLOQUES DECLARADOS. Ya pasó una corrida entera así por
leer mal esta sección. Si de verdad no podés puntuar un bloque, dejalo fuera y
decí por qué en `pendientes`; lo que no se puede evaluar se declara, no se
rellena — pero no saltees el EFE por las dudas.

Escribís vos (es juicio, no se puede calcular):
- Los sub-scores CRUDOS de los bloques A, B, C, D, E — cada uno sobre su
  máximo: A ≤4, B ≤6, C ≤4, D ≤4, E ≤3. Una línea de justificación por bloque.
  Un valor fuera de rango vuelve en `rechazos` (se guarda topeado, pero se
  delata).
- EL DT: LA RED MANDA, LA BASE ES UNA ALARMA. Cada candidato de la agenda
  trae `dt.a` / `dt.b`: el entrenador que tiene nuestra base, con `fuente`
  (`alineacion` = el que se sentó en el banco en el último partido, el más
  fiable; `coachs` = la carrera de la API, que llega meses tarde),
  `edadDias`, `fiable` y una `nota`. Es un punto de partida, no la verdad:
  el 18/09 la base tenía al saliente en 4 de 19 equipos, de 3 a 27 meses
  atrás. La regla, sin excepción:
    1. Buscá en prensa de ESTA semana quién dirige. Si la prensa dice un
       nombre, ES ESE, aunque la base diga otro y aunque `fiable` sea true.
       Escribilo en `dt` con la fuente en `notas.A`; la app marca la
       discrepancia sola (alerta `DT-DISCREPANCIA`) y la base se corrige en
       la próxima corrida. No discutas con la base, no promedies, no dejes el
       bloque A a medias por la duda.
    2. Si la prensa no dice nada y `fiable` es true, tomá el de la base y
       decilo en `notas.A` («según la base, visto en el banco el 14/09»).
    3. Si no podés establecerlo de ninguna de las dos formas, `dt` va como
       `"sin establecer"`, el bloque A queda fuera y lo decís en
       `pendientes`. Ese parte NO entra al aprendizaje (cuarentena
       automática): mejor un caso fuera que un A puntuado sobre un DT que ya
       no está, que mueve el parte diez puntos y dispara o calla T.54 en falso.
- LA FORMA DE `dt` ES `{"nombre": "Diego Simeone", "desde": "2011-12-23"}`
  (el día 01 si solo se sabe el mes) o `{"nombre": "…", "meses": 14}`. La
  antigüedad —insumo de A, F3 y S1— la calcula la app: `meses` declarado
  manda; si no, de `desde` a la fecha del partido; si no, del DT de nuestra
  base cuando el apellido coincide; y si nada de eso, `meses: null`, **nunca
  0** (0 es «recién llegado» y así entraba cada `dt` mandado como texto).
  `nombre` va a secas: una oración de cien caracteres (pasó en el 1549491) se
  rechaza y la fuente va en `notas.A`. Si no sabés quién dirige, el valor
  canónico es `"sin establecer"` —no «desconocido», no vacío, no un guion—.
- Un bloque que la RÚBRICA manda excluir (p. ej. C sin constantes K por
  R-KT.2 en un recién ascendido) va en `excluidos`: `{"C": "motivo"}`. Así el
  máximo baja a 23 y el porcentaje se calcula sobre lo evaluable. Es DISTINTO
  de un bloque que no pudiste puntuar: ese se deja fuera de `bloques` y se
  explica en `pendientes`; nunca lo mandes como 0.
- La tabla F1: 14-16 jugadores con zona (GK/DEF/MID/ATK), rol (TF/TH/ROT/SUP)
  y apps. SIN columna de estado.
- Las bajas y sanciones ya públicas, en `fuera`, con su motivo y su fuente. Y
  a esos mismos jugadores, TAMBIÉN en `plantel` con su zona y su rol: una baja
  que no está en la tabla F1 no pesa en el Impacto Ponderado.
- Las alertas del protocolo que se disparen (T.54, R-KT.2, GK-DOWNGRADE,
  FACTOR-X, COLAPSO EN CASCADA…).
- El matchup H: diagnóstico, razón, el perfil táctico de cada equipo Y los tres
  indicadores `h2a` / `h2b` / `h2c` (verde/ambar/rojo/na) que lo sostienen. Un
  "MATCHUP FAVORABLE" sin los tres es una etiqueta que nadie puede discutir.
- EL REVENTÓN DE LA BURBUJA, ANTES de escribir la lectura SAD y el 1X2:
    GET {base}/fixtures/{fixtureId}            → `local.id` y `visitante.id`
    GET {base}/equipos/{local.id}/burbujas?proximo={fixtureId}
    GET {base}/equipos/{visitante.id}/burbujas?proximo={fixtureId}
  SIEMPRE con `proximo={fixtureId}`: sin él el próximo rival sale del
  calendario del equipo, y un fixture viejo sin marcar lo desvía (al Betis le
  salió un rival que no era el del partido).
  Es una guía CALCULADA de cuándo la K de resultado de cada equipo suele
  volver a cero, calibrada con 171 mil burbujas reales. No es probabilidad y
  no la reemplaces con tu impresión. Mirá `familias.total` (la que manda):
  `riesgo.nivel`, `riesgo.puntos`, `riesgo.confianza`, `riesgo.motivos` y
  `rival.tramo`. Reglas de uso:
    · riesgo MUY ALTO o ALTO con confianza media o alta → NO recomiendes que
      la racha siga. Si tu 1X2 iba por ahí, decilo en la lectura y bajá el
      peso de esa fuente.
    · riesgo BAJO no autoriza nada: es «sin señal de reventón», no «va a
      seguir». Seis de cada diez burbujas revientan igual.
    · la K alta NO es alarma (viene marcada «informativo, la K no puntúa»):
      lo que revienta es el rival que viene frente al nivel con el que ese
      equipo suele caer. Leé el `tramo` del rival.
    · `sin base` = no hay reventones previos de ese signo: no lo uses.
    · confianza baja (DT nuevo, plantel en obra, muestra corta) = la historia
      es de otro equipo; anotalo y no apoyes nada solo en esto.
    · ALERTA DE EXTREMO — NO TE LA PODÉS SALTAR. Si `familias.total.extremo.activo`
      es true en cualquiera de los dos, esa burbuja está en su máximo
      histórico (`extremo.motivos` te dice si es la K o la racha y sobre
      cuántos partidos: «la más alta en N partidos»). El riesgo NO lo cuenta
      —la tasa de reventón no sube con la K— y por eso puede decir BAJO con
      la K en récord: eso pasó en Alavés–Valencia (K de Valencia en −32
      sobre un máximo de 24, «riesgo bajo», 0-1). Reglas duras:
        1. escribí EXTREMO con el N de partidos en `lecturaSad.reventon`
           («B: EXTREMO, K −32 la más baja en 118 partidos; riesgo bajo»);
        2. en `pronostico`, NINGUNA recomendación de carga fuerte ni de
           «apuesta segura» a que esa racha siga; si tu 1X2 va por ahí,
           bajá la confianza declarada y decilo en el falsador;
        3. no la conviertas en lo contrario: no es «va a reventar», es «acá
           no se pone plata grande». El backend agrega la alerta K-EXTREMO
           al parte por su cuenta: si tu lectura no la menciona, se nota.
  Escribí UNA línea por equipo en `lecturaSad.reventon`, por ejemplo:
  «A: muy alto (8), rival mucho más fuerte que su zona de reventón → no
  seguir la racha de A; B: bajo, sin señal». NO copies los números al
  parte: el backend los recalcula al leer y los muestra al lado de tu línea.
- La LECTURA SAD, que es lo que se lee primero cuando ya se vieron los números:
  módulo operativo, 1X2, contexto emocional, dato estructural y la paradoja del
  partido (vacía si no hay).
- La CAJA DE SENSIBILIDAD por equipo: por cada hueco declarado, qué cambiaría si
  el dato fuera otro. Es lo que convierte un "sin dato" en una incertidumbre
  acotada en vez de una excusa.
- El TDE estructurado en `tde.bloques[]`, **uno por equipo** — el índice es
  de un equipo, no del partido, y el del otro en `notas` es prosa que nadie
  puede comprobar—, además del documento en prosa. ANTES de puntuarlo:
    GET {base}/analisis/cowork/tde/{fixtureId}
  trae calculados P1a (input inviolable: sale de μ_partido, prohibido
  derivarlo del gap), F2 (descanso y calendario: «dato del motor o no es
  dato») y F1 (rotación desde las alineaciones ingestadas). Tomalos tal cual;
  F2 solo sube a mano por viaje largo, altitud o calor, y P1a solo baja a 0
  por «necesita ganar». Lo tuyo son los 16 de `noCalculables`.
  Cada bloque lleva `indicadores` en 0 / 0.5 / 1 con TODOS los que puntuaste
  (F1-F4, C1-C3, P1a-P4, S1-S3 y SOB1-SOB3): el IE y el ISE los calcula el
  backend con sus compuertas, y un `ie` suelto se guarda solo como lo que
  llegó. La escala es 0-10 (bandas 3 / 5 / 7), NUNCA 0-100. No mandes
  P(echada) ni riesgo compuesto: están suspendidas. Los niveles
  verde/ámbar/rojo sí los ponés vos: el backend no le inventa umbrales a tu
  escala. DOS CAMPOS, NO UNO: en `ie`/`ise` va el NÚMERO y en
  `ieNivel`/`iseNivel` va la ETIQUETA ("verde" | "ambar" | "rojo"). Diez
  partes llegaron con el número en `ieNivel` y quedaron sin nivel: ahora eso
  vuelve en `rechazos` (y el número se rescata en `ie`). `disciplina43` solo
  va en true si mandás las dos vías (o los indicadores): sin eso se rechaza.
- Los eventos INSTITUCIONALES del timeline en `timelineEventos` (nunca partidos).
- El pronóstico clave por equipo foco en `cadena`: una frase, la que después se
  va a poder declarar acertada o fallada.
- El pronóstico con sus TRES fuentes declaradas en simultáneo (Disciplina 33):
  motor de Regresión al Nivel (sad-analysis), matriz manual y mercado. Si el
  motor no pudo correr, se dice — no se reemplaza con estimación (Disciplina 21).
- Los documentos en prosa (ver punto 5).

NO escribas, porque lo calcula la app y se ignora si llega:
  total · máximo alcanzable · porcentaje · clasificación FORMADO/EN FORMACIÓN/
  SIN FORMACIÓN · Impacto Ponderado · reducción por zona · multiplicador ×1.5
  del arquero · las ramas A y B · alerta F3 · F4 · el nombre de los equipos ·
  la fecha · el calendario de próximos rivales · los resultados del timeline.

Esto no es un recorte de alcance: es que esas cifras ya existen calculadas y
copiarlas solo agrega minutos de escritura y una forma más de equivocarse.

## 5. LOS DOCUMENTOS (markdown, dentro del parte)

Van en `documentos`, cada uno con su `id`. Markdown normal: títulos, listas,
negritas, citas y tablas se pintan bien en la app.

  dtp       diagnóstico táctico (skill diagnostico-tactico): cadena rodante —
            cerrás el partido anterior de cada equipo y abrís el de esta fecha.
            La lectura de alineación va con el XI DE REFERENCIA (última fecha
            jugada, no el plantel), declarado como tal.
  matriz    Matriz de Escenarios Tácticos v2.0. En sesión interactiva el skill
            pide confirmación; acá la autorización ya está dada por este prompt.
            Anotalo: "Matriz ejecutada bajo autorización batch".
  tde       Teorema del Echado. El skill normalmente pregunta por sus
            variables: P1a, F1 y F2 los tomás de GET /analisis/cowork/tde/{id}
            (ver punto 4); el resto buscalo en la web, cargá con fuente lo
            que encuentres, y lo que no aparezca va como `sin dato` + caja de
            sensibilidad Y ADEMÁS entra en `pendientes`. Si el IE o el ISE
            cruzan el borde entre tipologías, activás Disciplina 43 y declarás
            las dos vías con sus ventanas separadas.
  timeline  NO va como documento. Los eventos institucionales van en
            `timelineEventos` (ver punto 7) y la app los funde con los partidos
            que calcula de su base. Mandarlo como HTML lo deja fuera de esa
            fusión y sin el tema de la app: no lo hagas.
  ensayo    cómo puede darse el partido, en prosa de periodista, sin siglas,
            con fundamento técnico. Cierra con probabilidad de marcador y de
            ganador. Es lo primero que se lee: escribilo para eso.

No escribas un CSV de registro ni toques ningún archivo compartido: la
consolidación la hace la app.

## 6. EL PROBLEMA DEL ONCE — LEELO ANTES DE EMPEZAR

Ninguna fuente publica el XI confirmado la noche anterior. El batch corre
con el once pendiente POR DISEÑO, y eso NO es un agujero del parte. En las
ligas que API-Football cubre, el once llega solo por la ingesta y lo cierra el
barrido del punto 8; en las que no (Primera B de Colombia, Primera de Uruguay)
el pantallazo es el procedimiento.

- Regla dura (Disciplina 35): el bloque F no se puntúa sin XI confirmado.
  No lo rellenes con el plantel. No lo estimes.
- Vos preparás la tabla F1 (14-16 jugadores con zona, rol y apps) y las bajas
  públicas. Eso es todo lo que tiene que existir esta noche.
- Las dos ramas del impacto (piso y techo) las calcula la app con los pesos
  del protocolo. NO las escribas.
- La marca "XI NO CONFIRMADO" la pinta la app sola mientras el parte esté en
  `pendiente_xi`. No hace falta que la escribas en ningún lado.

Si contra todo pronóstico SÍ aparece el XI confirmado (rueda de prensa, cuenta
oficial), no lo metas en el parte: depositá el parte normal y después mandá el
once por su endpoint (punto 8), citando dónde lo encontraste en `fuente`.

## 7. DEPOSITAR

  POST {base}/analisis/cowork
  Content-Type: application/json

{
  "fixtureId": 1390233,
  "equipos": {
    "a": {
      "bloques": {"A": 3, "B": 4.5, "C": 2, "D": 3, "E": 2},
      "notas": {"A": "mismo DT hace 14 meses, contrato hasta fin de año",
                "E": "1.62 ppp, 1 derrota en los últimos 6"},
      "dt": {"nombre": "Nombre del DT", "desde": "2025-06-15"},
      "perfil": {"sistema": "4-3-3", "estilo": "presión alta",
                 "fortaleza": "juego asociado por dentro",
                 "vulnerabilidad": "espalda de los laterales"},
      "plantel": [
        {"nombre": "Nombre Apellido", "posicion": "Portero",
         "zona": "GK", "rol": "TF", "apps": "18/20"}
      ],
      "fuera": [{"nombre": "Nombre Apellido", "estado": "baja",
                 "motivo": "lesión muscular — Depor, 10/09"}],
      "factorX": [{"nombre": "Nombre Apellido",
                   "contexto": "fichaje de julio sin minutos; 12 goles en su liga anterior"}],
      "sensibilidad": [{"supuesto": "el central 2 no llega",
                        "efecto": "DEF pasa a zona debilitada y el matchup deja de ser claro"}]
    },
    "b": { "…igual…, y si la rúbrica excluye un bloque:",
           "excluidos": {"C": "R-KT.2: recién ascendido, sin constantes K"} }
  },
  "alertas": [{"codigo": "T.54", "equipo": "b", "tipo": "estructural",
               "detalle": "DT interino desde hace 3 semanas"}],
  "matchup": {"diagnostico": "FAVORABLE", "favorece": "a",
              "razon": "bloque bajo del rival con vida útil ≤65' contra un ataque que llega por fuera",
              "h2a": "verde", "h2b": "verde", "h2c": "ambar"},
  "lecturaSad": {
    "moduloOperativo": "Regresión al Nivel con gap favorable al local; módulo de goles habilitado",
    "unXDos": {"texto": "Local con ventaja estructural; el empate es la cobertura",
               "rangoAmpliado": false},
    "contextoEmocional": "El visitante llega de dos derrotas y con el interino sin margen",
    "datoEstructural": "Núcleo del local intacto hace tres temporadas; el visitante renovó seis titulares",
    "paradoja": "El del mejor EFE es el que más depende de un solo hombre"
  },
  "tde": {
    "bloques": [
      {"equipo": "b",
       "indicadores": {"F1": 0.5, "F2": 1, "F3": 0.5, "F4": 0,
                       "C1": 1, "C2": 0.5, "C3": 0,
                       "P1a": 0.5, "P1b": 1, "P1c": 0, "P2": 0.5, "P3": 0.5, "P4": 0,
                       "S1": 0.5, "S2": 0, "S3": 0.5,
                       "SOB1": 0, "SOB2": 0.5, "SOB3": 0},
       "ieNivel": "ambar", "iseNivel": "verde",
       "tipologia": "repliegue por agotamiento", "ventana": "75-90'",
       "disciplina43": false,
       "vias": [{"nombre": "ECHADA", "indice": 5.8, "ventana": "75-90'",
                 "detalle": "el bloque baja diez metros tras el primer gol en contra"}],
       "falsador": "si sostiene la línea por encima de su área tras el 75', el índice está mal"},
      {"equipo": "a",
       "indicadores": {"…los mismos 19 indicadores, puntuados para ESTE equipo…": 0},
       "ieNivel": "verde", "iseNivel": "ambar",
       "tipologia": "sobreexposición por urgencia", "ventana": "60-75'",
       "vias": [{"nombre": "SOBREEXPOSICION", "indice": 4.7, "ventana": "60-75'",
                 "detalle": "adelanta los dos laterales con el marcador abierto"}],
       "falsador": "si conserva los laterales por detrás de la línea de balón"}
    ]
  },
  "timelineEventos": [
    {"fecha": "2026-03-02", "equipo": "Nombre del club", "tipo": "tecnico",
     "titulo": "Cambio de DT", "detalle": "sale tras 4 fechas sin ganar",
     "destacado": true, "fuente": "Depor"}
  ],
  "timelineNarrativa": "Semestre de curva ascendente para el local; el visitante alterna.",
  "cadena": {
    "a": {"pronostico": "domina por fuera y define antes del 70'"},
    "b": {"pronostico": "aguanta con bloque bajo y busca el contragolpe"}
  },
  "pronostico": {
    "motor": "gap §5 a favor del local (+0.31)",
    "matriz": "52 / 27 / 21",
    "mercado": "1.85 / 3.40 / 4.20 (promedio de 6 casas)",
    "probabilidades": {"local": 52, "empate": 27, "visita": 21},
    "marcador": "2-1",
    "falsador": "si el visitante abre el marcador antes del 20', la lectura de bloque bajo queda fallada"
  },
  "documentos": [
    {"id": "ensayo", "cuerpo": "## La lectura\n\nTexto…"},
    {"id": "dtp", "cuerpo": "…"},
    {"id": "matriz", "cuerpo": "…"},
    {"id": "tde", "cuerpo": "…"}
  ],
  "pendientes": ["XI de los dos equipos",
                 "TDE: no se encontró el dato de minutos del central 2"],
  "fuentes": ["futbolperuano.com", "RPP", "Depor"],
  "descartados": ["1390240 ya se había jugado al llegar (2-0): no se analiza con resultado a la vista"],
  "notas": ""
}

`a` es SIEMPRE el local y `b` el visitante. Si lo invertís, el análisis queda
cruzado y nadie se entera hasta que se juegue.

LEÉ EL RECIBO que devuelve el POST:
- `discrepancias` con contenido = mandaste un equipo que no es el del fixture.
  Verificá el `fixtureId` contra la agenda y volvé a depositar.
- `jugadores` con menos de los que escribiste = a esos les faltaba zona o rol
  y no entraron. Completalos y re-depositá (es idempotente: el último manda).
- `rechazos` con contenido = eso NO entró. Cada uno dice dónde estaba, por qué
  y qué se esperaba. Corrígelo y re-depositá completo. Los tres que más
  salieron el 18/09 y que antes pasaban callados: `tde.bloques[i].ieNivel`
  (mandaste el número donde va la etiqueta), `equipos.{a,b}.dt` (el DT llegó
  sin `desde` ni `meses`: la antigüedad quedó en null) y
  `equipos.{a,b}.dt.nombre` (una oración donde va un nombre).
- `perdido`/`aviso` con contenido = este depósito dejó el parte con MENOS de lo
  que tenía. El POST reemplaza entero: si fue sin querer, re-depositá completo.
- `eventosTimeline` en 0 habiendo mandado eventos = eran de tipo partido y se
  descartaron, o les faltaba fecha o título.
- `conLecturaSad` o `conTde` en false = ese bloque no llegó y la pestaña va a
  salir vacía. Si fue a propósito (sin dato), anotalo en `pendientes`.
- `ladosTde` = de qué equipos quedó índice. Si dice `["a"]` o `["b"]`, el otro
  equipo se quedó sin TDE: el índice es POR EQUIPO y caben los dos.
- `faltan` = bloques ausentes AHORA que se van a cobrar al cerrar el caso
  dentro de 12 h, cuando llenarlos ya sería escribir con el resultado puesto.
  Cada uno dice qué va a costar y cómo se arregla hoy. Leelo siempre.
- `equipos.{a,b}.sinBloques` en true al releer el parte = no entró ni un
  sub-score del EFE. Volvé al punto 4.
- `cadena` vacía = no mandaste pronóstico por equipo y la película del equipo
  no avanzó esta fecha.
- `cadenaIgnorada` con equipos = ese lado YA tenía pronóstico declarado y se
  conserva el primero. Un re-depósito no lo pisa a propósito: cambiarlo
  después sería reescribirlo con más información.

PARA CORREGIR UN PARTE que ya está: GET {base}/analisis/cowork/{fixtureId},
modificá lo que haga falta y volvé a hacer POST con ESE MISMO cuerpo entero.
El POST acepta tal cual la respuesta del GET (lo calculado se ignora en
silencio) y así no se pierde nada de lo que ya había.

## 8. CUANDO LLEGUE EL ONCE

Tres caminos; la app hace la cuenta en los tres, sin costo y sin modelo.

0) EL BARRIDO, que es el que tenés que usar por defecto:
     POST {base}/analisis/cowork/xi/auto
   Cierra el bloque F de TODOS los partes cuya alineación ya esté ingestada.
   Es idempotente y no gasta nada, así que se puede disparar cuantas veces
   haga falta. Seis partidos que arrancan juntos son seis cierres de
   milisegundos: no hay carrera contra el reloj.
   En la respuesta:
     `cerrados`          los que quedaron listos.
     `reemplazados`      lados pegados a mano que ahora tienen la ficha: la
                         ficha manda, no hace falta hacer nada.
     `conConflicto`      el once no casa con la tabla F1: NO se fuerza. Revisá
                         la tabla, no insistas con el mismo once.
     `sinFichaTodavia`   todavía puede cerrar solo. Reintentá más tarde.
     `nuncaVaALlegar`    el partido YA TERMINÓ y esa liga no da alineaciones
                         por API-Football. Ahí reintentar no sirve: esos
                         necesitan el pantallazo a mano, y para esas ligas eso
                         es el procedimiento, no la excepción. `ligasSinOnce`
                         te las junta para que lo veas como patrón.

a) Un partido puntual que ya capturó nuestra ingesta:
     POST {base}/analisis/cowork/{fixtureId}/xi
     {"desdeFicha": true}
   Responde 409 si la ficha todavía no tiene alineaciones. No insistas: no es
   un error tuyo, es que no salió aún.

b) El once que te pasó el usuario (pantallazo de BeSoccer, captura de la
   transmisión, lo que sea). Leelo, escribí los nombres y mandá:
     POST {base}/analisis/cowork/{fixtureId}/xi
     {"a": {"once": ["…", "… 11 nombres …"],
            "banca": ["…"],
            "formacion": "4-3-3",
            "fuente": "pantallazo BeSoccer 14/09 18:40"}}

   Escribí los nombres como estén en el pantallazo; la app los cruza con tu
   tabla F1 tolerando abreviaturas ("A. Campos" casa con "Ángelo Campos").
   Lo que no case vuelve listado en `noReconocidos`: si son muchos, revisá que
   sea el partido correcto antes de volver a mandar.

   Si un apellido se repite en la tabla, la app lo deja sin resolver y lo dice
   en `dudas`. Eso se arregla mandando el nombre completo, no insistiendo.

La respuesta trae el parte recalculado: IP, reducción por zona, F3 y F4 ya
hechos. No los escribas vos.

## 9. REGLAS DURAS

- No inventes alineaciones, lesiones, minutos ni estadísticas. Ante la duda,
  el campo va vacío y el hueco se declara en `pendientes`.
- Dos fuentes que se contradicen (típico: quién dirige al equipo según el acta
  oficial vs la prensa) → documentás LAS DOS y declarás la contradicción en
  `notas`. No la resuelvas en silencio.
- Nada de revisiones con el resultado puesto.
- `timelineEventos` solo acepta `institucional`, `tecnico`, `sancion` e `hito`.
  Un evento de tipo `resultado`, `derrota` o `empate` se descarta al depositar:
  esos los pone la app con el marcador de su propia ingesta.
- Fuentes peruanas de referencia: futbolperuano.com, RPP, Ovación, Líbero,
  Depor, El Comercio.

## 10. AL TERMINAR

Tres líneas, sin adornos: cuántos partidos depositaste (con sus fixtureId),
cuántos quedaron esperando once, y qué se rompió.
```

---

# PROMPT CORTO — "LLEGÓ EL ONCE"

Para cuando le mandás a Cowork un pantallazo de la alineación.

```text
Te paso la alineación de un partido que ya tiene parte depositado.

1. GET  << {base} >>/analisis/cowork/pendientes  → encontrá el fixtureId del
   partido (o usá el que te diga el mensaje) y fijate qué lado falta.
2. Leé el pantallazo y escribí los once nombres tal como aparecen, más la
   banca si se ve, más la formación si se ve.
3. POST << {base} >>/analisis/cowork/{fixtureId}/xi
   {"a": {"once": [...], "banca": [...], "formacion": "...",
          "fuente": "pantallazo <<de dónde>>, <<fecha y hora>>"}}
   (usá "b" si el que falta es el visitante; los dos a la vez también vale)
4. Contame en tres líneas: IP resultante por equipo, si saltó F3, y qué
   nombres quedaron en `noReconocidos` o en `dudas`.

No estimes ningún número: la app calcula el impacto. Si no leés bien un
nombre, decilo — un nombre mal leído es un titular que la app va a contar como
ausente.
```

---

# PROMPT CORTO — "RETOMAR HOY": lo que el batch no subió

Para cuando la corrida nocturna se cortó o se saltó partidos y hay que cubrir
los de hoy que todavía no arrancaron. Mismas reglas del batch (v2.5); cambia
solo cómo se elige la lista.

```text
Vas a cubrir los partidos de HOY que se quedaron sin parte. Reglas del batch
nocturno v2.5 (contrato, sesión limpia por partido, EFE con sus sub-scores,
TDE con indicadores, reventón de la burbuja leído antes del 1X2, tres
fuentes del pronóstico). Nada nuevo, salvo la lista.

ALCANCE: <<todo el padrón / «España» / «Perú» / …>>. Un país o una liga va
TAL CUAL en `liga=`; «todo» deja `liga=` vacío. Si no entendés el alcance,
preguntá y pará: no analices otra cosa. TOPE: <<5>> partes en esta corrida;
lo que sobre queda para la próxima (la agenda lo retoma con `yaHechos`).

0. Anclá la hora real con la herramienta del sistema (America/Lima) y leé
   GET << {base} >>/analisis/cowork/contrato.

1. GET << {base} >>/analisis/cowork/latido
   Decime en una línea `estado`, `depositadosEnLaVentana` y
   `coberturaDeAyer.faltaron`. Es el diagnóstico; no arregla nada.

1b. CERRÁ LO DE AYER ANTES DE ABRIR LO DE HOY.
   GET << {base} >>/analisis/cowork/veredictos/pendientes
   Todo partido que figure TERMINADO con marcador entra, aunque haya
   arrancado hace menos de 12 h. Por cada `pendientes[]`: leé el parte
   (GET /analisis/cowork/{fixtureId}) y escribí el veredicto con las
   reglas del prompt «VALIDAR LO DE AYER» (seleccion ciega salvo que
   hayas mirado el marcador antes, modoEvaluacion PRE, porLado a/b con
   veredicto + queP + leccion + skill). Si `pendientes` viene vacío, leé
   `nota` y `noListados` y decime por qué cada uno no entró: «ya está en
   check» no es un motivo, el motivo es el que trae `porque`.
   Que el once haya llegado y el bloque F esté cerrado NO cierra el caso:
   el caso se cierra con el veredicto, y sin veredicto la lección no existe.

2. GET << {base} >>/analisis/cowork/agenda?limite=<<5>>&liga=<<>>
   NO uses `fecha=`: traería los que ya arrancaron. Sin fecha la agenda es
   «desde ahora y por 24 h»: entran solo los que faltan por jugarse, y
   `porHacer` son los que no tienen parte. La fase de grupos internacional y
   las segundas quedan fuera solas; si el usuario las quiere, `grupos=true` /
   `segundas=true`. Antes de arrancar decime en una línea `ventana`,
   `filtro.ligasQueCasan` y cuántos hay en `porHacer`.
   Trabajá EXACTAMENTE `porHacer`, en ese orden. `yaHechos` no se toca: un
   re-depósito reemplaza el parte entero.
   Un partido que ya se jugó o está en juego NO se analiza aunque falte: un
   parte con el resultado a la vista no calibra nada. Anotalo en el cierre.
   Si `analizar` viene vacío, decime `ventana`, `corte` y `descartados` y
   paramos.

3. Por cada fixtureId de `porHacer`, en su propia sesión:
   - GET /analisis/cowork/tde/{fixtureId} → P1a, F1 y F2 ya calculados.
   - EFE: sub-scores A-E crudos (un bloque que la rúbrica excluye va en
     `excluidos` con motivo; uno que no pudiste puntuar se deja fuera y va a
     `pendientes`; nunca un 0 inventado).
   - Tabla F1 (14-16 con zona/rol/apps) y bajas públicas también en `plantel`.
   - Reventón de la burbuja ANTES del 1X2: GET /fixtures/{fixtureId} te da
     `local.id` y `visitante.id`; GET /equipos/{id}/burbujas?proximo={fixtureId}
     de los dos (siempre con `proximo=`, para que el rival sea ESTE partido).
     Mirá `familias.total.riesgo` (nivel, puntos, confianza, motivos) y
     `familias.total.rival.tramo`. MUY ALTO o ALTO con confianza media o
     alta = no recomendar que esa racha siga (y decirlo en la lectura);
     BAJO no autoriza nada; la K alta no es alarma, el rival sí; `sin base`
     no se usa. Y la ALERTA DE EXTREMO no se salta: si
     `familias.total.extremo.activo` es true, la burbuja está en su máximo
     histórico y aunque el riesgo diga BAJO escribís EXTREMO con el N de
     partidos en `lecturaSad.reventon` y NO recomendás carga fuerte a que
     esa racha siga (bajá la confianza del pronóstico y decilo en el
     falsador). Una línea por equipo en `lecturaSad.reventon`, sin copiar
     números (el backend los recalcula al leer).
   - Alertas, matchup con h2a/h2b/h2c, lectura SAD, sensibilidad.
   - `tde.bloques[]` uno por equipo con `indicadores` 0/0.5/1, escala 0-10.
   - `timelineEventos` solo institucionales; `cadena.a/b.pronostico`;
     `pronostico` con motor + matriz + mercado, probabilidades y falsador.
   - Documentos: ensayo, dtp, matriz, tde.
   Con poco margen hasta el pitazo, lo que NO se recorta: bloques A-E ·
   tabla F1 · bajas · alertas · pronóstico con sus tres fuentes · cadena ·
   TDE con indicadores. El ensayo y el timeline se caen primero y se anotan
   en `pendientes`.

4. POST << {base} >>/analisis/cowork por partido. Leé el recibo:
   `rechazos`, `faltan`, `discrepancias`, `jugadores`, `ladosTde`,
   `cadenaIgnorada`. Si `faltan` trae `cadena`, `tde` o
   `pronostico.probabilidades`, completalo AHORA y re-depositá completo: en
   12 h ya no se puede llenar sin hindsight.

5. Al final, una sola vez: POST << {base} >>/analisis/cowork/xi/auto
   Cierra el bloque F de todo lo que ya tenga alineación ingestada. Decime
   `cerrados`, `conConflicto`, `sinFichaTodavia` y `nuncaVaALlegar`.

6. Cierre en cuatro líneas: fixtureIds depositados, cuáles de `porHacer`
   quedaron sin parte y por qué (ya jugado / sin datos / se acabó el
   tiempo), qué recibos trajeron `rechazos` o `faltan`, y si algo del
   contrato no coincidió con este prompt.
```

---

## Modo emergencia

La sección Análisis mantiene el motor por API plegado detrás de un botón
(`EMERGENCIA · Generar aquí con la API de Claude`). Sirve para un partido que
Cowork no alcanzó a cubrir y que hace falta ya. Cuesta lo de siempre
(`docs/efe-dtp/COSTO_IA.md`) y tarda 1-3 minutos; el chequeo previo sigue
diciendo qué va a costar antes de gastar.

Un parte de Cowork y un EFE por API pueden convivir sobre el mismo partido:
son dos registros distintos y ninguno pisa al otro.

---

# PROMPT CORTO — "VALIDAR LO DE AYER"

Para la corrida de validación, 12 horas después de los partidos.

```text
Vas a cerrar los casos que quedaron abiertos. No analices nada nuevo.

1. GET << {base} >>/analisis/cowork/veredictos/pendientes
   Devuelve un sobre: `pendientes` (lo que hay que cerrar, con su marcador),
   `noListados` (cada parte sin veredicto que NO entró, con el motivo y, si
   está en juego, su minuto y marcador parcial), `criterio`, `ventanaHoras` y
   `sinCerrar`. Si `pendientes` viene vacío, leé `nota` y `noListados` y
   contame qué dijeron: ahí está si hay que esperar, avisar o si no hay nada.
   Un partido que figura TERMINADO con marcador entra aunque haya arrancado
   hace menos de 12 h: a la mañana siguiente, lo de anoche ya está listo.
   Que el once haya llegado y el bloque F esté cerrado NO cierra el caso.

2. Para cada uno, leé el parte (GET /analisis/cowork/{fixtureId}) y compará lo
   que dijiste con lo que pasó. El marcador, el acierto del 1X2, el Brier y la
   ventana del TDE los calcula la app: NO los escribas, leelos de la respuesta
   del POST.

3. POST << {base} >>/analisis/cowork/{fixtureId}/veredicto
   {
     "seleccion": "ciega",
     "modoEvaluacion": "PRE",
     "mancha": "",
     "falsadorCumplido": false,
     "porLado": {
       "a": {"veredicto": "acierto", "queP": "ganó por fuera, como se dijo", "leccion": ""},
       "b": {"veredicto": "fallo",
             "queP": "aguantó el tramo final que se le daba por perdido",
             "leccion": "el bloque bajo entrenado sostiene los 90: no asumir vida útil corta sin dato",
             "skill": "teorema-del-echado",
             "reglaTocada": "escala de P(echada)"}
     }
   }

SOBRE `seleccion` — es el campo que decide si el caso sirve para calibrar:
  ciega            el partido salió de la agenda, se eligió sin saber nada.
                   Es lo normal en este pipeline y es lo que hay que poner.
  por_resultado    lo elegiste porque pasó algo llamativo.
  post_resultado   miraste el marcador ANTES de puntuar.
Si dudás entre ciega y post_resultado, es post_resultado. Un caso mal
declarado como ciego envenena la calibración entera; uno declarado de más solo
se queda sin acreditar.

La regla de la duda vale **cuando había resultado que mirar**. Un parte tocado
con el partido en marcha y 0-0 sigue siendo ciego: no existía marcador que
contaminara nada. Eso no se tapa, se declara en `mancha`.

SOBRE `mancha` — una frase, y vacía casi siempre. Es para el caso ciego que
igual tiene algo que contar: "el parte se reescribió en el minuto 2 con el
partido rodando; el pronóstico quedó intacto", "la alineación llegó por
pantallazo sin sellar". No te salva de declarar bien `seleccion`: si lo que
pasó fue que miraste el marcador, eso es `post_resultado` y ninguna salvedad
lo arregla.

SOBRE `modoEvaluacion`: dice CONTRA QUÉ puntuaste, no cuánto viste.
  PRE    cerraste el caso contra el RESULTADO FINAL. Es lo normal.
  COND   lo cerraste contra un marcador PARCIAL, con el partido rodando: el
         acierto es condicional y podría darse vuelta. No acredita.
Todo veredicto se escribe después del partido y eso no lo vuelve COND. Haber
seguido el partido en vivo tampoco: el pronóstico ya estaba sellado y el
backend no deja pisarlo. Si eso pesa, va en `mancha`, no acá.
Declarar PRE sobre un partido sin terminar devuelve 422: el backend lo
comprueba contra nuestra base.

SOBRE la lección: una frase accionable y sobre el MECANISMO, no sobre el
rival. "Barcos define solo" no sirve; "el favorito con ventaja desde el 42
concede entre el 77 y el 90" sí. Poné `skill` SIEMPRE que la
lección sea de un skill: sin él la lección queda en `sinSkill`, aparte, y no
cuenta para nada. `reglaTocada` solo si podés nombrar la regla concreta
("bloque F · indicador F2", "ventana de 15 minutos") — si no sale del propio
texto de la lección, dejala vacía antes que inventarla.

Lo que la lección puede llegar a mover depende de la población, y eso lo
calcula la app: un caso `ciega`+`PRE` puede sostener un cambio de peso; uno
contaminado solo fija rúbrica. Se ve en `puedeMoverNumeros` en
`GET /analisis/cowork/lecciones`.


Si el POST devuelve `rechazos` con algo dentro, leelo: es un campo que
escribiste mal y que NO se guardó, con la sugerencia de cómo se llama.

Si el POST devuelve `sinPronosticoPrevio` con equipos dentro: ese lado no
tenía pronóstico declarado y su cadena NO recibió veredicto. No lo arregles
re-depositando el parte con un pronóstico nuevo —sería escribirlo con el
resultado puesto—: anotalo y seguí.

Al terminar, tres líneas: cuántos casos cerraste, cuántos acertaron el 1X2, y
cuántas lecciones dejaste con su skill.
```

---

# PROMPT CORTO — CORRIDA DE PRUEBA SOBRE UNA LIGA

Para probar el pipeline sobre unos partidos concretos, sin esperar al batch.
Es la versión mínima: por `ligaId`, tres partidos, sin veredictos ni
`xi/auto`. Para cubrir una liga entera a cualquier hora está el prompt
«LA LIGA X, AHORA», más abajo.

```text
Corrida de prueba del pipeline SAD. Mismas reglas del batch nocturno, pero la
lista de partidos la fijo yo con un filtro, no el padrón de prioridades.

1. GET << {base} >>/analisis/cowork/agenda?ligaId=<<262>>&desdeAhora=true&horas=<<6>>&incluirDescartados=true&limite=<<3>>

   Devuelve los partidos de esa liga que todavía no empezaron, dentro de la
   ventana. Vienen con su `motivo`: si dice "liga grande sin equipo arriba ni
   cambio de DT", es que no habrían entrado al batch por sí solos, y está bien
   —los estoy pidiendo yo—.

   Si `analizar` viene vacío: NO inventes fixtureIds. Decime qué devolvió
   (ventana, filtro, cuántos partidos vio) y paramos ahí.

2. Para cada partido, el pipeline completo del batch nocturno: EFE con su
   rúbrica, tabla F1 sin estado, alertas, matchup con h2a/h2b/h2c, lectura
   SAD, sensibilidad, TDE estructurado, eventos institucionales del timeline,
   cadena, y los documentos en prosa.

   Con poco tiempo hasta el pitazo, el orden de lo que NO se puede recortar:
   bloques A-E · tabla F1 · bajas públicas · alertas · pronóstico con sus tres
   fuentes. El ensayo y el timeline son lo primero que se cae si no llegás, y
   se anota en `pendientes` en vez de escribirse a medias.

3. POST << {base} >>/analisis/cowork  (uno por partido)
   Leé el recibo: `discrepancias`, `jugadores`, `eventosTimeline`, `cadena`.

4. Contame: qué partidos depositaste con su fixtureId, qué quedó en
   `pendientes`, y si algún recibo trajo discrepancias.

El bloque F va congelado: no busques el XI confirmado, que a esta hora no
existe. Cuando salga te paso el pantallazo y lo cerramos por su endpoint.
```

---

# PROMPT CORTO — "LA LIGA X, AHORA"

Para pedir una liga entera a cualquier hora, sin esperar al batch y sin tocar
el padrón de prioridades. A las 07:18 trae lo que se juega desde las 07:18; a
las 14:00, lo que se juega desde las 14:00. Mismas reglas del batch nocturno
v2.5: lo único que cambia es cómo se arma la lista.

Reemplazar lo que está entre `<< >>` antes de mandarlo.

```text
Corrida a pedido sobre UNA liga. Reglas del batch nocturno v2.5 (contrato,
sesión limpia por partido, EFE con sus sub-scores, tabla F1, reventón de la
burbuja leído antes del 1X2, TDE con indicadores, cadena, pronóstico con sus
tres fuentes, "sin dato" es respuesta válida). Nada nuevo salvo la lista.

ALCANCE: << «Perú» / «España» / «Liga MX» / … >>
VENTANA: << 24 >> horas desde este momento (1 a 72; una jornada repartida en
          viernes-domingo necesita 72, la fecha de esta noche 12).
TOPE:    << 5 >> partes en esta corrida.

0. Anclá la hora real con la herramienta del sistema (America/Lima). No
   asumas qué día es. Después:
   GET << {base} >>/analisis/cowork/contrato
   Token acotado en `Authorization: Bearer <token>`. Un 403 significa que ese
   endpoint no es para vos: anotalo y seguí, no cambies de token.

1. LA LISTA:
   GET << {base} >>/analisis/cowork/agenda
       ?liga=<<ALCANCE>>&desdeAhora=true&horas=<<VENTANA>>&limite=<<TOPE>>

   - `liga=` va TAL CUAL, en texto: casa por país o por nombre («España» trae
     LaLiga). NO lo traduzcas a un `ligaId` que no te dieron.
   - Si `filtro.ligasQueCasan` viene VACÍO, esa liga no está en el padrón
     (copas nacionales y amistosos quedan fuera a propósito): decímelo y
     paramos. No la busques por otro lado ni la cambies por otra parecida.
   - Si es una SEGUNDA división, agregá `segundas=true`; si es fase de grupos
     / fase liga de un torneo internacional, `grupos=true`. Sin eso van a
     `descartados` con ese motivo escrito, y ahí se ve.
   - `desdeAhora=true` es lo que hace que esto funcione a cualquier hora:
     devuelve SOLO los partidos que todavía no empezaron. Nunca pases
     `fecha=`: traería también los que ya arrancaron.

   Antes de arrancar decime en una línea: `ventana`,
   `filtro.ligasQueCasan`, cuántos hay en `porHacer`, y `corte.quedanFuera`.

   Trabajá EXACTAMENTE `porHacer`, en ese orden. `yaHechos` NO se toca: un
   re-depósito reemplaza el parte entero.

   Si `analizar` viene vacío: NO inventes fixtureIds. Decime `ventana`,
   `corte` y los `descartados` con su motivo, y paramos. Vacío casi siempre
   quiere decir que esa liga no juega en esta ventana — se arregla subiendo
   `horas`, no cambiando de liga.

   TOPE Y CONTINUACIÓN: el `limite` es el tope de partes de ESTA corrida.
   Dieciséis partes en una sola conversación se cuelgan antes de terminar
   (pasó el 16/09). Si `corte` dice que quedaron partidos fuera, hacé los de
   `porHacer`, cerrá, y avisame: mando el prompt otra vez y la agenda sigue
   donde quedó (`yaHechos` / `porHacer`).

   Esto SIGUE SIENDO SELECCIÓN CIEGA: elegir una liga y una ventana antes del
   pitazo es selección ex ante. Lo dice `notaSeleccion`, y el veredicto se
   escribe con `seleccion: "ciega"` igual. Lo que contaminaría es elegir un
   partido PORQUE pasó algo en él.

2. Por cada fixtureId de `porHacer`, en su propia sesión:
   - GET /analisis/cowork/tde/{fixtureId} → P1a, F1 y F2 ya calculados, y
     `noCalculables` con lo que sigue siendo tuyo.
   - EFE: sub-scores A-E crudos. Un bloque que la rúbrica excluye va en
     `excluidos` con su motivo; uno que no pudiste puntuar se deja fuera y va
     a `pendientes`. Nunca un 0 inventado.
   - Tabla F1 (14-16 nombres con zona/rol/apps) y las bajas públicas también
     en `plantel`, o no pesan en el Impacto Ponderado.
   - Reventón ANTES del 1X2: GET /fixtures/{fixtureId} da `local.id` y
     `visitante.id`; GET /equipos/{id}/burbujas?proximo={fixtureId} de los
     dos, SIEMPRE con `proximo=`. Mirá `familias.total.riesgo` y
     `familias.total.rival.tramo`; si `familias.total.extremo.activo` es
     true, escribí EXTREMO con su N y no recomiendes carga fuerte a que esa
     racha siga. Una línea por equipo en `lecturaSad.reventon`, sin copiar
     números: el backend los recalcula al leer.
   - Alertas, matchup con h2a/h2b/h2c, lectura SAD, sensibilidad.
   - `tde.bloques[]` uno por equipo, con `indicadores` 0/0.5/1 y el nivel en
     `ieNivel`/`iseNivel` (etiqueta) y el número en `ie`/`ise`.
   - `timelineEventos` solo institucionales; `cadena.a/b.pronostico`;
     `pronostico` con motor + matriz + mercado, probabilidades y falsador.
   - Documentos: ensayo, dtp, matriz, tde.

   Con poco margen hasta el pitazo, lo que NO se recorta: bloques A-E · tabla
   F1 · bajas · alertas · pronóstico con sus tres fuentes · cadena · TDE con
   indicadores. El ensayo y el timeline se caen primero y se anotan en
   `pendientes`.

   Un partido que ya arrancó no se analiza aunque esté en la lista: un parte
   con el resultado a la vista no calibra nada. Anotalo en el cierre.

3. POST << {base} >>/analisis/cowork por partido. Leé el recibo: `rechazos`,
   `faltan`, `discrepancias`, `jugadores`, `ladosTde`, `cadenaIgnorada`. Si
   `faltan` trae `cadena`, `tde` o `pronostico.probabilidades`, completalo
   AHORA y re-depositá completo: después del pitazo ya no se puede llenar sin
   hindsight.

4. Al final, una sola vez: POST << {base} >>/analisis/cowork/xi/auto
   Cierra el bloque F de todo lo que ya tenga alineación ingestada. Decime
   `cerrados`, `conConflicto`, `sinFichaTodavia` y `nuncaVaALlegar`.

5. Cierre en cuatro líneas: fixtureIds depositados, cuáles de `porHacer`
   quedaron sin parte y por qué (ya jugado / sin datos / se acabó el tope),
   qué recibos trajeron `rechazos` o `faltan`, y cuántos partidos de la liga
   quedaron fuera por el `limite` (para saber si hay que mandar otra vuelta).
```

**Si además querés cerrar lo de ayer en la misma corrida**, mandá primero el
prompt «VALIDAR LO DE AYER» y después este: son dos trabajos distintos y
mezclarlos en una conversación es lo que la deja sin tokens a mitad de camino.
