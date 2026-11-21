# Propuesta de revisión · `sad-analysis` v4.7 → v4.8

**Estado: APROBADA por el usuario el 21/11/2026** («ármala y mergea… tal vez
debamos armar la 4.8 antes, este cambio me parece importante»). Aplicada el
mismo día: SKILL, `references/HISTORIAL.md`, `CORTE_VERSION`, anclas del
núcleo, prompt de `docs/COWORK.md` y modo `partes` de la corrida. La hora de
subida del zip va a `SUBIDA_VERSION` cuando el usuario lo suba.

**De dónde sale.** El rojo de Alavés–Deportivo (1570453, 21/11) salió de una
regla (la racha de un partido con riesgo alto lleva la espina al corte), no de
un juicio del analista. El usuario: «sería bueno que también el analista diga:
en este partido creo que no entro… debería verse en los partidos». Hasta acá
la duda del analista solo llegaba al semáforo si su espina iba contra su
elegido; lo que veía raro sin cambiar la espina quedaba en la prosa.

| n.º | Qué | Dónde | Tipo |
|---|---|---|---|
| 1 | `pronostico.entrar`: entraria · dudo · noEntraria, con motivo de una lista cerrada y el hecho del partido | 6-F nuevo, Auditoría 2 (10) | juicio nuevo + contrato |
| 2 | `separacionLiga`: con nivel `baja` el riesgo pesa menos; no mueve puntos (vivía solo en el prompt) | 1.7 (i) | redacción |
| 3 | Las otras familias: pesa el perfil DC; el resto es narrativa | 1.7 (j) | redacción |
| 4 | «Más empate con las dos burbujas en riesgo» no es regla: medido (REVENTON §19.1) | 1.7 (a) | cierre de candidato |
| 5 | Cuándo revienta, medido: sin periodicidad, la racha de un partido es la frágil, el típico por período no es guía, ganar por la mínima es aviso débil (REVENTON §20) | 1.7 (k) | redacción |

## 1. ¿Entrarías? (6-F)

**Por qué en el parte y no en la prosa.** Lo que el analista ve del partido y
el número no dice (un once incierto, un partido sin nada en juego, una lectura
de los skills que va contra el elegido) no tenía dónde contarse para que se
midiera. Un campo con lista cerrada se cuenta y se audita.

**Qué NO es.** No es la probabilidad ni mueve el 1X2 (el número sigue a las tres
fuentes, 6-A y 6-B). No es el semáforo: el semáforo sale de las espinas y el
analista no lo ve (regla anti-Goodhart de `docs/METODO_APUESTA.md`). Tampoco
repite lo que la app ya calcula (riesgo, DESCONFIAR, F3, extremo).

**Contrato** (`docs/openapi.yaml`, `EntrarAnalista`): `decision` obligatoria
de la lista; un motivo fuera de la lista se rechaza y los demás quedan; con 1X2
declarado y sin el bloque, el recibo lo pide en `faltan`; con `dudo` o
`noEntraria` sin motivo o sin porqué, también. La lista de Partidos
(`/analisis/lista-partidos`, cerrada al token de Cowork) lo trae y la tarjeta
lo pinta: ✋ «analista: no entra» en rojo, «analista: duda» en ámbar;
«entraría» no se pinta. El parte lo muestra debajo del falsador.

**Cómo se mide.** Quinto candidato del semáforo (`docs/METODO_APUESTA.md`):
desde la subida de la v4.8, el acierto del elegido con «dudo» o «noEntraria»
contra «entraria», con los escalones de siempre (30 para mirar, 60 para
decidir). Por acierto, nunca contra la casa.

## 2-5. Lo que pasa del prompt y de las mediciones al skill

Ya estaba anotado en DEUDA 41 para esta versión: `separacionLiga` y la regla de
las otras familias vivían solo en `docs/COWORK.md` (sin la guardia del test del
núcleo); el candidato del empate quedó medido y no se sostiene; y el cierre del
capítulo de las burbujas (REVENTON §20.2) se lleva a la lectura del reventón.
Ninguno mueve un número.
