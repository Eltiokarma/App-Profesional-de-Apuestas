---
name: corrida-sad
description: Corrida del pipeline SAD con Claude Code (reemplaza a Cowork desde el 13/10/2026). Modo `partes` analiza los partidos de la agenda con los skills (EFE, Teorema del Echado, DTP, sad-analysis) y deposita un parte por partido; modo `veredictos` cierra con autopsia por skill los partidos jugados; modo `reventones` estudia hacia atrás burbujas que reventaron (TDE de los dos equipos, DTP, EFE de ese día); modo `rehacer` rehace el DTP (y lo que el once cambie) de los partes con DTP-REHACER cuando sale el once oficial, antes del pitazo; modo `mantenimiento` lee las incidencias que dejaron las corridas, las verifica y arregla con tests lo que es código. Usar cuando una rutina programada o el usuario pida «la corrida», «los partes de hoy», «validar lo de ayer», «los veredictos» o «el mantenimiento».
---

# Corrida SAD con Claude Code

Desde el 13/10/2026 el análisis lo hace **Claude Code** en sesiones de la nube
lanzadas por rutinas, no Cowork. El contrato y el prompt de siempre siguen
mandando: `docs/COWORK.md` (el nombre del archivo quedó; «Cowork» ahí = quien
escribe el parte, hoy vos). Esta guía dice cómo correrlo desde Code.

**Ahorradora sin cambiar el resultado** (11/11/2026, incidencia 1377,
usuario: «todos los skills o rutinas que desplegamos deben ser ahorradores sin
afectar el resultado»). Este archivo es solo el índice: cada modo vive en su
archivo y se lee SOLO el del modo que corre, y solo cuando la primera llamada
dice que hay trabajo. Las reglas son las mismas de siempre, palabra por
palabra; lo que cambió es cuándo se leen.

## Paso 0 de cada modo: UNA llamada, y con nada que hacer se termina

Antes de `git pull`, de leer otro archivo o de cargar otro skill:

| Modo | Primera llamada | Vacío si… | Con trabajo, leé |
|---|---|---|---|
| `partes` | `GET $B/analisis/cowork/agenda?desdeAhora=true&horas=N&limite=30` (N por la hora de Lima, abajo) | `porHacer` vacío | `modos/partes.md` |
| `veredictos` | `GET $B/analisis/cowork/veredictos/pendientes?limite=45` | la lista viene vacía | `modos/veredictos.md` |
| `rehacer` | `GET $B/analisis/cowork/rehacer` | `pendientes` vacío | `modos/rehacer.md` |
| `reventones` | `GET $B/analisis/cowork/reventones?liga=<id>&meses=6&conFicha=true` | ninguno con `estudiado: false` | `modos/reventones.md` |
| `mantenimiento` | — (con la cola en cero igual hace la prevención) | nunca | `modos/mantenimiento.md` |

`horas` del modo partes, por la HORA DE LIMA a la que corrés: 03:00-08:59 →
7 (tramo 1) · 09:00-13:59 → 6 (tramo 2) · 14:00-02:59 → 14 (tramo 3). Si el
disparo trae otros parámetros de agenda, mandan esos, salvo un `limite` menor
que 30.

**Vacío**: respondé UNA línea («Nada que hacer en <modo> a las HH:MM de
Lima», o «Sin veredictos pendientes») y terminá: sin `git pull`, sin leer el
archivo del modo, sin otra llamada. `partes` y `veredictos` avisan esa línea
al celular (corren pocas veces al día); `rehacer` NO avisa (corre cada 10-20
minutos). **Con trabajo**: `git checkout main && git pull origin main`
(mantenimiento: la rama designada recreada desde `origin/main`), leé
`.claude/skills/corrida-sad/modos/<modo>.md` y seguilo entero: manda ese
archivo. Lo que ya trajo la primera llamada no se vuelve a pedir.

Archivos de esta carpeta, y quién los lee:

- `modos/<modo>.md`: los pasos de cada modo (y los encargos de sus
  subagentes, que se copian enteros al subagente: el orquestador no necesita
  más que eso).
- `incidencias.md`: cómo depositar lo roto. Lo lee la corrida SOLO si tiene
  algo que depositar.
- `no-se-reporta.md`: la lista de lo decidido que no se vuelve a abrir. La lee
  quien va a depositar una incidencia, antes de depositarla, y el
  mantenimiento cuando la amplía (paso 7-bis).

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
commitea nada. **Una carpeta por subagente** (`<scratchpad>/<fixtureId>/`),
y se lo decís en el encargo: los subagentes corren en paralelo y, con la misma
carpeta, uno leía el JSON que el otro acababa de escribir (15/10/2026: el de
Boca–Vasco recibió el veredicto y la ficha de Bucaramanga–Águilas en sus dos
primeras consultas). Nunca un nombre de archivo fijo como `ficha.json` fuera
de esa carpeta.
Usá SIEMPRE rutas absolutas (`-o <scratchpad>/<fixtureId>/x.json`): un `-o get.json` relativo
cae en la raíz del repo (17/10/2026).

## Al terminar cualquier modo: avisá al celular

Las rutinas corren solas y el usuario no mira la sesión. Mandá las tres
líneas finales al celular con la herramienta **PushNotification** (cargala con
ToolSearch `select:PushNotification`), también si la corrida falló o no tenía
nada que hacer. Sin el token, sin datos sensibles.

Excepción: el modo `rehacer` corre cada 30 minutos y avisa SOLO si rehízo
algo o algo falló.

## Lo que NO hace esta corrida

- No levanta cuarentenas, no desmiente bancos, no abre revisiones ni marca
  lecciones `aplicada`: es del usuario, con la llave maestra.
- En partes, veredictos y reventones no commitea ni toca el código: un bug de
  la app va como incidencia (qué, dónde, con qué fixture). El código lo toca
  SOLO el modo `mantenimiento`, con sus reglas.
