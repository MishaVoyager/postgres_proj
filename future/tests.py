# @pytest.mark.asyncio
# async def test_return_resource_with_queue(db_fixture):
#     resource = await gen_resource(1)
#     visitor = await gen_visitor("test@skbkontur.ru", 1)
#     visitor_in_queue = await gen_visitor("test2@skbkontur.ru", 2)
#     queue_record = await enqueue(resource.resource_id, visitor_in_queue.external_id, gen_past_time())
#     take_record = await take_resource_universal(resource.resource_id, visitor.external_id)
#     return_record = await return_resource_universal(1, 1)
#     assert return_record.record_id == take_record.record_id
#     assert return_record.enqueue_date is None
#     assert return_record.take_date is not None
#     assert return_record.return_date is not None
#     take_record = await get_taken_record(visitor_in_queue.email, resource.resource_id)
#     assert take_record.record_id == queue_record.record_id
#     assert take_record.enqueue_date is None
#     assert take_record.take_date is not None
#     async with UnitOfWork() as uow:
#         old_records = await uow.old_records.list()
#         assert len(old_records) == 1
#         old_record = await uow.old_records.get(return_record.record_id)
#         assert old_record.take_date == return_record.take_date
#         assert old_record.return_date == return_record.return_date
#
#
# @pytest.mark.asyncio
# async def test_dequeue(db_fixture):
#     resource = await gen_resource(1)
#     visitor = await gen_visitor("test@skbkontur.ru", 1)
#     await enqueue(1, 1)
#     async with UnitOfWork() as uow:
#         assert len(await uow.records.list()) == 1
#     await dequeue(1, 1)
#     async with UnitOfWork() as uow:
#         assert len(await uow.records.list()) == 0
#
#
# @pytest.mark.asyncio
# async def test_dequeue_with_two_visitors(db_fixture):
#     resource = await gen_resource(1)
#     visitor = await gen_visitor("test@skbkontur.ru", 1)
#     visitor2 = await gen_visitor("test2@skbkontur.ru", 2)
#     enqueue_record = await enqueue(1, 1)
#     enqueue_record2 = await enqueue(1, 2)
#     await dequeue(1, 1)
#     assert (await get_queued_record(visitor2.email, resource.resource_id)).record_id == enqueue_record2.record_id
#     await dequeue(1, 2)
#     async with UnitOfWork() as uow:
#         assert len(await uow.records.list()) == 0

# @pytest.mark.asyncio
# async def test_take_resource_for_interval_in_hours(db_fixture):
#     resource = await gen_resource(1, category_name="Принтер")
#     visitor = await gen_visitor("test@skbkontur.ru", 1)
#     interval = td(hours=8)
#     record = await take_resource_for_interval_universal(1, 1, interval)
#     assert record.take_date is not None
#     assert record.return_date == record.take_date + interval
#
#
# @pytest.mark.asyncio
# async def test_take_resource_for_interval_in_days(db_fixture):
#     resource = await gen_resource(1, category_name="Принтер")
#     visitor = await gen_visitor("test@skbkontur.ru", 1)
#     interval = td(days=3)
#     record = await take_resource_for_interval_universal(1, 1, interval)
#     assert record.take_date is not None
#     assert record.return_date == record.take_date + interval

# @pytest.mark.asyncio
# async def test_take_for_period(db_fixture):
#     resource = await gen_resource(1, category_name="Принтер")
#     visitor = await gen_visitor("test@skbkontur.ru", 1)
#     record = await take_resource_universal(1, 1, gen_past_time(), gen_future_time())
#     assert record.email == visitor.email
#     assert record.resource_id == resource.resource_id
#

#
# @pytest.mark.asyncio
# async def test_search_by_id(db_fixture):
#     resource1 = await gen_resource(1)
#     resource2 = await gen_resource(2)
#     async with UnitOfWork() as uow:
#         resources = await uow.resources.search("1")
#         await uow.commit()
#     assert len(resources) == 1
#     assert resource1 in resources
#     assert resource2 not in resources
#
#
# @pytest.mark.asyncio
# async def test_search_by_name(db_fixture):
#     resource1 = await gen_resource(1, name="ресурс")
#     resource2 = await gen_resource(2, name="хрень")
#     async with UnitOfWork() as uow:
#         resources = await uow.resources.search("рес")
#         await uow.commit()
#     assert len(resources) == 1
#     assert resource1 in resources
#     assert resource2 not in resources

# @pytest.mark.asyncio
# async def test_enqueue(db_fixture):
#     resource = await gen_resource(1)
#     visitor = await gen_visitor("test@skbkontur.ru", 1)
#     record = await enqueue(1, 1)
#     assert record.enqueue_date
#
#
# @pytest.mark.asyncio
# async def test_return_resource_without_queue(db_fixture):
#     resource = await gen_resource(1)
#     visitor = await gen_visitor("test@skbkontur.ru", 1)
#     take_record = await take_resource_universal(resource.resource_id, visitor.external_id)
#     return_record = await return_resource_universal(1, 1)
#     assert return_record.record_id == take_record.record_id
#     assert return_record.enqueue_date is None
#     assert return_record.take_date is not None
#     assert return_record.return_date is not None
#     async with UnitOfWork() as uow:
#         records = await uow.records.list()
#         assert len(records) == 0
#         old_record = await uow.old_records.get(take_record.record_id)
#         assert old_record.take_date == return_record.take_date
#         assert old_record.return_date == return_record.return_date
#
#
# @pytest.mark.asyncio
# async def test_get_taken_by_user_records(db_fixture):
#     resource = await gen_resource(1)
#     visitor = await gen_visitor("mnoskov@skbkontur.ru", 1)
#     past_record = await gen_record(resource, visitor, take_date=gen_past_time())
#     future_record = await gen_record(resource, visitor, take_date=gen_future_time())
#     records = await get_taken(1)
#     assert len(records) == 1
#     assert records[0].take_date == past_record.take_date
#
#
# @pytest.mark.asyncio
# async def test_get_user_wishlist_records(db_fixture):
#     visitor = await gen_visitor("mnoskov@skbkontur.ru", 1)
#     resource = await gen_resource(1)
#     resource2 = await gen_resource(2)
#     resource3 = await gen_resource(3)
#     record_queued = await gen_record(resource, visitor, enqueue_date=gen_past_time())
#     record_taken = await gen_record(resource2, visitor, take_date=gen_past_time())
#     record_booked = await gen_record(resource3, visitor, take_date=gen_future_time())
#
#     records = await get_wishlist(1)
#     assert len(records) == 2
#     assert record_queued in records
#     assert record_booked in records
#     assert record_taken not in records
#
#
# @pytest.mark.asyncio
# async def test_get_queue_for_resource_records(db_fixture):
#     resource = await gen_resource(1)
#     visitor = await gen_visitor("mnoskov@skbkontur.ru", 1)
#     visitor2 = await gen_visitor("test1@skbkontur.ru", 2)
#     visitor3 = await gen_visitor("test2@skbkontur.ru", 3)
#     record = await gen_record(resource, visitor, enqueue_date=None)
#     record2 = await gen_record(resource, visitor2, enqueue_date=gen_past_time())
#     record3 = await gen_record(resource, visitor3, enqueue_date=gen_future_time())
#     visitor4 = await gen_visitor("test3@skbkontur.ru", 4)
#     resource2 = await gen_resource(2)
#     record4 = await gen_record(resource2, visitor4, enqueue_date=gen_past_time())
#     queue = await get_queue(1)
#
#     assert len(queue) == 2
#     assert queue[0] == record2
#     assert queue[1] == record3
#