from typing import List, Optional, Tuple

from domain.models import Record, Resource, Visitor
from service_layer.unit_of_work import UnitOfWork


async def get_take_and_future_records(resource_name: str) -> Tuple[Optional[Record], List[Record]]:
    records = list()
    take_record = None
    async with UnitOfWork() as uow:
        resource = await uow.resources.get(resource_name)
        if resource.take_record:
            take_record = resource.take_record
        records += resource.future_records
        await uow.commit()
    return take_record, sorted(records)


async def get_resource_by_id(resource_id: int) -> Resource:
    async with UnitOfWork() as uow:
        resource = await uow.resources.get_by_id(resource_id)
        await uow.commit()
    return resource


async def get_resource_by_name(name: str) -> Resource:
    async with UnitOfWork() as uow:
        resource = await uow.resources.get(name)
        await uow.commit()
    return resource


async def get_record(record_id: int) -> Tuple[Record, Visitor, Resource]:
    async with UnitOfWork() as uow:
        record = await uow.records.get(record_id)
        visitor = record.visitor
        resource = record.resource
        await uow.commit()
    return record, visitor, resource


async def get_visitor_by_external_id(external_id: int) -> Visitor:
    async with UnitOfWork() as uow:
        visitor = await uow.visitors.get_by_external_id(external_id)
        await uow.commit()
    return visitor


async def get_visitor(email: str) -> Visitor:
    async with UnitOfWork() as uow:
        visitor = await uow.visitors.get(email)
        await uow.commit()
    return visitor


async def get_future_reservations_for_resource(resource_name: str) -> List[Record]:
    async with UnitOfWork() as uow:
        resource = await uow.resources.get(resource_name)
        future_records = resource.future_records
        await uow.commit()
    return future_records

async def get_future_reservations_for_visitor(email: str) -> List[Record]:
    async with UnitOfWork() as uow:
        visitor = await uow.visitors.get(email)
        future_records = visitor.future_records
        await uow.commit()
    return future_records

async def get_categories() -> List[str]:
    async with UnitOfWork() as uow:
        categories = await uow.categories.list()
        await uow.commit()
    return [i.name for i in categories]


async def get_resources_in_category(category: str) -> List[Resource]:
    async with UnitOfWork() as uow:
        category = await uow.categories.get(category)
        resources = category.resources
        await uow.commit()
    return resources

async def get_old_records_by_email(email: str):
    async with UnitOfWork() as uow:
        visitor = await uow.visitors.get(email)
        old_records = visitor.old_records
        await uow.commit()
    return old_records

async def get_old_records_by_resource_name(resource_name: str):
    async with UnitOfWork() as uow:
        resource = await uow.resources.get(resource_name)
        old_records = resource.old_records
        await uow.commit()
    return old_records

#
#
# async def get_current_take_record(resource_id: int):
#     async with UnitOfWork() as uow:
#         resource = await uow.resources.get(resource_id)
#         record = resource.take_record
#         await uow.commit()
#     return record
#
#
# async def get_taken_record(email: str, resource_id: int) -> Optional[Record]:
#     async with UnitOfWork() as uow:
#         record = (await uow.resources.get(resource_id)).take_record
#         records = (await uow.visitors.get(email)).take_records
#         await uow.commit()
#     if record not in records:
#         return None
#     return record
#
#
# async def get_taken(visitor_external_id: int) -> List[Record]:
#     async with UnitOfWork() as uow:
#         visitor = await uow.visitors.get_by_external_id(visitor_external_id)
#         records = visitor.take_records
#         await uow.commit()
#     return records
#
#
# async def get_take_record_for_resource(resource_id: int) -> Optional[Record]:
#     async with UnitOfWork() as uow:
#         resource = await uow.resources.get(resource_id)
#         records = resource.records
#         await uow.commit()
#     records = [i for i in records if i.take_date and i.take_date < get_time_now()]
#     if len(records) > 1:
#         raise ValueError("Ресурс не может быть занят одновременно два раза")
#     elif len(records) == 1:
#         return records[0]
#     else:
#         return None
