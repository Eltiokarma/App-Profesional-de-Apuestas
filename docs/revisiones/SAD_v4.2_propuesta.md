# Propuesta de revisión · `sad-analysis` v4.1 → v4.2

**Estado:** PROPUESTA, para aprobar por el usuario. Redactada el 28/10/2026
desde las **165 lecciones pendientes** del skill (130 de partes escritos con
la v4.1, del 25 al 27/10), la calibración del 1X2 por versión y la
calibración de la espina (`GET /analisis/cowork/espina/calibracion`). La base
es la v4.1 vigente (`docs/skills/sad-analysis/SKILL.md`).

## De dónde sale

- **165 lecciones:** 68 aciertos, 45 parciales y 52 fallos. Todas ciegas PRE.
  Jev marcó una sola como «pide mover un número».
- **La v4.1 funciona, y esta revisión no la toca.** Acierto del 1X2 declarado
  en población ciega, por versión del skill al depositar:

  | Versión | Partes | Aciertos | Tasa |
  |---|---|---|---|
  | anterior a v4.0 | 175 | 97 | 55 % |
  | v4.0 | 102 | 47 | 46 % |
  | **v4.1** | **67** | **44** | **66 %** |

  Por tramo, la v4.1 quedó pegada al mercado (dijimos 55 y el mercado daba 57
  en el 50-59; 69 contra 71 en el 60+) y acertó al menos lo que dijo: 16 de
  22 en el 50-59, 12 de 15 en el 60+. Las dos reglas del 25/10 (el empate
  parte del mercado; el favorito no se recorta sin dato) son la causa más
  probable de la mejora. **Nada de lo que sigue las afloja.**
- **La espina, medida** (582 lados ciegos con tarjeta):
  - La tarjeta **fuerte** acierta el 59 % (101 de 170); la **débil**, el 41 %
    (168 de 412).
  - La tarjeta débil **de la condición** es peor que una moneda: local 26 %
    (10 de 38), visita 34 % (12 de 35).
  - Cuando el analista va **contra** la tarjeta, acierta él 63 de 134 y la
    tarjeta 29.
  - La lectura `cero` acierta el 22 % (14 de 64), lo mismo que la frecuencia
    del empate (20 %). `neutra`: 0 de 20.

## Lo que la v4.1 acertó y no hay que tocar

- **El favorito no se recorta sin dato propio (6-B).** Internacional–
  Botafogo: 9 puntos de recorte por bajas que ya estaban en la cuota, ganó el
  local 3-0. Junior–Águilas: 13 puntos menos que el mercado, ganó el local, y
  el mercado habría dado Brier 0,375 contra 0,595. Con el dato escrito, el
  recorte fue bien (O'Higgins–Cobresal: empate).
- **El riesgo frena la carga, no elige el lado (1.7 a).** Toulouse, Cerro
  Largo y Cienciano cargaron a que la racha siguiera con riesgo alto y
  reventaron; Belgrano y Santos Laguna respetaron el riesgo.
- **FAMILIA-RECORD se sostiene (1.7 d).** Toulouse, Águilas, Metropolitanos,
  Fortaleza, Medellín: en su récord la burbuja siguió.
- **K-CERCA-EXTREMO es prudencia (1.7 e) y la espina no dice «sigue» en el
  extremo.** Chapecoense, Tolima, O'Higgins, São Paulo, Leones, Libertad:
  reventaron. Desde el 26/10 la app lo avisa (`ESPINA-SIGUE-EN-EXTREMO`).

## Los cuatro cambios propuestos

### 1. El mercado que se mueve, y la razón que cae

**Lo medido:**

- **Cúcuta–Águilas:** el parte dejó al local 3,6 puntos sobre el mercado
  mientras la cuota se corría hacia la visita (delta de apertura a cierre) y
  Berdugo era duda. Ganó la visita 0-2.
- **Cagliari–Bologna:** el parte se separó del mercado con tres razones; una,
  la del EFE, estaba anulada por `EFE-EMPATE-TECNICO` en el mismo parte.
  Ganó el favorito del mercado.
- **Aston Villa–City, Leones–Libertad, Barcelona–Real Madrid:** el 1X2 se
  apoyó en la brecha del EFE con T.54 del otro lado. Las tres fallaron.

**Propuesta (6-A y 6-B):**

1. **El 1X2 no se aparta del mercado en la dirección contraria al delta**
   (apertura → cierre de `/cuotas/{id}/historial`) sin un dato propio que lo
   explique. Un delta que se corre es información que el mercado ya tiene.
2. **Una razón que una alerta del propio parte anula no sostiene el número.**
   Si el EFE está en empate técnico (`EFE-EMPATE-TECNICO`), con ESCALA-LIGAS
   o con T.54, el porcentaje del EFE no cuenta como razón para separarse del
   mercado ni del motor. Si era la razón, el número vuelve al mercado.

### 2. Los dos perfiles de doble oportunidad alineados son un hecho; uno solo no

**Lo medido.** El perfil DC por condición (REVENTON §15.1) es lo único de las
otras familias que mejoró el 1X2 en el backtest. En esta tanda:

- **Cuando los dos lados apuntan a lo mismo, acertó:**
  - Leones–Libertad: Leones no pierde en casa el 78 %, Libertad no gana de
    visita el 79 %; ganó el local 4-1. El motor, el EFE y las dos tarjetas
    iban al visitante.
  - Fortaleza–Cali: 76 % y 77 % contra el visitante; empate. El parte subió
    el empate solo 2 puntos.
  - Palestino–Colo Colo: 70 % y 57 %; empate. El 1X2 siguió al mercado
    «sin dato propio», y el dato estaba.
  - Pumas–Tigres: 56 % y 66 % de no ganar los dos; empate.
- **Cuando era de un solo lado, falló:** Coritiba (el rival no ganaba de
  visita 0 de 15, y la racha se cortó ese día) y Vélez (no gana el 70 % fuera,
  y ganó 0-5).

**Propuesta:**

1. **Los dos perfiles DC de la condición apuntando al mismo resultado** (el
   local no pierde y el visitante no gana, cada uno en dos de cada tres
   partidos o más) **son un hecho de ESTE partido** en el sentido del 6-B. Con
   ese hecho, el 1X2 puede apartarse del mercado hacia ese lado, nombrándolo:
   «+N al empate y al local por los dos perfiles DC (78 % / 79 %)».
2. **Un perfil extremo de un solo lado no alcanza.** Es frecuencia del
   equipo, no un hecho del partido, y no mueve el 1X2 sobre el mercado.
3. ⚠️ **«Dos de cada tres» es un umbral nuevo**, de lectura, sin peso en la
   app. El backtest del perfil DC contra el mercado sigue sin correrse (lo
   decidiste el 17/10). Si se aprueba, la serie se mide en Aprendizaje antes
   de darle más peso.

### 3. La tarjeta débil de la condición no se sigue por defecto, y la lista de lo que no es un hecho

**Lo medido.** Los números de arriba: la tarjeta fuerte acierta el 59 % y
conviene seguirla; la débil de la condición acierta el 26-34 %, peor que el
azar; y cuando el analista va contra la tarjeta, gana él (63 contra 29). Las
lecciones donde ir contra la tarjeta falló comparten la razón, que no era un
hecho:

- **Rotación sin confirmar:** Tigre–Tucumán (una sola cadena de prensa, nivel
  C).
- **Frecuencia propia:** Gremio («0 de 15 de visita»), Portuguesa (frecuencia
  de empates), Cerro Largo (el empate en casa).
- **La brecha del EFE con T.54:** Palestino, City.
- **El H2H de la sede:** Aucas («nueve visitas sin ganar»).

**Propuesta (paso 1.6):**

1. **La tarjeta débil de la condición no se sigue por defecto.** Con guía
   `condicion` y tarjeta débil, la espina sale de los skills (procedimiento,
   paso 3) y el `porque` no la cita como apoyo.
2. **Lo que NO es un hecho para ir contra una tarjeta fuerte**, escrito como
   lista en la regla (c): la frecuencia propia del equipo (de local, de
   visita, de empates), un perfil DC de un solo lado, una rotación que no
   confirmó el club o una fuente de nivel A, la brecha del EFE con T.54 /
   R-KT.2 / ESCALA-LIGAS, y el H2H de la sede.
3. **Sin tocar** la regla (a): `cero` sigue necesitando un hecho. Los datos
   (22 % contra 20 % de frecuencia) la sostienen.

### 4. El falsador mide conversión o vía, y el marcador lee el volumen de los dos lados

**Lo medido:**

- **Sporting–Viseu:** el falsador medía volumen (xG) y no sonó con el
  favorito perdiendo 1-2: Sporting superó en xG y Viseu convirtió su
  transición.
- **Aurora–Real Tomayapo:** el falsador «si genera peligro en juego abierto,
  la lectura está mal» se cumplió y el 1X2 se sostuvo.
- **Central Córdoba–Vélez:** el marcador 0-1 salió de «Vélez genera poco»
  (0,9 de xG) contra un local que concede 1,81. Salió 0-5.
- **Jaguares–Tolima:** un under con un ataque que remata mucho y no
  convierte, contra un bloque que concede volumen.

**Propuesta:**

1. **6-C:** el falsador no se escribe sobre el volumen (xG, remates,
   posesión), que no separa el resultado. Se escribe sobre la **conversión**
   o la **vía de gol** que la lectura da por cerrada.
2. **Paso 3.5:** el marcador lee **el volumen de los dos lados**: lo que
   genera uno contra lo que concede el otro (`/equipos/{id}/stats`, xG a
   favor y en contra). El xG medio de un equipo no viaja solo.

## Lo que NO se propone (n chico)

- **Riesgo alto en las dos burbujas → más empate.** Napoli–Roma, Cerro Largo
  y Sunderland–Leeds terminaron con las dos rachas cortadas. Tres casos; la
  regla del empate ya admite «dos burbujas negativas enfrentadas». Candidato.
- **El motor por encima del mercado con dos DT nuevos o ESCALA-LIGAS.**
  Nacional–Braga, Sporting–Viseu, Villa–City, Aucas y Toulouse: el motor
  estuvo más cerca. La serie DIV-MOTOR-MERCADO sigue contándose; con la v4.1
  pegada al mercado y acertando el 66 %, no se cambia el ancla por cinco
  casos.
- **La tarjeta fuerte «por poco» en una racha de un partido** (Fortaleza 52 %,
  Mirassol 50 %): candidato a medir por largo de racha.
- **Los dos gatillos del débil en la matriz** (Bolívar–Vinto): es de
  `efe-dashboard`, va a su próxima revisión.

## Cómo se aplica si se aprueba

1. **Skill:** `SKILL.md` a v4.2, con los cambios en los pasos 1.6, 3.5, 6-A,
   6-B y 6-C, y el changelog arriba.
2. **App:** `lecciones.CORTE_VERSION["sad-analysis"]` suma `("v4.2",
   "2026-10-28")`. No hay código nuevo: el delta ya está en
   `/cuotas/{id}/historial` y los perfiles DC en `/burbujas`.
3. **`docs/COWORK.md`:** el prompt suma una línea: los dos perfiles DC
   alineados como hecho, y uno solo no.
4. Zip para subir a la cuenta.
