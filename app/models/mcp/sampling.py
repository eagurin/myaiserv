"""
Модели для сэмплирования MCP.
"""

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, Field

from app.models.mcp.message import Message


class ModelPreferences(BaseModel):
    """
    Предпочтения для модели при сэмплировании.

    Attributes:
        temperature: Температура сэмплирования
        top_p: Top-p параметр
        max_tokens: Максимальное число токенов для генерации
    """

    temperature: Optional[float] = Field(0.7, description="Температура сэмплирования")
    top_p: Optional[float] = Field(1.0, description="Top-p параметр")
    max_tokens: Optional[int] = Field(
        1024, description="Максимальное число токенов для генерации"
    )


class SamplingRequest(BaseModel):
    """
    Запрос на сэмплирование от модели.

    Attributes:
        messages: Список сообщений для контекста
        preferences: Предпочтения сэмплирования
    """

    messages: List[Message] = Field(..., description="Список сообщений для контекста")
    preferences: Optional[ModelPreferences] = Field(
        None, description="Предпочтения сэмплирования"
    )


class SamplingResponse(BaseModel):
    """
    Ответ на запрос сэмплирования.

    Attributes:
        message: Сгенерированное сообщение
    """

    message: Message = Field(..., description="Сгенерированное сообщение")


class MCPErrorResponse(BaseModel):
    """
    Ответ с ошибкой от MCP.

    Attributes:
        error: Текст ошибки
        details: Детали ошибки
    """

    error: str = Field(..., description="Текст ошибки")
    details: Optional[Dict[str, Any]] = Field(None, description="Детали ошибки")
