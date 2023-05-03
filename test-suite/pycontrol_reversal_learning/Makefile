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

py: app.shy event_handler.shy led.shy poke.shy sol.shy task.shy timer.shy scy

deps:
	$(MAKE) timer.scy
	$(MAKE) timer_extended.scy
	$(MAKE) led.scy
	$(MAKE) led_extended.scy
	$(MAKE) sol.scy
	$(MAKE) sol_extended.scy
	$(MAKE) poke.scy
	$(MAKE) poke_extended.scy
	$(MAKE) event_handler.scy
	$(MAKE) event_handler_extended.scy
	$(MAKE) task.scy
	$(MAKE) task_extended.scy

pycontrol_reversal_learning-stats.json:
	$(MAKE) timer-stats.json
	$(MAKE) led-stats.json
	$(MAKE) sol-stats.json
	$(MAKE) poke-stats.json
	$(MAKE) event_handler-stats.json
	$(MAKE) task-stats.json
	$(MAKE) app-stats.json

stats: pycontrol_reversal_learning-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

