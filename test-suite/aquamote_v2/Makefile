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
	$(MAKE) -C ../aquamote_v1 magnetic.scy
	$(MAKE) -C ../aquamote_v1 valve.scy
	$(MAKE) -C ../base timer.scy
	$(MAKE) -C ../aquamote_v1 lowpower-strict.scy
	$(MAKE) -C ../aquamote_v1 valvehandlertimer.scy
	$(MAKE) -C ../aquamote_v1 gprsclient.scy
	$(MAKE) -C ../aquamote_v1 httpclient.scy
	$(MAKE) -C ../aquamote_v1 radioclient.scy

aquamote_v2-stats.json:
	$(MAKE) -C ../aquamote_v1 magnetic-stats.json
	$(MAKE) -C ../aquamote_v1 valve-stats.json
	$(MAKE) -C ../base timer-stats.json
	$(MAKE) -C ../aquamote_v1 lowpower-strict-stats.json
	$(MAKE) -C ../aquamote_v1 valvehandlertimer-stats.json
	$(MAKE) -C ../aquamote_v1 gprsclient-stats.json
	$(MAKE) -C ../aquamote_v1 httpclient-stats.json
	$(MAKE) -C ../aquamote_v1 radioclient-stats.json
	$(MAKE) aquamote_core-stats.json

stats: aquamote_v2-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../aquamote_v1 clean
	$(MAKE) -C ../aquamote_v1 clean
	$(MAKE) -C ../base clean
	$(MAKE) -C ../aquamote_v1 clean
	$(MAKE) -C ../aquamote_v1 clean
	$(MAKE) -C ../aquamote_v1 clean
	$(MAKE) -C ../aquamote_v1 clean
	$(MAKE) -C ../aquamote_v1 clean


.PHONY: all pdf scy deps clean

