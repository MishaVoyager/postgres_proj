# import pytest

# from domain.models import Visitor, Resource, Record, Category
# from tests.fakes import FakeUnitOfWork


# @pytest.fixture
# def db_fixture():
#     yield


# def test_add_user(db_fixture):
#     with FakeUnitOfWork() as uow:
#         visitor = Visitor(visitor_id=1, email="vecheren@gmail.com", is_admin=True)
#         uow.visitors.add(visitor)
#         uow.commit()


# def test_delete_user(db_fixture):
#     with FakeUnitOfWork() as uow:
#         visitor = Visitor(visitor_id=1, email="vecheren@gmail.com", is_admin=True)
#         uow.visitors.add(visitor)
#         uow.commit()
#         visitor = uow.visitors.get("vecheren@gmail.com")
#         uow.visitors.delete(visitor)
#         uow.commit()


# def test_add_recource(db_fixture):
#     with FakeUnitOfWork() as uow:
#         category = Category("cat")
#         uow.categories.add(category)
#         uow.commit()

#         resource = Resource(resource_id=1, name="name", category="cat")
#         uow.resources.add(resource)
#         uow.commit()


# def test_delete_resource(db_fixture):
#     with FakeUnitOfWork() as uow:
#         category = Category("cat")
#         uow.categories.add(category)
#         uow.commit()
#         resource = Resource(resource_id=1, name="name", category="cat")
#         uow.resources.add(resource)
#         uow.commit()
#         resource = uow.resources.get(1)
#         uow.resources.delete(resource)
#         uow.commit()


# def test_add_record(db_fixture):
#     with FakeUnitOfWork() as uow:
#         category = Category("cat")
#         uow.categories.add(category)
#         uow.commit()
#         visitor = Visitor(visitor_id=1, email="vecheren@gmail.com", is_admin=True)
#         resource = Resource(resource_id=1, name="name", category="cat")
#         uow.records.add(visitor)
#         uow.records.add(resource)
#         uow.commit()

#         record = Record(visitor=visitor, resource=resource)
#         uow.records.add(record)
#         uow.commit()


# def test_delete_record(db_fixture):
#     """
#     Запись можно добавить, только если  предыдущие коммиты уже добавили пользователя и ресурс.
#     Одновременно - нельзя, будет IntegrityError
#     """
#     with FakeUnitOfWork() as uow:
#         category = Category("cat")
#         uow.categories.add(category)
#         uow.commit()
#         visitor = Visitor(visitor_id=1, email="vecheren@gmail.com", is_admin=True)
#         resource = Resource(resource_id=1, name="name", category="cat")
#         record = Record(visitor=visitor, resource=resource)
#         uow.visitors.add(visitor)
#         uow.resources.add(resource)
#         uow.commit()
#         uow.records.add(record)
#         uow.commit()

#         record = uow.records.get(1)
#         uow.records.delete(record)
#         uow.commit()
