from datetime import datetime
from typing import Optional
from dataclasses import dataclass

from sqlalchemy import (
    Table,
    MetaData,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    ForeignKey,
    event, func, create_engine,
)
from sqlalchemy.orm import mapper, relationship, registry

from models import Visitor

mapper_registry = registry()

visitor = Table(
    "__user__",
    mapper_registry.metadata,
    Column("id", Integer, autoincrement=True),
    Column("email", String, primary_key=True),
    Column("is_admin", Boolean),
    Column("created_at", DateTime, nullable=True, server_default=func.now())
)


def start_mappers():
    visitor_mapper = mapper_registry.map_imperatively(Visitor, visitor)
    engine = create_engine(f"postgresql+psycopg2://postgres:pgpwd4habr@localhost:5432/postgres")
    mapper_registry.metadata.create_all(engine)
