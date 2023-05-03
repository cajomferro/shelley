include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: smartled.pdf

png: smartled.png

scy: deps
	$(MAKE) smartled.scy

USES = -u uses.yml



deps:
	$(MAKE) -C ../base led.scy
	$(MAKE) -C ../base timer.scy

smartled-stats.json:
	$(MAKE) -C ../base led-stats.json
	$(MAKE) -C ../base timer-stats.json
	$(MAKE) smartled-stats.json

stats: smartled-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean

