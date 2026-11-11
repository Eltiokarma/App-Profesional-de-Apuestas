<!-- Modo `rehacer` de la corrida SAD. Lo carga SOLO la corrida de este modo (SKILL.md dice cuándo). Credenciales y reglas comunes: SKILL.md. -->

## Modo `rehacer` (cuando sale el once, antes del pitazo)

Pedido del usuario (22/10/2026), tras Sporting 2-3 LASK: DTP-REHACER sonó
(3-4-3 en vez del 3-5-2 de la apertura) y nadie lo rehízo, como en 9 de 24
partidos del 11/10. La app cierra el bloque F sola con la alineación, pero el
mapa de duelos y el 1X2 quedan escritos sobre otro equipo. Esta corrida corre
cada 20 minutos (:02, :22 y :42 de Lima desde el 31/10/2026, más :12 de 10 a 23
desde el 01/11 y :52 desde el 10/11, incidencia 1304; antes cada 30: el
once llega ~25 min antes y caía entre dos disparos, incidencia 636) y es CORTA:
casi siempre no hay nada que hacer.

1. **UNA sola llamada, antes de nada** (22/10/2026: cada disparo vacío
   costaba ~0,25 USD por leer la agenda y cada parte):
   `curl -sS -H "Authorization: Bearer $SAD_TOKEN_COWORK" "$SAD_API_BASE/analisis/cowork/rehacer"`.
   Trae los partes que arrancan entre **5 y 80 minutos** (`enVentana`; el piso
   bajó de 30 a 15 el 24/10/2026 y a 5 el 31/10/2026: la API publica el once
   ~25 min antes) y, de
   esos, los que tienen **DTP-REHACER** (`pendientes`: el once oficial
   contradice la apertura del DTP) o **PARTE-OTRA-FECHA** (el parte se
   escribió para la fecha vieja de un partido reprogramado: ese se rehace
   ENTERO, con el modo `partes`, no solo el DTP; desde el 25/10/2026,
   incidencia 395) o **DT-VS-BANCO** (el once oficial sienta a otro DT que el
   del parte: confirmalo en prensa y corregí SOLO el DT con `POST
   /analisis/cowork/{id}/dt`, o declará `dt.banco` si el titular no se sienta;
   desde el 27/10/2026, incidencia 711) o **ALERTA-CONDICIONAL-AL-ONCE** («alerta condicional al once: EJE-DEBUTANTE», 10/11/2026, incidencia 1190): con el once oficial, resolvé esa alerta sobre el grid —confirmala o sacala— y escribí «confirmada/descartada con el once» en su detalle, aunque DTP-REHACER no suene. Con `pendientes` vacío: terminá YA en una
   línea («Nada que rehacer a las HH:MM de Lima»), sin `git pull`, sin leer
   el resto de este skill, sin otra llamada y **sin avisar al celular** (corre
   cada 20 minutos: un aviso vacío cada vez se deja de leer).
2. Con algún pendiente, recién ahí: `TZ=America/Lima date` y seguí.
3. Como mucho **8** partidos (decisión del usuario, 04/11/2026, incidencia
   1164: el 03/11 hubo 7 para el pitazo de las 15:00 y Feyenoord–Inter quedó
   sin rehacer con el tope de 6). Si hay más de 8, primero los que arrancan
   antes. **Excepción: un partido que el disparo siguiente ya no alcanza no
   espera** (usuario, 04/11/2026, noches de Champions con 8-10 pitazos a la
   misma hora): si su hora tope (pitazo − 5) cae antes del próximo disparo de
   la grilla (:02 · :12 · :22 · :42 · :52) más 10 minutos de trabajo, entra en ESTE
   disparo aunque pase el tope. El tope solo difiere a los que todavía tienen
   otra vuelta. Un subagente por partido, en paralelo, con este encargo:

> Tus archivos van SOLO en `<scratchpad>/rehacer-{id}/`. El partido {id}
> arranca a las {hora Lima}; hora tope de depósito: el pitazo − 5 minutos.
> Credenciales en `$SAD_API_BASE`/`$SAD_TOKEN_COWORK` (nunca las imprimas).
> Cargá `anthropic-skills:diagnostico-tactico` y `anthropic-skills:sad-analysis`.
>
> 1. `GET $B/analisis/cowork/{id}` (el parte entero: lo vas a devolver
>    ENTERO), `GET $B/fixtures/{id}/ficha` (el once oficial, con grid) y
>    `GET $B/analisis/cowork/dtp/{id}`. El motivo está en el detalle de la
>    alerta DTP-REHACER y en `dtp.bloques[].calculado.contraElOnce`.
> 2. En el bloque del DTP marcado —y SIEMPRE también en el bloque del rival,
>    porque su M2 nombra como rivales a los jugadores que cambiaron (incidencia
>    525, DTP v1.5)—: rehacé **M1** con el once oficial
>    (`sistema` y `xiReferencia` = los once titulares de la ficha) y **M2** en
>    sus dos capas (DTP v1.4): lo estructural (carriles, zonas, mecanismos)
>    se revisa; los duelos con nombre propio se reescriben con ESTE once, en
>    las dos direcciones del carril. Una vía de gol que dependía de un
>    jugador que no está, se saca; la del que entró, se escribe.
>    **Cambiar el nombre no es reescribir** (06/11/2026, incidencia 1259,
>    Willem II–PEC Zwolle: los duelos del extremo Slory pasaron a Vilhena,
>    que juega por dentro, con la misma frase): el duelo del que entró se
>    escribe con SU rol y su casilla del grid; si no hay tiempo para eso, el
>    duelo se saca y se dice en `notas`, no se deja con el rol del que salió.
> 3. **El sistema sale del grid** (incidencia 849): `m1.sistema` es la
>    formación de la ficha oficial (o la del grid si la API la corrigió), no
>    la que traía la apertura; actualizar solo `xiReferencia` deja la alerta
>    sonando.
> 4. **Todo lo que NOMBRA al once viejo se reescribe** (incidencia 850, La
>    Guaira y Vasco: se rehízo el DTP y el TDE, la matriz, el falsador y el
>    ensayo siguieron con la línea de cinco y con un titular que arrancó en el
>    banco). Buscá en el parte ENTERO cada jugador que salió del once y cada
>    mención del sistema viejo —`tde.bloques[]` (indicadores, ramas,
>    reasignación, tipología), `matriz`, el falsador del pronóstico,
>    EJE-DEBUTANTE y las alertas declaradas, la prosa del DTP, el ensayo y las
>    notas del EFE, y también `documentos[]` (el del TDE repite C1 y SOB2: 1219)
>    y las listas de banco del DTP (`viasGol`, `veredictoRamas`: un titular de
>    la hoja no va ahí, 1225)— y reescribí esas frases con el once oficial.
>    Y al revés: un jugador de `fuera` que está en la hoja (titular o banco)
>    sale de `fuera` (1213, Pollero entró y marcó). **El `cierre` de cada
>    bloque del DTP NO entra en el reemplazo de nombres** (1258): es la
>    autopsia del partido ANTERIOR, con los nombres de ese día. Lo demás no
>    se toca: una baja decisiva que no juega, un arquero distinto (EFE v1.6,
>    B6), la rama del TDE que dependía de un intérprete. Si el 1X2 se mueve,
>    movelo con su porqué en la lectura del 1X2 (disciplina 33); si no, no.
>    Antes de depositar, listá en tu respuesta los nombres que salieron y
>    confirmá que ninguno queda en el texto como titular.
>    **El TDE hereda del DTP, y al rehacer el que se mueve es el TDE**
>    (31/10/2026, incidencia 634, decisión del usuario): si el once cambia el
>    nivel del rest defense o la clase del bloque, el SOB2 y el C1 del
>    `tde.bloques[]` de ese equipo se reescriben con el valor del DTP rehecho.
>    NUNCA se devuelve el DTP al nivel de la apertura para que se calle
>    HERENCIA-DTP: eso deja el DTP más viejo que el once.
>    **Y si al moverlos suena TIPOLOGIA-VS-INDICES** (el ISE quedó bajo el
>    IE o al revés; 11/11/2026, incidencia 1298, aprobada por el usuario:
>    Fortuna–Telstar y PSG–Troyes la cambiaron a mano, Valencia–Real Madrid la
>    dejó): cargá `anthropic-skills:teorema-del-echado` y re-juzgá la
>    tipología modal de ese bloque con el skill; si el skill la sostiene,
>    decilo en `tde.bloques[].notas` con el porqué. Nunca la cambies a mano
>    sin el skill ni la dejes callada. No mueve pesos ni umbrales del TDE.
> 5. `POST $B/analisis/cowork` con el cuerpo ENTERO (el POST reemplaza; la
>    cadena conserva la primera apertura, eso no se toca). El cuerpo es la
>    respuesta del GET con tus cambios, **`entrada` incluida**: ahí viajan los
>    eventos del timeline y los pronósticos de la cadena, y sacarla los borra
>    (incidencia 1201; el GET re-depositado tal cual no pierde nada). Leé el recibo:
>    DTP-REHACER tiene que haber desaparecido de `alertas` en el GET
>    siguiente; si sigue, decí por qué (`contraElOnce.motivos`).
> 6. Después del pitazo NO deposites: decilo. Respuesta final: qué cambió
>    en M1/M2, qué otras secciones reescribiste por el once (paso 4), si se
>    movió el 1X2 (de cuánto a cuánto) y si la alerta se fue.

4. Depositá lo roto como incidencias (`.claude/skills/corrida-sad/incidencias.md`;
   `origen: "partes"`, `corrida: "rehacer
   <fecha hora>"`). Respuesta final, tres líneas: partidos rehechos, los que
   no (y por qué) y qué se rompió. Al celular SOLO si se rehízo algo o algo
   falló.
