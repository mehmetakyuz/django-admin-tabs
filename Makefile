SHELL                := /bin/bash -o pipefail
OS                   := $(shell uname -s)
pip                  := venv/bin/pip
python               := venv/bin/python
command          	 := docker exec -it django-admin-tabs

define \n


endef

.PHONY: fmt clean cleanpy


venv: # Create venv if it doesn't exist.
	test -d venv || python3.8 -m venv venv
	source venv/bin/activate
	$(pip) install --upgrade pip

venv/install: venv # Install env with all required packages.
	$(pip) install --upgrade pip
	poetry install

dev: # Start development containers
	docker-compose up --build --remove-orphans

test:
	$(command) python manage.py test django_admin_tabs

coverage: venv # Run the tests and generate a coverage report.
	 $(coverage) run -m py.test
	$(coverage) html
	open ./htmlcov/index.html 2>&1 >/dev/null

cleanpy: # Remove .pyc / __pycache__.
	find . -name '*.pyc' -delete
	find . -name '__pycache__' -delete

clean: cleanpy # Remove .pyc / __pycache__ and any intermediate files.
	rm -rf venv

migrate: # Runs all not applied migrations, `make migrate`,
	$(command) python manage.py migrate $(APP) $(MIGRATION)

makemigrations:
	$(command) python manage.py makemigrations $(CMD)

showmigrations:
	$(command) python manage.py showmigrations

superuser:
	$(command) python manage.py createsuperuser

shell: # Enter the python shell
	$(command) python manage.py shell

pre-commit: # Run pre-commit hooks
	pre-commit run --all-files
