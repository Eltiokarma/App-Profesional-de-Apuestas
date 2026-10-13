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
3. **Balón parado y arquero** pesan más (5 de 9 entre principal y
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
