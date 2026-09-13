# Plantilla de caso

Dos bloques. El primero se llena **antes** del partido; el segundo **después**. Nunca al mismo tiempo, salvo que el caso se marque `RETRO`.

---

## A — DECLARACIÓN (pre-partido)

```
id             TDE-0XX
modo           DECLARADO | RETRO
modo_evaluacion  PRE | COND      (solo PRE acredita validacion predictiva)
estado_marcador  (obligatorio si modo_evaluacion = COND, ej. 2-1 a favor desde el 65)
fecha          YYYY-MM-DD
torneo         (Liga 1 Clausura 2026, Copa Libertadores fase de grupos, etc.)
jornada        F4
equipo         (equipo evaluado)
rival          (rival)
condicion      L | V
estadio        (nombre, altitud si es relevante)
nivel_dato     A | B | C

Bloque F (×3)   score 0-1     F1 __ F2 __ F3 __ F4 __
Bloque C (×2)   score 0-1     C1 __ C2 __ C3 __
Bloque P (×2)   score 0-1     P1a __ P1b __ P1c __ P2 __ P3 __ P4 __
Bloque S (×1.5) score 0-1     S1 __ S2 __ S3 __ | n/a

compuertas_operadas
  [ ] 1 - P1a = 0, bloque P topeado en 0.5
  [ ] 2 - C1 <= 0.5, S2 topeado en 0.5
  [ ] 3 - P4 desdoblado (indicar si 1 o 0.5 y por que)
  [ ] n/a de S3 (equipo sin presion alta por diseño)
  (declarar tambien las que se evaluaron y NO se activaron)

fuente_de_P1a   mu_partido (modo PRE) | ventaja obtenida (modo COND) | cualitativo declarado
  PROHIBIDO usar el gap o el gap diferencial como input de P1a
  si se uso Regresion al Nivel: mu propio __ · mu rival __ · margen corregido por localia __
  si NO hay salida del motor: declararlo en el output y puntuar cualitativo
  snapshot contaminado post-partido?  si | no   (verificar si la forma de los ultimos 5 incluye este partido)
  bandera VENTAJA-INESPERADA?  si | no   (ventaja obtenida por el equipo de mu mas bajo por mas de 0.30
                                          - agravante declarado de P(fractura|echada), sin coeficiente)

dias_descanso y dureza del proximo rival  → del motor si existe, nunca a ojo (regla de procedencia de F2)

IE             __ / 10
P(echada)              __ %
P(fractura|echada)     __ %
P(gol|fractura)        __ %
riesgo_compuesto       __ %
banda_5_7_activa       si | no    (si es si, declarar la advertencia en el output)

VIA 2 — sobreexposicion            SOB1 __ SOB2 __ SOB3 __
ISE                    __ / 10
P(sobreexposicion)             __ %
P(gol|sobreexposicion)         __ %
  interaccion entre vias declarada:  el rival va ganando y administra?  si | no
  (si es si, la sobreexposicion propia queda sin castigo - declarar y NO aplicar coeficiente)
riesgo_via_2                   __ %

riesgo_tramo_final     __ %   (el MAXIMO de las dos vias, no la suma)

tipo_modal     ECHADA-VOL | ECHADA-FIS | ECHADA-SUP | ECHADA-PSI | ECHADA-NUM | SOB
ventana_modal  0-15 | 15-30 | 30-45 | 45-60 | 60-75 | 75-90
perfil_ventanas  [__, __, __, __, __, __]

dos_indicadores_dominantes
  1. (código y por qué)
  2. (código y por qué)

contramedida_esperada  (la del tipo modal, según TIPOLOGIA.md)
que_falsaria_el_pronostico  (escribir la observación concreta que dejaría el IE en evidencia)
```

El campo `que_falsaria_el_pronostico` es obligatorio. Un pronóstico que no se puede falsar no se puede calibrar. **Desde v0.1.3 hay que escribir un falsador por vía**: uno para el IE y uno para el ISE. Un falsador único no distingue cuál de los dos índices falló.

El bloque `VIA 2` es obligatorio incluso cuando el IE es bajo. Un IE bajo sin ISE declarado es un caso incompleto y no entra al cómputo de `cobertura de vía` de `CALIBRACION.md`.

**Regla de redacción del falsador** *(v0.1.1)*: escribirlo como condición **observable pura**. Prohibido incluir cláusulas de estado del marcador que puedan invertirse ("sin ir ganando", "si va perdiendo"), porque el evento real puede cumplir el mecanismo y no la cláusula, y entonces la alarma no suena. Formato correcto: *"si el equipo retrocede antes del minuto 60, el IE está subvalorado"*. Formato incorrecto: *"si retrocede antes del 60 sin ir ganando"*.

---

## B — CIERRE (post-partido)

```
se_echo        si | no | parcial
se_expuso      si | no | parcial
firma_bloque_sostenido  si | no | parcial   (las tres señales de DETECCION_DATOS)
minuto_real    __      (minuto donde la transición se volvió observable)
tipo_real      (el mecanismo que efectivamente operó; puede ser más de uno, ordenar por peso)
se_partio      si | no
gol_en_echada  si | no
gol_en_sobreexposicion  si | no
minuto_gol     __
resultado      X-Y
nivel_dato_post  A | B | C
proxies_usados   (cuáles: minutos de cambio, faltas por zona, córners por franja, etc.)

evaluacion
  banda_acertada       si | no
  ventana_error        __ ventanas de diferencia
  tipo_acertado        si | no
  fractura_acertada    si | no | no aplica

leccion    (qué entra al ajuste: rúbrica de un indicador, peso de un bloque, o nada)
```

**Regla de la lección**: la mayoría de los cierres deben terminar en "nada". Si cada caso genera un cambio de pesos, el módulo está sobreajustando al último partido — exactamente el sesgo que la v2.0 de la Matriz de Escenarios corrigió para la goleada.
