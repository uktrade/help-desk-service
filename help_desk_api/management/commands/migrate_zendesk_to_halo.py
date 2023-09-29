#!/usr/bin/env python3

import sys
import time

import requests
from django.core.management import BaseCommand

# from halo.halo_api_client import HaloAPIClient
from halo.halo_manager import HaloManager

from help_desk_api.models import HelpDeskCreds

GROUPS_URL = "/api/v2/groups.json?page[size]=100"
TICKETS_URL = "/api/v2/tickets.json?page[size]=100"
USERS_URL = "/api/v2/users.json?page[size]=100"
TICKET_FIELDS_URL = "/api/v2/ticket_fields.json?page[size]=100"


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

        # Get Zendesk Groups to be mapped
        group_data = zendesk_init.get_groups()
        # Map/Copy Zendesk Groups to halo Teams
        group_id_to_team = map_zen_groupid_to_halo_teams(group_data, halo_client)
        group_ids = list(group_id_to_team)

        # Get Zendesk users to be mapped to halo
        users_data = zendesk_init.get_users()
        # Separate end_users, agents and admins
        end_user_data = zendesk_init.get_end_users()
        agent_data = zendesk_init.get_agents()
        admin_data = zendesk_init.get_admins()

        # Map/Copy zendesk end_users to halo
        map_zen_users_to_halo(end_user_data, halo_client)
        # Map/Copy zendesk agents to halo
        map_zen_agents_to_halo(agent_data, halo_client)
        # Need to examine roles for admin user
        map_zen_agents_to_halo(admin_data, halo_client)

        # In Zendesk ticket users are referred as requesters and
        # the requester_id is the user_id
        requester_id = {}
        for i in range(len(users_data)):
            requester_id[users_data[i]["id"]] = {
                "user_email": users_data[i]["email"],
                "user_name": users_data[i]["name"],
                "site_id": users_data[i]["site_id"],
            }

        # Get all requester ids by extracting the keys from dict requester_id
        requester_ids = list(requester_id)

        # Get Zendesk ticket_fields/custom_fields to be mapped to halo
        # Returns a dict with id->custom_field_name
        zendesk_custom_fields = zendesk_init.get_ticket_fields()
        print(zendesk_custom_fields)

        # Get Zendesk tickets to be mapped to halo
        ticket_data = zendesk_init.get_tickets()
        # For each ticket, append dict with user_email, user_name when creating HALO tickets
        for i in range(len(ticket_data)):
            if ticket_data[i]["ticket"]["requester_id"] in requester_ids:
                ticket_data[i]["ticket"].update(
                    requester_id[ticket_data[i]["ticket"]["requester_id"]]
                )
            else:
                ticket_data[i]["ticket"].update(
                    {"user_email": None, "user_name": "Anonymous", "site_id": 18}
                )
            if ticket_data[i]["ticket"]["group_id"] in group_ids:
                ticket_data[i]["ticket"].update(
                    {"team": group_id_to_team[ticket_data[i]["ticket"]["group_id"]]}
                )
        """
        The Zendesk tickets are copied to halo
        If a Zendesk ticket id is in field userdef5 in Halo it is skipped
        """
        id = 0
        halo_tickets_from_zen = {}
        zen_tickets_ids = []
        response_tickets = halo_client.get_tickets()
        for i in range(len(response_tickets["tickets"])):
            if response_tickets["tickets"][i].get("userdef5"):
                id = response_tickets["tickets"][i]["id"]
                userdef5 = response_tickets["tickets"][i]["userdef5"]
                halo_tickets_from_zen[id] = userdef5
                zen_tickets_ids.append(int(userdef5))

        for i in range(len(ticket_data)):
            if ticket_data[i]["ticket"]["id"] in zen_tickets_ids:
                print("Ticket already exists with id=", ticket_data[i]["ticket"]["id"])
            else:
                print(
                    "Creating ticket ",
                    ticket_data[i]["ticket"]["id"],
                    "group_id:",
                    ticket_data[i]["ticket"]["group_id"],
                )
                # halo_client.create_ticket(ticket_data[i])


def map_zen_groupid_to_halo_teams(group_data, halo_client):
    """
    The Zendesk groups are copied to halo teams
    If a Zendesk group/team exists in Halo it is skipped
    """
    response = halo_client.get_teams()
    zen_group_names = []
    for i in range(len(response)):
        if response[i]["name"]:
            team_name = response[i]["name"]
            zen_group_names.append(team_name)

    group_id = {}
    for i in range(len(group_data)):
        group_id[group_data[i].get("id")] = group_data[i].get("name")
        if group_data[i]["name"] in zen_group_names:
            print("Team already exists with name: ", group_data[i]["name"])
        else:
            print("Creating team ", group_data[i]["id"], "name:", group_data[i]["name"])
            # halo_client.create_team(group_data[i])
    return group_id


def map_zen_agents_to_halo(agent_data, halo_client):
    """
    The Zendesk agents are copied to halo
    If a Zendesk agent name exists in Halo it is skipped
    """
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
            print("Creating Agent ", agent_data[i]["id"], "name:", agent_data[i]["name"])
            # halo_client.create_agent(agent_data[i])


def map_zen_users_to_halo(end_user_data, halo_client):
    """
    The Zendesk end_users are copied to halo
    If a Zendesk user id is in field other5 in Halo it is skipped
    """
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
            # halo_client.create_user(end_user_data[i])


class ZenDeskInit(object):
    def __init__(self, zenUrl=None, email=None):
        credentials = HelpDeskCreds.objects.get(zendesk_email=email)

        username = credentials.zendesk_email + "/token"
        password = credentials.zendesk_token
        session = self._start_session(username, password)
        self.groups_url = zenUrl + GROUPS_URL
        self._groups = ZenDeskApi(self.groups_url, session)

        self.tickets_url = zenUrl + TICKETS_URL
        self._tickets = ZenDeskApi(self.tickets_url, session)

        self.users_url = zenUrl + USERS_URL
        self._users = ZenDeskApi(self.users_url, session)

        self.ticket_fields_url = zenUrl + TICKET_FIELDS_URL
        self._ticket_fields = ZenDeskApi(self.ticket_fields_url, session)

    def _start_session(self, username, password):
        session = requests.Session()
        session.auth = (username, password)
        return session

    def get_users(self):
        self.users = self._users.get_all_users(self.users_url)
        return self.users

    def get_end_users(self):
        return self._users.get_end_users(self.users)

    def get_agents(self):
        return self._users.get_agents(self.users)

    def get_admins(self):
        return self._users.get_admins(self.users)

    def get_groups(self):
        return self._groups.get_groups(self.groups_url)

    def get_ticket_fields(self):
        return self._ticket_fields.get_ticket_fields(self.ticket_fields_url)

    def get_tickets(self):
        return self._tickets.get_tickets(self.tickets_url)


class ZenDeskApi(object):
    def __init__(self, url, session):
        self.session = session
        self.url = url

    def get_tickets(self, url):
        no_of_pages = 300

        zendesk_tickets_all = []
        zendesk_tickets = []
        counter = 0
        tickets = {}
        tickets["meta"] = {"has_more": True}

        while tickets["meta"]["has_more"]:
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

            tickets = response.json()
            zendesk_tickets = [
                {
                    "ticket": {
                        "id": ticket["id"],
                        "comment": {"body": "Migration to HALO"},
                        "description": ticket["description"],
                        "subject": ticket["subject"],
                        "group_id": ticket["group_id"],
                        "requester_id": ticket["requester_id"],
                        "tags": ticket["tags"],
                    }
                }
                for ticket in tickets["tickets"]
            ]
            zendesk_tickets_all += zendesk_tickets

            url = tickets["links"]["next"]
            if counter > no_of_pages:
                print("Exiting while loop counter=", counter)
                # exit while loop
                break
        return zendesk_tickets_all

    def get_groups(self, url):
        no_of_pages = 10
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

    def get_all_users(self, url):
        """
        Get all Zendesk users including agents and admins
        """
        no_of_pages = 400

        zendesk_users_all = []
        zendesk_users = []
        counter = 0
        users = {}
        users["meta"] = {"has_more": True}

        while users["meta"]["has_more"]:
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

            users = response.json()
            zendesk_users = [
                {
                    "email": user["email"],
                    "id": user["id"],
                    "name": user["name"],
                    "role": user["role"],
                    "default_group_id": user["default_group_id"],
                    "site_id": 18,
                }
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
            {
                "email": user["email"],
                "id": user["id"],
                "name": user["name"],
                "role": user["role"],
                "site_id": 18,
            }
            for user in users
            if user["role"] == "end-user"
        ]
        return zendesk_end_users

    def get_agents(self, users):
        zendesk_agents = [
            {
                "email": user["email"],
                "id": user["id"],
                "name": user["name"],
                "default_group_id": user["default_group_id"],
            }
            for user in users
            if user["role"] == "agent"
        ]
        return zendesk_agents

    def get_admins(self, users):
        zendesk_admins = [
            {
                "email": user["email"],
                "id": user["id"],
                "name": user["name"],
                "role": user["role"],
                "default_group_id": user["default_group_id"],
                "site_id": 18,
            }
            for user in users
            if user["role"] == "admin"
        ]
        return zendesk_admins

    def get_ticket_fields(self, url):
        no_of_pages = 100

        zendesk_ticket_fields_all = {}
        # zendesk_ticket_fields = []
        counter = 0
        ticket_fields = {}
        ticket_field_id = {}
        ticket_fields["meta"] = {"has_more": True}

        while ticket_fields["meta"]["has_more"]:
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

            ticket_fields = response.json()
            for ticket_field in ticket_fields["ticket_fields"]:
                if ticket_field.get("custom_field_options"):
                    ticket_field_id[ticket_field.get("id")] = ticket_field.get("raw_title")

            zendesk_ticket_fields_all.update(ticket_field_id)

            url = ticket_fields["links"]["next"]
            if counter > no_of_pages:
                # exit while loop
                break

        return zendesk_ticket_fields_all
