"""
Модуль исключений.
Содержит определения пользовательских исключений приложения.
"""

from typing import Any, Optional

from fastapi import HTTPException, status


class BaseAppException(Exception):
    """Базовое исключение приложения."""

    def __init__(self, message: str = "Произошла ошибка"):
        self.message = message
        super().__init__(self.message)


class ResourceNotFoundException(BaseAppException):
    """Исключение для случаев, когда ресурс не найден."""

    def __init__(self, message: str = "Ресурс не найден"):
        super().__init__(message)


class ValidationException(BaseAppException):
    """Исключение для ошибок валидации."""

    def __init__(self, message: str = "Ошибка валидации"):
        super().__init__(message)


class AuthenticationException(BaseAppException):
    """Исключение для ошибок аутентификации."""

    def __init__(self, message: str = "Ошибка аутентификации"):
        super().__init__(message)


class AuthorizationException(BaseAppException):
    """Исключение для ошибок авторизации."""

    def __init__(self, message: str = "Недостаточно прав"):
        super().__init__(message)


class DatabaseException(BaseAppException):
    """Исключение для ошибок базы данных."""

    def __init__(self, message: str = "Ошибка базы данных"):
        super().__init__(message)


class APIException(HTTPException):
    """
    Исключение API для возврата HTTP-ошибок.

    Расширяет стандартное HTTPException FastAPI для удобства использования.
    """

    def __init__(
        self,
        status_code: int = status.HTTP_500_INTERNAL_SERVER_ERROR,
        detail: Any = "Внутренняя ошибка сервера",
        headers: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status_code,
            detail=detail,
            headers=headers,
        )


# Предопределенные HTTP-исключения для удобства использования
class BadRequestException(APIException):
    """400 Bad Request."""

    def __init__(
        self,
        detail: Any = "Некорректный запрос",
        headers: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=detail,
            headers=headers,
        )


class UnauthorizedException(APIException):
    """401 Unauthorized."""

    def __init__(
        self,
        detail: Any = "Требуется аутентификация",
        headers: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=detail,
            headers=headers,
        )


class ForbiddenException(APIException):
    """403 Forbidden."""

    def __init__(
        self,
        detail: Any = "Доступ запрещен",
        headers: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=detail,
            headers=headers,
        )


class NotFoundException(APIException):
    """404 Not Found."""

    def __init__(
        self,
        detail: Any = "Ресурс не найден",
        headers: Optional[dict[str, Any]] = None,
    ):
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=detail,
            headers=headers,
        )
