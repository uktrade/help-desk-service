SHELL := /bin/bash
APPLICATION_NAME="help-desk-service"

# Colour coding for output
COLOUR_NONE=\033[0m
COLOUR_GREEN=\033[32;01m
COLOUR_YELLOW=\033[33;01m
COLOUR_RED='\033[0;31m'

.PHONY: help test
help:
	@echo -e "$(COLOUR_GREEN)|--- $(APPLICATION_NAME) ---|$(COLOUR_NONE)"
	@echo -e "$(COLOUR_YELLOW)make build$(COLOUR_NONE) : Run docker-compose build"
	@echo -e "$(COLOUR_YELLOW)make up$(COLOUR_NONE) : Run docker-compose up"
	@echo -e "$(COLOUR_YELLOW)make down$(COLOUR_NONE) : Run docker-compose down"
	@echo -e "$(COLOUR_YELLOW)check-fixme$(COLOUR_NONE) : Check for fixme comments"
	@echo -e "$(COLOUR_YELLOW)make migrations$(COLOUR_NONE) : Run Django makemigrations"
	@echo -e "$(COLOUR_YELLOW)make migrate$(COLOUR_NONE) : Run Django migrate"
	@echo -e "$(COLOUR_YELLOW)make createcachetable?$(COLOUR_NONE) : Create the DB table used by the Django cache"
	@echo -e "$(COLOUR_YELLOW)make shell$(COLOUR_NONE) : Run a Django shell"
	@echo -e "$(COLOUR_YELLOW)make flake8$(COLOUR_NONE) : Run flake8 checks"
	@echo -e "$(COLOUR_YELLOW)make black$(COLOUR_NONE) : Run black"
	@echo -e "$(COLOUR_YELLOW)make isort$(COLOUR_NONE) : Run isort"
	@echo -e "$(COLOUR_YELLOW)make bash$(COLOUR_NONE) : Start a bash session on the application container"
	@echo -e "$(COLOUR_YELLOW)make all-requirements$(COLOUR_NONE) : Generate requirements files"
	@echo -e "$(COLOUR_YELLOW)make pytest$(COLOUR_NONE) : Run pytest"

build:
	docker-compose build

up:
	docker-compose up

down:
	docker-compose down

check-fixme:
	! git --no-pager grep -rni fixme -- ':!./makefile' ':!./.circleci/config.yml'

first-use:
	docker-compose down
	docker-compose up -d db
	docker-compose run --rm help-desk-service python manage.py migrate
	docker-compose up

migrations:
	docker-compose run --rm help-desk-service python manage.py makemigrations

migrate:
	docker-compose run --rm help-desk-service python manage.py migrate

checkmigrations:
	docker-compose run --rm --no-deps help-desk-service python manage.py makemigrations --check

shell:
	docker-compose run --rm help-desk-service python manage.py shell

flake8:
	docker-compose run --rm help-desk-service flake8 $(file)

black:
	docker-compose run --rm help-desk-service black .

isort:
	docker-compose run --rm help-desk-service isort .

mypy:
	docker-compose run --rm help-desk-service mypy .

collectstatic:
	docker-compose run --rm help-desk-service python manage.py collectstatic

bash:
	docker-compose run --rm help-desk-service bash

all-requirements:
	docker-compose run --rm help-desk-service poetry export -f requirements.txt --output requirements.txt --without-hashes --with production --without dev,testing

pytest:
	docker-compose run --rm help-desk-service pytest --cov --cov-report xml --ds=config.settings.test -raP --capture=sys --ignore=node_modules --ignore=front_end --ignore=features --ignore=staticfiles -n 4

superuser:
	docker-compose run --rm help-desk-service python manage.py createsuperuser

createcachetable:
	docker-compose run --rm help-desk-service python manage.py createcachetable
