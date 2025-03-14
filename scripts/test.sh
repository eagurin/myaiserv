#!/usr/bin/env bash
set -e

# Скрипт для запуска тестов
# Можно передать аргументы для pytest
TESTS_DIR="./tests"

echo "Запуск тестов..."
if [ ! -d "${TESTS_DIR}" ]; then
    echo "Ошибка: директория tests не существует"
    exit 1
fi

poetry run pytest \
    -v \
    --tb=short \
    "$@"

echo "Тесты выполнены успешно"