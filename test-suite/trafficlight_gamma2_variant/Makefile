include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: crossroad_controller.pdf

png: crossroad_controller.png

scy: deps
	$(MAKE) crossroad_controller.scy

USES = -u uses.yml



deps:
	$(MAKE) timer.scy
	$(MAKE) lightcommands.scy
	$(MAKE) policeinterrupt.scy
	$(MAKE) control.scy
	$(MAKE) trafficlightctrl.scy

trafficlight_gamma2_variant-stats.json:
	$(MAKE) timer-stats.json
	$(MAKE) lightcommands-stats.json
	$(MAKE) policeinterrupt-stats.json
	$(MAKE) control-stats.json
	$(MAKE) trafficlightctrl-stats.json
	$(MAKE) crossroad_controller-stats.json

stats: trafficlight_gamma2_variant-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv


.PHONY: all pdf scy deps clean

