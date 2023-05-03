include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = --optimize --include-iface-ops

all: py

pdf: app.pdf

png: app.png

scy: deps
	$(MAKE) app.scy
	$(MAKE) app_extended.scy

USES = -u uses.yml

py: wifi.shy controller.shy wireless.shy timer.shy ahttp.shy app.shy valve.shy sector.shy scy

deps:
	$(MAKE) valve.scy
	$(MAKE) valve_extended.scy
	$(MAKE) timer.scy
	$(MAKE) timer_extended.scy
	$(MAKE) sector.scy
	$(MAKE) sector_extended.scy
	$(MAKE) wifi.scy
	$(MAKE) wifi_extended.scy
	$(MAKE) ahttp.scy
	$(MAKE) ahttp_extended.scy
	$(MAKE) wireless.scy
	$(MAKE) wireless_extended.scy
	$(MAKE) controller.scy
	$(MAKE) controller_extended.scy

thesis_aquamote_example-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) timer-stats.json
	$(MAKE) sector-stats.json
	$(MAKE) wifi-stats.json
	$(MAKE) ahttp-stats.json
	$(MAKE) wireless-stats.json
	$(MAKE) controller-stats.json
	$(MAKE) app-stats.json

stats: thesis_aquamote_example-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

