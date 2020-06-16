include ../common.mk

all: scy

pdf: led_strict.pdf simple_button.pdf desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml led_strict.scy simple_button.scy

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy
