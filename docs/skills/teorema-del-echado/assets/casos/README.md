# El registro NO viaja en este paquete

El `registro.csv` canónico vive **en el repo**, no acá. Este directorio se
conserva solo como marcador de ruta.

**Por qué.** El registro cambia *por partido*; el skill se reempaqueta *por
versión*. Empaquetar un dato de esa cadencia dentro de un artefacto de esta
otra ya produjo tres desincronizaciones: la de v0.1.7 (SKILL.md en v0.1.6,
CALIBRACION.md en v0.1.5, CSV en 17 filas), la pérdida de TDE-035 a TDE-042,
y la canonización de los vocabularios de categoría. Una copia que no existe
no se puede leer vieja.

**Estado del canónico al cierre de v0.1.20 (14.09.2026):**

```
35 filas · 51 columnas · 65.898 bytes
sha256  4a315dd9ca46db1b265435a214dbfa74545c7e38eeff00d84d1e158a8af0861a
```

`scripts/calibrar-tde.py` verifica ese sha256 en cada corrida. Si no coincide,
**manda el repo** y el proceso lo declara en voz alta en vez de continuar en
silencio. El sha256 fijado solo se mueve declarando el alta.

**El estado vigente se identifica por sha256, nunca por conteo de filas ni por
fecha:** dos de las tres desincronizaciones no cambiaron el conteo.

IDs al cierre de v0.1.20: TDE-001…009, 011…018, 021…026, 029…034, 043…048.
Numeraciones ausentes y sus etiquetas: `SKILL.md` § EL REGISTRO.
