from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from interfaces import IRepository, IUnitOfWork
from models import Visitor


class VisitorRepository(IRepository[Visitor]):
    def __init__(self, session: Session):
        self.session = session

    def add(self, visitor) -> None:
        self.session.add(visitor)

    def get(self, email) -> Visitor:
        return self.session.query(Visitor).filter_by(email=email).first()

    def list(self):
        pass

    def delete(self, visitor) -> None:
        self.session.delete(visitor)


class VisitorFakeRepository[Visitor](IRepository):
    def __init__(self, visitors: list):
        self.visitors = list(visitors)

    def add(self, visitor: Visitor) -> None:
        self.visitors.append(visitor)

    def get(self, email) -> Visitor:
        return [i for i in self.visitors if i.email == email][0]

    def list(self):
        pass

    def delete(self, visitor: Visitor) -> None:
        self.visitors.remove(visitor)


class UnitOfWork(IUnitOfWork):
    def __init__(self):
        self.session_factory = sessionmaker(bind=create_engine(
            "postgresql+psycopg2://postgres:pgpwd4habr@localhost:5432/postgres",
            isolation_level="REPEATABLE READ")
        )

    def __enter__(self):
        self.session = self.session_factory()  # type: Session
        self.visitors = VisitorRepository(self.session)
        return super().__enter__()

    def __exit__(self, *args):
        super().__exit__(*args)
        self.session.close()

    def _commit(self):
        self.session.commit()

    def rollback(self):
        self.session.rollback()
