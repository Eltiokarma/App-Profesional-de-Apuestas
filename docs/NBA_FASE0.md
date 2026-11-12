# NBA · fase 0 · ¿la teoría SAD ve algo que la cuota no?

> Pedido del usuario (12/11/2026): extender la teoría a otros deportes,
> empezando por el básquet, **solo NBA**, mercados **ganador y hándicap**.
> La fase 0 **solo mide**: no hay ingesta diaria, ni pantalla, ni skill. Si la
> teoría no separa nada que la cuota no tenga ya, no se construye nada más.

## 1. Qué se corre

```bash
python -m backend.nba.descarga     # ESPN, sin clave → ./nba_data (fuera de git)
python -m backend.nba.fase0        # → nba_data/fase0.json y fase0.txt
python -m backend.test_nba_fase0   # sin red, en CI
```

- **Fuente.** La API pública de ESPN, que no está documentada y no pide clave:
  el marcador por día y, por partido, las cuotas de cada casa (ganador y
  hándicap del local, con su cuota). Hay cuotas desde 2015-16.
  - API-Basketball (de API-Sports) pediría su propia suscripción.
  - stats.nba.com no responde desde el contenedor.
  - Como la API de ESPN no está documentada, puede cambiar sin aviso. Para
    medir alcanza; para producción habría que ver una fuente con contrato.
- **Qué entra.** Temporada regular, play-in y playoffs entre las 30
  franquicias. Quedan afuera la pretemporada, el All-Star y los partidos de
  gira.
- **Cancha neutral.** La burbuja de Orlando (30/07 al 11/10/2020) es neutral
  aunque ESPN no la marque así; también los partidos en México y París.
- **La cuota.** Es la mediana entre casas, sin las líneas en vivo ni la de
  apertura. La probabilidad es 1/cuota normalizada, o sea sin el margen de la
  casa. Es la línea que ESPN deja como «actual», que en un partido terminado
  es la de cierre (aproximada: no hay hora de captura).
- **Nada entra a `sad.db`** ni a la app.

## 2. El motor llevado al básquet (`backend/nba/motor.py`)

Es la misma teoría de `docs/MOTOR_SAD_EXTRACCION.md`. Lo que cambia es lo que
el básquet obliga a cambiar, y cada cambio queda como parámetro a la vista. El
motor del fútbol no se toca.

| pieza | fútbol | NBA (fase 0) | por qué |
|---|---|---|---|
| P del nivel | puntos 3/1/0 ÷ 20 | 3 × victorias ÷ 20 | no hay empate; se mantiene la escala 0–3 |
| G del nivel | Σ(gf−ga)/Σ(gf+ga), últimos 5 | lo mismo × **ESCALA_G** | en básquet ese cociente ronda ±0,05 y sin escalar no pesa; la escala se elige **en el entrenamiento** |
| q | \|dif\| × res × nivel rival | (\|dif\| ÷ **10**) × res × nivel rival | ganar por 10 ≈ ganar por 1 gol |
| visita | × 1,4 | × 1,4 (**sin calibrar**) | se dejó el del fútbol |
| reventón | a 0 (empate) o al otro signo | **siempre al otro signo** | no hay empate: cada derrota corta la + y abre la − |
| nivel en el backtest | el guardado con fecha anterior | el previo al partido; **sin** regla retroactiva | con menos de 20 partidos previos no hay nivel y el partido no entra |
| cancha neutral | — | sin factor de visita, no mueve local/visita | burbuja 2020, partidos internacionales |
| descanso | `jugadores.dias_descanso` | el mismo (por horas; ≤ 1 día = back-to-back) | la guardia de arquitectura |

## 3. Qué se mide (`backend/nba/fase0.py`)

Es el método del backtest del 1X2 del fútbol (`docs/REVENTON.md` §13):
logística ajustada con el 80 % más viejo y evaluada en el 20 % más nuevo,
log-loss por partido y la diferencia con un IC bootstrap emparejado (500
remuestreos). «Mejora» quiere decir que el IC queda entero bajo 0.

- **Ganador.** Hay cuatro modelos que van sumando piezas:
  - G0: el nivel con la localía.
  - G1: más el descanso.
  - G2: más la racha y las K.
  - G3: más el reventón (racha sobre su mediana, K sobre la mediana de su
    pico, rival en la dirección del riesgo). Es la teoría entera.

  Después vienen **MK0**, que es la cuota sola, y **MK1**, la cuota más la
  teoría. Lo que importa para apostar es MK1 contra MK0. Se agrega una
  simulación plana a la cuota mediana cuando MK1 ve 3 puntos o más de
  ventaja; es indicativa y no es la rentabilidad.
- **Hándicap.** La pregunta es si el local cubre la línea (los push quedan
  afuera). El motor predice el margen con una regresión, y la ventaja es el
  margen predicho más la línea. La vara es ln 2 (una moneda al aire) y el
  52,4 % que hace falta para ganarle a −110. También se compara el error del
  margen del motor con el de la línea misma.
- **Reventón.** Se toma cada lado con una racha abierta y base propia (3 o
  más reventones de ese signo). Se compara qué tan seguido se corta la racha
  con lo que decía la cuota, por largo de racha. Después, la logística de la
  cuota sola contra la cuota más la burbuja.

## 4. Resultados

(se completa con la corrida)
