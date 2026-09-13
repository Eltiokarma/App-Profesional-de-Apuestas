# Casos de referencia — Auditorías SAD

Precedentes reales donde el protocolo SAD falló y se corrigió. Cada caso está vinculado a una regla específica. Consultar cuando haya duda sobre cómo aplicar una regla, o para evitar errores recurrentes.

---

## Caso 1: Real Madrid vs Getafe — 02/03/2026 (0-1)

**Regla vinculada:** convergencia de K techo + doble oportunidad trampa + Tensión del Favorito → el favorito no gana.

**Señales que existían pre-partido:**

- `k_local = 41.7` (mismo techo que el estallido anterior en 41.2).
- Doble oportunidad `1X = 1.07` → trampa textual (por encima de 1.05).
- Tensión del Favorito: 51.5% de probabilidad de ruptura.
- Burbuja de historial directo: 8 victorias consecutivas de Real Madrid sobre Getafe.
- `k_goles_anotado` en 103.7 → reventó (burst) a 0.

**Error cometido:** se diluyó la convergencia con argumentos de historial directo (*"siempre le gana al Getafe"*) y con el nombre del equipo.

**Lección:** cuando **K techo + doble oportunidad trampa + Tensión del Favorito** convergen, el favorito **no gana**. No diluir con historial directo, Poisson ni reputación. **Nunca.**

---

## Caso 2: Newcastle vs Manchester City — FA Cup, 07/03/2026

**Regla vinculada:** Ley 4 Escenario 3 — las bajas estructurales **congelan** las K.

**Señales:**

- Newcastle con ausencias estructurales (Bruno Guimarães, Schär y otros).
- Las K estaban en techo y debían estallar → en vez de eso, **siguieron creciendo**.
- Manchester City con rotación defensiva pero ofensiva intacta → `k_goles_visita_anotado` **no se depreció**.

**Error cometido:** se esperaba un estallido de las K de Newcastle por estar en techo, sin verificar que el XI que había acumulado esa presión no era el que iba a jugar.

**Lección:** el estallido requiere el **mismo XI** que acumuló la presión. Sin ese XI, la presión se desborda — la K puede seguir creciendo en lugar de estallar. Una rotación que afecta solo a la defensa deja intacta `k_goles_anotado`. La dominancia individual en historial directo de un jugador confirmado como titular sí modifica las lecturas K.

---

## Caso 3: Bologna vs Hellas Verona — 08/03/2026 (1-2) — Caso fundacional de v3.1

**Reglas vinculadas:** Ley 9 (Nivel sobre nombre) + convergencia multi-señal + Ley 3 bidireccional + Auditoría 1 + cumplimiento de mínimo del underdog.

### Señales que existían y fueron desactivadas

1. **`k_general` = 12.25** (percentil 76 de estallidos, supera mediana de 24 meses).
   - **Desactivado con:** *"rival de nivel 1.23 no provoca estallidos"* → **violación clara de Ley 9.**

2. **2 desaceleraciones consecutivas de `k_general`** (Δ +14.8 → +5.8 → +3.9).
   - Minimizado como *"refuerza el 1-0"* en vez de activarse como señal de estallido inminente.

3. **Patrón de trayectoria: 3 subidas → estallido** (ciclo repetido en el histórico).
   - Ciclos previos: 6.7 → 13.0 → estallido; 6.1 → 16.1 → estallido; ciclo actual: 2.6 → 8.3 → 12.3 → ?
   - Identificado pero **no activado** como gatillo.

4. **Estallido posterior de `k_goles_local_recibido`** desde 47.8 → 0.
   - Historial: el siguiente local mostraba goles en contra > 0.
   - Registrado pero no contado como convergencia.

5. **Ley 3: Europa League vs Roma en 4 días.**
   - Se eligió la lectura A (*"alimentación"*) sin verificar que las K tenían gatillo activo.
   - Con el gatillo activo, la lectura B (*"vulnerabilidad"*) era la correcta.

6. **Victoria de Verona estimada en 0%.**
   - A pesar de: 4 factores de riesgo en Bologna + rebote de `k_goles_visita_anotado` en Verona + retorno de Orban.

### Errores raíz

- Violación de Ley 9 como **sesgo rector**: todo el análisis se construyó sobre *"rival débil"*.
- Convergencia exigida como *"múltiples K en techo"* cuando el criterio correcto es *"múltiples señales de la misma K"*.
- Auditoría 1 filtrada usando la identidad del rival.
- Ley 3 aplicada unidireccionalmente.

### Correcciones implementadas en v3.1

1. **Ley 9 reforzada:** el nivel del rival **nunca** desactiva un gatillo K propio.
2. **Convergencia redefinida:** 2+ señales direccionales (misma K o distintas).
3. **Ley 3 obligatoriamente bidireccional** (presentar ambas lecturas).
4. **Auditoría 1 blindada** contra el filtro por rival.
5. **Patrón de trayectoria "N subidas → estallido"** como gatillo independiente.
6. **Estallido posterior de `k_goles_recibido`** como gatillo de goles en contra esperados.
7. **Cumplimiento de mínimo del underdog** (5% / 10% / 15% según factores de riesgo).
