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
   "rachaPerdidas": null,
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
     "pitazo": "2026-10-28 19:30:00",
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
   "clave": "kelly",
   "nombre": "Kelly completo",
   "descripcion": "f* = (p·c − 1)/(c − 1) de la banca a la selección con más ventaja; sin ventaja no apuesta",
   "banca": 109.2,
   "ganancia": 9.2,
   "apostado": 10.93,
   "apuestas": 2,
   "ganadas": 2,
   "roi": 0.8415,
   "caidaMaxima": 0.0,
   "quebro": null,
   "rachaPerdidas": null,
   "serie": [
    {
     "fixtureId": null,
     "pitazo": null,
     "banca": 100.0
    },
    {
     "fixtureId": 900003,
     "pitazo": "2026-10-28 19:45:00",
     "banca": 104.0
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 109.2
    }
   ]
  },
  {
   "clave": "kellyMedio",
   "nombre": "Kelly ½",
   "descripcion": "la mitad de la fracción de Kelly",
   "banca": 104.55,
   "ganancia": 4.55,
   "apostado": 5.4,
   "apuestas": 2,
   "ganadas": 2,
   "roi": 0.8426,
   "caidaMaxima": 0.0,
   "quebro": null,
   "rachaPerdidas": null,
   "serie": [
    {
     "fixtureId": null,
     "pitazo": null,
     "banca": 100.0
    },
    {
     "fixtureId": 900003,
     "pitazo": "2026-10-28 19:45:00",
     "banca": 102.0
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 104.55
    }
   ]
  },
  {
   "clave": "kellyCuarto",
   "nombre": "Kelly ¼",
   "descripcion": "un cuarto de la fracción de Kelly",
   "banca": 102.26,
   "ganancia": 2.26,
   "apostado": 2.68,
   "apuestas": 2,
   "ganadas": 2,
   "roi": 0.8432,
   "caidaMaxima": 0.0,
   "quebro": null,
   "rachaPerdidas": null,
   "serie": [
    {
     "fixtureId": null,
     "pitazo": null,
     "banca": 100.0
    },
    {
     "fixtureId": 900003,
     "pitazo": "2026-10-28 19:45:00",
     "banca": 101.0
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 102.26
    }
   ]
  },
  {
   "clave": "martingala",
   "nombre": "Martingala",
   "descripcion": "1 unidad a nuestro elegido, se duplica tras cada derrota y vuelve a 1 al ganar",
   "banca": 102.55,
   "ganancia": 2.55,
   "apostado": 7.0,
   "apuestas": 5,
   "ganadas": 3,
   "roi": 0.3643,
   "caidaMaxima": 0.0099,
   "quebro": null,
   "rachaPerdidas": 0,
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
     "pitazo": "2026-10-28 19:30:00",
     "banca": 100.05
    },
    {
     "fixtureId": 900003,
     "pitazo": "2026-10-28 19:45:00",
     "banca": 102.05
    },
    {
     "fixtureId": 900004,
     "pitazo": "2026-10-28 20:00:00",
     "banca": 101.05
    },
    {
     "fixtureId": 900005,
     "pitazo": "2026-10-29 19:30:00",
     "banca": 102.55
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
    "kelly": {
     "apostado": 0.0,
     "ganancia": 0.0,
     "apuestas": 0,
     "roi": null
    },
    "kellyMedio": {
     "apostado": 0.0,
     "ganancia": 0.0,
     "apuestas": 0,
     "roi": null
    },
    "kellyCuarto": {
     "apostado": 0.0,
     "ganancia": 0.0,
     "apuestas": 0,
     "roi": null
    },
    "martingala": {
     "apostado": 2.0,
     "ganancia": 0.05,
     "apuestas": 2,
     "roi": 0.025
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
    "kelly": {
     "apostado": 10.9333,
     "ganancia": 9.2,
     "apuestas": 2,
     "roi": 0.8415
    },
    "kellyMedio": {
     "apostado": 5.4,
     "ganancia": 4.55,
     "apuestas": 2,
     "roi": 0.8426
    },
    "kellyCuarto": {
     "apostado": 2.6833,
     "ganancia": 2.2625,
     "apuestas": 2,
     "roi": 0.8432
    },
    "martingala": {
     "apostado": 5.0,
     "ganancia": 2.5,
     "apuestas": 3,
     "roi": 0.5
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
     "banca": null
    },
    "kelly": {
     "seleccion": "visita",
     "monto": 4.368,
     "ganancia": null,
     "banca": null
    },
    "kellyMedio": {
     "seleccion": "visita",
     "monto": 2.091,
     "ganancia": null,
     "banca": null
    },
    "kellyCuarto": {
     "seleccion": "visita",
     "monto": 1.0226,
     "ganancia": null,
     "banca": null
    },
    "martingala": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": null,
     "banca": null
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
     "banca": 100.8
    },
    "kelly": {
     "seleccion": "local",
     "monto": 6.9333,
     "ganancia": 5.2,
     "banca": 109.2
    },
    "kellyMedio": {
     "seleccion": "local",
     "monto": 3.4,
     "ganancia": 2.55,
     "banca": 104.55
    },
    "kellyCuarto": {
     "seleccion": "local",
     "monto": 1.6833,
     "ganancia": 1.2625,
     "banca": 102.26
    },
    "martingala": {
     "seleccion": "local",
     "monto": 2.0,
     "ganancia": 1.5,
     "banca": 102.55
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
     "banca": 100.05
    },
    "kelly": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 104.0
    },
    "kellyMedio": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 102.0
    },
    "kellyCuarto": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 101.0
    },
    "martingala": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 101.05
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
     "banca": 101.05
    },
    "kelly": {
     "seleccion": "local",
     "monto": 4.0,
     "ganancia": 4.0,
     "banca": 104.0
    },
    "kellyMedio": {
     "seleccion": "local",
     "monto": 2.0,
     "ganancia": 2.0,
     "banca": 102.0
    },
    "kellyCuarto": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 1.0,
     "banca": 101.0
    },
    "martingala": {
     "seleccion": "local",
     "monto": 2.0,
     "ganancia": 2.0,
     "banca": 102.05
    }
   }
  },
  {
   "fixtureId": 900002,
   "pitazo": "2026-10-28 19:30:00",
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
    "local": 57.0,
    "empate": 24.0,
    "visita": 19.0
   },
   "cuotas": {
    "local": 1.72,
    "empate": 3.9,
    "visita": 4.8
   },
   "mercado": {
    "local": 55.6,
    "empate": 24.5,
    "visita": 19.9
   },
   "resultado": "empate",
   "elegido": "local",
   "kelly": {
    "seleccion": "empate",
    "fraccion": -0.0221,
    "valor": -0.064
   },
   "estado": "cerrada",
   "porEstrategia": {
    "plana": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 100.05
    },
    "kelly": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0
    },
    "kellyMedio": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0
    },
    "kellyCuarto": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0
    },
    "martingala": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": -1.0,
     "banca": 100.05
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
     "banca": 101.05
    },
    "kelly": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0
    },
    "kellyMedio": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0
    },
    "kellyCuarto": {
     "seleccion": null,
     "monto": 0.0,
     "ganancia": 0.0,
     "banca": 100.0
    },
    "martingala": {
     "seleccion": "local",
     "monto": 1.0,
     "ganancia": 1.05,
     "banca": 101.05
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
