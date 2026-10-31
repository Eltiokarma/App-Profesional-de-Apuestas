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
  - **Test de arquitectura (regla 1):** ninguna comparación de letras fuera de ese archivo, y ningún módulo que quite tildes a un nombre por su cuenta (811: el NFKD suelto tiraba la «ð»).
  - Los apodos conocidos del DT van en `identidad.APODOS_DT`, lista cerrada con su caso (951, «Pacheta»).
  - **Escaneo:** chequeo `jugador-duplicado`.
  - Un id que aparece en dos clubes con menos de 3 días entre hojas es un id chocado, no un traspaso (`f1_base.OTRO_EQUIPO_GAP_DIAS`, 961).
  - Al depositar, la fila F1 cuyo nombre no es el de su `jugadorId` en la base se avisa en `faltan` (`parte.nombres_vs_id`, 938): el id manda en el IP, el nombre en la pantalla.
  - El mismo jugador con otro id entre dos hojas: `identidad.ids_equivalentes`, que usan `cambiosXi` y las parejas nuevas del DTP (899).
  - **El diminutivo** es una lista cerrada en `identidad.HIPOCORISTICOS` («Fran»/«Francisco», «Rafa»/«Rafael», 937), nunca «el prefijo»: «Joselu» y «José» pueden ser dos personas.
  - **La sombra de la API** (0 partidos con minutos y ninguna hoja) se funde con su gemelo en `f1_base.deduplicar` (904). **Los ids que se alternan** también: nunca juntos en una hoja y 6+ hojas entre los dos con este equipo (Juan Francisco Bisanz figuró como 304371, 406291 y 304389, nunca dos a la vez); un arquero y uno de campo nunca se funden así.
  - **Lo que los datos no alcanzan a decidir** se marca y se protege, no se adivina: dos filas del mismo nombre que nunca compartieron hoja llevan `posibleMismoQue` y el bloque F no cuenta a una de baja si la otra jugó (932, Pratto). Dos ids que compartieron una hoja son dos personas, y el escaneo ya no las reporta (887, los dos «T. Palacios»).
  - **El que se fue:** su última hoja con otro club lo saca de la tabla (`f1_base.juegan_en_otro`, 931). La misma regla vale para todo: el ido no vuelve a la tabla por sus onces recientes (1032) y los penales lo dan fuera del plantel (`enPlantilla: false`, `juegaEn`, 1029).
  - **Dos titulares con el mismo apellido:** la mención pegada a la inicial de uno no nombra al otro en `contraElOnce` (1027, los dos Mina del Emelec), y dos ids con el mismo nombre visible salen con el nombre largo o el id en el XI y los cambios del DTP (`dtp_cowork.desambiguar`, 1040, los dos «T. Palacios»).
- **Si vuelve:** el caso nuevo va a `identidad.py` con su test. Nunca un `if` en el módulo donde apareció.

### 2. El DT de la base, viejo o cruzado

- **Síntoma:** el parte se escribe con el entrenador saliente; cuarentenas por DT equivocado.
- **Casos:** deudas 2 y 6 (17 de 22 DT salientes el 16/09; la alineación rancia de Santa Fe–Cali; Pellegrini Ripamonti).
- **Guardia:**
  - **Refresco diario:** `jugadores --dt-agenda`; la alineación vale solo si es de los últimos 3 partidos.
  - **Alertas** `DT-DISCREPANCIA` y `DT-SIN-DT`.
  - **Cuarentena automática** que enseña.
  - **Escaneo:** chequeo `dt-sin-confirmar`.
  - Un país o un equipo no es un DT: se filtra al guardar la hoja (como en /coachs) y al leerla (`jugadores.es_nombre_de_dt`, 1019, «Bolívia»).
  - Un once sin DT en la hoja entre dos entrenadores hace incierto el debut: el cambio de la semana (F1 del TDE sin dato) se afirma solo si el debut más viejo posible cae en la semana (`tde.cambio_dt_reciente`, 1037, Llaneros).
  - Lo que se lee del DT es del DT que está: la formación dominante del calendario cuenta solo los onces de su banco (665), y su «primer banco visto» es la llegada solo si el partido anterior tiene hoja con otro DT; si no, `desdeConfirmar` (750).
- **Si vuelve:** la prensa manda; la base es la alarma, no la verdad.

### 3. El once que llega tarde, y el rehacer que no alcanza

- **Síntoma:** `DTP-REHACER` sin rehacer, el once de una copa capturado con la ficha, la prosa escrita sobre el once viejo.
- **Casos:** 444/451/454 (orden de la cola), 735, 737 (copas fuera de la cola del en vivo), 847, 848, 849 y 850.
- **Guardia:**
  - **Cola de onces:** `en_vivo.fixtures_para_xi` pide el once de todo partido con parte, de cualquier liga, y lo refresca a 40 minutos.
  - **Etiqueta del momento:** `momento_rehacer` distingue `tardio`, `sinRehacer` y `conocido`.
  - **El rehacer:** el modo rehacer de `corrida-sad` reescribe todo lo que nombra al once viejo.
  - **Escaneo:** chequeo `once-tarde`.
  - El chequeo `once-tarde` del escaneo no cuenta el partido cuya ficha post-partido se selló sin alineaciones: la API no la dio nunca, es cobertura (deuda 5), no un once tarde (953; Copa del Rey con clubes de Tercera).
  - El último partido de copa no corta la cadena ni fija el M1: `aperturaPrevia` busca el último partido con parte (997), y el caso del bloque toma la fecha y la competición de ese mismo partido (`dtp_cowork._anterior_con_parte`, 1016) y `ultimoOnceDeLiga` acompaña al once rotado de copa (966); una apertura que entró «sin dato» de XI se reemplaza con la que lo trae (992).
  - Con la apertura de un partido anterior al último, `aperturaPrevia.cierreContra` trae el marcador y los goles de ESE partido: el cierre se valida contra él, no contra `partidoAnterior` (1035).
  - Lo que el texto pone en el banco no es el seguro: el rest defense quita los nombres pegados a «en el banco» / «de suplente» antes de buscar suplentes (`dtp_cowork.sin_en_banco`, 1047), como las piezas del M2 con `_DESDE_BANCO`.
- **Si vuelve:** mirar primero si el partido entró en la cola, y recién después la rutina.

### 4. Quién no puede jugar

- **Síntoma:** un sancionado disponible; una baja de la API que ya jugó; el ruido de «Missing Fixture».
- **Casos:** 772 (Neymar), 778, 835; Missing Fixture (71, 312, 415).
- **Guardia:**
  - **Sanciones de la base:** `backend/sanciones.py` calcula la roja y el ciclo de amarillas.
  - **Alerta** `SANCION-SIN-DECLARAR`.
  - **Missing Fixture:** cuenta solo las marcas vigentes, y una sanción es siempre señal.
  - **Escaneo:** chequeos `sancion` y `sancion-sin-declarar`.
  - La regla de la competición es la del reglamento: en Inglaterra la roja se cumple en cualquier competición doméstica (`sanciones.ROJA_DOMESTICA`, 958); el mismo evento dos veces no son dos amarillas (971); sin la regla de amarillas se dice (`sinRegla`, 1011); la hoja del partido de la roja no desmiente la sanción (980); la baja sin id casa por la fila de su id y la nota se lee venga donde venga (969, 959).
  - En el umbral del ciclo de amarillas se dice si suspende o si ya cumplió (`cicloAmarillas`, 1043): un número en el umbral sin explicación se lee como sanción olvidada.
  - La roja al cuerpo técnico no es de un jugador: `sanciones.del_equipo` la separa en `cuerpoTecnico` con la regla de la ficha (`ficha_tactica._cuerpo_tecnico_e_ids`) y la agenda la marca en `dt.expulsado` (919, 920).
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
  - **Un valor desconocido se dice, no se convierte callado:** un `estado` de baja que no es baja · duda · descanso vuelve en `rechazos`; el no convocado por descanso va a F4 y no pesa en el IP (807, rúbrica EFE v1.7).
  - **Un null dice por qué:** la tarjeta de la espina vacía trae `sinTarjeta` (K en 0, otra condición, sin guía; 866, 720). Un campo calculado que sale null sin motivo se lee como «falla» o como «cero».
  - **Lo declarado sin dato no se cobra:** el recibo no pide un bloque del TDE que el parte trae en `sinDato` (808) ni rechaza el `xiReferencia` que dice por qué no hay ningún once (813).
  - **Depósito:** el bloque del TDE guarda `notas` y devuelve en `rechazos` cada clave que no guarda (`parte.CLAVES_BLOQUE_TDE`, 863): lo que llega y no se guarda se dice. Una lista de claves nuevas nace con TODO lo que el prompt pide mandar en ese bloque (928: `sinDato` quedó fuera y se rechazaba). Y con lo que el GET le agrega (`ECO_BLOQUE_TDE`): el eco de un parte vuelve con eso (981). Lo que no se perdió no es un rechazo (1010: el `dt` sin antigüedad va en `sinAntiguedad`).
- **Si vuelve:** una fase que no guarda nada tiene que verse en el latido. Si no se ve, falta una señal.

### 6. Una regla del skill que se incumple

- **Síntoma:** el parte va contra una regla escrita del skill: la espina «sigue» en el récord, el EFE ordena un empate técnico, T.54 sin declarar, el favorito recortado sin dato.
- **Casos:** lecciones del 25-27/10.
- **Guardia:** la regla se CALCULA y suena en el recibo:
  - alertas `EFE-EMPATE-TECNICO`, `ESPINA-SIGUE-EN-EXTREMO`, `T.54-SIN-DECLARAR`, `TIPOLOGIA-VS-INDICES` y `HERENCIA-DTP`;
  - `vsMercado.naceDeRecorte`.
  - Una regla nueva no se cobra hacia atrás (`REGLAS_CALCULADAS_DESDE`).
  - Una regla del skill que el recibo y el veredicto aplican vive en una función que usan los dos: `parte.rama_empuja` (qué rama del TDE declara `desenlace`, 908: la de empate en ECHADA no).
  - La alerta de una regla que el texto ya cumple (el `porque` la nombra) no va a la tira: un aviso permanente se deja de leer (ESPINA-VS-RIESGO 291, ESPINA-SIGUE-EN-EXTREMO 874).
  - Las K armadas en otra categoría se marcan en la tarjeta (`escala.historiaOtraCategoria`, 974/975; también si la historia ENTERA de liga es de la categoría de abajo, `enTodaLaHistoria`, 1034: el perfil DC y las otras familias leen toda la historia): solo marca, ningún número se mueve (decisión del 22/10).
  - La base de un equipo es la liga de su temporada en curso cuando sus últimos 5 partidos de liga son de ella, no la mayoría del año (`escala.base_de`, 824: el ascendido).
  - Lo que se dice del PRÓXIMO partido sale de la competición de ese partido, no de la base del último año: `separacion_liga.del_partido` (869, el ascendido).
  - Los días de descanso salen de `jugadores.dias_descanso` (por horas) en el calendario, el TDE, el DTP y el camino de recuperación; `test_arquitectura` lo verifica (769, 870).
  - Un insumo calculado con muestra corta lo dice y no afirma (`PENALES_MUESTRA_MIN`, 942); el ejecutor de baja o sin titularidad reciente baja en la lista (895).
  - Un aviso que cobra contra una lista de la base mira quién puede HOY (plantel y once oficial) y reconoce el texto que nombra al de la lista: `dtp_cowork._ejecutores_hoy` y `_nombra_ejecutor` (864, 885: el ejecutor en el banco, la línea que lo nombra con un «si no»). El mismo id con dos grafías es un jugador (872).
- **Si vuelve:** si la regla se puede calcular, se calcula. Si no, va a la próxima revisión del skill.

### 7. Una regla del fútbol leída del marcador

- **Síntoma:** se deduce del resultado algo que el resultado no dice.
- **Casos:** 774 (Palmeiras pasó por penales y el parte lo dio por eliminado); 846 (partido único resuelto en los 90').
- **Guardia:**
  - **Llaves:** `backend/eliminatoria.py`, con `avanza` en null cuando no se sabe.
  - **Alerta** `ELIMINATORIA-AL-REVES`. Con dos llaves de la misma copa y desenlaces distintos (pasó octavos, cayó en cuartos), la frase solo se compara con la anterior si nombra a su rival (1031, Luqueño).
  - **Tests:** `test_eliminatoria`.
  - Los tramos del veredicto del TDE: el régimen lo define el marcador (una roja no abre otro, 943), el tramo que abre y cierra en el mismo añadido no pone a prueba la rama (745) y la roja con el id real de un titular con id negativo en la hoja se busca por nombre (940).
  - La prórroga se jugó solo si hay su marcador (la EFL Cup va directo a penales, 977); las copas a partido único van en `eliminatoria.PARTIDO_UNICO` con su caso (Copa Paraguay, 1017).
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
  - Un marcador viaja con el orden en que se lee: en los antecedentes `marcador` es el del equipo y `marcadorPartido` local-visita, como `marcadorPronosticado` (907).
  - El recibo trae `alertasAlLeer` (las calculadas que el GET le pone al parte, 771 y 806) y no rechaza lo que el prompt pide dejar vacío (el `dt.desde` sin fuente, 827): recibo y prompt dicen lo mismo.
  - **El ejemplo del prompt pasa el recibo:** un test lee la `reasignacion` de ejemplo de `docs/COWORK.md` y exige que no dispare `faltan` (1030: el recibo pedía `desenlace` y `sob2` que el ejemplo no traía).
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
  - `cuota_mercados.historial_util`: el historial de cuotas es el de ESTE partido (21 días antes del pitazo, desde la primera captura con 3 casas) y una cuota ≤ 1,00 no es cuota (765, 779, 829);
  - `nombres.limpiar_nombre`;
  - la línea del jugador sale de la fila del grid cuando el once lo trae completo, no de la letra de la API (`f1_base._lineas_por_grid`, 725; la misma regla que el once oficial del DTP);
  - el pipeline sin duplicados;
  - la cobertura de fichas aprendida por liga;
  - el `conflicto` de la agenda y el chequeo `dos-partidos`, con la misma regla (`jugadores.choque`, 24 h) en el calendario y los próximos de /predicciones (843, 892).
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

### 15. El nivel del motor medido con partidos de otra exigencia

- **Síntoma:** el 1X2 del motor favorece al débil con fiabilidad «alta».
- **Caso:** 860, Konyaspor 0-4 Galatasaray.
  - El motor dio 41 % al 14.º y 31 % al líder.
  - La ventana de 20 del nivel de Galatasaray traía 6 amistosos de pretemporada (Monza 0-2, Venezia 0-3, Villarreal 1-2) y 3 de Champions. En esa ventana sacaba 1,65 puntos por partido; en la liga, 2,44.
  - Lo salvó seguir al mercado.
  - **Medido después (30/10): los amistosos NO eran la causa.** Sin ellos el local queda en 40,8 %. El 41 % sale de un nivel que separaba a los dos por solo 0,26, menos de lo que vale jugar en casa (0,382 de μ = 0,55 de nivel). La localía tampoco es: la de la Süper Lig, medida por liga, es 0,479, de las del medio. La forma no entra al 1X2. La primera explicación («el nivel mal medido y la regresión castigan dos veces») se contó antes de medir y no se sostuvo.
- **Guardia:**
  - **Composición contada:** `backend/analisis/ventana_nivel.py` cuenta de qué está hecha la ventana de cada lado (`ventanaNivel` en `/predicciones`).
  - **Fiabilidad:** con 3+ amistosos baja `fiabilidadMu` a «media», con `porVentana` y la nota.
  - **Escaneo:** el chequeo informativo `nivel-con-amistosos`.
  - **Medición:** `backend/backtest_nivel_ventana.py` (30/10, 9.191 partidos de prueba). Sacar los amistosos del nivel no mejora el 1X2; sacar también los internacionales lo empeora donde hay amistosos. Con 3+ amistosos el motor queda el doble de lejos del mercado (0,084 de log-loss contra 0,041): eso sostiene el aviso.
  - El motor no se toca sin esa medición y sin el visto bueno del usuario.
- **Si vuelve:** mirar `ventanaNivel` antes de creerle a una divergencia grande entre el motor y el mercado. Y la causa de un número del motor se mide (`/predicciones` trae μ, nivel y `unXDos.d`) antes de escribirla.
