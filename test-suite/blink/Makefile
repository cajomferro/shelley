include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: blink.pdf

png: blink.png

scy: deps
	$(MAKE) blink.scy

USES = -u uses.yml



deps:
	$(MAKE) -C ../base timer.scy
	$(MAKE) -C ../base led.scy

blink-stats.json:
	$(MAKE) -C ../base timer-stats.json
	$(MAKE) -C ../base led-stats.json
	$(MAKE) blink-stats.json

stats: blink-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean

