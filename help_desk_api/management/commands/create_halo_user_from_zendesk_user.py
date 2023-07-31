#!/usr/bin/env python3

# Import the Zenpy Class
import requests
import pandas as pd
import json
from pprint import pprint
import time
import sys

import json
import pathlib

from django.conf import settings
from django.core.management import BaseCommand
from halo.halo_api_client import HaloAPIClient
from halo.halo_manager import HaloManager

from help_desk_api.models import HelpDeskCreds

import sys


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
        url = "https://uktrade.zendesk.com/" + options['url']
        
        # Get credentials for halo client and create one
        credentials = HelpDeskCreds.objects.get(zendesk_email=options["credentials"])
        halo_client = HaloManager(
            credentials.halo_client_id, credentials.halo_client_secret
        )

        # Initialise Zendesk for specific url and credentials
        zendesk_init = ZenDeskInit(url, zendesk_email)
        # Get Zendesk users to be mapped to halo
        user_data = zendesk_init.get_users(url)
        pprint(user_data)
        print(len(user_data))
        
        response = halo_client.get_users()

        id = 0
        halo_users_from_zen = {}
        zen_user_ids = []
        for i in range(len(response['users'])):
            if response['users'][i].get('other5'):
                id = response['users'][i]['id']
                other5 = response['users'][i]['other5']
                halo_users_from_zen[id] = other5
                zen_user_ids.append(int(other5))

        #print(zen_user_ids)

        cnt = 0
        for i in range(len(user_data)):
            cnt += 1
            if user_data[i]['id'] in zen_user_ids:
                print("User already exists with id=", user_data[i]['id'])
            else:
                if cnt < 4:
                    print("Creating a halo user", user_data[i]['id'])
                    print(user_data[i])
                    response = halo_client.create_user(
                        user_data[i]
                    )


class ZenDeskInit(object):
    def __init__(self, zenUrl = None, email = None):
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
        return self._users.get_users(url)


class ZenUsersApi(object):
    def __init__(self, url, session):
        self.session = session
        self.url = url

    def get_users(self, url):
        cols = ['id','name','email']
        extra_col = 'site_id'
        extra_col_val = 18
        no_of_pages = 1

        df_users_all = pd.DataFrame()

        counter = 0
        while url:
            response = self.session.get(url)
            # 429 indicates too many requests
            # Retry-after tells us how long to wait before making another request
            if response.status_code == 429:
                print('Rate limited! Please wait.')
                time.sleep(int(response.headers['retry-after']))
                continue
            if response.status_code !=200:
                print('Status:', response.status_code)
                sys.exit()   
            users = response.json()
            df_users = pd.json_normalize(users["users"])

            # Since df_users[col] is a view we need a copy to avoid pandas warning
            selected_user_fields = df_users[cols].copy()
            if extra_col:
                selected_user_fields[extra_col] = extra_col_val

            # Start accumulating dataframes as we extract more users
            df_users_all = pd.concat([df_users_all, selected_user_fields], ignore_index = True)

            # Counter is used to control how many pages to get at each run
            counter += 1
            url = users['next_page']
            if counter > no_of_pages:
                url is None
                users_json = df_users_all.to_json(orient='records')
                # Parse JSON string and convert into a Dict
                parsed = json.loads(users_json)
                break

        return parsed