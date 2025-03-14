#!/usr/bin/env python3
"""
Основной скрипт для полной реструктуризации проекта.
Запускает последовательно все скрипты реструктуризации и создает бэкап.
"""

import os
import shutil
import subprocess
import sys
import time
from datetime import datetime


def create_backup() -> str:
    """
    Создать бэкап проекта перед реструктуризацией.

    Returns:
        Путь к созданному бэкапу
    """
    backup_dir = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    print(f"Создание бэкапа проекта в: {backup_dir}...")

    # Создаем директорию для бэкапа
    os.makedirs(backup_dir, exist_ok=True)

    # Определяем что копировать
    dirs_to_backup = ["src", "tests", "migrations"]
    files_to_backup = []

    for root, _, files in os.walk("."):
        # Пропускаем служебные директории
        if (
            ".git" in root
            or ".venv" in root
            or "__pycache__" in root
            or ".mypy_cache" in root
            or ".ruff_cache" in root
            or backup_dir in root
        ):
            continue

        # Собираем файлы из корня проекта
        if root == ".":
            for file in files:
                if file.endswith((".py", ".md", ".toml", ".ini", ".cfg")):
                    files_to_backup.append(file)

    # Копируем директории
    for directory in dirs_to_backup:
        if os.path.exists(directory):
            shutil.copytree(
                directory,
                os.path.join(backup_dir, directory),
                symlinks=True,
                ignore=shutil.ignore_patterns(
                    "__pycache__",
                    "*.pyc",
                    ".mypy_cache",
                    ".ruff_cache",
                ),
            )

    # Копируем файлы
    for file in files_to_backup:
        if os.path.exists(file):
            shutil.copy2(file, os.path.join(backup_dir, file))

    print(f"Бэкап создан в директории: {backup_dir}")
    return backup_dir


def run_script(script_name: str) -> bool:
    """
    Запустить Python скрипт и вернуть результат выполнения.

    Args:
        script_name: Имя скрипта для запуска

    Returns:
        True если скрипт выполнен успешно, иначе False
    """
    script_path = os.path.join("scripts", script_name)

    if not os.path.exists(script_path):
        print(f"ОШИБКА: Скрипт {script_path} не найден")
        return False

    print(f"\n{'=' * 50}")
    print(f"Запуск скрипта: {script_name}")
    print(f"{'=' * 50}\n")

    try:
        result = subprocess.run(
            [sys.executable, script_path],
            check=True,
            capture_output=True,
            text=True,
        )
        print(result.stdout)
        if result.stderr:
            print(f"ПРЕДУПРЕЖДЕНИЯ:\n{result.stderr}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"ОШИБКА при выполнении скрипта {script_name}:")
        print(e.stdout)
        print(f"Код ошибки: {e.returncode}")
        print(f"Ошибка: {e.stderr}")
        return False


def main() -> int:
    """
    Запустить полную реструктуризацию проекта.

    Returns:
        Код возврата (0 - успех, 1 - ошибка)
    """
    start_time = time.time()
    print("Начало полной реструктуризации проекта...")

    # Создание бэкапа
    backup_dir = create_backup()

    # Список скриптов для выполнения в порядке запуска
    scripts = [
        "setup_structure.py",
        "migrate_structure.py",
        "update_imports.py",
        "update_tests.py",
    ]

    # Запуск скриптов по очереди
    failed_scripts = []
    for script in scripts:
        if not run_script(script):
            failed_scripts.append(script)

    # Вывод результатов
    elapsed_time = time.time() - start_time
    print("\n" + "=" * 50)
    print("Результаты реструктуризации:")
    print(f"Общее время выполнения: {elapsed_time:.2f} секунд")
    print(f"Создан бэкап: {backup_dir}")

    if failed_scripts:
        print("\nНЕ УДАЛОСЬ ВЫПОЛНИТЬ СЛЕДУЮЩИЕ СКРИПТЫ:")
        for script in failed_scripts:
            print(f"- {script}")
        print("\nПроект мог быть реструктуризирован частично.")
        print("Проверьте ошибки выше и выполните оставшиеся шаги вручную.")
        return 1
    else:
        print("\nРеструктуризация проекта УСПЕШНО ЗАВЕРШЕНА!")
        print("\nПосле проверки работоспособности проекта вы можете:")
        print("1. Удалить директорию src/app, если все работает корректно")
        print("2. Запустить тесты для проверки целостности проекта")
        return 0


if __name__ == "__main__":
    sys.exit(main())
