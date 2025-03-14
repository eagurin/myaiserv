from enum import Enum
from typing import Any, Dict, List, Optional, Union

from graphql.type import (
    GraphQLField,
    GraphQLList,
    GraphQLNonNull,
    GraphQLObjectType,
    GraphQLSchema,
    GraphQLString,
)
from pydantic import BaseModel, Field


class ResourceType(str, Enum):
    """Типы ресурсов MCP"""

    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DATASET = "dataset"
    SCHEMA = "schema"
    CONFIG = "config"


class MessageRole(str, Enum):
    """Роли в диалоге MCP"""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ContentType(str, Enum):
    """Типы контента в сообщениях MCP"""

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"
    JSON = "json"


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
    resourceType: Optional[ResourceType] = Field(None, description="Тип ресурса")


class Tool(BaseModel):
    """Модель инструмента MCP

    Examples:
            >>> tool = Tool(
            ...     name="calculate_sum",
            ...     description="Add two numbers",
            ...     input_schema={
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
    input_schema: Dict[str, Any] = Field(
        ..., description="JSON Schema входных параметров"
    )
    requires_approval: bool = Field(False, description="Требуется ли одобрение")


class PromptArgument(BaseModel):
    """Аргумент промпта MCP"""

    name: str = Field(..., description="Имя аргумента")
    description: Optional[str] = Field(None, description="Описание аргумента")
    required: bool = Field(default=False, description="Обязательность аргумента")
    type: str = Field("string", description="Тип аргумента")
    default: Optional[Any] = Field(None, description="Значение по умолчанию")


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
    template: Optional[str] = Field(None, description="Шаблон промпта")
    arguments: Optional[List[PromptArgument]] = Field(
        None, description="Аргументы промпта"
    )
    system_prompt: Optional[str] = Field(None, description="Системный промпт")


class MessageContent(BaseModel):
    """Контент сообщения MCP"""

    type: ContentType = Field(ContentType.TEXT)
    text: Optional[str] = None
    data: Optional[str] = None
    mime_type: Optional[str] = None
    resource_uri: Optional[str] = None


class Message(BaseModel):
    """Модель сообщения MCP"""

    role: MessageRole
    content: Union[MessageContent, List[MessageContent]]


class ModelPreferences(BaseModel):
    """Предпочтения модели для сэмплинга"""

    model_name: Optional[str] = None
    provider: Optional[str] = None
    max_tokens: Optional[int] = None
    temperature: Optional[float] = None
    top_p: Optional[float] = None
    top_k: Optional[int] = None
    frequency_penalty: Optional[float] = None
    presence_penalty: Optional[float] = None


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

    messages: List[Dict[str, Any]]
    modelPreferences: Optional[Dict[str, Any]] = None
    systemPrompt: Optional[str] = None
    includeContext: Optional[str] = "none"
    temperature: Optional[float] = None
    maxTokens: Optional[int] = 1024
    stopSequences: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class SamplingResponse(BaseModel):
    """Ответ на запрос сэмплинга"""

    model: str
    stopReason: Optional[str] = None
    role: MessageRole
    content: MessageContent


class MCPErrorResponse(BaseModel):
    """Модель ошибки MCP"""

    code: str
    message: str
    details: Optional[Dict[str, Any]] = None


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
                                "name": GraphQLField(GraphQLNonNull(GraphQLString)),
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
