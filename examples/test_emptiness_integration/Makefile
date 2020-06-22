include ../common.mk
.PHONY: all pdf scy clean all

all: scy

pdf: button.pdf led.pdf timer.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml ../base/timer.scy ../base/led.scy ../base/button.scy

clean:
	rm -f *.scy *.pdf *.gv

