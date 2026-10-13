---
name: corrida-sad
description: Corrida del pipeline SAD con Claude Code (reemplaza a Cowork desde el 13/10/2026). Modo `partes` analiza los partidos de la agenda con los skills (EFE, Teorema del Echado, DTP, sad-analysis) y deposita un parte por partido; modo `veredictos` cierra con autopsia por skill los partidos jugados. Usar cuando una rutina programada o el usuario pida «la corrida», «los partes de hoy», «validar lo de ayer» o «los veredictos».
---

# Corrida SAD con Claude Code

Desde el 13/10/2026 el análisis lo hace **Claude Code** en sesiones de la nube
lanzadas por rutinas, no Cowork. El contrato y el prompt de siempre siguen
mandando: `docs/COWORK.md` (el nombre del archivo quedó; «Cowork» ahí = quien
escribe el parte, hoy vos). Esta guía dice cómo correrlo desde Code.

## Credenciales (antes de nada)

- `SAD_API_BASE` = la base de la API, terminada en `/api/v1`.
- `SAD_TOKEN_COWORK` = el token ACOTADO (lista de permitidos). Viven en las
  variables del entorno de la nube.
- `export B="$SAD_API_BASE" T="$SAD_TOKEN_COWORK"` y siempre
  `curl -sS -H "Authorization: Bearer $T" "$B/…"`.
- **Nunca** imprimas, escribas en un archivo del repo ni repitas el token. Si
  un endpoint responde 403, NO busques otro token: ese endpoint no es tuyo,
  anotalo y seguí. El token maestro no se usa jamás desde una sesión.
- Si falta alguna de las dos variables: no hay corrida. Terminá diciendo cuál
  falta (sin inventar resultados) — se agrega en la configuración del entorno.

Hora: `TZ=America/Lima date` (la referencia del proyecto es Lima). Archivos de
trabajo en el scratchpad de la sesión, nunca en el repo: esta corrida NO
commitea nada.

## Modo `partes` (antes del partido)

1. `GET $B/analisis/cowork/contrato` (manda sobre cualquier ejemplo) y
   `GET $B/analisis/cowork/latido` (qué quedó roto de ayer: decilo al final).
2. `GET $B/analisis/cowork/agenda?limite=8` → la lista de trabajo es
   `porHacer` (lo ya depositado está en `yaHechos`: no se rehace). Descartá
   los que arrancan en menos de 60 minutos: un parte no se escribe con el
   pitazo encima y JAMÁS después del pitazo.
3. **Un subagente por partido, en paralelo** (herramienta Agent, tipo
   `general-purpose`, todos en el mismo mensaje). Es la «sesión limpia por
   partido» del punto 3 del prompt: el contexto de un partido no contamina al
   otro. A cada uno le pasás el `fixtureId`, los dos equipos, la hora de
   inicio en Lima, la **hora tope** (inicio − 45 min), su fila de la agenda y
   las instrucciones de la sección «Encargo de un partido» de abajo, entera.
4. Al volver todos: `POST $B/analisis/cowork/xi/auto` (cierra los onces que
   ya estén; el ciclo en vivo del backend lo vuelve a hacer solo cuando salen
   las alineaciones). `GET …/agenda?limite=8` de nuevo: `porHacer` tiene que
   haber quedado vacío salvo lo que se descartó a propósito.
5. Respuesta final, tres líneas: partes depositados (fixtureId y partido),
   cuáles no y por qué, y qué se rompió (incluido lo que dijo el latido).

### Encargo de un partido (copiar entero al subagente)

> Sos el analista SAD de UN partido, en modo batch desatendido. Nadie te va
> a contestar: toda duda se declara en el parte, nunca se inventa.
>
> - Leé `docs/COWORK.md` desde «# PROMPT COWORK — SAD BATCH NOCTURNO» hasta
>   «# PROMPT CORTO — "LLEGÓ EL ONCE"»: es el prompt y manda en todo. Ignorá
>   su punto 2 (la selección ya está hecha: tu partido es este) y el bloque
>   de credenciales (usá `$SAD_API_BASE` y `$SAD_TOKEN_COWORK`, nunca los
>   imprimas). Si dudás de una forma del contrato, mirá `backend/analisis/
>   parte.py` (solo lectura; no modifiques el repo).
> - Skills (herramienta Skill), cargalos ANTES de puntuar:
>   `anthropic-skills:efe-clasificador`, `anthropic-skills:teorema-del-echado`,
>   `anthropic-skills:diagnostico-tactico`, `anthropic-skills:sad-analysis`.
>   Prensa con WebSearch/WebFetch (cargalos con ToolSearch
>   `select:WebSearch,WebFetch`).
> - Orden: `GET antecedentes/{id}` → `fixtures/{id}` → `analisis/cowork/
>   tde/{id}` → `analisis/cowork/dtp/{id}` → **`analisis/cowork/f1/{id}`**
>   (la tabla F1 sale de acá, con `jugadorId`; los `decisivo` no pueden
>   faltar) → `equipos/{id}/burbujas?proximo={id}` de los dos → `cuotas/{id}`
>   → prensa (DT de ESTA semana, bajas, once probable) → el JSON del parte
>   EXACTO al punto 7 (a = local).
> - Lo que dejaron las autopsias del 11/10 y ya es campo: `reasignacion` en
>   CADA bloque del TDE con las dos ramas (`siMarcaPrimero`,
>   `siRecibePrimero`); la ventana de una echada condicionada a ir ganando se
>   ancla al minuto de la ventaja, no al reloj; COLAPSO EN CASCADA solo si el
>   rival con D3 superior va a seguir atacando; la posesión y el rest defense
>   valen contra ESTE rival y con ESTE once.
> - **Alertas: solo códigos que existen en los skills** (T.54, T.54-B,
>   R-KT.2, GK-DOWNGRADE, FACTOR-X, G-BLOQUE, G-SORPRESA, COLAPSO EN
>   CASCADA… los que nombra la rúbrica). Una observación que no tiene código
>   (un DT suspendido, un plantel desarmado, una trampa del mercado) va en
>   `notas` del bloque o en la lectura, NO como alerta con un código inventado:
>   un código nuevo no lo cuenta nadie y ensucia la tira. En la corrida del
>   13/10 aparecieron cuatro (DT-SUSPENDIDO, PLANTEL-DESMANTELADO, DC-TRAMPA,
>   BAJA-ORGANIZADOR).
> - `POST $B/analisis/cowork` y LEÉ EL RECIBO ENTERO: `rechazos`, `faltan`,
>   `perdido`, `ladosTde`, `discrepancias`. Con algo ahí: `GET` → corregir →
>   `POST` del cuerpo entero (el POST reemplaza). La `cadena` se conserva del
>   PRIMER depósito: el primero ya lleva la definitiva.
> - Reloj: `TZ=America/Lima date` seguido. Depositá antes de la hora tope; si
>   15 minutos antes no está completo, depositá lo que tengas con lo faltante
>   en `pendientes`. Después del pitazo NO deposites: decilo.
> - Respuesta final breve (sin el token): hora del depósito; recibo
>   (rechazos, faltan, aviso/perdido); EFE % de cada lado según el GET; 1X2 y
>   marcador; alertas (tuyas y del backend); DT de cada lado y si hubo
>   DT-DISCREPANCIA; qué quedó pendiente o roto.

## Modo `veredictos` (después del partido)

1. `GET $B/analisis/cowork/veredictos/pendientes` → los partes jugados sin
   veredicto. Si no hay, decilo en una línea y terminá.
2. Un subagente por partido, en paralelo, con este encargo:

> Cerrá el caso del fixture {id} con el prompt «# PROMPT CORTO — "VALIDAR LO
> DE AYER"» de `docs/COWORK.md` (leelo entero). Lo objetivo (marcador, 1X2,
> Brier, ventana del TDE, rama de la reasignación, reventón) lo calcula la
> app: leelo de `GET $B/analisis/cowork/{id}/veredicto` y de la ficha
> (`GET $B/fixtures/{id}/ficha`), no lo escribas.
>
> La autopsia es POR SKILL, no por el 1X2: cargá
> `anthropic-skills:teorema-del-echado`, `anthropic-skills:efe-clasificador`
> y `anthropic-skills:diagnostico-tactico` y seguí su procedimiento de
> cierre de caso (en el TDE, «Cómo se cierra un caso» de CALIBRACION; en el
> DTP, la autopsia de goles con responsables y MECANISMO-ABIERTO). Cada
> hallazgo que toca una regla es UNA lección con `skill` y `reglaTocada`: la
> primera en `leccion`, las demás en `otrasLecciones` (hasta 6). Una
> confirmación de una regla también es lección («disciplina 44 declarada y
> cumplida»): es lo que cuenta casos a favor.
>
> `seleccion`: `ciega` si el partido salió de la agenda; `modoEvaluacion`:
> `PRE` si terminó. Con duda entre ciega y post_resultado, es post_resultado.
> `POST $B/analisis/cowork/{id}/veredicto` y leé `rechazos`. Respuesta final:
> marcador, veredicto por lado y la lista de lecciones (skill · regla).

3. Respuesta final, tres líneas: veredictos cerrados, lecciones por skill, y
   qué no se pudo cerrar y por qué.

## Lo que NO hace esta corrida

- No levanta cuarentenas, no desmiente bancos, no abre revisiones ni marca
  lecciones `aplicada`: es del usuario, con la llave maestra.
- No commitea ni toca el código. Si encuentra un bug de la app, lo describe
  en la respuesta final (qué, dónde, con qué fixture) y nada más.
