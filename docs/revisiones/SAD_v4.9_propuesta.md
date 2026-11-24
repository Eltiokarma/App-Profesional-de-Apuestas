# Propuesta de revisión · `sad-analysis` v4.8 → v4.9 (el «¿entrarías?»)

**Estado: PROPUESTA (24/11/2026)**, para aprobar punto por punto. No se tocó
el skill, ni el código, ni ningún parte.

**De dónde sale.** El usuario (24/11): «en el frontend ha estado saliendo algo
así como *el analista duda*, con cierto color: ¿esa lectura cambia con lo
aprendido?». No cambia: el chip ✋ sale de `pronostico.entrar` (6-F, v4.8,
21/11) y la revisión del 24/11 tocó TDE, DTP y EFE. Pero al medirlo apareció
que el chip casi siempre está prendido y no separa.

## Lo medido (98 partidos jugados con veredicto, del 21 al 23/11)

¿Acertó el 1X2 del parte según lo que dijo el analista en `pronostico.entrar`?

| Lo que dijo | Partidos | Acertó el 1X2 |
|---|---:|---:|
| `entraria` | 8 | 6 (75 %) |
| `dudo` | 56 | 33 (59 %) |
| `noEntraria` | 4 | 1 (25 %) |
| sin el campo (partes de antes de la v4.8) | 30 | 17 (57 %) |

Dentro de `dudo`, por motivo:

| Motivos de `dudo` | Partidos | Acertó el 1X2 |
|---|---:|---:|
| solo `ONCE-INCIERTO` | 37 | 24 (65 %) |
| `ONCE-INCIERTO` y otro | 14 | 6 (43 %) |
| sin `ONCE-INCIERTO` | 5 | 3 (60 %) |

`ONCE-INCIERTO` aparece en 53 de los 68 partes que declaran el campo.

**Lectura.**
- El parte se escribe la noche anterior, antes del once: el once **siempre**
  es incierto a esa hora. «Dudo» por `ONCE-INCIERTO` solo describe la hora a la
  que se escribió, no el partido. Por eso el amarillo sale en el 82 % de los
  partes y deja de avisar algo.
- La duda que es **solo** por el once acertó más que el promedio (65 %): no es
  una señal de no entrar.
- La que suma otro motivo (43 %) y el «no entraría» (1 de 4) van en la
  dirección del candidato. Muestra mínima: nada de esto decide; se mide con
  los escalones del semáforo (30 para mirar, 60 para decidir).
- **El rehacer no lo revisa.** En Juventus–Venezia (1550201) el `porque` dice
  «once oficial ya en la hoja» y la decisión sigue en `dudo`. El modo `rehacer`
  solo corre con DTP-REHACER y sus hermanas; el «¿entrarías?» no figura en su
  lista de lo que se reescribe.

## Puntos para aprobar

| N.º | Qué cambia | Tipo | Casos | Recomendación |
|---|---|---|---|---|
| 1 | Antes del once, `ONCE-INCIERTO` **solo** no es «dudo»: va en `condicionadoAlOnce: true` con la decisión que darías si sale el once que leíste | regla + contrato | 37 | **Aprobar** |
| 2 | Con el once oficial, `ONCE-INCIERTO` deja de ser motivo: el rehacer re-juzga `entrar` con la hoja y apaga `condicionadoAlOnce` | regla (rehacer) | 1550201 | **Aprobar** |
| 3 | El chip ✋ se pinta solo con «dudo» o «no entraría» de verdad; el condicionado al once no se pinta (o va en gris, «espera el once») | app | — | **Aprobar** (gris) |
| 4 | El candidato del semáforo se mide aparte: «dudo/no entraría» sin el once como único motivo, contra «entraría» | medición | — | **Aprobar** |

### 1. `ONCE-INCIERTO` solo no es duda · [regla] [contrato]

**Qué dice hoy** (`docs/skills/sad-analysis/SKILL.md`, 6-F): `ONCE-INCIERTO`
es uno de los motivos de «dudo» o «noEntraria» («no se sabe qué once sale, o el
que sale no es el que se leyó»).

**Texto propuesto** (reemplaza la viñeta de los motivos y suma una):

> - **El once incierto, solo, no es duda** *(v4.9)*. El parte se escribe antes
>   del once: a esa hora el once siempre es incierto, y eso no dice nada de
>   ESTE partido (21-23/11: 37 «dudo» solo por el once, el elegido ganó el 65 %).
>   Si tu única reserva es el once, escribí la decisión que darías **si sale el
>   once que leíste** y marcá `"condicionadoAlOnce": true`, con el jugador o la
>   línea de la que depende en el `porque`. `ONCE-INCIERTO` como motivo de
>   «dudo» o «noEntraria» va **solo con otro motivo** de la lista, o cuando la
>   incertidumbre es del partido y no de la hora (un DT que anunció rotación
>   total, dos arqueros que se alternan sin dueño, una crisis del plantel), dicho
>   con su fuente.

Contrato: `pronostico.entrar.condicionadoAlOnce` (booleano, opcional, default
`false`). Va primero a `docs/openapi.yaml`, después a `parte._entrar`, a
`src/api/types.ts` y a los dos datasources, con su test.

### 2. Con el once, se re-juzga · [regla del rehacer]

**Texto propuesto** (6-F, en lugar de «Con el once oficial, si el motivo era el
once, se rehace»):

> - **Con el once oficial, el once ya no es motivo** *(v4.9)*. Al rehacer,
>   `entrar` se re-juzga con la hoja: si el once que salió es el que leíste,
>   la decisión condicionada queda firme y `condicionadoAlOnce` pasa a
>   `false`; si no, se decide de nuevo con el hecho de hoy. `ONCE-INCIERTO` no
>   sobrevive al once oficial.

En la app: el rehacer suma **ENTRAR-CONDICIONAL-AL-ONCE** a su lista de motivos
(`parte.REHACER_POR`), como ALERTA-CONDICIONAL-AL-ONCE con EJE-DEBUTANTE: un
parte con `condicionadoAlOnce` y el once oficial capturado entra al rehacer. En
el modo `rehacer` de la corrida, el paso 4 nombra `pronostico.entrar`.
**Costo:** más disparos con trabajo. Alternativa más barata: re-juzgar solo
cuando el rehacer ya corre por otro motivo, y que el chip muestre «espera el
once» hasta el pitazo. Recomendación: la alerta (el chip tiene que decir algo
del partido cuando importa, que es antes del pitazo).

### 3. El chip · [app]

`AnalistaChip` (`src/components/LecturaListaChips.tsx`) pinta hoy toda
decisión distinta de `entraria`. Con el punto 1: amarillo y rojo solo para la
duda real; `condicionadoAlOnce` en gris con «espera el once» (tooltip: la
decisión condicionada y de qué jugador depende). Auditoría móvil a 360 y 390.

### 4. Cómo se mide · [medición]

El quinto candidato del semáforo (`docs/METODO_APUESTA.md`) se cuenta desde la
subida de la v4.9 con la decisión **después del once** (la del rehacer, o la
condicionada si el once salió como se leyó). Los partes de la v4.8 se reportan
aparte, partidos en «solo el once» y «con otro motivo», para no mezclar. Por
acierto: cuánto más pierde el elegido con «dudo/no entraría» que con
«entraría»; nunca contra la casa.

## Lo que no entra

- Mover el 1X2 por el «¿entrarías?»: sigue sin tocar el número (6-F).
- Sacar `ONCE-INCIERTO` de la lista: sirve cuando la incertidumbre es del
  partido (rotación anunciada, arco sin dueño).
- Cualquier conclusión sobre «no entraría»: 4 partidos.

## Decisiones para el usuario

1. Aprobar los puntos 1 a 4.
2. Punto 2: (a) **alerta propia que dispara el rehacer** (recomendado) o (b)
   re-juzgar solo cuando el rehacer ya corre.
3. Punto 3: el condicionado al once (a) **en gris, «espera el once»**
   (recomendado) o (b) sin chip.
