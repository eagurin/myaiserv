#!/usr/bin/env bash
set -e

# Скрипт для очистки кеша и временных файлов
echo "Проверка прав доступа..."
if [ ! -w "." ]; then
    echo "Ошибка: нет прав на запись в текущую директорию"
    exit 1
fi

# Создание списка директорий для очистки
dirs_to_clean=(
    ".pytest_cache"
    ".coverage"
    ".mypy_cache"
    ".ruff_cache"
    "htmlcov"
    "dist"
    "build"
    ".eggs"
)

# Проверка и очистка каждой директории
for dir in "${dirs_to_clean[@]}"; do
    if [ -d "$dir" ]; then
        echo "Удаление $dir..."
        rm -rf "$dir" || {
            echo "Ошибка при удалении $dir"
            exit 1
        }
    fi
done

# Очистка Python кэша
echo "Очистка Python кэша..."
find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
find . -type f -name "*.pyc" -delete 2>/dev/null || true
find . -type f -name "*.pyo" -delete 2>/dev/null || true
find . -type f -name "*.pyd" -delete 2>/dev/null || true
find . -type f -name ".coverage" -delete 2>/dev/null || true
find . -type f -name "coverage.xml" -delete 2>/dev/null || true
find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
find . -type d -name "*.egg" -exec rm -rf {} + 2>/dev/null || true

# Очистка логов
if [ -d "logs" ]; then
    echo "Очистка логов..."
    rm -rf logs/* || {
        echo "Ошибка при очистке логов"
        exit 1
    }
fi

echo "Очистка завершена успешно"