"""Canonización de nombres de equipo — una sola implementación.

La investigación llega con el nombre que usan los medios ("Universitario de
Deportes", "Cristal", "Cajamarca FC") y la despensa se guarda bajo el nombre
de la app (teams.name), que es la clave con la que el EFE la busca. Sin este
puente, un dato investigado se deposita bajo un nombre que nadie consulta y el
análisis lo cuenta como faltante — es decir, se paga la búsqueda igual.

La usan el endpoint de carga manual (backend/app.py) y el cargador en bloque
(backend/analisis/despensa_bulk.py): la misma regla en los dos caminos.
"""
import unicodedata


def normalizar(s: str) -> str:
    """minúsculas y sin tildes: 'Melgar FBC' → 'melgar fbc'."""
    return "".join(
        ch for ch in unicodedata.normalize("NFD", (s or "").lower())
        if unicodedata.category(ch) != "Mn"
    )


def canonizar(nombre: str, equipos: "list[tuple[str, str]]") -> str:
    """`equipos` = [(nombre_app, nombre_app_normalizado)].

    Devuelve el nombre de la app si hay match ÚNICO (exacto → parcial →
    tokens); ambiguo o desconocido vuelve tal cual, y quien llama lo delata en
    su salida en vez de adivinar: dos equipos distintos bajo el mismo nombre
    sería peor que un dato sin depositar.
    """
    q = normalizar(nombre)
    if not q:
        return nombre
    exacto = [n for n, nn in equipos if nn == q]
    if len(exacto) == 1:
        return exacto[0]
    parcial = [n for n, nn in equipos if q in nn or nn in q]
    if len(parcial) == 1:
        return parcial[0]
    # tokens sin orden: "FC Cajamarca" vs "Cajamarca FC", o añadidos tipo
    # "Club Deportivo Los Chankas" vs "Los Chankas" — solo con match ÚNICO
    qt = set(q.split())
    tokens = [n for n, nn in equipos if qt and (qt <= set(nn.split()) or set(nn.split()) <= qt)]
    return tokens[0] if len(tokens) == 1 else nombre
