# Skills del proyecto SAD

Esta carpeta es la **fuente de verdad** de los skills del SAD. Antes vivían solo
en la cuenta de claude.ai (`~/.claude/skills/`, `source: "custom"`), que se
sincroniza **hacia abajo** en cada sesión: el contenedor es efímero y cualquier
edición hecha ahí se pierde al terminar. Versionados acá, viajan con el código
que describen y se revisan en el mismo PR que lo cambia.

## Por qué importa: los skills describen matemática que se mueve

El motor (`src/motor/`, `backend/`) evoluciona; un skill que quedó en la versión
anterior no falla ruidosamente — **emite un análisis plausible y equivocado**.
Ejemplo real: `ley_regresion_nivel.md` mantuvo durante meses el signo invertido
del Gap (`forma − nivel` en vez de `μ − forma`), la μ v1 con coeficientes
duplicados, y dos hipótesis (H2/H3) que el backtest había desmentido.

## Contrato de sincronización

| Cambia esto… | …hay que revisar |
|---|---|
| `src/motor/regression.ts` · `MU`, umbrales | `sad-analysis/references/ley_regresion_nivel.md` |
| `src/motor/levels.ts` · ventanas, fallbacks | ídem (§1) |
| `src/motor/constants.ts` · q*/k*, fusión | `sad-analysis/SKILL.md` (fusión K) |
| `src/motor/discretizer.ts` · bins | `ley_regresion_nivel.md` §8 |
| `docs/MOTOR_SAD_EXTRACCION.md` | el reference correspondiente |
| Resultados de `backend/backtest_gap.py` | `ley_regresion_nivel.md` §7 (veredicto) |
| `backend/calendario.py` · `backend/cronologia.py` | `efe-dashboard`, `futbol-timeline` |
| `docs/efe-dtp/DTP_DISENO.md` | `diagnostico-tactico`, `teorema-del-echado` |

**Regla:** un PR que toca la matemática y no toca el skill que la describe
necesita una línea en la descripción explicando por qué no hacía falta.

## Cómo mantenerlos al día

1. **En el PR** — la tabla de arriba es la checklist. Es lo más barato y lo que
   más drift evita.
2. **Auditoría periódica** — una sesión programada relee `src/motor/`,
   `docs/MOTOR_SAD_EXTRACCION.md` y el último backtest, los contrasta contra
   cada skill y abre PR solo si encuentra divergencia real.
3. **Al cambiar la calibración** — después de `backtest_gap --calibrar`, los
   coeficientes nuevos van al código, al doc §5 **y** al reference. Los tres o
   ninguno.

## Prompt de auditoría (para la sesión programada)

> Audita los skills de `.claude/skills/` contra el código real del repo. Para
> cada reference verifica: fórmulas y coeficientes (¿coinciden con
> `src/motor/`?), convenciones de signo, umbrales, y si alguna afirmación
> empírica quedó desmentida por el último backtest. No reescribas por estilo:
> solo divergencias verificables, cada una citando `archivo:línea` del código
> que la contradice. Si no hay ninguna, no abras PR y decilo.

## Duplicados con la cuenta

Mientras un skill exista **a la vez** en la cuenta y en `.claude/skills/`, hay
dos copias con el mismo nombre y la sesión puede cargar la vieja. Al migrar uno,
borrar la versión de la cuenta (claude.ai → Skills) y dejar solo la del repo.

Estado actual:

| Skill | En el repo | En la cuenta |
|---|---|---|
| `sad-analysis` | ✅ (fuente de verdad) | pendiente de borrar |
| `efe-dashboard` | ❌ | ✅ |
| `diagnostico-tactico` | ❌ | ✅ |
| `teorema-del-echado` | ❌ | ✅ |
| `futbol-timeline` | ❌ | ✅ |
