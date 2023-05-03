include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: valves61_1.pdf

png: valves61_1.png

scy: deps
	$(MAKE) valves61_1.scy

USES = -u uses.yml



deps:
	$(MAKE) valve61.scy

valve-too-long-stats.json:
	$(MAKE) valve61-stats.json
	$(MAKE) valves61_1-stats.json

stats: valve-too-long-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv


.PHONY: all pdf scy deps clean

