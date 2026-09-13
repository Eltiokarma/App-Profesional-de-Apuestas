# Ley de la Regresión al Nivel

> **Versión alineada al motor (2026-08).** Reemplaza la referencia anterior, que **contradecía al código en tres puntos**: definía el Gap con el signo invertido (`forma − nivel` en lugar de `μ − forma`), no usaba la regresión μ, y sostenía dos hipótesis (H2 y H3) que el backtest desmintió. Fuentes: `docs/MOTOR_SAD_EXTRACCION.md` §5, `src/motor/regression.ts`, `src/motor/levels.ts`, `backend/backtest_gap.py`.
>
> **El código manda.** Si esta referencia y el motor discrepan alguna vez, gana el motor y hay que actualizar este archivo.

Consultar cuando haya dudas sobre: cálculo de nivel, Gap clásico, Gap ajustado por calendario, μ, camino de recuperación, partido trampa, discretización en bins, o interpretación de desviaciones.

---

## 1. Principio

Todo equipo tiene un **nivel real** que se mueve lento. Su **forma reciente** se mueve rápido y con ruido. Cuando ambas se separan, hay una fuerza que empuja la forma de vuelta al nivel. La ley mide esa separación (**Gap**) y su dirección.

Principio rector: **el value no cura el reset.** Con señal clara de regresión, una cuota atractiva no justifica ir en contra.

---

## 2. El Nivel

Nivel continuo, recalculado partido a partido:

```
P     = Σ(puntos de los últimos 20 partidos) / 20        → [0, 3]
G     = Σ(gf − ga últimos 5) / Σ(gf + ga últimos 5)      → [−1, +1]   (0 si no hubo goles)
Nivel = P + G + 1                                         → ~0.5 – 3.5
```

Ventana **20** para P (memoria estructural) y **5** para G dentro de esa misma ventana (dirección actual). **Élite > 3.0.**

**Inicialización retroactiva.** Con menos de 20 partidos, todos valen `0.5`. En el partido nº 20 se calcula el primer nivel real y se **asigna hacia atrás a los 20 primeros**.

**Nivel a fecha.** Último registro con `date <= fecha`, por búsqueda binaria. Hay **dos fallbacks distintos y deliberados**:

| Fallback | Cuándo | Por qué |
|----------|--------|---------|
| `0.5` | Consumo general | Valor conservador de equipo sin historial |
| `1.0` | Cuando pondera constantes K o niveles de rival (`CONSTANTS_LEVEL_FALLBACK`) | Un 0.5 anularía los q\* |

**No unificarlos.** La diferencia es intencional.

---

## 3. La forma reciente

```
pts_recent = Σ(puntos últimos 5) / 5      → null si no hay 5 partidos
```

Ventana **5** (`RECENT_WINDOW`). Sin 5 partidos **no hay Gap**: no se estima, se devuelve nulo.

---

## 4. μ — la expectativa · el corazón del modelo

El Gap **no** compara forma contra nivel crudo. Compara forma contra **puntos esperados**, dados por una regresión lineal calibrada:

```
μ = 1.241 + 0.334·nivel_equipo − 0.357·nivel_rival + 0.382·localía      (recortado a [0, 3])
```

Es la **v2 (2026-07)**, por OLS sobre 10 000 observaciones reales (`backtest_gap --calibrar`, RMSE 1.256 contra 1.291 de la v1). Coeficientes estables en dos muestras independientes.

> **La v1 heredada** (`1.110 / 0.686 / −0.669 / 0.422`) **duplicaba** el efecto de la diferencia de niveles y sobreestimaba a los favoritos en ~0.4 pts. Si aparece en algún lado, es código viejo.

### Estructura por liga — medida, no corregida

Recalibrar por liga mejora el RMSE en ≤0.022, así que **una sola μ mundial basta para la matemática**. Pero para la **lectura cualitativa** conviene decirlo cuando aplique:

| Liga / contexto | Particularidad | Consecuencia para la lectura |
|-----------------|----------------|------------------------------|
| **Perú** | Localía **+0.73** | Casi el doble del 0.382 global: el local vale más de lo que μ dice |
| **Sudamérica en general** | Localía **+0.48 … +0.73** | Corregir hacia arriba al local antes de decidir quién es favorito |
| **Argentina** | Nivel propio y de rival ponderados **a la mitad** (~±0.15) | Liga de paridad: un diferencial de μ chico **no** significa igualdad de fuerzas, significa que la liga comprime el coeficiente |
| **Amistosos** | Localía **+0.23** | El mínimo de la escala |

> ⛔ **PROHIBIDO RECALCULAR `μ_partido` CON ESTOS COEFICIENTES** *(alta 30.08.2026)*. Esta tabla es para **decir** que el local peruano vale más de lo que μ refleja. No es para sustituir el 0.382 dentro de la fórmula y volver a publicar el número. En el caso Moquegua–Alianza Atlético (F7 Clausura Perú 2026) el motor entregó μ 1.32 contra 1.44, con el **visitante** arriba; el analista aplicó el +0.73 peruano, publicó 1.67 contra 1.44 e invirtió el favorito. Ganó el visitante 1-4, y el movimiento de cuota se había ido en la dirección del motor.
>
> Tres razones por las que la corrección manual está mal, aunque el coeficiente medido sea correcto:
> 1. **El +0.73 ya está dentro del nivel.** Los niveles de los dos equipos se calculan sobre 20 partidos de la misma liga, así que la ventaja de campo peruana ya está incorporada en los puntos que cada uno acumuló de local y de visitante. Sumarla otra vez es contarla dos veces.
> 2. **Recalibrar por liga mejora el RMSE en ≤0.022.** El propio veredicto empírico de esta ley dice que una sola μ mundial basta para la matemática. Corregir a mano por partido cuesta más precisión de la que aporta.
> 3. **Si el coeficiente está mal, el arreglo es del motor.** Un cambio de localía por liga se prueba sobre la base entera con su RMSE, no se decide en un partido. Y **no vale publicar las dos versiones**: donde hay dos números propios, el analista elige en silencio el que le cierra la historia.

### El mercado como fuente — nivel y delta son dos cantidades *(alta 30.08.2026)*

El precio de cierre y el movimiento del precio responden preguntas distintas y hay que registrarlos por separado.

| Cantidad | Qué mide | Cómo se lee |
|----------|----------|-------------|
| **Nivel de cierre** | Dónde está el volumen: incluye el sesgo de local, de equipo grande y de sentimiento | Composición de la demanda, **no** probabilidad |
| **Delta apertura→cierre** | Información que entró durante la ventana previa | Señal informativa. **Cuando contradice al nivel, prevalece el delta** |
| **Forma del movimiento** | Escalón contra goteo | Un escalón en un solo tick es información entrando; un goteo es volumen acumulándose |
| **Comportamiento del empate** | Si el empate se mueve o queda congelado | Transferencia limpia entre los dos equipos con el empate en 0.0 = reponderación de fuerza. El empate moviéndose = dinero minorista, que apuesta a resultados |
| **Posición de la casa afilada** | Dónde está la casa de margen mínimo dentro del rango entre casas | En el medio → la dispersión es ruido minorista. En un extremo → desacuerdo informado |

Convertir siempre a **probabilidad implícita normalizada** antes de comparar con una matriz propia: los céntimos no son comparables entre selecciones, porque 0.30 sobre una cuota de 2.39 son 4.8 puntos de probabilidad y sobre 3.20 son 3.2.

---

## 5. Gap clásico — el signo importa

```
pts_esperados = μ(nivel, rival = 2.0, localía = 0.5)     ← rival promedio, localía neutra
gap           = pts_esperados − pts_recent
```

### Tabla de signo · la corrección más importante de esta versión

| Signo | Significado | Tendencia |
|---|---|---|
| **`gap > 0`** | rinde **por debajo** de su nivel — **sub-rendimiento** | tiende a **mejorar** |
| **`gap < 0`** | rinde **por encima** de su nivel — **sobre-rendimiento** | tiende a **empeorar** |

> **La referencia anterior tenía esto al revés.** Definía `Gap = forma − nivel`, con lo cual un `gap > 0` se leía como sobre-rendimiento y "precaución", cuando el motor lo emite como sub-rendimiento y "tiende a mejorar". Cualquier lectura construida sobre la tabla vieja **recomendaba en dirección contraria**. Al leer una salida del motor, verificar la etiqueta textual (`tiende a mejorar` / `tiende a empeorar`) además del número.

Umbrales: `|gap| > 0.5` **fuerte** · `0.3 – 0.5` **leve** · `< 0.3` **equilibrio**.

Diferencial del partido: `gap_diff = gap_local − gap_visitante`.

---

## 6. Gap ajustado por calendario · extensión aditiva

El gap clásico es **asimétrico por construcción**: compara 5 partidos con rivales y localías *reales* contra una expectativa *genérica*. Cinco visitas seguidas a élites disparan un "sub-rendimiento" que no existe. La corrección reusa la misma μ:

```
pts_esperados_ajustados = (1/5)·Σ μ(nivel_equipo, nivel_rival_i, localía_i)
                          sobre los MISMOS 5 partidos de pts_recent
gap_ajustado            = pts_esperados_ajustados − pts_recent
```

`nivel_rival_i` es el nivel continuo del rival **a la fecha de ese partido** (fallback 1.0), `localía_i` ∈ {0, 1}. Mismos umbrales y misma lectura de signo.

**Convive con el clásico, no lo reemplaza**: `gap` / `senal` / `tendencia` contra `gapAjustado` / `senalAjustada` / `tendenciaAjustada`.

> **Regla de lectura.** Cuando el clásico y el ajustado discrepan, **la diferencia es el calendario, y eso es el hallazgo** — no un error del motor ni una contradicción que haya que resolver eligiendo uno.

---

## 7. Camino de recuperación y partido trampa

El Gap dice *dirección*, no *dónde se expresa*. La regresión elige el partido barato: quien sub-rinde hoy contra un grande mejora pasado mañana contra el débil.

```
μ_partido        = μ(nivel, nivel_rival REAL del fixture, localía real)
camino           = [μ(nivel, rival_j, localía_j) de los próximos ≤3 fixtures]
recuperabilidad  = media del camino
señal_calendario = blando  si recuperabilidad > μ_genérica + 0.15
                   duro    si                 < μ_genérica − 0.15
                   neutro  en el resto
```

- `gap > 0` + **blando** → mejora inminente.
- `gap > 0` + **duro** → mejora **aplazada**: no apostar hoy a la recuperación.
- Simétrico para `gap < 0`.

**Partido trampa**: rival de hoy con nivel ≤ propio − 0.8 **y** un "grande" (torneo internacional, o rival de nivel ≥ propio) a ≤4 días antes o después. Es una **bandera informativa, no un término del modelo**: μ no tiene componente de fatiga y no se le inventa uno.

> **`μ_partido` y `gap` son cantidades distintas y responden preguntas distintas.** `μ_partido` responde *quién tiene más puntos esperados en este partido* — o sea quién es favorito, con rival y localía reales. `gap` responde *cuánto se desvía cada equipo de su propia expectativa genérica*. **Pueden apuntar en direcciones opuestas sin que ninguno esté mal**, y confundirlos es el error más fácil de cometer con esta ley. Si hace falta saber quién es favorito, el número es `μ_partido`, nunca el gap ni el gap diferencial.

---

## 8. Veredicto empírico · lo que evita sobrevender la ley

Backtest sin fuga (nivel y forma reconstruidos a fecha − 1 s), n = 8 816 con μ v2:

1. **Al partido siguiente las señales del gap son débiles: ≤0.1 pts de residual.** La ley **no** es un predictor de resultado inmediato.
2. Lo único que **replicó en dos muestras**: el **sobre-rendimiento fuerte PERSISTE** (+0.11 ± 0.05). Es **anti-reversión** — contradice la hipótesis clásica de que lo caliente se enfría rápido.
3. A ~5 partidos el gap clásico **insinúa** reversión suave. Ese, y no el partido siguiente, es su horizonte.
4. El gradiente **blando / duro no mostró poder incremental**: queda como contexto descriptivo.
5. **Partido trampa: sin efecto incremental**, replicado 3 veces. Bandera, no matemática.

**Lectura de producto:** la tendencia del gap es **orientativa a mediano plazo**, no promesa inmediata.

### Hipótesis del modelo · estado actual

| # | Hipótesis | Estado |
|---|-----------|--------|
| H1 | El nivel cambia lento (ventana 20), la forma es volátil (ventana 5) | **Vigente** |
| H2 | A mayor Gap absoluto, mayor probabilidad de corrección | **DESMENTIDA** por el backtest |
| H3 | Asimetría — el sub-rendimiento corrige más rápido que el sobre-rendimiento | **DESMENTIDA**, y el hallazgo replicado va en dirección opuesta: lo que persiste es el sobre-rendimiento fuerte |

> No reintroducir H2 ni H3 en ninguna lectura. Son intuitivas, suenan bien y están medidas como falsas.

---

## 9. Discretización · 10 bins fijos

**Solo para features y lectura, nunca para la matemática.**

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

## 10. Reglas duras

- **El Gap no predice goles ni marcador.** No derivar Under / Over desde la Regresión sola.
- `|gap| ≥ 0.8` = **señal estructural**, mismo peso que un K techo.
- **Nunca emitir Gap con menos de 5 partidos ni Nivel con menos de 20.** Se declara "sin datos", no se estima.
- Nivel inflado por rivales débiles → **contrastar contra el gap ajustado** antes de concluir.
- **Copa contra liga**: la rotación habitual deprime el nivel artificialmente.
- **Amistosos de clubes**: son el bucket más grande de la base (**12 783 fixtures**) y hoy alimentan forma y niveles como cualquier partido oficial. Un "bajón" de los últimos 5 construido sobre amistosos **es ruido**. Verificar la composición de la ventana antes de leer una señal.
- **Reportar siempre los dos gaps** —clásico y ajustado— más el signo explícito, para que nadie lo lea al revés.
- Si hace falta saber **quién es favorito**, usar `μ_partido`. El gap y el gap diferencial no responden esa pregunta.
- **`μ_partido` se publica como sale. Nunca se recalcula con la localía por liga** (ver la prohibición de la sección 4).
- **Corte de contexto: la ventana de 20 no atraviesa una discontinuidad estructural en silencio.** Cuando un equipo cruza un cambio de categoría, un desmantelamiento de plantel en el mercado de mitad de año o un cambio de sede, la ventana promedia a **dos equipos distintos** y devuelve un número único que no describe a ninguno de los dos. En el caso Moquegua (nivel 1.90) la ventana abarcaba un club sin estadio propio al arranque, un plantel desarmado en junio y constantes de otra categoría. **Se trunca la ventana en el corte, o se publican los dos niveles a cada lado con la diferencia declarada.** Nunca se publica el promedio solo.
- **La composición de la ventana de 5 se declara antes de leer la forma.** No solo por amistosos: un partido en altura, uno de copa con rotación o uno contra un rival de estilo opuesto contaminan el perfil que después se traslada al partido siguiente.

---

## 11. Trampas a evitar

| Trampa | Cómo se manifiesta | Antídoto |
|--------|--------------------|----------|
| **Signo invertido** | Leer `gap > 0` como sobre-rendimiento | Verificar la etiqueta textual `tiende a mejorar` / `tiende a empeorar` |
| **Confundir μ con gap** | Usar el gap diferencial para decidir quién es favorito | `μ_partido` para favoritismo, `gap` para desvío |
| **Nivel inflado** | Racha contra rivales débiles | Contrastar con el gap ajustado |
| **Ventana con amistosos** | "Bajón" de 5 partidos que son de pretemporada | Revisar la composición de la ventana |
| **Corrección manual de localía** | El analista suma el coeficiente de liga a `μ_partido` y el favorito se invierte | `μ_partido` se publica como sale del motor. Prohibido |
| **Corte de contexto no marcado** | Nivel único sobre una ventana que cruza un ascenso, un desmantelamiento o un cambio de sede | Truncar en el corte o publicar los dos niveles |
| **Perfil de posesión importado** | Se traslada el % de balón de un partido a otro como si fuera del equipo | La posesión es de la interacción. Declararla condicional al marcador |
| **Mercado leído solo por nivel** | Se toma la cuota de cierre como probabilidad y se ignora el movimiento | Registrar nivel **y** delta. El delta manda cuando contradice |
| **Copa deprimiendo el nivel** | Rotación sistemática | Anotarlo en la lectura, no corregir el número |
| **Predecir el partido siguiente** | "Le toca ganar porque sub-rinde" | ≤0.1 pts de residual: el horizonte es ~5 partidos |
| **Reintroducir H2 / H3** | "Cuanto más grande el gap, más rápido corrige" | Desmentidas por el backtest |
| **Value contra reset** | Cuota atractiva contra señal clara | El value no cura el reset |
