#!/usr/bin/env python
"""
Скрипт для автоматического исправления отсутствующих аннотаций типов в проекте.
Ищет функции без аннотаций возвращаемых значений и добавляет их.
"""

import ast
import os
import re
from pathlib import Path
from typing import List, Tuple


class FunctionVisitor(ast.NodeVisitor):
    """Посещает все функции в AST и находит те, у которых отсутствуют аннотации типов."""

    def __init__(self) -> None:
        self.functions_without_return_annotation = []
        self.functions_without_arg_annotations = []

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """Посещает определение функции и проверяет аннотации."""
        # Проверяем аннотацию возвращаемого значения
        if node.returns is None:
            self.functions_without_return_annotation.append(node)

        # Проверяем аннотации аргументов
        for arg in node.args.args:
            if arg.annotation is None and arg.arg != "self" and arg.arg != "cls":
                self.functions_without_arg_annotations.append((node, arg))

        self.generic_visit(node)


def find_functions_without_annotations(
    file_path: str,
) -> Tuple[List[ast.FunctionDef], List[Tuple[ast.FunctionDef, ast.arg]]]:
    """Находит функции без аннотаций типов в файле."""
    with open(file_path, encoding="utf-8") as file:
        content = file.read()

    try:
        tree = ast.parse(content)
        visitor = FunctionVisitor()
        visitor.visit(tree)
        return (
            visitor.functions_without_return_annotation,
            visitor.functions_without_arg_annotations,
        )
    except SyntaxError:
        print(f"Ошибка синтаксиса в файле {file_path}")
        return [], []


def add_return_annotation(file_path: str, function: ast.FunctionDef) -> None:
    """Добавляет аннотацию возвращаемого значения к функции."""
    with open(file_path, encoding="utf-8") as file:
        lines = file.readlines()

    # Находим строку с определением функции
    line_idx = function.lineno - 1
    line = lines[line_idx]

    # Проверяем, есть ли в функции return с значением
    has_return_value = False
    for node in ast.walk(function):
        if isinstance(node, ast.Return) and node.value is not None:
            has_return_value = True
            break

    # Определяем тип возвращаемого значения
    return_annotation = " -> None" if not has_return_value else " -> Any"

    # Добавляем аннотацию перед двоеточием
    if ":" in line:
        new_line = line.replace(":", f"{return_annotation}:", 1)
        lines[line_idx] = new_line

        # Добавляем импорт Any, если необходимо
        if return_annotation == " -> Any" and "from typing import Any" not in "".join(
            lines
        ):
            for i, line in enumerate(lines):
                if line.startswith("import ") or line.startswith("from "):
                    if "typing" in line and "Any" not in line:
                        # Добавляем Any к существующему импорту из typing
                        if "import " in line and "from typing" in line:
                            match = re.search(r"from typing import (.*)", line)
                            if match:
                                imports = match.group(1).strip()
                                if imports.endswith(","):
                                    lines[i] = line.replace(
                                        imports,
                                        f"{imports} Any",
                                    )
                                else:
                                    lines[i] = line.replace(
                                        imports,
                                        f"{imports}, Any",
                                    )
                                break
                    elif i == 0 or not lines[i - 1].startswith("from typing"):
                        # Добавляем новый импорт
                        lines.insert(i, "from typing import Any\n")
                        break

    with open(file_path, "w", encoding="utf-8") as file:
        file.writelines(lines)


def process_python_files(directory: str) -> None:
    """Обрабатывает все Python файлы в директории и её поддиректориях."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith(".py"):
                file_path = os.path.join(root, file)
                (
                    functions_without_return,
                    functions_without_args,
                ) = find_functions_without_annotations(file_path)

                if functions_without_return:
                    print(
                        f"Файл {file_path} содержит "
                        f"{len(functions_without_return)} функций "
                        f"без аннотаций возвращаемого значения"
                    )
                    for function in functions_without_return:
                        add_return_annotation(file_path, function)
                        print(f"  Добавлена аннотация для функции {function.name}")


if __name__ == "__main__":
    src_dir = Path(__file__).parent.parent / "src"
    process_python_files(str(src_dir))
    print("Готово! Аннотации типов добавлены.")
