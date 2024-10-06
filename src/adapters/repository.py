import datetime
from abc import ABC
from abc import abstractmethod
from datetime import datetime as dt
from datetime import timedelta as td
from datetime import timezone as tz
from typing import Optional, List

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.operators import ilike_op, and_

from domain.models import Visitor, Resource, Record, Category, OldRecord
from helpers.helpers import get_time_now


class IRepository(ABC):

    @abstractmethod
    async def get(self, obj_primary_key):
        raise NotImplemented

    @abstractmethod
    def add(self, obj) -> None:
        raise NotImplemented

    @abstractmethod
    async def list(self) -> List:
        raise NotImplemented

    @abstractmethod
    async def delete(self, obj) -> None:
        raise NotImplemented


class AbstractOldRecordRepository(IRepository):
    @abstractmethod
    async def get(self, record_primary_key) -> Optional[OldRecord]:
        raise NotImplemented

    @abstractmethod
    async def list(self) -> List[OldRecord]:
        raise NotImplemented

    @abstractmethod
    def add(self, record) -> None:
        raise NotImplemented

    @abstractmethod
    async def delete(self, record) -> None:
        raise NotImplemented


class AbstractRecordRepository(IRepository):
    @abstractmethod
    async def get(self, record_primary_key) -> Optional[Record]:
        raise NotImplemented

    @abstractmethod
    async def get_expiring(self, days_before_now: int) -> List[Record]:
        raise NotImplemented

    @abstractmethod
    async def get_expired(self) -> List[Record]:
        raise NotImplemented

    @abstractmethod
    async def list(self) -> List[Record]:
        raise NotImplemented

    @abstractmethod
    def add(self, record) -> None:
        raise NotImplemented

    @abstractmethod
    async def delete(self, record) -> None:
        raise NotImplemented


class AbstractResourceRepository(IRepository):
    @abstractmethod
    async def get(self, resource_primary_key) -> Optional[Resource]:
        raise NotImplemented

    @abstractmethod
    async def get_by_id(self, resource_id) -> Optional[Resource]:
        raise NotImplemented

    @abstractmethod
    async def list(self) -> List[Resource]:
        raise NotImplemented

    @abstractmethod
    def add(self, resource) -> None:
        raise NotImplemented

    @abstractmethod
    async def delete(self, resource) -> None:
        raise NotImplemented

    @abstractmethod
    async def search(self, search_key, limit: Optional[int] = None) -> List[Resource]:
        raise NotImplemented


class AbstractVisitorRepository(IRepository):
    @abstractmethod
    async def get(self, visitor_primary_key) -> Optional[Visitor]:
        raise NotImplemented

    @abstractmethod
    async def get_by_external_id(self, visitor_external_id) -> Visitor:
        raise NotImplemented

    @abstractmethod
    async def list(self) -> List[Visitor]:
        raise NotImplemented

    @abstractmethod
    def add(self, visitor) -> None:
        raise NotImplemented

    @abstractmethod
    async def delete(self, visitor) -> None:
        raise NotImplemented


class AbstractCategoryRepository(IRepository):
    @abstractmethod
    async def get(self, category_primary_key) -> Optional[Category]:
        raise NotImplemented

    @abstractmethod
    async def list(self) -> List[Category]:
        raise NotImplemented

    @abstractmethod
    def add(self, category) -> None:
        raise NotImplemented

    @abstractmethod
    async def delete(self, category) -> None:
        raise NotImplemented


class OldRecordRepository(AbstractOldRecordRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, record: Record) -> None:
        old_record = OldRecord(
            record_id=record.record_id,
            email=record.email,
            resource_name=record.resource_name,
            take_date=record.take_date,
            return_date=record.return_date,
            enqueue_date=record.enqueue_date,
            created_at=record.created_at,
            updated_at=record.updated_at
        )
        self.session.add(old_record)

    async def get(self, record_id: int) -> Optional[OldRecord]:
        return await self.session.get(OldRecord, record_id)

    async def list(self) -> List[OldRecord]:
        result = await self.session.execute(select(OldRecord))
        return result.scalars().unique().all()

    async def delete(self, record: OldRecord) -> None:
        await self.session.delete(record)


class RecordRepository(AbstractRecordRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, record: Record) -> None:
        self.session.add(record)

    async def get(self, record_id: int) -> Optional[Record]:
        return await self.session.get(Record, record_id)

    async def get_expired(self) -> List[Record]:
        result = await self.session.execute(select(Record).filter(Record.return_date <= get_time_now()))
        return result.scalars().unique().all()

    async def get_expiring(self, expire_after_days: int) -> List[Record]:
        result = await self.session.execute(select(Record).filter(
            # Бронь заканчивается завтра
            and_(
                Record.return_date > get_time_now(),
                Record.return_date <= dt.combine(get_time_now() + td(days=expire_after_days),
                                                 datetime.time.max, tz.utc),
            )
        ))
        return result.scalars().unique().all()

    async def list(self) -> List[Record]:
        result = await self.session.execute(select(Record))
        return result.scalars().unique().all()

    async def delete(self, record: Record) -> None:
        await self.session.delete(record)


def _prepare_filters_for_strings(fields: list[str], search_key: str, limit: Optional[int] = 1000) -> list:
    """Готовит фильтры для поиска по тексту"""
    search_filter = list()
    for field in fields:
        search_filter.append(ilike_op(field, f"%{search_key}%"))
        search_filter.append(ilike_op(field, f"%{search_key.capitalize()}%"))
        search_filter.append(ilike_op(field, f"%{search_key.upper()}%"))
    return search_filter


class ResourceRepository(AbstractResourceRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, resource: Resource) -> None:
        self.session.add(resource)

    async def get_by_id(self, resource_id: int) -> Optional[Resource]:
        result = await self.session.execute(select(Resource).filter_by(resource_id=resource_id))
        resources = result.scalars().unique().all()
        if len(resources) == 0:
            return None
        else:
            return resources[0]

    async def get(self, name: str) -> Optional[Resource]:
        return await self.session.get(Resource, name)

    async def list(self) -> List[Resource]:
        result = await self.session.execute(select(Resource))
        return result.scalars().unique().all()

    async def delete(self, resource: Resource) -> None:
        await self.session.delete(resource)

    async def get_many(self, resources_ids: list):
        """TODO: переписать с использованием query, чтобы отправлялся один запрос"""
        return [await self.session.get(Resource, i) for i in resources_ids]

    async def search(self, search_key, limit: Optional[int] = 1000) -> List[Resource]:
        pass
        # if search_key.isnumeric():
        #     filters = [Resource.resource_id.in_([int(search_key)])]
        # else:
        #     filters = _prepare_filters_for_strings(
        #         [Resource.name, Resource.external_id, Resource.comment, Resource.address],
        #         search_key=search_key
        #     )
        # result = await self.session.execute(select(Resource).filter(or_(*filters)).limit(limit))
        # return result.scalars().unique().all()


class VisitorRepository(AbstractVisitorRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, visitor: Visitor) -> None:
        self.session.add(visitor)

    async def get_by_external_id(self, external_id) -> Optional[Visitor]:
        result = await self.session.execute(select(Visitor).filter_by(external_id=external_id))
        visitors = result.scalars().unique().all()
        if len(visitors) == 0:
            return None
        else:
            return visitors[0]

    async def get(self, email: str) -> Optional[Visitor]:
        return await self.session.get(Visitor, email)

    async def list(self) -> List[Visitor]:
        result = await self.session.execute(select(Visitor))
        return result.scalars().unique().all()

    async def delete(self, visitor: Visitor) -> None:
        await self.session.delete(visitor)


class CategoryRepository(AbstractCategoryRepository):
    def __init__(self, session: AsyncSession):
        self.session = session

    def add(self, category: Category) -> None:
        self.session.add(category)

    async def get(self, name: str) -> Optional[Category]:
        return await self.session.get(Category, name)

    async def list(self) -> List[Category]:
        result = await self.session.execute(select(Category))
        return result.scalars().unique().all()

    async def delete(self, category: Category) -> None:
        await self.session.delete(category)
