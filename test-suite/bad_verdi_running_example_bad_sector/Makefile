include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: py

pdf: sector.pdf

png: sector.png

scy: deps
#	$(MAKE) sector.scy -> TODO: fix the comma problem

USES = -u uses.yml

py: valve.shy sector.shy scy

deps:
	$(MAKE) valve.scy
	! $(SHELLEYMC) $(USES) -s $(VALIDITY_CHECKS) sector_extended.shy

stats: bad_verdi_running_example_bad_sector-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

