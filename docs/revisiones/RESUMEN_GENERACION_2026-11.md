# Generación de noviembre 2026 · resumen para decidir

**Encargo del usuario (09/11/2026, ~20:45 de Lima):** «no es posible que no
lancemos una nueva versión de cada skill; fue una semana de muchísimos errores
y hay aprendizajes que hicimos aparte conversando».

**Estado:** cuatro PROPUESTAS sin aprobar. No se tocó ningún
`docs/skills/*/SKILL.md`, ni `CORTE_VERSION`, ni el estado de ninguna lección.
Eso se hace después de que el usuario apruebe, por cambio o entera.

| Skill | Propuesta | Versión | Cambios |
|---|---|---|---|
| sad-analysis | [`SAD_v4.5_propuesta.md`](SAD_v4.5_propuesta.md) (ampliada) | v4.4 → v4.5 | 1-9 + «Medido en conversación» 10-19 |
| teorema-del-echado | [`TDE_v0.1.26_propuesta.md`](TDE_v0.1.26_propuesta.md) (ampliada) | v0.1.25 → v0.1.26 | 1-14 |
| efe-clasificador + efe-dashboard | [`EFE_v1.10_propuesta.md`](EFE_v1.10_propuesta.md) (nueva, absorbe la `EFE_v1.10`) | v1.9 → v1.10 (decidido 10/11) · dashboard v1.12 → v1.13 | 1-12 + D1-D4 |
| diagnostico-tactico | [`DTP_v1.8_propuesta.md`](DTP_v1.8_propuesta.md) (ampliada) | v1.7 → v1.8 | 1-14 + génesis del gol |

## Con qué se hizo, y qué quedó fuera

- **Dossier del 10/11 a las 02:13 UTC** (21:13 de Lima del 09/11):
  `GET /analisis/cowork/revision/{skill}` y todas las lecciones pendientes de
  cada skill, de los partidos del 01/11 al 09/11.
- **Se cambió el plan a pedido del usuario (09/11, ~21:10):** no se esperó a
  que cerraran los ~50 veredictos de esa noche. Esos veredictos (y lo que se
  haya cerrado después de las 02:13 UTC) **quedaron fuera**: sirven para
  **comprobar** lo propuesto. Cada cambio de cada propuesta lleva su línea
  **«Se sostiene si… / Lo tumba si…»** al lado, con lo que tendría que verse en
  esos veredictos.
- Lecciones pendientes al corte:

| Skill | Pendientes | Partidos | Nuevas desde las propuestas del 08/11 | De copa | Cuarentena que enseña |
|---|---:|---:|---:|---:|---:|
| sad-analysis | 237 | 152 | 58 (40 partidos) | 5 | 1 |
| teorema-del-echado | 865 | 236 | 227 (67 partidos) | 17 | 11 |
| efe-clasificador | 568 | 236 | 152 (67 partidos) | 9 | 4 |
| diagnostico-tactico | 1032 | 236 | 268 (67 partidos) | 18 | 10 |

- **Jev no marcó ninguna lección pendiente que pida mover un número.** Esta
  tanda fija **rúbrica**. Ningún peso, umbral ni corte se mueve sin medir. Lo
  que haría falta medir va con ⚠️.
- Los 4 casos que todavía esperan su cuarentena (LDU 1631509, Palmeiras
  1492426, Manta 1639824 y 1639827) **no sostienen ninguna regla**. En
  sad-analysis, TDE, EFE y DTP ninguna regla nueva se apoya en ellos.
- **El modo de fallo `lectura_efe` (130 fallos, el más grande) casi nunca es
  del EFE.** 125 de los 130 están en los dossiers del TDE y del DTP, y citan
  reglas de esos skills (disciplinas 44, 65 y 66 del TDE; M2, M5 y veredicto
  por rama del DTP). Las 46 del DTP son todas del DTP. La taxonomía de Jev no
  tiene otra casilla de «mala lectura», así que todo cae ahí (lo mismo que dice
  la incidencia 1062). Solo unas 14 vienen de un insumo del EFE: el banco
  probable, una línea nueva, el sistema con DT nuevo o la rotación. Eso va al
  cambio 10 del EFE.

Leyenda: **[rúbrica]** texto del skill, sin números · **[DECIDE]** pide la
decisión del usuario · **[MEDIR]** ⚠️ medir antes · **[APP]** calculable, lo
hace la app, no la corrida.

---

## sad-analysis v4.4 → v4.5

**De dónde sale:** las 179 lecciones del 08/11, con sus cambios 1-7 intactos,
más 58 nuevas del 08-09/11 (29 aciertos, 8 parciales y 21 fallos, todas
`ciega` + `PRE`). Además, lo medido conversando con el usuario del 03 al 09/11
y los puntos 24-26 de `DEUDA.md`.

1. El origen de la burbuja (inflada por batacazo o construida por invicto),
   medido contra la casa. **[DECIDE]**: choca con la decisión del 03/11 (no se
   busca valor contra la casa), porque propone mover el número. Ver el 19.
2. El nivel a favor y el riesgo del reventón en la lectura del 1X2. Refuerzo:
   Puebla 1551036, OFI, América de Cali y Levante; en contra (condicional):
   Porto 1575544 y Elche 1570445. [rúbrica]
3. Prudencia con la burbuja en el extremo. Refuerzan América–Pumas, Brighton y
   Fenerbahçe, pero solo la mitad de la regla. [rúbrica]
4. Refuerzo de América de Cali y de la medición del punto 11. [rúbrica]
5. Lo que está en juego incluye a quién le sirve el empate (Carabobo–La
   Guaira 1646935). [rúbrica]
6. El falsador del dominio: Vitória SC–Porto propone el xG. **[DECIDE]**
7. Siete refuerzos (Rayo, Cuenca, Lazio, Aucas, PSV, Portuguesa, Union SG).
   [rúbrica]
8. **Nuevo.** Riesgo alto o muy alto en las DOS burbujas: el empate se nombra
   como la salida que corta las dos, y el elegido no sube sobre el mercado
   (Chivas–León 1551037, Barcelona SC–LDU 1639804, Lazio–Napoli 1550193).
   [rúbrica] [MEDIR] [APP: alerta `RIESGO-EN-LOS-DOS`]
9. **Nuevo.** La cadena (el pronóstico por equipo) dice lo mismo que el parte
   (Sport Boys 1549552, Llaneros 1549853). [rúbrica] [APP: `CADENA-VS-PARTE`]

**Medido en conversación (sección propia, 10-19):**

10. Empate: la casa lo calibra tramo por tramo. Refuerza 6-B («el empate parte
    del mercado») y 1.6 (c) con el 17,7 contra 28,7 % (n 175). En copas, el
    empate por debajo de la casa queda como observación. La «12» no cambia
    nada.
11. Perfiles DC alineados (n 195): dicen «la visita no gana» y el mercado ya lo
    cobra. Propone además que no resten a la visita por debajo del mercado
    (endurece la v4.4). **[DECIDE]**
12. Cómo fallamos (45 % empate, 55 % el otro lado): refuerza 6-B; nada que
    cambiar.
13. Elegir la visita: a la par del mercado gana; apartarse cuesta. Refuerza
    «el número del favorito es el del mercado». La visita al 40-49 % queda
    como observación. [APP]
14. Win rate por tramo desde el 28/10: nada que cambiar (el 60+ es el más
    parejo).
15. Rachas entre partidos: no hay dependencia; refuerza la Ley 5 suspendida.
16. Anticulebra (DEUDA 24): observación sin regla.
17. Resaca del clásico (DEUDA 25): pista con su regla fija de medición.
18. Inflada o construida (DEUDA 26): es el cambio 1; espera 100+ casos por
    grupo.
19. Decisión del 03/11 escrita en 6-B: «el parte no busca valor contra la
    casa». **[DECIDE]**: choca con el cambio 1 y con el «Cuándo se reabre» por
    valor.

Preguntas abiertas: si K-EXTREMO es la única excepción a «no apartarse del
mercado» (Twente y Panathinaikos), y si el corte por defecto en el extremo pasa
a `pronostico` (Heerenveen).

## teorema-del-echado v0.1.25 → v0.1.26

**De dónde sale:** 865 pendientes, de las que 227 son nuevas, de 67 partidos
del 08-09/11 (112 aciertos, 47 parciales y 68 fallos). Se leyeron enteros los
115 fallos y parciales nuevos.

1. «Sostiene el punto»: qué no es motivo. Refuerzan Estrela–Benfica y
   Vitória–Porto; en contra, PAOK–Olympiakos 1593357. [rúbrica]
2. El defecto «sigue atacando» es solo de los tres. La racha entra a la lista
   de lo que no es motivo (Sunderland). [rúbrica]
3. El antecedente tiene que coincidir también en el marcador y en la cuenta de
   jugadores. Refuerzan Lille y Puebla; en contra, Recoleta. [rúbrica]
4. Con roja propia, la ventana arranca en la roja (Jaguares, León,
   Gençlerbirliği). [rúbrica]
5. El banco se toma de la hoja (10 partidos). [rúbrica] [APP]
6. La pieza del seguro se nombra, y el cierre anota cuándo salió (León,
   Barcelona). [rúbrica] [APP]
7. S1 sobre los titulares que van al choque (7 lecciones). [rúbrica]
8. F2 subido a mano. **[DECIDE]**. Ninguna lección nueva lo toca.
9. Confirmaciones sin texto nuevo (disciplinas 65, 66, 61, 43, 14, 23, 17 y
   24). [rúbrica]
10. **Nuevo.** La ventana de la vía del banco cuenta desde que el banco entra
    (Asteras–Kalamata 1593354, Elche–Betis 1570445). [MEDIR] [APP]
11. **Nuevo.** Con 0-0 de visita y el empate útil, la sobreexposición de la
    hora pide un hecho de hoy (Atromitos 1593356, Levante 1570444). Tensión
    con el cambio 1: **[DECIDE]**.
12. **Nuevo.** S1 desde la base: las amarillas y rojas de `sanciones.py` en
    `GET …/tde/{id}`. [APP]
13. **Nuevo.** La rama del TDE y el M3 del DTP del mismo equipo dicen lo mismo,
    o se nombra cuál manda (Chivas–León 1551037, Union–Köln 1575207).
    [rúbrica]
14. **Nuevo · incidencia 1056.** Las ramas del que persigue (`siRecibePrimero`,
    `siLeEmpatan`, `siIguala`) heredan el SOB2 de `nivelFocoPersiguiendo` del
    DTP, y `HERENCIA-DTP` compara también la rama (Westerlo–Charleroi
    1558679). **[DECIDE]**. Hoy la app hereda solo el de la base
    (`HEREDA_SOB2 = ("siMarcaPrimero",)` en `parte.py`) y
    `nivelFocoPersiguiendo` se guarda pero no se usa. Se recomienda la opción
    (a): heredar y avisar, sin recalcular partes viejos. **Ojo:** el skill del
    DTP todavía dice «no se hereda hasta que el usuario decida». Si se aprueba,
    hay que cambiar también esa línea del DTP y la de `DEUDA.md`.

## efe-clasificador v1.9 → v1.10 (+ efe-dashboard v1.12 → v1.13)

**De dónde sale:** 568 pendientes, de las que 152 son nuevas (76 aciertos, 31
parciales y 45 fallos). Se leyeron las 88 `lectura_efe` del TDE, el DTP y el
EFE. Absorbe la `EFE_v1.10_propuesta.md` del 08/11 (sus cambios 1-6), que no se
borró.

**El número de versión lo decide el usuario.** Las lecciones justifican una
1.10, no una 2.0: no mueven números ni cambian la estructura de la rúbrica.
Sería 2.0 si se aplica junto con el núcleo, que sí cambia la forma de los
archivos.

1. El rehacer empieza por la tabla F1; una baja que está en la hoja pasa a
   disponible; la F1 lleva a los candidatos al puesto de cada baja. Es la falla
   más grande (113 lecciones con titulares sin fila F1), y la causa es la
   rutina: el modo `rehacer` no carga el EFE. [rúbrica] [APP] **[DECIDE:
   incidencia 1068]**
2. El sistema va condicionado con D1 🔶 o con T.54 corta (Genk, Cercle). ¿Se
   estira a toda serie del DT de menos de 6-8 partidos? **[DECIDE]**
3. EJE-DEBUTANTE sobre la línea entera del grid, y nunca condicional con el once
   a la vista. [rúbrica] [APP]
4. B6 sin fuente es «sin dato»; el suplente sin rodaje es una vía a vigilar
   (Aucas). [rúbrica] [APP]
5. Sanciones: la roja calculada es Baja con su rama, y el ciclo de amarillas es
   Duda. Kortrijk 1558673 lo desmiente en parte (la roja calculada jugó; puede
   ser un dato mal leído). **[DECIDE]** [APP]
6. La rama «once alternativo» se abre por un hecho; el porcentaje se condiciona
   solo con la costumbre del DT. **Afloja la v1.7.** [MEDIR] **[DECIDE]**
7. **Nuevo.** La F3 en DEF se lee en el volumen concedido; el marcador lo decide
   el arquero. Corrige el «no el volumen» de la v1.9. [rúbrica]
8. **Nuevo.** La F3 en ATK se paga en volumen, en dónde se remata o en la
   conversión; con un recambio con rodaje no anuncia nada. [rúbrica]
9. **Nuevo.** La baja de un titular fijo con un recambio sin minutos es vía del
   rival aunque la zona quede en ámbar (Lens, AEK). **[DECIDE: regla o
   nota]**
10. **Nuevo.** «Banco probable» en la F1, y B5 nombra el banco por rol; DTP,
    TDE y la matriz lo toman de ahí. Es el insumo del EFE que más aparece en
    las `lectura_efe` de otros skills. [rúbrica] [APP]
11. **Nuevo.** D3 con T.54 y pocos casos lleva caja de sensibilidad (Estrela).
    [MEDIR] [APP]
12. **Nuevo.** La brecha entre los dos, en la misma base (5 casos en contra y 1
    a favor). [MEDIR]

Dashboard v1.13: D1 la caja dibuja las dos variantes del sistema · D2 el banco
de la matriz sale del banco probable de la F1 (Independiente 1493235) · D3 la
nota F3 copia las filas nuevas de la tabla · D4 se actualiza la descripción.

## diagnostico-tactico v1.7 → v1.8

**De dónde sale:** 1032 pendientes, de las que 268 son nuevas (84 fallos, 37
parciales y 147 aciertos), todas acreditables. Acompaña al
`DTP_autopsia_gol_estudio.md`.

1. Volumen contra lo concedido; la referencia no sale de un solo partido ni de
   una racha (58 lecciones; en contra, NEC 1552223). **[DECIDE: ¿manda la
   diferencia de volumen o la lista de vías cumplida?]**
2. La vía entera, la condición con su contrario; ceder no es una señal.
   [rúbrica]
3. La posesión «igualado» y «arriba» por separado (en contra, Heerenveen
   1552221). [rúbrica]
4. La pelota parada es condicional para el que cede (Santa Clara, Ameliano).
   [rúbrica]
5. El banco y los penales se sacan de la hoja (6 penales pateados por alguien
   que entró del banco). La lista tiene que poder decir «el mismo» (AZ
   1552224). [rúbrica] [APP]
6. El grid se copia (Beşiktaş, Le Havre, Rayo, América de Cali). [rúbrica]
   [APP]
7. La vía de expulsión con todas las piezas de la línea del duelo (Monterrey).
   [rúbrica]
8. Quién queda atrás tras los cambios, en todas las ramas (15 lecciones).
   [rúbrica] [APP]
9. MECANISMO-ABIERTO: el conteo a mano sale bien. [rúbrica]
10. El reconvertido también ataca: sin casos nuevos. [rúbrica]
11. **Nuevo.** El perfil de balón del rival se mide en su condición de hoy, no
    con el promedio de la temporada (OFI, Genk, Olympiakos…). **[DECIDE]**: el
    ejemplo de Paderborn de la v1.7 puede leerse en contra. [APP]
12. **Nuevo.** El lateral o defensor fresco que entra es banco ofensivo (Man
    United, Bucaramanga, Porto, Chivas–León, Başakşehir, Bolívar). [rúbrica]
    [APP]
13. **Nuevo.** Los penales concedidos en serie son del equipo. Hay 3 casos,
    pero 2 son del mismo cruce. **[DECIDE]** [APP]
14. **Nuevo.** Un reconvertido o una línea nueva es una vía a verificar, no un
    mismatch dado (Getafe, Lille–Bodø, Napoli–Lazio). [rúbrica]

Génesis del gol: 24 lecciones nuevas dicen «sin crónica». [rúbrica] [APP]

`rolesVsGrid`: `ROLES_GRID_REHACE` sigue en `False`. Solo una lección lo nombra
(Belgrano 1493233, hallazgo real). La medición propuesta para decidir es cruzar
`contraElOnce.rolesVsGrid` en los 6 casos del cambio 6 (calculable, sin
tokens). Nada de lo pendiente del DTP en la app está hecho todavía.

---

## Lo que pide la decisión del usuario, en un lugar

| # | Decisión | Dónde |
|---|---|---|
| 1 | ¿El origen de la burbuja contra la casa entra, si la decisión del 03/11 dice que no se busca valor? | SAD 1 y 19 |
| 2 | ¿K-EXTREMO es la única excepción a no apartarse del mercado? | SAD, «NO se propone» |
| 3 | ¿Los perfiles DC alineados prohíben restar a la visita bajo el mercado? | SAD 11 |
| 4 | ¿El xG entra al falsador del dominio? | SAD 6 |
| 5 | ¿F2 se puede subir a mano? | TDE 8 |
| 6 | ¿Con 0-0 de visita y el empate útil, la sobreexposición de la hora pide un hecho de hoy? (tensión con TDE 1) | TDE 11 |
| 7 | **Incidencia 1056**: ¿las ramas del que persigue heredan el SOB2 del DTP? (recomendado: sí, heredar y avisar, sin recalcular partes viejos) | TDE 14 + línea del DTP |
| 8 | ¿El EFE es 1.10 o 2.0? | EFE, «Estado» |
| 9 | Incidencia 1068: ¿el rehacer carga el EFE y empieza por la F1? | EFE 1 |
| 10 | Sistema condicionado: ¿a toda serie corta del DT? | EFE 2 |
| 11 | Sanción calculada: ¿Baja o Duda? (Kortrijk; recomendado: opción (a) hasta verificar) | EFE 5 |
| 12 | Once alternativo condicionado solo por la costumbre del DT (afloja la v1.7) | EFE 6 |
| 13 | Recambio sin minutos en zona ámbar: ¿regla o nota? | EFE 9 |
| 14 | Volumen contra vías cumplidas: ¿cuál manda? | DTP 1 |
| 15 | El perfil de balón en la condición de hoy contra el ejemplo de Paderborn | DTP 11 |
| 16 | Penales en serie con 3 casos (2 del mismo cruce) | DTP 13 |
| 17 | ¿Jev tiene una casilla propia de «mala lectura» del TDE y del DTP, para que `lectura_efe` deje de recibir todo? | EFE A0 · DTP |

## Lo que pide medir antes (⚠️)

- SAD 8: la frecuencia del empate con riesgo alto en las dos burbujas, contra el
  empate del mercado.
- SAD 1 / DEUDA 26: inflada contra construida, hasta 100+ casos por grupo.
- TDE 10: la ventana de la vía del banco desde la entrada.
- EFE 6: la costumbre de rotación del DT (A8).
- EFE 11: el acierto de D3 con 1-3 casos (A7).
- EFE 12: la brecha en la misma base (A6).
- DTP: la banda de «parejo» para el volumen y el valor por penal (backtest,
  como en el 08/11), y `rolesVsGrid` sobre los 6 casos.

## Cómo comprobarlo con los veredictos que quedaron fuera

Cada cambio trae, en su propuesta, la línea **«Se sostiene si… / Lo tumba
si…»**. Para el DTP hay además una tabla, en la sección de comprobación. El
procedimiento:

1. Bajar las lecciones de los veredictos cerrados después del 10/11 a las 02:13
   UTC (`GET …/lecciones?skill=…&estado=pendiente`, quedarse con las que no
   estaban en este dossier).
2. Para cada cambio, buscar sus casos por `reglaTocada` y leer si sostienen o
   tumban.
3. Un cambio que tumban no se aprueba como está: vuelve a la propuesta con el
   caso.

---

## El núcleo de los skills: las 5 dudas abiertas, con recomendación

`NUCLEO_SKILLS_propuesta.md` (03/11) **no se aplicó**. Cada propuesta marca, en
su sección «Núcleo e historial», qué del skill nuevo es núcleo (lo que lee la
corrida) y qué es historial (casos y de dónde salió, para
`references/HISTORIAL.md`).

1. **Disciplina 35 contra 55 del TDE: ¿`F1` sin XI confirmado es `sin dato` o
   nivel C?** Recomendación: **vale la 55 (nivel C)**. Es la posterior
   (v0.1.19), es la que aplica la corrida y es coherente con P1 del DTP y D2
   del dashboard («el once probable es nivel C»). La 35 se copia al historial
   como derogada por la 55.
2. **Disciplinas 34 y 37, y la regla de `P(gol)` (T1, T4, T7): ¿vigentes,
   reescritas o caídas?** Recomendación: **la 34 (rango conjunto en la caja)
   se copia vigente**, porque no depende del riesgo compuesto y la caja la
   necesita. **La 37 se reescribe sobre IE/ISE** (la ventana se declara para la
   vía de índice mayor y, a menos de 5 puntos, las dos), porque el núcleo ya la
   cita. **La de `P(gol)` con ejecutor de penales se declara caída** con la
   suspensión de la v0.1.20, salvo que el usuario quiera reabrir esa tabla.
3. **`registro.csv` en la corrida: ¿solo un Grep por equipo para `F3`?**
   Recomendación: **sí**. Ahorra 16,5 K por subagente, la regla de `F3` sigue
   igual, y la copia empaquetada ya se declara obsoleta salvo chequeo de
   sha256.
4. **¿D1 («el suplente de impacto es factor X») entra también al barrido fijo de
   F5 de la rúbrica?** Recomendación: **sí**, como quinta lista. Coincide con
   el cambio 10 del EFE v2.0 (banco probable en la F1). Conviene aprobarlo junto
   con ese cambio.
5. **¿El encargo dice explícitamente si carga `efe-dashboard`?** Recomendación:
   **sí, y que no lo cargue en `partes`**. La matriz la escribe el parte y el
   dashboard es visualización. Si se aprueba D2 del dashboard (el banco de la
   matriz sale de la F1), esa regla va también al prompt o a sad-analysis, para
   que no quede solo en un skill que no se carga.

## Después de aprobar

Por cada skill aprobado: redactar en `docs/skills/<skill>/SKILL.md`, sellar
`CORTE_VERSION`, y anotar en `SUBIDA_VERSION` la hora en que el usuario sube
el zip. Las lecciones pasan a `aplicada` o `descartada` con
`aplicadaEn`. Lo marcado [APP] va al mantenimiento como pendientes de
`PENDIENTES.md`.

---

## Actualización del 10/11 (segundo corte, 04:29 UTC)

Ya se cerraron todos los veredictos (0 pendientes). Las 315 lecciones nuevas, de 29 partidos del 07 y el 08/11, se usaron para COMPROBAR cada cambio. Cada propuesta lleva, por cambio, su «Comprobación 10/11» y al final una **Tabla de cambios**.

**Decidido por el usuario el 10/11**
- **Incidencia 1056: APROBADA, opción (a) «heredar y avisar».** Es el TDE 14 y el DTP 16: sin recalcular partes viejos y con el texto del DTP reemplazado. En la app falta marcarla `aprobada` con la llave maestra (🔑, tarjeta Decisiones pendientes): el token de Cowork no puede.
- **EFE: v1.10, no 2.0.** El archivo es `EFE_v1.10_propuesta.md`. Absorbe la propuesta del 08/11, que queda en la historia de git.
- **Origen de la burbuja (SAD 1):** sigue vigente la decisión del 03/11, que DEUDA 26 (08/11) confirma y que ninguna decisión posterior contradice. El dato «contra la casa» es la fuente, no el objetivo. Si con 100+ casos por grupo se confirma sobre nuestro win rate, mueve la confianza del elegido, nunca el 1X2.

**Lo que trajo el segundo corte**
- **Ningún cambio cae, salvo el EFE 6.2** (la costumbre de rotación del DT condiciona el porcentaje). Con calendario exigente rotaron 4 de cada 5 DT. Se propone sacarlo y mantener la v1.7. **[DECIDE]**
- **Cambios nuevos:**
  - SAD 20: el banco del rival que nombra el falsador también frena la carga del 1X2. Cuatro fallos: Newell's, Viseu, Everton de Viña y Alianza Lima.
  - TDE 15: «sigue atacando» se lee por la amenaza, no por la posesión. Casos: Coquimbo, Medellín y Tolima.
  - EFE 13: con un once tardío, de menos de 20 minutos, la F1 queda «sin verificar». Casos: Fortaleza e Instituto–Newell's.
  - DTP 15: la vía del que persigue tiene que sobrevivir a los cambios habituales del DT. Casos: Huachipato, Alianza Atlético y Palestino.
- **Para decidir:**
  - SAD 2: la mitad de las espinas «sigue» contra riesgo alto se cortaron. La recomendación es aprobarlo como rúbrica.
  - EFE 3: la frase del condicional pasa al aviso de la app.
  - DTP 8: el rearme del medio tiene 2 casos limpios.
  - DTP 14: «con la vía nombrada, la rama sube».
- **1068, recomendación (c) empezando por la (b).** Con el once a la vista, 31 lados de 27 partidos tenían titulares sin fila. En el segundo corte, 18 de 20 lados tenían 1 o 2 filas de menos, que es cruzar listas. En 8 de esos 20 lados el jugador sin fila marcó o asistió. La (a), que el rehacer cargue el EFE, se usa solo con 3 o más titulares fijos cambiados o con otro arquero.
- **Para la app (nuevo):** guardar a qué hora llegó la formación y marcar la que la API corrigió después del pitazo. Pasó en 6 partidos.

---

## Decisiones del 10/11 y estado: LISTAS PARA REDACTAR

El usuario decidió el 10/11: la **1068 con la opción (c)**, empezando por la (b), y **«lo demás como recomiendas»**. Cada propuesta lleva su sección «Decisiones del 10/11» y su «Lista para redactar», con las anclas comprobadas contra el SKILL.md vigente y el texto exacto de cada cambio. **Ninguna tiene bloqueos para redactar.**

| Skill | Entran al SKILL.md | Notas o candidatos | Solo app | Afloja algo vigente |
|---|---|---|---|---|
| sad-analysis v4.5 | 15: 1-9, 20 y los puntos 10, 11, 13, 15 y 19, más el changelog | 5 candidatos, 6 observaciones | 13 | no |
| teorema-del-echado v0.1.26 | 12: 1-8 y 12-15, más el changelog | 9 y 11 fuera, 10 a medir, 7 candidatos | 13 | no (el 4 corrige una frase que 8+ casos desmienten) |
| efe-clasificador v1.10 (+ dashboard v1.13) | 10: 1, 2, 3, 4, 5, 6 sin el 6.2, 7, 8, 10 y 13; D1-D4 | 9 y 11 como nota; 12 y 6.2 fuera | 11 | **sí, dos**: el 4 (la vía firme pasa a «vía a vigilar», 8 casos) y el 5 (el ciclo de amarillas pasa a Duda) |
| diagnostico-tactico v1.8 | 15: 1-9, 11, 12, 14, 15, 16 y la génesis, más el changelog | 4 candidatos (rearme del medio, 10, 13, seguro «sin»), 5 notas | 5 | no |

**Decisiones que aplicó cada subagente y conviene mirar al redactar**
- **SAD 11:** para que no choque con «el favorito no se recorta» (v4.1), lo que suben los perfiles DC al empate sale del local, y con el local en 50 % o más el empate no se aparta por los perfiles. Lo agregó el subagente; la propuesta no lo traía.
- **SAD 9** entra con solo 2 casos propios, porque endurece una regla. Con la regla conservadora sería candidato.
- **DTP 10** (el reconvertido que ataca) queda como candidato, aunque la propuesta lo subía a regla.
- **EFE 5** se apoya en tres sanciones falsas de la UEFA que salían de la regla vieja de `sanciones.py`.
- **A0 (Jev):** la (a): `lectura_efe` pasa a ser `lectura` del skill de su dossier, y lo que Jev ya selló no se reetiqueta. Vale para el EFE y el DTP.

**Lo que hay que subir junto y lo que falta en la app**
- **TDE 14 y DTP 16 (la 1056) se suben juntos.** La app (`HEREDA_SOB2` en `parte.py`) la implementa el mantenimiento; hasta entonces, el analista copia el SOB2.
- **1068 (c):** primero la app (fila `delOnceOficial`), después `EFE-RECOMPUTO-PENDIENTE` en `GET …/rehacer` y por último la rutina `corrida-sad`, en tres lugares: líneas 255, 229-237 y 291-293. Hoy no existe ninguno de los tres, así que esa línea de la rutina no se activa hasta que la app lo traiga.
- **El banco probable** lo piden el EFE 10, el DTP 5 y el TDE 5 con tres nombres distintos: en la app tiene que ser una sola lista.
- **La `certeza` de las sanciones (A3)** la tienen que leer también el DTP 7 y el TDE 12.
- **La (f) de 1.7 del SAD** no opera hasta que `/burbujas` traiga `origen`.

**El núcleo:** las 5 recomendaciones de arriba quedan aprobadas («como recomiendas»), pero el núcleo **no se aplica en esta tanda**: es otro cambio, con su test (`test_nucleo_skills`), y conviene hacerlo después de subir estas versiones.
