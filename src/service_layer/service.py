import copy
from datetime import datetime as dt, timedelta as td
from typing import List, Optional, Tuple

from domain.models import Record, Resource, Visitor, Status, StageInfo
from helpers.helpers import get_time_now
from service_layer.records_helper import get_visitor_by_external_id, get_record
from service_layer.unit_of_work import UnitOfWork


async def get_resources_take_and_future_records() -> List[Tuple[Resource, Optional[Record], List[Record]]]:
    async with UnitOfWork() as uow:
        resources = await uow.resources.list()
        result = [(i, i.take_record, i.future_records) for i in resources]
        await uow.commit()
    return result


def get_last_booked_day_in_row(records: List[Record]) -> dt:
    """Возвращает день, когда ресурс освободится (после последовательно занятых дней)"""
    last_record = records[0]
    if len(records) == 1:
        return last_record.return_date
    for record in records[1:]:
        if last_record.return_date.date() + td(days=1) == record.take_date.date():
            last_record = record
        else:
            break
    return last_record.return_date


async def get_stage_info_for_visitor(email: str) -> List[StageInfo]:
    stage_infos = list()
    for resource, take_record, future_records in await get_resources_take_and_future_records():
        first_booked_day_in_future = None
        last_booked_day_in_row = None
        if take_record is not None:
            if take_record.email == email:
                status = Status.Yours
            else:
                status = Status.Others
                records = list()
                records.append(take_record)
                records += future_records
                last_booked_day_in_row = get_last_booked_day_in_row(records)
        elif len(future_records) == 0:
            status = Status.NoOne
        else:
            status = Status.WillBeTaken
            first_booked_day_in_future = future_records[0].take_date
        stage_info = StageInfo(
            resource_id=resource.resource_id,
            name=resource.name,
            current_take_date=None if take_record is None else take_record.take_date,
            current_return_date=None if take_record is None else take_record.return_date,
            status=status,
            first_booked_day_in_future=first_booked_day_in_future,
            last_booked_day_in_row=last_booked_day_in_row
        )
        stage_infos.append(stage_info)
    return stage_infos


async def take_resource(
        resource_name: str,
        visitor_external_id: int,
        since: dt,
        until: dt) -> Tuple[Optional[Resource], Optional[Record], Optional[Record]]:
    """Возвращает информацию про успешную запись, ресурс и конфликтующую запись"""
    async with UnitOfWork() as uow:
        resource = await uow.resources.get(resource_name)
        visitor = await uow.visitors.get_by_external_id(visitor_external_id)
        for record in [i for i in resource.records]:
            reservation_conflict = record.take_date <= since <= record.return_date \
                                   or record.take_date <= until <= record.return_date \
                                   or since <= record.take_date <= until
            if reservation_conflict:
                await uow.commit()
                return resource, None, record
        record = Record(resource_name=resource_name, email=visitor.email, take_date=since, return_date=until)
        uow.records.add(record)
        await uow.commit()
    return resource, record, None


async def return_resource(record_id: int, visitor_external_id: int) -> Tuple[Optional[Record], Optional[Resource]]:
    visitor_who_asks = await get_visitor_by_external_id(visitor_external_id)
    record, visitor, resource = await get_record(record_id)
    return_is_forbidden = record is None or (visitor_who_asks != visitor and not visitor.is_admin)
    if return_is_forbidden:
        return None, None
    record_before_update_return_date = copy.copy(record)
    record.return_date = get_time_now()
    async with UnitOfWork() as uow:
        uow.old_records.add(record)
        await uow.records.delete(record)
        await uow.commit()
    return record_before_update_return_date, resource


async def should_auth(external_id: int) -> bool:
    async with UnitOfWork() as uow:
        visitor = await uow.visitors.get_by_external_id(external_id)
        await uow.commit()
    return visitor is None


async def auth(
        email: str,
        external_id: int,
        is_admin: bool = False,
        chat_id: Optional[int] = None,
        username: Optional[str] = None,
        comment: Optional[str] = None
) -> Visitor:
    """Для первого входа пользователя в телеграме"""
    async with UnitOfWork() as uow:
        visitor = await uow.visitors.get(email) or Visitor(email)
        visitor.external_id = external_id
        visitor.is_admin = is_admin
        visitor.chat_id = chat_id
        visitor.username = username
        visitor.comment = comment
        uow.visitors.add(visitor)
        await uow.commit()
    return visitor


async def get_all_expired_records() -> List[Record]:
    async with UnitOfWork() as uow:
        records = await uow.records.get_expired()
        await uow.commit()
    return records


async def get_all_expiring_records(expire_after_days: int = 2) -> List[Record]:
    async with UnitOfWork() as uow:
        records = await uow.records.get_expiring(expire_after_days)
        await uow.commit()
    return records


async def delete_records(records):
    async with UnitOfWork() as uow:
        for record in records:
            await uow.records.delete(record)
        await uow.commit()
    return records

# async def change_record(
#         record_id: int,
#         take_date: Optional[dt] = None,
#         return_date: Optional[dt] = None
# ) -> Optional[Record]:
#     async with UnitOfWork() as uow:
#         record = await uow.records.get(record_id)
#         if record is None:
#             return None
#         if not await resource_is_free_universal(record.visitor.external_id, record.resource_id, take_date, return_date):
#             return None
#         if take_date:
#             record.take_date = take_date
#         if return_date:
#             record.return_date = return_date
#         await uow.commit()
#     return record
