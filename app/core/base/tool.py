"""
Базовый класс для инструментов MCP.
"""

from abc import abstractmethod
from typing import Any, Dict

from app.core.base.component import MCPComponent


class MCPTool(MCPComponent):
    """
    Базовый класс для всех инструментов MCP.

    Инструменты предоставляют функциональность, которую можно вызывать
    через MCP API.

    Attributes:
        name: Имя инструмента
        description: Описание инструмента
        input_schema: JSON Schema для входных параметров
    """

    def __init__(self) -> None:
        """Инициализирует инструмент с пустыми атрибутами."""
        self.name: str = ""
        self.description: str = ""
        self.input_schema: Dict[str, Any] = {}

    @abstractmethod
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """
        Выполняет инструмент с указанными параметрами.

        Args:
            parameters: Параметры для выполнения инструмента

        Returns:
            Dict[str, Any]: Результат выполнения инструмента
        """
        pass
