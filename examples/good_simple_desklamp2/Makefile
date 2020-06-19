include ../common.mk
.PHONY: all pdf scy clean all

all: scy
scy: desklamp.scy

desklamp.scy: desklamp.yml ../base/led_strict.scy ../base/simple_button.scy

clean:
	rm -f *.scy *.pdf *.gv
