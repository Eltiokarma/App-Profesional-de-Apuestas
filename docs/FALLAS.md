# Clases de falla — qué nos falló, por qué, y qué lo impide ahora

> Creado el 30/10/2026 (pedido del usuario: «un escaneo preventivo sobre nuestro
> código o en general todo lo que falla, para en el futuro no fallar»). Es el
> catálogo que mantiene el mantenimiento: cada grupo de código que arregla dice
> a qué clase pertenece y, si la clase es nueva, la suma acá **con su guardia**.
> `backend/test_arquitectura.py` exige que cada clase tenga una.

## De dónde sale

859 incidencias del 18 al 30/10/2026:
- **Por estado:** 314 resueltas con código; 279 datos de la API; 106 eran por diseño; 83 descartadas; el resto abiertas o esperando decisión.
- **Por área, las que más se repiten:** ficha 129, F1 128, DT 121, DTP 107, TDE 84 y once 44. Casi la mitad es **identidad**: quién es quién, jugador o DT.
- **Ritmo:** entraban 110-135 por día en las primeras jornadas y 43-58 en las últimas.

El patrón que se repite no es «el código está mal escrito». Es otra cosa:
1. **Reparamos casos, no clases.** La misma regla vivía en varios módulos, se parchaba uno y el error volvía por el otro.
2. **Construimos lo básico recién cuando alguien tropezaba.** Las suspensiones, quién pasó una llave o el once de las copas solo se construyeron después de que un parte se equivocó.

Las guardias de abajo atacan esas dos causas:
- **Para el código**, el test de arquitectura en CI.
- **Para los datos**, el escaneo preventivo (`GET /analisis/cowork/escaneo`).
- **Para los partes**, las alertas calculadas.

Tres lugares donde vive una guardia:
- `backend/test_arquitectura.py` → reglas que se verifican **leyendo el código**. Fallan en CI.
- `backend/analisis/escaneo.py` (`CHEQUEOS`) → reglas que se verifican **mirando los datos** de la agenda. Las corre el mantenimiento y abre una incidencia por chequeo.
- Alertas calculadas del parte (`parte._ALERTAS_CALCULADAS`) → reglas que se verifican **sobre un parte**. Suenan en el recibo y en la tira.

---

### 1. Identidad: quién es quién (jugador y DT)

- **Síntoma:** un jugador sale dos veces en la tabla F1, una baja que jugó, un DT «equivocado» que era el mismo, un titular que no casa con la referencia.
- **Casos:**
  - Jugador: 381 (Wesley Natã), 423 (S. Córdoba), 449 (Emmanuel/Emanuel), 582, 673 (Bisanz), 724 (11 veces), 741 y 839 (J. Peña y Y. Guzmán, registros superpuestos), 855 (Danilo), 856 (Berríos).
  - DT: Hoeneß/Hoeneb y Bazalar/Balazar.
- **Causa:** cinco módulos con cuatro versiones de «una letra» y dos formas de quitar tildes.
- **Guardia:**
  - **Regla única:** `backend/identidad.py`, con sus casos reales en `test_identidad.py`.
  - **Test de arquitectura (regla 1):** ninguna comparación de letras fuera de ese archivo.
  - **Escaneo:** chequeo `jugador-duplicado`.
- **Si vuelve:** el caso nuevo va a `identidad.py` con su test. Nunca un `if` en el módulo donde apareció.

### 2. El DT de la base, viejo o cruzado

- **Síntoma:** el parte se escribe con el entrenador saliente; cuarentenas por DT equivocado.
- **Casos:** deudas 2 y 6 (17 de 22 DT salientes el 16/09; la alineación rancia de Santa Fe–Cali; Pellegrini Ripamonti).
- **Guardia:**
  - **Refresco diario:** `jugadores --dt-agenda`; la alineación vale solo si es de los últimos 3 partidos.
  - **Alertas** `DT-DISCREPANCIA` y `DT-SIN-DT`.
  - **Cuarentena automática** que enseña.
  - **Escaneo:** chequeo `dt-sin-confirmar`.
- **Si vuelve:** la prensa manda; la base es la alarma, no la verdad.

### 3. El once que llega tarde, y el rehacer que no alcanza

- **Síntoma:** `DTP-REHACER` sin rehacer, el once de una copa capturado con la ficha, la prosa escrita sobre el once viejo.
- **Casos:** 444/451/454 (orden de la cola), 735, 737 (copas fuera de la cola del en vivo), 847, 848, 849 y 850.
- **Guardia:**
  - **Cola de onces:** `en_vivo.fixtures_para_xi` pide el once de todo partido con parte, de cualquier liga, y lo refresca a 40 minutos.
  - **Etiqueta del momento:** `momento_rehacer` distingue `tardio`, `sinRehacer` y `conocido`.
  - **El rehacer:** el modo rehacer de `corrida-sad` reescribe todo lo que nombra al once viejo.
  - **Escaneo:** chequeo `once-tarde`.
- **Si vuelve:** mirar primero si el partido entró en la cola, y recién después la rutina.

### 4. Quién no puede jugar

- **Síntoma:** un sancionado disponible; una baja de la API que ya jugó; el ruido de «Missing Fixture».
- **Casos:** 772 (Neymar), 778, 835; Missing Fixture (71, 312, 415).
- **Guardia:**
  - **Sanciones de la base:** `backend/sanciones.py` calcula la roja y el ciclo de amarillas.
  - **Alerta** `SANCION-SIN-DECLARAR`.
  - **Missing Fixture:** cuenta solo las marcas vigentes, y una sanción es siempre señal.
  - **Escaneo:** chequeos `sancion` y `sancion-sin-declarar`.
- **Si vuelve:** si es una regla de amarillas de otra liga, va a `UMBRALES` con la fuente del reglamento.

### 5. La falla callada

- **Síntoma:** algo deja de funcionar y nadie lo ve.
- **Casos:**
  - Tres semanas sin cuotas prepartido (deuda 8): un `except` las tragaba en cada corrida.
  - Siete tests que CI no corría (30/10/2026).
- **Guardia:**
  - **Latido:** el silencio cuenta como rojo; `cuotasPrepartido` y `presupuestoApi`.
  - **Test de arquitectura:** regla 4 (cada `except Exception` dice por qué es seguro seguir) y regla 2 (cada test corre en CI).
  - **Escaneo:** chequeos `sin-cuotas` y `ficha-sin-eventos`.
- **Si vuelve:** una fase que no guarda nada tiene que verse en el latido. Si no se ve, falta una señal.

### 6. Una regla del skill que se incumple

- **Síntoma:** el parte va contra una regla escrita del skill: la espina «sigue» en el récord, el EFE ordena un empate técnico, T.54 sin declarar, el favorito recortado sin dato.
- **Casos:** lecciones del 25-27/10.
- **Guardia:** la regla se CALCULA y suena en el recibo:
  - alertas `EFE-EMPATE-TECNICO`, `ESPINA-SIGUE-EN-EXTREMO`, `T.54-SIN-DECLARAR`, `TIPOLOGIA-VS-INDICES` y `HERENCIA-DTP`;
  - `vsMercado.naceDeRecorte`.
  - Una regla nueva no se cobra hacia atrás (`REGLAS_CALCULADAS_DESDE`).
  - Un aviso que cobra contra una lista de la base mira quién puede HOY (plantel y once oficial) y reconoce el texto que nombra al de la lista: `dtp_cowork._ejecutores_hoy` y `_nombra_ejecutor` (864, 885: el ejecutor en el banco, la línea que lo nombra con un «si no»). El mismo id con dos grafías es un jugador (872).
- **Si vuelve:** si la regla se puede calcular, se calcula. Si no, va a la próxima revisión del skill.

### 7. Una regla del fútbol leída del marcador

- **Síntoma:** se deduce del resultado algo que el resultado no dice.
- **Casos:** 774 (Palmeiras pasó por penales y el parte lo dio por eliminado); 846 (partido único resuelto en los 90').
- **Guardia:**
  - **Llaves:** `backend/eliminatoria.py`, con `avanza` en null cuando no se sabe.
  - **Alerta** `ELIMINATORIA-AL-REVES`.
  - **Tests:** `test_eliminatoria`.
- **Si vuelve:** toda regla de competición (llaves, sanciones, desempates) sale de la base con su fuente, nunca del texto.

### 8. La fuga del resultado (mirar el futuro sin querer)

- **Síntoma:** un backtest demasiado bueno.
- **Casos:** deuda 13: el nivel del rival escrito después del partido. El 1X2 subió de 47 % a 54 % y los puntos se calibraron con la fuga.
- **Guardia:**
  - **Nivel previo:** `backtest_burbuja.nivel_rival_previo`, con su test anti-fuga.
  - **Vista al día del partido:** `antesDe=<fixture>` en `/constantes`, `/niveles` y `/burbujas`.
  - **Corte temporal** en todos los backtests; la guardia de 15-35 % de empates.
- **Si vuelve:** todo backtest nuevo lleva un test que plante la fuga y la detecte.

### 9. El contrato desincronizado

- **Síntoma:**
  - El parte llega con un campo fuera de la forma (el número en `ieNivel`) o se pierde un bloque.
  - Un endpoint o una alerta sin documentar.
- **Casos:** los diez partes con `ieNivel` numérico; `timelineEventos` con tipos fuera de la lista; `/analisis/cowork/contrato` y 7 alertas sin documentar (30/10/2026).
- **Guardia:**
  - **Recibo:** `rechazos` y `faltan` en cada depósito.
  - **Forma del cuerpo:** `GET /analisis/cowork/contrato`, que sale de las mismas constantes que validan.
  - **Test de arquitectura (regla 3):** cada endpoint y cada alerta calculada están en `docs/openapi.yaml`.
- **Si vuelve:** primero el contrato, después el código (CLAUDE.md).

### 10. Lo que el skill o el prompt inventan

- **Síntoma:** el analista llama a algo que no existe y lo improvisa.
- **Casos:**
  - `/estadisticas/gap`, que no existe.
  - El Poisson sobre μ, en 78 partes, porque el skill pedía un modelo de goles que no había.
  - La Fe Perdida sin motor; el «checklist de 9 puntos».
- **Guardia:**
  - **Test de arquitectura (regla 5):** cada ruta que citan el skill de la corrida, `docs/COWORK.md` y `sad-analysis` existe.
  - **Motores suspendidos:** sad v4.0 suspende lo que no tiene motor.
- **Si vuelve:** un insumo que el skill necesita y no existe se construye o se suspende. No se deja al analista adivinarlo.

### 11. Los datos sucios de la API

- **Síntoma:** el dato llega mal.
- **Casos** (279 incidencias): dos fixtures del mismo partido, cuotas incoherentes (Marathonbet), mojibake en los nombres, el grid de la API equivocado, `/coachs` atrasado, alineaciones que no llegan (deuda 5).
- **Guardia:**
  - `cuota_mercados.casas_dos_salidas_incoherentes`;
  - `nombres.limpiar_nombre`;
  - el pipeline sin duplicados;
  - la cobertura de fichas aprendida por liga;
  - el `conflicto` de la agenda y el chequeo `dos-partidos`.
  - Un `dato_api` visto en 3+ partidos sube al usuario con una regla de código propuesta.
- **Si vuelve:** si se repite, deja de ser «dato de la API» y pasa a ser una regla nuestra.

### 12. El costo que se dispara

- **Síntoma:** la factura sube sin uso: Railway por la RAM, la API-Football agotada al mediodía, sesiones de rutina que engordan.
- **Casos:** `sad.db` de 30 GB (61 USD); deuda 9 (plan agotado a las 12:40); sesiones de rutina de 570.000 a 660.000 tokens.
- **Guardia:**
  - **Base de datos:** retención por fixture y `adelgazar`; los mercados guardados son solo los que se leen.
  - **API-Football:** el reparto del en vivo en el tiempo y el latido `presupuestoApi`.
  - **Consultas:** la guardia de peso del escaneo (`test_sanciones`: las consultas no crecen con los partidos y las sanciones se calculan una vez).
  - **Sesiones:** el recordatorio de tamaño de las sesiones fijas.
- **Si vuelve:** una consulta dentro de un bucle sobre partidos es un N+1: va en una sola consulta.

### 13. La métrica contaminada

- **Síntoma:** las tablas de Aprendizaje o la simulación dicen algo que no es cierto.
- **Casos:**
  - Las copas nacionales inflando el tramo de 60 %+.
  - Partes con el DT equivocado acreditando.
  - Reglas cobradas a partes escritos antes de que existieran.
- **Guardia:**
  - **Poblaciones:** `ciega`/`PRE`, `copa` y la cuarentena que enseña.
  - **Reglas nuevas:** `DESENLACE_DEFECTO_DESDE` y `REGLAS_CALCULADAS_DESDE` (`posteriorAlParte`).
  - **Cohortes** selladas al depositar.
- **Si vuelve:** lo que no es comparable sale de la métrica con su motivo, y se dice.

### 14. La automatización que no hace lo que creemos

- **Síntoma:** la rutina dispara y no hace nada, o hace lo de antes.
- **Casos:**
  - Rutina de sesión nueva sin el repo (13/10).
  - Disparar a mano desde fuera abre otra sesión.
  - El texto de una rutina solo se edita desde su propia conversación: las de mantenimiento seguían en «3 grupos» (30/10).
- **Guardia:**
  - **Sesiones fijas** con `git pull` en cada disparo.
  - **Ids anotados** en CLAUDE.md (deudas 11 y 17).
  - **El texto manda poco:** el texto de la rutina solo apunta al skill y el skill del repo manda.
- **Si vuelve:** cambiar el skill, no el texto de la rutina. Si hay que cambiar el texto, crear la rutina nueva y desactivar la vieja.
