<!-- Modo `mantenimiento` de la corrida SAD. Lo carga SOLO la corrida de este modo (SKILL.md dice cuándo). Credenciales y reglas comunes: SKILL.md. -->

## Modo `mantenimiento` (los parches, automáticos)

La rutina diaria que arregla lo que las corridas vieron roto (pedido del
usuario, 18/10/2026: la API siempre puede fallar y van a aparecer errores
nuevos). Acá SÍ se toca el código, con las reglas del repo (`CLAUDE.md` y, por área, `docs/REGLAS.md` mandan)
y con freno.

**La cola no puede crecer** (31/10/2026, usuario: «el mantenimiento tiene que
cerrar todo, optimizar todo hasta casi quedarse sin chamba»). La meta de CADA
pasada es la cola de abiertas en CERO. El mínimo aceptable: terminar con menos
abiertas que al empezar Y haber cerrado más de las que entraron desde la pasada
anterior. No hay tope de grupos: se trabaja hasta vaciar la cola, y con la
cola vacía se sigue con la prevención (paso 7-bis), que es lo que hace que
mañana entren menos. Al empezar anotá cuántas abiertas hay y cuántas entraron
desde la pasada anterior (las de `creadoEn` posterior): el informe final las
compara.

0. **Primero lo que quedó a medias y lo que decidió el usuario** (27/10/2026):
   - `GET $B/health` → `commit` (lo que corre en producción) y
     `GET $B/analisis/cowork/incidencias?estado=por_desplegar`: cada una cuyo
     merge YA está en ese commit (`git merge-base --is-ancestor <merge> <commit>`
     tras `git fetch origin main`) pasa a `resuelta`. Si lleva más de 24 h sin
     desplegarse, deposita UNA incidencia `bloquea` «despliegue atascado» con
     el PR y pasala a `usuario`.
   - `GET …/incidencias?estado=aprobada`: el usuario aprobó la propuesta desde
     la app. Van ANTES que las abiertas y cuentan como grupos de código del
     paso 3. Si la propuesta era una acción suya (una cuarentena, un
     desmentido, una variable), aprobar significa «hecho»: verificá con los
     GET que esté hecho y cerrala `resuelta`; si no, devolvela a `usuario`
     diciendo qué falta. Aprobar NO abre las zonas del paso 4 (motor, skills,
     tokens, datos, Railway): esas siguen siendo del usuario.
   - `GET …/incidencias?estado=usuario` + `GET …/incidencias/causas`: **limpiá
     la cola del usuario**. La que ya resolvió un PR mergeado después de que
     se derivó, cerrala `resuelta` con ese PR; las de la misma familia de
     causa (`causas[].ids`) déjalas en UNA: las demás pasan a `descartada`
     con «agrupada en #N». Al usuario le llega una decisión por causa, en la
     tarjeta «Decisiones pendientes» de Partidos, con la `resolucion` como
     propuesta: escribila para que se pueda aprobar sin abrir otra cosa (qué
     cambia, dónde, qué se pierde). **Si lo que proponés es una CUARENTENA**
     (10/11/2026, usuario: «poner algo en cuarentena es un dolor de huevos»),
     mandala también ESTRUCTURADA en el mismo POST …/estado:
     `"cuarentena": {"fixtures": [1492426], "motivo": "insumo falso: …", "ensena": true}`
     (motivo de 12+ caracteres, por criterio y nunca por resultado; los
     partidos a APARTAR, no el de la incidencia si es otro). La tarjeta abre el
     formulario ya escrito y, cuando el usuario confirma, pone la cuarentena y
     la incidencia queda `resuelta` sola: no hay nada que verificar después.
0-bis. **El escaneo preventivo** (30/10/2026, pedido del usuario: «no esperar
   a que salten estas cosas»): `GET $B/analisis/cowork/escaneo` recorre la
   agenda de las próximas 36 h y las partes jugadas en las últimas 48 h con los
   chequeos de lo básico (sancionados, el mismo jugador dos veces en la F1,
   DT sin confirmar, dos partidos el mismo día, sin cuotas, once tarde, ficha
   sin eventos). Los chequeos con `informativo: true` (`nivel-con-amistosos`
   y, desde el 02/11/2026, `sancion`, `sin-plantel` y `dt-sin-confirmar`, que
   se cerraban siempre por diseño) NO se depositan: son datos para el parte, no fallas.
   Por CADA otro chequeo con hallazgos depositá UNA incidencia
   (`POST …/incidencias`, `origen: "escaneo"`, el `area` y la `severidad` del
   chequeo, `titulo` = el del chequeo, `detalle` = los partidos y hallazgos,
   `fixtureId` = el primero): la misma abierta suma `veces`, no se duplica. Desde
   ahí entran al paso 1 como las demás. Un dato que un parte o un veredicto
   reporta y que el escaneo NO vio es un chequeo que falta: sumalo a
   `backend/analisis/escaneo.py` (`CHEQUEOS`, con la regla que cuida y su
   test en `backend/test_sanciones.py`) como parte del grupo que lo arregla.
1. `git fetch origin main`; trabajá en la rama designada de la sesión
   recreada desde `origin/main` (`git checkout -B <rama> origin/main`: su PR
   anterior ya se mergeó o no existe). `GET $B/analisis/cowork/incidencias`
   (abiertas, graves y repetidas primero) y `GET $B/analisis/cowork/latido`.
   Sin incidencias abiertas ni aprobadas: seguí con la prevención (7-bis).
   Una `en_curso` cuya resolución dice que la toma OTRA sesión (la de trabajo
   del usuario) no se toca; una `en_curso` de una pasada anterior sin PR se
   retoma como abierta.
   **Causa conocida, no se re-investiga** (27/10/2026): cada abierta trae
   `conocida` (la última cerrada de su familia, con la resolución). Si es
   `dato_api` · `por_diseno` · `descartada` y la nueva no trae nada que la
   resolución no cubra, cerrala igual remitiendo a ella («misma causa que
   #N: …») sin volver a verificar contra la base. Si la conocida es
   `resuelta` y la causa volvió, el parche no alcanzó: es código otra vez.
   **Lo que se repite sube al usuario**: `GET …/incidencias/causas?recurrentes=true`
   lista los `dato_api` vistos en 3+ partidos distintos sin decisión
   (`recurrente`) y lo que volvió después de un PR (`reaparece`). Por cada
   recurrente, pasá UNA incidencia de la familia a `usuario` con la regla de
   código que taparía el dato (como 381 y 673, que pasaron a código cuando el
   usuario las vio): qué se calcularía, con qué fuente, y qué caso lo pide.
   **Agrupá por CAUSA antes de tocar nada** (pedido del usuario, 22/10/2026:
   la cola llegó a 88 arreglando de a una). Varias incidencias suelen ser la
   misma raíz —el cruce de nombres de `contraElOnce`, la identidad del jugador
   en la ficha, la tabla F1, las ventanas del TDE, la escala entre ligas, las
   bajas de la API—: se arregla la raíz y se cierran todas las que cubre. Armá
   la lista de grupos (área + causa + ids) y ordenala por TAMAÑO (cuántas
   incidencias y `veces` suma la familia) y después por gravedad: **la familia
   más grande va PRIMERO**. «Grande» nunca es motivo para dejarla para
   después (30/10: la identidad de la F1, la clase que más pesa, quedó abierta
   «por grande» y la cola subió de 50 a 69): se parte en sub-causas y cada
   sub-causa es un grupo con su PR.
2. **Verificá cada una contra los datos antes de tocar nada** (los GET de la
   API, el código, los tests): una incidencia es un reporte, no una orden.
   Clasificala:
   - `por_diseno`: la app hace lo que se decidió (está en `CLAUDE.md`, en `docs/REGLAS.md`, en `docs/DEUDA.md` o en el
     doc del área). Resolución: la regla y dónde está escrita.
   - `dato_api`: la API trajo algo malo y no hay regla razonable que lo
     evite. Resolución: qué dato, de dónde, y qué alerta ya lo cubre.
   - `usuario`: le toca a una persona (una variable de Railway, una
     cuarentena o un desmentido con la llave maestra, una decisión).
     Resolución: qué hacer, exacto.
   - `descartada`: no se reproduce. Resolución: qué miraste.
   - código: marcala `en_curso` y arreglala (paso 3).
3. **El parche**: el cambio mínimo que lo arregla, con un test que falla sin
   él (en el `test_*.py` del área o en `backend/test_cowork.py`) y un
   comentario con el caso real que lo motivó, como el resto del repo. Cambios
   de contrato: primero `docs/openapi.yaml`, después backend, `src/api/
   types.ts`, los dos datasources y tests. **La CLASE, no el caso** (30/10/2026:
   la identidad del jugador se parchó 8 veces en un mes, cada vez en un
   módulo): antes de parchar, buscá la MISMA regla en los otros módulos
   (`grep` de la función o del criterio: el cruce de nombres vive en
   `bloque_f`, `f1_base`, `dtp_cowork`, `parte` y `ingesta/jugadores`) y
   arreglala en todos los que la usan, con un test por cada uno. **Cada grupo
   deja su guardia** (30/10/2026, usuario: «escaneo preventivo sobre nuestro
   código»): decí a qué clase de `docs/FALLAS.md` pertenece y, si la clase es
   nueva, sumala ahí con su guardia; si la regla se puede verificar leyendo el
   código, va a `backend/test_arquitectura.py`; si se ve en los datos, a
   `CHEQUEOS` del escaneo; si se ve en un parte, es una alerta calculada. La
   identidad de un jugador o un DT se arregla SOLO en `backend/identidad.py`
   (con su caso en `backend/test_identidad.py`). **Todos los grupos de
   código, sin tope** (31/10/2026; antes 6, y antes 3), **un PR por grupo**
   (cada uno con su batería del paso 5 en verde y su merge antes del
   siguiente): un grupo cierra todas sus incidencias de una vez. Las que NO
   son código (`dato_api` · `por_diseno` · `descartada` · `usuario`) se
   clasifican TODAS en la misma corrida. Solo queda abierto lo que de verdad
   no se puede cerrar en esta pasada (un test rojo que no es tuyo, un
   despliegue caído), y la respuesta final dice qué y por qué.
4. **Lo que NO se toca solo** (va a `usuario` con la propuesta escrita en
   `resolucion`, sin commit):
   - la matemática del motor (`src/motor/`, `backend/analisis/motor.py`,
     `docs/MOTOR_SAD_EXTRACCION.md`) y cualquier número calibrado
     (`PUNTOS_*`, `TASA_BACKTEST`, `MOVIMIENTO*` en `burbuja.py`/`burbuja.ts`,
     los pesos de un skill, umbrales del TDE/EFE);
   - los skills (`docs/skills/`) y lo que puntúan;
   - la autenticación y los tokens (`_COWORK_PERMITIDO`, `SAD_TOKEN_*`):
     abrir un endpoint es una decisión;
   - borrar datos, levantar o poner cuarentenas, el presupuesto de la API
     (`SAD_*` de cuota) y las variables de Railway;
   - un REDISEÑO: un cambio de contrato o de arquitectura que nadie pidió.
     Un grupo grande NO es un rediseño: se parte en sub-causas (paso 1) y
     cada una va en su PR de ≤ 10 archivos o ~400 líneas.
5. **Validá todo**: `npm run build`, `npm run test:motor`, `test:kview`,
   `test:burbuja`, `test:familias` y TODOS los `python -m backend.test_*` de
   `CLAUDE.md` (test_api, test_cowork, test_jugadores, test_ficha,
   test_en_vivo, test_dtp, test_calendario, test_cronologia, test_preflight,
   test_burbuja, test_familias, test_coherencia, test_modo_fallo, test_jev,
   test_backtest_burbuja, test_backtest_1x2, test_backtest_familias,
   test_cuotas_lote, test_despensa); si tocaste pantalla,
   `scripts/audit-movil.mjs` a 360 y 390. Un test que falla y no es tuyo
   (rojo en main también) se anota como incidencia nueva, no se tapa.
6. Commit (en español, qué y por qué, con las líneas de atribución que dé el
   entorno), push a la rama, PR a `main` con la lista de incidencias (id,
   qué era, qué se hizo). **Merge solo si** todo el paso 5 dio verde Y el
   diff respeta el paso 4; si no, el PR queda abierto y las incidencias en
   `usuario` con el enlace.
7. Cerrá cada incidencia: `POST $B/analisis/cowork/incidencias/{id}/estado`
   con `{"estado": …, "resolucion": "…", "pr": "#N"}` (cerrar exige
   resolución). **Resuelta es resuelta EN PRODUCCIÓN**: tras el merge, mirá
   `GET $B/health` → `commit`. Si ya contiene el merge, `resuelta`; si no
   (Railway tarda o está caído), `por_desplegar` con el PR, y la próxima
   pasada la confirma (paso 0). Con `commit` vacío (no se sabe) queda
   `resuelta` con «despliegue sin confirmar» en la resolución.
7-bis. **Con la cola en cero: la prevención** (31/10/2026, usuario: «optimizar
   todo hasta casi quedarse sin chamba»). Lo que entra mañana se decide hoy:
   - `GET …/incidencias/causas`: las familias que MÁS entraron en los últimos
     3 días. ¿Cada una tiene su guardia (chequeo del escaneo, regla de
     `backend/test_arquitectura.py`, alerta calculada, o el arreglo en la
     fuente que hace que no se produzca)? La que no, la gana en esta pasada,
     con su clase en `docs/FALLAS.md`.
   - Lo que las corridas reportan y se cierra siempre igual (`dato_api` o
     `por_diseno` con `conocida`): el reporte es ruido. Sumalo a la lista
     lista de `.claude/skills/corrida-sad/no-se-reporta.md` con la
     causa y dónde está decidida, para que la corrida no lo vuelva a abrir.
   - Las clases de `docs/FALLAS.md` sin guardia en código: una por pasada.
   Cada prevención va en su PR, con la misma batería y el mismo merge.
8. Respuesta final, cuatro líneas: **la cola** (abiertas al empezar → al
   terminar, y cuántas entraron desde la pasada anterior); grupos e
   incidencias resueltas (con PR y si ya están en producción); derivadas
   (dato_api · por_diseno · cuántas cerradas por causa conocida · cuántas
   causas nuevas esperan al usuario en «Decisiones pendientes»); y lo que
   quedó abierto, con el porqué, y la prevención que se hizo.
