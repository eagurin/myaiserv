"""
Инструмент для работы с файловой системой.
"""

import os
from typing import Any, Dict

from app.core.base.tool import MCPTool


class FileSystemTool(MCPTool):
    """Инструмент для базовых операций с файловой системой."""

    def __init__(self) -> None:
        super().__init__()
        # Используем текущую директорию проекта
        self.base_dir = os.path.abspath(os.getcwd())
        self.name = "file_operations"
        self.description = "Perform basic file system operations"
        self.input_schema = {
            "type": "object",
            "properties": {
                "operation": {
                    "type": "string",
                    "enum": ["read", "write", "list", "delete"],
                    "description": "File operation to perform",
                },
                "path": {
                    "type": "string",
                    "description": (
                        "File or directory path (relative to project root)"
                    ),
                },
                "content": {
                    "type": "string",
                    "description": "Content to write (for write operation)",
                },
            },
            "required": ["operation", "path"],
        }

    def _validate_path(self, path: str) -> str:
        """
        Validates and normalizes path to ensure it's within allowed directory
        """
        # Convert to absolute path
        if os.path.isabs(path):
            full_path = path
        else:
            full_path = os.path.abspath(os.path.join(self.base_dir, path))

        # Ensure path is within base directory
        if not full_path.startswith(self.base_dir):
            raise ValueError(f"Access denied: Path must be within {self.base_dir}")

        return full_path

    async def initialize(self) -> bool:
        return True

    async def cleanup(self) -> bool:
        return True

    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            operation = parameters["operation"]
            path = parameters["path"]

            # Валидация пути
            try:
                path = self._validate_path(path)
            except ValueError as e:
                return {
                    "content": [{"type": "text", "text": str(e)}],
                    "isError": True,
                }

            # Выполнение операции
            if operation == "read":
                result = await self._read_file(path)
            elif operation == "write":
                result = await self._write_file(path, parameters.get("content", ""))
            elif operation == "list":
                result = await self._list_directory(path)
            elif operation == "delete":
                result = await self._delete_file(path)
            else:
                return {
                    "content": [
                        {"type": "text", "text": f"Unknown operation: {operation}"}
                    ],
                    "isError": True,
                }

            return {"content": [{"type": "text", "text": result}]}

        except Exception as e:
            error_msg = f"Error during file operation: {str(e)}"
            if "path" in locals():
                error_msg += f"\nPath: {path}\nExists: {os.path.exists(path)}"
                error_msg += f"\nIs Dir: {os.path.isdir(path)}"
            return {
                "content": [{"type": "text", "text": error_msg}],
                "isError": True,
            }

    async def _read_file(self, path: str) -> str:
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found: {path}")

            with open(path, encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            raise ValueError(f"Error reading file: {str(e)}")

    async def _write_file(self, path: str, content: str) -> str:
        try:
            with open(path, "w", encoding="utf-8") as f:
                f.write(content)

            return "File written successfully"
        except Exception as e:
            raise ValueError(f"Error writing file: {str(e)}")

    async def _list_directory(self, path: str) -> str:
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Directory not found: {path}")

            if not os.path.isdir(path):
                raise NotADirectoryError(f"Not a directory: {path}")

            # Получаем список файлов и директорий
            entries = os.listdir(path)
            result = []

            # Добавляем информацию о каждом элементе
            for entry in sorted(entries):
                entry_path = os.path.join(path, entry)
                if os.path.isdir(entry_path):
                    entry_type = "directory"
                else:
                    entry_type = "file"

                try:
                    size = os.path.getsize(entry_path)
                    modified = os.path.getmtime(entry_path)
                except Exception:
                    size = 0
                    modified = 0

                result.append(
                    f"{entry} ({entry_type}, "
                    f"size: {size} bytes, "
                    f"modified: {modified})"
                )

            if not result:
                return "Directory is empty"

            return "\n".join(result)
        except Exception as e:
            raise ValueError(f"Error listing directory: {str(e)}")

    async def _delete_file(self, path: str) -> str:
        try:
            if not os.path.exists(path):
                raise FileNotFoundError(f"File not found: {path}")

            if os.path.isdir(path):
                os.rmdir(path)  # Удаляем только пустые директории
            else:
                os.remove(path)

            return "File deleted successfully"
        except Exception as e:
            raise ValueError(f"Error deleting file: {str(e)}")
