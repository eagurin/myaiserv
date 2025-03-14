"""
Модели сообщений MCP.
"""

from typing import List, Optional, Union

from pydantic import BaseModel, Field

from app.models.mcp.enums import ContentType, MessageRole


class MessageContent(BaseModel):
    """
    Контент сообщения MCP.

    Attributes:
        type: Тип контента
        text: Текстовое содержимое
        data: Данные в формате base64
        mime_type: MIME тип данных
        resource_uri: URI ресурса
    """

    type: ContentType = Field(ContentType.TEXT)
    text: Optional[str] = None
    data: Optional[str] = None
    mime_type: Optional[str] = None
    resource_uri: Optional[str] = None


class Message(BaseModel):
    """
    Модель сообщения MCP.

    Attributes:
        role: Роль отправителя сообщения
        content: Содержимое сообщения
    """

    role: MessageRole
    content: Union[MessageContent, List[MessageContent]]
