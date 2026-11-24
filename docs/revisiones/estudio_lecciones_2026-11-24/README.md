# Estudio de las lecciones pendientes — 24/11/2026 (paso 1 de la revisión)

> **Estado: DIAGNÓSTICO. No se modificó ningún skill.** Base: las lecciones
> `pendiente` de `GET /analisis/cowork/lecciones` (cohorte vigente
> c3-2026-09-23) bajadas el 24/11/2026 a las 11:05 UTC; partidos del 17 al
> 23/11, posteriores a la subida de TDE v0.1.27, DTP v1.9 y EFE v1.11 (17/11,
> 13:20 UTC; las pocas del propio 17/11 que pueden haber corrido con la
> anterior están marcadas en cada estudio). Población ciega PRE.
> **sad-analysis queda fuera**: subió a v4.7 y v4.8 el 21/11 y sus 121
> lecciones son de 3-4 días; lo que tiene pendiente (el ciego en el skill, las
> reglas de anclaje) espera a 60 cerrados con ciego (DEUDA 42).

Mismo método que el estudio del 17/11: cada lección se leyó entera y se
clasificó por su prosa, no por el veredicto del lado ni por la etiqueta de Jev.
Clases: `regla_sostuvo`, `mal_aplicada`, `regla_fallo`, `insumo`, `imprevisto`,
`otro_skill`, `no_dice`. Clasificación por lección en `clasif_<skill>.json`;
el detalle, en `estudio_<skill>[.parteN].md` (el TDE y el DTP se leyeron en
dos tramos por fecha: parte 1 del 17 al 21/11, parte 2 del 21 al 23/11).

## 1. Por clase

| Skill | Lecciones | Partidos | sostuvo | mal aplicada | regla falló | insumo | imprevisto | no dice | otro skill |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| TDE v0.1.27 | 468 | 135 | 349 (75 %) | 57 | 32 | 5 | 4 | 20 | 1 |
| DTP v1.9 | 537 | 137 | 297 (55 %) | 140 | 73 | 16 | 2 | 9 | 0 |
| EFE v1.11 | 226 | 132 | 138 (61 %) | 43 | 19 | 4 | 1 | 18 | 3 |

Sin copa nacional (TDE 57, DTP 49, EFE 26 lecciones fuera):
TDE 307 / 50 / 28 / 2 / 4 / 19 / 1 · DTP 275 / 128 / 70 / 9 / 2 / 4 / 0 ·
EFE 122 / 35 / 18 / 3 / 1 / 18 / 3.

Contra el 17/11 las proporciones casi no cambian (TDE 72 → 75 % sostuvo, DTP
54 → 55 %, EFE 65 → 61 %). Lo que más se repite sigue siendo **no cumplir una
regla ya escrita**: en el DTP hay 1,9 mal aplicadas por cada regla que falla.

## 2. Los arreglos de la app del 17/11: funcionaron

- **`bancoProbable`**: TDE disciplina 66, de 22 errores de banco a 10 en 135
  partidos (lo que queda es el rehacer que no reescribe la línea de banco del
  rival en las ramas, o el `porqueDesenlace`); EFE B5 se sostuvo 10 de 11 antes
  del once; DTP de 16 a 3 en la parte 1 y 13 en la parte 2, ya no por la lista
  (donde se copió entera, el banco marcó) sino por escribirlo «desde el 60'» o
  nombrar como banco a un titular cuando el once llegó tarde.
- **El rehacer con el once oficial**: el grid sin copiar bajó de 8 a 6, las
  filas F1 que faltaban casi desaparecieron, la posesión fuera de condición
  bajó de 12 a 10 y la `siExpulsion` incompleta del TDE de 4 a 1.
- **El incumplimiento se movió al resto del rehacer**: EFE, 14 mal aplicadas en
  13 partidos (B y F sin recomputar, B5 con titulares de la hoja, rehacer de un
  solo lado) **con FUERA-EN-LA-HOJA y EFE-RECOMPUTO-PENDIENTE sonando**: son
  avisos `tipo: dato` y el depósito entra igual.
- **El homónimo (21/11, 22:50)**: ninguna lección muestra ese error; no se puede
  juzgar todavía.

## 3. Incidencias de la app que salieron del estudio

1. **Jev dejó de etiquetar el modo de fallo desde el 21/11.** En los lados con
   fallo de orden 1: 1 de 42 etiquetado el 21/11, 0 de 39 el 22/11, 0 de 2 el
   23/11 (antes, la mitad o más). Verificar la clave y el disparo de
   `backend/analisis/modo_fallo.py` en producción. Además, donde sí etiquetó, 5
   de 14 `lectura` del TDE eran lecciones donde la regla se sostuvo.
2. **El grid corregido después del pitazo** (DTP, 18 lecciones en 16 partidos):
   la API corrige el grid cuando el partido ya empezó y ningún rehacer llega.
   Es insumo, no regla; que el veredicto lo distinga.
3. **Identidad**: Djené / «D. Dakonam» (Getafe 1570456) no se casaron →
   `backend/identidad.py` con su test.
4. **Lecciones del DTP sin DTP depositado**: Olimpia 1632065:a:5 y Libertad
   1632067:b:3. Tres lecciones del EFE son de otro skill (Maldonado, Ameliano,
   Millonarios).

## 4. Lo que tiene material (≥ 3 partidos)

### Transversal — para la app antes que para el texto

Repetir la regla en el skill no cambió la conducta las dos veces anteriores; lo
que movió la aguja fue darle el dato a la corrida (`bancoProbable`). Mismo
camino para:

- **Que el recibo frene** el depósito rehecho con EFE-RECOMPUTO-PENDIENTE o
  FUERA-EN-LA-HOJA sonando (EFE, 13 partidos), y el veredicto con condición
  que no publica la línea menos favorable (DTP, 8).
- **Datos por sede con su `n`**: córners que concede el rival (pelota parada
  del DTP, 9 + 3 mal aplicadas pese a la regla nueva de la v1.9); la referencia
  de volumen (7 de 7 mal aplicadas); el perfil de posesión del rival con sede y
  DT (7 de 7).
- **La línea del choque con sus amarillas** (TDE S1, 7 partidos nombraron
  candidatos y no la línea; DTP vía de expulsión, 11 mal aplicadas; en
  Audax 1505563 el TDE del mismo parte ya tenía las amarillas del central).
- **`parejasNuevas` sobre el once oficial** (EFE EJE-DEBUTANTE, 4 partidos).
- **Un campo `gatillo` / `seExponeSi` en la SOB1** del TDE (disciplina 18, nueva
  en la v0.1.27: 10 partidos sin condicionarla al régimen).
- Aviso cuando el banco ofensivo lleva un minuto fijo; campo de quién queda
  atrás por rama (DTP M3, 10 partidos).

### TDE v0.1.28 (texto)

- **La vía del empate en la rama de ventaja** (disciplina 66): 7 `regla_fallo`
  en 6 partidos más Querétaro 1551046: el empate llegó por titulares de la vía
  principal del rival, no por «banco + pelota parada». El matiz C6 pasa de 2 a
  6+ casos → la nota copia las vías del DTP rival por renglón.
- **44 (b)**: 8 tipologías de ventaja sin motivo nombrable o elegidas por C3 o
  por un antecedente que no coincide (sube desde 4) → aclarar «C3 no elige la
  tipología»; para la app, un `motivoTipologia` de lista cerrada.
- **Pieza del seguro relevada por otra del mismo rol** (63, 5 partidos): la rama
  nombra al heredero.
- **RELEVANCIA BAJA**: la premisa falló en 3 partidos que llegaron 0-0 más allá
  del 60' → aclarar que la alerta dice «lean las ramas»; medir la premisa.
- Se sostienen enteras: disciplina 61 (77 de 77), el `abierto` de la 65 (17 de
  17), `ventajaPorFuerza` (39 de 40), la superioridad «no administra» (11 de 11).

### DTP v1.10 (texto)

- **M5 es la única regla que falla en volumen**: 50 `regla_fallo` de 119
  lecciones (el resto se sostiene). 26 son NEUTRO que el volumen resolvió (la
  banda de «parejo», a medir: es un número), 12 FAVORABLE de más (sube desde
  ~6; en 5 el lado acertó por conversión) → aclaración sin número: el
  FAVORABLE apoyado en el nivel o en la contra escribe cuánto le concede al débil.
- **«Si la condición no depende del foco, manda la línea menos favorable»**:
  partida (3 mal aplicadas, 4 falló) → aclarar que si el parte sostiene la
  condición con un hecho nombrado (TDE, conducta repetida del DT), manda la
  condición.
- **Renglón 6 de `viasGol`**: el que llega no sale del renglón por figurar como
  centrador o asistidor en otro (4 partidos).
- **El reconvertido también ataca** (regla de la v1.9): 4 de 4 mal aplicadas y
  en las cuatro atacó; la regla se confirma, falta que se cumpla.
- **Candidatos que llegan al umbral**: el rearme del medio / del doble pivote
  (4-5 casos), el segundo de la lista de penales recibe la falta (4), el caso de
  la pregunta 6 viaja con el arquero (2 + anteriores).
- Se sostienen: MECANISMO-ABIERTO (28 de 29), penales con la base corta (sin
  ninguna mal aplicada), pregunta 6 y vida útil.

### EFE v1.12 (texto)

- **EJE-DEBUTANTE anuncia volumen concedido, no la vía** (19 sostuvo, 11 no
  dice): la rúbrica se contradice en el mismo párrafo («baja como vía de gol» /
  «no es vía de gol por sí sola») → alinear. Sin once, la condicional va sobre
  la línea, no sobre una pareja.
- **F3 por ataque o medio con la segunda línea o el banco enteros** (5
  `regla_fallo`: Corinthians, Dortmund, Galatasaray, Olympiakos, Tottenham): la
  cláusula «cubierta de oficio» se extiende ahí; no a la defensa.
- **C4 leído fuera de la condición del patrón** (4 `regla_fallo`): aclarar.
- **Arco alternado o sin dueño** (5 partidos): la caja nombra a todos los
  arqueros convocables; la app los carga en F1 y en el banco probable.
- **Rama «once alternativo»**: 13 de 17 sostuvo; sumar «campeón consagrado»
  como hecho que la abre; «prevé» en la previa no es un hecho.

### Candidatos a medir (números: sin backtest no entran)

Banda de «parejo» del M5 · ×1,5 de F2c y GK-DOWNGRADE · COLAPSO + AGRAVANTE
(quinto caso, Angers 1552825) · umbral de B5 🔶 (tercer caso, Le Mans
1552822) · TDE: defecto por quien persigue (14 a favor, 1 en contra), doble
golpe (8 partidos), superioridad ganando (cargan 11 de 11), roja propia ganando
(contradictoria), obligados que no se expusieron (C1), el favorito que se
aparta de «sigue atacando» con motivo (4 a 3).

## 5. Decisiones para el usuario

1. **Jev**: arreglar la etiqueta caída desde el 21/11 antes de la próxima
   revisión (incidencia 3.1).
2. **El recibo que frena**: pasar EFE-RECOMPUTO-PENDIENTE y FUERA-EN-LA-HOJA de
   aviso a bloqueo del depósito rehecho, y los datos por sede (córners, volumen,
   posesión) y la línea con amarillas al parte. Es la misma lección del 17/11:
   lo que funcionó fue el dato, no el texto.
3. **Paso 2**: redactar TDE v0.1.28, DTP v1.10 y EFE v1.12 con lo del §4. Son en
   su mayoría aclaraciones; ningún número se mueve sin backtest.
