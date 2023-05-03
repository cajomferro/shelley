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

py: app.shy controller.shy counter.shy led.shy scy

deps:
	$(MAKE) counter.scy
	$(MAKE) counter_extended.scy
	$(MAKE) led.scy
	$(MAKE) led_extended.scy
	$(MAKE) controller.scy
	$(MAKE) controller_extended.scy

people_counter-stats.json:
	$(MAKE) counter-stats.json
	$(MAKE) led-stats.json
	$(MAKE) controller-stats.json
	$(MAKE) app-stats.json

stats: people_counter-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

