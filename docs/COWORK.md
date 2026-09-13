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
| bloque H · matchup | diagnóstico, razón, perfiles y `h2a/h2b/h2c` | pestaña **Matchup** |
| lectura SAD | módulo operativo, 1X2, contexto, dato estructural, paradoja | pestaña **Lectura SAD** |
| caja de sensibilidad | `sensibilidad` por equipo | pestaña **Lectura SAD** |
| `sad-analysis` | las tres fuentes de probabilidad + falsador | pestaña **Lectura SAD** |
| `teorema-del-echado` | `tde`: IE, ISE, tipología, ventana, vías | pestaña **Teorema del Echado** |
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
| GET | `/analisis/cowork/agenda?fecha=&limite=` | los partidos del día por prioridad, con motivo |
| POST | `/analisis/cowork` | depositar el parte (idempotente por `fixtureId`) |
| GET | `/analisis/cowork/{fixtureId}` | leerlo con todo lo calculable ya calculado |
| POST | `/analisis/cowork/{fixtureId}/xi` | llega el once → se cierra el bloque F |
| GET | `/analisis/cowork/pendientes` | qué partes siguen esperando once |
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

El paso 1 del batch era, antes, que el modelo dedujera qué partido importaba.
Ahora lo resuelve `agenda()` con el criterio numérico del protocolo:

| Prioridad | Criterio | De dónde sale |
|---|---|---|
| 1 | Liga 1 Perú | país + nombre de la liga |
| 2 | clásico / derbi | `venue_city` compartida (**parcial**: solo derbis de ciudad) |
| 3 | copa internacional | nombre del torneo |
| 4 | liga grande con equipo en zona alta o en crisis | tabla + racha + cambio de DT |
| 5 | choque del top 6 europeo o partido con el líder | tabla |
| 0 | descartado | y viaja **con su motivo**, para poder auditarlo |

`CLÁSICO` es el que queda a medias, igual que en el bloque G: una rivalidad
nacional sin vecindad geográfica (Alianza–Cienciano) no sale de nuestros datos
y puede caer entre los descartados. Está declarado en la respuesta.

Ojo con el efecto práctico de la fila 4: **una jornada de Liga MX o de la Liga
Profesional en la que ningún equipo esté en zona de clasificación ni venga de
un cambio de DT sale entera como descartada.** Es el filtro haciendo su
trabajo —no se pueden analizar todas—, pero hay que saberlo antes de apuntar
el batch a una liga concreta y encontrarse la lista vacía.

### Los mandos manuales

Para apuntar el batch a mano (probar una liga, cubrir lo que queda de esta
noche) sin tocar el padrón:

| Parámetro | Qué hace |
|---|---|
| `ligaId=262` | solo esa liga |
| `desdeAhora=true&horas=6` | ventana rodante desde este momento, no el día natural |
| `incluirDescartados=true` | los de prioridad 0 entran al final, **con su motivo** |

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
| los goles con su minuto y su lado | si el falsador se cumplió |

Dos fronteras que conviene entender, porque explican por qué el reparto es ese
y no otro:

- **El falsador no lo verifica el backend.** Es prosa, y verificar prosa
  arbitraria con un 80% de acierto sería peor que no hacerlo: nadie sabría de
  cuál 20% desconfiar. Lo que la app hace es servir la evidencia con la que se
  comprueba —los goles con minuto y lado— y dejar que Cowork declare.
- **La ventana del TDE sí se comprueba**, porque "75-90'" son dos números y un
  gol tiene un minuto. Se cuentan solo los goles CONTRA el equipo evaluado: la
  echada se observa en lo que recibe, no en lo que hace.

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

`modoEvaluacion` es `PRE` si el veredicto se redactó sin mirar el marcador y
`COND` si se escribió con el partido en marcha o el resultado delante. Solo
`ciega` + `PRE` acredita.

### Anti-hindsight

Sin pronóstico previo declarado, **la cadena del equipo no recibe veredicto**.
El caso se guarda igual y los equipos afectados vuelven en
`sinPronosticoPrevio`. Un juicio sobre algo que nunca se declaró no es
auditable: es una opinión escrita después.

Por lo mismo, re-depositar el parte después del partido **no cambia el
pronóstico ya declarado ni borra el veredicto ya escrito**. Si mandás otro
pronóstico, se conserva el primero y el recibo lo delata en `cadenaIgnorada`.

---

# PROMPT COWORK — SAD BATCH NOCTURNO v2.1

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

## 2. QUÉ PARTIDOS (0 deducción: lo decide la base)

  GET {base}/analisis/cowork/agenda?limite=<<4>>

Devuelve `analizar` (los que tocan, ya ordenados por prioridad y con su
`fixtureId`), `enEspera` y `descartados` con su motivo. Usá `analizar` tal
cual. No re-ordenes, no agregues partidos por tu cuenta.

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

Escribís vos (es juicio, no se puede calcular):
- Los sub-scores CRUDOS de los bloques A, B, C, D, E — cada uno sobre su
  máximo: A ≤4, B ≤6, C ≤4, D ≤4, E ≤3. Una línea de justificación por bloque.
- La tabla F1: 14-16 jugadores con zona (GK/DEF/MID/ATK), rol (TF/TH/ROT/SUP)
  y apps. SIN columna de estado.
- Las bajas y sanciones ya públicas, en `fuera`, con su motivo y su fuente.
- Las alertas del protocolo que se disparen (T.54, R-KT.2, GK-DOWNGRADE,
  FACTOR-X, COLAPSO EN CASCADA…).
- El matchup H: diagnóstico, razón, el perfil táctico de cada equipo Y los tres
  indicadores `h2a` / `h2b` / `h2c` (verde/ambar/rojo/na) que lo sostienen. Un
  "MATCHUP FAVORABLE" sin los tres es una etiqueta que nadie puede discutir.
- La LECTURA SAD, que es lo que se lee primero cuando ya se vieron los números:
  módulo operativo, 1X2, contexto emocional, dato estructural y la paradoja del
  partido (vacía si no hay).
- La CAJA DE SENSIBILIDAD por equipo: por cada hueco declarado, qué cambiaría si
  el dato fuera otro. Es lo que convierte un "sin dato" en una incertidumbre
  acotada en vez de una excusa.
- El TDE estructurado en `tde` (IE, ISE, tipología, ventana, vías) además del
  documento en prosa. Los niveles verde/ámbar/rojo los ponés vos: el backend no
  le inventa umbrales a tu escala.
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
            variables: buscá en la web las que pueda, cargá con fuente lo que
            encuentres, y lo que no aparezca va como `sin dato` + caja de
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

Ninguna fuente peruana publica el XI confirmado la noche anterior. El batch
corre con el once pendiente POR DISEÑO, y eso NO es un agujero del parte:

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
      "dt": {"nombre": "Nombre del DT", "meses": 14},
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
    "b": { "…igual…" }
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
    "ie": 58, "ieNivel": "ambar", "ise": 31, "iseNivel": "verde", "equipo": "b",
    "tipologia": "repliegue por agotamiento", "ventana": "75-90'",
    "disciplina43": false,
    "vias": [{"nombre": "echada", "indice": 58, "ventana": "75-90'",
              "detalle": "el bloque baja diez metros tras el primer gol en contra"}],
    "falsador": "si sostiene la línea por encima de su área tras el 75', el índice está mal"
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
  "descartados": ["Liga MX: Pachuca vs Necaxa, ninguno en zona de clasificación"],
  "notas": ""
}

`a` es SIEMPRE el local y `b` el visitante. Si lo invertís, el análisis queda
cruzado y nadie se entera hasta que se juegue.

LEÉ EL RECIBO que devuelve el POST:
- `discrepancias` con contenido = mandaste un equipo que no es el del fixture.
  Verificá el `fixtureId` contra la agenda y volvé a depositar.
- `jugadores` con menos de los que escribiste = a esos les faltaba zona o rol
  y no entraron. Completalos y re-depositá (es idempotente: el último manda).
- `eventosTimeline` en 0 habiendo mandado eventos = eran de tipo partido y se
  descartaron, o les faltaba fecha o título.
- `conLecturaSad` o `conTde` en false = ese bloque no llegó y la pestaña va a
  salir vacía. Si fue a propósito (sin dato), anotalo en `pendientes`.
- `cadena` vacía = no mandaste pronóstico por equipo y la película del equipo
  no avanzó esta fecha.

## 8. CUANDO LLEGUE EL ONCE

Dos caminos; la app hace la cuenta en los dos, sin costo.

a) Lo que ya capturó nuestra ingesta de API-Football:
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
   Devuelve los partidos con parte depositado, ya jugados y sin veredicto,
   con su marcador. Si viene vacío, decilo y terminá.

2. Para cada uno, leé el parte (GET /analisis/cowork/{fixtureId}) y compará lo
   que dijiste con lo que pasó. El marcador, el acierto del 1X2, el Brier y la
   ventana del TDE los calcula la app: NO los escribas, leelos de la respuesta
   del POST.

3. POST << {base} >>/analisis/cowork/{fixtureId}/veredicto
   {
     "seleccion": "ciega",
     "modoEvaluacion": "PRE",
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

SOBRE `modoEvaluacion`: PRE si escribiste el juicio sin el marcador delante,
COND si lo escribiste con el partido en marcha o el resultado a la vista.

SOBRE la lección: una frase accionable y sobre el MECANISMO, no sobre el
rival. "Barcos define solo" no sirve; "el favorito con ventaja desde el 42
concede entre el 77 y el 90" sí. Poné `skill` solo si tenés claro a cuál le
toca, y `reglaTocada` solo si podés nombrar la regla concreta.

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
