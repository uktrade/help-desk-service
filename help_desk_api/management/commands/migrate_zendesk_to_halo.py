#!/usr/bin/env python3

import sys
import time

import requests
from django.core.management import BaseCommand

# from halo.halo_api_client import HaloAPIClient
from halo.halo_manager import HaloManager

from help_desk_api.models import HelpDeskCreds

from pprint import pprint
import sys

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

        # Get Zendesk groups to be mapped to halo
        group_data = zendesk_init.get_groups()
        print("Zendesk groups -----------------------------")
        #pprint(group_data)
        print(len(group_data))
        print("---------group ids---------------------")
        group_id = {}
        for i in range(len(group_data)):
            group_id[group_data[i].get("id")] = group_data[i].get("name")
        
        print(group_id)

        group_ids = list(group_id)
        print(group_ids)
        print(group_id)
        #sys.exit()

        # Get Zendesk ticket_fields to be mapped to halo
        ticket_fields_data = zendesk_init.get_ticket_fields()
        print("Zendesk ticket_fields -----------------------------")
        pprint(ticket_fields_data)
        print(len(ticket_fields_data))
        print("---------ticket_field ids---------------------")
        ticket_field_id = {}
        for i in range(len(ticket_fields_data)):
            ticket_field_id[ticket_fields_data[i].get("id")] = ticket_fields_data[i].get("name")
        
        print(ticket_field_id)

        ticket_field_ids = list(ticket_field_id)
        print(ticket_field_ids)

        #sys.exit()
        # No need for that... Just to check HALO
        halo_users = halo_client.get_users()
        print("uuuuuuuuuuuuu start")
        pprint(halo_users)
        print("uuuuuuuu end")
        print("halo ttttt  start")
        halo_tickets = halo_client.get_tickets()
        pprint(halo_tickets)
        print("halo ttttt end")
        sys.exit()

        # Get Zendesk users to be mapped to halo
        users_data = zendesk_init.get_users()
        # In Zendesk ticket users are referred as requesters and 
        # the requester_id is the user_id
        requester_id = {}
        for i in range(len(users_data)):
            requester_id[users_data[i]['id']] = {'user_email': users_data[i]['email'], 
                                                 'user_name': users_data[i]['name'], 
                                                 'site_id': users_data[i]['site_id']}
        
        # Get all requester ids by extracting the keys from dict requester_id
        requester_ids = list(requester_id)
        print("---------requester ids---------------------")
        print(requester_ids)
        #sys.exit()

        # Get Zendesk tickets to be mapped to halo
        ticket_data = zendesk_init.get_tickets()
        print("TICKET_DATA-------")
        #pprint(ticket_data)
        print("END TICKET_DATA--------")
        # For each ticket, append dict with user_email and user_name to be used when creating HALO tickets
        for i in range(len(ticket_data)):
                if ticket_data[i]['ticket']['requester_id'] in requester_ids:
                    ticket_data[i]['ticket'].update(requester_id[ticket_data[i]['ticket']['requester_id']])
                else:
                    print(ticket_data[i]['ticket']['requester_id'], "not found-----------")
                if ticket_data[i]['ticket']['group_id'] in group_ids:
                    ticket_data[i]['ticket'].update({'team': group_id[ticket_data[i]['ticket']['group_id']]})        
        
        # Temporary for checking - Need to check if tickets already exist/mapped on Halo
        #for i in range(len(ticket_data)):
        for i in range(1):
            print("Creating ticket ", ticket_data[i]['ticket']["id"], "user_name:", 
                  ticket_data[i]['ticket']["user_name"], "user_email", ticket_data[i]['ticket']["user_email"])
            print(ticket_data[i])
            data_sample = {'ticket': {'id': 16675, 'comment': {'body': 'Migration to HALO'}, 'description': 'Name: \nNIKOS BL\n\n', 'subject': 'Name: NB case', 'group_id': 26197425, 'requester_id': 18655244625, 'tags': ['directory'], 'user_email': 'nb@anytechnology.co.uk', 'user_name': 'NIKOS BALTAS', 'site_id': 18, 'team': 'Support Services'}}
            #halo_client.create_ticket(data_sample)   
            #halo_client.create_ticket(ticket_data[i])
        print("DONE ONE TICKET")
        #sys.exit()

        response = halo_client.get_tickets()
        print("HALO tickets START===============---------------------")
        pprint(response)
        print("HALO tickets END=================================")

        sys.exit()

        #TO DO loops below
        zen_ticket_ids = []
        for i in range(len(response["tickets"])):
            if response["tickets"][i]["id"]:
                ticket_id = response["tickets"][i]["id"]
                zen_ticket_ids.append(ticket_id)
        print(zen_ticket_ids)
        #sys.exit()

        for i in range(len(ticket_data)):
            if ticket_data[i]["name"] in zen_ticket_ids:
                print("Ticket already exists in HALO with id: ", ticket_data[i]["name"])
            else:
                print("Creating ticket ", ticket_data[i]["id"], "name:", group_data[i]["name"])
                #halo_client.create_team(ticket_data[i])

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
            print("Creating Agent ", "name:", agent_data[i]["name"])
            #halo_client.create_agent(agent_data[i])

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
            #halo_client.create_user(end_user_data[i])


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
        return self._users.get_all_users(self.users_url)

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

        print("tttttttttttt-start")
        while tickets["meta"]["has_more"]:
            # Counter is used to control how many pages to get at each run
            counter += 1
            #print("COUNTER=", counter)
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
            pprint(tickets)
            zendesk_tickets = [ {"ticket":
                {"id": ticket["id"], "comment": {"body": "Migration to HALO"},
                 "description": ticket["description"],
                 "subject": ticket["subject"], "group_id": ticket["group_id"],
                 "requester_id": ticket["requester_id"], "tags": ticket["tags"],
                 } } for ticket in tickets["tickets"]
            ]
            zendesk_tickets_all += zendesk_tickets

            url = tickets["links"]["next"]
            if counter > no_of_pages:
                print("Exiting while loop counter=", counter)
                # exit while loop
                break
        print("tttttttttttt-end")
        #pprint(zendesk_tickets_all)
        return zendesk_tickets_all

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
    

    def get_all_users(self, url):
        """
        Get all Zendesk users including agents and admins
        """
        no_of_pages = 365

        zendesk_users_all = []
        zendesk_users = []
        counter = 0
        users = {}
        users["meta"] = {"has_more": True}

        while users["meta"]["has_more"]:
            # Counter is used to control how many pages to get at each run
            counter += 1
            print("COUNT USERS=", counter)
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

        zendesk_ticket_fields_all = []
        zendesk_ticket_fields = []
        counter = 0
        ticket_fields = {}
        ticket_fields["meta"] = {"has_more": True}

        while ticket_fields["meta"]["has_more"]:
            # Counter is used to control how many pages to get at each run
            counter += 1
            print("TICKET FIELDS COUNTER=",counter)
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
            pprint(ticket_fields)
            zendesk_ticket_fields = [
                {"id": ticket_field["id"], "title": ticket_field["title"]} for ticket_field in ticket_fields["ticket_fields"]
            ]
            zendesk_ticket_fields_all += zendesk_ticket_fields

            url = ticket_fields["links"]["next"]
            if counter > no_of_pages:
                # exit while loop
                break
        
        print("tftftftftf---------")
        pprint(zendesk_ticket_fields_all)
        return zendesk_ticket_fields_all
    