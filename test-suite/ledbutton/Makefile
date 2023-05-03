include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: ledbutton.pdf

png: ledbutton.png

scy: deps
	$(MAKE) ledbutton.scy

USES = -u uses.yml



deps:
	$(MAKE) -C ../base simple_button.scy
	$(MAKE) led.scy

ledbutton-stats.json:
	$(MAKE) -C ../base simple_button-stats.json
	$(MAKE) led-stats.json
	$(MAKE) ledbutton-stats.json

stats: ledbutton-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean

