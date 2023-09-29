#!/usr/bin/env python3

import sys
import time

import requests
from django.core.management import BaseCommand

# from halo.halo_api_client import HaloAPIClient
from halo.halo_manager import HaloManager

from help_desk_api.models import HelpDeskCreds


class Command(BaseCommand):
    help = "Create Teams on Halo from Zendesk Groups"  # /PS-IGNORE

    def __init__(self, stdout=None, stderr=None, **kwargs):
        super().__init__(stdout, stderr, **kwargs)

    def add_arguments(self, parser):
        parser.add_argument(
            "-c",
            "--credentials",
            type=str,
            help="Email address linked to Halo credentials",
            required=True,
        )
        parser.add_argument(
            "-u",
            "--url",
            type=str,
            help="url of zedesk endpoint for groups/tickets etc. ",
            required=True,
        )

    def handle(self, *args, **options):
        zendesk_email = options["credentials"]
        url = "https://uktrade.zendesk.com"

        # Get credentials for halo client and create one
        credentials = HelpDeskCreds.objects.get(zendesk_email=options["credentials"])
        halo_client = HaloManager(credentials.halo_client_id, credentials.halo_client_secret)

        # Initialise Zendesk for specific url and credentials
        zendesk_init = ZenDeskInit(url, zendesk_email)
        # Get Zendesk users to be mapped to halo
        group_data = zendesk_init.get_groups()

        response = halo_client.get_teams()

        zen_group_names = []
        for i in range(len(response)):
            if response[i]["name"]:
                team_name = response[i]["name"]
                zen_group_names.append(team_name)

        for i in range(len(group_data)):
            if group_data[i]["name"] in zen_group_names:
                print("Team already exists with name: ", group_data[i]["name"])
            else:
                print("Creating team ", group_data[i]["id"], "name:", group_data[i]["name"])
                halo_client.create_team(group_data[i])


class ZenDeskInit(object):
    def __init__(self, zenUrl=None, email=None):
        credentials = HelpDeskCreds.objects.get(zendesk_email=email)

        username = credentials.zendesk_email + "/token"
        password = credentials.zendesk_token
        session = self._start_session(username, password)
        self.groups_url = zenUrl + "/api/v2/groups.json?page[size]=100"
        self._api = ZenDeskApi(self.groups_url, session)

    def _start_session(self, username, password):
        session = requests.Session()
        session.auth = (username, password)
        return session

    def get_groups(self):
        return self._api.get_groups(self.groups_url)


class ZenDeskApi(object):
    def __init__(self, url, session):
        self.session = session
        self.url = url

    def get_groups(self, url):
        no_of_pages = 5

        zendesk_groups_all = []
        zendesk_groups = []
        counter = 0
        groups = {}
        groups["meta"] = {"has_more": True}

        while groups["meta"]["has_more"]:
            # Counter is used to control how many pages to get at each run
            counter += 1
            response = self.session.get(url)
            # 429 indicates too many requests
            # Retry-after tells us how long to wait before making another request
            if response.status_code == 429:
                print("Rate limited! Please wait.")
                time.sleep(int(response.headers["retry-after"]))
                continue
            if response.status_code != 200:
                print("Status:", response.status_code)
                sys.exit()

            groups = response.json()
            zendesk_groups = [
                {"id": group["id"], "name": group["name"]} for group in groups["groups"]
            ]
            zendesk_groups_all += zendesk_groups

            url = groups["links"]["next"]
            if counter > no_of_pages:
                # exit while loop
                break

        return zendesk_groups_all
