"""
Классы ошибок для MCP компонентов.
"""

from typing import Any, Dict, Optional


class MCPError(Exception):
    """
    Базовый класс для ошибок MCP.

    Attributes:
        code: Код ошибки
        message: Сообщение об ошибке
        details: Дополнительные детали ошибки
    """

    def __init__(
        self,
        code: str,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Инициализирует ошибку MCP.

        Args:
            code: Код ошибки
            message: Сообщение об ошибке
            details: Дополнительные детали ошибки
        """
        self.code = code
        self.message = message
        self.details = details or {}
        super().__init__(f"{code}: {message}")

    def to_dict(self) -> Dict[str, Any]:
        """
        Преобразует ошибку в словарь для сериализации.

        Returns:
            Dict[str, Any]: Словарь с данными ошибки
        """
        return {
            "code": self.code,
            "message": self.message,
            "details": self.details,
        }


class ToolError(MCPError):
    """Ошибка, связанная с инструментами MCP."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Инициализирует ошибку инструмента.

        Args:
            message: Сообщение об ошибке
            details: Дополнительные детали ошибки
        """
        super().__init__("tool_error", message, details)


class ResourceError(MCPError):
    """Ошибка, связанная с ресурсами MCP."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Инициализирует ошибку ресурса.

        Args:
            message: Сообщение об ошибке
            details: Дополнительные детали ошибки
        """
        super().__init__("resource_error", message, details)


class PromptError(MCPError):
    """Ошибка, связанная с промптами MCP."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Инициализирует ошибку промпта.

        Args:
            message: Сообщение об ошибке
            details: Дополнительные детали ошибки
        """
        super().__init__("prompt_error", message, details)


class SamplingError(MCPError):
    """Ошибка, связанная с сэмплированием MCP."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        """
        Инициализирует ошибку сэмплирования.

        Args:
            message: Сообщение об ошибке
            details: Дополнительные детали ошибки
        """
        super().__init__("sampling_error", message, details)
