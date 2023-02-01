include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS =

all: py

pdf: vhandler.pdf

png: vhandler.png

scy: vhandler.scy

USES = -u uses.yml

py: vhandler_open_all.shy vhandler.shy valve.shy vhandler_close_all.shy scy

deps:
	$(MAKE) valve.scy
	$(MAKE) valve_extended.scy
	$(MAKE) vhandler_open_all.scy
	$(MAKE) vhandler_open_all_extended.scy
	$(MAKE) vhandler_close_all.scy
	$(MAKE) vhandler_close_all_extended.scy
	$(MAKE) vhandler_extended.scy

vhandler.scy: deps vhandler.shy

vhandler_examples_python_v1-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) vhandler_open_all-stats.json
	$(MAKE) vhandler_close_all-stats.json
	$(MAKE) vhandler-stats.json

stats: vhandler_examples_python_v1-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

