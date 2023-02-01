include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS =

all: py

pdf: app.pdf

png: app.png

scy: app.scy

USES = -u uses.yml

py: vhandler.shy app.shy valve.shy scy

deps:
	$(MAKE) valve.scy
	$(MAKE) valve_extended.scy
	$(MAKE) vhandler.scy
	$(MAKE) vhandler_extended.scy
	$(MAKE) app_extended.scy

app.scy: deps app.shy

vhandler_examples_python_if_v1-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) vhandler-stats.json
	$(MAKE) app-stats.json

stats: vhandler_examples_python_if_v1-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

