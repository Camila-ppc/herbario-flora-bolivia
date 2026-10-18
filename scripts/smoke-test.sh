#!/usr/bin/env bash
# Prueba de punta a punta del sistema a través del API Gateway.
# Uso:  bash scripts/smoke-test.sh            (requiere el sistema corriendo)
#       BASE_URL=http://localhost:8080 bash scripts/smoke-test.sh
BASE="${BASE_URL:-http://localhost:8080}"
ADMIN_USER="${ADMIN_USER:-admin}"
ADMIN_PASSWORD="${ADMIN_PASSWORD:-herbario123}"
JSON='Content-Type: application/json'

# call "<titulo>" <metodo> <ruta> [json] [con_token=1]
call() {
  local title="$1" method="$2" path="$3" data="$4" auth="${5:-1}"
  local args=(-s -X "$method" "$BASE$path" -w '\nHTTP %{http_code}')
  [ -n "$data" ] && args+=(-H "$JSON" -d "$data")
  [ "$auth" = "1" ] && args+=(-H "Authorization: Bearer $TOKEN")
  echo; echo "### $title"; echo "\$ curl -X $method $BASE$path${data:+ -d '$data'}"
  RESP=$(curl "${args[@]}"); echo "$RESP"
}
id_of() { echo "$RESP" | grep -o '"id":[0-9]*' | head -1 | cut -d: -f2; }

# Si algo falla a medias, borra lo creado para poder repetir el script sin conflictos
cleanup() {
  [ -z "$TOKEN" ] || [ "$DONE" = "1" ] && return
  for r in "avistamientos/$AVI" "plantas/$PLA" "familias/$FAM"; do
    case "$r" in */) continue ;; esac
    curl -s -o /dev/null -X DELETE "$BASE/api/$r" -H "Authorization: Bearer $TOKEN"
  done
}
trap cleanup EXIT
need() { [ -z "$1" ] && { echo; echo "ERROR: $2. Abortando."; exit 1; }; }

call "1. Health del gateway" GET /health "" 0
call "2. Acceso SIN token (debe dar 401)" GET /api/plantas "" 0
call "3. Login con credenciales incorrectas (401)" POST /auth/login '{"username":"admin","password":"mal"}' 0
call "4. Login correcto" POST /auth/login "{\"username\":\"$ADMIN_USER\",\"password\":\"$ADMIN_PASSWORD\"}" 0
TOKEN=$(echo "$RESP" | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)
[ -z "$TOKEN" ] && { echo "No se pudo obtener el token. Abortando."; exit 1; }

call "5. Listar familias" GET /api/familias
call "6. Crear familia" POST /api/familias '{"nombre":"Cactaceae","descripcion":"Familia de los cactus"}'
FAM=$(id_of); need "$FAM" "no se pudo crear la familia (¿quedó una 'Cactaceae' de una prueba anterior?)"
call "7. Crear familia duplicada (409)" POST /api/familias '{"nombre":"Cactaceae"}'
call "8. Crear planta" POST /api/plantas "{\"nombreCientifico\":\"Echinopsis tarijensis\",\"nombreComun\":\"Cardón\",\"ecorregion\":\"Valles secos\",\"altitudMin\":1800,\"altitudMax\":3200,\"familiaId\":$FAM}"
PLA=$(id_of); need "$PLA" "no se pudo crear la planta"
call "9. Crear planta con datos inválidos (400)" POST /api/plantas '{"nombreCientifico":"","familiaId":"x"}'
call "10. Buscar plantas por nombre (q=cardón)" GET "/api/plantas?q=card%C3%B3n"
call "11. Filtrar plantas en peligro" GET "/api/plantas?estado=en_peligro"
call "12. Obtener planta por id" GET "/api/plantas/$PLA"
call "13. Actualizar planta (PATCH)" PATCH "/api/plantas/$PLA" '{"estadoConservacion":"casi_amenazada"}'
call "14. Registrar avistamiento" POST /api/avistamientos "{\"plantaId\":$PLA,\"localidad\":\"Tarija - Tolomosa\",\"departamento\":\"Tarija\",\"latitud\":-21.5,\"longitud\":-64.8,\"fecha\":\"2026-10-10\",\"observador\":\"Estudiante UCB\"}"
AVI=$(id_of); need "$AVI" "no se pudo crear el avistamiento"
call "15. Avistamientos de la planta" GET "/api/plantas/$PLA/avistamientos"
call "16. Borrar familia con plantas (409)" DELETE "/api/familias/$FAM"
call "17. Borrar avistamiento (204)" DELETE "/api/avistamientos/$AVI"
call "18. Borrar planta (204)" DELETE "/api/plantas/$PLA"
call "19. Borrar familia (204)" DELETE "/api/familias/$FAM"
DONE=1
call "20. Planta borrada ya no existe (404)" GET "/api/plantas/$PLA"
call "21. Swagger publico (primeras lineas)" GET /docs-json "" 0 | head -4
echo; echo "Pruebas terminadas."
