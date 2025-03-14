#!/usr/bin/env python3
"""
Скрипт для обновления тестов после реструктуризации проекта.
Проверяет и исправляет пути импортов и фикстуры в тестах.
"""

import re
import sys
from pathlib import Path
from typing import Dict, List, Set


def find_test_files() -> List[Path]:
    """
    Найти все Python-файлы тестов в проекте.

    Returns:
        Список путей к файлам тестов
    """
    test_dir = Path("tests")
    if not test_dir.exists() or not test_dir.is_dir():
        print("ОШИБКА: Директория tests не найдена")
        return []

    return list(test_dir.rglob("test_*.py"))


def find_fixtures_in_conftest() -> Set[str]:
    """
    Найти все фикстуры в файлах conftest.py.

    Returns:
        Множество имен фикстур
    """
    fixtures = set()
    conftest_files = list(Path("tests").glob("**/conftest.py"))

    for conftest_file in conftest_files:
        try:
            with open(conftest_file, encoding="utf-8") as file:
                content = file.read()

                # Ищем определения фикстур
                for match in re.finditer(
                    r"@pytest\.fixture\s*(\([^)]*\))?\s*\ndef\s+" r"([a-zA-Z0-9_]+)",
                    content,
                ):
                    fixture_name = match.group(2)
                    fixtures.add(fixture_name)
        except Exception as e:
            print(f"ОШИБКА при чтении {conftest_file}: {str(e)}")

    return fixtures


def update_test_file(
    file_path: Path,
    fixtures: Set[str],
    import_map: Dict[str, str],
) -> bool:
    """
    Обновить импорты и использование в тестовом файле.

    Args:
        file_path: Путь к файлу теста
        fixtures: Множество имен доступных фикстур
        import_map: Словарь соответствия старых и новых путей импорта

    Returns:
        True, если были внесены изменения, иначе False
    """
    try:
        with open(file_path, encoding="utf-8") as file:
            content = file.read()

        # Сохраняем флаг изменений
        changed = False

        # Обновляем импорты
        for old_path, new_path in import_map.items():
            # Экранируем точки правильно для регулярных выражений
            old_esc = old_path.replace(".", r"\.")

            # Шаблоны для различных видов импорта
            patterns = [
                (
                    rf"from\s+{old_esc}\s+import\s+",
                    f"from {new_path} import ",
                ),
                (
                    rf"import\s+{old_esc}\b",
                    f"import {new_path}",
                ),
                (
                    rf"import\s+{old_esc}\s+as\s+",
                    f"import {new_path} as ",
                ),
            ]

            for pattern, replacement in patterns:
                new_content = re.sub(pattern, replacement, content)
                if new_content != content:
                    content = new_content
                    changed = True

        # Проверяем использование фикстур
        for fixture in fixtures:
            # Ищем использование фикстуры как аргумента функции
            for test_func_match in re.finditer(
                r"def\s+test_\w+\s*\(([^)]*)\):",
                content,
            ):
                args = test_func_match.group(1)
                if (
                    fixture in [a.strip() for a in args.split(",")]
                    and f"@pytest.mark.usefixtures('{fixture}')" not in content
                    and f'@pytest.mark.usefixtures("{fixture}")' not in content
                ):
                    # Фикстура используется, нет необходимости в изменениях
                    pass

        # Если были изменения, записываем файл
        if changed:
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(content)
            return True

        return False
    except Exception as e:
        print(f"ОШИБКА при обновлении {file_path}: {str(e)}")
        return False


def main() -> int:
    """
    Запустить обновление тестов после реструктуризации.

    Returns:
        Код возврата (0 - успех, 1 - ошибка)
    """
    print("Начало обновления тестов после реструктуризации...")

    # Карта соответствия импортов
    import_map = {
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

    # Находим все файлы тестов
    test_files = find_test_files()
    if not test_files:
        print("Файлы тестов не найдены")
        return 1

    print(f"Найдено тестовых файлов: {len(test_files)}")

    # Находим все фикстуры
    fixtures = find_fixtures_in_conftest()
    print(f"Найдено фикстур: {len(fixtures)}")

    # Обновляем каждый файл теста
    updated_count = 0
    for test_file in test_files:
        if update_test_file(test_file, fixtures, import_map):
            updated_count += 1
            print(f"Обновлен тестовый файл: {test_file}")

    print(f"Обновлено тестовых файлов: {updated_count} из {len(test_files)}")

    print("\nОбновление тестов завершено.")
    return 0 if updated_count > 0 or len(test_files) == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
