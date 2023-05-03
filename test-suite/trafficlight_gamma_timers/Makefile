include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: trafficlightctrl.pdf

png: trafficlightctrl.png

scy: deps
	$(MAKE) trafficlightctrl.scy

USES = -u uses.yml



deps:
	$(MAKE) control.scy
	$(MAKE) timer.scy
	$(MAKE) lightcommands.scy
	$(MAKE) policeinterrupt.scy

trafficlight_gamma_timers-stats.json:
	$(MAKE) control-stats.json
	$(MAKE) timer-stats.json
	$(MAKE) lightcommands-stats.json
	$(MAKE) policeinterrupt-stats.json
	$(MAKE) trafficlightctrl-stats.json

stats: trafficlight_gamma_timers-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv


.PHONY: all pdf scy deps clean

