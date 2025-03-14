#!/usr/bin/env bash
set -e

# Скрипт для запуска тестов с проверкой покрытия
SRC_DIR="./app"
TESTS_DIR="./tests"
COVERAGE_MIN="95"

echo "Запуск тестов с проверкой покрытия..."
if [ ! -d "${SRC_DIR}" ] || [ ! -d "${TESTS_DIR}" ]; then
    echo "Ошибка: директории src или tests не существуют"
    exit 1
fi

if [ ! -f "${SRC_DIR}/__init__.py" ]; then
    echo "Ошибка: исходные файлы для покрытия не найдены"
    exit 1
fi

# Проверка наличия тестов
test_files=$(find ${TESTS_DIR} -name "test_*.py")
if [ -z "$test_files" ]; then
    echo "Ошибка: тестовые файлы не найдены"
    exit 1
fi

echo "Запуск pytest с проверкой покрытия..."
poetry run pytest \
    -v \
    --tb=short \
    --cov=${SRC_DIR} \
    --cov-report=term-missing \
    --cov-report=html \
    --cov-fail-under=${COVERAGE_MIN} \
    ${TESTS_DIR}

echo "Тесты с покрытием выполнены успешно"