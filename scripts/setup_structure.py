#!/usr/bin/env python3
"""
Скрипт для настройки правильной структуры проекта.
Создает нужные директории и файлы, если они отсутствуют.
"""

from pathlib import Path


def create_directory(path: str) -> None:
    """Создать директорию, если она не существует."""
    Path(path).mkdir(parents=True, exist_ok=True)
    # Создать __init__.py если это пакет Python
    if Path(path).parent.name != "":  # Не создавать __init__.py в корне
        init_file = Path(path) / "__init__.py"
        if not init_file.exists():
            init_file.touch()
            print(f"Создан файл: {init_file}")
    print(f"Проверена директория: {path}")


def main() -> None:
    """Создать структуру проекта."""
    print("Настройка структуры проекта...")

    # Базовая структура приложения
    directories = [
        "src",
        "src/api",
        "src/api/v1",
        "src/api/v1/endpoints",
        "src/core",
        "src/db",
        "src/models",
        "src/schemas",
        "src/services",
        "src/repositories",
        "src/utils",
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/conftest",
        "migrations",
        "migrations/versions",
        "docs",
        "docs/source",
        "scripts",
    ]

    # Создание директорий
    for directory in directories:
        create_directory(directory)

    # Проверка базовых файлов
    base_files = [
        "src/main.py",
        "src/config.py",
        "src/api/v1/__init__.py",
        "src/api/v1/api.py",
        "src/core/security.py",
        "src/core/exceptions.py",
        "src/db/base.py",
        "src/db/session.py",
        "src/utils/logger.py",
        "tests/conftest.py",
        ".env.example",
        "README.md",
        "pyproject.toml",
    ]

    for file_path in base_files:
        if not Path(file_path).exists():
            print(f"ВНИМАНИЕ: Отсутствует файл {file_path}")

    # Проверка наличия дублирующих модулей
    print("\nПроверка дублирующих модулей...")
    potential_duplicates = [
        ("src/schemas.py", "src/schemas"),
        ("src/models.py", "src/models"),
        ("src/app/models", "src/models"),
        ("src/app/schemas", "src/schemas"),
        ("src/app", "src"),
    ]

    for source, target in potential_duplicates:
        if Path(source).exists() and Path(target).exists():
            print(f"НАЙДЕНО ДУБЛИРОВАНИЕ: {source} и {target}")

    print("\nСтруктура проекта настроена.")


if __name__ == "__main__":
    main()
