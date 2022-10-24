# Connecting the project to Zendesk

- Set the relevant environment variables in the .env file:
    - `HELP_DESK_INTERFACE=help_desk_client.zendesk_manager.ZendeskManager`
    - `HELP_DESK_CREDS='email=[Zendesk user email address],token=[Zendesk token],subdomain=[Zendesk site subdomain]'` 
- If you have not done so already, create a Django user
    - `make superuser`
- Create a token for that user
    - `make shell`
    - run the following in the shell:

```python
from rest_framework.authtoken.models import Token

token = Token.objects.create(user=...)  # Add a reference to the user object here
print(token.key)
```

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
