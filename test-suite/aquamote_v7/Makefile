include ../common.mk

MAKEFLAGS += --no-print-directory

USES = -u uses.yml
#VALIDITY_CHECKS=--skip-direct
#VALIDITY_CHECKS=--skip-mc
SHELLEYPY_OPTS = # --optimize --include-iface-ops

all: scy

pdf: aquamote_controller_radio_v3_lp_strict.pdf

png: aquamote_controller_radio_v3_lp_strict.png

scy: deps
	$(MAKE) aquamote_controller_radio_v3_lp_strict.scy

USES = -u uses.yml



deps:
	$(MAKE) -C ../aquamote_v1 valve.scy
	$(MAKE) -C ../aquamote_v1 magnetic.scy
	$(MAKE) -C ../aquamote_v1 lowpower-strict.scy
	$(MAKE) -C ../aquamote_v5 radio_v1.scy
	$(MAKE) radio_v2.scy
	$(MAKE) radio_v3.scy

aquamote_v7-stats.json:
	$(MAKE) -C ../aquamote_v1 valve-stats.json
	$(MAKE) -C ../aquamote_v1 magnetic-stats.json
	$(MAKE) -C ../aquamote_v1 lowpower-strict-stats.json
	$(MAKE) -C ../aquamote_v5 radio_v1-stats.json
	$(MAKE) radio_v2-stats.json
	$(MAKE) radio_v3-stats.json
	$(MAKE) aquamote_controller_radio_v3_lp_strict-stats.json

stats: aquamote_v7-stats.json

clean:
	rm -f *.scy *.pdf *.png *.gv *-stats.json *.int *.smv
	$(MAKE) -C ../aquamote_v1 clean
	$(MAKE) -C ../aquamote_v1 clean
	$(MAKE) -C ../aquamote_v1 clean
	$(MAKE) -C ../aquamote_v5 clean


.PHONY: all pdf scy deps clean

