include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: py

pdf: vhandler_sequence.pdf

png: vhandler_sequence.png

scy: deps
	$(MAKE) vhandler_sequence.scy
	$(MAKE) vhandler_sequence_extended.scy

USES = -u uses.yml

py: valve.shy vhandler_sequence.shy scy

deps:
	$(MAKE) valve.scy
	$(MAKE) valve_extended.scy

vhandler_examples_python_sequence_v1-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) vhandler_sequence-stats.json

stats: vhandler_examples_python_sequence_v1-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

