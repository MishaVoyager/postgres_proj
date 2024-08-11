import models
import orm
from domain import VisitorFakeRepository, UnitOfWork

orm.start_mappers()

def test_add_user():
    # orm.start_mappers()
    with UnitOfWork() as uow:
        visitor = models.Visitor(id=1, email="vecheren@gmail.com", is_admin=True)
        uow.visitors.add(visitor)
        uow.commit()


def test_delete_user():
    # orm.start_mappers()
    with UnitOfWork() as uow:
        visitor = uow.visitors.get("vecheren@gmail.com")
        uow.visitors.delete(visitor)
        uow.commit()


def test_add_fake():
    repo = VisitorFakeRepository(list())
    visitor = models.Visitor(id=1, email="vecheren@gmail.com", is_admin=True)
    repo.add(visitor)
    assert visitor in repo.visitors


def test_delete_fake():
    visitor = models.Visitor(id=1, email="vecheren@gmail.com", is_admin=True)
    repo = VisitorFakeRepository([visitor])
    repo.delete(visitor)
    assert len(repo.visitors) == 0

    # engine = create_engine(f"postgresql+psycopg2://postgres:pgpwd4habr@localhost:5432/postgres")
    # session: Session = create_session(engine)
    # repo = AlchemyRepository(session)
    # visitor = models.Visitor(id=1, email="vecheren@gmail.com", is_admin=True)
    # repo.add(visitor)
    # session.commit()
    # session.close()

    # engine = create_engine(f"postgresql+psycopg2://postgres:pgpwd4habr@localhost:5432/postgres")
    # session: Session = create_session(engine)
    # repo = AlchemyRepository(session)
    # visitor = repo.get_one(models.Visitor, ident="vecheren@gmail.com")
    # repo.delete(visitor)
    # session.commit()
    # session.close()
