# Propuesta para la próxima versión · «en quién desconfiar» (10/11/2026)

**Estado:** el usuario aprobó el 10/11 llevarla a la próxima versión de los
skills («lleva la propuesta a los skills para la próxima versión, tengo que
ver esa alerta»). Todavía no está redactada en ningún `SKILL.md`. Entra en
la próxima tanda (**sad-analysis v4.6**, **teorema-del-echado v0.1.27**),
con su dossier y sus lecciones nuevas, como el resto.

## De dónde sale

- `docs/revisiones/ESTUDIO_ECHADOS_2026-11.md`: los 107 fallos de 265 partes
  del 01 al 09/11, en dos grupos con su control:
  - 37 que perdieron la ventaja, contra 157 que la sostuvieron;
  - 70 que nunca se pusieron adelante, contra 194 que sí.
- La tabla de la base: 53.108 partidos de football-data, 11 ligas,
  2012-2026, con la cuota de cierre y el marcador al descanso.
- La idea del usuario: **«una de las formas de acertar es escoger qué
  alternativa no hay que escoger»**. Bajar de tres resultados a dos.

## Qué tan firme es cada hallazgo

| | Hallazgo | Respaldo | Firmeza |
|---|---|---|---|
| A | **La ventaja se sostiene según la fuerza previa, no según la táctica**. Con 1 de ventaja al descanso no gana el 47 % de los que tenían < 35 % y el 9 % de los que tenían 75 %+. Local y visita dan igual | 53 mil partidos; iguales en 2012-18 y 2018-26; coincide con nuestros 37 | **firme** |
| B | **Ponerse sobre la casa es la señal de que leímos de más**. Con 2+ pts sobre la casa, el elegido nunca se adelantó en el 57 % (base 26,5 %) | 23 partes; coincide con la visita de 2+ pts bajo la casa (ROI −20 %, n 31) y con la decisión del 03/11 | **firme en dirección**, número a medir |
| C | **Una racha de un partido no es una burbuja**. Racha + de 1 con riesgo alto: nunca arrancó el 39 %. Racha de 3+: el 11 % | 28 y 55 partes, una semana | **a medir** |
| D | **Donde desconfiamos, descartar al otro lado funciona**. Con alerta, el elegido acertó 50 %, pero «elegido o empate» acertó 85,7 % (la casa pedía 73,9 %) | 28 partes, la misma semana donde se encontró | **pista**: se mide hacia adelante (ya registrada en la Simulación, PR #469) |
| E | **La tipología del TDE (ECHADA / SOB) no separa quién pierde la ventaja** (17,6 % contra 17,5 %), y tampoco los cambios defensivos (16,4 %, base 19,1 %) | 37 contra 157 | **firme en lo negativo** (no separa); n chico |

## Cambios propuestos

### sad-analysis v4.6

1. **La alerta de confianza en el parte** *(calculable → app)*. La app
   calcula y pone en la tira del parte la alerta de tipo `dato`
   **DESCONFIAR**, con sus motivos: `SOBRE-LA-CASA` (2+ pts sobre la casa
   sin margen) y `BURBUJA-DE-UN-PARTIDO` (racha + de un partido con riesgo
   alto o muy alto). El analista no la calcula. La **nombra** en el
   `porque` del 1X2 y en la espina, y **no sube la carga**. No mueve el 1X2:
   es confianza (decisión del 03/11). La regla de la v4.5 «no apartarse del
   número de la casa» ya evita la mayoría de los `SOBRE-LA-CASA`. La alerta
   avisa cuando igual pasa. *Respaldo: B y C. Se sostiene si con 100+ alertas
   el elegido acierta menos con alerta que sin ella. Lo tumba si no hay
   diferencia.*
2. **Una racha de un solo partido no sostiene al elegido** (paso 1.6, junto a
   la regla (i) de la v4.5). Con racha de 1 partido y riesgo alto o muy alto,
   la espina no dice «sigue» sin un hecho de la lista. Si el 1X2 elige a ese
   lado igual, la tira ya trae `BURBUJA-DE-UN-PARTIDO`. Las burbujas de 3+
   partidos son las que arrancan: ahí la espina puede leer «sigue» con la
   tarjeta. *Respaldo: C. ⚠ El 39 % y el 11 % son de una semana: medir
   primero con 100+ casos de cada lado.*
3. **El descarte** (paso 6-B, junto a la Ley 6 de doble oportunidad). El parte
   declara en `pronostico` el resultado que **descarta** (el menos probable,
   o el que la lectura excluye con un hecho) y la frase que lo sostiene.
   Con DESCONFIAR, la lectura del 1X2 se escribe como «el otro lado no gana»
   antes que como «gana el elegido». Es narrativa, no apuesta: qué se juega
   lo decide el método (punto 6). El veredicto mide el descarte aparte del
   1X2: cuántas veces salió lo descartado, contra lo que le daba la casa.
   *Respaldo: D y la idea del usuario. Hoy el descarte sale 17,0 % contra
   21,8 % de la casa (264 partes), pero coincide con el de la casa en 251:
   todavía no descartamos distinto que ella.*

### teorema-del-echado v0.1.27

4. **La ventaja por fuerza** *(calculable → app)*. `ventajaPorMinuto` (ya en
   `GET …/tde/{id}`) se parte por la **probabilidad previa sin margen** del
   que marca primero, en los tramos < 35 · 35-48 · 48-60 · 60-75 · 75+ %. La
   rama `siMarcaPrimero` cita la columna de su tramo: «no gana» y «no
   pierde». Hasta que la app la calcule por minuto con la base, se cita la
   tabla de referencia del descanso (A, en `ESTUDIO_ECHADOS_2026-11.md` §9).
   *Respaldo: A.*
5. **El desenlace de la rama de ventaja lo pone la fuerza, no la tipología.**
   La tipología ECHADA / SOB describe la **vía** por la que llega el empate
   (banco rival, contra, pelota parada), y el número sale de la punta 4. Se
   suma a la disciplina 63 y al candidato del TDE 11 («la SOB de la hora
   pide un hecho de hoy»). *Respaldo: E. No afloja ninguna regla: deja de
   pedirle a la tipología algo que no separó.*

### Método de apuesta (`docs/METODO_APUESTA.md`), sin skill

6. **Qué hacer con la alerta lo decide la medición, no el skill.** Con 100+
   partidos cerrados con alerta (tarjeta «En quién desconfiar» de la
   Simulación) se elige una de tres opciones:
   - (a) seguir igual;
   - (b) bajar la carga del método en los partidos con alerta;
   - (c) jugar «elegido o empate» en vez del elegido.

   La (c) solo si la doble oportunidad acierta claramente más de lo que pide
   la casa, porque paga poco: cerca de 1,30 al 85 %.

## Lo que hace la app

- **Ya hecho (PR #469):** la alerta por apuesta y el resumen en la
  Simulación (`alertaConfianza`: con alerta contra sin alerta, doble
  oportunidad y descarte), desde el 10/11.
- **Falta:**
  - la alerta `DESCONFIAR` en la tira del parte, que también va al recibo;
  - `ventajaPorFuerza` en `GET …/tde/{id}`;
  - el `descarte` en el contrato del pronóstico, con su medición en el
    veredicto;
  - la tabla A por minuto con los eventos de `sad.db` en el servidor, más
    las ligas americanas, que football-data no trae.

## Núcleo e historial

- **Núcleo:** las frases de las puntas 1, 2, 3 y 5 en sus pasos o
  disciplinas.
- **Historial:** las tablas del estudio, los casos y los números de una
  semana.
