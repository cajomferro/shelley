include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: simple_button.pdf led_strict.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml ../base/led_strict.scy ../base/simple_button.scy

clean:
	rm -f *.scy *.pdf *.gv
