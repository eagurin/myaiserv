"""
Базовые абстрактные классы для реализации Model Context Protocol (MCP).
"""

import asyncio
from abc import ABC, abstractmethod
from collections.abc import AsyncGenerator
from datetime import datetime
from typing import Any, Callable, Optional, Protocol, TypeVar, Union

from pydantic import BaseModel

T = TypeVar("T")


class MCPTool(BaseModel):
    """Базовый класс для инструментов MCP."""

    name: str
    description: str
    version: str = "1.0.0"
    parameters: dict[str, Any] = {}
    required_params: list[str] = []

    def validate_params(self, params: dict[str, Any]) -> bool:
        """Проверка наличия всех обязательных параметров."""
        return all(param in params for param in self.required_params)

    @abstractmethod
    async def execute(self, params: dict[str, Any]) -> dict[str, Any]:
        """Выполнение инструмента с переданными параметрами."""
        pass


class MCPContent(BaseModel):
    """Модель содержимого для MCP."""

    type: str  # text, image, audio, etc.
    text: Optional[str] = None
    url: Optional[str] = None
    data: Optional[Any] = None


class MCPResponse(BaseModel):
    """Модель ответа от MCP инструмента."""

    content: Union[MCPContent, list[MCPContent]]
    is_error: bool = False
    message: Optional[str] = None


class MCPToolRegistry(ABC):
    """Реестр для управления инструментами MCP."""

    @abstractmethod
    async def register_tool(self, tool: MCPTool) -> bool:
        """Регистрация нового инструмента."""
        pass

    @abstractmethod
    async def get_tool(self, name: str) -> Optional[MCPTool]:
        """Получение инструмента по имени."""
        pass

    @abstractmethod
    async def list_tools(self) -> list[MCPTool]:
        """Получение списка всех доступных инструментов."""
        pass

    @abstractmethod
    async def execute_tool(
        self,
        name: str,
        params: dict[str, Any],
    ) -> MCPResponse:
        """Выполнение инструмента по имени."""
        pass


class MCPContext(BaseModel):
    """Контекст для работы с MCP."""

    id: str
    prompt: Optional[str] = None
    messages: list[dict[str, Any]] = []
    tools: list[dict[str, Any]] = []
    metadata: dict[str, Any] = {}


class BaseMCPComponent(ABC):
    """Базовый класс для всех MCP компонентов"""

    def __init__(self, name: str, description: Optional[str] = None):
        self.name = name
        self.description = description
        self._subscribers: dict[str, list[AsyncGenerator]] = {}
        self._error_handlers: list[Callable[[Exception], None]] = []

    async def notify_subscribers(self, event_type: str, data: Any) -> None:
        """Оповещение подписчиков о событии"""
        if event_type in self._subscribers:
            for subscriber in self._subscribers[event_type]:
                try:
                    await subscriber.asend(data)
                except Exception as e:
                    await self.handle_error(e)

    def add_error_handler(self, handler: Callable[[Exception], None]) -> None:
        """Добавление обработчика ошибок"""
        self._error_handlers.append(handler)

    @abstractmethod
    async def subscribe(self, event_type: str) -> AsyncGenerator:
        """Подписка на события компонента"""
        pass

    @abstractmethod
    async def handle_error(self, error: Exception) -> None:
        """Обработка ошибок компонента"""
        pass

    @abstractmethod
    async def initialize(self) -> None:
        """Инициализация компонента"""
        pass

    @abstractmethod
    async def cleanup(self) -> None:
        """Очистка ресурсов компонента"""
        pass

    def to_dict(self) -> dict[str, Any]:
        """Сериализация компонента"""
        return {
            "name": self.name,
            "description": self.description,
            "type": self.__class__.__name__,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "BaseMCPComponent":
        """Создание компонента из словаря"""
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
        )

    async def validate(self) -> bool:
        """Валидация компонента"""
        return True

    async def log_event(self, event_type: str, data: Any) -> None:
        """Логирование событий компонента"""
        event = {
            "timestamp": datetime.now().isoformat(),
            "component": self.name,
            "type": event_type,
            "data": data,
        }
        await self.notify_subscribers("log", event)


class Observer(Protocol):
    async def update(self, uri: str, data: Any) -> None:
        pass


class Observable(ABC):
    def __init__(self) -> None:
        self._observers: dict[str, list[Observer]] = {}

    async def notify_observers(self, uri: str, data: Any) -> None:
        for observer in self._observers.get(uri, []):
            await observer.update(uri, data)

    def add_observer(self, uri: str, observer: Observer) -> None:
        if uri not in self._observers:
            self._observers[uri] = []
        if observer not in self._observers[uri]:
            self._observers[uri].append(observer)

    def remove_observer(self, uri: str, observer: Observer) -> None:
        if uri in self._observers and observer in self._observers[uri]:
            self._observers[uri].remove(observer)
            if not self._observers[uri]:
                del self._observers[uri]

    @abstractmethod
    async def get_observable_state(self) -> dict[str, Any]:
        """Получение состояния наблюдаемого объекта"""
        pass


class MCPComponent(ABC):
    @abstractmethod
    async def initialize(self) -> bool:
        pass

    @abstractmethod
    async def cleanup(self) -> bool:
        pass


class MCPError(Exception):
    def __init__(self, code: str, message: str):
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


class MCPToolComponent(MCPComponent):
    def __init__(self) -> None:
        super().__init__()
        self.name: str = ""
        self.description: str = ""
        self.input_schema: dict[str, Any] = {}

    @abstractmethod
    async def execute(self, parameters: dict[str, Any]) -> dict[str, Any]:
        pass


class MCPResource(MCPComponent, Observable):
    def __init__(
        self,
        uri: str,
        name: str,
        description: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> None:
        Observable.__init__(self)
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type
        self._content: Optional[str] = None

    @property
    def content(self) -> Optional[str]:
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        self._content = value
        asyncio.create_task(self.notify_observers(self.uri, self))

    async def initialize(self) -> bool:
        return True

    async def cleanup(self) -> bool:
        return True

    async def get_observable_state(self) -> dict[str, Any]:
        """Реализация получения состояния для Observable"""
        return {
            "uri": self.uri,
            "name": self.name,
            "content": self._content,
            "mime_type": self.mime_type,
        }


class MCPPrompt(MCPComponent):
    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        template: Optional[str] = None,
        arguments: Optional[list[dict[str, Any]]] = None,
    ) -> None:
        self.name = name
        self.description = description
        self.template = template
        self.arguments = arguments or []

    async def initialize(self) -> bool:
        return True

    async def cleanup(self) -> bool:
        return True

    @abstractmethod
    async def generate_messages(
        self,
        arguments: dict[str, Any],
    ) -> list[dict[str, Any]]:
        pass


class ResourceFactory(ABC):
    @abstractmethod
    async def create_resource(
        self,
        uri: str,
        name: str,
        **kwargs: Any,
    ) -> MCPResource:
        pass


class ToolFactory(ABC):
    @abstractmethod
    async def create_tool(
        self,
        name: str,
        **kwargs: Any,
    ) -> MCPTool:
        pass


class PromptFactory(ABC):
    @abstractmethod
    async def create_prompt(
        self,
        name: str,
        **kwargs: Any,
    ) -> MCPPrompt:
        pass
