# Propuesta de revisión · `sad-analysis` v3.2 → v3.3

**Estado:** PROPUESTA. No está aplicada. El skill vive en la cuenta del usuario y
esto es el texto para decidir. Se redactó el 21/10/2026 desde el dossier
(`GET /analisis/cowork/revision/sad-analysis`, cohorte `c3-2026-09-23`) y desde
la calibración de la espina (`GET /analisis/cowork/espina/calibracion`). La
base es la v3.2 vigente de la cuenta, idéntica a la copia de
`docs/skills/sad-analysis/` (13/10).

## De dónde sale

- 379 lecciones. De ellas, 253 acreditan (ciegas y PRE) y 126 vienen de los
  estudios de reventones (`post_resultado`: fijan rúbrica, no acreditan).
  **Ninguna pide mover un número.**
- Las 253 acreditables, por tema:

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
- **El hallazgo de fondo.** Casi todo lo que estas lecciones corrigen **no
  está escrito en el skill**. La espina, la tarjeta, el riesgo del reventón,
  K-EXTREMO, FAMILIA-RECORD, ESCALA-LIGAS, las tres fuentes del pronóstico, el
  umbral 0,30 de `μ_partido` y el falsador viven en el prompt de la corrida
  (`docs/COWORK.md`) y en `docs/REVENTON.md`. La v3.2 es anterior a la app: no
  los nombra. Por eso las lecciones tienen dónde quedar en el prompt, pero no
  en el skill que el analista carga. **La v3.3 los trae al skill.**

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

## Los seis cambios propuestos

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
- La ley **no se renumera**: queda «5 — suspendida (v3.3)», con el motivo. Es
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

### 6. El marcador sale del número, no del rótulo

**Casos:**

- **«Partido cerrado» contra el número:** en Delfín–Manta, «dos de los que
  menos marcan» terminó con 6 goles, con `μ` de 1,68 y 1,08.
- **Racha larga tomada como certeza:** en Everton–Chelsea, «concede en 22
  seguidos, el gol es casi un hecho» y no concedió.
- **Marcador declarado contra la celda modal:** en Valencia–Athletic se
  declaró 1-1 con el 0-0 como celda modal del empate.

**Propuesta:**

- En la Ley 7 y en el Poisson, el marcador sale de las `λ`. Un rótulo («los
  que menos marcan», «partido cerrado») no achica la banda de tres o más
  goles que el número da.
- Una racha de goles en contra no convierte el gol del rival en certeza.
- Entre dos celdas casi empatadas, se nombran las dos.

## Lo que NO se propone

- **El peso del 70 % de las K (Ley 1) no se toca**, y tampoco ninguno de sus
  gatillos. `CLAUDE.md` lo dice: las K son la teoría central. Queda declarado
  el desfase, para que lo decidas tú: el backtest (REVENTON §13.3-13.4) mostró
  que las K no mejoran el 1X2 del motor, y desde el 14/10 se usan en la
  **lectura** (la espina), no en la fórmula. La v3.3 puede decir «el 70 % es
  el peso de las K en la lectura, no en el número del 1X2», o dejarlo como
  está. **Decisión tuya.**
- Ningún mínimo del underdog (5 / 10 / 15 %), ninguna severidad de la
  Auditoría 1 y ningún umbral de la doble oportunidad trampa (1,05).
- **Las entradas del skill** (dos CSV y un screenshot del mercado) no se
  rehacen. La corrida las toma de la API (`/constantes`, `/burbujas`, las
  cuotas), y adaptar el formato de entrada es una reescritura aparte, no una
  lección.
- **La serie DIV-MOTOR-MERCADO** sigue contándose. En la cohorte acertó a
  veces el motor (Boston River, Newcastle, Corinthians) y a veces el mercado
  (Everton, Angers, Athletic, Santos Laguna). No hay regla todavía.
- La pista de la combinada de los favoritos más fuertes del día (punto 1).

## Cómo se aplica si se aprueba

Igual que con el TDE, el DTP y el EFE:

1. Apruebas o corriges cada punto, y decides lo del 70 %.
2. Redacto la v3.3 en `docs/skills/sad-analysis/` (SKILL.md, el script de
   auditoría sin el paso 3 y las referencias con el encabezado de
   suspensión).
3. Ningún campo nuevo en el parte: la espina, el falsador y las tres fuentes
   ya tienen sitio. El prompt (`docs/COWORK.md`) se alinea donde repita una
   regla.
4. Te entrego el `.zip`.
5. Marcas con 🔑 las lecciones como aplicadas.
