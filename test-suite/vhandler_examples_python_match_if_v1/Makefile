include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: py

pdf: app.pdf

png: app.png

scy: deps
	$(MAKE) app.scy
	$(MAKE) app_extended.scy

USES = -u uses.yml

py: app.shy valve.shy vhandler.shy scy

deps:
	$(MAKE) valve.scy
	$(MAKE) valve_extended.scy
	$(MAKE) vhandler.scy
	$(MAKE) vhandler_extended.scy

vhandler_examples_python_match_if_v1-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) vhandler-stats.json
	$(MAKE) app-stats.json

stats: vhandler_examples_python_match_if_v1-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

