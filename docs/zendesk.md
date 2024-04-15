# Connecting the project to Zendesk

- If you have not done so already, create a Django user
    - `make superuser`
- In the Django admin, create a `HelpDeskCreds` instance:
    - `zendesk_email`: email address of a Zendesk account with required privileges (usually `administrator`)
    - `zendesk_token`: a valid Zendesk API token
    - `zendesk_subdomain`: the Zendesk subdomain for which these credentials are valid, e.g. `uktrade` for `uktrade.zendesk.com`
    - `help_desk`: direct requests received using these Zendesk credentials to Zendesk, Halo, or both
    - `halo_client_id`: Client ID for Halo API
    - `halo_client_secret`: Secret for Halo API

N.B. The `zendesk_token` value is encrypted on save, and cannot be modified.
To replace it with a new value, it will be necessary to delete the existing `HelpDeskCreds`
and recreate it with the new token.

- On your host machine, create the following env vars:
    - `ZENPY_FORCE_NETLOC=localhost:8000`
    - `ZENPY_FORCE_SCHEME=http`
- Install the zenpy package
- Run the following script on your host to create a ticket using Zenpy:

```python
from zenpy import Zenpy
from zenpy.lib.api_objects import Ticket

credentials = {
    "email" : "supply any value",
    "token" : "Your help desk service token",
    "subdomain": "supply any value"
}

zenpy_client = Zenpy(**credentials)

# Create a new ticket
zenpy_client.tickets.create(
	Ticket(
		subject="Test subject",
		description="Test description",
	)
)
```
