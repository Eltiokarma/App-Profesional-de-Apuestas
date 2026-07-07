"""Ingesta SAD — port del pipeline de cálculo (Etapa 1).

Cadena: sad.db → levels.db → constants.db → discreto.db, según
docs/MOTOR_SAD_EXTRACCION.md (§2 niveles, §3 constantes, §4 discretización)
y docs/INFORME_INGESTA.md (qué replicar y qué defectos NO copiar).

Solo librería estándar (sqlite3). El backend HTTP sigue siendo de solo
lectura; esta capa es la única que escribe las DBs derivadas.
"""
