<!-- Cómo depositar lo roto. Lo lee la corrida de partes, veredictos, reventones o rehacer SOLO cuando tiene algo que depositar. -->

## Al terminar partes, veredictos o reventones: depositá lo roto

Tu «Roto o a mirar» NO se queda en el chat: nadie lo lee ahí. Antes de avisar
al celular, mandalo como incidencias (una por hallazgo, aunque sea chico):

```
POST $B/analisis/cowork/incidencias
{"origen": "partes" | "veredictos" | "reventones",
 "corrida": "18/10 tramo 1",
 "items": [{"titulo": "DT de Bournemouth: la base dice Tindall y dirige Rose",
            "area": "dt", "severidad": "error", "fixtureId": 1557427,
            "detalle": "qué viste, dónde, con qué dato; qué hiciste en el parte"}]}
```

- `area`: dt · once · ficha · tde · dtp · f1 · timeline · reventon · burbujas
  · agenda · latido · cuotas · api · contrato · skill · aprendizaje · otro.
- `severidad`: `bloquea` (no se pudo depositar o cerrar, o el número que
  manda está mal) · `error` (la app dijo algo falso, y lo corregiste a mano o
  quedó así) · `aviso` (raro, a mirar).
- **El título nombra la CAUSA, no el caso** (20/10/2026: la cola llegó a 254
  porque cada partido abría la suya). Sin equipos ni jugadores en el título:
  «Titular de la ficha sin jugadorId», no «Titular de Rayo sin jugadorId»; el
  partido va en `fixtureId` y el caso concreto en `detalle`. Lo que va entre
  paréntesis o después de «:» no cuenta para agrupar. La misma causa abierta
  suma `veces` y junta los partidos en `fixtures`: que se repita es la señal de
  que el parche no alcanzó. Antes de depositar, mirá las abiertas
  (`GET …/incidencias`) y reusá su título si es la misma causa.
- Lo que es tuyo de corregir en el parte (un DT mal escrito) no es incidencia;
  lo que la APP hizo mal, sí, aunque lo hayas sorteado.
- **No se reporta**: antes de depositar, leé `no-se-reporta.md` (en esta misma carpeta): lo decidido que se cierra siempre igual no se vuelve a abrir.
