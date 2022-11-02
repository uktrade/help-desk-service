import json
import logging

import requests
from django.conf import settings
from django.core.cache import cache


class HaloRecordNotFoundException(Exception):
    pass


class HaloClientNotFoundException(Exception):
    pass


logger = logging.getLogger(__name__)


class HaloAPIClient:
    def __init__(self, client_id, client_secret) -> None:
        self.access_token = self.__authenticate(client_id, client_secret)

    def __authenticate(self, client_id, client_secret):
        # print("client_id=", client_id)
        # print("client_secret=", client_secret)

        if cache.get("access_token", None):
            return cache.get("access_token")

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
        cache.set("access_token", response_data["access_token"], 3000)
        return response_data["access_token"]

    def get(self, path, params={}):
        logger.error(f"https://{settings.HALO_SUBDOMAIN}.haloitsm.com/api/{path}")
        response = requests.get(
            f"https://{settings.HALO_SUBDOMAIN}.haloitsm.com/api/{path}",
            params=params,
            headers={
                "Authorization": f"Bearer {self.access_token}",
            },
        )
        # TODO error handling
        if response.status_code != 200:
            logger.error(f"{response.status_code} response from get endpoint")
            raise HaloClientNotFoundException()
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
        logger.error(response)
        if response.status_code != 201:
            logger.error(f"{response.status_code} response from get endpoint")
            logger.error(response.json())
            raise HaloClientNotFoundException()
        return response.json()
