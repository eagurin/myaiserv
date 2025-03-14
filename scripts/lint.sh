#!/usr/bin/env bash
set -e

# Скрипт для проверки стиля кода
SRC_DIR="./app"
TESTS_DIR="./tests"

echo "Проверка стиля кода..."
if [ ! -d "${SRC_DIR}" ] || [ ! -d "${TESTS_DIR}" ]; then
    echo "Ошибка: директории src или tests не существуют"
    exit 1
fi

# Создание временной директории для отчетов
tmp_dir=$(mktemp -d)
trap 'rm -rf "$tmp_dir"' EXIT

exit_code=0

# Параллельный запуск линтеров
echo "Запуск линтеров..."
{
    poetry run ruff check ${SRC_DIR} ${TESTS_DIR} > "$tmp_dir/ruff.log" 2>&1 || echo "ruff:$?" > "$tmp_dir/ruff.exit"
} &

{
    poetry run black --check ${SRC_DIR} ${TESTS_DIR} > "$tmp_dir/black.log" 2>&1 || echo "black:$?" > "$tmp_dir/black.exit"
} &

{
    poetry run isort --check-only ${SRC_DIR} ${TESTS_DIR} > "$tmp_dir/isort.log" 2>&1 || echo "isort:$?" > "$tmp_dir/isort.exit"
} &

# Ожидание завершения всех процессов
wait

# Вывод результатов
echo "Результаты проверки:"
echo "===================="

if [ -f "$tmp_dir/ruff.exit" ]; then
    echo "Ошибки ruff:"
    cat "$tmp_dir/ruff.log"
    exit_code=1
fi

if [ -f "$tmp_dir/black.exit" ]; then
    echo "Ошибки black:"
    cat "$tmp_dir/black.log"
    exit_code=1
fi

if [ -f "$tmp_dir/isort.exit" ]; then
    echo "Ошибки isort:"
    cat "$tmp_dir/isort.log"
    exit_code=1
fi

if [ $exit_code -eq 0 ]; then
    echo "Проверка стиля кода завершена успешно"
else
    echo "Проверка стиля кода завершена с ошибками"
    exit $exit_code
fi