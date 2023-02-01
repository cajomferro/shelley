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

py: twovalves.shy led.shy controller-alt.shy controller.shy timer.shy apptwovalves.shy app.shy valve.shy scy

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
	$(MAKE) app_extended.scy

app.scy: deps app.shy

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

