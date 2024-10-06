from dataclasses import dataclass
from datetime import datetime, datetime as dt
from enum import StrEnum
from typing import Optional, List

import emoji


class Resource:
    resource_id: int
    name: str
    category_name: str
    old_records: 'List[OldRecord]'
    queue_records: 'List[Record]'
    future_records: 'List[Record]'
    take_record: 'Optional[Record]'

    def __init__(
            self,
            resource_id: int,
            name: str,
            category: "Category",
            external_id: Optional[str] = None,
            comment: Optional[str] = None,
            address: Optional[str] = None,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,
            records: "List[Record]" = []
    ):
        self.resource_id = resource_id
        self.name = name
        self.external_id = external_id
        self.comment = comment
        self.address = address
        self.created_at = created_at
        self.updated_at = updated_at
        self.records = records
        self.category = category

    def __eq__(self, other):
        if not isinstance(other, Resource):
            return False
        return other.resource_id == self.resource_id

    def __repr__(self):
        return f"<Resource(" \
               f"resource_id={self.resource_id}, " \
               f"name={self.name}, " \
               f"category={self.category}, " \
               f"external_id={self.external_id or 'None'}" \
               f")>"


class Visitor:
    visitor_id: int
    records: "List[Record]"
    old_records: 'List[OldRecord]'
    future_records: 'List[Record]'
    take_records: 'List[Record]'
    queue_records: 'List[Record]'

    def __init__(
            self,
            email: str,
            is_admin: bool = False,
            external_id: Optional[int] = None,
            chat_id: Optional[int] = None,
            full_name: Optional[str] = None,
            username: Optional[str] = None,
            comment: Optional[str] = None,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,
    ):
        self.email = email
        self.is_admin = is_admin
        self.external_id = external_id
        self.chat_id = chat_id
        self.full_name = full_name
        self.username = username
        self.comment = comment
        self.created_at = created_at
        self.updated_at = updated_at

    def __eq__(self, other):
        if not isinstance(other, Visitor):
            return False
        return other.email == self.email

    def __repr__(self):
        return f"<Visitor(" \
               f"visitor_id={self.visitor_id}, " \
               f"email={self.email}, " \
               f"is_admin={self.is_admin}, " \
               f"external_id={self.external_id or 'None'}" \
               f")>"


class OldRecord:
    record_id: int
    email: str
    resource_name: str
    take_date: Optional[datetime]
    return_date: Optional[datetime]
    enqueue_date: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]
    resource: Optional[Resource]
    visitor: Optional[Visitor]

    def __init__(
            self,
            record_id: int,
            email: str,
            resource_name: str,
            take_date: Optional[datetime] = None,
            return_date: Optional[datetime] = None,
            enqueue_date: Optional[datetime] = None,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,

    ):
        self.record_id = record_id
        self.email = email
        self.resource_name = resource_name
        self.take_date = take_date
        self.return_date = return_date
        self.enqueue_date = enqueue_date
        self.created_at = created_at
        self.updated_at = updated_at

    def __gt__(self, other: 'OldRecord | Record'):
        if self.enqueue_date is None:
            return False
        if other.enqueue_date is None:
            return True
        return self.enqueue_date > other.enqueue_date

    def __eq__(self, other: 'OldRecord | Record') -> bool:
        if not isinstance(other, OldRecord) and not isinstance(other, Record):
            return False
        return other.record_id == self.record_id

    def __repr__(self) -> str:
        return f"<OldRecord(" \
               f"record_id={self.record_id}, " \
               f"email={self.email}, " \
               f"resource_name={self.resource_name}, " \
               f")>"


class Record:
    record_id: int
    resource: Optional[Resource]
    visitor: Optional[Visitor]
    email: str
    resource_name: str
    take_date: Optional[datetime]
    return_date: Optional[datetime]
    enqueue_date: Optional[datetime]
    created_at: Optional[datetime]
    updated_at: Optional[datetime]

    def __init__(
            self,
            email: str,
            resource_name: str,
            take_date: Optional[datetime] = None,
            return_date: Optional[datetime] = None,
            enqueue_date: Optional[datetime] = None,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None,

    ):
        self.email = email
        self.resource_name = resource_name
        self.take_date = take_date
        self.return_date = return_date
        self.enqueue_date = enqueue_date
        self.created_at = created_at
        self.updated_at = updated_at

    def __gt__(self, other):
        if self.take_date is None:
            return False
        if other.take_date is None:
            return True
        return self.take_date > other.take_date

    def __eq__(self, other):
        if not isinstance(other, Record):
            return False
        return other.record_id == self.record_id

    def __repr__(self):
        return f"<Record(" \
               f"record_id={self.record_id}, " \
               f"email={self.email}, " \
               f"resource_name={self.resource_name}, " \
               f")>"


class Category:
    def __init__(
            self,
            name: str,
            created_at: Optional[datetime] = None,
            updated_at: Optional[datetime] = None
    ):
        self.name = name
        self.created_at = created_at
        self.updated_at = updated_at
        self.resources: 'List[Resource]' = []

    def __eq__(self, other):
        if not isinstance(other, Category):
            return False
        return other.name == self.name

    def __repr__(self):
        return f"<Category(name={self.name})>"


class Status(StrEnum):
    Yours = emoji.emojize(":smiling_face_with_sunglasses:")
    Others = emoji.emojize(":stop_sign:")
    NoOne = emoji.emojize(":green_circle:")
    WillBeTaken = emoji.emojize(":yellow_circle:")


@dataclass
class StageInfo:
    resource_id: int
    name: str
    current_take_date: Optional[dt]
    current_return_date: Optional[dt]
    status: Status
    first_booked_day_in_future: Optional[dt] = None
    last_booked_day_in_row: Optional[dt] = None

    def __gt__(self, other: 'StageInfo'):
        return self.name > other.name

    def __eq__(self, other: 'StageInfo') -> bool:
        if not isinstance(other, StageInfo):
            return False
        return other.resource_id == self.resource_id
