# 🌿 Herbario de Flora Boliviana — API Gateway + Microservicio NestJS

Arquitectura orientada a servicios para catalogar la flora de Bolivia: **plantas**, **familias botánicas** y **avistamientos** en campo.
Está formada por un **API Gateway** (proxy inverso), un **microservicio backend en NestJS (TypeScript)** y una base de datos **PostgreSQL**, todo orquestado con **Docker Compose**.

```
                      ┌───────────────────────────── red Docker "herbario-net" (bridge) ─────────────────────────────┐
 Cliente              │                                                                                              │
 (Postman, cURL,  ───►│  API Gateway  ───────────►  Microservicio  ───────────►  PostgreSQL                          │
  navegador)  :8080   │  Node + Express             NestJS + TypeORM             postgres:16                          │
                      │  CORS · Logs · Rate limit   CRUD + DTO + Repository      (volumen pgdata)                    │
                      │  JWT · Proxy                :3000 (interno)              :5432 (interno)                     │
                      └──────────────────────────────────────────────────────────────────────────────────────────────┘
```

Solo el gateway (`:8080`) está publicado hacia el exterior; el microservicio y la base de datos solo son accesibles dentro de la red de Docker.

## 1. Stack

| Componente | Tecnología |
|---|---|
| API Gateway | Node.js 20, Express, `http-proxy-middleware`, `cors`, `morgan`, `express-rate-limit`, `jsonwebtoken` |
| Microservicio | **NestJS 10 (TypeScript)**, TypeORM, class-validator, Swagger |
| Base de datos | PostgreSQL 16 |
| Contenedores | Docker + Docker Compose (red `bridge`, `depends_on`, `healthcheck`) |

## 2. Estructura del proyecto

```
herbario-flora-bolivia/
├── docker-compose.yml
├── .env.example
├── gateway/                  # API Gateway (proxy inverso)
│   ├── Dockerfile
│   └── src/ (index.js, middlewares.js, config.js)
├── microservicio/            # Microservicio NestJS
│   ├── Dockerfile            # multi-stage (build + runtime)
│   └── src/
│       ├── familias/         # entity · dto · service (repository) · controller · module
│       ├── plantas/
│       ├── avistamientos/
│       ├── health/ · common/ · seed/
│       └── main.ts · app.module.ts
├── postman/herbario.postman_collection.json
├── scripts/ (smoke-test.sh, init-gitflow.sh)
└── docs/                     # informe técnico y diagramas C4
```

## 3. Requisitos

- [Docker Desktop](https://www.docker.com/products/docker-desktop/) (incluye Docker Compose)
- Git
- (Opcional) Postman, o `curl` (en Windows se recomienda **Git Bash**)

## 4. Clonar y ejecutar

```bash
git clone https://github.com/TU_USUARIO/herbario-flora-bolivia.git
cd herbario-flora-bolivia

# (opcional) personalizar variables
cp .env.example .env

docker-compose up --build
```

> Con Docker Desktop reciente también funciona `docker compose up --build` (sin guion).

La primera vez descarga imágenes y compila, puede tardar unos minutos. Cuando veas en los logs
`Microservicio escuchando en el puerto 3000` y `Gateway escuchando en :8080` el sistema está listo.
`docker-compose ps` debe mostrar los tres servicios en estado **healthy**.

| Qué | URL |
|---|---|
| API (a través del gateway) | http://localhost:8080/api/... |
| Swagger UI (documentación interactiva) | http://localhost:8080/docs |
| Health del gateway | http://localhost:8080/health |

Credenciales por defecto del login: usuario `admin`, contraseña `herbario123` (se cambian en `.env`).

Detener: `Ctrl + C` y luego `docker-compose down`.
Borrar también los datos de la BD: `docker-compose down -v`.

Al arrancar por primera vez se cargan datos de ejemplo (5 familias, 5 plantas, 2 avistamientos). Se desactiva con `SEED_DATA=false`.

## 5. Cómo probar el sistema

### 5.1 Swagger
1. Abre http://localhost:8080/docs
2. Haz `POST /auth/login` por cURL/Postman (abajo) y copia el `access_token`.
3. Pulsa **Authorize**, pega el token y prueba cualquier endpoint con *Try it out*.

### 5.2 cURL (Git Bash / Linux / macOS)

```bash
# 1) Login -> guarda el token
TOKEN=$(curl -s -X POST http://localhost:8080/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"herbario123"}' | grep -o '"access_token":"[^"]*"' | cut -d'"' -f4)

# 2) Sin token -> 401
curl -i http://localhost:8080/api/plantas

# 3) Listar plantas
curl -s http://localhost:8080/api/plantas -H "Authorization: Bearer $TOKEN"

# 4) Crear familia y planta
curl -s -X POST http://localhost:8080/api/familias \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"nombre":"Cactaceae","descripcion":"Familia de los cactus"}'

curl -s -X POST http://localhost:8080/api/plantas \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"nombreCientifico":"Echinopsis tarijensis","nombreComun":"Cardón","ecorregion":"Valles secos","altitudMin":1800,"altitudMax":3200,"familiaId":6}'

# 5) Filtros
curl -s "http://localhost:8080/api/plantas?estado=en_peligro" -H "Authorization: Bearer $TOKEN"
curl -s "http://localhost:8080/api/plantas?q=que%C3%B1ua"     -H "Authorization: Bearer $TOKEN"

# 6) Registrar un avistamiento
curl -s -X POST http://localhost:8080/api/avistamientos \
  -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" \
  -d '{"plantaId":1,"localidad":"Tarija - Tolomosa","departamento":"Tarija","latitud":-21.5,"longitud":-64.8,"fecha":"2026-10-10","observador":"Estudiante UCB"}'

# 7) Actualizar y borrar
curl -s -X PATCH  http://localhost:8080/api/plantas/1 -H "Authorization: Bearer $TOKEN" -H "Content-Type: application/json" -d '{"estadoConservacion":"vulnerable"}'
curl -i -X DELETE http://localhost:8080/api/avistamientos/1 -H "Authorization: Bearer $TOKEN"
```

**Windows PowerShell** (`curl` allí es un alias, usa `Invoke-RestMethod`):

```powershell
$login = Invoke-RestMethod -Method Post -Uri http://localhost:8080/auth/login `
  -ContentType 'application/json' -Body '{"username":"admin","password":"herbario123"}'
$h = @{ Authorization = "Bearer $($login.access_token)" }
Invoke-RestMethod http://localhost:8080/api/plantas -Headers $h
```

### 5.3 Script de pruebas automático
Ejecuta 20 casos (login, 401, CRUD completo, validaciones 400, conflictos 409, 404) y limpia lo que crea:

```bash
bash scripts/smoke-test.sh
```

### 5.4 Postman
Importa `postman/herbario.postman_collection.json` y ejecútala en orden con el **Runner**.
La petición *Login* guarda el token en una variable y las siguientes lo usan automáticamente.

### 5.5 Probar las características del gateway
- **JWT:** `GET /api/plantas` sin token devuelve `401`.
- **Rate limiting:** más de 10 intentos de login por minuto devuelven `429` (global: 100 peticiones/min por IP).
- **Logging / trazabilidad:** `docker-compose logs gateway microservicio` muestra el mismo `x-request-id` en ambos servicios.
- **502 Bad Gateway:** `docker-compose stop microservicio` y llama a la API; el gateway responde `502` en vez de colgarse.
- **CORS:** configurable con `CORS_ORIGINS` (por defecto `*`).

## 6. Endpoints

Todos bajo `/api` y requieren `Authorization: Bearer <token>` (excepto `/auth/login`, `/health` y `/docs`).

| Recurso | Método y ruta | Descripción |
|---|---|---|
| Auth | `POST /auth/login` | Devuelve el JWT |
| Familias | `GET /api/familias` · `GET /api/familias/:id` | Listar / obtener |
| | `POST /api/familias` · `PATCH /api/familias/:id` · `DELETE /api/familias/:id` | Crear / actualizar / borrar (409 si tiene plantas) |
| Plantas | `GET /api/plantas?familiaId=&ecorregion=&estado=&q=` | Listar con filtros |
| | `GET /api/plantas/:id` · `GET /api/plantas/:id/avistamientos` | Obtener / sus avistamientos |
| | `POST /api/plantas` · `PATCH /api/plantas/:id` · `DELETE /api/plantas/:id` | Crear / actualizar / borrar |
| Avistamientos | `GET /api/avistamientos?plantaId=&departamento=` · `GET /api/avistamientos/:id` | Listar / obtener |
| | `POST /api/avistamientos` · `PATCH /api/avistamientos/:id` · `DELETE /api/avistamientos/:id` | Crear / actualizar / borrar |

Valores válidos: `estadoConservacion` ∈ `preocupacion_menor, casi_amenazada, vulnerable, en_peligro, en_peligro_critico`;
`departamento` ∈ `La Paz, Cochabamba, Santa Cruz, Oruro, Potosí, Chuquisaca, Tarija, Beni, Pando`; `fecha` en formato `YYYY-MM-DD`.

## 7. Variables de entorno

Ver `.env.example`. Las principales: `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `JWT_SECRET`, `JWT_EXPIRES_IN`, `ADMIN_USER`, `ADMIN_PASSWORD`, `CORS_ORIGINS`, `RATE_LIMIT_MAX`, `SEED_DATA`.
⚠️ Cambia `JWT_SECRET` y `ADMIN_PASSWORD` si despliegas fuera del entorno académico.

## 8. Desarrollo local sin Docker (opcional)

Necesitas Node 20+ y un PostgreSQL local con la base `herbario_db` y el usuario `herbario` / `herbario123`.

```bash
# Terminal 1 — microservicio
cd microservicio && npm install && npm run start:dev      # :3000

# Terminal 2 — gateway
cd gateway && npm install && MICROSERVICE_URL=http://localhost:3000 npm start   # :8080
```

## 9. Patrones y decisiones de diseño

- **Repository:** los servicios inyectan `Repository<Entidad>` de TypeORM (`@InjectRepository`) y no tocan SQL directamente.
- **DTO:** cada recurso tiene `Create*Dto`, `Update*Dto` (`PartialType`) y `Query*Dto` con validación (`class-validator`, `whitelist` + `forbidNonWhitelisted`).
- **Inyección de dependencias:** módulos, servicios y controladores de NestJS.
- **Integridad:** `Familia → Planta` con `RESTRICT` (409 al borrar una familia con plantas) y `Planta → Avistamiento` con `CASCADE`.
- **Esquema:** TypeORM crea las tablas automáticamente (`DB_SYNC=true`); en producción real se usarían migraciones.

## 10. Git Flow

Ramas: `main` (releases), `develop` (integración), `feature/*` (una por componente), `release/*`. Los merges usan `--no-ff` y la versión 1.0.0 está etiquetada (`v1.0.0`).
Convención de commits: `feat`, `fix`, `docs`, `build`, `test`, `chore`.

```bash
git log --graph --oneline --all
```
