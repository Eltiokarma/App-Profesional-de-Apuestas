# Propuesta de revisión · `efe-clasificador` v1.7 → v1.8

**Estado:** PROPUESTA, para aprobar por el usuario. Redactada el 28/10/2026
desde las **179 lecciones pendientes** del skill, todas de partes escritos con
la v1.7 (del 25 al 27/10) y todas ciegas PRE. La base es la v1.7 vigente
(`docs/skills/efe-clasificador/`, `references/rubrica-efe-v1.7.md`).

## De dónde sale

- **179 lecciones:** 92 aciertos, 36 parciales y 51 fallos.
- **Ninguna pide mover un número.** Jev no marcó ninguna con
  `proponeMoverNumero`. Esta versión no toca pesos, máximos ni cortes de la
  tabla de puntuación. Los únicos umbrales que se mencionan ya existen en la
  rúbrica y se reusan (cambio 2).
- **Sesgo de atribución, como en las anteriores.** Muchos «fallos» del lado
  son del 1X2, con la regla del EFE confirmada en la misma lección. El caso
  más claro es la regla de la brecha: casi todas sus lecciones dicen
  «declarada y cumplida» aunque el lado salga como fallo.

## Lo que la v1.7 acertó y no hay que tocar

- **La brecha no se lee con T.54, R-KT.2 o ESCALA-LIGAS (cambio 5 de la
  v1.7).** Se confirmó unas 20 veces: Cúcuta (18 puntos de brecha, ganó el de
  37 %), América–Pachuca (36 puntos, ganó el de menor porcentaje), Tolima–
  Pasto (30 puntos), La Calera–U. Católica (49 puntos), Pumas–Tigres,
  Toulouse–Troyes, Bolívar–Vinto, Coritiba–Gremio y otros. Desde el 26/10 la
  app la calcula (`EFE-EMPATE-TECNICO`), así que se dejó de incumplir por
  olvido.
- **EJE-DEBUTANTE con la pareja de un partido (cambio 6).** Once lecciones,
  casi todas «amplió el rango sin fijar el marcador»: Pachuca (un solo gol con
  21 remates en contra), Llaneros (penal y roja de la pareja nueva), Tigres
  (2,27 xG en contra y un gol). Condicionarla al once oficial también se
  confirmó (Águilas: volvió Ontaneda y no recibió).
- **La semántica del D3 (cambio 3).** Diez lecciones: 🔶 es «reacciona sin
  sostener» (Roma–Cagliari: del 1-2 al 2-2 y después dos goles en dos
  minutos; Fortaleza: empata y no gana; Puebla: responde y pierde).
- **T.54 descuenta lo heredado y la serie corta amplía el rango (cambio 7).**
  La Guaira (el interino remontó), Bucaramanga (primer dato de D3 con
  Peirano), Rio Ave (el DT nuevo invicto no sostuvo un E en 0).
- **FACTOR-X amplía el rango** (Santos con Neymar expulsado) y **COLAPSO EN
  CASCADA no predice goleada** (cuatro casos).
- **La jerarquía de fuentes del F1 (cambio 2)**, cuando se aplicó: Gouiri
  (fuente sin fecha → duda, fue titular y asistió) y Brobbey (frase del DT +
  API «Questionable» → duda, fue titular).

## Los cinco cambios propuestos

### 1. T.54 se revisa en los DOS lados, con la fecha del DT, y la app avisa si falta

**Lo medido.** La regla de la brecha depende de que T.54 esté declarada. Los
fallos que quedan son partes que no la declararon donde correspondía:

- **Angers–Lorient:** los dos DT habían llegado en junio (≈ 4,5 meses) y T.54
  se declaró solo para Angers. Con T.54 en los dos lados, el 44 contra 68 era
  empate técnico; salió 0-0.
- **Comerciantes–Cienciano:** el DT asumió cuatro días antes del partido y el
  parte puntuó el bloque A sobre el cesado.
- **Rio Ave–Famalicão:** el bloque A en ❌ por interino no predijo el
  rendimiento, porque el sistema (D1) se heredó intacto. T.54-B no se
  evaluó.

**Propuesta:**

1. **T.54 se revisa siempre en los dos equipos**, con la fecha de llegada del
   DT escrita en el bloque A (`dt.desde` del parte). Un DT de menos de 6 meses
   es T.54 o T.54-B; no se deja en blanco.
2. **Un DT oficializado en los 7 días previos se puntúa como banco que
   dirige** (regla 3 de T.54, ya vigente) aunque la prensa de la semana sea
   escasa. Desde el 27/10 la app avisa `DT-VS-BANCO` cuando el once oficial
   sienta a otro DT que el del parte.
3. **App (si se aprueba):** el parte calcula la alerta de dato
   **`T.54-SIN-DECLARAR`** cuando `dt.desde` de un lado tiene menos de 6
   meses y el parte no trae T.54 ni T.54-B en ese lado. `EFE-EMPATE-TECNICO`
   la cuenta igual que una T.54 declarada. No toca ningún porcentaje: el
   umbral de 6 meses es el que ya define T.54.

### 2. El arquero: suplente con rodaje, y el arco sin dueño

**Lo medido:**

- **Suplente con historial en la categoría:**
  - Barcelona–Real Madrid: zona GK en rojo (reducción 86 % con el ×1,5) y
    Lunin, con recorrido en LaLiga, atajó cinco de seis.
  - Palestino–Colo Colo: F3 por zona GK y Vózinha, con minutos recientes, fue
    la figura (5 atajadas).
  - Toulouse–Troyes: el arquero titular cambió con el once oficial y el
    suplente sostuvo la valla.
- **Arco sin dueño:**
  - Leones del Norte: el EFE dudó entre dos arqueros y atajó un tercero, con
    7 atajadas.
  - Barracas–Estudiantes de Río Cuarto: el «cuarto arquero de la temporada»
    se leyó como vulnerabilidad e hizo 10 atajadas.

**Propuesta (sin tocar el ×1,5 ni el cálculo del IP):**

1. **La F3 por zona GK no se activa sola** si el suplente que ataja tiene
   ≥ 15 partidos en la categoría o titularidades en los últimos 12 meses. Es
   el mismo umbral que ya separa B6 🔶 de B6 ❌. La zona se describe
   «cubierta» (cambio 1.3 de la v1.7), y el riesgo del arco amplía el rango,
   no baja el centro.
2. **«Arco sin dueño»:** con dos o más arqueros alternándose sin motivo
   publicado, B6 abre la caja de sensibilidad con **los tres escenarios**
   (titular A, titular B, otro), no apuesta por uno. La rotación de
   arqueros, sola, no se lee como vulnerabilidad: se necesita la frecuencia
   de errores observada (GK-FALLA-ACTIVA).

### 3. La zona del ausente sale de su rol en el sistema, y el medio dice si el eje está entero

**Lo medido:**

- **Lecce–Juventus:** la F3 del medio (reducción 43,8 %) contaba como
  ausencias del medio a carrileros y rotación (Çelik, N. González, Locatelli).
  El eje que jugó, Douglas Luiz y McKennie, hizo los dos goles.
- **Atlético Torque–Cerro:** la F3 salió por ATK al 100 % con un solo ausente
  de rotación, y el gol fue del volante generador.
- **Coritiba–Gremio y Monterrey–Chivas:** la reducción DEF con zaga rearmada
  no se tradujo en goles con el equipo defendiendo en bloque bajo y el
  arquero titular de nivel (B6 ✅).

**Propuesta:**

1. **La zona del ausente se asigna por su rol en el sistema del once** (el
   grid, como ya pide la v1.7 para EJE-DEBUTANTE), no por la posición de la
   plantilla. Un carrilero de línea de cinco es DEF; uno de línea de cuatro
   con rol de volante es MID.
2. **La F3 del medio dice si el eje (pivotes e interiores) está entero.** Una
   reducción de MID hecha con ausencias de banda o de rotación se escribe
   «MID reducido, eje entero» y no se lee como el medio roto.
3. **Matiz que no cambia la regla:** la reducción DEF se paga en la vía del
   rival (penal, pelota parada, segundo palo) más que en el volumen. La
   Guaira concedió dos penales y ningún gol en juego abierto. La vía es lo
   que baja al DTP.

### 4. Las fuentes del F1 tienen fecha

**Lo medido.** La jerarquía de la v1.7 se aplicó, pero sin mirar la fecha:

- **La Calera–U. Católica:** las dudas venían de partes de hace un mes
  (Ampuero, Mena: titular y suplente), y la baja real (C. Cuevas, sin parte)
  no se vio.
- **Aldosivi–Belgrano:** una baja por lesión fechada 8 días antes, que la
  previa de la víspera contradecía, se declaró baja. El riesgo del arco se
  armó sobre el suplente y jugó el titular.
- **Pumas–Tigres:** L. Herrera se sacó de la tabla F1 por una «rescisión» de
  un agregador y estuvo en el banco oficial.

**Propuesta:**

1. **Dentro del mismo nivel de la jerarquía manda la fuente más reciente.**
   Una baja de más de 7 días que la previa de la víspera contradice es
   **⚠️ Duda**.
2. **Una salida del club (rescisión, traspaso, cesión) que el club no
   confirmó no saca al jugador de la tabla F1:** va como Duda.
3. **Sin parte de la semana, se dice** («estado F1 con fuentes de más de 7
   días») en la caja de sensibilidad.

### 5. La caja de sensibilidad baja al partido: rama del matchup y confianza

**Lo medido:**

- **Nacional–Braga:** la sensibilidad escribió «el interino cambia a línea de
  cinco por saber sufrir» (declaración pública del DT) y fue exactamente el
  partido. Quedó como nota y el matchup H no la usó.
- **Barcelona–Real Madrid:** la sensibilidad decía «si Espart no llega, la
  zona DEF se vuelve crítica»; pasó al 30' y el gol decisivo entró por ahí.
  El 86 % no bajó su confianza.
- **Cúcuta:** «si Berdugo no es titular, pierde al lanzador y la vía aérea»
  se cumplió: fuera de la hoja, 9 córners y 0,46 xG sin gol.

**Propuesta:**

1. **Un supuesto de la caja con una declaración pública del DT detrás** pasa
   al matchup H como **rama** («si juega con línea de cinco…»), no queda como
   nota.
2. **Si la sensibilidad apunta a una zona que se vuelve crítica** (DEF o GK)
   y el supuesto tiene base (duda real, sin recambio de oficio), la confianza
   del EFE se baja un escalón **antes** del 1X2, igual que con la F3.

## Matices que no son cambio (se escriben como nota)

- **Bloque E con racha de empates.** Colo Colo puntuó E3 ✅ (≤ 1 derrota en
  seis) con tres fechas de liga sin ganar, y empató de visita. E3 cuenta
  derrotas, y no se toca. Pero una racha de 3+ sin ganar en liga se dice en
  la lectura del E.
- **El bloque E dice qué se juega, no si compite** (Pasto: colista sin
  opciones, sostuvo un resultado de visita).
- **B5 con DT nuevo que rota titulares al banco** se lee como profundidad
  (La Calera: Ferreyra y Oyarzo entraron al descanso e hicieron dos goles y
  una asistencia).

## Lo que NO se propone

- **Ningún peso, máximo ni corte de clasificación.** Ninguna lección lo pide.
- **El ×1,5 del arquero.** Los casos de Lunin y Vózinha piden leerlo distinto
  (cambio 2), no moverlo.
- **E3 con empates.** Contar «sin ganar» en vez de derrotas cambia un
  criterio de puntuación. Con un caso (Colo Colo) queda como candidato.
- **COLAPSO + agravante → ruptura** sigue candidato, sin casos nuevos en
  esta tanda.

## Cómo se aplica si se aprueba

1. **Skill:** se redacta `references/rubrica-efe-v1.8.md` con el changelog y
   el `SKILL.md` pasa a v1.8. `efe-dashboard` no cambia, salvo la cita de la
   caja de sensibilidad (cambio 5).
2. **App:**
   - `lecciones.CORTE_VERSION["efe-clasificador"]` suma `("v1.8",
     "2026-10-28")`, para que «Cerrar las anteriores» cierre estas 179 en la
     v1.8.
   - Si se aprueba el cambio 1.3, la alerta `T.54-SIN-DECLARAR` en
     `parte.py` (tipo `dato`, desde `dt.desde`), contada por
     `EFE-EMPATE-TECNICO`, con su test.
3. **`docs/COWORK.md`:** el prompt suma dos líneas: T.54 en los dos lados con
   la fecha del DT, y la fecha de las fuentes del F1.
4. Zip para subir a la cuenta.
