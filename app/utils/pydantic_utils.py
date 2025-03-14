"""
Утилиты для работы с Pydantic v2.
"""

from typing import Any, Type, TypeVar

T = TypeVar("T")


def lenient_issubclass(
    cls: Any, class_or_tuple: Type[Any] | tuple[Type[Any], ...]
) -> bool:
    """
    Безопасная проверка наследования, которая не вызывает исключений.

    Args:
        cls: Класс для проверки
        class_or_tuple: Класс или кортеж классов для сравнения

    Returns:
        bool: True если cls является подклассом class_or_tuple, иначе False
    """
    try:
        return isinstance(cls, type) and issubclass(cls, class_or_tuple)
    except TypeError:
        return False


def smart_deepcopy(value: T) -> T:
    """
    Умное глубокое копирование объектов Pydantic.

    В Pydantic v2 рекомендуется использовать model_copy() для моделей
    и стандартный copy.deepcopy() для остальных объектов.

    Args:
        value: Значение для копирования

    Returns:
        Копия значения
    """
    from copy import deepcopy

    from pydantic import BaseModel

    if isinstance(value, BaseModel):
        return value.model_copy(deep=True)  # type: ignore
    return deepcopy(value)
