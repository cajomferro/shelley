include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: aquamote_core.pdf

png: aquamote_core.png

scy: deps
	$(MAKE) aquamote_core.scy

USES = -u uses.yml



deps:
	$(MAKE) magnetic.scy
	$(MAKE) valve.scy
	$(MAKE) -C ../base timer.scy
	$(MAKE) lowpower-strict.scy
	$(MAKE) valvehandlertimer.scy
	$(MAKE) gprsclient.scy
	$(MAKE) httpclient.scy
	$(MAKE) radioclient.scy

aquamote_v1-stats.json:
	$(MAKE) magnetic-stats.json
	$(MAKE) valve-stats.json
	$(MAKE) -C ../base timer-stats.json
	$(MAKE) lowpower-strict-stats.json
	$(MAKE) valvehandlertimer-stats.json
	$(MAKE) gprsclient-stats.json
	$(MAKE) httpclient-stats.json
	$(MAKE) radioclient-stats.json
	$(MAKE) aquamote_core-stats.json

stats: aquamote_v1-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../base clean


.PHONY: all pdf scy deps clean

