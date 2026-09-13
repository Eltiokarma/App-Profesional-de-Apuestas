# Template de Referencia — Futbol Timeline HTML

Este documento contiene la estructura HTML/CSS/JS canónica para generar timelines. Claude debe adaptar este template según los equipos, colores y datos reales. No copiar literalmente — usar como guía estructural.

## Estructura general del documento

```html
<!DOCTYPE html>
<html lang="es">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Timeline: [Equipo A] vs [Equipo B] ([Período])</title>
  <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
    /* ... estilos completos abajo ... */
  </style>
</head>
<body>
  <!-- 1. HEADER -->
  <!-- 2. STATS BAR -->
  <!-- 3. FILTROS -->
  <!-- 4. LEYENDA -->
  <!-- 5. TIMELINE CONTAINER -->
  <!-- 6. SCRIPT DE FILTROS -->
</body>
</html>
```

## 1. Header

```html
<div class="header">
  <h1>[Equipo A] vs [Equipo B]</h1>
  <p>Calendario comparativo de sucesos · [Período]</p>
</div>
```

Para un solo equipo: `<h1>[Equipo]</h1>` sin "vs".

## 2. Stats Bar

Incluir 4-6 bloques de estadísticas clave. Adaptar según el contexto. Ejemplos:

- Posición en tabla
- Puntos
- Última victoria
- Racha actual (partidos sin ganar, invictos, etc.)
- Diferencia de gol
- Goles a favor / en contra

```html
<div class="stats-bar">
  <div class="stat-block">
    <div class="label">[Equipo] — Posición</div>
    <div class="value [clase-color]">[valor]</div>
  </div>
  <!-- repetir por cada stat -->
</div>
```

## 3. Filtros

Botones clicables que muestran/ocultan eventos. Siempre incluir "Todo" como activo por defecto.

```html
<div class="filters">
  <button class="filter-btn active" data-filter="all">Todo</button>
  <button class="filter-btn" data-filter="equipoA">[Equipo A]</button>
  <button class="filter-btn" data-filter="equipoB">[Equipo B]</button>
  <button class="filter-btn" data-filter="institucional">Institucional</button>
  <button class="filter-btn" data-filter="partido">Partidos</button>
</div>
```

Para un solo equipo, omitir los botones de equipo individual.

## 4. Leyenda

```html
<div class="legend">
  <div class="legend-item"><div class="legend-dot" style="background:#5c5"></div>Victoria</div>
  <div class="legend-item"><div class="legend-dot" style="background:#e66"></div>Derrota</div>
  <div class="legend-item"><div class="legend-dot" style="background:#cc5"></div>Empate</div>
  <div class="legend-item"><div class="legend-dot" style="background:#c8f"></div>Institucional</div>
  <div class="legend-item"><div class="legend-dot" style="background:#6af"></div>Técnico</div>
  <div class="legend-item"><div class="legend-dot" style="background:#fa6"></div>Sanción</div>
  <div class="legend-item"><div class="legend-dot" style="background:#5dc"></div>Hito</div>
</div>
```

Solo incluir los tipos que realmente aparecen en el timeline.

## 5. Timeline Container

### Separador de mes
```html
<div class="month-label"><span>[MES AÑO]</span></div>
```

### Evento de equipo A (izquierda)
```html
<div class="event-row left" data-team="equipoA" data-cat="partido">
  <div class="event-card">
    <div class="event-date">[DD MMM YYYY] · Fecha [N]</div>
    <span class="team-badge badge-equipoA">[EQUIPO A]</span>
    <span class="event-type type-[tipo]">[Etiqueta]</span>
    <div class="event-title">[Título corto]</div>
    <div class="event-detail">[Contexto 1-2 oraciones]</div>
  </div>
  <div class="dot-center dot-equipoA"></div>
</div>
```

### Evento de equipo B (derecha)
Misma estructura, pero con `class="event-row right"` y badges/dots del equipo B.

### Evento compartido (centro)
```html
<div class="event-row center" data-team="both" data-cat="partido">
  <div class="event-card">
    <div class="event-date">[Fecha]</div>
    <span class="team-badge badge-equipoA">[EQ A]</span>
    <span class="team-badge badge-equipoB" style="margin-left:4px">[EQ B]</span>
    <span class="event-type type-hito">[Etiqueta]</span>
    <div class="event-title">[Título]</div>
    <div class="event-detail">[Detalle]</div>
  </div>
  <div class="dot-center dot-both"></div>
</div>
```

## 6. Script de filtros

```javascript
document.querySelectorAll('.filter-btn').forEach(btn => {
  btn.addEventListener('click', () => {
    document.querySelectorAll('.filter-btn').forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
    const filter = btn.dataset.filter;
    
    document.querySelectorAll('.event-row').forEach(row => {
      if (filter === 'all') {
        row.classList.remove('hidden');
      } else if (filter === 'equipoA') {
        row.classList.toggle('hidden', row.dataset.team !== 'equipoA');
      } else if (filter === 'equipoB') {
        row.classList.toggle('hidden', row.dataset.team !== 'equipoB' && row.dataset.team !== 'both');
      } else if (filter === 'institucional') {
        row.classList.toggle('hidden', row.dataset.cat !== 'institucional');
      } else if (filter === 'partido') {
        row.classList.toggle('hidden', row.dataset.cat !== 'partido');
      }
    });
  });
});
```

## CSS Completo

Sección de estilos canónica. Adaptar colores de equipo según corresponda.

### Variables de color por equipo

Asignar colores reales del equipo. Ejemplos de mapping:

| Equipo | Color primario | Uso |
|--------|---------------|-----|
| River Plate | #c83232 (rojo) | badges, dots, stats |
| Boca Juniors | #1a3c7a (azul) | badges, dots, stats |
| Pereira | #c8aa32 (dorado) | badges, dots, stats |
| Cúcuta | #c83232 (rojo/negro) | badges, dots, stats |
| Nacional | #1a7a1a (verde) | badges, dots, stats |
| Millonarios | #1a3caa (azul) | badges, dots, stats |
| América Cali | #cc2222 (rojo) | badges, dots, stats |
| Junior | #cc2222 (rojo) | badges, dots, stats |
| Alianza Lima | #1a2a5a (azul) | badges, dots, stats |

Si no se conoce el color exacto del equipo, usar dorado para equipo izquierdo y rojo para equipo derecho.

### Estilos base (copiar y adaptar)

```css
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
  font-family: 'Inter', sans-serif;
  background: #0a0a0f;
  color: #e0e0e0;
  padding: 20px;
  min-height: 100vh;
}

.header {
  text-align: center;
  margin-bottom: 40px;
  padding: 30px 20px;
  background: linear-gradient(135deg, rgba([colorA],0.15), rgba(20,20,40,0.8), rgba([colorB],0.15));
  border-radius: 16px;
  border: 1px solid rgba(255,255,255,0.08);
}

.header h1 {
  font-size: 1.8rem;
  font-weight: 800;
  background: linear-gradient(90deg, [colorA], #fff, [colorB]);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  margin-bottom: 8px;
}

.header p { color: #888; font-size: 0.85rem; }

.legend {
  display: flex;
  justify-content: center;
  gap: 24px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.legend-item { display: flex; align-items: center; gap: 8px; font-size: 0.78rem; color: #aaa; }
.legend-dot { width: 12px; height: 12px; border-radius: 50%; }

.filters {
  display: flex;
  justify-content: center;
  gap: 10px;
  margin-bottom: 30px;
  flex-wrap: wrap;
}

.filter-btn {
  padding: 6px 16px;
  border-radius: 20px;
  border: 1px solid rgba(255,255,255,0.15);
  background: rgba(255,255,255,0.05);
  color: #ccc;
  cursor: pointer;
  font-size: 0.75rem;
  font-family: 'Inter', sans-serif;
  transition: all 0.2s;
}

.filter-btn:hover { background: rgba(255,255,255,0.1); }
.filter-btn.active { background: rgba(255,255,255,0.15); color: #fff; border-color: rgba(255,255,255,0.3); }

.timeline-container {
  max-width: 900px;
  margin: 0 auto;
  position: relative;
}

.timeline-line {
  position: absolute;
  left: 50%;
  top: 0;
  bottom: 0;
  width: 2px;
  background: linear-gradient(to bottom, rgba(255,255,255,0.05), rgba(255,255,255,0.12), rgba(255,255,255,0.05));
  transform: translateX(-50%);
}

.month-label {
  text-align: center;
  margin: 30px 0 16px;
  position: relative;
  z-index: 2;
}

.month-label span {
  background: #14141e;
  padding: 6px 20px;
  border-radius: 20px;
  font-size: 0.72rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 2px;
  color: #666;
  border: 1px solid rgba(255,255,255,0.08);
}

.event-row {
  display: flex;
  align-items: flex-start;
  margin-bottom: 12px;
  position: relative;
}

.event-row.left .event-card { margin-right: auto; margin-left: 0; }
.event-row.right .event-card { margin-left: auto; margin-right: 0; }

.event-card {
  width: 44%;
  padding: 14px 16px;
  border-radius: 10px;
  position: relative;
  transition: transform 0.15s;
}

.event-card:hover { transform: translateY(-1px); }

/* Equipo A = izquierda */
.event-row.left .event-card {
  background: linear-gradient(135deg, rgba([colorA],0.12), rgba([colorA],0.04));
  border: 1px solid rgba([colorA],0.2);
}

/* Equipo B = derecha */
.event-row.right .event-card {
  background: linear-gradient(135deg, rgba([colorB],0.12), rgba([colorB],0.04));
  border: 1px solid rgba([colorB],0.2);
}

/* Evento compartido = centro */
.event-row.center .event-card {
  width: 60%;
  margin: 0 auto;
  background: linear-gradient(135deg, rgba(100,100,200,0.12), rgba(100,100,200,0.04));
  border: 1px solid rgba(100,100,200,0.2);
}

.event-date {
  font-size: 0.65rem;
  font-weight: 600;
  color: #777;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 4px;
}

.event-type {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 0.6rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 6px;
}

.type-resultado { background: rgba(50,180,50,0.2); color: #5c5; }
.type-derrota { background: rgba(220,50,50,0.2); color: #e66; }
.type-empate { background: rgba(200,200,50,0.2); color: #cc5; }
.type-institucional { background: rgba(200,100,255,0.2); color: #c8f; }
.type-tecnico { background: rgba(50,150,255,0.2); color: #6af; }
.type-sancion { background: rgba(255,100,50,0.2); color: #fa6; }
.type-hito { background: rgba(50,220,200,0.2); color: #5dc; }

.event-title {
  font-size: 0.82rem;
  font-weight: 600;
  color: #ddd;
  line-height: 1.3;
  margin-bottom: 4px;
}

.event-detail {
  font-size: 0.72rem;
  color: #999;
  line-height: 1.4;
}

.team-badge {
  font-size: 0.6rem;
  font-weight: 700;
  padding: 2px 6px;
  border-radius: 3px;
  margin-bottom: 6px;
  display: inline-block;
}

/* Adaptar colores de badge por equipo */
.badge-equipoA { background: rgba([colorA],0.3); color: [colorA-light]; }
.badge-equipoB { background: rgba([colorB],0.3); color: [colorB-light]; }

.dot-center {
  position: absolute;
  left: 50%;
  top: 20px;
  width: 10px;
  height: 10px;
  border-radius: 50%;
  transform: translateX(-50%);
  z-index: 3;
}

.dot-equipoA { background: [colorA]; box-shadow: 0 0 8px rgba([colorA],0.4); }
.dot-equipoB { background: [colorB]; box-shadow: 0 0 8px rgba([colorB],0.4); }
.dot-both { background: #6666cc; box-shadow: 0 0 8px rgba(100,100,200,0.4); }

.stats-bar {
  display: flex;
  justify-content: center;
  gap: 40px;
  margin: 30px 0;
  padding: 20px;
  background: rgba(255,255,255,0.03);
  border-radius: 12px;
  border: 1px solid rgba(255,255,255,0.06);
  flex-wrap: wrap;
}

.stat-block { text-align: center; }
.stat-block .label { font-size: 0.65rem; color: #666; text-transform: uppercase; letter-spacing: 1px; }
.stat-block .value { font-size: 1.4rem; font-weight: 800; margin-top: 4px; }

.hidden { display: none; }

@media (max-width: 700px) {
  .event-card { width: 85% !important; }
  .event-row.left .event-card,
  .event-row.right .event-card { margin: 0 auto; }
  .timeline-line { left: 16px; }
  .dot-center { left: 16px; }
  .header h1 { font-size: 1.3rem; }
}
```

## Notas de diseño

- Las cards nunca deben tener borde sólido brillante. Siempre semitransparente con `rgba`.
- El hover es sutil (1px arriba). Nada dramático.
- Los filtros usan `classList.toggle('hidden', condición)` para mostrar/ocultar.
- El data-team debe ser un ID sin espacios (ej: "pereira", "cucuta", "river", "boca").
- El data-cat es "partido" o "institucional" (para filtros).
- Para timeline de un solo equipo, adaptar: timeline-line a `left: 16px`, todos los event-row como `left`, sin filtros de equipo.
