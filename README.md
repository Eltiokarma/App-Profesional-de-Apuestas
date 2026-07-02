# SAD · Análisis pre-partido

Web app **desktop-first y responsive** para análisis pre-partido de fútbol y apuestas.
Implementada en **React + Vite + TypeScript** a partir del prototipo de Claude Design
(`project/SAD.dc.html`). Estética oscura tipo terminal deportiva, con tema claro/oscuro,
tipografía editorial (Archivo) y monospace (IBM Plex Mono) para cuotas y métricas.

## Secciones

- **Cuotas** (la estrella) — cada cuota es una **gráfica de movimiento** desde la apertura
  hasta el final del partido. Tabs por mercado (1X2, Doble oportunidad, Más/Menos, Hándicap,
  Ambos marcan), leyenda con **% de variación** en vivo, tarjetas de mercado con sparklines y
  marcado manual de value bets. Modos Prepartido / En vivo (marcador, minuto, divisor KO y
  línea del minuto actual).
- **Burbujas** — constantes K (Dixon-Coles) como bubble chart: tamaño = magnitud,
  color = nivel del rival, posición = favorable/desfavorable. Selector de constante y de modelo,
  panel de valores y "Próximos 3".
- **Skills** — tarjetas EFE / SAD / DT / Timeline con generar → spinner → generado. EFE abre
  como dashboard (gauges, bloques A–E, alertas); los demás como reporte por secciones. Historial.
- **Estadísticas** — forma últimos 5, comparativa con barras, H2H y tabla de posiciones.

Incluye header de fixture persistente, **menú de partidos tipo BeSoccer** agrupado por
competición, estados vacíos, loading skeletons, **vista de celular** (tab bar inferior +
previsualización en marco de teléfono con el botón 📱) y datos de ejemplo realistas. Todo en español.

## Cómo ejecutar

```bash
npm install
npm run dev      # servidor de desarrollo (http://localhost:5173)
npm run build    # typecheck + build de producción a dist/
npm run preview  # sirve el build de producción
```

## Estructura

- `src/data/` — equipos, partidos, tablas, definiciones de mercados/skills/niveles (tipados).
- `src/lib/` — helpers puros: PRNG determinista, series de cuotas, construcción de la gráfica
  (`chart.ts`), sparklines, burbujas (`bubbles.ts`), vista de partido (`view.ts`).
- `src/store.ts` — estado central de la app (hook `useSad`), espejo del `DCLogic` del prototipo.
- `src/components/` — sidebar, headers desktop/móvil, match picker, bottom nav, SVG de la gráfica, estados.
- `src/sections/` — las 4 secciones (Cuotas, Burbujas, Skills, Estadísticas).
- `project/`, `chats/` — bundle original de Claude Design (referencia de diseño e intención).

---

# CODING AGENTS: READ THIS FIRST

This is a **handoff bundle** from Claude Design (claude.ai/design).

A user mocked up designs in HTML/CSS/JS using an AI design tool, then exported this bundle so a coding agent can implement the designs for real.

## What you should do — IMPORTANT

**Read the chat transcripts first.** There are 1 chat transcript(s) in `chats/`. The transcripts show the full back-and-forth between the user and the design assistant — they tell you **what the user actually wants** and **where they landed** after iterating. Don't skip them. The final HTML files are the output, but the chat is where the intent lives.

**Read `project/SAD.dc.html` in full.** The user had this file open when they triggered the handoff, so it's almost certainly the primary design they want built. Read it top to bottom — don't skim. Then **follow its imports**: open every file it pulls in (shared components, CSS, scripts) so you understand how the pieces fit together before you start implementing.

**If anything is ambiguous, ask the user to confirm before you start implementing.** It's much cheaper to clarify scope up front than to build the wrong thing.

## About the design files

The design medium is **HTML/CSS/JS** — these are prototypes, not production code. Your job is to **recreate them pixel-perfectly** in whatever technology makes sense for the target codebase (React, Vue, native, whatever fits). Match the visual output; don't copy the prototype's internal structure unless it happens to fit.

**Don't render these files in a browser or take screenshots unless the user asks you to.** Everything you need — dimensions, colors, layout rules — is spelled out in the source. Read the HTML and CSS directly; a screenshot won't tell you anything they don't.

## Bundle contents

- `README.md` — this file
- `chats/` — conversation transcripts (read these!)
- `project/` — the `SAD: análisis pre-partido` project files (HTML prototypes, assets, components)
