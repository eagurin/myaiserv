"""
Базовый класс для ресурсов MCP.
"""

from typing import Optional

from app.core.base.component import MCPComponent
from app.core.base.observer import Observable


class MCPResource(MCPComponent, Observable):
    """
    Базовый класс для всех ресурсов MCP.

    Ресурсы представляют данные, которые могут быть использованы
    инструментами и промптами.

    Attributes:
        uri: Уникальный идентификатор ресурса
        name: Имя ресурса
        description: Описание ресурса
        mime_type: MIME тип ресурса
    """

    def __init__(
        self,
        uri: str,
        name: str,
        description: Optional[str] = None,
        mime_type: Optional[str] = None,
    ) -> None:
        """
        Инициализирует ресурс.

        Args:
            uri: Уникальный идентификатор ресурса
            name: Имя ресурса
            description: Описание ресурса
            mime_type: MIME тип ресурса
        """
        Observable.__init__(self)
        self.uri = uri
        self.name = name
        self.description = description
        self.mime_type = mime_type
        self._content: Optional[str] = None

    @property
    def content(self) -> Optional[str]:
        """
        Возвращает содержимое ресурса.

        Returns:
            Optional[str]: Содержимое ресурса или None, если оно не установлено
        """
        return self._content

    @content.setter
    def content(self, value: str) -> None:
        """
        Устанавливает содержимое ресурса и уведомляет наблюдателей.

        Args:
            value: Новое содержимое ресурса
        """
        import asyncio

        self._content = value
        asyncio.create_task(self.notify_observers(self.uri, self))

    async def initialize(self) -> bool:
        """
        Инициализирует ресурс.

        Returns:
            bool: True, если инициализация прошла успешно
        """
        return True

    async def cleanup(self) -> bool:
        """
        Освобождает ресурсы, используемые ресурсом.

        Returns:
            bool: True, если очистка прошла успешно
        """
        return True
