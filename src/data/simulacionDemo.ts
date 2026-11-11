// Generado con backend.analisis.simulacion.simular sobre apuestas inventadas:
// la demo usa la MISMA cuenta que el backend (no una copia en TS).
// Se rehace con: python scripts/generar_simulacion_demo.py
import type { SimulacionApuesta } from '../api/types'

export const SIMULACION_DEMO: SimulacionApuesta = {
 "trasFallos": {
  "base": {
   "n": 9,
   "aciertos": 5,
   "tasa": 0.5556,
   "intervalo": [
    0.2666,
    0.8112
   ]
  },
  "porK": [
   {
    "k": 1,
    "n": 3,
    "aciertos": 2,
    "tasa": 0.6667,
    "intervalo": [
     0.2077,
     0.9385
    ]
   },
   {
    "k": 2,
    "n": 0,
    "aciertos": 0,
    "tasa": null,
    "intervalo": null
   },
   {
    "k": 3,
    "n": 0,
    "aciertos": 0,
    "tasa": null,
    "intervalo": null
   },
   {
    "k": 4,
    "n": 0,
    "aciertos": 0,
    "tasa": null,
    "intervalo": null
   }
  ],
  "contacto": {
   "k": 3,
   "nMinimo": 100,
   "tasaMinima": 0.65,
   "n": 0,
   "tasa": null,
   "intervalo": null,
   "faltan": 100,
   "cumple": false,
   "estado": "en_observacion",
   "texto": "en observación: 0 de 100 casos tras 3 fallos"
  }
 },
 "desde": "2026-10-28 05:00:00",
 "bancaInicial": 100.0,
 "unidad": 1.0,
 "cerradas": 9,
 "pendientes": 1,
 "aciertos": 5,
 "estrategias": [
  {
   "clave": "proporcional",
   "nombre": "Proporcional con freno",
   "descripcion": "1 % de la banca a nuestro elegido; un tramo de confianza se pausa si en sus últimos 50 partidos acertó menos de lo que pedía la cuota, y vuelve cuando se recupera",
   "banca": 100.65,
   "ganancia": 0.65,
   "apostado": 9.07,
   "apuestas": 9,
   "ganadas": 5,
   "roi": 0.0718,
   "caidaMaxima": 0.0199,
   "quebro": null,
   "exposicionMaxima": 2.0,
   "montoMaximo": 1.03,
   "lineas": null,
   "tramos": [
    {
     "tramo": "<40",
     "n": 1,
     "aciertos": 0,
     "tasa": 0.0,
     "pide": 0.3846,
     "z": -0.79,
     "pausado": false
    },
    {
     "tramo": "40-49",
     "n": 2,
     "aciertos": 2,
     "tasa": 1.0,
     "pide": 0.4712,
     "z": 1.5,
     "pausado": false
    },
    {
     "tramo": "50-59",
     "n": 3,
     "aciertos": 2,
     "tasa": 0.6667,
     "pide": 0.5556,
     "z": 0.39,
     "pausado": false
    },
    {
     "tramo": "60+",
     "n": 3,
     "aciertos": 1,
     "tasa": 0.3333,
     "pide": 0.6155,
     "z": -1.0,
     "pausado": false
    }
   ],
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
    },
    {
     "fixtureId": 900006,
     "pitazo": "2026-10-29 20:00:00",
     "banca": 102.0
    },
    {
     "fixtureId": 900007,
     "pitazo": "2026-11-11 19:00:00",
     "banca": 102.69
    },
    {
     "fixtureId": 900008,
     "pitazo": "2026-11-11 21:00:00",
     "banca": 101.67
    },
    {
     "fixtureId": 900009,
     "pitazo": "2026-11-12 01:00:00",
     "banca": 100.65
    }
   ]
  },
  {
   "clave": "metodoVerde",
   "nombre": "Método solo en verde",
   "descripcion": "el método (1 % de la banca y el mismo freno por tramo) apostando solo cuando el semáforo del elegido está en verde: nuestro 1X2 a ≤ 2 pts de la casa y el marcador declarado con el elegido",
   "banca": 99.71,
   "ganancia": -0.29,
   "apostado": 4.02,
   "apuestas": 4,
   "ganadas": 2,
   "roi": -0.0715,
   "caidaMaxima": 0.0132,
   "quebro": null,
   "exposicionMaxima": 1.01,
   "montoMaximo": 1.01,
   "lineas": null,
   "tramos": [
    {
     "tramo": "<40",
     "n": 1,
     "aciertos": 0,
     "tasa": 0.0,
     "pide": 0.3846,
     "z": -0.79,
     "pausado": false
    },
    {
     "tramo": "40-49",
     "n": 2,
     "aciertos": 2,
     "tasa": 1.0,
     "pide": 0.4712,
     "z": 1.5,
     "pausado": false
    },
    {
     "tramo": "50-59",
     "n": 3,
     "aciertos": 2,
     "tasa": 0.6667,
     "pide": 0.5556,
     "z": 0.39,
     "pausado": false
    },
    {
     "tramo": "60+",
     "n": 3,
     "aciertos": 1,
     "tasa": 0.3333,
     "pide": 0.6155,
     "z": -1.0,
     "pausado": false
    }
   ],
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
     "banca": 101.05
    },
    {
     "fixtureId": 900003,
     "pitazo": "2026-10-28 19:45:00",
     "banca": 101.05
    },
    {
     "fixtureId": 900004,
     "pitazo": "2026-10-28 20:00:00",
     "banca": 100.04
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 100.04
    },
    {
     "fixtureId": 900006,
     "pitazo": "2026-10-29 20:00:00",
     "banca": 100.04
    },
    {
     "fixtureId": 900007,
     "pitazo": "2026-11-11 19:00:00",
     "banca": 100.72
    },
    {
     "fixtureId": 900008,
     "pitazo": "2026-11-11 21:00:00",
     "banca": 99.71
    },
    {
     "fixtureId": 900009,
     "pitazo": "2026-11-12 01:00:00",
     "banca": 99.71
    }
   ]
  },
  {
   "clave": "plana",
   "nombre": "Apuesta plana (control)",
   "descripcion": "1 unidad a nuestro elegido en cada partido",
   "banca": 100.68,
   "ganancia": 0.68,
   "apostado": 9.0,
   "apuestas": 9,
   "ganadas": 5,
   "roi": 0.0756,
   "caidaMaxima": 0.0195,
   "quebro": null,
   "exposicionMaxima": 2.0,
   "montoMaximo": 1.0,
   "lineas": null,
   "tramos": null,
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
    },
    {
     "fixtureId": 900006,
     "pitazo": "2026-10-29 20:00:00",
     "banca": 102.0
    },
    {
     "fixtureId": 900007,
     "pitazo": "2026-11-11 19:00:00",
     "banca": 102.68
    },
    {
     "fixtureId": 900008,
     "pitazo": "2026-11-11 21:00:00",
     "banca": 101.68
    },
    {
     "fixtureId": 900009,
     "pitazo": "2026-11-12 01:00:00",
     "banca": 100.68
    }
   ]
  },
  {
   "clave": "plana60",
   "nombre": "Plana solo 60 %+",
   "descripcion": "1 unidad a nuestro elegido solo cuando le damos 60 % o más",
   "banca": 98.75,
   "ganancia": -1.25,
   "apostado": 3.0,
   "apuestas": 3,
   "ganadas": 1,
   "roi": -0.4167,
   "caidaMaxima": 0.0125,
   "quebro": null,
   "exposicionMaxima": 1.0,
   "montoMaximo": 1.0,
   "lineas": null,
   "tramos": null,
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
    },
    {
     "fixtureId": 900006,
     "pitazo": "2026-10-29 20:00:00",
     "banca": 99.75
    },
    {
     "fixtureId": 900007,
     "pitazo": "2026-11-11 19:00:00",
     "banca": 99.75
    },
    {
     "fixtureId": 900008,
     "pitazo": "2026-11-11 21:00:00",
     "banca": 98.75
    },
    {
     "fixtureId": 900009,
     "pitazo": "2026-11-12 01:00:00",
     "banca": 98.75
    }
   ]
  },
  {
   "clave": "kelly",
   "nombre": "Kelly completo",
   "descripcion": "f* = (p·c − 1)/(c − 1) de la banca a la selección con más ventaja; sin ventaja no apuesta",
   "banca": 103.88,
   "ganancia": 3.88,
   "apostado": 16.11,
   "apuestas": 5,
   "ganadas": 2,
   "roi": 0.2406,
   "caidaMaxima": 0.0419,
   "quebro": null,
   "exposicionMaxima": 11.01,
   "montoMaximo": 6.88,
   "lineas": null,
   "tramos": null,
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
    },
    {
     "fixtureId": 900006,
     "pitazo": "2026-10-29 20:00:00",
     "banca": 104.29
    },
    {
     "fixtureId": 900007,
     "pitazo": "2026-11-11 19:00:00",
     "banca": 104.29
    },
    {
     "fixtureId": 900008,
     "pitazo": "2026-11-11 21:00:00",
     "banca": 103.88
    },
    {
     "fixtureId": 900009,
     "pitazo": "2026-11-12 01:00:00",
     "banca": 103.88
    }
   ]
  },
  {
   "clave": "kellyMedio",
   "nombre": "Kelly ½",
   "descripcion": "la mitad de la fracción de Kelly",
   "banca": 101.94,
   "ganancia": 1.94,
   "apostado": 7.97,
   "apuestas": 5,
   "ganadas": 2,
   "roi": 0.2436,
   "caidaMaxima": 0.0215,
   "quebro": null,
   "exposicionMaxima": 5.42,
   "montoMaximo": 3.39,
   "lineas": null,
   "tramos": null,
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
    },
    {
     "fixtureId": 900006,
     "pitazo": "2026-10-29 20:00:00",
     "banca": 102.15
    },
    {
     "fixtureId": 900007,
     "pitazo": "2026-11-11 19:00:00",
     "banca": 102.15
    },
    {
     "fixtureId": 900008,
     "pitazo": "2026-11-11 21:00:00",
     "banca": 101.94
    },
    {
     "fixtureId": 900009,
     "pitazo": "2026-11-12 01:00:00",
     "banca": 101.94
    }
   ]
  },
  {
   "clave": "kellyCuarto",
   "nombre": "Kelly ¼",
   "descripcion": "un cuarto de la fracción de Kelly",
   "banca": 100.97,
   "ganancia": 0.97,
   "apostado": 3.97,
   "apuestas": 5,
   "ganadas": 2,
   "roi": 0.2451,
   "caidaMaxima": 0.0109,
   "quebro": null,
   "exposicionMaxima": 2.69,
   "montoMaximo": 1.68,
   "lineas": null,
   "tramos": null,
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
    },
    {
     "fixtureId": 900006,
     "pitazo": "2026-10-29 20:00:00",
     "banca": 101.07
    },
    {
     "fixtureId": 900007,
     "pitazo": "2026-11-11 19:00:00",
     "banca": 101.07
    },
    {
     "fixtureId": 900008,
     "pitazo": "2026-11-11 21:00:00",
     "banca": 100.97
    },
    {
     "fixtureId": 900009,
     "pitazo": "2026-11-12 01:00:00",
     "banca": 100.97
    }
   ]
  },
  {
   "clave": "martingala",
   "nombre": "Martingala",
   "descripcion": "por líneas: cada línea va 1 unidad a nuestro elegido, se duplica tras perder y vuelve a 1 al ganar; con todas en juego se abre otra",
   "banca": 103.28,
   "ganancia": 3.28,
   "apostado": 13.0,
   "apuestas": 9,
   "ganadas": 5,
   "roi": 0.2523,
   "caidaMaxima": 0.0198,
   "quebro": null,
   "exposicionMaxima": 5.0,
   "montoMaximo": 4.0,
   "lineas": {
    "abiertas": 2,
    "perdiendo": 2,
    "proximoMayor": 2.0
   },
   "tramos": null,
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
    },
    {
     "fixtureId": 900006,
     "pitazo": "2026-10-29 20:00:00",
     "banca": 104.6
    },
    {
     "fixtureId": 900007,
     "pitazo": "2026-11-11 19:00:00",
     "banca": 105.28
    },
    {
     "fixtureId": 900008,
     "pitazo": "2026-11-11 21:00:00",
     "banca": 104.28
    },
    {
     "fixtureId": 900009,
     "pitazo": "2026-11-12 01:00:00",
     "banca": 103.28
    }
   ]
  },
  {
   "clave": "martingala60",
   "nombre": "Martingala 60 %+",
   "descripcion": "la misma martingala por líneas, solo cuando nuestro elegido tiene 60 % o más",
   "banca": 99.5,
   "ganancia": -0.5,
   "apostado": 4.0,
   "apuestas": 3,
   "ganadas": 1,
   "roi": -0.125,
   "caidaMaxima": 0.01,
   "quebro": null,
   "exposicionMaxima": 2.0,
   "montoMaximo": 2.0,
   "lineas": {
    "abiertas": 1,
    "perdiendo": 1,
    "proximoMayor": 2.0
   },
   "tramos": null,
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
    },
    {
     "fixtureId": 900006,
     "pitazo": "2026-10-29 20:00:00",
     "banca": 100.5
    },
    {
     "fixtureId": 900007,
     "pitazo": "2026-11-11 19:00:00",
     "banca": 100.5
    },
    {
     "fixtureId": 900008,
     "pitazo": "2026-11-11 21:00:00",
     "banca": 99.5
    },
    {
     "fixtureId": 900009,
     "pitazo": "2026-11-12 01:00:00",
     "banca": 99.5
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
    "proporcional": {
     "apostado": 2.0,
     "ganancia": 0.05,
     "apuestas": 2,
     "roi": 0.025
    },
    "metodoVerde": {
     "apostado": 1.0,
     "ganancia": 1.05,
     "apuestas": 1,
     "roi": 1.05
    },
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
   "partidos": 4,
   "aciertos": 3,
   "estrategias": {
    "proporcional": {
     "apostado": 4.002,
     "ganancia": 1.951,
     "apuestas": 4,
     "roi": 0.4875
    },
    "metodoVerde": {
     "apostado": 1.0105,
     "ganancia": -1.0105,
     "apuestas": 1,
     "roi": -1.0
    },
    "plana": {
     "apostado": 4.0,
     "ganancia": 1.95,
     "apuestas": 4,
     "roi": 0.4875
    },
    "plana60": {
     "apostado": 1.0,
     "ganancia": 0.75,
     "apuestas": 1,
     "roi": 0.75
    },
    "kelly": {
     "apostado": 14.9862,
     "ganancia": 5.0042,
     "apuestas": 3,
     "roi": 0.3339
    },
    "kellyMedio": {
     "apostado": 7.4136,
     "ganancia": 2.501,
     "apuestas": 3,
     "roi": 0.3374
    },
    "kellyCuarto": {
     "apostado": 3.6867,
     "ganancia": 1.2502,
     "apuestas": 3,
     "roi": 0.3391
    },
    "martingala": {
     "apostado": 8.0,
     "ganancia": 4.55,
     "apuestas": 4,
     "roi": 0.5687
    },
    "martingala60": {
     "apostado": 2.0,
     "ganancia": 1.5,
     "apuestas": 1,
     "roi": 0.75
    }
   }
  },
  {
   "version": "v4.5",
   "partidos": 3,
   "aciertos": 1,
   "estrategias": {
    "proporcional": {
     "apostado": 3.0636,
     "ganancia": -1.35,
     "apuestas": 3,
     "roi": -0.4407
    },
    "metodoVerde": {
     "apostado": 2.0076,
     "ganancia": -0.3269,
     "apuestas": 2,
     "roi": -0.1628
    },
    "plana": {
     "apostado": 3.0,
     "ganancia": -1.32,
     "apuestas": 3,
     "roi": -0.44
    },
    "plana60": {
     "apostado": 1.0,
     "ganancia": -1.0,
     "apuestas": 1,
     "roi": -1.0
    },
    "kelly": {
     "apostado": 0.4172,
     "ganancia": -0.4172,
     "apuestas": 1,
     "roi": -1.0
    },
    "kellyMedio": {
     "apostado": 0.2043,
     "ganancia": -0.2043,
     "apuestas": 1,
     "roi": -1.0
    },
    "kellyCuarto": {
     "apostado": 0.1011,
     "ganancia": -0.1011,
     "apuestas": 1,
     "roi": -1.0
    },
    "martingala": {
     "apostado": 3.0,
     "ganancia": -1.32,
     "apuestas": 3,
     "roi": -0.44
    },
    "martingala60": {
     "apostado": 1.0,
     "ganancia": -1.0,
     "apuestas": 1,
     "roi": -1.0
    }
   }
  }
 ],
 "alertaConfianza": {
  "desde": "2026-11-10 05:00:00",
  "sobreCasa": 2.0,
  "conAlerta": {
   "n": 0,
   "aciertos": 0,
   "tasa": null,
   "pide": null,
   "roiPlano": null,
   "dobleOportunidad": null,
   "intervalo": null
  },
  "sinAlerta": {
   "n": 0,
   "aciertos": 0,
   "tasa": null,
   "pide": null,
   "roiPlano": null,
   "dobleOportunidad": null,
   "intervalo": null
  },
  "porMotivo": {},
  "descarte": null,
  "nota": "la alerta no cambia el elegido ni ninguna estrategia: se registra por apuesta desde el 10/11/2026 y se mide hacia adelante (docs/revisiones/ESTUDIO_ECHADOS_2026-11.md). Con 100+ partidos con alerta se decide si frena la carga del método"
 },
 "semaforo": {
  "desde": "2026-11-11 05:00:00",
  "umbral": 2.0,
  "todo": {
   "verde": {
    "n": 4,
    "aciertos": 2,
    "tasa": 0.5,
    "intervalo": [
     0.15,
     0.85
    ],
    "pide": 0.5781,
    "ventaja": -0.0781,
    "roiPlano": -0.0675
   },
   "amarillo": {
    "n": 5,
    "aciertos": 3,
    "tasa": 0.6,
    "intervalo": [
     0.2307,
     0.8824
    ],
    "pide": 0.5056,
    "ventaja": 0.0944,
    "roiPlano": 0.19
   },
   "sinDato": {
    "n": 0,
    "aciertos": 0,
    "tasa": null,
    "intervalo": null,
    "pide": null,
    "ventaja": null,
    "roiPlano": null
   }
  },
  "nuevo": {
   "verde": {
    "n": 2,
    "aciertos": 1,
    "tasa": 0.5,
    "intervalo": [
     0.0945,
     0.9055
    ],
    "pide": 0.6266,
    "ventaja": -0.1266,
    "roiPlano": -0.16
   },
   "amarillo": {
    "n": 1,
    "aciertos": 0,
    "tasa": 0.0,
    "intervalo": [
     0.0,
     0.7935
    ],
    "pide": 0.3846,
    "ventaja": -0.3846,
    "roiPlano": -1.0
   },
   "sinDato": {
    "n": 0,
    "aciertos": 0,
    "tasa": null,
    "intervalo": null,
    "pide": null,
    "ventaja": null,
    "roiPlano": null
   }
  },
  "criterio": {
   "nMinimo": 150,
   "ventajaMinima": 0.05,
   "n": 2,
   "faltan": 148,
   "intervaloSobreLaCuota": false,
   "amarillosDebajo": true,
   "cumple": false,
   "estado": "en_observacion",
   "texto": "en observación: 2 de 150 verdes nuevos, el elegido acierta 50.0 % contra 62.7 % que pedía la cuota (-12.7 pts)"
  },
  "nota": "verde = nuestro 1X2 a ≤ 2 pts de la casa (sin margen) en los tres resultados y el marcador declarado con el elegido; amarillo = falla una. Calculado, nunca declarado, y fuera de la vista del analista (no va al recibo ni a un endpoint del token de Cowork). El criterio cuenta solo los partidos desde el 11/11/2026"
 },
 "apuestas": [
  {
   "fixtureId": 900011,
   "pitazo": "2026-11-12 20:00:00",
   "partido": {
    "local": "Napoli",
    "visita": "Roma",
    "liga": "Serie A"
   },
   "depositadoEn": "2026-11-12 10:30:00",
   "versiones": {
    "sad-analysis": "v4.5",
    "efe-clasificador": "v1.10",
    "teorema-del-echado": "v0.1.26",
    "diagnostico-tactico": "v1.8"
   },
   "versionPrompt": "v2.5",
   "probabilidades": {
    "local": 47.0,
    "empate": 28.0,
    "visita": 25.0
   },
   "cuotas": {
    "local": 2.05,
    "empate": 3.35,
    "visita": 3.9
   },
   "mercado": {
    "local": 46.4,
    "empate": 28.4,
    "visita": 24.4
   },
   "resultado": null,
   "semaforo": {
    "estado": "confirma",
    "motivos": [],
    "elegido": "local",
    "distancia": 0.6,
    "marcadorSigno": "local",
    "umbral": 2.0
   },
   "elegido": "local",
   "kelly": {
    "seleccion": "visita",
    "fraccion": -0.0086,
    "valor": -0.025
   },
   "estado": "pendiente",
   "porEstrategia": {
    "proporcional": {
     "seleccion": "local",
     "monto": 1.0065,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": ""
    },
    "metodoVerde": {
     "seleccion": "local",
     "monto": 0.9971,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": ""
    },
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
     "seleccion": null,
     "monto": 0.0,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "kellyMedio": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "kellyCuarto": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "martingala": {
     "seleccion": "local",
     "monto": 2.0,
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
   "fixtureId": 900009,
   "pitazo": "2026-11-12 01:00:00",
   "partido": {
    "local": "Alianza Lima",
    "visita": "Universitario",
    "liga": "Liga 1"
   },
   "depositadoEn": "2026-11-11 15:40:00",
   "versiones": {
    "sad-analysis": "v4.5",
    "efe-clasificador": "v1.10",
    "teorema-del-echado": "v0.1.26",
    "diagnostico-tactico": "v1.8"
   },
   "versionPrompt": "v2.5",
   "probabilidades": {
    "local": 38.0,
    "empate": 31.0,
    "visita": 31.0
   },
   "cuotas": {
    "local": 2.6,
    "empate": 3.0,
    "visita": 3.0
   },
   "mercado": {
    "local": 35.9,
    "empate": 32.0,
    "visita": 32.1
   },
   "resultado": "visita",
   "semaforo": {
    "estado": "duda",
    "motivos": [
     {
      "codigo": "LEJOS-DE-LA-CASA",
      "detalle": "en local le damos 38.0 % y la casa 35.9 % (+2.1 pts; el verde pide ≤ 2 en los tres)"
     }
    ],
    "elegido": "local",
    "distancia": 2.1,
    "marcadorSigno": "local",
    "umbral": 2.0
   },
   "elegido": "local",
   "kelly": {
    "seleccion": "local",
    "fraccion": -0.0075,
    "valor": -0.012
   },
   "estado": "cerrada",
   "porEstrategia": {
    "proporcional": {
     "seleccion": "local",
     "monto": 1.0167,
     "ganancia": -1.0167,
     "banca": 100.65,
     "linea": null,
     "motivo": ""
    },
    "metodoVerde": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.71,
     "linea": null,
     "motivo": "semáforo en amarillo"
    },
    "plana": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 100.68,
     "linea": null,
     "motivo": ""
    },
    "plana60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 98.75,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "kelly": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 103.88,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "kellyMedio": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 101.94,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "kellyCuarto": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.97,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "martingala": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 103.28,
     "linea": 1,
     "motivo": ""
    },
    "martingala60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.5,
     "linea": null,
     "motivo": "bajo 60 %"
    }
   }
  },
  {
   "fixtureId": 900008,
   "pitazo": "2026-11-11 21:00:00",
   "partido": {
    "local": "PSG",
    "visita": "Marseille",
    "liga": "Ligue 1"
   },
   "depositadoEn": "2026-11-11 12:20:00",
   "versiones": {
    "sad-analysis": "v4.5",
    "efe-clasificador": "v1.10",
    "teorema-del-echado": "v0.1.26",
    "diagnostico-tactico": "v1.8"
   },
   "versionPrompt": "v2.5",
   "probabilidades": {
    "local": 63.0,
    "empate": 20.0,
    "visita": 17.0
   },
   "cuotas": {
    "local": 1.52,
    "empate": 4.4,
    "visita": 6.0
   },
   "mercado": {
    "local": 63.4,
    "empate": 21.3,
    "visita": 15.3
   },
   "resultado": "empate",
   "semaforo": {
    "estado": "confirma",
    "motivos": [],
    "elegido": "local",
    "distancia": 1.7,
    "marcadorSigno": "local",
    "umbral": 2.0
   },
   "elegido": "local",
   "kelly": {
    "seleccion": "visita",
    "fraccion": 0.004,
    "valor": 0.02
   },
   "estado": "cerrada",
   "porEstrategia": {
    "proporcional": {
     "seleccion": "local",
     "monto": 1.0269,
     "ganancia": -1.0269,
     "banca": 101.67,
     "linea": null,
     "motivo": ""
    },
    "metodoVerde": {
     "seleccion": "local",
     "monto": 1.0072,
     "ganancia": -1.0072,
     "banca": 99.71,
     "linea": null,
     "motivo": ""
    },
    "plana": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 101.68,
     "linea": null,
     "motivo": ""
    },
    "plana60": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 98.75,
     "linea": null,
     "motivo": ""
    },
    "kelly": {
     "seleccion": "visita",
     "monto": 0.4172,
     "ganancia": -0.4172,
     "banca": 103.88,
     "linea": null,
     "motivo": ""
    },
    "kellyMedio": {
     "seleccion": "visita",
     "monto": 0.2043,
     "ganancia": -0.2043,
     "banca": 101.94,
     "linea": null,
     "motivo": ""
    },
    "kellyCuarto": {
     "seleccion": "visita",
     "monto": 0.1011,
     "ganancia": -0.1011,
     "banca": 100.97,
     "linea": null,
     "motivo": ""
    },
    "martingala": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 104.28,
     "linea": 2,
     "motivo": ""
    },
    "martingala60": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 99.5,
     "linea": 1,
     "motivo": ""
    }
   }
  },
  {
   "fixtureId": 900007,
   "pitazo": "2026-11-11 19:00:00",
   "partido": {
    "local": "Bayern",
    "visita": "Dortmund",
    "liga": "Bundesliga"
   },
   "depositadoEn": "2026-11-11 12:05:00",
   "versiones": {
    "sad-analysis": "v4.5",
    "efe-clasificador": "v1.10",
    "teorema-del-echado": "v0.1.26",
    "diagnostico-tactico": "v1.8"
   },
   "versionPrompt": "v2.5",
   "probabilidades": {
    "local": 58.0,
    "empate": 22.0,
    "visita": 20.0
   },
   "cuotas": {
    "local": 1.68,
    "empate": 4.2,
    "visita": 4.6
   },
   "mercado": {
    "local": 57.2,
    "empate": 22.9,
    "visita": 19.9
   },
   "resultado": "local",
   "semaforo": {
    "estado": "confirma",
    "motivos": [],
    "elegido": "local",
    "distancia": 0.9,
    "marcadorSigno": "local",
    "umbral": 2.0
   },
   "elegido": "local",
   "kelly": {
    "seleccion": "visita",
    "fraccion": -0.0222,
    "valor": -0.08
   },
   "estado": "cerrada",
   "porEstrategia": {
    "proporcional": {
     "seleccion": "local",
     "monto": 1.02,
     "ganancia": 0.6936,
     "banca": 102.69,
     "linea": null,
     "motivo": ""
    },
    "metodoVerde": {
     "seleccion": "local",
     "monto": 1.0004,
     "ganancia": 0.6803,
     "banca": 100.72,
     "linea": null,
     "motivo": ""
    },
    "plana": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 0.68,
     "banca": 102.68,
     "linea": null,
     "motivo": ""
    },
    "plana60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.75,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "kelly": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 104.29,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "kellyMedio": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 102.15,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "kellyCuarto": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 101.07,
     "linea": null,
     "motivo": "sin ventaja"
    },
    "martingala": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 0.68,
     "banca": 105.28,
     "linea": 1,
     "motivo": ""
    },
    "martingala60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.5,
     "linea": null,
     "motivo": "bajo 60 %"
    }
   }
  },
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
   "resultado": "local",
   "semaforo": {
    "estado": "duda",
    "motivos": [
     {
      "codigo": "LEJOS-DE-LA-CASA",
      "detalle": "en visita le damos 34.0 % y la casa 30.1 % (+3.9 pts; el verde pide ≤ 2 en los tres)"
     },
     {
      "codigo": "MARCADOR-CONTRADICE",
      "detalle": "el marcador 2-2 dice empate y el elegido es local"
     }
    ],
    "elegido": "local",
    "distancia": 3.9,
    "marcadorSigno": "empate",
    "umbral": 2.0
   },
   "elegido": "local",
   "kelly": {
    "seleccion": "visita",
    "fraccion": 0.04,
    "valor": 0.088
   },
   "estado": "cerrada",
   "porEstrategia": {
    "proporcional": {
     "seleccion": "local",
     "monto": 1.0005,
     "ganancia": 1.2006,
     "banca": 102.0,
     "linea": null,
     "motivo": ""
    },
    "metodoVerde": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.04,
     "linea": null,
     "motivo": "semáforo en amarillo"
    },
    "plana": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 1.2,
     "banca": 102.0,
     "linea": null,
     "motivo": ""
    },
    "plana60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.75,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "kelly": {
     "seleccion": "visita",
     "monto": 4.1305,
     "ganancia": -4.1305,
     "banca": 104.29,
     "linea": null,
     "motivo": ""
    },
    "kellyMedio": {
     "seleccion": "visita",
     "monto": 2.0328,
     "ganancia": -2.0328,
     "banca": 102.15,
     "linea": null,
     "motivo": ""
    },
    "kellyCuarto": {
     "seleccion": "visita",
     "monto": 1.0082,
     "ganancia": -1.0082,
     "banca": 101.07,
     "linea": null,
     "motivo": ""
    },
    "martingala": {
     "seleccion": "local",
     "monto": 4.0,
     "ganancia": 4.8,
     "banca": 104.6,
     "linea": 2,
     "motivo": ""
    },
    "martingala60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.5,
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
   "semaforo": {
    "estado": "duda",
    "motivos": [
     {
      "codigo": "LEJOS-DE-LA-CASA",
      "detalle": "en local le damos 60.0 % y la casa 54.7 % (+5.3 pts; el verde pide ≤ 2 en los tres)"
     }
    ],
    "elegido": "local",
    "distancia": 5.3,
    "marcadorSigno": "local",
    "umbral": 2.0
   },
   "elegido": "local",
   "kelly": {
    "seleccion": "local",
    "fraccion": 0.0667,
    "valor": 0.05
   },
   "estado": "cerrada",
   "porEstrategia": {
    "proporcional": {
     "seleccion": "local",
     "monto": 1.0005,
     "ganancia": 0.7504,
     "banca": 100.8,
     "linea": null,
     "motivo": ""
    },
    "metodoVerde": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.04,
     "linea": null,
     "motivo": "semáforo en amarillo"
    },
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
   "semaforo": {
    "estado": "confirma",
    "motivos": [],
    "elegido": "local",
    "distancia": 1.2,
    "marcadorSigno": "local",
    "umbral": 2.0
   },
   "elegido": "local",
   "kelly": {
    "seleccion": "empate",
    "fraccion": -0.0004,
    "valor": -0.001
   },
   "estado": "cerrada",
   "porEstrategia": {
    "proporcional": {
     "seleccion": "local",
     "monto": 1.0005,
     "ganancia": -1.0005,
     "banca": 100.05,
     "linea": null,
     "motivo": ""
    },
    "metodoVerde": {
     "seleccion": "local",
     "monto": 1.0105,
     "ganancia": -1.0105,
     "banca": 100.04,
     "linea": null,
     "motivo": ""
    },
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
   "semaforo": {
    "estado": "duda",
    "motivos": [
     {
      "codigo": "LEJOS-DE-LA-CASA",
      "detalle": "en local le damos 52.0 % y la casa 48.3 % (+3.7 pts; el verde pide ≤ 2 en los tres)"
     },
     {
      "codigo": "MARCADOR-CONTRADICE",
      "detalle": "el marcador 1-1 dice empate y el elegido es local"
     }
    ],
    "elegido": "local",
    "distancia": 3.7,
    "marcadorSigno": "empate",
    "umbral": 2.0
   },
   "elegido": "local",
   "kelly": {
    "seleccion": "local",
    "fraccion": 0.04,
    "valor": 0.04
   },
   "estado": "cerrada",
   "porEstrategia": {
    "proporcional": {
     "seleccion": "local",
     "monto": 1.0005,
     "ganancia": 1.0005,
     "banca": 101.05,
     "linea": null,
     "motivo": ""
    },
    "metodoVerde": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 101.05,
     "linea": null,
     "motivo": "semáforo en amarillo"
    },
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
   "semaforo": {
    "estado": "duda",
    "motivos": [
     {
      "codigo": "LEJOS-DE-LA-CASA",
      "detalle": "en local le damos 62.0 % y la casa 59.0 % (+3.0 pts; el verde pide ≤ 2 en los tres)"
     }
    ],
    "elegido": "local",
    "distancia": 3.0,
    "marcadorSigno": "local",
    "umbral": 2.0
   },
   "elegido": "local",
   "kelly": {
    "seleccion": "local",
    "fraccion": 0.0071,
    "valor": 0.0044
   },
   "estado": "cerrada",
   "porEstrategia": {
    "proporcional": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 100.05,
     "linea": null,
     "motivo": ""
    },
    "metodoVerde": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 101.05,
     "linea": null,
     "motivo": "semáforo en amarillo"
    },
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
   "semaforo": {
    "estado": "confirma",
    "motivos": [],
    "elegido": "local",
    "distancia": 1.0,
    "marcadorSigno": "local",
    "umbral": 2.0
   },
   "elegido": "local",
   "kelly": {
    "seleccion": "local",
    "fraccion": -0.0152,
    "valor": -0.016
   },
   "estado": "cerrada",
   "porEstrategia": {
    "proporcional": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 1.05,
     "banca": 101.05,
     "linea": null,
     "motivo": ""
    },
    "metodoVerde": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 1.05,
     "banca": 101.05,
     "linea": null,
     "motivo": ""
    },
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
