# Переменные окружения по умолчанию
export PYTHONPATH := "./app"
export PYTHON_VERSION := "3.12"

# Настройки проекта
project_name := "app"
src_dir := "./app"
tests_dir := "./tests"
coverage_min := "95"
log_file := "justfile.log"

# Настройки Docker
docker_image := "app"
docker_tag := "latest"
docker_file := "Dockerfile"
docker_compose_file := "docker-compose.yml"

# Порты и хосты
host := "0.0.0.0"
port := "8000"
reload := "true"

# Настройки виртуального окружения
venv_name := ".venv"
poetry_version := "1.8.3"

# Установка значений по умолчанию
set dotenv-load := true
set shell := ["bash", "-c"]
set positional-arguments := true

# Список всех доступных команд
default:
    @just --list

# Установка зависимостей
install:
    ./scripts/check_environment.sh
    ./scripts/install.sh

# Обновление зависимостей
update:
    poetry update
    poetry lock
    poetry install

# Форматирование кода
fmt:
    ./scripts/format_code.sh

# Проверка типов
typecheck:
    ./scripts/typecheck.sh

# Линтинг
lint:
    ./scripts/lint.sh

# Тесты
test *args='':
    ./scripts/test.sh {{args}}

# Тесты с покрытием
test-cov:
    ./scripts/test_coverage.sh

# Очистка кеша и временных файлов
clean:
    ./scripts/clean.sh

# Проверка безопасности
security:
    ./scripts/security.sh

# Полная проверка кода
check:
    @echo "Запуск полной проверки кода..."
    @just fmt
    @just lint
    @just typecheck
    @just test
    @just security
    @echo "Все проверки успешно завершены"

# Миграции базы данных
db-revision message:
    ./scripts/db_migrations.sh revision "{{message}}"

db-upgrade:
    ./scripts/db_migrations.sh upgrade

db-downgrade:
    ./scripts/db_migrations.sh downgrade

# Запуск приложения
dev:
    ./scripts/dev.sh

run:
    ./scripts/run.sh

# Создание нового модуля
new-module name:
    mkdir -p {{src_dir}}/{{name}}
    touch {{src_dir}}/{{name}}/__init__.py
    touch {{src_dir}}/{{name}}/models.py
    touch {{src_dir}}/{{name}}/schemas.py
    touch {{src_dir}}/{{name}}/service.py
    touch {{src_dir}}/{{name}}/repository.py
    touch {{src_dir}}/{{name}}/router.py
    mkdir -p {{tests_dir}}/{{name}}
    touch {{tests_dir}}/{{name}}/__init__.py
    touch {{tests_dir}}/{{name}}/test_models.py
    touch {{tests_dir}}/{{name}}/test_service.py
    touch {{tests_dir}}/{{name}}/test_api.py

# Генерация документации
docs-build:
    poetry run sphinx-build -b html docs/source docs/build

docs-serve:
    poetry run python -m http.server --directory docs/build 8080

# Pre-commit хуки
setup-hooks:
    poetry run pre-commit install
    poetry run pre-commit install --hook-type commit-msg

check-hooks:
    poetry run pre-commit run --all-files

# Управление версиями
bump-version type:
    @if [ "{{type}}" = "major" ] || [ "{{type}}" = "minor" ] || [ "{{type}}" = "patch" ]; then \
        poetry version {{type}}; \
        version=$$(poetry version -s); \
        git add pyproject.toml; \
        git commit -m "bump: version $$version"; \
        git tag -a "v$$version" -m "version $$version"; \
        echo "Создана новая версия: $$version"; \
    else \
        echo "Ошибка: неверный тип версии. Используйте major, minor или patch"; \
        exit 1; \
    fi

# Docker команды
docker-build:
    docker build \
        --no-cache \
        --build-arg POETRY_VERSION={{poetry_version}} \
        --build-arg APP_USER=app \
        --build-arg APP_UID=1000 \
        -t {{docker_image}}:{{docker_tag}} \
        -f {{docker_file}} \
        .

docker-compose-build:
    docker-compose -f {{docker_compose_file}} build

docker-compose-up *args='':
    docker-compose -f {{docker_compose_file}} up {{args}}

docker-compose-down:
    docker-compose -f {{docker_compose_file}} down

docker-compose-logs *args='':
    docker-compose -f {{docker_compose_file}} logs {{args}}

docker-compose-ps:
    docker-compose -f {{docker_compose_file}} ps

docker-compose-restart *args='':
    docker-compose -f {{docker_compose_file}} restart {{args}}

docker-compose-exec service cmd:
    docker-compose -f {{docker_compose_file}} exec {{service}} {{cmd}}

docker-compose-shell service:
    docker-compose -f {{docker_compose_file}} exec {{service}} sh

docker-compose-pull:
    docker-compose -f {{docker_compose_file}} pull

docker-compose-clean:
    docker-compose -f {{docker_compose_file}} down -v
    docker-compose -f {{docker_compose_file}} down --rmi all

poetry-lock:
    poetry lock --no-update
