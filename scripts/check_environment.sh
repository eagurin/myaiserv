#!/usr/bin/env bash
set -e

# Скрипт для проверки окружения
PYTHON_VERSION="3.12"

# Проверка версии Python
echo "Проверка версии Python..."
python_version=$(python -V 2>&1 | cut -d' ' -f2)
if [[ "$python_version" != ${PYTHON_VERSION}* ]]; then
    echo "Ошибка: требуется Python ${PYTHON_VERSION}"
    exit 1
fi

# Проверка свободного места
echo "Проверка свободного места на диске..."
if [ $(df -P . | awk 'NR==2 {print $4}') -lt 1048576 ]; then
    echo "Ошибка: недостаточно свободного места"
    exit 1
fi

echo "Проверка окружения завершена успешно"