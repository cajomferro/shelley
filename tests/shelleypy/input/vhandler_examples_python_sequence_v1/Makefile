include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS =

all: py

pdf: vhandler_sequence.pdf

png: vhandler_sequence.png

scy: vhandler_sequence.scy

USES = -u uses.yml

py: vhandler_sequence.shy valve.shy scy

deps:
	$(MAKE) valve.scy
	$(MAKE) valve_extended.scy
	$(MAKE) vhandler_sequence_extended.scy

vhandler_sequence.scy: deps vhandler_sequence.shy

vhandler_examples_python_sequence_v1-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) vhandler_sequence-stats.json

stats: vhandler_examples_python_sequence_v1-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

