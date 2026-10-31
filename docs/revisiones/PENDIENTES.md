# Pendientes para la próxima revisión de cada skill

Lo que el usuario ya aprobó para una revisión que todavía no se escribió. La
revisión de cada skill empieza por acá (y por su dossier en Aprendizaje): un
pendiente que solo vive en una incidencia cerrada se pierde.

## teorema-del-echado (TDE) — para la v0.1.25

- **`salida: otra_via` también para la pelota parada** (incidencia 744,
  decisión del usuario 31/10/2026). Hoy `otra_via` existe solo para penal y
  autogol (v0.1.23), y un gol de córner o tiro libre cuando la vía escrita no
  operó queda `concedio` (Botafogo 0-2 de centro y rebote, Remo con un córner
  defendiendo 2-0, Everton, Sassuolo). Propuesta: sumar `pelota_parada`
  (córner, tiro libre), calculable desde el detalle del evento cuando la API lo
  trae; si no, sigue siendo juicio del cierre. Medir antes con los veredictos
  del 28/10 en adelante cuántas salidas cambia.
