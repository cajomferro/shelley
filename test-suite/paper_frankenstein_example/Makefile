include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: py

pdf: controller.pdf

png: controller.png

scy: deps
	$(MAKE) controller.scy
	$(MAKE) controller_extended.scy

USES = -u uses.yml

py: controller.shy timer.shy valve.shy scy

deps:
	$(MAKE) valve.scy
	$(MAKE) valve_extended.scy
	$(MAKE) timer.scy
	$(MAKE) timer_extended.scy

paper_frankenstein_example-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) timer-stats.json
	$(MAKE) controller-stats.json

stats: paper_frankenstein_example-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv *.shy


.PHONY: all pdf scy deps clean

