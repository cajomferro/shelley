include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: crossroad.pdf

png: crossroad.png

scy: deps
	$(MAKE) crossroad.scy

USES = -u uses.yml



deps:
	$(MAKE) trafficlight.scy
	$(MAKE) traffic-ctl.scy

trafficlight_gamma_tc-stats.json:
	$(MAKE) trafficlight-stats.json
	$(MAKE) traffic-ctl-stats.json
	$(MAKE) crossroad-stats.json

stats: trafficlight_gamma_tc-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv


.PHONY: all pdf scy deps clean

