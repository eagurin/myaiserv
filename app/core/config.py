"""
Модуль конфигурации приложения.
Содержит настройки для различных компонентов системы.
"""

from pathlib import Path
from typing import Any, Optional, Union

from pydantic import AnyHttpUrl, field_validator
from pydantic.networks import PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Настройки приложения."""

    # Базовые настройки
    PROJECT_NAME: str = "MyAIServ"
    PROJECT_DESCRIPTION: str = "Сервис искусственного интеллекта"
    VERSION: str = "0.1.0"
    DEBUG: bool = False

    # API настройки
    API_V1_STR: str = "/api/v1"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Настройки безопасности
    # Для разработки, в продакшене использовать переменную окружения
    SECRET_KEY: str = "supersecretkey"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 дней
    ALGORITHM: str = "HS256"

    # CORS настройки
    CORS_ORIGINS: list[AnyHttpUrl] = []

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, list[str]]) -> Union[list[str], str]:
        """Валидация и преобразование CORS_ORIGINS."""
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",")]
        elif isinstance(v, (list, str)):
            return v
        raise ValueError(v)

    # Настройки базы данных
    POSTGRES_SERVER: str = "localhost"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "myaiserv"
    POSTGRES_PORT: int = 5432
    DATABASE_URI: Optional[PostgresDsn] = None

    @field_validator("DATABASE_URI", mode="before")
    @classmethod
    def assemble_db_connection(cls, v: Optional[str], info: Any) -> Any:
        """Сборка строки подключения к БД."""
        if isinstance(v, str):
            return v

        values = info.data
        return PostgresDsn.build(
            scheme="postgresql",
            username=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            port=values.get("POSTGRES_PORT"),
            path=f"/{values.get('POSTGRES_DB') or ''}",
        )

    # Настройки логирования
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    # Пути к файлам и директориям
    BASE_DIR: Path = Path(__file__).resolve().parent.parent.parent

    # Конфигурация настроек
    model_config = SettingsConfigDict(
        case_sensitive=True,
        env_file=".env",
        extra="ignore",  # Разрешаем дополнительные поля из переменных окружения
    )


# Создание экземпляра настроек
settings = Settings()