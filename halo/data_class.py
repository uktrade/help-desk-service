import datetime

# from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional


class Priority(Enum):
    URGENT = "urgent"
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


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
class HelpDeskGroup:
    name: str
    created_at: Optional[datetime.datetime] = None
    deleted: Optional[bool] = None
    id: Optional[int] = None
    updated_at: Optional[datetime.datetime] = None
    url: Optional[str] = None


@dataclass
class HelpDeskUser:
    id: Optional[int] = None
    full_name: Optional[str] = None
    email: Optional[str] = None
    site_id: Optional[int] = None
    groups: Optional[List[HelpDeskGroup]] = None


@dataclass
class HelpDeskComment:
    body: str
    author_id: Optional[int] = None
    public: bool = True


@dataclass
class HelpDeskCustomField:
    id: int
    value: str


@dataclass
class ZendeskTicket:
    subject: str
    id: Optional[int] = None
    description: Optional[str] = None
    user: Optional[HelpDeskUser] = None
    group_id: Optional[int] = None
    external_id: Optional[int] = None
    assignee_id: Optional[int] = None
    comment: Optional[HelpDeskComment] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[HelpDeskCustomField]] = None
    recipient_email: Optional[str] = None
    responder: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    due_at: Optional[datetime.datetime] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    ticket_type: Optional[TicketType] = None


class HelpDeskException(Exception):
    pass


class HelpDeskTicketNotFoundException(Exception):
    pass
