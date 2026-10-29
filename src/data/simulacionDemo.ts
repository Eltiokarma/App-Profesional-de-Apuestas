// Generado con backend.analisis.simulacion.simular sobre apuestas inventadas:
// la demo usa la MISMA cuenta que el backend (no una copia en TS).
import type { SimulacionApuesta } from '../api/types'

export const SIMULACION_DEMO: SimulacionApuesta = {
 "desde": "2026-10-28 05:00:00",
 "bancaInicial": 100.0,
 "unidad": 1.0,
 "cerradas": 5,
 "pendientes": 1,
 "aciertos": 3,
 "estrategias": [
  {
   "clave": "plana",
   "nombre": "Apuesta plana (control)",
   "descripcion": "1 unidad a nuestro elegido en cada partido",
   "banca": 100.8,
   "ganancia": 0.8,
   "apostado": 5.0,
   "apuestas": 5,
   "ganadas": 3,
   "roi": 0.16,
   "caidaMaxima": 0.0099,
   "quebro": null,
   "exposicionMaxima": 2.0,
   "montoMaximo": 1.0,
   "lineas": null,
   "serie": [
    {
     "fixtureId": null,
     "pitazo": null,
     "banca": 100.0
    },
    {
     "fixtureId": 900001,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 101.05
    },
    {
     "fixtureId": 900002,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 100.05
    },
    {
     "fixtureId": 900003,
     "pitazo": "2026-10-28 19:45:00",
     "banca": 101.05
    },
    {
     "fixtureId": 900004,
     "pitazo": "2026-10-28 20:00:00",
     "banca": 100.05
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 100.8
    }
   ]
  },
  {
   "clave": "plana60",
   "nombre": "Plana solo 60 %+",
   "descripcion": "1 unidad a nuestro elegido solo cuando le damos 60 % o más",
   "banca": 99.75,
   "ganancia": -0.25,
   "apostado": 2.0,
   "apuestas": 2,
   "ganadas": 1,
   "roi": -0.125,
   "caidaMaxima": 0.01,
   "quebro": null,
   "exposicionMaxima": 1.0,
   "montoMaximo": 1.0,
   "lineas": null,
   "serie": [
    {
     "fixtureId": null,
     "pitazo": null,
     "banca": 100.0
    },
    {
     "fixtureId": 900001,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 100.0
    },
    {
     "fixtureId": 900002,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 99.0
    },
    {
     "fixtureId": 900003,
     "pitazo": "2026-10-28 19:45:00",
     "banca": 99.0
    },
    {
     "fixtureId": 900004,
     "pitazo": "2026-10-28 20:00:00",
     "banca": 99.0
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 99.75
    }
   ]
  },
  {
   "clave": "kelly",
   "nombre": "Kelly completo",
   "descripcion": "f* = (p·c − 1)/(c − 1) de la banca a la selección con más ventaja; sin ventaja no apuesta",
   "banca": 108.42,
   "ganancia": 8.42,
   "apostado": 11.57,
   "apuestas": 3,
   "ganadas": 2,
   "roi": 0.7285,
   "caidaMaxima": 0.0071,
   "quebro": null,
   "exposicionMaxima": 11.01,
   "montoMaximo": 6.88,
   "lineas": null,
   "serie": [
    {
     "fixtureId": null,
     "pitazo": null,
     "banca": 100.0
    },
    {
     "fixtureId": 900001,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 100.0
    },
    {
     "fixtureId": 900002,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 99.29
    },
    {
     "fixtureId": 900003,
     "pitazo": "2026-10-28 19:45:00",
     "banca": 103.26
    },
    {
     "fixtureId": 900004,
     "pitazo": "2026-10-28 20:00:00",
     "banca": 103.26
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 108.42
    }
   ]
  },
  {
   "clave": "kellyMedio",
   "nombre": "Kelly ½",
   "descripcion": "la mitad de la fracción de Kelly",
   "banca": 104.18,
   "ganancia": 4.18,
   "apostado": 5.74,
   "apuestas": 3,
   "ganadas": 2,
   "roi": 0.7286,
   "caidaMaxima": 0.0035,
   "quebro": null,
   "exposicionMaxima": 5.42,
   "montoMaximo": 3.39,
   "lineas": null,
   "serie": [
    {
     "fixtureId": null,
     "pitazo": null,
     "banca": 100.0
    },
    {
     "fixtureId": 900001,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 100.0
    },
    {
     "fixtureId": 900002,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 99.65
    },
    {
     "fixtureId": 900003,
     "pitazo": "2026-10-28 19:45:00",
     "banca": 101.64
    },
    {
     "fixtureId": 900004,
     "pitazo": "2026-10-28 20:00:00",
     "banca": 101.64
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 104.18
    }
   ]
  },
  {
   "clave": "kellyCuarto",
   "nombre": "Kelly ¼",
   "descripcion": "un cuarto de la fracción de Kelly",
   "banca": 102.08,
   "ganancia": 2.08,
   "apostado": 2.86,
   "apuestas": 3,
   "ganadas": 2,
   "roi": 0.7287,
   "caidaMaxima": 0.0018,
   "quebro": null,
   "exposicionMaxima": 2.69,
   "montoMaximo": 1.68,
   "lineas": null,
   "serie": [
    {
     "fixtureId": null,
     "pitazo": null,
     "banca": 100.0
    },
    {
     "fixtureId": 900001,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 100.0
    },
    {
     "fixtureId": 900002,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 99.82
    },
    {
     "fixtureId": 900003,
     "pitazo": "2026-10-28 19:45:00",
     "banca": 100.82
    },
    {
     "fixtureId": 900004,
     "pitazo": "2026-10-28 20:00:00",
     "banca": 100.82
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 102.08
    }
   ]
  },
  {
   "clave": "martingala",
   "nombre": "Martingala",
   "descripcion": "por líneas: cada línea va 1 unidad a nuestro elegido, se duplica tras perder y vuelve a 1 al ganar; con todas en juego se abre otra",
   "banca": 99.8,
   "ganancia": -0.2,
   "apostado": 6.0,
   "apuestas": 5,
   "ganadas": 3,
   "roi": -0.0333,
   "caidaMaxima": 0.0198,
   "quebro": null,
   "exposicionMaxima": 5.0,
   "montoMaximo": 4.0,
   "lineas": {
    "abiertas": 2,
    "perdiendo": 1,
    "proximoMayor": 4.0
   },
   "serie": [
    {
     "fixtureId": null,
     "pitazo": null,
     "banca": 100.0
    },
    {
     "fixtureId": 900001,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 101.05
    },
    {
     "fixtureId": 900002,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 100.05
    },
    {
     "fixtureId": 900003,
     "pitazo": "2026-10-28 19:45:00",
     "banca": 101.05
    },
    {
     "fixtureId": 900004,
     "pitazo": "2026-10-28 20:00:00",
     "banca": 99.05
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 99.8
    }
   ]
  },
  {
   "clave": "martingala60",
   "nombre": "Martingala 60 %+",
   "descripcion": "la misma martingala por líneas, solo cuando nuestro elegido tiene 60 % o más",
   "banca": 100.5,
   "ganancia": 0.5,
   "apostado": 3.0,
   "apuestas": 2,
   "ganadas": 1,
   "roi": 0.1667,
   "caidaMaxima": 0.01,
   "quebro": null,
   "exposicionMaxima": 2.0,
   "montoMaximo": 2.0,
   "lineas": {
    "abiertas": 1,
    "perdiendo": 0,
    "proximoMayor": 1.0
   },
   "serie": [
    {
     "fixtureId": null,
     "pitazo": null,
     "banca": 100.0
    },
    {
     "fixtureId": 900001,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 100.0
    },
    {
     "fixtureId": 900002,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 99.0
    },
    {
     "fixtureId": 900003,
     "pitazo": "2026-10-28 19:45:00",
     "banca": 99.0
    },
    {
     "fixtureId": 900004,
     "pitazo": "2026-10-28 20:00:00",
     "banca": 99.0
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 100.5
    }
   ]
  }
 ],
 "porVersion": [
  {
   "version": "v4.1",
   "partidos": 2,
   "aciertos": 1,
   "estrategias": {
    "plana": {
     "apostado": 2.0,
     "ganancia": 0.05,
     "apuestas": 2,
     "roi": 0.025
    },
    "plana60": {
     "apostado": 1.0,
     "ganancia": -1.0,
     "apuestas": 1,
     "roi": -1.0
    },
    "kelly": {
     "apostado": 0.7097,
     "ganancia": -0.7097,
     "apuestas": 1,
     "roi": -1.0
    },
    "kellyMedio": {
     "apostado": 0.3548,
     "ganancia": -0.3548,
     "apuestas": 1,
     "roi": -1.0
    },
    "kellyCuarto": {
     "apostado": 0.1774,
     "ganancia": -0.1774,
     "apuestas": 1,
     "roi": -1.0
    },
    "martingala": {
     "apostado": 2.0,
     "ganancia": 0.05,
     "apuestas": 2,
     "roi": 0.025
    },
    "martingala60": {
     "apostado": 1.0,
     "ganancia": -1.0,
     "apuestas": 1,
     "roi": -1.0
    }
   }
  },
  {
   "version": "v4.2",
   "partidos": 3,
   "aciertos": 2,
   "estrategias": {
    "plana": {
     "apostado": 3.0,
     "ganancia": 0.75,
     "apuestas": 3,
     "roi": 0.25
    },
    "plana60": {
     "apostado": 1.0,
     "ganancia": 0.75,
     "apuestas": 1,
     "roi": 0.75
    },
    "kelly": {
     "apostado": 10.8557,
     "ganancia": 9.1347,
     "apuestas": 2,
     "roi": 0.8415
    },
    "kellyMedio": {
     "apostado": 5.3808,
     "ganancia": 4.5338,
     "apuestas": 2,
     "roi": 0.8426
    },
    "kellyCuarto": {
     "apostado": 2.6785,
     "ganancia": 2.2584,
     "apuestas": 2,
     "roi": 0.8432
    },
    "martingala": {
     "apostado": 4.0,
     "ganancia": -0.25,
     "apuestas": 3,
     "roi": -0.0625
    },
    "martingala60": {
     "apostado": 2.0,
     "ganancia": 1.5,
     "apuestas": 1,
     "roi": 0.75
    }
   }
  }
 ],
 "apuestas": [
  {
   "fixtureId": 900006,
   "pitazo": "2026-10-29 20:00:00",
   "partido": {
    "local": "Real Madrid",
    "visita": "Barcelona",
    "liga": "LaLiga"
   },
   "depositadoEn": "2026-10-29 15:01:00",
   "versiones": {
    "sad-analysis": "v4.2",
    "efe-clasificador": "v1.8",
    "teorema-del-echado": "v0.1.24",
    "diagnostico-tactico": "v1.6"
   },
   "versionPrompt": "v2.5",
   "probabilidades": {
    "local": 40.0,
    "empate": 26.0,
    "visita": 34.0
   },
   "cuotas": {
    "local": 2.2,
    "empate": 3.7,
    "visita": 3.2
   },
   "mercado": {
    "local": 43.8,
    "empate": 26.1,
    "visita": 30.1
   },
   "resultado": null,
   "elegido": "local",
   "kelly": {
    "seleccion": "visita",
    "fraccion": 0.04,
    "valor": 0.088
   },
   "estado": "pendiente",
   "porEstrategia": {
    "plana": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": ""
    },
    "plana60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "kelly": {
     "seleccion": "visita",
     "monto": 4.1305,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": ""
    },
    "kellyMedio": {
     "seleccion": "visita",
     "monto": 2.0328,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": ""
    },
    "kellyCuarto": {
     "seleccion": "visita",
     "monto": 1.0082,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": ""
    },
    "martingala": {
     "seleccion": "local",
     "monto": 4.0,
     "ganancia": null,
     "banca": null,
     "linea": 2,
     "motivo": ""
    },
    "martingala60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": "bajo 60 %"
    }
   }
  },
  {
   "fixtureId": 900005,
   "pitazo": "2026-10-29 19:30:00",
   "partido": {
    "local": "Liverpool",
    "visita": "Chelsea",
    "liga": "Premier League"
   },
   "depositadoEn": "2026-10-29 09:55:00",
   "versiones": {
    "sad-analysis": "v4.2",
    "efe-clasificador": "v1.8",
    "teorema-del-echado": "v0.1.24",
    "diagnostico-tactico": "v1.6"
   },
   "versionPrompt": "v2.5",
   "probabilidades": {
    "local": 60.0,
    "empate": 22.0,
    "visita": 18.0
   },
   "cuotas": {
    "local": 1.75,
    "empate": 3.9,
    "visita": 4.6
   },
   "mercado": {
    "local": 54.7,
    "empate": 24.5,
    "visita": 20.8
   },
   "resultado": "local",
   "elegido": "local",
   "kelly": {
    "seleccion": "local",
    "fraccion": 0.0667,
    "valor": 0.05
   },
   "estado": "cerrada",
   "porEstrategia": {
    "plana": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 0.75,
     "banca": 100.8,
     "linea": null,
     "motivo": ""
    },
    "plana60": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 0.75,
     "banca": 99.75,
     "linea": null,
     "motivo": ""
    },
    "kelly": {
     "seleccion": "local",
     "monto": 6.8841,
     "ganancia": 5.1631,
     "banca": 108.42,
     "linea": null,
     "motivo": ""
    },
    "kellyMedio": {
     "seleccion": "local",
     "monto": 3.3879,
     "ganancia": 2.5409,
     "banca": 104.18,
     "linea": null,
     "motivo": ""
    },
    "kellyCuarto": {
     "seleccion": "local",
     "monto": 1.6803,
     "ganancia": 1.2602,
     "banca": 102.08,
     "linea": null,
     "motivo": ""
    },
    "martingala": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 0.75,
     "banca": 99.8,
     "linea": 1,
     "motivo": ""
    },
    "martingala60": {
     "seleccion": "local",
     "monto": 2.0,
     "ganancia": 1.5,
     "banca": 100.5,
     "linea": 1,
     "motivo": ""
    }
   }
  },
  {
   "fixtureId": 900004,
   "pitazo": "2026-10-28 20:00:00",
   "partido": {
    "local": "Atlético",
    "visita": "Villarreal",
    "liga": "LaLiga"
   },
   "depositadoEn": "2026-10-28 15:02:00",
   "versiones": {
    "sad-analysis": "v4.2",
    "efe-clasificador": "v1.8",
    "teorema-del-echado": "v0.1.24",
    "diagnostico-tactico": "v1.6"
   },
   "versionPrompt": "v2.5",
   "probabilidades": {
    "local": 55.0,
    "empate": 27.0,
    "visita": 18.0
   },
   "cuotas": {
    "local": 1.75,
    "empate": 3.7,
    "visita": 5.0
   },
   "mercado": {
    "local": 54.9,
    "empate": 25.9,
    "visita": 19.2
   },
   "resultado": "visita",
   "elegido": "local",
   "kelly": {
    "seleccion": "empate",
    "fraccion": -0.0004,
    "valor": -0.001
   },
   "estado": "cerrada",
   "porEstrategia": {
    "plana": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 100.05,
     "linea": null,
     "motivo": ""
    },
    "plana60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.0,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "kelly": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 103.26,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "kellyMedio": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 101.64,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "kellyCuarto": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.82,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "martingala": {
     "seleccion": "local",
     "monto": 2.0,
     "ganancia": -2.0,
     "banca": 99.05,
     "linea": 2,
     "motivo": ""
    },
    "martingala60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.0,
     "linea": null,
     "motivo": "bajo 60 %"
    }
   }
  },
  {
   "fixtureId": 900003,
   "pitazo": "2026-10-28 19:45:00",
   "partido": {
    "local": "Inter",
    "visita": "Milan",
    "liga": "Serie A"
   },
   "depositadoEn": "2026-10-28 14:55:00",
   "versiones": {
    "sad-analysis": "v4.2",
    "efe-clasificador": "v1.8",
    "teorema-del-echado": "v0.1.24",
    "diagnostico-tactico": "v1.6"
   },
   "versionPrompt": "v2.5",
   "probabilidades": {
    "local": 52.0,
    "empate": 27.0,
    "visita": 21.0
   },
   "cuotas": {
    "local": 2.0,
    "empate": 3.5,
    "visita": 4.0
   },
   "mercado": {
    "local": 48.3,
    "empate": 27.6,
    "visita": 24.1
   },
   "resultado": "local",
   "elegido": "local",
   "kelly": {
    "seleccion": "local",
    "fraccion": 0.04,
    "valor": 0.04
   },
   "estado": "cerrada",
   "porEstrategia": {
    "plana": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 1.0,
     "banca": 101.05,
     "linea": null,
     "motivo": ""
    },
    "plana60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.0,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "kelly": {
     "seleccion": "local",
     "monto": 3.9716,
     "ganancia": 3.9716,
     "banca": 103.26,
     "linea": null,
     "motivo": ""
    },
    "kellyMedio": {
     "seleccion": "local",
     "monto": 1.9929,
     "ganancia": 1.9929,
     "banca": 101.64,
     "linea": null,
     "motivo": ""
    },
    "kellyCuarto": {
     "seleccion": "local",
     "monto": 0.9982,
     "ganancia": 0.9982,
     "banca": 100.82,
     "linea": null,
     "motivo": ""
    },
    "martingala": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 1.0,
     "banca": 101.05,
     "linea": 1,
     "motivo": ""
    },
    "martingala60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.0,
     "linea": null,
     "motivo": "bajo 60 %"
    }
   }
  },
  {
   "fixtureId": 900002,
   "pitazo": "2026-10-28 15:00:00",
   "partido": {
    "local": "Arsenal",
    "visita": "Tottenham",
    "liga": "Premier League"
   },
   "depositadoEn": "2026-10-28 10:10:00",
   "versiones": {
    "sad-analysis": "v4.1",
    "efe-clasificador": "v1.7",
    "teorema-del-echado": "v0.1.24",
    "diagnostico-tactico": "v1.6"
   },
   "versionPrompt": "v2.5",
   "probabilidades": {
    "local": 62.0,
    "empate": 22.0,
    "visita": 16.0
   },
   "cuotas": {
    "local": 1.62,
    "empate": 4.1,
    "visita": 5.4
   },
   "mercado": {
    "local": 59.0,
    "empate": 23.3,
    "visita": 17.7
   },
   "resultado": "empate",
   "elegido": "local",
   "kelly": {
    "seleccion": "local",
    "fraccion": 0.0071,
    "valor": 0.0044
   },
   "estado": "cerrada",
   "porEstrategia": {
    "plana": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 100.05,
     "linea": null,
     "motivo": ""
    },
    "plana60": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 99.0,
     "linea": null,
     "motivo": ""
    },
    "kelly": {
     "seleccion": "local",
     "monto": 0.7097,
     "ganancia": -0.7097,
     "banca": 99.29,
     "linea": null,
     "motivo": ""
    },
    "kellyMedio": {
     "seleccion": "local",
     "monto": 0.3548,
     "ganancia": -0.3548,
     "banca": 99.65,
     "linea": null,
     "motivo": ""
    },
    "kellyCuarto": {
     "seleccion": "local",
     "monto": 0.1774,
     "ganancia": -0.1774,
     "banca": 99.82,
     "linea": null,
     "motivo": ""
    },
    "martingala": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 100.05,
     "linea": 2,
     "motivo": ""
    },
    "martingala60": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 99.0,
     "linea": 1,
     "motivo": ""
    }
   }
  },
  {
   "fixtureId": 900001,
   "pitazo": "2026-10-28 15:00:00",
   "partido": {
    "local": "Real Betis",
    "visita": "Sevilla FC",
    "liga": "LaLiga"
   },
   "depositadoEn": "2026-10-28 09:58:00",
   "versiones": {
    "sad-analysis": "v4.1",
    "efe-clasificador": "v1.7",
    "teorema-del-echado": "v0.1.24",
    "diagnostico-tactico": "v1.6"
   },
   "versionPrompt": "v2.5",
   "probabilidades": {
    "local": 48.0,
    "empate": 28.0,
    "visita": 24.0
   },
   "cuotas": {
    "local": 2.05,
    "empate": 3.4,
    "visita": 3.9
   },
   "mercado": {
    "local": 47.0,
    "empate": 28.3,
    "visita": 24.7
   },
   "resultado": "local",
   "elegido": "local",
   "kelly": {
    "seleccion": "local",
    "fraccion": -0.0152,
    "valor": -0.016
   },
   "estado": "cerrada",
   "porEstrategia": {
    "plana": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 1.05,
     "banca": 101.05,
     "linea": null,
     "motivo": ""
    },
    "plana60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "kelly": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "kellyMedio": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "kellyCuarto": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "martingala": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 1.05,
     "banca": 101.05,
     "linea": 1,
     "motivo": ""
    },
    "martingala60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "bajo 60 %"
    }
   }
  }
 ],
 "excluidos": [
  {
   "fixtureId": 900010,
   "pitazo": "2026-10-28 23:00:00",
   "partido": {
    "local": "Villarreal",
    "visita": "Real Betis",
    "liga": "LaLiga"
   },
   "motivo": "sin las tres cuotas del 1X2 capturadas"
  }
 ],
 "nota": "DEMO: apuestas inventadas para ver la pantalla; en producción salen de los partes depositados"
}
