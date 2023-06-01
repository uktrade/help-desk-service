import datetime
import inspect

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
    note: str
    who: Optional[int] = None

    @classmethod
    def from_json(cls, comments):
        comments_list = []
        if "actions" in comments:
            for action in comments["actions"]:
                comment = cls.comments_processing(action)
                if isinstance(comment, ZendeskComment):
                    comments_list.append(cls.comments_processing(action))
        else:
            comments_list.append(cls.comments_processing(comments))
        return comments_list

    @classmethod
    def comments_processing(cls, comments):
        data = {}
        if comments["outcome"] == "comment":
            for k, v in comments.items():
                if k in inspect.signature(cls).parameters:
                    data[k] = v
            return cls(**data)


@dataclass
class ZendeskCustomField:
    id: int
    value: str


@dataclass
class ZendeskTicket:
    summary: str
    id: Optional[int] = None
    details: Optional[str] = None
    user: Optional[ZendeskUser] = None
    group_id: Optional[int] = None
    external_id: Optional[int] = None
    assignee_id: Optional[int] = None
    comment: Optional[ZendeskComment] = None
    tags: Optional[List[str]] = None
    custom_fields: Optional[List[ZendeskCustomField]] = None
    recipient_email: Optional[str] = None
    responder: Optional[str] = None
    created_at: Optional[datetime.datetime] = None
    updated_at: Optional[datetime.datetime] = None
    due_at: Optional[datetime.datetime] = None
    status: Optional[Status] = None
    priority: Optional[Priority] = None
    ticket_type: Optional[TicketType] = None

    @classmethod
    def from_json(cls, ticket_response):
        data = {}
        for k, v in ticket_response.items():
            if k in inspect.signature(cls).parameters:
                if k == "comment":
                    data[k] = ZendeskComment.from_json(v)
                elif k == "priority":
                    data[k] = v["name"].lower()
                else:
                    data[k] = v
        return cls(**data)


class ZendeskException(Exception):
    pass


class ZendeskTicketNotFoundException(Exception):
    pass
