# help-desk-service

A service for interacting with help desks such as Zendesk and Halo ITSM.

## Setup

- Set up pre-commit as per https://github.com/uktrade/pii-secret-check-hooks
- Copy the example env file `cp .env.example .env`
- Build local docker instance:
    - `make build`
    - `make migrate` or `make first-use` 
- Start the local docker instance `make up`
- Open a browser at `http://localhost:8000/`

## Update requirements files

`make all-requirements`

## Project documentation

- [Index](/docs/index.md)
    - [Environment Variables](/docs/environment-variables.md)

## Project structure

- `config/` - Django settings and top-level project config
- `help_desk_api/` - Common code and integrations with external systems
