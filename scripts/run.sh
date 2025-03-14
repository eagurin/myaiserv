#!/usr/bin/env bash
set -e

# Скрипт для запуска приложения
PROJECT_NAME="app"
HOST="0.0.0.0"
PORT="8000"

echo "Запуск сервера..."
poetry run uvicorn \
    ${PROJECT_NAME}.main:app \
    --host ${HOST} \
    --port ${PORT} \
    --workers 4 \
    --log-level info