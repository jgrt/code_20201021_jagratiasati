.PHONY: all prepare-dev venv lint test run shell clean build install docker
SHELL=/bin/bash

VENV_NAME?=vamstar
VENV_BIN=$(shell pwd)/${VENV_NAME}/bin
VENV_ACTIVATE=. ${VENV_BIN}/activate

PYTHON=${VENV_BIN}/python3

all:

	@echo "make prepare-env"
	@echo "    Create python virtual environment and install dependencies."
	@echo "make test"
	@echo "    Run tests on project."


prepare-env:

	which python3 || apt install -y python3 python3-pip
	which virtualenv || python3 -m pip install virtualenv
	make venv


venv: $(VENV_NAME)/bin/activate
$(VENV_NAME)/bin/activate: setup.py

	test -d $(VENV_NAME) || virtualenv -p python3 $(VENV_NAME)
	${PYTHON} -m pip install -U pip setuptools
	${PYTHON} -m pip install -e .[dev]
	touch $(VENV_NAME)/bin/activate


test: venv

	${PYTHON} -m pytest -vv tests




