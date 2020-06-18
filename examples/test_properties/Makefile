include ../common.mk

all: scy

pdf: desklamp.pdf

scy: desklamp.scy

desklamp.scy: desklamp.yml
	! $(SHELLEYC) -d $< --no-output

desklamp4.scy: desklamp4.yml led_strict.scy simple_button.scy

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy

.SUFFIXES: .yml .scy .int

