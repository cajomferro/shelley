DOCKER_IMAGE_LABEL = shelley
TEST_SUITE_EXAMPLES = test-suite
DEMOS = demos

all: run

build:
	docker build -t $(DOCKER_IMAGE_LABEL) .

run:
	docker run -it --rm \
		-v $(PWD)/shelley:/app/shelley \
		-v $(PWD)/shelleybench:/app/shelleybench \
		-v $(PWD)/benchmark:/app/benchmark \
		-v $(PWD)/$(DEMOS):/app/$(DEMOS) \
		-v $(PWD)/$(TEST_SUITE_EXAMPLES):/app/$(TEST_SUITE_EXAMPLES) \
		-v $(PWD)/tests:/app/tests \
		$(DOCKER_IMAGE_LABEL) bash