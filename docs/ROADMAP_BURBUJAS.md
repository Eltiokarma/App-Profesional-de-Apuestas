# Roadmap · Familias nuevas de burbujas (K especializadas)

> Spec del proyecto futuro acordado: extender el motor de acumuladores K a
> familias por tipo de evento y a las cuotas prepartido capturadas. La
> visualización ya existe (gráfica de líneas de picos acumulados con reseteo,
> `src/components/KLineChart.tsx`); lo que se define aquí es **qué acumular**.

## 1. Burbujas por mercado: Doble Oportunidad

Acumulador `k_dc` que crece mientras el equipo **no pierde** (1X desde su
perspectiva) y se resetea al perder:

```
q_dc = dif × nivel_rival           si res ∈ {victoria, empate} → k_dc += max(q_dc, 0.5·nivel_rival)
                                   si res = derrota            → k_dc = 0
```

(el empate aporta un mínimo proporcional al nivel del rival para que la racha
"sin perder" crezca aunque no haya diferencia de goles). Variantes local/visita
con la misma regla de condición que las K actuales.

## 2. Burbujas por margen: derrota/victoria por N goles

Familias paramétricas por margen exacto de goles `N ∈ {1, 2, 3+}`:

- `k_derrota_1`: acumula `nivel_rival` cada partido consecutivo perdido por
  exactamente 1 gol; se resetea cuando el margen de derrota cambia o el equipo
  puntúa. Análogas `k_derrota_2`, `k_derrota_3plus`.
- `k_victoria_1`, `k_victoria_2`, `k_victoria_3plus`: simétricas para victorias.

Semántica: son detectores de **patrones de marcador sostenidos** ("siempre
pierde por la mínima"), insumo directo para la Ley del Marcador. Reglas de
reseteo idénticas al motor: solo una familia del mismo signo ≠ 0 a la vez.

## 3. Burbujas sobre cuotas prepartido

Acumuladores sobre la **cuota prepartido capturada** (tabla `odds`), no sobre
el resultado:

- `k_cuota_favorito`: acumula mientras el equipo cierra como favorito
  (cuota 1X2 propia mínima del mercado) y **cumple**; se resetea cuando siendo
  favorito no gana. El aporte es `(1/cuota) × nivel_rival` — favorito ante
  rival fuerte aporta más.
- `k_cuota_tapado`: espejo para victorias cerrando como no-favorito, con
  aporte `cuota × nivel_rival` (sorpresas grandes acumulan más).

### Partidos sin cuota capturada (huecos)

Las cuotas se llevan capturando meses, pero la historia de partidos llega a
~5 años: habrá huecos. Regla elegida (conservadora, no inventa datos):

1. Un partido **sin cuota capturada no aporta ni resetea** las k_cuota_* —
   conserva el valor anterior (misma semántica que los k local/visita fuera de
   su condición). En la gráfica se marca atenuado ("sin cuota").
2. La racha de cuotas lleva su propio contador de partidos **con** dato, y la
   UI muestra la cobertura ("k_cuota sobre 14 de 20 partidos").
3. Nunca se interpola una cuota: si el hueco supera un umbral configurable
   (p. ej. 10 partidos seguidos sin dato), el acumulador se marca "sin
   cobertura suficiente" en vez de mostrarse como racha válida.

## 4. Cambios de infraestructura que requiere

| Pieza | Cambio |
|---|---|
| Pipeline (Python) | nuevas columnas en `constants`/`processed_matches` por familia; misma detección retroactiva e idempotencia |
| Contrato (`openapi.yaml`) | `fusion` pasa a incluir las familias nuevas; endpoint `/cuotas/{fixtureId}` histórico por fixture ya existe |
| Web | `FUSED_KEY` se amplía con las familias; el selector de tipo de K crece a grupos (Resultado · Goles · Mercados · Márgenes) |
| Datos | timestamp de captura en `odds` (hoy no existe) para poder auditar cobertura |

## 5. Orden de implementación sugerido

1. `k_dc` (una familia, valida el patrón end-to-end en pipeline + contrato + UI).
2. Márgenes (`derrota/victoria por N`) — son 6 acumuladores mecánicos del mismo molde.
3. `k_cuota_*` con la regla de huecos (requiere timestamp de captura en `odds`).
