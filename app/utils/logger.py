"""
Модуль логирования.
Содержит настройки и функции для логирования.
"""

import logging
import sys
from collections.abc import MutableMapping
from typing import (
    Any,  # Для совместимости с LoggerAdapter
    Optional,
)

from app.core.config import settings

# Формат логов
log_format = settings.LOG_FORMAT

# Настройка корневого логгера
logging.basicConfig(
    level=settings.LOG_LEVEL,
    format=log_format,
    handlers=[logging.StreamHandler(sys.stdout)],
)


def get_logger(name: str) -> logging.Logger:
    """
    Получение настроенного логгера.

    Args:
        name: Имя логгера (обычно __name__ модуля)

    Returns:
        Настроенный логгер
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """
    Адаптер логгера для добавления контекстной информации.

    Позволяет добавлять дополнительные поля к каждому сообщению лога.
    """

    def __init__(
        self,
        logger: logging.Logger,
        extra: Optional[dict[str, Any]] = None,
    ):
        """
        Инициализация адаптера.

        Args:
            logger: Базовый логгер
            extra: Дополнительные поля для логов
        """
        super().__init__(logger, extra or {})

    def process(
        self,
        msg: str,
        kwargs: MutableMapping[str, Any],
    ) -> tuple[str, MutableMapping[str, Any]]:
        """
        Обработка сообщения перед логированием.

        Args:
            msg: Сообщение для лога
            kwargs: Дополнительные аргументы

        Returns:
            Кортеж из обработанного сообщения и аргументов
        """
        # Добавление контекстной информации к сообщению
        extra = kwargs.get("extra", {})
        extra.update(self.extra)
        kwargs["extra"] = extra

        return msg, kwargs


# Создание корневого логгера приложения
logger = get_logger("app")

# Пример использования:
# from app.utils.logger import logger
# logger.info("Сообщение")
#
# С контекстом:
# context_logger = LoggerAdapter(logger, {"request_id": "123"})
# context_logger.info("Сообщение с контекстом")