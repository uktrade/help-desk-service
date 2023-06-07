import datetime
from enum import Enum
from typing import List, Optional

from pydantic.dataclasses import dataclass


class Priority(Enum):
    URGENT = "Critical"
    HIGH = "High"
    NORMAL = "Medium"
    LOW = "Low"


class TicketType(Enum):
    QUESTION = "question"
    INCIDENT = "incident"
    PROBLEM = "problem"
    TASK = "task"


class Status(Enum):
    CLOSED = "closed"
    NEW = "new"
    PENDING = "pending"
    OPEN = "open"


@dataclass
class ZendeskGroup:
    name: str
    created_at: Optional[datetime.datetime] = None
    deleted: Optional[bool] = None
    id: Optional[int] = None
    updated_at: Optional[datetime.datetime] = None
    url: Optional[str] = None


@dataclass
class ZendeskUser:
    id: Optional[int] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    site_id: Optional[int] = None
    groups: Optional[List[ZendeskGroup]] = None


@dataclass
class ZendeskComment:
    id: int
    note: Optional[str] = None
    who: Optional[str] = None


@dataclass
class ZendeskCustomField:
    id: int
    value: str


@dataclass
class ZendeskTag:
    id: int
    text: str


@dataclass
class ZendeskAttachment:
    id: int
    filename: str
    isimage: bool


@dataclass
class ZendeskTicket:
    summary: str
    id: Optional[int] = None
    details: Optional[str] = None
    user: Optional[ZendeskUser] = None
    group_id: Optional[int] = None
    external_id: Optional[int] = None
    assignee_id: Optional[int] = None
    comment: Optional[List[ZendeskComment]] = None
    tags: Optional[List[ZendeskTag]] = None
    custom_fields: Optional[List[ZendeskCustomField]] = None
    recipient_email: Optional[str] = None
    responder: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    due_at: Optional[datetime.datetime] = None
    status: Optional[Status] = None
    priority_type: Optional[Priority] = None
    ticket_type: Optional[TicketType] = None
    attachments: Optional[List[ZendeskAttachment]] = None


class ZendeskException(Exception):
    pass


class ZendeskTicketNotFoundException(Exception):
    pass
