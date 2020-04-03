BUILD_EXTENSIONS=scb scy
APPCOMPILER_DIR=../..
APPCOMPILER_SCRIPT=appcompiler
EXAMPLE_DIR=examples/desklamp
DEVICE=$(EXAMPLE_DIR)/desklamp.yaml
USES=$(EXAMPLE_DIR)/button.scy\:Button $(EXAMPLE_DIR)/led.scy\:Led $(EXAMPLE_DIR)/timer.scy\:Timer
APPCOMPILER_CMD=@cd $(APPCOMPILER_DIR) && python3 -m $(APPCOMPILER_SCRIPT)

all: clean build

build: build_deps
	$(APPCOMPILER_CMD) -u $(USES) -d $(DEVICE)

build_deps:
	$(APPCOMPILER_CMD) -d $(EXAMPLE_DIR)/timer.yaml
	$(APPCOMPILER_CMD) -d $(EXAMPLE_DIR)/led.yaml
	$(APPCOMPILER_CMD) -d $(EXAMPLE_DIR)/button.yaml

clean:
	rm -rf $(foreach postfix, $(BUILD_EXTENSIONS), *.$(postfix))
