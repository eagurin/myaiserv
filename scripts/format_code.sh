#!/usr/bin/env bash
set -e

# Скрипт для форматирования кода
# Авто-форматирование с помощью black, isort и ruff

SRC_DIR="./app"
TESTS_DIR="./tests"

echo "Запуск black..."
poetry run black ${SRC_DIR} ${TESTS_DIR}

echo "Запуск isort..."
poetry run isort ${SRC_DIR} ${TESTS_DIR}

echo "Запуск ruff format..."
poetry run ruff format ${SRC_DIR} ${TESTS_DIR}

echo "Запуск ruff check --fix..."
poetry run ruff check --fix ${SRC_DIR} ${TESTS_DIR}

echo "Форматирование кода завершено."