# Despensa desde el Claude de escritorio — investigación gratis

El costo del EFE por API está dominado por el análisis EN FRÍO: investigar en
la web plantel, DT, bajas y contexto de dos equipos (~$0.50-0.80). Ese primer
lote se puede hacer **gratis** en el Claude de escritorio/web (suscripción
plana) y depositarlo en la despensa de la app. El siguiente EFE por API recibe
todo como `datos_cacheados`, no lanza búsquedas web y cuesta **~$0.10-0.20**
(solo el razonamiento del protocolo).

## Flujo (2 minutos por lote)

1. Abre tu Claude de escritorio y pega el prompt de abajo, rellenando los
   partidos (los nombres de los equipos EXACTOS como salen en la app).
2. Claude investiga y devuelve un bloque JSON.
3. En la app: pantalla de análisis de cualquier partido → **"Cargar
   investigación del Claude de escritorio"** → pega el JSON → Depositar.
4. Pulsa "Generar análisis EFE": verás en el log `faltantes (0-2)` y
   `costo≈$0.1x`.

Un solo lote puede traer TODOS los equipos del fin de semana. Los TTL de la
despensa: DT y plantel 14 días · fixture 7 días · XI y bajas 48 h · tabla y
resultados 24 h (estos dos igual salen gratis de sad.db — no hace falta
investigarlos). Carga el lote el día del partido o la víspera.

## Prompt para el Claude de escritorio

Copia desde aquí, edita la lista de partidos y pégalo en Claude
(escritorio o web, con búsqueda web activada):

```
Investiga en la web, con fuentes de hoy, a los equipos de estos partidos:

- Universitario vs Alianza Lima (Liga 1 Perú)
- ADT vs Sporting Cristal (Liga 1 Perú)

Para CADA equipo produce resúmenes TEXTUALES densos y autocontenidos
(nombres, fechas, cifras, fuente) de estos campos:

- dt: entrenador actual, fecha de asunción, contexto (interino, cuestionado…).
- plantel: jugadores clave con posición y rendimiento, fichajes/salidas
  recientes, dependencias ofensivas.
- bajas: lesionados, sancionados y dudas para el próximo partido, con motivo.
- xi_reciente: el once más reciente y la formación utilizada.
- fixture: sus próximos 3-5 partidos con fechas y torneos.

Al final devuélveme EXCLUSIVAMENTE un bloque de código JSON con esta forma
(sin texto fuera del bloque):

{
  "equipos": [
    {
      "equipo": "Universitario",
      "datos": {
        "dt": "…",
        "plantel": "…",
        "bajas": "…",
        "xi_reciente": "…",
        "fixture": "…"
      }
    }
  ],
  "fuentes": ["url1", "url2"]
}

Los nombres en "equipo" deben ser EXACTAMENTE los que te di arriba. Máximo
~120 palabras por campo. Si algo no lo encontraste, pon "" en ese campo.
```

## Notas

- **Tipos válidos**: `dt`, `plantel`, `tabla`, `resultados`, `fixture`,
  `xi_reciente`, `bajas`. Otros se ignoran (la respuesta lo indica). `tabla`
  y `resultados` no hace falta pedirlos: la app ya los tiene de su base.
- **El nombre del equipo debe coincidir con `teams.name`** de la app (el que
  ves en el buscador o en la página del equipo). Si no coincide, el depósito
  se guarda bajo otro nombre y el EFE no lo encuentra.
- Vía curl (para automatizar): `POST /api/v1/analisis/despensa` con el mismo
  JSON y `Authorization: Bearer $SAD_API_TOKEN`.
- La capa de jugadores (docs/JUGADORES.md) sigue cubriendo plantel/dt/bajas
  gratis desde API-Football cuando hay cobertura: la despensa manual manda
  sobre la web, y la ficha de la base manda sobre ambas. Cuantas más fuentes
  gratis, menos busca la API.
