PO = poetry

RUN = $(PO) run

PYTEST = $(RUN) pytest
PYTEST_FLAGS =
MYPY = $(RUN) mypy
MYPY_FLAGS = --show-error-context --show-column-numbers --pretty

all: check

init:
	$(PO) update

check:
	$(MYPY) $(MYPY_FLAGS) .

test: check
	$(PYTEST) $(PYTEST_FLAGS) tests

examples: test
	$(MAKE) -C examples

clean:
	$(MAKE) -C examples clean

.PHONY: init check test all