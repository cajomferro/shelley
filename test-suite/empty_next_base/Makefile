include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: led.pdf

png: led.png

scy: deps
	$(MAKE) led.scy

USES = -u uses.yml



deps:

empty_next_base-stats.json:
	$(MAKE) led-stats.json

stats: empty_next_base-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv


.PHONY: all pdf scy deps clean

