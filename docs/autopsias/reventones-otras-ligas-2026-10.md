# Reventones fuera de Perú — primera tanda (13/10/2026)

Nueve estudios hacia atrás (modo `reventones` de `corrida-sad`) en seis ligas,
para ver si los patrones de las tres tandas de Perú
(`reventones-peru-2026-10.md`, 25 estudios) se sostienen. Población
`post_resultado`: fijan rúbrica, no mueven números. Sin el denominador de las
burbujas que no reventaron, nada de esto es probabilidad.

| Partido | Equipo · tipo | Mecanismo (secundario) | Riesgo · extremo | Señales previas |
|---|---|---|---|---|
| Brighton 3-0 Arsenal (19/09, Premier) | Arsenal · racha + (6) | superioridad del rival (balón parado) | MUY ALTO · cerca | Saliba fuera |
| Nottingham Forest 0-1 Coventry (19/09, Premier) | Coventry · racha − (5) | el rival se sobreexpuso (varianza) | bajo · RÉCORD | rival superior, DT nuevo del rival (5.º en un año), bajas · Coventry recién ascendido |
| Betis 1-0 Real Madrid (04/09, LaLiga) | Madrid · racha + (6) | arquero rival (balón parado) | bajo · cerca | DT nuevo (Mourinho), 7 bajas · 3 de 6 de la racha eran amistosos |
| Alavés 0-1 Valencia (15/09, LaLiga) | Valencia · racha − (4) | cambio de DT (interino a 48 h) | bajo · RÉCORD | DT nuevo, rival superior · 5 cambios en el once |
| Defensa y Justicia 1-1 Aldosivi (23/07, Argentina) | Defensa · racha − (6) | cambio de DT (balón parado) | MUY ALTO · RÉCORD | DT nuevo (la base tenía al saliente) |
| Palmeiras 1-2 Atlético-MG (26/07, Brasil) | Palmeiras · racha + (4) | error del arquero (sobreexposición) | MUY ALTO · — | 4 suspendidos, cambio de sistema forzado |
| Llaneros 2-0 Atlético Nacional (21/09, Colombia) | Nacional · racha + (6) | rotación (error del arquero suplente) | bajo · cerca | 8 cambios con el arco, 3.er partido en 8 días |
| Lazio 2-2 Milan (12/09, Serie A) | Lazio · racha + (9) | echada del que ganaba (racha de otra competición) | bajo · RÉCORD | DT nuevos los dos · 5 de 9 de la racha eran amistosos |
| Millwall 2-2 West Ham (19/09, Championship) | West Ham · racha + (4) | balón parado (saques largos) | bajo · RÉCORD | derbi · West Ham recién descendido |

## Lo que se sostiene

1. **El extremo es la alarma que más aparece.** 8 de 9 llegaban con la burbuja
   en su récord o cerca (en Perú, 18 de 25). En 6 de esos 8 el riesgo
   calculado decía BAJO. La regla de prudencia de REVENTON §10 se sostiene en
   seis ligas.
2. **El riesgo calibrado acierta cuando dice MUY ALTO** (Arsenal, Defensa,
   Palmeiras): los tres reventaron. Sin denominador no es tasa, pero ninguno
   de los MUY ALTO estudiados quedó en pie.
3. **El DT nuevo vuelve a ser protagonista**: 2 mecanismos `cambio_dt`
   (Valencia con interino, Defensa con Vaccari) y DT nuevo como señal en 6 de 9.

## Lo que NO se sostiene fuera de Perú

1. **`regresion_al_nivel` casi no aparece.** En Perú fue el mecanismo más
   frecuente de la tercera tanda; acá ninguno lo eligió como principal.
   Fuera de Perú los cortes tienen un hecho concreto: arquero, balón parado,
   rotación, DT. Hipótesis: en Perú la diferencia de nivel entre rivales de
   la misma liga es menor y las rachas cortas son más ruido.
2. **`racha_de_otra_competicion` cambia de cara**: en Perú era la Copa de la
   Liga; en Europa son **los amistosos de pretemporada**, que inflan la K y
   el récord (Lazio 5 de 9, Madrid 3 de 6). La alerta de extremo sonó en los
   dos, pero «inflada». Ver *decisión pendiente*.
3. **Balón parado y arquero** pesan más (6 de 9 entre principal y
   secundario). El arquero —propio o rival— no tiene casillero previo en
   ninguna capa: candidato GK-FALLA-ACTIVA (Palmeiras, segundo caso) y su
   espejo (Valles, Medina).

## Arreglado en el código con esta tanda

- **`once_distinto` daba falsos positivos** (Arsenal, Coventry): comparaba con
  el último partido de la racha, que era de copa con el once rotado. Ahora
  compara con el último de la MISMA competición.
- **Cambio de categoría** (West Ham descendido, Coventry ascendido): las
  medianas del reventón se aprendieron en la categoría vieja. Para West Ham
  casi todo rival del Championship queda «lejos» y el riesgo sale bajo por la
  escala; para Coventry el récord es casi mecánico. `escala.cambioDeCategoria`
  en la burbuja y `rival_de_otra_base` en el estudio lo dicen.
- **Copas y divisiones** (Cristal–Bentín en Perú): ver
  `backend/analisis/escala.py`.

## Decisión pendiente (del usuario)

- **¿Los amistosos cuentan en la burbuja?** Hoy el motor los procesa como
  cualquier partido; Lazio llegó a su récord de 9 con 5 amistosos. Sacarlos
  toca la matemática del motor (`docs/MOTOR_SAD_EXTRACCION.md`) y el backtest;
  marcar el extremo como «inflado» cuando la mitad o más de la racha es de
  otra competición no toca el motor pero sí el espejo TS y los vectores
  dorados.

## Datos de la base a revisar

- **Copas nacionales que faltan**: la EFL Cup de West Ham con Fulham (15/09)
  no está en la base; con ese partido la racha ya estaba cortada.
- **DT de la base**: Defensa y Justicia figuraba con Soso, que se fue el
  24/05 (Vaccari en el banco). La alineación rancia de la deuda 6, en
  Argentina.
- **Sede**: Coventry–Villa por copa figura de local en la base; la previa lo
  da en Villa Park.

# Segunda tanda fuera de Perú (14/10/2026) — 43 estudios en total

| Partido | Equipo · tipo | Mecanismo (secundario) | Riesgo · extremo | Lo nuevo |
|---|---|---|---|---|
| Eintracht 2-2 Freiburg (19/09, Bundesliga) | Freiburg · racha + (8) | balón parado (arquero rival) | bajo · RÉCORD | 5 de 8 de la racha fuera de liga (amistosos y previa de Conference) |
| Schalke 0-0 Bayern (05/09, Bundesliga) | Bayern · racha + (6) | arquero rival (rotación) | ALTO · — | el ALTO salió de un +3 con el nivel de Schalke medido en la 2. Bundesliga |
| Elversberg 1-2 Bayern (13/09, Bundesliga) | Elversberg · racha + (3) | superioridad del rival | MUY ALTO · RÉCORD | ascendido: MUY ALTO tres semanas seguidas, reventó 1 de 3 |
| Dunkerque 2-1 Saint-Étienne (12/09, Ligue 2) | Saint-Étienne · racha + (7) | arquero rival (varianza) | bajo · RÉCORD | sin los 2 amistosos la racha no era récord |
| Juárez 2-0 Tigres (19/09, Liga MX) | Juárez · racha − (8) | penal (cambio de DT) | ALTO · RÉCORD | la racha cruzó tres bancos; cortó en el 2.º partido de Lema |
| San Luis 4-0 U. Católica (11/07, Copa Chile) | U. Católica · racha + (9) | rotación (balón parado) | bajo · RÉCORD | ya clasificada, rival de Primera B |
| IDV 2-2 U. Católica (29/08, LigaPro) | IDV · racha + (16) | otro → doble golpe (superioridad) | MUY ALTO · RÉCORD | la racha la armaron DOS onces, uno por competición |
| Progreso 1-0 Danubio (29/08, Uruguay) | Progreso · racha − (5) | varianza (arquero propio) | MUY ALTO · RÉCORD | lo sostuvo el arquero del que venía perdiendo |
| Mallorca 1-1 Elversberg (08/08, amistoso) | Mallorca · racha + (4) | roja (racha de otra competición) | MUY ALTO · cerca, inflada | escala al revés: Mallorca descendido y Elversberg ascendido en el receso |

## Una corrección antes de los conteos

Todos los casos estudiados **reventaron**: así se eligen. Decir «el riesgo
MUY ALTO se cumplió» en la primera tanda no prueba nada sin las burbujas que
NO reventaron con ese riesgo — Elversberg lo mostró: MUY ALTO tres semanas
seguidas y reventó una. Lo que sí se puede leer de los estudios es el
MECANISMO y qué datos le faltaron a la página; la tasa la mide el backtest.

## Lo que se repite

1. **El extremo encendido** en 8 de 9 (en 3 de ellos con riesgo bajo).
   Sumando todo: es la alarma que más acompaña a un reventón, con la misma
   reserva de denominador.
2. **El arquero**, propio o rival, en 4 de 9 (Freiburg, Bayern,
   Saint-Étienne, Progreso), con 6 en la tanda anterior. No tiene casillero en
   ningún skill: es el candidato más repetido de los 43 estudios.
3. **`regresion_al_nivel`: cero** otra vez fuera de Perú.
4. **Los amistosos** arman récords: Freiburg, Saint-Étienne, Elversberg y
   Mallorca. Cuentan (decisión del 14/10), y la marca `inflada` ahora salta
   también cuando el récord de racha solo existe contándolos.
5. **La escala** pesó en 4 de 9 (Bayern–Schalke, Elversberg, U. Católica,
   Mallorca), y en Mallorca salió al revés.

## Arreglado en el código con esta tanda

- **La escala mueve la confianza**: con `comparable: false` el riesgo va con
  confianza «baja» y el motivo (nunca se mueven los puntos).
- **Cambio de categoría en el receso**: en un amistoso o una copa de
  pretemporada la escala mira la liga del próximo partido de liga de cada uno
  (`escala.liga_vigente`), no solo la del año anterior.
- **`inflada`** cuando sin los amistosos la racha no sería récord.
- **`dt_distinto_al_de_la_racha`** (calculada): el DT del banco contra el del
  primer partido de la racha (Juárez).
- Listas: mecanismos `arquero_propio`, `doble_golpe`, `cambio_masivo`;
  señales `sin_nada_en_juego`, `rival_con_once_alternativo`,
  `plantel_renovado`.

## Abierto (candidatos sin aplicar)

- Una burbuja armada por **dos onces** (IDV): medirla por competición u once.
- **Nada en juego** (U. Católica) podría calcularse desde la tabla del grupo.
- `dt_nuevo_rival` podría encenderse solo desde el DT del banco.
- La base de DT sigue inconsistente en rachas con varios bancos (Juárez: la
  ficha del 5/09 daba a Caixinha cuando dirigía Valero).

# Tercera tanda fuera de Perú — FOCO EN EL ARQUERO (14/10/2026) — 52 estudios

Con el perfil calculado del arquero en la ficha (`backend/analisis/arquero.py`)
y un bloque `arquero` por lado en cada estudio.

| Partido | Equipo · tipo | Mecanismo (secundario) | El arquero |
|---|---|---|---|
| OH Leuven 1-1 Cercle (12/09, Bélgica) | Leuven · racha − (6) | regresión al nivel (arquero propio) | van den Heuvel, atajada al 88' con 1-0 |
| Vitória SC 0-0 Casa Pia (06/09, Portugal) | Casa Pia · racha − (6) | **arquero propio** (varianza) | Mandić entró lesionado Gomes al 29' y ganó tres mano a mano |
| Shelbourne 2-2 Ajax (13/08, previa Conference) | Ajax · racha + (7) | rotación con la serie resuelta (arquero rival) | Beach, atajada del 2-3 al 89' |
| Ponte Preta 1-0 CRB (20/09, Serie B) | Ponte · racha − (6) | **arquero propio** (el rival se sobreexpuso) | Vinícius Ferrari, 7 atajadas |
| Union SG 1-1 OH Leuven (11/10, Bélgica) | Union · racha + (6) | otro: bajas forzadas tras 21 días de parón | no decisivo (suplente rival, señal bien encendida) |
| Porto 3-1 Benfica (20/09, Portugal) | Benfica · racha + (8) | roja | no decisivo |
| Famalicão 1-1 Sporting (13/09, Portugal) | Sporting · racha + (5) | **arquero rival** (varianza) | Carević, 4 de 5 al arco, dos en el 90+ |
| River 2-0 Argentinos (16/08, Argentina) | River · racha − (5) | regresión al nivel del plantel | no decisivo |
| San Lorenzo 2-1 4 de Mayo (23/09, Copa Paraguay) | San Lorenzo · racha − (7) | racha de otra competición (penal) | el arquero rival (aficionado) en los dos goles |

## Lo que dice el arquero

**Es un mecanismo, y tiene dirección.** En los 52 estudios aparece en ~16. En
casi todos es **el arquero del equipo más débil**:

- la racha positiva de un favorito que domina revienta contra el arquero
  RIVAL (Valles, Karius, Carević, Beach, Ramos, Atubolu);
- la racha negativa de un débil se corta sostenida por su arquero PROPIO
  (Bacchia, Mandić, Vinícius Ferrari, van den Heuvel, Medina);
- los errores son el espejo: Carlos Miguel, Marquínez (suplente), Cristaldo.

**El perfil calculado NO lo anticipa.** De los arqueros decisivos de esta
tanda, ninguno se veía en su perfil: Vinícius Ferrari y Rui Silva llegaban
NEGATIVOS y jugaron bien; Carević, neutro; Mandić no tenía perfil. Con n ≤ 8
y detrás de defensas malas, goles contra xG mide a la defensa tanto como al
arquero, y una goleada lo domina (Casa Pia). La «goals prevented» de la API
contradice al xG en la mitad de los casos. **La forma del arquero, medida así,
no sirve para pronosticar.** Lo único objetivo que funcionó es
`arquero_suplente` (Union SG, bien encendida).

**Propuesta (sin aplicar, la decide el usuario):** el arquero no entra como
señal de forma sino como **varianza del no favorito**. Cuando una burbuja
depende de que el que domina le gane al arquero del débil —favorito con racha
positiva contra un rival de bloque bajo, o débil con racha negativa contra un
favorito que va a acumular remates—, el riesgo de la burbuja tiene una cola
que la K no ve. Candidato para el TDE (bloque C) y para la lectura del
reventón: una marca «ARQUERO-NO-FAVORITO» de dispersión, sin dirección y sin
puntos, igual que el extremo. Medirla requiere el denominador (backtest con
remates al arco del favorito), no más estudios de reventones.

## Arreglado en el código con esta tanda

- Arquero: detalle partido a partido y `muestraCorta` (< 5 partidos con xG);
  el habitual sale de la competición del partido (Ajax: un arquero en Europa y
  otro en la liga); el suplente trae sus números (`hoyPerfil`).
- `paron_largo` (calculada, 14+ días sin partido) y mecanismo `bajas_forzadas`.
- `dt_distinto_al_de_la_racha` ya no mira los amistosos (banco de prueba).

## Datos de la base a revisar

- **DT del banco, otra vez**: San Lorenzo (Paraguay) con dos DT que se habían
  ido meses antes en las alineaciones; Shelbourne con otro nombre que la
  prensa. La regla «la alineación fresca manda» elige mal cuando la fuente de
  la alineación está mal.
- Ponte Preta: la API trae 6 titulares y un asistente con el id de otro.
- Copas de sede neutral o en casa del rival figuran con local nominal.
