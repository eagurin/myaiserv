import json
import os
from datetime import datetime
from typing import Any, Dict, Optional

import aiofiles

from .base_mcp import MCPResource


class FileResource(MCPResource):
    """Базовый класс для файловых ресурсов"""

    def __init__(self, name: str, path: str, mime_type: str = "text/plain"):
        uri = f"file://{path}"
        super().__init__(name, uri, mime_type)
        self.path = path

    async def read(self) -> Any:
        """Чтение файла"""
        if not os.path.exists(self.path):
            raise FileNotFoundError(f"File not found: {self.path}")

        async with aiofiles.open(self.path, "r") as f:
            content = await f.read()
            await self.log_event("read", {"path": self.path})
            return content

    async def write(self, data: Any) -> None:
        """Запись в файл"""
        async with aiofiles.open(self.path, "w") as f:
            await f.write(str(data))
            await self.log_event("write", {"path": self.path})

    async def initialize(self) -> None:
        """Инициализация ресурса"""
        os.makedirs(os.path.dirname(self.path), exist_ok=True)

    async def cleanup(self) -> None:
        """Очистка ресурса"""
        pass


class JSONResource(FileResource):
    """Ресурс для работы с JSON файлами"""

    def __init__(self, name: str, path: str):
        super().__init__(name, path, "application/json")

    async def read(self) -> Any:
        """Чтение JSON файла"""
        content = await super().read()
        return json.loads(content)

    async def write(self, data: Any) -> None:
        """Запись в JSON файл"""
        content = json.dumps(data, indent=2)
        await super().write(content)


class MemoryResource(MCPResource):
    """Ресурс для хранения данных в памяти"""

    def __init__(self, name: str, mime_type: str = "application/json"):
        uri = f"memory://{name}"
        super().__init__(name, uri, mime_type)
        self._data: Any = None
        self._last_modified: Optional[datetime] = None

    async def read(self) -> Any:
        """Чтение данных из памяти"""
        if self._data is None:
            raise ValueError("No data available")
        await self.log_event("read", {"timestamp": self._last_modified})
        return self._data

    async def write(self, data: Any) -> None:
        """Запись данных в память"""
        self._data = data
        self._last_modified = datetime.now()
        await self.log_event("write", {"timestamp": self._last_modified})

    async def initialize(self) -> None:
        """Инициализация ресурса"""
        self._data = None
        self._last_modified = None

    async def cleanup(self) -> None:
        """Очистка ресурса"""
        self._data = None
        self._last_modified = None


class APIResource(MCPResource):
    """Ресурс для работы с API"""

    def __init__(self, name: str, base_url: str, mime_type: str = "application/json"):
        uri = f"api://{base_url}"
        super().__init__(name, uri, mime_type)
        self.base_url = base_url
        self._headers: Dict[str, str] = {}

    async def read(self) -> Any:
        """Чтение данных из API"""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.get(self.base_url, headers=self._headers)
            response.raise_for_status()
            await self.log_event("read", {"url": self.base_url})
            return response.json()

    async def write(self, data: Any) -> None:
        """Отправка данных в API"""
        import httpx

        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.base_url, headers=self._headers, json=data
            )
            response.raise_for_status()
            await self.log_event("write", {"url": self.base_url})

    def set_headers(self, headers: Dict[str, str]) -> None:
        """Установка заголовков для API запросов"""
        self._headers.update(headers)

    async def initialize(self) -> None:
        """Инициализация ресурса"""
        self._headers = {
            "Content-Type": self.mime_type,
            "Accept": self.mime_type,
        }

    async def cleanup(self) -> None:
        """Очистка ресурса"""
        self._headers.clear()
