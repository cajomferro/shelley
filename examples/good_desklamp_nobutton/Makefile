include ../common.mk

all: scy

pdf: led.pdf timer.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml timer.scy led.scy

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy
