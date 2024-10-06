# async def take_resource_for_interval_universal(
#         resource_id: int,
#         visitor_external_id: int,
#         interval: td) -> Optional[Record]:
#     take_date = get_time_now()
#     return await take_resource_universal(resource_id, visitor_external_id, take_date, take_date + interval)
#
#
# async def take_resource_universal(
#         resource_id: int,
#         visitor_external_id: int,
#         take_date: Optional[dt] = None,
#         return_date: Optional[dt] = None,
# ) -> Optional[Record]:
#     """Если ресурс не занят, создаем для пользователя запись с take_date (если занят, его должны сначала вернуть)"""
#     if not await resource_is_free_universal(visitor_external_id, resource_id, take_date, return_date):
#         return None
#     async with UnitOfWork() as uow:
#         visitor = await uow.visitors.get_by_external_id(visitor_external_id)
#         time = take_date if take_date else get_time_now()
#         record = Record(resource_id=resource_id, email=visitor.email, take_date=time, return_date=return_date)
#         uow.records.add(record)
#         await uow.commit()
#     return record
#
#
# async def return_resource_universal(resource_id: int, visitor_external_id: int) -> Optional[Record]:
#     """Универсальный вариант для очереди + расписания"""
#     queue = await get_queue(resource_id)
#     async with UnitOfWork() as uow:
#         visitor = await uow.visitors.get_by_external_id(visitor_external_id)
#         take_record = await get_taken_record(visitor.email, resource_id)
#         await uow.commit()
#     if take_record is None:
#         return None
#     take_record.return_date = get_time_now()
#     async with UnitOfWork() as uow:
#         uow.old_records.add(take_record)
#         await uow.records.delete(take_record)
#         if len(queue) != 0:
#             next_user_record = await uow.records.get(queue[0].record_id)
#             next_user_record.enqueue_date = None
#             next_user_record.take_date = get_time_now()
#         await uow.commit()
#     return take_record
#
#
# async def enqueue(resource_id: int, visitor_external_id: int, enqueue_date: dt = None):
#     async with UnitOfWork() as uow:
#         visitor = await uow.visitors.get_by_external_id(visitor_external_id)
#         time = enqueue_date if enqueue_date else get_time_now()
#         record = Record(visitor.email, resource_id, enqueue_date=time)
#         uow.records.add(record)
#         await uow.commit()
#     return record
#
#
# async def dequeue(resource_id: int, visitor_external_id: int):
#     async with UnitOfWork() as uow:
#         visitor = await uow.visitors.get_by_external_id(visitor_external_id)
#         record = await get_queued_record(visitor.email, resource_id)
#         await uow.commit()
#     async with UnitOfWork() as uow:
#         await uow.records.delete(record)
#         await uow.commit()
#
#
# async def get_wishlist(visitor_external_id: int) -> List[Record]:
#     async with UnitOfWork() as uow:
#         visitor = await uow.visitors.get_by_external_id(visitor_external_id)
#         records = visitor.future_records + visitor.queue_records
#         await uow.commit()
#     return records
#
#
# async def get_queued_record(email: str, resource_id: int) -> Record:
#     async with UnitOfWork() as uow:
#         result = await uow.execute(
#             select(Record).filter_by(email=email, resource_id=resource_id).where(Record.enqueue_date is not None))
#         records = result.scalars().unique().get_all()
#         if len(records) != 1:
#             raise ValueError(f"Пользователь {email} встал {len(records)} раз в очередь на ресурс {resource_id}")
#         await uow.commit()
#     return records[0]
#
#
# async def get_queue(resource_id: int) -> List[Record]:
#     async with UnitOfWork() as uow:
#         resource = await uow.resources.get(resource_id)
#         queue = resource.queue_records
#         await uow.commit()
#     return queue
#
#
# async def resource_is_free_universal(visitor_external_id: int, resource_id: int, since: Optional[dt] = None,
#                                      until: Optional[dt] = None):
#     """Вариант для очереди + расписания"""
#     async with UnitOfWork() as uow:
#         resource = await uow.resources.get(resource_id)
#         if since is None and until is None:
#             await uow.commit()
#             return resource.take_record is None
#         for record in [i for i in resource.records]:
#             reservation_conflict = record.take_date <= since <= record.return_date \
#                                    or record.take_date <= until <= record.return_date \
#                                    or since <= record.take_date <= until
#             if reservation_conflict:
#                 await uow.commit()
#                 return False
#         await uow.commit()
#         return True
