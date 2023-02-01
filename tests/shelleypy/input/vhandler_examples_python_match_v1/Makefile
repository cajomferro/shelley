include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS =

all: py

pdf: vhandler_match.pdf

png: vhandler_match.png

scy: vhandler_match.scy

USES = -u uses.yml

py: vhandler_match.shy valve.shy scy

deps:
	$(MAKE) valve.scy
	$(MAKE) valve_extended.scy
	$(MAKE) vhandler_match_extended.scy

vhandler_match.scy: deps vhandler_match.shy

vhandler_examples_python_match_v1-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) vhandler_match-stats.json

stats: vhandler_examples_python_match_v1-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

