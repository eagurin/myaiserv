from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union

from pydantic import BaseModel, Field


class ResourceType(str, Enum):
    """Типы ресурсов MCP"""

    TEXT = "text"
    BINARY = "binary"


class MessageRole(str, Enum):
    """Роли в диалоге MCP"""

    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class ContentType(str, Enum):
    """Типы контента в сообщениях MCP"""

    TEXT = "text"
    IMAGE = "image"
    RESOURCE = "resource"


class Resource(BaseModel):
    """Модель ресурса MCP

    Examples:
            >>> resource = Resource(
            ...     uri="file:///logs/app.log",
            ...     name="Application Logs",
            ...     description="Application runtime logs",
            ...     mimeType="text/plain"
            ... )
    """

    uri: str = Field(..., description="Уникальный идентификатор ресурса")
    name: str = Field(..., description="Человекочитаемое имя ресурса")
    description: Optional[str] = Field(None, description="Описание ресурса")
    mimeType: Optional[str] = Field(None, description="MIME тип ресурса")


class Tool(BaseModel):
    """Модель инструмента MCP

    Examples:
            >>> tool = Tool(
            ...     name="calculate_sum",
            ...     description="Add two numbers",
            ...     inputSchema={
            ...         "type": "object",
            ...         "properties": {
            ...             "a": {"type": "number"},
            ...             "b": {"type": "number"}
            ...         },
            ...         "required": ["a", "b"]
            ...     }
            ... )
    """

    name: str = Field(..., description="Уникальное имя инструмента")
    description: str = Field(..., description="Описание функциональности")
    inputSchema: Dict[str, Any] = Field(
        ..., description="JSON Schema входных параметров"
    )


class PromptArgument(BaseModel):
    """Аргумент промпта MCP"""

    name: str = Field(..., description="Имя аргумента")
    description: Optional[str] = Field(None, description="Описание аргумента")
    required: bool = Field(
        default=False, description="Обязательность аргумента"
    )


class Prompt(BaseModel):
    """Модель промпта MCP

    Examples:
            >>> prompt = Prompt(
            ...     name="analyze-code",
            ...     description="Analyze code for improvements",
            ...     arguments=[
            ...         PromptArgument(
            ...             name="language",
            ...             description="Programming language",
            ...             required=True
            ...         )
            ...     ]
            ... )
    """

    name: str = Field(..., description="Уникальное имя промпта")
    description: Optional[str] = Field(None, description="Описание промпта")
    arguments: Optional[List[PromptArgument]] = Field(
        None, description="Аргументы промпта"
    )


class MessageContent(BaseModel):
    """Контент сообщения MCP"""

    type: ContentType
    text: Optional[str] = None
    data: Optional[str] = None
    mimeType: Optional[str] = None
    resource: Optional[Resource] = None


class Message(BaseModel):
    """Модель сообщения MCP"""

    role: MessageRole
    content: MessageContent


class ModelPreferences(BaseModel):
    """Предпочтения модели для сэмплинга"""

    hints: Optional[List[Dict[str, str]]] = None
    costPriority: Optional[float] = Field(None, ge=0, le=1)
    speedPriority: Optional[float] = Field(None, ge=0, le=1)
    intelligencePriority: Optional[float] = Field(None, ge=0, le=1)


class SamplingRequest(BaseModel):
    """Запрос на сэмплинг

    Examples:
            >>> request = SamplingRequest(
            ...     messages=[
            ...         Message(
            ...             role=MessageRole.USER,
            ...             content=MessageContent(
            ...                 type=ContentType.TEXT,
            ...                 text="What's the weather?"
            ...             )
            ...         )
            ...     ],
            ...     maxTokens=100
            ... )
    """

    messages: List[Message]
    modelPreferences: Optional[ModelPreferences] = None
    systemPrompt: Optional[str] = None
    includeContext: Optional[Literal["none", "thisServer", "allServers"]] = (
        "none"
    )
    temperature: Optional[float] = Field(None, ge=0, le=1)
    maxTokens: int
    stopSequences: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class SamplingResponse(BaseModel):
    """Ответ на запрос сэмплинга"""

    model: str
    stopReason: Optional[str] = None
    role: MessageRole
    content: MessageContent


class MCPError(BaseModel):
    """Модель ошибки MCP"""

    code: int
    message: str
    data: Optional[Any] = None


# GraphQL типы для интеграции
from graphql import (GraphQLField, GraphQLList, GraphQLNonNull,
                     GraphQLObjectType, GraphQLSchema, GraphQLString)

# Определение GraphQL схемы для MCP
mcp_schema = GraphQLSchema(
    query=GraphQLObjectType(
        name="Query",
        fields={
            "listTools": GraphQLField(
                GraphQLList(
                    GraphQLNonNull(
                        GraphQLObjectType(
                            name="Tool",
                            fields={
                                "name": GraphQLField(
                                    GraphQLNonNull(GraphQLString)
                                ),
                                "description": GraphQLField(GraphQLString),
                            },
                        )
                    )
                )
            ),
            # Добавьте другие поля запросов
        },
    )
)
