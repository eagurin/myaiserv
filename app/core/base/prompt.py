"""
Базовый класс для промптов MCP.
"""

from abc import abstractmethod
from typing import Any, Dict, List, Optional

from app.core.base.component import MCPComponent


class MCPPrompt(MCPComponent):
    """
    Базовый класс для всех промптов MCP.

    Промпты представляют шаблоны для генерации сообщений,
    которые могут быть использованы для взаимодействия с LLM.

    Attributes:
        name: Имя промпта
        description: Описание промпта
        template: Шаблон промпта
        arguments: Аргументы промпта
    """

    def __init__(
        self,
        name: str,
        description: Optional[str] = None,
        template: Optional[str] = None,
        arguments: Optional[List[Dict[str, Any]]] = None,
    ) -> None:
        """
        Инициализирует промпт.

        Args:
            name: Имя промпта
            description: Описание промпта
            template: Шаблон промпта
            arguments: Аргументы промпта
        """
        self.name = name
        self.description = description
        self.template = template
        self.arguments = arguments or []

    async def initialize(self) -> bool:
        """
        Инициализирует промпт.

        Returns:
            bool: True, если инициализация прошла успешно
        """
        return True

    async def cleanup(self) -> bool:
        """
        Освобождает ресурсы, используемые промптом.

        Returns:
            bool: True, если очистка прошла успешно
        """
        return True

    @abstractmethod
    async def generate_messages(
        self, arguments: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        Генерирует сообщения на основе аргументов.

        Args:
            arguments: Аргументы для генерации сообщений

        Returns:
            List[Dict[str, Any]]: Сгенерированные сообщения
        """
        pass
