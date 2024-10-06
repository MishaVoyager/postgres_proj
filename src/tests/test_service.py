from datetime import timedelta as td

import pytest
import pytest_asyncio

import adapters.dbhelper
from domain.models import Status
# from datetime import datetime as dt, timezone as tz
from helpers.helpers import get_time_now
from service_layer.records_helper import get_future_reservations_for_resource, \
    get_future_reservations_for_visitor, get_resources_in_category, get_categories, get_old_records_by_email, \
    get_old_records_by_resource_name
from service_layer.service import take_resource, return_resource, should_auth, auth, get_all_expired_records, \
    get_all_expiring_records, get_last_booked_day_in_row, get_resources_take_and_future_records, \
    get_stage_info_for_visitor
from tests.generator import gen_resource, gen_visitor, gen_past_time, gen_future_time, gen_record


@pytest_asyncio.fixture(loop_scope="function")
async def db_fixture():
    await adapters.dbhelper.drop_db_async()
    await adapters.dbhelper.start_db_async()
    yield
    adapters.dbhelper.clear_all_mappers()
    await adapters.dbhelper.drop_db_async()


@pytest.mark.asyncio
async def test_take_resource(db_fixture):
    resource = await gen_resource(1, name="resource")
    visitor = await gen_visitor("mnoskov@skbkontur.ru", 1)
    since = gen_past_time()
    until = gen_future_time()
    resource2, record, conflict_record = await take_resource(resource.name, visitor.external_id, since, until)
    assert resource2 == resource
    assert record.take_date == since
    assert record.return_date == until
    assert conflict_record is None


@pytest.mark.asyncio
async def test_take_resource_few_times_with_conflict(db_fixture):
    resource = await gen_resource(1, name="resource")
    visitor = await gen_visitor("mnoskov@skbkontur.ru", 1)
    since = gen_past_time()
    until = gen_future_time()
    await take_resource(resource.name, visitor.external_id, since, until)
    visitor2 = await gen_visitor("test@skbkontur.ru", 2)
    resource2, record, conflict_record = await take_resource(resource.name, visitor2.external_id, since + td(days=1),
                                                             until + td(days=-1))
    assert conflict_record.take_date == since
    assert conflict_record.return_date == until
    assert record is None
    assert resource2 == resource


@pytest.mark.asyncio
async def test_take_resource_few_times_without_conflict(db_fixture):
    resource = await gen_resource(1, name="resource")
    visitor = await gen_visitor("mnoskov@skbkontur.ru", 1)
    _, record, _ = await take_resource(resource.name, visitor.external_id, get_time_now() + td(days=8),
                                       get_time_now() + td(days=9))
    _, record2, _ = await take_resource(resource.name, visitor.external_id, get_time_now() + td(days=10),
                                        get_time_now() + td(days=11))
    records_for_resource = await get_future_reservations_for_resource(resource.name)
    records_for_visitor = await get_future_reservations_for_visitor(visitor.email)
    assert records_for_resource == [record, record2]
    assert records_for_visitor == [record, record2]


@pytest.mark.asyncio
async def test_get_resources_in_category(db_fixture):
    resource1 = await gen_resource(1, category_name="Принтер", name="1")
    resource2 = await gen_resource(2, category_name="Принтер", name="2")
    resource3 = await gen_resource(3, category_name="ККТ", name="3")

    resources = await get_resources_in_category("Принтер")
    assert len(resources) == 2
    assert resource1 in resources
    assert resource2 in resources


@pytest.mark.asyncio
async def test_get_categories(db_fixture):
    resource1 = await gen_resource(2, category_name="Принтер", name="2")
    resource2 = await gen_resource(3, category_name="ККТ", name="3")
    categories = await get_categories()
    assert [i for i in categories] == ["Принтер", "ККТ"]


@pytest.mark.asyncio
async def test_should_auth_old_user(db_fixture):
    email = "test@skbkontur.ru"
    visitor = await gen_visitor(email, 55)
    assert (await should_auth(55)) is False


@pytest.mark.asyncio
async def test_auth_new_user(db_fixture):
    email = "test@skbkontur.ru"
    assert await should_auth(55)
    visitor = await auth(email, 55, False, 100500, "voyager", "comment")
    assert visitor.email == email
    assert visitor.external_id == 55


@pytest.mark.asyncio
async def test_auth_user_without_extra_info(db_fixture):
    email = "test@skbkontur.ru"
    visitor = await gen_visitor(email)
    assert await should_auth(55)
    visitor = await auth(email, 55, False, 100500, "voyager", "comment")
    assert visitor.email == email
    assert visitor.external_id == 55


@pytest.mark.asyncio
async def test_get_all_expired_records(db_fixture):
    record1 = await gen_record(await gen_resource(1, name="1"), await gen_visitor(), take_date=gen_past_time(),
                               return_date=get_time_now())
    record2 = await gen_record(await gen_resource(2, name="2"), await gen_visitor("test2@skbkontur.ru"),
                               take_date=gen_past_time(),
                               return_date=get_time_now())
    record3 = await gen_record(await gen_resource(3, name="3"), await gen_visitor("test3@skbkontur.ru"),
                               take_date=gen_past_time(),
                               return_date=get_time_now() + td(minutes=1))
    records = await get_all_expired_records()
    assert records == [record1, record2]


@pytest.mark.asyncio
async def test_get_all_expiring_records(db_fixture):
    record1 = await gen_record(await gen_resource(1, name="1"), await gen_visitor(), take_date=gen_past_time(),
                               return_date=get_time_now())
    record2 = await gen_record(await gen_resource(2, name="2"), await gen_visitor("test2@skbkontur.ru"),
                               take_date=gen_past_time(),
                               return_date=get_time_now() + td(days=2))
    record3 = await gen_record(await gen_resource(3, name="3"), await gen_visitor("test3@skbkontur.ru"),
                               take_date=gen_past_time(),
                               return_date=get_time_now() + td(days=0, hours=23, minutes=59, seconds=59))
    record4 = await gen_record(await gen_resource(4, name="4"), await gen_visitor("test4@skbkontur.ru"),
                               take_date=gen_past_time(),
                               return_date=get_time_now() + td(days=3))
    records = await get_all_expiring_records(2)
    assert records == [record2, record3]


@pytest.mark.asyncio
async def test_old_record_by_visitor(db_fixture):
    resource = await gen_resource(1)
    visitor = await gen_visitor("test@skbkontur.ru", 1)
    _, take_record, _ = await take_resource(resource.name, visitor.external_id, gen_past_time(), gen_future_time())
    return_record, _ = await return_resource(take_record.record_id, 1)
    assert take_record == return_record
    old_records = await get_old_records_by_email(visitor.email)
    assert len(old_records) == 1
    old_record = old_records[0]
    assert old_record.take_date == return_record.take_date
    assert old_record.resource == resource
    old_records2 = await get_old_records_by_resource_name(resource.name)
    assert old_records == old_records2


@pytest.mark.asyncio
async def test_get_last_booked_day_in_row_with_one_record(db_fixture):
    resource = await gen_resource(1, name="Стейдж1")
    visitor = await gen_visitor("test@skbkontur.ru", 1)
    last_booked_day = get_time_now() + td(days=4)
    _, record1, _ = await take_resource(resource.name, 1, since=get_time_now() - td(days=1),
                                        until=last_booked_day)
    assert get_last_booked_day_in_row([record1]) == last_booked_day


@pytest.mark.asyncio
async def test_get_last_booked_day_in_row_with_two_records_with_break(db_fixture):
    resource = await gen_resource(1, name="Стейдж1")
    visitor = await gen_visitor("test@skbkontur.ru", 1)
    last_booked_day_in_row = get_time_now() + td(days=1)
    last_booked_day = get_time_now() + td(days=4)
    _, record1, _ = await take_resource(resource.name, 1, since=get_time_now() - td(days=1),
                                        until=last_booked_day_in_row)
    _, record2, _ = await take_resource(resource.name, 1, since=get_time_now() + td(days=3), until=last_booked_day)
    assert get_last_booked_day_in_row([record1, record2]) == last_booked_day_in_row


@pytest.mark.asyncio
async def test_get_last_booked_day_in_row_with_two_records_in_row(db_fixture):
    resource = await gen_resource(1, name="Стейдж1")
    visitor = await gen_visitor("test@skbkontur.ru", 1)
    last_booked_day = get_time_now() + td(days=3)
    _, record1, _ = await take_resource(resource.name, 1, since=get_time_now() - td(days=1),
                                        until=get_time_now() + td(days=1))
    _, record2, _ = await take_resource(resource.name, 1, since=get_time_now() + td(days=2), until=last_booked_day)
    assert get_last_booked_day_in_row([record1, record2]) == last_booked_day


@pytest.mark.asyncio
async def test_get_resources_take_and_future_records_are_sorted(db_fixture):
    resource = await gen_resource(1, name="Стейдж1")
    visitor = await gen_visitor("test@skbkontur.ru", 1)

    _, record3, _ = await take_resource(resource.name, 1, since=get_time_now() + td(days=4),
                                        until=get_time_now() + td(days=5))

    _, record2, _ = await take_resource(resource.name, 1, since=get_time_now() + td(days=2),
                                        until=get_time_now() + td(days=3))
    _, record1, _ = await take_resource(resource.name, 1, since=get_time_now() - td(days=1),
                                        until=get_time_now() + td(days=1))

    resource, take_record, future_records = (await get_resources_take_and_future_records())[0]
    is_sorted_asc = all(a < b for a, b in zip(future_records, future_records[1:]))

    assert resource == resource
    assert take_record == record1
    assert is_sorted_asc


@pytest.mark.asyncio
async def test_get_resources_take_and_future_records_only_future(db_fixture):
    resource = await gen_resource(1, name="Стейдж1")
    visitor = await gen_visitor("test@skbkontur.ru", 1)

    _, record3, _ = await take_resource(resource.name, 1, since=get_time_now() + td(days=4),
                                        until=get_time_now() + td(days=5))

    _, record2, _ = await take_resource(resource.name, 1, since=get_time_now() + td(days=2),
                                        until=get_time_now() + td(days=3))

    resource, take_record, future_records = (await get_resources_take_and_future_records())[0]
    is_sorted_asc = all(a < b for a, b in zip(future_records, future_records[1:]))

    assert take_record is None
    assert is_sorted_asc


@pytest.mark.asyncio
async def test_get_resources_take_and_future_records_few_resources(db_fixture):
    resource = await gen_resource(1, name="Стейдж1")
    resource2 = await gen_resource(2, name="Стейдж2")
    visitor = await gen_visitor("test@skbkontur.ru", 1)

    _, record1, _ = await take_resource(resource.name, 1, since=get_time_now() - td(days=1),
                                        until=get_time_now() + td(days=1))
    _, record2, _ = await take_resource(resource.name, 1, since=get_time_now() + td(days=2),
                                        until=get_time_now() + td(days=3))
    _, record3, _ = await take_resource(resource.name, 1, since=get_time_now() + td(days=4),
                                        until=get_time_now() + td(days=5))

    _, record4, _ = await take_resource(resource2.name, 1, since=get_time_now() - td(days=1),
                                        until=get_time_now() + td(days=1))
    _, record5, _ = await take_resource(resource2.name, 1, since=get_time_now() + td(days=2),
                                        until=get_time_now() + td(days=3))
    _, record6, _ = await take_resource(resource2.name, 1, since=get_time_now() + td(days=4),
                                        until=get_time_now() + td(days=5))
    result = await get_resources_take_and_future_records()

    resource3, take_record, future_records = result[0]
    assert resource3 == resource
    assert take_record == record1
    assert future_records == [record2, record3]

    resource4, take_record, future_records = result[1]
    assert resource4 == resource2
    assert take_record == record4
    assert future_records == [record5, record6]


@pytest.mark.asyncio
async def test_get_stage_info_for_visitor(db_fixture):
    resource = await gen_resource(1, name="Стейдж1")
    resource2 = await gen_resource(2, name="Стейдж2")
    resource3 = await gen_resource(3, name="Стейдж3")
    resource4 = await gen_resource(4, name="Стейдж4")
    resource5 = await gen_resource(5, name="Стейдж5")
    resource6 = await gen_resource(6, name="Стейдж6")
    visitor = await gen_visitor("test@skbkontur.ru", 1)
    visitor2 = await gen_visitor("test2@skbkontur.ru", 2)
    visitor3 = await gen_visitor("mnoskov@skbkontur.ru", 230809906)

    # Status.Yours
    your_take_date = get_time_now() - td(days=1)
    your_return_date = get_time_now() + td(days=40)
    await take_resource(resource.name, 230809906, since=your_take_date, until=your_return_date)

    # Для второго ресурса - Status.NoOne

    # Status.Others
    others_take_date = get_time_now() - td(days=1)
    others_return_date = get_time_now() + td(days=40)
    await take_resource(resource3.name, 1, since=others_take_date, until=others_return_date)

    # Status.Others (несколько записей от разных людей подряд)
    last_booked_day_in_row = get_time_now() + td(days=30)
    await take_resource(resource4.name, 1, since=get_time_now() - td(days=1), until=last_booked_day_in_row)
    await take_resource(resource4.name, 2, since=get_time_now() + td(days=11), until=get_time_now() + td(days=30))

    # Status.WillBeTaken
    first_booked_day_in_future = get_time_now() + td(days=11)
    await take_resource(resource5.name, 1, since=get_time_now() + td(days=11), until=get_time_now() + td(days=30))

    stage_infos = await get_stage_info_for_visitor("mnoskov@skbkontur.ru")

    assert stage_infos[0].status == Status.Yours
    assert stage_infos[0].current_take_date == your_take_date
    assert stage_infos[0].current_return_date == your_return_date

    assert stage_infos[1].status == Status.NoOne
    assert stage_infos[1].name == resource2.name
    assert stage_infos[1].resource_id == resource2.resource_id

    assert stage_infos[2].status == Status.Others
    assert stage_infos[2].current_take_date == others_take_date
    assert stage_infos[2].current_return_date == others_return_date

    assert stage_infos[3].status == Status.Others
    assert stage_infos[3].last_booked_day_in_row == last_booked_day_in_row
    assert stage_infos[3].first_booked_day_in_future is None

    assert stage_infos[4].status == Status.WillBeTaken
    assert stage_infos[4].first_booked_day_in_future == first_booked_day_in_future
    assert stage_infos[4].last_booked_day_in_row is None


#
@pytest.mark.asyncio
@pytest.mark.manual
async def test_drop_db():
    await adapters.dbhelper.drop_db_async()


@pytest.mark.asyncio
@pytest.mark.manual
async def test_create_test_date():
    await adapters.dbhelper.drop_db_async()
    await adapters.dbhelper.start_db_async()
    comment = "Адрес: https://market.testkontur.ru\r\nАдминка: https://market.testkontur.ru/AdminTools"
    resource = await gen_resource(1, name="Стейдж1", comment=comment)
    resource2 = await gen_resource(2, name="Стейдж2", comment=comment)
    resource3 = await gen_resource(3, name="Стейдж3", comment=comment)
    resource4 = await gen_resource(4, name="Стейдж4", comment=comment)
    resource5 = await gen_resource(5, name="Стейдж5", comment=comment)
    resource6 = await gen_resource(6, name="Стейдж6", comment=comment)
    visitor = await gen_visitor("test@skbkontur.ru", 1)
    visitor2 = await gen_visitor("test2@skbkontur.ru", 2)
    visitor3 = await gen_visitor("mnoskov@skbkontur.ru", 230809906)

    # Status.Yours
    await take_resource(resource.name, 230809906, since=get_time_now() - td(days=1), until=get_time_now() + td(days=40))

    # Для второго ресурса - Status.NoOne

    # Status.Others
    await take_resource(resource3.name, 1, since=get_time_now() - td(days=1), until=get_time_now() + td(days=40))

    # Status.Others (несколько записей от разных людей подряд)
    await take_resource(resource4.name, 1, since=get_time_now() - td(days=1), until=get_time_now() + td(days=10))
    await take_resource(resource4.name, 2, since=get_time_now() + td(days=11), until=get_time_now() + td(days=30))

    # Status.WillBeTaken
    await take_resource(resource5.name, 1, since=get_time_now() + td(days=11), until=get_time_now() + td(days=30))
