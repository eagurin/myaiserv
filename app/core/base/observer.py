"""
Реализация паттерна Наблюдатель для MCP компонентов.
"""

from abc import ABC
from typing import Any, Dict, List, Protocol


class Observer(Protocol):
    """
    Протокол для наблюдателей, которые получают уведомления от Observable.
    """

    async def update(self, uri: str, data: Any) -> None:
        """
        Получает уведомление об изменении данных.

        Args:
            uri: Идентификатор ресурса, который изменился
            data: Новые данные
        """
        ...


class Observable(ABC):
    """
    Базовый класс для объектов, за которыми можно наблюдать.

    Позволяет регистрировать, удалять и уведомлять наблюдателей.
    """

    def __init__(self) -> None:
        """Инициализирует словарь наблюдателей."""
        self._observers: Dict[str, List[Observer]] = {}

    async def notify_observers(self, uri: str, data: Any) -> None:
        """
        Уведомляет всех наблюдателей об изменении данных.

        Args:
            uri: Идентификатор ресурса, который изменился
            data: Новые данные
        """
        for observer in self._observers.get(uri, []):
            await observer.update(uri, data)

    def add_observer(self, uri: str, observer: Observer) -> None:
        """
        Добавляет наблюдателя для указанного URI.

        Args:
            uri: Идентификатор ресурса для наблюдения
            observer: Наблюдатель, который будет получать уведомления
        """
        if uri not in self._observers:
            self._observers[uri] = []
        if observer not in self._observers[uri]:
            self._observers[uri].append(observer)

    def remove_observer(self, uri: str, observer: Observer) -> None:
        """
        Удаляет наблюдателя для указанного URI.

        Args:
            uri: Идентификатор ресурса
            observer: Наблюдатель для удаления
        """
        if uri in self._observers and observer in self._observers[uri]:
            self._observers[uri].remove(observer)
            if not self._observers[uri]:
                del self._observers[uri]
