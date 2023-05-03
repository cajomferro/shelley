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

py: app.shy apptwovalves.shy controller-alt.shy controller.shy led.shy timer.shy twovalves.shy valve.shy scy

deps:
	$(MAKE) valve.scy
	$(MAKE) valve_extended.scy
	$(MAKE) twovalves.scy
	$(MAKE) twovalves_extended.scy
	$(MAKE) apptwovalves.scy
	$(MAKE) apptwovalves_extended.scy
	$(MAKE) timer.scy
	$(MAKE) timer_extended.scy
	$(MAKE) led.scy
	$(MAKE) led_extended.scy
	$(MAKE) controller.scy
	$(MAKE) controller_extended.scy
	$(MAKE) controller-alt.scy
	$(MAKE) controller-alt_extended.scy

vhandler_examples_python_v3-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) twovalves-stats.json
	$(MAKE) apptwovalves-stats.json
	$(MAKE) timer-stats.json
	$(MAKE) led-stats.json
	$(MAKE) controller-stats.json
	$(MAKE) controller-alt-stats.json
	$(MAKE) app-stats.json

stats: vhandler_examples_python_v3-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

