# Help Desk Service

A service for interacting with help desks such as Zendesk and Halo ITSM.

The service provides an API that should be used for ticket management and creation.

## Setup

- Set up pre-commit as per https://github.com/uktrade/pii-secret-check-hooks
- Copy the example env file `cp .env.example .env`
- Build local docker instance:
    - `make build`
    - `make migrate` or `make first-use` 
- Start the local docker instance: `make up` or `make up-detached` to start in detached mode
- The service will be available at: `http://localhost:8000/`

## Update requirements files

`make all-requirements`

## Initialise the Django cache

`make createcachetable`

## Project documentation

- [Environment Variables](/docs/environment-variables.md)
- [Connecting the project to Zendesk](/docs/zendesk.md)

## Project structure

- `config/` - Django settings and top-level project config
- `help_desk_api/` - API for help desk ticket management
