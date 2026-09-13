# El bucle de aprendizaje — diseño, todavía sin construir

> **Estado: fase B HECHA (13.09.2026).** El veredicto a las 12 h está
> construido y en la app. Las fases C, D y A siguen planificadas. Cada fase se
> marca aquí al construirse.

## Lo que se quiere, en una frase

Que Cowork **mire lo que ya dijo antes de analizar**, que **valide su propio
pronóstico 12 horas después del partido**, que **deje escrito qué aprendió
cuando falla**, y que cada tantos fallos **pida permiso** para convertir esas
lecciones en una versión nueva de un skill.

Cuatro piezas, en ese orden:

```
  A. ANTECEDENTES     Cowork lee lo que dijo de estos equipos → escribe menos      PENDIENTE
  B. VEREDICTO 12h    ¿acertó? lo objetivo lo calcula la app; el juicio lo escribe   HECHA
  C. LECCIONES        lo aprendido se acumula por skill, con su población declarada  PENDIENTE
  D. REVISIÓN         cada N fallos la app arma el dossier y el usuario autoriza     PENDIENTE
```

---

## La disciplina que el bucle NO puede romper

Esto va primero porque es lo que hace que el resto valga algo. Los skills ya
traen su propia regla, y coinciden:

> `teorema-del-echado` · CALIBRACION.md
> *"Hay dos poblaciones de RETRO. Los cuatro sembrados fueron elegidos porque
> hubo echada; los reconstruidos por fecha completa son ciegos al resultado.
> Mezclarlos infla la tasa de echada de 11% a 31%, y ese sesgo es el que
> sostenía la escala."*

> `diagnostico-tactico` · registro de la cadena
> *"Los casos contaminados fijan rúbrica pero **no acreditan**."*

De ahí salen cinco invariantes para cualquier cosa que construyamos:

1. **Toda fila lleva su `seleccion`**: `ciega` (el partido se eligió antes de
   saber nada), `por_resultado` (se eligió porque pasó algo) o
   `post_resultado` (se puntuó con el marcador ya a la vista). El parte de
   Cowork nace ciego —se elige de la agenda, la noche anterior— y eso es
   justamente lo que lo hace valioso: **es la primera vez que el sistema
   produce casos ciegos en volumen y sin esfuerzo**.
2. **Solo la población ciega calcula métricas.** Las otras dos se guardan, se
   muestran y se excluyen del acierto y del Brier. Un panel que mezcle las
   tres miente.
3. **`modo_evaluacion` PRE o COND.** Solo PRE acredita validación predictiva.
   Si el veredicto se escribió con el partido en curso y el marcador puesto,
   es COND y se declara.
4. **Sin pronóstico previo no hay veredicto.** Es la regla anti-hindsight que
   `cadena_dtp` ya implementa (`guardar_cadena` nunca pisa una apertura
   existente). El bucle la hereda entera.
5. **La app no mueve un peso jamás.** Acumula, cuenta y presenta. Que un peso
   del IE cambie es una decisión del usuario sobre el skill, con el listón de
   evidencia del propio skill (el TDE pide N ≥ 5 ciegos cerrados).

### El matiz sobre "cada 4 partidos fallados"

Cuatro fallos es un buen disparador para **abrir la revisión**: junta material
suficiente para que mirarlo valga la pena. No es un permiso para mover nada.
El TDE dice explícitamente "ningún peso tocado" mientras no haya N ≥ 5 casos
**ciegos y cerrados**, y cuatro fallos pueden ser cuatro casos contaminados.

Así que el dossier de la fase D muestra **dos cifras separadas**, nunca una:

- *"4 fallos acumulados"* → por eso te estoy escribiendo.
- *"de los cuales 2 son ciegos y cerrados; el skill pide 5"* → por eso todavía
  no se toca la escala.

Confundirlas es el error que este documento existe para evitar.

---

## Qué existe ya y qué falta

| Pieza | Estado hoy | Qué falta |
|---|---|---|
| Pronóstico declarado pre-partido | ✅ `parte_cowork` + `cadena_dtp.registro.pronostico_clave` | — |
| Marcador final del partido | ✅ `fixtures` (ingesta) | — |
| Cierre del eslabón (qué pasó, veredicto, lección) | ⚠️ el hueco existe en `cadena_dtp`, **nadie lo escribe** | endpoint + quien lo llame |
| Casos de validación del EFE | ⚠️ tabla `casos_validacion` en efe.db, **vacía** | poblarla |
| Registro del TDE | ❌ vive en el `.csv` del skill, fuera de la app | tabla propia |
| Casos del `sad-analysis` | ❌ `references/casos_referencia.md`, a mano | — |
| Métricas de acierto / Brier | ❌ | calcularlas (es aritmética: va en el backend) |
| Pantalla de aprendizaje | ❌ | sección nueva |

La buena noticia: **la mitad del andamiaje ya está puesto** y quedó puesto por
razones independientes. `cadena_dtp` tiene el campo `registro` con
`{pronostico_clave, que_paso, veredicto, leccion}` exactamente, y su regla
anti-hindsight ya funciona.

---

## A · Antecedentes: que Cowork no reescriba lo que ya sabe

**Problema.** Cowork analiza Alianza vs Cristal hoy sin recordar que analizó a
Alianza hace dos fechas, que dijo "se echa entre el 75 y el 90" y que acertó.
Vuelve a investigar todo desde cero: tiempo y contexto tirados.

**Propuesta.** Un endpoint que devuelva, para los dos equipos del partido, lo
que el sistema ya dijo y cómo salió:

```
GET /analisis/cowork/antecedentes/{fixtureId}
```

```jsonc
{
  "a": {
    "equipo": "Alianza Lima",
    "partes": [                       // los últimos N, del más reciente atrás
      {"fixtureId": 123, "fecha": "2026-09-06", "rival": "Melgar",
       "clasificacion": "FORMADO", "porcentaje": 74,
       "pronostico": "domina por fuera y define antes del 70'",
       "veredicto": "fallo", "queP": "0-0, no generó por fuera",
       "leccion": "el bloque bajo de Melgar no es improvisado: vida útil 90'",
       "seleccion": "ciega", "tde": {"ie": 58, "acerto": false}}
    ],
    "aciertoCiego": {"n": 6, "acertados": 4, "brier": 0.19},
    "leccionesVigentes": ["…las lecciones sin aplicar que le tocan a este equipo…"]
  },
  "b": { … }
}
```

**Qué gana el prompt:** un paso nuevo antes del análisis —"lee tus
antecedentes"— y una orden explícita: *lo que ya dijiste y sigue siendo
cierto, no lo vuelvas a investigar; cítalo. Lo que fallaste, corrígelo y di
por qué.*

**Lo que NO debe pasar:** que los antecedentes contaminen la ceguera. Los
antecedentes son de **partidos anteriores ya cerrados**, nunca del partido que
se está analizando. Eso mantiene el caso nuevo en población `ciega`.

---

## B · El veredicto a las 12 horas

**Quién hace qué.** La misma regla de siempre (`docs/efe-dtp/COSTO_IA.md`): lo
que se puede calcular, se calcula.

| Lo calcula la app | Lo escribe Cowork |
|---|---|
| marcador final, ganador real | por qué falló |
| ¿acertó el 1X2 declarado? | qué mecanismo no vio |
| ¿acertó el marcador exacto? | la lección, en una frase accionable |
| error de la probabilidad (Brier por caso) | a qué skill le toca la lección |
| ¿el gol del tramo final cayó en la ventana del TDE? | si el caso es `ciego` o está contaminado |
| los goles con su minuto y su lado (la evidencia) | **si se cumplió el falsador** |

**Corrección sobre la primera versión de este documento:** aquí decía que el
falsador lo verificaría el backend. Al construirlo quedó claro que no: el
falsador es prosa libre y un verificador que acierte el 80% de las veces es
peor que no tenerlo, porque nadie sabría de cuál 20% desconfiar. Lo que la app
hace es **servir la evidencia** con la que se comprueba —los goles con su
minuto y su lado— y dejar que Cowork declare `falsadorCumplido`.

Lo que sí se comprueba solo es **la ventana del TDE**, y por una razón
concreta: `"75-90'"` son dos números y un gol tiene un minuto. Se cuentan solo
los goles CONTRA el equipo evaluado —la echada se observa en lo que recibe— y
si la ficha de eventos no está capturada, `golEnVentana` vuelve `null` en vez
de `false`: no comprobable no es lo mismo que no ocurrido.

**Contrato propuesto:**

```
GET  /analisis/cowork/veredictos/pendientes
     → partidos con parte, terminados hace >12h y sin veredicto.
       Es lo que dispara la corrida de Cowork: no hace falta que nadie
       se acuerde.

POST /analisis/cowork/{fixtureId}/veredicto
{
  "seleccion": "ciega",
  "modoEvaluacion": "PRE",
  "porLado": {
    "a": {"veredicto": "fallo", "queP": "…", "leccion": "…",
          "skill": "teorema-del-echado"},
    "b": {"veredicto": "acierto", "queP": "…", "leccion": ""}
  },
  "notas": ""
}
→ devuelve el veredicto CON la parte calculada ya rellena, para que Cowork
  vea el marcador y el Brier que le salieron sin tener que pedirlos.
```

El veredicto entra en `cadena_dtp.registro` (el hueco que ya existe). La
lección viaja dentro del veredicto con su `skill`; la fase C la indexará desde
ahí en vez de pedir una tabla a medio construir hoy.

**Construido así** (`backend/analisis/veredicto.py` + `parte.py`):

- El objetivo se **recalcula en cada lectura**, nunca se sella. Si la ingesta
  corrige un marcador o llega la ficha de eventos que faltaba, la próxima
  lectura trae el cálculo bueno sin que nadie reescriba el juicio.
- El Brier es de **tres resultados** (Σ(pᵢ−oᵢ)², 0 perfecto, 2 máximo) y lo
  dice en su propio campo `escala`. El objetivo `< 0.20` del TDE es un Brier
  **binario**: no están en la misma escala y ponerlos en la misma tabla sería
  un error de lectura.
- Un reparto que no suma 100 se normaliza. Un 1X2 con dos selecciones
  empatadas en el máximo **no cuenta acierto**: se declara en `nota` en vez de
  desempatarse a ojo.
- Un marcador de un partido en curso se sirve igual (para eso existe `COND`)
  pero viene marcado `terminado: false`.

**Un bug que el diseño predijo y los tests destaparon:** re-depositar el parte
después de cerrar el caso borraba el veredicto de la cadena, porque la
apertura escribía un registro vacío encima. Ahora el re-depósito conserva el
veredicto **y** el pronóstico ya declarado, y delata en `cadenaIgnorada` que
llegó uno distinto. Es exactamente el hindsight que la fase B existe para
impedir, entrando por la puerta de atrás.

**Cuidado con el orden.** Si Cowork escribe el veredicto *antes* de consultar
el marcador, el caso es PRE. Si consulta el marcador y después puntúa, es
`post_resultado` y no acredita. El endpoint no puede saberlo solo: **lo
declara Cowork y el prompt tiene que decirlo con todas las letras.**

---

## C · Las lecciones, acumuladas por skill

Tabla nueva en `efe.db` (la capa de análisis sigue siendo la única que escribe
ahí):

```sql
CREATE TABLE lecciones (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill TEXT NOT NULL,            -- teorema-del-echado, efe-clasificador, …
    fixture_id INTEGER,
    equipo TEXT,
    fecha TEXT,
    veredicto TEXT,                 -- acierto | parcial | fallo
    seleccion TEXT,                 -- ciega | por_resultado | post_resultado
    modo_evaluacion TEXT,           -- PRE | COND
    que_fallo TEXT,
    leccion TEXT NOT NULL,
    regla_tocada TEXT,              -- "escala de P(echada)", "bloque B6", …
    estado TEXT DEFAULT 'pendiente',-- pendiente | en_revision | aplicada | descartada
    aplicada_en TEXT,               -- versión del skill donde entró
    creado_en TEXT NOT NULL
);
```

`estado` es lo que evita el bucle infinito: una lección aplicada deja de
contar para el disparador y queda de historia.

```
GET  /analisis/cowork/lecciones?skill=&estado=
POST /analisis/cowork/lecciones/{id}   → cambiar estado (lo hace el usuario)
```

**En el frontend:** una sección **Aprendizaje** con, por skill:

- tasa de acierto **sobre la población ciega**, con el `n` a la vista y las
  otras poblaciones contadas aparte (nunca sumadas);
- el Brier cuando haya probabilidades declaradas, con su objetivo del skill;
- las lecciones pendientes, con el partido del que salieron;
- y un semáforo honesto: *"2 ciegos cerrados · el skill pide 5"*.

Y en la pantalla del partido, el eslabón cerrado: pronóstico → qué pasó →
veredicto → lección. Eso ya sabe pintarlo `DtpPizarra`.

---

## D · La revisión: del montón de lecciones al `.zip`

**Disparador:** 4 partidos fallados con lección pendiente para un mismo skill.
La app lo detecta y lo marca; **no** escribe nada ni genera nada.

**Dossier** (`GET /analisis/cowork/revision/{skill}`): las lecciones
pendientes, los casos con su población, las métricas ciegas frente al listón
del propio skill, y qué regla concreta toca cada lección.

**Flujo, con el usuario en el medio:**

```
  app  → "4 fallos en teorema-del-echado (2 ciegos cerrados; el skill pide 5)"
  vos  → abrís el dossier y decidís
  vos  → "autorizado, armá la versión nueva"
  Cowork → toma el skill vigente + el dossier, redacta el diff, arma el .zip
  vos  → lo instalás en la cuenta
  app  → marca esas lecciones `aplicada` con la versión donde entraron
```

Tres cosas que **no** van a pasar, y conviene que estén escritas:

- La app no genera el `.zip` sola ni por un cron.
- Cowork no toca su propio skill: propone, y hasta la autorización el archivo
  no se mueve.
- Una lección de un caso contaminado puede **fijar rúbrica** (aclarar cómo se
  aplica una regla) pero **no mueve un número**. Esa distinción la lleva el
  dossier, no el criterio de quien lo lea ese día.

---

## Orden sugerido

| Fase | Qué desbloquea | Tamaño |
|---|---|---|
| **B** · veredicto + cálculo objetivo | es el que genera el dato; sin él las demás no tienen de qué vivir | mediano |
| **C** · lecciones + pantalla | hace visible lo acumulado y cierra la cadena en la pantalla de Equipo | mediano |
| **A** · antecedentes | ahorra tiempo de Cowork; necesita que B lleve un tiempo corriendo para tener qué mostrar | pequeño |
| **D** · dossier de revisión | lo último: sin lecciones acumuladas no hay nada que revisar | pequeño |

Empezar por B tiene una ventaja concreta: **desde el primer partido validado
el sistema empieza a acumular casos ciegos**, que es justo lo que a los skills
les falta. Aunque las fases C y D tarden, el dato no se pierde.

## Lo que queda por decidir

- **El timeline no tiene registro propio.** ¿Se le mide algo (si los eventos
  institucionales que trajo eran ciertos y relevantes) o se acepta que es un
  skill de contexto y no de pronóstico? Se inclina a lo segundo.
- **Qué es "acierto" para el EFE.** El EFE no pronostica un resultado:
  clasifica un estado. Su validación es la del skill (el caso numerado que
  ata una corrección a un partido), no un acierto/fallo de marcador. Meterlo
  en la misma tasa que el 1X2 sería comparar cosas distintas.
- **Las 12 horas.** Con partidos de noche, 12h cae a la mañana siguiente y
  está bien. Con un partido de mediodía cae de madrugada. ¿Se fija una hora
  del día en vez de un delta? La lista de pendientes lo resuelve igual: lo que
  no se validó hoy sigue ahí mañana.
