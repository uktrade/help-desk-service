# Help Desk Service

A service for interacting with help desks such as Zendesk and Halo ITSM.

The service provides a subset of a Zendesk-compatible API that should be used for ticket management and creation.

## Initial setup

- Set up pre-commit as per https://github.com/uktrade/pii-secret-check-hooks
- Copy the example env file `cp .env.example .env`
- Build local docker instance:
    - `make build`
    - `make first-use` 

The service will be available at: `http://localhost:8000/`

## Usage

- Start the local docker instance: `make up`, or `make up-detached` to start in detached mode

## Update requirements files

`make all-requirements`

## Initialise the Django cache

`make createcachetable`

## Project documentation

- [Environment Variables](/docs/environment-variables.md)
- [Connecting the project to Zendesk](/docs/zendesk.md)
- [Defining the mapping from Zendesk custom fields to Halo](/docs/zendesk-to-halo-mapping.md)

## Project structure

- `config` - Django settings and top-level project config
- `halo` -  Halo API client
- `healthcheck` -  Service health check for Pingdom
- `help_desk_api` - mapping of Zendesk API to Halo API
- `zendesk_api_proxy` - Django middleware for dispatching incoming requests to Zendesk and/or Halo (according to configuration of `HelpDeskCreds`)

## AWS components for email handling

- `email_router` - Code for Lambda function to post received emails as tickets
  - `ses_email_receiving` - Lambda function code
  - `utils/build_layer.py` - Utility to package a Lambda layer based on `lambda_layer_requirements.txt`

## Will like dandelions