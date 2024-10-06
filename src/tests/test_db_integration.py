# import pytest

# import adapters.dbhelper
# from domain.models import Visitor, Resource, Record, Category
# from service_layer.unit_of_work import UnitOfWork


# @pytest.fixture
# def db_fixture():
#     adapters.dbhelper.drop_db()
#     adapters.dbhelper.start_db()
#     yield
#     adapters.dbhelper.clear_all_mappers()
#     adapters.dbhelper.drop_db()


# def test_add_user(db_fixture):
#     with UnitOfWork() as uow:
#         visitor = Visitor(email="vecheren@gmail.com", is_admin=True)
#         uow.visitors.add(visitor)
#         uow.commit()


# def test_delete_user(db_fixture):
#     with UnitOfWork() as uow:
#         visitor = Visitor(email="vecheren@gmail.com", is_admin=True)
#         uow.visitors.add(visitor)
#         uow.commit()
#         visitor = uow.visitors.get("vecheren@gmail.com")
#         uow.visitors.delete(visitor)
#         uow.commit()


# def test_add_resource(db_fixture):
#     with UnitOfWork() as uow:
#         category = Category("cat")
#         uow.categories.add(category)
#         resource = Resource(resource_id=1, name="name", category=category)
#         uow.resources.add(resource)
#         uow.commit()


# def test_delete_resource(db_fixture):
#     with UnitOfWork() as uow:
#         category = Category("cat")
#         uow.categories.add(category)
#         resource = Resource(resource_id=1, name="name", category=category)
#         uow.resources.add(resource)
#         uow.commit()
#         resource = uow.resources.get(1)
#         uow.resources.delete(resource)
#         uow.commit()


# def test_add_record(db_fixture):
#     with UnitOfWork() as uow:
#         category = Category("cat")
#         uow.categories.add(category)
#         visitor = Visitor(email="vecheren@gmail.com", is_admin=True)
#         resource = Resource(resource_id=1, name="name", category=category)
#         uow.visitors.add(visitor)
#         uow.resources.add(resource)
#         record = Record(visitor=visitor, resource=resource)
#         uow.records.add(record)
#         uow.commit()


# def test_delete_record(db_fixture):
#     with UnitOfWork() as uow:
#         category = Category("cat")
#         uow.categories.add(category)
#         visitor = Visitor(email="vecheren@gmail.com", is_admin=True)
#         resource = Resource(resource_id=1, name="name", category=category)
#         record = Record(resource=resource, visitor=visitor)
#         uow.visitors.add(visitor)
#         uow.resources.add(resource)
#         uow.records.add(record)
#         uow.commit()
#         record = uow.records.get(1)

#         uow.records.delete(record)
#         uow.commit()


# def test_get_records_fromresource(db_fixture):
#     with UnitOfWork() as uow:
#         category = Category("cat")
#         uow.categories.add(category)
#         visitor1 = Visitor(email="vecheren@gmail.com", is_admin=True)
#         visitor2 = Visitor(email="test@gmail.com", is_admin=False)
#         resource = Resource(resource_id=1, name="name", category=category)
#         record1 = Record(visitor=visitor1, resource=resource)
#         record2 = Record(visitor=visitor2, resource=resource)

#         uow.visitors.add(visitor1)
#         uow.visitors.add(visitor2)
#         uow.resources.add(resource)
#         uow.commit()
#         uow.records.add(record1)
#         uow.records.add(record2)
#         uow.commit()

#         resourcex = uow.resources.get(1)
#         record_one = resourcex.records[0]
#         record_two = resourcex.records[1]
#         print()
