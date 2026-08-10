# Ley de la Regresión al Nivel

Consultar este archivo cuando haya dudas sobre: cálculo de nivel, Gap, μ (puntos
esperados), gap ajustado por calendario, camino de recuperación, discretización
en bins, o interpretación de desviaciones.

> **Sincronizado con el motor** (`src/motor/regression.ts`, `src/motor/levels.ts`)
> y con `docs/MOTOR_SAD_EXTRACCION.md` §5. Ante cualquier duda manda el CÓDIGO.
> Última revisión de contenido: μ v2 (2026-07) + veredicto del backtest.

---

## Principio

Todo equipo tiene un **nivel real** que se mueve lento. Su **forma reciente** se
mueve rápido y es ruidosa. Cuando ambas se separan hay una **fuerza de regresión**
que empuja la forma de vuelta al nivel. La ley mide esa separación (**Gap**) y su
dirección.

Principio rector: **"el value no cura el reset"** — con señal clara de regresión,
una cuota atractiva no justifica ir en contra.

---

## 1. Cálculo del Nivel

Nivel continuo, recalculado partido a partido (`src/motor/levels.ts`).

### Componente de puntos (ventana de 20 partidos)

```
P = Σ(puntos últimos 20) / 20
```

Rango: 0.0 (todas derrotas) a 3.0 (todas victorias). Promedio típico ≈ 1.3 – 1.5.

### Componente de goles (últimos 5 de esa misma ventana)

```
G = Σ(gf − ga últimos 5) / Σ(gf + ga últimos 5)
```

Rango: −1.0 a +1.0. Si `total_goles = 0`, entonces `G = 0`.

### Nivel final

```
Nivel = P + G + 1
```

Rango típico: 0.5 – 3.5. Promedio ≈ 2.0 – 2.5. **Élite > 3.0.**

**Ventana de inicialización (retroactiva):** con menos de 20 partidos, todos los
registros valen `0.5`. En el partido nº 20 se calcula el primer nivel real y se
**asigna hacia atrás a los 20 primeros**.

**Nivel a fecha:** último registro con `date <= fecha` (búsqueda binaria). Hay
**dos fallbacks distintos y deliberados**:

| Contexto | Fallback | Motivo |
|---|---|---|
| Consumo general | `0.5` | Equipo sin historia = débil por defecto |
| Ponderar constantes K y niveles de rival | `1.0` | Evita anular los q* y disparar recálculos |

No unificarlos. Es la discrepancia 2 de §5, resuelta a favor del código.

---

## 2. Forma reciente

```
pts_recent = Σ(puntos últimos 5) / 5        → null si no hay 5 partidos
```

Ventana **5** (`RECENT_WINDOW`). Sin 5 partidos **no hay Gap**: se declara
"sin datos", nunca se estima.

---

## 3. μ — la expectativa (el corazón del modelo)

El Gap **no** compara forma contra nivel crudo. Compara forma contra **puntos
esperados**, dados por una regresión lineal calibrada:

```
μ = 1.241 + 0.334·nivel_equipo − 0.357·nivel_rival + 0.382·localía
    (recortado a [0, 3];  localía ∈ [0, 1])
```

Es la **v2 (2026-07)**, por OLS sobre 10 000 observaciones reales de `sad.db`
(`python -m backend.backtest_gap --calibrar`; RMSE 1.256 vs 1.291 de la v1).
Coeficientes estables en dos muestras independientes (3 000 y 10 000 obs).

**La v1 heredada** (`1.110 + 0.686·nivel − 0.669·rival + 0.422·localía`)
**duplicaba** el efecto de la diferencia de niveles: sobreestimaba a los
favoritos en ~0.4 pts y subestimaba a los débiles. Si un análisis viejo usó
esos coeficientes, sus gaps de favoritos están inflados.

### Estructura por liga (medida, no corregida)

Recalibrar por liga mejora el RMSE ≤ 0.022 → **una sola μ mundial basta**. Pero
la estructura existe y conviene mencionarla en la lectura cualitativa:

- **Localía**: de **+0.23** (amistosos) a **+0.73** (Perú). Sudamérica en
  +0.48…+0.73, casi el doble del 0.382 global.
- **Argentina**: pondera nivel/rival a la mitad (~±0.15) — liga de paridad.
- **Amistosos de clubes**: el bucket más grande de la base (12 783 fixtures),
  con los efectos más débiles de nivel y localía. Hoy alimentan forma y niveles
  como cualquier partido oficial.

---

## 4. Gap clásico — **el signo importa**

```
pts_esperados = μ(nivel, rival = 2.0, localía = 0.5)     ← rival promedio, localía neutra
gap           = pts_esperados − pts_recent
```

⚠️ **Convención del código, opuesta a la del documento original del SAD.** El doc
viejo definía `Gap = forma − nivel` (gap>0 = sobrerinde). El motor implementa
`gap = μ − forma`:

| Signo | Significado | Tendencia |
|---|---|---|
| `gap > 0` | rinde **POR DEBAJO** de su nivel | tiende a **mejorar** |
| `gap < 0` | rinde **POR ENCIMA** de su nivel | tiende a **empeorar** |

Es la misma información con el signo invertido y con expectativa basada en μ, no
en el nivel crudo. Un análisis que use la tabla vieja **emite la recomendación al
revés**.

### Umbrales de señal

| \|gap\| | Señal |
|---|---|
| `> 0.5` | **fuerte** |
| `0.3 – 0.5` | **leve** |
| `< 0.3` | **equilibrio** |

### Gap diferencial

```
gap_diff = gap_local − gap_visitante
```

Positivo = el local subrinde más que el visitante (más margen de mejora).

---

## 5. Gap ajustado por calendario (extensión aditiva)

El gap clásico es **asimétrico por construcción**: compara 5 partidos con rivales
y localías *reales* contra una expectativa *genérica* (rival 2.0, localía 0.5).
Cinco visitas seguidas a élites disparan un "subrinde" que no existe. La
corrección reusa la misma μ, sin recalibrar nada:

```
pts_esperados_ajustados = (1/5) · Σ μ(nivel_equipo, nivel_rival_i, localía_i)
                          sobre los MISMOS 5 partidos de pts_recent
gap_ajustado            = pts_esperados_ajustados − pts_recent
```

- `nivel_rival_i` = nivel continuo del rival **a la fecha de ese partido**
  (semántica `date <= fecha`, **fallback 1.0**).
- `localía_i` = 1 si fue local, 0 si visitante.
- Mismos umbrales y misma lectura de signo que el clásico.
- Es **aditivo**: el clásico se mantiene intacto (`gap`/`senal`/`tendencia`); el
  ajustado viaja en `gapAjustado`/`senalAjustada`/`tendenciaAjustada` +
  `ptsEsperadosAjustados` (contrato `GapEquipo`).
- `gap_diff_ajustado = gap_ajustado_local − gap_ajustado_visitante`.

**Regla de lectura:** cuando clásico y ajustado discrepan, la diferencia **es el
calendario** — y ese es el hallazgo, no un error. Reportar siempre los dos.

---

## 6. Camino de recuperación (calendario FUTURO) y partido trampa

El Gap dice *dirección*, no *dónde se expresa*. La regresión elige el partido
barato: quien subrinde hoy contra un grande mejora pasado mañana contra el débil.
El nivel se mantiene por caminos distintos. Capa **descriptiva** sobre μ, también
aditiva:

```
μ_partido        = μ(nivel, nivel_rival REAL del fixture analizado, localía real)
                   → si HOY puede expresarse la regresión
camino           = [ μ(nivel, rival_j, localía_j) de los próximos ≤3 fixtures ]
recuperabilidad  = media del camino (null si no hay próximos)
señal_calendario = blando si recuperabilidad > μ_genérica + 0.15
                   duro   si                 < μ_genérica − 0.15
                   neutro en el resto
```

| Gap | Calendario | Lectura |
|---|---|---|
| `> 0` (subrinde) | **blando** | mejora inminente |
| `> 0` (subrinde) | **duro** | mejora aplazada — no apostar hoy a la recuperación |
| `< 0` (sobrerinde) | **duro** | caída inminente |
| `< 0` (sobrerinde) | **blando** | caída aplazada |

**Partido trampa** (rotación/cansancio): rival de hoy con nivel ≤ propio − 0.8
**y** un "grande" (torneo internacional o rival de nivel ≥ propio) a ≤4 días
antes o después. Es una **BANDERA informativa**, no un término del modelo: μ no
tiene componente de fatiga y no se le inventa uno.

Umbrales (0.15 · 0.8 · 4 días · 3 próximos) siguen siendo **provisionales**.

Contrato: `muPartido`, `proximos[]` (rival, nivel, μ, localía, internacional,
días de descanso), `recuperabilidad`, `senalCalendario`, `partidoTrampa`.
Fixtures pospuestos/cancelados quedan fuera del camino.

---

## 7. Veredicto empírico — qué sostiene la evidencia

Backtest sin fuga (nivel y forma reconstruidos a `fecha − 1 s`), μ v2, n = 8 816
(`python -m backend.backtest_gap --muestra 800`):

1. **Al partido siguiente las señales del gap son débiles: ≤ 0.1 pts de
   residual.** La ley **no** es un predictor de resultado inmediato.
2. Lo único que **replicó en dos muestras**: el **sobrerinde fuerte PERSISTE**
   al partido siguiente (**+0.11 ± 0.05**). Es **anti-reversión**.
3. A ~5 partidos el gap clásico **insinúa** reversión suave. Ese, y no el
   partido siguiente, es su horizonte natural.
4. El gradiente **blando/duro no mostró poder incremental**. Queda como contexto
   descriptivo del camino de recuperación.
5. **Partido trampa: sin efecto incremental** (replicado 3 veces; +0.08 vs −0.00
   del control). Bandera, no matemática.

**Lectura de producto:** la tendencia del gap es **orientativa a mediano plazo**,
no una promesa inmediata.

### Hipótesis históricas — estado actual

| # | Hipótesis original | Estado |
|---|---|---|
| H1 | El nivel cambia lento (20), la forma es volátil (5) | **Vigente** — es el diseño del motor |
| H2 | A mayor \|Gap\|, mayor probabilidad de corrección | **No confirmada** al partido siguiente |
| H3 | El sub-rendimiento corrige más rápido que el sobre-rendimiento | **Desmentida** — lo que replicó fue lo contrario: el sobrerinde fuerte persiste |

No citar H2/H3 como si estuvieran validadas.

---

## 8. Discretización (10 bins fijos)

Solo para lectura y features de ML. **La matemática del Gap usa siempre el nivel
continuo**, nunca el bin (discrepancia 1 de §5, resuelta a favor del código).

| Bin | Rango | Etiqueta |
|---|---|---|
| 0 | < 0.6 | Sin datos |
| 1 | 0.6 – 1.3 | Muy débil |
| 2 | 1.3 – 1.6 | Débil |
| 3 | 1.6 – 1.9 | Regular bajo |
| 4 | 1.9 – 2.1 | Promedio bajo |
| 5 | 2.1 – 2.35 | Promedio |
| 6 | 2.35 – 2.55 | Promedio alto |
| 7 | 2.55 – 2.85 | Fuerte |
| 8 | 2.85 – 3.2 | Muy fuerte |
| 9 | > 3.2 | Élite |

---

## 9. Reglas duras para el análisis

- **El Gap no predice goles ni marcador.** Prohibido derivar Under/Over desde la
  Regresión sola.
- `|gap| ≥ 0.8` = **señal estructural** = mismo peso que un K techo (es la
  condición por la que la Ley 2 hereda cuando las K callan).
- La Regresión es **complementaria** (Nivel 2): nunca revierte una K clara.
- Nunca emitir Gap con menos de 5 partidos, ni Nivel con menos de 20.
- **Reportar siempre los dos gaps** (clásico y ajustado) y el signo explícito,
  para que nadie lo lea al revés.
- Declarar el horizonte: la señal es de mediano plazo (~5 partidos), no del
  partido de hoy.

### Formato sugerido del veredicto

```
LEY 2 — REGRESIÓN: [Equipo]
Nivel: [x.xx] (bin [n] · [etiqueta])   Forma 5: [x.xx] pts
Gap clásico:  [+/−x.xx] → [subrinde / sobrerinde] · señal [fuerte/leve/equilibrio]
Gap ajustado: [+/−x.xx] → [ídem]   (diferencia = efecto calendario)
Calendario futuro: [blando/neutro/duro] · recuperabilidad [x.xx]
Bandera partido trampa: [sí/no]
Horizonte: mediano plazo (~5 partidos). Estructural si |gap| ≥ 0.8.
```

---

## 10. Trampas a evitar

- **Signo invertido.** La trampa nº 1. `gap > 0` = SUBrinde en este motor.
- **Coeficientes v1.** Si aparecen `0.686 / −0.669`, el cálculo está desactualizado.
- **Nivel inflado por rivales débiles.** Contrastar contra el gap **ajustado**
  antes de concluir.
- **Copa vs liga.** La rotación habitual en copa deprime el nivel artificialmente.
- **Amistosos.** Un "bajón" construido sobre amistosos es ruido: hoy entran al
  cálculo como partidos oficiales.
- **Sobrevender el corto plazo.** El backtest dice que el partido siguiente
  apenas se mueve. Prometer corrección inmediata es ir contra la evidencia propia.
- **Value no cura el reset.** Una cuota alta no compensa una señal clara.
