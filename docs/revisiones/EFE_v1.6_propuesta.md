# Propuesta de revisión · `efe-clasificador` v1.5 → v1.6

**Estado:** APROBADA por el usuario (21/10/2026, los seis puntos). Redactada en
`docs/skills/efe-clasificador/` (v1.6; la rúbrica pasa a
`references/rubrica-efe-v1.6.md`). Ningún campo nuevo en el parte: las
alertas viajan en `alertas` como hasta ahora. Falta que el usuario la suba a
su cuenta. Se redactó el 21/10/2026 desde el dossier
(`GET /analisis/cowork/revision/efe-clasificador`, cohorte `c3-2026-09-23`). La
base es la v1.5 vigente (25/03), traída de la cuenta a
`docs/skills/efe-clasificador/` (SKILL.md y `references/rubrica-efe-v1.5.md`).

## De dónde sale

- 35 casos ciegos PRE, 341 lecciones acreditables. **Ninguna pide mover un
  número.**
- Se leyeron los fallos y parciales de los seis grupos más cargados:
  FACTOR-X (21), COLAPSO EN CASCADA (21), T.54 (21), arquero B6/GK (17),
  B5 (11) y G-SORPRESA (9).
- **Sesgo de atribución:** muchos «fallos» del lado son el 1X2, con la alerta
  del EFE confirmada en la misma lección. FACTOR-X y T.54 son el caso más
  claro: casi todas sus lecciones dicen «confirmada».

## Lo que esta capa acierta y no hay que tocar

- **FACTOR-X «amplía el rango, no mueve el centro».** En unos doce cierres el
  jugador declarado decidió y la instrucción de no mover el 1X2 fue correcta:
  Coutinho, Tahiel Jiménez (tres goles), Canelo, Pedrinho, Vombergar, Maciel,
  Isak y Liberali.
- **T.54 descuenta la serie del DT anterior.** Confirmada en Albion,
  Gladbach, Auxerre, Monagas, Cajamarca, San Lorenzo y Cerro. Su variante
  T.54-B sostuvo en Lorient y en Once Caldas.
- **B5 (banco de impacto).** Confirmado en Atlético, Liverpool, Shakhtar,
  Emelec y Delfín.

## Los seis cambios propuestos

### 1. COLAPSO EN CASCADA deja de predecir goleadas

**Lo medido:** el escenario completo de la alerta —el equipo con D3 ❌
recibe primero contra un rival con D3 ✅ o 🔶— se dio en **unos ocho casos
y en ninguno hubo colapso**:

- Mushuc Runa (empató a los 17').
- Emelec.
- Deportivo La Guaira (remontó).
- Necaxa (siguió generando hasta el 90).
- Tigre (empató a los 6').
- Deportivo Pereira.
- Racing de Santander (remontó).
- Estudiantes de Río Cuarto (remontó).

Las dos goleadas de la cohorte fueron de equipos con **D3 🔶, no ❌**:
Fenerbahçe 0-6 en la Champions y Cagliari 0-4. Lo vieron también los
registros del TDE: TDE-012 y TDE-029 tuvieron el escenario completo y el
desenlace no acompañó.

La lección que más se repite: **«D3 ❌ predice perder la ventaja, no
romperse»** (Racing, Los Chankas).

**Propuesta:**

- La alerta conserva el **escenario**: el equipo con D3 ❌, si recibe
  primero, tiene que abrir líneas.
- Pierde la **predicción**: «probabilidad de goleada significativamente
  mayor» se borra, y también la instrucción de considerar mercados de
  hándicap y de más/menos goles.
- Se reescribe como **«D3 ❌ = riesgo de perder una ventaja, no de
  romperse»**.
- Es la misma salida que el TDE aplicó en su v0.1.20 con las probabilidades
  que no se sostenían: suspender la lectura, no borrar el mecanismo.
- **El candidato D3-DEGRADADO** (un D3 🔶 medido en otro contexto se trata
  como ❌) suma Fenerbahçe y Cagliari, y queda **con dos casos a favor, como
  candidato**.
- El **tope del bloque D por D3 ❌** (2,5 de 4) es un número: **no se toca**.
  Queda anotado para revisar con el backtest.

### 2. FACTOR-X: el barrido de F5 es sistemático, no a ojo

**Casos:** lo que más falla no es la regla sino a quién se le aplica. El
decisivo muchas veces no estaba declarado:

- Prass en Hoffenheim, un regreso de lesión titular.
- Ayrton Costa en Boca, un regreso que no estaba en la tabla F1.
- Flecker y Dibango en LASK, sin registro en la base.
- Carvajal en Getafe, un libre inscrito esa semana.

Y en la Libertadores se declaró a Rojo, que CONMEBOL no había habilitado.

**Propuesta:** F5 recorre **cuatro listas fijas**:

- (a) **todos** los regresos de lesión larga del once, no solo el que nombra
  la previa;
- (b) las altas de la semana, libres incluidos;
- (c) al cerrar el once oficial, **todo titular sin registro en la base o
  fuera de la tabla F1** es candidato a FACTOR-X;
- (d) en copa internacional, la habilitación se verifica en la **lista de
  buena fe del torneo**, no en la de la liga local.

**La regla «amplía el rango, no mueve el centro» no se toca.**

### 3. T.54 descuenta TODO lo heredado y respeta lo nuevo

**Casos:**

- **D3 y C4 del DT anterior.** En Albion, el D3 se midió en las ocho derrotas
  del DT saliente y activó el tope del bloque D. En Pereira, la serie de
  goleadas recibidas era de otro cuerpo técnico y se usó para leer colapso.
- **La racha del DT nuevo.** En Santos Laguna se descontaron también las
  cuatro victorias con Paiva, que eran la única señal del equipo actual.
  Pasó lo mismo con Nacional y Albion.
- **El DT anunciado que no estaba inscrito.** En Corinthians se puntuó a
  Seedorf, que no estaba en el BID; el banco era del interino.
- **Leer T.54 como señal de resultado.** Universitario ganó 4-1 de visita con
  su cuarto DT del año.

**Propuesta:**

- (a) Con T.54, **D3, C4 y cualquier lectura de colapso medidos bajo el DT
  anterior van `sin dato`**, no ❌. Es la regla de «sin dato es respuesta
  válida» aplicada a la herencia.
- (b) La serie se **corta en la fecha del cambio**: lo hecho antes se
  descuenta; lo hecho bajo el DT nuevo es la señal del equipo actual.
- (c) El bloque A y T.54 se puntúan sobre **el banco que dirige**. Un DT
  anunciado que no está inscrito no debuta: es la misma regla que `dt.banco`
  del parte.
- (d) T.54 descuenta la serie, **no el partido**: no se lee como señal de
  derrota.

### 4. B5 se puntúa por lo que entra, no por lo que falta

**Casos:**

- **Puntuado por lesionados.** En São Paulo, B5 bajó por el conteo de
  lesionados y Lucas Moura entró al descanso y cambió el partido.
- **Sin evidencia.** En Pereira, B5 ❌ se puntuó porque no se encontró un
  suplente de impacto, y el empate lo hicieron dos que entraron al descanso.
- **Rotación de una pareja.** En Fluminense, B5 ✅ («la rotación es
  profundidad») no sostuvo cuando se rotó la pareja del medio. En Nacional
  pasó lo mismo con el once entero rotado, con calor y tres días de
  descanso.

**Propuesta:**

- (a) B5 se puntúa por el **impacto documentado del que entra**. **Sin
  evidencia, `sin dato`**: puntuar bajo por no encontrar es el mismo error
  que puntuar alto por reputación. El TDE ya lo escribió para su F3.
- (b) **B5 ✅ no compensa un F3 rojo cuando la rotación toca una pareja de
  la misma línea:** la profundidad por puesto no reemplaza los minutos
  juntos.

### 5. El arquero: B6 se rehace con el once y GK-FALLA-ACTIVA se da de alta

**Casos de B6 con el once:** Lille atajó con Gill, debutante en el club,
cuando B6 decía Özer. Como atajó con Robert Sánchez, cedido el 31/08. Real
Oruro, con un arquero que nadie había investigado.

**Caso del suplente por lesión corta:** en Aldosivi entró el suplente por un
desgarro del titular y cometió el error del 2-1. No activa GK-DOWNGRADE, pero
el riesgo tampoco se declaró.

**Casos de un arquero que está fallando:**

- Cusco: Pedro Díaz.
- Athletico Paranaense: un arquero recién reinstalado, implicado en los dos
  goles.
- Grêmio–Internacional: un rechace de Anthoni.
- Alianza Lima: TDE-047, en la v1.3 del DTP.

El candidato GK-FALLA-ACTIVA ya estaba declarado en el TDE y en el DTP, con el
umbral de ≥ 2 errores que terminaron en gol.

**Propuesta:**

- (a) **B6 se rehace con el once oficial**, como el bloque F. Un cambio de
  arquero el mismo día abre la caja de sensibilidad en vez de darse por
  sabido.
- (b) Un **suplente que entra por lesión corta** no activa GK-DOWNGRADE, pero
  **se declara** como riesgo del arco y baja al DTP como vía del rival.
- (c) **Alta de la alerta `GK-FALLA-ACTIVA`, declarativa y sin peso:** un
  arquero titular con ≥ 2 errores que terminaron en gol en sus últimos 5
  partidos. Es el mismo umbral que la vía del arquero de la v1.3 del DTP. No
  mueve el IP ni el porcentaje. Viaja a la tira y al DTP como vía.

### 6. G-SORPRESA se lee como FACTOR-X: amplía el rango

**Lo medido:** salió mitad y mitad.

- **Regresó:** Torque (dos veces), Mónaco, Betis y Querétaro.
- **Sostuvo:** Lazio, Sport Huancayo, Bodø y River.

Lo dicen las propias lecciones: «un partido no refuta la regresión» y «el
sobre-rendimiento fuerte persiste». Es el mismo hallazgo que el backtest del
motor (disciplina 12 del TDE).

**Propuesta:**

- La alerta **no mueve el 1X2 de la fecha**: amplía el rango, como FACTOR-X.
- **Candidato, no aplicado:** pesa más cuando coincide con un F3 rojo o con
  carga de copa (Mónaco, Torque). Son dos casos.

## Lo que NO se propone

- Ningún peso, ningún máximo ponderado y ningún corte de la tabla de
  puntuación.
- El tope del bloque D por D3 ❌ queda como está, aunque el punto 1 lo pone
  en duda: es un número y se mide con el backtest.

## Cómo se aplica si se aprueba

Igual que el TDE y el DTP:

1. El usuario aprueba o corrige.
2. Se redacta la v1.6 en `docs/skills/efe-clasificador/`.
3. Se le da sitio en el parte a lo que necesite campo. Por ejemplo,
   `GK-FALLA-ACTIVA` como alerta capturada y las alertas que el backend ya
   conoce.
4. Se entrega el `.zip`.
5. El usuario marca como aplicadas las lecciones con 🔑.
