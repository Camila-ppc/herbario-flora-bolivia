#!/usr/bin/env bash
# Crea el repositorio Git con historial ordenado según Git Flow:
#   main  <-- release/1.0.0 <-- develop <-- feature/*
# Usa solo comandos git estándar (no necesita la extensión "git-flow").
# Uso (desde la raíz del proyecto, UNA sola vez):  bash scripts/init-gitflow.sh
set -e

[ -d .git ] && { echo "Ya existe un repositorio Git aquí. Abortando."; exit 1; }
git config user.name  >/dev/null || { echo "Configura tu nombre:  git config --global user.name  \"Tu Nombre\"";  exit 1; }
git config user.email >/dev/null || { echo "Configura tu correo:  git config --global user.email \"tu@correo.com\""; exit 1; }

commit() { git add "${@:2}"; git commit -q -m "$1"; echo "  commit: $1"; }
feature() { # feature <nombre>  -> crea la rama desde develop
  git checkout -q develop; git checkout -q -b "feature/$1"; echo ">> rama feature/$1"; }
finish() {  # finish <nombre> -> merge --no-ff a develop y borra la rama
  git checkout -q develop
  git merge -q --no-ff "feature/$1" -m "merge: feature/$1 into develop"
  git branch -q -d "feature/$1"; }

git init -q -b main
commit "chore: commit inicial con .gitignore y variables de ejemplo" .gitignore .env.example
git checkout -q -b develop

feature microservicio-base
commit "feat(ms): proyecto NestJS base con TypeScript y Swagger" \
  microservicio/package.json microservicio/package-lock.json microservicio/tsconfig.json \
  microservicio/tsconfig.build.json microservicio/nest-cli.json microservicio/src/main.ts
commit "feat(ms): healthcheck, enums y manejo de errores de base de datos" \
  microservicio/src/health microservicio/src/common
finish microservicio-base

feature microservicio-familias
commit "feat(ms): CRUD de familias botanicas (entity, DTO, repository, service, controller)" microservicio/src/familias
finish microservicio-familias

feature microservicio-plantas
commit "feat(ms): CRUD de plantas con filtros y relacion a familia" microservicio/src/plantas
finish microservicio-plantas

feature microservicio-avistamientos
commit "feat(ms): CRUD de avistamientos asociados a plantas" microservicio/src/avistamientos
finish microservicio-avistamientos

feature microservicio-integracion
commit "feat(ms): AppModule con TypeORM/PostgreSQL y datos de ejemplo (seed)" \
  microservicio/src/app.module.ts microservicio/src/seed
finish microservicio-integracion

feature api-gateway
commit "feat(gateway): proyecto Express y configuracion por variables de entorno" \
  gateway/package.json gateway/package-lock.json gateway/src/config.js
commit "feat(gateway): proxy inverso, CORS, logging con request-id, rate limiting y JWT" \
  gateway/src/middlewares.js gateway/src/index.js
finish api-gateway

feature docker
commit "build(docker): Dockerfile multi-stage del microservicio" microservicio/Dockerfile microservicio/.dockerignore
commit "build(docker): Dockerfile del gateway" gateway/Dockerfile gateway/.dockerignore
commit "build(docker): docker-compose con red bridge, depends_on y healthchecks" docker-compose.yml
finish docker

feature documentacion-pruebas
commit "test: scripts de prueba (cURL) y coleccion de Postman" scripts postman
commit "docs: README con guia de instalacion, ejecucion y pruebas" README.md
[ -d docs ] && [ -n "$(ls -A docs 2>/dev/null)" ] && commit "docs: informe tecnico y diagramas C4" docs
finish documentacion-pruebas

# --- Release 1.0.0 ---
git checkout -q -b release/1.0.0
cat > CHANGELOG.md <<'EOT'
# Changelog

## [1.0.0]
- API Gateway con proxy inverso, CORS, logging con x-request-id, rate limiting y JWT.
- Microservicio NestJS con CRUD de familias, plantas y avistamientos sobre PostgreSQL.
- Orquestacion con docker-compose (red bridge, depends_on y healthchecks).
EOT
commit "chore(release): preparar version 1.0.0 (CHANGELOG)" CHANGELOG.md
git checkout -q main
git merge -q --no-ff release/1.0.0 -m "merge: release/1.0.0 into main"
git tag -a v1.0.0 -m "Version 1.0.0"
git checkout -q develop
git merge -q --no-ff release/1.0.0 -m "merge: release/1.0.0 back into develop"
git branch -q -d release/1.0.0

echo; echo "Listo. Historial:"; git log --graph --oneline --all | head -40
if [ -n "$(git status --porcelain)" ]; then echo; echo "Nota: quedaron archivos sin versionar (git status)."; fi
echo
echo "Siguiente paso: crear el repo vacio en GitHub y ejecutar:"
echo "  git remote add origin https://github.com/TU_USUARIO/herbario-flora-bolivia.git"
echo "  git push -u origin --all && git push origin --tags"
