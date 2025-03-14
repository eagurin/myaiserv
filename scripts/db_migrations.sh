#!/usr/bin/env bash
set -e

# Скрипт для работы с миграциями базы данных
# Первый аргумент - операция (revision, upgrade, downgrade)
# Второй аргумент - сообщение для миграции (только для revision)

if [ "$1" = "revision" ]; then
    message="$2"
    if [ -z "$message" ]; then
        echo "Ошибка: необходимо указать сообщение для миграции"
        exit 1
    fi
    
    echo "Создание миграции: $message"
    if [ ! -f "alembic.ini" ]; then
        echo "Ошибка: файл alembic.ini не найден"
        exit 1
    fi

    # Проверка подключения к БД
    if ! poetry run alembic current &>/dev/null; then
        echo "Ошибка: нет подключения к базе данных"
        exit 1
    fi

    # Проверка директории миграций
    if [ ! -d "migrations" ]; then
        echo "Ошибка: директория migrations не существует"
        exit 1
    fi

    # Проверка прав на запись в директорию миграций
    if [ ! -w "migrations" ]; then
        echo "Ошибка: нет прав на запись в директорию migrations"
        exit 1
    fi
    
    poetry run alembic revision --autogenerate -m "$message"
    echo "Миграция создана успешно"
    
elif [ "$1" = "upgrade" ]; then
    echo "Применение миграций..."
    if [ ! -f "alembic.ini" ]; then
        echo "Ошибка: файл alembic.ini не найден"
        exit 1
    fi
    poetry run alembic upgrade head
    echo "Миграции применены успешно"
    
elif [ "$1" = "downgrade" ]; then
    echo "Откат последней миграции..."
    if [ ! -f "alembic.ini" ]; then
        echo "Ошибка: файл alembic.ini не найден"
        exit 1
    fi
    poetry run alembic downgrade -1
    echo "Миграция откачена успешно"
    
else
    echo "Ошибка: неверная операция. Используйте revision, upgrade или downgrade"
    exit 1
fi