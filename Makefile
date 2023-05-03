PO = poetry
RUN = $(PO) run

PYTEST = $(RUN) pytest
PYTEST_FLAGS =--ignore=tests/shelleypy/test_not_working.py
MYPY = $(RUN) mypy
MYPY_FLAGS = --show-error-context --show-column-numbers --pretty
BLACK = $(RUN) black

TEST_SUITE_EXAMPLES = test-suite
DEMOS = demos

all: check test format

deps:
	$(PO) update

check:
	$(MYPY) $(MYPY_FLAGS) .

test: #check
	$(PYTEST) $(PYTEST_FLAGS) tests

suite:
	$(MAKE) -C $(TEST_SUITE_EXAMPLES)

clean:
	$(MAKE) -C examples clean

format:
	$(BLACK) shelley

count-test-suite:
	find $(TEST_SUITE_EXAMPLES)/ | grep -c "\.shy$$"

.PHONY: init check test all examples