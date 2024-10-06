from sqlalchemy import (
    Table,
    Column,
    Integer,
    String,
    Boolean,
    DateTime,
    MetaData, Identity, ForeignKey, text,
)
from sqlalchemy.orm import registry, relationship

from domain.models import Visitor, Resource, Record, Category, OldRecord
from helpers.helpers import get_time_now


def get_resource_table(metadata: MetaData):
    return Table(
        "resource",
        metadata,
        Column("resource_id", Integer, Identity(start=1, increment=1), nullable=False),
        Column("name", String, nullable=False, primary_key=True),
        Column("category_name", ForeignKey("category.name", onupdate="cascade", ondelete="cascade"), nullable=False),
        Column("external_id", String),
        Column("comment", String),
        Column("address", String),
        Column("created_at", DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")),
        Column("updated_at", DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())"),
               onupdate=text("TIMEZONE('utc', now())"))
    )


def get_visitor_table(metadata: MetaData):
    return Table(
        "visitor",
        metadata,
        Column("visitor_id", Integer, Identity(start=1, increment=1), nullable=False),
        Column("email", String, primary_key=True, nullable=False),
        Column("is_admin", Boolean, default=False),
        Column("external_id", Integer, unique=True),
        Column("chat_id", Integer, unique=True),
        Column("full_name", String),
        Column("username", String),
        Column("comment", String),
        Column("created_at", DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")),
        Column("updated_at", DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())"),
               onupdate=text("TIMEZONE('utc', now())"))
    )


def get_record_table(metadata: MetaData):
    return Table(
        "record",
        metadata,
        Column("record_id", Integer, Identity(start=1, increment=1), primary_key=True, nullable=False),
        Column("resource_name", ForeignKey("resource.name", onupdate="cascade", ondelete="cascade"),
               nullable=False),
        Column("email", ForeignKey("visitor.email", onupdate="cascade", ondelete="cascade"), nullable=False),
        Column("take_date", DateTime(timezone=True)),
        Column("return_date", DateTime(timezone=True)),
        Column("enqueue_date", DateTime(timezone=True)),
        Column("created_at", DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")),
        Column("updated_at", DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())"),
               onupdate=text("TIMEZONE('utc', now())")),
    )


def get_old_record_table(metadata: MetaData):
    return Table(
        "old_record",
        metadata,
        Column("record_id", Integer, primary_key=True, nullable=False),
        Column("resource_name", ForeignKey("resource.name", onupdate="cascade", ondelete="cascade"),
               nullable=False),
        Column("email", ForeignKey("visitor.email", onupdate="cascade", ondelete="cascade"), nullable=False),
        Column("take_date", DateTime(timezone=True)),
        Column("return_date", DateTime(timezone=True)),
        Column("enqueue_date", DateTime(timezone=True)),
        Column("created_at", DateTime(timezone=True)),
        Column("updated_at", DateTime(timezone=True)),
    )


def get_category_table(metadata: MetaData):
    return Table(
        "category",
        metadata,
        Column("name", String, primary_key=True, nullable=False),
        Column("created_at", DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())")),
        Column("updated_at", DateTime(timezone=True), server_default=text("TIMEZONE('utc', now())"),
               onupdate=text("TIMEZONE('utc', now())"))
    )


def get_empty_metadata() -> MetaData:
    return MetaData(naming_convention={
        "ix": "%(column_0_label)s_idx",
        "uq": "%(table_name)s_%(column_0_name)s_key",
        "ck": "%(table_name)s_%(constraint_name)s_check",
        "fk": "%(table_name)s_%(column_0_name)s_%(referred_table_name)s_fkey",
        "pk": "%(table_name)s_pkey"
    })


def get_mapper_registry():
    mapper_registry = registry(metadata=get_empty_metadata())
    category = get_category_table(mapper_registry.metadata)
    category_mapper = mapper_registry.map_imperatively(
        Category,
        category,
        properties={
            "resources": relationship("Resource", back_populates="category", lazy="selectin")
        }
    )
    visitor = get_visitor_table(mapper_registry.metadata)
    visitor_mapper = mapper_registry.map_imperatively(
        Visitor,
        visitor,
        properties={
            "records": relationship("Record", back_populates="visitor", lazy="selectin"),
            "old_records": relationship("OldRecord", back_populates="visitor", lazy="selectin"),
            "future_records": relationship(
                "Record",
                back_populates="visitor",
                lazy="selectin",
                primaryjoin="and_(Visitor.email == Record.email, Record.take_date > func.now())",
                order_by="Record.take_date.asc()",
            ),
            "take_records": relationship(
                "Record",
                back_populates="visitor",
                lazy="selectin",
                primaryjoin="and_(Visitor.email == Record.email, Record.take_date <= func.now())",
                order_by="Record.take_date.asc()",
            ),
            "queue_records": relationship(
                "Record",
                back_populates="visitor",
                lazy="selectin",
                primaryjoin="and_(Visitor.email == Record.email, Record.enqueue_date != None)",
                order_by="Record.enqueue_date.asc()",
            ),
        }
    )
    resource = get_resource_table(mapper_registry.metadata)
    time = get_time_now()
    resource_mapper = mapper_registry.map_imperatively(
        Resource,
        resource,
        properties={
            "category": relationship("Category", back_populates="resources", lazy="joined", uselist=False),
            "old_records": relationship("OldRecord", back_populates="resource", lazy="selectin"),
            "records": relationship("Record", back_populates="resource", lazy="selectin"),
            "queue_records": relationship(
                "Record",
                back_populates="resource",
                lazy="selectin",
                primaryjoin="and_(Resource.name == Record.resource_name, Record.enqueue_date != None)",
                order_by="Record.enqueue_date.asc()",
            ),
            "future_records": relationship(
                "Record",
                back_populates="resource",
                lazy="selectin",
                primaryjoin="and_(Resource.name == Record.resource_name, Record.take_date > func.now())",
                order_by="Record.take_date.asc()",
            ),
            "take_record": relationship(
                "Record",
                back_populates="resource",
                lazy="selectin",
                primaryjoin="and_(Resource.name == Record.resource_name, Record.take_date <= func.now())",
                uselist=False
            ),
        }
    )
    record = get_record_table(mapper_registry.metadata)
    record_mapper = mapper_registry.map_imperatively(
        Record,
        record,
        properties={
            "resource": relationship("Resource", back_populates="records", lazy="joined", uselist=False,
                                     single_parent=True),
            "visitor": relationship("Visitor", back_populates="records", lazy="joined", uselist=False,
                                    single_parent=True),
        }
    )
    old_record = get_old_record_table(mapper_registry.metadata)
    old_record_mapper = mapper_registry.map_imperatively(
        OldRecord,
        old_record,
        properties={
            "resource": relationship("Resource", back_populates="old_records", lazy="joined", uselist=False,
                                     single_parent=True),
            "visitor": relationship("Visitor", back_populates="old_records", lazy="joined", uselist=False,
                                    single_parent=True),
        }
    )
    return mapper_registry
