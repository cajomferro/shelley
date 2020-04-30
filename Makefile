PO = poetry

RUN = $(PO) run

PYTEST = $(RUN) pytest
PYTEST_FLAGS =
MYPY = $(RUN) mypy
MYPY_FLAGS = --show-error-context --show-column-numbers --pretty
BLACK = $(RUN) black

all: check test format

deps:
	$(PO) update

check:
	$(MYPY) $(MYPY_FLAGS) .

test: check
	$(PYTEST) $(PYTEST_FLAGS) tests

examples:
	$(MAKE) -C examples SHELLEYC="$(RUN) shelleyc" SHELLEYV="$(RUN) shelleyv"

clean:
	$(MAKE) -C examples clean

format:
	$(BLACK) .

.PHONY: init check test all examples