.EXPORT_ALL_VARIABLES:
PYTHON_OK := $(shell which python)
PYTHON_VERSION := $(shell python -V | cut -d' ' -f2)
PYTHON_REQUIRED := $(shell cat .python-version)

check_python:
	@echo '*********** Checking for Python installation ***********'
    ifeq ('$(PYTHON_OK)','')
	    $(error python interpreter: 'python' not found!)
    else
	    @echo Found Python
    endif
	@echo '*********** Checking for Python version ***********'
    ifneq ('$(PYTHON_REQUIRED)','$(PYTHON_VERSION)')
	    $(error incorrect version of python found: '${PYTHON_VERSION}'. Expected '${PYTHON_REQUIRED}'!)
    else
	    @echo Found Python ${PYTHON_REQUIRED}
    endif
.PHONY: check_python

black: check_python
	poetry run black *.py
.PHONY: black

init: check_python
	pip install poetry==1.1.6
	poetry run pip install pip -U
	export POETRY_VIRTUALENVS_IN_PROJECT=true && poetry install
.PHONY: init

test: check_python black
	export PYTHONPATH="${PYTHONPATH}:`pwd`/" && poetry run pytest -v
.PHONY: test

all_tests: black test
	poetry run bandit ec2_metadata.py
	poetry run safety check -i 38053

clean:
	rm -rf ./dist/
	rm -rf ./.mypy_cache
	rm -rf ./.pytest_cache
	rm -rf ./mdtp_ec2_metadata.egg-info
	rm -f .coverage
.PHONY: clean

build:
	poetry build
.PHONY: build

publish: build
	poetry config repositories.custom ${REPOSITORY_URL}
    ifneq ('$(REPOSITORY_USER)','')
        ifneq ('$(REPOSITORY_PASS)','')
	        @poetry config http-basic.custom ${REPOSITORY_USER} ${REPOSITORY_PASS}
        endif
    endif
	poetry publish -r custom
	poetry config http-basic.custom --unset
	poetry config repositories.custom --unset
.PHONY: publish
