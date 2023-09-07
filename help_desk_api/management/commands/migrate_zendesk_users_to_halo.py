#!/usr/bin/env python3

import sys
import time
import requests
from django.core.management import BaseCommand

from halo.halo_manager import HaloManager
from help_desk_api.models import HelpDeskCreds


class Command(BaseCommand):
    help = "Create user on Halo from Zendesk records"  # /PS-IGNORE

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
            help="url of zedesk endpoint for users/tickets etc. ",
            required=True,
        )

    def handle(self, *args, **options):
        zendesk_email = options["credentials"]
        url = "https://uktrade.zendesk.com/api/v2/users.json?page[size]=100"
        
        # Get credentials for halo client and create one
        credentials = HelpDeskCreds.objects.get(zendesk_email=options["credentials"])
        halo_client = HaloManager(credentials.halo_client_id, credentials.halo_client_secret)

        # Initialise Zendesk for specific url and credentials
        zendesk_init = ZenDeskInit(url, zendesk_email)
        # Get Zendesk users to be mapped to halo
        zendesk_init.get_users(url)

        end_user_data = zendesk_init.get_end_users() 
        agent_data = zendesk_init.get_agents()
        admin_data = zendesk_init.get_admins()

        # Map/Copy zendesk end_users to halo
        map_zen_users_to_halo(end_user_data, halo_client)
        # Map/Copy zendesk agents to halo
        map_zen_agents_to_halo(agent_data, halo_client)

        
def map_zen_agents_to_halo(agent_data, halo_client):
    '''
    The Zendesk agents are copied to halo
    If a Zendesk agent name exists in Halo it is skipped
    '''
    response = halo_client.get_agents()
    zen_agent_names = []
        
    for i in range(len(response)):
        if response[i].get("name"):
            name = response[i]["name"]
            zen_agent_names.append(name)
        
    for i in range(len(agent_data)):
        if agent_data[i]["name"] in zen_agent_names:
            print("Agent already exists with name=", agent_data[i]["name"])
        else:
            print("Creating Agent ", "name:", agent_data[i]["name"])
            #response = halo_client.create_agent(agent_data[i])


def map_zen_users_to_halo(end_user_data, halo_client):
    '''
    The Zendesk end_users are copied to halo
    If a Zendesk user id is in field other5 in Halo it is skipped 
    '''
    id = 0
    halo_users_from_zen = {}
    zen_user_ids = []
    response_users = halo_client.get_users()
    for i in range(len(response_users["users"])):
        if response_users["users"][i].get("other5"):
            id = response_users["users"][i]["id"]
            other5 = response_users["users"][i]["other5"]
            halo_users_from_zen[id] = other5
            zen_user_ids.append(int(other5))

    for i in range(len(end_user_data)):
        if end_user_data[i]["id"] in zen_user_ids:
            print("User already exists with id=", end_user_data[i]["id"])
        else:
            print("Creating user ", end_user_data[i]["id"], "name:", end_user_data[i]["name"])
            #response = halo_client.create_user(user_data[i])

class ZenDeskInit(object):
    def __init__(self, zenUrl=None, email=None):
        credentials = HelpDeskCreds.objects.get(zendesk_email=email)

        username = credentials.zendesk_email + "/token"
        password = credentials.zendesk_token
        session = self._start_session(username, password)
        self._users = ZenUsersApi(zenUrl, session)

    def _start_session(self, username, password):
        session = requests.Session()
        session.auth = (username, password)
        return session

    def get_users(self, url):
        self.users = self._users.get_all_users(url)
        return self.users
    
    def get_end_users(self):
        return self._users.get_end_users(self.users)

    def get_agents(self):
        return self._users.get_agents(self.users)

    def get_admins(self):
        return self._users.get_admins(self.users)

class ZenUsersApi(object):
    def __init__(self, url, session):
        self.session = session
        self.url = url

    def get_all_users(self, url):
        '''
        Get all Zendesk users including agents and admins
        '''
        no_of_pages = 3

        zendesk_users_all = []
        zendesk_users = []
        counter = 0
        users = {}
        users["meta"] = {"has_more": True}

        while users["meta"]["has_more"]:
            # Counter is used to control how many pages to get at each run
            counter += 1
            print("COUNT=", counter)
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

            users = response.json()
            zendesk_users = [
                {"email": user["email"], "id": user["id"], "name": user["name"], 
                 "role": user["role"], "default_group_id": user["default_group_id"], "site_id": 18}
                for user in users["users"]
            ]
            zendesk_users_all += zendesk_users

            url = users["links"]["next"]
            if counter > no_of_pages:
                # exit while loop
                break

        return zendesk_users_all
    
    def get_end_users(self, users):
        zendesk_end_users = [
            {"email": user["email"], "id": user["id"], "name": user["name"],
               "role": user["role"], "site_id": 18}
              for user in users if user["role"] == 'end-user'
        ]
        return zendesk_end_users

    def get_agents(self, users):
        zendesk_agents = [
            {"email": user["email"], "id": user["id"], "name": user["name"],
               "default_group_id": user["default_group_id"]}
              for user in users if user["role"] == 'agent'
        ]
        return zendesk_agents

    def get_admins(self, users):
        zendesk_admins = [
            {"email": user["email"], "id": user["id"], "name": user["name"],
               "role": user["role"], "default_group_id": user["default_group_id"], "site_id": 18}
              for user in users if user["role"] == 'admin'
        ]
        return zendesk_admins

