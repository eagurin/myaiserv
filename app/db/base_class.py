"""
Базовый класс для моделей SQLAlchemy.
"""

from typing import Any, ClassVar

from sqlalchemy.ext.declarative import as_declarative, declared_attr


@as_declarative()
class Base:
    """
    Базовый класс для всех моделей SQLAlchemy.

    Автоматически генерирует имя таблицы и предоставляет
    общую функциональность для всех моделей.
    """

    id: Any
    __name__: ClassVar[str]

    # Генерация имени таблицы из имени класса
    @declared_attr
    def __tablename__(cls) -> str:
        """
        Автоматически генерирует имя таблицы из имени класса.
        Преобразует CamelCase в snake_case.

        Returns:
            Имя таблицы в формате snake_case
        """
        return cls.__name__.lower()
