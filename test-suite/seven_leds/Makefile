include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: seven_leds.pdf

png: seven_leds.png

scy: deps
	$(MAKE) seven_leds.scy

USES = -u uses.yml



deps:
	$(MAKE) -C ../base led.scy

seven_leds-stats.json:
	$(MAKE) -C ../base led-stats.json
	$(MAKE) seven_leds-stats.json

stats: seven_leds-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean

