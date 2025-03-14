#!/usr/bin/env bash
set -e

# Скрипт для запуска сервера в режиме разработки
PROJECT_NAME="app"
HOST="0.0.0.0"
PORT="8000"

echo "Проверка порта ${PORT}..."
if lsof -i:${PORT} >/dev/null; then
    echo "Ошибка: порт ${PORT} уже используется"
    exit 1
fi

# Проверка наличия основного файла приложения
if [ ! -f "${PROJECT_NAME}/main.py" ]; then
    echo "Ошибка: файл main.py не найден"
    exit 1
fi

# Проверка переменных окружения
if [ ! -f ".env" ]; then
    echo "Внимание: файл .env не найден, будут использованы значения по умолчанию"
fi

# Проверка доступности директории для логов
log_dir="logs"
if [ ! -d "$log_dir" ]; then
    mkdir -p "$log_dir"
fi

# Проверка наличия файла конфигурации логирования
LOG_CONFIG_ARGS=""
if [ -f "logging.conf" ]; then
    LOG_CONFIG_ARGS="--log-config logging.conf"
else
    echo "Внимание: файл logging.conf не найден, будет использована стандартная конфигурация логирования"
fi

echo "Запуск сервера для разработки..."
poetry run uvicorn \
    ${PROJECT_NAME}.main:app \
    --reload \
    --host ${HOST} \
    --port ${PORT} \
    --log-level debug \
    ${LOG_CONFIG_ARGS} 2>&1 | tee -a "$log_dir/dev.log"