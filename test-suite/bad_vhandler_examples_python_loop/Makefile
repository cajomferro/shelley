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

py: vhandler.shy valve.shy scy

deps:
	$(MAKE) valve.scy
	$(MAKE) valve_extended.scy
	! $(SHELLEYMC) $(USES) -s $(VALIDITY_CHECKS) vhandler_extended.shy

vhandler.scy: deps vhandler.shy

vhandler_examples_python_loop_v1-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) vhandler-stats.json

stats: vhandler_examples_python_loop_v1-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

