from adapters.repository import (
    AbstractCategoryRepository,
    AbstractResourceRepository,
    AbstractRecordRepository,
    AbstractVisitorRepository
)

from domain.models import Visitor, Record, Resource, Category
from service_layer.unit_of_work import IUnitOfWork


class FakeVisitorRepository(AbstractVisitorRepository):
    def __init__(self, visitors: list = []):
        self.visitors = list(visitors)

    def add(self, visitor: Visitor) -> None:
        self.visitors.append(visitor)

    def get(self, email) -> Visitor:
        return [i for i in self.visitors if i.email == email][0]

    def list(self):
        pass

    def delete(self, visitor: Visitor = []) -> None:
        self.visitors.remove(visitor)

    def get_many(self, ids: list) -> 'list[Visitor]':
        raise NotImplemented


class FakeResourceRepository(AbstractResourceRepository):
    def __init__(self, resources: list = []):
        self.resources = list(resources)

    def add(self, resource: Resource) -> None:
        self.resources.append(resource)

    def get(self, resource_id) -> Resource:
        return [i for i in self.resources if i.resource_id == resource_id][0]

    def list(self):
        pass

    def delete(self, resource: Resource) -> None:
        self.resources.remove(resource)

    def get_many(self, ids: list) -> 'list[Resource]':
        raise NotImplemented


class FakeRecordRepository(AbstractRecordRepository):
    def __init__(self, records: list):
        self.records = list(records)

    def add(self, record: Record) -> None:
        self.records.append(record)

    def get(self, record_id) -> Record:
        return [i for i in self.records if i.record_id == record_id][0]

    def list(self):
        pass

    def delete(self, record: Record) -> None:
        self.records.remove(record)

    def get_many(self, ids: list) -> 'list[Record]':
        raise NotImplemented


class FakeCategoryRepository(AbstractCategoryRepository):
    def __init__(self, categories: list):
        self.categories = list(categories)

    def add(self, category: Category) -> None:
        self.categories.append(category)

    def get(self, name) -> Category:
        return [i for i in self.categories if i.name == name][0]

    def list(self):
        pass

    def delete(self, category: Category) -> None:
        self.categories.remove(category)

    def get_many(self, ids: list) -> 'list[Category]':
        raise NotImplemented


class FakeUnitOfWork(IUnitOfWork):
    def __init__(self, visitors: list = [], resources: list = [], records: list = [], categories: list = []):
        self.visitors = FakeVisitorRepository(visitors)
        self.resources = FakeResourceRepository(resources)
        self.records = FakeRecordRepository(records)
        self.categories = FakeCategoryRepository(categories)
        self.commited = False

    def __enter__(self):
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass
