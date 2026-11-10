# Pendientes para la próxima revisión de cada skill

Lo que el usuario ya aprobó para una revisión que todavía no se escribió. La
revisión de cada skill empieza por acá (y por su dossier en Aprendizaje): un
pendiente que solo vive en una incidencia cerrada se pierde.

## Redactado el 10/11/2026 — lo que queda de la APP

Las cuatro revisiones aprobadas el 10/11 (sad-analysis v4.5, TDE v0.1.26,
EFE v1.10 + efe-dashboard v1.13, DTP v1.8) ya están en `docs/skills/`. Cada
propuesta tiene su lista completa en «Para la app». Lo que bloquea una regla
redactada:

- **1056 (aprobada):** `HEREDA_SOB2` en `parte.py` también para las ramas
  del que persigue (`siRecibePrimero`, `siLeEmpatan`, `siIguala`) desde
  `nivelFocoPersiguiendo` (o `nivelRivalPersiguiendo`), y `HERENCIA-DTP` que
  compare la rama. No se recalculan partes viejos. Mientras tanto, el analista
  copia el SOB2.
- **1068 (c):** primero la fila `delOnceOficial` en `f1/{id}` (rol ROT, sin
  stats de temporada, marcada «agregada por la app»); después
  `EFE-RECOMPUTO-PENDIENTE` en `GET …/rehacer` (3+ titulares fijos
  cambiados o arquero distinto); y recién entonces la rutina `corrida-sad`,
  modo `rehacer`, que con esa alerta carga `efe-clasificador` (líneas
  ~229-237, ~255 y ~291-293 de su SKILL.md).
- **Banco probable:** una sola lista en la app para EFE 10, DTP 5 y TDE 5
  (hoy cada propuesta la nombra distinto).
- **Sanciones con `certeza` (A3 del EFE):** la leen EFE 5, DTP 7 y TDE 12.
  Kortrijk 1558673 va primero.
- **SAD 1, el origen de la burbuja:** `origen` en `/burbujas`, con las alertas
  `BURBUJA-INFLADA` y `BURBUJA-CONSTRUIDA`. Sin eso, la regla (f) no se
  declara.
- **Alertas de dato nuevas:** `RIESGO-EN-LOS-DOS`, `CADENA-VS-PARTE` y
  `BANCO-EN-FALSADOR` (SAD); `EJE-DEBUTANTE-SIN-DECLARAR` y `-SIN-OBJETO`, y
  `onceTardio` (EFE); `P6-OTRA-LINEA`, `M1-VS-ONCE-OFICIAL` y
  `bancoOfensivo` (DTP); la hora de llegada de la formación y su corrección
  tras el pitazo (DTP 6).
- **Jev, A0:** `lectura_efe` pasa a ser `lectura` del skill de su dossier. Lo
  ya sellado no se reetiqueta.
- **Medir:** EFE A6, A7 y A8; TDE 10; SAD 8 y 20; DTP `rolesVsGrid` sobre los
  6 casos del cambio 6.

## Redactado el 01/11/2026 — lo que queda de la APP

Las cuatro revisiones aprobadas el 01/11 (TDE v0.1.25, sad-analysis v4.4,
DTP v1.7, EFE v1.9 + efe-dashboard v1.12) ya están en `docs/skills/`. La 744
(`otra_via` para la pelota parada) entró a la disciplina 61 del TDE: la vía se
declara en el cierre con fuente. Hecho en la app con la redacción: el defecto
`abierto` del desenlace (`veredicto.regimen_desenlace`, los partes de la
v0.1.24 se cobran con su regla), `porqueDesenlace` pedido para `se_rompe` y
`rescata`, la espina sin `neutra` y con `guia: pronostico` (contrato, recibo,
`porGuia`). Lo marcado «pendiente de la app» en los skills, para el
mantenimiento si el usuario lo pide (cada uno con su sección en la propuesta):

- **TDE** (§ «Lo que tendría que hacer la app»): `viaGol` por gol en el cierre
  y la salida/ventana del reloj a `otra_via` con él (`porOtraVia`); quién
  persigue por `μ_partido` en cada tramo; banco ofensivo del rival, concesión
  tras roja propia e insumos de `S1` en `GET …/tde/{id}`; `ARQUERO-NUEVO`;
  `HERENCIA-DTP` en el `sob2` de rama; el rehacer recalcula el ISE de rama.
- **sad-analysis** (§ «Cómo se aplica», 2): motor contra mercado cuando eligen
  distinto, `DC-ALINEADOS`, `1X2-CARGA-CONTRA-RIESGO`, `ESPINA-VS-MARCADOR`,
  `GUIA-CONDICION-CON-T54/ESCALA`, el marcador declarado medido aparte.
- **DTP**: `P6-OTRA-LINEA`, `M1-VS-ONCE-OFICIAL`, pares de MECANISMO, M5 con
  volumen dentro del área, banco ofensivo; Fortuna y Estrela como incidencias.
- **EFE**: `EFE-RECOMPUTO-PENDIENTE`, `EJE-DEBUTANTE-SIN-DECLARAR/-SIN-OBJETO`
  (parejas nuevas sobre el once oficial), `recambio` en `f1/{id}`, nombres de
  la prosa sin fila F1, el arquero del día.
