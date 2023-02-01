include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS =

all: py

pdf: vhandler_if.pdf

png: vhandler_if.png

scy: vhandler_if.scy

USES = -u uses.yml

py: vhandler_if.shy valve.shy scy

deps:
	$(MAKE) valve.scy
	$(MAKE) valve_extended.scy
	$(MAKE) vhandler_if_extended.scy

vhandler_if.scy: deps vhandler_if.shy

vhandler_examples_python_if_v3-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) vhandler_if-stats.json

stats: vhandler_examples_python_if_v3-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

