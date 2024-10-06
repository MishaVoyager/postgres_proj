# pylint: disable=attribute-defined-outside-init
from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import async_sessionmaker

from adapters.dbhelper import get_engine_async
from adapters.repository import (
    VisitorRepository,
    ResourceRepository,
    RecordRepository,
    CategoryRepository,
    AbstractRecordRepository,
    AbstractCategoryRepository,
    AbstractResourceRepository,
    AbstractVisitorRepository, OldRecordRepository, AbstractOldRecordRepository
)


class IUnitOfWork(ABC):
    visitors: AbstractVisitorRepository
    resources: AbstractResourceRepository
    records: AbstractRecordRepository
    categories: AbstractCategoryRepository
    old_records: AbstractOldRecordRepository

    async def __aenter__(self) -> 'IUnitOfWork':
        return self

    async def __aexit__(self, *args):
        await self.rollback()

    async def commit(self):
        await self._commit()

    @abstractmethod
    async def _commit(self):
        raise NotImplementedError

    @abstractmethod
    async def rollback(self):
        raise NotImplementedError

    @abstractmethod
    async def merge(self, obj):
        raise NotImplementedError

    @abstractmethod
    def add(self, obj):
        raise NotImplementedError

    @abstractmethod
    async def execute(self, stmt):
        raise NotImplementedError


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = async_sessionmaker(
            bind=get_engine_async(),
            expire_on_commit=False,
        )

    async def __aenter__(self) -> 'UnitOfWork':
        self.session = self.session_factory()
        self.visitors = VisitorRepository(self.session)
        self.resources = ResourceRepository(self.session)
        self.records = RecordRepository(self.session)
        self.categories = CategoryRepository(self.session)
        self.old_records = OldRecordRepository(self.session)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        await super().__aexit__(*args)
        await self.session.close()

    async def _commit(self):
        await self.session.commit()

    async def rollback(self):
        await self.session.rollback()

    async def merge(self, obj):
        await self.session.merge(obj)

    def add(self, obj):
        self.session.add(obj)

    async def execute(self, stmt):
        return await self.session.execute(stmt)
