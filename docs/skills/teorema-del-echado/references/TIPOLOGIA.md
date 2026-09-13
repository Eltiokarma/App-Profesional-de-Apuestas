# Tipología — seis causas y dos eventos críticos

> **v0.1.3 (09.08.2026).** Alta de `SOB` como sexta tipología y de `SOBREEXPOSICIÓN` como segundo evento crítico. Derivado de TDE-014.

Cada tipo trae **definición**, **señal observable**, **cuándo falla el diagnóstico** y **contramedida**. Antes de asignar un tipo, leer la ficha completa: el módulo no permite aplicar un mecanismo sin haber leído dónde falla.

---

## ECHADA-VOL — Voluntaria / administrativa

**Definición.** El DT decide replegar para administrar un resultado, o es visitante contra uno más fuerte y el plan es aguantar y salir de contra. Aquí el repliegue es voluntario.

**Señal observable.** Cambio defensivo explícito; la línea baja 10-12 metros de golpe tras un cambio, no tras una jugada.

**Cuándo falla el diagnóstico.** Administrar 30 minutos en bloque bajo exige una disciplina que pocos planteles tienen. Falla cuando el equipo no ensayó el repliegue — no cuando la decisión fue mala. Confundir una mala ejecución con una mala idea es el error más frecuente del analista.

**Contramedida.** Sostener un punto de referencia arriba. Un delantero que aguante el balón convierte el repliegue en descanso; sin él, el repliegue es asfixia y cada despeje vuelve en ocho segundos.

---

## ECHADA-FIS — Física

**Definición.** La causa más común y la menos reconocida. Los volantes dejan de llegar al segundo balón y la línea de fondo retrocede para no dejar la espalda descubierta. Calendario cargado, altura, calor, minutos acumulados en los mismos titulares.

**Señal observable.** Se vuelve visible entre el minuto 60 y 65. La distancia entre volantes y defensa crece **antes** de que la defensa baje. La primerísima señal es la caída de duelos de segunda pelota, 8-10 minutos antes.

**Cuándo falla el diagnóstico.** Antes que nada, el test de coherencia de v0.1.1: si la transición aparece antes del minuto 45, **no es física** — revisar `SUP` y `PSI` antes de asignar este tipo. El sesgo documentado del módulo es asignar `FIS` por defecto porque el bloque F pesa ×3. Después, el error clásico: se atribuye a falta de carácter. El mitigante real no es el corazón, es el banco (Bradley et al. 2009: la distancia de sprint de alta intensidad cae 20-30% en el segundo tiempo; Mohr et al. 2003: el tiempo de reacción de los centrales se degrada 100-200 ms en los últimos 15 minutos).

**Contramedida.** Cambios en el mediocampo, no en la defensa. Refrescar la primera línea de presión es más barato que reforzar la última.

---

## ECHADA-SUP — Presión superada

**Definición.** El rival aprende a saltar la primera línea con un pase, y el equipo aprende a no presionar. Retrocede porque presionar y fallar es peor que no presionar.

**Señal observable.** PPDA que sube sin que caiga el ritmo físico. Dos o tres pases interiores exitosos del rival y la presión se apaga.

**Cuándo falla el diagnóstico.** Se confunde con la echada física y se corrige con piernas frescas que no arreglan nada, porque el problema es de plan, no de pulmón. Test rápido: si la echada aparece antes del minuto 45, casi nunca es física.

**Contramedida.** Cambiar la referencia de presión, no la intensidad: presionar el pase interior en lugar del hombre con la pelota.

---

## ECHADA-PSI — Psicológica

**Definición.** Miedo a perder lo que ya se tiene. El favorito que va 1-0 deja de jugar para ganar y empieza a jugar para no perder. También aparece tras recibir un gol o con público hostil.

**Señal observable.** Cae el volumen de pases hacia adelante en tercio rival sin que cambie el marcador ni el estado físico. Puede aparecer muy temprano: en TDE-005 el retroceso se volvió observable al minuto 20, diez minutos después de ponerse 1-0. Balones largos sin destino. Laterales que dejan de subir.

**Cuándo falla el diagnóstico.** Baumeister et al. 1998: el autocontrol colectivo consume recursos finitos, así que lo psicológico y lo físico se mezclan y son difíciles de separar en tiempo real. Regla práctica: si el retroceso coincide con un gol o una jugada polémica, es PSI; si coincide con el reloj, es FIS.

**Contramedida.** Una consigna concreta y ejecutable para el tramo final. No "aguantar", sino "dos toques y falta lejos del área". Lo vago acelera la echada.

---

## ECHADA-NUM — Numérica

**Definición.** Tarjeta roja, lesión que obliga a rearmar, o cambios defensivos que bajan el punto de referencia del equipo.

**Señal observable.** Instantánea. El dibujo cambia en una jugada.

**Cuándo falla el diagnóstico.** Es la única echada que no admite discusión táctica. Lo que se evalúa es el rearmado, no la decisión de replegar.

**Contramedida.** Sacrificar al hombre de la zona de menor peligro, no al más cansado.

---

## SOB — Sobreexposición

**Definición.** El equipo **no** repliega cuando correspondía. Necesita el gol, sube a los dos laterales, adelanta la línea y deja de tener volante de contención. No es un error de ejecución ni falta de orden: es un riesgo que compra a propósito y que casi nunca se contabiliza como riesgo. Es la vía espejo de la echada y produce el mismo síntoma observable — gol concedido en los últimos 15 minutos.

**Señal observable.** El equipo domina territorialmente y su volumen de remates sube mientras el rival deja de tener la pelota y empieza a tener contragolpes. Los dos laterales por delante de la línea media de forma simultánea y sostenida. Faltas tácticas propias en el círculo central: es el síntoma de que el equipo ya se dio cuenta de que está expuesto.

**Cuándo falla el diagnóstico.** De dos maneras opuestas. La primera: confundirlo con mala suerte. Un gol al minuto 90 de contragolpe se lee como accidente cuando es la consecuencia estadística de una estructura mantenida 20 minutos. La segunda, más peligrosa para el módulo: usarlo **después** del gol como explicación cómoda. `SOB` solo vale declarado antes; explicar un gol tardío como sobreexposición al verlo es hindsight con nombre nuevo (disciplina 9 del SKILL).

**Contramedida.** Un pivote fijo por delante de los centrales, aunque signifique un atacante menos. Es la misma contramedida que la FRACTURA, y no es coincidencia: las dos vías se resuelven poniendo un hombre en la franja que quedó vacía. La diferencia es de dónde viene el vacío — en la fractura, la línea bajó y los volantes no; en la sobreexposición, los volantes subieron y nadie se quedó.

**Interacción con la otra vía** *(v0.1.5)*. `SOB` describe un riesgo que el equipo compra, pero el gol lo tiene que hacer el rival. Si el rival va ganando y elige administrar, la sobreexposición queda sin castigo aunque la estructura esté igual de abierta: en TDE-016 un ISE de 10 no concedió por eso. Antes de cerrar `P(gol | sobreexposición)`, declarar qué está haciendo el rival. No aplicar descuento numérico hasta N ≥ 8 en la vía 2.

**Contraste obligatorio.** Antes de asignar `SOB`, verificar que el equipo efectivamente **no** retrocedió. Si retrocedió y además quedó partido, el tipo es `FRACTURA`. Los dos códigos describen goles en la misma ventana y son excluyentes.

---

## FRACTURA — El equipo no se echó, se partió

**Definición.** El síntoma peligroso no es el repliegue, es la descoordinación: la línea de cuatro retrocede pero los volantes no la siguen, y se abre la franja entre líneas donde el rival empieza a recibir de cara. De ahí sale la mayoría de los goles de los últimos 15 minutos.

**Señal observable.** Distancia línea de fondo – línea de volantes por encima de 18-20 metros sostenidos. Rival recibiendo de frente entre líneas dos veces seguidas sin oposición.

**Por qué tiene código propio.** Es la única variable del módulo con poder predictivo sobre el gol; el resto solo predice territorio. Por eso se estima aparte como `P(fractura | echada)` y no como consecuencia automática.

**Contramedida.** Es la única emergencia real: un pivote que baje con la línea, aunque signifique renunciar a salir jugando.

---

## Los dos eventos críticos, en una línea

| | Qué hace la línea de fondo | Qué hacen los volantes | Dónde queda el hueco |
|---|---|---|---|
| `FRACTURA` | Retrocede | No la siguen | Entre líneas, delante de los centrales |
| `SOB` | Se mantiene alta | Suben | Detrás de los centrales, a la espalda de los laterales |

Misma ventana, mismo síntoma, hueco distinto. Y la misma contramedida: un hombre que ocupe la franja vacía.

---

## Nota de vocabulario

Si el repliegue está entrenado y sostenido, el output correcto **no** es una echada — es un bloque bajo estructural, y el módulo debe reportar riesgo bajo aunque la altura de la línea sea idéntica. La palabra es peyorativa en su uso coloquial y el TDE respeta esa carga.

El uso literal de "echarse al piso" para cortar el ritmo o perder tiempo **no** entra en este módulo: es gestión del reloj, no repliegue. Si el usuario lo menciona en ese sentido, aclararlo y derivarlo a M3 del DTP.

---

## Estados que NO son echada (v0.1.9)

La rúbrica tiene seis tipologías de echada y una vía de sobreexposición. Hay tres estados observables que se le parecen y no lo son, y confundirlos contamina el registro:

| Estado | Cómo se ve | Por qué no es echada | Qué hacer |
|---|---|---|---|
| **Bloque bajo estructural** | Línea baja sostenida 30+ minutos | Es un plan entrenado con rodaje. C1 = 0 | Reportar riesgo bajo aunque la altura de línea sea idéntica |
| **Roto** | Concede 3+ goles, líneas partidas | No hay nada que proteger. El estado dejó de ser echada en el gol que abrió el partido | Cortar el análisis de echada en ese minuto exacto y decir cuál fue (disciplina 3) |
| **Rama abandonada** | El marcador resuelve antes de la ventana declarada | El escenario que el índice describía nunca existió | `clase_caso = rama_abandonada`, excluir de toda métrica de frecuencia (disciplina 24) |

**Caso de referencia de `roto` y `rama_abandonada` a la vez:** TDE-026, Botafogo en Cusco. Cuatro goles en contra antes del minuto 36, `ECHADA-VOL` declarada para 75-90 que nunca tuvo escenario, y los dos goles del tramo final concedidos por **sobreexposición propia** buscando el descuento — la vía que su propia fila puntuaba en ISE 1.7.
