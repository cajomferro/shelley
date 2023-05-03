include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: py

pdf: vhandler.pdf

png: vhandler.png

scy: deps
	$(MAKE) vhandler.scy
	$(MAKE) vhandler_extended.scy

USES = -u uses.yml

py: valve.shy vhandler.shy scy

deps:
	$(MAKE) valve.scy
	$(MAKE) valve_extended.scy

vhandler_examples_python_if_v2-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) vhandler-stats.json

stats: vhandler_examples_python_if_v2-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

