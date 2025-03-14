#!/usr/bin/env bash
set -e

# Скрипт для установки зависимостей
POETRY_VERSION="1.8.3"

echo "Проверка наличия poetry..."
if ! command -v poetry &> /dev/null; then
    echo "Poetry не установлен. Установка poetry..."
    curl -sSL --retry 3 --retry-delay 5 https://install.python-poetry.org | POETRY_HOME="${HOME}/.local/poetry" python3 - || {
        echo "Ошибка установки Poetry"
        exit 1
    }
    export PATH="${HOME}/.local/poetry/bin:$PATH"
fi

echo "Проверка версии Poetry..."
poetry_current_version=$(poetry --version 2>/dev/null | sed -n 's/.*version \([0-9.]*\).*/\1/p' || echo "0")
if [ "$poetry_current_version" != "${POETRY_VERSION}" ]; then
    echo "Неверная версия Poetry ($poetry_current_version). Переустановка на версию ${POETRY_VERSION}..."
    curl -sSL --retry 3 --retry-delay 5 https://install.python-poetry.org | POETRY_HOME="${HOME}/.local/poetry" python3 - --version ${POETRY_VERSION} || {
        echo "Ошибка переустановки Poetry"
        exit 1
    }
fi

echo "Настройка poetry..."
poetry config virtualenvs.in-project true || exit 1
poetry config virtualenvs.create true || exit 1

echo "Очистка кэша poetry..."
poetry cache clear . --all || true

echo "Проверка существующего poetry.lock..."
if [ -f "poetry.lock" ]; then
    echo "Бэкап poetry.lock..."
    cp poetry.lock poetry.lock.backup || true
fi

echo "Обновление poetry.lock..."
poetry lock --no-update || {
    echo "Ошибка при обновлении poetry.lock"
    if [ -f "poetry.lock.backup" ]; then
        echo "Восстановление poetry.lock из бэкапа..."
        mv poetry.lock.backup poetry.lock
    fi
    exit 1
}

echo "Установка зависимостей проекта..."
poetry install --no-root --sync --no-interaction || {
    echo "Ошибка установки зависимостей"
    if [ -f "poetry.lock.backup" ]; then
        echo "Восстановление poetry.lock из бэкапа..."
        mv poetry.lock.backup poetry.lock
    fi
    exit 1
}

if [ -f "poetry.lock.backup" ]; then
    rm poetry.lock.backup
fi

echo "Установка pre-commit хуков..."
if ! poetry run pre-commit install && poetry run pre-commit install --hook-type commit-msg; then
    echo "Ошибка установки pre-commit хуков"
    exit 1
fi

echo "Установка завершена успешно"