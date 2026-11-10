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

## Lo que sigue

El estudio de los **70** fallos en los que el elegido nunca se puso adelante: por qué la burbuja no arrancó (rival, sede, fatiga, DT, mercado), contra burbujas de riesgo parecido que siguieron.
