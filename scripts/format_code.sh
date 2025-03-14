#!/bin/bash

# Форматирование кода с помощью black, isort, ruff
echo "Форматирование кода..."
black src tests
isort src tests
ruff check --fix src tests

# Проверка типов с помощью mypy
echo "Проверка типов..."
mypy src

# Проверка на ошибки с помощью flake8
echo "Проверка на ошибки..."
flake8 src tests

echo "Готово!"
