BUILD_EXTENSIONS=scb scy
APPCOMPILER_DIR=../..
APPCOMPILER_SCRIPT=appcompiler
EXAMPLE_DIR=examples/smartbutton
DEVICE=$(EXAMPLE_DIR)/smartbutton.yaml
USES=$(EXAMPLE_DIR)/button.scy\:Button
APPCOMPILER_CMD=@cd $(APPCOMPILER_DIR) && python3 -m $(APPCOMPILER_SCRIPT)

all: clean build

build: build_deps
	$(APPCOMPILER_CMD) -u $(USES) -d $(DEVICE)

build_deps:
	$(APPCOMPILER_CMD) -d $(EXAMPLE_DIR)/button.yaml

clean:
	rm -f $(foreach postfix, $(BUILD_EXTENSIONS), *.$(postfix))
