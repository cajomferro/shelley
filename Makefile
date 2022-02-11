PO = poetry
GIT = git
RUN = $(PO) run

PYTEST = $(RUN) pytest
PYTEST_FLAGS =
MYPY = $(RUN) mypy
MYPY_FLAGS = --show-error-context --show-column-numbers --pretty
BLACK = $(RUN) black

all: check test format

init:
	$(GIT) submodule update --init
	$(GIT) submodule foreach git checkout master

pull:
	$(GIT) pull --recurse-submodules

docker-build:
	docker compose build

docker-run:
	docker compose run --rm main bash

deps:
	$(PO) update

check:
	$(MYPY) $(MYPY_FLAGS) .

test: #check
	$(PYTEST) $(PYTEST_FLAGS) tests

examples:
	$(MAKE) -C shelley-examples

clean:
	$(MAKE) -C examples clean

format:
	$(BLACK) shelley

.PHONY: init check test all examples