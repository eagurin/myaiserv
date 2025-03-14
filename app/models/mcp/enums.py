"""
Перечисления для MCP.
"""

from enum import Enum


class ResourceType(str, Enum):
    """
    Типы ресурсов MCP.

    Attributes:
        DOCUMENT: Документ
        IMAGE: Изображение
        AUDIO: Аудио
        VIDEO: Видео
        DATASET: Набор данных
        SCHEMA: Схема
        CONFIG: Конфигурация
    """

    DOCUMENT = "document"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    DATASET = "dataset"
    SCHEMA = "schema"
    CONFIG = "config"


class MessageRole(str, Enum):
    """
    Роли в диалоге MCP.

    Attributes:
        SYSTEM: Системное сообщение
        USER: Сообщение пользователя
        ASSISTANT: Сообщение ассистента
        TOOL: Сообщение инструмента
    """

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class ContentType(str, Enum):
    """
    Типы контента в сообщениях MCP.

    Attributes:
        TEXT: Текст
        IMAGE: Изображение
        AUDIO: Аудио
        VIDEO: Видео
        FILE: Файл
        JSON: JSON
    """

    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    FILE = "file"
    JSON = "json"
