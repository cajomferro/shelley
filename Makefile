PO = poetry
GIT = git
RUN = $(PO) run

PYTEST = $(RUN) pytest
PYTEST_FLAGS = --ignore=tests/shelleypy/test_not_working.py
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
	docker build -t shelleychecker .

docker-run:
	docker run -it --rm \
		-v $(PWD)/shelley:/app/shelley \
		-v $(PWD)/examples:/app/examples \
		-v $(PWD)/shelley-examples:/app/shelley-examples \
		-v $(PWD)/tests:/app/tests \
		shelleychecker bash

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