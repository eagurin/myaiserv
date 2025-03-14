"""
Инструмент для работы с файловой системой.
"""

import os
import shutil
from typing import Any, Dict

from app.core.base_mcp import MCPTool


class FileOperationsTool(MCPTool):
    """
    Инструмент для работы с файловой системой.
    Поддерживает операции чтения, записи, удаления и листинга файлов.
    """

    def __init__(self):
        super().__init__(
            name="file_operations",
            description="Операции с файловой системой: чтение, запись, удаление и листинг файлов",
        )
        self.parameters = {
            "operation": {
                "type": "string",
                "description": "Операция с файлом (read, write, delete, list)",
                "enum": ["read", "write", "delete", "list"],
            },
            "path": {
                "type": "string",
                "description": "Путь к файлу или директории",
            },
            "content": {
                "type": "string",
                "description": "Содержимое для записи в файл (только для операции write)",
            },
            "encoding": {
                "type": "string",
                "description": "Кодировка файла",
                "default": "utf-8",
            },
        }
        self.required_params = ["operation", "path"]

    async def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполнение операции с файловой системой.

        Args:
            params: Параметры операции
                operation: Операция (read, write, delete, list)
                path: Путь к файлу или директории
                content: Содержимое для записи (опционально)
                encoding: Кодировка (опционально)

        Returns:
            Результат операции
        """
        operation = params.get("operation")
        path = params.get("path")
        content = params.get("content", "")
        encoding = params.get("encoding", "utf-8")

        if not self.validate_params(params):
            return {
                "error": "Не указаны обязательные параметры",
                "required": self.required_params,
            }

        try:
            if operation == "read":
                return await self._read_file(path, encoding)
            elif operation == "write":
                return await self._write_file(path, content, encoding)
            elif operation == "delete":
                return await self._delete_file(path)
            elif operation == "list":
                return await self._list_directory(path)
            else:
                return {
                    "error": f"Неподдерживаемая операция: {operation}",
                    "supported": ["read", "write", "delete", "list"],
                }
        except Exception as e:
            return {
                "error": f"Ошибка при выполнении операции: {str(e)}",
                "operation": operation,
                "path": path,
            }

    async def _read_file(self, path: str, encoding: str) -> Dict[str, Any]:
        """Чтение файла."""
        if not os.path.exists(path):
            return {"error": f"Файл не найден: {path}"}

        if not os.path.isfile(path):
            return {"error": f"Путь не является файлом: {path}"}

        try:
            with open(path, encoding=encoding) as file:
                content = file.read()

            return {
                "success": True,
                "content": content,
                "path": path,
                "size": os.path.getsize(path),
            }
        except UnicodeDecodeError:
            # Попытка прочитать как бинарный файл
            with open(path, "rb") as file:
                content = file.read()

            return {
                "success": True,
                "content": "<binary-data>",
                "path": path,
                "size": os.path.getsize(path),
                "is_binary": True,
            }

    async def _write_file(
        self, path: str, content: str, encoding: str
    ) -> Dict[str, Any]:
        """Запись в файл."""
        try:
            # Создаем директории, если их нет
            os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)

            with open(path, "w", encoding=encoding) as file:
                file.write(content)

            return {
                "success": True,
                "path": path,
                "size": os.path.getsize(path),
                "bytes_written": len(content.encode(encoding)),
            }
        except Exception as e:
            return {"error": f"Ошибка при записи файла: {str(e)}"}

    async def _delete_file(self, path: str) -> Dict[str, Any]:
        """Удаление файла или директории."""
        if not os.path.exists(path):
            return {"error": f"Файл или директория не найдены: {path}"}

        try:
            if os.path.isfile(path):
                os.remove(path)
                return {
                    "success": True,
                    "path": path,
                    "type": "file",
                }
            elif os.path.isdir(path):
                shutil.rmtree(path)
                return {
                    "success": True,
                    "path": path,
                    "type": "directory",
                }
        except Exception as e:
            return {"error": f"Ошибка при удалении: {str(e)}"}

    async def _list_directory(self, path: str) -> Dict[str, Any]:
        """Вывод содержимого директории."""
        if not os.path.exists(path):
            return {"error": f"Директория не найдена: {path}"}

        if not os.path.isdir(path):
            return {"error": f"Путь не является директорией: {path}"}

        try:
            items = []
            for item in os.listdir(path):
                item_path = os.path.join(path, item)
                item_type = "file" if os.path.isfile(item_path) else "directory"
                items.append(
                    {
                        "name": item,
                        "type": item_type,
                        "size": (
                            os.path.getsize(item_path)
                            if os.path.isfile(item_path)
                            else None
                        ),
                    }
                )

            return {
                "success": True,
                "path": path,
                "items": items,
                "count": len(items),
            }
        except Exception as e:
            return {"error": f"Ошибка при получении списка файлов: {str(e)}"}
