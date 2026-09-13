# Parche para `EFE_v1_5_prompt.md` — v1.7 (30.08.2026)

> El prompt del proyecto es la fuente de verdad y es de solo lectura desde el contenedor.
> Hay que aplicar estos dos bloques **a mano**, desde la interfaz del proyecto.

---

## 1 · Añadir a la sección `ALERTAS AUTOMÁTICAS` → *Alertas por fecha*

- **COLAPSO POR VENTAJA PERDIDA** *(NUEVO v1.7)* → Si el equipo **no sostuvo ninguna ventaja de un gol** en la temporada en curso Y el rival tiene **≥2 suplentes con impacto documentado** desde el banco, emitir:

  > 💔 **ALERTA COLAPSO POR VENTAJA PERDIDA:** La alerta de COLAPSO EN CASCADA describe la caída del equipo **después de recibir el primer gol**. Existe la secuencia inversa y es más destructiva: el equipo **se pone en ventaja** y se desarma cuando se la empatan. Al golpe táctico —tuvo que reorganizarse desde una posición mental de ganador— se le suma el emocional de haber tenido el partido en la mano. El mecanismo es el mismo de la indefensión aprendida, pero con un coste de referencia mayor: no perdió una expectativa, perdió una posesión.
  >
  > **Predice:** diferencia amplia en contra a partir del minuto en que la ventaja se pierde, **no** a partir del primer gol recibido. Considerar handicap y over.
  >
  > **Criterios de activación:**
  > 1. El equipo no sostuvo ninguna ventaja de un gol en la temporada en curso (equivale a `C3 = ❌` del módulo del tramo final)
  > 2. El rival tiene ≥2 suplentes con gol, asistencia o impacto táctico documentado desde el banco esta temporada (equivale a `B5 = ✅` del rival)
  > 3. No requiere que el equipo tenga D3 ❌: es una alerta independiente de COLAPSO EN CASCADA y puede convivir con ella
  >
  > **Caso de referencia:** CD Moquegua 1-4 Alianza Atlético (F7 Clausura Perú 2026). Moquegua se puso 1-0 al minuto 20 y estaba 1-1 al minuto 24. Terminó 1-4, con los goles tercero y cuarto marcados por dos suplentes rivales que entraron al 59 y al 76. Su indicador de cierres previos estaba correctamente puntuado en el peor nivel y **ninguna alerta del sistema lo recogía**, porque todas las existentes describen la caída tras recibir, no tras perder una ventaja.

- **BLOQUE NO PROBADO** *(NUEVO v1.7)* → Si el rival juega con bloque bajo o medio-bajo que clasifica como **estructural** en el checklist, pero **todas sus vallas invictas salieron de partidos sin presión real** (empates y 0-0 contra rivales sin obligación de atacar), emitir:

  > 🧱 **ALERTA BLOQUE NO PROBADO:** El bloque del rival tiene los insumos de un bloque entrenado —modelo de más de seis meses, centrales de oficio, línea con rodaje, banco con recambios— pero **nunca sostuvo un resultado contra un rival obligado a ir a buscarlo**. La vida útil de 80-90 minutos se mantiene, porque los insumos son reales, pero **la alerta de degradación NO se suprime**: no hay evidencia de que ese bloque aguante bajo presión, solo de que no fue atacado.
  >
  > **Instrucción:** ampliar el rango de confianza, no mover el centro. Es la misma lógica de FACTOR-X aplicada a la estructura defensiva en vez de a un jugador.

---

## 2 · Añadir a la `Tabla resumen de alertas`

| Código | Tipo | Condición de activación |
|--------|------|------------------------|
| COLAPSO POR VENTAJA PERDIDA | Por fecha | No sostuvo ventajas de un gol + rival con banco de impacto |
| BLOQUE NO PROBADO | Por fecha | Bloque estructural con vallas invictas solo en partidos sin presión |

---

## 3 · Añadir al `BLOQUE D`, bajo la regla especial de D3

> **Nota v1.7 — la sexta pregunta del bloque.** El checklist de clasificación del bloque (skill `diagnostico-tactico` v1.2) suma una pregunta que no cuenta para el recuento y funciona como llave aparte: *¿este bloque sostuvo el resultado alguna vez estando empatado o en desventaja, contra un rival obligado a atacar?* Si la respuesta es no, el bloque es **estructural no probado** y la alerta de degradación se emite igual. Un bloque que solo aguantó contra rivales sin urgencia no demostró que aguanta, demostró que no lo atacaron.
