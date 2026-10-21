# Propuesta de revisión · `sad-analysis` v3.2 → v4.0 (y `efe-dashboard` v1.8 → v1.9)

**Estado:** PROPUESTA. No está aplicada. El skill vive en la cuenta del usuario y
esto es el texto para decidir. Arrancó el 21/10/2026 como una v3.3 (los seis
puntos de la parte B) y pasó a v4.0 el mismo día, cuando se midió qué del skill
llegaba a los partes (parte A). Fuentes: el dossier
(`GET /analisis/cowork/revision/sad-analysis`, cohorte `c3-2026-09-23`), la
calibración de la espina (`GET /analisis/cowork/espina/calibracion`) y los 209
partes con veredicto. La base es la v3.2 vigente de la cuenta, idéntica a la
copia de `docs/skills/sad-analysis/` (13/10); la de `efe-dashboard` es la v1.8
de la cuenta (traída al repo el mismo día).

## De dónde sale

- **El skill es del sistema viejo.** El predictor de goles Poisson v6, la Fe
  Perdida (el péndulo de la hinchada) y el ICF con Random Forest de la Tensión
  del Favorito eran motores del repo anterior (Professional-Player): **ninguno
  existe en esta app**. El skill además pide dos CSV y un screenshot del
  mercado que la corrida no tiene. Lo único al día es la referencia de la
  Regresión al Nivel, alineada al motor en agosto.
- **Lo que llegó a los partes** (209 con veredicto):

| Huella | Partes | Qué pasó |
|---|---|---|
| Poisson con `μ` como λ de goles | 78 | Error de unidad: μ son puntos. Medido en 51 mil partidos, el 1X2 que da es algo peor que una conversión calibrada (parte D) y su marcador exacto no tiene base |
| Fe Perdida | 5 | 2 inventadas sin dato (Boca–São Paulo 1629831, derbi de Montevideo 1638254); 3 sin efecto |
| Tensión del Favorito | 4 | Las mismas 2 inventadas; 2 «no aplica» |
| Veredicto K con gatillos | 2 | A mano con la API; otros 11 declararon «sin CSV, no corrió» |
| Doble oportunidad trampa | 12 | Legítimo: cuotas reales |
| ICF, Ley 8 | 0 | — |

- **379 lecciones**: 253 acreditan (ciegas y PRE) y 126 son de los estudios de
  reventones (`post_resultado`). **Ninguna pide mover un número.** Las 253, por
  tema:

| Tema | Acierto | Parcial | Fallo |
|---|---|---|---|
| Espina de la burbuja | 34 | 38 | 37 |
| Reventón (riesgo, extremo, récord) | 26 | 13 | 17 |
| Regresión al nivel / μ / tres fuentes | 19 | 11 | 18 |
| Falsador, contexto y otras | 7 | 3 | 7 |
| Goles, mercado, Tensión del Favorito, doble oportunidad | 9 | 7 | 7 |

- **Sesgo de atribución:** muchos «fallos» del lado son el 1X2, con la alerta
  del reventón cumplida en la misma lección (City, Atlético, Liverpool,
  Brentford, Boca).
- **Casi todo lo que las lecciones corrigen no está en el skill.** La espina,
  la tarjeta, el riesgo del reventón, K-EXTREMO, FAMILIA-RECORD, ESCALA-LIGAS,
  las tres fuentes, el umbral 0,30 y el falsador viven en el prompt
  (`docs/COWORK.md`) y en `docs/REVENTON.md`: las lecciones de la espina no se
  pueden cerrar contra ninguna versión del skill.
- **Quién da el veredicto hoy.** EFE, TDE y DTP describen y no dan ganador. El
  1X2 y el marcador están en `pronostico` y los arma el analista con tres
  fuentes; la «lectura integrada» (módulo operativo, 1X2, contexto, dato
  estructural, paradoja) la define `efe-dashboard` en su paso 5, que además
  pide un contexto emocional con «Anticulebra, Fe Perdida». El skill que dice
  dar el resultado (`sad-analysis`, con el veredicto K) ya no lo da desde que
  las K salieron del número (14/10).

## Parte A — La forma nueva (v4.0)

### A1. `sad-analysis` es el skill de la SÍNTESIS

Es dueño de dos cosas, y de nada que no tenga dato en la app:

1. **El pronóstico**: las tres fuentes a la vista (motor, matriz, mercado), las
   probabilidades 1X2, el marcador declarado y el falsador. Pasa a este skill
   la **lectura integrada** que hoy define el paso 5 de `efe-dashboard`
   (módulo operativo · 1X2 · contexto · dato estructural · paradoja): son los
   campos de `lecturaSad` del parte.
2. **La lectura de las K**: la espina y el reventón (parte B, puntos 2 y 3).

### A2. Las K: teoría central, en la lectura

La Ley 1 sigue siendo la primaria **de la lectura** (qué pasa con la burbuja de
cada equipo) y conserva sus gatillos, la fusión y la anti-tautología. Lo que
cambia es una frase: el «70 % del peso» es el peso de las K en la lectura, **no
en el número del 1X2**, porque el backtest (REVENTON §13.3-13.4) mostró que no
lo mejoran y desde el 14/10 no entran a la fórmula. **Es el único cambio de
texto en la Ley 1 y pide tu aprobación explícita.**

### A3. Lo que se SUSPENDE por no tener motor en la app

Cada uno queda en el skill como «suspendido (v4.0)» con su motivo; nada se
borra ni se renumera, igual que el TDE en la v0.1.20.

| Qué | Por qué | Qué lo reemplaza |
|---|---|---|
| Ley 5 · Tensión del Favorito (ICF, Random Forest, convergencia crítica) | sin motor, y el backtest del 19/10 no encontró culebra (B1) | regla de mercado: la combinada paga el margen k veces |
| Fe Perdida (péndulo, flags) | sin motor; dos partes la inventaron | nada: la presión o la hinchada se cuentan como contexto con fuente, sin «módulo» |
| Modelo de goles Poisson v6 (Ley del Marcador) | sin motor; se improvisó con μ en 78 partes | el 1X2 del motor calibrado (parte D); el marcador, ver B6 |
| Ley 8 · Canales opuestos | sin dato de audiencia; 0 usos | nada |
| Entradas por CSV y screenshot, `audit_protocol.py` | la corrida lee la API | las rutas de la API (`/constantes`, `/burbujas`, `/predicciones`, `/cuotas`); la auditoría pasa a ser la del recibo del parte (`faltan`, `rechazos`) |

Se quedan, porque tienen dato: Ley 1 (K), Ley 2 (Regresión al Nivel, μ),
Ley 3 (rivales futuros, calendario de la base), Ley 4 (once, F1 de la base),
Ley 6 (doble oportunidad trampa, cuotas reales), Ley 7 (goles × fecha ×
condición, K de goles y stats) y Ley 9.

## Parte B — Las lecciones (los seis puntos de la v3.3)

## Lo que esta capa acierta y no hay que tocar

- **La espina leída a un lado acierta por encima de la frecuencia del
  movimiento.** `positiva` acierta el 55 % (96 lados) y `negativa` el 58 %
  (83 lados), contra un 39 % de frecuencia de ese movimiento.
- **Ir contra la tarjeta con un hecho del partido suma.** Cuando el analista
  la contradijo, acertó 21 de 55 veces y la tarjeta 10.
- **La tarjeta fuerte acierta.** Lo hace el 64 % de las veces (72 lados), y
  la débil el 38 %.
- **K-EXTREMO y K-CERCA-EXTREMO como prudencia, no como corte.** Se
  confirmaron en City (K +59), Atlético, Liverpool, ADT y Los Chankas. En
  Santos Laguna y Cúcuta la burbuja siguió, y la alerta solo frenó la carga.
  Las dos cosas son lo que la regla dice.
- **La Ley 9 (nivel sobre nombre) y la regla anti-tautología.** Nadie las
  discute.

### 1. La Ley 5 (Tensión del Favorito) sale del skill

Es la deuda 16 de `CLAUDE.md`, pendiente desde el 19/10.

**Lo medido:**

- El estudio de ML de febrero dejó roto `ml_break_score`: el 42,9 % de los
  valores en cero y sin relación con los resultados. El ICF dio r = 0,10.
- El backtest del 19/10 (63.475 partidos del padrón 2019-2026) **no encontró
  culebra**. Con la jornada «intacta», el siguiente favorito gana igual o algo
  más de lo esperado.
- La combinada de los favoritos del día sale lo que da el producto de sus
  probabilidades.
- En el dossier, ninguna lección la sostiene. Las cuatro etiquetadas cerca de
  ella hablan de rotación y de mercado, no de culebra.

**Propuesta:**

- La Ley 5 sale del Nivel 1 de filtros obligatorios. Sale también la
  **convergencia crítica** («K techo + doble oportunidad trampa + tensión →
  el favorito no gana») y el paso 3 del script de auditoría
  (`audit_protocol.py`).
- La ley **no se renumera**: queda «5 — suspendida (v4.0)», con el motivo. Es
  la misma salida que el TDE en su v0.1.20: se suspende lo que no se
  sostiene y no se borra la historia.
- Queda en pie, como regla de mercado y no como ley: **«la combinada de
  favoritos tiene poca probabilidad y paga el margen de la casa k veces»**.
  Nunca «el siguiente favorito va a caer».
- `references/motor_tension_favorito.md` y el caso de `casos_referencia.md`
  quedan como **historia**, con un encabezado de suspensión.
- La pista de la combinada de los favoritos más fuertes (+48 %, IC −9 % a
  +116 %, 71 días) **no entra**: se sigue midiendo.

### 2. La lectura de la burbuja (espina) entra al skill como paso propio

Hoy la espina es obligatoria en el parte desde el 14/10, pero el skill no la
nombra.

**Propuesta:** un **Paso 1.6 — Espina de la burbuja**, después del veredicto
K. Trae la regla del prompt (positiva · cero · negativa · neutra, guía total o
de la condición, empezar por la tarjeta) y las lecciones de la cohorte:

- **(a) `cero` necesita un hecho de ESTE partido.** Leída como `cero`, la
  espina acertó 8 de 37 veces (22 %), lo mismo que la frecuencia del empate
  (21 %): no agrega nada. La frecuencia con que el equipo corta sus burbujas
  empatando no alcanza. Falló en Cagliari (14 de 20 cortes a empate), IdV
  (46 de 92), ADT, Guabirá y Racing.

  Lo que sí empujó al empate fue un hecho del partido:
  - los dos perfiles DC apuntando al empate (Sarmiento–Barracas);
  - las dos burbujas negativas enfrentadas (Corinthians–Vitória);
  - un rival que empata la mitad de sus partidos (Portuguesa, 7 de 13).
- **(b) El `porque` y la lectura tienen que ir en la misma dirección.** Si el
  propio porqué dice que la racha se corta, la espina no puede leer que
  sigue: Puerto Cabello, Bucaramanga y Newcastle.
- **(c) Contra la tarjeta, con un hecho concreto, no con un perfil.** Lo que
  ganó fue un DT nuevo invicto con el once de vuelta (Nacional), un once roto
  o una rotación por copa. Lo que perdió fue la diferencia de EFE, la altura
  o el perfil de visita (Independiente Petrolero, Pasto y Chicó).
- **(d) Burbuja de un partido:** «se da vuelta» no tiene más base que «se
  reinicia» (Leeds, Barcelona SC, Union Berlin).
- **(e) Guía de la condición con T.54 o ESCALA-LIGAS.** Si la K de la
  condición se armó con otro DT o en otra categoría, se lee la total o se
  declara la reserva. Casos: San Lorenzo, UCV Moquegua y Málaga (guía armada
  en Segunda). Es la misma regla que el T.54 del EFE v1.6: la serie del DT
  anterior se descuenta y la del nuevo cuenta.
- **(f) `neutra` es honesta pero no puntúa** (0 de 18). Con riesgo alto o muy
  alto, una `neutra` que no nombra el riesgo deja sin lectura al lado que
  decide el partido (Auxerre, Albion).

### 3. El riesgo del reventón es una tasa que frena la carga, no un lado del 1X2

**Casos:**

- **El riesgo empujó el 1X2 contra el favorito y la racha siguió:**
  Palmeiras (ganó por dos de visita), Chelsea, Feyenoord, Cúcuta (cuarta
  victoria seguida) y Aldosivi.
- **El 1X2 cargó a favor de la racha con riesgo alto y reventó:** Auxerre,
  América de Cali y City (47 % a que siguiera).

Las dos cosas encajan con la guía calibrada: con riesgo muy alto la racha
sigue el 28 % de las veces, no nunca.

**Propuesta:**

- **(a)** Con riesgo alto o muy alto, **el 1X2 no carga a favor de la
  racha**. Tampoco se da vuelta contra el favorito del mercado solo por el
  riesgo.
- **(b)** El **tramo del rival se sobreestima cuando el rival rota** por
  otra competición. Pasó con São Paulo (Vasco rotado por la semifinal) y con
  Torque.
- **(c)** Con **ESCALA-LIGAS**, el tramo del rival compara niveles de dos
  bases y el riesgo se lee con la confianza bajada. Casos: Bodø, Porto,
  Sporting Cristal, U. Católica, West Ham descendido y Elversberg.
- **(d)** **FAMILIA-RECORD se sostiene:** una racha en su récord no se corta
  por estar en récord. Así pasó con Inter Bogotá, Ameliano, Brest, Central
  Córdoba, Tolima y Cajamarca. Leer el corte de una burbuja en su récord
  necesita algo más que el récord.

El gatillo 1 de la Ley 1 («¿techo histórico?») se lee hoy como señal de
estallido. El backtest dice que **la K no puntúa** (REVENTON §13.2): estar por
encima de la K con que suele reventar no adelanta el corte. Se propone una
**nota** al gatillo, sin tocar la Ley 1: «el techo es prudencia (no cargar a
que siga), no anuncio de corte». Es la lectura que ya tienen K-EXTREMO y las
lecciones.

### 4. Ley 2: las tres fuentes, el umbral 0,30 y la disciplina 33 entran al skill

El pronóstico con tres fuentes (motor, matriz y mercado) está en el prompt,
y la disciplina 33 en el TDE. El skill que hace el 1X2 no nombra ninguna de
las dos.

**Casos:**

- **Margen de `μ` bajo 0,30 cargado a un lado por relato.** Pasó con la
  localía cualitativa (Sport Boys, Chicó–Cúcuta), con «DT nuevo + altura»
  (Pasto), con el calendario contra el mercado y sin delta (Athletico) y al
  recortar al visitante por debajo del motor (Juventus–Lazio). Y en sentido
  contrario: un margen bajo el umbral no vuelve pick al empate cuando motor y
  mercado apuntan al mismo lado (Parma).
- **`μ` entre dos bases (ESCALA-LIGAS).** Gobernó el 1X2 y falló en Porto,
  Fenerbahçe y Aston Villa–Fenerbahçe, y en LASK–Liverpool falló contra la
  matriz que se apartó. Se invirtió en silencio y también falló en Bodø
  (ganó el local que el motor ponía arriba); Feyenoord también acertó con la
  dirección del motor.
- **La contradicción escrita en prosa y el número anclado a un solo lado:**
  Alianza Atlético, Fluminense–Santos, Santos Laguna y Estudiantes de Mérida.
- **La rotación por copa la ve el mercado y el motor no:** Estudiantes L.P.,
  São Paulo–Vasco y Torque. Pero el descuento propio por bajas que el mercado
  ya conoce falló: Nacional en Chicó.

**Propuesta, cuatro reglas en la Ley 2:**

- **(a)** El pronóstico declara **las tres fuentes en simultáneo**. Si el
  motor no corrió, se dice, no se reemplaza (disciplinas 21 y 33).
- **(b)** Con **margen de `μ_partido` bajo 0,30**, el 1X2 queda cerca de lo
  que da el motor. Se aparta solo con un **dato nuevo** que el motor no ve:
  un once rotado, una baja estructural o la Ley 3 confirmada. Una localía
  cualitativa o un perfil no alcanzan.
- **(c)** Con **ESCALA-LIGAS**, el `μ` se publica como sale, **ni gobierna el
  1X2 ni se invierte en silencio**: se ensancha el rango y se publican los
  dos números.
- **(d)** **Disciplina 33 en el skill:** cuando dos señales propias van
  contra el 1X2, el número se mueve o se publican los dos con su origen. Un
  descuento propio contra el mercado pide un dato que el mercado no tenga.

Además, **la Ley 3 activa con rotación confirmada baja al favorito**:
Estudiantes L.P. quedó en el 42 % con el once mixto y perdió en casa.

### 5. El falsador se escribe sobre un hecho observable, de los dos lados

**Casos:**

- **Condicionado al marcador:** «si el favorito marca primero» en Braga, que
  marcó primero y perdió sin que el falsador sonara. Lo mismo con «si Cúcuta
  marca antes del 60'» en Chicó.
- **Atado al reloj:** en Fluminense–Palmeiras, el gol de Palmeiras llegó al
  45, fuera del primer tiempo que vigilaba el falsador.
- **De un solo lado:** en Juventus–Lazio vigilaba solo el dominio local, y en
  Real Oruro–Aurora el «ambos marcan» cayó por el lado que no convirtió.

**Propuesta:** el falsador del 1X2 es una **condición observable pura**,
escrita sobre el **mecanismo**: quién genera, por dónde y con qué. No se
escribe sobre el estado del marcador ni sobre un minuto, y **cubre los dos
lados** de la lectura. Entra a la Auditoría 2 como quinta pregunta.

### 6. El marcador sale de la lectura de goles, no de un Poisson sobre μ

**Casos:**

- **«Partido cerrado» contra el número:** en Delfín–Manta, «dos de los que
  menos marcan» terminó con 6 goles, con `μ` de 1,68 y 1,08.
- **Racha larga tomada como certeza:** en Everton–Chelsea, «concede en 22
  seguidos, el gol es casi un hecho» y no concedió.
- **Marcador declarado contra la celda modal:** en Valencia–Athletic se
  declaró 1-1 con el 0-0 como celda modal del empate.

**Propuesta:**

- La app **no tiene modelo de goles**: el marcador exacto es lectura, no
  número. Sale de la Ley 7 (K de goles por condición, ciclos), de las stats
  (`/equipos/{id}/stats`: goles, xG) y del 1X2 del motor, y se declara como
  celda probable **sin porcentaje inventado**. Nunca de un Poisson con μ.
- Un rótulo («los que menos marcan», «partido cerrado») no achica la banda de
  goles que dicen los promedios.
- Una racha de goles en contra no convierte el gol del rival en certeza.
- Entre dos celdas casi empatadas, se nombran las dos.
- Un modelo de goles calibrado (λ de goles por equipo) queda como posible
  trabajo del backend, **no propuesto ahora**.

## Parte C — `efe-dashboard` v1.8 → v1.9

- **Paso 5 (lectura integrada) pasa a `sad-analysis`.** El dashboard la
  muestra pero no la define; el texto dice «ver `sad-analysis` v4.0».
- **Sale el «Contexto emocional: presión, hinchada, Anticulebra, Fe
  Perdida».** Queda «contexto con fuente» (presión de tabla, hinchada, clima
  del club, citado), sin módulos que no existen.
- **`ANTICULEBRA-INVERTIDA`** (candidato, «el favorito que se relaja en un
  TRAMO TRAMPA») se renombra **`FAVORITO-RELAJADO`**: el contexto se queda,
  sin el nombre de un motor suspendido.
- **El «checklist de 9 puntos» y la «Ficha de Mecanismo»** que cita el paso 6
  no existen en disco (deuda 15): se quitan las dos menciones y queda lo que
  sí está escrito (filas obligatorias por escenario, casos a favor y en
  contra, disciplina 33).
- **La matriz se queda en el dashboard** y es una de las tres fuentes del
  pronóstico. Su probabilidad por escenario se compara con el 1X2 del motor
  (`unXDos`), ya no con un Poisson.

## Parte D — El 1X2 del motor, calculado (HECHO en esta rama)

La opción (b) aprobada el 21/10: lo que está en la base se calcula.

- `GET /predicciones/{id}` trae **`unXDos`** (local · empate · visita): una
  logística multinomial sobre d = μ_local − μ_visita y d²
  (`backend/analisis/unxdos_motor.py`, espejo `src/lib/unxdos.ts`, vectores
  `scripts/casos_unxdos.json`, `docs/MOTOR_SAD_EXTRACCION.md` §5.6). Se ve en
  Estadísticas, debajo del gap.
- **Calibración** (`python -m backend.backtest_unxdos_motor`): 51.254 partidos
  del padrón 2019-2026, nivel de cada lado el último anterior al partido,
  prueba temporal con el 20 % más reciente (10.251 partidos):

| prueba | log-loss | Brier | acierto |
|---|---|---|---|
| logística sobre μ | **1.0512** | 0.6333 | 46,5 % |
| Poisson sobre μ (lo improvisado) | 1.0590 | 0.6382 | 46,3 % |
| frecuencia | 1.0707 | 0.6473 | 44,6 % |

  Logística − Poisson: −0.0078 [−0.0099, −0.0057]. El Poisson no estaba lejos
  (por eso los 78 partes no salieron peor), pero era un error de unidad y su
  marcador exacto no tenía base. Por tramo de d, modelo y realidad quedan a ≤ 4
  puntos.
- El prompt (`docs/COWORK.md`) y `corrida-sad` ya dicen: la fuente «motor» del
  pronóstico es `unXDos`, copiada tal cual, y **nunca un Poisson sobre μ**.
  Contra el mercado sigue valiendo REVENTON §13.5: el motor capta un tercio de
  lo que sabe la cuota.

## Lo que NO se propone

- **Ningún gatillo ni regla de la Ley 1** fuera de la frase del 70 % (A2).
- Ningún mínimo del underdog (5 / 10 / 15 %), ninguna severidad de la
  Auditoría 1 y ningún umbral de la doble oportunidad trampa (1,05).
- **La serie DIV-MOTOR-MERCADO** sigue contándose. En la cohorte acertó a
  veces el motor (Boston River, Newcastle, Corinthians) y a veces el mercado
  (Everton, Angers, Athletic, Santos Laguna). No hay regla todavía.
- La pista de la combinada de los favoritos más fuertes del día (B1).
- Re-depositar o tocar los 78 partes con Poisson: lo dicho queda como se dijo
  (el 1X2 se mide igual con su Brier) y los 2 con Fe Perdida inventada no
  cambian su población.

## Cómo se aplica si se aprueba

1. Apruebas o corriges las partes A, B y C, y la frase del 70 % (A2). La parte
   D ya está hecha (código, tests y prompt).
2. Redacto `sad-analysis` v4.0 en `docs/skills/sad-analysis/`: el SKILL.md
   reescrito sobre las leyes con dato, las secciones suspendidas con su
   motivo, las referencias de goles, Fe Perdida y Tensión con encabezado de
   suspensión, y `audit_protocol.py` fuera (o marcado suspendido).
3. Redacto `efe-dashboard` v1.9 (parte C).
4. Ningún campo nuevo en el parte: la espina, el falsador, las tres fuentes y
   la lectura SAD ya tienen sitio. El prompt se alinea donde repita una regla
   y apunta al skill.
5. Te entrego los dos `.zip` y marcas con 🔑 las lecciones aplicadas.
