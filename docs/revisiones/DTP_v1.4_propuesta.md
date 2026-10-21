# Propuesta de revisión · `diagnostico-tactico` v1.3 → v1.4

**Estado:** PROPUESTA, no aplicada. El skill vive en la cuenta del usuario;
esto es el texto para decidir. Redactada el 21/10/2026 desde el dossier
(`GET /analisis/cowork/revision/diagnostico-tactico`, cohorte `c3-2026-09-23`).
Partimos de la v1.3 vigente (13/09), traída de la cuenta a
`docs/skills/diagnostico-tactico/SKILL.md`.

## De dónde sale

- 57 casos ciegos PRE y 503 lecciones acreditables. **Ninguna pide mover un
  número**: la revisión fija la rúbrica.
- Se leyeron los fallos y parciales de los cinco grupos más cargados:
  - MECANISMO-ABIERTO: 43.
  - Vías de gol de M2: 56.
  - Duelos por carril: 24.
  - Checklist del bloque: 65.
  - Once probable de nivel C: 44.
- **Sesgo de atribución:** como en el TDE, muchos «fallos» del lado son el
  1X2 con la vía del DTP **cumplida** en la misma lección. Ejemplos: Cúcuta,
  Toluca, Medellín, São Paulo y Carabobo. El DTP acierta más de lo que dicen
  sus conteos de fallos.

## Lo que esta capa acierta (y no hay que tocar)

- **Las vías de gol:** en decenas de cierres, la vía escrita fue literalmente
  la del gol (Rayo, Barcelona SC, Inter Bogotá, Marseille, Alavés).
- **El improvisado de vida útil 55-65:** confirmado en Aurora, Le Havre,
  Fiorentina y Emelec.
- **La clase `estructural no probado` (pregunta 6):** no suprimir la alerta se
  sostuvo en Betis y en Paris FC.

## Los seis cambios propuestos

### 1. MECANISMO-ABIERTO: la frecuencia sin mecánica tiene clase propia

**Casos:** Puerto Cabello (dos goles en cinco minutos), La Guaira, Alianza
Atlético (dos autogoles), Atlético Tucumán, Torque, Delfín, Betis–Barcelona y
Monza–Cagliari. En unos diez cierres hubo **≥ 2 goles en el mismo partido
pero la fuente no da la jugada**. Cada analista lo resolvió distinto: «no se
activa», «candidato», «se declara para la fecha siguiente».

**Propuesta:** la clase **`MECANISMO-ABIERTO · sin mecánica`**. Se activa con
la frecuencia (≥ 2 goles en ≤ 15 minutos o sin corrección en vivo) cuando no
hay fuente que nombre la jugada. Entra a M2 del próximo rival como **vía a
verificar** con nivel de dato C, nunca como vía declarada. No degrada K.

### 2. El mecanismo se nombra por la zona o el rol, no por el intérprete

**Casos:**
- Porto: el carril del lateral izquierdo dio el gol con OTRO lateral; la
  línea no repitió el 80 % y el carril siguió siendo la vía.
- Wanderers: «el mecanismo es la marca del segundo palo, no la pelota
  parada».
- León: los tres goles de córner fueron de intérpretes distintos.
- Barcelona SC: «la vía se sostiene por el pasador, no por el rematador».

**Propuesta:** el paso 2 del procedimiento (si la línea repite ≥ 80 %) se
lee **por zona**. Si el mecanismo es de carril o de zona (segundo palo,
espalda del lateral, salida bajo presión), sigue abierto aunque cambie el
intérprete, mientras el rol se repita. El 80 % de intérpretes vale solo para
los mecanismos de pareja (dos centrales, el doble pivote). **El contraste:**
cuando cambian el DT o la mitad de la línea, el mecanismo no viaja
(Corinthians, Newcastle).

### 3. El duelo por carril se escribe en las dos direcciones

**Casos:**
- Guaraní: el carril que cargó para atacar fue por donde le marcaron.
- Lille–Brest: el lateral que sube fue el que hizo el penal.
- Fluminense–Palmeiras: atacó Piquerez, el de la espalda «a favor».
- Gladbach–Hoffenheim y Shakhtar–AEK: «el carril donde el lateral rival sube
  es de doble filo».

**Propuesta:** todo mismatch de carril declara **las dos caras**: lo que gana
el que ataca y lo que expone si pierde la pelota. Se resuelve con el seguro
de atrás (rest defense). Un mismatch «a favor» sin su cara de vuelta está
incompleto.

### 4. Vías de gol: lo aéreo, el banco, el penal y los centrales que llegan

**Casos:**
- Centro y pelota parada: Torque, Guabirá, Juventus–Lazio y Estudiantes–San
  Lorenzo (el central rival llegó solo al área).
- Banco que entra a centrar o a correr: Alavés, Villarreal y Central Córdoba.
- Penal y ejecutor de penales: Monagas, Barracas y Mushuc.

**Propuesta, cuatro líneas obligatorias en M2:**
- La vía aérea se declara **por centro en juego abierto Y por pelota
  parada**.
- El duelo aéreo cuenta a **todos los que atacan el área**, centrales
  incluidos.
- **El banco del que persigue es vía:** centradores o velocistas frescos.
- **El ejecutor de penales del rival se nombra.** Es la misma lógica que el
  TDE ya aplica en v0.1.14.

El umbral de ≥ 2 errores para la vía del arquero **se mantiene**. Atlético
es el contraejemplo: un arquero suplente no es vía por serlo. Queda como
candidato el «arquero sin dueño», con ≥ 3 arqueros en la temporada
(Estudiantes de Río Cuarto, un caso).

### 5. Checklist del bloque: la pregunta 6 y la 4, más precisas

**Casos de la pregunta 6:** en ~15 cierres, el propio partido fue «el caso
nombrado que le faltaba a la 6»: Lazio, Lorient, Portuguesa, Once Caldas,
Cúcuta y Getafe. Pero hubo dos falsos «probados»:
- Villarreal: el caso era de local y de otra competición; concedió cuatro
  fuera.
- Manta: el caso era un 0-0, y no sostuvo una ventaja ni once minutos.

Varios bloques sostuvieron **con uno menos**: Atlético, Getafe y América.

**Propuesta para la pregunta 6:**
- (a) El caso cuenta si se sostuvo **una ventaja o un empate contra un rival
  obligado, en sede y competición comparables**. Un 0-0 sin ventaja que
  cuidar prueba menos.
- (b) **Sostener con inferioridad numérica cuenta** como caso.
- (c) El cierre de cada DTP **escribe el caso de la 6** cuando el partido lo
  da, y la apertura siguiente lo lee de la cadena. Hoy se descubre a mano en
  cada cierre.

**Propuesta para la pregunta 4:** el refresco se mide por **lo que el DT
cambió de verdad en los últimos partidos**, no por el conteo de lesionados.
Casos: Alianza Valledupar hizo cinco cambios en todas las líneas; Pereira
también es de la 4, por segunda vez. El costo de **rearmar la línea en un
doble cambio** (Sarmiento, dos fechas seguidas) queda como candidato.

**Además:** el improvisado puede romperse **antes** del 55 si el rival
ataca su debilidad desde el arranque (Parma, Angers, Fiorentina). La vida
útil 55-65 es el techo, no el piso.

### 6. Con el once en nivel C, M2 separa lo que depende del intérprete

**Casos:** en ~15 cierres, DTP-REHACER sonó y el mapa de duelos describía
«otro equipo»: Inter Bogotá, Nacional, Sarmiento, Leones, Gladbach,
Hoffenheim, Málaga y Peñarol. Lo que **sí** sobrevivió al once rotado fueron
los **carriles y los mecanismos**: Rayo («el mapa acertó el carril aun con el
XI de referencia rotado en tres nombres») y Liverpool en LASK.

**Propuesta:** sin el once oficial, M2 se escribe en dos capas:
- **(i) Lo estructural:** carril, zona y mecanismo. Vale con nivel C.
- **(ii) El duelo con nombre propio:** se marca **condicional al once**.

Con DTP-REHACER encendido y sin rehacer antes del pitazo, el cierre lee la
capa (ii) como **apertura caída**, no como fallo del mecanismo. La capa (i)
se juzga igual. Un M2 sobre un XI escrito solo como frase (Portuguesa, Rayo
Zuliano) no se puede comprobar: el XI de referencia va como lista.

## Lo que NO se propone

- Ningún número: ni la vida útil, ni el umbral del 80 % para las parejas, ni
  el ≥ 2 del arquero.
- La clase del bloque no cubre el error en la salida bajo presión. Cagliari
  concedió cuatro siendo estructural y probado. Se declara como hueco: es
  vía de gol (M2), no clase de bloque.

## Cómo se aplica si se aprueba

Igual que el TDE:
1. El usuario aprueba o corrige.
2. Se redacta la v1.4 en `docs/skills/diagnostico-tactico/SKILL.md`.
3. Si un campo nuevo lo necesita, se le da sitio en el parte: la clase «sin
   mecánica», las dos caras del carril y el caso de la pregunta 6 en la
   cadena.
4. Se entrega el `.zip` para subir a la cuenta.
5. Se marcan como aplicadas las lecciones correspondientes, con 🔑.
