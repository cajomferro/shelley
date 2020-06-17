include ../common.mk

all: scy

scy: desklamp1.scy desklamp2.scy

desklamp1.scy: desklamp1.yml led_strict.scy simple_button.scy
	! $(SHELLEYC) -u uses.yml -d $< --no-output

desklamp2.scy: desklamp2.yml led_strict.scy simple_button.scy
	! $(SHELLEYC) -u uses.yml -d $< --no-output

clean:
	rm -f *.scy *.pdf *.int

.PHONY: all pdf scy

.SUFFIXES: .yml .scy .int

