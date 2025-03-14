#!/usr/bin/env bash
set -e

# Скрипт для проверки типов с помощью mypy
SRC_DIR="./app"
TESTS_DIR="./tests"

echo "Проверка типов..."
if [ ! -d "${SRC_DIR}" ] || [ ! -d "${TESTS_DIR}" ]; then
    echo "Ошибка: директории src или tests не существуют"
    exit 1
fi

# Очистка кэша mypy перед проверкой
echo "Очистка кэша mypy..."
rm -rf .mypy_cache

# Установка ограничения памяти
export MYPY_FORCE_COLOR=1
export MYPYPATH="${PYTHONPATH}"

echo "Проверка конфигурации mypy..."
if ! poetry run mypy --version >/dev/null 2>&1; then
    echo "Ошибка: mypy не установлен"
    exit 1
fi

echo "Запуск проверки типов..."
poetry run mypy \
    --show-error-codes \
    --pretty \
    --warn-unused-configs \
    --namespace-packages \
    --explicit-package-bases \
    ${SRC_DIR} ${TESTS_DIR}

echo "Проверка типов завершена успешно"