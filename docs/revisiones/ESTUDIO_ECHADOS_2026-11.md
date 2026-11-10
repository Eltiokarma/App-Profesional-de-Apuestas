# Estudio de los 37 echados (10/11/2026)

**Pedido del usuario (10/11):** «lo que tienes son 107 burbujas que no han
funcionado como creemos… el centro de todo aprendizaje es la burbuja y
después el teorema del echado». Se empezó por los 37 partidos que el lente
del TDE explica mejor.

**Universo.** Son los partes cerrados del 01 al 09/11 (265). En **194**
nuestro elegido se puso adelante en el marcador:
- **37** perdieron la ventaja y no ganaron (19,1 %);
- **157** la sostuvieron. Ese es el **grupo de control**.

Los datos salen del parte depositado (TDE previo, espina, burbuja,
probabilidad de la casa) y de la ficha (`/fixtures/{id}/ficha`: eventos,
cambios, rojas y estadísticas).

## 1. Cómo se perdieron (autopsia con el TDE, 37 casos)

Tres subagentes hicieron la autopsia de cada caso con la v0.1.26 del skill.
Cada caso lleva un mecanismo de una lista cerrada, más un segundo opcional:

| Mecanismo | Principal | Como 2.º | Total |
|---|---:|---:|---:|
| **banco del rival** (el gol vino de alguien que entró y el que ganaba no respondió) | 6 | 9 | **15** |
| otro (empate en 1-10' sin cambios ni rojas, o gol sin crónica) | 9 | 1 | 10 |
| echada (replegó sin control) | 4 | 4 | 8 |
| penal | 4 | 3 | 7 |
| superado (el rival dominó todo el tramo) | 4 | 3 | 7 |
| sobreexposición (siguió atacando y lo agarraron de contra) | 6 | 0 | 6 |
| pelota parada | 1 | 3 | 4 |
| roja propia | 2 | 1 | 3 |
| error individual | 1 | 1 | 2 |

**¿El TDE previo lo vio?** Sí en 8, a medias en 23 y no en 6. Casi todos los
«a medias» dicen lo mismo: el TDE escribe que con una ventaja temprana manda
la línea del empate, y a veces nombra el banco rival, pero no dice **por qué
vía** llega el empate. En dos casos (Chivas y Union Berlin) la rama decía
«sigue atacando» y el equipo administró: la tipología quedó al revés.

## 2. Qué separa a los 37 de los 157 (control)

Cada señal que propusieron las autopsias se midió en los dos grupos. La base
es que se pierde la ventaja en 19,1 % de los casos.

| Señal | Perdieron | Aguantaron | Con la señal, se pierde la ventaja |
|---|---:|---:|---:|
| **Prob. de la casa del elegido < 48 % y se adelantó antes del 30'** | 13/37 | 24/157 | **35,1 %** (n 37) |
| Prob. de la casa < 48 % | 21/37 | 57/157 | 26,9 % (n 78) |
| Remates del rival ≥ propios (todo el partido, no es previa) | 15/37 | 40/157 | 27,3 % (n 55) |
| Se adelantó antes del 30' | 20/37 | 71/157 | 22,0 % |
| Riesgo de burbuja alto o muy alto | 21/37 | 84/157 | 20,0 % |
| Elegido con burbuja negativa (racha mala) | 14/37 | 58/157 | 19,4 % |
| Roja propia **antes** del gol recibido | 2/37 | 8/157 | 20 % |
| Ventaja con gol de penal o en contra | 5/37 | 22/157 | 18,5 % |
| TDE previo: rama de ventaja ECHADA / SOB | 13 · 20 | 61 · 94 | 17,6 % · 17,5 % |
| Metió un defensor por un medio o un delantero | 11/37 | 56/157 | 16,4 % |
| Se adelantó ≥ 45' y el rival hizo 2+ cambios en 15' | 6/37 | 32/157 | 15,8 % |
| ISE previo ≥ 6,5 (obligado) | 5/37 | 44/157 | 10,2 % |
| **Prob. de la casa ≥ 60 %** | 3/37 | 58/157 | **4,9 %** (n 61) |

**Trampa que el control evitó.** Contando toda roja propia, se perdía la
ventaja 52 % de las veces. Pero casi todas esas rojas llegaron **después** de
recibir el gol (por frustración): eran consecuencia, no causa. Contando solo
la roja anterior al gol recibido queda en 20 %, igual que la base.

**El gol del banco** está en 15 de los 37, pero también en los partidos que
aguantaron: entre los que recibieron al menos un gol, vino de un suplente en
43 % de los que perdieron contra 35 % de los que aguantaron. Es la vía
**más común** por la que se rompe una ventaja, no la que separa quién la
pierde.

## 3. Lo que dice

1. **Lo que separa es quién lleva la ventaja, no qué hace con ella.** Una
   ventaja temprana de un equipo al que la casa le daba menos de 48 % se
   deshace 1 de cada 3 veces. La de un equipo de 60 %+ se deshace 1 de cada
   20. Es la burbuja del usuario dentro del partido: el gol temprano del
   débil **infla** un resultado que su nivel no sostiene, y la regresión al
   nivel lo devuelve.
2. **Lo táctico (cambios defensivos, echarse o no, rojas, la tipología del
   TDE previo) no separó** a los que perdieron de los que aguantaron con esta
   muestra. El TDE acierta el **dónde** (la línea del empate, el banco rival)
   y falla el **cuál**, porque lo decide la fuerza del que gana más que su
   plan.
3. **n chico.** 37 contra 157, con un intervalo ancho. El 35 % y el 5 % son
   una pista fuerte, no un número calibrado.

## 4. Propuesta (para la próxima revisión del TDE y la app)

- **calculable, medir primero en la base.** Hay que construir la tabla «P(sostener la
  ventaja) por minuto en que se adelanta × prob. previa de la casa» sobre
  los ~35 mil partidos de `sad.db` con cuota (gratis, sin tokens). Si
  sostiene el 35 % / 5 %, la rama `siMarcaPrimero` toma su desenlace por
  defecto de esa tabla (como `ventajaPorMinuto`, pero partida por fuerza) y
  el TDE deja de decidirlo por tipología.
- **TDE (rúbrica, candidata):** en la rama de ventaja, la vía del empate se
  escribe con el banco rival nombrado y su minuto habitual de entrada (ya
  pedido en TDE 5 y DTP 12). La tipología ECHADA/SOB se sostiene solo con un
  hecho de hoy (TDE 11, candidato).
- **sad-analysis (narrativa):** un elegido de < 48 % que va a depender de
  ponerse adelante temprano tiene la burbuja «inflada dentro del partido»;
  es un aviso de **confianza**, no del 1X2 (decisión del 03/11).

## 5. Los 37 casos

| Partido (fixture) | Se adelantó | Prob. casa | Mecanismo | 2.º | Ruptura | ¿El TDE lo vio? |
|---|---:|---:|---|---|---:|---|
| Atletico Paranaense – Vasco DA Gama (04/11), elegido local (1492440) | 22' | 45.8 | error_individual | banco_rival | 61 | parcial |
| Instituto Córdoba 2-2 Newell's (elegido: Instituto, local) (1493236) | 7' | 49.2 | banco_rival |  | 66 | parcial |
| Cobresal – Everton de Viña (1505547) | 59' | 35.8 | echada |  | 90+5 | parcial |
| ADT – Sporting Cristal (07/11), elegido visita (1549545) | 47' | 37.1 | pelota_parada |  | 94 | si |
| Cienciano 1-2 Sport Huancayo (elegido: Cienciano, local) (1549546) | 5' | 42.6 | penal |  | 40 | no |
| Los Chankas – Alianza Lima (1549551) | 51' | 53.4 | banco_rival | superado | 59 | si |
| Universitario – UCV Moquegua (09/11), elegido local (1549553) | 36' | 76.0 | penal | banco_rival | 78 | parcial |
| Chicó 2-1 Inter de Bogotá (elegido: Inter, visita) (1549856) | 33' | 40.1 | penal |  | 44 | no |
| Torino – Lecce (1550195) | 60' | 52.1 | banco_rival | error_individual | 73 | si |
| Monterrey – Club Tijuana (01/11), elegido local (1551025) | 45' | 59.8 | sobreexposicion |  | 60 | si |
| Pumas 2-2 América (elegido: América, visita) (1551035) | 3' | 43.0 | otro | penal | 4 | parcial |
| León – Chivas (1551037) | 69' | 45.7 | echada | banco_rival | 87 | no |
| Groningen – Sparta Rotterdam (01/11), elegido local (1552215) | 1' | 53.9 | sobreexposicion | banco_rival | 15 | si |
| Willem II 1-1 PEC Zwolle (elegido: PEC, visita) (1552216) | 2' | 45.1 | otro |  | 3 | parcial |
| Fortuna Sittard – Telstar (1552217) | 15' | 45.5 | superado | echada | 45 | parcial |
| Heerenveen – Feyenoord (08/11), elegido visita (1552221) | 25' | 55.6 | superado | pelota_parada | 47 | parcial |
| Le Mans 1-1 Monaco (elegido: Monaco, visita) (1552814) | 40' | 57.0 | echada | banco_rival | 90 | si |
| Kortrijk – Mechelen (1558657) | 53' | 40.8 | roja_propia | echada | 69 | parcial |
| St. Truiden – OH Leuven (01/11), elegido local (1558669) | 46' | 55.8 | sobreexposicion |  | 53 | si |
| Antwerp 2-2 Lommel (elegido: Antwerp, local) (1558671) | 40' | 50.0 | sobreexposicion |  | 47 | si |
| Club Brugge – Anderlecht (1558672) | 41' | 59.8 | sobreexposicion | otro | 58 | parcial |
| Getafe – Sevilla (01/11), elegido visita (1570438) | 19' | 38.9 | otro | superado | 68 | parcial |
| Málaga 1-2 Racing Santander (elegido: Málaga, local) (1570447) | 28' | 39.6 | sobreexposicion | superado | 50 | parcial |
| Osasuna – Athletic Club (1570448) | 84' | 46.1 | echada | pelota_parada | 90 | no |
| Union Berlin – 1. FC Köln (01/11), elegido local (1575207) | 10' | 36.0 | banco_rival | echada | 79 | no |
| Paderborn 2-2 Frankfurt (elegido: Frankfurt, visita) (1575220) | 23' | 43.7 | otro | penal | 45 | parcial |
| Santa Clara – Gil Vicente (1575542) | 29' | 42.0 | superado | roja_propia | 52 | no |
| Kasımpaşa – Beşiktaş (01/11), elegido visita (1584453) | 28' | 60.5 | banco_rival | echada | 87 | parcial |
| Göztepe 1-2 Başakşehir (elegido: Göztepe, local) (1584463) | 18' | 45.8 | otro | banco_rival | 22 | parcial |
| Asteras Trípolis – Kalamata (1593354) | 46' | 47.2 | banco_rival |  | 67 | parcial |
| Olympiakos Piraeus – PAOK (08/11), elegido local (1593357) | 58' | 57.8 | otro |  | 71 | parcial |
| Fenerbahçe 3-2 Liverpool (elegido: Liverpool, visita) (1635658) | 25' | 64.3 | otro | banco_rival | 29 | parcial |
| Universidad Católica – Aucas (1639802) | 27' | 45.2 | superado | banco_rival | 45+1 | parcial |
| Mushuc Runa SC – Manta FC (03/11), elegido local (1639831) | 4' | 59.6 | otro | penal | 9 | parcial |
| Leones del Norte 1-1 Guayaquil City (elegido: Leones, local) (1639858) | 17' | 56.1 | otro | pelota_parada | 27 | parcial |
| Caracas – Puerto Cabello (1646933) | 81' | 34.8 | roja_propia | banco_rival | 89 | parcial |
| Portuguesa FC – Metropolitanos FC (08/11), elegido visita (1646934) | 5' | 37.5 | penal |  | 41 | parcial |

# Parte 2 · Los 70 que nunca arrancaron (10/11/2026)

De los 107 fallos, en **70** el elegido **nunca se puso adelante**: 32
terminaron en empate y 38 en derrota. La pregunta es por qué la burbuja que
leímos no arrancó. Se hizo una autopsia con el lente de la burbuja primero
(skill `sad-analysis` v4.5 y `docs/REVENTON.md`). El control son los **194**
partidos en que el elegido sí se puso adelante. La base es que el elegido
nunca se adelanta en **26,5 %** de los casos.

## 6. Por qué no arrancó (autopsia, 70 casos)

| Causa | Partidos |
|---|---:|
| **Varianza** (dominó y no la metió: xG o remates a favor, penales errados, arquero rival) | **23** |
| Rival más fuerte de lo que leímos | 12 |
| Le creímos de más a nuestra burbuja (corta, inflada, contra la casa) | 9 |
| Mandó la burbuja del rival | 8 |
| Partido cerrado (el empate era lo esperable) | 6 |
| Once o bajas | 5 |
| Fatiga o rotación | 4 |
| Sede o viaje | 2 |
| DT o sistema | 1 |

**¿Lo merecimos por la estadística?** Sí en **27**, parejo en 15, no en 23 y
sin datos en 5. En 4 de cada 10 «nunca arrancó» generamos más que el rival.
Esos no son burbujas mal leídas: son goles que no entraron.

## 7. Qué separa a los 70 de los 194 (control)

| Señal previa (antes del pitazo) | Nunca | Arrancó | Con la señal, nunca se adelantó |
|---|---:|---:|---:|
| **Nuestra prob. 2+ pts sobre la casa y la casa < 48 %** | 13/70 | 6/194 | **68,4 %** (n 19) |
| **Nuestra prob. 2+ pts sobre la casa** | 13/70 | 10/194 | **56,5 %** (n 23) |
| Prob. de la casa < 45 % | 41/70 | 55/194 | 42,7 % (n 96) |
| Burbuja propia + de 1 partido con riesgo alto/muy alto | 11/70 | 17/194 | 39,3 % (n 28) |
| Sin burbuja propia (K en 0) | 15/70 | 30/194 | 33,3 % (n 45) |
| Rival cerca o en su extremo en su condición | 9/70 | 20/194 | 31,0 % (n 29) |
| Motor y nosotros eligen distinto | 4/70 | 9/194 | 30,8 % (n 13) |
| Burbuja propia − de 1-2 con riesgo alto («deja de perder») | 16/70 | 56/194 | 22,2 % (n 72) |
| **Burbuja propia larga (3+ partidos)** | 6/70 | 49/194 | **10,9 %** (n 55) |
| **Prob. de la casa ≥ 60 %** | 4/70 | 61/194 | **6,2 %** (n 65) |

## 8. Lo que dice

1. **La señal más fuerte es ponerse por encima de la casa.** Cuando nuestra
   probabilidad del elegido quedó 2+ puntos sobre la de la casa, el elegido
   nunca se puso adelante en más de la mitad de los casos (68 % si además
   era un equipo de menos de 48 %). Es la burbuja **leída de más**: la
   racha o los perfiles nos convencieron más que al mercado. Confirma la
   decisión del 03/11 y la regla de la v4.5 de no apartarse del número de la
   casa. Los perfiles DC eran la causa más común de esos puntos, y la v4.5 ya
   los devuelve al mercado.
2. **Una burbuja larga sí arranca; una burbuja de un partido no es una
   burbuja.** Con 3+ partidos de racha, el elegido nunca se adelantó solo en
   el 11 % de los casos. Con una racha + de un solo partido y riesgo alto, en
   el 39 %. La burbuja del usuario funciona cuando existe: el error fue
   llamar burbuja a un resultado suelto.
3. **«Deja de perder» no es la trampa.** Una racha − corta con riesgo alto
   leída como corte arrancó **más** que la base (22 % contra 26,5 %).
4. **Un tercio fue fútbol puro.** En 27 de los 70 dominamos y no la metimos.
   Ninguna regla convierte eso en acierto.

## 9. La tabla de la base: ¿cuánto se sostiene una ventaja según la fuerza?

Fuente: football-data.co.uk, 11 ligas europeas del padrón (Inglaterra 1 y 2,
España, Italia, Alemania, Francia, Países Bajos, Portugal, Bélgica, Grecia y
Turquía), 2012/13-2025/26. Son **53.108 partidos** con la cuota de cierre
sin margen (Pinnacle o, si no hay, el promedio de casas) y el marcador al
descanso. El CSV no trae minutos, así que la ventaja medida es la del
**descanso**.

**Gana por 1 al descanso:**

| Prob. previa del que gana | n | Gana | Empata | Pierde | **No gana (se le escapa)** |
|---|---:|---:|---:|---:|---:|
| < 35 % | 8.145 | 53,1 % | 27,8 % | 19,0 % | **46,9 %** ± 1,1 |
| 35-48 % | 5.988 | 69,0 % | 22,1 % | 8,9 % | **31,0 %** ± 1,2 |
| 48-60 % | 3.940 | 75,6 % | 18,3 % | 6,1 % | **24,4 %** ± 1,3 |
| 60-75 % | 3.143 | 84,3 % | 12,6 % | 3,1 % | **15,7 %** ± 1,3 |
| 75 %+ | 1.338 | 90,6 % | 8,1 % | 1,3 % | **9,4 %** ± 1,6 |

**Gana por 2+ al descanso:** se le escapa a 17,4 % · 8,1 % · 5,4 % · 3,4 % ·
1,3 % (mismos tramos).

**Local y visita dan igual:** con 1 de ventaja al descanso se le escapa a
45,7 % y 47,5 % (< 35 %), a 30,4 % y 32,0 % (35-48 %), a 24,7 % y 23,6 %
(48-60 %) y a 15,8 % y 15,4 % (60-75 %). La condición no cambia nada una vez
que el equipo va ganando: manda la fuerza.

**Estable en el tiempo** (1 de ventaja, % que no gana): en 2012-18, 46,1 ·
29,6 · 22,8 · 15,6 · 8,7; en 2018-26, 47,4 · 32,1 · 25,5 · 15,7 · 10,0.

**Lo que confirma.** El 35 % de nuestro estudio (elegido de menos de 48 %
adelante antes del 30') cae justo entre el 31 % y el 47 % de la base. Esto
ya no es una pista de 37 casos: es una ley con 53 mil partidos detrás.
**Un gol del débil no cambia lo que es el débil.** El equipo de menos de 35 %
que va ganando al descanso no gana casi la mitad de las veces, y el de 75 %+
no gana solo 1 de cada 10.

## 10. Propuesta para la próxima revisión

- **TDE (rama `siMarcaPrimero`), calculable:** el desenlace por defecto de
  la rama de ventaja sale de esta tabla según la prob. previa de la casa, y
  no de la tipología. La app la sirve en `GET …/tde/{id}` como
  `ventajaPorFuerza`. El TDE describe la vía (banco, penal, contra); la
  tabla pone el número. **Pendiente:** rehacerla por minuto con los eventos
  de `sad.db` en el servidor (el CSV solo trae el descanso), y para las ligas
  americanas, que no están en football-data.
- **sad-analysis (burbuja):** una burbuja de **1 partido** no se lee como
  burbuja para sostener al elegido. Con riesgo alto, la espina no dice
  «sigue» con un solo partido (va con la regla (i) de la v4.5, ahora con su
  número: 39 % contra 11 %).
- **sad-analysis (mercado):** la medición confirma la regla de la v4.5 de no
  quedar sobre la casa. El aviso «nuestra prob. 2+ sobre la casa» es
  calculable (`vsMercado`) y puede ir como alerta de confianza en el recibo.
- **Medir:** con 100+ casos nuevos se repiten estas tres señales (perder la
  ventaja, nunca arrancar, burbuja de 1 partido). El script de la tabla de la
  base está en `docs/revisiones/datos/tabla_ventaja_por_fuerza.py`.
