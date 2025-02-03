import asyncio
import json
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, AsyncGenerator, Dict, List, Optional


class BaseMCPComponent(ABC):
    """Базовый класс для всех MCP компонентов"""

    def __init__(self, name: str, description: str = None):
        self.name = name
        self.description = description
        self._subscribers: Dict[str, List[AsyncGenerator]] = {}
        self._error_handlers: List[callable] = []

    async def notify_subscribers(self, event_type: str, data: Any) -> None:
        """Оповещение подписчиков о событии"""
        if event_type in self._subscribers:
            for subscriber in self._subscribers[event_type]:
                try:
                    await subscriber.asend(data)
                except Exception as e:
                    await self.handle_error(e)

    async def subscribe(self, event_type: str) -> AsyncGenerator:
        """Подписка на события компонента"""
        if event_type not in self._subscribers:
            self._subscribers[event_type] = []

        queue = asyncio.Queue()
        self._subscribers[event_type].append(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            self._subscribers[event_type].remove(queue)

    def add_error_handler(self, handler: callable) -> None:
        """Добавление обработчика ошибок"""
        self._error_handlers.append(handler)

    async def handle_error(self, error: Exception) -> None:
        """Обработка ошибок"""
        for handler in self._error_handlers:
            try:
                await handler(error)
            except Exception:
                pass

    @abstractmethod
    async def initialize(self) -> None:
        """Инициализация компонента"""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Очистка ресурсов"""
        pass

    def to_dict(self) -> Dict[str, Any]:
        """Сериализация компонента"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BaseMCPComponent":
        """Десериализация компонента"""
        return cls(name=data["name"], description=data.get("description"))

    async def validate(self) -> bool:
        """Валидация компонента"""
        return True

    async def log_event(self, event_type: str, data: Any) -> None:
        """Логирование события"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "component": self.name,
            "type": event_type,
            "data": data,
        }
        await self.notify_subscribers("log", event)


class MCPTool(BaseMCPComponent):
    """Базовый класс для инструментов"""

    def __init__(
        self, name: str, description: str, input_schema: Dict[str, Any]
    ):
        super().__init__(name, description)
        self.input_schema = input_schema

    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Выполнение инструмента"""
        pass


class MCPResource(BaseMCPComponent):
    """Базовый класс для ресурсов"""

    def __init__(self, name: str, uri: str, mime_type: str = None):
        super().__init__(name)
        self.uri = uri
        self.mime_type = mime_type

    @abstractmethod
    async def read(self) -> Any:
        """Чтение ресурса"""
        pass

    @abstractmethod
    async def write(self, data: Any) -> None:
        """Запись в ресурс"""
        pass


class MCPPrompt(BaseMCPComponent):
    """Базовый класс для промптов"""

    def __init__(
        self, name: str, description: str, arguments: List[Dict[str, Any]]
    ):
        super().__init__(name, description)
        self.arguments = arguments

    @abstractmethod
    async def generate(
        self, arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """Генерация сообщений"""
        pass
