"""
Модуль сессии SQLAlchemy.
Содержит настройки подключения к базе данных.
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import settings

# Создание движка SQLAlchemy
engine = create_engine(
    str(settings.DATABASE_URI),  # Преобразуем в строку для совместимости
    pool_pre_ping=True,
    echo=settings.DEBUG,
)

# Создание фабрики сессий
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)


def get_db() -> Generator[Session, None, None]:
    """
    Зависимость для получения сессии базы данных.

    Yields:
        Сессия SQLAlchemy
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
