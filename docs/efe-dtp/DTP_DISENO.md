# DTP — diseño de implementación

El protocolo NO se inventa aquí: ya está en
`backend/analisis/prompts/SYSTEM_PROMPT_SAD_API.md` (modos `dtp_apertura` /
`dtp_completo`, esquema DTP y los seis módulos). Este documento decide **cómo
se conecta a esta app**: qué dato necesita cada módulo, de dónde sale, qué
falta hoy y en qué orden se construye.

Regla que gobierna todo el diseño, heredada del EFE: **el dato duro sale de
NUESTRA base; el modelo razona, no investiga.** Cada campo que el DTP tenga
que buscar en la web son 1-2 búsquedas y ahí se va el dinero.

---

## 1. Qué exige cada módulo y qué hay hoy

`DTP(N) = CIERRE de N−1 (M4+M5) + APERTURA de N (M1+M2+M3+M6)`.

| Módulo | Dato que exige | Fuente natural | Estado hoy |
|---|---|---|---|
| **M1** XI como declaración | XI + formación del partido N y del N−1 del mismo equipo, para leer *cambios_vs_anterior* y *roles_reasignados* | `fixtures/lineups` | ❌ se pide en el momento del EFE y se guarda como **texto** en la despensa; no hay histórico ni estructura |
| **M2** duelos por carril | posición de cada titular **en el campo** (carril izquierda/centro/derecha) de ambos equipos | `fixtures/lineups` → `player.grid` (`fila:columna`) | ❌ el `grid` no se guarda; sin él, "duelos por carril" sería inventado |
| **M3** plan por fases | nada nuevo: se deriva de M1+M2 + contexto EFE | — | ✅ |
| **M4** autopsia de goles | goles del partido N−1 con **minuto, autor, asistente, vía** y la secuencia | `fixtures/events` | ❌ `fixture_eventos` solo tiene lo que el ciclo EN VIVO vio en directo; un partido no seguido minuto a minuto no tiene ni un gol |
| **M5** contraste con el pronóstico | la **apertura guardada antes** del partido N−1 | `cadena_dtp.apertura_json` | ❌ la tabla existe y nadie la escribe |
| **M6** competitivo/rotación/fatiga | XI de N−1 vs XI de N *de la misma competición*, días de descanso, ausencias | lineups + `fixtures` (fechas) + capa de jugadores | ⚠️ parcial: fechas y ausencias sí, XI comparado no |

Complemento útil pero no bloqueante: **posesión, tiros, córners, xG por
partido** (`fixtures/statistics`) — sostiene el *peligro_real* de M5 con
números en vez de impresiones. Hoy: ❌ nada.

**Conclusión: tres de los seis módulos no tienen materia prima.** No es un
problema de prompt.

---

## 2. Fase A — los datos (sin LLM) · HECHA

Tres tablas nuevas en `sad.db`, propiedad de `backend/ingesta/` como el resto.

```sql
CREATE TABLE alineaciones (            -- fixtures/lineups
    fixture_id INTEGER NOT NULL,
    team_id    INTEGER NOT NULL,
    formacion  TEXT,                   -- "4-2-3-1"
    entrenador TEXT,
    player_id  INTEGER,
    jugador    TEXT,
    numero     INTEGER,
    posicion   TEXT,                   -- G|D|M|F de la API
    grid       TEXT,                   -- "fila:columna" → EL CARRIL (M2)
    titular    INTEGER NOT NULL,       -- 1 XI · 0 banco
    PRIMARY KEY (fixture_id, team_id, player_id)
);

CREATE TABLE fixture_stats (           -- fixtures/statistics (formato largo:
    fixture_id INTEGER NOT NULL,       -- la API añade y quita métricas sin avisar)
    team_id    INTEGER NOT NULL,
    clave      TEXT NOT NULL,          -- "Ball Possession", "expected_goals"…
    valor      TEXT,
    PRIMARY KEY (fixture_id, team_id, clave)
);
```

y `fixture_eventos` (ya existía) gana `extra`, `jugador_id`, `asistente` y
`asistente_id` — no distinguía el minuto añadido ni quién asistió, y M4 los
necesita. La migración es en caliente (`ALTER TABLE` si falta la columna): las
DBs ya desplegadas no hay que recrearlas. Su guardado pasó a ser **compartido**
con el ciclo en vivo, para que lo capturado en directo y lo capturado después
del partido tengan exactamente las mismas columnas.

**Quién los llena.** Un módulo nuevo `backend/ingesta/ficha_partido.py`, con
la misma disciplina que el resto de la ingesta:

- objetivo: los partidos **terminados** de los equipos que tienen un fixture
  NS en las próximas 48 h y que aún no tengan ficha;
- por partido: 3 requests (`lineups`, `events`, `statistics`);
- **tope y orden explícitos**: los últimos `SAD_FICHA_PARTIDOS` (default 3)
  por equipo, el más reciente primero — para la cadena basta 1, los otros dos
  dan el "cambios vs anterior" de M1 y M6;
- idempotente: si la ficha ya está, 0 requests;
- se cuelga de la corrida diaria, no de un hilo nuevo.

**Costo**: un partido de la jornada = 2 equipos × 1 partido anterior × 3 = **6
requests**. Con el default de 3 partidos por equipo, 18 la primera vez y 6 en
las siguientes. Es ruido frente a las ~1.500/día del plan.

**Lo que NO se hace**: barrido histórico de fichas. Ingestar lineups/events de
temporadas pasadas serían decenas de miles de requests para un dato que el DTP
solo mira del partido inmediatamente anterior.

⚠️ **Pendiente de verificar con datos reales** (no se puede desde una sesión
sin clave): que el plan contratado sirva `player.grid` en `fixtures/lineups` y
`expected_goals` en `fixtures/statistics`. El código no lo asume: guarda lo que
venga y `ficha_partido --estado` lo canta —

```
filas de alineación: 240 · con grid (carril de M2): 240
  ⚠ NINGUNA trae grid: M2 tendría que degradarse a carriles por posición
  ⚠ sin expected_goals en el catálogo: M5 se queda sin respaldo numérico
```

— y la ficha servida lleva `conGrid: false` para que el DTP vea el hueco en
vez de inventarse un carril. Correr ese comando tras la primera corrida real
es el primer paso de la fase B.

---

## 3. Fase B — el motor · HECHA

### Esquema

`backend/analisis/esquemas.py` gana `DTP`, calcado de las claves del system
prompt (`cadena`, `cierre.m4_goles[]`, `cierre.m5`, `cierre.registro`,
`apertura.m1/m2/m3_fases/m6`, `datos_faltantes`, `fuentes`). Structured
outputs lo garantizan igual que con el EFE.

### Funciones

```python
generar_dtp(fixture_id, equipo_foco, permitir_frio=False) -> dict
```

1. Resuelve el partido N y el **N−1 del equipo foco** (último terminado en
   `fixtures`).
2. Arma `datos_cacheados` con: alineación de N (oficial o probable),
   alineación + eventos + stats de N−1, resultado real de N−1, EFE de N si
   existe, y el `apertura_json` guardado para N−1 si lo hay.
3. Elige modo: **`dtp_completo`** si hay apertura previa de N−1;
   **`dtp_apertura`** si no. Sin partido anterior, solo apertura — lo dice el
   protocolo.
4. Llama con `con_busqueda=False` por defecto: **el DTP no debería buscar
   nada**. Si falta un dato duro (p. ej. no hay alineación de N−1), va a
   `datos_faltantes` y el candado de frío decide, igual que en el EFE.
5. Guarda en `cadena_dtp (equipo_foco, partido_n)`: `apertura_json` siempre;
   `cierre_json` y `registro` cuando el modo fue completo.

`partido_n` = número de partido del equipo foco en la temporada (posición en
su histórico de `fixtures` terminados), no un contador global: es lo que hace
que la cadena sea reproducible.

### Anti-hindsight (la regla que da valor a la cadena)

- El **cierre** de N−1 solo puede contrastar contra una apertura **escrita
  antes** de que N−1 se jugara. Si no existe, `m5.contraste_pronostico` va
  vacío y `registro.veredicto` no se emite — no se fabrica un pronóstico
  retroactivo.
- La **apertura** de N con XI probable se guarda como `estado='preliminar'`;
  cuando llega el XI oficial se genera la `confirmada` sin borrar la anterior
  (misma mecánica que el EFE). Queda registro de qué se sabía y cuándo.

### Endpoints

| Endpoint | Qué hace |
|---|---|
| `POST /api/v1/analisis/dtp` | `{fixtureId, equipoFoco, forzar?, permitirFrio?}` → lanza en el hilo de trabajo, igual que el EFE |
| `GET /api/v1/analisis/dtp/estado/{id}` | sondeo mientras se genera |
| `GET /api/v1/fixtures/{id}/dtp?equipoFoco=` | lee lo guardado (200 vacío si no hay: "real o nada") |
| `GET /api/v1/equipos/{id}/cadena` | la película: N, rival, veredicto y lección por partido |

Contrato primero en `docs/openapi.yaml`, después backend, `src/api/types.ts`,
los dos datasources y `backend/test_api.py` — la regla del proyecto.

**El cierre no necesita endpoint propio.** El `/api/cierre` del plan original
existía porque el resultado se cargaba a mano; aquí el marcador y los eventos
ya entran solos por la ingesta, así que el cierre de N−1 se resuelve dentro
del `dtp_completo` de N. Un endpoint menos que mantener.

### Costo

Sin búsquedas web y con el system cacheado, la llamada es del orden del EFE
caliente: **~$0.10-0.25** por DTP con Sonnet. La cadena no multiplica el
costo: cada partido paga uno.

---

## 4. Fase C — la pantalla · HECHA

En la sección Análisis, **debajo del EFE**, como manda `PLAN_ADAPTADO.md`:

- **CIERRE del partido anterior**: pizarra de goles (disparador → secuencia →
  definición) con responsables por nivel (principal / secundario /
  estructural) y las absoluciones; el veredicto del pronóstico con sus
  aciertos y fallos.
- **APERTURA del próximo**: mapa de duelos por carril (izquierda / centro /
  derecha, con el mismatch escrito), vida útil del planteo rival, plan por
  tramos (0-25 / 25-65 / 65-80+) con sus palancas.
- **Cadena** en la página de Equipo: la lista de N con veredicto y lección —
  es el activo que se acumula.
- Estado vacío honesto y badge `preliminar` / `confirmado` con la hora.

---

## 5. Orden y verificación

1. ~~**A1** ficha de partido: tablas + `ficha_partido.py` + test offline.~~
   **Hecho.** `backend/ingesta/ficha_partido.py`, en la corrida diaria;
   `backend/test_ficha.py` en CI. `fixture_eventos` migró en caliente (gana
   `extra`, `jugador_id`, `asistente`, `asistente_id`) y su guardado es ahora
   compartido: el ciclo en vivo y la ingesta post-partido escriben lo mismo.
2. ~~**A2** exponer la ficha en el backend.~~ **Hecho.**
   `/fixtures/{id}/ficha` gana el bloque `tactica` (contrato en openapi,
   DTOs, mock y `test_api`). El carril de M2 se deriva del `grid` normalizado
   por cuántos jugadores hay en esa línea, y `conGrid: false` avisa cuando la
   API no lo sirvió: el DTP verá el hueco en vez de inventarse un carril.
3. ~~**B1** esquema DTP + `generar_dtp`.~~ **Hecho.** `esquemas.DTP` +
   `motor.generar_dtp/iniciar_dtp/estado_dtp`, endpoints y contrato completo.
   `_lanzar`/`_estado` se generalizaron con `clave`/`existente`/`borrar`
   porque el DTP vive en `cadena_dtp` POR EQUIPO FOCO (dos por fixture) y no
   en `analisis`, cuya clave única es (tipo, fixture, estado).
4. ~~**B2** cadena + anti-hindsight.~~ **Hecho.** El cierre se escribe en el
   eslabón de N−1 (no en el de N) y `guardar_cadena` **nunca** pisa una
   apertura ya escrita: un pronóstico no se puede reescribir después del
   partido. Sin apertura previa, `veredicto` va vacío y el payload lleva la
   orden explícita de no reconstruirlo. Test: `backend/test_dtp.py`.
5. ~~**C** pantalla.~~ **Hecho.** `src/components/DtpPizarra.tsx` (pizarra +
   cadena), bloque DTP en la sección Análisis con toggle de equipo foco y
   sondeo propio, y `Cadena DTP` en la página de Equipo.

Cada fase se puede parar sin dejar nada a medias: A sirve por sí sola (la
ficha de partido mejora el EFE y la UI), B sin C ya deja la cadena escrita.

---

## 6. Lo que este diseño NO resuelve

- **Mecánica fina del gol** (quién marcaba a quién, si fue error de blindaje o
  de línea). `fixtures/events` da minuto, autor, asistente y tipo; el resto lo
  infiere el modelo desde el XI y los carriles. El protocolo obliga a
  etiquetar hecho ≠ interpretación: eso hay que respetarlo en el prompt, no
  disimularlo con un dato que no tenemos.
- **Ligas sin cobertura de lineups** en API-Football: sin XI no hay M1 ni M2.
  El DTP debe negarse a abrir y decir por qué, como hace el candado de frío.
- **xG** si el plan no lo sirve: M5 pierde el respaldo numérico del peligro
  real y se queda en la cronología del giro.
