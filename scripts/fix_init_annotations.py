#!/usr/bin/env python
"""
Скрипт для исправления аннотаций типов в методах __init__.
Исправляет ошибки, когда аннотация возвращаемого значения -> None
добавлена в неправильное место.
"""

import os
import re
from pathlib import Path


def fix_init_annotations(file_path: str) -> None:
    """
    Исправляет аннотации типов в методах __init__ в указанном файле.

    Args:
        file_path: Путь к файлу для исправления
    """
    with open(file_path, encoding="utf-8") as file:
        content = file.read()

    # Ищем паттерн: def __init__(self, param -> None: Type):
    pattern = r"def __init__\((.*?)\s+->\s+None:\s+(.*?)\):"

    # Заменяем на: def __init__(self, param: Type) -> None:
    fixed_content = re.sub(pattern, r"def __init__(\1: \2) -> None:", content)

    if content != fixed_content:
        with open(file_path, "w", encoding="utf-8") as file:
            file.write(fixed_content)
        print(f"Исправлен файл: {file_path}")


def process_python_files(directory: str) -> None:
    """
    Обрабатывает все Python файлы в директории и её поддиректориях.

    Args:
        directory: Путь к директории для обработки
    """
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                fix_init_annotations(file_path)


if __name__ == "__main__":
    src_dir = Path(__file__).parent.parent / "src"
    process_python_files(str(src_dir))
    print("Готово! Аннотации типов исправлены.")
