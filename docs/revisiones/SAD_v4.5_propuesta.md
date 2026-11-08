# Propuesta de revisión · `sad-analysis` v4.4 → v4.5

**Estado:** PROPUESTA, falta que el usuario la apruebe (08/11/2026, usuario:
«ese aprendizaje está al nivel de un skill… vamos corrigiendo la brújula»).
No toca `docs/skills/sad-analysis/SKILL.md` hasta la aprobación. Al aprobarse:
se redacta en el SKILL, `CORTE_VERSION` con la v4.5 y, cuando el usuario suba
el zip, su hora en `SUBIDA_VERSION`.

## Por qué

La teoría de las burbujas dice cuánto puede rendir un equipo hasta reventar.
Hasta hoy el skill leía el TAMAÑO de la burbuja (K, racha, récord, riesgo) y
no su ORIGEN. La medición del 08/11 (DEUDA 26) dice que el origen importa, y
que importa **contra la casa**, no solo contra el azar:

- **Burbuja INFLADA por un golpe.** Un equipo que acaba de ganar teniendo
  25 % o menos (un batacazo: la K sube mucho porque le ganó a uno más fuerte)
  rinde bajo su cuota en el partido siguiente (−1,4 ± 1,2 puntos) y en el
  subsiguiente (−2,1 ± 1,2), y −2,6 ± 1,6 si ese subsiguiente es contra un
  rival fuerte. La casa le cree el golpe.
- **Burbuja CONSTRUIDA por una racha.** Un equipo con 10+ partidos sin perder
  gana +1,8 ± 1,3 sobre su cuota, y con 15+, +2,6 ± 2,1. La casa no le termina
  de creer.

Fuente: 62.320 partidos con la cuota de CIERRE (football-data.co.uk,
2012-2026; las diez ligas europeas del padrón, Argentina, Brasil y México).
Cada señal se partió en 2012-18 y 2019-26 y sale igual en las dos mitades.
Casi todo el efecto es de Europa: en las tres ligas americanas hay pocos casos
y no se ve. Ninguna señal sola le gana al margen de las casas.

**En nuestras apuestas** (269 cerradas desde el 28/10): con elegido invicto de
5+ acertamos 78 % cuando la cuota pedía 57 % (+21,0 ± 13,7; n = 46). Con
elegido tras batacazo, 14 casos: todavía no dice nada.

## Lo que cambia (paso 1.7, una regla nueva)

**(f) El origen de la burbuja: inflada o construida** *(v4.5)*. La línea de
`lecturaSad.reventon` dice de dónde viene la burbuja de cada equipo, con el
dato que lo prueba:

- **Inflada**: ganó como gran no-favorito (≤ 25 % sin margen) en uno de sus
  dos partidos anteriores. Con el elegido inflado, el 1X2 **no sube sobre el
  mercado** a ese lado, y el `porque` lo nombra («viene de ganar con 18 % al
  Bayern: burbuja inflada»). Es la misma lógica de «cargar» de 1.7 (a): frena
  la carga, no elige el lado.
- **Construida**: 10+ partidos sin perder. Con el elegido construido, el
  riesgo de reventón **no es razón para bajarlo del mercado** (ya lo dice
  6-B), y el `porque` lo nombra. **No suma puntos sobre el mercado**: la
  regla del favorito de la v4.4 sigue entera.

Lo que **no** cambia: ningún número de la app, ningún «+N» ni «−N», el 1X2 del
motor, los puntos del riesgo y la regla del favorito de 6-B. La señal mueve la
CONFIANZA y la carga, como la estabilidad en 1.7.

## Lo que pide a la app (después de aprobar)

Que el dato lo calcule la app, no Cowork (CLAUDE.md: «lo que está en nuestra
base se calcula»): en `/burbujas`, por equipo, `origen` con `inflada` (el
partido del golpe, su probabilidad sin margen) y `construida` (partidos sin
perder), y dos alertas de tipo `dato`, **BURBUJA-INFLADA** y
**BURBUJA-CONSTRUIDA**, documentadas en `docs/openapi.yaml`. La probabilidad
del golpe sale de `/cuotas` del partido previo; sin cuota capturada no hay
alerta (no se adivina desde el Elo).

## Cuándo se reabre

Con 100+ apuestas por grupo en la simulación (elegido inflado, elegido
construido). Si sobre NUESTRO acierto la inflada resta y la construida suma,
con los intervalos fuera de cero, la revisión siguiente propone mover el
número, con la validación por fecha de la v4.1. Si no, la regla (f) se queda
como lectura o se saca.
