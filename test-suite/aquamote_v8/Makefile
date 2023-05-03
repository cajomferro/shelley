include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: aquamote_controller_radioclient.pdf

png: aquamote_controller_radioclient.png

scy: deps
	$(MAKE) aquamote_controller_radioclient.scy

USES = -u uses.yml



deps:
	$(MAKE) -C ../aquamote_v1 valve.scy
	$(MAKE) -C ../base timer.scy
	$(MAKE) -C ../aquamote_v1 magnetic.scy
	$(MAKE) -C ../aquamote_v1 lowpower-strict.scy
	$(MAKE) -C ../aquamote_v1 valvehandlertimer.scy
	$(MAKE) wificlient.scy
	$(MAKE) httpclient.scy
	$(MAKE) radioclient.scy

aquamote_v8-stats.json:
	$(MAKE) -C ../aquamote_v1 valve-stats.json
	$(MAKE) -C ../base timer-stats.json
	$(MAKE) -C ../aquamote_v1 magnetic-stats.json
	$(MAKE) -C ../aquamote_v1 lowpower-strict-stats.json
	$(MAKE) -C ../aquamote_v1 valvehandlertimer-stats.json
	$(MAKE) wificlient-stats.json
	$(MAKE) httpclient-stats.json
	$(MAKE) radioclient-stats.json
	$(MAKE) aquamote_controller_radioclient-stats.json

stats: aquamote_v8-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../aquamote_v1 clean
	$(MAKE) -C ../base clean
	$(MAKE) -C ../aquamote_v1 clean
	$(MAKE) -C ../aquamote_v1 clean
	$(MAKE) -C ../aquamote_v1 clean


.PHONY: all pdf scy deps clean

