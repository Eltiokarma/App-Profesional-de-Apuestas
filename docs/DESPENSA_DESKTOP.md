# Despensa — la investigación que evita pagar búsquedas web en cada EFE

> **Dos caminos para llenarla.** El de abajo (escritorio, copiar-pegar) sigue
> valiendo para un apuro. El recomendado hoy es el **barrido en bloque
> versionado en el repo**, que se carga solo en cada deploy:
> [ver más abajo](#barrido-en-bloque-desde-el-repo-quincenal).

## Barrido EN BLOQUE desde el repo (quincenal)

La investigación vive como archivo en `backend/analisis/despensa/<liga>.json`,
se revisa en un PR y el backend la deposita en `efe.db` **al arrancar**: sin
tokens, sin red y sin que nadie tenga que acordarse de pegar nada.

```bash
python -m backend.analisis.despensa_bulk --listar   # qué hay y qué edad tiene
python -m backend.analisis.despensa_bulk            # cargar (idempotente)
python -m backend.analisis.despensa_bulk --liga peru-primera --forzar
```

Formato del archivo:

```json
{
  "liga": "Perú - Primera División (Liga 1 2026)",
  "investigado_en": "2026-07-27",
  "fuentes": ["https://…"],
  "equipos": [
    { "equipo": "Universitario de Deportes",
      "alias": ["Universitario"],
      "datos": { "dt": "…", "plantel": "…", "bajas": "" } }
  ]
}
```

Tres reglas que hacen que esto no mienta:

1. **`capturado_en` es `investigado_en`**, no la hora del deploy. Un bloque de
   hace un mes entra vencido y el EFE lo cuenta como faltante. Sellarlo con la
   fecha de carga sería fabricar frescura: el análisis creería tener datos de
   hoy sobre un plantel de hace un mes.
2. **Nunca pisa un dato más nuevo.** La carga manual de la víspera (bajas
   frescas) sobrevive a un redeploy que reinyecta el bloque quincenal.
3. **Campo vacío = la web no lo dijo.** No se rellena por intuición: se deja
   `""` y el EFE lo busca. Un DT inventado sale mucho más caro que una búsqueda.

`alias` existe porque los medios y la app (API-Football) no siempre llaman
igual al club ("Deportivo Moquegua" vs "UCV Moquegua"). Si ningún alias casa,
el log del arranque lo canta: `⚠ NO existen en la app (nadie leerá su
despensa)`. Ese aviso hay que atenderlo — el dato estaría depositado en una
clave que nadie consulta.

### El ciclo de 15 días

1. Pedirle a Claude Code el refresco del barrido (investiga en la web y
   reescribe los `<liga>.json` con la fecha del día).
2. Revisar el PR: se lee como texto, se ve qué cambió por club.
3. Merge → Railway redespliega → el log muestra `[despensa-bulk] …: N datos de
   M equipos`.

**Ojo con `bajas`:** su TTL son 48 h, así que un barrido quincenal NO lo
mantiene fresco (y no debe: una lesión de hace dos semanas es ruido). Las
lesiones confirmadas salen de la capa de jugadores (API-Football) y las dudas
de prensa, del barrido ligero de la víspera. Lo que el bloque quincenal cubre
de verdad es `dt` y `plantel`, que son justo los dos campos que solo da la web.

### La ventana cara ya no existe

Un TTL más corto que el barrido abre un día en que la despensa venció y el
barrido todavía no llegó — y ese día TODO EFE vuelve a pagar búsquedas. Estaba
"resuelto" pidiéndole al operador que pusiera una variable en Railway, que es
otra forma de decir que seguía abierto.

Ahora se cierra en el código, en dos capas:

1. **El TTL se deriva del barrido.** `SAD_DESPENSA_CADENCIA_DIAS` (15 por
   defecto) declara cada cuánto se barre, y el TTL sale de ahí + 2 días de
   margen. Cambiar la cadencia arrastra el TTL sola; no hay dos números que
   puedan desalinearse.
2. **Gracia para `dt` y `plantel`.** Si un barrido no se corre, un dato vencido
   pero de menos de un ciclo extra **se sigue sirviendo, declarando su edad**
   (`[dato de hace 19 días, sin refrescar…]`) en vez de disparar una búsqueda.
   Un plantel de hace tres semanas es peor que uno de ayer, pero es mucho mejor
   que pagar por buscarlo — y decir su edad deja que el análisis lo descuente.
   Pasada la gracia vuelve a contar como faltante: servir un dato viejo sin
   límite sí sería mentir.

Los demás tipos no llevan gracia porque no la necesitan: `tabla`, `resultados`
y `fixture` salen de `sad.db`, y `xi_reciente`/`bajas` de API-Football.

`SAD_DESPENSA_TTL_DIAS` sigue existiendo y manda si se fija explícitamente,
pero ya no hace falta tocarlo.

---

## Desde el Claude de escritorio (copiar-pegar)

El costo del EFE por API está dominado por el análisis EN FRÍO: investigar en
la web plantel, DT, bajas y contexto (~$0.50-0.80 por partido). Ese lote se
hace **gratis** en el Claude de escritorio/web (suscripción plana), **liga
entera de una vez**, y se deposita en la despensa de la app. El siguiente EFE
por API recibe todo como `datos_cacheados`, no lanza búsquedas web y cuesta
**~$0.10-0.20** (solo el razonamiento del protocolo).

## Flujo por liga (una vez por semana, ~5 min)

1. En la app, abre la página de la liga (p. ej. Primera División Perú) y pulsa
   **"Prompt despensa (liga entera)"** junto a la Clasificación: copia al
   portapapeles el prompt con los **nombres exactos** de todos los equipos.
2. Pégalo en tu Claude de escritorio (con búsqueda web). Claude investiga y
   devuelve **bloques JSON por tandas de 6 equipos** (para que ninguna
   respuesta se corte). Si se detiene, dile "continúa con la siguiente tanda".
3. En la app: pantalla de análisis de cualquier partido → **"Cargar
   investigación del Claude de escritorio"** → pega cada bloque → Depositar.
   (Cada tanda es una pegada; el orden da igual.)
4. Genera los EFE de la jornada: `faltantes (0-2)` y `costo≈$0.1x` en el log.

Repite por cada liga que vayas a apostar esa semana. El prompt es siempre el
mismo — solo cambia la liga, y el botón lo arma por ti.

## Qué se investiga en el escritorio y qué NO

El prompt pide SOLO lo que la web sabe y los datos no: `dt` (contexto),
`plantel` (lectura cualitativa) y `bajas` (dudas de prensa). El resto lo
cubre la app sin costo de búsqueda:

- `tabla`, `resultados`, `fixture`: de sad.db (gratis).
- `xi_reciente` (formación): de API-Football — el XI oficial si ya se publicó,
  o la alineación del último partido jugado si no (requests del plan, no web).
- lesiones confirmadas, plantel numérico y DT: capa de jugadores
  (docs/JUGADORES.md) donde API-Football tenga cobertura.

Precedencia: ficha de la base > despensa manual > búsqueda web.

## TTL de la despensa (cuándo repetir el barrido)

- `dt` y `plantel`: **14 días** — un barrido cada dos semanas basta.
- `bajas`: **48 h** — barrido ligero (solo ese campo) la víspera de la jornada.

## Nombres de equipo

El botón de la liga usa los nombres exactos de la app, así que no hay que
preocuparse. Si escribes el prompt a mano y un nombre no coincide, el backend
lo **canoniza** (match único, sin tildes/mayúsculas: "Betis" → "Real Betis");
la respuesta lista los ajustes en `canonizados`. Un nombre ambiguo o
desconocido se guarda tal cual y la respuesta lo delata: revísalo.

## El prompt (lo que genera el botón)

Por si quieres armarlo a mano o adaptarlo — mismo texto que
`src/lib/despensa.ts`:

```
Investiga en la web, con fuentes de hoy, a TODOS estos equipos de <LIGA>:

- <Equipo 1>
- <Equipo 2>
- … (la tabla completa de la liga)

SOLO estos tres campos por equipo — NO investigues tabla, resultados,
calendario, alineaciones, formaciones ni estadísticas de jugadores: la app ya
los saca de su propia base y de su API de datos. Interesa lo que las webs de
datos NO listan:

- dt: contexto del entrenador — fecha de asunción, interino o confirmado, cuestionamiento en prensa, relación con el vestuario.
- plantel: lectura CUALITATIVA — jerarquías reales, quién está en forma o caído, fichajes/salidas recientes y cómo encajan, conflictos o líos internos.
- bajas: dudas y novedades de PRENSA para el próximo partido — las lesiones confirmadas ya las tiene la app; interesan las dudas, sanciones internas, regresos y rumores de rotación.

ENTREGA POR TANDAS: un bloque de código JSON por cada 6 equipos (así ninguna
respuesta se corta). Cada bloque con esta forma exacta, sin texto fuera del
bloque:

{
  "equipos": [
    {
      "equipo": "<nombre EXACTAMENTE como te lo di>",
      "datos": { "dt": "…", "plantel": "…", "bajas": "…" }
    }
  ],
  "fuentes": ["url1", "url2"]
}

Máximo ~120 palabras por campo; si algo no lo encontraste, pon "" en ese
campo. Cuando termines una tanda, sigue con la siguiente hasta cubrir todos.
```

Consejo: guarda el prompt como un Proyecto en Claude ("Despensa SAD") con esta
instrucción fija — cada semana solo pegas la lista de equipos del botón.

## Cronología para el timeline (segundo prompt)

El mismo flujo sirve para el modo timeline: el botón **"Prompt timeline"**
(página de la liga, o el de los dos equipos en la caja del partido) pide los
eventos extra-cancha de los últimos 6 meses — cambios de DT, crisis,
sanciones, fichajes clave, hitos — como lista `timeline_eventos` por equipo
(tipos: `tecnico`, `institucional`, `sancion`, `hito`; los resultados de
partidos NO se piden: salen de sad.db). Se pega en la misma caja (puede ir
mezclado con las tandas de research) y dura **72 h** en la despensa.

Con la cronología de ambos equipos cargada, el timeline **no lanza ninguna
búsqueda web**: solo arma la película (~$0.03-0.06 con Haiku). El log lo
confirma: `[timeline] eventos frescos de ambos equipos: sin búsqueda web`.

## Automatización (opcional)

`POST /api/v1/analisis/despensa` con el mismo JSON y
`Authorization: Bearer $SAD_API_TOKEN` — sirve para subir por curl o script
los bloques guardados en un archivo:

```bash
curl -X POST "$API/api/v1/analisis/despensa" \
  -H "Authorization: Bearer $SAD_API_TOKEN" -H "Content-Type: application/json" \
  -d @tanda1.json
```
