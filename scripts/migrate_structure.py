#!/usr/bin/env python3
"""
Скрипт для миграции существующей структуры файлов проекта в новую структуру.
Перемещает файлы из устаревших директорий в соответствующие новые.
"""

import shutil
from pathlib import Path
from typing import Dict, List, Tuple


def safe_move(source: Path, target: Path) -> None:
    """
    Безопасно переместить файл из источника в цель.

    Args:
        source: Исходный путь файла
        target: Целевой путь файла
    """
    # Убедимся, что целевая директория существует
    target.parent.mkdir(parents=True, exist_ok=True)

    # Проверим наличие файла источника
    if not source.exists():
        print(f"ПРОПУЩЕНО: Исходный файл {source} не существует")
        return

    # Проверим, не существует ли уже целевой файл
    if target.exists():
        print(f"КОНФЛИКТ: Целевой файл {target} уже существует")

        # Обрабатываем директории и файлы по-разному
        if target.is_dir():
            print(f"  Целевой путь {target} является директорией, " f"слияние...")
            # Для директорий не создаем резервные копии, а просто сливаем содержимое
        else:
            # Для файлов создаем резервные копии
            backup = target.with_suffix(f"{target.suffix}.bak")
            shutil.copy2(target, backup)
            print(f"  Создана резервная копия: {backup}")

    # Создаем родительские директории, если их нет
    target.parent.mkdir(parents=True, exist_ok=True)

    # Перемещаем файл
    try:
        if source.is_dir():
            # Если это директория, копируем содержимое рекурсивно
            if target.exists() and target.is_dir():
                # Если целевая директория существует, копируем содержимое
                for item in source.glob("*"):
                    if item.is_file():
                        shutil.copy2(item, target / item.name)
                    else:
                        shutil.copytree(
                            item,
                            target / item.name,
                            dirs_exist_ok=True,
                        )
            else:
                # Иначе создаем новую директорию
                shutil.copytree(source, target, dirs_exist_ok=True)
            print(f"СКОПИРОВАНА ДИРЕКТОРИЯ: {source} -> {target}")
        else:
            # Если это файл, копируем
            shutil.copy2(source, target)
            print(f"СКОПИРОВАН ФАЙЛ: {source} -> {target}")
    except Exception as e:
        print(f"ОШИБКА при копировании {source} -> {target}: {str(e)}")


def relocate_files() -> None:
    """Переместить файлы в соответствующие директории новой структуры."""
    # Пары (источник, цель) для перемещения файлов
    relocations: List[Tuple[str, str]] = [
        # Перемещение схем
        ("src/schemas.py", "src/schemas/base.py"),
        # Перемещение моделей
        ("src/models.py", "src/models/base.py"),
        # Перемещение из app/models в models
        ("src/app/models", "src/models"),
        # Перемещение из app/schemas в schemas
        ("src/app/schemas", "src/schemas"),
        # Перемещение из app/api в api
        ("src/app/api", "src/api"),
        # Перемещение из app/core в core
        ("src/app/core", "src/core"),
        # Перемещение из app/utils в utils
        ("src/app/utils", "src/utils"),
        # Перемещение из app/db в db
        ("src/app/db", "src/db"),
        # Перемещение из app/services в services
        ("src/app/services", "src/services"),
        # Перемещение из app/repositories в repositories
        ("src/app/repositories", "src/repositories"),
        # Перемещение из app/crud в repositories/crud
        ("src/app/crud", "src/repositories/crud"),
    ]

    # Особые файлы для перемещения
    special_files: Dict[str, str] = {"src/app/main.py": "src/main.py"}

    # Обработка перемещений
    for source_str, target_str in relocations:
        source = Path(source_str)
        target = Path(target_str)

        if source.exists():
            print(f"Перемещение: {source} -> {target}")
            safe_move(source, target)

    # Обработка особых файлов
    for source_str, target_str in special_files.items():
        source = Path(source_str)
        target = Path(target_str)

        if source.exists() and not target.exists():
            print(f"Перемещение особого файла: {source} -> {target}")
            safe_move(source, target)


def main() -> None:
    """Выполнить миграцию структуры проекта."""
    print("Начало миграции структуры проекта...")

    # Сначала убедимся, что все нужные директории созданы
    try:
        # Импортируем и запускаем скрипт создания структуры
        from setup_structure import main as setup_main

        setup_main()
    except ImportError:
        print(
            "ВНИМАНИЕ: Скрипт setup_structure.py не найден, "
            "директории не будут созданы автоматически"
        )

    # Перемещаем файлы
    relocate_files()

    print("\nМиграция структуры проекта завершена.")
    print(
        "Примечание: Некоторые файлы могли быть только скопированы, " "а не перемещены."
    )
    print("Проверьте структуру и удалите ненужные файлы вручную.")


if __name__ == "__main__":
    main()
