# Propuesta de revisión · `teorema-del-echado` v0.1.20 → v0.1.21

**Estado:** PROPUESTA. No está aplicada en ningún lado. El skill vive en la
cuenta del usuario; esto es el texto para decidir y, si se aprueba, para
subir. Redactada el 21/10/2026 desde el dossier de la app
(`GET /analisis/cowork/revision/teorema-del-echado`, cohorte `c3-2026-09-23`).

## De dónde sale

- **138 casos ciegos PRE** de la cohorte vigente. Las lecciones atribuidas
  al TDE son 617, y de ellas 513 acreditan.
- La regla con más lecciones es la **disciplina 44** (reasignación
  condicional por primer gol): 211 lecciones acreditables, con 86 aciertos,
  63 parciales y 62 fallos. Aparece con cuatro nombres distintos que son la
  misma regla.
- **Ninguna de las 211 pide mover un número** (Jev, `proponeMoverNumero`).
  Todo lo de abajo es definición de dominio y declaración, la misma clase
  de cambio que el propio skill admite sin umbral binding: no toca pesos,
  fórmula ni compuertas.
- **Sesgo de atribución declarado:** quien cierra el caso nombra la regla
  sobre todo cuando algo falla. Muchos «fallos» del lado son el 1X2 o el
  marcador, con la disciplina 44 «declarada y cumplida» en la propia
  lección. Los conteos de abajo salen de buscar palabras en la prosa: son
  orden de magnitud, no tasas.

## Qué dice la disciplina 44 hoy

> En modo PRE se declara, para cada equipo, qué valor tomaría `SOB1` y si
> cambia el tipo modal si ese equipo marca primero.

Funciona: en la mayoría de los casos la rama que se jugó era una de las dos
declaradas, y la lectura útil del partido fue la reasignación, no la
ventana del reloj (la disciplina 50 ya lo intuía). Lo que fallan son **cinco
huecos de la regla**, siempre los mismos.

## Los cinco cambios propuestos

### 1. La reasignación cubre UN giro, y el partido suele tener dos

**Casos:** AEK en Shakhtar–AEK (0-1 al 28', 1-1 al 34', concedió dos en el
tramo final), Angers–Marseille (marcó al 14', le dieron vuelta antes del
descanso), Estudiantes–San Lorenzo (la rama disparó al 14' y el empate del
43' la deshizo), Aucas–LDU (1-0 al 12', empate al 45+4) y Albion–Torque
(«la reasignación debe declarar también qué pasa si le empatan»). Unos 50
textos mencionan el empate o la ventaja perdida.

**Propuesta, disciplina 44-bis:** además de «si marca primero» por equipo, se
declara **una línea para el empate posterior** («si le empatan antes del
75'»): qué vía reabre y desde qué minuto. La rama de ventaja **caduca** cuando
la ventaja se pierde, y el tramo se lee con la línea del empate, que
también se puntúa. Si el marcador se da vuelta antes de la ventana, aplica
la disciplina 24 (`rama_abandonada`) como hoy.

### 2. «Marca primero → administra» no es la rama por defecto del favorito, del obligado ni del que juega con uno más

**Casos:** Libertad 4-0 Guayaquil City (abrió al 40' y siguió atacando: 3
goles más antes del 67'), Santos 3-0 Querétaro, Hoffenheim («no administró,
castigó»), Aldosivi (obligado de tabla: con 1-0 siguió metiendo
delanteros), PSG en City–PSG (ni se echó ni administró la pelota: 46 %),
Mirassol (uno más desde el 14': «con superioridad el que marca primero no
administra») y Olimpia. Unos 23 textos.

**Propuesta:** en la línea «si marca primero», `SOB1 → 0` y la etiqueta
`ECHADA-VOL`/«administra» **solo se escriben si se nombra por qué ese
equipo administraría** (perfil, DT, antecedente de cierre). Para el
favorito por `μ_partido` con margen ≥ 0,30, el obligado de tabla y el que
juega con superioridad numérica, la rama por defecto es **«sigue
atacando»**. Su riesgo es la ventaja amplia temprana, que es
`rama_abandonada` por las disciplinas 3 y 29, no la echada. Es la
disciplina 6 aplicada a la rama: no se predice desde «va ganando», sino
desde qué le pasa a ese equipo.

### 3. La ventana de una rama se declara RELATIVA al gol que la abre

**Casos:** FC Cajamarca–UCV Moquegua («la ventana de una rama de
reasignación se declara RELATIVA al gol, nunca fija en el reloj»),
Betis–Porto (las dos concesiones a 7' y 14' del gol: la ventana anclada al
gol contuvo la ráfaga entera, la del reloj solo una), Leones–Emelec,
Real Sociedad–Deportivo y Racing–Valencia (rama sin ventana propia: «no se
pudo comprobar»).

**Propuesta:** cada rama lleva **su** ventana y se escribe «desde el minuto
del gol hasta +15» (o hasta +N, con el régimen de la disciplina 45 si es
SOB). La app ya la mide así. La ventana del reloj se sigue declarando y
puntuando para no romper la serie del sesgo tardío.

### 4. Una roja cambia la rama, y la 44 no lo dice

**Casos:** Mirassol (uno más desde el 14'), Palmeiras en Athletico–Palmeiras
(con la roja al 43' yendo ganando migró a `ECHADA-NUM` y no concedió),
Cerro Porteño («el riesgo llegó en la ventana pero por inferioridad
numérica») y Brentford (la roja cortó la rama a los 9'). Unos 25 textos.

**Propuesta:** la reasignación agrega **una línea condicional por
expulsión**, alineada con el candidato de la disciplina 16 ya declarado en
v0.1.12: roja yendo empatado o ganando → `ECHADA-NUM` y el ISE se anula;
roja yendo perdiendo → el ISE se agrava. Con estos casos más TDE-034, el
candidato de la 16 ya tiene evidencia para revisarse. **Decisión del
usuario:** aplicarlo o seguir esperando el umbral de ≥ 3 casos ciegos. Ya
los hay; falta contarlos en el registro.

### 5. El que persigue no siempre concede: a veces marca

**Casos:** Emelec («la exposición del que persigue rindió goles A FAVOR en
cinco y siete minutos»), IdV en Macará–IdV (37' expuesto, no concedió), San
Lorenzo, Carabobo, Lille (84' expuesto sin conceder), Boca–Vasco y
Athletico–Palmeiras (no concedió porque el rival en ventaja administró:
disciplina 14).

**Propuesta, solo declaración:** la rama `siRecibePrimero → SOB` se cierra
como «régimen observado» aunque no conceda, y el cierre separa tres
salidas: concedió · no concedió porque el rival administró (disciplina 14)
· marcó él. No es un fallo de la rama. El ISE mide el riesgo de conceder,
no el desenlace. Evita que la 44 acumule «fallos» que son la disciplina 14
operando.

## Lo que NO se propone

- **Ningún peso, ninguna compuerta, ningún umbral.** Las 211 lecciones no
  piden mover números, y el umbral binding (N ≥ 5 echadas ciegas en el
  esquema vigente) sigue sin cumplirse.
- **La declaración de `VENTAJA-INESPERADA` para el de menor `μ_partido`**
  (Sport Boys, Alianza Lima) ya está en el skill desde v0.1.17. Lo que
  falló fue que no se cumplió, no la regla. Va como recordatorio en el
  prompt de la corrida, no al skill.
- **El descendido que recibe primero no colapsa por definición**
  (Estudiantes de Río Cuarto remontó). Es un solo caso y va como candidato
  declarado, no aplicado.

## Cómo se aplica si se aprueba

1. El usuario aprueba (o corrige) los cinco puntos.
2. Se redacta la v0.1.21 del skill: changelog, disciplinas 44-bis y
   reescritura de la 44, y las notas de cierre de la 14 y la 16.
3. El usuario la sube a su cuenta.
4. En la app (🔑): abrir la revisión del TDE y marcar `aplicada`, con
   «v0.1.21», las lecciones que entraron.
5. La corrida (`docs/COWORK.md`) pide en `tde.bloques[].reasignacion` las
   líneas nuevas (empate y expulsión), y el veredicto mide la rama con su
   ventana relativa, como ya lo hace.
