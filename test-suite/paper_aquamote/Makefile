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
	$(MAKE) valve.scy
	$(MAKE) timer.scy
	$(MAKE) magnetic.scy
	$(MAKE) power_handler.scy
	$(MAKE) valvehandler.scy
	$(MAKE) gprsclient.scy
	$(MAKE) httpclient.scy
	$(MAKE) wireless.scy

paper_aquamote-stats.json:
	$(MAKE) valve-stats.json
	$(MAKE) timer-stats.json
	$(MAKE) magnetic-stats.json
	$(MAKE) power_handler-stats.json
	$(MAKE) valvehandler-stats.json
	$(MAKE) gprsclient-stats.json
	$(MAKE) httpclient-stats.json
	$(MAKE) wireless-stats.json
	$(MAKE) controller-stats.json

stats: paper_aquamote-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv


.PHONY: all pdf scy deps clean

