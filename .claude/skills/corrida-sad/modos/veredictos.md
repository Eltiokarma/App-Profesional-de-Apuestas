<!-- Modo `veredictos` de la corrida SAD. Lo carga SOLO la corrida de este modo (SKILL.md dice cuándo). Credenciales y reglas comunes: SKILL.md. -->

## Modo `veredictos` (después del partido)

1. `GET $B/analisis/cowork/veredictos/pendientes?limite=45` → los partes
   jugados sin veredicto (lo que no entra queda para la próxima corrida, los
   más viejos primero; 45 desde el 27/10/2026: con 30 la cola llegó a 40
   vencidos tras un fin de semana; si el disparo trae otro `limite`, manda ese). Si no hay, decilo en una
   línea y terminá.
   Cada pendiente trae `prensa` (bool) y `prensaMotivo`: los elige el
   backend (`backend/analisis/prensa.py`, 13/11/2026) —los IMPORTANTES siempre
   (selecciones oficiales, eliminatorias de Champions/Europa
   League/Conference/Libertadores/Sudamericana y la última fecha de la fase de
   liga de la Champions, fases decisivas de las ligas, finales de copa) y,
   hasta el 50 % de los partidos de cada día, los que el 1X2 PERDIÓ, el más
   confiado primero—. No lo cambies a ojo: copialo al encargo de cada
   subagente como «prensa: sí (<prensaMotivo>)» o «prensa: no». El veredicto
   corre horas después del partido justamente para que la crónica ya esté.
2. Un subagente por partido, en paralelo y **en tandas de a 8 como mucho**
   (incidencia 1353, como en partes: el veredicto es idempotente, así que un
   POST con 502 se verifica con GET y se reintenta), con este encargo:

> Tus archivos de trabajo van SOLO en `<scratchpad>/{id}/` (otros subagentes
> corren en paralelo). Cerrá el caso del fixture {id} con el prompt «# PROMPT CORTO — "VALIDAR LO
> DE AYER"» de `docs/COWORK.md` (leelo entero). Lo objetivo (marcador, 1X2,
> Brier, ventana del TDE, rama de la reasignación, reventón) lo calcula la
> app: leelo de `GET $B/analisis/cowork/{id}/veredicto` y de la ficha
> (`GET $B/fixtures/{id}/ficha`), no lo escribas.
>
> La autopsia es POR SKILL, no por el 1X2: cargá
> `anthropic-skills:teorema-del-echado`, `anthropic-skills:efe-clasificador`
> y `anthropic-skills:diagnostico-tactico` y seguí su procedimiento de
> cierre de caso (en el TDE, «Cómo se cierra un caso» de CALIBRACION; en el
> DTP, la autopsia de goles con responsables y MECANISMO-ABIERTO). Cada
> hallazgo que toca una regla es UNA lección con `skill` y `reglaTocada`: la
> primera en `leccion`, las demás en `otrasLecciones` (hasta 6). Una
> confirmación de una regla también es lección («disciplina 44 declarada y
> cumplida»): es lo que cuenta casos a favor.
>
> **DTP-REHACER en el cierre: leé su `momento`** (26/10/2026: el 25/10 doce
> lecciones dijeron «sonó y no se rehízo» y la rutina había rehecho 18 partes;
> la API corrigió la formación cuando ya no quedaba disparo). `tardio` = la
> versión final del once llegó después del último disparo útil (piso de 15 min
> hasta el 31/10/2026, de 5 desde entonces): es apertura caída
> por un once TARDÍO, no un aviso ignorado — no escribas «no se rehízo» ni lo
> cargues como fallo del skill. `sinRehacer` = llegó a tiempo y nadie rehízo:
> anotalo en «Roto o a mirar» (falla de la corrida de rehacer), no como
> lección del DTP. `conocido` = el once ya estaba al depositar y la apertura
> igual lo contradice: ahí sí es lección. `parteTardio` = el parte se depositó
> por primera vez después del pitazo (1392): no hubo apertura previa que
> rehacer; va a «Roto o a mirar» (falla de la corrida de partes), no como
> lección del DTP. Sin `momento` (partes viejos), decí que no se sabe cuándo
> llegó el once.
>
> **Una regla no se cobra hacia atrás** (27/10/2026): una alerta con
> `posteriorAlParte` (ESPINA-SIGUE-EN-EXTREMO, EFE-EMPATE-TECNICO en partes
> anteriores al 26/10) y un desenlace del TDE con `noEvaluable` son reglas que
> el parte no podía conocer: no escribas «la incumplió» ni la cargues como
> fallo. Si el caso enseña algo sobre esa regla, va como confirmación o
> contraejemplo, no como incumplimiento.
>
> La matriz: `GET $B/analisis/cowork/{id}/objetivo` (antes del veredicto; el
> GET de `…/veredicto` da 404 hasta el primer POST) trae en `objetivo.matriz`
> qué escenario jugó cada equipo y qué se había escrito para él. Con
> `sinMatriz` el parte es anterior a la matriz estructurada: juzgá el
> escenario contra la prosa de `documentos[id=matriz]`. Por lado, `escenario: {aparecio: si|parcial|no,
> que}`: si la palanca o el gatillo escrito fue lo que pasó (sin tasa).
>
> Las otras burbujas cortadas: `objetivo.otrasFamilias` lista, por lado, las
> burbujas de doble oportunidad, márgenes y goles que el marcador cortó. Por
> cada una con `porExplicar` (grande o en su récord), escribí en
> `porLado.<lado>.cortes` `{familia, ambito, mecanismo, porque}`, con el
> mecanismo de la lista del estudio de reventones y el HECHO que lo prueba
> (ficha, once, DT, pelota parada). Un 0-2 de local del que siempre marca en
> casa tiene que quedar explicado (REVENTON §15.2); sin hecho, `varianza`.
>
> El banco: si la ficha trae en el banco a alguien que NO es el DT del parte
> y la prensa del partido explica por qué (DT suspendido o ausente, o la
> alineación de la API está mal: Juárez 18/10 con «T. Campos» y Lema en el
> banco), declaralo con `POST $B/analisis/cowork/{id}/dt` mandando el DT del
> parte con `banco: {motivo: suspendido|ausente|api_errada, nombre, fuente}`
> —el `dt` se reemplaza entero, así que va también `nombre` y `desde`—.
> Sin eso el caso cae en cuarentena automática por DT equivocado. Si el DT
> del parte ERA el equivocado, no lo tapes: corregí `nombre` y que entre en
> cuarentena, que para eso está.
>
> Lo que la app ya NO cobra, y no hace falta pelearlo: la ventana del TDE de
> un equipo que ya recibió 3 antes de ella (`clase: roto`, disciplina 3) o
> con el marcador 3 arriba (`rama_abandonada`, 24), una ventana relativa al
> gol y la de una rama declarada con su propia `ventana` (se mide esa). Y si
> la prosa del reventón de un parte de antes del 14/10 (tarde) no coincide
> con `reventonCalculado`, es la recalibración de los puntos (REVENTON
> §13.2): la prosa dice lo que la tarjeta mostraba ese día.
>
> **El reporte de la prensa, SOLO si el orquestador te lo marcó** (13/11/2026,
> usuario). Si tu encargo dice «prensa: sí (<motivo>)», DESPUÉS de leer lo
> calculado buscá la crónica del partido en internet (WebSearch, cargala con
> ToolSearch `select:WebSearch,WebFetch`; 2-3 búsquedas: crónica, figuras y
> DT/conferencia, en la prensa del país de cada equipo) y escribí en `notas`
> del veredicto el reporte: «Prensa (medio, fecha): …» con las ocasiones
> claras y su minuto, los goles y cómo nacieron, el plan de cada DT, lesiones
> o cambios forzados, la expulsión que cambió el partido y lo que dijeron los
> DT; al final la lista de fuentes (medio y URL). Lo que la prensa PRUEBA
> entra donde corresponde (el `porque` de un corte, el `que` del escenario,
> una lección con su skill) con la fuente en la frase; lo que solo opina no
> es lección. Los números no se reemplazan: si la prensa da otro xG o
> posesión que la ficha, manda la ficha y la diferencia se anota en `notas`.
> Sin crónica encontrada, `notas` lo dice («Prensa: sin crónica») y seguís.
> Con «prensa: no», NO busques en internet.
>
> `seleccion`: `ciega` si el partido salió de la agenda; `modoEvaluacion`:
> `PRE` si terminó. Con duda entre ciega y post_resultado, es post_resultado.
> `POST $B/analisis/cowork/{id}/veredicto` y leé `rechazos`. Respuesta final:
> marcador, veredicto por lado y la lista de lecciones (skill · regla).

3. Depositá lo roto como incidencias (`.claude/skills/corrida-sad/incidencias.md`). Respuesta final,
   tres líneas: veredictos cerrados, lecciones por skill, y
   qué no se pudo cerrar y por qué.
