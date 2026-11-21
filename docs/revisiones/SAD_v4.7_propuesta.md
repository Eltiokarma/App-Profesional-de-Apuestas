# Propuesta de revisión · `sad-analysis` v4.6 → v4.7

**Estado: PROPUESTA (21/11/2026), para aprobar punto por punto.** No toca
`docs/skills/sad-analysis/SKILL.md` hasta que el usuario la apruebe. Al
redactarse: el SKILL, `references/HISTORIAL.md`, `CORTE_VERSION` con la v4.7
(`backend/analisis/lecciones.py`) y, cuando el usuario suba el zip, su hora en
`SUBIDA_VERSION`.

**De dónde sale.** De la investigación del Bayern 1-1 Köln (1575221, 20/11),
que el usuario pidió debatir el 20 y 21/11: «la lección que casemos de ahí es
fundamental». Se midieron ocho hipótesis con scripts del repo, sobre el
padrón (hasta 43.167 favoritos, 2019-2026, niveles PREVIOS de los dos lados,
sin copas nacionales) y, cuando había, contra la cuota (desde agosto). Este
documento es el **registro completo**: lo que se confirmó (entra al skill), lo
que se midió y NO sirve (entra como prohibición, para que no se vuelva a
escribir como motivo), y lo que queda a medir hacia adelante (no entra).

**Cómo le llega al analista.** El analista lee `sad-analysis` en cada parte:
lo que cambia cómo se escribe el 1X2, la espina, el marcador o la carga va
ahí. Lo que la app puede calcular no se le pide al modelo (`docs/efe-dtp/
COSTO_IA.md`): el punto 7 pide a la app dos alertas `dato` para que el
analista las lea hechas. Lo del semáforo no es del analista (no entra al
parte): vive en `docs/METODO_APUESTA.md`. Las lecciones de TDE y DTP del
caso viajan por Aprendizaje (veredicto 1575221) y su revisión normal.

## 0. Resumen

| n.º | Qué | Medición | Tipo | Recomendación |
|---|---|---|---|---|
| 1 | «Riesgo bajo» no es «sin señal de reventón» | el elegido de 70 %+ ganó 47 de 52; el bajo revienta 37 % | redacción | aprobar |
| 2 | El perfil DC del RIVAL es resistencia que el motor no ve; la casa ya la cobra | +7 a +10 pts de «no gana» contra el nivel, en todos los segmentos; contra la casa, −2 | lectura | aprobar |
| 3 | El margen del favorito grande: no declarar goleada contra un rival que casi nunca golean y un favorito que no viene goleando | no cubre el −1,5 el 76-83 % (+7 a +9 pts) | marcador | aprobar |
| 4 | En Sudamérica y México el gigante gana apretado | cubre el −1,5 6-20 pts menos que su ventaja | marcador | aprobar |
| 5 | Lo medido que NO es motivo (lista cerrada) | ocho mediciones | prohibición | aprobar |
| 6 | Los perfiles DC: leer las dos mitades | Köln: se citó «no gana 68 %», no «no pierde 67 %» | redacción | aprobar |
| 7 | Para la app: dos alertas `dato` calculadas | — | app | pedir como desarrollo |
| 8 | Candidatos del semáforo (no son del analista) | a medir desde el 22/11 | METODO_APUESTA | no al skill |

---

## 1. «Riesgo bajo» no es «sin señal de reventón» (paso 1.7)

**Caso.** El parte del Bayern escribió «A: bajo, muy favorito… → sin señal de
reventón». Riesgo bajo dice que la racha suele seguir, no que no se corta: en
producción el nivel bajo revienta el 37 % (66 de 177). Para el favorito
enorme el número estaba bien (el elegido con 70 %+ ganó 47 de 52, 90 %), lo
que estaba mal era la frase.

**Texto propuesto (1.7, nueva viñeta).** «Riesgo bajo se escribe como lo que
es: la racha suele seguir. No se escribe "sin señal de reventón" ni "seguro":
el bajo revienta uno de cada tres; el favorito de 85 %+ no gana uno de cada
ocho a diez.»

## 2. El perfil DC del rival: resistencia que el motor no ve (6-B y 6-A)

**Medición** (`backend/backtest_rival_resiste.py --padron`, 21/11). Rival que
no pierde el 60 %+ de su historia en la condición de hoy (`perfilDc` de la
tarjeta de `/burbujas`), contra favoritos del mismo tramo de 0,1 de ventaja:

| Favorito | Falla con / sin | Diferencia | Caza de los tropiezos |
|---|---|---|---|
| por nivel 0,5+ | 55 / 41 % | +7,4 (se repite) | 60 % |
| muy favorito 1,0+ | 51 / 35 % | +9,4 (se repite) | 57 % |
| gigante (nivel 3,5+) | 45 / 30 % | +8,2 | 67 % |
| gigante con 1,5+ | 40 / 26 % | +9,6 | 62 % |

64 de 73 ligas en el mismo sentido. **Contra la cuota, −2,2 pts** (n 633): la
casa ya lo cobra. Confirma el §15.1 de REVENTON (el perfil DC mejora al motor).
La forma reciente del rival («no perdió 6+ de 10») da solo +1 a +4.

**Texto propuesto.** En 6-A, a la fuente «motor»: «El motor no ve el perfil
DC del rival: con un rival que no pierde el 60 %+ en su condición, el
favorito por μ gana 7-10 pts menos de lo que dice el nivel. Cuando el 1X2 se
apoya en el motor (sin cuota en la app, o al apartarse del mercado), se
nombra y se descuenta en la lectura; con cuota, el mercado ya lo trae y no se
resta otra vez (regla vigente de 6-B: los perfiles no mueven el 1X2 bajo el
mercado).» No cambia ningún número ni la regla de «dos perfiles alineados».

## 3. El margen del favorito: la goleada y el marcador (paso 3.5)

**Medición** (`backend/backtest_margen.py --padron`, 21/11, REVENTON §15.4).
El gigante gana por 2+ el 37 %; con la casa en 80 %+, el 64 %; en 85 %+, el
78 % (n 32). No cubre el −1,5 (gana por 0 o 1, o no gana), contra el mismo
tramo de ventaja y en las dos épocas:

| Señal previa | Muy favorito | Gigante |
|---|---|---|
| rival que pierde por 2+ el 15 % o menos en su condición | +7,2 | +7,1 |
| favorito que ganó por 2+ en 3 o menos de sus últimos 10 | +5,6 | +6,2 |
| **las dos** | **+8,9** (no cubre 80 % contra 64 %) | **+7,9** (76 contra 61) |

**Texto propuesto (3.5).** «La goleada como rama (v4.4/v4.5) NO se nombra, y
el marcador declarado no da al favorito ganando por 2+, cuando el rival
casi nunca pierde por 2+ en su condición y el favorito no viene goleando (2+
en 3 o menos de sus últimos 10): ahí el favorito gana por 0 o 1 ocho de cada
diez. Con una sola de las dos, se nombra la celda de un gol de diferencia del
acotado como salida.» Choca con la viñeta de la goleada cuando el tramo 3+
es el más probable: en ese caso manda esta (la distribución del motor no ve
el perfil del rival).

## 4. Por liga: en Sudamérica y México el grande gana apretado (paso 3.5)

**Medición** (misma corrida). El gigante cubre el −1,5 menos de lo que dice su
ventaja: Brasil Serie B −19,5 pts, Uruguay −12, Sudamericana −12, Chile −12,
Colombia −10, Argentina −10, Perú −9, Ecuador −8, Brasil −7, Libertadores −7,
Liga MX −6. En Europa, al revés: Premier +6, Bundesliga +8, Portugal +10,
Eredivisie +12.

**Texto propuesto (3.5).** «En las ligas sudamericanas, la Libertadores, la
Sudamericana y la Liga MX, el marcador declarado del favorito grande se
elige con un gol de diferencia salvo un hecho del partido; la goleada va como
rama solo con el hecho escrito en otro lado del parte (TDE, matriz).»

## 5. Lo medido que NO es motivo (Prohibiciones permanentes, lista cerrada)

Ninguno de estos se escribe como razón para desconfiar del favorito ni para
mover el 1X2, la espina o la carga. Cada uno con su medición:

| Lo que no es motivo | Medición | Dónde |
|---|---|---|
| La racha sin perder del favorito en su récord («21 de local sin perder») | +0,4 pts de «no gana», n 12.187; contra la casa −3,7 | REVENTON §15.3, `backtest_dc_record` |
| La forma reciente del favorito por debajo de lo que dice la casa | −1,9 pts, n 411 de 1.249 | METODO_APUESTA, `backtest_forma_cuota` |
| DIV-MOTOR-MERCADO (el motor muy por debajo de la casa) | en los de 70 %+, ganó 29 de 30 con la alerta | partes acreditables |
| F3 en el elegido (llega con bajas) | 22 de 25 contra 25 de 27 | partes acreditables |
| Venir empatando o de burbujas cortas | no separa (73 equipos) | este estudio |
| Primer partido tras la fecha FIFA | 37 contra 41 % de «no gana», n 84 | este estudio |
| Las burbujas abiertas del rival (racha sin perder 3+, o en récord) | +0,7 y −1,5 pts, no separan | `backtest_rival_resiste` |
| La burbuja de goleadas del rival (5+ sin perder por 2+) | +2 a +3 pts: débil, menos que su perfil | `backtest_margen` |

**Texto propuesto (Prohibiciones, nueva).** La tabla, en una línea por fila, con
la regla: «lo que avisa es el perfil largo del rival y la forma de goleo; las
rachas abiertas y los récords no».

## 6. Los perfiles DC se citan enteros (6-B)

**Caso.** El parte citó de Köln «no gana de visita 68 %» y no «no pierde 67 %»:
eligió la mitad que confirmaba. **Texto propuesto (6-B, viñeta de perfiles).**
«Un perfil DC se cita con sus dos mitades (no pierde · no gana), aunque no
mueva el número.»

## 7. Para la app (calculado; el analista lo lee, no lo cuenta)

Dos alertas `dato` en el parte, calculadas en el backend con lo anterior al
partido (como DESCONFIAR):

- **`RIVAL-RESISTE`**: el elegido es favorito por nivel (0,5+) y el rival no
  pierde el 60 %+ en su condición (perfil DC). Dice cuántos puntos se le
  escapan al motor en ese segmento.
- **`HANDICAP-APRETADO`**: el rival pierde por 2+ el 15 % o menos en su
  condición y el favorito ganó por 2+ en 3 o menos de sus últimos 10, o la
  liga es de las de §4. Dice «el favorito gana por 0-1 ocho de cada diez».

Contrato primero (`docs/openapi.yaml`), con test. **No está hecho**: se pide
como desarrollo después de aprobar esta propuesta.

## 8. Lo que no es del analista: los candidatos del semáforo

Congelados el 22/11/2026 y medidos hacia adelante (`docs/METODO_APUESTA.md`,
DEUDA 37): «verde con rival que no perdió 6+ de 10 → amarillo» y «verde con
rival de perfil DC 60 %+ → amarillo». El semáforo no entra al parte; no van
al skill.

## Lecciones del caso que viajan por Aprendizaje (no por esta propuesta)

En el veredicto 1575221: la pieza de la VÍA en la rama que persigue (TDE,
candidato de un caso); el bloque «improvisado» que era un bloque bajo de plan
(DTP, checklist p4 y vida útil); el falsador de la echada escrito sobre la
fractura y no sobre los remates de afuera (TDE); el renglón del M2 que
depende de una pieza (DTP). Se revisan con su skill, con los demás casos.
