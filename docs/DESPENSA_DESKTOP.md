# Despensa desde el Claude de escritorio — barrido de ligas gratis

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

## Automatización (opcional)

`POST /api/v1/analisis/despensa` con el mismo JSON y
`Authorization: Bearer $SAD_API_TOKEN` — sirve para subir por curl o script
los bloques guardados en un archivo:

```bash
curl -X POST "$API/api/v1/analisis/despensa" \
  -H "Authorization: Bearer $SAD_API_TOKEN" -H "Content-Type: application/json" \
  -d @tanda1.json
```
