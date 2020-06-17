include ../common.mk

all: scy

pdf: desklamp3.pdf

scy: desklamp1.scy desklamp2.scy desklamp3.scy

desklamp1.scy: desklamp1.yml led_strict.scy simple_button.scy
	! $(SHELLEYC) -u uses.yml -d $< --no-output

desklamp2.scy: desklamp2.yml led_strict.scy simple_button.scy
	! $(SHELLEYC) -u uses.yml -d $< --no-output

desklamp3.scy: desklamp3.yml led_strict.scy simple_button.scy

desklamp4.scy: desklamp3.yml led_strict.scy simple_button.scy

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy

.SUFFIXES: .yml .scy .int

