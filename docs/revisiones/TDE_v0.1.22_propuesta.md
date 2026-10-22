# Propuesta de revisión · `teorema-del-echado` v0.1.21 → v0.1.22

**Estado:** APROBADA por el usuario (22/10/2026, los tres puntos). Redactada
en `docs/skills/teorema-del-echado/SKILL.md` (disciplinas 62, 63 y 64) y con
sitio en el parte (`sob2`/`sob3` e `iseRama` por rama, `faltan` del `sob2`).
El juicio tramo por tramo del punto 3 entró al veredicto el 22/10
(`objetivo.tde.bloques[].tramos`, `veredicto.tramos_por_marcador`), junto con
la ventana del reloj puntuada aparte (`reloj`, serie del sesgo tardío en
`ventanaTde.reloj` de las lecciones).
Falta que el usuario la suba a su cuenta. Se redactó el 22/10/2026, a partir del
caso Sporting 2-3 LASK (Champions, 21/10) y de las lecciones del dossier
(`GET /analisis/cowork/revision/teorema-del-echado`, cohorte `c3-2026-09-23`)
que tocan las ramas de la reasignación. La base es la v0.1.21 que el usuario
subió a la cuenta el 21/10.

## De dónde sale

**El caso.** Sporting abrió de penal al 5' y siguió atacando: 62 % de la
pelota, 15 remates, xG 3,18. Le empataron al 15'. Con 1-1 se volcó y
concedió dos contras por el centro en cinco minutos (63' y 68'), y perdió
2-3.

La rama `siLeEmpatan` de la v0.1.21 estaba escrita y describió el mecanismo
exacto: «si le empatan antes del 75, vuelve a empujar y reabre la SOB desde
ese minuto». Pero quedó en prosa. El ISE del bloque siguió en **1,67**, con
SOB1 0 y SOB2 0, y el 1X2 subió al 66 % sobre el motor. La lección del caso
lo dice así: «la rama de empate se escribió en prosa sin valor propio y el
número no la acompañó».

**El patrón.** En el dossier hay 78 lecciones acreditables, falladas o
parciales, sobre las ramas, el empate, el que persigue o el seguro de atrás.
Se repiten tres huecos:

- **La rama no tiene número.** Pasó en Sporting–LASK: el texto cambia el
  régimen y el ISE se queda en el del arranque.
- **El seguro de atrás (SOB2) se hereda fijo.** En Sporting–LASK venía del
  DTP: Altimira delante de los centrales. Ese seguro sirve para el arranque,
  pero no para cuando el equipo persigue con los laterales arriba.
  Borussia Mönchengladbach siguió concediendo contras también con el 1-1.
  En Málaga, el que persiguió concedió el 1-3, el 2-4 y el 2-5 por robo y
  transición.
- **Los partidos de tres giros.** Bayern–Arsenal tuvo remontada al 61' y
  Lille–Galatasaray tres giros antes del descanso. En Paris FC–Rennes la
  sobreexposición se cobró con el partido empatado, no yendo abajo. La rama
  que ya no corresponde al marcador sigue leyéndose como vigente.

**Sesgo de atribución:** quien cierra el caso nombra la regla sobre todo
cuando falla. Varios de estos casos son «declarada y cumplida» (Parma,
Le Havre, Rayo Zuliano, Leeds): la disciplina 44 funciona. Lo que falta es
que su número viaje con ella.

## Lo que no se toca

- La fórmula del ISE (`(SOB1 + SOB2 + SOB3) / 3 × 10`), los pesos del IE, las
  compuertas y las bandas.
- La regla «el que marca primero no administra por defecto» de la v0.1.21.
  Se cumplió en Sporting, que siguió atacando con el 1-0.
- La disciplina 61. LASK la confirmó: recibió primero, persiguió y marcó él.

## Los tres cambios propuestos

### 1. Cada rama lleva su propio número (ISE de la rama)

Hoy una rama declara `sob1`, `tipologia`, `nota` y `ventana`.

**Propuesta:** cada rama que cambia el régimen declara sus **tres SOB**
(`sob1`, `sob2`, `sob3`), y la app calcula el **ISE de la rama** con la
misma fórmula de siempre. Aplica a `siRecibePrimero`, `siLeEmpatan` y a
`siMarcaPrimero` cuando sigue atacando.

- **Una rama que dice «se expone» y deja el ISE del arranque es una
  contradicción** entre el texto y el número (disciplina 33): el recibo la
  avisa en `faltan`.
- El veredicto mide la ventana de la rama **con el ISE de la rama**, no con
  el de la base.
- No es un peso nuevo. Es la misma cuenta, hecha para el estado del partido
  en que la rama se juega.

### 2. El seguro de atrás (SOB2) se declara por rama

El SOB2 que el TDE hereda del DTP (el rest defense) vale para el **arranque**.

**Propuesta:** la herencia del DTP alimenta **solo la base**. En la rama del
que persigue (`siRecibePrimero` o `siLeEmpatan` con el equipo empujando), el
SOB2 se vuelve a puntuar contra **ese** régimen: laterales arriba, pivote
solo y cambios ofensivos.

- Un seguro «fijo» del arranque no se traslada a la rama si el plan del
  equipo, al perseguir, es justamente desarmarlo.
- Sin evidencia de cómo queda el seguro al perseguir, SOB2 de la rama = 0,5
  (`sin dato` como cuenta media). Nunca se copia el 0 del arranque.

### 3. La rama vigente es la del marcador, no la del primer gol

**Propuesta, solo declaración:** en cada tramo del partido manda la rama del
**marcador de ese momento**.

| Estado del marcador | Rama que manda |
|---|---|
| Ganando | `siMarcaPrimero` |
| Perdiendo (aunque haya ido ganando) | `siRecibePrimero` |
| Empatado después de ir ganando | `siLeEmpatan` |
| Empatado después de ir perdiendo | la rama del que iguala |

**Candidato, no aplicado: la rama del que iguala** (`siIguala`), es decir,
qué hace el que empata un partido que iba perdiendo. Casos: Paris FC–Rennes
(concedió a los 2' de igualar) y Albion–Torque. Dos casos: queda como
candidato hasta el tercero ciego.

En el veredicto, un partido de tres giros se juzga tramo por tramo con la
rama de cada tramo. El primer gol no fija una rama para los 90 minutos.

## Lo que necesita en la app (después de aprobar)

- **Parte:** `tde.bloques[].reasignacion.<rama>` acepta `sob2` y `sob3`
  además de `sob1`. El backend devuelve `iseRama` con la fórmula del ISE
  (`backend/analisis/tde.py`) y el recibo avisa si una rama de régimen SOB
  viene sin sus SOB.
- **Veredicto:** la ventana de la rama se mide con `iseRama`, y la rama de
  cada tramo sale del marcador (cambio 3). El 3 es el más grande: se haría
  aparte si se aprueba.
- `docs/COWORK.md` y `corrida-sad` piden las SOB por rama.

## Cómo se aplica si se aprueba

1. El usuario aprueba o corrige los tres puntos.
2. Redacto la v0.1.22 en `docs/skills/teorema-del-echado/`: changelog,
   disciplina 44 con las SOB por rama y la nota de SOB2 por rama.
3. Le doy sitio en el parte (`sob2`/`sob3`, `iseRama`) y en el veredicto.
4. Te entrego el `.zip` y lo subes a la cuenta.
5. Se marcan como aplicadas, con 🔑, las lecciones de Sporting–LASK y de las
   ramas.
