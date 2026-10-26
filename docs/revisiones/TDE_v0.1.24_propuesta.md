# Propuesta de revisión · `teorema-del-echado` v0.1.23 → v0.1.24

**Estado:** PROPUESTA, sin aprobar. Redactada el 26/10/2026 a partir de las
autopsias de la corrida de veredictos del 26/10 (30 partidos del 25/10, 16
fallos del 1X2) y de una medición sobre la cohorte vigente entera
(`c3-2026-09-23`: 253 casos ciegos `PRE` con veredicto, sin cuarentena).
Nada de esto está en `docs/skills/teorema-del-echado/SKILL.md` todavía.

## De dónde sale

**Lo que dijeron las autopsias.** De los 16 fallos del 25/10, en 6 el débil
marcó temprano y administró sin romperse (Nacional–Braga 19', Nacional
UY–Liverpool 32', Emelec–G. City 45+2, Monterrey–Chivas 9', Aucas–Barcelona
8', Barça–Madrid). En 4 el favorito, persiguiendo, se expuso y recibió
otro (Barça 87', Sporting 74', Rio Ave 80' y 85', Aucas con diez). El TDE
tenía escritas las dos ramas; lo que faltó fue que esas ramas dijeran
**cómo termina** el régimen, no solo si se expone.

**Lo que dice la cohorte (253 casos).** El primer gol decide casi todo el
1X2:

| Primer gol | n | gana el elegido por el 1X2 | empate | gana el otro |
|---|---|---|---|---|
| del elegido | 141 | 76 % | 13 % | 11 % |
| del otro | 99 | 20 % | 26 % | 54 % |
| 0-0 | 12 | — | 100 % | — |

Y dos lecturas que el TDE ya calcula separan desenlaces.

**1. El ISE de la rama `siRecibePrimero` separa la remontada.** El equipo
que recibe primero, cualquiera de los dos, según el ISE de su rama
(disciplina 62):

| ISE de la rama | n | le meten otro | lo da vuelta | rescata algo |
|---|---|---|---|---|
| ≥ 7 | 38 | 66 % (IC 50-79) | **5 % (IC 1-17)** | 24 % (IC 13-39) |
| < 7 | 33 | 45 % (IC 30-62) | **21 % (IC 11-38)** | 39 % (IC 25-56) |
| sin número (partes anteriores al 22/10) | 170 | 60 % | 16 % | 34 % |

Solo con el favorito elegido por el 1X2 persiguiendo, la remontada con ISE
≥ 7 es **0 de 15**.

**2. Con la ventaja, manda el minuto del gol, no el IE.** El que marca
primero, por el minuto del gol:

| Primer gol | n | no pierde | gana |
|---|---|---|---|
| ≤ 15' | 86 | 79 % | 60 % |
| 16-30' | 46 | 78 % | 63 % |
| 31-45+ | 53 | 91 % | 70 % |
| 46-60' | 23 | 96 % | 74 % |
| 61-75' | 19 | 89 % | 68 % |
| 76'+ | 14 | 100 % | 93 % |

Y por su IE, cuántas veces se le escapa la ventaja (empata o pierde):

| IE | n | se le escapa |
|---|---|---|
| < 3 | 29 | 41 % (IC 26-59) |
| 3-5 | 148 | 32 % (IC 25-40) |
| ≥ 5 | 64 | 31 % (IC 21-43) |

El IE no separa: el que tiene IE alto no deja escapar más la ventaja que el
de IE medio. Es coherente con el semáforo del IE, que sigue bajo y con 0
positivos que cuenten.

**Sesgos y límites, declarados antes de proponer:**

- **n chico en las ramas con número.** El ISE de rama existe desde la v0.1.22
  (22/10), así que son 71 casos y no 241. Los intervalos de la remontada
  (1-17 contra 11-38) se tocan.
- **El ISE de rama se agrupa.** Casi todo cae en 8,3 o 10. El corte en 7
  separa «las tres SOB arriba o casi» del resto; no es un umbral fino.
- **Versiones mezcladas.** La cohorte junta partes de la v0.1.20 a la
  v0.1.23. Ningún parte medido es todavía de las versiones subidas el 25/10.
- **La tabla del minuto no es del TDE.** Es la frecuencia de la cohorte,
  que el skill no calcula. Entra como referencia, nunca como peso
  (disciplina 14).

## Lo que no se toca

- La fórmula del ISE ni la del ISE de rama: `(SOB1 + SOB2 + SOB3) / 3 × 10`.
- Los pesos del IE, las compuertas, las bandas y la ventana por defecto.
- El semáforo del IE: sigue bajo. La medición de arriba lo confirma; no lo
  levanta.
- La disciplina 61: la rama del que persigue se cierra por el régimen, no por
  el desenlace. La propuesta agrega una **declaración** del desenlace, que se
  mide aparte y no cambia cómo se juzga la rama.
- El registro: 35 filas, sin altas. Los casos de la app no son filas del
  registro.

## Los dos cambios propuestos

### 1. La rama del que persigue declara su desenlace (disciplina 65, nueva)

Hoy `siRecibePrimero` dice si el equipo se expone (las tres SOB y el ISE de
la rama), pero no qué suele pasar con ese régimen. La autopsia del 25/10 lo
leyó cuatro veces después del partido: «se expuso y le metieron otro».

**Propuesta:** toda rama que pasa a sobreexposición (`siRecibePrimero`,
`siLeEmpatan` cuando vuelve a empujar y `siIguala` cuando sigue empujando)
declara un campo **`desenlace`** con una de tres lecturas:

- **`se_rompe`:** concede otro antes de igualar y no remonta.
- **`rescata`:** iguala o da vuelta.
- **`abierto`:** el TDE no tiene base para elegir.

Además:

- **Con ISE de rama ≥ 7 la lectura por defecto es `se_rompe`.** Escribir
  `rescata` exige un hecho del partido: que el rival no sabe administrar
  (disciplina 14 al revés), un banco ofensivo documentado o una expulsión
  rival. Se escribe con su `porque`. En la cohorte, 2 de 38 lo dieron vuelta.
- **Con ISE de rama < 7 la lectura por defecto es `abierto`.**
- **Es una lectura, no un número.** No mueve el ISE, no entra al IE y no fija
  ninguna probabilidad. Lo que el 1X2 haga con ella lo decide sad-analysis,
  que ya lee las ramas.
- **Se mide aparte.** El veredicto compara el `desenlace` declarado con lo
  que pasó en el tramo de la rama. Con n ≥ 30 ramas jugadas por lectura se
  revisa si el corte en 7 se sostiene o hay que moverlo, con el backtest a
  la vista.

Origen: lo medido arriba, con remontada de 5 % (ISE ≥ 7) contra 21 %
(ISE < 7). Es candidata con un solo corte de la cohorte, y por eso entra
como lectura declarada y medible, no como regla dura.

### 2. La ventaja temprana es la frágil: la rama de ventaja se lee por el minuto (disciplina 66, nueva)

El IE mide el riesgo de que el que protege se parta. En la cohorte, el IE
del que marcó primero no separa si la ventaja se escapa (31-41 % en los
tres tramos); el minuto del gol sí (≤ 30': ~21 % de derrotas; desde el
31': ~6 %).

**Propuesta:**

- **`siMarcaPrimero` distingue la ventaja temprana (gol hasta el 30') de la
  tardía (desde el 31').** Con ventaja temprana, la línea de `siLeEmpatan`
  es la que más se juega: ya es obligatoria desde la v0.1.23 (disciplina 44
  (a)), y ahora se escribe **primero** y con su número.
- **Con ventaja tardía, el TDE no promete una rotura que la cohorte no
  muestra.** Una echada declarada desde el 31' con IE medio lleva en la
  nota la referencia «la ventaja desde el 31 se sostuvo 9 de cada 10 veces
  en la cohorte». Es una referencia, no un peso: la ventana y el IE se
  siguen escribiendo y puntuando para no romper la serie.
- **El IE del que lleva ventaja no se usa para anunciar el empate o la
  vuelta.** Para eso está la rama del rival que persigue (cambio 1). Es la
  disciplina 50 aplicada a la ventaja: el módulo dice cuándo es el
  instrumento y cuándo no.

## Lo que tendría que hacer la app si se aprueba

Va aparte del skill y se hace después de aprobar:

- **Parte:** `reasignacion.<rama>.desenlace` (`se_rompe` · `rescata` ·
  `abierto`) y su `porque`. El recibo avisa en `faltan` si una rama de
  sobreexposición no lo trae, o si dice `rescata` con ISE de rama ≥ 7 sin
  `porque`.
- **Veredicto:** en cada tramo de una rama jugada, dice si el desenlace
  declarado se cumplió. Las lecciones lo cuentan por lectura (Wilson,
  n ≥ 10).
- **Referencia calculada:** la tabla del minuto (no pierde según el minuto
  del primer gol) sale de la base y no se le pide al modelo. Puede viajar en
  `GET /analisis/cowork/tde/{id}` como `referencias.ventajaPorMinuto`, con
  su n.

## Los otros skills: no se tocan ahora

Se midieron sobre los mismos 253 casos las hipótesis de las autopsias que
tocaban a los otros skills, y ninguna se sostuvo:

- **sad-analysis:**
  - Con las dos espinas en «cero», el empate salió 25 % (n = 20), contra
    21 % en el resto: no anuncian la X.
  - La espina contra la tarjeta con riesgo alto acertó 43 %, y la que la
    sigue, 47 %: tampoco separa.
  - El empate declarado está calibrado: el reparto le da 24-30 % según el
    tramo y salió 18-26 %. Nunca se elige porque nunca es el más probable,
    no porque esté subestimado.
- **EFE:** elegir el lado con +10 de porcentaje acertó 56 % con T.54,
  R-KT.2 o ESCALA-LIGAS, y 62 % sin esas alertas, con los intervalos
  cruzados. La regla de la v1.7 (empate técnico de formación) ya cubre esto
  y todavía no hay partes con la v1.7.
- **DTP:** que el bloque del favorito escriba la rama «persiguiendo» no le
  ayudó a rescatar el partido (35 %, n = 17, contra 48 % sin escribirla).
  La v1.5 (dos ramas por marcador) todavía no tiene partes.

EFE v1.7, DTP v1.5 y sad-analysis v4.1 se aprobaron el 25/10 y ningún parte
medido es de esas versiones. Corresponde medirlas antes de proponerles nada.

## Cómo se midió

Para repetir la medición, los scripts están en el scratchpad de la sesión
del 26/10 (`scr/medir.py`, `scr/medir2.py` y `scr/medir3.py`). Leen el
veredicto y el parte de cada caso de
`GET /analisis/cowork/lecciones?cohorte=vigente`. Los intervalos son de
Wilson al 95 %.
