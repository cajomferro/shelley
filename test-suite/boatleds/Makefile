include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: controller.pdf

png: controller.png

scy: deps
	$(MAKE) controller.scy

USES = -u uses.yml



deps:
	$(MAKE) led.scy
	$(MAKE) button.scy
	$(MAKE) timer.scy

boatleds-stats.json:
	$(MAKE) led-stats.json
	$(MAKE) button-stats.json
	$(MAKE) timer-stats.json
	$(MAKE) controller-stats.json

stats: boatleds-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv


.PHONY: all pdf scy deps clean

