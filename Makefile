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

deps:
	$(PO) update

check:
	$(MYPY) $(MYPY_FLAGS) .

test: #check
	$(PYTEST) $(PYTEST_FLAGS) tests

examples:
	$(MAKE) -C shelley-examples SHELLEYC="$(RUN) shelleyc" SHELLEYV="$(RUN) shelleyv"

clean:
	$(MAKE) -C examples clean

format:
	$(BLACK) .

.PHONY: init check test all examples