import json
import logging
from dataclasses import dataclass
from typing import List, Optional

import requests
from django.conf import settings


class HaloRecordNotFoundException(Exception):
    pass


class HaloClientNotFoundException(Exception):
    pass


# @dataclass
# class Ticket:
#     id: int
#     summary: str
#     user_id: int
#     status_id: Optional[int]  # todo get status id from halo
#     priority_id: Optional[int]  # todo get priority id from halo
#     emailcclist: Optional[List[str]]
#     details: Optional[str]
#     agent_id: Optional[int]
#     team_id: Optional[int]
#     ticket_tags: Optional[str]
#     third_party_id: Optional[int]  # /PS-IGNORE
#     custom_fields: Optional[List[object]]
#     # comment:
#     tickettype_id: Optional[int]
#     datecreated: Optional[datetime.datetime] = None
#     updated_at: Optional[datetime.datetime] = None

logger = logging.getLogger(__name__)


class HaloAPIClient:
    def __init__(self, client_id, client_secret) -> None:
        self.access_token = self.__authenticate(client_id, client_secret)

    def __authenticate(self, client_id, client_secret):
        data = {
            "grant_type": "client_credentials",
            "client_id": client_id,
            "client_secret": client_secret,
            "scope": "all",
        }
        response = requests.post(
            f"https://{settings.HALO_SUBDOMAIN}.haloitsm.com/auth/token",
            data=data,
            headers={
                "Content-Type": "application/x-www-form-urlencoded",
                "Accept": "application/json",
            },
        )
        if response.status_code != 200:
            logger.error(f"{response.status_code} response from auth endpoint")
            logger.error(response)
            raise HaloClientNotFoundException()

        response_data = response.json()
        return response_data["access_token"]

    def get(self, path, params = {}):
        response = requests.get(
            f"https://{settings.HALO_SUBDOMAIN}.haloitsm.com/api/{path}",
            params=params,
            headers={
                "Authorization": f"Bearer {self.access_token}",
            },
        )
        # TODO error handling Handle 400s & 401 (normally token expired)
        if response.status_code != 200:
            logger.error(f"{response.status_code} response from get endpoint")
            raise HaloRecordNotFoundException()
        return response.json()

    def post(self, path, payload):
        logger.error(f"https://{settings.HALO_SUBDOMAIN}.haloitsm.com/api/{path}")
        logger.error(json.dumps(payload))
        response = requests.post(
            f"https://{settings.HALO_SUBDOMAIN}.haloitsm.com/api/{path}",
            data=json.dumps(payload),
            headers={
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json",
            },
        )
        if response.status_code != 201:
            logger.error(f"{response.status_code} response from get endpoint")
            logger.error(response.json())
            #TODO update handling
            raise HaloClientNotFoundException()
        return response.json()
