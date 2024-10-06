import random
from datetime import datetime as dt, timezone as tz
from typing import Optional

from domain.models import Resource, Category, Visitor, Record
from service_layer.unit_of_work import UnitOfWork


async def gen_resource(resource_id: int = 1, category_name: str = "cat1", name: str = "resource",
                       comment: str = None) -> Resource:
    async with UnitOfWork() as uow:
        stored_category = await uow.categories.get(category_name)
        category = stored_category if stored_category else Category(category_name)
        resource = Resource(resource_id=resource_id, name=name, category=category, comment=comment)
        uow.resources.add(resource)
        await uow.commit()
    return resource


async def gen_visitor(email: str = "test@skbkontur.ru", external_id: Optional[int] = None) -> Visitor:
    async with UnitOfWork() as uow:
        visitor = Visitor(email=email, is_admin=True, external_id=external_id)
        uow.visitors.add(visitor)
        await uow.commit()
    return visitor


async def gen_record(
        resource: Resource,
        visitor: Visitor,
        enqueue_date: dt = None,
        take_date: dt = None,
        return_date: dt = None
) -> Record:
    async with UnitOfWork() as uow:
        record = Record(
            resource_name=resource.name,
            email=visitor.email,
            enqueue_date=enqueue_date,
            take_date=take_date,
            return_date=return_date
        )
        uow.records.add(record)
        await uow.commit()
    return record


def gen_past_time() -> dt:
    year = random.randint(1, 2023)
    return dt(year, 11, 11, tzinfo=tz.utc)


def gen_future_time() -> dt:
    year = random.randint(2025, 10000)
    return dt(year, 11, 11, tzinfo=tz.utc)
