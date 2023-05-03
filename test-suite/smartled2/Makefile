include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: smartled2.pdf

png: smartled2.png

scy: deps
	$(MAKE) smartled2.scy

USES = -u uses.yml



deps:
	$(MAKE) -C ../base led.scy
	$(MAKE) -C ../base timer.scy

smartled2-stats.json:
	$(MAKE) -C ../base led-stats.json
	$(MAKE) -C ../base timer-stats.json
	$(MAKE) smartled2-stats.json

stats: smartled2-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean

