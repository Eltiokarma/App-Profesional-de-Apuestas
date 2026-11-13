// Generado con backend.analisis.simulacion.simular sobre apuestas inventadas:
// la demo usa la MISMA cuenta que el backend (no una copia en TS).
// Se rehace con: python scripts/generar_simulacion_demo.py
import type { SimulacionApuesta } from '../api/types'

export const SIMULACION_DEMO: SimulacionApuesta = {
 "trasFallos": {
  "base": {
   "n": 11,
   "aciertos": 6,
   "tasa": 0.5455,
   "intervalo": [
    0.2801,
    0.7873
   ]
  },
  "porK": [
   {
    "k": 1,
    "n": 4,
    "aciertos": 3,
    "tasa": 0.75,
    "intervalo": [
     0.3006,
     0.9544
    ]
   },
   {
    "k": 2,
    "n": 1,
    "aciertos": 1,
    "tasa": 1.0,
    "intervalo": [
     0.2065,
     1.0
    ]
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
 "cerradas": 11,
 "pendientes": 1,
 "aciertos": 6,
 "estrategias": [
  {
   "clave": "proporcional",
   "nombre": "Proporcional con freno",
   "descripcion": "1 % de la banca a nuestro elegido; un tramo de confianza se pausa si en sus últimos 50 partidos acertó menos de lo que pedía la cuota, y vuelve cuando se recupera",
   "banca": 100.75,
   "ganancia": 0.75,
   "apostado": 11.08,
   "apuestas": 11,
   "ganadas": 6,
   "roi": 0.0678,
   "caidaMaxima": 0.0199,
   "quebro": null,
   "exposicionMaxima": 3.02,
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
     "n": 3,
     "aciertos": 3,
     "tasa": 1.0,
     "pide": 0.4728,
     "z": 1.83,
     "pausado": false
    },
    {
     "tramo": "50-59",
     "n": 4,
     "aciertos": 2,
     "tasa": 0.5,
     "pide": 0.5449,
     "z": -0.18,
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
    },
    {
     "fixtureId": 900012,
     "pitazo": "2026-11-13 19:45:00",
     "banca": 101.76
    },
    {
     "fixtureId": 900013,
     "pitazo": "2026-11-13 21:00:00",
     "banca": 100.75
    }
   ]
  },
  {
   "clave": "metodoVerde",
   "nombre": "Método solo en verde",
   "descripcion": "el método (1 % de la banca y el mismo freno por tramo) apostando solo cuando el semáforo del elegido está en verde: la espina del elegido lo acompaña y la del rival no dice que siga",
   "banca": 103.62,
   "ganancia": 3.62,
   "apostado": 6.12,
   "apuestas": 6,
   "ganadas": 5,
   "roi": 0.5911,
   "caidaMaxima": 0.01,
   "quebro": null,
   "exposicionMaxima": 2.05,
   "montoMaximo": 1.04,
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
     "n": 3,
     "aciertos": 3,
     "tasa": 1.0,
     "pide": 0.4728,
     "z": 1.83,
     "pausado": false
    },
    {
     "tramo": "50-59",
     "n": 4,
     "aciertos": 2,
     "tasa": 0.5,
     "pide": 0.5449,
     "z": -0.18,
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
     "banca": 102.06
    },
    {
     "fixtureId": 900004,
     "pitazo": "2026-10-28 20:00:00",
     "banca": 102.06
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 102.83
    },
    {
     "fixtureId": 900006,
     "pitazo": "2026-10-29 20:00:00",
     "banca": 102.83
    },
    {
     "fixtureId": 900007,
     "pitazo": "2026-11-11 19:00:00",
     "banca": 103.53
    },
    {
     "fixtureId": 900008,
     "pitazo": "2026-11-11 21:00:00",
     "banca": 102.49
    },
    {
     "fixtureId": 900009,
     "pitazo": "2026-11-12 01:00:00",
     "banca": 102.49
    },
    {
     "fixtureId": 900012,
     "pitazo": "2026-11-13 19:45:00",
     "banca": 103.62
    },
    {
     "fixtureId": 900013,
     "pitazo": "2026-11-13 21:00:00",
     "banca": 103.62
    }
   ]
  },
  {
   "clave": "metodoMarcador",
   "nombre": "Método con el marcador",
   "descripcion": "el método (1 % de la banca y el mismo freno por tramo) apostando solo cuando el marcador más probable del modelo de goles va con el elegido (1-0 o 2-1 para el local, 0-1 para la visita)",
   "banca": 99.5,
   "ganancia": -0.5,
   "apostado": 5.94,
   "apuestas": 6,
   "ganadas": 3,
   "roi": -0.0834,
   "caidaMaxima": 0.0199,
   "quebro": null,
   "exposicionMaxima": 1.0,
   "montoMaximo": 1.0,
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
     "n": 3,
     "aciertos": 3,
     "tasa": 1.0,
     "pide": 0.4728,
     "z": 1.83,
     "pausado": false
    },
    {
     "tramo": "50-59",
     "n": 4,
     "aciertos": 2,
     "tasa": 0.5,
     "pide": 0.5449,
     "z": -0.18,
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
     "banca": 98.01
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 98.75
    },
    {
     "fixtureId": 900006,
     "pitazo": "2026-10-29 20:00:00",
     "banca": 98.75
    },
    {
     "fixtureId": 900007,
     "pitazo": "2026-11-11 19:00:00",
     "banca": 99.42
    },
    {
     "fixtureId": 900008,
     "pitazo": "2026-11-11 21:00:00",
     "banca": 98.42
    },
    {
     "fixtureId": 900009,
     "pitazo": "2026-11-12 01:00:00",
     "banca": 98.42
    },
    {
     "fixtureId": 900012,
     "pitazo": "2026-11-13 19:45:00",
     "banca": 99.5
    },
    {
     "fixtureId": 900013,
     "pitazo": "2026-11-13 21:00:00",
     "banca": 99.5
    }
   ]
  },
  {
   "clave": "metodoVerdeMarcador",
   "nombre": "Método en verde con el marcador",
   "descripcion": "el método (1 % de la banca y el mismo freno) solo con el semáforo en verde Y el marcador más probable con el elegido",
   "banca": 101.53,
   "ganancia": 1.53,
   "apostado": 4.03,
   "apuestas": 4,
   "ganadas": 3,
   "roi": 0.3789,
   "caidaMaxima": 0.01,
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
     "n": 3,
     "aciertos": 3,
     "tasa": 1.0,
     "pide": 0.4728,
     "z": 1.83,
     "pausado": false
    },
    {
     "tramo": "50-59",
     "n": 4,
     "aciertos": 2,
     "tasa": 0.5,
     "pide": 0.5449,
     "z": -0.18,
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
     "banca": 100.0
    },
    {
     "fixtureId": 900002,
     "pitazo": "2026-10-28 15:00:00",
     "banca": 100.0
    },
    {
     "fixtureId": 900003,
     "pitazo": "2026-10-28 19:45:00",
     "banca": 100.0
    },
    {
     "fixtureId": 900004,
     "pitazo": "2026-10-28 20:00:00",
     "banca": 100.0
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 100.75
    },
    {
     "fixtureId": 900006,
     "pitazo": "2026-10-29 20:00:00",
     "banca": 100.75
    },
    {
     "fixtureId": 900007,
     "pitazo": "2026-11-11 19:00:00",
     "banca": 101.44
    },
    {
     "fixtureId": 900008,
     "pitazo": "2026-11-11 21:00:00",
     "banca": 100.42
    },
    {
     "fixtureId": 900009,
     "pitazo": "2026-11-12 01:00:00",
     "banca": 100.42
    },
    {
     "fixtureId": 900012,
     "pitazo": "2026-11-13 19:45:00",
     "banca": 101.53
    },
    {
     "fixtureId": 900013,
     "pitazo": "2026-11-13 21:00:00",
     "banca": 101.53
    }
   ]
  },
  {
   "clave": "plana",
   "nombre": "Apuesta plana (control)",
   "descripcion": "1 unidad a nuestro elegido en cada partido",
   "banca": 100.78,
   "ganancia": 0.78,
   "apostado": 11.0,
   "apuestas": 11,
   "ganadas": 6,
   "roi": 0.0709,
   "caidaMaxima": 0.0195,
   "quebro": null,
   "exposicionMaxima": 3.0,
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
    },
    {
     "fixtureId": 900012,
     "pitazo": "2026-11-13 19:45:00",
     "banca": 101.78
    },
    {
     "fixtureId": 900013,
     "pitazo": "2026-11-13 21:00:00",
     "banca": 100.78
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
    },
    {
     "fixtureId": 900012,
     "pitazo": "2026-11-13 19:45:00",
     "banca": 98.75
    },
    {
     "fixtureId": 900013,
     "pitazo": "2026-11-13 21:00:00",
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
    },
    {
     "fixtureId": 900012,
     "pitazo": "2026-11-13 19:45:00",
     "banca": 103.88
    },
    {
     "fixtureId": 900013,
     "pitazo": "2026-11-13 21:00:00",
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
    },
    {
     "fixtureId": 900012,
     "pitazo": "2026-11-13 19:45:00",
     "banca": 101.94
    },
    {
     "fixtureId": 900013,
     "pitazo": "2026-11-13 21:00:00",
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
    },
    {
     "fixtureId": 900012,
     "pitazo": "2026-11-13 19:45:00",
     "banca": 100.97
    },
    {
     "fixtureId": 900013,
     "pitazo": "2026-11-13 21:00:00",
     "banca": 100.97
    }
   ]
  },
  {
   "clave": "martingala",
   "nombre": "Martingala",
   "descripcion": "por líneas: cada línea va 1 unidad a nuestro elegido, se duplica tras perder y vuelve a 1 al ganar; con todas en juego se abre otra",
   "banca": 104.48,
   "ganancia": 4.48,
   "apostado": 16.0,
   "apuestas": 11,
   "ganadas": 6,
   "roi": 0.28,
   "caidaMaxima": 0.0198,
   "quebro": null,
   "exposicionMaxima": 5.0,
   "montoMaximo": 4.0,
   "lineas": {
    "abiertas": 3,
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
    },
    {
     "fixtureId": 900012,
     "pitazo": "2026-11-13 19:45:00",
     "banca": 105.48
    },
    {
     "fixtureId": 900013,
     "pitazo": "2026-11-13 21:00:00",
     "banca": 104.48
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
    },
    {
     "fixtureId": 900012,
     "pitazo": "2026-11-13 19:45:00",
     "banca": 99.5
    },
    {
     "fixtureId": 900013,
     "pitazo": "2026-11-13 21:00:00",
     "banca": 99.5
    }
   ]
  },
  {
   "clave": "martingala60Ajustada",
   "nombre": "Martingala 60 %+ ajustada",
   "descripcion": "por líneas, solo con nuestro elegido a 60 % o más; tras perder apuesta 1 + lo perdido en la línea / (cuota − 1): recupera todo y gana lo de 1 u, con cualquier cuota",
   "banca": 99.75,
   "ganancia": -0.25,
   "apostado": 4.33,
   "apuestas": 3,
   "ganadas": 1,
   "roi": -0.0577,
   "caidaMaxima": 0.01,
   "quebro": null,
   "exposicionMaxima": 2.33,
   "montoMaximo": 2.33,
   "lineas": {
    "abiertas": 1,
    "perdiendo": 1,
    "proximoMayor": 1.0,
    "perdidaMayor": 1.0
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
     "banca": 100.75
    },
    {
     "fixtureId": 900006,
     "pitazo": "2026-10-29 20:00:00",
     "banca": 100.75
    },
    {
     "fixtureId": 900007,
     "pitazo": "2026-11-11 19:00:00",
     "banca": 100.75
    },
    {
     "fixtureId": 900008,
     "pitazo": "2026-11-11 21:00:00",
     "banca": 99.75
    },
    {
     "fixtureId": 900009,
     "pitazo": "2026-11-12 01:00:00",
     "banca": 99.75
    },
    {
     "fixtureId": 900012,
     "pitazo": "2026-11-13 19:45:00",
     "banca": 99.75
    },
    {
     "fixtureId": 900013,
     "pitazo": "2026-11-13 21:00:00",
     "banca": 99.75
    }
   ]
  },
  {
   "clave": "martingalaAjustadaVerdeMarcador",
   "nombre": "Martingala 🟢⚽ ajustada",
   "descripcion": "la martingala ajustada a la cuota, solo con el semáforo en verde Y el marcador más probable con el elegido",
   "banca": 102.53,
   "ganancia": 2.53,
   "apostado": 4.91,
   "apuestas": 4,
   "ganadas": 3,
   "roi": 0.5154,
   "caidaMaxima": 0.0099,
   "quebro": null,
   "exposicionMaxima": 1.91,
   "montoMaximo": 1.91,
   "lineas": {
    "abiertas": 1,
    "perdiendo": 0,
    "proximoMayor": 1.0,
    "perdidaMayor": 0.0
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
     "banca": 100.0
    },
    {
     "fixtureId": 900003,
     "pitazo": "2026-10-28 19:45:00",
     "banca": 100.0
    },
    {
     "fixtureId": 900004,
     "pitazo": "2026-10-28 20:00:00",
     "banca": 100.0
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 100.75
    },
    {
     "fixtureId": 900006,
     "pitazo": "2026-10-29 20:00:00",
     "banca": 100.75
    },
    {
     "fixtureId": 900007,
     "pitazo": "2026-11-11 19:00:00",
     "banca": 101.43
    },
    {
     "fixtureId": 900008,
     "pitazo": "2026-11-11 21:00:00",
     "banca": 100.43
    },
    {
     "fixtureId": 900009,
     "pitazo": "2026-11-12 01:00:00",
     "banca": 100.43
    },
    {
     "fixtureId": 900012,
     "pitazo": "2026-11-13 19:45:00",
     "banca": 102.53
    },
    {
     "fixtureId": 900013,
     "pitazo": "2026-11-13 21:00:00",
     "banca": 102.53
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
    "metodoMarcador": {
     "apostado": 1.0,
     "ganancia": -1.0,
     "apuestas": 1,
     "roi": -1.0
    },
    "metodoVerdeMarcador": {
     "apostado": 0.0,
     "ganancia": 0.0,
     "apuestas": 0,
     "roi": null
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
    },
    "martingala60Ajustada": {
     "apostado": 1.0,
     "ganancia": -1.0,
     "apuestas": 1,
     "roi": -1.0
    },
    "martingalaAjustadaVerdeMarcador": {
     "apostado": 0.0,
     "ganancia": 0.0,
     "apuestas": 0,
     "roi": null
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
     "apostado": 2.0311,
     "ganancia": 1.7759,
     "apuestas": 2,
     "roi": 0.8744
    },
    "metodoMarcador": {
     "apostado": 1.9701,
     "ganancia": -0.2549,
     "apuestas": 2,
     "roi": -0.1294
    },
    "metodoVerdeMarcador": {
     "apostado": 1.0,
     "ganancia": 0.75,
     "apuestas": 1,
     "roi": 0.75
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
    },
    "martingala60Ajustada": {
     "apostado": 2.3333,
     "ganancia": 1.75,
     "apuestas": 1,
     "roi": 0.75
    },
    "martingalaAjustadaVerdeMarcador": {
     "apostado": 1.0,
     "ganancia": 0.75,
     "apuestas": 1,
     "roi": 0.75
    }
   }
  },
  {
   "version": "v4.5",
   "partidos": 5,
   "aciertos": 2,
   "estrategias": {
    "proporcional": {
     "apostado": 5.0766,
     "ganancia": -1.2493,
     "apuestas": 5,
     "roi": -0.2461
    },
    "metodoVerde": {
     "apostado": 3.0885,
     "ganancia": 0.7913,
     "apuestas": 3,
     "roi": 0.2562
    },
    "metodoMarcador": {
     "apostado": 2.9659,
     "ganancia": 0.7599,
     "apuestas": 3,
     "roi": 0.2562
    },
    "metodoVerdeMarcador": {
     "apostado": 3.0261,
     "ganancia": 0.7753,
     "apuestas": 3,
     "roi": 0.2562
    },
    "plana": {
     "apostado": 5.0,
     "ganancia": -1.22,
     "apuestas": 5,
     "roi": -0.244
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
     "apostado": 6.0,
     "ganancia": -0.12,
     "apuestas": 5,
     "roi": -0.02
    },
    "martingala60": {
     "apostado": 1.0,
     "ganancia": -1.0,
     "apuestas": 1,
     "roi": -1.0
    },
    "martingala60Ajustada": {
     "apostado": 1.0,
     "ganancia": -1.0,
     "apuestas": 1,
     "roi": -1.0
    },
    "martingalaAjustadaVerdeMarcador": {
     "apostado": 3.9091,
     "ganancia": 1.78,
     "apuestas": 3,
     "roi": 0.4553
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
  "desde": "2026-11-13 05:00:00",
  "regla": "espinas",
  "todo": {
   "verde": {
    "n": 6,
    "aciertos": 5,
    "tasa": 0.8333,
    "intervalo": [
     0.4365,
     0.9699
    ],
    "pide": 0.5481,
    "ventaja": 0.2852,
    "roiPlano": 0.5967
   },
   "amarillo": {
    "n": 3,
    "aciertos": 1,
    "tasa": 0.3333,
    "intervalo": [
     0.0615,
     0.7923
    ],
    "pide": 0.5478,
    "ventaja": -0.2144,
    "roiPlano": -0.2667
   },
   "rojo": {
    "n": 2,
    "aciertos": 0,
    "tasa": 0.0,
    "intervalo": [
     0.0,
     0.6576
    ],
    "pide": 0.4487,
    "ventaja": -0.4487,
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
  "nuevo": {
   "verde": {
    "n": 1,
    "aciertos": 1,
    "tasa": 1.0,
    "intervalo": [
     0.2065,
     1.0
    ],
    "pide": 0.4762,
    "ventaja": 0.5238,
    "roiPlano": 1.1
   },
   "amarillo": {
    "n": 0,
    "aciertos": 0,
    "tasa": null,
    "intervalo": null,
    "pide": null,
    "ventaja": null,
    "roiPlano": null
   },
   "rojo": {
    "n": 1,
    "aciertos": 0,
    "tasa": 0.0,
    "intervalo": [
     0.0,
     0.7935
    ],
    "pide": 0.5128,
    "ventaja": -0.5128,
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
   "escalon": 0,
   "proximoEscalon": 30,
   "escalones": [
    30,
    60
   ],
   "faltan": 29,
   "n": 1,
   "verdes": {
    "n": 1,
    "tasa": 1.0
   },
   "noVerdes": {
    "n": 1,
    "tasa": 0.0,
    "intervalo": [
     0.0,
     0.7935
    ]
   },
   "separacion": 1.0,
   "nMinimo": 60,
   "separacionMinima": 0.1,
   "noVerdesDebajo": true,
   "cumple": false,
   "estado": "en_observacion",
   "texto": "en observación: 1 amarillos o rojos nuevos, el elegido gana 100.0 % en verde (1) y 0.0 % en amarillo o rojo (1, IC 0-79 %): +100.0 pts · faltan 29 no-verdes para el escalón 30"
  },
  "nota": "verde = la espina del elegido lo acompaña y la del rival no dice que siga; amarillo = la espina del elegido dice empate o la del rival dice que gana o empata; rojo = la espina del elegido dice que pierde (no apostar). Sale de las espinas del parte, no de la cuota. Calculado, nunca declarado, y fuera de la vista del analista (no va al recibo ni a un endpoint del token de Cowork). El criterio cuenta solo los partidos desde el 13/11/2026"
 },
 "marcador": {
  "desde": "2026-11-14 05:00:00",
  "todo": {
   "alineado": {
    "n": 6,
    "aciertos": 3,
    "tasa": 0.5,
    "intervalo": [
     0.1876,
     0.8124
    ],
    "pide": 0.5816,
    "ventaja": -0.0816,
    "roiPlano": -0.0783
   },
   "resto": {
    "n": 5,
    "aciertos": 3,
    "tasa": 0.6,
    "intervalo": [
     0.2307,
     0.8824
    ],
    "pide": 0.468,
    "ventaja": 0.132,
    "roiPlano": 0.25
   },
   "sinMarcador": {
    "n": 0,
    "aciertos": 0,
    "tasa": null,
    "intervalo": null,
    "pide": null,
    "ventaja": null,
    "roiPlano": null
   },
   "verdeAlineado": {
    "n": 4,
    "aciertos": 3,
    "tasa": 0.75,
    "intervalo": [
     0.3006,
     0.9544
    ],
    "pide": 0.5752,
    "ventaja": 0.1748,
    "roiPlano": 0.3825
   }
  },
  "nuevo": {
   "alineado": {
    "n": 0,
    "aciertos": 0,
    "tasa": null,
    "intervalo": null,
    "pide": null,
    "ventaja": null,
    "roiPlano": null
   },
   "resto": {
    "n": 0,
    "aciertos": 0,
    "tasa": null,
    "intervalo": null,
    "pide": null,
    "ventaja": null,
    "roiPlano": null
   },
   "sinMarcador": {
    "n": 0,
    "aciertos": 0,
    "tasa": null,
    "intervalo": null,
    "pide": null,
    "ventaja": null,
    "roiPlano": null
   },
   "verdeAlineado": {
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
   "escalon": 0,
   "proximoEscalon": 30,
   "escalones": [
    30,
    60
   ],
   "faltan": 30,
   "n": 0,
   "alineados": {
    "n": 0,
    "tasa": null,
    "intervalo": null
   },
   "resto": {
    "n": 0,
    "tasa": null
   },
   "separacion": null,
   "nMinimo": 60,
   "separacionMinima": 0.1,
   "alineadosEncima": false,
   "cumple": false,
   "estado": "en_observacion",
   "texto": "en observación: 0 alineados nuevos · faltan 30 alineados para el escalón 30"
  },
  "nota": "el marcador más probable del modelo de goles (el de la lista de Partidos), con la historia anterior al partido: el mismo al minuto 0. Se juzga el win rate; la cuota es información"
 },
 "apuestas": [
  {
   "fixtureId": 900013,
   "pitazo": "2026-11-13 21:00:00",
   "partido": {
    "local": "Juventus",
    "visita": "Lazio",
    "liga": "Serie A"
   },
   "depositadoEn": "2026-11-13 12:30:00",
   "versiones": {
    "sad-analysis": "v4.5",
    "efe-clasificador": "v1.10",
    "teorema-del-echado": "v0.1.26",
    "diagnostico-tactico": "v1.8"
   },
   "versionPrompt": "v2.5",
   "probabilidades": {
    "local": 50.0,
    "empate": 28.0,
    "visita": 22.0
   },
   "cuotas": {
    "local": 1.95,
    "empate": 3.4,
    "visita": 4.2
   },
   "mercado": {
    "local": 49.5,
    "empate": 28.4,
    "visita": 22.1
   },
   "resultado": "empate",
   "semaforo": {
    "estado": "noApostar",
    "motivos": [
     {
      "codigo": "ESPINA-CONTRA-EL-ELEGIDO",
      "detalle": "la espina del elegido (local) dice que pierde: se lo eligió contra su propia lectura"
     },
     {
      "codigo": "ESPINA-RIVAL-SIGUE",
      "detalle": "la espina del rival dice positiva: que gana"
     }
    ],
    "elegido": "local",
    "regla": "espinas",
    "espinaElegido": "negativa",
    "espinaRival": "positiva",
    "espinas": {
     "a": "negativa",
     "b": "positiva"
    },
    "distancia": 0.5,
    "marcadorSigno": "local"
   },
   "marcador": {
    "masProbable": "1-1",
    "prob": 0.126,
    "signo": "empate",
    "alineado": false
   },
   "elegido": "local",
   "kelly": {
    "seleccion": "empate",
    "fraccion": -0.02,
    "valor": -0.048
   },
   "estado": "cerrada",
   "porEstrategia": {
    "proporcional": {
     "seleccion": "local",
     "monto": 1.0065,
     "ganancia": -1.0065,
     "banca": 100.75,
     "linea": null,
     "motivo": ""
    },
    "metodoVerde": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 103.62,
     "linea": null,
     "motivo": "semáforo en rojo: no apostar"
    },
    "metodoMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.5,
     "linea": null,
     "motivo": "el marcador más probable (1-1) no va con el elegido"
    },
    "metodoVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 101.53,
     "linea": null,
     "motivo": "semáforo no está en verde"
    },
    "plana": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 100.78,
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
     "banca": 104.48,
     "linea": 3,
     "motivo": ""
    },
    "martingala60": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.5,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "martingala60Ajustada": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.75,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "martingalaAjustadaVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 102.53,
     "linea": null,
     "motivo": "semáforo no está en verde"
    }
   }
  },
  {
   "fixtureId": 900012,
   "pitazo": "2026-11-13 19:45:00",
   "partido": {
    "local": "Benfica",
    "visita": "Porto",
    "liga": "Liga Portugal"
   },
   "depositadoEn": "2026-11-13 12:10:00",
   "versiones": {
    "sad-analysis": "v4.5",
    "efe-clasificador": "v1.10",
    "teorema-del-echado": "v0.1.26",
    "diagnostico-tactico": "v1.8"
   },
   "versionPrompt": "v2.5",
   "probabilidades": {
    "local": 46.0,
    "empate": 27.0,
    "visita": 27.0
   },
   "cuotas": {
    "local": 2.1,
    "empate": 3.4,
    "visita": 3.6
   },
   "mercado": {
    "local": 45.6,
    "empate": 28.2,
    "visita": 26.2
   },
   "resultado": "local",
   "semaforo": {
    "estado": "confirma",
    "motivos": [],
    "elegido": "local",
    "regla": "espinas",
    "espinaElegido": "positiva",
    "espinaRival": "negativa",
    "espinas": {
     "a": "positiva",
     "b": "negativa"
    },
    "distancia": 1.2,
    "marcadorSigno": "local"
   },
   "marcador": {
    "masProbable": "1-0",
    "prob": 0.117,
    "signo": "local",
    "alineado": true
   },
   "elegido": "local",
   "kelly": {
    "seleccion": "visita",
    "fraccion": -0.0108,
    "valor": -0.028
   },
   "estado": "cerrada",
   "porEstrategia": {
    "proporcional": {
     "seleccion": "local",
     "monto": 1.0065,
     "ganancia": 1.1072,
     "banca": 101.76,
     "linea": null,
     "motivo": ""
    },
    "metodoVerde": {
     "seleccion": "local",
     "monto": 1.0249,
     "ganancia": 1.1274,
     "banca": 103.62,
     "linea": null,
     "motivo": ""
    },
    "metodoMarcador": {
     "seleccion": "local",
     "monto": 0.9842,
     "ganancia": 1.0826,
     "banca": 99.5,
     "linea": null,
     "motivo": ""
    },
    "metodoVerdeMarcador": {
     "seleccion": "local",
     "monto": 1.0042,
     "ganancia": 1.1046,
     "banca": 101.53,
     "linea": null,
     "motivo": ""
    },
    "plana": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 1.1,
     "banca": 101.78,
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
     "monto": 2.0,
     "ganancia": 2.2,
     "banca": 105.48,
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
    },
    "martingala60Ajustada": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.75,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "martingalaAjustadaVerdeMarcador": {
     "seleccion": "local",
     "monto": 1.9091,
     "ganancia": 2.1,
     "banca": 102.53,
     "linea": 1,
     "motivo": ""
    }
   }
  },
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
    "regla": "espinas",
    "espinaElegido": "positiva",
    "espinaRival": "negativa",
    "espinas": {
     "a": "positiva",
     "b": "negativa"
    },
    "distancia": 0.6,
    "marcadorSigno": "local"
   },
   "marcador": {
    "masProbable": "1-1",
    "prob": 0.122,
    "signo": "empate",
    "alineado": false
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
     "monto": 1.0249,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": ""
    },
    "metodoMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": "el marcador más probable (1-1) no va con el elegido"
    },
    "metodoVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": "el marcador más probable (1-1) no va con el elegido"
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
    },
    "martingala60Ajustada": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "martingalaAjustadaVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": null,
     "banca": null,
     "linea": null,
     "motivo": "el marcador más probable (1-1) no va con el elegido"
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
    "estado": "noApostar",
    "motivos": [
     {
      "codigo": "ESPINA-CONTRA-EL-ELEGIDO",
      "detalle": "la espina del elegido (local) dice que pierde: se lo eligió contra su propia lectura"
     },
     {
      "codigo": "ESPINA-RIVAL-SIGUE",
      "detalle": "la espina del rival dice positiva: que gana"
     }
    ],
    "elegido": "local",
    "regla": "espinas",
    "espinaElegido": "negativa",
    "espinaRival": "positiva",
    "espinas": {
     "a": "negativa",
     "b": "positiva"
    },
    "distancia": 2.1,
    "marcadorSigno": "local"
   },
   "marcador": {
    "masProbable": "1-1",
    "prob": 0.13,
    "signo": "empate",
    "alineado": false
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
     "banca": 102.49,
     "linea": null,
     "motivo": "semáforo en rojo: no apostar"
    },
    "metodoMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 98.42,
     "linea": null,
     "motivo": "el marcador más probable (1-1) no va con el elegido"
    },
    "metodoVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.42,
     "linea": null,
     "motivo": "semáforo no está en verde"
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
    },
    "martingala60Ajustada": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.75,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "martingalaAjustadaVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.43,
     "linea": null,
     "motivo": "semáforo no está en verde"
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
    "regla": "espinas",
    "espinaElegido": "positiva",
    "espinaRival": "negativa",
    "espinas": {
     "a": "positiva",
     "b": "negativa"
    },
    "distancia": 1.7,
    "marcadorSigno": "local"
   },
   "marcador": {
    "masProbable": "2-0",
    "prob": 0.112,
    "signo": "local",
    "alineado": true
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
     "monto": 1.0353,
     "ganancia": -1.0353,
     "banca": 102.49,
     "linea": null,
     "motivo": ""
    },
    "metodoMarcador": {
     "seleccion": "local",
     "monto": 0.9942,
     "ganancia": -0.9942,
     "banca": 98.42,
     "linea": null,
     "motivo": ""
    },
    "metodoVerdeMarcador": {
     "seleccion": "local",
     "monto": 1.0144,
     "ganancia": -1.0144,
     "banca": 100.42,
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
    },
    "martingala60Ajustada": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 99.75,
     "linea": 1,
     "motivo": ""
    },
    "martingalaAjustadaVerdeMarcador": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 100.43,
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
    "regla": "espinas",
    "espinaElegido": "positiva",
    "espinaRival": "negativa",
    "espinas": {
     "a": "positiva",
     "b": "negativa"
    },
    "distancia": 0.9,
    "marcadorSigno": "local"
   },
   "marcador": {
    "masProbable": "2-1",
    "prob": 0.104,
    "signo": "local",
    "alineado": true
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
     "monto": 1.0283,
     "ganancia": 0.6992,
     "banca": 103.53,
     "linea": null,
     "motivo": ""
    },
    "metodoMarcador": {
     "seleccion": "local",
     "monto": 0.9875,
     "ganancia": 0.6715,
     "banca": 99.42,
     "linea": null,
     "motivo": ""
    },
    "metodoVerdeMarcador": {
     "seleccion": "local",
     "monto": 1.0075,
     "ganancia": 0.6851,
     "banca": 101.44,
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
    },
    "martingala60Ajustada": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.75,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "martingalaAjustadaVerdeMarcador": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 0.68,
     "banca": 101.43,
     "linea": 1,
     "motivo": ""
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
      "codigo": "ESPINA-ELEGIDO-EMPATA",
      "detalle": "la espina del elegido (local) dice empate, no que gane"
     },
     {
      "codigo": "ESPINA-RIVAL-SIGUE",
      "detalle": "la espina del rival dice positiva: que gana"
     }
    ],
    "elegido": "local",
    "regla": "espinas",
    "espinaElegido": "cero",
    "espinaRival": "positiva",
    "espinas": {
     "a": "cero",
     "b": "positiva"
    },
    "distancia": 3.9,
    "marcadorSigno": "empate"
   },
   "marcador": {
    "masProbable": "1-1",
    "prob": 0.119,
    "signo": "empate",
    "alineado": false
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
     "banca": 102.83,
     "linea": null,
     "motivo": "semáforo en amarillo"
    },
    "metodoMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 98.75,
     "linea": null,
     "motivo": "el marcador más probable (1-1) no va con el elegido"
    },
    "metodoVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.75,
     "linea": null,
     "motivo": "semáforo no está en verde"
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
    },
    "martingala60Ajustada": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.75,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "martingalaAjustadaVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.75,
     "linea": null,
     "motivo": "semáforo no está en verde"
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
    "estado": "confirma",
    "motivos": [],
    "elegido": "local",
    "regla": "espinas",
    "espinaElegido": "positiva",
    "espinaRival": "negativa",
    "espinas": {
     "a": "positiva",
     "b": "negativa"
    },
    "distancia": 5.3,
    "marcadorSigno": "local"
   },
   "marcador": {
    "masProbable": "2-1",
    "prob": 0.102,
    "signo": "local",
    "alineado": true
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
     "seleccion": "local",
     "monto": 1.0206,
     "ganancia": 0.7654,
     "banca": 102.83,
     "linea": null,
     "motivo": ""
    },
    "metodoMarcador": {
     "seleccion": "local",
     "monto": 0.9801,
     "ganancia": 0.7351,
     "banca": 98.75,
     "linea": null,
     "motivo": ""
    },
    "metodoVerdeMarcador": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 0.75,
     "banca": 100.75,
     "linea": null,
     "motivo": ""
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
    },
    "martingala60Ajustada": {
     "seleccion": "local",
     "monto": 2.3333,
     "ganancia": 1.75,
     "banca": 100.75,
     "linea": 1,
     "motivo": ""
    },
    "martingalaAjustadaVerdeMarcador": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 0.75,
     "banca": 100.75,
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
    "estado": "duda",
    "motivos": [
     {
      "codigo": "ESPINA-RIVAL-SIGUE",
      "detalle": "la espina del rival dice positiva: que gana"
     }
    ],
    "elegido": "local",
    "regla": "espinas",
    "espinaElegido": "positiva",
    "espinaRival": "positiva",
    "espinas": {
     "a": "positiva",
     "b": "positiva"
    },
    "distancia": 1.2,
    "marcadorSigno": "local"
   },
   "marcador": {
    "masProbable": "1-0",
    "prob": 0.115,
    "signo": "local",
    "alineado": true
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
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 102.06,
     "linea": null,
     "motivo": "semáforo en amarillo"
    },
    "metodoMarcador": {
     "seleccion": "local",
     "monto": 0.99,
     "ganancia": -0.99,
     "banca": 98.01,
     "linea": null,
     "motivo": ""
    },
    "metodoVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "semáforo no está en verde"
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
    },
    "martingala60Ajustada": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.0,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "martingalaAjustadaVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "semáforo no está en verde"
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
    "estado": "confirma",
    "motivos": [],
    "elegido": "local",
    "regla": "espinas",
    "espinaElegido": "positiva",
    "espinaRival": "negativa",
    "espinas": {
     "a": "positiva",
     "b": "negativa"
    },
    "distancia": 3.7,
    "marcadorSigno": "empate"
   },
   "marcador": {
    "masProbable": "1-1",
    "prob": 0.124,
    "signo": "empate",
    "alineado": false
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
     "seleccion": "local",
     "monto": 1.0105,
     "ganancia": 1.0105,
     "banca": 102.06,
     "linea": null,
     "motivo": ""
    },
    "metodoMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.0,
     "linea": null,
     "motivo": "el marcador más probable (1-1) no va con el elegido"
    },
    "metodoVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "el marcador más probable (1-1) no va con el elegido"
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
    },
    "martingala60Ajustada": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 99.0,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "martingalaAjustadaVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "el marcador más probable (1-1) no va con el elegido"
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
      "codigo": "ESPINA-RIVAL-SIGUE",
      "detalle": "la espina del rival dice cero: que no pierde"
     }
    ],
    "elegido": "local",
    "regla": "espinas",
    "espinaElegido": "positiva",
    "espinaRival": "cero",
    "espinas": {
     "a": "positiva",
     "b": "cero"
    },
    "distancia": 3.0,
    "marcadorSigno": "local"
   },
   "marcador": {
    "masProbable": "1-0",
    "prob": 0.118,
    "signo": "local",
    "alineado": true
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
    "metodoMarcador": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 99.0,
     "linea": null,
     "motivo": ""
    },
    "metodoVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "semáforo no está en verde"
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
    },
    "martingala60Ajustada": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 99.0,
     "linea": 1,
     "motivo": ""
    },
    "martingalaAjustadaVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "semáforo no está en verde"
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
    "regla": "espinas",
    "espinaElegido": "positiva",
    "espinaRival": "negativa",
    "espinas": {
     "a": "positiva",
     "b": "negativa"
    },
    "distancia": 1.0,
    "marcadorSigno": "local"
   },
   "marcador": {
    "masProbable": "1-1",
    "prob": 0.121,
    "signo": "empate",
    "alineado": false
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
    "metodoMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "el marcador más probable (1-1) no va con el elegido"
    },
    "metodoVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "el marcador más probable (1-1) no va con el elegido"
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
    },
    "martingala60Ajustada": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "bajo 60 %"
    },
    "martingalaAjustadaVerdeMarcador": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0,
     "linea": null,
     "motivo": "el marcador más probable (1-1) no va con el elegido"
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
