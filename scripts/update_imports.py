#!/usr/bin/env python3
"""
Скрипт для обновления импортов в проекте после изменения структуры.
Заменяет старые пути импортов на новые соответствующие пути.
"""

import re
from pathlib import Path
from re import Pattern
from typing import Dict, List, Tuple


def build_import_patterns() -> List[Tuple[Pattern[str], str]]:
    """
    Создать список шаблонов для замены импортов.

    Returns:
        Список кортежей (шаблон регулярного выражения, замена)
    """
    # Определим карту замен импортов в формате:
    # {старый_путь_импорта: новый_путь_импорта}
    import_map: Dict[str, str] = {
        "src.app.models": "src.models",
        "src.app.schemas": "src.schemas",
        "src.app.api": "src.api",
        "src.app.core": "src.core",
        "src.app.db": "src.db",
        "src.app.services": "src.services",
        "src.app.utils": "src.utils",
        "src.app.crud": "src.repositories.crud",
        "src.app.repositories": "src.repositories",
        "src.app.main": "src.main",
        "src.schemas": "src.schemas.base",
        "src.models": "src.models.base",
    }

    # Создаем шаблоны для каждого импорта
    patterns: List[Tuple[Pattern[str], str]] = []

    for old, new in import_map.items():
        # Экранируем точки правильно для регулярных выражений
        old_esc = old.replace(".", r"\.")

        # Для импортов from X import Y
        from_pattern = re.compile(
            rf"from\s+{old_esc}\s+import\s+",
        )
        from_replace = f"from {new} import "
        patterns.append((from_pattern, from_replace))

        # Для импортов import X
        import_pattern = re.compile(
            rf"import\s+{old_esc}\b",
        )
        import_replace = f"import {new}"
        patterns.append((import_pattern, import_replace))

        # Для импортов import X as Y
        import_as_pattern = re.compile(
            rf"import\s+{old_esc}\s+as\s+",
        )
        import_as_replace = f"import {new} as "
        patterns.append((import_as_pattern, import_as_replace))

    return patterns


def update_file_imports(
    file_path: Path,
    patterns: List[Tuple[Pattern[str], str]],
) -> bool:
    """
    Обновить импорты в одном файле.

    Args:
        file_path: Путь к файлу для обновления
        patterns: Список шаблонов для замены

    Returns:
        True, если были внесены изменения, иначе False
    """
    try:
        # Читаем содержимое файла
        with open(file_path, encoding="utf-8") as file:
            content = file.read()

        # Сохраняем оригинальное содержимое для сравнения
        original_content = content

        # Применяем все шаблоны замены
        for pattern, replacement in patterns:
            content = pattern.sub(replacement, content)

        # Если были изменения, записываем файл
        if content != original_content:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            return True

        return False
    except Exception as e:
        print(f"ОШИБКА при обновлении импортов в {file_path}: {str(e)}")
        return False


def update_imports() -> None:
    """Обновить импорты во всех Python файлах проекта."""
    print("Обновление импортов в Python файлах...")

    # Создаем шаблоны для замены
    patterns = build_import_patterns()

    # Ищем все Python файлы в проекте
    python_files = list(Path("src").rglob("*.py")) + list(Path("tests").rglob("*.py"))

    # Обрабатываем каждый файл
    updated_count = 0
    for file_path in python_files:
        if update_file_imports(file_path, patterns):
            updated_count += 1
            print(f"Обновлены импорты: {file_path}")

    print(f"Всего обновлено файлов: {updated_count} из {len(python_files)}")


def main() -> None:
    """Запустить обновление импортов."""
    print("Начало обновления импортов...")

    update_imports()

    print("\nОбновление импортов завершено.")
    print(
        "Примечание: Возможно, потребуется вручная проверка и исправление "
        "некоторых сложных случаев импорта."
    )


if __name__ == "__main__":
    main()
