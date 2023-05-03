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

py: app.shy valve.shy scy

deps:
	$(MAKE) valve.scy
	$(MAKE) valve_extended.scy

verdi_running_example_app_v1-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) app-stats.json

stats: verdi_running_example_app_v1-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

