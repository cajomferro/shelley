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

py: led.shy controller.shy timer.shy app.shy valve.shy scy

deps:
	$(MAKE) valve.scy
	$(MAKE) valve_extended.scy
	$(MAKE) timer.scy
	$(MAKE) timer_extended.scy
	$(MAKE) led.scy
	$(MAKE) led_extended.scy
	$(MAKE) controller.scy
	$(MAKE) controller_extended.scy
	$(MAKE) app_extended.scy

app.scy: deps app.shy

vhandler_examples_python_v4-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) timer-stats.json
	$(MAKE) led-stats.json
	$(MAKE) controller-stats.json
	$(MAKE) app-stats.json

stats: vhandler_examples_python_v4-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

