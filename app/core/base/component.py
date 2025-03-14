"""
Базовый класс для всех MCP компонентов.
"""

from abc import ABC, abstractmethod


class MCPComponent(ABC):
    """
    Базовый абстрактный класс для всех компонентов MCP.

    Определяет общий интерфейс для инициализации и очистки ресурсов.
    """

    @abstractmethod
    async def initialize(self) -> bool:
        """
        Инициализирует компонент.

        Returns:
            bool: True если инициализация прошла успешно, иначе False
        """
        pass

    @abstractmethod
    async def cleanup(self) -> bool:
        """
        Освобождает ресурсы, используемые компонентом.

        Returns:
            bool: True если очистка прошла успешно, иначе False
        """
        pass
