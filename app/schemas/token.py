"""
Схемы для токенов аутентификации.
"""

from typing import Optional

from pydantic import BaseModel


class Token(BaseModel):
    """Схема токена доступа."""

    access_token: str
    token_type: str


class TokenPayload(BaseModel):
    """Схема полезной нагрузки токена."""

    sub: Optional[str] = None
