#!/usr/bin/env bash
# Diagnóstico del camino Cowork contra un backend desplegado.
#
#   SAD_BASE=https://tu-app.up.railway.app/api/v1 \
#   SAD_TOKEN_COWORK=... \
#   bash scripts/probar-cowork.sh [ligaId] [horas]
#
# No escribe nada: solo GETs. Interpreta los códigos en vez de dejártelos a ti,
# que es donde se pierde el tiempo (un 401 y un 404 significan cosas muy
# distintas y las dos se parecen a "no funciona").
set -uo pipefail

BASE="${SAD_BASE:-}"
TOKEN="${SAD_TOKEN_COWORK:-}"
LIGA="${1:-262}"        # 262 = Liga MX
HORAS="${2:-6}"

[ -z "$BASE" ] && { echo "Falta SAD_BASE (ej. https://tu-app.up.railway.app/api/v1)"; exit 1; }
[ -z "$TOKEN" ] && { echo "Falta SAD_TOKEN_COWORK"; exit 1; }
BASE="${BASE%/}"

codigo() { curl -s -o /tmp/sadprueba.json -w '%{http_code}' --max-time 20 "$@" 2>/dev/null || echo "000"; }
cuerpo() { head -c 400 /tmp/sadprueba.json 2>/dev/null; }

echo "· backend: $BASE"
echo

# 1 ── ¿está vivo? /health no pide token
H=$(codigo "$BASE/health")
case "$H" in
  200) echo "[1/4] health ................ OK ($(cuerpo | head -c 120))" ;;
  000) echo "[1/4] health ................ NO RESPONDE. URL mal escrita, servicio dormido o caído."; exit 1 ;;
  *)   echo "[1/4] health ................ HTTP $H — el servicio contesta pero mal."; exit 1 ;;
esac

# 2 ── ¿está desplegado el código del parte? 404 = el deploy es viejo
A=$(codigo -H "Authorization: Bearer $TOKEN" "$BASE/analisis/cowork/agenda?limite=1")
case "$A" in
  200) echo "[2/4] endpoints Cowork ...... OK, desplegados" ;;
  404) echo "[2/4] endpoints Cowork ...... NO EXISTEN en el deploy."
       echo "      El backend desplegado es ANTERIOR al camino Cowork."
       echo "      → hay que desplegar la rama (o mergearla a main si Railway sigue main)."
       exit 1 ;;
  401) echo "[2/4] endpoints Cowork ...... 401 NO AUTORIZADO."
       echo "      O el token no coincide, o el deploy no conoce SAD_TOKEN_COWORK"
       echo "      (código anterior al token acotado: solo aceptaría SAD_API_TOKEN)."
       exit 1 ;;
  403) echo "[2/4] endpoints Cowork ...... 403 con la agenda: eso no debería pasar."
       echo "      $(cuerpo)"; exit 1 ;;
  *)   echo "[2/4] endpoints Cowork ...... HTTP $A — $(cuerpo)"; exit 1 ;;
esac

# 3 ── el recorte del token: lo caro TIENE que dar 403
E=$(codigo -X POST -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
    -d '{"fixtureId":1}' "$BASE/analisis/efe")
if [ "$E" = "403" ]; then
  echo "[3/4] token acotado ......... OK: /analisis/efe responde 403"
else
  echo "[3/4] token acotado ......... ⚠ /analisis/efe respondió $E, NO 403."
  echo "      Ese token PUEDE gastar créditos. Revisa que SAD_TOKEN_COWORK esté"
  echo "      puesto, que sea DISTINTO de SAD_API_TOKEN, y que el deploy sea el nuevo."
fi

# 4 ── la agenda de verdad
Q="ligaId=$LIGA&desdeAhora=true&horas=$HORAS&incluirDescartados=true&limite=5"
G=$(codigo -H "Authorization: Bearer $TOKEN" "$BASE/analisis/cowork/agenda?$Q")
echo "[4/4] agenda liga $LIGA ....... HTTP $G"
echo
if [ "$G" = "200" ]; then
  python3 - <<'PY' 2>/dev/null || cat /tmp/sadprueba.json
import json
d = json.load(open("/tmp/sadprueba.json"))
print(f"ventana: {d.get('ventana')}")
items = d.get("analizar", []) + d.get("enEspera", [])
if not items:
    print("\nNingún partido de esa liga en la ventana.")
    print("Puede ser que ya empezaron todos, que la ingesta no tenga los fixtures de hoy,")
    print("o que el ligaId no sea el que crees. Prueba con más horas.")
else:
    print(f"\n{len(items)} partido(s):\n")
    for i in items:
        print(f"  {i['hora']}  {i['partido']}")
        print(f"          fixtureId {i['fixtureId']} · prioridad {i['prioridad']} · {i['motivo']}")
        if i.get("parte"):
            print(f"          ojo: ya tiene parte ({i['parte']})")
    print(f"\n{d.get('notaSeleccion','')}")
PY
fi
