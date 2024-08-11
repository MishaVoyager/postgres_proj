# pylint: disable=attribute-defined-outside-init
from abc import ABC, abstractmethod
from typing import Any

class IRepository[T](ABC):
    @abstractmethod
    def add(self, obj) -> None:
        raise NotImplemented

    @abstractmethod
    def get(self, email) -> T:
        raise NotImplemented

    @abstractmethod
    def list(self) -> list[T]:
        raise NotImplemented

    @abstractmethod
    def delete(self, obj) -> None:
        raise NotImplemented


class IUnitOfWork(ABC):
    visitors: IRepository

    def __enter__(self) -> 'IUnitOfWork':
        return self

    def __exit__(self, *args):
        self.rollback()

    def commit(self):
        self._commit()

    @abstractmethod
    def _commit(self):
        raise NotImplementedError

    @abstractmethod
    def rollback(self):
        raise NotImplementedError
